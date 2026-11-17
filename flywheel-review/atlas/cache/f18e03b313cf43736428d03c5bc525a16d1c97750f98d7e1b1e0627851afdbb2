# 09. Castle Game Engine as an X3D host

> **Say it:** Castle is a native Pascal engine whose internal model is the X3D node graph, which makes it the best-mapped host we examined for seam knowledge and traps; nothing measured here shows it leading on node coverage, conformance, fidelity or standard-setting, and the one comparator we ran (X_ITE) is ahead on fidelity and, at the name rung, on node coverage. **[C]**

| field | value |
|---|---|
| chapter code | `CAS` |
| prerequisites | [01 The tether](01-the-tether.md) for the loop; [03 The validator and the gates](03-validator-and-gates.md) for what a validator can and cannot see; [06 X_ITE, the reference renderer](06-xite-the-oracle.md) for the comparator |
| after this you can | (1) say what X3D is inside Castle and what it is not; (2) count loaders, savers and parse-only nodes with a script and name the denominator; (3) state three event-model traps and the light-model difference with the line that causes each; (4) read a Castle fidelity number with its rig, its reference and its blind spots; (5) say which sentences about Castle are allowed and which the evidence forbids |
| sources read | x3d.castle@d70e00c:{README.md, docs/*.md, docker/, castle-convert/x3dcastleexport.pas, castle-render/castle_render.dpr, tools/, tests/phase3_check.py, results/}; castle-engine@48ce617:src/scene/{x3d/{castleinternalnodesunsupported.pas, x3dnodes_standard_time.inc, x3dnodes_standard_navigation.inc, castlefields_misctypes.inc}, load/{x3dload.pas, x3dloadinternalgltf.pas, pasgltf/CastlePasGLTF.pas}, glsl/source/, castlescenecore.pas}, tests/code/testcases/testx3dnodes.pas |
| instruments used | `castle-engine@48ce617` (public master, 2026-11-10, read through a sparse checkout, not built); Castle 7.0-alpha.3 snapshot, FPC 3.2.2, Mesa llvmpipe for every carried render number; `Khronos glTF-Validator 2.0.0-dev.3.10`; `X_ITE 16.7.1` (npm dist read for class names, not run here; the carried rig numbers ran it in Chromium 153.0.8010.12, SwiftShader); `x3d_mcp fork b4efcd3`; Python 3.13.18; Node 22.23.4; `x3d.castle@d70e00c` |

Everything tagged "run 2026-11-14" was run in a software-only container (4 vCPU, no GPU). Other render numbers are carried from the receipts under `x3d.castle@d70e00c:results/`, re-derived from their JSON where I say so. The Castle source I could read is public master `castle-engine@48ce617`; the renders ran on a 7.0-alpha.3 snapshot bundle with no `.git`, so the two are the same tree only by timing (snapshot built 2026-11-12, last master commit 2026-11-10) **[L]**.

## 1. The map

```text
  files (x3d x3dv wrl glb gltf obj stl ply dae 3ds md3 ifc spine tmx ...)    21 registrations
      v  URL funnel + MIME-keyed registry (RegisterModelFormat)                7 with OnSave
  X3D NODE GRAPH   data: fields, ROUTEs, PROTO expanded, Inline loaded; 43 change classes
      |  (Castle-only nodes leak in: Skin, Effect, ScreenEffect, GeneratedShadowMap)
      v
  TCastleScene  (= TCastleTransform, a member of the engine tree, which is NOT X3D)
      v  ChangedAll / change classes
  SHAPE TREE   the evaluated scene: geometry + world matrix + lights + LOD/Switch wrappers
      |--> renderer: GLSL from plugs, one program per feature hash (llvmpipe here)
      |--> octrees, ray picking, physics colliders
      '--> OUR exporter (x3d-castle-convert): shape tree -> glb      70 of 70 validator-clean
```

| layer | what it holds | is it X3D | what we measured or read | instrument |
|---|---|---|---|---|
| file formats | 21 registered loaders, 7 savers | partly (3 of the 7 savers write X3D or VRML) | counted by script, section 3 | `castle-engine@48ce617` |
| node graph | the content of one asset | yes, natively; even a glb becomes X3D nodes | 11 groups parse-only, section 4 | `castle-engine@48ce617` |
| engine tree | the world: transforms, viewport, camera, components | no; persistence is JSON design files | read, section 2 | field-guide map, [L] |
| shape tree | the evaluated, flattened scene | derived from the graph | our exporter reads it, section 8 | `x3d.castle@d70e00c` |
| renderer | GLSL composed from plugs | n/a | quality leg, section 7 | llvmpipe, carried |

**In scope:** what Castle taught us about hosting X3D: loader and node inventory, event and light traps, the quality leg, our glb exporter, reproduction, the gap list, the critic's verdict, rules to copy or distrust. **Out of scope:** Castle's game-engine features, the 7.x line beyond the snapshot, and any peer engine (none was opened; section 11).

**Read next:** deeper, `x3d.castle@d70e00c:docs/exporter.md` and `docs/quality-leg.md` (this chapter re-derives their headline numbers); wider, [08 The Babylon bridge](08-babylon-bridge.md) for the other independent reader, and [10 The Blender pipeline](10-blender-pipeline.md) for the add-on whose reading of a file is the reference in section 7.

## 2. What Castle is, and what X3D is inside it

Castle is an Object Pascal engine that compiles every model format into one intermediate representation, an X3D node graph, then runs and draws that graph: a compiler front end plus a runtime **[L]** (field-guide readers; I re-read the registry and the unsupported-node unit at master, sections 3 and 4).

| fact | consequence for hosting X3D | grade | source |
|---|---|---|---|
| `TCastleSceneCore` is a `TCastleTransform`; the world is the engine tree, saved as JSON design files | a Viewpoint, Background or Fog in an X3D file reaches the viewport only through the deprecated `MainScene` path | [L] | field-guide map; `x3d.castle@d70e00c:castle-render/castle_render.dpr:713` says our harness uses `MainScene`, `UseHeadlight`, `AutoCamera`, all deprecated |
| nodes are data, shapes are the evaluated scene | the node walk and the shape walk can disagree (LOD, below) | [C] | `x3dnodes_standard_navigation.inc:607-616` against `x3dcastleexport.pas:1494-1507` |
| unknown classic-encoding nodes are skipped to the matching brace; a top-level read error warns once and stops the file | a classic file can load half its shapes and report success | [C] | `x3dnodes_x3dunknownnode.inc:56-90`; `x3dnodes_encoding_classic.inc:569-573` |
| Castle-only nodes share the graph with standard ones | saving or exporting can leak `Skin`, `Effect`, `ScreenEffect`, `keyValueQuaternions` | [L] | field-guide map (extension ledger) |
| `ProcessEvents` defaults to false | a still render never runs a ROUTE unless the harness turns events on | [C] | `castlescenecore.pas:2336-2337`; `castle_render.dpr:830` sets it true |

```text
  one file, three readers, three answers to "which LOD child is drawn?"
   node walk  (DirectEnumerateActive)  -> child 0, always ("always use the best LOD version")
   shape walk (TShapeTreeLOD.Level)    -> chosen from the camera distance, while rendering
   our exporter (UpdateLods)           -> sets Level once from the bound Viewpoint
```

A census or checker that enumerates nodes and a renderer that enumerates shapes disagree on any scene with `LOD` **[C]** for the two code paths (read; the disagreement itself was not run).

## 3. Loader and saver inventory: 21 and 7, counted

Method **[C]**, run 2026-11-14 on `castle-engine@48ce617`: every `ModelFormat := TModelFormat.Create; ... RegisterModelFormat(ModelFormat)` block under `src/`, minus the example in the doc comment of `x3dload.pas`; a saver assigns `ModelFormat.OnSave`. `RegisterModelFormat` refuses a duplicate MIME type, an empty MIME list or filter name, and an extension without its leading dot (`x3dload.pas:813-840`).

| # | format | extensions | saver |
|---|---|---|---|
| 1 to 3 | X3D XML; X3D classic; VRML | `.x3d .x3dz .x3d.gz`; `.x3dv .x3dvz .x3dv.gz`; `.wrl .wrl.gz .wrz` | yes, yes, yes (VRML writes classic) |
| 4 | Inventor | `.iv` | no |
| 5, 6 | glTF binary, glTF JSON | `.glb`, `.gltf` | yes, yes (the stock writer, section 8) |
| 7, 8 | STL, IFC | `.stl`, `.ifc .ifcjson` | yes, yes |
| 9 to 17 | OBJ, PLY, Collada, 3DS, MD3, Videoscape, Spine, Tiled TMX, images | one or two each | no |
| 18 to 21 | Cocos2d plist, Castle and Starling sprite sheets, Castle animation frames | `.plist`, `.castle-sprite-sheet`, `.starling-xml`, `.castle-anim-frames .kanim` | no |

Reading rules **[C]**: 21 and 7 are *registrations*, not working conversions. The whole-file X3D write-then-read test upstream has both calls commented out (`tests/code/testcases/testx3dnodes.pas:392-393`), so no suite there round-trips an X3D file. There is no X3D JSON or binary encoding. Breadth is a statement about inputs.

## 4. Node coverage: eleven groups, 99 registrations, three states

One internal unit holds X3D nodes Castle parses, keeps and saves but does not run; its header says "we can perfectly read and write them in X3D, but nothing more" (`castleinternalnodesunsupported.pas:16-25`) **[C]**. Run 2026-11-14 (`xite_names.py`, section 13) on `castle-engine@48ce617` and the `x_ite@16.7.1` npm dist:

| group | Castle registrations | same-named non-abstract class in X_ITE 16.7.1 | the misses |
|---|---:|---:|---|
| Geospatial, DIS, Layering, Layout, Picking, ParticleSystems, VolumeRendering | 11, 6, 3, 5, 5, 10, 13 | all | none |
| RigidBodyPhysics, Followers | 14, 10 | all | none |
| TextureProjector | 3 | 2 | `AbstractTextureProjector` (abstract, registered anyway) |
| SoundX3D4 | 19 | 18 | Castle `Oscillator`; X_ITE `OscillatorSource` (spec spelling not checked) |
| **total, 11 groups** | **99** | **97** | |

* The older figures ("98 concrete", "98 of 328", "/332", "/265") are five denominators for one fact. Here: entries in the 11 `RegisterNodeClasses([...])` lists, one abstract, so 98 concrete. The whole tree has 333 names in 43 calls (VRML 1.0 `_1` classes and Castle-only nodes included, so not a count of X3D 4.0 nodes) **[C]**.
* X_ITE 16.7.1 has 292 non-abstract classes by `getStaticProperties` (not reconciled with the 294 of [chapter 06](06-xite-the-oracle.md), a marker count on 16.7.0). **Name presence is the weakest rung**: not "creates", not "draws". Behaviour in X_ITE was not tested **[S]**.
* The critic's pre-registered refutation test for "Castle leads on node coverage" was: X_ITE implements more than half of the 11 groups. At the name rung it carries 11 of 11, so the sentence fails there; how well those nodes behave stays open.
* The reverse: X_ITE has 33 names Castle does not register, among them `GaussianSplats`, `GaussianSplatsShape` and 13 `*MaterialExtension` classes. Castle fails on `GaussianSplats` at load (`Unknown X3D node type`, [gap 1](#10-the-gap-list-and-what-became-of-it)).
* "Parse-only" is not "does nothing": the nodes enter the graph with their fields, so conversion and editing tools work. Some groups have a Castle-native replacement (physics, particles). More inert nodes sit inside "supported" components (`TransformSensor`, `Spline`, `Squad`, parts of NURBS) **[L]**; nobody counted behaviour node by node.

```text
  three states of support, and what each hides
   absent      unknown node: body dropped, one warning, a classic file may stop  GaussianSplats
   parse-only  in the graph, saved back, no behaviour                    99 registrations
   behaves     drawn, simulated or wired                                 the rest; depth unmeasured
  the loader does not say which state a node is in; only the unit holding the class does.
  A host receipt must list the nodes used, by state.
```

## 5. Event model traps

| trap | what the code says | grade | do |
|---|---|---|---|
| `ProcessEvents` off by default | `property ProcessEvents ... default false`; "If false, this all doesn't work, which makes the scene static" (`castlescenecore.pas:2336-2337`). Viewers and the editor turn it on | [C] code; viewers [L] | set it explicitly and record it |
| a TimeSensor first ticking exactly at `startTime` emits nothing | `SetElapsedTime` sends only if `Value <> FElapsedTime` (`x3dnodes_standard_time.inc:333-337`); `fraction_changed` and `time` are sent only from `EventElapsedTimeReceive` (`:768-785`); a later `Fraction = 0` is corrected to 1 (`:776`) | [C] read, not run | treat frame 0 as unverified; build D-CAS-7 |
| LOD shows child 0 in the node walk | `DirectEnumerateActive` returns `FdChildren[0]` (`x3dnodes_standard_navigation.inc:607-616`) | [C] | use the shape tree's level |
| a node cannot serve two scenes; start, stop and pause edits re-enter `SetTime` | field-guide trap list (`castlescenecore.pas:4839` is `HandleChangeTimeStopStart`) | [L] | deep-copy; a trace recorder must catch those entries |
| no test guards any of it | no match for `NextEventTime`, `PlusTicks`, `elapsedTime` or `fraction_changed` under `tests/code` | [C] grep, 2026-11-14 | put event-order fixtures in the host witness |

Who owns the TimeSensor origin behaviour is unresolved (the code comment cites a game-restart case): do not call it a spec trap before the spec's initial-time rule is quoted **[S]**. Our exporter's `--events-at=T` sets `ProcessEvents := true`, calls `Scene.SetTime(T)` and reads node fields (`x3dcastleexport.pas:2342-2348`); a value driving a shader uniform is not reached, and Castle's time starts at 0 where a page clock does not **[C]** read.

## 6. Rendering architecture and the light-model difference

The renderer splices named plugs into fixed GLSL templates and keys programs by a hash of the feature set; the plug idea is Castle-only, not in X3D 4.0 **[L]**.

```text
  shape -> TShader state (lights, fog, textures, effects) -> feature hash (sum/xor of primes)
        -> hit: no GLSL text built       miss: LinkProgram builds GLSL from plugs
        -> fragment: material, add_light per light, ambient, emissive, tone map, fog
  one GLSL source targets legacy GL, GL 3.1 core, GLES 3, WebGL2; a #version header is added
  unless the source starts with one      <- gap 2 lives here
```

| fact | grade | source |
|---|---|---|
| Phong and Physical models each have an `add_light.glsl`; both divide by `max(1.0, a.x + a.y*d + a.z*d*d)` and cut at `radius` | [C] | `castle-engine@48ce617:src/scene/glsl/source/lighting_model_phong/add_light.glsl:118-123`, `lighting_model_physical/add_light.glsl:123-128` |
| the glTF importer writes `Attenuation := (0, 0, 1)` on every glTF point and spot light, commenting that plain X3D defaults to none and would be "incredibly bright" | [C] | `x3dloadinternalgltf.pas:738-751` (TODO for `range`) |
| X3D files loaded directly get no such change: one PhysicalMaterial draws differently from an `.x3d` and a `.glb` | [C] | the two reads above |
| three authoring contracts: X3D nodes (intensity 1, attenuation `1 0 0`), glTF loader (`0 0 1`), Castle light components (`0 0 1`, intensity 100) | [L] | field-guide map; component defaults not re-read |
| no exposure setting: `u_Exposure` is commented out | [C] | `src/scene/glsl/source/tone_mapping.fs:21,114` |
| a still render needs the engine's update step before any shadow map exists | [L] | gap row 17 |

Worked example, arithmetic on the shader formula **[C]**: attenuation `1 0 0` gives `1/max(1, 1) = 1` at every distance; `0 0 1` at 3 m gives `1/max(1, 9) = 1/9`, so the first is 9 times brighter. At 0.5 m both give 1 (the `max(1, ...)` floor), so an "attenuation 0 0 1" adapter does not make Castle inverse-square for lights closer than 1 unit. Whether X3D 4.0 (clauses 17.2.2.3, 17.2.2.6) demands the first or the second for a PhysicalMaterial **was not quoted verbatim by anyone yet** **[S]**. "Castle is wrong here" is unsupported; "Castle differs from X_ITE and the reference, in this one line" is supported.

## 7. The quality leg: how close does each renderer get to a path-traced image?

Rig, **[C]** from `x3d.castle@d70e00c:results/quality/public/results.json` (`run_quality.py v1`, 2026-11-13): Blender 5.3.0 Cycles reference, 256 spp, no denoise, ideal point lights; x3d-blender-io add-on commit `603ca7a` imports the file; `X_ITE 16.7.1` and Babylon.js 9.32.0 in Chromium 153.0.8010.12 on SwiftShader through the fidelity rig; Castle 7.0-alpha.3 on Mesa llvmpipe; 512 x 512, no GPU. Metric: mean FLIP (flip-evaluator 1.7), lower is closer. 15 public scenes; "core 11" drops four where the reference itself is wrong (`annotation-standard`, `nurbs-weights`, `quaternion-xyzw`, `p2-point-classic`).

Re-derived with `core11.py` on 2026-11-14 (equal to the repository's table):

| leg | mean FLIP, all 15 | core 11 | independent of the reference's reading? |
|---|---:|---:|---|
| X_ITE 16.7.1 on the X3D file | 0.0748 | 0.0457 | partly: add-on light units are calibrated to X_ITE |
| Babylon on the add-on's glb | 0.0516 | 0.0485 | no, shares the add-on front end |
| Babylon on our Castle glb | 0.0658 | 0.0491 | yes |
| Castle native (`castle-render`, defaults) | 0.1321 | 0.1149 | yes |
| Castle SSAA 4x plus Gouraud (`castle_all`, chosen on these scenes) | 0.1289 | 0.1146 | in-sample choice |

* Castle native differs from the reference by +0.069 on core 11 and beats X_ITE on 4 of 11 scenes. On the other seven core scenes the means are 0.0406 against 0.0386.
* The gap is the light model: `materials-world` plus `lights-after` carry 77.0% of the all-15 gap (0.770). `p1-point-physical` goes 0.0546 to 0.0059 with attenuation `0 0 1` (X_ITE 0.0053): the gap closes. `p4-point-quadratic-physical` goes 0.0446 to 0.0237 against X_ITE 0.0085: 58% closes, the rest is unexplained. "Most of the gap is the light model" is true for p1 and barely for p4.
* Say "differs", not "behind": the reference is Cycles on the add-on's reading, and the Castle side reads the field as written **[S]** pending the spec clause.
* Castle's switches are worth less than the gap. Change in mean FLIP against native, re-derived over 15 scenes: SSAA 4x -0.0027, SSAA 2x -0.0018, MSAA 4x -0.0003, anisotropy 16 -0.0001, Gouraud -0.0004; shadow maps +0.0040 (9 scenes, file-literal reference); SSAO +0.0065; SSR +0.0002; tone maps +0.0228 to +0.0352; colour-space overrides +0.0443 and +0.1118; PBR mapping of classic Material +0.0079; environment light +0.0437. The reported -0.0106 for shadow maps against an all-lights-cast reference was not re-derived.
* The reference rewards omission: the add-on drops `NurbsCurve` and flattens a gradient Background; on `quaternion-xyzw` (`GaussianSplats`) a near-empty frame scores 0.1548 against X_ITE's correct 0.1962.
* Defensible reading **[L]**: a fast (about 0.5 s a frame here, against 3 to 6 s for the browser legs and 47 s for the reference), scriptable second reader of X3D that can be driven headless; not shown to be the quality renderer. n = 15, no GPU, one reference. The X_ITE side is in [chapter 06](06-xite-the-oracle.md), the add-on side in [chapter 10](10-blender-pipeline.md).

## 8. Our own glb exporter: shape tree to glb

`x3d-castle-convert` (`x3d.castle@d70e00c:castle-convert/x3dcastleexport.pas`, 2,412 lines by `wc -l`; the README says "about 1,700" and `docs/exporter.md` "about 2,500", both stale **[C]**) links against Castle's public units and walks the **shape tree**, taking each shape's `TShape.GeometryArrays`, the buffers Castle uploads to the GPU. What Castle draws is what ends up in the file. The stock writer (`SaveGLTF`) walks the node graph by hand and would have to re-implement every feature Castle resolves for rendering.

```text
  x3d file -> node graph -> Scene.Load -> shape tree --UpdateLods(Viewpoint)   [LOD: one level]
                                              |       --events-at=T           [opt-in: one frame]
                                              v
   per shape: world matrix + GeometryArrays -> POSITION NORMAL TEXCOORD_n COLOR_0 TANGENT
   per scene: Viewpoint -> camera; lights -> KHR_lights_punctual; headlight -> directional light
                                              v  OUT.glb + OUT.glb.export.json (counts, warnings)
   gates: glTF-Validator (0 errors, 0 warnings) -> census (what survived) -> rig (how it looks)
```

Stock writer against the shape-tree exporter over the 70 unique x3d.demo scenes, re-derived from `results/scout-70/` and `results/phase3/gate70-default/` **[C]**:

| measure | stock writer | exporter, phase 3 default | instrument |
|---|---:|---:|---|
| glbs failing the validator | 24 (14,379 errors) | 0 errors, 0 warnings, 70 clean (77 INFO) | `Khronos glTF-Validator 2.0.0-dev.3.10` |
| lit scenes keeping their lights | 0 of 43 | 41 of 43 | `census_compare.py` receipts |
| cameras kept | 0 of 55 | 55 of 55 | same |
| textures, vertex colours, lines, points | 0 | 11/17, 26/27, 14/17, 10/11 | same (the other 6 textured scenes use shader-driven data) |
| meshes written | 2,497 (phantom copies of the previous mesh for shapes with none) | 1,946 | census `meshes_engine`, `meshes_new` |
| animation | 0 | 0 of 21 (not covered) | same |

Rules that cost measurements. The rules are **[C]**, read at the cited lines; the pixel numbers are the repository's recorded results, **[L]**:

| X3D | glTF | rule and measurement |
|---|---|---|
| classic `Material` | metallic-roughness plus `KHR_materials_specular` | black `specularColor` (the X3D default) becomes `specularFactor 0`: `lod-control` 0.1 with the extension, 4.6 without. A coloured one becomes `linear(color)/0.04`, capped by `--specular-max-f0` (default 0.5); uncapped, Babylon 9.32 turned a gold cube teal |
| `PhysicalMaterial`, only `baseColor` | kept | PasGLTF's `GetEmpty` ignores `baseColorFactor` (`CastlePasGLTF.pas:3459-3465`), so roughness 0.9999 forces the block |
| lights | `KHR_lights_punctual`, units converted | physical `i * attenuation(d)`; classic `level(i * attenuation(d)) * d^2`; the rule of the x3d-blender-io importer, so both paths agree |
| spot `beamWidth >= cutOffAngle` | inner < outer, clamped | unclamped, the validator reports `KHR_LIGHTS_PUNCTUAL_LIGHT_SPOT_ANGLES` (drill D-CAS-5) |
| colours | linear | `--colour-space=as-is` moves `village` from 3.5 to 48.8 against X_ITE |
| texture wrap | exporter writes `samplers` | PasGLTF writes `wrapT` under the key `wrapS` (`CastlePasGLTF.pas:5585-5590`, master); exporter side `x3dcastleexport.pas:2267-2294` |

**Fidelity, re-derived.** Rig: x3d-blender-io `tools/fidelity_rig`, X_ITE 16.7.1 against Babylon.js 9.32.0 drawing each glb, Chromium 153.0.8010.12, SwiftShader, 512 x 512, mean absolute pixel difference 0 to 255, 21 scenes where every column exists, no GPU. From `results/phase3/rig-gate-summary.json` (3 repeats, per-scene median) and `results/rig-exporter/results.json` **[C]**:

| run | variant | mean | median |
|---|---|---:|---:|
| phase 2 binary, phase 3 gate | `self` (glb carries camera and headlight) | 7.53 | 1.05 |
| phase 3 default | `self` | 7.80 | 3.40 |
| phase 2 binary / phase 3 default | `rigcam` (rig adds the headlight) | 7.96 / 7.95 | 2.24 / 2.24 |
| phase 2 receipt (published "7.8, median 3.5") | `rigcam` | 7.80 | 0.88 |
| phase 2 receipt | add-on glb / Castle stock glb / `naive` (`as-is`, `light-scale=1`) | 9.22 / 17.62 / 11.42 | 3.56 / 14.09 / 6.10 |

The exporter sits level with, and a little under, the add-on's glb on this rig (7.8 against 9.2) and well under the stock writer (17.6); "level" is the honest word, not "better", because n = 21 and the median is unstable. The published "3.5" is not reproducible from its own receipt (0.88), nor is the stock median 17.1 (14.09 there). In the phase 3 `self` run four scenes (`lights-before` 61.92, `quaternion-xyzw` 21.27, `annotation-standard` 17.94, `nurbs-weights` 15.70) carry 71% of the sum; without `lights-before` the mean is 5.10, and 10 of 21 scenes are under 1.0. The causes are partly known (Text skipped, `GaussianSplats`, NURBS) and partly not (`lights-before` was not investigated **[S]**). Animated scenes land on another phase each run (`villagers` 1.33, 0.52, 1.05 on one byte-identical glb), and four runs of the same 21 scenes gave medians 0.58 (0.25 specular cap), 0.88, 1.05 and 3.40. Report the median with its range or drop it. Phase 3 changed what the glb carries, not the pixel number: every deterministic scene moved by at most 0.01.

Where the new code shows, on fixtures (`results/phase3/rig-fixtures-summary.json`, 2 repeats) **[C]** read: `texture-properties` 9.68 to 0.34; `texcoord-sets` 32.06 to 2.87; `alpha-modes` 5.06 to 1.92; `light-extras` 6.84 to 4.44; `switch-hidden` 2.26 to 0.94. Opt-in `--text-atlas` and `habsburg-timeline` get **worse** (6.90 to 9.41; 8.67 to 9.46) while labels appear: X_ITE draws crisp type, the glb carries a bitmap atlas, and a pixel metric prefers a missing label to a blurry one, so the flags stay off by default. Gate: 18 of 18 fixtures pass on the phase 3 binary against 4 of 18 on phase 2 (`fixtures.json`, `fixtures-baseline.json`, each also validated); README and `docs/reproduce.md` still say 17.

**Not covered** (`docs/exporter.md`, read): animation (`--events-at` writes one frame), skinning, shaders, Billboard, `GaussianSplats`, cube and 3D textures, `global=false` scoping of a `DirectionalLight`, drawn Background and Fog, image-based lighting (`EXT_lights_image_based` is unknown to the validator), `Text` without `--text-atlas`. Not measured: a physical GPU, any viewer but Babylon.js for these glbs, Unreal.

## 9. Reproducibility: pinned bundle, one image, one smoke test

| thing | value | grade | instrument |
|---|---|---|---|
| engine | Castle 7.0-alpha.3 snapshot, linux-x86_64 bundle, FPC 3.2.2 inside it | [C] | `docs/reproduce.md`, `docker/Dockerfile` |
| pin | bundle SHA-256 `4b8935a4d111...` checked with `sha256sum -c` after download; a replaced snapshot fails the build | [C] read | `docker/Dockerfile:25-28` |
| image and smoke test | `ubuntu:24.04`, bundle, exporter and `castle-render` built at image time, Xvfb plus llvmpipe; `smoke.sh` validates, exports a cube, takes a viewer screenshot, calls `castle-render` | [C] read | `docker/Dockerfile`, `docker/smoke.sh` |
| CI | the `docker` workflow ran twice on the public repository, both `success` including the smoke-test step: `80fd146` (8 min 32 s) and `b7cfff9` (2 min 50 s, cached) | [C] `gh run view`, 2026-11-14 | GitHub Actions |
| times | exporter 33 s cold, 2 s warm; 47 s with the bundle's FPC; quality run about 40 min on 4 shared vCPUs | [L] carried | `docs/reproduce.md`, `docker/README.md` |

`docker/README.md` still says the image "has not been built yet"; the CI runs supersede that **[C]**. The image has no GPU, so real MSAA, driver shader compiles and timings are untested.

**The 5.3.0 string.** `docs/reproduce.md` lists `castle-model-viewer / castle-model-converter 5.3.0` beside engine 7.0-alpha.3. Reviewers found the banner "7.0-alpha.3.snapshot" inside both binaries plus a bare `5.3.0`, so 5.3.0 is most likely the tool's own version, not an old engine **[L]** (strings only; binaries not executed, their source is not in the bundle). Do not write "Castle is 5.3.0", and do not attribute `--validate` or `--identify` behaviour to 7.0-alpha.3.

## 10. The gap list and what became of it

`x3d.castle@d70e00c:docs/castle-gaps.md` has 20 rows: 19 Confirmed, 1 Likely (row 17), graded by the repository. I re-checked rows 19 and 20 at source and the exporter-side results. My classification of the 20 rows (a judgment, **[L]**):

| kind | rows | meaning for a host |
|---|---|---|
| defect, reproduced | 2 (`#version` in a ComposedShader), 4 (`GeoViewpoint` raises `EAbstractError`), 8 to 11 (stock glb writer), 19, 20 (PasGLTF) | a file can be valid and still fail here |
| missing feature | 1 (`GaussianSplats`), 3 and 15 (WebP), 5 (`GeoElevationGrid`, `GeoLOD`), 13 (Text arrives as untextured quads) | route around it, or say the host cannot judge it |
| contract difference | 6 (camera and clear colour defaults), 12 (`ElevationGrid` without `height`), 16 (single `groundColor`), 18 (light attenuation) | differs from X_ITE; neither shown wrong |
| harness or method | 7 (`--anti-alias` no-op under Xvfb), 14 (a url in x3d.demo), 17 (a still render needs the update step) | not a Castle finding |

Burn-down: 12 of 20 have a workaround in our tooling (rows 3, 4, 6, 8, 9, 10, 11, 13, 15, 17, 19, 20); 8 do not (1, 2, 5, 7, 12, 14, 16, 18). The adapter that would close row 18 was proposed and **not built**. No row has been reported to the Castle project (the README says so); rows 12, 16 and 18 are not claims of Castle bugs while the spec text is unquoted.

Row 2 matters most for the thesis. This scene is valid X3D 4.0, carries a shader the host cannot compile, and the validator says nothing (drill D-CAS-6):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<X3D profile="Immersive" version="4.0">
  <head><component name="Shaders" level="1"/></head>
  <Scene>
    <Shape>
      <Appearance>
        <ComposedShader language="GLSL">
          <ShaderPart type="VERTEX">#version 300 es
in vec3 position;
void main() { gl_Position = vec4(position, 1.0); }</ShaderPart>
          <ShaderPart type="FRAGMENT">#version 300 es
precision mediump float;
out vec4 c;
void main() { c = vec4(1.0, 0.5, 0.0, 1.0); }</ShaderPart>
        </ComposedShader>
      </Appearance>
      <Box/>
    </Shape>
  </Scene>
</X3D>
```

Castle inserts feature `#define` lines at the start of the user's source, above the `#version` line, and the GLSL compiler rejects the program; the shape draws with the fallback shader (row 2, reproduced there on a 12-line scene and an unmodified x3d.demo scene; I did not run Castle). Rows 19 and 20 are still present at master `48ce617`: `CastlePasGLTF.pas:5589` writes `fWrapT` under `'wrapS'`, and `GetEmpty` omits `baseColorFactor` **[C]**.

## 11. The critic's verdict, and what it forbids

The field-guide process had skeptics check 279 claims; about half needed a fix (counts in N-CAS-28, carried **[S]**). A critic then opened the source for the eight most suspicious statements. Where a lens chapter and the errata disagree, the errata win. Sentences, with the evidence for each status:

| sentence | status | why |
|---|---|---|
| "Castle leads the X3D space" | **forbidden** | n = 1 native X3D engine examined; X_ITE, the only X3D comparator run, was ahead on 7 of 11 core scenes [C] and carries 11 of 11 of Castle's parse-only groups at the name rung [C] |
| "Castle has the broadest node coverage" | **forbidden** | 11 groups parse-only; LOD returns child 0 in the node walk [C] |
| "Castle is the conformance reference" | **forbidden** | tolerant loader, no event-timing test and a commented-out round-trip test [C]; no validator in the tree and CI jobs run with `--no-window-create` [L] |
| "Castle is behind on fidelity" | **forbidden as worded** | write "differs from the reference by +0.069 FLIP on core 11, cause traced to attenuation handling" |
| "Castle follows X_ITE" or the reverse | **forbidden** | influence untested; write "agree". Castle's source uses "follow" in three behaviour or naming decisions and one pointer (`x3dloadinternalply.pas:896`, `castleuriutils.pas:1235-1236`, `castleviewport_autonavigation.inc:285-290`) [C] |
| "glTF is Castle's native format" | **forbidden** | every format compiles to X3D; the world format is JSON; say "glTF is the best-travelled importer" [L] |
| "no peer exists" | **forbidden** | FreeWRL, Xj3D, X3DOM, InstantReality, Octaga, Cobweb were never opened |
| "the deepest X3D-as-substrate design in the one codebase we read, with unusually honest seam documentation; not benchmarked against other X3D engines" | **allowed** | the critic's sentence; the honesty ("for now", the inert-unit header) is also a map of what is missing |
| "a fast, scriptable second reader of X3D, drivable headless" | **allowed** | 0.5 s a frame on llvmpipe, carried **[L]** |

What would change the verdict, written before the data: a three-state node matrix over X3D 4.1 for Castle and X_ITE read from source (section 4 is its first, weakest column); two or more peer engines run on the same TimeSensor and ROUTE fixtures; a quoted X3D 4.0 clause for physical-light attenuation; adoption and cadence data (none collected; one maintainer holds about 97% of file headers, **[L]** from a grep). Until then "leads" has n = 1.

## 12. What to copy from Castle, and what to distrust

| # | rule | kind | grade | evidence |
|---|---|---|---|---|
| 1 | Key a host registry by MIME; refuse duplicates and empty fields; record what each host can decode | copy | [C] | `RegisterModelFormat` raises on all three (`x3dload.pas:813-840`) |
| 2 | Judge a load by warnings plus a shape census against the declared count | copy | [C] | a classic read error stops the file after one warning (`x3dnodes_encoding_classic.inc:569-573`) |
| 3 | Keep a three-state support table per host and list nodes used by state in every receipt | copy | [C] | only the 11-group unit marks inertness; section 4 |
| 4 | Export from the evaluated shape tree, not by walking nodes | copy | [C] | stock: 24 of 70 invalid, 0 of 43 lit scenes keep lights; shape tree: 0 invalid, 41 of 43 |
| 5 | Put the invalidation or support class in the node table and generate from it; fail on a missing class | copy | [L] | 43 change classes counted here; the default class dominates, so require an explicit one |
| 6 | Turn warnings into data (`OnWarning` listeners) and fail selected tests on a warning | copy | [L] | `castle-render` stores `Category: Message` lines |
| 7 | State what is unfinished where it is unfinished | copy | [C] | `castleinternalnodesunsupported.pas:16-25`; a TODO-heavy file is also a gap map, so count them |
| 8 | Pin the engine by hash, not URL, and run a smoke test in CI | copy | [C] | `docker/Dockerfile:25-28`, two green CI runs |
| 9 | Do not take the engine's docs as ground truth | distrust | [L] | status table lists 8 of the 11 parse-only groups; plug appendix stale (field-guide map) |
| 10 | Do not use its node table as a validator | distrust | [L] | hand-pasted, ranges are free text, 410 headers include abstract and non-X3D types |
| 11 | Do not copy tolerant loading as the default of a grammar check | distrust | [L] | out-of-range input is repaired with a warning, so a witness sees the repaired value |
| 12 | Do not read a Castle brightness number without its light contract | distrust | [C] | one PhysicalMaterial draws differently from `.x3d` and `.glb`; section 6 |
| 13 | Do not treat a Castle-only node or field as portable | distrust | [L] | `Skin`, `Effect`, `ScreenEffect`, `keyValueQuaternions`, `interpolation=STEP` |
| 14 | Do not treat the stock glTF writer as an exporter | distrust | [C] | gap rows 8 to 11, 19, 20; section 8 |
| 15 | Do not rely on the deprecated `MainScene` path surviving 7.0 final | distrust | [S] | our harness needs it for Viewpoint, Background, Fog; keep a canary scene |
| 16 | Do not reuse its text, generated files, shaders or test data before a licence check | distrust | [S] | core LGPL 2 or later with a static-linking exception, examples BSD-3, editor GPL, per-directory data licences; the node-DSL tool's licence was read two ways, so read `COPYING.md` first |

## 13. Re-run kit

Scripts behind the "run 2026-11-14" claims; they read and never write. `xite_names.py` also does the Castle-only count (D-CAS-1) when its second argument is omitted.

```python
# xite_names.py  usage: python3 xite_names.py castle-engine/src/scene/x3d [node_modules/x_ite/dist]
import re, glob, sys
cdir = sys.argv[1]; xdir = sys.argv[2] if len(sys.argv) > 2 else None
u = open(cdir + '/castleinternalnodesunsupported.pas').read()
files = [f for f in dict.fromkeys(re.findall(r'\{\$I ((?:auto_generated_node_helpers/)?x3dnodes_\w+\.inc)\}',
         u.split('\nimplementation')[1])) if 'enums' not in f]
xite = set()
if xdir:
    for f in [xdir + '/x_ite.js'] + glob.glob(xdir + '/assets/components/*Component.js'):
        for m in re.finditer(r'getStaticProperties \("(\w+)", "(\w+)", (\d+)', open(f).read()):
            if not m.group(1).startswith('X3D'): xite.add(m.group(1))
tot = hit = 0
for f in files:
    m = re.search(r'RegisterNodeClasses\(\[(.*?)\]\)', open(cdir + '/' + f).read(), re.S)
    ns = [re.sub(r'^T|Node$', '', x.strip()) for x in m.group(1).split(',') if x.strip()]
    h = [n for n in ns if n in xite]; tot += len(ns); hit += len(h)
    print(f.split('/')[-1], len(ns), len(h), sorted(set(ns) - xite) if xdir else '')
print(len(files), 'groups,', tot, 'registrations,', hit, 'names present in X_ITE', len(xite) or '(not asked)')
```

```python
# formats.py  usage: python3 formats.py castle-engine/src
import re, glob, sys
rows = []
for p in glob.glob(sys.argv[1] + '/**/*.pas', recursive=True):
    if p.endswith('x3dload.pas'): continue          # its only block is a doc-comment example
    s = open(p, errors='ignore').read()
    for m in re.finditer(r'ModelFormat := TModelFormat\.Create;(.*?)RegisterModelFormat\(ModelFormat\)', s, re.S):
        rows.append((p.split('/')[-1], re.search(r'^\s*ModelFormat\.OnSave\s*:=', m.group(1), re.M) is not None))
print(len(rows), 'registrations;', sum(r[1] for r in rows), 'with OnSave')
```

```python
# core11.py  usage: python3 core11.py x3d.castle/results/quality/public/results.json
import json, sys, statistics as st
d = json.load(open(sys.argv[1]))['scenes']
excl = {'annotation-standard', 'nurbs-weights', 'quaternion-xyzw', 'p2-point-classic'}
core = [s for s in d if s not in excl]
F = lambda s, l: d[s]['legs'][l]['vs_ref']['flip_mean']
for l in ['xite', 'babylon_addon', 'babylon_castle', 'castle_native', 'castle_all']:
    print(l, round(st.mean(F(s, l) for s in d), 4), round(st.mean(F(s, l) for s in core), 4))
print('castle_native beats xite on', sum(F(s, 'castle_native') < F(s, 'xite') for s in core), 'of', len(core))
```

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/castle-engine/castle-engine.git
git -C castle-engine sparse-checkout set src/scene tests/code     # master moves; this chapter read 48ce617
npm i x_ite@16.7.1 gltf-validator@2.0.0-dev.3.10
```

## Heuristics

| ID | Rule (imperative, at most 30 words) | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-CAS-1 | Judge a Castle load by its warnings and a shape census against the declared count; never by "it loaded" or an exit code. | C | classic reader warns once and skips the rest of the file | `castle-engine@48ce617:x3dnodes_encoding_classic.inc:569-573` |
| H-CAS-2 | Quote node coverage by rung and definition (registered, parse-only, name present in a peer, behaves); never a bare "98 of 328". | C | 99 registrations, 98 concrete, five denominators in circulation | `castle-engine@48ce617`; `x_ite@16.7.1` dist |
| H-CAS-3 | Treat name presence in a peer as the weakest rung; do not turn 97 of 99 into "X_ITE implements them". | C | the scan reads class names, not behaviour | `x_ite@16.7.1` dist |
| H-CAS-4 | Name the light contract (X3D attenuation, glTF loader `0 0 1`, Castle components) in every Castle brightness number. | C | the glTF loader writes `(0,0,1)`; X3D files get no adjustment | `castle-engine@48ce617:x3dloadinternalgltf.pas:751` |
| H-CAS-5 | Write "differs from the reference by F, cause traced to X", not "behind"; the reference is a reading of the file, not truth. | C | add-on drops NurbsCurve, flattens Background, applies 1/d^2 | `x3d.castle@d70e00c:results/quality/public/results.json` |
| H-CAS-6 | Set `ProcessEvents` explicitly in a harness and record it; a still render never runs a ROUTE by default. | C | `default false` | `castle-engine@48ce617:castlescenecore.pas:2337` |
| H-CAS-7 | Do not rely on frame 0 of a TimeSensor at exactly `startTime`; step past the origin or build the fixture. | S | code read gives no event on that tick; not run | `castle-engine@48ce617:x3dnodes_standard_time.inc:333-337,768-785` |
| H-CAS-8 | Take LOD from the shape tree for anything that must match a viewer; the node walk always returns child 0. | C | `DirectEnumerateActive` | `castle-engine@48ce617:x3dnodes_standard_navigation.inc:607-616` |
| H-CAS-9 | Export from the shape tree; gate every exporter change on the validator, a census and the rig, per flag combination. | C | 70 of 70 clean, also with flags on | `Khronos glTF-Validator 2.0.0-dev.3.10` |
| H-CAS-10 | Report a rig median with its range or drop it; four runs of one 21-scene set gave 0.58, 0.88, 1.05 and 3.40. | C | receipts re-read | `x3d.castle@d70e00c:results/phase3/` |
| H-CAS-11 | Do not rank legs by FLIP where the reference omits content; FLIP rewards the shared omission. | C | `quaternion-xyzw`: near-empty 0.1548 beats the correct 0.1962 | `x3d.castle@d70e00c:docs/quality-leg.md` |
| H-CAS-12 | Validate shaders against the host, not only the XSD: a valid ComposedShader with `#version` can fail on Castle. | L | validator clean on the snippet; Castle failure from the gap list, not run | `x3d_mcp fork b4efcd3`; `docs/castle-gaps.md` row 2 |
| H-CAS-13 | Write "agree" for measured agreement of two engines; never "follows" without a dated source. | C | influence direction untested | `castle-engine@48ce617`; critic's errata |
| H-CAS-14 | Pin an engine by archive hash and count a green CI smoke test as the proof of reproducibility, not a README sentence. | C | README says not built; two CI runs succeeded | `gh run view`; `docker/Dockerfile` |
| H-CAS-15 | Re-derive a carried count and say how it was counted; "21 and 7" are registrations, not working conversions. | C | round-trip test commented out | `tests/code/testcases/testx3dnodes.pas:392-393` |

## Drills

### D-CAS-1 Count the parse-only nodes and name the denominator
- **Level:** L2
- **Task:** Sparse-check out `castle-engine` and run `xite_names.py` with one argument. Report groups, registrations, and the abstract class.
- **Verify:** `python3 xite_names.py castle-engine/src/scene/x3d`
- **Answer:** 11 groups, 99 registrations (Geospatial 11, DIS 6, Layering 3, Layout 5, RigidBodyPhysics 14, Picking 5, Followers 10, ParticleSystems 10, TextureProjector 3, SoundX3D4 19, VolumeRendering 13); `AbstractTextureProjector` is abstract, so 98 concrete.
- **Checked:** 2026-11-14 `castle-engine@48ce617`, Python 3.13.18

### D-CAS-2 Count loaders and savers without trusting a number
- **Level:** L2
- **Task:** Run `formats.py`; name the 7 savers; say why "7 savers" is not "7 working exporters", citing one test line.
- **Verify:** `python3 formats.py castle-engine/src`
- **Answer:** 21 registrations, 7 with `OnSave`: X3D XML, X3D classic, VRML (writes classic), glb, gltf, STL, IFC. The whole-file X3D write-read test has both calls commented out (`testx3dnodes.pas:392-393`); the glb writer failed 24 of 70 scenes.
- **Checked:** 2026-11-14 `castle-engine@48ce617`, Python 3.13.18

### D-CAS-3 Re-derive the headline FLIP and what it hides
- **Level:** L2
- **Task:** Run `core11.py`. Report the core-11 means for X_ITE and Castle native, the scenes Castle wins, and the share of the all-15 Castle-minus-X_ITE FLIP gap carried by `materials-world` plus `lights-after`.
- **Verify:** `python3 core11.py x3d.castle/results/quality/public/results.json`; share = sum of those two scenes' (castle_native minus xite) `vs_ref.flip_mean` over the sum for all 15.
- **Answer:** X_ITE 0.0457, Castle native 0.1149, Castle wins 4 of 11, share 0.770. Add that the reference is Cycles on the add-on's reading of the file.
- **Checked:** 2026-11-14 `x3d.castle@d70e00c` receipt, Python 3.13.18

### D-CAS-4 Validate two exporter glbs
- **Level:** L2
- **Task:** `npm i gltf-validator@2.0.0-dev.3.10`, run `tools/gltf_validate.mjs` on `results/exporter-70/sample-glb/*.glb`; report counts and generator.
- **Verify:** `node gltf_validate.mjs out.json sample-glb/*.glb`
- **Answer:** both `E=0 W=0 I=0`, generator "x3d-castle-convert (Castle Game Engine shape-tree exporter)", 38,588 and 24,292 bytes. Structure only, not looks.
- **Checked:** 2026-11-14 `Khronos glTF-Validator 2.0.0-dev.3.10`, Node 22.23.4

### D-CAS-5 Break the spot-cone rule
- **Level:** L3
- **Task:** In the `lights-before` sample glb (a directional and a point light) add a third light of type `spot` with `innerConeAngle 0.9`, `outerConeAngle 0.5` to `KHR_lights_punctual`, rewrite the JSON chunk (pad to 4 bytes), validate; then find the exporter line that prevents it and say what X3D allows that glTF does not.
- **Verify:** the validator run; `grep -n "innerConeAngle" castle-convert/x3dcastleexport.pas`
- **Answer:** `E=1 W=0 I=1`, `KHR_LIGHTS_PUNCTUAL_LIGHT_SPOT_ANGLES @ /extensions/KHR_lights_punctual/lights/2/spot/outerConeAngle`. The exporter writes the inner angle just inside the cone (`x3dcastleexport.pas:1896-1903`); X3D lets `beamWidth` reach `cutOffAngle` ("no falloff inside the cone"), glTF does not.
- **Checked:** 2026-11-14 `Khronos glTF-Validator 2.0.0-dev.3.10`, Python 3.13.18

### D-CAS-6 A valid scene the validator cannot warn about
- **Level:** L3
- **Task:** Save the section 10 document as `shader.x3d`, run the fork's `validate_xml` and `semantic_diagnostics` on it, then specify the one-rule checker that catches it for a Castle target.
- **Verify:** in an `x3d_mcp` checkout: `PYTHONPATH=src python3 -c "from validation.validate import validate_xml; from validation import semantic; x=open('shader.x3d').read(); print(validate_xml(x)['valid']); print(semantic.semantic_diagnostics(x))"`
- **Answer:** `True`, schema 4.0, no errors; one INFO (`no-viewpoint`) and nothing on `#version`. The checker: any `ShaderPart` text starting with `#version` is a Castle trap (gap row 2). Castle's failure was read from the gap list, not run.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3` (validator half only)

### D-CAS-7 Design the TimeSensor origin fixture
- **Level:** L3
- **Task:** Write a scene with a `TimeSensor` (`startTime 0`, `cycleInterval 4`, `loop TRUE`) routed through a `PositionInterpolator` to a `Transform`. Predict the translation at the first frame for Castle (from `x3dnodes_standard_time.inc`) and for the spec; name the settings that decide it.
- **Verify:** run it in `castle-render` at `--time 0` and `0.001`, and in X_ITE; compare.
- **Answer:** from the code read, no `elapsedTime` or `fraction_changed` is sent on a first tick at exactly `startTime`, so the Transform keeps its authored translation; one frame later a `Fraction` of 0 is corrected to 1. Settings: `ProcessEvents`, the time of the first `SetTime`, and `0` against `0.001`. The spec's initial-time rule must be quoted before calling it a Castle quirk.
- **Checked:** not run

### D-CAS-8 Attenuation at 3 m and at 0.5 m
- **Level:** L1
- **Task:** From `add_light.glsl` (physical, lines 123-128) compute the factor for attenuation `1 0 0` and `0 0 1` at 0.5, 1, 3 and 10; say where the "attenuation 0 0 1" adapter fails to give inverse square.
- **Verify:** `python3 -c "print([(d, 1/max(1,d*d)) for d in (0.5,1,3,10)])"`
- **Answer:** `1 0 0` gives 1 everywhere; `0 0 1` gives 1, 1, 0.111, 0.01. At 3 m the first is 9 times brighter. At 0.5 m and 1 m they agree because of the `max(1, ...)` floor.
- **Checked:** 2026-11-14 Python 3.13.18 (arithmetic on the formula read at `castle-engine@48ce617`)

## Honest limits

* **I did not run Castle.** Every render number is carried from `x3d.castle@d70e00c:results/` and re-derived from its JSON where the text says so; the event traps and the `#version` failure are code reads or carried results **[C] for the read, [S] for the behaviour**.
* **Source and snapshot may differ.** I read public master `castle-engine@48ce617`; renders ran on a 7.0-alpha.3 snapshot bundle with no `.git`. Same tree by timing only **[L]**.
* **Name presence is not support.** 97 of 99 is a string-registration count in the `x_ite@16.7.1` npm dist; X_ITE was not run on those nodes **[S]** for behaviour. The 292 and chapter 06's 294 use different definitions and were not reconciled.
* **Spec text unquoted.** Whether X3D 4.0 clauses 17.2.2.3 and 17.2.2.6 require inverse-square falloff for a PhysicalMaterial is not settled; "bug" is unsupported, "differs" is supported **[S]**.
* **One reference, 15 scenes, no GPU.** All FLIP and pixel numbers come from software GL (llvmpipe, SwiftShader); a GPU could change timings and MSAA, not a light model **[L]**.
* **Stale numbers in the repository**, recorded and not edited: "about 1,700" and "about 2,500" lines against 2,412; "17 fixtures" against 18; "not yet built" against two green CI runs; published medians 3.5 and 17.1 against 0.88 and 14.09 in the same receipt **[C]**.
* **Conflict: tool version.** `docs/reproduce.md` lists 5.3.0 for viewer and converter; the binaries carry a 7.0-alpha.3 banner; unresolved without running them **[L]**.
* **Not covered:** peer engines, texturing, Text, HAnim and Sound semantics, the Script node, load time and memory, adoption and cadence, whole-file round trips, licence granularity.
* **The field-guide process corrected about half of its own claims.** I preferred its errata and re-derived what I could; its counts (279 checked, 127 confirmed, 133 corrected, 13 refuted, 6 unverifiable) are carried from a private note **[S]**.
* **The refutation test of section 4 reads one definition of "implements".** A behaviour-fixture definition could move the result either way.

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-CAS-1 | registered model formats; of them with `OnSave` | 21; 7 | C | `formats.py`, 2026-11-14 | `castle-engine@48ce617:src/` |
| N-CAS-2 | parse-only groups; registrations in them (one abstract) | 11; 99 | C | `xite_names.py` | `castle-engine@48ce617:src/scene/x3d/castleinternalnodesunsupported.pas` |
| N-CAS-3 | parse-only names with a same-named non-abstract class in X_ITE | 97 of 99 | C | `xite_names.py`, `x_ite@16.7.1` npm dist | `x_ite@16.7.1:dist/x_ite.js`, `dist/assets/components/` |
| N-CAS-4 | non-abstract classes found in X_ITE by `getStaticProperties` | 292 | C | `xite_names.py` | `x_ite@16.7.1:dist/` |
| N-CAS-5 | names and `RegisterNodeClasses` calls in the whole tree | 333; 43 | C | inline Python | `castle-engine@48ce617:src/` |
| N-CAS-6 | change classes in `TX3DChange`; spec files; generated helper files | 43; 42; 409 | C | inline Python, `ls` | `castle-engine@48ce617:src/scene/x3d/castlefields_misctypes.inc`, `tools/internal/x3d-nodes-to-pascal/` |
| N-CAS-7 | mean FLIP, core 11: X_ITE, Babylon add-on glb, Babylon Castle glb, Castle native, Castle all | 0.0457, 0.0485, 0.0491, 0.1149, 0.1146 | C | `core11.py`; FLIP 1.7, Cycles 256 spp, 512 px | `x3d.castle@d70e00c:results/quality/public/results.json` |
| N-CAS-8 | mean FLIP, all 15, same five legs | 0.0748, 0.0516, 0.0658, 0.1321, 0.1289 | C | `core11.py` | same |
| N-CAS-9 | core scenes where Castle native beats X_ITE; means on the other 7 core scenes | 4 of 11; 0.0406 against 0.0386 | C | `core11.py`, inline Python | same |
| N-CAS-10 | share of the all-15 Castle-minus-X_ITE gap in `materials-world` plus `lights-after` | 0.770 | C | inline Python | same |
| N-CAS-11 | `p1` Castle FLIP before and after attenuation `0 0 1`; X_ITE | 0.0546, 0.0059; 0.0053 | C | receipt read | `docs/quality-leg.md` section 3 |
| N-CAS-12 | `p4` Castle FLIP before and after; X_ITE; share of the gap closed | 0.0446, 0.0237; 0.0085; 58% | C | receipt read, arithmetic | same |
| N-CAS-13 | mean FLIP change of the best single Castle switch (SSAA 4x) | -0.0027 | C | inline Python, 15 scenes | `results.json` |
| N-CAS-14 | stock writer glbs failing the validator; errors | 24 of 70; 14,379 | C | `Khronos glTF-Validator 2.0.0-dev.3.10`, receipt | `results/scout-70/stock-writer-gltf-validate.json` |
| N-CAS-15 | exporter glbs with 0 errors and 0 warnings; INFO notes | 70 of 70; 77 | C | same validator, receipt | `results/phase3/gate70-default/gltf-validate.json` |
| N-CAS-16 | exporter census: lights, cameras, textures, vertex colours, lines, points, animation | 41/43, 55/55, 11/17, 26/27, 14/17, 10/11, 0/21 | C | `census_compare.py` receipt | `results/phase3/gate70-default/census.json` |
| N-CAS-17 | rig, 21 scenes, phase 3 `self`: mean; median | 7.80; 3.40 | C | X_ITE 16.7.1 vs Babylon 9.32.0, Chromium 153.0.8010.12, SwiftShader, 512 px | `results/phase3/rig-gate-summary.json` |
| N-CAS-18 | same rig, phase 2 binary `self`: mean; median | 7.53; 1.05 | C | same | same |
| N-CAS-19 | phase 2 receipt means: exporter `rigcam`, add-on glb, stock glb | 7.80, 9.22, 17.62 | C | same rig | `results/rig-exporter/results.json` |
| N-CAS-20 | share of the 21-scene sum carried by the four largest scenes | 71% | C | inline Python | `rig-gate-summary.json` |
| N-CAS-21 | fixtures passing: phase 3 binary; phase 2 binary | 18 of 18; 4 of 18 | C | `phase3_check.py` receipts | `results/phase3/fixtures.json`, `fixtures-baseline.json` |
| N-CAS-22 | gap rows: total; Confirmed; Likely | 20; 19; 1 | C | row count | `docs/castle-gaps.md` |
| N-CAS-23 | docker workflow runs, both success | 2 (8 min 32 s; 2 min 50 s) | C | `gh run view`, 2026-11-14 | `hagopjay/x3d.castle` Actions |
| N-CAS-24 | `#version` ComposedShader snippet through the validator | valid, 0 errors, 1 INFO | C | `x3d_mcp fork b4efcd3` | drill D-CAS-6 |
| N-CAS-25 | mutated glb, inner cone above outer | E=1 W=0 I=1 | C | `Khronos glTF-Validator 2.0.0-dev.3.10` | drill D-CAS-5 |
| N-CAS-26 | physical light factor at 3 m, attenuation `1 0 0` against `0 0 1` | 1 against 0.111 (9x) | C | arithmetic on `add_light.glsl` | `castle-engine@48ce617:src/scene/glsl/source/lighting_model_physical/add_light.glsl:123-128` |
| N-CAS-27 | specular cap 0.25 against 0.5, rig mean; median | 7.45 against 7.80; 0.58 against 3.40 | C | rig, 3 repeats, Babylon 9.32 only; receipt re-read | `results/phase3/rig-specular-cap025-summary.json` |
| N-CAS-28 | field-guide claims checked; split | 279 = 127 + 133 + 13 + 6 | S | carried from a private note | not linkable |

## Sources and provenance

* `x3d.castle@d70e00c` (public): `README.md`, `docs/*.md`, `docker/`, `castle-convert/`, `castle-render/castle_render.dpr`, `tools/`, `tests/phase3_check.py`, receipts under `results/`. Read 2026-11-14.
* `castle-engine@48ce617` (public master, 2026-11-10; sparse checkout of `src/scene`, `src/files`, `tests/code`, `tools/internal/x3d-nodes-to-pascal`): the files in the meta table. Read, not built.
* `x_ite@16.7.1` npm `dist/` (class registrations only, not run); `x3d_mcp@b4efcd3` (drill D-CAS-6); Khronos glTF-Validator 2.0.0-dev.3.10 from npm.
* A private field-guide process (mapper, skeptic, lens and critic passes over Castle 7.0-alpha.3) and the phase 3 hand-off notes were read as leads; their figures are [L] or [S] unless re-derived above, and the verdict wording of section 11 is the critic's, tightened to what the re-derivations support. They are not linked here.
* Gaps: no Castle binary was run; the bundle has no `.git`; nothing has been sent to the Castle project; no pass quoted the X3D 4.0 attenuation text.
* Siblings: [01 The tether](01-the-tether.md), [02 The Loom laws](02-loom-laws.md), [03 The validator and the gates](03-validator-and-gates.md), [04 MCP for agents](04-mcp-for-agents.md), [06 X_ITE](06-xite-the-oracle.md), [07 x3d.xray](07-xray.md), [08 The Babylon bridge](08-babylon-bridge.md), [10 The Blender pipeline](10-blender-pipeline.md), [11 glTF, USD, Khronos](11-gltf-usd-khronos.md).
