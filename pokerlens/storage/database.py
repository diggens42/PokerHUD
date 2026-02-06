"""SQLite database management for player stats and hand history."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional

import config


class Database:
    """SQLite database interface for PokerHUD."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file. Uses default if None.
        """
        self.db_path = db_path or config.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection context manager."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT DEFAULT ''
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP,
                    table_name TEXT,
                    stakes TEXT,
                    table_size INTEGER
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER REFERENCES sessions(id),
                    hand_number INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    board_cards TEXT,
                    pot_size REAL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hand_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hand_id INTEGER REFERENCES hands(id),
                    player_id INTEGER REFERENCES players(id),
                    seat_number INTEGER,
                    street TEXT CHECK(street IN ('preflop', 'flop', 'turn', 'river')),
                    action TEXT CHECK(action IN ('fold', 'check', 'call', 'bet', 'raise', 'all-in', 'post_blind')),
                    amount REAL DEFAULT 0,
                    is_voluntary INTEGER DEFAULT 0,
                    sequence_order INTEGER
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_stats_cache (
                    player_id INTEGER PRIMARY KEY REFERENCES players(id),
                    total_hands INTEGER DEFAULT 0,
                    vpip_hands INTEGER DEFAULT 0,
                    pfr_hands INTEGER DEFAULT 0,
                    postflop_bets INTEGER DEFAULT 0,
                    postflop_raises INTEGER DEFAULT 0,
                    postflop_calls INTEGER DEFAULT 0,
                    three_bet_opportunities INTEGER DEFAULT 0,
                    three_bet_made INTEGER DEFAULT 0,
                    fold_to_cbet_opportunities INTEGER DEFAULT 0,
                    fold_to_cbet_made INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_hand_actions_player ON hand_actions(player_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_hand_actions_hand ON hand_actions(hand_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_username ON players(username)")

    def get_or_create_player(self, username: str) -> int:
        """
        Get player ID or create new player.

        Args:
            username: Player username.

        Returns:
            Player ID.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM players WHERE username = ?", (username,))
            row = cursor.fetchone()
            
            if row:
                cursor.execute(
                    "UPDATE players SET last_seen = CURRENT_TIMESTAMP WHERE id = ?",
                    (row["id"],)
                )
                return row["id"]
            
            cursor.execute(
                "INSERT INTO players (username) VALUES (?)",
                (username,)
            )
            return cursor.lastrowid

    def get_player_by_id(self, player_id: int) -> Optional[dict]:
        """
        Get player by ID.

        Args:
            player_id: Player ID.

        Returns:
            Player dict or None.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_player_by_username(self, username: str) -> Optional[dict]:
        """
        Get player by username.

        Args:
            username: Player username.

        Returns:
            Player dict or None.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM players WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_player_notes(self, player_id: int, notes: str) -> None:
        """
        Update player notes.

        Args:
            player_id: Player ID.
            notes: Note text.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE players SET notes = ? WHERE id = ?",
                (notes, player_id)
            )

    def create_session(self, table_name: str, stakes: str, table_size: int) -> int:
        """
        Create new session.

        Args:
            table_name: Table name/identifier.
            stakes: Stakes description.
            table_size: Number of seats.

        Returns:
            Session ID.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (table_name, stakes, table_size) VALUES (?, ?, ?)",
                (table_name, stakes, table_size)
            )
            return cursor.lastrowid

    def end_session(self, session_id: int) -> None:
        """
        End session.

        Args:
            session_id: Session ID.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE sessions SET ended_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,)
            )

    def get_active_sessions(self) -> list[dict]:
        """
        Get all active sessions.

        Returns:
            List of session dicts.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE ended_at IS NULL")
            return [dict(row) for row in cursor.fetchall()]

    def create_hand(self, session_id: int, hand_number: int, board_cards: str, pot_size: float) -> int:
        """
        Create new hand record.

        Args:
            session_id: Session ID.
            hand_number: Hand number.
            board_cards: JSON string of board cards.
            pot_size: Final pot size.

        Returns:
            Hand ID.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO hands (session_id, hand_number, board_cards, pot_size) VALUES (?, ?, ?, ?)",
                (session_id, hand_number, board_cards, pot_size)
            )
            return cursor.lastrowid

    def add_hand_action(
        self,
        hand_id: int,
        player_id: int,
        seat_number: int,
        street: str,
        action: str,
        amount: float,
        is_voluntary: bool,
        sequence_order: int,
    ) -> int:
        """
        Add action to hand.

        Args:
            hand_id: Hand ID.
            player_id: Player ID.
            seat_number: Seat number.
            street: Street name.
            action: Action type.
            amount: Bet/raise amount.
            is_voluntary: Whether action is voluntary.
            sequence_order: Action sequence number.

        Returns:
            Action ID.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO hand_actions 
                (hand_id, player_id, seat_number, street, action, amount, is_voluntary, sequence_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (hand_id, player_id, seat_number, street, action, amount, int(is_voluntary), sequence_order)
            )
            return cursor.lastrowid

    def add_hand_actions_batch(self, actions: list[tuple]) -> None:
        """
        Add multiple actions efficiently.

        Args:
            actions: List of action tuples (hand_id, player_id, seat_number, street, action, amount, is_voluntary, sequence_order).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                """
                INSERT INTO hand_actions 
                (hand_id, player_id, seat_number, street, action, amount, is_voluntary, sequence_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                actions
            )

    def get_hand_actions(self, hand_id: int) -> list[dict]:
        """
        Get all actions for a hand.

        Args:
            hand_id: Hand ID.

        Returns:
            List of action dicts.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM hand_actions WHERE hand_id = ? ORDER BY sequence_order",
                (hand_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_player_hands(self, player_id: int, limit: Optional[int] = None) -> list[dict]:
        """
        Get hands involving a player.

        Args:
            player_id: Player ID.
            limit: Maximum number of hands to return.

        Returns:
            List of hand dicts.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT DISTINCT h.* FROM hands h
                JOIN hand_actions ha ON h.id = ha.hand_id
                WHERE ha.player_id = ?
                ORDER BY h.timestamp DESC
            """
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (player_id,))
            return [dict(row) for row in cursor.fetchall()]
