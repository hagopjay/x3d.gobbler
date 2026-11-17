# 07. x3d.xray, the X-ray method

> **Say it:** x3d.xray turns the git history of a family of repositories into one X3D scene whose every number is computed by code, graded by checks declared before the data is read, and re-derived by a second reader; on a repository too thin to grade, its honest output is "not run". **[C]**

| field | value |
|---|---|
| chapter code | `XRY` |
| prerequisites | [01 The tether](01-the-tether.md) for the loop; [03 The validator and the gates](03-validator-and-gates.md) for the rungs the gates call; [06 X_ITE, the reference renderer](06-xite-the-oracle.md) for the viewer |
| after this you can | (1) name the eleven stages and say which involve a model; (2) read an EDA ledger and say what Confirmed does and does not mean, with the 4-of-150 noise figure; (3) recompute the q arithmetic and the generator by hand; (4) explain why a producer and its independent reader can agree on a bug and what pins it; (5) run the pipeline and the examples without paid services and say what a thin repository produces |
| sources read | x3d.xray@8fa6845:README.md, x3dray/{looks,stats,eda,gallery,gallerycheck,compiler,harvest,gates}.py, x3dray/web/tools.js, examples/, tests/, experiments/smoke_synthetic_pipeline.py, docs/development-pass-{1,2,3}.html, specs/, families/; x3d.castle@d70e00c (public history only); x3d_mcp@b4efcd3:src/validation/ |
| instruments used | `x3d.xray@8fa6845`; `x3d_mcp fork b4efcd3`; `X3D XSD 4.0` (sha256 0509fa5bd601); lxml 6.1.3; Python 3.13.18; Git 2.43.0; Node 22.23.4; `X_ITE 16.7.0` (vendored by the page, not run for the page itself); software only (4 vCPU Intel Xeon 2.30 GHz, no GPU) |

Rig for every number marked **[C]**: a read-only checkout of `x3d.xray@8fa6845` (Merge pull request 11, 2026-11-13), Python 3.13.18, Git 2.43.0, run on 2026-11-14. Anything that wrote files wrote them to a scratch folder. The repository is public (`github.com/hagopjay/x3d.xray`).

## 1. The map

```text
  git clones of a family     (public repos itemised; private repos: counts and times only)
      |
      v  harvest   -> dataset.json, ties.json       no model; identities hashed
      v  curated   -> curated.json (optional)       hand-graded ties imported, addresses scrubbed
      v  structure -> concepts.json, bridges.json   formal concepts, betweenness; no model
      v  eda       -> eda.json                      audit, profiles, 12 declared looks, flags
      v  profile   -> profile.json                  signals, each with its numbers
      v  self      -> self.json                     the tool describes itself (module sha256)
      v  spec      -> spec.rendered.json            prose by a model, every digit a {slot}
      v  build     -> xray.x3d + layout.json        the scene: helix, constellation, city, looks
      v  page      -> index.html, bundle.json       an Artifact-shaped folder, vendored X_ITE
      v  gate      -> gates.json                    xsd loom fact privacy witness scene tools live
      v  receipt   -> receipt.json                  one sha256: inputs, modules, outputs, verdicts
```

| stage | command | model involved | what it can refuse |
|---|---|---|---|
| harvest | `python3 -m x3dray harvest --family F --root DIR --data DIR` | no | an unknown repo name (nearest names offered); nothing is guessed |
| structure | `... structure --data DIR` | no | n/a; sets aside merges, private commits and mass edits (over 15 files) and says how many |
| eda | `... eda --data DIR` | no | a dataset it cannot count (time beyond plus or minus 8.64e12 s, negative line counts): one `eda:` line, nothing written |
| spec | `... spec --data DIR --spec S` | yes: the prose is written by a model | any digit outside a slot; any slot that does not resolve |
| build | `... build --data DIR --out DIR` | no | n/a |
| gate | `... gate --data DIR --out DIR [--onto D --fork D]` | no | see section 8 |
| receipt | `... receipt --data DIR --out DIR` | no | n/a |

Only the `spec` stage and the Ask panel at run time involve a model, and "prose by Claude, numbers by code" is the contract: the model writes sentences around `{slot}` placeholders, code fills the slots from `profile.json`, and the fact gate fails any digit that is not in a slot (`x3d.xray@8fa6845:README.md`, "AI-native, and aware of itself").

**In scope:** the method (stages, rules, statistics, the gallery, the gates), what each development pass found, how to run it free, and what a thin repository produces. **Out of scope:** the private previews built from the method, and any named person's history. This chapter runs the tool on public histories only.

**Read next:** deeper, `x3d.xray@8fa6845:x3dray/looks.py` (the declared family and the grade function, 852 lines); wider, [03 The validator and the gates](03-validator-and-gates.md) for the rungs that the `gate` stage calls.

## 2. What each pass found

The repository records three development passes as self-contained pages under `docs/`, then the EDA stage, the in-browser recompute and the look gallery as features. The pass numbers below are read from those pages and the README **[L]** (the pages record their own runs; they were not re-run at their original commits). The last row is this chapter's own run.

| pass | version and date | tests recorded | what it found |
|---|---|---|---|
| 1 | 0.2.0.dev1, 2026-11-12 | 178 Python, 10 DOM checks | the passage-point routine asked "if I remove this vertex, are these repositories still connected" for every vertex and pair; replacing it with a biconnected-block index (build once, reuse) cut the 121-node analysis plus verifier from 10.14 s to 0.63 s (16.08x), with identical output hashes at 21, 41, 81 and 121 nodes. The old routine stayed as the independent oracle |
| 2 | 0.3.0.dev1, 2026-11-12 | 312 Python, 14 DOM checks | a scene checker that does not import the compiler: 13 audit cases (a baseline, 10 deliberate violations rejected, an equivalent nested-transform scene accepted, a scope probe accepted); a short acyclic DEF/USE graph can expand exponentially, so the checker shares a 250,000-visit budget |
| 3 | 0.4.0.dev1, 2026-11-12 | 442 Python, 23 DOM checks | immutable witnesses (full commit and blob ids, byte spans, raw SHA-256) so a moving HEAD cannot retarget evidence; two clocks (observed-by and valid-at); scale runs at 10, 100 and 1,000 entities; a fixed-ring layout gave 7,936 overlapping glyph pairs at 1,000 entities, adaptive rings gave 0 (closest gap -0.56493 to +0.34968 world units), and the page says zero overlaps is not legible labels |
| EDA and recompute | features, README | 857 run at 8fa6845 | a declared family of 12 looks, an exact-integer kernel, a JavaScript twin that recomputes the stored ledger byte for byte (sections 4 and 5) |
| this run | `x3d.xray@8fa6845`, 2026-11-14 | 857 ran: 810 passed, 3 failed, 24 errored, 20 skipped | all 27 failures and errors sit in the immutable-locator group (`test_locators`, `test_ties.ImmutableTieTests`, `test_continuum` and `test_prooflab` set-up); Git 2.43.0 answers `unknown option: --no-lazy-fetch`, the flag those tests need [C] |

