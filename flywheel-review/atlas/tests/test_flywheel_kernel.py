"""Protocol rejection and content-binding tests; no external service is used."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import flywheel_kernel as kernel


class GraphIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.graph = {"nodes": [{"id": "a", "type": "Law"}, {"id": "b", "type": "FailureMode"}],
                      "edges": [{"s": "a", "p": "paidForBy", "o": "b"}]}

    def test_duplicate_node_identity_is_rejected(self):
        self.graph["nodes"].append({"id": "a", "type": "Law"})
        with self.assertRaisesRegex(ValueError, "duplicate node"):
            kernel.validate_graph(self.graph)

    def test_unresolved_edge_is_rejected(self):
        self.graph["edges"][0]["o"] = "missing"
        with self.assertRaisesRegex(ValueError, "unresolved"):
            kernel.validate_graph(self.graph)

    def test_duplicate_edge_is_rejected(self):
        self.graph["edges"].append(copy.deepcopy(self.graph["edges"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate edge"):
            kernel.validate_graph(self.graph)

    def test_malformed_rows_raise_a_validation_error_instead_of_crashing(self):
        for graph in ([], {"nodes": {}, "edges": []}, {"nodes": [None], "edges": []},
                      {"nodes": self.graph["nodes"], "edges": [None]},
                      {"nodes": self.graph["nodes"], "edges": [{"s": [], "p": "x", "o": "a"}]}):
            with self.subTest(graph=graph), self.assertRaises(ValueError):
                kernel.validate_graph(graph)

    def test_empty_type_is_rejected(self):
        for value in ("", "   ", None, []):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "type absent"):
                kernel.validate_graph({"nodes": [{"id": "a", "type": value}], "edges": []})


class FoldbackProtocolTests(unittest.TestCase):
    def setUp(self):
        self.sources = {"fm/1", "law/7", "law/44"}
        demo = kernel.synthetic_demo(self.sources)
        self.incident = demo["incident"]
        self.artifacts = demo["artifacts"]
        self.events = demo["events"]

    def replay(self):
        return kernel.replay_incident(self.incident, self.artifacts, self.events, self.sources)

    def test_complete_synthetic_loop_is_explicitly_limited(self):
        result = self.replay()
        self.assertEqual((result["state"], result["verifiedReuses"]), ("reused", 1))
        self.assertIn("synthetic", result["meaning"])

    def test_skipping_reproduction_is_rejected(self):
        self.events.pop(1)
        with self.assertRaisesRegex(ValueError, "bad transition"):
            self.replay()

    def test_claiming_a_guard_without_negative_control_is_rejected(self):
        self.events[2]["runRefs"] = ["demo:positive"]
        with self.assertRaisesRegex(ValueError, "positive and negative"):
            self.replay()

    def test_controls_for_another_guard_cannot_promote_this_guard(self):
        self.artifacts[3]["guardRef"] = "demo:candidate"
        with self.assertRaisesRegex(ValueError, "not bound"):
            self.replay()

    def test_reproduction_must_bind_the_failed_artifact(self):
        self.artifacts[1]["subjectRef"] = "demo:guard"
        with self.assertRaisesRegex(ValueError, "not bound"):
            self.replay()

    def test_reuse_cannot_use_an_unpromoted_guard(self):
        new_guard = dict(self.artifacts[2], id="another:guard")
        self.artifacts.append(new_guard)
        self.events[-1]["guardRefs"] = [new_guard["id"]]
        with self.assertRaisesRegex(ValueError, "not promoted"):
            self.replay()

    def test_retrying_the_same_reuse_is_not_new_momentum(self):
        self.events.append(dict(self.events[-1], id="demo:retry"))
        self.assertEqual(self.replay()["verifiedReuses"], 1)

    def test_another_target_is_a_distinct_reuse(self):
        new_run = dict(self.artifacts[-1], id="another:reuse", target="heritage")
        self.artifacts.append(new_run)
        self.events.append(dict(self.events[-1], id="demo:another", domain="heritage", runRefs=[new_run["id"]]))
        self.assertEqual(self.replay()["verifiedReuses"], 2)

    def add_second_guard(self):
        guard = dict(self.artifacts[2], id="second:guard")
        negative = dict(self.artifacts[3], id="second:negative", guardRef=guard["id"])
        positive = dict(self.artifacts[4], id="second:positive", guardRef=guard["id"])
        self.artifacts.extend([guard, negative, positive])
        self.events[2]["guardRefs"].append(guard["id"])
        self.events[2]["runRefs"].extend([negative["id"], positive["id"]])
        return guard

    def test_controls_split_across_guards_cannot_promote_either(self):
        self.add_second_guard()
        self.events[2]["runRefs"] = ["demo:negative", "second:positive"]
        with self.assertRaisesRegex(ValueError, "each guard"):
            self.replay()

    def test_reuse_counts_its_bound_guard_without_cross_product(self):
        guard = self.add_second_guard()
        self.events[-1]["guardRefs"].append(guard["id"])
        self.assertEqual(self.replay()["verifiedReuses"], 1)

    def test_same_origin_domain_is_not_cross_domain_reuse(self):
        run = next(a for a in self.artifacts if a["id"] == "demo:reuse")
        run["target"] = self.events[0]["domain"]
        self.events[-1]["domain"] = run["target"]
        with self.assertRaisesRegex(ValueError, "differ from origin"):
            self.replay()

    def test_reuse_target_must_match_event_domain(self):
        self.events[-1]["domain"] = "heritage"
        with self.assertRaisesRegex(ValueError, "match the event domain"):
            self.replay()

    def test_reuse_input_digest_is_bound_to_scene_content(self):
        run = next(a for a in self.artifacts if a["id"] == "demo:reuse")
        run["inputSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "input hash does not match"):
            self.replay()

    def test_reuse_input_reference_cannot_be_omitted(self):
        run = next(a for a in self.artifacts if a["id"] == "demo:reuse")
        del run["inputRef"]
        with self.assertRaisesRegex(ValueError, "bound scene artifact"):
            self.replay()

    def test_duplicate_event_identity_is_rejected(self):
        self.events.append(copy.deepcopy(self.events[-1]))
        with self.assertRaisesRegex(ValueError, "duplicate event"):
            self.replay()

    def test_unresolved_source_or_artifact_is_rejected(self):
        self.incident["sourceRefs"] = ["missing/source"]
        with self.assertRaisesRegex(ValueError, "unresolved incident source"):
            self.replay()
        self.incident["sourceRefs"] = ["fm/1"]
        self.incident["artifactRefs"] = ["missing/artifact"]
        with self.assertRaisesRegex(ValueError, "unresolved incident artifact"):
            self.replay()

    def test_altered_artifact_bytes_fail_hash_binding(self):
        self.artifacts[1]["content"] += " forged"
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.replay()

    def test_unresolved_domain_is_rejected(self):
        self.events[0]["domain"] = "planetary-certain-success"
        with self.assertRaisesRegex(ValueError, "unresolved event domain"):
            self.replay()

    def test_reference_collections_cannot_masquerade_as_arrays(self):
        for bad in ("demo:candidate", {"demo:candidate": True}, ["demo:candidate", "demo:candidate"], [[]]):
            with self.subTest(bad=bad):
                self.events[0]["artifactRefs"] = bad
                with self.assertRaisesRegex(ValueError, "array of unique string"):
                    self.replay()

    def test_candidate_cannot_start_from_an_unrelated_bound_artifact(self):
        self.events[0]["artifactRefs"] = ["demo:guard"]
        with self.assertRaisesRegex(ValueError, "candidate artifacts must be bound"):
            self.replay()

    def test_empty_history_is_not_a_successful_replay(self):
        self.events = []
        with self.assertRaisesRegex(ValueError, "events must be nonempty"):
            self.replay()

    def test_nonobject_events_are_validation_failures(self):
        self.events[0] = None
        with self.assertRaisesRegex(ValueError, "event must be an object"):
            self.replay()

    def test_unhashable_artifact_reference_is_a_validation_failure(self):
        self.artifacts[-1]["inputRef"] = []
        with self.assertRaisesRegex(ValueError, "unresolved artifact inputRef"):
            self.replay()


class ArchiveCompilationTests(unittest.TestCase):
    def test_snapshot_metrics_and_determinism(self):
        first = kernel.compile_observatory(kernel.HERE / "out")
        second = kernel.compile_observatory(kernel.HERE / "out")
        self.assertEqual(kernel.canonical_bytes(first), kernel.canonical_bytes(second))
        snapshot = first["snapshot"]
        self.assertEqual((snapshot["nodeCount"], snapshot["edgeCount"]), (2181, 7222))
        self.assertEqual(snapshot["metrics"]["quotedNumbers"], 34)
        self.assertEqual(snapshot["metrics"]["unlinkedFailureModes"], 95)
        self.assertEqual(snapshot["metrics"]["unlinkedHeuristics"], 317)
        self.assertEqual(sum(c["check"] == "receipt-sha256" for c in snapshot["integrity"]["checks"]), 8)
        self.assertTrue(first["demo"]["synthetic"])
        self.assertTrue(all(d["evidence"] == "proposed" for d in first["domains"]))

    def compile_with_changed_receipt(self, mutate):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "atlas.json").write_bytes((kernel.HERE / "out" / "atlas.json").read_bytes())
            receipt = json.loads((kernel.HERE / "out" / "receipt.json").read_text())
            mutate(receipt)
            (root / "receipt.json").write_bytes(kernel.canonical_bytes(receipt))
            return kernel.compile_observatory(root)

    def test_empty_receipt_digest_map_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "eight canonical"):
            self.compile_with_changed_receipt(lambda r: r.update(sha256={}))

    def test_partial_receipt_digest_coverage_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "eight canonical"):
            self.compile_with_changed_receipt(lambda r: r["sha256"].pop("atlas.ttl"))

    def test_receipt_pin_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "source pins disagree"):
            self.compile_with_changed_receipt(lambda r: r["inputs"].update({"x3d.docs": "other-pin"}))

    def test_receipt_digest_must_be_lowercase_sha256(self):
        with self.assertRaisesRegex(ValueError, "invalid receipt SHA-256"):
            self.compile_with_changed_receipt(lambda r: r["sha256"].update({"atlas-claims.jsonl": "not-a-digest"}))

    def test_canonicalization_is_order_independent_and_rejects_nan(self):
        self.assertEqual(kernel.canonical_bytes({"b": 2, "a": 1}), kernel.canonical_bytes({"a": 1, "b": 2}))
        with self.assertRaises(ValueError):
            kernel.canonical_bytes({"value": float("nan")})

    def test_metadata_booleans_are_not_integer_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph = {"nodes": [{"id": "law/1", "type": "Law"}], "edges": [],
                     "meta": {"counts": {"Law": True}, "edges": {}}}
            (root / "atlas.json").write_bytes(kernel.canonical_bytes(graph))
            # No receipt is needed: shape validation must precede file assertions.
            with self.assertRaisesRegex(ValueError, "nonnegative integer counts"):
                kernel.compile_observatory(root)

    def test_equal_but_empty_pins_are_not_a_bound_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph = {"nodes": [{"id": "law/1", "type": "Law"}], "edges": [],
                     "meta": {"counts": {"Law": 1}, "edges": {}, "inputs": {}}}
            (root / "atlas.json").write_bytes(kernel.canonical_bytes(graph))
            (root / "receipt.json").write_bytes(kernel.canonical_bytes({"inputs": {}}))
            with self.assertRaisesRegex(ValueError, "source pins disagree"):
                kernel.compile_observatory(root)


if __name__ == "__main__":
    unittest.main()
