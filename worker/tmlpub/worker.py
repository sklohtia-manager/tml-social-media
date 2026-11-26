"""One worker cycle: sync approved manifests, publish due items, verify, retry within bounds, alert. Run by a systemd timer."""
import fcntl
import json
import random
import subprocess
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from . import config, manifest, store
from .adapters import AuthProblem, Uncertain
from .http import Http, HttpError

YOUTUBE_EARLY = timedelta(hours=6)   # YouTube uploads early as private with publishAt
LATE_LIMIT = timedelta(hours=2)      # never publish more than 2 h late without owner review


def now_utc():
    return datetime.now(timezone.utc)


def alert(text, sent=set()):
    """Owner alert through the approved command (never includes secrets). De-duplicated per process."""
    if text in sent:
        return
    sent.add(text)
    (config.STATE / "alerts.log").parent.mkdir(parents=True, exist_ok=True)
    with open(config.STATE / "alerts.log", "a") as f:
        f.write(f"{now_utc().isoformat()} {text}\n")
    if config.ALERT_COMMAND:
        subprocess.run(config.ALERT_COMMAND, shell=True, input=text.encode(), timeout=60, check=False)


def load_creds(name):
    path = config.SECRETS / f"{name}.json"
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def default_adapters(http=None):
    from .adapters.meta import Meta
    from .adapters.youtube import YouTube
    http = http or Http()
    yt, meta = load_creds("youtube"), load_creds("meta")
    return {"youtube": YouTube(http, yt) if yt else None, "meta": Meta(http, meta) if meta else None}


def sync(db, repo):
    created, problems = 0, []
    # Manual (already-posted) records load first, so they always block duplicates of the same content.
    for path, doc in sorted(manifest.load_all(repo), key=lambda pd: not pd[1].get("manual")):
        if "_error" in doc:
            problems.append(f"{path.name}: invalid JSON")
            continue
        try:
            rows, errors = manifest.validate(doc, repo)
        except Exception as e:  # one malformed manifest must never stop the queue; it is reported and skipped
            rows, errors = [], [f"malformed manifest ({type(e).__name__}: {e})"]
        problems += [f"{path.name}: {e}" for e in errors]
        for row in rows:
            if row["state"] == "approved" and store.published_elsewhere(db, row["content_id"], row["platform"]):
                store.log(db, row["key"], "skipped_duplicate", {"reason": "already published or manually posted"})
                continue
            created += store.upsert_new(db, row)
    return created, problems


def _publish(item, adapters):
    p = item["platform"]
    if p in ("youtube", "youtube_shorts"):
        return adapters["youtube"].upload(item, shorts=p == "youtube_shorts")
    if p == "instagram_reels":
        return adapters["meta"].instagram_reel(item)
    if p == "facebook_reels":
        return adapters["meta"].facebook_reel(item)
    raise ValueError(p)


def _verify(item, adapters):
    if item["platform"].startswith("youtube"):
        return adapters["youtube"].verify(item["remote_id"])
    return adapters["meta"].verify(item["remote_id"], item["platform"])


def _adapter_for(platform, adapters):
    return adapters.get("youtube" if platform.startswith("youtube") else "meta")


def process(db, item, adapters, now):
    key, p = item["key"], item["platform"]
    if config.pause_file(p).exists():
        return "paused"
    live = not config.DRY_RUN and p in config.ENABLED_PLATFORMS
    when = datetime.fromisoformat(item["scheduled_utc"]) if item["scheduled_utc"] else now
    state = item["state"]
    if state in ("approved", "retry_wait"):
        if time.time() < item["next_attempt"]:
            return "waiting"
        due = when - (YOUTUBE_EARLY if p.startswith("youtube") else timedelta(0))
        if now < due:
            return "not_due"
        if now > when + LATE_LIMIT:
            store.update(db, key, state="needs_review", last_error="missed its publishing window; owner to reschedule")
            alert(f"TML publisher: {key} missed its window and was NOT published late. Reschedule it in the queue if still wanted.")
            return "missed"
        if not live:
            store.log(db, key, "dry_run", {"would_publish_at": item["scheduled_utc"], "platform": p})
            return "dry_run"
        adapter = _adapter_for(p, adapters)
        if adapter is None:
            store.update(db, key, state="blocked", last_error="credentials not configured")
            alert(f"TML publisher: {p} credentials are not configured; {key} is blocked.")
            return "blocked"
        store.update(db, key, state="uploading", attempts=item["attempts"] + 1)
        try:
            result = _publish(item, adapters)
        except AuthProblem as e:
            store.update(db, key, state="blocked", last_error=str(e))
            alert(f"TML publisher: authentication problem on {p}: {e}. {key} is blocked; nothing was published.")
            return "blocked"
        except Uncertain as e:
            store.update(db, key, state="blocked", last_error=str(e))
            alert(f"TML publisher: {key} outcome uncertain ({e}). Blocked to avoid a duplicate; check the platform before re-queueing.")
            return "blocked"
        except HttpError as e:
            attempts = item["attempts"] + 1
            if e.transient and attempts < config.MAX_ATTEMPTS:
                delay = e.retry_after or config.BASE_BACKOFF * 2 ** (attempts - 1) + random.uniform(0, 60)
                store.update(db, key, state="retry_wait", next_attempt=time.time() + delay, last_error=f"HTTP {e.status} (transient)")
                return "retry"
            store.update(db, key, state="failed", last_error=f"HTTP {e.status}: {e.body[:200]}")
            alert(f"TML publisher: {key} failed (HTTP {e.status}) after {attempts} attempt(s).")
            return "failed"
        store.update(db, key, state="scheduled_remote", remote_id=result["remote_id"], permalink=result.get("permalink"))
        item = store.get(db, key)
    if item["state"] == "uploading":
        # A previous cycle stopped mid-upload. Reconcile instead of re-uploading.
        if not item["remote_id"]:
            store.update(db, key, state="blocked", last_error="interrupted before a remote id was recorded")
            alert(f"TML publisher: {key} was interrupted mid-upload. Blocked; check the platform before re-queueing.")
            return "blocked"
        store.update(db, key, state="scheduled_remote")
        item = store.get(db, key)
    if item["state"] == "scheduled_remote":
        if not live:
            return "dry_run"
        try:
            v = _verify(item, adapters)
        except (HttpError, AuthProblem) as e:
            store.log(db, key, "verify_error", {"error": str(e)})
            return "verify_pending"
        if v.get("rejected"):
            store.update(db, key, state="failed", last_error="platform rejected the media")
            alert(f"TML publisher: {p} rejected {key}.")
            return "failed"
        if v.get("public"):
            store.update(db, key, state="published_verified", permalink=v.get("permalink") or item["permalink"],
                         published_at=now.isoformat())
            return "published"
        if now > when + LATE_LIMIT:
            alert(f"TML publisher: {key} is not public {LATE_LIMIT} after its time (privacy={v.get('privacy')}). Check the platform.")
        return "verify_pending"
    return state


