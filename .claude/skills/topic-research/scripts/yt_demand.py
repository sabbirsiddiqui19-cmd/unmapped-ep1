#!/usr/bin/env python3
"""YouTube demand snapshot for candidate topics, per region, using the free Data API v3.

Writes OUT/raw.json, OUT/summary.md and (with --comments) OUT/requests.md.
Quota: search.list uses its own 100-calls/day bucket (1 per call); everything else
costs 1 unit from the shared 10,000/day. See ../SOURCES.md.
"""
import argparse
import datetime as dt
import json
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://www.googleapis.com/youtube/v3/"
REQUEST_RE = re.compile(
    r"\b(do a video|make a video|video (?:on|about)|you should (?:cover|do)|"
    r"(?:next|please) (?:do|cover)|what about|cover the|can you do)\b",
    re.I,
)


class Client:
    def __init__(self, key, fixture=None, max_search=60):
        self.key = key
        self.fixture = Path(fixture) if fixture else None
        self.max_search = max_search
        self.search_calls = 0
        self.units = 0

    def get(self, endpoint, params):
        if endpoint == "search":
            if self.search_calls >= self.max_search:
                raise RuntimeError(f"search budget of {self.max_search} calls reached")
            self.search_calls += 1
        else:
            self.units += 1
        if self.fixture:
            return self._fixture(endpoint, params)
        params = dict(params, key=self.key)
        url = API + endpoint + "?" + urllib.parse.urlencode(params)
        for attempt in range(3):
            try:
                with urllib.request.urlopen(url, timeout=30) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", "replace")
                if e.code == 403 and "commentsDisabled" in body:
                    return {"items": [], "disabled": True}
                if e.code == 403 and "quotaExceeded" in body:
                    raise RuntimeError("quota exceeded; try again after midnight Pacific time") from e
                if e.code >= 500 and attempt < 2:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise RuntimeError(f"{endpoint} HTTP {e.code}: {body[:300]}") from e
        return {}

    def _fixture(self, endpoint, params):
        data = json.loads((self.fixture / f"{endpoint}.json").read_text())
        if endpoint == "search":
            return data.get(f"{params['q']}|{params['regionCode']}", {"items": []})
        if endpoint in ("videos", "channels"):
            ids = set(params["id"].split(","))
            return {"items": [i for i in data["items"] if i["id"] in ids]}
        if endpoint == "playlistItems":
            return data.get(params["playlistId"], {"items": []})
        if endpoint == "commentThreads":
            return data.get(params["videoId"], {"items": []})
        return {}


def iso_duration_seconds(s):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    if not m:
        return 0
    d, h, mi, se = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + se


def chunks(seq, n=50):
    seq = list(seq)
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def fetch_videos(client, ids):
    out = {}
    for group in chunks(ids):
        r = client.get("videos", {"part": "snippet,statistics,contentDetails", "id": ",".join(group), "maxResults": 50})
        for v in r.get("items", []):
            out[v["id"]] = v
    return out


def fetch_channels(client, ids):
    out = {}
    for group in chunks(ids):
        r = client.get("channels", {"part": "snippet,statistics,contentDetails", "id": ",".join(group), "maxResults": 50})
        for c in r.get("items", []):
            out[c["id"]] = c
    return out


def channel_median_views(client, channel, min_seconds):
    uploads = channel.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
    if not uploads:
        return None
    r = client.get("playlistItems", {"part": "contentDetails", "playlistId": uploads, "maxResults": 50})
    ids = [i["contentDetails"]["videoId"] for i in r.get("items", [])]
    vids = fetch_videos(client, ids)
    return {
        vid: int(v["statistics"].get("viewCount", 0))
        for vid, v in vids.items()
        if iso_duration_seconds(v["contentDetails"].get("duration")) >= min_seconds
    }


