# 03. The validator and the gates

> **Say it:** A validator is a ladder, not a verdict: every rung names what it checked, the rungs below the renderer cannot see "looks right", and a verdict without a commit and a schema version is a rumour. **[C]**

| field | value |
|---|---|
| chapter code | `VAL` |
| prerequisites | [01 The tether](01-the-tether.md) for why a file must carry its own checks; [02 Loom laws](02-loom-laws.md) for the witness vocabulary |
| after this you can | run every rung of the x3d_mcp validator on a scene and say which rung fired; read an exact-fix hint and judge whether to apply it; say which schema ("4.0", "4.1", X3DUOM, X_ITE extension) a "valid" was valid against; run and read a loomkit witness and an accept decision; add a new semantic rule with a test; write a validator pin line that a stranger can re-run |
| sources read | x3d_mcp@b4efcd3:src/validation/*.py, src/tools/validate_tool.py, docs/EXACT-FIX-HINTS.md; x3d.loom@162ab18:kit/loomkit/*.py, kit/tests/test_gates.py, runs/*/evidence/grammar.json; x3d-blender-io@ab99988:tests/suite/, docs/test-suite/ |
| instruments used | `x3d_mcp fork b4efcd3`; `x3d_mcp upstream 74da0ec`; `X3D XSD 4.0` (sha256 0509fa5bd601), `X3D XSD 4.1` (sha256 1a7935caa7e6); `X3DUOM 4.1` (sha256 4fc10e8e15c0); lxml 6.1.3 over libxml2 2.14.6; Python 3.13.18; software only (4 vCPU Intel Xeon 2.30 GHz, no GPU) |

Rig for every number marked **[C]** below: a fresh virtualenv with the repo's pinned dependencies (`mcp` 1.30.0, `x3d` 4.0.65.8, `lxml` 6.1.3, `xmlschema` 4.3.2, `rdflib` 7.6.0, `pyshacl` 0.40.2, `pytest` 9.2.0), run on 2026-11-14 against a checkout of `x3d_mcp@b4efcd3`. The sources were read-only; scratch copies and patches lived outside the repos.

## 1. The map

```text
 scene text (XML)
   |
 R0  well-formed XML?              lxml parse                  "XML parse error: ..."
   v
 R1  which schema?                 resolve_xsd_version         note when a schema is substituted
   v                                4.0 | 4.1 | 3.x -> 4.0 | none or unknown -> 4.1
 R2  XSD content model and types   XMLSchema, libxml2 2.14.6   "Element 'Box': not expected"
   v                                one error per parent; the engine can give up on long lists
 R3  semantic rules (51 ids)       semantic_diagnostics        error | warning | info
   v    DEF/USE ROUTE containerField counts indices colours HAnim physics splats
 R4  exact-fix hints (19 rules)    validate_xml_with_hints     {rule, suggested_fix, confidence}
   v    10 edit ops; one hint per error the layer understands
 R5  apply and re-check            repair_x3d, exact_fix_hints(apply=true), autofix_x3d
   v    "valid_after" is a gate verdict, not an intent verdict
 R6  does it draw something?       render_image (Playwright + X_ITE)  read, not run here
   v    blank-frame detection; the only rung that can see "looks wrong"
 R7  conformance and gate scripts  loomkit witnesses -> accept -> receipt; blender-io; pytest
```

| rung | instrument (string to quote) | answers | cannot answer |
|---|---|---|---|
| R0 | lxml 6.1.3 / libxml2 2.14.6 | is this text XML at all | anything about X3D |
| R1 | `x3d_mcp fork b4efcd3` `validate.resolve_xsd_version` | which bundled XSD judges this file | whether the author meant that version |
| R2 | `X3D XSD 4.0` / `X3D XSD 4.1` via libxml2 | element order, attribute names, enumerations, number patterns | cross-references (DEF/USE, ROUTE), counts, anything the XSD cannot say |
| R3 | `x3d_mcp fork b4efcd3` `semantic.py` | the spec rules a schema language cannot express, plus renderer-dropped constructs (ROUTE before DEF) | whether the scene is placed, lit, in view |
| R4 | `x3d_mcp fork b4efcd3` `hints.py` + `verified-containment.json` | where a misplaced node may go; what the legal value is | intent: the hint is mechanical, the author's intent is not in the file |
| R5 | same | whether the scene passes R2+R3 after the edits | whether the edits kept the content you wanted |
| R6 | `X_ITE 16.4.3` (pinned by the repo README), Chromium | a frame with something in it | correctness of what is drawn; needs a browser |
| R7 | loomkit, blender-io suite, pytest | a repeatable accept or reject, bound to a candidate hash | anything outside the checks it is configured with |

**In scope:** the validator package of the x3d_mcp fork at `b4efcd3`, the exact-fix layer, and the two gate systems that call it or sit beside it (loomkit and the x3d-blender-io conformance suite). **Out of scope:** the MCP tool surface, transfer layer and guards (see [04 MCP for agents](04-mcp-for-agents.md)); ontology and SHACL checks (see [05 Semantic layer](05-semantic-layer.md)); X_ITE's own runtime behaviour (see [06 X_ITE, the oracle](06-xite-the-oracle.md)).

**Read next:** deeper, the rule code itself, `x3d_mcp@b4efcd3:src/validation/semantic.py` and the AST teardown in [the x3d_mcp masterclass](../x3d_mcp/MASTERCLASS.md); wider, [04 MCP for agents](04-mcp-for-agents.md) for how a model calls these rungs.

## 2. The rungs in code

All entry points are plain Python functions. The MCP tools in `src/tools/validate_tool.py` wrap them (`validate_x3d`, `validate_semantic`, `autofix_x3d`, `repair_x3d`, `exact_fix_hints`, `validate_current_scene`).

| function | file | returns | note |
|---|---|---|---|
| `validate_xml(xml, version=None)` | `src/validation/validate.py` | `{valid, errors, schema_version, notes?}` | `version` overrides the document's own attribute |
| `validate_xml_with_hints(xml, version=None)` | same | the above plus `hints` | one hint per XSD error the layer understands, keyed by `error_index` |
| `semantic_diagnostics(xml)` | `src/validation/semantic.py` | `list[Diagnostic(level, check, message, node_tag, def_name)]` | raises `XMLSyntaxError` or `NoSceneError`; runs `_check_profile_components` first, then 23 functions in `_ALL_CHECKS` |
| `validate_semantic(xml)` | same | markdown report | the report the MCP tool returns by default |
| `gate(xml)` | `src/validation/hints.py` | `{valid, stage, errors, hints}` | XSD first; semantic error-level checks only once the XSD passes |
| `repair_with_hints(xml)` | same | `{fixed, valid, applied, remaining_errors}` | applies hints one at a time and re-checks after each |
| `repair_x3d(xml)` | `src/validation/repair.py` | `{fixed, changes, unfixable, remaining}` | version, profile, component, DEF order, containerField, doctype, xsi namespace |
| `validate_json(text)` | `src/validation/validate.py` | `{valid, errors}` | checks X3D JSON against the 4.0 JSON Schema only |

The ladder is a **two-stage gate**, not a sum of all findings. `gate()` reports XSD errors and stops; it reports semantic errors only when the XSD passed. A scene with a Box in a Transform therefore shows one stage-`xsd` error through `gate()` while `semantic_diagnostics()` on the same text also reports `containerfield-unknown`.

