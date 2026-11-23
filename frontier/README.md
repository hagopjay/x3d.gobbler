# The Loom frontier board

Where should the Loom go next? This folder is the Assayer's answer: 64 candidate frontiers, each put through the
thirteen theses of the AI Engineering Atlas (rev 28, pinned in `flyte/atlas/`), ranked five ways, and tested for
how far each rank moves when the opinions behind it are wrong.

| File | What it is |
|---|---|
| `frontiers.json` | The registry. 64 frontiers in 5 families, hand-written. Each declares a grader, nine flags, five judged scores (1 to 5), Atlas themes, prior evidence paths and a first step. |
| `assay_frontiers.py` | The lens. No model call, no network (standard library plus this repo's Atlas loader). One check per thesis, readiness, five weightings, 2,000 seeded perturbations, a held-out seed. |
| `runs/frontier-2026-11-23/board.json` | The run record, with its score tuple (tool, registry and Atlas hashes, weights, seeds, repository heads). |
| `runs/frontier-2026-11-23/BOARD.md` | The same board as a table, plus every gate and the first step of the top 15. |
| `tests/test_frontier.py` | 16 tests: the committed board rebuilds identically, and 10 planted controls fail where they must. |

```bash
python3 frontier/assay_frontiers.py --repos .. --out frontier/runs/<name>   # --repos: folder holding the sibling checkouts
python3 -m pytest -q frontier/tests
```

## What is measured and what is opinion

| Part | Grade | Source |
|---|---|---|
| Five judged scores per frontier, and so every score and rank | **Suspected** | one model's opinion, written in `frontiers.json` on 23 Nov 2026 |
| Thesis checks (pass, warn, gate, stop) | Confirmed as computed | `assay_frontiers.py` applied to the declared grader and flags; the flags themselves are claims |
| 101 evidence paths, 0 missing | Confirmed | looked up on disk in 9 sibling checkouts at the heads recorded in `board.json` |
| Rank ranges | Confirmed as computed | 2,000 draws, seed 7: each judged score moves by -1, 0 or +1 (odds 1:2:1), each weight by up to 30 percent |

Score = 100 x weighted mean of the five judged axes (effort inverted) x (0.7 + 0.3 x readiness), where readiness is
checks passed over checks that apply. Balanced weights: flywheel 0.30, relevance 0.20, visual 0.20, gravitas 0.15,
effort 0.15.

## Result (run `frontier-2026-11-23`)

Counts: 25 domain, 15 AI engineering, 11 algorithmic, 10 generative art, 3 adversarial. By state: 22 unexplored,
23 touched, 15 explored, 4 deep. Worst check per frontier: 30 clean, 18 warn, 2 note, 11 gated, 3 stop.
54 of 64 first steps need no model call.

| # | Frontier | Family | State | Score | Checks | Rank range (5th to 95th) | In top 10 |
|--:|---|---|---|--:|:-:|:-:|--:|
| 1 | x3d.xray: binaries, code and captures as cities | domain | explored | 88.0 | 8/8 | 1 to 21 | 81% |
| 2 | Cross-engine differential rendering as the oracle | algorithmic | touched | 87.0 | 8/8 | 1 to 24 | 73% |
| 3 | BIM and construction through IfcOpenShell | domain | unexplored | 86.6 | 7/8 | 1 to 23 | 72% |
| 4 | OpenUSD conformance bridge | domain | touched | 86.0 | 8/8 | 1 to 27 | 64% |
| 5 | Quality-diversity evolution of X3D scenes | algorithmic | unexplored | 85.5 | 8/10 | 2 to 25 | 61% |
| 6 | STEM, maths and PolyXandria | domain | deep | 84.0 | 8/8 | 1 to 28 | 62% |
| 7 | Prompt injection through 3D files | adversarial | unexplored | 83.0 | 8/8 | 1 to 33 | 53% |
| 8 | A public scoreboard of models on Loom tasks | AI engineering | unexplored | 82.8 | 7/8 | 3 to 33 | 39% |
| 9 | The hostile-file corpus against every reader | adversarial | explored | 82.0 | 8/8 | 3 to 35 | 38% |
| 10 | Physics engines | domain | deep | 81.0 | 8/8 | 1 to 36 | 42% |

Rows 11 to 64 are in `BOARD.md`.

### Four things the run says

1. **The order is soft; the tier is not.** Across the top 20 the rank range is 31 places wide on average. No
   frontier is in the top 10 in more than 81 percent of draws. Read the board as tiers: a first tier of about 14
   (those whose 5th-percentile rank is 3 or better), not as an ordered list. The top-10 set is the same on the
   held-out seed 23 (10 of 10).
2. **Changing the question changes the answer.** Top three by weighting: flywheel-first gives cross-render,
   openusd, bim-ifc; showpiece gives xray, heritage, molecules; gravitas gives openusd, bim-ifc, x3d-injection;
   quick-win gives token-economy, hostile-all, mcp-loom. Only cross-render, bim-ifc, openusd and qd-evolve are in
   the top 8 of three or more of the five.
3. **The AI-engineering frontiers that rank high are the ones with a code grader.** x3d-bench (8), rag-loom (15),
   mcp-loom (17) and token-economy (22) all grade by code. The ones that need a judge or a paid first step sit
   lower because the lens gates them, not because they matter less: picture-judge (57), memory-trial (56),
   dspy-gepa (55), finetune (49).
4. **Three stops.** rl-gym and agent-swarm put an optimiser in front of a grader with no hold-out (T8);
   video-world has restricted data (T7), no code grader (T3, T5) and a paid first step (T11).

## Limits

- One model wrote every judged score. A second scorer (him, or another model) is the obvious next control; the
  registry format takes it without change.
- The flags are declared, not tested. `neg_controls: true` says controls can exist, not that they have been planted.
- Readiness counts checks equally. A `stop` is printed beside the rank and never averaged away, but it only costs
  the frontier its share of the readiness factor.
- Effort is a guess in sessions, not a measurement.
