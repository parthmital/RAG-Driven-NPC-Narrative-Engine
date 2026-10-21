"""Append-only SQLite event store."""

from __future__ import annotations
import json
import sqlite3
import logging
from pathlib import Path
from typing import List, Optional

from schemas.events import Event, EventType

log = logging.getLogger(__name__)


class EventStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_db(self) -> None:
        conn = self._connect()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                turn       INTEGER NOT NULL,
                event_type TEXT    NOT NULL,
                payload    TEXT    NOT NULL,
                timestamp  REAL    NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_turn ON events(turn)")
        conn.commit()
        log.debug("event store opened", extra={"path": str(self.db_path)})

    def append(self, event: Event) -> int:
        """Persist event; returns assigned row id."""
        self.append_many([event])
        return event.id

    def append_many(self, events: List[Event]) -> None:
        """Persist events in one transaction, so a crash keeps all or none."""
        conn = self._connect()
        with conn:
            for event in events:
                cur = conn.execute(
                    "INSERT INTO events (turn, event_type, payload, timestamp) VALUES (?, ?, ?, ?)",
                    (
                        event.turn,
                        event.event_type.value,
                        json.dumps(event.payload, ensure_ascii=False),
                        event.timestamp,
                    ),
                )
                event.id = cur.lastrowid
        for event in events:
            log.debug(
                "event appended",
                extra={
                    "event_id": event.id,
                    "type": event.event_type,
                    "turn": event.turn,
                },
            )

    def truncate_after(self, event_id: int) -> int:
        """Delete events logged after event_id; returns how many were removed."""
        conn = self._connect()
        with conn:
            cur = conn.execute("DELETE FROM events WHERE id > ?", (event_id,))
        return cur.rowcount

    def get_last_id(self) -> int:
        """Returns the ID of the most recent event, or 0 if empty."""
        conn = self._connect()
        row = conn.execute("SELECT MAX(id) as max_id FROM events").fetchone()
        return row["max_id"] or 0

    def load_all(self) -> List[Event]:
        """Replay full event log in order."""
        return self._load("", ())

    def load_after(self, event_id: int) -> List[Event]:
        """Events logged after event_id, in order."""
        return self._load("WHERE id > ?", (event_id,))

    def _load(self, where: str, params: tuple) -> List[Event]:
        conn = self._connect()
        rows = conn.execute(
            f"SELECT id, turn, event_type, payload, timestamp FROM events {where} ORDER BY id",
            params,
        ).fetchall()
        events = []
        for row in rows:
            try:
                e = Event(
                    id=row["id"],
                    turn=row["turn"],
                    event_type=EventType(row["event_type"]),
                    payload=json.loads(row["payload"]),
                    timestamp=row["timestamp"],
                )
                events.append(e)
            except Exception as exc:
                log.warning(
                    "corrupt event skipped",
                    extra={"event_id": row["id"], "error": str(exc)},
                )
        return events

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
