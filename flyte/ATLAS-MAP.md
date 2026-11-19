# The AI Engineering Atlas on Gobbler.flyte

Generated from `atlas/aie-atlas.json` (rev 28, 2026-10-20, SHA-256 `b8717094e21eb003…`) and `gobbler_flyte/atlas.py`. The Atlas is an agent-written catalogue of Chip Huyen's *AI Engineering* (O'Reilly, 2024) and the `chiphuyen/aie-book` repo, supplied by HagopJay on 19 Nov 2026 as the content for the Chip Huyen AI Engineering agent. In Gobbler.flyte that agent is the **Assayer**, a fifth organ (`gobbler_flyte/organs/assayer.py`).

Status: **built** = code in this repo does it and a test covers it; **ready** = the hook exists and the next step is small; **later** = needs a model call, a second machine or a person; **n/a** = about training or serving models, which this loop does not do.

## Themes

| Theme | Atlas rows (sources / concepts / code) | Home in Gobbler.flyte | Status | How |
|---|---|---|---|---|
| Agent design, context and protocols | 14 / 31 / 8 | gobbler.py graph | built | one thread per cycle, interrupts for humans, state in SQLite and files, not in the prompt (T11) |
| Benchmark integrity and audits | 19 / 27 / 4 | sealed bucket + instrument pins | built | about 1 in 5 refusals is held out; every score carries dated instrument pins and the Assayer flags pins older than 30 days (T6) |
| Eval containment and incident response | 9 / 23 / 6 | Assayer stop-the-line | built | a failed critical check writes STOP-THE-LINE.json and the runner starts no new cycle until a human clears it (T12) |
| Agent security and prompt injection | 13 / 11 / 5 | Scout + Weaver quoting | built | web text reaches the model quoted and linted (untrusted.py); Scout fetches only configured source ids (T7) |
| Reward hacking and grader gaming | 6 / 11 / 6 | Witness + Assayer canary | built | Weaver sees refusal codes, never the grader's source; a daily canary feeds known-bad fragments to the same instruments (T2, T8) |
| Evaluation process and tooling | 3 / 15 / 5 | Assayer | built | every cycle is assayed against the theses; the day gets a report with sources named |
| Agent evals and false success | 7 / 10 / 3 | Assayer daily report | built | pass@k and pass^k over cycles (Atlas K5), most frequent refusal code, and outcomes read from the world store, not from the agent (T3, T4) |
| Agent memory | 10 / 5 / 1 | memory.py | built | nine kinds, filter before rank, sealed hold-out with an audit (T11) |
| RL environments and training-time misbehavior | 0 / 4 / 3 | Weaver retry loop | built | retries are capped at 3 and a deterministic generator takes over, so a task the model cannot solve never rewards a hack (T13) |
| Architecture and product feedback | 2 / 1 / 0 | council + HITL + foldback | built | council stand-up, GitHub Issues questions with a 4 h timeout, foldback drafts counted apart from reuse |
| Models, prompting and foundations | 8 / 18 / 5 | llm.py | ready | structured output is enforced by the WeaverCandidate contract; sampling settings are pinned in config |
| Retrieval and RAG | 4 / 16 / 5 | compile_context ranking | ready | ranking is lexical today; reciprocal rank fusion (Atlas K2) is the next step once there is a second ranker |
| Reasoning-model evals | 4 / 3 / 1 | budget.py | ready | effort is pinned low and every call is priced; cost-aware reporting needs real calls |
| AI judges and grading | 6 / 13 / 2 | none yet (no model judge) | later | the loop's graders are code; a model judge would need kappa against his labels and a swap test (Atlas K6) first (T5) |
| Finetuning, data and memory math | 7 / 15 / 5 | n/a | n/a | the loop does not finetune |
| Inference and serving | 4 / 15 / 8 | n/a | n/a | the loop calls a hosted model; latency is not on its critical path |

Meta (book, repo, secondary reads): 13 / 0 / 0. Unthemed: 0 / 0 / 0.

## Theses and the Assayer's checks

| Thesis | Rule (Atlas) | Check | Severity |
|---|---|---|---|
| T1 A score is a tuple, not a number | Store the full tuple with every score and diff tuples before comparing two numbers. | `score_tuple` | warn |
| T2 Graders are software with bugs and an attack surface | Audit tasks, isolate the grader from the agent environment, and version the grader like code. | `canary` | stop |
| T3 Grade state, not narrative | Query the system of record for outcomes and keep path checks for hard constraints only. | `state_of_record` | stop |
| T4 Reliability is a distribution | Report k, variance and the worst-case category, not just a mean. | `daily:pass_hat_k` | daily report |
| T5 Judge validity comes before judge reliability | Validate against expert labels with kappa and decoys, and pin judge versions. | not tested: no model judge in the loop yet | - |
| T6 Benchmarks have half-lives | Date every score, schedule re-audits and keep a private slice. | `pin_age` | warn |
| T7 The sandbox is part of the system under test | Inventory permitted egress, remove shared writable stores and review containment before running capability evals. | `egress` | stop |
| T8 Agents optimize the grader they imagine | Check what agents believe about scoring, flag impossible tasks and give agents a safe way to stop. | `grader_opacity` | stop |
| T9 Swarms change the threat model | Evaluate group behavior and peer-instruction authority, not just single agents. | not tested: one demiurge, not a swarm: organs share no writable channel but the state | - |
| T10 Evidence needs provenance | Cite each claim to its evidence tier, state coverage fractions and mark unverified figures. | `provenance` | warn |
| T11 Keep state and context outside the model | Use handles, files and structured notes, and measure tokens per step. | `context_budget` | warn |
| T12 Operate evals like production | Run production monitors on internal evals, rehearse paging and enforce policy outside the model. | `stop_the_line` | halts the runner |
| T13 Misbehavior is trained in, not just discovered | Instrument RL runs: probe-rate curves, effort caps on never-solved tasks, and reward gates on boundary crossings. | `retry_cap` | stop |

## The library

`library.sqlite` holds the Atlas as memory records, apart from the world's own memory: 129 evidence refs (sources), 218 semantic claims (concepts, graded L when a cited source was read, else S), 80 procedures (13 theses with their concepts as parents, plus 67 code sketches) and 51 open questions (gaps and conflicts). Only the Assayer is a reader, so the library never enters Weaver's context. Nothing in it is graded C: no Gobbler instrument ran on it.

## Next, ranked

1. **Judge validity before a judge (T5).** If a model ever grades a turn, first measure it against his labels with Cohen's kappa and a position-swap test (Atlas sketch K6). Needs about 30 of his labels.
2. **Hybrid ranking (rag).** Add a second ranker to `compile_context` and fuse with reciprocal rank fusion (sketch K2) once the library or the world memory has enough rows for lexical ranking to miss.
3. **Stop-the-line issue.** In live mode, open a GitHub issue when STOP-THE-LINE.json is written, so the halt reaches him without reading the state branch.
4. **Real reliability.** pass@k per task needs repeated trials on the same signal; today's day is one trial per task, so the report pools attempts and says so.
5. **Pin re-audit.** `pins_audited_utc` in `config/flyte.json` is a typed date. A job that re-runs the canary against upstream heads and proposes a new date would close T6 properly.
