"""Tests for screen capture functionality."""
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from pokerlens.core.screen_capture import ScreenCapture


@pytest.fixture
def screen_capture():
    """Create a ScreenCapture instance for testing."""
    with patch("pokerlens.core.screen_capture.mss.mss") as mock_mss:
        mock_instance = MagicMock()
        mock_mss.return_value = mock_instance
        mock_instance.monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},  # All monitors
            {"left": 0, "top": 0, "width": 1920, "height": 1080},  # Monitor 1
        ]
        
        capture = ScreenCapture()
        capture._sct = mock_instance
        yield capture


def test_screen_capture_initialization(screen_capture):
    """Test ScreenCapture initializes correctly."""
    assert screen_capture._sct is not None


def test_get_monitor_count(screen_capture):
    """Test monitor count detection."""
    assert screen_capture.get_monitor_count() == 1


def test_get_monitor_dimensions(screen_capture):
    """Test retrieving monitor dimensions."""
    x, y, width, height = screen_capture.get_monitor_dimensions(1)
    assert x == 0
    assert y == 0
    assert width == 1920
    assert height == 1080


def test_invalid_monitor_number(screen_capture):
    """Test error handling for invalid monitor numbers."""
    with pytest.raises(ValueError):
        screen_capture.get_monitor_dimensions(99)


def test_capture_region_invalid_dimensions(screen_capture):
    """Test error handling for invalid region dimensions."""
    with pytest.raises(ValueError):
        screen_capture.capture_region(0, 0, -100, 100)
    
    with pytest.raises(ValueError):
        screen_capture.capture_region(0, 0, 100, 0)


def test_context_manager(screen_capture):
    """Test ScreenCapture works as context manager."""
    with screen_capture as sc:
        assert sc is not None
    
    screen_capture._sct.close.assert_called_once()
