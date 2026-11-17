# 20. Compute on the GPU: WebGPU kernels for X3D workloads

> **Say it:** Five X3D features (ParticleSystem, HAnim skinning, VolumeData, NURBS patches, GaussianSplats) have per-frame arithmetic that maps to WGSL compute kernels one thread per item, and each kernel is trustworthy only because it matches an independent CPU twin, fails when a bug is planted in it, and is timed three ways that disagree. **[C]**

| field | value |
|---|---|
| chapter code | `WGC` |
| prerequisites | [02 Loom laws](02-loom-laws.md), [08 The Babylon bridge](08-babylon-bridge.md) |
| after this you can | map an X3D feature onto a compute kernel and say what the kernel ignores; write a CPU twin and a tolerance that can fail; plant a bug and watch the gate go red; read a GPU timestamp, a wall time and a rAF frame time and say why they differ; say why a sort with fewer passes can still be slower |
| sources read | `x3d.loom@7c818e3:x3d.compute/{README.md,src/,fixtures/,bench/page.js,tools/,receipts/}` (read and run) |
| instruments used | Chromium 153.0.8010.12 with the SwiftShader WebGPU adapter (software, timestamp-query present) on 4x Intel Xeon 2.10 GHz, Node v22.23.4, `x3d.loom@7c818e3`; no real GPU was used for any number in this chapter |

The bridges draw X3D by walking the scene graph on the CPU. Five features spend their time in arithmetic that has no data dependence between items: a particle step, a vertex blend, a ray, a grid vertex, a splat. That arithmetic is the part a GPU does well, and WebGPU compute lets a browser run it without leaving the page. This chapter is about the kernels in `x3d.compute` and, more than that, about the rules that made their numbers believable: the twin, the planted bug, and the three clocks. Every timing here comes from a software adapter, so read each as a scaling number, not a GPU number. Section 8 lists what only a real GPU can answer.

---

## 1. The map

```text
   X3D fixture (.x3d)                      CPU twin (JS, f64 or matched f32 order)
        |  fromX3D()                                   |
        v                                              v
   packed params + buffers  --->  WGSL kernel  --->  GPU result  ---compare(tol)---> PASS / FAIL
                                      |                                                ^
                          timestamp-query (first/last pass)                            |
                                      |                              planted mutant must turn this red
                                      v
          wall ms (submit -> onSubmittedWorkDone)      rAF dt and sustained ms per frame
```

| in scope | out of scope here |
|---|---|
| five compute kernels, their fixtures and twins, the gate, the mutation check, the three timing methods, the sort variants | drawing (the demo draws the kernel output with ordinary render pipelines), a real-GPU receipt, a WebGL2 fallback, X3D event wiring of the results |

Read next: deeper, [08 The Babylon bridge](08-babylon-bridge.md) (the CPU-side semantics these kernels shortcut); wider, [14 Methods](14-methods.md) (how a claim earns its grade).

## 2. The five kernels

One table says what each kernel computes, what it deliberately does not, and what it is checked against. "Ignored" is the column to read first: a kernel that quietly drops a field is the failure the first review found.

| kernel (entry) | X3D feature | one thread is | mapped | ignored or refused (logged in the file header or `fromX3D`) | twin |
|---|---|---|---|---|---|
| `particles.wgsl` (`step`, `seed`) | ParticleSystem | a particle | ConeEmitter position, angle, speed, variation; ForcePhysicsModel force; WindPhysicsModel direction and speed; BoundedPhysicsModel Box as a floor | emitter mass, surfaceArea, lifetimeVariation, gustiness, turbulence; cone axis other than +Y is refused; drag 0.5 and restitution 0.5 are harness constants | same pcg hash and f32 operation order |
| `skinning.wgsl` (`skin`) | HAnimHumanoid, HAnimJoint | a vertex | skinCoordIndex and skinCoordWeight reduced to the top 4 influences per vertex; joint translation, center, rotation | joint scale and scaleOrientation, skinBindingMatrix are refused; a vertex with no weight uses an identity slot | forward kinematics plus a CPU blend, and a hand-worked chain |
| `volume.wgsl` (`march`) | VolumeData | a pixel | OpacityMapVolumeStyle (front-to-back over) and ProjectionVolumeStyle MAX | transfer function is a fixed ramp, nearest-voxel sampling, orthographic yaw-only camera, other styles refused | same march and step positions |
| `nurbs.wgsl` (`tess`) | NurbsPatchSurface | a grid vertex | rational, any order to 6, uKnot and vKnot, analytic normal, area element in `normal.w` | uClosed and vClosed (periodic) refused | a different algorithm: recursive Cox-de Boor in f64 |
| `splats.wgsl` (`project`, `bitonic_*`) | GaussianSplats | a splat, or a compare-exchange | EWA projection, 3 sigma radius, culling, depth sort | spherical-harmonic colour, tile binning | f64 projection and a CPU sort of the GPU's own keys |

