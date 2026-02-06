"""Map seat positions to screen coordinates with resize handling."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pokerlens.core.table_regions import TableSize, get_seat_regions


@dataclass
class SeatPosition:
    """Screen position for a seat's HUD display."""

    seat_number: int
    x: int
    y: int
    width: int = 120
    height: int = 60


class PositionTracker:
    """Tracks and updates HUD positions relative to table windows."""

    STAT_DISPLAY_OFFSET_X_PCT = 0.02
    STAT_DISPLAY_OFFSET_Y_PCT = -0.08

    def __init__(self, table_size: TableSize = TableSize.SIX_MAX):
        """
        Initialize position tracker.

        Args:
            table_size: Table size (6-max or 9-max).
        """
        self.table_size = table_size
        self._cached_positions: dict[int, SeatPosition] = {}
        self._last_table_dimensions: Optional[tuple[int, int, int, int]] = None

    def calculate_seat_positions(
        self,
        table_x: int,
        table_y: int,
        table_width: int,
        table_height: int,
    ) -> dict[int, SeatPosition]:
        """
        Calculate screen positions for all seat HUD displays.

        Args:
            table_x: Table window X position.
            table_y: Table window Y position.
            table_width: Table window width.
            table_height: Table window height.

        Returns:
            Dictionary mapping seat number to SeatPosition.
        """
        current_dims = (table_x, table_y, table_width, table_height)
        
        if current_dims == self._last_table_dimensions and self._cached_positions:
            return self._cached_positions

        positions = {}

        for seat_num in range(self.table_size.value):
            seat_regions = get_seat_regions(self.table_size, seat_num)
            
            name_region = seat_regions.player_name
            
            base_x = int(name_region.x_pct * table_width)
            base_y = int(name_region.y_pct * table_height)
            
            offset_x = int(self.STAT_DISPLAY_OFFSET_X_PCT * table_width)
            offset_y = int(self.STAT_DISPLAY_OFFSET_Y_PCT * table_height)
            
            display_x = table_x + base_x + offset_x
            display_y = table_y + base_y + offset_y
            
            positions[seat_num] = SeatPosition(
                seat_number=seat_num,
                x=display_x,
                y=display_y,
            )

        self._cached_positions = positions
        self._last_table_dimensions = current_dims

        return positions

    def get_seat_position(
        self,
        seat_number: int,
        table_x: int,
        table_y: int,
        table_width: int,
        table_height: int,
    ) -> Optional[SeatPosition]:
        """
        Get position for specific seat.

        Args:
            seat_number: Seat number.
            table_x: Table window X position.
            table_y: Table window Y position.
            table_width: Table window width.
            table_height: Table window height.

        Returns:
            SeatPosition or None if seat invalid.
        """
        positions = self.calculate_seat_positions(table_x, table_y, table_width, table_height)
        return positions.get(seat_number)

    def has_table_moved(
        self,
        table_x: int,
        table_y: int,
        table_width: int,
        table_height: int,
    ) -> bool:
        """
        Check if table dimensions have changed.

        Args:
            table_x: Current table X.
            table_y: Current table Y.
            table_width: Current table width.
            table_height: Current table height.

        Returns:
            True if table has moved or resized.
        """
        if not self._last_table_dimensions:
            return True

        return self._last_table_dimensions != (table_x, table_y, table_width, table_height)

    def clear_cache(self) -> None:
        """Clear cached positions."""
        self._cached_positions.clear()
        self._last_table_dimensions = None

    def adjust_for_seat_count(self, active_seat_count: int) -> None:
        """
        Adjust display strategy based on active seats.

        Args:
            active_seat_count: Number of occupied seats.
        """
        pass
