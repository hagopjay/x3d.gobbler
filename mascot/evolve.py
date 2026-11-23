#!/usr/bin/env python3
"""Breed the Gobbler's fan: a small MAP-Elites run over the fan genome. The first real try of the `qd-evolve` frontier.

    python3 mascot/evolve.py --board frontier/runs/<run>/board.json --out mascot/v6/elites.json

What is optimised, and by what (thesis T8: an optimiser learns the grader it is shown):
  shown to the search   fitness = fan area covered minus twice the area where two different feathers overlap, in the
                        front view, on a 0.2-unit grid; a feather dipping under y = 0.4 is refused; and every candidate
                        that would enter the archive must pass the pinned x3d_mcp validator (XSD + semantic).
  hidden from it        the render check (X_ITE, non-black) and his eye. Neither is ever fed back here.
  caps (thesis T13)     generations and batch are fixed before the run; no retry on refusal.

The archive is 3 x 3: spread (narrow, medium, wide) by curl (flat, cupped, swept). Nine different birds, not one
winner, because taste is his and a single optimum would only show what the fitness function likes.
Seeded; standard library plus the repository's own validator adapter.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "tools"))
import build_mascot as bm          # noqa: E402
import validate_scene as vs        # noqa: E402

GENERATIONS, BATCH, SEED, CELL = 120, 16, 11, 0.2
SPREAD_BINS, CURL_BINS = (150.0, 205.0), (0.08, 0.45)
BIN_NAMES = (("narrow", "medium", "wide"), ("flat", "cupped", "swept"))


def clamp(k, v):
    lo, hi = bm.GENE_RANGE[k]
    return int(round(min(hi, max(lo, v)))) if k == "tiers" else round(min(hi, max(lo, v)), 4)


FROZEN: dict = {}          # genes the search may not touch (name -> fixed value); set from --freeze


def random_genome(rng):
    return {k: FROZEN.get(k, clamp(k, rng.uniform(*bm.GENE_RANGE[k]))) for k in bm.GENE_RANGE}


def mutate(g, rng):
    h = dict(g)
    for k, (lo, hi) in bm.GENE_RANGE.items():
        if k not in FROZEN and rng.random() < 0.35:
            h[k] = clamp(k, g[k] + rng.gauss(0, 0.15) * (hi - lo))
    return h


def cell_of(g):
    return (sum(g["spread"] > b for b in SPREAD_BINS), sum(g["curl"] > b for b in CURL_BINS))


def measure(rows, g):
    """Front-view coverage and overlap from the vane sample points. Pure geometry, no renderer."""
    *_, samples = bm.build_fan(rows, g, with_beads=False)
    lengths = sorted(ft["length"] / (1 - 0.16 * ft["tier"]) for ft in bm.fan_layout(rows, g))
    grid, low = {}, 0
    for (x, y, _z), fid in samples:
        if y < 0.4: low += 1
        grid.setdefault((int(x // CELL), int(y // CELL)), set()).add(fid)
    covered = len(grid) * CELL * CELL
    overlap = sum(len(v) > 1 for v in grid.values()) * CELL * CELL
    return {"covered": round(covered, 3), "overlap": round(overlap, 3), "below_floor": low,
            "median_length_share": round(lengths[len(lengths) // 2] / lengths[-1], 3),
            "fitness": round(covered - 2 * overlap, 3)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--board", type=Path, required=True); ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--freeze", action="append", default=[], metavar="GENE=VALUE", help="take a gene away from the search")
    a = ap.parse_args(argv)
    for kv in a.freeze:
        k, v = kv.split("="); assert k in bm.GENE_RANGE, k
        FROZEN[k] = float(v)
    board = json.loads(a.board.read_text(encoding="utf-8")); rows = board["rows"]
    rng = random.Random(SEED); t0 = time.time()
    identity = vs.instrument_identity()
    archive, log = {}, []
    n = {"evaluated": 0, "refused_floor": 0, "not_better": 0, "validated": 0, "refused_validator": 0, "admitted": 0}
    for gen in range(GENERATIONS):
        for _ in range(BATCH):
            g = random_genome(rng) if (gen < 3 or not archive) else mutate(archive[rng.choice(sorted(archive))]["genome"], rng)
            m = measure(rows, g); n["evaluated"] += 1
            if m["below_floor"]:
                n["refused_floor"] += 1; continue
            c = cell_of(g)
            if c in archive and archive[c]["measure"]["fitness"] >= m["fitness"]:
                n["not_better"] += 1; continue
            x3d, _ = bm.build("v6", board, g)
            v = vs.validate_bytes(x3d.encode(), identity); n["validated"] += 1
            if v["status"] != "pass":
                n["refused_validator"] += 1; continue
            archive[c] = {"genome": g, "measure": m, "generation": gen, "scene_sha256": hashlib.sha256(x3d.encode()).hexdigest()}
            n["admitted"] += 1
        if gen % 10 == 9 or gen == GENERATIONS - 1:
            log.append({"generation": gen + 1, "cells": len(archive), "best": max(e["measure"]["fitness"] for e in archive.values()),
                        "mean": round(sum(e["measure"]["fitness"] for e in archive.values()) / len(archive), 3)})
    elites = []
    for c in sorted(archive):
        e = archive[c]
        elites.append({"cell": len(elites), "spread_bin": BIN_NAMES[0][c[0]], "curl_bin": BIN_NAMES[1][c[1]], **e})
    base = measure(rows, bm.DEFAULT_GENOME)
    at_bound = {k: sum(e["genome"][k] in bm.GENE_RANGE[k] for e in elites) for k in bm.GENE_RANGE if k not in FROZEN}
    out = {"schema": "gobbler.mascot-evolution/1", "algorithm": "MAP-Elites, 3 x 3 archive (spread by curl)",
           "settings": {"generations": GENERATIONS, "batch": BATCH, "seed": SEED, "grid_cell": CELL, "gene_range": bm.GENE_RANGE, "frozen": dict(FROZEN)},
           "shown_to_search": ["front-view coverage minus twice overlap", "floor refusal y < 0.4", "pinned x3d_mcp validator on archive entry"],
           "hidden_from_search": ["X_ITE render check", "his eye"],
           "validator": {"repository": identity["repository"], "commit": identity["commit"]},
           "board_registry_sha256": board["score_tuple"]["registry_sha256"],
           "counts": n, "hand_drawn_v5_fan": base, "progress": log, "genes_at_a_range_limit": at_bound,
           "seconds": round(time.time() - t0, 1), "model_calls": 0, "elites": elites}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("counts", "hand_drawn_v5_fan", "genes_at_a_range_limit", "seconds")}))
    for e in elites:
        print(e["cell"], e["spread_bin"], e["curl_bin"], e["measure"], e["genome"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
