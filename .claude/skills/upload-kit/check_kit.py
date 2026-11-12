#!/usr/bin/env python3
"""Validate a YouTube upload kit folder against the limits in REFERENCE.md.

Usage:
  check_kit.py KIT_DIR [--video FINAL.mp4] [--previous DIR ...] [--out REPORT.txt]

Exit code 1 when any FAIL is found.
"""
import argparse
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

results = []


def add(level, msg):
    results.append((level, msg))


def read_text(path):
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError:
        add("FAIL", f"{path.name}: not valid UTF-8")
        return None


def ts_to_seconds(ts):
    total = 0
    for part in ts.split(":"):
        total = total * 60 + int(part)
    return total


def fmt(seconds):
    m, s = divmod(seconds, 60)
    return f"{int(m)}:{s:05.2f}"


def probe(video):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size:stream=codec_type,codec_name,width,height,avg_frame_rate",
         "-of", "json", str(video)],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def check_video(video):
    if video is None:
        add("WARN", "no --video given: chapter and caption end times not checked against the real duration")
        return None
    if not video.exists():
        add("FAIL", f"video not found: {video}")
        return None
    info = probe(video)
    duration = float(info["format"]["duration"])
    for s in info.get("streams", []):
        if s["codec_type"] == "video":
            add("OK", f"video: {s['codec_name']} {s.get('width')}x{s.get('height')} @ {s.get('avg_frame_rate')} fps")
        elif s["codec_type"] == "audio":
            add("OK", f"audio: {s['codec_name']}")
    add("OK", f"duration {fmt(duration)} ({duration:.3f} s), size {int(info['format']['size']):,} B")
    if duration < 25:
        add("WARN", "video is shorter than 25 s, so an end screen cannot be added")
    return duration


def check_brackets(name, text):
    if "<" in text or ">" in text:
        add("FAIL", f"{name}: contains < or >, which YouTube does not allow")


def check_title(name, title):
    if not title:
        add("FAIL", f"{name}: empty title")
        return
    n = len(title)
    if n > 100:
        add("FAIL", f"{name}: {n} characters (limit 100): {title!r}")
    elif n > 60:
        add("WARN", f"{name}: {n} characters, may be cut on phones (about 60 shows): {title!r}")
    else:
        add("OK", f"{name}: {n} characters: {title!r}")
    check_brackets(name, title)
    if "#" in title:
        add("WARN", f"{name}: hashtag in title; keep hashtags in the description")
    letters = [c for c in title if c.isalpha()]
    if letters and all(c.isupper() for c in letters):
        add("WARN", f"{name}: whole title is in capitals")


def check_titles(kit):
    title = read_text(kit / "01_TITLE.txt")
    if title is None:
        add("FAIL", "01_TITLE.txt missing")
    else:
        check_title("01_TITLE", title)

    variants_text = read_text(kit / "01_TITLE_VARIANTS.txt")
    if variants_text is None:
        add("FAIL", "01_TITLE_VARIANTS.txt missing (needed for Test & Compare)")
        return title
    variants = [v.strip() for v in variants_text.splitlines() if v.strip()]
    if not 2 <= len(variants) <= 3:
        add("FAIL", f"01_TITLE_VARIANTS: {len(variants)} lines, Test & Compare takes 2 or 3")
    for i, v in enumerate(variants):
        check_title(f"variant {'ABC'[i] if i < 3 else i + 1}", v)
    if len({v.lower() for v in variants}) != len(variants):
        add("FAIL", "01_TITLE_VARIANTS: duplicate titles")
    if title and variants and variants[0] != title:
        add("WARN", "variant A differs from 01_TITLE.txt; A should be the title set at upload")
    for i in range(len(variants)):
        for j in range(i + 1, len(variants)):
            r = difflib.SequenceMatcher(None, variants[i].lower(), variants[j].lower()).ratio()
            if r > 0.8:
                add("WARN", f"variants {'ABC'[i]} and {'ABC'[j]} are {r:.0%} alike; test a different angle")
    return title


TS_LINE = re.compile(r"^\s*((?:\d{1,2}:)?\d{1,2}:\d{2})\s+\S")


