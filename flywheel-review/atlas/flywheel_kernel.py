#!/usr/bin/env python3
"""Compile an auditable archive view and replay a deliberately synthetic learning loop.

No network or third-party modules. Hashes bind local bytes, not authorship or truth.
The transition checker verifies evidence shape/binding, not the physical experiment.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
STATES = ("candidate", "reproduced", "guarded", "reused")
REQUIRED_OUTPUTS = frozenset({"atlas-claims.jsonl", "atlas-panel.json", "atlas-vocab.ttl", "atlas-world.x3d",
                              "atlas.json", "atlas.jsonld", "atlas.ttl", "findings.json"})


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_graph(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Reject a graph whose local identity or endpoint integrity is ambiguous."""
    nodes: dict[str, dict[str, Any]] = {}
    for node in graph["nodes"]:
        nid = node.get("id")
        if not isinstance(nid, str) or not nid or nid in nodes:
            raise ValueError(f"invalid or duplicate node id: {nid!r}")
        if not isinstance(node.get("type"), str):
            raise ValueError(f"node type absent: {nid}")
        nodes[nid] = node
    triples: set[tuple[str, str, str]] = set()
    for edge in graph["edges"]:
        s, p, o = edge.get("s"), edge.get("p"), edge.get("o")
        if s not in nodes or o not in nodes or not isinstance(p, str) or not p:
            raise ValueError(f"unresolved or invalid edge: {edge!r}")
        triple = (s, p, o)
        if triple in triples:
            raise ValueError(f"duplicate edge: {triple!r}")
        triples.add(triple)
    return nodes


def domain_manifest() -> list[dict[str, Any]]:
    """A proposed integration map; these rows are designs, never measured activity."""
    rows = [
        ("ontology", "Ontology", [.48,.67,1], "Name what a scene means", ["typed entities", "source assertions"], ["SHACL constraints", "queryable meanings"], ["x3d.onto"]),
        ("ml", "ML", [.98,.35,.65], "Generate, rank, and challenge candidates", ["versioned corpus", "held-out tasks"], ["candidate scenes", "scoped evaluations"], ["x3d.ML", "x3d.lab"]),
        ("maths", "Maths", [.69,.45,1], "Make structure and invariants visible", ["equations", "numerical tolerances"], ["reference solutions", "interactive explanations"], ["x3d.STEM"]),
        ("stem", "STEM", [.22,.88,1], "Turn curiosity into repeatable experiments", ["reference solutions", "learner questions"], ["instrumented worlds", "learning records"], ["x3d.STEM", "x3d.docs"]),
        ("gameplay", "Gameplay", [1,.70,.23], "Invite people to discover through play", ["mechanics", "human feedback"], ["play traces", "failure discoveries"], ["x3d.demo"]),
        ("gamedev", "Game development", [.92,.38,1], "Build reusable world-making systems", ["scene assets", "interaction contracts"], ["tested mechanics", "portable scenes"], ["x3d.loom", "x3d.demo"]),
        ("physics", "Physics", [1,.41,.20], "Compare simulated motion with a witness", ["units and geometry", "initial conditions"], ["trajectories", "error envelopes"], ["x3d.physics"]),
        ("music", "Music", [1,.34,.76], "Give structures a sound a person can judge", ["scores", "events and timing"], ["audio artifacts", "listening judgments"], ["x3d.music"]),
        ("data", "Data intensity", [.24,1,.67], "Keep reusable evidence findable", ["run artifacts", "content hashes"], ["datasets", "lineage and queries"], ["x3d.ML", "x3d.xray"]),
        ("heritage", "Heritage", [1,.77,.40], "Connect cultural sources with living worlds", ["credited sources", "rights and context"], ["contextualized scenes", "human interpretations"], ["x3d.Mashtots"]),
        ("blender-io", "Blender IO hub", [.30,.86,.80], "Move authored scenes through explicit contracts", ["Blender scene", "export settings"], ["X3D assets", "round-trip loss reports"], ["x3d-blender-io"]),
        ("architecture", "Architecture", [.93,.92,.43], "Give spaces geometry, meaning, and provenance", ["building elements", "spatial relationships"], ["inspectable spaces", "semantic validation"], ["x3d.demo", "x3d.onto"]),
    ]
    return [{"id": i, "label": label, "color": color, "role": role, "inputs": ins,
             "outputs": outs, "repositories": repos, "evidence": "proposed"}
            for i, label, color, role, ins, outs, repos in rows]


