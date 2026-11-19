"""One tick of the clock: wake sleeping cycles whose answer (or timeout) has come, then start a new cycle.

Called every 30 minutes by GitHub Actions or by a Flyte LaunchPlan; or 48 times
in a row by sim.py with a simulated clock. Each cycle is its own LangGraph
thread ("cycle-N") in a SQLite checkpointer, so a cycle waiting on a human
sleeps while later cycles keep turning.
"""
from __future__ import annotations

from datetime import datetime, timezone
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
        self.world_id = (self.world.archive().get("world_id") or "world")[:16] if self.world else "no-world"
        self.outbox = self.state_dir / "outbox"
        self.mem = MemoryStore(self.state_dir / "memory.sqlite")
        # The library (AI Engineering Atlas) is knowledge, kept apart from the world's experience; seeded once, idempotent.
        self.library = MemoryStore(self.state_dir / "library.sqlite")
        if self.library.get("aie:T13") is None:
            from .atlas import seed_library
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
    with (ctx.state_dir / "tape.jsonl").open("a") as f:
        for r in rows[already:]:
            f.write(json.dumps({"t": ctx.now, "cycle": cycle, **r}, sort_keys=True, default=str) + "\n")
    return len(rows)


def tick(state_dir: str | Path, *, mode: str = "offline", now: str | None = None, config: dict | None = None,
         channel=None, llm_factory=None, visible=None, loom_dir: str | None = None) -> dict:
    if mode not in ('live', 'offline', 'sim'):
        raise ValueError('mode must be live, offline or sim')
    config = config or load_config()
    now = now or utc_now()
    state_dir = Path(state_dir)
    channel = channel or default_channel(config, state_dir, mode)
    # an allowance typed since the last tick takes effect now
    typed = channel.allowance()
    if typed:
        a = {**load_allowance(state_dir), **typed}
        (state_dir / "allowance.json").parent.mkdir(parents=True, exist_ok=True)
        (state_dir / "allowance.json").write_text(json.dumps(a, indent=1))
    ctx = Ctx(state_dir=state_dir, mode=mode, now=now, config=config, allowance=load_allowance(state_dir), channel=channel,
              llm_factory=llm_factory, visible=visible, loom_dir=loom_dir)
    # One tick at a time per state directory: a second overlapping tick fails fast instead of reading the same
    # cycle number. (Actions already serialises with a concurrency group; this covers Flyte and local runs.)
    import fcntl
    lock = open(state_dir / ".tick.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close()
        ctx.mem.close()
        ctx.library.close()
        raise RuntimeError(f"another tick holds {state_dir / '.tick.lock'}")
    stop = state_dir / "STOP-THE-LINE.json"
    if stop.exists():                      # Atlas thesis T12: a failed critical check halts work until a human clears it
        try:
            held = json.loads(stop.read_text())
        except ValueError:
            held = {"unreadable": True}
        with (state_dir / "tape.jsonl").open("a") as f:
            f.write(json.dumps({"t": now, "cycle": None, "node": "gobbler", "kind": "stopped",
                                "text": f"line stopped by the Assayer since {held.get('utc')}: no cycle started, no sleeper resumed"},
                               sort_keys=True) + "\n")
        ctx.mem.close()
        ctx.library.close()
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()
        return {"utc": now, "stopped": held, "resumed": [], "started": None, "waiting": []}
    conn = sqlite3.connect(state_dir / "checkpoints.sqlite", check_same_thread=False)
    try:
        saver = SqliteSaver(conn)
        graph = build(ctx, saver)
        summary = {"utc": now, "resumed": [], "started": None, "waiting": []}

        # 1. sleeping cycles: answer -> resume; reversible past deadline -> preferred pick; else keep sleeping
        for key, t in sorted(ctx.memory["threads"].items(), key=lambda kv: int(kv[0])):
            if t["status"] != "waiting":
                continue
            cfg = {"configurable": {"thread_id": t["thread_id"]}}
            snap = graph.get_state(cfg)
            q = snap.values["decision"]
            answer = channel.poll(t["ref"], q, now)
            if not answer and q["reversible"] and q["deadline_utc"] and now >= q["deadline_utc"]:
                answer = {"choice": q["preferred"], "by": "timeout", "via": "clock", "utc": now}
            if not answer:
                summary["waiting"].append(int(key))
                continue
            out = graph.invoke(Command(resume=answer), cfg)
            t["taped"] = _tape(ctx, int(key), out["log"], t["taped"])
            t["status"] = "done"
            saver.delete_thread(t["thread_id"])          # finished cycles live on in tape/turns; checkpoints hold only sleepers
            channel.close(t["ref"], out["decision"])
            summary["resumed"].append({"cycle": int(key), **{k: answer[k] for k in ("choice", "by")}})
            ctx.open_decisions -= 1

        # 2. a new cycle every tick
        cycle = ctx.memory["cycles"] + 1
        ctx.memory["cycles"] = cycle
        cfg = {"configurable": {"thread_id": f"cycle-{cycle}"}}
        saver.delete_thread(f"cycle-{cycle}")       # a crashed earlier attempt at this cycle leaves no half-run graph state
        out = graph.invoke({"cycle": cycle, "started_utc": now, "mode": mode}, cfg)
        taped = _tape(ctx, cycle, out["log"], 0)
        if "__interrupt__" in out:
            q = out["__interrupt__"][0].value
            ref = channel.post(q)
            ctx.memory["threads"][str(cycle)] = {"thread_id": f"cycle-{cycle}", "status": "waiting", "ref": ref, "taped": taped}
            summary["waiting"].append(cycle)
        else:
            saver.delete_thread(f"cycle-{cycle}")
        summary["started"] = {"cycle": cycle, "signal": (out.get("signal") or {}).get("title"),
                              "ruling": (out.get("council") or {}).get("ruling"), "entry": (out.get("entry") or {}).get("n")}
        ctx.save()
        if ctx.world:                                     # the world as text: append-friendly for git, verifiable offline
            (state_dir / "world-archive.json").write_text(json.dumps(ctx.world.archive(), indent=1, sort_keys=True))
        conn.execute("VACUUM")
        return summary
    finally:
        conn.close()
        if ctx is not None:
            ctx.mem.close()
            ctx.library.close()
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()
