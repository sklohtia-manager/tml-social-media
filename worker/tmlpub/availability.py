"""Content availability check after each publishing deadline, with an owner-approved educational fallback.

Claude cloud routines create the daily editions; if a routine cannot run (for example the shared usage limit), nothing
else would notice. Ten minutes after each deadline this checks the Facebook Page and Instagram for the edition. Missing →
alert the owner, and, only for series the owner enabled in TMLPUB_FALLBACK_SERIES, publish the next approved evergreen
education post (clearly labelled education, never news) to Facebook and Instagram. X stays with Buffer and is reported.
"""
import json
import os
from datetime import datetime, time as dtime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from . import config, store
from .adapters import AuthProblem
from .http import HttpError

MEL = ZoneInfo(config.TIMEZONE)
SERIES = {  # deadline (local), marker that identifies the edition in captions
    "morning": (dtime(9, 30), "#TheLedgerMorning", "THE LEDGER MORNING"),
    "ready": (dtime(15, 15), "#AreYouFinanciallyReady", "ARE YOU FINANCIALLY READY"),
    "evening": (dtime(19, 30), "#TheLedgerEvening", "THE LEDGER EVENING"),
}
CHECK_DELAY = timedelta(minutes=10)
CHECK_WINDOW = timedelta(minutes=40)   # after this, the slot is recorded as missed without any fallback
FALLBACK_SERIES = set(filter(None, os.environ.get("TMLPUB_FALLBACK_SERIES", "").split(",")))
EVERGREEN_REUSE_DAYS = 30

SCHEMA = """CREATE TABLE IF NOT EXISTS availability (date TEXT, series TEXT, outcome TEXT, detail TEXT, at REAL,
            PRIMARY KEY(date, series));
            CREATE TABLE IF NOT EXISTS evergreen_use (item TEXT, date TEXT, platform TEXT, remote_id TEXT, PRIMARY KEY(item, date, platform));"""


def _found(captions, marker, label):
    return any(marker.lower() in c.lower() or label.lower() in c.lower() for c in captions)


def next_evergreen(db, repo, series, today):
    used_recent = {r[0] for r in db.execute("SELECT item FROM evergreen_use WHERE date>=?",
                                            ((today - timedelta(days=EVERGREEN_REUSE_DAYS)).isoformat(),))}
    for path in sorted((repo / "content" / "evergreen" / series).glob("*.json")):
        doc = json.loads(path.read_text())
        if doc.get("approval", {}).get("owner") is True and doc["id"] not in used_recent:
            return doc
    return None


def check(db, repo, meta, now=None, alert=None):
    db.executescript(SCHEMA)
    now = (now or datetime.now(timezone.utc)).astimezone(MEL)
    today = now.date()
    results = {}
    for series, (deadline, marker, label) in SERIES.items():
        due = datetime.combine(today, deadline, MEL)
        if not (due + CHECK_DELAY <= now <= due + CHECK_WINDOW):
            continue
        if db.execute("SELECT 1 FROM availability WHERE date=? AND series=?", (today.isoformat(), series)).fetchone():
            continue
        if meta is None:
            results[series] = "unchecked (Meta credentials not configured)"
            continue
        try:
            caps = meta.recent_captions(datetime.combine(today, dtime(0, 0), MEL).timestamp())
        except (HttpError, AuthProblem) as e:
            results[series] = f"check failed: {e}"
            alert(f"TML availability: could not check the {series} edition ({e}).")
            continue
        present = {p: _found(c, marker, label) for p, c in caps.items()}
        if all(present.values()):
            outcome, detail = "published", present
        else:
            missing = [p for p, ok in present.items() if not ok]
            outcome, detail = "missed", {"missing": missing}
            msg = f"TML availability: the {series} edition due {deadline.strftime('%H:%M')} is not on {', '.join(missing)}."
            if series in FALLBACK_SERIES:
                item = next_evergreen(db, repo, series, today)
                if item and not config.DRY_RUN and {"facebook_image", "instagram_image"} & config.ENABLED_PLATFORMS:
                    done = {}
                    for platform in missing:
                        if f"{platform}_image" not in config.ENABLED_PLATFORMS:
                            continue
                        r = meta.publish_image(platform, item["imageUrl"], item["captions"][platform])
                        db.execute("INSERT OR IGNORE INTO evergreen_use VALUES (?,?,?,?)", (item["id"], today.isoformat(), platform, r["remote_id"]))
                        done[platform] = r["remote_id"]
                    outcome, detail = "fallback_published", {"missing": missing, "evergreen": item["id"], "posted": done,
                                                             "x": "not covered (Buffer only); post manually if wanted"}
                    msg += f" Published approved education fallback {item['id']} to {', '.join(done) or 'none'}."
                elif item:
                    outcome, detail = "missed_fallback_dry_run", {"missing": missing, "would_publish": item["id"]}
                    msg += f" (Dry run: would publish approved education fallback {item['id']}.)"
                else:
                    msg += " No approved education fallback is available."
            alert(msg)
        db.execute("INSERT INTO availability VALUES (?,?,?,?,strftime('%s','now'))", (today.isoformat(), series, outcome, json.dumps(detail)))
        results[series] = outcome
    return results
