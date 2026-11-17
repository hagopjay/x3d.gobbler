# The X3D flywheel: where it stands and where to push

Written 16 November 2026 after reading the x3d family on GitHub (hagopjay). Local file, not pushed anywhere.

**What I read.** `x3d.docs` at `3aab064`: the start page, the tether chapter, the Loom laws, and the "Say it" line and "Honest limits" section of all 21 chapters, plus the changelog and the ledgers' totals. `LOOM-v1.md` (purpose, roles, roadmap, open questions, decisions). The READMEs of 17 repositories. Pull-request counts, stars, licences and visibility from the GitHub API.
**What I did not do.** I ran none of the code and re-derived no number except the ledger totals and the repository statistics. I did not re-read the six teardowns in full or the body of chapters 03 to 21. Everything below is a reading, graded Likely at best, until something is run.

---

## 1. The flywheel as it exists

The Loom already names the three parts: the **Loom** makes one thing right, the **flywheel** turns a failure anywhere into a rule everywhere, and the **knowledge graph** stores the momentum so it turns when no agent is running.

Read across the repositories, the wheel has seven stations:

| station | what happens | where it lives | state |
|---|---|---|---|
| 1. Weave | a model, Blender or a generator writes a scene from cards | x3d.loom generators, x3d-blender-io, x3d.lab Foundry | strong: dozens of projects |
| 2. Witness | validator ladder, X_ITE as oracle, second renderers, physics run records | x3d_mcp fork (53 tools, 115 commits ahead of upstream), loomkit, Babylon / three.js / Castle / Unreal legs, x3d.physics | strong for structure; appearance is software-GPU only; physics is new |
| 3. Receipt | the proof of how it was made travels with the file | x3dprov (x3d.ML), loom receipts | built, unsigned, version 0.1 |
| 4. Fold back | each failure becomes a law, a trap rule, a fixture | LOOM-v1: 44 laws, 160 failure modes; x3d_mcp checks | strong inside the family; nothing sent upstream |
| 5. Teach | what was learned is written so a person or an agent can learn it | x3d.docs: 6 teardowns, 21 chapters, 533 numbers (489 Confirmed), 325 heuristics, 163 drills (150 with a recorded run) | two days old and already large |
| 6. Show | worlds people want to open | x3d.demo, x3d.STEM, x3d.music, Mashtots, dirac, KANSEI, x3d.poc | strong: many live pages |
| 7. Draw in | someone outside tries it, breaks it, asks for something | nobody yet | not started |

And three stores of momentum: **rules as code** (validator checks, trap rules), **ledgers** (laws, failure modes, numbers, heuristics, each with a stable id), and the **corpus** (scenes, fixtures, mutants, run records).

## 2. Diagnosis

Three things are true at once.