```text
 pcg(i, frame, k) -> particle respawn          M[j] = world(pose) * inverse(world(rest))
 vertex v: p' = sum over <=4 of w_k * M[idx_k] * p     (idx = nj means "unweighted", M = identity)
 pixel (px,py): ray o + t*d through the unit cube, slab test per axis, then steps of (tmax-tmin)/N
 grid (i,j): u = span search, basis N_p(u) by Piegl-Tiller A2.2, S = sum N_i M_j P_ij, n = Su x Sv
 splat s: z = view depth; key = f32 bits of z (culled and padding: 0xFFFFFFFF); sort keys with values
```

## 3. How a kernel earns trust

### 3.1 The twin

Each kernel has a CPU twin in `src/ref/*.js` that reads the same fixture. Three rules decided the twins:

1. **Match the order of operations when the claim is bit-level, differ in algorithm when the claim is correctness.** The particle twin copies the f32 order of operations because a respawn decision flips on one ulp. The NURBS twin is a different algorithm on purpose: if both used the same basis recurrence, one bug would sit in both.
2. **Compare relative to a floor for quantities that are small by nature.** A splat conic is about 1/sigma squared, so an absolute tolerance of 1e-3 let a swapped-term mutant survive. `compareRel(a, b, rel, floor)` fixed it.
3. **Work one case out by hand.** An independent twin shares your convention errors. The skinning suite carries a chain whose expected positions were derived on paper (section 3.3).

### 3.2 The planted bug

`tools/mutation-check.sh` rewrites one line of a kernel in the page (`?mut=` carries `[kernel, old text, new text]`), runs only that kernel's suite, and requires the suite to read `false`. The first version of this script was wrong in three ways that each made it look better than it was:

| flaw in the first version | effect | fix |
|---|---|---|
| any result other than `true` counted as caught | a crash or a missing mutation target counted as a catch | read the receipt JSON; only `pass === false` is a catch; `ERROR` and missing are failures of the check |
| `val()` cut a mutation string at its first `=` | mutants containing `=` ran as truncated text, so some "catches" were crashes | slice after the first `=` |
| one mutant (drop the degree factor in the NURBS derivative) | survived forever: normals are scale-invariant, so it is an equivalent mutant | replace it by a sign mutant and add the area element `normal.w`, which is not scale-invariant |

Result in the current version: five unmutated baselines green, then 14 of 14 mutants red. The mutants cover the drag term, the speed variation, the restitution, two skin blend weights, the over-compositing term, the cube-face clamp, the NURBS basis sign, the area element, the conic, the depth key and three lines of the bitonic network.

### 3.3 The hand-worked chain

`SK.handChain()` is three joints and five vertices. J0 and J1 rotate +90 degrees about z (J1 about its own center, 1 0 0), J2 rotates 180 degrees, and vertex 4 is weighted 0.25, 0.5, 0.25 over the three joints after renormalisation (raw weights 0.5, 1, 0.5). The work for vertex 4 at rest position (1, 2, 0), done by hand:

| joint | step | result |
|---|---|---|
| J0 (weight 0.25) | R(90) about origin: (x, y) -> (-y, x) | (-2, 1, 0) |
| J1 (weight 0.5) | undo rest translation (0,-2,0) -> (1,0,0); about center (1,0,0) a rotation leaves it fixed; translate (0,2,0) -> (1,2,0); then J0's R(90) | (-2, 1, 0) |
| J2 (weight 0.25) | undo rest translation (0,1,0) -> (1,3,0); R(180) -> (-1,-3,0); translate (0,-1,0) -> (-1,-4,0); then J0's R(90) | (4, -1, 0) |
| blend | 0.25 (-2,1,0) + 0.5 (-2,1,0) + 0.25 (4,-1,0) | (-0.5, 0.5, 0) |

The GPU returned that point to within 6.1e-17 of the hand value (threshold 1e-5). The same chain has one vertex with no weight at all, which must come back unchanged at (5, 5, 5): that exercises the identity slot, the row `M[nj]`.

