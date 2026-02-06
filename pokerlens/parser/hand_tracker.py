"""Track hand boundaries and street progression via state changes."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pokerlens.parser.models import HandState, Street, SeatInfo


class HandTracker:
    """Tracks hand boundaries and maintains current hand state."""

    def __init__(self):
        """Initialize hand tracker."""
        self._current_hand: Optional[HandState] = None
        self._previous_pot: float = 0.0
        self._previous_dealer: int = -1
        self._previous_board_cards: list[str] = []
        self._hand_counter: int = 0

    @property
    def current_hand(self) -> Optional[HandState]:
        """Get current hand state."""
        return self._current_hand

    def detect_new_hand(
        self,
        dealer_position: int,
        pot_size: float,
        community_cards: list[str],
        seats: dict[int, SeatInfo],
    ) -> bool:
        """
        Detect if a new hand has started.

        Args:
            dealer_position: Current dealer button position.
            pot_size: Current pot size.
            community_cards: Community cards on board.
            seats: Current seat information.

        Returns:
            True if new hand detected.
        """
        is_new_hand = False

        if dealer_position != self._previous_dealer and dealer_position >= 0:
            is_new_hand = True

        if pot_size < self._previous_pot and pot_size >= 0:
            is_new_hand = True

        if len(community_cards) < len(self._previous_board_cards):
            is_new_hand = True

        active_players = sum(1 for seat in seats.values() if seat.has_cards)
        if active_players >= 2 and self._current_hand is None:
            is_new_hand = True

        return is_new_hand

    def start_new_hand(
        self,
        dealer_position: int,
        seats: dict[int, SeatInfo],
    ) -> HandState:
        """
        Start tracking a new hand.

        Args:
            dealer_position: Dealer button position.
            seats: Initial seat information.

        Returns:
            New HandState object.
        """
        if self._current_hand and not self._current_hand.is_complete:
            self._current_hand.is_complete = True

        self._hand_counter += 1

        self._current_hand = HandState(
            hand_id=None,
            hand_number=self._hand_counter,
            started_at=datetime.now(),
            current_street=Street.PREFLOP,
            pot_size=0.0,
            community_cards=[],
            actions=[],
            seats=seats.copy(),
            dealer_position=dealer_position,
            is_complete=False,
        )

        self._previous_dealer = dealer_position
        self._previous_pot = 0.0
        self._previous_board_cards = []

        return self._current_hand

    def detect_street_change(
        self,
        community_cards: list[str],
    ) -> Optional[Street]:
        """
        Detect if street has changed based on board cards.

        Args:
            community_cards: Current community cards.

        Returns:
            New street if changed, None otherwise.
        """
        if not self._current_hand:
            return None

        card_count = len(community_cards)

        if card_count == 0:
            new_street = Street.PREFLOP
        elif card_count == 3:
            new_street = Street.FLOP
        elif card_count == 4:
            new_street = Street.TURN
        elif card_count == 5:
            new_street = Street.RIVER
        else:
            return None

        if new_street != self._current_hand.current_street:
            self._current_hand.current_street = new_street
            self._previous_board_cards = community_cards.copy()
            return new_street

        return None

    def update_hand_state(
        self,
        pot_size: float,
        community_cards: list[str],
        seats: dict[int, SeatInfo],
    ) -> None:
        """
        Update current hand state.

        Args:
            pot_size: Current pot size.
            community_cards: Community cards.
            seats: Current seat information.
        """
        if not self._current_hand:
            return

        self._current_hand.pot_size = pot_size
        self._current_hand.community_cards = community_cards.copy()
        self._current_hand.seats = seats.copy()

        self._previous_pot = pot_size

        self.detect_street_change(community_cards)

    def end_current_hand(self) -> None:
        """Mark current hand as complete."""
        if self._current_hand:
            self._current_hand.is_complete = True

    def reset(self) -> None:
        """Reset tracker state."""
        self._current_hand = None
        self._previous_pot = 0.0
        self._previous_dealer = -1
        self._previous_board_cards = []
        self._hand_counter = 0
