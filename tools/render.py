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
  "question": false,                                                         # signature question: ONLY when the topic is
                                                                             # preparedness (owner rule 27 Nov 2026); never a default
  "kicker": "MONEY BASICS",                                                  # optional top label; defaults per edition
  "blocks": [{"term": "Income", "text": "Money you receive over time, such as your pay."}],   # optional definitions
  "takeaway": "One clear takeaway in plain words.",                         # optional, highlighted
  "example": {"label": "Hypothetical example", "text": "..."},              # optional; label must say hypothetical/illustration
  "layout": "band" | "hero" | "split"                                        # optional, varies design
}
Owner template rules (27 Nov 2026): the headline is the actual topic (never a generic "explainer"); one clear takeaway on the
graphic; text large enough for a phone (body 30 px or more at 1080 px wide); any current statistic on the image must carry its
source and date on the image; hypothetical examples are labelled; the signature question appears at most once across image and
caption and only when the topic fits.
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
          "ready": "FINANCIAL EDUCATION"}
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


THEMES = {"forest": (FOREST, "#FFFFFF", WARM, GOLD), "charcoal": (CHARCOAL, "#FFFFFF", WARM, GOLD),
          "warm": (WARM, FOREST, CHARCOAL, "#8C7335")}


def render(spec, size, kind, shift=0):
    W, H = size
    bg, ink, soft, accent = THEMES[spec.get("theme", "forest")]
    img = Image.new("RGB", size, bg)
    d = ImageDraw.Draw(img)
    pad = 70 if W < 1500 else 90
    band_h = 230 if kind != "x" else 200
    # Warm-white logo band at the bottom (logo never on dark backgrounds).
    d.rectangle([0, H - band_h, W, H], fill="#FFFFFF" if bg == WARM else WARM)
    d.rectangle([0, H - band_h - 6, W, H - band_h], fill=GOLD)
    paste_logo(img, 420 if kind != "x" else 380, H - band_h, band_h)
    top = (90 if kind != "story" else 290) + shift  # story keeps key text clear of the top 250 px
    bottom_limit = H - band_h - (60 if kind != "story" else 330 - band_h if band_h < 330 else 40)
    text_w = W - 2 * pad
    # Series or topic label (never the signature question)
    d.text((pad, top), spec.get("kicker") or LABELS[spec["edition"]], font=font("Inter-SemiBold.otf", 30 if kind != "x" else 28), fill=accent)
    date_label = spec.get("dateLabel", spec["date"] if spec["edition"] != "ready" else None)
    if date_label:
        d.text((pad, top + 46), date_label, font=font("Inter-Regular.otf", 26), fill=soft)
    y = top + (120 if date_label else 90)
    d.rectangle([pad, y - 20, pad + 120, y - 14], fill=GOLD)
    head_font, head_lines = fit(d, spec["headline"], "InterDisplay-Bold.otf", 74 if kind != "x" else 64, 40, text_w,
                                4 if kind != "x" else 3)
    for line in head_lines:
        d.text((pad, y), line, font=head_font, fill=ink)
        y += int(head_font.size * 1.18)
    y += 30
    fig = spec.get("figure")
    if fig and kind != "x" or (fig and not spec.get("points")):
        if fig:
            d.text((pad, y), fig["value"], font=font("InterDisplay-Bold.otf", 150 if kind != "x" else 120), fill=accent)
            y += 170 if kind != "x" else 135
            lab_font, lab_lines = fit(d, fig["label"], "Inter-Regular.otf", 32, 22, text_w, 2)
            for line in lab_lines:
                d.text((pad, y), line, font=lab_font, fill=soft)
                y += int(lab_font.size * 1.3)
            y += 25
    for i, point in enumerate(spec.get("points", [])[:4], 1):
        p_font, p_lines = fit(d, point, "Inter-Regular.otf", 34 if kind != "x" else 30, 22, text_w - 60, 3)
        d.text((pad, y), f"{i}", font=font("Inter-Bold.otf", 36), fill=accent)
        for line in p_lines:
            d.text((pad + 60, y), line, font=p_font, fill=ink)
            y += int(p_font.size * 1.3)
        y += 14
    blocks = spec.get("blocks") or []
    for b in blocks:
        t_font = font("Inter-SemiBold.otf", 40 if kind != "x" else 34)
        d.text((pad, y), b["term"], font=t_font, fill=accent)
        y += int(t_font.size * 1.25)
        b_font, b_lines = fit(d, b["text"], "Inter-Regular.otf", 36 if kind != "x" else 32, 30, text_w, 3)
        for line in b_lines:
            d.text((pad, y), line, font=b_font, fill=ink)
            y += int(b_font.size * 1.3)
        y += 22 if kind != "x" else 12
    if spec.get("takeaway"):
        k_font, k_lines = fit(d, spec["takeaway"], "Inter-SemiBold.otf", 36 if kind != "x" else 32, 30, text_w - 30, 4)
        top_k = y
        for line in k_lines:
            d.text((pad + 30, y), line, font=k_font, fill=ink)
            y += int(k_font.size * 1.3)
        d.rectangle([pad, top_k + 4, pad + 8, y - 8], fill=GOLD)
        y += 20
    ex = spec.get("example")
    if ex and kind != "x":
        d.text((pad, y), ex["label"].upper(), font=font("Inter-SemiBold.otf", 26), fill=accent)
        y += 38
        e_font, e_lines = fit(d, ex["text"], "Inter-Regular.otf", 32, 30, text_w, 3)
        for line in e_lines:
            d.text((pad, y), line, font=e_font, fill=soft)
            y += int(e_font.size * 1.3)
        y += 20
    if spec.get("context") and kind != "x":
        c_font, c_lines = fit(d, spec["context"], "Inter-Regular.otf", 32, 22, text_w, 3)
        for line in c_lines:
            d.text((pad, y), line, font=c_font, fill=soft)
            y += int(c_font.size * 1.3)
        y += 20
    if spec.get("question"):
        q_font = font("Inter-SemiBold.otf", 38 if kind != "x" else 32)
        for line in wrap(d, SIGNATURE, q_font, text_w):
            d.text((pad, y), line, font=q_font, fill=accent)
            y += int(q_font.size * 1.3)
    # Source and disclosure just above the band
    s_font, s_lines = fit(d, spec["source"], "Inter-Regular.otf", 24, 16, text_w, 2)
    small = font("Inter-Regular.otf", 22)
    sy = H - band_h - 30 - 22 - len(s_lines) * 30 - (300 - band_h if kind == "story" else 0)
    if y > sy - 10:
        raise ValueError(f"{kind}: content overflows into the source line; shorten the text.")
    for line in s_lines:
        d.text((pad, sy), line, font=s_font, fill=soft)
        sy += 30
    d.text((pad, sy + 4), DISCLOSURE, font=small, fill=soft)
    img.content_end = y
    img.source_top = H - band_h - 30 - 22 - len(s_lines) * 30 - (300 - band_h if kind == "story" else 0)
    return img


