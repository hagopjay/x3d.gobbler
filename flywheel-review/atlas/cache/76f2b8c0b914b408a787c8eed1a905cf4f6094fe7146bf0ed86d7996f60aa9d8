# 13. Physics in X3D: RigidBodyPhysics, PhysX, MuJoCo and the Ten Minute Physics ports

> **Say it:** A valid X3D physics scene says nothing about whether the simulation is stable, deterministic or right; the physics analogue of the validator is a run record whose hashes replay, whose references are exact, and whose controls are shown able to fail. **[C]**

| field | value |
|---|---|
| chapter code | `PHY` |
| prerequisites | [02 Loom laws](02-loom-laws.md), [03 Validator and gates](03-validator-and-gates.md) |
| after this you can | name the RigidBodyPhysics nodes and the fields an engine may ignore; state what the PhysX and MuJoCo bridges own and what they leave to X3D; read a `loom.physics-run/1` record and say which of 18 codes would fire; write an exact reference for a stepped scheme (not for the continuum); run six numpy drills that show drift, order, stability limits and a check that cannot fail |
| sources read | `x3d.loom@162ab18:x3d.physics/README.md`; `x3d.loom@162ab18:x3d.physics/ten-minute-physics/{README,ERRATA-v1-v4,FIELD-GUIDE-v5,FIELD-GUIDE-v6}.md`; `x3d.loom@162ab18:x3d.physics/physx-bridge/{SPEC,SPEC-RAGDOLL}.md`; `x3d.loom@162ab18:x3d.physics/mujoco-bridge/{PLAN,GATE-0,THREAT-MODEL}.md`, `docs/BRIDGE-CONTRACT.md`, `validation/importer-threat-results.json`; `x3d.loom@162ab18:PHYSICS-PLAYBOOK.md`; `x3d.loom@162ab18:LOOM-v1.md` (law 44, failure modes 148 to 160); `x3d.loom@162ab18:kit/loomkit/physics.py`; `x3d.demo@d10b457:docs/demos/ten-minute-physics/v1..v6`; `x3d.docs@f172f67:docs/x3d.loom/MASTERCLASS.md` (linked, not repeated) |
| instruments used | `x3d.loom@162ab18` kit (`kit/loom physics`, `kit/tests/test_gates.py`, `x3d.physics/tools/physx_controls.py`); `python3 -I` with numpy 2.5.3 (drills below, run 2026-11-14, software only, no GPU); `x3d.demo@d10b457` file listing and grep; numbers carried from receipts are marked "read, not run" |

This chapter teaches the physics layer of the Loom. The X3D validator ([chapter 3](03-validator-and-gates.md)) judges a file. Nothing in the file's grammar says whether the engine behind it drifts, whether a second engine is secretly still stepping, or whether a green test was loosened after it failed. The physics layer adds three instruments for that: exact references, per-step hashes replayed in every host, and controls that must fail. The measurements in the receipts were taken on one Apple-silicon Mac; nothing here has been replayed on a second machine.

---

## 1. The map

```text
 AUTHOR                    BRIDGE / ENGINE                   WITNESS (kit/loom physics)
 ------                    ---------------                   --------------------------
 X3D 4.0 file              reader  -> engine-neutral model   model sha256        PHYS_MODEL_STALE
  RigidBodyCollection      builder -> PxScene / mjModel       per-step hashes     PHYS_TRACE_TAMPERED
  RigidBody                stepper : FIXED step (1/240 s)     replay per host     PHYS_REPLAY_MISSING
  CollidableShape          writer  -> poses, joint outputs                        PHYS_HASH_DRIFT
  joints, CollisionSensor  recorder: command log + hash       exact references    PHYS_NO_REFERENCE
        |                         |                           declared limits     PHYS_LIMIT_WIDENED
        v                         v                           waivers (capped)    PHYS_WAIVERS_OVER_CAP
 validator (XSD + semantic)  loss report: mapped /            controls that fail  PHYS_CONTROL_SURVIVED
  "is the file legal?"        approximated / lost             takeover proof      PHYS_TAKEOVER_UNPROVEN
        |                         |                           loss report         PHYS_LOSS_UNREPORTED
        +---- legal != stable ----+---- stable != right ---- right != reproducible ----+
```

| layer | question it answers | instrument | what it cannot say |
|---|---|---|---|
| Grammar, Meaning (validator) | is the file legal X3D, are routes and containerFields sane | `x3d_mcp fork b4efcd3` | anything about stepping |
| Loss report | which authored fields did the engine honour | `physx-bridge/tests/mapping.test.ts` | whether the honoured fields give the right motion |
| Exact reference | does one law hold to a declared limit | `physx-bridge/tests/analytic.test.ts` | laws without a closed form (ragdoll, drum) |
| Determinism hashes | does the same input give the same bits in each host | FNV-1a per step, `kit/loom physics` | another machine or a real GPU |
| Controls | can the check fail | `physx_controls.py`, `mutate6.py` | that the check measures the right thing |

**In scope:** the X3D RigidBodyPhysics component, the two bridges, the Ten Minute Physics (TMP) port programme, law 44 and failure modes 148 to 160, playbook patterns 11 to 19, six runnable drills. **Not in scope:** the AST teardown of the Loom repo itself (see [the x3d.loom MASTERCLASS](../x3d.loom/MASTERCLASS.md)), the Babylon and Castle physics, GPU rollouts, and the PhysX or MuJoCo engines' internals.

Read next: deeper, [02 Loom laws](02-loom-laws.md) for the numbering of laws 19, 28, 40 to 44; wider, [10 Blender pipeline](10-blender-pipeline.md) for the other place a bake has to be proven rather than asserted.

---

## 2. RigidBodyPhysics in plain terms

The component defines rigid bodies, the shapes that collide, the joints that connect them and the sensors that report contacts. `x3d.physics/physx-bridge/SPEC.md` (draft 1.0) records that X_ITE 16.7.0 registers all 14 nodes of the component and that the field names were checked against X3DUOM 4.0 (read in the component file; the mapping test covers every field). **[C]** for the registration (SPEC.md, read, not re-run here).

| node | role | fields that matter | traps measured in X_ITE 16.7 (SPEC.md, PHYSICS-PLAYBOOK section 6) |
|---|---|---|---|
| `RigidBodyCollection` | the world: gravity, solver, enable switch | `gravity`, `iterations`, `preferAccuracy`, `enabled`, `contactSurfaceThickness`, `maxCorrectionSpeed`, `autoDisable` | `enabled=FALSE` stops Bullet (0 position events in 120 frames); `loadURL()` leaks one step; `errorCorrection` and `constantForceMix` are ODE-only |
| `RigidBody` | one body | `mass`, `centerOfMass`, `inertia` (3x3), `position`, `orientation`, `linearVelocity`, `angularVelocity`, `fixed`, damping, `forces`, `torques` | X_ITE ignores `inertia` and recomputes it from shapes; a literal identity inertia on a 5 g marble would stop it rolling |
| `CollidableShape` | a shape attached to a body | `shape` (Box, Sphere, Cylinder, Cone, IndexedFaceSet), `translation`, `rotation` | offsets directly under a body follow the body; use `CollidableOffset` for a local offset |
| `CollidableOffset` | a shape with a local transform | `translation`, `rotation`, `collidable` | portable scenes put offsets on the inner collidable |
| `CollisionCollection` | contact material for a set of collidables | `frictionCoefficients`, `bounce`, `minBounceSpeed`, `slipFactors`, `softnessConstantForceMix` | X_ITE maps `frictionCoefficients.y` to Bullet rolling friction; PhysX friction is isotropic |
| `CollisionSpace` | grouping for broad phase | `collidables`, `useGeometry` | approximated as filter groups in the PhysX bridge |
| `CollisionSensor` | reports contacts | `contacts` (Contact nodes), `intersections`, `isActive` | ignores `enabled` until its collider is re-assigned; resets `isActive` every frame |
| `Contact` | one contact point | `position`, `contactNormal`, `depth`, `body1`, `body2` | pooled, 16 per sensor per frame in the bridge |
| `BallJoint`, `SingleAxisHingeJoint`, `DoubleAxisHingeJoint`, `SliderJoint`, `UniversalJoint`, `MotorJoint` | constraints | `anchorPoint`, `axis`, `minAngle`, `maxAngle`, outputs `angle`, `separation`, `forceOutput` | X_ITE: no `UniversalJoint`, no `MotorJoint` constraint; hinge ignores min and max angle; joints need both bodies; anchors are world coordinates at load |

Reading rule: X3D declares what a body is; it does not declare the integrator, the step size, the solver (PGS, TGS) or the contact offset. Those are the engine's. Two engines under one file therefore disagree, and the disagreement is a measurement (section 3), not a bug in either.

---

## 3. The PhysX bridge

`x3d.physics/physx-bridge/`: "X3D with PhysX 5" (read at `x3d.loom@162ab18`; README says the source commit is `9a694e9` of a local repository with no remote). Standard X3D 4.0 RigidBodyPhysics scenes run on PhysX 5.12 (WASM, in a Web Worker) under X_ITE 16.7.0, with X_ITE's own Bullet switched off.

### 3.1 What runs where

