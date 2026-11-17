# 06. X_ITE, the reference renderer

> **Say it:** X_ITE is the second program that tells you what a scene draws and what its events do, and it is a good oracle only when you name its patch, its browser and its options, drive it with guarded code, and remember that it is a renderer with its own extensions, not a validator. **[C]**

| field | value |
|---|---|
| chapter code | `XIT` |
| prerequisites | [01 The tether](01-the-tether.md) for the loop; [03 The validator and the gates](03-validator-and-gates.md) for what runs before the renderer |
| after this you can | (1) say what "X_ITE supports 266 of 267 nodes" means and re-count it; (2) drive X_ITE by DOM and SAI, read events, and pick; (3) write a render claim that a stranger can re-run, and spot the three samplers that lie; (4) reproduce the hosted-page black draw and its fix; (5) build a parity harness with X_ITE as the reference and list where it is not the truth |
| sources read | x_ite npm tarballs 16.4.3, 16.5.0, 16.5.1, 16.6.0, 16.6.1, 16.7.0, 16.7.1 (unpacked, `dist/` read, executed in Chromium); x3d.docs@f172f67:docs/x_ite/MASTERCLASS.md, docs/tools-shared/xite_*.py, docs/vendor/x_ite/; x3d.loom@162ab18:LOOM-v1.md, kit/loomkit/pagetraps.py, x3d.webgpu/STATE.md, x3d.webgpu/BENCHMARK.md; x3d.demo@d10b457:docs/demos/*/*/x_ite.min.js; x3d_mcp@b4efcd3:src/validation/ |
| instruments used | `X_ITE 16.7.0` (and six other patches, named per row), `Chromium 153 (Chrome for Testing 153.0.8010.12), SwiftShader`, Playwright 1.63.0, Node 22.23.4; `x3d_mcp fork b4efcd3`, `X3D XSD 4.0` (sha256 0509fa5bd601), `X3D XSD 4.1` (sha256 1a7935caa7e6), `X3DUOM 4.1` (sha256 4fc10e8e15c0); lxml 6.1.3; Python 3.13.18; npm 10.9.9; software GL only, no GPU |

Rig for every number marked **[C]** below unless a row says otherwise: the unmodified npm tarball of the named X_ITE patch, served over loopback http, loaded in headless Chromium 153 (Chrome for Testing 153.0.8010.12) with `--use-gl=angle --use-angle=swiftshader`, a 320 x 240 `<x3d-canvas>`, run on 2026-11-14. `X_ITE 16.7.0` is the patch the repository vendors: `x_ite.min.js` there is byte-identical to the npm tarball (sha256 `b7df063e8cb1`, 1,306,961 B) and so is `x_ite.css` (sha256 `e8af335cd9e4`) [C]. The source repositories were read-only; every script and result lived in a scratch folder.

## 1. The map

```text
  scene.x3d (text: DEF/USE, ROUTE, fields)
      |
      |   validator rungs R0-R5 (chapter 03): legal? consistent? repaired?
      v
  +-----------------------------------------------------------------------------+
  |  X_ITE   one npm package, one JavaScript bundle, WebGL2 only                |
  |                                                                             |
  |   parse    XML, VRML, JSON, GLB, glTF, OBJ, PLY, STL, SVG   -> scene graph    |
  |   run      ROUTEs, TimeSensor, interpolators, Script, physics -> events      |
  |   draw     shadow pass, main pass (MSAA), OIT, tone map       -> pixels       |
  |   pick     GPU picking buffer                                 -> sensor events|
  +-----------------------------------------------------------------------------+
      |               |                 |                    |
      v               v                 v                    v
   pixels         event counts      field values        console text
   (rung R6)      (callbacks)       (SAI reads)         "Unknown node type ..."
      |
      v
  a render claim = scene hash + X_ITE patch + browser + GL backend + options + metric
```

| question | who answers it | X_ITE's role |
|---|---|---|
| is the file legal XML, XSD and spec-consistent | validator, rungs R0 to R5 | none: X_ITE parsed and drew all 5 invalid or inconsistent scenes of section 7 |
| does the file draw something | X_ITE plus a pixel metric | the only rung that sees "blank" |
| do events flow, does a sensor fire | X_ITE plus callbacks | the runtime that executes ROUTEs and picking |
| is the picture correct (colour, light, blend) | a person, or a second renderer | a reference with extensions, not the standard |
| is the claim reproducible | the claim itself | it must name patch, rig and options |

**In scope:** X_ITE as a program you drive and measure (patch, nodes, API, picking, splats, events), how to write and read a render claim, the two traps that waste the most time (hosted-page black draw, sampler lies), X_ITE as the reference arm of a parity harness, and where it is not the truth. **Out of scope:** the AST teardown ([the X_ITE masterclass](../x_ite/MASTERCLASS.md), linked, not repeated), the Babylon port ([08](08-babylon-bridge.md)), glTF and USD ([11](11-gltf-usd-khronos.md)), physics ([13](13-physics.md)).

**Read next:** deeper, [the X_ITE masterclass](../x_ite/MASTERCLASS.md) (module-level anatomy and the 32-step reading curriculum); wider, [07 x3d.xray](07-xray.md) for a method that turns a code base into a gated scene, with X_ITE as its viewer.

## 2. What X_ITE is, and what was measured about it

X_ITE is a JavaScript X3D browser published to npm as `x_ite` by one maintainer account, under the MIT licence. The teardown in the masterclass read the code of one patch and said so: it did not read commit history, maintainers or release cadence. The rows below separate what each source measured.

| property | value | grade | instrument | source |
|---|---|---|---|---|
| graphics API | WebGL2 only: 1 `getContext ("webgl2")` line, 0 hits for "webgpu" or "navigator.gpu" in `x_ite.js` plus the component bundles | C | `X_ITE 16.7.0`, grep over unminified `dist/` | npm tarball `x_ite@16.7.0` |
| npm maintainers | 1 | C | npm 10.9.9, `npm view x_ite maintainers`, 2026-11-14 | npm registry |
| npm versions, all time | 306 (first 4.0.2 on 2017-08-29, latest 16.7.1 on 2026-11-08) | C | npm 10.9.9, `npm view x_ite time` | npm registry |
| 16.x line | 23 releases from 2026-07-27 (16.0.0) to 2026-11-08 (16.7.1); gaps median 5.7 days, mean 4.7, max 12.9 | C | same | npm registry |
| releases in the 365 days to 2026-11-14 | 68 | C | same | npm registry |
| size | `x_ite.min.js` 1,306,961 B; 280,795 B at `gzip -9`; `assets/components` 9,800,769 B | C | `wc`, `gzip -9` on the tarball | `x_ite@16.7.0` |
| registered components | 39 | C | `browser.supportedComponents.length` in Chromium 153 | `X_ITE 16.4.3`, `16.5.1`, `16.6.1`, `16.7.0`, `16.7.1`: 39 on all five |
| source modules (webpack markers) | 752 in 24 bundles, 730 of them X_ITE's own `src/` | C | marker scan of `dist/x_ite.js` and 23 component bundles | `X_ITE 16.4.3` to `16.7.0` (752 on every patch, 730 own); 762 and 732 on `16.7.1` |
| the teardown's anatomy (98,369 lines, 5,940 functions, 194 field-exact nodes) | as stated | L | read in the masterclass; its data files are not in the public repo, so not re-run | x3d.docs@f172f67:docs/x_ite/MASTERCLASS.md |

Read the cadence rows as a risk statement, not a verdict: a patch that is 5.7 days old in the median means a claim about "X_ITE" without a patch number is stale within a week (section 8). Whether the author is one person in practice is not measured here; the registry lists one maintainer.

## 3. Coverage: 266 of 267, counted three ways

"X_ITE implements the standard" is three different counts. Each rung below is a different instrument and a different number; quote the rung with the number.

