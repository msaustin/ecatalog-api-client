#!/usr/bin/env python3

import pandas as pd
import click
import os
import shutil
import subprocess
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from rich.prompt import Confirm
from pathlib import Path
import sys
import json
import re
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

# Special-case categories that require exact formatting (non-standard colon spacing)
# Key should be normalized (lowercase, no spaces around colons) for matching
# Value is the exact required format for the API
SPECIAL_CASE_CATEGORIES = {
    "kids:accessories:pillows/throws": "Kids : Accessories: Pillows/throws",
    "adult:accessories:pillows/throws": "Adult : Accessories: Pillows/throws",
    "outdoor:accessories:pillows/throws": "Outdoor : Accessories: Pillows/throws",
    "adult:living room:chairs": "Adult : Livingroom : Chairs",
    "living room:chairs": "Adult : Livingroom : Chairs",
    "adult:living room:ottomans": "Adult : Livingroom : Ottomans",
    "living room:ottomans": "Adult : Livingroom : Ottomans",
    # Add more special cases here as needed
    # "adult:bedroom:chest/hutch": "Adult : Bedroom: Chest/Hutch",
}

# Special-case categories without site prefix (2-part format)
# These will have the site prefix added, then matched to SPECIAL_CASE_CATEGORIES
SPECIAL_CASE_CATEGORIES_NO_PREFIX = {
    "accessories:pillows/throws": "Accessories: Pillows/throws",
    # Add more special cases here as needed
}


def correct_common_data_errors(text: str, field_type: str = None) -> str:
    """
    Correct common data errors found in spreadsheets

    Args:
        text: Input text to correct
        field_type: Type of field ('category', 'decor', etc.) for specific corrections

    Returns:
        Corrected text
    """
    if not text or not isinstance(text, str):
        return text

    corrected = text

    # Category-specific corrections
    if field_type == "category":
        # Fix "Livingroom" -> "Living Room"
        corrected = corrected.replace("Livingroom", "Living Room")
        corrected = corrected.replace("Accessoreis", "Accessories")
        corrected = corrected.replace("Décor", "Decor")
        corrected = corrected.replace("Wall Dcor", "Wall Decor")
        corrected = corrected.replace(
            "Livingroom : Cocktail Tables", "Living Room : Cocktail Tables"
        )
        corrected = corrected.replace(
            "Kids : Accessories : Pillows/throws", "Kids : Accessories: Pillows/throws"
        )
        corrected = corrected.replace(
            "Accessories : Pillows/Throws", "Accessories: Pillows/throws"
        )
        corrected = corrected.replace("Cocktail Tables", "Cocktail Table")

    # Decor attribute corrections
    elif field_type == "decor":
        # Fix "Mid Century Modern" -> "Mid-Century Modern"
        corrected = corrected.replace("Mid Century Modern", "Mid-Century Modern")

        # Fix "Mid Century" (standalone) -> "Mid-Century Modern"
        if corrected == "Mid Century" or corrected == "MID CENTURY":
            corrected = "Mid-Century Modern"

    elif field_type == "size":
        corrected = corrected.replace('48" + Extra Large', '48"+ Extra Large')
        corrected = corrected.replace("48' + Extra Large", '48"+ Extra Large')

        corrected = corrected.replace('36"-48" Large', '36" - 48" Large')
        corrected = corrected.replace('24"-36" Medium', '24" - 36" Medium')
        corrected = corrected.replace('24"-36" Medium', '24" - 36" Medium')
        corrected = corrected.replace("24' - 36\" Medium", '24" - 36" Medium')
        corrected = corrected.replace('>24" Small', 'Under 24" Small')
        corrected = corrected.replace('<24" Small', 'Under 24" Small')

        if corrected == "Extra Large":
            corrected = '48" + Extra Large'
        if corrected == "Large":
            corrected = '36" - 48" Large'
        if corrected == "Medium":
            corrected = '24" - 36" Medium'
        if corrected == "Small":
            corrected = 'Under 24" Small'

        # --categories that do not end in "s"
        # select * from category where cat_title not like '%s' and cat_isselectable = 1

        # ending in "Posturepedic"
        # ending in "Bedding"
        # ending in "Only"
        # ending in "Foundation"

        # Chest/Hutch
        # Wall Decor
        # Seating
        # Storage
        # Fuel
        # Accent Furniture
        # Home Entertainment
        # Racing Collection

    # Add more corrections here as needed
    # corrected = corrected.replace("OtherWrongTerm", "CorrectTerm")

    return corrected


