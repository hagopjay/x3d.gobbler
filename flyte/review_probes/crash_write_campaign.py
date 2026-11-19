#!/usr/bin/env python3
"""Seven representative AFTER-write process deaths, not exhaustive instruction fuzzing.

Only local offline fixtures run. Each case starts fresh, kills a child using
os._exit(77) after an actual persistence operation returns, then runs two clean
recovery ticks in separate processes and inspects SQLite/JSON ledgers.

Example (from the repository root):
  ACCRETE_DIR=/path/to/x3d.accrete python flyte/review_probes/crash_write_campaign.py --repo .

Use --repo BASELINE for the same campaign against 9d4671d. Optional --output
saves the complete JSON matrix. No model, API, human-channel send, or allowance
is involved. A deliberately unsafe LOCAL fixture config triggers the STOP case.
This tests one chosen after-write location per persistence kind, not torn writes,
filesystem power loss, every transaction, every checkpoint, or every interleave.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

CASES = ("world_append", "turns_jsonl", "tape_jsonl", "memory_json", "memory_sqlite", "library_sqlite", "stop_file")


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def inspect_state(state, case):
    """Read durable state without constructing Ctx or modifying project stores."""
    from gobbler_flyte import atlas

    problems, sqlite_checks = [], {}
    def records(name, table):
        path = state / name
        if not path.exists():
            return []
        with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
            sqlite_checks[name] = db.execute("PRAGMA integrity_check").fetchone()[0]
            return list(db.execute("SELECT body FROM " + table))

    memories = [json.loads(row[0]) for row in records("memory.sqlite", "memory")]
    library = [json.loads(row[0]) for row in records("library.sqlite", "memory")]
    evidence = [json.loads(row[0]) for row in records("library.sqlite", "evidence")]
    entries = []
    world = state / "world.sqlite"
    if world.exists():
        with sqlite3.connect(world.as_uri() + "?mode=ro", uri=True) as db:
            sqlite_checks[world.name] = db.execute("PRAGMA integrity_check").fetchone()[0]
            entries = [{"n": n, "hash": h, "payload": json.loads(body)} for n, h, body in
                       db.execute("SELECT n,hash,payload FROM entries ORDER BY n")]
    checkpoints = state / "checkpoints.sqlite"
    if checkpoints.exists():
        with sqlite3.connect(checkpoints.as_uri() + "?mode=ro", uri=True) as db:
            sqlite_checks[checkpoints.name] = db.execute("PRAGMA integrity_check").fetchone()[0]
    turns = read_jsonl(state / "turns.jsonl")
    tape = read_jsonl(state / "tape.jsonl")
    schedule = json.loads((state / "memory.json").read_text()) if (state / "memory.json").exists() else {}
    ops = [entry["payload"].get("generation", {}).get("op") for entry in entries]
    if any(not op for op in ops) or len(ops) != len(set(ops)):
        problems.append("missing or duplicate committed world operation keys")
    if len(turns) != len({turn["cycle"] for turn in turns}):
        problems.append("duplicate turn rows for a cycle")
    admitted = {turn["entry_hash"]: turn for turn in turns if turn.get("admitted")}
    if set(admitted) != {entry["hash"] for entry in entries}:
        problems.append("world entries and admitted turn ledger disagree")
    episodes = {row["memory_id"]: row for row in memories if row["kind"] == "episode"}
    if any("episode:" + entry["hash"][:24] not in episodes for entry in entries):
        problems.append("world entry lacks its durable episode memory")
    for entry in entries:
        episode = episodes.get("episode:" + entry["hash"][:24])
        if episode and episode.get("subject_sha256") != entry["payload"].get("candidate", {}).get("raw_sha256"):
            problems.append("episode subject differs from the committed world candidate")
    event_ids = [row["event_id"] for row in tape if row.get("event_id")]
    if len(event_ids) != len(set(event_ids)):
        problems.append("duplicate tape event ids")
    opens = Counter(row.get("cycle") for row in tape if row.get("node") == "gobbler" and row.get("kind") == "open")
    if any(count > 1 for count in opens.values()):
        problems.append("cycle open event duplicated in run tape")
    a = atlas.load()
    expected = {"aie:" + row[0] for key in ("N", "THESES", "K", "G") for row in a[key]}
    if expected - {row["memory_id"] for row in library}:
        problems.append("library seed incomplete")
    if {"aie:" + row[0] for row in a["S"]} - {row["evidence_id"] for row in evidence}:
        problems.append("library source registry incomplete")
    threads = schedule.get("threads", {})
    if case == "stop_file":
        if not (state / "STOP-THE-LINE.json").exists():
            problems.append("durable stop was lost")
        if any(turn["cycle"] > 1 for turn in turns):
            problems.append("work continued after durable stop")
    else:
        if (state / "STOP-THE-LINE.json").exists():
            problems.append("unexpected stop after safe offline recovery")
        # Baseline keeps only interrupted threads; a finished direct cycle has
        # no thread row. Infer completion from the durable turn ledger instead.
        if any(row.get("status") != "done" for row in threads.values()):
            problems.append("cycle remains lost, running, or unexpectedly waiting after recovery")
        cycles = schedule.get("cycles", 0)
        if cycles < 2 or not set(map(int, threads)) <= set(range(1, cycles + 1)):
            problems.append("scheduler lost a reserved cycle")
        if {turn["cycle"] for turn in turns} != set(range(1, cycles + 1)):
            problems.append("completed fixture cycle has no turn ledger row")
    if any(value != "ok" for value in sqlite_checks.values()):
        problems.append("SQLite integrity check failed")
    return {"problems": problems, "world_entries": len(entries), "operation_keys": ops,
            "turn_cycles": [row["cycle"] for row in turns], "tape_open_counts": dict(opens),
            "scheduler_cycles": schedule.get("cycles"), "threads": {key: row.get("status") for key, row in threads.items()},
            "library_memories": len(library), "library_sources": len(evidence), "sqlite_integrity": sqlite_checks,
            "stop_exists": (state / "STOP-THE-LINE.json").exists()}


def child(args):
    sys.path.insert(0, str(args.repo / "flyte"))
    from gobbler_flyte import accrete_bridge as accrete
    from gobbler_flyte import runner
    from gobbler_flyte.memory import MemoryStore

    state = args.state
    if not accrete.available():
        print(json.dumps({"not_run": "x3d.accrete unavailable; set ACCRETE_DIR"}))
        return 2
    if args.phase == "inspect":
        print(json.dumps(inspect_state(state, args.case), sort_keys=True))
        return 0
    cfg = runner.load_config()
    cfg["sources"] = [row for row in cfg["sources"] if row["id"] == "web3d-news"]
    if args.case == "stop_file":
        cfg["sources"][0]["url"] = "http://example.invalid/local-review-control"
    if args.phase == "recover":
        out = []
        for now in ("2026-11-19T00:30:00Z", "2026-11-19T01:00:00Z"):
            out.append(runner.tick(state, mode="offline", now=now, config=cfg))
        print(json.dumps({"recovery_ticks": out}, sort_keys=True))
        return 0

    def die(detail):
        (state / "crash-boundary.json").write_text(json.dumps({"case": args.case, "after_actual_write": detail}))
        os._exit(77)

    old_append = accrete.World.append
    def append(world, *a, **kw):
        result = old_append(world, *a, **kw)
        if args.case == "world_append" and result.get("status") == "committed":
            die({"entry_n": result["n"], "entry_hash": result["hash"]})
        return result
    accrete.World.append = append

    old_put = MemoryStore._put
    def put(store, table, key, body):
        result = old_put(store, table, key, body)
        database = store.db.execute("PRAGMA database_list").fetchone()[2]
        if args.case == "memory_sqlite" and Path(database).name == "memory.sqlite" and table == "memory" and key.startswith("episode:"):
            die({"database": "memory.sqlite", "table": table, "key": key})
        if args.case == "library_sqlite" and Path(database).name == "library.sqlite" and key == "aie:K1":
            die({"database": "library.sqlite", "table": table, "key": key})
        return result
    MemoryStore._put = put

    old_open = Path.open
    class WrittenFile:
        def __init__(self, path, stream):
            self.path, self.stream = path, stream
        def __getattr__(self, name):
            return getattr(self.stream, name)
        def __enter__(self):
            self.stream.__enter__()
            return self
        def __exit__(self, *exc):
            result = self.stream.__exit__(*exc)
            if exc[0] is None:
                if args.case == "turns_jsonl" and self.path.name == "turns.jsonl":
                    die({"file": self.path.name, "rows": len(read_jsonl(self.path))})
                if args.case == "tape_jsonl" and self.path.name == "tape.jsonl":
                    die({"file": self.path.name, "rows": len(read_jsonl(self.path))})
                if args.case == "stop_file" and self.path.name == "STOP-THE-LINE.json":
                    die({"file": self.path.name})
                if args.case == "memory_json" and self.path.name == "memory.json":
                    payload = json.loads(self.path.read_text())
                    threads = payload.get("threads", {})
                    if payload.get("cycles") == 1 and (not threads or threads.get("1", {}).get("status") == "done"):
                        die({"file": self.path.name, "cycle": 1, "thread_status": threads.get("1", {}).get("status"),
                             "completion_basis": "done thread or baseline's completed direct cycle without a thread row"})
            return result
    def opened(path, mode="r", *a, **kw):
        stream = old_open(path, mode, *a, **kw)
        return WrittenFile(path, stream) if any(flag in mode for flag in "wa+") else stream
    Path.open = opened

    old_replace = os.replace
    def replace(source, destination, *a, **kw):
        result = old_replace(source, destination, *a, **kw)
        if args.case == "memory_json" and Path(destination).name == "memory.json":
            payload = json.loads(Path(destination).read_text())
            threads = payload.get("threads", {})
            if payload.get("cycles") == 1 and (not threads or threads.get("1", {}).get("status") == "done"):
                die({"file": "memory.json", "cycle": 1, "thread_status": threads.get("1", {}).get("status"),
                     "completion_basis": "done thread or baseline's completed direct cycle without a thread row",
                     "operation": "os.replace returned"})
        return result
    os.replace = replace
    runner.tick(state, mode="offline", now="2026-11-19T00:00:00Z", config=cfg)
    print(json.dumps({"not_run": "chosen boundary was not reached"}))
    return 2


def driver(args):
    matrix = []
    def run(case, phase, state):
        cmd = [sys.executable, str(Path(__file__).resolve()), "--repo", str(args.repo), "--phase", phase,
               "--case", case, "--state", str(state)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout)
            payload = None
            if proc.stdout.strip():
                try:
                    payload = json.loads(proc.stdout.strip().splitlines()[-1])
                except ValueError:
                    pass
            return {"returncode": proc.returncode, "result": payload, "stderr": proc.stderr[-3500:]}
        except subprocess.TimeoutExpired:
            return {"timeout": args.timeout}

    for case in ([args.case] if args.case else CASES):
        with tempfile.TemporaryDirectory(prefix="gobbler-crash-" + case + "-") as tmp:
            state = Path(tmp)
            crashed = run(case, "crash", state)
            marker = state / "crash-boundary.json"
            row = {"boundary": case, "crash": crashed}
            if crashed.get("returncode") != 77 or not marker.exists():
                row["status"] = "not_run" if (crashed.get("result") or {}).get("not_run") else "fail"
            else:
                row["injected_after"] = json.loads(marker.read_text())
                recovered = run(case, "recover", state)
                checked = run(case, "inspect", state)
                row.update({"recovery": recovered, "inspection": checked})
                problems = (checked.get("result") or {}).get("problems", ["inspection unavailable"])
                row["status"] = "pass" if recovered.get("returncode") == 0 and checked.get("returncode") == 0 and not problems else "fail"
            matrix.append(row)
    report = {"schema": "gobbler.representative-crash-writes/1", "grade": "C", "repo": str(args.repo),
              "python": sys.version, "accrete_dir": os.environ.get("ACCRETE_DIR"),
              "scope": "Seven chosen after-write boundaries; offline local fixtures; process death, not power loss or exhaustive crash consistency.",
              "matrix": matrix}
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n")
    print(rendered)
    return 0 if all(row["status"] == "pass" for row in matrix) else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=lambda value: Path(value).resolve(), default=Path(__file__).resolve().parents[2])
    parser.add_argument("--case", choices=CASES)
    parser.add_argument("--phase", choices=("crash", "recover", "inspect"))
    parser.add_argument("--state", type=lambda value: Path(value).resolve())
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.phase and (not args.case or args.state is None):
        parser.error("child phase requires --case and --state")
    return child(args) if args.phase else driver(args)


if __name__ == "__main__":
    raise SystemExit(main())
