"""C probe: an export cannot mark missing provenance complete or widen a local reader restriction."""
import json
import os
from pathlib import Path
import sys
repo = Path(os.environ.get("GOBBLER_REVIEW_TARGET", str(Path(__file__).resolve().parents[2])))
sys.path.insert(0, str(repo / "flyte"))
from gobbler_flyte.memory import EvidenceRef, MemoryRecord, MemoryStore
from gobbler_flyte.transport import export

s = MemoryStore()
s.put(MemoryRecord(memory_id="cx:unknown", kind="counterexample", text="private evidence incomplete", readers=["keeper"],
                   evidence_ids=["unregistered"], subject_sha256="a" * 64,
                   valid_from="2026-11-18T00:00:00Z", recorded_by="witness"))
s.put_evidence(EvidenceRef(evidence_id="registered", exposure="development", sha256="b" * 64, instrument="fixture registry"))
s.put(MemoryRecord(memory_id="cx:resolved", kind="counterexample", text="Locally resolved reference", readers=["keeper"],
                   evidence_ids=["registered"], subject_sha256="b" * 64,
                   valid_from="2026-11-18T00:00:00Z", recorded_by="witness"))
rows = export(s)
row = next(r for r in rows if "gobbler:cx:unknown" in r.get("tags", []))
checks = {"missing_lineage_is_incomplete": row["exposure"]["lineage_complete"] is False,
          "unknown_exposure_preserved": "unknown" in row["exposure"]["roles"],
          "restricted_reader_not_public": row["acl"]["classification"] != "public",
          "all_canonical_closures_incomplete": all(r["exposure"]["lineage_complete"] is False for r in rows),
          "all_unresolved_canonical_refs_unknown": all("unknown" in r["exposure"]["roles"] for r in rows)}
print(json.dumps({"grade": "C", "checks": checks, "exposure": row["exposure"], "acl": row["acl"]}, sort_keys=True))
s.close()
assert all(checks.values()), checks
