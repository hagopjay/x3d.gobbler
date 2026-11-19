"""Gobbler.flyte memory: typed records, a context compiler that filters before it ranks, and a sealed-test audit.

Adapted (not vendored) from the "X3D Agentic Flywheels" LangGraph reference package that HagopJay sent for
comment on 18 Nov 2026 (loom_flywheels/models.py, memory.py, context.py, SHA256SUMS verified, 33 tests reproduced).
What was taken: the nine memory kinds, immutable ids, lineage, revocation, contradiction bundles, exposure roles
(development / selection / sealed) and the rule that every rejection happens before ranking or prompt assembly.

What changed, with the probe that motivated it (flyte/tests/test_flyte.py::Memory):
  * The reference judged a memory by its own exposure label only. A memory labelled "development" that cites a
    sealed evidence id reached the context with its text (probe: "dev memory citing sealed evidence" -> included).
    Here a memory's effective exposure is the union over its lineage AND every evidence id it cites.
  * A memory citing an evidence id the registry does not know was also included. Here it is excluded
    ("unknown_evidence"): unresolvable provenance is not development evidence.
  * Every exclusion is returned with its reason, and every compiled context is journaled, so a later audit can prove
    that no sealed record ever reached a model prompt.

Only trusted organ code writes memory (Witness, Keeper). A model reply never writes a record or an exposure label.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from sqlite3 import connect as _sqlite_connect   # bound at import: a test patching runner.sqlite3 stays scoped to checkpoints
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Kind = Literal["episode", "semantic_claim", "procedure", "counterexample", "experiment", "decision",
               "open_question", "summary", "preference"]
Exposure = Literal["development", "selection", "sealed"]
KINDS = Kind.__args__                     # the nine kinds, same names as the reference schema


def wire(value) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value) -> str:
    return hashlib.sha256(wire(value).encode("utf-8")).hexdigest()


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class MemoryRecord(Record):
    memory_id: str = Field(pattern=r"^[A-Za-z0-9:_.-]{1,160}$")
    kind: Kind
    text: str = Field(min_length=1, max_length=4000)
    readers: list[str] = Field(min_length=1)                 # organs allowed to see it, e.g. ["weaver"]
    scope: dict[str, str] = Field(default_factory=dict)     # exact-match keys, e.g. {"world": "..."}
    evidence_ids: list[str] = Field(default_factory=list, max_length=50)
    parent_ids: list[str] = Field(default_factory=list, max_length=50)
    contradicts: list[str] = Field(default_factory=list, max_length=50)
    exposures: list[Exposure] = Field(default_factory=lambda: ["development"], min_length=1)
    evidence_level: Literal["C", "L", "S"] = "S"            # C = a named instrument ran
    review_state: Literal["provisional", "accepted", "retracted", "superseded"] = "accepted"
    valid_from: str = Field(pattern=r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
    valid_to: str | None = Field(default=None, pattern=r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
    recorded_by: Literal["witness", "keeper", "gobbler", "human"]
    cycle: int | None = Field(default=None, ge=1)
    subject_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")   # the exact bytes it is about

    @model_validator(mode="after")
    def _interval(self):
        if self.valid_to is not None and self.valid_to <= self.valid_from:
            raise ValueError("valid_to must follow valid_from")
        return self


class EvidenceRef(Record):
    """What the registry knows about an evidence id: its exposure and the bytes it names."""
    evidence_id: str
    exposure: Exposure
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    instrument: str


class WeaverCandidate(Record):
    """The contract a model reply must meet before Witness spends an instrument run on it."""
    x3d: str = Field(min_length=1, max_length=64_000)
    title: str = Field(min_length=1, max_length=120)
    instruction: str = Field(min_length=1, max_length=280)
    cites: list[str] = Field(default_factory=list, max_length=20)


class MemoryStore:
    """SQLite: immutable memory rows, an evidence registry, revocations and a context journal."""

    def __init__(self, path: Path | str = ":memory:"):
        self.db = _sqlite_connect(str(path), check_same_thread=False)
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS memory(id TEXT PRIMARY KEY, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS evidence(id TEXT PRIMARY KEY, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS revocation(id TEXT PRIMARY KEY, reason TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS context(id TEXT PRIMARY KEY, body TEXT NOT NULL);
        """)

    def close(self):
        self.db.close()

    def _put(self, table: str, key: str, body: str):
        with self.db:
            old = self.db.execute(f"SELECT body FROM {table} WHERE id=?", (key,)).fetchone()
            if old and old[0] != body:
                raise ValueError(f"immutable {table} id collision: {key}")
            self.db.execute(f"INSERT OR IGNORE INTO {table} VALUES(?,?)", (key, body))

    def put_evidence(self, ev: EvidenceRef):
        self._put("evidence", ev.evidence_id, wire(ev))

    def put(self, m: MemoryRecord):
        for p in m.parent_ids:
            if self.get(p) is None:
                raise ValueError(f"missing parent {p}")
        self._put("memory", m.memory_id, wire(m))

    def by_cycle(self, cycle: int, kind: str) -> list[MemoryRecord]:
        return [m for m in self.all() if m.cycle == cycle and m.kind == kind]

    def put_once(self, m: MemoryRecord) -> bool:
        """Write unless the id exists (a retried cycle or a repeated refusal keeps the first record). True if written."""
        if self.get(m.memory_id) is not None:
            return False
        self.put(m)
        return True

    def get(self, memory_id: str) -> MemoryRecord | None:
        r = self.db.execute("SELECT body FROM memory WHERE id=?", (memory_id,)).fetchone()
        return MemoryRecord.model_validate_json(r[0]) if r else None

    def evidence(self, evidence_id: str) -> EvidenceRef | None:
        r = self.db.execute("SELECT body FROM evidence WHERE id=?", (evidence_id,)).fetchone()
        return EvidenceRef.model_validate_json(r[0]) if r else None

    def all(self) -> list[MemoryRecord]:
        return [MemoryRecord.model_validate_json(r[0]) for r in self.db.execute("SELECT body FROM memory ORDER BY id")]

    def revoke(self, memory_id: str, reason: str):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO revocation VALUES(?,?)", (memory_id, reason))

    def revoked(self, memory_id: str) -> bool:
        return self.db.execute("SELECT 1 FROM revocation WHERE id=?", (memory_id,)).fetchone() is not None

    def lineage(self, m: MemoryRecord) -> list[MemoryRecord]:
        seen, todo = {}, [m]
        while todo:
            cur = todo.pop()
            if cur.memory_id in seen:
                continue
            seen[cur.memory_id] = cur
            for p in cur.parent_ids:
                parent = self.get(p)
                if parent is None:
                    raise ValueError("incomplete lineage")
                todo.append(parent)
        return list(seen.values())

    def journal_context(self, packet: dict) -> str:
        self._put("context", packet["context_sha256"], wire(packet))
        return packet["context_sha256"]

    def contexts(self) -> list[dict]:
        return [json.loads(r[0]) for r in self.db.execute("SELECT body FROM context ORDER BY rowid")]


