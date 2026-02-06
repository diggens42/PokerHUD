"""Screen capture using mss library for fast screenshot acquisition."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import mss
import mss.tools
from PIL import Image


class ScreenCapture:
    """Handles screen capture operations using mss."""

    def __init__(self):
        """Initialize the screen capture system."""
        self._sct = mss.mss()

    def capture_full_screen(self, monitor_number: int = 1) -> Image.Image:
        """
        Capture the entire screen.

        Args:
            monitor_number: Monitor index (1-based). 0 captures all monitors.

        Returns:
            PIL Image of the captured screen.

        Raises:
            ValueError: If monitor number is invalid.
        """
        if monitor_number < 0 or monitor_number > len(self._sct.monitors) - 1:
            raise ValueError(
                f"Invalid monitor number {monitor_number}. "
                f"Available: 0-{len(self._sct.monitors) - 1}"
            )

        monitor = self._sct.monitors[monitor_number]
        sct_img = self._sct.grab(monitor)
        return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    def capture_region(
        self, x: int, y: int, width: int, height: int
    ) -> Image.Image:
        """
        Capture a specific screen region.

        Args:
            x: Left position in pixels.
            y: Top position in pixels.
            width: Width in pixels.
            height: Height in pixels.

        Returns:
            PIL Image of the captured region.

        Raises:
            ValueError: If region dimensions are invalid.
        """
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid dimensions: {width}x{height}")

        region = {"left": x, "top": y, "width": width, "height": height}
        sct_img = self._sct.grab(region)
        return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    def save_capture(
        self, image: Image.Image, filepath: Path | str, format: str = "PNG"
    ) -> None:
        """
        Save a captured image to disk.

        Args:
            image: PIL Image to save.
            filepath: Destination path.
            format: Image format (PNG, JPEG, etc.).

        Raises:
            IOError: If save operation fails.
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        try:
            image.save(filepath, format=format)
        except Exception as e:
            raise IOError(f"Failed to save image to {filepath}: {e}") from e

    def get_monitor_count(self) -> int:
        """
        Get the number of monitors available.

        Returns:
            Number of physical monitors (excludes virtual "all monitors" entry).
        """
        return len(self._sct.monitors) - 1

    def get_monitor_dimensions(self, monitor_number: int = 1) -> tuple[int, int, int, int]:
        """
        Get dimensions of a specific monitor.

        Args:
            monitor_number: Monitor index (1-based).

        Returns:
            Tuple of (x, y, width, height).

        Raises:
            ValueError: If monitor number is invalid.
        """
        if monitor_number < 1 or monitor_number > len(self._sct.monitors) - 1:
            raise ValueError(
                f"Invalid monitor number {monitor_number}. "
                f"Available: 1-{len(self._sct.monitors) - 1}"
            )

        monitor = self._sct.monitors[monitor_number]
        return (
            monitor["left"],
            monitor["top"],
            monitor["width"],
            monitor["height"],
        )

    def close(self) -> None:
        """Release screen capture resources."""
        self._sct.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
