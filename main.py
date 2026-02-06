"""Main application entry point."""
from __future__ import annotations

import time
from pathlib import Path

from pokerlens.core.screen_capture import ScreenCapture
from pokerlens.core.table_detector import TableDetector
import config


def main():
    """Main application loop."""
    print(f"{config.APP_NAME} starting...")

    detector = TableDetector()
    capture = ScreenCapture()

    if config.DEBUG_SAVE_CAPTURES:
        config.DEBUG_CAPTURE_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Monitoring for PokerStars tables...")
    print(f"Capture interval: {config.CAPTURE_INTERVAL_MS}ms")
    print(f"Debug mode: {config.DEBUG_SAVE_CAPTURES}")

    capture_count = 0
    tracked_tables = {}

    try:
        while True:
            tables = detector.find_tables()

            current_hwnds = {table.hwnd for table in tables}
            previous_hwnds = set(tracked_tables.keys())

            new_tables = current_hwnds - previous_hwnds
            closed_tables = previous_hwnds - current_hwnds

            for hwnd in new_tables:
                table = next(t for t in tables if t.hwnd == hwnd)
                print(f"[+] New table detected: {table.title}")
                tracked_tables[hwnd] = table

            for hwnd in closed_tables:
                table = tracked_tables[hwnd]
                print(f"[-] Table closed: {table.title}")
                del tracked_tables[hwnd]

            for table in tables:
                if not detector.is_table_active(table.hwnd):
                    continue

                current_pos = detector.get_window_position(table.hwnd)
                if current_pos:
                    x, y, width, height = current_pos
                    if (x, y, width, height) != table.region:
                        tracked_tables[table.hwnd] = table._replace(
                            x=x, y=y, width=width, height=height
                        )

                try:
                    img = capture.capture_region(*table.region)

                    if config.DEBUG_SAVE_CAPTURES and capture_count % 10 == 0:
                        timestamp = int(time.time())
                        filename = f"table_{table.hwnd}_{timestamp}.png"
                        filepath = config.DEBUG_CAPTURE_DIR / filename
                        capture.save_capture(img, filepath)
                        print(f"[DEBUG] Saved capture: {filename}")

                except Exception as e:
                    print(f"[ERROR] Failed to capture table {table.hwnd}: {e}")

            capture_count += 1
            time.sleep(config.CAPTURE_INTERVAL_MS / 1000.0)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        capture.close()
        print("Cleanup complete.")


if __name__ == "__main__":
    main()
