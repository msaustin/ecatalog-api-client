#!/usr/bin/env python3

import pandas as pd
import click
import os
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from pathlib import Path
import sys
from typing import Dict, List, Optional
from dotenv import load_dotenv

from ecatalog_client import (
    ECatalogAPIClient,
    ItemNew,
    ItemDivisions,
    ItemDivision,
    ItemAttributes,
    OAuthConfig,
)

console = Console()

# Load environment variables
load_dotenv()


class ReskuItemImporter:
    def __init__(self, api_client: ECatalogAPIClient):
        self.client = api_client
        self.console = console

    def parse_divisions_from_region(self, region: str) -> ItemDivisions:
        """Parse division data from Region field"""
        # Start with all divisions as None (null)
        divisions = {"FL": None, "SE": None, "TX": None}

        if pd.notna(region):
            region_str = str(region).upper()
            # Handle different region formats - set specified divisions to Active=False
            if "FL" in region_str or "FLORIDA" in region_str:
                divisions["FL"] = ItemDivision(Active=False)
            if "SE" in region_str or "SOUTHEAST" in region_str:
                divisions["SE"] = ItemDivision(Active=False)
            if "TX" in region_str or "TEXAS" in region_str:
                divisions["TX"] = ItemDivision(Active=False)
            # Handle "ALL" or similar
            if "ALL" in region_str:
                divisions = {
                    "FL": ItemDivision(Active=False),
                    "SE": ItemDivision(Active=False),
                    "TX": ItemDivision(Active=False),
                }

        return ItemDivisions(**divisions)

    def parse_attributes_from_row(self, row: pd.Series) -> Optional[ItemAttributes]:
        """Parse item attributes from spreadsheet columns"""
        attributes = {}

        # Direct mapping from spreadsheet to API attributes
        attribute_mapping = {
            "Color": "Color",
            "Decor": "Décor",  # Note the accent
            "Finish": "Finish",
            "Features": "Features",
            "Material": "Material",
            "Movement": "Movement",
            "PieceCount": "Piece Count",
            "Shape": "Shape",
            "Size": "Size",
            "Style": "Style",
            "Theme": "Theme",
        }

        for api_field, spreadsheet_col in attribute_mapping.items():
            if spreadsheet_col in row.index and pd.notna(row[spreadsheet_col]):
                value = str(row[spreadsheet_col]).strip()
                if value:
                    # Handle comma-separated values
                    attributes[api_field] = [
                        v.strip() for v in value.split(",") if v.strip()
                    ]

        return ItemAttributes(**attributes) if attributes else None

    def row_to_item(self, row: pd.Series) -> Optional[ItemNew]:
        """Convert a spreadsheet row to an ItemNew object"""
        try:
            # Field mapping from spreadsheet columns to API fields
            field_mapping = {
                "Sku": "New SKU",
                "Site": "Site",
                "Collection": "Collection",
                "Category": "Ecat Category",
                "PDMDescription": "Description",
                "Title": "Title",
                "AdvertisingCopy": "Advertising Copy",
                "Image": "Ecat Image Name",
                "AdditionalNotes": "Additional Notes",
                "Dimensions": "Out Of Box Dim",
                "GenericName": "Generic Name",
                "DeliveryType": "Delivery Type",
                "ShippingCode": "Shipping Code",
            }

            # Optional fields with defaults
            optional_mapping = {
                "Brand": ("Specialty Brand", ""),
                "Dimensions": ("Out Of Box Dim", ""),
            }

            # Extract required fields
            item_data = {}
            missing_fields = []

            for api_field, spreadsheet_col in field_mapping.items():
                if spreadsheet_col in row.index and pd.notna(row[spreadsheet_col]):
                    value = str(row[spreadsheet_col]).strip()
                    if value:
                        item_data[api_field] = value
                    else:
                        missing_fields.append(f"{api_field} ({spreadsheet_col})")
                else:
                    missing_fields.append(f"{api_field} ({spreadsheet_col})")

            # Handle optional fields with defaults
            for api_field, (spreadsheet_col, default_value) in optional_mapping.items():
                if spreadsheet_col in row.index and pd.notna(row[spreadsheet_col]):
                    value = str(row[spreadsheet_col]).strip()
                    if value:
                        item_data[api_field] = value
                    else:
                        item_data[api_field] = default_value
                else:
                    item_data[api_field] = default_value

            # Special handling for Brand field based on Site
            if not item_data.get("Brand") or item_data["Brand"] == "":
                site = item_data.get("Site", "").upper()
                if site in ("RTG", "KTG"):
                    item_data["Brand"] = "Rooms To Go"
                elif site == "OTG":
                    item_data["Brand"] = "Rooms To Go Outdoor"

            # Check for critical missing fields - Collection is required
            critical_fields = [
                "Sku",
                "Site",
                "Collection",
                "PDMDescription",
                "Title",
                "GenericName",
                "DeliveryType",
            ]
            critical_missing = [
                field
                for field in critical_fields
                if field not in item_data or not item_data[field]
            ]

            if critical_missing:
                console.print(
                    f"[red]Missing critical fields for SKU {row.get('New SKU', 'Unknown')}: {critical_missing}[/red]"
                )
                console.print(f"[dim]Available columns: {', '.join(row.index.tolist())}[/dim]")
                return None

            # Use Category or Ecat Category for Category field
            if "Category" not in item_data:
                for cat_col in ["Ecat Category", "Category", "Top Category"]:
                    if cat_col in row.index and pd.notna(row[cat_col]):
                        value = str(row[cat_col]).strip()
                        if value:
                            item_data["Category"] = value
                            break
                else:
                    item_data["Category"] = "Uncategorized"

            # Handle optional boolean field - default to False if blank
            if "Single Item Room" in row.index and pd.notna(row["Single Item Room"]):
                item_data["SingleItemRoom"] = bool(row["Single Item Room"])
            else:
                item_data["SingleItemRoom"] = False

            # Handle Vendor Delivery Code -> DeliverySubType
            if "Vendor Delivery Code" in row.index and pd.notna(
                row["Vendor Delivery Code"]
            ):
                item_data["DeliverySubType"] = str(row["Vendor Delivery Code"]).strip()

            # Parse divisions from Region field
            region = row.get("Region", "")
            item_data["Divisions"] = self.parse_divisions_from_region(region)

            # Parse attributes
            attributes = self.parse_attributes_from_row(row)
            if attributes:
                item_data["Attributes"] = attributes

            return ItemNew(**item_data)

        except Exception as e:
            console.print(
                f"[red]Error creating item from row {row.get('New SKU', 'Unknown')}: {e}[/red]"
            )
            return None

    def preview_data_mapping(
        self, file_path: Path, sheet_name: Optional[str] = None
    ) -> None:
        """Preview how the spreadsheet data will be mapped"""
        try:
            if file_path.suffix.lower() in [".xlsx", ".xls"]:
                # Default to first sheet if no sheet name provided
                if sheet_name is None:
                    sheet_name = 0  # Read first sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            elif file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path)
            else:
                console.print(f"[red]Unsupported file format: {file_path.suffix}[/red]")
                return

            console.print(f"[bold]Data Mapping Preview[/bold]")
            console.print(f"Total rows: {len(df)}")

            # Show first few rows mapping
            for i in range(min(3, len(df))):
                row = df.iloc[i]
                console.print(
                    f"\n[cyan]Row {i + 1} - SKU: {row.get('New SKU', 'N/A')}[/cyan]"
                )

                table = Table()
                table.add_column("API Field", style="yellow")
                table.add_column("Spreadsheet Column", style="cyan")
                table.add_column("Value", style="white")

                # Show key mappings
                key_mappings = [
                    ("Sku", "New SKU"),
                    ("Site", "Site"),
                    ("Category", "Ecat Category"),
                    ("Title", "Title"),
                    ("Region/Divisions", "Region"),
                    ("GenericName", "Generic Name"),
                    ("DeliveryType", "Delivery Type"),
                ]

                for api_field, spreadsheet_col in key_mappings:
                    value = row.get(spreadsheet_col, "N/A")
                    if pd.notna(value):
                        value = (
                            str(value)[:50] + "..."
                            if len(str(value)) > 50
                            else str(value)
                        )
                    else:
                        value = "N/A"
                    table.add_row(api_field, spreadsheet_col, value)

                console.print(table)

        except Exception as e:
            console.print(f"[red]Error previewing data: {e}[/red]")

    def import_from_spreadsheet(
        self,
        file_path: Path,
        sheet_name: Optional[str] = None,
        dry_run: bool = True,
        limit: Optional[int] = None,
    ) -> Dict[str, int]:
        """Import items from the resku spreadsheet"""

        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return {"processed": 0, "created": 0, "failed": 0}

        try:
            if file_path.suffix.lower() in [".xlsx", ".xls"]:
                # Default to first sheet if no sheet name provided
                if sheet_name is None:
                    sheet_name = 0  # Read first sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            elif file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path)
            else:
                console.print(f"[red]Unsupported file format: {file_path.suffix}[/red]")
                return {"processed": 0, "created": 0, "failed": 0}

            # Apply limit if specified
            if limit and limit > 0:
                df = df.head(limit)
                console.print(
                    f"[bold]Loaded {len(df)} rows from {file_path.name} (limited to first {limit})[/bold]"
                )
            else:
                console.print(
                    f"[bold]Loaded {len(df)} rows from {file_path.name}[/bold]"
                )

            stats = {"processed": 0, "created": 0, "failed": 0}

            if dry_run:
                console.print(
                    "[yellow]DRY RUN MODE - No items will be created[/yellow]"
                )

            with Progress() as progress:
                task = progress.add_task("Processing items...", total=len(df))

                for index, row in df.iterrows():
                    stats["processed"] += 1

                    # Convert row to ItemNew object
                    item = self.row_to_item(row)
                    if not item:
                        stats["failed"] += 1
                        progress.update(task, advance=1)
                        continue

                    if dry_run:
                        console.print(
                            f"[cyan]Would create item:[/cyan] {item.Sku} - {item.Title}"
                        )
                        console.print(f"  Site: {item.Site}, Category: {item.Category}")
                        # Show division status: None=null, False=inactive, True=active
                        fl_status = (
                            "null"
                            if item.Divisions.FL is None
                            else f"Active={item.Divisions.FL.Active}"
                        )
                        se_status = (
                            "null"
                            if item.Divisions.SE is None
                            else f"Active={item.Divisions.SE.Active}"
                        )
                        tx_status = (
                            "null"
                            if item.Divisions.TX is None
                            else f"Active={item.Divisions.TX.Active}"
                        )
                        console.print(
                            f"  Divisions: FL={fl_status}, SE={se_status}, TX={tx_status}"
                        )
                        stats["created"] += 1
                    else:
                        # Actually create the item
                        try:
                            result = self.client.create_item(item)
                            if result:
                                # Extract work request ID if available
                                workrequest_id = result.get("workrequest_id")
                                if workrequest_id:
                                    console.print(
                                        f"[green]Created item:[/green] {item.Sku} - {item.Title} [dim](Work Request: {workrequest_id})[/dim]"
                                    )
                                else:
                                    console.print(
                                        f"[green]Created item:[/green] {item.Sku} - {item.Title}"
                                    )
                                stats["created"] += 1
                            else:
                                console.print(
                                    f"[red]Failed to create item:[/red] {item.Sku}"
                                )
                                stats["failed"] += 1
                        except Exception as e:
                            console.print(
                                f"[red]Error creating item {item.Sku}: {e}[/red]"
                            )
                            stats["failed"] += 1

                    progress.update(task, advance=1)

            return stats

        except Exception as e:
            console.print(f"[red]Error reading spreadsheet: {e}[/red]")
            return {"processed": 0, "created": 0, "failed": 0}


