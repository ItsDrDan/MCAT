#!/usr/bin/env python3
"""Rebuild the hub's question counts and search index from practice.html.

Run after adding questions:  python3 tools/build_hub_data.py
- Rewrites the `const HUB=...;` line in index.html (unit counts, passage
  counts, subject/section totals) so the hub never shows stale numbers.
- Rewrites data/search.json (one entry per unit; each string is a lowercased
  stem + options, or a passage title or one of its questions, for topic search).
"""
import json, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / "practice.html").read_text(encoding="utf-8")
Q = json.loads(re.search(r"\nconst Q = (\[.*?\]);\n", src, re.S).group(1))
P = json.loads(re.search(r"\nconst P = (\[.*?\]);\n", src, re.S).group(1))

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
print(f"HUB updated: {HUB['total']:,} questions ({len(Q):,} single + {HUB['total'] - len(Q):,} in {len(P)} passages)")
print("Sections:", HUB["secCount"])