def run_once(repo=None, adapters=None, now=None):
    repo = repo or config.REPO
    now = now or now_utc()
    config.STATE.mkdir(parents=True, exist_ok=True)
    with open(config.STATE / "worker.lock", "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return {"skipped": "another worker is running"}
        results = {}
        with store.connect() as db:
            created, problems = sync(db, repo)
            for msg in problems:
                alert(f"TML publisher: queue manifest problem: {msg}")
            if config.pause_file().exists():
                return {"paused": True, "created": created, "problems": problems}
            adapters = adapters if adapters is not None else default_adapters()
            for item in db.execute("SELECT * FROM items WHERE state IN ('approved','retry_wait','uploading','scheduled_remote')").fetchall():
                results[item["key"]] = process(db, item, adapters, now)
            from . import availability
            avail = availability.check(db, repo, adapters.get("meta"), now=now, alert=alert)
        return {"created": created, "problems": problems, "results": results, "availability": avail, "dryRun": config.DRY_RUN}


def health(adapters=None):
    adapters = adapters if adapters is not None else default_adapters()
    out = {}
    for name, adapter in adapters.items():
        if adapter is None:
            out[name] = {"ok": False, "detail": "not configured"}
            continue
        try:
            out[name] = adapter.health()
        except AuthProblem as e:
            out[name] = {"ok": False, "detail": str(e)}
            alert(f"TML publisher: {name} authentication check failed: {e}")
        except HttpError as e:
            out[name] = {"ok": False, "detail": f"HTTP {e.status}"}
    with open(config.STATE / "health.json", "w") as f:
        json.dump({"at": now_utc().isoformat(), "platforms": out}, f)
    return out


def daily_report(now=None):
    now = now or now_utc()
    since = time.time() - 86400  # rows touched in the last 24 hours (stored with the system clock)
    with store.connect() as db:
        rows = db.execute("SELECT key,state,permalink,remote_id,local_time,last_error FROM items WHERE updated_at>=? ORDER BY local_time",
                          (since,)).fetchall()
        lines = [f"TML publisher daily report ({now.astimezone(ZoneInfo(config.TIMEZONE)).date()} Melbourne). Dry run: {config.DRY_RUN}. Live platforms: {sorted(config.ENABLED_PLATFORMS) or 'none'}"]
        for r in rows:
            lines.append(f"- {r['key']}: {r['state']}" + (f" {r['permalink'] or r['remote_id']}" if r['state'] == 'published_verified' else "")
                         + (f" ({r['last_error']})" if r["last_error"] and r["state"] in ("blocked", "failed", "needs_review") else ""))
        db.executescript("CREATE TABLE IF NOT EXISTS availability (date TEXT, series TEXT, outcome TEXT, detail TEXT, at REAL, PRIMARY KEY(date, series));")
        lines.append("Daily editions (checked on Facebook and Instagram after each deadline):")
        for r in db.execute("SELECT date,series,outcome,detail FROM availability WHERE date>=? ORDER BY date,series",
                            ((now - timedelta(days=1)).date().isoformat(),)):
            lines.append(f"  {r['date']} {r['series']}: {r['outcome'].upper()} {r['detail']}")
        upcoming = db.execute("SELECT key,local_time FROM items WHERE state IN ('approved','retry_wait','scheduled_remote') ORDER BY local_time LIMIT 10").fetchall()
        lines.append("Next: " + (", ".join(f"{r['key']} at {r['local_time']}" for r in upcoming) or "nothing queued"))
    text = "\n".join(lines)
    (config.STATE / "reports").mkdir(parents=True, exist_ok=True)
    (config.STATE / "reports" / f"{now.date()}.txt").write_text(text)
    return text
