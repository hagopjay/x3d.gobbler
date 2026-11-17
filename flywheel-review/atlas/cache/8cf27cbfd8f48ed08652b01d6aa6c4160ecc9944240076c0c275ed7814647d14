# 18. Path-tracing X3D: three-gpu-pathtracer as a light-transport reference

> **Say it:** A path tracer is a second opinion on how an X3D scene is lit, not a better X_ITE: it agrees with X_ITE when it is limited to direct light (Cornell box, 1 bounce, FLIP 0.142), moves toward Cycles as bounces are added, and fails a "within the reference spread" bound on a scene whose lighting it does not model (PBR grid, 0.743 against a bound of 0.349). **[C]**

| field | value |
|---|---|
| chapter code | `PTR` |
| prerequisites | [02 Loom laws](02-loom-laws.md), [06 XITE, the oracle](06-xite-the-oracle.md), [08 Babylon bridge](08-babylon-bridge.md) (the three.js bridge sections), [12 Unreal tier 1](12-unreal-tier1.md) (the metric and the bound) |
| after this you can | state what a path tracer adds to an X3D scene and what it drops; convert X3D light units for a physically based renderer; run `run-pt.js` and read its FLIP table; spot a camera mismatch between two reference renderers; explain why the first Cycles numbers were wrong |
| sources read | `x3d.loom@5f59349:x3d.threejs/pathtracer/{README.md,run-pt.js,src/pt-adapter.js,flip_score.py,build_results.py,cycles_job.py,results/results.json}`; `x3d.lab@a7af249:notebooks/unreal/colab_g4/{leg_e_cells.py,scenes/*.x3d}`; `x3d.lab@a7af249:src/x3dlab/blender_worker.py`; three-gpu-pathtracer 0.0.28 `build/index.module.js` (light and bounce code, read) |
| instruments used | Chromium 153.0.8010.12 on SwiftShader (software Vulkan, no real GPU); three r187; three-gpu-pathtracer 0.0.28; three-mesh-bvh 0.9.18; X_ITE 16.6.0; bpy 5.3.0 (Cycles, CPU); flip-evaluator 1.7; numpy 2.5.4; Pillow 13.0.0 |

