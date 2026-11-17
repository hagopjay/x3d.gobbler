# 01. The tether

> **Say it:** X3D can be held to account because a program can name exactly what is wrong with a file, a second program can show what the file draws, and the record of both checks can travel inside the file; this holds for structure and behaviour, while appearance and intent still need a renderer and a person. **[L]**

| field | value |
|---|---|
| chapter code | `TH` |
| prerequisites | none |
| after this you can | (1) score any pipeline on five questions and say whether it earns a loop, a ledger or a log table; (2) draw the write, validate, fix, re-validate, render, ledger loop and name the instrument at each stage; (3) reproduce "valid but blank" and the pin-rule drift with free commands; (4) list what the tether does not give; (5) apply the decision procedure to a pipeline that is not 3D |
| sources read | `x3d.loom@162ab18:LOOM-v1.md` (sections 1, 3, 6, 7, 8), `x3d_mcp@b4efcd3:docs/EXACT-FIX-HINTS.md`, `x3d_mcp@b4efcd3:docs/ROUTE-COLOUR-HANIM-CHECKS.md`, `x3d_mcp@b4efcd3:evaluation/exact_fix_eval.py`, `x3d.loom@162ab18:kit/loomkit/accept.py`, `x3d.loom@162ab18:LESSONS-v1.0.md`, `x3d.docs@f172f67:docs/x3d.loom/MASTERCLASS.md` |
| instruments used | `x3d_mcp fork b4efcd3`, `X3D XSD 4.0` (sha256 0509fa5bd601), `X_ITE 16.7.0`, `Chromium 153 (Chrome for Testing 153.0.8010.12), SwiftShader`, `x3d.loom@162ab18` (loomkit), libxml2 2.14.6 / lxml 6.1.3, Python 3.13.18 |

## 1. The map

The tether is six legs that all attach to one text file. A pipeline is tethered when every leg exists and a red leg sends work back to the writer, never to a hand edit of the output.

```text
  writer (model, Blender, hand) -- unreliable by assumption
        |
        v   scene.x3d : text, hashable, named nodes (DEF/USE), wired events (ROUTE)
  +--------------------------------------------------------------------------------------+
  |  leg 1  RULES     X3D XSD 4.0 + X3DUOM 4.1 + semantic checks   says  "what is wrong"    |
  |  leg 2  ORACLE    one verdict per file, rule id, path, line    says  "where, and which" |
  |  leg 3  REPAIR    exact-fix hint -> apply -> re-validate       says  "is it fixed"      |
  |  leg 4  RENDER    second program draws it, pixel statistics    says  "is it visible"    |
  |  leg 5  HISTORY   hash chain in <head><meta>, receipt          says  "who did what"     |
  |  leg 6  HUMAN     named acceptor, waivers with owner and date  says  "who answers"      |
  +--------------------------------------------------------------------------------------+
        |  red on any leg
        v
  back to the card or generator; the output is never patched by hand (Loom law 1)
```

| in scope | out of scope |
|---|---|
| why the six legs make an AI answerable (section 2) | the validator's internals: [03](03-validator-and-gates.md) |
| the five-question score and how to apply it (section 3) | the tool surface an agent calls: [04](04-mcp-for-agents.md) |
| the loop, with one worked example that runs (sections 4 and 5) | the full list of laws and traps: [02](02-loom-laws.md) |
| measured evidence, the pin rule, and what is not given (sections 6 to 8) | the second renderer in depth: [06](06-xite-the-oracle.md) |
| an in-file ledger sketch and a decision procedure (sections 9 and 10) | signing and authorship: named as a gap, not solved here |

**Read next:** deeper, [03 validator and gates](03-validator-and-gates.md); wider, [02 the Loom laws](02-loom-laws.md).

## 2. Six properties that make an AI answerable

The thesis is a claim about properties, not about branding. Each row names where the property lives and what fails without it.

| # | property | what X3D provides | where it lives | without it | grade |
|---|---|---|---|---|---|
| 1 | rules a machine can read | XSD, X3DUOM, DTD, an ontology; the fork bundles `x3d-4.0.xsd` and `X3dUnifiedObjectModel-4.1.xml` | `x3d_mcp@b4efcd3:src/validation/schemas/` | review by eye; a model judges a statement the schema could answer exactly | [C] read |
| 2 | an oracle that is exact about what it checks | `validate_xml` (XSD) then `semantic_diagnostics` (route order, colour range, component levels, array counts, H-Anim names) | `x3d_mcp@b4efcd3:src/validation/` | "looks fine" verdicts; the same scene passes one day and fails the next | [C] run |
| 3 | a fix the oracle can name | `suggested_fix` ops: `set_attribute`, `move`, `wrap`, `rename_element`, `rename_attribute`, `remove_attribute`, `remove_element` (290, 127, 10, 58, 29, 29, 15 uses in the 540-case run) | `x3d_mcp@b4efcd3:src/validation/hints.py` | the writer guesses; the loop needs more rounds | [C] run |
| 4 | a second program that draws the same file | X_ITE in a browser; pixel statistics over its frame | `x3d.docs@f172f67:docs/vendor/x_ite/` | "valid" is read as "visible" | [C] run |
| 5 | history that travels with the file | `<head><meta>` carries a hash chain (x3dprov 0.1 in the Loom; a 40-line sketch in section 9) | `x3d.loom@162ab18:LOOM-v1.md` section 5 | a pass cannot be tied to the bytes it judged | [L] read, sketch [C] |
| 6 | a human who is answerable | nothing leaves without an explicit "send" (law 16); judges flag and never grade (law 6); every waiver names an owner and a date (law 43) | `x3d.loom@162ab18:LOOM-v1.md` section 3 | a green row nobody can be asked about | [L] read |

The tether line as the Loom states it: "X3D is the 3D format an AI can be held accountable to for structure and behaviour. For appearance, accountability takes a browser and an eye, and the Loom keeps all three in one loop" (proposed by a 29 Oct review, `x3d.loom@162ab18:LOOM-v1.md` section 1). **[L]**: the words are a proposal; the properties above are the part that was measured.

## 3. The five-question tether score

The score decides how much machinery a pipeline deserves. Binary, one point each. If you hesitate, score 0 and write why.

