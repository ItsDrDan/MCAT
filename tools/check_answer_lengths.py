#!/usr/bin/env python3
"""Guard against the "longest answer is right" giveaway.

Run before every push:  python3 tools/check_answer_lengths.py
Fails (exit 1) if, in any section's passage questions, always picking the
longest choice would score above 30%, or if more than 10% of correct answers
are at least 1.2x longer than every other choice, or if any subject's
single (discrete) questions score above 30%. Chance is 25%.
"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import bank
src = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else bank.src()
Q, P = bank.load()
strip = lambda h: re.sub(r"<[^>]+>", "", str(h))
def lens(q): return [len(strip(o)) for o in q["o"]]
def pick_longest(q):
    L = lens(q); m = max(L); top = [i for i, l in enumerate(L) if l == m]
    return (q["a"] in top) / len(top)
def big_gap(q):
    L = lens(q); return L[q["a"]] >= 1.2 * max(l for i, l in enumerate(L) if i != q["a"])
bad = False
for sec in ["cp", "cars", "bb", "ps"]:
    qs = [q for p in P if p["s"] == sec for q in p["qs"]]
    pl = sum(map(pick_longest, qs)) / len(qs); bg = sum(map(big_gap, qs)) / len(qs)
    flag = pl > 0.30 or bg > 0.10; bad |= flag
    print(f"{sec:5} passages  {len(qs):4} Qs  pick-longest {pl:5.1%}  big-gap {bg:5.1%}  {'FAIL' if flag else 'ok'}")
for subj in ["gc", "oc", "pm", "bc", "bio", "beh", "cars"]:
    qs = [q for q in Q if q["subj"] == subj]
    pl = sum(map(pick_longest, qs)) / len(qs); flag = pl > 0.30; bad |= flag
    print(f"{subj:5} discretes {len(qs):4} Qs  pick-longest {pl:5.1%}  {'FAIL' if flag else 'ok'}")
sys.exit(1 if bad else 0)
