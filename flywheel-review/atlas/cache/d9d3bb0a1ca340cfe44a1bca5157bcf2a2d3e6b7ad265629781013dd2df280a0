# 17. Pluggable physics engines behind RigidBodyPhysics: Rapier, cannon-es and the built-in solver

> **Say it:** The same RigidBodyPhysics file can be stepped by four engines, and the only way to tell them apart is to run each against a closed-form answer, a repeat, a second host and a sensor that must fire; the winner differs per question, and two of the engines carry defects that only a measurement shows. **[C]**

| field | value |
|---|---|
| chapter code | `ENG` |
| prerequisites | [13 Physics in X3D](13-physics.md) (sections 8 and 9), [08 The Babylon bridge](08-babylon-bridge.md) |
| after this you can | plug a second engine into the bridge's RigidBodyCollection without editing a bridge file; name what each engine gets right and wrong on seven analytic scenes; say why a CollisionSensor can miss an impact and the one-line fix; spot the cannon-es friction unit defect and the built-in Cone gap; reproduce every number with four commands |
| sources read | `x3d.loom@56340c2:x3d.physics/rigid-engines/{README.md,src/*.js,lib/*.js,tools/*.js,test/engines.test.js,results/*.json,fixtures/index.json}`; `x3d.loom@1e884b6:x3d.webgpu/bridge/src/nodes/RigidBodyCollection.js`; `x3d.docs@acd4e25:docs/learn/13-physics.md` sections 9.3 and 9.5; X_ITE 16.6.0 `RigidBodyPhysicsComponent` (read) |
| instruments used | Chromium 153.0.8010.12 (SwiftShader build), Node v22.23.4, X_ITE 16.6.0 (Ammo / Bullet), Rapier 0.21.0 (`@dimforge/rapier3d-compat`, WASM), cannon-es 0.20.0, three r187 (bridge host, not stepped here); every run 2026-11-15, software only, no GPU timing |

Chapter 13 section 9 showed that the Babylon bridge carries a small engine of its own and that X_ITE's Bullet has behaviours the spec does not state. This chapter asks the next question: what if the engine is not ours? The x3d.loom adapter `x3d.physics/rigid-engines` replaces one function of the bridge, `BR.phys.tick`, from its own file and hands every fixed 1/240 s sub-step to Rapier or cannon-es. No bridge source is edited; switching back to `'builtin'` restores the original behaviour. The measurements below are the evidence for choosing, or not choosing, either library.

---

## 1. The map

```text
 X3D 4.0 file (no script)           bridge reader (shared, unchanged)
  RigidBodyCollection  ----------->  BR.phys.build(n): bodies, shapes, joints, sensors
  RigidBody / CollidableShape                    |
  joints, CollisionSensor                        v
                                  engines.js  BR.phys.tick (replaced; original kept as builtinTick)
                                   fixed 1/240 s slices, clock accumulator, catch-up cap 0.5 s
                                                 |
              +---------------+------------------+---------------+
              v               v                  v               v
          'builtin'        'rapier'           'cannon'       'cannon-raw'
          sequential       WASM, soft         Gauss-Seidel   same, stock friction
          impulses         contacts, PGS      + friction     (kept for comparison)
              |               |                  |               |
              +---------------+---- B.x B.q B.v B.w + contacts() ---+
                                                 |
                       events on RigidBody (position, orientation, velocities)
                       CollisionSensor reads contacts: 'last' sub-step or 'frame' (whole tick)
```

| question | answer in this chapter | where |
|---|---|---|
| does the engine match a closed form? | seven analytic scenes, four engines, plus X_ITE | section 3 |
| is a run repeatable, and the same on another host? | 21 runs, bit-level | section 4 |
| what does it cost? | wall ms per sub-step, 25 to 250 bodies | section 5 |
| does a sensor see the hit? | 24 drop heights, six configurations | section 6 |
| chains, limits, joints | cradle, door, cart | section 7 |
| two defects found | cannon-es friction unit, built-in Cone | section 8 |
| which engine for which job | decision table | section 9 |

