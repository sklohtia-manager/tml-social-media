# Two Market Ledger: operational health report (Sat 28 Nov 2026, 08:40 AEDT)

Checked by Claude Desktop (cloud session) from live evidence: the scheduled-run records, Buffer (channels, post history, queue, metrics), the live public website, and issue #17 / the owner handover. **No Mac, VPS, YouTube Studio, TikTok or Meta access from this session**, so anything that needs those is marked NOT VERIFIED rather than assumed. No schedules, production services, websites or financial records were changed. No new development was started.

**Classes:** WORKING (executed successfully, evidence below) · SCHEDULED (set up, not yet due or no execution to judge) · MANUAL (done by a person by design) · BLOCKED (cannot proceed without an action) · NOT VERIFIED (no access or no evidence).

## 1. Headline findings
1. **The 9:30 AM Ledger Morning edition has missed two days running (26 and 27 Nov).** Both runs died within seconds with "You've hit your 5-hour limit" on the shared Claude plan (27 Nov: fired 9:09 AM, limit reset 10:30 AM, after the 10:15 AM no-catch-up cut-off). Nothing was published and no drafts were created. **Root cause:** the scheduled routines share the plan's 5-hour usage limit with interactive sessions; heavy interactive work in the preceding hours uses it up. **The next Morning run is due at 9:07 AM today (about 25 minutes after this report); its outcome is unknown.**
2. **The 3:15 PM and 7:30 PM editions are working:** published and verified on Instagram, Facebook and X on 27 Nov.
3. **The live public website (twomarketledger.com) shows no news, markets or explainers.** It is still the old private-ledger build. The new website, its news/market feeds and the legal pages exist only on the protected beta and in GitHub; nothing reaches the public site until a production release is approved.
4. **Nothing was accidentally paused.** The three routines are enabled; only the two original draft-only routines are disabled, deliberately. One gap: the "end-of-trial report, 3 Dec 08:45" has no scheduled task visible to this account (see section 4).

