#!/usr/bin/env python3
"""Atlas v0: compile the Loom's ledgers into one graph.

Inputs (pinned, read-only)
  src/LOOM-v1.md                     x3d.loom at the sha in src/LOOM.sha
  ../src/x3d.docs/docs/learn/*.md    x3d.docs at the sha in src/DOCS.sha

Outputs (out/)
  atlas.json        nodes and edges, each edge with the column it was read from
  atlas.jsonld      the same graph as JSON-LD 1.1
  atlas.ttl         the same graph as Turtle
  atlas-vocab.ttl   the classes and properties used
  findings.json     what the build could not resolve, and what the graph shows

Stdlib only, no clock, no network: the same inputs give the same bytes.
The witness is check_atlas.py, which reads the outputs back with rdflib.
"""
import collections
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
# ATLAS_LOOM and ATLAS_OUT let a draft of LOOM-v1.md be measured without touching src/ or out/
LOOM = pathlib.Path(os.environ.get("ATLAS_LOOM", HERE / "src" / "LOOM-v1.md"))
# X3D_DOCS points at any checkout of x3d.docs at the sha in src/DOCS.sha; tools/fetch_pins.py makes the default one.
DOCS = pathlib.Path(os.environ.get("X3D_DOCS", HERE / ".." / "src" / "x3d.docs")).resolve()
if not (DOCS / "docs" / "tools-shared" / "claims_lib.py").is_file():
    sys.exit(f"build_atlas: pinned x3d.docs helpers not found at {DOCS}\n"
             "  run: python3 tools/fetch_pins.py   (or set X3D_DOCS to a checkout at the sha in flywheel-review/atlas/src/DOCS.sha)")
LEARN = DOCS / "docs" / "learn"
OUT = pathlib.Path(os.environ.get("ATLAS_OUT", HERE / "out"))

# A placeholder namespace (RFC 2606 .example), the convention x3d.ML set for x3dprov: a registered one is the
# owner's call. Change it here only.
BASE = "https://x3datlas.example/0/"
VOCAB = "https://x3datlas.example/0#"
LOOM_REPO = "hagopjay/x3d.loom"
DOCS_REPO = "hagopjay/x3d.docs"

MAX_QUOTE = 38      # words in a quote the Atlas writes; the checker's cap is 40
LEAD = 20           # words of a long cell that a claim covers


def _load(name):
    """x3d.docs' own tools (stdlib only), loaded by path so nothing else in that folder is importable."""
    spec = importlib.util.spec_from_file_location(name, DOCS / "docs" / "tools-shared" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


L = _load("learn_lib")       # chapters, registers, drills
CL = _load("claims_lib")     # the claim ledger: tokens, FIND, COMPARE


def stated_totals():
    """What the sources say about themselves. The Atlas is compared with these, never with numbers typed here."""
    def gen(name):
        return (LEARN / name).read_text(encoding="utf-8").split("<!-- BEGIN GENERATED -->", 1)[1][:700]

    def grades(m, i):
        return {"C": int(m.group(i)), "L": int(m.group(i + 1)), "S": int(m.group(i + 2))}
    t = {}
    g3 = r"\[C\] (\d+) · \[L\] (\d+) · \[S\] (\d+)"
    m = re.search(r"\*\*(\d+) numbers\*\* from (\d+) chapters\. Grades: " + g3, gen("C-numbers-ledger.md"))
    t["numbers"], t["chapters"], t["number grades"] = int(m.group(1)), int(m.group(2)), grades(m, 3)
    m = re.search(r"\*\*(\d+) heuristics\.\*\* Grades: " + g3, gen("D-heuristics-ledger.md"))
    t["heuristics"], t["heuristic grades"] = int(m.group(1)), grades(m, 2)
    m = re.search(r"\*\*(\d+) drills\*\*, (\d+) with a recorded run", gen("E-drills.md"))
    t["drills"], t["drills run"] = int(m.group(1)), int(m.group(2))
    t["instrument strings"] = int(re.search(r"(\d+) distinct instrument strings", gen("A-validator-register.md")).group(1))
    t["pins"] = int(re.search(r"(\d+) \(repo, commit\) pairs", gen("F-source-map.md")).group(1))
    m = re.search(r"\*\*(\d+) claims\*\* in (\d+) chapter ledgers\. Verdicts: verified (\d+) · check (\d+) · reworded (\d+) "
                  r"· unchecked (\d+)", gen("G-claims-ledger.md"))
    t["claims"] = int(m.group(1))
    t["claim verdicts"] = {"verified": int(m.group(3)), "check": int(m.group(4)), "reworded": int(m.group(5)),
                           "unchecked": int(m.group(6))}
    say = (LEARN / "02-loom-laws.md").read_text(encoding="utf-8")
    m = re.search(r"(\d+) numbered laws and (\d+) numbered failure modes", say)
    t["laws"], t["failure modes"] = int(m.group(1)), int(m.group(2))
    t["failure classes"] = int(re.search(r"(\d+) rows in (\d+) classes", say).group(2))
    return t


# --------------------------------------------------------------------------------------------
# the graph
# --------------------------------------------------------------------------------------------
class Atlas:
    def __init__(self):
        self.nodes = {}
        self.edges = collections.defaultdict(set)      # (s, p, o) -> {where}
        self.findings = collections.defaultdict(list)
        self.claims = []                                # the Atlas's own claims/0.1 rows, one per copied value

    def node(self, nid, ntype, **props):
        n = self.nodes.setdefault(nid, {"id": nid, "type": ntype})
        if n["type"] != ntype:
            raise SystemExit(f"type clash on {nid}: {n['type']} vs {ntype}")
        for k, v in props.items():
            if v is None or v == "" or v == []:
                continue
            n[k] = v
        return n

    def edge(self, s, p, o, where):
        if s != o:
            self.edges[(s, p, o)].add(where)

    def find(self, kind, **row):
        self.findings[kind].append(row)


def raw_cells(line):
    """A table line cut on unescaped pipes, nothing stripped: parts[0] is what stands before the first pipe."""
    return re.split(r"(?<!\\)\|", line)


def own_claim(A, nid, field, line_text, before, cell, source, line_no):
    """One claims/0.1 row for a value the Atlas copied from one source line: the first LEAD words of `cell`,
    quoted together with what stands before them on that line. `before` is the raw text ahead of the cell."""
    k0 = len(CL.tokens(before))
    nv = min(len(CL.tokens(cell)), LEAD)
    spans, norm = CL.token_spans(line_text)
    if nv == 0 or k0 + nv > len(spans) or line_no is None:
        A.find("node without a checkable quote", node=nid, field=field)
        return
    text = line_text if len(norm) == len(line_text) else norm
    end = k0 + nv
    start = max(0, end - MAX_QUOTE)
    A.claims.append({"id": nid, "in": field, "value": text[spans[k0][1]:spans[end - 1][2]],
                     "quote": text[spans[start][1]:spans[end - 1][2]], "source": source, "line": line_no})


def slug(s):
    s = re.sub(r"[^a-z0-9._\-]+", "-", s.lower()).strip("-.")
    return re.sub(r"-{2,}", "-", s) or "x"


def clean(s):
    return re.sub(r"\s+", " ", s).strip()


def sha256_of(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------------------------
# reading cross-references out of free text
# --------------------------------------------------------------------------------------------
ID_RE = re.compile(r"\b([NHD])-([A-Z]{2,4})-(\d+)\b")
ID_RANGE_RE = re.compile(r"\b([NHD])-([A-Z]{2,4})-(\d+) to (?:[NHD]-[A-Z]{2,4}-)?(\d+)\b")
NUMLIST = r"(\d+(?:\s*(?:,|and|or|to)\s*\d+)*)(?![\d]*\.\d)"
LAW_RE = re.compile(r"\blaws?\s+" + NUMLIST, re.I)
FM_RE = re.compile(r"\b(?:failure modes?|fms?)\s+" + NUMLIST, re.I)
RECUR_RE = re.compile(r"\brecurred as (\d+)", re.I)
TRAP_RE = re.compile(r"\btraps? `?([a-z0-9]+(?:-[a-z0-9]+)+)`?")
DIAG_RE = re.compile(r"`([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)`")
NOT_DIAGNOSTICS = {"SOURCE_DATE_EPOCH"}            # environment variables and the like
SRC_RE = re.compile(r"\[([^\]\[]+)\](?!\()")
PREFIX = {"N": "number", "H": "heuristic", "D": "drill"}
MAX_RANGE = 30                                      # "failure modes 148 to 160" becomes edges; a wider span does not


def expand(numlist):
    """'10, 36 and 40' -> [10, 36, 40]; '41 to 43' -> [41, 42, 43]. Returns (ids, wide_ranges)."""
    out, wide = [], []
    for m in re.finditer(r"(\d+)\s*to\s*(\d+)|(\d+)", numlist):
        if m.group(3):
            out.append(int(m.group(3)))
        else:
            a, b = int(m.group(1)), int(m.group(2))
            if 0 < b - a < MAX_RANGE:
                out.extend(range(a, b + 1))
            else:
                wide.append((a, b))
    return out, wide


def refs(text):
    """Every stable id cited in a piece of text: [(target_id, how)]. how is 'id', 'list' or 'range'."""
    found = []
    spans = []
    for m in ID_RANGE_RE.finditer(text):
        kind, code, a, b = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
        if 0 < b - a < 40:
            spans.append(m.span())
            found += [(f"{PREFIX[kind]}/{kind}-{code}-{i}", "range") for i in range(a, b + 1)]
    for m in ID_RE.finditer(text):
        if any(s <= m.start() < e for s, e in spans):
            continue
        found.append((f"{PREFIX[m.group(1)]}/{m.group(0)}", "id"))
    for rx, kind in ((LAW_RE, "law"), (FM_RE, "fm")):
        for m in rx.finditer(text):
            ids, wide = expand(m.group(1))
            how = "range" if " to " in m.group(1) else "list"
            found += [(f"{kind}/{i}", how) for i in ids]
            found += [(f"{kind}/{a}..{b}", "wide") for a, b in wide]
    return found


def source_tags(text):
    """LOOM citations such as [LEC 1; FACTS P via DEF] -> [('LEC', 'LEC 1'), ('FACTS', 'FACTS P via DEF')]."""
    out = []
    for m in SRC_RE.finditer(text):
        for part in m.group(1).split(";"):
            words = part.strip().split()
            if words and re.fullmatch(r"[A-Z][A-Za-z0-9]+", words[0].strip("§,.")):
                out.append((words[0].strip("§,."), clean(part)))
    return out


# --------------------------------------------------------------------------------------------
# reading an instrument string
# --------------------------------------------------------------------------------------------
PIN_AT_RE = re.compile(r"([A-Za-z0-9_][A-Za-z0-9_.\-]*)@([0-9a-f]{7,12})\b")     # as in build_learn.py
PIN_ROLE_RE = re.compile(r"\b([A-Za-z0-9_][A-Za-z0-9_.\-]*) (fork|upstream) ([0-9a-f]{7,12})\b")
SHA_RE = re.compile(r"^(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)[0-9a-f]{7,12}$")
TOOL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.+\- ]*?)\s+(v?\d+(?:\.\d+)*(?:[-.][0-9A-Za-z.\-]+)?|r\d+)$")
VERSION_RE = re.compile(r"^v?\d+(?:\.\d+)+$")
DATE_RE = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")
RELATIVE_RE = re.compile(r"^same\b", re.I)
NOT_TOOLS = {"seed", "seeds", "step", "steps", "frame", "frames", "run", "runs", "section", "law", "fm", "pr",
             "port", "line", "lines", "page", "level", "cap", "rev", "at", "of", "x", "n", "k", "dt", "to",
             "fixture", "fixtures", "case", "cases", "round", "study", "test", "tests", "table", "figure",
             "chapter", "appendix", "sha256", "commit", "tag", "version", "patch", "and", "on", "in", "with"}
