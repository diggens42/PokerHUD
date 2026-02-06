"""Detect and track PokerStars table windows."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

import win32gui
import win32con


@dataclass
class TableWindow:
    """Information about a detected poker table window."""

    hwnd: int
    title: str
    x: int
    y: int
    width: int
    height: int

    @property
    def region(self) -> tuple[int, int, int, int]:
        """Get region tuple for screen capture."""
        return (self.x, self.y, self.width, self.height)


class TableDetector:
    """Detects PokerStars table windows by title matching."""

    POKERSTARS_PATTERNS = [
        r"Hold'em",
        r"Omaha",
        r"Tournament",
        r"Zoom",
        r"NL Hold'em",
        r"PL Omaha",
        r"FL Hold'em",
    ]

    def __init__(self):
        """Initialize the table detector."""
        self._compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.POKERSTARS_PATTERNS
        ]

    def find_tables(self) -> list[TableWindow]:
        """
        Find all PokerStars table windows currently open.

        Returns:
            List of TableWindow objects for detected tables.
        """
        tables = []

        def enum_callback(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return

            title = win32gui.GetWindowText(hwnd)
            if not title:
                return

            if self._is_pokerstars_table(title):
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                    x, y, right, bottom = rect
                    width = right - x
                    height = bottom - y

                    if width > 100 and height > 100:
                        tables.append(
                            TableWindow(
                                hwnd=hwnd,
                                title=title,
                                x=x,
                                y=y,
                                width=width,
                                height=height,
                            )
                        )
                except Exception:
                    pass

        win32gui.EnumWindows(enum_callback, None)
        return tables

    def find_table_by_hwnd(self, hwnd: int) -> Optional[TableWindow]:
        """
        Get table information for a specific window handle.

        Args:
            hwnd: Window handle.

        Returns:
            TableWindow if valid, None otherwise.
        """
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return None

            title = win32gui.GetWindowText(hwnd)
            if not self._is_pokerstars_table(title):
                return None

            rect = win32gui.GetWindowRect(hwnd)
            x, y, right, bottom = rect
            width = right - x
            height = bottom - y

            return TableWindow(
                hwnd=hwnd, title=title, x=x, y=y, width=width, height=height
            )
        except Exception:
            return None

    def _is_pokerstars_table(self, title: str) -> bool:
        """
        Check if window title matches PokerStars table patterns.

        Args:
            title: Window title string.

        Returns:
            True if title matches any known pattern.
        """
        if not title:
            return False

        for pattern in self._compiled_patterns:
            if pattern.search(title):
                return True

        return False

    def is_table_active(self, hwnd: int) -> bool:
        """
        Check if a table window still exists and is visible.

        Args:
            hwnd: Window handle.

        Returns:
            True if window is valid and visible.
        """
        try:
            return win32gui.IsWindowVisible(hwnd) and win32gui.IsWindow(hwnd)
        except Exception:
            return False

    def get_window_position(self, hwnd: int) -> Optional[tuple[int, int, int, int]]:
        """
        Get current position and size of a window.

        Args:
            hwnd: Window handle.

        Returns:
            Tuple of (x, y, width, height) or None if window is invalid.
        """
        try:
            rect = win32gui.GetWindowRect(hwnd)
            x, y, right, bottom = rect
            return (x, y, right - x, bottom - y)
        except Exception:
            return None
