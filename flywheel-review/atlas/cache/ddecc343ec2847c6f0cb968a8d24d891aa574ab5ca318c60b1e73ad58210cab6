# 12. Unreal as a tier-1 X3D framework

> **Say it:** Unreal is a plausible tier-1 endpoint for *rendering* an X3D scene through a glb, it cannot run X3D behaviour without a plugin that does not exist, and today every Unreal claim in this base is read, not run: no Unreal 5.8 install and no GPU run stand behind any of them. **[L]** for the architecture, **[S]** for every Unreal behaviour claim, **[C]** only for the conversions and arithmetic re-run on 2026-11-14.

| field | value |
|---|---|
| chapter code | `UNR` |
| prerequisites | [01 The tether](01-the-tether.md); [11 glTF, USD and Khronos](11-gltf-usd-khronos.md) for the carrier and the gate; [06 X_ITE, the oracle](06-xite-the-oracle.md) and [08 The Babylon bridge](08-babylon-bridge.md) for the two existing tier-1 renderers |
| after this you can | (1) say what "tier-1 X3D framework" means as a testable definition; (2) derive the Unreal-to-X3D axis, unit, rotation and winding conversion and check it with five lines of Python; (3) explain why instancing counts differ between a flat and an instanced export and what that does and does not prove; (4) separate what a fidelity metric measures from what it cannot; (5) run the test plan that would promote an Unreal claim to [C] |
| sources read | x3d-blender-io@ab99988:{release_notes.md, tools/fidelity_rig/README.md, tools/fidelity_rig/blender_leg.py}; two Unreal-project converter scripts and their outputs (not in a public repo; read and re-run, Section 8); Khronos extension registry (public, fetched 2026-11-14); a private digest of Unreal, web and quality-metric sources (lead only) |
| instruments used | `Khronos glTF-Validator 2.0.0-dev.3.10` (run 2026-11-14); Python 3 with numpy for the derivations (run 2026-11-14); `X_ITE 16.7.1` and `Babylon.js 9.32.0` on `Chromium 153, SwiftShader` (receipts carried from the repo README); `bpy 5.3.0` (receipts carried); **Unreal Engine 5.8: not installed, read, not run** |

**Read, not run.** The status of this chapter in one sentence: Unreal 5.8 is not installed here and no frame was rendered by it. Everything said about what Unreal does (importers, Lumen, Nanite, web targets, licence) comes from a private digest of Epic's documentation, written 2026-11-12, with the vendor pages partly blocked at the time. Those claims are [S] or at best [L], and none is used as a premise for a [C]. What is [C] below is only what this session computed: matrices, conversions, glb structure and validator output.

---

## 1. The map

```text
  X3D 4.0 source (validated)                       the same source feeds every tier-1 renderer
        |
        +--> X_ITE 16.7.1      interprets X3D live in the browser     (reference; behaviour runs)
        +--> Babylon.js        x3d.loom bridge interprets X3D nodes   (behaviour runs; see ch. 08)
        +--> Blender           translate once at import               (no behaviour)
        |        |
        |        +--> glb --[Khronos validator]--> Babylon.js / three.js / Castle / UNREAL?
        |
        +--> UNREAL 5.8        three candidate mechanisms:
                 A  glb or USD import (Interchange)   static scene, never run
                 B  custom importer plugin for X3D    to be built
                 C  engine-side ROUTE interpreter     to be built (Blueprint, C++, JS)
              browser: no Unreal target in 5.8; streamed video or third-party WebGPU port
```

| in scope | out of scope |
|---|---|
| what tier 1 would mean; mechanisms; the coordinate maths; instancing; looks; the measurement plan | a claim that Unreal renders any X3D scene correctly (nothing here shows it); Unreal licence advice; web-streaming product comparison beyond one table |

Read next: deeper, [11 glTF, USD and Khronos](11-gltf-usd-khronos.md) (the file that would be imported); wider, [09 Castle Game Engine](09-castle-engine.md) (the other engine whose model is X3D itself).

---

## 2. The question and a definition that can fail

**Question.** Can Unreal be a first-class X3D renderer, in the way X_ITE and Babylon.js are?

"First-class" is a word until it is a test. This base defines **tier 1** as an engine for which all of the following hold at once, each with a named instrument. An engine that fails one row is not "worse"; it is graded at the highest tier whose rows it passes.

| tier | requirement | evidence needed | X_ITE | Babylon.js (bridge) | Blender | Castle | Unreal 5.8 |
|---|---|---|---|---|---|---|---|
| T0 | a file reaches the engine | a load log and a screenshot | yes | yes | yes | yes | not run |
| T1 | geometry and materials arrive | a mean abs delta against X_ITE on named scenes | reference | measured (README) | measured (README) | partly (colour probes) | not run |
| T2 | lights, cameras and fixed animation arrive | per-feature checks | reference | measured | measured | partly | not run |
| T3 | the pipeline targets it **every run**, with an automated gate and a receipt | a CI job and a manifest | yes | yes | yes | no | no |
| T4 | behaviour runs (ROUTEs, sensors, Script) | event fixtures that pass | yes | yes (bridge) | no | yes (own model) | no, plugin to build |
| T5 | a public web reach | a browser URL | yes | yes | no | in development | no (5.8) |

Reading the columns: the cells for X_ITE, Babylon.js, Blender and Castle come from the other chapters and the repo receipts and are [L]. The Unreal column is [S] throughout, because T0 itself has not happened.

Verdict, graded [L] on reasoning and [S] on every Unreal behaviour: Unreal is a reasonable endpoint for **T0 to T2 and for offline images and video** (a quality ceiling, not a correctness reference). It is not a web runtime in 5.8. And **T4 needs new software**: no importer of X3D or VRML for Unreal was found in the sources read (a private digest reports none on Fab, in Datasmith or on GitHub; a search the reader can repeat).

---

## 3. Candidate mechanisms

| mechanism | what it gives | what it loses | cost | status | grade |
|---|---|---|---|---|---|
| A. glb through Interchange | static mesh actors, materials, lights, cameras, fixed clips | all behaviour; X3D lights need a unit calibration; DEF names unless extras are read | free tools; one commandlet | **never run here**; a private digest reports a bug with async glb import in a shipping 5.7.4 build, a single report, version not ours | [S] |
| A'. USD through Interchange | composed assets | same as A, plus USD-only loss of glTF materials unless mapped | free | Epic is reported to call asset import production-ready and level import experimental in 5.8; not tested | [S] |
| A''. Datasmith | CAD and DCC scenes | no X3D reader found | free | not tried | [S] |
| B. X3D importer plugin | the X3D scene graph in the editor, DEF names as actor labels, PROTOs expanded at import | behaviour unless C also exists | large (C++ module, Python commandlet possible) | does not exist | [S] |
| C. event runtime | ROUTEs, TimeSensor, interpolators, sensors as engine logic (Timeline, Event Dispatchers, Blueprint); Script via an embedded JS runtime (a maintained binding exists; version and licence not re-checked) | ECMAScript fidelity | very large; the hardest row in the node table | does not exist | [S] |
| D. glb plus `KHR_interactivity` | the same ROUTE graph as data in the glb, read by Babylon.js and, one day, by an Unreal plugin | tied to the extension's coverage | medium on the Babylon side | the registry lists `KHR_interactivity` as ratified (fetched 2026-11-14, sha256 prefix `32868b162d85`); nothing in the add-on writes it | [L] for the registry, [S] otherwise |
| E. browser reach | WebGPU or streamed video | a desktop Unreal in a tab | varies | see Section 7 | [S] |

The architectural rule the digest argues for, and which fits the tether: **compile once, interpret where it matters.** One validated X3D per scene is the truth; the add-on compiles its static content to glb for Babylon.js, Unreal and Blender; behaviour travels beside it as a sidecar (ROUTE graph, timers, interpolators) to each runtime able to read it. This is a design choice [S], not a measurement.

```text
  Two halves of "driving an engine from X3D"

        STATIC half                                   LIVE half
  X3D -> add-on -> glb -> engine                X3D -> interpreter in the engine
  (compile once; this repo does it)             (X_ITE, Castle, the Babylon bridge do it)
  shared by Blender, Babylon, Unreal            Unreal needs a NEW plugin to join this half
```

---

## 4. Coordinates and units: the matrix, derived and checked

Unreal is **left-handed, Z-up, centimetres**: X forward, Y right, Z up. X3D is **right-handed, Y-up, metres**. glTF is right-handed, Y-up, metres. Going between a left-handed and a right-handed system means one mirror somewhere. There is no way to do it with a proper rotation; that is a statement about determinants, checked below.

