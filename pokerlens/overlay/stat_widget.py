"""Player stat display widget with color-coded thresholds."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PyQt6.QtGui import QColor


@dataclass
class StatThresholds:
    """Thresholds for color-coding stats."""

    vpip_tight: float = 20.0
    vpip_loose: float = 35.0
    
    pfr_tight: float = 15.0
    pfr_loose: float = 25.0
    
    af_passive: float = 1.5
    af_aggressive: float = 3.0
    
    three_bet_low: float = 5.0
    three_bet_high: float = 10.0
    
    fold_to_cbet_low: float = 40.0
    fold_to_cbet_high: float = 60.0


class StatWidget:
    """Formats and color-codes player statistics."""

    def __init__(self, thresholds: Optional[StatThresholds] = None):
        """
        Initialize stat widget.

        Args:
            thresholds: Custom stat thresholds for color coding.
        """
        self.thresholds = thresholds or StatThresholds()

    def format_stats(
        self,
        player_name: str,
        hands: int,
        vpip: float,
        pfr: float,
        af: float,
        three_bet: float,
        fold_to_cbet: float,
    ) -> str:
        """
        Format stats for display.

        Args:
            player_name: Player username.
            hands: Total hands observed.
            vpip: VPIP percentage.
            pfr: PFR percentage.
            af: Aggression factor.
            three_bet: 3-bet percentage.
            fold_to_cbet: Fold to c-bet percentage.

        Returns:
            Formatted stat string.
        """
        if hands < 10:
            return f"{player_name}\n({hands} hands)"

        return (
            f"{player_name}\n"
            f"VPIP: {vpip:.0f}% | PFR: {pfr:.0f}%\n"
            f"AF: {af:.1f} | 3B: {three_bet:.0f}%\n"
            f"FCB: {fold_to_cbet:.0f}% | {hands}h"
        )

    def get_vpip_color(self, vpip: float) -> QColor:
        """
        Get color for VPIP stat.

        Args:
            vpip: VPIP percentage.

        Returns:
            QColor for stat.
        """
        if vpip < self.thresholds.vpip_tight:
            return QColor(100, 200, 100)
        elif vpip > self.thresholds.vpip_loose:
            return QColor(255, 100, 100)
        else:
            return QColor(255, 255, 150)

    def get_pfr_color(self, pfr: float) -> QColor:
        """
        Get color for PFR stat.

        Args:
            pfr: PFR percentage.

        Returns:
            QColor for stat.
        """
        if pfr < self.thresholds.pfr_tight:
            return QColor(100, 200, 100)
        elif pfr > self.thresholds.pfr_loose:
            return QColor(255, 100, 100)
        else:
            return QColor(255, 255, 150)

    def get_af_color(self, af: float) -> QColor:
        """
        Get color for AF stat.

        Args:
            af: Aggression factor.

        Returns:
            QColor for stat.
        """
        if af < self.thresholds.af_passive:
            return QColor(100, 200, 100)
        elif af > self.thresholds.af_aggressive:
            return QColor(255, 100, 100)
        else:
            return QColor(255, 255, 150)

    def get_player_style(
        self,
        vpip: float,
        pfr: float,
        af: float,
    ) -> str:
        """
        Classify player style.

        Args:
            vpip: VPIP percentage.
            pfr: PFR percentage.
            af: Aggression factor.

        Returns:
            Style description (e.g., "TAG", "LAG", "Nit").
        """
        is_tight = vpip < self.thresholds.vpip_tight
        is_loose = vpip > self.thresholds.vpip_loose
        is_aggressive = af > self.thresholds.af_aggressive
        is_passive = af < self.thresholds.af_passive

        if is_tight and is_aggressive:
            return "TAG"
        elif is_tight and is_passive:
            return "Nit"
        elif is_loose and is_aggressive:
            return "LAG"
        elif is_loose and is_passive:
            return "Fish"
        else:
            return "Reg"

    def get_sample_quality(self, hands: int) -> str:
        """
        Get sample size quality indicator.

        Args:
            hands: Number of hands observed.

        Returns:
            Quality description.
        """
        if hands < 10:
            return "insufficient"
        elif hands < 50:
            return "limited"
        elif hands < 200:
            return "decent"
        else:
            return "reliable"
