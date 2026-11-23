# The Loom frontier board

Assayed 64 frontiers against the AI Engineering Atlas rev 28 (`b8717094e21e`), registry `bb718da97d9b`, tool `24a629bfa9f7`, Python 3.13.18, 0 model calls, $0. Judged scores and ranks are graded Suspected (one model's opinion); the check counts are computed.

Score = 100 x weighted mean of the five judged axes (effort inverted) x (0.7 + 0.3 x readiness). Rank range = 5th to 95th percentile over 2000 seeded perturbations (seed 7).

| # | Frontier | Fam | State | Rel | Fly | Grav | Vis | Eff | Ready | Worst | Score | Rank range | In top 10 |
|--:|---|:-:|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|--:|:-:|--:|
| 1 | **x3d.xray: binaries, code and captures as cities** (`xray`) | D | explored | 5 | 4 | 4 | 5 | 2 | 8/8 | pass | 88.0 | 1 to 21 | 81% |
| 2 | **Cross-engine differential rendering as the oracle** (`cross-render`) | A | touched | 5 | 5 | 4 | 4 | 3 | 8/8 | pass | 87.0 | 1 to 24 | 73% |
| 3 | **BIM and construction through IfcOpenShell** (`bim-ifc`) | D | unexplored | 5 | 5 | 5 | 4 | 3 | 7/8 | warn | 86.6 | 1 to 23 | 72% |
| 4 | **OpenUSD conformance bridge** (`openusd`) | D | touched | 5 | 5 | 5 | 3 | 3 | 8/8 | pass | 86.0 | 1 to 27 | 64% |
| 5 | **Quality-diversity evolution of X3D scenes (MAP-Elites, novelty search)** (`qd-evolve`) | A | unexplored | 5 | 5 | 4 | 5 | 3 | 8/10 | warn | 85.5 | 2 to 25 | 61% |
| 6 | **STEM, maths and PolyXandria** (`stem-maths`) | D | deep | 4 | 4 | 4 | 5 | 2 | 8/8 | pass | 84.0 | 1 to 28 | 62% |
| 7 | **Prompt injection through 3D files: Metadata, WorldInfo, Script, Anchor and Inline as attack channels** (`x3d-injection`) | S | unexplored | 5 | 4 | 5 | 3 | 2 | 8/8 | pass | 83.0 | 1 to 33 | 53% |
| 8 | **A public scoreboard of models on Loom tasks** (`x3d-bench`) | E | unexplored | 5 | 5 | 5 | 3 | 3 | 7/8 | gate | 82.8 | 3 to 33 | 39% |
| 9 | **The hostile-file corpus against every reader, not only Blender** (`hostile-all`) | S | explored | 5 | 5 | 4 | 2 | 2 | 8/8 | pass | 82.0 | 3 to 35 | 38% |
| 10 | **Physics engines (PhysX, MuJoCo, Rapier; next Jolt and Bullet)** (`physics`) | D | deep | 4 | 4 | 4 | 5 | 3 | 8/8 | pass | 81.0 | 1 to 36 | 42% |
| 11 | **Generative shader art behind a compile-and-render guard (GLSL, WGSL)** (`shader-art`) | G | explored | 4 | 4 | 3 | 5 | 2 | 8/8 | pass | 81.0 | 1 to 36 | 42% |
| 12 | **Cultural heritage with CIDOC-CRM (Shroud, Giza)** (`heritage`) | D | explored | 4 | 4 | 5 | 5 | 3 | 7/8 | warn | 80.8 | 2 to 36 | 38% |
| 13 | **Molecules and proteins (zinc fingers reborn)** (`molecules`) | D | deep | 4 | 4 | 5 | 5 | 3 | 7/8 | warn | 80.8 | 2 to 36 | 36% |
| 14 | **Robotics: URDF, MJCF and ROS bags** (`robotics`) | D | touched | 4 | 4 | 5 | 5 | 3 | 7/8 | warn | 80.8 | 2 to 36 | 38% |
| 15 | **Retrieval over the Loom: the right law and failure mode on the page before the first line is written** (`rag-loom`) | E | unexplored | 5 | 5 | 3 | 2 | 2 | 8/8 | pass | 79.0 | 5 to 42 | 19% |
| 16 | **Text to X3D with the validator in the loop (repair from refusal codes)** (`text2x3d-loop`) | G | explored | 5 | 5 | 4 | 3 | 2 | 7/10 | gate | 78.3 | 7 to 40 | 14% |
| 17 | **The Loom as an MCP server: laws, failure modes and r2r check as tools any agent can call** (`mcp-loom`) | E | touched | 5 | 5 | 4 | 1 | 2 | 8/8 | pass | 78.0 | 5 to 41 | 19% |
| 18 | **Red-team the Loom's own graders: mutation-test every witness** (`mutate-graders`) | S | explored | 5 | 5 | 4 | 1 | 2 | 8/8 | pass | 78.0 | 6 to 41 | 17% |
| 19 | **Terrain and geospatial (Giza, Accrete, 3D Tiles, CityGML)** (`geospatial`) | D | explored | 4 | 4 | 5 | 5 | 4 | 7/8 | warn | 78.0 | 4 to 43 | 21% |
| 20 | **Motion capture to H-Anim (BVH, retargeting)** (`mocap-hanim`) | D | touched | 4 | 4 | 4 | 5 | 3 | 7/8 | warn | 78.0 | 3 to 41 | 24% |
| 21 | **Grammar-constrained decoding: compile the X3D schema into a grammar so a small model cannot emit an invalid scene** (`grammar-decode`) | G | unexplored | 5 | 4 | 5 | 2 | 3 | 8/8 | pass | 76.0 | 6 to 47 | 15% |
| 22 | **The token economy of X3D: which encoding can a model afford** (`token-economy`) | E | unexplored | 5 | 4 | 3 | 2 | 1 | 8/8 | pass | 76.0 | 6 to 47 | 14% |
| 23 | **Interactive evolution: you breed scenes by eye and your picks become the judge's labels** (`breed-judge`) | G | unexplored | 4 | 5 | 3 | 5 | 2 | 5/9 | gate | 75.4 | 11 to 44 | 4% |
| 24 | **Fields and flows: VTK, NetCDF climate, CFD** (`sci-fields`) | D | touched | 4 | 3 | 5 | 5 | 3 | 7/8 | warn | 75.1 | 8 to 48 | 8% |
| 25 | **Coverage-guided fuzzing of every X3D reader (Atheris, cargo-fuzz)** (`coverage-fuzz`) | A | explored | 5 | 5 | 3 | 1 | 2 | 8/8 | pass | 75.0 | 10 to 46 | 7% |
| 26 | **Shape grammars and L-systems as scene programs** (`grammar-gen`) | A | touched | 4 | 3 | 3 | 5 | 2 | 8/8 | pass | 75.0 | 6 to 48 | 14% |
| 27 | **Image and text to 3D models (TRELLIS, Hunyuan3D, TripoSR class) into X3D with receipts** (`image-to-3d`) | G | unexplored | 4 | 4 | 4 | 5 | 3 | 6/8 | gate | 74.9 | 7 to 46 | 12% |
| 28 | **Active experiment design: the r2r needs list picks the next run (bandits, expected information gain)** (`active-design`) | A | touched | 5 | 5 | 3 | 2 | 2 | 8/10 | warn | 74.3 | 12 to 49 | 3% |
| 29 | **X3D as a synthetic-data factory for vision models** (`synth-vision`) | E | unexplored | 4 | 3 | 5 | 4 | 3 | 8/8 | pass | 74.0 | 7 to 49 | 11% |
| 30 | **Canonical form for X3D (equality saturation: one scene, one spelling)** (`canon-egraph`) | A | unexplored | 5 | 4 | 4 | 2 | 3 | 8/8 | pass | 73.0 | 9 to 51 | 7% |
| 31 | **Geometry-processing witnesses (manifold, Euler characteristic, self-intersection)** (`geom-witness`) | A | touched | 4 | 4 | 3 | 3 | 2 | 8/8 | pass | 73.0 | 6 to 51 | 12% |
| 32 | **Medical volumes (DICOM, NIfTI) in X3D volume rendering** (`dicom-volume`) | D | touched | 4 | 3 | 5 | 5 | 4 | 7/8 | warn | 72.2 | 11 to 52 | 4% |
| 33 | **Gaussian splats and radiance fields into X3D 4.1** (`splat-x3d`) | G | explored | 4 | 3 | 4 | 5 | 3 | 7/8 | warn | 72.2 | 10 to 51 | 5% |
| 34 | **CAD: STEP and B-rep through OpenCascade** (`cad-step`) | D | unexplored | 4 | 4 | 5 | 4 | 4 | 6/8 | warn | 71.2 | 13 to 52 | 3% |
| 35 | **Particle collisions** (`collider`) | D | explored | 3 | 3 | 4 | 5 | 2 | 7/8 | warn | 71.2 | 12 to 52 | 4% |
| 36 | **Sky and ephemerides** (`sky`) | D | explored | 3 | 3 | 4 | 5 | 2 | 7/8 | warn | 71.2 | 11 to 53 | 4% |
| 37 | **Implicit fields and cellular automata to mesh (SDF, marching cubes, reaction-diffusion)** (`implicit-ca`) | A | touched | 3 | 3 | 3 | 5 | 2 | 8/8 | pass | 71.0 | 12 to 53 | 4% |
| 38 | **Signed provenance for 3D: from hash chain to signature** (`c2pa-3d`) | E | touched | 5 | 3 | 5 | 2 | 3 | 8/8 | pass | 70.0 | 16 to 56 | 1% |
| 39 | **LiDAR and point clouds (LAS, E57, photogrammetry)** (`point-clouds`) | D | unexplored | 4 | 3 | 4 | 5 | 3 | 6/8 | warn | 69.4 | 17 to 54 | 1% |
| 40 | **Unreal 5 bridge** (`unreal`) | D | touched | 4 | 4 | 4 | 5 | 5 | 6/8 | warn | 69.4 | 16 to 53 | 1% |
| 41 | **Solver-checked laws: prove the 44 laws and the r2r rules do not contradict** (`smt-laws`) | A | touched | 4 | 4 | 4 | 2 | 3 | 8/8 | pass | 69.0 | 12 to 55 | 3% |
| 42 | **Brain and connectome** (`brain`) | D | touched | 3 | 3 | 4 | 5 | 3 | 7/8 | warn | 68.3 | 16 to 56 | 1% |
| 43 | **Live digital twins: sensor streams and time series into a scene** (`live-twins`) | D | touched | 4 | 3 | 4 | 4 | 3 | 7/8 | warn | 68.3 | 15 to 56 | 2% |
| 44 | **Games as deterministic proofs (chess, platformer, drift)** (`games`) | D | deep | 3 | 3 | 2 | 5 | 2 | 8/8 | pass | 68.0 | 18 to 57 | 1% |
| 45 | **Procedural worlds: wave function collapse, noise terrain, erosion, cities** (`proc-worlds`) | G | touched | 3 | 3 | 3 | 5 | 3 | 8/8 | pass | 68.0 | 18 to 57 | 1% |
| 46 | **Knowledge graphs and hypergraphs in 3D** (`graphs-3d`) | D | explored | 3 | 3 | 3 | 4 | 2 | 8/8 | pass | 67.0 | 16 to 57 | 2% |
| 47 | **Music and time** (`music`) | D | explored | 3 | 3 | 3 | 4 | 2 | 8/8 | pass | 67.0 | 16 to 57 | 2% |
| 48 | **Ontology reasoning over scenes (OWL, SHACL)** (`onto-reason`) | E | explored | 4 | 3 | 4 | 3 | 3 | 8/8 | pass | 67.0 | 16 to 57 | 1% |
| 49 | **Fine-tune a small open model on validator-labelled Loom data** (`finetune`) | E | touched | 4 | 5 | 5 | 2 | 5 | 6/8 | gate | 66.6 | 27 to 56 | 0% |
| 50 | **Scene embeddings and graph networks: similarity, dedupe and a map of every scene** (`scene-embed`) | E | unexplored | 3 | 3 | 3 | 4 | 3 | 8/8 | pass | 64.0 | 23 to 59 | 0% |
| 51 | **Audio-reactive generative scenes** (`audio-reactive`) | G | explored | 3 | 2 | 2 | 5 | 2 | 8/8 | pass | 62.0 | 31 to 61 | 0% |
| 52 | **Stigmergic builders: simple agents weaving a scene by local rules** (`stigmergy`) | A | unexplored | 3 | 2 | 2 | 5 | 2 | 8/8 | pass | 62.0 | 33 to 62 | 0% |
| 53 | **Receipts as traces: one span per witness, one trace per run** (`trace-receipts`) | E | unexplored | 3 | 4 | 2 | 2 | 2 | 8/8 | pass | 62.0 | 27 to 61 | 0% |
| 54 | **Fabrication: 3MF and STL printability** (`fabrication`) | D | unexplored | 3 | 3 | 3 | 3 | 2 | 7/8 | note | 60.6 | 32 to 62 | 0% |
| 55 | **DSPy and GEPA optimisation of the rule proposer** (`dspy-gepa`) | E | touched | 4 | 4 | 3 | 1 | 2 | 7/10 | gate | 59.1 | 35 to 61 | 0% |
| 56 | **Does agent memory help? The on/off trial with a real model** (`memory-trial`) | E | touched | 4 | 4 | 3 | 1 | 2 | 7/10 | gate | 59.1 | 35 to 61 | 0% |
| 57 | **A picture judge calibrated against your eye** (`picture-judge`) | E | unexplored | 4 | 4 | 3 | 3 | 3 | 4/9 | gate | 58.3 | 41 to 62 | 0% |
| 58 | **X3D worlds as reinforcement-learning environments** (`rl-gym`) | E | unexplored | 3 | 3 | 4 | 4 | 4 | 7/10 | stop | 58.2 | 39 to 62 | 0% |
| 59 | **WebXR and headsets** (`xr-headset`) | D | touched | 3 | 2 | 3 | 5 | 3 | 5/9 | gate | 53.7 | 50 to 64 | 0% |
| 60 | **Video and world models to X3D (the 8-second stage)** (`video-world`) | G | touched | 3 | 3 | 4 | 5 | 5 | 3/9 | stop | 52.0 | 53 to 64 | 0% |
| 61 | **Topological data analysis of scene corpora (persistent homology)** (`tda-corpus`) | A | unexplored | 2 | 2 | 3 | 4 | 3 | 7/8 | note | 52.0 | 49 to 64 | 0% |
| 62 | **Builder, breaker and referee: a small swarm arguing over one scene** (`agent-swarm`) | E | unexplored | 3 | 3 | 3 | 3 | 3 | 6/11 | stop | 51.8 | 52 to 64 | 0% |
| 63 | **Generated PBR materials and textures** (`material-gen`) | G | unexplored | 3 | 2 | 2 | 4 | 3 | 6/8 | gate | 50.9 | 51 to 64 | 0% |
| 64 | **Script and language geometry (Mashtots)** (`language`) | D | touched | 2 | 2 | 4 | 4 | 3 | 4/9 | gate | 47.5 | 56 to 64 | 0% |

## Gates before starting

- **x3d-bench** (rank 8): T11: the first step needs a paid or GPU model call: his typed spend OK first
- **text2x3d-loop** (rank 16): T11: the first step needs a paid or GPU model call: his typed spend OK first
- **breed-judge** (rank 23): T3: outcome is a human opinion: record it as labels, never as a grade; T5: measure Cohen's kappa and a position swap against about 30 of his labels before it grades anything (Atlas sketch K6)
- **image-to-3d** (rank 27): T11: the first step needs a paid or GPU model call: his typed spend OK first
- **finetune** (rank 49): T11: the first step needs a paid or GPU model call: his typed spend OK first
- **dspy-gepa** (rank 55): T11: the first step needs a paid or GPU model call: his typed spend OK first
- **memory-trial** (rank 56): T11: the first step needs a paid or GPU model call: his typed spend OK first
- **picture-judge** (rank 57): T3: outcome is a model opinion: record it as labels, never as a grade; T5: measure Cohen's kappa and a position swap against about 30 of his labels before it grades anything (Atlas sketch K6); T11: the first step needs a paid or GPU model call: his typed spend OK first
- **rl-gym** (rank 58): T8: an optimiser faces a grader with no controls or no hold-out: it will learn the grader, not the task
- **xr-headset** (rank 59): T3: outcome is a human opinion: record it as labels, never as a grade; T5: measure Cohen's kappa and a position swap against about 30 of his labels before it grades anything (Atlas sketch K6)
- **video-world** (rank 60): T3: outcome is a model opinion: record it as labels, never as a grade; T5: measure Cohen's kappa and a position swap against about 30 of his labels before it grades anything (Atlas sketch K6); T7: restricted outside data or licence: needs his decision before any byte is fetched; T11: the first step needs a paid or GPU model call: his typed spend OK first
- **agent-swarm** (rank 62): T8: an optimiser faces a grader with no controls or no hold-out: it will learn the grader, not the task; T11: the first step needs a paid or GPU model call: his typed spend OK first
- **material-gen** (rank 63): T11: the first step needs a paid or GPU model call: his typed spend OK first
- **language** (rank 64): T3: outcome is a human opinion: record it as labels, never as a grade; T5: measure Cohen's kappa and a position swap against about 30 of his labels before it grades anything (Atlas sketch K6)

## First steps, top 15

1. **x3d.xray: binaries, code and captures as cities**. Makes anything with structure a scene. New readers (pcap, MCAP) just landed in the validator fork. *First step:* A packet capture as a city with every tower traceable to its bytes. *Grader:* hypothesis ledger re-run as code against the native binary.
2. **Cross-engine differential rendering as the oracle**. Six renderers vote on every scene; a lone dissenter is a bug report with a picture, and agreement is evidence no single engine can give. *First step:* Render the 30 conformance scenes in 3 engines with a fixed rig; publish the disagreement matrix and the 5 largest pixel gaps. *Grader:* X_ITE, three.js, Babylon, Castle, x3d.wgpu and Blender pixel difference.
3. **BIM and construction through IfcOpenShell**. The richest typed 3D data on Earth, with its own rule language (IDS). The Loom meets a peer validator and a paying industry. *First step:* One open sample building: IFC to X3D with a loss receipt; 10 quantities (areas, volumes, counts) against IfcOpenShell. *Grader:* IfcOpenShell geometry + buildingSMART IDS checks.
4. **OpenUSD conformance bridge**. USD is where the industry's money is. A measured, two-way loss table between X3D and USD is the document both camps lack. *First step:* 20 golden scenes through Blender to USD and back; loss receipt per field; usdchecker on each. *Grader:* usdchecker + a loss receipt in both directions.
5. **Quality-diversity evolution of X3D scenes (MAP-Elites, novelty search)**. An archive of valid-but-strange scenes that no person would write: every cell that one reader accepts and another breaks is a new receipt, found without a model call. *First step:* Evolve 200 generations over a 12-node vocabulary; fitness is admitted by the gate and renders non-black; keep one judge held out so the search cannot learn it. *Grader:* x3d_mcp validator + loom traps + render non-black check.
6. **STEM, maths and PolyXandria**. The cheapest exact references anywhere; best ground for testing new Loom organs. *First step:* Use as the test bed for qd-evolve and geom-witness. *Grader:* exact identities and convergence orders.
7. **Prompt injection through 3D files: Metadata, WorldInfo, Script, Anchor and Inline as attack channels**. If X3D is the format an AI is held accountable to, a scene must not be able to instruct the AI reading it. Nobody has mapped this surface. *First step:* List every X3D field that carries free text or a URL; build 40 hostile scenes; run them through the Gobbler's quoting lint. *Grader:* static taint lint (which text fields reach a prompt) + planted canary strings.
8. **A public scoreboard of models on Loom tasks**. The Loom's failure modes become an exam any model can sit. It is the one artefact outsiders can cite, and each model's misses are fresh receipts. *First step:* Freeze 60 tasks from failure modes that have a code grader; hold 12 private; score 3 trials per task. *Grader:* validator + traps + hidden reference answers.
9. **The hostile-file corpus against every reader, not only Blender**. 73 hostile files took the Blender add-on from 26 failures to 0. X_ITE, three.js, Castle and x3d.wgpu have never faced them. *First step:* Run the 73 files against x3d.wgpu and the x3d_mcp parser under the same limits; count failures per reader. *Grader:* sandboxed resource limits + crash and disclosure sentinels.
10. **Physics engines (PhysX, MuJoCo, Rapier; next Jolt and Bullet)**. 32 witness patterns already; a third and fourth engine turn cross-engine disagreement into the reference. *First step:* Same marble scene in Rapier and Jolt; report the first step where they part and why. *Grader:* step hash replayed in every host + analytic ladder.
11. **Generative shader art behind a compile-and-render guard (GLSL, WGSL)**. Shaders are where validators go blind; a guard that compiles, links and renders closes the gap the shader fixture guard admits it leaves. *First step:* Extend the 5-fixture shader guard to compile and render; evolve 100 fragment shaders under it. *Grader:* glslang and naga compile + lavapipe render hash.
12. **Cultural heritage with CIDOC-CRM (Shroud, Giza)**. Claims with grades are the Loom's own idea applied to history; the Shroud Atlas proved the speed. *First step:* Express the Giza 63 claims in CIDOC-CRM and check each resolves to a scene node. *Grader:* evidence-tier ledger tied to scene bytes.
13. **Molecules and proteins (zinc fingers reborn)**. Fertile and proven; the next gain is dynamics (trajectories) and density maps, where exact references still exist. *First step:* Take 3 of the 9 red zinc sites through a second reader and a trajectory frame witness. *Grader:* deposited structures + the metal-site witness with 25 negative controls.
14. **Robotics: URDF, MJCF and ROS bags**. A robot description is a scene graph with joints; the MuJoCo bridge and the new MCAP reader are two thirds of the road. *First step:* One open URDF arm to H-Anim-style joints; 100 random poses agree with MuJoCo to a stated tolerance. *Grader:* forward kinematics against MuJoCo on the same model.
15. **Retrieval over the Loom: the right law and failure mode on the page before the first line is written**. 213 failure modes are useless unread. Retrieval at kickoff makes every past receipt pay again; lexical first, so no model call. *First step:* Build BM25 over laws, failure modes and LEARNINGS; write 40 questions from real incidents; measure recall at 5. *Grader:* recall at 5 on held-out failure-mode questions.
