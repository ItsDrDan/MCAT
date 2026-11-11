#!/usr/bin/env python3
"""Rebuild the organic chemistry structure passages (ocs-*) into practice.html.
Needs RDKit: pip install rdkit.   Run from the repo root:  python3 tools/build_oc_structures.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from passage_kit import add_to_practice
import oc_structures_1a, oc_structures_1b
new = oc_structures_1a.P + oc_structures_1b.P
print(add_to_practice(new), "organic structure passages written")
