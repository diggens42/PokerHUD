"""Session lifecycle management."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pokerlens.storage.database import Database


class SessionManager:
    """Manages poker session lifecycle."""

    def __init__(self, database: Database):
        """
        Initialize session manager.

        Args:
            database: Database instance.
        """
        self.db = database
        self._active_sessions: dict[str, int] = {}

    def start_session(self, table_name: str, stakes: str = "Unknown", table_size: int = 6) -> int:
        """
        Start a new tracking session for a table.

        Args:
            table_name: Table identifier.
            stakes: Stakes description (e.g., "NL $0.50/$1.00").
            table_size: Number of seats at table.

        Returns:
            Session ID.
        """
        if table_name in self._active_sessions:
            return self._active_sessions[table_name]

        session_id = self.db.create_session(table_name, stakes, table_size)
        self._active_sessions[table_name] = session_id
        return session_id

    def end_session(self, table_name: str) -> None:
        """
        End a tracking session.

        Args:
            table_name: Table identifier.
        """
        if table_name not in self._active_sessions:
            return

        session_id = self._active_sessions[table_name]
        self.db.end_session(session_id)
        del self._active_sessions[table_name]

    def get_session_id(self, table_name: str) -> Optional[int]:
        """
        Get session ID for table.

        Args:
            table_name: Table identifier.

        Returns:
            Session ID or None if no active session.
        """
        return self._active_sessions.get(table_name)

    def is_session_active(self, table_name: str) -> bool:
        """
        Check if session is active for table.

        Args:
            table_name: Table identifier.

        Returns:
            True if session is active.
        """
        return table_name in self._active_sessions

    def end_all_sessions(self) -> None:
        """End all active sessions."""
        for table_name in list(self._active_sessions.keys()):
            self.end_session(table_name)

    def get_active_tables(self) -> list[str]:
        """
        Get list of tables with active sessions.

        Returns:
            List of table names.
        """
        return list(self._active_sessions.keys())

    def restore_sessions(self) -> None:
        """Restore active sessions from database."""
        active = self.db.get_active_sessions()
        for session in active:
            table_name = session["table_name"]
            if table_name:
                self._active_sessions[table_name] = session["id"]
