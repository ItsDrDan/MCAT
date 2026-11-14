#!/usr/bin/env python3
"""The question bank lives in two data files that practice.html loads:

    data/bank-q.js   const Q = [ ...single questions, one per line... ];
    data/bank-p.js   const P = [ ...passages, one per line... ];

Use load() and save() from other tools, so the one-item-per-line layout (small, readable git diffs) is kept.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATHS = {"Q": ROOT / "data" / "bank-q.js", "P": ROOT / "data" / "bank-p.js"}
HEAD = {"Q": "/* Pre-Med Pulse question bank: single questions, one per line. After editing run tools/build_hub_data.py, then tools/validate_bank.py. Never rename or remove an id. */",
        "P": "/* Pre-Med Pulse question bank: passages, one per line. A passage question's ID is <passage id>-q<n>, so never reorder or remove questions; add new ones at the end. */"}

def src():
    """Both data files as one string (for tools that search the raw text)."""
    return "\n".join(PATHS[n].read_text(encoding="utf-8") for n in ("Q", "P"))

def load():
    s = src()
    return tuple(json.loads(re.search(rf"\nconst {n} = (\[.*?\]);\n", s, re.S).group(1)) for n in ("Q", "P"))

def dumps(items):
    return "[\n" + ",\n".join(json.dumps(x, ensure_ascii=False) for x in items) + "\n]"

def save(name, items):
    PATHS[name].write_text(f"{HEAD[name]}\nconst {name} = {dumps(items)};\n", encoding="utf-8")
