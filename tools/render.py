#!/usr/bin/env python3
"""Two Market Ledger branded image renderer (deterministic, Pillow only).

Usage: python3 tools/render.py spec.json OUTDIR
spec = {
  "edition": "morning" | "ready" | "evening",
  "date": "2026-11-26",
  "slug": "inflation-october",
  "headline": "Australia's annual inflation rose to 4.9% in October",
  "figure": {"value": "4.9%", "label": "CPI, 12 months to October 2026"},   # optional
  "points": ["...", "..."],                                                  # optional (evening, 2-4)
  "context": "One short sentence of context.",                              # optional
  "source": "Source: ABS, Consumer Price Index, Australia, October 2026 (released 25 Nov 2026)",
  "question": true,                                                          # adds the signature question
  "layout": "band" | "hero" | "split"                                        # optional, varies design
}
Writes <date>-<edition>-<slug>-feed.jpg (1080x1350), -x.jpg (1600x900) and, for the ready series, -story.jpg (1080x1920).
Uses the approved logo brand/tml-logo-primary.png on a warm-white band only (brand/LOGO_USAGE.md).
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FOREST, CHARCOAL, GOLD, WARM = "#153D2E", "#202622", "#B89A55", "#F8F7F2"
LABELS = {"morning": "THE LEDGER MORNING", "evening": "THE LEDGER EVENING RECAP",
          "ready": "ARE YOU FINANCIALLY READY FOR TOMORROW?"}
DISCLOSURE = "General education only. Not financial advice."
SIGNATURE = "Are you financially ready for tomorrow?"
BANNED = re.compile(r"\b(buy now|sell now|don't miss out|once[- ]in[- ]a[- ]lifetime|guaranteed|sure[- ]shot|multibagger|"
                    r"penny stock|get[- ]rich|double your money|fast money|quick money|easy money|intraday|day trading|"
                    r"stock tips?|beat the market|moonshot|millionaire)\b", re.I)


def font(name, size):
    return ImageFont.truetype(str(ROOT / "fonts" / name), size)


def wrap(draw, text, fnt, width):
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def fit(draw, text, name, start, minimum, width, max_lines):
    size = start
    while size >= minimum:
        fnt = font(name, size)
        lines = wrap(draw, text, fnt, width)
        if len(lines) <= max_lines:
            return fnt, lines
        size -= 2
    raise ValueError(f"Text does not fit: {text[:60]}...")


def paste_logo(canvas, box_w, y, band_h):
    logo = Image.open(ROOT / "brand" / "tml-logo-primary.png").convert("RGBA")
    width = max(360, min(480, box_w))
    height = round(logo.height * width / logo.width)
    if height > band_h - 40:
        height = band_h - 40
        width = round(logo.width * height / logo.height)
    logo = logo.resize((width, height), Image.LANCZOS)
    canvas.paste(logo, ((canvas.width - width) // 2, y + (band_h - height) // 2), logo)


def render(spec, size, kind, shift=0):
    W, H = size
    img = Image.new("RGB", size, FOREST)
    d = ImageDraw.Draw(img)
    pad = 70 if W < 1500 else 90
    band_h = 230 if kind != "x" else 200
    # Warm-white logo band at the bottom (logo never on dark backgrounds).
    d.rectangle([0, H - band_h, W, H], fill=WARM)
    d.rectangle([0, H - band_h - 6, W, H - band_h], fill=GOLD)
    paste_logo(img, 420 if kind != "x" else 380, H - band_h, band_h)
    top = (90 if kind != "story" else 290) + shift  # story keeps key text clear of the top 250 px
    bottom_limit = H - band_h - (60 if kind != "story" else 330 - band_h if band_h < 330 else 40)
    text_w = W - 2 * pad
    # Series label
    d.text((pad, top), LABELS[spec["edition"]], font=font("Inter-SemiBold.otf", 30 if kind != "x" else 28), fill=GOLD)
    d.text((pad, top + 46), spec.get("dateLabel", spec["date"]), font=font("Inter-Regular.otf", 26), fill=WARM)
    y = top + 120
    d.rectangle([pad, y - 20, pad + 120, y - 14], fill=GOLD)
    head_font, head_lines = fit(d, spec["headline"], "InterDisplay-Bold.otf", 74 if kind != "x" else 64, 40, text_w,
                                4 if kind != "x" else 3)
    for line in head_lines:
        d.text((pad, y), line, font=head_font, fill="#FFFFFF")
        y += int(head_font.size * 1.18)
    y += 30
    fig = spec.get("figure")
    if fig and kind != "x" or (fig and not spec.get("points")):
        if fig:
            d.text((pad, y), fig["value"], font=font("InterDisplay-Bold.otf", 150 if kind != "x" else 120), fill=GOLD)
            y += 170 if kind != "x" else 135
            lab_font, lab_lines = fit(d, fig["label"], "Inter-Regular.otf", 32, 22, text_w, 2)
            for line in lab_lines:
                d.text((pad, y), line, font=lab_font, fill=WARM)
                y += int(lab_font.size * 1.3)
            y += 25
    for i, point in enumerate(spec.get("points", [])[:4], 1):
        p_font, p_lines = fit(d, point, "Inter-Regular.otf", 34 if kind != "x" else 30, 22, text_w - 60, 3)
        d.text((pad, y), f"{i}", font=font("Inter-Bold.otf", 36), fill=GOLD)
        for line in p_lines:
            d.text((pad + 60, y), line, font=p_font, fill="#FFFFFF")
            y += int(p_font.size * 1.3)
        y += 14
    if spec.get("context") and kind != "x":
        c_font, c_lines = fit(d, spec["context"], "Inter-Regular.otf", 32, 22, text_w, 3)
        for line in c_lines:
            d.text((pad, y), line, font=c_font, fill=WARM)
            y += int(c_font.size * 1.3)
        y += 20
    if spec.get("question"):
        q_font = font("Inter-SemiBold.otf", 38 if kind != "x" else 32)
        for line in wrap(d, SIGNATURE, q_font, text_w):
            d.text((pad, y), line, font=q_font, fill=GOLD)
            y += int(q_font.size * 1.3)
    # Source and disclosure just above the band
    s_font, s_lines = fit(d, spec["source"], "Inter-Regular.otf", 24, 16, text_w, 2)
    small = font("Inter-Regular.otf", 22)
    sy = H - band_h - 30 - 22 - len(s_lines) * 30 - (300 - band_h if kind == "story" else 0)
    if y > sy - 10:
        raise ValueError(f"{kind}: content overflows into the source line; shorten the text.")
    for line in s_lines:
        d.text((pad, sy), line, font=s_font, fill=WARM)
        sy += 30
    d.text((pad, sy + 4), DISCLOSURE, font=small, fill=WARM)
    img.content_end = y
    img.source_top = H - band_h - 30 - 22 - len(s_lines) * 30 - (300 - band_h if kind == "story" else 0)
    return img


def main(spec_path, outdir):
    spec = json.loads(Path(spec_path).read_text())
    text = " ".join(str(v) for v in [spec.get("headline"), spec.get("context"), spec.get("figure"), spec.get("points"), spec.get("source")])
    if BANNED.search(text):
        raise SystemExit(f"BLOCKED: prohibited wording in image text ({BANNED.search(text).group(0)}).")
    spec.setdefault("source", "Sources and dates are in the post text.")
    for key in ("edition", "date", "slug", "headline"):
        if not spec.get(key):
            raise SystemExit(f"Missing {key}")
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    base = f"{spec['date']}-{spec['edition']}-{spec['slug']}"
    sizes = [("feed", (1080, 1350)), ("x", (1600, 900))] + ([("story", (1080, 1920))] if spec["edition"] == "ready" else [])
    written = []
    for kind, size in sizes:
        path = out / f"{base}-{kind}.jpg"
        if path.exists():
            raise SystemExit(f"Refusing to overwrite {path}")
        img = render(spec, size, kind)
        if spec.get("date") == "card":  # topic cards: centre the content block in the free space
            start = 90 if kind != "story" else 290
            free = img.source_top - 40 - img.content_end
            if free > 60:
                img = render(spec, size, kind, shift=free // 2)
        img.save(path, "JPEG", quality=90, optimize=True)
        written.append(str(path))
    print(json.dumps({"written": written}))


if __name__ == "__main__":
    main(*sys.argv[1:3])