Timing, **[C]** on `x3d_mcp fork b4efcd3`, CPU only, Python 3.13.18: the first call into each XSD pays a compile of **1,456 ms (4.0)** and **1,547 ms (4.1)**; after that, repeat calls on a 12-line scene took a median of **0.022 ms** (`validate_xml`), **0.314 ms** (`semantic_diagnostics`) and **0.371 ms** (`gate`) over 300 runs each. The first semantic call took about 49 ms (it loads X3DUOM). Repeat-call medians flatter the validator (caches are warm); the cold figure is the one a one-shot CLI pays.

## 3. Rule families and their counts

A "rule" is ambiguous. This chapter counts one definition and names it.

| definition | count at `b4efcd3` | count at `74da0ec` | how counted |
|---|---|---|---|
| distinct rule ids reported by `semantic.py` | **51** | **19** | Python `ast` over `Diagnostic(level, check, ...)` calls, the helper closures `add`, `err`, `report`, `check`, and the two f-string ids `hanim-joint-name`, `hanim-segment-name` |
| check functions run by `semantic_diagnostics` | **24** (23 in `_ALL_CHECKS` plus `_check_profile_components`) | 10 | read from `_ALL_CHECKS` |
| `Diagnostic(...)` and `report(...)` call sites in `semantic.py` | 61 (the `add`, `err` and `check` helpers feed 7 more ids) | 24 | AST |
| ids only in `validation/splat_arrays.py` | 2 (`splat-array-syntax`, `splat-values-unchecked`) | n/a | AST over `Finding(level, check, ...)` |
| ids only in `transfer/inspect_splats.py` | 19 | n/a | AST over `note(level, id, ...)`; this is a file-inspection verdict, not a scene rule |
| union of the three | **72** | n/a | set union |
| hint rule ids in `hints.py` | **19** literal ids, 10 edit ops | n/a | regex and AST over `rule=` and `"rule":` |

The 19 at base and 10 check functions match the teardown; the teardown's "62" at `13121b6` cannot be reproduced under any single definition above (51 + 2 + 10 inspector ids is 63; the closest I can build). I count 51 for the scene validator and treat the 62 as a differently defined number. The validator code is byte-identical between `13121b6` and `b4efcd3` (`git diff --quiet` over `semantic.py`, `validate.py`, `hints.py`, `repair.py`), so the definition, not the commit, explains the gap. **[C]** for 51 and 19; the 62 stays **[L]** (stated in [the masterclass](../x3d_mcp/MASTERCLASS.md), definition not recoverable).

| family | ids at `b4efcd3` (51 total) | n |
|---|---|---|
| route | `route-before-def`, `route-invalid-from-field`, `route-invalid-to-field`, `route-missing-from-node`, `route-missing-to-node`, `route-never-fires`, `route-out-of-scope`, `route-type-mismatch`, `route-wrong-access-type` | 9 |
| DEF/USE | `duplicate-def`, `unused-def`, `use-before-def`, `use-undefined-def` | 4 |
| containerField | `containerfield-not-node`, `containerfield-type-mismatch`, `containerfield-unknown` | 3 |
| counts, indices, order | `array-count`, `array-count-extra`, `index-out-of-range`, `lod-range-order`, `tuple-count`, `interpolator-key-length`, `interpolator-key-order` | 7 |
| spec values | `colour-out-of-range`, `cycle-interval-zero`, `enum-invalid`, `rotation-zero-axis`, `value-out-of-range` | 5 |
| shape, structure | `shape-no-appearance`, `shape-no-geometry`, `empty-group`, `no-viewpoint` | 4 |
| naming | `naming-convention`, `hanim-joint-name`, `hanim-segment-name` | 3 |
| profile | `profile-component`, `profile-component-fix` | 2 |
| proto | `proto-undeclared` | 1 |
| physics | `physics-joint-body`, `physics-joint-cross-collection`, `physics-mass`, `physics-non-finite`, `physics-not-in-collection`, `physics-zero-axis` | 6 |
| splat | `splat-array-length`, `splat-no-color`, `splat-opacity-space`, `splat-quaternion-norm`, `splat-quaternion-order`, `splat-scale-space`, `splat-sh-partial` | 7 |

The counts are **[C]**; which PR added which rule is in the [teardown](../x3d_mcp/MASTERCLASS.md) PR table (**[L]**). Levels: only `error` blocks `gate()`. `unused-def`, `no-viewpoint`, `shape-no-appearance` and `profile-component-fix` are info-level in the code I read; `hanim-*-name` is warning-level for a recognisable wrong name and info-level for the "other names" summary on a segment.

The rule families are a record of incidents (a ROUTE the XSD accepts but X_ITE drops; a colour written 0..255; a splat in the wrong order), which is why [chapter 02](02-loom-laws.md) says every law is paid for.

## 4. What each rung catches and misses: sixteen scenes, true outputs

One control and fifteen single-fault scenes, written to a scratch folder and run through the ladder on `x3d_mcp fork b4efcd3` (2026-11-14). The base column is `x3d_mcp upstream 74da0ec` (semantic errors counted from its markdown report; its single bundled XSD is 4.1). Every scene is declared `version="4.0"` unless the row says otherwise. Error text is trimmed, not edited.

| scene | fault | R2 XSD | R3 semantic | R4 hint | base 74da0ec |
|---|---|---|---|---|---|
| s00 | control: spinning box, Interactive, 2 ROUTEs | valid | 0 diagnostics | none | 0 / 0 |
| s01 | closing tag missing | R0 stops: `XML parse error: Opening and ending tag mismatch: Shape line 4 and Transform, line 4, column 112` | skipped | none | same |
| s02 | `<Box/>` moved out of its Shape into the Transform | `Element 'Box': This element is not expected. Expected is one of ( ROUTE, ExternProtoDeclare, ProtoDeclare, IMPORT, EXPORT, Background, ColorInterpolator, CoordinateInterpolator, DirectionalLight, Group ).` | `containerfield-unknown` error, `shape-no-geometry` warning | `wrong-parent`, `move` into the sibling Shape, confidence `choice` | 1 error, 1 warning |
| s03 | `diffuseColor="0 102 255"` | pattern facet error naming the value | `colour-out-of-range` error: "divide by 255 if the values were written as 0..255" | `set_attribute diffuseColor="0 0.4 1"`, `choice` | XSD only, 0 semantic |
| s04 | `roughness` on `Material` | `attribute 'roughness' is not allowed` | none (stage stops at XSD) | `unknown-attribute`: "remove it. (PhysicalMaterial has a field 'roughness')" | XSD only |
| s05 | both ROUTEs placed before the nodes they name | **valid** | 2 `route-before-def` errors | `move` each ROUTE to the end of Scene, confidence `exact` | **0 errors** |
| s06 | `USE="Mat"` before `DEF="Mat"` | valid | `use-before-def` error | `swap_def_use`, `exact` | 1 error |
| s07 | SFRotation routed into `set_translation` | valid | `route-type-mismatch` error | `route-field`: "Use toField='set_rotation'" | 1 error |
| s08 | `coordIndex` uses 5, Coordinate has 4 points | **valid** | `index-out-of-range` error | **none** | **0 errors** |
| s09 | profile Interchange plus `PhysicalMaterial` | **valid** | `profile-component` error plus info with the fix | `add_components Shape level 2`, `exact` | **0 errors** |
| s10 | `version="4.0"` with `GaussianSplats` | invalid under 4.0 with a note naming 4.1; **valid when forced to 4.1** | `profile-component` error | `unknown-node` -> `remove_element` (see section 5) | **valid** (single 4.1 XSD) |
| s11 | `BlendMode` (an X_ITE node) under `Appearance`, declared 4.1 | `Element 'BlendMode': This element is not expected.` | none | `unknown-node` -> `remove_element` | XSD invalid, 0 semantic |
| s12 | Box 0.001 wide, 1,000,000 units away, `transparency="1"` | **valid** | **0 diagnostics** | none | 0 / 0 |
| s13 | two nodes share `DEF="Spinner"` | `'Spinner' is not a valid value of the atomic type 'xs:ID'` | `duplicate-def` plus 2 cascade errors | `bad-value`, `suggested_fix` is null | 3 errors |
| s14 | `fromField="fraction_change"` (typo) | valid | `route-invalid-from-field` error | `route-field`: "Use 'fraction_changed'", `exact` | 1 error |
| s15 | HAnim joint named `l_wrist` (a 1.x alias) | valid | 2 `hanim-joint-name` warnings, 3 info | none | 0 / 0 |

