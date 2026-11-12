#!/usr/bin/env python3
"""Monthly English Wikipedia pageviews for candidate articles (global; no country split).

Resolves redirects first, because pageviews are counted per exact title.
"""
import argparse
import datetime as dt
import json
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = "UnmappedPageResearch/1.0 (topic research script; contact via channel owner)"
WIKI_API = "https://en.wikipedia.org/w/api.php"
PV = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{}/monthly/{}/{}"


def get_json(url, fixture=None, key=None):
    if fixture:
        data = json.loads((fixture / "wiki.json").read_text())
        return data.get(key, {})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {}
        raise


def resolve(titles, fixture):
    mapping = {}
    for i in range(0, len(titles), 50):
        group = titles[i:i + 50]
        q = urllib.parse.urlencode({"action": "query", "format": "json", "redirects": 1,
                                    "titles": "|".join(group), "formatversion": 2})
        data = get_json(f"{WIKI_API}?{q}", fixture, "resolve")
        norm = {n["from"]: n["to"] for n in data.get("query", {}).get("normalized", [])}
        redir = {r["from"]: r["to"] for r in data.get("query", {}).get("redirects", [])}
        missing = {p["title"] for p in data.get("query", {}).get("pages", []) if p.get("missing")}
        for t in group:
            final = redir.get(norm.get(t, t), norm.get(t, t))
            mapping[t] = None if final in missing else final
        if not fixture:
            time.sleep(0.5)
    return mapping


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--articles", nargs="*", default=[])
    ap.add_argument("--articles-file", type=Path)
    ap.add_argument("--months", type=int, default=24)
    ap.add_argument("--today", help="YYYY-MM-DD, for reproducible tests")
    ap.add_argument("--fixture", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    titles = list(args.articles)
    if args.articles_file:
        titles += [t.strip() for t in args.articles_file.read_text().splitlines() if t.strip() and not t.startswith("#")]
    if not titles:
        sys.exit("no articles given")

    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    end = today.replace(day=1) - dt.timedelta(days=1)  # last full month
    y, m = end.year, end.month - args.months + 1
    while m < 1:
        y, m = y - 1, m + 12
    start = dt.date(y, m, 1)

    resolved = resolve(titles, args.fixture)
    lines = [
        f"# English Wikipedia pageviews, {start:%Y-%m} to {end:%Y-%m} (global, user agents only)",
        "",
        "Global figures from all countries; they show lasting interest, not US/UK demand.",
        "",
        "| Asked for | Resolved article | Avg / month | Last 12 mo | Prior 12 mo | Change |",
        "|---|---|---|---|---|---|",
    ]
    for t in titles:
        art = resolved.get(t)
        if not art:
            lines.append(f"| {t} | not found | | | | |")
            continue
        url = PV.format(urllib.parse.quote(art.replace(" ", "_"), safe=""), f"{start:%Y%m%d}", f"{end:%Y%m%d}")
        data = get_json(url, args.fixture, art)
        views = [i["views"] for i in data.get("items", [])]
        if not args.fixture:
            time.sleep(0.5)
        if not views:
            lines.append(f"| {t} | {art} | no data | | | |")
            continue
        last12 = sum(views[-12:])
        if len(views) >= 24:
            prior12 = sum(views[-24:-12])
            prior_txt = f"{prior12:,}"
            change = f"{(last12 - prior12) / prior12:+.0%}" if prior12 else "n/a"
        else:
            prior_txt, change = "n/a", "n/a"
        lines.append(f"| {t} | {art} | {statistics.mean(views):,.0f} | {last12:,} | {prior_txt} | {change} |")
    lines.append(f"\nSource: Wikimedia REST API per-article pageviews, retrieved {today}.")
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
