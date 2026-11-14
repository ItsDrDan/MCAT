#!/usr/bin/env python3
"""Quality checks for the MCAT question bank. Run before every push:

    python3 tools/validate_bank.py            # errors fail (exit 1); warnings are printed
    python3 tools/validate_bank.py --strict   # warnings fail too

GitHub runs this automatically on every push and pull request (.github/workflows/validate.yml).

ERRORS (must fix):
  - broken items: not 4 options, duplicate options, bad answer index, missing explanation,
    why-wrong notes missing or not "" for the correct option
  - duplicate question or passage IDs; bad subject/unit/level values
  - text that points at a fixed option letter or another question ("choice B", "Question 2",
    "same graph"), which breaks because the app shuffles options and questions
  - two passages with the same title (the bank once had 107 duplicates)
  - "paragraph N" references to a paragraph the passage doesn't have
  - hub counts in index.html out of date (fix: python3 tools/build_hub_data.py)
  - a question ID or passage question that existed before is gone (tools/id_manifest.json);
    after a deliberate removal run with --accept-ids
  - bad skill tags; hub "Connects to" links to units that don't exist; a ?mode= deep link no longer handled
WARNINGS (worth a look):
  - "all/none of the above" style options
  - figures with no text alternative for screen readers; images hot-linked from other sites
  - one- or two-word why-wrong notes ("Not this.")
  - science passages under 250 words
"""
import json, re, sys, html, collections as C
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / "practice.html").read_text(encoding="utf-8")
def grab(name):
    m = re.search(rf"\nconst {name} = (\[.*?\]);\n", src, re.S)
    if not m: sys.exit(f"Could not find const {name} in practice.html")
    return json.loads(m.group(1))
Q, P = grab("Q"), grab("P")

UNITS = {"gc": 12, "oc": 12, "pm": 12, "bc": 12, "bio": 12, "beh": 12, "cars": 3}
LEVELS = set("FCARM")
errors, warns = [], []
def err(i, msg): errors.append(f"{i}: {msg}")
def warn(i, msg): warns.append(f"{i}: {msg}")

strip = lambda h: html.unescape(re.sub(r"<[^>]+>", " ", str(h)))
norm = lambda s: re.sub(r"\s+", " ", strip(s)).strip()
LETTER_REF = re.compile(r"\b(choices?|options?|answers?)\s+\(?[A-D]\)?(\s+(and|or)\s+\(?[A-D]\)?)?\b(?![\w-])")
XREF = re.compile(r"\b(question\s+\d+|same (graph|figure|trace|table|plot) (as|from) (above|before|the previous)|the previous question|the question above)\b", re.I)
LEAD_LETTER = re.compile(r"^\s*[A-D]\s*(,|$)")
NONE_OPT = re.compile(r"^(all|none) of (the )?(above|these|them|the (three|four) \w+)\b|^no (row|option) (matches|applies)", re.I)

def check_item(iid, q, passage=False):
    o, a, e, w = q.get("o"), q.get("a"), q.get("e"), q.get("w")
    if not isinstance(o, list) or len(o) != 4: err(iid, "must have exactly 4 options"); return
    # case matters (genotypes like EE / Ee / ee); drawing-only options are compared by their markup
    if len({norm(x) or str(x) for x in o}) != 4: err(iid, "duplicate options")
    if not isinstance(a, int) or not 0 <= a < 4: err(iid, f"bad answer index {a!r}")
    if not e or not all(isinstance(s, str) and s.strip() for s in e): err(iid, "missing explanation steps")
    if not isinstance(w, list) or len(w) != 4: err(iid, "needs 4 why-wrong notes")
    else:
        if isinstance(a, int) and 0 <= a < 4 and w[a]: err(iid, "why-wrong note for the correct option must be empty")
        for k, s in enumerate(w):
            if isinstance(a, int) and k != a:
                if not str(s).strip(): err(iid, f"why-wrong note {k} is empty")
                elif len(norm(s).split()) <= 2: warn(iid, f"thin why-wrong note: {norm(s)!r}")
    texts = [q.get("q", "")] + list(o) + list(e or []) + list(w or []) + [q.get("t") or ""]
    for s in texts:
        if LETTER_REF.search(norm(s)): err(iid, f"refers to a fixed option letter: {norm(s)[:70]!r}"); break
    for s in [q.get("q", "")] + list(e or []):
        if XREF.search(norm(s)): err(iid, f"refers to another question or figure position: {norm(s)[:70]!r}"); break
    for s in o:
        if LEAD_LETTER.match(norm(s)): err(iid, f"option starts with a bare letter: {norm(s)!r}"); break
        if NONE_OPT.match(norm(s)): warn(iid, f"'none/all of the above'-style option: {norm(s)!r}")

