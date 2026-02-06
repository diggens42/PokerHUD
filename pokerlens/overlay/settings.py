"""Settings dialog and configuration management."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QDoubleSpinBox, QPushButton, QGroupBox, QFormLayout,
    QFileDialog, QCheckBox
)
from PyQt6.QtCore import Qt

import config


class Settings:
    """Application settings manager."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize settings.

        Args:
            config_path: Path to config JSON file.
        """
        self.config_path = config_path or (config.DATA_DIR / "settings.json")
        self.settings: dict[str, Any] = self._load_defaults()
        self.load()

    def _load_defaults(self) -> dict[str, Any]:
        """Load default settings."""
        return {
            "capture_interval_ms": config.CAPTURE_INTERVAL_MS,
            "tesseract_path": config.DEFAULT_TESSERACT_PATH,
            "db_path": str(config.DB_PATH),
            "debug_mode": config.DEBUG_SAVE_CAPTURES,
            "max_tables": 10,
            "hud_opacity": 0.85,
            "font_size": 10,
            "show_welcome": True,
            "vpip_tight": 20.0,
            "vpip_loose": 35.0,
            "pfr_tight": 15.0,
            "pfr_loose": 25.0,
            "af_passive": 1.5,
            "af_aggressive": 3.0,
        }

    def load(self) -> None:
        """Load settings from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    saved = json.load(f)
                    self.settings.update(saved)
            except Exception:
                pass

    def save(self) -> None:
        """Save settings to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.settings, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value."""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set setting value."""
        self.settings[key] = value

    def apply_to_config(self) -> None:
        """Apply settings to config module."""
        config.CAPTURE_INTERVAL_MS = self.get("capture_interval_ms", 500)
        config.DEBUG_SAVE_CAPTURES = self.get("debug_mode", False)
        config.DEFAULT_TESSERACT_PATH = self.get("tesseract_path", "")


class SettingsDialog(QDialog):
    """Settings dialog window."""

    def __init__(self, settings: Settings, parent=None):
        """
        Initialize settings dialog.

        Args:
            settings: Settings instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.settings = settings
        self._setup_ui()
        self._load_values()

    def _setup_ui(self):
        """Setup UI elements."""
        self.setWindowTitle("PokerHUD Settings")
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        general_group = self._create_general_group()
        layout.addWidget(general_group)

        hud_group = self._create_hud_group()
        layout.addWidget(hud_group)

        stats_group = self._create_stats_group()
        layout.addWidget(stats_group)

        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self._save_settings)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_general_group(self) -> QGroupBox:
        """Create general settings group."""
        group = QGroupBox("General")
        form = QFormLayout()

        self.capture_interval = QSpinBox()
        self.capture_interval.setRange(100, 2000)
        self.capture_interval.setSuffix(" ms")
        form.addRow("Capture Interval:", self.capture_interval)

        self.tesseract_path = QLineEdit()
        tesseract_layout = QHBoxLayout()
        tesseract_layout.addWidget(self.tesseract_path)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self._browse_tesseract)
        tesseract_layout.addWidget(browse_button)
        form.addRow("Tesseract Path:", tesseract_layout)

        self.debug_mode = QCheckBox("Save debug captures")
        form.addRow("Debug Mode:", self.debug_mode)

        self.max_tables = QSpinBox()
        self.max_tables.setRange(1, 20)
        form.addRow("Max Tables:", self.max_tables)

        group.setLayout(form)
        return group

    def _create_hud_group(self) -> QGroupBox:
        """Create HUD settings group."""
        group = QGroupBox("HUD Display")
        form = QFormLayout()

        self.hud_opacity = QDoubleSpinBox()
        self.hud_opacity.setRange(0.1, 1.0)
        self.hud_opacity.setSingleStep(0.05)
        form.addRow("Opacity:", self.hud_opacity)

        self.font_size = QSpinBox()
        self.font_size.setRange(6, 20)
        form.addRow("Font Size:", self.font_size)

        group.setLayout(form)
        return group

    def _create_stats_group(self) -> QGroupBox:
        """Create stats thresholds group."""
        group = QGroupBox("Stat Thresholds")
        form = QFormLayout()

        self.vpip_tight = QDoubleSpinBox()
        self.vpip_tight.setRange(0, 100)
        self.vpip_tight.setSuffix(" %")
        form.addRow("VPIP Tight:", self.vpip_tight)

        self.vpip_loose = QDoubleSpinBox()
        self.vpip_loose.setRange(0, 100)
        self.vpip_loose.setSuffix(" %")
        form.addRow("VPIP Loose:", self.vpip_loose)

        self.pfr_tight = QDoubleSpinBox()
        self.pfr_tight.setRange(0, 100)
        self.pfr_tight.setSuffix(" %")
        form.addRow("PFR Tight:", self.pfr_tight)

        self.pfr_loose = QDoubleSpinBox()
        self.pfr_loose.setRange(0, 100)
        self.pfr_loose.setSuffix(" %")
        form.addRow("PFR Loose:", self.pfr_loose)

        group.setLayout(form)
        return group

    def _load_values(self):
        """Load current settings into UI."""
        self.capture_interval.setValue(self.settings.get("capture_interval_ms", 500))
        self.hud_opacity.setValue(self.settings.get("hud_opacity", 0.80))
        self.font_size.setValue(self.settings.get("font_size", 10))
        self.tesseract_path.setText(self.settings.get("tesseract_path", ""))
        self.debug_mode.setChecked(self.settings.get("debug_mode", False))
        self.max_tables.setValue(self.settings.get("max_tables", 10))
        self.vpip_tight.setValue(self.settings.get("vpip_tight", 20.0))
        self.vpip_loose.setValue(self.settings.get("vpip_loose", 35.0))
        self.pfr_tight.setValue(self.settings.get("pfr_tight", 15.0))
        self.pfr_loose.setValue(self.settings.get("pfr_loose", 25.0))

    def _browse_tesseract(self):
        """Browse for Tesseract executable."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Tesseract Executable",
            "",
            "Executable (*.exe);;All Files (*.*)"
        )
        if path:
            self.tesseract_path.setText(path)

    def _save_settings(self):
        """Save settings and close."""
        self.settings.set("capture_interval_ms", self.capture_interval.value())
        self.settings.set("hud_opacity", self.hud_opacity.value())
        self.settings.set("font_size", self.font_size.value())
        self.settings.set("tesseract_path", self.tesseract_path.text())
        self.settings.set("debug_mode", self.debug_mode.isChecked())
        self.settings.set("max_tables", self.max_tables.value())
        self.settings.set("vpip_tight", self.vpip_tight.value())
        self.settings.set("vpip_loose", self.vpip_loose.value())
        self.settings.set("pfr_tight", self.pfr_tight.value())
        self.settings.set("pfr_loose", self.pfr_loose.value())
        
        self.settings.save()
        self.settings.apply_to_config()
        
        self.accept()