**[C]** for the last row: instrument `x3d.xray@8fa6845`, Git 2.43.0, Python 3.13.18, `python3 -m unittest discover -s tests`, 295.5 s. The README says the locator workflow needs "Git with `--no-lazy-fetch` support". A newer Git would be expected to clear the 27; that expectation is **[L]**, not run.

## 3. The data rules

Six rules in the README decide what the tool will say. Each is enforced by a gate or a test, not by style.

| rule | what it means in the data | enforced by |
|---|---|---|
| one vocabulary | every repo name resolves through the family file; an unknown name is refused with the nearest names | `harvest`; `tests/test_spec_contract.py` |
| unknown is not zero | a coverage ledger says how much history and tree was measured; the unmeasured is fog in the city, never an empty lot | `profile`; the scene |
| no witness, no tie | every tie carries evidence (paths, lines, hashes, stated lineage), graded C, L or S; the scene may not draw a tie the data lacks | witness gate |
| set aside, then counted | the file lattice and co-change graph leave out merges (git lists no paths for them), private commits and mass edits of more than 15 files; every answer says how many it left out | `structure`; `stats.MASS_FILES = 15` |
| no recorded session link is not no link | only commits with a session trailer can link two repos through a session; the absence of a chain is reported as such | `bridges.json` |
| viewpoints are claims | a Viewpoint is named by the claim it backs, not by where the camera stands | `compiler.py` |

Ties use the same three grades as this knowledge base: C (read in the exact code or file), L (read in a source it trusts), S (a guess). The mapping is the point of the tool's name in the family: "name the instrument behind every number" ([01 The tether](01-the-tether.md)) is implemented as a witness on every drawn tie.

## 4. The EDA statistics

`python3 -m x3dray eda` is "quasi-exploratory": what may be looked at is declared before the data is read, and what is found is graded by how well it survives declared checks. A grade is a robustness check over declared variations, never a probability.

```text
  commit rows (time, repo, class you|ai|bot, lines, files, merge flag, ...)
        |
        |  pair = the two author classes with the most non-merge commits, each >= 20
        v
  12 declared looks  (m = 12 whatever the data)
        |
        v   effect size, integer arithmetic only
  Cliff's delta counts (lines, files, gap_s)  |  total variation (hour4, weekday, repo)
        |        floor: |delta| >= 147/1000    |      floor: TV >= 1/10
        v
  add-one label-permutation count  k of M shuffles at least as extreme
        |   p = (k+1)/(M+1);  SplitMix64 stream seeded from sha256 of the look's label
        |   M = clamp (10,000,000 / W, 199, 999);  surprising when p <= 1/20
        v
  Benjamini-Hochberg q over the family  (m = 12 plus every look asked)
        |        q <= 1/10 to survive, q <= 1/20 for Confirmed
        v
  robustness checks:  4 forks | leave-one-repo-out | per-repo strata | interleaved-week halves
        |
        v
  first matching rule gives the grade  C | L | S | none, with a stored reason
```

### 4.1 The declared family

| id | kind | measure | meaning |
|---|---|---|---|
| `contrast:lines` | contrast | lines changed per commit | pair A against pair B |
| `contrast:files` | contrast | files changed per commit | same |
| `contrast:gap_s` | contrast | quiet seconds before a commit | same |
| `contrast:hour4` | contrast | UTC four-hour block | total variation |
| `contrast:weekday` | contrast | UTC weekday | total variation |
| `contrast:repo` | contrast | which repo the commit is in | total variation; never above Likely |
| `drift:first:{lines,hour4,weekday}` | drift | later half against earlier half of the first class's commits | 3 looks |
| `drift:second:{lines,hour4,weekday}` | drift | same for the second class | 3 looks |

Count: 6 contrasts and 6 drifts, `M_DECLARED = 12`, manifest sha256 prefix `a5fce6ec4bade0c8` (thresholds included) **[C]**, instrument `x3d.xray@8fa6845` (`looks.M_DECLARED`, `looks.manifest_sha256`). A look that cannot run enters the correction with p = 1 and says why it did not run.

### 4.2 The grade function, in order

`looks.grade` is a pure function over stored fields; the first rule that matches wins.

| order | condition | grade | stored reason |
|---|---|---|---|
| 1 | the look did not run | none | `not_run` |
| 2 | effect below the floor | none | `effect_below_floor` |
| 3 | add-one count above 1/20 | none | `not_surprising` |
| 4 | q above 1/10 | S | `not_surviving_BH` |
| 5 | an opposite effect in any repo stratum | S | `contrary_effect_in_a_repo` |
| 6 | q above 1/20 | L | `q_above_confirm_level` |
| 7 | no repo holds 20 commits of each group | L | `no_stratum_with_both_groups` |
| 8 | halves not evaluable or not replicating | L | `halves_not_evaluable`, `not_replicated_in_halves` |
| 9 | fewer than 3 distinct forks evaluable, or they disagree | L | `fewer_than_3_distinct_forks_evaluable`, `fork_disagreement` |
| 10 | fewer than 3 leave-one-repo-out runs, or they disagree | L | `leave_one_repo_out_unavailable`, `leave_one_repo_out_disagreement` |
| 11 | everything above passes at q at most 1/20 | C | `all_checks_pass` |