```text
   scene.x3d (standard nodes, no custom nodes)
        |
        v
   X_ITE 16.7  renders, ROUTEs, SAI          Bullet: RigidBodyCollection.enabled = FALSE
        |  SAI: read nodes, write output fields     (createX3DFromURL -> disable -> replaceWorld,
        v                                            which leaks no step; loadURL() leaks one)
   bridge (TypeScript, main thread)
        |  transferable buffers (no SharedArrayBuffer, so GitHub Pages works)
        v
   Web Worker: PhysX 5.12 via physx-js-webidl 2.9.1, CPU only
        fixed step 1/240 s, accumulator, CCD, sleeping
        FNV-1a hash of every moving body's float32 pose and velocities, each step
        |
        v   writes RigidBody.position/orientation/velocities, joint outputs, Contact nodes
   ROUTEs move the Transforms (authority: PhysX owns dynamics, X3D owns presentation)
```

### 3.2 The contract `x3d-physx/0.1` in one table

| item | rule | source |
|---|---|---|
| scene | X3D 4.0 whose physics is expressed only with RigidBodyPhysics nodes; bridge hints in `WorldInfo` metadata are optional | SPEC.md section 4 |
| identity | DEF names; PhysX handles never persisted | SPEC.md section 4 |
| commands | `run`, `pause`, `step(n)`, `reset`, `set_field`, `rebuild`, `record`, `replay`; ids and expected revision | SPEC.md section 4 |
| observations | per frame: poses, joint outputs, contacts, impact events; per run: a trajectory and a state hash per step | SPEC.md section 4 |
| loss report | per node and field: mapped, approximated (how), ignored (why) | SPEC.md sections 4 and 5 |
| authority | PhysX owns dynamic state and contacts; bridge writes only output fields and the RigidBody pose fields | SPEC.md section 3 |

### 3.3 Mapping, the parts that surprise

| X3D field | what the bridge does | status |
|---|---|---|
| `preferAccuracy` | turns on CCD for every dynamic body and the TGS solver | interpreted, declared |
| `iterations` | per-actor solver position iterations | mapped |
| `RigidBody.inertia` left at identity | computed from the collision shapes (as X_ITE does) | interpreted, declared |
| `minBounceSpeed` below `2*e*g*h/(1-e)` | raised to that value, reported in the loss report (a resting ball otherwise hops forever) | approximated |
| `fixed=TRUE` with a ROUTE-driven pose | kinematic body with one target per physics step sampled from the trajectory | interpreted |
| `errorCorrection`, `constantForceMix`, `finiteRotationAxis`, `slipFactors` | no PhysX equivalent | lost, reported |
| `UniversalJoint` | D6 joint, a constant-velocity joint, not a Hooke joint (0.18 rad/s apart at large angles in the test) | approximated |
| `MotorJoint` | ODE AMotor semantics: torque pair, no constraint (the first draft said "D6 drives" and was wrong) | mapped |

README of the physics folder lists "11 ODE-only fields reported as lost, not dropped" **[C]** (read in `x3d.physics/README.md`; the loss report is `tests/mapping.test.ts`, not re-run here).

### 3.4 The analytic ladder (law 19), measured in Node on PhysX 5.12

One test per law the engine must obey, with the limit declared in the spec before the run. Numbers are read from `physx-bridge/evidence/p1-analytic.json` and the playbook table (read, not re-run: PhysX WASM was not run for this chapter).

| test | reference | limit | measured |
|---|---|---|---|
| free fall, 1 s | the scheme's own discrete solution | 1e-4 m | 1.5e-6 m (file: 1.48e-6) |
| continuum gap on the same run | `y0 - g t^2 / 2` | known number | 0.02044 m, equal to `g h t / 2` |
| pendulum, L = 0.5 m, ball joint and hinge | `2 pi sqrt(L/g) (1 + theta0^2/16)` | 0.5 % | 1.4e-5 relative |
| restitution e = 0.6 | `rebound = e (v + g h)` (restitution is applied to the pre-solver velocity) | 1e-3 | 7.2e-8 worst of 5 bounces |
| incline 30 degrees, mu = 0.3 | `a = g (sin t - mu cos t)` | 2 % | 0.98 % |
| tunnelling, 5 m/s marble, 5 mm wall, 40 phases | CCD on never crosses | 0 of 40 | 0 of 40; control with CCD off: 10 of 40 cross |

The first row is the lesson of the chapter in miniature (failure mode 124, pattern 1). Semi-implicit Euler at step h for n steps gives `y0 - g h^2 n(n+1)/2`, not `y0 - g t^2/2`. Drill D-PHY-2 reproduces both numbers with numpy.

### 3.5 Gates, in the order the witness applies them

`kit/loom physics ROOT --evidence DIR --runs 'runs/*.physics.json' --hosts chromium,firefox,webkit,node --max-waivers 3 --require-takeover`. The kit's docstring lists 18 codes, checked in order, first failure stops the check (`x3d.loom@162ab18:kit/loomkit/physics.py`).

| order | code | what it refuses |
|---|---|---|
| 1 | `PHYS_SCHEMA` | not a `loom.physics-run/1` record |
| 2 | `PHYS_NO_RUNS` | nothing to judge (a pass over nothing is not a pass) |
| 3 | `PHYS_MODEL_STALE` | model file no longer hashes to the recorded sha256 |
| 4 | `PHYS_TRACE_TAMPERED` | per-step hashes do not hash to `trace_sha256` |
| 5 to 8 | `PHYS_REPLAY_MISSING`, `_REPLAY_STEPS`, `_ENGINE_DRIFT`, `_HASH_DRIFT` | a named host has no replay, ran other steps, ran another engine version, or differs at some step (first one reported) |
| 9 | `PHYS_NO_REFERENCE` | no exact reference at all |
| 10 to 12 | `PHYS_LIMIT_WIDENED`, `_FALSE_GREEN`, `_REFERENCE_FAIL` | a limit looser than the declared one; a pass whose own numbers fail it; a miss |
| 13 to 15 | `PHYS_TOLERANCE_FAIL`, `_WAIVER_INCOMPLETE`, `_WAIVERS_OVER_CAP` | an uncovered excursion; a waiver missing owner, date, reason, observed or limit; more waivers than the profile allows |
| 16 | `PHYS_CONTROL_SURVIVED` | a negative control that did not fail |
| 17 | `PHYS_TAKEOVER_UNPROVEN` | old engine not shown off on a host, or a leak not listed (law 41) |
| 18 | `PHYS_LOSS_UNREPORTED` | authored fields dropped without a loss report (law 40) |

### 3.6 What the recorded runs say (read, and re-judged by the witness)

| claim | value | source |
|---|---|---|
| Chromium run, replayed in Chromium, Firefox 146, WebKit 26, Node 24 | 1918 steps, 0 differing hashes | `x3d.physics/runs/physx-grand-cascade-chromium.physics.json`, PLAYBOOK pattern 3 |
| Firefox run, same four hosts | 969 steps, 0 differing hashes | `x3d.physics/runs/physx-grand-cascade-firefox.physics.json` |
| takeover: X_ITE's Bullet off | Chromium, Firefox, WebKit; 1 leak (`loadURL()` runs one step) handled | `evidence/p1-enabled-probe-*.json` |
| waivers | 3 (Galton 220 and 223 of 240 beads against 225; music box in WebKit, 15 of 18 pegs in the worse turn) | `evidence/p5-smoke.json` |
| the two records, judged by the kit on 2026-11-14 | status pass (see D-PHY-8) | re-run |

Not recorded: the ragdoll has no run record (per-step hashes not persisted); its limit overshoot (0.43 rad against 0.2) and the Gravitron gap (2.97 against 2.22 rad/s, 34 %) are in the evidence and the playbook only. The profile `x3d-physics-physx/v1` was not run to acceptance (README, "Not shown, on purpose").

### 3.7 The ragdoll

`SPEC-RAGDOLL.md` builds a PhysX articulation from a standard `HAnimHumanoid`. H-Anim's default `llimit = ulimit = 0 0 0` means free, not locked; a range under 0.01 rad is locked. Spherical limits beyond 1.9 rad and limbs started inside the floor go to NaN. **[C]** as recorded in PLAYBOOK section 6, read not re-run.

---

## 4. The MuJoCo bridge

`x3d.physics/mujoco-bridge/`: MuJoCo 3.17 (WASM) behind X3D scenes, release 0.2.0, Apache-2.0 (read; local repository `069ddd3`, no remote per the README). It differs from the PhysX bridge in kind: it is a **contract plus a threat model first**, an application contract and not an ISO profile (`docs/BRIDGE-CONTRACT.md`: "not an ISO X3D profile or an official MuJoCo interchange standard").

### 4.1 Contract `x3d-mujoco/0.1`, physical profile `contact-arm/1`

| item | rule |
|---|---|
| ownership | MuJoCo owns poses, velocities, actuator response, observations; X3D owns presentation, selection, drag input, authoring intent |
| commands | `target.set`, `model.replace`, `transport.set`, `reset`, `step`; each with id, expected model revision, acknowledgement; stale revision rejected; duplicate id with identical content returns the cached ack |
| coordinates | MuJoCo Z-up wxyz to X3D Y-up axis-angle by a proper change of basis: `p_X = (x_M, z_M, -y_M)`, `R_X = C R_M C^-1` |
| X3D content | standard geometry, `MetadataSet` under `WorldInfo`, `Transform`, `ROUTE`; `ContactForce` and `SimTime` are observation metadata, not X3D sensors |
| transport | local synchronous dispatch only; no WebSocket, no worker transport (read in the contract) |

### 4.2 Gate 0 (2026-11-06, Apple M3, Node 24.22.2): verdict "passed with conditions"

