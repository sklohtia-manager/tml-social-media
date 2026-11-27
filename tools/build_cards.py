#!/usr/bin/env python3
"""Rebuild the pre-rendered branded topic cards from ops/topic-cards.json (owner template rules, 27 Nov 2026).

Cards carry the actual topic as the headline and one plain takeaway. No statistics (so they never go stale), no
signature question. Usage: python3 tools/build_cards.py [--only <topic>]  (overwrites images/cards/card-*.jpg)
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import render  # noqa: E402

VARIANTS = {"": "forest", "-v2": "charcoal", "-v3": "warm"}


def main(only=None):
    cfg = json.loads((ROOT / "ops/topic-cards.json").read_text())
    out = ROOT / "images" / "cards"
    written = 0
    for topic, entry in cfg["topics"].items():
        if only and topic != only:
            continue
        title, line = entry[0], entry[1]
        kicker = entry[2] if len(entry) > 2 else None
        for edition in ("morning", "ready", "evening"):
            for suffix, theme in VARIANTS.items():
                spec = {"edition": edition, "date": "card", "dateLabel": "", "slug": topic, "headline": title, "takeaway": line,
                        "theme": theme, "source": "Sources and dates are in the post text."}
                if kicker and edition == "ready":
                    spec["kicker"] = kicker
                with tempfile.TemporaryDirectory() as tmp:
                    Path(tmp, "s.json").write_text(json.dumps(spec))
                    render.main(str(Path(tmp, "s.json")), tmp)
                    for f in Path(tmp).glob("card-*.jpg"):
                        kind = f.stem.rsplit("-", 1)[1]
                        dest = out / f"card-{edition}-{topic}{suffix}-{kind}.jpg"
                        dest.write_bytes(f.read_bytes())
                        written += 1
    print(json.dumps({"written": written}))


if __name__ == "__main__":
    main(sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--only" else None)
