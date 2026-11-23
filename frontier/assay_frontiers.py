#!/usr/bin/env python3
"""The Assayer's frontier lens: put every candidate frontier for the Loom through the Atlas's thirteen theses.

    python3 frontier/assay_frontiers.py --out frontier/runs/<name> [--repos /path/to/checkouts]

Deterministic, no model call, no network; standard library plus this repo's Atlas loader. The registry (frontiers.json) is hand-written:
its five judged scores are opinions and stay graded Suspected. What this tool adds is everything that can be
computed: one check per thesis from each frontier's declared grader and flags, the evidence paths looked up on
disk, a readiness fraction, a ranking under five weightings, and a seeded perturbation run that says how far each
rank moves when the opinions are wrong by a point (thesis T4: reliability is a distribution).

    thesis  check            asks of a frontier                                          worst outcome
    T1      score_tuple      is the grader a named instrument that can be pinned          warn
    T2      canary           do known-bad controls exist naturally                        warn
    T3      state_of_record  is the outcome read from an artefact, not from a narrative   gate
    T4      repeatable       can one trial be repeated from a seed                        warn
    T5      judge_validity   a human or model judge needs kappa against labels first      gate
    T6      holdout          can a private slice be kept                                  warn
    T7      egress           outside data: none, open licence, or restricted              stop
    T8      grader_gaming    an optimiser in the loop needs controls and a hold-out       stop
    T9      swarm            more than one agent sharing a channel                        warn
    T10     provenance       prior evidence found on disk, by path                        note
    T11     budget           does the first step need a paid or GPU model call            gate
    T13     effort_cap       an optimiser needs a generation cap written before it runs   warn

T12 (stop the line) is the tool's own behaviour: a `stop` is never averaged away, it is printed beside the rank.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "flyte"))
from gobbler_flyte import atlas as atlas_mod  # noqa: E402

AXES = ("relevance", "flywheel", "gravitas", "visual", "effort")
LENSES = {
    "balanced":       {"flywheel": .30, "relevance": .20, "visual": .20, "gravitas": .15, "effort": .15},
    "flywheel-first": {"flywheel": .50, "relevance": .20, "visual": .10, "gravitas": .10, "effort": .10},
    "showpiece":      {"flywheel": .15, "relevance": .10, "visual": .45, "gravitas": .25, "effort": .05},
    "gravitas":       {"flywheel": .20, "relevance": .20, "visual": .10, "gravitas": .45, "effort": .05},
    "quick-win":      {"flywheel": .30, "relevance": .20, "visual": .05, "gravitas": .05, "effort": .40},
}
CODE_KINDS = {"code", "reference", "cross-impl"}
KINDS = CODE_KINDS | {"human", "model"}
STATUSES = ("unexplored", "touched", "explored", "deep")
DRAWS, SEED, HELD_SEED = 2000, 7, 23


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _c(thesis: str, name: str, status: str, detail: str) -> dict:
    return {"thesis": thesis, "check": name, "status": status, "detail": detail}


def assay(f: dict, repos: Path | None) -> dict:
    g, fl = f["grader"], f["flags"]
    coded = g["kind"] in CODE_KINDS
    cs = [
        _c("T1", "score_tuple", "pass" if coded and g["name"].strip() else "warn",
           f"instrument: {g['name']}" if coded else f"the grader is a {g['kind']}, which cannot be pinned by hash"),
        _c("T2", "canary", "pass" if fl["neg_controls"] else "warn",
           "known-bad controls exist" if fl["neg_controls"] else "no natural known-bad control: plant some first"),
        _c("T3", "state_of_record", "pass" if coded else "gate",
           "outcome is read from an artefact" if coded else f"outcome is a {g['kind']} opinion: record it as labels, never as a grade"),
        _c("T4", "repeatable", "pass" if fl["seeded"] else "warn",
           "a trial repeats from a seed" if fl["seeded"] else "trials cannot be repeated exactly"),
        _c("T5", "judge_validity", "n/a" if coded else "gate",
           "no judge in the loop" if coded else "measure Cohen's kappa and a position swap against about 30 of his labels before it grades anything (Atlas sketch K6)"),
        _c("T6", "holdout", "pass" if fl["holdout"] else "warn",
           "a private slice can be kept" if fl["holdout"] else "no hold-out possible: every score will age in public"),
    ]
    if fl["data_restricted"]:
        cs.append(_c("T7", "egress", "stop", "restricted outside data or licence: needs his decision before any byte is fetched"))
    elif fl["data_open"]:
        cs.append(_c("T7", "egress", "warn", "open-licence outside data: attribution file, links and a takedown notice ship with the demo"))
    else:
        cs.append(_c("T7", "egress", "pass", "no outside data"))
    if fl["optimizer"]:
        ok = fl["neg_controls"] and fl["holdout"]
        cs.append(_c("T8", "grader_gaming", "warn" if ok else "stop",
                     "an optimiser faces the grader: keep one judge hidden from it and re-run the canary each generation" if ok
                     else "an optimiser faces a grader with no controls or no hold-out: it will learn the grader, not the task"))
        cs.append(_c("T13", "effort_cap", "warn", "write the generation and retry caps before the first run"))
    else:
        cs.append(_c("T8", "grader_gaming", "n/a", "nothing optimises against the grader"))
        cs.append(_c("T13", "effort_cap", "n/a", "no search loop"))
    cs.append(_c("T9", "swarm", "warn" if fl["swarm"] else "n/a",
                 "several agents share a channel: peer-instruction authority is untested here" if fl["swarm"] else "one agent"))
    found = missing = None
    if repos is not None:
        found = [e for e in f["evidence"] if (repos / e.split(":", 1)[0] / e.split(":", 1)[1]).exists()]
        missing = [e for e in f["evidence"] if e not in found]
    n = len(f["evidence"])
    cs.append(_c("T10", "provenance", "pass" if n else "note",
                 (f"{n} prior path(s) cited" + ("" if found is None else f", {len(found)} found on disk")) if n else "no prior work cited: everything here is opinion"))
    if fl["model_required"]:
        cs.append(_c("T11", "budget", "gate", "the first step needs a paid or GPU model call: his typed spend OK first"))
    else:
        cs.append(_c("T11", "budget", "pass", "first step runs with no model call" + (" (a model is optional later)" if fl["model_optional"] else "")))
    applicable = [c for c in cs if c["status"] != "n/a"]
    passed = [c for c in applicable if c["status"] == "pass"]
    worst = next((s for s in ("stop", "gate", "warn", "note") if any(c["status"] == s for c in cs)), "pass")
    return {"checks": cs, "readiness": round(len(passed) / len(applicable), 4), "passed": len(passed),
            "applicable": len(applicable), "worst": worst,
            "gates": [f"{c['thesis']}: {c['detail']}" for c in cs if c["status"] in ("stop", "gate")],
            "evidence_found": found, "evidence_missing": missing}


def composite(judged: dict, readiness: float, w: dict) -> float:
    base = sum(w[a] * ((6 - judged[a]) if a == "effort" else judged[a]) for a in AXES) / 5
    return 100 * base * (0.7 + 0.3 * readiness)


def rank(ids: list[str], scores: dict[str, float]) -> dict[str, int]:
    order = sorted(ids, key=lambda i: (-scores[i], i))
    return {i: n + 1 for n, i in enumerate(order)}


def perturb(fr: list[dict], ready: dict, seed: int, draws: int = DRAWS) -> dict:
    """Each judged score moves -1, 0 or +1 (odds 1:2:1, clamped to 1..5); each weight moves up to 30 percent."""
    rng = random.Random(seed)
    ids = [f["id"] for f in fr]
    ranks = {i: [] for i in ids}
    for _ in range(draws):
        w = {a: v * rng.uniform(0.7, 1.3) for a, v in LENSES["balanced"].items()}
        t = sum(w.values()); w = {a: v / t for a, v in w.items()}
        sc = {}
        for f in fr:
            j = {a: min(5, max(1, f["judged"][a] + rng.choice((-1, 0, 0, 1)))) for a in AXES}
            sc[f["id"]] = composite(j, ready[f["id"]], w)
        for i, r in rank(ids, sc).items():
            ranks[i].append(r)
    out = {}
    for i, rs in ranks.items():
        rs.sort()
        out[i] = {"p05": rs[int(.05 * draws)], "p50": rs[draws // 2], "p95": rs[int(.95 * draws) - 1],
                  "top5": round(sum(r <= 5 for r in rs) / draws, 4), "top10": round(sum(r <= 10 for r in rs) / draws, 4)}
    return out


def validate_registry(reg: dict, themes: set[str]) -> list[str]:
    errs, seen = [], set()
    for f in reg["frontiers"]:
        i = f.get("id", "?")
        if i in seen: errs.append(f"{i}: duplicate id")
        seen.add(i)
        if f["family"] not in reg["families"]: errs.append(f"{i}: unknown family")
        if f["status"] not in STATUSES: errs.append(f"{i}: unknown status")
        if f["grader"]["kind"] not in KINDS: errs.append(f"{i}: unknown grader kind")
        if set(f["judged"]) != set(AXES) or any(type(v) is not int or not 1 <= v <= 5 for v in f["judged"].values()):
            errs.append(f"{i}: judged scores must be the five axes, integers 1..5")
        if f["flags"]["data_open"] and f["flags"]["data_restricted"]: errs.append(f"{i}: data both open and restricted")
        if f["flags"]["model_required"] and f["flags"]["model_optional"]: errs.append(f"{i}: model both required and optional")
        for t in f["atlas_themes"]:
            if t not in themes: errs.append(f"{i}: atlas theme {t!r} is not in the Atlas")
        if f["status"] == "unexplored" and len(f["evidence"]) > 2: errs.append(f"{i}: called unexplored but cites {len(f['evidence'])} paths")
        if f["status"] in ("explored", "deep") and not f["evidence"]: errs.append(f"{i}: called {f['status']} with no evidence path")
    return errs


def git_head(p: Path) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(p), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10).stdout.strip() or None
    except Exception:
        return None


def run(registry: Path, repos: Path | None) -> dict:
    raw = registry.read_bytes()
    reg = json.loads(raw)
    at = atlas_mod.load()
    tc = atlas_mod.theme_counts(at)
    theses = {t[0]: {"title": t[1], "rule": t[4]} for t in at["THESES"]}
    errs = validate_registry(reg, {t[0] for t in at["THEMES"]})
    if errs:
        raise SystemExit("registry refused:\n  " + "\n  ".join(errs))
    fr = reg["frontiers"]
    ids = [f["id"] for f in fr]
    res = {f["id"]: assay(f, repos) for f in fr}
    missing = {i: r["evidence_missing"] for i, r in res.items() if r["evidence_missing"]}
    ready = {i: res[i]["readiness"] for i in ids}
    lens_scores = {L: {f["id"]: round(composite(f["judged"], ready[f["id"]], w), 2) for f in fr} for L, w in LENSES.items()}
    lens_ranks = {L: rank(ids, s) for L, s in lens_scores.items()}
    mc, mc_held = perturb(fr, ready, SEED), perturb(fr, ready, HELD_SEED)
    rows = []
    for f in fr:
        i = f["id"]
        counts = {"sources": 0, "concepts": 0, "sketches": 0}
        for t in f["atlas_themes"]:
            c = tc.get(t, {})
            counts["sources"] += c.get("S", 0); counts["concepts"] += c.get("N", 0); counts["sketches"] += c.get("K", 0)
        rows.append({"id": i, "family": f["family"], "status": f["status"], "title": f["title"], "gain": f["gain"],
                     "first_step": f["first_step"], "judged": f["judged"], "grader": f["grader"], "flags": f["flags"],
                     "atlas_themes": f["atlas_themes"], "atlas_rows": counts, "evidence": f["evidence"],
                     "assay": res[i], "score": lens_scores["balanced"][i], "rank": lens_ranks["balanced"][i],
                     "lens_rank": {L: lens_ranks[L][i] for L in LENSES}, "perturbation": mc[i]})
    rows.sort(key=lambda r: r["rank"])
    top10 = lambda m: sorted(sorted(ids, key=lambda i: (m[i]["p50"], -m[i]["top10"], i))[:10])
    a, b = top10(mc), top10(mc_held)
    repo_heads = {}
    if repos is not None:
        for name in sorted({e.split(":", 1)[0] for f in fr for e in f["evidence"]} | {"x3d.gobbler"}):
            repo_heads[name] = git_head(repos / name)
    fam, sta, worst = {}, {}, {}
    for r in rows:
        fam[r["family"]] = fam.get(r["family"], 0) + 1
        sta[r["status"]] = sta.get(r["status"], 0) + 1
        worst[r["assay"]["worst"]] = worst.get(r["assay"]["worst"], 0) + 1
    return {
        "schema": "gobbler.frontier-board/1",
        "score_tuple": {
            "tool": "frontier/assay_frontiers.py", "tool_sha256": sha(Path(__file__).read_bytes()),
            "registry_sha256": sha(raw), "registry_date": reg["date"],
            "atlas_rev": at["rev"], "atlas_sha256": atlas_mod.ATLAS_SHA256,
            "lenses": LENSES, "readiness_factor": "0.7 + 0.3 * readiness", "draws": DRAWS, "seed": SEED,
            "held_seed": HELD_SEED, "python": platform.python_version(), "model_calls": 0, "spend_usd": 0,
            "repo_heads": repo_heads,
            "grade": "Suspected for every judged score and rank; Confirmed only for the counts this tool computed",
        },
        "theses": theses, "families": reg["families"],
        "counts": {"frontiers": len(rows), "by_family": fam, "by_status": sta, "by_worst_check": worst,
                   "evidence_paths": sum(len(f["evidence"]) for f in fr),
                   "evidence_missing": sum(len(v) for v in missing.values()) if repos is not None else None,
                   "first_step_needs_no_model": sum(not f["flags"]["model_required"] for f in fr)},
        "stability": {"top10_seed": a, "top10_held_seed": b, "overlap": len(set(a) & set(b))},
        "evidence_missing": missing, "rows": rows,
    }


def board_md(b: dict) -> str:
    t = b["score_tuple"]; c = b["counts"]
    L = ["# The Loom frontier board", "",
         f"Assayed {c['frontiers']} frontiers against the AI Engineering Atlas rev {t['atlas_rev']} "
         f"(`{t['atlas_sha256'][:12]}`), registry `{t['registry_sha256'][:12]}`, tool `{t['tool_sha256'][:12]}`, "
         f"Python {t['python']}, {t['model_calls']} model calls, ${t['spend_usd']}. "
         "Judged scores and ranks are graded Suspected (one model's opinion); the check counts are computed.", "",
         "Score = 100 x weighted mean of the five judged axes (effort inverted) x (0.7 + 0.3 x readiness). "
         f"Rank range = 5th to 95th percentile over {t['draws']} seeded perturbations (seed {t['seed']}).", "",
         "| # | Frontier | Fam | State | Rel | Fly | Grav | Vis | Eff | Ready | Worst | Score | Rank range | In top 10 |",
         "|--:|---|:-:|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|--:|:-:|--:|"]
    for r in b["rows"]:
        j, a, p = r["judged"], r["assay"], r["perturbation"]
        L.append(f"| {r['rank']} | **{r['title']}** (`{r['id']}`) | {r['family']} | {r['status']} | {j['relevance']} | {j['flywheel']} | "
                 f"{j['gravitas']} | {j['visual']} | {j['effort']} | {a['passed']}/{a['applicable']} | {a['worst']} | {r['score']:.1f} | "
                 f"{p['p05']} to {p['p95']} | {100 * p['top10']:.0f}% |")
    L += ["", "## Gates before starting", ""]
    for r in b["rows"]:
        if r["assay"]["gates"]:
            L.append(f"- **{r['id']}** (rank {r['rank']}): " + "; ".join(r["assay"]["gates"]))
    L += ["", "## First steps, top 15", ""]
    for r in b["rows"][:15]:
        L.append(f"{r['rank']}. **{r['title']}**. {r['gain']} *First step:* {r['first_step']} *Grader:* {r['grader']['name']}.")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--registry", type=Path, default=HERE / "frontiers.json")
    ap.add_argument("--repos", type=Path, default=None, help="folder holding the sibling checkouts; evidence paths are looked up there")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    b = run(a.registry, a.repos)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "board.json").write_text(json.dumps(b, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (a.out / "BOARD.md").write_text(board_md(b), encoding="utf-8")
    c = b["counts"]
    print(f"frontiers {c['frontiers']}  families {c['by_family']}  states {c['by_status']}")
    print(f"worst check {c['by_worst_check']}  evidence paths {c['evidence_paths']} missing {c['evidence_missing']}")
    print(f"top-10 overlap between seed {SEED} and held seed {HELD_SEED}: {b['stability']['overlap']}/10")
    for r in b["rows"][:20]:
        p = r["perturbation"]
        print(f"{r['rank']:>2} {r['score']:5.1f} {r['family']} {r['assay']['passed']}/{r['assay']['applicable']} {r['assay']['worst']:<5} "
              f"[{p['p05']:>2}-{p['p95']:>2}] top10 {100 * p['top10']:3.0f}%  {r['id']}")
    return 1 if b["evidence_missing"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
