#!/usr/bin/env python3
"""Rebuild every passage that is generated from a source file in tools/ (drawn structures, physics diagrams, ...)
into practice.html. Needs RDKit for the organic files: pip install rdkit.
Run from the repo root:  python3 tools/build_figure_passages.py"""
import sys, os, importlib
sys.path.insert(0, os.path.dirname(__file__))
from passage_kit import add_to_practice
SOURCES = ["oc_structures_1a", "oc_structures_1b", "oc_structures_2a", "oc_structures_2b",
           "pm_diagrams_1a", "pm_diagrams_1b"]
new = [p for m in SOURCES for p in importlib.import_module(m).P]
print(add_to_practice(new), "figure passages written")
