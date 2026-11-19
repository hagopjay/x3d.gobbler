"""Project Gobbler.flyte memory into "X3D Agentic Memory transport records v1".

The schema (schemas/agentic-memory.schema.json, sha256 916d65c3...195a) is the one HagopJay sent for comment on
18 Nov 2026, copied byte for byte. cjson/finalize below follow its builder (schemas/build_schema.py: x3d-cjson-v1,
id = urn:x3d:<record_type>:sha256:<digest of the record without id>), so ids verify with that builder too.

This is a lossy interoperability projection, NOT a restorable MemoryStore backup.
Local review/revocation history, scope and relationship semantics require the
source store. Schema/hash validation is separate from reference closure or
semantic validation. Registry references alone do not attest an executed
instrument, and an arbitrary parent relation does not establish a lawful twin.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
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


def export(store: MemoryStore, *, project: str = "x3d.gobbler", tenant: str = "hagopjay", world_id: str = "world",
           recorded_at: str | None = None) -> list[dict]:
    # This records creation of the exported envelope, not an invented historical
    # ingestion time. Callers can pin it when they need reproducible exports.
    exported_at = recorded_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    instrument = urn("artifact", _sha("x3d.accrete gate 2.0.0 @ 93063bf + x3d_mcp b5c9956 + x3d.loom traps @ 4cf5c7a"))
    hitl_policy = urn("artifact", _sha(json.dumps({"timeout_minutes": 240, "authorized": ["hagopjay"], "irreversible": "typed send"})))

    def base(record_type, m, derived=()):
        exp, _ = effective_exposures(store, m)
        # Local evidence resolution is not canonical reference closure: this
        # projection omits the artifact/run/source-parent records it references.
        # Preserve known labels, but require a resolving importer to revalidate.
        exp.add("unknown")
        roles = sorted({"sealed": "sealed_test"}.get(e, e) for e in exp)
        try:
            lineage = store.lineage(m)
            readers = set(m.readers)
            for ancestor in lineage:
                readers.intersection_update(ancestor.readers)
        except ValueError:
            readers = set()
        grants = sorted(f"organ:{name}" for name in readers) or ["role:export-custodian"]
        policy_body = {"tenant": tenant, "project": project, "read_principals": grants}
        policy = {"policy_id": "gobbler-flyte-source-readers", "policy_sha256": _d(policy_body),
                  "classification": "restricted", "read_principals": grants, "data_owner": tenant}
        return {"schema_version": "x3d.agentic-memory/1", "record_type": record_type, "tenant_id": tenant, "project_id": project,
                "recorded_at": exported_at, "recorded_by": f"gobbler-flyte:{m.recorded_by}", "is_example": False, "acl": policy,
                "valid_time": {"from": m.valid_from, "to": m.valid_to}, "derived_from": sorted(set(derived)),
                "exposure": {"partition_ids": [], "roles": roles, "independence_groups": [f"world:{world_id}"], "lineage_complete": False}}

    def scope(artifacts):
        return {"repositories": [], "runtimes": [], "validators": [], "models": [], "artifact_ids": sorted(set(artifacts)),
                "preconditions": [], "parameters": [], "coverage": "exact_artifacts",
                "limits": ["Lossy projection, not a restorable memory backup; local scope/review/revocation metadata is not reconstructed.",
                           "Referenced artifact/run URNs are external placeholders, not complete canonical records in this export.",
                           "Simulated or offline Gobbler.flyte run unless the turn says live; scripted model replies are not model evidence."]}

    out, evidence_urn = [], {}
    mems = store.all()
    for m in mems:                                        # evidence first: memories cite their ids
        for eid in m.evidence_ids:
            ev = store.evidence(eid)
            if ev is None or eid in evidence_urn:
                continue
            # EvidenceRef records only a declaration of instrument/hash/exposure.
            # It has no executed-stage result or receipt; do not manufacture one,
            # especially when exporting the Atlas's source catalogue references.
            rec = finalize({**base("evidence", m), "subject_ids": [urn("artifact", ev.sha256)], "run_id": None,
                            "instrument_artifact_id": None, "origin": "source_read", "grade": "L", "status": "not_run",
                            "method": f"Local evidence registry declaration: {ev.instrument}",
                            "scope": scope([urn("artifact", ev.sha256)]), "locators": [], "measurements": [],
                            "assessment": {"source_attribution": "not_applicable", "semantic_adjudication": "not_applicable",
                                           "independence": "same_lineage", "reproducibility": "recorded_only"},
                            "limitations": ["Registry declaration read only; no execution receipt or per-stage outcome is preserved by EvidenceRef.",
                                            "Does not establish source reading, semantic truth, rendering, or reuse."]})
            out.append(rec)
            evidence_urn[eid] = rec["id"]
    for m in mems:
        art = urn("artifact", m.subject_sha256) if m.subject_sha256 else None
        if m.kind == "counterexample":
            payload = {"kind": "counterexample", "target_id": art, "positive_artifact_id": art,
                       # Local parents record refusal history, not an independently
                       # witnessed same-edit lawful twin, even within one cycle.
                       "lawful_twin_artifact_id": None,
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
                       "outcome": "abstain", "basis_evidence_ids": [],
                       "policy_artifact_id": hitl_policy, "rationale": "Decision outcome/reviewer not present as structured data. Source text: " + m.text[:300],
                       "reviewer": "unrecorded"}
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
        try:
            if r.get("record_type") == "memory" and r.get("payload_sha256") != _d(r.get("payload")):
                errors.append({"id": r.get("id"), "path": "payload_sha256", "message": "payload hash does not bind the supplied payload"})
            # Verify the SUPPLIED record, without finalize repairing its fields.
            supplied = {k: value for k, value in r.items() if k != "id"}
            want_id = urn(r.get("record_type", "unknown"), _d(supplied))
            if want_id != r.get("id"):
                errors.append({"id": r.get("id"), "path": "id", "message": "id does not bind the supplied canonical bytes"})
        except (TypeError, ValueError) as e:
            errors.append({"id": r.get("id"), "path": "", "message": str(e)[:200]})
    kinds = {}
    for r in records:
        k = r["record_type"] + (":" + r["payload"]["kind"] if r["record_type"] == "memory" else "")
        kinds[k] = kinds.get(k, 0) + 1
    return {"records": len(records), "kinds": kinds, "errors": errors[:20], "error_count": len(errors), "valid": not errors,
            "schema_sha256": SCHEMA_SHA256, "restorable": False,
            "validation_scope": "JSON Schema and supplied content hashes only; reference closure, source authorization and semantics are not validated."}
