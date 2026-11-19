"""Assayer: the fifth organ, the loop's AI engineer. It tests the cycle against the AI Engineering Atlas's theses.

HagopJay asked for a "Chip Huyen AI Engineering agent" and supplied the AI Engineering Atlas (an agent-written
catalogue of Chip Huyen's AI Engineering and the aie-book repo) as its content. The Assayer is that agent's
first form: deterministic code, no model call, no spend. Every cycle, whatever path it took, passes through it
on the way to close. It runs one check per testable thesis, cites the thesis from the library by id, and stops
the line when a critical check fails.

    thesis  check            what it reads                                       on failure
    T1      score_tuple      the turn row: instrument pins, mode, attempts, utc   warn
    T2      canary           daily per instrument/case identity: known controls   STOP
                             through gate, pinned validator and trap stage
    T3      state_of_record  the world store, by this cycle's operation key        STOP
    T6      pin_age          days since the instrument pins were last audited     warn
    T7      egress           every configured source and Scout fetch receipt       STOP
    T8      grader_opacity   contamination proxy; grader gaming remains untested    STOP
    T10     provenance       grade capped at Likely; source bytes hashed           warn
    T11     context_budget   tokens and dollars per step against the caps          warn
    T13     retry_cap        attempts never pass the inner-loop limit              STOP
    T12     stop_the_line    any STOP above writes STOP-THE-LINE.json; the runner starts nothing until a human clears it

T4 (reliability is a distribution) is measured over the day by assay_day(). T5 (judge validity) and T9 (swarms)
have no subject in this loop yet; the library says so instead of passing them.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
from math import comb
from pathlib import Path
from urllib.parse import urlsplit

from .. import accrete_bridge as accrete
from ..loom import traps
from ..sources import fetch_url
from ..state import row

STOP_FILE = "STOP-THE-LINE.json"
_TRAPS_SHA_AT_IMPORT = hashlib.sha256(Path(traps.__file__).read_bytes()).hexdigest()

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
    # A warning is admitted by Witness, but its presence proves that the trap stage ran.
    ("white-emissive-warning", '<Shape><Appearance><Material diffuseColor="1 0 0" emissiveColor="1 1 1"/>'
     '</Appearance><Sphere radius="0.35"/></Shape>', "pass"),
]
CANARY_EXPECTED = {
    "nested-animation": ("gate", ["GATE_CONTAINMENT"], []),
    "remote-texture": ("gate", ["GATE_NODE_FORBIDDEN"], []),
    "physical-material-immersive": ("x3d_mcp", ["MCP_SEMANTIC_PROFILE_COMPONENT"], []),
    "plain-sphere": ("loom_traps", [], []),
    "white-emissive-warning": ("loom_traps", [], ["color-emissive-white"]),
}
# The fragment gate already rejects out-of-range colours before traps can see them. An isolated error control
# therefore checks this otherwise masked part of the trap instrument; it is not claimed as a pipeline admission.
TRAP_CANARY = [
    ("color-range-error", '<Shape><Appearance><Material diffuseColor="1.2 0.2 0.2"/></Appearance><Sphere/></Shape>',
     [("color-range", "error")]),
    ("color-range-lawful-twin", '<Shape><Appearance><Material diffuseColor="0.9 0.2 0.2"/></Appearance><Sphere/></Shape>', []),
]


def _check(name: str, thesis: str, status: str, severity: str, detail: str) -> dict:
    return {"check": name, "thesis": thesis, "status": status, "severity": severity, "detail": detail[:240]}


def _days(a: str, b: str) -> float:
    f = "%Y-%m-%dT%H:%M:%SZ"
    return (datetime.strptime(b, f) - datetime.strptime(a, f)).total_seconds() / 86400


def run_canary() -> dict:
    """Run gate, pinned validator and traps, including a trap-stage positive control."""
    out = []
    for name, x3d, want in CANARY:
        g = accrete.gate(x3d, prefix="CANARY")
        got = "pass" if g["status"] == "pass" else "fail"
        stage, errors, trap_rules = "gate", g.get("errors", []), []
        if got == "pass":
            v = accrete.prevalidate(g["canonical_x3d"])
            stage = "x3d_mcp"
            if v["status"] != "pass":
                got, stage, errors = "fail", "x3d_mcp", v.get("errors") or [{"code": "MCP_FAIL"}]
            else:
                from accretion.world import wrap_scene
                stage = "loom_traps"
                hits = traps.check(wrap_scene(g["canonical_x3d"]).encode())
                trap_rules = sorted({h.rule for h in hits})
                errors = [{"code": "TRAP_" + h.rule.upper().replace("-", "_")} for h in hits if h.severity == "error"]
                if errors:
                    got = "fail"
        if g["status"] == "not_run":
            got = "not_run"
        codes = sorted({e["code"] for e in errors})[:4]
        expected = CANARY_EXPECTED.get(name)
        matches = got == want and (expected is None or (stage, codes, trap_rules) == expected)
        out.append({"fragment": name, "want": want, "got": got, "stage": stage,
                    "codes": codes, "trap_rules": trap_rules, "matches": matches})
    controls = []
    if accrete.available():
        from accretion.world import wrap_scene
        for name, fragment, expected in TRAP_CANARY:
            got = sorted({(h.rule, h.severity) for h in traps.check(wrap_scene(fragment).encode())})
            controls.append({"control": name, "want": expected, "got": got, "matches": got == expected,
                             "scope": "isolated trap instrument, not full pipeline admission"})
    return {"fragments": out, "trap_controls": controls,
            "held": all(o["matches"] for o in out) and all(o["matches"] for o in controls),
            "not_run": any(o["got"] == "not_run" for o in out)}


def _canary_key() -> str:
    """Bind daily reuse to the actual loaded instruments and canary definition."""
    identity = {"bridge": accrete.identity(), "traps_sha256": _TRAPS_SHA_AT_IMPORT}
    if hashlib.sha256(Path(traps.__file__).read_bytes()).hexdigest() != _TRAPS_SHA_AT_IMPORT:
        raise RuntimeError("loom trap source changed after import; restart before re-audit")
    if accrete.available():
        from accretion import gate, mcp_adapter
        gate_sha = hashlib.sha256(Path(gate.__file__).read_bytes()).hexdigest()
        if gate_sha != gate._IMPORTED_CODE_SHA256:
            raise RuntimeError("accrete gate source changed after import; restart before re-audit")
        identity["gate_sha256"] = gate_sha
        identity["validator"] = mcp_adapter.instrument_identity()["code_sha256"]
    payload = {"instruments": identity, "canary": CANARY, "expected": CANARY_EXPECTED, "isolated_trap_controls": TRAP_CANARY}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


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
    if ctx.world is not None:
        op = f"{ctx.world_id}:cycle-{state['cycle']}"
        held = ctx.world.find_op(op)
        if turn.get("admitted"):
            ok = bool(held) and held["hash"] == turn.get("entry_hash")
            detail = f"world holds {op} as #{held['n']} {held['hash'][:12]}" if ok else f"turn says admitted, world {'disagrees' if held else 'has no entry for ' + op}"
        else:
            ok = held is None
            detail = "nothing admitted, and the world holds nothing for this cycle" if ok else f"no admitted turn, but the world holds #{held['n']}"
        checks.append(_check("state_of_record", "T3", "pass" if ok else "fail", "stop", detail))

    # T2: a successful daily audit is reusable only for these instrument and canary bytes.
    day = ctx.now[:10]
    seen = ctx.memory.setdefault("assay", {})
    try:
        canary_key = _canary_key()
    except Exception as error:
        checks.append(_check("canary", "T2", "fail", "stop", f"instrument identity unavailable: {type(error).__name__}: {error}"))
    else:
        cached = seen.get("canary") or {}
        if seen.get("canary_day") != day or seen.get("canary_key") != canary_key or not cached.get("held") or cached.get("not_run"):
            try:
                c = run_canary()
            except Exception as error:
                c = {"held": False, "not_run": False, "fragments": [], "error": f"{type(error).__name__}: {error}"}
            seen.update(canary_day=day, canary_key=canary_key, canary=c)
            if c["not_run"]:
                checks.append(_check("canary", "T2", "not_run", "warn", "x3d.accrete missing: canary not run"))
            else:
                bad = [f"{o['fragment']} want {o['want']} got {o['got']} ({o['stage']}, {o['codes']})"
                       for o in c["fragments"] if not o.get("matches", o["got"] == o["want"])]
                bad += [f"isolated trap control {o['control']} disagreed" for o in c.get("trap_controls", []) if not o["matches"]]
                checks.append(_check("canary", "T2", "pass" if c["held"] else "fail", "stop",
                                     c.get("error") or "; ".join(bad) or (f"{len(c['fragments'])}/{len(c['fragments'])} held across gate, validator and traps"
                                     if c["held"] else "canary expectations disagreed")))

    # T6: benchmarks (and instruments) have half-lives. Pins must have been re-audited recently.
    audited = cfg.get("pins_audited_utc")
    if audited:
        try:
            age = _days(audited, ctx.now)
            limit = cfg.get("pin_max_age_days", 30)
            checks.append(_check("pin_age", "T6", "fail" if age < 0 or age > limit else "pass", "warn",
                                 f"self-reported pin audit {audited[:10]}, {age:.1f} days ago (limit {limit}); not a re-audit receipt"))
        except (TypeError, ValueError):
            checks.append(_check("pin_age", "T6", "fail", "warn", "invalid self-reported pin audit date"))
    else:
        checks.append(_check("pin_age", "T6", "not_run", "warn", "no pin audit date or re-audit receipt supplied"))

    # T7: check every source, not only the winner. Item links are data and are never egress receipts.
    sources = {s["id"]: s for s in ctx.config["sources"]}
    def https(url):
        try:
            parsed = urlsplit(url)
            return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password
        except (TypeError, ValueError):
            return False
    bad_sources = [sid for sid, src in sources.items() if not https(fetch_url(src))]
    if sig and sig.get("source") not in sources:
        bad_sources.append(str(sig.get("source")))
    sweeps = [r for r in state.get("log", []) if r.get("node") == "scout" and r.get("kind") == "sweep"]
    receipts = [p for r in sweeps for p in (r.get("data") or {}).get("per_source", [])]
    if sweeps:
        bad_sources += sorted(set(sources) - {p.get("source") for p in receipts})
    for receipt in receipts:
        src = sources.get(receipt.get("source"))
        actual = receipt.get("fetch_url")
        if not src or not https(actual) or actual != fetch_url(src):
            bad_sources.append(str(receipt.get("source")))
    checks.append(_check("egress", "T7", "fail" if bad_sources else "pass", "stop",
                         f"non-https, unconfigured or mismatched fetch source(s): {', '.join(sorted(set(bad_sources)))}" if bad_sources
                         else f"{len(sources)} configured https sources; {len(receipts)} fetch receipts checked"
                         + (" (configuration only; no fetch receipts)" if not receipts else "")))

    # T8: agents optimize the grader they imagine. Weaver sees refusal codes, never a held-out record.
    if getattr(ctx, "mem", None) is not None:
        from ..memory import audit_contamination
        a = audit_contamination(ctx.mem)
        checks.append(_check("grader_opacity", "T8", "fail" if a["leaks"] else "pass", "stop",
                             f"contamination audit only: {a['contexts']} contexts journaled, {a['held_out']} held-out records, {len(a['leaks'])} leak(s); grader gaming untested"))

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
    return {"schema": "gobbler.assay-day/2",
            "attempts": {"n": n, "witness_pass": c, "witness_pass_fraction": round(c / n, 4) if n else None,
                         "note": "descriptive fraction over adaptive attempts, including procedural fallback; not task pass@1"},
            "turns": {"n": len(turns), "admitted": sum(bool(t.get("admitted")) for t in turns),
                      "admitted_first_attempt": first,
                      "first_attempt_admission_rate": round(first / len(turns), 4) if turns else None,
                      "rate_scope": "turn ledger only; held/no-signal cycles without turns are excluded",
                      "attempts_histogram": dict(sorted(attempts.items()))},
            "same_signal_reliability": {"estimate": None,
                                        "reason": "requires independent repeated trials of each fixed signal with fixed instruments and policy; this adaptive trace cannot identify pass^3"},
            "refusal_codes": dict(sorted(codes.items(), key=lambda kv: -kv[1])),
            "most_frequent_refusal": sorted(codes, key=lambda c: (-codes[c], c))[0] if codes else None,
            "assayed_cycles": len(assays), "checks": dict(sorted(by_check.items())),
            "stops": sum(1 for r in tape if r.get("node") == "assayer" and r.get("kind") == "stop_the_line")}
