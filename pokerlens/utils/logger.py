"""Structured logging utility."""
from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import config


class Logger:
    """Structured logger with file and console output."""

    def __init__(
        self,
        name: str = config.APP_NAME,
        level: int = logging.INFO,
        log_to_file: bool = True,
    ):
        """
        Initialize logger.

        Args:
            name: Logger name.
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            log_to_file: Whether to write logs to file.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers.clear()

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if log_to_file:
            config.LOG_DIR.mkdir(parents=True, exist_ok=True)
            log_filename = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
            log_path = config.LOG_DIR / log_filename

            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(self._format_message(message, kwargs))

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(self._format_message(message, kwargs))

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(self._format_message(message, kwargs))

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(self._format_message(message, kwargs))

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(self._format_message(message, kwargs))

    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        self.logger.exception(self._format_message(message, kwargs))

    def _format_message(self, message: str, context: dict) -> str:
        """Format message with context."""
        if not context:
            return message

        context_str = " | ".join(f"{k}={v}" for k, v in context.items())
        return f"{message} | {context_str}"


_default_logger: Optional[Logger] = None


def get_logger(name: Optional[str] = None) -> Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name. If None, returns default logger.

    Returns:
        Logger instance.
    """
    global _default_logger

    if name is None:
        if _default_logger is None:
            _default_logger = Logger()
        return _default_logger

    return Logger(name=name)
