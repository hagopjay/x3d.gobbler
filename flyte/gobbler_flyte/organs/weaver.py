"""Weaver: signal -> a loom proposal (options + preferred pick) and an X3D candidate for the world.

Deterministic by default: a playbook maps the signal to an x3d.loom pipeline
action, and x3d.accrete's authored generator makes the world addition (zero
model calls). With a typed allowance, Haiku 5.5 writes the fragment instead and
the Witness gate referees it; refused attempts come back here with the gate's
error codes (the tight inner loop), and after the last attempt the procedural
path takes over so a turn is never lost to a bad fragment.
"""
from __future__ import annotations

import re

from .. import accrete_bridge as accrete
from ..llm import compile_prompt
from ..state import row

# (match, action, loom target, family, why a human may want a say)
PLAYBOOK = [
    (lambda s: s["source"] == "x_ite-releases", "rerun-xite-rig", "x3d.loom kit render rig + X_ITE pin", "beacon",
     "re-pin the renderer every receipt names"),
    (lambda s: s["source"] in ("threejs-releases", "babylon-releases"), "bridge-check", "x3d.loom x3d.threejs / Babylon bridge", "orrery",
     "bridge fixtures may shift"),
    (lambda s: s["source"] == "blender-x3d", "blenderizer-roundtrip", "x3d-blender-io roundtrip gate", "ziggurat",
     "exporter change touches every Blender scene"),
    (lambda s: s["source"] == "x3d_mcp-upstream", "validator-diff", "x3d_mcp fork vs upstream", "gyroscope",
     "validator pins move every number"),
    (lambda s: s["source"] == "loom-commits", "foldback-docs", "x3d.docs chapter + ledgers", "gyroscope",
     "a loom change not yet taught"),
    (lambda s: s["source"] == "web3d-news", "standards-note", "x3d.docs watch note + LOOM-v1 open questions", "coral",
     "Consortium news can change priorities"),
    (lambda s: s["source"].startswith("arxiv"), "atlas-reading-card", "Gobbler Atlas reading card", "mycelium",
     "papers need a human read"),
    (lambda s: s.get("label") == "adjacent", "adjacent-watch", "x3d.loom bridges map (adjacent tech)", "mycelium",
     "adjacent, not X3D itself"),
    (lambda s: True, "community-signal", "x3d.docs community log", "beacon", "open web signal"),
]

GATE_BRIEF = ("Write ONE small X3D 4.0 XML fragment (no <X3D> or <Scene> wrapper), at most 60 nodes. Allowed nodes only: Group, "
              "Transform, Shape, Appearance, Material, PhysicalMaterial, Box, Sphere, Cylinder, Cone, Coordinate, Color, IndexedFaceSet, "
              "IndexedLineSet, ElevationGrid, Extrusion, TimeSensor, PositionInterpolator, OrientationInterpolator, ColorInterpolator, "
              "ScalarInterpolator, DirectionalLight, PointLight, SpotLight, ROUTE. No Script, shaders, textures, URLs, Inline, Text, PROTO, "
              "Viewpoint or comments. Keep it within 3 m of the origin. ROUTEs only TimeSensor.fraction_changed -> interpolator.set_fraction "
              "-> Transform/material/light field. Reply with the XML only.")


def plan_for(signal: dict) -> tuple:
    for match, action, target, family, ask_reason in PLAYBOOK:
        if match(signal):
            return action, target, family, ask_reason
    raise AssertionError("playbook has a catch-all")


def propose(signal: dict, cycle: int) -> dict:
    action, target, family, ask_reason = plan_for(signal)
    title = signal["title"][:80]
    options = [
        {"id": "A", "label": f"{action} on {target}", "effect": "open a PR on the flyte branch with the change + a world addition"},
        {"id": "B", "label": "note only", "effect": "record the signal in the ledger and the world, no PR"},
        {"id": "C", "label": "skip", "effect": "ignore this signal; nothing enters the world"},
    ]
    ambiguous = signal["score"] < 0.7 or signal.get("synthetic", False)
    preferred = "B" if ambiguous else "A"
    outside = action == "validator-diff"           # upstream issue = a message outside the project: never automatic
    if outside:
        options[0] = {"id": "A", "label": "draft an upstream issue for Web3DConsortium/x3d_mcp",
                      "effect": "SEND OUTSIDE the family: needs your typed 'send'; never taken on timeout"}
        preferred = "B"
    return {"cycle": cycle, "action": action, "target": target, "family": family, "title": title, "signal_id": signal["id"],
            "options": options, "preferred": preferred, "reversible": not outside,
            "ask_human": action in ("rerun-xite-rig", "validator-diff", "blenderizer-roundtrip") or ambiguous,
            "ask_reason": ("the source is a SYNTHETIC fixture" if signal.get("synthetic") else f"score {signal['score']} is weak")
                          if ambiguous else ask_reason}


