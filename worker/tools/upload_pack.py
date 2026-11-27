#!/usr/bin/env python3
"""Build a manual Instagram Reel and TikTok upload pack for ONE owner-approved video (run on the owner's Mac).

  python3 upload_pack.py <export folder> <output folder outside any Git repository>

Reads <export folder>/manifest.json (Media Studio export contract, ops/MEDIA_STUDIO_HANDOFF.md). It REFUSES unless the manifest
carries the owner's approval for this exact file (approval.owner true, approvedBy/approvedAt, assetSha256 matches video.mp4),
the language is en or hi, and the output folder is not inside a Git repository (unpublished video must stay private).

Writes <output>/<contentId>/: video.mp4 (copy of the approved file), cover.jpg (if present), captions.srt (if present),
instagram_caption.txt, tiktok_caption.txt, UPLOAD_CHECKLIST.md. Platform captions come from manifest["social"] when present
("instagramCaption", "tiktokCaption"); otherwise they are composed from the title, description, sources and hashtags.
Nothing is uploaded or published by this script.
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

DISCLOSURE_HI = "शिक्षा के लिए, वित्तीय सलाह नहीं।"
DISCLOSURE_EN = "Education only. Not financial advice."


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def inside_git(path):
    try:
        out = subprocess.run(["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
        return out.returncode == 0 and out.stdout.strip() == "true"
    except FileNotFoundError:
        return False


def check(export, out_root):
    m = json.loads((export / "manifest.json").read_text())
    errors = []
    cid = m.get("contentId", "")
    if not re.fullmatch(r"TML-[A-Z0-9-]{2,40}", cid):
        errors.append("invalid contentId")
    if cid.startswith("TML-TEST-"):
        errors.append("test content IDs are never published; the approved public version needs its own content ID")
    a = m.get("approval") or {}
    if a.get("owner") is not True or not a.get("approvedBy") or not a.get("approvedAt"):
        errors.append("no owner approval recorded in the manifest")
    video = export / m.get("asset", "video.mp4")
    if not video.is_file():
        errors.append("video file missing")
    elif sha256(video) != m.get("assetSha256"):
        errors.append("video does not match the approved SHA-256")
    if m.get("language") not in ("en", "hi"):
        errors.append("language must be en or hi")
    if inside_git(out_root if out_root.exists() else out_root.parent):
        errors.append("output folder is inside a Git repository; unpublished video must stay private")
    return m, errors


def compose(m, platform):
    social = m.get("social") or {}
    key = "instagramCaption" if platform == "instagram" else "tiktokCaption"
    if social.get(key):
        return social[key].strip() + "\n"
    hi = m.get("language") == "hi"
    disclosure = DISCLOSURE_HI if hi else DISCLOSURE_EN
    tags = [t for t in (m.get("hashtags") or []) if t.startswith("#")]
    if "#TMLEducation" not in tags:
        tags.insert(0, "#TMLEducation")
    sources = "; ".join(s.get("publisher", "") + (f" ({s['period']})" if s.get("period") else "") for s in (m.get("sources") or []))
    desc = re.sub(r"https?://\S+", "", m.get("description", "")).strip()
    first = desc.split("\n\n")[0].strip() if desc else ""
    voice = "AI-generated narration." if "synthetic" in (m.get("voice") or "").lower() else ""
    if platform == "instagram":
        parts = [m["title"], first, ("Source: " + sources) if sources else "", voice, disclosure, " ".join(tags[:8])]
    else:  # TikTok: shorter
        parts = [m["title"], ("Source: " + sources) if sources else "", voice, disclosure, " ".join(tags[:5])]
    return "\n\n".join(p for p in parts if p) + "\n"


CHECKLIST = """# Manual upload checklist: {cid} ({lang})

Approved by: {who} on {when}. Exact file SHA-256: `{sha}`. Planned release (from the YouTube calendar, Melbourne time): {slot}.

## Before uploading
- [ ] The YouTube version of this video has been published, and the link is: ____________________
- [ ] This file is the approved version (the checksum above matches: `shasum -a 256 video.mp4`).
- [ ] Today is not a repost of anything in `queue/manual/` or `content/history.json`.

## Instagram Reel (Instagram app or Meta Business Suite)
1. New Reel, choose `video.mp4`. Cover: `cover.jpg` (or a frame with the large caption text).
2. Paste `instagram_caption.txt`. Captions are on screen already; don't add the SRT.
3. Turn the **AI label** on if the app offers it (the narration is synthetic).
4. Share to Reels, and share to feed only if you want it on the grid. Do not also cross-post to Facebook (the Facebook post is separate).
5. Copy the Reel link here: ____________________

## TikTok (TikTok app)
1. Upload `video.mp4`; choose the cover. Paste `tiktok_caption.txt`.
2. Turn **AI-generated content** on (synthetic narration). Visibility: public. Leave comments and duets as you prefer.
3. Copy the TikTok link here: ____________________

## After
- [ ] Send both links to Claude so they're recorded in `content/history.json` (this prevents any repost).
- [ ] At 48 hours and 7 days, read the views, likes, comments, shares and saves and tell Claude (or export them). Unavailable numbers are recorded as unavailable.
- [ ] Keep this folder private. Never put the video in a public repository.
"""


def build(export, out_root, slot="(per the confirmed YouTube calendar)"):
    export, out_root = Path(export), Path(out_root)
    m, errors = check(export, out_root)
    if errors:
        raise SystemExit("REFUSED: " + "; ".join(errors))
    dest = out_root / m["contentId"]
    if dest.exists():
        raise SystemExit(f"REFUSED: {dest} already exists")
    dest.mkdir(parents=True)
    shutil.copy2(export / m.get("asset", "video.mp4"), dest / "video.mp4")
    for src, name in (("thumbnail.jpg", "cover.jpg"), ("cover.jpg", "cover.jpg"), ("captions.srt", "captions.srt")):
        if (export / src).is_file() and not (dest / name).exists():
            shutil.copy2(export / src, dest / name)
    (dest / "instagram_caption.txt").write_text(compose(m, "instagram"))
    (dest / "tiktok_caption.txt").write_text(compose(m, "tiktok"))
    a = m["approval"]
    (dest / "UPLOAD_CHECKLIST.md").write_text(CHECKLIST.format(cid=m["contentId"], lang=m["language"], who=a["approvedBy"], when=a["approvedAt"],
                                                                sha=m["assetSha256"], slot=slot))
    return dest


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    print("Pack written to", build(sys.argv[1], sys.argv[2]))
