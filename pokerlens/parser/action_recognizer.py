"""Classify OCR text into poker actions with amount parsing."""
from __future__ import annotations

import re
from typing import Optional

from pokerlens.parser.models import ActionType


class ActionRecognizer:
    """Recognizes and parses poker actions from OCR text."""

    ACTION_PATTERNS = {
        ActionType.FOLD: [
            r"\bfold\b",
            r"\bfolds\b",
            r"\bfolded\b",
        ],
        ActionType.CHECK: [
            r"\bcheck\b",
            r"\bchecks\b",
            r"\bchecked\b",
        ],
        ActionType.CALL: [
            r"\bcall\b",
            r"\bcalls\b",
            r"\bcalled\b",
        ],
        ActionType.BET: [
            r"\bbet\b",
            r"\bbets\b",
        ],
        ActionType.RAISE: [
            r"\braise\b",
            r"\braises\b",
            r"\braised\b",
            r"\bre-raise\b",
            r"\breraise\b",
        ],
        ActionType.ALL_IN: [
            r"\ball.?in\b",
            r"\ballin\b",
        ],
    }

    AMOUNT_PATTERN = re.compile(
        r"[\$€£]?\s*(\d+(?:[,\.]\d+)?)",
        re.IGNORECASE
    )

    def __init__(self):
        """Initialize action recognizer with compiled patterns."""
        self._compiled_patterns = {
            action: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for action, patterns in self.ACTION_PATTERNS.items()
        }

    def recognize_action(self, text: str) -> Optional[ActionType]:
        """
        Identify action type from OCR text.

        Args:
            text: OCR result text.

        Returns:
            ActionType if recognized, None otherwise.
        """
        if not text:
            return None

        text_lower = text.lower().strip()

        for action_type, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(text_lower):
                    return action_type

        return None

    def parse_amount(self, text: str) -> float:
        """
        Extract monetary amount from text.

        Args:
            text: OCR result text containing amount.

        Returns:
            Parsed amount as float, or 0.0 if not found.
        """
        if not text:
            return 0.0

        text_clean = text.replace(",", "").replace(" ", "")

        match = self.AMOUNT_PATTERN.search(text_clean)
        if match:
            try:
                amount_str = match.group(1).replace(",", "")
                return float(amount_str)
            except (ValueError, AttributeError):
                pass

        return 0.0

    def parse_action_with_amount(self, text: str) -> tuple[Optional[ActionType], float]:
        """
        Parse both action type and amount from text.

        Args:
            text: OCR result text like "Raises $2.50" or "Bets 150".

        Returns:
            Tuple of (ActionType, amount).
        """
        action = self.recognize_action(text)
        amount = self.parse_amount(text)
        return (action, amount)

    def is_voluntary_action(self, action: ActionType) -> bool:
        """
        Check if action is voluntary (not blind posting).

        Args:
            action: Action type.

        Returns:
            True if action is voluntary.
        """
        return action not in {ActionType.POST_BLIND}

    def normalize_action_text(self, text: str) -> str:
        """
        Normalize action text for consistent parsing.

        Args:
            text: Raw OCR text.

        Returns:
            Normalized text.
        """
        if not text:
            return ""

        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        text = text.replace("aii", "all")
        text = text.replace("Foid", "Fold")
        text = text.replace("Cail", "Call")

        return text
