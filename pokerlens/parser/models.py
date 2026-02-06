"""Data models for hand state, actions, and table snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Street(Enum):
    """Poker street/round."""

    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"


class ActionType(Enum):
    """Poker action types."""

    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all-in"
    POST_BLIND = "post_blind"


class Position(Enum):
    """Player positions."""

    BTN = "button"
    SB = "small_blind"
    BB = "big_blind"
    UTG = "under_the_gun"
    MP = "middle_position"
    CO = "cutoff"
    UNKNOWN = "unknown"


@dataclass
class PlayerAction:
    """A single player action."""

    player_name: str
    seat_number: int
    action_type: ActionType
    amount: float
    street: Street
    timestamp: datetime = field(default_factory=datetime.now)
    is_voluntary: bool = True

    def __repr__(self) -> str:
        """String representation."""
        amt_str = f" ${self.amount:.2f}" if self.amount > 0 else ""
        return f"{self.player_name} {self.action_type.value}{amt_str}"


@dataclass
class SeatInfo:
    """Information about a table seat."""

    seat_number: int
    player_name: str
    stack_size: float
    is_occupied: bool
    has_cards: bool
    current_bet: float = 0.0
    position: Position = Position.UNKNOWN
    is_sitting_out: bool = False

    def __repr__(self) -> str:
        """String representation."""
        status = "active" if self.has_cards else "sitting out" if self.is_sitting_out else "empty"
        return f"Seat {self.seat_number}: {self.player_name} (${self.stack_size:.2f}) - {status}"


@dataclass
class TableSnapshot:
    """Complete table state at a point in time."""

    timestamp: datetime
    seats: dict[int, SeatInfo]
    dealer_position: int
    pot_size: float
    current_street: Street
    community_cards: list[str] = field(default_factory=list)
    last_action: Optional[PlayerAction] = None

    def get_active_players(self) -> list[SeatInfo]:
        """Get list of players with cards."""
        return [seat for seat in self.seats.values() if seat.has_cards]

    def get_player_by_name(self, name: str) -> Optional[SeatInfo]:
        """Find player by name."""
        for seat in self.seats.values():
            if seat.player_name == name:
                return seat
        return None

    def __repr__(self) -> str:
        """String representation."""
        active = len(self.get_active_players())
        return (
            f"TableSnapshot(pot=${self.pot_size:.2f}, "
            f"street={self.current_street.value}, "
            f"active_players={active})"
        )


@dataclass
class HandState:
    """Complete state of a poker hand."""

    hand_id: Optional[int]
    hand_number: Optional[int]
    started_at: datetime
    current_street: Street
    pot_size: float
    community_cards: list[str]
    actions: list[PlayerAction]
    seats: dict[int, SeatInfo]
    dealer_position: int
    is_complete: bool = False

    def add_action(self, action: PlayerAction) -> None:
        """Add an action to the hand history."""
        self.actions.append(action)

    def get_actions_for_street(self, street: Street) -> list[PlayerAction]:
        """Get all actions for a specific street."""
        return [a for a in self.actions if a.street == street]

    def get_player_actions(self, player_name: str) -> list[PlayerAction]:
        """Get all actions for a specific player."""
        return [a for a in self.actions if a.player_name == player_name]

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Hand #{self.hand_number or 'unknown'} "
            f"({self.current_street.value}, "
            f"${self.pot_size:.2f}, "
            f"{len(self.actions)} actions)"
        )
