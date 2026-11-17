#!/usr/bin/env python3
"""Portable, read-only audit of the attached Atlas snapshot (standard library).

This checks archive consistency. It does not rerun source claims, the historical
witness, an XSD validator, a renderer, or any upstream experiment. The archived
receipt is an input to compare, not an authenticated trust anchor.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

COPIED_TYPES = frozenset({"Law", "FailureMode", "FailureClass", "OpenQuestion", "Number", "Heuristic", "Drill"})
CANONICAL_OUTPUTS = frozenset({
    "atlas-claims.jsonl", "atlas-panel.json", "atlas-vocab.ttl", "atlas-world.x3d",
    "atlas.json", "atlas.jsonld", "atlas.ttl", "findings.json",
})


def _string_map(value: Any) -> bool:
    return isinstance(value, dict) and bool(value) and all(
        isinstance(key, str) and bool(key) and isinstance(item, str) and bool(item)
        for key, item in value.items())


def _count_map(value: Any) -> bool:
    return isinstance(value, dict) and all(
        isinstance(key, str) and bool(key) and type(count) is int and count >= 0
        for key, count in value.items())


def audit(output_directory: Path) -> dict[str, Any]:
    """Return a deterministic report; never write into the snapshot directory."""
    directory = output_directory.resolve()
    report: dict[str, Any] = {
        "schema": "atlas.snapshot-audit/1",
        "scope": "local-archive-consistency",
        "checks": [],
        "limits": [
            "Archived hashes establish agreement with an attached receipt, not authenticity or independent trust.",
            "Source quote matching and original experiments were not rerun.",
            "XML checks cover named references and basic structure, not XSD validity, field typing, rendering, or performance.",
            "A passing archive audit does not promote any evidence grade.",
        ],
    }

    def record(name: str, ok: bool, **detail: Any) -> None:
        report["checks"].append({"name": name, "ok": bool(ok), **detail})

    def read_json(name: str) -> Any:
        return json.loads((directory / name).read_text(encoding="utf-8"))

    try:
        atlas, receipt = read_json("atlas.json"), read_json("receipt.json")
        if not isinstance(atlas, dict) or not isinstance(receipt, dict):
            raise ValueError("atlas and receipt must be JSON objects")
        nodes, edges = atlas["nodes"], atlas["edges"]
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise ValueError("nodes and edges must be arrays")
        meta = atlas.get("meta")
        if not isinstance(meta, dict):
            raise ValueError("atlas.meta must be a JSON object")
        if not _count_map(meta.get("counts")) or not _count_map(meta.get("edges")):
            raise ValueError("atlas.meta.counts and atlas.meta.edges must map nonempty names to nonnegative integer counts")
        record("snapshot JSON readable", True)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        record("snapshot JSON readable", False, error=str(exc))
        report["ok"] = False
        return report

    atlas_inputs, receipt_inputs = meta.get("inputs"), receipt.get("inputs")
    record("receipt pins match graph pins", _string_map(atlas_inputs) and _string_map(receipt_inputs)
           and receipt_inputs == atlas_inputs, atlasInputs=atlas_inputs, receiptInputs=receipt_inputs,
           requirement="Both inputs must be nonempty string maps with identical repository pins.")

    sha_entries = receipt.get("sha256")
    mismatches, matched = [], []
    missing_hashes = sorted(CANONICAL_OUTPUTS - set(sha_entries)) if isinstance(sha_entries, dict) else sorted(CANONICAL_OUTPUTS)
    unexpected_hashes = sorted(set(sha_entries) - CANONICAL_OUTPUTS) if isinstance(sha_entries, dict) else []
    if isinstance(sha_entries, dict):
        for name, expected in sorted(sha_entries.items()):
            if not isinstance(expected, str) or len(expected) != 64 or any(char not in "0123456789abcdef" for char in expected):
                mismatches.append({"file": name, "reason": "expected SHA-256 must be 64 lowercase hexadecimal characters"})
                continue
            path = (directory / name).resolve()
            if not path.is_relative_to(directory):
                mismatches.append({"file": name, "reason": "outside snapshot directory"})
                continue
            try:
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError as exc:
                mismatches.append({"file": name, "reason": str(exc)})
                continue
            if actual != expected:
                mismatches.append({"file": name, "expected": expected, "actual": actual})
            else:
                matched.append(name)
    record("archived output hashes match", isinstance(sha_entries, dict) and not missing_hashes
           and not unexpected_hashes and not mismatches,
           matched=matched, mismatches=mismatches, missingHashes=missing_hashes, unexpectedHashes=unexpected_hashes,
           requirement="The receipt must cover exactly the eight canonical Atlas outputs.")

    id_counts = Counter(node["id"] for node in nodes if isinstance(node, dict)
                        and isinstance(node.get("id"), str))
    bad_nodes = [index for index, node in enumerate(nodes)
                 if not isinstance(node, dict) or not isinstance(node.get("id"), str)
                 or not node.get("id") or not isinstance(node.get("type"), str) or not node.get("type")]
    duplicates = sorted(str(nid) for nid, count in id_counts.items() if count > 1)
    record("graph node IDs are unique and typed", not bad_nodes and not duplicates,
           nodes=len(nodes), duplicates=duplicates, invalidRows=bad_nodes)
    ids = set(id_counts)
    malformed_edges, dangling = [], []
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict) or not all(isinstance(edge.get(key), str) and edge[key] for key in ("s", "p", "o")):
            malformed_edges.append(index)
        elif edge["s"] not in ids or edge["o"] not in ids:
            dangling.append({"index": index, "s": edge["s"], "p": edge["p"], "o": edge["o"]})
    record("graph edges resolve", not malformed_edges and not dangling, edges=len(edges),
           malformedRows=malformed_edges, dangling=dangling)
    type_counts = dict(sorted(Counter(node["type"] for node in nodes
                                      if isinstance(node, dict) and isinstance(node.get("type"), str)).items()))
    predicate_counts = dict(sorted(Counter(edge["p"] for edge in edges
                                           if isinstance(edge, dict) and isinstance(edge.get("p"), str)).items()))
    record("graph totals match embedded metadata",
           type_counts == meta["counts"] and predicate_counts == meta["edges"],
           counts=type_counts, predicateCounts=predicate_counts)

    try:
        ledger = [json.loads(line) for line in (directory / "atlas-claims.jsonl").read_text(encoding="utf-8").splitlines()
                  if line.strip()]
        if not all(isinstance(entry, dict) for entry in ledger):
            raise ValueError("ledger entries must be JSON objects")
        entries = [entry for entry in ledger if "_meta" not in entry]
        if not all(isinstance(entry.get("id"), str) for entry in entries):
            raise ValueError("ledger IDs must be strings")
        claim_ids = Counter(entry.get("id") for entry in entries)
        expected_ids = {node["id"] for node in nodes if isinstance(node, dict)
                        and isinstance(node.get("id"), str) and isinstance(node.get("type"), str)
                        and node["type"] in COPIED_TYPES}
        malformed = [i for i, row in enumerate(entries) if not all(key in row for key in ("id", "value", "quote", "source", "line"))]
        missing = sorted(expected_ids - set(claim_ids))
        unexpected = sorted(str(value) for value in set(claim_ids) - expected_ids)
        duplicate_claims = sorted(str(nid) for nid, count in claim_ids.items() if count > 1)
        record("copied rows each have one ledger entry", not missing and not unexpected and not duplicate_claims and not malformed,
               entries=len(entries), expectedRows=len(expected_ids), missing=missing, unexpected=unexpected,
               duplicates=duplicate_claims, malformedRows=malformed)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        record("copied rows each have one ledger entry", False, error=str(exc))

    try:
        tree = ET.parse(directory / "atlas-world.x3d")
        all_nodes = list(tree.iter())
        definitions: dict[str, str] = {}
        duplicate_defs, unresolved_uses, mismatched_uses = [], [], []
        for node in all_nodes:
            tag = node.tag.rsplit("}", 1)[-1]
            if "USE" in node.attrib:
                name = node.attrib["USE"]
                if name not in definitions:
                    unresolved_uses.append(name)
                elif definitions[name] != tag:
                    mismatched_uses.append(name)
            if "DEF" in node.attrib:
                name = node.attrib["DEF"]
                if name in definitions:
                    duplicate_defs.append(name)
                definitions[name] = tag
        routes = [node for node in all_nodes if node.tag.rsplit("}", 1)[-1] == "ROUTE"]
        bad_routes = [dict(route.attrib) for route in routes
                      if not all(route.attrib.get(key) for key in ("fromNode", "fromField", "toNode", "toField"))
                      or route.attrib.get("fromNode") not in definitions or route.attrib.get("toNode") not in definitions]
        script_count = sum(node.tag.rsplit("}", 1)[-1] == "Script" for node in all_nodes)
        record("scene named references resolve", not duplicate_defs and not unresolved_uses and not mismatched_uses and not bad_routes,
               definitions=len(definitions), routes=len(routes), duplicateDefs=duplicate_defs,
               unresolvedUses=unresolved_uses, mismatchedUses=mismatched_uses, invalidRoutes=bad_routes)
        record("scene has X3D root and no Script", tree.getroot().tag.rsplit("}", 1)[-1] == "X3D" and script_count == 0,
               scripts=script_count)
    except (OSError, ET.ParseError) as exc:
        record("scene named references resolve", False, error=str(exc))

    report["pins"] = atlas_inputs
    report["ok"] = all(check["ok"] for check in report["checks"])
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=Path(__file__).resolve().parent / "out")
    parser.add_argument("--output", type=Path, help="Write a separate report; never overwrite the archived receipt.")
    args = parser.parse_args()
    if args.output and args.output.resolve().is_relative_to(args.snapshot.resolve()):
        parser.error("--output must be outside the snapshot directory to preserve the archived evidence")
    result = audit(args.snapshot)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
