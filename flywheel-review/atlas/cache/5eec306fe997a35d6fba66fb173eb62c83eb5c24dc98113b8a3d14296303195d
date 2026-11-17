# 23. Traceability: a quote beside every value, and the lineage stack around it

> **Say it:** Make whoever writes a value copy the exact words it came from, and let plain code answer three questions (is the quote in the source, is the value in the quote, where is it); then record the answer in the scene's own hash chain, recompute it on audit, and say out loud what it cannot show: that the quote is the right place, that the value is true, or who wrote the record. **[C]**

| field | value |
|---|---|
| chapter code | `TRC` |
| prerequisites | [01 The tether](01-the-tether.md) for the thesis; [03 Validator and gates](03-validator-and-gates.md) for the exact stages a verdict sits next to; [22 Typed judgments](22-typed-judgments-jev.md) for why a model's answer may only flag |
| after this you can | (1) write a claim as `{field, value, quote, source}` and read the four verdicts and the grade each one allows; (2) say why "first hit" fails on a scene and what picks the node instead; (3) record a trace in a scene's `x3dprov` chain and audit it, and say which edits the audit catches and which no hash can; (4) place any new number in the seven-layer lineage stack and name the layer that is missing; (5) test a verifier by someone who has not seen its code |
| sources read | `x3d.ml@305fd60` (`src/x3dtrace.py`, `src/x3dprov_trace.py`, `docs/TRACE.md`, `docs/TRACE-REVIEW.md`, `measure/`); `x3d_mcp@e55375f` (`src/tools/scene_evidence.py`, `docs/scene-evidence.md`); `x3d.loom@be7c481` (`x3d.s1/README.md`, `x3d.s1/receipts/evidence-2026-11-16.json`); `x3d-blender-io@044bea3` (`source/lineage.py`); `x3d.castle@5b13f70` (`docs/ledger/`); the article "How I Added Traceability in Structured Data Extraction with AI" (Medium, November 2026, by Umair Ali Khan) and the GAIK toolkit (MIT, commit 394a94b), read as saved pages and source, run for the vectors |
| instruments used | `x3dtrace` engine sha256 prefix `dcba70d739007c0d`, Python 3.13.18, 4 vCPU x86_64 Linux container; `x3d_mcp@e55375f` tests with Python 3.13.18; Node 22 for the browser port vectors; no model API was called, no GPU, nothing timed on a renderer |

The method is simple to state and easy to get subtly wrong. A writer (a model, a tool, a person) returns each value together with a short exact quote of the place it read it from. Code then finds the quote in the source, checks that the value is inside the quote, and says where. No model is asked to judge. This chapter teaches the method as it was built for X3D, shows what a scene changes about it, measures it on the public corpus, and records the 49 defects that an independent reviewer and later reading found in the first build. It ends with the lineage stack the method is one layer of.

---

## 1. The map

```text
   source text (prompt, spec, log, the scene itself)          scene (X3D)
        |                                                         |
        |  writer copies the exact words beside each value        |
        v                                                         v
   claim = { field, value, quote, source }  ---- BIND ---->  field -> node -> attribute
        |
        |  FIND     is the quote an unbroken run of whole words in the source?
        |  COMPARE  is the value inside the quote (units, vectors, colours, words)?
        |  LOCATE   span, line and column, node path, DEF, world box
        v
   item = verdict + status + value_status + derivation + locus + selectors
        |
        v
   trace step in the scene's own <head> hash chain (x3dprov)  ---->  audit: recompute items
        |
        +--> PROV-O Quotation    +--> OpenLineage column lineage     [section 6]
```

