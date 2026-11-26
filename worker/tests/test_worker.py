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
        self.calls, self.fail, self.public, self.channel = [], fail or {}, True, "UCTML"

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
        if "youtube/v3/channels" in url:
            return 200, {}, json.dumps({"items": [{"id": self.channel, "snippet": {"title": "Two Market Ledger"}}]}).encode()
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
        self.orig = (config.STATE, config.DRY_RUN, config.ENABLED_PLATFORMS, config.ALERT_COMMAND, config.PRIVATE_ONLY)
        config.PRIVATE_ONLY = False
        self.orig_media = (config.ALLOW_REPO_MEDIA, config.STAGING)
        config.ALLOW_REPO_MEDIA = True
        config.STAGING = root / "incoming"
        config.STATE = root / "state"
        config.DRY_RUN = False
        config.ENABLED_PLATFORMS = {"youtube", "youtube_shorts", "instagram_reels", "facebook_reels"}
        config.ALERT_COMMAND = ""
        worker.alert.__defaults__[0].clear()

    def tearDown(self):
        config.STATE, config.DRY_RUN, config.ENABLED_PLATFORMS, config.ALERT_COMMAND, config.PRIVATE_ONLY = self.orig
        config.ALLOW_REPO_MEDIA, config.STAGING = self.orig_media
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
        return {"youtube": YouTube(http, {"client_id": "a", "client_secret": "b", "refresh_token": "c", "channel_id": "UCTML"}),
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

    def test_wrong_youtube_channel_blocks_before_any_upload(self):
        self.manifest()
        fake = Fake()
        fake.channel = "UCSOMEONEELSE"
        worker.run_once(self.repo, adapters=self.adapters(fake), now=NOW)
        item = self.state("TML-YT-003|youtube|default")
        self.assertEqual(item["state"], "blocked")
        self.assertIn("not the confirmed TML channel", item["last_error"])
        self.assertFalse([u for m, u in fake.calls if "upload/youtube" in u], "nothing is uploaded to another channel")

    def test_unconfirmed_channel_id_blocks(self):
        self.manifest()
        http = Http(Fake())
        adapters = {"youtube": YouTube(http, {"client_id": "a", "client_secret": "b", "refresh_token": "c"}), "meta": None}
        worker.run_once(self.repo, adapters=adapters, now=NOW)
        self.assertIn("no confirmed channel_id", self.state("TML-YT-003|youtube|default")["last_error"])

    def test_stored_youtube_data_is_refreshed_or_deleted_within_30_days(self):
        self.manifest()
        fake = Fake()
        worker.run_once(self.repo, adapters=self.adapters(fake), now=NOW)
        key = "TML-YT-003|youtube|default"
        with store.connect() as db:
            db.execute("UPDATE items SET updated_at=updated_at-26*86400 WHERE key=?", (key,))
        yt = self.adapters(fake)["youtube"]
        self.assertEqual(worker.refresh_youtube_data(yt), {"refreshed": 1, "deleted": 0})
        self.assertEqual(worker.refresh_youtube_data(yt), {"refreshed": 0, "deleted": 0}, "fresh again")
        with store.connect() as db:
            db.execute("UPDATE items SET updated_at=updated_at-26*86400 WHERE key=?", (key,))
        self.assertEqual(worker.refresh_youtube_data(self.adapters(Fake(fail={"youtube/v3/videos": 404}))["youtube"]),
                         {"refreshed": 0, "deleted": 1})
        item = self.state(key)
        self.assertEqual((item["remote_id"], item["permalink"], item["state"]), (None, None, "published_verified"))
        self.manifest()  # the same content is still never uploaded again
        fake2 = Fake()
        worker.run_once(self.repo, adapters=self.adapters(fake2), now=NOW + timedelta(minutes=5))
        self.assertFalse([u for m, u in fake2.calls if "upload/youtube" in u])

    def test_private_only_gate_blocks_public_items_but_runs_private_test(self):
        config.PRIVATE_ONLY = True
        self.manifest()  # an ordinary (public) approved video
        self.manifest(cid="TML-TEST-PRIVATE-001", targets=("youtube_shorts",), visibility="private")
        fake = Fake()
        fake.public = False
        out = worker.run_once(self.repo, adapters=self.adapters(fake), now=NOW)
        self.assertEqual(out["results"]["TML-YT-003|youtube|default"], "dry_run", "public publishing stays off")
        uploads = [c for c in fake.calls if "upload/youtube" in c[1] and c[0] == "POST"]
        self.assertEqual(len(uploads), 1, "only the private test is uploaded")
        item = self.state("TML-TEST-PRIVATE-001|youtube_shorts|default")
        self.assertEqual(item["state"], "private_verified")
        self.assertIn("private upload test", (config.STATE / "alerts.log").read_text())

    def test_private_test_never_sets_publish_time_and_flags_non_private(self):
        config.PRIVATE_ONLY = True
        self.manifest(cid="TML-TEST-PRIVATE-002", targets=("youtube",), visibility="private")
        fake = Fake()  # this fake reports the video as public
        bodies = []
        orig = fake.__call__
        def spy(method, url, headers, body):
            if "upload/youtube" in url and method == "POST":
                bodies.append(body)
            return orig(method, url, headers, body)
        out = worker.run_once(self.repo, adapters=self.adapters(spy), now=NOW)
        self.assertNotIn(b"publishAt", bodies[0])
        self.assertIn(b'"privacyStatus": "private"', bodies[0])
        self.assertEqual(self.state("TML-TEST-PRIVATE-002|youtube|default")["state"], "needs_review")

    def test_private_test_rules(self):
        self.manifest(cid="TML-YT-009", visibility="private")
        self.manifest(cid="TML-TEST-PRIVATE-003", targets=("instagram_reels",), visibility="private")
        out = worker.run_once(self.repo, adapters=self.adapters(Fake()), now=NOW)
        self.assertTrue(any("TML-TEST- content ID" in p for p in out["problems"]))
        self.assertTrue(any("YouTube only" in p for p in out["problems"]))

    def stage(self, cid, folder=None, **extra):
        d = config.STAGING / (folder or cid)
        d.mkdir(parents=True, exist_ok=True)
        (d / "video.mp4").write_bytes(b"staged private bytes")
        doc = {"contentId": cid, "title": "Hindi explainer", "caption": "Education only.", "asset": "video.mp4",
               "assetSha256": hashlib.sha256(b"staged private bytes").hexdigest(), "publishAt": NOW.isoformat(),
               "targets": [{"platform": "youtube_shorts"}], "language": "hi",
               "approval": {"owner": True, "approvedBy": "Founder", "approvedAt": "2026-11-30", "narrationApproved": True,
                            "rightsVerified": True, "captionsChecked": True, "playbackChecked": True}}
        doc.update(extra)
        (d / "manifest.json").write_text(json.dumps(doc))

    def test_production_refuses_media_from_the_public_repository(self):
        config.ALLOW_REPO_MEDIA = False
        self.manifest()
        out = worker.run_once(self.repo, adapters=self.adapters(Fake()), now=NOW)
        self.assertEqual(out["created"], 0)
        self.assertTrue(any("staged privately" in p for p in out["problems"]), out["problems"])

    def test_staged_private_export_uploads_with_language(self):
        config.ALLOW_REPO_MEDIA = False
        self.stage("TML-HI-001")
        bodies = []
        fake = Fake()
        def spy(method, url, headers, body):
            if "upload/youtube" in url and method == "POST":
                bodies.append(json.loads(body))
            return fake(method, url, headers, body)
        out = worker.run_once(self.repo, adapters=self.adapters(spy), now=NOW)
        self.assertEqual(self.state("TML-HI-001|youtube_shorts|default")["state"], "published_verified", out)
        self.assertEqual(bodies[0]["snippet"]["defaultAudioLanguage"], "hi")

    def test_staging_rules(self):
        config.ALLOW_REPO_MEDIA = False
        self.stage("TML-HI-002", folder="wrong-folder")
        self.stage("TML-HI-003", asset="../TML-HI-002/video.mp4")
        self.stage("TML-HI-004", language="fr")
        out = worker.run_once(self.repo, adapters=self.adapters(Fake()), now=NOW)
        text = " ".join(out["problems"])
        for needle in ("folder name must equal", "leaves its folder", "language must be"):
            self.assertIn(needle, text)
        self.assertEqual(out["created"], 0)

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


class AvailabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        (self.repo / "content" / "evergreen" / "ready").mkdir(parents=True)
        (self.repo / "content" / "evergreen" / "ready" / "E01.json").write_text(json.dumps({
            "id": "E01", "approval": {"owner": True}, "imageUrl": "https://raw.githubusercontent.com/x/card.jpg",
            "captions": {"facebook": "FINANCIAL EDUCATION · ARE YOU FINANCIALLY READY? fb", "instagram": "ig #AreYouFinanciallyReady"}}))
        self.orig = (config.STATE, config.DRY_RUN, config.ENABLED_PLATFORMS)
        config.STATE = root / "state"
        config.DRY_RUN = False
        config.ENABLED_PLATFORMS = {"facebook_image", "instagram_image"}
        from tmlpub import availability
        self.av = availability
        self.av.FALLBACK_SERIES = {"ready"}

    def tearDown(self):
        config.STATE, config.DRY_RUN, config.ENABLED_PLATFORMS = self.orig
        self.av.FALLBACK_SERIES = set()
        self.tmp.cleanup()

    class FakeMeta:
        def __init__(self, fb, ig):
            self.caps, self.published = {"facebook": fb, "instagram": ig}, []
        def recent_captions(self, since):
            return self.caps
        def publish_image(self, platform, url, caption):
            self.published.append(platform)
            return {"remote_id": "R-" + platform}

    def at(self, hh, mm):
        return datetime(2026, 12, 1, hh, mm, tzinfo=self.av.MEL)

    def test_present_edition_recorded_published(self):
        meta = self.FakeMeta(["THE LEDGER MORNING: ..."], ["... #TheLedgerMorning"])
        alerts = []
        with store.connect() as db:
            out = self.av.check(db, self.repo, meta, now=self.at(9, 41), alert=alerts.append)
        self.assertEqual(out, {"morning": "published"})
        self.assertEqual(alerts, [])

    def test_missing_news_edition_alerts_without_fallback(self):
        meta = self.FakeMeta([], [])
        alerts = []
        with store.connect() as db:
            out = self.av.check(db, self.repo, meta, now=self.at(19, 41), alert=alerts.append)
            again = self.av.check(db, self.repo, meta, now=self.at(19, 46), alert=alerts.append)
        self.assertEqual(out, {"evening": "missed"})
        self.assertEqual(again, {}, "each slot is checked once")
        self.assertEqual(meta.published, [], "news editions never get an automatic fallback unless enabled")
        self.assertIn("not on facebook, instagram", alerts[0])

    def test_missing_ready_edition_uses_approved_evergreen_once(self):
        meta = self.FakeMeta([], [])
        alerts = []
        with store.connect() as db:
            out = self.av.check(db, self.repo, meta, now=self.at(15, 26), alert=alerts.append)
            self.assertEqual(out, {"ready": "fallback_published"})
            self.assertEqual(sorted(meta.published), ["facebook", "instagram"])
            self.assertIsNone(self.av.next_evergreen(db, self.repo, "ready", self.at(15, 26).date() + timedelta(days=1)),
                              "the same evergreen item is not reused within 30 days")

    def test_outside_window_no_check(self):
        meta = self.FakeMeta([], [])
        with store.connect() as db:
            self.assertEqual(self.av.check(db, self.repo, meta, now=self.at(12, 0), alert=lambda m: None), {})


class MalformedManifestTests(unittest.TestCase):
    def test_malformed_manifest_is_reported_not_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            (repo / "queue").mkdir(parents=True)
            (repo / "queue" / "bad.json").write_text(json.dumps({"contentId": "TML-BAD-1", "approval": {"owner": True, "approvedAt": "x", "approvedBy": "y"},
                                                                  "asset": {"path": "nope"}, "targets": "youtube"}))
            orig = config.STATE
            config.STATE = Path(tmp) / "state"
            try:
                with store.connect() as db:
                    created, problems = worker.sync(db, repo)
            finally:
                config.STATE = orig
            self.assertEqual(created, 0)
            self.assertTrue(any("bad.json" in p for p in problems), problems)
