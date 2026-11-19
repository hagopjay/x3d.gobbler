"""C probe: validate must reject a tampered payload hash even if finalize repairs it in memory."""
import json
import os
from pathlib import Path
import sys
repo = Path(os.environ.get("GOBBLER_REVIEW_TARGET", str(Path(__file__).resolve().parents[2])))
sys.path.insert(0, str(repo / "flyte"))
from gobbler_flyte.memory import MemoryRecord, MemoryStore
from gobbler_flyte.transport import export, validate

s = MemoryStore()
s.put(MemoryRecord(memory_id="decision:1", kind="decision", text="Underspecified decision", readers=["gobbler"],
                   valid_from="2026-11-18T00:00:00Z", recorded_by="human", cycle=1))
row = next(r for r in export(s) if r["record_type"] == "memory")
row["payload_sha256"] = "0" * 64
result = validate([row])
print(json.dumps({"grade": "C", "valid": result["valid"], "error_count": result["error_count"], "errors": result["errors"]}, sort_keys=True))
s.close()
assert result["valid"] is False, "tampered payload_sha256 passed validation"
