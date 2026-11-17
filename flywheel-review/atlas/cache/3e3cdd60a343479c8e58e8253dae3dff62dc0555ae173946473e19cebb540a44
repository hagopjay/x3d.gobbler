# 08. The Babylon bridge

> **Say it:** one X3D file is the master, our own reader runs its events, and Babylon on WebGPU only paints the result; every picture is a claim against X_ITE on a named rig, every fallback says so on screen, and nothing about speed has been measured. **[C]**

| field | value |
|---|---|
| chapter code | `BAB` |
| prerequisites | [01 The tether](01-the-tether.md) for the loop; [06 X_ITE, the reference renderer](06-xite-the-oracle.md) for the reference arm and its patch rules; [02 Loom laws](02-loom-laws.md) for laws 38 to 40 |
| after this you can | (1) recount the bridge's node coverage and name the denominator; (2) read the 50-trap playbook by tier; (3) measure and read a PSNR against X_ITE without over-reading it; (4) port a shader by hash and prove a miss falls back; (5) follow the append-only procedure for a new demo |
| sources read | x3d.loom@162ab18:x3d.webgpu/{STATE,PATHS,BABYLON,BENCHMARK,SPEC}.md, the four BABYLON-BRIDGE-PLAYBOOK files, bridge/, demo/src/, runs/webgpu-*/; x3d.demo@d10b457:{CHANGELOG.md,docs/index.html}; x3d.docs@f172f67:docs/vendor/x_ite/x_ite.min.js |
| instruments used | `x3d.loom@162ab18`, `X_ITE 16.7.0` (grep only), `X_ITE 16.4.3` to `16.6.0` per receipt row, `Babylon 9.32.0`, `Chromium 153.0.8010.12 (Chrome for Testing), SwiftShader`, Node 22.23.4, Python 3 (numpy 2.5.3, Pillow 12.3.0, lxml), `xmllint`, `x3d_mcp fork b4efcd3` and `X3DUOM 4.0` through the bridge driver; software GL only |

Rig for every **[C]** below that this chapter re-ran (2026-11-14): read-only checkouts, scratch copies for anything that writes, Node 22.23.4, Python with `-I`, no network, no GPU. A number read from a recorded run is named by receipt path and graded **[L]** unless a drill re-derived it.

## 1. The map

```text
  scene.x3d   the master: validated first (chapters 01, 03), never edited to please a renderer
      |
      +------------------------+---------------------------------+
      v                        v                                 v
  X3D validator          X_ITE 16.x (WebGL2)            OUR READER = the brain
  XSD + semantic rules   reference body                 reader.js  parse, DEF/USE, ROUTE
  (chapter 03)           draws pixels A                 kit.js + nodes/*.js  event nodes
                              |                         sai.js  X3D.getBrowser() shim
                              |                                |  node tree + events
                              |                                v
                              |                   BABYLON 9.32.0 = the body (WebGPU)
                              |                   body.js  body-cam.js  body-br.js
                              |                   wgsl.js  FNV-1a(GLSL) -> hand WGSL
                              |                                |
                              |                                v
                              +-------> compare <----------- pixels B
                                           |
                                           v
                                 RECEIPT.md (rig, versions) + GAPS.md (each gap graded)
```

Sections: 2 why a second renderer; 3 architecture; 4 node coverage recounted; 5 the 50-trap playbook; 6 the parity method; 7 the ports; 8 laws 39 and 40 in code; 9 shader porting; 10 the adapter trap; 11 a 16-step port procedure; 12 why there is no speed claim.

**In scope:** the bridge as built in `x3d.loom@162ab18:x3d.webgpu/`, its tracker and playbook, and how to measure it. **Out of scope:** X_ITE internals ([06](06-xite-the-oracle.md), [the X_ITE masterclass](../x_ite/MASTERCLASS.md)); the Loom's AST teardown ([the loom masterclass](../x3d.loom/MASTERCLASS.md)); Castle on its own renderer ([09](09-castle-engine.md)); glTF export as a route ([11](11-gltf-usd-khronos.md)); physics ([13](13-physics.md)). **No speed claim appears here.** No receipt in the repository holds a timing from a real GPU for any Babylon or WebGPU body (section 12).

**Read next:** deeper, [06 X_ITE, the reference renderer](06-xite-the-oracle.md) for the arm every number here is measured against; wider, [07 x3d.xray](07-xray.md) for a second consumer of the same "scene as the master, viewer as a witness" idea.

## 2. Why: a second renderer, and why the file stays the master

| fact | value | grade | instrument | source |
|---|---|---|---|---|
| X_ITE draws through WebGL2 only | 0 hits for "webgpu", 0 for "navigator.gpu", 1 `getContext("webgl2"` in `x_ite.min.js` 16.7.0 (sha256 prefix b7df063e8cb1) | C | grep over the vendored bundle, `X_ITE 16.7.0` | x3d.docs@f172f67:docs/vendor/x_ite/x_ite.min.js (re-run: `grep -o -i webgpu` on the file, counted) |
| X3D cannot name a WebGPU shader | 4.1 draft lists Cg, GLSL, HLSL; VERTEX and FRAGMENT parts only; `WGSL` and `COMPUTE` need a standards proposal (gate G5) | L | read in README.md and SPEC.md | x3d.loom@162ab18:x3d.webgpu/README.md |
| scored options A to G | F (hybrid: X_ITE stays truth, showpieces on a runtime plus WebGPU body) 30 of 35; all others 19 to 25 | L | the scorecard is a judgement; every effort figure is [S] | x3d.loom@162ab18:x3d.webgpu/PATHS.md |
| why not export to glTF and use any engine | glTF drops ROUTEs, Script and shader nodes; the validator checks the source while the viewer would see a derived file (only option B fails the tether test outright) | L | PATHS.md section 2, BABYLON.md section 2.2 | x3d.loom@162ab18:x3d.webgpu/PATHS.md |

The design that follows is F on a Babylon body (path G): X_ITE stays the oracle and the validator's target, and the bridge renders showpieces, each gated by a measured comparison against X_ITE. This is [Loom law 38](02-loom-laws.md), one master, many renderers: a renderer that disagrees is a finding about the reader or the body, never a reason to edit the scene.

