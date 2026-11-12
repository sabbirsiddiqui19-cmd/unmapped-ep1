#!/usr/bin/env python3
"""Summarise Google Trends CSV downloads (timeline and interest-by-region files).

Timeline values are Google's 0-100 relative index, not search counts; "<1" is read as 0.5.
Compare terms only within one file, or across files of the same place and period through a shared
anchor term (--anchor). Region files with several terms hold each term's percentage share in a country.
"""
import argparse
import csv
import datetime as dt
import io
import re
import statistics
from pathlib import Path

TIME_HEADERS = {"week", "month", "day", "time", "date"}
REGION_HEADERS = {"country", "region", "subregion", "metro", "city"}
FOCUS = ["United States", "United Kingdom", "Canada", "Australia", "Ireland", "New Zealand"]


def parse_value(s):
    s = s.strip()
    if not s:
        return None
    if s == "<1":
        return 0.5
    s = s.rstrip("%")
    try:
        return float(s)
    except ValueError:
        return None


def parse_date(s):
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y-%m-%dT%H", "%m/%d/%Y", "%b %d, %Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
    return dt.date.fromisoformat(m.group(1)) if m else None


def load(path):
    text = path.read_text(encoding="utf-8-sig")
    rows = list(csv.reader(io.StringIO(text)))
    for i, r in enumerate(rows):
        if len(r) >= 2 and r[0].strip().lower() in TIME_HEADERS | REGION_HEADERS:
            kind = "time" if r[0].strip().lower() in TIME_HEADERS else "region"
            terms = [re.sub(r":\s*\(.*\)$", "", h).strip() for h in r[1:]]
            return kind, terms, [x for x in rows[i + 1:] if x and any(c.strip() for c in x)]
    return None, [], []


def summarise_time(terms, rows, anchor=None):
    dated = [(parse_date(r[0]), r[1:]) for r in rows]
    dated = [(d, v) for d, v in dated if d]
    if not dated:
        return ["  (no dated rows found)"]
    last = max(d for d, _ in dated)
    anchor_recent = None
    if anchor:
        if anchor.lower() in [t.lower() for t in terms]:
            k = [t.lower() for t in terms].index(anchor.lower())
            vals = [parse_value(v[k]) for d, v in dated if (last - d).days < 365 and k < len(v)]
            vals = [x for x in vals if x is not None]
            anchor_recent = statistics.mean(vals) if vals else None
        else:
            out_missing = f"Anchor term '{anchor}' is not in this file, so it cannot be compared with other files."
    head = "| Term | Avg last 12 mo | Avg prior 12 mo | Peak | Peak date |" + (" x anchor (last 12 mo) |" if anchor_recent else "")
    out = [head, "|---|---|---|---|---|" + ("---|" if anchor_recent else "")]
    for j, term in enumerate(terms):
        series = [(d, parse_value(v[j]) if j < len(v) else None) for d, v in dated]
        series = [(d, x) for d, x in series if x is not None]
        recent = [x for d, x in series if (last - d).days < 365]
        prior = [x for d, x in series if 365 <= (last - d).days < 730]
        peak_d, peak = max(series, key=lambda t: t[1]) if series else (None, None)
        fmt = lambda xs: f"{statistics.mean(xs):.1f}" if xs else "n/a"
        row = f"| {term} | {fmt(recent)} | {fmt(prior)} | {peak if peak is not None else 'n/a'} | {peak_d or 'n/a'} |"
        if anchor_recent:
            row += f" {statistics.mean(recent) / anchor_recent:.2f} |" if recent else " n/a |"
        out.append(row)
    out.append(f"\nLast data point: {last}.")
    if anchor and not anchor_recent:
        out.append(out_missing if anchor.lower() not in [t.lower() for t in terms]
                   else f"Anchor term '{anchor}' has no data in the last 12 months here.")
    return out


def summarise_region(terms, rows):
    share = any("%" in c for r in rows for c in r[1:])
    out = []
    if share:
        out.append("Values are each term's percentage share of the compared searches in that country, "
                   "not a 0-100 index. Download one term at a time to rank countries for a single topic.\n")
    out += ["| Term | " + " | ".join(FOCUS) + " |", "|---|" + "---|" * len(FOCUS)]
    for j, term in enumerate(terms):
        vals = {r[0].strip(): parse_value(r[j + 1]) if j + 1 < len(r) else None for r in rows}
        ranked = sorted((v, k) for k, v in vals.items() if v is not None)[::-1]
        rank = {k: i + 1 for i, (v, k) in enumerate(ranked)}
        cells = []
        for c in FOCUS:
            v = vals.get(c)
            if v is None:
                cells.append("not listed")
            elif share:
                cells.append(f"{v:g}%")
            else:
                cells.append(f"{v:g} (#{rank[c]} of {len(ranked)})")
        out.append(f"| {term} | " + " | ".join(cells) + " |")
    out.append("\n\"not listed\" means Trends gave no value for that country (often too little volume).")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=Path)
    ap.add_argument("--anchor", help="term included in every batch, used to compare files of the same place")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    lines = ["# Google Trends summary", "",
             "Data source: Google Trends (https://www.google.com/trends). Timeline values are a 0-100 relative "
             "index within each file, not search counts. Each section says how to read its numbers.", ""]
    files = sorted(args.folder.glob("*.csv"))
    if not files:
        lines.append("No CSV files found: Trends not collected.")
    for f in files:
        kind, terms, rows = load(f)
        lines.append(f"## {f.name}")
        if not kind:
            lines.append("Could not find a header row; open the file and check the format.\n")
            continue
        lines += summarise_time(terms, rows, args.anchor) if kind == "time" else summarise_region(terms, rows)
        lines.append("")
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
