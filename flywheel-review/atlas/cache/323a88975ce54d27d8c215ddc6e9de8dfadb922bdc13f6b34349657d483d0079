# 11. glTF, USD and Khronos: what survives and what the gate proves

> **Say it:** an X3D scene that goes through Blender to a glb keeps its geometry, materials, lights, cameras and fixed animation, loses its behaviour (ROUTEs, Scripts, PROTOs, sensors) and its authoring identity unless you pay to carry it, and the Khronos validator proves only that the glb is well-formed, never that the scene is in it. **[C]** for the validator behaviour re-run below, **[L]** for what each carrier keeps.

| field | value |
|---|---|
| chapter code | `GLT` |
| prerequisites | [01 The tether](01-the-tether.md) for the loop; [03 The validator and the gates](03-validator-and-gates.md) for what a validator can and cannot see |
| after this you can | (1) say per X3D feature whether it survives a glb or USD hop, and how that was graded; (2) run the Khronos glTF Validator gate on any glb and read its result honestly; (3) build a glb that passes the gate and is empty, and say why that is not a bug in the gate; (4) name the five export gotchas that bit this pipeline and the fix for each; (5) run the 10-step checklist for a trustworthy X3D to glb run |
| sources read | x3d-blender-io@ab99988:{tools/fidelity_rig/validate_glb.mjs, manifest.py, blender_leg.py, package.json, README.md, release_notes.md, tests/test_glb_validator_bpy.py, source/import_x3d.py}; glTF extension registry (public, fetched 2026-11-14, sha256 prefix `32868b162d85`); x3d.docs@f172f67:docs/x3d-blender-io/MASTERCLASS.md |
| instruments used | `Khronos glTF-Validator 2.0.0-dev.3.10` (npm, run 2026-11-14); `bpy 5.3.0` (read from repo receipts, not run: no `bpy` here); `X_ITE 16.7.1` and `Babylon.js 9.32.0` on `Chromium 153, SwiftShader` (receipts carried from the repo README); `x3d-blender-io@ab99988` |

Grading note for this chapter. Blender was **not** installed in the session that wrote it, so no export in this chapter was produced here. What was run on 2026-11-14: the glTF Validator on five existing glbs and two hand-built glbs, the glb JSON chunk parsed with Python, and the Khronos extension registry fetched and counted. Every Blender-side number is therefore a repo receipt (`read, not run`) and is graded [L] unless a re-run is named.

---

## 1. The map

```text
  X3D 4.0 file (the tether's source of truth; ROUTEs, Script, PROTO, sensors live ONLY here)
        |
        |  import_scene.x3d   (x3d-blender-io: ONE translation, at import, no event runtime)
        v
  Blender scene  Z-up, metres, Principled BSDF, lights in W / lux, actions, shape keys
        |   custom props x3d_def, x3d_def_path, x3d_use   (identity; survives only via extras)
        |
        +--> export_scene.gltf  (GLB, export_extras=True, COMPAT light units, export_apply=True)
        |        |
        |        v
        |    raw glb  --[ validate_glb.mjs: Khronos glTF Validator ]--> FILE.glb.validation.json
        |        |         exit 0 clean / 1 errors / 2 validator missing        (structure only)
        |        v
        |    manifest.json  (x3d sha256, add-on revision, Blender version, glb sha256, counts)
        |        |
        |        +--> Babylon.js 9.32.0  vs  X_ITE 16.7.1 on the X3D   (looks: mean abs delta)
        |
        +--> USD export (Blender's own exporter; NOT in the rig, NOT run here)
```

| in scope | out of scope |
|---|---|
| what survives X3D to glb to engines; the validator gate; the export gotchas | the X3D to Blender importer internals (see the [AST teardown](../x3d-blender-io/MASTERCLASS.md)); Unreal import ([12](12-unreal-tier1.md)); physics ([13](13-physics.md)) |

Read next: deeper, [03 The validator and the gates](03-validator-and-gates.md) for the X3D-side gates this chapter mirrors; wider, [12 Unreal as a tier-1 X3D framework](12-unreal-tier1.md) for a glb consumer that has never been run.

The thesis in one line: the **source** stays X3D and the glb is a build output with a receipt. A glb that "looks fine" is not accountable; a glb with a sha256, an add-on revision, a validator report and a named list of what was dropped is.

---

## 2. Carriers: what survives an X3D to glb or USD hop

Reading of this table: "kept" means a value reaches the file and an engine can draw it; "dropped" means no equivalent exists in the carrier; "baked" means the behaviour is sampled into data. Evidence is `read` (code or release note, not run here), `run` (re-run 2026-11-14), or `lead` (private note, not re-checked).

