---
name: tml-social-media
description: Audit, prepare, schedule, publish and verify Two Market Ledger social media and approved videos.
---

# Two Market Ledger — permanent social media operating policy
Version 1.0 | 27 November 2026 | Timezone: Australia/Melbourne

## Mission and priority
Social distribution is a core business priority, not an optional website task. Attract and retain an audience through accurate, timely, accessible financial journalism and education. Preserve the original logo and brand tagline “Two Nations. One Financial Future.” Educational closing: “Learn. Understand. Stay Informed.” Cover Australia, India and global markets. Public content is factual and educational only; no investment recommendations, personalised plans, buy/sell calls, fearmongering or guarantees. Never publish private founder holdings, research, credentials or paid material without explicit release approval.

## Immediate incident audit
1. Inventory all existing schedules, scripts, repositories, branches, connectors, token expiry, target account IDs, platform permissions, execution hosts, job logs and last successful publication. Do not assume a generated draft was published.
2. Reconcile 26–27 November 2026 Melbourne-time failures with actual platform history. Owner reports TML-YT-002 video variants were posted manually: reconcile each platform ID/link or owner evidence and do not repost them. Identify missing normal daily posts, wrong images/captions, partial jobs, duplicates and timezone errors. Do not blindly replay missed news; check freshness first.
3. Produce a root-cause report and corrective plan. Preserve existing approved cadence unless owner approves a change. Do not delete published content or replace working credentials without approval.

## Execution architecture
Prefer a dedicated, isolated publishing worker on the existing Hostinger VPS, using a durable database queue and systemd timer or equivalent. Confirm resource capacity and deployment approval first; no production website/database changes without separate approval. Use Claude cloud routines for research/editorial preparation if available; local Desktop routines need the Mac awake and app running. Never depend on a chat session, local browser cookie or laptop for production publishing. A skill file alone does not install or schedule anything. Use official platform APIs or compliant native schedulers; no CAPTCHA bypass, unofficial private APIs or password automation. Keep secrets in a restricted secret store, not Git, reports, logs or prompts. Verify channel/page/account IDs before each write.

## Content workflow
Research → source validation → draft → media render → policy and quality checks → approved/eligible queue → schedule → publish → verify → report. Use primary sources (ABS, RBA, ASX, RBI, SEBI, official exchanges, company filings) and record source URL, data period, release date, retrieval timestamp, geography and units. Distinguish actuals from forecasts and illustrations. Cross-check material claims, avoid stale quotes presented as live and skip uncertain items. Use platform-specific concise copy, readable graphics, licensed assets, source attribution and accurate headlines. No fake engagement or sensational claims. Correct substantive errors transparently; owner approval for deletions.

## Proposed schedule (owner approval required; preserve existing schedule until approved)
07:30 Melbourne: global overnight recap; 12:30: Australian market/economic update when substantive; 19:00: India/global update with market status clearly labelled (not a close recap unless closed). On relevant market holidays/weekends, use educational content or skip; do not invent news. Initially 2–3 approved Shorts/Reels per week and one longer educational video when ready. Adjust after two weeks of actual engagement data, not guessed optimal posting times. Respect daylight saving using IANA timezone, store UTC timestamps and local display times. Breaking news only if verified and within approved scope.

## Platform adapters
- Facebook Page and Instagram professional: official Meta publishing APIs or Meta Business Suite; verify permissions, media container processing, account linkage and final published IDs. Do not duplicate automatic cross-posts.
- X: official API with write/media permissions and confirmed cost limits; concise text, native media, source links when suitable. No unapproved paid API spend.
- YouTube: official Data API OAuth, channel verification, resumable upload, metadata, playlist, captions when supported; explicitly private first. Verify processing, copyright/rights checklist and owner-approved release time. Use native scheduling or API publishAt when supported; verify actual project restrictions. Do not assume API access or public publishing eligibility. Confirm Shorts classification in Studio when needed. No automated dubbing release without human review.
- TikTok: native scheduler or approved compliant publishing provider; verify audit, scope, consent, branding and direct-post eligibility. Otherwise prepare manual posting pack. Do not assume a private internal integration qualifies for Direct Post.
- WhatsApp Status: manual publishing pack and reminder; no verified official Status publishing API in this plan. Do not substitute bulk messaging or automate personal browser sessions.

## Video release gate
Only publish final owner-approved media with commercial rights verified, accurate narration/captions, correct platform variant, licensed assets, no watermark from another platform and final playback checks. TML-YT-001 is channel introduction; TML-YT-002 is education Episode 01. Preserve those files. For future videos: A YouTube Subscribe; B Instagram/Facebook/X Follow; C full WhatsApp; D short WhatsApp alternative; TikTok use compliant variant. Maintain 1080x1920 vertical for shorts, H.264/AAC, mobile-safe text; verify platform limits at upload. Store cover, script, SRT, metadata, source/rights manifest, duration, checksum and approval record. Hindi audio and subtitles require reviewed translation. AI voice rights remain a release blocker until verified; apply required platform AI disclosures. Never auto-publish silent drafts or unapproved voiceover. Private upload is not public publication.

