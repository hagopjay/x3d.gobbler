"""Real offline graph recovery probes; only durable writes are fault-injected."""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "flyte"))
sys.path.insert(0, str(ROOT / "review_probes"))

from gobbler_flyte import accrete_bridge
from gobbler_flyte.state import append_jsonl_once, read_jsonl
from recovery_common import checkpoint_loss, forced_silence, provenance_loss, stop_batch


@pytest.mark.skipif(not accrete_bridge.available(), reason="pinned local accrete instruments required")
@pytest.mark.parametrize("probe", [checkpoint_loss, provenance_loss, forced_silence, stop_batch])
def test_recovery_boundaries(tmp_path, probe):
    probe(tmp_path)


def test_torn_final_journal_record_recovers_without_discarding_committed_rows(tmp_path):
    path = tmp_path / "turns.jsonl"
    path.write_bytes(b'{"cycle":1,"admitted":true}\n{"cycle":2,"adm')
    assert read_jsonl(path) == [{"cycle": 1, "admitted": True}]
    append_jsonl_once(path, {"cycle": 2, "admitted": True}, "cycle")
    append_jsonl_once(path, {"cycle": 2, "admitted": True}, "cycle")
    assert [r["cycle"] for r in read_jsonl(path)] == [1, 2]


def test_corrupt_complete_journal_record_is_never_silently_lost(tmp_path):
    path = tmp_path / "turns.jsonl"
    original = b'{"cycle":1}\nnot-json\n'
    path.write_bytes(original)
    with pytest.raises(ValueError):
        read_jsonl(path)
    assert path.read_bytes() == original
