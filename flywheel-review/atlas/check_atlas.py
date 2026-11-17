#!/usr/bin/env python3
"""The Atlas witness. Reads out/ back with other programs and writes out/receipt.json.

  1. rebuild      build_atlas.py run again gives the same bytes
  2. two formats  rdflib parses atlas.ttl and atlas.jsonld into the same set of triples
  3. vocabulary   every class and property used is declared in atlas-vocab.ttl (or is rdfs / dcterms / prov)
  4. two routes   figures the builder computed in Python are recomputed with SPARQL over the Turtle file
  5. claims       x3d.docs' own checker (claims_lib: FIND, COMPARE, LOCATE) reads every Atlas claim at its pinned commit
  6. controls     three planted faults must be rejected by that same checker

Needs rdflib. Step 5 reads LOOM-v1.md at its pinned sha from raw.githubusercontent.com once, then from cache/.
Use --offline to skip the fetch (the LOOM claims are then 'unchecked' and the receipt says so).
"""
import collections
import functools
import hashlib
import json
import os
import pathlib
import subprocess
import sys

import rdflib

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(os.environ.get("ATLAS_OUT", HERE / "out"))
sys.path.insert(0, str(HERE))
import build_atlas as B  # noqa: E402

CL = B.CL
CL.token_spans = functools.lru_cache(maxsize=64)(CL.token_spans)     # one tokenisation per source file
FILES = ["atlas.json", "atlas.jsonld", "atlas.ttl", "atlas-vocab.ttl", "atlas-claims.jsonl", "findings.json"]


def digests():
    return {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in FILES}


