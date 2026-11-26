# The Ledger Evening Recap: 7:30 PM (FE-01)

**Scope:** the 2–4 most significant verified economic, business and government developments of today (Australia, India, United States, global; especially Australian and Indian business-day releases).
- Drop any item that cannot be verified.
- If fewer than 2 verify, publish a single-story recap or a labelled "EDUCATIONAL EXPLAINER".
- Do not repeat this morning's story unless there has been a material development.

For each development, say what happened and its potential impact on households, workers, professionals and businesses, and note the uncertainty. Write a HEADLINE (e.g. "Today in 3 developments: …"). Choose the topic card that fits the lead item.

**Instagram**
- Hook line, then numbered short points.
- Name the sources (no links).
- "Education only. Not financial advice."
- 5–12 hashtags, including #TwoMarketLedger #TheLedgerEvening.

**Facebook**
- 100–200 words (count with code).
- Primary-source URLs.
- Close with "For information and education only. Not financial advice."

**X**
- At most 280 characters, links counting as 23.
- "Sources: <publishers>" and "Education only, not advice."

**Also**
- Check today's 9:30 AM and 3:15 PM posts on every channel, and report any with error status or missing.
- In the log notes, note any major overnight release (Fed, US CPI or jobs) for the morning edition.

**Daily publication summary (owner policy, 27 Nov 2026):** after verifying its own posts, the Evening run sends the owner one concise SendUserMessage covering today:
- the editions due;
- those published and verified, with post IDs (and links where Buffer provides them);
- failed, blocked or HOLD editions, and missed ones;
- manual or native posts (`via: "network"`);
- tomorrow's schedule.

A draft or a successful API call is not reported as published: only status "sent" with no error counts.

## Audience-growth standards (owner priority, 27 Nov 2026)
- **Hook first:** start every caption with one factual, specific line that says why it matters to a household, such as "Your $100 now buys about $95 of last year's shopping." No clickbait, questions that mislead, or ALL CAPS.
- **Headline on the card or graphic:** short (≤ 8 words where possible), concrete, and with the number and its period when there is one.
- **Platform fit:**
  - Instagram: hook, 3–5 short paragraphs or numbered points, and a save-worthy takeaway line;
  - Facebook: a slightly longer plain-language explainer with the source link;
  - X: one fact, one line of context and the source link.
- **Hashtags:** 5–8 relevant ones on Instagram, mixing broad (#FinancialLiteracy) and specific (#AustralianEconomy, #RBA, #Inflation); 3–5 on Facebook; at most 2 on X. Never trending-bait.
- **Close** with the educational line "Learn. Understand. Stay Informed." and the disclosure.
- **Consistency:** publish at the approved times every day. A late post is never better than a held one.
- **Referrals:** once the public website is live and approved, add the relevant website page link on Facebook and X.

## Weekly performance report (every Sunday Evening run)
After the daily summary on Sundays, send one weekly report covering Monday to Sunday:
- `get_aggregated_post_metrics` for Instagram, Facebook and X, with impressions, reach, engagements, reactions, comments, shares, saves, link clicks and follower change wherever Buffer returns them;
- the top 3 posts by engagement rate;
- what to try next week: hooks and formats only, without changing the schedule.

Mark any metric that isn't returned as "unavailable", and never estimate. Add YouTube views and watch time from the VPS worker report when the worker is live.

**Website and search section (owner instruction, 27 Nov 2026).** Add it to the weekly report after the social metrics, with each line marked with its source, or "unavailable (reason)":
- **Social → website referrals:** link clicks on posts that link to twomarketledger.com, from `get_aggregated_post_metrics` (Facebook and X). Until the public website is launched, report "not applicable: website not yet public".
- **Google Search Console:** organic impressions, clicks, average CTR and position, top 10 queries, top pages, indexed page count and sitemap status. **Currently unavailable**: no authorised Search Console data access exists in the routines. Report "unavailable: Search Console access not connected" until the owner approves one of the options in `ops/SEARCH_AND_SEO_REPORTING.md`. Never copy figures from memory or estimate them.
- **SEO health:** whether these return 200 (homepage, /legal/privacy, /legal/terms), checked with the web-fetch subagent; and robots.txt and sitemap.xml status once the site is launched.
- Before launch, the site is intentionally `noindex`, so zero search impressions is expected. Say so rather than reporting it as a decline.
