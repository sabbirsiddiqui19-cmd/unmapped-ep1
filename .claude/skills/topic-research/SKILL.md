---
name: topic-research
description: Pick the next The Unmapped Page topic on its own from US/UK audience demand using only free tools, deep-check the finalists, and report one recommended topic; then, on the owner's go-ahead, research it into a source list and claim ledger. Use when the owner asks for topic research or types /topic-research, and whenever a fact in a script needs checking.
argument-hint: "[optional theme, e.g. phantom islands]"
---

# Topic research

This skill has three parts.

- **Part A** runs on its own from start to finish: it collects demand data, checks the finalists, picks the best topic, and ends with one short recommendation to the owner.
- **Part B** starts when the owner says to go ahead (for example "আগাও"). It researches the chosen topic until every fact the narration will use is in the claim ledger.
- **Part C** collects what published episodes show about real viewers, and feeds it into the next Part A.

If the owner gives a theme (`$ARGUMENTS`), keep the candidates inside that theme.

## How Part A runs

- Do not ask the owner anything during Part A. Make each decision with the rules below and write it in `run_log.md`.
- The only pause is when Chrome shows a login page or a CAPTCHA. Claude Code stops there on its own; the owner handles it and the run continues.
- Each signal has a desktop route and a phone route (see "Which route to use" below). Try the routes in order. Only when every route for a signal fails (no key, quota used up, a page that will not load after one retry), carry on without it and mark it `NOT COLLECTED` in the scores and in the report, with the reason. Never fill the gap with an estimate.
- Work at a human pace in the browser: one page at a time, a few seconds between searches, no bulk scraping.

Hard rules:

