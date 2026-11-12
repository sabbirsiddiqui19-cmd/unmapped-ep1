#!/usr/bin/env python3
"""Score candidate topics and pick one, using fixed weights, gates and tie rules.

  score.py scores.json --out TOPIC_SCORES.md

scores.json:
{"candidates": [{
   "topic": "Poyais",
   "scores":   {"demand": 4, "gap": 3, "sources": 4, "map": 5, "channel": 4, "safety": 5},
   "evidence": {"demand": "yt/summary.md: fresh views US 500,000 ...", ...},
   "signals_collected": 3, "signals_disagree": false,
   "finalist": true,
   "gates": {"two_t1t2_sources": true, "hook_fact_verified": true, "safe_map": true},
   "recent_uploads_12m": 2,
   "risk": "...", "opening_fact": "..."
}]}
"""
import argparse
import json
import sys
from pathlib import Path

WEIGHTS = {"demand": 30, "gap": 20, "sources": 20, "map": 15, "channel": 10, "safety": 5}
LABELS = {"demand": "US/UK demand", "gap": "Gap", "sources": "Source strength", "map": "Map fit",
          "channel": "Channel fit", "safety": "Safety"}
GATES = {"two_t1t2_sources": "2+ T1/T2 sources opened", "hook_fact_verified": "opening fact verified by 2 sources",
         "safe_map": "license-safe map found"}
TIE_MARGIN = 5


def confidence(c):
    n = int(c.get("signals_collected", 0))
    if n >= 3 and not c.get("signals_disagree"):
        return "High"
    if n >= 2:
        return "Medium"
    return "Low"


def validate(c):
    problems = []
    for part in WEIGHTS:
        v = c.get("scores", {}).get(part)
        if not isinstance(v, (int, float)) or not 0 <= v <= 5:
            problems.append(f"{part} score missing or outside 0-5")
        elif v > 0 and not str(c.get("evidence", {}).get(part, "")).strip():
            problems.append(f"{part} scored {v} without evidence")
    return problems


def total(c):
    return round(sum(WEIGHTS[p] * c["scores"][p] / 5 for p in WEIGHTS), 1)


def blockers(c):
    out = []
    if confidence(c) == "Low":
        out.append("confidence Low")
    if c["scores"]["safety"] < 5:
        out.append("safety below 5")
    if c["scores"]["sources"] < 3:
        out.append("source strength below 3")
    if not c.get("finalist"):
        out.append("not deep-checked")
    else:
        for g, label in GATES.items():
            if not c.get("gates", {}).get(g):
                out.append(f"gate failed: {label}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scores", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    cands = json.loads(args.scores.read_text(encoding="utf-8"))["candidates"]
    bad = {c["topic"]: validate(c) for c in cands}
    if any(bad.values()):
        for t, p in bad.items():
            for x in p:
                print(f"INVALID {t}: {x}", file=sys.stderr)
        sys.exit(2)

    for c in cands:
        c["_total"], c["_conf"], c["_block"] = total(c), confidence(c), blockers(c)
    ranked = sorted(cands, key=lambda c: c["_total"], reverse=True)
    eligible = [c for c in ranked if not c["_block"]]

    winner, tie_note = None, ""
    if eligible:
        best = eligible[0]["_total"]
        close = [c for c in eligible if best - c["_total"] <= TIE_MARGIN]
        close.sort(key=lambda c: (-c["scores"]["demand"], -c["scores"]["gap"],
                                  c.get("recent_uploads_12m", 99), -c["_total"]))
        winner = close[0]
        if len(close) > 1:
            tie_note = (f"{len(close)} topics within {TIE_MARGIN} points; tie broken by US/UK demand, "
                        "then gap, then fewer uploads in the last 12 months.")

    head = "| # | Topic | Total /100 | " + " | ".join(f"{LABELS[p]} ({WEIGHTS[p]})" for p in WEIGHTS) + \
           " | Confidence | Can win? |"
    lines = ["# Topic scores", "", head, "|" + "---|" * (len(WEIGHTS) + 5)]
    for i, c in enumerate(ranked, 1):
        cells = " | ".join(str(c["scores"][p]) for p in WEIGHTS)
        status = "yes" if not c["_block"] else "no: " + "; ".join(c["_block"])
        lines.append(f"| {i} | {c['topic']} | {c['_total']} | {cells} | {c['_conf']} | {status} |")

    lines += ["", "## Evidence", ""]
    for c in ranked:
        lines.append(f"### {c['topic']}")
        for p in WEIGHTS:
            ev = c.get("evidence", {}).get(p) or "NO DATA"
            lines.append(f"- **{LABELS[p]} {c['scores'][p]}/5:** {ev}")
        if c.get("risk"):
            lines.append(f"- **Risk:** {c['risk']}")
        if c.get("opening_fact"):
            lines.append(f"- **Opening fact:** {c['opening_fact']}")
        lines.append("")

    lines.append("## Decision")
    if winner:
        lines.append(f"Winner: **{winner['topic']}** ({winner['_total']}/100, confidence {winner['_conf']}).")
        if tie_note:
            lines.append(tie_note)
    else:
        lines.append("No topic passed every gate. See the 'Can win?' column.")
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(json.dumps({"winner": winner["topic"] if winner else None}))
    sys.exit(0 if winner else 3)


if __name__ == "__main__":
    main()