def main():
    offline = "--offline" in sys.argv
    R = {"schema": "atlas.receipt/0", "inputs": {}, "checks": []}
    ok_all = True

    def record(name, ok, **detail):
        nonlocal ok_all
        ok_all &= bool(ok)
        R["checks"].append({"name": name, "ok": bool(ok), **detail})
        print(f"{'ok ' if ok else 'RED'} {name}: " + ", ".join(f"{k} {v}" for k, v in detail.items() if not isinstance(v, (list, dict))))

    atlas = json.loads((OUT / "atlas.json").read_text(encoding="utf-8"))
    findings = json.loads((OUT / "findings.json").read_text(encoding="utf-8"))
    R["inputs"] = atlas["meta"]["inputs"]

    # 1. rebuild --------------------------------------------------------------------------------
    before = digests()
    run = subprocess.run([sys.executable, str(HERE / "build_atlas.py")], capture_output=True, text=True)
    after = digests()
    record("rebuild gives the same bytes", run.returncode == 0 and before == after, files=len(FILES),
           changed=[f for f in FILES if before[f] != after[f]])
    R["sha256"] = after
    record("every count matches what the sources state", all(p["ok"] for p in findings["parity"]),
           rows=len(findings["parity"]), red=[p["what"] for p in findings["parity"] if not p["ok"]])

    # 2. two formats ----------------------------------------------------------------------------
    g_ttl = rdflib.Graph().parse(OUT / "atlas.ttl", format="turtle")
    g_ld = rdflib.Graph().parse(OUT / "atlas.jsonld", format="json-ld")
    t1, t2 = set(g_ttl), set(g_ld)
    record("Turtle and JSON-LD are the same graph", t1 == t2 and len(t1) > 0, triples_turtle=len(t1),
           triples_jsonld=len(t2), only_turtle=len(t1 - t2), only_jsonld=len(t2 - t1))
    if t1 != t2:
        for t in sorted(t1 ^ t2)[:6]:
            print("   differs:", " ".join(str(x)[:90] for x in t))
    blank = sum(1 for s, p, o in t1 if isinstance(s, rdflib.BNode) or isinstance(o, rdflib.BNode))
    subjects = {str(s) for s, _, _ in t1}
    record("one subject per node, no blank nodes", len(subjects) == len(atlas["nodes"]) and blank == 0,
           subjects=len(subjects), nodes=len(atlas["nodes"]), blank=blank)
    dangling = sorted({str(o) for _, _, o in t1 if isinstance(o, rdflib.URIRef) and str(o).startswith(B.BASE)
                       and str(o) not in subjects})
    record("every edge ends on a node", not dangling, dangling=len(dangling), examples=dangling[:5])

    # 3. vocabulary -----------------------------------------------------------------------------
    vocab = rdflib.Graph().parse(OUT / "atlas-vocab.ttl", format="turtle")
    declared = {str(s) for s in vocab.subjects()}
    standard = ("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "http://www.w3.org/2000/01/rdf-schema#",
                "http://purl.org/dc/terms/", "http://www.w3.org/ns/prov#")
    used = {str(p) for _, p, _ in t1} | {str(o) for _, p, o in t1 if p == rdflib.RDF.type}
    undeclared = sorted(u for u in used if u not in declared and not u.startswith(standard))
    record("every class and property used is declared", not undeclared, used=len(used), undeclared=undeclared)

    # 4. two routes: Python in the builder, SPARQL here -----------------------------------------
    PRE = f"PREFIX a: <{B.VOCAB}> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX prov: <http://www.w3.org/ns/prov#> "
    q = g_ttl.query(PRE + "SELECT ?t (COUNT(?s) AS ?n) WHERE { ?s a ?t } GROUP BY ?t")
    by_class = {str(r.t).split("#")[1]: int(r.n) for r in q}
    record("SPARQL class counts equal the builder's", by_class == atlas["meta"]["counts"], classes=len(by_class))

    q = g_ttl.query(PRE + """SELECT ?v (COUNT(DISTINCT ?n) AS ?c) WHERE {
        ?n a a:Number . { ?n a:resolvedInstrument/a:usesTool ?tv } UNION { ?n a:usesTool ?tv }
        ?tv a:ofTool ?t ; a:version ?v . ?t rdfs:label "X_ITE" } GROUP BY ?v""")
    xite = {str(r.v): int(r.c) for r in q}
    record("numbers per X_ITE version: SPARQL equals the builder", xite == findings["tool versions under the numbers"].get("X_ITE"),
           sparql=json.dumps(xite, sort_keys=True))

    q = g_ttl.query(PRE + """SELECT (COUNT(DISTINCT ?n) AS ?c) WHERE {
        ?n a a:Number ; a:grade <grade/C> . ?c1 a:supports ?n ; a:verdict "verified" }""", base=B.BASE)
    c_ver = int(next(iter(q)).c)
    record("Confirmed numbers with a verified quote: SPARQL equals the builder",
           c_ver == findings["traceability"]["Confirmed numbers with a verified quote"], sparql=c_ver,
           builder=findings["traceability"]["Confirmed numbers with a verified quote"])

    q = g_ttl.query(PRE + """SELECT (COUNT(DISTINCT ?l) AS ?c) WHERE { ?l a a:Law ; a:checkKind "process" }""")
    n_proc = int(next(iter(q)).c)
    record("process-only laws: SPARQL equals the builder", n_proc == findings["check kinds"].get("process"),
           sparql=n_proc)

    q = g_ttl.query(PRE + """SELECT (COUNT(?s) AS ?c) WHERE { ?s prov:wasQuotedFrom ?d . ?d a a:SourceDocument ; a:atPin ?p }""")
    n_quoted = int(next(iter(q)).c)
    record("every quoted row reaches a pinned file", n_quoted ==
           sum(1 for e in atlas["edges"] if e["p"] == "quotedFrom"), rows=n_quoted)

    # 5. claims: the family's checker over the Atlas's own ledger -------------------------------
    meta, entries, problems = CL.load_ledger(OUT / "atlas-claims.jsonl")
    # the resolver looks in cache/ before the network, so a cached pinned file can be read offline too
    urls = {f"https://raw.githubusercontent.com/{CL.OWNERS.get(m.group(1), CL.OWNER)}/{m.group(1)}/{m.group(2)}/{m.group(3)}"
            for m in (CL.SOURCE_RE.match(e["source"]) for e in entries) if m and not (HERE.parent / "src" / m.group(1)).is_dir()}
    cached = all((HERE / "cache" / hashlib.sha256(u.encode()).hexdigest()).is_file() for u in urls)
    resolver = CL.Resolver(repos=HERE.parent / "src", fetch=(not offline) or cached, cache=HERE / "cache")
    policy = CL.Policy(strict_pins=True)
    verdicts = collections.Counter()
    pins = collections.Counter()
    by_type = collections.defaultdict(collections.Counter)
    bad = []
    for e in entries:
        item = CL.check_entry(e, resolver, policy)
        verdicts[item["verdict"]] += 1
        pins[item["pin"] or item["note"][:40]] += 1
        by_type[e["id"].split("/")[0]][item["verdict"]] += 1
        if item["verdict"] != "verified" and len(bad) < 12:
            bad.append({"id": e["id"], "verdict": item["verdict"], "status": item["status"],
                        "value_status": item["value_status"], "line": e.get("line"), "found_at": item["lines"][:3],
                        "note": item["note"]})
    node_ids = {n["id"] for n in atlas["nodes"]}
    claimable = [n["id"] for n in atlas["nodes"] if n["type"] in
                 ("Law", "FailureMode", "OpenQuestion", "Number", "Heuristic", "Drill", "FailureClass")]
    covered = {e["id"] for e in entries}
    record("the family's checker verifies every Atlas claim at its pin",
           verdicts["verified"] == len(entries) and not problems and len(entries) > 0,
           claims=len(entries), verified=verdicts["verified"], check=verdicts["check"], reworded=verdicts["reworded"],
           unchecked=verdicts["unchecked"], read=dict(pins), by_type={k: dict(v) for k, v in sorted(by_type.items())},
           not_verified=bad, offline=offline)
    record("every copied row has a claim", covered == set(claimable) and covered <= node_ids, rows=len(claimable),
           with_claim=len(covered), missing=sorted(set(claimable) - covered)[:8])
    R["engine"] = {"checker": "x3d.docs docs/tools-shared/claims_lib.py", "schema": CL.SCHEMA,
                   "claims_lib_sha256": hashlib.sha256((B.DOCS / "docs" / "tools-shared" / "claims_lib.py").read_bytes()).hexdigest(),
                   "strict_pins": True, "rdflib": rdflib.__version__, "python": sys.version.split()[0]}

    # 6. controls: the checker must be able to say no -------------------------------------------
    def first(prefix):
        return dict(next(e for e in entries if e["id"].startswith(prefix)))
    wrong_value = first("number/")
    wrong_value["value"] = "31415.9265"
    wrong_line = first("fm/")
    wrong_line["line"] = wrong_line["line"] + 7
    made_up = first("law/")
    made_up["quote"] = made_up["quote"] + " and a sentence the Loom never wrote"
    planted = {"a value that is not in its quote": wrong_value, "a quote hinted at the wrong line": wrong_line,
               "a quote that is not in the source": made_up}
    got = {name: CL.check_entry(e, resolver, policy)["verdict"] for name, e in planted.items()}
    record("three planted faults are rejected", all(v != "verified" for v in got.values()), verdicts=json.dumps(got))

    # 7. the walkable scene, if it was made ------------------------------------------------------
    world = OUT / "atlas-world.x3d"
    if world.is_file():
        import re
        import xml.etree.ElementTree as ET
        scene_files = ["atlas-world.x3d", "atlas-panel.json"]
        b4 = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in scene_files}
        run = subprocess.run([sys.executable, str(HERE / "fly_atlas.py")], capture_output=True, text=True)
        af = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in scene_files}
        record("scene: rebuild gives the same bytes", run.returncode == 0 and b4 == af, files=len(scene_files))
        R["sha256"].update(af)
        root = ET.parse(world).getroot()
        metas = {m.get("name"): m.get("content") for m in root.iter("meta")}
        record("scene: drawn from this atlas.json (sha256 in its head)", metas.get("x3datlas.atlas.sha256") == after["atlas.json"],
               head=str(metas.get("x3datlas.atlas.sha256"))[:12], atlas=after["atlas.json"][:12])
        sensors = {e.get("DEF"): e.get("description") for e in root.iter("TouchSensor")}
        panel = json.loads((OUT / "atlas-panel.json").read_text(encoding="utf-8"))["items"]
        kinds = collections.Counter(v["kind"] for v in panel.values())
        want = {"Law": "Law", "FailureMode": "Failure mode", "Chapter": "Chapter", "Number": "Number",
                "Heuristic": "Heuristic", "Drill": "Drill"}
        record("scene: one sensor per row, each with a description and a panel answer",
               set(sensors) == set(panel) and all(sensors.values())
               and all(kinds[k] == atlas["meta"]["counts"][t] for t, k in want.items()),
               sensors=len(sensors), panel=len(panel), kinds=dict(kinds))
        seen, early = set(), []
        for e in root.iter():
            if e.get("DEF"):
                seen.add(e.get("DEF"))
            if e.get("USE") and e.get("USE") not in seen:
                early.append(e.get("USE"))
        tags = collections.Counter(e.tag for e in root.iter())
        record("scene: no Script, no USE before its DEF", tags["Script"] == 0 and not early, shapes=tags["Shape"],
               routes=tags["ROUTE"], early=early[:5])
        env = dict(os.environ)
        sys.path.insert(0, str(HERE))
        import validate_one as _vo      # only to resolve the x3d_mcp checkout the same way the validator does
        mcp_dir = _vo.REPO
        env["X3D_MCP_DIR"] = mcp_dir
        v = subprocess.run([sys.executable, str(HERE / "validate_one.py"), str(world)], env=env, capture_output=True, text=True, timeout=300)
        m = re.search(r"XSD valid: (\w+).*semantic: (.*)$", v.stdout.splitlines()[0] if v.stdout else "")
        sem = re.findall(r"\d+", m.group(2)) if m else []
        mcp_sha = subprocess.run(["git", "-C", mcp_dir, "rev-parse", "--short=7", "HEAD"],
                                 capture_output=True, text=True).stdout.strip()
        R["engine"]["x3d_mcp_local_checkout"] = mcp_sha
        record("scene: x3d_mcp says XSD valid, 0 semantic errors, 0 warnings",
               bool(m) and m.group(1) == "True" and (sem[:2] == ["0", "0"] or "All Clear" in m.group(2)),
               x3d_mcp=mcp_sha, xsd=m.group(1) if m else "no answer", semantic=m.group(2) if m else v.stderr[-200:])

    R["ok"] = ok_all
    RECEIPT = pathlib.Path(os.environ.get("ATLAS_RECEIPT", OUT / "receipt.json"))   # ATLAS_RECEIPT keeps the archived receipt untouched
    RECEIPT.write_text(json.dumps(R, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("\nWITNESS " + ("GREEN" if ok_all else "RED") + f": {sum(c['ok'] for c in R['checks'])} of {len(R['checks'])} checks")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
