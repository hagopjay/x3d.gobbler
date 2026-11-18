# Runtime and executable acceptance review

Baseline: `11a561623b7539f1f9bf20f8ef7bc5b9706c10d2`.
Historical browser records in `receipts/browser-*.json` are preserved. They do
not bind their results to current source bytes. This extension keeps their
claims separate from fresh source-bound records prefixed `review-`.

## Findings and repairs

| Baseline defect | Repair | Limit |
| --- | --- | --- |
| Any status without “Opening” or “Loading” passed the boot assertion, including “Could not open the X3D loom”. | Native acceptance requires `window.__flywheel.ready === true`, successful lifecycle status, and expected named Gobbler controls in the actual loaded world. | The browser must execute before that is a result; static/source tests cannot supply it. |
| A missing dependency or failed Chromium launch exited without a new JSON record, allowing an old success to remain the only visible receipt. | The browser tool writes a fresh receipt in `finally`, with `not_run` for a blocked launch and a nonzero exit. Errors after launch are failures. | Receipt identity is local and unsigned. |
| The test server used a lexical string-prefix check and unguarded URI decoding. | Segment-aware confinement, real-path checks, malformed-URI handling and correct WASM/font MIME types. Five actual loopback HTTP controls cover a sibling-prefix escape and a symlink escape. | This is a local acceptance server, not a deployment service. |
| Missing assets could broadly suppress generic console resource errors. | Only explicitly requested optional UI font/logo paths may be omitted; omissions remain listed. Generic console errors and required resource failures are retained. | Optional omissions still weaken typography/branding acceptance. |
| Browser results were not tied to source/runtime identity. | Tool, application inputs and all bundled runtime files are hashed before execution, then compared after it. | A hash detects drift; it does not authenticate a publisher or prove an unexecuted gate. |
| Full X3D replay depended on an unspecified external validator checkout/environment. | A pinned, unchanged public validator subset and real schemas are supplied locally with origin hashes. | This is a direct-function validation adapter, not a network MCP transport or a complete spec implementation. |

The browser's pause assertion also compares against the actual initial state.
Reduced-motion preferences can legitimately start paused, so assuming the first
click must set `aria-pressed=true` was an incorrect test expectation.

## Evidence files

| File | Meaning |
| --- | --- |
| `receipts/review-runtime-inventory.json` | Exact 129-file X_ITE **16.7.0** inventory from the named repository baseline. No fresh npm/publisher-archive verification is inferred. |
| `receipts/review-x3d.json` | Fresh full XSD/implemented semantic checks of current authored scene inputs, with tool, vendor, schema and candidate hashes. |
| `receipts/review-browser.json` | Independent native attempt. In this environment the fresh launch is `not_run`: Chromium's `socket()` initialization is denied by the host. Zero native assertions executed. |
| `receipts/review-release.json` | Executed aggregate commands, test counts/skips, generated-input identity, source stability and explicit native boundary. |
| `receipts/review-accrete.json` | Independently executed offline/simulation Flyte tests through the actual public accrete gate, pinned validator and temporary SQLite world; its original scope and identities are retained. |
| `receipts/review-blender.json` | Actual Blender import/render with bounded mechanism placement and vertex-count controls. The aggregate rebinds source/tool/image bytes without claiming another render. |
| `VALIDATION.json` | The project's current consistency checks, refreshed by its own tool; not a native rendering certificate. |

The browser attempt occurred during the implementation pass. If later frontend
changes alter its input inventory, this does not become native evidence for the
new revision. Its blocked status remains an accurately scoped historical
attempt. Re-run it on a machine where Chromium can launch.

## Full local X3D instrument

`vendor/x3d_mcp/` is the unchanged public subset from
[`hagopjay/x3d_mcp@b5c9956917714747fe1d034c729612e99b0f09c9`](https://github.com/hagopjay/x3d_mcp/tree/b5c9956917714747fe1d034c729612e99b0f09c9).
Its origin inventory is itself pinned in `tools/validate_scene.py`; every source
and schema hash is checked before use, imported module origins are constrained,
and unexpected namespace collisions fail. Upstream validator code is not
monkeypatched and the XML-signature schema is real, not a stand-in.

The adapter deliberately records **XSD 4.0** separately from the upstream
semantic function's implemented **4.1 vocabulary**. Warnings and information
remain in the receipt. Three repaired/defective pairs test distinct failures:

1. A valid radius versus nonnumeric radius: XSD rejection.
2. A valid ROUTE source versus a missing named source: semantic rejection.
3. A valid identity transform versus a nonzero-angle rotation with a zero axis:
   semantic rejection, covering the class missed by the old portable XML gate.

Each input has an explicit 8 MiB budget. Only the owned standard optional X3D
DOCTYPE is accepted; arbitrary DTD/entity declarations are refused. The default
set is the current observatory, current cinematic scene, repaired Atlas world,
new laboratory scenes and additional examples. The immutable archived Atlas
world remains historical and is not silently rewritten to make a new gate pass.

## Reproduce

```bash
python3 -m pip install -r tools/requirements-validation.txt -r flyte/requirements.txt
python3 tools/validate_scene.py
node tools/browser_check.cjs --self-test
python3 tools/check_release.py
```

Use `GOBBLER_TEST_PYTHON` to select another Python interpreter and
`GOBBLER_TEST_NODE` for Node. Test dependencies must import before the aggregate
begins. The Flyte world integration controls additionally require the real
public `x3d.accrete` checkout/dependencies described by that component. Skips or
expected failures are marked incomplete rather than reported as a complete
release pass. Python suites run both normally and under `-O`; unittest
assertions remain active in both executions.

The aggregate independently locates the actual accrete backend through the same
bridge used by the tests. It records the full backend source-file inventory,
Git commit/working-tree state, admission-instrument identity and dependency
versions before and after execution. A change in any of them fails stability.
The historical integration receipt names the checked public revision; a future
run may deliberately use another revision, but must record its own bytes and
actually rerun the tests. No current integration result is inferred merely by
copying the older receipt.

The aggregate does not launch Chromium again. Run native acceptance separately:

```bash
# Playwright must be installed and resolvable by Node.
node tools/browser_check.cjs --json receipts/review-browser.json
node tools/browser_check.cjs --page Gobbler-Evidence-Loom.html --json receipts/review-browser-standalone.json
```

The native tool records actual Playwright/Chromium versions. Its rAF measurement
is UI cadence under requested software rendering, not GPU FPS. Neither a
nonempty scene nor a static screenshot establishes correct scientific claims,
audio quality, mobile device behavior, accessibility or real GPU performance.

## Next bounded acceptance work

First run both native entry points on supported desktop browsers. Inspect the
three laboratory interventions, current world names, keyboard controls,
reduced-motion startup and responsive layout. Then measure frame-time
percentiles, scene parse/commit time, memory and node counts under a fixed
workload and declared device. A second renderer/importer needs independent
occupancy/transform/material checks. Keep each result attached to its input and
instrument, with a specific acceptance question.