## Queue, reliability and evidence
Use stable content ID + platform + target account as unique idempotency key. Store asset SHA-256, caption version, scheduled UTC, local time, approval status, attempt count, provider request ID, remote post ID, permalink, publish time and sanitized errors. States: draft, needs_review, approved, queued, uploading, scheduled_remote, published_verified, retry_wait, blocked, failed, manual_pending, expired. Lock concurrent workers. Before retry after timeout, reconcile remote status; if uncertain block for review instead of duplicate post. Use bounded retries with backoff and jitter for transient failures, honor Retry-After; authentication/permission/policy failures alert immediately. Never retry expired news blindly. A successful upload or HTTP 200 alone is not verified public publication. Confirm remote status and target visibility; retain evidence. Record manual postings in same ledger. Pause switch per platform and globally. No automatic deletion. Send owner notification for missed schedules, blocked items and repeated failures via an approved channel, with actionable reason, no secrets.

## Approval and rollout
Existing expressly approved routine factual posts may proceed within scope after verified integration and owner-approved rollout. New workflows, schedule changes, paid costs, public video release and sensitive content need approval. Start with dry-run; then private/draft tests where supported; then one owner-approved live test per platform. Do not publish test spam. Confirm job executes when Mac and Claude are closed, recovery after restart, duplicate prevention, token expiry handling, correct timezone, partial-platform failures and rollback/pause. Report actual evidence, not simulated success. Use a separate branch/worktree; no unrelated website changes. Document commands, configuration names, service status and rollback without secrets. Do not call the system complete if any platform is untested.

## Owner reporting and growth
Daily summary: due, published verified with links, failed, blocked, manual pending, missed, next schedule. Weekly review: reach, views, watch time/retention, saves, shares, subscriber/follower changes, clicks where available; show unavailable metrics as unavailable. Use results to propose stronger hooks and formats without clickbait. Do not buy followers or spam. Archive reports and content manifests outside public web root.

## Reference documentation (recheck before integration)
- Claude cloud: https://code.claude.com/docs/en/claude-code-on-the-web
- Claude skills: https://code.claude.com/docs/en/skills
- YouTube upload: https://developers.google.com/youtube/data/guides/uploading_a_video
- YouTube videos: https://developers.google.com/youtube/data/reference/rest/v3/videos
- Meta Instagram: https://developers.facebook.com/docs/instagram-platform/
- X: https://docs.x.com/
- TikTok: https://developers.tiktok.com/docs/en/content-sharing-guidelines
- WhatsApp: https://developers.facebook.com/documentation/business-messaging/whatsapp/overview/

## First action when loaded
Audit existing social media jobs and today's failures, reconcile manual posts, identify blockers and propose changes. Install this skill at .claude/skills/tml-social-media/SKILL.md and add a short mandatory reference to existing CLAUDE.md without overwriting other rules. Ensure scheduled jobs explicitly load the policy. Deliver incident report, platform readiness matrix, deployment plan and owner approval checklist before enabling new public automation.

## Owner decisions (27 November 2026; permanent until the owner changes them)
1. **Schedule retained (Melbourne local time, IANA Australia/Melbourne):**
   - 9:30 AM Morning Market Brief (The Ledger Morning);
   - 3:15 PM Ready for Tomorrow;
   - 7:30 PM Evening Market Recap.

   Preparation runs stay at 9:00 AM, 2:30 PM and 7:00 PM in the existing Claude cloud routines. The 07:30/12:30/19:00 proposal above is **not** adopted.
2. **Channels:** Facebook, Instagram and X through Buffer, which stays for image posts and X. LinkedIn deferred. WhatsApp Status manual: the daily 3:15 PM vertical image is sent to the owner.
3. **VPS publishing service approved for development** (`worker/`).
   - Owner-approved video uploads to YouTube, YouTube Shorts, Instagram Reels and Facebook Reels through official APIs.
   - Durable queue, idempotency, bounded retries, verification, alerts, token monitoring, pause switches and a dry-run default.
   - **Not live until integration tests pass and the owner approves.**
   - It never posts what the routines post (image editions, X), and the routines never post videos through the worker.
4. **Videos:**
   - Every video needs owner approval before scheduled publication (the release gate in the manifest).
   - Never repost TML-YT-001 or TML-YT-002; manual records are in `queue/manual/`.
   - TikTok stays manual until a compliant audited integration exists.
