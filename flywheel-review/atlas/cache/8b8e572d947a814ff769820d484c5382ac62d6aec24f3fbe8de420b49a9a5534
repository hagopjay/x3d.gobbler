# 19. glTF tooling that keeps X3D identity: glTF-Transform, meshopt, Draco, KTX2 and the gates around them

> **Say it:** a glb from the Blender add-on can be cut to about a third of its size, or to a tenth of it on a mesh-heavy scene, and still be proven to carry every DEF name, camera, light, material and animation channel it started with, but only if the stock glTF-Transform steps that erase names are wrapped and the result is checked by gates the Khronos validator does not have. **[C]**

| field | value |
|---|---|
| chapter code | `GTO` |
| prerequisites | [03 The validator and the gates](03-validator-and-gates.md) for what a gate can prove; [11 glTF, USD and Khronos](11-gltf-usd-khronos.md) for where the identity extras come from (H-GLT-5) |
| after this you can | (1) pick one of nine optimiser profiles for a target and say what each one promises; (2) name the glTF-Transform steps that erase X3D identity and show the loss in tokens; (3) run the identity, geometry, material and animation gates on any glb pair; (4) read a validator "0 errors" on a compressed glb without over-reading it; (5) say which consumer decodes which compression, with the grade of each row |
| sources read | x3d.loom@b6a3650:x3d.gltf/{src,bin,web,tools,tests,fixtures,receipts}; x3d-blender-io@54aba0c:docs/brag/showpieces; x3d.castle@0a1073f:results/exporter-70/sample-glb; npm package sources of `three@0.187.0`, `babylonjs@9.32.0`, `x_ite@16.7.1` (read in `node_modules`) |
| instruments used | `glTF-Transform 4.5.1`; `meshoptimizer 1.3.0`; `draco3dgltf 1.5.9`; `ktx2-encoder 0.6.0`; `Khronos glTF-Validator 2.0.0-dev.3.10`; `Node v22.23.4`; `Chromium 153.0.8010.12, SwiftShader` for the browser byte-parity test; `esbuild 0.25.12`; `three.js r187`, `Babylon.js 9.32.0`, `X_ITE 16.7.1` for the render oracle |

Grading note. Every size, count and token number below comes from `x3dgltf` runs on 2026-11-15 whose receipts are committed under `x3d.gltf/receipts/`; the Khronos validator ran in Node. Nothing here was timed on a GPU, and the render oracle ran on a software adapter. The per-engine support matrix was read from package source and graded row by row (section 8).

---

## 1. The map

```text
 X3D --(Blender + x3d-blender-io)--> glb carrying x3d_* extras on nodes, meshes, materials, scenes
                                              |
                                              v
        +--------------------------------------------------------------------+
        | x3dgltf optimize IN.glb OUT.glb --profile P                        |
        |   dedup -> prune -> weld -> [reorder] -> [instance | quantize]     |
        |   -> [EXT_meshopt_compression | KHR_draco_mesh_compression | KTX2]  |
        +--------------------------------------------------------------------+
                                              |
        +----------+-------------+------------+-------------+----------------+
        v          v             v            v             v                v
   validator   identity      geometry     materials     animation        KTX2 container
 (source and   (token        (k-d tree     (look-        (channel,        (vkFormat 0,
  decoded)      multiset)     centroids)    fields)       key times)       ETC1S/UASTC)
                                              |
                                              v
          delivered glb --> three.js / Babylon.js / X_ITE / Unreal / Castle / blenderizer
```

| in scope | not in scope |
|---|---|
| glb size, draw calls, resident GPU bytes, and what each costs in identity | rendering speed on a GPU (nothing timed) |
| the nine profiles and their written contracts | USD (see chapter 11, section 7) |
| the identity, geometry, material and animation gates, with negative controls | behaviour: ROUTEs, Scripts, PROTOs are lost before this lane starts (chapter 11, section 2) |
| a Node CLI and a browser bundle that produce the same bytes | a hosted service; the lane is a library, a CLI and a demo page |
| the per-engine decoder matrix and the render oracle | engines other than three.js, Babylon.js, X_ITE, Unreal, Blender and Castle |

Read next: deeper, [11 glTF, USD and Khronos](11-gltf-usd-khronos.md) for the extras the gates depend on; wider, [12 Unreal as a tier-1 endpoint](12-unreal-tier1.md) for the consumer that imports the optimised glb.

---

## 2. What "identity" means for a glb

