# Educational explainer templates (tier D; authorised for automatic publishing, 28 Nov 2026)

Use for any edition when no fresher tier is verified, or for the 3:15 PM education slot. Always labelled; never presented as news. The model design is `ops/MODEL_EXPLAINER.md`.

## Choosing the content
1. First choice: the next unused owner-authorised item in `content/evergreen/ready/` (E01 onward; not used in the last 30 days per the log and Buffer history; no subject repeated within 21 days). Use its captions unchanged except the label line below.
2. Otherwise write a fresh explainer on the day's calendar theme (`ops/EDITORIAL_CALENDAR.md`). Facts only if verified on a primary page this run (or read from the research file with their release date); otherwise concept text with no statistics. Hypothetical arithmetic is labelled "Hypothetical example" and checked in code. A derived number is labelled "our calculation", never attributed to the source.

## Label and edition swap
| Edition | Label line (first line of Facebook; start of X) | Card edition | Hashtags |
|---|---|---|---|
| Morning 9:30 | `THE LEDGER MORNING \| EDUCATIONAL EXPLAINER (background, not today's news)` | `card-morning-<topic><variant>-…` | #TwoMarketLedger #TheLedgerMorning #TMLEducation |
| Ready 3:15 | `FINANCIAL EDUCATION · Education edition` | `card-ready-<topic><variant>-…` | #TwoMarketLedger #TMLEducation |
| Evening 7:30 | `THE LEDGER EVENING \| EDUCATIONAL EXPLAINER (background, not today's news)` | `card-evening-<topic><variant>-…` | #TwoMarketLedger #TheLedgerEvening #TMLEducation |
Cards exist for every topic in `ops/topic-cards.json` and every edition (three variants). Pick the topic whose title accurately describes the post; never the retired generic `explainer` cards.

## Text structure (all channels adapted, never identical)
- **Hook:** one specific, factual line on why it matters to a household. No clickbait.
- **Facebook (100–200 words):** label line, title, 3 short paragraphs (definition → how it works → hypothetical example or verified figure with its release date), the takeaway, source URL where a source is used, "Learn. Understand. Stay Informed.", hashtags, "For information and education only. Not financial advice."
- **Instagram:** hook, numbered points 1–3, "Save this" takeaway line, source named (no link), "Education only. Not financial advice.", 5–8 hashtags.
- **X (max 280 characters counting the real link length, checked in code):** one idea, label, "Education only, not advice.", at most 2 hashtags, link only if the whole text fits.
- Signature line "Are you financially ready for tomorrow?" only where the topic fits preparedness or planning ahead (once, second-last body line, with lead-in and closing; with #AreYouFinanciallyReady).

## Checks before publishing (all must pass; if one fails, fix or choose another item, do not hold)
- [ ] Labelled as an explainer/education edition; no "today", "breaking", "latest".
- [ ] Every figure verified on a primary page (with release date) or labelled hypothetical/our calculation; arithmetic recomputed in code.
- [ ] No advice, recommendation, ranking, product steer, prediction presented as fact, or trading/fast-money framing; lint clear.
- [ ] Branding: green-and-gold topic card with the TML logo; accurate card title; alt text; disclosure; "Learn. Understand. Stay Informed."
- [ ] X ≤ 280 characters; Facebook and Instagram captions differ.
- [ ] Not a repeat of a subject used in the last 21 days; no duplicate post today.
