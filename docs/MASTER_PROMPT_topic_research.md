# Master prompt: topic-research skill

> **owner-এর জন্য:** এই প্রম্পটটা দিয়েই `topic-research` skill বানানো হয়েছে। পরে নিয়ম বদলাতে চাইলে নিচের "Requirements" অংশে বদল করে Claude Code-এ পুরো প্রম্পটটা পেস্ট করবেন। তখন Claude Code skill-টা নতুন করে সাজাবে, কিন্তু `upload-kit`-এর সাথে যোগসূত্র ভাঙবে না।

---

Build or update the Claude Code skill at `.claude/skills/topic-research/` for the faceless YouTube channel The Unmapped Page: map-led documentaries about places, borders and maps that were wrong, faked or forgotten. Read the existing `.claude/skills/upload-kit/` first; both skills must work together as one pipeline. Do not touch finished episodes.

## Goal

Pick the next episode topic from real audience demand, then research it to a standard where every fact in the narration can be traced to sources. Nothing invented, nothing inconsistent, nothing taken from memory.

## Requirements

### Audience

- Primary audience: United States and United Kingdom.
- Secondary audience: Canada, Australia, Ireland and New Zealand.
- Every demand number must say which country it covers, or that it is global.

### Tools

- Only free tools are allowed. The owner has no paid tools.
- YouTube Data API v3 with a free key. `search.list` has its own bucket of 100 calls per day; other methods share 10,000 units per day.
- YouTube Studio's own free tools, read through Chrome: the Analytics → Trends tab (audience interest, top searches, content gaps; screenshots) and Advanced mode CSV exports.
- Google Trends with the YouTube Search property. There is no free official API, so the CSVs are downloaded through Chrome, with one anchor term repeated in every batch. When Chrome is not available (phone or cloud sessions), fetch the same data through SerpApi's free plan (`SERPAPI_KEY`) into the same CSV layout.
- Phone route for YouTube Studio, which has no free API for the Trends tab: the owner attaches screenshots of the Trends tab (and, for Part C, of an episode's geography, traffic source and search terms) to the `/topic-research` message, and the skill reads them exactly as shown.
- Wikimedia pageviews API.
- Library of Congress loc.gov API, including Chronicling America.
- Internet Archive.
- Wikidata.
- Wikimedia Commons.
- National archives and libraries of the US and UK.
- Web search and fetch.
- Any limit or endpoint the skill states must be checked against the provider's own page, with the check date written down.

### Autonomy

- `/topic-research [theme]` runs the whole topic choice without asking the owner anything.
- The only pause is a login or CAPTCHA page in Chrome.
- Studio and Google Trends data are collected through the Claude in Chrome tools in the owner's signed-in browser, at a human pace and read-only.
- If a tool is unavailable, carry on and mark that signal NOT COLLECTED. Never estimate it.
- The 3 finalists get a deep check with three gates:
  - 2 opened T1/T2 sources
  - the opening fact verified by 2 sources
  - a license-safe map
- A script picks the winner from fixed weights, gates and tie rules.
- The run ends with one Bengali message: "এই টপিকে আগাবেন স্যার: …". Part B starts only after the owner says go.
- A project `.claude/settings.json` allows the skill's scripts, web search and fetch, and the Chrome tools, and blocks reading `.env`.

### Demand step

- Score about 10 candidate topics. Each score part needs evidence (a number plus where it came from).
- Missing evidence scores 0 and is flagged. It is never estimated.
- Use these signals, and state what each one can and cannot show:
  - Studio Trends tab: audience interest and content gaps.
  - YouTube results per region: views per day, fresh views from the last 12 months, recent uploads, and breakout videos from small channels.
  - Viewer questions: YouTube comments that ask for topics, and Reddit (r/AskHistorians, r/MapPorn, r/geography) as T4 leads.
  - Trends interest for US and GB on YouTube Search.
  - Wikipedia pageviews, labelled as global.
- Give each topic a confidence level. When signals disagree, show the conflict instead of averaging it.
- Low search interest is not the same as low demand, because map documentaries get much of their audience from browse and suggested videos.

### Research step

- Keep a source list and a claim ledger.
- Use source tiers:
  - T1: primary documents, records, contemporary newspapers, original maps.
  - T2: scholarly sources.
  - T3: reputable reference works and journalism.
  - T4: leads only (Wikipedia, blogs, videos, AI answers).
- A VERIFIED claim needs at least 2 independent sources, at least one of them T1 or T2.
- Sources that copy the same origin count once.
- Record numbers with the exact source wording.
- Derived numbers show their formula.
- When sources conflict, record both. The script either says they disagree or drops the claim.
- Quotes must be verbatim, with their location in the source.
- For pre-1752 British dates, note Old Style or New Style.
- A primary source proves what it said, not that it was true; word such claims as attributed.
- Treat circular sourcing (journalism copying Wikipedia) as T4.
- Write the script in its own words apart from short attributed quotes.
- Give each historical place name with its modern equivalent.

### Script gate

- A checker blocks any number in the script, description or pinned comment that is not in a VERIFIED or CONTESTED ledger row (derived figures included).
- A fresh subagent that did not write the script (`.claude/agents/fact-auditor.md`) audits it against the ledger before voice-over, checks up to 10 cited URLs, and must report PASS.

### Assets

- Every image or map gets its license recorded at source.
- Public domain, CC0, CC BY and CC BY-SA are allowed.
- Any NC (non-commercial) or unclear license is not used without written permission, because the channel is monetized.

### Feedback from published episodes

- At the start of each run, for every episode at least 28 days old without feedback, Claude Code exports Studio Advanced mode CSVs (geography, traffic source, YouTube search terms) through Chrome and summarises them.
- Real channel data outranks outside signals.

### Hand-off to upload-kit

- `upload-kit` reads the research folder for its SEO step, its SOURCES and CREDITS sections, and the claim check. It does not repeat the demand research.

### Formats and safety

- Output files in the episode folder.
- Owner-facing notes in Bengali; viewer-facing text in English.
- Scripts run offline-testable, with fixtures.
- Never publish anything. Keep within API quotas. Send a descriptive User-Agent to Wikimedia.