BARE_TOOLS = {"swiftshader": "SwiftShader"}         # tools the base names without a version


def parse_instrument(text):
    """Split an instrument cell into what can be named exactly. Everything else stays a note."""
    plain = clean(L.strip_md(text))
    out = {"plain": plain, "relative": bool(RELATIVE_RE.match(plain)), "tools": [], "pins": [], "dates": [],
           "notes": []}
    out["dates"] = sorted(set(DATE_RE.findall(plain)))
    for m in PIN_AT_RE.finditer(plain):
        out["pins"].append((m.group(1), m.group(2), "at"))
    last_repo = None
    last_tool = None
    for tok in re.split(r"\s*[;,]\s*", plain):
        tok = tok.strip()
        if not tok:
            continue
        bare = clean(re.sub(r"\([^()]*\)", "", tok))          # "Chromium 153 (Chrome for Testing ...)" -> "Chromium 153"
        m = PIN_ROLE_RE.search(bare)
        if m:
            last_repo = (m.group(1), m.group(2))
            out["pins"].append((m.group(1), m.group(3), m.group(2)))
            for extra in re.findall(r"\band ([0-9a-f]{7,12})\b", bare[m.end():]):
                out["pins"].append((m.group(1), extra, m.group(2)))
            continue
        if SHA_RE.match(bare) and last_repo:
            out["pins"].append((last_repo[0], bare, last_repo[1]))
            continue
        if PIN_AT_RE.search(bare) or DATE_RE.fullmatch(bare):
            continue
        if VERSION_RE.match(bare) and last_tool:              # "X_ITE 16.6.0, 16.7.0"
            out["tools"].append((last_tool, bare.lstrip("v")))
            continue
        words = bare.split()
        tail = None
        if len(words) > 1 and words[-1].lower() in BARE_TOOLS:  # "Chromium 153.0.8010.12 SwiftShader"
            tail, bare = BARE_TOOLS[words[-1].lower()], " ".join(words[:-1])
        if bare.lower() in BARE_TOOLS:
            out["tools"].append((BARE_TOOLS[bare.lower()], None))
        else:
            m = TOOL_RE.match(bare)
            if m and m.group(1).split()[-1].lower() not in NOT_TOOLS and m.group(1).lower() not in NOT_TOOLS:
                last_tool = m.group(1)
                out["tools"].append((last_tool, m.group(2).lstrip("v")))
            elif not RELATIVE_RE.match(bare):
                out["notes"].append(tok)
        if tail:
            out["tools"].append((tail, None))
    out["tools"] = sorted(set(out["tools"]), key=lambda t: (t[0].lower(), t[1] or ""))
    out["pins"] = sorted(set(out["pins"]))
    return out


# --------------------------------------------------------------------------------------------
# small table readers
# --------------------------------------------------------------------------------------------
def numbered_rows(lines, start, stop, ncells):
    """Rows '| 12 | ... |' between two line indexes (0-based, stop exclusive): (line_no, n, cells)."""
    rows = []
    for i in range(start, stop):
        line = lines[i]
        m = re.match(r"^\|\s*(\d+)\s*\|", line)
        if not m:
            continue
        cells = L.split_row(line)
        rows.append((i + 1, int(m.group(1)), cells, len(cells) == ncells))
    return rows


def section_span(lines, heading_re):
    """(first, stop) 0-based line indexes of a '## ' section body."""
    start = next((i for i, l in enumerate(lines) if re.match(heading_re, l)), None)
    if start is None:
        raise SystemExit(f"section not found: {heading_re}")
    stop = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return start + 1, stop


def headline_of(cell):
    m = re.match(r"\s*\*\*(.+?)\*\*\s*(.*)$", cell, re.S)
    if not m:
        return clean(L.strip_md(cell)), ""
    return clean(L.strip_md(m.group(1))).rstrip("."), clean(L.strip_md(m.group(2)))


