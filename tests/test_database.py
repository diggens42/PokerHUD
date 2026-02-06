"""Tests for database functionality."""
import pytest
import tempfile
from pathlib import Path

from pokerlens.storage.database import Database
from pokerlens.storage.session import SessionManager


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    
    db = Database(db_path)
    yield db
    
    db_path.unlink()


class TestDatabase:
    """Tests for Database class."""

    def test_create_player(self, temp_db):
        """Test player creation."""
        player_id = temp_db.get_or_create_player("TestPlayer")
        assert player_id > 0
        
        player = temp_db.get_player_by_id(player_id)
        assert player["username"] == "TestPlayer"

    def test_get_or_create_player_idempotent(self, temp_db):
        """Test that get_or_create is idempotent."""
        id1 = temp_db.get_or_create_player("TestPlayer")
        id2 = temp_db.get_or_create_player("TestPlayer")
        assert id1 == id2

    def test_update_player_notes(self, temp_db):
        """Test updating player notes."""
        player_id = temp_db.get_or_create_player("TestPlayer")
        temp_db.update_player_notes(player_id, "Aggressive player")
        
        player = temp_db.get_player_by_id(player_id)
        assert player["notes"] == "Aggressive player"

    def test_create_session(self, temp_db):
        """Test session creation."""
        session_id = temp_db.create_session("Table 1", "NL $1/$2", 6)
        assert session_id > 0
        
        sessions = temp_db.get_active_sessions()
        assert len(sessions) == 1
        assert sessions[0]["table_name"] == "Table 1"

    def test_end_session(self, temp_db):
        """Test ending session."""
        session_id = temp_db.create_session("Table 1", "NL $1/$2", 6)
        temp_db.end_session(session_id)
        
        sessions = temp_db.get_active_sessions()
        assert len(sessions) == 0

    def test_create_hand(self, temp_db):
        """Test hand creation."""
        session_id = temp_db.create_session("Table 1", "NL $1/$2", 6)
        hand_id = temp_db.create_hand(session_id, 12345, '["Ah", "Kd", "Qc"]', 25.0)
        assert hand_id > 0

    def test_add_hand_action(self, temp_db):
        """Test adding hand action."""
        player_id = temp_db.get_or_create_player("TestPlayer")
        session_id = temp_db.create_session("Table 1", "NL $1/$2", 6)
        hand_id = temp_db.create_hand(session_id, 12345, "[]", 0.0)
        
        action_id = temp_db.add_hand_action(
            hand_id, player_id, 0, "preflop", "raise", 5.0, True, 1
        )
        assert action_id > 0
        
        actions = temp_db.get_hand_actions(hand_id)
        assert len(actions) == 1
        assert actions[0]["action"] == "raise"

    def test_batch_add_actions(self, temp_db):
        """Test batch action insertion."""
        player_id = temp_db.get_or_create_player("TestPlayer")
        session_id = temp_db.create_session("Table 1", "NL $1/$2", 6)
        hand_id = temp_db.create_hand(session_id, 12345, "[]", 0.0)
        
        actions = [
            (hand_id, player_id, 0, "preflop", "raise", 5.0, 1, 1),
            (hand_id, player_id, 0, "flop", "bet", 10.0, 1, 2),
        ]
        temp_db.add_hand_actions_batch(actions)
        
        retrieved = temp_db.get_hand_actions(hand_id)
        assert len(retrieved) == 2

    def test_stats_cache(self, temp_db):
        """Test stats caching."""
        player_id = temp_db.get_or_create_player("TestPlayer")
        
        temp_db.update_player_stats_cache(
            player_id,
            total_hands=10,
            vpip_hands=5,
            pfr_hands=3,
        )
        
        cache = temp_db.get_player_stats_cache(player_id)
        assert cache["total_hands"] == 10
        assert cache["vpip_hands"] == 5
        assert cache["pfr_hands"] == 3

    def test_rebuild_cache(self, temp_db):
        """Test cache rebuild."""
        player_id = temp_db.get_or_create_player("TestPlayer")
        session_id = temp_db.create_session("Table 1", "NL $1/$2", 6)
        hand_id = temp_db.create_hand(session_id, 12345, "[]", 0.0)
        
        temp_db.add_hand_action(hand_id, player_id, 0, "preflop", "raise", 5.0, True, 1)
        
        temp_db.rebuild_stats_cache()
        
        cache = temp_db.get_player_stats_cache(player_id)
        assert cache["total_hands"] > 0


class TestSessionManager:
    """Tests for SessionManager class."""

    def test_start_session(self, temp_db):
        """Test starting a session."""
        manager = SessionManager(temp_db)
        session_id = manager.start_session("Table 1", "NL $1/$2", 6)
        assert session_id > 0
        assert manager.is_session_active("Table 1")

    def test_end_session(self, temp_db):
        """Test ending a session."""
        manager = SessionManager(temp_db)
        manager.start_session("Table 1", "NL $1/$2", 6)
        manager.end_session("Table 1")
        assert not manager.is_session_active("Table 1")

    def test_get_session_id(self, temp_db):
        """Test retrieving session ID."""
        manager = SessionManager(temp_db)
        session_id = manager.start_session("Table 1", "NL $1/$2", 6)
        assert manager.get_session_id("Table 1") == session_id

    def test_end_all_sessions(self, temp_db):
        """Test ending all sessions."""
        manager = SessionManager(temp_db)
        manager.start_session("Table 1", "NL $1/$2", 6)
        manager.start_session("Table 2", "NL $2/$5", 9)
        
        manager.end_all_sessions()
        assert len(manager.get_active_tables()) == 0