def replay_incident(incident: dict[str, Any], artifacts: list[dict[str, Any]],
                    events: list[dict[str, Any]], known_source_ids: set[str]) -> dict[str, Any]:
    """Validate the bounded protocol; receipts remain synthetic if their inputs are.

    Promotion needs bound evidence of the expected kind and verdict. Reuse counts
    distinct (guard, target, input hash) tuples; retrying one run adds no momentum.
    Caller-supplied JSON is not authenticated and cannot establish empirical truth.
    """
    if not incident.get("id") or not incident.get("sourceRefs"):
        raise ValueError("incident must name its identity and source references")
    if any(ref not in known_source_ids for ref in incident["sourceRefs"]):
        raise ValueError("unresolved incident source reference")
    by_id: dict[str, dict[str, Any]] = {}
    for item in artifacts:
        aid = item.get("id")
        if not isinstance(aid, str) or not aid or aid in by_id:
            raise ValueError("invalid or duplicate artifact id")
        if not isinstance(item.get("content"), str) or item.get("sha256") != sha256(item["content"].encode("utf-8")):
            raise ValueError(f"artifact content hash mismatch: {aid}")
        by_id[aid] = item
    for ref in incident.get("artifactRefs", []):
        if ref not in by_id:
            raise ValueError("unresolved incident artifact reference")
    if not incident.get("artifactRefs"):
        raise ValueError("incident artifact references are required")
    for item in by_id.values():
        for field in ("guardRef", "subjectRef", "inputRef"):
            if field in item and item[field] not in by_id:
                raise ValueError(f"unresolved artifact {field}: {item['id']}")
    domains = {d["id"] for d in domain_manifest()}
    def refs(event: dict[str, Any], field: str, kind: str | None = None) -> list[dict[str, Any]]:
        values = event.get(field, [])
        if not values or any(ref not in by_id for ref in values):
            raise ValueError(f"unresolved or missing {field}")
        resolved = [by_id[ref] for ref in values]
        if kind and any(a.get("kind") != kind for a in resolved):
            raise ValueError(f"wrong evidence kind in {field}")
        return resolved
    event_ids: set[str] = set()
    reuse_keys: set[tuple[str, str, str]] = set()
    active_guards: set[str] = set()
    state: str | None = None
    origin_domain: str | None = None
    for event in events:
        eid = event.get("id")
        if not isinstance(eid, str) or not eid or eid in event_ids:
            raise ValueError("invalid or duplicate event id")
        event_ids.add(eid)
        if event.get("domain") not in domains:
            raise ValueError("unresolved event domain")
        nxt = event.get("state")
        if state is None:
            allowed = {"candidate"}
        elif state == "reused":
            allowed = {"reused"}
        else:
            allowed = {STATES[STATES.index(state) + 1]}
        if nxt not in allowed:
            raise ValueError(f"bad transition: {state!r} -> {nxt!r}")
        refs(event, "artifactRefs")
        if nxt == "candidate":
            origin_domain = event["domain"]
        if nxt == "reproduced":
            evidence = refs(event, "runRefs", "reproduction")
            if any(a.get("subjectRef") not in incident["artifactRefs"] for a in evidence):
                raise ValueError("reproduction is not bound to the incident artifact")
            if not any(a.get("verdict") == "observed-failure" for a in evidence):
                raise ValueError("reproduction requires an observed-failure run")
        elif nxt == "guarded":
            guards = refs(event, "guardRefs", "guard")
            evidence = refs(event, "runRefs", "control")
            if any(a.get("guardRef") not in {g["id"] for g in guards} for a in evidence):
                raise ValueError("controls are not bound to the promoted guard")
            for guard in guards:
                verdicts = {a.get("verdict") for a in evidence if a.get("guardRef") == guard["id"]}
                if not {"mutant-rejected", "valid-accepted"}.issubset(verdicts):
                    raise ValueError("each guard promotion requires passing positive and negative controls")
            active_guards = {a["id"] for a in guards}
        elif nxt == "reused":
            guards = refs(event, "guardRefs", "guard")
            if any(a["id"] not in active_guards for a in guards):
                raise ValueError("reuse refers to a guard that was not promoted")
            evidence = refs(event, "runRefs", "reuse")
            for run in evidence:
                if run.get("guardRef") not in {g["id"] for g in guards}:
                    raise ValueError("reuse run is not bound to the promoted guard")
                if run.get("verdict") != "accepted" or run.get("target") not in domains:
                    raise ValueError("reuse requires an accepted run with a target")
                if run["target"] == origin_domain or run["target"] != event["domain"]:
                    raise ValueError("reuse target must differ from origin and match the event domain")
                input_artifact = by_id.get(run.get("inputRef"))
                if input_artifact is None or input_artifact.get("kind") != "scene":
                    raise ValueError("reuse input must reference a bound scene artifact")
                digest = run.get("inputSha256", "")
                if digest != input_artifact["sha256"]:
                    raise ValueError("reuse input hash does not match its scene artifact")
                reuse_keys.add((run["guardRef"], run["target"], digest))
        state = nxt
    return {"state": state, "verifiedReuses": len(reuse_keys), "eventCount": len(events),
            "meaning": "protocol-checked synthetic reuse; no archived or live transfer is established"}


