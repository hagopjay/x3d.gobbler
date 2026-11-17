# The Atlas, version 0

One graph of what the X3D Loom family already knows by id: laws, failure modes, numbers, heuristics, drills,
instruments, pins and the claim ledgers. Built on 16 and 17 November 2026. Local files; nothing was pushed.

| input | pin | what is read |
|---|---|---|
| `x3d.loom` | `ba30153` (main, 17 Nov) | `LOOM-v1.md` sections 3, 8 and 10. Byte-identical to the copy at `7a7d657`, the first pin |
| `x3d.docs` | `ff0565e` (gh-pages, 17 Nov) | `docs/learn`: 23 chapters, appendices A, C to G, `claims/*.jsonl`, `claims/receipt.json` |

The pins live in `src/LOOM.sha` and `src/DOCS.sha`. The first build (16 Nov) read `x3d.docs@3aab064`, 21 chapters.

## Run it

```bash
PY=~/Projects/x3d/x3d_mcp/.venv/bin/python     # any Python 3.11+ with rdflib 7 works for the witness
$PY build_atlas.py      # standard library only; writes out/
$PY check_atlas.py      # the witness; writes out/receipt.json   (--offline reads cache/ only)
$PY report.py           # writes out/FINDINGS.md from findings.json and receipt.json
$PY fly_atlas.py        # writes out/atlas-world.x3d and out/atlas-panel.json (run check_atlas.py again after)
python3 -m http.server 8823 --bind 127.0.0.1    # then open http://localhost:8823/fly.html
```

| file in `out/` | what it is |
|---|---|
| `atlas.jsonld`, `atlas.ttl` | the graph, in two formats that parse to the same triples |
| `atlas-vocab.ttl` | the 21 classes and the properties, with a sentence each |
| `atlas.json` | the same nodes, plus every edge with the column it was read from |
| `atlas-claims.jsonl` | the Atlas's own claim ledger (`claims/0.1`): one quote per copied value |
| `findings.json`, `FINDINGS.md` | what could not be resolved, and what the graph shows |
| `receipt.json` | the witness results and the sha256 of each output |
| `atlas-world.x3d`, `atlas-panel.json` | the walkable scene (X3D 4.0, Immersive, no Script) and the panel answers for its 1,366 sensors |

## Ask it

```bash
$PY atlas.py laws-for ShaderPart shader      # kickoff: the laws, failure modes and traps that apply
$PY atlas.py what-broke "python -O|assert"   # failure modes by pattern, with fix, class, laws, recurrences
$PY atlas.py how-do-we-know N-TRC-1          # value, grade, instrument, pins, ledger quotes, caveats, permalink
$PY atlas.py how-do-we-know "law 15"
$PY atlas.py stands-on "X_ITE 16.6.0"        # the numbers that stand on a tool version or a pin
$PY atlas.py worklist                        # what the graph says is thin
```

Each takes `--json`. Those answers are the shape three small `x3d_mcp` tools would return (`laws_for`,
`what_broke`, `how_do_we_know`); nothing was added to `x3d_mcp`.

With SPARQL (any RDF store, or `sparql_scene`-style tooling over `atlas.ttl`):

```sparql
PREFIX a: <https://x3datlas.example/0#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# Confirmed numbers that stand on X_ITE 16.6.0 and have no verified quote
SELECT ?n WHERE {
  ?n a a:Number ; a:grade <grade/C> ; a:resolvedInstrument/a:usesTool ?tv .
  ?tv rdfs:label "X_ITE 16.6.0" .
  FILTER NOT EXISTS { ?c a:supports ?n ; a:verdict "verified" }
}
```

## Fly it

`fly.html` opens `out/atlas-world.x3d` in the vendored X_ITE 16.7.0 and adds a "how do we know?" panel. The scene
itself is plain X3D: every item is a shape with a `TouchSensor` whose `description` names it, so any X3D browser
can show it; the page only listens to those sensors and prints the same answer `atlas.py how-do-we-know` gives.

| where | what you see | what it encodes |
|---|---|---|
| centre | a mast with five rings and threads | X_ITE versions; one thread to every number that stands on each (100) |
| courtyard | loose stones in eleven groups | the 95 failure modes tied to no law, by class K1 to K11 |
| ring | 44 columns, by theme A to J | laws: height grows with linked failure modes; teal has a mechanical check, amber has review only; white collars count diagnostics; a path of stones leads to each law |
| arms | 23 gates with three shelves | numbers on the ground (green C, amber L, pink S; small when the instrument is "same"; a gold plate when a ledger quote is verified), heuristics above (faint when the evidence cites no id), drills on top (red when not run) |
| lines | white and gold | white where one row cites another by id; gold from a quoted number to the pin its quote was read at |

Seven viewpoints, three layer switches, and a find box (`N-TH-4`, `law 15`, `fm 88`). One clock: the gold of a
verified quote breathes.

