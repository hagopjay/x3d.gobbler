"""Crash/stop probes use real local graph, gate, validator, world; only writes are fault-injected."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from unittest.mock import patch


def require(condition, detail="recovery contract failed"):
    if not condition:
        raise AssertionError(detail)


def config_for(*ids, unsafe=()):
    from gobbler_flyte.runner import load_config
    cfg = copy.deepcopy(load_config())
    cfg["sources"] = [s for s in cfg["sources"] if s["id"] in ids]
    for src in cfg["sources"]:
        if src["id"] in unsafe:
            src["url"] = "http://example.invalid/review-egress-control"
    return cfg


def answer(root, cycle):
    (root / "answers" / f"{cycle:05d}.json").write_text(json.dumps({"by": "hagopjay", "text": "B"}))


def checkpoint_loss(root: Path):
    from gobbler_flyte.runner import Ctx, tick
    cfg = config_for("x_ite-releases")
    initial = tick(root, mode="offline", now="2026-11-19T00:00:00Z", config=cfg)
    require(initial["waiting"] == [1], initial)
    answer(root, 1)
    original = Ctx.save
    def fail_terminal_save(ctx):
        if ctx.memory["threads"].get("1", {}).get("status") == "done":
            raise OSError("review: crash before terminal scheduler save")
        return original(ctx)
    try:
        with patch.object(Ctx, "save", fail_terminal_save):
            tick(root, mode="offline", now="2026-11-19T00:30:00Z", config=cfg)
    except OSError:
        pass
    out = tick(root, mode="offline", now="2026-11-19T01:00:00Z", config=cfg)
    turns = [json.loads(x) for x in (root / "turns.jsonl").read_text().splitlines()]
    require(sum(t["cycle"] == 1 for t in turns) == 1, turns)
    require(json.loads((root / "memory.json").read_text())["threads"]["1"]["status"] == "done")
    return {"recovered": True, "turns_for_cycle_1": 1, "tick": out}


def provenance_loss(root: Path):
    from gobbler_flyte import runner
    cfg = config_for("web3d-news", "hn-x3d")
    with patch.object(runner, "_tape", side_effect=OSError("review: crash after graph before tape")):
        try:
            runner.tick(root, mode="offline", now="2026-11-19T00:00:00Z", config=cfg)
        except OSError:
            pass
    drafts = sorted((root / "outbox").glob("00001-*.md"))
    require(len(drafts) == 1, drafts)
    draft, frozen = drafts[0], drafts[0].read_bytes()
    out = runner.tick(root, mode="offline", now="2026-11-19T00:30:00Z", config=cfg,
                      visible=lambda item: item["source"] == "hn-x3d")
    require(draft.read_bytes() == frozen, "op-key recovered old world entry but replaced its foldback provenance")
    require(len(list((root / "outbox").glob("00001-*.md"))) == 1, "same world operation redrafted under a different action")
    return {"original_draft_preserved": True, "tick": out}


def forced_silence(root: Path):
    from gobbler_flyte.runner import tick
    first = tick(root, mode="offline", now="2026-11-19T00:00:00Z", config=config_for("x_ite-releases"))
    require(1 in first["waiting"])
    # The real egress assay sees this deliberately non-HTTPS configured source.
    tick(root, mode="offline", now="2026-11-19T00:30:00Z",
         config=config_for("x_ite-releases", "web3d-news", unsafe=("web3d-news",)))
    stop = root / "STOP-THE-LINE.json"
    require(stop.exists(), "real egress control did not stop the line")
    held = json.loads(stop.read_text())
    require(any(c["check"] == "egress" for c in held["failed"]), held)
    stop.unlink()  # Explicit local review fixture clears the stop; it supplies no answer.
    out = tick(root, mode="offline", now="2026-11-19T10:00:00Z", config=config_for("x_ite-releases"))
    require(all(r["cycle"] != 1 for r in out["resumed"]), "forced silence during stop became timeout consent")
    require(1 in out["waiting"], out)
    return {"forced_silence_not_consent": True, "stop_checks": held["failed"], "tick": out}


def stop_batch(root: Path):
    from gobbler_flyte.runner import tick
    from gobbler_flyte.memory import MemoryRecord, MemoryStore, digest
    cfg = config_for("x_ite-releases", "blender-x3d")
    first = tick(root, mode="offline", now="2026-11-19T00:00:00Z", config=cfg,
                 visible=lambda item: item["source"] == "x_ite-releases")
    require(1 in first["waiting"])
    second = tick(root, mode="offline", now="2026-11-19T00:30:00Z", config=cfg)
    require(2 in second["waiting"], second)
    answer(root, 1)
    answer(root, 2)
    # Plant a genuinely contaminated context journal, then let the unpatched
    # contamination audit and Assayer detect it. This does not fake a canary result.
    memory = MemoryStore(root / "memory.sqlite")
    memory.put(MemoryRecord(memory_id="review:sealed-control", kind="counterexample", readers=["weaver"],
                            text="Held-out review control.", exposures=["sealed"], evidence_level="S",
                            valid_from="2026-11-19T00:00:00Z", recorded_by="human"))
    packet = {"schema": "gobbler.context/1", "reader": "weaver", "now": "2026-11-19T00:45:00Z", "scope": {},
              "memories": [{"memory_id": "review:sealed-control", "kind": "counterexample", "text": "Held-out review control."}],
              "excluded": {}, "policy": {}}
    packet["context_sha256"] = digest(packet)
    memory.journal_context(packet)
    memory.close()
    out = tick(root, mode="offline", now="2026-11-19T01:00:00Z",
               config=cfg)
    stop = json.loads((root / "STOP-THE-LINE.json").read_text())
    require(any(c["check"] == "grader_opacity" for c in stop["failed"]), stop)
    require([r["cycle"] for r in out["resumed"]] == [1], "tick continued resuming sleepers after real stop")
    require(out["started"] is None, "tick started another cycle after real stop")
    return {"stopped_within_tick": True, "tick": out}