| check | result (as recorded in `GATE-0.md`, read) | re-checked here |
|---|---|---|
| `npm test` | 84 of 84: 34 runtime, 14 workbench, 9 UI DOM, 19 bridge, 8 bridge UI | not run (needs `npm ci`, WASM) |
| importer threat tests | 19 of 19: 16 defences hold, 3 gaps measured | counted from `validation/importer-threat-results.json`: 16 `defended`, 3 `gap`, all `pass` (D-PHY-9) |
| X3D 4.0 XSD | 2 of 2 | read |
| browser smoke | 9 of 9: Chromium 145, Firefox 146, WebKit 26, hardware WebGL 2 | read |
| validator fork `fa0b389` | all 9 scenes XSD-valid, all 9 failed semantics before the fix (5 containerField errors each); 0 errors after fix `a47dc57`, 2 naming warnings | read |

The finding worth copying: **XSD-valid and semantically wrong at once**. `MetadataSet` and `MetadataString` under `WorldInfo` and `Transform` lacked `containerField="metadata"`; X3DUOM 4.0's default for Metadata nodes is `value`. X_ITE rendered it anyway; a strict browser or converter could drop the contract metadata. This is the same class of defect chapter 3's Meaning gate exists for.

### 4.3 Threat model

Assets: the researcher's machine, the integrity of a cited experiment, the agent's context (an MCP tool returning attacker text is a prompt-injection path). Attackers: a shared `.x3d` or ZIP, an MJCF handed to an agent, later an anonymous uploader.

| id | threat | status in `THREAT-MODEL.md` |
|---|---|---|
| T1, T2 | XXE; entity expansion | defended: any `<!DOCTYPE` or `<!ENTITY` refused before parsing |
| T3 | oversized XML | defended: over 200,000 characters refused |
| T4 | script and active content | defended: allow-list of 25 script-free node types; `on*` and `url` attributes refused |
| T5 | URL fields under other names (`backUrl`) | gap, harmless today (value never leaves the importer); closed on the Python path (any attribute ending in `url` refused) |
| T7 | deep nesting | gap: 5,000 nested Transforms took 1.7 s in jsdom; Python path refuses depth over 64 |
| T10 | ZIP bomb, honest headers | defended: 5 MB per member, 12 MB total, 2 MB package |
| T11 | ZIP bomb, lying headers | gap: a 34 KB package inflated 30 MB before rejection; Estimate 2 GB at the 2 MB cap; closed on the Python path (CRC failure without inflating) |
| T12, T13, T14 | path traversal; smuggled MJCF; inconsistent package | defended (in-memory reads of three fixed names; MJCF must equal the regenerated MJCF byte for byte; refusal on mismatch) |
| T15 | substituted trial record | not checked until replay exists |

A gate that lists its own gaps (pattern 10) is worth more than one that lists none. MuJoCo has no run record: checkpoint replay is a phase-1 item in `PLAN.md`; only Gate 0 and the failure modes carry over. The playbook's pattern 9 separates the two things MuJoCo can be used to check: the native build replayed its own WASM trials to 6e-16 rad (that tests the build), while a closed form or a second engine tests the model (failure mode 142).

---

## 5. Why "valid" is not "stable", and the physics of the check

### 5.1 Fixed step against variable step

X_ITE's Bullet steps once per frame with `dt` = a 15-frame moving average of 1/frame-rate, starting from 0 (SPEC.md, read in source; frame-rate dependence measured: headless WebKit ran twice as many frames and the marble ended 3.8 m lower). The PhysX bridge steps at a fixed 1/240 s with an accumulator and replays bit for bit in four hosts.

| property | fixed step (bridge) | variable step (render-locked) |
|---|---|---|
| replay | per-step hashes can match | the same file gives different trajectories per frame rate |
| energy of a symplectic scheme | bounded near the shadow energy | bounded only if the step is constant; jitter adds a random walk (D-PHY-7) |
| cost of a slow frame | catch-up substeps (the bridge catches up lost time rather than dropping it; dropping 300 ms threw a cube 2 cm) | one large step; large steps are where stiff systems explode |
| X3D can say | nothing: no field names the step | nothing |

### 5.2 Solver iterations and substeps

