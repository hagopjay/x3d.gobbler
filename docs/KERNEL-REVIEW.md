# Evidence kernel and archive audit review

Baseline inspected: `11a561623b7539f1f9bf20f8ef7bc5b9706c10d2`.
Scope: local graph/archive consistency and the explicitly synthetic teaching
protocol. This pass does not reinterpret archived claim grades or rerun their
underlying experiments.

## Findings and repairs

| Finding | Independent failing case | Implemented response |
| --- | --- | --- |
| Kernel graph parsing assumed object rows and hashable IDs. Malformed rows could crash with `AttributeError`/`TypeError` rather than a validation result. An empty node type was accepted. | A `null` node; an edge with array-valued subject; a whitespace-only type. | Validate array/object/string shape before accessing fields or using identities as dictionary keys. Malformed shapes raise `ValueError`. |
| Python considers `True == 1`, so a one-node graph could satisfy a boolean embedded count. Equally empty receipt/graph pin maps also compared equal. | One Law node with `counts: {"Law": true}`; both source-pin maps empty. | Counts require exact nonnegative `int` values, excluding booleans. Both pin maps must be nonempty string maps before equality establishes agreement. |
| Replay treated loosely shaped reference containers as iterables and accepted an empty event list as a result with `state: null`. The first candidate event could select an unrelated bound artifact. | String/dictionary references, repeated refs, empty history, candidate selecting the guard rather than an incident artifact. | Nonempty arrays of unique string references; nonempty event/artifact lists; typed event/artifact objects; candidate references must belong to the named incident. |
| Portable audit checked edge endpoints and counts without rejecting repeated triples. Duplicate edges passed after updating metadata and receipt hashes. | Duplicate the existing grade triple, change its embedded count to two, then rehash all outputs. | Track duplicate `(subject, predicate, object)` triples and fail the existing edge-integrity check, independently of hash/count agreement. |
| A ledger row only needed five field names. Its line could be zero/boolean, quote nontext, or value absent from its supposed quote. | Rehash a ledger with `line: true`, or change `value` while keeping its old `quote`. | Require nonempty text identity/value/quote/source, a positive integer line, and the copied literal value within its recorded quote. |
| Root-only or multiply populated X3D documents passed the named basic-structure check. | `<X3D/>`; `<X3D><Scene/><Scene/></X3D>`. | Require exactly one direct Scene child in addition to the X3D root and no Script. |

These cases demonstrate why a self-consistent hash receipt cannot replace an
application invariant. A duplicate edge can have a perfectly matching hash and
perfectly matching totals while still violating graph identity rules.

## Evidence

The Atlas suite now contains **64 test cases**, twelve more than the inspected
baseline. Both commands pass:

```bash
python3 -m unittest discover -s flywheel-review/atlas/tests -q
python3 -O -m unittest discover -s flywheel-review/atlas/tests -q
python3 flywheel-review/atlas/flywheel_kernel.py --check
```

The last command proves that the successful compiled observatory is unchanged
for the supplied archive: SHA-256
`1b4fe6083d53839229df277d480d05f44cce1c2143927985bd301b8f2ea70c1f`.
Its 2,181 nodes and 7,222 edges remain archive facts. No generated scene or
standalone rebuild is needed solely for these kernel changes.

The fresh in-memory portable audit of `atlas/out/` passes all nine existing
check categories. It now reports `duplicateTriples` on edge checks and `scenes`
on the basic scene check. A separately regenerated audit receipt will therefore
contain new detail. The archived outputs and original receipt were not edited.

## Contracts retained

- `validate_graph(graph)` returns the same ID-to-node mapping for accepted
  graphs; invalid shapes now fail consistently before downstream computation.
- `replay_incident(...)` retains its successful result fields and transition
  order: candidate, reproduced, guarded, reused. Partial nonempty histories
  remain inspectable; an empty history cannot masquerade as an executed replay.
- Synthetic promotion still requires an observed-failure reproduction and
  paired positive/negative controls per guard. A reuse requires an active guard,
  a different declared target domain, and a scene input digest matching its bytes.
- A repeated `(guard ID, target domain, input digest)` adds no reuse count.
  Input identity, guard identity and target labels are local caller assertions,
  not independently authenticated organizations or agents.
- `audit(directory)` remains read-only. Its nine named categories and overall
  `ok` field remain stable; stricter failures add detail rather than modify the
  input evidence.

## Limits and useful next work

The ledger test establishes only a well-shaped local quote witness. It does not
fetch the pinned source, reproduce token normalization, prove that a graph field
equals the quote, or promote a claim from quoted to empirically reproduced.
The existing pinned full witness is a separate instrument.

Basic XML checks still do not establish XSD validity, field types, shader
compilation, visual fidelity or correct scientific interpretation. In particular,
archived zero-axis rotations remain the responsibility of the actual semantic
validator; adding a Scene count does not turn this portable audit into one.

The replay reads supplied verdicts. Its content digests detect changed content,
not a forged author or a truthful measurement. A stronger executed foldback
protocol would bind guard code/version, positive and negative input bytes,
runner/environment identity, and output bytes to an actual invocation. It would
then distinguish a declared consumer label from a separately maintained consumer
repository and its acceptance. This needs a versioned protocol extension rather
than silently promoting the existing synthetic teaching data.

When counting reuse, preserve the current retry invariant and explicitly choose
whether guard aliases with identical code bytes denote the same guard. Local
IDs alone should not be treated as evidence of independent consumers or new
knowledge. That is a proposed identity policy, not an implemented authenticity
guarantee.
