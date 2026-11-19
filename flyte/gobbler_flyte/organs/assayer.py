"""Assayer: the fifth organ, the loop's AI engineer. It tests the cycle against the AI Engineering Atlas's theses.

HagopJay asked for a "Chip Huyen AI Engineering agent" and supplied the AI Engineering Atlas (an agent-written
catalogue of Chip Huyen's AI Engineering and the aie-book repo) as its content. The Assayer is that agent's
first form: deterministic code, no model call, no spend. Every cycle, whatever path it took, passes through it
on the way to close. It runs one check per testable thesis, cites the thesis from the library by id, and stops
the line when a critical check fails.

    thesis  check            what it reads                                       on failure
    T1      score_tuple      the turn row: instrument pins, mode, attempts, utc   warn
    T2      canary           once per UTC day: known-bad and known-good fragments  STOP
                             through the same gate and pinned validator
    T3      state_of_record  the world store, by this cycle's operation key        STOP
    T6      pin_age          days since the instrument pins were last audited     warn
    T7      egress           the signal's source id against the configured list    STOP
    T8      grader_opacity   the context journal: no held-out record ever sent     STOP
    T10     provenance       grade capped at Likely; source bytes hashed           warn
    T11     context_budget   tokens and dollars per step against the caps          warn
    T13     retry_cap        attempts never pass the inner-loop limit              STOP
    T12     stop_the_line    any STOP above writes STOP-THE-LINE.json; the runner starts nothing until a human clears it

T4 (reliability is a distribution) is measured over the day by assay_day(). T5 (judge validity) and T9 (swarms)
have no subject in this loop yet; the library says so instead of passing them.
"""
from __future__ import annotations

from datetime import datetime
import json
from math import comb

from .. import accrete_bridge as accrete
from ..state import row

STOP_FILE = "STOP-THE-LINE.json"

# The canary set: the instruments must refuse what they refused before, and pass what they passed. Copies, not
# imports from sim.py, so a change to the sim's script cannot quietly change the canary.
CANARY = [
    ("nested-animation", '<Group><Transform DEF="Spin"><Shape><Box size="1 1 1"/></Shape></Transform>'
     '<TimeSensor DEF="T" cycleInterval="4" loop="true"/>'
     '<OrientationInterpolator DEF="R" key="0 1" keyValue="0 1 0 0 0 1 0 3.1416"/>'
     '<ROUTE fromNode="T" fromField="fraction_changed" toNode="R" toField="set_fraction"/>'
     '<ROUTE fromNode="R" fromField="value_changed" toNode="Spin" toField="set_rotation"/></Group>', "fail"),
    ("remote-texture", '<Group><Shape><Appearance><ImageTexture url="https://example.com/t.png"/></Appearance>'
     '<Box size="1 1 1"/></Shape></Group>', "fail"),
    ("physical-material-immersive", '<Transform><Shape><Appearance><PhysicalMaterial baseColor="0.3 0.8 0.9" metallic="0.8" '
     'roughness="0.25"/></Appearance><Sphere radius="0.35"/></Shape></Transform>', "fail"),
    ("plain-sphere", '<Transform><Shape><Appearance><Material diffuseColor="0.3 0.8 0.9"/></Appearance><Sphere radius="0.35"/>'
     '</Shape></Transform>', "pass"),
]


def _check(name: str, thesis: str, status: str, severity: str, detail: str) -> dict:
    return {"check": name, "thesis": thesis, "status": status, "severity": severity, "detail": detail[:240]}


def _days(a: str, b: str) -> float:
    f = "%Y-%m-%dT%H:%M:%SZ"
    return (datetime.strptime(b, f) - datetime.strptime(a, f)).total_seconds() / 86400


def run_canary() -> dict:
    """The same two instruments Witness uses, on fixed bytes. Returns per-fragment outcomes."""
    out = []
    for name, x3d, want in CANARY:
        g = accrete.gate(x3d, prefix="CANARY")
        got = "pass" if g["status"] == "pass" else "fail"
        stage, errors = "gate", g.get("errors", [])
        if got == "pass":
            v = accrete.prevalidate(g["canonical_x3d"])
            if v["status"] != "pass":
                got, stage, errors = "fail", "x3d_mcp", v.get("errors") or [{"code": "MCP_FAIL"}]
        if g["status"] == "not_run":
            got = "not_run"
        out.append({"fragment": name, "want": want, "got": got, "stage": stage,
                    "codes": sorted({e["code"] for e in errors})[:4]})
    return {"fragments": out, "held": all(o["got"] == o["want"] for o in out),
            "not_run": any(o["got"] == "not_run" for o in out)}


