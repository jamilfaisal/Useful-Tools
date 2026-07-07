"""SQLite-backed cache for Hacker News items."""

from __future__ import annotations

import json
from contextlib import contextmanager
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


DEFAULT_CACHE_DB_PATH = Path("output") / "cache.db"


def _normalize_db_path(db_path: Optional[str | Path]) -> Path:
    return Path(db_path) if db_path is not None else DEFAULT_CACHE_DB_PATH


def _get_connection(db_path: Optional[str | Path] = None) -> sqlite3.Connection:
    normalized_path = _normalize_db_path(db_path)
    normalized_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(normalized_path)


@contextmanager
def _connection(db_path: Optional[str | Path] = None):
    connection = _get_connection(db_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                raw_json TEXT NOT NULL,
                downloaded_at TEXT NOT NULL
            )
            """
        )
        connection.commit()
        yield connection
    finally:
        connection.close()


def get_item(item_id: int, db_path: Optional[str | Path] = None) -> Optional[dict[str, Any]]:
    """Return a cached Hacker News item as raw JSON data."""
    with _connection(db_path) as connection:
        cursor = connection.execute("SELECT raw_json FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()

    if not row:
        return None

    return json.loads(row[0])


def save_item(item: dict[str, Any], db_path: Optional[str | Path] = None) -> None:
    """Persist a raw Hacker News item JSON document."""
    if "id" not in item:
        raise KeyError("item must include an 'id' field")

    downloaded_at = datetime.now(timezone.utc).isoformat()
    with _connection(db_path) as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO items (id, raw_json, downloaded_at)
            VALUES (?, ?, ?)
            """,
            (item["id"], json.dumps(item), downloaded_at),
        )
        connection.commit()


def has_item(item_id: int, db_path: Optional[str | Path] = None) -> bool:
    """Return whether a Hacker News item exists in the local cache."""
    with _connection(db_path) as connection:
        cursor = connection.execute("SELECT 1 FROM items WHERE id = ?", (item_id,))
        return cursor.fetchone() is not None


class SQLiteCache:
    """Compatibility wrapper around the module-level cache helpers."""

    def __init__(self, db_path: str | Path = DEFAULT_CACHE_DB_PATH):
        self.db_path = db_path

    def get_item(self, item_id: int) -> Optional[dict[str, Any]]:
        return get_item(item_id, self.db_path)

    def save_item(self, item: dict[str, Any]) -> None:
        save_item(item, self.db_path)

    def has_item(self, item_id: int) -> bool:
        return has_item(item_id, self.db_path)
