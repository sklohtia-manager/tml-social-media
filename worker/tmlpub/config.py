"""Paths and settings. Everything comes from environment variables set by the systemd unit; nothing secret is in Git."""
import os
from pathlib import Path

STATE = Path(os.environ.get("TMLPUB_DIR", "/var/lib/tml-social"))
SECRETS = Path(os.environ.get("TMLPUB_SECRETS", "/etc/tml-social"))
REPO = Path(os.environ.get("TMLPUB_REPO", "/var/lib/tml-social/repo"))
DRY_RUN = os.environ.get("TMLPUB_DRY_RUN", "1") != "0"          # dry run unless explicitly disabled
ENABLED_PLATFORMS = set(filter(None, os.environ.get("TMLPUB_PLATFORMS", "").split(",")))  # empty = none live
ALERT_COMMAND = os.environ.get("TMLPUB_ALERT_COMMAND", "")       # e.g. an approved mail script; receives text on stdin
TIMEZONE = "Australia/Melbourne"
MAX_ATTEMPTS = 5
BASE_BACKOFF = 120   # seconds; doubled per attempt, plus jitter
# The worker owns video targets only. Image editions belong to the cloud routines via Buffer, X belongs to Buffer.
WORKER_PLATFORMS = {"youtube", "youtube_shorts", "instagram_reels", "facebook_reels"}
ROUTINE_PLATFORMS = {"x", "instagram_image", "facebook_image", "tiktok_manual", "whatsapp_manual"}


def db_path():
    return STATE / "queue.sqlite3"


def pause_file(platform=None):
    return STATE / ("PAUSE" if platform is None else f"PAUSE.{platform}")
