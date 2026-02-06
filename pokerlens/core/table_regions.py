"""Table region coordinate definitions for different table sizes."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class TableSize(Enum):
    """Supported table sizes."""

    SIX_MAX = 6
    NINE_MAX = 9


@dataclass
class RegionCoords:
    """Percentage-based coordinates for a screen region."""

    x_pct: float
    y_pct: float
    width_pct: float
    height_pct: float

    def to_absolute(self, table_width: int, table_height: int) -> tuple[int, int, int, int]:
        """
        Convert percentage-based coords to absolute pixels.

        Args:
            table_width: Width of table window in pixels.
            table_height: Height of table window in pixels.

        Returns:
            Tuple of (x, y, width, height) in pixels.
        """
        x = int(self.x_pct * table_width)
        y = int(self.y_pct * table_height)
        width = int(self.width_pct * table_width)
        height = int(self.height_pct * table_height)
        return (x, y, width, height)


@dataclass
class SeatRegions:
    """All regions for a single seat."""

    player_name: RegionCoords
    stack_size: RegionCoords
    bet_amount: RegionCoords
    action_text: RegionCoords
    cards: RegionCoords


REGION_MAPS: Dict[TableSize, Dict[int, SeatRegions]] = {
    TableSize.SIX_MAX: {
        0: SeatRegions(
            player_name=RegionCoords(0.35, 0.75, 0.30, 0.05),
            stack_size=RegionCoords(0.35, 0.80, 0.30, 0.05),
            bet_amount=RegionCoords(0.40, 0.65, 0.20, 0.05),
            action_text=RegionCoords(0.35, 0.70, 0.30, 0.05),
            cards=RegionCoords(0.40, 0.60, 0.20, 0.10),
        ),
        1: SeatRegions(
            player_name=RegionCoords(0.68, 0.60, 0.28, 0.05),
            stack_size=RegionCoords(0.68, 0.65, 0.28, 0.05),
            bet_amount=RegionCoords(0.55, 0.50, 0.20, 0.05),
            action_text=RegionCoords(0.68, 0.55, 0.28, 0.05),
            cards=RegionCoords(0.65, 0.45, 0.20, 0.10),
        ),
        2: SeatRegions(
            player_name=RegionCoords(0.68, 0.25, 0.28, 0.05),
            stack_size=RegionCoords(0.68, 0.30, 0.28, 0.05),
            bet_amount=RegionCoords(0.55, 0.35, 0.20, 0.05),
            action_text=RegionCoords(0.68, 0.20, 0.28, 0.05),
            cards=RegionCoords(0.65, 0.38, 0.20, 0.10),
        ),
        3: SeatRegions(
            player_name=RegionCoords(0.35, 0.08, 0.30, 0.05),
            stack_size=RegionCoords(0.35, 0.13, 0.30, 0.05),
            bet_amount=RegionCoords(0.40, 0.25, 0.20, 0.05),
            action_text=RegionCoords(0.35, 0.18, 0.30, 0.05),
            cards=RegionCoords(0.40, 0.28, 0.20, 0.10),
        ),
        4: SeatRegions(
            player_name=RegionCoords(0.04, 0.25, 0.28, 0.05),
            stack_size=RegionCoords(0.04, 0.30, 0.28, 0.05),
            bet_amount=RegionCoords(0.25, 0.35, 0.20, 0.05),
            action_text=RegionCoords(0.04, 0.20, 0.28, 0.05),
            cards=RegionCoords(0.15, 0.38, 0.20, 0.10),
        ),
        5: SeatRegions(
            player_name=RegionCoords(0.04, 0.60, 0.28, 0.05),
            stack_size=RegionCoords(0.04, 0.65, 0.28, 0.05),
            bet_amount=RegionCoords(0.25, 0.50, 0.20, 0.05),
            action_text=RegionCoords(0.04, 0.55, 0.28, 0.05),
            cards=RegionCoords(0.15, 0.45, 0.20, 0.10),
        ),
    },
    TableSize.NINE_MAX: {
        0: SeatRegions(
            player_name=RegionCoords(0.36, 0.78, 0.28, 0.04),
            stack_size=RegionCoords(0.36, 0.82, 0.28, 0.04),
            bet_amount=RegionCoords(0.40, 0.68, 0.20, 0.04),
            action_text=RegionCoords(0.36, 0.73, 0.28, 0.04),
            cards=RegionCoords(0.40, 0.63, 0.20, 0.09),
        ),
        1: SeatRegions(
            player_name=RegionCoords(0.58, 0.68, 0.26, 0.04),
            stack_size=RegionCoords(0.58, 0.72, 0.26, 0.04),
            bet_amount=RegionCoords(0.50, 0.58, 0.18, 0.04),
            action_text=RegionCoords(0.58, 0.63, 0.26, 0.04),
            cards=RegionCoords(0.55, 0.53, 0.18, 0.09),
        ),
        2: SeatRegions(
            player_name=RegionCoords(0.72, 0.52, 0.24, 0.04),
            stack_size=RegionCoords(0.72, 0.56, 0.24, 0.04),
            bet_amount=RegionCoords(0.58, 0.48, 0.18, 0.04),
            action_text=RegionCoords(0.72, 0.47, 0.24, 0.04),
            cards=RegionCoords(0.65, 0.43, 0.18, 0.09),
        ),
        3: SeatRegions(
            player_name=RegionCoords(0.72, 0.32, 0.24, 0.04),
            stack_size=RegionCoords(0.72, 0.36, 0.24, 0.04),
            bet_amount=RegionCoords(0.58, 0.40, 0.18, 0.04),
            action_text=RegionCoords(0.72, 0.27, 0.24, 0.04),
            cards=RegionCoords(0.65, 0.42, 0.18, 0.09),
        ),
        4: SeatRegions(
            player_name=RegionCoords(0.58, 0.16, 0.26, 0.04),
            stack_size=RegionCoords(0.58, 0.20, 0.26, 0.04),
            bet_amount=RegionCoords(0.50, 0.30, 0.18, 0.04),
            action_text=RegionCoords(0.58, 0.11, 0.26, 0.04),
            cards=RegionCoords(0.55, 0.33, 0.18, 0.09),
        ),
        5: SeatRegions(
            player_name=RegionCoords(0.36, 0.08, 0.28, 0.04),
            stack_size=RegionCoords(0.36, 0.12, 0.28, 0.04),
            bet_amount=RegionCoords(0.40, 0.22, 0.20, 0.04),
            action_text=RegionCoords(0.36, 0.04, 0.28, 0.04),
            cards=RegionCoords(0.40, 0.25, 0.20, 0.09),
        ),
        6: SeatRegions(
            player_name=RegionCoords(0.16, 0.16, 0.26, 0.04),
            stack_size=RegionCoords(0.16, 0.20, 0.26, 0.04),
            bet_amount=RegionCoords(0.32, 0.30, 0.18, 0.04),
            action_text=RegionCoords(0.16, 0.11, 0.26, 0.04),
            cards=RegionCoords(0.27, 0.33, 0.18, 0.09),
        ),
        7: SeatRegions(
            player_name=RegionCoords(0.04, 0.32, 0.24, 0.04),
            stack_size=RegionCoords(0.04, 0.36, 0.24, 0.04),
            bet_amount=RegionCoords(0.24, 0.40, 0.18, 0.04),
            action_text=RegionCoords(0.04, 0.27, 0.24, 0.04),
            cards=RegionCoords(0.17, 0.42, 0.18, 0.09),
        ),
        8: SeatRegions(
            player_name=RegionCoords(0.16, 0.68, 0.26, 0.04),
            stack_size=RegionCoords(0.16, 0.72, 0.26, 0.04),
            bet_amount=RegionCoords(0.32, 0.58, 0.18, 0.04),
            action_text=RegionCoords(0.16, 0.63, 0.26, 0.04),
            cards=RegionCoords(0.27, 0.53, 0.18, 0.09),
        ),
    },
}


def get_seat_regions(table_size: TableSize, seat_number: int) -> SeatRegions:
    """
    Get region definitions for a specific seat.

    Args:
        table_size: Table size (6-max or 9-max).
        seat_number: Seat number (0-indexed).

    Returns:
        SeatRegions for the specified seat.

    Raises:
        ValueError: If seat number is invalid for table size.
    """
    if table_size not in REGION_MAPS:
        raise ValueError(f"Unsupported table size: {table_size}")

    seat_map = REGION_MAPS[table_size]
    if seat_number not in seat_map:
        raise ValueError(
            f"Invalid seat {seat_number} for {table_size.name} table"
        )

    return seat_map[seat_number]