ids = C.Counter(x["id"] for x in Q + P)
for i, n in ids.items():
    if n > 1: err(i, f"ID used {n} times")
for q in Q:
    if q.get("subj") not in UNITS or not 1 <= q.get("unit", 0) <= UNITS.get(q.get("subj"), 0): err(q["id"], "bad subject/unit")
    if q.get("lv") not in LEVELS: err(q["id"], f"bad level {q.get('lv')!r}")
    check_item(q["id"], q)

cap = re.compile(r"^(figure|fig\.|table|scheme|graph)\s*\d", re.I)
def prose_paragraphs(t):
    t = re.sub(r"<table.*?</table>|<figure.*?</figure>|<svg.*?</svg>", "\n", t, flags=re.S)
    return [x for x in (norm(y) for y in re.findall(r"<p[^>]*>(.*?)</p>", t, re.S)) if len(x.split()) >= 3 and not cap.match(x)]
PARA = re.compile(r"[Pp]aragraphs?\s+(\d+)((?:\s*(?:,|and|–|-|to)\s*\d+)*)")
titles = C.defaultdict(list)
for p in P:
    titles[p["title"].strip().lower()].append(p["id"])
    if p.get("s") not in ("cp", "bb", "ps", "cars") or p.get("subj") not in UNITS or not 1 <= p.get("unit", 0) <= UNITS[p.get("subj")]:
        err(p["id"], "bad section/subject/unit")
    if not p.get("qs"): err(p["id"], "passage has no questions")
    n_par = len(prose_paragraphs(p["text"]))
    words = len(strip(re.sub(r"<table.*?</table>|<svg.*?</svg>", " ", p["text"], flags=re.S)).split())
    if p.get("s") != "cars" and words < 250: warn(p["id"], f"short science passage ({words} words)")
    for k, q in enumerate(p.get("qs", [])):
        iid = f"{p['id']}#{k + 1}"
        check_item(iid, q, passage=True)
        for s in [q.get("q", "")] + list(q.get("o", [])) + list(q.get("e", [])) + list(q.get("w", [])):
            for m in PARA.finditer(norm(s)):
                nums = [int(x) for x in re.findall(r"\d+", m.group(1) + m.group(2))]
                if n_par and max(nums) > n_par: err(iid, f"cites paragraph {max(nums)} but the passage has {n_par}")
for t, v in titles.items():
    if len(v) > 1: err(", ".join(v), f"duplicate passage title {t!r}")

allfig = [(q["id"], q["fig"]) for q in Q if q.get("fig")] + [(p["id"], p["text"]) for p in P]
for iid, f in allfig:
    for svg in re.findall(r"<svg[^>]*>", f):
        if not re.search(r'aria-label=|role="img"|aria-labelledby=', svg) and "<title>" not in f:
            warn(iid, "SVG figure has no text alternative (aria-label)"); break
    for img in re.findall(r"<img[^>]*>", f):
        if not re.search(r'alt="[^"]+', img): warn(iid, "image has no alt text")
        if re.search(r'src="https?://', img): warn(iid, "image is hot-linked from another site")

# hub counts must match the bank
idx = (ROOT / "index.html").read_text(encoding="utf-8")
m = re.search(r'^const HUB=(\{.*?\});$', idx, re.M)
if m:
    total = len(Q) + sum(len(p["qs"]) for p in P)
    if json.loads(m.group(1)).get("total") != total: err("index.html", f"hub total is out of date (bank has {total}); run python3 tools/build_hub_data.py")

