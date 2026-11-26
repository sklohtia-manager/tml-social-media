# TML publishing worker (VPS)

An isolated service for **owner-approved video uploads**:
- YouTube and Shorts;
- Instagram Reels and Facebook Reels.

It runs independently of the Mac, Claude Desktop, Chrome and Claude plan limits.

The Buffer cloud routines keep the daily image editions and X. The worker never touches them.

- **Queue:** JSON manifests in `queue/`, committed to this repository.
  - A manifest is eligible only with the owner's approval and all four release-gate confirmations: narration, rights, captions and playback.
  - The asset's SHA-256 must match the approved file.
  - Manual or already-posted records (`"manual": true`) permanently block re-posting the same content on that platform.
- **Durable state:** SQLite at `/var/lib/tml-social/queue.sqlite3`. The idempotency key is content|platform|account. The states follow the owner policy.
- **Safety:**
  - dry run by default, and live only for platforms listed in `TMLPUB_PLATFORMS`;
  - global `PAUSE` and per-platform `PAUSE.<platform>` files (`tmlpub.cli pause youtube`);
  - lock file;
  - bounded retries with backoff, jitter and Retry-After;
  - an uncertain outcome blocks for review instead of retrying;
  - nothing is ever published more than 2 hours late;
  - no deletion.
- **Verification:** an item counts as `published_verified` only when the platform reports it public (YouTube: public and processed; Instagram: permalink; Facebook: video ready with permalink). An upload alone is not publication.
- **Monitoring:**
  - `tmlpub.cli health` checks tokens and permissions daily, with an alert on failure;
  - `tmlpub.cli report --send` sends the daily report;
  - alerts go through `TMLPUB_ALERT_COMMAND` (for example the approved exception-email script) and `alerts.log`.
- **Secrets:** `/etc/tml-social/youtube.json` (client_id, client_secret, refresh_token) and `/etc/tml-social/meta.json` (page_id, ig_user_id, page_token). Owner root:tmlsocial, mode 640. They never go in Git, chat or logs.
- **Tests:** `cd worker && python3 -B -m unittest discover -s tests` (fake platform API, no network).

Owner setup guide: `ops/VIDEO_PLATFORM_SETUP.md`. Installation needs owner approval: `sudo bash worker/install.sh`. It stays disabled and in dry run.

## Content availability check (Phase 2)
After each publishing deadline (+10 minutes, within 40 minutes) `run` checks the Facebook Page and Instagram for that day's edition and records it in the `availability` table as published or missed (shown in the daily report). Missing → owner alert. Only series listed in `TMLPUB_FALLBACK_SERIES` (owner decision: at most `ready`) may publish an owner-approved evergreen item from `content/evergreen/ready/`, and only when not in dry run. This needs read access to the Meta page (`/etc/tml-social/meta.json`); without it the check reports "unchecked" and the routines' own cross-check (RUNBOOK §1, step 9) remains the record.

## Dry-run install on the VPS
See `ops/VPS_DRY_RUN_INSTALL.md`.

## Private-only gate and the private upload test (27 Nov 2026)
`TMLPUB_PRIVATE_ONLY=1` (the default) means that even with `TMLPUB_DRY_RUN=0`, only manifests marked `"visibility": "private"` (with a `TML-TEST-` content ID, YouTube only) are uploaded. They are uploaded as private, with no `publishAt`, and end in `private_verified`. Public automated publishing additionally needs `TMLPUB_PRIVATE_ONLY=0`, which is only set after the owner approves the private test. See `ops/PRIVATE_UPLOAD_TEST.md`.

## Token revocation procedure (privacy policy commitment)
The daily `health` run detects a revoked or failing YouTube token and raises an alert. Within 7 days, run `sudo shred -u /etc/tml-social/youtube.json` and `tmlpub.cli pause youtube`. Do the same when the tool is retired or on request. Stored YouTube video data is refreshed or deleted within 30 days automatically (`refresh_youtube_data`).
