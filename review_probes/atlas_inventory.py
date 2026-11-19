#!/usr/bin/env python3
"""Offline, read-only Atlas diagnostics; source statuses are catalog claims.

Usage: python review_probes/atlas_inventory.py [--repo /path/to/checkout]
Does not download the absent original HTML or treat a recorded hash as parity.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
args = parser.parse_args()
sys.path.insert(0, str(args.repo.resolve() / "flyte"))

from gobbler_flyte import atlas
from gobbler_flyte.memory import MemoryStore, Reader, compile_context

a = atlas.load()
lib = MemoryStore()
try:
    counts = atlas.seed_library(lib)
    rows = lib.all()
    t5 = lib.get("aie:T5")
    packet = compile_context(lib, Reader("assayer", "2035-01-01T00:00:00Z", {}),
                             kinds=("procedure", "semantic_claim"), query="benchmark", journal=False)
    print(json.dumps({
        "seeded": counts,
        "grades": dict(Counter(r.evidence_level for r in rows)),
        "source_self_report_status": dict(Counter(s[7] for s in a["S"])),
        "T5_grade": t5.evidence_level,
        "T5_parent_grades": [lib.get(p).evidence_level for p in t5.parent_ids],
        "without_valid_to": sum(r.valid_to is None for r in rows),
        "2035_context_rows_packed": len(packet["memories"]),
        "2035_exclusions": dict(Counter(packet["excluded"].values())),
        "theme_counts_from_port_only": atlas.theme_counts(a),
        "themeOf_source_parity": "not_verified: original HTML absent from reviewed repository",
        "claimed_original_html_sha256": a["provenance"]["html_sha256"],
    }, indent=2, sort_keys=True))
finally:
    lib.close()
