#!/usr/bin/env python3
"""Find questions that may be mis-keyed or confusing, using real student answers.

    python3 tools/item_analysis.py                 # fetch the last 365 days from the live stats URL
    python3 tools/item_analysis.py --days 90
    python3 tools/item_analysis.py --file items.json   # use a saved copy of  <stats URL>?items=1&game=mcat
    python3 tools/item_analysis.py --min 15        # minimum answers before a question is judged (default 15)

Needs the per-question stats add-on (tools/item_stats_apps_script.gs) installed in the stats
Apps Script. Writes a Markdown report to item-analysis.md and prints a summary.

Flags (only for the CURRENT wording of each question; answers from before an edit are counted separately):
  POSSIBLE MIS-KEY   one wrong choice is picked more often than the keyed answer
  TOO HARD           fewer than 30% correct (4-choice chance is 25%) — check the key, wording, and data
  TOO EASY           97%+ correct with 30+ answers — the distractors may be implausible
  DEAD DISTRACTOR    a wrong choice that almost nobody picks (under 3% with 40+ answers)
"""
import json, re, sys, argparse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATS_URL = "https://script.google.com/macros/s/AKfycbylSKoW9GE6AkN4HiC1uts3Y5Z4oUPHY7OQ88vXrjpcanooloYRTIGW9cS5n0dulp4vQg/exec"

ap = argparse.ArgumentParser()
ap.add_argument("--days", type=int, default=365)
ap.add_argument("--file")
ap.add_argument("--min", type=int, default=15)
args = ap.parse_args()

def qver(q):
    """Same fingerprint the site sends (FNV-1a over UTF-16 code units of stem|options, base 36)."""
    s = str(q["q"]) + "|" + "|".join(q["o"])
    h = 2166136261
    for ch in s:
        cp = ord(ch)
        unit = cp if cp < 0x10000 else 0xD800 + ((cp - 0x10000) >> 10)   # JS charCodeAt(0) of the code point
        h ^= unit
        h = (h * 16777619) & 0xFFFFFFFF
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    while True:
        h, r = divmod(h, 36); out = digits[r] + out
        if h == 0: return out

src = (ROOT / "practice.html").read_text(encoding="utf-8")
grab = lambda n: json.loads(re.search(rf"\nconst {n} = (\[.*?\]);\n", src, re.S).group(1))
bank = {}
for q in grab("Q"): bank[q["id"]] = q
for p in grab("P"):
    for i, q in enumerate(p["qs"]): bank[f'{p["id"]}-q{i + 1}'] = dict(q, _passage=p["id"])
daily = ROOT / "data" / "daily.json"
if daily.exists():
    for q in json.loads(daily.read_text(encoding="utf-8")): bank.setdefault(q["id"], q)

if args.file:
    data = json.loads(Path(args.file).read_text(encoding="utf-8"))
else:
    url = f"{STATS_URL}?items=1&game=mcat&days={args.days}"
    with urllib.request.urlopen(url, timeout=60) as r: data = json.loads(r.read().decode("utf-8"))
items = data.get("items", data if isinstance(data, list) else [])
if not items:
    sys.exit("No per-question data yet. Is the Apps Script add-on installed, and have students answered on the updated site?")

strip = lambda h: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(h))).strip()
flags, old, unknown, judged = [], 0, 0, 0
for it in items:
    q = bank.get(it["item"])
    if not q: unknown += 1; continue
    if it.get("ver") and it["ver"] != qver(q): old += 1; continue
    n = it["n"]
    if n < args.min: continue
    judged += 1
    p = it["correct"] / n
    picks = it.get("picks", [0, 0, 0, 0]); tot = sum(picks) or 1
    key = q["a"]
    wrong = [(picks[i], i) for i in range(4) if i != key]
    top_wrong = max(wrong)
    reasons = []
    if top_wrong[0] > picks[key]: reasons.append(f"POSSIBLE MIS-KEY: '{strip(q['o'][top_wrong[1]])[:60]}' picked {top_wrong[0]}× vs key {picks[key]}×")
    if p < 0.30: reasons.append(f"TOO HARD: {p:.0%} correct")
    if p >= 0.97 and n >= 30: reasons.append(f"TOO EASY: {p:.0%} correct")
    if tot >= 40:
        for c, i in wrong:
            if c / tot < 0.03: reasons.append(f"DEAD DISTRACTOR: '{strip(q['o'][i])[:50]}' ({c}/{tot})")
    if reasons:
        flags.append((0 if reasons[0].startswith("POSSIBLE") else 1 if reasons[0].startswith("TOO HARD") else 2, it["item"], n, p, strip(q["q"])[:110], reasons))

flags.sort()
lines = [f"# Item analysis ({data.get('days', args.days)} days, generated {data.get('generated', '')})", "",
         f"Questions with data: {len(items)} · judged (≥{args.min} answers, current wording): {judged} · flagged: {len(flags)} · "
         f"answers to older wording (skipped): {old} · IDs no longer in the bank: {unknown}", ""]
lines += ["| Question | Answers | Correct | Stem | Why flagged |", "|---|---|---|---|---|"]
for _, iid, n, p, stem, reasons in flags:
    lines.append(f"| {iid} | {n} | {p:.0%} | {stem.replace('|', '/')} | {'; '.join(reasons).replace('|', '/')} |")
(ROOT / "item-analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines[:3]))
print(f"Report written to {ROOT / 'item-analysis.md'}")
