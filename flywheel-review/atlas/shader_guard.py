#!/usr/bin/env python3
"""Execute one narrow fm/1 foldback guard on authored XML fixtures.

The guard spots raw GLSL mistaken for a ShaderPart URL. It also accepts explicit
shader data URIs and ordinary relative/HTTP(S) references. Passing means only
that this structural guard found no targeted fault: no shader is fetched,
compiled, linked, rendered, or certified by this program.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
from typing import Any
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures" / "shader-foldback"
RAW_GLSL = re.compile(r"(?:\bvoid\s+main\s*\(|(?:^|\n)\s*#version\b|\bprecision\s+(?:lowp|mediump|highp)\s+\w+\s*;)")
DATA_URI = re.compile(r"^data:[^,]*,", re.IGNORECASE | re.DOTALL)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def classify_reference(reference: str) -> str:
    value = reference.strip()
    if DATA_URI.match(value):
        return "data-uri"
    if re.match(r"^https?://", value, re.IGNORECASE):
        return "external-url"
    if RAW_GLSL.search(value):
        return "raw-glsl"
    return "relative-or-other-url"


def inspect_shader_xml(xml_bytes: bytes) -> dict[str, Any]:
    """Parse XML and MFString URL fields, returning targeted structural results."""
    diagnostics: list[dict[str, str]] = []
    references: list[dict[str, str]] = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        return {"ok": False, "shaderParts": 0, "references": [],
                "diagnostics": [{"code": "XML_PARSE_ERROR", "node": "document", "message": str(exc)}]}
    parts = [node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "ShaderPart"]
    for index, part in enumerate(parts):
        name = part.get("DEF") or f"ShaderPart[{index}]"
        # ElementTree exposes CDATA as normal .text; data URI bodies can contain
        # spaces/newlines and must be treated as one URI rather than MFString words.
        channels = []
        if part.get("url", "").strip():
            channels.append(("url", part.attrib["url"]))
        if (part.text or "").strip():
            channels.append(("text", part.text or ""))
        for channel, raw in channels:
            value = raw.strip()
            if channel == "text":
                values = [value]
            else:
                try:
                    values = shlex.split(value, comments=False, posix=True)
                except ValueError as exc:
                    diagnostics.append({"code": "SHADER_REFERENCE_PARSE_ERROR", "node": name,
                                        "channel": channel, "message": str(exc)})
                    continue
            kinds = [classify_reference(ref) for ref in values]
            # An unquoted raw literal can split into words before its GLSL marker
            # is recognized. Detect that form without misreading data-URI content.
            non_uri_words = " ".join(ref for ref, kind in zip(values, kinds) if kind not in {"data-uri", "external-url"})
            raw_literal = "raw-glsl" in kinds or bool(RAW_GLSL.search(non_uri_words))
            if raw_literal:
                diagnostics.append({"code": "SHADER_RAW_SOURCE", "node": name, "channel": channel,
                                    "message": "Raw GLSL occupies a URL channel; use an explicit data URI or a shader-file URL."})
            for ref, kind in zip(values, kinds):
                references.append({"node": name, "channel": channel, "kind": kind, "sha256": digest(ref.encode("utf-8"))})
    return {"ok": not diagnostics, "shaderParts": len(parts), "references": references, "diagnostics": diagnostics}


def run_foldback(fixture_dir: Path = FIXTURES, atlas_graph: Path = HERE / "out" / "atlas.json") -> dict[str, Any]:
    graph_bytes = atlas_graph.read_bytes()
    graph = json.loads(graph_bytes)
    nodes = {n["id"]: n for n in graph["nodes"]}
    source_ids = ("fm/1", "law/7")
    if any(ref not in nodes for ref in source_ids):
        raise ValueError("originating Atlas sources are unresolved")
    specs = [
        ("gamedev-raw-cdata.x3d", "gamedev", "negative-control", False),
        ("gamedev-raw-url.x3d", "gamedev", "negative-control", False),
        ("gamedev-fixed-data-uri.x3d", "gamedev", "positive-control", True),
        ("positive-https-relative.x3d", "gamedev", "positive-control", True),
        ("music-independent-data-uri.x3d", "music", "distinct-domain-consumer", True),
    ]
    results = []
    for name, domain, role, expected in specs:
        payload = (fixture_dir / name).read_bytes()
        result = inspect_shader_xml(payload)
        negative_caught = any(d["code"] == "SHADER_RAW_SOURCE" for d in result["diagnostics"])
        met_expectation = (result["shaderParts"] > 0 and bool(result["references"])
                           and result["ok"] == expected and (expected or negative_caught))
        results.append({"file": f"atlas/fixtures/shader-foldback/{name}", "sha256": digest(payload),
                        "domain": domain, "role": role, "expectedAccepted": expected,
                        "expectationMet": met_expectation, **result})
    controls_ok = all(r["expectationMet"] for r in results if r["role"].endswith("control"))
    consumer = next(r for r in results if r["role"] == "distinct-domain-consumer")
    code_bytes = Path(__file__).read_bytes()
    return {
        "schema": "flywheel.local-guard-run/1", "synthetic": False, "authoredFixtures": True,
        "guard": {"id": "shader-raw-source/narrow-1", "code": "atlas/shader_guard.py", "sha256": digest(code_bytes)},
        "sources": [{"id": ref, "definedAt": nodes[ref]["definedAt"], "recordSha256": digest(canonical_bytes(nodes[ref]))} for ref in source_ids],
        "atlas": {"path": "atlas/out/atlas.json", "sha256": digest(graph_bytes), "pins": graph["meta"]["inputs"]},
        "results": results, "controlsPassed": controls_ok,
        "localTransfer": {"origin": "gamedev", "consumer": "music", "distinctDomains": True,
                          "accepted": controls_ok and consumer["expectationMet"], "consumerSha256": consumer["sha256"]},
        "ok": all(r["expectationMet"] for r in results),
        "scope": "Executed local structural guard on newly authored fixtures. This is not the synthetic teaching replay.",
        "limits": ["No shaders were fetched, compiled, linked, or rendered.",
                   "Passing does not establish X3D schema validity or shader correctness.",
                   "The consumer is an authored music-labelled fixture, not a live music repository integration.",
                   "Raw GLSL recognition uses a narrow high-confidence marker set, not a complete GLSL parser.",
                   "Hashes bind the local bytes and source records; no external trust anchor is supplied."]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=FIXTURES)
    parser.add_argument("--atlas", type=Path, default=HERE / "out" / "atlas.json")
    parser.add_argument("--output", type=Path, default=HERE.parent / "foldback-run.json")
    args = parser.parse_args()
    try:
        report = run_foldback(args.fixtures, args.atlas)
        args.output.write_bytes(canonical_bytes(report))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"shader guard: {exc}\n")
    print(json.dumps({"ok": report["ok"], "fixtures": len(report["results"]), "output": str(args.output),
                      "scope": "local structural checks only", "sha256": digest(canonical_bytes(report))}, sort_keys=True))
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