```text
  rung 1  a module exists and registers a name           294 names   (static scan, 16.7.0)
  rung 2  scene.createNode (name) succeeds at runtime    266 of 267  X3DUOM 4.1 concrete nodes
  rung 3  the node parses from XML in a versioned file   section 7 (BlendMode, GaussianSplats)
  rung 4  the node draws or behaves as the spec says     not measured per node here
  rung 5  the node is the same as in the other browser   not measured here (chapters 08, 09)
```

| count | value | grade | instrument | note |
|---|---|---|---|---|
| X3DUOM 4.1 concrete nodes | 267 | C | `X3DUOM 4.1` (sha256 4fc10e8e15c0), ElementTree over `ConcreteNodes` | the denominator |
| `createNode` succeeds | 266 | C | `X_ITE 16.7.0`, Chromium 153, after `loadComponents (getProfile ("Full"))` | same 266 on 16.4.3, 16.5.1, 16.6.1, 16.7.0 and 16.7.1 |
| the one that fails | `ProtoInstance` ("Unknown node type") | C | same | it is syntax, not a node class: X_ITE implements it in its execution layer |
| names registered (`getStaticProperties`) | 294 at 16.7.0, 295 at 16.7.1 | C | regex over unminified `dist/` | the masterclass counts 292 concrete node modules, 26 of them X_ITE-only; this scan counts 28 not in X3DUOM 4.1, because it also counts `X3DBBoxNode`, `X3DImportedNodeInstance` and `X3DPrototypeInstance`; the two definitions are not reconciled |
| names in X3DUOM 4.1 | 266 of 294 | C | set intersection | the other 28 are X_ITE-only |
| spec deltas by field | 194 nodes field-exact, 43 add fields, 29 differ, 1 has no module | L | the masterclass (`xite_nodes.py`, regex over rebuilt source) | read, not re-run |

The 28 X_ITE-only names at 16.7.0 are four families (13 + 6 + 6 + 3): glTF material extensions (`SheenMaterialExtension`, `ClearcoatMaterialExtension` and 11 more), the Annotation family (6), rendering state (`BlendMode`, `DepthMode`, `InstancedShape`, `ImageTextureAtlas`, `SpecularGlossinessMaterial`, `GaussianSplatsShape`) and internal bases (`X3DBBoxNode`, `X3DImportedNodeInstance`, `X3DPrototypeInstance`). 16.7.1 adds `BehaviorEngine`.

**What "supported" hides.** A registered name can still be a stub. The field guide behind the masterclass recorded 13 silent stubs on 16.4.3 and 16.5.0 (6 DIS, `MotorJoint`, `UniversalJoint`, 3 shader containers, 2 Stream audio nodes), read from `x3d.webgpu/STATE.md` as a carried figure: grade **[L]**, not re-run here on 16.7.0. And "the component is registered" is not "the component level is enforced": a scene that names a profile it does not satisfy still loads (section 7).

## 4. Driving X_ITE

X_ITE exposes the same browser through three doors. The first two are the ones page code uses.

| door | entry | what you do there | verified here |
|---|---|---|---|
| DOM | `<x3d-canvas src="scene.x3d">`; attributes `splashScreen`, `contextMenu`, `notifications`, `timings` | declarative: let the page load the world | attributes set to `"false"` in every harness here; the canvas has a shadow root and an inner `<canvas>` [C] |
| SAI | `X3D.getBrowser ()`, then `createX3DFromString`, `replaceWorld`, `loadURL (new X3D.MFString (url))`, `scene.getNamedNode ("DEF")`, `field.addFieldCallback (key, fn)` | imperative: read, write, listen | all of them used on 5 patches [C] |
| X3D tree | `scene.rootNodes`, `scene.routes`, `browser.supportedComponents`, `browser.getBrowserOption (name)`, `browser.getRenderingProperty (name)` | inspect and configure | read on 5 patches [C] |

A minimal driven page, copyable (serve it over http; `x_ite.min.js` loads its CSS, components and fonts relative to its own URL):

```html
<!doctype html><meta charset="utf-8">
<script src="vendor/x_ite/x_ite.min.js"></script>
<x3d-canvas id="c" style="width:320px;height:240px"
            splashScreen="false" contextMenu="false" notifications="false" timings="false"></x3d-canvas>
<script type="module">
  const b = X3D.getBrowser ();
  const scene = await b.createX3DFromString (`<?xml version="1.0"?>
    <X3D profile="Interchange" version="4.0"><Scene>
      <Viewpoint position="0 0 6"/>
      <Shape><Appearance><Material emissiveColor="1 0.2 0.1"/></Appearance><Box size="2 2 2"/></Shape>
    </Scene></X3D>`);
  await b.replaceWorld (scene);
</script>
```

### 4.1 Calls whose shape is a trap

| call | what is true on 16.5.1 and 16.7.x | grade | instrument |
|---|---|---|---|
| `field.addFieldCallback (key, fn)` | the key is the first argument; a callback registered with a fresh key coexists with others | C | `X_ITE 16.7.0`, `16.5.1`, `16.4.3`, section 4.4 test |
| `browser.currentTime` | `undefined`; use `browser.getCurrentTime ()` (a function) | C | `X_ITE 16.5.1`, `16.7.0`, `16.7.1`, `typeof` probe |
| `getField (name)` | present at runtime (`typeof` is `function`) and absent from `x_ite.d.ts`; a private note calls it deprecated | C for present and untyped, S for "deprecated" | `X_ITE 16.7.0`, `typeof` probe and grep of the typings |
| frame-end event | `browser.finishEvents ()` returns the field; `browser.endEvents` is `undefined` on 16.4.3 to 16.7.1 | C | `typeof` probe on 16.4.3, 16.5.1, 16.6.1, 16.7.0, 16.7.1 |
| clock for a `TimeSensor` `startTime` | page code must own time, because `Browser.currentTime` is not there to read | C for the missing property, L for the rule (Loom lessons) | as above |

### 4.2 Events and the one-exception freeze

X_ITE runs field callbacks inside its routing pass. One exception that escapes a callback stops the route it was on. Measured on a `TimeSensor` looping at 1 s feeding a `ScalarInterpolator`, with callback A on the sensor and callback B counting the interpolator's `value_changed`:

| case | B events per 500 ms over 3 s | A calls | page errors | patch |
|---|---|---|---|---|
| A guarded (try/catch inside) | 28 to 31 in every window | 180 to 183 | 0 | `16.5.1`, `16.7.0`, `16.7.1` |
| A throws on its first call | 0 in every window | 1 | 1 | `16.5.1`, `16.7.0`, `16.7.1` |

Grade **[C]**; instrument `X_ITE 16.5.1`, `16.7.0`, `16.7.1` in Chromium 153, SwiftShader, 2026-11-14 (method in D-XIT-6). The rule is in the kit as `xite-callback-unguarded`: the callback body must start with `try` (`x3d.loom@162ab18:kit/loomkit/pagetraps.py`). The loom recorded the same freeze on 16.5.1 as failure mode 88 and asked for the check to be re-run when a fixture patch is pinned; this is that re-run on 16.7.0 and 16.7.1: the behaviour is unchanged.

### 4.3 Picking

Picking is on the GPU. A shape with `pointerEvents` true is pickable, however faint, and it hides a sensor's shape behind it.

```xml
<Transform><TouchSensor DEF="TS"/>
  <Shape DEF="TARGET"><Appearance><Material emissiveColor="1 0.2 0.1"/></Appearance><Box size="2 2 2"/></Shape></Transform>
<Transform translation="0 0 1.5">
  <Shape DEF="HALO"><Appearance><Material emissiveColor="1 1 1" transparency="0.9"/></Appearance><Box size="1 1 0.1"/></Shape></Transform>
```

