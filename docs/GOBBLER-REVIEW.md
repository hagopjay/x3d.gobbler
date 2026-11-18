# Gobbler: technical and creative baseline review

Baseline inspected: `11a561623b7539f1f9bf20f8ef7bc5b9706c10d2`.
Review date: 17 November 2026, America/New_York.

This document assesses that baseline. Function and file references below name
the inspected revision; accompanying implementation notes and fresh release
receipts determine which findings the current patch repairs. Archived claims
and measurements remain historical. A code reading, a local structural test,
a native rendering run and a scientific experiment answer different questions.

## The project worth preserving

Gobbler has a stronger identity than a generic dashboard: an expressive X3D
organism makes an accumulating body of evidence approachable. Twelve domain
feathers invite exploration; the Atlas supplies inspectable records; the
four-stage teaching replay explains how an incident could become a reusable
guard. The optional Flyte subsystem proposes candidates, witnesses them,
consults a human when required and drafts a possible foldback.

The central opportunity is to make the evidence relationships as inspectable
as the feathers. A useful flywheel turn is an improvement taken up by a
separately identified consumer under a stated acceptance test. Animation,
graph growth, accepted geometry and an outbox draft are valuable intermediate
results, but they do not themselves establish that turn.

| Foundation | Why it matters |
| --- | --- |
| Pinned Atlas snapshot and eight recorded output digests | The UI can identify a particular body of historical material rather than make an unbounded claim about the live repositories. |
| Separate authored guard fixtures and synthetic teaching replay | An executed local check can be explained without portraying invented events as archived measurements. |
| Pure kernel and portable audit | Important evidence semantics can be tested without a browser, paid model or network. |
| Explicit domain inputs and outputs | The feathers already describe potential interfaces; they need not be mistaken for measured activity. |
| X3D clocks, interpolators, shared geometry and named sensors | The visual medium is inspectable and amenable to standard scene tooling. |
| Keeper records reuse as pending | A committed scene and a drafted note do not automatically inflate adoption. |
| Default zero model allowance | Local study and deterministic tests remain possible without an API call. |

The full edition, the standalone convenience export, the archived walkable
Atlas and the original cinematic are distinct products. Preserve their identity
and limitations in their own build records rather than treat a successful one
as acceptance of all four.

## Findings ranked by consequence

### G01 — P1: browser success can survive an initialization failure

Baseline `tools/browser_check.cjs` considers boot successful when the status
text no longer matches `/Opening|Loading/i`. The frontend's error status is
`Could not open the X3D loom`, which satisfies that predicate. The next check
only requires a browser scene with nonempty roots; it does not establish that
the intended observatory and required named nodes loaded.

A read-only reproduction of the exact status predicate returned `true` for
the error text. This does not establish that an archived screenshot was wrong;
it establishes that the acceptance predicate is too weak.

Require an explicit ready state, expected scene identity and required named
nodes. Pair a known-good page with a deliberately missing or malformed scene
and require the second page to fail. Record page, scene, manifest, runtime and
checker digests in a fresh receipt. If launch is blocked, write `not_run` rather
than leaving a historical green result as the apparent current outcome.

### G02 — P1: one grade collapses distinct evidence questions

Baseline `flyte/gobbler_flyte/organs/witness.py::grade` returns `Confirmed` for
a nonsynthetic signal when structural validation passes and `target_seen` is
true. `target_seen` only checks whether one or more filesystem paths exist.
A read-only execution of the baseline function reproduced this result.

Path existence can confirm a narrowly worded presence assertion. It cannot
confirm the signal's factual truth, the proposed technical behavior, a useful
integration or adoption. The broad grade travels into turn records and drafts,
where readers can reasonably overread its scope.

Retain separate facets: signal provenance, structural acceptance, target
presence, behavior test, rendering, human judgment and consumer adoption.
An overall project grade may summarize a specifically named claim, but should
never silently stand in for all of those facets. Existing `reused: false` and
`reuse pending` behavior is a useful boundary to preserve.