- Only free tools. No paid tools, no trial credits. A free plan that needs only a sign-up (SerpApi's 250 searches a month) is allowed; never upgrade it.
- No fact comes from memory, from an AI answer, or from a source that was not opened in this session. If something cannot be found, it is written down as unknown.
- Every number has a country or "global" label, a source, and a date.
- `PUBLISH = NO`. Nothing is posted anywhere, and no YouTube setting is changed; in Studio, only read.

`SOURCES.md` in this folder lists the free sources, their access rules and license traps. Its check date is at the top; if it is older than 3 months, re-check the quota and rate-limit pages it cites before using the scripts.

## Audience priority

| Priority | Countries | Region codes |
|---|---|---|
| Primary | United States, United Kingdom | `US`, `GB` |
| Secondary | Canada, Australia, Ireland, New Zealand | `CA`, `AU`, `IE`, `NZ` |

Demand evidence from US and GB carries the most weight. Global figures are used only as context and are always labelled "global".

## Part A: choose the topic

Work in `episodes/_candidates/<YYYY-MM-DD>/`. Start `run_log.md` there with the date, the theme if one was given, and which tools are available (YT_API_KEY set or not, SERPAPI_KEY set or not, Chrome tools present or not, screenshots attached or not, search calls left today if known).

### Which route to use

The owner often starts runs from the Claude phone app, where Claude Code runs in a cloud session without Chrome. Check `run_log.md`'s tool list and pick the first route that is available for each signal:

| Signal | 1. Desktop route | 2. Phone route |
|---|---|---|
| Studio Trends tab | Chrome tools (A3) | Screenshots the owner attached to the `/topic-research` message (A3) |
| Google Trends | Chrome download (A3) | `trends_serpapi.py` with `SERPAPI_KEY` (A3) |
| Part C channel analytics | Chrome Advanced mode export | Screenshots the owner attached (Part C) |
| Reddit | Chrome, read-only | Web search and fetch |

Screenshots attached to the message are visible in the conversation and are also saved as files with the message; copy each one into the run folder before using it.

### What each free signal can and cannot show

Read this before scoring. No free tool gives YouTube search counts per country, so the score combines several partial signals and says how sure it is.

| Signal | What it shows | Country | Limits |
|---|---|---|---|
| YouTube Studio → Analytics → **Trends** tab (via Chrome) | "Audience interest" from very low to very high, top searches, and content gaps (searches with too few good results), all over the last 28 days | Not selectable | No API; some insights are limited to certain countries and languages |
| Google Trends, YouTube Search property | Relative interest over 5 years | US and GB chosen separately | 0-100 index, not counts; low-volume terms show 0 |
| `yt_demand.py` (YouTube Data API) | Views, upload dates and breakout videos among search results | Results viewable in US/GB | Shows supply and how well it performs, not searches |
| Viewer questions: YouTube comments, and Reddit (r/AskHistorians, r/MapPorn, r/geography) | What people ask about and react to | Not known | Small sample; Reddit is T4 and never a fact source |
| Wikipedia pageviews | Lasting interest in the subject | Global only | Not YouTube, not per country |
| The channel's own analytics (Part C) | Real share of US/UK viewers, traffic sources, search terms that found the channel | Real | Only for topics already published |

Map documentaries get much of their audience from browse and suggested videos rather than search. A low search signal does not mean no demand. Strong breakouts from small channels are the best free sign of browse demand.

### A1. Candidate list → `candidates.md`

Write 10 to 12 candidates. Each one gets:

- a one-line hook
- the map angle (what the map shows that words cannot)
- its Wikipedia article title, checked that it exists
- one or two search phrases a viewer would type

Ideas come from:

- requests in comments on the channel's own videos (`yt_demand.py --comments`) and in `feedback/` files from Part C
- breakout videos on similar channels
- the YouTube Studio Trends tab (through Chrome): top searches and content gaps on the default page
- Reddit, read-only through Chrome or web search: questions and well-upvoted posts in r/AskHistorians, r/MapPorn and r/geography from the last 12 months. Record the post link, date and upvotes in `reddit.md`.
- Wikipedia articles and lists such as "List of phantom islands", "Phantom settlement" and "Fictitious entry"; open each to confirm it exists
- anniversaries in the next 90 days, checked on Wikidata or Wikipedia

Leave out topics the channel already covered. Do not use the Studio Inspiration tab: YouTube is retiring it from August 2026, and its AI ideas may be inaccurate by YouTube's own warning.

Write the search phrases one per line to `candidates_terms.txt` and the article titles to `candidates_articles.txt`.

### A2. YouTube results → `yt/`

```
python3 .claude/skills/topic-research/scripts/yt_demand.py \
  --terms-file candidates_terms.txt --regions US GB --comments 3 --out yt/
```

The script needs `YT_API_KEY` in the environment or in `.env`.

**Quota.** `search.list` has its own daily bucket of 100 calls, and each term × region pair is one call. Twelve terms in US and GB is 24 calls. Everything else costs 1 unit each from the shared 10,000. The script refuses to start if the plan needs more than `--max-search-calls` (default 60). Add `CA AU` only for the final shortlist, and keep them only if the summary shows their results differ from the US ones.

**What `regionCode` means.** It restricts results to videos that can be viewed in that country. It does not mean the viewers came from that country. The summary prints how much the US and GB top 10 overlap; high overlap means the region filter changed little.

**Read from `yt/summary.md`:**

- **Median views per day of the top 10:** lifetime views divided by age, so it favours evergreen videos.
- **Fresh views:** total views of results uploaded in the last 12 months. This is the best free sign of current demand.
- **Uploaded in the last 12 months:** how crowded the topic is right now.
- **Breakouts:** videos with at least 3× their channel's median views, from channels under 100k subscribers. They show demand that a small channel can win. Only the channels that rank most often get a median, so this can be undercounted.
- **`yt/requests.md`:** comments asking for related topics.

### A3. Studio Trends and Google Trends

The desktop route uses the Claude in Chrome tools (`mcp__claude-in-chrome__*`), which work in the owner's own Chrome, already signed in to YouTube and Google. Without them, use the phone routes below.

**YouTube Studio Trends tab** → `studio_trends/`

Phone route (no Chrome tools):

1. Look for screenshots the owner attached to the `/topic-research` message. Copy them to `studio_trends/owner_<n>.png`.
2. Read each one and write `studio_trends/summary.md`: the top searches, the content gaps, and any "Audience interest" levels shown, exactly as they appear. Anything not visible is written as "not shown". Never guess text that is cut off or blurred.
3. Use the top searches and content gaps as candidate ideas in A1. Per-candidate "Audience interest" is only known for phrases the owner searched in the screenshots; for the rest write `NOT COLLECTED (phone route)`.
4. If nothing is attached, mark the Studio signal `NOT COLLECTED (no screenshots)` and say in the A8 report which screenshots to attach next time.

Desktop route (Chrome tools present):

1. Open `https://studio.youtube.com`, go to Analytics, and open the Trends tab. The Studio layout is being updated during 2026, so find the tab by reading the page rather than relying on a fixed position.
2. For each candidate's main phrase, use the tab's search box. Read the page text and record:
   - the "Audience interest" level
   - the top entries under "Searched on YouTube"
   - whether a content gap is shown
3. Save a screenshot as `studio_trends/<term>.png`.
4. Write `studio_trends/summary.md` with one row per candidate. Anything not shown on the page is written as "not shown".
5. Only read. Never press Save, Create, Upload or any setting.

**Google Trends** → `trends/`

Choose one **anchor term** for every batch, preferably a previous episode's subject (for example `poyais`), and write it in `run_log.md`. Each batch holds the anchor plus up to 4 candidates.

Phone route (no Chrome tools, `SERPAPI_KEY` set): SerpApi's free plan fetches the same Google Trends data, YouTube Search property included. It allows 250 searches a month and 50 an hour; one call below is one search. A normal run uses about 10 (3 batches × US and GB, plus up to 3 region calls for finalists in A6).

```
python3 .claude/skills/topic-research/scripts/trends_serpapi.py timeline \
  --terms "<term2>,<term3>,<term4>,<term5>" --anchor "<anchor>" --geo US --out trends/US_youtube_5y_a.csv
```

Repeat with `--geo GB`, then the next batches as `_b`, `_c`. For a finalist's country ranking use `trends_serpapi.py region --term "<term>" --out trends/region_<term>.csv`. If the script prints `NOT COLLECTED`, record its reason for that batch and carry on. Then run `trends_csv.py` as in step 6 below; it reads these files the same way as manual downloads.

Desktop route (Chrome tools present):

1. Use the anchor term chosen above.
2. Open, for each batch:

   `https://trends.google.com/trends/explore?date=today%205-y&geo=US&gprop=youtube&hl=en-US&q=<anchor>,<term2>,<term3>,<term4>,<term5>`

   Spaces in terms become `%20`. Repeat with `geo=GB`.
3. Use the download control of the "Interest over time" chart. Then move the file:

   ```
   python3 .claude/skills/topic-research/scripts/collect_download.py --dest trends/US_youtube_5y_a.csv
   ```

   Name the files `US_…_a`, `GB_…_a`, then `_b`, `_c` and so on for the next batches.
4. If no CSV can be downloaded (layout change, error page), mark that batch `NOT COLLECTED`. Never copy numbers off the chart by eye.
5. Wait about 10 seconds between batches. If Google shows "too many requests", wait 2 minutes and try once more, then mark the batch `NOT COLLECTED`.
6. Then run:

   ```
   python3 .claude/skills/topic-research/scripts/trends_csv.py trends/ --anchor <anchor> --out trends/summary.md
   ```

The "x anchor" column puts candidates from different batches of the same country on one scale. Compare US with US and GB with GB only. Values are relative, not counts, and low-volume terms show as 0 with noise.

### A4. Wikipedia interest → `wiki.md`

```
python3 .claude/skills/topic-research/scripts/wiki_pageviews.py \
  --articles-file candidates_articles.txt --months 24 --out wiki.md
```

These are English Wikipedia views from all countries, with redirects resolved first. Label them "global, en.wikipedia". They show lasting interest and say nothing about US or UK in particular. A sudden jump usually means news; check why before treating it as demand.

### A5. First scoring

Score every candidate 0 to 5 on the six parts below. Each score cites its evidence: a figure, the file it came from, and the country or "global".

| Part | Weight | Evidence |
|---|---|---|
| US/UK demand | 30 | Studio Trends audience interest; Google Trends US and GB (x anchor); fresh views and top-10 views/day in US/GB results; comment requests |
| Gap | 20 | Studio content-gap flag; few strong uploads in the last 12 months; breakouts from small channels; angles none of the top videos cover |
| Source strength | 20 | First pass: free T1/T2 sources visible in a quick search. Confirmed in A6 for finalists. |
| Map fit | 15 | The story depends on geography; there is a map to show and change |
| Channel fit | 10 | Fits "places the map got wrong"; not a repeat; Part C data shows similar topics held US/UK viewers |
| Safety | 5 | Advertiser-friendly; no living private people; not an active conflict |

Also record for each candidate:

- `signals_collected`: how many of the five demand signals were collected (Studio Trends, Google Trends, YouTube results, viewer questions from comments or Reddit, Wikipedia)
- `signals_disagree`: true when the signals point in different directions
- `recent_uploads_12m`: from `yt/summary.md`

Missing evidence scores 0. The 3 highest totals become finalists.

### A6. Finalist deep check → `finalists/<topic>.md`

For each of the 3 finalists:

1. **Sources.** Search loc.gov, the Internet Archive, Google Books, HathiTrust and scholarly sources. Answers on r/AskHistorians usually cite books and papers; use them as leads, then open the cited works themselves. Open at least 2 T1 or T2 sources about the topic and record their URLs. Gate `two_t1t2_sources` is true only if both were actually opened and are about this topic.
2. **Opening fact.** Pick the fact the video would open on. Confirm it in 2 independent sources from step 1 or other T1 to T3 sources, quoting the wording. Gate `hook_fact_verified` is true only if both agree.
3. **Maps.** Find at least one map or image the video could use, with its license read on the item's own page (see the table in `SOURCES.md`). Gate `safe_map` is true only for public domain, CC0, CC BY or CC BY-SA.
4. **Angle.** Read the titles and descriptions of the top 5 competing videos and write the angle this channel can take that they do not.
5. **Safety.** Recheck advertiser-friendliness. Set safety below 5 for anything involving living private people, recent deaths or active conflicts.

Update the finalists' scores with what the deep check found. Write `scores.json` (format at the top of `scripts/score.py`), setting `finalist` to true and filling the gates for the 3 finalists.

### A7. Pick → `TOPIC_SCORES.md`

```
python3 .claude/skills/topic-research/scripts/score.py scores.json --out TOPIC_SCORES.md
```

The script, not judgement, picks the winner:

- **Totals:** each weighted total is out of 100.
- **Confidence:**
  - High: 3 or more signals agree.
  - Medium: 2 or more signals.
  - Low: anything less.
- **Gates.** A topic can win only if all of these hold:
  - confidence is not Low
  - safety is 5
  - source strength is at least 3
  - all three A6 gates passed
- **Ties.** When eligible topics are within 5 points, the order is higher US/UK demand, then larger gap, then fewer uploads in the last 12 months.

**Exit code 2** means a score has no evidence. Fix it and run again.

**Exit code 3** means no finalist passed:

1. Write 8 new candidates.
2. Repeat A2 to A7 once.
3. If there is still no winner, report the best candidate as "not recommended yet" with the failed gates.

### A8. Report to the owner

End Part A with a short message in Bengali, in this shape:

> **এই টপিকে আগাবেন স্যার: <topic>**
> স্কোর <total>/100 · আস্থা <confidence>
> কেন: <2–3 lines with the strongest figures, each with its country and source file>
> ঝুঁকি: <one line>
> দ্বিতীয় পছন্দ: <runner-up> (<total>)
> যা সংগ্রহ করা যায়নি: <signals marked NOT COLLECTED with the reason, or "সব সংগ্রহ হয়েছে">
> পরের বার যা লাগবে: <only if something was missing: the key or screenshots that would fill it, in plain Bengali>

Keep everything else in the files (`TOPIC_SCORES.md`, `finalists/`, `run_log.md`).

Then stop. Part B starts only when the owner says to go ahead, or names a different candidate.

## Part B: research the chosen topic

Work in `episodes/EPn/research/`.

1. Copy the empty CSVs from `templates/` into that folder.
2. Copy the chosen topic's rows and evidence from Part A into `demand.md`.
3. Copy the topic's `yt/`, `trends/` and `studio_trends/` files from Part A into the same folder.

### B1. Sources → `sources.csv`

The columns are `id,title,author,publisher,year,url,tier,origin,accessed,notes`.

| Tier | Meaning | Examples |
|---|---|---|
| T1 | Primary | Original documents, government records, contemporary newspapers (Chronicling America, Welsh Newspapers, Trove, Papers Past), original maps, Hansard, The Gazette |
| T2 | Scholarly | Peer-reviewed articles, university-press books, museum or archive catalogue entries |
| T3 | Reputable reference and journalism | Britannica, BBC, Smithsonian Magazine, national broadcasters |
| T4 | Lead only | Wikipedia, blogs, YouTube videos, forums, AI answers |

- T4 sources are used to find T1 to T3 sources and never count as support.
- `origin` names the root source. Two articles that both rely on the same book share one origin and count once.
- Every row needs a URL that was opened in this session, or a full book citation with its page. Fill `accessed` with today's date.
- If a page might change, also save it in the Internet Archive (web.archive.org/save) and put the archive link in `notes`.

### B2. Claims → `claims.csv`

The columns are `id,claim,value,type,source_ids,quote,status,formula,notes`.

- Each fact the script might use gets its own row: one date, one number, one name or one event.
- `type` is one of `date`, `number`, `name`, `place`, `event`, `quote`, `derived`.
- `quote` holds the exact wording from the strongest source, with its page or section.

`status` is one of:

- **VERIFIED:** at least 2 T1 to T3 sources with different origins, at least one of them T1 or T2, and both agree.
- **CONTESTED:** the sources disagree. Record each version and its source in `notes`. The script must say the sources disagree, or leave the claim out.
- **UNVERIFIED:** not enough support yet. It cannot be used in the script.

A figure worked out from other rows (for example "about three in four died", from 180 of 250) gets `type` = `derived`:

- The working goes in `formula`.
- `source_ids` lists the input claim ids instead of source ids.
- It can be VERIFIED only when every input claim is VERIFIED.

Some details need extra care:

- **Numbers.** Keep the source's precision ("about 250" stays "about 250"). Money conversions to today's value name the converter and its base year as a source.
- **Dates.** For Britain and its colonies before 14 September 1752, note Old Style or New Style. Never mix them in one script.
- **Places.** Record the historical name, the modern name and country, and coordinates from Wikidata or GeoNames in `places.csv` (columns `name,modern_name,country,lat,lon,source_id`).
- **Quotes.** Use only verbatim quotes with their location. Never put a paraphrase in quotation marks.
- **What a primary source proves.** A T1 document proves what it says and when it said it, not that it was true. The Poyais brochure is T1 evidence that the brochure promised a harbour, not that there was one. Word such claims as "the brochure claimed …", and check the underlying fact against scholarly or official sources.
- **Circular sourcing.** If a T3 article repeats Wikipedia's wording or cites only Wikipedia, treat it as T4. Wikipedia can also cite journalism that copied Wikipedia, so follow every chain back to its origin.
- **Own words.** Write the script in its own words. Apart from short attributed quotes, never copy sentences from a source.
- **Dialogue and scenes.** Never present invented dialogue or scenes as fact. A dramatised visual needs an on-screen cue such as "illustration" or "reconstruction".

### B3. Assets → `assets.csv`

The columns are `id,what,url,author,license,license_url,checked,credit_line`.

- Allowed licenses: public domain, CC0, CC BY, CC BY-SA. Take the license from the item's own page; on Wikimedia Commons, use the file page's license section.
- NC (non-commercial) licenses, "all rights reserved", and unclear terms are not used without written permission, because the channel is monetized. The David Rumsey collection, for example, is CC BY-NC-SA. Any permission email goes in `notes`.
- Base maps: Natural Earth (public domain), or OpenStreetMap data (ODbL, credit "© OpenStreetMap contributors").

### B4. Script gate

The script writer works only from `claims.csv`. Before the voice-over is made:

1. Run the checker:

   ```
   python3 .claude/skills/topic-research/scripts/check_claims.py episodes/EPn/research \
     --text episodes/EPn/script/narration.md --out episodes/EPn/research/CHECK_CLAIMS.txt
   ```

   It fails when:
   - the ledger breaks the rules above
   - a number or year in the text (digits or words such as "fifty-eight") has no matching VERIFIED or CONTESTED row
   - a claim's sources are T4 only

   Dates count too, so the day in "7 December 1825" needs a row. The word "one" is skipped because it is too common in ordinary sentences; numbers written as digits are always checked.

   The checker matches values, not meaning: "250" passes if any usable claim holds 250, even if the script attaches it to the wrong thing. Names, places and wording are not checked automatically either. The audit in step 2 covers these.

   Fix the cause in the ledger or the script. Never loosen the checker.
2. Run the `fact-auditor` subagent (`.claude/agents/fact-auditor.md`). It works in its own fresh context. Give it only the paths to `claims.csv`, `sources.csv` and the script. Save its output as `AUDIT.md`, and resolve each item by cutting, softening, or adding a properly sourced ledger row. Run it again until it reports `RESULT: PASS`.
3. Run `check_claims.py` again until it exits 0.

### B5. Hand-off

`upload-kit` reads:

- `demand.md` and the `yt/` files for its title and tag work
- `sources.csv` (T1 to T3) for the description's SOURCES
- `assets.csv` for CREDITS
- `claims.csv`, through `check_claims.py`, for the description and pinned comment

Keep the file names and columns stable. If a column has to change, update `upload-kit/SKILL.md` in the same edit.

## Part C: learn from published episodes

Part A runs this first, on its own, for every published episode that is at least 28 days old and has no `episodes/EPn/feedback/` folder yet.

Phone route (no Chrome tools): use screenshots the owner attached of that episode's Studio Analytics (geography, traffic source, YouTube search terms). Copy them to `feedback/`, read the figures exactly as shown, and write `feedback/summary.md` as in step 2. If none are attached, note it in `run_log.md`, continue, and list in the A8 report which episode and which three screens to attach next time.

Desktop route:

1. In Chrome, open YouTube Studio → Analytics → Advanced mode for that episode. Export each view with "Export current view" (CSV, at most 500 rows) and move the file with `collect_download.py`:
   - Geography breakdown → `feedback/geography.csv`
   - Traffic source → `feedback/traffic.csv`
   - YouTube search terms (click "YouTube search" in the traffic source report) → `feedback/search_terms.csv`

   Only read and export. Change nothing in Studio.
2. Write `feedback/summary.md`, covering:
   - the share of views and watch time from US, GB, CA, AU, IE and NZ
   - the share from browse, suggested and search
   - the search terms that brought viewers
   - comments asking for topics (`yt_demand.py --comments` on the channel's own videos)
3. Part A uses these files for the Channel fit score and as a source of candidate ideas. Real viewer data from the channel outranks every outside signal.