def main(spec_path, outdir):
    spec = json.loads(Path(spec_path).read_text())
    text = " ".join(str(v) for v in [spec.get("headline"), spec.get("context"), spec.get("figure"), spec.get("points"), spec.get("source"),
                                     spec.get("blocks"), spec.get("takeaway"), spec.get("example")])
    if BANNED.search(text):
        raise SystemExit(f"BLOCKED: prohibited wording in image text ({BANNED.search(text).group(0)}).")
    if spec.get("figure") and not re.search(r"(19|20)\d\d", spec.get("source", "")):
        raise SystemExit("A current statistic on the image needs its source and date on the image (spec.source with a year).")
    ex = spec.get("example")
    if ex and not re.search(r"hypothetical|illustrat", ex.get("label", ""), re.I):
        raise SystemExit("Examples on the image must be labelled hypothetical or illustration.")
    if re.search(r"explainer", spec.get("headline", ""), re.I) and "financial education" in spec.get("headline", "").lower():
        raise SystemExit("Use the actual topic as the headline, not a generic 'explainer' title.")
    spec.setdefault("source", "Sources and dates are in the post text.")
    for key in ("edition", "date", "slug", "headline"):
        if not spec.get(key):
            raise SystemExit(f"Missing {key}")
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    base = f"{spec['date']}-{spec['edition']}-{spec['slug']}" + (f"-{spec['variant']}" if spec.get("variant") else "")
    sizes = [("feed", (1080, 1350)), ("x", (1600, 900))] + ([("story", (1080, 1920))] if spec["edition"] == "ready" else [])
    written = []
    for kind, size in sizes:
        path = out / f"{base}-{kind}.jpg"
        if path.exists():
            raise SystemExit(f"Refusing to overwrite {path}")
        img = render(spec, size, kind)
        if spec.get("date") == "card" or spec["edition"] == "ready":  # centre the content block in the free space
            start = 90 if kind != "story" else 290
            free = img.source_top - 40 - img.content_end
            if free > 60:
                img = render(spec, size, kind, shift=free // 2)
        img.save(path, "JPEG", quality=90, optimize=True)
        written.append(str(path))
    print(json.dumps({"written": written}))


if __name__ == "__main__":
    main(*sys.argv[1:3])