1. **The wheel spins hard, in a vacuum.** In about two weeks: 81 merged pull requests in x3d.loom, 44 in x3d-blender-io, 37 in x3d.demo, 33 in x3d.lab, 25 in x3d.docs. The discipline is real: grades on every claim, instruments named, "honest limits" on every chapter. But stations 1 to 6 are all inside the family. Stars across 17 repositories total 3; the 33 drafted upstream contributions are unsent; three earlier pull requests to the Consortium's x3d_mcp show as closed, not merged (I did not read why).
2. **The hub is missing.** The knowledge graph, the Loom's third word, exists as fragments: FACTS in x3d.onto, ledgers in x3d.docs, failure modes in LOOM-v1, receipts in x3d.ML, x3d.xray as a reader, KeGG as an idea. An agent starting work today is handed a 115 KB definition to paste. Nothing turns "when no agent is running".
3. **It has not touched the world yet.** The base says so itself, chapter after chapter: every pixel number is SwiftShader on one machine; cross-machine determinism is "visible, not run"; no USD hop was run; WebXR was not exercised; most chapters end "no model was run", so the central claim (that the tether makes a model's 3D better) rests on carried numbers; several artefacts carry "no human has listened yet". The scarce witness is no longer an agent. It is an independent reader: a person, a second machine, a real GPU, a real object.

So the next gains do not come from more bridges or more demos. They come from a hub, a door, and contact with reality.

## 3. Directions, in order

### A. The Atlas: make the knowledge graph the hub

Compile what already has ids into one graph: laws (1 to 44), failure modes (1 to 160), numbers (`N-…`), heuristics (`H-…`), drills (`D-…`), instruments and pins, scenes, receipts, chapters. Edges: *paid for by* (law to incident), *caught by* (failure to check), *measured at* (number to pin), *supersedes*, *contradicts*, *not run*.

- **Serve it** through x3d_mcp as two or three small tools (`laws_for(nodes, engines)`, `what_broke(pattern)`, `how_do_we_know(number_id)`), so an agent's kickoff is a query that returns the dozen laws and traps that apply, instead of the whole definition.
- **Fly it**: x3d.xray's method already turns structured history into an X3D scene. The Atlas as a walkable world (laws as columns, failure modes as the stones they stand on, numbers lighting up by grade) is the family's own map, in its own format.
- **Let it turn alone**: a nightly job re-runs the pinned numbers that can run for free at the newest validator and X_ITE pins, and opens a pull request that adds a dated row or demotes a claim (the pin rule, automated). This is "momentum when no agent is running".
- First step: a script over `x3d.docs/docs/learn/*.md` and `LOOM-v1.md` that emits the graph as JSON-LD and Turtle (the semantic layer of chapter 05 can then query it with SPARQL). Days, not weeks; no new measurements needed.

### B. Open the door: licences, a benchmark, a corpus

- **Licences first.** Most public repositories have none (x3d.loom, x3d.docs, x3d.lab, x3d.demo, x3d.STEM, x3d.xray, x3d.physics, Mashtots, dirac, platformer). Without one, nobody may legally reuse a line. A flywheel that wants researchers needs this before anything else.
- **Tether Bench.** A public, versioned benchmark: N prompts, any model writes X3D, the ladder scores it (valid as written, valid after exact fixes, visible, lawful), with the pins named. x3d.lab's Model Duel and Foundry are most of the machinery. It turns the base's weakest claim (model effects, carried at Likely) into its most reproducible, and it gives model builders a reason to come.
- **The corpus as a dataset.** Scenes with their verdicts at a pin, render statistics, exact-fix diffs and provenance: the 1,533 repository scenes, the 540 mutants, the per-node fixtures, the 195 export cases, the Foundry rounds. Released with a data card and a licence. This is the "3D data" half of the flywheel: evaluation and training data for models that write 3D, which barely exists anywhere.
- **Failure 161.** Invite outsiders to break the Loom: a minimal scene that passes every gate and is wrong. A confirmed find enters the ledger with the finder's name. Credit is the bounty; each find is a new rule.
- **Send three.** Pick the three upstream contributions with the cleanest evidence (for example the ROUTE-order and colour-range checks with their planted-fault tables, and one X_ITE finding with a minimal fixture) and send them. One accepted report is worth more traction than ten more internal chapters.

### C. Touch reality: real GPUs, a second machine, a real marble

- **A second machine for free.** Run the physics replay (`loom.physics-run/1` state hashes, Node and WASM) on GitHub Actions across Linux x86, Linux ARM, macOS ARM and Windows. That answers the Loom's open question 17 (cross-machine determinism) with four machines and no money.
- **A real-GPU lane.** A scheduled x3d.lab run on the G4 and one consumer device (this Mac's GPU in ordinary Chrome) to re-take the headline pixel and timing numbers. Promote or demote; either result is knowledge.
- **A real marble.** Build the ramp of `marble-minimal.x3d` on a table, film it at 240 frames a second on a phone, track the marble, and fit friction and restitution. Then PhysX, MuJoCo, Bullet and the world run side by side, and the world is the reference. The same for a pendulum, a domino wave, a Galton board, and a Chladni plate (sand on a speaker-driven plate against the computed modes: the cymatics of the Mashtots tour, made physical). So far every reference is a closed-form answer; this adds measured reality, which is rare, cheap, and exactly "a tool for learning about the physical world". It also feeds the JEPA bridge (real against simulated twins) and the MuJoCo bridge (system identification).

### D. The Curator's Desk: spend the human witness well

The human is the judge of record for taste, and agents now produce far more than one person can look at or hear. Make that queue a product: a page that serves five blind A/B pairs a day (stills, sounds, motions), records each pick as a gold label, and keeps a visible ledger of what no human has judged. The picks calibrate the model judges (which may only flag), and the debt stops being invisible.

### E. A scribe: a small model that writes lawful X3D

Chapter 16 compiled the X3D JSON Schema into node-restricted schemas for constrained decoding. With the corpus (B), fine-tune a small open model on the G4 as an X3D scribe, decode under the schema, and score it on Tether Bench against the hosted models. This is the model half of the data flywheel: data to model to better scenes to more data, measured each turn. It also makes the loop local, private and nearly free.

### F. The XR leg: evidence you can stand inside

X_ITE 16.7 ships a WebXR component (present in the bundle; not exercised anywhere in the base), and Babylon, the second body, has first-class WebXR. Nothing headset-related has been run, and no USD hop either.

- One flagship per route: a headset browser through WebXR; and glb to USDZ for a visionOS-style viewer, with the identity gates of chapter 19 extended to the USD hop (the missing chapter 22).
- **The witness panel.** One reusable PROTO, generated at weave time from the receipt, that floats beside any world and answers "how do we know?": witnesses, pins, grades, what was not run. On a page it is a side panel; in a headset it is an object you can walk up to. Spatial computing has plenty of content and almost no provenance. Accountable spatial content is the family's wedge.

### G. The dojo: the autodidact's track

The base has 163 drills with answer keys. Wrap them as runnable notebooks in x3d.lab with automatic checking and a personal ledger (predicted, ran, compared, learned), following chapter 14's method. Path E, the skeptic's tour, is the best onboarding a researcher could ask for; make it the front door.

## 4. Sequence

| when | what | why first |
|---|---|---|
| this week | licences on the public repositories; fix READMEs that still say "private"; one front page that maps the family | removes blockers; a day's work |
| this week | Atlas v0 from the existing ledgers; the Actions replay matrix; film the first real marble | all three use only what exists |
| next two weeks | choose and send three upstream contributions; the nightly pin sentinel; the Curator's Desk v0 | first outside contact; the wheel turns alone |
| next two months | Tether Bench v0 and corpus v0 with a data card; the WebXR flagship and the USD chapter; the dojo | the door opens |
| horizon | the scribe model; the registry of experiments; Failure 161 as a standing challenge | the flywheel feeds a model and a community |

## 5. Risks and housekeeping

1. **Two repositories say "private" and are public.** `x3d.onto`'s README says "Private until 2027-01-01" and lists steps to take "before any public candidate" (rewrite history for author emails, scrub vendor names and cost figures). `x3d.ML`'s says "Private, early", and the Loom's open question 9 says its main branch serves a private build graph with internal identifiers. Both are public today (checked through the API and an anonymous fetch on 16 Nov). If that was intended, the READMEs need updating; if not, it wants a look soon.
2. **Verification debt.** Agents wrote the base and agents checked it. Law 44 asks for a second reader who tries to break a number; so far that reader is another agent in the same family. Outside readers (B) and the world (C) are the fix.
3. **Software GPU, one machine.** Stated honestly everywhere, but it caps what can be claimed about speed, appearance and determinism.
4. **Sprawl.** Seventeen active repositories and two accounts with forks in both directions (the docs README still points at the hagsmac Pages address). The Atlas and one front page reduce the cost of finding anything.
5. **Carried numbers.** The paired model-run results (489 against 507 of 540, AUC 0.997) are graded Likely because their measuring documents are not public. Tether Bench replaces them with public runs.

## 6. What I would not do next

- Another renderer bridge or physics engine before the hub exists. There are already six bodies and four engines.
- More demos without a human pick behind them. The shelf is full; the judging is behind.
- Hosting or "planet scale" anything. The interactive path runs in the visitor's browser, and nobody outside has arrived yet. Traction first.

---

## 7. Update, 17 November 2026 (02:00 UTC): what the last hours changed

Refreshed from GitHub: 28 pull requests merged across eleven repositories between 16 Nov 17:36 and 17 Nov 01:47 UTC. I read the pull-request descriptions and the new `x3d.docs` files; I ran only the Atlas and the docs' claim checker.

| repository | merged | what landed |
|---|---|---|
| x3d.ML | #13 | `x3dtrace`: a quote beside every value, checked in code (FIND, COMPARE, LOCATE), stored as a step in the scene's own hash chain; PROV-O and OpenLineage views; an independent review (49 findings, 41 fixed, 8 open) |
| x3d_mcp | #21 to #26 | `scene_brief`, `scene_evidence` (the vendored engine), `source_witness_audit`, `patch_x3d_attribute`, `shacl_counterfactual`, typed SPARQL results, nine semantic twins with evidence states. The fork is now 131 commits ahead of upstream |
| x3d.loom | #83 to #85 | `x3d.s1` 0.2.0: the evidence check, exact facts that fail closed, mutation check v2, an offline Decision Observatory. `LOOM-v1.md` itself did not change |
| x3d.docs | #27 to #29 | chapters 22 (typed judgments) and 23 (traceability and lineage), the claim ledger toolkit (`check_claims.py`, `claims/0.1`), Appendix G. Now 23 chapters, 591 numbers, 359 heuristics, 177 drills |
| x3d.onto | #18, #19 | the Semantic Twin Lab design, 16 tool findings, a 45-item eval set, the Evidence Edition audit and its re-checks |
| x3d.lab, x3d.demo, x3d.music | #34; #39 to #45; #6 | traceability plan for run cards; trace viewer, ontology lab and twin demos; a lineage note |
| x3d-blender-io, x3d.castle, x3d.Mashtots | #45; #3; #5, #6 | a lineage report for the X3D 4.0 export; the docs' numbers checked against their sources; Letter Constellation v1 and quote matching for Armenian text |

**What this changes in the reading above.**

1. **Station 3 (Receipt) gained its missing half.** `x3dprov` said what ran on a scene; `x3dtrace` now says where each value came from, in four repositories at once, with one verdict vocabulary. The seven-layer lineage stack of chapter 23 (bytes, receipts, chain, evidence, ledger, views, anchor) names the one layer still unbuilt: the **anchor**. Its own measurement says why it matters: 3,269 of 3,269 edits to a stored trace caught, 0 of 160 consistent forgeries. A hash-only record cannot do better; a signature or a commit can.
2. **The wheel corrected itself within a day.** Chapter 22's "31 of 499 animated" became 56 after a dead branch was found, and "41 of 41 mutants killed" turned out to be a harness that could not fail (one mutant had survived). Both were found by re-running, written up, and the superseded rows kept. That is the fold-back loop working on the family's own claims, and it is the strongest evidence so far that the discipline is real.
3. **The hub now exists as a first version.** The Atlas (`atlas/`, local) holds 2,181 nodes and 7,222 edges, parses identically as Turtle and JSON-LD, and every row it copied (1,360) is verified at its pinned commit by `x3d.docs`' own claim checker. It adopts the new work as given: the `claims/0.1` ledger, the `.example` namespace convention, `prov:wasQuotedFrom`.
4. **What the Atlas shows about the base** (details in `atlas/out/FINDINGS.md`): the ledgers are well kept and thinly joined. 34 of 591 numbers have a verified quote (chapters 22 and 23 only); 95 of 160 failure modes are tied to no law by number; 317 of 359 heuristics cite no id in their evidence; 138 numbers name their instrument as "same"; 75 numbers stand on X_ITE 16.6.0 while the newest in use is 16.7.1. Each of these is a worklist, and each is cheap.

**What did not change.** No repository gained a licence. `x3d.onto` and `x3d.ML` are still public with READMEs that say "Private"; `x3d.ML#13` itself notes that the missing licence leaves the engine vendored into `x3d_mcp` without a stated licence of its own. Nothing went upstream or to the GAIK project. The reviewers are still agents of the same family.

**Adjusted next steps.**

- **Back-fill the ledgers** for chapters 01 to 21, starting with the 541 Confirmed numbers (`claims_suggest.py` exists for this; the Atlas lists the rows). This turns "a named tool ran" into "and here are the words".
- **Use the ids inside the cells**: `fm N` in each law's evidence, `law N` in each fix, `N-…` in each heuristic's evidence. One pull request to `LOOM-v1.md` and the chapters would roughly triple the graph's joins, and it would fix the two source defects the build found (row 87's unescaped pipes; "law 40 and 123" in failure mode 147).
- **Serve the Atlas** as three `x3d_mcp` tools, and give the nightly sentinel its list (numbers by tool version and pin).
- **Build the anchor**: commit each receipt, or sign it, so that the 0 of 160 becomes something a reader can check.
- **First outside contact, the easy one**: the GAIK project is credited in four repositories and has heard nothing. A short note with the 55 deliberate differences and the first-hit finding (86.1% wrong node on repeated quotes) is a gift to them and costs a page. It waits for an explicit "send".