5. **Growth is a high priority:** strong factual hooks, branded mobile-readable graphics, short animated education videos (owner-approved), platform-specific captions, relevant hashtags, consistent times and website referrals once the public site is live. Neutral and factual only: no misleading claims, recommendations or unverified forecasts.
6. **Reporting:**
   - a daily publication summary (Evening run);
   - a weekly performance report every Sunday (Evening run), using real Buffer and platform analytics only;
   - metrics that aren't available are reported as unavailable and never estimated.
7. **No paid APIs or subscriptions, no new expenditure.** No changes to the production website, the private investment dashboard or founder credentials.


## Owner decisions, Phase 2 (27 November 2026)
1. **VPS worker installation approved in dry-run mode** as an isolated service on the existing Hostinger VPS (own user, own directories, systemd timers that start automatically after a restart). Live publishing stays disabled until each platform integration is tested and the owner approves it. Verify scheduling, the durable queue, duplicate prevention, failure alerts, retries and the pause controls. No changes to the production website, the beta website, the private dashboard or the financial database.
2. **Buffer stays** for the daily schedule (9:30 / 3:15 / 7:30) on Facebook, Instagram and X. Never repost the videos already published manually (TML-YT-001, TML-YT-002).
3. **Content availability:**
   - keep at least **seven owner-approved evergreen education posts** with graphics for Ready for Tomorrow (`content/evergreen/ready/`, `ops/EVERGREEN_BANK.md`), prepared in advance;
   - verify time-sensitive news against current authoritative primary sources before publication, and **never publish outdated news as current**;
   - if a scheduled news edition cannot be produced, notify the owner; an approved, clearly identified education fallback is used **only for Ready for Tomorrow**, never in place of news;
   - check scheduled content is in place before every deadline, and have each run confirm the previous deadline's edition went out;
   - record PUBLISHED, DELAYED, FAILED and MISSED posts separately (RUNBOOK §7).
4. **Video:** Buffer can schedule Instagram Reels, Facebook Reels and X video on the current free plan (`ops/BUFFER_VIDEO_SCHEDULING.md`), which avoids the Meta API. YouTube needs the Google Cloud YouTube Data API through the VPS worker; set it up with the owner one screen at a time. TikTok and WhatsApp stay manual.
5. **Corrections:** company or market claims are verified from the company's own releases and regulatory filings, read directly, never from search snippets alone. Unsupported share-price claims are removed. Corrections of native posts are proposed to the owner and edited by the owner.
6. **Reporting continues:** the daily publication summary and the Sunday performance report.
7. **No new paid subscriptions, API charges or other expenditure.**


## Owner decisions: Google, SEO and YouTube (27 November 2026)
1. **Google verification:** Search Console ownership of twomarketledger.com is verified. The OAuth project `tml-publisher` is "In production" with the `youtube.upload` and `youtube.readonly` scopes. Brand and sensitive-scope verification is pending; it is optional for an app used by fewer than 100 people (Google: "When is verification not needed").
2. **Public legal pages** for Google: `/legal/privacy`, `/legal/terms` and `/legal/publisher`, server-rendered, with full Google OAuth and YouTube API disclosures. Prepared in website draft PR #47 and coordinated on issue #17. Not live until the owner approves a production release or the interim nginx option. Keep the approved TML logo.
3. **YouTube safety:**
   - the worker uploads only to the channel ID the owner confirmed at sign-in, and blocks otherwise;
   - stored YouTube data is refreshed or deleted within 30 days (YouTube Developer Policies III.E.4);
   - live publishing stays off until testing and owner approval;
   - credentials are never in Git or chat.
4. **Weekly report** adds a website and search section: Search Console impressions, clicks, CTR, position, queries, indexed pages and sitemap; social → website referrals; and legal/SEO page availability. Each metric shows its source or "unavailable (reason)". Never estimate. Pre-launch noindex means zero search traffic is expected. See `ops/SEARCH_AND_SEO_REPORTING.md`.
5. **Indexing:** beta, private dashboards, founder information and private financial data are never indexable. Public indexing is switched on only after an approved public launch.


## Owner decisions: final YouTube and Google configuration (27 November 2026)
1. **Policy contact:** contact@twomarketledger.com. It is not published until the owner confirms the mailbox works.
2. **Legal pages:** Option B only (three static legal pages on production). Production is modified only after final owner approval, with Claude Code's verified server location, log retention and security facts.
3. **Media Studio** (`~/Documents/Projects/TML-Media-Studio`, owned by Codex) produces English and Hindi videos. Do not recreate or duplicate it.
   - Export contract: `ops/MEDIA_STUDIO_HANDOFF.md`.
   - Unique IDs: `TML-<EN|HI>-<YYYYMMDD>-<NN>`.
   - Sources, language, captions (burned in), thumbnail and status in the manifest.
