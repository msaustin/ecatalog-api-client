#!/usr/bin/env python3

import click
import json
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.json import JSON
from dotenv import load_dotenv

from ecatalog_client import (
    ECatalogAPIClient,
    ItemPartialUpdate,
    ItemDeleteRequest,
    SkuSubstitutionRequest,
    SwapRoomItemsRequest,
    RoomItem,
    OAuthConfig,
)

console = Console()

# Load environment variables
load_dotenv()


def create_authenticated_client(api_url: str, manual_auth: bool = False, force_auth: bool = False) -> ECatalogAPIClient:
    """Create an authenticated eCatalog API client using M2M OAuth"""
    # Get OAuth credentials from environment
    oauth_token_url = os.getenv("OAUTH_TOKEN_URL", "http://127.0.0.1:8010/token")
    oauth_client_id = os.getenv("OAUTH_CLIENT_ID", "m2m-api-client")
    oauth_client_secret = os.getenv("OAUTH_CLIENT_SECRET")

    if not oauth_client_secret:
        console.print("[red]OAUTH_CLIENT_SECRET not found in environment[/red]")
        console.print("[yellow]Please set OAUTH_CLIENT_SECRET in .env file or environment variables[/yellow]")
        raise click.Abort()

    oauth_config = OAuthConfig(
        client_id=oauth_client_id,
        client_secret=oauth_client_secret,
        token_url=oauth_token_url,
        use_m2m=True,
        use_pkce=False,
    )

    client = ECatalogAPIClient(api_url, oauth_config=oauth_config)

    try:
        console.print("[yellow]Authenticating with M2M OAuth...[/yellow]")
        client.authenticate_m2m(force_reauth=force_auth)
        console.print("[green]Authentication successful![/green]")

    except Exception as e:
        console.print(f"[red]Authentication failed:[/red] {e}")
        console.print("[yellow]Common issues:[/yellow]")
        console.print("- Make sure your OAuth server is running")
        console.print("- Check that OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET are set correctly in .env")
        console.print("- Verify OAUTH_TOKEN_URL is correct")
        raise click.Abort()

    return client


@click.group()
@click.option(
    "--api-url", default="http://127.0.0.1:8000", help="eCatalog API base URL"
)
@click.option(
    "--no-auth", is_flag=True, help="Skip OAuth authentication (use for testing)"
)
@click.option(
    "--manual-auth", is_flag=True, help="Use manual OAuth flow (copy authorization code)"
)
@click.option(
    "--force-auth", is_flag=True, help="Force re-authentication (ignore cached tokens)"
)
@click.pass_context
def main(ctx, api_url, no_auth, manual_auth, force_auth):
    """eCatalog CLI - Workflow tool for eCatalog API operations"""
    ctx.ensure_object(dict)

    if no_auth:
        # For testing/development - skip OAuth
        ctx.obj["client"] = ECatalogAPIClient(api_url)
    else:
        # Production - use OAuth authentication
        ctx.obj["client"] = create_authenticated_client(api_url, manual_auth=manual_auth, force_auth=force_auth)

    ctx.obj["api_url"] = api_url


