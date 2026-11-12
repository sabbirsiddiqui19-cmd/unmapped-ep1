# Free sources for topic research

Checked: 2026-11-12. Re-check the pages marked "limit" before relying on a number once this date is more than 3 months old. Anything marked "not checked" must be checked on the provider's own page before first use, and this file updated.

## Demand data

### YouTube Data API v3 (free key from Google Cloud Console)

- **Search quota:** `search.list` has its own bucket of 100 calls per day, and each call costs 1. This split came in with the granular quota system announced on 2026-06-01.
- **Other methods:** `videos.list`, `channels.list`, `playlistItems.list` and `commentThreads.list` each cost 1 unit from a shared 10,000 units per day.
- **`regionCode`:** restricts search results to videos that can be viewed in that region. It says nothing about where viewers are.
- **Trending chart:** since 2025-07-21 the `mostPopular` chart returns the Trending Music, Movies and Gaming charts. It is not useful for documentary demand.
- **Source:** https://developers.google.com/youtube/v3/determine_quota_cost (limit page, last updated 2026-11-10) and https://developers.google.com/youtube/data/revision_history

### YouTube Studio (manual, free, the channel's own account)

- **Trends tab:** Analytics → Trends. It shows:
  - "Audience interest" from very low to very high, based on videos watched more than 1,000 times per week over the last 28 days
  - top searches over the last 28 days
  - content gaps, meaning searches where viewers cannot find enough quality results

  The help page notes that some insights are limited to certain countries, languages and devices, and it describes no region selector. Source: https://support.google.com/youtube/answer/11962757
- **Inspiration tab:** being retired from August 2026, and its AI ideas "may be inaccurate". Not used. Source: https://support.google.com/youtube/answer/15575509
- **Advanced mode export:** Analytics → Advanced mode → "Export current view", limited to 500 rows. It can break results down by geography and traffic source, and clicking "YouTube search" in the traffic source report shows the search terms that brought viewers. Source: https://support.google.com/youtube/answer/9717005

### Google Trends (manual)

- **Access:** there is no free official API. The official Trends API is a limited-access alpha (first testers were being onboarded from September 2025). The unofficial `pytrends` library scrapes internal endpoints that Google rate-limits, and is reported to no longer work reliably. Not used.
- **Download:** Explore has a Download button that gives a CSV.
- **Comparisons:** the redesigned page compares up to 8 groups of terms; the Classic page compares 5. Each term can have its own location.
- **Search types:** web, YouTube, image, News, Shopping.
- **Interest by region with several terms:** shows each term's percentage share in a region, not a 0-100 index. Download one term at a time to rank countries. Source: https://newsinitiative.withgoogle.com/resources/lessons/google-trends-understanding-the-data/
- **Explore URL:** `trends.google.com/trends/explore?date=today%205-y&geo=US&gprop=youtube&q=a,b`. These URL parameters are the ones the Explore page itself uses. They are not a documented API and could change; if the page ignores them, set the filters by hand in the page.
- **Comparing batches:** the help pages give no cross-batch method. The skill repeats one anchor term in every batch and divides by it. This is a working method, not an official Google feature.
- **What the values mean:** they run from 0 to 100, scaled by each topic's share of all searches in that place and period. They are not counts. Low-volume terms show as 0, and noise is added for privacy.
- **Citation:** reused data must be credited "Data source: Google Trends (https://www.google.com/trends)".
- **Sources:** https://support.google.com/trends/answer/4365533, https://support.google.com/trends/answer/4359550, https://support.google.com/trends/answer/4365538, https://www.seroundtable.com/google-trends-api-applications-approvals-39978.html

### Wikimedia pageviews

- **Per-article endpoint:** `https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{Title}/monthly/{YYYYMMDD}/{YYYYMMDD}`.
- **Scope:** counts are global, with no country split per article. Redirects are counted separately, so resolve the title first with the MediaWiki API (`action=query&redirects=1`).
- **Country data:** the published country data is per project and bucketed into ranges, so it cannot be used for a single topic.
- **User-Agent:** send a descriptive User-Agent with contact details.
- **Sources:** https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/concepts/country-data.html and https://docs.nexla.com/user-guides/connectors/wikipedia_pageviews_api

## Fact sources

### United States

**Library of Congress loc.gov JSON API.** Add `fo=json` to any collection URL.

- Chronicling America's own API ran 2007–2025. The collection is now reached only through the loc.gov API, for example:

  `https://www.loc.gov/collections/chronicling-america/?dl=page&start_date=1822-01-01&end_date=1823-12-31&qs=poyais&fo=json`

  Full OCR text sits in the `full_text` field of a page resource.
- **Limit:** 20 requests per minute on the JSON API. Going over blocks you for 1 hour, and the limits can drop under load. Sleep at least 3 seconds between calls.
- **Map rights:** Geography and Map Division digitized collections are "free to use and reuse" unless the item carries a Rights Advisory. Credit them as "Library of Congress, Geography and Map Division".
- **Sources:**
  - https://www.loc.gov/apis/additional-apis/chronicling-america-api/
  - https://libraryofcongress.github.io/data-exploration/loc.gov%20JSON%20API/Chronicling_America/README.html
  - https://www.loc.gov/apis/json-and-yaml/working-within-limits/
  - https://www.loc.gov/collections/civil-war-maps/about-this-collection/rights-and-access/

**US National Archives catalog.** Not checked.

### United Kingdom

All three are free to search on the web. Their API terms are not checked.

- Hansard (UK Parliament debates)
- The Gazette (official public record)
- Welsh Newspapers (National Library of Wales)

### Secondary-audience countries

Not checked. Read each terms page before first use.

- Trove (Australia). Its API needs a key, and the terms page could not be read on the check date.
- Papers Past / DigitalNZ (New Zealand).
- Canadiana (Canada).

### General

**Internet Archive.**

- Search: `https://archive.org/advancedsearch.php?q=QUERY&output=json&rows=N&page=P` (paging stops at 10,000 results).
- Large pulls: `https://archive.org/services/search/v1/scrape?fields=title,identifier,date&q=QUERY`
- Old books, often with full text.
- Save a page so it can still be cited later: `https://web.archive.org/save/<url>`.
- Source: https://doc-tools.readthedocs.io/en/ia-test-gsod/item-search-apis.html

**Other general sources:**

- **Wikidata:** dates, coordinates and identifiers. Each value must be cross-checked against its referenced source; a Wikidata value alone is T4.
- **Wikipedia:** a lead only (T4). Follow its footnotes to the T1 to T3 sources, then open and cite those.
- **HathiTrust and Google Books:** full view of public-domain books. Cite the edition and page.

## Map and image licenses

| Source | License | Use on a monetized channel |
|---|---|---|
| Natural Earth | Public domain ("All versions … are in the public domain") | Yes |
| OpenStreetMap data | ODbL | Yes, with credit "© OpenStreetMap contributors" |
| Library of Congress, Geography and Map Division | Free to use unless a Rights Advisory says otherwise | Yes; check each item's Rights Advisory |
| Wikimedia Commons | Varies per file | Only PD, CC0, CC BY or CC BY-SA; read each file page |
| David Rumsey Map Collection | CC BY-NC-SA 3.0, "not for commercial use"; other uses by request to carto@davidrumsey.com | No, unless written permission is saved in `assets.csv` |
| National Library of Scotland maps | The permissions page gives no blanket image license; Ordnance Survey sheets still in copyright need a royalty | Check each item; unclear means do not use |

Sources:

- https://www.naturalearthdata.com/about/
- https://davidrumsey.com/about
- https://nls.uk/collections/maps/services/permission
