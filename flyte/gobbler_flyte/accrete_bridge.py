"""x3d.accrete as the Gobbler's referee and memory.

Witness calls `accretion.gate.gate_fragment` (bounded vocabulary, DEF/USE, ROUTE
graph, caps, conservative fit) and Keeper commits through
`accretion.world.WorldStore.append`, which re-runs that gate and then the pinned
x3d_mcp XSD + semantic validators (commit b5c9956) before a SQLite
compare-and-swap append to a hash chain. Nothing is re-implemented here: if
x3d.accrete is missing, admission is `not_run` and nothing enters the world.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

_CANDIDATES = [os.environ.get("ACCRETE_DIR"),
               str(Path(__file__).resolve().parents[3] / "x3d.accrete"),      # sibling checkout
               str(Path(__file__).resolve().parents[2] / "vendor" / "x3d.accrete")]


def locate() -> Path | None:
    for c in _CANDIDATES:
        if c and (Path(c) / "accretion" / "gate.py").is_file():
            return Path(c)
    return None


ROOT = locate()
if ROOT and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def available() -> bool:
    return ROOT is not None


def identity() -> dict:
    if not ROOT:
        return {"status": "not_run", "why": "x3d.accrete not found (set ACCRETE_DIR)"}
    from accretion import gate as g, mcp_adapter as m
    try:
        commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:  # noqa: BLE001
        commit = ""
    return {"status": "ok", "accrete_commit": commit or "unknown", "gate_version": g.VERSION,
            "x3d_mcp_commit": m.COMMIT[:7], "x3d_mcp_repo": m.REPOSITORY}


def gate(xml: str, prefix: str) -> dict:
    if not ROOT:
        return {"status": "not_run", "errors": [{"code": "ACCRETE_MISSING", "message": "x3d.accrete not found"}]}
    from accretion.gate import gate_fragment
    return gate_fragment(xml, prefix=prefix)


def prevalidate(canonical_fragment: str) -> dict:
    """The same pinned x3d_mcp XSD + semantic check Keeper's commit will run, on the same wrapped bytes."""
    if not ROOT:
        return {"status": "not_run"}
    from accretion.mcp_adapter import validate_scene
    from accretion.world import wrap_scene
    v = validate_scene(wrap_scene(canonical_fragment))
    errors = [{"code": f"MCP_{stage.upper()}_{f.get('check', 'error').upper().replace('-', '_')}", "message": f.get("message", "")}
              for stage in ("xsd", "semantic") for f in v.get(stage, {}).get("findings", []) if f.get("level", "error") == "error"]
    return {"status": v.get("status"), "xsd": v.get("xsd", {}).get("status"), "semantic": v.get("semantic", {}).get("status"),
            "errors": errors}


def procedural_candidate(plan: dict, tier: int = 3) -> dict:
    from accretion.generator import generate
    return generate(plan, tier)


class World:
    """One growing world per Gobbler.flyte install. Append-only; every row hash-chained."""

    def __init__(self, path: Path):
        if not ROOT:
            raise RuntimeError("x3d.accrete not found (set ACCRETE_DIR)")
        from accretion.world import WorldStore
        self.store = WorldStore(Path(path))

    def head(self) -> dict:
        s = self.store.snapshot()
        return {"head": s["head"], "tail_hash": s["tail_hash"]}

    def next_plan(self) -> dict:
        from accretion.world import plan_next
        s = self.store.snapshot()
        return plan_next(s["placements"], s["tail_hash"])

    def append(self, candidate: dict | None, tier: int = 3) -> dict:
        from accretion.world import AdmissionRefused
        s = self.store.snapshot()
        try:
            r = self.store.append(tier=tier, expected_head=s["head"], expected_tail_hash=s["tail_hash"], candidate=candidate)
        except AdmissionRefused as e:
            return {"status": "refused", "why": str(e), "stages": e.attempt.get("stages", [])}
        e = r["entry"]
        return {"status": "committed", "n": e["n"], "hash": e["hash"], "title": e.get("title"),
                "stages": [{"id": st["id"], "status": st["status"]} for st in r["attempt"]["stages"]],
                "plan": {k: e.get(k) for k in ("cell", "level", "mode", "biome", "era", "translation", "color")},
                "generator": e.get("generator")}

    def find_op(self, op: str) -> dict | None:
        """The committed entry whose generator carries this operation key, if any (crash/retry recovery)."""
        for e in reversed(self.store.archive()["entries"]):
            if (e.get("payload", {}).get("generation") or {}).get("op") == op:
                return {"status": "committed", "n": e["n"], "hash": e["hash"], "recovered": True,
                        "title": e["payload"].get("title"), "stages": [], "plan": e["payload"].get("plan"),
                        "generator": e["payload"].get("generation")}
        return None

    def export_x3d(self) -> str:
        return self.store.export_x3d()

    def verify(self) -> dict:
        return self.store.verify()

    def archive(self) -> dict:
        return self.store.archive()