# --------------------------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------------------------
def build():
    A = Atlas()
    loom_sha = (HERE / "src" / "LOOM.sha").read_text().strip()
    docs_sha = (HERE / "src" / "DOCS.sha").read_text().strip()
    loom_link = f"https://github.com/{LOOM_REPO}/blob/{loom_sha}/LOOM-v1.md?plain=1#L"
    docs_link = f"https://github.com/{DOCS_REPO}/blob/{docs_sha}/docs/learn/"
    loom_src = f"x3d.loom@{loom_sha}:LOOM-v1.md"
    T = stated_totals()

    def docs_src(name):
        return f"x3d.docs@{docs_sha}:docs/learn/{name}"

    def add_pin(repo, sha, origin):
        pid = f"pin/{slug(repo)}@{sha[:12]}"
        n = A.node(pid, "Pin", label=f"{repo}@{sha[:12]}", repoName=repo, sha=sha[:12])
        n.setdefault("origins", [])
        if origin not in n["origins"]:
            n["origins"] = sorted(n["origins"] + [origin])
        rid = f"repo/{slug(repo)}"
        A.node(rid, "Repo", label=repo)
        A.edge(pid, "ofRepo", rid, "pin")
        return pid

    def add_doc(repo, sha, path, origin):
        did = f"doc/{slug(repo)}@{sha[:7]}/{re.sub(r'[^A-Za-z0-9._/~-]+', '-', path)}"
        A.node(did, "SourceDocument", label=f"{repo}@{sha[:7]}:{path}", path=path)
        A.edge(did, "atPin", add_pin(repo, sha[:12] if len(sha) < 40 else sha[:7], origin), "source document")
        return did

    def add_tool(name, version):
        tid = f"tool/{slug(name)}"
        A.node(tid, "Tool", label=name)
        if version is None:
            return tid
        vid = f"tool/{slug(name)}@{slug(version)}"
        A.node(vid, "ToolVersion", label=f"{name} {version}", version=version)
        A.edge(vid, "ofTool", tid, "instrument")
        return vid

    def link_refs(nid, text, where, pred="mentions", only=None):
        """Turn the ids cited in text into edges from nid. Unknown ids are findings, never edges."""
        for target, how in refs(text or ""):
            if how == "wide":
                A.find("wide range not expanded", node=nid, where=where, ref=target)
                continue
            kind = target.split("/")[0]
            if only and kind not in only:
                continue
            pending.append((nid, pred, target, where + ("" if how != "range" else " (range)")))

    def link_diags(nid, text, where, pred="mentions"):
        for code in DIAG_RE.findall(text or ""):
            if code not in NOT_DIAGNOSTICS:
                pending_diag.append((nid, pred, code, where))

    pending = []        # id references, resolved after every node exists
    pending_diag = []   # diagnostic references, resolved after the set of diagnostics is known

    # ---- grades -----------------------------------------------------------------------------
    for g, name, meaning in (("C", "Confirmed", "a named tool ran and showed it; the tool and version are named"),
                             ("L", "Likely", "read in code or a document, or reasoned, not run"),
                             ("S", "Suspected", "a hunch; anything a model wrote; any creative judgment")):
        A.node(f"grade/{g}", "Grade", label=name, code=g, text=meaning)

    # ---- LOOM-v1.md: laws (section 3) -------------------------------------------------------
    loom_lines = LOOM.read_text(encoding="utf-8").splitlines()
    loom_doc = add_doc("x3d.loom", loom_sha, "LOOM-v1.md", "atlas input")
    a, b = section_span(loom_lines, r"^## 3\. The laws")
    for line_no, n, cells, ok in numbered_rows(loom_lines, a, b, 4):
        if not ok:
            A.find("row with unexpected cell count", where=f"LOOM-v1.md:{line_no}", cells=len(cells))
            continue
        head, rest = headline_of(cells[1])
        lid = f"law/{n}"
        grades = sorted(set(re.findall(r"\(([CLS])[,)]", cells[3])))
        A.node(lid, "Law", n=n, label=f"Law {n}: {head}", headline=head, text=rest,
               forbids=clean(L.strip_md(cells[2])), paidForByText=clean(cells[3]),
               definedAt=loom_link + str(line_no), line=line_no)
        A.edge(lid, "quotedFrom", loom_doc, "LOOM-v1 §3")
        raw = loom_lines[line_no - 1]
        own_claim(A, lid, "headline", raw, "|".join(raw_cells(raw)[:2]), head, loom_src, line_no)
        for g in grades:
            A.edge(lid, "evidenceGrade", f"grade/{g}", "LOOM-v1 §3 paid for by")
        link_refs(lid, cells[3], "LOOM-v1 §3 paid for by", pred="paidForBy", only={"fm"})
        link_refs(lid, cells[3], "LOOM-v1 §3 paid for by", only={"law", "number", "heuristic", "drill"})
        link_refs(lid, cells[1] + " " + cells[2], "LOOM-v1 §3 law")
        link_diags(lid, " ".join(cells[1:]), "LOOM-v1 §3")
        for tag, cite in source_tags(cells[3]):
            A.node(f"source/{tag}", "Source", label=tag)
            A.edge(lid, "citesSource", f"source/{tag}", f"LOOM-v1 §3: [{cite}]")

    # ---- LOOM-v1.md: failure modes (section 8) ----------------------------------------------
    a, b = section_span(loom_lines, r"^## 8\. Known failure modes")
    for line_no, n, cells, ok in numbered_rows(loom_lines, a, b, 4):
        if not ok and len(cells) > 4 and re.fullmatch(r"\[.*\]", cells[-1]):
            A.find("table row with unescaped pipes, cells rejoined", where=f"LOOM-v1.md:{line_no}", row=n,
                   cells=len(cells))
            cells = [cells[0], "|".join(cells[1:-2]), cells[-2], cells[-1]]
        elif not ok:
            A.find("row with unexpected cell count", where=f"LOOM-v1.md:{line_no}", cells=len(cells))
            continue
        fid = f"fm/{n}"
        failure = clean(L.strip_md(cells[1]))
        A.node(fid, "FailureMode", n=n, label=f"Failure mode {n}", failure=failure, fix=clean(cells[2]),
               sourceText=clean(cells[3]), definedAt=loom_link + str(line_no), line=line_no)
        A.edge(fid, "quotedFrom", loom_doc, "LOOM-v1 §8")
        raw = loom_lines[line_no - 1]
        own_claim(A, fid, "failure", raw, "|".join(raw_cells(raw)[:2]), cells[1], loom_src, line_no)
        link_refs(fid, cells[2], "LOOM-v1 §8 fix", pred="fixedByLaw", only={"law"})
        link_refs(fid, cells[2], "LOOM-v1 §8 fix", only={"fm", "number", "heuristic", "drill"})
        link_refs(fid, cells[1], "LOOM-v1 §8 failure")
        link_diags(fid, cells[1] + " " + cells[2], "LOOM-v1 §8", pred="caughtBy")
        for m in RECUR_RE.finditer(cells[1] + " " + cells[2]):
            pending.append((fid, "recurredAs", f"fm/{m.group(1)}", "LOOM-v1 §8"))
        for trap in TRAP_RE.findall(cells[2]):
            A.node(f"trap/{trap}", "TrapRule", label=trap)
            A.edge(fid, "hasTrap", f"trap/{trap}", "LOOM-v1 §8 fix")
        for tag, cite in source_tags(cells[3]):
            A.node(f"source/{tag}", "Source", label=tag)
            A.edge(fid, "citesSource", f"source/{tag}", f"LOOM-v1 §8: [{cite}]")

    # ---- LOOM-v1.md: open questions (section 10) --------------------------------------------
    a, b = section_span(loom_lines, r"^## 10\. Open questions")
    for i in range(a, b):
        m = re.match(r"^(\d+)\.\s+(.*)$", loom_lines[i])
        if m:
            n = int(m.group(1))
            head, rest = headline_of(m.group(2))
            qid = f"question/{n}"
            A.node(qid, "OpenQuestion", n=n, label=f"Open question {n}: {head}", headline=head, text=rest,
                   definedAt=loom_link + str(i + 1), line=i + 1)
            A.edge(qid, "quotedFrom", loom_doc, "LOOM-v1 §10")
            own_claim(A, qid, "headline", loom_lines[i], m.group(1) + ".", head, loom_src, i + 1)
            link_refs(qid, m.group(2), "LOOM-v1 §10")
            link_diags(qid, m.group(2), "LOOM-v1 §10")

    # ---- chapters ---------------------------------------------------------------------------
    chs = L.chapters()
    code_to_ch = {}
    doc_of = {}
    lines_of = {}
    for c in chs:
        cid = f"chapter/{c.num}"
        code_to_ch[c.code] = cid
        doc_of[c.num] = add_doc("x3d.docs", docs_sha, f"docs/learn/{c.name}", "atlas input")
        lines_of[c.num] = c.text.splitlines()
        say_grade = L.grade_of(c.say[-12:]) if c.say else None
        A.node(cid, "Chapter", n=int(c.num), label=f"{c.num}. {c.title_plain}", title=c.title_plain, code=c.code,
               say=clean(L.strip_md(re.sub(r"\*\*\[[CLS]\]\*\*\s*$", "", c.say))),
               definedAt=docs_link + c.name, file=f"docs/learn/{c.name}")
        if say_grade:
            A.edge(cid, "grade", f"grade/{say_grade}", f"{c.name} Say it")
    for c in chs:
        cid = f"chapter/{c.num}"
        for m in re.finditer(r"\]\((\d\d)-[a-z0-9_\-]+\.md\)", c.meta.get("prerequisites", "")):
            if f"chapter/{m.group(1)}" in A.nodes:
                A.edge(cid, "requires", f"chapter/{m.group(1)}", f"{c.name} prerequisites")
        for m in PIN_AT_RE.finditer(c.text):
            A.edge(cid, "citesPin", add_pin(m.group(1), m.group(2), "chapter text"), c.name)

    def line_of(c, row_id, heading=False):
        rx = (r"^### " + re.escape(row_id) + r"\b") if heading else (r"^\|\s*" + re.escape(row_id) + r"\s*\|")
        m = re.search(rx, c.text, re.M)
        return c.text.count("\n", 0, m.start()) + 1 if m else None

    def link_instrument_parts(nid, parsed, where):
        for repo, sha, role in parsed["pins"]:
            A.edge(nid, "atPin", add_pin(repo, sha, "instrument" if role == "at" else f"instrument ({role})"), where)
        for name, version in parsed["tools"]:
            A.edge(nid, "usesTool", add_tool(name, version), where)

    # ---- numbers ----------------------------------------------------------------------------
    instrument_ids = {}

    def instrument_node(parsed):
        key = parsed["plain"]
        if key not in instrument_ids:
            iid = f"instrument/{slug(key)[:48].strip('-.')}-{hashlib.sha256(key.encode()).hexdigest()[:6]}"
            instrument_ids[key] = iid
            A.node(iid, "Instrument", label=key, asWritten=key, relative=parsed["relative"],
                   notes=parsed["notes"])
            if not parsed["relative"]:
                link_instrument_parts(iid, parsed, "instrument string")
        return instrument_ids[key]

    for c in chs:
        cid = f"chapter/{c.num}"
        last_explicit = None
        for r in c.numbers:
            if len(r) < 6:
                A.find("row with unexpected cell count", where=f"{c.name} {r[0]}", cells=len(r))
                continue
            nid = f"number/{r[0]}"
            ln = line_of(c, r[0])
            parsed = parse_instrument(r[4])
            iid = instrument_node(parsed)
            grade = L.grade_of(r[3])
            run = DATE_RE.search(r[5])
            A.node(nid, "Number", label=r[0], quantity=clean(L.strip_md(r[1])), value=clean(L.strip_md(r[2])),
                   instrumentText=parsed["plain"], sourceCell=clean(r[5]),
                   runDate=run.group(1) if run else None,
                   definedAt=f"{docs_link}{c.name}?plain=1#L{ln}" if ln else None, line=ln)
            A.edge(nid, "inChapter", cid, c.name)
            A.edge(nid, "quotedFrom", doc_of[c.num], f"{c.name} Numbers register")
            if ln:
                raw = lines_of[c.num][ln - 1]
                parts = raw_cells(raw)
                own_claim(A, nid, "value", raw, "|".join(parts[:3]), parts[3] if len(parts) > 3 else "",
                          docs_src(c.name), ln)
            if grade:
                A.edge(nid, "grade", f"grade/{grade}", f"{c.name} Numbers register")
            else:
                A.find("number without a readable grade", node=nid, cell=r[3])
            A.edge(nid, "measuredWith", iid, f"{c.name} Numbers register")
            if parsed["relative"]:
                if last_explicit is None:
                    A.find("relative instrument with nothing above it", node=nid, instrument=parsed["plain"])
                    A.nodes[nid]["instrumentResolution"] = "unresolved"
                else:
                    A.edge(nid, "resolvedInstrument", last_explicit, f"{c.name}: nearest explicit row above")
                    A.nodes[nid]["instrumentResolution"] = "inferred from the row above"
                    link_instrument_parts(nid, parsed, f"{c.name} Numbers register")   # "same, Node v22.23.4"
            else:
                last_explicit = iid
                A.edge(nid, "resolvedInstrument", iid, f"{c.name} Numbers register")
                A.nodes[nid]["instrumentResolution"] = "as written"
            for repo, sha, _ in parse_instrument(r[5])["pins"]:
                A.edge(nid, "atPin", add_pin(repo, sha, "number source"), f"{c.name} source cell")
            link_refs(nid, " ".join((r[1], r[2], r[5])), f"{c.name} Numbers register")
            link_diags(nid, " ".join((r[1], r[2], r[5])), f"{c.name} Numbers register")

    # ---- heuristics -------------------------------------------------------------------------
    for c in chs:
        cid = f"chapter/{c.num}"
        for r in c.heuristics:
            if len(r) < 5:
                A.find("row with unexpected cell count", where=f"{c.name} {r[0]}", cells=len(r))
                continue
            hid = f"heuristic/{r[0]}"
            ln = line_of(c, r[0])
            grade = L.grade_of(r[2])
            retired = bool(re.match(r"\s*~~", r[1]))
            A.node(hid, "Heuristic", label=r[0], rule=clean(L.strip_md(r[1])), evidence=clean(r[3]),
                   instrumentText=clean(L.strip_md(r[4])), retired=retired or None,
                   definedAt=f"{docs_link}{c.name}?plain=1#L{ln}" if ln else None, line=ln)
            A.edge(hid, "inChapter", cid, c.name)
            A.edge(hid, "quotedFrom", doc_of[c.num], f"{c.name} Heuristics")
            if ln:
                raw = lines_of[c.num][ln - 1]
                parts = raw_cells(raw)
                own_claim(A, hid, "rule", raw, "|".join(parts[:2]), parts[2] if len(parts) > 2 else "",
                          docs_src(c.name), ln)
            if grade:
                A.edge(hid, "grade", f"grade/{grade}", f"{c.name} Heuristics")
            else:
                A.find("heuristic without a readable grade", node=hid, cell=r[2])
            link_refs(hid, r[3], f"{c.name} Heuristics evidence", pred="evidencedBy")
            link_refs(hid, r[1], f"{c.name} Heuristics rule")
            link_diags(hid, r[1] + " " + r[3], f"{c.name} Heuristics")
            link_instrument_parts(hid, parse_instrument(r[4]), f"{c.name} Heuristics instrument")

    # ---- drills -----------------------------------------------------------------------------
    for c in chs:
        cid = f"chapter/{c.num}"
        for d in c.drills:
            did = f"drill/{d['id']}"
            ln = line_of(c, d["id"], heading=True)
            title = re.sub(r"^D-[A-Z]+-\d+\s*", "", d["head"])
            checked = d.get("checked", "").strip().split("\n")[0]
            ran = not re.match(r"\W*not run", checked, re.I)
            lvl = re.search(r"L[123]", d.get("level", ""))
            when = DATE_RE.search(checked)
            A.node(did, "Drill", label=f"{d['id']} {title}", title=title, level=lvl.group(0) if lvl else None,
                   task=clean(d.get("task", "")), verify=clean(d.get("verify", "")), answer=clean(d.get("answer", "")),
                   checkedText=clean(checked), status="ran" if ran else "not run",
                   checkedOn=when.group(1) if (ran and when) else None,
                   definedAt=f"{docs_link}{c.name}?plain=1#L{ln}" if ln else None, line=ln)
            A.edge(did, "inChapter", cid, c.name)
            A.edge(did, "quotedFrom", doc_of[c.num], f"{c.name} Drills")
            if ln:
                own_claim(A, did, "title", lines_of[c.num][ln - 1], "### " + d["id"], title, docs_src(c.name), ln)
            body = " ".join(d.get(k, "") for k in ("task", "verify", "answer"))
            link_refs(did, body + " " + title, f"{c.name} drill")
            link_diags(did, body, f"{c.name} drill")
            if ran:
                link_instrument_parts(did, parse_instrument(checked), f"{c.name} drill Checked")

    # ---- chapter 02: themes, checks, classes ------------------------------------------------
    ch02 = next(c for c in chs if c.num == "02")
    lines02 = ch02.text.splitlines()
    a, b = section_span(lines02, r"^## 2\. The laws, by theme")
    theme = None
    seen_in_theme = collections.Counter()
    ch02_headlines = {}
    for i in range(a, b):
        m = re.match(r"^### ([A-J])\. (.+)$", lines02[i])
        if m:
            theme = f"theme/{m.group(1)}"
            A.node(theme, "Theme", code=m.group(1), label=f"{m.group(1)}. {clean(m.group(2))}")
            continue
        m = re.match(r"^\|\s*(\d+)\s*\|", lines02[i])
        if not (m and theme):
            continue
        cells = L.split_row(lines02[i])
        n = int(m.group(1))
        lid = f"law/{n}"
        where = f"02-loom-laws.md:{i + 1}"
        if len(cells) != 5 or lid not in A.nodes:
            A.find("chapter 02 law row not matched", where=where, cells=len(cells))
            continue
        seen_in_theme[n] += 1
        ch02_headlines[n] = headline_of(cells[1])[0]
        check = clean(cells[4])
        kind = "code" if check.lower().startswith("code:") else "process" if check.lower().startswith("process:") else "other"
        A.node(lid, "Law", evidenceText=clean(cells[2]), violation=clean(L.strip_md(cells[3])), checkText=check,
               checkKind=kind)
        A.edge(lid, "inTheme", theme, where)
        link_refs(lid, cells[2], "ch 02 evidence", pred="paidForBy", only={"fm"})
        link_refs(lid, cells[2], "ch 02 evidence", only={"law", "number", "heuristic", "drill"})
        link_refs(lid, cells[3] + " " + cells[4], "ch 02 violation and check")
        if kind == "code":
            link_diags(lid, cells[4], "ch 02 check", pred="caughtBy")
        else:
            link_diags(lid, cells[4], "ch 02 check")
    for n in range(1, T["laws"] + 1):
        if seen_in_theme[n] != 1:
            A.find("law not in exactly one theme", law=n, times=seen_in_theme[n])
        elif A.nodes.get(f"law/{n}") and ch02_headlines[n] != A.nodes[f"law/{n}"]["headline"]:
            A.find("law headline differs between LOOM-v1 and chapter 02", law=n,
                   loom=A.nodes[f"law/{n}"]["headline"], chapter02=ch02_headlines[n])

    a, b = section_span(lines02, r"^## 3\. The failure-mode catalogue")
    class_of = collections.defaultdict(list)
    for i in range(a, b):
        m = re.match(r"^\|\s*(K\d+)\s*\|", lines02[i])
        if not m:
            continue
        cells = L.split_row(lines02[i])
        kid = f"class/{m.group(1)}"
        ids = [int(x) for x in re.findall(r"\d+", cells[3])]
        A.node(kid, "FailureClass", code=m.group(1), label=f"{m.group(1)}: {clean(L.strip_md(cells[1]))}",
               definedAt=f"{docs_link}02-loom-laws.md?plain=1#L{i + 1}", line=i + 1)
        A.edge(kid, "quotedFrom", doc_of["02"], "02-loom-laws.md §3")
        own_claim(A, kid, "name", lines02[i], "|".join(raw_cells(lines02[i])[:2]), cells[1], docs_src(ch02.name), i + 1)
        if int(cells[2]) != len(ids):
            A.find("class size does not match its id list", cls=m.group(1), stated=int(cells[2]), listed=len(ids))
        for n in ids:
            class_of[n].append(m.group(1))
            if f"fm/{n}" in A.nodes:
                A.edge(f"fm/{n}", "inClass", kid, f"02-loom-laws.md:{i + 1}")
        for n in re.findall(r"\*\*(\d+)\*\*", cells[4]):
            if f"fm/{n}" in A.nodes:
                A.edge(kid, "topOfClass", f"fm/{n}", f"02-loom-laws.md:{i + 1}")
        for src, dst in re.findall(r"\*\*(\d+)\*\*[^*]*?\(recurred as (\d+)\)", cells[4]):
            pending.append((f"fm/{src}", "recurredAs", f"fm/{dst}", f"02-loom-laws.md:{i + 1}"))
    for n in range(1, T["failure modes"] + 1):
        if len(class_of[n]) != 1:
            A.find("failure mode not in exactly one class", fm=n, classes=class_of[n])

    # ---- the claim ledgers of x3d.docs (docs/learn/claims/*.jsonl) and the checker's receipt --
    receipt = json.loads((LEARN / "claims" / "receipt.json").read_text(encoding="utf-8"))
    checked = collections.defaultdict(list)
    for e in receipt["entries"]:
        checked[(e["chapter"], e["id"], json.dumps(e["value"]), e["source"])].append(e)
    for path in sorted((LEARN / "claims").glob("*.jsonl")):
        meta, entries, problems = CL.load_ledger(path)
        chap = path.name[:2]
        for prob in problems:
            A.find("claim ledger line not read", file=path.name, problem=prob)
        for e in entries:
            cid = f"claim/{chap}-{e['_line']}"
            key = (chap, e["id"], json.dumps(e.get("value")), e.get("source"))
            rec = checked[key].pop(0) if checked[key] else None
            if rec is None:
                A.find("claim with no row in the receipt", claim=cid, id=e["id"])
            shown = json.dumps(e.get("value"), ensure_ascii=False)
            A.node(cid, "Claim", label=f"{e['id']} = {shown}", claimValue=shown, quote=e.get("quote"),
                   sourceRef=e.get("source"), sourceKind=CL.kind_of(e.get("source")), cell=e.get("in", "value"),
                   verdict=rec["verdict"] if rec else "no receipt row", quoteLine=rec.get("line") if rec else None,
                   definedAt=f"{docs_link}claims/{path.name}#L{e['_line']}", line=e["_line"])
            A.edge(cid, "inChapter", f"chapter/{chap}", path.name)
            target = f"{PREFIX[e['id'][0]]}/{e['id']}" if e["id"][0] in PREFIX else None
            if target in A.nodes:
                A.edge(cid, "supports", target, path.name)
            elif target:
                A.find("claim about an id that does not exist", claim=cid, id=e["id"])
            if e.get("grade"):
                A.edge(cid, "grade", f"grade/{e['grade']}", path.name)
            m = CL.SOURCE_RE.match(e.get("source") or "")
            if m:
                A.edge(cid, "quotedFrom", add_doc(m.group(1), m.group(2), m.group(3), "claim ledger"), path.name)
                pin = add_pin(m.group(1), m.group(2), "claim ledger")
                A.edge(cid, "atPin", pin, path.name)
                A.edge(f"chapter/{chap}", "citesPin", pin, path.name)      # Appendix F counts ledger pins too
            if e.get("from") and target:
                pending.append((target, "carriedFrom", f"{PREFIX.get(e['from'][0], 'x')}/{e['from']}", path.name))

    # ---- resolve the pending references -----------------------------------------------------
    for s, p, o, where in pending:
        if o in A.nodes:
            A.edge(s, p, o, where)
        else:
            A.find("reference to an id that does not exist", node=s, ref=o, where=where)
    diag_defined = {code for s, p, code, where in pending_diag if p == "caughtBy"}
    diag_defined |= set(DIAG_RE.findall(LOOM.read_text(encoding="utf-8"))) - NOT_DIAGNOSTICS
    for s, p, code, where in pending_diag:
        if code in diag_defined:
            A.node(f"diag/{code}", "Diagnostic", label=code)
            A.edge(s, p, f"diag/{code}", where)

    # ---- the dataset itself -----------------------------------------------------------------
    ds = "dataset/atlas-v0"
    A.node(ds, "Dataset", label="The Atlas, version 0",
           text="Laws, failure modes, numbers, heuristics, drills, instruments and pins of the X3D Loom, as one graph.",
           loomSha=loom_sha, docsSha=docs_sha, loomSha256=sha256_of(LOOM),
           inputFiles=len(chs) + 1)
    A.edge(ds, "derivedFrom", add_pin("x3d.loom", loom_sha[:7], "atlas input"), "src/LOOM.sha")
    A.edge(ds, "derivedFrom", add_pin("x3d.docs", docs_sha[:7], "atlas input"), "src/DOCS.sha")
    A.stated = T
    return A, chs