def median_excluding(uploads, vid):
    """Channel median over recent long uploads, leaving out the video being judged."""
    if not uploads:
        return None
    views = [n for v, n in uploads.items() if v != vid]
    return statistics.median(views) if len(views) >= 5 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", nargs="*", default=[])
    ap.add_argument("--terms-file", type=Path)
    ap.add_argument("--regions", nargs="+", default=["US", "GB"])
    ap.add_argument("--results", type=int, default=25)
    ap.add_argument("--min-seconds", type=int, default=180, help="ignore Shorts and clips below this length")
    ap.add_argument("--outlier-channels", type=int, default=15, help="channels to fetch medians for")
    ap.add_argument("--comments", type=int, default=0, help="top N videos per term to mine for requests")
    ap.add_argument("--max-search-calls", type=int, default=60)
    ap.add_argument("--today", help="YYYY-MM-DD, for reproducible tests")
    ap.add_argument("--fixture", type=Path, help="offline test data folder")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    terms = list(args.terms)
    if args.terms_file:
        terms += [t.strip() for t in args.terms_file.read_text().splitlines() if t.strip() and not t.startswith("#")]
    if not terms:
        sys.exit("no terms given")
    needed = len(terms) * len(args.regions)
    if needed > args.max_search_calls:
        sys.exit(f"{needed} search calls needed, budget is {args.max_search_calls}; cut terms or regions")

    key = os.environ.get("YT_API_KEY")
    if not key and Path(".env").exists():
        for line in Path(".env").read_text().splitlines():
            if line.startswith("YT_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"')
    if not key and not args.fixture:
        sys.exit("YT_API_KEY not set (environment or .env)")

    client = Client(key, args.fixture, args.max_search_calls)
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    args.out.mkdir(parents=True, exist_ok=True)

    hits = {}
    for term in terms:
        for region in args.regions:
            r = client.get("search", {
                "part": "snippet", "type": "video", "q": term, "regionCode": region,
                "relevanceLanguage": "en", "maxResults": args.results, "order": "relevance",
            })
            hits[(term, region)] = [i["id"]["videoId"] for i in r.get("items", []) if i.get("id", {}).get("videoId")]

    all_ids = {v for ids in hits.values() for v in ids}
    videos = fetch_videos(client, all_ids)
    channels = fetch_channels(client, {v["snippet"]["channelId"] for v in videos.values()})

    def row(vid):
        v = videos[vid]
        published = dt.date.fromisoformat(v["snippet"]["publishedAt"][:10])
        age = max((today - published).days, 1)
        views = int(v["statistics"].get("viewCount", 0))
        ch = channels.get(v["snippet"]["channelId"], {})
        subs = ch.get("statistics", {}).get("subscriberCount")
        hidden = ch.get("statistics", {}).get("hiddenSubscriberCount", False)
        return {
            "id": vid, "title": v["snippet"]["title"], "channel": v["snippet"]["channelTitle"],
            "channel_id": v["snippet"]["channelId"], "published": str(published), "age_days": age,
            "views": views, "views_per_day": round(views / age, 1),
            "seconds": iso_duration_seconds(v["contentDetails"].get("duration")),
            "subs": None if hidden or subs is None else int(subs),
        }

    # channels that most often rank, so the median lookups go where they matter
    rank_count = {}
    for ids in hits.values():
        for vid in ids:
            if vid in videos:
                c = videos[vid]["snippet"]["channelId"]
                rank_count[c] = rank_count.get(c, 0) + 1
    medians = {}
    for cid in sorted(rank_count, key=rank_count.get, reverse=True)[: args.outlier_channels]:
        if cid in channels:
            medians[cid] = channel_median_views(client, channels[cid], args.min_seconds)

    report = {"generated": str(today), "regions": args.regions, "terms": {}}
    lines = [
        f"# YouTube demand snapshot ({today})",
        "",
        "- regionCode limits results to videos viewable in that country; it does not show viewer location.",
        f"- Videos shorter than {args.min_seconds} s are left out.",
        "- Views/day is lifetime views divided by age, so it favours steady evergreen videos over recent spikes.",
        "- Fresh views = total views of results uploaded in the last 12 months (recent demand).",
        f"- Breakout = at least 3x the channel's median views on its last 50 long uploads (the video itself "
        f"left out), from a channel under 100k subscribers. Only the {args.outlier_channels} channels that rank "
        "most often get a median; others show n/a, so breakouts can be undercounted.",
        "- Subscriber counts from the API are rounded by YouTube.",
        "",
        "| Term | Region | Long videos | Median views/day (top 10) | Uploaded last 12 mo | Fresh views | Breakouts |",
        "|---|---|---|---|---|---|---|",
    ]
    detail = []
    for term in terms:
        report["terms"][term] = {}
        for region in args.regions:
            rows = [row(v) for v in hits[(term, region)] if v in videos]
            rows = [r for r in rows if r["seconds"] >= args.min_seconds]
            for r in rows:
                med = median_excluding(medians.get(r["channel_id"]), r["id"])
                r["outlier"] = round(r["views"] / med, 1) if med else None
            top = rows[:10]
            vpd = statistics.median([r["views_per_day"] for r in top]) if top else 0
            recent = sum(1 for r in rows if r["age_days"] <= 365)
            fresh = sum(r["views"] for r in rows if r["age_days"] <= 365)
            breakouts = [
                r for r in rows
                if r["outlier"] and r["outlier"] >= 3 and r["subs"] is not None and r["subs"] < 100_000
            ]
            report["terms"][term][region] = {"videos": rows, "median_vpd_top10": vpd,
                                             "recent_12m": recent, "fresh_views": fresh, "breakouts": [b["id"] for b in breakouts]}
            lines.append(f"| {term} | {region} | {len(rows)} | {vpd:,.0f} | {recent} | {fresh:,} | {len(breakouts)} |")
            if region in ("US", "GB"):
                detail.append(f"\n## {term} ({region}), top 5\n")
                if not top:
                    detail.append("- no long videos found")
                for r in top[:5]:
                    out = f"{r['outlier']}x" if r["outlier"] else "n/a"
                    subs = f"{r['subs']:,}" if r["subs"] is not None else "hidden"
                    detail.append(
                        f"- [{r['title']}](https://www.youtube.com/watch?v={r['id']}) · {r['channel']} "
                        f"({subs} subs) · {r['views']:,} views · {r['published']} · "
                        f"{r['views_per_day']:,.0f}/day · outlier {out}"
                    )

    if "US" in args.regions and "GB" in args.regions:
        lines.append("\nOverlap of the top 10 between US and GB results (high overlap = the region filter changed little):")
        for term in terms:
            us = [r["id"] for r in report["terms"][term]["US"]["videos"][:10]]
            gb = {r["id"] for r in report["terms"][term]["GB"]["videos"][:10]}
            share = f"{len(gb.intersection(us)) / len(us):.0%}" if us else "n/a"
            lines.append(f"- {term}: {share}")

    requests = []
    if args.comments:
        lines_req = ["# Topic requests found in comments", ""]
        for term in terms:
            seen = []
            for region in ("US", "GB"):
                for r in report["terms"][term].get(region, {}).get("videos", []):
                    if r["id"] not in seen:
                        seen.append(r["id"])
            for vid in seen[: args.comments]:
                c = client.get("commentThreads", {"part": "snippet", "videoId": vid, "order": "relevance",
                                                  "maxResults": 100, "textFormat": "plainText"})
                for item in c.get("items", []):
                    s = item["snippet"]["topLevelComment"]["snippet"]
                    text = s.get("textDisplay", "").replace("\n", " ")
                    if REQUEST_RE.search(text):
                        requests.append({"term": term, "video": vid, "likes": s.get("likeCount", 0), "text": text[:300]})
        requests.sort(key=lambda x: x["likes"], reverse=True)
        for q in requests:
            lines_req.append(f"- ({q['likes']} likes) [{q['term']}] https://www.youtube.com/watch?v={q['video']} — {q['text']}")
        (args.out / "requests.md").write_text("\n".join(lines_req) + "\n", encoding="utf-8")

    lines += detail
    lines.append(f"\nQuota used: {client.search_calls} search calls (bucket of 100/day), {client.units} units (of 10,000/day).")
    report["quota"] = {"search_calls": client.search_calls, "units": client.units}
    report["requests"] = requests
    (args.out / "raw.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (args.out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