In scope: the adapter, its measurements, the decision. Out of scope: PhysX and MuJoCo (chapter 13), rendering (the replays on the demo page are script-free interpolators), GPU timing (none is claimed).

Read next: deeper, [13 Physics in X3D](13-physics.md) section 9 (what X_ITE's Bullet does); wider, [08 The Babylon bridge](08-babylon-bridge.md).

---

## 2. The adapter contract

An engine is a factory registered with `BR.physEngines.register(name, engine)`. Selection is `BR.physEngines.use('rapier', { contactMode: 'frame' })`; the engine libraries arrive through `window.__physLibs = { RAPIER, CANNON }` and either is optional.

| part | contract | why it matters |
|---|---|---|
| `create(ctx)` | receives bodies (exact shapes, mass, principal inertia), joints, gravity, friction, bounce, `notes`; returns `{ step(h), pushFrom(B), contacts(), setGravity(g), jointState(J), dispose() }` | one description of the scene for every engine |
| unsupported node type | pushed to `ctx.notes` and shown in `BR.physEngines.notes` | a lossy mapping of a whole node is visible (single fields are not) |
| mass and inertia | principal inertia from the shapes (`E.util.inertiaOf`, Jacobi eigen decomposition); Rapier gets it as additional mass properties at the body origin with every collider density 0 | the body origin is the centre of mass, as in X_ITE's Bullet and the built-in engine |
| step | fixed `H = 1/240 s`; the tick accumulates the clock and runs as many slices as fit | pacing independence, section 4 |
| contacts | `{ a, b, n, p, depth, ga, gb, ba, bb }` per sub-step; `contactMode: 'last'` keeps the last sub-step (original behaviour), `'frame'` merges the whole tick | CollisionSensor, section 6 |
| output | position, orientation, velocities raised as events on each moving RigidBody; joint outputs follow `forceOutput` | a ROUTE to a Transform works with any engine |

Joint coverage: BallJoint, SingleAxisHingeJoint with limits and SliderJoint with limits are exercised by the tests and scenes; MotorJoint torque, UniversalJoint and DoubleAxisHingeJoint are mapped in code but not tested (Rapier locks the twist only, angle limits and motors are listed in `notes`). Fields are not all mapped: `stopBounce`, `stopErrorCorrection` and motor angle targets are read by the built-in engine only and no note says so. Shapes: Box, Sphere, Cylinder and Cone natively in Rapier; cannon-es takes Cylinder and Cone as a 12-segment `Cylinder`.

---

## 3. Fidelity against closed forms

Seven plain X3D 4.0 scenes (`fixtures/`), each with an analytic answer, run through the same reader in Node. X_ITE 16.6.0 ran the same text in Chromium 153 (two loads each).

| scene (analytic answer) | built-in | Rapier | cannon-es | cannon-es raw | X_ITE 16.6.0 (load 1 / load 2) |
|---|---|---|---|---|---|
| drop, bounce 0.5: apex above contact (1.125 m) | 1.125 | 1.121 | 1.235 | 1.235 | 0.784 / 0.522 |
| three-box stack: top box height (2.5 m) | 2.490 | 2.498 | 2.500 | 2.500 | 2.500 / 2.500 |
| slope, mu 0.2: acceleration (3.19 m/s2) | 3.20 | 3.20 | 3.43 | 0 | 4.09 / 4.50 |
| pendulum: period error against the physical-pendulum formula | 0.27 % | 0.19 % | 0.44 % | 0.44 % | 1.56 % / 5.83 % |
| hinge, limit 1.0 rad: max angle | 1.000 | 1.000 | 1.008 | 1.008 | 3.121 / 3.132 |
| slider, limit 1.5 m: max separation | 1.500 | 1.500 | 1.505 | 1.505 | 1.500 / 1.499 |
| elastic head-on hit: energy error | 0.39 % | 0.38 % | 14.02 % | 14.02 % | 9.55 % / 3.06 % |

Reading it: Rapier is within 0.4 % of every closed form here. The built-in engine is as good except for a stack that sits 8.7 mm low at the middle box and 10 mm at the top (0.4 % of the top height) and limits that relax after impact (hinge 0.714 rad and slider 1.424 m at 3 s, against 1.000 and 1.500 held by Rapier; cannon-es falls back further, to 0.445 rad and 0.502 m). cannon-es adds energy (+14.0 % on an elastic hit, +10 % on the bounce apex). X_ITE 16.6.0 ignores the hinge limit and does not repeat. **[C]** (instruments: `x3d.loom@56340c2` `tools/fidelity-node.js`, `tools/fidelity-xite.js`; rig above.)

The column "cannon-es raw" is the stock library: the cube does not move at all (acceleration 0) on a ramp where 3.19 m/s2 is right. Section 8 explains it.

---

## 4. Determinism

| check | built-in | Rapier | cannon-es | scenes |
|---|---|---|---|---|
| two runs, one process, whole trace identical | 7 of 7 | 7 of 7 | 7 of 7 | 7 analytic |
| 60 Hz ticks against a 40 ms / 8.3 ms jitter pattern, final state identical | 7 of 7 | 7 of 7 | 7 of 7 | same |
| positions identical, Node 22 against Chromium 153 | 7 of 7 | 7 of 7 | 7 of 7 | same |
| whole trace including orientation identical across hosts | 3 of 7 | 3 of 7 | 3 of 7 | same |

The 12 whole-trace mismatches differ by at most 1.1e-16 in the axis-angle orientation (acos and atan2 rounding in two V8 builds); positions differ by 0 m in all 21 runs. The fixed 1/240 s grid is why pacing does not matter. X_ITE does not have this property: its Bullet step is `1 / max(10, fps)` smoothed over 15 frames, so two loads of the drop scene gave apexes of 0.784 m and 0.522 m (section 3). **[C]** (`tools/determinism.js`; hash of float64 bits per sample.)

```text
 frame ticks:   |--16.7--|--16.7--|--16.7--|        regular 60 Hz
                |-----40-----|-8-|-----40-----|-8-|   jitter pattern
 engine slices: |.|.|.|.|.|.|.|.|.|.|.|.|.|.|        always 1/240 s, same count per sim second
                same slices  ->  same bits at every common sim time
```

---

## 5. Cost

Pile of N bodies (half spheres, half boxes) on a floor, 720 sub-steps of 1/240 s, best of 3, wall milliseconds per sub-step.

| N | built-in, Chromium | Rapier, Chromium | cannon-es, Chromium | built-in, Node | Rapier, Node | cannon-es, Node |
|---|---|---|---|---|---|---|
| 25 | 0.387 | 0.462 | 0.313 | 1.361 | 0.187 | 0.361 |
| 100 | 1.883 | 0.842 | 0.733 | 4.748 | 0.543 | 0.755 |
| 250 | 3.966 | 1.642 | 2.142 | 15.989 | 1.593 | 2.574 |

The bridge runs in a browser, so the Chromium columns are the ones to read; Node's V8 inflates the pure-JavaScript built-in engine by 4x at 250 bodies. At 250 bodies Rapier is 2.4x and cannon-es 1.9x faster than the built-in engine in Chromium; at 25 bodies the built-in engine is faster than Rapier (0.387 against 0.462 ms). **[C]** (`tools/speed.js`; one machine, no GPU involved.)

---

## 6. The CollisionSensor impact lottery

A bouncy sphere (bounce 0.9, never at rest) is dropped from 24 heights 13.7 mm apart, so the first impact lands on a different 1/240 s sub-step each time. Count the drops where the sensor's `isActive` rises during the first impact.

| configuration | impacts seen, of 24 |
|---|---|
| X_ITE 16.6.0 | 4 |
| built-in, `last` | 6 |
| cannon-es, `last` | 5 |
| Rapier, `last` | 11 |
| **Rapier, `frame`** | **24** |
| **cannon-es, `frame`** | **24** |

Cause: in `last` mode the sensor reads the contacts of the final sub-step of a tick, and a bouncing ball is in contact on one sub-step only; the impact falls in an earlier one in most ticks. `frame` merges the contacts of every sub-step in the tick. Rapier's contacts are speculative (a fast body is stopped by a contact still `dist` away; in 2 of 4 probed drops the impact step had dist +0.011 and +0.009 m), so a manifold counts when a point touches or the solver pushed on it in that step (`contactImpulse > 0`). Rapier also keeps a manifold for a few steps after the ball leaves, so its `last` count (11 of 24) includes stale contacts and is not comparable with the other `last` rows; `frame` mode asks only whether a contact happened in the tick. **[C]** (`tools/sensor-impact.js`; sampled as a page would hear it, a rising `isActive` after each tick.)

---

## 7. Chains and limits: three scenes

| scene | measure | built-in | Rapier | cannon-es |
|---|---|---|---|---|
| Newton's cradle, first ball lifted 0.71 m, bounce 1 | last ball peak rise (m) | 0.62 | 0.22 with 1 sub-step, **0.65 with 4** | 1.78 |
| same | first ball range over 8 s (m) | 0.71 | 0.71 | 2.11 |
| gate: door spun at 3.2 rad/s into a stop at 1.1 rad | door max angle (rad) | 1.11 | 1.10 | 1.10 |
| gate: cart thrown into a slider limit at 3.70 m (it starts at 0.90 m) | max separation (m) | 3.70 | 3.70 | 3.71 |
| avalanche: 40 bodies, 10 each sphere, box, cylinder, cone, into a funnel | bodies out of the funnel | **10** (all cones) | 0 | 0 |

The cradle is the hard case. The rises are measured **[C]**. Rapier with 1, 2 and 3 sub-steps gives 0.22, 0.21 and 0.22 m and with 4 and 8 gives 0.65 and 0.64 m; solver iterations 10 to 20, `numInternalPgsIterations` 1 to 8 and `contact_natural_frequency` 60 to 960 left it at 0.22 m (an ad hoc sweep, not committed; solver iterations 1 and 4 do change it). The explanation that Rapier's contact solver works from the approach speeds at the start of a step, so an impulse cannot hop through four contacts inside one step, is a hypothesis consistent with that pattern and was not isolated **[S]**; the cannon-es excess is measured (1.78 m for a 0.71 m lift, 2.5 times the energy), but +14 % per elastic hit would compound to about 1.7 times over four contacts, so the per-contact figure alone does not explain it **[S]**. Gate numbers: the cart reaches 3.70 m in the built-in and Rapier recordings and 3.71 m in cannon-es, at the slider limit, with the red block placed just beyond it. (`lib/demo-scenes.js`, `tools/record-demo.js`; Node v22.23.4; the replays are on the demo page `x3d.demo` `docs/demos/rigid-engines/v1/`, where X_ITE's Bullet runs live beside them.)