### G03 — P1: resource estimates need a strict arithmetic contract

Baseline `flyte/gobbler_flyte/budget.py` accepts numeric configuration and usage
without an explicit finite/nonnegative/type contract. Python JSON can decode
nonfinite constants unless strict loading is requested. Comparisons involving
NaN do not behave like ordinary budget bounds, and negative token usage would
reduce the ledger total. `check` also constructs a string proportional to the
caller-supplied character count solely to estimate tokens.

Test zero, negative, Boolean, noninteger and nonfinite values for prices,
allowances, token limits, usage and prompt length. Use bounded integer
arithmetic for prompt estimation and a declared monetary precision. Validate
ledger rows before summing them; corrupted usage should fail closed with a
specific diagnostic. A character-based token estimate remains an estimate,
not a provider-enforced hard billing cap. No paid call was needed or made for
this review.

### G04 — P1: checkpoint persistence does not make every side effect atomic

Baseline `runner.py::tick` uses a SQLite graph checkpointer, JSON memory,
append-only text logs, an outbox and a separate world store. Keeper appends to
the world before writing the draft and turn row. A failure between those
operations can leave partially completed work. Concurrent ticks can also read
the same cycle/memory state before either saves it.

This is a source-derived crash/concurrency risk, not a claim that the supplied
simulation suffered a duplicate. A durable graph checkpoint protects graph
state; filesystem and external side effects still require their own operation
identities and recovery rules.

Use one cycle operation key, reject overlapping local ticks, write mutable
memory by replacement and retain idempotent records for each side effect.
For the world append, require a durable operation key or a recoverable append
receipt from the world store; a local check-before-write alone cannot close a
crash window between two databases. Test failures after admission and before
checkpoint completion. Do not claim exactly-once external delivery until that
boundary is implemented and exercised.

### G05 — P1: the standalone builder depends on unchecked source rewrites

`gobbler-flyte/build_standalone.py` carefully checks several runtime-shim marker
counts, but performs frontend `str.replace` transformations without checking
that they matched. A harmless refactor of the loader, fetch options or controls
can leave the export making requests to nonexistent sibling resources.

The standalone also intentionally removes X3D text Shapes and omits audio,
while retaining accessible domain labels in HTML. That is a representation
projection with useful benefits and known losses, not byte or feature parity.

Use explicit loader hooks or checked marker contracts. Require each expected
replacement exactly once, reject remaining local resource channels that are
not intentionally retained, and test a source mutation that formerly bypassed
the replacement. Save an export loss inventory and a source-to-bundle manifest.
Native acceptance should include both HTTP and local-file use if both are
advertised; Web Crypto availability and asset loading can differ by context.

### G06 — P2: archived receipts need current identity before reuse

The baseline README reports browser measurements in its opening status but
later says local launch was restricted. `receipts/browser-observatory.json`
contains fifteen checks and browser/runtime observations but no source/tool
digests or run timestamp. The historical witness receipt names short instrument
revisions. `accrete_bridge.identity` similarly reports a checkout's short HEAD
without identifying local modifications or imported module bytes.

These records are useful historical observations. Their contents do not bind
the current changed source tree by themselves. A short commit label also does
not establish the bytes of a dirty checkout or an imported module resolved from
another path.

Keep historical records intact, add fresh source-bound receipts and state
which gates are current, stale or unexecuted. Record full repository revision,
dirty state, imported module origins and producer digests where practical.
Report hashes as local identity checks, not author authentication or empirical
truth. A new aggregate receipt should reference each child result and refuse
missing, stale or nonpassing required gates.

### G07 — P2: graph linkage and evidence strength are different relations

The kernel deliberately counts a failure mode as linked when a `paidForBy`,
`fixedByLaw` or `mentions` edge connects it with a law. It clearly documents
that broad criterion. The UI should preserve that explanation: a textual ID
join is not proof that the law repaired the incident. Likewise, an archived
quote match establishes a relationship to a source passage, not reproduction
of its physical, performance or learning claim.