| in scope | out of scope |
|---|---|
| the quote method as built in `x3dtrace`; its X3D differences; its record and audit; measured behaviour on the public corpus; the review that broke it; the lineage stack and where each layer lives | a model writing the quotes (not measured, needs model calls); signing and anchoring (not built); claims about world extents; PDF page boxes (the report keeps GAIK's field names; nothing here fills them) |

| verdict | meaning | the highest grade a claim may carry |
|---|---|---|
| `verified` | quote found, value inside it | [C] |
| `reworded` | value is a close reading (unit, colour name, number word) | [L] |
| `check` | quote not found, or value not in it | [S] |
| `unchecked` | no quote, or the source cannot be read here | [L] with a quote, [S] without |

Read next: deeper, [22 Typed judgments](22-typed-judgments-jev.md) for the rule that a model's answer never turns a witness green; wider, [G Claim ledger](G-claims-ledger.md) for the same method applied to this base's own numbers.

---

## 2. The method in six lines

1. **Copy, do not summarise.** The writer returns the value and, beside it, the exact words it read it from. A paraphrase is `check`: that is a rule, not a defect.
2. **FIND.** The quote must be an unbroken run of whole tokens in the named source. Punctuation, case and spacing are ignored in prose; a number keeps its sign, decimal point and exponent (`-1.5` is not `1 5`, `1e-5` is one number); identifiers keep their case.
3. **COMPARE.** The value must be in the quote. Numbers compare as numbers within a tolerance (`1e-6` by default); vectors compare per component, in order; a conversion is accepted only when the quote itself carries the evidence (`90 degrees` for 1.5708 rad, `50 %` for 0.5, `2 ft` for 0.6096 m, `#ff8000`, `red`, `seven`).
4. **LOCATE.** Character span, line and column; for a scene also the node path, the DEF path and a world-space box. The record also carries W3C Web Annotation selectors (TextQuote with prefix and suffix, TextPosition, XPath).
5. **Verdict and grade cap.** `verified`, `reworded`, `check`, `unchecked` (table in section 1). The cap is a ceiling: it says what the evidence allows, not what the claim deserves.
6. **Coverage.** The share of the scene's value-bearing attributes that came with a quote is `coverage`; the share whose quote was verified is `verified_coverage`, the number to trust, because a fabricated quote still counts as cited.

The article's insight is that this turns "the model said so" into a testable statement with a location, and that the test needs no model. What it does not do is as important: a verified quote proves the words are there and hold the value, not that they are the right words, that the source is right, or that the scene was built from them.

---

## 3. What a scene changes

| in the article (a PDF) | in an X3D scene | what the engine does |
|---|---|---|
| a value sits at a page position | a value is an attribute of a node | records an XPath 1.0 `field` (`/X3D/Scene/Transform[@DEF='Pier3']/@rotation`) and the DEF path |
| a box on the page | an axis-aligned box in world space, after every ancestor Transform, one per `USE` instance | `aabb_e6` in integer millionths of a scene unit, naming the ancestor that owns it |
| a repeated quote is occasional | the same attribute text appears on many nodes | the field's node picks the occurrence, not the first hit |
| numbers are scalars | vectors, colours in 0..1, axis-angle rotations | compared per component in order; a permuted vector is `check` |
| units are in the text | metres, radians, kilograms and newtons unless a `UNIT` statement says otherwise | a conversion only when the quote carries the unit; the caller passes the scene's `UNIT` as `length_scale` |
| one document | prompt, spec, `Inline` files, logs, the scene | several named sources; a quote found elsewhere than cited is status `moved` |
| source and answer differ | the scene can be the source of a quote about itself | both directions are stored the same way |
| a scan has no text | a texture or a `.glb` payload has no text | kind `binary`, verdict `unchecked` |

A worked case. The prompt says "6 m tall on a 0.4 m x 0.4 m footing". The scene stores `<Box size="0.4 2 0.4"/>` inside a Transform that scales y by 3. No attribute holds the number 6: the value is emergent. The engine will `verify` the footing, will not verify "6", and records the world box of the pier (0.4 x 6 x 0.4) so a later claim kind could check it. That claim kind is not built (section 9).

Eight facts the engine encodes, each with tests in `tests/test_x3dtrace.py`: the sign belongs to the number; order is part of a vector; an exponent is one number; DEF names are case-sensitive; an axis-angle has four numbers, and "90 degrees about the vertical axis" supplies the axis and the unit for all four; a scene's `UNIT` statement is read, but the caller must pass it as the policy's `length_scale` (a documented gap); a leading zero marks an identifier (`007` is not "Part 7"); and, added late, **a version is not a date**. `16.7.0` was once read as day, month and year, so `version = "7.16.0"` verified it (section 7, BUG-47).

---

## 4. What the corpus says

Corpus: every tracked `.x3d` file of seven public repositories (six contribute a unique scene; x3d.lab contributes none), de-duplicated by sha256: 1,614 files, 182 duplicates, 1,379 scenes parsed, 47 that do not parse, 6 that are not XML; 248,929 elements, 364,127 attributes, 100,392 value-bearing attributes. One author's repositories, many scenes machine-generated: prevalence figures are this corpus's, not X3D's. [C]

```text
 quote written as ...                       repeats inside its own scene
 -----------------------------------------------------------------------------
 value only            "1 1 1"              |##############################  57.6%
 attr="value"                               |######################          43.7%
 attr="value" + 3 neighbouring tokens       |###########                     22.4%
 whole start tag                            |############                    23.7%
 start tag + 3 tokens                       |########                        15.9%
```

| question | answer | instrument |
|---|---|---|
| repeated `attr="value"` quotes where first-hit lands on the wrong node | 37,797 of 43,903 (86.1%) | `measure/m_corpus.py`, engine `dcba70d7`, Python 3.13.18 |
| same, choosing the occurrence inside the node the claim's `field` names | 1 of 43,903 (a hand-made probe with a namespaced duplicate attribute on one node) | same |
| shapes that get a world box | 28,465 of 32,608 (87.3%); Text, Extrusion and NURBS have none | same |
| scenes whose shapes are all boxed | 878 of 1,142 | same |
| value attributes of model-written scenes for which a phrase of the prompt could be quoted (lexical matcher: 134 verified, 260 reworded) | 394 of 8,250 (4.78%) over 201 recorded runs | `measure/m_grounding.py`, engine `dcba70d7` |

The two halves of the first finding matter together: a first-hit rule, which is what the article's method and GAIK use, is wrong on most repeated scene quotes, and choosing by the field's node makes it right on all but a contrived one. The last row says that at most about one value in twenty of a model-written scene can be backed by a quote from its prompt. It is an upper bound on quoting, not a measure of grounding: the matcher is lexical, so a value that follows from the prompt without its words counts as unsupported, and a loose match counts as supported. It says what lineage must cover for the rest: a value nobody quoted needs a different class (chosen, derived, default), not a missing quote. Graded [L] for the reading, [C] for the count.

---

## 5. The record and the audit

`trace_claims` appends one `trace` step to the scene's `x3dprov` chain (a hash chain kept in `<head><meta>`), then a `summary` step so the trace has a successor. Everything hashed holds only text, integers and booleans, so Python and JavaScript hash alike: floats travel as their shortest text, boxes as integer micro-units, coverage as parts per million, items inline up to 64 KiB and otherwise in a sidecar named by the report hash.

`audit_trace` runs `verify()`, then for each trace step: the scene is unchanged by it, items hash to `report_sha256`, claims to `claims_sha256`, every supplied source still hashes to its recorded value, no field is traced twice, each XPath field resolves to one node whose text equals the value, and the whole check is **re-run** and compared item by item. Because the verdicts are recomputable, a flipped verdict is caught even in the last step, where a bare hash chain cannot see it.

Tamper measurement: 40 scenes sampled at random (seed 20261116), up to 25 claims each, 656 claims; an attack is caught when the audit status is not `verified`.

| edit | attempts | caught |
|---|---|---|
| item edited in the sidecar | 1,120 | 1,120 |
| same, trace step patched to match | 1,120 | 1,120 |
| item edited inline | 320 | 320 |
| claim edited; claim edited and re-hashed | 155; 155 | 155; 155 |
| forged trace step, later step untouched | 80 | 80 |
| scene edited | 319 | 319 |
| **consistent forgery, last step, unsealed** | 80 | **0** |
| **trace and later steps re-chained** | 80 | **0** |

The two zero rows are the stated limit. Rewriting the claims, the report and every later step consistently produces a different but internally honest trace, and no hash-only scheme can tell. Only something outside the chain can: a signature, a commit, a C2PA assertion. That is layer 7 of the stack (section 6) and it is not built. Sealing (the default) puts a `summary` step after the trace so the trace is not the last link; an unsealed trace whose last step is rewritten consistently falls in the first zero row. Cost per claim over the 656 claims: 0.35 ms to check, 0.72 ms to check and record, 0.59 ms to audit, on one core.

---

## 6. The lineage stack, and where each layer lives

```text
  layer       what it answers                       where it lives
  ------------------------------------------------------------------------------------
  7 anchor    who and when, outside the chain       NOT BUILT (signature, commit, C2PA)
  6 views     the facts in a standard form          x3d.ml: PROV-O, OpenLineage
  5 ledger    what is claimed, with its grade       x3d_mcp: claim_append; x3d.docs: G
  4 evidence  is the quote there, does it hold it   x3d.ml: x3dtrace; x3d_mcp: scene_evidence
  3 chain     what ran on this scene, in order      x3d.ml: x3dprov
  2 receipts  the run card of one tool run          x3d.lab run cards; x3d.loom receipts
  1 bytes     these exact bytes                     sha256 of every file
```

| repository | what was added | what it shows |
|---|---|---|
| x3d.ml | the engine, the `trace` step and audit, PROV-O and OpenLineage views, the independent test suite, the measurements | layers 3 to 6, and the defect register of section 7 |
| x3d_mcp | `scene_evidence`: claims against sources and against the scene itself (BIND), answer with offsets and node handles, never the quote | the method as a tool a model can call without being handed the document's own words |
| x3d-blender-io | `source/lineage.py`: per DEF'd attribute, the Blender datablock, the conversions applied, the line and column, and a verdict from an independent recompute of the emitter's arithmetic | lineage by construction: the exporter knows where each number came from, so the check recomputes instead of quoting |
| x3d.castle | `docs/ledger/`: nine numbers the docs state, each tied to the words that state it and to the file that holds it | its first run found the README saying the exporter is about 1,700 lines of Pascal and another doc about 2,500, where the file has 2,412 |
| x3d.loom | an evidence check in `x3d.s1` (stdlib, no model call) with planted-claim measurement | a false-verify rate with a rule-of-three bound, and one blind spot reported (a paraphrase of an instruction verifies as a quote) |
| x3d.docs | the claim ledger of Appendix G and this chapter's own ledger | the method applied to this base |

Two of these are different in kind. The exporter and the music project already have lineage by construction (a pointer from every written value to the datablock or score token it came from): there a quote is unnecessary and the check is a recompute. A quote is for the values nobody can recompute, which are the ones a model or a person typed.

---

## 7. The review: how to find what the author cannot see

The first build of the engine passed its author's tests. A second reviewer was given the engine's stated intent (docstring, method description, behaviour notes on GAIK) and **not its code**, and wrote 1,204 tests from that. The first run found 43 defects (138 expected-failure tests). They were then fixed or recorded; later reading found six more. The register is `docs/TRACE-REVIEW.md` in x3d.ml; the repro for each is in `tests/test_x3dtrace.py`.

| severity | example | state |
|---|---|---|
| HIGH | the opposite rotation is `verified` (the axis flipped, the same angle) | fixed |
| HIGH | nested USE doubling makes the world-box walk exponential: 17 levels took 13 s | fixed |
| HIGH | a quote number beyond float range (`1e999`) raises in the colour comparison, and a non-finite scene attribute raises in `check_claims` | fixed |
| HIGH | unit conflicts are skipped for vector components (a 2 ft cube verifies `2 2 2` in a metre scene) | fixed |
| HIGH | a dotted version is read as a date: `16.7.0` is verified by `version = "7.16.0"` (BUG-47) | fixed |
| MEDIUM | a field below a DEF (`//*[@DEF='BuoyC']/Shape/Sphere/@radius`) did not pick the node, so the first of three equal quotes was used (BUG-49) | fixed |
| HIGH | a vector is verified from numbers scattered through prose: `1 2 3` by "1 apple, 2 pears and then 3 cows" (BUG-45) | **open** |
| MEDIUM | coverage counts a claim only when its `field` is the inventory XPath (BUG-50) | **open** |
| LOW | a leading `v` on a version reads as a mismatch (BUG-48); a stray number blocks zero-fill (BUG-46) | **open** |

Eight items are open and each has an expected-failure test, so a later fix shows as a pass. Four are decisions or low-severity gaps the engine's author left on purpose (a shorter vector against a longer attribute; `round_to_printed` direction; trusting the recorded policy on replay; the cost of `suggest_claims`). The lesson is not the count. It is that **a verifier is itself a claim**: it needs a reviewer who has not seen its code, a conformance file that says where it differs from the method it adapts (55 of 135 rows differ on purpose, each with a reason), and a place to keep the failures that remain.

---

## 8. Using it

| step | command or call | what comes back |
|---|---|---|
| list what could carry a quote | `python3 src/x3dtrace.py inventory scene.x3d` | every value-bearing attribute with its XPath |
| check claims against sources | `python3 src/x3dtrace.py check claims.json --source spec=spec.txt` | one line per claim, exit 1 if any is `check` or `unchecked` |
| record and audit | `trace_claims(xml, claims, {"spec": text})`, `audit_trace(xml, {"spec": text}, scene=True)` | `verified`, `stale` (scene edited), or `broken-chain` |
| from a model, through MCP | `scene_evidence(content, claims, sources, expect="inventory")` | verdicts, offsets, node handles, coverage; the quote is never repeated |
| in a browser | `js/x3dtrace.js` | FIND and COMPARE for one claim, 1,767 of 1,767 test rows agree with the Python engine |

Write `field` as the inventory XPath (or `DEF@attr`) so a repeated quote lands on the right node and coverage counts the claim. Use the `strict` policy (or only `ambiguous_quote_is_check`) when a repeated quote with no prefix, suffix or field must fail.

---

## 9. What is missing, ranked

1. **Claims about emergent values** ("6 m tall"): a claim kind whose field is a world extent, checked against the recorded box. The box data is already stored per item.
2. **A gap rule for vectors in prose** (BUG-45): components spread over prose may reach `reworded`, not `verified`.
3. **A class for every unquoted value**: specified, chosen, derived, default. Only 4.78% of model-written values have a prompt phrase to quote, so "no quote" must become an answer.
4. **An anchor** (layer 7): a signature, a commit or a C2PA assertion, so the consistent forgery is no longer undetectable.
5. **A model writing the quotes**, measured: how often does it copy exactly? This needs model calls; it has not been run.

---

## Heuristics

| ID | Rule | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-TRC-1 | Make the writer copy the exact words beside each value, and check them in code; never ask a model whether a quote is right. | C | 0 of 806 wrong numbers, 0 of 5,357 words outside the quote, 0 of 5,808 fabricated quotes verified; 5,782 of 5,808 true claims verified | `x3d.loom@be7c481` `tools/evidence_measure.py`, Python 3.13.18, 501 scenes |
| H-TRC-2 | Read `verified` as "the words are there and hold the value", never as "true" or "the right place". | C | 501 of 501 paraphrased instruction-like strings verified as quotes; a repeated quote verifies at the first hit unless a node or context picks one | `x3d.loom@be7c481` receipt; `x3d.ml@305fd60` tests |
| H-TRC-3 | Pick the occurrence by the field's node; first hit is wrong on most repeated scene quotes. | C | 37,797 of 43,903 repeated `attr="value"` quotes (86.1%) | `x3d.ml@305fd60` `measure/m_corpus.py` |
| H-TRC-4 | Write `field` as the inventory XPath or `DEF@attr`; read `occurrences` and `disambiguated_by` on every item. | C | `//*[@DEF=..]/Shape/Sphere/@radius` once used the first of three equal quotes (BUG-49); coverage counts the inventory form only (BUG-50, open) | `x3d.ml@305fd60` tests, drill D-TRC-3 |
| H-TRC-5 | Accept a unit or colour conversion only when the quote carries the evidence for it, and record which conversion was applied. | C | `derivation` lists `deg2rad`, `axis`, `colorname`; a 2 ft cube no longer verifies `2 2 2` | `x3d.ml@305fd60` tests |
| H-TRC-6 | Compare a vector per component, in order, and treat a vector read from prose as weaker than one copied from a scene attribute. | C | BUG-3 fixed (the opposite rotation); BUG-10 open in part (`2 2` accepted for `2 2 2`); BUG-45 open: `1 2 3` verified by "1 apple, 2 pears and then 3 cows" | `x3d.ml@305fd60` tests, drill D-TRC-4 |
| H-TRC-7 | Report `verified_coverage`, not `coverage`. | C | 4 claims on a 4-attribute scene: coverage 1.0, verified coverage 0.5 | drill D-TRC-6 |
| H-TRC-8 | Seal the trace and audit by recomputing the check, not by comparing hashes alone. | C | 7 of 9 edit families caught 100% (3,269 of 3,269 attempts); the audit re-runs the verdicts | `x3d.ml@305fd60` `measure/m_tamper.py`, seed 20261116 |
| H-TRC-9 | Say that a hash chain cannot show who wrote a consistent rewrite; put an anchor outside the chain before calling a record tamper-proof. | C | 0 of 160 consistent forgeries caught | same |
| H-TRC-10 | Never read a version as a date; compare it as text. | C | `16.7.0` was verified by `7.16.0`, `5.8.4` by `4.8.5`, `2.6.4` by `4.6.2` (BUG-47, fixed) | `x3d.ml@305fd60` tests, drill D-TRC-4 |
| H-TRC-11 | Give a model the offsets and node handles of a check, not the quotes: the answer must not carry the document's own words. | C | `scene_evidence` repeats no quote or value unless `text="quoted"`; hostile scene, quote and field tests pass | `x3d_mcp@e55375f` `tests/test_scene_evidence.py`, 36 tests |
| H-TRC-12 | Have the verifier reviewed by someone who has not seen its code, and keep the open failures as expected-failure tests. | C | 43 defects in the first build from 1,204 tests; 8 still open, each with a test that passes when fixed | `x3d.ml@305fd60` `docs/TRACE-REVIEW.md` |
| H-TRC-13 | Where the exporter knows where a number came from, record the datablock and the conversion and recompute; use a quote only for values nobody can recompute. | L | a mutation test shows that an emitter that skips the sRGB step is caught by the recompute | `x3d-blender-io@044bea3` `tests/test_lineage.py`, 15 pure tests, read, not rerun here |
| H-TRC-14 | Measure a verifier's false-verify rate with planted claims of known truth and quote an upper bound, not only a zero. | C | each zero row carries a rule-of-three upper bound in the receipt | `x3d.loom@be7c481` `x3d.s1/receipts/evidence-2026-11-16.json` |

---

## Drills

Each drill needs a checkout of `x3d.ml` (the engine is standard library only; `D-TRC-5` also needs `lxml`). Run Python as `python3 -I`.

### D-TRC-1 The grade a verdict allows
- **Level:** L1
- **Task:** Which grade does the engine allow a `verified`, a `reworded`, a `check` and an `unchecked` item without a quote?
- **Verify:** `python3 -I -c "import sys;sys.path.insert(0,'src');import x3dtrace as T;print(T.grade_cap('verified',True),T.grade_cap('reworded',True),T.grade_cap('check',True),T.grade_cap('unchecked',False))"`
- **Answer:** Confirmed, Likely, Suspected, Suspected.
- **Checked:** 2026-11-16 `x3dtrace` dcba70d7, Python 3.13.18

### D-TRC-2 Four claims, two wrong
- **Level:** L2
- **Task:** Save the spec as `spec.txt` and the four claims as `claims.json` (the fields are inventory XPaths). Run the check and say why claims 3 and 4 fail. The scene is shown so you can see what the fields point at; `python3 -I src/x3dtrace.py inventory scene.x3d` prints the same four fields.
- **Verify:** `python3 -I src/x3dtrace.py check claims.json --source spec=spec.txt` (exit status 1)

```xml
<X3D profile="Immersive" version="4.0"><Scene>
<Transform DEF="Pier3" rotation="0 1 0 1.5708"><Shape><Box size="0.4 2 0.4"/></Shape></Transform>
<Transform DEF="Deck" translation="0 2 0"><Shape><Box size="6 0.2 2"/></Shape></Transform>
</Scene></X3D>
```

`spec.txt`: `Pier 3 is a box 0.4 m x 2 m x 0.4 m, turned 90 degrees about the vertical axis.` and `The deck is 6 m long and 2 m wide.`

```json
[{"field":"/X3D/Scene/Transform[@DEF='Pier3']/@rotation","value":"0 1 0 1.5708","quote":"turned 90 degrees about the vertical axis","source":"spec"},
 {"field":"/X3D/Scene/Transform[@DEF='Pier3']/Shape/Box/@size","value":"0.4 2 0.4","quote":"0.4 m x 2 m x 0.4 m","source":"spec"},
 {"field":"/X3D/Scene/Transform[@DEF='Deck']/Shape/Box/@size","value":"6 0.2 2","quote":"6 m long and 2 m wide","source":"spec"},
 {"field":"/X3D/Scene/Transform[@DEF='Deck']/@translation","value":"0 2 0","quote":"the deck sits two metres up","source":"spec"}]
```

- **Answer:** 2 verified, 2 check. Claim 1 is verified through `axis:vertical` and `deg2rad`. Claim 3 is `check`: the quote holds 6 and 2 but not 0.2, so the value is not in the quote. Claim 4 is `check`: that sentence is not in the spec.
- **Checked:** 2026-11-16 `x3dtrace` dcba70d7, Python 3.13.18

### D-TRC-3 First hit or the field's node
- **Level:** L2
- **Task:** A scene holds three buoys, `BuoyA`, `BuoyB`, `BuoyC`, each with `<Sphere radius="0.5"/>` and `translation` 0, 3 and 6 on x. Check the quote `radius="0.5"` for the claim whose field is `/X3D/Scene/Transform[@DEF='BuoyC']/Shape/Sphere/@radius`, with the scene as the source. On which line does the quote land, how many occurrences does the item report, and what does `disambiguated_by` say? Repeat with the field `x`.
- **Verify:** `check_claims([claim], [Source('scene', text, 'x3d')])` and print `occurrences`, `disambiguated_by`, `locus['line']`.
- **Answer:** With the BuoyC field: line 4 (BuoyC), 3 occurrences, `disambiguated_by` `field`. With `x`: line 2 (BuoyA), 3 occurrences, nothing disambiguated, still `verified`: that is first hit. Under the strict policy the second is `check`.
- **Checked:** 2026-11-16 `x3dtrace` dcba70d7, Python 3.13.18

### D-TRC-4 Break the verifier, then extend it
- **Level:** L3
- **Task:** (a) Check the value `16.7.0` against `version = "7.16.0"`, `X_ITE 16.7.0` and `v16.7.0`. (b) Check the vector `1 2 3` against `1 apple, 2 pears and then 3 cows`, `1 x 2 x 3` and `(1, 2, 3)`. (c) Sketch the rule that fixes the open one without breaking the two that must stay `verified`, and say which verdict the scattered case should reach.
- **Verify:** `check_claims([{"field":"f","value":V,"quote":Q,"source":"s"}], [Source("s", Q, "text")])` for each pair; `tests/test_x3dtrace.py -k scattered` holds the open test.
- **Answer:** (a) `check`, `verified`, `check` (the leading `v` is BUG-48, open). (b) `verified` for all three: the first is BUG-45, open. (c) Components may be separated only by whitespace, commas, `x`, `by`, `and` and a unit word; anything else caps the item at `reworded`, because a value assembled from scattered numbers is Likely at best. The rule must keep `5 m east and 7 m north` for `5 0 7` at `reworded`.
- **Checked:** 2026-11-16 `x3dtrace` dcba70d7, Python 3.13.18

### D-TRC-5 Edit the record
- **Level:** L2
- **Task:** Take the Pier3 scene of D-TRC-2 with a `<head><meta name="title" content="pier"/></head>` before the `<Scene>`, add a `generate` step with `add_step`, trace the first claim with `trace_claims`, then audit it three ways: as written, with the quote edited in the stored step, and with the scene's `rotation` edited. What status does each audit give?
- **Verify:** `T.audit_trace(xml, {"spec": spec}, scene=True)["status"]` with `x3dprov_trace as T` and `x3dprov as P` from `src/`.
- **Answer:** `verified`, `broken-chain`, `stale`.
- **Checked:** 2026-11-16 `x3dtrace` dcba70d7, `x3dprov` of `x3d.ml@305fd60`, Python 3.13.18, lxml 6

### D-TRC-6 Coverage that lies
- **Level:** L1
- **Task:** For D-TRC-2, pass the scene's inventory as `expected_fields`. What are `coverage` and `verified_coverage`? Then write the Pier3 claims with `//*[@DEF='Pier3']/...` fields and read both again. Which number would have misled you?
- **Verify:** `check_claims(claims, sources, TracePolicy(), [r['field'] for r in inventory(scene)])` and print `rep.coverage`, `rep.verified_coverage`.
- **Answer:** 1.0 and 0.5: all four attributes came with a quote, two were verified. With the DEF form for the two Pier3 claims: 0.5 and 0.0, because the DEF form is not counted (BUG-50, open). `coverage` alone would have said everything was cited.
- **Checked:** 2026-11-16 `x3dtrace` dcba70d7, Python 3.13.18

---

## Honest limits

* **[C]** No model was called. Nothing here measures how often a model copies a quote exactly; that experiment needs model calls and has not been run.
* **[C]** The corpus is one author's seven repositories; many scenes are machine-generated. Prevalence figures describe it, not X3D.
* **[C]** The record is unsigned. The 0 of 160 is the limit of any hash-only scheme, not a bug in this one.
* **[C]** `verified` is a statement about words. A source can be wrong and a quote can be the wrong sentence; a repeated quote is resolved only by a field, a prefix, a suffix or a line.
* **[C]** Eight review findings are open (section 7). The two that can raise a grade wrongly are BUG-45 (a vector from scattered numbers) and the choice, in BUG-10 and BUG-20, to accept a shorter vector and a rounded value.
* **[C]** The browser port covers FIND, COMPARE and the choice by prefix, suffix and line; it has no scene index, so it takes the first occurrence when only a field would choose, and HTML5-only named entities are not decoded. All 1,767 vector rows agree; none of them depends on the field choice, which the port's own fuzz run does hit in about 1.1% of its rows.
* **[L]** The grounding figure (4.78%) is an upper bound on how many values of 201 recorded model runs a verbatim prompt quote could back, found by a lexical matcher. It is not a measure of grounding in the wide sense: a value that follows from the prompt without its words counts as unsupported.
* **[L]** GAIK was read and run for its vectors at commit 394a94b; the implementation here is independent. Nothing was sent upstream.
* **[S]** The seven-layer stack is a design vocabulary, not a standard. Layer 7 has no implementation.
* **[C]** Timings are single runs on one shared container; the third digit moves between runs.

---

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-TRC-1 | tracked `.x3d` files; duplicates dropped; scenes parsed | 1,614; 182; 1,379 | [C] | `measure/m_corpus.py`, engine `dcba70d7`, Python 3.13.18 | `x3d.ml@305fd60:measure/results/m_corpus.json` |
| N-TRC-2 | parse failures; not XML | 47; 6 | [C] | same | same |
| N-TRC-3 | elements; attributes; value-bearing attributes | 248,929; 364,127; 100,392 | [C] | same | same |
| N-TRC-4 | repeated quotes, value only | 57.6% | [C] | same | same |
| N-TRC-5 | repeated quotes, `attr="value"` | 43.7% | [C] | same | same |
| N-TRC-6 | repeated quotes, start tag plus 3 tokens | 15.9% | [C] | same | same |
| N-TRC-7 | repeated `attr="value"` quotes; first hit on the wrong node | 43,903; 37,797 (86.1%) | [C] | same | same |
| N-TRC-8 | wrong when the field's node chooses | 1 of 43,903 | [C] | same | same |
| N-TRC-9 | shapes with a world box | 28,465 of 32,608 (87.3%) | [C] | same | same |
| N-TRC-10 | scenes with every shape boxed | 878 of 1,142 | [C] | same | same |
| N-TRC-11 | value attributes of model-written scenes for which a prompt phrase could be quoted | 394 of 8,250 (4.78%), 201 runs | [L] | `measure/m_grounding.py`, lexical matcher (an upper bound on quoting) | `x3d.ml@305fd60:measure/results/m_grounding.json` |
| N-TRC-12 | tamper: attempts caught, item edited in sidecar | 1,120 of 1,120 | [C] | `measure/m_tamper.py`, seed 20261116, 40 scenes, 656 claims | `x3d.ml@305fd60:measure/results/m_tamper.json` |
| N-TRC-13 | tamper: scene edited | 319 of 319 | [C] | same | same |
| N-TRC-14 | tamper: consistent forgeries caught (two families, 80 each) | 0 of 160 | [C] | same | same |
| N-TRC-15 | cost per claim: check; check and record; audit | 0.35; 0.72; 0.59 ms | [C] | same, one core | same |
| N-TRC-16 | independent review: tests written without the code; defects in the first build | 1,204; 43 | [C] | `tests/test_x3dtrace.py`, Python 3.13.18 | `x3d.ml@305fd60:docs/TRACE-REVIEW.md` |
| N-TRC-17 | conformance rows where x3dtrace differs from GAIK on purpose | 55 of 135 | [C] | `tests/fixtures/trace_conformance.json` | `x3d.ml@305fd60:docs/DESIGN.md` |
| N-TRC-18 | browser port rows agreeing with the engine | 1,767 of 1,767 | [C] | `js/test_vectors.js`, Node 22; the committed file holds 968 of them | `x3d.ml@305fd60:js/README.md` |
| N-TRC-19 | planted claims, `x3d.s1`: true claims verified; wrong number verified; word outside quote verified; fabricated quote verified | 5,782 of 5,808; 0 of 806; 0 of 5,357; 0 of 5,808 | [C] | `x3d.s1` `tools/evidence_measure.py`, Python 3.13.18, 501 scenes | `x3d.loom@be7c481:x3d.s1/README.md` |
| N-TRC-20 | paraphrased instruction-like strings verified as quotes (blind spot) | 501 of 501 | [C] | same | same |
| N-TRC-21 | `scene_evidence` tool tests | 36 | [C] | pytest, Python 3.13.18 | `x3d_mcp@e55375f:docs/scene-evidence.md` |
| N-TRC-22 | `scene_evidence`, 600-block scene (92,280 B) with 100 claims, BIND on | 71 ms | [C] | `evaluation/time_scene_evidence.py`, median of 7 calls, engine `dcba70d7`, 4 cores | same |
| N-TRC-23 | `x3d-blender-io` lineage tests: pure Python; with Blender | 15; 4 | [C] | Python 3.13.18; bpy 5.3.0 as recorded in the commit message | `x3d-blender-io@044bea3:source/lineage.py` |
| N-TRC-24 | open review findings, each with an expected-failure test | 8 | [C] | `tests/test_x3dtrace.py` | `x3d.ml@305fd60:docs/TRACE-REVIEW.md` |

---

## Sources and provenance

Read on 2026-11-16: the article "How I Added Traceability in Structured Data Extraction with AI" (Medium, November 2026, by Umair Ali Khan), as supplied; the GAIK toolkit (https://github.com/GAIK-project/gaik-toolkit, MIT, commit 394a94b) for its source-tracing component, read and run for its vectors, nothing sent upstream; the W3C Web Annotation Data Model, PROV-O and the OpenLineage column-lineage facet (1-2-0), whose schemas are vendored in `x3d.ml`; the C2PA specification 2.5, read for its hard-binding and region model (it names no X3D: a search of the text for "x3d" finds nothing). The repositories and commits are named in the header table and in the Source column. The engine is an independent implementation written from a behavioural description; the MIT notice and the list of deliberate differences are in `NOTICE-x3dtrace.md` of `x3d.ml`. The claim ledger for this chapter is `claims/23-traceability-lineage.jsonl`: each number above that is literal in a public file has a line with the words it was read from, pinned at the commit shown. Derived figures (the 86.1% share, the 87.3%, the 4.78%) are quoted from the files that state them or stay uncovered.
