# Scheduled run procedure: Two Market Ledger social editions (v2, 28 Nov 2026)

**Authority:** `ops/PUBLISHING_POLICY.md` is the single publishing policy; it overrides anything here or in `ops/series/*.md` that conflicts. Read in this order, once: `.claude/skills/tml-social-media/SKILL.md` (v1.0 plus the 28 Nov owner decision), `ops/PUBLISHING_POLICY.md`, this file, `ops/series/<series>.md`. The founding principles (`policy/FOUNDING_PRINCIPLES.md`) and `policy/FINANCIAL_CONTENT_RULES.md` compliance rules apply in full.

Never: post to LinkedIn or any channel other than the three in `ops/config.json`; personal profiles; purchase anything or change Buffer or channel settings; modify other scheduled tasks or any other repository; publish private family/user investment information or paid materials; use photos, third-party graphics, regulator logos or images of real people; touch private My Ledger data.

**Goal of every run: the edition is scheduled or published on Instagram, Facebook and X, and its status verified. A draft is not completion.** Be lean: one thread, no parallel agents, at most 4 page fetches (PUBLISHING_POLICY §4).

## 0. Time and mode
- `mcp__Buffer__get_account` → `currentTime` (Melbourne, with offset). Today = that date.
- **DRY RUN** only if the task message contains "MODE: DRY RUN": every post is `saveToDraft: true` and starts `TEST DRAFT — DO NOT PUBLISH —`; no notification.
- **Deadlines:** the post is scheduled (`customScheduled`) for the series `publish` time, or `shareNow` between `publish` and `lastCatchUp`. After `lastCatchUp` news tiers A/B are not published late; use tier C/D (not time-sensitive) and publish it as a late edition (never another day's news).

## 1. Setup (once per run, no repeats)
1. `git clone --depth 1 https://github.com/sklohtia-manager/tml-social-media /home/claude/tml` (on failure retry twice, 20 s apart; if it still fails, notify once with the exact error and stop).
2. `python3 /home/claude/tml/tools/preflight.py <series>` once. A `FAIL` of the policy files, logo, renderer or cards: notify the exact failed check and stop. Do not repeat the preflight.
3. Read `ops/config.json`, `content/history.json` (never repost the introduction videos or episodes; no educational subject within 21 days) and `ops/EDITORIAL_CALENDAR.md` (today's planned theme).
4. `list_posts` for the three channels, last 14 days, all statuses: this is the guaranteed history (topics, cards, IDs) and the duplicate check. A post of this series already exists on a channel if one is scheduled or sent within 45 minutes of the series' publish time today, or its text carries the series label or a `legacyMarkers` entry (`#TMLEducation` does not count; ignore `TEST DRAFT`). Then create nothing on that channel. A leftover draft of today's own edition is converted or deleted, never left as a duplicate.
5. `list_channels`: Instagram, Facebook and X must be connected and unlocked (retry once after 60 s on an API error). A channel that is still disconnected or locked is skipped and the owner is notified ("authentication lost: <channel>").
6. Read the shared research file (`claude/ledger-daily/research.md`, Projects tool). Reuse its verified rows. If the Projects tool is unavailable, continue; Buffer history is the record.
7. **Previous edition cross-check (one line, no extra research):** from the Buffer history classify the previous slot PUBLISHED / DELAYED / FAILED / MISSED. For anything else, update the log and `ops/MISSED_EDITIONS_LOG.md` when you can. Never replay stale news.

## 2. Choose the content (PUBLISHING_POLICY §1 ladder)
- Tier A news → B dated 24–72 h → C weekly/market summary → D educational explainer. Take the highest tier with one fully verified item and stop researching.
- Research budget: read the research file; check what official releases were due; fetch only the candidate's primary page(s), maximum 4 fetches, plus at most 2 web searches. A blocked page is recorded as `blocked` and skipped for the run; no retries or workarounds.
- Freshness: only tier A may say new/latest/today (primary release within 24 h; Morning: since the previous Evening). Every item states its release date. Distinguish fact, forecast, history and opinion; a derived figure is labelled "our calculation".
- Tier D: use an owner-authorised evergreen item from `content/evergreen/` not used in the last 30 days, or write a short explainer on the day's calendar theme using `ops/templates/explainer.md` (facts only if verified; otherwise concept text with no statistics). Evergreen items are authorised for automatic publishing (28 Nov owner instruction).
- Append each verified fact you used to the research file (once, one row per fact).

## 3. Compliance gate (once, on the final text)
- Write the final texts to `/tmp/post.txt` and run `python3 /home/claude/tml/tools/preflight.py --lint /tmp/post.txt` once. Exit 3 means rewrite or drop **that item and move down the ladder**; it never holds the whole edition.
- BLOCK (rewrite or drop): recommendations, rankings or steers on any product, fund, stock, ETF, super, loan, insurance, gold, crypto, property or asset class; buy/sell/hold calls, targets, signals or forecasts for named securities; guaranteed returns; trading, speculation, fast-money framing (R10); personalised advice; fear, urgency, sensationalism or political bias; private family information.
- Drop-the-item triggers (then use the next tier): a claim not confirmed on a primary page, share prices or index levels as the centre, Indian securities prices, rumours, causation the source does not state, data-rights doubt, a politically sensitive topic.

## 4. Images
- Choose the topic key in `ops/topic-cards.json` whose title accurately describes the post (there is no generic "explainer" card: the legacy `card-*-explainer-*` files are retired and must not be used). Three variants per topic (`""` forest, `-v2` charcoal, `-v3` warm white); use the variant not used longest; never the same topic+variant twice in 7 days in any series.
- URLs: `https://raw.githubusercontent.com/sklohtia-manager/tml-social-media/main/images/cards/card-<edition>-<topic><variant>-feed.jpg` (Instagram, Facebook) and `…-x.jpg` (X), where `<edition>` is `morning`, `ready` or `evening`. Confirm both files exist in the clone. altText: "Two Market Ledger <series label> card: <topic title>. General education only."
- Do not upload or render other images (scheduled runs cannot push to GitHub). A missing card: choose the next closest accurate topic; only if none fits, notify.

## 5. Publish
- Instagram: feed image (with altText), `metadata.instagram {type:"post", shouldShareToFeed:true}`, `schedulingType:"automatic"`. Facebook: its own post, `metadata.facebook.type:"post"`, feed image. X: X image; **at most 280 characters counting the real length of any link** (Buffer rejected a 304-character post; count with code, leave the link only if the whole text fits).
- Create each channel independently; one failure never stops the others.
- Post text per `ops/series/<series>.md`, `ops/templates/explainer.md` and the post template rules in `ops/series/ready.md` (signature line only where it fits; `#TMLEducation` standard).
- Plan limit (10 scheduled posts): one `shareNow` instead of scheduling; otherwise notify.

## 6. Verify, recover, notify
- `get_post` each post: `scheduled` or `sent`, no error. Not so: **one** recovery (check `list_posts` for a duplicate first; fix the cause; recreate once), then verify again.
- Duplicate self-check: exactly one post of this series per channel today. If two, delete nothing and notify with both IDs.
- Manual/native posts (`via: "network"`) are logged as MANUAL and never reposted.
- **Notify the owner only for a genuine technical, factual, compliance or authorisation issue that still stands after recovery.** State the problem, what was tried and the action needed. Routine success is silent (except the Evening daily report and the 3:15 PM WhatsApp image).
- Final response: tier used and why, headline, per-channel post IDs and statuses, image URLs, sources with dates.

## 7. Log
`project_read` then `project_write` the series log: one row per date and edition (update, never duplicate): date; edition; outcome (PUBLISHED, SCHEDULED, DELAYED, FAILED, MISSED, DRY-RUN, SKIPPED-DUPLICATE); **tier used (A/B/C/D) and reason**; headline; topic; card; sources with release dates; classification; post IDs with statuses; notes. Keep the latest 120 rows. The log and Buffer history are the memory between runs.
