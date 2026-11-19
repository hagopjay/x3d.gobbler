"""C probe: an Atlas/source registry citation must not become an executed C-grade refusal."""
import json
import os
from pathlib import Path
import sys
repo = Path(os.environ.get("GOBBLER_REVIEW_TARGET", str(Path(__file__).resolve().parents[2])))
sys.path.insert(0, str(repo / "flyte"))
from gobbler_flyte.memory import EvidenceRef, MemoryRecord, MemoryStore
from gobbler_flyte.transport import export

s = MemoryStore()
s.put_evidence(EvidenceRef(evidence_id="aie:source", exposure="development", sha256="a" * 64,
                          instrument="AI Engineering Atlas rev 28, source status v"))
s.put(MemoryRecord(memory_id="source:claim", kind="semantic_claim", text="Catalogue source statement", readers=["assayer"],
                   evidence_ids=["aie:source"], evidence_level="L", valid_from="2026-11-18T00:00:00Z", recorded_by="library"))
row = next(r for r in export(s) if r["record_type"] == "evidence")
checks = {"not_fabricated_execution": row["origin"] != "executed", "not_fabricated_C": row["grade"] != "C",
          "not_fabricated_failure": row["status"] != "fail", "registered_instrument_preserved": "Atlas" in row["method"]}
print(json.dumps({"grade": "C", "checks": checks,
                  "exported": {k: row[k] for k in ("origin", "grade", "status", "method")}}, sort_keys=True))
s.close()
assert all(checks.values()), checks
