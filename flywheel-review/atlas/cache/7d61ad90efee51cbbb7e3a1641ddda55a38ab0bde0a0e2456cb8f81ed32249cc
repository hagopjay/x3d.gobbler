# 16. Typed X3D: Zod, JSON Schema and the model that can be held to it

> **Say it:** The Web3D X3D 4.0 JSON Schema can be compiled into Zod schemas and TypeScript types (364 definitions, one in-memory correction), so a model's X3D JSON is checked in code with the exact path of every fault, shrunk to the few nodes a model needs for constrained decoding, and compared with the XSD and the semantic layer; four validators agreed on all 1,432 convertible repository scenes, and the 190 scenes where the XSD and the JSON Schema differ are almost all faults in the standards or in our converter, not in Zod. **[C]**

| field | value |
|---|---|
| chapter code | `ZOD` |
| prerequisites | [01 The tether](01-the-tether.md); [03 Validator and gates](03-validator-and-gates.md) for the XSD and semantic rungs; [04 MCP for agents](04-mcp-for-agents.md) for the tool surface |
| after this you can | (1) generate Zod and TS types from the Web3D JSON Schema and say which JSON Schema keywords the generator models; (2) turn a model's text into a verdict with a path, and into a repair prompt; (3) build a node-restricted schema and say what lean mode costs; (4) say what the JSON gate catches that the XSD cannot, and the reverse; (5) read the corpus table and know which disagreements are the standards' |
| sources read | `x3d.loom@d8e02ef:x3d.zod/{tools/gen.mjs,src/index.ts,src/restrict.ts,tools/xml2json.py,tools/corpus.py,tools/fuzz.mjs,tests/,receipts/}`; `x3d_mcp@60b9474:src/validation/{llm_schema.py,validate.py}` and `src/tools/validate_tool.py`; `x3d.demo@9c96896:docs/demos/typed-x3d/v1/` |
| instruments used | Web3D `x3d-4.0-JSONSchema.json` sha1 `c6765a4` (1,023,286 bytes) with the `NavigationInfo.@type` correction applied in memory; `zod 4.6.7`; `ajv 8.20.0` (Draft 2020-12, formats off); `jsonschema 4.26.0` (Python 3.13); `typescript 7.0.2`; `esbuild 0.25.12`; Node v22.23.4; `x3d_mcp fork fbe165f` for `validate_xml`, `validate_json`, `validate_semantic` and `json_to_xml`; `X_ITE 16.6.0` on Chromium with SwiftShader; one container with 4 CPU cores and no GPU |

A model that writes X3D has two failure modes: it writes something the standard forbids, and it writes something the standard allows that is wrong. The first is a typing problem and typing problems are cheap to catch if the schema is code. This chapter is the typing layer: how the JSON Schema becomes Zod, what it can and cannot see, and what four validators say when they all look at the same 1,533 scenes.

---

## 1. The map

```text
  Web3D x3d-4.0-JSONSchema.json (sha1 c6765a4, 364 $defs, 261 scene nodes, "Experimental")
        |  + in-memory correction: NavigationInfo.@type is an MFString typed "string"
        v
  tools/gen.mjs --> src/generated/x3d.zod.ts   887 z.strictObject, 301 z.union, 88 z.tuple,
        |                  |                    150 z.enum, plus 364 explicit TS types
        |                  +--> src/index.ts    validateX3DJson, parseLlmX3D, repairPrompt;
        |                                       paths like X3D/Scene/-children/0/Shape/...
        +--> src/restrict.ts, x3d_mcp llm_schema.py   schema for a chosen node vocabulary

  one model reply
     | JSON.parse --------------------------------> not JSON: "json_parse"
     v
  JSON gate (this chapter) --> XSD (after json_to_xml) --> semantic layer --> X_ITE picture
   typing, shape, ranges        enumerations, order         ROUTE targets,    what it looks like
                                                            profile, DEF/USE
```

| in scope | out of scope |
|---|---|
| the JSON Schema as code; node restriction; four-validator corpus run; fuzz; the mistakes a model makes | calling a model (nothing here does); ROUTE and DEF/USE meaning; X3D 4.1 content (the schema stops at 4.0) |