4. **Unpublished videos never go into the public repository.** They are staged privately on the VPS over SSH, and the worker refuses videos committed to the repository.
5. **Public automated YouTube publishing stays off** (`TMLPUB_PRIVATE_ONLY=1`) until one private upload test passes and the owner approves activation.
6. **Hindi target:** at least one Hindi video a day, subject to quality and approval. The three daily image schedules (9:30, 3:15, 7:30) are unchanged.


## Owner decisions: media operations (27 November 2026)
1. **6:30 PM Melbourne Hindi educational Short** approved as a production target (at least one Hindi video a day, subject to quality and owner approval). Preferred voice: natural male Hindi. Produced by Codex in TML-Media-Studio. Never duplicate Media Studio.
2. **Rolling seven-day editorial calendar** (`ops/EDITORIAL_CALENDAR.md`) covering:
   - Australian, Indian, and US/global developments;
   - inflation and purchasing power;
   - household savings and preparedness;
   - beyond property;
   - children's education and retirement;
   - historical events and their lessons.
3. **Central content history** (`content/history.json`): no repeat of the introduction videos or episodes, and no repeat of an educational subject within 21 days unless there is new official data.
4. **Daily operations checklist:** `ops/DAILY_OPERATIONS_CHECKLIST.md`.
5. **Legal-page log retention wording:** must state the actual verified retention (possibly "up to six weeks"). No unnecessary server changes just to match a wording.
6. Articles, evergreen posts and corrections each need individual owner approval.


## Status and owner decisions (27 November 2026, later)
- **YouTube OAuth is done:** the owner signed in on the Mac and the Two Market Ledger channel is confirmed. **Never ask the owner to repeat it.** Claude Code handles the token transfer (stdin install, no `/tmp`), the VPS worker (installed in dry run, pinned `d118b4b`) and the private upload test.
- **Schedule (Melbourne):** 9:30 AM The Ledger Morning; 3:15 PM Are You Financially Ready for Tomorrow?; 6:30 PM Hindi educational video (production target); 7:30 PM The Ledger Evening Recap. No duplicate scheduled tasks.
- **Hindi videos:** natural, fluent, human-sounding male narration (Codex, TML Media Studio).
- **Never publish** speculative headlines or unverified company announcements. Significant news is checked against primary sources.
- **Owner action list:** `ops/OWNER_ACTIONS.md`. It lists only genuine outstanding decisions, and completed items are removed.


## Operational completion and editorial freeze (27 November 2026)
- **No new major development or large article batches.** The 14 articles, 7 evergreen posts and the Nvidia correction await individual owner review.
- **Daily operations only:** the three existing schedules (no new or duplicate tasks); verified primary-source research (Australia, India, the US and other major economies); Hindi 6:30 PM production with Codex; and monitoring issue #17 for Claude Code's YouTube work.
- **Daily operational report** (Evening run): successful posts, failed posts, pending videos, website health and genuine owner actions. See `ops/series/evening.md`.
- **Central record:** `content/history.json` lists every published article, post and video, and is checked before anything is published.


## Official contact (27 November 2026)
**contact@twomarketledger.com** (Hostinger business email, tested both ways on 27 Nov) is the official public contact for general enquiries, privacy requests, complaints and support. Use it in public pages, bios and policy text where a contact is needed. Never use the founder's personal or Gmail address publicly.


## Social post template (owner instruction, 27 November 2026)
1. **"Are you financially ready for tomorrow?" is an approved Two Market Ledger signature line, kept available as an optional line in every template** (captions, graphics, videos). Not a default, header, footer or label.
   - Use it when the topic naturally connects to financial preparedness, resilience or planning ahead (for example the financial resilience post). **Once per piece**; in a post with an image, in the caption or on the image, never both.
   - Place it near the end, ideally as the **second-last line of the body**, with a natural lead-in sentence and a short closing line that completes the thought; source, disclaimer and hashtags follow. In videos, speak it once near the end the same way.
   - Everyday explainers such as "Income vs net wealth" don't use it; the topic's own takeaway closes the post.
2. **Graphic:** keep the green-and-gold layout and the TML logo. The headline is the actual topic, never a generic "Financial education explainer". One clear takeaway on the image, plus a short definition, example or verified figure where helpful. Phone-readable text. A current statistic on the image shows its source and date on the image. Hypothetical examples are labelled.
3. **Caption:** extra context, source links, factual and educational. Series hashtag for the 3:15 PM edition is now #TMLEducation (legacy #AreYouFinanciallyReady is still recognised for duplicate checks).
4. **Live posts are not replaced or reposted without the owner reviewing the revised graphic and caption first.**
Details: `ops/series/ready.md` ("Post template and signature rule"), `tools/render.py`, `tools/build_cards.py`.
