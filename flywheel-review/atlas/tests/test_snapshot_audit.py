"""Negative controls for the portable archive consistency audit."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from snapshot_audit import CANONICAL_OUTPUTS, audit


class SnapshotAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.graph = {"meta": {"counts": {"Law": 1, "Grade": 1}, "edges": {"grade": 1}, "inputs": {"fixture": "pinned-commit"}},
                      "nodes": [{"id": "law/1", "type": "Law"}, {"id": "grade/C", "type": "Grade"}],
                      "edges": [{"s": "law/1", "p": "grade", "o": "grade/C"}]}
        self.write_graph()
        (self.root / "atlas-claims.jsonl").write_text(json.dumps({"_meta": {"schema": "claims/0.1"}}) + "\n" +
            json.dumps({"id": "law/1", "value": "example", "quote": "example", "line": 1, "source": "fixture@pin:file"}) + "\n")
        (self.root / "atlas-world.x3d").write_text("<X3D><Scene><TimeSensor DEF='clock'/><Transform DEF='object'/><ROUTE fromNode='clock' fromField='fraction_changed' toNode='object' toField='set_translation'/></Scene></X3D>")
        for name in CANONICAL_OUTPUTS:
            path = self.root / name
            if not path.exists():
                path.write_text("fixture bytes\n")
        self.update_receipt()

    def write_graph(self):
        (self.root / "atlas.json").write_text(json.dumps(self.graph))

    def update_receipt(self):
        hashes = {name: hashlib.sha256((self.root / name).read_bytes()).hexdigest()
                  for name in CANONICAL_OUTPUTS}
        (self.root / "receipt.json").write_text(json.dumps({"sha256": hashes, "inputs": self.graph["meta"]["inputs"]}))

    def mutate_receipt(self, change):
        receipt = json.loads((self.root / "receipt.json").read_text())
        change(receipt)
        (self.root / "receipt.json").write_text(json.dumps(receipt))

    def check(self, result, name):
        return next(row for row in result["checks"] if row["name"] == name)

    def test_consistent_fixture_passes_without_promoting_claims(self):
        result = audit(self.root)
        self.assertTrue(result["ok"])
        self.assertEqual(result["scope"], "local-archive-consistency")
        self.assertIn("not promote", " ".join(result["limits"]))

    def test_altered_bytes_fail_archived_hash(self):
        with (self.root / "atlas.json").open("a") as stream:
            stream.write(" ")
        result = audit(self.root)
        self.assertFalse(result["ok"])
        self.assertFalse(self.check(result, "archived output hashes match")["ok"])

    def test_dangling_edge_fails_even_with_consistent_new_hash(self):
        self.graph["edges"][0]["o"] = "grade/missing"
        self.write_graph()
        self.update_receipt()
        result = audit(self.root)
        self.assertTrue(self.check(result, "archived output hashes match")["ok"])
        self.assertFalse(self.check(result, "graph edges resolve")["ok"])

    def test_duplicate_id_fails_even_with_consistent_new_hash(self):
        self.graph["nodes"].append(dict(self.graph["nodes"][0]))
        self.write_graph()
        self.update_receipt()
        result = audit(self.root)
        self.assertFalse(self.check(result, "graph node IDs are unique and typed")["ok"])

    def test_scene_unresolved_route_is_rejected(self):
        (self.root / "atlas-world.x3d").write_text("<X3D><Scene><ROUTE fromNode='absent' fromField='x' toNode='absent' toField='y'/></Scene></X3D>")
        self.update_receipt()
        result = audit(self.root)
        self.assertFalse(self.check(result, "scene named references resolve")["ok"])

    def test_missing_ledger_row_fails_coverage(self):
        (self.root / "atlas-claims.jsonl").write_text('{"_meta": {}}\n')
        self.update_receipt()
        result = audit(self.root)
        self.assertFalse(self.check(result, "copied rows each have one ledger entry")["ok"])

    def test_receipt_cannot_hash_outside_snapshot(self):
        (self.root / "receipt.json").write_text(json.dumps({"sha256": {"../not-allowed": "0" * 64}}))
        result = audit(self.root)
        self.assertFalse(self.check(result, "archived output hashes match")["ok"])

    def test_receipt_requires_all_eight_canonical_hashes(self):
        self.mutate_receipt(lambda receipt: receipt["sha256"].pop("atlas.json"))
        result = audit(self.root)
        check = self.check(result, "archived output hashes match")
        self.assertFalse(result["ok"])
        self.assertEqual(check["missingHashes"], ["atlas.json"])

    def test_receipt_pins_must_match_graph(self):
        self.mutate_receipt(lambda receipt: receipt["inputs"].update({"fixture": "different-commit"}))
        result = audit(self.root)
        self.assertFalse(result["ok"])
        self.assertFalse(self.check(result, "receipt pins match graph pins")["ok"])

    def test_receipt_pins_cannot_be_absent(self):
        self.mutate_receipt(lambda receipt: receipt.pop("inputs"))
        result = audit(self.root)
        self.assertFalse(self.check(result, "receipt pins match graph pins")["ok"])

    def test_invalid_hash_shape_fails_with_explanation(self):
        for bad_hashes in ([], None, {"atlas.json": ["invalid"]}):
            with self.subTest(bad_hashes=bad_hashes):
                self.mutate_receipt(lambda receipt: receipt.update({"sha256": bad_hashes}))
                result = audit(self.root)
                self.assertFalse(result["ok"])
                self.assertFalse(self.check(result, "archived output hashes match")["ok"])

    def test_invalid_metadata_shape_returns_failure_instead_of_crashing(self):
        for invalid_meta in (None, [], "bad", {"counts": []}, {"counts": {"Law": True}, "edges": {}}):
            with self.subTest(invalid_meta=invalid_meta):
                self.graph["meta"] = invalid_meta
                self.write_graph()
                result = audit(self.root)
                self.assertFalse(result["ok"])
                self.assertFalse(result["checks"][0]["ok"])
                self.assertIn("atlas.meta", result["checks"][0]["error"])

    def test_invalid_node_type_returns_failed_check_instead_of_crashing(self):
        self.graph["nodes"][0]["type"] = []
        self.write_graph()
        self.update_receipt()
        result = audit(self.root)
        self.assertFalse(self.check(result, "graph node IDs are unique and typed")["ok"])

    def test_duplicate_edge_fails_even_after_counts_and_hashes_are_updated(self):
        self.graph["edges"].append(dict(self.graph["edges"][0]))
        self.graph["meta"]["edges"]["grade"] = 2
        self.write_graph()
        self.update_receipt()
        result = audit(self.root)
        self.assertTrue(self.check(result, "archived output hashes match")["ok"])
        self.assertTrue(self.check(result, "graph totals match embedded metadata")["ok"])
        edges = self.check(result, "graph edges resolve")
        self.assertFalse(edges["ok"])
        self.assertEqual(edges["duplicateTriples"][0]["index"], 1)

    def test_hash_consistent_ledger_must_contain_a_typed_quote_witness(self):
        positive = {"id": "law/1", "value": "example", "quote": "example", "line": 1, "source": "fixture@pin:file"}
        for field, value in (("value", "different"), ("quote", None), ("line", True), ("line", 0), ("source", [])):
            with self.subTest(field=field, value=value):
                row = dict(positive, **{field: value})
                (self.root / "atlas-claims.jsonl").write_text(json.dumps(row) + "\n")
                self.update_receipt()
                result = audit(self.root)
                self.assertTrue(self.check(result, "archived output hashes match")["ok"])
                self.assertFalse(self.check(result, "copied rows each have one ledger entry")["ok"])

    def test_x3d_root_alone_does_not_supply_a_scene(self):
        for xml in ("<X3D/>", "<X3D><Scene/><Scene/></X3D>"):
            with self.subTest(xml=xml):
                (self.root / "atlas-world.x3d").write_text(xml)
                self.update_receipt()
                result = audit(self.root)
                self.assertFalse(self.check(result, "scene has X3D root and no Script")["ok"])


if __name__ == "__main__":
    unittest.main()