---

## 8. Two defects the measurements found

| defect | where | symptom | cause | fix |
|---|---|---|---|---|
| friction in the wrong unit | cannon-es 0.20.0 | a cube does not slip on a ramp at any angle up to its tipping angle whatever mu is (stock sweep: 45 and 45 degrees, where the cube topples, against slip angles of 11.3 and 26.6) | the Gauss-Seidel solver returns an impulse, the friction bound is built as a force, so at 1/240 s it is about 240 times too large (cause read in the cannon-es 0.20.0 source, symptom measured) | the adapter wraps `solver.solve` with `bound = mu * m_reduced * abs(g.n) * dt / points`; patched result 12 and 25 degrees (built-in and Rapier 12 and 27) |
| no collider for Cone | x3d.loom built-in engine (`RigidBodyCollection.js`) | all 10 cones of the avalanche fall through the funnel | the shape finder accepts a geometry that has `size` or `radius`; a Cone has `bottomRadius` and `height`, so it is not found | one condition, `|| 'bottomRadius' in k.f`; reported to the bridge owner, **not edited here** |

```text
 cannon-es friction:     force bound  F <= mu N         impulse solver needs  J <= mu N dt
                          (as built)   240x too big at dt = 1/240 s, and per contact point
                                  |
                                  v   adapter:  bound = mu * m_red * |g.n| * dt / n_points
```