def synthetic_demo(known_source_ids: set[str]) -> dict[str, Any]:
    def artifact(aid: str, kind: str, content: str, **extra: Any) -> dict[str, Any]:
        return {"id": aid, "kind": kind, "content": content, "sha256": sha256(content.encode()), "synthetic": True, **extra}
    artifacts = [
        artifact("demo:candidate", "scene", "ShaderPart raw GLSL teaching mutant; reconstructed from fm/1"),
        artifact("demo:repro", "reproduction", "Synthetic runner observes raw shader source treated as URL", verdict="observed-failure", subjectRef="demo:candidate"),
        artifact("demo:guard", "guard", "Reject a ShaderPart literal that lacks an explicit shader data URL"),
        artifact("demo:negative", "control", "Synthetic raw-source mutant is rejected", verdict="mutant-rejected", guardRef="demo:guard"),
        artifact("demo:positive", "control", "Synthetic data:x-shader/x-fragment fixture is accepted", verdict="valid-accepted", guardRef="demo:guard"),
        artifact("demo:music-scene", "scene", "synthetic-music-scene-1"),
        artifact("demo:reuse", "reuse", "Synthetic Music scene passes the explicit shader URL guard", verdict="accepted", target="music", guardRef="demo:guard", inputRef="demo:music-scene", inputSha256=sha256(b"synthetic-music-scene-1")),
    ]
    incident = {"id": "demo:shader-source", "title": "A shader failure becomes a reusable guard",
                "sourceRefs": ["fm/1", "law/7", "law/44"], "artifactRefs": ["demo:candidate"],
                "sourceRoles": {"fm/1": "shader source failure", "law/7": "originating foldback law linked by paidForBy", "law/44": "two-sided control discipline"},
                "scope": "Reconstructed teaching example inspired by archived nodes; no archived run is replayed."}
    events = [
        {"id": "demo:e1", "state": "candidate", "domain": "gamedev", "artifactRefs": ["demo:candidate"], "label": "A scene proposes a new effect"},
        {"id": "demo:e2", "state": "reproduced", "domain": "data", "artifactRefs": ["demo:candidate"], "runRefs": ["demo:repro"], "label": "A witness isolates the failure"},
        {"id": "demo:e3", "state": "guarded", "domain": "ontology", "artifactRefs": ["demo:guard"], "guardRefs": ["demo:guard"], "runRefs": ["demo:negative", "demo:positive"], "label": "Two controls show the guard can discriminate"},
        {"id": "demo:e4", "state": "reused", "domain": "music", "artifactRefs": ["demo:reuse"], "guardRefs": ["demo:guard"], "runRefs": ["demo:reuse"], "label": "A distinct domain consumes the guarded result"},
    ]
    result = replay_incident(incident, artifacts, events, known_source_ids)
    return {"synthetic": True, "label": "SYNTHETIC TEACHING REPLAY", "states": list(STATES),
            "incident": incident, "artifacts": artifacts, "events": events, "result": result}


