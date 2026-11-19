#!/usr/bin/env python3
"""Fail on hardcoded thesis L at 9d4671d; pass when premise grades are inherited."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
args = parser.parse_args()
sys.path.insert(0, str(args.repo.resolve() / "flyte"))

from gobbler_flyte import atlas
from gobbler_flyte.memory import MemoryStore

lib = MemoryStore()
try:
    atlas.seed_library(lib)
    t5 = lib.get("aie:T5")
    parents = [lib.get(p).evidence_level for p in t5.parent_ids]
    print(f"T5 grade={t5.evidence_level}, cited concept grades={parents}")
    if parents != ["S"] * 5 or t5.evidence_level != "S":
        raise AssertionError("thesis grade exceeds all five Suspected premises")
finally:
    lib.close()
