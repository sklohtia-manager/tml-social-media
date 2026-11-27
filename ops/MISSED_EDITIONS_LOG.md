# Missed and failed editions (permanent record)

Each row: what failed, why, whether a recovery was possible, and what was done. **A missed news edition is never published later as current news.** Education items that are still accurate (FRESH) may be offered for manual posting; STALE items are not.

| Date (Melbourne) | Edition | Outcome | Cause | Evidence | Recovery package | Action taken |
|---|---|---|---|---|---|---|
| Thu 26 Nov | Morning 9:30 AM | MISSED (nothing published, no draft) | Shared Claude plan 5-hour usage limit reached when the routine fired | trigger `trig_01CYJmXQrTzB7cJywAcnTps5` run FAILED (usage limit) | **STALE**: news of 26 Nov morning was overtaken by the later editions; none offered | none (policy: no catch-up, no replay) |
| Fri 27 Nov | Morning 9:30 AM | MISSED (nothing published, no draft) | Same: run at 9:09 AM, "5-hour limit, resets 10:30 AM" (after the 10:15 AM catch-up cut-off) | session `cse_01FWsAsL3bo3CNAFsbrRDwQZ`: `usage_limit_reached` (429), duration under 1 s | **STALE**: the day's releases were covered by the 3:15 PM and 7:30 PM editions | none; health report `ops/HEALTH_REPORT_2026-11-28.md`; reliability handover for Codex |

## Manual recovery package (procedure)
Built by an interactive session when a slot is MISSED or HELD and the owner asks (or by the VPS watchdog once it exists, see the Codex handover). Folder per slot with: ready-to-post captions per channel, the image, sources with publisher/date/period, a **freshness verdict** (FRESH if the primary release is under 24 hours old and still the latest relevant item; otherwise STALE), and the reason for the miss. STALE news items are listed but not offered for posting. TikTok, Reels and unapproved educational video stay manual. Nothing is published without the owner's go-ahead.