def smart_title_case(text: str) -> str:
    """
    Apply title case with special handling for roman numerals and acronyms

    Args:
        text: Input text to convert

    Returns:
        Text with proper title casing
    """
    if not text or not isinstance(text, str):
        return text

    # Roman numerals (common ones used in furniture/collections)
    roman_numerals = {
        "I",
        "II",
        "III",
        "IV",
        "V",
        "VI",
        "VII",
        "VIII",
        "IX",
        "X",
        "XI",
        "XII",
        "XIII",
        "XIV",
        "XV",
        "XVI",
        "XVII",
        "XVIII",
        "XIX",
        "XX",
    }

    # Sports and other acronyms that should stay uppercase
    acronyms = {
        "NFL",
        "MLB",
        "NBA",
        "NHL",
        "NCAA",
        "MLS",
        "UFC",
        "WWE",
        "ESPN",
        "USA",
        "US",
        "UK",
        "EU",
        "LED",
        "USB",
        "WIFI",
        "GPS",
        "DVD",
        "CD",
        "TV",
        "HD",
        "LCD",
        "OLED",
        "AC",
        "DC",
        "AM",
        "PM",
        "CEO",
        "CFO",
        "DIY",
        "FAQ",
        "PDF",
        "HTML",
        "CSS",
        "JS",
        "API",
        "URL",
        "SEO",
        "RTG",
        "OTG",
        "KTG",  # Site codes
    }

    # Words that should be lowercase (articles, prepositions, conjunctions)
    lowercase_words = {
        "a",
        "an",
        "and",
        "as",
        "at",
        "but",
        "by",
        "for",
        "if",
        "in",
        "nor",
        "of",
        "on",
        "or",
        "so",
        "the",
        "to",
        "up",
        "yet",
        "with",
        "from",
    }

    # Split text into words, preserving spaces and punctuation
    words = re.findall(r"\S+|\s+", text.strip())

    result = []
    for i, word in enumerate(words):
        if word.isspace():
            result.append(word)
            continue

        # Clean word for checking (remove punctuation for comparison)
        clean_word = re.sub(r"[^\w]", "", word).upper()

        # First word is always capitalized
        if i == 0 or (
            i > 0 and words[i - 1].isspace() and any(c in words[i - 1] for c in ".!?")
        ):
            if clean_word in roman_numerals:
                # Replace the roman numeral part with correct case
                result.append(
                    re.sub(r"[a-zA-Z]+", clean_word, word, flags=re.IGNORECASE)
                )
            elif clean_word in acronyms:
                # Replace the acronym part with uppercase
                result.append(
                    re.sub(r"[a-zA-Z]+", clean_word, word, flags=re.IGNORECASE)
                )
            else:
                result.append(word.capitalize())
        else:
            # Check for special cases
            if clean_word in roman_numerals:
                result.append(
                    re.sub(r"[a-zA-Z]+", clean_word, word, flags=re.IGNORECASE)
                )
            elif clean_word in acronyms:
                result.append(
                    re.sub(r"[a-zA-Z]+", clean_word, word, flags=re.IGNORECASE)
                )
            elif clean_word.lower() in lowercase_words:
                result.append(word.lower())
            else:
                result.append(word.capitalize())

    return "".join(result)