@click.command()
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--api-url", default="http://127.0.0.1:8000", help="eCatalog API base URL"
)
@click.option("--sheet-name", help="Excel sheet name (if applicable)")
@click.option(
    "--preview-mapping", is_flag=True, help="Show how data will be mapped before import"
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=True,
    help="Preview mode - don't actually create items",
)
@click.option(
    "--execute", is_flag=True, help="Actually create items (overrides dry-run)"
)
@click.option("--no-auth", is_flag=True, help="Skip OAuth authentication (for testing)")
def main(
    file_path: Path,
    api_url: str,
    sheet_name: Optional[str],
    preview_mapping: bool,
    dry_run: bool,
    execute: bool,
    no_auth: bool,
):
    """Import items from resku spreadsheet to eCatalog API"""

    if execute:
        dry_run = False

    console.print(f"[bold]eCatalog Resku Item Importer[/bold]")
    console.print(f"File: {file_path}")
    console.print(f"API: {api_url}")
    console.print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")

    # Create authenticated client
    if no_auth:
        client = ECatalogAPIClient(api_url)
        console.print("[yellow]Running without authentication[/yellow]")
    else:
        try:
            # Get OAuth credentials from environment
            oauth_token_url = os.getenv("OAUTH_TOKEN_URL", "http://127.0.0.1:8010/token")
            oauth_client_id = os.getenv("OAUTH_CLIENT_ID", "m2m-api-client")
            oauth_client_secret = os.getenv("OAUTH_CLIENT_SECRET")

            if not oauth_client_secret:
                console.print("[red]OAUTH_CLIENT_SECRET not found in environment[/red]")
                console.print("[yellow]Please set OAUTH_CLIENT_SECRET in .env file[/yellow]")
                sys.exit(1)

            oauth_config = OAuthConfig(
                client_id=oauth_client_id,
                client_secret=oauth_client_secret,
                token_url=oauth_token_url,
                use_m2m=True,
                use_pkce=False,
            )
            client = ECatalogAPIClient(api_url, oauth_config=oauth_config)
            client.authenticate_m2m()
            console.print("[green]M2M authentication successful[/green]")
        except Exception as e:
            console.print(f"[red]Authentication failed: {e}[/red]")
            console.print("[yellow]Try using --no-auth flag for testing[/yellow]")
            sys.exit(1)

    importer = ReskuItemImporter(client)

    if preview_mapping:
        importer.preview_data_mapping(file_path, sheet_name)
        return

    # Test API connection with authenticated call
    try:
        # Use a simple authenticated endpoint to test connection
        test_result = client.lookup_sku("TEST_CONNECTION")
        # The lookup may return None but if no exception is raised, connection works
        console.print(f"[green]Connected to API at {api_url}[/green]")
    except Exception as e:
        console.print(f"[red]API connection test failed: {e}[/red]")
        sys.exit(1)

    # Import items
    stats = importer.import_from_spreadsheet(file_path, sheet_name, dry_run)

    # Display results
    console.print(f"\n[bold]Import Results:[/bold]")
    console.print(f"Processed: {stats['processed']}")
    console.print(f"{'Would create' if dry_run else 'Created'}: {stats['created']}")
    console.print(f"Failed: {stats['failed']}")

    if dry_run and stats["created"] > 0:
        console.print(
            f"\n[yellow]Run with --execute to actually create {stats['created']} items[/yellow]"
        )


if __name__ == "__main__":
    main()
