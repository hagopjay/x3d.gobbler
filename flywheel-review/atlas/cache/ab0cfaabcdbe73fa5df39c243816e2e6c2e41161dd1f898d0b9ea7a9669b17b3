# 02. The Loom laws

> **Say it:** the Loom is 44 numbered laws and 160 numbered failure modes, each paid for by a recorded failure; this chapter indexes them by number so you can find the law that forbids a mistake, the incident that created it, and the check that catches it. **[L]** (the counts are **[C]**, parsed from the file)

| field | value |
|---|---|
| chapter code | `LAW` |
| prerequisites | [01 the tether](01-the-tether.md) (the loop and the pin rule) |
| after this you can | (1) cite a law or a failure mode by its stable number; (2) name the check that catches a violation, or say that none exists; (3) find the class of a surprise in the 160-row catalogue and its three costliest members; (4) pick the playbook pattern for a science or physics study; (5) run the one-page pre-flight checklist on a new project |
| sources read | `x3d.loom@162ab18:LOOM-v1.md` (sections 3, 4, 6, 7, 8), `LESSONS-v1.0.md`, `LEARNINGS-from-patches.md`, `GLOSSARY.md`, `SCIENCE-PLAYBOOK.md`, `PHYSICS-PLAYBOOK.md`, `REVIEW-loom2.md`, `REVIEW-scientific.md`, `SOURCES.md`, `SWEEP-REPORT.json`, `kit/loomkit/*.py`, `kit/tests/test_gates.py`, `kit/profiles/*.json`; teardown `x3d.docs@f172f67:docs/x3d.loom/MASTERCLASS.md` (linked, not repeated) |
| instruments used | `x3d.loom@162ab18` (loomkit, Python 3.13.18), `x3d_mcp fork b4efcd3`, `X_ITE 16.7.0`, `Chromium 153 (Chrome for Testing 153.0.8010.12), SwiftShader`, `git` on `x3d.loom@162ab18` |

## 1. The map

```text
 step   0 card     1 kickoff    2 weave     3 witness    4 gate      5 stump     6 judge
 laws   15 34      33 4 11 12   1 4 31 32   2 3 26 27    17 18 19    19 44       6 39 40
          |           |           |           |            |           |           |
          v           v           v           v            v           v           v
        pins,      trap list,  generator,  many blind-  candidate   mutants and  flags,
        "better"   budget      one clock   spot-split   hash, -O    controls     no scores

 step   7 receipt   8 debrief   9 fold-back    10 handoff     any red: fix the card or the
 laws   14 35 24    5 34        20 7 8 44      16 10 13       generator, weave again (law 1);
                                                              the red run stays in history (28)

 where the numbers live:
   LOOM-v1.md section 3 = laws 1..44          section 8 = failure modes 1..160
   SCIENCE-PLAYBOOK.md  = patterns A..I       PHYSICS-PLAYBOOK.md = patterns 1..19, laws 41..44
   LEARNINGS-from-patches.md = rules R1..R33  kit/loomkit = the stable diagnostic codes
```

| item | what it is | count | how the count was obtained | grade |
|---|---|---|---|---|
| laws | numbered, one failure each; append-only | 44 | rows of section 3 of `LOOM-v1.md`, ids 1..44 contiguous | [C] |
| failure modes | numbered traps with a fix | 160 | rows of section 8, ids 1..160 contiguous | [C] |
| witnesses | Grammar to Score, plus 3b page traps and 3c physics | 13 rows | section 6.1 table | [C] |
| acceptance profiles | `loom.profile/1` files | 20 files, 11 rows in section 6.2 | `kit/profiles/*.json`; table rows | [C] |
| stable codes | raising diagnostics in loomkit | `accept` 15 distinct, physics 18, science 27 | `accept.py`, `physics.py` docstring, `sci.py` | [C] |

In scope: the numbered rules and how to find and check them. Out of scope: the AST teardown of the repository ([the x3d.loom masterclass](../x3d.loom/MASTERCLASS.md)), the validator ([03](03-validator-and-gates.md)), the physics bridges in depth ([13](13-physics.md)).

**How the count grew** (re-derived from `git show <commit>:LOOM-v1.md` at each commit) **[C]**:

