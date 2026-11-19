"""Witness: the referee. It never writes the world; it says pass or fail, and names its instrument.

Pre-check = x3d.accrete gate_fragment on the exact candidate bytes. Keeper's
commit re-runs the gate and then the pinned x3d_mcp XSD + semantic validators,
so a Witness pass is necessary but never sufficient. Grades follow the project
rule: Confirmed / Likely / Suspected.
"""
from __future__ import annotations

from pathlib import Path

from .. import accrete_bridge as accrete
from ..loom import traps
from ..state import row


def grade(signal: dict, gate_ok: bool, target_seen: bool | None) -> str:
    if not gate_ok:
        return "Refused"
    if signal.get("synthetic"):
        return "Suspected"
    # A path's existence confirms only that the path exists. The candidate's
    # structural checks do not establish source truth, target behavior or reuse.
    return "Likely"


def _remember_refusal(ctx, state: dict, cand: dict, errors: list[dict]) -> None:
    """A refusal is a counterexample: executed instrument (grade C), bound to the exact fragment bytes.
    About one in five is sealed by its bytes and never reaches Weaver; the rest teach the next attempt."""
    import hashlib
    from ..memory import EvidenceRef, MemoryRecord, seal_bucket
    sha = hashlib.sha256(cand["x3d"].encode("utf-8")).hexdigest()
    exposure = seal_bucket(sha)
    codes = sorted({e["code"] for e in errors}) or ["UNSPECIFIED"]
    eid = f"witness:{sha[:24]}"
    ctx.mem.put_evidence(EvidenceRef(evidence_id=eid, exposure=exposure, sha256=sha,
                                     instrument=f"accrete gate {accrete.identity().get('gate_version')} + x3d_mcp + loom traps"))
    first = errors[0]["message"][:160] if errors else ""
    ctx.mem.put_once(MemoryRecord(memory_id=f"cx:{sha[:24]}", kind="counterexample", readers=["weaver"],
                             text=f"Refused {', '.join(codes)}: {first}", evidence_ids=[eid], exposures=[exposure],
                             evidence_level="C", valid_from=ctx.now, recorded_by="witness",
                             scope={"world": ctx.world_id}, cycle=state["cycle"], subject_sha256=sha))


def target_seen(ctx, proposal: dict) -> bool | None:
    """Does the loom pipeline the proposal names exist in a local x3d.loom checkout? None = not checked."""
    loom = ctx.loom_dir
    if not loom or not Path(loom).is_dir():
        return None
    probes = {"rerun-xite-rig": ["kit"], "bridge-check": ["x3d.threejs"], "blenderizer-roundtrip": ["LEARNINGS-blender-scivis.md"],
              "validator-diff": ["LOOM-v1.md"], "foldback-docs": ["LOOM-v1.md"], "standards-note": ["LOOM-v1.md"],
              "atlas-reading-card": ["SOURCES.md"], "adjacent-watch": ["x3d.webgpu"], "community-signal": ["README.md"]}
    return all((Path(loom) / p).exists() for p in probes.get(proposal["action"], ["README.md"]))


def witness(state: dict, ctx) -> dict:
    cand, proposal, signal = state.get("candidate"), state["proposal"], state["signal"]
    if not cand:
        return {"witness": {"status": "fail", "errors": [{"code": "NO_CANDIDATE", "message": "Weaver made nothing"}]},
                "log": [row("witness", "verdict", "nothing to witness")]}
    g = accrete.gate(cand["x3d"], prefix=f"W{state['cycle']:05d}")
    ok = g["status"] == "pass"
    v = accrete.prevalidate(g["canonical_x3d"]) if ok else {"status": "not_run"}
    if ok and v["status"] != "pass":
        ok = False
        g = {**g, "errors": v["errors"] or [{"code": "MCP_FAIL", "message": "pinned validator did not pass"}]}
    trap_hits = []
    if ok:
        from accretion.world import wrap_scene
        trap_hits = traps.check(wrap_scene(g["canonical_x3d"]).encode())
        if any(h.severity == "error" for h in trap_hits):
            ok = False
            g = {**g, "errors": [{"code": "TRAP_" + h.rule.upper().replace("-", "_"), "message": h.detail} for h in trap_hits if h.severity == "error"]}
    seen = target_seen(ctx, proposal)
    if not ok and getattr(ctx, "mem", None) is not None:
        _remember_refusal(ctx, state, cand, g.get("errors", []))
    verdict = {"status": "pass" if ok else "fail", "errors": g.get("errors", [])[:6], "grade": grade(signal, ok, seen),
               "evidence_facets": {"candidate_structure": "pass" if ok else "fail",
                   "source": "synthetic" if signal.get('synthetic') else "archived" if signal.get('provenance', {}).get('transport') == 'fixture' else "unverified_live",
                   "target_presence": "not_run" if seen is None else "present" if seen else "missing", "reuse": "unverified"},
               "instrument": accrete.identity(), "metrics": g.get("metrics"), "target_seen": seen,
               "canonical_sha256": g.get("canonical_sha256"), "validator": {k: v.get(k) for k in ("status", "xsd", "semantic")},
               "traps": [{"rule": h.rule, "severity": h.severity, "where": h.where} for h in trap_hits]}
    if ok:
        m = g.get("metrics", {})
        text = (f"gate {verdict['instrument'].get('gate_version')} PASS + x3d_mcp {verdict['instrument'].get('x3d_mcp_commit')} "
                f"XSD {v.get('xsd')} / semantic {v.get('semantic')} ({m.get('nodes', '?')} nodes, "
                f"{m.get('expanded_shapes', m.get('shapes', '?'))} shapes) + loom traps {len(trap_hits)} warning(s); grade {verdict['grade']}; loom target "
                f"{'found' if seen else 'not checked' if seen is None else 'MISSING'}")
    else:
        codes = ", ".join(sorted({e['code'] for e in verdict['errors']}))
        stage = "x3d_mcp" if v.get("status") not in (None, "not_run") else "gate"
        text = f"{stage} REFUSED attempt {state.get('attempts')}: {codes}" + (f" ({verdict['errors'][0]['message'][:110]})" if stage == "x3d_mcp" else "")
    return {"witness": verdict, "log": [row("witness", "verdict", text, errors=verdict["errors"][:3])]}