Read next: deeper, [03 Validator and gates](03-validator-and-gates.md) (the rungs this gate sits beside); wider, [21 Yjs](21-yjs-collaboration.md) (another place an agent's output must be checked before it enters a scene).

---

## 2. The generator

The schema uses a small slice of Draft 2020-12. Counting every keyword in the file shows why a hand-written generator is enough: `type`, `$ref`, `properties`, `items`, `minItems`, `maxItems`, `enum`, `oneOf`, `anyOf`, `minimum`, `maximum`, `exclusiveMinimum`, `prefixItems`, `required`, `additionalProperties`, `format`, `default`, `$comment`. Nothing else occurs (`x3d.zod/tools/gen.mjs` throws on an unsupported `$ref`).

| JSON Schema | Zod output | Note |
|---|---|---|
| `additionalProperties: false` (887 of 887 objects) | `z.strictObject` | a misspelled field is an error, never a silent no-op |
| `oneOf` of a USE arm and a definition arm (261 nodes) | `z.union` | safe because only the USE arm requires `@USE` |
| `prefixItems` (88 emitted, 79 as inline properties) | `z.tuple`, positions at or past `minItems` optional, extra length check | the bug in section 5 |
| `enum` (150) | `z.enum` | |
| `minimum`/`maximum`/`exclusiveMinimum` | `.min` `.max` `.gt` | colours 0 to 1, angles, sizes |
| `$ref` | a property getter | recursion without `z.lazy` on every field |
| `default`, `$comment`, `format` | ignored | `--comments` adds descriptions |

Two design choices matter more than the table. First, every definition is annotated `z.ZodType<T_Name>` with an explicit generated TS type; letting TypeScript infer 364 mutually recursive Zod types fails with "Type instantiation is excessively deep" (observed on the first attempt). Second, the generated file is 597,222 bytes and `tsc` checks it with the tests in about 8 s (`typescript 7.0.2`), so type drift between the two outputs is a build error, not a surprise.

```bash
cd x3d.loom/x3d.zod && npm ci
npm run gen && npm run typecheck && npm test
```

## 3. Turning a reply into a verdict

`validateX3DJson` returns `{ok, value}` or a list of `{path, code, message}`. The useful part is the path. Zod reports a failed union as a single "Invalid input", and every X3D node is a union of its USE arm and its definition arm, so a naive report points at the node and says nothing. `toIssues` opens each union and keeps the arm the document was trying to be: not the USE arm unless `@USE` is present, then the deepest, then the one with the fewest complaints.

| mistake in the reply | issue path (shortened) | message |
|---|---|---|
| `NavigationInfo.@type` as the string `"EXAMINE"` | `.../NavigationInfo/@type` | expected array, received string |
| `"@radius": "0.36"` | `.../Sphere/@radius` | expected number, received string |
| Box `@size` with two numbers | `.../Box/@size` | expected array to have >=3 items |
| a node called `Torus` | `.../-geometry` | Unrecognized key: "Torus" |
| `@diffuseColour` | `.../Material` | Unrecognized key: "@diffuseColour" |
| emissive colour `[255, 153, 30]` | `.../@emissiveColor/0` | expected number to be <=1 (3 issues) |
| `@version` `"4.1"` | `X3D/@version` | expected one of "3.0", "3.1", "3.2", "3.3", "4.0" |

`parseLlmX3D` accepts a fenced block or bare JSON; `repairPrompt` turns the first twelve issues into a prompt that names the schema and asks for the complete corrected document. A document nested so deeply that Zod's recursive descent overflows the stack is reported as `stack_depth`, which means *not checked*; it is never reported as valid (section 7).

## 4. The mask: a schema a decoder can use

The full schema is 502,810 bytes minified, which does not fit a structured-output request and offers a model 261 nodes it will not use. `restrictSchema` (TypeScript) and `restricted_schema` (Python, the `x3d_json_schema` tool of the x3d_mcp fork) keep the schema's structure and typing, delete every scene node outside a named vocabulary from every `properties` map, and prune the definitions that become unreachable.

| vocabulary | nodes | full-key bytes | lean bytes | defs kept (lean) |
|---|---|---|---|---|
| starter | 12 | 32,744 | 19,153 | 42 |
| animated | 19 | 44,177 | 25,635 | 49 |
| all of X3D 4.0 | 261 | 502,810 | not measured | 364 |

Lean mode also drops `@class`, `@id`, `@style`, `IS`, `-metadata`, `#comment` and every `$comment`, `default` and `description`. That is not free: of the 966 repository scenes the full schema accepts, 110 are rejected by the lean all-nodes schema (67 use `-metadata`, 41 use `@style`, 2 use `IS`), and a `ProtoDeclare` whose body wires fields with `IS` cannot be written in lean mode. Use `lean: false` when the model must write those. The `NavigationInfo` correction must be applied before restricting, because it keys on a `$comment` that lean mode deletes.

An independent comparison of the two implementations on 32 vocabulary and lean combinations (starter, animated, empty, all, single nodes, ten random sets, each lean off and on) found identical output. It also found two gaps that are now closed: the TypeScript side silently accepted a misspelled node name where Python raised, and nothing guarded the parity. Both test suites now pin the same two sha1 prefixes of the starter schemas and both refuse unknown names.

## 5. Four validators, 1,533 scenes

Every `.x3d` file in nine project repositories (1,533 files of at most 2 MB) was converted to X3D JSON by `tools/xml2json.py`, which takes its field typing and container placement from the JSON Schema itself, then judged by the XSD (x3d_mcp `validate_xml`), `jsonschema` (x3d_mcp `validate_json`), `ajv` and Zod.

| step | files |
|---|---|
| found | 1,533 |
| not convertible (XML will not parse, empty file, nesting beyond Python's recursion limit) | 97 |
| converted but containing `NaN` or `Infinity` (not JSON) | 4 |
| **checked by all four** | **1,432** |
| Zod, ajv and jsonschema gave the same verdict | **1,432** |

```text
                         JSON Schema accepts   JSON Schema rejects
        XSD accepts              918                   128
        XSD rejects               62                   324
```

The first run had one split, and it was our generator. `@geoSystem` is a tuple (`prefixItems` of 4, `minItems` 2); a Zod tuple demands every position, JSON Schema only constrains positions that exist. `TransmitterPdu.x3d` (`["UTM","Z3","N"]`) was accepted by three validators and rejected by Zod. The generator now marks positions at or past `minItems` optional and states the length bounds the tuple shape cannot, and `tests/tuples.test.ts` draws 400 random arrays against each of the 79 tuple-typed properties and compares Zod with ajv.

Speed per scene, this container, median and 95th percentile: ajv (compiled once) 0.19 ms and 2.6 ms; Zod 1.13 ms and 27 ms; `jsonschema` 2.3 ms and 251 ms. Zod is about six times slower than ajv at the median, and about twice as fast as `jsonschema` at the median and nine times at the 95th percentile.

### 5.1 Why the standards disagree on 190 scenes

A root-cause pass (four independent reviewers, each finding graded by whether it was reproduced on a minimal document) went through the first run's 224 disagreements. The upper block is the rerun's first issue per scene (128); the lower block keeps the first run's counts (72), since the reviewers' breakdown was taken then. Where the pass found our converter at fault, that is stated and the converter was fixed.

| direction | scenes | cause | grade |
|---|---|---|---|
| XSD accepts, JSON rejects | 60 | X3D 4.1 content the 4.0 schema cannot hold: `@version "4.1"` (30), the `GaussianSplats` node (7) and component name (23) | **[C]** |
| | 20 | `OscillatorSource` has no slot for its `PeriodicWave` child | **[C]** |
| | 9 | `ClipPlane @plane` bounds all four components to [-1,1]; the fourth is a distance | **[C]** |
| | 8 | `geoSystem` order keywords (`longitude_first`) and non-Earth ellipsoids have no arm | **[C]** |
| | 6 | `CollisionSensor @description` missing | **[C]** |
| | 13 | one-offs: `TextureProjector` vs the XSD's `TextureProjection`, `HAnimMotion @name`, empty MF arrays, Layout enums, `groundAngle` 1.571 against a 1.5708 bound | **[C]** |
| | 12 | probes and fixtures invalid on purpose (DEF and USE on one node, negative sensor size); three are a guess from the fixture name | **[L]** |
| XSD rejects, JSON accepts (first run's 72; 62 now) | 26 | the XSD is stricter than the X3DUOM (`containerField="pickTarget"`, a `xs:sequence` standing in for a choice); the JSON Schema is right | **[C]** |
| | 16 | the JSON Schema is too lenient: DEF, USE and ROUTE names are bare strings (11), MFVec3f length not a multiple of 3 (2), `ProtoInstance` without `@name`, `HAnimSite` under `HAnimJoint`, `EnvironmentLight` in a 4.0 schema | **[C]** |
| | 5 | things JSON cannot say: XML sibling order (2), document-wide DEF uniqueness (3) | **[C]** |
| | 25 | our converter hid the fault; 14 fixed (case-folded booleans, `-08`, invented version and profile, replaced `containerField`), 11 open (dropped text content, stripped namespaces) | **[C]** |

Of the first run's 224, 56 were the converter's: 29 scenes whose hex `SFImage` pixels it left as text, 2 whitespace-padded versions, and 25 of the lenient list. Fixing them moved the table from 894, 152, 72, 310 to the one above.

## 6. Three gates, nine mistakes

The same nine mistakes (an orrery damaged in nine ways a model does) through the JSON gate, the XSD after `json_to_xml`, and the semantic layer. These are nine constructed documents, not a measured error rate.

| # | mistake | JSON Schema | XSD | semantic |
|---|---|---|---|---|
| 1 | two numbers where three are needed | caught | caught | passes |
| 2 | a node that is not X3D (`Torus`) | caught | caught | passes |
| 3 | a misspelled field | caught | caught | passes |
| 4 | `NavigationInfo.@type` as a string | caught | passes | passes |
| 5 | colours on a 0 to 255 scale | caught | caught | caught (`colour-out-of-range`) |
| 6 | geometry without its `-geometry` slot | caught | passes | passes |
| 7 | a number as a string | caught | passes | passes |
| 8 | version "4.1" claimed | caught | passes | passes |
| 9 | ROUTE to a node that does not exist | passes | passes | caught (`route-missing-to-node`) |

The JSON gate catches 8 of 9, the XSD 4, the semantic layer 2, and every mistake is caught by at least one. Rows 4, 6, 7 and 8 pass the XSD because JSON typing (array against string, slot against key, number against string) is erased when the document becomes XML attributes. Row 9 passes both schema gates because a ROUTE is four strings to them. The clean scene passes all three, but only after one fix: the first draft used a `PointLight` under the `Interchange` profile, which the semantic layer rejected (`profile-component`), a fault the JSON Schema never saw.

## 7. What breaks Zod

| property | measured |
|---|---|
| fuzz, seed 1: 7,728 mutants of 966 valid scenes (delete, retype, rename, extend, truncate, enum swap, range, duplicate) | Zod and ajv disagreed on 0; 5,597 mutants still valid, 2,131 rejected |
| 79 tuple properties x 400 random arrays | 0 disagreements between Zod and ajv (it fails if the tuple fix is removed) |
| nesting depth | Zod's recursive descent overflowed on two scenes nested 240 and 300 Transforms deep, while ajv accepted them; the cut-off is about 115 nested Transforms at Node's default stack and about 484 with `--stack-size=4000` (a cold-start measurement) |

An LLM will not write a hundred nested Transforms, but an adversarial or machine-generated scene can, so the library catches the `RangeError` and returns `stack_depth`. The caller should fall back to an iterative validator (ajv, `jsonschema`).

---

## Heuristics

| ID | Rule (imperative, at most 30 words) | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-ZOD-1 | Generate the Zod from the schema file and pin the file's sha1; a hand-copied schema drifts without a signal. | C | `gen.json` records sha1 `c6765a4` and the generated file is regenerated and compared in a test | `x3d.zod` `tools/gen.mjs`, test `zod-002` |
| H-ZOD-2 | Annotate every generated Zod schema with an explicit generated TS type; do not let TypeScript infer a 364-definition recursive graph. | C | inferred form failed with "excessively deep" on the first attempt; annotated form checks in about 8 s | `typescript 7.0.2` |
| H-ZOD-3 | Treat `prefixItems` as positional constraints on positions that exist: mark positions at or past `minItems` optional, then state any length bound the tuple cannot. | C | `TransmitterPdu.x3d` `["UTM","Z3","N"]` rejected by Zod, accepted by ajv and jsonschema | corpus run, `tests/tuples.test.ts` |
| H-ZOD-4 | When a union fails, report the arm the document meant, not "Invalid input": drop the USE arm unless `@USE` is present, then take the deepest. | C | `NavigationInfo` and `@radius` mistakes point at the field | `x3d.zod` test `zod-010` |
| H-ZOD-5 | Put the schema correction in memory and keep the upstream file byte-identical and hashed; restrict only after correcting. | C | lean mode deletes the `$comment` the correction keys on | test `zod-001`, `llm_schema.py` |
| H-ZOD-6 | Restrict by vocabulary, not by prompt: a node outside the vocabulary must have probability zero, not a request not to use it. | L | constrained schemas of 19,153 to 25,635 bytes against 502,810 bytes; no model was run | `restrict.ts`, `llm_schema.py` |
| H-ZOD-7 | Use lean restriction only when the model never writes metadata, `@style` or `IS`; otherwise keep full keys and pay the bytes. | C | 110 of 966 scenes rejected by lean | `jsonschema 4.26.0` over the corpus |
| H-ZOD-8 | Run more than one validator and compare before trusting a count; a split is a bug in one of them. | C | one split found in 1,533 scenes, in our generator | four-validator corpus run |
| H-ZOD-9 | Check a schema-driven converter for repairs: a validator that sees a repaired document cannot catch the fault it hid. | C | 56 of 224 first-run disagreements were converter repairs | root-cause pass |
| H-ZOD-10 | Return "not checked" for a document the validator could not process; never fold a crash into valid or invalid. | C | Zod overflowed on 240 and 300 nested Transforms | `stack_depth` test `zod-008` |
| H-ZOD-11 | Put the schema gate first and the semantic layer last; neither implies the other. | C | 8 of 9 caught by JSON, 2 of 9 by semantic, 9 of 9 by the union | `matrix.json` in the demo |
| H-ZOD-12 | Do not read "valid" as "correct": a ROUTE to a node that does not exist passes both schema gates. | C | mistake 9 | `x3d_mcp fork fbe165f` `validate_semantic` |

## Drills

Commands run from `x3d.loom/x3d.zod` after `npm ci`.

### D-ZOD-1 Run the suite
- **Level:** L1
- **Task:** Run the node tests and count them.
- **Verify:** `npm test`
- **Answer:** 32 tests, 32 pass, 0 fail.
- **Checked:** 2026-11-15 Node v22.23.4, zod 4.6.7, ajv 8.20.0

### D-ZOD-2 Regenerate and compare
- **Level:** L2
- **Task:** Run the generator and read its receipt. How many definitions, tuples, strict objects, unions? Does the generated file change?
- **Verify:** `node tools/gen.mjs && git diff --stat -- src/generated`
- **Answer:** 364 definitions, 88 tuples, 887 strict objects, 301 unions, 150 enums; no diff. The receipt reports `upstreamMatches: true`.
- **Checked:** 2026-11-15 Node v22.23.4, schema sha1 `c6765a4`

### D-ZOD-3 Put the tuple bug back
- **Level:** L3
- **Task:** In `tools/gen.mjs`, make every `prefixItems` position required (remove the `.optional()` marking), regenerate, and run `node --test tests/tuples.test.ts tests/schema.test.ts`. Which tests fail and on what input?
- **Verify:** the two test files; restore with `git checkout tools/gen.mjs src/generated`.
- **Answer:** the tuple test fails (0 pass, 1 fail) and `zod-g06 geoSystem short tuple` fails in the schema tests (30 pass, 1 fail); the input is a `@geoSystem` array shorter than its prefix such as `["UTM","Z3","N"]`.
- **Checked:** 2026-11-15 Node v22.23.4, zod 4.6.7, ajv 8.20.0

### D-ZOD-4 The upstream file has the NavigationInfo bug
- **Level:** L2
- **Task:** Compile the unmodified upstream schema with ajv and test a `NavigationInfo` with `@type` as `["EXAMINE","ANY"]` and as `"EXAMINE"`. Then run `validateX3DJson` on both.
- **Verify:** three lines of ajv (Draft 2020 build, `strict: false`, `validateFormats: false`) against `schema/x3d-4.0-JSONSchema.json`; the library for the second half.
- **Answer:** upstream ajv rejects the array form and accepts the bare string; `validateX3DJson` accepts the array and reports the string at `.../NavigationInfo/@type` ("expected array, received string").
- **Checked:** 2026-11-15 ajv 8.20.0, zod 4.6.7, schema sha1 `c6765a4`

### D-ZOD-5 Size a vocabulary
- **Level:** L2
- **Task:** Restrict the schema to the starter vocabulary, lean on and off, and give the sizes. Then check that the Python tool agrees.
- **Verify:** `restrictSchema(schema, {nodes, lean})` in Node and `restricted_schema(PRESETS["starter"], lean)` in `x3d_mcp@60b9474:src/validation/llm_schema.py`; compare `sha1` of the key-sorted compact JSON, first 12 hex digits.
- **Answer:** 32,744 and 19,153 bytes; digests `339dee2fc602` (full keys) and `2e7ef1bfc403` (lean) on both sides.
- **Checked:** 2026-11-15 Node v22.23.4 and Python 3.13, schema sha1 `c6765a4`

### D-ZOD-6 Find the stack limit
- **Level:** L3
- **Task:** Binary-search the deepest chain of nested `Transform` nodes that Zod accepts at the default stack, then at `--stack-size=4000`. What does the library return beyond it?
- **Verify:** build the document in a loop, call `X3DJson.safeParse` inside `try`, bisect on depth; the library call is `validateX3DJson`.
- **Answer:** about 115 at the default stack and about 484 at `--stack-size=4000` (cold start, so treat as approximate); beyond it `validateX3DJson` returns one issue with code `stack_depth`.
- **Checked:** 2026-11-15 Node v22.23.4, zod 4.6.7

## Honest limits

- **No model was run.** The repair is a scripted replay and the mistakes are constructed. Whether a constrained decoder given a 19 KB schema writes better X3D than an unconstrained one is not measured here; **[S]**. The earlier constrained-decoding A/B in the project used a different schema encoding and is not compared.
- **The schema stops at X3D 4.0 and is marked experimental.** Sixty scenes fail only for 4.1 content; the gate is right for the file as published and wrong for the draft standard. **[C]**
- **The converter is ours.** 97 files did not convert, 4 contain `NaN` or `Infinity`, 595 of the 1,432 had at least one attribute or child the converter could not place (the schema then judged the text as written), and 11 converter repairs are still open (dropped text content, stripped namespaces). **[C]**
- **The fuzz and the corpus agree because both sit on the same schema semantics.** They test the generator against ajv, not the schema against the standard; the root-cause table is the second half.
- **The root-cause grades are reviewers' grades.** Each **[C]** was reproduced by a reviewer on a minimal document; I re-ran the counts, not each repro. Three rows are guesses from fixture names and say so.
- **Timings come from one container** with 4 CPU cores and no GPU. They rank validators; they are not a benchmark.
- **The demo's XSD and semantic columns are recorded**, not run in the page (they need Python).

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-ZOD-1 | definitions in the Web3D JSON Schema / of them scene nodes | 364 / 261 | [C] | `x3d.zod` `gen.mjs`, schema sha1 `c6765a4` | `x3d.loom@d8e02ef:x3d.zod/receipts/gen.json` |
| N-ZOD-2 | generated Zod file | 597,222 bytes | [C] | `gen.mjs` | `x3d.zod/src/generated/x3d.zod.ts` |
| N-ZOD-3 | strict objects / unions / tuples / enums emitted | 887 / 301 / 88 / 150 | [C] | `gen.mjs` | `x3d.zod/receipts/gen.json` |
| N-ZOD-4 | node tests | 32 of 32 pass | [C] | Node v22.23.4, zod 4.6.7, ajv 8.20.0 | `x3d.zod/tests` |
| N-ZOD-5 | full schema minified / starter lean / animated lean | 502,810 / 19,153 / 25,635 bytes | [C] | `restrictSchema` and `llm_schema.py` agree | `x3d.zod/src/restrict.ts`, `x3d_mcp@60b9474` |
| N-ZOD-6 | repository scenes found / checked by all four validators | 1,533 / 1,432 | [C] | `tools/corpus.py`, x3d_mcp fork fbe165f | `x3d.zod/receipts/corpus-summary.json` |
| N-ZOD-7 | scenes where Zod, ajv and jsonschema agree | 1,432 of 1,432 | [C] | same | same |
| N-ZOD-8 | XSD accepts and JSON accepts / XSD accepts and JSON rejects | 918 / 128 | [C] | `validate_xml`, `validate_json` | same |
| N-ZOD-9 | XSD rejects and JSON accepts / both reject | 62 / 324 | [C] | same | same |
| N-ZOD-10 | median validation time Zod / ajv / jsonschema | 1.13 / 0.19 / 2.3 ms | [C] | one container, 4 cores, no GPU | same |
| N-ZOD-11 | 95th percentile Zod / ajv / jsonschema | 27 / 2.6 / 251 ms | [C] | same | same |
| N-ZOD-12 | fuzz mutants / Zod-ajv disagreements | 7,728 / 0 | [C] | `tools/fuzz.mjs`, seed 1, 966 source scenes | `x3d.zod/receipts/fuzz.json` |
| N-ZOD-13 | tuple properties tested x random arrays | 79 x 400, 0 disagreements | [C] | `tests/tuples.test.ts` | `x3d.zod/tests` |
| N-ZOD-14 | lean restriction rejecting scenes the full schema accepts | 110 of 966 | [C] | `jsonschema 4.26.0` | independent review, `llm_schema.py` comments |
| N-ZOD-15 | nine-mistake matrix: caught by JSON / XSD / semantic / any | 8 / 4 / 2 / 9 | [C] | `x3d_mcp fork fbe165f`, Zod 4.6.7 | `x3d.demo@9c96896:docs/demos/typed-x3d/v1/matrix.json` |
| N-ZOD-16 | first-run disagreements that were converter repairs | 56 of 224 | [C] | root-cause pass | `x3d.zod/receipts/rootcause-v1.json` |
| N-ZOD-17 | Zod stack limit, nested Transforms | about 115 default, about 484 at 4000 | [C] | Node v22.23.4 (cold start) | drill D-ZOD-6 |
| N-ZOD-18 | Zod browser bundle | 734,727 bytes, 115,346 gzipped | [C] | `esbuild 0.25.12` | `x3d.demo@9c96896:docs/demos/typed-x3d/v1/x3d-zod.bundle.js` |

## Sources and provenance

`x3d.loom@d8e02ef` folder `x3d.zod` (branch of the first pull request), read and run on 2026-11-15; `x3d_mcp@60b9474` (`src/validation/llm_schema.py`, the `x3d_json_schema` tool, 11 tests; the full suite was 1,377 passed and 27 skipped before the digest tests, Python 3.13) and its validators at `fbe165f`; `x3d.demo@9c96896` for the page and `matrix.json`. The schema file is the Web3D Consortium's published `x3d-4.0-JSONSchema.json`; Zod by Colin McDonnell and contributors; ajv by Evgeny Poberezkin and contributors. The corpus is the `.x3d` files in the nine project repositories as checked out on 2026-11-15.
