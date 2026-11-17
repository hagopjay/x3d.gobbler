# 10. Blender as the studio: x3d-blender-io and the sci-vis knowledge base

> **Say it:** Blender is where a scene is modelled, lit and baked, and the add-on is the door it leaves through; every exit can be gated by a validator and a second renderer, a re-export is valid even when the source was not, so what you score is fidelity, with each number tied to a named rig. **[C]**

| field | value |
|---|---|
| chapter code | `BLE` |
| prerequisites | [01 The tether](01-the-tether.md) for the loop; [03 Validator and gates](03-validator-and-gates.md) for `validate_xml`; [06 X_ITE, the reference renderer](06-xite-the-oracle.md) for the reference arm; [08 The Babylon bridge](08-babylon-bridge.md) for the second renderer |
| after this you can | (1) place a feature in the add-on's two exporters and one importer; (2) choose Colour Space and Light Units and predict what X_ITE, Babylon.js and Blender each draw; (3) read a fidelity-rig result and say what `geometry_delta` does and does not prove; (4) run the tests and conformance suite from a pip-installed `bpy`; (5) bake light into X3D vertex colours and gate it; (6) grade a sci-vis survey claim |
| sources read | x3d-blender-io@ab99988:{README.md, release_notes.md, source/, tests/, tools/fidelity_rig/README.md, .github/}; x3d.docs@f172f67:docs/x3d-blender-io/MASTERCLASS.md; x3d_mcp@b4efcd3:src/validation/; the bake-stage skill text; private sci-vis and ecosystem notes (leads) |
| instruments used | `bpy 5.3.0` (pip wheel, Python 3.13.18, CPU only); `x3d_mcp fork b4efcd3`; `X3D XSD 4.0` and `X3D XSD 4.1` through the fork; `X3DUOM 4.1`; `X_ITE 16.7.1` and `Babylon.js 9.32.0` on `Chrome for Testing 153.0.8010.12, SwiftShader`; `Khronos glTF-Validator 2.0.0-dev.3.10`; `x3d-blender-io@ab99988`; software GL, no GPU |

Rig for every **[C]** here: read-only checkout of `x3d-blender-io@ab99988`, scratch copies for anything that writes, a venv with `bpy 5.3.0` and `x3d 4.0.65.8`, no network except `pip` and `npm`, no GPU, no paid service, all on 2026-11-14. Figures copied from a README or note and not re-run are **[L]** or **[S]** and say so.

## 1. The map

```text
  Blender scene (bpy 5.x)
    meshes, materials, lights,         Cycles bake            export_scene.x3d
    armatures, shape keys, splats ───► (vertex colours) ───►  ├ X3D 3.3 legacy writer
                                                              ├ X3D 4.0 IR writer (PBR, HAnim,
  X3D file (any validity)                                     │  Inline, morph)
    legacy tree parser + IR parser     import_scene.x3d       └ X3D 4.1 draft (GaussianSplats)
    Colour Space, Light Units    ◄──── "as X_ITE draws it"
                                                   gates
                           1 x3d_mcp fork: XSD + semantic    3 glb ► Babylon.js 9.32.0
                           2 X_ITE 16.7.1 draws the X3D      4 Khronos glTF-Validator
  score = fidelity against X_ITE, never "the re-export is valid"
```

| in scope | out of scope here |
|---|---|
| architecture, node coverage, the sRGB and X_ITE-light-units defaults | the AST teardown: [the x3d-blender-io masterclass](../x3d-blender-io/MASTERCLASS.md) |
| fidelity rig, tests, conformance suite, how to re-run them | glTF/USD/Khronos rules (`11-gltf-usd-khronos.md`), Unreal (`12-unreal-tier1.md`), physics (`13-physics.md`) |
| bake recipe, round-trip principle, sci-vis knowledge base, bridges, ecosystem watch | Castle as a render target: [09 Castle Engine](09-castle-engine.md) |

Read next: deeper, [06 X_ITE, the reference renderer](06-xite-the-oracle.md) (the thing every default below is fitted to); wider, [08 The Babylon bridge](08-babylon-bridge.md) (the second renderer the glb leg is drawn in).

## 2. Two exporters and one importer wearing one operator

The add-on (`io_scene_x3d`, extension id `x3d_blender_io`) is a fork of Blender's community X3D/VRML2 extension. Upstream stops at X3D 3.x with a legacy `Material`; the fork adds an intermediate-representation (IR) writer for X3D 4.x and a large amount of importer work. What could be re-counted at `x3d-blender-io@ab99988`:

| piece | what it is | where | grade |
|---|---|---|---|
| legacy writer (X3D 3.3 option) | `fw('%s<Shape' % ident)` string writer; also the router that calls `extract` | `source/export_x3d.py`, 1,985 lines | **[C]** (`wc -l`) |
| IR writer (4.0, 4.1 draft) | Blender to `extract.py` to `ir.py` dataclasses (no `bpy`) to `emit_x3d40.py` to `validate.py` | 1,374 and 886 lines | **[C]** |
| importer | one dominant legacy parser plus builders; the IR parser serves Inline assets only | `source/import_x3d.py`, 7,340 of 16,753 lines in `source/*.py` | **[C]** |
| bridges | `splat_io.py`, `splat_native.py`, `bridge_gltf.py`, `viewpoint_fov.py`, `geospatial.py`, `matrix_safety.py` | `source/` | **[C]** (read) |