def check_chapters(desc, duration):
    lines = desc.splitlines()
    block = []
    for line in lines:
        m = TS_LINE.match(line)
        if m:
            block.append(m.group(1))
        elif block:
            break
    if not block:
        add("FAIL", "description: no chapter timestamps found")
        return
    if ts_to_seconds(block[0]) != 0:
        add("FAIL", f"chapters: first timestamp is {block[0]}, must be 00:00")
    elif block[0] != "00:00":
        add("WARN", f"chapters: first timestamp written as {block[0]}; YouTube Help documents 00:00")
    if len(block) < 3:
        add("FAIL", f"chapters: {len(block)} found, at least 3 needed")
    secs = [ts_to_seconds(t) for t in block]
    bad = False
    for a, b, ta, tb in zip(secs, secs[1:], block, block[1:]):
        if b <= a:
            add("FAIL", f"chapters: {tb} is not after {ta}")
            bad = True
        elif b - a < 10:
            add("FAIL", f"chapters: {ta} to {tb} is {b - a} s, minimum 10 s")
            bad = True
    if duration is not None:
        if secs[-1] >= duration:
            add("FAIL", f"chapters: last timestamp {block[-1]} is past the end of the video ({fmt(duration)})")
            bad = True
        elif duration - secs[-1] < 10:
            add("FAIL", f"chapters: last chapter is {duration - secs[-1]:.1f} s, minimum 10 s")
            bad = True
    if not bad:
        add("OK", f"chapters: {len(block)}, ascending, each at least 10 s")


def prose_part(desc):
    """Opening, summary and question: everything before the CHAPTERS header or first timestamp."""
    out = []
    for line in desc.splitlines():
        if line.strip().upper() in {"CHAPTERS", "SOURCES", "CREDITS"} or TS_LINE.match(line):
            break
        out.append(line)
    return " ".join(out).strip()


def check_description(kit, duration):
    desc = read_text(kit / "02_DESCRIPTION.txt")
    if desc is None:
        add("FAIL", "02_DESCRIPTION.txt missing")
        return None
    size = len(desc.encode("utf-8"))
    add("FAIL" if size > 5000 else "OK", f"description: {size:,} bytes (limit 5,000)")
    check_brackets("description", desc)
    first = desc.splitlines()[0] if desc else ""
    if TS_LINE.match(first) or first.startswith("#"):
        add("WARN", "description starts with a timestamp or hashtag; the first lines should describe the video")
    check_chapters(desc, duration)

    tags = re.findall(r"(?<![\w#])#\w+", desc)
    if len(tags) > 60:
        add("FAIL", f"hashtags: {len(tags)}; more than 60 and YouTube ignores all of them")
    elif len(tags) > 5:
        add("WARN", f"hashtags: {len(tags)}; only up to 3 show by the title, keep 3 to 5")
    elif not tags:
        add("WARN", "hashtags: none; 3 relevant ones at the end are recommended")
    else:
        add("OK", f"hashtags: {len(tags)} ({' '.join(tags)})")

    upper = {line.strip().upper() for line in desc.splitlines()}
    for section in ("SOURCES", "CREDITS"):
        if section not in upper:
            add("WARN", f"description: no {section} section")
    return desc


def tag_cost(tags):
    return sum(len(t) + (2 if " " in t else 0) for t in tags) + max(len(tags) - 1, 0)


def check_tags(kit):
    text = read_text(kit / "03_TAGS.txt")
    if text is None:
        add("FAIL", "03_TAGS.txt missing")
        return
    tags = [t.strip() for t in text.replace("\n", ",").split(",") if t.strip()]
    cost = tag_cost(tags)
    level = "FAIL" if cost > 500 else "WARN" if cost > 400 else "OK"
    add(level, f"tags: {len(tags)} tags, {cost} of 500 characters (API count)")
    check_brackets("tags", text)
    lowered = [t.lower() for t in tags]
    dupes = {t for t in lowered if lowered.count(t) > 1}
    if dupes:
        add("WARN", f"tags: duplicates {sorted(dupes)}")
    if any(t.startswith("#") for t in tags):
        add("WARN", "tags: remove # from tags")


