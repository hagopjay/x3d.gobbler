#!/usr/bin/env python3
"""Draft three patches to LOOM-v1.md from the x3d.loom clone at HEAD. Writes patches and stage files here; edits nothing else.

  01-defects.patch               three places where the text breaks a table or names an id ambiguously
  02-joins-same-incident.patch   a law and a failure row that name the same incident cite each other (grade L)
  03-joins-readings.patch        a failure that is a case of what a law forbids gets "(law N, S)": a model's reading
"""
import difflib
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
CLONE = HERE.parent / "src" / "x3d.loom"
base_sha = subprocess.run(["git", "-C", str(CLONE), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
base = subprocess.run(["git", "-C", str(CLONE), "show", "HEAD:LOOM-v1.md"], capture_output=True, text=True).stdout


def cells(line):
    return re.split(r"(?<!\\)\|", line)


def edit_line(text, starts, old, new):
    """Replace old with new exactly once, in the one line that starts with `starts`."""
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(starts)]
    assert len(hits) == 1, (starts, len(hits))
    assert lines[hits[0]].count(old) == 1, (starts, old, lines[hits[0]].count(old))
    lines[hits[0]] = lines[hits[0]].replace(old, new)
    return "\n".join(lines)


def fm_line(text, n):
    lines = text.split("\n")
    a = next(i for i, l in enumerate(lines) if l.startswith("## 8. Known failure modes"))
    b = next(i for i in range(a + 1, len(lines)) if lines[i].startswith("## "))
    hits = [i for i in range(a, b) if re.match(rf"^\| {n} \|", lines[i])]
    assert len(hits) == 1, (n, hits)
    return lines, hits[0]


def cite(text, n, laws, grade=None):
    """Append '(law N)' or '(laws N and M, S)' to the Fix cell of failure mode n."""
    lines, i = fm_line(text, n)
    parts = cells(lines[i])
    assert len(parts) == 6, (n, len(parts))
    for law in laws:
        assert not re.search(rf"\blaws? [\d, and]*\b{law}\b", parts[3]), (n, law, "already cited")
    word = ("law " + str(laws[0])) if len(laws) == 1 else ("laws " + " and ".join(map(str, laws)))
    parts[3] = parts[3].rstrip() + f" ({word}{', ' + grade if grade else ''}) "
    lines[i] = "|".join(parts)
    return "\n".join(lines)


# ---- 1. defects ---------------------------------------------------------------------------------
s1 = edit_line(base, "| 87 |", "(expected ~ |t - t_r|^1/2)", r"(expected ~ \|t - t_r\|^1/2)")
s1 = edit_line(s1, "| 147 |", "upstream at law 40 and 123", "upstream at law 40 and failure mode 123")
s1 = edit_line(s1, "| 32 | **", "(C, 78)", "(C, failure mode 78)")

# ---- 2. the same incident, named at both ends (L) ------------------------------------------------
SAME = [  # (law, failure mode, text in the law's cell, its replacement, why)
    (2, 1, "valid and white (C, [LEC 1])", "valid and white (C, [LEC 1], failure mode 1)",
     "both cite LEC 1 for a valid scene that draws white"),
    (7, 1, "in a day (C, [LEC 6])", "in a day (C, [LEC 6], failure mode 1)",
     "the law's incident is the trap shader-raw-source, which is failure mode 1's fix"),
    (9, 11, "declared Full (L, [LEC 8])", "declared Full (L, [LEC 8], failure mode 11)",
     "both cite LEC 8 for the optimiser that declares profile Full"),
    (17, 12, "exit 0 (C, [LS1 §9 A01])", "exit 0 (C, [LS1 §9 A01], failure mode 12)",
     "both cite LS1 A01: a stale browser pass authorised changed code"),
    (18, 13, "under `-O` (C, [LS1 §9 A02])", "under `-O` (C, [LS1 §9 A02], failure mode 13)",
     "both cite LS1 A02 and IFC: asserts stripped under -O"),
    (34, 89, "F01/F02 records (L, [XTD §1, §9])", "F01/F02 records (L, [XTD §1, §9]; F01 is failure mode 89)",
     "the law cites the teardown's F01 record; failure mode 89's source is that record"),
    (32, 78, None, None, "the law's evidence already names it; patch 1 writes out 'failure mode 78'"),
]
s2 = s1
for law, fm, old, new, why in SAME:
    if old:
        s2 = edit_line(s2, f"| {law} | **", old, new)
by_fm = {}
for law, fm, *_ in SAME:
    by_fm.setdefault(fm, []).append(law)
for fm, laws in sorted(by_fm.items()):
    s2 = cite(s2, fm, sorted(laws))
INTRO = "Each row is a trap someone paid for. The fix is the v1 rule; LEARNINGS-from-patches.md has the longer account."
L_NOTE = (" A trailing `(law N)` names the law a failure falls under; where it was added on 17 November 2026 it is a reading (L): "
          "the law's own evidence names the same incident.")
assert s2.count(INTRO) == 1
s2 = s2.replace(INTRO, INTRO + L_NOTE)

# ---- 3. readings: the failure is a case of what the law forbids (S) -------------------------------
READ = {  # failure mode: ([laws], why)
    2: ([2], "valid X3D, invalid GLSL: a case of shipping on '0 errors'"),
    3: ([2, 7], "the fork passes and X_ITE drops the ROUTE (law 2); the fix is a trap rule (law 7)"),
    27: ([2], "metadata valid but unattached at runtime"),
    57: ([3], "the browser passed what the Meaning witness refuses: two witnesses, different blind spots"),
    73: ([3], "loaded in X_ITE, refused by the Meaning witness"),
    102: ([3], "X_ITE draws what the XSD refuses; the fix runs both"),
    141: ([3], "the XSD passed while the semantic validator found errors; the fix runs both"),
    44: ([4], "the platform was an undeclared input of the rebuild"),
    4: ([7], "the fix is a trap rule"), 5: ([7], "the fix is a trap rule"), 8: ([7], "the fix is a trap rule"),
    9: ([7], "the fix is a trap rule"), 109: ([7], "the fix is a trap rule"), 110: ([7], "the fix is a trap rule"),
    111: ([7], "the fix is a trap rule"), 112: ([7], "the fix is a trap rule"), 113: ([7], "the fix is a page trap rule"),
    24: ([15], "CPU time called GPU time, idle frames called fps: a number without its instrument"),
    42: ([15], "verdicts spread over five validator commits: unpinned verdicts"),
    47: ([17], "a 'valid' badge shown on changed bytes; the fix rebinds claims to the current bytes"),
    55: ([18], "the recurrence of failure mode 13: a gate that vanishes under -O"),
    66: ([19], "a negative control that could not fail at a symmetric view"),
    96: ([19], "controls checked that a rule fired, not what it reported"),
    71: ([23], "a display precision fixed in advance failed its witness"),
    142: ([25], "an engine cross-checked against itself: no independent assumption"),
    19: ([26], "the witness read its own overlays"), 20: ([26], "the image difference came from the UI, not the scene"),
    30: ([26], "a loading overlay made an empty frame look full"),
    85: ([26], "a detector with the wrong geometry, trusted before a known-answer test"),
    108: ([26], "witnesses that measured their own sampling or renderer"),
    124: ([27], "a stepped engine judged against the continuum answer: unlike with unlike"),
    59: ([28], "an approximation failed its gate; the fix forbids widening the threshold after the run"),
    7: ([31], "X_ITE has no public scene clock; the fix gives time one owner"),
    131: ([31], "scene clocks ran ahead of physics; the fix makes clocks follow physics"),
    49: ([32], "page code assumed textures resolve against the scene URL"),
    61: ([32], "page code assumed the hidden attribute wins over CSS display"),
    77: ([32], "a page global collided with the browser's window.top"),
    84: ([32], "evidence code assumed a viewpoint change is instant; X_ITE glides for a second"),
    101: ([32], "page code assumed X_ITE starts in a hidden tab"),
    104: ([32], "a post pass assumed when X_ITE's canvas holds a drawn frame"),
    117: ([32], "a context-lost handler assumed it spoke for the current canvas"),
    118: ([32], "page code assumed X_ITE can be torn down"),
    130: ([32], "page code assumed createX3DFromString settles in WebKit"),
    144: ([32], "tests assumed the default headless browser can run the page"),
    58: ([33], "the -I trap of failure mode 43, hit a second time"),
    81: ([36], "an empty sample passed vacuously: a pass that saw nothing"),
    92: ([36], "a page that never ran passed every pattern rule"),
    126: ([44], "a CCD-on test alone proved nothing; the fix keeps a control that must fail"),
}
s3 = s2
for fm, (laws, why) in sorted(READ.items()):
    s3 = cite(s3, fm, laws, "S")
S_NOTE = (" Marked `S`, it is a model's judgment that the failure is a case of what the law forbids; the owner confirms it by "
          "deleting the mark, or strikes it.")
s3 = s3.replace(INTRO + L_NOTE, INTRO + L_NOTE + S_NOTE)


def patch(a, b, name):
    d = "".join(difflib.unified_diff(a.splitlines(True), b.splitlines(True), "a/LOOM-v1.md", "b/LOOM-v1.md", n=1))
    (HERE / name).write_text(d, encoding="utf-8")
    return sum(1 for l in d.splitlines() if l.startswith("+") and not l.startswith("+++"))


n1 = patch(base, s1, "01-defects.patch")
n2 = patch(s1, s2, "02-joins-same-incident.patch")
n3 = patch(s2, s3, "03-joins-readings.patch")
for name, text in (("stage0-base.md", base), ("stage1.md", s1), ("stage2.md", s2), ("stage3.md", s3)):
    (HERE / name).write_text(text, encoding="utf-8")
# every row of the two tables still has four cells
for stage, text in (("1", s1), ("2", s2), ("3", s3)):
    bad = [l[:20] for l in text.split("\n") if re.match(r"^\| \d+ \|", l) and len(cells(l)) != 6
           and not l.startswith("| Date")]
    print(f"stage {stage}: rows with a cell count other than 4: {bad[:6]}")
print(f"base {base_sha[:7]}; lines changed: defects {n1}, same incident {n2}, readings {n3}")
import json
(HERE / "joins.json").write_text(json.dumps({"base": base_sha, "same_incident": [[l, f, w] for l, f, _, _, w in SAME],
                                             "readings": {str(k): v for k, v in READ.items()}}, indent=1) + "\n")