This chapter teaches one integration: the three.js bridge ([chapter 8](08-babylon-bridge.md), section 14) builds a three.js scene from an X3D file; [three-gpu-pathtracer](https://github.com/gkjohnson/three-gpu-pathtracer) then traces light through that scene on the GPU, in the browser. The result is a reference for light transport that sits beside X_ITE (what an X3D browser draws), Cycles (what a production path tracer draws) and Unreal ([chapter 12](12-unreal-tier1.md)). The chapter is about the comparison: what had to be converted, what the numbers say, and the two mistakes that were made and caught on the way.

---

## 1. The map

```text
 X3D file (Leg E: e1 PBR grid, e2 Cornell box, e3 light ladder)
    |
    +--> X_ITE 16.6.0 --------------------------------> PICTURE X   (what an X3D browser draws)
    |
    +--> reader + three.js body (x3d.threejs/bridge) --> three Scene
    |         |                                             |
    |         +--> bridge raster (lights x PI, Phong) ----> PICTURE R   (the bridge's own picture)
    |         |
    |         +--> src/pt-adapter.js (lights, materials, background re-set)
    |                   |
    |                   +--> three-gpu-pathtracer (BVH, N bounces, S samples) ---> PICTURE P
    |
    +--> x3d-blender-io import --> Cycles (bpy, camera = X3D fieldOfView) --> PICTURE C

 metric: object-pixel FLIP over X, R, P, C  (flip-evaluator LDR, pixels where either is not sky)
 test  : max(P-X, P-C) <= X-C + 0.05   (the Unreal lane's tier-1 bound, ch12 section 11)
```

| stage | file | what it owns | what it leaves out |
|---|---|---|---|
| scene | `x3d.threejs/bridge` | reader, body, Transform, lights, materials | not edited by this work |
| adapter | `x3d.threejs/pathtracer/src/pt-adapter.js` | light units, Phong to physical, background, frame loop | ground colours, light radius cut-off, ambient |
| runner | `run-pt.js` | static server, Chromium, X_ITE and path-traced pictures, timings | no real-GPU timing |
| score | `flip_score.py`, `build_results.py` | object-pixel FLIP, bound test, strips | one camera per scene |
| Cycles | `cycles_job.py` | the lab's Blender worker with the camera matched | Blender's default view transform not isolated |
| demo | `x3d.demo` Demo 25 | live wipe against X_ITE, bounce slider, emissive switch | speed claims |

In scope: three scenes, one camera each, 320 x 240, 96 samples. Out of scope: real-GPU speed, denoising, the WebGPU path tracer, volumes and textures in the path tracer, animation.

**Read next:** [12 Unreal tier 1](12-unreal-tier1.md) for the metric and the bound this chapter reuses; [06 XITE, the oracle](06-xite-the-oracle.md) for why X_ITE is the baseline.

---

## 2. What a path tracer changes about X3D lighting

X3D 4.0 lighting (19775-1, clause 17) is local: each light shades each surface by its own N.L and the material, with fog and an optional ambient term. Nothing in the standard says light bounces. A path tracer solves the rendering equation by sampling paths, so everything X3D leaves out comes back in.

| X3D idea | X_ITE 16.6.0 | path tracer | consequence in the pictures |
|---|---|---|---|
| light bounces | none | every bounce | red and green wall colour on the Cornell boxes |
| shadows | only if the file asks (`shadows`) | always | the PBR grid throws shadows in the path-traced picture only |
| `emissiveColor` | colours the surface, lights nothing | the surface is a light | the Cornell ceiling panel lights the room |
| `ambientIntensity` | a fixed term | none; the bounced light is the ambient | dark corners in e1 |
| light `radius` | hard cut-off | not applied | none in the three scenes (radius covers the room) |
| PhysicalMaterial, no environment | a default glow | black metals | metals read darker in the path tracer |
| classic Material (Phong) | rho x I | converted (section 3) | a fit, not a match |

Grades: the X_ITE rows and the path-tracer rows are **[C]** where a picture shows them (Cornell panel, e1 shadows) and **[L]** for the radius and ambient rows (read in code, not isolated by a fixture).

---

## 3. The adapter: three conversions that carry the result

`src/pt-adapter.js` is shared by the runner and by the demo page. It does five things; three change numbers.

**3.1 Light units.** The bridge sets every light to intensity x PI and bakes the X3D attenuation polynomial into a patched shader. The path tracer reads `light.decay` and `light.distance` itself, so each light is re-set in physical terms. X_ITE lights PhysicalMaterial as rho/pi x I and classic Material as rho x I; three.js's Lambert is rho/pi x I, so a PBR scene needs the light at I, not I x PI.

| X3D attenuation (a0 a1 a2) | path-tracer decay | intensity | scenes |
|---|---|---|---|
| 1 0 0 | 0 | I / a0 | e3 bay 2 |
| 0 0 1 | 2 | I / a2 | e2, e3 bay 3 |
| 0 1 0 | 1 | I / a1 | none |
| anything else | 2 | fitted at half the radius, logged | none |

```js
// src/pt-adapter.js, the whole decision
if (a[1] === 0 && a[2] === 0) { o.decay = 0; o.intensity = I / Math.max(a[0], 1e-6); }
else if (a[0] === 0 && a[1] === 0) { o.decay = 2; o.intensity = I / a[2]; }
```

**3.2 Classic Material.** MeshPhong becomes MeshPhysical with the diffuse colour times PI, so that rho/pi x I x PI lands on rho x I. It is a fit: the path tracer then also returns PI times too much indirect light from those surfaces. It matters only in e3 (five converted materials) and is logged in every result file.

**3.3 Background.** The body draws a Background as sphere meshes. A path tracer treats them as lit geometry (e3's sky came out white). The adapter removes them and uses the first `skyColor` as the miss colour; ground colours and angles are not drawn.

**3.4 The frame loop and `window.X3D`.** The body runs its own `requestAnimationFrame` loop; `freeze()` stops it, or a raster frame overwrites the path tracer's canvas. The bridge's SAI shim also assigns `window.X3D`; a page that loads X_ITE first must keep its own reference (`const XITE = window.X3D`) or X_ITE's `getBrowser` is gone. This cost an hour on the demo page.

**3.5 Settings.** `bounces` 1 or 6, 96 samples, 2 x 2 tiles, `filterGlossyFactor` 0.5, no environment, no tone mapping, linear output (the bridge's colour-management-off choice, so the picture is comparable with X_ITE's raw numbers).

---

## 4. The numbers, and the bound that moved

Object-pixel FLIP is the Unreal lane's metric ([chapter 12](12-unreal-tier1.md), section 11): flip-evaluator LDR, mean over the pixels where either picture differs from the scene's sky colour (the Unreal lane keys a magenta background). Lower is closer.

| scene | P(6 b) vs X | P vs C | P(1 b) vs X | R vs X | C vs X | bound X-C+0.05 | P within | R within |
|---|---|---|---|---|---|---|---|---|
| e1 PBR grid | 0.641 | 0.743 | 0.664 | 0.476 | 0.299 | 0.349 | **no** | no |
| e2 Cornell | 0.265 | 0.380 | 0.142 | 0.595 | 0.468 | 0.517 | yes | no |
| e3 light ladder | 0.490 | 0.751 | 0.490 | 0.693 | 0.705 | 0.755 | yes (by 0.005) | no |

Instrument: Chromium 153.0.8010.12 SwiftShader, three r187, three-gpu-pathtracer 0.0.28, X_ITE 16.6.0, bpy 5.3.0 CPU 256 samples with OpenImageDenoise, 320 x 240, 96 samples; `x3d.loom@5f59349:x3d.threejs/pathtracer/results/results.json`. Noise floor: two 96-sample Cornell runs differ by 0.055 [C]. The light-ladder pass is inside the noise floor and is not a result.

What the table says, ranked by how much it changes a decision:

1. **The bridge's own raster picture fails the bound on all three scenes.** It sits 0.48 to 0.69 from X_ITE across the three scenes. [C] The cause named in the Unreal lane's notes is the PI factor on PBR lights; this chapter did not isolate it, so it is **[L]**.
2. **One bounce is X_ITE.** The Cornell box at 1 bounce is 0.142 from X_ITE, 0.265 at 6 bounces, and the 6-bounce picture is closer to Cycles (0.380) than the 1-bounce picture is (0.494). [C]
3. **The PBR grid is not explained.** The path tracer is 0.743 from Cycles against a bound of 0.349. Suspected, not isolated: no ambient term, the shadows, how the bridge sets metals. **[S]**
4. **The light ladder cannot separate renderers.** Four bays of white panels over black: object share is 16.4 percent and every picture is 0.49 to 0.79 from every other. [C]

### 4.1 The first table was wrong

The first run used the lab's Cycles render as it came. It reported the path tracer inside the bound on all three scenes (e1 0.636, e2 0.279, e3 0.501 against X; bounds 0.644, 0.468, 0.819). The Cycles pictures were drawn smaller than X_ITE's. The add-on sets the Blender camera from an X3D `fieldOfView` at Blender's 16:9 default; rendering at 320 x 240 then keeps the horizontal angle (1.2695 rad) and widens the vertical one to 1.0092 rad where X3D asked 0.7854. X3D `fieldOfView` applies to the smaller picture axis (19775-1, 23.4.2), vertical at 4:3. Every Cycles number was inflated, the spread X-C with it, and the bound with that. `cycles_job.py` patches one worker line in memory (sensor fit vertical, angle = `fieldOfView`); with the camera matched e1 fails. [C]

```text
 spread X-C, e1      first run  0.594   (Cycles framed wide)
                     matched    0.299
 bound X-C + 0.05    first run  0.644 -> P-C 0.617 passed
                     matched    0.349 -> P-C 0.743 fails
```

The Unreal lane compared against the same Cycles pictures made the same way. Whether its Leg E numbers carry the same framing offset has not been checked here. **[S]**

---

## 5. Running it

```bash
cd x3d.loom/x3d.threejs/pathtracer && npm i
export CHROMIUM_EXECUTABLE=/path/to/chromium          # any Chromium; SwiftShader is fine
node run-pt.js --out out6 --samples 96 --bounces 6 --xite scenes/e1-pbr-grid.x3d scenes/e2-cornell-box.x3d scenes/e3-light-ladder.x3d
node run-pt.js --out out1 --samples 96 --bounces 1 scenes/e1-pbr-grid.x3d scenes/e2-cornell-box.x3d scenes/e3-light-ladder.x3d
python cycles_job.py LAB/src/x3dlab/blender_worker.py ADDON/source cyc   # python with bpy
python build_results.py out6 out1 cyc OUT [DEMODIR]                       # table, strips, the Demo 25 page
```

On SwiftShader a scene takes 100 to 190 s at 96 samples (about 1 s per sample, plus a shader build of about 50 s); `tTrace` is measured after a `gl.finish()` and a one-pixel read, because without it the timer stops before the GPU has done the work (first runs reported 0.8 s for 96 samples). Real-GPU speed is not measured.

The result files per run (`results/runs/f6`, `f1`) carry the light-conversion log, the GL renderer string and the page errors. A run with page errors is not counted.

---

## 6. The demo, and what it is for

Demo 25 (`x3d.demo` `docs/demos/three-pathtracer/v1/`) puts X_ITE and the path tracer in one frame with a draggable wipe, a bounce slider, an "emissive surfaces cast light" switch and the three scenes. It is built to show three things at a glance: one bounce agrees with X_ITE; bounces add light X3D does not carry; an emissive surface is paint to X_ITE and a lamp to a path tracer. It reports the visitor's own GPU string and samples per second and makes no speed claim. Checked headless on SwiftShader only: 181 samples, X_ITE scene loaded, path-traced canvas non-black. **[C]** for that check; **[S]** for behaviour on a real GPU, a phone, or a browser without float render targets (the page falls back to the pictures).

---

## Heuristics

| ID | Rule (imperative, at most 30 words) | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-PTR-1 | Put every renderer in a comparison through the same camera maths before comparing numbers; check the framing by eye first, it costs one picture. | [C] | Cycles drew 1.0092 rad where 0.7854 was asked; first table passed all three scenes, matched table failed e1 | bpy 5.3.0; flip-evaluator 1.7 |
| H-PTR-2 | Apply X3D `fieldOfView` to the smaller picture axis, never the horizontal one, when building any camera outside an X3D browser. | [C] | 19775-1 23.4.2; D-PTR-1 | numpy 2.5.4 |
| H-PTR-3 | Set a physically based renderer's lights to I for PhysicalMaterial scenes and I x PI only when matching classic rho x I shading. | [L] | X_ITE PBR lights rho/pi x I; Cornell 1 bounce 0.142 from X_ITE | X_ITE 16.6.0; run-pt.js |
| H-PTR-4 | Remove any mesh a bridge draws for a Background before path tracing, and set the miss colour instead; a lit sky sphere turns the frame white. | [C] | e3 first run: frame FLIP 0.93 with the sphere, 0.09 to 0.50 without | run-pt.js |
| H-PTR-5 | Stop the body's own animation-frame loop before accumulating samples, or a raster frame overwrites the accumulated picture. | [L] | the loop is `requestAnimationFrame(loop)` in `body-three.js`; the first shots survived by timing luck | `x3d.loom@5f59349` |
| H-PTR-6 | Keep your own reference to X_ITE's `window.X3D` before loading any bundle that defines `X3D`; the bridge's SAI shim overwrites it. | [C] | `getBrowser` returned null until fixed; D-PTR-4 | headless Chromium 153 |
| H-PTR-7 | State the noise floor next to every FLIP pass, and call a pass smaller than the floor "inside noise". | [C] | floor 0.055; e3 passes by 0.005 | two 96-sample Cornell runs |
| H-PTR-8 | Time GPU work after a `gl.finish()` and a pixel read; a timer that stops at the last draw call times the queue, not the work. | [C] | `tTrace` 0.8 s before, 104 s after, for 96 samples | Chromium 153 SwiftShader |
| H-PTR-9 | Treat an emissive surface as a light in a path tracer and as paint in X_ITE; offer the switch rather than choose silently. | [C] | Cornell panel; demo switch | run-pt.js; Demo 25 |
| H-PTR-10 | Do not read a path-traced mismatch as an X3D defect until a direct-light run (1 bounce) shows whether the gap is transport or conversion. | [L] | Cornell 0.142 at 1 bounce, 0.265 at 6 | run-pt.js |

---

## Drills

Code below was run with `python3 -I`, numpy 2.5.4 and Pillow 13.0.0 on 2026-11-15, software only; paths are relative to `x3d.loom/x3d.threejs/pathtracer`.

### D-PTR-1 The vertical angle that Cycles drew
- **Level:** L1
- **Task:** The add-on gave a Blender camera a horizontal angle of 1.2695 rad. At 320 x 240, what vertical angle does that draw, and what had X3D asked for (`fieldOfView="0.7854"`)?
- **Verify:**
```python
import math
ax = 1.2695
print(2 * math.atan(math.tan(ax / 2) * 240 / 320))
```
- **Answer:** 1.0092 rad drawn against 0.7854 asked, 28.5 percent wider. At 16:9 the same horizontal angle gives 0.7854, which is why the add-on's value looks right at Blender's default resolution.
- **Checked:** `2026-11-15 python3 -I numpy 2.5.4`

### D-PTR-2 Apply the bound
- **Level:** L2
- **Task:** From `results/results.json`, list the scenes where the path tracer passes `max(P-X, P-C) <= X-C + 0.05` and the scenes where the bridge raster does.
- **Verify:**
```python
import json
r = json.load(open("results/results.json"))["scenes"]
for n, v in r.items(): print(n, max(v["pt6_vs_xite"], v["pt6_vs_cycles"]), max(v["raster_vs_xite"], v["raster_vs_cycles"]), v["bound"])
```
- **Answer:** Path tracer: e2 (0.380 against 0.518) and e3 (0.751 against 0.755), not e1 (0.743 against 0.349). Raster: none (0.501, 0.595, 0.789).
- **Checked:** `2026-11-15 python3 -I`

### D-PTR-3 Re-score a strip
- **Level:** L2
- **Task:** `results/strips/e2-cornell-box.webp` holds four 320 x 240 panels (X_ITE, Cycles, raster, path tracer). Cut them and compute path-tracer-against-X_ITE object FLIP with a black background. Why does it not equal 0.265?
- **Verify:**
```python
from PIL import Image; from flip_score import score
im = Image.open("results/strips/e2-cornell-box.webp").convert("RGB")
for i, n in enumerate("xcrp"): im.crop((320 * i, 0, 320 * i + 320, 240)).save(f"/tmp/{n}.png")
print(score("/tmp/x.png", "/tmp/p.png", [0, 0, 0]))
```
- **Answer:** 0.264. The strip is lossy webp (quality 88), so the value moves by about 0.001 from 0.265 measured on the PNGs; it is a reproduction check, not a new measurement.
- **Checked:** `2026-11-15 python3 -I flip-evaluator 1.7`

### D-PTR-4 Find what overwrites X_ITE
- **Level:** L2
- **Task:** Load the bridge bundle and X_ITE on one page. Find the line in the bundle that makes `X3D.getBrowser('#xc')` return nothing, and write the one-line fix.
- **Verify:** `grep -n "window.X3D = X3D" docs/demos/three-pathtracer/v1/vendor/bundle-body.js` (in `x3d.demo`).
- **Answer:** line 12271 in the 2026-11-15 bundle assigns the SAI shim to `window.X3D`. Fix: `const XITE = window.X3D;` straight after the X_ITE script tag and use `XITE.getBrowser`.
- **Checked:** `2026-11-15 grep, headless Chromium 153`

### D-PTR-5 Break a light conversion
- **Level:** L3
- **Task:** In `src/pt-adapter.js` set the light intensity to I x PI for PBR scenes (`lights: 'classic'`) and re-run e2 at 96 samples and 6 bounces. Predict the direction of the change in P-vs-X before you run it, then run `build_results.py` and compare.
- **Verify:** `node run-pt.js --out o --lights classic --samples 96 --bounces 6 --xite scenes/e2-cornell-box.x3d`, then `flip_score.py` on the X and P pictures.
- **Answer:** expected: much brighter, FLIP up from 0.265 (the earlier run with an unscaled path-traced light was blown out at 16 and 64 samples in the first pictures). Not scored in this chapter. 
- **Checked:** `not run`

### D-PTR-6 Isolate the e1 gap
- **Level:** L3
- **Task:** Design three runs that separate the suspected causes of e1's 0.743 (no ambient term, shadows, metal handling) and say which picture each is compared with.
- **Verify:** compare against Cycles with the world colour and shadow settings you control; each run changes one thing.
- **Answer:** none yet; this is the open item. A reasonable first cut: Cycles with shadows disabled on the lights, the path tracer with an environment colour equal to the sky, and a metallic-0 copy of the grid.
- **Checked:** `not run`

---

## Honest limits

- No real-GPU timing: every time here is software Vulkan (SwiftShader), about one sample per second. Nothing is claimed about speed on a GPU. **[C]**
- One camera per scene, one run per cell except the Cornell noise pair; no confidence intervals. **[C]**
- Cycles goes through Blender's default view transform; the X_ITE and path-traced pictures do not. That offset is not isolated and inflates every Cycles number by an unknown amount. **[S]**
- The first table (section 4.1) is published history, not a result; the Unreal lane's Leg E Cycles pictures were made the same way and may carry the same framing offset. **[S]**
- The cause of the bridge raster's distance from X_ITE (the PI factor) is read from the Unreal lane's notes and not isolated here. **[L]**
- WebGLPathTracer is marked deprecated in 0.0.28 in favour of WebGPUPathTracer (console warning); a WebGPU run is not done. **[C]**
- The path tracer draws no textures other than what the bridge builds as three.js maps, no volumes, no fog, no animation. Not tested. **[S]**
- FLIP says how far two pictures are, not which is right; a scene can pass by being far from everything. **[C]**

---

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-PTR-1 | e2 Cornell, path tracer 6 bounces vs X_ITE, object FLIP | 0.265 | [C] | Chromium 153 SwiftShader; X_ITE 16.6.0; 96 spp | `x3d.loom@5f59349:x3d.threejs/pathtracer/results/results.json` |
| N-PTR-2 | e2 Cornell, path tracer 1 bounce vs X_ITE | 0.142 | [C] | same | same |
| N-PTR-3 | e2 Cornell, path tracer vs Cycles | 0.380 | [C] | same; bpy 5.3.0 CPU 256 spp OIDN | same |
| N-PTR-4 | e2 Cornell, Cycles vs X_ITE (spread) | 0.468 | [C] | same | same |
| N-PTR-5 | e1 PBR grid, path tracer vs Cycles | 0.743 | [C] | same | same |
| N-PTR-6 | e1 pass bound (X-C + 0.05) | 0.349 | [C] | same | same |
| N-PTR-7 | e3 light ladder, path tracer vs Cycles; bound | 0.751; 0.755 | [C] | same | same |
| N-PTR-8 | e2 bridge raster vs X_ITE | 0.595 | [C] | same | same |
| N-PTR-9 | Noise floor: two 96 spp Cornell runs against each other | 0.055 | [C] | same | `results/runs/` notes; README |
| N-PTR-10 | Cycles vertical angle drawn at 4:3 from the add-on's horizontal 1.2695 rad | 1.0092 rad (asked 0.7854) | [C] | numpy 2.5.4 (D-PTR-1) | `cycles_job.py` docstring |
| N-PTR-11 | First (wrong) e1 spread X-C and bound before the camera match | 0.594; 0.644 | [C] | same rig, unmatched Cycles | commit history of `x3d.loom` PR #76 |
| N-PTR-12 | Path-tracer time per 96-sample scene on SwiftShader | 59 to 111 s trace, 100 to 190 s with shader build | [C] | Chromium 153 SwiftShader | `results/runs/f6/*.json` |
| N-PTR-13 | Object share of e3 light ladder | 16.4 percent of pixels | [C] | same | `results/results.json` |
| N-PTR-14 | e3 frame FLIP with a lit sky sphere vs without | 0.93 vs 0.09 | [C] | same | first and final run files |
| N-PTR-15 | Demo 25 headless check: samples reached; X_ITE root nodes | 181; 12 | [C] | Chromium 153 SwiftShader | `x3d.demo` PR 29 description |

---

## Sources and provenance

| repo@sha | path | read how |
|---|---|---|
| `x3d.loom@5f59349` | `x3d.threejs/pathtracer/*` (adapter, runner, scoring, results, README) | run |
| `x3d.lab@a7af249` | `notebooks/unreal/colab_g4/leg_e_cells.py`, `scenes/*.x3d`, `src/x3dlab/blender_worker.py` | read; the worker run with one line patched (`cycles_job.py`) |
| `x3d.demo@272f4fd` | `docs/demos/three-pathtracer/v1/` | run headless |
| three-gpu-pathtracer 0.0.28, three-mesh-bvh 0.9.18, three r187 | `build/index.module.js` | read (decay, distance, bounces, deprecation) |
| `x3d.docs@acd4e25` | `docs/learn/12-unreal-tier1.md` | read (metric and bound) |

Run on 2026-11-15. The Unreal lane's Leg E numbers were used as the definition of the metric and bound only; no number of that lane is repeated here.

Siblings: [02 Loom laws](02-loom-laws.md), [06 XITE, the oracle](06-xite-the-oracle.md), [08 Babylon bridge](08-babylon-bridge.md), [12 Unreal tier 1](12-unreal-tier1.md).