### 3.4 Cases that cannot pass by luck

| kernel | case added after review | what it catches |
|---|---|---|
| particles | all uniforms non-default (speed 1.7, cone 0.4 rad, variation 0.4, wind, drag 0.8, gravity -7, floor 0.2, restitution 0.6, lifetime 1.3 s, seed 99) and n = 4093, not a multiple of 64 | a field that is ignored or swapped; the bounds check; respawn (4,093 of 4,093 respawned during the run) |
| volume | a ramp non-zero up to every face at yaw 0, pi/2, 0.6 and 2.4 | the axis-parallel slab branch; first and last sample; clamp at the faces |
| nurbs | eight patches: orders 3 to 5, rational, interior knots, unclamped repeated end knots | the end-span NaN case; basis order; weights |
| splats | 3,000 random-orientation splats seen from inside the cloud: 1,051 visible, 944 behind the near plane, 1,005 off screen | cull reasons, depth key, padding keys |

## 4. The three clocks

A frame counter, a wall clock and a GPU timestamp measure different things. The harness keeps them apart in every row of every receipt.

| clock | what it measures | where it misleads |
|---|---|---|
| GPU timestamp (`timestamp-query`) | first pass begin to last pass end, median of 12 to 15 runs after warm-up | on SwiftShader it times CPU-emulated execution; absent on some adapters |
| wall ms | `submit()` to `onSubmittedWorkDone()` | includes queue and driver latency |
| rAF dt | the interval `requestAnimationFrame` reports | stays at the display interval while the queue falls behind |
| `sustained_ms_per_frame` | (last frame done - first frame done) / (frames - 1) | the honest rate; the first version divided by N, not N-1 |

```text
 volume 256^3, 512x512, 384 steps, opacity (Chromium 153 SwiftShader, 4 cores)
   rAF dt median      16.7 ms   <- the loop looks like 60 fps
   sustained          355.7 ms  <- what the user gets
   GPU timestamp      375.5 ms
```

Timestamp rules that cost a validation error each: write `timestampWrites` with a begin index on the first pass and an end index on the last pass of a workload; a middle pass must carry none. Auto pipeline layouts drop bindings the entry point does not use statically, so `bitonic_local_sort` touches `_ = B.n;` to keep binding 0 alive.

## 5. What the workloads cost on a software adapter

All rows: Chromium 153.0.8010.12, SwiftShader, 4x Xeon 2.10 GHz, `x3d.loom@7c818e3:x3d.compute/receipts/full-swiftshader.json`, GPU timestamp medians.

| kernel | size | ms | rate |
|---|---|---|---|
| particles | 65,536 | 2.43 | 27.0 M particles/s |
| particles | 262,144 | 9.47 | 27.7 M/s |
| particles | 1,048,576 | 29.94 | 35.0 M/s |
| skinning (24 joints) | 65,536 vertices | 7.25 | 9.04 M vertices/s |
| skinning | 1,048,576 | 105.4 | 9.95 M/s |
| skinning | 2,097,152 | 187.7 | 11.2 M/s |
| volume, opacity | 64^3, 256x256, 96 steps | 28.7 | 2.29 M rays/s |
| volume, opacity | 128^3, 256x256, 192 steps | 51.9 | 1.26 M rays/s |
| volume, opacity | 256^3, 512x512, 384 steps | 375.5 | 0.70 M rays/s |
| nurbs (8x8 control, order 4x4) | 128x128 grid | 11.3 | 1.45 M vertices/s |
| nurbs | 512x512 | 156.5 | 1.68 M/s |
| nurbs | 2048x2048 | 2,389 | 1.76 M/s |

Reading the table: particle and skinning rates climb a little with size (launch overhead amortised), volume rate falls with volume size (more samples per ray), NURBS is flat (arithmetic bound at about 700 flops per vertex by estimate). Particles at 262,144 need 9.5 ms here; the same step on a real GPU is a question this chapter cannot answer.

## 6. The sort is the splat cost

Rendering splats needs them in depth order. The kernel projects every splat (one thread each), writes the key `f32 bits of depth` (culled and padding slots 0xFFFFFFFF), and sorts key and value pairs with a bitonic network. Two variants are implemented and both are exact against a CPU sort of the GPU's own keys.

