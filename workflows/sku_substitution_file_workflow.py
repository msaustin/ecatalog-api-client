#!/usr/bin/env python3

"""
End-to-End SKU Substitution File Workflow

This script provides a complete workflow for processing SKU substitution files:
1. Dry-run validation with JSON export
2. User confirmation for live submission
3. Live submission with work request collection
4. Batch work request processing
5. Logging of all operations

Expects Excel/CSV files with columns:
- Division (FL, SE, TX)
- Old Sku (replaced SKU)
- New Sku (substituted SKU)
- Package Skus (optional, comma-separated)
"""

import click
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from rich.panel import Panel
from dotenv import load_dotenv

from ecatalog_client import ECatalogAPIClient, OAuthConfig
from workflows.import_sku_substitution import SkuSubstitutionImporter
from workflows.workflow_logger import WorkflowLogger

console = Console()

# Load environment variables
load_dotenv()


class SkuSubstitutionFileWorkflow:
    """Complete end-to-end SKU substitution file processing workflow"""

    def __init__(self, api_client: ECatalogAPIClient):
        self.client = api_client
        self.console = console
        self.importer = SkuSubstitutionImporter(api_client)

        # Initialize workflow logger
        project_root = Path(__file__).parent.parent
        logs_dir = project_root / "data" / "sku_substitution" / "logs"
        self.logger = WorkflowLogger("sku_substitution", logs_dir)

    def run_end_to_end_workflow(self, file_path: Path, sheet_name: Optional[str] = None) -> bool:
        """Run the complete SKU substitution workflow"""
        try:
            console.print(Panel.fit("[bold blue]🔄 SKU Substitution End-to-End Workflow[/bold blue]"))
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

            # Step 4: Live submission with work request collection
            console.print("\n[bold]Step 4: Live Submission & Work Request Collection[/bold]")
            work_request_ids, substitution_keys, substitution_details = self._run_live_submission(file_path, sheet_name)

            if not work_request_ids:
                console.print("[yellow]⚠️ No work requests were created[/yellow]")
                console.print("[yellow]Check if substitutions were processed synchronously[/yellow]")
                return True

            # Step 5: Batch process work requests
            console.print(f"\n[bold]Step 5: Processing {len(work_request_ids)} Work Requests[/bold]")
            processing_success = self._process_work_requests(file_path.name, substitution_details, work_request_ids)

            if not processing_success:
                console.print("[red]❌ Work request processing failed[/red]")
                return False

            # Step 6: Completion summary
            console.print("\n[bold]Step 6: Workflow Complete[/bold]")
            console.print(f"[blue]✅ {len(work_request_ids)} work requests submitted for processing[/blue]")
            console.print("[yellow]Note: Use 'workrequest list' or 'workrequest get <id>' to check status[/yellow]")

            # Step 7: Display work request IDs
            self._display_work_request_summary(work_request_ids)

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
            import traceback
            console.print(traceback.format_exc())
            return False

    def _run_dry_run_validation(self, file_path: Path, sheet_name: Optional[str]) -> Optional[Dict]:
        """Run dry-run validation with JSON export"""
        try:
            console.print("[blue]Running dry-run validation and exporting JSON payloads...[/blue]")

            stats = self.importer.import_from_spreadsheet(
                file_path, sheet_name, dry_run=True, export_json=True
            )

            return {
                'stats': stats,
                'file_path': file_path,
                'sheet_name': sheet_name,
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

        table.add_row("Total Requests", str(stats['processed']), "✅ Processed")
        table.add_row("Valid Requests", str(stats['created']), "✅ Ready for Submission")
        table.add_row("Failed Validation", str(stats['failed']), "❌ Invalid" if stats['failed'] > 0 else "✅ All Valid")

        console.print(table)

        if stats['failed'] > 0:
            console.print(f"\n[red]⚠️  {stats['failed']} request(s) failed validation[/red]")
            console.print("[dim]Check the console output above for specific validation errors[/dim]")

    def _get_user_confirmation(self, results: Dict) -> bool:
        """Get user confirmation to proceed with live submission"""
        stats = results['stats']

        if stats['failed'] > 0:
            console.print(f"\n[yellow]⚠️  Warning: {stats['failed']} request(s) will be skipped due to validation errors[/yellow]")

        if stats['created'] == 0:
            console.print("[red]No valid requests to submit[/red]")
            return False

        console.print(f"\n[bold green]Ready to submit {stats['created']} valid substitution request(s)[/bold green]")
        console.print("[yellow]⚠️  This will make real changes to the system![/yellow]")
        return Confirm.ask("Proceed with live submission?", default=False)

    def _run_live_submission(self, file_path: Path, sheet_name: Optional[str]) -> Tuple[List[int], List[str], List[Dict]]:
        """Run live submission and collect work request IDs"""
        work_request_ids = []
        substitution_keys = []

        try:
            console.print("[blue]Submitting SKU substitution requests...[/blue]")

            stats = self.importer.import_from_spreadsheet(
                file_path, sheet_name, dry_run=False, export_json=False
            )

            work_request_ids = stats.get('work_request_ids', [])
            substitution_keys = stats.get('substitution_keys', [])
            substitution_details = stats.get('substitution_details', [])

            console.print(f"[green]✅ Submission completed: {stats['created']} request(s) submitted[/green]")
            console.print(f"[blue]📋 Collected {len(work_request_ids)} work request IDs[/blue]")

            # Log the submission with detailed substitution info
            status = "Success" if stats['failed'] == 0 else "Partial"
            notes = f"Submitted: {stats['created']}, Failed: {stats['failed']}" if stats['failed'] > 0 else ""
            self._log_substitution_operation(
                action="Import",
                source_file=file_path.name,
                substitution_details=substitution_details,
                work_request_ids=work_request_ids,
                status=status,
                notes=notes
            )

            return work_request_ids, substitution_keys, substitution_details

        except Exception as e:
            console.print(f"[red]Live submission error: {e}[/red]")

            # Log the failed submission
            self._log_substitution_operation(
                action="Import",
                source_file=file_path.name,
                substitution_details=substitution_details if substitution_details else [],
                work_request_ids=work_request_ids,
                status="Failed",
                notes=str(e)
            )
            return [], [], []

    def _process_work_requests(self, source_file: str, substitution_details: List[Dict], work_request_ids: List[int]) -> bool:
        """Process work requests in batch"""
        try:
            console.print(f"[blue]Submitting {len(work_request_ids)} work requests for processing...[/blue]")

            # Use the client's process_workrequests method
            result = self.client.process_workrequests(work_request_ids)

            if result:
                console.print("[green]✅ Work requests submitted for processing[/green]")

                # Log the processing with detailed substitution info
                self._log_substitution_operation(
                    action="Submit",
                    source_file=source_file,
                    substitution_details=substitution_details,
                    work_request_ids=work_request_ids,
                    status="Success",
                    notes="Work requests submitted for batch processing"
                )
                return True
            else:
                console.print("[red]❌ Failed to submit work requests for processing[/red]")

                # Log the failure
                self._log_substitution_operation(
                    action="Submit",
                    source_file=source_file,
                    substitution_details=substitution_details,
                    work_request_ids=work_request_ids,
                    status="Failed",
                    notes="Failed to submit work requests"
                )
                return False

        except Exception as e:
            console.print(f"[red]Work request processing error: {e}[/red]")

            # Log the error
            self._log_substitution_operation(
                action="Submit",
                source_file=source_file,
                substitution_details=substitution_details,
                work_request_ids=work_request_ids,
                status="Failed",
                notes=str(e)
            )
            return False

    def _log_substitution_operation(
        self,
        action: str,
        source_file: str,
        substitution_details: List[Dict],
        work_request_ids: List[int],
        status: str,
        notes: str
    ) -> None:
        """
        Log SKU substitution operation with detailed substitution data.
        Creates a log entry with Division, Old SKU, New SKU, and Package SKUs columns.
        """
        import pandas as pd
        from datetime import datetime

        try:
            log_path = self.logger._get_log_file_path()

            # Check if log file exists and load it
            if log_path.exists():
                try:
                    df = pd.read_excel(log_path)
                except Exception:
                    df = pd.DataFrame()
            else:
                df = pd.DataFrame()

            # Create new DataFrame with SKU substitution-specific columns if empty
            if df.empty:
                df = pd.DataFrame(columns=[
                    'Timestamp',
                    'Action',
                    'Source File',
                    'Division',
                    'Old SKUs',
                    'New SKUs',
                    'Package SKUs',
                    'Work Request IDs',
                    'Work Request Count',
                    'Status',
                    'Notes'
                ])

            # Add a row for each substitution detail
            for i, detail in enumerate(substitution_details):
                # Get the corresponding work request ID if available
                wr_id = work_request_ids[i] if i < len(work_request_ids) else ""

                new_row = {
                    'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'Action': action,
                    'Source File': source_file,
                    'Division': detail.get('division', ''),
                    'Old SKUs': detail.get('old_skus', ''),
                    'New SKUs': detail.get('new_skus', ''),
                    'Package SKUs': detail.get('package_skus', ''),
                    'Work Request IDs': str(wr_id) if wr_id else '',
                    'Work Request Count': 1 if wr_id else 0,
                    'Status': status,
                    'Notes': notes
                }

                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # Save to Excel
            df.to_excel(log_path, index=False, engine='openpyxl')

            self.logger.logger.info(
                f"Logged {action} operation: {len(substitution_details)} substitution(s), "
                f"{len(work_request_ids)} work requests"
            )

        except Exception as e:
            self.logger.logger.error(f"Failed to log substitution operation: {e}")
            # Don't raise - logging failures shouldn't stop workflow

    def _display_work_request_summary(self, work_request_ids: List[int]) -> None:
        """Display work request IDs for reference"""
        if not work_request_ids:
            return

        console.print(f"\n[bold]Work Request IDs:[/bold]")

        # Display in groups of 10 for readability
        for i in range(0, len(work_request_ids), 10):
            batch = work_request_ids[i:i+10]
            console.print(f"  {', '.join(map(str, batch))}")

    def _handle_file_archiving(self, file_path: Path) -> bool:
        """Handle archiving of the processed Excel file"""
        try:
            # Ask user if they want to archive the file
            should_archive = Confirm.ask(f"\nArchive {file_path.name} to /data/sku_substitution/archive/?", default=True)

            if not should_archive:
                console.print("[dim]Skipping file archiving[/dim]")
                return True

            # Create archive directory if it doesn't exist
            project_root = Path(__file__).parent.parent
            archive_dir = project_root / "data" / "sku_substitution" / "archive"
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
    """Run complete end-to-end SKU substitution workflow"""

    # Handle default directory and file selection
    if file_path is None:
        project_root = Path(__file__).parent.parent
        default_dir = project_root / "data" / "sku_substitution"

        # List Excel files in the sku_substitution directory
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

    console.print(f"[bold]🔄 SKU Substitution End-to-End Workflow[/bold]")
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
        test_result = client.lookup_sku("TEST_CONNECTION")
        console.print(f"[green]Connected to API at {api_url}[/green]\n")
    except Exception as e:
        console.print(f"[red]API connection test failed: {e}[/red]")
        return

    # Run the complete workflow
    workflow = SkuSubstitutionFileWorkflow(client)
    success = workflow.run_end_to_end_workflow(file_path, sheet_name)

    if success:
        console.print("\n[bold green]🎉 Workflow completed successfully![/bold green]")
    else:
        console.print("\n[bold red]❌ Workflow failed or was cancelled[/bold red]")


if __name__ == '__main__':
    main()
