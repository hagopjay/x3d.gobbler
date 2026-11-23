"""The frontier lens: the committed board is current, repeatable, and its controls fail where they must."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import assay_frontiers as af  # noqa: E402

RUN = HERE / "runs" / "frontier-2026-11-23" / "board.json"


def frontier(**flags):
    base = {"optimizer": False, "model_required": False, "model_optional": False, "data_open": False,
            "data_restricted": False, "swarm": False, "seeded": True, "neg_controls": True, "holdout": True}
    base.update(flags)
    return {"id": "x", "family": "A", "status": "unexplored", "title": "t", "gain": "g", "first_step": "f",
            "judged": {a: 3 for a in af.AXES}, "grader": {"kind": "code", "name": "some instrument"},
            "flags": base, "atlas_themes": ["bench"], "evidence": []}


def status(result, thesis):
    return next(c["status"] for c in result["checks"] if c["thesis"] == thesis)


class Board(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.committed = json.loads(RUN.read_text(encoding="utf-8"))
        cls.fresh = af.run(HERE / "frontiers.json", None)

    def test_committed_board_was_made_by_this_tool_from_this_registry(self):
        for key in ("tool_sha256", "registry_sha256", "atlas_sha256"):
            self.assertEqual(self.committed["score_tuple"][key], self.fresh["score_tuple"][key], key)

    def test_ranks_scores_and_rank_ranges_rebuild_identically(self):
        pick = lambda b: [(r["id"], r["rank"], r["score"], r["lens_rank"], r["perturbation"], r["assay"]["readiness"]) for r in b["rows"]]
        self.assertEqual(pick(self.committed), pick(self.fresh))

    def test_no_model_call_and_no_spend(self):
        self.assertEqual((self.committed["score_tuple"]["model_calls"], self.committed["score_tuple"]["spend_usd"]), (0, 0))

    def test_every_cited_path_was_found_when_the_run_was_made(self):
        self.assertEqual(self.committed["counts"]["evidence_missing"], 0)
        self.assertGreater(self.committed["counts"]["evidence_paths"], 90)

    def test_held_out_seed_agrees_on_the_top_ten(self):
        self.assertGreaterEqual(self.committed["stability"]["overlap"], 8)

    def test_a_stop_is_never_averaged_away(self):
        stops = [r for r in self.committed["rows"] if r["assay"]["worst"] == "stop"]
        self.assertTrue(stops)
        for r in stops:
            self.assertTrue(any(g.startswith(("T7", "T8")) for g in r["assay"]["gates"]), r["id"])


class ControlsThatMustFail(unittest.TestCase):
    def test_clean_frontier_passes_every_applicable_check(self):
        r = af.assay(frontier(), None)
        self.assertEqual((r["worst"], r["passed"], r["applicable"]), ("note", 7, 8))   # the one remark: no prior evidence cited

    def test_optimiser_without_holdout_stops(self):
        self.assertEqual(status(af.assay(frontier(optimizer=True, holdout=False), None), "T8"), "stop")

    def test_optimiser_without_controls_stops(self):
        self.assertEqual(status(af.assay(frontier(optimizer=True, neg_controls=False), None), "T8"), "stop")

    def test_optimiser_with_both_still_warns_and_needs_a_cap(self):
        r = af.assay(frontier(optimizer=True), None)
        self.assertEqual((status(r, "T8"), status(r, "T13")), ("warn", "warn"))

    def test_restricted_data_stops(self):
        self.assertEqual(status(af.assay(frontier(data_restricted=True), None), "T7"), "stop")

    def test_human_or_model_judge_is_gated_twice(self):
        for kind in ("human", "model"):
            f = frontier(); f["grader"] = {"kind": kind, "name": "an opinion"}
            r = af.assay(f, None)
            self.assertEqual((status(r, "T3"), status(r, "T5"), status(r, "T1")), ("gate", "gate", "warn"), kind)

    def test_paid_first_step_is_gated(self):
        self.assertEqual(status(af.assay(frontier(model_required=True), None), "T11"), "gate")

    def test_missing_evidence_path_is_reported(self):
        f = frontier(); f["evidence"] = ["x3d.gobbler:no/such/file.md"]
        self.assertEqual(af.assay(f, HERE.parents[1])["evidence_missing"], ["x3d.gobbler:no/such/file.md"])

    def test_registry_refusals(self):
        themes = {"bench"}
        good = {"families": {"A": "a"}, "frontiers": [frontier()]}
        self.assertEqual(af.validate_registry(good, themes), [])
        for edit, word in ((lambda f: f.update(atlas_themes=["nope"]), "atlas theme"),
                           (lambda f: f["judged"].update(effort=6), "integers 1..5"),
                           (lambda f: f.update(status="explored"), "no evidence path"),
                           (lambda f: f["flags"].update(data_open=True, data_restricted=True), "both open and restricted"),
                           (lambda f: f["grader"].update(kind="vibes"), "grader kind")):
            bad = copy.deepcopy(good); edit(bad["frontiers"][0])
            errs = af.validate_registry(bad, themes)
            self.assertTrue(any(word in e for e in errs), (word, errs))
        dup = copy.deepcopy(good); dup["frontiers"].append(copy.deepcopy(dup["frontiers"][0]))
        self.assertTrue(any("duplicate" in e for e in af.validate_registry(dup, themes)))

    def test_readiness_moves_the_score_and_effort_is_inverted(self):
        j = {a: 3 for a in af.AXES}; w = af.LENSES["balanced"]
        self.assertGreater(af.composite(j, 1.0, w), af.composite(j, 0.5, w))
        self.assertGreater(af.composite(dict(j, effort=1), 1.0, w), af.composite(dict(j, effort=5), 1.0, w))


if __name__ == "__main__":
    unittest.main()