## 2. Social publishing (Buffer, the three routines, video)
| Service or platform | Status | Last successful execution | Next scheduled | Errors or blockers | Action | Owner |
|---|---|---|---|---|---|---|
| **Ledger Morning routine** (9:00 AM run, 9:30 AM post) | **BLOCKED (usage limit)** | Not in the last two days (26 and 27 Nov both failed) | Sat 28 Nov 9:07 AM (post 9:30) | Shared 5-hour plan limit reached at run time, twice. No catch-up after 10:15 AM by policy | Keep interactive Claude use light 8:00–9:40, 14:00–15:20, 18:30–19:35 (the three run windows). No purchase of credits (not authorised). If it fails again, the slot is recorded as MISSED, never replayed | Owner (usage), Claude |
| **Ready routine** (2:30 PM run, 3:15 PM post) | **WORKING** | 27 Nov: run 2:38 PM, posts sent 3:15 PM on all three channels (IG `6b08fb6a…`, FB `…110`, X `…7816`), no errors | Sat 28 Nov 2:37 PM | The 27 Nov post used the old generic card ("Financial education explainer"); the template and 336 topic cards were rebuilt that afternoon, so tomorrow onward uses the new design. WhatsApp image (sent to the owner by this run): receipt NOT VERIFIED | none | Claude |
| **Evening routine** (7:00 PM run, 7:30 PM post, plus Sunday report) | **WORKING** | 27 Nov: run succeeded 7:01–7:32 PM; sent 7:30 PM on all three (IG `6b0939d1…`, FB `…d2…fb`, X `…ddd7`), new topic card "Jobs and wages", ABS source link, disclaimer | Sat 28 Nov 7:01 PM; Sunday 29 Nov includes the weekly report | none | none | Claude |
| **Facebook** (Page, via Buffer) | **WORKING** | 27 Nov 7:30 PM (also owner-approved explainer 5:14 PM) | with the routines | Connected, not locked | none | Claude |
| **Instagram** (business, via Buffer) | **WORKING** | 27 Nov 7:30 PM | with the routines | Connected, not locked | none | Claude |
| **X (@TwoMarketLedger)** (via Buffer) | **WORKING** | 27 Nov 7:30 PM | with the routines | Connected, not locked | none | Claude |
| **LinkedIn** (Buffer) | **BLOCKED (by design)** | n/a | n/a | Locked on the free plan; routines never post there | none unless the owner wants it | Owner |
| **Buffer queue** | **WORKING** | n/a | n/a | **Empty** (0 scheduled, draft, approval or error posts) as expected; posts are created the same day. Plan limit 10 scheduled posts; no pressure | none | Claude |
| **Failed, missed, duplicated posts (26–27 Nov)** | see right | n/a | n/a | **Missed:** Morning 26 Nov and 27 Nov. **Failed:** none with an error status. **Duplicated:** none found (each channel's posts on 27 Nov were distinct: 3:15 PM, 5:14 PM owner-approved explainer, 7:30 PM) | none (no replay of missed news) | Claude |
| **Branding, captions, images, sources** | **WORKING** | 27 Nov Evening and the approved explainer | with each run | Logo, green-and-gold card, ABS/RBA source lines and disclaimers all present | none | Claude |
| **YouTube (VPS publishing worker)** | **NOT VERIFIED** (last known: installed, dry run) | 27 Nov ~7:14 AM (Claude Code): health OK, token refreshed, channel "Two Market Ledger" matched | timers every 5 min, daily health 8:30 PM | No YouTube access from this session. Public publishing is **disabled by design** until the private test passes and the owner approves. Nothing scheduled on YouTube | Claude Code to confirm timers and daily health since 27 Nov (including after the planned 28 Nov 1:00 AM reboot window, if it happened) | Claude Code |
| **YouTube OAuth token** | **NOT VERIFIED today** | 27 Nov: valid (app "In production", so no 7-day expiry) | n/a | Revocable at any time by Google | none | Claude Code |
| **TikTok** | **MANUAL** | n/a (no videos posted yet) | per approved video | No official automation (by design). Upload packs are built by `worker/tools/upload_pack.py` | none until a video is approved | Owner |
| **Instagram Reels / Facebook Reels (Meta API)** | **NOT VERIFIED** | n/a | n/a | Meta credentials not configured (by design); Reels are manual | none | Owner |
| **WhatsApp status** | **MANUAL** | daily image is sent to the owner by the Ready run | 28 Nov 2:37 PM | Posting is manual; receipt not verifiable from here | none | Owner |

## 3. Website: news, markets, insights
Distinguishing what the **backend collected** from what the **live public site displays**:
| Service | Collected by the backend | Displayed on the live public site | Status |
|---|---|---|---|
| Official news (Australia, India, Global; government and central-bank items) | Beta server: timer every 15 min; last report (27 Nov): 86 runs, 0 failures; 16 feeds | **No.** twomarketledger.com serves only the old sign-in shell (`/` 200); `/api/daily` returns 404 | Collection: **NOT VERIFIED today** (last evidence 27 Nov). Display: **BLOCKED** |
| Markets (AUD/INR, Brent/WTI, CPI, jobs, GDP, RBA cash rate 4.85%) | Beta: verified on screen 27 Nov (RBA daily series, 25 Nov observation) | **No** | same |
| Daily explainers and insights | Eight explainers drafted; hidden until approved | **No** | **BLOCKED** (owner approval, one by one) |
| Website news export and content refresh | `tml-news` timer rebuilds the feed every 15 min on the beta | n/a | **NOT VERIFIED today** |
| Beta site (password-protected, not public) | Running release `2b099c2`; answers 401 to the public (as intended) | Not public | **WORKING** (protected); content not inspectable from here |
| Legal pages (/legal/privacy, /terms, /publisher) | Ready in PR #47 (publishable) | **No** (404 on production) | **BLOCKED** (owner approval of Option B deployment) |

**Will the new public website receive these updates automatically after deployment?** Yes by design: the collection and refresh timers run on the server independent of any person, and a deployed site reads the rebuilt feed. **What is still needed before that happens:** (1) the owner's approval to deploy the new site to production (a full release, not the limited Option B); (2) production standing authorisation for automatic public display (the existing authorisation is **beta only**; the production draft is revoked); (3) source and rights reconciliation (registry marked pending vs engine approval) and the legal and source review (#18); (4) approval of the unreviewed sections and explainers; (5) a production-side check that the feed path works at the production address; (6) indexing stays off until the launch is approved.

## 4. Outstanding tasks, blockers and approvals
| Item | Status | Responsible |
|---|---|---|
| Morning routine misses (usage limit) | **BLOCKED**, recurring | Owner / Claude |
| Legal pages Option B deployment; Google branding resubmission (24 h after domain verification has passed, but the pages must be live first) | **BLOCKED** on owner approval | Owner, Claude Code |
| Root SSH key confirmation; alert email; recovery keys; reboot window approval | Pending owner (handover items 1–5, 10) | Owner |
| #48 independent review (three backup profiles) | Pending | Codex |
| Media Studio files, titles, descriptions, playlist info; Thursday Short; rice-pack release ID | Pending | Codex |
| Private YouTube upload test (needs the owner's approval of the exact file, then one run) | Pending | Owner, Claude Code |
| The 14 articles, 7 evergreen posts, Nvidia correction, revised "Income vs net wealth", trial week 1 | Pending owner approval (individually) | Owner |
| Beta trial end report (due Thu 3 Dec 8:45 AM) | **No scheduled task visible** to this account | Claude Code to confirm how it is scheduled |
| Off-site backups, email alerts | Not active (prepared) | Owner approval |
| Production access / server changes | Need the owner's approval and Claude Code | Claude Code |
| Upcoming limits | **Shared Claude plan 5-hour limit** (main risk). Buffer free plan (3 channels, 10 scheduled posts) fine. Beta HTTPS certificate valid to 23 Feb 2027. Google OAuth in production (no expiry). No expiring credential found | Owner |

## 5. Operational continuity
All previously approved routines remain enabled with **no duplicate schedules** (three enabled; two legacy draft-only routines disabled on purpose). Existing times are unchanged. Nothing unapproved was published; no video, product, or website deployment was started; production financial records were not touched. Discretionary development resumes its pause after this report.

## 6. Minor fixes made within scope
None needed. (The generic-card issue was already fixed on 27 Nov.) No safe fix exists for the plan usage limit: it needs lighter interactive use, not a configuration change, and buying credits is not authorised.
