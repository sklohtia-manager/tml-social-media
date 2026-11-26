# Proposed automated video publishing workflow (for owner approval after the private test passes)

**Status:** proposal. Nothing here is active. Public automated video publishing stays off (`TMLPUB_PRIVATE_ONLY=1`) until the owner approves this document after a successful private upload test.

## Cadence (owner policy)
Initially 2–3 Shorts or Reels a week, plus one longer educational video when ready. Reviewed after two weeks of real engagement data.

## Languages
English and Hindi. Owner production target: at least one Hindi video a day, subject to quality and approval. A suggested Hindi Shorts slot is 6:30 PM Melbourne (1:00 PM IST); this needs owner approval. The three daily image editions are unchanged.

## Per video
1. **Media Studio (Codex)** exports a finished video to the specification (`ops/MEDIA_STUDIO_HANDOFF.md`) on the Mac. It is never committed to Git. After approval it is staged privately on the VPS with `worker/tools/stage_video.sh`.
2. **Claude** runs the policy and compliance checks (no advice, trading or fast-money framing; sources for any figure), the format check, the duplicate check against the manual ledger, and proposes a publishing time and captions.
3. **Owner** watches the exact file and replies "approve <contentId> for <date/time>". Claude records the approval. Any edit invalidates it.
4. **YouTube and Shorts (VPS worker, official API):**
   - uploaded privately up to 6 hours before release, with YouTube's own `publishAt` set to the approved time;
   - YouTube makes it public at that time, and the worker verifies "public and processed" within 2 hours;
   - it is never published late, and alerts are sent on any problem.
5. **Instagram Reels, Facebook Reels and X video (Buffer, existing plan, no new cost):** the daily routine schedules each platform once at the approved time with "Ref: <contentId>", and the duplicate check runs first.
6. **TikTok and WhatsApp:** a manual posting pack is sent to the owner.
7. **Reporting:** the daily summary lists video posts; the Sunday report adds YouTube views and watch time where available, or marks them unavailable.

## Switch-on (after approval)
`/etc/tml-social/worker.env`:
```
TMLPUB_DRY_RUN=0
TMLPUB_PRIVATE_ONLY=0
TMLPUB_PLATFORMS=youtube,youtube_shorts
```
Emergency stop: `tmlpub.cli pause` or `TMLPUB_DRY_RUN=1`.

The three daily image editions (9:30, 3:15 and 7:30) are unchanged by any of this.
