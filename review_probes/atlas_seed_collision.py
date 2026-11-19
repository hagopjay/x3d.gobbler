#!/usr/bin/env python3
"""Fail when pinned seeding silently accepts a conflicting immutable record."""
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
    stale = lib.get("aie:K1").model_copy(update={"subject_sha256": "0" * 64})
    with lib.db:
        lib.db.execute("DELETE FROM memory WHERE id = ?", (stale.memory_id,))
    lib.put(stale)
    try:
        atlas.seed_library(lib)
    except ValueError as exc:
        if "immutable memory id collision" not in str(exc):
            raise
        print("conflicting pinned row refused:", exc)
    else:
        raise AssertionError("seed_library silently accepted a stale immutable K1 record")
finally:
    lib.close()
