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

from ..state import row

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
        entry = ctx.world.append(state["candidate"])
        if entry["status"] == "committed":
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
            f"- witness: grade {state['witness']['grade']}, gate {state['witness']['instrument'].get('gate_version')}, "
            f"x3d_mcp {state['witness']['instrument'].get('x3d_mcp_commit')}\n"
            f"- world: entry #{entry['n']} `{entry['hash'][:16]}`\n"
            f"- decided by: {decided.get('by', 'no question asked (preferred pick)')} via {decided.get('via', '-')}\n\n"
            f"Status: drafted, reuse pending. A flywheel turn is counted only when a second consumer takes this up.\n")
        log.append(row("keeper", "foldback", f"drafted {drafted.name} for {repo} ({'PR' if choice == 'A' else 'note'}); reuse pending"))
    turn = {"cycle": state["cycle"], "signal": signal["id"], "action": proposal["action"], "choice": choice,
            "admitted": bool(entry and entry.get("status") == "committed"), "drafted": bool(drafted), "reused": False,
            "entry_n": entry.get("n") if entry else None, "entry_hash": entry.get("hash") if entry else None,
            "grade": state["witness"].get("grade"), "attempts": state.get("attempts"),
            "decision": state.get("decision"), "spend_usd": round(sum(s["actual_usd"] for s in state.get("spend", [])), 6),
            "utc": ctx.now}
    with (ctx.state_dir / "turns.jsonl").open("a") as f:
        f.write(json.dumps(turn, sort_keys=True, default=str) + "\n")
    return {"entry": entry or {}, "turn": turn, "log": log}
