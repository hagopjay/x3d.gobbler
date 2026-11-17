# Gobbler / The Evidence Loom


> **Status, 17 Nov 2026.** Independently re-run and extended: see [CHANGES.md](CHANGES.md). Browser rendering is now measured (Chromium 153, software GL): 15/15 checks on the observatory and on the single-file export; the pinned helper tree is recoverable (`python3 tools/fetch_pins.py`) and the full Atlas witness replays 19/19. Live page: Settings, Pages, branch `main`, folder `/` (https://hagopjay.github.io/x3d.gobbler/). `make all` runs the offline checks.

An X3D flywheel observatory built from the supplied flywheel archive. Twelve inspectable domain feathers surround an abstract Gobbler; a pinned Atlas provides its memory. This iteration connects the visual to real snapshot facts and gives the foldback idea an executable local test.

## Open it

**Quick preview:** open `Gobbler-Evidence-Loom.html` in a modern WebGL2 browser. It embeds the engine, geometry, graph, and reports. Domain names stay in the HTML dock; the full project adds 3D labels and the original soundtrack. The standalone export is browser-checked (see CHANGES.md).

**Editable full edition, Windows / WSL2 or Linux:** extract the entire ZIP, then run from its root:

```bash
python3 serve.py
```

Open **http://localhost:8831/gobbler-flyte/** in your Windows or Linux browser. On Windows without WSL, `py serve.py` also works. The server binds only loopback. Python 3.13+ is suitable; this session tested 3.12. No installation or external API is needed for normal use.

- Select a feather using the domain dock or the X3D wheel.
- Use **Evidence** to inspect recounts and source pins.
- Use **Foldback** to scrub the clearly synthetic four-stage teaching sequence.
- The executed local shader guard has a separate inspector. Its five fixture results come from actual Python checks.
- Use **Find** to search the complete local Atlas and inspect its records and edges. The graph digest must match before search results appear.
- Change viewpoint, approach a selected wheel, pause motion, hide labels, or reduce decorative detail. Reduced-motion preference pauses scene clocks initially.
- Sound is opt-in and independent of scene clocks. The supplied original score is preserved; this iteration does not claim sample-accurate audiovisual synchronization or a new listening review.

The original nine-wheel art remains at `/gobbler-flyte/cinematic.html`; the original walkable graph is `/flywheel-review/atlas/fly.html`.

## Read the assessment

`X3D-Flywheel-Atlas.html` is the finished reading edition. Its source is `flywheel-review/ATLAS-INSIGHTS.md`.

The core conclusion: measure a flywheel turn as an evidence-bound improvement reused by a second consumer. Keep graph size, quotation coverage, reproduced experiments, and human judgments distinct.

The snapshot has **2,181 entities, 7,222 edges, 44 laws, 160 failure modes**, and **34/591 numbered claims with archived verified quote support**. These are archive facts, not a fresh GitHub census. All eight hashes in the historical receipt match. The portable audit separately passes nine checks.

## Rebuild and verify

```bash
python3 flywheel-review/atlas/flywheel_kernel.py
python3 gobbler-flyte/build_observatory.py
python3 flywheel-review/atlas/shader_guard.py
python3 flywheel-review/atlas/snapshot_audit.py --output flywheel-review/snapshot-audit.json
python3 verify.py
python3 gobbler-flyte/build_standalone.py --output Gobbler-Evidence-Loom.html
```

The 52 regression tests exercise the evidence kernel, portable audit, and actual shader guard. `verify.py` additionally checks deterministic scene rebuilding, source digests, scene/document names, animation tuples, and local assets. `VALIDATION.json`, `snapshot-audit.json`, and `foldback-run.json` are separate receipts; the original `atlas/out/receipt.json` is retained untouched.

The new shader guard is deliberately narrow. It rejects raw GLSL in a ShaderPart URL channel, accepts data URIs and normal URL references, and runs an authored Music fixture through the same check. It does not fetch, compile, link, or render shaders. A successful authored consumer fixture is not evidence of adoption by a live repository.

The new observatory source uses shared meshes, one batched star field, standard X3D clocks/interpolators, no Script node, and no external scene dependency. The scene embeds both Atlas and manifest digests. All motion is illustrative; it is never counted as repository activity.

## Evidence limits

Hardware GPU speed, mobile rendering, and audio listening were not verified here. The local browser launch was restricted; the available preview browser could not reach the local server. UI cadence is explicitly labelled as such and is not a GPU benchmark.

The full Atlas witness replays after `python3 tools/fetch_pins.py` (pinned `x3d.docs@ff0565e`) with `X3D_MCP_DIR` pointing at an x3d_mcp checkout; see `receipts/witness-replay.json`. The new portable audit verifies the archived outputs without silently substituting a stale historical green receipt. No evidence grade is promoted by these checks. Hash agreement establishes byte consistency, not authorship or empirical truth.

## Fold back to GitHub

The accompanying patch is based on the exact extracted archive layout, not an invented current upstream commit. `PR-BODY.md` contains the concrete changes, validation, scope, and recommended landing plan. The patch was checked against a clean extraction of the original ZIP.

```bash
# Run inside a clean extraction of the ORIGINAL supplied archive.
git apply --check /path/to/X3D-Flywheel-Foldback.patch
git apply /path/to/X3D-Flywheel-Foldback.patch
python3 verify.py
```

GitHub publication was unavailable: the account's GitHub integration is disabled and the CLI has no authenticated account. No remote branch or PR was created. Suggested landing is a reviewed subtree in `x3d.demo`, with the portable evidence helpers subsequently moved to the Atlas/Loom home. Confirm the current repository layout and base before translating the archive-relative paths. The existing `loom-pr/` patch series in the input is preserved separately; this iteration does not claim to have applied or submitted it.

The supplied runtime and notices remain under `vendor/x_ite/` (one shared copy; it was byte-identical in the two places it first shipped). The standalone export includes the bundled notices. No blanket license decision is imposed on the original project.
