# Platform readiness matrix (27 Nov 2026)

| Platform | Current method | Automated? | Verified | Gaps and requirements | Cost |
|---|---|---|---|---|---|
| Facebook Page | Buffer (official Meta integration) via Claude cloud routine | Yes: image posts | Published 26 Nov 19:30 (6b07e7ebaca86124808ed14d) | Video and Reels via Buffer are untested | A$0 (Buffer free) |
| Instagram (business) | Buffer | Yes: image posts | Published 26 Nov 19:30 (6b07e7ebf13f49a925a26a65) | Reels untested. Owner to check the IG→FB auto-share setting stays off | A$0 |
| X | Buffer | Yes: image posts | Published 26 Nov 19:30 (6b07e7ecf13f49a925a26a9d) | Video untested | A$0 |
| YouTube and Shorts | None | No | — | YouTube Data API: OAuth client, channel verification, resumable upload (1,600 quota units per upload; default 10,000 units a day). **Videos uploaded through unaudited API projects are locked private until Google's audit.** Alternatively, the native YouTube Studio scheduler. Buffer's free plan has no 4th channel | A$0 (API quota) |
| TikTok | None | No | — | The Content Posting API needs an app audit for Direct Post; until then, upload only to drafts or the native scheduler | A$0 |
| WhatsApp Status | Manual pack | No (by policy) | 1080×1920 image sent to the owner daily | No official Status API; stays manual | A$0 |
| LinkedIn | Deferred | No | — | A company page and the owner's decision are needed | — |
