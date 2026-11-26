"""Queue manifests committed to the repository (queue/*.json). Only owner-approved, checksum-matching media is eligible."""
import hashlib
import json
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from . import config, store

ID = re.compile(r"^[A-Z0-9][A-Z0-9-]{2,40}$")
HOLD = re.compile(r"\b(buy now|sell now|don'?t miss out|guaranteed (returns?|profit|income)|risk[- ]free|sure[- ]shot|multibaggers?|"
                  r"penny stocks?|get[- ]rich|double your money|fast money|quick money|easy money|become a millionaire|intraday|"
                  r"day trading|stock tips?|beat(ing)? the market|you should (buy|sell|invest)|we recommend)\b", re.I)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(doc, repo):
    """Return (rows, errors). Every failure blocks; nothing is guessed."""
    errors, rows = [], []
    cid = doc.get("contentId", "")
    if not ID.match(cid):
        return [], [f"invalid contentId {cid!r}"]
    if doc.get("manual"):
        for target in doc.get("targets", []):
            rows.append(dict(key=store.key_for(cid, target["platform"], target.get("account", "default")), content_id=cid,
                             platform=target["platform"], account=target.get("account", "default"),
                             state="manual_published" if target.get("remoteId") or target.get("permalink") else "manual_pending",
                             title=doc.get("title"), remote_id=target.get("remoteId"), permalink=target.get("permalink"),
                             published_at=target.get("publishedAt"), manifest=json.dumps(doc)))
        return rows, errors
    private_test = doc.get("visibility") == "private"
    if private_test:
        # A private upload test: own content ID (so the real video's later publication is never blocked), YouTube only.
        if not cid.startswith("TML-TEST-"):
            return [], [f"{cid}: a private test must use a TML-TEST- content ID"]
        if {t.get("platform") for t in doc.get("targets", [])} - {"youtube", "youtube_shorts"}:
            return [], [f"{cid}: a private test may target YouTube only"]
    elif doc.get("visibility") not in (None, "public"):
        return [], [f"{cid}: unknown visibility {doc.get('visibility')!r}"]
    if doc.get("_source") == "repo" and not config.ALLOW_REPO_MEDIA:
        return [], [f"{cid}: unpublished media must be staged privately on the server, not committed to the public repository"]
    if doc.get("_source") == "staging" and doc.get("_folder") != cid:
        return [], [f"{cid}: staging folder name must equal the contentId"]
    if doc.get("language", "en") not in config.LANGUAGES:
        return [], [f"{cid}: language must be one of {sorted(config.LANGUAGES)}"]
    approval = doc.get("approval") or {}
    if approval.get("owner") is not True or not approval.get("approvedAt") or not approval.get("approvedBy"):
        return [], [f"{cid}: no owner approval recorded"]
    for flag in ("narrationApproved", "rightsVerified", "captionsChecked", "playbackChecked"):
        if approval.get(flag) is not True:
            errors.append(f"{cid}: release gate '{flag}' not confirmed")
    text = " ".join(str(doc.get(k, "")) for k in ("title", "caption", "description"))
    if HOLD.search(text):
        errors.append(f"{cid}: held wording ({HOLD.search(text).group(0)})")
    asset = (repo / doc.get("asset", "")).resolve()
    if doc.get("asset") and repo.resolve() not in asset.parents:
        errors.append(f"{cid}: asset path leaves its folder")
    elif not doc.get("asset") or not asset.is_file():
        errors.append(f"{cid}: asset missing")
    elif sha256(asset) != doc.get("assetSha256"):
        errors.append(f"{cid}: asset checksum does not match the approved file")
    try:
        when = datetime.fromisoformat(doc["publishAt"])
        if when.tzinfo is None:
            raise ValueError("publishAt needs a UTC offset")
    except (KeyError, ValueError) as e:
        errors.append(f"{cid}: publishAt invalid ({e})")
        when = None
    if errors:
        return [], errors
    for target in doc.get("targets", []):
        platform = target.get("platform")
        if platform in config.ROUTINE_PLATFORMS:
            continue  # handled by the cloud routines through Buffer, never by the worker
        if platform not in config.WORKER_PLATFORMS:
            errors.append(f"{cid}: unknown platform {platform}")
            continue
        rows.append(dict(key=store.key_for(cid, platform, target.get("account", "default")), content_id=cid, platform=platform,
                         account=target.get("account", "default"), state="approved", title=doc.get("title"),
                         caption=target.get("caption") or doc.get("caption"), caption_version=doc.get("captionVersion", "1"),
                         asset_path=str(asset), asset_sha256=doc["assetSha256"],
                         scheduled_utc=when.astimezone(timezone.utc).isoformat(),
                         local_time=when.astimezone(ZoneInfo(config.TIMEZONE)).isoformat(),
                         approved_by=approval["approvedBy"], approved_at=approval["approvedAt"], manifest=json.dumps(doc)))
    return rows, errors


def load_all(repo, staging=None):
    """(path, doc, base) for public-repo records (queue/**) and private staged exports (<staging>/<id>/manifest.json)."""
    docs = []
    for path in sorted((repo / "queue").rglob("*.json")):
        try:
            doc = json.loads(path.read_text())
            doc["_source"] = "repo"
        except ValueError as e:
            doc = {"_error": str(e)}
        docs.append((path, doc, repo))
    staging = staging if staging is not None else config.STAGING
    if staging.is_dir():
        for path in sorted(staging.glob("*/manifest.json")):
            try:
                doc = json.loads(path.read_text())
                doc["_source"] = "staging"
                doc["_folder"] = path.parent.name
            except ValueError as e:
                doc = {"_error": str(e)}
            docs.append((path, doc, path.parent))
    return docs