def assay_cycle(state: dict, ctx) -> list[dict]:
    cfg = ctx.config.get("assay", {})
    turn, w, sig = state.get("turn") or {}, state.get("witness") or {}, state.get("signal")
    checks = []

    # T1: a score is a tuple. An admitted or refused turn must carry the instrument identity and the run's coordinates.
    if turn:
        inst = w.get("instrument") or {}
        missing = [k for k in ("gate_version", "x3d_mcp_commit", "accrete_commit") if not inst.get(k)]
        missing += [k for k in ("mode", "utc", "attempts", "grade") if turn.get(k) in (None, "")]
        if any(s.get("model") in (None, "") for s in state.get("spend", [])):
            missing.append("model")
        checks.append(_check("score_tuple", "T1", "fail" if missing else "pass", "warn",
                             f"missing {', '.join(missing)}" if missing else
                             f"gate {inst['gate_version']}, x3d_mcp {inst['x3d_mcp_commit']}, accrete {inst['accrete_commit']}, {turn['mode']}, {turn['utc']}"))

    # T3: grade state, not narrative. What Keeper says it admitted must be what the world store holds.
    if turn and ctx.world is not None:
        op = f"{ctx.world_id}:cycle-{state['cycle']}"
        held = ctx.world.find_op(op)
        if turn.get("admitted"):
            ok = bool(held) and held["hash"] == turn.get("entry_hash")
            detail = f"world holds {op} as #{held['n']} {held['hash'][:12]}" if ok else f"turn says admitted, world {'disagrees' if held else 'has no entry for ' + op}"
        else:
            ok = held is None
            detail = "nothing admitted, and the world holds nothing for this cycle" if ok else f"turn says not admitted, but the world holds #{held['n']}"
        checks.append(_check("state_of_record", "T3", "pass" if ok else "fail", "stop", detail))

    # T2: graders are software with bugs. Once per UTC day, the instruments must still refuse known failures.
    day = ctx.now[:10]
    seen = ctx.memory.setdefault("assay", {})
    if seen.get("canary_day") != day:
        c = run_canary()
        seen["canary_day"] = day
        seen["canary"] = c
        if c["not_run"]:
            checks.append(_check("canary", "T2", "not_run", "warn", "x3d.accrete missing: canary not run"))
        else:
            bad = [f"{o['fragment']} want {o['want']} got {o['got']}" for o in c["fragments"] if o["got"] != o["want"]]
            checks.append(_check("canary", "T2", "fail" if bad else "pass", "stop",
                                 "; ".join(bad) if bad else f"{len(c['fragments'])}/{len(c['fragments'])} held: "
                                 + ", ".join(f"{o['fragment']}={o['got']}({o['stage']})" for o in c["fragments"])))

    # T6: benchmarks (and instruments) have half-lives. Pins must have been re-audited recently.
    audited = cfg.get("pins_audited_utc")
    if audited:
        age = _days(audited, ctx.now)
        limit = cfg.get("pin_max_age_days", 30)
        checks.append(_check("pin_age", "T6", "fail" if age > limit else "pass", "warn",
                             f"instrument pins audited {audited[:10]}, {age:.1f} days ago (limit {limit})"))

    # T7: the sandbox is part of the system. Work may come only from a configured source.
    if sig:
        # What is checked is where Scout fetched from, not the link an item points at (that is data, never fetched).
        src = next((s for s in ctx.config["sources"] if s["id"] == sig.get("source")), None)
        fetched = (src or {}).get("url") or (f"https://api.github.com/repos/{src['repo']}/releases" if src and src.get("repo") else "")
        ok = bool(src) and fetched.startswith("https://")
        checks.append(_check("egress", "T7", "pass" if ok else "fail", "stop",
                             f"fetched from configured source {src['id']} over https" if ok
                             else f"source {sig.get('source')!r} is not a configured https source"))

    # T8: agents optimize the grader they imagine. Weaver sees refusal codes, never a held-out record.
    if getattr(ctx, "mem", None) is not None:
        from ..memory import audit_contamination
        a = audit_contamination(ctx.mem)
        checks.append(_check("grader_opacity", "T8", "fail" if a["leaks"] else "pass", "stop",
                             f"{a['contexts']} contexts journaled, {a['held_out']} held out, {len(a['leaks'])} leak(s)"))

    # T10: evidence needs provenance. No turn claims more than Likely, and archived sources carry their bytes' hash.
    if turn:
        prov = turn.get("source_provenance") or {}
        bad = []
        if turn.get("grade") == "Confirmed":
            bad.append("grade Confirmed exceeds the Likely cap")
        if prov.get("transport") in ("fixture", "http") and not prov.get("body_sha256"):
            bad.append("source bytes not hashed")
        checks.append(_check("provenance", "T10", "fail" if bad else "pass", "warn",
                             "; ".join(bad) if bad else f"grade {turn.get('grade')}, source {prov.get('transport', 'n/a')} sha {str(prov.get('body_sha256', '-'))[:12]}"))

    # T11: context is a budget. Tokens and dollars per step stay under their caps.
    spend = state.get("spend", [])
    if spend:
        cap = ctx.config["llm"]["per_cycle_cap_usd"]
        tok_cap = cfg.get("max_tokens_in_per_call", 6000)
        usd = round(sum(s["actual_usd"] for s in spend), 6)
        worst = max(s["tokens_in"] for s in spend)
        ok = usd <= cap and worst <= tok_cap
        checks.append(_check("context_budget", "T11", "pass" if ok else "fail", "warn",
                             f"{len(spend)} call(s), max {worst} tokens in (cap {tok_cap}), ${usd} (cap ${cap})"))

    # T13: misbehavior is trained in. An impossible task must not earn unlimited retries.
    if state.get("attempts") is not None and sig:
        lim = ctx.config["inner_loop"]["max_weave_attempts"]
        checks.append(_check("retry_cap", "T13", "pass" if state["attempts"] <= lim else "fail", "stop",
                             f"{state['attempts']} attempt(s), limit {lim}"))
    return checks


