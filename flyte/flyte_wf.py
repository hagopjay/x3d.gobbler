"""Gobbler.flyte on its own Flyte server.

Local, no server:        pyflyte run flyte_wf.py gobbler_flyte --state_dir /abs/path/state --mode offline
Flyte sandbox (his PC):  flytectl demo start   # Docker; free; then
                         pyflyte register flyte_wf.py && flytectl update launchplan -p flytesnacks -d development \
                             gobbler_flyte_every_30m --version <v> --activate
The task is the same `tick()` GitHub Actions runs, so both hosts share one state folder format
(checkpoints.sqlite, world.sqlite, tape.jsonl, turns.jsonl, spend.jsonl, memory.json). Mount the
state folder as a persistent volume on the sandbox; a Flyte task's own disk is thrown away.
"""
from __future__ import annotations

import json

from flytekit import CronSchedule, LaunchPlan, task, workflow


@task(retries=0, cache=False)
def tick_task(state_dir: str, mode: str, loom_dir: str) -> str:
    from gobbler_flyte.runner import tick
    return json.dumps(tick(state_dir, mode=mode, loom_dir=loom_dir or None))


@workflow
def gobbler_flyte(state_dir: str = "state", mode: str = "offline", loom_dir: str = "") -> str:
    return tick_task(state_dir=state_dir, mode=mode, loom_dir=loom_dir)


every_30m = LaunchPlan.get_or_create(
    gobbler_flyte, name="gobbler_flyte_every_30m",
    schedule=CronSchedule(schedule="*/30 * * * *"),
    default_inputs={"state_dir": "/data/gobbler-flyte/state", "mode": "live", "loom_dir": ""},
)