| step | `isOver` events | `touchTime` events | patch |
|---|---|---|---|
| click the box centre, halo pickable (default `pointerEvents` true) | 0 | 0 | `16.4.3`, `16.5.1`, `16.7.0` |
| set `HALO.pointerEvents = false` by SAI, click again | 1 | 1 | `16.4.3`, `16.5.1`, `16.7.0` |

Grade **[C]** (method in D-XIT-4). Two consequences. First, `Shape.pointerEvents` is an X_ITE field, not a standard one: `x3d_mcp fork b4efcd3` rejects `<Shape pointerEvents='false'>` under both XSD 4.0 and XSD 4.1 ("attribute 'pointerEvents' is not allowed") and `X3DUOM 4.1` lists 14 fields for `Shape`, none of them `pointerEvents` [C]. The only 4.1 element with a `pointerEvents` attribute is `GaussianSplats`. A private note said the opposite for `Shape`; the schemas and the validator say it is an extension, so set it by SAI after load and name the shape by DEF. Second, a private note says a `TouchSensor` needs `PointingDeviceSensor` level 1 declared on strict hosts; the harness used profile `Full`, so that point is **[S]**, not re-tested.

Viewpoint changes glide for one second by default (Loom failure mode 84): set `NavigationInfo.transitionType` to `TELEPORT` before a still or a pick test (`x3d.loom@162ab18:LOOM-v1.md`, read, not re-run). A picture or a pick taken inside the glide reads the old pose.

### 4.4 Splats

X_ITE 16.7.0 has two ways in. A `GaussianSplats` node carries its data in fields (`positions`, `opacities`, and the rest), and the GLB parser handles the `KHR_gaussian_splatting` extension (`x_ite.js` lines 42247 and 42266 in the unminified `16.7.0` bundle) [C, read]. Sorting runs in a module Worker created from a blob URL (`new Blob ([content], { type: "text/javascript" })` in `GaussianSplatsComponent.js`) whose body imports `mkkellogg-sort.worker.js` (1,798 B) next to a 2,093 B WebAssembly sorter; a strict host therefore needs `worker-src blob:`, `'wasm-unsafe-eval'` and the library path reachable [L: read in the component source, not tested under a policy]. Node defaults differ from the spec (`pointerEvents` and `castShadow` false on the node, true on `GaussianSplatsShape`; **[L]**, `x3d.loom@162ab18:x3d.webgpu/STATE.md`).

**The loading hang (public-safe part).** A private note from a 16.5.0 build says `loadURL` can hang when a splat node is frustum-culled before its first sort. This chapter could not confirm the mechanism: the component source at 16.4.3, 16.5.0 and 16.7.0 contains no load-count call (0 matches for `LoadCount`, `loadState`, `setLoadState` in `GaussianSplatsComponent.js`), and no hang test was run. Grade **[S]**, carried from a private note, not re-checked, and `STATE.md` in the loom repo grades it "S for 16.7.0" too. The defensive rule stands on its own and is [C] as a rule of the kit: give every world load a time budget and treat non-settlement as an error (`loadurl-unbudgeted`).

## 5. Writing and reading an honest render claim

A render claim has six parts. Drop any one and the claim cannot be re-run.

```text
  claim = ( scene sha256 , X_ITE patch + file sha256 , browser build , GL backend ,
            options set or left default , metric with its reference and threshold )

  "drew"   : fraction of pixels differing from the Background colour, 1.7520e-1, > floor 1e-2
  NOT      : "it rendered fine"
```

| part | what to record | how | example from this chapter |
|---|---|---|---|
| scene | sha256 of the exact bytes, plus the profile and version attributes | `sha256sum` | the five scenes of section 7 are in D-XIT-5 |
| X_ITE patch | the npm version and the sha256 of `x_ite.min.js` | `X3D.getBrowser ().version`; `sha256sum` | `16.7.0`, `b7df063e8cb1` |
| browser | name and full build | `navigator.userAgent`, or the launcher's version call | Chrome for Testing 153.0.8010.12 |
| GL backend | `SwiftShader` or the named GPU and driver | launch flags; `getRenderingProperty` | SwiftShader; `MaxLights` 8, `MaxTextureSize` 8192, `TextureUnits` 64, `MaxSamples` 4 |
| options | every `getBrowserOption` that affects colour | read after load | `ColorSpace LINEAR_WHEN_PHYSICAL_MATERIAL`, `ToneMapping NONE`, `DisplayColorSpace SRGB`, `Exposure 1`, `Multisampling 4`, `OrderIndependentTransparency false` |
| metric | what is compared with what, over how many frames, with what floor | write it down before the run | non-background fraction against the declared Background, last frame after settle, floor 1% |

The defaults above were identical on 16.4.3, 16.5.1, 16.6.1, 16.7.0 and 16.7.1 [C], which is itself a result: a claim made on 16.5.1 about colour is not invalidated by 16.7.1 on these options. It is invalidated by a scene that sets its own `ToneMapping`.

### 5.1 Three samplers that lie

A frame sampler is code that decides "drew" or "blank". Three variants fail on a scene whose Background is not black. Setup: three scenes with a mid-grey Background `0.2 0.2 0.2` (51/255): one box in view (`visible`), one shape with no geometry (`blank`), one box 40 m behind the camera (`offcamera`). Frame log from `finishEvents`, with the fraction of pixels more than 24/765 away from (51, 51, 51):

| scene | frames in the first 2.5 s | first two frames | later frames | screenshot, 3 s later |
|---|---|---|---|---|
| `visible` | 7 (last at 311 ms) | 1.0000, 1.0000 | 0.1752 on every one | 0.1752 |
| `blank` | 6 or 7 (last at about 121 to 130 ms) | 1.0000, 1.0000 | 0.0000 on every one | 0.0000 |
| `offcamera` | 6 (last at about 125 to 147 ms) | 1.0000, 1.0000 | 0.0000 on every one | 0.0000 |

Grade **[C]**, `X_ITE 16.7.0`, Chromium 153, SwiftShader, 320 x 240 (method in D-XIT-2); the same pattern on 16.4.3, 16.5.1, 16.6.1 and 16.7.1, where the late-frame fractions are 0.1752 and 0.0000 on all five patches.

| sampler | reads | verdict on `blank` | why it fails |
|---|---|---|---|
| maximum over the first N frames | 1.0000 | "drew" (wrong) | the first two frames are cleared to black, which differs from the grey Background by 100% |
| a single sample at a fixed delay | depends on the delay | right or wrong by timing | on-demand rendering: the frame count and times vary per patch and per run |
| non-background fraction of a screenshot of the host element | 1.0000 if the element is hidden | "drew" (wrong) | in the hosted-page trap of section 6 the canvas is 0 x 0 and the clip is the white page, not the scene |
| last frame after settle, with the canvas size checked | 0.0000 | "blank" (right) | the rule the harness uses |

So the honest sampler is: register the frame watcher before the load, discard frames until the draw has settled (two consecutive frames within a stated tolerance, or a fixed number of frames), read the last frame, and require the canvas to be non-empty. The private note said the same in other words: "no frame" is a timing artefact, and the first frames after `replaceWorld` can be stale; the fraction-against-Background formulation here adds the explicit failure of the maximum rule.

**Frame counts are not stable facts.** A private note recorded about 4 frames for an empty scene and about 64 for a drawing one on 16.5.0; here a one-box scene gave 5 to 7 frames in 2.5 s either way. Quote a frame count only with the scene, rig and patch, and never a frame rate from software GL.

### 5.2 Writing the claim

A claim that passes the template:

> Scene `visible.x3d` (sha256 prefix recorded in the receipt) drew 17.52% non-background pixels at 320 x 240 on `X_ITE 16.7.0` (`x_ite.min.js` sha256 `b7df063e8cb1`), Chrome for Testing 153.0.8010.12, SwiftShader, default browser options, last frame after settle, against Background 0.2 0.2 0.2, floor 1%. Not measured: colour correctness, frame rate, other browsers.

