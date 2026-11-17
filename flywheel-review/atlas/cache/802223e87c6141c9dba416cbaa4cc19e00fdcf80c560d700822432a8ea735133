# 15. Animation timelines: Theatre.js and GSAP to X3D

> **Say it:** An authored timeline becomes X3D as a TimeSensor, interpolators and ROUTEs, and the only honest way to ship it is to measure the bake against the tool, because interpolators are straight lines and ColorInterpolator blends in HSV. **[C]**

| field | value |
|---|---|
| chapter code | `ANM` |
| prerequisites | [06](06-xite-the-oracle.md); [08](08-babylon-bridge.md) sections on the reader and the SAI |
| after this you can | bake a Theatre.js state or a GSAP timeline into interpolators and say how far it is from the tool; predict where an ease costs keys; drive a running scene through the SAI instead; state what the Theatre and GSAP licences let you ship |
| sources read | `x3d.loom@1d1109e:x3d.anim/{README.md,src/*,tools/*,test/anim.test.js,receipts/*.json}`; npm registry metadata for `@theatre/core`, `@theatre/studio`, `gsap` |
| instruments used | `X_ITE 16.6.0`, `Chromium 153.0.8010.12, SwiftShader`, three.js r187 with the x3d.threejs bridge body, `gsap 3.15.1`, `@theatre/core 0.7.2`, Node 22.23.4 |

## 1. The map

```text
 Theatre state.json --(@theatre/core evaluates)--+
                                                 +--> bake --> channels --> TimeSensor
 GSAP timeline ------(tl.time(t) evaluates)------+            (keys kept    + *Interpolator
                                                              at authored    + 2 ROUTE / field
 live path: the tool keeps the clock                          instants)         |
   --> node[field] = new X3D.SFVec3f(..)  ------------------------------------>+--> X_ITE | bridge
 back path: X3D text --> channels --> Theatre state | GSAP code
```

| path | who owns the clock | needs script in the page | what the file contains |
|---|---|---|---|
| exported | the X3D `TimeSensor` | no | interpolators, 60 fps worth of keys at most |
| live (SAI) | Theatre or GSAP | yes | nothing animated; the tool's real eases run |
| back | the author again, in either tool | no | linear segments (Theatre handles `[0.5,0.5,0.5,0.5]`, GSAP ease `none`) |

**In scope:** TimeSensor, ScalarInterpolator, PositionInterpolator, OrientationInterpolator, ColorInterpolator, ROUTE; X_ITE 16.6.0 and the three.js bridge. **Not in scope:** CoordinateInterpolator and morph targets, Spline interpolators, the Babylon body (the reader is shared, the three.js body was the one run), Theatre's studio UI.

## 2. The contract with the authoring tool

| thing | rule |
|---|---|
| object name | the Theatre object name, or the key of the GSAP target tree, is the node's `DEF` |
| prop path | `field`, or `field.x`, `field.y`, `field.z` for vectors, `field.r/g/b` for colours; unknown fields are an error |
| rotation | Euler degrees about fixed X, then Y, then Z, written as axis-angle for `OrientationInterpolator` |
| unkeyed components | read as 0 in Theatre; pass defaults (a scale of 1) or the object collapses |
| keys | every authored key time and tween boundary stays a key; between them 60 fps samples are thinned by Ramer-Douglas-Peucker against the X3D interpolation rule |

Where the keys go, for one eased channel (value against time; `|` a kept sample):

```text
 v ^                         ...  authored end key (always kept)
   |                    ..''
   |                .'' |        steep part: many samples kept
   |             .''    |
   |        ...''       |        flat part: few samples kept, error stays under tol
   |  ....''            |
   +--|-----|----|--|---|--|--> t     dense 60 fps grid + authored times, thinned by tolerance
```

```xml
<TimeSensor DEF='Clock_gsap_orbit' cycleInterval='3.4' loop='true' startTime='1'/>
<ColorInterpolator DEF='I_BoxMat_diffuseColor' key='0 0.147 0.294 ...' keyValue='0.9 0.3 0.1, ...'/>
<ROUTE fromNode='Clock_gsap_orbit' fromField='fraction_changed' toNode='I_BoxMat_diffuseColor' toField='set_fraction'/>
<ROUTE fromNode='I_BoxMat_diffuseColor' fromField='value_changed' toNode='BoxMat' toField='diffuseColor'/>
```

## 3. What the numbers say

