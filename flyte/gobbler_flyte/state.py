"""The shared state that flows through one Gobbler cycle."""
from __future__ import annotations

import operator
import json
import os
from pathlib import Path
from typing import Annotated, Any, TypedDict


class FlyteState(TypedDict, total=False):
    cycle: int                  # cycle number, also the LangGraph thread suffix
    started_utc: str            # clock value when the cycle began (simulated or real)
    mode: str                   # "live" | "offline" | "sim"
    signals: list[dict]         # Scout output, ranked, already de-duplicated
    collisions: list[dict]      # things that look like X3D but are not (Ryzen X3D, X3D video net)
    signal: dict                # the one signal this cycle works on
    proposal: dict              # Weaver output: action, options, preferred pick, reversibility
    candidate: dict             # X3D fragment candidate for the world (accrete candidate shape)
    witness: dict               # Witness verdict for the latest candidate
    attempts: int               # Weaver<->Witness inner-loop count
    council: dict               # the stand-up: each organ's line plus the Gobbler's ruling
    decision: dict              # human decision record (asked, answered or timed out)
    entry: dict                 # world entry Keeper committed (n, hash, title)
    turn: dict                  # flywheel turn record
    assay: dict                 # Assayer: thesis checks for this cycle (AI Engineering Atlas)
    spend: Annotated[list[dict], operator.add]   # every priced call this cycle
    log: Annotated[list[dict], operator.add]     # the run tape: one row per organ action


def row(node: str, kind: str, text: str, **data: Any) -> dict:
    """One line on the run tape."""
    return {"node": node, "kind": kind, "text": text, **({"data": data} if data else {})}


def read_jsonl(path: Path) -> list[dict]:
    """Read an append journal, repairing only a torn final, unterminated record.

    A corrupt complete line is never silently discarded. The tick lock serializes
    writers; flush/fsync in append_jsonl_once makes completed records durable.
    """
    if not path.exists():
        return []
    data = path.read_bytes()
    lines, records, offset = data.splitlines(keepends=True), [], 0
    for index, line in enumerate(lines):
        if not line.strip():
            offset += len(line)
            continue
        try:
            records.append(json.loads(line))
        except (ValueError, UnicodeDecodeError):
            if index != len(lines) - 1 or line.endswith(b"\n"):
                raise
            with path.open("r+b") as stream:
                stream.truncate(offset)
                stream.flush(); os.fsync(stream.fileno())
            break
        offset += len(line)
    return records


def append_jsonl_once(path: Path, record: dict, key: str) -> dict:
    """Return a committed row for this key, adding it durably only if absent."""
    return append_jsonl_batch_once(path, [record], key)[0]


def append_jsonl_batch_once(path: Path, records: list[dict], key: str) -> list[dict]:
    """One scan and fsync per batch; complete rows survive a partial batch write."""
    existing = {item[key]: item for item in read_jsonl(path) if key in item}
    results, additions = [], []
    for record in records:
        if record[key] not in existing:
            existing[record[key]] = record
            additions.append(record)
        results.append(existing[record[key]])
    if not additions:
        return results
    path.parent.mkdir(parents=True, exist_ok=True)
    needs_newline = path.exists() and path.stat().st_size > 0 and not path.read_bytes().endswith(b"\n")
    with path.open("a", encoding="utf-8") as stream:
        if needs_newline:
            stream.write("\n")
        for record in additions:
            stream.write(json.dumps(record, sort_keys=True, default=str) + "\n")
        stream.flush(); os.fsync(stream.fileno())
    return results
