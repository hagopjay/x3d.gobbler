"""Adversarial memory/transport regressions; no model, API, database service or world required."""
from __future__ import annotations

import copy
import hashlib
import json
import unittest

from gobbler_flyte.memory import (EvidenceRef, MemoryRecord, MemoryStore, Reader, audit_contamination,
                                 compile_context, effective_exposures, wire)
from gobbler_flyte.transport import cjson, export, finalize, validate


NOW = "2026-11-19T00:00:00Z"


def mem(name, **updates):
    values = dict(memory_id=name, kind="counterexample", text="counterexample fixture", readers=["weaver"],
                  valid_from="2026-11-18T00:00:00Z", recorded_by="witness")
    return MemoryRecord(**{**values, **updates})


def packet(store, **kw):
    return compile_context(store, Reader("weaver", NOW, {}), kinds=("counterexample", "episode", "decision"),
                           query="fixture", **kw)


class ContextBoundary(unittest.TestCase):
    def setUp(self):
        self.store = MemoryStore()
        self.addCleanup(self.store.close)

    def test_private_exclusions_do_not_reach_packet_or_change_hash(self):
        self.store.put(mem("visible"))
        original = packet(self.store, max_bytes=600)
        for i in range(40):
            self.store.put(mem(f"private:patient-{i}", readers=["keeper"]))
        diagnostics = {}
        current = packet(self.store, max_bytes=600, diagnostics=diagnostics)
        self.assertEqual(original, current)
        self.assertNotIn("private:patient", wire(current))
        self.assertEqual(diagnostics["excluded"]["private:patient-0"], "not_a_reader")
        self.assertLessEqual(len(wire(current).encode()), 600)

    def test_final_hash_and_metadata_count_toward_budget(self):
        self.store.put(mem("visible", text="A" * 250))
        p = packet(self.store, max_bytes=550)
        self.assertLessEqual(len(wire(p).encode()), 550)
        with self.assertRaisesRegex(ValueError, "envelope"):
            packet(self.store, max_bytes=10)
        for bad in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                packet(self.store, max_bytes=bad)

    def test_contradiction_bundle_cannot_smuggle_hidden_partner(self):
        self.store.put(mem("allowed", contradicts=["hidden"]))
        self.store.put(mem("hidden", readers=["keeper"], text="PRIVATE_SECRET"))
        diagnostics = {}
        p = packet(self.store, diagnostics=diagnostics)
        self.assertEqual(p["memories"], [])
        self.assertNotIn("hidden", wire(p))
        self.assertNotIn("PRIVATE_SECRET", wire(p))
        self.assertEqual(diagnostics["excluded"]["allowed"], "contradiction_partner_hidden")
        self.assertEqual(diagnostics["excluded"]["hidden"], "not_a_reader")

    def test_late_sealed_evidence_and_diamond_union_remain_filtered(self):
        self.store.put(mem("root", evidence_ids=["late"]))
        self.store.put(mem("left", parent_ids=["root"]))
        self.store.put(mem("right", parent_ids=["root"]))
        self.store.put(mem("diamond", parent_ids=["left", "right"]))
        before = {}
        self.assertEqual(packet(self.store, diagnostics=before)["memories"], [])
        self.assertEqual(before["excluded"]["diamond"], "unknown_evidence")
        self.store.put_evidence(EvidenceRef(evidence_id="late", exposure="sealed", sha256="a" * 64, instrument="fixture"))
        after = {}
        self.assertEqual(packet(self.store, diagnostics=after)["memories"], [])
        self.assertEqual(after["excluded"]["diamond"], "held_out")
        self.assertEqual(effective_exposures(self.store, self.store.get("diamond")), ({"development", "sealed"}, None))

    def test_deep_lineage_is_iterative_and_cyclic_corruption_does_not_erase_taint(self):
        self.store.put(mem("root", exposures=["sealed"]))
        parent = "root"
        for i in range(1100):
            name = f"deep:{i}"
            self.store.put(mem(name, parent_ids=[parent]))
            parent = name
        exposures, reason = effective_exposures(self.store, self.store.get(parent))
        self.assertEqual((exposures, reason), ({"development", "sealed"}, None))
        # Public put prevents introducing a cycle; this simulates a corrupt import
        # to exercise defensive traversal without claiming public writes allow it.
        a = mem("cycle:a", parent_ids=["cycle:b"])
        b = mem("cycle:b", parent_ids=["cycle:a"], exposures=["sealed"])
        self.store._put("memory", a.memory_id, wire(a))
        self.store._put("memory", b.memory_id, wire(b))
        self.assertEqual(effective_exposures(self.store, a), ({"development", "sealed"}, None))

    def test_revocation_and_missing_parent_fail_closed(self):
        self.store.put(mem("root"))
        self.store.put(mem("child", parent_ids=["root"]))
        self.store.revoke("root", "withdrawn")
        diagnostics = {}
        self.assertEqual(packet(self.store, diagnostics=diagnostics)["memories"], [])
        self.assertEqual(diagnostics["excluded"]["child"], "revoked_lineage")
        with self.store.db:
            self.store.db.execute("DELETE FROM memory WHERE id='root'")
        diagnostics = {}
        self.assertEqual(packet(self.store, diagnostics=diagnostics)["memories"], [])
        self.assertEqual(diagnostics["excluded"]["child"], "incomplete_lineage")


