import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import upload_pack  # noqa: E402


class UploadPackTests(unittest.TestCase):
    def make(self, tmp, approved=True, cid="TML-HI-20261201-01", tamper=False, **extra):
        d = Path(tmp) / "export"
        d.mkdir()
        (d / "video.mp4").write_bytes(b"approved bytes")
        (d / "captions.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nनमस्ते\n")
        (d / "thumbnail.jpg").write_bytes(b"jpg")
        m = {"contentId": cid, "language": "hi", "title": "वेतन और खरीदने की क्षमता", "description": "पहला पैराग्राफ।\n\nhttps://www.abs.gov.au/x",
             "asset": "video.mp4", "assetSha256": hashlib.sha256(b"approved bytes" + (b"x" if tamper else b"")).hexdigest(),
             "hashtags": ["#TMLEducation", "#HindiShorts"], "voice": "synthetic (disclosed)", "sources": [{"publisher": "ABS", "period": "Oct 2026"}]}
        if approved:
            m["approval"] = {"owner": True, "approvedBy": "Founder", "approvedAt": "2026-11-30"}
        m.update(extra)
        (d / "manifest.json").write_text(json.dumps(m, ensure_ascii=False))
        return d

    def test_builds_pack_for_approved_video(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "packs"
            out.mkdir()
            dest = upload_pack.build(self.make(tmp), out)
            self.assertTrue((dest / "video.mp4").is_file() and (dest / "cover.jpg").is_file() and (dest / "captions.srt").is_file())
            ig = (dest / "instagram_caption.txt").read_text()
            tt = (dest / "tiktok_caption.txt").read_text()
            self.assertIn("#TMLEducation", ig)
            self.assertIn("Source: ABS (Oct 2026)", ig)
            self.assertIn("AI-generated narration", ig)
            self.assertNotIn("http", ig)  # links aren't clickable on Instagram or TikTok
            self.assertLess(len(tt), len(ig))
            self.assertIn("AI label", (dest / "UPLOAD_CHECKLIST.md").read_text())

    def test_refuses_unapproved_tampered_test_or_git_output(self):
        for kwargs, needle in (({"approved": False}, "no owner approval"), ({"tamper": True}, "SHA-256"),
                               ({"cid": "TML-TEST-20261128-01"}, "test content IDs"), ({"language": "fr"}, "language")):
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / "packs"
                out.mkdir()
                with self.assertRaises(SystemExit) as cm:
                    upload_pack.build(self.make(tmp, **kwargs), out)
                self.assertIn(needle, str(cm.exception))
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q", tmp], check=True)
            out = Path(tmp) / "packs"
            out.mkdir()
            with tempfile.TemporaryDirectory() as tmp2:
                with self.assertRaises(SystemExit) as cm:
                    upload_pack.build(self.make(tmp2), out)
                self.assertIn("inside a Git repository", str(cm.exception))

    def test_uses_social_captions_when_supplied_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "packs"
            out.mkdir()
            exp = self.make(tmp, social={"instagramCaption": "IG text", "tiktokCaption": "TT text"})
            dest = upload_pack.build(exp, out)
            self.assertEqual((dest / "instagram_caption.txt").read_text().strip(), "IG text")
            with self.assertRaises(SystemExit):
                upload_pack.build(exp, out)


if __name__ == "__main__":
    unittest.main()