The four forks are `all`, `no_merge`, `default_branch` and `no_mass` (commits touching at most 15 files); forks holding exactly the same commits count once. Source: `x3d.xray@8fa6845:x3dray/looks.py` lines 309 to 349 and `stats.py` lines 23 and 24. **[C]**, read in the exact code.

### 4.3 The arithmetic, re-derived

Everything is integer or `Fraction`; there is no float in `eda.json`, and the file is byte-identical across runs.

| item | value | grade | instrument |
|---|---|---|---|
| SplitMix64, seed 0, first word | 16294208416658607535 = 0xE220A8397B1DCDAF | C | `x3dray.stats.SplitMix64` (matches the published reference word) |
| SplitMix64, seed 1234567, first two words | 6457827717110365317, 3203168211198807973 | C | same |
| add-one p for 1 shuffle at least as extreme in 999 | 2/1000 (shown as 0.0020) | C | `fractions.Fraction`; the examples print 0.0020 |
| largest count that still passes "p at most 1/20" at M = 999 | k = 49 (`20*(k+1) <= 1000`) | C | arithmetic on `looks.THRESHOLDS["ALPHA"]` |
| BH q for two looks at p = 2/1000, family m = 12 | 3/250 = 0.0120 | C | `stats.bh_q` |
| same, m = 13 | 13/1000 = 0.0130 | C | `stats.bh_q` |
| same, m = 51 | 51/1000 = 0.0510 | C | `stats.bh_q` |

The last three rows are the "price of looking": the formula is `q_i = min(q_{i+1}, m * p_i / i)`, so with two looks at the same p, q = m * 0.002 / 2, and every extra look anyone takes raises m. At m = 51 the same p gives q = 0.0510, which does not clear 1/20. `examples/eda_3_the_price_of_looking.py` prints exactly this table (0 other looks: m = 13, q 0.0130; 38 other looks: m = 51, q 0.0510, "does not clear") and it ran here **[C]**.

### 4.4 What the examples show

All three run offline on seeded synthetic data and are run as tests in CI. Output below is from this run (`x3d.xray@8fa6845`, Python 3.13.18).

| example | setup | result |
|---|---|---|
| `eda_1_signal_and_noise.py`, planted | one author class writes commits 5x smaller in a narrower band of hours (seed 7, 4 repos x 150 commits) | `contrast:lines` C (effect 647/1000, q 0.0060) and `contrast:hour4` C (380/1000, q 0.0060); ledger C 2, L 0, S 0, none 10 |
| `eda_1_signal_and_noise.py`, noise | nothing planted, 3 repos x 120 commits, seeds 1028 to 1033 | 5 of 6 seeds earn no Confirmed; seed 1031 earns one: `contrast:hour4` effect 195/1000, q 0.0280, while its other flagged looks are L (`fork_disagreement`) and S (`contrary_effect_in_a_repo`) |
| calibration | 150 pure-noise histories, seeds 1000 to 1149, `--calibrate` | **4 of 150** earned at least one Confirmed (2.67%), recomputed in this run |
| `eda_2_simpsons_paradox.py` | the author class follows the repo (4 repos x 150 commits) | `contrast:lines` effect -589/1000, q 0.0060 is L (`no_stratum_with_both_groups`), `contrast:repo` is L (`leave_one_repo_out_unavailable`); nothing Confirmed, because the strata check could not run |
| `eda_3_the_price_of_looking.py` | the same p, more looks before it | q rises from 0.0130 (m = 13) to 0.0510 (m = 51) |

Grade **[C]** for each row: instrument `x3d.xray@8fa6845`, examples run 2026-11-14 (the calibration with `--calibrate`, about 6 minutes on 4 vCPU). Read the calibration row as the honest limit on the word "Confirmed": about one pure-noise history in 37 earns it, so a Confirmed look can be a false positive and the page must say so. The 4-of-150 figure is a property of these seeds and this synthetic generator; it is not a general false-positive rate.

### 4.5 What the statistics do not claim

- Commits are treated as exchangeable under the permutation null; they are not (they cluster in sessions).
- Benjamini-Hochberg assumes independent or positively dependent looks; these share commits, so q is "indicative" (`looks.BH_NOTE`).
- Times are UTC author times. Renames are not followed. Lines changed come from `git numstat`, so vendored and generated files count in full. Squashed or rebased history hides who did the work.
- Slices and `compare` calls are never graded: the robustness checks exist only for the 12 declared looks.
- A pattern that survives is "not causal, not predictive" (`looks.SAY_AT_MOST["C"]`).

## 5. JavaScript inference: recompute and compare

The page and the MCP server share one tool set (`x3dray/web/tools.js`; 11 tools shared, 1 MCP-only, 4 page-only, from `python3 -m x3dray tools` **[C]**). Two of its `eda` topics matter for accountability.

| topic | what it does | refusals |
|---|---|---|
| `recompute` | runs the 12 declared looks again in the browser from the bundle's commit rows with a JavaScript twin (synchronous SHA-256, SplitMix64 on two 32-bit halves, exact integer Cliff and total-variation counts, the add-one null, BH, the grade rule), compares the canonical text with the stored section byte for byte, answers `match: true` with both digests or names the differing paths | checks known answers first (SHA-256 of "abc", published SplitMix64 words, the manifest hash); refuses before drawing if the permutations exceed 25 million draws or the rows break the `stats.py` row contract |
| `compare` | asks whether slice A differs from slice B on one of six measures; returns the effect, an exact add-one count and a BH q over every look asked plus the 12 declared, with that denominator printed | refuses a group under 20 commits or a bill above 4 million draws instead of thinning; at most 30 distinct comparisons per tool set; always `grade: null` |

Design points worth copying. The seed for `compare` comes from the two groups' value lists in digest order, so asking B against A, or spelling a filter differently, is the same question with the same stream: a question cannot be re-rolled for a better p. The count of looks restarts from 12 on a reload, and the answer says so (`counted_in`). Python stays the specification: `tests/test_eda_infer.py` and `tests/test_eda_js_parity.py` hold the two in agreement on ties, huge values, no author pair and a 24,000-commit bundle; both modules ran in the full suite here and passed **[C]** (810 of 857 passing, the 27 failures being the locator group of section 2).

