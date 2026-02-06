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

    def get_player_stats_cache(self, player_id: int) -> Optional[dict]:
        """
        Get cached stats for player.

        Args:
            player_id: Player ID.

        Returns:
            Stats dict or None.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM player_stats_cache WHERE player_id = ?", (player_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_player_stats_cache(
        self,
        player_id: int,
        total_hands: int = 0,
        vpip_hands: int = 0,
        pfr_hands: int = 0,
        postflop_bets: int = 0,
        postflop_raises: int = 0,
        postflop_calls: int = 0,
        three_bet_opportunities: int = 0,
        three_bet_made: int = 0,
        fold_to_cbet_opportunities: int = 0,
        fold_to_cbet_made: int = 0,
    ) -> None:
        """
        Update cached stats for player.

        Args:
            player_id: Player ID.
            total_hands: Total hands count.
            vpip_hands: VPIP hands count.
            pfr_hands: PFR hands count.
            postflop_bets: Postflop bet count.
            postflop_raises: Postflop raise count.
            postflop_calls: Postflop call count.
            three_bet_opportunities: 3-bet opportunity count.
            three_bet_made: 3-bet made count.
            fold_to_cbet_opportunities: Fold to cbet opportunity count.
            fold_to_cbet_made: Fold to cbet made count.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO player_stats_cache 
                (player_id, total_hands, vpip_hands, pfr_hands, postflop_bets, postflop_raises, 
                 postflop_calls, three_bet_opportunities, three_bet_made, 
                 fold_to_cbet_opportunities, fold_to_cbet_made, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(player_id) DO UPDATE SET
                    total_hands = total_hands + excluded.total_hands,
                    vpip_hands = vpip_hands + excluded.vpip_hands,
                    pfr_hands = pfr_hands + excluded.pfr_hands,
                    postflop_bets = postflop_bets + excluded.postflop_bets,
                    postflop_raises = postflop_raises + excluded.postflop_raises,
                    postflop_calls = postflop_calls + excluded.postflop_calls,
                    three_bet_opportunities = three_bet_opportunities + excluded.three_bet_opportunities,
                    three_bet_made = three_bet_made + excluded.three_bet_made,
                    fold_to_cbet_opportunities = fold_to_cbet_opportunities + excluded.fold_to_cbet_opportunities,
                    fold_to_cbet_made = fold_to_cbet_made + excluded.fold_to_cbet_made,
                    last_updated = CURRENT_TIMESTAMP
                """,
                (player_id, total_hands, vpip_hands, pfr_hands, postflop_bets, postflop_raises,
                 postflop_calls, three_bet_opportunities, three_bet_made,
                 fold_to_cbet_opportunities, fold_to_cbet_made)
            )

    def rebuild_stats_cache(self) -> None:
        """Rebuild all cached stats from scratch."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM player_stats_cache")
            
            cursor.execute("SELECT id FROM players")
            player_ids = [row["id"] for row in cursor.fetchall()]
            
            for player_id in player_ids:
                stats = self._calculate_raw_stats(player_id, cursor)
                if stats["total_hands"] > 0:
                    cursor.execute(
                        """
                        INSERT INTO player_stats_cache 
                        (player_id, total_hands, vpip_hands, pfr_hands, postflop_bets, postflop_raises,
                         postflop_calls, three_bet_opportunities, three_bet_made,
                         fold_to_cbet_opportunities, fold_to_cbet_made)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (player_id, stats["total_hands"], stats["vpip_hands"], stats["pfr_hands"],
                         stats["postflop_bets"], stats["postflop_raises"], stats["postflop_calls"],
                         stats["three_bet_opportunities"], stats["three_bet_made"],
                         stats["fold_to_cbet_opportunities"], stats["fold_to_cbet_made"])
                    )

    def _calculate_raw_stats(self, player_id: int, cursor) -> dict:
        """Calculate raw stat counts from actions."""
        cursor.execute(
            "SELECT COUNT(DISTINCT hand_id) FROM hand_actions WHERE player_id = ?",
            (player_id,)
        )
        total_hands = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(DISTINCT hand_id) FROM hand_actions
            WHERE player_id = ? AND street = 'preflop' AND is_voluntary = 1
            AND action IN ('call', 'bet', 'raise', 'all-in')
            """,
            (player_id,)
        )
        vpip_hands = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(DISTINCT hand_id) FROM hand_actions
            WHERE player_id = ? AND street = 'preflop' AND action IN ('raise', 'all-in')
            """,
            (player_id,)
        )
        pfr_hands = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*) FROM hand_actions
            WHERE player_id = ? AND street IN ('flop', 'turn', 'river') AND action = 'bet'
            """,
            (player_id,)
        )
        postflop_bets = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*) FROM hand_actions
            WHERE player_id = ? AND street IN ('flop', 'turn', 'river') AND action = 'raise'
            """,
            (player_id,)
        )
        postflop_raises = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*) FROM hand_actions
            WHERE player_id = ? AND street IN ('flop', 'turn', 'river') AND action = 'call'
            """,
            (player_id,)
        )
        postflop_calls = cursor.fetchone()[0]

        return {
            "total_hands": total_hands,
            "vpip_hands": vpip_hands,
            "pfr_hands": pfr_hands,
            "postflop_bets": postflop_bets,
            "postflop_raises": postflop_raises,
            "postflop_calls": postflop_calls,
            "three_bet_opportunities": 0,
            "three_bet_made": 0,
            "fold_to_cbet_opportunities": 0,
            "fold_to_cbet_made": 0,
        }
