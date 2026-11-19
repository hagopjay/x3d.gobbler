"""One tick of the clock: wake sleeping cycles whose answer (or timeout) has come, then start a new cycle.

Called every 30 minutes by GitHub Actions or by a Flyte LaunchPlan; or 48 times
in a row by sim.py with a simulated clock. Each cycle is its own LangGraph
thread ("cycle-N") in a SQLite checkpointer, so a cycle waiting on a human
sleeps while later cycles keep turning.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sqlite3
import tempfile

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from . import accrete_bridge as accrete
from .budget import Budget, _time
from .gobbler import build
from .hitl import FileChannel, GitHubIssues
from .llm import HaikuLLM
from .memory import MemoryStore                   # imported here so its sqlite binding is the real one
from .state import append_jsonl_batch_once, append_jsonl_once

HERE = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Ctx:
    """Everything an organ may touch. Organs get nothing else."""

    def __init__(self, *, state_dir: Path, mode: str, now: str, config: dict, allowance: dict, channel=None,
                 llm_factory=None, visible=None, loom_dir: str | None = None):
        if mode not in ('live', 'offline', 'sim'):
            raise ValueError('mode must be live, offline or sim')
        _time(now)
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.mode, self.now, self.config = mode, now, config
        self.sources = config["sources"]
        self.budget = Budget(config, allowance, self.state_dir / "spend.jsonl", config["authorized_humans"])
        self.world = accrete.World(self.state_dir / "world.sqlite") if accrete.available() else None
        self.world_id = self.world.world_id[:16] if self.world else "no-world"
        self.outbox = self.state_dir / "outbox"
        self.mem = MemoryStore(self.state_dir / "memory.sqlite")
        # The library (AI Engineering Atlas) is knowledge, kept apart from the world's experience; seeded once, idempotent.
        self.library = MemoryStore(self.state_dir / "library.sqlite")
        from .atlas import seed_complete, seed_library
        if not seed_complete(self.library):
            seed_library(self.library)
        self.loom_dir = loom_dir
        self.channel = channel
        self._llm_factory = llm_factory
        self.visible = visible or (lambda item: True)
        self.memory_path = self.state_dir / "memory.json"
        m = json.loads(self.memory_path.read_text()) if self.memory_path.exists() else {"seen": [], "cycles": 0, "threads": {}}
        self.memory = {**m, "seen": set(m["seen"])}
        self.open_decisions = sum(1 for t in self.memory["threads"].values() if t["status"] == "waiting")

    def llm(self):
        if self.mode == 'offline':
            raise RuntimeError('offline mode never constructs a model client')
        if self._llm_factory:
            client = self._llm_factory()
            if self.mode == 'sim' and getattr(client, 'simulated', False) is not True:
                raise RuntimeError('sim mode requires an explicitly simulated client')
            return client
        if self.mode == 'sim':
            raise RuntimeError('sim mode requires an injected simulated client')
        llm = self.config["llm"]
        return HaikuLLM(llm["model"], llm["max_tokens"], llm["effort"])

    def save(self) -> None:
        m = {**self.memory, "seen": sorted(self.memory["seen"])}
        # Atomic replacement prevents a partial JSON file; it does not make the
        # world, checkpoint, outbox and tape one cross-store transaction.
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', dir=self.state_dir, prefix='.memory-',
                                             encoding='utf-8', delete=False) as stream:
                temp_path = Path(stream.name)
                json.dump(m, stream, indent=1, sort_keys=True)
                stream.flush(); os.fsync(stream.fileno())
            os.replace(temp_path, self.memory_path)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)


def load_config(path: Path | None = None) -> dict:
    return json.loads((path or HERE / "config" / "flyte.json").read_text())


def load_allowance(state_dir: Path) -> dict:
    p = Path(state_dir) / "allowance.json"           # a typed OK lands here; the committed default is zero
    return json.loads((p if p.exists() else HERE / "config" / "allowance.json").read_text())


def default_channel(config: dict, state_dir: Path, mode: str):
    h = config["hitl"]
    if mode == "live" and h["channel"] == "github-issues":
        return GitHubIssues(h["repo"], h["label"], config["authorized_humans"])
    return FileChannel(Path(state_dir), config["authorized_humans"])


def _tape(ctx: Ctx, cycle: int, rows: list[dict], already: int) -> int:
    append_jsonl_batch_once(ctx.state_dir / "tape.jsonl",
                            [{"t": ctx.now, "cycle": cycle, **item,
                              "event_id": f"{ctx.world_id}:cycle-{cycle}:log-{index}"}
                             for index, item in enumerate(rows[already:], start=already)], "event_id")
    return len(rows)


def tick(state_dir: str | Path, *, mode: str = "offline", now: str | None = None, config: dict | None = None,
         channel=None, llm_factory=None, visible=None, loom_dir: str | None = None) -> dict:
    if mode not in ('live', 'offline', 'sim'):
        raise ValueError('mode must be live, offline or sim')
    config = config or load_config()
    now = now or utc_now()
    state_dir = Path(state_dir)
    _time(now)
    state_dir.mkdir(parents=True, exist_ok=True)
    # Lock BEFORE constructing Ctx: that constructor reads scheduler state and
    # seeds stores. A context read before the lock can become stale while waiting.
    import fcntl
    lock = open(state_dir / ".tick.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close()
        raise RuntimeError(f"another tick holds {state_dir / '.tick.lock'}")
    ctx, conn = None, None
    try:
        stop = state_dir / "STOP-THE-LINE.json"
        channel = channel or default_channel(config, state_dir, mode)
        # A stopped line performs no channel API polling, including allowance polling.
        if not stop.exists():
            typed = channel.allowance()
            if typed:
                a = {**load_allowance(state_dir), **typed}
                (state_dir / "allowance.json").write_text(json.dumps(a, indent=1))
        ctx = Ctx(state_dir=state_dir, mode=mode, now=now, config=config, allowance=load_allowance(state_dir), channel=channel,
                  llm_factory=llm_factory, visible=visible, loom_dir=loom_dir)
        summary = {"utc": now, "resumed": [], "started": None, "waiting": []}

        def stopped():
            if not stop.exists():
                return False
            try:
                held = json.loads(stop.read_text())
            except ValueError:
                held = {"unreadable": True}
            # Persist the pause even if the stop file is cleared before the next tick.
            ctx.memory.setdefault("stop_pause", {"started_utc": held.get("utc") or now})
            ctx.save()
            summary["stopped"] = held
            summary["waiting"] = sorted(int(k) for k, t in ctx.memory["threads"].items() if t["status"] == "waiting")
            append_jsonl_once(state_dir / "tape.jsonl",
                              {"t": now, "cycle": None, "node": "gobbler", "kind": "stopped",
                               "text": f"line stopped since {held.get('utc')}: remaining sleepers and new work held",
                               "event_id": f"stop-observed:{now}"}, "event_id")
            return True

        if stopped():
            return summary
        conn = sqlite3.connect(state_dir / "checkpoints.sqlite", check_same_thread=False)
        saver = SqliteSaver(conn)
        graph = build(ctx, saver)

        def config_for_thread(thread):
            return {"configurable": {"thread_id": thread["thread_id"]}}

        def remember(out):
            # Scout's mutable side effects must survive a crash after its checkpoint.
            for signal in [out.get("signal"), *out.get("collisions", [])]:
                if signal:
                    ctx.memory["seen"].add(signal["id"])

        def settle(cycle, thread, out, *, interrupted=False):
            remember(out)
            thread["taped"] = _tape(ctx, cycle, out.get("log", []), thread.get("taped", 0))
            if interrupted or "__interrupt__" in out:
                q = out["__interrupt__"][0].value if "__interrupt__" in out else out["decision"]
                thread["ref"] = thread.get("ref") or channel.post(q)
                thread["status"] = "waiting"
                ctx.save()                       # retain checkpoint until scheduler state is durable
            else:
                thread["status"] = "done"
                if thread.get("ref") and out.get("decision"):
                    thread["close_pending"] = out["decision"]
                ctx.save()                       # terminal scheduler commit BEFORE checkpoint deletion
                saver.delete_thread(thread["thread_id"])
                if thread.get("close_pending"):
                    channel.close(thread["ref"], thread["close_pending"])
                    thread.pop("close_pending", None)
                    ctx.save()

        # Recover an orphan from the older scheduler too: its completed checkpoint
        # is authoritative; never delete it and generate a different candidate.
        orphan_cycle = ctx.memory["cycles"] + 1
        orphan_cfg = {"configurable": {"thread_id": f"cycle-{orphan_cycle}"}}
        orphan = graph.get_state(orphan_cfg)
        if orphan.values:
            ctx.memory["cycles"] = orphan_cycle
            ctx.memory["threads"][str(orphan_cycle)] = {"thread_id": f"cycle-{orphan_cycle}", "status": "running",
                "taped": 0, "started_utc": orphan.values.get("started_utc", now), "mode": orphan.values.get("mode", mode)}
            ctx.save()

        # Resume reserved/in-flight cycles at their saved node, preserving candidate,
        # decision, signal and operation key across world/ledger/checkpoint crashes.
        for key, thread in sorted(ctx.memory["threads"].items(), key=lambda kv: int(kv[0])):
            if thread["status"] == "done":
                if thread.get("close_pending"):
                    channel.close(thread["ref"], thread["close_pending"])
                    thread.pop("close_pending", None)
                    ctx.save()
                saver.delete_thread(thread["thread_id"])
                continue
            if thread["status"] != "running":
                continue
            if thread.get("mode", mode) != mode:
                raise RuntimeError("cannot recover a cycle under a different run mode")
            cfg = config_for_thread(thread)
            snap = graph.get_state(cfg)
            if snap.values and snap.next == ("wait",) and snap.values.get("decision", {}).get("status") == "asked":
                settle(int(key), thread, snap.values, interrupted=True)
            else:
                out = (graph.invoke(None, cfg) if snap.values and snap.next else dict(snap.values)) if snap.values else \
                    graph.invoke({"cycle": int(key), "started_utc": thread["started_utc"], "mode": mode}, cfg)
                settle(int(key), thread, out)
            summary.setdefault("recovered", []).append(int(key))
            if stopped():
                return summary

        # Silence during an enforced stop is not a response opportunity. Give every
        # reversible sleeper a fresh full window after clearing, update its posted
        # question, and persist this before considering timeout defaults.
        if ctx.memory.get("stop_pause"):
            deadline = (datetime.strptime(now, "%Y-%m-%dT%H:%M:%SZ") +
                        timedelta(minutes=config["hitl"]["timeout_minutes"])).strftime("%Y-%m-%dT%H:%M:%SZ")
            for thread in ctx.memory["threads"].values():
                if thread["status"] != "waiting":
                    continue
                cfg = config_for_thread(thread)
                snap = graph.get_state(cfg)
                q = snap.values.get("decision")
                if q and q["reversible"] and q.get("status") == "asked":
                    q = {**q, "deadline_utc": deadline, "reopened_utc": now}
                    graph.update_state(cfg, {"decision": q}, as_node="ask")
                    if hasattr(channel, "update"):
                        channel.update(thread["ref"], q)
                    else:
                        channel.post(q)
            ctx.memory.pop("stop_pause")
            ctx.save()

        # Sleeping cycles: typed answer or a genuine uninterrupted response window.
        for key, t in sorted(ctx.memory["threads"].items(), key=lambda kv: int(kv[0])):
            if t["status"] != "waiting":
                continue
            cfg = {"configurable": {"thread_id": t["thread_id"]}}
            snap = graph.get_state(cfg)
            if snap.values and not snap.next:
                settle(int(key), t, snap.values)
                summary.setdefault("recovered", []).append(int(key))
                if stopped():
                    return summary
                continue
            if not snap.values:
                raise RuntimeError(f"waiting cycle {key} has no checkpoint; manual ledger reconciliation required")
            q = snap.values["decision"]
            answer = channel.poll(t["ref"], q, now)
            if not answer and q["reversible"] and q["deadline_utc"] and now >= q["deadline_utc"]:
                answer = {"choice": q["preferred"], "by": "timeout", "via": "clock", "utc": now}
            if not answer:
                summary["waiting"].append(int(key))
                continue
            out = graph.invoke(Command(resume=answer), cfg)
            settle(int(key), t, out)
            summary["resumed"].append({"cycle": int(key), **{k: answer[k] for k in ("choice", "by")}})
            ctx.open_decisions -= 1
            if stopped():
                return summary

        # 2. a new cycle every tick
        cycle = ctx.memory["cycles"] + 1
        ctx.memory["cycles"] = cycle
        cfg = {"configurable": {"thread_id": f"cycle-{cycle}"}}
        thread = {"thread_id": f"cycle-{cycle}", "status": "running", "taped": 0, "started_utc": now, "mode": mode}
        ctx.memory["threads"][str(cycle)] = thread
        ctx.save()                               # reserve the cycle BEFORE any graph side effect
        out = graph.invoke({"cycle": cycle, "started_utc": now, "mode": mode}, cfg)
        settle(cycle, thread, out)
        summary["started"] = {"cycle": cycle, "signal": (out.get("signal") or {}).get("title"),
                              "ruling": (out.get("council") or {}).get("ruling"), "entry": (out.get("entry") or {}).get("n")}
        summary["waiting"] = sorted(int(k) for k, t in ctx.memory["threads"].items() if t["status"] == "waiting")
        stopped()
        if ctx.world:                                     # the world as text: append-friendly for git, verifiable offline
            (state_dir / "world-archive.json").write_text(json.dumps(ctx.world.archive(), indent=1, sort_keys=True))
        conn.execute("VACUUM")
        return summary
    finally:
        if conn is not None:
            conn.close()
        if ctx is not None:
            ctx.mem.close()
            ctx.library.close()
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()