class DropshipItemImporter:
    def __init__(self, api_client: ECatalogAPIClient):
        self.client = api_client
        self.console = console

    def parse_divisions_from_regionlist(self, region_list: str) -> ItemDivisions:
        """Parse division data from RegionList field (comma-separated)"""
        # Start with all divisions as None (null)
        divisions = {"FL": None, "SE": None, "TX": None}

        if pd.notna(region_list):
            region_str = str(region_list).upper()
            # Parse comma-separated regions - set specified divisions to Active=False
            regions = [r.strip() for r in region_str.split(",") if r.strip()]
            for region in regions:
                if region == "FL":
                    divisions["FL"] = ItemDivision(Active=False)
                elif region == "SE":
                    divisions["SE"] = ItemDivision(Active=False)
                elif region == "TX":
                    divisions["TX"] = ItemDivision(Active=False)

        return ItemDivisions(**divisions)

    def parse_attributes_from_row(self, row: pd.Series) -> Optional[ItemAttributes]:
        """Parse item attributes from spreadsheet columns"""
        attributes = {}

        # Direct mapping from dropship spreadsheet to API attributes
        attribute_mapping = {
            "Color": "Color",
            "Decor": "Decor",
            "Finish": "Finish",
            "Features": "Features",
            "Material": "Material",
            "Movement": "Movement",
            "PieceCount": "PieceCount",
            "Shape": "Shape",  # Not in sample but keeping for completeness
            "Size": "Size",
            "Style": "Style",
            "Theme": "Theme",  # Not in sample but keeping for completeness
            "Team": "team",  # Dropship specific - lowercase
        }

        for api_field, spreadsheet_col in attribute_mapping.items():
            if spreadsheet_col in row.index and pd.notna(row[spreadsheet_col]):
                value = str(row[spreadsheet_col]).strip()
                if value:
                    # Apply common data corrections for specific attributes
                    if api_field == "Decor":
                        value = correct_common_data_errors(value, "decor")
                    elif api_field == "Size":
                        value = correct_common_data_errors(value, "size")

                    # Handle comma-separated values
                    corrected_values = []
                    for v in value.split(","):
                        v_clean = v.strip()
                        if v_clean:
                            # Apply corrections to each value in comma-separated list
                            if api_field == "Decor":
                                v_clean = correct_common_data_errors(v_clean, "decor")
                            elif api_field == "Size":
                                v_clean = correct_common_data_errors(v_clean, "size")
                            corrected_values.append(v_clean)

                    if corrected_values:
                        attributes[api_field] = corrected_values

        return ItemAttributes(**attributes) if attributes else None

    def row_to_item(self, row: pd.Series) -> Optional[ItemNew]:
        """Convert a spreadsheet row to an ItemNew object"""
        try:
            # Field mapping from dropship spreadsheet columns to API fields
            field_mapping = {
                "Sku": "Sku",
                "Site": "site",
                "Collection": "Collection",
                "Category": "Category",
                "PDMDescription": "VendorDescription",
                "Title": "Name",
                "AdvertisingCopy": "Advertising Copy",
                "Image": "Image",
                "AdditionalNotes": "Notes",
                "Dimensions": "Dimensions",
                "GenericName": "GenericName",
                "DeliveryType": "DeliveryType",
                "ShippingCode": "ShippingCode",
            }

            # Optional fields with defaults
            optional_mapping = {
                "Brand": ("Brand", ""),
            }

            # Extract required fields
            item_data = {}
            missing_fields = []

            for api_field, spreadsheet_col in field_mapping.items():
                if spreadsheet_col in row.index and pd.notna(row[spreadsheet_col]):
                    value = str(row[spreadsheet_col]).strip()
                    if value:
                        # Apply smart title case to Collection field
                        if api_field == "Collection":
                            value = smart_title_case(value)
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
                        # Apply smart title case to Collection field
                        if api_field == "Collection":
                            value = smart_title_case(value)
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

            # Special handling for Category field - expand to full 3-part format if needed
            if "Category" in item_data and item_data["Category"]:
                category = item_data["Category"]

                # Apply common data corrections to category
                category = correct_common_data_errors(category, "category")

                # Normalize for lookup: lowercase, remove spaces around colons
                normalized_category = (
                    category.lower()
                    .replace(" : ", ":")
                    .replace(": ", ":")
                    .replace(" :", ":")
                )

                # Check if this is a special-case category (3-part with site prefix already)
                if normalized_category in SPECIAL_CASE_CATEGORIES:
                    # Use the exact required format from our special cases registry
                    item_data["Category"] = SPECIAL_CASE_CATEGORIES[normalized_category]
                # Check if this is a 2-part special case that needs site prefix added
                elif normalized_category in SPECIAL_CASE_CATEGORIES_NO_PREFIX:
                    # Determine site prefix
                    site = item_data.get("Site", "").upper()
                    catalog_prefix = ""
                    if site == "RTG":
                        catalog_prefix = "adult"
                    elif site == "KTG":
                        catalog_prefix = "kids"
                    elif site == "OTG":
                        catalog_prefix = "outdoor"

                    # Build the normalized 3-part category key
                    if catalog_prefix:
                        normalized_with_prefix = (
                            f"{catalog_prefix}:{normalized_category}"
                        )
                        # Check if the prefixed version exists in our special cases
                        if normalized_with_prefix in SPECIAL_CASE_CATEGORIES:
                            item_data["Category"] = SPECIAL_CASE_CATEGORIES[
                                normalized_with_prefix
                            ]
                        else:
                            console.print(
                                f"[yellow]Warning: Special case '{normalized_category}' needs prefix but '{normalized_with_prefix}' not found in registry for SKU {row.get('Sku', 'Unknown')}[/yellow]"
                            )
                            return None
                    else:
                        console.print(
                            f"[red]Cannot determine site prefix for special case category '{category}' for SKU {row.get('Sku', 'Unknown')}[/red]"
                        )
                        return None
                else:
                    # Standard category processing
                    # Split on ":" delimiter (without spaces) and trim whitespace from each part
                    parts = [part.strip() for part in category.split(":")]

                    # Filter out empty parts
                    parts = [part for part in parts if part]

                    # Category must have at least 2 parts (category : subcategory)
                    if len(parts) < 2:
                        console.print(
                            f"[red]Invalid category format for SKU {row.get('Sku', 'Unknown')}: '{category}' - must have at least 'Category : Subcategory' format[/red]"
                        )
                        return None

                    # If category has exactly 2 parts, add catalog prefix based on site
                    if len(parts) == 2:
                        site = item_data.get("Site", "").upper()
                        catalog_prefix = ""
                        if site == "RTG":
                            catalog_prefix = "Adult"
                        elif site == "KTG":
                            catalog_prefix = "Kids"
                        elif site == "OTG":
                            catalog_prefix = "Outdoor"

                        if catalog_prefix:
                            parts.insert(0, catalog_prefix)

                    # Join parts with " : " (with spaces)
                    item_data["Category"] = " : ".join(parts)

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
                console.print(
                    f"[dim]Available columns: {', '.join(row.index.tolist())}[/dim]"
                )
                return None

            # Category should be present in dropship files

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

            # Parse divisions from RegionList field
            region_list = row.get("RegionList", "")
            item_data["Divisions"] = self.parse_divisions_from_regionlist(region_list)

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
                    f"\n[cyan]Row {i + 1} - SKU: {row.get('Sku', 'N/A')}[/cyan]"
                )

                table = Table()
                table.add_column("API Field", style="yellow")
                table.add_column("Spreadsheet Column", style="cyan")
                table.add_column("Value", style="white")

                # Show key mappings for dropship format
                key_mappings = [
                    ("Sku", "Sku"),
                    ("Site", "site"),
                    ("Category", "Category"),
                    ("Title", "Name"),
                    ("RegionList/Divisions", "RegionList"),
                    ("GenericName", "GenericName"),
                    ("DeliveryType", "DeliveryType"),
                    ("Brand", "Brand"),
                    ("Vendor", "Vendor"),
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
        export_json: bool = False,
    ) -> Dict[str, any]:
        """Import items from the dropship spreadsheet"""

        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return {"processed": 0, "created": 0, "failed": 0, "workrequest_ids": []}

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
                return {
                    "processed": 0,
                    "created": 0,
                    "failed": 0,
                    "workrequest_ids": [],
                }

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

            stats = {"processed": 0, "created": 0, "failed": 0, "workrequest_ids": []}

            # Create JSON output directory if needed
            json_output_dir = None
            if export_json:
                json_output_dir = Path(
                    "/Users/maust/Documents/CURSOR/prboardcli/data/dropship/json"
                )
                json_output_dir.mkdir(parents=True, exist_ok=True)
                console.print(
                    f"[blue]JSON payloads will be exported to: {json_output_dir}[/blue]"
                )

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

                    # Export JSON payload if requested
                    if export_json and json_output_dir:
                        try:
                            # Create JSON payload using same method as API call
                            item_payload = item.model_dump(
                                by_alias=True, exclude_none=True
                            )
                            json_filename = f"{item.Sku}.json"
                            json_filepath = json_output_dir / json_filename

                            with open(json_filepath, "w") as f:
                                json.dump(item_payload, f, indent=2)

                            console.print(f"[dim]Exported JSON: {json_filename}[/dim]")
                        except Exception as e:
                            console.print(
                                f"[yellow]Warning: Failed to export JSON for {item.Sku}: {e}[/yellow]"
                            )

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
                                    stats["workrequest_ids"].append(workrequest_id)
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
            return {"processed": 0, "created": 0, "failed": 0, "workrequest_ids": []}


