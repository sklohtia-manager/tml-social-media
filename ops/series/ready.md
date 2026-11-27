# 3:15 PM financial education edition (formerly titled "Are You Financially Ready for Tomorrow?"; founder authorisation 26 Nov 2026)

A daily financial-education, brand-awareness and preparedness series. Each post explains why Two Market Ledger exists: helping everyday people understand how economic change affects their lives, families, savings and future, beyond salary, bills and property. It never recommends products or sells.

**Theme:** use the least recently used theme. No theme is repeated within 12 days (check the series log and recent sent posts). Do not repeat today's Morning story. "Inflation and purchasing power" was covered on 26 Nov 2026.

| # | Theme | Topic card |
|---|---|---|
| 1 | Financial freedom and long-term preparedness | resilience |
| 2 | Inflation and purchasing power | inflation |
| 3 | Cost of living and household finances | cost-of-living |
| 4 | Thinking beyond property ownership | beyond-property |
| 5 | Understanding international economies | trade |
| 6 | Asset classes and diversification (concepts only) | beyond-property (or a matching new card) |
| 7 | Retirement and children's education | retirement or education-costs |
| 8 | Employment and income uncertainty | jobs-wages |
| 9 | Manufacturing, technology and emerging industries | growth |
| 10 | Historical economic crises and their lessons | economic-history |
| 11 | Building financial awareness using existing income | cost-of-living |
| 12 | Income vs wealth | income-wealth |

"Financial freedom" means long-term preparedness built steadily, never quick wealth.

**Flow:** what's happening → why it matters to ordinary people → how it could affect our future → a reflective question (no fear) → why financial education and Two Market Ledger matter.

**Instagram**
- Hook, then short paragraphs.
- Name the source (no links).
- "Education only. Not financial advice."
- 5–12 hashtags, including #TwoMarketLedger and the series tag #TMLEducation.

**Facebook**
- 100–200 words.
- Primary-source URL.
- End with "For information and education only. Not financial advice."

**X**
- At most 280 characters: one sharp fact and one question.
- "Source: <publisher>", "Education only, not advice." and the link.
- At most 2 hashtags.

**WhatsApp status (founder's personal sharing; never posted by us)**
- Render a fresh 1080×1920 image of today's topic: write a spec JSON with `edition: "ready"`, the actual topic as `headline`, a `takeaway`, optional `blocks` (short definitions) or a figure (with its period), and a `source` line that includes the publisher and date whenever a figure is shown. Add `question: true` only under the signature rule below. Then run `python3 tools/render.py spec.json /tmp/out`.
- Inspect the image.
- SendUserFile it (status proactive) with the caption "3:15 PM: <headline>" plus a 1–2 line WhatsApp caption.
- Send it every day the content is ALLOW, including a missed edition saved as drafts (then add "(today's posts are drafts, not published)" to the caption). If the edition is HOLD, send nothing; the notification covers it.

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

## Educational fallback (owner instruction, 27 Nov 2026)
If today's edition cannot be produced or verified, follow RUNBOOK §1B: use the next owner-approved item from `content/evergreen/ready/` (see `ops/EVERGREEN_BANK.md`), labelled "education edition", and notify the founder. Never present it as news. The WhatsApp image for a fallback day uses the item's title as the headline, with no figure.

## Post template and signature rule (owner instruction, 27 Nov 2026; overrides anything above)
- **Signature line (approved, owner decision 27 Nov 2026).** "Are you financially ready for tomorrow?" is an **approved Two Market Ledger signature line** and stays **available as an optional line in every template** (captions, graphics and videos). It is not a default and not a header, footer or label.
  - **When:** use it when the topic naturally connects to financial preparedness, resilience or planning ahead (for example the financial resilience post). For everyday explainers such as "Income vs net wealth", don't use it; let the topic's own takeaway close the post.
  - **How often:** once per piece. In a post with an image, it appears in the caption or on the image, never both.
  - **Where:** near the end, ideally as the **second-last line of the body**, with a natural lead-in sentence before it and a short closing line after it that completes the thought. The source line, disclaimer and hashtags follow as usual. Example: "A buffer is one way of planning ahead, so a surprise stays manageable. / Are you financially ready for tomorrow? / Knowing your essential monthly costs is where preparedness begins."
  - **Videos:** the narrator says it once, near the end, with the same lead-in and closing, ahead of the closing brand line.
  - **Fear-free:** it is reflective, never urgent, never a product steer, never tied to a market move.
- **Graphic:** keep the green-and-gold layout and the TML logo. The headline is the **actual topic** (for example "Income vs net wealth"), never a generic "Financial education explainer". The graphic carries **one clear takeaway**, plus, where helpful, a short definition, example or verified figure. Text must be readable on a phone (`tools/render.py` enforces at least 30 px body text at 1080 px wide).
- **Statistics on images:** a current statistic on the image must show its source and date on the image. The pre-rendered topic cards carry no statistics, so figures from scheduled runs go in the caption.
- **Examples:** hypothetical examples are labelled ("Hypothetical example" or "Illustration") on the image and in the caption.
- **Caption:** extra context, the definitions' or figures' source, and links. Factual and educational only.
- **Topic card choice:** the card title must accurately describe the post. If no card fits, use the closest card whose title is still accurate (for example "Finances beyond property"), never an inaccurate one. Concept cards for the coming week's calendar topics are rendered and pushed in advance by an interactive session (`tools/build_cards.py` and `ops/topic-cards.json`).