def compile_observatory(atlas_dir: Path) -> dict[str, Any]:
    atlas_dir = atlas_dir.resolve()
    graph_bytes = (atlas_dir / "atlas.json").read_bytes()
    graph = json.loads(graph_bytes)
    nodes = validate_graph(graph)
    counts = dict(sorted(Counter(n["type"] for n in nodes.values()).items()))
    predicates = dict(sorted(Counter(e["p"] for e in graph["edges"]).items()))
    if counts != graph["meta"]["counts"] or predicates != graph["meta"]["edges"]:
        raise ValueError("graph metadata counts disagree with actual records")
    receipt = json.loads((atlas_dir / "receipt.json").read_text())
    if receipt["inputs"] != graph["meta"]["inputs"]:
        raise ValueError("receipt source pins disagree with graph")
    digests = receipt.get("sha256")
    if not isinstance(digests, dict) or set(digests) != REQUIRED_OUTPUTS:
        raise ValueError("receipt must cover exactly the eight canonical Atlas outputs")
    checks = []
    for name, expected in sorted(digests.items()):
        if not isinstance(expected, str) or len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
            raise ValueError(f"invalid receipt SHA-256: {name}")
        path = (atlas_dir / name).resolve()
        if not path.is_relative_to(atlas_dir):
            raise ValueError("receipt file escapes atlas directory")
        actual = sha256(path.read_bytes())
        if actual != expected:
            raise ValueError(f"receipt hash mismatch: {name}")
        checks.append({"check": "receipt-sha256", "file": name, "sha256": actual, "ok": True})
    edges = graph["edges"]
    verified_claims = {n["id"] for n in nodes.values() if n["type"] == "Claim" and n.get("verdict") == "verified"}
    quoted_numbers = {e["o"] for e in edges if e["p"] == "supports" and e["s"] in verified_claims and nodes[e["o"]]["type"] == "Number"}
    confirmed_numbers = {e["s"] for e in edges if e["p"] == "grade" and e["o"] == "grade/C" and nodes[e["s"]]["type"] == "Number"}
    # Match the archived builder's documented broad linkage criterion. A mentions
    # edge counts as an explicit ID join, not as a claim that the law fixed it.
    linked_failures = set()
    for edge in edges:
        s, o = nodes[edge["s"]], nodes[edge["o"]]
        if edge["p"] in {"paidForBy", "fixedByLaw", "mentions"} and {s["type"], o["type"]} == {"Law", "FailureMode"}:
            linked_failures.add(s["id"] if s["type"] == "FailureMode" else o["id"])
    linked_heuristics = {e["s"] for e in edges if e["p"] == "evidencedBy" and nodes[e["s"]]["type"] == "Heuristic"}
    checks += [{"check": "unique-node-and-edge-identities", "ok": True}, {"check": "all-edge-endpoints-resolve", "ok": True}, {"check": "metadata-counts-match-records", "ok": True}]
    snapshot = {
        "kind": "archive", "source": "flywheel-review/atlas/out/atlas.json", "sha256": sha256(graph_bytes),
        "pins": graph["meta"]["inputs"], "nodeCount": len(nodes), "edgeCount": len(edges), "counts": counts,
        "metrics": {"numbers": counts.get("Number", 0), "quotedNumbers": len(quoted_numbers),
                    "confirmedNumbers": len(confirmed_numbers), "confirmedQuotedNumbers": len(confirmed_numbers & quoted_numbers),
                    "unlinkedFailureModes": counts.get("FailureMode", 0) - len(linked_failures),
                    "unlinkedHeuristics": counts.get("Heuristic", 0) - len(linked_heuristics)},
        "metricDefinitions": {
            "quotedNumbers": "Number targets of supports edges from Claim nodes carrying archived verdict=verified.",
            "unlinkedFailureModes": "FailureMode nodes without a paidForBy, fixedByLaw, or mentions edge to a Law in either direction; an ID join is not proof of a fix.",
            "unlinkedHeuristics": "Heuristic nodes without an outgoing evidencedBy edge.",
            "confirmedNumbers": "Number nodes graded grade/C in the archive, without re-promoting the underlying experiment."
        },
        "integrity": {"status": "checked-local", "checks": checks},
        "limits": ["This is the supplied archive snapshot, not a current GitHub inventory.",
                   "Verified quotes are archived claim verdicts; original experiments were not rerun.",
                   "Receipt hashes check local consistency, not authenticity or an external trust anchor.",
                   "Domain assignments are proposed interfaces; their activity and cross-domain transfer are unmeasured.",
                   "No RDF semantic parity, renderer, physics, ML, or human-review check is performed by this kernel."],
    }
    return {"schema": "flywheel.observatory/1", "snapshot": snapshot, "domains": domain_manifest(),
            "demo": synthetic_demo(set(nodes))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas-dir", type=Path, default=HERE / "out")
    parser.add_argument("--output", type=Path, default=HERE.parent.parent / "gobbler-flyte" / "observatory.json")
    parser.add_argument("--check", action="store_true", help="compare the output with a deterministic rebuild without writing")
    args = parser.parse_args()
    try:
        result = compile_observatory(args.atlas_dir)
        payload = canonical_bytes(result)
        if args.check:
            if args.output.read_bytes() != payload:
                raise ValueError(f"stale output: {args.output}")
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(payload)
    except (KeyError, OSError, ValueError, TypeError) as exc:
        parser.exit(1, f"flywheel kernel: {exc}\n")
    print(json.dumps({"ok": True, "output": str(args.output), "sha256": sha256(payload),
                      "nodes": result["snapshot"]["nodeCount"], "edges": result["snapshot"]["edgeCount"],
                      "demoSynthetic": True}, sort_keys=True))


if __name__ == "__main__":
    main()