| X3D feature | glb (glTF 2.0) | USD | Evidence | Grade |
|---|---|---|---|---|
| Transform, Group, Shape, DEF/USE meshes | kept; USE becomes a shared mesh, flat import drops DEF'd Transforms into object names plus `x3d_def_path` extras | kept as Xform and Mesh; references and payloads have no glTF form | `release_notes.md` identity entry, read | [L] |
| IndexedFaceSet, primitives, TriangleSets | kept as meshes (a Box imports as a mesh; the 4.0 export writes primitives back) | kept as Mesh | `release_notes.md`, read | [L] |
| PhysicalMaterial, Material, UnlitMaterial | PBR metal-rough, classic Material approximated, unlit becomes `KHR_materials_unlit` | UsdPreviewSurface (not examined) | release notes lines on UnlitMaterial and colour space, read | [L] |
| Colour space | classic colours are sRGB in X_ITE, linear in glTF: converted at import under option `SRGB` | not examined | README measurement: `emissiveColor 0.5` draws 128 in X_ITE, 186 from an as-is glb, 127 from a converted one (X_ITE 16.7.1, Babylon.js 9.32.0, Chromium 153) | [L] |
| DirectionalLight, PointLight, SpotLight | `KHR_lights_punctual`; units fitted so Babylon draws what X_ITE draws (light units option) | UsdLux (not examined) | probes table in rig README, read | [L] |
| Viewpoint, OrthoViewpoint, GeoViewpoint | cameras; headlight is NOT a glTF object (rig adds it in Babylon) | cameras | rig README, read | [L] |
| TimeSensor + interpolators + ROUTE (fixed) | **baked** into an animation: Position/Orientation/Scale interpolators to node channels, CoordinateInterpolator to morph-target weights | baked to time samples if exported | `import_x3d.py` ROUTE handling (read); morph-weights channel re-parsed from a glb 2026-11-14 | [C] for the morph channel, [L] otherwise |
| ROUTE as a live event graph | **dropped** (a baked clip has no graph); `KHR_interactivity` is the only glTF-side place it could go | dropped | Section 3; no exporter writes it | [L] |
| Script (ECMAScript), sensors (Touch, Proximity, Visibility) | **dropped**: no glTF equivalent in 2.0 | dropped | nothing in the add-on reads or writes a Script; AST coverage table lists the touched components | [L] |
| PROTO / ExternProto | expanded or absent: the glb has no concept of a prototype | composition arcs differ in kind | read: `_NOT_SWITCH_CHILDREN` lists ProtoDeclare as a non-child | [L] |
| Inline | imported as an Empty carrying `x3d_inline_url`; the content is imported if the URL resolves; an unresolved Inline gives an empty glb | `references` are not used | `import_x3d.py:6518-6580`, read; 5 of 33 repo glbs empty | [L] |
| Switch, LOD | Switch: the chosen child only; LOD: no glTF counterpart (a vendor extension `MSFT_lod` exists) | variants / purpose differ | registry lists `MSFT_lod` as a vendor extension (fetched); Switch handling read | [L] |
| NURBS (13 nodes) | no node is read by the add-on per the AST coverage table; tessellate before import | NURBS curves exist in USD, not examined | MASTERCLASS section 2.1 coverage, measured 2026-11-13 | [L] |
| ParticleSystems (10 nodes) | no node read; no glTF particle feature | no | MASTERCLASS section 2.1 | [L] |
| ComposedShader / ProgramShader (GLSL) | **dropped**: glTF has no shader slot; a GLSL scene must be baked to textures or re-authored as PBR | MaterialX or OSL, different language | `SHADER_SPECS` read in importer (translation spec in repo, not run here) | [L] |
| Sound, AudioClip | not in glTF 2.0 core; `KHR_audio_graph` is a *Proposal* in the registry | `UsdMedia` audio, not examined | registry fetched 2026-11-14 | [L] |
| RigidBodyPhysics | `KHR_physics_rigid_bodies` is a *Review Draft* in the registry; the add-on touches no RigidBodyPhysics node | `UsdPhysics` | registry; MASTERCLASS component list | [L] |
| HAnim | armature and skin (joints, weights) | UsdSkel | add-on README: armatures export as HAnim; glb side not re-run | [L] |
| GeoElevationGrid | a mesh (703 vertices, 1,296 triangles in the Showcase globe; 0 errors, 0 warnings) | not examined | release notes, read | [L] |
| Gaussian splats | `KHR_gaussian_splatting` (ratified per the registry); add-on reads splat PointClouds | not examined | registry; `source/splat_native.py` header | [L] |

The loss list is the useful part. Everything labelled **dropped** is behaviour, and behaviour is exactly the part the thesis of this knowledge base says must stay accountable in the X3D file. So: a glb is a *delivery copy of the static scene plus fixed clips*. Treat a missing behaviour as an expected loss, say so in the manifest, and never infer "the X3D scene works" from "the glb loads".

```text
  What a glb can and cannot carry from an X3D scene (read from repo, grade [L])

  STATIC            geometry  materials  textures  lights  cameras  hierarchy     --> kept
  SAMPLED           interpolator clips, CoordinateInterpolator morphs             --> baked
  IDENTITY          DEF names, USE links, Inline URLs                             --> only in extras
  ------------------------------------------------------------------------------------------
  BEHAVIOUR         ROUTE graph  Script  sensors  PROTO  Switch-at-runtime       --> dropped
  SPECIAL           NURBS  ParticleSystems  GLSL shaders  Sound  Physics         --> dropped (today)
```

### 2.1 A worked loss: what the Prismatica animated glb kept of two ROUTEs

