#!/usr/bin/env python3

"""
End-to-End RTG Delivered Workflow

This script provides a complete workflow for processing RTG delivered files:
1. Dry-run import with JSON export and validation
2. User confirmation for live import
3. Live import with work request collection
4. Batch work request processing
5. Status monitoring with progress display
"""

import click
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from rich.panel import Panel
from dotenv import load_dotenv

from ecatalog_client import ECatalogAPIClient, OAuthConfig
from workflows.import_rtg_delivered_items import RtgDeliveredItemImporter

console = Console()

# Load environment variables
load_dotenv()


class RtgDeliveredWorkflow:
    """Complete end-to-end RTG delivered processing workflow"""

    def __init__(self, api_client: ECatalogAPIClient):
        self.client = api_client
        self.console = console
        self.importer = RtgDeliveredItemImporter(api_client)

    def run_end_to_end_workflow(self, file_path: Path, sheet_name: Optional[str] = None) -> bool:
        """Run the complete RTG delivered workflow"""
        try:
            console.print(Panel.fit("[bold blue]🚀 RTG Delivered End-to-End Workflow[/bold blue]"))
            console.print(f"Processing file: [cyan]{file_path.name}[/cyan]\n")

            # Step 1: Dry run with validation
            console.print("[bold]Step 1: Dry Run Validation & JSON Export[/bold]")
            validation_results = self._run_dry_run_validation(file_path, sheet_name)

            if not validation_results:
                console.print("[red]❌ Dry run validation failed[/red]")
                return False

            # Step 2: Display validation summary
            self._display_validation_summary(validation_results)

            # Step 3: User confirmation
            if not self._get_user_confirmation(validation_results):
                console.print("[yellow]Workflow cancelled by user[/yellow]")
                return False

            # Step 4: Live import with work request collection
            console.print("\n[bold]Step 4: Live Import & Work Request Collection[/bold]")
            work_request_ids = self._run_live_import(file_path, sheet_name)

            if not work_request_ids:
                console.print("[red]❌ Live import failed - no work requests created[/red]")
                return False

            # Step 5: Batch process work requests
            console.print(f"\n[bold]Step 5: Processing {len(work_request_ids)} Work Requests[/bold]")
            processing_success = self._process_work_requests(work_request_ids)

            if not processing_success:
                console.print("[red]❌ Work request processing failed[/red]")
                return False

            # Step 6: Initial status check
            console.print("\n[bold]Step 6: Work Request Status Check[/bold]")
            console.print(f"[blue]✅ {len(work_request_ids)} work requests submitted for processing[/blue]")
            console.print("[yellow]Note: Real-time monitoring is disabled until server provides better status updates[/yellow]")

            # Perform one final status check
            final_status = self._get_final_status_summary(work_request_ids)

            # Step 7: Final summary
            self._display_final_summary(final_status)

            # Step 8: Archive file if requested
            archive_success = self._handle_file_archiving(file_path)
            if not archive_success:
                console.print("[yellow]⚠️ File archiving failed, but workflow completed successfully[/yellow]")

            return True

        except KeyboardInterrupt:
            console.print("\n[yellow]Workflow cancelled by user[/yellow]")
            return False
        except Exception as e:
            console.print(f"[red]Workflow error: {e}[/red]")
            return False

    def _run_dry_run_validation(self, file_path: Path, sheet_name: Optional[str]) -> Optional[Dict]:
        """Run dry-run import with JSON export and collect validation results"""
        try:
            console.print("[blue]Running dry-run validation and exporting JSON payloads...[/blue]")

            # Capture validation errors
            validation_errors = []
            original_console_print = console.print

            def capture_validation_errors(*args, **kwargs):
                message = str(args[0]) if args else ""
                if "[red]" in message and ("SKU" in message or "Missing" in message or "Invalid" in message):
                    validation_errors.append(message)
                original_console_print(*args, **kwargs)

            # Temporarily replace console.print to capture errors
            console.print = capture_validation_errors

            try:
                # Run dry-run with JSON export
                stats = self.importer.import_from_spreadsheet(
                    file_path, sheet_name, dry_run=True, export_json=True
                )
            finally:
                # Restore original console.print
                console.print = original_console_print

            return {
                'stats': stats,
                'file_path': file_path,
                'sheet_name': sheet_name,
                'validation_errors': validation_errors
            }

        except Exception as e:
            console.print(f"[red]Dry run validation error: {e}[/red]")
            return None

    def _display_validation_summary(self, results: Dict) -> None:
        """Display validation results summary"""
        stats = results['stats']

        table = Table(title="🔍 Validation Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="white", justify="right")
        table.add_column("Status", style="green")

        table.add_row("Total Records", str(stats['processed']), "✅ Processed")
        table.add_row("Valid Records", str(stats['created']), "✅ Ready for Import")
        table.add_row("Failed Records", str(stats['failed']), "❌ Validation Failed" if stats['failed'] > 0 else "✅ All Valid")

        console.print(table)

        if stats['failed'] > 0:
            console.print(f"\n[red]⚠️  {stats['failed']} records failed validation[/red]")

            # Display specific validation errors
            validation_errors = results.get('validation_errors', [])
            if validation_errors:
                console.print("\n[bold red]Validation Errors:[/bold red]")
                for error in validation_errors[:10]:  # Show first 10 errors
                    clean_error = error.replace("[red]", "").replace("[/red]", "").strip()
                    console.print(f"  • {clean_error}")

                if len(validation_errors) > 10:
                    console.print(f"  ... and {len(validation_errors) - 10} more errors")
            else:
                console.print("[dim]Check the console output above for specific validation errors[/dim]")

    def _get_user_confirmation(self, results: Dict) -> bool:
        """Get user confirmation to proceed with live import"""
        stats = results['stats']

        if stats['failed'] > 0:
            console.print(f"\n[yellow]⚠️  Warning: {stats['failed']} records will be skipped due to validation errors[/yellow]")

        if stats['created'] == 0:
            console.print("[red]No valid records to import[/red]")
            return False

        console.print(f"\n[bold green]Ready to import {stats['created']} valid records[/bold green]")
        return Confirm.ask("Proceed with live import?", default=False)

    def _run_live_import(self, file_path: Path, sheet_name: Optional[str]) -> List[int]:
        """Run live import and collect work request IDs"""
        work_request_ids = []

        try:
            stats = self._import_with_workrequest_collection(file_path, sheet_name, work_request_ids)

            console.print(f"[green]✅ Import completed: {stats['created']} items created[/green]")
            console.print(f"[blue]📋 Collected {len(work_request_ids)} work request IDs[/blue]")

            return work_request_ids

        except Exception as e:
            console.print(f"[red]Live import error: {e}[/red]")
            return []

    def _import_with_workrequest_collection(self, file_path: Path, sheet_name: Optional[str],
                                          work_request_ids: List[int]) -> Dict[str, int]:
        """Import items and collect work request IDs"""
        return self._enhanced_import_from_spreadsheet(file_path, sheet_name, work_request_ids)

    def _enhanced_import_from_spreadsheet(self, file_path: Path, sheet_name: Optional[str],
                                        work_request_ids: List[int]) -> Dict[str, int]:
        """Enhanced import that captures work request IDs from API responses"""
        import pandas as pd
        from rich.progress import Progress

        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return {"processed": 0, "created": 0, "failed": 0}

        try:
            # Read the spreadsheet
            if file_path.suffix.lower() in [".xlsx", ".xls"]:
                if sheet_name is None:
                    sheet_name = 0
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            elif file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path)
            else:
                console.print(f"[red]Unsupported file format: {file_path.suffix}[/red]")
                return {"processed": 0, "created": 0, "failed": 0}

            # Filter rows based on "Build in" status
            total_rows = len(df)
            filtered_df = df[df.apply(self.importer.should_import_row, axis=1)]
            filtered_count = len(filtered_df)
            skipped_count = total_rows - filtered_count

            console.print(
                f"[blue]Filtered: {filtered_count} rows with 'Build in' status, {skipped_count} rows skipped[/blue]"
            )

            if filtered_count == 0:
                console.print("[yellow]No rows found with 'Build in' status to import[/yellow]")
                return {"processed": 0, "created": 0, "failed": 0}

            df = filtered_df
            console.print(f"[bold]Processing {len(df)} records for live import...[/bold]")
            stats = {"processed": 0, "created": 0, "failed": 0}

            with Progress() as progress:
                task = progress.add_task("Creating items...", total=len(df))

                for _, row in df.iterrows():
                    stats["processed"] += 1

                    # Convert row to ItemNew object
                    item = self.importer.row_to_item(row)
                    if not item:
                        stats["failed"] += 1
                        progress.update(task, advance=1)
                        continue

                    # Actually create the item and capture work request ID
                    try:
                        result = self.client.create_item(item)
                        if result:
                            # Extract work request ID
                            workrequest_id = result.get("workrequest_id")
                            if workrequest_id:
                                work_request_ids.append(workrequest_id)
                                console.print(f"[green]✅ {item.Sku}[/green] [dim]→ Work Request: {workrequest_id}[/dim]")
                            else:
                                console.print(f"[green]✅ {item.Sku}[/green] [yellow]→ No work request ID returned[/yellow]")
                            stats["created"] += 1
                        else:
                            console.print(f"[red]❌ Failed to create: {item.Sku}[/red]")
                            stats["failed"] += 1
                    except Exception as e:
                        console.print(f"[red]❌ Error creating {item.Sku}: {e}[/red]")
                        stats["failed"] += 1

                    progress.update(task, advance=1)

            return stats

        except Exception as e:
            console.print(f"[red]Error reading spreadsheet: {e}[/red]")
            return {"processed": 0, "created": 0, "failed": 0}

    def _process_work_requests(self, work_request_ids: List[int]) -> bool:
        """Process work requests in batch"""
        try:
            console.print(f"[blue]Submitting {len(work_request_ids)} work requests for processing...[/blue]")

            result = self.client.process_workrequests(work_request_ids)

            if result:
                console.print("[green]✅ Work requests submitted for processing[/green]")
                return True
            else:
                console.print("[red]❌ Failed to submit work requests for processing[/red]")
                return False

        except Exception as e:
            console.print(f"[red]Work request processing error: {e}[/red]")
            return False

    def _get_final_status_summary(self, work_request_ids: List[int]) -> Dict[str, int]:
        """Get a simple status summary without real-time monitoring"""
        console.print("[blue]Checking current status of work requests...[/blue]")

        try:
            status_counts = self._check_all_work_request_status(work_request_ids)
            console.print(f"[dim]Status check completed for {len(work_request_ids)} work requests[/dim]")
            return status_counts

        except Exception as e:
            console.print(f"[yellow]Status check failed: {e}[/yellow]")
            return {
                "PENDING": len(work_request_ids),
                "RUNNING": 0,
                "COMPLETED": 0,
                "FAILED": 0
            }

    def _check_all_work_request_status(self, work_request_ids: List[int]) -> Dict[str, int]:
        """Check status of all work requests"""
        status_counts = {"PENDING": 0, "RUNNING": 0, "COMPLETED": 0, "FAILED": 0}

        for wr_id in work_request_ids:
            try:
                wr_details = self.client.get_workrequest(wr_id)
                if wr_details and 'status' in wr_details:
                    status = wr_details['status'].upper()
                    if status in status_counts:
                        status_counts[status] += 1
                    else:
                        status_counts["PENDING"] += 1
                else:
                    status_counts["PENDING"] += 1
            except Exception:
                status_counts["PENDING"] += 1

        return status_counts

    def _display_final_summary(self, final_status: Dict[str, int]) -> None:
        """Display final workflow summary"""
        console.print(Panel.fit("[bold green]🎉 Workflow Complete![/bold green]"))

        table = Table(title="📋 Final Results")
        table.add_column("Status", style="cyan")
        table.add_column("Count", justify="right")

        for status, count in final_status.items():
            color = "green" if status == "COMPLETED" else "red" if status == "FAILED" else "yellow"
            table.add_row(status, f"[{color}]{count}[/{color}]")

        console.print(table)

        if final_status["FAILED"] > 0:
            console.print(f"[red]⚠️  {final_status['FAILED']} work requests failed[/red]")
            console.print("[dim]Use CLI work request commands to check individual failure reasons[/dim]")

        console.print("\n[blue]💡 Next Steps:[/blue]")
        console.print("• Use [bold]uv run python cli.py workrequest list[/bold] to see all work requests")
        console.print("• Use [bold]uv run python cli.py workrequest get <ID>[/bold] to check specific work request status")
        console.print("• Work requests may take time to complete - check back later if still pending")

    def _handle_file_archiving(self, file_path: Path) -> bool:
        """Handle archiving of the processed Excel file"""
        try:
            should_archive = Confirm.ask(f"\nArchive {file_path.name} to /data/rtg_delivered/archive/?", default=True)

            if not should_archive:
                console.print("[dim]Skipping file archiving[/dim]")
                return True

            # Create archive directory
            project_root = Path(__file__).parent.parent
            archive_dir = project_root / "data" / "rtg_delivered" / "archive"
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
@click.argument('file_path', type=click.Path(path_type=Path), required=False)
@click.option('--api-url', default='http://127.0.0.1:8000', help='eCatalog API base URL')
@click.option('--sheet-name', help='Excel sheet name (if applicable)')
@click.option('--no-auth', is_flag=True, help='Skip OAuth authentication (for testing)')
def main(file_path: Optional[Path], api_url: str, sheet_name: Optional[str], no_auth: bool):
    """Run complete end-to-end RTG delivered workflow"""

    # Handle default directory and file selection
    if file_path is None:
        project_root = Path(__file__).parent.parent
        default_dir = project_root / "data" / "rtg_delivered"

        # List Excel files in the rtg_delivered directory
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

    # Verify file exists
    if not file_path.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        return

    console.print(f"[bold]🚀 RTG Delivered End-to-End Workflow[/bold]")
    console.print(f"File: {file_path}")
    console.print(f"API: {api_url}\n")

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
                return

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
            return

    # Test API connection
    try:
        client.lookup_sku("TEST_CONNECTION")
        console.print(f"[green]Connected to API at {api_url}[/green]")
        console.print("")  # Empty line
    except Exception as e:
        console.print(f"[red]API connection test failed: {e}[/red]")
        return

    # Run the complete workflow
    workflow = RtgDeliveredWorkflow(client)
    success = workflow.run_end_to_end_workflow(file_path, sheet_name)

    if success:
        console.print("\n[bold green]🎉 Workflow completed successfully![/bold green]")
    else:
        console.print("\n[bold red]❌ Workflow failed or was cancelled[/bold red]")


if __name__ == '__main__':
    main()