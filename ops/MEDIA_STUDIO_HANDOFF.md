# Media Studio → publishing workflow: standard export contract (v2, 27 Nov 2026)

- **Media Studio:** a separate local project on the owner's Mac (`~/Documents/Projects/TML-Media-Studio`), owned by **Codex**. It covers English and Hindi production. Claude does **not** recreate or duplicate any rendering, narration, translation or conversion.
- **Claude:** owns the queue contract, the compliance checks, the VPS worker (YouTube) and the daily routines (Buffer).
- **Privacy:** unpublished videos and media **never** go into the public `tml-social-media` repository. Exports move from the Mac to the VPS's private staging folder over SSH (`worker/tools/stage_video.sh`). The worker refuses any video committed to the repository.

## 1. One folder per video: `exports/<contentId>/`
| File | Required | Specification |
|---|---|---|
| `video.mp4` | yes | H.264 (High), yuv420p, AAC 48 kHz stereo, `-movflags +faststart`, constant 30 fps. **Shorts and Reels: 1080×1920, ≤ 3 min** (60 s or less preferred). **Long-form: 1920×1080.** Maximum 500 MB. **Captions burned in** (see the captions row) |
| `manifest.json` | yes | Fields below |
| `captions.srt` | recommended | UTF-8 SRT in the video's language. Our OAuth scopes (upload, read-only) can't add caption tracks to YouTube, so on-screen (burned-in) captions are the standard. The SRT is kept for the record and for later use |
| `thumbnail.jpg` | long-form | 1280×720, under 2 MB, TML brand, no share prices or "buy" wording. Shorts use a frame from the video |

## 2. `manifest.json`
```json
{
  "contentId": "TML-HI-20261128-01",
  "language": "hi",
  "format": "short",
  "title": "महंगाई क्या है? | What is inflation? (≤ 100 characters)",
  "description": "2–5 short paragraphs of education. Sources listed. 'शिक्षा के लिए, वित्तीय सलाह नहीं। Education only. Not financial advice.'",
  "hashtags": ["#TwoMarketLedger", "#FinancialLiteracy"],
  "sources": [{"publisher": "Reserve Bank of India", "title": "...", "url": "https://...", "period": "Oct 2026", "retrieved": "2026-11-27"}],
  "asset": "video.mp4",
  "assetSha256": "<sha256 of video.mp4>",
  "durationSeconds": 58,
  "targets": [{"platform": "youtube_shorts"}],
  "publishAt": "2026-11-28T18:30:00+11:00",
  "status": "ready_for_review",
  "producedBy": "TML Media Studio (Codex)",
  "voice": "human | synthetic (disclosed)",
  "translationOf": "TML-EN-20261128-01 (optional)"
}
```
- **Unique video ID:** `TML-<LANG>-<YYYYMMDD>-<NN>`, for example `TML-EN-20261128-01` or `TML-HI-20261128-01`. Private tests use `TML-TEST-…`. IDs are never reused, even if a video is withdrawn.
- **Language:** `en` or `hi`. It is sent to YouTube as the default language and audio language. Hindi titles and descriptions may be bilingual.
- **Sources:** every figure, date or claim in the video comes from a primary official source, listed here. No figure means an empty list.
- **Status:** `draft`, then `ready_for_review` (Media Studio), then `approved` (recorded by Claude after the owner approves the exact file), then `scheduled` or `published` (worker). Media Studio never writes the `approval` block itself.
- **AI disclosure:** if the narration or footage is synthetic, `voice` says so, and the description includes "This video uses AI-generated narration." Hindi and English versions are each reviewed separately; translation is never auto-approved.

## 3. Flow
1. **Codex:** render to the specification and write `manifest.json` with `status: ready_for_review`. Tell Claude on issue #17 (ID, language, title). The files stay on the Mac.
2. **Claude:** run the policy check (FINANCIAL_CONTENT_RULES.md: no advice, trading, speculation or fast money; sources present), check the manifest and specification (`ffprobe` via Claude Code on the Mac), the duplicate check, and propose a time. Then ask the owner.
3. **Owner:** watches the exact file and replies "approve <contentId> for <time>". Claude Code adds the `approval` block, recomputes nothing (the SHA-256 must still match) and runs `stage_video.sh` to copy it privately to the VPS.
4. **VPS worker:** uploads to YouTube private first, with YouTube's own `publishAt` for public release, once public publishing is approved, and verifies. Buffer handles Instagram, Facebook and X once each through the routines. Those need a public file URL at publication time, which is a later decision; until then YouTube only.

## 4. Production target: English and Hindi
- Owner target: **at least one Hindi video a day**, subject to quality and approval, alongside English.
- A suggested slot is YouTube Shorts at **6:30 PM Melbourne** (1:00 PM IST, which suits Indian viewers), separate from the three image editions (9:30, 3:15, 7:30), which stay unchanged. This needs owner approval.
- The worker and the policy checks already accept `hi`. Review capacity is the real limit: every video needs the owner's approval of the exact file.

## 5. Questions for Codex (issue #17)
1. Can Media Studio export exactly this folder and manifest, so no manual conversion is needed? What changes would it need?
2. Please prepare **one new private test video that has never been published**, for example `TML-TEST-20261128-01`: a short neutral education clip, ≤ 60 s, English or Hindi, with `targets: youtube_shorts` and `"visibility": "private"`. Keep it on the Mac. Claude Code stages it.
3. What does Hindi production look like today: voice, translation review, fonts for burned-in Devanagari captions?
