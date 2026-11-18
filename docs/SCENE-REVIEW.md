# Scene geometry, camera and shader review

Baseline: `11a561623b7539f1f9bf20f8ef7bc5b9706c10d2`.
Scope: the existing twelve-feather observatory and nine-wheel cinematic writer.
The original visual identity, seeded palettes, soundtrack, wheel clock names,
domain order and distinction between evidence and illustrative animation are
retained. This review does not promote an animation into measured repository
activity.

## Repairs and useful extensions

| Concern | Concrete change | Independent acceptance |
| --- | --- | --- |
| Viewpoint aim and navigation pivot were conflated | Observatory viewpoints now carry explicit orientations aimed at their declared centers. `centerOfRotation` remains a navigation pivot, rather than being expected to orient the camera. | Apply the written axis-angle rotation to local forward `(0,0,-1)` using an independent Rodrigues calculation; compare with the target direction. |
| Cinematic camera conversion was singular at a half turn or a vertical sightline | Both writers share a quaternion-branch `look_at` helper. Vertical views choose a deterministic alternate up vector; coincident/nonfinite inputs fail. | Cardinal directions, both poles, a half turn and an oblique direction have known answers. A zero-axis half-turn mutant is refused. |
| Feather tethers began near, rather than at, the actual eye centers | Compute their starting points from the serialized frame angle and eye height. The corrected eye plane is `z=-2.3`, rather than `-2.2`. | Compare actual serialized `FeatherFrame`/`Eye` transforms with the first `Flow` coordinate; maximum permitted component error is `5.1e-5` scene units. |
| Raised feather ridges produced non-planar quads | Write explicit triangles for both vane halves. Vertices, colors, outline and ridge remain the same. | All twelve vanes contain 176 explicit triangles; each written triangle has nonzero area. |
| Cinematic wheel discs were perpendicular to their rings | Rotate each thin cylinder so its longitudinal axis is local ±Z and its disc lies in the torus's XY plane. | Check the transformed default cylinder axis against the ring-plane normal for all nine discs. |
| Three cinematic `smoothstep` calls used descending edges | Use `1-smoothstep(low,high,x)` for the intended descending falloffs. | Decode all actual shader sources and require ascending literal edge pairs. This removes a specified undefined case; it is not shader compilation evidence. |
| Shader transport mixed literal source and URL channel conventions | Write one percent-encoded data URI in each ShaderPart `url` MFString. | Decode all four written ShaderParts; retain the exact GLSL version header and entry point. A source-body-only mutant fails the URL-channel control. |
| Labels were escaped only as XML attributes | Escape the MFString literal and XML attribute as separate layers. | A label containing quotes, ampersands, angle brackets and Windows-style backslashes roundtrips exactly. |
| Shared torus geometry had no parameter guard | Refuse degenerate radii and noninteger/too-small subdivisions before generating coordinates. | Check known radii, nonzero outward face winding, index bounds, preceding typed USE references and refusal cases. |

The geometry improvements make existing relationships more legible. A tether
that visibly misses its wheel center weakens its explanatory role; a disc in the
wrong plane communicates the wrong mechanism. These are worthwhile corrections
even when a schema accepts the document.

The zero/half-turn conversion was a latent helper defect: the bounded current
tour did not have to hit the exact singular direction to justify a known-answer
repair. Similarly, explicit encoded URLs harden portability; no claim is made
that the prior data-URI text channel failed in every X3D browser. The suspicious
`replace(...,0)` expression in the old cylinder writer was a no-op and did not
actually emit duplicate `_d` definitions. It was removed during the disc repair;
the report does not count it as a duplicate-DEF bug.

## Geometry API and generator contract

`gobbler-flyte/build_observatory.py` reads `observatory.json` and writes
`observatory.x3d`, resetting the deterministic seed, XML collector and shared
mesh inventory on every build. It remains Python standard-library code with no
network access. Its scene is X3D 4.0, Immersive with Shape level 5.

Existing SAI names remain stable: `ViewFront`, `ViewClose`, `ViewOrbit`,
`LearningRing`, `Breath`, `Stars`; and per-domain `Feather`, `Wheel`, `Halo`,
`Label`, `Pick`, `DomainView`, `Clock_Wheel`, `Pulse`, `Flow` plus their indices.
The new names `FeatherFrame{i}`, `Eye{i}` and `VaneMesh{i}` expose inspectable
coordinate anchors and surfaces without changing picking or domain identity.

The callable `look_at`, `mfstring`, `material`, `shape`, `line` and `text`
helpers can support other owned demonstrations. `torus` uses the module's
document-scoped `MESHES` registry: clear it before a separate document, or
preserve its preceding definitions. A USE is shared geometry within an X3D
execution context, not a promise of GPU instancing or independent portability.

The cinematic `build.py` imports the shared camera/string helpers from its
sibling. Regeneration writes `scene.x3d` and the same seeded `data.json` bytes;
the synthetic figures and their explicit labels are unchanged.

## Reproduce

```bash
python3 gobbler-flyte/build_observatory.py
python3 gobbler-flyte/build.py
python3 tools/test_scene_geometry.py
python3 -O tools/test_scene_geometry.py
```

All **12 tests pass** normally and with Python optimization enabled. Tests build
both actual writers into a temporary directory, examine those outputs and
require byte equality with the committed scenes. They do not rewrite the
checked-in scenes while executing.

The original scene layout, DEF/USE closure, ROUTE names and deterministic
rebuild checks are complemented by geometric known answers. Those checks do
not establish native X_ITE loading, shader linking, material/color fidelity,
rendered typography, picking, frame rate, GPU memory behavior or soundtrack
quality. Full schema/semantic and native-runtime checks have their own receipts.

## Sources and transferable heuristics

- [X3D 4.0 Navigation component](https://www.web3d.org/documents/specifications/19775-1/V4.0/Part01/components/navigation.html): viewpoint orientation and navigation center are distinct fields with distinct roles.
- [X3D 4.0 Geometry3D component](https://www.web3d.org/documents/specifications/19775-1/V4.0/Part01/components/geometry3D.html): primitive axes, face geometry and the undefined interpretation of non-planar/degenerate polygons.
- [GLSL ES 3.00 specification](https://registry.khronos.org/OpenGL/specs/es/3.0/GLSL_ES_Specification_3.00.pdf), common functions: `smoothstep` requires ordered edges for defined results. The review changes the expression rather than assuming a particular driver implements an inverted ramp.

Transfer the method to STEM and maths scenes: test a camera by the direction it
actually projects, a connector by its transformed endpoints, a surface by its
topology and winding, and a shader by both transport and language semantics.
Then retain native rendering as a separate gate. A visually persuasive object
can be structurally valid while communicating an incorrect geometric relation.