| commit | date | change | laws | failure modes |
|---|---|---|---|---|
| `0244784` | 2026-11-05 | v1.0 public snapshot | 35 | 92 |
| `849fc7e` | 2026-11-05 | Mashtots2 fold-in | 36 | 101 |
| `9ef7a19` | 2026-11-05 | snapshot 4, Manifold of Emotion | 37 | 108 |
| `511de0e` | 2026-11-07 | two rebuilds by another model | 40 | 123 |
| `2f52728` | 2026-11-13 | PhysX and MuJoCo bridges: physics witness, laws 41 to 43 | 43 | 147 |
| `babba96` | 2026-11-13 | Ten Minute Physics fold-back (PR #41, merged as `c782ea1`): law 44, failure modes 148 to 160, playbook patterns 11 to 19 | 44 | 160 |

**Read next:** deeper, [03 validator and gates](03-validator-and-gates.md) (the checks behind laws 2, 8, 15); wider, [13 physics](13-physics.md) (laws 41 to 44 at work).

## 2. The laws, by theme

Each row: the law's number and exact headline (`LOOM-v1.md` section 3), the incident that created it, the typical violation, and the check that catches it. `code:` names a stable diagnostic or rule in loomkit or a witness; `process:` means review, a practice or a project's own gate, with no mechanical check in the kit. Evidence is carried from `LOOM-v1.md` with its own grade ("src C" is the source's Confirmed; in this base a carried row is [L] at most). "Re-run" marks what was executed for this chapter on 2026-11-14.

The laws are grade [L] as a set: each generalises C-graded incidents. Laws 43 and 44 are scoped to physics profiles first (decision of 13 Nov); if either proves wrong it is marked a false positive in the table, not deleted.

### A. Make it again, keep every layer

| # | law | evidence | typical violation | check |
|---|---|---|---|---|
| 1 | **Generator, not file.** Fix the card or the generator, then weave again | Dynasty Loom v3: 87 of 87 files rebuilt byte for byte (src C); a hand edit on the Data City run gave `STALE_WITNESS` (src C) | hand-editing a generated .x3d | code: rebuild and compare sha256; `STALE_WITNESS` (`accept.py`), re-run in [01](01-the-tether.md) |
| 4 | **If you can't make it again, you don't know what it is.** Declare every input, the date included | a clock moved 3 days and the rebuild differed (fm 10); set order changed bytes (fm 36) | `datetime.now()` in a generator; unsorted sets | process: rebuild with `SOURCE_DATE_EPOCH` moved, compare bytes (fm 10, 36, 40) |
| 14 | **Add layers, never replace.** Version everything | every Loomsong version kept its predecessor's receipt (src C) | overwriting a demo or a receipt | code: `RECEIPT_EXISTS` (`receipt.py`); the `prev` field |

### B. Witness design: how to build an instrument that can be trusted

| # | law | evidence | typical violation | check |
|---|---|---|---|---|
| 2 | **Valid is not visible.** Grammar passing starts the inspection, never ends it | 3 of 3 pocket worlds valid and white (src C); here 17.52% vs 0.00% non-background pixels, both valid (re-run, [C]) | shipping on "0 errors" | code: an Eyes witness with a pixel floor ([01](01-the-tether.md) section 5) |
| 3 | **Many witnesses, blind spots that don't overlap** | labels vanished only under the host policy (fm 6, src C) | one clever test for all | code: the profile's required set: `MISSING_WITNESS`, `EMPTY_PROFILE` |
| 19 | **A control must fail for the intended reason.** One stable diagnostic per negative control; a crash is `error`, not a catch | IndexError mistaken for rejection (src L); Break-the-Loom requires the exact diagnostic (src C) | "some failure happened" counted as a catch | code: `expect()` in `kit/tests/test_gates.py` raises `WRONG_DIAGNOSTIC` or `SURVIVING_CONTROL`; exit 2 for an instrument crash |
| 25 | **Independent witnesses need independent assumptions** | shader and CPU probe agreed on a wrong L/(N-1) spacing (fm 54, src C as reported) | a second implementation that shares the coordinate convention | process: list the shared assumptions beside the witness |
| 26 | **Suspect the witness first.** The same value across unrelated inputs, or no change when the cause changes, means it measures something else | a wrong-view capture read as a GPU bug; a check returned 0.31 cells in every case (fm 64, 70, src C) | debugging the subject before the instrument | process: vary the cause and watch the number; signal floor (fm 65) |
| 27 | **Like with like.** Same window, state and conditions; state the witness exactly where the construction allows | pitch check red twice on correct audio, 31% (fm 79, src C) | a windowed estimate against a point value | process: an exact statement (zero crossings) plus a negative control |
| 36 | **A pass names what it saw.** A witness reports an inventory of what it read | page traps passed six .js files with 0 field callbacks seen (fm 93, src C) | a clean result over nothing relevant | code: `seen` counts in `kit/loom pagetraps`; `PHYS_NO_RUNS`; `EMPTY_CANDIDATE` |
| 44 | **A check is shown able to fail, and a number is not Confirmed until a second reader has tried to break it** | the energy check read 1.33e-15 with the buggy rule, 2.0e-15 fixed, 0 with no collisions (fm 148); 125 claims, 25 negative findings survived (src C) | a self-graded Confirmed; a mutation control that changes nothing (fm 157: 2 of 11) | code: `PHYS_CONTROL_SURVIVED`; 14 of 14 mutations of the real record caught (re-run, [C]); limits-commit check is not in the kit |

### C. Gates and evidence integrity

| # | law | evidence | typical violation | check |
|---|---|---|---|---|
| 8 | **Gates are fixed like code**: tests on both sides and a corpus re-run | glsl-int-literal: 62 findings over 859 files, all one false line (src C) | silencing a noisy rule | code: 15 trap rules and 8 page-trap rules each pass a clean and catch a failing fixture (re-run, [C]) |
| 17 | **Evidence is bound to the exact candidate**, test code included | Study 01 packaged a changed shader against a stale browser pass (src C) | packaging changed code with an old pass | code: `STALE_WITNESS`, `CANDIDATE_CHANGED_DURING_WITNESS`, `EVIDENCE_DRIFT`, `DEVELOPMENT_WITNESS` |
| 18 | **A gate is code that cannot be switched off.** Raising predicates, never `assert`; tested under `python -O` | Red Score packaged under `-O`; IfcOpenShell asserts forced a refusal (src C) | `assert` as the gate | code: `need()` in `core.py`; the suite runs in both modes, 82 controls each (re-run, [C]) |
| 24 | **Open what you hash.** Decode every payload and archive before its hash enters a receipt | Living Archive zip truncated yet receipted; a re-hashed truncated PNG passes the shipped audit (src C) | a receipt that certifies broken bytes | code: `SCI_PUBLICATION_UNDECODABLE`; `unzip -t`; `kit/examples/salvage_zip.py` |
| 35 | **A signature proves a key, not an author** | the demo seal was forgeable from its own source (src L) | an HMAC key in the source or the envelope | code: receipts carry `signed=false`; `verify-receipt` says only "intact"; forgery re-run in [01](01-the-tether.md) section 9 |

### D. Claims, grades and scope

| # | law | evidence | typical violation | check |
|---|---|---|---|---|
| 5 | **Say how sure you are.** C, L or S on every claim, with its instrument | "upstream is broken" split into C and L (src C/L) | upgrading a grade in translation | code: `UNMEASURED_REQUIRED_WITNESS` (a pass graded S), `UNKNOWN_GRADE` (`core.py`) |
| 6 | **Models speak in S.** Judges flag, never grade | re-judging a frame moved the score by sd 0.12 to 0.25; a black still scored 2.33 (src C) | a model sentence entering the record as fact | code: `PICTURE_GRADING`, `MODEL_TRUTH_PROMOTION`, `STALE_PICTURE_REVIEW` (`picture.py`) |
| 13 | **Unknown is not zero; no witness, no tie** | Data City null semantics (fm 33, src C) | `COALESCE(missing, 0)` | process: the project's truth gate; the fold-back kit's profile contract is not in loomkit |
| 15 | **Name the instrument behind every number** | "7 to 10 of 10 repairs" holds at upstream 74da0ec, 3 to 6 at 020221e (src C); 15.0% became 14.1% with one script (re-run, [C]) | unpinned verdicts; software-GL frame rates | code: the witness record's `instrument` field; the fork witness names its commit |
| 34 | **Every result states its scope and its reproduction level** (L2 isolation, L3 real browser, L4 comparative) | the X_ITE teardown's F01 and F02 records; "physics CPU only" (src L) | a pass with unstated reach | code: `limitations` in witness records and receipts; process: the debrief's "what a pass does not establish" |

### E. The learning loop

| # | law | evidence | typical violation | check |
|---|---|---|---|---|
| 7 | **Every mistake pays rent once**: incident, fact, rule with tests, fork check, upstream | shader-raw-source: white sphere to gate rule in a day (fm 1, src C) | fixing a trap in one project only | code: a trap rule with two-sided tests (`traps.py`); process: the FACTS entry |
| 9 | **The metric will be attacked.** Close escape hatches before optimising | 67 of 67 optimised valid scenes declared Full (src L); hard prompts 84% plain, 30% with Full barred | rewarding "valid" alone | process: re-score with the escape hatch barred (x3d.onto lawful metric; read, not run) |
| 20 | **Fold back small, with the counterexample**: additions-only, minimal failing fixture, scope, blind spots | all five project patches share the shape (src C) | grand universal rules; browser facts promoted to X3D prohibitions | code: `kit/loom foldback` (apply check, additions-only, smoke normal and `-O` in an empty repo) |

### F. Budget, truth and release

| # | law | evidence | typical violation | check |
|---|---|---|---|---|
| 10 | **Truth gates when the world is real** | 20 errors and 26 warnings in shipped family data (src C) | an invented person, face or date | process: a per-project truth witness (`kit/loom command --name truth`) |
| 11 | **Ask once, cache forever.** Every paid call keyed by prompt hash and capped | portrait cache: 2 calls per person (src C) | re-requesting the same picture | process: separate duplicate-key and over-cap fixtures (fm 31); receipts list `model_calls` with a cached flag |
| 12 | **Budget is a witness.** Two or three agents at a time; partial results on disk | 22 parallel agents exhausted the allowance (fm 41, src C) | wide fan-outs | process: at most 3 agents |
| 16 | **Nothing leaves without "send".** Public pages pass a leak sweep first | 33 upstream PRs drafted, 0 sent (src C); `SWEEP-REPORT.json`: status pass, 67 replacements, residue empty | outbound PRs, emails or pushes on assumption | code: `kit/loom sweep` raises `LEAK_RESIDUE` if a forbidden pattern survives |

### G. Science and numerics

| # | law | evidence | typical violation | check |
|---|---|---|---|---|
| 21 | **Invariants admit; they do not confirm intent** | reversed vortex circulation conserved every invariant (fm 51, src C as reported) | accepting a simulation because energy is conserved | process: a separate event witness (topology, morphology) |
| 22 | **Certify the space, not the number** | good eigenvalues, non-orthogonal degenerate modes (fm 52) | animating an arbitrary basis vector as "the mode" | process: an orthogonality or subspace witness; `SCI_REQUIRED_WITNESS_MISSING` enforces the kind's list |
| 23 | **Display precision is part of the scientific budget** | 8-bit moved the early zero-isosurface; 16-bit fixed it (fm 53) | relabelling clipped values | code: `SCI_DISPLAY_QUANTIZATION`, `SCI_DISPLAY_CLIPPING` |
| 28 | **Explore the worst case before declaring a limit; then fix the instrument, not the threshold** | 3s normalization 8.2e-4 after limits set on easy orbitals (fm 76) | limits set on easy cases, widened afterwards | code: `PHYS_LIMIT_WIDENED` (physics); process: limits in the builder docstring with exploration numbers |
| 29 | **One cause at a time** | a fast ring blamed on the boundary was the periodic images, with the correction's sign wrong (fm 86, 87) | a correction for an untested cause | process: change one variable; grade a fitted correction L |
| 30 | **Nothing transfers across dimension or geometry unmeasured** | a 2D seed died in 3D; labyrinths became sheets (fm 67 to 69, 82) | a borrowed 2D recipe or regime name | process: every name in a caption is a measured claim, threshold declared first |

### H. Runtime, page and host

| # | law | evidence | typical violation | check |
|---|---|---|---|---|
| 31 | **One clock, one owner** | picture and audio 0.8 to 1.5 s apart until the audio drove the picture (fm 80) | two clocks "started together" | code: page trap `xite-browser-currenttime`; process: the evidence compares the clocks |
| 32 | **The runtime's contracts are part of the build** | one escaping callback froze all routing in X_ITE 16.5.1 (fm 88, 94, src C) | unguarded field callbacks; navigation before the scene exists | code: page traps `xite-callback-unguarded`, `nav-before-scene`, `loadurl-unbudgeted`, `window-global-shadow` |
| 33 | **Read your own checklist** | the clock trap was in the kickoff and was hit anyway (fm 72) | rediscovering a recorded trap | process: the first-reply check and `kit/templates/KICKOFF-PRE.md` |
| 40 | **A fallback must say so** | a reviewer judged a procedural stand-in; X_ITE drew black under the host policy (fm 116, 122) | a page that looks finished on a stand-in | code: `PHYS_LOSS_UNREPORTED`; process: the Host witness on a strict policy copy |

### I. One master, many bodies

| # | law | evidence | typical violation | check |
|---|---|---|---|---|
| 37 | **An artefact that claims to stand alone is tested alone** | a saved moment drew opaque sheets without its page; fixed, SSIM 0.9987 against the live frame (fm 103) | testing an export only inside the app | process: load it alone and compare with the live view |
| 38 | **One master, many renderers.** A second renderer reads the validated X3D itself | both rebuilds drew from converted copies; merged build reads 48 of 48 ROUTEs, cloth mask IoU 0.976 to 0.992 (fm 115, 123) | a second renderer fed from a drifting export; a pixel hash across renderers | process: same sha256, a coverage manifest, a shape witness per beat |
| 39 | **A look may add, never assert** | clipping went 88.4% to 0% by changing the light values, not the tone curve (fm 114) | unlabelled generated detail; clipping hidden by tone mapping | process: an ART mark on pixels and filenames; a 1x switch; a `toneMapping NONE` reference view |

### J. Stepped physics

| # | law | evidence | typical violation | check |
|---|---|---|---|---|
| 41 | **A replaced engine is shown off, in every host that has it, and its leaks are listed** | X_ITE's Bullet stepped once after `loadURL()` (y 0.32 to 0.319974, fm 127) | taking "disabled" for "off" | code: `PHYS_TAKEOVER_UNPROVEN` |
| 42 | **Determinism is claimed per step and per host** | 1918 steps recorded in Chromium, 969 in Firefox, 0 differing hashes in 4 hosts (fm 128, 129; one machine) | a final-state hash; a claim from one place | code: `PHYS_HASH_DRIFT`, `PHYS_REPLAY_MISSING`, `PHYS_REPLAY_STEPS`, `PHYS_ENGINE_DRIFT`, `PHYS_TRACE_TAMPERED` |
| 43 | **A tolerance is written before the run; an excursion is a waiver, not a pass** | 3 of 33 smoke tests failed under load and were accepted as 3 waivers; ragdoll overshoot 0.43 against 0.2 rad (fm 133, 137) | loosening a threshold to turn red green | code: `PHYS_LIMIT_WIDENED`, `PHYS_FALSE_GREEN`, `PHYS_WAIVER_INCOMPLETE`, `PHYS_WAIVERS_OVER_CAP`; cap 3 passes and cap 0 fails on the real records (re-run, [C]) |

Law 44 is listed under B, its theme being witness design; it shares the physics scope with 41 to 43. Count of the `check` column by this chapter's reading **[L]**: 27 laws begin `code:` and 17 begin `process:` (4, 9, 10, 11, 12, 13, 21, 22, 25, 26, 27, 29, 30, 33, 37, 38, 39); drill D-LAW-2 recounts them from this file. A `code:` entry sometimes names only a record field that makes a check possible (laws 15 and 34), not a decision gate.

## 3. The failure-mode catalogue: 160 rows in 11 classes

The failure modes are numbered 1 to 160 in `LOOM-v1.md` section 8 (the ids are the stable reference; cite "failure mode 88", never a paraphrase). The classes below are this chapter's grouping, not a Loom id: [L], and each failure mode sits in exactly one class (drill D-LAW-7 verifies that the lists below cover 1 to 160 once). The top three per class are chosen by cost (the loss recorded) and by recurrence.

| class | name | n | ids | top 3 (number, what happened, the fix) |
|---|---|---|---|---|
| K1 | the witness measured the wrong thing or the wrong state | 23 | 11, 19, 20, 24, 25, 26, 28, 29, 30, 37, 40, 48, 64, 65, 70, 79, 85, 95, 105, 108, 142, 149, 152 | **64** a capture of the wrong view mode was read as a GPU bug: the page reports the view it drew and the witness rejects a mismatch. **70** one check returned the same value in every case at 8 and 16 bits: split it, one cause per witness. **79** a windowed estimate against a point value gave 31% "error" on correct audio: like with like, state the witness exactly |
| K2 | gates and controls that cannot fail | 15 | 13, 14, 15, 55, 66, 81, 92, 93, 96, 97, 148, 150, 151, 157, 160 | **13** `python -O` strips asserts so a red gate packages (recurred as 55): raising predicates, test both modes. **148** a check passed for the wrong implementation (1.33e-15 buggy, 2.0e-15 fixed, 0 none): run the wrong twin. **93** a witness passed having read nothing relevant: report `seen` |
| K3 | evidence binding, freshness, provenance, claim scope | 12 | 12, 21, 46, 47, 56, 74, 90, 98, 99, 123, 155, 156 | **12** an old browser pass authorised changed code: bind to the candidate digest, tests included. **46** a receipt hashed a truncated zip: open before hashing. **98** a shipped result file was older than the code (148 recorded, 150 run): name the code hash, re-run on receipt |
| K4 | valid is not visible; XSD, standard and runtime disagree | 13 | 1, 2, 3, 4, 8, 9, 27, 57, 73, 91, 102, 103, 141 | **1** raw GLSL in a `ShaderPart` is read as a URL and draws white: `data:x-shader/x-fragment,` prefix, trap `shader-raw-source`. **91** 17 of 91 "valid" scenes rendered blank and 10 invalid ones drew: keep grammar, meaning and eyes separate. **141** the XSD passed while the semantic validator found 5 errors per scene: run both |
| K5 | runtime, page and host contracts | 22 | 6, 7, 49, 61, 72, 77, 78, 80, 84, 88, 89, 94, 101, 104, 113, 116, 117, 118, 122, 128, 130, 144 | **88** one exception in a field callback freezes every route (recurred as 94): guard every callback, probe with a deliberate throw. **72** `Browser.currentTime` does not exist and the trap was already in the kickoff: `getCurrentTime()`, read the list. **116** X_ITE drew black under the hosted policy because its stylesheet was blocked: inline it, test under the policy |
| K6 | reproducibility and build hygiene | 11 | 10, 16, 36, 43, 44, 45, 58, 60, 75, 83, 139 | **10** the build date leaked into output: `SOURCE_DATE_EPOCH`, rebuild with the clock moved. **44** a cross-platform rebuild differed in PNG bytes and last-bit floats: compare decoded content, claim byte identity only on the original platform. **58** `python -I` dropped the builder's directory a second time after 43: launch with `-E -s` |
| K7 | science and numerics | 20 | 50, 51, 52, 53, 54, 59, 62, 63, 67, 68, 69, 71, 76, 82, 86, 87, 153, 154, 158, 159 | **51** invariants held while the event went the wrong way: a witness of the promised event. **76** the limit was set on easy orbitals and 3s broke it: worst case first, then refine. **86** a plausible cause was tested and rejected (periodic images were the cause): one change at a time |
| K8 | physics engines and stepped simulation | 14 | 124, 125, 126, 127, 129, 131, 132, 133, 134, 135, 136, 137, 138, 140 | **124** a stepped engine judged against the continuum answer looked wrong by 1/2 g h t (0.0204 m): use the scheme's own discrete solution (1.5e-6 m). **127** "disabled" was taken for "off": a takeover proof per host. **133** smoke tests failed under load with no record of who accepted them: waivers with owner, date and a cap |
| K9 | rendering, look and multi-renderer parity | 14 | 5, 17, 18, 22, 23, 106, 109, 110, 111, 112, 114, 115, 119, 120 | **115** cloth outline overlap fell to 0.855 and 0.778 with identical geometry (translucency blends in different spaces): compare shapes with translucent parts hidden (0.99), never pixels across renderers. **109** HSV against RGB colour interpolation: densify keys, trap `color-keys-sparse`. **114** tone mapping crushed darks and ACES hid clipped cloth: a `NONE` reference view, fix the light (88.4% to 0%) |
| K10 | data identity and truth | 6 | 32, 33, 34, 35, 38, 39 | **33** a missing value became zero: null end to end. **32** a count passed while identity was wrong: match identities. **38** a load "ended cleanly" at 88.6% of a table: rename the output only after counts reconcile |
| K11 | process, budget and governance | 10 | 31, 41, 42, 100, 107, 121, 143, 145, 146, 147 | **41** 22 parallel agents exhausted the allowance: at most 3. **146** a fold-back was assumed while two threads built bridges with no PR: the last step of a thread is its PR, numbered from upstream's tip that day. **121** an X_ITE bug was reported that was ours (shared Coordinate): a minimal repro before any upstream claim |

```text
  failure modes per class (each # is one failure mode; 160 in all)
  K1  witness measured the wrong thing        23 #######################
  K5  runtime, page and host contracts        22 ######################
  K7  science and numerics                    20 ####################
  K2  gates and controls that cannot fail     15 ###############
  K8  physics engines, stepped simulation     14 ##############
  K9  rendering, look, renderer parity        14 ##############
  K4  valid is not visible; XSD vs runtime    13 #############
  K3  evidence binding, provenance, scope     12 ############
  K6  reproducibility, build hygiene          11 ###########
  K11 process, budget, governance             10 ##########
  K10 data identity and truth                  6 ######
```

Failure modes that record their own recurrence (regex `recurred|second time|A repeat|second occurrence|second delivery|hit twice` over section 8, two false hits removed by hand) **[C]**: 55 (repeats 13), 58 (repeats 43), 72 (repeats a trap its own kickoff listed), 73 (repeats 57), 94 (repeats 88), 107 (twice in one night), 128 (hit twice). Seven of 160: the traps that came back were the ones kept only in prose.

How a surprise is looked up: grep `LOOM-v1.md` for the symptom word, read the row's fix, then read the law named in the fix; if no row matches, the surprise is a candidate failure mode: write the symptom, the cause, the fix and the test, and number it from upstream's tip (fm 146, 147).

## 4. The playbook patterns

Two playbooks turn the laws into reusable patterns. Science: nine patterns A to I (`SCIENCE-PLAYBOOK.md` section 2). Physics: nineteen numbered patterns (`PHYSICS-PLAYBOOK.md` section 3; patterns 11 to 19 came with law 44).

| id | pattern | proof recorded | laws, failure modes |
|---|---|---|---|
| S-A | exact references even when the problem is "solved": closed forms, dispersion, exact discrete identities | order 2.05; 2.5e-5 raw, 5e-9 after Richardson | 19, 28; 76 |
| S-B | convergence: observed order, Richardson, a finer check grid | abs(p - expected) within 0.05 to 0.1 | 28; 76 |
| S-C | invariants admit, events confirm | vortex direction, Turing morphology | 21; 51 |
| S-D | every regime name in a caption is a measured claim | "spots", "reconnection" with thresholds | 30; 69 |
| S-E | controls that must fail: flipped capture, signal floor, a bug kept as a switch | MSAA black screen 61.4 to 3.9 | 19; 65, 66, 97 |
| S-F | the display chain is part of the science: quantisation, clipping counted | 8-bit to 16-bit per case | 23; 53, 71 |
| S-G | cross-implementation witnesses; shared code is a shared assumption | mesh counts exact, volume 1e-6 | 25; 54 |
| S-H | reproducibility: bitwise-reproducible kernels, seeds in the manifest | prefix rerun bit for bit | 4; 10 |
| S-I | units: nominal conversions stated as nominal | Lyman-alpha units check | 34 |
| P-1 | the scheme's own answer is the reference | 1.5e-6 m against 0.0204 m continuum gap | 19, 28; 124 |
| P-2 | the analytic ladder, limits declared in the SPEC first | pendulum 1.4e-5 relative | 28; 125, 126 |
| P-3 | hash every step, replay in every host | 1918 steps, 0 differing hashes in 4 hosts | 42; 128, 129 |
| P-4 | compare the reader's model with the Node model, in the browser | 36 bodies, 0 differences | 26; 129, 134 |
| P-5 | the takeover proof: old engine 0 events in 120 frames, leaks listed | 3 browsers | 41; 127 |
| P-6 | tolerance, then waiver; a self-check that misses is logged, not tuned | 3 waivers; 34% Gravitron | 43; 133, 137 |
| P-7 | controls that must fail, run on the real records | 14 of 14 caught | 19, 44 |
| P-8 | derived scores get a hand-checkable unit test | 619 against 636 by hand (-3%) | 44; 136, 138 |
| P-9 | a build check is not a model check | native vs WASM 6e-16 rad | 25; 142 |
| P-10 | a threat model with measured gaps | 16 defences hold, 3 gaps | 145 |
| P-11 | every check ships its wrong twin | 1.33e-15 / 2.0e-15 / 0 | 44; 148, 151 |
| P-12 | read each quantity where nothing has just enforced it | 2.4e-2 pre-projection vs 2e-16 after | 44; 149, 152 |
| P-13 | commit the limits first; the runner refuses to start if they differ | limits file sha256 in every record | 43, 44; 156 |
| P-14 | a second reader breaks the numbers before they are Confirmed | 125 checked, 25 survived, 0 false alarms | 44 |
| P-15 | an explanation is a claim with its own test | checkerboard mode 0.7082, not 0.83 | 29; 153, 154 |
| P-16 | orders are slopes read at an end time; energy is not position | Euler order 2.0 at 2 pi, 1.0 at T = 1 | 159 |
| P-17 | a spatial structure is checked by set equality, cost counted | 905 pairs missed by the wrong sort | 160 |
| P-18 | count caught controls; make each control change something | 9 of 11, then 11 of 11 | 19, 44; 157 |
| P-19 | keep falsified predictions in the notes, out of the witness | 2 cloth rules falsified | 158 |

## 5. The loop, roles, gates and rubrics in compact form

**The ten steps** (`LOOM-v1.md` section 4); a red witness at any step returns to the card or the generator, never to the artifact.

| step | does | artefact | stable codes or checks |
|---|---|---|---|
| 0 card | source of truth `repo@commit`, a measurable "better", must-not-change | card file | none: process |
| 1 kickoff | paste PRE: target, tool pins, trap list, generator first, guardrails, witness plan, outputs | `kit/templates/KICKOFF-PRE.md` | first-reply check |
| 2 weave | generator emits files and a manifest | `build-manifest.json` | `SOURCE_DATE_EPOCH`, declared inputs |
| 3 witness | cheapest first: Grammar, Meaning, Traps, then browser and human | `loom.witness/1` records | `CANDIDATE_CHANGED_DURING_WITNESS` |
| 4 gate | the profile's closed set of current witnesses | acceptance summary | `MISSING_WITNESS`, `STALE_WITNESS`, `WITNESS_NOT_PASS`, `UNMEASURED_REQUIRED_WITNESS`, `COVERAGE_REQUIRED`, `EVIDENCE_DRIFT` |
| 5 stump | single-fault mutants with repaired controls; rubrics for models | mutant matrix | `SURVIVING_CONTROL` |
| 6 judge | the human's eye is the judge of record; model judges flag only | `loom.picture-review/1` | `PICTURE_GRADING`, `MODEL_TRUTH_PROMOTION` |
| 7 receipt | `loom.receipt/1`, unsigned, refuses to overwrite | `receipts/<artifact>.json` | `RECEIPT_EXISTS` |
| 8 debrief | scope, witness inventory with boundaries, incidents with maturity | `DEBRIEF-FORM.md` | none |
| 9 fold-back | additions-only patch with counterexamples; PR numbered from upstream's tip | `tools/<name>/` | `kit/loom foldback` |
| 10 handoff | paste POST: the done-when; a missing item means not done | `HANDOFF-POST.md` | none |

**Roles.** The human: curator (decides what is woven), judge of record, the "send" and the "yes" before anything public, paid or deleted. Models: builder (writes S, acts only through generators and witnesses, at most 3 at once), judge (flags only), optimiser (offline, on a yes, metric closed first).

**Witnesses** (13 rows, section 6.1): Grammar, Meaning, Traps, 3b Page traps, 3c Physics, Behaviour, Eyes, Host, Receipts, Truth, Budget, Ear, Score. Each row names what it is blind to; that is why there are many (law 3).

**Statuses and labels.** Status: `pass`, `fail`, `error`, `not_run`, `not_applicable`, `deferred` (a second axis, apart from grade). Grade: C (a named tool ran), L (read or reasoned), S (suspected; anything a model wrote). Labels, never grades: Synthetic (fixtures, seeded mutants) and Authored (a value chosen by design, shown beside its measured counterpart). Exit codes of `kit/loom`: 0 accepted, 1 a contract violation with a stable code, 2 an instrument or input error.

**Acceptance order** (`accept.py`, 15 distinct codes):

```text
  accept(): the first broken contract stops the check, in this order
  profile  PROFILE_SCHEMA > EMPTY_PROFILE > PROFILE_WITNESS_NAME > PROFILE_DUPLICATE_WITNESS
  record   MISSING_WITNESS > MALFORMED_WITNESS > WITNESS_SCHEMA > WRONG_WITNESS_NAME
  fresh    STALE_WITNESS (law 17) > DEVELOPMENT_WITNESS
  verdict  WITNESS_NOT_PASS > STATUS_NEEDS_REASON > UNMEASURED_REQUIRED_WITNESS (pass = C)
  reach    COVERAGE_REQUIRED (law 36) > EVIDENCE_DRIFT (evidence files re-hashed)
  then     the receipt may be written (law 14); exit 0 accepted, 1 violation, 2 instrument error
```

**Thresholds belong to a profile** (section 6.3; a few that gate): eyes nonblank: mean luminance above 2/255, over 2% of the region above 5/255, under 15% above 250/255; effect presence: unchanged-frame control under 0.001/255; camera motion under 4 units/s and 20 deg/s; judge noise: differences under 0.2 are noise. Hard boundaries need just-inside and just-outside fixtures.

**Stumping rubric rules** (for prompts that test models, section 6.4): each criterion ends "If ..., this item fails"; 80% or more of the points on criteria worth 14 to 25; files and naming at 5% or less; every quote appears word for word in the brief and every expected number is recomputed; version traps name the version, never the new API.

## 6. Pre-flight checklist (one page, derived from the laws)

Tick each line or write why not. The number in brackets is the law; "fm" is a failure mode.

**Before building**
- [ ] Card names the source of truth as `repo@commit`, a measurable "better" and what must not change [15, 34]
- [ ] Pins written: validator commit, X_ITE version, browser build and rig, Blender build; every number will carry them [15]
- [ ] Trap list read and said in the first reply [33]; the profile picked, required witnesses and visible-not-run both listed [3, 34]
- [ ] Limits written now, worst-case exploration numbers beside them, limits file committed [28, 43, 44]
- [ ] Exact references named (closed form, or the scheme's own discrete solution); if none, the card says "self-consistency only" [19, 21]
- [ ] Inputs declared: seed, date, versions, file order [4]; at most 3 agents, caps and cache keys [11, 12]

**While building**
- [ ] A generator emits every file; no hand edits; sorted keys [1, 4]
- [ ] Page code: guarded field callbacks, `getCurrentTime()`, navigation after the scene, budgeted world loads, no window-name globals, one clock owner [31, 32]
- [ ] Every X3D passes Grammar and Meaning, components declared [2, 32; fm 73, 141]
- [ ] Model output enters as S and is labelled; a fallback announces itself [6, 40]
- [ ] One variable at a time; red runs kept in history [28, 29]

**Before accepting**
- [ ] Witnesses cheapest first, each record bound to the candidate hash with test code in it [17]
- [ ] Each witness has a control that must fail for its own code, and the gate passes under `python -O` [18, 19, 44]
- [ ] Each pass says what it saw: files, callbacks, runs, frames [36]
- [ ] Eyes has a pixel floor and a control that bites (asymmetric view, flipped capture) [2, 26; fm 65, 66]
- [ ] The artefact is tested alone, and a second renderer reads the same master by sha256 [37, 38]
- [ ] Physics: a hash per step in every named host, the takeover shown off, a loss report, waivers capped [40, 41, 42, 43]
- [ ] Archives, images and JSON are opened before they are hashed [24]; shared assumptions listed [25]

**Before delivering**
- [ ] Receipt written only after acceptance, unsigned and saying so, unrun witnesses visible [14, 35]
- [ ] Scope and reproduction level stated; every claim graded C, L or S with its instrument [5, 15, 34]
- [ ] Real-world content passed a truth gate; unknown is not zero [10, 13]
- [ ] Leak sweep run; nothing leaves without "send" [16]

**After**
- [ ] Debrief filled; lessons folded back as an additions-only patch with the counterexample [20]
- [ ] New rules have tests on both sides and a corpus re-run [7, 8]; numbered from upstream's tip that day [fm 146, 147]

## Heuristics

| ID | Rule | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-LAW-1 | Cite laws and failure modes by number; the numbers are the stable ids, never a paraphrase. | [C] | ids 1..44 and 1..160 contiguous (N-LAW-1, N-LAW-2) | `x3d.loom@162ab18:LOOM-v1.md` |
| H-LAW-2 | Number a new law or failure mode from upstream's tip on the day of the PR, not from a local copy. | [C] | failure modes 146 and 147 record two sibling threads that did not | `x3d.loom@162ab18` git history |
| H-LAW-3 | Ship every witness with a control that must fail for its own diagnostic; a surviving control fails the suite. | [C] | weakened copy raised `SURVIVING_CONTROL: STALE_WITNESS` (D-LAW-4) | loomkit `test_gates.py` |
| H-LAW-4 | Write gates as raising predicates and run the whole suite under `python -O`. | [C] | 82 controls caught in both modes (N-LAW-7); `assert` is stripped under `-O` (D-LAW-4) | loomkit, Python 3.13.18 |
| H-LAW-5 | Pin a coverage count in a profile knowingly: adding a rule to a witness rejects every profile that pinned the old count. | [C] | 15 profiles pin 11 trap rules, the kit has 15, `COVERAGE_REQUIRED traps.rules` (D-LAW-6) | `x3d.loom@162ab18:kit/profiles` |
| H-LAW-6 | Read the `seen` inventory of every pass; a pass over zero relevant items judged nothing. | [L] | failure mode 93: 6 files, 0 callbacks; `PHYS_NO_RUNS` | read, `pagetraps.py` |
| H-LAW-7 | Declare limits before the run and commit the file; record an excursion as a waiver with an owner and a date. | [C] | cap 3 passes, cap 0 raises `PHYS_WAIVERS_OVER_CAP` on the real PhysX records (D-LAW-5) | loomkit physics witness |
| H-LAW-8 | Do not widen a law beyond its stated scope; laws 43 and 44 are physics-first and reversible. | [C] | scope sentences in `LOOM-v1.md` laws 43 and 44 | read |
| H-LAW-9 | Look the symptom up in the failure-mode catalogue before debugging a witness; seven entries record a recurrence. | [C] | recurrence regex over section 8 (N-LAW-14) | `x3d.loom@162ab18:LOOM-v1.md` |
| H-LAW-10 | Judge a stepped engine against the scheme's own discrete solution and report the continuum gap as a known number. | [L] | 1.5e-6 m against a 0.0204 m gap (fm 124); the witness was re-run, the engine was not | `PHYSICS-PLAYBOOK.md`, read |
| H-LAW-11 | Re-derive counts from tables, not from prose summaries; summaries drift. | [C] | the three stale counts in section "Honest limits" (N-LAW-16 to N-LAW-18) | `x3d.loom@162ab18` |
| H-LAW-12 | Fold a lesson back as an additions-only patch that carries its minimal failing fixture. | [L] | five of five project patches share the shape (law 20) | `LEARNINGS-from-patches.md`, read |
| H-LAW-13 | Run the pre-flight checklist at the start and again before acceptance; a skipped line needs a written reason. | [S] | derived from the laws; not yet measured as a practice | design rule |
| H-LAW-14 | Treat a second reader's recomputation as the step that makes a number Confirmed. | [L] | law 44: 125 claims, 25 negative findings survived a second skeptical agent | `PHYSICS-PLAYBOOK.md`, read |

## Drills

### D-LAW-1 Which law and which failures came with PR #41
- **Level:** L1 (look it up)
- **Task:** Find the commit that added law 44, which failure modes and playbook patterns arrived with it, and the merge that carried it into main.
- **Verify:** `git log --format='%h %s' -- LOOM-v1.md` and `git show --stat babba96` in a checkout of `hagopjay/x3d.loom`.
- **Answer:** `babba96` "Fold back the Ten Minute Physics ports: law 44, failure modes 148-160, playbook patterns 11-19, x3d.physics/ten-minute-physics" (13 files, 1,069 insertions), merged by `c782ea1` (PR #41). Section 1 of this chapter gives the count at each commit.
- **Checked:** 2026-11-14, `git` on `x3d.loom@162ab18`

### D-LAW-2 Re-derive the counts
- **Level:** L2 (run a tool and compare)
- **Task:** From `LOOM-v1.md` and from this chapter, count the laws, the failure modes, and the `code:` and `process:` checks.
- **Verify:** run in a checkout of `x3d.loom` with this chapter saved as `02-loom-laws.md`:

```python
import re
t = open("LOOM-v1.md", encoding="utf-8").read().split("\n")
def rows(a, b):
    i = next(k for k, l in enumerate(t) if l.startswith(a)); j = next(k for k, l in enumerate(t) if l.startswith(b))
    return [int(m.group(1)) for l in t[i:j] if (m := re.match(r"\| (\d+) \|", l))]
laws, fms = rows("## 3. The laws", "## 4. The loop"), rows("## 8. Known failure modes", "## 9. Planned")
print(len(laws), laws == list(range(1, 45)), len(fms), fms == list(range(1, 161)))
doc = open("02-loom-laws.md", encoding="utf-8").read()
cells = re.findall(r"^\| (\d+) \| \*\*.*\| (code|process):", doc, re.M)
print(len(cells), sum(c == "code" for _, c in cells), sum(c == "process" for _, c in cells))
```

- **Answer:** `44 True 160 True`, then `44 27 17`.
- **Checked:** 2026-11-14, `x3d.loom@162ab18`, Python 3.13.18 (the second line is run against this file as published)

### D-LAW-3 Run the kit's self-test
- **Level:** L2 (run a tool and compare)
- **Task:** Run the two-mode self-test and read the counts; compare them with the figures that older documents quote.
- **Verify:** `python3 -I kit/tests/test_gates.py` (it writes `kit/tests/last-run.json`; run it in a copy).
- **Answer:** both modes print `82 negative controls caught with the intended code; 15 trap rules, 8 page-trap rules and 10 page forms ... pass their clean fixture and catch their failing one`. `LOOM-v1.md` section 7.4 says 41 controls and 11 rules (3 to 4 Nov), `LESSONS-v1.0.md` says 44 and 6 page rules (5 Nov); the code is the newer source.
- **Checked:** 2026-11-14, `x3d.loom@162ab18` loomkit, Python 3.13.18, normal and `-O`

### D-LAW-4 Weaken a gate and watch the suite fail
- **Level:** L3 (break it, fix it, extend it)
- **Task:** In a copy of `kit/`, delete the `STALE_WITNESS` predicate from `kit/loomkit/accept.py` (the line `need(record.get("subject_sha256") == subject["sha256"], "STALE_WITNESS", name)`), run the self-test, then show what `assert` does under `-O`.
- **Verify:** `python3 -I kit/tests/test_gates.py`; `python3 -c "assert 1 == 2"` against `python3 -O -c "assert 1 == 2; print('passed')"`.
- **Answer:** the suite stops with `RuntimeError: SURVIVING_CONTROL: STALE_WITNESS` (the control for law 17 now passes, so it fails the suite). The `assert` raises normally and is skipped under `-O`, which is why law 18 forbids it as a gate.
- **Checked:** 2026-11-14, `x3d.loom@162ab18` loomkit in a scratch copy, Python 3.13.18

### D-LAW-5 Let the physics witness judge the real records
- **Level:** L2 (run a tool and compare)
- **Task:** Run `kit/loom physics` on the two PhysX records at a waiver cap of 3 and of 0, then run the 14 mutation controls.
- **Verify:** from a copy of `x3d.loom` (so evidence is written outside the repo): `kit/loom physics x3d.physics --evidence EV --runs 'runs/*.physics.json' --hosts chromium,firefox,webkit,node --max-waivers 3 --require-takeover`, the same with `--max-waivers 0`, and `python3 -I x3d.physics/tools/physx_controls.py`.
- **Answer:** cap 3: `pass`. Cap 0: `fail`, reason `PHYS_WAIVERS_OVER_CAP: physx-bridge/grand-cascade/recorded-in-chromium: 3 waivers, the profile allows 0`. Controls: `14 controls on the real record, 14 caught with the intended code`. The Chromium record has 1918 steps and replays in 5 hosts with 0 mismatches; the Firefox record 969 steps. All on one machine.
- **Checked:** 2026-11-14, `x3d.loom@162ab18` loomkit physics witness on `x3d.physics/runs`, Python 3.13.18

### D-LAW-6 Find the profile that cannot accept a new run
- **Level:** L3 (break it, fix it, extend it)
- **Task:** Run `kit/loom traps` on any scene folder, write the other four witnesses of `x3d-static/v1` with the coverage the profile asks for (`grammar` and `meaning` with 2 files, `truth`, `foldback`), and call `accept` with `kit/profiles/x3d-static.json`. Then list which profiles pin which trap-rule count and propose a fix.
- **Verify:** `kit/loom accept`; a loop over `kit/profiles/*.json` printing each `required` entry's `coverage.rules`.
- **Answer:** `COVERAGE_REQUIRED` with detail `traps.rules`: the witness records 15 rules and the profile pins 11. 15 of the 17 profiles with a `traps` entry pin 11; only `x3d-physics` and `x3d-physics-physx` pin 15. By design this is the coverage rule (R7) working; the consequence is that a rule added to the kit invalidates old profiles until their pins are raised in a versioned change. Extension: copy the profile, set `rules` to 15, accept.
- **Checked:** 2026-11-14, `x3d.loom@162ab18` loomkit, `kit/profiles/x3d-static.json`, Python 3.13.18

### D-LAW-7 Classify, then verify the catalogue
- **Level:** L1 (look it up)
- **Task:** Assign failure modes 1, 17, 49, 93, 124, 143 and 154 to a class K1 to K11 and name the law that explains each. Then check that the class table in section 3 covers 1 to 160 exactly once.
- **Verify:** the class table; this script, run with `02-loom-laws.md` in the current folder:

```python
import re
doc = open("02-loom-laws.md", encoding="utf-8").read()
ids, ns = [], 0
for m in re.finditer(r"^\| (K\d+) \| [^|]+ \| (\d+) \| ([0-9, ]+) \|", doc, re.M):
    got = [int(x) for x in m.group(3).split(",")]
    ns += int(m.group(2)); ids += got
    assert len(got) == int(m.group(2)), m.group(1)
print(ns, len(ids), sorted(ids) == list(range(1, 161)))
```

- **Answer:** the closest law is a judgement: 1 is K4 (law 2); 17 is K9 (no numbered law; rule R16 of `LEARNINGS-from-patches.md`, declare coordinate spaces); 49 is K5 (law 32, the runtime's contracts); 93 is K2 (law 36); 124 is K8 (pattern P-1, law 19); 143 is K11 (no numbered law; the nearest is 16, release); 154 is K7 (law 44 and pattern P-15). The script prints `160 160 True`.
- **Checked:** 2026-11-14, the K-table of this chapter, Python 3.13.18 (the script only; the classification is a judgement)

### D-LAW-8 Apply the checklist to a described project
- **Level:** L1 (look it up)
- **Task:** A thread builds a browser demo of a spring-mass system on X_ITE. It hand-edits the generated .x3d to fix a colour, ships a browser pass recorded last week, reports "deterministic" after one Chrome replay, and plans to widen the energy limit from 1e-3 to 1e-2 because one case went red. List the laws it violates and the failure modes that match.
- **Verify:** section 2 and the checklist in section 6.
- **Answer:** law 1 (hand edit; `STALE_WITNESS` would follow), law 17 (a week-old pass; fm 12), law 42 (one host, not per step; fm 128, 129), laws 28 and 43 (widening a limit; fm 133, `PHYS_LIMIT_WIDENED`). Also law 34 if no scope is stated.
- **Checked:** not run

## Honest limits

- The laws, patterns and failure modes were **read**, with the counts re-derived by script; the incidents behind them were not re-run. Their measuring documents (project debriefs and other private source documents) are not public, so evidence cells are carried at [L] at most.
- Re-run here: the kit self-test (82 controls, both modes), the physics witness on the two real records (cap 3 and cap 0, 14 of 14 controls), a weakened gate (`SURVIVING_CONTROL`), the profile coverage mismatch, and the git history counts. Not run: any browser witness of the Loom's own studies, the science witness on a real bank, Babylon and the x3d.STEM repository (not in this base).
- The grouping of laws into themes A to J and failure modes into classes K1 to K11 is this chapter's judgement [L]; the numbers are the Loom's. The `code:` and `process:` split is this chapter's reading of the check column [L].
- Counts in older prose disagree with the tables (grade [C] that they disagree; the tables and code win): `LESSONS-v1.0.md` says 43 laws and 147 failure modes (the file's tables say 44 and 160); `README.md` says "14 places sources disagree" (`SOURCES.md` section 2 has 16 rows), "25 reusable rules" (`LEARNINGS-from-patches.md` section 6 has 33, R1 to R33) and "ten witness patterns" for physics (the playbook has 19); `LOOM-v1.md` section 7.4 says 41 negative controls and 11 trap rules (the kit runs 82 and 15); section 6.1 says 6 page-trap rules (the kit has 8).
- Profiles pin trap coverage at 11 for 15 of 17 profiles with a trap entry while the kit has 15 rules; the old profiles cannot accept a fresh traps witness (D-LAW-6). This is the coverage rule working, and it is also a maintenance gap [L].
- Laws 43 and 44 are scoped to physics profiles and are open to being marked false positives. The limits-commit check of law 44 and failure mode 156 is not implemented in the kit (`PHYSICS-PLAYBOOK.md` section 9 says so).
- The ranking "top 3 per class" is by recorded cost and recurrence, a judgement, not a measurement.
- Seventeen laws (4, 9, 10, 11, 12, 13, 21, 22, 25, 26, 27, 29, 30, 33, 37, 38, 39) have no mechanical check in the kit; a reader who wants one has to build it, and the kit's `code:` entries for laws 15, 31, 34 and 35 are partial.
- Decision text in `LOOM-v1.md` section 11 and owner statements are not reproduced; only the resulting rules are.

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-LAW-1 | laws in `LOOM-v1.md` section 3, ids contiguous | 44 | [C] | python parse of the table, `x3d.loom@162ab18` | `x3d.loom@162ab18:LOOM-v1.md` |
| N-LAW-2 | failure modes in section 8, ids contiguous | 160 | [C] | python parse of the table, `x3d.loom@162ab18` | `x3d.loom@162ab18:LOOM-v1.md` |
| N-LAW-3 | witness rows in section 6.1 | 13 | [C] | python parse, `x3d.loom@162ab18` | `x3d.loom@162ab18:LOOM-v1.md` |
| N-LAW-4 | profile files and profile rows in section 6.2 | 20 files, 11 rows | [C] | count, `x3d.loom@162ab18` | `x3d.loom@162ab18:kit/profiles/` |
| N-LAW-5 | laws and failure modes at the first public snapshot | 35 and 92 | [C] | `git show 0244784:LOOM-v1.md`, python parse | `x3d.loom@0244784:LOOM-v1.md` |
| N-LAW-6 | laws and failure modes added by commit `babba96` (PR #41) | law 44; failure modes 148 to 160 (13) | [C] | `git show --stat babba96` | `x3d.loom@babba96:LOOM-v1.md` |
| N-LAW-7 | negative controls caught, each mode | 82 (normal and `-O`) | [C] | loomkit `test_gates.py`, Python 3.13.18 | `x3d.loom@162ab18:kit/tests/test_gates.py` |
| N-LAW-8 | trap rules, page-trap rules, page forms, two-sided | 15, 8, 10 | [C] | loomkit self-test | `x3d.loom@162ab18:kit/loomkit/traps.py`, `pagetraps.py` |
| N-LAW-9 | physics diagnostic codes and tests | 18 codes; 30 physics tests | [C] | `physics.py` docstring; `last-run.json` | `x3d.loom@162ab18:kit/loomkit/physics.py` |
| N-LAW-10 | physics witness on the two real records | cap 3 pass; cap 0 `PHYS_WAIVERS_OVER_CAP` | [C] | loomkit physics, `x3d.physics/runs` | `x3d.loom@162ab18:x3d.physics/runs/` |
| N-LAW-11 | mutation controls on the real record | 14 of 14 caught | [C] | `physx_controls.py` | `x3d.loom@162ab18:x3d.physics/tools/physx_controls.py` |
| N-LAW-12 | steps recorded and replay hosts, Chromium and Firefox records | 1918 and 969 steps; 5 replays each, 0 mismatches | [C] | loomkit physics, one machine | `x3d.loom@162ab18:x3d.physics/runs/` |
| N-LAW-13 | profiles with a `traps` entry pinning 11 and 15 rules | 15 pin 11; 2 pin 15; the kit has 15 | [C] | python over `kit/profiles/*.json` | `x3d.loom@162ab18:kit/profiles/` |
| N-LAW-14 | failure modes that record a recurrence | 7 (55, 58, 72, 73, 94, 107, 128) | [C] | regex over section 8, 2 false hits removed | `x3d.loom@162ab18:LOOM-v1.md` |
| N-LAW-15 | failure-mode classes in this chapter, ids covered once | 11 classes, 160 ids | [C] | D-LAW-7 script | this chapter, section 3 |
| N-LAW-16 | disagreement rows in `SOURCES.md` section 2 | 16 (README says 14) | [C] | count | `x3d.loom@162ab18:SOURCES.md` |
| N-LAW-17 | rules R1 to R33 in `LEARNINGS-from-patches.md` section 6 | 33 (README says 25) | [C] | count | `x3d.loom@162ab18:LEARNINGS-from-patches.md` |
| N-LAW-18 | physics playbook witness patterns | 19 (README says ten) | [C] | count | `x3d.loom@162ab18:PHYSICS-PLAYBOOK.md` |
| N-LAW-19 | leak sweep of the public snapshot | status pass, 67 replacements, residue empty | [L] | as recorded, not re-run | `x3d.loom@162ab18:SWEEP-REPORT.json` |
| N-LAW-20 | laws whose check column starts `code:` and `process:` | 27 and 17 | [L] | D-LAW-2 script (judgement of the column) | this chapter, section 2 |

## Sources and provenance

- `x3d.loom@162ab18` (main, 2026-11-13): `LOOM-v1.md` sections 1 to 8 read, parsed and, at 8 commits, re-parsed from git; `LESSONS-v1.0.md`, `LEARNINGS-from-patches.md`, `GLOSSARY.md`, `SCIENCE-PLAYBOOK.md`, `PHYSICS-PLAYBOOK.md`, `REVIEW-loom2.md`, `REVIEW-scientific.md`, `SOURCES.md`, `SWEEP-REPORT.json` read; `kit/loomkit/` read; `kit/tests/test_gates.py` and the physics witness run on scratch copies. The checkout was not modified.
- `x3d.docs@f172f67:docs/x3d.loom/MASTERCLASS.md`: the measured AST teardown (eight sub-projects that share a method, not a library); linked, not repeated.
- Date read and run: 2026-11-14. Private working notes on the loop and the grand review were treated as starting points only; every number used here was re-derived from the public files above or is carried and marked [L]. Gaps in private sources are not linked.
- Siblings: [01 the tether](01-the-tether.md), [03 validator and gates](03-validator-and-gates.md), [06 X_ITE the oracle](06-xite-the-oracle.md), [13 physics](13-physics.md).
