# Legal pages for the Google OAuth consent screen (TML Publisher)

## Live check (27 Nov 2026, 04:22 AEDT)
- https://twomarketledger.com/ returns 200, but it serves only the old minimal app shell.
- `/legal/privacy`, `/legal/terms`, `/privacy` and `/terms` all return **404**.
- www.twomarketledger.com redirects to twomarketledger.com.
- beta.twomarketledger.com returns **401** (password-protected), so Google cannot read it.

**So there are no live public privacy or terms URLs yet.**

## Proposed URLs (after approval and publication)
- Privacy policy: https://twomarketledger.com/legal/privacy
- Terms of service: https://twomarketledger.com/legal/terms
- Homepage: https://twomarketledger.com/

These are the same paths the public site already links to in `web/public/site.js`. Drafts: `PRIVACY_POLICY_DRAFT.md` and `TERMS_OF_SERVICE_DRAFT.md`.

## Publishing (needs separate owner approval: production server change)
The least-intrusive route serves the two approved pages as static HTML from nginx: two exact `location =` blocks on the production site. The app, database and beta are untouched. A full public-site deployment (PR #37) is separate and not needed for this.

## Google console notes
- **Testing:** an External app in "Testing" status does not need these URLs. But its refresh tokens expire after 7 days, which is unsuitable for the VPS worker.
- **In production:** needs the homepage and privacy policy on a domain verified in Google Search Console and listed under Authorised domains. `youtube.upload` is a sensitive scope: until Google verifies the app, the owner sees an "unverified app" warning and can still continue for their own channel.
- Uploads from unaudited API projects stay private (the worker already uploads private-first).