@main.command()
@click.argument("sku")
@click.pass_context
def lookup(ctx, sku):
    """Look up a SKU to check its type and availability"""
    client = ctx.obj["client"]

    try:
        result = client.lookup_sku(sku)
        if result:
            console.print(f"[bold green]SKU Found:[/bold green] {sku}")

            table = Table()
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Type", result.type)
            table.add_row("Site", result.site)
            table.add_row("Exists", str(result.exists))
            table.add_row("Divisions", json.dumps(result.divisions, indent=2))

            console.print(table)
        else:
            console.print(f"[red]SKU not found:[/red] {sku}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@main.command()
@click.argument("sku")
@click.pass_context
def details(ctx, sku):
    """Get complete SKU details - looks up SKU type and fetches full item/room details"""
    client = ctx.obj["client"]

    try:
        # Step 1: Look up the SKU to determine its type
        console.print(f"[yellow]Looking up SKU:[/yellow] {sku}")
        lookup_result = client.lookup_sku(sku)

        if not lookup_result:
            console.print(f"[red]SKU not found:[/red] {sku}")
            return

        if not lookup_result.exists:
            console.print(f"[red]SKU exists but is not active:[/red] {sku}")
            console.print(f"Type: {lookup_result.type}, Site: {lookup_result.site}")
            return

        console.print(f"[green]Found {lookup_result.type}:[/green] {sku}")

        # Step 2: Fetch detailed information based on type
        if lookup_result.type.upper() == "ITEM":
            console.print("[yellow]Fetching item details...[/yellow]")
            item = client.get_item(sku)

            if item:
                console.print(f"\n[bold green]ITEM DETAILS:[/bold green] {item.Title}")

                # Display item details in a table
                table = Table()
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="white")

                table.add_row("SKU", item.Sku)
                table.add_row("Site", item.Site)
                table.add_row("Category", item.Category)
                table.add_row("Collection", item.Collection)
                table.add_row("Brand", item.Brand or "")
                table.add_row("Title", item.Title)
                table.add_row("Dimensions", item.Dimensions)
                table.add_row("Generic Name", item.GenericName)
                table.add_row("Delivery Type", item.DeliveryType)

                console.print(table)

                # Display advertising copy
                if item.AdvertisingCopy:
                    console.print(f"\n[bold]Advertising Copy:[/bold]")
                    console.print(
                        item.AdvertisingCopy[:200] + "..."
                        if len(item.AdvertisingCopy) > 200
                        else item.AdvertisingCopy
                    )

            else:
                console.print(f"[red]Could not fetch item details for:[/red] {sku}")

        elif lookup_result.type.upper() == "ROOM":
            console.print("[yellow]Fetching room details...[/yellow]")
            room = client.get_room(sku)

            if room:
                console.print(f"\n[bold green]ROOM DETAILS:[/bold green] {room.Title}")

                table = Table()
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="white")

                table.add_row("SKU", room.Sku)
                table.add_row("Site", room.Site)
                table.add_row("Category", room.Category)
                table.add_row("Collection", room.Collection)
                table.add_row("Title", room.Title or "")

                console.print(table)

                # Display room items if available
                if room.RoomItems:
                    console.print(f"\n[bold]Room Items:[/bold]")
                    for division, items in room.RoomItems.model_dump().items():
                        if items:
                            console.print(f"\n{division} Division:")
                            items_table = Table()
                            items_table.add_column("SKU", style="cyan")
                            items_table.add_column("Quantity", style="white")

                            for item in items:
                                items_table.add_row(item["Sku"], str(item["Quantity"]))
                            console.print(items_table)

            else:
                console.print(f"[red]Could not fetch room details for:[/red] {sku}")

        else:
            console.print(f"[yellow]Unknown SKU type:[/yellow] {lookup_result.type}")
            console.print(f"SKU: {sku}, Site: {lookup_result.site}")

        # Display division information
        console.print(f"\n[bold]Division Availability:[/bold]")
        divisions_table = Table()
        divisions_table.add_column("Division", style="cyan")
        divisions_table.add_column("Status", style="white")

        for division, status in lookup_result.divisions.items():
            if isinstance(status, dict) and "Active" in status:
                status_text = "Active" if status["Active"] else "Inactive"
            else:
                status_text = str(status)
            divisions_table.add_row(division, status_text)

        console.print(divisions_table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@main.group()
def item():
    """Item management commands"""
    pass


@item.command()
@click.argument("sku")
@click.pass_context
def get(ctx, sku):
    """Get item details by SKU"""
    client = ctx.obj["client"]

    try:
        item = client.get_item(sku)
        if item:
            console.print(f"[bold green]Item:[/bold green] {item.Title}")

            # Display item details in a table
            table = Table()
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("SKU", item.Sku)
            table.add_row("Site", item.Site)
            table.add_row("Category", item.Category)
            table.add_row("Collection", item.Collection)
            table.add_row("Brand", item.Brand or "")
            table.add_row("Title", item.Title)
            table.add_row("Dimensions", item.Dimensions)
            table.add_row("Generic Name", item.GenericName)
            table.add_row("Delivery Type", item.DeliveryType)

            console.print(table)

            # Display advertising copy
            if item.AdvertisingCopy:
                console.print(f"\n[bold]Advertising Copy:[/bold]")
                console.print(
                    item.AdvertisingCopy[:200] + "..."
                    if len(item.AdvertisingCopy) > 200
                    else item.AdvertisingCopy
                )

        else:
            console.print(f"[red]Item not found:[/red] {sku}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@item.command()
@click.argument("sku")
@click.option("--title", help="Update item title")
@click.option("--advertising-copy", help="Update advertising copy")
@click.option("--dimensions", help="Update dimensions")
@click.pass_context
def update(ctx, sku, title, advertising_copy, dimensions):
    """Update item fields by SKU"""
    client = ctx.obj["client"]

    # Build update object with provided fields
    update_data = {}
    if title:
        update_data["Title"] = title
    if advertising_copy:
        update_data["AdvertisingCopy"] = advertising_copy
    if dimensions:
        update_data["Dimensions"] = dimensions

    if not update_data:
        console.print(
            "[red]No update fields provided. Use --title, --advertising-copy, or --dimensions[/red]"
        )
        return

    try:
        update_obj = ItemPartialUpdate(**update_data)
        result = client.update_item(sku, update_obj)
        if result:
            console.print(f"[green]Item updated successfully:[/green] {sku}")
            console.print(f"Message: {result.get('message', 'Success')}")
            if "updated_fields" in result:
                console.print(f"Updated fields: {', '.join(result['updated_fields'])}")
        else:
            console.print(f"[red]Failed to update item:[/red] {sku}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@item.command()
@click.argument("sku")
@click.argument("site")
@click.option(
    "--division",
    type=click.Choice(["FL", "SE", "TX"]),
    help="Specific division to delete from",
)
@click.option(
    "--delete-import-data", is_flag=True, help="Also delete import data tables"
)
@click.pass_context
def delete(ctx, sku, site, division, delete_import_data):
    """Delete item by SKU"""
    client = ctx.obj["client"]

    try:
        delete_request = ItemDeleteRequest(
            Site=site, Division=division, DeleteImportData=delete_import_data
        )
        result = client.delete_item(sku, delete_request)
        if result:
            console.print(f"[green]Delete request submitted:[/green] {sku}")
            console.print(f"Message: {result.get('message', 'Success')}")
            if "workrequest_id" in result:
                console.print(f"Work Request ID: {result['workrequest_id']}")
        else:
            console.print(f"[red]Failed to delete item:[/red] {sku}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@main.group()
def room():
    """Room management commands"""
    pass


@room.command()
@click.argument("sku")
@click.pass_context
def get(ctx, sku):
    """Get room details by SKU"""
    client = ctx.obj["client"]

    try:
        room = client.get_room(sku)
        if room:
            console.print(f"[bold green]Room:[/bold green] {room.Title}")

            table = Table()
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("SKU", room.Sku)
            table.add_row("Site", room.Site)
            table.add_row("Category", room.Category)
            table.add_row("Collection", room.Collection)
            table.add_row("Title", room.Title or "")

            console.print(table)

            # Display room items if available
            if room.RoomItems:
                console.print(f"\n[bold]Room Items:[/bold]")
                for division, items in room.RoomItems.model_dump().items():
                    if items:
                        console.print(f"\n{division} Division:")
                        items_table = Table()
                        items_table.add_column("SKU", style="cyan")
                        items_table.add_column("Quantity", style="white")

                        for item in items:
                            items_table.add_row(item["Sku"], str(item["Quantity"]))
                        console.print(items_table)

        else:
            console.print(f"[red]Room not found:[/red] {sku}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@room.command()
@click.argument("sku")
@click.argument("site")
@click.option(
    "--division",
    type=click.Choice(["FL", "SE", "TX"]),
    help="Specific division to delete from",
)
@click.option(
    "--delete-import-data", is_flag=True, help="Also delete import data tables"
)
@click.pass_context
def delete(ctx, sku, site, division, delete_import_data):
    """Delete room by SKU"""
    client = ctx.obj["client"]

    try:
        delete_request = ItemDeleteRequest(
            Site=site, Division=division, DeleteImportData=delete_import_data
        )
        result = client.delete_room(sku, delete_request)
        if result:
            console.print(f"[green]Delete request submitted:[/green] {sku}")
            console.print(f"Message: {result.get('message', 'Success')}")
            if "workrequest_id" in result:
                console.print(f"Work Request ID: {result['workrequest_id']}")
        else:
            console.print(f"[red]Failed to delete room:[/red] {sku}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@room.command()
@click.argument("room_sku")
@click.option("--swap-out", "swap_out_items", multiple=True, required=True, help="Items to swap out (format: SKU:QUANTITY)")
@click.option("--swap-in", "swap_in_items", multiple=True, required=True, help="Items to swap in (format: SKU:QUANTITY)")
@click.option(
    "--division",
    "divisions",
    multiple=True,
    required=True,
    type=click.Choice(["FL", "SE", "TX"]),
    help="Divisions to apply swap (repeat for multiple)",
)
@click.pass_context
def swap_items(ctx, room_sku, swap_out_items, swap_in_items, divisions):
    """Swap items in a room"""
    client = ctx.obj["client"]

    try:
        # Parse swap out items
        swap_out_list = []
        for item_str in swap_out_items:
            if ':' not in item_str:
                console.print(f"[red]Invalid format for swap-out item: {item_str}[/red]")
                console.print("[yellow]Use format: SKU:QUANTITY (e.g., 23056066:1)[/yellow]")
                return
            sku, qty = item_str.split(':', 1)
            swap_out_list.append(RoomItem(Sku=sku.strip(), Quantity=int(qty.strip())))

        # Parse swap in items
        swap_in_list = []
        for item_str in swap_in_items:
            if ':' not in item_str:
                console.print(f"[red]Invalid format for swap-in item: {item_str}[/red]")
                console.print("[yellow]Use format: SKU:QUANTITY (e.g., 2235560P:1)[/yellow]")
                return
            sku, qty = item_str.split(':', 1)
            swap_in_list.append(RoomItem(Sku=sku.strip(), Quantity=int(qty.strip())))

        # Create swap request
        swap_request = SwapRoomItemsRequest(
            RoomSku=room_sku,
            SwapOutRoomItems=swap_out_list,
            SwapInRoomItems=swap_in_list,
            Divisions=list(divisions)
        )

        console.print(f"[yellow]Swapping items in room {room_sku}...[/yellow]")
        result = client.swap_room_items(swap_request)

        if result:
            console.print(f"[green]✅ Room item swap successful[/green]")
            console.print(f"Message: {result.get('message', 'Success')}")
            if 'workrequest_id' in result:
                console.print(f"Work Request ID: {result['workrequest_id']}")
        else:
            console.print(f"[red]Failed to swap room items[/red]")

    except ValueError as e:
        console.print(f"[red]Invalid quantity value: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@main.group()
def substitution():
    """SKU substitution workflow commands"""
    pass


@substitution.command()
@click.option("--site", required=True, help="Site (e.g., RTG, OTG)")
@click.option("--replaced-sku", "replaced_skus", multiple=True, required=True, help="SKUs being replaced (repeat for multiple)")
@click.option("--substituted-sku", "substituted_skus", multiple=True, required=True, help="SKUs to substitute with (repeat for multiple)")
@click.option(
    "--division",
    "divisions",
    multiple=True,
    required=True,
    type=click.Choice(["FL", "SE", "TX"]),
    help="Divisions to apply substitution (repeat for multiple)",
)
@click.option("--package-sku", "package_skus", multiple=True, help="Specific package SKUs to target (repeat for multiple)")
@click.pass_context
def prevalidate(ctx, site, replaced_skus, substituted_skus, divisions, package_skus):
    """Prevalidate a SKU substitution request"""
    client = ctx.obj["client"]

    try:
        # Debug: Print the values being passed
        console.print(f"[blue]Debug - Site:[/blue] {site}")
        console.print(f"[blue]Debug - Replaced SKUs:[/blue] {list(replaced_skus)}")
        console.print(f"[blue]Debug - Substituted SKUs:[/blue] {list(substituted_skus)}")
        console.print(f"[blue]Debug - Divisions:[/blue] {list(divisions)}")
        console.print(f"[blue]Debug - Package SKUs:[/blue] {list(package_skus) if package_skus else None}")

        substitution_req = SkuSubstitutionRequest(
            Site=site,
            ReplacedSkus=list(replaced_skus),
            SubstitutedSkus=list(substituted_skus),
            Divisions=list(divisions),
            PackageSkus=list(package_skus) if package_skus else None,
        )

        result = client.prevalidate_sku_substitution(substitution_req)
        if result:
            console.print(f"[bold]Prevalidation Result:[/bold]")
            console.print(
                f"Valid: [{'green' if result.get('valid') else 'red'}]{result.get('valid')}[/]"
            )

            if result.get("validation_results"):
                console.print(f"\n[bold]Validation Details:[/bold]")
                console.print(JSON(json.dumps(result["validation_results"], indent=2)))

            if result.get("errors"):
                console.print(f"\n[red]Errors:[/red]")
                for error in result["errors"]:
                    console.print(f"  • {error}")

            if result.get("warnings"):
                console.print(f"\n[yellow]Warnings:[/yellow]")
                for warning in result["warnings"]:
                    console.print(f"  • {warning}")
        else:
            console.print("[red]Prevalidation failed[/red]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@main.group()
def workflow():
    """Workflow scripts for bulk operations"""
    pass


@workflow.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--sheet-name", help="Excel sheet name (if applicable)")
@click.option(
    "--execute", is_flag=True, help="Actually create items (default is dry-run)"
)
@click.pass_context
def import_items(ctx, file_path, sheet_name, execute):
    """Import items from spreadsheet file (generic format)"""
    from workflows.import_items import ItemImporter
    import pandas as pd
    from pathlib import Path

    client = ctx.obj["client"]
    file_path = Path(file_path)

    dry_run = not execute
    if dry_run:
        console.print(
            "[yellow]DRY RUN MODE - Use --execute to actually create items[/yellow]"
        )

    importer = ItemImporter(client)
    stats = importer.import_from_spreadsheet(file_path, sheet_name, dry_run)

    console.print(f"\n[bold]Results:[/bold]")
    console.print(f"Processed: {stats['processed']}")
    console.print(f"{'Would create' if dry_run else 'Created'}: {stats['created']}")
    console.print(f"Failed: {stats['failed']}")


@workflow.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--sheet-name", help="Excel sheet name (if applicable)")
@click.option("--limit", type=int, help="Limit to first N rows for testing")
@click.option("--preview-mapping", is_flag=True, help="Show how data will be mapped")
@click.option(
    "--execute", is_flag=True, help="Actually create items (default is dry-run)"
)
@click.pass_context
def import_resku_items(ctx, file_path, sheet_name, limit, preview_mapping, execute):
    """Import items from resku spreadsheet format"""
    from workflows.import_resku_items import ReskuItemImporter
    from pathlib import Path

    client = ctx.obj["client"]
    file_path = Path(file_path)

    importer = ReskuItemImporter(client)

    if preview_mapping:
        importer.preview_data_mapping(file_path, sheet_name)
        return

    dry_run = not execute
    if dry_run:
        console.print(
            "[yellow]DRY RUN MODE - Use --execute to actually create items[/yellow]"
        )

    if limit:
        console.print(f"[blue]Testing mode: Processing only first {limit} rows[/blue]")

    stats = importer.import_from_spreadsheet(file_path, sheet_name, dry_run, limit)

    console.print(f"\n[bold]Results:[/bold]")
    console.print(f"Processed: {stats['processed']}")
    console.print(f"{'Would create' if dry_run else 'Created'}: {stats['created']}")
    console.print(f"Failed: {stats['failed']}")


@workflow.command()
@click.pass_context
def sku_substitution(ctx):
    """Interactive SKU substitution prevalidation workflow"""
    from workflows.sku_substitution import SkuSubstitutionWorkflow

    client = ctx.obj["client"]

    workflow = SkuSubstitutionWorkflow(client)
    success = workflow.run_interactive_prevalidation()

    if success:
        console.print("\n[green]✅ Workflow completed successfully![/green]")
    else:
        console.print("\n[red]❌ Workflow completed with issues or was cancelled.[/red]")


@workflow.command()
@click.argument("file_path", type=click.Path(path_type=Path), required=False)
@click.option("--sheet-name", help="Excel sheet name (if applicable)")
@click.pass_context
def dropship(ctx, file_path, sheet_name):
    """End-to-end workflow for dropship items"""
    from workflows.dropship_workflow import DropshipWorkflow
    from pathlib import Path

    client = ctx.obj["client"]

    # Handle file selection
    if file_path is None:
        from pathlib import Path
        project_root = Path.cwd()
        default_dir = project_root / "data" / "dropship"

        # List Excel files
        excel_files = list(default_dir.glob("*.xlsx")) + list(default_dir.glob("*.xls"))

        if not excel_files:
            console.print(f"[red]No Excel files found in {default_dir}[/red]")
            console.print("Please specify a file path or add Excel files to the dropship directory")
            return

        # If only one file, use it automatically
        if len(excel_files) == 1:
            file_path = excel_files[0]
            console.print(f"[green]Using file: {file_path.name}[/green]")
        else:
            # Let user choose from available files
            console.print(f"[bold]Found {len(excel_files)} Excel files in {default_dir}:[/bold]")
            for i, f in enumerate(excel_files, 1):
                console.print(f"  {i}. {f.name}")

            while True:
                try:
                    choice = click.prompt("Select file number", type=int)
                    if 1 <= choice <= len(excel_files):
                        file_path = excel_files[choice - 1]
                        break
                    else:
                        console.print(f"[red]Please enter a number between 1 and {len(excel_files)}[/red]")
                except click.Abort:
                    console.print("[yellow]Operation cancelled[/yellow]")
                    return
                except (ValueError, IndexError):
                    console.print("[red]Invalid selection[/red]")
    else:
        file_path = Path(file_path)

    # Verify file exists
    if not file_path.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        return

    # Run the workflow
    workflow = DropshipWorkflow(client)
    success = workflow.run_end_to_end_workflow(file_path, sheet_name)

    if success:
        console.print("\n[green]✅ Workflow completed successfully![/green]")
    else:
        console.print("\n[red]❌ Workflow completed with issues or was cancelled.[/red]")


@workflow.command()
@click.argument("file_path", type=click.Path(path_type=Path), required=False)
@click.option("--sheet-name", help="Excel sheet name (if applicable)")
@click.pass_context
def room_item_swap(ctx, file_path, sheet_name):
    """End-to-end workflow for room item swaps"""
    from workflows.room_item_swap_workflow import RoomItemSwapWorkflow
    from pathlib import Path

    client = ctx.obj["client"]

    # Handle file selection
    if file_path is None:
        from pathlib import Path
        project_root = Path.cwd()
        default_dir = project_root / "data" / "room_item_swap"

        # List Excel files
        excel_files = list(default_dir.glob("*.xlsx")) + list(default_dir.glob("*.xls"))

        if not excel_files:
            console.print(f"[red]No Excel files found in {default_dir}[/red]")
            console.print("Please specify a file path or add Excel files to the room_item_swap directory")
            return

        # If only one file, use it automatically
        if len(excel_files) == 1:
            file_path = excel_files[0]
            console.print(f"[green]Using file: {file_path.name}[/green]")
        else:
            # Let user choose from available files
            console.print(f"[bold]Found {len(excel_files)} Excel files in {default_dir}:[/bold]")
            for i, f in enumerate(excel_files, 1):
                console.print(f"  {i}. {f.name}")

            while True:
                try:
                    choice = click.prompt("Select file number", type=int)
                    if 1 <= choice <= len(excel_files):
                        file_path = excel_files[choice - 1]
                        break
                    else:
                        console.print(f"[red]Please enter a number between 1 and {len(excel_files)}[/red]")
                except click.Abort:
                    console.print("[yellow]Operation cancelled[/yellow]")
                    return
                except (ValueError, IndexError):
                    console.print("[red]Invalid selection[/red]")
    else:
        file_path = Path(file_path)

    # Verify file exists
    if not file_path.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        return

    # Run the workflow
    workflow = RoomItemSwapWorkflow(client)
    success = workflow.run_end_to_end_workflow(file_path, sheet_name)

    if success:
        console.print("\n[green]✅ Workflow completed successfully![/green]")
    else:
        console.print("\n[red]❌ Workflow completed with issues or was cancelled.[/red]")


@workflow.command()
@click.argument("file_path", type=click.Path(path_type=Path), required=False)
@click.option("--sheet-name", help="Excel sheet name (if applicable)")
@click.pass_context
def rtg_delivered(ctx, file_path, sheet_name):
    """End-to-end workflow for RTG delivered products"""
    from workflows.rtg_delivered_workflow import RtgDeliveredWorkflow
    from pathlib import Path

    client = ctx.obj["client"]

    # Handle file selection
    if file_path is None:
        from pathlib import Path
        project_root = Path.cwd()
        default_dir = project_root / "data" / "rtg_delivered"

        # List Excel files
        excel_files = list(default_dir.glob("*.xlsx")) + list(default_dir.glob("*.xls"))

        if not excel_files:
            console.print(f"[red]No Excel files found in {default_dir}[/red]")
            console.print("Please specify a file path or add Excel files to the rtg_delivered directory")
            return

        # If only one file, use it automatically
        if len(excel_files) == 1:
            file_path = excel_files[0]
            console.print(f"[green]Using file: {file_path.name}[/green]")
        else:
            # Let user choose from available files
            console.print(f"[bold]Found {len(excel_files)} Excel files in {default_dir}:[/bold]")
            for i, f in enumerate(excel_files, 1):
                console.print(f"  {i}. {f.name}")

            while True:
                try:
                    choice = click.prompt("Select file number", type=int)
                    if 1 <= choice <= len(excel_files):
                        file_path = excel_files[choice - 1]
                        break
                    else:
                        console.print(f"[red]Please enter a number between 1 and {len(excel_files)}[/red]")
                except click.Abort:
                    console.print("[yellow]Operation cancelled[/yellow]")
                    return
                except (ValueError, IndexError):
                    console.print("[red]Invalid selection[/red]")
    else:
        file_path = Path(file_path)

    # Verify file exists
    if not file_path.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        return

    # Run the workflow
    workflow = RtgDeliveredWorkflow(client)
    success = workflow.run_end_to_end_workflow(file_path, sheet_name)

    if success:
        console.print("\n[green]✅ Workflow completed successfully![/green]")
    else:
        console.print("\n[red]❌ Workflow completed with issues or was cancelled.[/red]")


@workflow.command()
@click.argument("file_path", type=click.Path(path_type=Path), required=False)
@click.option("--sheet-name", help="Excel sheet name (if applicable)")
@click.pass_context
def sku_substitution(ctx, file_path, sheet_name):
    """End-to-end workflow for SKU substitution from file"""
    from workflows.sku_substitution_file_workflow import SkuSubstitutionFileWorkflow
    from pathlib import Path

    client = ctx.obj["client"]

    # Handle file selection
    if file_path is None:
        from pathlib import Path
        project_root = Path.cwd()
        default_dir = project_root / "data" / "sku_substitution"

        # List Excel files
        excel_files = list(default_dir.glob("*.xlsx")) + list(default_dir.glob("*.xls"))

        if not excel_files:
            console.print(f"[red]No Excel files found in {default_dir}[/red]")
            console.print("Please specify a file path or add Excel files to the sku_substitution directory")
            return

        # If only one file, use it automatically
        if len(excel_files) == 1:
            file_path = excel_files[0]
            console.print(f"[green]Using file: {file_path.name}[/green]")
        else:
            # Let user choose from available files
            console.print(f"[bold]Found {len(excel_files)} Excel files in {default_dir}:[/bold]")
            for i, f in enumerate(excel_files, 1):
                console.print(f"  {i}. {f.name}")

            while True:
                try:
                    choice = click.prompt("Select file number", type=int)
                    if 1 <= choice <= len(excel_files):
                        file_path = excel_files[choice - 1]
                        break
                    else:
                        console.print(f"[red]Please enter a number between 1 and {len(excel_files)}[/red]")
                except click.Abort:
                    console.print("[yellow]Operation cancelled[/yellow]")
                    return
                except (ValueError, IndexError):
                    console.print("[red]Invalid selection[/red]")

    # Verify file exists
    if not file_path.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        return

    # Run the workflow
    workflow = SkuSubstitutionFileWorkflow(client)
    success = workflow.run_end_to_end_workflow(file_path, sheet_name)

    if success:
        console.print("\n[green]✅ Workflow completed successfully![/green]")
    else:
        console.print("\n[red]❌ Workflow completed with issues or was cancelled.[/red]")


@main.command()
@click.option("--workflow", type=click.Choice(["dropship", "rtg-delivered", "room-item-swap", "sku-substitution", "all"]), default="all", help="Specific workflow to clean (default: all)")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def clean(ctx, workflow, confirm):
    """Clean JSON files from workflow directories"""
    from pathlib import Path
    from rich.prompt import Confirm

    project_root = Path.cwd()

    # Define workflow directories
    workflows_to_clean = {
        "dropship": project_root / "data" / "dropship" / "json",
        "rtg-delivered": project_root / "data" / "rtg_delivered" / "json",
        "room-item-swap": project_root / "data" / "room_item_swap" / "json",
        "sku-substitution": project_root / "data" / "sku_substitution" / "json"
    }

    # Filter based on selection
    if workflow != "all":
        workflows_to_clean = {workflow: workflows_to_clean[workflow]}

    # Count files to delete
    total_files = 0
    file_counts = {}
    for name, json_dir in workflows_to_clean.items():
        if json_dir.exists():
            json_files = list(json_dir.glob("*.json"))
            file_counts[name] = len(json_files)
            total_files += len(json_files)
        else:
            file_counts[name] = 0

    if total_files == 0:
        console.print("[yellow]No JSON files found to clean[/yellow]")
        return

    # Display what will be deleted
    console.print(f"[bold]Files to be deleted:[/bold]")
    for name, count in file_counts.items():
        if count > 0:
            console.print(f"  {name}: [cyan]{count}[/cyan] JSON files")
    console.print(f"\n[bold]Total: [cyan]{total_files}[/cyan] files[/bold]")

    # Confirm deletion
    if not confirm:
        if not Confirm.ask("\nAre you sure you want to delete these files?", default=False):
            console.print("[yellow]Operation cancelled[/yellow]")
            return

    # Delete files
    deleted_count = 0
    for name, json_dir in workflows_to_clean.items():
        if json_dir.exists():
            json_files = list(json_dir.glob("*.json"))
            for json_file in json_files:
                try:
                    json_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    console.print(f"[red]Error deleting {json_file.name}: {e}[/red]")

    console.print(f"[green]✅ Successfully deleted {deleted_count} JSON files[/green]")


@main.command()
@click.pass_context
def status(ctx):
    """Check API server status"""
    client = ctx.obj["client"]
    api_url = ctx.obj["api_url"]

    try:
        response = client.session.get(f"{api_url}/")
        if response.status_code == 200:
            console.print(f"[green]✓ API server is running at {api_url}[/green]")
        else:
            console.print(
                f"[red]✗ API server responded with status {response.status_code}[/red]"
            )
    except Exception as e:
        console.print(f"[red]✗ Cannot connect to API server at {api_url}[/red]")
        console.print(f"Error: {e}")


@main.group()
@click.pass_context
def workrequest(ctx):
    """Work request management commands"""
    # Context is inherited from main command
    pass


@workrequest.command()
@click.argument("workrequest_id", type=int)
@click.pass_context
def get(ctx, workrequest_id):
    """Get work request details by ID"""
    client = ctx.obj["client"]

    try:
        result = client.get_workrequest(workrequest_id)
        if result:
            console.print(f"[bold green]Work Request {workrequest_id}:[/bold green]")

            table = Table()
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")

            for key, value in result.items():
                table.add_row(str(key), str(value))

            console.print(table)
        else:
            console.print(f"[red]Work request not found:[/red] {workrequest_id}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@workrequest.command("list")
@click.option("--status", help="Filter by status (PENDING, RUNNING, COMPLETED, FAILED)")
@click.option("--route-name", help="Filter by route name")
@click.pass_context
def list_workrequests(ctx, status, route_name):
    """List work requests"""
    client = ctx.obj["client"]

    try:
        results = client.list_workrequests(status=status, route_name=route_name)
        if results:
            console.print(f"[bold green]Work Requests:[/bold green]")

            table = Table()
            table.add_column("ID", style="cyan")
            table.add_column("Status", style="white")
            table.add_column("Route", style="white")
            table.add_column("Created", style="white")

            for wr in results:
                table.add_row(
                    str(wr.get('id', '')),
                    wr.get('status', ''),
                    wr.get('route_name', ''),
                    str(wr.get('created_at', ''))[:19] if wr.get('created_at') else ''
                )

            console.print(table)
            console.print(f"\n[blue]Found {len(results)} work request(s)[/blue]")
        else:
            console.print("[yellow]No work requests found[/yellow]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@workrequest.command()
@click.argument("workrequest_id", type=int)
@click.argument("additional_ids", nargs=-1, type=int)
@click.pass_context
def process(ctx, workrequest_id, additional_ids):
    """Process one or more work requests by ID"""
    client = ctx.obj["client"]

    try:
        # Combine all work request IDs into a single list
        workrequest_ids = [workrequest_id] + list(additional_ids)
        console.print(f"[yellow]Processing work request(s): {', '.join(map(str, workrequest_ids))}[/yellow]")
        result = client.process_workrequests(workrequest_ids)

        if result:
            console.print("[green]✅ Work request processing initiated[/green]")
            if result.get('message'):
                console.print(f"Message: {result['message']}")

            # Debug: print result type and content
            console.print(f"[blue]Result type: {type(result)}[/blue]")
            console.print(f"[blue]Result content: {result}[/blue]")

            try:
                console.print(JSON(json.dumps(result, indent=2)))
            except Exception as json_error:
                console.print(f"[yellow]Could not format as JSON: {json_error}[/yellow]")
                console.print(f"Raw result: {result}")
        else:
            console.print("[red]Failed to process work requests[/red]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        import traceback
        console.print(f"[red]Traceback:[/red]")
        console.print(traceback.format_exc())


@workrequest.command()
@click.argument("flow_type", type=click.Choice(["product_creation", "product_update", "room_item_swap", "product_deletion", "sku_substitution"]))
@click.option("--workrequest-ids", multiple=True, type=int, help="Specific work request IDs to process")
@click.pass_context
def process_workflows(ctx, flow_type, workrequest_ids):
    """Process workflows by flow type"""
    client = ctx.obj["client"]

    try:
        wr_ids = list(workrequest_ids) if workrequest_ids else None
        console.print(f"[yellow]Processing {flow_type} workflows[/yellow]")

        if wr_ids:
            console.print(f"[blue]Filtering to work request IDs: {', '.join(map(str, wr_ids))}[/blue]")

        result = client.process_workflows(flow_type, wr_ids)

        if result:
            console.print(f"[green]✅ Workflow processing initiated[/green]")
            console.print(JSON(json.dumps(result, indent=2)))
        else:
            console.print("[red]Failed to process workflows[/red]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@main.command()
@click.pass_context
def logout(ctx):
    """Clear cached authentication tokens"""
    client = ctx.obj["client"]

    try:
        if hasattr(client, 'clear_token_cache'):
            client.clear_token_cache()
            console.print("[green]✓ Authentication tokens cleared[/green]")
            console.print("[yellow]You will need to re-authenticate on next API call[/yellow]")
        else:
            console.print("[yellow]No cached tokens to clear (OAuth not configured)[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Failed to clear tokens: {e}[/red]")


if __name__ == "__main__":
    main()