class TransportBoundary(unittest.TestCase):
    def setUp(self):
        self.store = MemoryStore()
        self.addCleanup(self.store.close)

    def rows(self):
        return export(self.store, recorded_at=NOW)

    def test_missing_provenance_and_acl_are_not_widened(self):
        self.store.put(mem("cx", readers=["keeper"], evidence_ids=["missing"], subject_sha256="a" * 64))
        row = next(r for r in self.rows() if r["record_type"] == "memory")
        self.assertFalse(row["exposure"]["lineage_complete"])
        self.assertIn("unknown", row["exposure"]["roles"])
        self.assertEqual(row["acl"]["classification"], "restricted")
        self.assertEqual(row["acl"]["read_principals"], ["organ:keeper"])
        self.assertEqual(row["recorded_at"], NOW)
        self.assertNotEqual(row["recorded_at"], row["valid_time"]["from"])

    def test_ancestor_reader_restrictions_survive_export(self):
        self.store.put(mem("parent", readers=["keeper"], subject_sha256="a" * 64))
        self.store.put(mem("child", readers=["weaver", "keeper"], parent_ids=["parent"], subject_sha256="b" * 64))
        child = next(r for r in self.rows() if "gobbler:child" in r.get("tags", []))
        self.assertEqual(child["acl"]["read_principals"], ["organ:keeper"])

    def test_registry_declaration_does_not_become_executed_refusal(self):
        self.store.put_evidence(EvidenceRef(evidence_id="source", exposure="development", sha256="a" * 64,
                                           instrument="Atlas source catalogue"))
        self.store.put(mem("claim", kind="semantic_claim", recorded_by="library", evidence_level="L", evidence_ids=["source"]))
        row = next(r for r in self.rows() if r["record_type"] == "evidence")
        self.assertEqual((row["origin"], row["grade"], row["status"]), ("source_read", "L", "not_run"))
        self.assertIn("Atlas source catalogue", row["method"])
        self.assertIsNone(row["run_id"])

    def test_unknown_decisions_and_twin_relations_are_not_invented(self):
        self.store.put(mem("decision", kind="decision", text="No decision was recorded", recorded_by="human", cycle=1))
        self.store.put(mem("cx", subject_sha256="a" * 64, cycle=1))
        self.store.put(mem("episode", kind="episode", parent_ids=["cx"], subject_sha256="b" * 64,
                           recorded_by="keeper", evidence_level="C", cycle=1))
        rows = [r for r in self.rows() if r["record_type"] == "memory"]
        dec = next(r for r in rows if r["payload"]["kind"] == "decision")["payload"]
        cx = next(r for r in rows if r["payload"]["kind"] == "counterexample")["payload"]
        self.assertEqual((dec["outcome"], dec["reviewer"]), ("abstain", "unrecorded"))
        self.assertIsNone(cx["lawful_twin_artifact_id"])

    def test_supplied_hashes_checked_without_normalization_repair(self):
        self.store.put(mem("decision", kind="decision", text="Unknown", recorded_by="human", cycle=1))
        row = next(r for r in self.rows() if r["record_type"] == "memory")
        self.assertTrue(validate([row])["valid"])
        tampered = copy.deepcopy(row)
        tampered["payload_sha256"] = "0" * 64
        self.assertFalse(validate([tampered])["valid"])
        # Even recomputing the envelope ID must not excuse a false payload hash.
        unsigned = {k: v for k, v in tampered.items() if k != "id"}
        tampered["id"] = "urn:x3d:memory:sha256:" + hashlib.sha256(cjson(unsigned)).hexdigest()
        errors = validate([tampered])
        self.assertFalse(errors["valid"])
        self.assertIn("payload_sha256", {e["path"] for e in errors["errors"]})

    def test_canonical_ids_and_declared_validation_scope(self):
        self.store.put_evidence(EvidenceRef(evidence_id="known", exposure="development", sha256="b" * 64,
                                           instrument="declared fixture instrument"))
        self.store.put(mem("known-cx", subject_sha256="b" * 64, evidence_ids=["known"]))
        self.store.put(mem("cx", subject_sha256="a" * 64))
        rows = self.rows()
        for row in rows:
            # Resolving local registry citations cannot establish canonical
            # artifact/run/source-parent closure in this partial projection.
            self.assertFalse(row["exposure"]["lineage_complete"])
            self.assertIn("unknown", row["exposure"]["roles"])
            self.assertIn("development", row["exposure"]["roles"])
            self.assertEqual(finalize(row)["id"], row["id"])
            supplied = {k: v for k, v in row.items() if k != "id"}
            self.assertTrue(row["id"].endswith(hashlib.sha256(cjson(supplied)).hexdigest()))
        checked = validate(rows)
        self.assertTrue(checked["valid"], checked)
        self.assertFalse(checked["restorable"])
        self.assertIn("reference closure", checked["validation_scope"])


if __name__ == "__main__":
    unittest.main()
