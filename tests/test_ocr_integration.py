"""Integration test for OCR with table regions."""
from pathlib import Path

from PIL import Image

from pokerlens.core.ocr_engine import OCREngine
from pokerlens.core.screen_capture import ScreenCapture
from pokerlens.core.table_detector import TableDetector
from pokerlens.core.table_regions import TableSize, get_seat_regions
import config


def test_ocr_integration():
    """Test OCR integration with table region extraction."""
    config.DEBUG_SAVE_CAPTURES = True
    config.DEBUG_CAPTURE_DIR.mkdir(parents=True, exist_ok=True)

    detector = TableDetector()
    capture = ScreenCapture()
    ocr = OCREngine()

    tables = detector.find_tables()

    if not tables:
        print("No PokerStars tables detected. Open a table to test.")
        return

    print(f"Found {len(tables)} table(s)")

    for table in tables:
        print(f"\n{'='*60}")
        print(f"Table: {table.title}")
        print(f"Position: ({table.x}, {table.y})")
        print(f"Size: {table.width}x{table.height}")
        print(f"{'='*60}\n")

        try:
            table_image = capture.capture_region(*table.region)

            debug_path = config.DEBUG_CAPTURE_DIR / f"table_{table.hwnd}_full.png"
            capture.save_capture(table_image, debug_path)
            print(f"[DEBUG] Saved full table capture: {debug_path.name}")

            table_size = TableSize.SIX_MAX

            for seat_num in range(table_size.value):
                print(f"\nSeat {seat_num}:")

                seat_regions = get_seat_regions(table_size, seat_num)

                name_coords = seat_regions.player_name.to_absolute(
                    table.width, table.height
                )
                stack_coords = seat_regions.stack_size.to_absolute(
                    table.width, table.height
                )
                bet_coords = seat_regions.bet_amount.to_absolute(
                    table.width, table.height
                )

                name_result = ocr.read_text(table_image, region=name_coords)
                print(f"  Name: '{name_result.text}' (conf: {name_result.confidence:.1f}%)")

                stack_result = ocr.read_number(table_image, region=stack_coords)
                print(f"  Stack: '{stack_result.text}' (conf: {stack_result.confidence:.1f}%)")

                bet_result = ocr.read_number(table_image, region=bet_coords)
                print(f"  Bet: '{bet_result.text}' (conf: {bet_result.confidence:.1f}%)")

                x, y, w, h = name_coords
                name_crop = table_image.crop((x, y, x + w, y + h))
                crop_path = config.DEBUG_CAPTURE_DIR / f"seat{seat_num}_name.png"
                capture.save_capture(name_crop, crop_path)

        except Exception as e:
            print(f"[ERROR] Failed to process table: {e}")

    capture.close()
    print("\n[INFO] Integration test complete. Check captures/ directory for debug images.")


if __name__ == "__main__":
    test_ocr_integration()
