# Ready for Tomorrow: evergreen education bank (7 days)

Prepared 27 Nov 2026; expanded to **14 items (E01–E14) on 28 Nov 2026**. **Authorised for automatic publishing** by the owner's 28 Nov 2026 instruction (educational explainers publish automatically when factual, branding and compliance checks pass); each file's `approval` block records this. Any text edit invalidates the approval until the checks are re-run. Usable in **any edition** (Morning, Ready, Evening) via the label and card swap in `ops/templates/explainer.md`.

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
| E08 | Interest rates and the household budget | interest-rates-v2 | none (concept) |
| E09 | What exchange rates do to a cross-border budget | currency-v2 | hypothetical: A$200 at 50 vs 55 rupees = 10,000 vs 11,000 |
| E10 | Why economic history is worth knowing | economic-history-v2 | none |
| E11 | Housing costs in a household budget | housing-v2 | hypothetical: $1,500 / $5,000 = 30% |
| E12 | Reading an energy bill | energy-v2 | hypothetical: 600 units × 30c = $180 |
| E13 | Spreading out education costs | education-costs-v2 | hypothetical: $8,000 × 4 = $32,000 |
| E14 | Gross pay, tax and take-home pay | budget-tax-v2 | hypothetical: $1,000 gross → $800 take-home |

All seven pass `tools/preflight.py --lint`. They carry no current statistics, so they cannot go out of date, and each is labelled **"education edition"**, never news.

## When they are used (PUBLISHING_POLICY.md §1, tier D)
- Any edition, whenever no fresher tier (A news, B dated 24–72 h, C weekly summary) has a fully verified item. Always labelled as an explainer or education edition, never as news.
- Each item is used at most once in 30 days. A routine fallback is recorded in the log; the owner is notified only if something is wrong.
- **Rolling reserve:** at least 7 unused approved items must always be available. An interactive session replenishes it weekly; the Sunday report shows how many remain (14 on 28 Nov 2026, none used yet).

## Signature line (owner decision, 27 Nov 2026)
The approved line "Are you financially ready for tomorrow?" is used once, near the end with a lead-in and a short closing, only where the topic fits: **E01** (financial resilience), **E06** (time and long-term plans) and **E07** (preparing for change). E02–E05 close on their own takeaway.
