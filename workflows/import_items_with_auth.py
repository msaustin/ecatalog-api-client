#!/usr/bin/env python3

import pandas as pd
import click
from rich.console import Console
from rich.progress import Progress, TaskID
from pathlib import Path
import sys
from typing import Dict, List, Optional

from ecatalog_client import (
    ECatalogAPIClient,
    ItemNew,
    ItemDivisions,
    ItemDivision,
    ItemAttributes,
    OAuthConfig,
)

console = Console()


class ItemImporter:
    def __init__(self, api_client: ECatalogAPIClient):
        self.client = api_client
        self.console = console

    def parse_divisions(self, row: pd.Series) -> ItemDivisions:
        """Parse division data from spreadsheet columns"""
        divisions = {}

        for division in ["FL", "SE", "TX"]:
            # Look for columns like 'FL_Active', 'SE_Active', 'TX_Active' or just 'FL', 'SE', 'TX'
            active_col = f"{division}_Active"
            if active_col in row.index:
                active = bool(row[active_col]) if pd.notna(row[active_col]) else False
            elif division in row.index:
                active = bool(row[division]) if pd.notna(row[division]) else False
            else:
                # Default to False if not specified - requires explicit activation
                active = False

            divisions[division] = ItemDivision(Active=active)

        return ItemDivisions(**divisions)

    def parse_attributes(self, row: pd.Series) -> Optional[ItemAttributes]:
        """Parse item attributes from spreadsheet columns"""
        attributes = {}

        # Map common attribute columns
        attribute_mapping = {
            "Color": ["Color", "Colors", "color"],
            "Decor": ["Decor", "decor"],
            "Finish": ["Finish", "finish"],
            "Features": ["Features", "features"],
            "Material": ["Material", "material"],
            "Movement": ["Movement", "movement"],
            "PieceCount": ["PieceCount", "Piece_Count", "piece_count"],
            "Shape": ["Shape", "shape"],
            "Size": ["Size", "size"],
            "Style": ["Style", "style"],
            "Theme": ["Theme", "theme"],
            "Team": ["Team", "team"],
        }

        for attr_name, possible_columns in attribute_mapping.items():
            for col in possible_columns:
                if col in row.index and pd.notna(row[col]):
                    # Handle comma-separated values
                    value = str(row[col]).strip()
                    if value:
                        attributes[attr_name] = [
                            v.strip() for v in value.split(",") if v.strip()
                        ]
                    break

        return ItemAttributes(**attributes) if attributes else None

    def row_to_item(self, row: pd.Series) -> Optional[ItemNew]:
        """Convert a spreadsheet row to an ItemNew object"""
        try:
            # Required fields mapping
            required_mapping = {
                "Sku": ["New SKU", "New Sku"],
                "Site": ["Site", "site"],
                "Category": ["Ecat Category"],
                "Collection": ["Collection", "collection"],
                "PDMDescription": ["Description", "PDMDescription", "pdm_description"],
                "Title": ["Title", "title", "Item_Title"],
                "AdvertisingCopy": [
                    "Advertising_Copy",
                    "AdvertisingCopy",
                    "advertising_copy",
                ],
                "Dimensions": ["Out Of Box Dim"],
                "Image": ["Ecat Image Name", "Image", "image", "Image_Name"],
                "GenericName": [
                    "Generic Name",
                    "Generic_Name",
                    "GenericName",
                    "generic_name",
                ],
                "DeliveryType": [
                    "Delivery Type",
                    "Delivery_Type",
                    "DeliveryType",
                    "delivery_type",
                ],
            }

            # Extract required fields
            item_data = {}
            missing_fields = []

            for field, possible_columns in required_mapping.items():
                value = None
                for col in possible_columns:
                    if col in row.index and pd.notna(row[col]):
                        value = str(row[col]).strip()
                        break

                if value:
                    item_data[field] = value
                else:
                    missing_fields.append(field)

            if missing_fields:
                console.print(
                    f"[red]Missing required fields for row: {missing_fields}[/red]"
                )
                return None

            # Optional fields
            optional_mapping = {
                "Brand": ["Brand", "brand"],
                "AdditionalNotes": [
                    "Additional_Notes",
                    "AdditionalNotes",
                    "additional_notes",
                    "Notes",
                ],
                "DeliverySubType": [
                    "Delivery_Sub_Type",
                    "DeliverySubType",
                    "delivery_sub_type",
                ],
                "ShippingCode": ["Shipping_Code", "ShippingCode", "shipping_code"],
                "GroupKey": ["Group_Key", "GroupKey", "group_key"],
                "GroupKeyModifier": [
                    "Group_Key_Modifier",
                    "GroupKeyModifier",
                    "group_key_modifier",
                ],
            }

            for field, possible_columns in optional_mapping.items():
                for col in possible_columns:
                    if col in row.index and pd.notna(row[col]):
                        item_data[field] = str(row[col]).strip()
                        break

            # Boolean fields - only set if explicitly provided
            if "Single_Item_Room" in row.index or "SingleItemRoom" in row.index:
                single_room_col = (
                    "Single_Item_Room"
                    if "Single_Item_Room" in row.index
                    else "SingleItemRoom"
                )
                if pd.notna(row[single_room_col]):
                    item_data["SingleItemRoom"] = bool(row[single_room_col])

            # Parse divisions and attributes
            item_data["Divisions"] = self.parse_divisions(row)
            attributes = self.parse_attributes(row)
            if attributes:
                item_data["Attributes"] = attributes

            return ItemNew(**item_data)

        except Exception as e:
            console.print(f"[red]Error creating item from row: {e}[/red]")
            return None

    def import_from_spreadsheet(
        self, file_path: Path, sheet_name: Optional[str] = None, dry_run: bool = True
    ) -> Dict[str, int]:
        """Import items from a spreadsheet file"""

        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return {"processed": 0, "created": 0, "failed": 0}

        try:
            # Read the spreadsheet
            if file_path.suffix.lower() in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            elif file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path)
            else:
                console.print(f"[red]Unsupported file format: {file_path.suffix}[/red]")
                return {"processed": 0, "created": 0, "failed": 0}

            console.print(f"Loaded {len(df)} rows from {file_path}")
            console.print(f"Columns: {', '.join(df.columns.tolist())}")

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
    dry_run: bool,
    execute: bool,
    no_auth: bool,
):
    """Import items from a spreadsheet file to eCatalog API"""

    if execute:
        dry_run = False

    console.print(f"[bold]eCatalog Item Importer[/bold]")
    console.print(f"File: {file_path}")
    console.print(f"API: {api_url}")
    console.print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")

    # Create authenticated client
    if no_auth:
        client = ECatalogAPIClient(api_url)
        console.print("[yellow]Running without authentication[/yellow]")
    else:
        try:
            import os
            from dotenv import load_dotenv

            # Load environment variables from .env file
            load_dotenv()

            # Get OAuth credentials from environment
            oauth_token_url = os.getenv("OAUTH_TOKEN_URL", "http://127.0.0.1:8010/token")
            oauth_client_id = os.getenv("OAUTH_CLIENT_ID", "m2m-api-client")
            oauth_client_secret = os.getenv("OAUTH_CLIENT_SECRET")

            if not oauth_client_secret:
                console.print("[red]OAUTH_CLIENT_SECRET not found in environment[/red]")
                console.print("[yellow]Please set OAUTH_CLIENT_SECRET in .env file or environment variables[/yellow]")
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

    importer = ItemImporter(client)

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
