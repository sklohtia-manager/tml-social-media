# Daily operations checklist (Melbourne time)

**Owner quick view:** check your phone at about 9:45 AM, 3:30 PM and 7:45 PM. A message from Claude means something needs you. No message means the edition published normally (apart from the daily 3:15 WhatsApp image).

## Research (automatic, every edition)
- [ ] 9:00, 2:30 and 7:00: the routine starts, runs preflight (policies, logo, cards, renderer) and reads `content/history.json`, the calendar and the last 14 days of Buffer history.
- [ ] Facts come only from primary official sources, read in the same run, with the release date and period recorded. Anything older than 24 hours is never called new.
- [ ] Unverifiable or uncertain: drop **that item** and move down the content ladder (A news → B dated 24–72 h → C weekly summary → D educational explainer, `ops/PUBLISHING_POLICY.md`). Never hold an edition for lack of news.

## Content creation (automatic)
- [ ] Captions per platform (Facebook, Instagram, X) with the hook, source, signature question and the line "Education only. Not financial advice."
- [ ] Branded topic card, rotated so no card repeats within 7 days. The 3:15 WhatsApp status image goes to the owner.
- [ ] Compliance gate: no advice, recommendations, trading, fast money, predictions or political opinion.

## Video production (Codex, Media Studio, on the Mac)
- [ ] English and Hindi videos (target: at least one Hindi Short a day at 6:30 PM), exported to the standard format (`ops/MEDIA_STUDIO_HANDOFF.md`) with sources and AI-voice disclosure where relevant.
- [ ] The video ID is new, and the subject has not been repeated within 21 days (`content/history.json`).
- [ ] Posted on issue #17 for review, with ID, language, title and length.

## Approval (owner)
- [ ] Watch each video and reply "approve <ID> for <time>". Any edit means approving again.
- [ ] Articles and evergreen posts: approve each one individually from the review PDFs.
- [ ] Corrections (for example, Nvidia): approve the exact text, then edit the native post yourself.

## Publishing
- [ ] 9:30, 3:15 and 7:30 image editions are scheduled by the routines through Buffer, exactly once each.
- [ ] Videos: approved files are staged privately on the VPS (`stage_video.sh`). YouTube goes through the worker (private-only until activation is approved). Instagram, Facebook and X go through Buffer once each with "Ref: <ID>". TikTok and WhatsApp are manual.
- [ ] Never repost TML-YT-001 or TML-YT-002, or any video in `queue/manual/`.

## Failure handling
| What happened | What the system does | What the owner does |
|---|---|---|
| A routine didn't run (for example, the usage limit) | The next run's cross-check marks it MISSED and records it. A news edition is never replayed late. An authorised educational explainer can fill any slot that is still within its catch-up window | Nothing, unless you want to post manually |
| Source unreachable or facts unverified | Blocked source skipped (not retried); the edition moves down the ladder and is still published and verified | Nothing |
| Buffer channel disconnected | That channel is skipped; "authentication lost: <channel>" | Reconnect the channel in Buffer |
| Worker or YouTube problem (token revoked, wrong channel, upload uncertain) | Item blocked plus alert; nothing is retried blindly; never published late | Read the alert; Claude Code checks the VPS |
| A private test turns out public | Marked `needs_review` with an immediate alert | Open YouTube Studio and set it to private |
| Something is wrong after publishing | Suspend, preserve evidence, propose a correction (rule R08 step 6) | Approve the correction or deletion |
| Emergency stop | `tmlpub.cli pause`; ask Claude to hold editions | Say "pause all publishing" |

## Weekly (Sunday Evening run)
- [ ] Weekly performance report: social metrics, the website-and-search section, video results. Unavailable data is marked "unavailable".
- [ ] Roll the editorial calendar forward a week. Update `content/history.json` in an interactive session.