Both were found by comparing a number to its closed form: the ramp acceleration of 0 and the escape count of exactly 10. **[C]** (`tools/friction-sweep.js`; `test/engines.test.js`; `RigidBodyCollection.js` read at `x3d.loom@1e884b6`.)

---

## 9. Which engine for which job

| need | choose | why (measured) |
|---|---|---|
| X_ITE parity | none of them; keep X_ITE's Bullet | Bullet's quirks (frame-rate step, friction product, no hinge limits) are reproduced only by Bullet (chapter 13 section 9) |
| repeatable, explainable, small scenes | built-in | faster than Rapier at 25 bodies in Chromium (0.387 against 0.462 ms; cannon-es is faster still, 0.313 ms); within 0.4 % on the closed forms except a 10 mm stack sag and relaxing limits |
| stacks, many bodies, chains, limits | Rapier (`sub: 4` for chains) | within 0.4 % on all seven scenes and the only engine that holds a hinge and a slider limit after impact; 2.4x faster than built-in at 250 bodies in Chromium |
| lightweight second opinion | cannon-es (patched) | 1.9x faster than built-in at 250 bodies; accept +14 % energy on elastic hits |
| a CollisionSensor that should see an impact | Rapier or cannon-es with `contactMode: 'frame'` | 24 of 24 on this one scene (first impact of one sphere, 60 Hz ticks); not available for the built-in engine, which ignores the mode (6 of 24); no fast or thin bodies tested |