Cases: a 24-satellite GSAP orrery (76 channels, 6.91 s, 30 fps, camera held fixed, the world Transform moves), a GSAP timeline (6 channels, 3.4 s, 7 tweens, eases power2, sine, back, bounce, elastic, expo) and a Theatre state (5 channels, 4 s, Bezier handles). 41 fractions of the cycle, sampled with the clock frozen and `set_fraction` written to every interpolator. Instrument for all rows: `X_ITE 16.6.0` and the three.js r187 bridge, `Chromium 153.0.8010.12, SwiftShader`.

| channel | keys | bake error (own grid) | X_ITE vs the tool |
|---|---|---|---|
| GSAP Box.translation | 34 | 0.00423 | 0.00423 |
| GSAP Box.rotation (rad) | 58 | 0.00217 | 0.00209 |
| GSAP BoxMat.diffuseColor | 25 | 0.0037 | 0.00189 |
| GSAP BoxMat.transparency (bounce) | 50 | 0.00814 | 0.000875 |
| GSAP Ball.translation (elastic) | 28 | 0.0138 | 0.0122 |
| Theatre Box.translation | 59 | 0.00755 | 0.00695 |
| Theatre Box.rotation (rad) | 64 | 0.00203 | 0.002 |
| Theatre BoxMat.diffuseColor | 73 | 0.00536 | 0.00326 |
| GSAP orrery, worst of 76 channels (S17.translation, 35 keys) | 2,467 keys in all | 0.0286 | 0.0263 |

Three agreements, each a different question: our model of the interpolators against X_ITE (worst 1.83e-6, orrery; includes HSV and slerp); the bridge's reader against X_ITE (worst 1.86e-6, orrery); the live path, the tool's state written through the SAI and read back from X_ITE (worst 2.8e-17). Pictures, bridge against X_ITE, 18 pairs at 25, 60 and 95 percent through the interpolator path and the live path: worst 34.02 dB (orrery; 46.95 and 55.01 dB on the other two), foreground IoU at least 0.993.

## 4. The bake, in the order it bites

