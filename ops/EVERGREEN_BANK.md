# Ready for Tomorrow: evergreen education bank (7 days)

Prepared 27 Nov 2026. **All seven need the owner's approval before use** (set `approval.owner` to true with `approvedBy` and `approvedAt` in each file, or tell Claude "approve evergreen E01–E07"). Any edit after approval invalidates it.

Files: `content/evergreen/ready/E01.json` … `E07.json`. Each has Facebook, Instagram and X captions and uses an existing branded topic card (charcoal variant `-v2`, already hosted).

| ID | Title | Card | Facts used |
|---|---|---|---|
| E01 | Financial resilience starts with a buffer | resilience-v2 | none (concept) |
| E02 | What inflation does to a fixed amount of money | inflation-v2 | arithmetic only: 3% a year assumed, $100 → $97.09 after 1 year, $74.41 after 10 |
| E03 | Knowing where the money goes | cost-of-living-v2 | none |
| E04 | Thinking beyond property | beyond-property-v2 | none |
| E05 | Why other economies matter at home | trade-v2 | none (general mechanism) |
| E06 | Time is the quiet part of every plan | retirement-v2 | arithmetic only: $50 × 52 × 10 = $26,000; × 20 = $52,000, no growth assumed |
| E07 | Income can change; preparation helps | jobs-wages-v2 | none |

All seven pass `tools/preflight.py --lint`. They carry no current statistics, so they cannot go out of date, and each is labelled **"education edition"**, never news.

## When they are used
- **Only for the 3:15 PM Ready for Tomorrow slot**, and only when that day's edition cannot be produced or verified. Morning and Evening are news; their fallback is a held draft plus an owner alert, never a substitute post.
- Each item is used at most once in 30 days. The owner is always notified when one is used.
- The bank is replenished so that at least 7 unused approved items are always available. The Sunday report shows how many remain.