def effective_exposures(store: MemoryStore, m: MemoryRecord) -> tuple[set[str], str | None]:
    """Union of exposures over the lineage and every cited evidence id. Returns (exposures, blocking reason)."""
    out: set[str] = set()
    try:
        lineage = store.lineage(m)
    except ValueError:
        return {"sealed"}, "incomplete_lineage"
    for x in lineage:
        out.update(x.exposures)
        for eid in x.evidence_ids:
            ev = store.evidence(eid)
            if ev is None:
                return out | {"sealed"}, "unknown_evidence"
            out.add(ev.exposure)
    return out, None


@dataclass(frozen=True)
class Reader:
    organ: str
    now: str
    scope: dict


def _eligible(store: MemoryStore, m: MemoryRecord, reader: Reader) -> str | None:
    """None if eligible, else the first reason it is not. Order matters only for the reported reason."""
    for x in store.lineage(m):
        if store.revoked(x.memory_id):
            return "revoked_lineage"
        if x.review_state != "accepted":
            return "not_accepted"
        if reader.organ not in x.readers:
            return "not_a_reader"
        if not (x.valid_from <= reader.now and (x.valid_to is None or reader.now < x.valid_to)):
            return "outside_valid_time"
        if any(reader.scope.get(k) != v for k, v in x.scope.items()):
            return "scope_mismatch"
    exp, why = effective_exposures(store, m)
    if why:
        return why
    if exp & {"sealed", "selection"}:
        return "held_out"
    return None


