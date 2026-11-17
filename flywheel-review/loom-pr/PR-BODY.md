# LOOM-v1: three text defects fixed, and failure modes joined to laws by number

Three commits on branch `atlas/loom-v1-ids`. Base: `hagopjay/x3d.loom` main at `ba30153`, fetched 17 November 2026 (02:00 UTC).

**Numbers claimed, checked against that commit:** no new law and no new failure mode. Still 44 laws and 160 failure modes. One file changes, `LOOM-v1.md`: 3 lines in patch 1, 13 in patch 2, 49 in patch 3 (64 distinct lines; section 8's opening line is touched twice).

## Why

A graph was compiled from `LOOM-v1.md` and the learning base (the Atlas, local). It showed that 95 of the 160 failure modes are tied to no law by number, and 12 laws cite no failure mode by number: the laws and the failures are joined mostly by prose. It also tripped on three places where the text breaks a table or names an id ambiguously. This draft fixes those three and writes joins into the cells, each with its grade.

## The three patches

They apply in order (`git apply --check` passes for each on the base). Take 1 alone, 1 and 2, or all three.

### 1. `01-defects.patch` (3 lines)

| where | now | becomes | why |
|---|---|---|---|
| failure mode 87 | `(expected ~ \|t - t_r\|^1/2)` with bare pipes | the two pipes escaped | GitHub cuts the Failure cell at "(expected ~", shows `t - t_r` as the fix, and drops the real fix and source. Rendered through GitHub's markdown API before and after: the cell is complete after the change |
| failure mode 147 | "upstream at law 40 and 123" | "upstream at law 40 and failure mode 123" | there is no law 123; the sentence pairs a law with a failure mode, as its first half does |
| law 32, paid for by | "(C, 78)" | "(C, failure mode 78)" | a bare number; the clause before it writes "failure mode 88" |

### 2. `02-joins-same-incident.patch` (13 lines): grade L

A law and a failure row that name the same incident now cite each other: `failure mode N` in the law's *Paid for by*, `(law N)` at the end of the failure's *Fix*. The basis is the two rows themselves (same source id, same event). The sources (`LEC`, `LS1`, `XTD`) were **not** opened, so this is a reading of `LOOM-v1.md`, not of its sources. Section 8's opening line gains one sentence saying so.

| law | failure mode | basis |
|---|---|---|
| 2. Valid is not visible | 1. Valid X3D draws white: raw GLSL in a ShaderPart is read as a URL | both cite LEC 1 for a valid scene that draws white |
| 7. Every mistake pays rent once | 1. Valid X3D draws white: raw GLSL in a ShaderPart is read as a URL | the law's incident is the trap shader-raw-source, which is failure mode 1's fix |
| 9. The metric will be attacked | 11. Optimiser declares profile Full | both cite LEC 8 for the optimiser that declares profile Full |
| 17. Evidence is bound to the exact candidate | 12. Old browser pass authorises changed code | both cite LS1 A01: a stale browser pass authorised changed code |
| 18. A gate is code that cannot be switched off | 13. python -O strips asserts; red gate packages | both cite LS1 A02 and IFC: asserts stripped under -O |
| 34. Every result states its scope and its reproduction level | 89. X_ITE's replaceWorld can leave the caller's promise pending when an internal… | the law cites the teardown's F01 record; failure mode 89's source is that record |
| 32. The runtime's contracts are part of the build | 78. A hash change that arrived while the X3D scene was loading reached the case l… | the law's evidence already names it; patch 1 writes out 'failure mode 78' |

### 3. `03-joins-readings.patch` (49 lines): grade S

48 failure rows gain `(law N, S)` at the end of their *Fix*. Each is my judgment that the failure is a case of what the law's *Forbids* column describes. Law 6 says a model's sentence enters the record as S, so each carries the mark; confirm one by deleting `, S`, strike one by deleting the parenthesis. The same sentence in section 8 says this.

| failure mode | law | why |
|---|---|---|
| 2. Valid X3D, invalid GLSL (active reserved) | 2. Valid is not visible | valid X3D, invalid GLSL: a case of shipping on '0 errors' |
| 27. Metadata valid but unattached | 2. Valid is not visible | metadata valid but unattached at runtime |
| 3. ROUTE before its node: fork passes, X_ITE drops | 2. Valid is not visible; 7. Every mistake pays rent once | the fork passes and X_ITE drops the ROUTE (law 2); the fix is a trap rule (law 7) |
| 57. Component declared by name only; X_ITE ignores levels, so TextureProperties (… | 3. Many witnesses, blind spots that don't overlap | the browser passed what the Meaning witness refuses: two witnesses, different blind spots |
| 73. A node outside the profile (PhysicalMaterial needs Shape level 2) loaded in X… | 3. Many witnesses, blind spots that don't overlap | loaded in X_ITE, refused by the Meaning witness |
| 102. The X3D 4.0 schema gives PointSet no vertex attributes, though X_ITE accepts… | 3. Many witnesses, blind spots that don't overlap | X_ITE draws what the XSD refuses; the fix runs both |
| 141. The XSD passed while the semantic validator found 5 errors per scene: Metadat… | 3. Many witnesses, blind spots that don't overlap | the XSD passed while the semantic validator found errors; the fix runs both |
| 44. Rebuild on another platform: PNG bytes and last-bit floats differ while conte… | 4. If you can't make it again, you don't know what it is | the platform was an undeclared input of the rebuild |
| 4. Colour above 1: XSD error blames something else | 7. Every mistake pays rent once | the fix is a trap rule |
| 5. White emissive washes out coloured faces | 7. Every mistake pays rent once | the fix is a trap rule |
| 8. Still PNG in MovieTexture hangs the world | 7. Every mistake pays rent once | the fix is a trap rule |
| 9. GaussianSplats culled never sorts, loading never ends | 7. Every mistake pays rent once | the fix is a trap rule |
| 109. One file, two renderers, different night skies: X_ITE blends ColorInterpolato… | 7. Every mistake pays rent once | the fix is a trap rule |
| 110. A light faded to intensity 0 kept its ambient term to the end, then vanished:… | 7. Every mistake pays rent once | the fix is a trap rule |
| 111. A fully transparent shape cast a shadow: X_ITE draws it into the shadow map | 7. Every mistake pays rent once | the fix is a trap rule |
| 112. The picture jumped at every loop: interpolators on a looping clock ended away… | 7. Every mistake pays rent once | the fix is a trap rule |
| 113. A 4K still button rendered the image and saved nothing: the hosting sandbox i… | 7. Every mistake pays rent once | the fix is a page trap rule |
| 24. CPU time renamed GPU time; idle frames called fps | 15. Name the instrument behind every number | CPU time called GPU time, idle frames called fps: a number without its instrument |
| 42. Validator pins spread over five fork commits | 15. Name the instrument behind every number | verdicts spread over five validator commits: unpinned verdicts |
| 47. Stale "valid X3D" badge shown on changed bytes | 17. Evidence is bound to the exact candidate | a 'valid' badge shown on changed bytes; the fix rebinds claims to the current bytes |
| 55. Admission gate written as assert: red passes under -O (recurred in a new proj… | 18. A gate is code that cannot be switched off | the recurrence of failure mode 13: a gate that vanishes under -O |
| 66. A negative control that cannot fail proves nothing: at a mirror-symmetric vie… | 19. A control must fail for the intended reason | a negative control that could not fail at a symmetric view |
| 96. An output field that no control checked was wrong from the day it shipped: js… | 19. A control must fail for the intended reason | controls checked that a rule fired, not what it reported |
| 71. A display precision fixed in advance failed one case (shallow gradients) and… | 23. Display precision is part of the scientific budget | a display precision fixed in advance failed its witness |
| 142. An engine was cross-checked against itself: native MuJoCo replayed the browse… | 25. Independent witnesses need independent assumptions | an engine cross-checked against itself: no independent assumption |
| 19. Diagnostic colours contaminated by overlays | 26. Suspect the witness first | the witness read its own overlays |
| 20. Image difference came from UI, not the scene | 26. Suspect the witness first | the image difference came from the UI, not the scene |
| 30. Loading overlay made an empty frame look full | 26. Suspect the witness first | a loading overlay made an empty frame look full |
| 85. A detector with the wrong geometry: the vortex-cell marker flagged neighbours… | 26. Suspect the witness first | a detector with the wrong geometry, trusted before a known-answer test |
| 108. Witnesses that measured their sampling or their renderer: curve agreement by… | 26. Suspect the witness first | witnesses that measured their own sampling or renderer |
| 124. A stepped engine was judged against the continuum answer and looked wrong by… | 27. Like with like | a stepped engine judged against the continuum answer: unlike with unlike |
| 59. An analytic approximation (CIE colour matching) failed its declared gate in t… | 28. Explore the worst case before declaring a limit; then fix the instrument, not the threshold | an approximation failed its gate; the fix forbids widening the threshold after the run |
| 7. X_ITE has no public scene clock | 31. One clock, one owner | X_ITE has no public scene clock; the fix gives time one owner |
| 131. Scene clocks ran ahead while physics lagged under load, and 60 fps was claime… | 31. One clock, one owner | scene clocks ran ahead of physics; the fix makes clocks follow physics |
| 49. Textures resolved against the HTML page, not the scene URL: 39 silently missi… | 32. The runtime's contracts are part of the build | page code assumed textures resolve against the scene URL |
| 61. CSS display overrode the hidden attribute, so a loading veil dimmed every fra… | 32. The runtime's contracts are part of the build | page code assumed the hidden attribute wins over CSS display |
| 77. A top-level const top in a classic page script collides with the browser's wi… | 32. The runtime's contracts are part of the build | a page global collided with the browser's window.top |
| 84. Screenshots taken right after a viewpoint change caught X_ITE's default one-s… | 32. The runtime's contracts are part of the build | evidence code assumed a viewpoint change is instant; X_ITE glides for a second |
| 101. A hidden page does not run: X_ITE does not start in a hidden pane or tab, whe… | 32. The runtime's contracts are part of the build | page code assumed X_ITE starts in a hidden tab |
| 104. Two animation-frame loops raced: a post pass read X_ITE's canvas between a cl… | 32. The runtime's contracts are part of the build | a post pass assumed when X_ITE's canvas holds a drawn frame |
| 117. After switching renderers and back, the view stayed black: the old canvas's c… | 32. The runtime's contracts are part of the build | a context-lost handler assumed it spoke for the current canvas |
| 118. Tearing X_ITE down to free memory threw inside X_ITE ("reading '0'" of null) | 32. The runtime's contracts are part of the build | page code assumed X_ITE can be torn down |
| 130. WebKit's createX3DFromString stalls without a word | 32. The runtime's contracts are part of the build | page code assumed createX3DFromString settles in WebKit |
| 144. Behaviour ran on browser defaults that cannot run the page: headless Chromium… | 32. The runtime's contracts are part of the build | tests assumed the default headless browser can run the page |
| 58. python -I dropped the builder's own directory from sys.path (a second time, a… | 33. Read your own checklist | the -I trap of failure mode 43, hit a second time |
| 81. A sign convention emptied a witness: the strain phase ran backwards, every fr… | 36. A pass names what it saw | an empty sample passed vacuously: a pass that saw nothing |
| 92. My own hardening script left '}););' in the vortex page: the page never ran,… | 36. A pass names what it saw | a page that never ran passed every pattern rule |
| 126. The default 2 cm contact offset hid a 5 mm wall from a 5 m/s marble, so a CCD… | 44. A check is shown able to fail, and a number is not Confirmed until a second reader has tried to break it | a CCD-on test alone proved nothing; the fix keeps a control that must fail |

Ten of these are one rule applied evenly: where the fix is a trap rule, the row cites law 7 (every mistake pays rent once). Ten more put browser and X_ITE surprises under law 32 (the runtime's contracts are part of the build); that is the widest reading here and the first to question.

## Measured effect

The Atlas builder was run on the file at each stage (`ATLAS_LOOM=stageN.md`; chapters from `x3d.docs@ff0565e` unchanged).

| stage | failure modes tied to no law | laws citing no failure mode | law-failure citations | text findings |
|---|---|---|---|---|
| base | 95 | 12 | 75 | 2 |
| after patch 1 | 94 | 12 | 76 | 0 |
| after patch 2 | 90 | 9 | 88 | 0 |
| after patch 3 | 42 | 8 | 137 | 0 |

"Tied" counts a citation in either direction, including those chapter 02 of the learning base already makes. Every row of the two tables still splits into four cells at each stage.

## Not done, and limits

- **42 failure modes stay loose**: 14, 15, 16, 17, 18, 21, 22, 23, 25, 26, 28, 29, 32, 34, 35, 37, 38, 39, 43, 45, 48, 50, 60, 62, 63, 74, 75, 83, 90, 107, 119, 120, 125, 134, 135, 136, 138, 139, 140, 143, 145, 146. I saw no law they plainly fall under; several may deserve a law of their own (for example 62 and 63 on numerics, 134 to 136 on articulation limits).
- **8 laws still cite no failure mode**: 1, 5, 6, 10, 14, 16, 20, 35. Their incidents are named by source only.
- No source document was opened. A same-incident join could be wrong if two incidents share a source id.
- Nothing was run from the kit. `kit/` and the three workflows were searched for code that reads `LOOM-v1.md`; only prose references were found.
- `x3d.docs` chapter 02 quotes these tables at `x3d.loom@162ab18`. It is unaffected until its pin moves; then its counts of joins change.
- `(law N, S)` is new notation in this file. If you would rather keep section 8 free of S marks, drop patch 3 and keep its table as a worklist.

## How to check

```bash
git apply --check 01-defects.patch && git apply 01-defects.patch      # then 02, then 03
grep -c '(law[s]* [0-9 and]*, S)' LOOM-v1.md                          # 48 after patch 3
python3 - <<'PY'                                                       # every law and failure row has four cells
import re
text = open('LOOM-v1.md', encoding='utf-8').read()
bad = total = 0
for head in ('## 3. The laws', '## 8. Known failure modes'):
    body = text.split(head, 1)[1].split('\n## ', 1)[0]
    for l in body.splitlines():
        if re.match(r'^\| \d+ \| ', l):
            total += 1
            bad += len(re.split(r'(?<!\\)\|', l.strip())) != 6
print(bad, 'rows that do not split into four cells, of', total)   # 0 of 204
PY
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)