# --------------------------------------------------------------------------------------------
# vocabulary: one table drives the JSON-LD context, the Turtle writer and atlas-vocab.ttl
# --------------------------------------------------------------------------------------------
CLASSES = {
    "Law": "A numbered law of the Loom (LOOM-v1.md section 3).",
    "FailureMode": "A numbered failure someone paid for, with its fix (LOOM-v1.md section 8).",
    "FailureClass": "Chapter 02's grouping of the failure modes, K1 to K11. A reading, not a Loom id.",
    "Theme": "Chapter 02's grouping of the laws, A to J.",
    "Diagnostic": "A stable diagnostic code raised by loomkit or a witness.",
    "TrapRule": "A named trap rule of the validator.",
    "OpenQuestion": "A numbered open question (LOOM-v1.md section 10).",
    "Number": "A measured or carried quantity in a chapter's Numbers register.",
    "Heuristic": "A rule of thumb in a chapter's Heuristics table.",
    "Drill": "An exercise with a task, a verify command and an answer key.",
    "Chapter": "A chapter of the learning base.",
    "Instrument": "An instrument string exactly as written in a Numbers register.",
    "Tool": "A program named inside an instrument string.",
    "ToolVersion": "A tool at a named version.",
    "Pin": "A repository at a commit.",
    "Repo": "A repository, by name.",
    "SourceDocument": "A file at a commit: repo@sha:path. The same idea as x3dprov's SourceDocument.",
    "Claim": "One line of a chapter's claim ledger (claims/0.1): a value, the quote that holds it, its source, and the "
             "checker's verdict from the receipt.",
    "Source": "A source id cited by LOOM-v1.md (defined in the Loom's SOURCES.md, not read here).",
    "Grade": "C, L or S.",
    "Dataset": "This graph.",
}
# key -> (kind, comment). kind: str | int | bool | date | iri (absolute link) | ref (edge to a node)
PROPS = {
    "label": ("str", None), "n": ("int", "The stable number of a law, failure mode, question or chapter."),
    "headline": ("str", None), "text": ("str", None), "forbids": ("str", None),
    "paidForByText": ("str", "LOOM-v1 section 3, column 'Paid for by', as written."),
    "evidenceText": ("str", "Chapter 02, column 'evidence', as written."),
    "violation": ("str", "Chapter 02, column 'typical violation'."),
    "checkText": ("str", "Chapter 02, column 'check', as written."),
    "checkKind": ("str", "'code' when a mechanical check exists in the kit, 'process' when only review does."),
    "failure": ("str", None), "fix": ("str", None), "sourceText": ("str", None),
    "quantity": ("str", None), "value": ("str", "The value as written; not parsed."),
    "instrumentText": ("str", None), "sourceCell": ("str", None), "runDate": ("date", None),
    "instrumentResolution": ("str", "'as written', 'inferred from the row above' or 'unresolved'."),
    "rule": ("str", None), "evidence": ("str", None), "retired": ("bool", None),
    "title": ("str", None), "level": ("str", None), "task": ("str", None), "verify": ("str", None),
    "answer": ("str", None), "checkedText": ("str", None), "status": ("str", "'ran' or 'not run'."),
    "checkedOn": ("date", None), "code": ("str", None), "say": ("str", None), "file": ("str", None),
    "asWritten": ("str", None), "relative": ("bool", "True when the string points at another row ('same')."),
    "notes": ("str", "Parts of an instrument string the builder could not name as a tool, a pin or a date."),
    "version": ("str", None), "repoName": ("str", None), "sha": ("str", None), "origins": ("str", None),
    "line": ("int", "Line in the source file at the pin."),
    "definedAt": ("iri", "Permalink to the defining line at the pinned commit."),
    "path": ("str", None), "claimValue": ("str", "The claimed value, as JSON."),
    "quote": ("str", "The words the value was read from, as published in the ledger."),
    "sourceRef": ("str", "The ledger's source string: repo@sha:path, self:, external: or private:."),
    "sourceKind": ("str", None), "cell": ("str", "Which register cell holds the value."),
    "verdict": ("str", "verified, check, reworded or unchecked: the checker's word, read from the receipt."),
    "quoteLine": ("int", "Line of the quote in its source, from the receipt."),
    "loomSha": ("str", None), "docsSha": ("str", None), "loomSha256": ("str", None), "inputFiles": ("int", None),
    # edges
    "paidForBy": ("ref", "Law to failure mode: cited in the law's 'paid for by' or 'evidence' column."),
    "fixedByLaw": ("ref", "Failure mode to law: the fix column cites the law."),
    "caughtBy": ("ref", "Law or failure mode to the diagnostic that catches it."),
    "hasTrap": ("ref", "Failure mode to the trap rule named in its fix."),
    "recurredAs": ("ref", "Failure mode to the later failure mode it recurred as."),
    "inTheme": ("ref", None), "inClass": ("ref", None),
    "topOfClass": ("ref", "Class to one of its three costliest failure modes (chapter 02's choice)."),
    "inChapter": ("ref", None), "grade": ("ref", None), "evidenceGrade": ("ref", "A grade cited in a law's evidence."),
    "measuredWith": ("ref", "Number to its instrument string as written."),
    "resolvedInstrument": ("ref", "Number to the instrument it stands on, after following 'same'."),
    "usesTool": ("ref", None), "ofTool": ("ref", None), "atPin": ("ref", None), "ofRepo": ("ref", None),
    "evidencedBy": ("ref", "Heuristic to a number, drill, law or failure mode cited in its evidence column."),
    "mentions": ("ref", "Any other citation of a stable id."),
    "citesPin": ("ref", None), "requires": ("ref", "Chapter to a prerequisite chapter."),
    "quotedFrom": ("ref", "The file at a commit a row or a quote was copied from. Mapped to prov:wasQuotedFrom."),
    "supports": ("ref", "Claim to the number or heuristic it gives a quote for."),
    "carriedFrom": ("ref", "A number taken from another row (the ledger's 'from'); its grade may not rise."),
    "citesSource": ("ref", None), "derivedFrom": ("ref", "Mapped to prov:wasDerivedFrom."),
}
STANDARD = {"label": "rdfs:label", "definedAt": "dcterms:source", "derivedFrom": "prov:wasDerivedFrom",
            "quotedFrom": "prov:wasQuotedFrom"}
