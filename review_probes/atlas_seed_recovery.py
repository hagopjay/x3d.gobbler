#!/usr/bin/env python3
"""Fail on 9d4671d's incomplete-seed restart; pass after the seed guard fix.

Usage: python review_probes/atlas_seed_recovery.py [--repo /path/to/checkout]
No network, model, allowance, or accrete operation is required.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
args = parser.parse_args()
sys.path.insert(0, str(args.repo.resolve() / "flyte"))

from gobbler_flyte import atlas
from gobbler_flyte.memory import MemoryStore
from gobbler_flyte.runner import Ctx, load_config


with tempfile.TemporaryDirectory() as tmp:
    lib = MemoryStore(Path(tmp) / "library.sqlite")
    original = lib.put

    def interrupted(rec):
        if rec.memory_id == "aie:K1":
            raise RuntimeError("injected crash after T13, before K1")
        return original(rec)

    lib.put = interrupted
    try:
        atlas.seed_library(lib)
    except RuntimeError as exc:
        print(exc)
    if lib.get("aie:T13") is None or lib.get("aie:K1") is not None:
        raise AssertionError("probe did not reach the intended crash boundary")
    lib.close()
    ctx = Ctx(state_dir=Path(tmp), mode="offline", now="2026-11-19T00:00:00Z",
              config=load_config(), allowance={})
    try:
        count = len(ctx.library.all())
        print(f"after real Ctx restart: memories={count}, K1_present={ctx.library.get('aie:K1') is not None}")
        if count != 349 or ctx.library.get("aie:K1") is None:
            raise AssertionError("incomplete library was permanently accepted as seeded")
    finally:
        ctx.mem.close()
        ctx.library.close()
