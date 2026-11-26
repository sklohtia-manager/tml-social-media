# Search Console and SEO in the weekly report

**Status (27 Nov 2026):**
- Search Console ownership of twomarketledger.com is verified (Domain property).
- The website is not yet public: production runs the old private build, and the new public site is `noindex` until the owner approves launch.
- Organic search data is therefore expected to be zero or near zero.
- No routine or service has authorised Search Console data access, so the weekly report marks these metrics **unavailable**.

## What the report tracks once access exists
| Metric | Source | Available now? |
|---|---|---|
| Organic impressions, clicks, CTR, average position (week and previous week) | Search Console → Performance (Search Analytics API) | No |
| Top queries and top pages | same | No |
| Indexed pages; pages not indexed and why | Search Console → Indexing → Pages | No |
| Sitemap status and URL count | Search Console → Sitemaps | No (no sitemap until launch) |
| Website referrals from social posts | Buffer link-click metrics | Yes, when posts link to the site |
| Website visits | none: the public site deliberately has no analytics or trackers | No (by design) |
| Legal and SEO page availability (200 checks) | web-fetch from the Evening routine | Yes |

## Options for authorised Search Console access (owner decision; all free)
1. **Manual (no setup):** each Sunday the owner opens Search Console → Performance and tells Claude the four headline numbers. The report then marks them "owner-reported".
2. **Through the VPS worker (recommended after launch):**
   - add the read-only scope `https://www.googleapis.com/auth/webmasters.readonly` to the `tml-publisher` OAuth project;
   - re-run the Mac sign-in helper;
   - the worker sends a weekly website-and-search summary alongside its daily report.
   - **Before this:** the privacy policy must be updated to disclose the extra scope (a new draft for approval), and the consent-screen scopes list updated.
3. A Search Console connector in Claude, if one becomes available to the routines at no cost.

Until the owner chooses, the report says: "Search Console: unavailable (no authorised access connected)."
