"""Transparent click-through overlay window using PyQt6."""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QColor, QPainter, QFont
from PyQt6.QtWidgets import QWidget, QApplication


class HUDWindow(QWidget):
    """Transparent overlay window that clicks pass through."""

    def __init__(self, x: int, y: int, width: int, height: int):
        """
        Initialize HUD window.

        Args:
            x: Window x position.
            y: Window y position.
            width: Window width.
            height: Window height.
        """
        super().__init__()
        self._setup_window(x, y, width, height)
        self._stats_to_display: list[tuple[int, int, str]] = []

    def _setup_window(self, x: int, y: int, width: int, height: int) -> None:
        """Configure window properties for transparent overlay."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
        )
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
        self.setGeometry(x, y, width, height)

    def set_stats_display(self, stats: list[tuple[int, int, str]]) -> None:
        """
        Set stats to display.

        Args:
            stats: List of (x, y, text) tuples for stat positions.
        """
        self._stats_to_display = stats
        self.update()

    def add_stat_display(self, x: int, y: int, text: str) -> None:
        """
        Add a stat display at position.

        Args:
            x: X position relative to window.
            y: Y position relative to window.
            text: Text to display.
        """
        self._stats_to_display.append((x, y, text))
        self.update()

    def clear_stats(self) -> None:
        """Clear all displayed stats."""
        self._stats_to_display.clear()
        self.update()

    def paintEvent(self, event) -> None:
        """Paint stats on transparent overlay."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        font = QFont("Arial", 9, QFont.Weight.Bold)
        painter.setFont(font)

        for x, y, text in self._stats_to_display:
            lines = text.split("\n")
            line_height = 14
            max_width = max(painter.fontMetrics().horizontalAdvance(line) for line in lines)
            box_height = len(lines) * line_height + 6

            bg_rect = QRect(x - 2, y - 2, max_width + 8, box_height)
            painter.fillRect(bg_rect, QColor(0, 0, 0, 180))

            painter.setPen(QColor(255, 255, 255))
            for i, line in enumerate(lines):
                painter.drawText(x + 2, y + 12 + (i * line_height), line)

    def update_position(self, x: int, y: int, width: int, height: int) -> None:
        """
        Update window position and size.

        Args:
            x: New x position.
            y: New y position.
            width: New width.
            height: New height.
        """
        self.setGeometry(x, y, width, height)


def create_hud_window(x: int, y: int, width: int, height: int) -> HUDWindow:
    """
    Create and show HUD window.

    Args:
        x: Window x position.
        y: Window y position.
        width: Window width.
        height: Window height.

    Returns:
        HUDWindow instance.
    """
    window = HUDWindow(x, y, width, height)
    window.show()
    return window
