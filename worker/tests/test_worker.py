"""Integration tests for the publishing worker with a fake platform transport (no network, no credentials)."""
import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tmlpub import config, store, worker  # noqa: E402
from tmlpub.adapters.meta import Meta  # noqa: E402
from tmlpub.adapters.youtube import YouTube  # noqa: E402
from tmlpub.http import Http  # noqa: E402

NOW = datetime(2026, 12, 1, 8, 0, tzinfo=timezone.utc)


class Fake:
    """Scripted platform API. Records every call."""
    def __init__(self, fail=None):
        self.calls, self.fail, self.public = [], fail or {}, True

    def __call__(self, method, url, headers, body):
        self.calls.append((method, url))
        for needle, status in list(self.fail.items()):
            if needle in url:
                return status, {}, b'{"error":"x"}'
        if "oauth2" in url:
            return 200, {}, b'{"access_token":"t"}'
        if "upload/youtube" in url and method == "POST":
            return 200, {"Location": "https://upload.example/session"}, b"{}"
        if "upload.example/session" in url:
            return 200, {}, b'{"id":"VID123"}'
        if "youtube/v3/videos" in url:
            status = "public" if self.public else "private"
            return 200, {}, json.dumps({"items": [{"status": {"privacyStatus": status, "uploadStatus": "processed"}}]}).encode()
        if url.endswith("/media") and method == "POST":
            return 200, {}, b'{"id":"C1","uri":"https://rupload.example/ig"}'
        if "rupload.example" in url:
            return 200, {}, b'{"success":true}'
        if "C1?fields=status_code" in url:
            return 200, {}, b'{"status_code":"FINISHED"}'
        if url.endswith("/media_publish"):
            return 200, {}, b'{"id":"M9"}'
        if "M9?fields=permalink" in url:
            return 200, {}, b'{"permalink":"https://www.instagram.com/reel/abc/","media_type":"VIDEO"}'
        return 404, {}, b"{}"


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        (self.repo / "queue").mkdir(parents=True)
        (self.repo / "videos").mkdir()
        self.video = self.repo / "videos" / "ep02.mp4"
        self.video.write_bytes(b"fake mp4 bytes")
        self.orig = (config.STATE, config.DRY_RUN, config.ENABLED_PLATFORMS, config.ALERT_COMMAND)
        config.STATE = root / "state"
        config.DRY_RUN = False
        config.ENABLED_PLATFORMS = {"youtube", "youtube_shorts", "instagram_reels", "facebook_reels"}
        config.ALERT_COMMAND = ""
        worker.alert.__defaults__[0].clear()

    def tearDown(self):
        config.STATE, config.DRY_RUN, config.ENABLED_PLATFORMS, config.ALERT_COMMAND = self.orig
        self.tmp.cleanup()

    def manifest(self, cid="TML-YT-003", publish=NOW, targets=("youtube",), approval=True, caption="Inflation explained.", **extra):
        doc = {"contentId": cid, "title": "What is inflation?", "caption": caption, "asset": "videos/ep02.mp4",
               "assetSha256": hashlib.sha256(self.video.read_bytes()).hexdigest(), "publishAt": publish.isoformat(),
               "targets": [{"platform": t} for t in targets]}
        if approval:
            doc["approval"] = {"owner": True, "approvedBy": "Founder", "approvedAt": "2026-11-30", "narrationApproved": True,
                               "rightsVerified": True, "captionsChecked": True, "playbackChecked": True}
        doc.update(extra)
        (self.repo / "queue" / f"{cid}.json").write_text(json.dumps(doc))

    def adapters(self, fake):
        http = Http(fake)
        return {"youtube": YouTube(http, {"client_id": "a", "client_secret": "b", "refresh_token": "c"}),
                "meta": Meta(http, {"page_id": "P", "ig_user_id": "IG", "page_token": "T"}, sleep=lambda s: None)}

    def state(self, key):
        with store.connect() as db:
            return dict(store.get(db, key))

    def test_unapproved_or_tampered_media_is_never_queued(self):
        self.manifest(approval=False)
        out = worker.run_once(self.repo, adapters=self.adapters(Fake()), now=NOW)
        self.assertEqual(out["created"], 0)
        self.assertTrue(any("no owner approval" in p for p in out["problems"]))
        self.manifest(cid="TML-YT-004")
        self.video.write_bytes(b"changed after approval")
        out = worker.run_once(self.repo, adapters=self.adapters(Fake()), now=NOW)
        self.assertTrue(any("checksum" in p for p in out["problems"]))

    def test_held_wording_blocks(self):
        self.manifest(caption="Buy now before it's too late")
        out = worker.run_once(self.repo, adapters=self.adapters(Fake()), now=NOW)
        self.assertEqual(out["created"], 0)
        self.assertTrue(any("held wording" in p for p in out["problems"]))

    def test_dry_run_makes_no_platform_calls(self):
        config.DRY_RUN = True
        self.manifest()
        fake = Fake()
        out = worker.run_once(self.repo, adapters=self.adapters(fake), now=NOW)
        self.assertEqual(out["results"]["TML-YT-003|youtube|default"], "dry_run")
        self.assertEqual(fake.calls, [])

    def test_youtube_publish_verify_and_idempotent(self):
        self.manifest()
        fake = Fake()
        worker.run_once(self.repo, adapters=self.adapters(fake), now=NOW)
        item = self.state("TML-YT-003|youtube|default")
        self.assertEqual((item["state"], item["remote_id"]), ("published_verified", "VID123"))
        uploads = sum(1 for m, u in fake.calls if "upload/youtube" in u)
        worker.run_once(self.repo, adapters=self.adapters(fake), now=NOW + timedelta(minutes=5))
        self.assertEqual(sum(1 for m, u in fake.calls if "upload/youtube" in u), uploads, "never uploads twice")

    def test_youtube_scheduled_stays_unverified_until_public(self):
        self.manifest(publish=NOW + timedelta(hours=3))
        fake = Fake()
        fake.public = False
        worker.run_once(self.repo, adapters=self.adapters(fake), now=NOW)
        self.assertEqual(self.state("TML-YT-003|youtube|default")["state"], "scheduled_remote", "upload is not publication")
        fake.public = True
        worker.run_once(self.repo, adapters=self.adapters(fake), now=NOW + timedelta(hours=3, minutes=5))
        self.assertEqual(self.state("TML-YT-003|youtube|default")["state"], "published_verified")

    def test_manual_posts_prevent_duplicates(self):
        (self.repo / "queue" / "manual.json").write_text(json.dumps({"contentId": "TML-YT-003", "manual": True,
            "targets": [{"platform": "youtube", "permalink": "https://youtu.be/x"}]}))
        self.manifest()
        fake = Fake()
        worker.run_once(self.repo, adapters=self.adapters(fake), now=NOW)
        self.assertFalse(any("upload/youtube" in u for m, u in fake.calls))

    def test_transient_errors_retry_then_fail(self):
        self.manifest()
        fake = Fake(fail={"upload/youtube": 503})
        worker.run_once(self.repo, adapters=self.adapters(fake), now=NOW)
        item = self.state("TML-YT-003|youtube|default")
        self.assertEqual(item["state"], "retry_wait")
        self.assertGreater(item["next_attempt"], 0)
        with store.connect() as db:
            store.update(db, item["key"], attempts=config.MAX_ATTEMPTS - 1, next_attempt=0)
        worker.run_once(self.repo, adapters=self.adapters(fake), now=NOW)
        self.assertEqual(self.state("TML-YT-003|youtube|default")["state"], "failed")

    def test_uncertain_upload_blocks_instead_of_retrying(self):
        self.manifest()
        worker.run_once(self.repo, adapters=self.adapters(Fake(fail={"upload.example/session": 503})), now=NOW)
        self.assertEqual(self.state("TML-YT-003|youtube|default")["state"], "blocked")
        self.assertIn("uncertain", (config.STATE / "alerts.log").read_text())

    def test_auth_failure_alerts_and_blocks(self):
        self.manifest()
        worker.run_once(self.repo, adapters=self.adapters(Fake(fail={"oauth2": 400})), now=NOW)
        self.assertEqual(self.state("TML-YT-003|youtube|default")["state"], "blocked")
        self.assertIn("authentication", (config.STATE / "alerts.log").read_text())

    def test_missed_window_is_not_published_late(self):
        self.manifest(publish=NOW - timedelta(hours=5))
        fake = Fake()
        worker.run_once(self.repo, adapters=self.adapters(fake), now=NOW)
        self.assertEqual(self.state("TML-YT-003|youtube|default")["state"], "needs_review")
        self.assertFalse(any("upload/youtube" in u for m, u in fake.calls))

    def test_pause_switches(self):
        self.manifest()
        config.STATE.mkdir(parents=True, exist_ok=True)
        config.pause_file().write_text("x")
        fake = Fake()
        self.assertTrue(worker.run_once(self.repo, adapters=self.adapters(fake), now=NOW)["paused"])
        config.pause_file().unlink()
        config.pause_file("youtube").write_text("x")
        self.assertEqual(worker.run_once(self.repo, adapters=self.adapters(fake), now=NOW)["results"]["TML-YT-003|youtube|default"], "paused")
        self.assertEqual(fake.calls, [])

    def test_instagram_reel_flow_and_routine_targets_ignored(self):
        self.manifest(targets=("instagram_reels", "x"))
        worker.run_once(self.repo, adapters=self.adapters(Fake()), now=NOW)
        item = self.state("TML-YT-003|instagram_reels|default")
        self.assertEqual((item["state"], item["permalink"]), ("published_verified", "https://www.instagram.com/reel/abc/"))
        with store.connect() as db:
            self.assertIsNone(store.get(db, "TML-YT-003|x|default"), "X stays with the Buffer routines")

    def test_daily_report(self):
        self.manifest()
        worker.run_once(self.repo, adapters=self.adapters(Fake()), now=NOW)
        text = worker.daily_report(now=NOW)
        self.assertIn("TML-YT-003|youtube|default: published_verified https://www.youtube.com/watch?v=VID123", text)


if __name__ == "__main__":
    unittest.main()