### 4.1 Points

The conversion used by both Unreal-project converters (read, and re-run) swaps the Y and Z axes and divides by 100:

```text
  X3D = ( ue.x, ue.z, ue.y ) / 100          P = | 1 0 0 |      det P = -1   (a mirror)
                                                | 0 0 1 |      P is its own inverse (P P = I)
                                                | 0 1 0 |
```

The up axis lands on +Y as X3D wants; forward (X) stays X; the UE right axis (Y) becomes X3D's Z. Another choice, `(x, z, -y)`, has determinant +1: it is a rotation and would leave the handedness wrong. So the swap is not arbitrary, it is the simplest *mirror* that also fixes the up axis. [C] by the determinants (run 2026-11-14: det P = -1.0, det of `(x, z, -y)` = +1.0).

Worked point: UE location `(120, 340, 90)` cm becomes X3D `(1.2, 0.9, 3.4)` m. [C], by the converter's own formula `translation = (x/100, z/100, y/100)`.

### 4.2 Rotations: conjugation, not substitution

A linear map `q = R p` in UE coordinates becomes, in X3D coordinates `p' = P p`, `q' = P R P p'`. So the X3D rotation is the conjugate `R' = P R P`. The two converters build the Unreal rotation matrix from pitch, yaw, roll as FRotationMatrix axes (columns are the local axes in world), conjugate it, and read an axis-angle off the result.

| UE (pitch, yaw, roll) degrees | R (UE, rounded) | R' = P R P (X3D) | X3D `rotation` |
|---|---|---|---|
| (0, 90, 0) yaw | `[[0,-1,0],[1,0,0],[0,0,1]]` | `[[0,0,-1],[0,1,0],[1,0,0]]` | `0 -1 0 1.5708` |
| (0, 0, 90) roll | `[[1,0,0],[0,0,1],[0,-1,0]]` | `[[1,0,0],[0,0,-1],[0,1,0]]` | `1 0 0 1.5708` |
| (90, 0, 0) pitch | `[[0,0,-1],[0,1,0],[1,0,0]]` | `[[0,-1,0],[1,0,0],[0,0,1]]` | `0 0 1 1.5708` |

All values were computed with the converter's own `ue_rot`, `P`, `mm` and `axis_angle` functions, run 2026-11-14 [C]. Sanity check by hand for the first row: a UE yaw of +90 turns the forward axis X toward Y, so UE `(1,0,0)` goes to `(0,1,0)`; in X3D that vector is `(0,0,1)`. X3D rotation about `-Y` by 90 degrees sends `(1,0,0)` to `(0,0,1)`. They agree. The determinant of every conjugated matrix was checked as +1 for four random angle triples: conjugating by a mirror keeps a rotation a rotation [C].

Why the axis-angle has the opposite sign on the yaw: positive yaw in a left-handed Z-up frame appears as a *negative* rotation about the new up axis in a right-handed Y-up frame. The conversion has to carry that sign, and the derivation says where it comes from.

### 4.3 Winding and the `solid` trap

A mirror flips the sign of a cross product. Test (run 2026-11-14): the triangle `(0,0,0), (1,0,0), (0,1,0)` has `(b-a) x (c-a) = (0,0,1)` in UE coordinates. After the swap the same index order gives `(0,-1,0)`, while the mapped outward direction `P n` is `(0,1,0)`. A right-handed formula applied to the mirrored triangle disagrees in sign with the mapped normal [C].

Consequence: a converter must *decide* the winding by a numeric normal test against the engine's own front-face convention, never by assumption. Both converters write comments saying the index order is reversed; neither was checked against an Unreal render. A converter that writes `solid='false'` hides a wrong winding (both faces draw), so a wrong order passes every visual check except lighting and shadows. That is a [S] about the converters' output, and a [C] rule about what `solid='false'` hides (X3D `solid` governs back-face culling).

### 4.4 Field of view and cameras

X3D `Viewpoint.fieldOfView` is the **minimum** viewing angle, the one across the smaller image dimension. Unreal's default camera and the cine camera's focal length give a **horizontal** angle (the cine camera uses the sensor width). So a horizontal angle `h` on a screen of aspect `a` (width over height, greater than 1) becomes

```text
  fieldOfView = 2 * atan( tan(h/2) / a )     (vertical, because height is the smaller side)
```

| input | X3D fieldOfView | instrument |
|---|---|---|
| horizontal 58 degrees, 16:9 | 0.6045 rad = 34.63 degrees | Python, run 2026-11-14 [C] |
| 35 mm lens on a 23.76 mm wide sensor, horizontal | 37.50 degrees horizontal; 21.62 degrees vertical at 16:9 | Python, run 2026-11-14 [C] |

The sensor width 23.76 mm is the converters' assumption and is [S] (the script marks it "likely default, unverified"). The converters place the angle in `fieldOfView` unconverted, which is exact only for a square or portrait frame; whether that matters depends on how the comparison renderer treats it. That is a question for the measurement plan (gate G4), not a verdict.

### 4.5 Units and float range

Unreal works in centimetres, so a scene authored in metres arrives 100 times larger in numbers. At float32, the gap between adjacent values is 0.0078 at 100,000 cm and 0.0625 at 1,000,000 cm [C], so a scene 10 km across has about 6 cm of positional granularity far from the origin. Unreal's large-world coordinates use double precision in places; the claim is [S]. For X3D scenes with a GeoOrigin the same trap exists in Blender and was met there (gotcha 6 in [chapter 11](11-gltf-usd-khronos.md)).

---

## 5. Instancing: HISM, GPU instancing and the Thalassa and Prismatica counts

X3D reuse is DEF/USE: one geometry node defined once, referenced many times. A converter that emits one `Transform` per instance with a `USE` shape gets the same effect in X3D. Engines vary on what they do with it.

| representation | what repeats | engine target |
|---|---|---|
| X3D `DEF` shape plus many `Transform` with `USE` | geometry node | X_ITE and Castle share the node internally |
| glb, flat | a shared `mesh` index, one node per instance | any glTF viewer; node count equals instance count |
| glb with `EXT_mesh_gpu_instancing` | one node holding per-instance TRS accessors | Babylon.js draws it (receipt below); Unreal not tested |
| Unreal HISM or ISM | an instanced static mesh component | the mechanism Unreal would use; reached from glb only if the importer reads the extension (not tested) |

### 5.1 The counts, re-derived

Two Unreal-project scenes were converted to X3D by their converter scripts (static analysis, no Unreal). The outputs were counted on 2026-11-14:

| scene | `<Transform>` elements | of which `USE` shapes | `DEF` shapes | ROUTEs | instance count in the public release note |
|---|---|---|---|---|---|
| exhibition scene (THALASSA) | **1,719** | 1,711 | 18 | 0 | 1,718 instances + 1 lone mesh |
| aurora scene (PRISMATICA), static | 1,216 | 1,208 | 15 | 0 | 1,216 instances in 8 lists |
| aurora scene, animated | 1,216 | 1,208 | 17 | 2 | n/a |

The 1,719 in the exhibition output equals the release note's 1,718 instances plus its 1 lone mesh, so the two sources agree. The aurora converter was re-run on 2026-11-14 with its default arguments and produced a file byte-identical to the stored static output (`cmp` clean) [C]: the conversion is deterministic. The exhibition converter needs the project's own Python model and was not re-run, only its output counted.

Reading the numbers: the three counts are reported raw. `Transforms - DEF shapes` does not equal the `USE` count (1,719 - 18 = 1,701, against 1,711 counted), because some `DEF` names sit on groups and other nodes rather than on shapes; the difference was not decomposed.

### 5.2 What the glb does with them

Re-parsed and re-validated on 2026-11-14 (`Khronos glTF-Validator 2.0.0-dev.3.10`; details in [chapter 11 Section 5.4](11-gltf-usd-khronos.md)):

| scene | flat nodes / bytes | instanced nodes / bytes | node reduction | byte reduction | triangles |
|---|---|---|---|---|---|
| exhibition | 1,721 / 491,832 | 10 / 125,224 | 99.4 % | 74.5 % | 2,064 both |
| aurora static | 1,224 / 1,097,864 | 16 / 864,228 | 98.7 % | 21.3 % | 27,544 both |

