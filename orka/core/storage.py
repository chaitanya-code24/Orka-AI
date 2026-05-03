import json
import sqlite3
from pathlib import Path
from threading import Lock
from typing import Any


class SQLiteStorage:
    def __init__(self, db_path: str):
        self.db_path = str(db_path)
        self._lock = Lock()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._lock, self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS customers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    city TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipient TEXT NOT NULL,
                    message TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def save_run(self, run_id: str, payload: dict[str, Any]) -> None:
        serialized = json.dumps(payload)
        created_at = str(payload.get("timestamp", ""))
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO runs (run_id, payload, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET payload=excluded.payload, created_at=excluded.created_at
                """,
                (run_id, serialized, created_at),
            )

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT payload FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            return None
        return json.loads(row["payload"])

    def list_runs(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT payload FROM runs ORDER BY created_at DESC").fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def create_customer(self, customer: dict[str, Any], created_at: str) -> None:
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO customers (id, name, city, status, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    customer["id"],
                    customer["name"],
                    customer["city"],
                    customer["status"],
                    created_at,
                ),
            )

    def list_customers(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, name, city, status, created_at FROM customers ORDER BY created_at ASC"
            ).fetchall()
        return [dict(row) for row in rows]

    def create_email(self, email: dict[str, Any], created_at: str) -> None:
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO emails (recipient, message, status, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    email["to"],
                    email["message"],
                    email["status"],
                    created_at,
                ),
            )

    def list_emails(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT recipient, message, status, created_at FROM emails ORDER BY created_at ASC"
            ).fetchall()
        return [dict(row) for row in rows]

    def reset(self) -> None:
        with self._lock, self._connect() as connection:
            connection.execute("DELETE FROM runs")
            connection.execute("DELETE FROM customers")
            connection.execute("DELETE FROM emails")


_default_storage: SQLiteStorage | None = None


def get_default_storage(db_path: str | None = None) -> SQLiteStorage:
    global _default_storage

    if _default_storage is None:
        if db_path is None:
            db_path = str(Path("orka.db"))
        _default_storage = SQLiteStorage(db_path)
    elif db_path is not None and _default_storage.db_path != str(db_path):
        _default_storage = SQLiteStorage(db_path)

    return _default_storage


def set_default_storage(storage: SQLiteStorage) -> None:
    global _default_storage
    _default_storage = storage