A claim that fails it: "renders fine in X_ITE". It names no patch, no rig, no metric and no floor.

The weak forms fail by omission: "X_ITE draws it" names no patch, rig or metric; "drew on X_ITE 16.7.0" lacks browser, backend, options and metric; "17.5% non-background on X_ITE 16.7.0, Chromium 153 SwiftShader" lacks the scene hash, options and floor.

## 6. The traps that cost the most

### 6.1 The hosted-page black draw

Symptom: the page script runs, buttons work, the 3D view is black or empty. Cause (read at `x_ite.js` lines 54801 to 54822 in `16.7.0`): X_ITE creates a `<link rel="stylesheet">` in its shadow root, with a `crossOrigin` of "anonymous" and, in production builds, an `integrity` attribute, and it sets `.x_ite-private-browser` to `display: none` until that link loads. If the page's content-security policy blocks stylesheets from the host that serves `x_ite.css`, the `onerror` handler rejects, nothing ever unhides the surface, and the inner canvas stays 1 x 1.

```text
   page CSP:  style-src  fonts.googleapis.com  'unsafe-inline'      (no 'self', no CDN)
        |
        v
   <link rel=stylesheet href=".../x_ite.css">  --blocked-->  onerror -> promise rejects
        |                                                       |
        |  .x_ite-private-browser { display:none }  <-----------+   never reset
        v
   canvas 1 x 1 px, CSS box 0 x 0, host element renders as an empty box
```

Reproduced under an emulated policy (`default-src 'none'; script-src 'self' 'unsafe-eval' 'wasm-unsafe-eval'; style-src https://fonts.googleapis.com 'unsafe-inline'; connect-src 'self'; img-src 'self' data: blob:; font-src https://fonts.gstatic.com; worker-src blob:`):

| case | `.x_ite-private-browser` display | canvas (CSS px / drawing buffer) | non-background fraction | patch |
|---|---|---|---|---|
| no policy | block | 320 x 240 / 320 x 240 | 0.1752 | `16.5.1`, `16.7.0` |
| policy, stylesheet blocked | none | 0 x 0 / 1 x 1 | 1.0000 (white page, see 5.1) | `16.5.1`, `16.7.0` |
| policy, with the fix below | block | 320 x 240 / 320 x 240 | 0.1752 | `16.5.1`, `16.7.0` |

Grade **[C]** (D-XIT-3). The fix, public and mechanical: read the stylesheet text into the page (a `<script type="text/x-css">` block is permitted by many policies; strip `@font-face` and `url(...)`), adopt it into the canvas's shadow root with `new CSSStyleSheet ().replaceSync (css)` and `shadowRoot.adoptedStyleSheets`, then set `.x_ite-private-browser` `style.display = ""`. Doing this once, before the world loads, was enough in this test; a private note says to repeat it for a few seconds and after each `loadURL`, which this chapter did not test **[S]**. The same trap is recorded in the Loom as failure mode 116 on 16.5.1 ("X_ITE drew black on a hosted page: the policy blocked its CDN stylesheet"), with the same fix. Related: a strict policy also blocks the PT Sans interface fonts (a console message, harmless for the canvas), and X_ITE needs `'unsafe-eval'` for its `new Function` sites and `'wasm-unsafe-eval'` for its three WASM modules; a loose scan of `dist/` found 12 `new Function` lines where `STATE.md` counts 9 under a stricter regex, so quote neither as an audit.

Two more traps from the same family are read in `x3d.loom@162ab18:LOOM-v1.md`, not re-run: a host that refuses `.x3d` as a served extension (serve `application/xml`, strip a DOCTYPE the host refuses, re-validate the stripped copy), and a hidden pane or tab, where X_ITE does not start because animation frames are throttled (failure mode 101).

Two more traps are covered earlier: stale and early frames (section 5.1; swap in an empty world or use a fresh page per scene) and a callback that throws (section 4.2). Both, and `xite-browser-currenttime`, `nav-before-scene`, `window-global-shadow`, `js-syntax` and `loadurl-unbudgeted`, are static rules in `kit/loomkit/pagetraps.py`; run them before a browser is started.

## 7. Where X_ITE is not the truth

X_ITE is a renderer with its own extensions and its own tolerances. A scene that draws in X_ITE can be invalid, inconsistent or non-portable. Five scenes, each parsed and drawn by `X_ITE 16.7.0` and judged by `x3d_mcp fork b4efcd3` in the same run:

| scene | X_ITE 16.7.0 | `x3d_mcp fork b4efcd3` | what it shows |
|---|---|---|---|
| `profile="Core"` that uses `Viewpoint`, `Shape`, `Box` | parses, draws 0.1752, no warning | XSD valid; semantic layer `profile-component` errors (3 shown) | the browser does not enforce profile or component levels |
| `GaussianSplats` in a `version="4.0"` file | logs "Unknown node type 'GaussianSplats'", the rest draws (0.1752) | XSD 4.0 invalid ("not expected") | X_ITE gates a 4.1 node by file version |
| the same node in `version="4.1"` | parses, 3 root nodes | XSD 4.1 valid | version attribute, not content, decides |
| ROUTE written before the DEF it names | warns "Unknown named or imported node 'T'", `scene.routes.length` 0, the scene draws (0.1752) | semantic `route-before-def` error (2) | the browser drops the ROUTE silently; the animation never runs |
| same ROUTE after the DEFs | `scene.routes.length` 1 | clean | order matters to X_ITE, not to the XSD |
| `BlendMode` in `Appearance`, no component line | logs "Unknown node type 'BlendMode' ... insufficient component/profile statements", the node is dropped, draws (0.1752) | XSD invalid ("not expected") | an extension node needs its component |
| `BlendMode` with `<component name="X_ITE" level="1"/>` | parses, no log, 2 root nodes | XSD invalid twice: the element, and the component name `X_ITE` is not in the 4.0 enumeration | extension content cannot pass the standard schema |

Grade **[C]** (D-XIT-5). Reading it: the draw metric reads 0.1752 on all seven rows; five of them are invalid or inconsistent, and in three of those five something was dropped without a failure (a `GaussianSplats` node in a 4.0 file, a `BlendMode` node without its component, a ROUTE before its DEF). The validator rungs and the renderer answer different questions, and neither can replace the other. This is the reason the tether has both ([01 The tether](01-the-tether.md)) and why the ROUTE-before-DEF rule exists in the fork ([03 The validator and the gates](03-validator-and-gates.md)).

### 7.1 Extensions and renderer choices that are not in the standard

| item | in X_ITE | in the standard | grade | instrument |
|---|---|---|---|---|
| `Shape.pointerEvents` | field, default true | not in `X3DUOM 4.1` `Shape`; XSD 4.0 and 4.1 reject the attribute | C | `x3d_mcp fork b4efcd3`; `X3DUOM 4.1` |
| `Appearance.blendMode`, `depthMode` | fields; `BlendMode`, `DepthMode` nodes in component `X_ITE` | absent from X3DUOM 4.1; X_ITE ships its own `dist/X3DUOM.xml`, an extension of the 4.0 model with 32 `ConcreteNode` entries (`STATE.md` counts 17 of them as new) | C | `X_ITE 16.7.0` `dist/X3DUOM.xml`; section 7 |
| light model | shadow fields on six light nodes (`shadowBias`, `shadowColor`, `shadowMapSize`); a light at intensity 0 is dropped but its ambient term is not (Loom failure mode 110) | spec lights have no shadow fields | L for the 110 row (read, not re-run); C for the added fields (masterclass H3 table, read) | `x3d.loom@162ab18:LOOM-v1.md`; masterclass |
| transparency blending | translucency blended in display space; a three.js reader blends in linear (Loom failure mode 115: outline overlap 0.855 and 0.778 with identical geometry) | the spec's lighting model is silent on the colour space of blending | L | `x3d.loom@162ab18:LOOM-v1.md`, read, not re-run |
| colour management | `ColorSpace` default `LINEAR_WHEN_PHYSICAL_MATERIAL`, `DisplayColorSpace` `SRGB`, `ToneMapping` `NONE`, `Exposure` 1; options include 3 ACES variants and `KHR_PBR_NEUTRAL` | the standard does not define a tone-map or display colour space option | C for defaults on 5 patches | `X_ITE 16.4.3` to `16.7.1`, `getBrowserOption` |

