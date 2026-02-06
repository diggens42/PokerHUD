"""System tray integration for PokerHUD."""
from __future__ import annotations

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal


class SystemTray(QObject):
    """System tray icon with menu controls."""

    start_tracking = pyqtSignal()
    stop_tracking = pyqtSignal()
    open_settings = pyqtSignal()
    quit_app = pyqtSignal()

    def __init__(self, parent=None):
        """
        Initialize system tray.

        Args:
            parent: Parent QObject.
        """
        super().__init__(parent)
        self._tray_icon = None
        self._menu = None
        self._is_tracking = False
        self._setup_tray()

    def _setup_tray(self):
        """Setup system tray icon and menu."""
        self._tray_icon = QSystemTrayIcon(self)
        self._tray_icon.setToolTip("PokerHUD - Not Tracking")
        
        self._menu = QMenu()
        
        self._start_action = QAction("Start Tracking", self)
        self._start_action.triggered.connect(self._on_start)
        self._menu.addAction(self._start_action)
        
        self._stop_action = QAction("Stop Tracking", self)
        self._stop_action.triggered.connect(self._on_stop)
        self._stop_action.setEnabled(False)
        self._menu.addAction(self._stop_action)
        
        self._menu.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings.emit)
        self._menu.addAction(settings_action)
        
        self._menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app.emit)
        self._menu.addAction(quit_action)
        
        self._tray_icon.setContextMenu(self._menu)
        
        self._tray_icon.activated.connect(self._on_tray_activated)

    def _on_start(self):
        """Handle start tracking."""
        self._is_tracking = True
        self._start_action.setEnabled(False)
        self._stop_action.setEnabled(True)
        self._tray_icon.setToolTip("PokerHUD - Tracking Active")
        self.start_tracking.emit()

    def _on_stop(self):
        """Handle stop tracking."""
        self._is_tracking = False
        self._start_action.setEnabled(True)
        self._stop_action.setEnabled(False)
        self._tray_icon.setToolTip("PokerHUD - Not Tracking")
        self.stop_tracking.emit()

    def _on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self._is_tracking:
                self._on_stop()
            else:
                self._on_start()

    def show(self):
        """Show system tray icon."""
        if self._tray_icon:
            self._tray_icon.show()

    def hide(self):
        """Hide system tray icon."""
        if self._tray_icon:
            self._tray_icon.hide()

    def show_message(self, title: str, message: str, duration: int = 3000):
        """
        Show notification message.

        Args:
            title: Notification title.
            message: Notification message.
            duration: Display duration in milliseconds.
        """
        if self._tray_icon:
            self._tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Information,
                duration
            )

    def update_table_count(self, count: int):
        """
        Update tooltip with table count.

        Args:
            count: Number of tracked tables.
        """
        if self._is_tracking:
            status = f"PokerHUD - Tracking {count} table{'s' if count != 1 else ''}"
        else:
            status = "PokerHUD - Not Tracking"
        
        if self._tray_icon:
            self._tray_icon.setToolTip(status)
