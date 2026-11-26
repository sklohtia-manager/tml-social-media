# Owner setup guide: YouTube, Meta (Instagram and Facebook Reels) and TikTok

Everything here is free. **Never paste passwords, secrets or tokens into a chat, email or Git.** The helper scripts read secrets at hidden prompts and write files only on your Mac, which you then copy to the VPS.

## A. Google Cloud and the YouTube Data API (about 20 minutes)
1. Go to <https://console.cloud.google.com/> and sign in with the Google account that **owns or manages the Two Market Ledger YouTube channel**.
2. In the top bar choose **Select a project → New project**. Name it `tml-publisher`, then **Create**.
3. Open **APIs & Services → Library**. Search for **YouTube Data API v3**, open it and click **Enable**.
4. Open **Google Auth Platform → Branding** (older consoles call this "OAuth consent screen"):
   - app name `Two Market Ledger` (must match the website brand; see the website repository, `ops/google/GOOGLE_VERIFICATION_AND_SEO.md`);
   - user support email and developer contact: your email;
   - **Audience → External**;
   - (Test users are only needed while in Testing; the project is already "In production".)
5. **Data access → Add or remove scopes.** Add `.../auth/youtube.upload` and `.../auth/youtube.readonly`, then save.
6. **Audience → Publish app** (status "In production"). Leave it unverified; that's fine for your own channel. Important: in "Testing" status Google expires refresh tokens after 7 days, which would stop uploads weekly.
7. **Clients (Credentials) → Create client → Application type: Desktop app**, named `tml-worker`. **Download JSON** and keep it on your Mac only.
8. **Token generation on the Mac:** follow `ops/YOUTUBE_TOKEN_SETUP.md` step by step.
9. **Upload limits (checked on Google's own pages, 27 Nov 2026):**
   - the videos.insert documentation now says "Videos uploaded from unverified API projects are not restricted to private viewing mode";
   - quota: "100 calls per day … 1 unit in the Video Uploads quota bucket";
   - the worker still uploads **private first** (owner policy) and sets the approved publish time;
   - the YouTube API compliance audit is only needed to request more quota.

## B. Meta: Instagram Reels and Facebook Reels (about 30 minutes)
1. **Link Instagram to the Page:** in Facebook, open the **Two Market Ledger** Page, then **Settings → Linked accounts → Instagram**, and connect **@twomarketledger** (a professional account). In Instagram, check **Settings → Accounts Center → Sharing across profiles** and keep automatic sharing to Facebook **off**, so nothing is posted twice.
2. Go to <https://developers.facebook.com/apps/> and choose **Create app**:
   - use case **Other**, type **Business**;
   - name `Two Market Ledger Publisher`, linked to your business portfolio if asked.
3. Stay in **Development** mode. As the app's admin you can grant these permissions for your own Page and Instagram account without App Review.
4. Open **Tools → Graph API Explorer**:
   - select your app;
   - add the permissions `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `publish_video`, `instagram_basic`, `instagram_content_publish` and `business_management`;
   - click **Generate Access Token** and approve **Two Market Ledger** and **@twomarketledger**.
5. In **App settings → Basic**, note the **App ID** and click **Show** for the **App Secret**. Don't copy them anywhere except the script prompt.
6. On the Mac, in `worker/tools`, run `python3 meta_auth.py`. Paste the App ID, the App Secret and the Explorer token at the hidden prompts. It writes `meta.json` containing a long-lived Page token.
7. Copy `meta.json` to `/etc/tml-social/meta.json` on the VPS, the same way as step A9, then delete it from the Mac.

## C. TikTok (investigated: manual for now)
- TikTok's Content Posting API needs a registered developer app.
- **Unaudited apps can only post with private (SELF_ONLY) visibility.** Public "Direct Post" requires TikTok's audit.
- Recommendation: keep TikTok manual. The worker prepares a manual pack (video, caption and hashtags). Revisit after the audit, if wanted.

## D. X and WhatsApp
- **X:** stays on Buffer. Approved videos for X go out through the Buffer routines, never through the worker, so nothing is posted twice.
- **WhatsApp Status:** stays manual. The 3:15 PM routine sends you the daily status image.

## E. After setup (with Claude)
1. Claude Code on the Mac installs the worker (`sudo bash worker/install.sh`). It stays disabled and in dry-run mode.
2. Run `tmlpub.cli health`: it checks both tokens without publishing.
3. Upload one owner-approved test video **privately** to YouTube and record its video ID.
4. One owner-approved live test per platform.
5. With your approval, set `TMLPUB_DRY_RUN=0` and `TMLPUB_PLATFORMS=youtube,youtube_shorts,instagram_reels,facebook_reels` in `/etc/tml-social/worker.env`, then enable the timers.