# the Daily 5 pool must serve the bank's current version of each question
daily_path = ROOT / "data" / "daily.json"
if daily_path.exists():
    QB = {q["id"]: q for q in Q}
    stale = [d["id"] for d in json.loads(daily_path.read_text(encoding="utf-8"))
             if d["id"] not in QB or any(d.get(k) != QB[d["id"]].get(k) for k in ("q", "o", "a", "e", "w", "t", "lv", "k", "fig"))]
    if stale: err("data/daily.json", f"{len(stale)} Daily 5 question(s) differ from the bank (e.g. {stale[:3]}); run python3 tools/build_hub_data.py")

# ---- stable IDs: saved progress, review queues and item stats all point at these ----
# tools/id_manifest.json lists every question ID and each passage's question count. An ID that disappears,
# or a passage that loses questions, is an error. After a deliberate removal: python3 tools/validate_bank.py --accept-ids
man_path = ROOT / "tools" / "id_manifest.json"
now_ids = {"q": sorted(q["id"] for q in Q), "p": {p["id"]: len(p["qs"]) for p in P}}
if "--accept-ids" in sys.argv or not man_path.exists():
    man_path.write_text(json.dumps(now_ids, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"ID manifest written: {len(now_ids['q']):,} question IDs, {len(now_ids['p'])} passages")
else:
    man = json.loads(man_path.read_text(encoding="utf-8"))
    gone = sorted(set(man["q"]) - set(now_ids["q"]))
    if gone: err("id_manifest", f"{len(gone)} question ID(s) were removed or renamed (e.g. {gone[:3]}); students' saved progress points at them")
    for pid, n_old in man["p"].items():
        if pid not in now_ids["p"]: err(pid, "passage ID was removed or renamed; saved progress points at its questions")
        elif now_ids["p"][pid] < n_old: err(pid, f"passage had {n_old} questions and now has {now_ids['p'][pid]}; add new questions at the end, never remove or renumber")
    added = len(set(now_ids["q"]) - set(man["q"])) + sum(1 for pid in now_ids["p"] if pid not in man["p"])
    if added: warn("id_manifest", f"new IDs not in the manifest yet ({added}); run python3 tools/validate_bank.py --accept-ids")

# ---- tags the app reads: AAMC skill (k), CARS skill (c) ----
for q in Q + [x for p in P for x in p["qs"]]:
    iid = q.get("id") or q.get("q", "")[:40]
    if "k" in q and q["k"] not in (1, 2, 3, 4): err(iid, f"bad skill tag k={q['k']!r}")
    if "c" in q and q["c"] not in ("R1", "R2", "R3"): err(iid, f"bad CARS skill tag c={q['c']!r}")

# ---- hub links between related units must point at real units ----
m = re.search(r'^const REL=(\{.*?\});$', idx, re.M | re.S)
if m:
    for k, vs in json.loads(m.group(1)).items():
        for x in [k] + vs:
            sb, _, un = x.partition(":")
            if sb not in UNITS or not un.isdigit() or not 1 <= int(un) <= UNITS[sb]: err("index.html", f"related-unit link points at a unit that doesn't exist: {x}")

# ---- deep links documented in the README must still be understood by practice.html ----
for mode in ("drill", "review", "passage", "timed", "eqs", "full", "gym", "real"):
    if f'"{mode}"' not in src.split("const Q = ")[0] + src[-60000:]: err("practice.html", f"deep link ?mode={mode} is no longer handled")

strict = "--strict" in sys.argv
kinds = C.Counter(w.split(": ", 1)[1].split(":")[0].split("(")[0].strip() for w in warns)
print(f"{len(Q):,} single questions, {len(P)} passages, {sum(len(p['qs']) for p in P):,} passage questions")
print(f"ERRORS: {len(errors)}")
for e_ in errors[:200]: print("  ✗", e_)
print(f"WARNINGS: {len(warns)}  " + "; ".join(f"{k} ×{n}" for k, n in kinds.most_common(8)))
if "--all" in sys.argv:
    for w_ in warns: print("  !", w_)
sys.exit(1 if errors or (strict and warns) else 0)