PREFIXES = [("atlas", VOCAB), ("rdfs", "http://www.w3.org/2000/01/rdf-schema#"),
            ("xsd", "http://www.w3.org/2001/XMLSchema#"), ("dcterms", "http://purl.org/dc/terms/"),
            ("prov", "http://www.w3.org/ns/prov#"), ("owl", "http://www.w3.org/2002/07/owl#")]


def curie(key):
    return STANDARD.get(key, f"atlas:{key}")


def merged(A):
    """Nodes with their outgoing edges folded in as lists of ids, sorted: the shape both writers use."""
    out = {nid: dict(n) for nid, n in A.nodes.items()}
    for (s, p, o) in A.edges:
        out[s].setdefault(p, []).append(o)
    for n in out.values():
        for k, v in n.items():
            if isinstance(v, list):
                n[k] = sorted(set(v))
    return [out[k] for k in sorted(out)]


def write_jsonld(nodes, path):
    ctx = {"@base": BASE, "@vocab": VOCAB}
    ctx.update({p: iri for p, iri in PREFIXES})
    for key, (kind, _) in PROPS.items():
        term = {"@id": curie(key)}
        if kind in ("ref", "iri"):
            term["@type"] = "@id"
        elif kind == "date":
            term["@type"] = "xsd:date"
        ctx[key] = term if len(term) > 1 or key in STANDARD else curie(key)
    graph = []
    for n in nodes:
        item = {"@id": n["id"], "@type": n["type"]}
        for k, v in n.items():
            if k not in ("id", "type"):
                item[k] = v
        graph.append(item)
    path.write_text(json.dumps({"@context": ctx, "@graph": graph}, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8")


def ttl_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t") + '"'


def ttl_value(kind, v):
    if kind == "ref":
        return f"<{v}>"
    if kind == "iri":
        return f"<{v}>"
    if kind == "int":
        return str(int(v))
    if kind == "bool":
        return "true" if v else "false"
    if kind == "date":
        return f'{ttl_str(v)}^^xsd:date'
    return ttl_str(str(v))


def write_turtle(nodes, path):
    out = [f"@base <{BASE}> ."] + [f"@prefix {p}: <{iri}> ." for p, iri in PREFIXES] + [""]
    for n in nodes:
        parts = [f"a atlas:{n['type']}"]
        for k in sorted(k for k in n if k not in ("id", "type")):
            kind = PROPS[k][0]
            vals = n[k] if isinstance(n[k], list) else [n[k]]
            parts.append(f"{curie(k)} " + ", ".join(ttl_value(kind, v) for v in vals))
        out.append(f"<{n['id']}> " + " ;\n    ".join(parts) + " .\n")
    path.write_text("\n".join(out), encoding="utf-8")


def write_vocab(path):
    out = [f"@prefix {p}: <{iri}> ." for p, iri in PREFIXES] + [
        "", f"<{VOCAB[:-1]}> a owl:Ontology ; rdfs:label \"The Atlas vocabulary, version 0\" .", ""]
    for name, comment in CLASSES.items():
        out.append(f"atlas:{name} a rdfs:Class ; rdfs:label {ttl_str(name)} ; rdfs:comment {ttl_str(comment)} .")
    out.append("")
    for key, (kind, comment) in PROPS.items():
        if key in STANDARD:
            continue
        typ = "owl:ObjectProperty" if kind == "ref" else "owl:DatatypeProperty"
        line = f"atlas:{key} a {typ} ; rdfs:label {ttl_str(key)}"
        if comment:
            line += f" ; rdfs:comment {ttl_str(comment)}"
        out.append(line + " .")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------------------------
# what the graph shows
# --------------------------------------------------------------------------------------------
def analyse(A, chs):
    nodes, edges = A.nodes, A.edges
    by_type = collections.Counter(n["type"] for n in nodes.values())
    outs = collections.defaultdict(lambda: collections.defaultdict(set))
    ins = collections.defaultdict(lambda: collections.defaultdict(set))
    for (s, p, o) in edges:
        outs[s][p].add(o)
        ins[o][p].add(s)
    R = {"counts": dict(sorted(by_type.items())),
         "edges": dict(sorted(collections.Counter(p for (_, p, _) in edges).items())),
         "edge total": len(edges)}

    # parity with the expected totals and with the appendices x3d.docs generates itself
    def appendix_rows(name, id_re):
        text = (LEARN / name).read_text(encoding="utf-8")
        return [L.split_row(l) for l in text.splitlines() if re.match(r"^\|\s*" + id_re, l)]
    app_c = appendix_rows("C-numbers-ledger.md", r"N-[A-Z]{2,4}-\d+")
    app_d = appendix_rows("D-heuristics-ledger.md", r"H-[A-Z]{2,4}-\d+")
    app_e = appendix_rows("E-drills.md", r"D-[A-Z]{2,4}-\d+")
    app_f = appendix_rows("F-source-map.md", r"`[^`]+`\s*\|\s*`[0-9a-f]{7,12}`")
    app_a = appendix_rows("A-validator-register.md", r"`")
    chapter_pins = {o for (s, p, o) in edges if p == "citesPin"}
    ran = sum(1 for n in nodes.values() if n["type"] == "Drill" and n["status"] == "ran")
    T = A.stated

    def grade_of(nid):
        g = outs[nid]["grade"]
        return sorted(g)[0][-1] if g else "?"

    def grade_table(t):
        c = collections.Counter(grade_of(nid) for nid, n in nodes.items() if n["type"] == t)
        return {g: c[g] for g in ("C", "L", "S", "?") if c[g] or g != "?"}
    claim_verdicts = collections.Counter(n["verdict"] for n in nodes.values() if n["type"] == "Claim")
    parity = [
        ("laws vs chapter 02's statement", by_type["Law"], T["laws"]),
        ("failure modes vs chapter 02's statement", by_type["FailureMode"], T["failure modes"]),
        ("failure classes vs chapter 02's statement", by_type["FailureClass"], T["failure classes"]),
        ("chapters vs Appendix C's statement", by_type["Chapter"], T["chapters"]),
        ("numbers vs Appendix C's statement", by_type["Number"], T["numbers"]),
        ("numbers vs Appendix C's rows", by_type["Number"], len(app_c)),
        ("number grades vs Appendix C's statement", grade_table("Number"), T["number grades"]),
        ("heuristics vs Appendix D's statement", by_type["Heuristic"], T["heuristics"]),
        ("heuristics vs Appendix D's rows", by_type["Heuristic"], len(app_d)),
        ("heuristic grades vs Appendix D's statement", grade_table("Heuristic"), T["heuristic grades"]),
        ("drills vs Appendix E's statement", by_type["Drill"], T["drills"]),
        ("drills vs Appendix E's rows", by_type["Drill"], len(app_e)),
        ("drills with a recorded run vs Appendix E's statement", ran, T["drills run"]),
        ("instrument strings vs Appendix A's statement", by_type["Instrument"], T["instrument strings"]),
        ("instrument strings vs Appendix A's rows", by_type["Instrument"], len(app_a)),
        ("pins cited by chapters vs Appendix F's statement", len(chapter_pins), T["pins"]),
        ("pins cited by chapters vs Appendix F's rows", len(chapter_pins), len(app_f)),
        ("claims vs Appendix G's statement", by_type["Claim"], T["claims"]),
        ("claim verdicts vs Appendix G's statement",
         {k: claim_verdicts[k] for k in ("verified", "check", "reworded", "unchecked")}, T["claim verdicts"]),
    ]
    R["parity"] = [{"what": w, "atlas": a, "expected": e, "ok": a == e} for w, a, e in parity]
    ids_c = {r[0] for r in app_c}
    R["ids missing from one side"] = sorted(({n["label"] for n in nodes.values() if n["type"] == "Number"}) ^ ids_c)

    R["grades"] = {"numbers": grade_table("Number"), "heuristics": grade_table("Heuristic")}

    # laws and failure modes
    law_fms = {}
    for nid, n in nodes.items():
        if n["type"] != "Law":
            continue
        linked = outs[nid]["paidForBy"] | {o for o in outs[nid]["mentions"] if o.startswith("fm/")} \
            | ins[nid]["fixedByLaw"] | {s for s in ins[nid]["mentions"] if s.startswith("fm/")}
        law_fms[nid] = linked
    R["laws by linked failure modes"] = [
        {"law": nodes[l]["n"], "headline": nodes[l]["headline"], "failure modes": len(f),
         "check": nodes[l].get("checkKind", "?"), "diagnostics": len(outs[l]["caughtBy"])}
        for l, f in sorted(law_fms.items(), key=lambda kv: (-len(kv[1]), nodes[kv[0]]["n"]))]
    R["laws with no failure mode cited by number"] = sorted(nodes[l]["n"] for l, f in law_fms.items() if not f)
    linked_fms = set().union(*law_fms.values())
    orphans = sorted(n["n"] for nid, n in nodes.items() if n["type"] == "FailureMode" and nid not in linked_fms)
    R["failure modes linked to no law"] = {"count": len(orphans), "ids": orphans}
    by_class = collections.defaultdict(lambda: [0, 0])
    for nid, n in nodes.items():
        if n["type"] == "FailureMode":
            k = sorted(outs[nid]["inClass"])[0].split("/")[1] if outs[nid]["inClass"] else "?"
            by_class[k][0] += 1
            by_class[k][1] += nid not in linked_fms
    R["failure classes"] = [{"class": k, "name": nodes[f"class/{k}"]["label"], "failure modes": v[0],
                             "linked to no law": v[1]}
                            for k, v in sorted(by_class.items(), key=lambda kv: int(kv[0][1:]) if kv[0] != "?" else 99)]
    R["process-only laws ranked by failures"] = [
        r for r in R["laws by linked failure modes"] if r["check"] == "process"]
    R["check kinds"] = dict(collections.Counter(n.get("checkKind", "?") for n in nodes.values() if n["type"] == "Law"))
    R["diagnostics"] = sorted(
        ({"code": n["label"], "laws": sorted(nodes[s]["n"] for s in ins[nid]["caughtBy"] if s.startswith("law/")),
          "failure modes": sorted(nodes[s]["n"] for s in ins[nid]["caughtBy"] if s.startswith("fm/"))}
         for nid, n in nodes.items() if n["type"] == "Diagnostic"), key=lambda d: d["code"])
    R["trap rules"] = sorted(
        ({"trap": n["label"], "failure modes": sorted(nodes[s]["n"] for s in ins[nid]["hasTrap"])}
         for nid, n in nodes.items() if n["type"] == "TrapRule"), key=lambda d: d["trap"])
    R["recurrences"] = sorted([nodes[s]["n"], nodes[o]["n"]] for (s, p, o) in edges if p == "recurredAs")

    # numbers: how each one is held
    res = collections.Counter(n.get("instrumentResolution", "?") for n in nodes.values() if n["type"] == "Number")
    R["number instruments"] = dict(sorted(res.items()))

    def footing(nid):
        inst = sorted(outs[nid]["resolvedInstrument"])
        pins = set(outs[nid]["atPin"])
        tools = set(outs[nid]["usesTool"])
        for i in inst:
            pins |= outs[i]["atPin"]
            tools |= outs[i]["usesTool"]
        return pins, tools
    weak = []
    for nid, n in nodes.items():
        if n["type"] == "Number" and grade_of(nid) == "C":
            pins, tools = footing(nid)
            versions = {t for t in tools if "@" in t}
            if not pins and not versions:
                weak.append(n["label"])
    R["Confirmed numbers with no pin and no versioned tool in their instrument"] = {
        "count": len(weak), "ids": sorted(weak, key=lambda s: (s.split("-")[1], int(s.split("-")[2])))}

    tool_use = collections.defaultdict(lambda: collections.defaultdict(set))
    pin_use = collections.defaultdict(lambda: collections.defaultdict(set))
    for nid, n in nodes.items():
        if n["type"] != "Number":
            continue
        pins, tools = footing(nid)
        for t in tools:
            if "@" in t:
                fam = sorted(outs[t]["ofTool"])[0]
                tool_use[nodes[fam]["label"]][nodes[t]["version"]].add(n["label"])
        for p in pins:
            pin_use[nodes[p]["repoName"]][nodes[p]["sha"]].add(n["label"])
    R["tool versions under the numbers"] = {
        name: {v: len(ids) for v, ids in sorted(vs.items())}
        for name, vs in sorted(tool_use.items(), key=lambda kv: -sum(len(i) for i in kv[1].values()))
        if sum(len(i) for i in vs.values()) >= 5}
    R["pins under the numbers"] = {
        repo: {sha: len(ids) for sha, ids in sorted(shas.items(), key=lambda kv: -len(kv[1]))}
        for repo, shas in sorted(pin_use.items(), key=lambda kv: -sum(len(i) for i in kv[1].values()))}
    R["unnamed instrument parts"] = collections.Counter(
        note for n in nodes.values() if n["type"] == "Instrument" for note in n.get("notes", [])).most_common(25)
    R["instrument strings fully named"] = sum(
        1 for n in nodes.values() if n["type"] == "Instrument" and not n.get("relative") and not n.get("notes"))

    # heuristics: can the graph trace the claim?
    untraced = collections.Counter()
    untraced_c = []
    for nid, n in nodes.items():
        if n["type"] == "Heuristic":
            if not outs[nid]["evidencedBy"]:
                untraced[grade_of(nid)] += 1
                if grade_of(nid) == "C":
                    untraced_c.append(n["label"])
    R["heuristics whose evidence cites no id"] = {"by grade": dict(sorted(untraced.items())),
                                                  "Confirmed": sorted(untraced_c)}
    cited = collections.Counter()
    for (s, p, o) in edges:
        if p in ("evidencedBy", "mentions") and o.startswith("number/"):
            cited[o] += 1
    R["numbers cited most"] = [{"id": nodes[o]["label"], "times": c, "quantity": nodes[o]["quantity"][:90]}
                               for o, c in cited.most_common(10)]
    R["numbers cited by nothing"] = by_type["Number"] - len(cited)
    quoted = collections.defaultdict(set)
    for (s, p, o) in edges:
        if p == "supports":
            quoted[o].add(nodes[s]["verdict"])
    per_ch = collections.defaultdict(lambda: [0, 0, 0])
    c_total = c_verified = 0
    for nid, n in nodes.items():
        if n["type"] != "Number":
            continue
        ch = sorted(outs[nid]["inChapter"])[0].split("/")[1]
        per_ch[ch][0] += 1
        per_ch[ch][1] += bool(quoted[nid])
        per_ch[ch][2] += "verified" in quoted[nid]
        if grade_of(nid) == "C":
            c_total += 1
            c_verified += "verified" in quoted[nid]
    R["traceability"] = {
        "numbers": by_type["Number"],
        "numbers with a ledger quote": sum(v[1] for v in per_ch.values()),
        "numbers with a verified quote": sum(v[2] for v in per_ch.values()),
        "Confirmed numbers": c_total, "Confirmed numbers with a verified quote": c_verified,
        "heuristics with a ledger quote": sum(1 for nid in quoted if nid.startswith("heuristic/")),
        "chapters with a ledger": sorted(ch for ch, v in per_ch.items() if v[1]),
        "by chapter": {ch: {"numbers": v[0], "quoted": v[1], "verified": v[2]} for ch, v in sorted(per_ch.items())},
        "claims by kind of source": dict(sorted(collections.Counter(
            n.get("sourceKind") or "?" for n in nodes.values() if n["type"] == "Claim").items())),
        "claims on a prose statement (Q- ids)": sum(
            1 for nid, n in nodes.items() if n["type"] == "Claim" and not outs[nid]["supports"]),
        "pins the claims stand on": sorted({nodes[o]["label"] for (s, p, o) in edges
                                            if p == "atPin" and s.startswith("claim/")}),
        "carried numbers": sorted([nodes[s]["label"], nodes[o]["label"]] for (s, p, o) in edges if p == "carriedFrom"),
    }
    R["atlas claims written"] = len(A.claims)
    R["drills not run"] = sorted(n["label"] for n in nodes.values() if n["type"] == "Drill" and n["status"] != "ran")

    # pins
    pins = [n for n in nodes.values() if n["type"] == "Pin"]
    R["pins"] = {"total": len(pins), "cited by chapters": len(chapter_pins),
                 "named only inside an instrument or a source cell":
                     sorted(n["label"] for n in pins if "chapter text" not in n["origins"] and "atlas input" not in n["origins"])}
    loom_pins = sorted({nodes[p]["sha"] for p in chapter_pins if nodes[p]["repoName"] == "x3d.loom"})
    R["x3d.loom commits the chapters read"] = loom_pins
    R["x3d.loom commit this Atlas read"] = nodes["dataset/atlas-v0"]["loomSha"][:7]
    R["findings"] = {k: v for k, v in sorted(A.findings.items())}
    return R


def main():
    OUT.mkdir(exist_ok=True)
    A, chs = build()
    nodes = merged(A)
    edge_list = [{"s": s, "p": p, "o": o, "where": sorted(w)} for (s, p, o), w in sorted(A.edges.items())]
    report = analyse(A, chs)
    meta = {"name": "The Atlas", "version": "0", "base": BASE, "vocab": VOCAB,
            "inputs": {"x3d.loom": A.nodes["dataset/atlas-v0"]["loomSha"], "x3d.docs": A.nodes["dataset/atlas-v0"]["docsSha"]},
            "counts": report["counts"], "edges": report["edges"]}
    (OUT / "atlas.json").write_text(json.dumps({"meta": meta, "nodes": [A.nodes[k] for k in sorted(A.nodes)],
                                                "edges": edge_list}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    write_jsonld(nodes, OUT / "atlas.jsonld")
    write_turtle(nodes, OUT / "atlas.ttl")
    write_vocab(OUT / "atlas-vocab.ttl")
    head = {"_meta": {"schema": CL.SCHEMA, "note": "one row per value the Atlas copied from a source line: the value's "
                      "first words, the quote that holds them on that line, the file at the pinned commit",
                      "coverage_floor": 1.0}}
    (OUT / "atlas-claims.jsonl").write_text(
        "\n".join(json.dumps(o, ensure_ascii=False, sort_keys=True) for o in [head] + A.claims) + "\n", encoding="utf-8")
    (OUT / "findings.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    bad = [p for p in report["parity"] if not p["ok"]]
    print(f"nodes {len(A.nodes)}  edges {len(A.edges)}")
    for k, v in report["counts"].items():
        print(f"  {k:14s} {v}")
    for p in report["parity"]:
        print(f"  {'ok ' if p['ok'] else 'RED'} {p['what']}: {p['atlas']}" + ("" if p["ok"] else f" (expected {p['expected']})"))
    print(f"  own claims written: {len(A.claims)}")
    for k, v in A.findings.items():
        print(f"  finding: {k}: {len(v)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