`take_look` is one more event in the investigation hash chain: it records that a look was taken (declared, a slice, a row query or a comparison) so that a reload continues the count. The README states what this does not prove: that the look was computed, shown or read, who took it, or that nothing else was looked at, so the counts are a lower bound and the chain is integrity bookkeeping, not authentication.

## 6. The 3D look gallery and the independent-reader lesson

The scene's Looks view draws the 12 declared looks as small multiples, one panel each in declared order (6 contrasts on the first row, 6 drifts below). A panel has a slab coloured by grade (hollow when the look did not run), three bars (effect, the share of shuffles at least as extreme, and q, each 6/1000 of a unit per permille), four cubes (forks, leave-one-repo-out, repo strata, halves: pass, fail, or hollow when the check could not run) and a label with the stored sentence. A bar of zero is not drawn: absence is the zero, and only a hollow slab means "not run".

```text
   producer                              independent reader
   x3dray/gallery.py                     x3dray/gallerycheck.py
   (writes the XML from stored           imports: json, re, xml.etree, decimal only
    integers: bar = |permille| * 0.006)  (no compiler, no producer, no eda/looks/stats)
        |                                      |
        |   xray.x3d  --------------------->   re-derives panel list, grid, bar heights,
        |                                       colours, check cubes, text from bundle.eda
        |                                       tolerance 0.0011 against a resolution 0.006
        v                                      v
   they agree  ==  the XML matches the stored numbers      NOT  ==  the stored numbers are right
```

The reader refuses a missing, extra, duplicated, reordered or moved panel, a changed size, colour, hollowness or digit, anything unregistered inside the layer, DEF/USE sharing, a second layer and a marker outside it. It does not check the rest of the scene outside the layer, the camera, rendered text size or pixels.

**The lesson.** A signed Cliff's delta is negative when the second class has the larger values; the bar must be its magnitude, in the other colour. A producer and a reader written from the same reading of the data can both drop the sign and agree. The file `gallery.py` line 103 and `gallerycheck.py` line 120 each compute `abs (permille)`; the test at `tests/test_gallery.py` line 78 pins the raw stored value (`permille < 0`) and the expected bar and colour. Experiment on a scratch copy, both modules edited to `max (0, permille)` (a negative effect drawn as no bar):

| state | tests in `tests/test_gallery.py` | failing |
|---|---|---|
| unmodified `x3d.xray@8fa6845` | 43 run, 43 pass | none |
| shared mistake in producer and reader | 43 run, 42 pass | exactly one: `test_a_negative_cliff_effect_is_a_bar_of_its_magnitude_in_the_other_colour` |

Grade **[C]**, instrument `x3d.xray@8fa6845` and a scratch copy of `x3dray/`, `tests/` and `experiments/`, Python 3.13.18, 27 s per run (D-XRY-6). The independent reader, the gate that runs it on the real compile path and 41 other tests all stay green with the shared mistake: independence only helps if tests also pin raw stored values (a negative effect, a distance), not just producer-against-reader agreement. That the mistake happened once in the real build before the pin was added is carried from a private note (**[S]**, not re-checked); the experiment above does not depend on it.

## 7. The code city, and what a thin repository looks like

The code city draws one district per repo at its tip and one building per file. The rules are in `x3dray/compiler.py` (lines 847 to 896, **[C]** read):

| element | rule | consequence |
|---|---|---|
| district side | `2.0 + 0.9 * log2 (1 + files / 40)`; a repo with no measured tree gets 1.6 and a darker plate | size says how many files, not how good they are |
| buildings | the top 64 files by lines, ordered by kind then lines | 64 is a cap: the rest of the repo is not drawn |
| building height | `0.06 + 0.42 * log2 (1 + lines / 25)` | logarithmic: a 10x file is about 1.4 units taller, not 10x |
| hot roof | churn at or above `max (1000, 90th-percentile churn of the drawn files)`; roof height `0.05 + 0.05 * log10 (churn)` | a roof means total lines changed, whatever the cause |
| unmeasured | colour `#7f93a3`, drawn as fog, never as an empty lot | unknown is not zero |

A **thin repository** is one with too few commits for the statistics and too little history for churn to mean rework. To see what the method says, this chapter ran the real stages (`harvest`, `structure`, `eda`, `profile`) on one public repository, `x3d.castle@d70e00c`, as a one-repo family (the run is D-XRY-4; no private preview was used or described):

| measure | value | grade | instrument |
|---|---|---|---|
| commits, active days, author classes | 10 commits, 1 active day (2026-11-13), classes ai 9 and you 1 | C | `x3d.xray@8fa6845` `harvest` on `x3d.castle@d70e00c` |
| tip tree | 363 files, 12,218,378 B, 78,637 text lines; `data` 142 files and 62,892 lines, `code` 15 files and 3,495 lines, `media` 80 files | C | same, `dataset.json` |
| concentration | the top 64 files hold 79.2% of the text lines (62,306 of 78,637) | C | same |
| churn against size | 274 of 283 text files (96.8%) have churn equal to size; 349 of 363 files were touched by exactly one commit | C | same; `git log` per file |
| hottest roofs | `results.json` 19,849 lines churned, `matrix.json` 4,146, then a Pascal exporter unit at 2,622 | C | same |
| file lattice | 1 concept over 15 files, 0 area rules: the other files arrive in commits of more than 15 files and are set aside | C | `structure` |
| EDA | 12 declared looks, 0 evaluated, 12 not run, reason "fewer than two author classes have 20 or more commits outside merges" | C | `eda`; `looks.PAIR_REASON` |

```text
   thin repo (10 commits, 1 day)            what each stage may honestly say
   -------------------------------          ------------------------------------------------
   harvest     10 commits, 363 files        counts and the tree: measured
   structure   15 files in the lattice      "set aside 348 files in mass edits": say so
   eda         pair needs 20+ per class     12 looks "not run" with the reason; no grade
   city        top 64 files = 79% of lines  hot roofs = big recorded results, not rework
   profile     23 signals computed          README: small populations report "unavailable"
```