A position-based solver converges by small steps, not by relaxing harder inside a big one. The independent review of the v2 cloth ran equal-cost sweeps (20 sweeps per frame): 20 substeps x 1 iteration gave peak stretch 0.173; 10x2 0.236; 5x4 0.241; 4x5 0.267; 2x10 0.387; 1x20 1.96 (ERRATA-v1-v4, read, reviewer's numpy run, **[C]** by the reviewer, not re-run here). A single constraint cannot show iterations against substeps (v1 bead: 1 against 10 iterations at one substep differ by 5e-15), only that smaller steps lose less energy. D-PHY-3 reproduces the substep trend.

-----> stable? ----------> deterministic? -----------> right?
   XSD+semantic     CFL / step / iters    hash per step, per host     exact reference
   (chapter 3)      D-PHY-6, 7            PHYS_HASH_DRIFT             PHYS_REFERENCE_FAIL
        |               |                       |                          |
   counter-example: a wave grid at c dt/dx = 0.72 is legal X3D and reaches 1e59 (D-PHY-6);
   a billiards port conserves kinetic energy to 1e-15 with the collision rule inverted (D-PHY-4).
```

---

## 6. The Ten Minute Physics port programme

Six batches of independent ports of the ideas in Matthias Müller's *Ten Minute Physics* series to script-free X3D 4.0, built under the Loom's physics witness. The README states the ports are own code written from published method descriptions, no code copied; the upstream repository showed no LICENSE file when checked on 13 Nov 2026, so nothing from it is redistributed, and the work is independent and not endorsed by the author. Scenes and records live in `x3d.demo`, `docs/demos/ten-minute-physics/v1` to `v6` (PRs 19, 20, 22, 23, 24, 25); the generator scripts and committed limits are in `x3d.physics/ten-minute-physics/witness-scripts/`.

A structural fact worth saying plainly: **the ports use no RigidBodyPhysics nodes and no scripts**. `grep -lE 'RigidBody|Script'` over all 17 scenes returns nothing (D-PHY-10). Each scene is a numpy simulation baked into interpolators (for example 200 interpolator elements in the sweep-and-prune scene), so X3D is the presentation and the numbers come from the witness, not from an X3D engine. That is why the validator can pass them and the witness is still what grades the physics.

### 6.1 The scenes, by batch

Counts and numbers: one machine, numpy; validator `x3d_mcp fork 13121b6` (batch 6 receipt: XSD 4.0 plus semantic, 0 errors on its three scenes); renderer X_ITE 16.7.1, headless Chromium, software GL, screenshots only. All numbers below are read from the receipts and field guides, **[L]** unless the row says re-run.

| batch | scene (series number) | status | one-line lesson |
|---|---|---|---|
| v1 | 01 cannonball | merged, corrected by errata | explicit Euler with mirror walls saturates near 12.9 E0; "grows without limit" was refuted |
| v1 | 03 billiards | merged, **buggy rule**, fixed in v3 | impulse fired on separating pairs; kinetic-energy check read 1.33e-15 for the bug |
| v1 | 05 bead (XPBD) | merged, two claims vacuous | residual read after projection is zero by construction; pre-projection 2.4e-2 at 1 substep |
| v2 | 10 jelly | merged | edges cannot see inversion (a mirror image keeps all six lengths); signed-volume constraint needed |
| v2 | 14 cloth | merged | 20 substeps x 1 iteration beats 1 x 20 at equal cost (0.173 against 1.96 peak stretch) |
| v2 | 20 height-field water | merged, explanation corrected | stable only below c dt/dx = 0.7082 (28 x 28 grid); cause is the checkerboard mode, not "outrunning a cell" |
| v3 | 03 billiards, fixed | merged | the head-on exchange test fails the bug; it is exact but axis-aligned, so weak |
| v3 | 06 pendulum engines | merged | MuJoCo 4.0.1 used as a model cross-check, not a build check |
| v4 | 11 spatial hashing | merged | exact when the cell is at least a diameter: 0 missed, 0 false in 49 checks; control caption was wrong by 2x |
| v4 | 17 smoke tunnel | merged | the XSD accepts a ColorInterpolator routed into Color; the semantic check does not |
| v4 | 25 double pendulum vs MuJoCo | merged | agreement 1.3e-7 m over 3 s; the 9.8 s horizon is a 1e-9 model difference times chaos |
| v5 | 15 cloth self collision | passed witness | 0 sheet crossings with collision (10 samples), 91 without |
| v5 | 18 FLIP water | passed witness | slosh period 0.12 % from linear theory; push-apart variant 8.6 % long |
| v5 | 22 rigid-body lab | passed witness | XPBD box slope 0.12 % from Coulomb, MuJoCo 1.4e-5 relative; gyroscopic term required |
| v6 | 19 ODE integrators | passed witness, 11 of 11 controls | order depends on end time; bounded energy is not accuracy |
| v6 | 23 sweep and prune | passed witness | 1002 tests per frame against 19,900 brute force; sort by left edge, not centre (905 pairs missed) |
| v6 | 24 Morton codes and BVH | passed witness | 78.6 tests per query of 4096, 0 wrong of 1000; shrink node boxes by 0.02 and 2466 hits vanish |

That is 17 scenes in six batches (counted from the file listing, D-PHY-10), covering series numbers from 01 to 25. The task brief's "25-ish ports" refers to the series numbering; 17 are built.

### 6.2 What each batch taught the framework

| batch | taught | rule it became |
|---|---|---|
| v1 to v3 | a check that cannot fail for the wrong implementation | law 44, failure modes 148, 149, 150 |
| v3, v5 | an independent review recomputes the claims | 125 claims checked, 55 findings reported, 25 negative findings survived a skeptical second pass, 0 false alarms (ERRATA-v1-v4) |
| v4 | limits "written before the run" cannot be shown when one run writes both `limit` and `declared_limit` | failure mode 156; commit the limits first |
| v6 | limits committed and pushed before the run; the runner refuses to start if the file differs from its commit | pattern 13; limits commit `01bb9dd`, batch 6 receipt |
| v6 | 2 of 11 mutation controls were vacuous (scaled a limit of 0) | failure mode 157; fixed to 11 of 11 |

### 6.3 Errata v1 to v4: the corrections most worth knowing

| # | what was claimed | what the reviewer found | grade |
|---|---|---|---|
| 1 | "collisions conserve energy to 1.3e-15" | same number with the buggy rule (1.33e-15), the fixed (2.0e-15) and no collisions (0) | [C] |
| 2 | the cue "pushed" the struck ball (v1 billiards) | 6211 impulses fired on separating pairs; 131,418 approaching overlaps ignored; cue reached the far cushion with 0.1 % of KE transferred | [C] |
| 3 | cannonball "grows without limit" | saturates at about 12.9 E0 (13.16 at 3000 s, 12.77 at 9000 s) | [C] |
| 4 | bead "constraint drift < 2e-16" | measured after projection; pre-projection 2.4e-2, 1.1e-3, 7.2e-5, 2.9e-6 at 1, 5, 20, 100 substeps | [C] |
| 7 | wave blows up because it "outruns a cell" | c dt/dx was 0.83; cause is the checkerboard mode, limit 0.7082 | [C] |
| 10 | head-on pair test is a complete reference | axis-aligned, so wrong normal passes; 19 of 300 oblique pairs had differing per-step hashes (1 ulp, `np.linalg.norm`) | [C] |
| 11 | "5 cm for 9.8 s: chaos is not the problem" | horizon is `ln(tol / d0) / lambda`: 8.9 s at 1e-9, 5.5 s at 1e-6, 2.0 s at 1e-3 (lambda about 2 per second) | [C] |
| 12 | MuJoCo energy drift 3.4e-6 | stored energy is the last RK4 stage; after `mj_forward` it is 8.86e-9 | [C] |

Grades are the reviewer's, read from the errata (the recomputations were not repeated here except where a drill says so).

### 6.4 Field guide v5 and v6 in one table

| rule (abridged) | number | grade in the guide |
|---|---|---|
| exact oblique pair test in every collision code | head-on test would still pass a wrong normal | Confirmed |
| substeps over iterations at equal cost | cloth peak stretch 55.2 %, 23.0 %, 6.8 % at 4, 8, 20 substeps (29 x 29) | Confirmed |
| hash cell at least the largest diameter | misses 1884, 195, 22, 0 at 0.5, 0.75, 0.9, 1.0 diameters | Confirmed |
| know the CFL number and its cause | 0.7071 infinite grid, 0.7082 on 28 x 28 | Confirmed |
| order is read at an end time (v6) | symplectic Euler 2.00 at T = 2 pi, 1.00 at T = 1; explicit 1.10 at 2 pi | Confirmed |
| bounded energy is not accuracy (v6) | Verlet 0.74 % energy, 0.61 off position after 5 orbits; RK4 0.0022 (283 times) | Confirmed |

---

## 7. Law 44, failure modes 148 to 160, playbook patterns 11 to 19

Ids verified against `x3d.loom@162ab18:LOOM-v1.md` (law 44 at the laws table; failure modes 148 to 160 at the failure-mode table) and `PHYSICS-PLAYBOOK.md` (patterns 11 to 19).

**Law 44, quoted:** "A check is shown able to fail, and a number is not Confirmed until a second reader has tried to break it." Scope: physics profiles first, like law 43.

| failure mode | one line (condensed from LOOM-v1.md) | fix |
|---|---|---|
| 148 | a check passes for a wrong implementation (1.33e-15, 2.0e-15, 0) | run it on the wrong implementation; use an exchange test |
| 149 | quantity read after the step that enforces it | read before the projection or say which state |
| 150 | a second reference was the first again (flux and divergence, difference 7e-16); control had no passing twin | list what each reference cannot see; add a passing twin |
| 151 | only exact collision test was head-on and axis-aligned; `np.linalg.norm` 1 ulp, 19 of 300 pairs differ | oblique reference; write the sqrt out |
| 152 | number read at the wrong state (3.4e-6 against 8.86e-9; 1.2e6 against 1e30) | say when it was read; call the forward pass first |
| 153 | chaos horizon credited to the integrator | horizon formula; run a twin shifted by the difference |
| 154 | explanation without a discriminating test | grade Suspected until an experiment separates it |
| 155 | caption disagrees with code (0.30 against 0.6 diameters) | generate captions from the run's variables |
| 156 | "limits before the run" could not be shown | commit limits first; runner refuses a changed file |
| 157 | two of eleven mutation controls vacuous | nonzero-limit references; report caught of total |
| 158 | two written tunnelling predictions falsified | write before the grid, keep in notes, never wire in |
| 159 | integrator judged from one measurement | two end times; report energy and position separately |
| 160 | spatial structure verified by speed | set equality with brute force; count tests; keep the wrong variant |

| pattern | title (PHYSICS-PLAYBOOK.md) | the discipline in one clause |
|---|---|---|
| 11 | Every check ships its wrong twin (law 44) | a reference is run against a known-wrong implementation first |
| 12 | Read each quantity where nothing has just enforced it | name the state at the read |
| 13 | Commit the limits first, and let the runner check | `tmp6.py` refuses to start if `limits6.json` differs from its commit; writes commit and sha256 into each record |
| 14 | A second reader breaks the numbers before they are Confirmed | 125 claims, 25 survived, 0 false alarms |
| 15 | An explanation is a claim with its own test | CFL 0.7082 against "outruns a cell"; chaos horizon formula |
| 16 | Orders are slopes read at an end time; energy is not position | Verlet 0.61 against RK4 0.0022 |
| 17 | A spatial structure is checked by set equality, and cost is counted | 0 missed or false; tests, not seconds |
| 18 | Count caught controls, and make each one change something | 9 of 11 became 11 of 11 |
| 19 | Keep falsified predictions in the notes and out of the witness | a failing reference would turn the record red for a reason that is not a defect |

Open (PLAYBOOK section 9): `loom physics` does not yet verify a `limits.commit`; the kit ignores that block in the batch 6 records.

---

## 8. Determinism and energy as the physics validator

| validator concept | physics analogue | instrument | what a failure looks like |
|---|---|---|---|
| XSD grammar | record schema | `PHYS_SCHEMA` | missing field |
| semantic rule with exact fix | exact reference with declared limit | `PHYS_REFERENCE_FAIL`, `PHYS_LIMIT_WIDENED` | observed above limit; limit looser than declared |
| the file hash in a ledger | model sha256 and trace sha256 | `PHYS_MODEL_STALE`, `PHYS_TRACE_TAMPERED` | edited step hash |
| second renderer | second host replay | `PHYS_HASH_DRIFT` | first differing step is named |
| negative fixture | control that must fail | `PHYS_CONTROL_SURVIVED` | CCD off: 10 of 40 phases tunnel (this is the control succeeding) |
| warning budget | waiver with owner and date, capped | `PHYS_WAIVERS_OVER_CAP` | more than `max_waivers` |

Energy conservation is a check only against the right reference. For a stepped scheme the right energy is the **shadow energy**: symplectic Euler conserves `E - g h v / 2` and explicit Euler `E + g h v / 2` in free flight (to 9e-13 in the v3 receipts), while both drift by plus or minus `g^2 h^2 / 2` per step in true energy (FIELD-GUIDE-v5 rule 7). Energy is a necessary check for a conservative system and is blind to a wrong collision sign, a wrong normal and a wrong phase (failure modes 148, 159).

---

## 9. The Babylon bridge's own engine, and what X_ITE's Bullet does that the spec does not say

The Babylon bridge (`x3d.loom` `x3d.webgpu/bridge`) reached the rigid body group at tracker batch 37 (x3d.loom PR #56): RigidBodyCollection, RigidBody, CollidableShape, CollidableOffset and CollisionCollection. These five were chosen because they are the nodes the platformer levels, the PhysX scenes and the marble machine all share (RigidBodyCollection and RigidBody each appear in 31 files of the Loom repos, CollidableShape in 27, the joints in 13 to 22). **[C]** (`grep -rl` over the repos at the time of the batch, counted by the batch's author.)

### 9.1 Why a small engine of our own

| option | cost | chosen? |
|---|---|---|
| Babylon's Havok plugin | a binary the page has to fetch; the pages run under tight network rules | no |
| the PhysX 5 bridge (section 3) | a worker and its own build; right for a finished demo | no |
| about 230 lines of JavaScript in `RigidBodyCollection.js` | no download, repeatable, every behaviour explainable and testable against X_ITE | yes |

### 9.2 What the engine does

| part | choice | why |
|---|---|---|
| time | fixed 1/240 s slices up to the clock, catch-up capped at 0.5 s | repeatable; small steps keep contacts stable; a stalled tab cannot spiral (H-PHY-8) |
| integrator | symplectic (semi-implicit) Euler | bounded energy error for the same cost (section 5) |
| contacts | sphere-sphere, sphere-box (closest point), box-box by the separating axis test over 15 axes with corner contacts | a box on a floor gets four points and does not rock |
| solver | sequential impulses, `iterations` passes (default 10), pushes only, Coulomb friction limited to mu times the normal impulse | the standard small-engine choice |
| mass | inertia from the shapes (box and sphere formulas, parallel-axis to the body origin); the `inertia` field is ignored | X_ITE's Bullet derives it from the shapes too |
| output | `position`, `orientation`, `linearVelocity`, `angularVelocity` raised as events | a ROUTE to a Transform is all it takes |

### 9.3 Five things X_ITE's Bullet does (measured at 16.6.0, source read at 16.7.0)

| # | behaviour | measured effect | how it was found |
|---|---|---|---|
| 1 | every body gets friction 0.5 and Bullet multiplies the two bodies' values | default contact friction 0.25; a box thrown at 4 m/s slides 3.06 to 3.27 m where mu 0.5 gives v squared over 2 mu g = 1.63 m | slide test, two runs |
| 2 | `frictionCoefficients` is read only if `appliedParameters` contains `FRICTION_COEFFICIENT_2` (underscore); the 4.0 XSD and the spec write `FRICTION_COEFFICIENT-2` (hyphen) | a valid scene never gets its friction in X_ITE | component source |
| 3 | restitution is set from the body's own speed at configuration time, so a fixed wall (speed 0) gets 0, and Bullet multiplies the two | nothing bounces off a fixed body unless `minBounceSpeed` is 0; with 0, a ball returned at 3.2 to 4 m/s from 4 | wall test, component source |
| 4 | the translation and rotation of a CollidableOffset or CollidableShape reach the physics only in `eventsProcessed`, after the node first receives an event | a sphere offset 1 m below its body rested the body at 0.5 m in X_ITE, 1.5 m in the bridge | offset test, component source |
| 5 | the step follows measured frame time; the collider's `collidables` list is not used for collision | results differ in the third digit between runs | repeated runs, component source |

Instruments: x3d.loom PR #56 fixtures (`RigidBodyCollection`, `RigidBody`, `CollisionCollection`, `CollidableShape`, `CollidableOffset`) run in our reader and in X_ITE 16.6.0 (WebGL2, Chromium 153.0.8010.12, SwiftShader), Babylon 9.32.0; where X_ITE differs the fixture checks each engine against its own value. **[C]** The 16.7.0 source lines (`setFriction(.5)`, `FRICTION_COEFFICIENT_2`, speed against `_minBounceSpeed`, `eventsProcessed`) were read in `docs/vendor/x_ite/assets/components/RigidBodyPhysicsComponent.min.js`; behaviour at 16.7.0 was not run. **[L]**

### 9.4 How the tests keep honest

With collisions switched off the ball fell to y = -10.9 and two equal spheres passed through each other (velocities +2 and -2 instead of swapped), so the head-on pair test, the rest heights and the force rate (2 N on 1 kg gives 2 m/s each second) are real checks (H-PHY-2, H-PHY-3). Because Bullet's step varies, tests use ranges, never exact trajectories.

### 9.5 The six joints (x3d.loom batch 42)

A joint removes degrees of freedom. In the bridge each joint is a few velocity rows in the same loop as the contacts: three point rows (anchors move together), two align rows (hinge axes stay parallel), one perpendicular row (universal and second hinge), one-sided limit rows, and a two-sided motor row capped at maxTorque times the step. Position drift is eased out at 20 percent per step. The hinge angle is a running unwrapped angle, so it is signed and continuous; X_ITE's is the unsigned size of an axis-angle rotation.

| # | X_ITE 16.6.0 behaviour measured | Bridge | Test |
|---|---|---|---|
| 1 | BallJoint: anchor outputs are local to each body | outputs local too (first draft returned world positions) | pendulum stays 2.00 m from the pivot in both engines; body1AnchorPoint [0,0,0] |
| 2 | SingleAxisHingeJoint: limits and stop fields are never applied | limit rows applied | limits plus and minus 0.5 rad: bridge angle -0.50, ball at x 1.755, y 4.034; X_ITE angle 3.45 |
| 3 | DoubleAxisHingeJoint: acts as a plain hinge, swung the ball about the vertical in this pose, hinge1Angle stays 0; motor fields unused | hinge-2 with motor | motor 1 rad/s for 1.5 s: bridge hinge1Angle 1.1 to 1.9; X_ITE ball ended at (0, 5, 2) from (2, 5, 0) |
| 4 | SliderJoint: both frames come from body 1's position; sliderForce never applied | slides on the axis, force applied | gravity off, sliderForce 2: bridge reaches the 2.5 m stop; X_ITE stays |
| 5 | MotorJoint: no torque is applied | torque about motorNAxis | 1 N m on a 1 kg, 0.3 m sphere: about 27.8 rad/s per second in theory, 25.1 measured (wall-clock wait) |
| 6 | UniversalJoint: marked not supported, no constraint | anchors meet, axes stay perpendicular | bridge axes dot product under 0.05; X_ITE ball falls below y 3 in 1.5 s |

Instruments: x3d.loom batch 42 fixtures (`BallJoint`, `SingleAxisHingeJoint`, `SliderJoint`, `DoubleAxisHingeJoint`, `MotorJoint`, `UniversalJoint`) run in our reader and in X_ITE 16.6.0 (WebGL2, Chromium 153.0.8010.12, SwiftShader), Babylon 9.32.0. **[C]** The cause of X_ITE's hinge-2 behaviour (axis mixed into the frame) is **[S]**; the behaviour itself was measured. A first draft of the limit rows had their signs swapped and the hinge ran away to angle -989 and x -90; the limit test is what caught it.

---

## Heuristics

| ID | Rule (imperative, at most 30 words) | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-PHY-1 | Use the scheme's own discrete solution as the exact reference for a stepped engine, and report the continuum gap as a known number. | [C] | PhysX free fall 1.5e-6 m from discrete, 0.0204 m from continuum; D-PHY-2 reproduces both | `x3d.loom@162ab18` `p1-analytic.json`; numpy 2.5.3 |
| H-PHY-2 | Run every new check against a known-wrong implementation before trusting it; if the wrong one passes, the check says nothing. | [C] | KE 0.5 for fixed, buggy and no collisions (D-PHY-4); law 44 | numpy 2.5.3; ERRATA-v1-v4 |
| H-PHY-3 | Add an oblique collision case; a head-on axis-aligned test makes every dot product exact and passes a wrong normal. | [C] | 19 of 300 oblique pairs differed per step; failure mode 151 | ERRATA-v1-v4 (reviewer), read |
| H-PHY-4 | Read constraint residuals before the projection that enforces them, or name the state read. | [C] | bead 7.3e-3 pre-projection at 1 substep (D-PHY-3); review 2.4e-2 | numpy 2.5.3; ERRATA-v1-v4 |
| H-PHY-5 | Fit a convergence order at two end times, neither only a multiple of the period. | [C] | symplectic Euler 1.00 at T = 1, 2.00 at T = 2 pi (D-PHY-5) | numpy 2.5.3 |
| H-PHY-6 | Report energy error and position error as two numbers; bounded energy does not bound phase. | [C] | Verlet 0.74 % energy, 0.61 off position; RK4 0.0022 off | `x3d.demo@d10b457` v6 receipt, read |
| H-PHY-7 | Know the CFL number of a grid scheme and its cause before tuning anything else. | [C] | 0.72 reaches 1e59 on 28 x 28 within 400 steps, 0.7071 stays 4.6e-3 (D-PHY-6) | numpy 2.5.3 |
| H-PHY-8 | Step at a fixed dt with an accumulator; never let the render rate set the physics step. | [L] | X_ITE Bullet moving-average dt; jitter changes trajectory (D-PHY-7); bridge fixed 1/240 s | `physx-bridge/SPEC.md`; numpy 2.5.3 |
| H-PHY-9 | Hash every step, replay in every named host, and name the first differing step; a final-state hash alone cannot localise. | [C] | 1918 and 969 steps, 0 differing hashes in 4 hosts | `kit/loom physics` on `x3d.physics/runs` |
| H-PHY-10 | When page code replaces a runtime's engine, prove the old one is off in each host and list its leaks. | [C] | Bullet off in 3 browsers; `loadURL()` leaks one step | `evidence/p1-enabled-probe-*.json`, read |
| H-PHY-11 | Commit the limits file before the run and let the runner refuse a changed file; `limit` and `declared_limit` from one run prove nothing. | [C] | failure mode 156; v6 limits commit `01bb9dd` | `x3d.demo@d10b457` receipt |
| H-PHY-12 | A mutation control must change the record; count caught of total and distrust a control whose reference limit is 0. | [C] | 9 of 11 became 11 of 11 | v6 receipt |
| H-PHY-14 | Treat a second engine as a model check, not a build check, and compute the chaos horizon before blaming a method. | [C] | MuJoCo against RK4 1.3e-7 m over 3 s; horizon 8.9 s at 1e-9 | ERRATA-v1-v4, read |
| H-PHY-15 | Run the schema check and the semantic check; the XSD accepts routes and containerFields the semantic rules reject. | [C] | MuJoCo bridge: 9 of 9 XSD-valid, 9 of 9 semantic failures before fix | `x3d_mcp fork fa0b389` as recorded in GATE-0 |
| H-PHY-16 | Read the engine's contact parameters from its source before you compare a bridge to it; Bullet multiplies friction and restitution of the two bodies, so one value hides in the product. | [C] | default friction 0.25 against 0.5; slide 3.06 to 3.27 m against 1.63 m | x3d.loom PR #56 fixtures; X_ITE 16.6.0, Chromium 153, SwiftShader; source read at 16.7.0 |
| H-PHY-17 | Write `appliedParameters` in the spelling the engine reads and check what it does with the spec's; X_ITE reads `FRICTION_COEFFICIENT_2`, the XSD says `FRICTION_COEFFICIENT-2`. | [C] | one underscore, one hyphen | `RigidBodyPhysicsComponent.min.js` 16.7.0, read |
| H-PHY-18 | For a bounce test against a wall or floor set `minBounceSpeed` to 0 in X_ITE; a fixed body has speed 0, so the default 0.1 gives it restitution 0. | [C] | ball returned at 3.2 to 4 m/s only with 0 | x3d.loom PR #56 `CollisionCollection` fixture; X_ITE 16.6.0 |
| H-PHY-19 | Do not trust a CollidableOffset or CollidableShape translation in X_ITE until the node has received an event; test where the body rests. | [C] | rest height 0.5 m in X_ITE against 1.5 m expected | x3d.loom PR #56 `CollidableOffset` fixture; X_ITE 16.6.0 |
| H-PHY-20 | When two engines differ by design, check each against its own written value and log the gap; never loosen a tolerance until both pass. | [L] | five nodes, four per-engine values | x3d.loom PR #56 fixtures |
| H-PHY-21 | Count the degrees of freedom a joint removes before testing it: ball 3, hinge 5, slider 5, universal 4, motor 0; then test the one that is left. | [C] | six fixtures, each checking the free motion (swing, slide, spin) as well as the constraint | x3d.loom batch 42 fixtures; X_ITE 16.6.0 |
| H-PHY-22 | Test a joint limit by checking the body against the limit, not that the joint exists; X_ITE 16.6.0 builds hinges without limits. | [C] | bridge angle -0.50 against X_ITE 3.45 for the same swing | `SingleAxisHingeJoint` fixture |
| H-PHY-23 | Treat an unsigned joint angle as a size and compare absolute values across engines; do not compare signs. | [C] | X_ITE angle 3.45 where a signed continuous angle would pass pi | `SingleAxisHingeJoint` fixture |
| H-PHY-24 | Check that a force or torque field does anything at all (rate of change over a second) before trusting a joint node; X_ITE reads sliderForce and axisTorque and applies neither. | [C] | slider stays; motor angular velocity changes under 0.01 rad/s in X_ITE, 25.1 rad/s per second in the bridge | `SliderJoint`, `MotorJoint` fixtures |

---

## Drills

All code below is copyable and was run with `python3 -I` and numpy 2.5.3 on 2026-11-14 on the machine of this session (software only). `import numpy as np, math` and `g = 9.81` are assumed.

### D-PHY-1 Symplectic against explicit Euler on a pendulum
- **Level:** L2
- **Task:** Integrate a pendulum (L = 1, theta0 = 1 rad, h = 0.01, T = 100 s) with explicit Euler and with symplectic Euler. Report final and maximum relative energy change `(E - E0)/E0`.
- **Verify:**
```python
def pend(method, h, T, th0=1.0, L=1.0):
    th, w = th0, 0.0
    E = lambda th, w: 0.5*L*L*w*w + g*L*(1-math.cos(th))
    E0 = E(th, w); Es = []
    for _ in range(int(round(T/h))):
        if method == 'explicit':
            a = -g/L*math.sin(th); th, w = th + h*w, w + h*a
        else:
            w += h*(-g/L*math.sin(th)); th += h*w
        Es.append(E(th, w))
    return E0, np.array(Es)
for m in ('explicit', 'symplectic'):
    E0, Es = pend(m, 0.01, 100)
    print(m, (Es[-1]-E0)/E0, np.max(abs(Es-E0))/E0)
```
- **Answer:** explicit: final +10.89, max 11.01 (energy has grown elevenfold). Symplectic: final +0.0002, max 0.0150 (bounded oscillation around the shadow energy).
- **Checked:** `2026-11-14 python3 -I numpy 2.5.3`: explicit 10.8933 and 11.0130, symplectic 0.0002 and 0.0150.

### D-PHY-2 The exact reference for a stepped scheme
- **Level:** L2
- **Task:** Free fall from y0 = 10 m for 1 s at h = 1/240 with semi-implicit Euler (velocity first). Compare with the discrete closed form `y0 - g h^2 n(n+1)/2` and with `y0 - g t^2/2`.
- **Verify:**
```python
h = 1/240; n = 240; y = 10.0; v = 0.0
for _ in range(n): v -= g*h; y += v*h
print(y, 10 - g*h*h*n*(n+1)/2, 10 - 0.5*g, y - (10 - 0.5*g), g*h/2)
```
- **Answer:** simulated 5.0745625 equals the discrete value to the printed digits; the continuum value is 5.095; the gap -0.020437 equals `g h t / 2` = 0.020438 (t = 1). PhysX 5.12 shows the same gap in its own run (0.02044 m, read from `p1-analytic.json`).
- **Checked:** `2026-11-14 python3 -I numpy 2.5.3`: sim 5.074562500, discrete 5.074562500, continuum 5.095000000, gap -0.020437.

### D-PHY-3 XPBD bead on a wire: substeps against residual and energy
- **Level:** L2
- **Task:** A unit-mass bead starts at rest at (1, 0) on a circular wire of radius 1, gravity -y, 60 frames per second, 10 s. Each substep: predict, then project onto the circle, then set `v = (x - x_prev)/h`. Record the worst violation **before** projection and the final energy change for 1, 5, 20, 100 substeps per frame.
- **Verify:**
```python
def bead(sub, frame=1/60, T=10, R=1.0):
    h = frame/sub; x = np.array([R, 0.0]); v = np.zeros(2)
    E = lambda x, v: 0.5*(v@v) + g*x[1]
    E0 = E(x, v); worst = 0
    for _ in range(int(T/frame)):
        for _ in range(sub):
            xp = x.copy(); v = v + h*np.array([0, -g]); x = x + h*v
            worst = max(worst, abs(math.sqrt(x@x) - R))
            x = x*(R/math.sqrt(x@x)); v = (x - xp)/h
    return worst, E(x, v) - E0
for s in (1, 5, 20, 100): print(s, *bead(s))
```
- **Answer:** pre-projection violation falls about 23x, 16x, 25x per step (7.3e-3, 3.2e-4, 2.0e-5, 8.2e-7); energy lost by t = 10 s is 8.79, 4.36, 1.46, 0.31 J/kg (the swing amplitude is g R = 9.81). Read after the projection, the violation would be about 1e-16 for every row (the review's point). The review's numbers differ (2.4e-2 at 1 substep) because its bead, start and time differ; the trend is the claim.
- **Checked:** `2026-11-14 python3 -I numpy 2.5.3`: 7.31e-03, 3.19e-04, 2.03e-05, 8.16e-07; dE -8.7945, -4.3632, -1.4550, -0.3125.

### D-PHY-4 A check that cannot fail: the wrong twin
- **Level:** L3
- **Task:** Two equal discs of diameter 1, mass 1; the cue moves at 1 m/s into the other at rest, head-on. Implement the collision with the correct trigger (approaching, `vrel > 0`) and with the inverted trigger (separating, `vrel < 0`), plus no collisions. (a) Show kinetic energy at the end is 0.5 in all three. (b) Find a test that tells them apart. Extend: write the oblique version and state the expected outgoing angle.
- **Verify:**
```python
def run(rule, steps=1500, h=1e-3):
    p = np.array([[-1.0, 0.0], [0.0, 0.0]]); v = np.array([[1.0, 0.0], [0.0, 0.0]])
    for i in range(steps):
        p += h*v
        d = p[1]-p[0]; dist = np.linalg.norm(d)
        if dist < 1.0 and rule != 'none':
            n = d/dist; vr = (v[0]-v[1])@n
            if (vr > 0) if rule == 'fixed' else (vr < 0):
                dv = vr*n; v[0] -= dv; v[1] += dv
        if i == 1000: v_at = v.copy()
    return v, v_at
for r in ('fixed', 'buggy', 'none'):
    vf, v1 = run(r); print(r, 0.5*np.sum(vf*vf), v1[0], v1[1])
```
- **Answer:** (a) KE end is 0.500000 for fixed, buggy and none. (b) The exchange test: at t = 1.0 s the fixed rule has the struck disc moving at 1.0 and the cue at 0; the buggy rule and no collision leave the struck disc at rest (the cue passes through it; the buggy rule exchanges only after the discs pass each other). Oblique: tangential components unchanged, normal components swapped, so the outgoing velocities are perpendicular (dot about -2e-16, failure mode 148). Because this scene is axis-aligned, it is the weak form; failure mode 151 asks for the oblique one.
- **Checked:** `2026-11-14 python3 -I numpy 2.5.3`: KE 0.500000 three times; v at t = 1.0 s fixed [0,0] and [1,0]; buggy [1,0] and [0,0]; none [1,0] and [0,0]. The oblique extension was not run.

### D-PHY-5 Order of a method depends on where you measure
- **Level:** L2
- **Task:** Integrate the harmonic oscillator `x'' = -x` (x0 = 1, v0 = 0) with explicit and symplectic Euler to T = 1 and to T = 2 pi at 50, 100, 200, 400, 800 steps. Fit the log-log slope of the phase-space error `hypot(x - cos T, v + sin T)` against h.
- **Verify:**
```python
def ho(m, h, T):
    x, v = 1.0, 0.0
    for _ in range(int(round(T/h))):
        if m == 'explicit': x, v = x + h*v, v - h*x
        else: v -= h*x; x += h*v
    return x, v
for T in (1.0, 2*math.pi):
    for m in ('explicit', 'symplectic'):
        hs = [T/k for k in (50, 100, 200, 400, 800)]
        errs = [math.hypot(ho(m, h, T)[0]-math.cos(T), ho(m, h, T)[1]+math.sin(T)) for h in hs]
        print(T, m, np.polyfit(np.log(hs), np.log(errs), 1)[0])
```
- **Answer:** T = 1: 1.00 and 1.00. T = 2 pi: explicit 1.06, symplectic 2.00. A first-order method measures second order at one full period because the leading error term cancels; the v6 receipt reports 2.0 and 1.10 for the same effect (explicit 1.06 here against 1.10 there: the step-size grids differ).
- **Checked:** `2026-11-14 python3 -I numpy 2.5.3`: T=1 explicit 1.00, symplectic 1.00; T=2pi explicit 1.06, symplectic 2.00.

### D-PHY-6 The CFL limit is a stability limit, not "outrunning a cell"
- **Level:** L3
- **Task:** Run the 2D wave equation `v += (c dt/dx)^2 * laplacian(u); u += v` (symplectic Euler, 5-point Laplacian, fixed boundaries) on a 28 x 28 grid with a 1e-3 random start, 400 steps, at c dt/dx = 0.60, 0.70, 0.7071, 0.72, 0.80. Then bisect the limit and explain it with the largest Laplacian eigenvalue.
- **Verify:**
```python
def wave(cfl, N=28, steps=400):
    u = np.zeros((N, N)); vv = np.zeros((N, N)); rng = np.random.default_rng(1)
    u[1:-1, 1:-1] = rng.normal(size=(N-2, N-2))*1e-3; k = cfl*cfl
    for _ in range(steps):
        lap = np.zeros_like(u)
        lap[1:-1, 1:-1] = u[2:, 1:-1]+u[:-2, 1:-1]+u[1:-1, 2:]+u[1:-1, :-2]-4*u[1:-1, 1:-1]
        vv += k*lap; u += vv; u[0] = u[-1] = 0; u[:, 0] = u[:, -1] = 0
    return np.abs(u).max()
for c in (0.6, 0.70, 0.7071, 0.72, 0.8): print(c, wave(c))
```
- **Answer:** at 0.60, 0.70 and 0.7071 the amplitude stays near 1e-3 to 5e-3; at 0.72 it is 1.2e59 and at 0.80 4.4e170. Stability needs `c^2 dt^2 lambda_max <= 4`; for the 5-point Laplacian lambda_max/dx^2 tends to 8 in two dimensions, giving `c dt/dx <= 1/sqrt(2) = 0.7071` (0.7082 on the finite 28 x 28 grid per the review's bisection, because the finite grid's largest eigenvalue is a bit under 8). The wave speed in cells per step (0.72) is under one, so "outrunning a cell" cannot be the cause. The bisection to 0.7082 was **not** run here.
- **Checked:** `2026-11-14 python3 -I numpy 2.5.3`: 0.6 -> 2.69e-03; 0.70 -> 3.42e-03; 0.7071 -> 4.65e-03; 0.72 -> 1.18e+59; 0.80 -> 4.40e+170. Bisection not run.

### D-PHY-7 Fixed against variable step
- **Level:** L2
- **Task:** Symplectic-Euler pendulum, 10,000 steps of nominal h = 0.01. Run with jitter 0 and with each step drawn uniformly from `h (1 +- 0.5)`, for two random seeds. Compare energy change and final angle.
- **Verify:**
```python
def vs(jit, seed):
    rng = np.random.default_rng(seed); th, w = 1.0, 0.0
    E0 = 0.5*w*w + g*(1-math.cos(th))
    for _ in range(10000):
        h = 0.01*(1+jit*rng.uniform(-1, 1)); w += h*(-g*math.sin(th)); th += h*w
    return (0.5*w*w + g*(1-math.cos(th)) - E0)/E0, th
for j in (0, 0.5): print(j, vs(j, 0), vs(j, 1))
```
- **Answer:** jitter 0: dE/E0 0.0002, final angle 0.007586 for both seeds (the seed is unused, so bit-identical). Jitter 0.5: dE/E0 -0.0117, final angle 0.1592 against 0.4356 for the two seeds. Same file, same nominal step, different runs: with a render-locked variable step, a hash replay across hosts is impossible by construction.
- **Checked:** `2026-11-14 python3 -I numpy 2.5.3`: jitter 0 dE/E0 0.0002 theta 0.007586 twice; jitter 0.5 dE/E0 -0.0117, theta 0.159239 and 0.435642.

### D-PHY-8 Re-judge the PhysX run records and attack them
- **Level:** L2
- **Task:** From a checkout of `x3d.loom`, run the witness on the two real records, then the 14 negative controls, then the kit self-test. Report status and counts.
- **Verify:**
```bash
kit/loom physics x3d.physics --evidence x3d.physics/runs/physics-20261113/evidence --runs 'runs/*.physics.json' --hosts chromium,firefox,webkit,node --max-waivers 3 --require-takeover
python3 -I x3d.physics/tools/physx_controls.py
python3 -I kit/tests/test_gates.py
```
- **Answer:** witness status pass, reason empty; controls "14 caught with the intended code"; kit test 82 negative controls caught with the intended code in normal Python and under `-O`. Note: the `--runs` glob is relative to the ROOT argument (`x3d.physics`); using `x3d.physics/runs/*.physics.json` there returns `NO_FILES_MATCHED`.
- **Checked:** `2026-11-14 x3d.loom@162ab18 kit/loom physics`: status pass; `physx_controls.py`: "14 controls on the real record, 14 caught with the intended code"; `test_gates.py`: 82 controls, optimized False and True. This verifies the records replay in the **recorded** hosts (it reads the hashes; it does not run PhysX again).

### D-PHY-9 Count the MuJoCo threat checks yourself
- **Level:** L1
- **Task:** From `x3d.physics/mujoco-bridge/validation/importer-threat-results.json`, count checks by `kind` and `status`, and compare with the claim "19 of 19: 16 defences hold, 3 gaps measured".
- **Verify:**
```python
import json, collections
d = json.load(open('x3d.physics/mujoco-bridge/validation/importer-threat-results.json'))
print(collections.Counter((c['kind'], c['status']) for c in d['checks']))
```
- **Answer:** 16 `defended` with status `pass` and 3 `gap` with status `pass` (a gap check "passes" by measuring the weak behaviour). A `gap` that shows `pass` is not a defence; read the kind column.
- **Checked:** `2026-11-14 x3d.loom@162ab18`: Counter({('defended','pass'): 16, ('gap','pass'): 3}).

### D-PHY-10 The ports are baked, not simulated by X3D
- **Level:** L1
- **Task:** In a checkout of `x3d.demo`, count the `.x3d` scenes under `docs/demos/ten-minute-physics/` and grep them for `RigidBody` and `Script`. Count Interpolator elements in `v6/23-sweep-and-prune.x3d`.
- **Verify:**
```bash
ls docs/demos/ten-minute-physics/v*/*.x3d | wc -l
grep -lE 'RigidBody|Script' docs/demos/ten-minute-physics/v*/*.x3d | wc -l
grep -c Interpolator docs/demos/ten-minute-physics/v6/23-sweep-and-prune.x3d
```
- **Answer:** 17 scenes; 0 files with RigidBody or Script; `grep -c` counts matching lines: 200. A script-free scene cannot step anything; the numbers come from the generators in `witness-scripts/`. (`grep -c` counts lines, not occurrences; the scene is one element per line in this file.)
- **Checked:** `2026-11-14 x3d.demo@d10b457 grep`: 17; 0; 200.

### D-PHY-11 Find the four X_ITE contact rules in the source
- **Level:** L2 (run a tool and compare)
- **Task:** In the vendored `docs/vendor/x_ite/assets/components/RigidBodyPhysicsComponent.min.js`, find (a) the default friction set on every body, (b) the spelling of the friction parameter it recognises, (c) the test that decides a body's restitution, (d) where a collidable's translation reaches the physics. Say what each means for a scene that follows the spec.
- **Verify:** `grep -o 'setFriction([^)]*)' F`, `grep -o 'FRICTION_COEFFICIENT_2' F | wc -l`, `grep -o 'getLinearVelocity().length()>=t._minBounceSpeed' F`, `grep -o 'eventsProcessed(){this.matrix.setTransform' F`, with F the file above.
- **Answer:** (a) `setFriction(.5)` for every body, then `setFriction(t._frictionCoefficients.x)` only when the parameter is applied; (b) `FRICTION_COEFFICIENT_2` with an underscore, appearing twice, never the spec's hyphen form; (c) restitution is the bounce only when the body's own linear speed is at least `minBounceSpeed`, otherwise 0, so a fixed body gets 0; (d) in `eventsProcessed`, after the node first receives an event.
- **Checked:** 2026-11-14 `grep` over X_ITE 16.7.0 (read, behaviour not run)

---

## Honest limits

- **[C] The X_ITE Bullet measurements are 16.6.0 on a software GPU in headless Chromium 153.** The 16.7.0 file shows the same code for friction, restitution and `eventsProcessed`; its behaviour was not run. Bullet's variable step means a distance such as 3.06 to 3.27 m is a range, not a constant. The bridge's own engine has no sleeping, no joints yet, and collides boxes and spheres exactly (cylinders and cones as spheres).
- **[C] One machine.** Every replay in the bridge records ran on one Apple-silicon Mac; "deterministic across hosts" means across Chromium, Firefox 146, WebKit 26 and Node 24 on it, not across machines or CPUs (README, "Not shown"; PLAYBOOK section 5, `visible_not_run: cross-machine`).
- **[C] PhysX and MuJoCo were not run for this chapter.** All engine numbers (analytic ladder, 1918 and 969 steps, Gate 0 counts) are read from evidence files and receipts. What was re-run: the witness over the records (it reads hashes), 14 controls, 82 kit controls, the threat count, the numpy drills.
- **[C] The ragdoll and MuJoCo have no run record.** The witness cannot judge them; their gaps (0.43 rad against 0.2; 2.97 against 2.22 rad/s) are logged and not tuned.
- **[L] The profile `x3d-physics-physx/v1` was not run to acceptance.** Only the `physics` witness ran; Grammar, Meaning, Traps, Page traps and Behaviour on these scenes need the validator fork checkout and a browser.
- **[L] The ports' numbers are one-machine counts and measurements** from the receipts; the ERRATA reviewers recomputed v1 to v4, and v5 and v6 have the second-reader step only in the sense that a different reviewer pass is described for earlier batches. A review of v5 and v6 is not recorded here. The v6 receipt grades the Kepler crossover Suspected.
- **[L] Source disagreement on counts.** The task brief mentions "25-ish ports"; the directory has 17 scenes, with series numbers up to 25. The 17 stands (counted).
- **[C] Pre-registration is only as good as git history.** Even batch 6 can be rewritten by the repository owner (failure mode 156); `loom physics` does not yet read `limits.commit`.
- **[L] Both bridges' repositories are cited by short sha from README text** (`9a694e9`, `069ddd3`); they are described as local with no remote, so those two commits are not resolvable from the public record.

---

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-PHY-1 | Explicit Euler pendulum energy growth, h = 0.01, 100 s | +10.89 (final dE/E0) | [C] | numpy 2.5.3 | D-PHY-1 |
| N-PHY-2 | Symplectic Euler pendulum, same run | +0.0002 final, 0.0150 max | [C] | numpy 2.5.3 | D-PHY-1 |
| N-PHY-3 | Discrete free fall against continuum gap, 1 s at 1/240 | -0.020437 m (`g h t/2` = 0.020438) | [C] | numpy 2.5.3 | D-PHY-2 |
| N-PHY-4 | PhysX 5.12 free fall error against discrete solution | 1.5e-6 m (limit 1e-4) | [L] | read, not run: `x3d.loom@162ab18:x3d.physics/physx-bridge/evidence/p1-analytic.json` | same file |
| N-PHY-5 | Bead pre-projection violation, 1 to 100 substeps | 7.31e-3, 3.19e-4, 2.03e-5, 8.16e-7 | [C] | numpy 2.5.3 | D-PHY-3 |
| N-PHY-6 | Kinetic energy, fixed, buggy and no collisions | 0.500000 each | [C] | numpy 2.5.3 | D-PHY-4 |
| N-PHY-7 | Order of symplectic Euler, T = 1 and T = 2 pi | 1.00 and 2.00 | [C] | numpy 2.5.3 | D-PHY-5 |
| N-PHY-8 | Wave grid max amplitude at c dt/dx 0.7071 and 0.72, 400 steps | 4.65e-3 and 1.18e59 | [C] | numpy 2.5.3 | D-PHY-6 |
| N-PHY-9 | Variable-step pendulum, two seeds, jitter 0.5 | final angle 0.1592 and 0.4356 | [C] | numpy 2.5.3 | D-PHY-7 |
| N-PHY-10 | Physics witness on the 2 PhysX records | pass | [C] | `x3d.loom@162ab18` `kit/loom physics` | D-PHY-8 |
| N-PHY-11 | Negative controls on the real records | 14 of 14 caught | [C] | `x3d.loom@162ab18` `physx_controls.py` | D-PHY-8 |
| N-PHY-12 | Kit self-test controls | 82, normal and `-O` | [C] | `x3d.loom@162ab18` `kit/tests/test_gates.py` | D-PHY-8 |
| N-PHY-13 | `PHYS_*` codes in the witness | 18 listed in the docstring | [C] | `x3d.loom@162ab18:kit/loomkit/physics.py` | section 3.5 |
| N-PHY-14 | MuJoCo importer threat checks | 16 defended and 3 gaps (19) | [C] | read via python json count, `x3d.loom@162ab18` | D-PHY-9 |
| N-PHY-15 | Ten Minute Physics scenes built | 17 in 6 batches | [C] | `ls`, `x3d.demo@d10b457` | D-PHY-10 |
| N-PHY-16 | RigidBody or Script elements in those scenes | 0 files | [C] | `grep -lE`, `x3d.demo@d10b457` | D-PHY-10 |
| N-PHY-17 | Replay of the Chromium run: steps and differing hashes | 1918 steps, 0 differing, 4 hosts | [L] | read, `x3d.loom@162ab18:x3d.physics/runs/physx-grand-cascade-chromium.physics.json` | PLAYBOOK pattern 3 |
| N-PHY-18 | CCD tunnelling, 5 m/s marble, 5 mm wall | 0 of 40 on, 10 of 40 off | [L] | read, `physx-bridge/tests/analytic.test.ts` evidence | PLAYBOOK pattern 7 |
| N-PHY-19 | Independent review of v1 to v4 | 125 claims, 55 findings, 25 survived, 0 false alarms | [L] | read, `ten-minute-physics/ERRATA-v1-v4.md` | law 44 row |
| N-PHY-20 | Default contact friction in X_ITE (two bodies at 0.5, multiplied) | 0.25 | [C] | x3d.loom PR #56, X_ITE 16.6.0, Chromium 153, SwiftShader | section 9.3 |
| N-PHY-21 | Box thrown at 4 m/s, slide distance in X_ITE and in the bridge | 3.06 to 3.27 m and 1.63 m | [C] | same rig | section 9.3 |
| N-PHY-22 | Ball at 4 m/s against a fixed wall, bounce 1, minBounceSpeed 0, speed after | 3.2 to 4 m/s in X_ITE; 3.99 in the bridge | [C] | same rig | section 9.3 |
| N-PHY-23 | Body rest height with a sphere offset 1 m below the origin | 0.5 m in X_ITE, 1.5 m in the bridge | [C] | same rig | section 9.3 |
| N-PHY-24 | Files using RigidBodyCollection, RigidBody, CollidableShape | 31, 31, 27 | [L] | `grep -rl` by the batch author over the Loom repos, not re-run here | section 9 |
| N-PHY-25 | Hinge limits plus and minus 0.5 rad, final ball position, bridge | x 1.755, y 4.034, angle -0.50 | [C] | batch 42 `SingleAxisHingeJoint` probe; X_ITE 16.6.0, Chromium 153, SwiftShader | section 9.5 |
| N-PHY-26 | Same swing in X_ITE, unsigned angle | 3.45 (limits ignored) | [C] | same rig | section 9.5 |
| N-PHY-27 | Motor torque 1 N m on 1 kg, 0.3 m sphere, angular acceleration | 25.1 rad/s per second measured; 27.8 theory | [C] | same rig, wall-clock wait | section 9.5 |
| N-PHY-28 | DoubleAxisHingeJoint motor 1 rad/s for 1.5 s, hinge1Angle band in the test | 1.1 to 1.9 rad | [C] | same rig | section 9.5 |

---

## Sources and provenance

| repo@sha | path | read how |
|---|---|---|
| `x3d.loom@162ab18` | `x3d.physics/README.md`, `ten-minute-physics/*.md`, `physx-bridge/SPEC.md`, `SPEC-RAGDOLL.md`, `mujoco-bridge/{PLAN,GATE-0,THREAT-MODEL}.md`, `docs/BRIDGE-CONTRACT.md`, `validation/importer-threat-results.json` | read; JSON counted by script |
| `x3d.loom@162ab18` | `PHYSICS-PLAYBOOK.md` (patterns 1 to 19, sections 4 to 9), `LOOM-v1.md` (law 44, failure modes 148 to 160, ids verified by line) | read |
| `x3d.loom@162ab18` | `kit/loomkit/physics.py`, `kit/loom`, `kit/tests/test_gates.py`, `x3d.physics/tools/physx_controls.py`, `x3d.physics/runs/*.physics.json` | run (D-PHY-8) |
| `x3d.demo@d10b457` | `docs/demos/ten-minute-physics/v1` to `v6` (file lists, v6 receipt, grep) | read and counted |
| `x3d.docs@f172f67` | `docs/x3d.loom/MASTERCLASS.md` | linked only |

Read on 2026-11-14. Private memory notes on the port programme and on the Loom fold-back were used only as leads and none of their content was needed; every figure above comes from a repository file, a recorded receipt cited by path, or a run this session. Not used: the project-file screenshots of the ports (images are not copied), and anything on unpublished lab material. The ports' upstream method descriptions belong to Matthias Müller (Ten Minute Physics); this chapter reproduces no upstream code.

See also: [17 Pluggable physics engines](17-physics-engines.md) (Rapier, cannon-es and the built-in solver behind RigidBodyCollection, measured against X_ITE 16.6.0).

Siblings: [01 The tether](01-the-tether.md), [02 Loom laws](02-loom-laws.md), [03 Validator and gates](03-validator-and-gates.md), [06 XITE, the oracle](06-xite-the-oracle.md), [10 Blender pipeline](10-blender-pipeline.md).
