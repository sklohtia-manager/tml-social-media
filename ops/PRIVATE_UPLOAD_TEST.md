# One private automated YouTube upload test

**Goal:** prove, end to end on the VPS, that the worker can upload one owner-approved Media Studio video to the **Two Market Ledger** channel as **private**, verify it, and report it, without anything becoming public.

## Safety gates (all in code and tested)
- `TMLPUB_PRIVATE_ONLY=1` (the default): even with live mode on, only manifests marked `"visibility": "private"` are uploaded. Every ordinary video stays dry-run.
- A private test must use a `TML-TEST-` content ID and target YouTube only. The real video's later publication is therefore never treated as a duplicate.
- **Privacy:** the upload is `private`, and no `publishAt` is sent, so YouTube never makes it public on its own. If YouTube reports it as anything other than private, the worker marks it `needs_review` and alerts you.
- **Channel check:** the token must belong to the confirmed Two Market Ledger channel ID, or nothing is uploaded.
- **Never repost:** TML-YT-001 and TML-YT-002 are excluded. Use a new Media Studio video, or one you explicitly choose.

## Steps
1. **Owner:** choose the approved Media Studio video and tell Claude its name. No file goes through chat.
2. **Claude Code (Mac), with owner approval:**
   - put the MP4 at `media/TML-TEST-PRIVATE-001/video.mp4` in `tml-social-media`;
   - copy `ops/templates/private-upload-test.json` to `queue/TML-TEST-PRIVATE-001.json` and fill in the title, SHA-256, a `publishAt` about 15 minutes ahead, and the owner approval (name and time);
   - commit and push.
   - **Note:** the repository is public, so the file is visible on GitHub from then on. For a test, use a video you're happy to have visible, or one already released elsewhere.
3. **Claude Code (Mac), on the VPS:** set `/etc/tml-social/worker.env` to
   ```
   TMLPUB_DRY_RUN=0
   TMLPUB_PRIVATE_ONLY=1
   TMLPUB_PLATFORMS=youtube_shorts
   ```
   Then `sudo systemctl start tml-social.service` and `journalctl -u tml-social -n 40`.
4. **Expected:**
   - `TML-TEST-PRIVATE-001|youtube_shorts|default: private_verified` (it may take 1–3 cycles of 5 minutes while YouTube processes the video);
   - an alert "private upload test … succeeded";
   - the video appears in **YouTube Studio → Content** as **Private**.
5. **Owner:** in YouTube Studio, check the video plays and is private, and that the title and description are right. Tell Claude "private test passed" (or what's wrong).
6. **Reset (Claude Code):** set `TMLPUB_DRY_RUN=1` again until the owner approves the future workflow. The private video can stay private or be deleted in Studio; that's your choice.

Rollback at any point: `tmlpub.cli pause` (all platforms) or set `TMLPUB_DRY_RUN=1`.
