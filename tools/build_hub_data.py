#!/usr/bin/env python3
"""Rebuild the hub's question counts and search index from practice.html.

Run after adding questions:  python3 tools/build_hub_data.py
- Rewrites the `const HUB=...;` line in index.html (unit counts, passage
  counts, subject/section totals) so the hub never shows stale numbers.
- Refreshes data/daily.json (the Daily 5 pool) so each question matches the bank.
- Rewrites data/search.json (one entry per unit; each string is a lowercased
  stem + options, or a passage title or one of its questions, for topic search).
"""
import json, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent)); import bank
src = bank.src()
Q, P = bank.load()

idx_path = ROOT / "index.html"
idx = idx_path.read_text(encoding="utf-8")
m = re.search(r"^const HUB=(\{.*?\});$", idx, re.M)
if not m:
    sys.exit("Could not find the HUB line in index.html")
HUB = json.loads(m.group(1))

strip = lambda h: re.sub(r"<[^>]+>", " ", str(h))
def norm(s):
    s = unicodedata.normalize("NFKD", strip(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[–—−-]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

counts, pcount, search = {}, {}, []
for subj, units in HUB["units"].items():
    n = len(units)
    c = [0] * n; pc = [0] * n; texts = [[] for _ in range(n)]
    for q in Q:
        if q["subj"] == subj and 1 <= q["unit"] <= n:
            c[q["unit"] - 1] += 1
            texts[q["unit"] - 1].append(norm(q["q"] + " " + " ".join(q["o"])))
    for p in P:
        if p["subj"] == subj and 1 <= p["unit"] <= n:
            u = p["unit"] - 1
            c[u] += len(p["qs"]); pc[u] += 1
            texts[u].append(norm(p["title"]))
            texts[u].extend(norm(x["q"] + " " + " ".join(x["o"])) for x in p["qs"])
    counts[subj], pcount[subj] = c, pc
    for u, name in enumerate(units):
        search.append({"s": subj, "u": u + 1, "name": name, "t": texts[u]})

HUB["counts"], HUB["pcount"] = counts, pcount
HUB["subjCount"] = {s: sum(c) for s, c in counts.items()}
sc = HUB["subjCount"]
HUB["secCount"] = {"cp": sc["gc"] + sc["oc"] + sc["pm"] + sc["bc"], "cars": sc["cars"],
                   "bb": sc["bio"] + sc["bc"], "ps": sc["beh"]}
HUB["total"] = len(Q) + sum(len(p["qs"]) for p in P)
HUB["passages"] = len(P)

idx = idx[:m.start()] + "const HUB=" + json.dumps(HUB, ensure_ascii=False, separators=(",", ":")) + ";" + idx[m.end():]
# keep the share-card description in step with the real total
rounded = f"{HUB['total'] // 100 * 100:,}+"
idx = re.sub(r'(<meta property="og:description" content=")[\d,]+\+', r"\g<1>" + rounded, idx)
idx_path.write_text(idx, encoding="utf-8")
(ROOT / "data" / "search.json").write_text(json.dumps(search, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

# Daily 5 pool: keep the same question IDs, but always serve the bank's current version of each
# (otherwise fixes made in practice.html never reach the Daily 5, and per-question stats from the
# Daily 5 carry an out-of-date wording fingerprint).
daily_path = ROOT / "data" / "daily.json"
DAILY_FIELDS = ["id", "subj", "unit", "lv", "q", "o", "a", "e", "w", "k", "t", "fig"]
QB = {q["id"]: q for q in Q}
daily_old = json.loads(daily_path.read_text(encoding="utf-8"))
daily_new, dropped, refreshed = [], [], 0
for d in daily_old:
    q = QB.get(d["id"])
    if not q: dropped.append(d["id"]); continue
    fresh = {k: q[k] for k in DAILY_FIELDS if k in q}
    if fresh != d: refreshed += 1
    daily_new.append(fresh)
daily_path.write_text(json.dumps(daily_new, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

print(f"HUB updated: {HUB['total']:,} questions ({len(Q):,} single + {HUB['total'] - len(Q):,} in {len(P)} passages)")
print("Sections:", HUB["secCount"])
print(f"Daily 5 pool: {len(daily_new)} questions, {refreshed} refreshed from the bank" + (f", {len(dropped)} dropped (no longer in the bank): {dropped[:5]}" if dropped else ""))

# Stamp practice.html's bank version (BANKV) and the offline worker's cache name with a hash of the bank,
# so a browser never pairs a new page with an old saved bank, and old offline copies are dropped.
import hashlib
stamp = hashlib.md5(src.encode("utf-8")).hexdigest()[:10]
app_path = ROOT / "practice.html"
app = app_path.read_text(encoding="utf-8")
app2 = re.sub(r'const BANKV="[0-9a-f]*"', f'const BANKV="{stamp}"', app)
if app2 != app: app_path.write_text(app2, encoding="utf-8"); print("Bank stamp:", stamp)
sw_path = ROOT / "sw.js"
if sw_path.exists():
    sw = sw_path.read_text(encoding="utf-8")
    assets = sorted("assets/" + p.relative_to(ROOT / "assets").as_posix() for p in (ROOT / "assets").rglob("*") if p.is_file() and p.suffix in (".webp", ".png", ".svg", ".jpg"))
    sw2 = re.sub(r'const CACHE = "mcat-[0-9a-f]*";', f'const CACHE = "mcat-{stamp}";', sw)
    sw2 = re.sub(r'const DATA = \[.*?\];', "const DATA = " + json.dumps([f"data/bank/{c}.js?v={stamp}" for c in bank.CHUNKS] + ["data/daily.json", "data/search.json", "data/learn.json"]) + ";", sw2, flags=re.S)
    sw2 = re.sub(r'const ART = \[.*?\];', "const ART = " + json.dumps(assets) + ";", sw2, flags=re.S)
    if sw2 != sw: sw_path.write_text(sw2, encoding="utf-8"); print("Offline worker updated:", f"mcat-{stamp}", len(assets), "images")
