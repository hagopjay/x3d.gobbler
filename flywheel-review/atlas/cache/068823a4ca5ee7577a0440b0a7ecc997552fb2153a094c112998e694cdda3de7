# 14. Methods: how to learn, test and extend this base

> **Say it:** You learn X3D here by predicting a result, running the tool, comparing, grading the gap and recording a rule with a falsifier; a heuristic you cannot falsify is not in the ledger. **[L]**

| field | value |
|---|---|
| chapter code | `MET` |
| prerequisites | [00](00-start-here.md); any one of chapters 01 to 13 |
| after this you can | run the predict-run-compare loop on any drill; seed a failure and predict the diagnostic; audit a number for its pin; add a heuristic with the right grade; score your own pipeline against the tether |
| sources read | `x3d.docs@f172f67:docs/learn/*` (this base), `docs/tools-shared/{learn_lib,build_learn,check_learn}.py` |
| instruments used | `check_learn.py` and `build_learn.py` at this commit, Python 3.13 |

## 1. The map

```text
   READ the rule --> PREDICT the result --> RUN the tool --> COMPARE --> GRADE the gap
        ^                                                                   |
        |                                                                   v
   PIN + DATE  <---- RECORD heuristic with falsifier <---- EXPLAIN why prediction missed
        |
        +--> re-run at a new pin: add a dated row, demote on contradiction
```

| method | what you do | where it is practised | failure it prevents |
|---|---|---|---|
| M1 predict-then-run | write the expected output before running the drill | every L2 drill | reading answer keys as facts |
| M2 seed-a-failure | take a valid scene, apply one failure mode, predict the diagnostic code | [03](03-validator-and-gates.md), [02](02-loom-laws.md) | trusting a gate that never saw a bad input |
| M3 two-renderer reading | state a render claim as patch plus rig, then check it in a second renderer | [06](06-xite-the-oracle.md), [08](08-babylon-bridge.md) | one renderer agreeing with itself |
| M4 grade ladder | demote any number you cannot re-derive to [L] or [S] | [AUTHORING](AUTHORING.md) | rumours promoted to facts |
| M5 pin-and-diff | re-run a [C] row at a newer commit; record both | [A](A-validator-register.md), [F](F-source-map.md) | stale numbers |
| M6 minimal reproduction | cut a failing scene to the smallest file that still fails | [03](03-validator-and-gates.md) | bugs reported without evidence |
| M7 teach-back | restate a chapter as 3 heuristics each with a falsifier | this chapter | passive reading |

Read next: [02](02-loom-laws.md) for the failure modes to seed; [D](D-heuristics-ledger.md) for the rules to attack.

## 2. A four-week curriculum

| week | read | drills (run, do not skim) | checkpoint you can state |
|---|---|---|---|
| 1 | [01](01-the-tether.md), [03](03-validator-and-gates.md) | all L2 drills of 01 and 03 | which rung of the ladder catches a given fault, and which rung never will |
| 2 | [06](06-xite-the-oracle.md), [08](08-babylon-bridge.md), [10](10-blender-pipeline.md) | one L3 per chapter | a render claim with patch, rig and a second-renderer number |
| 3 | [04](04-mcp-for-agents.md), [05](05-semantic-layer.md), [02](02-loom-laws.md) | tool-call transcripts, SPARQL and SHACL drills | a repair loop and what valid-but-wrong still escapes it |
| 4 | [09](09-castle-engine.md), [11](11-gltf-usd-khronos.md), [12](12-unreal-tier1.md), [13](13-physics.md), [07](07-xray.md) | the not-run drills | one new row in a Numbers register, with its instrument, sent as a PR |

## 3. Cross-chapter patterns (the same lesson in different clothes)

| pattern | seen in | one-line form |
|---|---|---|
| exact oracle before judge | [01](01-the-tether.md), [05](05-semantic-layer.md) | if a file can answer exactly, do not ask a model |
| valid is not visible, not placed, not stable | [03](03-validator-and-gates.md), [05](05-semantic-layer.md), [13](13-physics.md) | every grammar pass opens a second question |
| producer and reader that share a reading agree on the bug | [07](07-xray.md) | pin raw stored values, not only producer-vs-reader agreement |
| a fallback must announce itself | [02](02-loom-laws.md), [08](08-babylon-bridge.md) | silent degradation reads as success |
| a number is true at a pin | [03](03-validator-and-gates.md), [A](A-validator-register.md) | name the commit or do not quote it |
| structure gates do not judge looks | [11](11-gltf-usd-khronos.md) | a valid glb can be empty |
| native hosts teach seams | [09](09-castle-engine.md) | n=1 engine: lessons, not rankings |
| status claims for unrun targets stay low | [12](12-unreal-tier1.md) | no install, no [C] |

## 4. Self-assessment: score your pipeline

```text
 tether score   unreliable   exact     valid != works   history must   someone answerable
 (one point     writer?      oracle?   (render check)   travel?        later?
  each)           [1]          [2]          [3]             [4]            [5]
 4-5 = loop + ledger     3 = ledger + gate     0-2 = a log table is enough
```


Give one point each (the tether score of [01](01-the-tether.md)): unreliable writer; exact oracle available; valid differs from works; history must travel with the artifact; someone answerable later.
4 to 5: full tether (loop plus ledger). 3: ledger plus gate. 2 or less: a log table is enough. Only X3D is measured in this base; any other family you score is your own [S] until you run it.

## Heuristics

