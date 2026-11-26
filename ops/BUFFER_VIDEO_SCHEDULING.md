# Can our existing Buffer plan schedule videos? (checked 27 Nov 2026, 03:31 AEDT)

**Short answer: yes for Instagram, Facebook and X, at no cost; no for YouTube on the current plan.**

| Check | Result |
|---|---|
| Buffer organisation limits (`get_account`, live) | 3 channels, 10 scheduled posts at a time. Channels used: Instagram, Facebook, X (LinkedIn connected but locked). |
| Buffer publishing tool (`create_post`) | Accepts a **video asset** from a public, directly downloadable URL. Instagram: type `reel` (shared to feed). Facebook: type `reel` or a video post. X: native video. YouTube: type `short` or `regularVideo`, but only for a connected YouTube channel. |
| YouTube through Buffer | Needs a 4th channel. The free plan has 3, so this means a paid plan or disconnecting one of the three. **Neither is authorised.** |
| TikTok, WhatsApp | TikTok would also need a channel slot; WhatsApp is not a Buffer channel. Both stay manual. |

Not yet tested end to end: no real video has been scheduled through Buffer, because every video needs owner approval first and we must not repost TML-YT-001 or TML-YT-002. The first approved Short will be the test, scheduled once per platform with "Ref: <contentId>".

## Recommendation (simplest route, A$0)
1. **Instagram Reels, Facebook Reels and X video: Buffer**, scheduled once from the approved file's raw GitHub URL (≤ 100 MB per file), the same way the image editions work. This means **the Meta Graph API setup is not needed** for publishing. It stays documented as an optional later step (and the worker's Meta adapter stays disabled).
2. **YouTube and YouTube Shorts: the VPS worker** through the free YouTube Data API (default 10,000 quota units a day; an upload costs far less than that, and the exact figure is checked in the Google Cloud console during setup), private first. This is the only part that needs Google Cloud.
3. **Buffer's 10-post limit:** daily editions are created at 9:00, 2:30 and 7:00 for the same day, so the queue normally holds 0–3 posts. A video uses one slot per platform; schedule it no more than 24 hours ahead.
4. The worker's manual ledger (`queue/manual/`) and the routines' "Ref:" check together stop any video being posted twice.

The owner makes the final choice. The Meta setup screens remain in `ops/VIDEO_PLATFORM_SETUP.md` if wanted later.
