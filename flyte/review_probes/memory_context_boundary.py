"""C probe: inaccessible rows must not leak IDs, perturb context hashes or exceed the packet cap."""
import json
import os
from pathlib import Path
import sys
repo = Path(os.environ.get("GOBBLER_REVIEW_TARGET", str(Path(__file__).resolve().parents[2])))
sys.path.insert(0, str(repo / "flyte"))
from gobbler_flyte.memory import MemoryRecord, MemoryStore, Reader, compile_context, wire

s = MemoryStore()
r = Reader("weaver", "2026-11-19T00:00:00Z", {})
def record(i, readers):
    return MemoryRecord(memory_id=i, kind="counterexample", text="visible fixture", readers=readers,
                        valid_from="2026-11-18T00:00:00Z", recorded_by="witness")
s.put(record("visible", ["weaver"]))
before = compile_context(s, r, kinds=("counterexample",), query="fixture", max_bytes=600, journal=False)
for i in range(40):
    s.put(record(f"private:medical:patient-{i:03d}", ["keeper"]))
after = compile_context(s, r, kinds=("counterexample",), query="fixture", max_bytes=600, journal=False)
checks = {"hidden_ids_absent": "private:medical" not in wire(after),
          "hidden_rows_do_not_change_context": before["context_sha256"] == after["context_sha256"],
          "final_packet_within_cap": len(wire(after).encode()) <= 600}
print(json.dumps({"grade": "C", "checks": checks, "final_bytes": len(wire(after).encode()), "cap": 600}, sort_keys=True))
s.close()
assert all(checks.values()), checks
