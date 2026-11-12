#!/usr/bin/env python3
"""Check a research folder's claim ledger, and check text files against it.

  check_claims.py RESEARCH_DIR [--text FILE ...] [--ignore N ...] [--out REPORT]

Ledger rules (sources.csv + claims.csv) are described in ../SKILL.md, part B.
Every number or year in each --text file must appear in a usable claim
(VERIFIED or CONTESTED, including derived rows). Exit code 1 on any FAIL.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

SOURCE_COLS = ["id", "title", "author", "publisher", "year", "url", "tier", "origin", "accessed", "notes"]
CLAIM_COLS = ["id", "claim", "value", "type", "source_ids", "quote", "status", "formula", "notes"]
TYPES = {"date", "number", "name", "place", "event", "quote", "derived"}
STATUSES = {"VERIFIED", "CONTESTED", "UNVERIFIED"}

UNITS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen".split())}
TENS = {w: 10 * (i + 2) for i, w in enumerate("twenty thirty forty fifty sixty seventy eighty ninety".split())}
SCALES = {"hundred": 100, "thousand": 1_000, "million": 1_000_000, "billion": 1_000_000_000}
NUM_WORDS = set(UNITS) | set(TENS) | set(SCALES)
DIGITS = re.compile(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)(?:\s*(thousand|million|billion)\b)?", re.I)
TIMESTAMP = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?(?:[,.]\d{1,3})?\b")
SKIP_BLOCKS = {"CHAPTERS", "CREDITS"}

results = []
broken_claims = set()


def add(level, msg):
    results.append((level, msg))


def claim_fail(cid, msg):
    broken_claims.add(cid)
    add("FAIL", f"claim {cid}: {msg}")


def words_to_numbers(text):
    """Yield numbers written in words, e.g. 'three hundred and fifty-five' -> 355."""
    tokens = re.findall(r"[a-z]+", text.lower().replace("-", " "))
    run, i = [], 0
    while i <= len(tokens):
        tok = tokens[i] if i < len(tokens) else None
        if tok in NUM_WORDS or (tok == "and" and run and i + 1 < len(tokens) and tokens[i + 1] in NUM_WORDS):
            if tok != "and":
                run.append(tok)
        else:
            if run and run != ["one"]:
                total = current = 0
                for w in run:
                    if w in UNITS:
                        current += UNITS[w]
                    elif w in TENS:
                        current += TENS[w]
                    elif w == "hundred":
                        current = max(current, 1) * 100
                    else:
                        total += max(current, 1) * SCALES[w]
                        current = 0
                yield float(total + current), " ".join(run)
            run = []
        i += 1


def numbers_in(text):
    text = TIMESTAMP.sub(" ", text)
    found = []
    for m in DIGITS.finditer(text):
        raw = m.group(1).replace(",", "")
        try:
            value = float(raw)
        except ValueError:
            continue
        if m.group(2):
            value *= SCALES[m.group(2).lower()]
        found.append((round(value, 6), m.group(0).strip()))
    # digits already consumed "1.3 million"; drop them so "million" is not read again as a word
    found += [(round(v, 6), w) for v, w in words_to_numbers(DIGITS.sub(" ", text))]
    return found


def read_csv(path, cols):
    if not path.exists():
        add("FAIL", f"{path.name} missing")
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in cols if c not in (reader.fieldnames or [])]
        if missing:
            add("FAIL", f"{path.name}: missing columns {missing}")
            return []
        return [{k: (v or "").strip() for k, v in row.items()} for row in reader]


def tier_of(s):
    m = re.fullmatch(r"T?([1-4])", s["tier"], re.I)
    return int(m.group(1)) if m else None


def check_sources(sources):
    by_id = {}
    for s in sources:
        sid = s["id"]
        if not sid:
            add("FAIL", "sources.csv: row without id")
            continue
        if sid in by_id:
            add("FAIL", f"sources.csv: duplicate id {sid}")
        by_id[sid] = s
        if tier_of(s) is None:
            add("FAIL", f"source {sid}: tier must be T1-T4, got {s['tier']!r}")
        if s["url"]:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", s["accessed"]):
                add("FAIL", f"source {sid}: has a URL but 'accessed' is not YYYY-MM-DD")
        elif not (s["title"] and s["author"] and s["year"]):
            add("FAIL", f"source {sid}: needs a URL, or title + author + year for a printed work")
    return by_id


def check_claims(claims, sources):
    by_id = {}
    for c in claims:
        if c["id"] in by_id:
            add("FAIL", f"claims.csv: duplicate id {c['id']}")
        by_id[c["id"]] = c
    for c in claims:
        cid, status, ctype = c["id"], c["status"], c["type"].lower()
        refs = [x.strip() for x in re.split(r"[;,\s]+", c["source_ids"]) if x.strip()]
        if status not in STATUSES:
            claim_fail(cid, f"status must be one of {sorted(STATUSES)}, got {status!r}")
            continue
        if ctype not in TYPES:
            claim_fail(cid, f"type must be one of {sorted(TYPES)}, got {ctype!r}")
        if ctype == "derived":
            if not c["formula"]:
                claim_fail(cid, "derived claim needs a formula")
            bad = [r for r in refs if r not in by_id]
            if bad or not refs:
                claim_fail(cid, f"derived claim must list input claim ids (unknown: {bad})")
            elif status == "VERIFIED" and any(by_id[r]["status"] != "VERIFIED" for r in refs):
                claim_fail(cid, "marked VERIFIED but an input claim is not VERIFIED")
            continue
        unknown = [r for r in refs if r not in sources]
        if unknown:
            claim_fail(cid, f"unknown source ids {unknown}")
        used = [sources[r] for r in refs if r in sources]
        support = [s for s in used if (tier_of(s) or 4) <= 3]
        if status == "VERIFIED":
            origins = {s["origin"] or s["id"] for s in support}
            if len(origins) < 2:
                claim_fail(cid, f"VERIFIED needs 2 independent T1-T3 sources, has {len(origins)}")
            if not any((tier_of(s) or 4) <= 2 for s in support):
                claim_fail(cid, "VERIFIED needs at least one T1 or T2 source")
            if not c["quote"]:
                claim_fail(cid, "VERIFIED needs the source wording in 'quote'")
        elif status == "CONTESTED":
            if not c["notes"]:
                claim_fail(cid, "CONTESTED needs both versions and their sources in 'notes'")
            if not support:
                claim_fail(cid, "CONTESTED still needs at least one T1-T3 source")
        if used and not support:
            claim_fail(cid, "supported only by T4 sources")
    return by_id


def text_lines(path):
    """Yield (line_no, text) skipping SRT timing lines, chapter/credit blocks and markdown headings."""
    skipping = False
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        s = line.strip()
        if s.upper() in SKIP_BLOCKS:
            skipping = True
            continue
        if skipping:
            if not s:
                skipping = False
            continue
        if path.suffix.lower() == ".srt" and (s.isdigit() or "-->" in s):
            continue
        if re.match(r"^#{1,6}\s", s):
            continue
        yield n, line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("research", type=Path)
    ap.add_argument("--text", type=Path, nargs="*", default=[])
    ap.add_argument("--ignore", nargs="*", default=[], help="numbers allowed without a claim, e.g. 4 for '4K'")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    sources = check_sources(read_csv(args.research / "sources.csv", SOURCE_COLS))
    claims = check_claims(read_csv(args.research / "claims.csv", CLAIM_COLS), sources)
    counts = {}
    for c in claims.values():
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    add("OK", f"ledger: {len(sources)} sources, {len(claims)} claims {counts}")

    usable, unverified = {}, {}
    for c in claims.values():
        ok = c["status"] in ("VERIFIED", "CONTESTED") and c["id"] not in broken_claims
        target = usable if ok else unverified
        for value, _ in numbers_in(f"{c['claim']} {c['value']}"):
            target.setdefault(value, set()).add(c["id"])
    ignore = {round(float(x), 6) for x in args.ignore}

    for path in args.text:
        if not path.exists():
            add("FAIL", f"text file not found: {path}")
            continue
        missing = 0
        for n, line in text_lines(path):
            for value, raw in numbers_in(line):
                if value in usable or value in ignore:
                    continue
                missing += 1
                if value in unverified:
                    add("FAIL", f"{path.name}:{n}: '{raw}' only matches UNVERIFIED or invalid claim(s) {sorted(unverified[value])}")
                else:
                    add("FAIL", f"{path.name}:{n}: '{raw}' has no claim in the ledger — {line.strip()[:120]}")
        if not missing:
            add("OK", f"{path.name}: every number matches a usable claim")

    order = {"FAIL": 0, "WARN": 1, "OK": 2}
    lines = [f"[{lvl}] {msg}" for lvl, msg in sorted(results, key=lambda r: order[r[0]])]
    fails = sum(1 for r in results if r[0] == "FAIL")
    lines.append(f"\n{fails} FAIL")
    report = "\n".join(lines)
    print(report)
    if args.out:
        args.out.write_text(report + "\n", encoding="utf-8")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
