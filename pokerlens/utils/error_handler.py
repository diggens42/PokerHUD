"""Centralized error handling and recovery strategies."""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Optional, Callable
from functools import wraps

from pokerlens.utils.logger import Logger


class ErrorHandler:
    """Handles errors with recovery strategies and user-friendly messages."""

    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialize error handler.

        Args:
            logger: Logger instance.
        """
        self.logger = logger or Logger("error_handler")
        self._error_counts: dict[str, int] = {}
        self._max_retries = 3

    def check_tesseract(self, tesseract_path: str) -> tuple[bool, str]:
        """
        Check if Tesseract is available.

        Args:
            tesseract_path: Path to Tesseract executable.

        Returns:
            Tuple of (is_available, error_message).
        """
        if not tesseract_path:
            return False, "Tesseract path not configured. Please set it in Settings."

        tesseract_exe = Path(tesseract_path)
        if not tesseract_exe.exists():
            return False, (
                f"Tesseract not found at: {tesseract_path}\n\n"
                "Please install Tesseract OCR:\n"
                "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "2. Install to default location\n"
                "3. Update path in Settings"
            )

        if not os.access(tesseract_exe, os.X_OK):
            return False, f"Tesseract found but not executable: {tesseract_path}"

        return True, ""

    def check_database(self, db_path: Path) -> tuple[bool, str]:
        """
        Check database integrity.

        Args:
            db_path: Path to database file.

        Returns:
            Tuple of (is_valid, error_message).
        """
        import sqlite3

        if not db_path.exists():
            return True, ""

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            conn.close()

            if result[0] != "ok":
                backup_path = db_path.with_suffix(".db.backup")
                shutil.copy2(db_path, backup_path)
                
                return False, (
                    f"Database corrupted. Backup saved to:\n{backup_path}\n\n"
                    "The database will be recreated. Previous data may be lost."
                )

            return True, ""

        except sqlite3.Error as e:
            return False, f"Database error: {str(e)}\n\nThe database will be recreated."

    def handle_ocr_failure(self, table_id: str, error: Exception) -> None:
        """
        Handle OCR failure with retry logic.

        Args:
            table_id: Table identifier.
            error: Exception that occurred.
        """
        key = f"ocr_{table_id}"
        self._error_counts[key] = self._error_counts.get(key, 0) + 1

        if self._error_counts[key] >= self._max_retries:
            self.logger.warning(
                "OCR failures exceeded max retries",
                table=table_id,
                count=self._error_counts[key]
            )
            del self._error_counts[key]
        else:
            self.logger.debug(
                "OCR failure, will retry",
                table=table_id,
                attempt=self._error_counts[key],
                error=str(error)
            )

    def handle_capture_failure(self, table_id: str, error: Exception) -> None:
        """
        Handle screen capture failure.

        Args:
            table_id: Table identifier.
            error: Exception that occurred.
        """
        self.logger.error("Screen capture failed", table=table_id, error=str(error))

    def reset_error_count(self, table_id: str, error_type: str) -> None:
        """
        Reset error count after successful operation.

        Args:
            table_id: Table identifier.
            error_type: Type of error (e.g., "ocr", "capture").
        """
        key = f"{error_type}_{table_id}"
        if key in self._error_counts:
            del self._error_counts[key]


def safe_operation(error_handler: ErrorHandler, operation_name: str):
    """
    Decorator for safe operations with error handling.

    Args:
        error_handler: ErrorHandler instance.
        operation_name: Name of operation for logging.

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_handler.logger.error(
                    f"Operation failed: {operation_name}",
                    error=str(e),
                    error_type=type(e).__name__
                )
                return None
        return wrapper
    return decorator
