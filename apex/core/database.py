"""SQLite persistence layer for APEX conversations, messages, and settings."""

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional
import sqlite3
import uuid
from apex.core.config import config
from apex.core.logging import logger


def _get_utc_now() -> str:
    """Return ISO 8601 formatted UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


class Database:
    """Thread-safe SQLite database manager for local persistence."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.db_path
        self._init_db()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager that always closes the SQLite connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Create necessary database tables if they do not exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as conn:
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)

            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                );
            """)

            # Key-Value Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)

            # User-Approved Long-Term Memory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)

            # Performance indices
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conv 
                ON messages(conversation_id, timestamp);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conv_updated 
                ON conversations(updated_at DESC);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_cat 
                ON memories(category);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_updated 
                ON memories(updated_at DESC);
            """)
            conn.commit()
            logger.debug("Database initialized at %s", self.db_path)

    # -------------------------------------------------------------------------
    # Conversation Operations
    # -------------------------------------------------------------------------

    def create_conversation(self, title: str = "New Chat", conv_id: Optional[str] = None) -> str:
        """Create a new conversation session and return its ID."""
        conv_id = conv_id or str(uuid.uuid4())
        now = _get_utc_now()
        with self._connection() as conn:
            conn.execute(
                "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?);",
                (conv_id, title, now, now),
            )
            conn.commit()
        logger.info("Created conversation %s: '%s'", conv_id, title)
        return conv_id

    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all conversations ordered by most recently updated."""
        with self._connection() as conn:
            cursor = conn.execute(
                "SELECT id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC;"
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for a single conversation."""
        with self._connection() as conn:
            cursor = conn.execute(
                "SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?;",
                (conv_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_conversation_title(self, conv_id: str, new_title: str) -> None:
        """Update conversation title."""
        now = _get_utc_now()
        with self._connection() as conn:
            conn.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?;",
                (new_title, now, conv_id),
            )
            conn.commit()

    def delete_conversation(self, conv_id: str) -> None:
        """Delete a conversation and all its messages."""
        with self._connection() as conn:
            conn.execute("DELETE FROM conversations WHERE id = ?;", (conv_id,))
            conn.commit()
        logger.info("Deleted conversation %s", conv_id)

    # -------------------------------------------------------------------------
    # Message Operations
    # -------------------------------------------------------------------------

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        msg_id: Optional[str] = None
    ) -> str:
        """Add a message to a conversation."""
        msg_id = msg_id or str(uuid.uuid4())
        now = _get_utc_now()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO messages (id, conversation_id, role, content, timestamp)
                VALUES (?, ?, ?, ?, ?);
                """,
                (msg_id, conversation_id, role, content, now),
            )
            conn.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?;",
                (now, conversation_id),
            )
            conn.commit()
        return msg_id

    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Retrieve all messages for a conversation ordered chronologically."""
        with self._connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, conversation_id, role, content, timestamp
                FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC;
                """,
                (conversation_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    # -------------------------------------------------------------------------
    # Settings Operations
    # -------------------------------------------------------------------------

    def set_setting(self, key: str, value: str) -> None:
        """Upsert a key-value setting."""
        now = _get_utc_now()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at;
                """,
                (key, value, now),
            )
            conn.commit()

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve a setting value by key."""
        with self._connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM settings WHERE key = ?;",
                (key,),
            )
            row = cursor.fetchone()
            return row["value"] if row else default

    # -------------------------------------------------------------------------
    # Long-Term Memory Operations
    # -------------------------------------------------------------------------

    def add_memory(
        self,
        content: str,
        category: str = "general",
        source: str = "user_explicit",
        memory_id: Optional[str] = None,
    ) -> str:
        """Add a user-approved piece of information to long-term memory."""
        memory_id = memory_id or str(uuid.uuid4())
        now = _get_utc_now()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO memories (id, category, content, source, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (memory_id, category.lower(), content.strip(), source, now, now),
            )
            conn.commit()
        logger.info("Added memory %s [%s]: '%s'", memory_id, category, content[:40])
        return memory_id

    def list_memories(
        self,
        search_query: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List long-term memories with optional search and category filters."""
        sql = "SELECT id, category, content, source, created_at, updated_at FROM memories WHERE 1=1"
        params = []

        if category and category.lower() != "all":
            sql += " AND category = ?"
            params.append(category.lower())

        if search_query and search_query.strip():
            sql += " AND content LIKE ?"
            params.append(f"%{search_query.strip()}%")

        sql += " ORDER BY updated_at DESC;"

        with self._connection() as conn:
            cursor = conn.execute(sql, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single memory record by ID."""
        with self._connection() as conn:
            cursor = conn.execute(
                "SELECT id, category, content, source, created_at, updated_at FROM memories WHERE id = ?;",
                (memory_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_memory(
        self,
        memory_id: str,
        new_content: str,
        new_category: Optional[str] = None,
    ) -> bool:
        """Update the content or category of a memory."""
        now = _get_utc_now()
        with self._connection() as conn:
            if new_category:
                res = conn.execute(
                    "UPDATE memories SET content = ?, category = ?, updated_at = ? WHERE id = ?;",
                    (new_content.strip(), new_category.lower(), now, memory_id),
                )
            else:
                res = conn.execute(
                    "UPDATE memories SET content = ?, updated_at = ? WHERE id = ?;",
                    (new_content.strip(), now, memory_id),
                )
            conn.commit()
            return res.rowcount > 0

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a single memory record."""
        with self._connection() as conn:
            res = conn.execute("DELETE FROM memories WHERE id = ?;", (memory_id,))
            conn.commit()
            logger.info("Deleted memory %s", memory_id)
            return res.rowcount > 0

    def clear_all_memories(self) -> int:
        """Wipe all stored long-term memories permanently."""
        with self._connection() as conn:
            res = conn.execute("DELETE FROM memories;")
            conn.commit()
            logger.warning("All long-term memories have been cleared (%s deleted)", res.rowcount)
            return res.rowcount


# Global database instance
db = Database()