Expose the exact predicate and evidence activity when selecting an edge. Keep
the archived grade, quote verification, local audit and later behavioral run
as separate records. Query views can offer both broad traceability and a
stronger, explicitly defined repair/reuse view without rewriting the archive.

### G08 — P2: replay validation needs explicit input and control bindings

`flywheel_kernel.py::replay_incident` already checks many useful constraints:
stage order, evidence kinds, guard membership, distinct target domains and
deduplicated `(guard, target, input hash)` reuse keys. Preserve that work.
The baseline nevertheless accepts an empty event list and returns `state=None`.
Several collection and reference fields assume well-shaped input.

An empty replay makes no false reuse promotion, but accepting it as a valid
protocol result weakens its input contract. Validate object shapes, nonempty
identities, collection types and event ownership before processing. Bind
positive and negative controls to actual input artifacts when the claim is
about discrimination. A declarative `verdict` field should not be mistaken for
the executed instrument that produced it. Tests need a nearby wrong-binding
case, not only a mutated numeric count.

### G09 — P2: async UI state needs a last-intent contract

The frontend's Atlas loader already shares one request and verifies bytes
before search; search also checks that the typed query is still current after
awaiting that request. Those are good patterns. However, baseline error
reporting mainly accumulates console/state strings, lifecycle cleanup is absent,
and selection, replay stage, pause clocks and loaded scene state are coupled
through module globals.

Treat each load or pending UI action as an operation with an active revision.
Dispose timers, callbacks and audio on page exit; preserve the user's last
selection while loading; report failures where the person acted; react to
reduced-motion changes as well as the initial preference. Test the actual
frontend contract with deferred completions. Such a harness validates
orchestration, not native X_ITE fields, pixel readability or physical device
accessibility.

### G10 — P2: visual motion needs a persistent semantic legend

The baseline correctly says that motion is illustrative and domain interfaces
are proposed. Nevertheless, a bright wheel spinning beside a large graph count
can imply live, quantified progress. The three-layer distinction should stay
visible while exploring: historical archive, current local checks, and imagined
future integration.

Use shape or line style as well as color for evidence status. Keep decorative
breathing/orbits on a different control from measured events. A reuse pulse
should require a selected adoption record, and its tooltip should reveal both
consumer and input identity. An evidence facet may be unknown even when every
object is beautifully rendered. A pause indicator should distinguish scene
clocks, audio and external collection; no single cadence number represents all
three.

## Architecture: four objects, four activities

The most useful common unit is a claim with a bounded input and a scoped
witness. Its representation should remain connected without collapsing those
identities.

| Object | Existing example | Associated activity | What the activity can establish |
| --- | --- | --- | --- |
| Source snapshot | Atlas JSON and source pins | Snapshot audit or quoted-row check | Local identity, reference integrity and defined quote matching |
| Candidate artifact | X3D fragment or authored fixture | Structural gate / semantic validator | The implemented structural conditions on those bytes |
| Analysis observation | Guard verdict, spend estimate, visual metric | Guard run, accounting calculation, browser check | The named result under the named instrument and conditions |
| Consumer artifact | Music-labelled fixture or external target | Local fixture consumption / actual integration | Precisely the tested consumption path; adoption needs its own evidence |

PROV-O provides a useful vocabulary for separating entities, activities and
agents. Keep a snapshot or receipt as an entity and the run that produced it as
an activity. SHACL can later express graph constraints; a shapes pass checks
those conditions and does not independently certify the meaning of every
claim. The accompanying `INTEGRATION-ONTOLOGY.json` is a vocabulary hook and
work register, not an OWL ontology, a complete JSON Schema or an executed
reasoner.

## Creative extension: let a person challenge the evidence

### 1. The Evidence Intervention Lab

