# Media Studio → publishing workflow (contract proposal for Codex)

**Goal:** finished Media Studio videos enter the publishing queue **without manual file conversions or duplicate work**. Codex owns Media Studio; Claude owns this repository's queue, worker and daily routines.

## What Media Studio exports per finished video (one folder)
| File | Specification |
|---|---|
| `video.mp4` | H.264 High profile, yuv420p, AAC 48 kHz, `+faststart`; **1080×1920 vertical, ≤ 3 min** for Shorts and Reels (≤ 60 s recommended); 1920×1080 for long-form. **≤ 95 MB** (GitHub's per-file limit; Buffer fetches from the raw URL) |
| `captions.srt` | Optional but recommended; UTF-8, matches the narration |
| `thumbnail.jpg` | Optional, 1280×720 (long-form only) |
| `manifest.json` | The queue manifest below, **without** the `approval` block |

`manifest.json` fields (validated by `worker/tmlpub/manifest.py`):
- `contentId`: `TML-YT-###` for episodes, or `TML-SHORT-###`;
- `title` (≤ 100 characters);
- `caption` and/or `description`: education framing, and the line "Education only. Not financial advice.";
- `asset` (`media/<contentId>/video.mp4`) and `assetSha256`;
- `targets`: any of `youtube`, `youtube_shorts`, `instagram_reels`, `facebook_reels`, `x`;
- `publishAt`: the owner's chosen time with its offset.

Media Studio **must not** set `approval`. The owner approves the exact file. Claude then records `approvedBy`, `approvedAt` and the four release-gate confirmations (narration, rights, captions, playback). Any change to the file changes the SHA-256 and invalidates the approval.

## Flow
1. **Codex (Media Studio):** render, then export the folder to `tml-social-media/media/<contentId>/` and the manifest to `queue/<contentId>.json` (unapproved). Commit to a branch `media/<contentId>` and open a pull request. No conversion step is needed afterwards.
2. **Claude:**
   - run the compliance lint and the policy check (FINANCIAL_CONTENT_RULES.md: no advice, trading or fast-money framing);
   - check the specifications with `ffprobe`;
   - confirm the content ID is not in the manual ledger (`queue/manual/`);
   - report to the owner.
3. **Owner:** watch it and approve the exact version. Claude records the approval and merges.
4. **Distribution:**
   - **VPS worker:** YouTube and Shorts (official API);
   - **Buffer** through the daily routines: Instagram Reels, Facebook Reels and X video, once each, carrying "Ref: <contentId>" (`ops/BUFFER_VIDEO_SCHEDULING.md`);
   - TikTok and WhatsApp stay manual (a posting pack is prepared).
5. **Verification and the ledger:** the worker records `published_verified`; the routines record their Buffer post IDs. The daily and weekly reports include videos.

## Open questions for Codex (please answer on issue #17)
1. Where does Media Studio live (repository and path), and what does it output today (codec, size, duration, captions)?
2. Can it export directly to the specification above, so nothing needs converting?
3. Which finished video should be used for the single private YouTube test (`ops/PRIVATE_UPLOAD_TEST.md`)?