Counts of this corpus, **[C]**: 15 faulty scenes; 8 pass the XSD; 6 of those 8 carry a semantic error; the remaining 2 (s12, s15) pass the gate completely (s15 with warnings). Four scenes the fork base accepted outright (s05, s08, s09, s10) are rejected at `b4efcd3`; s03 gains a semantic error on top of the XSD error the base already gave; s15 gains two warnings.

```text
 first rung to say "no"  (x = fires, w = warning only, - = fires but offers no fix)
                                                       R0   R2   R3   hint
 s01 unclosed tag ................................      x
 s02 Box in Transform ............................           x    x     x
 s03 colour 0..255 ...............................           x    x     x
 s04 PBR field on Material .......................           x          x
 s05 ROUTE before DEF ............................                x     x
 s06 USE before DEF ..............................                x     x
 s07 ROUTE type mismatch .........................                x     x
 s08 coordIndex past the end .....................                x     -
 s09 profile lacks Shape level 2 .................                x     x
 s10 4.1 node in a 4.0 file ......................           x    x     x  (hint deletes node)
 s11 X_ITE-only node .............................           x          x  (hint deletes node)
 s12 invisible and far away ...................... no rung fires; only a render or an eye can
 s13 duplicate DEF ...............................           x    x     -
 s14 ROUTE field typo ............................                x     x
 s15 HAnim 1.x joint name ........................                w
```

**Valid is not visible:** s12 passes R2, R3 and R4 with zero diagnostics and draws nothing a person can see; only R6 or a human can say so. **Valid is not placed:** a Box 1,000,000 units away is as legal as one at the origin; no rung compares positions with a viewpoint. **Valid to WHICH schema** is section 6.

`s15` shows that a gate can pass a scene whose joint names no animation tool will bind. Warnings are information, not blockers, unless a profile says otherwise.

## 5. Exact-fix hints: real outputs

The XSD says what is wrong ("Element 'Box': This element is not expected"). A hint says where the Box may go and the edit that puts it there (`src/validation/hints.py`, 1,127 lines; it draws on X3DUOM `acceptableNodeTypes`, a 154 KB table of placements the XSD itself accepted, and the XSD message text). One hint, verbatim from `gate()` on scene s05 (ROUTE before DEF):

```json
{"source": "semantic", "check": "route-before-def", "rule": "route-before-def",
 "node": "ROUTE", "path": "/X3D/Scene/ROUTE[1]", "line": 5, "field": "fromNode",
 "message": "ROUTE comes before DEF='Clock'. Move it to the end of Scene, after the nodes it names.",
 "suggested_fix": {"op": "move", "path": "/X3D/Scene/ROUTE[1]", "to_path": "/X3D/Scene"},
 "confidence": "exact", "error_index": 0}
```

`suggested_fix.op` is one of 10 operations: `set_attribute`, `remove_attribute`, `rename_attribute`, `rename_element`, `move`, `wrap`, `remove_element`, `insert_element`, `add_components`, `swap_def_use`. `confidence` took two values in my run: `exact` (one legal answer) and `choice` (several legal answers, one picked). Six more (**[C]**, `x3d_mcp fork b4efcd3`):

| scene | rule | message (verbatim, trimmed) | op | confidence |
|---|---|---|---|---|
| s02 | `wrong-parent` | Transform has no field that takes a Box. Move it into the sibling `<Shape>` (field geometry). | `move` | choice |
| s03 | `colour-out-of-range` | the values look like 0..255, so they were divided by 255. Use diffuseColor='0 0.4 1'. | `set_attribute` | choice |
| s04 | `unknown-attribute` | Material has no field 'roughness'; remove it. (PhysicalMaterial has a field 'roughness') | `remove_attribute` | choice |
| s06 | `use-before-def` | Swap them: put the DEF node where the first USE is, and a USE where the DEF was. | `swap_def_use` | exact |
| s09 | `profile-component` | Add `<component name='Shape' level='2'/>` to `<head>`. | `add_components` | exact |
| s14 | `route-field` | fromField='fraction_change' is not a usable output field of TimeSensor. Use 'fraction_changed'. | `set_attribute` | exact |

The s04 hint removes the field and names the node that owns it. Whether you wanted `PhysicalMaterial` is intent, and intent is not in the file.

**The apply loop** (`exact_fix_hints(apply=true)`, Python `repair_with_hints`) applies hints one at a time and re-checks after each. Over the sixteen scenes, **[C]**:

| outcome | scenes | n |
|---|---|---|
| already passes the gate | s00, s12, s15 | 3 |
| invalid, ends valid by a non-destructive edit | s02, s03, s04, s05, s06, s07, s09, s14 | 8 |
| invalid, ends valid **because an element was deleted** | s10 (GaussianSplats), s11 (BlendMode) | 2 |
| invalid, loop cannot fix | s01 (not XML), s08 (no hint for an index error), s13 (`suggested_fix` is null) | 3 |

For s10 the right repair is in `repair_x3d`: it raised `version` 4.0 to 4.1 and added `<component name='GaussianSplats' level='1'/>`. For s11 `repair_x3d` refuses (`unfixable: not an X3D node in any bundled X3DUOM`). **A loop that reports `valid_after: true` has told you nothing about what was lost until you read `applied`.** And `repair_x3d` has its own gap, **[C]**:

| scene | `repair_x3d` changes | `remaining` says | `validate_semantic` still says |
|---|---|---|---|
| s05 ROUTE before DEF | none | `schema_valid: true, profile_ok: true` | 2 `route-before-def` errors |
| s08 index past the end | none | `schema_valid: true, profile_ok: true` | 1 `index-out-of-range` error |

`remaining` re-validates the XSD and the profile only. Run the semantic layer on the repaired text.

**The author's evaluation, re-run.** `evaluation/exact_fix_eval.py` mutates seed scenes with 12 fault classes (seed 20261029, 45 cases per class) and calls no model. I re-ran it at `b4efcd3` in a scratch checkout (11 s; 24 seeds, 10,294 sites, 540 cases, 577 errors):

