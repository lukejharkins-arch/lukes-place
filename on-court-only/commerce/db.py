"""SQLite access shared by every agent, the API and the reports."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from commerce.config import DB_PATH, SCHEMA_PATH


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def connect(path=None) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path or DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text())
    conn.commit()


@contextmanager
def tx(conn: sqlite3.Connection):
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def rows(conn, sql, params=()):
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def one(conn, sql, params=()):
    r = conn.execute(sql, params).fetchone()
    return dict(r) if r else None


def audit(conn, actor, action, entity_type=None, entity_id=None, detail=None):
    conn.execute(
        "INSERT INTO audit_log(actor, action, entity_type, entity_id, detail) VALUES (?,?,?,?,?)",
        (actor, action, entity_type, entity_id, json.dumps(detail) if isinstance(detail, (dict, list)) else detail),
    )


def jload(value, default=None):
    if value in (None, ""):
        return [] if default is None else default
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return [] if default is None else default
