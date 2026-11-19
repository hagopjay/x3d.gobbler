"""Keeper: commits the turn to the world, writes the ledger, drafts the foldback, counts honestly.

Three counters, never merged (the Atlas rule: a flywheel turn is an
evidence-bound improvement reused by a second consumer):
  admitted   - an entry passed gate + XSD + semantic and joined the hash chain
  drafted    - a foldback note for x3d.loom / x3d.docs sits in the outbox
  reused     - a second consumer took it up (a merged PR); only a later tick can confirm
"""
from __future__ import annotations

import json
from pathlib import Path

from ..state import append_jsonl_once, read_jsonl, row

FOLDBACK = {
    "rerun-xite-rig": ("x3d.loom", "LEARNINGS-gobbler.md"),
    "bridge-check": ("x3d.loom", "x3d.threejs/README.md"),
    "blenderizer-roundtrip": ("x3d.loom", "LEARNINGS-blender-scivis.md"),
    "validator-diff": ("x3d.loom", "LOOM-v1.md"),
    "foldback-docs": ("x3d.docs", "docs/"),
    "standards-note": ("x3d.docs", "docs/"),
    "atlas-reading-card": ("x3d.gobbler", "flywheel-review/atlas/"),
    "adjacent-watch": ("x3d.loom", "SOURCES.md"),
    "community-signal": ("x3d.docs", "docs/"),
}