| Q | question | scores 1 point when | quick test (under 10 minutes) | X3D |
|---|---|---|---|---|
| Q1 | is the writer unreliable? | a model, a script or a person at speed writes the artifact and errors are not rare | take 20 outputs and count the ones a reviewer would reject | 1 |
| Q2 | is there an EXACT oracle? | a program gives pass or fail, names the rule and the place, and gives the same verdict twice, with no judgement call | run it twice on one file; ask whether a model is inside the verdict | 1 |
| Q3 | can valid differ from works? | the oracle passes something that fails in use, so a second instrument is needed | build one artifact that passes and fails in use; if you cannot, run a cohort and count | 1 |
| Q4 | must the history travel? | the artifact is copied, re-hosted or reviewed away from the system that made it | list the places the file goes; does the log go too? | 1 |
| Q5 | will someone answer later? | a named person or team must defend the decision after the fact | write the name of who is asked when it goes wrong | 1 |

```text
  score    5 or 4            3                  2 or less
           |                 |                  |
           v                 v                  v
        full tether      gate + ledger      log table
        (legs 1 to 6)    (legs 1,2,5,6)     (record who, what, when; no loop)

  Q2 is a gate on its own: Q2 = 0 means build a ledger, never a repair loop,
  whatever the total (a loop without an exact oracle repairs toward a guess).
```

**How to score any pipeline** (the method is a design rule, **[S]** for every family except X3D, because only X3D was measured):

1. Write the artifact and the writer in one line.
2. Run the five quick tests; record the evidence for each point in one cell.
3. Apply the bands. A pipeline that scores 5 but fails the Q2 test twice was mis-scored.
4. Name the instrument that would carry each leg. A leg without an instrument is a plan.
5. Re-score when the oracle changes: a new validator pin is a new score.

| pipeline | Q1 | Q2 | Q3 | Q4 | Q5 | score | band | evidence behind the points | grade |
|---|---|---|---|---|---|---|---|---|---|
| X3D scene written by a model | 1 | 1 | 1 | 1 | 1 | 5 | full tether | 0 of 24 seed scenes flagged at the control, 13 of 13 injected route faults flagged, 17.52% vs 0.00% non-background pixels (sections 5, 6) | [L] from [C] parts |
| a glb asset from an exporter | 1 | 1 | 1 | 0 | 1 | 4 | full tether if a carrier exists | Khronos glTF-Validator is exact on structure; whether metadata survives a re-export is not measured here (see [11](11-gltf-usd-khronos.md)) | [S] |
| model-written SQL migration | 1 | 1 | 1 | 0 | 1 | 4 | loop plus render-equivalent (run on a copy) | the parser is exact; "valid" does not mean safe to run on a large table; the migration table is already a ledger | [S] |
| model-written Python function | 1 | 1 | 1 | 0 | 1 | 4 | loop; Q2 is only as exact as the tests | the compiler is exact, the test suite is not complete | [S] |
| model-written summary of a report | 1 | 0 | 1 | 0 | 1 | 3 | ledger (Q2 = 0) | no program decides "faithful"; a judge model is a writer, not an oracle | [S] |
| a hand-drawn diagram image | 0 | 0 | 0 | 0 | 1 | 1 | log table | nothing to validate | [S] |

Anti-patterns when scoring: counting "has a test suite" as an exact oracle; counting a judge model as Q2; scoring Q4 from what you could add later rather than what travels today; copying the X3D column to another family without a measurement.

## 4. The loop

```text
  write ---> validate (XSD, then semantic) ---> valid? --no--> exact-fix hint (op, path, line)
    ^                                              |                     |
    |                                             yes                    v
    |                                              v              apply ONE fix
    |                                       render check                 |
    |                                    (frame, pixel floor)            v
    |                                              |             re-validate (same pin)
    |                                    visible?--no--> back to card/generator  |
    |                                              |                              |
    |                                             yes                             |
    |                                              v                              |
    |                                    ledger: bind hash, pin, frame,           |
    |                                    witness status; named acceptor           |
    |                                              |                              |
    +------------ red anywhere: fix the card, not the file <---------------------+
```

| step | instrument | output | stop rule | catches |
|---|---|---|---|---|
| write | model, Blender add-on, generator | `scene.x3d` | a generator emits it; no hand edits (law 1) | nothing; this is the unreliable leg |
| validate | `x3d_mcp fork b4efcd3`: `validate_xml` then `semantic_diagnostics` (`hints.gate` runs both) | `{valid, stage, errors, hints}` | stop at first failing stage | grammar, containment, enums, ROUTE order, colour range, component levels |
| fix | `suggested_fix` from `hints.py`; `repair_with_hints` applies one at a time | edited text | re-validate after each fix; cap the rounds (the paired model run used 2) | the named errors only |
| render | `X_ITE 16.7.0`, `Chromium 153 ... SwiftShader` | PNG, pixel fraction | a floor chosen before the run (here 1% non-background) | blank, off-camera, culled, transparent |
| ledger | hash of the candidate, witness records, receipt (`loom accept`, `loom receipt`) | `receipt.json`, unsigned | accept only a closed set of current witnesses | stale passes, missing witnesses |
| accept | a named human, a profile | decision, waivers | waivers have owner, date, reason | what no instrument can see |

Two facts the loop must not hide. A scene that becomes valid after hints is not a reviewed scene: the original came back exactly in 268 of 540 cases and 15 became valid only because an element was deleted (`x3d_mcp fork b4efcd3`, seed 20261029) **[C]**. And hints are proposals: one broken ROUTE produced two hints in the worked example below, and only the re-validation step shows which was real **[C]**.

## 5. Worked example: valid, blank, refused

Two scenes differ by one attribute. The second looks away from the box.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<X3D profile="Immersive" version="4.0">
  <Scene>
    <Viewpoint position="0 0 6" description="front"/>
    <Shape>
      <Appearance><Material diffuseColor="1 0 0"/></Appearance>
      <Box size="2 2 2"/>
    </Shape>
  </Scene>
</X3D>
```

For `blank.x3d`, change the viewpoint to `<Viewpoint position="0 0 6" orientation="0 1 0 3.14159" description="faces away"/>`.

**Step 1, validate** (from a checkout of `hagopjay/x3d_mcp` at `b4efcd3`, files in the current folder):

```bash
python3 - <<'EOF'
import sys; sys.path.insert(0, "src")
from validation.hints import gate
for n in ("visible", "blank"):
    r = gate(open(f"{n}.x3d", encoding="utf-8").read())
    print(n, r["valid"], r["stage"], len(r["errors"]), len(r["hints"]))
