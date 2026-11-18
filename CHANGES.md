# Intervention Lab and rigorous review pass (17 Nov 2026)

This pass targets GitHub commit `11a561623b7539f1f9bf20f8ef7bc5b9706c10d2`.
It adds three X3D evidence experiments, repairs the kernel/Flyte/frontend/scene
boundaries, hardens standalone rebuilding, and supplies full pinned validation
with source-bound release evidence. See [implementation review](docs/IMPLEMENTATION-REVIEW.md),
[baseline assessment](docs/GOBBLER-REVIEW.md) and [release receipt](receipts/review-release.json).

Fresh native browser execution is `not_run`: Chromium socket initialization is
blocked by this host. The Blender preview is an actual import/placement check
with explicit studio presentation changes, not browser pixels. The earlier
browser figures below remain historical and do not certify the changed revision.

---

# Historical independent assessment and changes (17 Nov 2026)

Rig: Python 3.13.18, rdflib 7.6.0, x3d_mcp `fa5dccf` (XSD + semantic validator), Node Playwright with Chromium 153.0.8010.12 on software GL (SwiftShader). Nothing here is a GPU measurement.

| # | Finding | Grade | Evidence | Fix |
|---|---|---|---|---|
| 1 | Upload reproduces as claimed: 52 unit tests, 11 offline checks | Confirmed | `python -m unittest` and `verify.py`, run fresh on the extracted ZIP | none needed |
| 2 | The "missing helpers" are recoverable: the pinned `x3d.docs@ff0565e` has `docs/tools-shared`. With it, the Atlas rebuilds **byte-identical** (6 output files) and the original 17-check witness passes | Confirmed | `receipts/witness-replay.json` | `tools/fetch_pins.py`; `build_atlas.py` honours `X3D_DOCS` and says what to run when the tree is absent |
| 3 | Absolute `/Users/...` x3d_mcp path in `validate_one.py` (x2) and `check_atlas.py` | Confirmed | grep | `X3D_MCP_DIR` or a sibling `x3d_mcp` checkout; duplicate copy removed |
| 4 | `atlas-world.x3d` viewpoint `V_laws` had orientation `0 0 0 3.142` (zero-length axis). Current x3d_mcp reports it as `rotation-zero-axis` | Confirmed | validator: 1 error before, 0 after | `look_at()` takes the axis from the symmetric part near a half turn. Fixed scene lives in `atlas/out-r1/`; archived `out/` stays hash-bound and untouched |
| 5 | At 1440x900 the left panel overflowed into the controls and the feather nav intercepted clicks on the Foldback button | Confirmed | Playwright click timeout; screenshot | panels bottom-anchored and scrollable; canvas edges feathered |
| 6 | The single-file export (`Gobbler-Evidence-Loom.html`) **did not open the scene**: X_ITE lazy-loads components, a wasm tangent library and its stylesheet from sibling folders, none of which exist in one file. Status stuck at "Could not open the X3D loom" | Confirmed | Playwright, original upload served over http | five components, the wasm and the stylesheet embedded; engine shimmed to read them (blob/data URLs). 15/15 browser checks now pass |
| 7 | Two identical vendored X_ITE trees (17 MB each) | Confirmed | `diff -rq` | one shared `vendor/x_ite/` |
| 8 | Zero-axis class of bug is invisible to the portable XML checks | Likely | verify.py passed with the bad viewpoint | validator replay is now part of the witness (`make replay`) |

## What is still not verified
Hardware GPU speed, Firefox and Safari, real phones, listening to the score, XSD of the *original* upload's other scenes (observatory.x3d and scene.x3d now validate: 0 errors, 0 warnings).

## Not applied
`flywheel-review/loom-pr/` patches 2 and 3 no longer apply to x3d.loom main (it moved to 186 failure modes); patch 1 (three text defects) applies and is carried in the x3d.loom PR.
