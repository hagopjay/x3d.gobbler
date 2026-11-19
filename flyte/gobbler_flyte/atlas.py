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

Concept grades are attributed to the catalogue: L means it self-reports a cited source as read
(status v or a), else S. Gobbler has not independently read those sources. A thesis inherits the weakest
grade among its cited concepts. Nothing in the library is C: no Gobbler instrument ran on it.
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

# Where a local mechanism related to each theme lives. "built" does not establish the theme's theses.
# "built" = code in this repo exercises a local mechanism today; "ready" = a named
# hook exists and the next step is small; "later" = needs a model call, a second machine or a human; "n/a" = the
# theme is about training or serving models, which this loop does not do.
ONTOLOGY = {
    "rl":      {"home": "Weaver retry loop", "kinds": ["procedure"], "status": "built",
                "how": "bounded retries and deterministic fallback implement effort control; no RL training or misbehavior measurement is performed (T13)"},
    "hack":    {"home": "Witness + Assayer canary", "kinds": ["counterexample", "procedure"], "status": "built",
                "how": "admitted development feedback and instrument-bound gate/validator/trap canaries; contamination is checked, grader gaming remains unmeasured (T2, T8)"},
    "evalsec": {"home": "Assayer stop-the-line", "kinds": ["decision", "open_question"], "status": "built",
                "how": "a failed critical check writes STOP-THE-LINE.json and the runner starts no new cycle until a human clears it (T12)"},
    "sec":     {"home": "Scout + Weaver quoting", "kinds": ["procedure"], "status": "built",
                "how": "web text reaches the model quoted and linted (untrusted.py); Scout fetches only configured source ids (T7)"},
    "reason":  {"home": "budget.py", "kinds": ["experiment"], "status": "ready",
                "how": "effort is pinned low and every call is priced; cost-aware reporting needs real calls"},
    "mem":     {"home": "memory.py", "kinds": ["episode", "counterexample", "decision"], "status": "built",
                "how": "nine kinds, filter before rank, sealed hold-out with an audit (T11)"},
    "agev":    {"home": "Assayer daily report", "kinds": ["experiment"], "status": "built",
                "how": "descriptive attempt fractions and first-attempt turn outcomes; repeated-signal reliability remains unmeasured (T3, T4)"},
    "judge":   {"home": "none yet (no model judge)", "kinds": ["experiment"], "status": "later",
                "how": "the loop's graders are code; a model judge would need kappa against his labels and a swap test (Atlas K6) first (T5)"},
    "bench":   {"home": "sealed bucket + instrument pins", "kinds": ["counterexample"], "status": "built",
                "how": "about 1 in 5 refusals is held out; every score carries dated instrument pins and the Assayer flags pins older than 30 days (T6)"},
    "evalops": {"home": "Assayer", "kinds": ["experiment", "summary"], "status": "built",
                "how": "every cycle is assayed against the theses; the day gets a report with sources named"},
    "rag":     {"home": "compile_context ranking", "kinds": ["semantic_claim"], "status": "ready",
                "how": "ranking is lexical today; reciprocal rank fusion (Atlas K2) is the next step once there is a second ranker"},
    "agdes":   {"home": "gobbler.py graph", "kinds": ["procedure"], "status": "built",
                "how": "one checkpointed thread per cycle, human interrupts and bounded compiled context; broader protocol effectiveness is not established (T11)"},
    "ft":      {"home": "n/a", "kinds": [], "status": "n/a", "how": "the loop does not finetune"},
    "serve":   {"home": "n/a", "kinds": [], "status": "n/a", "how": "the loop calls a hosted model; latency is not on its critical path"},
    "found":   {"home": "llm.py", "kinds": ["procedure"], "status": "ready",
                "how": "structured output is enforced by the WeaverCandidate contract; sampling settings are pinned in config"},
    "prod":    {"home": "council + HITL + foldback", "kinds": ["decision"], "status": "built",
                "how": "council stand-up, GitHub Issues questions with a 4 h timeout, foldback drafts counted apart from reuse"},
}

