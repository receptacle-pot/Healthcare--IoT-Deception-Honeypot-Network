from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .analytics import risk_score
from .geo import enrich_ip

class EventStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "honeypot.db"
        self.jsonl_path = self.data_dir / "events.jsonl"
        self.lock = threading.RLock()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        with self.lock:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    service TEXT NOT NULL,
                    src_ip TEXT NOT NULL,
                    src_port INTEGER,
                    username TEXT,
                    password TEXT,
                    command TEXT,
                    payload TEXT,
                    method TEXT,
                    path TEXT,
                    user_agent TEXT,
                    raw TEXT,
                    risk_score INTEGER NOT NULL,
                    geo_country TEXT,
                    geo_city TEXT,
                    geo_latitude REAL,
                    geo_longitude REAL,
                    network_type TEXT
                )
                """
            )
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_events_src_ip ON events(src_ip)")
            self.conn.commit()

    def add_event(
        self,
        *,
        event_type: str,
        service: str,
        src_ip: str,
        src_port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        command: str | None = None,
        payload: str | None = None,
        method: str | None = None,
        path: str | None = None,
        user_agent: str | None = None,
        raw: dict[str, Any] | str | None = None,
    ) -> dict[str, Any]:
        ts = datetime.now(timezone.utc).isoformat()
        geo = enrich_ip(src_ip)
        score = risk_score(event_type, command, payload)
        raw_text = json.dumps(raw, sort_keys=True) if isinstance(raw, dict) else raw

        with self.lock:
            cursor = self.conn.execute(
                """
                INSERT INTO events (
                    ts, event_type, service, src_ip, src_port, username, password,
                    command, payload, method, path, user_agent, raw, risk_score,
                    geo_country, geo_city, geo_latitude, geo_longitude, network_type
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ts,
                    event_type,
                    service,
                    src_ip,
                    src_port,
                    username,
                    password,
                    command,
                    payload,
                    method,
                    path,
                    user_agent,
                    raw_text,
                    score,
                    geo.country,
                    geo.city,
                    geo.latitude,
                    geo.longitude,
                    geo.network_type,
                ),
            )
            self.conn.commit()
            event = self.get_event(cursor.lastrowid)
            with self.jsonl_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, sort_keys=True) + "\n")
            return event

    def get_event(self, event_id: int) -> dict[str, Any]:
        with self.lock:
            row = self.conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
        if row is None:
            raise KeyError(event_id)
        return dict(row)

    def list_events(self, *, limit: int = 200, after_id: int | None = None) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 1000))
        with self.lock:
            if after_id is None:
                rows = self.conn.execute(
                    "SELECT * FROM events ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
                return [dict(row) for row in reversed(rows)]
            rows = self.conn.execute(
                "SELECT * FROM events WHERE id > ? ORDER BY id ASC LIMIT ?",
                (after_id, limit),
            ).fetchall()
            return [dict(row) for row in rows]

    def close(self) -> None:
        with self.lock:
            self.conn.close()
