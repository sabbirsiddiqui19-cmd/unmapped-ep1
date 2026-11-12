#!/usr/bin/env python3
"""Move the newest CSV that the browser just downloaded into the research folder.

  collect_download.py --dest trends/US_youtube_5y_a.csv [--since-minutes 5] [--downloads ~/Downloads]
"""
import argparse
import shutil
import sys
import time
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", type=Path, required=True)
    ap.add_argument("--since-minutes", type=float, default=5)
    ap.add_argument("--downloads", type=Path, default=Path.home() / "Downloads")
    ap.add_argument("--wait", type=float, default=20, help="seconds to wait for the file to appear")
    args = ap.parse_args()

    deadline = time.time() + args.wait
    while True:
        cutoff = time.time() - args.since_minutes * 60
        found = [p for p in args.downloads.glob("*.csv") if p.stat().st_mtime >= cutoff]
        partial = list(args.downloads.glob("*.crdownload"))
        if found and not partial:
            break
        if time.time() > deadline:
            sys.exit(f"no new CSV in {args.downloads} from the last {args.since_minutes} minutes")
        time.sleep(1)

    newest = max(found, key=lambda p: p.stat().st_mtime)
    args.dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(newest), args.dest)
    print(f"{newest.name} -> {args.dest}")


if __name__ == "__main__":
    main()