# Thesis -> the Assayer checks that test it in this loop (names in organs/assayer.py), or why none can yet.
THESIS_CHECKS = {
    "T1": ["score_tuple"], "T2": ["canary"], "T3": ["state_of_record"], "T4": ["daily:first_attempt_admission_rate"],
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


def _seed_levels(atlas: dict) -> dict[str, str]:
    status = {s[0]: s[7] for s in atlas["S"]}
    levels = {n[0]: "L" if any(status.get(c.strip()) in READ for c in n[4].split(",")) else "S"
              for n in atlas["N"]}
    for t in atlas["THESES"]:
        # A synthesis cannot be more certain than its weakest cited premise.
        levels[t[0]] = "L" if t[3] and all(levels.get(c) == "L" for c in t[3]) else "S"
    return levels


def seed_complete(store: MemoryStore, atlas: dict | None = None) -> bool:
    """All pinned rows are present, not merely the last thesis written.

    Each SQLite row commits independently. A crash after T13 still leaves the
    sketches and gaps unwritten, so a thesis cannot serve as a completion flag.
    Check ids, kinds, source-row digests and grades; unrelated library rows are allowed.
    A changed existing row is not repaired silently: seed_library's immutable
    writes reject the collision for an operator to investigate.
    """
    atlas = atlas if atlas is not None else load()
    levels = _seed_levels(atlas)
    for s in atlas["S"]:
        ev = store.evidence(f"aie:{s[0]}")
        if ev is None or ev.sha256 != _sha(s) or ev.exposure != "development":
            return False
    for rows, kind in ((atlas["N"], "semantic_claim"), (atlas["THESES"], "procedure"),
                       (atlas["K"], "procedure"), (atlas["G"], "open_question")):
        for row in rows:
            rec = store.get(f"aie:{row[0]}")
            if (rec is None or rec.kind != kind or rec.subject_sha256 != _sha(row)
                    or rec.evidence_level != levels.get(row[0], "S")):
                return False
    return True


def _put_seed_record(store: MemoryStore, rec: MemoryRecord) -> bool:
    """Reuse identical pinned rows; never hide a conflicting immutable id."""
    old = store.get(rec.memory_id)
    if old is not None and old != rec:
        raise ValueError(f"immutable memory id collision: {rec.memory_id}; library needs an explicit rebuild: "
                         "python -m gobbler_flyte.atlas rebuild-library PATH (stop the runner first)")
    store.put(rec)  # validates parents and rejects an unequal existing body
    return old is None


def seed_library(store: MemoryStore, atlas: dict | None = None) -> dict:
    """Idempotent: every row has a fixed id, so a second seed writes nothing."""
    atlas = atlas or load()
    t0 = f"{atlas['date']}T00:00:00Z"
    status = {s[0]: s[7] for s in atlas["S"]}
    levels = _seed_levels(atlas)
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
        level = levels[n[0]]
        rec = MemoryRecord(memory_id=f"aie:{n[0]}", kind="semantic_claim", text=f"{n[2]}. {n[3]}"[:4000], readers=["assayer"],
                           evidence_ids=cites[:50], evidence_level=level, valid_from=t0, recorded_by="library",
                           subject_sha256=_sha(n))
        wrote["semantic_claim"] += _put_seed_record(store, rec)
        concept_ids.add(n[0])
    for t in atlas["THESES"]:
        parents = [f"aie:{c}" for c in t[3] if c in concept_ids]
        rec = MemoryRecord(memory_id=f"aie:{t[0]}", kind="procedure", text=f"{t[1]}. {t[2]} Rule: {t[4]}"[:4000],
                           readers=["assayer"], parent_ids=parents, evidence_level=levels[t[0]], valid_from=t0, recorded_by="library",
                           subject_sha256=_sha(t))
        wrote["procedure"] += _put_seed_record(store, rec)
    for k in atlas["K"]:
        rec = MemoryRecord(memory_id=f"aie:{k[0]}", kind="procedure", text=f"Code sketch {k[0]}, {k[2]}: {k[3]}"[:4000],
                           readers=["assayer"], evidence_level="S", valid_from=t0, recorded_by="library", subject_sha256=_sha(k))
        wrote["procedure"] += _put_seed_record(store, rec)
    for g in atlas["G"]:
        rec = MemoryRecord(memory_id=f"aie:{g[0]}", kind="open_question", text=f"Atlas {g[1]}: {g[2]}"[:4000], readers=["assayer"],
                           evidence_level="S", valid_from=t0, recorded_by="library", subject_sha256=_sha(g))
        wrote["open_question"] += _put_seed_record(store, rec)
    return wrote


def rebuild_library(path: Path) -> dict:
    """Explicit offline migration: validate a new DB, archive the old DB, atomically replace.

    The caller must stop the runner first. Existing immutable record bodies are
    never edited in place. The archive is a consistent SQLite backup. An active
    journal/WAL is refused; no source files or model calls are involved.
    """
    import os
    import sqlite3
    import tempfile
    import uuid

    path = Path(path).resolve()
    if any(Path(str(path) + suffix).exists() for suffix in ("-wal", "-shm", "-journal")):
        raise ValueError("library has an active SQLite sidecar; stop the runner and close it before rebuilding")
    handle, temporary = tempfile.mkstemp(prefix=".atlas-rebuild-", suffix=".sqlite", dir=path.parent)
    os.close(handle)
    temporary = Path(temporary)
    backup = None
    try:
        store = MemoryStore(temporary)
        try:
            counts = seed_library(store)
            if not seed_complete(store):
                raise ValueError("rebuilt library is incomplete; original was not replaced")
        finally:
            store.close()
        if path.exists():
            backup = path.with_name(path.name + ".before-rebuild-" + uuid.uuid4().hex[:12])
            source = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
            archive = sqlite3.connect(backup)
            try:
                source.backup(archive)
            finally:
                archive.close()
                source.close()
            with backup.open("rb") as stream:
                os.fsync(stream.fileno())
        with temporary.open("rb") as stream:
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        return {"library": str(path), "archive": str(backup) if backup else None, "seeded": counts}
    finally:
        temporary.unlink(missing_ok=True)


def thesis(atlas: dict, tid: str) -> dict:
    t = next(x for x in atlas["THESES"] if x[0] == tid)
    return {"id": t[0], "title": t[1], "rule": t[4], "concepts": t[3]}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Offline Atlas library maintenance; stop the runner before rebuilding.")
    parser.add_argument("command", choices=["rebuild-library"])
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    print(json.dumps(rebuild_library(args.path), indent=2, sort_keys=True))