def check_thumbnails(kit):
    try:
        from PIL import Image
    except ImportError:
        add("WARN", "Pillow not installed (pip install pillow); thumbnails not checked")
        return
    files = sorted(p for p in kit.glob("00_THUMBNAIL*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".bmp"})
    if not files:
        add("FAIL", "no 00_THUMBNAIL* image")
        return
    main = [p for p in files if "mobile" not in p.stem.lower()]
    if len(main) < 2:
        add("WARN", "only one thumbnail; Test & Compare needs 2 or 3")
    for p in files:
        size = p.stat().st_size
        with Image.open(p) as im:
            w, h = im.size
            fmt_name = im.format
        msg = f"{p.name}: {w}x{h} {fmt_name}, {size / 1_048_576:.2f} MB"
        if w < 640:
            add("FAIL", msg + " (width under 640)")
        elif size > 50 * 1_048_576:
            add("FAIL", msg + " (over 50 MB)")
        elif abs(w / h - 16 / 9) > 0.01:
            add("WARN", msg + " (not 16:9)")
        elif size > 2 * 1_048_576 and "mobile" not in p.stem.lower():
            add("WARN", msg + " (over 2 MB: upload from a computer, or add a _mobile copy)")
        elif w < 1280:
            add("WARN", msg + " (YouTube recommends 3840x2160)")
        else:
            note = "" if w >= 3840 else " (accepted; YouTube recommends 3840x2160)"
            add("OK", msg + note)


SRT_TIME = re.compile(r"^(\d{2}):(\d{2}):(\d{2})[,.](\d{3}) --> (\d{2}):(\d{2}):(\d{2})[,.](\d{3})")


def check_srt(kit, duration):
    path = kit / "05_CAPTIONS_English.srt"
    text = read_text(path)
    if text is None:
        add("FAIL", "05_CAPTIONS_English.srt missing or unreadable")
        return
    blocks = re.split(r"\n\s*\n", text.replace("\r\n", "\n"))
    prev_end = 0.0
    errors = 0
    last_end = 0.0
    for n, block in enumerate(blocks, start=1):
        lines = block.strip().splitlines()
        if len(lines) < 3:
            add("FAIL", f"SRT cue {n}: incomplete block")
            errors += 1
            continue
        if lines[0].strip() != str(n):
            add("FAIL", f"SRT cue {n}: numbered {lines[0].strip()!r}")
            errors += 1
        m = SRT_TIME.match(lines[1].strip())
        if not m:
            add("FAIL", f"SRT cue {n}: bad time line {lines[1]!r}")
            errors += 1
            continue
        g = [int(x) for x in m.groups()]
        start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        if end <= start:
            add("FAIL", f"SRT cue {n}: ends before it starts")
            errors += 1
        if start < prev_end - 0.001:
            add("FAIL", f"SRT cue {n}: overlaps the previous cue")
            errors += 1
        prev_end = end
        last_end = max(last_end, end)
        if errors > 10:
            add("FAIL", "SRT: stopping after 10 errors")
            return
    if duration is not None and last_end > duration + 0.05:
        add("FAIL", f"SRT: last cue ends at {fmt(last_end)}, after the video ends ({fmt(duration)})")
        errors += 1
    if not errors:
        add("OK", f"SRT: {len(blocks)} cues, ordered, no overlaps, last ends {fmt(last_end)}")


def check_credits(kit, desc):
    credits = read_text(kit / "07_CREDITS_AND_LICENSES.md")
    if credits is None or desc is None:
        return
    for lic in ("CC BY-SA", "CC BY-NC", "CC BY"):
        if lic in credits and lic not in desc:
            add("FAIL", f"07 lists a {lic} asset but the description has no {lic} credit")


def check_variety(kit, desc, previous):
    if desc is None:
        return
    mine = prose_part(desc).lower().split()
    compared = 0
    for prev in previous:
        if prev.resolve() == kit.resolve():
            continue
        other = read_text(prev / "02_DESCRIPTION.txt")
        if not other:
            continue
        compared += 1
        r = difflib.SequenceMatcher(None, mine, prose_part(other).lower().split()).ratio()
        if r > 0.5:
            add("WARN", f"description opening is {r:.0%} alike to {prev}; rewrite it (inauthentic content policy)")
    if previous and not compared:
        add("WARN", "no earlier 02_DESCRIPTION.txt found to compare against")
    elif compared:
        add("OK", f"description opening compared with {compared} earlier kit(s)")


def check_files(kit):
    expected = [
        "00_START_HERE.md", "04_PINNED_COMMENT.txt", "06_UPLOAD_SETTINGS.md",
        "07_CREDITS_AND_LICENSES.md", "08_BUILD_REPORT.md", "09_SEO_RESEARCH.md", "10_PROMO.md",
    ]
    for name in expected:
        if not (kit / name).exists():
            level = "FAIL" if name in {"04_PINNED_COMMENT.txt", "06_UPLOAD_SETTINGS.md", "07_CREDITS_AND_LICENSES.md"} else "WARN"
            add(level, f"{name} missing")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kit", type=Path)
    ap.add_argument("--video", type=Path)
    ap.add_argument("--previous", type=Path, nargs="*", default=[])
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    if not args.kit.is_dir():
        sys.exit(f"not a folder: {args.kit}")

    duration = check_video(args.video)
    check_titles(args.kit)
    desc = check_description(args.kit, duration)
    check_tags(args.kit)
    check_thumbnails(args.kit)
    check_srt(args.kit, duration)
    check_credits(args.kit, desc)
    check_variety(args.kit, desc, args.previous)
    check_files(args.kit)

    order = {"FAIL": 0, "WARN": 1, "OK": 2}
    lines = [f"[{lvl}] {msg}" for lvl, msg in sorted(results, key=lambda r: order[r[0]])]
    counts = {k: sum(1 for r in results if r[0] == k) for k in order}
    lines.append(f"\n{counts['FAIL']} FAIL, {counts['WARN']} WARN, {counts['OK']} OK")
    report = "\n".join(lines)
    print(report)
    if args.out:
        args.out.write_text(report + "\n", encoding="utf-8")
    sys.exit(1 if counts["FAIL"] else 0)


if __name__ == "__main__":
    main()