Turn the four-stage replay into an interactive experiment. Hold the initial
incident fixed, then let the learner remove the positive control, change a
consumer input, duplicate a reuse event or stale the guard digest. Ask them to
predict whether promotion or momentum should change before applying it.

Use the same inspected X3D object in paired chambers. A relation bridge can
break at the exact failed condition, while the surface geometry remains valid.
The result should say which contract changed; the decorative ring should not
turn a Boolean pass into a general measure of scientific confidence.

The strongest “aha” is that two identical pictures can carry different evidence,
and two different files can satisfy the same stated invariant. At least one
mutant must be rejected while its nearby valid twin passes. Root implementation
and release notes should identify which experiments actually land in this pass.

### 2. The Receipt Prism

Give a selected record a small set of orthogonal facets: source identity,
structural validity, behavioral result, rendering, human judgment and adoption.
Illuminate each facet only from its own evidence activity. A valid X3D scene
can therefore show a lit structural face and an unmeasured rendering face.

Use a fixed, clearly labeled categorical arrangement; prism area or brightness
must not imply a calibrated scalar confidence. Click through to the exact
artifact hash and run. A filter such as “rendered but never judged” would make
the scarce human witness visible and actionable across music, heritage and
educational demos.

### 3. The Two-Consumer Bridge

Show one repaired technique consumed by two independently named examples:
for instance, a shader URL guard used by a game scene and a music scene. Keep
the authored local example visibly distinct from an external repository
adoption. An identical retry should land on the same bridge rather than create
another unit of momentum.

For cross-domain scientific work, replace the shader fixture with a transform
or units contract. A Blender scene, a STEM visualization and a chess position
can all reuse the contract while testing different invariants. This turns an
abstract network into a practical explanation of what is preserved, what is
lost and who actually consumed the result.

## Taxonomy for the wider X3D family

| Axis | Categories | Heuristic |
| --- | --- | --- |
| Subject | Scene, source, claim, incident, guard, run, consumer, learning task | Name the object before assigning a grade. |
| Origin | Historical archive, authored fixture, synthetic teaching record, live observation | Origin and execution are separate facets. |
| Activity | Generate, normalize, validate, render, measure, judge, integrate, adopt | Completion of one activity does not imply completion of another. |
| Evidence facet | Identity, structure, behavior, appearance, physical agreement, learning, adoption | A gate must name the facet it tests. |
| Execution | Pass, fail, error, not run | Missing execution must not be encoded as false success. |
| Freshness | Current for exact inputs, stale, unknown | A successful historical run may remain historically true while being stale for new inputs. |
| Representation | X3D, browser state, JSON observation, RDF graph, raster, audio | Record each conversion's scope and losses. |
| Readiness | Implemented, locally checked, awaiting external acceptance, proposed, blocked | Do not count a roadmap item as a capability. |

## Bounded integration register

The identifiers below also occur in the machine-readable work register. Every
row is proposed future work unless an accompanying implementation note says
otherwise; these are acceptance conditions, not fresh result claims.

