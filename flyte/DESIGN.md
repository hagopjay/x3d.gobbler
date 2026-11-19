# Gobbler.flyte 0.1: design, numbers and limits

Written 18 Nov 2026. Every number names its instrument. "Sim" means the simulated day in `runs/sim-2026-11-18/`
(real graph, real gate, real validator, real hash chain; simulated clock, simulated replies, simulated HagopJay).

## 1. One demiurge, four organs

The Gobbler is not a flock. It is one supervising LangGraph `StateGraph` (the demiurge). It has four organs and a council where they report.

```
 every 30 min (GitHub Actions cron, or a Flyte LaunchPlan, or `python -m gobbler_flyte tick`)
   |
   v
 open --> SCOUT --(nothing new)--> close
            |  web3d.org RSS, HN, arXiv, x3d.loom commits, GitHub releases (x_ite, x3d_mcp, blenderizer, three.js, Babylon)
            |  namesake filter (Ryzen X3D, X3D video net) + loom untrusted-text lint
            v
         WEAVER <------- refused, attempts left (max 3) ------- WITNESS
            |  playbook: signal -> x3d.loom pipeline action           ^  accrete gate 2.0.0 (24 nodes + ROUTE, caps, fit)
            |  candidate: Haiku 5.5 (only under a typed allowance)    |  x3d_mcp b5c9956 XSD 4.0 + semantic (same bytes Keeper commits)
            |             or accrete's authored generator (0 calls)   |  x3d.loom traps (15 rules, each paid for by an incident)
            +---------------------------------------------------------+
                                     | pass, or attempts spent
                                     v
                                  COUNCIL  (stand-up: one line per organ, then the Gobbler's ruling)
                     ask /           | proceed           \ hold (refusal kept as a lesson)
                       ask -> wait   |                     close
               interrupt(): the cycle sleeps in SQLite;
               an authorized reply, or the 4 h timeout (reversible only), resumes it
                                     v
                                  KEEPER -> close
            accrete WorldStore.append: gate + XSD + semantic again, SQLite compare-and-swap, hash chain
            foldback draft for x3d.loom / x3d.docs in outbox/, ledger rows in turns.jsonl + tape.jsonl
```

The loop is tight in two places. Inside one cycle, Weaver and Witness bounce until the fragment is admitted or the attempts run out, and the refusal codes are the feedback. Across cycles, a cycle waiting on a human sleeps in its own LangGraph thread (`cycle-N`) while the next ticks keep turning.

## 2. His picks (thread, 18 Nov 01:43Z: "i agree with all your choices")

| # | Question | Answer in force | Where it lives in code |
|---|---|---|---|
| 1 | Agent cast | 4 organs: Scout, Weaver, Witness, Keeper; the Gobbler is the graph | `gobbler.py`, `organs/` |
| 2 | 24/7 host | GitHub Actions cron every 30 min (free on public x3d.gobbler); Flyte LaunchPlan as his own server | `.github/workflows/gobbler-flyte.yml`, `flyte_wf.py` |
| 3 | Spend gate | one typed daily allowance ("OK $0.03/day" on a flyte-decision issue) | `budget.py`, `hitl.py` |
| 4 | Brain | no model by default; **only his own Claude Haiku 5.5 key** ("if it is my haiku 5.5 that runs the agents then i can allow some cap") | `llm.py`, `config/flyte.json` |
| 5 | Authorized humans | hagopjay only | `config/flyte.json` `authorized_humans` |
| 6 | Where they ask | GitHub Issues, label `flyte-decision` | `hitl.GitHubIssues` |
| 7 | Timeout | 4 h, then the preferred pick; irreversible never auto | `gobbler.ask`, `runner.tick` |
| 8 | Sources | web3d.org, GitHub releases, HN, Reddit r/threejs + r/webgl (X and Discord skipped: logins) | `config/flyte.json` `sources` |
| 9 | Own powers | PRs on their own branch only, through the auto-merge lane | Keeper writes drafts; PR opening is step 2 (see 12) |
| 10 | Name | **Gobbler.flyte**, not "Flock": one demiurge; the name says it can run on its own Flyte server | this folder |