def handle_file_archiving(file_path: Path) -> bool:
    """Handle archiving of the processed Excel file"""
    try:
        # Ask user if they want to archive the file
        should_archive = Confirm.ask(
            f"\nArchive {file_path.name} to /data/dropship/archive/?", default=True
        )

        if not should_archive:
            console.print("[dim]Skipping file archiving[/dim]")
            return True

        # Create archive directory if it doesn't exist
        project_root = Path(__file__).parent.parent
        archive_dir = project_root / "data" / "dropship" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Generate archive filename with timestamp if file already exists
        archive_path = archive_dir / file_path.name
        if archive_path.exists():
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = file_path.stem
            suffix = file_path.suffix
            archive_path = archive_dir / f"{stem}_{timestamp}{suffix}"

        # Move the file to archive
        shutil.move(str(file_path), str(archive_path))
        console.print(f"[green]✅ File archived to: {archive_path}[/green]")
        return True

    except Exception as e:
        console.print(f"[red]Failed to archive file: {e}[/red]")
        return False


@click.command()
@click.argument("file_path", type=click.Path(path_type=Path), required=False)
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
@click.option(
    "--export-json",
    is_flag=True,
    help="Export JSON payloads to /data/dropship/json/ directory",
)
def main(
    file_path: Optional[Path],
    api_url: str,
    sheet_name: Optional[str],
    preview_mapping: bool,
    dry_run: bool,
    execute: bool,
    no_auth: bool,
    export_json: bool,
):
    """Import items from dropship spreadsheet to eCatalog API"""

    if execute:
        dry_run = False

    # Handle default directory and file selection
    if file_path is None:
        project_root = Path(__file__).parent.parent
        default_dir = project_root / "data" / "dropship"

        # List Excel files in the dropship directory
        excel_files = list(default_dir.glob("*.xlsx")) + list(default_dir.glob("*.xls"))

        if not excel_files:
            console.print(f"[red]No Excel files found in {default_dir}[/red]")
            console.print(
                "Please specify a file path or add Excel files to the dropship directory"
            )
            return

        # If only one file, use it automatically
        if len(excel_files) == 1:
            file_path = excel_files[0]
            console.print(f"[green]Using file: {file_path.name}[/green]")
        else:
            # Let user choose from available files
            console.print(
                f"[bold]Found {len(excel_files)} Excel files in {default_dir}:[/bold]"
            )
            for i, f in enumerate(excel_files, 1):
                console.print(f"  {i}. {f.name}")

            while True:
                try:
                    choice = click.prompt("Select file number", type=int)
                    if 1 <= choice <= len(excel_files):
                        file_path = excel_files[choice - 1]
                        break
                    else:
                        console.print(
                            f"[red]Please enter a number between 1 and {len(excel_files)}[/red]"
                        )
                except click.Abort:
                    console.print("[yellow]Operation cancelled[/yellow]")
                    return
                except (ValueError, IndexError):
                    console.print("[red]Invalid selection[/red]")

    # Verify file exists
    if not file_path.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        return

    console.print("[bold]eCatalog Dropship Item Importer[/bold]")
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
            oauth_token_url = os.getenv(
                "OAUTH_TOKEN_URL", "http://127.0.0.1:8010/token"
            )
            oauth_client_id = os.getenv("OAUTH_CLIENT_ID", "m2m-api-client")
            oauth_client_secret = os.getenv("OAUTH_CLIENT_SECRET")

            if not oauth_client_secret:
                console.print("[red]OAUTH_CLIENT_SECRET not found in environment[/red]")
                console.print(
                    "[yellow]Please set OAUTH_CLIENT_SECRET in .env file[/yellow]"
                )
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

    importer = DropshipItemImporter(client)

    if preview_mapping:
        importer.preview_data_mapping(file_path, sheet_name)
        return

    # Test API connection with authenticated call
    try:
        # Use a simple authenticated endpoint to test connection
        client.lookup_sku("TEST_CONNECTION")
        # The lookup may return None but if no exception is raised, connection works
        console.print(f"[green]Connected to API at {api_url}[/green]")
    except Exception as e:
        console.print(f"[red]API connection test failed: {e}[/red]")
        sys.exit(1)

    # Import items
    stats = importer.import_from_spreadsheet(
        file_path, sheet_name, dry_run, export_json=export_json
    )

    # Display results
    console.print("\n[bold]Import Results:[/bold]")
    console.print(f"Processed: {stats['processed']}")
    console.print(f"{'Would create' if dry_run else 'Created'}: {stats['created']}")
    console.print(f"Failed: {stats['failed']}")

    if dry_run and stats["created"] > 0:
        console.print(
            f"\n[yellow]Run with --execute to actually create {stats['created']} items[/yellow]"
        )
    elif not dry_run and stats["created"] > 0:
        # Get work request IDs that were created
        workrequest_ids = stats.get("workrequest_ids", [])

        if workrequest_ids:
            console.print(
                f"\n[blue]Created {len(workrequest_ids)} work request(s)[/blue]"
            )

            # Ask if user wants to process all work requests
            should_process = Confirm.ask(
                "\nProcess all work requests now?", default=True
            )

            if should_process:
                # Build the command to run
                wr_ids_str = " ".join(map(str, workrequest_ids))
                console.print(
                    f"\n[yellow]Processing work requests: {wr_ids_str}[/yellow]"
                )

                try:
                    result = subprocess.run(
                        ["uv", "run", "cli.py", "workrequest", "process"]
                        + [str(wr_id) for wr_id in workrequest_ids],
                        cwd=Path(__file__).parent.parent,
                        capture_output=True,
                        text=True,
                    )

                    # Display the output
                    if result.stdout:
                        console.print(result.stdout)
                    if result.stderr:
                        console.print(f"[red]{result.stderr}[/red]")

                    if result.returncode == 0:
                        console.print(
                            "[green]✅ Work requests processed successfully[/green]"
                        )
                    else:
                        console.print(
                            f"[red]❌ Work request processing failed with exit code {result.returncode}[/red]"
                        )

                except Exception as e:
                    console.print(
                        f"[red]Error running work request processing: {e}[/red]"
                    )
            else:
                console.print("[dim]Skipping work request processing[/dim]")

        # Only offer archiving if items were actually created (not in dry-run mode)
        archive_success = handle_file_archiving(file_path)
        if not archive_success:
            console.print(
                "[yellow]⚠️ File archiving failed, but import completed successfully[/yellow]"
            )


if __name__ == "__main__":
    main()
