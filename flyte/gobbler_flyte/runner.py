"""One tick of the clock: wake sleeping cycles whose answer (or timeout) has come, then start a new cycle.

Called every 30 minutes by GitHub Actions or by a Flyte LaunchPlan; or 48 times
in a row by sim.py with a simulated clock. Each cycle is its own LangGraph
thread ("cycle-N") in a SQLite checkpointer, so a cycle waiting on a human
sleeps while later cycles keep turning.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from . import accrete_bridge as accrete
from .budget import Budget
from .gobbler import build
from .hitl import FileChannel, GitHubIssues
from .llm import HaikuLLM

HERE = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Ctx:
    """Everything an organ may touch. Organs get nothing else."""

    def __init__(self, *, state_dir: Path, mode: str, now: str, config: dict, allowance: dict, channel=None,
                 llm_factory=None, visible=None, loom_dir: str | None = None):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.mode, self.now, self.config = mode, now, config
        self.sources = config["sources"]
        self.budget = Budget(config, allowance, self.state_dir / "spend.jsonl", config["authorized_humans"])
        self.world = accrete.World(self.state_dir / "world.sqlite") if accrete.available() else None
        self.outbox = self.state_dir / "outbox"
        self.loom_dir = loom_dir
        self.channel = channel
        self._llm_factory = llm_factory
        self.visible = visible or (lambda item: True)
        self.memory_path = self.state_dir / "memory.json"
        m = json.loads(self.memory_path.read_text()) if self.memory_path.exists() else {"seen": [], "cycles": 0, "threads": {}}
        self.memory = {**m, "seen": set(m["seen"])}
        self.open_decisions = sum(1 for t in self.memory["threads"].values() if t["status"] == "waiting")

    def llm(self):
        if self._llm_factory:
            return self._llm_factory()
        llm = self.config["llm"]
        return HaikuLLM(llm["model"], llm["max_tokens"], llm["effort"])

    def save(self) -> None:
        m = {**self.memory, "seen": sorted(self.memory["seen"])}
        self.memory_path.write_text(json.dumps(m, indent=1, sort_keys=True))


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
    conn = sqlite3.connect(state_dir / "checkpoints.sqlite", check_same_thread=False)
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
    conn.close()
    return summary