---

## Heuristics

| ID | Rule (imperative, at most 30 words) | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-ENG-1 | Check every engine against a closed form before comparing engines to each other; a mutual match proves only that they share a bias. | [C] | cannon-es +14.0 % energy on an elastic hit, visible only against the analytic 0 % | `x3d.loom@56340c2` `results/fidelity-node.json`; Node v22.23.4 |
| H-ENG-2 | When a library accepts a friction value, run a ramp sweep; a cube that holds until it topples, for every mu, is a unit error, not a surface property. | [C] | cannon-es raw 45 and 45 degrees (the tipping angle) against slip angles 11.3 and 26.6 | `tools/friction-sweep.js`; cannon-es 0.20.0 |
| H-ENG-3 | Count escapees per shape kind in a contained stress scene; an exact count equal to one kind's population is a missing collider. | [C] | 10 escaped, 10 cones | `tools/record-demo.js`, `RigidBodyCollection.js` at `x3d.loom@1e884b6` |
| H-ENG-4 | Let a CollisionSensor read every sub-step of a tick, not the last; test it with many drop heights that land on different sub-steps. | [C] | 24 of 24 in frame mode against 5 to 11 in last mode (Rapier's last count includes stale contacts) | `tools/sensor-impact.js`, `test/engines.test.js`; Node v22.23.4 (X_ITE row: Chromium 153.0.8010.12) |
| H-ENG-5 | Step external engines on the bridge's fixed grid and never on the frame time; then hash the trace under jittered frames to prove it. | [C] | 21 of 21 final states equal under 40 ms / 8.3 ms ticks | `tools/determinism.js` |
| H-ENG-6 | Compare hosts on positions first and on orientation second; axis-angle conversion differs in the last bits between V8 builds. | [C] | 21 of 21 positions identical, 12 of 21 whole traces not, maximum 1.1e-16 | `tools/determinism.js`; Node v22.23.4, Chromium 153 |
| H-ENG-7 | Time engines in the host that will run them; the same code ranks the engines differently in Node and in the browser. | [C] | built-in 15.989 ms in Node, 3.966 ms in Chromium at 250 bodies | `tools/speed.js` |
| H-ENG-8 | Give a stiff chain sub-steps before touching solver iterations; measure the end-of-chain response, not the first contact. | [C] | Rapier cradle 0.22 m with 1 sub-step, 0.65 m with 4, unchanged by 1 to 8 PGS and 10 to 20 iterations | `test/engines.test.js`, Rapier 0.21.0 |
| H-ENG-9 | Set the body origin to the centre of mass and pass principal inertia explicitly when an engine derives its own; otherwise it silently overrides the X3D rule. | [L] | Rapier mass set as additional properties with collider density 0; pendulum period error 0.19 % | `engine-rapier.js` read; `tools/fidelity-node.js` |
| H-ENG-10 | Put every unmapped node type into a visible notes list instead of dropping it, and list ignored fields too; a quiet drop reads as a pass. | [L] | `ctx.notes` lists Universal and DoubleAxis limits and motors, but `stopBounce` is dropped without a note | `engines.js`, `engine-rapier.js` read |
| H-ENG-11 | Restore the original function when switching an adapter off, and keep it callable under another name. | [L] | `builtinTick` kept; `use('builtin')` drops the engine state | `engines.js` read |

---

## Drills

### D-ENG-1 The ramp that sticks
- **Level:** L2
- **Task:** Run the friction sweep and say which of the four engines is wrong at mu 0.2 and mu 0.5, and by how many degrees.
- **Verify:** `cd x3d.physics/rigid-engines && npm install && export NODE_PATH=$PWD/node_modules && node tools/friction-sweep.js`
- **Answer:** `cannon-raw` first moves at 45 degrees in both cases, which is where the unit cube topples (slip angles are 11.3 and 26.6, so it holds 33.7 and 18.4 degrees too long); built-in and Rapier 12 and 27; patched cannon 12 and 25.
- **Checked:** `2026-11-15 x3d.loom@56340c2, Node v22.23.4, cannon-es 0.20.0`: mu 0.5 builtin 27, rapier 27, cannon 25, cannon-raw 45.

### D-ENG-2 Find the escaped cones
- **Level:** L1
- **Task:** In `RigidBodyCollection.js` find the condition that decides which geometry node is used as a collision shape, and say why a Cone does not satisfy it.
- **Verify:** `grep -n "'radius' in k.f" x3d.webgpu/bridge/src/nodes/RigidBodyCollection.js`
- **Answer:** `'size' in k.f || 'radius' in k.f`; a Cone's fields are `bottomRadius` and `height`, so `shapesOf` returns no shape for it. The avalanche scene loses exactly its 10 cones.
- **Checked:** `2026-11-15 x3d.loom@1e884b6`: one match, the condition above.

### D-ENG-3 Make the sensor miss
- **Level:** L3
- **Task:** Run the sensor test, then change `'frame'` to `'last'` in its Rapier loop and count the drops the sensor sees; explain the drop.
- **Verify:** `node --test --test-name-pattern "sensor frame" test/engines.test.js`, then edit the call `seen(eng, 'frame', h)` and run again, or run `node tools/sensor-impact.js`.
- **Answer:** in `frame` mode 24 of 24 for Rapier and cannon-es; in `last` mode Rapier 11 and cannon-es 5 of 24, because only one sub-step of a tick holds the contact.
- **Checked:** `2026-11-15 x3d.loom@56340c2`: the test passes with `frame`; `results/sensor-impact.json` holds 11 and 5 for `last`.

### D-ENG-4 Four sub-steps for a cradle
- **Level:** L2
- **Task:** Run the cradle with Rapier at one and at four sub-steps and report the last ball's rise; state what raising `numSolverIterations` does.
- **Verify:** `node --test --test-name-pattern "rapier sub-steps" test/engines.test.js` (the test asserts under 0.3 m for 1 and 0.55 to 0.75 m for 4).
- **Answer:** 0.22 m with 1, 0.65 m with 4 (built-in 0.62 m); iterations 10 to 20 and PGS 1 to 8 change nothing.
- **Checked:** `2026-11-15 x3d.loom@56340c2, Rapier 0.21.0`: test passes; sweep printed 0.22 for every iteration setting, 0.65 and 0.64 for 4 and 8 sub-steps.

### D-ENG-5 Same bits under jitter
- **Level:** L2
- **Task:** Show that the stack scene ends in the same state at 60 Hz ticks and under a 40 ms / 8.3 ms pattern, for each engine.
- **Verify:** `node --test --test-name-pattern "determinism stack3" test/engines.test.js`
- **Answer:** three passing tests, one per engine: both the repeat hash and the jitter final-state hash are equal.
- **Checked:** `2026-11-15 x3d.loom@56340c2, Node v22.23.4`: 3 of 3 pass.

### D-ENG-6 Rank by host
- **Level:** L1
- **Task:** From `results/speed.json` compute how many times faster Rapier and cannon-es are than the built-in engine at 250 bodies, in Chromium and in Node.
- **Verify:** `python3 -c "import json;d=json.load(open('results/speed.json'))['N250'];print({h:{e:round(d[h]['builtin']/d[h][e],2) for e in ('rapier','cannon')} for h in ('chromium','node')})"`
- **Answer:** Chromium 2.42 and 1.85; Node 10.04 and 6.21. The Node ratios are 3.4 to 4.1 times the Chromium ratios because Node slows only the built-in engine (4.0x at 250 bodies), which is why the host matters.
- **Checked:** `2026-11-15 x3d.loom@56340c2`: Chromium {rapier 2.42, cannon 1.85}.

---

## Honest limits

- **[C] One machine, software GPU.** Every Chromium number is Chromium 153.0.8010.12 on SwiftShader; wall times are CPU times of one machine and are not frame rates. Cross-machine determinism was not tested.
- **[C] Seven small analytic scenes.** The ranking says nothing about large mixed scenes, deep stacks, meshes or fast thin objects; no CCD test was run.
- **[C] The demo scenes were recorded in Node only.** Node against Chromium equality was checked on the seven analytic scenes, not on the avalanche, cradle and gate; each demo recording was run twice in Node and matched bit for bit (`repeat_identical` in `data/stats.json`).
- **[C] Rapier's `last` sensor count is inflated by stale manifolds** and the 11 of 24 is not comparable with the other `last` rows.
- **[L] X_ITE numbers are 16.6.0, two loads each.** Bullet's step follows frame time, so a third load gives a third number; the table shows a range of two.
- **[L] Rapier's cradle result depends on a sub-step count that was chosen by trial.** Four was the first value that worked (eight gave 0.64 m); no study of the cost to other scenes was made.
- **[L] Joint coverage is partial.** Universal and DoubleAxis hinge angle limits and motors are not mapped in Rapier; MotorJoint, UniversalJoint and DoubleAxisHingeJoint are mapped in code but no test or scene exercises them.
- **[S] Why the built-in engine's hinge relaxes** (0.714 rad at 3 s with stopBounce 0) was not investigated; only the measurement is stated.
- **[C] The Cone fix is proposed, not applied or run.** It is a one-condition change in a shared bridge file owned by another thread.
- **[L] Licences.** Rapier is Apache-2.0 and cannon-es MIT as stated by their packages; nothing is vendored in the repository.

---

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-ENG-1 | Drop bounce apex above contact, analytic 1.125 m: built-in, Rapier, cannon-es | 1.125, 1.121, 1.235 m | [C] | Node v22.23.4, Rapier 0.21.0, cannon-es 0.20.0 | `x3d.loom@56340c2:x3d.physics/rigid-engines/results/fidelity-node.json` |
| N-ENG-2 | Same drop in X_ITE 16.6.0, two loads | 0.784 and 0.522 m | [C] | X_ITE 16.6.0, Chromium 153.0.8010.12, SwiftShader | `results/fidelity-xite.json` |
| N-ENG-3 | Elastic head-on hit, energy error: built-in, Rapier, cannon-es, X_ITE | 0.39, 0.38, 14.02, 9.55 / 3.06 % | [C] | same rigs | `fidelity-node.json`, `fidelity-xite.json` |
| N-ENG-4 | Slope mu 0.2, acceleration, analytic 3.19 m/s2: built-in, Rapier, cannon-es, cannon-es raw | 3.20, 3.20, 3.43, 0 | [C] | Node v22.23.4 | `fidelity-node.json` |
| N-ENG-5 | Ramp angle where a unit cube first moves at mu 0.2 and 0.5 (analytic slip 11.3, 26.6): cannon-es raw | 45 and 45 degrees (tipping, not slipping) | [C] | cannon-es 0.20.0 | `results/friction-sweep.json` |
| N-ENG-6 | Same, cannon-es with the adapter patch | 12 and 25 degrees | [C] | cannon-es 0.20.0 plus `engine-cannon.js` | `results/friction-sweep.json` |
| N-ENG-7 | Pendulum period error against the physical-pendulum formula: built-in, Rapier, cannon-es | 0.27, 0.19, 0.44 % | [C] | Node v22.23.4 | `fidelity-node.json` |
| N-ENG-8 | Hinge limit 1.0 rad, max angle: Rapier, X_ITE | 1.000 and 3.121 rad | [C] | Node v22.23.4; X_ITE 16.6.0 | `fidelity-node.json`, `fidelity-xite.json` |
| N-ENG-9 | Runs repeatable bit for bit, and equal under jittered ticks | 21 of 21 and 21 of 21 | [C] | Node v22.23.4 | `results/determinism.json` |
| N-ENG-10 | Position difference Node against Chromium; whole-trace matches; max orientation difference | 0 m in 21 of 21; 9 of 21; 1.1e-16 | [C] | Node v22.23.4, Chromium 153.0.8010.12 | `results/determinism.json` |
| N-ENG-11 | Wall ms per 1/240 s step at 250 bodies, Chromium: built-in, Rapier, cannon-es | 3.966, 1.642, 2.142 | [C] | Chromium 153.0.8010.12 SwiftShader, best of 3 | `results/speed.json` |
| N-ENG-12 | Same at 25 bodies, Chromium | 0.387, 0.462, 0.313 | [C] | same | `results/speed.json` |
| N-ENG-13 | Same at 250 bodies, Node | 15.989, 1.593, 2.574 | [C] | Node v22.23.4 | `results/speed.json` |
| N-ENG-14 | CollisionSensor first impact seen of 24 drops: X_ITE, built-in last, Rapier last, cannon-es last | 4, 6, 11, 5 | [C] | Chromium 153 / Node v22.23.4 | `results/sensor-impact.json` |
| N-ENG-15 | Same in frame mode: Rapier and cannon-es | 24 and 24 | [C] | Node v22.23.4 | `results/sensor-impact.json`, `test/engines.test.js` |
| N-ENG-16 | Cradle, last ball peak rise for a 0.71 m lift: built-in, Rapier 1 sub-step, Rapier 4 sub-steps, cannon-es | 0.62, 0.22, 0.65, 1.78 m | [C] | Node v22.23.4, Rapier 0.21.0 | `data/stats.json` of `x3d.demo` demo `rigid-engines/v1` (fields `last_ball_peak_rise_m`, `last_ball_peak_rise_m_1_sub_step`) |
| N-ENG-17 | Avalanche, 40 bodies, bodies out of the funnel: built-in, Rapier, cannon-es | 10, 0, 0 | [C] | Node v22.23.4 | `data/stats.json` |

---

## Sources and provenance

| repo@sha | path | read how |
|---|---|---|
| `x3d.loom@56340c2` | `x3d.physics/rigid-engines/` (README, `src/`, `lib/`, `tools/`, `test/engines.test.js`, `results/*.json`, `fixtures/`) | run: 32 tests, tools listed in the README |
| `x3d.loom@1e884b6` | `x3d.webgpu/bridge/src/nodes/RigidBodyCollection.js` (shape finder, built-in engine) | read |
| `x3d.docs@acd4e25` | `docs/learn/13-physics.md` sections 9.3 and 9.5 (X_ITE Bullet behaviours H-PHY-16 to 24) | read; this chapter's measurements corroborate the frame-rate step and the missing hinge limit |
| `x3d.demo` branch `claude/project-thread-c4iymr` | `docs/demos/rigid-engines/v1/` (replays, `data/stats.json`, live X_ITE pane) | built and checked in headless Chromium |

Read and run on 2026-11-15. The engines are third-party libraries (Rapier by Dimforge, Apache-2.0; cannon-es, MIT); the adapter, tests and fixtures are own code. Nothing from private notes was used.

Siblings: [13 Physics in X3D](13-physics.md), [08 The Babylon bridge](08-babylon-bridge.md), [06 XITE, the oracle](06-xite-the-oracle.md), [14 Methods](14-methods.md).