The instanced files carry `EXT_mesh_gpu_instancing`, which the validator does not know: it passes them at INFO, content unchecked. Babylon.js 9.32.0 draws the instanced glb with 0 of 262,144 pixels different from the flat one (headless Chromium 153, SwiftShader, rig frame 512 x 512; carried from the repo's release notes). That is evidence that the *extension content is what it should be for Babylon*, not for Unreal.

What this does and does not show for Unreal:

| claim | grade | what would confirm it |
|---|---|---|
| the instanced glb is smaller and equivalent in Babylon.js | [L] (receipt carried) | re-run the rig |
| Unreal's importer reads `EXT_mesh_gpu_instancing` into an instanced mesh component | [S] | gate G2 below |
| Unreal draws 1,719 instances at lower cost than 1,719 separate actors | [S] | gate G6: GPU time on a named GPU |
| Nanite would take these meshes | [S] | the importer's Nanite option, gate G2 |

---

## 6. Looks: Lumen, Nanite, and X_ITE

The comparison is between rendering *models*, not between products. X_ITE 16.7.1 is a WebGL 2 forward renderer with PBR and image-based light; Unreal 5.8 has dynamic global illumination (Lumen), virtualised geometry (Nanite), virtual shadow maps and a path tracer. All Unreal rows below come from a private digest of Epic's documentation and are [S].

| aspect | X_ITE 16.7.1 | Unreal 5.8 (digest) | consequence for X3D scenes |
|---|---|---|---|
| tone mapping default | the 16.7.1 code sets `NONE` (its reference page says `KHR_PBR_NEUTRAL`; the code wins) [L, read in the digest, matches the rig] | Filmic or ACES by default | a fair comparison needs one tone curve in every engine, for example Khronos PBR Neutral, via a replacement tonemapper in Unreal |
| classic `Material` lighting | display-space shading, no 1/d² falloff | physically-based, linear | an X3D classic scene looks different by design; the add-on's light-units option fits glTF lights to X_ITE, not to Unreal |
| point-light falloff | classic: none within `radius`; `PhysicalMaterial`: 1/d² | inverse-square with attenuation radius | the same scene is brighter or dimmer; calibration constant K unknown |
| global illumination | none | Lumen | Unreal will be better lit than X3D asked for; log as intended difference, not a defect |
| geometry | triangles | triangles or Nanite clusters | no X3D effect except at very high counts |
| shadows | per-light maps | virtual shadow maps | different softness |
| X3D features with no Unreal analogue | n/a | ParticleSystem to Niagara, ComposedShader to custom HLSL materials | listed as expected loss in [chapter 11](11-gltf-usd-khronos.md) |
| headless on a CPU | measured on SwiftShader | reported to need a Shader Model 6 class GPU for Nanite and Lumen; no software Vulkan supported | every Unreal number needs a real GPU |

A frame where Unreal beats X_ITE on a quality metric is logged as an **intended difference**, not a regression. This is the sense in which X_ITE stops being the answer key for quality and stays the answer key for *correctness of translation*: the first axis tells you whether Unreal drew what the file says, the second whether it drew it well.

---

## 7. How fidelity is measured

### 7.1 The rig, as it exists

Everything measured so far is `tools/fidelity_rig` in `x3d-blender-io@ab99988` (read; its figures carried, not re-run): X_ITE 16.7.1 on the X3D against Babylon.js 9.32.0 on the glb, same headless Chromium 153 on SwiftShader, 512 x 512, from the first Viewpoint, reporting `mean_abs_delta` (whole frame, 0 to 255), `geometry_delta` (only where the glb draws geometry, from a magenta-and-green mask render) and 5 x 5 `patches` at listed pixels. Five light probes (a 0.8 grey under one light) pin the light model:

| probe | X_ITE | Babylon.js, light units BLENDER | Babylon.js, light units X_ITE |
|---|---|---|---|
| p1 PhysicalMaterial, PointLight 1 | 74 | 30 | 74 |
| p2 classic Material, PointLight 1 | 204 | 27 | 203 |
| p3 classic Material, DirectionalLight 1 | 204 | 120 | 203 |
| p4 PhysicalMaterial, PointLight 1, attenuation 1 0 0.2 | 57 | 30 | 56 |
| p5 PhysicalMaterial, DirectionalLight 0.3 | 78 | 78 | 78 |

The rig has **no Unreal leg**. The probes would be the first scenes to put into one, because the numbers are small and the light model is the thing Unreal most likely differs on.

### 7.2 The metrics, with what each can and cannot say

| metric | answers | cannot answer | tool (free) | state |
|---|---|---|---|---|
| mean abs delta | how far, on average, per channel | where; whether a human would see it | the rig's `compare.py` | measured for Babylon, none for Unreal |
| RMSE, PSNR | how much squared error | perceptual difference; PSNR rewards blur | numpy; PSNR = 10 log10(255² / MSE) | formula run 2026-11-14 |
| FLIP | where a human sees the difference between two rendered images; writes an error map | absolute correctness | NVIDIA `flip-evaluator`, BSD-3, per the digest [S]; pixels-per-degree must be fixed per receipt | not installed here |
| SSIM, LPIPS | structure and learned similarity | calibrated error; LPIPS needs a licence check | scikit-image, `lpips` per the digest [S] | not installed here |
| frame budget | does it run | looks | GPU timer queries on a named GPU | needs a real GPU |

PSNR numbers have no meaning without the image pair. A run on 2026-11-14 with random 8-bit images: an additive noise of standard deviation 5 gives MSE 24.11 and PSNR 34.31 dB; a constant offset of 3 gives 38.63 dB [C, numpy]. Two engines whose frames differ only by a global exposure offset score as well as two that differ in one corner by a larger amount. That is why the rig's whole-frame number and its geometry mask exist.

### 7.3 What a fair comparison has to hold constant

The Khronos render-fidelity site renders its scenarios in several renderers and compares each against a base golden, flagging results worse than a stated dB threshold, with Cycles goldens tone-curved after rendering (digest, [S]). The lesson transfers: **an engine comparison means nothing until the engines share a tone mapper, exposure, camera, resolution and environment light.** For Unreal that means a recorded tonemapper replacement and a recorded exposure compensation in the manifest; and a reference that is not the same importer path (Blender Cycles sees the scene through the very import the glb is made from, so an import bug would move the reference too). Unreal's own path tracer becomes a second reference once a GPU exists.

---

## 8. What the Unreal 5.8 projects looked like when read statically

Two projects, an exhibition-style scene and an aurora-style scene, were read through their engine-independent code and manifest, not opened in Unreal. What the reading produced is a *converter pair* that emits X3D plus proxy materials:

| item | what was read |
|---|---|
| exhibition converter | takes a scene manifest (declared in the project as `thalassa-scene/v1`, UE centimetres, left-handed Z-up) and writes X3D 4.0 in metres Y-up: instance transforms, five proxy PBR materials read off constants, cameras converted by the Section 4 maths |
| aurora converter | ports the project's C++ geometry maths (ribbons, faceted core, stage, columns, motes) to Python and writes X3D; the vertex displacement done by the material at run time is baked into the geometry at a chosen phase, or animated through a CoordinateInterpolator |
| materials | procedural, built from custom HLSL nodes. X3D cannot express them, so both converters write **proxies**: a PhysicalMaterial from constants, or an UnlitMaterial plus vertex colour for emissive HDR surfaces. Proxy grade [S] |
| lights | one directional plus four point-light proxies standing in for rect lights (X3D has no area light) |
| random scatter | one converter ports Unreal's random stream with a note that the port is unverified, so scatter positions are [S] |
| validation | the glbs produced from the outputs pass the Khronos validator with 0 errors and 0 warnings (Section 5.2, run 2026-11-14); nothing compared them with an Unreal render |

Therefore: what is established about these projects is that their *engine-independent maths* can be turned into X3D and a glb, and that the glb is structurally valid. What is not established is any statement about how they look in Unreal. A frame from Unreal would be the first evidence, and the conversions would then be a candidate oracle, not the other way round.

---

## 9. The test plan that would promote claims to [C]

Preconditions (none were met when this chapter was first written; all were met on 2026-11-14, see [section 10](#10-the-first-run-unreal-584-on-a-cloud-gpu-2026-11-14-to-15)): Unreal Engine 5.8 installed on a Linux or Windows machine with a Shader Model 6 class GPU (ray-tracing cores for the hardware paths); a named GPU and driver; the rig's scenes available.

| gate | what runs | pass criterion | promotes |
|---|---|---|---|
| G0 | `UnrealEditor -run=pythonscript` or the Interchange Python manager imports `p1-point-physical.glb` headless | process exit 0; a static mesh asset and a light actor exist in the content browser | "Unreal imports our glb" from [S] to [C] |
| G1 | import all 5 probes and the 9 demo scenes | no importer error log lines; actor count equals node count in the glb JSON (excluding instanced nodes) | importer coverage rows of Section 3 |
| G2 | import the instanced exhibition glb | an instanced mesh component with 1,718 instances (count from the glb accessor), or a recorded failure | the instancing rows of Section 5.2 |
| G3 | the coordinate test scene: a Box at X3D `(1, 2, 3)` with a yaw of 90 degrees about Y | actor location `(100, 300, 200)` cm and rotation yaw consistent with Section 4.2, within 1 cm and 0.1 degrees | the Section 4 conversion for the glb path |
| G4 | render the 5 probes with one fixed camera, tonemapper replaced by one agreed curve, exposure compensation recorded, Movie Render Queue to PNG and EXR | the centre-patch mean at X_ITE's value plus or minus 5 on 0 to 255 for p1 to p5, **or** a recorded calibration constant K that brings all five inside plus or minus 5 | light-unit rows; also decides the `fieldOfView` question in Section 4.4 |
| G5 | the same scenes in X_ITE 16.7.1 and Babylon.js 9.32.0 in the rig, and Cycles; compute mean abs delta, PSNR and FLIP between every pair | all pairs recorded; Unreal versus Cycles FLIP mean no greater than Babylon.js versus Cycles on the same scene, else logged as a difference | the quality axis |
| G6 | frame time with GPU timer queries over 600 frames after warm-up on the exhibition scene, flat versus instanced | median and 95th percentile recorded with the GPU name; no pass threshold, a measurement | the frame-budget row |
| G7 | event fixtures (TimeSensor to interpolator to Transform) run in Unreal through whichever event mechanism exists | the Transform's position at t = 0.5 matches the X_ITE 16.7.1 position to 1e-3 | T4; this gate cannot be passed before mechanism B or C exists |
| G8 | repeat G0 to G5 on a second machine | the same pass or fail on every gate | determinism of the receipts |

A gate that fails is a result, recorded as a dated row; the earlier statement is demoted, not edited away (the base's augmentation loop, `AUTHORING.md` section 6). Promotion rule: a claim moves from [S] to [L] when a gate passes once on one machine, to [C] when G8 holds.

---

## 10. The first run: Unreal 5.8.4 on a cloud GPU (2026-11-14 to 15)

This section is dated and supersedes nothing above it: Sections 3 to 9 stay as written, and the rows here are the first measurements that
stand beside them. One machine, one night, the x3d.lab notebook 07 pipeline (glb through Interchange, stills through Movie Render Queue).
By the promotion rule of Section 9, a gate passed once on one machine lifts its claim from [S] to [L], not to [C]; the numbers
themselves are [C] because they were measured with the instruments named.

### 10.1 The rig

| part | value |
|---|---|
| GPU | NVIDIA RTX PRO 6000 Blackwell Server Edition (95.6 GB), driver 580.82.07, CUDA 13.0, compute capability 12.0 (a Colab G4 runtime) |
| host | Ubuntu 24.04, AMD EPYC 9B45, 48 CPUs, 177 GB RAM |
| engine | Unreal Engine 5.8.4-58902052, Vulkan, shader platforms SM6 and SM6 ray tracing; bindless through `VK_EXT_descriptor_buffer`; async compute off; hardware Lumen with hit lighting, MegaLights and Substrate on |
| X3D to glb | `bpy 5.2.3` with `x3d-blender-io@54aba0c`; `Khronos glTF-Validator 2.0.0-dev.3.10` |
| reference | `X_ITE 16.7.0`, headless Chromium 159.0.8154.6 on ANGLE Vulkan 1.4.312 on the same GPU (not SwiftShader) |
| pipeline | `x3d.lab@70551e8`, notebook 07 (`notebooks/unreal/src/07_unreal.py`); fixes from this run in x3d.lab PR #29 |

```text
  X3D --bpy 5.2.3 + add-on--> glb --validator--> Interchange --> level, lights, cameras
                                                                       |
  calib box --> K = 1.017 (light units)     exposure bracket (720p Lumen)
                                                                       |
                                                                       v
          MRQ stills: preview 1080p Lumen | 4K HW Lumen | 4K path tracer
                                                                       |
            compare vs X_ITE 16.7.0 (same GPU) and Cycles: match, IoU, SSIM, luma
```

### 10.2 The gates of Section 9, as far as this run went

| gate | result | grade of the claim now | evidence |
|---|---|---|---|
| G0 headless import | passed: every scene imported in a one-shot editor run, exit 0 | "Unreal imports our glb" [L] | notebook 07 step 8 scorecard |
| G1 importer coverage | partial: 8 scenes imported (calib, stilllife, two Unreal-project scenes, odyssey, three Khronos controls); triangle WARN on stilllife, 27,560 in the glb against 9,403 counted, Likely the Nanite fallback count | [L] for coverage of these scenes | step 8 accounting rows |
| G2 instancing | recorded failure: Interchange logs `Extension is not supported: EXT_mesh_gpu_instancing` and the instanced exhibition glb arrives as 8 meshes with 1,711 instances dropped; the plain DEF/USE glb of the same scene keeps sharing (1,719 actors on 8 meshes) | "Unreal 5.8.4 reads `EXT_mesh_gpu_instancing`": refuted on this build [C] | Interchange log line |
| G3 coordinates | not run as a dedicated test; silhouettes match X_ITE (below), which a wrong axis swap would break | [L] | indirect |
| G4 light units | calibrated: K = 1.01736 (the code assumed 1.2); rule `lux = lin(i) x pi x K` for a classic directional light | [C] for this engine build and rig | calib box centre pixel, match look |
| G5 engine pairs | partial: stilllife only, numbers below; FLIP not reported | [L] | step 10 |
| G6 frame time | not run (stills only) | unchanged | none |
| G7 behaviour | not run; step 7 freezes animated scenes instead (Section 10.4) | unchanged | none |
| G8 second machine | not run | unchanged | none |

| stilllife, 1080p preview, match look | vs X_ITE 16.7.0 | vs Cycles |
|---|---|---|
| silhouette match (2 px tolerance) | 1.000 | not reported |
| mask IoU | 0.997 | not reported |
| SSIM | 0.8195 | 0.7334 |
| mean colour delta (0 to 255) | 11.5 | not reported |
| luma ratio Unreal / other | 0.715 | 0.601 |

### 10.3 What the run taught, ranked by how much it changes a pipeline

| rank | finding | grade | what to do |
|---|---|---|---|
| 1 | Manual exposure tuned on the calibration box does not fit scenes: odyssey's White Room (four spots at X3D intensity 100) rendered 86 % clipped white at the calibrated EV and wanted -14 EV; the Khronos controls (no lights of their own) wanted +2; one X3D scene still wanted more than +8 | [C] | bracket each scene before expensive stills (notebook 07 `EXPOSURE = "auto"`, PR #29) |
| 2 | The path tracer and Lumen hit lighting trace Nanite's reduced fallback mesh by default: X3D Spheres (64 segments) were visibly faceted in 4K path-traced stills and round with `r.RayTracing.Nanite.Mode 1`, same view | [C] (visual, one view; no metric) | set it on every ray-traced rung |
| 3 | `EXT_mesh_gpu_instancing` is not read by Interchange in 5.8.4 | [C] | ship the DEF/USE glb to Unreal; expand instancing in the import script if counts get large |
| 4 | The USD path brings lights and cameras but no mesh actors; `UsdStageImportOptions` no longer has `import_lights`, `import_cameras`, `meters_per_unit` | [C] for this build | glb is the carrier for Unreal 5.8.4 |
| 5 | The editor binary links ATK and GTK; the stock Ubuntu 24.04 cloud image lacks them, so the first start exits with code 127 | [C] | install the desktop libraries before the first start |
| 6 | Unreal is darker than X_ITE on the same classic scene under the match look (luma ratio 0.715) after calibration | [C] for stilllife | log as a difference; the light model, not the import, is the Likely cause [L] |
| 7 | X_ITE ran on the real GPU (ANGLE Vulkan), not SwiftShader, in the same session | [C] | name the GPU in X_ITE receipts from such runs |

### 10.4 Exposure: the bracket that replaced a hand-set number

```text
  round 1 (one Unreal start, 1280 x 720, Lumen):  +4   0   -4   -8   -12   -16   EV offsets
  score each still: |median luma - 0.38| + 2.5 x max(0, clipped - 2 %) + max(0, black - 25 %)
  round 2: best +-1, +-2; if the best was the edge, also 4 and 8 stops further that way
  render the keepers at the best offset (4K HW Lumen, or the path tracer)
```

| scene | picked offset | note | grade |
|---|---|---|---|
| odyssey, frozen at 0.886 of its 138 s film (the White Room) | -14 EV | first bracket stopped at its -10 edge; the second reached -14 | [C] |
| Khronos Lantern, ToyCar (glTF), WaterBottle | +2 EV | no lights of their own; made for an environment map this stage does not add | [C] |
| ToyCar (X3D 4 conversion) | +8 EV, the edge | also mis-framed: the model is centimetre-sized | [C] |

Animated scenes need a moment. The notebook freezes a scene that is dark at time 0 at its brightest moment (every
TimeSensor-driven interpolator evaluated at one fraction and written into its target); for odyssey that is fraction 0.886, inside the White Room,
so the stills show the authored state of the film at about 122 s, not the time-0 set. [C], `x3d.lab@70551e8:notebooks/unreal/x3due/staging.py`.

## 11. Known physics, a pass line written first, and the GPU's ceiling (2026-11-15)

Same night, same machine as Section 10. Three small X3D 4.0 scenes were written to stress the light model rather than the import, and
measured against both references. Then a pass line for tier 1 was written down before any proof run, and the card's raw compute was measured
from Python on Vulkan. The scenes, cells and a findings README are public in `hagopjay/x3d.lab`, `notebooks/unreal/colab_g4/` (PR #32).

### 11.1 The three scenes (Leg E)

| scene | what it isolates |
|---|---|
| E1 PBR grid | 7 x 7 PhysicalMaterial spheres, metallic 0 to 1 against roughness 0 to 1; one DirectionalLight key, one PointLight fill |
| E2 Cornell box | red and green walls, two boxes, one ceiling light; bounce light and shadows |
| E3 light ladder | each X3D light type in its own bay, PhysicalMaterial against classic Material |

### 11.2 Agreement, and why the whole-frame number misleads

FLIP was computed twice for each pair: over the whole frame, and over object pixels only (pixels where either image is not the flat
magenta key). Match look, preview rung, 1080p; X_ITE 16.7.0 on ANGLE Vulkan on the same GPU; Cycles through the same add-on.

| scene | vs X_ITE, frame / object | vs Cycles, frame / object | object share of the frame |
|---|---|---|---|
| E1 PBR grid | X_ITE produced no still (cause open) | 0.289 / 0.427 | 67.5 % |
| E2 Cornell box | 0.321 / 0.489 | 0.285 / 0.433 | 65.6 % |
| E3 light ladder | 0.092 / 0.735 | 0.091 / 0.724 | 11.7 % |

E3 is the case to remember. Its whole-frame FLIP of 0.09 reads as close agreement, but 88 % of that frame is identical key background. Over the
object it is the largest disagreement of the three. [C] for the numbers. The object score is the one that ranks the scenes correctly.

```text
  whole-frame mean = share x object mean + (1 - share) x background mean
  E3:  0.117 x 0.735 + 0.883 x ~0.007  ~= 0.092     (the background pulls it to near zero)
```

### 11.3 What the scenes named

| gap | grade | evidence | status |
|---|---|---|---|
| Unreal lights cast shadows although X3D 4.0 `shadows` defaults to false | [C] | E2 under the match look | fixed in `x3d.lab` PR #31 (the field is carried to the light; looks can override); not yet re-measured |
| One light model per scene: X_ITE lights PhysicalMaterial with rho/pi x i and classic Material with rho x i; the converter picks one rule for the whole scene | [C] | E3 bays disagree by material kind | open; per-material handling needed |
| Point and spot falloff is inverse-square, matched at the scene centre | [C] | E3 | by design; X3D attenuation is not reproduced |
| Metals read dark with no environment to reflect | [L] | E1 against Cycles | open; an environment light would test it |

Under the cinematic look on the same night, E2 showed colour bleed from Lumen global illumination: red on the near face of the tall box, a
green tint on the floor by the green wall, soft shadows. X_ITE does not compute bounce light, so this is a difference by design, not an
error. [C] by eye, one still.

### 11.4 A pass line for tier 1, fixed before the run

A gate whose bounds are chosen after the numbers are seen can always be passed. These three were written into the proof cell
(`tier1_proof_cells.py`, F1) before it ran. Each is scored per viewpoint on a fresh runtime of `x3d.lab` main:

| check | bound | why this bound |
|---|---|---|
| silhouette | mask IoU against X_ITE >= 0.95 | Leg 1 measured 0.997; geometry and cameras are the solved part |
| repeatable | object FLIP between two renders of the same still by Unreal <= 0.02 | the noise floor; any engine difference below it is not measurable |
| within the reference spread | max(FLIP Unreal-X_ITE, FLIP Unreal-Cycles) <= FLIP X_ITE-Cycles + 0.05 | the two references disagree with each other; Unreal need not beat them, only stay inside their disagreement |

```text
            X_ITE
           /     \
   UE-X  /       \  X-C   <- the references' own spread
        /         \
     Unreal ------ Cycles
            UE-C
  pass if max(UE-X, UE-C) <= X-C + 0.05,  silhouette IoU >= 0.95,  repeat <= 0.02
```

Status: run on 2026-11-15, result in Section 11.7. Tier 1 is not claimed. The prediction written here before the run, graded [S], was
that E3 would fail "within the reference spread" on the light-model gap of Section 11.3. It did, and so did two other views.

### 11.5 The card's ceiling, from Python on Vulkan

`wgpu-py 0.33.0`, forced onto its Vulkan backend, runs WGSL compute shaders on the same GPU. This gives the hardware's ceiling, which the
render pipeline's numbers can be compared against.

| measurement | value | grade |
|---|---|---|
| FP32 fused multiply-add shader, 60 s | 98.1 TFLOPS average (best batch 98.2) | [C] |
| during it: utilisation, power, SM clock | 100 %, 541 W peak, 2,430 MHz | [C] (nvidia-smi, 0.5 s samples) |
| theoretical FP32 at that clock | about 117 TFLOPS (about 24,000 FP32 lanes x 2 x 2.43 GHz) | [L] (lane count not checked on this machine) |
| ray-marched Mandelbulb, 3840 x 2160, 4 rays per pixel, render only | 94.0 fps, 3.12 G rays/s (the burn's first 10 fps average had PNG saves inside its timer) | [C] |
| the same fractal at 7680 x 4320, 64 rays per pixel (2.1 G rays) | 0.67 s | [C] |
| all-pairs N-body, 262,144 bodies, 2,400 steps | 1.48 x 10^12 pair interactions/s; 29.7 TFLOPS at the customary 20 flops per interaction (about 30 % of the FMA figure: each interaction needs a reciprocal square root, which the FMA shader never calls) | [C] for the rate; [L] for the reason |

Unreal's stills on the same machine used 7.5 to 12.6 GB of the card's 95.6 GB, at about 10 s per 1080p Lumen still. The pipeline is far
from the hardware's limits, so no tier-1 result on this rig is limited by the GPU. [C] for the memory figures.

### 11.6 Lessons that change how the next run is written

| rank | lesson | grade |
|---|---|---|
| 1 | Score agreement over object pixels; report the object share beside it | [C] |
| 2 | Write a gate's bounds into the cell before the run that tests them | [C] (method) |
| 3 | Name grades so the engine's job-name sanitiser keeps them apart: `+3` and `-3` both become `_3`; use `p3` / `m3` (the lab now refuses a collision) | [C] |
| 4 | A render rung that turns depth of field and fringe off needs grades to turn them back on in their own cvars | [C] |
| 5 | An exposure fit that compares two images returns exactly 0 when no pixel is lit in both; fall back to a percentile match | [C] |
| 6 | Time only what is measured: a save inside a frame timer cut a 94 fps figure to 10 | [C] |

### 11.7 The proof run: tier 1 not earned, by a small margin in two of three failures

The run of Section 11.4 happened the same night, on a fresh runtime of `x3d.lab` main (auto exposure, Nanite ray-tracing mode and the
`shadows` fix all in), with the bounds unchanged. Rig as Section 10.1: UE 5.8.4 Vulkan SM6+RT with hardware Lumen, X_ITE 16.7.0 on ANGLE
Vulkan on the same GPU, Cycles from Blender 5.2.3, flip-evaluator LDR over object pixels. All figures [C].

| scene / viewpoint | IoU | UE-X | UE-C | X-C | repeat | verdict | the failed check, by how much |
|---|---|---|---|---|---|---|---|
| stilllife / CA_Camera | – | – | 0.214 | – | 0.000 | SKIP | X_ITE returned no still, so there is no outline to score |
| odyssey / DroneCam | 1.000 | 0.667 | 0.699 | 0.527 | 0.000 | FAIL | spread: 0.699 against a bound of 0.577, over by 0.122 |
| odyssey / GiftFrame | 1.000 | 0.626 | – | – | 0.000 | PASS | (no Cycles still for a second viewpoint: two checks of three) |
| E1 PBR grid / Front | 1.000 | 0.221 | 0.260 | 0.298 | 0.000 | PASS | Unreal is closer to X_ITE than Cycles is |
| E2 Cornell box / Front | 0.999 | 0.516 | 0.419 | 0.458 | 0.000 | FAIL | spread: 0.516 against 0.508, over by 0.008 |
| E3 light ladder / Front | 0.980 | 0.735 | 0.724 | 0.677 | 0.000 | FAIL | spread: 0.735 against 0.727, over by 0.008 |

Totals: 2 PASS, 3 FAIL, 1 SKIP. Peak VRAM across the stills was 12.2 GB.

What the run settles:

- **Geometry and cameras are done.** Every outline scored IoU 0.980 or better against X_ITE. [C]
- **Unreal is deterministic here.** A still rendered twice differs by object FLIP 0.000 on every view, so the noise floor is zero, not 0.02. [C]
- **E1 works in X_ITE after all.** The pass of Section 11.2 had no X_ITE still for E1; this run has one, and on it Unreal agrees with X_ITE
  more closely (0.221) than Cycles does (0.298), black fully metallic sphere included. Why the earlier run drew nothing is still not known. [C] for the numbers.
- **The `shadows` fix was not the main gap.** E2's object FLIP to X_ITE went from 0.489 to 0.516 and E3's stayed at 0.735. Point and spot
  falloff (inverse-square in Unreal, matched to X3D attenuation only at the scene's centre) and the one-light-model-per-scene rule remain,
  and both E2 and E3 are lit that way. [C] that the numbers did not move; [L] for the cause.
- **odyssey's DroneCam fails against Cycles, not X_ITE.** One exposure per scene is fitted on one camera (Section 10.4). [S] that this is the cause.

The bounds stay as written. Two failures are within 0.008 of the line; moving the line after seeing them would turn the gate into a
description. The next run changes the pipeline instead: fit each X3D point and spot light's attenuation with Unreal's non-inverse-square
falloff (a light can turn inverse-squared falloff off and take a falloff exponent), and fit exposure per camera. [S] that this closes E2 and E3.

---

## Heuristics

| ID | Rule | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-UNR-1 | Convert UE to X3D with one mirror: point `(x, z, y)/100`, rotation `P R P`; check determinants before trusting any converter. | [C] | det P = -1, det of `P R P` = +1 on four triples | Python, run 2026-11-14 |
| H-UNR-2 | Decide winding by a numeric normal test in the engine's convention; never reverse indices by assumption, and never hide a guess behind `solid='false'`. | [C] | a mirror flips the sign of a cross product | Python, run 2026-11-14 |
| H-UNR-3 | Convert a horizontal field of view to X3D's minimum-angle `fieldOfView` with `2 atan(tan(h/2)/aspect)`. | [C] | 58 degrees at 16:9 gives 34.63 degrees | Python, run 2026-11-14 |
| H-UNR-4 | Write "read, not run" next to any claim about Unreal until gate G0 passes on a named machine. | [L] | no Unreal install in this base | none |
| H-UNR-5 | Compare engines only under one tone mapper, one exposure, one camera, one resolution and one environment light, all recorded. | [L] | Khronos render-fidelity method; rig holds these for X_ITE and Babylon | rig README, read |
| H-UNR-6 | Report a perceptual metric together with the image pair and its fixed settings; a PSNR alone is a rumour. | [C] | offset of 3 gives 38.6 dB, noise sigma 5 gives 34.3 dB | numpy, run 2026-11-14 |
| H-UNR-7 | Log an Unreal frame that looks better than X_ITE as an intended difference; treat X_ITE as the answer key for translation, not quality. | [L] | Lumen and Nanite are outside X3D's light model | digest, [S] for Unreal specifics |
| H-UNR-8 | Count instances from three places (X3D, glb JSON, engine) and require agreement before claiming instancing works. | [C] for the first two | 1,719 / 1,721 nodes / 10 nodes | grep and JSON parse, run 2026-11-14 |
| H-UNR-9 | Do not infer that an instanced glb works in a second engine from a first: the validator cannot read `EXT_mesh_gpu_instancing`. | [C] | `NOT VALIDATED` line | `Khronos glTF-Validator 2.0.0-dev.3.10`, run 2026-11-14 |
| H-UNR-10 | Treat behaviour as a separate tier: no glb import gives ROUTEs; tier 4 needs software that does not exist. | [L] | no importer found; ROUTE count in glb is 0 | read; JSON parse |
| H-UNR-11 | Keep a calibration constant for X3D lights in Unreal as an explicit manifest field, not a hidden multiplier. | [S] | design expectation | none |
| H-UNR-12 | Bracket exposure per scene before any expensive still; a calibration box fixes light units, not exposure. | [C] | odyssey -14 EV, Khronos controls +2 EV | UE 5.8.4 on RTX PRO 6000, 2026-11-14 |
| H-UNR-13 | Turn on `r.RayTracing.Nanite.Mode 1` wherever rays are traced, or curved X3D primitives render faceted. | [C] | faceted spheres in the path tracer, round with the setting | UE 5.8.4 on RTX PRO 6000, 2026-11-15 |
| H-UNR-14 | Ship the DEF/USE glb to Unreal, not the `EXT_mesh_gpu_instancing` glb, until Interchange reads the extension. | [C] | 1,711 instances dropped, 8 meshes kept | UE 5.8.4 Interchange log, 2026-11-15 |
| H-UNR-15 | When a bracket's best is its edge, extend it; an edge pick means the scene's exposure was not reached. | [C] | odyssey picked -10 at the edge, then -14 | same run |
| H-UNR-16 | Report FLIP over object pixels, with the object share, beside any whole-frame score; a keyed background dilutes the mean toward zero. | [C] | E3 0.092 whole frame, 0.735 over its 11.7 % object | flip-evaluator LDR on G4 stills, 2026-11-15 |
| H-UNR-17 | Fix a gate's bounds in the cell before the run that tests it, and let the references' own disagreement set the agreement bound. | [C] (method) | bounds in `tier1_proof_cells.py` written before any proof run | `x3d.lab` PR #32 |
| H-UNR-18 | Carry X3D 4.0's `shadows` field to the engine light; a renderer default that casts shadows is a silent disagreement. | [C] | E2 shadows under the match look | UE 5.8.4 on RTX PRO 6000, 2026-11-15; fix `x3d.lab` PR #31 |
| H-UNR-19 | Measure the hardware ceiling separately from the pipeline, so a slow number can be blamed on the right layer. | [L] | 98.1 TFLOPS from Python against 7.5-12.6 GB and 10 s stills in Unreal | wgpu-py 0.33.0 Vulkan, 2026-11-15 |
| H-UNR-20 | When a gate fails by a hair, keep the bound and change the pipeline; report the margin beside the verdict. | [C] (method) | E2 and E3 over the spread bound by 0.008 each, bounds unchanged | tier-1 proof run, 2026-11-15 |

---

## Drills

### D-UNR-1 Derive and check the axis swap
- **Level:** L2
- **Task:** write `P = [[1,0,0],[0,0,1],[0,1,0]]`, compute `det P`, then the determinant of the alternative `Q = [[1,0,0],[0,0,1],[0,-1,0]]`. Convert the UE yaw 90 degrees rotation `[[0,-1,0],[1,0,0],[0,0,1]]` to X3D with `P R P` and read the axis-angle.
- **Verify:** `python3 -c "import numpy as np; ..."` with `np.linalg.det`; axis from `R[2][1]-R[1][2]`, `R[0][2]-R[2][0]`, `R[1][0]-R[0][1]`.
- **Answer:** `det P = -1`, `det Q = +1` (so Q is a rotation and cannot fix handedness); `P R P = [[0,0,-1],[0,1,0],[1,0,0]]`, axis-angle `0 -1 0 1.5708`.
- **Checked:** 2026-11-14 Python 3 (the converters' own `ue_rot`, `mm`, `axis_angle`).

### D-UNR-2 Convert a field of view
- **Level:** L1
- **Task:** a camera has a horizontal field of view of 58 degrees on a 16:9 image. What `fieldOfView` (radians) does X3D need? What is it for a 35 mm lens on a 23.76 mm sensor?
- **Verify:** `python3 -c "import math; h=math.radians(58); print(2*math.atan(math.tan(h/2)/(16/9)))"`.
- **Answer:** 0.6045 rad (34.63 degrees); for the lens, horizontal 37.50 degrees and vertical 21.62 degrees at 16:9.
- **Checked:** 2026-11-14 Python 3.

### D-UNR-3 Catch the winding flip
- **Level:** L2
- **Task:** apply `P` to the triangle `(0,0,0), (1,0,0), (0,1,0)`. Compute `(b-a) x (c-a)` before and after. Compare the after-normal with `P` times the before-normal. State what a converter must do.
- **Verify:** numpy `np.cross`.
- **Answer:** before `(0,0,1)`; after `(0,-1,0)`; `P n = (0,1,0)`. They differ in sign, so the right-handed cross-product normal is not carried by the mirror. A converter must pick index order by a numeric test against the engine's front-face rule, and `solid='false'` hides a wrong pick.
- **Checked:** 2026-11-14 Python 3 with numpy.

### D-UNR-4 Instancing arithmetic
- **Level:** L1
- **Task:** from the public release note, compute the node and byte reduction of the exhibition scene when instancing is on, and confirm the note says it.
- **Verify:** `grep -c "1,721 nodes and 491,832 B to 10 nodes and 125,224 B" release_notes.md` in `x3d-blender-io@ab99988`; `python3 -c "print(1-10/1721, 1-125224/491832)"`.
- **Answer:** the grep prints 1; node reduction 99.4 %; byte reduction 74.5 %. For the aurora scene 1,224 to 16 nodes (98.7 %) and 1,097,864 to 864,228 B (21.3 %).
- **Checked:** 2026-11-14 grep on `x3d-blender-io@ab99988` and Python 3.

### D-UNR-5 Break a PSNR comparison
- **Level:** L3
- **Task:** make two 64 x 64 random RGB images that differ by a constant offset of 3 and two that differ by Gaussian noise of sigma 5. Compute the PSNR of each. Then construct a third pair, identical except for one 8 x 8 square set to black, whose PSNR is higher than the offset pair's. What does that say about using PSNR to rank engines?
- **Verify:** numpy; PSNR = `10 log10(255² / mean((A-B)²))`.
- **Answer:** offset 3 gives 38.63 dB and noise sigma 5 gives 34.31 dB (seeded as in the check). A black 8 x 8 square on the same seeded image (1.6 % of the pixels) gives MSE 348.6 and 22.71 dB, lower than both, so here PSNR does rank it worse; but the same square on a dark image would score far higher, and the offset pair, which is wrong everywhere, scores best. The point is that PSNR cannot tell a localised wrong object from a global exposure shift. That is why the rig also reports a geometry-only delta and why FLIP's error map is kept.
- **Checked:** 2026-11-14 numpy for all three numbers (offset 38.63 dB, noise 34.31 dB, square 22.71 dB).

### D-UNR-6 Write the pass and fail line for a gate
- **Level:** L3
- **Task:** for gate G3 (coordinate test), write the exact checker: given the glb JSON and an Unreal actor transform dump, return PASS or FAIL. Use X3D `(1,2,3)` m and 90 degrees yaw about Y.
- **Verify:** an Unreal-side dump; not available here.
- **Answer:** expected UE location `(x*100, z*100, y*100) = (100, 300, 200)` cm; the yaw is the inverse of the Section 4.2 mapping. The checker passes if location is within 1 cm and the actor's forward vector is within 0.1 degrees of the expected one.
- **Checked:** not run (no Unreal here).

### D-UNR-7 Pick an exposure from a bracket
- **Level:** L2
- **Task:** a fake engine draws a still whose linear value is `0.38^2.2 x 2^-(ev + 14)`, shown with gamma 2.2. Score offsets +4 to -16 with the Section 10.4 rule, run the second round, and report the pick and whether it is an edge.
- **Verify:** `pytest notebooks/unreal/tests/test_ue_g4_first_run.py::test_fit_exposure_finds_a_dark_scene` in `hagopjay/x3d.lab` (PR #29 branch).
- **Answer:** round 1 picks -12 or -16 by a hair; round 2 tries -10, -11, -13, -14 (and -18, -20 at an edge) and picks -14, not an edge.
- **Checked:** 2026-11-15 pytest 9 on the PR #29 branch (11 new tests pass).

### D-UNR-8 Count what Interchange kept
- **Level:** L2
- **Task:** for an instanced glb, count meshes and instances from the glb JSON (`EXT_mesh_gpu_instancing` accessors), then the static mesh actors Unreal created. State which number the engine lost and which log line says why.
- **Verify:** glb JSON parse; the Interchange log of the import.
- **Answer:** 8 meshes in both; 1,711 instances in the glb, none in the level; `Extension is not supported: EXT_mesh_gpu_instancing`.
- **Checked:** 2026-11-15 UE 5.8.4 Interchange on RTX PRO 6000 (one run).

---

## Honest limits

- **No Unreal run exists.** No frame, import log, actor count or frame time came from Unreal 5.8 in this base. Everything on Unreal behaviour is [S] and says so. [S]
- **Superseded 2026-11-15 by Section 10:** one run on one machine now stands behind the import, calibration, instancing, exposure and Nanite rows there. Frame times, behaviour, a second machine and FLIP between engines are still not measured. The stills and logs of that run are in a private notebook output, not in a public repository, so a reader cannot re-open them; the notebook and its tests are public. [L]
- **Updated 2026-11-15 by Section 11:** FLIP between engines is now measured for three scenes on one machine, over object pixels. Frame times, behaviour and a second machine are still not measured, the tier-1 proof run has not happened, and why X_ITE produced no still for E1 is not known. [L]
- **Updated 2026-11-15 by Section 11.7:** the tier-1 proof run happened and tier 1 was not earned (2 PASS, 3 FAIL, 1 SKIP on one machine). The cause of the failures is graded [L] and [S], not measured; a second machine and frame times are still missing. [C] for the verdicts.
- **The Nanite finding is visual.** One view, two stills, judged by eye; no metric was computed between them. [L]
- **The Unreal digest is a lead.** It was written 2026-11-12 with some vendor pages unreachable (the licence pages returned an error), so licence terms, product pricing and web-streaming claims are not stated here. A reader needs the vendors' own pages. [S]
- **Web targets move fast.** The digest reports an experimental WebGPU target in a 5.9 preview and a commercial streaming route that supports 5.8; both are vendor or Epic claims, not tested, and dated. They are not repeated as facts here. [S]
- **The Unreal-project converters are not public.** Section 5 and 8 counts agree with a public release note; the scripts themselves and the outputs are in a private project folder. A reader outside cannot repeat the counting. [L]
- **The 1,719 versus 1,711 + 18 arithmetic was not decomposed.** The three counts are reported raw. [S] for any story about why they do not sum.
- **Winding in the converters is unchecked.** Sign flips under a mirror are derived; whether the converters' reversed index order is right for Unreal's front-face rule was never rendered. [S]
- **Proxy materials.** Procedural HLSL materials became constants. Any "looks like" statement about the two projects would be about the proxies. [S]
- **Rig numbers are carried.** The probe table and the 0-of-262,144 pixel result are from the repo, not re-run in this session. [L]
- **FLIP, SSIM and LPIPS were not run.** Only PSNR (a numpy formula) was run. [S]

---

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-UNR-1 | determinant of the axis swap P | -1 | [C] | Python 3, 2026-11-14 | derivation in Section 4.1 |
| N-UNR-2 | determinant of the alternative `(x, z, -y)` | +1 | [C] | Python 3, 2026-11-14 | Section 4.1 |
| N-UNR-3 | UE `(120, 340, 90)` cm to X3D | `(1.2, 0.9, 3.4)` m | [C] | converter formula, 2026-11-14 | Section 4.1 |
| N-UNR-4 | yaw 90 degrees to X3D rotation | `0 -1 0 1.5708` | [C] | converter functions, 2026-11-14 | Section 4.2 |
| N-UNR-5 | horizontal 58 degrees at 16:9 to `fieldOfView` | 0.6045 rad (34.63 degrees) | [C] | Python 3, 2026-11-14 | Section 4.4 |
| N-UNR-6 | float32 spacing at 100,000 and 1,000,000 | 0.0078 and 0.0625 | [C] | numpy, 2026-11-14 | Section 4.5 |
| N-UNR-7 | exhibition output `<Transform>` count | 1,719 | [C] | `grep -o '<Transform '`, 2026-11-14 | converter output (private file) |
| N-UNR-8 | aurora static output `<Transform>` / USE | 1,216 / 1,208 | [C] | grep, 2026-11-14 | converter output; re-run byte-identical |
| N-UNR-9 | exhibition glb nodes: flat / instanced | 1,721 / 10 | [C] | JSON parse, `Khronos glTF-Validator 2.0.0-dev.3.10`, 2026-11-14 | `x3d-blender-io@ab99988:release_notes.md` agrees |
| N-UNR-10 | exhibition glb bytes: flat / instanced | 491,832 / 125,224 | [C] | file size, 2026-11-14 | same |
| N-UNR-11 | aurora glb nodes: flat / instanced | 1,224 / 16 | [C] | JSON parse, 2026-11-14 | same |
| N-UNR-12 | aurora glb bytes: flat / instanced | 1,097,864 / 864,228 | [C] | file size, 2026-11-14 | same |
| N-UNR-13 | triangles: exhibition / aurora static | 2,064 / 27,544 | [C] | `Khronos glTF-Validator 2.0.0-dev.3.10`, 2026-11-14 | carried project glbs |
| N-UNR-14 | validator verdict on all four static and instanced glbs | 0 errors, 0 warnings | [C] | same | same |
| N-UNR-15 | instanced render versus flat render in Babylon.js 9.32.0 | 0 of 262,144 pixels differ | [L] | Chromium 153, SwiftShader (carried) | `x3d-blender-io@ab99988:release_notes.md` |
| N-UNR-16 | probe p1 / p2 centre patch: X_ITE | 74 / 204 | [L] | `X_ITE 16.7.1`, Chromium 153, SwiftShader (carried) | `x3d-blender-io@ab99988:tools/fidelity_rig/README.md` |
| N-UNR-17 | PSNR of offset-3 pair / noise sigma 5 pair | 38.63 dB / 34.31 dB | [C] | numpy, 2026-11-14 | Section 7.2 |
| N-UNR-18 | Unreal 5.8 frames rendered in this base | 0 | [C] | none | this chapter |
| N-UNR-19 | light calibration constant K | 1.01736 (assumed 1.2) | [C] | UE 5.8.4 on RTX PRO 6000 Blackwell SE, driver 580.82.07, 2026-11-14 | notebook 07 step 8 (recorded run, not in a repo) |
| N-UNR-20 | stilllife vs X_ITE 16.7.0: match / IoU / SSIM | 1.000 / 0.997 / 0.8195 | [C] | same, X_ITE on ANGLE Vulkan, Chromium 159 | notebook 07 step 10 |
| N-UNR-21 | stilllife luma ratio Unreal / X_ITE and Unreal / Cycles | 0.715 / 0.601 | [C] | same | notebook 07 step 10 |
| N-UNR-22 | cold start (first shader compile) / warm start | 312.7 s / 15.3 s | [C] | same, 44 shader workers | notebook 07 step 6 |
| N-UNR-23 | 1080p Lumen still, stilllife / peak VRAM | 10 s / 7.5 GB | [C] | same | notebook 07 step 9 |
| N-UNR-24 | instances dropped by Interchange from the instanced glb | 1,711 | [C] | same | Interchange log |
| N-UNR-25 | odyssey White Room: clipped pixels at the calibrated EV / picked offset | 86 % / -14 EV | [C] | same | exposure bracket |
| N-UNR-26 | Khronos controls: picked offset | +2 EV | [C] | same | exposure bracket |
| N-UNR-27 | scorecard of the first leg | 40 PASS, 3 WARN, 0 FAIL, 1 SKIP | [C] | same | notebook 07 step 11 |
| N-UNR-28 | E1 PBR grid vs Cycles, FLIP frame / object | 0.289 / 0.427 | [C] | flip-evaluator LDR, G4 stills, 2026-11-15 | Section 11.2 |
| N-UNR-29 | E2 Cornell box vs X_ITE, FLIP frame / object | 0.321 / 0.489 | [C] | same | Section 11.2 |
| N-UNR-30 | E2 Cornell box vs Cycles, FLIP frame / object | 0.285 / 0.433 | [C] | same | Section 11.2 |
| N-UNR-31 | E3 light ladder vs X_ITE, FLIP frame / object | 0.092 / 0.735 | [C] | same | Section 11.2 |
| N-UNR-32 | E3 light ladder vs Cycles, FLIP frame / object | 0.091 / 0.724 | [C] | same | Section 11.2 |
| N-UNR-33 | E3 object share of the frame | 11.7 % | [C] | same | Section 11.2 |
| N-UNR-34 | FP32 FMA throughput from Python on Vulkan, 60 s | 98.1 TFLOPS (best 98.2) | [C] | wgpu-py 0.33.0 Vulkan, RTX PRO 6000 Blackwell SE, driver 580.82.07, 2026-11-15 | Section 11.5 |
| N-UNR-35 | power and SM clock peak during it | 541 W, 2,430 MHz | [C] | nvidia-smi, 0.5 s samples, 2026-11-15 | Section 11.5 |
| N-UNR-36 | Mandelbulb 4K, 4 rays per pixel, render only | 94.0 fps (3.12 G rays/s) | [C] | wgpu-py 0.33.0 Vulkan, RTX PRO 6000 Blackwell SE, 2026-11-15 | Section 11.5 |
| N-UNR-37 | tier-1 bounds: IoU / repeat / spread margin | 0.95 / 0.02 / 0.05 | [C] | `x3d.lab` PR #32, `tier1_proof_cells.py` | Section 11.4 |
| N-UNR-38 | Mandelbulb 8K at 64 rays per pixel | 0.67 s | [C] | same | Section 11.5 |
| N-UNR-39 | all-pairs N-body, 262,144 bodies: interaction rate | 1.48 x 10^12 /s (29.7 TFLOPS at 20 flops each) | [C] | same | Section 11.5 |
| N-UNR-40 | tier-1 proof run verdicts (PASS / FAIL / SKIP) | 2 / 3 / 1 | [C] | UE 5.8.4 Vulkan SM6+RT, X_ITE 16.7.0 ANGLE Vulkan, Cycles 5.2.3, flip-evaluator LDR object pixels, RTX PRO 6000 Blackwell SE, 2026-11-15 | Section 11.7 |
| N-UNR-41 | outline IoU vs X_ITE, range over scored views | 0.980-1.000 | [C] | same | Section 11.7 |
| N-UNR-42 | repeat render object FLIP, every view | 0.000 | [C] | same | Section 11.7 |
| N-UNR-43 | E1 PBR grid: UE-X / UE-C / X-C object FLIP | 0.221 / 0.260 / 0.298 | [C] | same | Section 11.7 |
| N-UNR-44 | E2 Cornell box: UE-X / UE-C / X-C object FLIP | 0.516 / 0.419 / 0.458 | [C] | same | Section 11.7 |
| N-UNR-45 | E3 light ladder: UE-X / UE-C / X-C object FLIP | 0.735 / 0.724 / 0.677 | [C] | same | Section 11.7 |
| N-UNR-46 | odyssey DroneCam: UE-X / UE-C / X-C object FLIP | 0.667 / 0.699 / 0.527 | [C] | same | Section 11.7 |
| N-UNR-47 | peak VRAM across the proof run's stills | 12.2 GB | [C] | same | Section 11.7 |

---

## Sources and provenance

- `x3d-blender-io@ab99988`: `release_notes.md` (Group instances entry), `tools/fidelity_rig/README.md`, `blender_leg.py`. Public repository `hagopjay/x3d-blender-io`.
- Khronos glTF extension registry, fetched 2026-11-14.
- Two converter scripts for Unreal-project scenes (manifest to X3D; C++ maths to X3D): read in full, one re-run (byte-identical output), outputs counted and the produced glbs re-validated with `gltf-validator@2.0.0-dev.3.10` on 2026-11-14. The scripts and the projects are not in a public repository; counts are cross-checked against the public release note.
- A private digest of Unreal, web-reach, Castle and quality-metric sources (written 2026-11-12, one adversarial pass 2026-11-12). Read as a lead. Its Unreal, web, licence and metric-tool claims are not re-checked and are graded [S].
- `x3d.lab@70551e8`: `notebooks/unreal/src/07_unreal.py`, `x3due/staging.py`, `x3due/tier.py`; the fixes of Section 10 in x3d.lab PR #29. Public repository `hagopjay/x3d.lab`.
- The 2026-11-14 to 15 run: notebook 07 output read as it ran (scorecard, Interchange and render logs, stills); not in a public repository.
- Sibling chapters: [11 glTF, USD and Khronos](11-gltf-usd-khronos.md), [08 The Babylon bridge](08-babylon-bridge.md), [09 Castle Game Engine](09-castle-engine.md), [13 Physics](13-physics.md).
