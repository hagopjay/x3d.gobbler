# Flyte workflow review and bounded repairs

Baseline inspected: `11a561623b7539f1f9bf20f8ef7bc5b9706c10d2`.
The workflow is an optional orchestration layer, separate from the browser
observatory and its archived graph. Its useful unit is a source observation,
candidate, scoped witness, decision and turn. A sculpture passing validation
does not establish that an external claim is true or that another project reused
the proposed work.

## Findings repaired

| Boundary | Baseline defect | Implemented behavior and control |
| --- | --- | --- |
| Execution mode | An unknown mode fell through to network fetching. `offline` mode could construct the real model client when an allowance was present. | Unknown modes fail before channel/network work. Offline generation is procedural even with an allowance/key. Sim mode requires an injected client explicitly declaring simulation. A real LangGraph offline control asserts zero network/model construction. |
| Fixture provenance | Ordinary archived feed items lost the fixture status returned by the fetcher. Synthetic release rows relied on their payload to retain a synthetic flag. | Every fetched item retains mode, fixture/live transport and exact parsed-body SHA-256; fixtures name their source file. Authored release fixtures are forcibly synthetic. Turn records and local drafts retain that distinction. |
| Evidence grade | A passing candidate and an existing target path produced `Confirmed`. | Broad grade is capped at `Likely` for nonsynthetic observations, `Suspected` for synthetic ones and `Refused` on failure. Separate facets record candidate structure, source provenance, target presence and unverified reuse. No automatic empirical confirmation is inferred. |
| Allowance parsing | A valid prefix could accept trailing contradictory text. The CLI routed a valid dollar-sign-free monthly allowance to a decision answer file. | The complete first line must match the allowance grammar; CLI routing calls that parser. Tests reject contradictory suffixes and an overflowing number, and verify monthly routing. |
| Budget arithmetic | Negative/nonfinite prices, usage or allowances could poison accounting; six-decimal rounding erased small costs; fake prompt allocation scaled with an untrusted count. | Validate finite nonnegative numeric values and integer token counts; retain full arithmetic precision; compute token estimate directly from the character count; enforce canonical UTC strings. Nullable absent caps normalize to zero. |
| Usage replay | Recording the same provider request ID twice double-counted identical usage. | An existing matching request ID returns the previous usage row. A conflicting cycle/organ/model/token/simulation identity raises. This is usage-ledger idempotence, not whole-cycle exactly-once execution. |
| Human decision parsing | Searching for the substring `send` accepted `resend` or a sentence saying `do not send`. | The irreversible A option requires the explicit first-line form `A send` (optional final period/exclamation). Negative controls reject those lookalikes. This review sends no message. |
| Local persistence | Rewriting memory in place could truncate JSON, and exceptional graph construction left its SQLite connection open. | Flush/fsync a temporary memory file and atomically replace it; clean up failed replacements. The checkpoint connection closes in `finally`. Fault controls preserve previous memory bytes and observe connection cleanup. |
| Feed resources | A live response was read without a byte limit. | Read at most the declared 2 MiB plus one detection byte; reject oversize bodies and unknown feed kinds before parsing. This is a declared budget, not a complete feed-security audit. |

The source/body identity identifies the bytes consumed by the parser. It does
not authenticate a publisher or certify that a remote publication remains
current. In particular, fixture mode never becomes a fresh live observation
because its path exists or because its sculpture passes XSD checks.

## Accounting semantics

The configured prices and model name are retained as historical project
parameters. This review does not validate their present commercial availability
or pricing and makes no paid API calls. Reported simulated usage is still
separately flagged and is not an invoice.

The pre-call calculation combines a heuristic input-token estimate with the
configured maximum output count. It is not a tokenizer-derived upper bound.
`estimate_exceeded` records an observed overrun; later gates use actual recorded
usage. This mechanism cannot guarantee a hard provider invoice cap: a real
request can fail after being billed, actual input counts can exceed the
heuristic, and parallel runners do not reserve funds transactionally. Those are
explicit follow-up requirements before unattended paid operation.

## Validation

The existing fourteen unittest cases are retained and extended with fifteen
independent controls. Assertions use unittest methods, so optimization cannot
erase them. No test uses a live feed, real model API, external issue or message.
The real-graph offline control uses an intentionally unavailable world adapter
and asserts a held, nonadmitted turn; it does not pretend admission passed.

With the pinned LangGraph dependencies installed:

```bash
python3 -m unittest discover -s flyte/tests -v
python3 -O -m unittest discover -s flyte/tests -v
```

Three existing integration cases require the public `x3d.accrete` checkout and
its actual pinned validator. When unavailable they explicitly skip; that result
must be reported as incomplete integration evidence. The accompanying review
workflow provisions the public checkout to execute those cases rather than
converting skips into passes. The release receipt owns final counts, dependency
identities and results.

## Deferred work: do not infer these guarantees

1. **Cross-store crash recovery.** Keeper appends to the world before writing
   its draft/turn ledger, while the runner persists memory, checkpoints and tape
   separately. An interruption can therefore duplicate admission or omit a
   correlated record on retry. Use a durable per-cycle operation ID, an outbox
   transaction and reconciliation with the actual world chain before claiming
   exactly-once turns.
2. **Concurrent spend reservations.** Serialize runners or add a transactional
   reservation ledger with settlement/recovery. A usage request-ID check alone
   does not protect two simultaneous writers or requests without an ID.
3. **Adversarial pagination and answer lifecycle.** GitHub issue polling has
   fixed page limits; chronological validation, edited/deleted answers and
   durable resolution need independent tests. File channels are local workflow
   inputs, not authenticated identities by themselves.
4. **Capability identity.** `accrete.available()` currently means a candidate
   checkout path exists, and its short commit label does not certify a clean,
   compatible instrument. Bind full source/dependency hashes and execute
   positive/negative capability controls before treating that adapter as ready.
5. **Independent adoption evidence.** Keeper correctly records `reused=False`.
   A merged PR, external consumer execution and measured improvement require
   their own observations; none follows from an admission, draft or animation.

Archived simulation runs remain untouched. Their older grades and prices are
historical outputs, not freshly recomputed acceptance of this changed source.
