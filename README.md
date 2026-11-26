# tml-social-media

The central source of truth for Two Market Ledger's automated social media: three daily editions on Facebook, Instagram and X, via Buffer.

| Path | Purpose |
|---|---|
| `ops/RUNBOOK.md` | Procedure every scheduled run follows: preflight, research, compliance, images, publishing, logs |
| `ops/series/*.md` | Instructions for The Ledger Morning (9:30 AM), Are You Financially Ready for Tomorrow? (3:15 PM) and The Ledger Evening Recap (7:30 PM), Melbourne time |
| `ops/config.json` | Buffer organisation and channel IDs, schedule, cut-offs, log locations |
| `policy/` | Approved rules: financial content rules (incl. FE-01), founding principles, publishing authorisations, editorial policy excerpt |
| `brand/` | Approved logo and usage rules |
| `tools/render.py` | Deterministic branded image renderer (Pillow) |
| `tools/preflight.py` | Preflight checks and R10/R02 wording lint |
| `images/cards/` | Pre-rendered branded topic cards used as post images (public URLs for Buffer) |
| `images/YYYY/MM/` | Edition images rendered in interactive sessions |
| `fonts/` | Inter (SIL Open Font License, `fonts/OFL.txt`) |

This repository is **public** (Buffer must download images from it). It contains only published-content rules, branding and tooling: no credentials, no private family or investment information, no paid materials.

Two Market Ledger provides general education and information only. It is not financial product advice.