What this teaches. First, churn equals size when every file is written once; a hot roof on a one-commit file marks a large recorded result file (here JSON data), not rework, and reading it as rework is the mistake. Second, "not run" is a result: the ledger shows 12 of 12 not run, not 12 findings of "no effect". Third, the record is a function of the commit count: more commits and a second author class with 20 or more commits are what let the looks run, and nothing in the tool will pretend otherwise.

## 8. The scene, the gates and a fixed defect

The scene is X3D 4.0, profile Immersive. The synthetic fixture build of this chapter (2 repos, 16 commits) produced `xray.x3d` of 125,302 B with 98 labels, 2 repo nodes, 12 buildings and 3 days.

### 8.1 The eight gates

| gate | checks | ran here | result |
|---|---|---|---|
| xsd | the scene against the X3D 4.0 schema | yes, `x3d_mcp fork b4efcd3` `validate_xml` (not the repo's `xmllint` path) | valid, 0 errors; semantic layer 0 errors, 7 warnings (2 `empty-group`, 5 `naming-convention`), 145 info (`unused-def`) |
| loom | the Loom gate of `x3d.onto` on the scene | no (needs an `x3d.onto` clone) | not run |
| fact | no digit outside a slot, every slot resolves, every claim backed | yes (smoke pipeline) | pass |
| privacy | no address, session URL or secret-shaped string in any written file; no private repo itemised | yes (smoke pipeline) | pass |
| witness | no tie without evidence; concepts, bridges and `eda` recomputed from the dataset must match | yes (smoke pipeline) | pass |
| scene | an independent XML reader compares the declared geometry, identity, witnesses and grade colours with the plan | partly (unit tests) | not run on the smoke scene |
| tools | every tool runs within the 32 KB result limit; the MCP server answers | no (family-specific fixtures) | not run |
| live | Chromium under a strict content policy: the scene loads and draws every label, a click opens a card, Ask runs against a stand-in | no | not run |

The smoke pipeline (`experiments/smoke_synthetic_pipeline.py`, synthetic Git fixtures, no model) reports `ok: true` and `release_ready: false`: three gates ran and passed, XSD, Loom, tools and live were skipped, and a skipped gate counts as incomplete for release (`gate --release`). **[C]**, instrument `x3d.xray@8fa6845`, source head recorded as `8fa6845a3f1b`, `X_ITE 16.7.0` dist from the npm tarball, 2026-11-14. The page that ships with the scene vendors X_ITE; for the black-draw trap on hosted pages see [06 X_ITE, the reference renderer](06-xite-the-oracle.md).

### 8.2 The `MetadataString` containerField defect

The scene tags semantic metadata with `MetadataString` nodes. In X3D 4.0 the default `containerField` of `MetadataString` is `value`, so inside a `Transform` or `Shape` a validator reports `containerfield-unknown` unless the attribute says `metadata`.

| question | answer at `x3d.xray@8fa6845` | grade | evidence |
|---|---|---|---|
| does the defect still stand? | no: both emitters write `containerField='metadata'` | C | `x3dray/compiler.py` line 91 and `x3dray/gallery.py` line 67 |
| is it pinned by tests? | yes, twice | C | `tests/test_gallery.py` line 51 (`test_every_metadata_string_names_its_container_field`), `tests/test_scene_plan.py` line 37 |
| where was it found? | by a validator pass over a generated build with an earlier fork commit | L | the comment at `tests/test_gallery.py` line 52 names `x3d_mcp fork 13121b6`; the fix history is not in this checkout (one commit visible), so the date of the fix is not established |
| does the current scene pass? | 90 of 90 `MetadataString` carry `containerField='metadata'`; XSD 4.0 valid; 0 `containerfield-unknown` | C | `x3d_mcp fork b4efcd3` on the smoke scene |
| what does the old defect look like? | remove the attribute from all 90: XSD 4.0 still reports 0 errors, the semantic layer reports 90 `containerfield-unknown` errors | C | same scene, attribute stripped by a one-line regex (D-XRY-5) |

The last row is the useful part. The schema rung cannot see this defect at all; only the fork's semantic rung can, which is the ladder argument of [03 The validator and the gates](03-validator-and-gates.md) in a single measured example. A pipeline that gated only on XSD would have shipped it.

## 9. Running it free

| need | free | what this chapter ran |
|---|---|---|
| Python 3.10+, git, Node 18+ | yes | Python 3.13.18, Git 2.43.0, Node 22.23.4 |
| unit tests | yes: `python3 -m unittest discover -s tests` (about 5 minutes) | 857 ran, 810 passed, 27 failed or errored on Git 2.43.0 (section 2) |
| examples | yes: `python3 examples/eda_N_*.py`; `--calibrate` on example 1 takes about 6 minutes | all three; calibration recomputed |
| synthetic pipeline | yes: `python3 experiments/smoke_synthetic_pipeline.py --xite DIST --font TTF --output-json OUT` | passed; `X_ITE 16.7.0` dist from the npm tarball, a system TTF font |
| a real family | yes, on public repos: a family JSON listing repos, identities (hashed) and vocabulary, then `harvest`, `structure`, `eda`, `profile` | a one-repo family on a public repo (D-XRY-4) |
| XSD gate | needs `xmllint` in the repo's path | covered here by `x3d_mcp fork b4efcd3` and lxml |
| Loom gate | needs a clone of `x3d.onto` | not run |
| live gate | needs Playwright with Chromium | not run for this tool; the X_ITE harness of chapter 06 shows the pattern |
| the model for `spec` and Ask | a model; not run | the spec stage was exercised only through the smoke pipeline's fixture spec |

Commands, in the order the README gives them (a family file, a root folder holding the clones, a scratch data folder):

```bash
python3 -m x3dray harvest   --family families/F.json --root ROOT --data data/F
python3 -m x3dray structure --data data/F
python3 -m x3dray eda       --data data/F
python3 -m x3dray profile   --data data/F
python3 -m x3dray tools     # the tool set the page and MCP share
```

## Heuristics

| ID | Rule (imperative) | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-XRY-1 | Declare the family of looks before reading the data, hold m fixed, and count every extra look in m. | C | same p, q 0.0130 at m = 13 and 0.0510 at m = 51 | `x3d.xray@8fa6845`, `stats.bh_q` |
| H-XRY-2 | Say that a Confirmed can be a false positive, and quote 4 of 150 with its seeds and generator. | C | 4 of 150 noise histories earned one (2.67%), recomputed | `x3d.xray@8fa6845`, `examples/eda_1_signal_and_noise.py --calibrate` |
| H-XRY-3 | Make an unrun check fail the grade: no stratum, no halves, fewer than 3 forks means Likely at most. | C | Simpson example: q 0.0060 and effect -589/1000 graded L | `x3d.xray@8fa6845`, `looks.grade` |
| H-XRY-4 | Use exact integer arithmetic and a published generator where two implementations must agree byte for byte. | C | SplitMix64 reference words match; JS twin parity: 16 and 37 tests pass | `x3d.xray@8fa6845`, `stats.SplitMix64` |
| H-XRY-5 | Give the independent reader no imports from the producer, and pin raw stored values in tests, not only agreement. | C | shared sign mistake: 42 of 43 gallery tests stay green, the raw pin fails | `x3d.xray@8fa6845`, scratch copy |
| H-XRY-6 | Report "not run" with its reason and draw the unmeasured as fog, never as zero. | C | thin repo: 12 of 12 looks not run, reason stored | `x3d.xray@8fa6845` on `x3d.castle@d70e00c` |
| H-XRY-7 | Read churn together with size: on a repo where files are written once, a hot roof marks a large result file. | C | 274 of 283 text files have churn equal to size | same |
| H-XRY-8 | Gate on the semantic rung as well as the XSD; a missing `containerField` passes the schema and fails the semantic rule. | C | 0 XSD errors and 90 `containerfield-unknown` on the stripped scene | `x3d_mcp fork b4efcd3`, `X3D XSD 4.0` |
| H-XRY-9 | Make a question impossible to re-roll: seed from the content, cap comparisons, print the denominator. | L | `compare` seeds from value lists in digest order, caps at 30, prints m; read in the README and `tools.js`, example 3 ran | `x3d.xray@8fa6845` |
| H-XRY-10 | Refuse over budget instead of thinning: cap permutations times draws and say so. | C | `WORK_CAP` 10,000,000, ad hoc cap 4,000,000, `M` clamped to 199..999 | `x3d.xray@8fa6845:x3dray/looks.py`, `stats.py` (read) |
| H-XRY-11 | Treat a hash chain of looks as bookkeeping, not authentication, and state what it cannot prove. | L | README: the chain does not prove a look was computed, shown or read, or who took it | `x3d.xray@8fa6845:README.md` (read) |
| H-XRY-12 | Treat a local red as a question about the rig before the code: 27 failures shared one cause. | C | all 27 in the locator group; Git 2.43.0 rejects `--no-lazy-fetch` | `x3d.xray@8fa6845`, Git 2.43.0 |

## Drills

### D-XRY-1 Recompute the noise calibration
- **Level:** L2
- **Task:** Run `examples/eda_1_signal_and_noise.py` and then with `--calibrate`. Report the planted ledger, which noise seed earns a Confirmed and the calibration count, and say what the number does and does not license.
- **Verify:** `python3 examples/eda_1_signal_and_noise.py --calibrate` from the repository root (about 6 minutes).
- **Answer:** planted: `contrast:lines` and `contrast:hour4` are C (q 0.0060), ledger C 2, L 0, S 0, none 10. Noise: seed 1031 earns a Confirmed (`contrast:hour4`, 195/1000, q 0.0280); the other five seeds earn none. Calibration: 4 of 150 histories (seeds 1000 to 1149) earn at least one Confirmed, 2.67%. It licenses "a Confirmed can occur on noise"; it does not give a false-positive rate for real data.
- **Checked:** 2026-11-14 `x3d.xray@8fa6845`, Python 3.13.18

### D-XRY-2 The price of looking, by hand and by code
- **Level:** L1
- **Task:** Two looks have add-one p = 2/1000. Compute q for each with the BH formula `q_i = min (q_{i+1}, m * p_i / i)` at m = 12, 13 and 51, then check with `stats.bh_q`.
- **Verify:** `from fractions import Fraction as F; from x3dray import stats; stats.bh_q ([("a", F (2, 1000)), ("b", F (2, 1000))], 13)`.
- **Answer:** q = m * 0.002 / 2 = 0.0120, 0.0130, 0.0510. Only the first two clear 1/20; at m = 51 the look is no longer Confirmed even though p did not move.
- **Checked:** 2026-11-14 `x3d.xray@8fa6845`, Python 3.13.18

### D-XRY-3 Pin the generator and the add-one limit
- **Level:** L2
- **Task:** Print the first three words of `SplitMix64 (0)` and the first two of `SplitMix64 (1234567)`. Then find the largest permutation count k that still satisfies "p at most 1/20" for M = 999.
- **Verify:** `from x3dray import stats; r = stats.SplitMix64 (0); [r.next_u64 () for _ in range (3)]`; the limit from `20 * (k + 1) <= 1 * (999 + 1)`.
- **Answer:** seed 0: 16294208416658607535, 7960286522194355700, 487617019471545679 (the first is 0xE220A8397B1DCDAF); seed 1234567: 6457827717110365317, 3203168211198807973. The limit is k = 49, so 50 or more as-extreme shuffles out of 999 give "not surprising".
- **Checked:** 2026-11-14 `x3d.xray@8fa6845`, Python 3.13.18

### D-XRY-4 Run the method on a thin public repository
- **Level:** L2
- **Task:** Copy `families/hagopjay-x3d.json`, set `lineage` to `[]`, `vocabulary` to `{}` and `repos` to one public repo (`{"name": "x3d.castle", "dir": "hagopjay/x3d.castle", "kind": "own", "visibility": "public", "role": "exporter", "aliases": ["x3d.castle"]}`). Put a symlink to a checkout under `ROOT/hagopjay/`. Run `harvest`, `structure`, `eda`, `profile`. Report commits, the EDA ledger and the file-lattice size.
- **Verify:** the one-line output of each stage, then `eda.json` `looks.ledger` and `looks.pair_reason`.
- **Answer:** at `x3d.castle@d70e00c`: `harvest: 1 repos, 10 commits, 0 tie pairs`; `structure: 1 concepts over 15 files, 0 area rules`; `eda: 10 commits, 12 declared looks (0 Confirmed, 0 Likely, 0 Suspected, 0 without a grade, 12 not run)`; `profile: 23 signals`.
- **Checked:** 2026-11-14 `x3d.xray@8fa6845`, `x3d.castle@d70e00c`, Git 2.43.0

### D-XRY-5 Reproduce the containerField defect and see which rung catches it
- **Level:** L3
- **Task:** Build the synthetic scene with `experiments/smoke_synthetic_pipeline.py` (keep `xray.x3d`). Validate it with the fork's `validate_xml` and `semantic_diagnostics`, count the `MetadataString` nodes with `containerField='metadata'`, then remove the attribute (`re.sub (r" containerField='metadata'", "", xml)`) and validate again.
- **Verify:** `from validation.validate import validate_xml; from validation.semantic import semantic_diagnostics` from `x3d_mcp@b4efcd3:src`.
- **Answer:** original: XSD 4.0 valid, 0 errors; 90 of 90 `MetadataString` tagged; semantic layer 0 errors, 7 warnings, 145 info. Stripped: XSD 4.0 still valid with 0 errors; semantic layer 90 `containerfield-unknown` errors. Only the semantic rung sees it.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3`, `X3D XSD 4.0`, lxml 6.1.3, `x3d.xray@8fa6845`

### D-XRY-6 Make the producer and the reader agree on a bug
- **Level:** L3
- **Task:** Copy `x3dray/`, `tests/` and `experiments/` to a scratch folder. In `x3dray/gallery.py` line 103 and `x3dray/gallerycheck.py` line 120, replace `abs (int (... "permille" ...))` by `max (0, int (...))` (a negative effect becomes no bar). Run `python3 -m unittest discover -s tests -p test_gallery.py` before and after. Name the failing test and say what it pins.
- **Verify:** the unittest summary of each run.
- **Answer:** before: 43 run, OK. After: 43 run, 1 failure, `test_a_negative_cliff_effect_is_a_bar_of_its_magnitude_in_the_other_colour`; it asserts the raw stored permille is negative and that the bar has the magnitude in the other colour. The 42 tests that compare producer with reader stay green.
- **Checked:** 2026-11-14 `x3d.xray@8fa6845` (scratch copy), Python 3.13.18

### D-XRY-7 Run the synthetic pipeline and read the gate verdicts
- **Level:** L2
- **Task:** Run `experiments/smoke_synthetic_pipeline.py` with a vendored X_ITE `dist` folder and a TTF. Read `ok`, `release_ready`, each gate and the `not_run` list. Explain why `ok` is true and `release_ready` is false.
- **Verify:** the `--output-json` file.
- **Answer:** `ok: true`, `release_ready: false`; gates `fact`, `privacy`, `witness` pass; `xsd`, `loom`, `tools`, `live` skip; the page has 37 files and 6,295,152 B, 16 commits harvested, `receipt_covered_served_assets` 38 of 39 served (the receipt excludes its own bytes by design). A skipped gate is incomplete for release.
- **Checked:** 2026-11-14 `x3d.xray@8fa6845`, `X_ITE 16.7.0` dist, Python 3.13.18

### D-XRY-8 Classify five looks by the grade function
- **Level:** L1
- **Task:** Using section 4.2, grade: (a) effect 120/1000, Cliff floor 147/1000; (b) q 0.07, no opposite effect; (c) q 0.03, all checks pass, no repo holds 20 commits of each group; (d) q 0.03, 4 forks agree, 3 leave-one-repo-out agree, halves replicate, a stratum holds both groups; (e) q 0.03, but one repo shows the opposite effect.
- **Verify:** `looks.grade` over the stored fields of a look.
- **Answer:** (a) none, `effect_below_floor`; (b) L, `q_above_confirm_level` (q above 1/20 and at most 1/10); (c) L, `no_stratum_with_both_groups`; (d) C, `all_checks_pass`; (e) S, `contrary_effect_in_a_repo`.
- **Checked:** not run (read at `x3d.xray@8fa6845:x3dray/looks.py` lines 309 to 349)

## Honest limits

- **Synthetic and public only.** The noise figures, the examples and the pipeline run use seeded synthetic data; the only real history read is the public `x3d.castle` repository. No claim is made about any person's real work habits. The 4-of-150 figure belongs to those seeds and that generator **[C]**.
- **The pass pages are read, not re-run [L].** The test counts (178, 312, 442), the 10.14 s to 0.63 s benchmark, the scale table and the 7,936 overlaps come from `docs/development-pass-*.html`; the benchmark JSON in `experiments/` was not re-run.
- **Gates not run:** `loom` (needs `x3d.onto`), `tools` and `live` (family-specific fixtures, Playwright page), the family-specific self-tests, the Ask panel against a real runtime, and any rendering of the scene in a browser. "Valid and gated" does not mean "looks right".
- **27 of 857 tests did not pass here** on Git 2.43.0, all in the locator group; the cause (`--no-lazy-fetch` unsupported) is observed [C], and that a newer Git clears them is **[L]**, not run.
- **The statistics are indicative, not inferential.** Exchangeability fails (commits cluster in sessions), BH assumes independence or positive dependence, times are UTC, renames are not followed, squashed history hides authorship.
- **The thin-repo run is one repository at one commit** (`x3d.castle@d70e00c`); the repository is active, so its numbers will move.
- **Fix history unknown.** The checkout shows one commit, so when the `containerField` fix landed is not established; only its current state and its tests are.
- **The independent-reader story** (that the real build once drew a negative effect as no bar) is carried from a private note **[S]**; the experiment of D-XRY-6 reproduces the mechanism, not the incident.
- **Counts are per commit.** The pass pages record 178, 312 and 442 tests at their own versions; this run counts 857 at the current commit. These are different commits, not a conflict, and none of the earlier figures was re-derived.

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-XRY-1 | declared looks | 12 (6 contrasts, 6 drifts); manifest sha256 prefix a5fce6ec4bade0c8 | C | `x3d.xray@8fa6845` | x3d.xray@8fa6845:x3dray/looks.py |
| N-XRY-2 | thresholds | Cliff floor 147/1000, TV floor 1/10, alpha 1/20, q survive 1/10, q Confirmed 1/20, MIN_SIDE 20, M 199..999, WORK_CAP 10,000,000 | C | read in code | x3d.xray@8fa6845:x3dray/looks.py |
| N-XRY-3 | noise calibration | 4 of 150 pure-noise histories earn a Confirmed (2.67%) | C | `examples/eda_1_signal_and_noise.py --calibrate`, seeds 1000 to 1149 | x3d.xray@8fa6845:examples/ |
| N-XRY-4 | planted signal | 2 C looks (effect 647/1000 and 380/1000, q 0.0060) | C | same, seed 7 | same |
| N-XRY-5 | price of looking | q 0.0130 at m = 13; 0.0510 at m = 51; 0.0120 at m = 12 | C | `stats.bh_q` | x3d.xray@8fa6845:x3dray/stats.py |
| N-XRY-6 | SplitMix64 seed 0 first word | 16294208416658607535 (0xE220A8397B1DCDAF) | C | `stats.SplitMix64` | x3d.xray@8fa6845:x3dray/stats.py |
| N-XRY-7 | largest passing permutation count at M = 999 | 49 | C | arithmetic on `ALPHA` | x3d.xray@8fa6845:x3dray/looks.py |
| N-XRY-8 | test suite | 857 ran, 810 passed, 3 failed, 24 errored, 20 skipped, 295.5 s | C | `unittest discover`, Git 2.43.0, Python 3.13.18 | x3d.xray@8fa6845:tests/ |
| N-XRY-9 | JS twin and inference tests | 37 and 16 tests pass | C | `test_eda_infer`, `test_eda_js_parity`, Node 22.23.4 | x3d.xray@8fa6845:tests/ |
| N-XRY-10 | gallery suite | 43 pass; 42 pass with a shared sign mistake | C | scratch copy, Python 3.13.18 | x3d.xray@8fa6845:tests/test_gallery.py |
| N-XRY-11 | tool set | 11 shared, 1 MCP-only, 4 page-only | C | `python3 -m x3dray tools` | x3d.xray@8fa6845:x3dray/web/tools.js |
| N-XRY-12 | repository size | 12,844 Python lines in `x3dray/`, 4,842 JavaScript lines in the web folders, 44 test files, 875 `def test_` lines | C | `wc -l`, grep | x3d.xray@8fa6845 |
| N-XRY-13 | synthetic scene | `xray.x3d` 125,302 B, 98 labels, 12 buildings, 16 commits; XSD 4.0 valid | C | `x3d_mcp fork b4efcd3`, lxml 6.1.3 | experiments/smoke_synthetic_pipeline.py run |
| N-XRY-14 | semantic findings on that scene | 0 errors, 7 warnings, 145 info | C | `x3d_mcp fork b4efcd3` | same |
| N-XRY-15 | `MetadataString` tagged | 90 of 90; stripped: 90 `containerfield-unknown`, XSD errors 0 | C | `x3d_mcp fork b4efcd3` | same (D-XRY-5) |
| N-XRY-16 | smoke pipeline | `ok` true, `release_ready` false; 3 gates pass, 4 skipped; page 37 files, 6,295,152 B | C | `x3d.xray@8fa6845` | smoke JSON, 2026-11-14 |
| N-XRY-17 | thin repo: history | 10 commits, 1 day, ai 9 and you 1, 363 files | C | `x3d.xray@8fa6845` on `x3d.castle@d70e00c` | D-XRY-4 |
| N-XRY-18 | thin repo: tree | 12,218,378 B, 78,637 text lines; top 64 files 79.2% of lines | C | same | same |
| N-XRY-19 | thin repo: churn | 274 of 283 text files churn equals size; 349 of 363 files in one commit | C | same | same |
| N-XRY-20 | thin repo: EDA | 12 looks, 0 evaluated; lattice 1 concept over 15 files | C | same | same |
| N-XRY-21 | pass 1 benchmark | 121 nodes: 10.14 s to 0.63 s (16.08x), outputs hash-equal | L | read, not re-run | x3d.xray@8fa6845:docs/development-pass-1.html |
| N-XRY-22 | pass tests | 178, 312 and 442 Python tests at passes 1, 2, 3 | L | read, not re-run | x3d.xray@8fa6845:docs/development-pass-{1,2,3}.html |
| N-XRY-23 | pass 3 layout repair | 7,936 overlapping glyph pairs to 0 at 1,000 entities | L | read, not re-run | x3d.xray@8fa6845:docs/development-pass-3.html |
| N-XRY-24 | limits of the calibration | 4 of 150 is for these seeds and this generator | C | `examples/eda_1_signal_and_noise.py` | x3d.xray@8fa6845:examples/ |

## Sources and provenance

- `x3d.xray@8fa6845` (Merge pull request 11, 2026-11-13; shallow checkout, one commit visible): `README.md`, `x3dray/{looks,stats,eda,gallery,gallerycheck,compiler,harvest,gates}.py`, `x3dray/web/tools.js`, `examples/`, `tests/`, `experiments/smoke_synthetic_pipeline.py`, `families/hagopjay-x3d.json`, `docs/development-pass-{1,2,3}.html`. Public repository: `github.com/hagopjay/x3d.xray`.
- `x3d.castle@d70e00c` (public history, read through the tool's own `harvest`), `x3d_mcp@b4efcd3` (`src/validation/validate.py`, `semantic.py`, the bundled XSD 4.0 and 4.1).
- Re-run on 2026-11-14 in a scratch folder, repositories untouched: the full unit suite, the three examples and the calibration, the stats probes, the synthetic pipeline, the one-repo run, the validator run on the generated scene (original and stripped), the shared-mistake experiment on a copy.
- Not re-run: the development-pass benchmarks and test counts, the gates `loom`, `tools` and `live`, the Ask panel, any model call.
- Private-source gap: private notes on the x-ray's state, a private preview and the independent-reader incident were pointers only; no private artefact, link or preview is described here, and what a private preview contains is not stated.
- Siblings: [01 The tether](01-the-tether.md), [03 The validator and the gates](03-validator-and-gates.md), [06 X_ITE, the reference renderer](06-xite-the-oracle.md), [10 Blender pipeline](10-blender-pipeline.md).
