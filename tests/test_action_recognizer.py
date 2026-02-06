"""Tests for action recognition and hand state transitions."""
import pytest
from datetime import datetime

from pokerlens.parser.action_recognizer import ActionRecognizer
from pokerlens.parser.hand_tracker import HandTracker
from pokerlens.parser.models import ActionType, Street, SeatInfo, Position


class TestActionRecognizer:
    """Tests for ActionRecognizer."""

    @pytest.fixture
    def recognizer(self):
        """Create recognizer instance."""
        return ActionRecognizer()

    def test_recognize_fold(self, recognizer):
        """Test fold action recognition."""
        assert recognizer.recognize_action("Folds") == ActionType.FOLD
        assert recognizer.recognize_action("FOLD") == ActionType.FOLD
        assert recognizer.recognize_action("Player folds") == ActionType.FOLD

    def test_recognize_call(self, recognizer):
        """Test call action recognition."""
        assert recognizer.recognize_action("Calls") == ActionType.CALL
        assert recognizer.recognize_action("calls $10") == ActionType.CALL

    def test_recognize_raise(self, recognizer):
        """Test raise action recognition."""
        assert recognizer.recognize_action("Raises") == ActionType.RAISE
        assert recognizer.recognize_action("Re-raises to $50") == ActionType.RAISE

    def test_recognize_all_in(self, recognizer):
        """Test all-in recognition."""
        assert recognizer.recognize_action("All-in") == ActionType.ALL_IN
        assert recognizer.recognize_action("allin") == ActionType.ALL_IN

    def test_parse_amount(self, recognizer):
        """Test amount parsing."""
        assert recognizer.parse_amount("$10.50") == 10.5
        assert recognizer.parse_amount("Raises $25") == 25.0
        assert recognizer.parse_amount("150") == 150.0
        assert recognizer.parse_amount("") == 0.0

    def test_parse_action_with_amount(self, recognizer):
        """Test combined action and amount parsing."""
        action, amount = recognizer.parse_action_with_amount("Raises $15.50")
        assert action == ActionType.RAISE
        assert amount == 15.5

    def test_is_voluntary(self, recognizer):
        """Test voluntary action detection."""
        assert recognizer.is_voluntary_action(ActionType.CALL) is True
        assert recognizer.is_voluntary_action(ActionType.POST_BLIND) is False

    def test_normalize_text(self, recognizer):
        """Test text normalization."""
        assert "Fold" in recognizer.normalize_action_text("  Foid  ")
        assert "Call" in recognizer.normalize_action_text("Cail")


class TestHandTracker:
    """Tests for HandTracker."""

    @pytest.fixture
    def tracker(self):
        """Create tracker instance."""
        return HandTracker()

    @pytest.fixture
    def sample_seats(self):
        """Create sample seat data."""
        return {
            0: SeatInfo(0, "Player1", 100.0, True, True),
            1: SeatInfo(1, "Player2", 100.0, True, True),
        }

    def test_start_new_hand(self, tracker, sample_seats):
        """Test starting a new hand."""
        hand = tracker.start_new_hand(0, sample_seats)
        assert hand is not None
        assert hand.current_street == Street.PREFLOP
        assert hand.hand_number == 1

    def test_detect_new_hand_dealer_change(self, tracker, sample_seats):
        """Test new hand detection via dealer button change."""
        tracker.start_new_hand(0, sample_seats)
        assert tracker.detect_new_hand(1, 10.0, [], sample_seats) is True

    def test_detect_street_change(self, tracker, sample_seats):
        """Test street change detection."""
        tracker.start_new_hand(0, sample_seats)
        
        new_street = tracker.detect_street_change(["Ah", "Kd", "Qc"])
        assert new_street == Street.FLOP

        new_street = tracker.detect_street_change(["Ah", "Kd", "Qc", "Js"])
        assert new_street == Street.TURN

    def test_update_hand_state(self, tracker, sample_seats):
        """Test hand state updates."""
        tracker.start_new_hand(0, sample_seats)
        tracker.update_hand_state(20.0, ["Ah", "Kd", "Qc"], sample_seats)
        
        assert tracker.current_hand.pot_size == 20.0
        assert len(tracker.current_hand.community_cards) == 3

    def test_end_hand(self, tracker, sample_seats):
        """Test ending a hand."""
        tracker.start_new_hand(0, sample_seats)
        tracker.end_current_hand()
        assert tracker.current_hand.is_complete is True

    def test_reset(self, tracker, sample_seats):
        """Test tracker reset."""
        tracker.start_new_hand(0, sample_seats)
        tracker.reset()
        assert tracker.current_hand is None