def _strip(text: str) -> str:
    m = re.search(r"```(?:xml)?\s*(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip()


def weaver(state: dict, ctx) -> dict:
    signal = state["signal"]
    attempts = state.get("attempts", 0) + 1
    proposal = state.get("proposal") or propose(signal, state["cycle"])
    plan = ctx.world.next_plan() if ctx.world else {"seed": "0" * 64, "n": 0}
    plan = {**plan, "seed_word": proposal["family"]}          # family follows the signal type
    story = f"Turn {state['cycle']}: {proposal['action']} - {signal['title'][:60]}"
    log, spend = [], []
    last = state.get("witness") or {}
    use_llm = ctx.mode in ('live', 'sim') and attempts < ctx.config["inner_loop"]["max_weave_attempts"]
    model_block_reason = None
    if signal.get("source") not in {s["id"] for s in ctx.config.get("sources", [])}:
        use_llm, model_block_reason = False, "unconfigured source: no model prompt"
    elif getattr(ctx, "mem", None) is None:
        use_llm, model_block_reason = False, "memory compiler unavailable: no model prompt"
    if model_block_reason:
        log.append(row("weaver", "prompt-blocked", model_block_reason))
    gate_check = None
    if use_llm:
        # All refusal feedback, including the immediately previous attempt,
        # must take the same lineage/ACL/exposure path as historical lessons.
        # Interpolating last.errors here bypassed a sealed refusal's exclusion.
        memory_ctx = None
        if getattr(ctx, "mem", None) is not None:
            from ..memory import Reader, compile_context
            diagnostics = {}  # operator-only exclusion details, never model input
            memory_ctx = compile_context(ctx.mem, Reader("weaver", ctx.now, {"world": ctx.world_id}),
                                         kinds=("counterexample", "procedure", "decision"), query=proposal["action"],
                                         max_bytes=2400, diagnostics=diagnostics)
            log.append(row("weaver", "context", f"memory context {memory_ctx['context_sha256'][:12]}: {len(memory_ctx['memories'])} in, "
                           f"{len(diagnostics['excluded'])} filtered out before ranking "
                           f"({', '.join(f'{k} {v}' for k, v in sorted(__import__('collections').Counter(diagnostics['excluded'].values()).items()))})",
                           context_sha256=memory_ctx["context_sha256"]))
        action, target, _, _ = plan_for(signal)  # trusted playbook strings, not free text from resumed state
        prompt = compile_prompt(GATE_BRIEF, memory_ctx, signal_title=signal["title"], action=action, target=target)
        gate_check = ctx.budget.check(len(GATE_BRIEF) + len(prompt), ctx.now, state["cycle"])
        log.append(row("gobbler", "budget", f"{'allow' if gate_check['allowed'] else 'deny'} Haiku call: est ${gate_check['estimate_usd']} ({gate_check['why']})",
                       **gate_check))
    if use_llm and gate_check["allowed"]:
        reply = ctx.llm().complete(GATE_BRIEF, prompt)
        spend.append(ctx.budget.record(now_utc=ctx.now, cycle=state["cycle"], organ="weaver", tokens_in=reply.tokens_in,
                                       tokens_out=reply.tokens_out, estimate_usd=gate_check["estimate_usd"],
                                       simulated=reply.simulated, request_id=reply.request_id))
        from ..memory import WeaverCandidate
        try:                                       # the contract: bounded, no extra fields, nothing the model may invent
            wc = WeaverCandidate(x3d=_strip(reply.text) or " ", title=story[:120], instruction=proposal["target"][:280])
            fragment = wc.x3d.strip()
        except Exception as e:
            fragment = ""
            log.append(row("weaver", "contract", f"attempt {attempts}: reply broke the candidate contract ({type(e).__name__})"))
        candidate = {"title": story[:120], "instruction": proposal["target"][:280], "x3d": fragment or "<!-- empty reply -->",
                     "generator": {"kind": "model", "id": ctx.config["llm"]["model"], "version": "flyte-0.1",
                                   "organ": "weaver", "attempt": attempts, "simulated": reply.simulated,
                                   "prompt_sha256": prompt.prompt_sha256,
                                   **({"context_sha256": memory_ctx["context_sha256"]} if memory_ctx else {})}}
        log.append(row("weaver", "weave", f"attempt {attempts}: Haiku wrote {len(candidate['x3d'])} bytes "
                       f"({reply.tokens_in} in / {reply.tokens_out} out, ${spend[-1]['actual_usd']}{' simulated' if reply.simulated else ''})"))
    else:
        if not accrete.available():
            return {"attempts": attempts, "proposal": proposal, "candidate": None,
                    "log": log + [row("weaver", "weave", "x3d.accrete missing: no candidate can be made")]}
        c = accrete.procedural_candidate(plan, tier=3)
        candidate = {**c, "title": story[:120], "instruction": f"{proposal['target']}. {c['instruction']}"[:280],
                     "generator": {**c["generator"], "organ": "weaver", "attempt": attempts, "path": "accrete-procedural"}}
        why = model_block_reason or ("offline mode, no model client" if ctx.mode == 'offline' else \
            "inner loop exhausted, procedural fallback" if attempts >= ctx.config["inner_loop"]["max_weave_attempts"] and last else "no model allowance")
        log.append(row("weaver", "weave", f"attempt {attempts}: accrete {c['generator']['family']} sculpture, {len(c['x3d'])} bytes, 0 model calls ({why})"))
    if attempts == 1:
        log.insert(0, row("weaver", "proposal", f"{proposal['action']} -> {proposal['target']}; options A/B/C, prefers {proposal['preferred']}"
                          + (f"; will ask: {proposal['ask_reason']}" if proposal["ask_human"] else ""), proposal=proposal))
    return {"attempts": attempts, "proposal": proposal, "candidate": candidate, "spend": spend, "log": log}
