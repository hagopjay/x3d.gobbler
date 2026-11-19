"""The AI Engineering Atlas as Gobbler.flyte's library: what the Assayer knows, mapped onto the world's ontology.

Source: flyte/atlas/aie-atlas.json, the DATA block of "AI_Engineering_Atlas.html" (rev 28, 2026-10-20), which
HagopJay supplied on 19 Nov 2026 as the content for the "Chip Huyen AI Engineering agent". The atlas is an
agent-written catalogue of Chip Huyen's AI Engineering (O'Reilly, 2024) and the chiphuyen/aie-book repo:
129 sources, 218 concepts, 67 code sketches, 51 gaps and conflicts, 16 themes, 13 theses. The file is pinned
by SHA-256; a test fails if it drifts.

Two stores, two ontologies, kept apart on purpose:
  * THE WORLD's memory (memory.sqlite): experience. Refusals, admissions, decisions, made by trusted organ code.
  * The library (library.sqlite): knowledge. Atlas sources become evidence refs, concepts become semantic
    claims, theses and code sketches become procedures, gaps become open questions. Only the Assayer reads it,
    so 400-odd library rows never crowd Weaver's context or its exclusion list.

Grades are inherited honestly: a claim is L when at least one of its sources was read by the atlas agent
(status v or a), else S. Nothing in the library is C: no Gobbler instrument ran on it.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .memory import EvidenceRef, MemoryRecord, MemoryStore

HERE = Path(__file__).resolve().parents[1]
ATLAS = HERE / "atlas" / "aie-atlas.json"
ATLAS_SHA256 = "b8717094e21eb003c70a4cb5114d40acd6d3fbca810654b608a88dc058b7d57b"
READ = {"v", "a"}                                  # atlas status codes for "read" and "abstract read"

# Where each Atlas theme lives in Gobbler.flyte. "built" = code in this repo exercises it today; "ready" = a named
# hook exists and the next step is small; "later" = needs a model call, a second machine or a human; "n/a" = the
# theme is about training or serving models, which this loop does not do.
ONTOLOGY = {
    "rl":      {"home": "Weaver retry loop", "kinds": ["procedure"], "status": "built",
                "how": "retries are capped at 3 and a deterministic generator takes over, so a task the model cannot solve never rewards a hack (T13)"},
    "hack":    {"home": "Witness + Assayer canary", "kinds": ["counterexample", "procedure"], "status": "built",
                "how": "Weaver sees refusal codes, never the grader's source; a daily canary feeds known-bad fragments to the same instruments (T2, T8)"},
    "evalsec": {"home": "Assayer stop-the-line", "kinds": ["decision", "open_question"], "status": "built",
                "how": "a failed critical check writes STOP-THE-LINE.json and the runner starts no new cycle until a human clears it (T12)"},
    "sec":     {"home": "Scout + Weaver quoting", "kinds": ["procedure"], "status": "built",
                "how": "web text reaches the model quoted and linted (untrusted.py); Scout fetches only configured source ids (T7)"},
    "reason":  {"home": "budget.py", "kinds": ["experiment"], "status": "ready",
                "how": "effort is pinned low and every call is priced; cost-aware reporting needs real calls"},
    "mem":     {"home": "memory.py", "kinds": ["episode", "counterexample", "decision"], "status": "built",
                "how": "nine kinds, filter before rank, sealed hold-out with an audit (T11)"},
    "agev":    {"home": "Assayer daily report", "kinds": ["experiment"], "status": "built",
                "how": "pass@k and pass^k over cycles (Atlas K5), most frequent refusal code, and outcomes read from the world store, not from the agent (T3, T4)"},
    "judge":   {"home": "none yet (no model judge)", "kinds": ["experiment"], "status": "later",
                "how": "the loop's graders are code; a model judge would need kappa against his labels and a swap test (Atlas K6) first (T5)"},
    "bench":   {"home": "sealed bucket + instrument pins", "kinds": ["counterexample"], "status": "built",
                "how": "about 1 in 5 refusals is held out; every score carries dated instrument pins and the Assayer flags pins older than 30 days (T6)"},
    "evalops": {"home": "Assayer", "kinds": ["experiment", "summary"], "status": "built",
                "how": "every cycle is assayed against the theses; the day gets a report with sources named"},
    "rag":     {"home": "compile_context ranking", "kinds": ["semantic_claim"], "status": "ready",
                "how": "ranking is lexical today; reciprocal rank fusion (Atlas K2) is the next step once there is a second ranker"},
    "agdes":   {"home": "gobbler.py graph", "kinds": ["procedure"], "status": "built",
                "how": "one thread per cycle, interrupts for humans, state in SQLite and files, not in the prompt (T11)"},
    "ft":      {"home": "n/a", "kinds": [], "status": "n/a", "how": "the loop does not finetune"},
    "serve":   {"home": "n/a", "kinds": [], "status": "n/a", "how": "the loop calls a hosted model; latency is not on its critical path"},
    "found":   {"home": "llm.py", "kinds": ["procedure"], "status": "ready",
                "how": "structured output is enforced by the WeaverCandidate contract; sampling settings are pinned in config"},
    "prod":    {"home": "council + HITL + foldback", "kinds": ["decision"], "status": "built",
                "how": "council stand-up, GitHub Issues questions with a 4 h timeout, foldback drafts counted apart from reuse"},
}

# Thesis -> the Assayer checks that test it in this loop (names in organs/assayer.py), or why none can yet.
THESIS_CHECKS = {
    "T1": ["score_tuple"], "T2": ["canary"], "T3": ["state_of_record"], "T4": ["daily:pass_hat_k"],
    "T5": [], "T6": ["pin_age"], "T7": ["egress"], "T8": ["grader_opacity"], "T9": [],
    "T10": ["provenance"], "T11": ["context_budget"], "T12": ["stop_the_line"], "T13": ["retry_cap"],
}
NOT_TESTED = {"T5": "no model judge in the loop yet", "T9": "one demiurge, not a swarm: organs share no writable channel but the state"}


def load(path: Path = ATLAS, *, verify: bool = True) -> dict:
    raw = Path(path).read_bytes()
    if verify and hashlib.sha256(raw).hexdigest() != ATLAS_SHA256:
        raise ValueError("aie-atlas.json bytes changed; re-pin ATLAS_SHA256 only with a new provenance note")
    return json.loads(raw)


def theme_of(atlas: dict, row: list, kind: str, kref: dict | None = None) -> str:
    """The atlas page's own themeOf(), ported: overrides, then meta chapters, then the first theme whose tags match."""
    override = {"K8": "agev", "c83": "evalsec", "c91": "evalsec", "K28": "evalsec", "K31": "evalsec"}
    if row[0] in override:
        return override[row[0]]
    chapter = row[2] if kind == "S" else row[1]
    if kind != "K" and chapter in ("x", "b"):
        return "meta"
    tags = row[6] if kind == "S" else row[5] if kind == "N" else ((kref or {}).get(row[0]) or [""] * 6)[5]
    have = set(tags.split(","))
    for t in atlas["THEMES"]:
        pos = [x for x in t[3] if not x.startswith("!")]
        neg = [x[1:] for x in t[3] if x.startswith("!")]
        if any(x in have for x in pos) and not any(x in have for x in neg):
            return t[0]
    return "misc"