def keeper(state: dict, ctx) -> dict:
    proposal, signal = state["proposal"], state["signal"]
    choice = (state.get("decision") or {}).get("choice") or proposal["preferred"]
    log = []
    entry = None
    if choice == "C":
        log.append(row("keeper", "skip", f"option C chosen ({(state.get('decision') or {}).get('by', 'preferred')}): nothing enters the world"))
    elif ctx.world is None:
        log.append(row("keeper", "world", "x3d.accrete missing: admission not_run, nothing committed"))
    else:
        # One operation key per cycle. A tick that crashed after the world append but before its memory was
        # saved re-runs the same cycle number; the key finds the entry it already admitted instead of a duplicate.
        op = f"{ctx.world_id}:cycle-{state['cycle']}"
        entry = ctx.world.find_op(op)
        if entry:
            log.append(row("keeper", "recovered", f"world entry #{entry['n']} {entry['hash'][:12]} already holds operation {op}; not appended again"))
        else:
            cand = {**state["candidate"], "generator": {**state["candidate"]["generator"], "op": op}}
            entry = ctx.world.append(cand)
        if entry.get("recovered"):
            pass
        elif entry["status"] == "committed":
            stages = " ".join(f"{s['id']}:{s['status']}" for s in entry["stages"])
            log.append(row("keeper", "commit", f"world entry #{entry['n']} {entry['hash'][:12]} committed ({stages})",
                           entry=entry))
        else:
            log.append(row("keeper", "refused", f"world refused at commit: {entry['why'][:120]}", stages=entry["stages"]))
    drafted = None
    if choice in ("A", "B") and entry and entry.get("status") == "committed":
        repo, path = FOLDBACK.get(proposal["action"], ("x3d.docs", "docs/"))
        drafted = ctx.outbox / f"{state['cycle']:05d}-{proposal['action']}.md"
        drafted.parent.mkdir(parents=True, exist_ok=True)
        decided = state.get("decision") or {}
        drafted.write_text(
            f"# Foldback draft, cycle {state['cycle']}\n\n"
            f"- target: `{repo}` `{path}`\n- action: {proposal['action']} ({'PR' if choice == 'A' else 'note only'})\n"
            f"- signal: [{signal['title']}]({signal['url']}) from `{signal['source']}`"
            f"{' (SYNTHETIC fixture)' if signal.get('synthetic') else ''}, score {signal['score']} ({'; '.join(signal['why'])})\n"
            f"- observation: run mode `{ctx.mode}`, source transport `{signal.get('provenance', {}).get('transport', 'unrecorded')}`, "
            f"body SHA-256 `{signal.get('provenance', {}).get('body_sha256', 'unrecorded')}`\n"
            f"- witness: grade {state['witness']['grade']}, gate {state['witness']['instrument'].get('gate_version')}, "
            f"x3d_mcp {state['witness']['instrument'].get('x3d_mcp_commit')}\n"
            f"- world: entry #{entry['n']} `{entry['hash'][:16]}`\n"
            f"- decided by: {decided.get('by', 'no question asked (preferred pick)')} via {decided.get('via', '-')}\n\n"
            f"Status: drafted, reuse pending. A flywheel turn is counted only when a second consumer takes this up.\n")
        log.append(row("keeper", "foldback", f"drafted {drafted.name} for {repo} ({'PR' if choice == 'A' else 'note'}); reuse pending"))
    turn = {"cycle": state["cycle"], "signal": signal["id"], "action": proposal["action"], "choice": choice,
            "mode": ctx.mode, "source_provenance": signal.get('provenance'), "synthetic": bool(signal.get('synthetic')),
            "evidence_facets": {**(state['witness'].get('evidence_facets') or {}),
                                "admission": "committed" if entry and entry.get("status") == "committed" else "not_admitted",
                                "human": {"hagopjay": "answered"}.get((state.get("decision") or {}).get("by"),
                                          "timeout_preferred_pick" if (state.get("decision") or {}).get("by") == "timeout"
                                          else "answered" if state.get("decision") else "not_asked"),
                                "render": "not_run"},
            "admitted": bool(entry and entry.get("status") == "committed"), "drafted": bool(drafted), "reused": False,
            "entry_n": entry.get("n") if entry else None, "entry_hash": entry.get("hash") if entry else None,
            "grade": state["witness"].get("grade"), "attempts": state.get("attempts"),
            "decision": state.get("decision"), "spend_usd": round(sum(s["actual_usd"] for s in state.get("spend", [])), 6),
            "utc": ctx.now}
    if getattr(ctx, "mem", None) is not None:
        from ..memory import MemoryRecord
        scope = {"world": ctx.world_id}
        dec = state.get("decision") or {}
        if dec.get("by") and dec["by"] not in ("timeout",):
            ctx.mem.put_once(MemoryRecord(memory_id=f"decision:cycle-{state['cycle']}", kind="decision", readers=["weaver", "gobbler"],
                                     text=f"{dec['by']} picked {dec.get('choice')} for {proposal['action']} on {proposal['target']}"[:400],
                                     evidence_level="C", valid_from=ctx.now, recorded_by="human", scope=scope, cycle=state["cycle"]))
        if entry and entry.get("status") == "committed":
            import hashlib
            twins = [m.memory_id for m in ctx.mem.by_cycle(state["cycle"], "counterexample")]   # refused earlier this cycle
            ctx.mem.put_once(MemoryRecord(memory_id=f"episode:{entry['hash'][:24]}", kind="episode", readers=["weaver", "gobbler"],
                                     text=f"Admitted entry #{entry['n']} ({proposal['action']}, attempt {state.get('attempts')})"
                                          + (f" after {len(twins)} refused fragment(s): the lawful twin of each" if twins else ""),
                                     evidence_level="C", valid_from=ctx.now, recorded_by="keeper", scope=scope,
                                     parent_ids=twins, cycle=state["cycle"],
                                     subject_sha256=hashlib.sha256(state["candidate"]["x3d"].encode("utf-8")).hexdigest()))
    turns = ctx.state_dir / "turns.jsonl"
    done = {item["cycle"]: item for item in read_jsonl(turns)}
    if state["cycle"] in done:                       # the same cycle re-run after a crash: one ledger row per cycle
        saved = done[state["cycle"]]
        if any(saved.get(key) != turn.get(key) for key in ("signal", "action", "choice", "entry_hash", "admitted")):
            raise RuntimeError("cycle operation conflicts with its committed turn ledger")
        turn = saved
        log.append(row("keeper", "recovered", f"turn row for cycle {state['cycle']} already written; not duplicated"))
    else:
        turn = append_jsonl_once(turns, turn, "cycle")
    return {"entry": entry or {}, "turn": turn, "log": log}
