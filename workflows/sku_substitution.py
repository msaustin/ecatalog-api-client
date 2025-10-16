#!/usr/bin/env python3

"""
Interactive SKU Substitution Workflow

This script provides a guided, interactive interface for SKU substitution prevalidation.
Instead of complex CLI flags, it walks the user through each step.
"""

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.json import JSON
from typing import List, Optional
import json

from ecatalog_client import ECatalogAPIClient, SkuSubstitutionRequest

console = Console()


class SkuSubstitutionWorkflow:
    """Interactive workflow for SKU substitution prevalidation"""

    def __init__(self, client: ECatalogAPIClient):
        self.client = client

    def run_interactive_prevalidation(self) -> bool:
        """Run the interactive SKU substitution prevalidation workflow"""
        console.print("[bold blue]🔄 SKU Substitution Prevalidation Workflow[/bold blue]")
        console.print("This workflow will guide you through validating a SKU substitution request.\n")

        try:
            # Step 1: Get site
            site = self._get_site()

            # Step 2: Get replaced SKUs
            replaced_skus = self._get_replaced_skus()

            # Step 3: Get substituted SKUs
            substituted_skus = self._get_substituted_skus()

            # Step 4: Get divisions
            divisions = self._get_divisions()

            # Step 5: Get package SKUs (optional)
            package_skus = self._get_package_skus()

            # Step 6: Review and confirm
            if not self._review_substitution_request(site, replaced_skus, substituted_skus, divisions, package_skus):
                console.print("[yellow]Substitution request cancelled.[/yellow]")
                return False

            # Step 7: Execute prevalidation
            return self._execute_prevalidation(site, replaced_skus, substituted_skus, divisions, package_skus)

        except KeyboardInterrupt:
            console.print("\n[yellow]Workflow cancelled by user.[/yellow]")
            return False
        except Exception as e:
            console.print(f"[red]Error in workflow: {e}[/red]")
            return False

    def _get_site(self) -> str:
        """Get the site for the substitution"""
        console.print("[bold]Step 1: Site Information[/bold]")

        common_sites = ["RTG", "OTG", "WG", "ATG"]
        console.print(f"Common sites: {', '.join(common_sites)}")

        while True:
            site = Prompt.ask("Enter site", default="RTG").strip().upper()
            if site:
                return site
            console.print("[red]Site cannot be empty. Please enter a valid site.[/red]")

    def _get_replaced_skus(self) -> List[str]:
        """Get the SKUs being replaced"""
        console.print("\n[bold]Step 2: SKUs Being Replaced[/bold]")
        console.print("Enter the SKUs that will be replaced.")
        console.print("[blue]You can enter multiple SKUs separated by commas (e.g., SKU1, SKU2, SKU3)[/blue]")

        while True:
            sku_input = Prompt.ask("Replaced SKUs", default="").strip()
            if not sku_input:
                console.print("[red]At least one replaced SKU is required.[/red]")
                continue

            # Parse comma-separated SKUs
            skus = [sku.strip() for sku in sku_input.split(',') if sku.strip()]

            if not skus:
                console.print("[red]At least one replaced SKU is required.[/red]")
                continue

            # Remove duplicates while preserving order
            unique_skus = []
            for sku in skus:
                if sku not in unique_skus:
                    unique_skus.append(sku)

            console.print(f"[green]Added {len(unique_skus)} replaced SKU(s): {', '.join(unique_skus)}[/green]")
            return unique_skus

    def _get_substituted_skus(self) -> List[str]:
        """Get the SKUs to substitute with"""
        console.print("\n[bold]Step 3: Substituted SKUs[/bold]")
        console.print("Enter the SKUs that will replace the old ones.")
        console.print("[blue]You can enter multiple SKUs separated by commas (e.g., SKU1, SKU2, SKU3)[/blue]")

        while True:
            sku_input = Prompt.ask("Substituted SKUs", default="").strip()
            if not sku_input:
                console.print("[red]At least one substituted SKU is required.[/red]")
                continue

            # Parse comma-separated SKUs
            skus = [sku.strip() for sku in sku_input.split(',') if sku.strip()]

            if not skus:
                console.print("[red]At least one substituted SKU is required.[/red]")
                continue

            # Remove duplicates while preserving order
            unique_skus = []
            for sku in skus:
                if sku not in unique_skus:
                    unique_skus.append(sku)

            console.print(f"[green]Added {len(unique_skus)} substituted SKU(s): {', '.join(unique_skus)}[/green]")
            return unique_skus

    def _get_divisions(self) -> List[str]:
        """Get the divisions for the substitution"""
        console.print("\n[bold]Step 4: Divisions[/bold]")
        console.print("Select the divisions where this substitution should apply:")

        available_divisions = ["FL", "SE", "TX"]
        divisions = []

        for division in available_divisions:
            if Confirm.ask(f"Apply to {division} division?", default=True):
                divisions.append(division)

        if not divisions:
            console.print("[red]At least one division must be selected.[/red]")
            return self._get_divisions()

        console.print(f"[green]Selected divisions: {', '.join(divisions)}[/green]")
        return divisions

    def _get_package_skus(self) -> Optional[List[str]]:
        """Get package SKUs (optional)"""
        console.print("\n[bold]Step 5: Package SKUs (Optional)[/bold]")

        if not Confirm.ask("Do you want to target specific package SKUs?", default=False):
            return None

        console.print("Enter package SKUs to target:")
        console.print("[blue]You can enter multiple SKUs separated by commas (e.g., SKU1, SKU2, SKU3)[/blue]")

        while True:
            sku_input = Prompt.ask("Package SKUs", default="").strip()
            if not sku_input:
                return None

            # Parse comma-separated SKUs
            skus = [sku.strip() for sku in sku_input.split(',') if sku.strip()]

            if not skus:
                return None

            # Remove duplicates while preserving order
            unique_skus = []
            for sku in skus:
                if sku not in unique_skus:
                    unique_skus.append(sku)

            console.print(f"[green]Added {len(unique_skus)} package SKU(s): {', '.join(unique_skus)}[/green]")
            return unique_skus

    def _review_substitution_request(self, site: str, replaced_skus: List[str],
                                   substituted_skus: List[str], divisions: List[str],
                                   package_skus: Optional[List[str]]) -> bool:
        """Review the substitution request before execution"""
        console.print("\n[bold]Step 6: Review Substitution Request[/bold]")

        # Create a summary table
        table = Table()
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Site", site)
        table.add_row("Replaced SKUs", ", ".join(replaced_skus))
        table.add_row("Substituted SKUs", ", ".join(substituted_skus))
        table.add_row("Divisions", ", ".join(divisions))
        table.add_row("Package SKUs", ", ".join(package_skus) if package_skus else "None")

        console.print(table)

        return Confirm.ask("\nProceed with prevalidation?", default=True)

    def _execute_prevalidation(self, site: str, replaced_skus: List[str],
                             substituted_skus: List[str], divisions: List[str],
                             package_skus: Optional[List[str]]) -> bool:
        """Execute the prevalidation request"""
        console.print("\n[bold]Step 7: Executing Prevalidation[/bold]")

        try:
            # Create request using field aliases (the way the API expects them)
            request_data = {
                "Site": site,
                "Replaced Skus": replaced_skus,
                "Substituted Skus": substituted_skus,
                "Divisions": divisions,
            }

            if package_skus:
                request_data["Package Skus"] = package_skus

            substitution_req = SkuSubstitutionRequest.model_validate(request_data)

            console.print("[yellow]Sending prevalidation request to API...[/yellow]")
            result = self.client.prevalidate_sku_substitution(substitution_req)

            if result:
                self._display_prevalidation_results(result)
                is_valid = result.get('valid', False)

                # If valid, offer to submit the substitution
                if is_valid:
                    if self._confirm_submission():
                        return self._submit_substitution(substitution_req)

                return is_valid
            else:
                console.print("[red]Prevalidation request failed - no response from API[/red]")
                return False

        except Exception as e:
            console.print(f"[red]Error during prevalidation: {e}[/red]")
            return False

    def _display_prevalidation_results(self, result: dict):
        """Display the prevalidation results in a formatted way"""
        console.print("\n[bold]📋 Prevalidation Results[/bold]")

        # Main result
        is_valid = result.get('valid', False)
        status_color = "green" if is_valid else "red"
        status_text = "✅ VALID" if is_valid else "❌ INVALID"

        console.print(f"Status: [{status_color}]{status_text}[/{status_color}]")

        # Validation details
        if result.get("validation_results"):
            console.print(f"\n[bold]Validation Details:[/bold]")
            console.print(JSON(json.dumps(result["validation_results"], indent=2)))

        # Errors
        if result.get("errors"):
            console.print(f"\n[red]❌ Errors:[/red]")
            for error in result["errors"]:
                console.print(f"  • {error}")

        # Warnings
        if result.get("warnings"):
            console.print(f"\n[yellow]⚠️  Warnings:[/yellow]")
            for warning in result["warnings"]:
                console.print(f"  • {warning}")

        # Summary
        if is_valid:
            console.print(f"\n[green]✅ Substitution request is valid and ready to proceed![/green]")
        else:
            console.print(f"\n[red]❌ Substitution request has validation issues that must be resolved.[/red]")

    def _confirm_submission(self) -> bool:
        """Confirm if user wants to submit the substitution for execution"""
        console.print("\n[bold yellow]🚀 Ready to Submit Substitution[/bold yellow]")
        console.print("The prevalidation was successful. You can now submit this substitution for actual execution.")
        console.print("[yellow]⚠️  Warning: This will make real changes to the system![/yellow]")

        return Confirm.ask("Submit the SKU substitution for execution?", default=False)

    def _submit_substitution(self, substitution_req: SkuSubstitutionRequest) -> bool:
        """Submit the substitution for execution"""
        console.print("\n[bold]Step 8: Submitting Substitution for Execution[/bold]")

        try:
            console.print("[yellow]Submitting substitution request to API...[/yellow]")
            result = self.client.submit_sku_substitution(substitution_req)

            if result:
                self._display_submission_results(result)
                return True
            else:
                console.print("[red]Substitution submission failed - no response from API[/red]")
                return False

        except Exception as e:
            console.print(f"[red]Error during substitution submission: {e}[/red]")
            return False

    def _display_submission_results(self, result: dict):
        """Display the substitution submission results"""
        console.print("\n[bold]📋 Substitution Submission Results[/bold]")

        # Check for common response fields
        if result.get("success"):
            console.print(f"[green]✅ Substitution submitted successfully![/green]")

        if result.get("message"):
            console.print(f"Message: {result['message']}")

        if result.get("work_request_id") or result.get("workrequest_id"):
            work_id = result.get("work_request_id") or result.get("workrequest_id")
            console.print(f"Work Request ID: [bold]{work_id}[/bold]")

        if result.get("status"):
            console.print(f"Status: {result['status']}")

        # Display full result if it contains other useful info
        if len(result) > 3:  # More than just basic fields
            console.print(f"\n[bold]Full Response:[/bold]")
            console.print(JSON(json.dumps(result, indent=2)))

        console.print(f"\n[green]🎉 SKU substitution has been submitted for processing![/green]")