| size | passes naive / tiled | project ms | naive sort ms | tiled sort ms | tiled over naive |
|---|---|---|---|---|---|
| 65,536 | 136 / 36 | 4.47 | 122.9 | 414.1 | 0.30x |
| 262,144 | 171 / 55 | 9.54 | 547.4 | 1,987 | 0.28x |
| 1,048,576 | 210 / 78 | 55.6 | 3,043 | 9,138 | 0.33x |

At one million splats the naive sort is 98.2 percent of project plus sort (3,043 of 3,098.5 ms). Optimising the projection would change the frame by under two percent. The tiled variant sorts 512-element tiles in workgroup memory with `workgroupBarrier` and uses global passes only across tiles, so it needs 78 passes where the naive network needs 210. It is also 3 to 3.6 times slower here. SwiftShader emulates workgroup barriers with real thread synchronisation, so a pass count that falls does not mean the time falls. Which variant wins on a real GPU is open; the harness answers it with `node tools/run.js --gpu`.

## 7. What the review found

A 92-agent review of the first version produced 41 findings; they are kept as received in `receipts/review-2026-11-15-untriaged.json`. The ones that were real:

| finding | cause | fix | caught by |
|---|---|---|---|
| fixture mass, surfaceArea, lifetimeVariation ignored | the kernel never read them and said so nowhere | listed in the header; the harness refuses cone axes it cannot do | all-uniform particle case |
| cone angle taken from a recomputed value | kernel and twin derived the base separately | one `cosCone` computed in f64 and passed in | particle suite and mutant |
| speed variation one-sided | `1 + v*rnd` instead of `1 + v*(2*rnd-1)` | symmetric form | variation mutant |
| volume `PixelTexture3D` header order | image is `components width height depth` then voxels, not width first | `fromX3D` reads `comp w h d` | non-cubic and header checks |
| NURBS NaN in the last span | repeated end knots made the span search step past the end | span clamp | `P_unclamped_repeat_end` patch |
| mutation check counted crashes | see 3.2 | rewritten | planted-bug run |
| sustained ms off by N/(N-1) | divided by frames, not frames minus one | fixed | receipt |

## 8. What needs a real GPU

| question | why software cannot answer | how to get the answer |
|---|---|---|
| is the tiled sort faster than the naive one | SwiftShader serialises barriers | `node tools/run.js --gpu --only=splats` |
| how many particles hold 60 fps | emulated ALU, 4 cores | `--gpu --only=particles`, read `sustained_ms_per_frame` |
| does a real canvas present | headless SwiftShader never presents a WebGPU canvas; the bridge test harness stubs the context for this reason | the demo's `?dbg=offscreen` renders offscreen and blits for screenshots; a person with a GPU opens the demo |
| does the 4-influence limit matter for production rigs | needs real rigs, not a 24-joint tube | run `SK.influences()` on a real HAnim file; it reports `dropped` |

## Heuristics

| ID | Rule | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-WGC-1 | Report sustained ms per frame beside rAF dt; a compute queue can be far behind while rAF reads the display interval. | [C] | 256^3 volume: rAF 16.7 ms, sustained 355.7 ms | `x3d.compute` receipt, SwiftShader |
| H-WGC-2 | Give each kernel a CPU twin, and where you can afford it use a different algorithm, not a port. | [C] | NURBS twin is recursive Cox-de Boor; max position diff 7.2e-7 | `x3d.loom@7c818e3`, SwiftShader |
| H-WGC-3 | Plant a bug in every gate and require an explicit red; count a crash or a missing target as a failure of the check. | [C] | first script counted crashes; now 14 of 14 | `tools/mutation-check.sh` |
| H-WGC-4 | Compare small quantities relatively with a magnitude floor; an absolute tolerance hides errors in values near 1/sigma squared. | [C] | conic mutant survived absolute 1e-3 | `compareRel`, receipt |
| H-WGC-5 | Run one case with every parameter non-default; a default fixture cannot see a field the kernel ignores. | [C] | particle case B, n = 4093 | receipt |
| H-WGC-6 | Work one expected value out by hand; a twin shares your convention errors. | [C] | FK chain, vertex 4 at (-0.5, 0.5, 0) | `SK.handChain()`, receipt |
| H-WGC-7 | Put `timestampWrites` on the first and last pass only; a middle pass with the field and no indices is a validation error. | [C] | splat passes | Chromium 153, WebGPU |
| H-WGC-8 | An auto pipeline layout drops statically unused bindings; touch the binding or write an explicit layout. | [C] | `_ = B.n;` in `bitonic_local_sort` | Chromium 153, WebGPU |
| H-WGC-9 | Profile the sort before the projection; for large splat clouds the sort is the frame. | [C] | 98.2 percent at 1,048,576 | receipt, SwiftShader |
| H-WGC-10 | Do not choose a sort variant from pass counts or from a software adapter; measure on the target GPU. | [C] | tiled 78 passes, 3.0 to 3.6x slower | receipt, SwiftShader |
| H-WGC-11 | Log in the kernel header every X3D field the kernel ignores, and make the loader refuse inputs it cannot do. | [L] | review finding on ignored particle fields | review of the first version (`x3d.loom@7c69356`), read and fixed |
| H-WGC-12 | Test pages that must screenshot a WebGPU canvas on a software adapter need an offscreen render path. | [C] | real canvas never presented | Chromium 153, SwiftShader |

