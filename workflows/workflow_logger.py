"""
Workflow Logger for tracking batch operations and work requests.

This module provides functionality to log workflow operations to Excel files,
including timestamps, filenames, SKUs processed, and work request IDs.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import logging


class WorkflowLogger:
    """Logger for workflow batch operations"""

    def __init__(self, workflow_name: str, logs_dir: Path):
        """
        Initialize workflow logger.

        Args:
            workflow_name: Name of the workflow (e.g., 'dropship', 'rtg_delivered')
            logs_dir: Directory where log files should be stored
        """
        self.workflow_name = workflow_name
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Set up Python logging
        self.logger = logging.getLogger(f"workflow_logger.{workflow_name}")

    def _get_log_file_path(self) -> Path:
        """Get the log file path for today's date"""
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"{today}-{self.workflow_name}.xlsx"
        return self.logs_dir / filename

    def _initialize_log_file(self, log_path: Path) -> pd.DataFrame:
        """
        Initialize or load existing log file.

        Args:
            log_path: Path to the log file

        Returns:
            DataFrame with log data
        """
        if log_path.exists():
            # Load existing log
            try:
                df = pd.read_excel(log_path)
                self.logger.info(f"Loaded existing log file: {log_path}")
                return df
            except Exception as e:
                self.logger.warning(f"Could not load existing log file: {e}. Creating new one.")

        # Create new DataFrame with columns
        df = pd.DataFrame(columns=[
            'Timestamp',
            'Action',
            'Source File',
            'SKUs',
            'SKU Count',
            'Work Request IDs',
            'Work Request Count',
            'Status',
            'Notes'
        ])
        self.logger.info(f"Initialized new log file: {log_path}")
        return df

    def log_batch_operation(
        self,
        action: str,
        source_file: str,
        skus: List[str],
        workrequest_ids: Optional[List[int]] = None,
        status: str = "Success",
        notes: str = ""
    ) -> None:
        """
        Log a batch operation to the Excel file.

        Args:
            action: Description of the action (e.g., 'Import', 'Submit', 'Process')
            source_file: Name of the source file being processed
            skus: List of SKUs processed
            workrequest_ids: List of work request IDs created/processed
            status: Status of the operation (e.g., 'Success', 'Partial', 'Failed')
            notes: Additional notes or error messages
        """
        try:
            log_path = self._get_log_file_path()
            df = self._initialize_log_file(log_path)

            # Prepare the new row
            new_row = {
                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Action': action,
                'Source File': source_file,
                'SKUs': ', '.join(skus) if skus else '',
                'SKU Count': len(skus) if skus else 0,
                'Work Request IDs': ', '.join(map(str, workrequest_ids)) if workrequest_ids else '',
                'Work Request Count': len(workrequest_ids) if workrequest_ids else 0,
                'Status': status,
                'Notes': notes
            }

            # Append the new row
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # Save to Excel
            df.to_excel(log_path, index=False, engine='openpyxl')

            self.logger.info(
                f"Logged {action} operation: {len(skus) if skus else 0} SKUs, "
                f"{len(workrequest_ids) if workrequest_ids else 0} work requests"
            )

        except Exception as e:
            self.logger.error(f"Failed to log batch operation: {e}")
            # Don't raise - logging failures shouldn't stop workflow

    def log_import(
        self,
        source_file: str,
        skus: List[str],
        workrequest_ids: Optional[List[int]] = None,
        status: str = "Success",
        notes: str = ""
    ) -> None:
        """
        Log an import operation.

        Args:
            source_file: Name of the file being imported
            skus: List of SKUs imported
            workrequest_ids: List of work request IDs created
            status: Status of the operation
            notes: Additional notes
        """
        self.log_batch_operation(
            action="Import",
            source_file=source_file,
            skus=skus,
            workrequest_ids=workrequest_ids,
            status=status,
            notes=notes
        )

    def log_submission(
        self,
        source_file: str,
        skus: List[str],
        workrequest_ids: List[int],
        status: str = "Success",
        notes: str = ""
    ) -> None:
        """
        Log a work request submission operation.

        Args:
            source_file: Name of the source file
            skus: List of SKUs in the work requests
            workrequest_ids: List of work request IDs submitted for processing
            status: Status of the operation
            notes: Additional notes
        """
        self.log_batch_operation(
            action="Submit",
            source_file=source_file,
            skus=skus,
            workrequest_ids=workrequest_ids,
            status=status,
            notes=notes
        )

    def log_processing(
        self,
        source_file: str,
        skus: List[str],
        workrequest_ids: List[int],
        status: str = "Success",
        notes: str = ""
    ) -> None:
        """
        Log a work request processing operation.

        Args:
            source_file: Name of the source file
            skus: List of SKUs being processed
            workrequest_ids: List of work request IDs being processed
            status: Status of the operation
            notes: Additional notes
        """
        self.log_batch_operation(
            action="Process",
            source_file=source_file,
            skus=skus,
            workrequest_ids=workrequest_ids,
            status=status,
            notes=notes
        )

    def get_log_summary(self) -> Optional[pd.DataFrame]:
        """
        Get a summary of today's log entries.

        Returns:
            DataFrame with log summary or None if no log exists
        """
        log_path = self._get_log_file_path()
        if not log_path.exists():
            return None

        try:
            df = pd.read_excel(log_path)
            return df
        except Exception as e:
            self.logger.error(f"Failed to read log summary: {e}")
            return None