def compile_context(store: MemoryStore, reader: Reader, *, kinds: tuple[str, ...], query: str,
                    max_bytes: int = 6000, journal: bool = True) -> dict:
    """Filter, then rank, then pack. Contradicting records travel together or not at all."""
    views = store.all()
    excluded, ok = {}, {}
    for m in views:
        try:
            why = _eligible(store, m, reader)
        except ValueError:
            why = "incomplete_lineage"
        if why:
            excluded[m.memory_id] = why
        else:
            ok[m.memory_id] = m
    adj = {m.memory_id: set(m.contradicts) for m in views}
    for a, bs in list(adj.items()):
        for b in bs:
            adj.setdefault(b, set()).add(a)
    words = set(query.casefold().split())
    seeds = sorted((m for m in ok.values() if m.kind in kinds), key=lambda m: (
        0 if m.kind == "counterexample" else 1 if adj.get(m.memory_id) else 2,
        -len(words & set(m.text.casefold().split())), m.memory_id))
    packet = {"schema": "gobbler.context/1", "reader": reader.organ, "now": reader.now, "scope": reader.scope,
              "memories": [], "policy": {"retrieved_text_is_data": True, "filtered_before_ranking": True}}
    used = set()
    for m in seeds:
        if m.memory_id in used:
            continue
        bundle, todo = set(), [m.memory_id]
        while todo:
            x = todo.pop()
            if x not in bundle:
                bundle.add(x)
                todo.extend(adj.get(x, set()) - bundle)
        if not bundle <= set(ok):
            for x in bundle - set(ok):
                excluded.setdefault(x, "contradiction_partner_hidden")
            excluded.setdefault(m.memory_id, "contradiction_partner_hidden")
            continue
        rows = [{"memory_id": x, "kind": ok[x].kind, "text": ok[x].text, "evidence_level": ok[x].evidence_level,
                 "contradicts": sorted(adj.get(x, set()))} for x in sorted(bundle - used)]
        trial = {**packet, "memories": packet["memories"] + rows}
        if len(wire(trial).encode()) <= max_bytes:
            packet, used = trial, used | bundle
    packet["excluded"] = dict(sorted(excluded.items()))
    packet["context_sha256"] = digest(packet)
    if journal:
        store.journal_context(packet)
    return packet


def audit_contamination(store: MemoryStore) -> dict:
    """Prove from the journal that no held-out record, and no record leaning on held-out evidence, reached a prompt."""
    held = {m.memory_id for m in store.all() if effective_exposures(store, m)[0] & {"sealed", "selection"}}
    leaks = []
    snaps = store.contexts()
    for p in snaps:
        for row in p["memories"]:
            if row["memory_id"] in held:
                leaks.append({"context_sha256": p["context_sha256"], "memory_id": row["memory_id"]})
    return {"schema": "gobbler.contamination-audit/1", "contexts": len(snaps), "held_out": len(held),
            "leaks": leaks, "clean": not leaks,
            "scope": "Journal of compiled contexts against current held-out labels; a prompt built outside compile_context is not covered."}


def seal_bucket(sha256_hex: str, one_in: int = 5) -> Exposure:
    """Deterministic hold-out: about one counterexample in `one_in` is sealed, chosen by its bytes, not by its outcome."""
    return "sealed" if int(sha256_hex[:8], 16) % one_in == 0 else "development"