| ID | Priority | Work | Acceptance evidence |
| --- | --- | --- | --- |
| W01 | P1 | Native observatory and standalone acceptance | Same pinned runtime; explicit ready/expected-node checks; negative loading twin; current input/tool hashes; screenshots reviewed for layout and meaning. |
| W02 | P1 | Crash-safe cycle side effects | Inject failure at each admission/draft/checkpoint boundary; resume without duplicate world admission, turn, spend or external delivery. |
| W03 | P1 | Budget reservations and token-bound accounting | Finite validated amounts; provider token counting or conservative declared bound; overlapping-call and crash tests; estimated versus billed costs kept separate. |
| W04 | P1 | Faceted evidence schema | A deliberately unrendered but structurally valid scene has the correct independent statuses; no path-existence promotion of unrelated claims. |
| W05 | P2 | MathLab counterfactual consumer | One mathematical invariant, exact reference/tolerance, valid and defective pair; learner prediction and observed result linked to source bytes. |
| W06 | P2 | STEM units/transform consumer | Analytical or measured reference, units/frame convention, error envelope, independently checked plotted and exported geometry. |
| W07 | P2 | Chess relationship consumer | A pinned-attack counterexample with independent legal/attack witnesses; generic scene validity kept separate from chess-rule correctness. |
| W08 | P2 | Blender IO consumer | Full import/export settings; axis/scale/material/text loss inventory; measured object identities and geometry; actual round trip if advertised. |
| W09 | P2 | ML held-out evaluation bridge | Frozen dataset and split, model/instrument pins, duplicate/near-duplicate policy, task-specific metrics and errors; no training improvement inferred from corpus growth. |
| W10 | P2 | Curator's desk for visual/audio judgment | Explicit consented task; blind comparison where useful; device/context and inter-rater agreement recorded; no model vote relabeled human judgment. |
| W11 | P2 | Measured graph/render scaling | Fixed 100/1,000/10,000-record workloads; cold/warm parse, query time, memory, frame percentiles and queue age on named hardware. |
| W12 | P2 | External adoption receipt | Separate consumer commit and artifact, explicit acceptance activity and result, retry deduplication and revocation/supersession handling. |

The MathLab, STEM and chess connections are proposed handoffs grounded in the
methods of those projects; this report does not claim to have modified their
repositories. The public Gobbler work should not absorb private Blender
training corpora or private workflow records by implication.

## Deep heuristics worth folding back

1. **Put the tested claim in the receipt.** `Confirmed` without a subject and
   acceptance question is too easy to overread.
2. **Let counterexamples teach the boundary.** The closest useful mutant often
   explains a contract better than a larger successful scene.
3. **Bind a result to the input it actually used.** The chess pre-move score bug
   and a stale scientific plot are the same architectural family of error.
4. **Save raw and normalized representations.** A canonical fragment is useful,
   but the normalization activity and original bytes explain what changed.
5. **Deduplicate meaning, not animation.** A repeated retry can be another
   operational event without becoming another independent adoption.
6. **Separate evidence grade from evidence coverage.** More facets tested is
   different from stronger support for one facet.
7. **Treat stale UI as a false explanation.** Clearing old geometry and
   invalidating pending work are semantic obligations, not cosmetic cleanup.
8. **Measure the expensive uncertainty next.** After structure is reliable,
   another structural count may add less information than one native render,
   physical measurement or independent human judgment.
9. **A hash is an identity mechanism.** Authentication, valid inference and
   empirical correctness need additional evidence.
10. **Keep the organism expressive.** The Gobbler can be joyful and abstract
    while every quantitative visual channel remains modest and inspectable.

## Primary references and source-reading boundary

- [W3C PROV-O](https://www.w3.org/TR/prov-o/): provenance vocabulary for
  distinct entities, activities and agents; used here as a modeling hook.
- [W3C SHACL](https://www.w3.org/TR/shacl/): constraints over RDF data graphs;
  suggested for future graph-contract validation, not executed in this review.
- [X_ITE Browser Services](https://create3000.github.io/x_ite/reference/browser-services/):
  documented browser/scene operations and identity; current docs do not replace
  acceptance of this repository's pinned runtime.
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence):
  checkpoint and store scope; external side-effect recovery remains an
  application concern.
- Local baseline sources: `flywheel-review/atlas/flywheel_kernel.py`,
  `snapshot_audit.py`, `shader_guard.py`, `gobbler-flyte/observatory.js`,
  `build_standalone.py`, `tools/browser_check.cjs`, and Flyte's `runner.py`,
  `budget.py`, `accrete_bridge.py`, `organs/witness.py` and `organs/keeper.py`.

This baseline review ran bounded read-only function/predicate reproductions;
it did not run a paid model, send messages, publish a branch, reproduce the
archived scientific claims or certify a native browser result. Final release
receipts own the exact scope of newly executed acceptance checks.
