"""Transparent click-through overlay window using PyQt6."""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QColor, QPainter, QFont, QPen
from PyQt6.QtWidgets import QWidget, QApplication, QMenu, QInputDialog
from PyQt6.QtCore import QPoint, pyqtSignal


class HUDWindow(QWidget):
    """Transparent overlay window with polished visuals."""

    note_requested = pyqtSignal(str)

    def __init__(self, x: int, y: int, width: int, height: int, opacity: float = 0.85):
        """
        Initialize HUD window.

        Args:
            x: Window x position.
            y: Window y position.
            width: Window width.
            height: Window height.
            opacity: Background opacity (0.0-1.0).
        """
        super().__init__()
        self._opacity = opacity
        self._setup_window(x, y, width, height)
        self._stats_to_display: list[tuple[int, int, str, str]] = []
        self._font_size = 10
        self._enable_input_temporarily()

    def _enable_input_temporarily(self):
        """Temporarily enable input for context menu."""
        flags = self.windowFlags()
        flags &= ~Qt.WindowType.WindowTransparentForInput
        self.setWindowFlags(flags)
        self.show()

    def _setup_window(self, x: int, y: int, width: int, height: int) -> None:
        """Configure window properties for transparent overlay."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
        self.setGeometry(x, y, width, height)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos: QPoint):
        """Show context menu for player notes."""
        for x, y, text, player_name in self._stats_to_display:
            rect = QRect(x - 6, y - 6, 120, 60)
            if rect.contains(pos):
                menu = QMenu(self)
                note_action = menu.addAction(f"Add Note for {player_name}")
                action = menu.exec(self.mapToGlobal(pos))
                if action == note_action:
                    self.note_requested.emit(player_name)
                break

    def set_opacity(self, opacity: float) -> None:
        """
        Set background opacity.

        Args:
            opacity: Opacity value (0.0-1.0).
        """
        self._opacity = max(0.0, min(1.0, opacity))
        self.update()

    def set_font_size(self, size: int) -> None:
        """
        Set font size.

        Args:
            size: Font size in points.
        """
        self._font_size = max(6, min(20, size))
        self.update()

    def set_stats_display(self, stats: list[tuple[int, int, str, str]]) -> None:
        """
        Set stats to display.

        Args:
            stats: List of (x, y, text, player_name) tuples for stat positions.
        """
        self._stats_to_display = stats
        self.update()

    def add_stat_display(self, x: int, y: int, text: str, player_name: str) -> None:
        """
        Add a stat display at position.

        Args:
            x: X position relative to window.
            y: Y position relative to window.
            text: Text to display.
            player_name: Player name for notes.
        """
        self._stats_to_display.append((x, y, text, player_name))
        self.update()

    def clear_stats(self) -> None:
        """Clear all displayed stats."""
        self._stats_to_display.clear()
        self.update()

    def paintEvent(self, event) -> None:
        """Paint stats on transparent overlay with visual polish."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        font = QFont("Segoe UI", self._font_size, QFont.Weight.Bold)
        painter.setFont(font)

        for x, y, text, player_name in self._stats_to_display:
            lines = text.split("\n")
            line_height = self._font_size + 4
            
            max_width = 0
            for line in lines:
                width = painter.fontMetrics().horizontalAdvance(line)
                max_width = max(max_width, width)
            
            box_height = len(lines) * line_height + 8
            padding = 6

            bg_rect = QRect(x - padding, y - padding, max_width + padding * 2, box_height)
            
            bg_color = QColor(20, 20, 30, int(self._opacity * 220))
            painter.fillRect(bg_rect, bg_color)
            
            border_pen = QPen(QColor(70, 70, 90, int(self._opacity * 255)), 1)
            painter.setPen(border_pen)
            painter.drawRect(bg_rect)

            text_color = QColor(240, 240, 255)
            painter.setPen(text_color)
            
            for i, line in enumerate(lines):
                y_pos = y + (self._font_size + 2) + (i * line_height)
                painter.drawText(x, y_pos, line)

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


def create_hud_window(x: int, y: int, width: int, height: int, opacity: float = 0.85) -> HUDWindow:
    """
    Create and show HUD window.

    Args:
        x: Window x position.
        y: Window y position.
        width: Window width.
        height: Window height.
        opacity: Background opacity.

    Returns:
        HUDWindow instance.
    """
    window = HUDWindow(x, y, width, height, opacity)
    window.show()
    return window
