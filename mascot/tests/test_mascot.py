"""The mascot scenes are data: they rebuild byte for byte, pass the pinned validator, and the breeding record holds."""
from __future__ import annotations

import json
import math
import random
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "tools"))
import build_mascot as bm  # noqa: E402
import evolve  # noqa: E402

BOARD = json.loads((ROOT / "frontier" / "runs" / "frontier-2026-11-23" / "board.json").read_text(encoding="utf-8"))
ELITES = json.loads((HERE / "v6" / "elites.json").read_text(encoding="utf-8"))
GAMED = json.loads((HERE / "v6" / "run1-gamed" / "elites.json").read_text(encoding="utf-8"))


class Scenes(unittest.TestCase):
    def test_v5_rebuilds_to_the_committed_bytes(self):
        x, facts = bm.build("v5", BOARD, {})
        self.assertEqual(x, (HERE / "v5" / "gobbler-v5.x3d").read_text(encoding="utf-8"))
        self.assertEqual((facts["feathers"], facts["gems"], facts["thesis_studs"]), (len(BOARD["rows"]), len(BOARD["rows"]), 13))

    def test_v6_rebuilds_from_its_recorded_genome(self):
        hero = json.loads((HERE / "v6" / "gobbler-v6.facts.json").read_text(encoding="utf-8"))
        x, _ = bm.build("v6", BOARD, hero["genome"])
        self.assertEqual(x, (HERE / "v6" / "gobbler-v6.x3d").read_text(encoding="utf-8"))
        self.assertIn(hero["genome"], [dict(bm.DEFAULT_GENOME, **e["genome"]) for e in ELITES["elites"]])

    def test_beads_count_the_checks_passed(self):
        _, facts = bm.build("v5", BOARD, {})
        self.assertEqual(facts["beads"], sum(r["assay"]["passed"] for r in BOARD["rows"]))

    def test_feather_length_follows_the_score(self):
        lay = bm.fan_layout(BOARD["rows"], bm.DEFAULT_GENOME)
        by = sorted(lay, key=lambda f: f["row"]["score"])
        self.assertTrue(all(a["length"] <= b["length"] + 1e-9 for a, b in zip(by, by[1:])))

    def test_half_turn_camera_has_a_unit_axis(self):
        # The control that failed first: looking straight back along +Z used to write the axis 0 0 0.
        ax = bm.look_at((0, 5, -20), (0, 5, 0))
        self.assertAlmostEqual(math.sqrt(sum(c * c for c in ax[:3])), 1.0, places=6)
        self.assertAlmostEqual(ax[3], math.pi, places=6)

    def test_scenes_pass_the_pinned_validator(self):
        try:
            import validate_scene as vs
            identity = vs.instrument_identity(); vs.load_vendor(identity)
        except Exception as e:                                    # the validator's own dependencies are absent
            self.skipTest(f"pinned validator not runnable here: {e}")
        for p in (HERE / "v5" / "gobbler-v5.x3d", HERE / "v6" / "gobbler-v6.x3d"):
            self.assertEqual(vs.validate_bytes(p.read_bytes(), identity)["status"], "pass", p.name)
        broken = (HERE / "v5" / "gobbler-v5.x3d").read_text(encoding="utf-8").replace("<Sphere radius='0.085'/>", "<Sphere radius='wide'/>", 1)
        self.assertNotEqual(vs.validate_bytes(broken.encode(), identity)["status"], "pass", "a planted defect must be refused")


class Breeding(unittest.TestCase):
    def test_recorded_measures_recompute(self):
        for e in ELITES["elites"] + GAMED["elites"]:
            self.assertEqual(evolve.measure(BOARD["rows"], e["genome"]), e["measure"])
        self.assertEqual(evolve.measure(BOARD["rows"], bm.DEFAULT_GENOME), ELITES["hand_drawn_v5_fan"])

    def test_first_run_flattened_the_data_and_the_frozen_run_did_not(self):
        honest = ELITES["hand_drawn_v5_fan"]["median_length_share"]
        self.assertTrue(all(e["measure"]["median_length_share"] > honest for e in GAMED["elites"]))
        self.assertTrue(all(e["genome"]["profile"] < 1.0 for e in GAMED["elites"]))
        self.assertTrue(all(e["measure"]["median_length_share"] == honest and e["genome"]["profile"] == 1.0 for e in ELITES["elites"]))

    def test_a_frozen_gene_cannot_be_mutated(self):
        evolve.FROZEN.clear(); evolve.FROZEN["profile"] = 1.0
        try:
            rng = random.Random(1); g = evolve.random_genome(rng)
            for _ in range(200): g = evolve.mutate(g, rng)
            self.assertEqual(g["profile"], 1.0)
        finally:
            evolve.FROZEN.clear()

    def test_archive_is_full_and_every_entry_passed_the_validator(self):
        for run in (ELITES, GAMED):
            self.assertEqual(len(run["elites"]), 9)
            self.assertEqual(run["counts"]["refused_validator"], 0)
            self.assertEqual(run["counts"]["validated"], run["counts"]["admitted"])
            self.assertEqual(run["model_calls"], 0)


if __name__ == "__main__":
    unittest.main()