The animated conversion of one of the Unreal-project scenes has exactly two ROUTEs (a TimeSensor to a CoordinateInterpolator, then the interpolator to a Coordinate's `set_point`), counted with `grep -c '<ROUTE'` on the converter output on 2026-11-14. The glb the add-on produced from it (`bpy 5.3.0`, Blender glTF I/O 5.3.43, carried file) was parsed with Python's `json` on 2026-11-14:

| quantity | value |
|---|---|
| glTF animations | 1, named `RibbonMeshAction` |
| channels | 1, target path `weights` |
| the ribbon mesh primitive has `targets` | true (it has morph targets) |
| ROUTE elements in the glb | 0 (the format has none) |

So the *effect* of the ROUTE pair (a displaced surface cycling through key frames) survives as a morph clip, and the *wiring* does not. A reader who edits the glb cannot re-route the clock. That is the whole story of the carrier in one example.

---

## 3. The KHR extension map and its status

Status is date-sensitive. The map below is read from the public Khronos extension registry page (`KhronosGroup/glTF`, `extensions/README.md`, fetched 2026-11-14, sha256 prefix `32868b162d85`). A registry file does not carry ratification dates, so any date is [S] unless the extension's own spec says it.

| section of the registry | count (2026-11-14) | what it means |
|---|---|---|
| Ratified Khronos Extensions | 27 (24 `KHR_*`, 3 `EXT_*`) | covered by the Khronos IP framework |
| In-progress (Proposal / Initial / Review Draft / Release Candidate) | 9 extensions + 1 project | not safe to require in a delivered glb |
| Archived | 3 | do not write |

The ratified rows relevant to an X3D pipeline, with the X3D concept they carry:

| extension | status 2026-11-14 | X3D concept | does our pipeline write it? |
|---|---|---|---|
| `KHR_lights_punctual` | Ratified | DirectionalLight, PointLight, SpotLight | yes: `required` in the Prismatica glbs (re-parsed) |
| `KHR_materials_unlit` | Ratified | UnlitMaterial, lines, points | yes (re-parsed) |
| `KHR_materials_emissive_strength` | Ratified | HDR emissive | not seen in the glbs read |
| `KHR_materials_transmission`, `_volume`, `_ior` | Ratified | PhysicalMaterial transmission | not examined |
| `KHR_materials_specular`, `_clearcoat`, `_sheen`, `_anisotropy`, `_iridescence`, `_dispersion` | Ratified | X3D 4.1 MaterialExtension nodes (no 1:1 map measured) | `_specular` appears in an older unlit path per release notes; others not examined |
| `KHR_materials_variants` | Ratified | no X3D node; Switch only loosely | no |
| `KHR_texture_transform` | Ratified | TextureTransform | not examined |
| `KHR_texture_basisu` | Ratified | compressed textures (KTX2) | no |
| `KHR_mesh_quantization` | Ratified | none (storage) | no |
| `KHR_draco_mesh_compression` | Ratified | none (storage) | no |
| `KHR_node_visibility`, `_selectability`, `_hoverability` | Ratified | Switch/visible, pickability | no |
| `KHR_animation_pointer` | Ratified | animation of any property: the glTF analogue of a ROUTE to a field | no |
| `KHR_interactivity` | Ratified | the glTF-side behaviour graph: the one place ROUTE-like logic could live | no |
| `KHR_gaussian_splatting` | Ratified | `GaussianSplats` (X3D 4.1 draft) | splat importer reads it |
| `EXT_mesh_gpu_instancing` | Ratified (EXT) | DEF/USE reuse at scale | yes, behind an option (Section 5.4) |
| `EXT_meshopt_compression`, `EXT_texture_webp` | Ratified (EXT) | none (storage) | no |
| `KHR_materials_diffuse_transmission` | Release Candidate | none | no |
| `KHR_physics_rigid_bodies`, `KHR_collision_shapes` | Review Draft | RigidBodyPhysics, CollisionCollection | no (see [13](13-physics.md)) |
| `KHR_audio_graph` | Proposal | Sound | no |
| `KHR_materials_pbrSpecularGlossiness` | Archived | none: do not write | no |

Two cautions, both from re-running the validator.

1. **Ratified does not mean validated.** `EXT_mesh_gpu_instancing` is in the ratified list, yet `Khronos glTF-Validator 2.0.0-dev.3.10` does not know it: a glb that uses it passes at INFO with "cannot validate an extension as it is not supported" (run 2026-11-14 on two glbs, Section 5.3). The gate's `extensionsNotValidated` field exists to say so.
2. **Ratified does not mean drawn.** Which engine draws which extension is a separate measurement. Castle, X_ITE, Babylon.js and Unreal each have their own list, and the registry says nothing about them.

The date claims that circulate (when `KHR_interactivity`, `KHR_gaussian_splatting` and glTF 2.1 reached which stage) came from private digests and a third-party tracker. They are [S] here: "carried, not re-checked". What is [C] is the registry page itself on the day it was fetched.

---

## 4. The pipeline X3D -> Blender -> glb / USD

### 4.1 The one export call

`tools/fidelity_rig/blender_leg.py` is the single place the glb is made for the rig. It is short enough to quote (x3d-blender-io@ab99988, lines 19 to 31; read, and its output measured by the rig):

```python
bpy.context.scene.frame_start = 0   # X3D time 0 lands on frame_start; glTF writes frame/fps
assert bpy.ops.import_scene.x3d(filepath=x3d) == {"FINISHED"}
assert bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_lights=True,
    export_cameras=True, export_import_convert_lighting_mode="COMPAT", use_renderable=True,
    export_yup=True, export_extras=True, export_apply=True, use_mesh_edges=True,
    use_mesh_vertices=True, export_gpu_instances=<env BLENDER_X3D_GPU_INSTANCES>) == {"FINISHED"}
```

| option | why it is set | consequence if wrong |
|---|---|---|
| `frame_start = 0` before import | the importer puts X3D time 0 on `frame_start` | every clip starts 1/24 s late at the factory frame 1 (Section 6) |
| `export_extras=True` | carries `x3d_def`, `x3d_def_path`, `x3d_use` into node, mesh, material `extras` | the glb has no link back to the DEF names |
| `export_apply=True` | modifiers applied; checked harmless for the add-on's morphs | none measured on 34 of 34 scenes (Section 6) |
| `use_renderable=True` | only renderable objects | hidden helper objects leak into the glb otherwise |
| `export_import_convert_lighting_mode="COMPAT"` | W to candela conversion consistent with the light-units fit | a lights fit that no longer matches X_ITE |
| `use_mesh_edges`, `use_mesh_vertices` | lines and points export as primitives | `IndexedLineSet` and `PointSet` vanish |
| `export_gpu_instances` | writes `EXT_mesh_gpu_instancing` for same-mesh children of one Empty | 1,721 nodes instead of 10 (Section 5.4) |

### 4.2 Coordinates, in one line

X3D is right-handed Y-up, metres. Blender is right-handed Z-up. glTF is right-handed Y-up, metres. The add-on does the single Y-up to Z-up conversion at import and Blender's exporter undoes it with `export_yup=True`. The rule that keeps this accountable: convert **once**, never add a second rotation after the exporter has converted. The handedness-changing case (Unreal) is derived in [chapter 12](12-unreal-tier1.md).

### 4.3 The manifest: what travels beside the glb

`tools/fidelity_rig/manifest.py` writes `out/LABEL/<scene>/manifest.json`, schema `x3d-blender-io.glb-manifest/v1`, with no timestamps so the same inputs give the same manifest:

| field | what it records |
|---|---|
| x3d path and sha256 | which source |
| add-on git revision, Blender version | which compiler |
| `BLENDER_X3D_*` options, `X3D_SPLAT_IMPORT` | which settings |
| glb sha256 and bytes | which output |
| validator summary, `extensionsUsed`, `extensionsRequired`, counts | what the gate saw |

This is the "receipt" of the tether applied to a glb: given the manifest, a stranger can re-run the leg and compare a sha256. The repo records that two separate imports of one file give byte-identical glbs, with or without extras (Blender 5.3.0, read).

### 4.4 USD

The add-on has no USD writer of its own and the rig has no USD leg. The only USD route that exists here is Blender's own exporter after the import, which was **not run** in this session or recorded in the repo as a measured leg. Everything in Section 7 is therefore [L] or [S].

---

## 5. The Khronos validator gate

### 5.1 What `validate_glb.mjs` is

`tools/fidelity_rig/validate_glb.mjs` wraps the `gltf-validator` npm package (pinned `2.0.0-dev.3.10` in `package.json`). Contract, read from the file:

| item | behaviour |
|---|---|
| usage | `node validate_glb.mjs FILE.glb [--max-warnings N] [--out REPORT.json] [--quiet]`; `--version` prints the validator version |
| output | `FILE.glb.validation.json`: schema `x3d-blender-io.glb-validation/v1`, bytes, sha256, counts of errors / warnings / infos / hints, every issue with code, severity, pointer, message |
| derived | triangle, vertex, draw-call, material counts; `extensionsUsed`, `extensionsRequired`, `extensionsNotValidated` |
| exit codes | 0 clean, 1 errors (or more than N warnings, or the file would not parse), 2 usage error or validator package missing |
| installation | `npm install` in the rig folder, or `GLTF_VALIDATOR_DIR` points at another install (CI sets it) |
| CI | `tests/test_glb_validator_bpy.py` runs the gate without a browser; `GLTF_VALIDATOR_REQUIRED=1` turns a missing validator into a failure instead of silent skips |

### 5.2 What it proves, and what it does not

| the gate proves | the gate does not prove |
|---|---|
| container and chunk layout are well formed | that any geometry is present |
| JSON matches the glTF 2.0 schema | that the scene is the X3D scene (an unsupported node imports to nothing) |
| accessor and buffer-view bounds, index ranges, references resolve | that materials look right (colour space, light units are looks) |
| material and animation rules (for example a weights channel must have morph targets) | that an engine draws it |
| extensions it knows are used legally | extensions it does not know: reported at INFO only, content unchecked |

The repo's own measurement of this limit (Blender 5.3.0, gltf-validator 2.0.0-dev.3.10, carried from `release_notes.md` and the README, read): of the repo's 34 scenes, 33 export a glb, all 33 with 0 errors and 0 warnings; **5 of the 33 are empty** (unsupported node, or an Inline glb that imports to nothing) and 2 hold only points. All pass the gate. A passing gate on those is correct and useless, which is the point of this section.

### 5.3 Re-run: a valid glb with nothing in it

The gate was installed from npm into a scratch folder and run on 2026-11-14 (`Khronos glTF-Validator 2.0.0-dev.3.10`, node 22). Two hand-built glbs (the first is 48 bytes), built with this snippet (copy it as is):

```python
import struct
def glb(json_bytes, path):
    j = json_bytes + b' ' * ((4 - len(json_bytes) % 4) % 4)
    open(path, 'wb').write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(j))
                           + struct.pack('<II', len(j), 0x4E4F534A) + j)
glb(b'{"asset":{"version":"2.0"}}', 'empty.glb')
glb(b'{"asset":{"version":"2.0"},"extensionsUsed":["VENDOR_made_up"],'
    b'"extensionsRequired":["VENDOR_made_up"]}', 'reqext.glb')
```

```bash
node validate_glb.mjs empty.glb      # exit 0
node validate_glb.mjs reqext.glb     # exit 0, plus a NOT VALIDATED line
```

| file | result (run 2026-11-14) |
|---|---|
| `empty.glb` (48 B) | `OK`: 0 errors, 0 warnings, 0 infos; 0 tris, 0 draw calls, 0 materials; exit 0 |
| `reqext.glb` | `OK`: 0 errors, 0 warnings, 1 info; line `NOT VALIDATED: VENDOR_made_up (... REQUIRED by the file)`; exit 0 |

Both facts matter. An empty scene is a valid glb. A glb that *requires* an extension nobody can read is a valid glb. The wrapper's `NOT VALIDATED` line (and `extensionsNotValidated` in the JSON) exists because the validator itself reports only INFO; without the wrapper, an agent reading "0 errors" would conclude more than the tool says.

### 5.4 Re-run: the existing converter glbs

Five glbs already in the project, produced by the add-on from the two Unreal-project conversions (the instanced pair with `export_gpu_instances` on; carried files, re-validated 2026-11-14 with the same gate):

| glb | nodes | file bytes | errors / warnings | triangles | extensions used |
|---|---|---|---|---|---|
| exhibition, flat | 1,721 | 491,832 | 0 / 0 | 2,064 | none |
| exhibition, instanced | 10 | 125,224 | 0 / 0 | 2,064 | `EXT_mesh_gpu_instancing` (NOT VALIDATED) |
| cathedral static, flat | 1,224 | 1,097,864 | 0 / 0 | 27,544 | `KHR_materials_unlit`, `KHR_lights_punctual` |
| cathedral static, instanced | 16 | 864,228 | 0 / 0 | 27,544 | the two above plus `EXT_mesh_gpu_instancing` (NOT VALIDATED) |
| cathedral animated | 1,224 | 4,741,136 | 0 / 0 | 11,160 | the two KHR ones |

Reading the table: instancing keeps triangles and draw calls identical to the flat file while the node count falls from 1,721 to 10 and the size to a quarter; the validator reports the same 0 errors for both and cannot look inside the extension. The node, byte and triangle numbers match the public `release_notes.md` entry for the Group instances option (read), so that entry is now re-derived rather than carried. The animated file's validator triangle count (11,160) differs from the static one (27,544) because its ribbon mesh holds fewer indices (24,576 against 73,728, read from the accessors); the reason is a different tessellation setting in the conversion, which was not re-derived here.

`required` carries `KHR_lights_punctual` in the cathedral glbs. A viewer that ignores lights will refuse or degrade; this is the manifest's `extensionsRequired` doing its job.

---

## 6. Gotchas learned (each has a receipt)

| # | symptom | cause | right fix | wrong fix | evidence |
|---|---|---|---|---|---|
| 1 | every clip starts at 0.041667 s (1/24) | the importer puts X3D time 0 on `scene.frame_start`; the glTF exporter writes `frame / fps`; factory frame 1 | set `frame_start = 0` **before** import | `export_anim_slide_to_zero` | first sample 0.0 s, last 2.0 s for a 2 s cycle with the fix; README, Blender 5.3.0, read, [L] |
| 2 | "slide to zero" seems to work | the flag is **ignored** when `export_force_sampling` is off, and slides each action by its own first key, so a first key at 0.5 s moves to 0 | do not use it | using it as a default | error 0.5 s on a 0.5 s first key, README, read |
| 3 | final pose missing on a short loop | integer-frame sampling stops a frame early: a 0.7 s cycle ends at 0.6667 s; a key at 0.3 of a 2 s cycle falls at frame 14.4 and is dropped (0.125 units of position error) | keep cycles on whole frames, or use `export_force_sampling=False` for Transform animation; HAnim joints with it are untested | trusting the first sample only | README, read |
| 4 | worry that `export_apply=True` drops morphs | the exporter's help says it prevents shape keys | none needed: byte-identical glbs on 34 of 34 scenes and two CoordinateInterpolator scenes | removing the flag | README, Blender 5.3.0, read; the claim is true only for shape keys plus a non-armature modifier, which only the Solidify import option makes (then the glb fails with `ANIMATION_CHANNEL_TARGET_NODE_WEIGHTS_NO_MORPHS`) |
| 5 | the glb names the importing machine's folders | `x3d_inline_resolved_path` and `x3d_scene_source_path` were stored absolute | store relative to the importing file or as a file name (`mfstring.portable_path`) | scrubbing the glb afterwards | release notes line 5; `import_x3d.py:6553`, `populate.py:78`, read, [C] for the code line |
| 6 | scene with an Inline under scale `1.057e-16` imports then exports about 1e8 too small | Blender's exporter writes `parent.matrix_world.inverted_safe() @ child`; in float32 the 4x4 determinant of that scale underflows and `inverted_safe()` returns a scale near 1e8 | move any world scale outside [1e-6, 1e6] off an Empty that has children onto the children's parent inverse (`matrix_safety.push_scale_to_children`) | trusting the validator (it passed with 0 errors) | release notes line 7, Blender 5.3.0, read; same glb now validator 0 errors, drawn like X_ITE in Babylon.js 9.32.0 |
| 7 | 1,721 flat nodes where 10 would do | USE and Group make every instance a scene root; the exporter writes `EXT_mesh_gpu_instancing` only for children of one Empty that share a mesh | the **Group instances** import option (`BLENDER_X3D_GPU_INSTANCES=1`) | hand-editing the glb | Section 5.4, [C] for node counts |
| 8 | unlit shapes draw white in Babylon | `UnlitMaterial` once imported as Principled with black base colour and emissive colour; glTF multiplies `COLOR_0` into the black base only | import as an Emission shape that exports `KHR_materials_unlit` | none | release notes line 22, read |
| 9 | a `ColorRGBA` cloud layer is an opaque shell | the glb alphaMode was OPAQUE | alphaMode BLEND under AUTO, alpha in `COLOR_0` | none | release notes line 21, read |

Three rules fall out of this table. The validator never catches a timing, identity or scale fault (all of 1, 5, 6 passed with 0 errors). A flag whose help text sounds right can be wrong for your inputs (2, 4). And a fix has to be tested in the *glb*, not in Blender's viewport, because the defects live in the exporter's arithmetic.

---

## 7. USD mapping notes

None of the USD notes below was run in this base. They come from reading and from private digests, so they are [L] at best.

| topic | note | grade |
|---|---|---|
| role | USD is a composed master with layers, references and variants; glTF is a flat delivery copy. The digests agree that export is a publication step, not a round trip | [L] |
| composition | USD references, payloads, layers and overs have no glTF form; the X3D analogue is Inline and PROTO, which exist only at the X3D layer. A USD to glTF hop flattens, and so does glTF to USD | [L] |
| variants | `KHR_materials_variants` carries only the material part; X3D Switch and LOD have no glTF counterpart | [L] |
| lights | only punctual lights survive glTF; UsdLux has more light types (area, dome) than X3D or glTF can say | [L] |
| packaging | USDZ is an uncompressed, aligned archive made by UsdUtils; it is not a renamed zip. Relevant only for Apple AR copies | [L] |
| ingest | Unreal's USD import is described by Epic as production-ready for assets and still experimental for levels in 5.8 (see [12](12-unreal-tier1.md)); not tested here | [S] |
| the rig | no USD leg exists; a USD writer would need its own validator (usdchecker) and a scene-level compare. Adding one is the roadmap item "USD round trip" in the Unreal chapter | [L] |

What the add-on does with USD today: its splat importer reads splat PointClouds that Blender's USD importer can create (`source/splat_native.py`, header comment, read). That is import, not export.

---

## 8. Ten steps to a trustworthy X3D -> glb run

```text
  1 validate X3D --> 2 pin tools --> 3 frame_start=0 --> 4 import --> 5 export (extras on)
        |                                                                  |
        +----------------------- manifest <-- 8 hash everything <----------+
  6 gate (exit code) --> 7 read 'NOT VALIDATED' + empties --> 9 render compare --> 10 receipt
```

| step | do | pass / fail test | why |
|---|---|---|---|
| 1 | validate the X3D with the fork validator first ([03](03-validator-and-gates.md)) | 0 errors | a broken source gives a glb that is valid and wrong |
| 2 | pin versions: add-on revision, Blender, validator | all three in the manifest | numbers from another build are not comparable |
| 3 | set `scene.frame_start = 0` before import | first animation sample is 0.0 s | gotcha 1 |
| 4 | import with the option set the rig uses; turn on Group instances for scenes with many USE copies | import returns FINISHED; log has no "unsupported type" for nodes you care about | an unsupported node imports to nothing |
| 5 | export with `export_extras=True`, `use_renderable=True`, `export_apply=True` | glb written, extras carry `x3d_def` | identity survives only here |
| 6 | run `node validate_glb.mjs scene.glb` | exit 0; 0 errors; decide a warning budget with `--max-warnings` | structure gate |
| 7 | read the summary lines: `NOT VALIDATED`, triangle count, draw calls | triangles greater than 0 and equal to the X3D's expected count; no unexpected `required` extension | the gate cannot see an empty or point-only glb |
| 8 | write the manifest: sha256 of the X3D and the glb, add-on revision, options | two runs give identical sha256 | determinism is the receipt |
| 9 | render Babylon.js on the glb and X_ITE on the X3D in one browser at one size | mean abs delta and geometry delta recorded with the rig line (Chromium 153, SwiftShader) | looks are a separate gate |
| 10 | store results with a list of expected losses (Section 2) | the list names every dropped behaviour | silence about a loss is a defect |

A scene fails step 7 for the reasons the repo records: `stars-view` (Inline under an extreme scale) before the fix; the two GeoElevationGrid scenes before PR #35 (a 132-byte glb that validated). The check that would have caught each is "triangles greater than zero", not the validator.

---

## Heuristics

| ID | Rule | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-GLT-1 | Never read "0 errors" from the Khronos validator as "the scene survived"; also check triangles, draw calls and node counts against the X3D. | [C] | 48-byte empty glb exits 0 | `Khronos glTF-Validator 2.0.0-dev.3.10`, run 2026-11-14 |
| H-GLT-2 | Print `extensionsNotValidated` next to every pass; a required extension the validator does not know passes at INFO. | [C] | `reqext.glb` passes, wrapper prints `NOT VALIDATED ... REQUIRED` | `Khronos glTF-Validator 2.0.0-dev.3.10`, run 2026-11-14 |
| H-GLT-3 | Treat ROUTE, Script, sensors, PROTO, NURBS, particles, GLSL and physics as expected losses and list them in the manifest, never as "not supported yet" silence. | [L] | carriers table, read | `x3d-blender-io@ab99988` |
| H-GLT-4 | Set `frame_start = 0` before import; do not use `export_anim_slide_to_zero` to fix animation timing. | [L] | first sample 0.041667 s versus 0.0 s; flag ignored without force sampling | `bpy 5.3.0` receipts, read |
| H-GLT-5 | Carry the DEF through `export_extras=True` in node, mesh and material extras; names alone are not the DEF. | [L] | Blender suffixes duplicates (`BoxShape.001`); Transform DEFs are lost in flat import | `x3d-blender-io@ab99988` release notes, read |
| H-GLT-6 | Keep the per-scene manifest beside the glb: x3d sha256, add-on revision, Blender version, glb sha256, validator summary. | [L] | `manifest.py` schema v1, deterministic | `x3d-blender-io@ab99988` |
| H-GLT-7 | For scenes with hundreds of repeated shapes, turn on Group instances; verify node, triangle and draw-call counts do not change except nodes. | [C] | 1,721 to 10 nodes, triangles 2,064 both | `Khronos glTF-Validator 2.0.0-dev.3.10`, run 2026-11-14 |
| H-GLT-8 | Read ratification from the registry file, not from a digest; give the fetch date and the file hash. | [C] | 27 ratified entries on 2026-11-14 | Khronos registry, sha256 prefix `32868b162d85` |
| H-GLT-9 | Treat a scale outside 1e-6 to 1e6 in a parent chain as a bug in waiting; the glb exporter inverts parent matrices in float32. | [L] | 1.057e-16 became 1e8 | `bpy 5.3.0` receipts, read |
| H-GLT-10 | Render to compare in one browser at one size with both engines pinned; compare the geometry mask, not only the whole frame. | [L] | rig README: `mean_abs_delta` versus `geometry_delta` | `X_ITE 16.7.1`, `Babylon.js 9.32.0`, Chromium 153, SwiftShader (carried) |
| H-GLT-11 | A USD hop is a flatten in both directions; never use it as a correctness test. | [L] | digests agree; none run here | read, not run |

---

## Drills

### D-GLT-1 Build a glb that passes and is empty
- **Level:** L2
- **Task:** install the validator, build `empty.glb` from the Section 5.3 snippet, run the gate, then add a `scenes` array with one node and no mesh and run it again.
- **Verify:** `node validate_glb.mjs empty.glb` and read `totalTriangleCount` in the `.validation.json`.
- **Answer:** exit 0, 0 errors, 0 warnings, 0 tris, 0 draw calls, 0 materials. A one-node scene with no mesh also passes (it adds an info at most). The lesson: the gate is silent on emptiness.
- **Checked:** 2026-11-14 `Khronos glTF-Validator 2.0.0-dev.3.10` (the empty glb only; the one-node variant was not run).

### D-GLT-2 Make a required extension pass
- **Level:** L2
- **Task:** build `reqext.glb` (Section 5.3) and run the gate. Which line tells you the content is unchecked, and which field of the JSON report carries it?
- **Verify:** `node validate_glb.mjs reqext.glb` then `python3 -c "import json;print(json.load(open('reqext.glb.validation.json'))['extensionsNotValidated'])"`.
- **Answer:** exit 0; the console line starts `NOT VALIDATED: VENDOR_made_up` and ends `REQUIRED by the file`; the field is `extensionsNotValidated` (`['VENDOR_made_up']`). The validator itself reported 1 info (`UNSUPPORTED_EXTENSION`).
- **Checked:** 2026-11-14 `Khronos glTF-Validator 2.0.0-dev.3.10`.

### D-GLT-3 Count the ratified extensions
- **Level:** L1
- **Task:** fetch the glTF extension registry and count the ratified extensions by prefix.
- **Verify:** `curl -s https://raw.githubusercontent.com/KhronosGroup/glTF/main/extensions/README.md | awk '/^## Ratified/{f=1} /^## In-progress/{f=0} f' | grep -c '^\* \['`
- **Answer:** 27 on 2026-11-14 (24 `KHR_`, 3 `EXT_`). The count will change; the drill is to record the date and the file hash with it.
- **Checked:** 2026-11-14 registry file sha256 prefix `32868b162d85` (counted by line range 12 to 38; the awk form above was not run verbatim).

### D-GLT-4 Instancing leaves the triangle count alone
- **Level:** L2
- **Task:** given a flat and an instanced glb of the same scene, show with the gate that only the node count and size change.
- **Verify:** run `node validate_glb.mjs` on both; compare `totalTriangleCount`, `drawCallCount`, and count `nodes` by parsing the JSON chunk (`struct.unpack('<I', b[12:16])`, then `json.loads(b[20:20+L])`).
- **Answer:** for the exhibition pair: 1,721 nodes versus 10; 491,832 B versus 125,224 B; 2,064 triangles and 8 draw calls in both; 0 errors in both, `EXT_mesh_gpu_instancing` flagged NOT VALIDATED in the instanced one.
- **Checked:** 2026-11-14 `Khronos glTF-Validator 2.0.0-dev.3.10` on carried project files (a reader without the files can use `tests/test_import_gpu_instances_bpy.py` in the repo instead).

### D-GLT-5 Find the loss in a glb
- **Level:** L3
- **Task:** take an X3D with a TimeSensor, a CoordinateInterpolator and two ROUTEs. Convert it, then write a 10-line Python script that lists, from the glb JSON, every place where the ROUTE graph could have survived. Extend it to fail the run if the X3D has ROUTEs and the glb has neither `animations` nor `KHR_interactivity`.
- **Verify:** parse the JSON chunk; count `animations`, channel `path` values, and `extensions`.
- **Answer:** for the Prismatica animated conversion: 1 animation, 1 channel, path `weights`, 0 ROUTE objects anywhere. The script should print the channel paths and flag that the wiring is gone while the effect is baked.
- **Checked:** 2026-11-14 Python `json` on the carried glb (the failing-run extension was not written).

### D-GLT-6 Find the animation start fault without Blender
- **Level:** L3
- **Task:** from any glb with an animation, read the first input accessor's `min` and decide whether the clip is a frame late.
- **Verify:** `accessors[animation.samplers[0].input].min[0]` equals 0.0 for a correct clip; 0.041667 at 24 fps means the `frame_start` fault.
- **Answer:** a correct clip has min 0.0. With the rig's fix the first sample is 0.0 s and the last is 2.0 s for a 2 s cycle; without it 0.041667 s (Blender 5.3.0, repo receipt).
- **Checked:** not run (no animated glb with the fault was produced here).

---

## Honest limits

- **No Blender here.** No export in this chapter was produced in the writing session. Every `bpy 5.3.0` figure is a receipt from `x3d-blender-io@ab99988` (README or release notes) and is [L]. [S] only for items that were never measured anywhere.
- **No USD run at all.** Section 7 is reading and digests. A USD hop could break any row in Section 2.
- **The validator is structural.** `2.0.0-dev.3.10` does not know `EXT_mesh_gpu_instancing`, a *ratified* extension, so the gate says nothing about the contents of the instanced glbs. A newer validator may know it; that was not tried.
- **The carriers table is read, not exercised.** Rows graded [L] were taken from importer code and release notes. NURBS, particles, Script and shaders were not each fed through the importer; "no node read" comes from the AST coverage table of 2026-11-13, itself inferred from string literals.
- **Registry dates are not in the registry.** The ratified list is [C] for 2026-11-14; ratification dates and "glTF 2.1" timing are [S].
- **Engine support is a separate question.** Which engine draws which extension was not enumerated here. Babylon.js 9.32.0 drawing the instanced glb pixel for pixel like the flat one (0 of 262,144 pixels differ) is a repo receipt, carried.
- **Two private-source figures are not used.** A test count and several digest claims about third-party tool versions were left out because they were not re-derived.
- **Converter inputs are not public.** The Unreal-project converter scripts and glbs used in Sections 2.1 and 5.4 are not in a public repository at the time of writing; their counts agree with a public release note, which is the citable source.

---

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-GLT-1 | validator verdict on a 48-byte glb with no scene | 0 errors, 0 warnings, 0 tris | [C] | `Khronos glTF-Validator 2.0.0-dev.3.10` | scratch run 2026-11-14 (snippet in Section 5.3) |
| N-GLT-2 | required unknown extension: validator infos / exit code | 1 info, exit 0 | [C] | `Khronos glTF-Validator 2.0.0-dev.3.10` | scratch run 2026-11-14 |
| N-GLT-3 | ratified extensions in the registry | 27 (24 KHR, 3 EXT) | [C] | Khronos registry sha256 prefix `32868b162d85` | `KhronosGroup/glTF:extensions/README.md`, fetched 2026-11-14 |
| N-GLT-4 | exhibition flat glb nodes / bytes / tris | 1,721 / 491,832 / 2,064 | [C] | `Khronos glTF-Validator 2.0.0-dev.3.10` plus JSON parse | carried project glb, run 2026-11-14; matches `x3d-blender-io@ab99988:release_notes.md` |
| N-GLT-5 | exhibition instanced glb nodes / bytes | 10 / 125,224 | [C] | same | same |
| N-GLT-6 | cathedral flat glb nodes / bytes / tris | 1,224 / 1,097,864 / 27,544 | [C] | same | same |
| N-GLT-7 | cathedral instanced glb nodes / bytes | 16 / 864,228 | [C] | same | same |
| N-GLT-8 | cathedral animated glb bytes / animations / channel path | 4,741,136 / 1 / `weights` | [C] | JSON parse 2026-11-14 | carried project glb |
| N-GLT-9 | repo scenes exporting a glb, all with 0 errors and 0 warnings | 33 of 34 | [L] | `bpy 5.3.0`, `Khronos glTF-Validator 2.0.0-dev.3.10`, carried | `x3d-blender-io@ab99988:tools/fidelity_rig/README.md` |
| N-GLT-10 | of those 33, empty glbs / points-only glbs | 5 / 2 | [L] | same | `x3d-blender-io@ab99988:release_notes.md` |
| N-GLT-11 | first animation sample, default versus `frame_start = 0` | 0.041667 s versus 0.0 s | [L] | `bpy 5.3.0` | `x3d-blender-io@ab99988:tools/fidelity_rig/README.md` |
| N-GLT-12 | `export_apply` True versus False: byte-identical glbs | 34 of 34 scenes | [L] | `bpy 5.3.0` | same |
| N-GLT-13 | extreme scale: exporter result for Inline scale 1.057e-16 | about 1e8 too small (scale near 1e8 instead of 9.46e15) | [L] | `bpy 5.3.0` | `x3d-blender-io@ab99988:release_notes.md` |
| N-GLT-14 | `emissiveColor 0.5` as drawn: X_ITE / as-is glb / sRGB glb | 128 / 186 / 127 | [L] | `X_ITE 16.7.1`, `Babylon.js 9.32.0`, Chromium 153, SwiftShader | `x3d-blender-io@ab99988:release_notes.md` |
| N-GLT-15 | instanced versus flat render in Babylon.js 9.32.0 | 0 of 262,144 pixels differ | [L] | Chromium 153, SwiftShader (carried) | `x3d-blender-io@ab99988:release_notes.md` |
| N-GLT-16 | ROUTE elements in the animated X3D / in its glb | 2 / 0 | [C] | `grep -c '<ROUTE'` and JSON parse, 2026-11-14 | carried project files |

---

## Sources and provenance

- `x3d-blender-io@ab99988`: `tools/fidelity_rig/{validate_glb.mjs, manifest.py, blender_leg.py, package.json, README.md}`, `tests/test_glb_validator_bpy.py`, `release_notes.md`, `source/{import_x3d.py, populate.py, mfstring.py, matrix_safety.py, splat_native.py}`. Public repository `hagopjay/x3d-blender-io`.
- `x3d.docs@f172f67:docs/x3d-blender-io/MASTERCLASS.md`: AST coverage tables (measured 2026-11-13).
- Khronos glTF extension registry (`KhronosGroup/glTF`, `extensions/README.md`), fetched 2026-11-14.
- npm `gltf-validator@2.0.0-dev.3.10`, installed 2026-11-14 in a scratch folder and run through the repo's own `validate_glb.mjs`.
- Two private digests about glTF and USD guides were read as leads; every figure taken from them is either re-derived above or graded [S] and not used as a premise.
- Private-source gaps: converter scripts and glbs for two Unreal-project scenes are not in a public repo; their numbers are cited through the public release notes.
