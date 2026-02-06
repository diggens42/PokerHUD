"""Main application entry point."""
from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QInputDialog

from pokerlens.core.ocr_engine import OCREngine
from pokerlens.core.screen_capture import ScreenCapture
from pokerlens.core.table_detector import TableDetector
from pokerlens.core.table_regions import TableSize
from pokerlens.overlay.hud_window import HUDWindow
from pokerlens.overlay.position_tracker import PositionTracker
from pokerlens.overlay.stat_widget import StatWidget
from pokerlens.overlay.system_tray import SystemTray
from pokerlens.overlay.settings import Settings, SettingsDialog
from pokerlens.parser.table_state import TableStateParser
from pokerlens.parser.hand_tracker import HandTracker
from pokerlens.storage.database import Database
from pokerlens.storage.session import SessionManager
from pokerlens.stats.calculator import StatsCalculator
from pokerlens.utils.logger import get_logger
import config


class PokerHUDApp:
    """Main application controller with multi-table support."""

    def __init__(self):
        """Initialize application."""
        self.logger = get_logger()
        
        self.settings = Settings()
        self.settings.apply_to_config()
        
        self.detector = TableDetector()
        self.capture = ScreenCapture()
        self.ocr = OCREngine(self.settings.get("tesseract_path"))
        self.database = Database()
        self.session_manager = SessionManager(self.database)
        self.stats_calculator = StatsCalculator(self.database)
        
        self.tracked_tables: dict[int, dict] = {}
        self.hud_windows: dict[int, HUDWindow] = {}
        
        self.app = QApplication(sys.argv)
        self.max_tables = self.settings.get("max_tables", 10)
        self.is_tracking = False
        
        self.system_tray = SystemTray()
        self.system_tray.start_tracking.connect(self._start_tracking)
        self.system_tray.stop_tracking.connect(self._stop_tracking)
        self.system_tray.open_settings.connect(self._open_settings)
        self.system_tray.quit_app.connect(self._quit)
        self.system_tray.show()

    def _open_settings(self):
        """Open settings dialog."""
        dialog = SettingsDialog(self.settings)
        if dialog.exec():
            self.max_tables = self.settings.get("max_tables", 10)
            self.logger.info("Settings updated")
        self.system_tray.show_message("PokerHUD", "Application started. Click 'Start Tracking' to begin.")

        if config.DEBUG_SAVE_CAPTURES:
            config.DEBUG_CAPTURE_DIR.mkdir(parents=True, exist_ok=True)

        capture_count = 0

        try:
            while True:
                if not self.is_tracking:
                    self.app.processEvents()
                    time.sleep(0.1)
                    continue

                tables = self.detector.find_tables()
                
                if len(tables) > self.max_tables:
                    self.logger.warning(
                        "Too many tables detected",
                        count=len(tables),
                        max=self.max_tables
                    )
                    tables = tables[:self.max_tables]
                
                current_hwnds = {table.hwnd for table in tables}
                previous_hwnds = set(self.tracked_tables.keys())

                new_tables = current_hwnds - previous_hwnds
                closed_tables = previous_hwnds - current_hwnds

                for hwnd in new_tables:
                    self._handle_new_table(tables, hwnd)

                for hwnd in closed_tables:
                    self._handle_closed_table(hwnd)

                for table in tables:
                    if not self.detector.is_table_active(table.hwnd):
                        continue

                    self._update_table(table, capture_count)

                self.system_tray.update_table_count(len(self.tracked_tables))
                                if len(tables) > self.max_tables:
                    self.logger.warning(
                        "Too many tables detected",
                        count=len(tables),
                        max=self.max_tables
                    )
                    tables = tables[:self.max_tables]
                
                current_hwnds = {table.hwnd for table in tables}
                previous_hwnds = set(self.tracked_tables.keys())

                new_tables = current_hwnds - previous_hwnds
        self.system_tray.show_message(
            "New Table Detected",
            f"Now tracking: {table.title[:50]}",
            2000
        )
        
                closed_tables = previous_hwnds - current_hwnds

                for hwnd in new_tables:
                    self._handle_new_table(tables, hwnd)

                for hwnd in closed_tables:
                    self._handle_closed_table(hwnd)

                for table in tables:
                    if not self.detector.is_table_active(table.hwnd):
                        continue

                    self._update_table(table, capture_count)

                capture_count += 1
                self.app.processEvents()
                time.sleep(config.CAPTURE_INTERVAL_MS / 1000.0)

        except KeyboardInterrupt:
            self.logger.info("Shutting down")
        finally:
            self._cleanup()

    def _handle_new_table(self, tables: list, hwnd: int):
        """Handle new table detection with dedicated HUD."""
        table = next(t for t in tables if t.hwnd == hwnd)
        self.logger.info(
            "New table detected",
            table=table.title,
            position=f"{table.x},{table.y}",
            size=f"{table.width}x{table.height}"
        )
        
        table_size = self._detect_table_size(table.title)
        
        session_id = self.session_manager.start_session(
            table.title,
            stakes=self._parse_stakes(table.title),
            table_size=table_size.value
        )
        
        parser = TableStateParser(self.ocr, table_size)
        tracker = HandTracker()
        position_tracker = PositionTracker(table_size)
        stat_widget = StatWidget()
        
        opacity = self.settings.get("hud_opacity", 0.80)
        font_size = self.settings.get("font_size", 10)
        
        hud_window = HUDWindow(table.x, table.y, table.width, table.height, opacity=opacity)
        hud_window.set_font_size(font_size)
        hud_window.note_requested.connect(self._add_player_note)
        hud_window.show()
        
        self.tracked_tables[hwnd] = {
            "table": table,
            "session_id": session_id,
            "parser": parser,
            "tracker": tracker,
            "position_tracker": position_tracker,
            "stat_widget": stat_widget,
            "table_size": table_size,
        }
        self.hud_windows[hwnd] = hud_window
        
        self.logger.info("HUD created for table", hwnd=hwnd, active_tables=len(self.tracked_tables))

    def _handle_closed_table(self, hwnd: int):
        """Handle table closure and cleanup."""
        table_info = self.tracked_tables[hwnd]
        self.logger.info("Table closed", table=table_info["table"].title)
        
        self.session_manager.end_session(table_info["table"].title)
        
        if hwnd in self.hud_windows:
            self.hud_windows[hwnd].close()
            del self.hud_windows[hwnd]
        
        del self.tracked_tables[hwnd]
        
        self.logger.info("HUD removed", active_tables=len(self.tracked_tables))

    def _detect_table_size(self, title: str) -> TableSize:
        """Detect table size from title."""
        if "6-max" in title.lower() or "6 max" in title.lower():
            return TableSize.SIX_MAX
        elif "9-max" in title.lower() or "9 max" in title.lower():
            return TableSize.NINE_MAX
        return TableSize.SIX_MAX

    def _parse_stakes(self, title: str) -> str:
        """Parse stakes from table title."""
        import re
        match = re.search(r"\$[\d.]+/\$[\d.]+", title)
        if match:
            return match.group(0)
        return "Unknown"

    def _add_player_note(self, player_name: str):
        """Add note for player."""
        from PyQt6.QtWidgets import QInputDialog
        
        player = self.database.get_player_by_username(player_name)
        if not player:
            return
        
        current_note = player.get("notes", "")
        note, ok = QInputDialog.getMultiLineText(
            None,
            "Player Note",
            f"Note for {player_name}:",
            current_note
        )
        
        if ok:
            self.database.update_player_notes(player["id"], note)
            self.logger.info("Note added", player=player_name)

    def _update_table(self, table, capture_count: int):
        """Update table state and HUD."""
        hwnd = table.hwnd
        
        current_pos = self.detector.get_window_position(hwnd)
        if current_pos:
            x, y, width, height = current_pos
            if (x, y, width, height) != table.region:
                table = table._replace(x=x, y=y, width=width, height=height)
                self.tracked_tables[hwnd]["table"] = table
                
                if hwnd in self.hud_windows:
                    self.hud_windows[hwnd].update_position(x, y, width, height)

        try:
            img = self.capture.capture_region(*table.region)
            
            table_info = self.tracked_tables[hwnd]
            parser = table_info["parser"]
            position_tracker = table_info["position_tracker"]
            stat_widget = table_info["stat_widget"]
            
            snapshot = parser.parse_table(img, table.width, table.height)
            
            stat_displays = []
            seat_positions = position_tracker.calculate_seat_positions(
                table.x, table.y, table.width, table.height
            )
            
            for seat_num, seat_info in snapshot.seats.items():
                if not seat_info.is_occupied:
                    continue
                
                player = self.database.get_player_by_username(seat_info.player_name)
                if player:
                    stats = self.stats_calculator.calculate_player_stats(player["id"])
                    if stats and stats.total_hands >= 10:
                        pos = seat_positions[seat_num]
                        stat_text = stat_widget.format_stats(
                            stats.username,
                            stats.total_hands,
                            stats.vpip,
                            stats.pfr,
                            stats.af,
                            stats.three_bet_pct,
                            stats.fold_to_cbet_pct,
                            self.database,
                        )
                        stat_displays.append((pos.x, pos.y, stat_text, seat_info.player_name))
            
            if hwnd in self.hud_windows:
                self.hud_windows[hwnd].set_stats_display(stat_displays)
            
            if config.DEBUG_SAVE_CAPTURES and capture_count % 20 == 0:
                timestamp = int(time.time())
                filename = f"table_{hwnd}_{timestamp}.png"
                filepath = config.DEBUG_CAPTURE_DIR / filename
                self.capture.save_capture(img, filepath)

        except Exception as e:
            self.logger.error("Failed to update table", hwnd=hwnd, error=str(e))

    def _cleanup(self):
        """Cleanup resources."""
        self.session_manager.end_all_sessions()
        
        for hud_window in self.hud_windows.values():
            hud_window.close()
        
        self.capture.close()
        self.logger.info("Cleanup complete")


def main():
    """Main entry point."""
    app = PokerHUDApp()
    app.run()


if __name__ == "__main__":
    main()
