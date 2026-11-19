"""Offline Assayer review probes; set GOBBLER_REVIEW_TARGET to replay against an untouched checkout.

These tests execute the real pinned gate, XSD/semantic validator, trap stage and WorldStore.
The canary failure injection changes a canary input/expectation, never run_canary's result.
"""
from __future__ import annotations

from contextlib import contextmanager
import copy
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

TARGET = Path(os.environ.get("GOBBLER_REVIEW_TARGET", Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(TARGET / "flyte"))

from gobbler_flyte import accrete_bridge as accrete
from gobbler_flyte.organs import assayer
from gobbler_flyte.organs.witness import witness
from gobbler_flyte.runner import Ctx, load_config, tick


@contextmanager
def context(path, config=None):
    ctx = Ctx(state_dir=path, mode="offline", now="2026-11-19T00:00:00Z",
              config=config or load_config(), allowance={})
    try:
        yield ctx
    finally:
        ctx.mem.close()
        ctx.library.close()


def check(rows, name):
    found = [r for r in rows if r["check"] == name]
    assert found, f"check {name!r} was skipped"
    return found[0]


def test_canary_covers_the_real_witness_trap_stage(tmp_path):
    result = assayer.run_canary()
    assert not result["not_run"], "run this probe with ACCRETE_DIR pointing at the pinned checkout"
    assert result["held"], result
    controls = [r for r in result["fragments"] if r.get("trap_rules")]
    assert controls, "canary never exercised a positive trap-stage control"
    assert controls[0]["trap_rules"] == ["color-emissive-white"]
    assert all(c["matches"] for c in result["trap_controls"])
    assert any(("color-range", "error") in c["got"] for c in result["trap_controls"])
    frag = next(x for name, x, _ in assayer.CANARY if name == controls[0]["fragment"])
    with context(tmp_path) as ctx:
        real = witness({"cycle": 1, "candidate": {"x3d": frag}, "proposal": {"action": "standards-note"},
                        "signal": {}}, ctx)["witness"]
    assert real["status"] == "pass"  # Warnings remain warnings; the canary checks that the stage actually saw one.
    assert sorted({h["rule"] for h in real["traps"]}) == controls[0]["trap_rules"]


def test_canary_cache_changes_with_definition_and_real_mismatch_stops(tmp_path):
    with context(tmp_path) as ctx:
        assert check(assayer.assay_cycle({"cycle": 1}, ctx), "canary")["status"] == "pass"
        plain = next(x for name, x, _ in assayer.CANARY if name == "plain-sphere")
        # This authored fault control is really admitted by the real instruments, contradicting its expected refusal.
        with patch.object(assayer, "CANARY", [*assayer.CANARY, ("review-expectation-mismatch", plain, "fail")]):
            result = assayer.assayer({"cycle": 2}, ctx)
        assert check(result["assay"]["checks"], "canary")["status"] == "fail"
        assert (tmp_path / assayer.STOP_FILE).exists()
    stopped = tick(tmp_path, mode="offline", now="2026-11-19T00:30:00Z")
    assert stopped["started"] is None and "stopped" in stopped


def test_canary_cache_binds_trap_source_bytes(tmp_path):
    from gobbler_flyte.loom import traps
    with context(tmp_path) as ctx:
        assert check(assayer.assay_cycle({"cycle": 1}, ctx), "canary")["status"] == "pass"
        changed = tmp_path / "changed-traps.py"
        changed.write_bytes(Path(traps.__file__).read_bytes() + b"\n# review source-drift control\n")
        with patch.object(traps, "__file__", str(changed)):
            result = assayer.assayer({"cycle": 2}, ctx)
        assert check(result["assay"]["checks"], "canary")["status"] == "fail"
        assert (tmp_path / assayer.STOP_FILE).exists()


def test_state_of_record_detects_real_append_without_turn(tmp_path):
    with context(tmp_path) as ctx:
        candidate = accrete.procedural_candidate(ctx.world.next_plan())
        candidate["generator"]["op"] = f"{ctx.world_id}:cycle-7"
        assert ctx.world.append(candidate)["status"] == "committed"
        result = assayer.assayer({"cycle": 7}, ctx)
        assert check(result["assay"]["checks"], "state_of_record")["status"] == "fail"
        assert (tmp_path / assayer.STOP_FILE).exists()


def test_egress_checks_unchosen_configured_source(tmp_path):
    config = copy.deepcopy(load_config())
    config["sources"].append({"id": "review-unselected", "kind": "rss", "url": "http://example.invalid/feed"})
    with context(tmp_path, config) as ctx:
        rows = assayer.assay_cycle({"cycle": 1, "signal": {"source": "web3d-news"}}, ctx)
    assert check(rows, "egress")["status"] == "fail"


def test_egress_checks_nonchosen_fetch_receipt(tmp_path):
    with context(tmp_path) as ctx:
        rows = assayer.assay_cycle({"cycle": 1, "signal": {"source": "web3d-news"}, "log": [
            {"node": "scout", "kind": "sweep", "data": {"per_source": [
                {"source": "hn-webgpu", "fetch_url": "https://example.invalid/not-configured", "transport": "http"}
            ]}}
        ]}, ctx)
    assert check(rows, "egress")["status"] == "fail"


def test_existing_checks_can_reject_explicit_invariant_violations(tmp_path):
    config = copy.deepcopy(load_config())
    config["assay"]["pins_audited_utc"] = "2025-01-01T00:00:00Z"
    with context(tmp_path, config) as ctx:
        rows = assayer.assay_cycle({"cycle": 1, "signal": {"source": "web3d-news"}, "attempts": 4,
                                   "turn": {"grade": "Confirmed", "admitted": False},
                                   "spend": [{"actual_usd": 1, "tokens_in": 6001}]}, ctx)
    for name in ("score_tuple", "pin_age", "provenance", "context_budget", "retry_cap"):
        assert check(rows, name)["status"] == "fail", name


def test_pin_age_rejects_a_future_self_attestation(tmp_path):
    config = copy.deepcopy(load_config())
    config["assay"]["pins_audited_utc"] = "2030-01-01T00:00:00Z"
    with context(tmp_path, config) as ctx:
        rows = assayer.assay_cycle({"cycle": 1}, ctx)
    assert check(rows, "pin_age")["status"] == "fail"


def test_assay_day_labels_attempt_and_turn_denominators():
    root = TARGET / "flyte/runs/sim-2026-11-18-r4"
    tape = [json.loads(x) for x in (root / "tape.jsonl").read_text().splitlines() if x]
    turns = [json.loads(x) for x in (root / "turns.jsonl").read_text().splitlines() if x]
    result = assayer.assay_day(tape, turns)
    assert result["attempts"]["n"] == 61
    assert result["attempts"]["witness_pass"] == 35
    assert result["attempts"]["witness_pass_fraction"] == 0.5738
    assert result["turns"]["admitted_first_attempt"] == 18
    assert result["turns"]["first_attempt_admission_rate"] == 0.5143
    assert "pass_hat_3" not in result["attempts"]
    assert result["same_signal_reliability"]["estimate"] is None