Babylon is the default body because, among the engines surveyed, it alone has a path from GLSL to WGSL [L]. The bridge never used that path: `grep -rli 'glslang\|twgsl'` over `demo/src`, `bridge/src` and `runs/webgpu-*` returns 0 files [C, 2026-11-14]; it hand-ports shaders (section 9). Gate G2 (do the Collider's GLSL programs compile through glslang plus twgsl and match X_ITE?) is listed in `x3d.webgpu/README.md` and has no receipt: `bench/receipts/` holds one file, the G1 adapter probe [C, `ls`].

## 3. Architecture: the reader is the brain, Babylon is the body

The reader holds time, ROUTEs, sensors and the SAI; Babylon objects are disposable views of the node tree; a page written for X_ITE keeps calling `X3D.getBrowser()` and a shim answers.

```text
  page app.js (unchanged)           one frame
        |  X3D.getBrowser()...
        v
  +----------+  fields   +--------------------------+  changed(node, field)  +-------------+
  | sai.js   | --------> | reader.js  node tree     | ---------------------> | body.js     |
  | shim     | <-------- | emit / drain events      | <--------------------- | Babylon     |
  +----------+ callbacks | DEF/USE = shared objects |  picks, camera, time   | meshes,     |
                         | ROUTEs, TimeSensor       |                        | materials,  |
  kit.js: BR.node(name, spec), one file per node     |                        | lights,     |
  (field table from X3DUOM; receive/tick/build)      |                        | cameras     |
                         +--------------------------+                        +-------------+
                  ComposedShader GLSL -> whitespace collapse -> FNV-1a -> wgsl.js table
                  hit: hand-ported WGSL.  miss: Material fallback + notice on screen
```

Files, with `wc -c` sizes [C] (`x3d.loom@162ab18:x3d.webgpu/`): `demo/src/brain/reader.js` 30,896 B (parse, typed fields, DEF/USE, ROUTE cascade, TimeSensor, interpolators); `body.js` 33,752 (node tree to Babylon: groups, shapes, lights, PBR, lines, text, clip planes); `body-cam.js` 13,540 (viewpoints, orbit, picking, frame loop); `sai.js` 21,911 (`getNamedNode`, `createNode`, `addRoute`, `replaceWorld`, callbacks); `wgsl.js` 12,111 (hash-keyed ports); `shared/adapter.js` 1,097 and `shared/timing.js` 11,928 (section 10, section 12); `bridge/src/kit.js` 31,928 (`BR.node(name, spec)`: field table, `receive`, `tick`, `init`, `build`, `geometry`, `changed`); `bridge/src/body-br.js` 55,254 (the Babylon side of the kit; nodes without a `build` stay silent); `bridge/src/fidelity.js` 6,439 (preflight report); `bridge/src/nodes/*.js` 115 files, one per node.

A kit node is small: `BooleanToggle` is one `BR.node` call with a field table and one `receive`; its test spec is `set`, `event`, `expect` steps run in our reader and in X_ITE through the SAI both speak. On a scratch copy, `node --test tools/*.test.js` passed 33 of 33 and `python3 tools/driver.py check BooleanToggle --no-xite` printed `PASS BooleanToggle xsd:ok ours:pass 9/9 xite:skipped` [C, 2026-11-14]; `--no-xite` is exploratory and cannot close a batch.

What exists is not what the spec describes: `SPEC.md` and `BABYLON.md` describe a TypeScript runtime generated from X3DUOM 4.1 and registered as a Babylon `SceneLoader` plugin, with a Script sandbox and a load receipt; what runs is plain JavaScript (the demo README says "working demos, not the runtime the spec describes"). The spec's M1 parity rule (mean absolute difference at most 4/255, luma within 0.01 against X_ITE 16.7.0) has been applied to no port [C: every receipt uses PSNR, MAD or silhouette overlap].

## 4. Node coverage, recounted at x3d.loom@162ab18

The primer v2 of 8 November said **68 of 260** X3D 4.0 node types. The tracker at `162ab18` says **186 of 260**: `python3 tools/driver.py status` prints `reader knows 186/260 | base 75 blocked 1 bridged 41 claimed 8 gap 70 todo 65`. Both are right about different things, and the difference is the lesson.

Census commands: D-BAB-1 (`node tools/census.js ../demo/src`, today) and D-BAB-2 (the same on `git archive 60824ce`); all re-run 2026-11-14.

| denominator | count | share of 260 | what it measures | grade | instrument |
|---|---|---|---|---|---|
| concrete nodes in the tracker | 260 | 100% | `X3dUnifiedObjectModel-4.0.xml`; includes `ProtoInstance` syntax | C | `X3DUOM 4.0` via `NODES.json` meta |
| page-bundle census, 8 Nov (60824ce) | 68 (72 defs) | 26.2% | types with a field table in at least one Babylon page | C | `census.js`, re-run on `git archive 60824ce` |
| same census, today | 75 (79 defs) | 28.8% | adds Inline, LOD, ProximitySensor, four HAnim names from the Demiurge and Dynasty parts | C | `census.js`, 162ab18 |
| same census plus the hall extension | 83 (87 defs) | 31.9% | adds the 8 nodes marked `claimed` | C | `census.js` with `hall/reader-ext-hl.js` |
| tracker headline "reader knows" | 186 | 71.5% | `base` 75 + kit modules 111 (41 `bridged`, 70 `gap`) | C | `driver.py status` |
| bridged without a logged gap | 41 | 15.8% | fixture validates against the 4.0 XSD, test passes in our reader and X_ITE | C | `driver.py status` |
| still `todo` | 65 | 25.0% | NURBS 13, VolumeRendering 13, RigidBodyPhysics 13 (+1 blocked), Geospatial 11, DIS 6, Picking 5, HAnim 2, TextureProjection 2 | C | `NODES.json` |

The delta since the primer, like for like [C]:

| step | change | cause |
|---|---|---|
| 68 to 75 on the page-bundle census | +7 | Demiurge (Inline, LOD, ProximitySensor, four HAnim types) and Dynasty added reader parts |
| 75 to 186 on the tracker headline | +111 | kit modules written batch by batch: 41 `bridged`, 70 `gap` |
| 68 to 186, the naive subtraction | +118 | mixes two definitions; the tracker did not exist at 60824ce (first commit `db725e8`, 8 Nov, after the primer's tree) |
| 175 (batch 20, 9 Nov) to 186 (batch 26, 13 Nov) | +11 net | batches 21 to 26 filled 30 tracker slots (17 `bridged`, 13 `gap`), so 19 of them added no name; the batch-21 commit message says five `gap` nodes moved to `bridged` [C, `git show e6c3f9a`] |

Batches 21 to 26 arrived through PRs #43 (batch 21), #44 (22, 23) and #45 (24, 25, 26) on 13 Nov. The headline printed in each `BATCH-NN.md` is a snapshot of a mutable tracker and is not monotonic:

| batch | nodes | bridged / gap | headline after | PSNR range, dB (320 x 240) |
|---|---|---|---|---|
| 21 | five fan, strip and quad sets | 5 / 0 | 175 | 32.71 to 34.91 (5 rows) |
| 22 | StaticGroup, Texturing3D coordinate nodes | 3 / 2 | 179 | 33.85 to 36.63 (6 rows) |
| 23 | CADAssembly, CADFace; three particle emitters and models | 2 / 3 | 184 | 11.73 to 38.03 (11 rows) |
| 24 | FillProperties, TwoSidedMaterial, TextureCoordinateGenerator, two 3D textures | 0 / 5 | 184 | 16.62 to 32.13 (5 rows) |
| 25 | four 2D geometries; LineSet | 4 / 1 | 181 | 26.35 to 35.86 (5 rows) |
| 26 | CADLayer, CADPart, Polyline2D; CoordinateDouble, Polypoint2D | 3 / 2 | 186 | 28.35 to 40.03 (10 rows) |

The dip at batch 25 (184 to 181) is consistent with `driver.py reopen`, which returns worked-on nodes to `wip` before they are re-checked [L, docstring read; the batch-25 reopen list was not traced]. All 42 visual rows together: PSNR 11.73 to 40.03, median 35.92 [C, parsed from `BATCH-21..26.md`]. Read those with section 6: a node can PASS with 11.73 dB.

What is missing (`NODES.json`) [C]: NURBS 13 and VolumeRendering 13 are all `todo`; RigidBodyPhysics has 13 `todo` and 1 `blocked`; Geospatial 11, DIS 6 and Picking 5 are `todo`; Sound has 19 of 21 nodes at `gap` (the Analyser note says nothing is wired into the analyser yet; not checked for the other 18); Shaders 5 of 8 and Layout 5 of 5 are `gap`.

**Three claims hide behind one count.** "Reader knows" means a field table exists; it does not mean the node passes a fixture or that the picture is right. The repository's own assessment of the tracker at `6b3cb76` says recognising, passing a field test and drawing correctly "are different achievements", that the canonical test bundle registered 180 names at the 175 headline, and that the tracker is "not a rendering conformance percentage" [L, read, not re-run]. `bridged` is the strongest word in the tracker and still means one fixture in two engines at 320 x 240.

A name-level census of the 111 parseable demo scenes (86 base-only, 22 needing a `gap`, `todo` or `claimed` node, 1 with unknown names) is drill D-BAB-5; "base" is the union of six reader parts, not what any one page loads.

### 4.1 Volume rendering: ten nodes, one lattice (x3d.loom batch 43)

X_ITE 16.6.0 does not ray-cast a volume. It draws 400 view-aligned quads (200 at LOW, 600 at HIGH), spaced |dimensions| / 399 apart along the viewing direction, each reading the voxel texture and blended back to front with plain source-alpha blending and no correction for the spacing. So `alpha` means "per slice": 230 slices of alpha 0.02 give 1 - 0.98^230 = 0.990 opaque (D-BAB-9). The bridge marches one ray per pixel through the box on the same planes, front to back in float, and stops at 0.998 opaque. The style code is generated as WGSL per volume with every field written in, so a field change rebuilds that volume. Ten nodes pass in our reader and in X_ITE: `VolumeData`, `IsoSurfaceVolumeData`, `SegmentedVolumeData`, and the Opacity map, Shaded, ToneMapped, Cartoon, Boundary, Edge and Silhouette styles [C].

| # | X_ITE 16.6.0 behaviour measured or read | What the bridge does | Test |
|---|---|---|---|
| 1 | A default OpacityMap always runs first and turns a voxel (r, g, b, a) into (r, r, r, r) | same, so a red RGBA voxel draws white and a green one draws nothing | `VolumeData` fixture |
| 2 | A volume with no voxels, or one not loaded yet, is a white 1 x 1 x 1 volume that fills the box | same | `VolumeData` fixture, second volume |
| 3 | A user OpacityMap reads its 2D table at (r, r), the diagonal, not at intensity against gradient | same: voxels 0, 85, 170, 255 pick red, green, blue, white | `OpacityMapVolumeStyle` fixture |
| 4 | Shaded lighting defaults to FALSE; the headlight gives 204 face on, 144 at 45 degrees | same | `ShadedVolumeStyle` fixture |
| 5 | ToneMapped: facing the light is the COOL colour, (37, 37, 218) at 45 degrees | same | `ToneMappedVolumeStyle` fixture |
| 6 | Cartoon measures the angle from the eye to the sample, so faces turned to the eye are dropped; HSV mix, red to blue passes through (150, 0, 255) | same | `CartoonVolumeStyle` fixture |
| 7 | IsoSurface draws every sample above the value as an opaque flat grey of the surface value (200 draws 128 at value 0.5) | same; `contourStepSize` left unused (X_ITE tests only the lowest contour) | `IsoSurfaceVolumeData` fixture |
| 8 | A changed 2D transfer-function PixelTexture image is not taken after load | updates | `OpacityMapVolumeStyle` fixture, per-engine check |
| 9 | Faint-alpha stacks come out lighter (8 bit blend per slice): 24 against 10, 28 against 14, 78 against 40 | float accumulation | `VolumeData`, `EdgeEnhancementVolumeStyle`, `BoundaryEnhancementVolumeStyle` fixtures, per-engine values |

Instruments: x3d.loom batch 43 fixtures (151 assertions over ten nodes) run in our reader and in X_ITE 16.6.0 (WebGL2, Chromium 153.0.8010.12, SwiftShader), Babylon 9.32.0 WebGPU, 320 x 240; X_ITE behaviour read in its `VolumeRenderingComponent`. **[C]** for every row. The cause of row 9 (8 bit rounding on a white background) is **[S]**; the difference itself was measured. Gaps logged: no fog or clip planes, no per-pixel cutting by piercing shapes, no light cones, `shadows` and `phaseFunction` unused (X_ITE ignores them too), plane count fixed at 400. The same PR fixes the solid FALSE back-face gap recorded in section 13 (N-BAB-26): solid TRUE now culls, solid FALSE lights the back side, and a sweep of the 118 scene fixtures found and fixed two knock-ons [C, `_backface` fixtures]. `BlendedVolumeStyle`, `ComposedVolumeStyle` and `ProjectionVolumeStyle` are the next batch.

## 5. The playbook, merged: 50 traps, ranked

The playbook is four files in `x3d.loom@162ab18:x3d.webgpu/`, each a new file that leaves the earlier ones unchanged: `BABYLON-BRIDGE-PLAYBOOK.md` v1 (7 Nov, 11,796 B: laws, ports #1 to #3, adapter pitfall, publishing), `-v2.md` (8 Nov, 9,044 B: a trap table by area from ports #3 to #9 and the Odyssey port), `-v3.md` (7,005 B: Demiurge and Dynasty) and `-v4.md` (1,304 B: the Hall, eight lines) [C, `wc -c`]. Merged and de-duplicated here: **50 traps (T01 to T44 in the table, T45 to T50 beside it); 13 first appear in v1, 19 in v2, 13 in v3, 5 in v4** [C, counted from the table below by script].

Ranking rubric (ours, **[S]**: no incidence data exists): tier **A** is silent on the default path or hit by two or more ports (the picture is plausible, wrong and unlogged); **B** is silent but scene-specific; **C** is loud (an error, a blank page) or tooling; **W** is a WGSL porting rule. Inside a tier: ports hit, then how silent. When a port "looks wrong", read tier A first: the playbook's advice is to find the symptom before touching lighting, because most of the cost was convention, not physics. The "check" column is a grep I ran at `162ab18` over `demo/src/` (a file present means the fix exists in some page, not in every body); "read" means no check was made.

| ID | tier | from; port | symptom and cause | fix | check |
|---|---|---|---|---|---|
| T01 | A | v1, v2; Brain, Odyssey | PBR looks cool and inside-out; X3D counter-clockwise is the front face | `sideOrientation = CounterClockWise`; `null` on MeshBuilder primitives, which the flag turns inside out | grep: 3 files |
| T02 | A | v1, v2; Brain | PhysicalMaterial colours are already linear: converting again made cortex too dark | assign `baseColor` to `albedoColor` as authored; v1 and v2 say "convert authored sRGB" (conflict C1) | `body.js` line 303 |
| T03 | A | v2; Odyssey | scene too bright, 8-light cap hit: 59 of 60 lights have `global=false`, Babylon lights everything | `includedOnlyMeshes` = meshes under the light's parent group, applied after the world builds and on change; a shape sees at most 6 | grep: odyssey-ext.js |
| T04 | A | v2; Odyssey | a USE is a placement: state keyed by node id is overwritten by the second placement (74 lights for 62 placements) | state per Babylon object; the shared body still keys `rec` by id (assessment P1, open at 6b3cb76) | assessment; not re-checked |
| T05 | A | v2; Odyssey | corridor floods pink: Babylon adds an emissive texture to the emissive colour, X3D multiplies | texture in `diffuseTexture`, colour in `emissiveColor` | read |
| T06 | A | v2, bridge README; Manifold | `events.emit` queued ROUTEs but never ran `addFieldCallback`: nothing animates; two wrappers fire callbacks twice | run callbacks from one emit hook (`R.hooks.cb`) | README findings |
| T07 | A | v2; Manifold | first frames washed out: final image processing converts linear to gamma, display-referred shaders already did | `imageProcessing.fromLinearSpace = false` | grep: body-manifold.js |
| T08 | A | v1, v2, v3; Brain, Dynasty | glow sprites draw over glass: `alphaIndex` defaults to MAX_VALUE | explicit `alphaIndex` on every non-glass mesh; blended shapes in document order | grep: 7 files |
| T09 | A | v4; Hall | a textured unlit shape ignores its PNG alpha (glows, shafts, halos drawn opaque) | `hasAlpha`, alpha from diffuse, sorted blend, depth write off; JPEGs stay opaque | grep: 4 files |
| T10 | A | v3; Dynasty | additive glow layers draw black glass: `BlendMode` (ONE, ONE) ignored | (ONE, ONE) to `ALPHA_ONEONE`, (SRC_ALPHA, ONE) to `ALPHA_ADD`, else default plus a note; re-apply on assignment | grep: 2 files |
| T11 | A | v3; Demiurge | a looping `TimeSensor` with `startTime 0` runs from 1970: `elapsedTime` 1.8e9, a shader loses every digit | start it when the world activates; X_ITE counts from activation | read |
| T12 | A | v2, v4; Odyssey, Hall | seeking a TimeSensor twice at one timestamp lands once; a paused film stays frozen | `events.begin(ts + 1e-6)`; disable, wait two frames, set start, resume and pause times, enable; clear pause on disable | grep: odyssey (2 files) |
| T13 | A | v3; Demiurge | near plane 0.3 cuts the Earth and village out (1 m is 0.0004 units) | honour `nearDistance` and `farDistance`; re-apply when they change | grep: body-dm.js |
| T14 | A | v3; Demiurge, Dynasty | X_ITE's logarithmic depth has no Babylon counterpart; shaders that wrote `gl_FragDepth` mis-sort | `engine.useReverseDepthBuffer = true` (`?rz=0` off); write plain projected depth `c.z / c.w` | grep: 4 boot files |
| T15 | B | v1, v2 | billboards face the wrong way in a right-handed scene | orient each frame in the body (+Z at the eye) | `body.js` 78 to 95 |
| T16 | B | v1, v2 | unlit text and lines draw black | `emissiveColor`; a line set with no `Color` uses the Material's | grep: 6 files |
| T17 | B | v1 | a clip plane clips the whole scene | `material.clipPlane`, not `scene.clipPlane` | grep: body-cam.js |
| T18 | B | v1 | torso failed to load: `Matrix.FromQuaternion` on a Transform with `center` or `scaleOrientation` | `toRotationMatrix`; shear is dropped (assessment P1) | grep: body.js |
| T19 | B | v1 | viewpoint inside a rotated Transform; zoom divides by zero at the rotation centre | apply the parent rotation; clamp distance | read |
| T20 | B | v2 | coplanar textured glow panel and floor z-fight | `zOffset 4`, `zOffsetUnits 8` on the panel | grep: 2 files |
| T21 | B | v2 | metals dark and speckled; packed maps wrong | `enableSpecularAntiAliasing`, an environment floor; roughness G, metallic B, data textures `gammaSpace=false`, `invertNormalY=true` | grep: 3 files |
| T22 | B | v2 | cube map with `noMipmap = true` raises WebGPU mip errors | `noMipmap = false` | read |
| T23 | B | v2 | a mesh whose first `setVerticesData` call is a custom attribute drops it | set the position first | read |
| T24 | B | v2 | blended glow sorts differently from X_ITE | feed `bboxCenter` to `mesh.setBoundingInfo` | grep: body-gob.js |
| T25 | B | v2 | `geometryData` and `babylonGeometry` shared one cache key: the second rebuild drew 0 vertices | suffix the key with the colour variant; dispose both | read |
| T26 | B | v2 | `Background` sky gradient drawn sRGB-encoded by Babylon, almost black by headless X_ITE | logged as a gap, not tuned | GAPS.md |
| T27 | B | v3 | two views on two engines: the shim holds one browser and one body | second custom element `x3d-babylon` chosen when an adapter answers; the other view stays on X_ITE | grep: boot-dl.js |
| T28 | B | v3 | bare `Appearance` with no Material and a per-face `Color` drew black on black | route through an unlit vertex-colour program, opaque | read |
| T29 | B | v3 | `Inline`, `ProximitySensor`, `IMPORT`/`EXPORT` have no Babylon counterpart | fetch and adopt on `load`; box-test the eye in the sensor frame; answer `getImportedNode` from `getNamedNode` | grep: 3 files |
| T30 | B | v3 | `alphaMode AUTO` and a proxy sphere paint glow over an opaque core | AUTO is opaque for programs that write alpha 1; write `fragDepth`, depth write off on the blended material | grep: wgsl-dl.js |
| T31 | B | v3 | a page that probes the engine (`getComponent`, `createNode("BlendMode")`) picks its path from your shim's answer | list the probes; test both answers and every look | read |
| T32 | B | v3 | a textured UnlitMaterial at full opacity: 14 portrait plates showed at once | carry the material, `opacity = 1 - transparency`, re-apply on change | read |
| T33 | B | v4 | `Extrusion`, `Disk2D`, `Rectangle2D` have no Babylon node | convert to IndexedFaceSet at parse time; update buffers in place for animation | hall/reader-ext-hl.js |
| T34 | C | v1 | `BlendMode` and `DepthMode` are X_ITE-only; the 4.0 XSD rejects them, and `ParticleSystem` with physics | say so in the validation line; 4 names sit outside the 4.0 list | NODES.json meta |
| T35 | C | v2 | loading Babylon replaces `window.X3D`; the X_ITE engine stops | restore it after the bundle loads; engines switch both ways | grep: 6 files |
| T36 | C | v2, v3 | WGSL compile errors arrive as console warnings; a `*/` inside a block comment of a concatenated bundle ends it | the harness listens to warnings; `node --check` the bundle (only build-hall.py does) | grep: 1 of 13 |
| T37 | C | v2 | first frame shows half-built pipelines; a slowed rAF ages time-driven code | `scene.whenReadyAsync()`; pass `maxDt` | grep: 3 files |
| T38 | C | v4 | more than 16 vertex outputs: each shadow-mapped light costs two | count shadow lights per mesh before choosing cascades | read |
| T39 | C | v4, v2 | brightness gap blamed on the light unit: `lightScale 0.75` moved luma 4 percent | measure the unit first; glTF punctual units kept a hall within 1 grey level | Hall RECEIPT |
| T40 | W | v1, v2, v4 | no `gl_PointSize`, no wide lines | camera-facing quads with a `corner` attribute (`corner * (s / viewport.zw) * w`); ribbons for lines | grep: wgsl-point.js |
| T41 | W | v2, v3 | `pow(x, 2.)` of a negative; `smoothstep(a, b, x)` with a > b; `select(false, true, c)` order | `x * x`; write the clamp formula; re-derive every `select()` | read |
| T42 | W | v3 | no `inverse()`, no matrix/scalar divide, no implicit int-float mix, no `uniform float u[32]` | cofactor `inv3`; `f32(i)`; eight `vec4f` `u0..u7` and `uAt(i)` | read |
| T43 | W | v3 | window y runs down: `cross(dFdx, dFdy)` flips, dither mirrors; derivatives must precede `discard` | `cross(dpdy, dpdx)`; accept the mirrored pattern; compute `fwidth` first | Demiurge G8 |
| T44 | W | v3 | look constants differ per theme, code does not: hash keys need one port per theme | key by ComposedShader DEF; read `const` lines from the scene's GLSL | `DL_BY_DEF` |

Six more traps live in other sections and keep their numbers here:

| ID | tier | from | trap and where it lives |
|---|---|---|---|
| T45 | B | v2 | 263k-number MF arrays through the SAI: non-copying `fieldView`, typed `MFVec4f` and `MFFloat` parse (Manifold) |
| T46 | C | v1 | no adapter on some Windows laptops: section 10 |
| T47 | C | v1 | edited GLSL falls back to no shader (X3D 31.2.2): section 9 |
| T48 | C | v1 | the tone-map choice changes the picture: section 8 |
| T49 | C | v4 | `loadURL` takes an MFString; fixed page chrome over a canvas needs a `ResizeObserver` (Hall) |
| T50 | C | v2, v3 | a hidden canvas keeps rendering (skip when `getClientRects().length === 0`); a headless click on an auto-hidden control needs a mouse move first |

Carried, in no playbook version [L unless marked]: Babylon mixes fog after tone mapping, X_ITE in linear, so pass a display-space fog colour [S]; `VertexData.ComputeNormals` assumes left-handed, so pass `{ useRightHandedSystem: true }` (grep: 7 files); PCF shadows drew nothing and `usePoissonSampling` did (`drift/drift-ext.js` line 319); GL depth bias is twice too strong in WebGPU (`z -= (k / 2) * w`); a flat varying comes from the first vertex in WebGPU, the last in GL (Gobbler 3 gap G7).

## 6. The parity method: PSNR against X_ITE on a software GPU

The measurement is a witness, not a score: same file, two renderers, a number that says where to look.

1. Same scene file (record its sha256), Viewpoint, canvas size and Switch settings, in X_ITE (name the patch: 16.4.3, 16.5.1 or 16.6.0 appear in the receipts) and in the bridge page (`Babylon 9.32.0`), "As authored" only.
2. Headless Chromium 153 on SwiftShader cannot present a WebGPU swap chain (every pipeline reports "Instance dropped"). `stub-swapchain.py` replaces `canvas.getContext('webgpu')` with an object whose `getCurrentTexture()` returns an offscreen texture; the page reads it back (`__demo.capture`, `__snap`).
3. Slow `requestAnimationFrame` (600 ms splat viewers, 1.2 s brain) or frames pile up and the read-back waits over ten minutes.
4. Pin time: seek both renderers (Odyssey), use the page's freeze, or compare the scene hash instead of pixels for scenes that grow (`scenes.sha256` for the HEP events).
5. PSNR on 8-bit RGB, `10 * log10(255^2 / MSE)`, with the mean absolute difference; state whole frame, crop or mask. Layers that differ by construction (tracts, slice planes, labels) score low: say so, do not tune to the metric.
6. Write `RECEIPT.md` (rig, versions, scripts) and `GAPS.md` (each line graded). The bridge's visual rig adds bounds to a test spec (`iou` silhouette overlap, `mad`, `fg` mean colour of drawn pixels, `cover`, `bbox`, `count`); a shot where neither engine drew anything fails unless `empty` is true.

A worked number (D-BAB-4, re-run): the two committed facade frames, 960 x 540, X_ITE 16.4.3 against our own-runtime page.

| window | PSNR | MAE of 255 |
|---|---|---|
| whole frame | 39.30 dB | 0.84 |
| bottom 40 rows cropped (the receipt's caption crop) | 41.90 dB | 0.79 |

The receipt's 41.9 dB and 0.79 are re-derived; the same frames differ by 2.6 dB between the whole frame and one crop. A PSNR without its window is not comparable with another PSNR.

```text
  dB   what the rows are                                   rows (reference X_ITE patch)
  50 +  shaders ported term for term, no lens or bloom     Pantheon splats 50.17, 51.01 (16.4.3)
  49 +                                                      Manifold 49.34, 48.47 (16.5.1)
  42 +  one generated view                                  facade 41.90, re-derived (16.4.3)
  35 +  lit meshes, glass, layers                           brain 33.03 all; 35.11 glass to
     |                                                      30.26 torso (16.6.0)
  30 +  "same picture, small shading differences"           Dynasty 29.0 to 37.8 (16.5.1)
  25 +  "same scene, detail differs"                        KANSEI 24.36 to 32.46; Chirp 24.87
     |                                                      to 25.36; Odyssey 25.5 to 30.7
  21 +  thin things: ribbons, labels, slice planes          brain tracts 22.51, labels 21.53
  17 +  method: clocks, pose, background                    Hall 17.5 to 25.3; Gobbler 3 14.60
     |                                                      to 19.66; Cloud 19.24 whole frame
   7 +  "means little" in the receipt's own words           Demiurge 7.18 to 13.26 (16.5.1)
```

Rows are read from `runs/webgpu-*/RECEIPT.md` and `GAPS.md` at `x3d.loom@162ab18` **[L]**; rig in each: Chromium 153.0.8010.12, SwiftShader, stubbed swap chain (Odyssey names "headless Chromium" without a version). The tiers are ours; the receipts say only that 30 dB or more is "the same picture with small shading and edge differences" and 24 to 29 dB the same scene differing in detail.

**What the ladder cannot say:**

| it cannot say | evidence | grade |
|---|---|---|
| that a bright number is a faithful picture | `Polypoint2D`: iou 1, 40.03 dB, drawn pixels' mean colour [202, 162, 41] in ours and [64, 51, 13] in X_ITE: a few small squares on black move PSNR little (`BATCH-26.md`, X_ITE 16.6.0, 320 x 240) | C (read) |
| that a low number is a wrong picture | `ExplosionEmitter`: iou 0.05, 11.73 dB, verdict PASS: particle age differs on a CPU raster, so extent is compared with a wide bound (`BATCH-23.md`) | C (read) |
| that the window is the same | Cloud 19.24 dB whole frame, 21.01 with background excluded; facade 39.30 against 41.90 | C |
| that the clocks agree | Gobbler 3 captured the engines at different instants; its gap G4 says PSNR "is not a parity figure"; Demiurge G4: 7 to 13 dB "means little"; Dynasty night Crown 18.8 and Wide 22.1 "probably pose drift" [S]. Odyssey and KANSEI pin time (seek; sim hash equal in 6 of 6 views); the Hall's receipt says its film clock agrees; for the other receipts the clock is not stated | C (read) |
| that it holds on a real GPU or within a tolerance | all rows are SwiftShader; the spec's profiles (`parity/look` 4/255 and luma 0.01; SSIM 0.95 and PSNR 30 for the benchmark) are proposals and calibration (X_ITE against itself on two GPUs, TBD-13) is not done | C |

## 7. The ports and what each taught

| # | port, PR (merge) | headline parity (reference, size) | what it taught |
|---|---|---|---|
| 1 | Pantheon splats, #11 (7 Nov), own runtime | 50.17, 51.01 dB (16.4.3, 960 x 540) | the stub swap chain; GPU bitonic sort; X_ITE's splat shader ported line by line |
| 2 | HEP events and facade, #12 (7 Nov) | facade 41.9 dB (16.4.3); events by scene hash | event scenes grow: compare hashes; 140,000 splats pad to 262,144 (171 dispatches) |
| 3 | Neural Canvas, #13 (7 Nov) | 33.03 all; 21.53 to 35.11 per layer (16.6.0, 640 x 360) | winding, `alphaIndex`, billboards, clip planes, 4 shader keys |
| 4 | adapter retry, #14 (7 Nov) | none | harmless, not the cure for the blocklist (section 10) |
| 5 | KANSEI, #17 (7 Nov) | 24.36 to 32.46 masked (16.5.1, 640 x 360) | fog order, right-handed normals, shadows; keep the simulation out of the renderer |
| 6 | Manifold, #19 (7 Nov) | 49.34, 48.47 (16.5.1, 640 x 360) | emit callbacks, `fromLinearSpace`, attribute order, big arrays; 7 keys |
| 7 | Chirp and Cloud, #21 (7 Nov) | 24.87 to 25.36; 19.24 to 19.40 whole, 21.01 to 24.96 masked (16.5.1, 1100 x 700) | unlit HDR vertex colour, the geometry cache key, `Background` sky; re-run earlier pages after editing shared files |
| 8 | Gobbler 3, #22 (7 Nov) | 14.60 to 19.66 (16.5.1, 640 x 360) | depth bias, flat varyings, point quads; clocks not locked; 6 keys |
| 9 | Material Odyssey, #23 (8 Nov) | 25.5 to 30.7 as authored; 18.4 to 28.2 look on (16.4.3, 1280 x 536) | light scope, USE audit, emissive texture, seeking; no new node type needed |
| 10 | Gobbler Demiurge, #24 (8 Nov) | 7.18 to 13.26 (16.5.1, 960 x 540) | `startTime 0`, pause, near and far, reversed depth; 4 keys |
| 11 | Dynasty Loom, #25; Library Hall, #27 (8 Nov) | 29.0 to 37.8; 17.5 to 25.3 (16.5.1) | two engines on one page, `BlendMode`, `IMPORT`/`EXPORT`; the Hall has no shader ("the first all-standard-node page", v4) |

[L] for every parity cell (read in the named receipts, not re-run except the facade).

## 8. A look may add, never assert; a fallback must say so

Both rules are [Loom laws](02-loom-laws.md) (39 and 40), kept on this track as code habits.

| rule | mechanism and evidence | grade |
|---|---|---|
| a look decorates and can be switched off | Odyssey: switch `OD.on`, Look button (key L), `?look=0`; Chirp and Cloud: a pill and `?look=0`. Recipe: generated cube environment, `DefaultRenderingPipeline` (MSAA 4, bloom, grain, vignette, neutral tone map), camera dust, up to three spot shadow generators. Odyssey look off 25.5 to 30.7 dB, on 18.4 to 28.2 dB (16.4.3): the look adds reflections, bloom, shadows, grain and dust by design and is "not a target" | L (playbook v2 section 2, receipt) |
| a default can assert | Collider: Neutral tone map at exposure 1.65 turned towers pink-white (13.9% near-white crown pixels against 1.2% for per-channel exp at 1.35), found by counting pixels on a purpose-built region, not by PSNR | L (playbook v1 4.2) |
| a miss, a gap or a software adapter must show | a hash miss draws the Material; 6 of 13 builders refuse an unported shader; `scene.getFidelityReport()` keeps recognition, known gaps and unverified fidelity apart ("no report is a conformance certificate", `bridge/README.md`); `adapter.js` and `timing.js` name the adapter and label SwiftShader, WARP and llvmpipe "these numbers do not count" | C (read, grep) |
| unknown nodes should not vanish silently | the reader tallies unknown tags; on screen only in the manifold and Gobbler 3 pages, a console line elsewhere (2 of 7 pages at 8 Nov) | S (primer, carried) |

## 9. Shader porting: hash-keyed GLSL to hand-written WGSL

```text
  <ComposedShader DEF=..>  ShaderPart VERTEX url="data:..,GLSL"   ShaderPart FRAGMENT url=..
        |  decode the data URL (base64 or percent), keep the text after the first comma
        v
  collapse each run of whitespace to one space, trim:     s.replace(/\s+/g, ' ').trim()
        v
  FNV-1a, 32-bit:  h = 0x811c9dc5;  per UTF-16 unit  h ^= c;  h = imul(h, 0x01000193) >>> 0
        v
  key = hex8(vertex) + '-' + hex8(fragment)          e.g.  1bc84a9f-b6fcc411  (collision flash)
        v
  table lookup:  hit  -> hand-ported WGSL with its uniform names
                 miss -> Material fallback and a notice on screen (law 40); never a guess
```

Worked example, the five Collider programs (D-BAB-3: an independent Python port of the same hash over `demo/collider.x3d`, equal to the `key:` fields in `collider-v2.html`) **[C]**:

| DEF | role | key (vertex-fragment) |
|---|---|---|
| `trkShader2` | tracks | `da010848-2732de59` |
| `twrShader2` | calorimeter towers | `e899d3ba-71ea799c` |
| `shellShader2` | detector shells | `2318d20e-451c1b62` |
| `flashShader2` | collision flash | `1bc84a9f-b6fcc411` |
| `hazeShader2` | backdrop haze | `07e052cf-7ecaed2f` |

Extra spaces inside the flash fragment leave the key unchanged; changing one constant (`12.0` to `12.5`) moves only the fragment half, to `1bc84a9f-bd1839be`, and the program misses. That is the feature: the page cannot claim to render code it did not run.

Counts at `162ab18` [C, grep `'[0-9a-f]{8}-[0-9a-f]{8}'` over 9 files of `demo/src`]: 26 distinct hash keys (Collider 5, brain 4, manifold 7, Gobbler 3 6, Demiurge 4); the primer's 22 on 8 Nov is 5 + 4 + 7 + 6, before Demiurge. Dynasty keys 6 programs (`sky`, `ring`, `seedcore`, `seedglow`, `fiber`, `shell`) by ComposedShader DEF, because its two looks differ only in `const` look constants read out of the scene's own GLSL (`dynasty/wgsl-dl.js`, `DL_BY_DEF`). The Hall's builder refuses any ComposedShader.

The WGSL rules that cost time are T40 to T44 in section 5. Review rule from the Gobbler port: one author writes the WGSL term for term and a second re-derives every constant, operator and `select()` argument order; that review found one real defect [L, carried]. WGSL compile errors surface as console warnings, so a harness must listen to them (T36).

## 10. The adapter and blocklist trap

| observation | detail | source | grade |
|---|---|---|---|
| symptom | "requestAdapter() returned no adapter" or "WebGPU not available" on one Windows laptop (Intel gen-9 integrated GPU, UHD 620 class, Chrome 156); plain and `high-performance` requests both null | playbook v1 section 4.1 | L (read; no Windows here) |
| cause | `chrome://gpu` Dawn Info lists the adapter only on the D3D11 backend, blocklisted ("D3D11 backend not fully implemented", crbug.com/41479539); the only other adapter, the CPU Basic Render Driver, is blocklisted too | same; `x3d.demo@d10b457:docs/index.html` repeats it | L |
| a wrong theory | "the viewer asked only for `high-performance`": `shared/adapter.js` now retries plain, caller options, low-power, fallback adapter and records the winner in `window.__adapterVia`; harmless, not the cure | playbook v1; `adapter.js` | C (read) |
| the fix that worked | `chrome://flags/#enable-unsafe-webgpu` set to Enabled, relaunch. The demo page warns it "switches off Chrome's safety check for WebGPU on that GPU, so use it for these demos only". A Mac with a normal Metal adapter was fine; Edge is another route | playbook v1; `docs/index.html` | L |
| a source conflict | `STATE.md` 4.2 records a probe on this hardware (7 Nov) that got a hardware adapter without the flag and says Chromium's default blocklist patterns hold only Qualcomm and `*:*:PowerVR*25.1*`; the playbook says the same hardware later returned null and the browser state had differed. Cause unknown | `STATE.md`, playbook v1 | L; neither re-run |

A page must show the tip when `requestAdapter()` is null, and which adapter and request answered (law 40). Diagnose in order: a probe page over http or `file://`, never `about:blank` where `navigator.gpu` is absent (`bench/webgpu-probe.html`); `chrome://gpu`, Dawn Info, "Blocklisted"; the flag, knowing what it disables; another browser or machine. In this sandbox the only adapter is SwiftShader's fallback, with `--enable-unsafe-webgpu` [L, `STATE.md` section 5].

## 11. Porting a new demo: sixteen steps, append-only

`x3d.demo` keeps every version: `docs/versions/vN/index.html` is a frozen snapshot, `docs/index.html` the newest copy, demos live at `docs/demos/<name>/vN/`; "nothing is overwritten; a change makes a new version" (`x3d.demo@d10b457:CHANGELOG.md`). Of the 13 `build*.py`, 5 enforce a new output folder in code (`grep -l -i "refusing to overwrite\|never overwrite\|must be new" build*.py`: demiurge, dynasty, hall, manifold, odyssey), 6 refuse an unported shader (`grep -l "no WGSL port\|carries a ComposedShader" build*.py`) and 1 runs `node --check` on the bundle (hall) [C].

| # | step |
|---|---|
| 1 | validate the scene, record its sha256; the file is the master (law 38) |
| 2 | census its node names against `NODES.json`; list every non-`base` node and every ComposedShader |
| 3 | copy the carrier: `reader.js`, `body.js`, `body-cam.js`, `sai.js`, `wgsl.js`, `boot.js`, `adapter.js`, `timing.js`; add `kit.js`, `nodes/*.js`, `body-br.js` only if the scene needs kit nodes (builders omit the kit by default) |
| 4 | pin Babylon to one exact version from a CDN with a subresource-integrity hash (9.32.0 so far) |
| 5 | hash every shader, write the ports, make the builder refuse an unported one |
| 6 | run the demo's own `app.js` unchanged against the SAI shim; a patch is a finding |
| 7 | match X_ITE as authored first; add looks after, switchable, with `?look=0` |
| 8 | read `global` on every light and scope the non-global ones; audit USE for state keyed by node id; check the light unit before blaming it (T03, T04, T39) |
| 9 | put fallbacks on screen: shader miss, unknown nodes, adapter name, the flag tip |
| 10 | build into a **new** folder; `node --check` the bundle |
| 11 | measure: stub swap chain, slowed rAF, pinned time, As authored, window named, per layer |
| 12 | write `runs/<name>-<date>/RECEIPT.md` (rig, versions, scripts) and `GAPS.md` (each line graded); list audio, Timing and a real-GPU pass as open |
| 13 | leak sweep on the served bytes: model and vendor names, cloud ids, cost figures, private links, unpublished material, keys, embedded metadata |
| 14 | publish to `docs/demos/<name>/v1/` (vN+1 for a revision), add `docs/versions/vN`, copy it to `docs/index.html`, add a CHANGELOG line and a `SOURCES.md` row with byte hashes |
| 15 | say on the page what it is: renderer and version, "correctness evidence, no timings", the flag tip |
| 16 | if you edited a shared file, re-run the earlier pages' smoke tests; open a PR; verify the live URL after Pages builds |

## 12. No speed claim exists, and what one would take

- No receipt holds a WebGPU or Babylon timing from a real GPU: `bench/receipts/` has one file, the G1 adapter probe; the timing test I read (`runs/webgpu-drift-20261107`) feeds synthetic timestamps to the panel [C, `ls`, receipt read].
- The Timing panel is opt-in: 2 s warm-up, 20 s window, p50, p95, p99, adapter and canvas recorded, software adapters labelled; 7 of 13 builders include it [C, `shared/timing.js`, grep].
- The decision rule (`BENCHMARK.md` section 9, **[L]**): Go only if parity holds (SSIM 0.95, PSNR 30), p95 is at most 0.70 of arm A in all 3 runs, at most 0.85 of the engine's own WebGL2 arm, with no 10% regression; otherwise No-go or Inconclusive. Gate G0 (consent to use a named real GPU for metrics) is open.
- The only real-GPU number in the sources is an X_ITE frame rate on one machine, vsync-capped: a ceiling check, not a comparison ([06](06-xite-the-oracle.md), `STATE.md`) [L, carried].

A timing claim needs a named GPU and driver, vsync off, three runs and their spread, the same scene on the X_ITE arm and on the engine's WebGL2 arm, and a receipt that fits `bench/receipt.schema.json`. Until then this chapter says nothing about "faster", "lighter" or "smoother", and neither should a page.
## 13. NURBS in the bridge: shared maths, X_ITE's tessellation rule, and where X_ITE is wrong

Batch 44 bridged ten of the 13 NURBS nodes: NurbsCurve, NurbsCurve2D, ContourPolyline2D, Contour2D, NurbsPositionInterpolator, NurbsOrientationInterpolator, NurbsSurfaceInterpolator, NurbsPatchSurface, NurbsSet and NurbsSwungSurface. NurbsSweptSurface, NurbsTextureCoordinate and NurbsTrimmedSurface are open. Read at `x3d.loom@4887a98` (the batch-44 pull request branch, not yet on main when this section was written); reference engine `X_ITE 16.6.0`; rig for every number in this section: `Chromium 153.0.8010.12 (Chrome for Testing), headless, SwiftShader (CPU), Babylon 9.32.0 (WebGPU), Playwright 1.62.1`. The explanation for a reader new to NURBS is `x3d.webgpu/bridge/WHY-nurbs-batch.md`; the findings file is `x3d.webgpu/bridge/knowledge/NURBS-FINDINGS.md`.

```text
 control points + order + knots + weights           compared with X_ITE through its own API
        |                                           (getVertices, tessellate, SAI events)
        v
  BR.nurbs (src/nurbs.js)  --> NurbsCurve ............ line strip, point list
   knots, span, basisDers      NurbsCurve2D, ContourPolyline2D, Contour2D ... point list
   curve, surface, mesh        Position, Orientation, SurfaceInterpolator ... events
   extrude                     NurbsPatchSurface ..... triangles, uv, normals
                               NurbsSet .............. tessellationScale -> triangle counts
                               NurbsSwungSurface ..... triangles via the Extrusion frame walk
```

### 13.1 What was built and why it is one library

| piece | what it does | grade | instrument |
|---|---|---|---|
| `src/nurbs.js` (`BR.nurbs`) | knot validity and fallbacks, span search (Piegl and Tiller A2.1), basis derivatives (A2.3), rational curve and surface, analytic surface normal, tessellation rule, swung-surface extrusion | C | `x3d.loom@4887a98`, read and run |
| `spec.refs` in the kit | node fields (a curve's `controlPoint` Coordinate) that a node's cached geometry depends on; both `geometryChanged` wrappers in `body-br.js` read them, so a moved control point redraws the curve | C | `x3d.loom@4887a98:x3d.webgpu/bridge/src/body-br.js` |
| `xsdAllow` fix | a spec naming several nodes added only the first to the XSD copy (after the first insert the anchor text no longer matched) | C | `driver.py` before and after, `x3d.loom@4887a98` |
| 10 fixtures and specs | each node passes its spec in our reader and in X_ITE; XSD checked with `xmllint` | C | `driver.py batch -n 10 --close`, rig above |

The reason for one library: ten nodes need the same four steps (check the knot vector, find the span, evaluate the basis, cut a tessellation count). One implementation means one set of bugs and one place the X_ITE rules live. Unit check (D-BAB-6): a weighted quarter circle has radius error 2.2e-16 [C].

### 13.2 The tessellation rule is X_ITE's on purpose; the maths is the standard's

The standard fixes the curve and leaves the cutting into segments to the browser, so the rule is where two engines drift. The bridge copies X_ITE 16.6.0's count so a model has the same number of segments in both: `t > 0` is `t` segments, `t < 0` is `-t * dimension`, `0` is `2 * dimension`; NurbsSet multiplies by `tessellationScale` and floors. A scale of 0 or below leaves X_ITE with zero segments and NaN vertices; the bridge keeps one cell [C]. Every point list, uv and triangle corner agrees with X_ITE's own vertex arrays in the fixtures (NurbsCurve 32 of 32 steps in each engine, NurbsPatchSurface 35 of 35, NurbsSet 47 of 47 and 46 of 46, NurbsSwungSurface 18 of 18 [C]).

### 13.3 Where X_ITE 16.6.0 is wrong, and where it is only different

| # | behaviour | X_ITE 16.6.0 | bridge | grade |
|---|---|---|---|---|
| 1 | weights | a weighted quarter circle has radius up to 1.24; a rational B-spline has 1.00 | rational, radius 1.00 to 1e-5 | C |
| 2 | interpolators and weights | the weighted midpoint is the unweighted point (0.75, 0.75, 0); the exact point is (0.7071, 0.7071, 0) | exact to 1e-6 | C |
| 3 | invalid curve at an interpolator | throws TypeError (reading `domain` of undefined) when `set_fraction` arrives; the page stops answering | no event, no throw; the step runs in our engine only | C |
| 4 | patch normals | average of face normals inside an 85 degree crease: faceted at low tessellation | analytic dS/du x dS/dv; largest component difference to X_ITE 0.21 at 12 x 12 cells, 0.28 at 8 x 8 | C |
| 5 | closed surface seam | normals leave a seam (its source says "TODO: handle uClosed") | smooth across the seam | C |
| 6 | Extrusion Y axis at an interior spine point | bisector of the two unit vectors | chord spine[i+1] - spine[i-1]; same to 1.2e-7 on an even spine, up to 0.017 apart on a 2.2-unit vase | C on the number, L on the chord reading |
| 7 | surface interpolator normal | unnormalised cross product | unit vector; directions agree to 1e-5 | C |

Rows 1 to 3 are X_ITE defects the bridge does not copy; rows 4, 5 and 7 are differences chosen for quality (standing rule: quality over matching X_ITE, measured and bounded in the spec); row 6 is an open reading of ISO/IEC 19775-1 whose text was not in the repository. Separate from NURBS: a solid FALSE face seen from behind is lit by X_ITE and drawn black by the Babylon body (a two-quad IndexedFaceSet measured 9312 of 19012 pixels drawn), so the affected fixtures keep that view off screen and compare triangles only [C, cause S].

### 13.4 Two schema findings and one test-rig trap

- The 4.0 XSD content model of NurbsSet is a `sequence` of NurbsPatchSurface, NurbsSweptSurface, NurbsSwungSurface, NurbsTrimmedSurface and ProtoInstance, repeated; a set that names only patches does not validate. The spec carries `xsdChoice: ["NurbsSet"]` and the receipt says the XSD was patched [C, `xmllint` against `x3d_mcp` `x3d-4.0.xsd`]. Held for an upstream report, not sent.
- Contour2D, NurbsCurve2D and ContourPolyline2D are children of no scene node in the schema; the specs use `xsdAllow` [C].
- A `Coordinate` inside a NURBS curve or patch without `containerField="controlPoint"` leaves X_ITE with no control points and no error [C].

## 14. A second body: the reader on three.js

The three.js bridge is a scaffold at `x3d.loom@108a282` (`x3d.threejs/bridge/`): a three.js r187 drawing half for the reader this chapter describes, written without copying or editing anything under `x3d.webgpu/`. It is a feasibility proof with a tracker, not a port: 15 of 260 nodes are drawn, 119 need the body, 47 wait on the Babylon batches [C].

```text
   x3d.webgpu/ (read at bundle time, not copied)            x3d.threejs/bridge/
   reader.js  kit.js  nodes/*.js  sai.js   ------------->   tools/bundle.js  --> page
   Body.geometryData (vertex data)         ------------->        + src/body-three.js (THREE)
                                                                 + src/nodes/*.js (empty; registry ready)
   fixtures/*.x3d + *.test.json (events)   ------------->   tools/run-tests.js: ours | X_ITE 16.6.0
                                                             fixtures/ (scene, for the three.js body)
```

### 14.1 Why this is easy, and what is not

| layer | lines | engine mentions | in the scaffold |
|---|---|---|---|
| `reader.js`, `sai.js`, `kit.js` | 388, 319, 648 | 0, 1, 4 | shared |
| 150 node files | 5882 | 19 files | shared; the 19 are the port list |
| Babylon body: `body.js`, `body-cam.js`, `body-br.js` | 518, 234, 919 | 62, 17, 53 | replaced; the three.js core body is 284 lines |

The reader has no engine call, so the hard 80 percent was already engine-neutral. The hooks left to port, counted by regex: 15 `geometry` hooks (all plain vertex data), 61 `build` (43 call only `Body` methods) and 61 `changed` [L]. By group: 79 event and logic nodes cost nothing, about 50 percent map onto three.js objects, about 20 percent are real work (volume, particles, HAnim, text, layering); about 45 to 65 person-days for the 119 open nodes [S]. The full table is `x3d.threejs/bridge/ESTIMATE.md`.

### 14.2 What the first run taught

| # | finding | numbers | grade |
|---|---|---|---|
| 1 | the stock Babylon body binds no Viewpoint at load; `body-br.js` adds it. A body that forgets draws at the default pose | silhouette IoU 0.34 to 0.64 on all 10 fixtures before, 0.99 to 1.00 on 9 after (Material 0.90) | C |
| 2 | three.js lights are physical units: a factor PI makes diffuse x intensity x N.L | the 10 fixtures draw lit colours within a few grey levels of X_ITE (foreground mean) | C |
| 3 | X_ITE evaluates Phong with the reflection vector, three.js with Blinn-Phong; four times the exponent matches the highlight | Sphere 28.22 to 36.98 dB, Box 63.84 to 70.12 dB from that change alone | C |
| 4 | a Transform with `scaleOrientation` keeps its shear as one matrix; the Babylon body decomposes to TRS and drops it | Transform fixture: IoU 1.00, 99 dB, both pictures | C |
| 5 | the same 30 event fixtures run through the three.js bundle | 29 of 30 pass in ours and X_ITE; ColorDamper passes in ours and X_ITE never goes inactive across the hue seam (spec `xiteDisagrees`) | C |

The visual rows: 16 pictures, IoU 0.90 to 1.00, PSNR 32.38 to 70.12 dB over the 11 that differ at all (median 42.95), 5 identical (2 of them empty pictures). Colour management is off and the output is linear, because X_ITE writes authored values as they are; `opts.srgb` is one switch, so the colour-space choice stays the owner's. Instrument: `X_ITE 16.6.0`, `Chromium 153.0.8010.12`, SwiftShader, 320 x 240, three.js r187 [C].

### 14.3 X_ITE lighting is a target, not a rule

Under the owner's 14 Nov ruling the scaffold splits its checks. Events, fields, silhouettes and geometry are hard: X_ITE is the oracle and a disagreement fails the node. Lit colour is a reference: each spec's `compare` bound is measured and receipted, may be widened with a written `lookNote`, and a quality choice (tone map, image-based light, `MeshPhysicalMaterial` extensions) is logged, not failed. None is on by default, because the classic Phong look reproduces and compares cheaply [C, design].

### 14.4 Batch 1: lights, fog, textures, and how X_ITE's formulas were found

Batch 1 (`x3d.loom@95eda37`) added PointLight, SpotLight, Fog, ImageTexture, PixelTexture, TextureTransform and TextureCoordinate with 8 scene fixtures; the tracker now reads drawn 23, reader-checked 29, reader 49, todo 122, upstream 37 [C, `driver.py status`]. three.js has no per-formula switches, so each formula was read in X_ITE 16.6.0's own source and patched into the shader chunks once (`patchThreeShaders`; a replace that matches nothing throws, so a three.js upgrade fails loudly).

| # | what | X_ITE 16.6.0 | three.js r187 as shipped | result against X_ITE | grade |
|---|---|---|---|---|---|
| 1 | light radius | hard edge, flat inside | window `(1 - (d / r)^4)^2` | step at the radius; PointLight 36.3 to 51.2 dB | C |
| 2 | spot cone | full inside beamWidth, linear ramp in the angle | smoothstep over cosines | SpotLight 63.1 dB, 2 pictures | C |
| 3 | fog | distance to the eye; LINEAR `max(range - d, 0) / range`, EXPONENTIAL `exp(-d / max(range - d, 0.001))` | view depth, smoothstep, `exp(-density^2 d^2)` | Fog 46.6 to 53.4 dB, 3 pictures | C |
| 4 | attenuation | `1 / max(a0 + a1 d + a2 d^2, 1)` | `d^-decay`, no constant term | exact for a1 = 0 or a2 = 0 after normalising by a0 (`decay` carries b2 or -b1): 59.2 dB; both terms at once is a fit | C |
| 5 | Sphere, Cylinder, Cone | u = 0 at -Z growing toward -X; planar cap images | u = 0 at -X (Sphere) or +Z (Cylinder); transposed caps | textured primitives 24.0 to 39.6 dB after the turn and the cap rewrite | C |
| 6 | TextureTransform | matrix `-C S R C T` as a column matrix | (no counterpart, the matrix is ours) | 50.1 dB; the Transform order `T C R S -C` gives 21.3 dB; 4 sign variants tried | C |

Rig for every number: Chromium 153.0.8010.12, SwiftShader, 320 x 240, X_ITE 16.6.0 with its notifications off (the "Loading done" toast had drawn 4000 extra pixels into a picture), three.js r187. A first read of the X_ITE source is not proof: the TextureTransform product looked like the Transform order and was 29 dB wrong until the variants were measured. The 30 compared pictures of both batches: IoU 0.90 to 1.00, PSNR 32.4 to 70.1 dB over the 24 that differ (median 50.1), 6 identical [C].

### 14.5 Batch 2: geometry sets, lines, points, Billboard, LOD and ClipPlane

Batch 2 (`x3d.loom@38530ab`) drew 30 more nodes by the tracker's count, from 27 new scene fixtures (the rest ride along: Group, Normal, Collision, StaticGroup); the tracker reads drawn 53, reader-checked 29, reader 46, todo 95, upstream 37 [C, `driver.py status`]. Eleven of the 26 needed no node-specific body code: seven bridge nodes return vertex data from a `geometry()` hook (QuadSet, IndexedQuadSet, TriangleFanSet, IndexedTriangleFanSet, IndexedTriangleStripSet, TriangleSet2D, ArcClose2D) and four return a polyline from `lines()` (LineSet, Arc2D, Circle2D, Polyline2D); the three.js body calls the same hook the Babylon body calls and wraps the arrays in a `BufferGeometry` or `LineSegments` [C, `grep` over `bridge/src/nodes/`]. Of the 31 new pictures, 8 are pixel-identical to X_ITE (TriangleSet, ElevationGrid, IndexedLineSet, LineSet, PointSet, Rectangle2D, Circle2D, Polyline2D at 99 dB), the rest are within IoU 0.91 to 1.00.

What was learned, in the order it happened:

| # | what | result | grade |
|---|---|---|---|
| 1 | A node the reader already defines cannot be defined again: `BR.node` throws "already in the reader" at load and the page then says only `Body is not defined`. The Hall reader already turns Extrusion, Rectangle2D and Disk2D into an IndexedFaceSet at parse time, and defines PointSet; the first Extrusion and PointSet nodes written here killed the bundle. | both removed; Extrusion drew through the existing path | C |
| 2 | ElevationGrid has two valid triangulations; X_ITE cuts each square from its first corner to the far one, `(a, c, d)` and `(a, d, b)`. | 99 dB (identical) against mad 2.7 and 29.1 dB with the other diagonal | C |
| 3 | `Body.geometryData` was lifted verbatim from the Babylon body and carries its omissions: IndexedFaceSet normals are always flat, a Normal node is ignored and colours are always per corner. Extrusion, which the reader turns into an IndexedFaceSet with a creaseAngle, therefore drew faceted. A small `BR.ifsExtras` adds Normal, creaseAngle and per-face colour. | Extrusion IoU 0.98 to 0.99, mad 0.41 to 0.16, foreground mean exact; PSNR moved 39.98 to 38.65 dB (edge pixels) on the first fixture; after its fourth shape became a real star the row reads IoU 0.99, mad 0.20, 37.51 dB; the new IndexedFaceSetNormals fixture is 80.17 dB with all three features lit | C |
| 4 | Billboard, LOD and ClipPlane port as per-frame functions of the camera (`updateView()`); the Babylon maths was engine-neutral and carried over. | Billboard 63.13 dB (identical silhouette), LOD 38.99, 64.48 and 55.16 dB at three distances, ClipPlane 50.24, 55.61 and 49.40 dB | C |
| 5 | Lines and points are `LineSegments` and `Points` with a 1-pixel material in the Material's emissive colour (white with no Material, replaced by Color); X_ITE draws them the same way here. | IndexedLineSet, LineSet and PointSet 99 dB | C |
| 6 | A first IndexedFaceSetNormals fixture used normals pointing up under the headlight, so every face was black in both engines and the "pass" meant nothing (6108 foreground pixels against 9236 once the normals were slanted). | fixture changed | C |

A 35-agent adversarial review of the batch (three reviewers over code, runtime behaviour and claims; every finding tried by a verifier) reported 29 confirmed defects, four rated high: an ElevationGrid Normal read per vertex instead of per square, a render-loop throw when a group is rebuilt in a world with no ClipPlane, change hooks of line and point nodes never called, and children events ignored on Billboard, LOD, Anchor, Collision and StaticGroup; 3 reports were refuted. All were fixed before the merge request, and three of them became unit tests.

Not matched: IndexedTriangleSet and IndexedQuadSet generated normals sit at IoU 0.95 (a dim rim; the cause was not isolated), and PhysicalMaterial is reference-only at IoU 0.91, 25.32 dB, because X_ITE adds an environment glow that three.js has no counterpart for without an environment map. The unit tests (`node --test tools/`, 7 pass) load the body bundle in node with a stub window and check ElevationGrid winding, creaseAngle and TriangleSet counts without a browser.

### 14.6 Batch 3: textures, fog, background and the camera

Batch 3 (`x3d.loom@72a4bca`, the pull request #69 branch, read and run 2026-11-15) drew 13 more nodes from 13 scene fixtures: TwoSidedMaterial, TextureCoordinateGenerator, MultiTexture, TextureProperties, LineProperties, OrthoViewpoint, FillProperties, LocalFog, FogCoordinate, Background, TextureBackground, Polypoint2D and CoordinateDouble. The tracker reads drawn 65, reader-checked 29, reader 45, todo 93, upstream 28 [C, `driver.py status`]. The 13 fixtures add 25 pictures, 10 of them pixel-identical to X_ITE; the other 15 sit at 35.03 to 67.60 dB (median 48.04), silhouette IoU 0.98 to 1.00 [C, `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187, receipts]. All 58 fixtures and 14 unit tests pass.

What was learned, in the order it happened:

| # | what | result | grade |
|---|---|---|---|
| 1 | A texture node's *default* behaviour has to be put in a fixture, not assumed. A TextureProperties with every field at its default (`<TextureProperties/>`, magnification FASTEST) is sampled smoothly by X_ITE; only the NEAREST_PIXEL names give hard texels. The first reading of FASTEST as "nearest" was wrong. | 28.23 dB with FASTEST nearest, 67.60 dB with only NEAREST_PIXEL nearest | C |
| 2 | Without a TextureProperties, X_ITE samples an image under 16 x 16 pixels with hard texels (a 4 x 4 image on a box is a clean checkerboard), and a 16 x 16 or 32 x 32 image smoothly. The exact edge between 4 and 16 was not bisected; 16 is the value the Babylon volume code already carries. | 4 x 4: smooth drawing gave 18.8 dB, nearest gave 64.50 dB; 16 x 16 and 32 x 32 smooth match | C for 4 and 16, L for the rest of the range |
| 3 | X_ITE draws a line `linewidthScaleFactor` pixels wide. The README said X_ITE draws every line one pixel wide; that was true only for lines with no LineProperties. WebGL has no wide lines, so each segment is a quad widened in the vertex shader. | IoU 0.63 with thin lines, 0.98 and 47.71 dB with quads (1051 foreground pixels in X_ITE, 1069 here) | C |
| 4 | A MultiTexture ADD stage is added to the texture colour *before* the light and is not clipped at 1. Three placements were tried against X_ITE: summed on an 8-bit canvas (clipped), added after the light, added before the light unclipped. Region means told them apart where the frame dB barely moved. | ADD cube mean red 181.1, 226.2 and 214.1 against X_ITE 214.9; frame 28.15, 27.84 and 35.03 dB | C |
| 5 | The ground of a Background does not stop at its last `groundAngle`: X_ITE holds the last ground colour out to the horizon. With the ground ending early the horizon was a curved edge below the real one. | level view mad 36.07 (9.75 dB) before, 0.28 (53.61 dB) after; up 48.04 and down 52.79 dB unchanged | C |
| 6 | The six faces of a TextureBackground follow from the viewing direction: for each face the viewer's look direction, right and up give the plane's basis (front looks down -Z; top has its image up toward +Z, bottom toward -Z). Each face got a 3 x 3 PixelTexture with a white bottom-left and a black top-right pixel, so a turned or mirrored image shows. | all six directions pixel-identical on the first run (99 dB) | C |
| 7 | The runner's value converter, shared with the Babylon bridge, has no MFColor: a `set` of a colour list made X_ITE draw black while the reader accepted it, which read as an engine difference. | patched at read time in `tools/run-tests.js` (the Babylon file is untouched); Background recolour step 42.26 dB | C |
| 8 | A Cylinder with `top` or `bottom` FALSE still drew its caps: the TwoSidedMaterial fixture, an open tube seen from above, showed it (no blue inside). | 22.41 dB before the fix, 39.57 after | C |
| 9 | LocalFog needs one fog per mesh and three.js has one per scene: each mesh sets `scene.fog` in `onBeforeRender` to the fog of its nearest enclosing group, and the frame puts the world fog back; fields are read at every draw. A FogCoordinate is a per-vertex attribute and a material patch: `mix(fogColor, colour, 1 - depth)`. | LocalFog 60.30 dB, identical after switching one fog off and narrowing another; FogCoordinate 43.55 dB before and after flipping the depths | C |

Hatching (FillProperties) is a screen-space overlay mesh with a 32 x 32 mask read at the fragment position, one texel per pixel; the 19 masks are cut out of the Babylon body at bundle time, so both bridges carry one table (identical to X_ITE, 99 dB). An OrthoViewpoint swaps in an orthographic camera and takes the headlight with it (60.17 dB, and the perspective view after it 67.15 dB).

Not matched: MultiTexture is composed on a 256 x 256 8-bit canvas (35.03 dB, mean error under 1 grey level on the ADD cube), TwoSidedMaterial has no ambient term (39.57 dB), set_bind between several Backgrounds is not ported, and the camera-space TextureCoordinateGenerator modes redo every vertex on the CPU when the view moves.

### 14.7 Batch 4: cube maps, the pointer layer, ComposedShader, Inline and Text

Batch 4 (`x3d.loom@a6e3d31`, merged as pull request #69 at `7f6496b`, read and run 2026-11-15) drew 16 more nodes from 17 fixtures: ImageCubeMapTexture, ComposedCubeMapTexture, GeneratedCubeMapTexture, ComposedShader, Text and FontStyle, Inline, TouchSensor, PlaneSensor, SphereSensor, CylinderSensor, KeySensor, StringSensor, VisibilitySensor and TransformSensor. The pictures: ImageCubeMapTexture IoU 1.00 at 31.45 and 31.98 dB, ComposedCubeMapTexture 1.00 at 29.12 dB, GeneratedCubeMapTexture 0.94 and 0.98 at 34.03 dB, ComposedShader 1.00 at 40.47 and 39.75 dB, Inline 1.00 at 55.83 and 52.54 dB, Text 0.65 at 19.21 dB [C, `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187, `receipts/`]. What each one taught, in the order it happened:

| # | what | result | grade |
|---|---|---|---|
| 1 | X_ITE draws a cube map only through a TextureCoordinateGenerator: the same box without one is not a mirror. The mode is camera-space reflection, so the cube turns with the camera. The first fixture had no generator and read as a bug in the bridge. | magenta and blue split before the generator was restored; both engines then agree at IoU 1.00 | C |
| 2 | Faces: a cross image and a ComposedCubeMapTexture are drawn unturned on their faces, and a 2:1 panorama has its middle at +Z running toward +X. The first panorama used the longitude `atan2(dx, -dz)` and was a quarter turn off. | `atan2(dx, dz)` matched; IoU 1.00 | C |
| 3 | A GeneratedCubeMapTexture is looked up in the camera frame, not the world frame (no camera-to-world turn), and needs no mipmaps: with mipmaps and linear filtering its borders were blurred against X_ITE's. | main 0.94, turned 0.98; 34.03 dB both | C |
| 4 | X_ITE hands the ShaderPart sources of a ComposedShader to the compiler as written, as GLSL ES 3.00 (the author writes `#version 300 es`) and adds three defines. A CDATA ShaderPart loses its line breaks in X_ITE, so the fixture uses `data:` urls. | the shader draws in both engines at 40.47 dB | C |
| 5 | three.js `RawShaderMaterial` puts its own `#define` lines before the source, and a `#version` line may not follow them. The author's `#version 300 es` line has to come out and `glslVersion` has to carry it. Without that the program does not compile and the Shape falls back to its Material. | with the line left in, the pictures are empty (IoU 0, D-BAB-72) | C |
| 6 | TouchSensor follows 19775-1 20.4.3 as X_ITE does: isOver on entering the shape, the hit outputs while over, isActive TRUE on the press, FALSE on the release, touchTime on a release still over the shape. A press on a drag sensor takes the pointer from the view; a press on a TouchSensor does not. | 34 of 34 steps in both engines | C |
| 7 | X_ITE keeps a VisibilitySensor with `size 0 0 0` active. The spec says it is off; the fixture marks the step `xiteDisagrees` and asserts the specified value on our side. | recorded as a departure, not copied | C |
| 8 | Text is a glyph atlas drawn on one quad per line, laid out with the reader's fields (justify on the ink box, `length`, `maxExtent`, `spacing`) and the Droid Serif, PT Sans and Ubuntu Mono files X_ITE ships. The boxes match X_ITE to the pixel; the letters do not, because the browser's rasteriser and X_ITE's own glyph renderer draw different outlines. | IoU 0.65, 19.21 dB: the lowest number in the table, kept in the table | C |

Inline fetches the file (gunzip when the first two bytes are 1f 8b), parses it with the SAI shim, and builds the roots under its own group. A relative url is read against the page and a url inside the Inline file against the main file (a gap at batch 4; section 14.8 closes the first half of it).

Not matched at batch 4: vertical and right-to-left Text, a texture on a Text, the geometry, tessellation and compute shader stages, ShaderPart urls that need a fetch, and the pick sensors (the shared `BR.pick` walks Babylon meshes and needs an adapter).

### 14.8 Batch 5: CAD, geospatial, and what a review of batch 4 found on paths no picture drives

Batch 5 (`x3d.loom@1192dd4`, pull request #70, read and run 2026-11-15) draws CADAssembly, CADLayer, CADPart and CADFace (a Group, a Group with a Transform's fields, and a face that holds one shape: IoU 0.99, 51.21 to 54.88 dB over four pictures), GeoLocation and GeoTransform (one 64-bit matrix each: the 16 numbers of the row-vector matrix are the 16 numbers of a column-major three.js matrix, and `Matrix4.elements` stays JavaScript doubles until the modelView is made), GeoOrigin, GeoCoordinate, GeoViewpoint, GeoLOD, GeoTouchSensor and GeoProximitySensor, and the ViewpointGroup list. The geographic maths is the Babylon bridge's own (`BR.geo`); only the drawing half was written again. All 95 fixtures pass in both engines [C, `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187].

Then batch 4 was reviewed (H-BAB-32): five lenses (pointer semantics, cube maps and shaders, Inline and Text, input from a hostile file, regressions in shared code), 171 agents, 83 raw findings, two skeptics for each. 69 survived: 10 high, 36 medium, 23 low. Not one of them is a picture difference; every one is on a path no fixture drove, and each is now fixed or recorded:

| # | path | what was wrong | fix |
|---|---|---|---|
| 1 | a second finger or button while a sensor is held | the press cleared the held sensor, so isActive stayed TRUE and a drag never ended | the second pointer is ignored while a sensor holds the first |
| 2 | an Inline that is DEF'd and USE'd | the stale-record guard compared with the last record of the node id, so every copy but the last was dropped | one record per use, a `dead` flag per record |
| 3 | an Inline that includes itself, or a very large file | no guard: a self-including file loaded forever, a gzip bomb was unbounded | depth 8, 512 loads per world, 32 MB (128 MB unzipped), the file's own url compared along the chain |
| 4 | a world replaced while a file is on its way | the parse had already put the new TimeSensors and DEFs on the page | they are taken off again; `clearWorld` also clears cube targets, glyph atlases, the texture cache and the mesh lists |
| 5 | a material changed on a shader mesh, or a TwoSidedMaterial with a cube map or Text | the refresh threw on a `RawShaderMaterial`; the TwoSided early return skipped the cube, fog-coordinate and Text code | shader meshes are skipped in the refresh; the early return is gone |
| 6 | author GLSL and field names | a regular expression that backtracked, a `#version` scan that was quadratic, a field named `__proto__` or `x3d_ProjectionMatrix`, a pair that compiles and does not link | linear scans, reserved names skipped, a throw-away link |
| 7 | picking | ClipPlanes, the near plane and back faces were ignored; hover ran on every move; a normal went into the sensor frame with the inverse instead of the transpose; an Anchor fired on any button and over a nearer sensor | all five corrected; hover only when the world has a pointer sensor |
| 8 | `javascript:` in an Anchor url | the test missed `java<tab>script:` and a leading control character | the shared `Anchor.js` strips what a URL parser strips (one line, also protects the Babylon body) |

The drill after the batch found a weak fixture. Swapping the basis of the GeoViewpoint orientation (`makeBasis(E, U, S)` to `makeBasis(S, U, E)`) still passed all 98 of 98 steps, because the batch-46 fixture sits on a `rotateYUp` origin where the frame at the camera is the identity. The new fixture `GeoViewpointFrame` (latitude 0, longitude 90, no origin, boxes at 55 m north and east) draws IoU 1.00 and 64.48 dB with the right basis and IoU 0 and 18.49 dB with the swapped one [C].

Not done: Layering and Layout, HAnim, particles, Texturing3D, Sound, the pick sensors, TextureProjector. The tracker reads drawn 98, reader-checked 32, reader 41, todo 66, upstream 23.

### 14.9 Batch 6: layers, viewports and the layout engine, drawn as passes

Batch 6 (`x3d.loom@c9b7695`, pull request #72, read and run 2026-11-15) draws LayerSet, Layer, LayoutLayer, Viewport, Layout, LayoutGroup, ScreenGroup and ScreenFontStyle. A LayerSet is not a scene graph feature in three.js; it is a list of render passes. Layer 0 is the world, layer k gets the `Object3D.layers` bit k, a Viewport node in the world gets a bit from 20 up, and `renderAll` makes one `render` call per pass: its own camera (the layer's first Viewpoint, else one at 0 0 10; a LayoutLayer looks through an orthographic one, the canvas 2 units high), its own viewport and scissor rectangle from the `clipBoundary`, and `clearDepth` between two passes so a later layer is in front. The layout engine is X_ITE's `Layout.push` as the Babylon bridge ports it, run once a frame from the parents down. All eight fixtures pass in both engines (Layer 51 of 51 steps ours and 59 of 59 X_ITE, LayerSet 86, Layout 122, LayoutGroup 65, LayoutLayer 60 of 60 against 66, ScreenGroup 75, ScreenFontStyle 27, Viewport 65); the 12 pictures of Layout, LayoutLayer, ScreenGroup and Viewport are IoU 1.00 at 99 dB. The two ours-only gaps are the pick sensors, so the steps of Layer and LayoutLayer that expect a pick are marked X_ITE only.

Four things the pictures did not show and the work did:

| # | what | where it showed | rule |
|---|---|---|---|
| 1 | A colour `scene.background` clears the colour buffer in every `render` call, even with `autoClear` off. The second pass wiped the first. | LayerSet, 4 of 86 steps fail with the red world box missing | give the Background to the first pass only; a layer has none of its own |
| 2 | The headlight is a child of the camera. A pass camera that is not in the scene does not draw its children, so every layer and every world Viewport was unlit, and the world went dark when a layer was drawn first (`order="1 0"`). | the review; no fixture had a headlight and a layer | put every pass camera in the scene; re-parent the headlight to the camera that draws, every pass |
| 3 | The ScreenGroup fixture passed in a chunk of fixtures and failed alone: the layout list lived on the body and survived the world swap, and the layout ran only when a LayerSet existed. | the first full sweep, chunk 7 | clear layers, viewports, passes and layouts in `clearWorld`; run the layout every frame |
| 4 | A press holds the pointer to the layer it started in (X_ITE `Layer.pointer`). Dragged over a shape of a higher layer, the held TouchSensor stayed over and its release fired `touchTime`; with picking through every layer it lost both. | the review; fixture LayerPress, X_ITE 14 of 14 | remember the pass of the press hit and pick only through it until the release |

The review of the batch (H-BAB-32): five lenses (render passes, picking, layout fidelity, lifecycle, regressions), 39 agents, 17 findings, 10 confirmed by two skeptics. Besides rows 2 and 4: world Viewport bits wrapped after eight, so the ninth drew the first's content (and a nested Viewport was masked by its parent); a Viewport used twice kept one of its two uses; a rebuilt LayerSet kept its lights, clip planes and cameras; a LayerSet inside a group is ignored by X_ITE and is now ignored here with a note; a ScreenGroup inside a world Viewport sized itself from the whole canvas. Each is fixed; LayerHeadlight, LayerPress and ViewportMany run the paths. Three findings split the skeptics and are not changed: the Background belongs to the first pass in the order, not to layer 0; the rectangle of a Viewport is fractional where X_ITE floors it to whole pixels; one skeptic saw a USE'd Viewport drawn unclipped in the world pass that the code now handles. A layer has no lights, Background or NavigationInfo of its own, and `activeLayer` is held, not acted on.

The tracker reads drawn 105, reader-checked 33, reader 41, todo 58, upstream 23; 106 fixtures, 106 pass, 130 pictures, IoU 0.65 (Text) to 1.00, median 54.88 dB. Not done: HAnim, particles, Texturing3D, Sound, the pick sensors, TextureProjector.

### 14.10 Batch 7: Texturing3D, Sound placement, particles, TextureProjector and HAnim

Batch 7 (`x3d.loom@9f969d2`, run 2026-11-15) draws the last five families that had no three.js body: six Texturing3D nodes, the three Sound placement nodes, ParticleSystem with its emitters and physics, TextureProjector with its parallel twin, and the six HAnim nodes. The tracker then reads drawn 130, reader-checked 34, reader 41, todo 32, upstream 23; 132 fixtures, 132 pass, rig Chromium 153.0.8010.12 SwiftShader, three.js r187, X_ITE 16.6.0, 320 x 240.

```text
 Texturing3D   ShaderMaterial, GLSL3, sampler3D          (the volume path reuses the shared BR.vol maths)
 Sound         shared Web Audio nodes, placement hooks   (listener and sources moved by the camera each frame)
 Particles     CPU simulation, one THREE.Points per system (emitter shapes are the shared BR.ps)
 Projector     onBeforeCompile on every mesh material, 4 projectors in one set of shared uniforms
 HAnim         CPU skinning, skin = v + sum w (J v - v), the formula X_ITE evaluates
```

Four things the batch taught:

| # | what | where it showed | rule |
|---|---|---|---|
| 1 | X_ITE's matrices are written as row vectors; three.js is column-major. The same list of 16 numbers read the other way is the same transformation, so `fromArray` on the list is the port, and the product order reverses (`inv(t2w) * P * bias` becomes `bias * P * inv(t2w)`). | TextureProjector: first run, picture matches X_ITE at 60.14 dB | do not transpose, reverse the product |
| 2 | Shared uniform state outlives a world swap. A per-mesh scope mask left at 0 by the last frame of the previous world made the next world's projector tint nothing. It passed alone and failed after another fixture. | TextureProjectorParallel after TextureProjector | set shared uniforms to their neutral value every frame, and run fixtures alone and in both orders |
| 3 | A runner edit dropped a closing brace in the events page. Every events-mode fixture then failed with a page error that carried no stack, while the scene fixtures kept passing. | the full sweep after batch 7c was not run until batch 7f | run the whole sweep after any change to `tools/run-tests.js`, and keep the page error's message and stack |
| 4 | X_ITE adds a joint displacer's displacement after the skin matrices, rotated by the joint matrix. A Babylon morph target moves the vertex before skinning, which equals it only for a vertex that follows that one joint. CPU skinning takes X_ITE's order directly and has no four-influence limit. | HAnimDisplacer, bone matrices and 16 skinned positions equal to X_ITE | when the reference has a formula, copy the formula instead of the nearest engine feature |

What the particles measured: a cone emitter with 400 particles and no force matches X_ITE's cloud in extent (bounding box within 5 pixels) and count (2764 against 2626 drawn pixels), IoU 0.57 because the particles are random. X_ITE lifts a force-driven cloud far higher than a ForcePhysicsModel of 0 -2 0 should, and draws a colour ramp without colour keys white; the fixtures avoid both and the gaps are written in them. HAnim and the projector match X_ITE's pictures at 60 dB and its numbers exactly.

### 14.11 Batch 8: picking a million triangles with a bounds tree, and drawing one scene nine ways

Two additions to the three.js body (`x3d.loom` branch `claude/project-thread-1kk4vm`, run 2026-11-15) and the two demos that show them (`x3d.demo` pull request 31: `three-bvh/v1` and `three-style-board/v1`). Rig for every number here: Chromium 153.0.8010.12 headless on SwiftShader, three.js r187, three-mesh-bvh 0.9.18, X_ITE 16.6.0, 320 x 240 for fixtures [C].

```text
 pointer ray --> Pointing.cast(body, ray, list) --> Mesh.raycast  (= acceleratedRaycast)
                                                       |-- first use of a mesh with 2000 or more triangles: build a bounds tree
                                                       |-- the buffer's version changed: rebuild
                                                       '-- skinned (HAnim) geometry: no tree, its positions move every frame
 one X3D file --> one scene graph --> nine renderers, each swapping in its own TSL node material per mesh
```

What the batch taught:

| # | what | where it showed | rule |
|---|---|---|---|
| 1 | A picking test that only checks the answer cannot tell a tree from no tree. The "plain" cast silently used the tree, so the equality check was vacuous. The plain mode now detaches the tree for one cast and restores it at once, and the fixture asserts that no mesh holds a tree during the plain cast. | BvhPicking fixture, an ElevationGrid of 161 x 161 heights | state which path ran, then compare answers [C] |
| 2 | A marker sphere placed at the hit point blocked the next pick, because it was in the list of things the ray may hit. Lines are not in that list, so the crosshair is an IndexedLineSet. | the BVH demo | draw the feedback with geometry the picker ignores [C] |
| 3 | `three.webgpu.js` carries no GLSL shader chunks, so the Body's own `WebGLRenderer` must come from `three.module.js`; both builds share `three.core.js`, so a material made by one is accepted by the other. | the style board, first load | one import map, two entry points, one core [C] |
| 4 | A WebGPU render pass clears the whole target, so one renderer per tile is used, with the same scene graph and a different material set. | the style board | the unit of isolation is the renderer, not the viewport [C] |
| 5 | The tile backgrounds stayed black whatever the clear colour was: the X3D `Background` is drawn by the bridge as a sky dome mesh at render order -1000, and the file's sky colour is nearly black. The board hides that mesh while it draws a tile and lets the tile's own backdrop show. | the Still life scene, `Background skyColor="0.004 0.0032 0.0026"` | when a clear colour does nothing, look for a mesh that covers it [C] |

What the bounds tree measured (125,000 triangles, 23 rays): 33 times faster per pick than the plain raycast, and the same point on 23 of 23 rays [C]. At 1,000,000 triangles the tree builds in about 0.5 s on the first pick and a pick takes about 0.1 ms; a scan of 24,000 rays from the camera takes about 110 ms through the tree. The plain time for that scan is extrapolated from the race (about 4.6 minutes) and labelled as an estimate on the page [S]. No frame rate is claimed: the software rasteriser draws 1,000,000 triangles at 1 to 2 frames per second.

What the style board does and does not show: nine looks (the bridge's own materials, toon, hologram, blueprint, halftone, thermal, normals, pearl, dither) built from `three/tsl` node materials out of each X3D material's colours, on the Still life, Prismatica and Asterion scenes. The WebGPURenderer chose its WebGL 2 backend on this rig, so no WebGPU timing exists [L]. Shapes that use a raw GLSL `ComposedShader` are hidden, because a node material cannot restyle them. A scene over a million triangles shows one tile, since nine passes of 3.6 million triangles do not fit software rendering. The GLSL patches the bridge already carries (projector, fog coordinate, the ADD multi-texture stage) are not ported to TSL [L].

## 15. Geospatial and the last volume styles: a position is a point, and two engines disagree on a rotated volume

Batch 45 bridged ten nodes: GeoOrigin, GeoCoordinate, GeoLocation, GeoTransform, GeoViewpoint, GeoElevationGrid, GeoPositionInterpolator, and the volume styles BlendedVolumeStyle, ComposedVolumeStyle and ProjectionVolumeStyle. Read at `x3d.loom@bfeba57` (the batch-45 pull request branch); reference engine `X_ITE 16.6.0`; rig for every number in this section: `Chromium 153.0.8010.12`, SwiftShader (no real GPU), `Babylon 9.32.0`, 320 x 240 pictures. The reasoning is in `x3d.webgpu/bridge/WHY-geospatial-batch.md`.

```text
 geoCoords (lat, lon, height)  --GD or UTM or GC-->  geocentric metres (6.4e6, float64)
                                   |  minus GeoOrigin, rotated into east / up / -north when rotateYUp
                                   v
                          small local metres  --> GeoCoordinate points -> any geometry
                                              --> GeoLocation, GeoTransform matrices (L^-1 M L)
                                              --> GeoViewpoint pose, GeoElevationGrid triangles
                                              --> GeoPositionInterpolator: great circle, linear radius
```

### 15.1 The earth is the scene, and float32 cannot hold it

A geographic position becomes geocentric metres, about 6.4 million, where a 32 bit float resolves about half a metre. The bridge converts and subtracts the origin in double precision and hands the graphics card only the small remainder; a GeoOrigin with `rotateYUp` true is what makes the remainder small, because it also turns the axes to +X east, +Y up, -Z north [C]. Without it the world lies on its side and the numbers stay large, so the geocentric cases are checked as matrices and not as pictures [C]. "Up" is the ellipsoid normal, not the direction to the centre: the two differ by 0.19 degrees at latitude 45 [C].

### 15.2 GeoTransform does not move its children to the centre

The matrix is L^-1 M L, with L the placement at `geoCenter`. With default fields it is the identity and the children stay where they were written; a reader who takes the specification to mean "children at geoCenter" would be wrong for X_ITE 16.6.0, and the bridge follows X_ITE [C]. The fixture rotates 90 degrees about the local up at a `geoCenter` 111.3 m east of the origin: a box 10 m east of the centre goes to 10 m north of it, in both engines [C].

### 15.3 A great circle with a linear radius

GeoPositionInterpolator interpolates along a great circle about the earth's centre (the GeoOrigin point when there is one), changing the radius linearly, not in latitude, longitude and height. The middle of latitude 0 to latitude 60 is latitude 30.0833 and 2.66 km below the ellipsoid [C]. This is X_ITE's choice, copied so the numbers agree; the specification does not prescribe it [S, spec text not re-read].

### 15.4 Three volume styles, three surprises

ComposedVolumeStyle is a chain: each child gets the colour the one before returned and replaces it, so [red, blue] draws blue and [blue, red] draws red [C]. BlendedVolumeStyle computes clamp(c x w1 + b x w2) on all four channels, alpha included, so the default weights halve a faint volume and the slice is dropped under 1/255 [C]. ProjectionVolumeStyle is not a ray cast: each of the 400 slice fragments marches 16 steps of its own, from a start whose offset along the view is doubled, so a uniform grey 204 volume under AVERAGE (divided by 16, always) draws 38 [C]. X_ITE cannot draw the schema weight names ALPHA1 and ONE_MINUS_ALPHA1 (a stray space in the shader text makes the volume vanish), and it draws nothing when two Blended nodes meet; the bridge reads the schema names and draws any number [C].

### 15.5 Smooth volumes: dim shells, and a rotated volume X_ITE lights wrongly

The cube fixtures of batch 43 could not show what smooth data does. A 16 cubed Gaussian ball was drawn under four lit styles. Unrotated, the engines agree within about 8 levels on Shaded and 12 on ToneMapped along a row [C]. A smooth ball draws as a dim shell in both engines: the transition layer is already opaque before the bright core, so a ball whose core is 243 draws 18 grey, and a block of 204 that fills half the width of a 16 voxel volume draws 70 (the arithmetic is D-BAB-13) [C]. When the Transform above the volume rotates it, X_ITE lights it differently: a ball should look the same in any orientation, the bridge's does and X_ITE's does not (rotation about Z moves the lit side, about Y it goes almost black, only a half turn is unchanged) [C, observation]. The cause is not isolated: the gradient seems to be turned the wrong way [S]. The bridge keeps the rotation-independent picture and the fixture checks that volume in the bridge only.

### 15.6 Two test-rig slips

A plain list handed to a double field (`GeoOrigin.geoCoords`) made X_ITE draw nothing and then crash the page; the runner now builds an SFVec3d and names the type in the step [C]. And a case that X_ITE cannot compile (ALPHA1) left the rig waiting ten minutes, so it is described and not part of the fixture [C].

## 16. Batch 46: the rest of the geospatial group, and six nodes that do nothing on purpose

Batch 46 bridged ten nodes: GeoLOD, GeoTouchSensor, GeoProximitySensor, GeoMetadata and the DIS nodes EspduTransform, ReceiverPdu, SignalPdu, TransmitterPdu, DISEntityManager and DISEntityTypeMapping. Read at `x3d.loom@c80cecd` (the batch-46 pull request); reference engine `X_ITE 16.6.0`; rig for every number in this section: `Chromium 153.0.8010.12`, SwiftShader (no real GPU), `Babylon 9.32.0`, 320 x 240 pictures. The reasoning is in `x3d.webgpu/bridge/WHY-geo-dis-batch.md`.

```text
 camera --(eye-space distance of local(center))--> GeoLOD:  d < range ? level 1 : level 0
                                                     level_changed  ->  children   (this order)
 pointer --hit on a Shape--> GeoTouchSensor: hitTexCoord, hitNormal, hitPoint (sensor-local)
                                             hitGeoCoord = geoOf(sensor, LOCAL hitPoint)
 camera --pose in the sensor's parent frame--> GeoProximitySensor: isActive, position, orientation,
                                             centerOfRotation, geoCoord_changed = geoOf(sensor, position)
```

### 16.1 GeoLOD has one range and two levels

The specification talks about a list of ranges and about unloading; X_ITE 16.6.0 has a single `range` and exactly two levels, decided on every frame as `distance < range`, strictly, with the distance taken in EYE space from the camera to `center` (through the node's geoSystem and GeoOrigin, like a GeoLocation) [C]. A parent scale therefore counts: with a centre 50 m up, a parent scale of 1.9 gives level 1 and 2.1 gives level 0 [C]. Level 1 is announced at once, but the picture keeps the root until all four child scenes are finished (loaded, failed or empty), and children are fetched at the first visit to level 1 and never unloaded [C]. `level_changed` fires before `children`, the opposite of what the specification text implies [C], and starts at -1 [C]. `rootNode` wins over `rootUrl`, which is still fetched [C]. The fixtures use `data:model/x3d+xml,` urls so that they need no server [C].

### 16.2 The geographic coordinate of a touch is the geographic reading of a LOCAL point

GeoTouchSensor's output is `hitGeoCoord_changed` (there is no `geoCoords_changed`) [C]. X_ITE converts `hitPoint_changed`, which is in the sensor's own parent frame, through the sensor's geoSystem and GeoOrigin as if that frame were the origin frame. Under a Transform or a GeoLocation the result is not where the hit is: a sensor in a GeoLocation 3.3 m east of the origin reports longitude 8.4e-7 degrees, not 3.0e-5 [C]. The bridge copies it, because the aim is the same numbers and the shortcut is documented [C]; the fix would be one matrix. Two Babylon details: a pick at (160,120) is half a pixel from X_ITE's, so hitPoint differs by 0.0155 m at a distance of 9 (tolerance 0.05), and the body's meshes carry `v` flipped, so the bridge reports `1 - v` [C].

### 16.3 A proximity sensor that reports where the viewer is, and a `geoCenter` that is not a coordinate

GeoProximitySensor wraps a ProximitySensor: a box (`center`, `size`), inclusive, size 0 never active, size -1 always inside [C]. `geoCenter` is copied raw into `center` only when it is written at run time, the attribute in a file is ignored, and `center` is plain local metres (a `geoCenter` of 0 0 10 reads 10 m, not 10 degrees) [C]. On exit the last position outside is announced first (geoCoord_changed, position_changed), then isActive false and exitTime [C]. X_ITE draws on demand and notices an ENTER after a pure camera move only when something else keeps the page drawing, so the fixture animates a small box [C].

### 16.4 Six nodes that store their fields and do nothing

X_ITE 16.6.0 marks the DIS component as not supported. EspduTransform is a Group: translation, rotation and scale are stored and never applied, nothing is sent, no output (isActive, timestamp, firedTime and the rest) ever fires, and `enabled` false does not hide anything [C]. The four PDU nodes and the manager and mapping store their fields and draw nothing; the mapping never loads its url [C]. SFTime outputs default to -1, geoSystem defaults to GD WE, and the fixture head must name the DIS component or X_ITE drops the node [C]. The bridge copies all of it, and the fixtures assert silence with `noevent` after two seconds [C].

### 16.5 One fix outside the batch: an inputOutput set is one event

Setting an inputOutput field in the SAI shim raised the page's field callbacks twice (once from the body hook, once from the event queue); X_ITE raises one. The reader now marks the call (`R.rx`) so the callbacks run once [C].

## 17. Batch 47: a sensor that reads the world's contacts, a list, and a data node

Batch 47 bridged the three nodes that let a scene hear about the physics world: CollisionSensor, CollisionSpace and Contact. Read at `x3d.loom@80388ce` (the batch-46 and batch-47 pull request); reference engine `X_ITE 16.6.0` (Bullet compiled to WebAssembly); rig for every number in this section: `Chromium 153.0.8010.12`, SwiftShader (no real GPU), `Babylon 9.32.0`. The reasoning is in `x3d.webgpu/bridge/WHY-physics-sensing-batch.md`. The physics world itself is chapter [13](13-physics.md).

```text
 world sub-step (1/240 s) --> contacts of the LAST sub-step, each tagged (body, top-level collidable) x 2
                                   |
 CollisionSensor.tick: flatten(collider.collidables)  ->  body -> last listed collidable
                       keep a contact when a body of the pair is in that map  (distance <= 0)
                       isActive (only on change) -> intersections -> contacts   (every frame while touching)
 Contact: a pooled data node the sensor fills; writing one in a scene or to set_contacts does nothing
```

### 17.1 CollisionSensor does not detect anything

Once per frame X_ITE reads the contacts the world left after its last sub-step, keeps those that touch or penetrate (distance at most 0), and keeps a contact when at least one of its two bodies owns a collidable that the sensor's own `collider` lists [C]. The sensor's collider is a separate CollisionCollection from the world's. Only the top-level geometry of a body counts: list the CollidableOffset, not the shape inside it, and a body with several listed collidables is named by the last one [C]. `isActive` is sent when it changes; `intersections` and `contacts` are sent on every frame while a contact exists, as the same node objects, and are never cleared: once the touch ends `isActive` is false and the lists keep their last length [C]. `enabled` is read only at load and when `collider` is written, so a file with `enabled="false"` stays dead until the collider is written again [C]. The bridge copies all of it.

### 17.2 CollisionSpace is a list, and Contact is a pool

CollisionSpace only flattens its `collidables` through nested spaces, live: emptying a nested list ends the contact within a frame. `enabled` and `useGeometry` are never read [C]. Contact is a data node the sensor fills from a pool; it copies appliedParameters, bounce, minBounceSpeed, frictionCoefficients, surfaceSpeed and the softness fields from the sensor's collider, and slipFactors into slipCoefficients, while position, contactNormal (unit length) and depth (at least 0) come from the world [C]. In X_ITE 16.6.0 `body1`, `body2`, `geometry1` and `geometry2` stay null, because the code writes a property with a trailing underscore [C]. The bridge departs here on purpose and fills them, as the specification says; the fixture asserts X_ITE's null on the X_ITE side and the pair on ours.

### 17.3 What can be asserted, and what is a lottery

An impact lasts one sub-step in both engines: X_ITE gave true, false, true within 150 ms and no event at all with bounce on [C]. The fixtures therefore assert only resting contacts: a ball exactly touching a fixed ground and a unit cube resting on it. The count for a cube is a range (Bullet kept 2 of the 4 lower corners, the bridge 4) and the sign of `contactNormal` depends on the order of the pair, so only its length and axis are asserted [C]. Cylinders and cones are bounding spheres in the bridge world, so their flat-face contacts are approximate (logged).

### 17.4 One trap in the sweep

A scene sweep of 60 or more picture fixtures in one process crashes the page; the full regression (142 picture fixtures and 45 event fixtures) runs in chunks of 8 and passes after batches 46 and 47 [C].

## 18. Batch 48: eight nodes the reader had already eaten

Batch 48 gave fixtures to the eight nodes the Library hall port had drawn but nobody had tested: Collision, CoordinateInterpolator, CoordinateInterpolator2D, Disk2D, Extrusion, MultiTextureCoordinate, PointProperties and Rectangle2D. Read at `x3d.loom@cd71796` (the batch-48 and batch-49 pull request); reference engine `X_ITE 16.6.0`; rig for every number in this section: `Chromium 153.0.8010.12`, SwiftShader (no real GPU), `Babylon 9.32.0`. The reasoning is in `x3d.webgpu/bridge/WHY-hall-nodes-batch.md`.

### 18.1 A reader that converts a node deletes it

The hall reader turned Disk2D, Rectangle2D and Extrusion into an IndexedFaceSet while parsing, so the scene graph never held the original node and its fields (innerRadius, size, crossSection, spine) read as nothing through the SAI [C]. The bridge now owns any node type for which it registers a `geometry` hook: the node stays in the graph, and the hall maths is called through `R.hallGeom` to make the triangles. Pictures stay the same (silhouette overlap with X_ITE 0.93 for Extrusion, 0.97 for Rectangle2D, 0.98 for Disk2D) and events and `changed` work again [C].

```text
parse:   Disk2D { innerRadius 0.2 outerRadius 1 }   (kept as a real node, fields alive)
draw:    spec.geometry(node) -> R.hallGeom.disk(node) -> {pos, nrm, uv, idx} -> BR.hallFaces -> mesh
event:   set innerRadius -> spec.changed -> body.regeo -> redraw
```

### 18.2 Defaults and plumbing the tests found

PointProperties: the hall default for pointSizeMinValue was 0; the standard and X_ITE say 1, with scale 1, max 1 and attenuation 1 0 0 [C]. On this rig ours drew 12 point quads where X_ITE drew 3 for the same PointSet, so the fixture asserts the vertex count and the defaults and not a picture [C]. CoordinateInterpolator2D gave zeros because `toSAI('MFVec2f')` read a flat typed array as if it held pairs; it reads two numbers at a time now, which fixed every 2D interpolator output [C]. Collision draws its children (the hall body was missing from the bundle) and, like X_ITE, fires no isActive or collideTime without navigation collision [C]. MultiTextureCoordinate gives each stage of a MultiTexture its own matrix, the TextureTransform composed with an affine fit of channel i from channel 0; where the channels are not related by an affine map the fit is a least-squares approximation and is logged as a gap [L].

Steps ours and X_ITE: Collision 29 and 29, CoordinateInterpolator 20 and 20, CoordinateInterpolator2D 20 and 20, PointProperties 22 and 22, Extrusion 45 and 45, Rectangle2D 31 and 31, Disk2D 39 and 39, MultiTextureCoordinate 13 and 12 [C].

### 18.3 What a review finds that a green sweep cannot

After the fixtures and the 144-picture sweep were green, four reviewers each took a lens (reader regressions, body and kit, NURBS maths, lifecycle and events) and two skeptics tried to refute every claim; 23 of 24 held up [C]. Almost all were places no fixture puts the node, or changes that arrive by event: a Rectangle2D as a picking geometry read as nothing once the reader stopped converting it; a ROUTE into `set_spine` was refused because the field was initialize-only; an interpolator output read before any event threw; a PointSet with PointProperties and no Coordinate aborted the whole scene build; a MultiTexture stage that could not be drawn shifted every later stage by one; a moved Coordinate redrew a NurbsCurve but not the surface swept along it [C]. All were fixed except the ones logged as gaps: contours that cross each other, `trimmingContour.push` through the SAI proxy, camera-space texture coordinate generators inside a MultiTextureCoordinate, and a repainted PixelTexture stage [L].

## 19. Batch 49: the end of NURBS, and three places where reading the source was not enough

Batch 49 bridged NurbsTextureCoordinate, NurbsSweptSurface and NurbsTrimmedSurface, the last three NURBS nodes. Read at `x3d.loom@cd71796`; reference engine `X_ITE 16.6.0`; rig as in section 18. The reasoning is in `x3d.webgpu/bridge/WHY-nurbs-finish-batch.md`.

### 19.1 NurbsTextureCoordinate has no weights in X_ITE

X_ITE builds each texture control point as (x, y, 0, w) but samples the surface with `haveWeights` false, so nothing divides by the weight: the coordinates are the plain B-spline of the points [C]. A centre weight of 3 leaves the uv grid regular in steps of 0.125 [C]. The standard says rational; the bridge copies X_ITE and logs the difference. My first version divided by the weights from reading the source and failed at once (0.114 against 0.125), so the receipt is the measurement, not the reading [C].

### 19.2 NurbsSweptSurface is an Extrusion with crease angle pi

The cross-section curve is carried along the trajectory frame by frame and the normals are smoothed everywhere. A trajectory that is not a NurbsCurve, a missing cross-section, or a one point trajectory draws nothing in both engines. Triangle counts are equal (160 and 36 for the two shapes on screen) and positions agree to 0.02 [C].

### 19.3 NurbsTrimmedSurface keeps what an odd number of contours contain

A point is kept when an odd number of contours contain it. A contour inside another is a hole whichever way it runs, two identical squares leave nothing, a contour around the whole domain keeps everything and no contours is untrimmed [C]. The two engines cut the grid at the contour into different triangles, so the fixture compares area and bounding box of the kept part (equal to three decimals in all eight cases) and the silhouette [C]. All 260 node types in the tracker now have a reader; what remains is logged gaps, not missing nodes [C].

## Heuristics

| ID | Rule (imperative, at most 30 words) | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-BAB-1 | Give every node count its denominator and definition: page-bundle census, tracker headline or bridged-without-gap. Never subtract across definitions. | C | 68, 75, 186 and 41 all describe one codebase (N-BAB-2 to N-BAB-5) | `census.js`, `driver.py status`, `x3d.loom@162ab18` |
| H-BAB-2 | Treat `bridged` as one fixture passing in two engines at 320 x 240, and read the node's gap note before quoting it. | C | 70 of the 111 kit modules are `gap`; the assessment separates recognised, passing and correct | `NODES.json`, `ASSESSMENT-2026-11-08.md` |
| H-BAB-3 | Write the PSNR window (whole frame, crop or mask) beside every dB figure. | C | same two frames: 39.30 dB whole, 41.90 cropped | numpy PSNR, 960 x 540 (D-BAB-4) |
| H-BAB-4 | Do not accept or reject a node on dB; use the bounds written in its test spec and look at the picture. | C | 11.73 dB with verdict PASS; 40.03 dB with a drawn colour 3 to 4 times dimmer | `BATCH-23.md`, `BATCH-26.md`, X_ITE 16.6.0 |
| H-BAB-5 | Pin time in both renderers before comparing an animated scene, or label the figure "not a parity figure". | L | Gobbler 3 and Demiurge receipts say so; Odyssey and KANSEI pin | `runs/webgpu-*/GAPS.md`, SwiftShader |
| H-BAB-6 | Key a shader port by FNV-1a of the whitespace-collapsed GLSL; on a miss draw the Material and say so; make the builder refuse an unported shader. | C | whitespace edit keeps the key, one constant changes the fragment half; 6 of 13 builders refuse | Python port of the page hash (D-BAB-3) |
| H-BAB-7 | When a port looks wrong, check tier A of the trap table before touching light: winding, colour space, light scope, USE identity, emissive texture. | L | the playbooks' own advice; the tier order is our judgement [S] | playbooks v1 to v4 |
| H-BAB-8 | On every public WebGPU page show the adapter, which request answered and, when null, the flag tip with its safety cost. | L | one gen-9 laptop got no adapter until the flag was set | playbook v1; `docs/index.html` |
| H-BAB-9 | Make no speed claim without a named real GPU, driver, three runs and a receipt that fits the schema. | C | 0 timing receipts for any bridge body; 1 file in `bench/receipts/` | `ls`, `BENCHMARK.md` section 9 |
| H-BAB-10 | Where a playbook line and the code disagree, the code wins; record both and correct the playbook by a new version. | C | v1 and v2 say "convert authored sRGB"; `body.js` line 303 assigns the colour as authored | `brain/body.js` read |
| H-BAB-16 | Ask what the renderer samples, not what the spec says: X_ITE draws a volume as 400 slices with no spacing correction, so copy its lattice before comparing pixels. | C | a 4-level ramp, a block and a cartoon band match within 2 levels | x3d.loom batch 43 fixtures; X_ITE 16.6.0 source read |
| H-BAB-17 | Test a volume style against a second volume with no voxels: X_ITE draws the empty one as a white box. | C | white box measured | `VolumeData` fixture |
| H-BAB-18 | Check the default opacity map first: it keeps only the red channel, so a red RGBA voxel is white and a green one is invisible. | C | (255, 0, 0, 255) draws white | `VolumeData` fixture |
| H-BAB-19 | Where two engines blend differently, write each engine's own value into the test and say which one is more accurate; never loosen the tolerance. | L | 24 against 10, 28 against 14, 78 against 40 | x3d.loom batch 43 fixtures |
| H-BAB-11 | Copy the reference engine's tessellation rule so segment counts match; follow the standard for the maths. A count is a convention, a weight is a definition. | C | NURBS point lists agree in 32 of 32 to 55 of 55 steps; X_ITE weights give radius 1.24 | `X_ITE 16.6.0`, SwiftShader, `x3d.loom@4887a98` |
| H-BAB-12 | When the reference throws or hangs on an invalid input, run that step in your engine only and say so in the gap log; never let a test depend on a hung page. | C | `set_fraction` into an order 4, three point curve stops X_ITE answering | `X_ITE 16.6.0`, Chromium 153.0.8010.12 |
| H-BAB-13 | Prefer the exact derivative to an averaged one where the standard gives it; bound the difference from the reference in the spec instead of matching it. | C | patch normals differ 0.21 and 0.28; spec bound 0.3 | `X_ITE 16.6.0`, 12 x 12 and 8 x 8 cells |
| H-BAB-14 | When a node's geometry depends on another node's field, declare that field to the kit (`spec.refs`) and test a live change by event. | C | a moved control point redraws the curve only through `refs` | `x3d.loom@4887a98:x3d.webgpu/bridge/src/body-br.js` |
| H-BAB-15 | Check a schema failure against the content model before editing the fixture: some 4.0 nodes cannot be written validly as specified. Record the patch in the receipt. | C | NurbsSet is a sequence, not a choice; Contour2D has no parent in the model | `xmllint`, `x3d_mcp` `x3d-4.0.xsd`, driver spec keys `xsdChoice` and `xsdAllow` |
| H-BAB-20 | Share the reader and write only the body: read the reader files at bundle time instead of copying them, so a reader fix reaches every engine. | C | three.js body 284 lines against 1671 for the Babylon one; no file under `x3d.webgpu/` changed | `x3d.loom@108a282`, `wc -l` |
| H-BAB-21 | Bind the first Viewpoint at load in any new body and test the framing before the lighting. | C | IoU 0.34 to 0.64 before, 0.99 to 1.00 after, on the same 10 fixtures | `X_ITE 16.6.0`, SwiftShader, three.js r187 |
| H-BAB-22 | Make X_ITE hard for events, fields and silhouettes, and a bounded reference for lit colour; write the reason when a quality choice leaves it. | C | scaffold split; owner's ruling of 14 Nov | `tools/run-tests.js`, `x3d.loom@108a282` |
| H-BAB-23 | Convert light units and the Phong exponent between engines before judging a look: three.js needs a factor PI on lights and about four times the exponent. | C | Sphere 28.22 to 36.98 dB, Box 63.84 to 70.12 dB | `X_ITE 16.6.0`, three.js r187, SwiftShader |
| H-BAB-24 | Read the reference engine's formula in its source before tuning a look, patch your engine's shader chunk once with it, and make the patch throw when the engine's text moves. | C | six formulas, 36 to 63 dB; a moved chunk would fail at load | `X_ITE 16.6.0` source, three.js r187, SwiftShader |
| H-BAB-25 | When a formula's order or sign is uncertain, render every variant against the reference in one run and keep the one that wins by the widest margin. | C | TextureTransform: 50.1 dB against 21.2 to 25.7 dB for the other seven | `X_ITE 16.6.0`, three.js r187, 8 variants over two runs, SwiftShader |
| H-BAB-26 | Turn the reference engine's own notifications and timing overlays off before taking a picture. | C | a "Loading done" toast added about 4000 differing pixels | `X_ITE 16.6.0` `setBrowserOption`, 320 x 240 |
| H-BAB-27 | Before defining a node for a new body, grep every reader extension for it; a second definition throws at load and the page reports only that the body class is missing. | C | `BR.node` threw for Extrusion and PointSet; the page said `Body is not defined` | `x3d.loom@38530ab`, `grep` over `demo/src/*/reader*.js` |
| H-BAB-28 | Load the body bundle in node with a stub window before a browser run: load errors and data-code bugs show at once and become unit tests. | C | the missing-body failure reproduced in node; 7 tests pass | `node --test tools/`, `x3d.loom@38530ab` |
| H-BAB-29 | Where two triangulations are both valid, render both against the reference and keep the one that is pixel-identical. | C | ElevationGrid 99 dB against 29.13 dB | X_ITE 16.6.0, SwiftShader |
| H-BAB-30 | A function lifted from another engine's body carries that body's omissions: list the features it never used (creaseAngle, Normal, per-face colour) and give each a fixture. | C | Extrusion faceted until `BR.ifsExtras`; IndexedFaceSetNormals 80.17 dB | `x3d.loom@38530ab` |
| H-BAB-31 | Check that a passing fixture can fail: if both engines draw black or nothing, the match proves nothing. | C | 6108 against 9236 foreground pixels after the normals were changed | IndexedFaceSetNormals receipt |
| H-BAB-32 | Review each batch with independent adversarial reviewers before the merge request: they find what the picture comparison cannot (dynamic changes, input-event paths, stale lists), and a verifier per finding keeps the false ones out. | C | 29 confirmed, 3 refuted; the 45 fixtures had passed before the review | workflow run of 35 agents over `x3d.loom@8a1e769`, fixes in `38530ab` |
| H-BAB-33 | Convert and subtract the GeoOrigin in float64, and hand a float32 matrix only the small remainder; never draw a geocentric point directly. | C | 6.4e6 m has 0.5 m resolution in float32 (N-BAB-49) | `GeoCoordinate.js` `BR.geo` |
| H-BAB-34 | Read a GeoTransform as L^-1 M L, not as "children at geoCenter"; test it with a rotation about the local up. | C | default fields give the identity; box 10 m east goes to 10 m north (N-BAB-51) | `GeoTransform.test.json` |
| H-BAB-35 | Test a lit volume style on smooth data, rotated and unrotated; a cube hides both the dim shell and the rotation error. | C | ball under Shaded: unrotated agree, rotated differ (N-BAB-53, N-BAB-54) | `_volume-smooth-lit` |
| H-BAB-36 | Give a test-rig `set` of a double field its type; a plain list becomes NaN in X_ITE and looks like an X_ITE defect. | C | geoCoords set drew nothing until SFVec3d was built | `tools/run-tests.js` |
| H-BAB-70 | Put a node's defaults in the fixture beside its non-default settings: render `<TextureProperties/>` as well as the NEAREST variant before reading a default's name as a behaviour. | C | FASTEST read as nearest: 28.23 dB; measured smooth: 67.60 dB | `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187, TextureProperties fixture |
| H-BAB-71 | Bracket a reference engine's threshold with inputs on both sides in one scene (4 x 4, 16 x 16 and 32 x 32 images) before writing the rule. | C | 4 x 4 hard texels, 16 and 32 smooth; the edge between 4 and 16 is not bisected | `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187 |
| H-BAB-72 | Pick between blend orders by region means as well as frame dB: one cube of three told the placements apart. | C | ADD cube red mean 181.1, 226.2, 214.1 against 214.9; frame dB 28.15, 27.84, 35.03 | `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187, MultiTexture fixture |
| H-BAB-73 | Test a background or cube map from every direction with an asymmetric marker on each face, so a turned or mirrored face cannot pass. | C | six faces identical on the first run with a white bottom-left and black top-right pixel | `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187, TextureBackground fixture |
| H-BAB-74 | Make sure a `set` step changes the reference engine's picture too: a harness conversion gap looks like an engine difference. | C | MFColor `set` drew X_ITE black until the runner converted it | `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187, `tools/run-tests.js` |
| H-BAB-37 | Take a distance for a level of detail in the camera's frame, not the node's: a parent scale changes it. | C | scale 1.9 gives level 1, 2.1 gives level 0 | `GeoLOD.test.json` |
| H-BAB-38 | When a node is marked not supported in the reference engine, copy its silence and assert it with `noevent`; never add behaviour the oracle lacks. | C | six DIS nodes, 69 to 146 steps each, same in both engines | `X_ITE 16.6.0`, `x3d.loom@c80cecd` |
| H-BAB-39 | Name the frame of every geographic output: a value that is local to a sensor is only the true position when nothing moves the sensor. | C | hitGeoCoord under a GeoLocation reads 8.4e-7, not 3.0e-5 degrees | `GeoTouchSensor.test.json` |
| H-BAB-40 | Keep the reference engine drawing (animate something) when a test depends on a sensor noticing a camera move. | C | X_ITE sees an enter only after an extra frame | `GeoProximitySensor.test.json` |
| H-BAB-41 | Assert only resting contacts for a collision sensor: an impact lasts one sub-step in both engines and is a lottery. | C | X_ITE sent true, false, true within 150 ms, nothing with bounce on | `CollisionSensor.test.json` |
| H-BAB-42 | Copy a reference engine's null before correcting it: assert its value on its side and the specified value on yours, and log the departure. | C | Contact body1, body2, geometry1, geometry2 | `Contact.test.json` |
| H-BAB-75 | Put the reference engine's rule for a node in a one-node probe before writing its body: X_ITE draws a cube map only through a TextureCoordinateGenerator, and a fixture without one measures nothing. | C | magenta and blue split until the generator was in the scene | `CubeMaps.js`, `ImageCubeMapTexture.x3d` |
| H-BAB-76 | Let the renderer own the `#version` line: take the author's `#version 300 es` out of a RawShaderMaterial source and pass it as `glslVersion`, and use `data:` urls in fixtures (CDATA loses its line breaks in X_ITE). | C | the shader pictures are empty with the line left in (IoU 0) | `Shaders.js`, `ComposedShader.x3d` |
| H-BAB-77 | Test a frame-dependent node on a frame that is not the identity: a fixture on a `rotateYUp` origin cannot tell the right basis from the wrong one. | C | swapped basis 98 of 98 steps; on the new fixture IoU 0 and 18.49 dB | `GeoViewpointFrame.test.json` |
| H-BAB-78 | Write a fixture for every path a review fixes: each of the 69 findings of batch 4 was on a path (second finger, USE'd node, replaced world) that no fixture drove. | C | InlineUse: both copies draw, load FALSE takes both away, TRUE brings both back | `InlineUse.test.json` |
| H-BAB-79 | Guard an include before it is fetched: depth, fan-out, size, and a cycle on the chain's own urls. | C | 8 deep, 512 loads, 32 MB (128 MB unzipped) | `body-three.js` `loadInline` |
| H-BAB-80 | A security fix in a shared file is told to the lane that owns it: the scheme test of an Anchor must drop what a URL parser drops (tab, line break, leading control characters). | C | `java<tab>script:` ran past the test | `Anchor.js` |
| H-BAB-86 | A colour `scene.background` clears the colour buffer in every `render` call even with `autoClear` off: give the Background to the first pass only. | C | LayerSet 4 of 86 steps fail without it | `x3d.loom@c9b7695`, X_ITE 16.6.0, Chromium 153.0.8010.12 SwiftShader |
| H-BAB-87 | A headlight that is a child of the camera needs every pass camera in the scene; test a layer with the headlight on, in both orders. | C | unlit layers and a dark world with order `1 0` (review of batch 6) | `fixtures/LayerHeadlight.test.json` |
| H-BAB-88 | Run every fixture alone as well as in a chunk: state that survives a world swap passes in a chunk and fails alone. | C | ScreenGroup 75 of 75 in a chunk after Layout fixtures, failing from step 4 alone | `tools/driver.py check ScreenGroup` |
| H-BAB-89 | A held press belongs to the layer it started in; follow the pointer through that pass only. | C | LayerPress 14 of 14 in X_ITE; the TouchSensor left over without the rule | `fixtures/LayerPress.test.json` |
| H-BAB-90 | Give each world Viewport a bit of its own and mask the outer one first; wrapping after eight draws the ninth into the first. | C | ViewportMany, ten tiles, 12 of 12 | `fixtures/ViewportMany.test.json` |
| H-BAB-91 | Reset every shared per-frame uniform to its neutral value each frame; a mask left by the last frame of an earlier world tinted nothing in the next. | C | TextureProjectorParallel after TextureProjector, 96 of 96 | `fixtures/TextureProjectorParallel.test.json` |
| H-BAB-92 | A change to the test runner needs the full sweep, not the fixtures of the batch: one missing brace broke every events-mode fixture. | C | ScreenFontStyle, HAnimMotion, GeoPositionInterpolator, 27, 104, 51 steps | `x3d.threejs/bridge/tools/run-tests.js` |
| H-BAB-93 | Skin on the CPU with the reference's formula when the reference does not use an engine feature (skin = v + sum w (J v - v), displacers rotated after the skin). | C | HAnimHumanoid 17 of 17, bone matrices and 16 positions equal | `fixtures/HAnimHumanoid.test.json` |
| H-BAB-94 | When a fast path and a slow path must agree, make the test prove which one ran: detach the tree for the plain cast and assert no mesh holds one. | C | BvhPicking, 161 x 161 grid, plain and tree same point | `fixtures/BvhPicking.test.json` |
| H-BAB-95 | A clear colour that changes nothing means something is drawn over it: hide the X3D Background dome when a viewer wants its own backdrop. | C | style board tiles, sky colour 0.004 0.0032 0.0026 | `docs/demos/three-style-board/v1/index.html` (x3d.demo) |
| H-BAB-96 | Take the Body's WebGLRenderer from three.module.js and the node materials from three.webgpu.js; one renderer per tile. | C | style board loads and draws nine tiles | `docs/demos/three-style-board/v1/index.html` (x3d.demo) |
| H-BAB-81 | When a reader rewrites a node at parse time, give the bridge ownership of that node type instead of patching around it: the fields come back and so do events. | C | Disk2D, Rectangle2D and Extrusion fields read as nothing; IoU 0.93 to 0.98 after | `x3d.loom@cd71796`, `lifecycle.test.js` |
| H-BAB-82 | Measure a weight rule in the reference engine with a fixture that has a non-uniform weight; the source can read as rational and be sampled as plain. | C | NurbsTextureCoordinate centre weight 3 leaves X_ITE's uv regular; reading the source gave 0.114 against 0.125 | `NurbsTextureCoordinate.test.json`, X_ITE 16.6.0 |
| H-BAB-83 | Compare two triangulations of a cut shape by area and bounding box, not by corners. | C | trimmed surface: all eight cases equal to three decimals though the triangles differ | `NurbsTrimmedSurface.test.json` |
| H-BAB-84 | Give every list-valued shared-code fix (a SAI conversion, a default) a sweep of all earlier fixtures before the merge request. | C | one change to `toSAI('MFVec2f')` touches every 2D interpolator | chunked regression sweep, chunks of 8 |
| H-BAB-85 | After a batch is green, review it with lenses that ask where the node is used and what arrives by event, and have two skeptics try to refute each claim; the picture sweep cannot see either. | C | 23 of 24 claims held; none was visible to 144 picture and 48 event fixtures | workflow run of 52 agents over the uncommitted batch 48 and 49 diff |

## Drills

### D-BAB-1 Recount the bridge's coverage
- **Level:** L2
- **Task:** From `x3d.loom@162ab18:x3d.webgpu/bridge`, print the tracker totals, then count node names in the six reader parts and say how many of them are in the 260.
- **Verify:** `python3 tools/driver.py status`; `node tools/census.js ../demo/src > c.json`; then `python3 -I -c "import json;c=set(json.load(open('c.json'))['defs']);n=json.load(open('NODES.json'))['nodes'];print(len(c),len([x for x in c if x in n]))"`
- **Answer:** `reader knows 186/260 | base 75 blocked 1 bridged 41 claimed 8 gap 70 todo 65`; census prints `79 75` (4 defs outside the 4.0 list: `BlendMode`, `DepthMode`, `EnvironmentLight`, `GaussianSplats`). 186 = 75 + 41 + 70.
- **Checked:** 2026-11-14 `x3d.loom@162ab18`, Node 22.23.4, Python 3

### D-BAB-2 Re-derive the primer's 68
- **Level:** L2
- **Task:** Reproduce the primer's "68 of 260" from the tree it cites, then list what the same census gains by today.
- **Verify:** `git archive 60824ce x3d.webgpu/demo/src | tar -x -C OLD`; `node tools/census.js OLD/x3d.webgpu/demo/src`; repeat on the current tree and diff the `defs`.
- **Answer:** 72 defs, 68 in the 4.0 list, against 79 and 75 today. Added: `HAnimHumanoid`, `HAnimJoint`, `HAnimSegment`, `HAnimSite`, `Inline`, `LOD`, `ProximitySensor`; none removed. The tracker did not exist at 60824ce, so 68 to 186 is not like for like.
- **Checked:** 2026-11-14 `x3d.loom@162ab18` and `60824ce`, Node 22.23.4

### D-BAB-3 Break a shader key, then predict which half moves
- **Level:** L3
- **Task:** Compute the keys of the five ComposedShaders in `x3d.webgpu/demo/collider.x3d` with an independent implementation and compare them with the `key:` fields in `collider-v2.html`. Then (a) add runs of spaces inside `flashShader2`'s fragment and (b) change `u_phase * 12.0` to `u_phase * 12.5`; predict both keys first.
- **Verify:**
```python
import re, sys, urllib.parse
from lxml import etree
def fnv(s):
    h = 0x811c9dc5
    for c in s: h = ((h ^ ord(c)) * 0x01000193) & 0xffffffff
    return '%08x' % h
n = lambda s: re.sub(r'\s+', ' ', s).strip()
def src(u):
    b = re.match(r'\s*"?(data:[^"]*)"?\s*$', u, re.S).group(1).split(',', 1)[1]
    return urllib.parse.unquote(b) if re.search(r'%[0-9a-fA-F]{2}', b) else b
for cs in etree.parse(sys.argv[1]).iter('ComposedShader'):
    if cs.get('DEF'):                        # USE copies carry no parts
        p = {x.get('type').upper(): src(x.get('url')) for x in cs.iter('ShaderPart')}
        print(cs.get('DEF'), fnv(n(p['VERTEX'])) + '-' + fnv(n(p['FRAGMENT'])))
```
- **Answer:** the five keys equal the table in section 9. (a) leaves `1bc84a9f-b6fcc411` unchanged; (b) gives `1bc84a9f-bd1839be`: only the fragment half moves and the page would miss the port and fall back.
- **Checked:** 2026-11-14 `x3d.loom@162ab18`, Python 3 with lxml, scratch copies of the scene

### D-BAB-4 Move a PSNR by changing its window
- **Level:** L2
- **Task:** Compute PSNR and mean absolute error between the two committed facade frames, whole and with the bottom 40 rows cropped, and say which the receipt used.
- **Verify:** `runs/webgpu-quick-wins-20261107/frame-facade-webgpu.png` and `frame-facade-xite16.4.3.png` (960 x 540); `psnr = 10*np.log10(255**2 / ((a-b)**2).mean())` on RGB floats, over `[:540]` and `[:500]`.
- **Answer:** whole frame 39.30 dB (MAE 0.84); bottom 40 rows cropped 41.90 dB (MAE 0.79), the receipt's 41.9 and 0.79. A 2.6 dB spread from the window alone.
- **Checked:** 2026-11-14 numpy 2.5.3, Pillow 12.3.0, `x3d.loom@162ab18`

### D-BAB-5 Census a corpus before you promise a port
- **Level:** L3
- **Task:** For every `.x3d` under `x3d.demo@d10b457:docs/demos`, list node names, classify each by `NODES.json` status and report how many scenes need only `base` names. Then say why "base" is not a promise that a given page can load the scene.
- **Verify:** parse each file with lxml, skip `X3D head Scene ROUTE field meta component unit IS connect fieldValue Proto* IMPORT EXPORT`, treat `BlendMode DepthMode EnvironmentLight GaussianSplats` as extension names, look the rest up in `NODES.json`.
- **Answer:** 111 files parse (the two `facade.x3d` do not); 86 use only `base` or extension names, 22 use at least one `gap`, `todo` or `claimed` node (CoordinateInterpolator 9, LineSet 8, PointProperties 6, Geo nodes 2 each), 1 uses unknown names. "Base" is the union of six reader parts: a page loads only its own bundle, and each page's census must be run on its own `PARTS` list (the hall extension alone adds 8).
- **Checked:** 2026-11-14 lxml, `x3d.demo@d10b457`, `x3d.loom@162ab18`

### D-BAB-9 Opacity of a stack of slices
- **Level:** L1
- **Task:** X_ITE blends 400 slices with source-alpha and no spacing correction. A ray crosses 230 slices of alpha 0.02. How opaque is the pixel, and what would 200 and 600 slices (LOW and HIGH) give?
- **Verify:** `1 - (1 - a) ** n` in Python.
- **Answer:** 0.9904 for 230; for a full 200, 400 and 600 slices 0.9824, 0.9997 and 0.999995. The same alpha is thicker at HIGH, so alpha is "per slice" and a quality setting changes the picture.
- **Checked:** 2026-11-14 python3 -I
### D-BAB-6 Check the weights: radius 1.00, not 1.24
- **Level:** L2
- **Task:** Load `src/nurbs.js` in plain Node, build the weighted quarter circle (control points `1 0 0, 1 1 0, 0 1 0`, order 3, knots `0 0 0 1 1 1`, weights `1, 0.7071, 1`) and the same curve unweighted, and report the largest radius error of the weighted one and both midpoints. Then say which of the two midpoints X_ITE's NurbsPositionInterpolator returns.
- **Verify:**
```js
const fs = require('fs'), BR = {};
new Function('BR', fs.readFileSync('src/nurbs.js', 'utf8'))(BR);
const q = { pts: [[1, 0, 0], [1, 1, 0], [0, 1, 0]], order: 3, knot: [0, 0, 0, 1, 1, 1] };
const w = BR.nurbs.curve({ ...q, weight: [1, Math.SQRT1_2, 1] }), u = BR.nurbs.curve(q);
let worst = 0; for (let i = 0; i <= 20; i++) { const p = w.at(i / 20); worst = Math.max(worst, Math.abs(Math.hypot(p[0], p[1]) - 1)); }
console.log(worst, w.at(0.5), u.at(0.5));
```
Run from `x3d.webgpu/bridge` of `x3d.loom@4887a98`.
- **Answer:** radius error 2.2e-16; weighted midpoint (0.7071, 0.7071, 0), unweighted (0.75, 0.75, 0). X_ITE 16.6.0 returns the unweighted one (0.75, 0.75, 0), which a rational B-spline does not.
- **Checked:** 2026-11-14 Node, `x3d.loom@4887a98`

### D-BAB-7 Re-run one NURBS node against X_ITE
- **Level:** L2
- **Task:** Run the driver check for NurbsPositionInterpolator and read the step counts; then find which steps run in our engine only and why.
- **Verify:** `python3 tools/driver.py check NurbsPositionInterpolator` from `x3d.webgpu/bridge` with X_ITE 16.6.0 and Babylon 9.32.0 in place (see the README); open `fixtures/NurbsPositionInterpolator.test.json` and search for `only`.
- **Answer:** ours 55 of 55, X_ITE 52 of 52 steps pass. Four steps carry `only: "ours"`: the weighted midpoint checked against the exact (0.7071, 0.7071, 0) to 1e-6, its radius check, and the invalid-curve `set_fraction` with its no-event check (X_ITE throws and stops answering). One carries `only: "xite"`: it records X_ITE's own unweighted (0.75, 0.75, 0). 55 - 4 = 51 shared steps, plus 1 = 52.
- **Checked:** 2026-11-14 `x3d.loom@4887a98`, `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, Babylon 9.32.0

### D-BAB-8 Predict a set's triangle counts
- **Level:** L3
- **Task:** A NurbsPatchSurface A has `uTessellation=8`, `vTessellation=4` (8 x 4 cells), another, B, has 6 x 6. Both are in a NurbsSet. Predict A's triangle count at `tessellationScale` 1, 0.5, 2 and 0.3, and B's count after `removeGeometry` of B at scale 1.5. Then check against `fixtures/NurbsSet.test.json`.
- **Verify:** the `jsn` steps in `fixtures/NurbsSet.test.json` (steps 1, 6, 11, 16, 27); `python3 tools/driver.py check NurbsSet`.
- **Answer:** cells = floor(8 x scale) times floor(4 x scale), two triangles per cell: 64, 16, 256 and 4 (floor(2.4) x floor(1.2) = 2 x 1 cells). B leaves the set and returns to its own 6 x 6 x 2 = 72 triangles. The spec records 64, 16, 256, 4 and 72; both engines agree.
- **Checked:** 2026-11-14 `x3d.loom@4887a98`, `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, Babylon 9.32.0

### D-BAB-10 Break the first-Viewpoint rule and read the picture
- **Level:** L2
- **Task:** In `x3d.threejs/bridge/src/body-three.js` delete the lines in `setWorld` that bind the first Viewpoint, run the Box fixture, and predict the silhouette IoU before you look.
- **Verify:** `python3 tools/driver.py check Box` from `x3d.threejs/bridge`, with X_ITE 16.6.0 and three.js r187 in place; restore the lines afterwards.
- **Answer:** the body keeps its default pose (0 0 10, field of view 0.7854) while the fixture's Viewpoint sits at 0 0 8, so the box is drawn smaller than X_ITE draws it: the Box fixture measured IoU 0.64 (5773 pixels against 9021) before the lines existed, and 1.00 after.
- **Checked:** 2026-11-14 `x3d.loom@108a282`, `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187

### D-BAB-11 Swap the ElevationGrid diagonal and predict the number
- **Level:** L2
- **Task:** In `x3d.threejs/bridge/src/nodes/Geometry.js` change `tri.push(a, c, d, a, d, b)` to `tri.push(a, c, b, b, c, d)`, run the ElevationGrid fixture and predict whether the silhouette or the shading moves before you look.
- **Verify:** `NODE_PATH=/opt/node22/lib/node_modules node tools/run-tests.js ElevationGrid` from `x3d.threejs/bridge`, with X_ITE 16.6.0 and three.js r187 in place; restore the line afterwards.
- **Answer:** the silhouette does not move (both triangulations cover the same squares, IoU 0.97 and above); the shading does, because the flat facets of a creaseAngle 0 grid follow the diagonal: mad 2.70 and 29.13 dB against 99 dB (identical) with X_ITE's diagonal.
- **Checked:** 2026-11-14 `x3d.loom@38530ab`, `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187

### D-BAB-12 Midpoint of latitude 0 to latitude 60
- **Level:** L2
- **Task:** Interpolate halfway between (lat 0, lon 0, h 0) and (lat 60, lon 0, h 0) the way X_ITE 16.6.0 does: convert both to geocentric (WGS84), take the great-circle direction halfway, take the radius halfway, convert back. What are the latitude and the height?
- **Verify:** about 20 lines of Python (ECEF, slerp of unit vectors, linear radius, iterate the geodetic inverse).
- **Answer:** latitude 30.0832518, height -2663.0003 m; the radii are 6378137.0 and 6362132.224 m. The path is not (30, 0, 0).
- **Checked:** 2026-11-15 python3 -I

### D-BAB-13 Why a block of 204 draws 70
- **Level:** L3
- **Task:** A 16 cubed volume of dimensions 0.8 has voxels of 204 in the middle 8 along the viewing axis and 0 outside, linear filtering. X_ITE blends 400 slices spaced 0.8 x sqrt(3) / 399 apart with source alpha, no correction, the default ramp g = (v x 256 / 255 - 0.5 / 255) giving colour g and alpha g. Predict the centre pixel (0 to 255), and say why it is not 204.
- **Verify:** a loop over the slices front to back (pixel += (1 - A) x g x g; A += (1 - A) x g), stopping at A > 0.998.
- **Answer:** 70.35, so 70. The linear ramp from 0 to 204 between two voxel centres is 14 slices long; its alpha is already opaque before the full 204 is reached, so the pixel is the colour of the ramp, not the block. With nearest filtering (8 voxels) there is no ramp and the pixel is 204.
- **Checked:** 2026-11-15 python3 -I (70.35); the rig gives 70 in both engines

### D-BAB-70 Make FASTEST mean nearest and predict which box moves
- **Level:** L2
- **Task:** In `x3d.threejs/bridge/src/body-three.js`, in `texProps`, change `mag === 'NEAREST_PIXEL'` to `mag === 'NEAREST_PIXEL' || mag === 'FASTEST'`, run the TextureProperties fixture and predict which of its seven shapes changes before you look.
- **Verify:** `NODE_PATH=/opt/node22/lib/node_modules node tools/run-tests.js --shots /tmp/shots TextureProperties` from `x3d.threejs/bridge`, with X_ITE 16.6.0 and three.js r187 in place; restore the line afterwards.
- **Answer:** only the box whose texture has `<TextureProperties/>` with every field at its default goes hard-edged (its magnification is FASTEST); the silhouettes do not move (IoU 1.00) and the picture falls from 67.60 dB (mad 0.01) to 28.23 dB (mad 1.27), because X_ITE draws that box smooth.
- **Checked:** 2026-11-15 `x3d.loom@72a4bca`, `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187

### D-BAB-71 Stop the ground at its last groundAngle
- **Level:** L3
- **Task:** In `x3d.threejs/bridge/src/nodes/Background.js` delete the line that adds a stop at the horizon (`if (stops[0][0] > Math.PI / 2) stops.unshift(...)`), run the Background fixture and predict which of its three views get worse before you look.
- **Verify:** `NODE_PATH=/opt/node22/lib/node_modules node tools/run-tests.js --shots /tmp/shots Background` from `x3d.threejs/bridge`; restore the line afterwards.
- **Answer:** only the level view: the ground (last groundAngle 1.4 of a possible 1.5708) ends 0.17 radian below the horizon with a curved edge, so the picture has mad 36.07 (9.75 dB) against 0.28 (53.61 dB); the up view (48.04 dB) and the down view (52.79 dB) do not show the horizon and do not move.
- **Checked:** 2026-11-15 `x3d.loom@72a4bca`, `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187

### D-BAB-72 Leave the `#version` line in a ComposedShader
- **Level:** L2
- **Task:** In `x3d.threejs/bridge/src/nodes/Shaders.js`, in `make`, change `es3 = !!(lv && lf)` to `es3 = false && !!(lv && lf)` so the author's `#version 300 es` line stays in the source, run the ComposedShader fixture and predict which of its steps fail before you look.
- **Verify:** `NODE_PATH=/opt/node22/lib/node_modules node tools/run-tests.js --shots /tmp/shots ComposedShader` from `x3d.threejs/bridge`, with X_ITE 16.6.0 and three.js r187 in place; restore the line afterwards.
- **Answer:** the 9 event steps still pass (the node and its fields are read by the reader), and both pictures are empty: IoU 0 and mad 21.87 for `main` (foreground mean 0 against 140, 148, 63) and mad 18.17 for `fields`. three.js puts its own `#define` lines first and a `#version` line may not follow them, so the program does not compile and the Shape is drawn with its Material.
- **Checked:** 2026-11-15 `x3d.loom@1192dd4`, `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187

### D-BAB-73 Transpose the matrix of a GeoLocation
- **Level:** L3
- **Task:** In `x3d.threejs/bridge/src/nodes/Geo.js`, in `place`, change `r.tn.matrix.fromArray(G.matrixOf(n));` to `r.tn.matrix.fromArray(G.matrixOf(n)).transpose();`, run the GeoLocation and GeoTransform fixtures and predict where the node ends up.
- **Verify:** `NODE_PATH=/opt/node22/lib/node_modules node tools/run-tests.js --shots /tmp/shots GeoLocation GeoTransform` from `x3d.threejs/bridge`; restore the line afterwards.
- **Answer:** the row-vector matrix keeps its translation in elements 12 to 14, which is where a column-major three.js matrix keeps it; transposed, the translation lands in the bottom row and is lost. GeoLocation fails 9 of 22 steps (the position reads 0 0 0 where 6378137 0 0 is expected; boxes sit at the origin) and GeoTransform fails 5 of 34 steps.
- **Checked:** 2026-11-15 `x3d.loom@1192dd4`, `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187
### D-BAB-74 How much of a patch does a ring keep
- **Level:** L2
- **Task:** A trimmed patch has an outer square contour from 0.1 to 0.9 in both parametric directions and, inside it, a 16 sided polygon of radius 0.25 centred at 0.5 0.5. Using the odd rule, what fraction of the parametric domain is kept?
- **Verify:** `python3 -I -c "import math;print(0.8*0.8-0.5*16*0.25**2*math.sin(2*math.pi/16))"`
- **Answer:** 0.4487. The square covers 0.64 of the domain and the hole removes 0.1913 of it because a point inside both contours has an even count.
- **Checked:** 2026-11-15 python3 -I (0.4487)

### D-BAB-75 Keep the Background on every pass
- **Level:** L2
- **Task:** In `x3d.threejs/bridge/src/body-three.js`, in `renderAll`, change `if (i) this.scene.background = null;` to `if (false) this.scene.background = null;`, run the LayerSet and Layer fixtures and predict which steps fail.
- **Verify:** `NODE_PATH=/opt/node22/lib/node_modules node tools/run-tests.js LayerSet Layer` from `x3d.threejs/bridge`; restore the line afterwards.
- **Answer:** the Background is a colour, so every `render` call clears the colour buffer inside its scissor; the second pass erases the first. LayerSet fails 4 of 86 steps (the red world box under order `0 1` and `1 0` reads black). Layer passes: its world is empty.
- **Checked:** 2026-11-15 `x3d.loom@c9b7695`, `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187

### D-BAB-76 What the skin of one vertex becomes
- **Level:** L2
- **Task:** One vertex sits at 1 0 0. One joint with a binding that makes the rest pose the identity is turned 90 degrees about Z, so its matrix J takes 1 0 0 to 0 1 0. The vertex gives that joint a skinCoordWeight of 0.5. Using X_ITE 16.6.0's skin formula, where does the vertex go?
- **Verify:** `python3 -I -c "v=(1,0,0);w=0.5;Jv=(0,1,0);print(tuple(v[i]+w*(Jv[i]-v[i]) for i in range(3)))"`
- **Answer:** 0.5 0.5 0. The weight the joint does not take stays on the rest position, so the vertex lands halfway along the way from where it was to where the joint would put it.
- **Checked:** 2026-11-15 python3 -I ((0.5, 0.5, 0.0))

### D-BAB-77 How many heights make 125,000 triangles
- **Level:** L1
- **Task:** The bounds-tree demo's smallest size is an ElevationGrid with n x n heights, two triangles to each grid cell, 125,000 triangles in all. What is n?
- **Verify:** `python3 -I -c "import math; print(int(math.isqrt(125000//2))+1)"`
- **Answer:** 251. There are 250 x 250 cells, 62,500, and two triangles each make 125,000. The 500,000 size is 501 x 501 heights.
- **Checked:** 2026-11-15 python3 -I (251)

## Honest limits

- **Software GL only, Chromium only [C].** Every pixel number is SwiftShader in Chrome for Testing 153.0.8010.12; no real GPU, Firefox or Safari. Babylon 9.32.0 is a snapshot; 9.33.0 to 9.35.0 (per the primer) were not run [L].
- **Per-port dB figures are read, not re-run [L].** Re-run here: the facade frames, the census counts, the hash keys, the greps, the 33 tests. The 42 visual rows of batches 21 to 26 were parsed from the batch reports, not regenerated (that needs X_ITE 16.6.0 and a browser).
- **Sources disagree.** C1: playbooks v1 and v2 say to convert authored sRGB; `brain/body.js` line 303 assigns the colour as authored; the code is the evidence and no later playbook version corrects the sentence. C2: "42 of 260" (playbook v1), 62, 68 and 186 count different readers; the primer explains 42 as 44 table entries minus 2 X_ITE-only names [L, carried]. C3: the blocklist, `STATE.md` against the playbook (section 10). C4: the primer's "55 traps" is its own symptom table; the 50 here merge the four playbook files; they are not the same list. C5: the primer's 22 hash keys against 26 today. C6: batch headlines are non-monotonic (184, 184, 181, 186); the dip's cause is inferred [L].
- **Open defects were read at `6b3cb76`, not re-checked at `162ab18` [L]:** shared-node occurrence bookkeeping, dropped shear, IndexedFaceSet normals, ignored `head/unit`, ColorRGBA alpha. They bound what "bridged" means.
- **Behaviour was never compared [L].** No event traces, pointer tapes or audio pass; fixtures compare ROUTE chains in two engines, not whole pages. The noise floor of X_ITE against itself (TBD-13) is unmeasured, so no dB threshold here is a standard.
- **Carried, not re-checked [S]:** law-40 coverage by page, the Gobbler review defect, all effort figures in `PATHS.md` and `BABYLON.md` (person-weeks are guesses), the 1,396 `gl.*` call sites. Private run logs, device owners' details and unpublished material are left out on purpose.
- **NURBS section read at the batch-44 branch, not main [L]:** `x3d.loom@4887a98` carried the pull request when written; counts are from the batch run of 2026-11-14 (our reader and X_ITE 16.6.0 on SwiftShader). Not covered: real GPU timing, GeoCoordinate control points, NurbsTextureCoordinate, trimming, picking of NURBS lines. The chord reading of the Extrusion Y axis is Likely: read from memory of 19775-1, not re-checked against the text.
- **The three.js bridge is 132 fixtures, not a port [L].** At batch 8 the bridge README counts 130 nodes drawn, 32 still to do (mostly NURBS and nodes that wait on the Babylon batches); HAnim, particles, Texturing3D, Sound, the pick sensors and TextureProjector are drawn since batch 7 (the 106-fixture and 105-node counts in section 14 are as of batch 6), the bounds tree skips skinned geometry, `global=FALSE` is honoured for projectors but light scope is not implemented, a GeoViewpoint draws on a plain depth buffer where X_ITE uses a logarithmic one, 32 Babylon fixtures probe `__body` internals and match here by picture only, and the batch-46 GeoViewpoint fixture cannot tell a wrong frame basis from a right one (GeoViewpointFrame does) [L]. Text letter shapes differ from X_ITE's (IoU 0.65). No real-GPU timing exists.
- **Geospatial section read at the batch-45 branch, not main [L]:** counts are from the batch run of 2026-11-15 on SwiftShader; geocentric (no GeoOrigin) pictures are not made (32 bit world matrix), GeoViewpoint navigation is computed, not wired, and WM, the angle unit and the geoid are not implemented in X_ITE 16.6.0 or the bridge. The rotated-volume error of X_ITE is observed on one Gaussian ball and its cause is not isolated [S].

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-BAB-1 | concrete nodes in the bridge tracker | 260 | C | `X3DUOM 4.0` via `NODES.json` | x3d.loom@162ab18:x3d.webgpu/bridge/NODES.json |
| N-BAB-2 | tracker headline "reader knows" | 186 of 260 (71.5%): base 75, gap 70, bridged 41; claimed 8, blocked 1, todo 65 | C | `driver.py status`, `x3d.loom@162ab18` | x3d.loom@162ab18:x3d.webgpu/bridge/tools/driver.py (D-BAB-1) |
| N-BAB-3 | page-bundle census, 8 Nov tree | 68 of 260 (72 defs) | C | `census.js` on `git archive 60824ce` | x3d.loom@60824ce:x3d.webgpu/demo/src (D-BAB-2) |
| N-BAB-4 | page-bundle census, today | 75 of 260 (79 defs); 83 (87) with the hall extension | C | `census.js`, 162ab18 | x3d.loom@162ab18:x3d.webgpu/bridge/tools/census.js |
| N-BAB-5 | bridged without a logged gap | 41 of 260 (15.8%) | C | `driver.py status` | x3d.loom@162ab18:x3d.webgpu/bridge/NODES.json |
| N-BAB-6 | batch headlines 20 to 26 | 175, 175, 179, 184, 184, 181, 186 | L | read in `BATCH-NN.md` | x3d.loom@162ab18:x3d.webgpu/bridge/BATCH-20.md to BATCH-26.md |
| N-BAB-7 | slots filled by batches 21 to 26 | 30: 17 bridged, 13 gap; PRs #43 to #45 | C | `NODES.json`, merge log | x3d.loom@162ab18:x3d.webgpu/bridge/NODES.json |
| N-BAB-8 | visual compare rows, batches 21 to 26 | 42 rows; PSNR 11.73 to 40.03, median 35.92 | C | parsed from the reports; X_ITE 16.6.0, 320 x 240, SwiftShader | x3d.loom@162ab18:x3d.webgpu/bridge/BATCH-21.md to BATCH-26.md |
| N-BAB-9 | X_ITE 16.7.0 WebGPU strings | 0 "webgpu", 0 `navigator.gpu`, 1 `getContext("webgl2"` | C | grep, `x_ite.min.js` sha256 prefix b7df063e8cb1 | x3d.docs@f172f67:docs/vendor/x_ite/x_ite.min.js (grep, section 2) |
| N-BAB-10 | merged traps | 50: first seen v1 13, v2 19, v3 13, v4 5; tiers A 14, B 20, C 11, W 5 | C (count), S (ranking) | script over the section 5 table | this chapter, section 5 |
| N-BAB-11 | distinct hash-keyed shader programs | 26 (Collider 5, brain 4, manifold 7, Gobbler 3 6, Demiurge 4); 22 on 8 Nov; 6 more keyed by DEF in Dynasty | C | grep of `'[0-9a-f]{8}-[0-9a-f]{8}'` | x3d.loom@162ab18:x3d.webgpu/demo/src |
| N-BAB-12 | facade PSNR by window | 39.30 dB whole; 41.90 dB bottom 40 rows cropped; MAE 0.84 and 0.79 | C | numpy, Pillow, 960 x 540, X_ITE 16.4.3 reference | x3d.loom@162ab18:runs/webgpu-quick-wins-20261107/ (D-BAB-4) |
| N-BAB-13 | Pantheon splats; Manifold | 50.17 and 51.01 dB; 49.34 and 48.47 dB | L | `X_ITE 16.4.3` (960 x 540); `X_ITE 16.5.1` (640 x 360); SwiftShader | x3d.loom@162ab18:runs/webgpu-{pantheon-splats,manifold}-2026110*/RECEIPT.md |
| N-BAB-14 | brain, Babylon 9.32.0 | 33.03 all; 35.11 glass to 21.53 labels; torso 30.26 | L | `X_ITE 16.6.0`, 640 x 360, SwiftShader | x3d.loom@162ab18:runs/webgpu-brain-20261107/RECEIPT.md |
| N-BAB-15 | KANSEI, masked | 24.36 to 32.46 over 6 views; sim hash equal in 6 of 6 | L | `X_ITE 16.5.1`, 640 x 360, SwiftShader | x3d.loom@162ab18:runs/webgpu-drift-20261107/RECEIPT.md |
| N-BAB-16 | Material Odyssey | 25.5 to 30.7 as authored (6 film times); 18.4 to 28.2 look on | L | `X_ITE 16.4.3`, 1280 x 536, SwiftShader | x3d.loom@162ab18:runs/webgpu-odyssey-20261108/RECEIPT.md |
| N-BAB-17 | Chirp; Cloud; Gobbler 3; Demiurge; Dynasty; Hall | 24.87 to 25.36; 19.24 to 19.40 (21.01 to 24.96 masked); 14.60 to 19.66; 7.18 to 13.26; 29.0 to 37.8; 17.5 to 25.3 dB | L | `X_ITE 16.5.1`, SwiftShader | x3d.loom@162ab18:runs/webgpu-{chirp,cloud,gobbler,demiurge,dynasty,hall}-*/ |
| N-BAB-18 | corpus name census | 111 files: 86 base-only, 22 need gap or todo or claimed, 1 unknown | C | lxml, `NODES.json` | x3d.demo@d10b457:docs/demos (D-BAB-5) |
| N-BAB-19 | real-GPU timing receipts for any bridge body | 0; `bench/receipts/` holds 1 file (the G1 adapter probe) | C | `ls` | x3d.loom@162ab18:x3d.webgpu/bench/receipts/ |
| N-BAB-27 | X_ITE volume slice count | 400 at MEDIUM (200 LOW, 600 HIGH); spacing \|dimensions\| / 399 | C | X_ITE 16.6.0, `VolumeRenderingComponent` read | x_ite 16.6.0 npm package, `VolumeRenderingComponent.js` (read) |
| N-BAB-28 | batch 43 fixture assertions | 151 over 10 nodes (19, 30, 14, 8, 18, 11, 10, 11, 11, 19) | C | x3d.loom batch 43 receipts; X_ITE 16.6.0, Chromium 153, SwiftShader | x3d.loom `receipts/` (batch 43) |
| N-BAB-29 | faint-alpha stack, bridge against X_ITE | 10 against 24 plain stack; 14 against 28 Edge; 40 against 78 Boundary | C | x3d.loom batch 43 fixtures; X_ITE 16.6.0 | `VolumeData`, `EdgeEnhancementVolumeStyle`, `BoundaryEnhancementVolumeStyle` fixtures |
| N-BAB-20 | batch 44 nodes bridged; steps passed, ours and X_ITE | 10 nodes; NurbsCurve 32 and 32, NurbsCurve2D 36 and 36, ContourPolyline2D 14 and 14, Contour2D 22 and 22, NurbsPositionInterpolator 55 and 52, NurbsOrientationInterpolator 51 and 48, NurbsSurfaceInterpolator 52 and 51, NurbsPatchSurface 35 and 35, NurbsSet 47 and 46, NurbsSwungSurface 18 and 18 | C | `driver.py batch -n 10 --close`, X_ITE 16.6.0, Chromium 153.0.8010.12, SwiftShader | x3d.loom@4887a98:x3d.webgpu/bridge/BATCH-44.md |
| N-BAB-21 | weighted quarter circle radius | 1.00 to 2.2e-16 here; up to 1.24 in X_ITE 16.6.0 | C | Node (D-BAB-6); X_ITE 16.6.0 SwiftShader | x3d.loom@4887a98:x3d.webgpu/bridge/fixtures/NurbsCurve.test.json |
| N-BAB-22 | weighted midpoint of the quarter circle | (0.7071, 0.7071, 0) here; (0.75, 0.75, 0) in X_ITE 16.6.0 | C | Node (D-BAB-6); X_ITE SAI | x3d.loom@4887a98:x3d.webgpu/bridge/fixtures/NurbsPositionInterpolator.test.json |
| N-BAB-23 | patch normal difference to X_ITE | largest component 0.21 (12 x 12 cells), 0.28 (8 x 8); spec bound 0.3 | C | X_ITE 16.6.0 private getNormals, SwiftShader | x3d.loom@4887a98:x3d.webgpu/bridge/fixtures/NurbsPatchSurface.test.json |
| N-BAB-24 | swung surface frame difference | 1.2e-7 on an even spine; up to 0.017 on a 2.2-unit vase; spec bound 0.02 | C | X_ITE 16.6.0 private getVertices, SwiftShader | x3d.loom@4887a98:x3d.webgpu/bridge/fixtures/NurbsSwungSurface.test.json |
| N-BAB-25 | NURBS visual compare rows, batch 44 | 6 rows; iou 0.85 to 0.99; mad 1.64 to 3.74; PSNR 23.38 to 37.12 dB (320 x 240) | C | X_ITE 16.6.0, SwiftShader, parsed from the report | x3d.loom@4887a98:x3d.webgpu/bridge/BATCH-44.md |
| N-BAB-26 | solid FALSE back face gap | 9312 of 19012 pixels drawn in a two-quad IndexedFaceSet fixture | C | Babylon 9.32.0 body vs X_ITE 16.6.0, SwiftShader | x3d.loom@4887a98:x3d.webgpu/bridge/fixtures/NurbsPatchSurface.test.json |
| N-BAB-30 | three.js bridge status of the 260 nodes | drawn 15, reader-checked 29, reader 50, todo 119, upstream 47 | C | `driver.py status` | x3d.loom@108a282:x3d.threejs/bridge/NODES.json |
| N-BAB-31 | lines: reader, sai, kit, 150 node files; Babylon body files; three.js body | 388, 319, 648, 5882; 518 + 234 + 919 = 1671; 284 | C | `wc -l` | x3d.loom@108a282:x3d.webgpu/ and x3d.threejs/bridge/src/body-three.js |
| N-BAB-32 | node hooks left to port | 15 geometry (15 plain data), 61 build (43 call only Body), 61 changed; 19 files name the engine | L | regex over `src/nodes/*.js` | x3d.loom@108a282:x3d.webgpu/bridge/src/nodes |
| N-BAB-33 | three.js visual rows | 16 pictures; IoU 0.90 to 1.00; PSNR 32.38 to 70.12 dB over 11, median 42.95; 5 identical (2 empty) | C | X_ITE 16.6.0, three.js r187, Chromium 153.0.8010.12, SwiftShader, 320 x 240 | x3d.loom@108a282:x3d.threejs/bridge/receipts/ |
| N-BAB-34 | first Viewpoint bound at load, IoU before and after | 0.34 to 0.64 on 10 of 10; 0.99 to 1.00 on 9 of 10, Material 0.90 | C | same rig, two runs of the 10 fixtures | x3d.loom@108a282:x3d.threejs/bridge/fixtures/ |
| N-BAB-35 | Phong exponent factor 4 | Sphere 28.22 to 36.98 dB; Box 63.84 to 70.12 dB | C | same rig | x3d.loom@108a282:x3d.threejs/bridge/src/body-three.js |
| N-BAB-36 | event fixtures through the three.js bundle | 30 run; 29 pass in ours and X_ITE; ColorDamper differs by a documented X_ITE hue-seam defect | C | X_ITE 16.6.0, Chromium 153.0.8010.12 | x3d.loom@108a282:x3d.threejs/bridge/receipts/ |
| N-BAB-37 | three.js bridge status, batch 1 | drawn 23, reader-checked 29, reader 49, todo 122, upstream 37 | C | `driver.py status` | x3d.loom@95eda37:x3d.threejs/bridge/NODES.json |
| N-BAB-38 | batch 1 lighting rows against X_ITE | SpotLight 63.14 and 63.13 dB; PointLight 36.61, 36.30, 51.15; attenuation 59.17 | C | X_ITE 16.6.0, three.js r187, SwiftShader, 320 x 240 | x3d.loom@95eda37:x3d.threejs/bridge/receipts/ |
| N-BAB-39 | Fog rows | 52.00, 53.41, 46.55 dB; IoU 0.99 | C | same rig | x3d.loom@95eda37:x3d.threejs/bridge/receipts/Fog.json |
| N-BAB-40 | texture rows | ImageTexture 99 dB (identical); PixelTexture 45.66; TextureTransform 50.12 and 50.21; textured primitives 39.58 | C | same rig | x3d.loom@95eda37:x3d.threejs/bridge/receipts/ |
| N-BAB-41 | TextureTransform order and sign, 4 variants in the Transform order and 4 in the column order | 50.12 (-C S R C T, rotation +, translation +); 21.34, 25.72, 21.39 for the other signs; 21.30 for T C R S -C | C | same rig, one run | x3d.loom@95eda37:x3d.threejs/bridge/src/body-three.js |
| N-BAB-42 | all compared pictures of the two batches | 30 pictures; IoU 0.90 to 1.00; PSNR 32.38 to 70.12 dB over 24, median 50.13; 6 identical | C | same rig | x3d.loom@95eda37:x3d.threejs/bridge/receipts/ |
| N-BAB-43 | three.js bridge status, batch 2 | drawn 53, reader-checked 29, reader 46, todo 95, upstream 37 | C | `driver.py status` | x3d.loom@38530ab:x3d.threejs/bridge/NODES.json |
| N-BAB-44 | all compared pictures after batch 2 | 61 pictures; IoU 0.90 to 1.00; PSNR 25.32 to 80.17 dB over 47 that differ, median 50.24; 14 at 99 dB (12 identical, 2 empty frames) | C | X_ITE 16.6.0, Chromium 153.0.8010.12, SwiftShader, three.js r187 | x3d.loom@38530ab:x3d.threejs/bridge/receipts/*.json |
| N-BAB-45 | pictures new in batch 2 | 31 pictures over 27 fixtures; 8 pixel-identical; IoU 0.91 to 1.00 | C | same rig | same receipts |
| N-BAB-46 | ElevationGrid triangulation | diagonal (a, c, d) (a, d, b): 99 dB; the other diagonal: mad 2.70, 29.13 dB | C | same rig, same fixture twice | x3d.loom@38530ab:x3d.threejs/bridge/src/nodes/Geometry.js |
| N-BAB-47 | Extrusion before and after BR.ifsExtras (first fixture) | IoU 0.98 to 0.99; mad 0.41 to 0.16; PSNR 39.98 to 38.65 dB; star fixture after: 0.99, 0.20, 37.51 dB | C | same rig | x3d.loom@38530ab:x3d.threejs/bridge/receipts/Extrusion.json |
| N-BAB-48 | lines of the three.js body | body-three.js 461 (was 284 for 12 core nodes), nodes/Geometry.js 115 | C | `wc -l` | x3d.loom@38530ab:x3d.threejs/bridge/src |
| N-BAB-49 | float32 resolution at geocentric radius 6.4e6 m | about 0.5 m | C | float32 spacing at 6.4e6 | x3d.loom@bfeba57:x3d.webgpu/bridge/src/nodes/GeoCoordinate.js |
| N-BAB-50 | great-circle midpoint, latitude 0 to 60, WGS84 | latitude 30.0832518, height -2663.0003 m | C | Python, X_ITE 16.6.0 | x3d.loom@bfeba57:x3d.webgpu/bridge/fixtures/GeoPositionInterpolator.test.json (D-BAB-12) |
| N-BAB-51 | GeoTransform rotation 90 degrees about local up, geoCenter 111.32 m east | box 10 m east of the centre drawn 10 m north of it | C | both engines | x3d.loom@bfeba57:x3d.webgpu/bridge/fixtures/GeoTransform.test.json |
| N-BAB-52 | GeoViewpoint speed, height 500 m, speedFactor 3 | 153 | C | `BR.geo.speedOf`; X_ITE formula (height + 10) / 10 x factor | x3d.loom@bfeba57:x3d.webgpu/bridge/fixtures/GeoViewpoint.test.json |
| N-BAB-53 | Shaded, 16 cubed Gaussian ball, directional light, unrotated, red along a row (ours, X_ITE) | 6/42/80/115/139/154/162 and 0/39/75/108/135/159/159 | C | SwiftShader, 320 x 240 | x3d.loom@bfeba57:x3d.webgpu/bridge/fixtures/_volume-smooth-lit.test.json |
| N-BAB-54 | same ball turned 0.9 rad about Z, Shaded, five probes (ours, X_ITE) | lit side 156 and 36 (ours, X_ITE) at the same probe | C | SwiftShader | rig runs of 2026-11-15, not in a fixture |
| N-BAB-55 | plain Gaussian ball, core 243, centre pixel | 18 (bridge), 23 (X_ITE) | C | SwiftShader | rig run of 2026-11-15 |
| N-BAB-56 | block of 204 filling half the width, 16 voxels, centre pixel | 70 in both engines; 204 at 8 voxels (nearest) and 97 at 32 voxels | C | SwiftShader | D-BAB-13 |
| N-BAB-57 | ProjectionVolumeStyle AVERAGE of a uniform grey 204 volume | 38 | C | both engines | x3d.loom@bfeba57:x3d.webgpu/bridge/fixtures/ProjectionVolumeStyle.test.json |
| N-BAB-58 | BlendedVolumeStyle defaults, voxels 204 and 102 | 153 (ALPHA0: 215, ONE_MINUS_ALPHA0: 91) | C | both engines | x3d.loom@bfeba57:x3d.webgpu/bridge/fixtures/BlendedVolumeStyle.test.json |
| N-BAB-59 | batch 45 fixture steps passed (ours / X_ITE) | Geo 305 and 300; Blended 63 and 53, Composed 17 and 17, Projection 32 and 32 | C | `run-tests.js` | x3d.loom@bfeba57:x3d.webgpu/bridge/fixtures |
| N-BAB-70 | three.js bridge status, batch 3 | drawn 65, reader-checked 29, reader 45, todo 93, upstream 28 | C | `driver.py status` | x3d.loom@72a4bca:x3d.threejs/bridge/NODES.json |
| N-BAB-71 | all compared pictures after batch 3 | 86 pictures; IoU 0.90 to 1.00; PSNR 25.32 to 80.17 dB over 62 that differ, median 50.23; 24 at 99 dB (identical or empty frames) | C | `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187 | x3d.loom@72a4bca:x3d.threejs/bridge/receipts/*.json |
| N-BAB-72 | pictures new in batch 3 | 25 pictures over 13 fixtures; 10 pixel-identical; the other 15 at 35.03 to 67.60 dB, median 48.04; IoU 0.98 to 1.00 | C | same rig | same receipts |
| N-BAB-73 | TextureProperties fixture, FASTEST read as nearest against measured smooth | 28.23 dB (mad 1.27) against 67.60 dB (mad 0.01) | C | same rig | fixtures/TextureProperties.x3d, receipts/TextureProperties.json |
| N-BAB-74 | a 4 x 4 texture on a box, smooth against hard texels | 18.80 dB against 64.50 dB | C | same rig | TextureProperties fixture, first version |
| N-BAB-75 | LineProperties, thin lines against screen-space quads | IoU 0.63 (689 against 1051 foreground pixels) against 0.98 and 47.71 dB (1069) | C | same rig | receipts/LineProperties.json |
| N-BAB-76 | MultiTexture ADD placements | frame 28.15 (canvas sum), 27.84 (after the light), 35.03 dB (before the light, unclipped); ADD cube mean red 181.1, 226.2, 214.1 against 214.9 | C | same rig | receipts/MultiTexture.json |
| N-BAB-77 | Background level view, ground stopping at the last groundAngle against held to the horizon | mad 36.07 (9.75 dB) against 0.28 (53.61 dB) | C | same rig | receipts/Background.json |
| N-BAB-78 | TwoSidedMaterial on an open cylinder, caps always drawn against honoured | 22.41 dB against 39.57 dB | C | same rig | receipts/TwoSidedMaterial.json |
| N-BAB-79 | LocalFog and FogCoordinate | 60.30 dB and 99 dB after two field events; FogCoordinate 43.55 dB twice | C | same rig | receipts/LocalFog.json, receipts/FogCoordinate.json |
| N-BAB-60 | GeoLOD, centre 50 m up, parent scale 1.9 and 2.1 | level 1 and level 0 | C | both engines | x3d.loom@c80cecd:x3d.webgpu/bridge/fixtures/GeoLOD.test.json |
| N-BAB-61 | hitGeoCoord longitude under a GeoLocation 3.3 m east of the origin | 8.4e-7 degrees (true: 3.0e-5) | C | X_ITE 16.6.0 and bridge | x3d.loom@c80cecd:x3d.webgpu/bridge/fixtures/GeoTouchSensor.test.json |
| N-BAB-62 | batch 46 fixture steps passed, ours and X_ITE alike | GeoLOD 92, GeoTouchSensor 51, GeoProximitySensor 64, GeoMetadata 30, EspduTransform 146, ReceiverPdu 69, SignalPdu 70, TransmitterPdu 82, DISEntityManager 30, DISEntityTypeMapping 43 | C | `run-tests.js` | x3d.loom@c80cecd:x3d.webgpu/bridge/fixtures |
| N-BAB-63 | batch 47 fixture steps passed, ours and X_ITE alike | CollisionSensor 36, CollisionSpace 34, Contact 30 | C | `run-tests.js` | x3d.loom@80388ce:x3d.webgpu/bridge/fixtures |
| N-BAB-64 | unit cube resting on a fixed ground, contacts kept | Bullet 2 of the 4 lower corners; bridge 4 | C | X_ITE 16.6.0, SwiftShader rig | x3d.loom@80388ce:x3d.webgpu/bridge/fixtures/CollisionSensor.test.json |
| N-BAB-65 | resting distance of a ball on the ground | X_ITE 3e-8; bridge up to 5 mm (slop) | C | both engines | WHY-physics-sensing-batch.md section 5 |
| N-BAB-66 | full regression after the shim fix and batch 47 | 142 picture fixtures and 45 event fixtures pass, in chunks of 8 | C | our engine, SwiftShader | x3d.loom@80388ce |
| N-BAB-80 | three.js bridge status, batch 5 | drawn 98, reader-checked 32, reader 41, todo 66, upstream 23 | C | `driver.py status` | x3d.loom@1192dd4:x3d.threejs/bridge/NODES.json |
| N-BAB-81 | all compared pictures after batch 5 | 116 pictures; IoU 0.65 to 1.00; PSNR 19.21 to 99 dB, median 53.67; 25 at 99 dB | C | `X_ITE 16.6.0`, Chromium 153.0.8010.12 SwiftShader, three.js r187 | x3d.loom@1192dd4:x3d.threejs/bridge/receipts/* |
| N-BAB-82 | cube-map pictures | ImageCubeMapTexture 31.45 and 31.98 dB; ComposedCubeMapTexture 29.12; GeneratedCubeMapTexture 34.03 (IoU 0.94 and 0.98) | C | same rig | receipts/*CubeMapTexture.json |
| N-BAB-83 | ComposedShader pictures | 40.47 and 39.75 dB, IoU 1.00; with the `#version` line left in IoU 0 (mad 21.87 and 18.17) | C | same rig | receipts/ComposedShader.json, D-BAB-72 |
| N-BAB-84 | Text against X_ITE's glyph renderer | IoU 0.65, 19.21 dB (the boxes match to the pixel) | C | same rig | receipts/Text.json |
| N-BAB-85 | CAD nodes, four fixtures of one scene | IoU 0.99; 54.88, 51.22, 51.21 and 53.67 dB | C | same rig | receipts/CAD*.json |
| N-BAB-86 | Geo fixture steps passed, ours and X_ITE alike | GeoViewpoint 98 and 96, GeoLOD 92, GeoElevationGrid 64, GeoProximitySensor 64, GeoTouchSensor 51, GeoTransform 34, GeoLocation 22 and 19, GeoOrigin 22, GeoCoordinate 16 | C | same rig | receipts/Geo*.json |
| N-BAB-87 | review of batch 4 | 171 agents, 83 raw findings, 69 survived two skeptics (10 high, 36 medium, 23 low); by lens 16 regression, 15 pointer, 15 input, 12 cube and shader, 11 Inline and Text | C | workflow run 2026-11-15 | x3d.loom pull request #70 |
| N-BAB-88 | GeoViewpoint frame, right basis against swapped | IoU 1.00 and 64.48 dB against IoU 0 and 18.49 dB (the batch-46 fixture: 98 of 98 either way) | C | same rig | receipts/GeoViewpointFrame.json |
| N-BAB-89 | GeoLocation with the matrix transposed (D-BAB-73) | 9 of 22 steps fail; the position reads 0 0 0 where 6378137 0 0 is expected | C | same rig | receipts/GeoLocation.json |
| N-BAB-95 | Layer, LayerSet, Layout, LayoutGroup, LayoutLayer, ScreenGroup, ScreenFontStyle, Viewport against X_ITE | 8 of 8 pass; 12 pictures IoU 1.00 at 99 dB (Layout 3, LayoutLayer 2, ScreenGroup 3, Viewport 4) | C | Chromium 153.0.8010.12 SwiftShader, X_ITE 16.6.0, three.js r187 | receipts/Layout.json |
| N-BAB-96 | LayerSet with the Background left on every pass (D-BAB-75) | 4 of 86 steps fail; red world box missing | C | same rig | receipts/LayerSet.json |
| N-BAB-97 | LayerHeadlight, headlight shot | IoU 0.90, 16.66 dB: the lit boxes differ in extent, the pixel probes agree | C | same rig | receipts/LayerHeadlight.json |
| N-BAB-98 | ViewportMany, ten tiles | IoU 0.98, 26.27 dB, 12 of 12 steps | C | same rig | receipts/ViewportMany.json |
| N-BAB-99 | three.js bridge status, batch 7 | drawn 130, reader-checked 34, reader 41, todo 32, upstream 23; 132 of 132 fixtures pass | C | `driver.py check` over all fixtures | x3d.loom@9f969d2:x3d.threejs/bridge/NODES.json |
| N-BAB-100 | TextureProjector and TextureProjectorParallel base picture | IoU 1.00, 60.14 and 59.54 dB; 99 of 99 and 96 of 96 steps | C | SwiftShader, 320 x 240 | receipts/TextureProjector.json |
| N-BAB-101 | HAnimHumanoid and HAnimDisplacer rest picture | IoU 1.00, 60.56 and 60.21 dB; 17 of 17 and 37 of 37 steps | C | same rig | receipts/HAnimHumanoid.json |
| N-BAB-102 | ParticleSystem cone cloud against X_ITE | bbox within 5 px, drawn pixels 2764 and 2626, IoU 0.57, 18.2 dB | C | same rig | receipts/ParticleSystem.json |
| N-BAB-103 | Texturing3D main pictures (Pixel, Composed, Image) | IoU 1.00; 38.57, 31.13 and 99 dB | C | same rig | receipts/PixelTexture3D.json |
| N-BAB-104 | Bounds tree against plain raycast, 125,000-triangle ElevationGrid | 33 times faster per pick; same point on 23 of 23 rays | C | Chromium 153.0.8010.12, SwiftShader, three-mesh-bvh 0.9.18 | docs/demos/three-bvh/v1 (x3d.demo) |
| N-BAB-105 | 1,000,000 triangles: tree build, one pick, 24,000-ray scan | about 0.5 s, about 0.1 ms, about 110 ms | C | same rig | docs/demos/three-bvh/v1 (x3d.demo) |
| N-BAB-106 | Full fixture sweep of the three.js body after batch 8 | 132 of 132 (127 scene, 5 events) | C | same rig | x3d.threejs/bridge/tools/run-tests.js |
| N-BAB-90 | Disk2D, Rectangle2D, Extrusion silhouette overlap with X_ITE | 0.98, 0.97, 0.93 | C | SwiftShader, 320 x 240 | x3d.loom@cd71796:x3d.webgpu/bridge/receipts |
| N-BAB-91 | PointProperties default pointSizeMin, scale, max | 1, 1, 1 in the standard and X_ITE; hall default was 0 | C | X_ITE 16.6.0 | PointProperties.test.json |
| N-BAB-92 | NurbsTextureCoordinate uv step with centre weight 3, 8 cells | 0.125 in X_ITE (regular); rational form would give 0.114 | C | X_ITE 16.6.0 | NurbsTextureCoordinate.test.json |
| N-BAB-93 | NurbsSweptSurface triangles, octagon along a bend and triangle along an arc | 160 and 36, equal in both engines | C | both engines | NurbsSweptSurface.test.json |
| N-BAB-94 | NurbsTrimmedSurface untrimmed 8 x 8 patch triangles | 128 in both engines | C | both engines | NurbsTrimmedSurface.test.json |

## Sources and provenance

- `x3d.loom@162ab18` (read 2026-11-14): `x3d.webgpu/{README,STATE,PATHS,BABYLON,BENCHMARK,SPEC}.md`, the four playbook files, `bridge/` (tracker, assessment, batches 01 to 26, tools, src, fixtures, receipts), `demo/src/`, `runs/webgpu-*/`. Re-run: census, driver status, tests, hash keys, greps. `x3d.loom@60824ce` extracted with `git archive` (D-BAB-2).
- `x3d.demo@d10b457`: `CHANGELOG.md` (append-only rule), `docs/index.html` (blocklist text), `docs/demos/SOURCES.md`, every `.x3d` for D-BAB-5. `x3d.docs@f172f67`: `docs/vendor/x_ite/x_ite.min.js` (grep, section 2); chapters [06](06-xite-the-oracle.md) and [02](02-loom-laws.md); [the Loom masterclass](../x3d.loom/MASTERCLASS.md) for the AST view of the same repository, not duplicated here.
- `x3d.loom@4887a98` (batch 44, read and run 2026-11-14): `x3d.webgpu/bridge/{BATCH-44.md,WHY-nurbs-batch.md,knowledge/NURBS-FINDINGS.md,src/nurbs.js,src/nodes/Nurbs*.js,fixtures/Nurbs*,receipts/Nurbs*}`.
- `x3d.loom@108a282` (scaffold, read and run 2026-11-14): `x3d.threejs/bridge/{README.md,ESTIMATE.md,src/body-three.js,tools/*,fixtures/*,receipts/*,NODES.json}`; the Babylon files it reads at bundle time are those of `x3d.loom@ed1bed8`.
- `x3d.loom@95eda37` (batch 1, read and run 2026-11-14): `x3d.threejs/bridge/{src/body-three.js,fixtures/{PointLight,PointLightAttenuation,SpotLight,Fog,PixelTexture,ImageTexture,TextureTransform,TexturedPrimitives}.*,receipts/*}`; X_ITE formulas read in `x_ite.js` 16.6.0 (`Fog2.glsl`, `TextureTransform`, `QuadSphereOptions`, `CylinderOptions`).
- `x3d.loom@38530ab` (batch 2, read and run 2026-11-14): `x3d.threejs/bridge/{src/body-three.js,src/nodes/Geometry.js,tools/tooling.test.js,fixtures/*,receipts/*}`; X_ITE 16.6.0 read for the ElevationGrid and line behaviour only through renders.
- `x3d.loom@72a4bca` (batch 3, read and run 2026-11-15): `x3d.threejs/bridge/{src/body-three.js,src/nodes/{Textures,Fog,Background}.js,tools/{bundle.js,run-tests.js,tooling.test.js},fixtures/*,receipts/*}`; X_ITE 16.6.0 read for nothing new (every rule here is a measurement against it); the MFColor converter patch is in `tools/run-tests.js`.
- `x3d.loom@c80cecd` and `@80388ce` (batches 46 and 47, read and run 2026-11-15): `x3d.webgpu/bridge/{BATCH-46.md,BATCH-47.md,WHY-geo-dis-batch.md,WHY-physics-sensing-batch.md,src/nodes/{GeoLOD,GeoTouchSensor,GeoProximitySensor,GeoMetadata,CollisionSensor,CollisionSpace,Contact,RigidBodyCollection}.js,fixtures/*,receipts/*}`; X_ITE 16.6.0 read for each node's runtime behaviour.
- `x3d.loom@a6e3d31` (batch 4, merged at `7f6496b`) and `x3d.loom@1192dd4` (batch 5, pull request #70, read and run 2026-11-15): `x3d.threejs/bridge/{src/body-three.js,src/nodes/{CubeMaps,Pointing,Shaders,Text,Geo,CAD,Textures}.js,fixtures/*,receipts/*,NODES.json}`; the review workflow's result (69 findings) is summarised in 14.8, its journal is not reproduced.
- Private-source gap: a private primer of 8 November and private notes on each port were pointers only. Figures here were re-derived from the repository or read from a named receipt; the rest are graded [S] or [L] and labelled carried. No private document, link, identifier or chat wording is reproduced.
- Siblings: [01](01-the-tether.md), [03](03-validator-and-gates.md), [04](04-mcp-for-agents.md), [07](07-xray.md), [09](09-castle-engine.md), [11](11-gltf-usd-khronos.md), [13](13-physics.md).
