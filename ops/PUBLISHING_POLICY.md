# Two Market Ledger: authoritative daily publishing policy (v2, 28 November 2026)

**Owner instruction, 28 Nov 2026.** This is the single publishing policy for the three daily editions (9:30 AM Morning, 3:15 PM Ready/Education, 7:30 PM Evening; Australia/Melbourne, every day including weekends and public holidays). It replaces every earlier rule that holds, drafts or skips an edition merely because fresh news is unavailable. Where any other file conflicts with this one, **this file wins** (the founding principles and `policy/FINANCIAL_CONTENT_RULES.md` compliance rules still apply in full). "The edition is complete when it is scheduled or published to Instagram, Facebook and X **and its status is verified**; a draft is not completion."

## 1. Content ladder (move down automatically; never HOLD an edition for lack of news)
| Tier | Content | Label and wording |
|---|---|---|
| A | Latest verified news: a primary release or announcement from the last 24 hours (Morning: since the previous Evening edition) | "News"; may say new/latest/today only for tier A |
| B | A verified development from the previous 24–72 hours that is still relevant, **dated** | Date in the first line; "In case you missed it" / "Background"; never "breaking" or "today" |
| C | Market summary or weekly economic developments (official releases from the week; no index or share price levels as the centrepiece; no Indian securities prices) | "This week" with each item's release date |
| D | Verified educational explainer or financial-literacy content (fresh topic from verified facts, or an owner-authorised evergreen item from the reserve) | "EDUCATIONAL EXPLAINER" (Morning/Evening) or "Education edition" (3:15 PM) |

- Choose the highest tier with **one fully verified item**. If tier A is not verified within the research budget (section 4), take B, then C, then D. D is always available, so an edition is never empty.
- One failed fact drops **that item** and the run moves down the ladder. The edition is not held. A whole edition is held only if every ladder item would breach a compliance rule (practically never) or the channel or Buffer cannot publish after bounded recovery (section 5).
- Do not repeat an earlier edition's story the same day. No educational subject repeats within 21 days unless there is new official data.
- Never describe tier B, C or D as news, breaking or current. Never publish outdated information as current. Never publish inaccurate information to meet a schedule: drop the item, not the edition.

## 2. Authorisation (founder, 28 Nov 2026)
- Educational explainers (tier D, including the evergreen bank `content/evergreen/`) are authorised for **automatic publishing without further manual approval**, provided every factual, branding and compliance check passes. Any figure is verified on a primary source this run or is plain arithmetic labelled "our calculation"; a derived number is never attributed to the source.
- Tier A/B/C follow FE-01 (`policy/AUTHORISATIONS.md`): every factual claim confirmed on the primary page, neutral and educational.
- Still never published: financial advice; personalised plans; buy, sell or hold calls; trading signals; product, stock, ETF, fund, super, loan or insurance recommendations or rankings; price targets; quick-money, trading or speculation framing; guaranteed returns; unverified predictions presented as facts; private family or user information; fear or urgency framing; political bias.

## 3. Research sources (`content/research/sources.json` is the structured list)
Official first, then corroborate: Australia (ABS, RBA, Treasury, ASX announcements, ASIC); India (RBI, SEBI, Ministry of Finance/PIB, MoSPI, BSE and NSE announcements only, no price data); United States (Federal Reserve, BEA, BLS) and global (IMF, World Bank, OECD); then reputable news (corroboration and context only). Distinguish fact, forecast, history and opinion; state each fact's release date and period.
**Blocked sources:** if a page or PDF is blocked (bot check, domain not allowed, timeout), record it in the daily research file as `blocked` and move to the next source in the same region. **Never retry a blocked source in the same run** and do not try workarounds.

## 4. Credit-saving workflow (mandatory)
- **No parallel agents and no deep research.** One run, one thread. Do not use the Agent tool except a single `web-fetch` call per primary page where no other fetch tool exists, **maximum 4 page fetches per run** (plus at most 2 web searches for discovery). Expand beyond the essentials only if tier A has no candidate, never above that cap.
- **Order:** (1) read the shared daily research file; (2) check the official release calendar for what was due since the last edition; (3) fetch only the pages for the best candidate; (4) decide the tier.
- **Shared daily research file:** the Project file `claude/ledger-daily/research.md` (Projects tool; if unavailable, Buffer history is the record). One table row per verified fact: date, region, publisher, URL, fact, figure and unit, period, release date, retrieved at, tier, editions that used it. All three editions and any website item **read it first and reuse verified rows** instead of re-fetching: a fact verified this week with a release date inside its tier window needs no re-fetch (say "verified <date>"). Estimates and revision-prone figures are re-fetched if older than 24 hours.
- **Preflight once per run** (`python3 tools/preflight.py <series>`); do not repeat it and do not re-run the lint on unchanged text. Lint the final text once.
- **Reusable assets:** branded topic cards (`images/cards/`, any topic, any edition, three variants) and the text templates in `ops/templates/`. No new image rendering for ordinary posts; WhatsApp image only for the 3:15 PM edition.
- **Bounded retries:** a failed operation is retried at most once, after checking whether it actually succeeded. No loops, no repeated failed fetches.
- **Lower-cost models** for routine tasks where the platform supports it; the three routines run on Sonnet 5.5 (not Opus). Verification quality comes first: use a cheaper model only after the owner agrees it did not reduce accuracy.
- **Reserve:** keep at least **7 unused approved evergreen items** (tier D) with their cards; an interactive session replenishes it weekly (Sunday report shows the count).
- Target: a normal run finishes in about 15 tool turns and one thread.

## 5. Publishing, verification and recovery
1. Create each channel's post (Instagram, Facebook, X) once: `customScheduled` at the publish time before it; `shareNow` from the publish time until the series `lastCatchUp`. **Past `lastCatchUp`, a tier A or B news edition is not published late; the same run drops to C/D, which are not time-sensitive and may still be published as a "late edition" until the next edition's slot.**
2. Before creating, check `list_posts` (last 24 h, all statuses) for the same series label or publish-window duplicate; never create a duplicate. Draft leftovers of today's own edition are converted or deleted.
3. `get_post` every post: status `scheduled` or `sent` with no error. Anything else: **one** bounded recovery (check for duplicates, fix the cause, recreate once), then verify again.
4. Notify the owner (SendUserMessage) **only** for a genuine technical, factual, compliance or authorisation issue that still stands after recovery (lost channel authentication, plan limit, Buffer outage, all ladder tiers failed). Routine success is silent (except the Evening daily report and the 3:15 PM WhatsApp image).
5. Other approved channels run on their own schedules and are not touched by these runs: YouTube (VPS worker, private-only until approved), Instagram/Facebook Reels, TikTok (manual), WhatsApp status (manual).

## 6. Website
The public website's news and education feed is produced by the VPS news engine (`ops/news` in the website repository), currently running on the protected beta only. The social routines **reuse the same verified facts** (the research file) but do not edit the site and never touch private My Ledger data, savings plans, holdings or portfolios. Updating the production public site is a separate owner-approved deployment (see PUBLIC_LAUNCH_READINESS.md in the website repository).

## 7. Records
One row per edition in the series log (outcome, tier used, ladder reason, card, sources, post IDs and statuses) and in `content/history.json` when an interactive session reconciles. Misses go to `ops/MISSED_EDITIONS_LOG.md`.