The Blender add-on writes the X3D identity of every imported node into glTF `extras` (chapter 11, H-GLT-5): `x3d_def`, `x3d_def_path` (the chain of DEF'd ancestors), `x3d_use`, `x3d_viewpoint_description` on nodes, `x3d_head_meta` on the scene. Without them a glb cannot be traced back to the X3D scene it came from; the tether (chapter 01) is cut at the first optimiser that merges or drops a named node. The lane measures that as a **token multiset**: every named or tagged property becomes one string, source and output are compared as multisets, and the difference is split into lost and added.

| token kind | what it carries | example (from the PRISMATICA cathedral glb) |
|---|---|---|
| `node` | node name and its whole `extras` | `node\|Pillar_017\|{"x3d_def":"Pillar_017","x3d_def_path":["Nave","Pillar_017"]}` |
| `mesh`, `material`, `scene` | name and extras | `scene\|...\|{"x3d_head_meta":[{"name":"title",...}]}` |
| `camera`, `light` | name, extras and the projection or light parameters | `camera\|Viewpoint1\|{...}\|perspective\|0.8,0.1,100,` |
| `asset` | root extras | `asset\|{...}` |

The cathedral glb has 1,251 tokens; the contract of a profile says what may happen to them.

| contract | meaning | profiles |
|---|---|---|
| `exact` | every token survives (lost 0, added 0) | lossless, meshopt-lossless, quantized, web, web-filter, draco, web-ktx2, web-ktx2-etc1s |
| `mapped` | tags survive inside `extras.x3d_instances` of a new batch node (lost 0); the batch nodes are new | instanced |
| `lossy` | tokens may be lost; the loss is counted and printed, never hidden | static-joined, stock-instance |

A second identity check is `x3d_def_path` itself: a claim that a node sits under `Nave` is only true if the glb hierarchy still says so. The add-on writes the field as a `/`-joined string (`"Nave/Pillar_017"`), not the list the first version of this lane assumed; for most of the lane's life the check read zero claims on every real file and passed vacuously, and the gap was found by an independent reader of the lane. Parsed correctly, the cathedral carries 1,216 claims and 1,208 of them hold in the source (why the other eight do not was not traced), the `stilllife` file carries 9 and none hold, and the fixture `identity-dup` carries 4 and holds 4. For an `exact` profile the gate now fails if the output has a different number of claims or fewer that hold than the source (`src/gates.mjs`). The cathedral under `instanced` is a `mapped` contract and is not held to the claim count, because the batch nodes are new.

### 2.1 The two wrappers that make `exact` possible

Stock glTF-Transform has two steps that change identity without losing a vertex. The lane wraps both and then lets the gate prove the wrapper works.

```text
 stock instance({min:2})            instanceWithIdentity({min:2})
 ------------------------           ---------------------------------------------
 N nodes sharing a mesh             record (name, extras) of each node, in order
   -> 1 batch node, N TRS           run the stock instance()
   -> the N nodes deleted           write the records to batch.extras.x3d_instances
   -> every DEF name gone           snapshot() expands them back into N node tokens

 stock quantize()                   quantizeKeepingIdentity()
 ------------------------           ---------------------------------------------
 animated or parent node ->         same call, then mark each helper node with
   anonymous child node made          extras.x3d_wrapper_of = <parent>
   animation channels retargeted    nodeKey() resolves a wrapper to its parent, so
   to the child                       animation channels still match by target
```

Measured on the cathedral, stock `instance()` takes 1,218 draw calls to 10 and erases 1,216 of 1,251 tokens; the wrapper takes 1,218 to 10 and erases 0 (`receipts/step-probe.md`; `receipts/summary.md`). On the animated fixture, stock `quantize()` leaves 1 of 3 animation channels without a matching target; the wrapper leaves 0 of 3.

---

## 3. Step anatomy: what each glTF-Transform step does to identity

Each step ran alone on a fresh read of each glb. "Lost" counts identity tokens; "unmatched" counts animation channels that no longer find their target node.

| step | cathedral: lost of 1,251, KiB | still life: lost of 27, KiB | identity-dup: lost of 19 | animated: lost of 8, channels unmatched of 3 | repeated: lost of 47, KiB |
|---|---|---|---|---|---|
| dedup() stock | 0, 1,190.8 to 1,143.3 | 0, 1,645.4 to 1,644.9 | 2 | 0, 0 | 0, 10.6 to 10.6 |
| dedup SAFE (accessor, texture) | 0, 1,190.8 to 1,143.3 | 0, 1,645.4 to 1,644.9 | 0 | 0, 0 | 0, 10.6 to 10.6 |
| prune() stock | 0, 1,190.8 to 891.6 | 0, 1,645.4 to 1,451.7 | 0 | 0, 0 | 0, 10.6 to 9.6 |
| prune SAFE (keepLeaves, keepExtras, keepAttributes) | 0, 1,190.8 to 1,189.9 | 0, 1,645.4 to 1,644.9 | 0 | 0, 0 | 0, 10.6 to 10.6 |
| weld() | 0, 1,190.8 to 1,204.4 | 0, 1,645.4 to 1,644.9 | 0 | 0, 0 | 0, 10.6 to 10.6 |
| reorder() | 0, 1,190.8 to 1,189.9 | 0, 1,645.4 to 1,644.9 | 0 | 0, 0 | 0, 10.6 to 10.6 |
| quantize() stock | 0, 1,190.8 to 877.9 | 0, 1,645.4 to 1,353.5 | 0 | 0, 1 | 0, 10.6 to 9.4 |
| quantize wrapper (marks helper nodes) | 0, 1,190.8 to 877.9 | 0, 1,645.4 to 1,353.5 | 0 | 0, 0 | 0, 10.6 to 9.4 |
| meshopt() stock | 0, 1,190.8 to 583.8 | 0, 1,645.4 to 982.7 | 0 | 0, 1 | 0, 10.6 to 8.4 |
| draco() stock | 0, 1,190.8 to 507.1 | 0, 1,645.4 to 808.2 | 0 | 0, 0 | 0, 10.6 to 6.8 |
| flatten() | 0, 1,190.8 to 1,189.9 | 1, 1,645.4 to 1,644.8 | 1 | 0, 0 | 0, 10.6 to 10.6 |
| join() | 1208, 1,190.8 to 16,482.7 | 0, 1,645.4 to 1,644.9 | 1 | 0, 0 | 39, 10.6 to 193.0 |
| palette({min:5}) | 10 (+5), 1,190.8 to 1,309.5 | 0, 1,645.4 to 1,644.9 | 0 | 0, 0 | 0, 10.6 to 10.6 |
| instance({min:2}) stock | 1216, 1,190.8 to 843.8 | 0, 1,645.4 to 1,644.9 | 2 | 0, 0 | 40, 10.6 to 7.7 |
| instance wrapper (stamps x3d_instances) | 0, 1,190.8 to 980.4 | 0, 1,645.4 to 1,644.9 | 0 | 0, 0 | 0, 10.6 to 9.3 |
| simplify(0.5) | 0, 1,190.8 to 845.8 | 0, 1,645.4 to 1,279.0 | 0 | 0, 0 | 0, 10.6 to 10.2 |
| resample() | 0, 1,190.8 to 1,189.9 | 0, 1,645.4 to 1,644.9 | 0 | 0, 0 | 0, 10.6 to 10.6 |
| sparse() | 0, 1,190.8 to 1,189.9 | 0, 1,645.4 to 1,644.9 | 0 | 0, 0 | 0, 10.6 to 10.6 |

What the table says, ranked by damage:

| rank | step | measured effect | why |
|---|---|---|---|
| 1 | `join()` | cathedral: 1,208 of 1,251 tokens lost, 1,190.8 KiB to 16,482.7 KiB (13.8 times) | merges meshes; each source mesh and node name has nowhere to live |
| 2 | `instance({min:2})` | cathedral: 1,216 tokens lost, size down to 843.8 KiB | deletes the N nodes it folds into a batch |
| 3 | `palette({min:5})` | cathedral: 10 lost, 5 added | collapses near-identical materials into a palette |
| 4 | `dedup()` (default) | `identity-dup` fixture: 2 lost | merges accessors, meshes and materials that differ only by name |
| 5 | `flatten()` | still life: 1 tagged token lost | removes a transform-only node that carried a DEF |
| 6 | `quantize()`, `meshopt()` stock | animated fixture: 1 of 3 channels unmatched | anonymous helper node takes over the weights channel |

The steps that are safe as they are: `reorder()`, `resample()`, `sparse()`, stock `draco()`, `weld()` and `simplify()` lost 0 tokens on every file probed. Safe on identity is not the same as free: `weld()` grew the cathedral from 1,190.8 KiB to 1,204.4 KiB, and `simplify(0.5)` removes triangles, which the geometry gate then refuses for an `exact` or bit-bounded profile.

---

## 4. The nine profiles

| profile | contract | writes | steps | use it when |
|---|---|---|---|---|
| `lossless` | exact / exact | nothing | dedup(accessor, texture), prune(keep extras), weld | you want a canonical, deduplicated glb with nothing new in `extensionsUsed` |
| `meshopt-lossless` | exact / exact | EXT_meshopt_compression | lossless + reorder + meshopt on unquantized data | bit-exact floats, smaller on the wire |
| `quantized` | exact / 14-bit | KHR_mesh_quantization | lossless + quantize(14/10/12) | the consumer reads quantization but not meshopt |
| `web` | exact / 14-bit | quantization, meshopt | quantized + reorder + meshopt | the default for browsers (the `gltfpack -c` family) |
| `web-filter` | exact / 14-bit | quantization, meshopt | web with meshopt filters | the wire is brotli and bytes before decompression matter least |
| `draco` | exact / 14-bit | KHR_draco_mesh_compression | lossless + Draco edgebreaker | the consumer has a Draco decoder and no meshopt |
| `web-ktx2` | exact / 14-bit | web + KHR_texture_basisu | web + UASTC KTX2 textures | VRAM matters more than transfer size |
| `web-ktx2-etc1s` | exact / 14-bit | web + KHR_texture_basisu | web + ETC1S KTX2 textures | smallest textures, visible block artefacts on gradients |
| `instanced` | mapped / 14-bit | web + EXT_mesh_gpu_instancing | web + instanceWithIdentity | a scene of hundreds of repeated shapes |

Two more profiles exist to be measured and never shipped: `static-joined` (flatten and join, the draw-call crunch) and `stock-instance` (glTF-Transform's own `instance()`). They are the traps of section 3 as profiles, so the matrix and the browser demo can show the cost next to the safe path. `x3dgltf profiles` prints the list with the contract of each.

Geometry bounds are written in the contract, not in the gate: `exact` allows a centroid deviation of 1e-7 of the scene diagonal (one float32 ULP is 1.19e-7), `bits:N` allows 2^-(N-1): 1.22e-4 for 14 bits, 4.88e-4 for 12.

---

## 5. The gates

`x3dgltf verify SRC OUT --profile P` runs five checks and the CLI exits 1 if any fails. The portable ones (identity, geometry, materials, animation) are one module that runs in Node and in the browser bundle.

| gate | what it computes | bound | negative control (test in `tests/lane.test.mjs`) |
|---|---|---|---|
| identity | token multiset difference, source vs output; `x3d_def_path` claims that still hold | exact: lost 0 and added 0; mapped: lost 0 | a stock `dedup()` on the name-only duplicate fixture fails it |
| geometry, triangles | non-degenerate triangle count; zero-area triangles are counted apart | exact: no change; bits: collapse at most max(16, 0.1%) of the solid triangles | `static-joined` on the cathedral fails (18,994 collapsed) |
| geometry, centroids | every source triangle matched to the nearest output triangle centroid through a static k-d tree, deviation as a fraction of the scene diagonal | contract bound; unmatched must be 0; bounds within 2x; area within max(20x bound, 1e-9) | a 0.1% scale change on a node fails it |
| geometry, normals | angle between matched triangle normals, p99 | 1 degree for quantized, 1e-3 for exact; a dropped normal counts as a failure unless identity is lossy | `static-joined` on thalassa: p99 68.2 degrees |
| materials | look-defining material fields after normalising through the lane's own reader and writer; texture indices scrubbed | identical | altering a base colour fails it |
| animation | channels matched by animation name, target node key and path; exact keys or linear-resampled compare | unmatched 0; exact profiles: value delta 0 | shifting one keyframe fails it |
| validator | Khronos validator on the source, the delivered file and, if compressed, the decoded canonical file | errors 0; unexplained warnings not above the source's | a corrupted accessor fails it |
| KTX2 container | vkFormat 0, ETC1S (163) or UASTC (166), BasisLZ for ETC1S, mip chain, multiple-of-4 sizes | problems empty | n/a (container advisories only) |

Why a k-d tree: the first matcher used a grid and did not finish in 250 s on the 600,976-triangle cathedral; the tree compares it with itself in 2.0 s. Why centroids and not vertices: an optimiser may reorder, weld, split or quantize vertices, but a triangle that survives keeps its centroid within the quantization step.

### 5.1 A worked bound: the 2.19e-9 that was not a bug

The Castle exporter's `annotation-standard` glb (1,404 triangles, diagonal 5.72) failed the first, stricter exact bound of 1e-9 with a deviation of 2.19e-9 on `lossless` and `meshopt-lossless`. Cause, found by running one step at a time: the file stores each node as a 4x4 `matrix`; glTF-Transform decomposes a matrix to translation, rotation and scale on read, and its writer snaps a scale within float32 noise of 1 (here 1.0000000367) to the default. The source scale error is the float32 rounding of the matrix, 1.2e-7 at worst. The bound for `exact` became one float32 ULP, and two tests pin it: a `matrix` node carrying 1.00000004 scales passes `lossless`, and a real 0.1% scale change on the same nodes still fails the geometry gate.

```bash
cd x3d.gltf && node --test tests/*.test.mjs   # 13 lane tests + 4 browser parity tests
```

---

## 6. The validator gap

`Khronos glTF-Validator 2.0.0-dev.3.10` does not know `EXT_meshopt_compression`, `KHR_draco_mesh_compression`, `KHR_texture_basisu` or `EXT_mesh_gpu_instancing`: it reports them as unknown extensions and can say nothing about the data inside. A compressed glb passes with "0 errors" and the geometry is unchecked (chapter 11, H-GLT-2). The lane closes the gap twice.

1. **Canonical file.** `validateDelivery` decodes the delivered glb (meshopt, Draco; compression extensions disposed), rewrites it as plain glTF and validates that too. The report prints both, and `extensionsNotValidated` next to every pass.
2. **Explained warnings.** `KHR_texture_basisu` images trigger a validator warning that is a property of the validator, not of the file; the lane counts those as `explainedWarnings` and fails only on `unexplainedWarnings` above the source's own count. The KTX2 container is checked separately by `ktx2check.mjs` (section 5).

Over the 132 matrix cells, the delivered file had validator errors in 0; the decoded canonical file was validated in 95 cells (errors in 0); the validator named an extension it does not check in 104 cells (EXT_meshopt_compression 84, EXT_mesh_gpu_instancing 28, KHR_draco_mesh_compression 11, KHR_texture_basisu 2). Source: `receipts/matrix/matrix.json`, field `validator`.

---

## 7. Measured: the corpus matrix

The matrix ran every profile on 12 glbs: the four add-on showpieces, `stars-view`, five files from the Unreal lane (the cathedral static, animated and static-instanced, and the thalassa exhibition plain and instanced) and two Castle exporter files. File names, sizes and sha256 are in `receipts/corpus.json`; the per-cell receipts are in `receipts/matrix/`. Brotli is level 11 and gzip is level 9 (Node `zlib`).

**Profile totals over the corpus** (sum over the files each profile ran on; "gates pass" counts files)

| profile | files | gates pass | KiB before | KiB after | % of before | gzip % | brotli % | identity tokens lost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| lossless | 12 | 12/12 | 17180.6 | 17702.4 | 103.0% | 106.5% | 102.6% | 0 |
| meshopt-lossless | 12 | 12/12 | 17180.6 | 11652.3 | 67.8% | 88.8% | 106.4% | 0 |
| quantized | 12 | 12/12 | 17180.6 | 9965.3 | 58.0% | 74.4% | 73.2% | 0 |
| web | 12 | 12/12 | 17180.6 | 6154.1 | 35.8% | 50.2% | 60.6% | 0 |
| web-filter | 12 | 12/12 | 17180.6 | 5646.1 | 32.9% | 44.7% | 54.3% | 0 |
| draco | 12 | 12/12 | 17180.6 | 7690.4 | 44.8% | 57.5% | 69.7% | 0 |
| web-ktx2 | 12 | 12/12 | 17180.6 | 6327.5 | 36.8% | 52.6% | 63.9% | 0 |
| web-ktx2-etc1s | 12 | 12/12 | 17180.6 | 5590.4 | 32.5% | 42.5% | 50.3% | 0 |
| instanced | 12 | 12/12 | 17180.6 | 5515.1 | 32.1% | 49.2% | 58.8% | 0 |
| static-joined | 12 | 8/12 | 17180.6 | 10696.8 | 62.3% | 40.8% | 43.8% | 5945 |
| stock-instance | 12 | 12/12 | 17180.6 | 16768.7 | 97.6% | 104.7% | 100.9% | 4150 |

**Per file: the smallest profile that passed every gate, by raw bytes and by brotli**

| glb | KiB source | gzip KiB | brotli KiB | smallest passing (raw) | KiB | % | smallest passing (brotli) | brotli KiB | % | draw calls source -> instanced | identity tokens |
|---|---:|---:|---:|---|---:|---:|---|---:|---:|---|---:|
| asterion.glb | 4404.4 | 624.0 | 359.9 | web-filter | 420.9 | 9.6% | draco | 112.2 | 31.2% | 284 -> 284 | 587 |
| lumen.glb | 2689.1 | 1252.2 | 550.8 | draco | 231.3 | 8.6% | web-filter | 106.3 | 19.3% | 34 -> 34 | 86 |
| prismatica-aurora-cathedral.glb | 1190.8 | 525.5 | 384.8 | instanced | 445.4 | 37.4% | draco | 125.3 | 32.6% | 1218 -> 10 | 1251 |
| stilllife-addon.glb | 1645.4 | 1098.8 | 908.5 | web-ktx2-etc1s | 509.1 | 30.9% | web-ktx2-etc1s | 368.3 | 40.5% | 5 -> 5 | 27 |
| stars-view.glb | 40.7 | 25.7 | 22.5 | web | 20.6 | 50.7% | web | 12.5 | 55.6% | 1 -> 1 | 8 |
| prismatica-aurora-cathedral-animated.glb | 4630.0 | 2557.1 | 2289.0 | web-filter | 1857.8 | 40.1% | quantized | 1261.0 | 55.1% | 1218 -> 1218 | 1251 |
| prismatica-aurora-cathedral-static.glb | 1072.1 | 521.3 | 390.8 | instanced | 341.0 | 31.8% | draco | 123.0 | 31.5% | 1218 -> 10 | 1251 |
| prismatica-aurora-cathedral-static-instanced.glb | 844.0 | 487.8 | 366.4 | draco | 159.9 | 19.0% | draco | 101.4 | 27.7% | 10 -> 10 | 43 |
| thalassa-exhibition.glb | 480.3 | 96.4 | 75.6 | instanced | 175.2 | 36.5% | instanced | 37.4 | 49.4% | 1719 -> 8 | 1737 |
| thalassa-exhibition-instanced.glb | 122.3 | 38.8 | 33.3 | draco | 85.8 | 70.1% | draco | 31.9 | 95.9% | 8 -> 8 | 26 |
| docs__demos__blender-x3d-io__v1__scenes__annotation-standard.glb | 37.7 | 16.3 | 9.9 | draco | 11.0 | 29.1% | web-filter | 4.7 | 47.6% | 5 -> 5 | 16 |
| docs__demos__blender-x3d-io__v1__scenes__lights-before.glb | 23.7 | 12.4 | 8.3 | draco | 6.6 | 27.6% | draco | 3.7 | 45.0% | 3 -> 3 | 13 |

**The two traps, every file** (a lossy contract passes when its bounds hold; the identity column is the cost)

| glb | profile | draw calls | nodes | triangles (source -> out) | identity tokens lost of source | KiB source -> out | gates |
|---|---|---|---|---|---:|---|---|
| asterion.glb | stock-instance | 284 -> 284 | 288 -> 288 | 93682 -> 93682 | 0 of 587 | 4404.4 -> 4851.9 | pass (loss is allowed and counted) |
| asterion.glb | static-joined | 284 -> 10 | 288 -> 14 | 93682 -> 93682 | 548 of 587 | 4404.4 -> 1026.9 | pass (loss is allowed and counted) |
| lumen.glb | stock-instance | 34 -> 34 | 39 -> 39 | 89568 -> 89568 | 0 of 86 | 2689.1 -> 2697.2 | pass (loss is allowed and counted) |
| lumen.glb | static-joined | 34 -> 7 | 39 -> 12 | 89568 -> 89568 | 54 of 86 | 2689.1 -> 553.2 | pass (loss is allowed and counted) |
| prismatica-aurora-cathedral.glb | stock-instance | 1218 -> 10 | 1224 -> 16 | 600976 -> 600976 | 1216 of 1251 | 1190.8 -> 858.3 | pass (loss is allowed and counted) |
| prismatica-aurora-cathedral.glb | static-joined | 1218 -> 10 | 1224 -> 16 | 600976 -> 600976 | 1208 of 1251 | 1190.8 -> 1383.5 | FAIL: 18994 triangles collapsed (more than 0.1% of 600; normals p99 1.412 degrees exceeds 1 |
| stilllife-addon.glb | stock-instance | 5 -> 5 | 11 -> 11 | 27560 -> 27560 | 0 of 27 | 1645.4 -> 1644.9 | pass (loss is allowed and counted) |
| stilllife-addon.glb | static-joined | 5 -> 5 | 11 -> 10 | 27560 -> 27560 | 1 of 27 | 1645.4 -> 990.6 | pass (loss is allowed and counted) |
| stars-view.glb | stock-instance | 1 -> 1 | 4 -> 4 | 0 -> 0 | 0 of 8 | 40.7 -> 40.7 | pass (loss is allowed and counted) |
| stars-view.glb | static-joined | 1 -> 1 | 4 -> 3 | 0 -> 0 | 1 of 8 | 40.7 -> 22.6 | pass (loss is allowed and counted) |
| prismatica-aurora-cathedral-animated.glb | stock-instance | 1218 -> 1218 | 1224 -> 1224 | 584592 -> 584592 | 0 of 1251 | 4630.0 -> 4643.0 | pass (loss is allowed and counted) |
| prismatica-aurora-cathedral-animated.glb | static-joined | 1218 -> 10 | 1224 -> 16 | 584592 -> 584592 | 1208 of 1251 | 4630.0 -> 1821.2 | FAIL: 18994 triangles collapsed (more than 0.1% of 584; normals p99 1.412 degrees exceeds 1 |
| prismatica-aurora-cathedral-static.glb | stock-instance | 1218 -> 10 | 1224 -> 16 | 600976 -> 600976 | 1216 of 1251 | 1072.1 -> 856.9 | pass (loss is allowed and counted) |
| prismatica-aurora-cathedral-static.glb | static-joined | 1218 -> 10 | 1224 -> 16 | 600976 -> 600976 | 1208 of 1251 | 1072.1 -> 1381.7 | FAIL: 18994 triangles collapsed (more than 0.1% of 600; normals p99 1.412 degrees exceeds 1 |
| prismatica-aurora-cathedral-static-instanced.glb | stock-instance | 10 -> 10 | 16 -> 16 | 600976 -> 600976 | 0 of 43 | 844.0 -> 857.2 | pass (loss is allowed and counted) |
| prismatica-aurora-cathedral-static-instanced.glb | static-joined | 10 -> 10 | 16 -> 16 | 600976 -> 600976 | 0 of 43 | 844.0 -> 182.4 | pass (loss is allowed and counted) |
| thalassa-exhibition.glb | stock-instance | 1719 -> 8 | 1721 -> 10 | 686712 -> 686712 | 1718 of 1737 | 480.3 -> 130.4 | pass (loss is allowed and counted) |
| thalassa-exhibition.glb | static-joined | 1719 -> 5 | 1721 -> 7 | 686712 -> 686712 | 1717 of 1737 | 480.3 -> 3204.0 | FAIL: 401116 triangles collapsed (more than 0.1% of 68; centroid deviation 3.69e-2 of the diagonal excee; normals p99 68.173 degrees exceeds 1 |
| thalassa-exhibition-instanced.glb | stock-instance | 8 -> 8 | 10 -> 10 | 686712 -> 686712 | 0 of 26 | 122.3 -> 130.7 | pass (loss is allowed and counted) |
| thalassa-exhibition-instanced.glb | static-joined | 8 -> 8 | 10 -> 10 | 686712 -> 686712 | 0 of 26 | 122.3 -> 101.9 | pass (loss is allowed and counted) |
| docs__demos__blender-x3d-io__v1__scenes__annotation-standard.glb | stock-instance | 5 -> 5 | 10 -> 10 | 1404 -> 1404 | 0 of 16 | 37.7 -> 34.8 | pass (loss is allowed and counted) |
| docs__demos__blender-x3d-io__v1__scenes__annotation-standard.glb | static-joined | 5 -> 5 | 10 -> 10 | 1404 -> 1404 | 0 of 16 | 37.7 -> 16.0 | pass (loss is allowed and counted) |
| docs__demos__blender-x3d-io__v1__scenes__lights-before.glb | stock-instance | 3 -> 3 | 6 -> 6 | 974 -> 974 | 0 of 13 | 23.7 -> 22.8 | pass (loss is allowed and counted) |
| docs__demos__blender-x3d-io__v1__scenes__lights-before.glb | static-joined | 3 -> 3 | 6 -> 6 | 974 -> 974 | 0 of 13 | 23.7 -> 12.8 | pass (loss is allowed and counted) |

Ranked findings from those tables. Each is [C] for the corpus and the tool versions above, and none is a claim about any other file.

| rank | finding | numbers |
|---|---|---|
| 1 | the traps are cheap to fall into and invisible to a size check | cathedral `stock-instance`: 1,218 to 10 draw calls, smaller by 27.9%, gates PASS, 1,216 of 1,251 tokens gone; thalassa `stock-instance` 480.3 to 130.4 KiB with 1,718 of 1,737 gone; thalassa `static-joined` grows 480.3 to 3,204.0 KiB and loses 401,116 triangles |
| 2 | `instanced` is the smallest shipping profile on repeated-shape scenes and loses nothing | prismatica-aurora-cathedral-static: 1,218 to 10 draw calls, 1,072.1 to 341.0 KiB (31.8%), 0 lost; prismatica-aurora-cathedral: 1,218 to 10 draw calls, 1,190.8 to 445.4 KiB (37.4%), 0 lost; thalassa-exhibition: 1,719 to 8 draw calls, 480.3 to 175.2 KiB (36.5%), 0 lost |
| 3 | Draco's raw win mostly disappears on the wire; meshopt filters keep theirs | corpus totals: `draco` 44.8% raw but 69.7% brotli, `web-filter` 32.9% and 54.3%; per file `draco` is the smallest passing profile on 5 of 12 files by raw bytes and 6 by brotli |
| 4 | `lossless` is not a no-op and can grow a file | `lossless` totals 103.0% of the source over the corpus; it grew 8 of 12 files, the most on asterion (4,404.4 to 4,851.9 KiB, 110.2%) and the cathedral (`weld()` alone: 1,190.8 to 1,204.4 KiB) |
| 5 | UASTC KTX2 saves GPU memory and costs transfer bytes | still life: `web` 1,072.7 KiB, `web-ktx2` (UASTC) 1,246.2 KiB, `web-ktx2-etc1s` 509.1 KiB; texture memory (glTF-Transform's formula) 5,461.3 KiB under `web`, 1,365.4 under UASTC, 682.7 under ETC1S |
| 6 | Draco drops zero-area triangles; quantization collapses sub-step triangles | lumen quantized: 8 triangles collapsed below the quantization step; lumen web: 8 triangles collapsed below the quantization step; lumen web-filter: 8 triangles collapsed below the quantization step; lumen draco: 6 triangles collapsed below the quantization step |

---

## 8. Which consumer decodes what

Every row was read from the consumer's own source or documentation, then re-checked by a second reader who tried to refute it (147 rows re-checked, 146 confirmed). Grades: [C] means the exact code was read or the case was run (three.js, Babylon.js and X_ITE in headless Chromium, `Chromium 153.0.8010.12`, software GL); [L] means an Epic API page, release note or staff post, because the Unreal Engine source is not readable here; a cell with two entries differs between the versions named.

| feature | three.js r187 | Babylon.js 9.32.0 | X_ITE 16.7.1 | Unreal Interchange 5.5 to 5.8 | Blender 5.3 import | Castle 7.0-alpha.3 reader |
|---|---|---|---|---|---|---|
| KHR_draco_mesh_compression | yes [C] | yes [C] | yes [C] | yes [L] | yes [C] | no [C] |
| EXT_meshopt_compression | not read | not read | not read | no [L] | not read | not read |
|   its filters and modes | yes [C] | partial [C] | yes [C] | no [L] | yes [C] | no [C] |
| KHR_mesh_quantization | yes [C] | yes [C] | yes [C] | yes [L] | yes [C] | partial [C] |
| KHR_texture_basisu (KTX2) | yes [C] | yes [C] | yes [C] | no [L] | partial [C] | no [C] |
| EXT_texture_webp | yes [C] | yes [C] | yes [C] | no [L] | yes [C] | no [C] |
| KHR_texture_transform | yes [C] | yes [C] | yes [C] | yes [L] | yes [C] | yes [C] |
| EXT_mesh_gpu_instancing | yes [C] | yes [C] | partial [C] | no [L] | yes [C] | no [C] |
| KHR_materials_unlit | yes [C] | yes [C] | yes [C] | yes [L] | yes [C] | yes [C] |
| KHR_lights_punctual | yes [C] | yes [C] | partial [C] | yes [L] | yes [C] | yes [C] |
| specular, ior, emissive_strength, clearcoat | yes [C] | yes [C] | yes [C] | yes [L] | yes [C] | no [C] |
| morph targets, animated weights | yes [C] | yes [C] | partial [C] | partial [S] 5.5; yes [L] 5.6-5.8 | yes [C] | no [C] |
| node, mesh, material extras after load | yes [C] | partial [C] | no [C] | yes [L] 5.5-5.8; unknown [S] 5.5-5.8 | yes [C] | yes [C] |
| unknown required extension | partial [C] | yes [C] | no [C] | unknown [S] | yes [C] | yes [C] |

The same table turned into the question the lane asks: **can this consumer read what the profile writes?** A profile reads when every extension it writes is a "yes". Derived from the table above, so it carries the weaker grade of the rows it uses.

| profile | three.js r187 | Babylon.js 9.32.0 | X_ITE 16.7.1 | Unreal Interchange 5.5 to 5.8 | Blender 5.3 import | Castle 7.0-alpha.3 reader |
|---|---|---|---|---|---|---|
| `lossless` | reads | reads | reads | reads | reads | reads |
| `meshopt-lossless` | does not read | does not read | does not read | does not read | does not read | does not read |
| `quantized` | reads | reads | reads | reads | reads | reads in part |
| `web` | does not read | does not read | does not read | does not read | does not read | does not read |
| `web-filter` | does not read | does not read | does not read | does not read | does not read | does not read |
| `draco` | reads | reads | reads | reads | reads | does not read |
| `web-ktx2` | does not read | does not read | does not read | does not read | does not read | does not read |
| `web-ktx2-etc1s` | does not read | does not read | does not read | does not read | does not read | does not read |
| `instanced` | does not read | does not read | does not read | does not read | does not read | does not read |

Decisions that fall out of those two tables, ranked by how much damage the wrong choice does.

| rank | consumer | what the rows say | what to do |
|---|---|---|---|
| 1 | Castle 7.0-alpha.3 | reads no Draco, no meshopt, no KTX2, no `EXT_mesh_gpu_instancing`; a glb that requires none of them still loads, an instanced one shows one copy of each mesh, a KTX2-only texture loads untextured, with no warning [C, read from source] | send it `lossless`; never `instanced` or the KTX2 profiles |
| 2 | Unreal Interchange 5.5 to 5.8 | reads Draco and quantization; no meshopt, no KTX2, no instancing extension [L] | send it `quantized` or `draco`; never `web`, `web-filter` or `instanced` |
| 3 | X_ITE 16.7.1 | drops node, mesh and material extras on glb import, so the `x3d_def` tags are not in the X3D scene it builds; ignores an unknown required extension without a warning [C] | judge identity by the lane's gate, not by what X_ITE shows |
| 4 | Babylon.js 9.32.0 | fetches its Draco, meshopt and KTX2 decoders from its CDN at run time (not in the npm packages); the CDN meshopt decoder is built from meshoptimizer 0.20 and has no COLOR filter; keeps node and material extras but not mesh extras [C] | allow the CDN or mirror the decoders; test `web-filter` on a glb with vertex colours before shipping it |
| 5 | three.js r187 | decodes everything the lane writes once `DRACOLoader`, `KTX2Loader` and `MeshoptDecoder` are set; a missing decoder fails only when the extension is required [C] | wire the three decoders; `userData` carries every extra |
| 6 | Blender 5.3 import | reads all of it, including instancing as real instances; aborts on an unknown required extension [C] | the round trip back to Blender works for every profile |




---

## 9. The render oracle

`x3d.gltf/render/` loads one glb in three.js r187, Babylon.js 9.32.0 and X_ITE 16.7.1 (headless `Chromium 153.0.8010.12`, ANGLE over SwiftShader, 256 px, local decoders, every non-localhost request blocked) from a camera framed on the **original** file, and measures how far the picture of an optimised file moved from the same engine's picture of the original. Cross-engine differences are not used, because the engines light and tone-map differently; only same-engine deltas mean anything. The oracle's determinism test renders each file twice, the second time in a freshly launched Chromium, and asserts a mean delta below 0.5; the recorded delta was 0.0000 in all three engines (`render/README.md`).

Here the oracle was pointed at the lane's own profiles: 4 showpieces, 114 engine-profile cells, 111 loaded, 1 did not load, 2 not run. Each cell: mean absolute delta over R, G, B and the share of pixels whose largest channel moved by more than 16.

**stilllife**

| profile | KiB | gates | identity lost | three: mean delta / px>16 | babylon: mean delta / px>16 | xite: mean delta / px>16 |
|---|---:|---|---:|---|---|---|
| lossless | 1,644.9 | pass | 0 of 27 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| meshopt-lossless | 1,335.1 | pass | 0 of 27 | 0.000 / 0.002% | 0.000 / 0.000% | 0.001 / 0.002% |
| quantized | 1,353.5 | pass | 0 of 27 | 0.008 / 0.014% | 0.008 / 0.014% | 0.008 / 0.015% |
| web | 1,072.7 | pass | 0 of 27 | 0.008 / 0.014% | 0.008 / 0.014% | 0.008 / 0.015% |
| web-filter | 982.7 | pass | 0 of 27 | 0.030 / 0.023% | 0.028 / 0.032% | 0.023 / 0.024% |
| draco | 808.2 | pass | 0 of 27 | 0.010 / 0.006% | 0.009 / 0.009% | 0.007 / 0.006% |
| instanced | 1,072.7 | pass | 0 of 27 | 0.008 / 0.014% | 0.008 / 0.014% | 0.008 / 0.015% |
| web-ktx2 | 1,246.2 | pass | 0 of 27 | 0.010 / 0.014% | not run (KTX2 decoders are CDN-only) | 0.025 / 0.020% |
| web-ktx2-etc1s | 509.1 | pass | 0 of 27 | 0.013 / 0.014% | not run (KTX2 decoders are CDN-only) | 0.025 / 0.020% |
| stock-instance | 1,644.9 | pass | 0 of 27 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| static-joined | 990.6 | pass | 1 of 27 | 0.008 / 0.014% | 0.008 / 0.014% | 0.008 / 0.015% |

**prismatica**

| profile | KiB | gates | identity lost | three: mean delta / px>16 | babylon: mean delta / px>16 | xite: mean delta / px>16 |
|---|---:|---|---:|---|---|---|
| lossless | 1,204.4 | pass | 0 of 1251 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| meshopt-lossless | 913.9 | pass | 0 of 1251 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| quantized | 877.9 | pass | 0 of 1251 | 0.054 / 0.018% | 0.074 / 0.017% | 0.013 / 0.012% |
| web | 638.0 | pass | 0 of 1251 | 0.054 / 0.018% | 0.074 / 0.017% | 0.013 / 0.012% |
| web-filter | 583.8 | pass | 0 of 1251 | 0.057 / 0.018% | 0.081 / 0.017% | 0.020 / 0.012% |
| draco | 507.1 | pass | 0 of 1251 | 0.022 / 0.008% | 0.020 / 0.008% | 0.009 / 0.008% |
| instanced | 445.4 | pass | 0 of 1251 | 0.054 / 0.018% | 0.074 / 0.017% | 0.013 / 0.012% |
| stock-instance | 858.3 | pass | 1216 of 1251 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| static-joined | 1,383.5 | FAIL | 1208 of 1251 | 0.059 / 0.029% | 0.079 / 0.027% | did not load |

**asterion**

| profile | KiB | gates | identity lost | three: mean delta / px>16 | babylon: mean delta / px>16 | xite: mean delta / px>16 |
|---|---:|---|---:|---|---|---|
| lossless | 4,851.9 | pass | 0 of 587 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| meshopt-lossless | 2,898.5 | pass | 0 of 587 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| quantized | 824.7 | pass | 0 of 587 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| web | 497.0 | pass | 0 of 587 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| web-filter | 420.9 | pass | 0 of 587 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| draco | 585.0 | pass | 0 of 587 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| instanced | 497.0 | pass | 0 of 587 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| stock-instance | 4,851.9 | pass | 0 of 587 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| static-joined | 1,026.9 | pass | 548 of 587 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |

**lumen**

| profile | KiB | gates | identity lost | three: mean delta / px>16 | babylon: mean delta / px>16 | xite: mean delta / px>16 |
|---|---:|---|---:|---|---|---|
| lossless | 2,697.2 | pass | 0 of 86 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| meshopt-lossless | 1,372.7 | pass | 0 of 86 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| quantized | 1,692.0 | pass | 0 of 86 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| web | 644.1 | pass | 0 of 86 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| web-filter | 490.7 | pass | 0 of 86 | 0.001 / 0.000% | 0.001 / 0.000% | 0.002 / 0.006% |
| draco | 231.3 | pass | 0 of 86 | 0.000 / 0.000% | 0.000 / 0.000% | 0.001 / 0.000% |
| instanced | 644.1 | pass | 0 of 86 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| stock-instance | 2,697.2 | pass | 0 of 86 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |
| static-joined | 553.2 | pass | 54 of 86 | 0.000 / 0.000% | 0.000 / 0.000% | 0.000 / 0.000% |

What the tables say. The largest mean delta of any profile that passed its gates, in any engine, is 0.081 of 255. The oracle can see damage: a deliberately coarse Draco (5-bit positions) moves the picture 40 to 75 times more than ordinary Draco in all three engines (`render/README.md`). The traps are the point of the second finding: on the PRISMATICA cathedral `stock-instance` erases 1216 of 1251 identity tokens and the picture moves by at most 0.000 mean delta in any of the three engines, the same as a lossless file. The one cell that did not load is `static-joined` on the cathedral in X_ITE (timeout after 25 s; the other two engines loaded it, and the identity gate fails it for 1,208 lost tokens). A render check cannot see the loss of a DEF name; the identity gate can. Neither replaces the other.

Instrument limits: square frames, one viewpoint, no animation, skins or morph targets exercised, software GL that exposes BC7, so KTX2 is transcoded to a GPU-compressed format; Babylon.js KTX2 is not run because its transcoders come from its CDN and the oracle is offline (the earlier run that reached the CDN decoded both ETC1S and UASTC with mean delta 0.004 and 0.002).


---

## 10. Plugging it in

| consumer | what the lane gives it | recommended profile | grade |
|---|---|---|---|
| blenderizer (`x3d-blender-io`) | a post-export optimise-and-verify step; the manifest records the profile and the gate summary beside the glb sha256 | `lossless` first (any consumer), `web` for browsers | [L]: design, not wired into the add-on in this change |
| x3d.loom three.js and Babylon.js bridges | the same glb, smaller, with the identity extras intact for the bridge to read | `web` (both read meshopt and quantization) | [C] for decode, section 8 |
| X_ITE glb import | a glb the X_ITE reader can read | see section 8: pick the profile whose extensions X_ITE decodes | [C] |
| Castle exporter | verification of its glb (the 2.19e-9 matrix finding came from it) | `lossless` as the identity-preserving canonical form | [C] |
| Unreal glb import (x3d.lab) | fewer draw calls with the DEF names recoverable from the batch extras | see section 8 for which extensions the importer reads | [L] |

---

## 11. The browser forge and byte parity

`web/forge.mjs` bundles the same optimiser and the same four portable gates into one ES module (400.2 KiB minified, `esbuild 0.25.12`). Draco, KTX2 and the Khronos validator stay in Node. The demo page runs `forge()` in a Web Worker on the visitor's copy of a showpiece, shows the identity audit name by name, and compares the SHA-256 of the output with the receipt the Node CLI wrote. Parity is a test, not a claim: `tests/web.test.mjs` runs the bundle in `Chromium 153.0.8010.12` and compares bytes against Node for four profile and fixture pairs; all four are identical.

---

## 12. Run it

```bash
cd x3d.gltf && npm ci
node bin/x3dgltf.mjs profiles                                   # contracts
node bin/x3dgltf.mjs inspect model.glb                          # inventory, byte table, gzip/brotli
node bin/x3dgltf.mjs validate model.glb                         # validator on the file and its decoded form
node bin/x3dgltf.mjs optimize model.glb out.glb --profile web --receipt out.json
node bin/x3dgltf.mjs verify  model.glb out.glb --profile web    # exit 0 only if every gate passes
node bin/x3dgltf.mjs matrix --files a.glb,b.glb --profiles web,draco,instanced --out run --md run.md --expect-fail static-joined
node tools/step-probe.mjs run/steps.json run/steps.md model.glb # one stock step at a time against the identity gate
```

---

## Heuristics

| ID | Rule (imperative, at most 30 words) | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-GTO-1 | Count identity tokens before and after every optimiser step; a size win with tokens lost is a loss, not a win. | [C] | stock `instance()` on the cathedral: 1,190.8 to 843.8 KiB, 1,216 of 1,251 tokens lost | `x3dgltf step-probe`, glTF-Transform 4.5.1 |
| H-GTO-2 | Do not run stock `instance()` or `join()` on a glb whose names matter; use `instanceWithIdentity` or skip the step. | [C] | `join()`: 1,208 tokens lost and 16,482.7 KiB; `instance()`: 1,216 lost | `x3dgltf step-probe`, glTF-Transform 4.5.1 |
| H-GTO-3 | Wrap `quantize()` when the glb has animation; stock leaves a channel without its target node. | [C] | animated fixture: 1 of 3 channels unmatched stock, 0 of 3 wrapped | `x3dgltf step-probe`, glTF-Transform 4.5.1 |
| H-GTO-4 | Dedup accessors and textures only, with `keepUniqueNames`; leave name-only duplicate meshes and materials standing, because a name is an identity. | [C] | `identity-dup` fixture: stock `dedup()` loses 2 tokens, the lane's loses 0 | `x3dgltf step-probe`, glTF-Transform 4.5.1 |
| H-GTO-5 | Validate the decoded canonical file as well as the delivered one, and print `extensionsNotValidated` beside every pass. | [C] | validator names `EXT_meshopt_compression` as not validated on the `web` cathedral | `Khronos glTF-Validator 2.0.0-dev.3.10` |
| H-GTO-6 | Read triangle counts from the inventory (per drawn instance), never from the validator's total (per unique mesh). | [C] | cathedral: validator 27,544, inventory 600,976 | `Khronos glTF-Validator 2.0.0-dev.3.10`, `x3dgltf inspect` |
| H-GTO-7 | Write the geometry bound into the profile contract, and make `exact` one float32 ULP, not zero; a stored `matrix` moves a glb by 2.19e-9. | [C] | Castle `annotation-standard` glb under `lossless` | `x3dgltf verify`, glTF-Transform 4.5.1 |
| H-GTO-8 | Match triangles by centroid through a k-d tree; a grid matcher does not finish on a 600,976-triangle scene. | [C] | grid did not finish in 250 s; tree self-compare 2.0 s | `x3d.gltf/src/geometry.mjs`, Node v22.23.4 |
| H-GTO-9 | Count zero-area triangles apart; Draco drops them and a bit-bounded profile must not fail for a triangle that never had an area. | [C] | see receipts/matrix/cells for the notes of each draco cell | `x3dgltf matrix` |
| H-GTO-10 | Compare profiles on gzip and brotli as well as raw bytes; the raw ranking is not the wire ranking. | [C] | the smallest passing profile by raw bytes differs from the smallest by brotli on 6 of 12 files (asterion: web-filter raw, draco brotli; lumen: draco raw, web-filter brotli; prismatica-aurora-cathedral: instanced raw, draco brotli) | `x3dgltf matrix`, Node `zlib` |
| H-GTO-11 | Judge KTX2 by `gpuTextureBytes` and by wire bytes separately; UASTC can cost transfer and save memory. | [C] | still life: `web-ktx2` is 1,246.2 KiB against 1,072.7 KiB for `web`, with texture memory 1,365.4 KiB against 5,461.3 KiB | `x3dgltf matrix`, `ktx2-encoder 0.6.0` |
| H-GTO-12 | Read the consumer's decoder row before choosing a compression; "the engine loads glTF" does not mean it loads meshopt or Draco. | [L] | Castle 7.0-alpha.3 and Unreal Interchange 5.5 to 5.8 read neither meshopt nor KTX2 (section 8) | package source, section 8 |
| H-GTO-13 | Prove a browser path equals the CLI path with a SHA-256 of the output, not with a screenshot. | [C] | 4 of 4 parity tests identical in `Chromium 153.0.8010.12` | `tests/web.test.mjs` |
| H-GTO-14 | Print a lossy profile's pass with what the pass means: bounds held, identity not. A bare PASS on `stock-instance` reads as success. | [C] | `stock-instance` on the cathedral: PASS with 1,216 tokens lost | `x3dgltf verify` |

---

## Drills

### D-GTO-1 Count the contracts
- **Level:** L1
- **Task:** list the profiles and count how many promise `exact`, `mapped` and `lossy` identity.
- **Verify:** `node bin/x3dgltf.mjs profiles | grep -c "identity exact"` and the same with `mapped` and `lossy`, from `x3d.gltf/`.
- **Answer:** 8 exact, 1 mapped (`instanced`), 2 lossy (`static-joined`, `stock-instance`).
- **Checked:** 2026-11-15 `x3dgltf` at x3d.loom@b6a3650, Node v22.23.4

### D-GTO-2 Spring the trap, then step around it
- **Level:** L2
- **Task:** optimise the PRISMATICA cathedral glb with `stock-instance` and with `instanced`. Compare draw calls, size and tokens lost.
- **Verify:** `node bin/x3dgltf.mjs optimize prismatica-aurora-cathedral.glb out.glb --profile stock-instance`, then `--profile instanced`. The glb is `docs/brag/showpieces/prismatica/prismatica-aurora-cathedral.glb` in x3d-blender-io@54aba0c.
- **Answer:** both take 1,218 draw calls to 10. `stock-instance`: 858.3 KiB, identity kept 35 of 1,251, lost 1,216, and a PASS line followed by a NOTE that the pass is not about identity. `instanced`: 445.4 KiB, kept 1,251 of 1,251, lost 0.
- **Checked:** 2026-11-15 `x3dgltf`, glTF-Transform 4.5.1, Node v22.23.4

### D-GTO-3 The validator that cannot see the geometry
- **Level:** L2
- **Task:** optimise the cathedral with `web`, validate the result, and say which extension the validator does not check and what the lane does about it.
- **Verify:** `node bin/x3dgltf.mjs optimize prismatica-aurora-cathedral.glb web.glb --profile web --no-verify && node bin/x3dgltf.mjs validate web.glb`.
- **Answer:** delivered 0 errors, 0 warnings; the line "NOT VALIDATED by gltf-validator 2.0.0-dev.3.10: EXT_meshopt_compression"; a second line for the canonical file (meshopt disposed, decoded), 0 errors, 0 warnings. Triangles reported are 27,544, not 600,976 (H-GTO-6).
- **Checked:** 2026-11-15 `Khronos glTF-Validator 2.0.0-dev.3.10`, Node v22.23.4

### D-GTO-4 A gate that can fail
- **Level:** L3
- **Task:** run the four negative controls and read what each one breaks. Then write a fifth: change one scale in a `lossless` output by 0.1% and show the geometry gate fails while the float32 noise of a stored matrix does not.
- **Verify:** `node --test --test-name-pattern "negative control" tests/lane.test.mjs`; for the fifth, `tests/lane.test.mjs` has `matrix nodes: float32 noise in a stored matrix passes an exact profile, a real 0.1% scale change still fails the gate`.
- **Answer:** four of four negative controls pass (geometry moved 2%, a DEF stripped, a base colour changed, a keyframe shifted); the fifth passes too: the 1.00000004 matrix passes `lossless`, a 1.001 scale fails `geometry`.
- **Checked:** 2026-11-15 `node --test`, Node v22.23.4

### D-GTO-5 Which stock step takes the animation channel
- **Level:** L3
- **Task:** run the step probe on the animated fixture and find the two stock steps that leave a channel unmatched, then the wrapper that fixes one of them.
- **Verify:** `node tools/step-probe.mjs run/steps.json run/steps.md animated.glb` (the fixture is built by `fixtures/build.mjs`); read the "animation channels unmatched" column.
- **Answer:** stock `quantize()` and stock `meshopt()` each leave 1 of 3 channels unmatched; `quantize wrapper` leaves 0 of 3. `meshopt()` quantizes internally, which is why it behaves like `quantize()`.
- **Checked:** 2026-11-15 `x3dgltf step-probe`, glTF-Transform 4.5.1

### D-GTO-6 Rank the wire
- **Level:** L2
- **Task:** from `receipts/summary.md`, find the profile that wins on raw bytes and the profile that wins on brotli for the thalassa exhibition and for the PRISMATICA cathedral glb.
- **Verify:** `node tools/summarize.mjs receipts/matrix/matrix.json receipts/matrix/matrix-traps.json` and read the per-file table.
- **Answer:** thalassa-exhibition: raw instanced (175.2 KiB), brotli instanced (37.4 KiB); prismatica-aurora-cathedral: raw instanced (445.4 KiB), brotli draco (125.3 KiB).
- **Checked:** 2026-11-15 `x3dgltf matrix`, Node `zlib` gzip 9 and brotli 11

---

## Honest limits

- **[C]** Nothing was timed. Sizes, counts and tokens are measured; load time, decode time and frame time are not, on any GPU or on the software adapter.
- **[C]** The corpus is 12 glbs from this project. A different scene can rank the profiles differently; every ranking in section 7 is about these files.
- **[C]** The validator, Draco and KTX2 run in Node only. The browser bundle claims the four portable gates and the meshopt profiles, nothing else.
- **[C]** The gates compare a source and an output of the lane. They do not prove either file is a faithful rendering of the original X3D; that is the render oracle (section 9) and chapter 06.
- **[C]** The `x3d_def_path` gate compares claim counts and how many hold; it does not re-derive whether the add-on's path is the right path for the node. On `stilllife` 9 claims are made and none hold in the source, so the gate can only promise "no worse than the source" there.
- **[C]** The `static-joined` normals check samples about 400 triangles; one corpus file animates (the animated cathedral: 1 animation, 1 channel), so the multi-channel animation gate is exercised by fixtures only.
- **[L]** The Unreal and Castle rows of the support matrix were read from API headers, documentation and source, not run: there was no Unreal Editor and no Castle binary in the session.
- **[L]** Babylon.js fetches its Draco and basis transcoders from its CDN at run time; those decoder versions are the CDN's, not the npm package's.
- **[S]** A `web-lean` profile that prunes attributes no material uses would be about 300 KiB smaller on the cathedral (stock `prune()` removes 299.2 KiB and loses 0 tokens). It is not offered because the normals gate treats a dropped normal as a loss. Not built, not measured end to end.
- **[S]** The Blender add-on is not changed by this lane. A post-export optimise step is a design, not wired code.

---

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-GTO-1 | PRISMATICA cathedral draw calls, source to `instanced` | 1,218 to 10 | [C] | `x3dgltf optimize`, glTF-Transform 4.5.1 | x3d.loom@b6a3650:x3d.gltf/receipts/matrix/ |
| N-GTO-2 | cathedral identity tokens | 1,251 | [C] | `x3dgltf verify` | x3d.loom@b6a3650:x3d.gltf/receipts/matrix/ |
| N-GTO-3 | tokens lost by stock `instance()` on the cathedral | 1,216 of 1,251 | [C] | `x3dgltf step-probe` | x3d.loom@b6a3650:x3d.gltf/receipts/step-probe.md |
| N-GTO-4 | tokens lost by `join()` on the cathedral, and its size | 1,208; 1,190.8 to 16,482.7 KiB | [C] | `x3dgltf step-probe` | x3d.loom@b6a3650:x3d.gltf/receipts/step-probe.md |
| N-GTO-5 | cathedral under `web` and under `instanced` | 638.0 KiB (53.6%); 445.4 KiB (37.4%) | [C] | `x3dgltf optimize` | x3d.loom@b6a3650:x3d.gltf/receipts/matrix/ |
| N-GTO-6 | validator triangle total vs inventory, cathedral | 27,544 vs 600,976 | [C] | `Khronos glTF-Validator 2.0.0-dev.3.10` | x3d.loom@b6a3650:x3d.gltf/src/measure.mjs |
| N-GTO-7 | Castle `annotation-standard` deviation under `lossless` | 2.19e-9 of the diagonal | [C] | `x3dgltf verify` | x3d.loom@b6a3650:x3d.gltf/tests/lane.test.mjs |
| N-GTO-8 | `exact` geometry bound | 1e-7 of the diagonal (float32 ULP 1.19e-7) | [C] | `x3d.gltf/src/profile-contract.mjs` | x3d.loom@b6a3650:x3d.gltf/src/profile-contract.mjs |
| N-GTO-9 | stock `quantize()` channels unmatched, animated fixture | 1 of 3 | [C] | `x3dgltf step-probe` | x3d.loom@b6a3650:x3d.gltf/receipts/step-probe.md |
| N-GTO-10 | `weld()` growth on the cathedral | 1,190.8 to 1,204.4 KiB | [C] | `x3dgltf step-probe` | x3d.loom@b6a3650:x3d.gltf/receipts/step-probe.md |
| N-GTO-11 | stock `prune()` on the cathedral | 1,190.8 to 891.6 KiB, 0 tokens lost | [C] | `x3dgltf step-probe` | x3d.loom@b6a3650:x3d.gltf/receipts/step-probe.md |
| N-GTO-12 | browser bundle size | 400.2 KiB minified | [C] | `esbuild 0.25.12` | x3d.loom@b6a3650:x3d.gltf/web/forge.mjs |
| N-GTO-13 | k-d tree self-compare of the cathedral | 2.0 s (grid: not finished in 250 s) | [C] | Node v22.23.4 | x3d.loom@b6a3650:x3d.gltf/src/geometry.mjs |
| N-GTO-14 | lane tests | 13 lane + 4 browser parity, all passing | [C] | `node --test`, Node v22.23.4 | x3d.loom@b6a3650:x3d.gltf/tests/ |
| N-GTO-15 | corpus totals under `web`: raw, gzip, brotli | 35.8%, 50.2%, 60.6% | [C] | `x3dgltf matrix`, Node `zlib` | x3d.loom@b6a3650:x3d.gltf/receipts/summary.md |
| N-GTO-16 | corpus totals under `instanced`: raw, gzip, brotli | 32.1%, 49.2%, 58.8% | [C] | `x3dgltf matrix`, Node `zlib` | x3d.loom@b6a3650:x3d.gltf/receipts/summary.md |
| N-GTO-17 | corpus totals under `draco`: raw, gzip, brotli | 44.8%, 57.5%, 69.7% | [C] | `x3dgltf matrix`, `draco3dgltf 1.5.9` | x3d.loom@b6a3650:x3d.gltf/receipts/summary.md |
| N-GTO-18 | corpus totals under `lossless`: raw | 103.0% | [C] | `x3dgltf matrix` | x3d.loom@b6a3650:x3d.gltf/receipts/summary.md |
| N-GTO-19 | identity tokens lost by a shipping profile, whole corpus | 0 over 108 cells | [C] | `x3dgltf verify` | x3d.loom@b6a3650:x3d.gltf/receipts/matrix/matrix.json |
| N-GTO-20 | tokens lost by the two traps, whole corpus | 10,095 over 24 cells | [C] | `x3dgltf verify` | x3d.loom@b6a3650:x3d.gltf/receipts/matrix/matrix.json |
| N-GTO-21 | thalassa `static-joined` | 480.3 to 3,204.0 KiB, geometry gate FAIL | [C] | `x3dgltf verify` | x3d.loom@b6a3650:x3d.gltf/receipts/matrix/cells/thalassa-exhibition.static-joined.json |
| N-GTO-22 | asterion `lossless` | 4,404.4 to 4,851.9 KiB (110.2%) | [C] | `x3dgltf optimize` | x3d.loom@b6a3650:x3d.gltf/receipts/matrix/cells/asterion.lossless.json |
| N-GTO-23 | still life `web-ktx2-etc1s` | 1,645.4 to 509.1 KiB (30.9%) | [C] | `ktx2-encoder 0.6.0` | x3d.loom@b6a3650:x3d.gltf/receipts/matrix/cells/stilllife-addon.web-ktx2-etc1s.json |
| N-GTO-24 | matrix cells run | 132 (108 shipping, 24 trap) | [C] | `x3dgltf matrix` | x3d.loom@b6a3650:x3d.gltf/receipts/matrix/matrix.json |

---

## Sources and provenance

| source | state read | what for |
|---|---|---|
| x3d.loom@b6a3650 `x3d.gltf/` | read and run, 2026-11-15 | every number in sections 2 to 7 and 11 |
| x3d-blender-io@54aba0c `docs/brag/showpieces/` | read and run | the four showpiece glbs and `stars-view` |
| x3d.castle@0a1073f `results/exporter-70/sample-glb/` | read and run | two exporter glbs, one with stored matrices |
| `three@0.187.0`, `babylonjs@9.32.0`, `babylonjs-loaders@9.32.0`, `x_ite@16.7.1` npm packages | source read in `node_modules` | section 8 |
| Epic Interchange API headers and documentation, glTFRuntime, Blender `io_scene_gltf2`, Castle Game Engine source | read, not run | section 8, grades [L] and [C]-read |
| glTF-Transform 4.5.1, meshoptimizer 1.3.0, draco3dgltf 1.5.9, ktx2-encoder 0.6.0, gltf-validator 2.0.0-dev.3.10 | npm, run in Node v22.23.4 | all runs |

Private-source gaps: the Unreal Engine source is not public to this session, so no Interchange row is graded from source. Unpublished material of any project is not used.