The first row is the cleanest worked example of the thesis. An AI that "fixes" a picking problem by writing `pointerEvents='false'` into the file makes the file invalid; the validator names the attribute, the rung that sees a wrong attribute is not the renderer. The right fix is in the page: name the shape by DEF and set the field after load.

## 8. Versions, and what changed between them

Every number in this table is **[C]**, `x_ite` npm tarballs unpacked and run in Chromium 153, SwiftShader, 2026-11-14.

| patch | npm date | `x_ite.min.js` B | modules | node names | `createNode` of 267 | changes read from the module and name sets |
|---|---|---|---|---|---|---|
| 16.4.3 | 2026-10-05 | 1,306,369 | 752 | 294 | 266 | baseline |
| 16.5.0 | 2026-10-11 | 1,305,750 | 752 | 294 | not run | `X3DImportedNodeProxy` replaced by `X3DImportedNodeInstance` |
| 16.5.1 | 2026-10-13 | 1,306,526 | 752 | 294 | 266 | none in names or modules |
| 16.6.0 | 2026-10-21 | 1,306,147 | 752 | 294 | not run | none |
| 16.6.1 | 2026-10-27 | 1,306,129 | 752 | 294 | 266 | none |
| 16.7.0 | 2026-10-31 | 1,306,961 | 752 | 294 | 266 | `GLB2Parser` renamed `GLBParser` |
| 16.7.1 | 2026-11-08 | 1,310,785 | 762 | 295 | 266 | +10 modules: `BehaviorEngine` node, `GLTFPointerAliases`, the Khronos glTF interactivity engine and `gl-matrix` as bundled dependencies |

Across all seven patches: 39 components, the same browser option defaults (section 5), the same 0.1752 and 0.0000 on the draw test, the same picking and callback behaviour on the three patches tried. In the 34 days from 16.4.3 (2026-10-05) to 16.7.1 (2026-11-08) the registry lists 6 further releases, and the measured surface moved by two renames (one node class, one parser) and one addition (10 modules, 1 node). The practical lesson is the converse of the cadence number: churn at the API and defaults level is low in this window, but a pinned patch still has to be named because the bundle changes every release.

