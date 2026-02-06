"""Statistical calculations for poker players."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pokerlens.storage.database import Database


@dataclass
class PlayerStats:
    """Calculated player statistics."""

    player_id: int
    username: str
    total_hands: int
    vpip: float
    pfr: float
    af: float
    three_bet_pct: float
    fold_to_cbet_pct: float

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.username} ({self.total_hands} hands): "
            f"VPIP={self.vpip:.1f}% PFR={self.pfr:.1f}% AF={self.af:.2f} "
            f"3B={self.three_bet_pct:.1f}% FCB={self.fold_to_cbet_pct:.1f}%"
        )


class StatsCalculator:
    """Calculate poker statistics from database."""

    def __init__(self, database: Database):
        """
        Initialize calculator.

        Args:
            database: Database instance.
        """
        self.db = database

    def calculate_player_stats(self, player_id: int) -> Optional[PlayerStats]:
        """
        Calculate all stats for a player.

        Args:
            player_id: Player ID.

        Returns:
            PlayerStats or None if player not found.
        """
        player = self.db.get_player_by_id(player_id)
        if not player:
            return None

        total_hands = self._get_total_hands(player_id)
        if total_hands == 0:
            return PlayerStats(
                player_id=player_id,
                username=player["username"],
                total_hands=0,
                vpip=0.0,
                pfr=0.0,
                af=0.0,
                three_bet_pct=0.0,
                fold_to_cbet_pct=0.0,
            )

        vpip = self._calculate_vpip(player_id, total_hands)
        pfr = self._calculate_pfr(player_id, total_hands)
        af = self._calculate_af(player_id)
        three_bet_pct = self._calculate_three_bet_pct(player_id)
        fold_to_cbet_pct = self._calculate_fold_to_cbet_pct(player_id)

        return PlayerStats(
            player_id=player_id,
            username=player["username"],
            total_hands=total_hands,
            vpip=vpip,
            pfr=pfr,
            af=af,
            three_bet_pct=three_bet_pct,
            fold_to_cbet_pct=fold_to_cbet_pct,
        )

    def _get_total_hands(self, player_id: int) -> int:
        """Get total hands played."""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(DISTINCT hand_id) FROM hand_actions WHERE player_id = ?",
                (player_id,)
            )
            return cursor.fetchone()[0]

    def _calculate_vpip(self, player_id: int, total_hands: int) -> float:
        """
        Calculate VPIP (Voluntarily Put $ In Pot).

        Percentage of hands where player made voluntary preflop action.
        """
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(DISTINCT hand_id) FROM hand_actions
                WHERE player_id = ? 
                AND street = 'preflop'
                AND is_voluntary = 1
                AND action IN ('call', 'bet', 'raise', 'all-in')
                """,
                (player_id,)
            )
            vpip_hands = cursor.fetchone()[0]
            return (vpip_hands / total_hands * 100) if total_hands > 0 else 0.0

    def _calculate_pfr(self, player_id: int, total_hands: int) -> float:
        """
        Calculate PFR (Pre-Flop Raise %).

        Percentage of hands where player raised preflop.
        """
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(DISTINCT hand_id) FROM hand_actions
                WHERE player_id = ?
                AND street = 'preflop'
                AND action IN ('raise', 'all-in')
                """,
                (player_id,)
            )
            pfr_hands = cursor.fetchone()[0]
            return (pfr_hands / total_hands * 100) if total_hands > 0 else 0.0

    def _calculate_af(self, player_id: int) -> float:
        """
        Calculate AF (Aggression Factor).

        (Bets + Raises) / Calls on postflop streets.
        """
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT COUNT(*) FROM hand_actions
                WHERE player_id = ?
                AND street IN ('flop', 'turn', 'river')
                AND action IN ('bet', 'raise', 'all-in')
                """,
                (player_id,)
            )
            aggressive_actions = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*) FROM hand_actions
                WHERE player_id = ?
                AND street IN ('flop', 'turn', 'river')
                AND action = 'call'
                """,
                (player_id,)
            )
            calls = cursor.fetchone()[0]

            return (aggressive_actions / calls) if calls > 0 else float(aggressive_actions)

    def _calculate_three_bet_pct(self, player_id: int) -> float:
        """
        Calculate 3-Bet %.

        Percentage of opportunities where player 3-bet preflop.
        This is a simplified calculation - full implementation would track facing raises.
        """
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT COUNT(*) FROM hand_actions
                WHERE player_id = ?
                AND street = 'preflop'
                AND action IN ('raise')
                """,
                (player_id,)
            )
            three_bets = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(DISTINCT hand_id) FROM hand_actions
                WHERE player_id = ?
                AND street = 'preflop'
                """,
                (player_id,)
            )
            opportunities = cursor.fetchone()[0]

            return (three_bets / opportunities * 100) if opportunities > 0 else 0.0

    def _calculate_fold_to_cbet_pct(self, player_id: int) -> float:
        """
        Calculate Fold to C-Bet %.

        Percentage of times player folded to continuation bet on flop.
        Simplified implementation.
        """
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT COUNT(*) FROM hand_actions
                WHERE player_id = ?
                AND street = 'flop'
                AND action = 'fold'
                """,
                (player_id,)
            )
            folds = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*) FROM hand_actions
                WHERE player_id = ?
                AND street = 'flop'
                AND action IN ('fold', 'call', 'raise')
                """,
                (player_id,)
            )
            opportunities = cursor.fetchone()[0]

            return (folds / opportunities * 100) if opportunities > 0 else 0.0
