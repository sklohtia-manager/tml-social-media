# Scheduled run procedure: Two Market Ledger social editions

This repository is the source of truth. Every scheduled run first reads `.claude/skills/tml-social-media/SKILL.md` (the owner's permanent social media operating policy), then follows this file and `ops/series/<series>.md`. The skill's proposals that need owner approval (new schedule, new platforms, VPS worker, video release) do not change this procedure until they are approved. The founding principles (`policy/FOUNDING_PRINCIPLES.md`) override everything. **If uncertain, HOLD.**

Never: post to LinkedIn or any channel other than the three in `ops/config.json`; post to personal profiles; purchase anything or change Buffer or channel settings; modify other scheduled tasks or any other repository; publish private family investment information or paid materials; use photos, third-party graphics, regulator logos or images of real people.

## 0. Time and mode
- Run `mcp__Buffer__get_account` and take `currentTime` (Melbourne, with offset). Today = that date.
- **No catch-up:** if the current time is after the series' `lastCatchUp`, create today's edition as Buffer **drafts only** (never scheduled, never published), log it as "missed — draft only (no catch-up)", and notify the founder once. Never publish another day's content, and never publish a missed edition the next day.
- **DRY RUN:** if the task message contains "MODE: DRY RUN", nothing is scheduled or published. Every post is created with `saveToDraft: true` and its text starts with `TEST DRAFT — DO NOT PUBLISH —`. Project logs get a row marked DRY RUN. The founder is not notified; report in the final response only. In DRY RUN, run the duplicate check and report its result, then still create the TEST DRAFTs so the content can be reviewed. The ready series also sends its WhatsApp image, captioned "TEST".

## 1. Preflight (mandatory; nothing is created until it passes)
1. `git clone --depth 1 https://github.com/sklohtia-manager/tml-social-media /home/claude/tml` (on failure retry twice, 20 s apart).
2. `python3 /home/claude/tml/tools/preflight.py <series>` must print `"preflight": "PASS"`. A missing policy file, logo, renderer or topic card is a **mandatory failure**: stop, create nothing, and notify the founder with the exact failed check.
3. Read `policy/FINANCIAL_CONTENT_RULES.md`, `policy/FOUNDING_PRINCIPLES.md`, `policy/AUTHORISATIONS.md`, `policy/EDITORIAL_POLICY.md`, `brand/LOGO_USAGE.md` and `ops/config.json` from the clone.
4. **Central content history and calendar:** read `content/history.json` (never repost the introduction videos or episodes; no educational subject repeated within 21 days unless there is new official data) and `ops/EDITORIAL_CALENDAR.md` (today's planned theme; verified news takes priority).
4a. **History (always):** `list_posts` for the three channels over the last 14 days (all statuses). Buffer's post history is the guaranteed record shared by every run: post IDs, text, source links, image URLs (which encode the topic card and variant), and created and sent times. Use it for topic, theme and card rotation even when the Projects tool is missing.
5. **Series log** (Projects tool, when available): `project_read` the series log in `ops/config.json`. If it does not exist, create it with `project_write` (header row only). If the Projects tool is not available in this run or the log cannot be read or written, continue using the Buffer history. Put the complete log row in the final response, and add it to any notification you send.
6. **Buffer:** `list_channels` for the organisation. Instagram, Facebook and X must be present, `isDisconnected: false` and `isLocked: false`. On an API error, wait 60 s and retry once. A channel that is still disconnected or locked is skipped, and the founder is notified ("authentication lost: <channel>"). The other channels continue.
7. **Duplicates:** `list_posts` for the three channels created since 00:00 today (sent, scheduled, sending, draft, needs_approval). A post of this series already exists on a channel if (a) one is scheduled or sent within **45 minutes of the series' publish time** today, or (b) its text carries the series **label** or a `legacyMarkers` entry. Then create nothing on that channel. **The standard hashtag `#TMLEducation` does not count**: other education posts (for example trial posts at 12:30 PM) must not block the 3:15 PM edition. **Ignore drafts whose text starts with `TEST DRAFT`**: they are dry-run artefacts and never block a real edition. Today's earlier series' stories must not be repeated.
8. **Research sources:** confirm official sources can be read in this run. Use the Agent tool with `subagent_type: "web-fetch"` on one relevant primary page, for example the ABS or RBA release you intend to cite. If no primary source can be retrieved, the edition **cannot meet FE-01 (a)**: HOLD (drafts only) and notify "primary sources unreachable".
9. **Availability of earlier slots (cross-check, every run):** using the Buffer history, confirm the previous deadline's edition actually went out: the 9:00 run checks yesterday's 7:30 PM Evening; the 2:30 run checks today's 9:30 AM Morning; the 7:00 run checks today's 3:15 PM Ready. Classify it as PUBLISHED (sent within 15 minutes of the deadline), DELAYED (sent later), FAILED (created but errored or not sent) or MISSED (never created). For anything other than PUBLISHED, write or update that slot's log row and notify the founder once. Also add a row to `ops/MISSED_EDITIONS_LOG.md` (a later interactive session can do this when the routine could not). If the slot is MISSED, do **not** replay stale news; a recovery package (see that file) is built only on the owner's request. Never re-post a missed news edition.

## 1A. Videos (manual ledger)
- Read `queue/manual/*.json` and `queue/*.json`. Never post any video yourself.
- Never post a video or clip of a contentId listed there.
- Image editions are the routines' job; videos are the VPS worker's job (`worker/`), so nothing can be published twice.
- **Approved videos for X:** if a non-manual manifest in `queue/` lists target `x`, carries owner approval and its `publishAt` falls inside this run's publish window:
  1. schedule it once in Buffer (X channel) as a video asset from its raw GitHub URL, with "Ref: <contentId>" in the text;
  2. before creating it, check `list_posts` for that Ref, and never create a second one.

## 1B. Content availability and educational fallback
- **Deadline check:** before ending the run, confirm that this edition is scheduled for its deadline on every channel (or record why not). Each run ends at least 15 minutes before its deadline.
- **Ready for Tomorrow only (3:15 PM):** if today's edition cannot be produced or verified (sources unreachable, verification incomplete or HOLD), use the next **owner-approved** evergreen item from `content/evergreen/ready/` (`approval.owner: true`) not used in the last 30 days (check the log and Buffer history for its title). Publish its captions and card exactly as approved, labelled "education edition", and notify the founder ("Ready fallback used: <id>, reason: …"). Log it as FALLBACK-EDUCATION. If no approved item is available, HOLD as usual.
- **Morning and Evening (news):** never substitute evergreen content and never publish an older story as today's news. HOLD (drafts) and notify the founder.
- A fallback is never used after `lastCatchUp`; the no-catch-up rule still applies.

## 2. Research and verification
- **Trend and topic check:** follow `ops/TREND_CHECKLIST.md` (YouTube Studio Trends, Google Trends, TikTok Creative Center, our own insights; Australia and India/Hindi separately) and log the result in `ops/trend-log.json`. The scheduled routines can check Buffer insights only; they write "not checked" for the rest and never guess.
- Use WebSearch for discovery only. Every figure, date and claim must be confirmed on the **primary official page**, fetched in this run with the web-fetch subagent: RBA, ABS, Treasury, ATO, ASIC, APRA; RBI, MoSPI, Ministry of Finance, PIB, SEBI; Federal Reserve, BLS, BEA; OECD, IMF, World Bank, IEA; official government announcements; or company releases and filings.
- For each fact, record the publisher, URL, period, release date and retrieval time.
- **Freshness:** every news item states its release date. Only describe something as new, today's or latest if its primary release is from the last 24 hours (Morning: since the previous Evening edition). Older releases may be referred to only with their date and as background, never as current news. If the newest verified item is older than that, HOLD and notify.
- Distinguish fact, forecast (attributed), historical evidence and opinion. Never invent news, numbers, quotes or causation. A claim that cannot be verified is dropped; if the story depends on it, HOLD.

## 3. Compliance gate (FINANCIAL_CONTENT_RULES.md, FOUNDING_PRINCIPLES.md, EDITORIAL_POLICY.md)
- **BLOCK** (rewrite or do not publish):
  - recommendations, rankings or steers on any product, fund, stock, ETF, super, loan, insurance, gold, crypto, property or asset class;
  - buy, sell or hold calls, targets, signals, forecasts for named securities, or guaranteed returns;
  - trading, speculation, fast-money or get-rich-quick framing (R10);
  - personalised financial, tax, legal or migration advice;
  - sensationalism, fear, urgency or political bias;
  - misleading country comparisons;
  - private family investment information or paid materials.
- **HOLD** (drafts only, and notify):
  - a claim not confirmed on a primary source fetched this run;
  - share prices, index levels or market moves at the centre of the story;
  - any Indian securities price data;
  - rumours or anonymous sources;
  - causation not stated by the source;
  - doubt about data rights;
  - a politically sensitive topic;
  - anything uncertain.
- Write all final texts to `/tmp/post.txt` and run `python3 /home/claude/tml/tools/preflight.py --lint /tmp/post.txt`. Exit code 3 means **HOLD**. A clear lint is not approval; the gate above still applies.
- **ALLOW** only if every check, every FE-01 condition (or the 3:15 PM authorisation) and every founding principle passes.

## 4. Images (approved method: hosted branded topic cards)
- Choose the topic key in `ops/topic-cards.json` whose **title accurately describes the post** (there is no generic "explainer" card). Follow the post template rules in `ops/series/ready.md` ("Post template and signature rule"); they apply to all three series.
- Each topic has three design variants: `""` (forest), `-v2` (charcoal) and `-v3` (warm white). **No repeats:** read the series log and use the variant of this topic that has not been used for the longest time. Never use the same topic and variant combination twice within 7 days in any series. If all three variants of the best topic were used in the last 7 days, choose the closest other topic that fits.
- The image URLs are:
  - feed (Instagram and Facebook): `https://raw.githubusercontent.com/sklohtia-manager/tml-social-media/main/images/cards/card-<edition>-<topic><variant>-feed.jpg`;
  - X: `…-x.jpg`.
- Confirm both files exist in the clone. If they don't, it is a mandatory failure: drafts only, and notify.
- altText: "Two Market Ledger <series label> card: <topic title>. General education only."
- Do not upload or host any other image. Scheduled runs have no GitHub write access, and a missing image never triggers a workaround: drafts only, and notify.

## 5. Publish
- `dueAt` = today at the series `publish` time (ISO 8601 with the offset from `get_account`).
  - Before that time, use `mode: "customScheduled"`.
  - Between `publish` and `lastCatchUp`, use `shareNow`.
  - After `lastCatchUp`, drafts only.
- Create each channel's post independently: a failure on one never stops the others.
- **Instagram:** feed image asset (with altText), `metadata.instagram {type: "post", shouldShareToFeed: true}`, `schedulingType: "automatic"`.
- **Facebook:** always its own post (Buffer does not cross-post Instagram to Facebook, so Facebook gets each edition exactly once). `metadata.facebook.type: "post"`, feed image asset.
- **X:** X image asset; at most 280 characters, with links counting as 23 (count with code).
- **HOLD or BLOCK:** compliant drafts (`saveToDraft: true`) with the same images, and notify.
- **Plan limit (10 scheduled posts):** on that error, save as a draft and notify. For other errors, fix the cause, run `list_posts` to make sure there is no duplicate, then retry once.

## 6. Verify and notify
- `get_post` each post: expect "scheduled" (or "sent") with no error. If the run is still active after the publish time, re-check until "sent" (up to about 20 minutes).
- **Manual and native posts:** posts that the owner published directly on a platform appear in `list_posts` with `via: "network"`. Record them in the log as MANUAL. Never repost, copy or duplicate them. Treat their topic as already covered today.
- **Duplicate self-check:** repeat step 1.7 and confirm each channel now has exactly one post of this series today. If there are two, delete nothing; notify the founder with both IDs.
- **SendUserMessage only when intervention is needed:**
  - preflight failure;
  - publication or image failure;
  - lost authentication;
  - unreachable primary sources;
  - HOLD or BLOCK;
  - plan limit;
  - Project log not writable.

  State the problem, what was tried and the exact action needed. Routine success sends no message (except the 3:15 PM WhatsApp image; see the series file).
- **Final response:** decision, headline, per-channel post IDs and statuses, image URLs, and sources with URLs and dates.

## 7. Log
`project_read`, then `project_write` the full series log: one table row per date and edition (update the row rather than duplicating it). Columns:
1. date;
2. edition;
3. outcome, recorded separately for each kind: PUBLISHED, SCHEDULED, DELAYED, FAILED, MISSED, MISSED-DRAFT, HOLD-DRAFT, FALLBACK-EDUCATION, DRY-RUN or SKIPPED-DUPLICATE (a slot found MISSED, DELAYED or FAILED by a later run's cross-check gets its row updated, with the checking run noted);
4. headline;
5. theme (ready series) or topic;
6. card (topic and variant, e.g. `inflation-v2`);
7. source URLs with publisher and release dates;
8. classification;
9. Instagram, Facebook and X post IDs with statuses;
10. failures or notes.

Keep the latest 120 rows. Write a row even when the run fails or skips (FAILED or SKIPPED, with the reason). This log is the persistent memory between runs; Buffer's post history is the second record.