Checked on 17 Nov: the witness (5 more checks, 19 in all) confirms the scene rebuilds to the same bytes, carries the
sha256 of the `atlas.json` it was drawn from, has one sensor and one panel answer per row, has no Script, and is
XSD valid with 0 semantic errors and 0 warnings in `x3d_mcp`. That validator is the local checkout at `fa0b389`
(17 Oct), not today's fork main. In X_ITE 16.7.0, in the app's browser pane on this Mac, the page resolved 1,366 of
1,366 sensors with no console error, and hover, click, viewpoints and the find box worked. That is seen in
screenshots; no pixel fraction or frame time was measured, and no other X3D browser was tried.

## The model

Nodes: `Law` 44, `FailureMode` 160, `FailureClass` 11, `Theme` 10, `Diagnostic` 35, `TrapRule` 11,
`OpenQuestion` 18, `Chapter` 23, `Number` 591, `Heuristic` 359, `Drill` 177, `Claim` 84, `Instrument` 355,
`Tool` 68, `ToolVersion` 84, `Pin` 66, `Repo` 10, `SourceDocument` 37, `Source` 34, `Grade` 3, `Dataset` 1.

| edge | from, to | read from |
|---|---|---|
| `paidForBy` | law, failure mode | "failure mode N" in the law's *Paid for by* (LOOM-v1) or *evidence* (chapter 02) |
| `fixedByLaw` | failure mode, law | "law N" in the failure's *Fix* column |
| `caughtBy` | law or failure mode, diagnostic | a `code:` check in chapter 02; a code named in a fix |
| `hasTrap`, `recurredAs`, `inClass`, `topOfClass`, `inTheme` | | LOOM-v1 section 8 and chapter 02 |
| `measuredWith` | number, instrument | the instrument string exactly as written |
| `resolvedInstrument` | number, instrument | the same, after following `same` to the nearest explicit row above (marked inferred) |
| `usesTool`, `ofTool`, `atPin`, `ofRepo` | | parts of an instrument, source or *Checked* cell that name a tool version or `repo@sha` |
| `evidencedBy` | heuristic, any id | ids in the *Evidence* column |
| `supports` | claim, number or heuristic | `claims/*.jsonl`; the verdict comes from `claims/receipt.json` |
| `carriedFrom` | row, row | the ledger's `from` |
| `prov:wasQuotedFrom` | row or claim, `SourceDocument` | the file at the commit it was copied from |
| `mentions`, `citesPin`, `requires`, `citesSource`, `grade`, `inChapter` | | any other stable id, pin, prerequisite, source tag |

Choices that follow what landed in the family on 16 and 17 November:

- **Namespace.** A placeholder, `https://x3datlas.example/0#`, the convention `x3d.ML` set for `x3dprov`
  (`https://x3dprov.example/0.1#`): a registered namespace is the owner's call. One constant in `build_atlas.py`.
- **Quotes.** `prov:wasQuotedFrom` to a `SourceDocument` (`repo@sha:path`), as `x3dprov_provo.py` does for a quote.
- **Claims.** The chapter ledgers of `x3d.docs` (`claims/0.1`, chapter 23) are nodes, with the checker's verdict words
  (`verified`, `check`, `reworded`, `unchecked`) taken from the receipt, never recomputed here.
- **The Atlas's own ledger.** For every row it copies, the builder writes a `claims/0.1` line: the value's first
  20 words, a quote of at most 38 words from the same source line, the file at the pinned commit, the line.
  `check_atlas.py` hands these to `x3d.docs`' own `claims_lib.check_entry` with strict pins.

## The witness

`check_atlas.py`, 14 checks, all green on 17 Nov: the rebuild is byte-identical; every count equals what the
appendices state about themselves (19 rows, no number typed into the builder); Turtle and JSON-LD parse to the
same 23,273 triples in rdflib; every class and property is declared; four figures agree between the builder's
Python and SPARQL over the Turtle file; **1,360 of 1,360 Atlas claims verified at their pinned commits** by the
family's checker; and three planted faults (wrong value, wrong line, invented quote) are each rejected.

This proves the Atlas says what the ledgers say. It does not re-run a number, and it does not prove a ledger right.

## One judgment left to the owner

`policy.py: kickoff_rank()` orders the laws in a `laws-for` answer. The default lifts laws that have no mechanical
check, on the view that only attention catches what no gate catches. That is a guess about attention, not a
measurement; it is five lines and marked TODO.

## Not in version 0

- No scene, receipt or run record is in the graph yet (the corpus side of the flywheel).
- Honest-limits sections and prose claims have no ids, so they are not nodes.
- `SOURCES.md` was not read, so the 34 Loom source tags are bare names.
- Tool names are read by a small grammar; 274 of 355 instrument strings are pointers or keep some part as a free-text note.
- Nothing is served: no MCP tool and no nightly re-run. Those are the next two steps.
- The scene has no camera flight to a found item, and the 66 pins and 355 instruments are not drawn (only the six pins the quotes stand on).
