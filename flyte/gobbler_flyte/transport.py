"""Export Gobbler.flyte memory as "X3D Agentic Memory transport records v1" and validate them against that schema.

The schema (schemas/agentic-memory.schema.json, sha256 916d65c3...195a) is the one HagopJay sent for comment on
18 Nov 2026, copied byte for byte. cjson/finalize below follow its builder (schemas/build_schema.py: x3d-cjson-v1,
id = urn:x3d:<record_type>:sha256:<digest of the record without id>), so ids verify with that builder too.

Exported: counterexample, episode and decision memories, plus one evidence record per Witness refusal.
A counterexample's lawful twin is the fragment Keeper admitted later in the same cycle, when there was one:
the reference schema has the slot, and the inner loop produces exactly that pair.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from .memory import MemoryStore, effective_exposures

HERE = Path(__file__).resolve().parents[1]
SCHEMA = HERE / "schemas" / "agentic-memory.schema.json"
SCHEMA_SHA256 = "916d65c335f4a562f6aebd90b971680cac604ab1a965e0305db2442c2a1f195a"
MAX_SAFE = 2**53 - 1
ASCII_KEY = r"^[A-Za-z_][A-Za-z0-9_]*$"


def cjson(value) -> bytes:
    def check(x):
        if x is None or type(x) is bool:
            return
        if type(x) is int:
            if abs(x) > MAX_SAFE:
                raise ValueError("integers must be I-JSON safe")
            return
        if type(x) is str:
            x.encode("utf-8", errors="strict")
            return
        if type(x) is list:
            for i in x:
                check(i)
            return
        if type(x) is dict:
            for k, v in x.items():
                if type(k) is not str or not re.fullmatch(ASCII_KEY, k):
                    raise ValueError("canonical object keys must be ASCII identifiers")
                check(v)
            return
        raise ValueError(f"unsupported canonical type {type(x).__name__}; floats are forbidden")
    check(value)
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _d(value) -> str:
    return hashlib.sha256(cjson(value)).hexdigest()


def finalize(record: dict) -> dict:
    item = dict(record)
    item.pop("id", None)
    if item["record_type"] == "memory":
        item["payload_sha256"] = _d(item["payload"])
    item["id"] = f"urn:x3d:{item['record_type']}:sha256:{_d(item)}"
    return item


def urn(kind: str, sha: str) -> str:
    return f"urn:x3d:{kind}:sha256:{sha}"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def export(store: MemoryStore, *, project: str = "x3d.gobbler", tenant: str = "hagopjay", world_id: str = "world") -> list[dict]:
    policy = {"policy_id": "gobbler-flyte-public-repo", "policy_sha256": _sha("gobbler-flyte public repository records"),
              "classification": "public", "read_principals": ["role:gobbler-flyte"], "data_owner": "hagopjay"}
    instrument = urn("artifact", _sha("x3d.accrete gate 2.0.0 @ 93063bf + x3d_mcp b5c9956 + x3d.loom traps @ 4cf5c7a"))
    hitl_policy = urn("artifact", _sha(json.dumps({"timeout_minutes": 240, "authorized": ["hagopjay"], "irreversible": "typed send"})))

    def base(record_type, m, derived=()):
        exp, _ = effective_exposures(store, m)
        roles = sorted({"sealed": "sealed_test"}.get(e, e) for e in exp)
        return {"schema_version": "x3d.agentic-memory/1", "record_type": record_type, "tenant_id": tenant, "project_id": project,
                "recorded_at": m.valid_from, "recorded_by": f"gobbler-flyte:{m.recorded_by}", "is_example": False, "acl": policy,
                "valid_time": {"from": m.valid_from, "to": m.valid_to}, "derived_from": sorted(set(derived)),
                "exposure": {"partition_ids": [], "roles": roles, "independence_groups": [f"world:{world_id}"], "lineage_complete": True}}

    def scope(artifacts):
        return {"repositories": [], "runtimes": [], "validators": [], "models": [], "artifact_ids": sorted(set(artifacts)),
                "preconditions": [], "parameters": [], "coverage": "exact_artifacts",
                "limits": ["Simulated or offline Gobbler.flyte run unless the turn says live; scripted model replies are not model evidence."]}

    out, evidence_urn = [], {}
    mems = store.all()
    for m in mems:                                        # evidence first: memories cite their ids
        for eid in m.evidence_ids:
            ev = store.evidence(eid)
            if ev is None or eid in evidence_urn:
                continue
            rec = finalize({**base("evidence", m), "subject_ids": [urn("artifact", ev.sha256)], "run_id": urn("run", _sha(f"{world_id}:cycle-{m.cycle}")),
                            "instrument_artifact_id": instrument, "origin": "executed", "grade": "C", "status": "fail",
                            "method": "x3d.accrete gate_fragment, then the pinned x3d_mcp validator in accrete's wrapper, then loom traps",
                            "scope": scope([urn("artifact", ev.sha256)]), "locators": [], "measurements": [],
                            "assessment": {"source_attribution": "not_applicable", "semantic_adjudication": "not_applicable",
                                           "independence": "same_lineage", "reproducibility": "recorded_only"},
                            "limitations": ["Structural refusal only: says nothing about rendering, meaning or reuse."]})
            out.append(rec)
            evidence_urn[eid] = rec["id"]
    twin_of = {}
    for m in mems:
        if m.kind == "episode" and m.subject_sha256:
            for p in m.parent_ids:
                twin_of[p] = urn("artifact", m.subject_sha256)
    for m in mems:
        art = urn("artifact", m.subject_sha256) if m.subject_sha256 else None
        if m.kind == "counterexample":
            payload = {"kind": "counterexample", "target_id": art, "positive_artifact_id": art,
                       "lawful_twin_artifact_id": twin_of.get(m.memory_id),
                       "expected": {"datatype": "string", "value": "admitted", "unit": None, "language": None},
                       "observed": {"datatype": "string", "value": "refused", "unit": None, "language": None},
                       "failure_mode": m.text[:300],
                       "minimization": {"algorithm": "none", "oracle_id": instrument, "preserved_predicate": "refused by the same instrument",
                                        "minimality": "not_attempted"}}
        elif m.kind == "episode":
            payload = {"kind": "episode", "run_id": urn("run", _sha(f"{world_id}:cycle-{m.cycle}")), "trigger": "Gobbler.flyte tick",
                       "action_ids": [art] if art else [], "outcome": "success",
                       "failure_codes": sorted({c for p in m.parent_ids for c in re.findall(r"[A-Z][A-Z0-9_]{3,}", (store.get(p).text if store.get(p) else ""))}),
                       "measurements": [], "lesson_candidates": [m.text[:300]]}
        elif m.kind == "decision":
            payload = {"kind": "decision", "target_ids": [urn("run", _sha(f"{world_id}:cycle-{m.cycle}"))],
                       "outcome": "reject" if " picked C " in m.text else "accept_in_scope", "basis_evidence_ids": [],
                       "policy_artifact_id": hitl_policy, "rationale": m.text[:300], "reviewer": m.text.split(" ")[0]}
        else:
            continue
        cited = [evidence_urn[e] for e in m.evidence_ids if e in evidence_urn]
        rec = finalize({**base("memory", m, derived=[art] if art else []), "payload": payload,
                        "scope": scope([art] if art else []), "evidence_ids": cited, "tags": [m.kind, f"gobbler:{m.memory_id}"],
                        "review_after": None})
        out.append(rec)
    return out


def validate(records: list[dict]) -> dict:
    from jsonschema import Draft202012Validator, FormatChecker
    raw = SCHEMA.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SCHEMA_SHA256:
        raise ValueError("agentic-memory schema bytes changed")
    v = Draft202012Validator(json.loads(raw), format_checker=FormatChecker())
    errors = []
    for r in records:
        for e in v.iter_errors(r):
            errors.append({"id": r.get("id"), "path": "/".join(map(str, e.absolute_path)), "message": e.message[:200]})
        if finalize(r)["id"] != r["id"]:
            errors.append({"id": r.get("id"), "path": "id", "message": "id does not bind the canonical bytes"})
    kinds = {}
    for r in records:
        k = r["record_type"] + (":" + r["payload"]["kind"] if r["record_type"] == "memory" else "")
        kinds[k] = kinds.get(k, 0) + 1
    return {"records": len(records), "kinds": kinds, "errors": errors[:20], "error_count": len(errors), "valid": not errors,
            "schema_sha256": SCHEMA_SHA256}
