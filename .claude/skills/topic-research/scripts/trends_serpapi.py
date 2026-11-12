#!/usr/bin/env python3
"""Fetch Google Trends data through SerpApi's free plan and save it as Trends-style CSV.

Used when Claude in Chrome is not available (phone or cloud sessions). The CSV it writes has the
same layout as a manual Trends download, so trends_csv.py reads both.

  trends_serpapi.py timeline --terms "phantom islands,poyais" --anchor "lost city" --geo US --out trends/US_a.csv
  trends_serpapi.py region --term "phantom islands" --out trends/region_phantom_islands.csv

Key: SERPAPI_KEY from the environment or .env. Free plan: 250 searches a month, 50 an hour
(checked 2026-11-12). Each call below is one search. The raw JSON is saved next to the CSV.
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ENDPOINT = "https://serpapi.com/search.json"
GEO_NAMES = {"US": "United States", "GB": "United Kingdom", "CA": "Canada", "AU": "Australia",
             "IE": "Ireland", "NZ": "New Zealand", "": "Worldwide"}
MAX_TERMS = 5  # Google Trends compares at most 5 terms in one request


def api_key():
    key = os.environ.get("SERPAPI_KEY")
    if not key and Path(".env").exists():
        for line in Path(".env").read_text().splitlines():
            if line.startswith("SERPAPI_KEY="):
                key = line.split("=", 1)[1].strip().strip('"')
    if not key:
        sys.exit("NOT COLLECTED: SERPAPI_KEY not set (environment or .env)")
    return key


def fetch(params, fixture=None):
    if fixture:
        return json.loads(Path(fixture).read_text(encoding="utf-8"))
    params = dict(params, engine="google_trends", api_key=api_key())
    req = urllib.request.Request(ENDPOINT + "?" + urllib.parse.urlencode(params),
                                 headers={"User-Agent": "UnmappedPage-topic-research/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"NOT COLLECTED: SerpApi HTTP {e.code}: {e.read()[:300]!r}")
    except urllib.error.URLError as e:
        sys.exit(f"NOT COLLECTED: cannot reach SerpApi ({e.reason}); check the session's network setting")
    if data.get("error"):
        sys.exit(f"NOT COLLECTED: SerpApi error: {data['error']}")
    return data


def save_raw(out, data):
    data.get("search_parameters", {}).pop("api_key", None)
    out.with_suffix(".json").write_text(json.dumps(data, indent=1), encoding="utf-8")


def timeline(args):
    terms = [t.strip() for t in args.terms.split(",") if t.strip()]
    if args.anchor and args.anchor.lower() not in [t.lower() for t in terms]:
        terms.append(args.anchor)
    if len(terms) > MAX_TERMS:
        sys.exit(f"at most {MAX_TERMS} terms per call, anchor included (got {len(terms)})")
    params = {"q": ",".join(terms), "data_type": "TIMESERIES", "date": args.date}
    if args.geo:
        params["geo"] = args.geo
    if args.gprop:
        params["gprop"] = args.gprop
    data = fetch(params, args.fixture)
    rows = data.get("interest_over_time", {}).get("timeline_data", [])
    if not rows:
        sys.exit("NOT COLLECTED: no timeline_data in the response (terms may have too little volume)")
    place = GEO_NAMES.get(args.geo, args.geo)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([f"Category: All categories (SerpApi, gprop={args.gprop or 'web'}, date={args.date})"])
        w.writerow([])
        w.writerow(["Week"] + [f"{t}: ({place})" for t in terms])
        for r in rows:
            day = dt.datetime.fromtimestamp(int(r["timestamp"]), dt.timezone.utc).date().isoformat()
            vals = {v.get("query", "").lower(): v.get("value", "") for v in r.get("values", [])}
            w.writerow([day] + [vals.get(t.lower(), "") for t in terms])
    save_raw(args.out, data)
    print(f"{len(rows)} points for {len(terms)} terms ({place}) -> {args.out}")


def region(args):
    params = {"q": args.term, "data_type": "GEO_MAP_0", "date": args.date}
    if args.gprop:
        params["gprop"] = args.gprop
    data = fetch(params, args.fixture)
    rows = data.get("interest_by_region", [])
    if not rows:
        sys.exit("NOT COLLECTED: no interest_by_region in the response (term may have too little volume)")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([f"Category: All categories (SerpApi, gprop={args.gprop or 'web'}, date={args.date})"])
        w.writerow([])
        w.writerow(["Country", f"{args.term}: ({args.date})"])
        for r in rows:
            w.writerow([r.get("location", r.get("geo", "")), r.get("value", "")])
    save_raw(args.out, data)
    print(f"{len(rows)} countries for '{args.term}' -> {args.out}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("timeline")
    t.add_argument("--terms", required=True, help="comma-separated, up to 5 including the anchor")
    t.add_argument("--anchor")
    t.add_argument("--geo", default="US", help="US, GB, CA, AU, IE, NZ, or empty for worldwide")
    r = sub.add_parser("region")
    r.add_argument("--term", required=True)
    for p in (t, r):
        p.add_argument("--date", default="today 5-y")
        p.add_argument("--gprop", default="youtube", help="youtube for YouTube Search; empty for web")
        p.add_argument("--out", type=Path, required=True)
        p.add_argument("--fixture", help="read this saved JSON instead of calling the API (tests)")
    args = ap.parse_args()
    timeline(args) if args.cmd == "timeline" else region(args)


if __name__ == "__main__":
    main()
