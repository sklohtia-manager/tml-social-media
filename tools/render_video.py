#!/usr/bin/env python3
"""Branded animated vertical short (1080x1920, H.264, 30 fps) from text slides. Pillow + ffmpeg, no stock media.

  python3 tools/render_video.py spec.json out.mp4
spec = {"series": "TWO MARKET LEDGER · FINANCIAL EDUCATION", "slides": [{"headline": "...", "body": "...", "seconds": 4}, ...],
        "source": "Source: ABS, CPI, October 2026", "closing": "Learn. Understand. Stay Informed."}
Output is a SILENT DRAFT for owner review: never publish it automatically (owner release gate: narration, captions,
rights and playback must be approved). Text stays inside mobile safe areas (top 250 px and bottom 380 px are kept clear).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import BANNED, FOREST, GOLD, WARM, font, paste_logo, wrap  # noqa: E402

W, H, FPS = 1080, 1920, 30


def frame(slide, spec, progress):
    img = Image.new("RGB", (W, H), FOREST)
    d = ImageDraw.Draw(img)
    band = 330
    d.rectangle([0, H - band, W, H], fill=WARM)
    d.rectangle([0, H - band - 6, W, H - band], fill=GOLD)
    paste_logo(img, 420, H - band, band - 80)
    d.text((80, 270), spec.get("series", "TWO MARKET LEDGER"), font=font("Inter-SemiBold.otf", 32), fill=GOLD)
    # simple, readable animation: gold rule grows, text slides up and fades in during the first 0.6 s
    t = min(1.0, progress / 0.6)
    d.rectangle([80, 330, 80 + int(160 * t), 338], fill=GOLD)
    offset = int((1 - t) * 40)
    y = 400 + offset
    colour = tuple(int(c * t + f * (1 - t)) for c, f in zip((255, 255, 255), (21, 61, 46)))
    hf = font("InterDisplay-Bold.otf", 92)
    for line in wrap(d, slide["headline"], hf, W - 160)[:5]:
        d.text((80, y), line, font=hf, fill=colour)
        y += 108
    y += 30
    bf = font("Inter-Regular.otf", 46)
    soft = tuple(int(c * t + f * (1 - t)) for c, f in zip((248, 247, 242), (21, 61, 46)))
    for line in wrap(d, slide.get("body", ""), bf, W - 160)[:7]:
        d.text((80, y), line, font=bf, fill=soft)
        y += 62
    small = font("Inter-Regular.otf", 30)
    d.text((80, H - band - 120), spec.get("source", ""), font=small, fill=WARM)
    d.text((80, H - band - 76), "General education only. Not financial advice.", font=small, fill=WARM)
    return img


def main(spec_path, out):
    spec = json.loads(Path(spec_path).read_text())
    text = " ".join(s["headline"] + " " + s.get("body", "") for s in spec["slides"])
    if BANNED.search(text):
        raise SystemExit(f"BLOCKED: prohibited wording ({BANNED.search(text).group(0)})")
    slides = spec["slides"] + [{"headline": spec.get("closing", "Learn. Understand. Stay Informed."),
                                "body": "Are you financially ready for tomorrow?", "seconds": 3}]
    with tempfile.TemporaryDirectory() as tmp:
        n = 0
        for slide in slides:
            frames = int(slide.get("seconds", 4) * FPS)
            for i in range(frames):
                frame(slide, spec, i / FPS).save(f"{tmp}/f{n:05d}.png")
                n += 1
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", f"{tmp}/f%05d.png",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "20", "-movflags", "+faststart", out],
                       check=True)
    print(json.dumps({"written": out, "seconds": sum(s.get("seconds", 4) for s in slides), "status": "silent draft: owner review required"}))


if __name__ == "__main__":
    main(*sys.argv[1:3])
