"""Durable queue. Idempotency key = content_id|platform|account. States follow the owner's social media policy."""
import json
import sqlite3
import time
from contextlib import contextmanager

from . import config

STATES = {"draft", "needs_review", "approved", "queued", "uploading", "scheduled_remote", "published_verified",
          "retry_wait", "blocked", "failed", "manual_pending", "manual_published", "expired", "private_verified"}
FINAL = {"published_verified", "manual_published", "failed", "expired", "private_verified"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
  key TEXT PRIMARY KEY, content_id TEXT NOT NULL, platform TEXT NOT NULL, account TEXT NOT NULL,
  state TEXT NOT NULL, title TEXT, caption TEXT, caption_version TEXT, asset_path TEXT, asset_sha256 TEXT,
  scheduled_utc TEXT, local_time TEXT, approved_by TEXT, approved_at TEXT, attempts INTEGER NOT NULL DEFAULT 0,
  next_attempt REAL NOT NULL DEFAULT 0, remote_id TEXT, permalink TEXT, published_at TEXT, request_id TEXT,
  last_error TEXT, manifest TEXT, updated_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, at REAL NOT NULL, key TEXT, event TEXT NOT NULL, detail TEXT);
"""


@contextmanager
def connect(path=None):
    path = path or config.db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30)
    db.row_factory = sqlite3.Row
    try:
        with db:
            db.executescript(SCHEMA)
            yield db
    finally:
        db.close()


def key_for(content_id, platform, account):
    return f"{content_id}|{platform}|{account}"


def log(db, key, event, detail=None):
    db.execute("INSERT INTO events (at,key,event,detail) VALUES (?,?,?,?)",
               (time.time(), key, event, json.dumps(detail)[:2000] if detail is not None else None))


def get(db, key):
    return db.execute("SELECT * FROM items WHERE key=?", (key,)).fetchone()


def upsert_new(db, row):
    """Insert a new item; never overwrite an existing one (idempotent sync)."""
    if get(db, row["key"]):
        return False
    cols = ",".join(row) + ",updated_at"
    db.execute(f"INSERT INTO items ({cols}) VALUES ({','.join('?' * (len(row) + 1))})", (*row.values(), time.time()))
    log(db, row["key"], "created", {"state": row["state"]})
    return True


def update(db, key, **fields):
    assert "state" not in fields or fields["state"] in STATES, fields.get("state")
    fields["updated_at"] = time.time()
    db.execute(f"UPDATE items SET {','.join(f'{k}=?' for k in fields)} WHERE key=?", (*fields.values(), key))
    log(db, key, "update", {k: v for k, v in fields.items() if k not in ("updated_at", "caption")})


def published_elsewhere(db, content_id, platform):
    """True if this content is already live (or manually posted) on this platform under any account."""
    return bool(db.execute("SELECT 1 FROM items WHERE content_id=? AND platform=? AND state IN "
                           "('published_verified','manual_published','manual_pending','scheduled_remote','uploading')", (content_id, platform)).fetchone())