| fact | value | grade |
|---|---|---|
| **ColorInterpolator blends in HSV** (hue the short way, spec 19775-1; X_ITE does so) | red to blue at 0.5: X_ITE gives (1, 0, 1), an RGB lerp (0.5, 0, 0.5); ignoring it was 0.059 off, modelling it 7.6e-8 | [C] |
| the sample grid sets an error floor that `tol` cannot lower | `bounce.out`, 2 s, 60 fps: 120, 47 and 24 keys at tol x0.25, x1, x4 all give max error 0.0145 | [C] |
| a smooth ease obeys `tol` | `power2.inOut`: 54, 28, 15 keys for max error 0.00052, 0.00196, 0.00713 | [C] |
| steps cannot be straight segments | `steps(6)`: 14 keys, max error 0.139 at every tolerance | [C] |
| **X_ITE gives an achromatic colour end the other end's hue** (`Color3.lerp`: s = 0 takes the partner's hue, short way round) | 4 orrery colour channels 0.0167 off until modelled, then 1.8e-6 | [C] |
| authored key times belong to one channel, not to the whole timeline | orrery 16,031 keys with global times, 2,467 with per-channel times, same tolerance | [C] |
| a bound Viewpoint under an animated Transform: X_ITE follows the parent, the three.js body did not (fixed on x3d.loom PR #75) | probe 13456, 2912, 2912 on the fixed build; demo moves the world, not the camera | [C] |
| Euler to quaternion to axis-angle | angle by `atan2`, not `acos` (acos loses 1e-8 near 0) | [C] |

## 5. Licences, plainly

| package | licence | what it means here |
|---|---|---|
| `@theatre/core` 0.7.2 | Apache-2.0 | imported to evaluate a saved state with Theatre's own curve maths |
| `@theatre/studio` 0.7.2 | AGPL-3.0-only | never imported, bundled or served; the author runs it locally and saves JSON; embedding it in a page you ship brings the AGPL to that page |
| `gsap` 3.15.1 | standard no-charge licence | free for most uses, not for tools that compete with GSAP's own; used at build time, the X3D contains none of it |

Engineering notes, not legal advice. **[L]** (registry metadata read; the GSAP licence text read at its public page, not re-read for this edition).

## Heuristics

| ID | Rule (imperative, at most 30 words) | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-ANM-1 | Interpolate colours in HSV when you model ColorInterpolator, or the bake is wrong between keys. | C | 0.059 off, then 7.6e-8 | `X_ITE 16.6.0` |
| H-ANM-2 | Use the authoring tool itself as the oracle and measure the bake on a grid the baker did not sample. | C | check grid 4x finer, offset a third | `x3d.anim/src/bake.js` |
| H-ANM-3 | Keep every authored key time as a key; thin only the samples between them. | C | key counts per channel in the table | `tools/verify.js` |
| H-ANM-4 | Raise the sample rate, not `tol`, when an ease has kinks between samples. | C | bounce.out floor 0.0145 at all tolerances | `bake()` run |
| H-ANM-5 | Give unkeyed Theatre components their rest values; a missing scale track reads as 0. | C | defaults in `tools/cases.js` | `@theatre/core 0.7.2` |
| H-ANM-6 | Never import the studio package into an exporter; read the saved state JSON. | L | AGPL-3.0-only vs Apache-2.0 | registry metadata |
| H-ANM-7 | Skip the keys with the GSAP `_gsap` record when you copy a target tree: it is circular. | C | stack overflow in the first run | `gsap 3.15.1` |
| H-ANM-8 | Give HTML ids unique names: a section id and a canvas id collide and `getElementById` returns the first. | C | two blank widgets in the demo page | Chromium 153 |
| H-ANM-9 | Give an achromatic ColorInterpolator end the partner's hue when you model HSV, as X_ITE's `Color3.lerp` does. | C | 0.0167 off on 4 channels, then 1.8e-6 | `X_ITE 16.6.0` |
| H-ANM-10 | Keep authored key times per channel, not per timeline, or every channel inherits every other's keys. | C | 16,031 keys against 2,467 | `x3d.anim/receipts/gsap-orrery.json` |
| H-ANM-11 | Move the world under a fixed camera when a scene must run on every body; a Viewpoint under an animated Transform is not followed everywhere. | C | probe 13456, 2912, 2912 on the fixed build | `x3d.loom` PR #75 |

## Drills

### D-ANM-1 Red to blue at half time
- **Level:** L2
- **Task:** In X_ITE, route a ColorInterpolator with keys `0 1` and values `1 0 0, 0 0 1` and read the colour at `set_fraction` 0.5. Predict it first.
- **Verify:** `x3d.anim/tools/xite.js` `withXite`, `loadScene`, write the fraction, read `Material.diffuseColor`.
- **Answer:** (1, 0, 1), magenta, not (0.5, 0, 0.5).
- **Checked:** `2026-11-15 X_ITE 16.6.0, Chromium 153.0.8010.12 SwiftShader`: [0.9999999999999991, 0, 1]

### D-ANM-2 What a tolerance buys
- **Level:** L2
- **Task:** Bake `power2.inOut` over 2 s at 60 fps with tol x0.25, x1, x4 and count keys and error. Then do `bounce.out` and explain why its error does not move.
- **Verify:** call `bake('e', t => ({X:{transparency: ease(t/2)}}), {X:{transparency:0}}, {duration:2, fps:60, tol})` from `x3d.anim/src/bake.js` with `gsap.parseEase`.
- **Answer:** power2.inOut 54, 28, 15 keys at 0.00052, 0.00196, 0.00713. bounce.out 120, 47, 24 keys at 0.0145 each: the error is between 60 fps samples.
- **Checked:** `2026-11-15 gsap 3.15.1, Node 22.23.4`

### D-ANM-3 Which Theatre package may be in a shipped page
- **Level:** L1
- **Task:** Read the licence of `@theatre/core` and `@theatre/studio` from the registry and say which one an exporter may import freely.
- **Verify:** `npm view @theatre/studio license`
- **Answer:** studio is `AGPL-3.0-only`, core is `Apache-2.0`. The exporter imports core only.
- **Checked:** `2026-11-15 npm registry, 0.7.2`

### D-ANM-4 Run the whole rig
- **Level:** L2
- **Task:** Run the unit tests and the verifier and read the worst bridge-vs-X_ITE value.
- **Verify:** `cd x3d.loom/x3d.anim && npm ci && npm test && CHROMIUM_EXECUTABLE=... node tools/verify.js`
- **Answer:** 17 of 17 tests pass; worst bridge vs X_ITE 7.13e-7 (Theatre), 5.51e-7 (GSAP orbit), 1.86e-6 (orrery).
- **Checked:** `2026-11-15 X_ITE 16.6.0, three.js r187, Chromium 153.0.8010.12 SwiftShader`

### D-ANM-5 Break the HSV rule
- **Level:** L3
- **Task:** Replace `lerpHsv` in `src/model.js` with a straight RGB lerp, run `node tools/verify.js`, and read the colour channel's `xiteVsOurs`.
- **Verify:** `receipts/theatre-box.json`, row `BoxMat.diffuseColor`.
- **Answer:** about 0.059 (the first-run figure) instead of 7.6e-8, and `ok` false.
- **Checked:** not run again after the first run that found it; the 0.059 figure is from that run.

### D-ANM-6 Euler convention
- **Level:** L2
- **Task:** Convert Euler (10, 20, 30) degrees to a quaternion and back with `src/math.js` and say the convention.
- **Verify:** `npm test` first test.
- **Answer:** fixed X, then Y, then Z (q = qz*qy*qx); the round trip is within 1e-9 rad.
- **Checked:** `2026-11-15 Node 22.23.4`

### D-ANM-7 Count the keys of the orrery
- **Level:** L2
- **Task:** Read `receipts/gsap-orrery.json` and give the channel count, total keys and the worst bridge-vs-X_ITE value. Then say what changed from 16,031 keys.
- **Verify:** `node tools/verify.js` then `receipts/gsap-orrery.json`.
- **Answer:** 76 channels, 2,467 keys, worst bridge vs X_ITE 1.86e-6; per-channel authored times replaced one global list.
- **Checked:** `2026-11-15 X_ITE 16.6.0, three.js r187, Chromium 153.0.8010.12 SwiftShader`

## Honest limits

- **[C]** Steps and holds are not representable: a straight segment cannot jump. A hold needs a duplicate key time or a BooleanSequencer; not built.
- **[C]** Three cases (two on a one-object stage, one 24-satellite orrery); no skinned or morphing scenes, no CoordinateInterpolator.
- **[C]** The live path was verified on X_ITE and the three.js body; the Babylon body shares the reader and SAI but was not run.
- **[S]** Theatre handle semantics for a second-segment ease at a connected key are taken from `@theatre/core` itself, not re-derived; one state fixture only.
- **[C]** Rotations pass through Euler on the way back to Theatre and GSAP, so that direction is approximate (0.05 degree tolerance).
- **[S]** Pictures are 320x240 software GL; no timing is claimed.

---

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-ANM-1 | Our interpolator model vs X_ITE, worst of 87 channels | 1.83e-06 | [C] | `X_ITE 16.6.0`, Chromium 153 SwiftShader | section 3 |
| N-ANM-2 | Bridge reader vs X_ITE, worst | 1.86e-06 | [C] | same rig plus three.js r187 body | section 3 |
| N-ANM-3 | X_ITE vs GSAP itself, worst | 0.0263 | [C] | same rig, gsap 3.15.1 | section 3 |
| N-ANM-4 | X_ITE vs Theatre itself, worst | 0.00695 | [C] | same rig, @theatre/core 0.7.2 | section 3 |
| N-ANM-5 | Live path read-back error, worst | 2.78e-17 | [C] | same rig | section 3 |
| N-ANM-6 | Pictures bridge vs X_ITE, worst PSNR and IoU | 34.02 dB, 0.9968 (orrery); 46.95 and 55.01 dB elsewhere | [C] | same rig, 320x240 | section 3 |
| N-ANM-7 | Keys written, GSAP and Theatre | 219 (orbit), 273 (Theatre), 2,467 (orrery) | [C] | `x3d.anim/receipts/*.json` | section 3 |
| N-ANM-8 | Colour error without HSV, then with | 0.059 then 7.6e-8 | [C] | X_ITE 16.6.0 | section 4 |
| N-ANM-9 | bounce.out floor at 60 fps | 0.0145 at 120, 47, 24 keys | [C] | gsap 3.15.1, Node 22 | D-ANM-2 |
| N-ANM-10 | steps(6) error | 0.139 | [C] | same | section 4 |
| N-ANM-11 | power2.inOut keys at tol x0.25, x1, x4 | 54, 28, 15 (error 0.00052, 0.00196, 0.00713) | [C] | gsap 3.15.1, Node 22 | D-ANM-2 |
| N-ANM-12 | Unit tests in `x3d.anim` | 17 of 17 pass, no browser | [C] | Node 22.23.4 | D-ANM-4 |
| N-ANM-13 | Orrery keys, global vs per-channel authored times | 16,031 vs 2,467 | [C] | `x3d.anim` bake, 76 channels | section 4 |
| N-ANM-14 | Colour error before the achromatic-hue rule, orrery | 0.0167 on 4 channels | [C] | X_ITE 16.6.0 | section 4 |

---

## Sources and provenance

| repo@sha | path | read how |
|---|---|---|
| `x3d.loom@3acc825` | `x3d.anim/*` (README, src, tools, test, receipts) | run |
| npm registry | `@theatre/core`, `@theatre/studio`, `gsap` metadata | read |
| `x3d.demo` | `docs/demos/timeline-theatre-gsap/v1` | run in headless Chromium |

Read on 2026-11-15. Private notes were not used as sources.

Siblings: [06 XITE, the oracle](06-xite-the-oracle.md), [08 The Babylon bridge](08-babylon-bridge.md), [13 Physics](13-physics.md).