## Drills

### D-WGC-1 Run the gate
- **Level:** L1
- **Task:** Run all five correctness suites without the timing runs and read which pass.
- **Verify:** from `x3d.loom/x3d.compute`: `node tools/run.js --quick --nobench --name=drill` (needs playwright on `NODE_PATH` and a Chromium)
- **Answer:** `particles`, `skinning`, `volume`, `nurbs`, `splats` all `true`, `gpu_errors` empty, about 2 s of page time.
- **Checked:** 2026-11-15 Chromium 153.0.8010.12 SwiftShader, `x3d.loom@7c818e3`

### D-WGC-2 Plant a bug
- **Level:** L3
- **Task:** Flip the sign of the NURBS basis term in the kernel through the mutation hook and confirm the NURBS gate goes red.
- **Verify:** `node tools/run.js --quick --nobench --only=nurbs --name=drill --mutate='nurbs|(*d)[r] = f32(p) * (a - b);|(*d)[r] = f32(p) * (a + b);'`
- **Answer:** `"nurbs": false` in the printed summary; with no `--mutate` the same command prints `true`.
- **Checked:** 2026-11-15 Chromium 153.0.8010.12 SwiftShader, `x3d.loom@7c818e3`

### D-WGC-3 Price the sort
- **Level:** L2
- **Task:** From `receipts/full-swiftshader.json`, compute the share of project plus naive sort that the sort takes at 1,048,576 splats.
- **Verify:** `node -e "const b=require('./receipts/full-swiftshader.json').suites.splats.bench[2];console.log(b.sort_ms_naive_derived/b.project_plus_naive_sort.gpu_ms.median)"`
- **Answer:** 0.982 (3,043 ms of 3,098.5 ms).
- **Checked:** 2026-11-15 recorded receipt, Node v22.23.4

### D-WGC-4 Do the skeleton by hand
- **Level:** L2
- **Task:** Compute the skinned position of vertex 4 of `SK.handChain()` on paper (section 3.3), then compare with the library.
- **Verify:** `node --input-type=module -e "import('./src/ref/skinning.js').then(S=>{const h=S.handChain(),i=S.influences(h.joints,h.nv),M=S.skinMatrices(h.joints,h.pose),r=S.skinCPU(h.rest,new Float32Array(h.nv*4),i.idx,i.w,M,h.nv);console.log(Array.from(r.P.slice(16,19)))})"`
- **Answer:** (-0.5, 0.5, 0) up to rounding.
- **Checked:** 2026-11-15 Node v22.23.4, `x3d.loom@7c818e3` (same computation printed all fifteen coordinates equal to the expected list)

### D-WGC-5 Read three clocks
- **Level:** L1
- **Task:** For the 256^3 opacity volume row in the receipt, list the rAF median, the sustained ms per frame and the GPU timestamp, and say which two disagree with the third.
- **Verify:** open `receipts/full-swiftshader.json`, suite `volume`, bench row `256^3`, style `opacity`.
- **Answer:** rAF 16.7 ms, sustained 355.7 ms, GPU 375.5 ms; rAF is the outlier.
- **Checked:** 2026-11-15 recorded receipt

### D-WGC-6 Break the sort
- **Level:** L3
- **Task:** Change the direction test of the first bitonic kernel and confirm the splat gate fails.
- **Verify:** `node tools/run.js --quick --nobench --only=splats --name=drill --mutate='splats|let up = (i & B.k) == 0u;|let up = (i & B.k) != 0u;'`
- **Answer:** `"splats": false`; the naive and tiled sorts both report positions wrong against the CPU sort.
- **Checked:** 2026-11-15 `tools/mutation-check.sh` (that mutant is number 12 of the 14)