What the 4.0 export writes, with the PR from the masterclass table (**[L]** for PR numbers): Principled BSDF to `PhysicalMaterial` plus five glTF-style texture slots (emission-only to `UnlitMaterial`); hierarchy, lights, cameras, text and sampled animation to `Transform`, three light nodes, `Viewpoint`, `TimeSensor` with interpolators and ROUTEs; HAnim 2.0 both ways (#2, #4); the Inline bridge for x3d, glb, ply and splat assets (#5); X3D 4.1 `GaussianSplats` from a splat mesh or a Blender 5.3 native PointCloud (#5, #10; 4.0 degrades to a coloured `PointSet`); fold morph, shape keys to `CoordinateInterpolator` and back (#22); and, after #38, an unedited imported Box, Sphere, Cylinder or Cone exports as that node (`x3d_primitive` plus a vertex checksum).

**A provenance trap. [C]** `source/blender_manifest.toml` says version `2.6.4`; `source/__init__.py` `bl_info` says `(2, 6, 1)`; the exporter writes `<meta name="generator" content="X3D Blender I/O v2.6.1">`. A file's provenance string names a version that is not the manifest's (drill D-BLE-1).

## 3. Node coverage growth: 39 to 54 written, 42 to 68 read

The teardown reports, for the fork's first commit `7f8c0fb` against `e071a61`: nodes written 39 to **54**, read 42 to **68**, written and read 26 to **43**, components touched 14 to **20** of 37, out of the 267 concrete nodes of X3DUOM 4.1. **[L]**: the number comes from a document whose method (string literals plus per-module role rules, graded by evidence strength) has no public script in this repo.

I re-derived a **lower bound** with a naive rule to show how much the method matters. **[C]**, `x3d-blender-io@ab99988`, `X3DUOM 4.1` from `x3d_mcp@b4efcd3`: written = an XML tag literal `<Name` in `emit_x3d40.py`, `export_x3d.py`, `extract.py`, `export_pipeline.py`, `material.py`; read = a string literal equal to a node name in the seven importer and bridge modules.

| count | teardown (`e071a61`) | naive scan (`ab99988`) | why they differ |
|---|---|---|---|
| concrete nodes in X3DUOM 4.1 | 267 | 267 | same denominator **[C]** |
| written | 54 | 46 | tags built from f-strings or constants (five `Metadata*` nodes, `Switch`) are missed by an exact match |
| read | 68 | 65 | names that appear only in a collection or a ROUTE field name are credited by the teardown |
| both | 43 | 38 | follows |

The teardown is not contradicted (a naive rule is a lower bound 8 and 3 below it) and not reproduced. Treat 54 and 68 as the best available count, **[L]**, and quote the rule beside any coverage number.

Where the growth shows (teardown, **[L]**): Core metadata 1 to 7 written (PR #16), Geometry2D 0 to 8 read (#17, #26), Geospatial 0 to 3 read (#35), Interpolation 0 to 3 written, HAnim 0 to 2 both ways, `GaussianSplats` and `Inline` 0 to 1. 17 of 37 components are untouched, among them RigidBodyPhysics, NURBS, Followers, ParticleSystems and VolumeRendering.

One finding changes how you test: the importer animates by ROUTE **field names** (`value_changed` to `set_translation`, `set_rotation`, `set_scale`), not by node type, so a spline interpolator routed to a Transform imports as linear keys with no warning. **[L]** (teardown, AST read, not executed; not re-checked at `ab99988`).

## 4. The colour-space decision

**What the renderers disagree on. [C]** (README measurement, `X_ITE 16.7.1`, headless Chrome 153, SwiftShader; the add-on's own probes re-run in section 6 confirm the lighting half):

| colour in the file | X_ITE reads it as | Blender and glTF read it as | consequence of copying the number |
|---|---|---|---|
| `Material`, `TwoSidedMaterial`, `UnlitMaterial` colour | display (sRGB) values: 0.5 draws 128 | linear | copied as is, a classic scene is drawn too bright in Blender and Babylon.js |
| a `Color` node under those materials | display, in place of the material colour | | |
| `PhysicalMaterial` colours | linear (the glTF way): `baseColor` 0.5 under a light of 1 draws 110, `emissiveColor` 0.5 draws 187 | linear | no conversion needed |
| a `Color` node under `PhysicalMaterial` | a linear factor on `baseColor` | | |

The README adds that Castle Game Engine drew the same 128, 186 and 108 to 110, so two independent X3D engines agree on the split. **[L]** (a README line; Castle not run here; see [09 Castle Engine](09-castle-engine.md)).

**Decision, PR #30 (merged 2026-11-12): sRGB is the default.** Import and export both: `AUTO` reads the scene's stored `x3d_color_space`, then the environment variable `BLENDER_X3D_COLOR_SPACE`, then `SRGB`. Why that choice and not `AS_IS`: the default import now draws a classic scene the way X_ITE and Castle draw it; the cost is that Blender's numbers differ from the file's, so the export has to convert back. The export option closes the loop (PR #29): under `SRGB` the 3.3 writer sRGB-encodes a Material's `diffuseColor`, `specularColor`, `emissiveColor`; the 4.0 writer sRGB-encodes an `UnlitMaterial`'s `emissiveColor`; `PhysicalMaterial` colours are always written linear. **[C]** as a statement of the code's documented behaviour (README, `source/__init__.py` enum `color_space` read); the numeric round-trip is covered by `tests/test_colour_round_trip_bpy.py`, which passed in the run in section 7.

Worked example (release notes, **[L]**): a classic light `color='1 0.5 0.2'` read as sRGB becomes Blender `1 0.214 0.0331`; the 3.3 writer writes it back as `1 0.5 0.2`; the 4.0 writer writes the linear `1 0.214041 0.033105`, because its `PhysicalMaterial`s are lit linearly in X_ITE. Same light, two correct file values: that is why the option is per writer.

Two colour traps worth a heuristic each:

| trap | symptom | fix | instrument |
|---|---|---|---|
| float colour attribute channel just over 1 | `ColorRGBA` pattern facet fails the XSD (a molecular-nodes palette wrote a red of 1.000169) | clamp to [0, 1] on export (the 4.0 writer now does) | `x3d_mcp fork b4efcd3` message "attribute 'color': [facet 'pattern']" (reproduced, drill D-BLE-2) |
| per-vertex `Color` converted twice | 0.5 came in as 0.04, not 0.21 | convert once (release notes, **[L]**) | release_notes.md |

## 5. The light-units decision

X3D gives a light an `intensity`, not watts. X_ITE 16.7.1 lights a `PhysicalMaterial` the glTF way (1/d² falloff times the X3D `attenuation`, colour over pi, linear space) and a classic `Material` the old way (only `attenuation`, so the default `1 0 0` never falls off, display space). Blender, glTF viewers and Babylon.js light everything the first way. The import option `light_units` picks the mapping:

| `light_units` | DirectionalLight | PointLight, SpotLight | when `AUTO` picks it |
|---|---|---|---|
| `BLENDER` | `i` lux | `1.75 i / 4 pi` = 0.139 `i` (the glTF COMPAT candela, Blender watts = 4 pi cd) | colour space `AS_IS` |
| `X_ITE`, physical scene | `i` | `i · att(d / s) · s²` (exact at every distance for `attenuation 1 0 0`) | colour space `SRGB` (the default) |
| `X_ITE`, classic scene | `f · i` | `f · i · att(d / s) · d² / w(d)`, `f` fitted | same |

`s` is the light's own frame (file unit times Transform scales); `d` is the light's reference distance, the median distance to the shapes it reaches; `w(d) = clamp(1 - (d/r)^4, 0, 1)²` is the range window Babylon.js 9.32.0 applies to a glTF `range`. **[L]** for the formulas (README), **[C]** that the option and the three enum values exist (`source/__init__.py`, `light_units` EnumProperty).

**The classic-light fit.** A classic scene has no exact glTF match: X_ITE shades `emissiveColor + diffuseColor · L` in display space with no falloff, a glTF viewer adds linear light falling as 1/d². So the import casts a 64 by 64 ray grid over the first Viewpoint's view, compares X_ITE's `min(e + b · L, 1)` with `srgb(min(E + B · lux / pi, 1))` per channel, and picks each light's factor `f` to minimise the mean difference. What it cannot copy (README, **[L]**): falloff away from the fitted distances, display-space Lambert on oblique light (a 0.8 grey at 58 degrees from a classic point light: 109 in X_ITE, 167 in Babylon.js), the sRGB toe below albedo 0.04, X_ITE's `shadows`, classic specular highlights.

The price (README): a round trip that **starts in Blender** keeps its light energies only with `light_units = BLENDER`.

## 6. The fidelity rig

`tools/fidelity_rig` runs a scene through the add-on to a glb (Blender 5.3, COMPAT light units, renderable objects only, cameras, lights, loose edges and points), then draws X_ITE on the X3D and Babylon.js on the glb in the same headless Chromium at 512 by 512, from the X3D's first Viewpoint.

```text
   scene.x3d ──► Blender leg (bpy 5.3.0): import ──► glTF export ──► scene.glb
        │                                                              │
        │                                                  Khronos glTF-Validator 2.0.0-dev.3.10
        │                                                  (0-error gate; manifest with sha256)
        ▼                                                              ▼
   X_ITE 16.7.1  ──► xite.png                              Babylon.js 9.32.0 ──► babylon.png
        │                                                      + magenta/green clear ──► mask
        └───────────────► mean |delta| (0..255) ◄─────────────────┘
   mean_abs_delta   whole frame (background included)
   geometry_delta   only where the glb draws geometry (mask)
   patches          5x5 means at listed pixels (probe scenes)
```

| output | meaning | what it does not mean |
|---|---|---|
| `mean_abs_delta` | mean absolute pixel difference over the whole 512 by 512 frame, 0..255 | diluted by background: p1 shows 0.07 while its geometry delta is 0.24 |
| `geometry_delta` | the same, only where the glb has geometry | not a perceptual metric; a flat shift and a wrong shape can score alike |
| `patches` | X_ITE and Babylon.js 5 by 5 means at chosen pixels | three pixels per probe; not an image comparison |
| `validator_ok` | the glb passed `gltf-validator` with 0 errors | a valid glb can be empty, look wrong, or use an extension an engine ignores (the rig README says so) |
| manifest | `x3d-blender-io.glb-manifest/v1`: x3d sha256, add-on revision, Blender version, options, glb sha256, validator summary | provenance, not correctness |

**Re-run, 2026-11-14. [C]** `x3d-blender-io@ab99988`, `bpy 5.3.0`, `X_ITE 16.7.1`, `Babylon.js 9.32.0`, `Chrome for Testing 153.0.8010.12, SwiftShader`, `gltf-validator 2.0.0-dev.3.10`. The rig's own `package.json` pins and its probe set were used; the only change was pointing the rig copy's launcher at the installed Chrome for Testing 153 binary (the Playwright browser download was not used). Centre patch (pixel 256, 256), X_ITE / Babylon.js, in 0..255:

| probe | X_ITE | light units BLENDER | light units X_ITE | `geometry_delta`, X_ITE units | README value (centre) |
|---|---|---|---|---|---|
| p1 PhysicalMaterial, PointLight 1 | 74 | 30 | 74 | 0.24 | 74 / 30 / 74 |
| p2 classic Material, PointLight 1 | 204 | 27 | 203 | 47.07 | 204 / 27 / 203 |
| p3 classic Material, DirectionalLight 1 | 204 | 120 | 203 | 1.5 | 204 / 120 / 203 |
| p4 PhysicalMaterial, PointLight 1, attenuation `1 0 0.2` | 57 | 30 | 56 | 3.37 | 57 / 30 / 56 |
| p5 PhysicalMaterial, DirectionalLight 0.3 | 78 | 78 | 78 | 0.2 | 78 / 78 / 78 |

All five centre-patch cells reproduce the README's table to the integer. The more important number is the one the README table does not print: p2's `geometry_delta` is **47.07** even though its centre patch matches (204 against 203). The left box of p2 reads 109 in X_ITE and 167 in Babylon.js, the right box 190 and 97: the fit anchors the light at one reference distance, and the other two boxes are at 1.8 m and 4.2 m. A centre-patch match proves the fit's anchor, not the scene. That is the sharpest practical lesson of the rig. All five glbs passed the validator gate with 0 errors and 0 warnings (3 infos each).

Pin drift, **[C]** 2026-11-14 (`npm view`): `x_ite` latest 16.7.1 equals the rig pin; `babylonjs` latest is 9.36.0, the rig pins 9.32.0. Re-measure the probes before moving a pin.

The README also records, **[L]** (read, not re-run): nine x3d.demo scenes with lights improved from Blender units to X_ITE units on `geometry_delta` (25.3 against 40.5 for a 151-Material constellation, 13.7 against 37.3 for a materials shelf); two Blender-lab scenes of 89,568 and 93,682 triangles scored 3.32 and 3.48 with 0 validator errors; of 34 repo scenes, 33 export a glb, all with 0 errors and 0 warnings.

Two bugs the rig found (README, **[L]**): the glTF exporter writes `frame / fps`, so with factory frame 1 a glb's animation ran 1/24 s late (the rig sets `frame_start = 0`); and object names are not the DEF (Blender suffixes duplicates), so the importer tags `x3d_def`, `x3d_def_path`, `x3d_use` into the glb's `extras`.

## 7. Tests, conformance, and how to re-run them

**The unit and bpy tests. [C]** `x3d-blender-io@ab99988`, Python `ast` over `tests/test_*.py`: **336** `test_*` functions in **35** files, of which **274** are in 30 `*_bpy.py` files (need `bpy`) and 62 in five plain files. Running `.github/scripts/run_tests_in_blender.py` (which skips `*_bpy*` modules when `import bpy` fails): **62 tests, OK** with no `bpy`. With `bpy 5.3.0` installed: **335 tests ran, OK, skipped 10**; the ten skips are all `test_glb_validator_bpy` (the Node package `gltf-validator` was not installed). With `npm install gltf-validator@2.0.0-dev.3.10` and `GLTF_VALIDATOR_DIR` pointing at it, with `GLTF_VALIDATOR_REQUIRED=1`: **10 of 10 pass**. So 335 ran and 335 pass, 0 skipped, with the validator present. The AST count is one higher than the run count: the one function the runner does not report is `test_the_validator_loads` (the teardown inferred such an off-by-one for PRs from #33 on; the name is now found).

**The export conformance suite. [C]** `tests/suite/x3d_test_suite.py` builds one Blender scene and three exports (`main`, `crease`, `x41`); `tests/suite/validate_x3d_export.py` checks the file. Re-run on `bpy 5.3.0` (5 s):

| result line | value |
|---|---|
| cases | 195 = 148 CORE + 21 FIDELITY + 26 ROADMAP (matches `tests/suite/README.md`) |
| CORE | 148 of 148 pass |
| ROADMAP | 21 MISSING (expected gaps), 5 NEW (implemented since the roadmap was written) |
| FIDELITY | 19 WARN, 2 PASS |
| the three exports through `x3d_mcp fork b4efcd3` `validate_xml` | `x3d_suite_main.x3d` (7,010,591 bytes) valid on 4.0; `x3d_suite_crease.x3d` (4,911,800 bytes) valid on 4.0; `x3d_suite_x41.x3d` (4,617,408 bytes) valid on 4.1; 0 errors each |

**Where sources disagree. [C]** The teardown says 194 cases; the suite README, the CI step name and the run say 195. The code wins; the teardown's AST parse of case sites is stale by one. CI runs the suite on Blender 5.1.2 and the wheel job on Python 3.11; this chapter's `bpy 5.3.0` is outside that matrix (workflow read, **[L]**).

**How to reproduce (free, CPU only).**

```bash
# 1. venv with the bpy wheel (427.5 MB) and the Web3D x3d package
python3 -m venv /tmp/ble && /tmp/ble/bin/pip install bpy==5.3.0 x3d numpy pillow

# 2. unit and bpy tests, from a checkout (the runner skips *_bpy* without bpy)
cd x3d-blender-io
PYTHONDONTWRITEBYTECODE=1 /tmp/ble/bin/python -B .github/scripts/run_tests_in_blender.py | tail -4
#   expect: Ran 335 tests ... OK (skipped=10)   (skips are the glTF-validator tests)

# 3. un-skip the glb tests with the pinned validator
mkdir /tmp/gv && (cd /tmp/gv && npm install gltf-validator@2.0.0-dev.3.10)
cd tests && GLTF_VALIDATOR_DIR=/tmp/gv/node_modules/gltf-validator GLTF_VALIDATOR_REQUIRED=1 \
  /tmp/ble/bin/python -B -m unittest test_glb_validator_bpy      # expect: Ran 10 tests ... OK

# 4. the conformance suite
cd .. && /tmp/ble/bin/python -B tests/suite/x3d_test_suite.py -- --out /tmp/suite --repo "$PWD" --export
python3 -B tests/suite/validate_x3d_export.py /tmp/suite --html /tmp/suite/report.html | tail -4
#   expect: CORE conformance: 148/148 passed | NEW features detected: 5

# 5. the fidelity rig probes (needs Node, npm install in tools/fidelity_rig, and a Chromium 153)
cd tools/fidelity_rig && npm install && BPY_PYTHON=/tmp/ble/bin/python python3 compare.py after ../../source probes.json
```

Run Python with `-B` so a read-only checkout stays clean (`find . -name __pycache__` is the check).

## 8. The bake stage: light travels with the file

Light is computed once in Blender and carried by X3D as one colour per face corner, so the page draws baked meshes unlit with no per-frame lighting. Use it for static lit geometry; use a small shader for anything that must follow the view (a rim, a glint); a mover cannot use a baked direction. The recipe is a Loom skill (`loom-blender-bake-stage`); below is its procedure, with grades by what I re-ran.

| step | what | grade |
|---|---|---|
| 1 | model in bmesh, merge into few meshes, store face albedo in a corner attribute `Alb` | **[L]** skill text |
| 2 | Cycles CPU, denoise off, indirect clamp 4.0, fixed seed; skill: 384 samples (96 preview); my re-run: **16** | **[L]**; re-run **[C]** |
| 3 | one sun, azimuth 220, elevation 55, colour (1, 0.85, 0.62), strength 5, disc 6 degrees; sky 0.25 (probe the sky against the key, do not guess) | **[L]**; re-run used the same sun and sky |
| 4 | `render.bake.target = 'VERTEX_COLORS'`, DIFFUSE, direct and indirect on, colour pass off: the bake holds light only | **[C]** |
| 5 | finish in Python: exposure so the 70th-percentile corner is 1.0; floor the light at (0.05, 0.07, 0.12); times linear albedo; sRGB curve; shoulder from 0.8 | **[C]** |
| 6 | export X3D 4.0; strip `PhysicalMaterial`, `Background`, `NavigationInfo`; 3 decimals; an all-opaque `ColorRGBA` becomes `Color` | **[L]**; strips not run |
| 7 | gate: validator (XSD, semantic, profile), then X_ITE with the console open | validator **[C]**; X_ITE not opened for the toy |
| 8 | frames at the stops; a black frame is retaken, never scored | **[L]** |
| 9 | receipt: Blender version, exporter commit, script and file sha256, bake settings, light percentiles; editing the script, even a comment, breaks the pinned sha256 | **[L]** |

**A re-run at toy scale. [C]** `bpy 5.3.0`, Cycles CPU, 16 samples, an 8 by 8 ground grid plus a 1.5 m box in one mesh (280 face corners), the sun above, flat sky 0.25. Cycles baked to a `FLOAT_COLOR` corner attribute (`FINISHED`). Raw channels ran from **0.0** to **1.9151** (raw light exceeds 1: the trap). The 70th-percentile corner luminance was 1.3212, so exposure was **0.7569**; after floor, sRGB curve and shoulder the largest channel was **0.9696**. The add-on exported 9,356 bytes with one `ColorRGBA` and no `Color`; the fork validator said **valid, 0 errors**; the whole run took 0.7 s. One channel set to 1.0059 (the value that sank an Earth export) gave 1 error: `Element 'ColorRGBA', attribute 'color': [facet 'pattern']`. At large scale the skill reports the fork's message can blame a size limit instead, so bisect the array (**[L]**, not reproduced: the toy file is 9 KB).

Other traps, all **[S]** (carried from the skill text; the receipt behind the village numbers is not public): per-corner colour splits vertices on (vertex, uv, colour, normal), so DEF/USE stops helping, and a village-scale scene went from 26 KB to 330 KB gzipped, about half from lost sharing and half from added geometry (load it lazily behind an Inline); `DepthMode` and `BlendMode` are X_ITE-only and refused unless an X_ITE component is declared; X_ITE draws transparent shapes after opaque ones with depth writes off, so a translucent shell around the camera hides the scene; GLSL ES 3.00 needs a decimal point on float literals; a ROUTE written before its nodes is dropped by X_ITE and passed by the validator; call `index_update` before assigning vertex-group weights; software GL shows black first frames.

The receipt is this stage's accountability object: it names the script, Blender and exporter commit behind the file, and shows when the script changed.

## 9. The round-trip principle: score fidelity, not validity

The exporter writes what Blender holds and never sees the source's mistakes, so a re-export is valid even when the source was not: "the round trip validates" says nothing about the source and little about the importer.

```text
   source.x3d  (3 XSD errors)                     re-export.x3d  (0 errors)
   ┌───────────────────────────────────┐          ┌───────────────────────────────────┐
   │ Material diffuseColor="2.5 .5 .1" │ import   │ PhysicalMaterial baseColor        │
   │ <Box size=... bogusField="oops"/> │ ───────► │   "1.000000 0.214041 0.010023"    │
   │ <Box/> directly under a Transform │ Blender  │ <Box size="1 1 1" solid="false"/> │
   └───────────────────────────────────┘ export   │ (second Box gone)                 │
          validator: invalid                       └───────────────────────────────────┘
                                                          validator: valid
```

**Run. [C]** `x3d-blender-io@ab99988`, `bpy 5.3.0`, `x3d_mcp fork b4efcd3` (`validate_xml`): the source above is invalid (3 errors: the colour pattern, the unknown attribute, the misplaced `Box`). The add-on imported it (`FINISHED`, one object, `T`) and exported X3D 4.0 (`FINISHED`); the re-export is **valid, 0 errors**. What changed, read from the output: the colour 2.5 was clamped to 1 and the others converted (`0.5` to `0.214041`, `0.1` to `0.010023`), the classic `Material` became a `PhysicalMaterial`, the unknown attribute vanished, and the `Box` that was outside any `Shape` was dropped (both operators still returned `FINISHED`). A validity score would have read "3 errors to 0", a gain; the fidelity reading is "two of three defects destroyed information, one repaired structure".

So validate the source, score the round trip by fidelity against the source's render (the rig's `geometry_delta`, or a value-level loss ledger), and never cite "the re-export validates" for the importer. Its own defence is a must-not-raise test on mutated sources (bridge B07, section 12).

## 10. The Blender scientific-visualisation knowledge base

The knowledge base was built on 2026-10-24 from a six-part research survey ("the Survey", written by an earlier Claude session on 2026-10-15 to 18) and versioned: v1, then a v1.1 addendum beside it that overrides items instead of editing them. It is a **set of leads with grades**, not a measurement set. Its value here is the grading rule and the list of hands-on tests it leaves open.

| Survey tag | meaning in the Survey | grade here | why |
|---|---|---|---|
| [V] | read in a primary document | **Likely** | someone else read it; we did not reproduce it |
| [R] | secondary or trade press | **Suspected** | not read at source |
| [I] | inference | **Suspected** | reasoning, not observation |
| none yet | | **Confirmed** | only after reproduction with a named validator, X_ITE patch and Blender build |

The knowledge base states "nothing below is Confirmed yet" on the day it was written. **[C]** as a statement of its rule; section 11 re-checks some of its facts.

**Thesis.** Capture and generation got cheap; trust (lighting, measurement, validation, provenance) is the scarce part. In the Survey's lane comparison the Blender agent lane runs arbitrary Python with no guard, the X3D lane has a validator between model and scene. **[L]** (the Survey's; the `x3d_mcp` side is measured in [03](03-validator-and-gates.md) and [04](04-mcp-for-agents.md)). The failures differ: the Blender lane produces valid-looking but wrong colour or scale; the X3D lane produces schema-valid but untrue scenes (units, mapping), which a semantic layer can still catch ([05](05-semantic-layer.md)).

**Engine facts that matter (Survey, Likely unless noted).** Colour management is the largest hidden error class: use the Standard view transform when colour encodes a value (AgX tone-maps) and tag data images Non-Color. Numbers narrow at Blender's border (32-bit float against Python's 64-bit; **[S]**, one forum thread): centre and scale before import. The add-on's answer is measured: `source/matrix_safety.py` exists because a Transform scale of 1.057e-16 underflowed Blender's float32 inverse (PR #37, **[L]**). X3D has no atoms, bonds or interactions; per-point data rides in `Color`/`ColorRGBA` or `Metadata*`. The Survey's tool tiers (Molecular Nodes, Microscopy Nodes, Bioxel Nodes, SciBlend as tier A) are **[S]** and stale in weeks.

One overlap: the release notes record a Molecular Nodes 520.2.0 pLDDT palette writing a red of 1.000169, invalidating 9,756 and 17,326 channels on two AlphaFold models under `x3d_mcp fork 13121b68e6d9`; the 4.0 writer now clamps to [0, 1]. **[L]** (models not in the repo).

### Splats: the part the add-on is closest to

The Survey's size arithmetic was **re-derived from the add-on's PLY writer. [C]** `source/splat_io.write_ply`, `x3d-blender-io@ab99988`, 1,000 synthetic splats per degree, bytes after `end_header` divided by N:

| SH degree | floats per splat | measured bytes per splat | Survey | 10 million splats |
|---|---|---|---|---|
| 0 | 17 | **68.0** | 68 | 680 MB |
| 1 | 26 | **104.0** | 104 | 1.04 GB |
| 2 | 41 | **164.0** | 164 | 1.64 GB |
| 3 | 62 | **248.0** | 248 | 2.48 GB |

The layout is the reference 3DGS PLY (three normal floats included); each degree read back at the same degree. **[C]**

| quantity | X3D 4.1 `GaussianSplats` | Blender 5.3 PointCloud | glTF `KHR_gaussian_splatting` |
|---|---|---|---|
| position, scale | `positions`, `scales` (linear) | `position`, `scale` float3 linear | `POSITION`, `...:SCALE` |
| rotation | `orientations` as x y z w | `rotation` quaternion (w x y z) | `...:ROTATION` |
| opacity, SH DC | `opacities`, `sphericalHarmonicsDegree0Coef0` | `radiance:base` (xyz = DC, w = opacity) | `...:OPACITY`, `..._SH_DEGREE_0_COEF_0` |
| SH higher | `sphericalHarmonicsDegree{d}Coef{c}` | `radiance:sh_{i}`, i = 0..14 | `..._SH_DEGREE_{d}_COEF_{c}` |

Crosswalk **[L]** (ecosystem map; the add-on's `splat_native.py` implements the Blender column). The quaternion order is a standing trap: the draft node text does not state it, the add-on writes `x y z w`, X_ITE 16.4.3 reads `x y z w`, and the same data written `w x y z` renders as streaks (README, **[L]**).

## 11. Corrections, and what changed under a re-check

| id | claim as written | state, and my re-check 2026-11-14 |
|---|---|---|
| C1 | the Survey says Blender's X3D is 3.3 with no PBR; the add-on writes 4.0 PhysicalMaterial, animation, HAnim, Inline, morph, a 4.1 splats fixture | **[C]** for the add-on's side (sections 2, 7). For upstream the code disagrees with both sources: the legacy writer, option label "X3D 3.3", writes `<X3D version="3.0">` and the 3.0 DTD (`source/export_x3d.py` lines 342 to 343, confirmed by running an X3D33 export). The Survey's "3.3" is **[S]** |
| C2, C3, C4 | static-meshes text corrected later; how SciBlend reads X3D unknown; version register unverified | open or not re-checked, **[S]**; versions below re-checked where cheap |
| C5, C6 | trade-press [V] tags downgraded to Suspected; the Survey ran no hands-on tests | the rule is the point; this chapter produces some Confirmed rows |
| U1 | native splats upgraded from Suspected to Likely (Blender git, 2026-10-11) | **[C]** on a release build, below |
| U2 | the add-on exports native 5.3 splats to X3D 4.1 and imports them | **[C]**: the native-splat tests in `tests/test_roundtrip_bpy.py` ran in the 335-test pass, `bpy 5.3.0` |
| U3 | extension id `x3d_blender_io`, no clash with upstream `web3d_x3d_vrml2_format` | **[C]** `source/blender_manifest.toml` |

**What `bpy 5.3.0` (a release build) says. [C]**, probed 2026-11-14:

| question | answer | against the source |
|---|---|---|
| native splat type? | `PointCloud.type` enum is `['POINTS', 'GAUSSIAN_SPLAT']` | confirms U1; the ecosystem map wrote `POINT` (**[S]** loser) |
| import? | `bpy.ops.wm.spz_import` and `wm.ply_import` exist | confirms |
| export? | no operator named for `splat`, `spz` or `gaussian` except `spz_import` (and the unrelated `graph.gaussian_smooth`); `wm.ply_export` on a native splat exported **0 vertices** (156 bytes, `element vertex 0`) | turns "no export" from a note into a run |
| X3D in core? | no `import_scene.x3d` or `export_scene.x3d` without the add-on; `import_scene.gltf` and `export_scene.gltf` exist | confirms the extension model |
| is 5.3 out? | map said "scheduled 2026-11-10"; PyPI has `bpy 5.3.0`, `version_cycle` `release`, newest in `pip index versions bpy` | **[C]** a release wheel exists |

Consequence: X3D 4.1 `GaussianSplats` is the only route this base found that carries a Blender 5.3 native splat out of Blender. **[C]** that 5.3.0's PLY export wrote none; **[L]** that no other route exists (add-ons and Geometry Nodes workflows were not searched).

The Survey's eight hands-on tests, state today: (1) science-fixture round trip, partial (colour and metadata round trips are tested; no volume-grid fixture in the repo, **[L]**); (2) Standard against AgX render, not run; (3) 32-bit precision, partly answered by `tests/test_import_extreme_scale_bpy.py` (ran, passed, **[C]**); (4) PLY to X3D to Blender, sizes **[C]** above, error figures not re-measured; (5) pLDDT bands, not run; (6) agent A/B, not run (bridge B18); (7) glTF to a second runtime, done by the rig (section 6); (8) largest structure load, not run.

## 12. The flywheel bridges, ranked

A later study (2026-10-25) ranked 18 bridges between the Blender lane, the X3D validator and the rest of the project; a verifier pass then re-read each. It is a lesson in grading before it is a roadmap: of 13 bridges first graded Confirmed, **12 came out Likely** and one stayed Confirmed (B17); one Likely fell to Suspected (B16). **[S]** for all of it: carried from a private note, no bridge's inputs re-run, several in private repositories.

| rank | bridge (direction, effort) | grade after verification |
|---|---|---|
| 1 | B01 splat round-trip fixture ladder, synthetic S0 to S3 and real R1 to R5, with an expected-loss table (both, M) | Likely |
| 2 | B02 validator `huge_tree` handling plus an honest "not checkable at this size" verdict (to X3D, S) | Likely; duplicates an open board item |
| 3 | B03 exporter option: maximum bytes per `GaussianSplats` node (to X3D, M) | Likely |
| 4 | B04 importer value-correctness pack: double colour decode, X3DUOM defaults, unlit EOTF (to Blender, M) | Likely |
| 5 | B05 Blender-script guard: preflight, export, validator gate, loss audit, ledger row (to Blender, M) | Likely; only two rules coded, "3 of 5 caught" needs a flag |
| 6 | B06 numeric look-parity chart (both, S) | Likely |
| 7 | B07 importer must-not-raise suite from mutated sources (to Blender, S) | Likely |
| 8 | B08 renderer-independent splat oracle plus an X_ITE ordering ladder (to Blender, M) | Likely |
| 9 | B09 twelve sci-vis semantic checks for the validator (to X3D, S) | Likely |
| 10 | B10 sci-vis fixture factory plus exporter metadata and units gaps (to X3D, M) | Likely |
| 11 | B11 round-trip tiers A to D with a value-level loss ledger (both, M) | Likely |
| 12 | B12 provenance chain for Blender renders, plus export-side leak fixes (to X3D, M) | Likely |
| 13 | B13 Blender 5.3 readiness: native-splat probe, CI leg, watch refresh (to Blender, S) | Suspected; partly answered by section 11 |
| 14 | B14 orchestration skeleton calling existing scripts (both, M) | Suspected |
| 15 | B15 three-way oracle metric plus sci-vis attacker families (both, L) | Likely |
| 16 | B16 SPZ import path and sidecar for Blender 5.2 LTS (both, M) | Suspected; 5.3 imports SPZ natively |
| 17 | B17 licence passport on Blender exports (both, S) | Confirmed |
| 18 | B18 Blender-agent against `x3d_mcp` A/B, scored on fidelity (both, L) | Suspected |

The ranking orders by value over effort, not readiness. B05 and B07 are the ones this chapter's measurements make concrete (section 9: validity is the wrong score; the importer is the only defence against a bad source). B13 and B16 shrank the day Blender 5.3.0 shipped. B05's best idea: run the loss audit on the source scene before export, because after a round trip it is empty.

## 13. The ecosystem-watch routine

A routine fires daily at 13:51 UTC in three steps. (1) `watch.py`, stdlib only, about 8 s: `git ls-remote` tags and heads on `blender/blender`, shallow commit-only fetches of nine repos with a keyword filter, PyPI JSON (`bpy`, `x3d`, `mcp-for-blender`) and npm JSON (`x_ite`, `splat-transform`, `spark`), diffed against `state.json` into an append-only `LEDGER.md` plus a JSON digest. (2) A web pass of at most six searches, only for hosts curl cannot reach (the extension index, Blender's own forge, release notes, Khronos news, the x3d-ecosystem list). (3) Each change is judged against the ranked map and reported in one short digest, or not at all. A quiet day produces no message. **[L]** (routine and script read; not run).

The map scores each item Impact (1 to 5) times Timing (1 to 3) over Effort (1 to 3), timing 3 meaning "act before 5.3 ships". Top of the first edition (2026-10-11), scores are the author's judgement **[L]**:

| rank | item | score | state |
|---|---|---|---|
| 1 | native `GAUSSIAN_SPLAT` PointCloud export and import | 15 | done in PR #10; type, import and missing export **[C]** on `bpy 5.3.0` |
| 2 | extension id collision with upstream | 12 | done in PR #10: `x3d_blender_io` **[C]** |
| 3 | `KHR_gaussian_splatting` import in Blender's glTF add-on | 12 | in the 5.3 branch (git, per the note); not re-run |
| 4 | Blender Lab official MCP server | 10 | web-sourced, **[S]** |
| 5 | X_ITE pin bump | 9 | rig pin and npm latest both 16.7.1 **[C]** |
| 8 | bpy 5.3 wheel in CI | 6 | wheel exists; CI matrix tops out at 5.2.2 (teardown, **[L]**); the standing open item |

Today's probes, **[C]** 2026-11-14: `bpy` newest 5.3.0 (then 5.2.4, 5.2.3, 5.2.2); `x3d` 4.0.65.8 (ledger baseline 4.0.65.7); `x_ite` 16.7.1; `babylonjs` 9.36.0 against the rig's 9.32.0. Four values moved since the first ledger entry. The ledger's evidence levels are worth copying: `git` (strongest), `pkg`, `web` (secondary), `inferred`; unreachable hosts are named so a blocked probe is not read as "no change".

## Heuristics

| ID | Rule (imperative, at most 30 words) | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-BLE-1 | Never score an importer by whether its re-export validates; validate the source, then score fidelity against the source's render. | **[C]** | a 3-error source re-exported with 0 errors while two of three defects lost their data (section 9) | `x3d_mcp fork b4efcd3`, `bpy 5.3.0` |
| H-BLE-2 | Quote the rule next to every coverage number; a count without its counting rule is not comparable. | **[C]** | 54 written by the teardown against 46 by a naive literal scan, same checkout family | `X3DUOM 4.1`, `x3d-blender-io@ab99988` |
| H-BLE-3 | Treat a centre-patch match as proof of the fit's anchor only; read `geometry_delta` across the whole scene. | **[C]** | p2 centre 204 against 203 yet `geometry_delta` 47.07 | `X_ITE 16.7.1`, `Babylon.js 9.32.0`, Chrome 153 SwiftShader |
| H-BLE-4 | Import classic X3D colours as sRGB and write PhysicalMaterial colours linear; choose per material model, not per file. | **[L]** | README: X_ITE reads classic colours as display values, physical as linear; round-trip tests pass | `X_ITE 16.7.1` (README), `bpy 5.3.0` tests |
| H-BLE-5 | Pick Light Units BLENDER for a scene that starts in Blender and X_ITE for a scene that starts in an X3D file. | **[C]** | Babylon.js centre patches 30, 27, 120, 30 under BLENDER units against 74, 203, 203, 56 under X_ITE units, where X_ITE draws 74, 204, 204, 57 | rig re-run, `bpy 5.3.0` |
| H-BLE-6 | Pin the rig's renderer versions and re-measure the probes before moving a pin. | **[C]** | Babylon.js latest 9.36.0 against the pinned 9.32.0 on 2026-11-14 | `npm view`, rig `package.json` |
| H-BLE-7 | Clamp every colour that comes from a formula or a float attribute to [0, 1] before export, then gate. | **[C]** | channel 1.0059 fails the XSD pattern; baked raw channels reach 1.9151 | `x3d_mcp fork b4efcd3`, `bpy 5.3.0` Cycles CPU |
| H-BLE-8 | Run the loss audit on the source scene before export; after the round trip it is empty. | **[S]** | carried from a private verifier note | not re-run |
| H-BLE-9 | A valid glb proves structure only; check it is not empty and list the extensions the validator did not know. | **[L]** | rig README: unknown extensions are INFO only; `extensionsNotValidated` lists them | `Khronos glTF-Validator 2.0.0-dev.3.10` |
| H-BLE-10 | Compare counts from the run, not the AST: the AST gave 336 test functions, the run gave 335. | **[C]** | one helper `test_the_validator_loads` is not reported by the runner | `bpy 5.3.0`, unittest |
| H-BLE-11 | When a document and the code disagree (194 against 195 cases; "3.3" against `version="3.0"`), cite the code and demote the document to Suspected. | **[C]** | suite run 195; export header 3.0 | `bpy 5.3.0`, `x3d-blender-io@ab99988` |
| H-BLE-12 | Map survey tags to grades by rule: [V] to Likely, [R] and [I] to Suspected, Confirmed only after reproduction with a named instrument. | **[C]** | the knowledge base states and applies the rule; sections 10 and 11 apply it | knowledge base v1 (read) |
| H-BLE-13 | Re-probe a "future feature" the day its wheel ships: a release build settles enum values, operators and missing exports in minutes. | **[C]** | `POINTS` not `POINT`; `ply_export` wrote 0 vertices; `spz_import` only | `bpy 5.3.0` |

## Drills

### D-BLE-1 Which version does an exported file claim?
- **Level:** L2
- **Task:** Export a scene as X3D 4.0 and compare the `generator` meta with the manifest version.
- **Verify:** `grep -n '^version' source/blender_manifest.toml`; `grep -n '"version"' source/__init__.py`; `grep generator out.x3d`.
- **Answer:** manifest `2.6.4`; `bl_info` `(2, 6, 1)`; the file says `X3D Blender I/O v2.6.1`.
- **Checked:** 2026-11-14 `bpy 5.3.0`, `x3d-blender-io@ab99988`.

### D-BLE-2 Reproduce the colour trap
- **Level:** L3
- **Task:** Push one `ColorRGBA` channel to 1.0059, validate before and after, then say why no renderer would have shown it.
- **Verify:** `validate_xml` from `x3d_mcp@b4efcd3` (`sys.path.insert(0, 'src')`, `from validation.validate import validate_xml`).
- **Answer:** clean file 0 errors; edited file 1 error, `Element 'ColorRGBA', attribute 'color': [facet 'pattern']` naming the value. Renderers clamp or ignore it.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3`, `bpy 5.3.0`.

### D-BLE-3 Count the tests two ways
- **Level:** L2
- **Task:** Count `test_*` functions with `ast`; run the runner without and with `bpy`; explain each difference.
- **Verify:** `python3 -B .github/scripts/run_tests_in_blender.py | tail -4`; for the glb tests set `GLTF_VALIDATOR_DIR` and `GLTF_VALIDATOR_REQUIRED=1`.
- **Answer:** AST 336 in 35 files (274 bpy in 30, 62 plain). No `bpy`: 62 OK. With `bpy`: 335 ran, OK, 10 skipped (`test_glb_validator_bpy`); with the validator those 10 pass. The gap of one is `test_the_validator_loads`.
- **Checked:** 2026-11-14 `bpy 5.3.0`, `gltf-validator 2.0.0-dev.3.10`.

### D-BLE-4 A matching centre, a failing scene
- **Level:** L3
- **Task:** Run the five probes with Light Units `X_ITE` and with `BLENDER`. For p2 read the three patches and `geometry_delta`; say which number to trust.
- **Verify:** `compare.py LABEL ../../source probes.json`, then `out/LABEL/results.json`.
- **Answer:** centre, X_ITE / Babylon.js, X_ITE units: 74/74, 204/203, 204/203, 57/56, 78/78; BLENDER units: 74/30, 204/27, 204/120, 57/30, 78/78. p2 `geometry_delta` 47.07 (left box 109 against 167, right 190 against 97): trust `geometry_delta`.
- **Checked:** 2026-11-14 `X_ITE 16.7.1`, `Babylon.js 9.32.0`, Chrome for Testing 153.0.8010.12 SwiftShader, `bpy 5.3.0`.

### D-BLE-5 Is a re-export evidence of a good importer?
- **Level:** L2
- **Task:** Take an X3D with a colour of 2.5, an unknown attribute and a Box outside any Shape. Validate, import, export as 4.0, validate, and list what information changed.
- **Verify:** `validate_xml` on both files; read the re-export.
- **Answer:** source 3 errors, re-export 0. Changed: colour clamped then converted (`0.214041`, `0.010023`), `Material` became `PhysicalMaterial`, the attribute and the stray Box gone.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3`, `bpy 5.3.0`.

### D-BLE-6 Splat bytes, from the writer
- **Level:** L2
- **Task:** Write 1,000 synthetic splats at SH degree 0 to 3 with `splat_io.write_ply`; compute bytes per splat after the header.
- **Verify:** `python3 -B` with `sys.path.insert(0, 'source')`, `from ir import IRGaussianSplats`, `import splat_io`.
- **Answer:** 68.0, 104.0, 164.0, 248.0 bytes (17, 26, 41, 62 floats); each reads back at its degree; 10 million at degree 3 is 2.48 GB.
- **Checked:** 2026-11-14 `x3d-blender-io@ab99988`, Python 3.13.18.

### D-BLE-7 Can Blender 5.3 export a splat?
- **Level:** L3
- **Task:** Build a native splat with `splat_native.build_native_splat_pointcloud`, select it, call `bpy.ops.wm.ply_export`; list operators named for `splat`, `spz` or `gaussian`.
- **Verify:** `bpy 5.3.0`; `dir(bpy.ops.<module>)` over all modules.
- **Answer:** type `GAUSSIAN_SPLAT`; the PLY is 156 bytes with `element vertex 0`; operators: `wm.spz_import` and the unrelated `graph.gaussian_smooth`. Extension: export with `export_scene.x3d`, `x3d_version='X3D41'` and validate on 4.1.
- **Checked:** 2026-11-14 `bpy 5.3.0` (PLY export and operator list ran; the 4.1 export is covered by the test pass, not re-run here).

### D-BLE-8 Grade a Survey claim
- **Level:** L1
- **Task:** The Survey tags "X_ITE 16.6.0 reads splat PLY, SPZ and SOG" with [V]. Give the grade, what Confirmed needs, and the instrument string.
- **Verify:** the grading map in section 10; the instrument rule in AUTHORING section 2.
- **Answer:** **Likely**. Confirmed needs a run: load an SPZ and a SOG in `X_ITE 16.6.0` or 16.7.1 on a named rig. A later study contradicted it without a source line; neither is Confirmed.
- **Checked:** not run

### D-BLE-9 A toy bake, gated
- **Level:** L3
- **Task:** Bake Cycles DIFFUSE (direct plus indirect) to a corner `FLOAT_COLOR` attribute on a grid plus a box, apply the finish steps, export X3D 4.0, validate. Report raw maximum, exposure and final maximum; then set a channel to 1.0059 and re-validate.
- **Verify:** `scene.render.bake.target = 'VERTEX_COLORS'`, `bpy.ops.object.bake(type='DIFFUSE')`; `validate_xml`.
- **Answer:** 280 corners at 16 samples: raw maximum 1.9151, exposure 0.7569, final maximum 0.9696, 9,356 bytes, valid; the 1.0059 edit fails the colour pattern. Write the receipt this toy run skipped: Blender version, script and file sha256, percentile.
- **Checked:** 2026-11-14 `bpy 5.3.0`, `x3d_mcp fork b4efcd3`.

## Honest limits

- **[C]** Everything was run at `x3d-blender-io@ab99988` on `bpy 5.3.0`, Python 3.13.18. CI uses Blender 4.5.14, 5.1.2, 5.2.2 and a Python 3.11 wheel job; none of those was run here.
- **[C]** The rig re-run launched the installed Chrome for Testing 153.0.8010.12 in a scratch copy instead of Playwright's own download. Numbers matched the README to the integer, but its browser path was not literally followed. Only the five probes were run; the 34-scene sweep, nine x3d.demo scenes and two Blender-lab scenes are README figures, **[L]**.
- **[C]** X_ITE was not opened on the toy bake or the conformance exports; only the validator gated them. Valid is not "looks right".
- **[S]** Bake-stage traps beyond the colour clamp, the village numbers, the bridges, the tool tiers and ecosystem versions before 2026-11-14 are carried from private notes and the skill text; several bridges refer to private repositories, so their inputs cannot be re-run from public files.
- **[L]** Node coverage 54 and 68 is the teardown's; my naive scan gives 46 and 65. The teardown's CI figures (33 successes, 5 cancelled, 0 failed in 38 pushes) were not re-fetched.
- **[C]** RigidBodyPhysics is among the 17 untouched components; a physics scene from another tool would not survive an import here (teardown inference, not run); see `13-physics.md`.
- **[S]** Sources that disagree, code wins: 194 against 195 cases (code 195); `POINT` against `POINTS` (bpy `POINTS`); upstream "X3D 3.3" against a written 3.0 header (code 3.0); `bl_info` 2.6.1 against manifest 2.6.4 (both in the checkout, unresolved).
- **Not shown:** a Castle, Unreal or path-traced leg (chapters 09 and 12). Unpublished scenes and upstream reports not yet public are left out on purpose.

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-BLE-1 | `test_*` functions (AST) | 336 in 35 files (274 in 30 bpy files) | **[C]** | Python 3.13.18 `ast` | x3d-blender-io@ab99988:tests/ |
| N-BLE-2 | tests run without `bpy` | 62, OK | **[C]** | unittest runner | x3d-blender-io@ab99988:.github/scripts/run_tests_in_blender.py |
| N-BLE-3 | tests run with `bpy` | 335 ran, OK, 10 skipped (glb validator absent) | **[C]** | `bpy 5.3.0` | same |
| N-BLE-4 | glb-validator tests with the validator present | 10 of 10 pass | **[C]** | `gltf-validator 2.0.0-dev.3.10`, `bpy 5.3.0` | x3d-blender-io@ab99988:tests/test_glb_validator_bpy.py |
| N-BLE-5 | conformance cases | 195 = 148 CORE + 21 FIDELITY + 26 ROADMAP | **[C]** | `tests/suite/x3d_test_suite.py` on `bpy 5.3.0` | x3d-blender-io@ab99988:tests/suite/README.md |
| N-BLE-6 | CORE pass, ROADMAP, FIDELITY | 148/148; 21 MISSING + 5 NEW; 19 WARN + 2 PASS | **[C]** | `validate_x3d_export.py`, `bpy 5.3.0` | same |
| N-BLE-7 | suite exports valid | main 7,010,591 B (4.0), crease 4,911,800 B (4.0), x41 4,617,408 B (4.1), 0 errors | **[C]** | `x3d_mcp fork b4efcd3` | same |
| N-BLE-8 | concrete nodes in X3DUOM 4.1 | 267 | **[C]** | XML count of `ConcreteNode` | x3d_mcp@b4efcd3:src/validation/schemas/X3dUnifiedObjectModel-4.1.xml |
| N-BLE-9 | nodes written / read, teardown | 54 / 68 (base 39 / 42), both 43 | **[L]** | teardown method, not reproduced | x3d.docs@f172f67:docs/x3d-blender-io/MASTERCLASS.md |
| N-BLE-10 | nodes written / read, naive literal scan | 46 / 65, both 38 | **[C]** | rule in section 3 | x3d-blender-io@ab99988:source/ |
| N-BLE-11 | probe centre patch, X_ITE units (X_ITE / Babylon.js) | 74/74, 204/203, 204/203, 57/56, 78/78 | **[C]** | `X_ITE 16.7.1`, `Babylon.js 9.32.0`, Chrome 153 SwiftShader | x3d-blender-io@ab99988:tools/fidelity_rig/probes.json |
| N-BLE-12 | probe centre patch, BLENDER units (Babylon.js) | 30, 27, 120, 30, 78 | **[C]** | same | same |
| N-BLE-13 | p2 `geometry_delta` | 47.07 (centre 204 against 203) | **[C]** | same | same |
| N-BLE-14 | glb validator on the five probe glbs | 0 errors, 0 warnings, 3 infos each | **[C]** | `Khronos glTF-Validator 2.0.0-dev.3.10` | x3d-blender-io@ab99988:tools/fidelity_rig/validate_glb.mjs |
| N-BLE-15 | PLY bytes per splat, SH 0 to 3 | 68, 104, 164, 248 | **[C]** | `splat_io.write_ply`, 1,000 splats | x3d-blender-io@ab99988:source/splat_io.py |
| N-BLE-16 | toy bake: raw max, exposure, final max, bytes | 1.9151, 0.7569, 0.9696, 9,356 B (280 corners) | **[C]** | `bpy 5.3.0` Cycles CPU 16 spp, `x3d_mcp fork b4efcd3` | (scratch script; reproduced by D-BLE-9) |
| N-BLE-17 | add-on version strings | manifest 2.6.4; `bl_info` 2.6.1; generator meta v2.6.1 | **[C]** | `grep`, export header | x3d-blender-io@ab99988:source/blender_manifest.toml, source/__init__.py |
| N-BLE-18 | legacy exporter header | `<X3D version="3.0">` for the option labelled "X3D 3.3" | **[C]** | run of an X3D33 export | x3d-blender-io@ab99988:source/export_x3d.py:342 |
| N-BLE-19 | native splat type values | `['POINTS', 'GAUSSIAN_SPLAT']`; `wm.ply_export` of a splat: 0 vertices, 156 B | **[C]** | `bpy 5.3.0` | probe (D-BLE-7) |
| N-BLE-20 | npm and PyPI latest on 2026-11-14 | bpy 5.3.0; x3d 4.0.65.8; x_ite 16.7.1; babylonjs 9.36.0 (rig pins 9.32.0) | **[C]** | `pip index versions`, `npm view` | registries |
| N-BLE-21 | source size | 16,753 lines in `source/*.py`; `import_x3d.py` 7,340; `export_x3d.py` 1,985 | **[C]** | `wc -l` | x3d-blender-io@ab99988:source/ |
| N-BLE-22 | demo scenes, Blender units to X_ITE units, `geometry_delta` | 40.5 to 25.3 (ontology constellation), 37.3 to 13.7 (materials shelf) | **[L]** | rig on nine scenes, README | x3d-blender-io@ab99988:README.md |
| N-BLE-23 | baked village file growth | 26 KB to 330 KB gzipped | **[S]** | carried from the bake-stage skill text | skill text, receipt not public |
| N-BLE-24 | bridges first graded Confirmed that verified lower | 12 of 13 | **[S]** | verifier pass in a private note | carried, not re-checked |

## Sources and provenance

- **Repos read:** `x3d-blender-io@ab99988` (merge of PR #39, manifest 2.6.4) read and run; `x3d_mcp@b4efcd3` for `validate_xml` and X3DUOM 4.1; `x3d.docs@f172f67` for [the x3d-blender-io masterclass](../x3d-blender-io/MASTERCLASS.md), measured at `e071a61` on 2026-11-13.
- **Run 2026-11-14:** venv with `bpy 5.3.0` (427.5 MB wheel, Python 3.13.18) and `x3d 4.0.65.8`; Node 22 with `gltf-validator 2.0.0-dev.3.10`, `x_ite 16.7.1`, `babylonjs 9.32.0`; Chrome for Testing 153.0.8010.12 with SwiftShader; no GPU, no paid service.
- **Private leads, re-derived or graded [S]:** the sci-vis knowledge base (v1, v1.1), the flywheel study, the upstream-state study, the ecosystem map, ledger and routine, the bake-stage skill. Not linked; figures are re-derived above or marked carried.
- **Siblings:** [01 The tether](01-the-tether.md), [03 Validator and gates](03-validator-and-gates.md), [04 MCP for agents](04-mcp-for-agents.md), [05 The semantic layer](05-semantic-layer.md), [06 X_ITE, the reference renderer](06-xite-the-oracle.md), [07 X-ray](07-xray.md), [08 The Babylon bridge](08-babylon-bridge.md), [09 Castle Engine](09-castle-engine.md); later chapters `11-gltf-usd-khronos.md`, `12-unreal-tier1.md`, `13-physics.md` as plain names until they exist.