def kref(atlas: dict) -> dict:
    import re
    out = {}
    for n in atlas["N"]:
        for k in re.findall(r"K\d+", n[3]):
            out.setdefault(k, n)
    return out


def theme_counts(atlas: dict) -> dict:
    kr = kref(atlas)
    counts: dict[str, dict[str, int]] = {}
    for kind, rows in (("S", atlas["S"]), ("N", atlas["N"]), ("K", atlas["K"])):
        for r in rows:
            t = theme_of(atlas, r, kind, kr)
            counts.setdefault(t, {"S": 0, "N": 0, "K": 0})[kind] += 1
    return counts


def _sha(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def seed_library(store: MemoryStore, atlas: dict | None = None) -> dict:
    """Idempotent: every row has a fixed id, so a second seed writes nothing."""
    atlas = atlas or load()
    t0 = f"{atlas['date']}T00:00:00Z"
    status = {s[0]: s[7] for s in atlas["S"]}
    rev = atlas["rev"]
    wrote = {"evidence": 0, "semantic_claim": 0, "procedure": 0, "open_question": 0}
    for s in atlas["S"]:
        before = store.evidence(f"aie:{s[0]}")
        store.put_evidence(EvidenceRef(evidence_id=f"aie:{s[0]}", exposure="development", sha256=_sha(s),
                                       instrument=f"AI Engineering Atlas rev {rev}, source status {s[7]}"))
        wrote["evidence"] += before is None
    concept_ids = set()
    for n in atlas["N"]:
        cites = [f"aie:{x.strip()}" for x in n[4].split(",") if x.strip() in status]
        level = "L" if any(status[c[4:]] in READ for c in cites) else "S"
        rec = MemoryRecord(memory_id=f"aie:{n[0]}", kind="semantic_claim", text=f"{n[2]}. {n[3]}"[:4000], readers=["assayer"],
                           evidence_ids=cites[:50], evidence_level=level, valid_from=t0, recorded_by="library",
                           subject_sha256=_sha(n))
        wrote["semantic_claim"] += store.put_once(rec)
        concept_ids.add(n[0])
    for t in atlas["THESES"]:
        parents = [f"aie:{c}" for c in t[3] if c in concept_ids]
        rec = MemoryRecord(memory_id=f"aie:{t[0]}", kind="procedure", text=f"{t[1]}. {t[2]} Rule: {t[4]}"[:4000],
                           readers=["assayer"], parent_ids=parents, evidence_level="L", valid_from=t0, recorded_by="library",
                           subject_sha256=_sha(t))
        wrote["procedure"] += store.put_once(rec)
    for k in atlas["K"]:
        rec = MemoryRecord(memory_id=f"aie:{k[0]}", kind="procedure", text=f"Code sketch {k[0]}, {k[2]}: {k[3]}"[:4000],
                           readers=["assayer"], evidence_level="S", valid_from=t0, recorded_by="library", subject_sha256=_sha(k))
        wrote["procedure"] += store.put_once(rec)
    for g in atlas["G"]:
        rec = MemoryRecord(memory_id=f"aie:{g[0]}", kind="open_question", text=f"Atlas {g[1]}: {g[2]}"[:4000], readers=["assayer"],
                           evidence_level="S", valid_from=t0, recorded_by="library", subject_sha256=_sha(g))
        wrote["open_question"] += store.put_once(rec)
    return wrote


def thesis(atlas: dict, tid: str) -> dict:
    t = next(x for x in atlas["THESES"] if x[0] == tid)
    return {"id": t[0], "title": t[1], "rule": t[4], "concepts": t[3]}