## 3. Organs

| Organ | Reads | Writes | Instruments it names | Model use |
|---|---|---|---|---|
| Scout | 12 sources (`config/flyte.json`) | ranked signals, namesakes set aside, `seen` memory | `relevance.classify` rules; `loom/untrusted.lint_text` (x3d.loom 4cf5c7a) | none |
| Weaver | top signal, last Witness refusal codes | proposal (A/B/C, preferred pick, reversible?), X3D candidate | playbook (9 actions); accrete `generator.generate` (6 families) | Haiku 5.5 only if allowance and budget allow; else 0 calls |
| Witness | candidate bytes | verdict + grade (Confirmed / Likely / Suspected / Refused) | accrete gate 2.0.0; x3d_mcp b5c9956 XSD + semantic (via accrete's vendored copy); loom traps (15 rules); loom target probe | none |
| Keeper | verdict, decision | world entry (hash chain), turns.jsonl, outbox foldback draft, world-archive.json | accrete `WorldStore.append` (CAS + append-only triggers) | none |
| Gobbler | everything | open/council/ask/wait/close rows, budget rows | `Budget.check` (list price, worst case) | none |

Three counters, never merged (Atlas rule, `flywheel-review/FLYWHEEL.md`): **admitted** (entry in the chain), **drafted** (foldback in the outbox), **reused** (a second consumer took it up; only a merged PR can confirm it, so it stays 0 until the PR step exists).

## 4. Human in the loop

| Case | What happens | Timeout pick? |
|---|---|---|
| Witness grade Confirmed or Likely, reversible, no ask flag | proceeds on the preferred pick, logged | n/a |
| Weak score (< 0.7) or SYNTHETIC source | asks; preferred pick is B (note only) | yes, after 4 h |
| X_ITE / validator / blenderizer actions | asks (they move pins every receipt names) | yes, after 4 h |
| Outside send (upstream issue to Web3DConsortium/x3d_mcp) | asks; "A" only counts with the word "send" | **never** |
| 3 questions already open | reversible: preferred pick goes ahead and says so; irreversible: still asks | n/a |
| Comment by anyone not in `authorized_humans` | ignored | n/a |
| "OK $x/day" by an authorized login | becomes the allowance (refused above $1/day as implausible) | n/a |

Answers are read on the next tick, so a reply at 09:50 resumes the cycle at 10:00 (sim cycle 19).

## 5. Spend

Haiku 5.5 list price $0.10 / $0.50 per 1M input/output tokens (prompts up to 100K). Source: claude-api skill model table, cached 2026-11-03. Re-check before turning it on. Estimates use arithmetic, not invoices. The ledger records `response.usage` after every real call.

| Quantity | Value | How |
|---|---|---|
| Worst case per call | $0.000625 | ~2,500 in at 3.5 chars/token + 1,200 out (`max_tokens`) |
| Per-cycle cap | $0.003 | config `per_cycle_cap_usd` (about 4 calls) |
| Sim: 52 calls in 24 h | $0.0283 of a $0.03 allowance | 121,380 in / 32,320 out (scripted usage x list price; no API call) |
| A month at "OK $0.03/day" | at most $0.90 | 30 x 0.03, enforced by `Budget.check` |
| A month at zero allowance | $0 | every organ has a deterministic path |
| GitHub Actions minutes | $0 on a public repo | x3d.gobbler is public (GitHub search API, 18 Nov) |

## 6. What the live web said (snapshot 18 Nov 2026 01:46Z, this container, curl)

| Source | Result | Lesson now in code |
|---|---|---|
| web3d.org `/rss.xml` | 200, 10 items, all X3D | trusted source (`x3d-home`) |
| web3d.org `/news/feed` | 200 but HTML (Drupal), 0 items | use `/rss.xml` |
| HN date search "x3d" | 20 stories, **0** about X3D (the tokenizer matches "3D") | use a title search with a quoted term |
| HN title search "x3d" | 12 stories: 6 X3D, **6 AMD Ryzen X3D chips** | `amd-x3d` namesake rule |
| arXiv `all:X3D` | 15 papers: **11 the X3D video-recognition network**, 1 X3D-relevant, 3 other | `x3d-video-net` rule incl. `X3D-M` / `X3D-L` variants |
| GitHub release Atom (x_ite, three.js, Babylon, Web3DConsortium) | **403 from this container's proxy** | releases API with GITHUB_TOKEN on Actions; untested here; sim uses 4 labelled SYNTHETIC rows |
| Reddit `.rss` | 404 from this container | kept in config; unverified until the first Actions run |
| x3d.loom commits Atom | 200, 20 entries | merge commits dropped (the change is its own entry) |

## 7. The simulated day (`runs/sim-2026-11-18/summary.json`)

| Measure | Value |
|---|---|
| Ticks / tape rows | 48 / 525 |
| Cycles with a fresh signal / empty | 35 / 13 |
| World entries admitted (gate + XSD + semantic + CAS) | **35 of 35 turns**; archive verifies (35 checked, `verify_archive`) |
| Weave attempts / Witness refusals | 61 / 26 (GATE_CONTAINMENT 9, MCP_SEMANTIC_PROFILE_COMPONENT 9, GATE_NODE_FORBIDDEN 8) |
| Entries by generator | 26 model-written (FakeLLM script), 9 accrete procedural (fallback after 2 refusals) |
| Questions / answered by him / timed out | 8 / 3 / 5; the outside send waited 6 h for his "B" and was never auto-taken |
| Namesakes set aside | 17 |
| Grades of admitted turns | 31 Confirmed, 4 Suspected (synthetic sources) |
| Foldback drafts / reused | 35 / 0 (reuse needs a merged PR) |
| Wall clock | 4.3 to 4.8 s for 48 ticks (Python 3.13.18, this container) |
| Stills | X_ITE 16.6.0 (x3d.accrete vendor), Chromium 157.0.8103.78 headless, SwiftShader, 1280x720: `stills/world-01,12,35.png` |

## 8. Finding F1: the referee disagrees with itself (Confirmed)

x3d.accrete's gate (2.0.0 @ 93063bf) admits `PhysicalMaterial`. Its world wrapper writes `profile="Immersive"` with no `<component name="Shape" level="2"/>`. So the pinned x3d_mcp semantic check (b5c9956, `profile-component`) refuses every PhysicalMaterial candidate at commit. This is x3d.loom LEARNINGS-accretion.md row 1, recorded at the 17 Nov review; Gobbler.flyte re-found it on its first simulated cycle, so it is still open at 93063bf. In the first simulated day, when only Keeper ran the validator, 22 of 44 turns were refused at commit, all by this one check. Witness now runs the validator before Keeper, so a model hears the reason and retries. Two possible fixes for x3d.accrete, his call: (a) the wrapper declares `component Shape:2` when a fragment uses PhysicalMaterial, or (b) the gate drops PhysicalMaterial. Test: `tests/test_flyte.py::Referee`.

## 9. Synergy sweep (9 agents, 96 finds, 54 Confirmed; full list in `runs/synergy-sweep.json`)

| Rank | Piece | Organ | State |
|---|---|---|---|
| 1 | x3d.accrete `WorldStore.append` + `gate_fragment` + `generator` + `mcp_adapter` | Keeper, Witness, Weaver | **wired** |
| 2 | x3d.loom `kit/loomkit/traps.py` (15 incident-paid rules) | Witness | **wired** (hash-pinned copy) |
| 3 | x3d.loom `x3d.s1/x3d_s1/untrusted.py` (injection lint) | Scout, Weaver | **wired**: web text reaches Haiku quoted, capped or withheld |
| 4 | x3d.gobbler `flywheel_kernel.py` (candidate > reproduced > guarded > reused) | Keeper | next: drive the reuse counter with it |
| 5 | x3d.loom `kit/loomkit/receipt.py` + `accept.py` (loom.receipt/1, named profiles) | Keeper | next: one receipt per admitted turn |
| 6 | x3d_mcp `validation/hints.py` (`gate`, `repair_with_hints`) | Weaver | next: repair before re-asking the model (0-cost retries) |
| 7 | x3d.accrete `tools/export_static.py` + X_ITE viewer | Keeper | next: publish the growing world to Pages each tick |
| 8 | x3d_mcp `x3d_utils/claims.py` (hash-chained claim ledger, graded) | Keeper | next: claims for every number on the tape |
| 9 | x3d.ml `drift/canary.py` (validator drift canary, already in Actions) | Witness | next: alarm when a pin moves |
| 10 | x3d.lab `x3dlab/shrink.py` (delta debugging) | Witness | next: shrink a refused fragment to the minimal failing case for the foldback note |
| 11 | x3d-blender-io `tools/fidelity_rig/render.mjs` (X_ITE + Babylon pinned) | Witness | next: render witness row (accrete keeps it `not_run`) |
| 12 | x3d.demo front-page card format | Keeper | Demo 44 card asked of the bridge thread |

Instrument skew the sweep found, which matters before any number is compared: X_ITE is pinned at 16.4.3 (x3d_mcp render.py), 16.5.0 (x3d.ml), 16.5.1 (loom shots.cjs), 16.6.0 (accrete), 16.7.1 (blenderizer rig). The validator is pinned at b5c9956 (accrete, stem) and 8dd0d3e (x3d.ml jsval, drift canary).

## 10. Hosts

| Host | Cost | State | Status |
|---|---|---|---|
| GitHub Actions cron | $0 (public repo) | text ledgers on branch `gobbler-flyte-state`; SQLite in the Actions cache | written; the state-branch shell logic was tested twice against a local bare clone; **not yet run on GitHub**; OFF until `FLYTE_ENABLED=true` |
| Flyte (his own server) | $0 (sandbox in Docker on his PC) | mount `state/` as a volume | `pyflyte run flyte_wf.py gobbler_flyte` ran one real tick here (flytekit 1.16.32, local); LaunchPlan `gobbler_flyte_every_30m` serialises with `*/30 * * * *`; sandbox not tried |
| His PC, plain | $0 | `flyte/state/` | `python -m gobbler_flyte tick` + `answer` commands |

## 11. Real vs simulated

| Real in the sim | Simulated in the sim |
|---|---|
| LangGraph graph, interrupt/resume, SQLite checkpoints | the clock (48 ticks) |
| Scout's filter on a real 01:46Z snapshot (71 items) | the arrival minute of each snapshot item |
| accrete gate, x3d_mcp XSD + semantic, loom traps, CAS world | 4 GitHub release rows (labelled SYNTHETIC) |
| budget arithmetic and caps | Haiku replies and their token usage (FakeLLM) |
| timeout and irreversible rules | HagopJay's replies (SimHumans) |

## 12. Next steps, ranked

1. Turn on: set `FLYTE_ENABLED=true`, run once by hand (Actions > gobbler-flyte > Run workflow), read the first live tape.
2. Keeper opens real PRs (A picks) on `flyte/<cycle>` branches through the auto-merge lane; reuse is counted when one merges.
3. Wire synergy items 4 to 7 (receipt per turn, kernel-driven reuse, hints repair, Pages world).
4. Village Voice: a Gemini critic organ (organ #5) only on his yes. Gemini spend is outside this allowance.
5. Fix F1 in x3d.accrete (his pick of a or b).

## 13. Limits

No live LLM call was made: every model reply in this folder is scripted. No GitHub issue was opened. The Actions workflow has never run on GitHub. The GitHub release and Reddit paths are unverified. The stills come from software GL (SwiftShader) on one machine, not a GPU. "Admitted" means bounded-vocabulary + XSD + semantic + chain. It does not mean beautiful, visible from every camera, or adopted by anyone.

## 14. Review integration (18 Nov 2026, after PR #1)

A second model reviewed main at 11a5616 (`../docs/FLYTE-REVIEW.md` and the other review files). Its patch went in unchanged. Then this pass ran what the reviewer's host could not, and closed part of what it deferred.

| From the review (kept as is) | Effect on the loop |
|---|---|
| Grade capped at Likely (Suspected for synthetic). Path existence no longer gives Confirmed. | The simulated day re-run gives 31 Likely and 4 Suspected, where it used to give 31 Confirmed. Nothing else changed. |
| `evidence_facets` on every turn: candidate structure, source (archived / synthetic / unverified_live), target presence, reuse | One grade no longer stands in for six questions |
| Mode isolation: unknown mode fails; offline never builds a model client; sim needs a client that declares `simulated` | The cron can't drift into a priced call by mode |
| Allowance and answer grammar are exact. `A send` must be the whole answer, so "resend" or "do not send" no longer pass. Finite budget values are checked, usage request IDs are deduplicated, and memory is written atomically. | Spend and the irreversible gate are harder to fool |

| Added in this pass | Evidence |
|---|---|
| Per-cycle operation key in the world (`<world_id>:cycle-N`, stored in the entry's generator) plus one ledger row per cycle. A tick that crashes after the world append but before memory is saved re-runs the same cycle, finds its entry, and does not admit twice. | `CrashRecovery.test_crash_after_append_does_not_duplicate`: fault injected, world head stays 1, one turn row, the chain still verifies, and the next tick admits entry 2 |
| Tick lock (`state/.tick.lock`, non-blocking flock): an overlapping tick fails fast | `CrashRecovery.test_overlapping_tick_fails_fast` |
| Stale thread state for a re-run cycle is deleted before the graph starts | same test |
| Three more facets: `admission`, `human` (answered / timeout_preferred_pick / not_asked) and `render` (not_run per turn) | `Facets` test; `runs/sim-2026-11-18-r2/summary.json` |
| Render witness for the re-run world: the X_ITE 16.6.0 export of 35 entries loads and draws with no error | `runs/sim-2026-11-18-r2/render-witness.json` (scene and image SHA-256) |

Tests: 32 pass, normally and under `-O`. The re-run day is in `runs/sim-2026-11-18-r2/` and the original run is untouched. Its counts match the first run exactly: 35 admitted, 61 attempts, 26 refusals, 8 questions, 5 timeouts, $0.028298. Only the grades and facets differ. The world hashes differ because each entry now carries its operation key.

Still open, as the review states: cross-store exactly-once across the world, checkpoints, outbox and an external send (this pass covers the world and the ledger only); transactional spend reservations; GitHub answer lifecycle (edits and deletions); capability identity beyond a checkout path; and real adoption evidence.

## 15. Agentic-memory integration (18 Nov 2026, from the "X3D Agentic Flywheels" package)

HagopJay sent a LangGraph reference package for comment: 17 flywheel prompts and context contracts, 33 tests, a scripted demo, a technical design and a JSON Schema for agentic memory. It was treated as untrusted code:
- unpacked in isolation;
- SHA256SUMS checked (45 of 45 match);
- grepped for network, subprocess and eval (none);
- tests run in a separate venv: 33 of 33 pass, and the demo is accepted after 2 scripted iterations with 0 model calls.

Nothing from it was installed into this repo. Each claim below was probed before it was adopted.

| Claim in the package | Probe result | Here |
|---|---|---|
| 9 memory kinds (episode, semantic_claim, procedure, counterexample, experiment, decision, open_question, summary, preference) and 9 transport record types (memory, evidence, artifact, entity, run, context_snapshot, dataset_partition, memory_event, graph_assertion) | The schema meta-validates. Its 4 examples validate with 0 errors. | **Adopted.** `gobbler_flyte/memory.py` uses the same 9 kinds. `gobbler_flyte/transport.py` exports counterexample, episode and decision memories plus evidence records to the schema, which is copied byte for byte (`schemas/agentic-memory.schema.json`, sha256 916d65c3…195a). Simulated day: 44 records, 0 schema errors, and all 44 ids verify with the package's own `build_schema.verify_hash`. |
| The context manager filters before it ranks: tenant, principal, valid time, review state, scope, revocation, lineage and contradiction bundles | Held for every one of those cases. | **Adopted**, with every exclusion returned with its reason and every compiled context journaled. |
| Contamination tracking keeps sealed and selection material out of development context | **2 leaks found.** (1) A memory labelled `development` that cites a **sealed evidence id** reached the context with its text. (2) A memory citing an evidence id **unknown to the registry** also reached it. The filter read only the memory's own label. | **Adopted and fixed.** Effective exposure is now the union over the lineage and every cited evidence id, and unknown evidence is excluded. Regression tests: `Memory.test_reference_package_leaks_are_closed`. Added `audit_contamination`, which proves from the context journal that no held-out record reached a prompt; its negative control is a hand-built leaking context, which the audit flags. |
| Candidate contract: extra fields forbidden, sizes bounded, no invented artifact refs or evidence | Held: extra field, empty summary and a bad artifact name were all rejected. | **Adopted** as `WeaverCandidate`. A Haiku reply that breaks it never reaches Witness as a real candidate. |
| Sealed tests | The package specifies them but holds none out in its demo. | **Built.** About 1 in 5 Witness refusals is sealed by its own bytes (`seal_bucket`), never by its outcome. Sealed counterexamples, and episodes that descend from them, stay out of Weaver's context. Simulated day: 45 contexts, 2 held out, 0 leaks. |
| Counterexample with a lawful twin | A schema slot only. | **Filled.** When Weaver is refused and then admitted in the same cycle, the admitted fragment is the refused one's lawful twin. Simulated day: 3 of 3 counterexamples have one. |

Honest scale: the simulated day yields only 3 distinct counterexamples, because the scripted replies repeat fragments, and identical bytes share one record. A live day will give more.

Not adopted, and why:

| Part | Reason |
|---|---|
| The 17 flywheel prompts and catalog | These are other lanes (chess, Blender IO, STEM authoring and others). Gobbler.flyte has 9 playbook actions. They are kept as a reference for those lanes, not vendored. |
| Its LangGraph engine (intake, prepare, propose, evaluate, review, persist) | Gobbler's graph already has its council, the 4 h timeout pick and per-cycle interrupts. The engine's mandatory review on every run conflicts with the timeout rule. Its execution-binding idea matches the op keys already in place (section 14). |
| Tenant and principal model, Neo4j Cypher, LangChain adapter | This is a single-tenant repo with no graph server (GCP is off and spend is near zero). The transport export keeps records portable to that store later. |
| Its ranking | Lexical overlap only, so not a semantic retriever. It is kept, because it is cheap and deterministic, and counterexamples rank first. |

## 16. The Assayer: the AI Engineering agent (19 Nov 2026)

HagopJay asked for a "Chip Huyen AI Engineering agent" and supplied its content: the AI Engineering Atlas, an agent-written catalogue of Chip Huyen's *AI Engineering* (O'Reilly, 2024) and the `chiphuyen/aie-book` repo (rev 28, 2026-10-20). The Atlas has 129 sources, 218 concepts, 67 code sketches, 51 gaps and conflicts, 16 themes and 13 theses. It was handled as data: only the page's DATA block was evaluated, as literals, and none of the page's code was kept. It is pinned at `atlas/aie-atlas.json` (SHA-256 `b8717094…`), and a test fails if it drifts.

**Two ontologies, kept apart.** THE WORLD's memory (`memory.sqlite`) is experience: refusals, admissions and decisions, written by trusted organ code. The library (`library.sqlite`) is knowledge: the Atlas as 129 evidence refs, 218 semantic claims, 80 procedures and 51 open questions. Claims are graded L when a cited source was read, else S; none is C. Only the Assayer reads the library, so it never enters Weaver's context. A test proves that every library row is `not_a_reader` for Weaver.

**The fifth organ.** Every path to `close` now passes the Assayer. It runs one deterministic check per testable thesis, cites the thesis from the library by id, makes no model call and costs nothing.

| Thesis | Check | On failure |
|---|---|---|
| T1 A score is a tuple | instrument pins, mode, attempts, utc and model on every turn | warn |
| T2 Graders have bugs | once per UTC day, 3 known-bad and 1 known-good fragment through the same gate and pinned validator | **stop** |
| T3 Grade state, not narrative | the world store, read by this cycle's operation key, must agree with the turn row | **stop** |
| T6 Benchmarks have half-lives | instrument pins re-audited within 30 days (`config.assay.pins_audited_utc`) | warn |
| T7 The sandbox is part of the system | the signal came from a configured https source (an item's own link is data, not egress) | **stop** |
| T8 Agents optimize the grader they imagine | the contamination audit: no held-out record ever reached a prompt | **stop** |
| T10 Evidence needs provenance | grade never above Likely; archived source bytes hashed | warn |
| T11 Context is a budget | tokens in per call and dollars per cycle under their caps | warn |
| T13 Misbehavior is trained in | attempts never pass the inner-loop limit | **stop** |
| T12 Operate evals like production | any **stop** writes `STOP-THE-LINE.json`; the runner then starts no cycle and resumes no sleeper until a human deletes it | halts |
| T4 Reliability is a distribution | `assay-report.json` for the day: pass@1 and pass^3 (Atlas sketch K5), the attempts histogram and refusal codes | report |

T5 (judge validity) and T9 (swarms) have no subject in this loop. The map says so rather than passing them.

**It caught a bug on its first run.** The first version of the egress check also required the signal's own link to be https. An HN item linking to an http page stopped the line at cycle 19, and the simulated day admitted 18 turns instead of 35. The check was wrong, not the loop: Scout fetched from the configured https API, and the item's link is never fetched. The check now judges the fetch source. The first canary also had a "known-bad" fragment that the gate admits. It lacked the interpolator and ROUTEs that the real refusal had nested inside the Group, and adding them brings GATE_CONTAINMENT back (Likely: the exact rule was not read). The canary reported itself not held instead of passing. Both mistakes were caught by the mechanism they were testing.

**The re-run day** is in `runs/sim-2026-11-18-r4/`, with r3 untouched. Per-turn outcomes are identical to r3: 35 admitted, the same actions, choices, attempts, grades and spend ($0.028298). All 48 cycles were assayed, with 0 stops. The canary held 4 of 4 once. T3 state_of_record passed 35 of 35. Pooled over 61 attempts, pass@1 is 0.574 and pass^3 is 0.182. The pooling is stated in the report: these are different tasks, not K5's repeated trials. 18 of 35 turns were admitted on the first attempt, and the most frequent refusal was GATE_CONTAINMENT (9, tied with MCP_SEMANTIC_PROFILE_COMPONENT).

Where every Atlas theme lives, what is built, what is ready and what comes next: [ATLAS-MAP.md](ATLAS-MAP.md). Tests: 49 pass, normally and under `-O`.

## 17. Second external review: hardening (19 Nov 2026)

HagopJay sent the loop to an outside reviewer with a prompt that named our own weak spots. The reviewer returned a ranked review, six patch groups, 26 before/after probes and a complete patch against `9d4671d`. The patch is applied **unchanged** as one commit. This thread then re-ran the evidence on its own host instead of relying on the reviewer's receipts (`receipts/review2-reproduction.json`, grade C):

- **Probes.** Each of the 26 probes fails on an untouched `9d4671d` worktree and passes on the patched tree. Every baseline failure is a real assertion or the reported KeyError, not an import error.
- **Crash campaign.** In the reviewer's seven after-write process deaths, the baseline fails 3: world append (episode subject differs from the committed candidate), tape append (duplicate cycle-open event) and library seed (incomplete). The patched tree passes 7 of 7.
- **Tests and checks.** 94 tests pass, also under `-O`. `check_release.py` passes 19/19, and `verify.py` reports 0 FAIL.
- **Simulated day** (`runs/sim-2026-11-18-r5/`, with r1 to r4 untouched).
  - Unchanged from r4: the per-turn outcomes (35 admitted; same actions, choices, attempts and grades) and the actual spend ($0.028298 over 52 calls).
  - Changed: the pre-call estimates, because the prompt changed.
  - Contexts fall from 45 to 37 unique hashes, because hidden exclusions no longer enter the packet.
  - The canary now holds 5 of 5 across gate, validator and traps. T3 is checked on all 48 cycles, not just the 35 with turns.

What changed in substance:

| Area | Before | After |
|---|---|---|
| Sleeper recovery | Checkpoint deleted before the scheduler saved; a crash wedged the next tick | Scheduler state saved first; in-flight cycles resume at their saved node with the original candidate |
| STOP | Checked once per tick, and a cleared long stop let overdue sleepers take the timeout pick at once | Checked after every resumed cycle; a cleared stop reopens a full 4 h window |
| Prompt boundary | Sealed refusals could re-enter through the direct retry text; model-echoed validator text reached later prompts raw | One admission path for all feedback; diagnostics quoted or withheld; the compiled prompt is hash-bound before the adapter |
| Context packet | Hidden ids appeared in `excluded`; the byte cap applied before final serialization | Exclusions go to an operator-only sink; the cap is enforced on the final bytes |
| Transport | Catalogue rows exported as executed C failures; a tampered `payload_sha256` validated after silent repair; reviewer guessed from the first word | A conservative projection with `restorable: false`; supplied hashes are checked; unknown decisions abstain; twins stay null without structured proof |
| Assayer | The canary skipped traps and ran once a day whatever changed; T3 only ran with a turn; egress only checked the chosen signal; a future pin date passed | Instrument-bound canary with trap controls; T3 on every cycle; per-fetch receipts; future dates refused; `assay-day/2` with explicit denominators and same-signal reliability left unmeasured |
| Atlas library | Seeded if `aie:T13` existed; theses graded L regardless of premises | Full-inventory check with resumable seed; weakest-premise thesis grades (6 theses fall to S); explicit archived rebuild for old libraries |

**This thread's own pass.** 21 of the 94 tests are pytest functions (parametrize, raises). CI ran `python -m unittest discover`, which silently skips them: it runs 73. CI and the README now use pytest, normally and under `-O`.

**Statistics corrected** (the reviewer's reading, which we accept):
- "pass@1 0.574" was 35 Witness passes in 61 adaptive attempts.
- Task first-attempt admission is 18 of 35 (0.514).
- The old pass^3 was a combination ratio over different tasks, not reliability.
- "2 held out" means two linked memory records, not two contexts.
- Matching r3 to r5 is a regression result. FakeLLM ignores its prompt, so these runs say nothing about whether memory helps a model.

**Narrower claims.** The contamination audit measures exposure-policy compliance, not grader gaming. The retry cap is an invariant, not an RL method. A typed date is not a re-audit. The Atlas's read statuses are attributed self-reports. The two bad checks caught in §16 were first-run debugging, not autonomous self-correction.

**Deployment.** The cron has never run (`FLYTE_ENABLED` is unset), so no live `library.sqlite` needs the archived rebuild. If one ever does: stop the runner, then run `python -m gobbler_flyte.atlas rebuild-library /abs/path/library.sqlite`. It archives the old database; it does not delete it.

**Next, from the review.** In order:
1. Give each Assayer check a contract record: claim, predicate, scope, instrument and control digests, positive and negative controls, failure action, and expiry.
2. Write a lossless export with execution receipts and reference closure.
3. Measure improvement directly: memory on vs off over fixed task families, repeated trials on identical signals with fallbacks counted apart, and reuse witnessed downstream.

Live issue delivery, provider-billing reconciliation and power-loss recovery remain unvalidated.
