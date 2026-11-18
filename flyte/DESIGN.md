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