def assayer(state: dict, ctx) -> dict:
    checks = assay_cycle(state, ctx)
    lib = getattr(ctx, "library", None)
    cited = []
    for c in checks:
        rec = lib.get(f"aie:{c['thesis']}") if lib is not None else None
        c["library"] = rec.memory_id if rec else None
        if rec:
            cited.append(rec.memory_id)
    stops = [c for c in checks if c["status"] == "fail" and c["severity"] == "stop"]
    warns = [c for c in checks if c["status"] == "fail" and c["severity"] == "warn"]
    log = []
    for c in checks:
        if c["status"] != "pass" or c["check"] in ("canary", "state_of_record"):
            log.append(row("assayer", c["check"], f"{c['thesis']} {c['check']}: {c['status'].upper()} ({c['detail']})", check=c))
    summary = (f"{sum(c['status'] == 'pass' for c in checks)}/{len(checks)} thesis checks pass"
               + (f", {len(warns)} warning(s)" if warns else "") + (f", STOP: {', '.join(c['check'] for c in stops)}" if stops else "")
               + f"; cites {', '.join(sorted(set(cited))) or 'no library'}")
    log.append(row("assayer", "assay", summary, checks=[{k: c[k] for k in ("check", "thesis", "status")} for c in checks]))
    if stops:
        stop = {"schema": "gobbler.stop-the-line/1", "utc": ctx.now, "cycle": state["cycle"],
                "failed": [{k: c[k] for k in ("check", "thesis", "detail", "library")} for c in stops],
                "clear": "A human reads the failure, fixes or accepts it, then deletes this file. No tick starts work while it exists."}
        (ctx.state_dir / STOP_FILE).write_text(json.dumps(stop, indent=1, sort_keys=True))
        log.append(row("assayer", "stop_the_line", f"T12 stop the line: wrote {STOP_FILE}; the next tick starts nothing until a human clears it"))
    return {"assay": {"checks": checks, "stops": len(stops), "warnings": len(warns)}, "log": log}


# --- the day (T4) -------------------------------------------------------------------------------------------------

def pass_at_k(n: int, c: int, k: int) -> float:
    """Atlas code sketch K5 (unbiased pass@k from n trials, c successes)."""
    return 1.0 if n - c < k else 1 - comb(n - c, k) / comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    """Atlas code sketch K5 (pass^k: the chance that all k draws succeed)."""
    return comb(c, k) / comb(n, k) if n >= k else 0.0


def assay_day(tape: list[dict], turns: list[dict]) -> dict:
    """Reliability as a distribution, read from the tape and the ledger, not from any organ's own summary."""
    verdicts = [r for r in tape if r.get("node") == "witness" and r.get("kind") == "verdict"]
    n = len(verdicts)
    c = sum(1 for r in verdicts if " PASS " in f" {r['text']} ")
    codes: dict[str, int] = {}
    for r in verdicts:
        for e in (r.get("data") or {}).get("errors", []):
            codes[e["code"]] = codes.get(e["code"], 0) + 1
    attempts: dict[int, int] = {}
    for t in turns:
        attempts[t.get("attempts") or 0] = attempts.get(t.get("attempts") or 0, 0) + 1
    first = sum(1 for t in turns if t.get("admitted") and t.get("attempts") == 1)
    assays = [r for r in tape if r.get("node") == "assayer" and r.get("kind") == "assay"]
    by_check: dict[str, dict[str, int]] = {}
    for r in assays:
        for ch in (r.get("data") or {}).get("checks", []):
            by_check.setdefault(f"{ch['thesis']} {ch['check']}", {}).setdefault(ch["status"], 0)
            by_check[f"{ch['thesis']} {ch['check']}"][ch["status"]] += 1
    return {"schema": "gobbler.assay-day/1",
            "attempts": {"n": n, "witness_pass": c, "pass_at_1": round(pass_at_k(n, c, 1), 4) if n else None,
                         "pass_hat_3": round(pass_hat_k(n, c, 3), 4) if n >= 3 else None,
                         "note": "pooled over attempts on different tasks: a reliability profile of the loop, not K5's per-task estimate"},
            "turns": {"n": len(turns), "admitted": sum(bool(t.get("admitted")) for t in turns),
                      "admitted_first_attempt": first, "attempts_histogram": dict(sorted(attempts.items()))},
            "refusal_codes": dict(sorted(codes.items(), key=lambda kv: -kv[1])),
            "most_frequent_refusal": sorted(codes, key=lambda c: (-codes[c], c))[0] if codes else None,
            "assayed_cycles": len(assays), "checks": dict(sorted(by_check.items())),
            "stops": sum(1 for r in tape if r.get("node") == "assayer" and r.get("kind") == "stop_the_line")}
