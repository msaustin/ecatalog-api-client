#!/usr/bin/env python3

"""
SKU Substitution Importer

Reads SKU substitution requests from Excel/CSV files and processes them.
Expected columns:
- Collection Name (optional, for reference)
- Division (FL, SE, TX)
- Old Sku (replaced SKU)
- New Sku (substituted SKU)
- Package Skus (optional, comma-separated list of package SKUs to target)
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.progress import Progress

from ecatalog_client import ECatalogAPIClient, SkuSubstitutionRequest

console = Console()


class SkuSubstitutionImporter:
    """Import and process SKU substitution requests from spreadsheet files"""

    def __init__(self, api_client: ECatalogAPIClient):
        self.client = api_client
        self.console = console

    def import_from_spreadsheet(
        self,
        file_path: Path,
        sheet_name: Optional[str] = None,
        dry_run: bool = True,
        export_json: bool = False,
    ) -> Dict[str, int]:
        """
        Import SKU substitution requests from spreadsheet file.

        Args:
            file_path: Path to Excel/CSV file
            sheet_name: Sheet name for Excel files (default: first sheet)
            dry_run: If True, validate but don't submit. If False, submit to API.
            export_json: If True, export JSON payloads to json directory

        Returns:
            Dictionary with stats: processed, created, failed, work_request_ids, substitution_keys
        """
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

            console.print(f"[bold]Read {len(df)} rows from {file_path.name}[/bold]")

            # Validate required columns
            required_columns = ["Division", "Old Sku", "New Sku"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                console.print(f"[red]Missing required columns: {', '.join(missing_columns)}[/red]")
                console.print(f"[yellow]Available columns: {', '.join(df.columns)}[/yellow]")
                return {"processed": 0, "created": 0, "failed": 0}

            # Get site from filename or use default
            site = self._extract_site_from_filename(file_path.name)

            # Group by division and build substitution requests
            grouped_requests = self._group_substitutions(df, site)

            console.print(f"[blue]Grouped into {len(grouped_requests)} substitution request(s)[/blue]")

            stats = {
                "processed": 0,
                "created": 0,
                "failed": 0,
                "work_request_ids": [],
                "substitution_keys": []
            }

            # Process each grouped substitution request
            with Progress() as progress:
                task = progress.add_task(
                    f"[cyan]{'Validating' if dry_run else 'Submitting'} substitution requests...",
                    total=len(grouped_requests)
                )

                for idx, (key, sub_request) in enumerate(grouped_requests.items()):
                    stats["processed"] += 1
                    stats["substitution_keys"].append(key)

                    if export_json:
                        self._export_json(sub_request, key, file_path)

                    if dry_run:
                        # Dry run: prevalidate
                        console.print(f"\n[yellow]Prevalidating:[/yellow] {key}")
                        result = self._prevalidate_substitution(sub_request)
                        if result and result.get("valid"):
                            stats["created"] += 1
                            console.print(f"[green]✅ Valid substitution[/green]")
                        else:
                            stats["failed"] += 1
                            console.print(f"[red]❌ Invalid substitution[/red]")
                    else:
                        # Live run: submit
                        console.print(f"\n[yellow]Submitting:[/yellow] {key}")
                        result = self._submit_substitution(sub_request)
                        if result:
                            work_request_id = result.get("workrequest_id") or result.get("work_request_id")
                            if work_request_id:
                                stats["work_request_ids"].append(work_request_id)
                                console.print(f"[green]✅ Work Request: {work_request_id}[/green]")
                            stats["created"] += 1
                        else:
                            stats["failed"] += 1
                            console.print(f"[red]❌ Submission failed[/red]")

                    progress.update(task, advance=1)

            return stats

        except Exception as e:
            console.print(f"[red]Error reading spreadsheet: {e}[/red]")
            import traceback
            console.print(traceback.format_exc())
            return {"processed": 0, "created": 0, "failed": 0}

    def _extract_site_from_filename(self, filename: str) -> str:
        """Extract site from filename (e.g., MERCH_SUBSKU_HLVN -> assume RTG)"""
        # Default to RTG - you can add logic to detect site from filename
        return "RTG"

    def _group_substitutions(self, df: pd.DataFrame, site: str) -> Dict[str, SkuSubstitutionRequest]:
        """
        Group substitution rows into SkuSubstitutionRequest objects.
        Groups by division and creates one request per division.
        """
        grouped_requests = {}

        for division in df["Division"].unique():
            division_df = df[df["Division"] == division]

            # Collect all old and new SKUs for this division
            replaced_skus = division_df["Old Sku"].dropna().astype(str).tolist()
            substituted_skus = division_df["New Sku"].dropna().astype(str).tolist()

            # Collect package SKUs if present
            package_skus = None
            if "Package Skus" in division_df.columns:
                # Flatten all package SKUs (they're comma-separated in cells)
                all_packages = []
                for packages in division_df["Package Skus"].dropna():
                    if isinstance(packages, str):
                        all_packages.extend([p.strip() for p in packages.split(",") if p.strip()])
                # Remove duplicates
                package_skus = list(set(all_packages)) if all_packages else None

            # Create request using field aliases
            request_data = {
                "Site": site,
                "Replaced Skus": replaced_skus,
                "Substituted Skus": substituted_skus,
                "Divisions": [division],
            }

            if package_skus:
                request_data["Package Skus"] = package_skus

            try:
                sub_request = SkuSubstitutionRequest.model_validate(request_data)
                key = f"{site}_{division}_{len(replaced_skus)}skus"
                grouped_requests[key] = sub_request

                console.print(f"[blue]Created request for {division}:[/blue] {len(replaced_skus)} SKU pairs")
                if package_skus:
                    console.print(f"  [dim]Targeting {len(package_skus)} package SKUs[/dim]")

            except Exception as e:
                console.print(f"[red]Error creating request for {division}: {e}[/red]")

        return grouped_requests

    def _prevalidate_substitution(self, sub_request: SkuSubstitutionRequest) -> Optional[Dict]:
        """Prevalidate a substitution request"""
        try:
            result = self.client.prevalidate_sku_substitution(sub_request)

            if result:
                # Display validation errors/warnings
                if result.get("errors"):
                    console.print("[red]Errors:[/red]")
                    for error in result["errors"]:
                        console.print(f"  • {error}")

                if result.get("warnings"):
                    console.print("[yellow]Warnings:[/yellow]")
                    for warning in result["warnings"]:
                        console.print(f"  • {warning}")

            return result
        except Exception as e:
            console.print(f"[red]Prevalidation error: {e}[/red]")
            return None

    def _submit_substitution(self, sub_request: SkuSubstitutionRequest) -> Optional[Dict]:
        """Submit a substitution request for processing"""
        try:
            result = self.client.submit_sku_substitution(sub_request)
            return result
        except Exception as e:
            console.print(f"[red]Submission error: {e}[/red]")
            return None

    def _export_json(self, sub_request: SkuSubstitutionRequest, key: str, source_file: Path):
        """Export substitution request to JSON file"""
        try:
            project_root = Path(__file__).parent.parent
            json_dir = project_root / "data" / "sku_substitution" / "json"
            json_dir.mkdir(parents=True, exist_ok=True)

            # Use key as filename
            json_path = json_dir / f"{key}.json"

            # Convert to dict using by_alias to match API format
            payload = sub_request.model_dump(by_alias=True, exclude_none=True)

            with open(json_path, "w") as f:
                json.dump(payload, f, indent=2)

            console.print(f"[dim]Exported JSON: {json_path.name}[/dim]")

        except Exception as e:
            console.print(f"[yellow]Warning: Failed to export JSON: {e}[/yellow]")