EOF
```

**Step 2, render.** The page template wraps one scene; the Node script drives headless Chrome through the DevTools protocol, waits in real time (virtual-time budgets stopped X_ITE on its splash screen in the first attempt), reads X_ITE's own version and takes a screenshot.

```html
<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="x_ite/x_ite.css"><script src="x_ite/x_ite.min.js"></script>
<style>html,body{margin:0;background:#fff}x3d-canvas{width:320px;height:240px;display:block}</style>
<x3d-canvas src="blank.x3d" contentScale="1"></x3d-canvas>
```

```js
// shot.mjs  usage: node shot.mjs URL OUT.png   (Node 22; CHROME env var overrides the binary name)
import { spawn } from 'node:child_process'; import fs from 'node:fs';
const [url, out] = process.argv.slice(2), port = 9333 + Math.floor(Math.random() * 500);
const chrome = spawn(process.env.CHROME || 'google-chrome', ['--headless=new', '--no-sandbox', '--use-gl=angle',
  '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', `--remote-debugging-port=${port}`,
  '--window-size=320,240', 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms)); let tabs;
for (let i = 0; i < 50; i++) { try { tabs = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
  if (tabs.find(t => t.type === 'page')) break; } catch {} await sleep(200); }
const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise(r => ws.onopen = r);
let id = 0; const pend = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Emulation.setDeviceMetricsOverride', { width: 320, height: 240, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url }); await sleep(9000);
const v = await send('Runtime.evaluate', { expression: 'document.querySelector("x3d-canvas").browser.version', returnByValue: true });
console.log('X_ITE', v.result.result.value);
fs.writeFileSync(out, Buffer.from((await send('Page.captureScreenshot', { format: 'png' })).result.data, 'base64'));
chrome.kill('SIGKILL'); process.exit(0);
```

```bash
python3 -m http.server 8765 --bind 127.0.0.1 &   # serve the folder holding x_ite/, the pages and the scenes
node shot.mjs http://127.0.0.1:8765/visible.html visible.png
python3 - <<'EOF'
from PIL import Image; import numpy as np
im = np.asarray(Image.open("visible.png").convert("RGB")).astype(int)
print("non-background fraction %.4f" % (np.abs(im - im[2, 2]).sum(axis=2) > 30).mean())
EOF
```

**Result** (`x3d_mcp fork b4efcd3`; `X_ITE 16.7.0`, `Chromium 153 (Chrome for Testing 153.0.8010.12), SwiftShader`, 320 x 240) **[C]**:

| scene | fork gate | stage | errors | non-background fraction | unique colours in frame |
|---|---|---|---|---|---|
| `visible.x3d` | valid | semantic | 0 | 0.1752 | 2 |
| `blank.x3d` | valid | semantic | 0 | 0.0000 | 1 |

Both are valid and identical in every node; only one draws. The validator was right about what it checks; it was never asked about the camera.

**Step 3, make the loop refuse it.** Put the checks behind a Loom profile with three required witnesses (`grammar`, `traps`, `eyes`). The `grammar` witness is the `gate` loop above wrapped as a command; `eyes` wraps the render and exits 1 when any scene is under 1% non-background pixels. Each adapter follows the exit contract of `kit/loomkit/cli.py:cmd_command` (0 pass, 1 fail, anything else error). From a checkout of `hagopjay/x3d.loom` at `162ab18`, on a project folder `proj/` that holds `scenes/`, `tools/` and `gen/`:

```bash
kit/loom traps   proj --evidence ev --files 'scenes/*.x3d' --host strict
kit/loom command proj --evidence ev --name grammar -- python3 tools/validate_scenes.py
kit/loom command proj --evidence ev --name eyes    -- python3 tools/eyes.py
kit/loom accept  proj --evidence ev --profile drill-profile.json
kit/loom receipt proj --evidence ev --profile drill-profile.json --subject "drill" --out receipt/receipt.json
kit/loom verify-receipt receipt/receipt.json
```

with `drill-profile.json` equal to `{"schema":"loom.profile/1","name":"drill/visible-v1","required":[{"witness":"grammar"},{"witness":"traps","coverage":{"rules":15}},{"witness":"eyes"}],"visible_not_run":["host"]}`.

| state of `proj/` | what ran | result | code | grade |
|---|---|---|---|---|
| `visible.x3d` only (5 files in the candidate) | all three witnesses | accepted; receipt written; `verify-receipt` says intact | none | [C] |
| `blank.x3d` added (6 files), witnesses not re-run | `accept` | rejected: `grammar` was bound to the old candidate | `STALE_WITNESS` | [C] |
| witnesses re-run on 6 files | `grammar` pass, `traps` pass, `eyes` fail | rejected: `eyes: fail` | `WITNESS_NOT_PASS` | [C] |

Instrument for the table: `x3d.loom@162ab18` (`kit/loomkit`), `x3d_mcp fork b4efcd3`, `X_ITE 16.7.0`, `Chromium 153 ... SwiftShader`. The eyes log of the third run read `scenes/blank.x3d: non-background fraction 0.0000 BLANK` and `scenes/visible.x3d: non-background fraction 0.1752 OK`. A candidate that contains the test code (`tools/`) is what makes the stale check work (law 17): editing an adapter would also have made the old passes stale.

**Step 4, what the hints say** about three broken variants of the same scene (`x3d_mcp fork b4efcd3`, `hints.gate`) **[C]**:

| variant | stage | rule | suggested fix | confidence |
|---|---|---|---|---|
| `<Box/>` directly under `<Transform>` | xsd | `wrong-parent` | `wrap` in `Shape` (`Shape.geometry` takes a Box) | choice |
| `diffuseColor="255 0 0"` | xsd | `colour-out-of-range` | `set_attribute diffuseColor "1 0 0"` (values looked like 0..255, divided by 255) | choice |
| a ROUTE placed before the DEF it names | semantic | `route-before-def` | `move` the ROUTE to the end of the Scene | exact |

In the third variant the gate returned one error and two hints. The second hint pointed at a ROUTE that already follows its nodes. `repair_with_hints` applied one fix (`move` of `ROUTE[1]`) and the re-check passed, so the loop was right and the hint list over-reported **[C]**, observed on one snippet and not investigated further.

## 6. Measured evidence

Rows marked "re-run" were executed for this chapter on 2026-11-14; rows marked "carried" were read in `x3d.loom@162ab18:LOOM-v1.md` and not re-checked (their measuring documents are not public), so they are capped at [L].

| claim | result | instrument | grade | status |
|---|---|---|---|---|
| valid is not visible (constructed) | 2 of 2 valid; 17.52% vs 0.00% non-background | `x3d_mcp fork b4efcd3`; `X_ITE 16.7.0`, Chromium 153, SwiftShader | [C] | re-run |
| valid is not visible (cohort) | 17 of 91 "valid" scenes rendered blank; 10 invalid scenes still drew something | cohort of a service validator and X_ITE, LOOM-v1 failure mode 91 | [L] | carried |
| valid scenes that draw nothing | 203 of 1,058 | LOOM-v1 section 7.2 | [L] | carried |
| wrong-but-valid scenes (synthetic) | 13 of 16 pass strict validation; the lawful metric catches 16 | LOOM-v1 section 7.2 | [L] | carried |
| report-only repair loop (a model sees the plain errors) | first repair valid 489 of 540 (90.6%); after round 2, 524 of 540 (97.0%); 540 synthetic mutants | a hosted model, LOOM-v1 section 7.1 | [L] | carried |
| the same loop with exact-fix hints | first repair valid 507 of 540 (93.9%), 31 gained and 13 lost, p 0.0096; round 2: 530 vs 524, not significant | a hosted model, LOOM-v1 section 7.1 | [L] | carried |
| exact-fix hints with no model | hint loop alone 521 of 540 (96.5%); `repair_x3d` alone 76 of 540 (14.1%) | `x3d_mcp fork b4efcd3`, `exact_fix_eval.py --seed 20261029 --per-class 45` | [C] | re-run |
| the model-free metric | lawful metric AUC 0.997 on 383 recorded scenes; 67 of 67 optimised scenes declared the Full profile when that escape hatch was open | x3d.onto lawful metric, LOOM-v1 section 7.2 | [L] | carried |
| detection of injected defects, by construction | route moved to the top of the Scene: 13 of 13 caught by the gate, 0 of 13 by the XSD alone; 0 of 24 unchanged seeds flagged | `x3d_mcp fork b4efcd3`, `validate_xml` vs `hints.gate`, 24 seed scenes | [C] | re-run |
| a blind spot of the same oracle | first `Transform` translated to `1000 0 0` (a floating part): 0 of 14 caught by either | same | [C] | re-run |
| the fork's own planted-fault table | ROUTE moved to the start: 0 to 200 of 200; negative first colour component: 0 to 200 of 200; `1.5` re-split: 177 to 200; H-Anim 1.x alias: 59 of 59; controls 0 invalid | libxml2 2.14.6, `x3d_mcp@b4efcd3:docs/ROUTE-COLOUR-HANIM-CHECKS.md` | [L] | read, not run |
| grounding a model judge in the schema | 99 vs 87 of 115 fuzzer findings judged right (p 0.017); invented evidence 9 vs 29 | a hosted model, LOOM-v1 section 7.1 | [L] | carried |
| a model judge's score is noise | re-judging the same frame moved the score by sd 0.12 to 0.25; a black still once scored 2.33 | LOOM-v1 section 6 step 6 | [L] | carried |

Two caveats the evidence rows depend on. The hint corpus is by the same author as the hint rules (`EXACT-FIX-HINTS.md` says so), so it measures the errors the hints were designed for **[L]**. And `x3d_mcp@b4efcd3:docs/EXACT-FIX-HINTS.md` still says the model repair loop is "not measured (S)" while LOOM-v1 section 7.1 reports a paired model run; both are in the record, and the model rows stay at [L] until the run is repeated. That the two documents conflict is **[C]** (both files were read).

## 7. The pin rule: numbers hold only at the named validator commit

Law 15 says to name the instrument behind every number. The re-run shows why. The same script, the same seed and the same machine, at four validator commits:

| fork commit | date | seeds | mutation sites | errors | before (`repair_x3d` alone) | after (`repair_x3d` then hints) | hints alone | seed restored | valid by deleting an element |
|---|---|---|---|---|---|---|---|---|---|
| `535fdac` | 2026-10-29 | 25 | 15,651 | 570 | 81 (15.0%) | 523 (96.9%) | 522 (96.7%) | 257 | 12 |
| `ffbc20f` | 2026-10-30 | 24 | 10,294 | 577 | 76 (14.1%) | 522 (96.7%) | 521 (96.5%) | 268 | 15 |
| `327c5c4` | 2026-11-01 | 24 | 10,294 | 577 | 76 (14.1%) | 522 (96.7%) | 521 (96.5%) | 268 | 15 |
| `b4efcd3` | 2026-11-13 | 24 | 10,294 | 577 | 76 (14.1%) | 522 (96.7%) | 521 (96.5%) | 268 | 15 |

All counts out of 540 cases; `x3d_mcp` forks, `exact_fix_eval.py --seed 20261029 --per-class 45`, Python 3.13.18, lxml 6.1.3, libxml2 2.14.6 **[C]**. At `535fdac` the recorded numbers in `EXACT-FIX-HINTS.md` (81, 523, 522, 257, 12, 25 seeds) reproduce exactly. After PR #15 (30 Oct) the same script gives different counts.

Cause, as far as it was traced: the seed list lost `examples/scenes/doha_qatar.x3d`. The raw file fails the gate at both commits (1 semantic error at `535fdac`, 2 at `b4efcd3`: `profile-component` for an `ElevationGrid` outside the declared profile, and `array-count` for a `Background` with one `groundColor` and one `groundAngle`). The script keeps a seed only if it clears the gate after `repair_x3d`; that it no longer does at `b4efcd3` is inferred from the seed lists **[L]**, the lists themselves and the two error counts are measured **[C]**.

How to write a pinned number, and what to do when the pin moves:

| do | example |
|---|---|
| write the commit, the seed and the library versions next to the value | `96.5% (521/540) hints alone, x3d_mcp fork b4efcd3, seed 20261029, libxml2 2.14.6` |
| keep the old row and add a dated row | `96.7% (522/540), x3d_mcp fork 535fdac, 2026-10-29` stays in the register |
| never edit a quoted number in place | a later chapter cites the row, it does not retype the value |
| say what changed when you can | "one seed left the corpus when `array-count` arrived" |
| treat an unpinned claim as a rumour | "7 to 10 of 10 repairs pass" holds at upstream `74da0ec` and was 3 to 6 at `020221e` (LOOM-v1 law 15, carried) |

## 8. What the tether does NOT give

| gap | evidence | what covers it | grade |
|---|---|---|---|
| intent | 268 of 540 repaired scenes equal the seed; the rest are valid, not necessarily what the author meant | a human reading the diff; a seed or card to diff against | [C] |
| a complete oracle | a floating part passes the whole gate (0 of 14); the XSD accepts `0.5 0.5 1.5 ...`, a leading minus and an exponent in colours, until the semantic layer was added | more rules, each with an injected-fault test; the render leg | [C], [L] for the colour cases |
| taste and appearance | a frame floor says "not blank", not "good"; model judges re-score the same frame with sd 0.12 to 0.25 | the human eye (law 6: judges flag, never grade) | [C], [L] |
| authorship | a chain re-stamped after a scene edit verifies (section 9); law 35: a signature proves a key, not an author | a key pinned outside the file; not built here | [C] |
| real-GPU behaviour | every frame in this chapter is SwiftShader; X_ITE reported 6.8 to 9.1 frames per second during the capture, which is not a speed claim | a named GPU and driver | [C] |
| the same answer in every host and on every machine | physics determinism claims are per step and per host on one machine (law 42) | a second machine's replay | [L] |
| two renderers that disagree | X_ITE blends ColorInterpolator in HSV, a three.js reader in RGB; translucency blends differ (failure modes 109, 115) | shape witnesses, never pixel hashes across renderers (law 38) | [L] |
| hints that over-report | one error, two hints (section 5) | re-validate after each applied fix | [C] |
| security of the oracle itself | the validator server parses with lxml defaults, so internal entities resolve; a threat check measured 16 defences and 3 gaps (failure mode 145) | parse with entity resolution off; the threat check | [L] |
| other pipelines | only X3D was measured; every other score here is a design expectation | measure one pipeline at a time | [S] |

## 9. History in the artifact: a sketch, and its limit

Leg 5 needs the record to travel inside the file. The Loom's own implementation is x3dprov 0.1 (a hash chain in `<head><meta>`, unsigned; read in LOOM-v1 section 5, the code is not read here). This sketch is written for the chapter, stdlib only, and is not x3dprov:

```python
import hashlib, json, re, sys   # chain.py: stdlib only; a sketch of leg 5, not x3dprov
META = re.compile(r'^[ \t]*<meta name="tether\.step\.\d+" content=\'[^\']*\'/>\n', re.M)
def sha(b): return hashlib.sha256(b if isinstance(b, bytes) else b.encode()).hexdigest()
def body(t): return META.sub("", t)                      # the bytes the chain binds
def steps(t): return [json.loads(m) for m in re.findall(r'<meta name="tether\.step\.\d+" content=\'([^\']*)\'/>', t)]
def digest(r): return sha(json.dumps({k: r[k] for k in sorted(r) if k != "step_sha256"}, sort_keys=True))
def stamp(t, actor, check, result):
    prev = steps(t); p = prev[-1]["step_sha256"] if prev else "0" * 64
    r = {"n": len(prev) + 1, "prev": p, "scene_sha256": sha(body(t)), "actor": actor, "check": check, "result": result}
    r["step_sha256"] = digest(r)
    return t.replace("  </head>", f'    <meta name="tether.step.{r["n"]}" content=\'{json.dumps(r, sort_keys=True)}\'/>\n  </head>', 1)
def verify(t):
    p, last = "0" * 64, None
    for i, r in enumerate(steps(t), 1):
        if r["n"] != i or r["prev"] != p or r["step_sha256"] != digest(r): return f"BROKEN CHAIN at step {i}"
        p, last = r["step_sha256"], r
    if last is None: return "NO CHAIN"
    return "OK" if last["scene_sha256"] == sha(body(t)) else "SCENE CHANGED AFTER LAST STEP"
if __name__ == "__main__": print(verify(open(sys.argv[1]).read()))
```

The scene needs a `<head>` with at least one `<meta>`. Stamp twice (the fork gate, then the render), then try four things:

| action | `verify` says | meaning | grade |
|---|---|---|---|
| nothing | `OK` | the last step names the scene bytes | [C] |
| edit `size="2 2 2"` to `size="9 9 9"` | `SCENE CHANGED AFTER LAST STEP` | drift is visible | [C] |
| edit `"valid"` to `"INVALID"` inside step 1 | `BROKEN CHAIN at step 1` | the history is tamper-evident | [C] |
| strip the chain, edit the scene, stamp both steps again | `OK` | no check ran on the 9 x 9 x 9 scene; the chain shows drift, not authorship | [C] |

The stamped scene still passes the fork gate (`valid True` at `x3d_mcp fork b4efcd3`), so the ledger is allowed by the standard **[C]**. Closing the last row needs a signature over the validator build, the report hash and the scene hash under a key pinned outside the file (law 35); that is stated as open in LOOM-v1 and is not built in this base **[L]**.

## 10. Decision procedure for a new pipeline

```text
  start: name the artifact and the writer
     |
     v
  Q2: can a program give an exact verdict (rule, place, same twice)?
     |-- no --> ledger only: record who, what, when, with hashes; stop here
     |-- yes
     v
  Q3: can you build one artifact that passes and fails in use (10 minutes)?
     |-- no  --> run a cohort of 50 and count; zero is evidence, record the denominator
     |-- yes --> choose the second instrument, set its floor, add a control that must FAIL
     v
  Q4/Q5: does the file travel? is someone named?
     |-- no/no --> gate + log table
     |-- yes   --> bind the ledger to a candidate hash; name the acceptor, the waivers
     v
  pin every number to an instrument string; add the loop; cap rounds; re-score per pin
```

| step | action | output you keep | grade of the method |
|---|---|---|---|
| 1 | one line: artifact, writer, who is asked later | the line | [S] |
| 2 | write the five quick-test results in one table | the score and its evidence | [S] |
| 3 | list candidate oracles; mark each exact or not; a judge model is never exact | the oracle choice | [S] |
| 4 | construct the valid-but-fails case; if none, run a cohort | one file or one count with its denominator | [S], method proven on X3D [C] |
| 5 | pick the second instrument, a floor, and a control that must fail | instrument string, floor, control id | [S] |
| 6 | decide what the ledger binds (the candidate hash, the pin, the witness status) | schema, location | [S] |
| 7 | name the acceptor, the waivable items and the cap | the profile | [S] |
| 8 | run, record the pin on every number, keep red runs | dated rows | [S] |

Worked example, not 3D: **model-written SQL migrations** (all points [S]). Q1 1 (generated), Q2 1 (a parser plus a dry run on a scratch copy; exact), Q3 1 (a valid migration can lock a large table), Q4 0 (the migration table already travels with the database), Q5 1 (a named database owner). Score 4: a loop with one cap (two rounds), a render-equivalent leg (run on a copy and record row counts and lock time), a ledger that binds the migration hash to the dry-run result, and a named acceptor. The first control that must fail is a migration known to lock the table: if the dry-run witness passes it, the witness is not a witness (law 19).

## Heuristics

| ID | Rule | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-TH-1 | Score a pipeline on the five questions before proposing a loop; under 3 gets a log table, and Q2 = 0 gets a ledger. | [S] | section 3; X3D 5 of 5, other families unmeasured | design rule; X3D legs [C] |
| H-TH-2 | Build the exact oracle first; a repair loop with no exact oracle repairs toward a guess. | [L] | LOOM-v1 law 15; model-free hints repair 96.5% (N-TH-4) | `x3d_mcp fork b4efcd3` |
| H-TH-3 | Run a render check even when the validator passes; "valid" does not say "visible". | [C] | 17.52% vs 0.00% non-background pixels, both valid (N-TH-1, N-TH-2) | `X_ITE 16.7.0`, Chromium 153, SwiftShader |
| H-TH-4 | Re-validate after every applied hint and treat hints as proposals. | [C] | one error, two hints; one fix, valid (D-TH-3) | `x3d_mcp fork b4efcd3` |
| H-TH-5 | Quote every repair rate with the validator commit, the seed and the library versions. | [C] | 15.0% became 14.1% with the same script (N-TH-5, N-TH-6) | `x3d_mcp fork 535fdac` and `b4efcd3` |
| H-TH-6 | Report detection on injected faults and false alarms on controls together, with denominators. | [C] | 13 of 13 injected, 0 of 24 controls flagged (N-TH-8, N-TH-10) | `x3d_mcp fork b4efcd3` |
| H-TH-7 | List the fault classes you did not inject; the first one you add may score zero. | [C] | a floating part passes 0 of 14 (N-TH-9) | `x3d_mcp fork b4efcd3` |
| H-TH-8 | Measure the model-free baseline before crediting a model with a repair gain. | [C] | hints alone repair 521 of 540 (N-TH-4); the model gain carried at [L] (N-TH-14) | `x3d_mcp fork b4efcd3` |
| H-TH-9 | Treat a scene that became valid by repair as unreviewed; diff it against the card or seed. | [C] | the seed returned exactly in 268 of 540; 15 by deleting an element (N-TH-7) | `x3d_mcp fork b4efcd3` |
| H-TH-10 | Keep the ledger inside the file, and never call a hash chain proof of authorship. | [C] | a re-stamped forgery verifies (D-TH-6) | chain sketch, section 9 |
| H-TH-11 | Bind every pass to the candidate hash, tests included, so an edit makes old passes stale. | [C] | `STALE_WITNESS` after adding a scene (D-TH-5) | `x3d.loom@162ab18` loomkit |
| H-TH-12 | Name an acceptor and write waivers with an owner and a date; a green row nobody owns is not a tether leg. | [L] | LOOM-v1 laws 6, 16, 43 | read, not run |
| H-TH-13 | State the tether line with its scope: structure and behaviour are held, appearance needs a browser and an eye. | [L] | LOOM-v1 section 1 | read |
| H-TH-14 | Do not copy the X3D score to another family; write it [S] until one pipeline there has been measured. | [S] | section 3 table | design rule |

## Drills

### D-TH-1 Score five pipelines
- **Level:** L1 (look it up)
- **Task:** Score these on the five questions and name the band: (a) a model writing glTF through an exporter, (b) a model writing Terraform plans, (c) a model drafting contract clauses, (d) a script generating X3D from CSV, (e) a person sketching on paper.
- **Verify:** compare with the section 3 table and the decision tree in section 10.
- **Answer:** (a) Q1 1, Q2 1, Q3 1, Q4 0, Q5 1: 4, loop if metadata can travel; (b) 1 1 1 0 1: 4, `plan` is the dry-run leg; (c) Q2 0: ledger, 3 at most; (d) Q1 0 to 1 (a script is repeatable but can be wrong), Q2 1, Q3 1, Q4 1, Q5 1: 4 to 5; (e) 1 point or less: log table. All are [S].
- **Checked:** not run

### D-TH-2 Valid but blank
- **Level:** L2 (run a tool and compare)
- **Task:** Build `visible.x3d` and `blank.x3d` from section 5, validate both with the fork gate, render both in X_ITE, and compute the non-background pixel fraction.
- **Verify:** the step 1 and step 2 commands in section 5.
- **Answer:** both `valid True`, stage `semantic`, 0 errors; fractions 0.1752 and 0.0000; unique colours 2 and 1.
- **Checked:** 2026-11-14, `x3d_mcp fork b4efcd3`; `X_ITE 16.7.0`, `Chromium 153 (Chrome for Testing 153.0.8010.12), SwiftShader`, 320 x 240

### D-TH-3 Read the hints, then break the loop
- **Level:** L2 (run a tool and compare)
- **Task:** Feed `hints.gate` the three variants in section 5 step 4. For the ROUTE case count errors and hints, then run `hints.repair_with_hints` and check `valid` and how many fixes it applied.
- **Verify:** `python3 -c` with `sys.path.insert(0, "src")` and `from validation.hints import gate, repair_with_hints` in a checkout of `x3d_mcp@b4efcd3`.
- **Answer:** `wrong-parent` (wrap `Shape`), `colour-out-of-range` (`1 0 0`), `route-before-def` (move to end of Scene, confidence exact); the ROUTE variant returns 1 error and 2 hints; the repair loop applies 1 fix (`ROUTE[1]`) and `valid` is True.
- **Checked:** 2026-11-14, `x3d_mcp fork b4efcd3`, lxml 6.1.3, libxml2 2.14.6

### D-TH-4 Move the pin
- **Level:** L3 (break it, fix it, extend it)
- **Task:** In a throwaway clone of `hagopjay/x3d_mcp`, run `python3 evaluation/exact_fix_eval.py --seed 20261029 --per-class 45` at `535fdac` and at `b4efcd3` (the script rewrites `evaluation/exact_fix/results.json`; discard it between runs). Compare the counts, then diff the `seeds` lists in the two `results.json` files and find out why one seed left.
- **Verify:** the printed summary lines; `results.json` key `seeds`; run `validation.hints.gate` on the dropped file at both commits.
- **Answer:** `535fdac`: 25 seeds, 15,651 sites, 570 errors, 81 / 523 / 522, 257 restored, 12 deleted. `b4efcd3`: 24 seeds, 10,294 sites, 577 errors, 76 / 522 / 521, 268, 15. The dropped seed is `examples/scenes/doha_qatar.x3d`; at `b4efcd3` its gate result has 2 semantic errors (`profile-component`, `array-count`). Extension: add a row to your own register instead of replacing the old one.
- **Checked:** 2026-11-14, `x3d_mcp fork 535fdac`, `ffbc20f`, `327c5c4`, `b4efcd3`; Python 3.13.18, lxml 6.1.3

### D-TH-5 Make the profile refuse a blank frame
- **Level:** L3 (break it, fix it, extend it)
- **Task:** Using section 5 step 3, accept a project that holds only `visible.x3d`, then add `blank.x3d` without re-running anything, then re-run the witnesses. Record the three outcomes and their codes. Extension: edit one line of your `eyes` adapter after a pass and re-run `accept`.
- **Verify:** `kit/loom accept` output and exit code (1 means a contract violation with a stable code).
- **Answer:** accepted (5 files); `STALE_WITNESS` (detail `grammar`, 6 files); after re-running, `WITNESS_NOT_PASS` (detail `eyes: fail`; grammar and traps pass). The extension gives `STALE_WITNESS` because the adapter is part of the candidate.
- **Checked:** 2026-11-14, `x3d.loom@162ab18` loomkit; `x3d_mcp fork b4efcd3`; `X_ITE 16.7.0`, `Chromium 153 ... SwiftShader`

### D-TH-6 Forge the ledger
- **Level:** L3 (break it, fix it, extend it)
- **Task:** Save `chain.py` from section 9. Stamp a small scene twice, verify it, edit the scene, edit step 1, then strip the chain, edit the scene and stamp again. Then extend the sketch so that the last step also carries an HMAC and say what that does and does not add.
- **Verify:** `python3 chain.py stamped.x3d` and the three tampered copies.
- **Answer:** `OK`; `SCENE CHANGED AFTER LAST STEP`; `BROKEN CHAIN at step 1`; the re-stamped forgery verifies `OK`. An HMAC with a key stored in the file or the source adds nothing (law 35: a key inside the envelope is forgeable); with a key held outside the file it binds the stamper to the key, still not to a person.
- **Checked:** 2026-11-14, `chain.py` as printed in section 9, Python 3.13.18; the stamped scene also passed `x3d_mcp fork b4efcd3` (`valid True`)

### D-TH-7 Detection against injected faults
- **Level:** L2 (run a tool and compare)
- **Task:** Take the 24 seed scenes of `exact_fix_eval.load_seeds(20261029)` at `b4efcd3`. For each seed that has a ROUTE, move its first ROUTE to the top of the Scene; for each seed that has a top-level Transform, set `translation="1000 0 0"` on the first one. Count what `validate_xml` alone flags and what `hints.gate` flags, and flag the unchanged seeds as controls.
- **Verify:** a 30-line script that parses with lxml, edits, serialises, and calls the two functions.
- **Answer:** controls flagged by the gate: 0 of 24. Route faults: 13 seeds; XSD alone 0, gate 13. Displacement: 14 seeds; XSD alone 0, gate 0. The second result is the blind spot, the first is the layer that closes the earlier one.
- **Checked:** 2026-11-14, `x3d_mcp fork b4efcd3`, lxml 6.1.3, libxml2 2.14.6

## Honest limits

- Only X3D was measured. Every score for another family (section 3, section 10) is a design expectation, [S].
- The paired model-run numbers (489 vs 507 of 540, 99 vs 87 of 115, AUC 0.997, 203 of 1,058) are carried from LOOM-v1; their measuring documents are not public and none was re-run, so they stay at [L]. No paid call was made for this chapter.
- `EXACT-FIX-HINTS.md` at `b4efcd3` says the model repair loop is not measured while LOOM-v1 reports it; the code supports the doc only for the model-free parts.
- The hint corpus is written by the author of the hint rules; its high coverage says the rules cover their own mutation classes ([L] that it carries to real model errors).
- The render check is one scene, one camera, 320 x 240, SwiftShader, a 1% floor chosen for this chapter. It detects "nothing drawn"; it does not detect "drawn wrong".
- The injected-fault runs use two fault classes on 24 seeds. 13 of 13 is a count, not a rate for real model errors.
- The over-reporting hint was seen once; its cause was not traced.
- The chain is a sketch. x3dprov (in a repository this base does not read) was read about, not run. Nothing here is signed.
- The loop was run on a single machine; nothing here says the same frames appear on a real GPU or another machine.
- Reading versus running: the six-property table and the tether line are read; sections 5, 7, 9 and drills D-TH-2 to D-TH-7 were run.
- Sources disagree in places: see the pin table (section 7) for the counts that moved between validator commits, and the model-loop status above.

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-TH-1 | non-background pixel fraction, `visible.x3d` | 0.1752 | [C] | `X_ITE 16.7.0`, Chromium 153, SwiftShader, 320 x 240 | section 5 (run 2026-11-14) |
| N-TH-2 | non-background pixel fraction, `blank.x3d` (valid, faces away) | 0.0000 | [C] | `X_ITE 16.7.0`, Chromium 153, SwiftShader, 320 x 240 | section 5 (run 2026-11-14) |
| N-TH-3 | scenes valid at the fork gate, of the two | 2 of 2 | [C] | `x3d_mcp fork b4efcd3` | section 5 (run 2026-11-14) |
| N-TH-4 | hint loop alone, repaired cases | 521 of 540 (96.5%) | [C] | `x3d_mcp fork b4efcd3`, seed 20261029 | `x3d_mcp@b4efcd3:evaluation/exact_fix_eval.py` (run 2026-11-14) |
| N-TH-5 | `repair_x3d` alone, repaired cases, at `b4efcd3` | 76 of 540 (14.1%) | [C] | `x3d_mcp fork b4efcd3`, seed 20261029 | `x3d_mcp@b4efcd3:evaluation/exact_fix_eval.py` |
| N-TH-6 | `repair_x3d` alone, repaired cases, at `535fdac` | 81 of 540 (15.0%) | [C] | `x3d_mcp fork 535fdac`, seed 20261029 | `x3d_mcp@535fdac:evaluation/exact_fix_eval.py` (run 2026-11-14) |
| N-TH-7 | hint loop gives the seed back exactly, at `b4efcd3` | 268 of 540 (49.6%); 15 valid only by deleting an element | [C] | `x3d_mcp fork b4efcd3` | `x3d_mcp@b4efcd3:evaluation/exact_fix_eval.py` |
| N-TH-8 | injected route faults caught, gate vs XSD alone | 13 of 13 vs 0 of 13 | [C] | `x3d_mcp fork b4efcd3`, 24 seeds | section 6 (run 2026-11-14) |
| N-TH-9 | injected displaced part caught | 0 of 14 | [C] | `x3d_mcp fork b4efcd3`, 24 seeds | section 6 (run 2026-11-14) |
| N-TH-10 | unchanged seeds flagged by the gate | 0 of 24 | [C] | `x3d_mcp fork b4efcd3` | section 6 (run 2026-11-14) |
| N-TH-11 | seeds, mutation sites, errors at `535fdac` and at `b4efcd3` | 25, 15,651, 570 and 24, 10,294, 577 | [C] | `x3d_mcp fork 535fdac` and `b4efcd3` | section 7 (run 2026-11-14) |
| N-TH-12 | fix operations used in the 540-case run at `b4efcd3` | `set_attribute` 290, `move` 127, `rename_element` 58, `remove_attribute` 29, `rename_attribute` 29, `remove_element` 15, `wrap` 10 | [C] | `x3d_mcp fork b4efcd3` | `x3d_mcp@b4efcd3:evaluation/exact_fix_eval.py` |
| N-TH-13 | hints for one broken ROUTE in the worked example | 2 hints for 1 error; 1 fix applied, valid True | [C] | `x3d_mcp fork b4efcd3` | section 5 step 4 (run 2026-11-14) |
| N-TH-14 | model repair with hints vs plain errors, first round | 507 vs 489 of 540; 31 gained, 13 lost; p 0.0096 | [L] | a hosted model, as reported | `x3d.loom@162ab18:LOOM-v1.md` section 7.1 |
| N-TH-15 | valid scenes that drew nothing; blank among valid | 203 of 1,058; 17 of 91 | [L] | as reported, not re-checked | `x3d.loom@162ab18:LOOM-v1.md` section 7.2, failure mode 91 |
| N-TH-16 | planted ROUTE-first faults caught before and after PR #15 | 0 to 200 of 200 | [L] | libxml2 2.14.6, fork 56809ca to the PR #15 change | `x3d_mcp@b4efcd3:docs/ROUTE-COLOUR-HANIM-CHECKS.md` |
| N-TH-17 | scenes in the fork's XSD-verdict corpus run | 2,857 (1,593 invalid, 1,264 valid), verdict unchanged | [L] | libxml2 2.14.6, as reported | `x3d_mcp@b4efcd3:docs/ROUTE-COLOUR-HANIM-CHECKS.md` |
| N-TH-18 | lawful metric AUC on recorded scenes | 0.997 on 383 | [L] | x3d.onto, as reported | `x3d.loom@162ab18:LOOM-v1.md` section 7.2 |
| N-TH-19 | chain forgery after a scene edit verifies | 1 of 1 | [C] | chain sketch, Python 3.13.18 | section 9 (run 2026-11-14) |
| N-TH-20 | doha seed gate errors at `535fdac` and `b4efcd3` | 1 and 2 semantic errors | [C] | `x3d_mcp fork 535fdac` and `b4efcd3` | section 7 (run 2026-11-14) |
| N-TH-21 | tether score of X3D | 5 of 5 | [L] | reasoned from the [C] rows above | section 3 |

## Sources and provenance

- `x3d.loom@162ab18` (main): `LOOM-v1.md` sections 1, 3, 6, 7, 8 read; `kit/loomkit/accept.py`, `cli.py`, `core.py` read and run; `LESSONS-v1.0.md` read. Run on a scratch copy; the checkout was not modified.
- `x3d_mcp@b4efcd3`: `docs/EXACT-FIX-HINTS.md`, `docs/ROUTE-COLOUR-HANIM-CHECKS.md`, `evaluation/exact_fix_eval.py`, `src/validation/hints.py` read; the eval and the gate run on scratch copies at `535fdac`, `ffbc20f`, `327c5c4` and `b4efcd3`.
- `x3d.docs@f172f67`: `docs/vendor/x_ite/x_ite.min.js` (header `X_ITE v16.7.0`, sha256 prefix b7df063e8cb1) used for the render; `docs/x3d.loom/MASTERCLASS.md` read for orientation.
- Date read and run: 2026-11-14. The tether score as a five-question method was found in a private working note and is restated here as a design rule at [S]; no figure from that note is used. Other private-source gaps are not linked.
- Sibling chapters: [02 the Loom laws](02-loom-laws.md), [03 validator and gates](03-validator-and-gates.md), [04 MCP for agents](04-mcp-for-agents.md), [06 X_ITE the oracle](06-xite-the-oracle.md), [11 glTF, USD and Khronos](11-gltf-usd-khronos.md).
