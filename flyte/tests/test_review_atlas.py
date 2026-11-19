"""Offline Atlas bootstrap regressions from the external review."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gobbler_flyte import atlas
from gobbler_flyte.memory import MemoryStore
from gobbler_flyte.runner import Ctx, load_config


class AtlasRecovery(unittest.TestCase):
    def partial_seed(self, store):
        put = store.put

        def interrupted(rec):
            if rec.memory_id == "aie:K1":
                raise RuntimeError("simulated crash before code sketches")
            return put(rec)

        with patch.object(store, "put", side_effect=interrupted):
            with self.assertRaisesRegex(RuntimeError, "simulated crash"):
                atlas.seed_library(store)
        self.assertIsNotNone(store.get("aie:T13"))
        self.assertIsNone(store.get("aie:K1"))

    def test_context_startup_finishes_a_seed_interrupted_after_theses(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib = MemoryStore(Path(tmp) / "library.sqlite")
            self.partial_seed(lib)
            lib.close()
            ctx = Ctx(state_dir=Path(tmp), mode="offline", now="2026-11-19T00:00:00Z",
                      config=load_config(), allowance={})
            try:
                self.assertIsNotNone(ctx.library.get("aie:K1"), "T13 is not a seed-completion marker")
                self.assertEqual(len(ctx.library.all()), 218 + 13 + 67 + 51)
                self.assertTrue(atlas.seed_complete(ctx.library))
            finally:
                ctx.mem.close()
                ctx.library.close()

    def test_deleted_sketch_or_evidence_invalidates_completeness(self):
        lib = MemoryStore()
        try:
            atlas.seed_library(lib)
            self.assertTrue(atlas.seed_complete(lib))
            with lib.db:
                lib.db.execute("DELETE FROM memory WHERE id = ?", ("aie:K1",))
            self.assertFalse(atlas.seed_complete(lib))
            self.assertEqual(atlas.seed_library(lib)["procedure"], 1)
            self.assertTrue(atlas.seed_complete(lib))
            with lib.db:
                lib.db.execute("DELETE FROM evidence WHERE id = ?", ("aie:M1",))
            self.assertFalse(atlas.seed_complete(lib))
            self.assertEqual(atlas.seed_library(lib)["evidence"], 1)
            self.assertTrue(atlas.seed_complete(lib))
        finally:
            lib.close()

    def test_conflicting_existing_row_is_not_silently_accepted(self):
        lib = MemoryStore()
        try:
            atlas.seed_library(lib)
            row = lib.get("aie:K1").model_copy(update={"subject_sha256": "0" * 64})
            with lib.db:
                lib.db.execute("DELETE FROM memory WHERE id = ?", ("aie:K1",))
            lib.put(row)
            with self.assertRaisesRegex(ValueError, "immutable memory id collision"):
                atlas.seed_library(lib)
        finally:
            lib.close()

    def test_thesis_grade_never_exceeds_any_cited_concept(self):
        lib = MemoryStore()
        try:
            atlas.seed_library(lib)
            t5 = lib.get("aie:T5")
            self.assertEqual([lib.get(p).evidence_level for p in t5.parent_ids], ["S"] * 5)
            self.assertEqual(t5.evidence_level, "S")
            for row in atlas.load()["THESES"]:
                rec = lib.get("aie:" + row[0])
                if any(lib.get(p).evidence_level == "S" for p in rec.parent_ids):
                    self.assertEqual(rec.evidence_level, "S", rec.memory_id)
        finally:
            lib.close()

    def test_explicit_rebuild_archives_original_immutable_library(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "library.sqlite"
            lib = MemoryStore(path)
            atlas.seed_library(lib)
            old = lib.get("aie:T5").model_copy(update={"evidence_level": "L"})
            with lib.db:
                lib.db.execute("DELETE FROM memory WHERE id = ?", (old.memory_id,))
            lib.put(old)
            self.assertFalse(atlas.seed_complete(lib))
            with self.assertRaisesRegex(ValueError, "explicit rebuild"):
                atlas.seed_library(lib)
            lib.close()
            receipt = atlas.rebuild_library(path)
            before = MemoryStore(receipt["archive"])
            after = MemoryStore(path)
            try:
                self.assertEqual(before.get("aie:T5").evidence_level, "L")
                self.assertEqual(after.get("aie:T5").evidence_level, "S")
                self.assertTrue(atlas.seed_complete(after))
            finally:
                before.close()
                after.close()


if __name__ == "__main__":
    unittest.main()
