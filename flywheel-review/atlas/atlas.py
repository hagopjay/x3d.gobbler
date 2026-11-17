#!/usr/bin/env python3
"""Ask the Atlas. Reads out/atlas.json; standard library only.

  atlas.py stats
  atlas.py laws-for ShaderPart ROUTE          which laws, failure modes and traps apply to these nodes or engines
  atlas.py what-broke "white|blank"           failure modes that match a pattern, with their fix
  atlas.py how-do-we-know N-TH-4              the footing of a number, a heuristic, a drill, "law 15" or "fm 88"
  atlas.py stands-on "X_ITE 16.6.0"           numbers that stand on a tool version or a pin (x3d_mcp@b4efcd3)
  atlas.py worklist                           what the graph says is thin
Add --json for a machine answer (the shape an MCP tool would return).
"""
import collections
import json
import pathlib
import re
import sys

import policy

HERE = pathlib.Path(__file__).resolve().parent


class Atlas:
    def __init__(self, path=HERE / "out" / "atlas.json"):
        d = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        self.meta = d["meta"]
        self.n = {n["id"]: n for n in d["nodes"]}
        self.out = collections.defaultdict(lambda: collections.defaultdict(list))
        self.inc = collections.defaultdict(lambda: collections.defaultdict(list))
        for e in d["edges"]:
            self.out[e["s"]][e["p"]].append(e["o"])
            self.inc[e["o"]][e["p"]].append(e["s"])

    def of(self, t):
        return [n for n in self.n.values() if n["type"] == t]

    def grade(self, nid):
        g = self.out[nid]["grade"]
        return g[0][-1] if g else "?"

    def resolve(self, text):
        t = text.strip()
        m = re.fullmatch(r"([NHD])-[A-Z]{2,4}-\d+", t)
        if m:
            return {"N": "number", "H": "heuristic", "D": "drill"}[m.group(1)] + "/" + t
        m = re.fullmatch(r"(?i)(law|l)[ /]?(\d+)", t)
        if m:
            return f"law/{m.group(2)}"
        m = re.fullmatch(r"(?i)(fm|failure mode|failure)[ /]?(\d+)", t)
        if m:
            return f"fm/{m.group(2)}"
        m = re.fullmatch(r"(?i)(question|q)[ /]?(\d+)", t)
        if m:
            return f"question/{m.group(2)}"
        return t if t in self.n else None

    # ---- laws-for -------------------------------------------------------------------------------
    def law_failures(self, lid):
        fms = set(self.out[lid]["paidForBy"]) | set(self.inc[lid]["fixedByLaw"])
        fms |= {o for o in self.out[lid]["mentions"] if o.startswith("fm/")}
        fms |= {s for s in self.inc[lid]["mentions"] if s.startswith("fm/")}
        return fms

    def laws_for(self, terms):
        terms = [t.lower() for t in terms]

        def hits(*texts):
            blob = " ".join(x for x in texts if x).lower()
            return sum(1 for t in terms if t in blob)
        fm_hit = {n["id"]: hits(n["failure"], n["fix"]) for n in self.of("FailureMode")}
        fm_hit = {k: v for k, v in fm_hit.items() if v}
        laws = []
        for n in self.of("Law"):
            direct = hits(n["headline"], n.get("text"), n.get("forbids"), n.get("violation"), n.get("checkText"))
            linked = sorted((f for f in self.law_failures(n["id"]) if f in fm_hit), key=lambda f: self.n[f]["n"])
            if direct or linked:
                code = n.get("checkKind") == "code"
                laws.append({"law": n["n"], "headline": n["headline"], "forbids": n.get("forbids"),
                             "check": n.get("checkText"), "mechanical": code,
                             "diagnostics": sorted(self.n[d]["label"] for d in self.out[n["id"]]["caughtBy"]),
                             "matching_failures": [self.n[f]["n"] for f in linked],
                             "rank": policy.kickoff_rank(direct, len(linked), code), "at": n["definedAt"]})
        laws.sort(key=lambda r: (-r["rank"], r["law"]))
        fms = [self.failure(f) for f in sorted(fm_hit, key=lambda f: (-fm_hit[f], self.n[f]["n"]))]
        return {"terms": terms, "laws": laws, "failure_modes": fms}

    def failure(self, fid):
        n = self.n[fid]
        laws = sorted({self.n[x]["n"] for x in self.out[fid]["fixedByLaw"] + self.inc[fid]["paidForBy"]
                       + [o for o in self.out[fid]["mentions"] if o.startswith("law/")]})
        return {"failure_mode": n["n"], "failure": n["failure"], "fix": n["fix"],
                "class": [self.n[c]["label"] for c in self.out[fid]["inClass"]], "laws": laws,
                "traps": sorted(self.n[t]["label"] for t in self.out[fid]["hasTrap"]),
                "diagnostics": sorted(self.n[d]["label"] for d in self.out[fid]["caughtBy"]),
                "recurred_as": [self.n[o]["n"] for o in self.out[fid]["recurredAs"]],
                "source": n.get("sourceText"), "at": n["definedAt"]}

    def what_broke(self, pattern):
        rx = re.compile(pattern, re.I)
        return {"pattern": pattern, "failure_modes": [
            self.failure(n["id"]) for n in sorted(self.of("FailureMode"), key=lambda n: n["n"])
            if rx.search(n["failure"]) or rx.search(n["fix"])]}

    # ---- how-do-we-know -------------------------------------------------------------------------
    def footing(self, nid):
        pins, tools = set(self.out[nid]["atPin"]), set(self.out[nid]["usesTool"])
        for i in self.out[nid]["resolvedInstrument"]:
            pins |= set(self.out[i]["atPin"])
            tools |= set(self.out[i]["usesTool"])
        return sorted(self.n[p]["label"] for p in pins), sorted(self.n[t]["label"] for t in tools)

    def claims(self, nid):
        return [{"value": json.loads(self.n[c]["claimValue"]), "verdict": self.n[c]["verdict"],
                 "quote": self.n[c].get("quote"), "source": self.n[c].get("sourceRef"),
                 "line": self.n[c].get("quoteLine")} for c in sorted(self.inc[nid]["supports"])]

    def how_do_we_know(self, ref):
        nid = self.resolve(ref)
        if not nid:
            return {"error": f"no node for {ref!r}"}
        n = self.n[nid]
        chapter = [self.n[c]["label"] for c in self.out[nid]["inChapter"]]
        cited_by = sorted({self.n[s]["label"].split()[0] for p in ("evidencedBy", "mentions") for s in self.inc[nid][p]
                           if self.n[s]["type"] in ("Heuristic", "Drill", "Number")})
        if n["type"] == "Number":
            pins, tools = self.footing(nid)
            claims = self.claims(nid)
            resolved = [self.n[i]["asWritten"] for i in self.out[nid]["resolvedInstrument"]]
            caveats = []
            if n.get("instrumentResolution") != "as written":
                caveats.append("the instrument is written as a pointer ('same'); the Atlas took the nearest explicit row above")
            if not pins and not any(re.search(r"\d", t) for t in tools):
                caveats.append("no pin and no versioned tool could be read from the instrument string")
            if not claims:
                caveats.append("no ledger quote: the value has not been checked against a source by the claim checker")
            elif not any(c["verdict"] == "verified" for c in claims):
                caveats.append("a ledger quote exists but none is verified")
            if self.out[nid]["carriedFrom"]:
                caveats.append("carried from " + ", ".join(self.n[o]["label"] for o in self.out[nid]["carriedFrom"]))
            if self.grade(nid) != "C":
                caveats.append(f"grade {self.grade(nid)}: not measured by a named tool")
            return {"id": n["label"], "quantity": n["quantity"], "value": n["value"], "grade": self.grade(nid),
                    "chapter": chapter, "instrument_as_written": n["instrumentText"],
                    "instrument_resolution": n.get("instrumentResolution"), "stands_on_instrument": resolved,
                    "pins": pins, "tools": tools, "source": n.get("sourceCell"), "run": n.get("runDate"),
                    "ledger_quotes": claims, "cited_by": cited_by, "caveats": caveats, "at": n["definedAt"]}
        if n["type"] == "Heuristic":
            ev = []
            for o in self.out[nid]["evidencedBy"]:
                t = self.n[o]
                ev.append({"id": t["label"].split(":")[0], "value": t.get("value"), "grade": self.grade(o)}
                          if t["type"] == "Number" else {"id": t["label"]})
            caveats = [] if ev else ["the evidence column cites no stable id; it is prose the graph cannot follow"]
            return {"id": n["label"], "rule": n["rule"], "grade": self.grade(nid), "chapter": chapter,
                    "evidence_as_written": n["evidence"], "evidence_followed": ev, "instrument": n.get("instrumentText"),
                    "ledger_quotes": self.claims(nid), "caveats": caveats, "at": n["definedAt"]}
        if n["type"] == "Drill":
            return {"id": n["label"], "level": n.get("level"), "status": n["status"], "checked": n.get("checkedText"),
                    "chapter": chapter, "task": n.get("task"), "verify": n.get("verify"), "at": n["definedAt"]}
        if n["type"] == "Law":
            fms = sorted(self.law_failures(nid), key=lambda f: self.n[f]["n"])
            return {"id": n["label"], "forbids": n.get("forbids"), "paid_for_by": n.get("paidForByText"),
                    "theme": [self.n[t]["label"] for t in self.out[nid]["inTheme"]],
                    "failure_modes": [{"n": self.n[f]["n"], "failure": self.n[f]["failure"][:140]} for f in fms],
                    "check": n.get("checkText"), "mechanical": n.get("checkKind") == "code",
                    "diagnostics": sorted(self.n[d]["label"] for d in self.out[nid]["caughtBy"]),
                    "sources": sorted(self.n[s]["label"] for s in self.out[nid]["citesSource"]),
                    "caveats": [] if fms else ["cites no failure mode by number; its incidents are named in prose"],
                    "at": n["definedAt"]}
        if n["type"] == "FailureMode":
            return self.failure(nid)
        return {k: v for k, v in n.items() if k not in ("type",)}

    # ---- stands-on ------------------------------------------------------------------------------
    def stands_on(self, what):
        key = what.strip().lower()
        hits = collections.defaultdict(list)
        for n in self.of("Number"):
            pins, tools = self.footing(n["id"])
            for label in pins + tools:
                if key == label.lower() or (key in label.lower() and len(key) > 3):
                    hits[label].append(n["label"])
        return {"asked": what, "numbers": {k: sorted(v, key=lambda s: (s.split("-")[1], int(s.split("-")[2])))
                                           for k, v in sorted(hits.items())},
                "total": len({x for v in hits.values() for x in v})}

    # ---- worklist -------------------------------------------------------------------------------
    def worklist(self):
        f = json.loads((HERE / "out" / "findings.json").read_text(encoding="utf-8"))
        t = f["traceability"]
        return {
            "numbers without a verified ledger quote": t["numbers"] - t["numbers with a verified quote"],
            "chapters with no claim ledger": sorted(set(n["label"][:2] for n in self.of("Chapter")) - set(t["chapters with a ledger"])),
            "numbers whose instrument is a pointer": f["number instruments"].get("inferred from the row above", 0),
            "Confirmed numbers with no pin and no versioned tool": f["Confirmed numbers with no pin and no versioned tool in their instrument"]["count"],
            "failure modes linked to no law": f["failure modes linked to no law"]["count"],
            "laws that cite no failure mode by number": f["laws with no failure mode cited by number"],
            "laws with no mechanical check, by failures": [[r["law"], r["failure modes"]] for r in f["process-only laws ranked by failures"]],
            "heuristics whose evidence cites no id": f["heuristics whose evidence cites no id"]["by grade"],
            "drills not run": f["drills not run"],
            "X_ITE versions under the numbers": f["tool versions under the numbers"].get("X_ITE"),
            "source text to fix": f["findings"],
        }

    def stats(self):
        return {"inputs": self.meta["inputs"], "counts": self.meta["counts"], "edges": self.meta["edges"]}


def show(obj, indent=0):
    pad = "  " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                print(f"{pad}{k}:")
                show(v, indent + 1)
            else:
                print(f"{pad}{k}: {v if v not in ([], {}, None) else '-'}")
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, dict):
                show(v, indent)
                print()
            else:
                print(f"{pad}- {v}")
    else:
        print(f"{pad}{obj}")


def main(argv):
    as_json = "--json" in argv
    args = [a for a in argv if a != "--json"]
    if not args:
        print(__doc__)
        return 2
    A = Atlas()
    cmd, rest = args[0], args[1:]
    if cmd == "stats":
        r = A.stats()
    elif cmd == "laws-for" and rest:
        r = A.laws_for(rest)
    elif cmd == "what-broke" and rest:
        r = A.what_broke(rest[0])
    elif cmd == "how-do-we-know" and rest:
        r = A.how_do_we_know(" ".join(rest))
    elif cmd == "stands-on" and rest:
        r = A.stands_on(" ".join(rest))
    elif cmd == "worklist":
        r = A.worklist()
    else:
        print(__doc__)
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=1) if as_json else "", end="\n" if as_json else "")
    if not as_json:
        show(r)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
