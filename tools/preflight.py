#!/usr/bin/env python3
"""Local preflight for a scheduled Two Market Ledger social run. Prints JSON; exit code 0 only if every check passes.

  python3 tools/preflight.py SERIES            # morning | ready | evening
  python3 tools/preflight.py --lint FILE       # R10 / R02 wording check on a text file (exit 3 if held)
"""
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ["policy/FINANCIAL_CONTENT_RULES.md", "policy/FOUNDING_PRINCIPLES.md", "policy/AUTHORISATIONS.md",
            "policy/EDITORIAL_POLICY.md", "brand/LOGO_USAGE.md", "brand/tml-logo-primary.png", "ops/RUNBOOK.md",
            "ops/config.json", "ops/topic-cards.json", "tools/render.py",
            "fonts/Inter-Regular.otf", "fonts/Inter-SemiBold.otf", "fonts/Inter-Bold.otf", "fonts/InterDisplay-Bold.otf"]
MUST_CONTAIN = {"policy/FINANCIAL_CONTENT_RULES.md": ["FE-01", "R02", "R08"],
                "policy/FOUNDING_PRINCIPLES.md": ["STRICTLY NO FINANCIAL ADVICE", "R10"]}
HOLD_WORDS = re.compile(
    r"\b(buy now|sell now|don'?t miss out|once[- ]in[- ]a[- ]lifetime|guaranteed (returns?|profit|income)|risk[- ]free returns?|sure[- ]shot|"
    r"multibaggers?|penny stocks?|get[- ]rich|double your money|doubling (your )?money|overnight wealth|fast money|quick money|easy money|"
    r"become a millionaire|intraday|day trading|f&o|stock tips?|beat(ing)? the market|moonshot|to the moon|"
    r"(buy|sell|hold) (call|rating|signal|recommendation)|target price|price target|top \d+ (funds|stocks)|best (fund|stock|etf)s?|"
    r"safest (investment|etf|fund)s?)\b", re.I)


def lint(path):
    text = Path(path).read_text()
    hits = sorted({m.group(0).lower() for m in HOLD_WORDS.finditer(text)})
    print(json.dumps({"lint": "HOLD" if hits else "clear", "matches": hits}))
    return 3 if hits else 0


def main(series):
    checks = []
    def check(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})
    config = json.loads((ROOT / "ops/config.json").read_text())
    check("series known", series in config["series"], series)
    for rel in REQUIRED:
        p = ROOT / rel
        check(f"file {rel}", p.is_file() and p.stat().st_size > 0, hashlib.sha256(p.read_bytes()).hexdigest()[:12] if p.is_file() else "missing")
    for rel, needles in MUST_CONTAIN.items():
        text = (ROOT / rel).read_text() if (ROOT / rel).is_file() else ""
        check(f"content {rel}", all(n in text for n in needles), ",".join(n for n in needles if n not in text) or "ok")
    try:
        from PIL import Image
        logo = Image.open(ROOT / "brand/tml-logo-primary.png")
        check("logo decodes", logo.size[0] >= 1000 and logo.mode in ("RGBA", "LA"), f"{logo.size} {logo.mode}")
    except Exception as error:  # noqa: BLE001
        check("logo decodes", False, str(error))
    cards = json.loads((ROOT / "ops/topic-cards.json").read_text())["topics"]
    edition = series if series in ("morning", "ready", "evening") else "morning"
    kinds = ["feed", "x"] + (["story"] if edition == "ready" else [])
    missing = [f"card-{edition}-{t}-{k}.jpg" for t in cards for k in kinds if not (ROOT / "images/cards" / f"card-{edition}-{t}-{k}.jpg").is_file()]
    check("topic cards present", not missing, f"{len(cards)} topics" if not missing else ",".join(missing[:5]))
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import render
        with tempfile.TemporaryDirectory() as tmp:
            spec = {"edition": edition, "date": "2000-01-01", "slug": "preflight", "headline": "Preflight render test",
                    "context": "Branding check.", "source": "Source: preflight", "question": edition == "ready"}
            Path(tmp, "s.json").write_text(json.dumps(spec))
            render.main(str(Path(tmp, "s.json")), tmp)
            check("image renderer", len(list(Path(tmp).glob("*.jpg"))) == len(kinds), "rendered")
    except SystemExit as error:
        check("image renderer", False, str(error))
    except Exception as error:  # noqa: BLE001
        check("image renderer", False, repr(error))
    ok = all(c["ok"] for c in checks)
    print(json.dumps({"preflight": "PASS" if ok else "FAIL", "series": series,
                      "failed": [c for c in checks if not c["ok"]], "checked": len(checks)}))
    return 0 if ok else 2


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--lint":
        sys.exit(lint(sys.argv[2]))
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
