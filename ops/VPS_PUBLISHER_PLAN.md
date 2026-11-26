# Proposal: dedicated publishing worker on the Hostinger VPS (needs owner approval; nothing is installed)

**Goal:** publish and verify independently of Claude plan limits, the Mac and browsers. The Claude routines keep the research and editorial work.

**Design**
- **Service:** separate Unix user `tmlsocial`, a SQLite queue in `/var/lib/tml-social`, and a systemd timer every 5 minutes. No ports open, no web UI, no access to the website database.
- **Queue key:** content ID + platform + account. It stores:
  - states: draft → needs_review → approved → queued → uploading → scheduled_remote → published_verified (or retry_wait, blocked, failed, manual_pending, expired);
  - for each item: asset SHA-256, caption version, UTC and local times, remote post ID, permalink, attempt count and sanitised errors.
- **Input:** the routines (or the owner) commit approved items as JSON manifests plus media to `queue/` in this repository. The worker pulls with a read-only deploy key. Repository approval is the gate.
- **Adapters:**
  - YouTube Data API (OAuth refresh token in `/etc/tml-social/youtube.json`, mode 0600, private-first uploads);
  - Meta Graph API for Reels (needs a Meta app with `instagram_content_publish` and `pages_manage_posts`);
  - X API (paid tiers are not approved);
  - Buffer stays the publisher for image posts.
- **Reliability:**
  - lock file;
  - bounded retries with jitter, honouring Retry-After;
  - reconcile remote status before any retry, and block on doubt;
  - token-expiry check daily;
  - per-platform and global pause files;
  - no automatic deletion.
- **Alerts and reports:** the daily summary and failure alerts reuse the exception-only Gmail alert path in `two-market-ledger/ops/news/ALERTS_AND_OFFSITE_BACKUP.md`, once that is approved.
- **Capacity:** the existing VPS already runs the news engine (about 60 MB of memory per run). The worker is similar.

**Steps, each needing approval:**
1. Owner creates a Google Cloud project, a YouTube OAuth client and a Meta app (free).
2. Claude builds the worker on a branch, with tests and a dry-run mode.
3. Install it on the VPS from the Mac (the same procedure as the news engine).
4. Upload one private YouTube test video and record the video ID.
5. One owner-approved live test per platform.
6. Enable the timers.

Rollback: disable the timers. The queue is kept for review.