## Honest limits

* Every timing is SwiftShader on 4 Xeon cores. They are scaling numbers and carry no claim about a GPU. **[C]**
* The tiled-sort result (3.0 to 3.6x slower) is a property of the software adapter until a real GPU says otherwise. **[C]** for SwiftShader, **[S]** for anything else.
* The fixtures were read by the harness and by the X3D readers in the twins; they were not run through the `x3d_mcp` validator for this chapter. **[S]**
* The volume kernel uses nearest-voxel sampling, a fixed transfer function and an orthographic yaw-only camera; the screen basis is left-handed, so the image is a horizontal mirror of a right-handed X3D camera. Kernel and twin share this, so the gate cannot see it. **[C]**
* The particle kernel ignores mass, surfaceArea and lifetimeVariation that the three.js bridge honours; the two are not interchangeable. **[C]**
* Top-4 skin influences are enough for the 144-vertex fixture (0 dropped) and the procedural tube; real rigs may need more. **[S]**
* The 92-agent review is kept as received (41 findings); only the ones in section 7 were verified and fixed, the rest were not individually closed. **[C]**
* Throughput figures quoted in the project brief for real GPUs were carried from a note and not re-checked here, so none appears in the numbers register. **[S]**

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-WGC-1 | correctness suites passing | 5 of 5 | [C] | Chromium 153.0.8010.12 SwiftShader, `x3d.loom@7c818e3` | `x3d.compute/receipts/full-swiftshader.json` |
| N-WGC-2 | full receipt run time | 391.1 s | [C] | same, 4x Xeon 2.10 GHz | same |
| N-WGC-3 | planted bugs caught | 14 of 14, with 5 of 5 green baselines | [C] | same | `x3d.compute/receipts/mutation-check.txt` |
| N-WGC-4 | review findings received | 41 | [C] | 92-agent review of the first version | `x3d.compute/receipts/review-2026-11-15-untriaged.json` |
| N-WGC-5 | particles, worst abs diff, 4,096 x 120 steps | 5.75e-4 | [C] | same | receipt, particles |
| N-WGC-6 | skinning, worst abs diff, 65,536-vertex tube | 3.8e-6 | [C] | same | receipt, skinning |
| N-WGC-7 | NURBS worst position and normal diff, 8 patches | 7.2e-7 and 1.5e-5 | [C] | same | receipt, nurbs |
| N-WGC-8 | splat projection, worst relative diff | 7.9e-5 | [C] | same | receipt, splats |
| N-WGC-9 | particle step, 262,144 particles | 9.47 ms | [C] | same, GPU timestamp | receipt |
| N-WGC-10 | skinning, 1,048,576 vertices, 24 joints | 105.4 ms | [C] | same | receipt |
| N-WGC-11 | volume 256^3, 512x512, 384 steps: GPU, sustained, rAF | 375.5, 355.7, 16.7 ms | [C] | same | receipt |
| N-WGC-12 | NURBS 512x512 grid | 156.5 ms | [C] | same | receipt |
| N-WGC-13 | splats 1,048,576: project, naive sort, tiled sort | 55.6, 3,043, 9,138 ms | [C] | same | receipt |
| N-WGC-14 | sort share of project plus naive sort at 1,048,576 | 98.2 percent | [C] | same | receipt |
| N-WGC-15 | bitonic passes at 1,048,576, naive and tiled | 210 and 78 | [C] | same | receipt |
| N-WGC-16 | edge-case splat cloud (3,000): visible, behind near, off screen | 1,051, 944, 1,005 | [C] | same | receipt, splats |
| N-WGC-17 | hand-worked chain, max error against the GPU | 6.1e-17 | [C] | same | receipt, skinning |

## Sources and provenance

`hagopjay/x3d.loom@7c818e3` folder `x3d.compute` (branch of the pull request that adds it), read and run on 2026-11-15 on the rig in the header; WGSL and WebGPU behaviour as implemented by Chromium 153.0.8010.12 (Dawn and SwiftShader), the W3C WebGPU and WGSL specifications read for the timestamp-query and layout rules. NURBS basis after Piegl and Tiller, The NURBS Book, algorithms A2.1 and A2.2; Gaussian splat projection after Zwicker et al., EWA splatting. Companion demo: `x3d.demo` `docs/demos/webgpu-compute/v1`. Nothing was run on a real GPU.
