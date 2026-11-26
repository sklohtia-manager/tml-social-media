# One private automated YouTube upload test

**Goal:** prove, end to end on the VPS, that the worker can upload one owner-approved Media Studio video to the **Two Market Ledger** channel as **private**, verify it, and report it, without anything becoming public.

## Safety gates (all in code and tested)
- `TMLPUB_PRIVATE_ONLY=1` (the default): even with live mode on, only manifests marked `"visibility": "private"` are uploaded. Every ordinary video stays dry-run.
- A private test must use a `TML-TEST-` content ID and target YouTube only. The real video's later publication is therefore never treated as a duplicate.
- **Privacy:** the upload is `private`, and no `publishAt` is sent, so YouTube never makes it public on its own. If YouTube reports it as anything other than private, the worker marks it `needs_review` and alerts you.
- **Channel check:** the token must belong to the confirmed Two Market Ledger channel ID, or nothing is uploaded.
- **Never repost:** the test is a new, never-published video, staged privately (never committed to the public repository).

## Steps
1. **Codex (Media Studio):** prepare a **new, never-published** test video, `exports/TML-TEST-20261128-01/` with `video.mp4` and a `manifest.json` following `ops/MEDIA_STUDIO_HANDOFF.md`, plus `"visibility": "private"` and `targets: youtube_shorts`. It stays on the Mac and is **not committed** anywhere.
2. **Owner:** watch it and approve: "approve TML-TEST-20261128-01 for the private test".
3. **Claude Code (Mac):**
   - add the `approval` block (owner name and time, plus the four confirmations);
   - set `publishAt` about 15 minutes ahead;
   - run `bash worker/tools/stage_video.sh <export folder> root@<vps>`. This checks the SHA-256, language and format, then copies the folder privately to `/var/lib/tml-social/incoming/TML-TEST-20261128-01/`.
4. **Claude Code (VPS), with owner approval:** set `/etc/tml-social/worker.env` to
   ```
   TMLPUB_DRY_RUN=0
   TMLPUB_PRIVATE_ONLY=1
   TMLPUB_PLATFORMS=youtube_shorts
   ```
   Then `sudo systemctl start tml-social.service` and `journalctl -u tml-social -n 40`.
5. **Expected:** `TML-TEST-20261128-01|youtube_shorts|default: private_verified` within 1–3 five-minute cycles, an alert "private upload test … succeeded", and the video in **YouTube Studio → Content** as **Private**.
6. **Owner:** check it plays, is private, and has the right title, language and description. Reply "private test passed" (or what's wrong).
7. **Claude Code:** set `TMLPUB_DRY_RUN=1` again until the owner approves the publishing workflow.

Rollback at any point: `tmlpub.cli pause` (all platforms) or set `TMLPUB_DRY_RUN=1`.