| ID | Rule | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-MET-1 | Write the predicted answer before running a drill; a correct prediction teaches less than a wrong one. | L | method argument; no trial run | none (design rule) |
| H-MET-2 | Seed one failure at a time into a valid scene, so the diagnostic maps to one cause. | L | practice in chapters 02 and 03 | `x3d_mcp fork b4efcd3` |
| H-MET-3 | Demote on contradiction: record both numbers and the pins, never overwrite. | L | [AUTHORING](AUTHORING.md) section 6 | none (policy) |
| H-MET-4 | Give a heuristic a falsifier (a result that would refute it) or leave it out of the ledger. | L | [D](D-heuristics-ledger.md) construction | `check_learn.py` structure only |
| H-MET-5 | Run the drill before trusting its answer key; mark `Checked` honestly. | C | 89 of 97 drills carry a run record at this commit | `build_learn.py`, this commit |
| H-MET-6 | Prefer the lowest grade the evidence allows; a copied number is [L] at best. | L | grade mix below | Appendix C count |
| H-MET-7 | Cut a failing scene to the smallest file that still fails before reporting it. | L | practice in chapter 03 | `x3d_mcp fork b4efcd3` |
| H-MET-8 | Two independent readings agree only if tests pin a raw value; compare against stored values, not only each other. | C | chapter 07 gallery lesson | `x3d.xray@8fa6845` |

## Drills

### D-MET-1 Count the base
- **Level:** L1
- **Task:** Count heuristics, drills and numbers in the base.
- **Verify:** `python3 docs/tools-shared/build_learn.py` (first line of output).
- **Answer:** 161 heuristics, 97 drills, 277 numbers before this chapter was added.
- **Checked:** 2026-11-14 `build_learn.py` at this commit.

### D-MET-2 Grade mix
- **Level:** L2
- **Task:** From Appendix C, compute the share of [C], [L], [S] numbers and say what an [S] share of 4 of 277 implies about how the registers were written.
- **Verify:** `grep -c '| C |' docs/learn/C-numbers-ledger.md` and the same for L and S, or the header line of the appendix.
- **Answer:** 235 C, 38 L, 4 S before this chapter; [S] is rare because registers list measured rows first and carry unverified claims in prose (a limit of the registers).
- **Checked:** 2026-11-14 `learn_lib.py` count, Python 3.13.

### D-MET-3 Break the linter
- **Level:** L3
- **Task:** Delete the Instrument cell of one number row in a scratch copy and predict the linter's message.
- **Verify:** `python3 docs/tools-shared/check_learn.py` on the copy.
- **Answer:** `empty Instrument cell` for that `N-` id, exit status 1.
- **Checked:** 2026-11-14 `check_learn.py` at this commit.

### D-MET-4 Pin audit
- **Level:** L2
- **Task:** Pick three [C] rows from different chapters and find the repo and commit for each in Appendix F.
- **Verify:** open [F](F-source-map.md); each cited `repo@sha` must appear.
- **Answer:** every cited pair is listed with its chapters; a row whose source has no pair is a defect to report.
- **Checked:** not run.

### D-MET-5 Teach-back
- **Level:** L3
- **Task:** Restate one chapter as three heuristics with falsifiers and a grade each; submit as a PR to that chapter.
- **Verify:** `check_learn.py` passes and the new ids are unique.
- **Answer:** none fixed; the check is a clean lint plus a drill that would have caught the rule.
- **Checked:** not run.

## Honest limits

- The methods are a design, not a measured effect on learners; no trial of M1 to M7 exists. **[S]**
- The curriculum timings are an estimate. **[S]**
- Grade counts describe how rows were written, not how true the base is. **[L]**
- Cross-chapter patterns are this author's grouping of the chapters' own rules. **[L]**

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-MET-1 | chapters 01 to 13 | 13 | C | `check_learn.py` at this commit | `x3d.docs@f172f67:docs/learn/` |
| N-MET-2 | heuristics before chapter 14 | 161 | C | `build_learn.py` at this commit | `docs/learn/D-heuristics-ledger.md` |
| N-MET-3 | drills before chapter 14 | 97 | C | `build_learn.py` at this commit | `docs/learn/E-drills.md` |
| N-MET-4 | drills with a recorded run | 89 | C | `build_learn.py` at this commit | `docs/learn/E-drills.md` |
| N-MET-5 | numbers registered | 277 | C | `build_learn.py` at this commit | `docs/learn/C-numbers-ledger.md` |
| N-MET-6 | numbers graded C | 235 | C | `learn_lib.py` count | `docs/learn/C-numbers-ledger.md` |
| N-MET-7 | numbers graded L | 38 | C | `learn_lib.py` count | `docs/learn/C-numbers-ledger.md` |
| N-MET-8 | numbers graded S | 4 | C | `learn_lib.py` count | `docs/learn/C-numbers-ledger.md` |
| N-MET-9 | heuristics graded C | 124 | C | `learn_lib.py` count | `docs/learn/D-heuristics-ledger.md` |
| N-MET-10 | heuristics graded L | 30 | C | `learn_lib.py` count | `docs/learn/D-heuristics-ledger.md` |
| N-MET-11 | heuristics graded S | 7 | C | `learn_lib.py` count | `docs/learn/D-heuristics-ledger.md` |
| N-MET-12 | methods in this chapter | 7 | C | read | this file |

## Sources and provenance

Counts taken from the base at branch `claude/project-thread-3r22fz` on 2026-11-14, tools `x3d.docs@f172f67:docs/tools-shared/`. Nothing external was read for this chapter.
