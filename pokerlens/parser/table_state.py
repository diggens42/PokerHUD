"""Parse full table state from OCR and detect actions via diffing."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from PIL import Image

from pokerlens.core.ocr_engine import OCREngine
from pokerlens.core.table_regions import TableSize, get_seat_regions
from pokerlens.parser.action_recognizer import ActionRecognizer
from pokerlens.parser.models import PlayerAction, SeatInfo, Street, TableSnapshot


class TableStateParser:
    """Parses complete table state from OCR."""

    def __init__(self, ocr: OCREngine, table_size: TableSize = TableSize.SIX_MAX):
        """
        Initialize table state parser.

        Args:
            ocr: OCR engine instance.
            table_size: Table size (6-max or 9-max).
        """
        self.ocr = ocr
        self.table_size = table_size
        self.action_recognizer = ActionRecognizer()
        self._previous_snapshot: Optional[TableSnapshot] = None

    def parse_table(
        self,
        table_image: Image.Image,
        table_width: int,
        table_height: int,
    ) -> TableSnapshot:
        """
        Parse complete table state from image.

        Args:
            table_image: Captured table image.
            table_width: Table window width.
            table_height: Table window height.

        Returns:
            TableSnapshot with current table state.
        """
        seats = {}

        for seat_num in range(self.table_size.value):
            seat_regions = get_seat_regions(self.table_size, seat_num)

            name_coords = seat_regions.player_name.to_absolute(table_width, table_height)
            stack_coords = seat_regions.stack_size.to_absolute(table_width, table_height)
            bet_coords = seat_regions.bet_amount.to_absolute(table_width, table_height)

            name_result = self.ocr.read_text(table_image, region=name_coords)
            player_name = name_result.text if name_result.confidence > 50 else ""

            is_occupied = self.ocr.is_valid_player_name(player_name)
            has_cards = is_occupied

            stack_size = 0.0
            if is_occupied:
                stack_result = self.ocr.read_number(table_image, region=stack_coords)
                stack_size = self.action_recognizer.parse_amount(stack_result.text)

            current_bet = 0.0
            if is_occupied:
                bet_result = self.ocr.read_number(table_image, region=bet_coords)
                current_bet = self.action_recognizer.parse_amount(bet_result.text)

            seats[seat_num] = SeatInfo(
                seat_number=seat_num,
                player_name=player_name,
                stack_size=stack_size,
                is_occupied=is_occupied,
                has_cards=has_cards,
                current_bet=current_bet,
            )

        snapshot = TableSnapshot(
            timestamp=datetime.now(),
            seats=seats,
            dealer_position=0,
            pot_size=0.0,
            current_street=Street.PREFLOP,
            community_cards=[],
        )

        return snapshot

    def detect_actions(
        self,
        current_snapshot: TableSnapshot,
    ) -> list[PlayerAction]:
        """
        Detect actions by comparing snapshots.

        Args:
            current_snapshot: Current table snapshot.

        Returns:
            List of detected actions.
        """
        actions = []

        if not self._previous_snapshot:
            self._previous_snapshot = current_snapshot
            return actions

        for seat_num, current_seat in current_snapshot.seats.items():
            if not current_seat.is_occupied:
                continue

            prev_seat = self._previous_snapshot.seats.get(seat_num)
            if not prev_seat or not prev_seat.is_occupied:
                continue

            bet_change = current_seat.current_bet - prev_seat.current_bet
            stack_change = prev_seat.stack_size - current_seat.stack_size

            if bet_change > 0 or stack_change > 0:
                pass

        self._previous_snapshot = current_snapshot

        return actions

    def reset(self) -> None:
        """Reset parser state."""
        self._previous_snapshot = None