| measure | repo doc (PR #14 time) | re-run at `b4efcd3` |
|---|---|---|
| errors with a `suggested_fix` | 552 / 570 (96.8%) | 558 / 577 (96.7%) |
| valid after `repair_x3d` alone | 81 / 540 (15.0%) | 76 / 540 (14.1%) |
| valid after `repair_x3d`, then the hint loop | 523 / 540 (96.9%) | 522 / 540 (96.7%) |
| valid only because an element was removed | 12 / 540 (2.2%) | 15 / 540 (2.8%) |
| loop returns the seed exactly | 257 / 540 (47.6%) | 268 / 540 (49.6%) |

The columns differ by one seed scene (24 here, 25 in the doc) and by rules PR #15 added later. The mutation classes and the hint rules share one author; the doc says so, and my re-run uses the same script, so both measure the faults the hints were designed for. By class, `missing-required` is the weak one (60.0% of errors get a fix: `meta` and `component` values carry intent) and `wrong-field` restores the seed 0.0% of the time (it writes an explicit `containerField` where the seed relied on the default: equivalent, not byte-equal). **[C]** for the re-run, **[L]** for the doc column.

## 6. Valid to WHICH schema

"Valid" without a schema name is not a claim. The validator knows five vocabularies, and they disagree at the edges.

| vocabulary | bundled file (sha256 prefix) | what it knows | used by |
|---|---|---|---|
| `X3D XSD 4.0` | `x3d-4.0.xsd` (0509fa5bd601) | ratified 4.0 elements and attributes | R2 for `version="4.0"` and for any 3.x |
| `X3D XSD 4.1` | `x3d-4.1.xsd` (1a7935caa7e6) | the 4.1 draft; default when no version | R2 for 4.1, none, unknown |
| `X3DUOM 4.0` / `4.1` | `X3dUnifiedObjectModel-*.xml` (7e426a238656, 4fc10e8e15c0) | 260 / 267 concrete nodes with field types, defaults, `acceptableNodeTypes` | R3 field lookups, R4 hints, `describe_node` |
| JSON Schema 4.0 | `x3d-4.0-JSONSchema.json` (cb265672c4b6) | X3D JSON encoding, 4.0 only | `validate_json` |
| X3D Ontology 4.0 / 4.1 | `X3dOntology4.*.ttl` | classes and properties for RDF, SHACL | the semantic-web tools (chapter 05) |

Counted from the files, **[C]**: X3DUOM 4.1 has seven concrete nodes that X3DUOM 4.0 lacks (`EnvironmentLight`, `FontLibrary`, `GaussianSplats`, `HAnimPose`, `InlineGeometry`, `RenderedTexture`, `Tangent`) and none the other way. The XSD pair differs by the same names (plus one local element); `EnvironmentLight` appears as an element name in both XSD files, yet a `version="4.0"` scene containing it fails (note: "Node 'EnvironmentLight' is not in X3D 4.0; it was added in X3D 4.1") and passes when forced to 4.1. The XSD file and X3DUOM 4.0 therefore disagree about that node; the validator follows X3DUOM for its version note and the XSD for the verdict. The cause of the XSD side I did not chase (**[S]**).

How the version attribute picks the schema (`validate.resolve_xsd_version`), **[C]**:

| declared | schema used | note returned |
|---|---|---|
| `4.0` | 4.0 | none |
| `4.1` | 4.1 | none |
| `3.0` to `3.3` | 4.0 | "X3D 3.3 has no bundled schema; validated against X3D 4.0, of which X3D 3.3 is a subset." |
| missing | 4.1 | "No version attribute; validated against X3D 4.1." |
| anything else (`9.9`) | 4.1 | "Unknown version '9.9'; validated against X3D 4.1." |
| `validate_xml(text, version="4.1")` | 4.1, whatever the file says | none |

At the fork base `74da0ec` there was one XSD, 4.1, for every file: s10 (a 4.1-only node in a file that declares 4.0) came back **valid**. At `b4efcd3` it is invalid under 4.0 and valid when forced to 4.1. That is the same scene giving two verdicts, and both were "valid XSD" claims until a version and a commit were attached.

**X_ITE extensions.** [The X_ITE masterclass](../x_ite/MASTERCLASS.md) counts 26 X_ITE-only node types, among them `BlendMode`, `DepthMode`, `InstancedShape` and `SpecularGlossinessMaterial` (read, **[L]**). A membership scan found none of the four in either bundled XSD or X3DUOM, and `BlendMode` in neither `Web3dExtensions*.xsd` nor the 4.1 ontology (**[C]**, regex over the files). Scene s11: XSD invalid, `repair_x3d` unfixable, the hint loop "fixes" it by deleting the node. A scene using an X_ITE extension is X_ITE-valid, not X3D-valid; say which, and do not let a repair tool delete it.

**JSON.** `validate_json` uses the 4.0 JSON Schema: `@version` accepts only 3.0 to 3.3 and 4.0, so a 4.1 document is rejected with `X3D/@version: '4.1' is not one of ['3.0', '3.1', '3.2', '3.3', '4.0']` (**[C]**; my fixture also lacked the required `encoding` key, which the same run reports, so read only the version line as the finding).

**Oversize.** `valid: false` is not always "invalid". An 11,700,036-byte `GaussianSplats` start tag returned in 1,763 ms with:

```json
{"valid": false, "checked": false, "verdict": "not-checkable-at-this-size",
 "errors": ["Not checkable at this size: GaussianSplats (line 2, 11,700,036 bytes) is larger than libxml2's 10,000,000-byte start-tag limit, so the XSD check did not run ..."],
 "schema_version": "4.1"}
```

`checked: false` means no verdict was reached; a consumer that tests only `valid` cannot tell an unchecked scene from an invalid one. (**[C]**, `x3d_mcp fork b4efcd3`, `X3D XSD 4.1`.)

## 7. The gates

### 7.1 loomkit: witnesses, accept, receipt

`x3d.loom@162ab18:kit/loomkit` is a standard-library-only gate kit around the validator. A **candidate** is the sha256 of the sorted file inventory of a folder; a **witness** is one JSON record (`loom.witness/1`) bound to that hash; **accept** decides from a named profile, never from a score. Status (`pass | fail | error | not_run | not_applicable | deferred`) and grade (`C | L | S`) are separate axes.

```text
 candidate folder --sha256 inventory--> subject_sha256
        |
        +-- loomkit traps | pagetraps | grammar | foldback | sci | play | physics | ...
        |      each writes evidence/<name>.json {status, grade, instrument, measurements,
        |                                        coverage, limitations, evidence[], subject}
        v
   loomkit accept --profile P     one record per required witness, else a stable code:
        |                         MISSING_WITNESS  STALE_WITNESS  WITNESS_NOT_PASS
        |                         UNMEASURED_REQUIRED_WITNESS  COVERAGE_REQUIRED  EVIDENCE_DRIFT
        v
   loomkit receipt -> receipt.json (unsigned; candidate hash, witness hashes, not_run, prev)
        v
   loomkit verify-receipt         RECEIPT_DRIFT if any byte of the body changed
```

The CLI has 17 sub-commands at `162ab18`: `candidate`, `traps`, `pagetraps`, `grammar` (writes two witnesses, `grammar` and `meaning`), `foldback`, `sci`, `metalsite`, `hepevent`, `play`, `physics`, `command`, `record`, `accept`, `receipt`, `verify-receipt`, `sweep` (the leak sweep; the source tree is never modified) and `picture`. The brief for this chapter named gates xsd, loom, fact, privacy, witness and scene; **none of those names exists** in `cli.py` (**[C]**). Nearest: `grammar` (XSD), `meaning` (semantic), `sweep` (privacy), `command`/`record`/`accept` (witnesses), `candidate` (scene folder identity).

Exit codes, observed **[C]**: `0` whenever a witness was written, **including `status: fail`**; `1` for a rejection (`{"rejected": CODE}`); `2` for an instrument error. The docstring's "0 = passed" holds for `accept` and `verify-receipt`, not for the producers. Read the status of a witness, not the exit code.

**A real run** (three scratch scenes, loomkit `162ab18`, fork `b4efcd3`, 2026-11-14, **[C]**):

| step | result |
|---|---|
| `traps` on s00, s02, s05 | `fail`: 2 errors, both `route-before-def` on s05; s02 gets none |
| `grammar` on the same | `grammar` fail (s02: 1 XSD error); `meaning` fail (s02: 1 error 1 warning; s05: 2 errors); both name commit `b4efcd39b989...`, `dirty: false` |
| `accept`, bad candidate | `{"rejected": "WITNESS_NOT_PASS", "detail": "grammar: fail"}`, exit 1 |
| s00 only, three witnesses, `accept` | `accepted`, grade `C` on all three, `visible_not_run: ["eyes"]` |
| append a comment to s00, `accept` | `{"rejected": "STALE_WITNESS", "detail": "grammar"}`, exit 1 |

Two instruments, two blind spots: the loomkit trap and the fork's semantic rule of the same name caught s05 independently; the XSD caught s02, which no trap looks for.

**The adapter fails closed.** `kit/loomkit/grammar.py` imports `src.validation.validate` in the fork's own venv. At `b4efcd3` that module does `from validation import listvalues, oversize`, which needs `src/` on `sys.path`. In a venv without an editable install the first run gave `InstrumentError ... No module named 'validation'`, exit 2. A one-line `.pth` file fixed it. A broken instrument is `error`, never `pass`.

**Controls.** `kit/tests/test_gates.py` (run on a scratch copy; it writes `last-run.json`) printed, for both `optimized=False` and `python -O`: "82 negative controls caught with the intended code; 15 trap rules, 8 page-trap rules and 10 page forms ... pass their clean fixture and catch their failing one", in 3.8 s. A control rejected for the wrong reason counts as a broken test. **[C]**.

### 7.2 The x3d-blender-io conformance suite

`x3d-blender-io@ab99988:tests/suite` builds a Blender scene of cases, exports it with the add-on, judges the file with a standard-library validator (`validate_x3d_export.py`, 1,702 lines, `--selftest`), and can load it in X_ITE (`x3d_browser_check.py`, needs Playwright). Verdicts: `PASS`, `FAIL` (CORE failed, exit 1), `WARN` (FIDELITY), `MISSING` (ROADMAP, expected), `NEW` (ROADMAP passed), `SKIP`, `ERROR`. Without Blender I could verify, **[C]**:

| item | value | how |
|---|---|---|
| catalogue (suite 2.0.0) | 195 = 148 CORE + 21 FIDELITY + 26 ROADMAP | tier cells in `docs/test-suite/x3d_case_catalog.md` |
| recorded, add-on v2.6.1, Blender 5.2.2 | CORE 143 pass 4 fail; FIDELITY 2 pass 19 warn; ROADMAP 26 missing (194 cases) | embedded data of `reports/x3d_validation_report.html` |
| same suite on `main` 0c48976, Blender 5.1.0 | CORE 143 / 4; ROADMAP 21 missing 5 new | `reports/..._origin_main_0c48976.html` |
| with the phantom-sphere fix | CORE **147 / 147**; ROADMAP 21 missing 5 new | `reports/..._with_phantom_fix.html` |
| validator self-test | 27 checks pass | `validate_x3d_export.py --selftest` |

"148/148" is **not a recorded result**: the scoreboards cover the 194-case scene (147 CORE) and end at 147/147; the catalogue now lists 148 CORE and a 148/148 scoreboard needs Blender (**[S]**). The CI job ("Export conformance suite (Blender 5.1.2)") is written to fail on any CORE failure; I read it, I did not run it. The suite's `integrity.*` cases (DEF unique, USE resolves earlier, ROUTE targets exist, numbers finite, coordIndex valid, interpolators well-formed, SFColor in 0..1) are the R3 families written a second time by a different author in a different language: a cheap cross-check on the first.

## 8. The pin rule and the validator register

**The rule.** Quote a validator as `x3d_mcp fork <sha7>` (a commit, never a branch, never "latest", never "the fork"), with the schema version it judged against. A gate witness records `commit`, `branch`, `dirty` and the interpreter path in its instrument block and adds the limitation "Fork commit X on branch Y; not the family pin unless they match". The family-wide pin was decided as a tag, `loom-pin-2026-11-01` (`x3d.loom@162ab18:GLOSSARY.md`); the `x3d_mcp` checkout has **0 tags** (**[C]**, `git tag`), so every recorded run names a commit instead. When two pins have byte-identical validator code, re-scoring costs nothing and changes nothing; when they differ, re-score.

The register, from recorded `evidence/grammar.json` records in `x3d.loom@162ab18:runs/` (24 grammar witnesses) and from `git log` of the checkout (**[C]**):

| pin | commit date | commit subject | recorded use | validator code vs `b4efcd3` |
|---|---|---|---|---|
| `x3d_mcp upstream 74da0ec` | 2026-08-05 | upstream main, Merge PR #21 | fork base; 19 rule ids, 10 checks, one XSD (4.1) | differs (this chapter's base column) |
| `x3d_mcp fork fa0b389` | 2026-10-17 | validate_semantic: add RigidBodyPhysics checks (X-09, X-10) | **15 runs**, 2026-11-04 to 2026-11-06 (data-city x2, scientific x2, chirp x2, electron-cloud x2, kerr2 x2, turing-garden x2, living-heart, manifold, vortex-sound) | predates the ROUTE-order, colour-range and HAnim checks of 2026-10-30; not diffed here |
| `x3d_mcp fork 788041c` | 2026-10-30 | Add ROUTE order, colour range and H-Anim name checks; report libxml2 engine give-ups by value | cited as the commit that gained `route-before-def` in the loomkit trap comment; no recorded grammar witness uses it | `src/validation` identical to `327c5c4` |
| `x3d_mcp fork 327c5c4` | 2026-11-01 | Merge PR #16 | **4 runs** on 2026-11-06 (drift, platformer, zinc-scenes, zinc-scenes-v2) | `.py` identical |
| `x3d_mcp fork 13121b6` | 2026-11-03 | MCP and friends playground | **1 run** (brain, 2026-11-06) and 21 scenes in the x3d.mol project | `.py` identical; 4 schema-data files differ later |
| `x3d_mcp fork b4efcd3` | 2026-11-13 | Merge PR #17 | this chapter | itself |
| no commit field | n/a | n/a | 4 grammar witnesses (hep-demo x2, zinc-site, zinc-structures) carry no fork identity | not the fork |

"Identical" is `git diff --quiet` over `semantic.py`, `validate.py`, `hints.py`, `repair.py` (13121b6 to b4efcd3), plus an empty `git diff --stat -- src/validation` for 788041c to 327c5c4 and 327c5c4 to 13121b6. Consequence: **verdicts recorded at 327c5c4 and 13121b6 are the verdicts of b4efcd3** for the XSD, semantic, hint and repair layers; those recorded at `fa0b389` are not (**[C]** the diffs; **[L]** the consequence, since I re-scored no recorded run and 13121b6 to b4efcd3 added schema data for the semantic-web tools).

Other commits named in older working notes (`cf84f64`, `d5598c4`, `8c0a457`, `56809ca`, `535fdac`, `c9c9788`, `acdf5c4`) exist in the checkout, dated 2026-10-08 to 2026-10-30; that they served as pins for particular experiments is **[S]**, carried from private notes and not re-checked, and no number in this chapter depends on them.

## 9. Blind spots, ranked

| rank | blind spot | evidence | what would cover it |
|---|---|---|---|
| 1 | **Visible and placed.** A scene can be valid, clean and show nothing | s12: R2 to R5 silent | a render check (R6), a viewpoint-versus-bounds rule, a person |
| 2 | **Intent.** The loop returns the seed exactly in 268 of 540 cases | re-run of `exact_fix_eval.py` (49.6%) | a spec in the file; review `applied` |
| 3 | **Deletion as repair** (15 of 540; s10, s11) | `valid_after: true` with `remove_element` | read `applied`; use `repair_x3d` for version problems |
| 4 | **`remaining` is not the semantic gate** | s05, s08 | run `validate_semantic` after every repair |
| 5 | **Errors with no fix:** index range (s08), duplicate DEF (s13), bad XML (s01) | `hints: 0` or `suggested_fix: null` | a new hint rule (section 10) |
| 6 | **Vocabulary outside the bundle:** X_ITE-only nodes fail every rung | s11; no match in XSD, X3DUOM, extension XSDs, ontology | an explicit extension profile; never auto-delete |
| 7 | **libxml2 limits:** 10,000,000-byte start tag; the pattern engine gives up on long lists | oversize probe; docs: a bad colour from about the 13th list entry | `listvalues.py` (linear-time reader), chunking |
| 8 | **One XSD error per parent** | EXACT-FIX-HINTS.md | loop to a fixpoint (the apply loop does) |
| 9 | **Rules written to one renderer.** `route-before-def` exists because X_ITE drops an early ROUTE | ROUTE-COLOUR-HANIM-CHECKS.md (it adds that the X3D Schematron also calls it an error) | label each rule: spec, schema, or X_ITE behaviour |
| 10 | **Same-author corpora** | EXACT-FIX-HINTS.md; my re-run uses the same script | an independent defect corpus, real user scenes |
| 11 | **JSON knows 4.0 only** | version enum | none in the bundle |
| 12 | **Render rung not run;** the README pins `X_ITE 16.4.3` | read, not run | a rig with a browser; chapter 06 |
| 13 | **Cross-file references** (Inline, ExternProto, textures) | not tested | **[S]**: assume unchecked |

## 10. How to write a new rule

The rule I wrote for this chapter closes blind spot 1 in a small way: a `Material` with `transparency >= 1` draws nothing. It lives in a scratch copy, not in the fork.

```python
_POINTING_SENSORS = {"TouchSensor", "PlaneSensor", "CylinderSensor", "SphereSensor", "ProximitySensor"}

def _check_invisible_material(scene):
    diagnostics = []
    for el in scene.iter("Material"):
        if el.get("USE"):
            continue
        try:
            t = float(el.get("transparency", "0"))
        except ValueError:
            continue
        if t >= 1.0:
            parent = el.getparent()                       # Appearance
            shape = parent.getparent() if parent is not None else None
            if shape is not None and shape.getparent() is not None and any(
                    _local_tag(sib) in _POINTING_SENSORS for sib in shape.getparent()):
                continue                                  # an invisible hit area is a known idiom
            diagnostics.append(Diagnostic(
                level="warning", check="invisible-material",
                message="Material transparency='1' draws nothing: the Shape is valid but cannot be seen. "
                        "Lower transparency below 1, or remove the Shape.",
                node_tag="Material", def_name=(shape.get("DEF", "") if shape is not None else "")))
    return diagnostics
# then add _check_invisible_material to _ALL_CHECKS in src/validation/semantic.py
```

| step | what to do | what happened here |
|---|---|---|
| 1 | Start from a scene that fails in the field; name the incident | s12: valid, clean, invisible |
| 2 | Write `_check_x(scene) -> list[Diagnostic]`; level honestly (error only for what a conforming viewer refuses or drops) | `warning`: a transparent box is legal |
| 3 | Register it in `_ALL_CHECKS`; add a positive and a negative test | 23 to 24 functions; two tests |
| 4 | **Run it over every scene you own** before anyone else does | 2 hits in 14 scenes: a deliberate hit-area `Box size='8 2 .001'` beside a `TouchSensor`, and a deliberately faulted fixture |
| 5 | Refine or demote; add a test for the exemption | exempt a Shape beside a pointing-device sensor: 1 hit left (the fixture, `transparency='1.2'`) |
| 6 | If an exact fix exists, add a hint rule in `hints.py` with honest `confidence`; else leave `suggested_fix` null | none added: intent decides |
| 7 | Add a class to `evaluation/exact_fix_eval.py` if a hint exists; write the note in `docs/`; record the new commit in the pin register | scratch patch only |

Result, **[C]** (scratch copy of `x3d_mcp@b4efcd3`, 2026-11-14): the two semantic test files went from 148 to 151 passed in 1.70 s; s00 stays at 0 diagnostics; s12 reports `invisible-material`. A warning does not stop `gate()`. A gate that refuses invisible scenes is a profile decision, not a rule-level one.

## Heuristics

| ID | Rule (imperative, at most 30 words) | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-VAL-1 | Never write "valid" alone; write validator commit, schema version and the call that ran. A verdict without both cannot be re-run. | C | s10 is valid at base 74da0ec and invalid at b4efcd3 for the same bytes | `x3d_mcp fork b4efcd3` vs `x3d_mcp upstream 74da0ec` |
| H-VAL-2 | Run the semantic layer after the XSD, always. XSD-valid is not gate-clean. | C | 8 of 15 faulty scenes pass the XSD; 6 of those 8 carry a semantic error | `x3d_mcp fork b4efcd3`, `X3D XSD 4.0` |
| H-VAL-3 | Read `checked` before `valid`. `valid: false, checked: false` means no verdict, not a failure. | C | 11,700,036-byte start tag returned `not-checkable-at-this-size` | `x3d_mcp fork b4efcd3`, libxml2 2.14.6 |
| H-VAL-4 | After any automatic repair, read `applied`; a loop that reports valid by deleting a node has lost content. | C | s10 and s11 end valid by `remove_element`; 15 of 540 eval cases | `x3d_mcp fork b4efcd3` `exact_fix_hints(apply=true)` |
| H-VAL-5 | Do not read `repair_x3d` `remaining` as clean; re-run `validate_semantic` on the repaired text. | C | s05 and s08: `schema_valid: true` while a semantic error stands | `x3d_mcp fork b4efcd3` `repair_x3d` |
| H-VAL-6 | Declare the version in every file; an undeclared version is judged as 4.1, a declared 3.x as 4.0. | C | `resolve_xsd_version` table; s10 | `x3d_mcp fork b4efcd3`, `X3D XSD 4.0`, `X3D XSD 4.1` |
| H-VAL-7 | Treat X_ITE-only nodes as an extension profile; never let a repair delete them to reach "valid". | C | s11 BlendMode: unfixable in `repair_x3d`, deleted by the hint loop | `x3d_mcp fork b4efcd3`, `X3DUOM 4.1`, `X3DUOM 4.0` |
| H-VAL-8 | Pin the commit, and diff the validator code between pins before re-scoring: identical code means identical verdicts. | C | `src/validation` identical across 788041c, 327c5c4, 13121b6; `.py` identical to b4efcd3 | `x3d_mcp fork b4efcd3` (git diff) |
| H-VAL-9 | Keep two instruments with different blind spots on the same candidate; one agreeing and one disagreeing gate is information. | C | loomkit trap and fork semantic both caught s05; only the XSD caught s02 | loomkit `162ab18`, `x3d_mcp fork b4efcd3` |
| H-VAL-10 | Run a new rule over every scene you have before landing it; a legitimate idiom will trigger a first draft. | C | invisible-material hit a deliberate hit-area `Box` in 1 of 14 scenes | `x3d_mcp fork b4efcd3` scratch patch |
| H-VAL-11 | Read the status of a gate witness, not the process exit code; a failing producer can exit 0. | C | `loomkit traps` printed `status: fail` with exit 0; `accept` exited 1 | loomkit `162ab18` |
| H-VAL-12 | Count rules with a stated definition (ids, sites, functions); a bare "62 rules" is not comparable. | C | 51 ids, 61 sites, 24 functions, 72 across layers at one commit | `x3d_mcp fork b4efcd3` (ast) |

## Drills

### D-VAL-1 Count the rules two ways
- **Level:** L2
- **Task:** At `x3d_mcp@b4efcd3` count the distinct rule ids `src/validation/semantic.py` reports and the check functions `semantic_diagnostics` runs; repeat at `74da0ec`. State your definition.
- **Verify:** parse with Python `ast`; take string constants in the second argument of `Diagnostic(...)` and of the `check`/`add`/`err`/`report` helpers, add the f-string ids `hanim-joint-name` and `hanim-segment-name`; read `_ALL_CHECKS`.
- **Answer:** 51 ids and 24 functions (23 in `_ALL_CHECKS` plus `_check_profile_components`) at `b4efcd3`; 19 ids and 10 functions at `74da0ec`. With `splat_arrays.py` the union is 53; with the `inspect_splats.py` ids, 72.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3` and `x3d_mcp upstream 74da0ec`, Python `ast`.

### D-VAL-2 Walk a scene up the ladder
- **Level:** L2
- **Task:** Write s05 (the control scene with both ROUTEs above the TimeSensor and the interpolator). Run `validate_xml`, `semantic_diagnostics` and `gate`. Which rung fails first, what is the hint, does the fork base agree?
- **Verify:** `from validation.validate import validate_xml`, `from validation.semantic import semantic_diagnostics`, `from validation.hints import gate`, with `src/` on `sys.path`.
- **Answer:** `validate_xml` says valid for 4.0. `semantic_diagnostics` returns 2 `route-before-def` errors (`Clock`, `Spin`). `gate` returns `valid: false, stage: "semantic"` and two hints (`move` to the end of `Scene`, `exact`). The base validator reports 0 semantic errors.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3`, `X3D XSD 4.0` (0509fa5bd601); base column from `x3d_mcp upstream 74da0ec`.

### D-VAL-3 Same bytes, two schemas
- **Level:** L2
- **Task:** Declare `version="4.0"` and add one `GaussianSplats` node (`positions`, `scales`, `orientations`, `opacities`, `sphericalHarmonicsDegree0Coef0`). Validate as written, then with `version="4.1"` passed to `validate_xml`; then run `repair_x3d` and `exact_fix_hints(apply=true)` and compare what each did.
- **Verify:** `validate_xml(text)`, `validate_xml(text, version="4.1")`, and the two tool functions.
- **Answer:** invalid under 4.0 with a note that the node arrived in 4.1; valid forced to 4.1. `repair_x3d` raises the version to 4.1 and adds the `GaussianSplats` component at level 1. The hint loop reaches "valid" by deleting the node (`unknown-node`, `remove_element`).
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3`, `X3D XSD 4.0`, `X3D XSD 4.1`.

### D-VAL-4 Add a rule, then break it
- **Level:** L3
- **Task:** In a scratch copy, add warning `invisible-material` for `Material transparency >= 1`, with a positive and a negative test. Run every example and fixture scene through it, find the false positive, and add an exemption with a test.
- **Verify:** `pytest tests/test_semantic.py tests/test_scene_semantics_fixtures.py`; a loop over `examples/`, `output/`, `tests/fixtures/` calling `semantic_diagnostics`.
- **Answer:** first draft: 2 of 14 scenes hit, `MaterialModulator.x3d` (a transparent `Box size="8 2 .001"` beside a `TouchSensor`: a hit area) and `LabScene41Faulted.x3d` (`transparency='1.2'`, a deliberate fault). Exempting a Shape with a pointing-device sensor among its siblings leaves 1 hit. Tests: 148 passed before, 151 after.
- **Checked:** 2026-11-14 scratch copy of `x3d_mcp@b4efcd3`, pytest 9.2.0.

### D-VAL-5 A gate that rejects, accepts and goes stale
- **Level:** L3
- **Task:** With loomkit `162ab18` and the fork venv, make a candidate of s00, s02 and s05; write `grammar`, `meaning` and `traps` witnesses; `accept` against a profile requiring all three. Then keep only s00, re-run, accept, append a comment to s00 and accept again.
- **Verify:** `python3 -m loomkit grammar|traps|accept CAND --evidence EV ...` from `kit/`; the fork needs `.venv/bin/python` and `src/` importable.
- **Answer:** first accept: `WITNESS_NOT_PASS grammar: fail`, exit 1 (traps: 2 `route-before-def`; grammar: 1 XSD error on s02; meaning fail). s00 alone: `accepted`, grades `C`, `visible_not_run: ["eyes"]`. After the edit: `STALE_WITNESS grammar`. If the fork venv cannot import `validation`, grammar exits 2 with `InstrumentError`, never 0.
- **Checked:** 2026-11-14 loomkit `162ab18`, `x3d_mcp fork b4efcd3`.

### D-VAL-6 The conformance suite, without Blender
- **Level:** L1
- **Task:** How many cases are in the x3d-blender-io catalogue, how many CORE, what does the last recorded CORE scoreboard say, and is "148/148" recorded?
- **Verify:** count tier cells in `docs/test-suite/x3d_case_catalog.md`; parse the `DATA` object in the three reports under `docs/test-suite/reports/`; run `validate_x3d_export.py --selftest`.
- **Answer:** 195 cases, 148 CORE, 21 FIDELITY, 26 ROADMAP. Recorded CORE: 143 pass 4 fail, then 147 / 147 (194-case scene). No 148/148 report exists. The self-test passes 27 checks.
- **Checked:** 2026-11-14 `x3d-blender-io@ab99988`, Python 3.13.18.

### D-VAL-7 What "not checkable" looks like
- **Level:** L2
- **Task:** Build a document with one `GaussianSplats` attribute of about 11.7 MB of numbers and validate it. Which keys say the result is not a verdict?
- **Verify:** `validate_xml(text)`; read `checked`, `verdict`, `oversize`.
- **Answer:** `valid: false`, `checked: false`, `verdict: "not-checkable-at-this-size"`; the error names libxml2's 10,000,000-byte start-tag limit and `X3D_MCP_XML_HUGE=on` as the opt-in; 1,763 ms.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3`, libxml2 2.14.6.

## Honest limits

- **R6 was not run.** `render_image` needs Playwright and Chromium. **[C]** that no R2 to R5 rung fires on s12; **[S]** on how it looks.
- **Sixteen scenes, one author.** They show the ladder's shape, not a defect distribution.
- **Rule counts depend on a definition.** I count 51 ids in `semantic.py`; the masterclass's 62 at `13121b6` is a differently defined number I could not rebuild. The code supports 51/53/72 under stated definitions; the 62 is **[L]**.
- **Docs versus re-run.** The repo doc's exact-fix figures (96.9% after, 15.0% before) differ from my re-run (96.7%, 14.1%). The re-run is tied to a commit; the doc column is **[L]**.
- **loomkit scope.** I ran `traps`, `grammar`, `accept` and the controls. I read but did not run `receipt`, `sweep`, `physics`, `hepevent`, `sci`, `play`, `foldback`, `metalsite`, `picture`.
- **The pin tag** `loom-pin-2026-11-01` is named in the loom docs; the checkout has no tags, so whether it exists upstream is **[S]**.
- **Blender suite not re-run** (no Blender): 147/147 is recorded, 148/148 is not.
- **One interpreter, one libxml2 build** (the rig line); others were not tried.
- **Cross-file references** (Inline, ExternProto, textures) were not probed.
- **Warm timings are repeat-call medians;** cold costs are the 1.4 to 1.5 s schema compile and about 50 ms for the first semantic call.

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-VAL-1 | distinct rule ids in `semantic.py` | 51 | C | `x3d_mcp fork b4efcd3`, Python `ast` | x3d_mcp@b4efcd3:src/validation/semantic.py |
| N-VAL-2 | same, at the fork base | 19 ids, 10 check functions, 24 report sites | C | `x3d_mcp upstream 74da0ec`, Python `ast` | x3d_mcp@74da0ec:src/validation/semantic.py |
| N-VAL-3 | rule ids across semantic, splat arrays, splat inspector | 72 (51 + 2 + 19) | C | `x3d_mcp fork b4efcd3`, Python `ast` | x3d_mcp@b4efcd3:src/validation/{semantic,splat_arrays}.py, src/transfer/inspect_splats.py |
| N-VAL-4 | hint rule ids and edit operations | 19 and 10 | C | `x3d_mcp fork b4efcd3`, regex and `ast` | x3d_mcp@b4efcd3:src/validation/hints.py |
| N-VAL-5 | full test suite | 1,367 passed, 27 skipped, 1,394 collected, 104 s | C | pytest 9.2.0, Python 3.13.18, no Chromium | x3d_mcp@b4efcd3:tests/ |
| N-VAL-6 | concrete nodes in X3DUOM 4.0 and 4.1 | 260 and 267; 7 only in 4.1 | C | `X3DUOM 4.1` (4fc10e8e15c0), `X3DUOM 4.0` (7e426a238656) | x3d_mcp@b4efcd3:src/validation/schemas/X3dUnifiedObjectModel-4.{0,1}.xml |
| N-VAL-7 | XSD cold compile | 1,456 ms (4.0), 1,547 ms (4.1) | C | `x3d_mcp fork b4efcd3`, libxml2 2.14.6, 4 vCPU 2.30 GHz | scratch timing run, 2026-11-14 |
| N-VAL-8 | warm repeat-call median, 12-line scene | 0.022 ms XSD, 0.314 ms semantic, 0.371 ms gate | C | `x3d_mcp fork b4efcd3`, 300 runs each | scratch timing run, 2026-11-14 |
| N-VAL-9 | faulty scenes passing the XSD, and carrying a semantic error | 8 of 15, and 6 of those 8 | C | `x3d_mcp fork b4efcd3` | 15 scratch scenes, section 4 |
| N-VAL-10 | hint loop on the 13 invalid scenes | 10 end valid, 2 of them by deleting a node, 3 not fixed | C | `x3d_mcp fork b4efcd3` `exact_fix_hints(apply=true)` | scratch run, 2026-11-14 |
| N-VAL-11 | exact-fix evaluation re-run | 540 cases, 577 errors; 14.1% before, 96.7% after, 49.6% seed-exact, 2.8% by removal | C | `x3d_mcp fork b4efcd3`, seed 20261029 | x3d_mcp@b4efcd3:evaluation/exact_fix_eval.py |
| N-VAL-12 | exact-fix numbers in the docs | 96.9% after, 15.0% before, 47.6% seed-exact (570 errors) | L | stated in the repo, not re-derived at its commit | x3d_mcp@b4efcd3:docs/EXACT-FIX-HINTS.md |
| N-VAL-13 | oversize verdict | 11,700,036-byte start tag, `checked: false`, 1,763 ms | C | `x3d_mcp fork b4efcd3`, `X3D XSD 4.1` | scratch probe, 2026-11-14 |
| N-VAL-14 | loomkit controls | 82 negative controls, 15 trap rules, 8 page-trap rules, 10 page forms, both `-O` modes, 3.8 s | C | loomkit `162ab18` | x3d.loom@162ab18:kit/tests/test_gates.py |
| N-VAL-15 | loomkit sub-commands | 17 | C | loomkit `162ab18`, read | x3d.loom@162ab18:kit/loomkit/cli.py |
| N-VAL-16 | recorded grammar witnesses per validator pin | fa0b389: 15; 327c5c4: 4; 13121b6: 1; none: 4 (24 total) | C | loomkit `162ab18` evidence records | x3d.loom@162ab18:runs/*/evidence/grammar.json |
| N-VAL-17 | blender-io catalogue | 195 cases: 148 CORE, 21 FIDELITY, 26 ROADMAP | C | `x3d-blender-io@ab99988` catalogue | x3d-blender-io@ab99988:docs/test-suite/x3d_case_catalog.md |
| N-VAL-18 | blender-io recorded CORE scoreboard | 143 pass 4 fail, then 147 / 147 (194-case scene) | C | recorded reports parsed; Blender 5.2.2 and 5.1.0, add-on v2.6.1 | x3d-blender-io@ab99988:docs/test-suite/reports/ |
| N-VAL-19 | blender-io "148/148" | not recorded | S | not run (no Blender here) | x3d-blender-io@ab99988:docs/test-suite/SUITE_COMMENTARY.md |
| N-VAL-20 | new rule scratch patch | tests 148 to 151 passed; false positives 2 to 1 of 14 scenes | C | scratch copy of `x3d_mcp fork b4efcd3` | scratch patch, section 10 |
| N-VAL-21 | masterclass rule count at `13121b6` | 62 (definition not recoverable) | L | stated in the teardown; not reproduced | x3d.docs@f172f67:docs/x3d_mcp/MASTERCLASS.md |

## Sources and provenance

- `x3d_mcp@b4efcd3` (Merge PR #17, 2026-11-13): `src/validation/{validate,semantic,hints,repair,splat_arrays,oversize,listvalues}.py`, `src/tools/validate_tool.py`, `src/validation/schemas/*`, `docs/EXACT-FIX-HINTS.md`, `docs/ROUTE-COLOUR-HANIM-CHECKS.md`, `evaluation/exact_fix_eval.py`, `tests/`. Compared against `74da0ec` (upstream main, 2026-08-05), `fa0b389`, `788041c`, `327c5c4`, `13121b6` by `git log`, `git show` and `git diff`.
- `x3d.loom@162ab18`: `kit/loomkit/{core,cli,grammar,accept,receipt,sweep,traps,pagetraps}.py`, `kit/tests/test_gates.py`, `GLOSSARY.md`, `LOOM-v1.md`, `runs/*/evidence/grammar.json`.
- `x3d-blender-io@ab99988`: `tests/suite/`, `docs/test-suite/` (catalogue, commentary, three HTML reports).
- `x3d.docs@f172f67`: `docs/x3d_mcp/MASTERCLASS.md` (rule table, PR table), `docs/x_ite/MASTERCLASS.md` (X_ITE-only node types).
- Re-run on 2026-11-14 in a scratch virtualenv: AST rule and tool counts, sixteen scenes through every rung, base-versus-head comparison, `repair_x3d` and `exact_fix_hints` across the corpus, the exact-fix evaluation, the full test suite, the oversize probe, loomkit traps, grammar, accept and controls, the blender-io self-test and report parsing, and a scratch rule patch.
- Not re-derived: the 62-rule figure, the pin tag's existence, any Blender run, the render rung. Some older commit names appear in private working notes and are listed in the pin register as unverified uses only. Claims about private data, unpublished material and upstream reports are not made here.
- Siblings: [01 The tether](01-the-tether.md), [02 Loom laws](02-loom-laws.md), [04 MCP for agents](04-mcp-for-agents.md), [05 Semantic layer](05-semantic-layer.md), [06 X_ITE, the oracle](06-xite-the-oracle.md), [10 Blender pipeline](10-blender-pipeline.md).
