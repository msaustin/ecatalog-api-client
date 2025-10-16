#!/usr/bin/env python3

"""
End-to-End Room Item Swap Workflow

This script provides a complete workflow for processing room item swap files:
1. Dry-run import with JSON export and validation (each room swap gets its own JSON file)
2. User confirmation for live import
3. Live import with work request collection (one work request per room swap)
4. Individual work request processing (for traceability and isolation)
5. Display work request IDs for manual status checking

Note: Each room swap is processed independently with its own work request
for better traceability and isolation. This ensures that failures in one
room swap do not affect others.

Status monitoring is intentionally disabled to avoid database lock conflicts
while work requests are being processed. Use 'workrequest list' or
'workrequest get <id>' commands to check status manually.
"""

import click
import json
import os
import time
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.prompt import Confirm
from rich.panel import Panel
from dotenv import load_dotenv

from ecatalog_client import ECatalogAPIClient, OAuthConfig
from workflows.import_room_item_swap import RoomItemSwapImporter
from workflows.workflow_logger import WorkflowLogger

console = Console()

# Load environment variables
load_dotenv()


class RoomItemSwapWorkflow:
    """Complete end-to-end room item swap processing workflow"""

    def __init__(self, api_client: ECatalogAPIClient):
        self.client = api_client
        self.console = console
        self.importer = RoomItemSwapImporter(api_client)

        # Initialize workflow logger
        project_root = Path(__file__).parent.parent
        logs_dir = project_root / "data" / "room_item_swap" / "logs"
        self.logger = WorkflowLogger("room_item_swap", logs_dir)

    def run_end_to_end_workflow(self, file_path: Path, sheet_name: Optional[str] = None) -> bool:
        """Run the complete room item swap workflow"""
        try:
            console.print(Panel.fit("[bold blue]🔄 Room Item Swap End-to-End Workflow[/bold blue]"))
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
            work_request_ids, room_skus = self._run_live_import(file_path, sheet_name)

            if not work_request_ids:
                console.print("[yellow]⚠️ No work requests were created (swaps may have completed synchronously)[/yellow]")
                # This is not necessarily an error - some operations may complete immediately
                console.print("[green]✅ Room item swaps completed[/green]")
                return True

            # Step 5: Batch process work requests
            console.print(f"\n[bold]Step 5: Processing {len(work_request_ids)} Work Requests[/bold]")
            processing_success = self._process_work_requests(file_path.name, room_skus, work_request_ids)

            if not processing_success:
                console.print("[red]❌ Work request processing failed[/red]")
                return False

            # Step 6: Completion summary
            console.print("\n[bold]Step 6: Workflow Complete[/bold]")
            console.print(f"[blue]✅ {len(work_request_ids)} work requests submitted for processing[/blue]")
            console.print("[yellow]Note: Status monitoring is disabled to avoid database lock conflicts[/yellow]")
            console.print("[dim]Use 'workrequest list' or 'workrequest get <id>' to check status later[/dim]")

            # Display work request IDs for reference
            console.print(f"\n[bold]Work Request IDs:[/bold]")
            for idx, wr_id in enumerate(work_request_ids, 1):
                console.print(f"  {idx}. {wr_id}")

            # Step 7: Archive file if requested
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
            console.print(f"[red]Traceback:[/red]")
            console.print(traceback.format_exc())
            return False

    def _run_dry_run_validation(self, file_path: Path, sheet_name: Optional[str]) -> Optional[Dict]:
        """Run dry-run import with JSON export and collect validation results"""
        try:
            console.print("[blue]Running dry-run validation and exporting JSON payloads...[/blue]")

            # Run dry-run with JSON export
            stats = self.importer.import_from_spreadsheet(
                file_path, sheet_name, dry_run=True
            )

            return {
                'stats': stats,
                'file_path': file_path,
                'sheet_name': sheet_name,
            }

        except Exception as e:
            console.print(f"[red]Dry run validation error: {e}[/red]")
            import traceback
            console.print(traceback.format_exc())
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
        table.add_row("Validation Errors", str(stats['validation_errors']), "❌ Invalid" if stats['validation_errors'] > 0 else "✅ All Valid")
        table.add_row("Failed Records", str(stats['failed']), "❌ Failed" if stats['failed'] > 0 else "✅ None")

        console.print(table)

        if stats['validation_errors'] > 0 or stats['failed'] > 0:
            console.print(f"\n[red]⚠️  {stats['validation_errors'] + stats['failed']} records have issues[/red]")

    def _get_user_confirmation(self, results: Dict) -> bool:
        """Get user confirmation to proceed with live import"""
        stats = results['stats']

        if stats['validation_errors'] > 0:
            console.print(f"\n[yellow]⚠️  Warning: {stats['validation_errors']} records will be skipped due to validation errors[/yellow]")

        valid_count = stats['created'] - stats['validation_errors']

        if valid_count == 0:
            console.print("[red]No valid records to import[/red]")
            return False

        console.print(f"\n[bold green]Ready to process {valid_count} valid room item swaps[/bold green]")
        return Confirm.ask("Proceed with live import?", default=False)

    def _run_live_import(self, file_path: Path, sheet_name: Optional[str]) -> Tuple[List[int], List[str]]:
        """Run live import and collect work request IDs"""
        work_request_ids = []
        room_skus = []

        try:
            stats = self.importer.import_from_spreadsheet(
                file_path, sheet_name, dry_run=False
            )

            console.print(f"[green]✅ Import completed: {stats['created']} swaps executed[/green]")

            work_request_ids = stats.get('work_request_ids', [])
            room_skus = stats.get('room_skus', [])

            if work_request_ids:
                console.print(f"[blue]📋 Collected {len(work_request_ids)} work request IDs[/blue]")

            # Log the import operation
            status = "Success" if stats['failed'] == 0 else "Partial"
            notes = f"Swaps: {stats['created']}, Failed: {stats['failed']}" if stats['failed'] > 0 else ""
            self.logger.log_import(
                source_file=file_path.name,
                skus=room_skus,
                workrequest_ids=work_request_ids,
                status=status,
                notes=notes
            )

            return work_request_ids, room_skus

        except Exception as e:
            console.print(f"[red]Live import error: {e}[/red]")
            import traceback
            console.print(traceback.format_exc())

            # Log the failed import
            self.logger.log_import(
                source_file=file_path.name,
                skus=room_skus,
                workrequest_ids=work_request_ids,
                status="Failed",
                notes=str(e)
            )
            return [], []

    def _process_work_requests(self, source_file: str, room_skus: List[str], work_request_ids: List[int]) -> bool:
        """Process each work request individually for better traceability"""
        if not work_request_ids:
            return True

        try:
            console.print(f"[blue]Processing {len(work_request_ids)} work requests individually for traceability...[/blue]")

            success_count = 0
            failed_count = 0

            # Process each work request individually
            with Progress() as progress:
                task = progress.add_task("[cyan]Processing work requests...", total=len(work_request_ids))

                for wr_id in work_request_ids:
                    try:
                        # Process single work request
                        result = self.client.process_workflows("room_item_swap", [wr_id])

                        if result:
                            success_count += 1
                            console.print(f"[green]✓[/green] Work request {wr_id} submitted for processing")
                        else:
                            failed_count += 1
                            console.print(f"[red]✗[/red] Work request {wr_id} failed to submit")

                    except Exception as e:
                        failed_count += 1
                        console.print(f"[red]✗[/red] Work request {wr_id} error: {e}")

                    progress.advance(task)

            console.print(f"\n[bold]Work Request Processing Summary:[/bold]")
            console.print(f"  Total: {len(work_request_ids)}")
            console.print(f"  Submitted: {success_count}")
            console.print(f"  Failed: {failed_count}")

            # Log the processing operation
            status = "Success" if failed_count == 0 else "Partial" if success_count > 0 else "Failed"
            notes = f"Submitted: {success_count}, Failed: {failed_count}" if failed_count > 0 else ""
            self.logger.log_processing(
                source_file=source_file,
                skus=room_skus,
                workrequest_ids=work_request_ids,
                status=status,
                notes=notes
            )

            return success_count > 0

        except Exception as e:
            console.print(f"[red]Error processing work requests: {e}[/red]")

            # Log the error
            self.logger.log_processing(
                source_file=source_file,
                skus=room_skus,
                workrequest_ids=work_request_ids,
                status="Failed",
                notes=str(e)
            )
            return False

    # NOTE: Status monitoring methods disabled to avoid database lock conflicts
    # while work requests are being processed. Users can check status manually
    # using 'workrequest list' or 'workrequest get <id>' commands.

    # def _get_final_status_summary(self, work_request_ids: List[int]) -> Dict:
    #     """Get final status summary for all work requests"""
    #     summary = {
    #         'total': len(work_request_ids),
    #         'pending': 0,
    #         'running': 0,
    #         'completed': 0,
    #         'failed': 0,
    #         'unknown': 0
    #     }
    #
    #     if not work_request_ids:
    #         return summary
    #
    #     try:
    #         # Query status for all work requests
    #         for wr_id in work_request_ids:
    #             try:
    #                 result = self.client.get_workrequest(wr_id)
    #                 if result:
    #                     status = result.get('status', 'UNKNOWN').upper()
    #                     if status == 'PENDING':
    #                         summary['pending'] += 1
    #                     elif status == 'RUNNING':
    #                         summary['running'] += 1
    #                     elif status == 'COMPLETED':
    #                         summary['completed'] += 1
    #                     elif status == 'FAILED':
    #                         summary['failed'] += 1
    #                     else:
    #                         summary['unknown'] += 1
    #                 else:
    #                     summary['unknown'] += 1
    #             except Exception:
    #                 summary['unknown'] += 1
    #
    #     except Exception as e:
    #         console.print(f"[yellow]Could not fetch final status: {e}[/yellow]")
    #
    #     return summary
    #
    # def _display_final_summary(self, status_summary: Dict) -> None:
    #     """Display final summary of work request statuses"""
    #     table = Table(title="📊 Final Status Summary")
    #     table.add_column("Status", style="cyan")
    #     table.add_column("Count", style="white", justify="right")
    #
    #     table.add_row("Total", str(status_summary['total']))
    #     table.add_row("Pending", str(status_summary['pending']))
    #     table.add_row("Running", str(status_summary['running']))
    #     table.add_row("Completed", str(status_summary['completed']))
    #     table.add_row("Failed", str(status_summary['failed']))
    #     table.add_row("Unknown", str(status_summary['unknown']))
    #
    #     console.print(table)

    def _handle_file_archiving(self, file_path: Path) -> bool:
        """Archive the processed file"""
        try:
            # Ask user if they want to archive
            if not Confirm.ask(f"\nArchive {file_path.name} to archive directory?", default=True):
                return True

            archive_dir = file_path.parent / 'archive'
            archive_dir.mkdir(parents=True, exist_ok=True)

            archive_path = archive_dir / file_path.name

            # If file already exists in archive, add timestamp
            if archive_path.exists():
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_path = archive_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"

            shutil.move(str(file_path), str(archive_path))
            console.print(f"[green]✅ File archived to: {archive_path}[/green]")
            return True

        except Exception as e:
            console.print(f"[red]Failed to archive file: {e}[/red]")
            return False


def main():
    """Main entry point for testing"""
    from pathlib import Path

    api_url = os.getenv("API_URL", "http://127.0.0.1:8000")
    oauth_token_url = os.getenv("OAUTH_TOKEN_URL", "http://127.0.0.1:8010/token")
    oauth_client_id = os.getenv("OAUTH_CLIENT_ID", "m2m-api-client")
    oauth_client_secret = os.getenv("OAUTH_CLIENT_SECRET")

    if not oauth_client_secret:
        console.print("[red]OAUTH_CLIENT_SECRET not set[/red]")
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

    workflow = RoomItemSwapWorkflow(client)

    # Example usage
    file_path = Path("data/room_item_swap/10-7-2025-FL-Active_Online_Rooms_with_CT_ET_Items_Inside.xlsx")

    if file_path.exists():
        success = workflow.run_end_to_end_workflow(file_path)
        if success:
            console.print("\n[green]✅ Workflow completed successfully![/green]")
        else:
            console.print("\n[red]❌ Workflow failed[/red]")


if __name__ == "__main__":
    main()