**Vendored patches in the public repositories are not one version.** `x3d.demo@d10b457` carries 20 vendored `x_ite.min.js` files: 1 at 16.4.3, 13 at 16.5.1, 5 at 16.6.0 and 1 at 16.7.0 (from each file's banner), and 29 HTML pages reference it [C]; "renders in X_ITE" there is four programs. `x3d_mcp@b4efcd3` pins `npm install x_ite@16.4.3` in its README, `x3d.xray@8fa6845` vendors 16.7.0, and the Loom's lessons file lists 16.5.0, 16.5.1, 16.6.1 and 16.7.0 across deliveries with the instruction to pin one and re-run the callback-freeze test on it (`x3d.loom@162ab18:LESSONS-v1.0.md`, line 149). The masterclass header says 16.7.0 and that lessons file says 16.6.1 for the same teardown; module counts are equal on both (752 and 730), so the anatomy holds for either.

## 9. The learning heuristics and the curriculum

The masterclass turns X_ITE's structure into eight heuristics (H1 to H8) and a 32-step reading path, generated by `tools-shared/xite_learn.py` from an AST of the rebuilt source: each webpack bundle keeps `;// ./src/<path>` markers, and splitting there gives back the module tree. This chapter re-ran the split on seven patches and re-derived H7; the other inputs live in data files that are not in the public repository, so they are read, not re-run.

| heuristic | what it ranks | how it is computed | one value from the teardown | re-derived here |
|---|---|---|---|---|
| H1 keystone | modules everything leans on, short | PageRank over module-use edges divided by square root of lines | `Namespace`: 721 dependents, 19 lines | not re-run; marker scan gives 16 code lines and 25 raw lines for `Namespace.js` |
| H2 leverage | abstract types unlocking most concrete nodes per 100 lines | concrete descendants / lines of the abstract module | `X3DAppearanceChildNode`: 30 nodes, 19 lines, 150 per 100 | not re-run |
| H3 spec deltas | where the renderer knows more than the spec | field-by-field difference to X3DUOM 4.1 | most added: `shadowBias` (6), `shadowColor` (6), `shadowMapSize` (6), `tangent` (5) | `Appearance` has `blendMode` and `depthMode` in its module: yes |
| H4 surprise, H5 twins, H6 temperament | machinery behind few fields (`StaticGroup`: 6 fields, 830 lines); nodes built alike (`PointLight`, `SpotLight`); data, event-driven, engine or sensor (192, 43, 30, 25) | log-log residual, Jaccard at least 0.8, event-field share | as stated | not re-run |
| H7 locus | where a component's behaviour lives | lines in `Components/<C>` vs `Browser/<C>` | `GaussianSplats` 83% in the browser machinery | yes, within one point (below) |

H7 re-derived on the unminified `16.7.0` bundles (share of lines in `Browser/<C>` over nodes plus browser, raw marker-to-marker lines and code lines with blanks and comments removed; teardown value last):

| component | node lines (raw / code) | browser lines (raw / code) | share raw / code | teardown |
|---|---|---|---|---|
| WebXR | 0 / 0 | 679 / 472 | 100% / 100% | 100% |
| GaussianSplats | 163 / 115 | 792 / 561 | 83% / 83% | 83% |
| Text | 555 / 390 | 1,169 / 876 | 68% / 69% | 68% |
| Texturing3D | 1,166 / 896 | 1,496 / 1,217 | 56% / 58% | 58% |
| Navigation | 2,148 / 1,677 | 2,922 / 2,099 | 58% / 56% | 56% |
| Shape | 2,720 / 2,155 | 218 / 170 | 7% / 7% | 7% |
| RigidBodyPhysics | 3,261 / 2,493 | 20 / 15 | 1% / 1% | 1% |
| HAnim | 2,243 / 1,680 | 0 / 0 | 0% / 0% | 0% |

Grade **[C]** for the shares (D-XIT-7); the absolute line counts differ from the teardown's because the definitions of a line differ (for example `X3DNode.js`: 1,528 raw, 1,185 code here, 1,235 in the masterclass), so quote shares, not line counts, across the two.

### 9.1 The curriculum as four tracks

The 32 steps are four tracks of eight. Use the track to decide how to read; the full list with links is in section 3 of the masterclass.

The 32 steps are four tracks of eight: steps 1 to 8 keystone (`Namespace`, `Fields`, `FieldDefinitionArray`, `X3DFieldDefinition`, `Algorithm`, `X3DCast`, `X3DConstants`, `X3DNode`), 9 to 16 abstract types by leverage (`X3DAppearanceChildNode` first), 17 to 24 quick wins by your usage per line read (`WorldInfo`, `MetadataString`, `Normal`, `Coordinate`...), 25 to 32 deep dives where code outgrows fields (`ParticleSystem`, `Appearance`, `Extrusion`, `StaticGroup`, `IndexedFaceSet`, `NavigationInfo`, `CollidableShape`, `HAnimHumanoid`).

The track order is the lesson: read the 8 shared modules first (together 1,652 lines by the masterclass's counts, 1,235 of them `X3DNode`), because every node file is written in their vocabulary; then the abstracts that unlock many nodes; then what your own files use; then the big machines. For the X3D author who is not studying the code, the same data gives a different use: H3 is the list of fields you can set only by SAI or only in X_ITE, and H7 says which component's behaviour you cannot learn from its node file.

## Heuristics

| ID | Rule (imperative) | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-XIT-1 | Name the X_ITE patch and the sha256 of `x_ite.min.js` in every render claim; do not assume one repository uses one patch. | C | 20 vendored copies in 4 patches in one repo; 16.x median gap 5.7 days (N-XIT-9, N-XIT-17) | `x3d.demo@d10b457`; npm 10.9.9 |
| H-XIT-2 | Quote coverage by rung (registered, `createNode`, parses in a versioned file, draws); never "supports the standard". | C | 294 registered, 266 of 267 create, 3 of 7 scenes in section 7 lost something | `X_ITE 16.7.0`, Chromium 153 |
| H-XIT-3 | Sample the last frame after the draw settles and check the canvas size; never the maximum over early frames or a host-element screenshot alone. | C | blank scene reads 1.0000 on its first two frames and on a hidden canvas | `X_ITE 16.7.0`, SwiftShader |
| H-XIT-4 | Before publishing a hosted page, run it under the host's policy; adopt the stylesheet into the shadow root and unhide the surface. | C | canvas 0 x 0 under a stylesheet-blocking policy; 0.1752 with the fix | `X_ITE 16.5.1`, `16.7.0` |
| H-XIT-5 | Start every field-callback body with `try`; one escaping exception stops the route it ran on. | C | 0 events in 3 s against 28 to 31 per 500 ms | `X_ITE 16.5.1`, `16.7.0`, `16.7.1` |
| H-XIT-6 | Silence effect shapes for picking with `Shape.pointerEvents = false` by SAI after load; never write the attribute in a file that must validate. | C | 0 hits to 1 hit; XSD 4.0 and 4.1 reject the attribute | `X_ITE 16.7.0`; `x3d_mcp fork b4efcd3` |
| H-XIT-7 | Validate before you render; treat a drawn scene as unvalidated until the rungs agree. | C | 5 of 5 invalid or inconsistent scenes drew 0.1752 | `X_ITE 16.7.0`; `x3d_mcp fork b4efcd3` |
| H-XIT-8 | Keep X_ITE extension nodes (`BlendMode`, `DepthMode`, material extensions) out of files that must pass the XSD; use them only in files labelled as X_ITE-targeted. | C | `BlendMode` needs `<component name="X_ITE">`; XSD rejects both | `X_ITE 16.7.0`; `X3D XSD 4.0` |
| H-XIT-9 | In a parity harness fix the variables first: opaque geometry, `ToneMapping NONE`, `TELEPORT` transitions, frozen time, same canvas size; compare translucent parts separately. | L | Loom failure modes 84, 109, 114, 115 (read, not re-run) | `x3d.loom@162ab18:LOOM-v1.md` |
| H-XIT-10 | Give every world load a time budget and report non-settlement as an error. | L | rule `loadurl-unbudgeted`; the hang itself is [S] | `x3d.loom@162ab18:kit/loomkit/pagetraps.py` |
| H-XIT-11 | Re-derive a carried count before quoting it, and say which definition counted it. | C | 292 and 26 (teardown) against 294 and 28 (this scan); 98,369 against 123,417 lines | marker scan of `x_ite@16.7.0` |
| H-XIT-12 | Before reading a node file, check where the component's behaviour lives (H7); for 83% of `GaussianSplats` it is not in the node. | C | shares re-derived within one point on 8 components | marker scan of `x_ite@16.7.0` |

## Drills

### D-XIT-1 Count the coverage three ways
- **Level:** L2
- **Task:** Unpack `x_ite@16.7.0`. Count (a) names registered through `getStaticProperties`, (b) X3DUOM 4.1 concrete nodes, (c) the intersection, (d) the names not in X3DUOM. Then, in a browser, count how many of the 267 names `scene.createNode` accepts after `loadComponents (getProfile ("Full"))`.
- **Verify:** `mkdir t && cd t && npm pack x_ite@16.7.0 && tar xzf x_ite-16.7.0.tgz`, then:
```python
import re, glob, xml.etree.ElementTree as ET
ST = re.compile(r'getStaticProperties \("(\w+)",\s*"(\w+)",\s*(\d+),')
files = ['package/dist/x_ite.js'] + [f for f in glob.glob('package/dist/assets/components/*.js') if not f.endswith('.min.js')]
names = set()
for f in files:
    names |= {m.group(1) for m in ST.finditer(open(f, encoding='utf-8').read())}
uom = ET.parse('X3dUnifiedObjectModel-4.1.xml').getroot()          # from x3d_mcp src/validation/schemas
concrete = {n.get('name') for n in uom.find('ConcreteNodes')}
print(len(names), len(concrete), len(names & concrete), len(names - concrete), sorted(concrete - names))
```
- **Answer:** `294 267 266 28 ['ProtoInstance']`. In the browser, `createNode` succeeds for 266 and fails only for `ProtoInstance`; the count is the same on 16.4.3, 16.5.1, 16.6.1, 16.7.0 and 16.7.1.
- **Checked:** 2026-11-14 `X_ITE 16.7.0` (static scan) and `X_ITE 16.4.3`, `16.5.1`, `16.6.1`, `16.7.0`, `16.7.1` (`createNode`), `X3DUOM 4.1`, Chromium 153, SwiftShader

### D-XIT-2 Catch the sampler that lies
- **Level:** L2
- **Task:** Load three scenes with `Background skyColor="0.2 0.2 0.2"` (a visible 2 m box at `Viewpoint position="0 0 6"`; a `Shape` with no geometry; the box translated 40 m behind the camera). For each, register a `finishEvents` watcher before the load, log the non-background fraction per frame (reference 51/255 grey, tolerance 24/765), and take a screenshot 2.5 s later. Report the maximum, the last frame and the screenshot.
- **Verify:** the watcher (register before `replaceWorld`):
```js
const b = X3D.getBrowser (), gl = document.getElementById ("c").shadowRoot.querySelector ("canvas");
const tmp = document.createElement ("canvas"), ctx = tmp.getContext ("2d", { willReadFrequently: true }), frames = [];
b.finishEvents ().addFieldCallback ("watch", () => { try {
  tmp.width = gl.width; tmp.height = gl.height; ctx.drawImage (gl, 0, 0);
  const d = ctx.getImageData (0, 0, tmp.width, tmp.height).data; let diff = 0;
  for (let i = 0; i < d.length; i += 4) if (Math.abs (d[i]-51) + Math.abs (d[i+1]-51) + Math.abs (d[i+2]-51) > 24) diff++;
  frames.push (+(diff / (d.length / 4)).toFixed (4)); } catch (e) {} });
await b.replaceWorld (await b.createX3DFromString (xml));
```
- **Answer:** all three scenes start with frames of 1.0000 (cleared black against a grey Background). Then `visible` settles at 0.1752 (screenshot 0.1752); `blank` and `offcamera` settle at 0.0000 (screenshot 0.0000). A maximum-over-early-frames rule reads 1.0000 for all three, so it calls the blank scenes drawn. Frame counts were 5 to 7 in 2.5 s.
- **Checked:** 2026-11-14 `X_ITE 16.4.3`, `16.5.1`, `16.6.1`, `16.7.0`, `16.7.1`, Chromium 153, SwiftShader, 320 x 240

### D-XIT-3 Reproduce the hosted-page black draw and fix it
- **Level:** L3
- **Task:** Serve a page that loads `x_ite.min.js` with this header on the HTML only: `Content-Security-Policy: default-src 'none'; script-src 'self' 'unsafe-eval' 'wasm-unsafe-eval'; style-src https://fonts.googleapis.com 'unsafe-inline'; connect-src 'self'; img-src 'self' data: blob:; font-src https://fonts.gstatic.com; worker-src blob:`. Load the `visible` scene and read `.x_ite-private-browser` display, the inner canvas size and a page screenshot. Then add the fix (inline CSS text without `@font-face` and `url()`, `adoptedStyleSheets`, unhide) and repeat.
- **Verify:** `getComputedStyle (shadowRoot.querySelector (".x_ite-private-browser")).display`; `shadowRoot.querySelector ("canvas").width`; the fraction of non-grey pixels in the clip. Do not use an element screenshot of `x3d-canvas`: it waits for an element that is never visible.
- **Answer:** no policy: `block`, 320 x 240, 0.1752. Policy: `none`, canvas 0 x 0 CSS and 1 x 1 drawing buffer, fraction 1.0000 (a white page, not a drawing). Policy plus fix: `block`, 320 x 240, 0.1752. Same on 16.5.1 and 16.7.0. Extension (not run here): add the origin that serves `x_ite.css` to `style-src` and confirm that the failure disappears without the fix.
- **Checked:** 2026-11-14 `X_ITE 16.5.1`, `16.7.0`, Chromium 153, SwiftShader, emulated policy above (the real host's policy was not available)

### D-XIT-4 Break picking with a faint shape, then fix it
- **Level:** L2
- **Task:** Load the section 4.3 scene (a box with a `TouchSensor`, a 90% transparent slab 1.5 m in front). Register `addFieldCallback` on `isOver` and `touchTime`, move the mouse over the box centre, press and release. Then set `HALO.pointerEvents = false` by SAI and repeat. Last, validate `<Shape pointerEvents='false'>` with a validator and say what it reports.
- **Verify:** Playwright `page.mouse.move`, `down`, `up` with 600 ms waits; `x3d_mcp fork b4efcd3` `validate_xml` on a two-line scene for XSD 4.0 and 4.1.
- **Answer:** first click: 0 `isOver` and 0 `touchTime` events. After the SAI write: 1 and 1. The validator reports "Element 'Shape', attribute 'pointerEvents': The attribute 'pointerEvents' is not allowed" under both 4.0 and 4.1, so the field can only be set from code.
- **Checked:** 2026-11-14 `X_ITE 16.4.3`, `16.5.1`, `16.7.0`; `x3d_mcp fork b4efcd3`; Chromium 153, SwiftShader

### D-XIT-5 Five scenes the renderer accepts and the validator does not
- **Level:** L2
- **Task:** Build the seven scenes of section 7. Load each in X_ITE (parse result, `scene.routes.length`, drawn fraction) and run each through `validate_xml` and `semantic_diagnostics`.
- **Verify:** `from validation.validate import validate_xml` and `from validation.semantic import semantic_diagnostics` from `x3d_mcp@b4efcd3:src`, on the same strings.
- **Answer:** X_ITE draws 0.1752 on all seven. The validator accepts two (`GaussianSplats` in 4.1, ROUTE after DEF) and reports five problems: `profile-component` errors for Core; XSD "not expected" for `GaussianSplats` in 4.0; `route-before-def` (2 errors) with X_ITE's `routes.length` 0 against 1 for the fixed scene; XSD "not expected" for `BlendMode`; and for the declared variant two XSD errors (the element, and `X_ITE` outside the component enumeration).
- **Checked:** 2026-11-14 `X_ITE 16.7.0`, `x3d_mcp fork b4efcd3`, `X3D XSD 4.0` and `4.1`, lxml 6.1.3, Chromium 153, SwiftShader

### D-XIT-6 Freeze a route with one exception
- **Level:** L3
- **Task:** Scene: `TimeSensor DEF="T" loop="true" cycleInterval="1"` ROUTEd `fraction_changed` to a `ScalarInterpolator DEF="I" key="0 1" keyValue="0 1"`. Add callback A on `T.fraction_changed` and callback B on `I.value_changed` (B counts per 500 ms window for 3 s). Run once with A guarded by try/catch and once with A throwing on its first call. Then write the one-line rule that would have caught the throwing A before the browser started.
- **Verify:** `T.addFieldCallback ("A", "fraction_changed", () => { throw new Error ("boom"); })` against the guarded form; the static rule is `xite-callback-unguarded` in `x3d.loom@162ab18:kit/loomkit/pagetraps.py`.
- **Answer:** guarded: B gets 28 to 31 events per window, A about 180 calls. Throwing: B gets 0 in every window, A is called once, one page error. Rule: a callback body must start with `try`. The same on 16.5.1, 16.7.0 and 16.7.1.
- **Checked:** 2026-11-14 `X_ITE 16.5.1`, `16.7.0`, `16.7.1`, Chromium 153, SwiftShader

### D-XIT-7 Re-derive H7, the locus of behaviour
- **Level:** L2
- **Task:** From the unminified bundles of `x_ite@16.7.0`, split each bundle at lines matching `^;// \./((?:src|node_modules)/\S+)\s*$`, keep modules under `src/x_ite/Components/<C>/` and `src/x_ite/Browser/<C>/`, sum lines per component, and compute the browser share. Compare with the masterclass table for `WebXR`, `GaussianSplats`, `Text`, `RigidBodyPhysics`, `HAnim`.
- **Verify:** the masterclass H7 table in `x3d.docs@f172f67:docs/x_ite/MASTERCLASS.md`. Also report the module count (752 on 24 bundles, 730 own).
- **Answer:** shares 100%, 83%, 68%, 1%, 0% (raw and code-line counts agree within 2 points on all eight rows of section 9); module counts 752 and 730. Absolute lines differ from the teardown (`X3DNode.js` 1,528 raw and 1,185 code against 1,235), so compare shares only.
- **Checked:** 2026-11-14 marker scan of `x_ite@16.7.0`, `16.6.1`, `16.7.1` (module counts 752, 752, 762), Python 3.13.18

### D-XIT-8 Count the patches a repository ships
- **Level:** L1
- **Task:** In a checkout of `x3d.demo`, list every vendored `x_ite.min.js` and count by version banner; count the HTML pages that reference it.
- **Verify:** `find docs -name x_ite.min.js | while read f; do head -c 40 "$f" | grep -o 'X_ITE v[0-9.]*'; done | sort | uniq -c`, then `grep -rl x_ite.min.js --include='*.html' docs | wc -l`.
- **Answer:** `1 X_ITE v16.4.3`, `13 X_ITE v16.5.1`, `5 X_ITE v16.6.0`, `1 X_ITE v16.7.0` (20 files); 29 pages.
- **Checked:** 2026-11-14 `x3d.demo@d10b457`, shell

## Honest limits

- **Software GL only, Chromium only.** Every pixel number is SwiftShader in Chrome for Testing 153.0.8010.12; real-GPU edges, Firefox and Safari were not measured. The only real-GPU figure in the sources is carried: 59.7 fps median, Intel UHD 620, 16.5.1, vsync-capped (`x3d.loom@162ab18:x3d.webgpu/STATE.md`), **[L]**.
- **Correctness was not measured.** "Drew" means a non-background fraction. Colour, lighting, shadows, blending, text, textures, KTX2, audio, WebXR, Script nodes and physics were not exercised here.
- **The teardown's analysis is carried, not re-run.** The AST data (`xite/data/*.json`) that `xite_nodes.py`, `xite_ast.py` and `xite_learn.py` read is not in the public repository, and those scripts hold paths to a local checkout, so they cannot run as shipped. Re-derived here: module counts, the name scan, H7, version diffs. Carried [L]: the teardown's line and function counts, field conformance, H1 to H6 and H8.
- **Sources disagree.** Registered names: 292 concrete modules and 26 X_ITE-only (masterclass) against 294 and 28 (this scan, different definition). Teardown version: 16.7.0 (masterclass header, `xite_learn.py` docstring) against 16.6.1 (Loom lessons); module counts are equal on both, so the anatomy holds for either. `new Function` sites: 12 (loose regex here) against 9 (`STATE.md`). `Shape.pointerEvents` in 4.1: a private note says yes, `X3DUOM 4.1` and both XSDs say no; the schemas win. Frame counts: private note 4 and 64 on 16.5.0, here 5 to 7. Lines: 123,417 raw lines here against 98,369 (teardown `loc`).
- **Carried from private notes, not re-checked [S]:** the splat loading hang, the `TouchSensor` component requirement, `getField` deprecation, `endEvents` on 16.4.1, the repeat timing of style adoption. The hosted-page policy was an emulation of one described in a private note; the real host may differ.
- **Cadence is a registry fact, not a forecast;** "one maintainer" is the registry's list.
- **Only five patches were run in a browser** (16.4.3, 16.5.1, 16.6.1, 16.7.0, 16.7.1); 16.5.0 and 16.6.0 were scanned, not run.

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-XIT-1 | X3DUOM 4.1 concrete nodes | 267 | C | `X3DUOM 4.1` (sha256 4fc10e8e15c0), ElementTree | x3d_mcp@b4efcd3:src/validation/schemas/X3dUnifiedObjectModel-4.1.xml |
| N-XIT-2 | nodes X_ITE can `createNode` | 266 of 267 (`ProtoInstance` fails); same on 5 patches | C | `X_ITE 16.7.0` (and 16.4.3, 16.5.1, 16.6.1, 16.7.1), Chromium 153, SwiftShader | scratch run, 2026-11-14 (D-XIT-1) |
| N-XIT-3 | registered node names | 294 at 16.7.0; 295 at 16.7.1; 266 in X3DUOM 4.1, 28 not | C | regex over unminified `dist/` | npm tarball `x_ite@16.7.0` (D-XIT-1) |
| N-XIT-4 | supported components | 39 on 5 patches | C | `X_ITE 16.7.0`, `browser.supportedComponents` | scratch run, 2026-11-14 |
| N-XIT-5 | webpack modules, own sources | 752 in 24 bundles, 730 own (16.4.3 to 16.7.0); 762 and 732 at 16.7.1 | C | marker scan, `X_ITE 16.7.0` | npm tarballs (D-XIT-7) |
| N-XIT-6 | `x_ite.min.js` size | 1,306,961 B raw; 280,795 B at `gzip -9`; sha256 prefix b7df063e8cb1; byte-identical to the vendored copy | C | `wc`, `gzip -9`, `sha256sum` | x3d.docs@f172f67:docs/vendor/x_ite/x_ite.min.js |
| N-XIT-7 | WebGL2 only | 1 `getContext ("webgl2")` line; 0 hits for webgpu | C | grep, `X_ITE 16.7.0` | npm tarball `x_ite@16.7.0` |
| N-XIT-9 | release cadence, 16.x | 23 releases, 2026-07-27 to 2026-11-08, median gap 5.7 d, 68 in 365 d | C | npm 10.9.9 `npm view x_ite time` | npm registry, read 2026-11-14 |
| N-XIT-10 | npm versions and maintainers | 306 versions; 1 maintainer; latest 16.7.1 | C | npm 10.9.9 | npm registry, read 2026-11-14 |
| N-XIT-11 | draw test, visible box | 0.1752 on 5 patches | C | `X_ITE 16.4.3` to `16.7.1`, Chromium 153, SwiftShader, 320 x 240 | scratch run (D-XIT-2) |
| N-XIT-12 | draw test, blank and off-camera | 0.0000 on 5 patches; first two frames 1.0000 | C | same | scratch run (D-XIT-2) |
| N-XIT-14 | picking with a pickable faint shape | 0 events; 1 event after `pointerEvents = false` | C | `X_ITE 16.4.3`, `16.5.1`, `16.7.0` | scratch run (D-XIT-4) |
| N-XIT-15 | hosted-page policy trap | canvas 0 x 0 CSS, 1 x 1 buffer; 0.1752 with the fix | C | `X_ITE 16.5.1`, `16.7.0`, emulated policy | scratch run (D-XIT-3) |
| N-XIT-16 | callback freeze | B events per 500 ms: 28 to 31 guarded, 0 throwing | C | `X_ITE 16.5.1`, `16.7.0`, `16.7.1` | scratch run (D-XIT-6) |
| N-XIT-17 | vendored patches in `x3d.demo` | 20 files: 1 x 16.4.3, 13 x 16.5.1, 5 x 16.6.0, 1 x 16.7.0; 29 pages | C | shell over banners | x3d.demo@d10b457:docs/demos (D-XIT-8) |
| N-XIT-18 | renderer vs validator, seven scenes | all draw 0.1752; 5 invalid or inconsistent; 3 dropped something silently | C | `X_ITE 16.7.0`; `x3d_mcp fork b4efcd3` | scratch run (D-XIT-5) |
| N-XIT-19 | browser option defaults | `ColorSpace LINEAR_WHEN_PHYSICAL_MATERIAL`, `ToneMapping NONE`, `DisplayColorSpace SRGB`, `Exposure 1`, `Multisampling 4`, `OrderIndependentTransparency false`, `MaximumFrameRate 80` | C | `X_ITE 16.4.3` to `16.7.1`, `getBrowserOption` | scratch run, 2026-11-14 |
| N-XIT-21 | version diff 16.4.3 to 16.7.1 | 2 renames, +10 modules and +1 node at 16.7.1; defaults unchanged | C | marker and name scan | npm tarballs (section 8) |
| N-XIT-22 | locus shares (H7) | `WebXR` 100%, `GaussianSplats` 83%, `Text` 68%, `RigidBodyPhysics` 1%, `HAnim` 0% | C | marker scan, `X_ITE 16.7.0` | npm tarball (D-XIT-7) |
| N-XIT-23 | teardown anatomy | 98,369 lines, 730 modules, 5,940 functions; 194 / 43 / 29 / 1 field conformance | L | read, not re-run | x3d.docs@f172f67:docs/x_ite/MASTERCLASS.md |
| N-XIT-24 | curriculum | 32 steps in 4 tracks of 8 | C | read in the exact file | x3d.docs@f172f67:docs/x_ite/MASTERCLASS.md |

## Sources and provenance

- npm tarballs of `x_ite` 16.4.3, 16.5.0, 16.5.1, 16.6.0, 16.6.1, 16.7.0 and 16.7.1 (unpacked in a scratch folder, never installed), read on 2026-11-14: `dist/x_ite.js`, `dist/assets/components/*.js`, `dist/x_ite.d.ts`, `dist/X3DUOM.xml`, and executed in Chromium through Playwright 1.63.0. The vendored `x3d.docs@f172f67:docs/vendor/x_ite/x_ite.min.js` and `x_ite.css` are byte-identical to the 16.7.0 tarball.
- `x3d.docs@f172f67`: `docs/x_ite/MASTERCLASS.md` and `docs/tools-shared/xite_{split,ast,nodes,learn,scenes,doc}.py` (read; not run, data files absent).
- `x3d.loom@162ab18`: `LOOM-v1.md` (failure modes 84, 88, 101, 109 to 111, 114 to 116, 118, 127, 140), `LESSONS-v1.0.md`, `kit/loomkit/pagetraps.py`, `x3d.webgpu/STATE.md`, `x3d.webgpu/BENCHMARK.md` (read, not run).
- `x3d.demo@d10b457`, `x3d_mcp@b4efcd3` (`README.md`, `src/validation/`), `x3d.xray@8fa6845` (`README.md`, the vendored patch statement).
- Private-source gap: private notes about the hosted-page trap, picking, splat loading and the earlier field guide were used as pointers only. Each figure that appears here was re-derived above, or is graded [S] or [L] where it was not. No private document, link or identifier is reproduced.
- Siblings: [01 The tether](01-the-tether.md), [03 The validator and the gates](03-validator-and-gates.md), [04 MCP for agents](04-mcp-for-agents.md), [07 x3d.xray](07-xray.md), [08 Babylon bridge](08-babylon-bridge.md), [13 Physics](13-physics.md).
