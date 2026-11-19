"""C probe: unstructured text/parenthood cannot establish a decision or a lawful-twin relation."""
import json
import os
from pathlib import Path
import sys
repo = Path(os.environ.get("GOBBLER_REVIEW_TARGET", str(Path(__file__).resolve().parents[2])))
sys.path.insert(0, str(repo / "flyte"))
from gobbler_flyte.memory import MemoryRecord, MemoryStore
from gobbler_flyte.transport import export

s = MemoryStore()
base = dict(readers=["gobbler"], valid_from="2026-11-18T00:00:00Z", recorded_by="human", cycle=1)
s.put(MemoryRecord(memory_id="decision:1", kind="decision", text="No decision has been recorded", **base))
s.put(MemoryRecord(memory_id="cx:1", kind="counterexample", text="Refused example", subject_sha256="a" * 64, **base))
s.put(MemoryRecord(memory_id="episode:2", kind="episode", text="Unrelated later admission", parent_ids=["cx:1"],
                   subject_sha256="b" * 64, **{**base, "cycle": 2}))
rows = [r for r in export(s) if r["record_type"] == "memory"]
decision = next(r for r in rows if r["payload"]["kind"] == "decision")["payload"]
cx = next(r for r in rows if r["payload"]["kind"] == "counterexample")["payload"]
checks = {"unknown_decision_abstains": decision["outcome"] == "abstain",
          "reviewer_not_guessed_from_first_word": decision["reviewer"] != "No",
          "cross_cycle_parent_not_lawful_twin": cx["lawful_twin_artifact_id"] is None}
print(json.dumps({"grade": "C", "checks": checks, "decision": decision,
                  "lawful_twin_artifact_id": cx["lawful_twin_artifact_id"]}, sort_keys=True))
s.close()
assert all(checks.values()), checks
