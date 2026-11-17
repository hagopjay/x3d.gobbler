# 04. x3d_mcp as the agent interface

> **Say it:** x3d_mcp gives a model 53 callable tools whose answers are small, structured and checkable, tells it the canonical path on connect, and keeps big documents and hostile queries out of its context with guards that live in the tool, not in the prompt. **[C]**

| field | value |
|---|---|
| chapter code | `MCP` |
| prerequisites | [03 The validator and the gates](03-validator-and-gates.md) (the rungs these tools wrap); [01 The tether](01-the-tether.md) |
| after this you can | list the tool families and say which tools exist on a given transport; pick the tool for a task and predict how many bytes come back; move a 10 MB scene through the server without pasting it; read a guard refusal; reproduce a tool transcript without an MCP client; say which agent-benefit claims are measured and which are only stated |
| sources read | x3d_mcp@b4efcd3:src/server.py, src/tools/*.py, src/transfer/*.py, src/x3d_utils/ontology_guard.py, README.md, docs/transfer-layer.md, docs/splats.md, docs/playground/ARCHITECTURE.md, docs/EXACT-FIX-HINTS.md, tests/; x3d.docs@f172f67:docs/x3d_mcp/MASTERCLASS.md |
| instruments used | `x3d_mcp fork b4efcd3`; `x3d_mcp upstream 74da0ec` (tools/list size only); `mcp` 1.30.0 (FastMCP, in process); `X3D XSD 4.0`, `X3D XSD 4.1`; Python 3.13.18; lxml 6.1.3 (libxml2 2.14.6); software only (4 vCPU Intel Xeon 2.30 GHz, no GPU) |

Rig for every number marked **[C]**: a fresh virtualenv installed from the ranges in the repo's `pyproject.toml` (`mcp>=1.29,<2` resolved to 1.30.0; `x3d` 4.0.65.8, `rdflib` 7.6.0, `pyshacl` 0.40.2, `numpy` 2.5.4, `zstandard` 0.25.0, `brotli` 1.2.1), 2026-11-14, source checkouts read-only. **No MCP client was used.** Tools were called as Python functions through a stand-in that records what `register(mcp)` decorates (section 8), and the list sizes came from FastMCP's own `list_tools()`. Nothing that costs money or needs a model, GPU or browser was run.

## 1. The map

```text
   MCP client (a model's host)
        |  stdio (default)             or          streamable-http  /mcp  (+ /blob)
        v                                                  v
   +--------------------- src/server.py (FastMCP "x3d-mcp") ---------------------+
   |  INSTRUCTIONS: the path, the traps, blob and splat paragraphs (conditional)  |
   |  12 register(mcp) calls, plus blob tools and splat tools when enabled        |
   +----+----------+----------+----------+----------+----------+----------+------+
        |          |          |          |          |          |          |
     workflow   granular    query     validate   scene_ops  semantics   transfer
     3 tools    9 tools    4 tools    6 tools    3 tools    5 tools     4 tools
        |          |          |          |          |          |          |
        +----------+----------+----+-----+----------+----------+----------+
                                    v
     validation/ (rungs of chapter 03)   x3d_utils/ (X3DUOM, ontology)   transfer/
     7 of 13 tool families drawn; the table below lists all
```

| family (module) | tools | n | returns | note |
|---|---|---|---|---|
| validate (`validate_tool`) | `validate_x3d`, `validate_semantic`, `validate_current_scene`, `autofix_x3d`, `repair_x3d`, `exact_fix_hints` | 6 | JSON; `validate_semantic` is markdown by default | the rungs of [chapter 03](03-validator-and-gates.md) |
| granular | `create_node`, `set_field`, `add_child`, `add_route`, `def_node`, `use_node`, `remove_node`, `get_scene`, `reset_scene` | 9 | text | an in-memory scene per session |
| workflow | `create_scene`, `create_geometry`, `compose_scene` | 3 | X3D text (xml, json or vrml) | 512 B for one box |
| query | `list_nodes`, `describe_node`, `list_components`, `list_profiles` | 4 | JSON | `describe_node('Material')` is 21,310 chars |
| scene_ops | `modify_x3d_node`, `remove_x3d_node`, `move_x3d_node` | 3 | document or envelope | take `blob_id` and `return_mode` |
| animate | `animate_x3d_node`, `add_x3d_route`, `x3d_animation_info` | 3 | text | |
| convert | `convert_x3d`, `x3d_generation_schema` | 2 | document or envelope | `x3d_generation_schema` came in PR #12 (masterclass) |
| render | `x3dom_page`, `render_image`, `render_current_scene`, `x3dom_starter` | 4 | HTML or PNG | `render_image` needs Playwright and Chromium (optional extra) |
| semantics | `query_ontology`, `query_ontology_page`, `node_parents`, `describe_ontology_term`, `where_can_place` | 5 (+2 resources) | JSON | guarded SPARQL |
| semantic_web | `scene_to_rdf`, `sparql_scene`, `shacl_validate`, `rdf_infer`, `ontology_vs_gate` | 5 | JSON | [chapter 05](05-semantic-layer.md) |
| claims | `claim_append`, `claims_page`, `claims_verify` | 3 | JSON | hash-chained ledger |
| splats | `splat_inspect`, `splat_chunk` | 2 | JSON | needs numpy; over HTTP needs the blob store |
| transfer | `blob_put`, `blob_info`, `blob_read`, `blob_delete` | 4 | JSON | registered only when the store is on |
| **total** | | **53** | | prompts 5, resources 2 |

Counted three ways at `b4efcd3`, **[C]**: Python `ast` over the `@mcp.tool` decorators (53 tools, 5 prompts, 2 resources), a run of every `register(mcp)` against a recording stand-in (53, 5, 2), and FastMCP `list_tools()` on the real server module (53 tools, 5 prompts, 1 resource, 1 resource template). The five prompts are `build_scene`, `audit_scene`, `semantic_audit`, `animate_scene`, `convert_to_x3dom`. The resources are `x3d-ontology://turtle` and the template `x3d-ontology://placement/{child}`. [The x3d_mcp masterclass](../x3d_mcp/MASTERCLASS.md) counts 48 `@mcp.tool` at `13121b6` and 34 at the fork base; the five semantic-web tools landed after its snapshot (48 + 5 = 53 at `b4efcd3`, **[L]** for the earlier snapshot, which I did not re-run).

**Which tools exist depends on the transport**, **[C]** (real `FastMCP` list, `MCP_TRANSPORT` and `X3D_MCP_BLOB_TOKEN` varied):

| configuration | tools | `tools/list` bytes (compact JSON) |
|---|---|---|
| stdio (default) | 53 | 64,426 |
| streamable-http with `X3D_MCP_BLOB_TOKEN` (32+ chars) | 53 | 64,426 |
| streamable-http, no token | **47** (no blob tools, no splat tools) | 56,205 |
| fork base `74da0ec` | 34 (4 prompts, no resources) | 28,075 |

The instructions follow the same switch: 3,353 characters over HTTP without a token (no large-scene or splat block, because there is no store to name a file in), 4,692 on stdio or with a token. A client that expects `blob_put` on an HTTP server started without a token will not find it, and will not be told to look.

**In scope:** the tool surface, its transfer layer and guards, and how a model should drive it. **Out of scope:** the validator rules themselves ([03](03-validator-and-gates.md)), ontology and SHACL semantics ([05](05-semantic-layer.md)), Playwright rendering ([06](06-xite-the-oracle.md)).

**Read next:** deeper, [03 The validator and the gates](03-validator-and-gates.md) for what the validate tools run, with `x3d_mcp@b4efcd3:docs/transfer-layer.md` for the byte layer; wider, [05 Semantic layer](05-semantic-layer.md).

## 2. What the server says on connect

`server.py` hands the client an `instructions` string. It is the one piece of prompting the server controls, so it is worth reading as a contract. Its structure, **[C]** (read):

| block | content | when |
|---|---|---|
| THE PATH | 1 LOOK UP (`describe_node`, `list_nodes`; "never guess field or containerField names"); 2 BUILD; 3 VALIDATE "always BOTH" `validate_x3d` and `validate_semantic`; 4 RENDER and look; "a scene is not finished until validate_semantic is clean AND you have rendered it" | always |
| MEANING, NOT ONLY SYNTAX | `scene_to_rdf`, `sparql_scene`, `shacl_validate`, `claim_append`; "The ontology proposes, the shapes dispose, the validators gate: an ontology answer is never a validity verdict" | always |
| NON-OBVIOUS RULES | containerField defaults only fit the usual parent; DEF before USE; ROUTE types and access types must match | always |
| LARGE SCENES, SPLATS AND DATA FILES | never paste over about 100 KB; use `path=` (stdio) or `PUT /blob` (HTTP) then `blob_id=`; `return_mode="summary"` or `"blob"` | blob store on |
| GAUSSIAN SPLATS | a splat scene is 5 to 65 MB; one node validates only to roughly 75,000 to 100,000 splats (libxml2's 10 MB start-tag limit); `splat_inspect` then `splat_chunk` | numpy present and (store on or stdio) |

Size, **[C]** (`len(mcp.instructions)` on the real server module): 2,212 characters at `74da0ec`; at `b4efcd3` 3,353 over HTTP without a token and 4,692 on stdio. Together with the tool list that is what every session pays before the first call: 28,075 B of `tools/list` at base, 64,426 B at head (+36,351 B for 19 more tools; the five largest schemas are `splat_chunk` 3,681 B, `x3d_generation_schema` 2,461, `shacl_validate` 2,401, `repair_x3d` 2,338 and `scene_to_rdf` 2,276, together 13,157 B or 20 % of the head figure). Bytes, not tokens: I did not tokenise.

The prompts encode the same path as a script. The base registers four prompts; `semantic_audit(content, focus)` is the one added since. `audit_scene` and `build_scene` are the entry points for "check this" and "make this".

## 3. JSON in, JSON out, and where it is not

The repo's own doc says tools take `content: str` and return strings. In practice there are four reply shapes:

| shape | tools | example size |
|---|---|---|
| JSON object | `validate_x3d`, `autofix_x3d`, `repair_x3d`, `exact_fix_hints`, all `query_*`/`describe_*`/`list_*`, ontology, claims, blob, splat, semantic-web | `validate_x3d` on a clean scene: 62 B |
| markdown report | `validate_semantic` (default `return_mode="full"`), `validate_current_scene` (markdown plus an embedded JSON block) | 242 B for a clean scene with one info line |
| document text | `create_*`, `compose_scene`, `modify_x3d_node` and friends in `full` mode | 512 B for one box |
| envelope | any tool with `return_mode="summary"` or `"blob"` | 539 B for a one-error summary |

The envelope has a fixed head: `{"return_mode", "source", "input": {"sha256", "bytes"}, ...}`, then tool-specific keys, then `document: {sha256, bytes, media_type, nodes, node_types, blob_id?, stored_size?}` for tools that return a document. Lists are capped at `X3D_MCP_SUMMARY_ITEMS` (200) with `<name>_total` and `<name>_truncated` beside them.

Every document-taking tool accepts exactly one of `content`, `path` or `blob_id`; the error for none or two is returned as JSON or a markdown "Input Error", not raised. Errors are data: `{"error": "Query refused: ..."}`, `{"valid": false, "errors": [...]}`. A caller that parses only success shapes will miss them.

One protocol detail from the repo docs (**[L]**, not re-measured): a `-> str` tool is sent twice (`content[].text` and `structuredContent.result`), so a 10 MB result is 20 MB on the wire; the four blob tools and the three claims tools are registered with `structured_output=False` (**[C]**, read of the decorators).

## 4. The transfer layer, measured

**Why it exists, [C].** `mcp` 1.30.0 refuses a request body over 4 MiB: `DEFAULT_MAX_REQUEST_BODY_SIZE = 4 * 1024 * 1024` and a `413 "Request body too large"` in `server/transport_security.py` (read in the installed package; I did not exercise it over a socket). Any scene over 4 MiB cannot be a `content` argument over HTTP. The fix is to name documents by id.

```text
  by value                                   by name
  --------                                   -------
  model --10 MB content--> modify_x3d_node   upload once: blob_put(path=...) or PUT /blob
  model <--10 MB document-- modify_x3d_node  model --blob_id--> modify_x3d_node(blob)
  (repeated per edit, both ways)             model <-- {changes, document:{sha256, blob_id}}
                                             (about 1 KB per edit)
```

**Before and after, reproducible.** A synthetic scene: 40,000 `Transform`/`Shape`/`Box` nodes, 6,505,087 B (sha256 prefix `6e0a70454d0f`), built by a 12-line generator. Ten `modify_x3d_node` edits (`translation` of `n0` to `n9`), called in process, counting the UTF-8 bytes of the arguments sent and of the string returned, **[C]**:

| path | bytes sent | bytes returned | total | wall time |
|---|---|---|---|---|
| inline `content`, `return_mode="full"` | 87,011,328 | 89,451,090 | **176,462,418** | 1.8 s |
| `blob_put(path=...)` once, then `blob_id` with `return_mode="blob"` | 947 | 9,902 | **10,849** | 4.0 s |

A ratio of about 16,300 to 1 in bytes crossing the tool boundary, and the blob path is slower in wall time (4.0 s against 1.8 s, in process, no network): the docs put the cost in hashing, compression and a worker thread; I did not profile it. The first edit re-serialises the document indented, so a 6,505,087 B input becomes an 8,945,109 B output; `modify_x3d_node` does not preserve formatting. `blob_put` stored the scene as zstd in 100,091 B (65 to 1); that ratio is a property of a highly repetitive synthetic scene and says nothing about real ones (the repo doc reports 25 to 1 for zstd level 3 on a real 10.9 MB scene, **[L]**, not re-run).

Summaries are small, not always tiny, **[C]**: `validate_x3d(blob_id, return_mode="summary")` on the 8.9 MB blob answered in 320 B; `validate_semantic(..., "summary")` answered in 47,537 B because the scene has 40,000 `unused-def` info findings; the list is capped at 200 items and the counts per check sit in `by_check`.

**Splat chunking, measured.** A synthetic 3DGS-style PLY (200,000 splats, 11,200,362 B, random values, seed 20261114), on `x3d_mcp fork b4efcd3`, **[C]**:

| step | result |
|---|---|
| `splat_inspect(path=...)` | 3,310 B answer in 0.17 s; verdict `ok` with two info reasons: "200,000 splats do not fit one validatable GaussianSplats node (61,062 at these digits): use splat_chunk (4 chunks at minimum)" and a coordinate-frame note recommending `coordinate_system='rdf'` for a y-down training file |
| `splat_chunk(path=..., target=50000, out_dir=..., validate=True)` | 2,913 B answer in 4.87 s; 4 chunk files of 6.6, 6.55, 6.55, 6.5 MB plus a master scene of `Inline` nodes; every file XSD-valid, 0 semantic errors, 0 warnings (5 of 5) |
| one node, no chunking | not checkable: an 11,700,036-byte `GaussianSplats` tag returns `valid: false, checked: false, verdict: "not-checkable-at-this-size"` in 1,763 ms |

The 10,000,000-byte start-tag limit is libxml2's. `X3D_MCP_XML_HUGE=on` allows a bounded `huge_tree` retry; the docs name it a security trade-off (**[L]**) and it is off by default.

**When the store is on** (docs, confirmed by the 47/53 tool counts above): stdio, always; HTTP only with a token of 32 or more characters; `X3D_MCP_BLOB=on` over HTTP without a token is a start-up error. Defaults read from the code: largest blob 256 MiB, in-RAM budget 128 MiB, decoded blob a tool will take 96 MiB (`X3D_MCP_TOOL_MAX_BYTES`; the header comment in `blobs.py` says 64M and the code and `docs/transfer-layer.md` say 96M: the code wins). Ids are the sha256 of the bytes; the same bytes give the same id.

## 5. Guards

| guard | default | real output (`x3d_mcp fork b4efcd3`, **[C]**) |
|---|---|---|
| SPARQL: no `SERVICE` | on | `{"error": "Query refused: SERVICE is not allowed (it makes the server send HTTP requests)"}` |
| SPARQL: no `FROM` / `FROM NAMED` | on | `{"error": "Query refused: FROM and FROM NAMED are not allowed; the ontology graph is fixed"}` |
| SPARQL: SELECT and ASK only | on | an `INSERT DATA` gives `Query refused: SPARQL does not parse: Expected {SelectQuery \| ConstructQuery \| DescribeQuery \| AskQuery}, found 'INSERT'` |
| SPARQL: size | 20,000 characters (`X3D_MCP_SPARQL_MAX_CHARS`) | a 30,346-character query: `Query refused: query is 30346 characters; the limit is 20000` |
| SPARQL: deadline | 20 s (`X3D_MCP_SPARQL_TIMEOUT`) | with the limit set to 1 s, a triple cross-join stopped at 1.01 s: `{"error": "query ran past 1 s and was stopped (X3D_MCP_SPARQL_TIMEOUT)"}` |
| SPARQL: row cap | 20,000 (`X3D_MCP_ONTOLOGY_MAX_ROWS`) | with the cap at 5: `"count": 5, "truncated": true, "total": 17736`, pointer to `query_ontology_page` |
| node name in `node_parents` | `[A-Za-z_][A-Za-z0-9_]{0,127}` | `node_parents("Box> } ; DROP")`: `Query refused: node type must be a plain name such as Sphere` |
| `path=` over HTTP | refused | with `MCP_TRANSPORT=streamable-http`: `Path input is disabled over the HTTP transport. Provide inline X3D content instead.` |
| stdout hygiene | `server.py` swaps `sys.stdout` to stderr around its imports | the `x3d` package prints a banner to stdout on import; under stdio that would corrupt the JSON-RPC stream (`server.py` lines 41 to 49, read) |
| blob ids | 64 hex characters | other strings are rejected before reaching the table (code and tests, read) |
| blob upload | bearer token, rate and size limits, decoded-to-wire ratio 250 | `tests/test_transfer_http.py`: 413 before any body byte; 413 on the ratio; passes |
| large calls | worker thread at 1 MiB (`X3D_MCP_OFFLOAD_MIN`), 2 concurrent blob calls | docs and code, read; the 6.7 s event-loop stall that motivated it is **[L]** |

The whole suite on this rig, **[C]**: 1,394 tests collected, 1,367 passed, 27 skipped, 104 s (the skips are chiefly the Chromium render tests and optional-extra tests). The deadline and row-cap behaviour above is also in the suite; I re-ran the outputs, not only the tests.

The guard design rule worth copying: the guard sits in the tool, parses before it executes (SPARQL is parsed to its algebra and refused on the parsed form, not by string matching), and answers with a refusal that names the setting. A model that sees "limit is 20000 (X3D_MCP_SPARQL_MAX_CHARS)" can repair its call; an operator can see which knob to move.

## 6. The Accountability Playground (what the docs say, read not run)

`docs/playground/{ARCHITECTURE,GUIDE,ADMIN}.md` describe a web service in which a model writes a scene and the fork's validator judges it. It needs sign-in and model endpoints, so I did not run it. The loop, from `ARCHITECTURE.md`:

| step | what happens |
|---|---|
| 1 write | a writer model streams a scene; code fences and prose are stripped |
| 2 validate | XSD for the declared version, then `semantic_diagnostics`; each finding has a layer, line, check id, message, hint |
| 3 validator fixes | `repair_x3d` applies exact fixes only (profile, component, version) and revalidates; "it never guesses" |
| 4 writer repairs | the writer sees its draft and the defect list, up to a repair limit |
| 5 judge | a model from another family reviews draft 1 without the validator; its defects are matched to the validator's errors by line (plus or minus 1) or quoted token |
| 6 browser | a sandboxed iframe renders the final scene; a blank result triggers one visibility repair |

Two facts matter for an auditor. First, the playground imports the validator in process and does not go through the MCP tool surface ([the teardown](../x3d_mcp/MASTERCLASS.md) section 3), so it does not exercise what this chapter describes. Second, its judge compares a validator-free model review against the validator, which is the right shape for the question "does the file carry the accountability, or does the model's opinion?"; no numbers from it are used here.

## 7. Task to tool, with the cost of each answer

The bytes below are real, **[C]** (`x3d_mcp fork b4efcd3`, in-process calls of section 8; "arg B" is the UTF-8 length of the argument values, "out B" the length of the returned string). One scene of 645 bytes was used throughout, so costs scale with the document, not with the tool. Wall times moved by up to 7 % between two runs of the transcript; byte counts matched except `blob_info` (the expiry stamp changes its digits).

| task | call | arg B | out B | note |
|---|---|---|---|---|
| which components exist | `list_components()` | 0 | 8,593 | JSON |
| which nodes in a component | `list_nodes(component="Shape")` | 5 | 202 | JSON |
| fields of a node | `describe_node("Box")` | 3 | 5,829 | `describe_node("Material")` is 21,310 characters |
| build a small scene from a spec | `compose_scene(objects=[...], viewpoint=...)` | 83 | 512 | one box, XML |
| XSD verdict, valid | `validate_x3d(content)` | 512 | 62 | about 1.5 s: first load of the 4.1 schema |
| semantic verdict, clean | `validate_semantic(content)` | 512 | 242 | markdown; 24 ms |
| XSD verdict, one error | `validate_x3d(content)` | 645 | 285 | about 1.5 s: first load of the 4.0 schema |
| what to change | `exact_fix_hints(content)` | 645 | 1,325 | one hint, `wrong-parent`, `move`, `choice` |
| change it | `exact_fix_hints(content, apply=True)` | 649 | 2,314 | adds `fixed`, `valid_after`, `applied`; the repaired text comes back whole |
| profile, component, version repair | `repair_x3d(content)` | 650 | 1,174 | `component Shape level 2` |
| park a document | `blob_put(content=...)` | 652 | 331 | 645 B stored as 393 B zstd |
| validate by name | `validate_x3d(blob_id, return_mode="summary")` | 71 | 539 | |
| edit by name | `modify_x3d_node(blob_id, ..., return_mode="summary")` | 102 | 825 | keys: `return_mode, source, ok, input, document, changes, changes_total` |
| blob facts | `blob_info(blob_id)` | 64 | 547 to 548 | size, stored size, codec, expiry, preview |
| record a claim | `claim_append(...)` | 158 | 1,265 | record plus the whole ledger so far |
| verify the ledger | `claims_verify(ledger)` | 326 | 118 | |
| scene as a graph | `scene_to_rdf(content, return_mode="summary")` | 652 | 1,545 | 119 triples, 14 individuals |
| graph against shapes | `shacl_validate(graph_id)` | 16 | 2,097 | 1 Violation, 1 Warning; about 1.0 s |
| where may a node go | `where_can_place("Box", limit=5)` | 4 | 802 | |
| a splat file | `splat_inspect(path=...)`, then `splat_chunk` | | 3,310 / 2,913 | section 4, 200,000 splats |
| a picture | `render_image` | | | read, not run: needs Playwright and Chromium |

Which way to hand the server a document is a size decision, and the server's own instructions say so:

```text
  document size           how to name it                     answer
  ----------------------  ---------------------------------  --------------------------
  up to about 100 KB      content=  (inline)                 full, or summary
  100 KB to 4 MiB, stdio  path=, or blob_put then blob_id    summary or blob
  100 KB to 4 MiB, HTTP   PUT /blob, then blob_id=           summary or blob
  over 4 MiB, HTTP        PUT /blob only (SDK refuses body)  summary or blob
  splat file, 5-65 MB     splat_inspect, then splat_chunk    chunk files + master scene
  one tag over ~10 MB     cannot be one node                 not-checkable-at-this-size
```

The 100 KB figure is the instructions' own; the 4 MiB row is the SDK cap of section 4; the splat and start-tag rows are measured in section 4.

## 8. A reproducible transcript, without an MCP client

Nothing below needs a model, a network or a browser. The point is a stranger's ability to get the same bytes. Setup, read from `pyproject.toml` (ranges) and run with the versions in the rig line:

```bash
python3 -m venv venv
./venv/bin/pip install "mcp>=1.29,<2" "x3d>=4.0.65.5,<5" lxml xmlschema jsonschema rdflib \
    "pyshacl>=0.30,<1" numpy zstandard brotli
git clone <x3d_mcp repository> x3d_mcp && git -C x3d_mcp checkout b4efcd3   # read-only use
export X3D_MCP_SRC=$PWD/x3d_mcp/src
```

File one, `x3d_mcp_calls.py`. It stands in for FastMCP: each `register(mcp)` decorates plain closures, so the harness records the closures and calls them.

```python
import asyncio, importlib, inspect, json, os, sys
sys.path.insert(0, os.environ["X3D_MCP_SRC"])          # <checkout>/src

class FakeMCP:
    """Records what each register(mcp) decorates; every other hook is a no-op."""
    def __init__(self): self.tools = {}
    def tool(self, *a, **kw):
        def deco(fn):
            self.tools[kw.get("name", fn.__name__)] = fn
            return fn
        return deco
    def prompt(self, *a, **kw): return lambda fn: fn
    def resource(self, *a, **kw): return lambda fn: fn
    def custom_route(self, *a, **kw): return lambda fn: fn

MODULES = ["workflow", "granular", "convert", "query", "validate_tool", "render", "scene_ops",
           "animate", "prompts", "semantics", "semantic_web", "claims", "splats", "transfer"]

def load():
    mcp = FakeMCP()
    for m in MODULES:
        importlib.import_module("tools." + m).register(mcp)
    return mcp

async def call(mcp, tool, **kw):
    fn = mcp.tools[tool]
    r = fn(**kw)
    if inspect.isawaitable(r):           # 26 of the 53 tool functions are `async def`
        r = await r
    return r if isinstance(r, str) else json.dumps(r)
```

File two, `transcript.py` (the scene is the file of chapter 03's s02, a Box outside its Shape; `S09` is the same text with a different profile, a `PhysicalMaterial` and the Box inside the Shape):

```python
import asyncio, hashlib, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from x3d_mcp_calls import load, call

BAD = '''<?xml version="1.0" encoding="UTF-8"?>
<X3D profile="Interactive" version="4.0"><head><meta name="title" content="t"/></head><Scene>
  <Viewpoint position="0 0 6"/>
  <Transform DEF="Spinner"><Shape><Appearance><Material diffuseColor="0 0.4 1"/></Appearance></Shape><Box/></Transform>
  <TimeSensor DEF="Clock" cycleInterval="4" loop="true"/>
  <OrientationInterpolator DEF="Spin" key="0 0.5 1" keyValue="0 1 0 0 0 1 0 3.14159 0 1 0 6.28318"/>
  <ROUTE fromNode="Clock" fromField="fraction_changed" toNode="Spin" toField="set_fraction"/>
  <ROUTE fromNode="Spin" fromField="value_changed" toNode="Spinner" toField="set_rotation"/>
</Scene></X3D>'''
S09 = (BAD.replace('profile="Interactive"', 'profile="Interchange"')
          .replace('<Material diffuseColor', '<PhysicalMaterial baseColor')
          .replace('</Appearance></Shape><Box/>', '</Appearance><Box/></Shape>'))
mcp, rows = load(), []
print("BAD bytes", len(BAD.encode()), "sha256", hashlib.sha256(BAD.encode()).hexdigest()[:12])

async def go(tool, **kw):                      # call, and record argument bytes, answer bytes, ms
    t0 = time.perf_counter()
    out = await call(mcp, tool, **kw)
    rows.append((len(rows) + 1, tool, sum(len(str(v).encode()) for v in kw.values()),
                 len(out.encode()), (time.perf_counter() - t0) * 1000))
    return out

async def main():
    await go("list_components"); await go("list_nodes", component="Shape"); await go("describe_node", node_type="Box")
    doc = await go("compose_scene", objects=[{"shape": "box", "color": [0, 0.4, 1], "def_name": "Cube"}],
                   viewpoint={"position": [0, 0, 6]})
    print("validate_x3d(composed)  ", json.loads(await go("validate_x3d", content=doc)))
    await go("validate_semantic", content=doc)
    print("validate_x3d(BAD)       ", json.loads(await go("validate_x3d", content=BAD))["errors"])
    h = json.loads(await go("exact_fix_hints", content=BAD))["hints"][0]
    print("hint                    ", h["rule"], h["suggested_fix"]["op"], h["confidence"])
    a = json.loads(await go("exact_fix_hints", content=BAD, apply=True))
    print("hints apply             ", a["valid_after"], [x["rule"] for x in a["applied"]])
    print("repair_x3d(S09)         ", json.loads(await go("repair_x3d", content=S09))["changes"])
    put = json.loads(await go("blob_put", content=BAD, name="s02.x3d"))
    print("blob_put                ", {k: put[k] for k in ("size", "stored_size", "encoding")}, put["blob_id"][:12])
    v = json.loads(await go("validate_x3d", blob_id=put["blob_id"], return_mode="summary"))
    print("validate_x3d(blob_id)   ", {k: v[k] for k in ("return_mode", "valid", "schema_version", "error_count")})
    m = json.loads(await go("modify_x3d_node", content="", blob_id=put["blob_id"], def_name="Spinner",
                            field_changes=json.dumps({"translation": "1 2 3"}), return_mode="summary"))
    print("modify_x3d_node keys    ", list(m))
    await go("blob_info", blob_id=put["blob_id"])
    sha = hashlib.sha256(BAD.encode()).hexdigest()
    c = json.loads(await go("claim_append", claim="s02 is not XSD-valid", grade="Confirmed", subject=sha,
                            instrument=json.dumps({"validator": "b4efcd3", "tool": "validate_x3d"}),
                            evidence="transcript call 6"))
    v = json.loads(await go("claims_verify", ledger=c["ledger"]))
    print("claims_verify           ", v["ok"], v["records"])
    g = json.loads(await go("scene_to_rdf", content=BAD, return_mode="summary"))
    print("scene_to_rdf            ", g["triples"], "triples", g["individuals"], "individuals")
    s = json.loads(await go("shacl_validate", graph_id=g["graph_id"]))
    print("shacl_validate          ", s["counts"], s["by_check"])
    await go("where_can_place", child="Box", limit=5)
    print("\n #  tool                 arg_B     out_B      ms")
    for n, t, a_, o, ms in rows:
        print(f"{n:>2}  {t:20s} {a_:6,d} {o:9,d} {ms:7.1f}")

asyncio.run(main())
```

Run it as `./venv/bin/python -I transcript.py` (the `-I` flag keeps stray `PYTHONPATH` and the current directory out; the script puts its own folder on the path). Output on the rig of this chapter, **[C]**, 2026-11-14, with the one banner line the `x3d` package prints on import omitted:

```console
BAD bytes 645 sha256 f76343d3dcd0
validate_x3d(composed)   {'valid': True, 'errors': [], 'schema_version': '4.1'}
validate_x3d(BAD)        ["Line 4: Element 'Box': This element is not expected. Expected is one of ( ROUTE, ExternProtoDeclare, ProtoDeclare, IMPORT, EXPORT, Background, ColorInterpolator, CoordinateInterpolator, DirectionalLight, Group )."]
hint                     wrong-parent move choice
hints apply              True ['wrong-parent']
repair_x3d(S09)          [{'kind': 'component', 'name': 'Shape', 'from': None, 'to': '2', 'reason': "nodes outside profile 'Interchange'"}]
blob_put                 {'size': 645, 'stored_size': 393, 'encoding': 'zstd'} f76343d3dcd0
validate_x3d(blob_id)    {'return_mode': 'summary', 'valid': False, 'schema_version': '4.0', 'error_count': 1}
modify_x3d_node keys     ['return_mode', 'source', 'ok', 'input', 'document', 'changes', 'changes_total']
claims_verify            True 1
scene_to_rdf             119 triples 14 individuals
shacl_validate           {'Violation': 1, 'Warning': 1, 'Info': 0} {'field-not-in-domain': 1, 'shape-no-geometry': 1}
```

The byte table printed at the end is the table of section 7. The blob id is the sha256 of the bytes, so `f76343d3dcd0` is both the first line's hash and the start of the `blob_put` id: if your first line differs, your scene is not this scene. The harness does not show FastMCP's argument validation (it calls the closures directly, so a wrongly typed call can pass), the wire frame (counts are Python return values, without the JSON-RPC envelope or the duplicate `structuredContent`), or conditional registration (it registers every module; section 1 gives the real counts per transport).

## 9. Safe and unsafe usage

| practice | why | evidence |
|---|---|---|
| name big documents, never paste them | 4 MiB request cap over HTTP; 176 MB against 10.8 KB at 40,000 nodes | section 4, **[C]** |
| run `validate_x3d` and `validate_semantic`, both | the instructions say so; 8 of 15 faulty scenes pass the XSD and 6 of those 8 carry a semantic error | [chapter 03](03-validator-and-gates.md), **[C]** |
| read `checked` before `valid` | `valid: false, checked: false` is "no verdict" | [chapter 03](03-validator-and-gates.md), **[C]** |
| read `applied` after `apply=True` | the hint loop can reach "valid" by deleting an element | [chapter 03](03-validator-and-gates.md), **[C]** |
| parse every reply as possibly an error object | errors are data: `{"error": ...}`, `{"valid": false, ...}`, `Input Error` markdown | section 3, **[C]** |
| ask for `summary` when the document is not needed back, then check its size | a summary of an 8.9 MB scene was 320 B for the XSD and 47,537 B for the semantic layer (40,000 info findings) | section 4, **[C]** |
| treat `path=` under stdio as a file-read primitive | see below | probe, **[C]** |
| over HTTP, set a token of 32 or more characters | without it: 47 tools, no store, `X3D_MCP_BLOB=on` is a start-up error | section 1, **[C]** |
| keep ontology answers out of verdicts | the server's own line: "an ontology answer is never a validity verdict" | instructions, **[C]** (read) |
| do not treat the claim ledger as signed | see below | probe, **[C]** |
| trust the SPARQL guard, not the model's query | parsed form, not string matching; refusal names the knob | section 5, **[C]** |

**The stdio path policy, probed** (**[C]**, `x3d_mcp fork b4efcd3`, 2026-11-14, two files in a scratch folder):

| call | result |
|---|---|
| `validate_x3d(path="notes.cfg")`, a file that is XML but not X3D | read; the error echoes the root element name: `Element 'passwd_like': No matching global declaration available for the validation root.`, `schema_version: "4.1"`, note "No version attribute" |
| `validate_x3d(path="data.txt")`, plain text | read; `XML parse error: Start tag expected, '<' not found, line 1, column 1` |
| `blob_put(path="data.txt")` | stored, 19 B, a `blob_id`; `blob_read(blob_id)` then pages the bytes back |
| `blob_put(path="notes.cfg")` | refused: `blob_put(path=) reads scene, data and splat files by extension (.csv, .glb, ... .xml); set X3D_MCP_BLOB_PATH_ROOTS to a directory to read other names from it` |
| any `path=` with `MCP_TRANSPORT=streamable-http` | refused: `Path input is disabled over the HTTP transport. Provide inline X3D content instead.` |

Read: under stdio the server runs as the user who started it and trusts the model that is connected to it. `validate_x3d(path=)` reads any UTF-8 file that user can read and leaks only what a validator error quotes (an element name, a parse position); `blob_put(path=)` reads any file with one of 27 extensions (including `.txt`, `.md`, `.json`, `.xml`) and `blob_read` returns it whole. This is the repo's documented design ("a local-use affordance"; `docs/transfer-layer.md` says so), not a defect. The consequence is operational: start a stdio server as a user whose readable `.txt`, `.md`, `.json` and `.xml` files you would show the model, or set `X3D_MCP_BLOB_PATH_ROOTS`. I did not test `X3D_MCP_ALLOWED_HOSTS` or `X3D_MCP_ALLOWED_ORIGINS` (code and docs read).

**The ledger, probed** (**[C]**, `claim_append`, `claims_verify`, two records, `x3d_mcp fork b4efcd3`): each record carries `schema, claim, grade, subject, instrument, evidence, prev, sha256`, and `prev` is the previous record's hash. Editing a claim's text gives `ok: false` with `hash does not match the record` at index 0; deleting the first record gives `prev is not the hash of the record before`; a fresh one-record ledger that says the opposite gives `ok: true, records: 1`. A hash chain is tamper-evident to someone who holds the head hash, and says nothing about who wrote it. Truncating the tail was not probed. Grades in the ledger are the caller's word (`Confirmed`, `Likely`, `Suspected`), checked for spelling and not for truth.

## 10. Measured and claimed agent benefit

The thesis of this base is that a file can be held to account. This chapter's tools are how an agent meets that accountability. What can be said about the benefit to the agent, as of 2026-11-14:

| claim | where it stands | grade |
|---|---|---|
| the server tells a model the path (look up, build, validate both, render) on connect | the text is in `server.py`; 4,692 characters on stdio | **[C]** that it is sent; **[S]** that it changes what a model does |
| big documents cost 176,462,418 B inline against 10,849 B by name (40,000 nodes, 10 edits) | measured, synthetic scene, in process | **[C]** for bytes; **[S]** for any effect on a model's success |
| the 53-tool surface costs 64,426 B of `tools/list` per session, +36,351 B (+129.5 %) over the 34-tool base | measured, compact JSON, bytes not tokens | **[C]** |
| the hint loop restores validity on 96.7 % of 540 mutated scenes (14.1 % by `repair_x3d` alone) | re-run at `b4efcd3`, no model; mutations and rules share an author | **[C]** for the re-run |
| hints improve a model's repair loop | the repo's own heading is "Model repair loop: not measured (S)"; the experiment (`evaluation/hint_loop_gemini.py`, paired arms, up to 2 rounds, exact McNemar) needs a paid model API and was not run | **[S]** |
| the plain-error baseline already reaches 60/60 in one round on the author's eval-plan prompts | stated in `docs/EXACT-FIX-HINTS.md`; not re-run | **[L]** |
| a false-positive fix cut error-level files from 96 to 22 on 264 scenes (PR #4) | PR description, quoted by the masterclass as "claimed" | **[L]** |
| count and index rules raised a blind mutation set from 62.6 % to 100 % caught, no new alarms (PR #8) | PR description, same | **[L]** |
| the Accountability Playground shows validator-fixed against writer-fixed repairs | the architecture is read; no playground run and no numbers used | not graded |

Where this leaves the thesis: the tool surface is cheap to describe and measurable in bytes, and the exact-fix hints are measurable without a model. **What is not measured, here or in the sources I read, is the difference this surface makes to a model's rate of valid-and-visible scenes.** That needs the repo's own design, written out as an obligation: the same prompts, the same model, an arm with the tools and an arm without, a named validator commit, a visibility check through [the second renderer](06-xite-the-oracle.md), and a paired test. Until that exists the honest sentence is the one in the Say-it box: the tools make answers small and checkable; whether they make the agent better is open.

## Heuristics

| ID | Rule (imperative, at most 30 words) | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-MCP-1 | Count tools on the transport you will ship; the same code lists 53 tools on stdio, 47 on HTTP without a blob token. | C | `list_tools()` under three environments | `x3d_mcp fork b4efcd3`, `mcp` 1.30.0 |
| H-MCP-2 | Budget `tools/list` before the first call: 64,426 B for 53 tools, 36,351 B more than the base. Trim by transport if context is scarce. | C | `list_tools()` serialised compact | `x3d_mcp fork b4efcd3`, `x3d_mcp upstream 74da0ec` |
| H-MCP-3 | Never paste a document over about 100 KB; name it with `path=` or `blob_id=`. Over HTTP, over 4 MiB, the name is the only way. | C | 17,494,418 B inline against 10,756 B at 4,000 nodes | `x3d_mcp fork b4efcd3`; `mcp` 1.30.0 `transport_security.py` |
| H-MCP-4 | Ask for `return_mode="blob"` when the edited document is not needed back, and `summary` for a verdict, then check how large the summary is. | C | semantic summary 47,537 B on 40,000 info findings | `x3d_mcp fork b4efcd3` |
| H-MCP-5 | Parse every reply as a possible error object; read `valid` and `checked` together, and `applied` after any automatic fix. | C | `not-checkable-at-this-size`; s10 and s11 valid by deletion | `x3d_mcp fork b4efcd3` |
| H-MCP-6 | Run a stdio server as a user whose readable text, JSON and XML files you would show the model; `path=` and `blob_put(path=)` read them. | C | probe: `.txt` stored and readable, `.cfg` refused | `x3d_mcp fork b4efcd3` |
| H-MCP-7 | Over HTTP set a blob token of 32 or more characters, or expect 47 tools and no store. | C | env matrix; start-up error without token | `x3d_mcp fork b4efcd3` |
| H-MCP-8 | Put the guard in the tool, parse before executing, and have the refusal name the setting that moves it. | C | SPARQL refused on the parsed algebra; each message names its variable | `x3d_mcp fork b4efcd3` |
| H-MCP-9 | Treat a claim ledger as tamper-evident, not signed; keep the head hash somewhere the writer cannot reach. | C | edit and first-record drop detected; fresh forged chain verifies | `x3d_mcp fork b4efcd3` |
| H-MCP-10 | Keep ontology and SHACL answers out of validity claims; cite them as meaning, and the validators as the gate. | C | server instructions; `ontology_vs_gate` | `x3d_mcp fork b4efcd3` (read) |
| H-MCP-11 | When you claim an agent benefit, name the model, the prompt set, the validator commit and the arm without the tool. Otherwise write "not measured". | S | the repo's hint-loop heading; no paired run exists | `x3d_mcp fork b4efcd3` docs |
| H-MCP-12 | Call tools through a harness before wiring a client: you get bytes and wall time per call, and no model to blame. | C | the 19-call transcript | `x3d_mcp fork b4efcd3`, Python 3.13.18 |

## Drills

### D-MCP-1 Count the surface three ways
- **Level:** L2
- **Task:** At `x3d_mcp@b4efcd3` count tools, prompts and resources by Python `ast` over `src/tools/*.py`, by a recording stand-in for `mcp`, and by FastMCP `list_tools()` on `src/server.py`. Then repeat `list_tools()` with `MCP_TRANSPORT=streamable-http`, with and without `X3D_MCP_BLOB_TOKEN`.
- **Verify:** count `@mcp.tool`, `@mcp.prompt`, `@mcp.resource` decorators with `ast.walk`; the stand-in is `FakeMCP` of section 8; for the real server load `server.py` with `importlib` and run `asyncio.run(mcp.list_tools())`.
- **Answer:** 53 tools, 5 prompts, 2 resources by the first two methods; FastMCP lists 53 tools, 5 prompts, 1 resource and 1 resource template. Variants: stdio 53; HTTP without a token 47; HTTP with a 32-character or longer token 53. The six missing are `blob_put`, `blob_info`, `blob_read`, `blob_delete`, `splat_inspect`, `splat_chunk`.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3`, `mcp` 1.30.0, Python `ast`.

### D-MCP-2 Price a session before it starts
- **Level:** L2
- **Task:** Serialise `tools/list` as compact JSON (`json.dumps(..., separators=(",", ":"))` of each tool's `model_dump(by_alias=True, exclude_none=True, mode="json")`) and read `len(mcp.instructions)`, for `b4efcd3` on stdio and for the fork base `74da0ec`. Name the five largest tool schemas at head.
- **Verify:** `await mcp.list_tools()` on each checkout's `src/server.py`; sort by serialised length.
- **Answer:** base 34 tools, 28,075 B, instructions 2,212 characters. Head on stdio 53 tools, 64,426 B, instructions 4,692 characters; HTTP without a token 47 tools, 56,205 B, 3,353 characters. Largest at head: `splat_chunk` 3,681 B, `x3d_generation_schema` 2,461, `shacl_validate` 2,401, `repair_x3d` 2,338, `scene_to_rdf` 2,276.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3` and `x3d_mcp upstream 74da0ec`, `mcp` 1.30.0.

### D-MCP-3 Edit a big scene twice, once by value and once by name
- **Level:** L2
- **Task:** Generate a scene of 4,000 `Transform`/`Shape`/`Box` nodes (`DEF="n0"` to `"n3999"`, `translation` set from the index, `Material` colours from the index modulo 10). Make 10 `modify_x3d_node` edits of `translation` on `n0` to `n9`: once inline with `return_mode="full"` (feed each answer to the next call), once with `blob_put(path=...)` and then `blob_id` with `return_mode="blob"`. Count argument bytes plus answer bytes.
- **Verify:** the harness of section 8; `len(str(value).encode())` over the arguments and `len(answer.encode())` for each call.
- **Answer:** the generator I used wrote a 642,887 B scene (sha256 prefix `06fdd220d5bc`); inline 8,625,328 B sent plus 8,869,090 B returned, 17,494,418 B total; by name 947 B sent plus 9,809 B returned, 10,756 B total, a ratio of about 1,630 to 1. Your absolute figures differ with the generator; the ratio should land within a factor of two. At 40,000 nodes (6,505,087 B) the same run gave 176,462,418 B against 10,849 B.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3`, in-process calls, 4 vCPU Intel Xeon 2.30 GHz.

### D-MCP-4 Trip each SPARQL guard
- **Level:** L3
- **Task:** With `query_ontology`: (a) send a query containing `SERVICE`; (b) one with `FROM`; (c) an `INSERT DATA`; (d) a query over 20,000 characters; (e) set `X3D_MCP_ONTOLOGY_MAX_ROWS=5` and select all triples; (f) set `X3D_MCP_SPARQL_TIMEOUT=1` and run a triple cross-join. Then call `node_parents` with `"Box> } ; DROP"`. Record each refusal, and say what the model could do with each message.
- **Verify:** `await call(mcp, "query_ontology", sparql=...)` of section 8; set the environment variables before loading the modules.
- **Answer:** (a) `Query refused: SERVICE is not allowed (it makes the server send HTTP requests)`; (b) `FROM and FROM NAMED are not allowed; the ontology graph is fixed`; (c) `SPARQL does not parse: Expected {SelectQuery | ConstructQuery | DescribeQuery | AskQuery}, found 'INSERT'`; (d) `query is 30346 characters; the limit is 20000` for a 30,346-character query; (e) `count: 5, truncated: true, total: 17736`, pointing to `query_ontology_page`; (f) stopped at 1.01 s, `query ran past 1 s and was stopped (X3D_MCP_SPARQL_TIMEOUT)`; node name: `node type must be a plain name such as Sphere`. Only (c) does not name a knob, because there is none: updates are not a mode.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3`, rdflib 7.6.0.

### D-MCP-5 What does `path=` reach
- **Level:** L2
- **Task:** Make a file `notes.cfg` holding `<passwd_like user="alice"><entry shell="/bin/sh"/></passwd_like>` and a file `data.txt` holding one line of text. Call `validate_x3d(path=...)` on each, `blob_put(path=...)` on each, and `validate_x3d(path=...)` again with `MCP_TRANSPORT=streamable-http`. Which of the five calls read the file?
- **Verify:** the harness of section 8; set `os.environ["MCP_TRANSPORT"]` before the last call.
- **Answer:** four of five read the file: both `validate_x3d` calls under stdio, and `blob_put` on `data.txt` (19 B stored). `blob_put` on `notes.cfg` is refused for its extension, with the message naming `X3D_MCP_BLOB_PATH_ROOTS`. Under the HTTP setting `validate_x3d(path=)` answers `Path input is disabled over the HTTP transport`. The XSD error quoted the element name `passwd_like`, which is what a validator error leaks.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3`.

### D-MCP-6 Forge a ledger
- **Level:** L3
- **Task:** Append two claims with `claim_append` (pass the first answer's `ledger` into the second call). Verify with `claims_verify`. Then (a) edit the first record's `claim` text, (b) drop the first line, (c) build a fresh one-record ledger that says the opposite. Which are caught? What would catch (c)?
- **Verify:** `claims_verify(ledger=...)`; the record keys are `schema, claim, grade, subject, instrument, evidence, prev, sha256`.
- **Answer:** intact: `ok: true, records: 2`. (a) `ok: false`, `hash does not match the record`, index 0. (b) `ok: false`, `prev is not the hash of the record before`, index 0. (c) `ok: true, records: 1`. Only a head hash held elsewhere, or a signature, would catch (c); the ledger has neither. Dropping the last record was not probed.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3`.

### D-MCP-7 Do it through a real client
- **Level:** L3
- **Task:** Start `python src/server.py` with `MCP_TRANSPORT=streamable-http`, a 32-character `X3D_MCP_BLOB_TOKEN` and a loopback host. With any MCP client list tools and read the instructions; `PUT` a 6 MB scene to `/blob` with the bearer token and call `validate_x3d(blob_id=..., return_mode="summary")`. Compare the tool count, the `tools/list` size and the answer with D-MCP-1, D-MCP-2 and the transcript.
- **Verify:** client output against the numbers in this chapter; also send a body over 4 MiB to `/mcp` and read the status.
- **Answer:** expected from the source, **[S]** until run: 53 tools; a body over 4,194,304 bytes refused with 413 `Request body too large`; the upload accepted up to 256 MiB.
- **Checked:** not run (no MCP client or socket was used in this chapter).

## Honest limits

- **No MCP client and no socket.** Every byte count is of a Python return value from a direct call. Argument validation by FastMCP, the JSON-RPC envelope and the duplicated `structuredContent` of `-> str` tools are not in my numbers. The 4 MiB cap is read in the installed `mcp` 1.30.0, not exercised. **[C]** for the read, **[S]** for the status code on the wire.
- **No model in the loop.** I measured the tool surface, not any effect on a model's output. The one repo experiment that would (`hint_loop_gemini.py`) needs a paid API and was not run. **[S]** for any benefit claim.
- **Synthetic scenes.** The 40,000-node scene and the 200,000-splat file are generated and repetitive; the 65 to 1 compression and 16,300 to 1 byte ratio are properties of them. The repo's 25 to 1 on a real scene is **[L]**.
- **Bytes, not tokens.** No tokeniser was run. **One rig:** 4 vCPU Intel Xeon 2.30 GHz, Python 3.13.18, `mcp` 1.30.0, software only; wall times (1.8 s inline against 4.0 s by name) are single runs.
- **Not run:** `render_image` and the Playwright tools (no Chromium), the Playground (sign-in and model endpoints), the HTTP routes and their rate and quota knobs (tests passed; no server was started), `X3D_MCP_ALLOWED_HOSTS` and `X3D_MCP_ALLOWED_ORIGINS`. Read, not run.
- **Source disagreements.** The `X3D_MCP_TOOL_MAX_BYTES` default is 96M in code and docs and 64M in a header comment of `blobs.py`: the code wins. The masterclass's 48 tools were the count at `13121b6`; 53 is the count at `b4efcd3`. The tool-list size at the fork base I measured (28,075 B, 34 tools) is the only base figure here.
- **Ledger probes** covered edit, first-record drop and a fresh chain; tail truncation and reordering were not probed.
- **Version drift.** A newer `mcp` may change the request cap or the `FastMCP` import path (the repo notes that 2.x renamed it).

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-MCP-1 | tools, prompts, resources registered | 53, 5, 2 (FastMCP lists 1 resource and 1 template) | C | `x3d_mcp fork b4efcd3`, Python `ast`, `mcp` 1.30.0 | x3d_mcp@b4efcd3:src/tools/*.py |
| N-MCP-2 | tools by transport | stdio 53; HTTP with token 53; HTTP without token 47 | C | `x3d_mcp fork b4efcd3`, `list_tools()` | x3d_mcp@b4efcd3:src/server.py |
| N-MCP-3 | tools and prompts at the fork base | 34 and 4 | C | `x3d_mcp upstream 74da0ec`, `list_tools()` | x3d_mcp@74da0ec:src/server.py |
| N-MCP-4 | `tools/list` size, compact JSON | 28,075 B (base); 64,426 B (stdio); 56,205 B (HTTP no token) | C | `x3d_mcp upstream 74da0ec`, `x3d_mcp fork b4efcd3` | scratch run, 2026-11-14 (method in D-MCP-2) |
| N-MCP-5 | growth of `tools/list` over the base | +36,351 B (+129.5 %) | C | arithmetic on N-MCP-4 | section 2 |
| N-MCP-6 | server instructions length | 2,212 (base); 3,353 (HTTP no token); 4,692 (stdio) characters | C | `x3d_mcp upstream 74da0ec`, `x3d_mcp fork b4efcd3` | x3d_mcp@b4efcd3:src/server.py |
| N-MCP-7 | tool functions that are `async def` | 26 of 53 | C | `x3d_mcp fork b4efcd3`, `inspect.iscoroutinefunction` | section 8 harness, 2026-11-14 |
| N-MCP-8 | bytes crossing the tool boundary, 10 edits, 40,000-node scene (6,505,087 B) | 176,462,418 inline; 10,849 by `blob_id` | C | `x3d_mcp fork b4efcd3`, in-process | scratch run, 2026-11-14 (method in D-MCP-3) |
| N-MCP-9 | same, 4,000-node scene (642,887 B) | 17,494,418 inline; 10,756 by `blob_id` | C | `x3d_mcp fork b4efcd3`, in-process | D-MCP-3, 2026-11-14 |
| N-MCP-10 | `blob_put` stored size of the 40,000-node scene | 100,091 B (zstd) for 6,505,087 B | C | `x3d_mcp fork b4efcd3`, zstandard 0.25.0 | scratch run, 2026-11-14 (method in D-MCP-3) |
| N-MCP-11 | SDK request-body cap | 4 MiB (4,194,304 B), `413 Request body too large` | C | `mcp` 1.30.0 `server/transport_security.py` (read) | installed package source |
| N-MCP-12 | splat run, 200,000 splats (11,200,362 B) | `splat_inspect` 3,310 B in 0.17 s; `splat_chunk` 4 chunks of 6.5 to 6.6 MB in 4.87 s, 5 of 5 files valid | C | `x3d_mcp fork b4efcd3`, numpy 2.5.4 | scratch run, seed 20261114 |
| N-MCP-13 | oversize start tag | 11,700,036 B, `checked: false`, 1,763 ms | C | `x3d_mcp fork b4efcd3`, libxml2 2.14.6 | scratch probe, 2026-11-14 |
| N-MCP-14 | SPARQL guard defaults | 20,000 chars; 20 s; 20,000 rows | C | `x3d_mcp fork b4efcd3` (read; refusals exercised at 1 s and 5 rows) | x3d_mcp@b4efcd3:src/x3d_utils/ontology_guard.py |
| N-MCP-15 | test suite | 1,367 passed, 27 skipped, 1,394 collected, 104 s | C | pytest 9.2.0, Python 3.13.18, no Chromium | x3d_mcp@b4efcd3:tests/ |
| N-MCP-16 | one 645 B scene, answer sizes | `validate_x3d` 62 B valid, 285 B one error; `exact_fix_hints` 1,325 B; `blob_put` 331 B; summary 539 B | C | `x3d_mcp fork b4efcd3` | section 7 table |
| N-MCP-17 | first `validate_x3d` call per schema version | 1,443 to 1,645 ms over two runs (4.1 and 4.0); later calls under 1 ms | C | `x3d_mcp fork b4efcd3`, libxml2 2.14.6 | section 8 byte table |
| N-MCP-18 | ledger probes on two records | edit caught, first-record drop caught, fresh forged chain verifies | C | `x3d_mcp fork b4efcd3` | D-MCP-6 |
| N-MCP-19 | stdio `path=` reach | 2 `validate_x3d` reads, 1 of 2 `blob_put` reads; 27 allowed extensions | C | `x3d_mcp fork b4efcd3` | D-MCP-5 |
| N-MCP-20 | tools in the masterclass snapshot | 48 (and 34 at the base) | L | stated in the teardown at `13121b6`, not re-run | x3d.docs@f172f67:docs/x3d_mcp/MASTERCLASS.md |
| N-MCP-21 | repo-stated zstd ratio on a real 10.9 MB scene | 25 to 1 | L | stated in the repo, not re-run | x3d_mcp@b4efcd3:docs/transfer-layer.md |
| N-MCP-22 | PR claims: false positives 96 to 22 (264 scenes); blind set 62.6 % to 100 % | as stated | L | PR descriptions via the masterclass; not re-derived | x3d.docs@f172f67:docs/x3d_mcp/MASTERCLASS.md |

## Sources and provenance

- `x3d_mcp@b4efcd3` (Merge PR #17, 2026-11-13): `src/server.py`, `src/tools/*.py`, `src/transfer/*.py`, `src/x3d_utils/{source,ontology_guard}.py`, `README.md`, `pyproject.toml`, `docs/transfer-layer.md`, `docs/splats.md`, `docs/EXACT-FIX-HINTS.md`, `docs/playground/ARCHITECTURE.md`, `tests/`. The fork base `74da0ec` was used for the tool-list and instruction sizes only.
- `x3d.docs@f172f67`: `docs/x3d_mcp/MASTERCLASS.md` (snapshot at `13121b6`: tool counts, PR claims, the playground-as-validator-client finding).
- `mcp` 1.30.0 (installed package): `server/transport_security.py` for the request-body cap.
- Re-run on 2026-11-14 in a scratch virtualenv, source checkouts untouched: AST and recorded-call counts, `list_tools()` under three environments, the 19-call transcript, the 40,000- and 4,000-node transfer runs, the 200,000-splat run, the oversize probe, the guards, the path probe, the ledger probe, and the full test suite.
- Not re-derived: the masterclass's 48-tool snapshot, PR descriptions, the repo's real-scene compression ratio, anything about the Playground's behaviour, any model's use of these tools. Claims about private data and unpublished material are not made here.
- Siblings: [01 The tether](01-the-tether.md), [03 The validator and the gates](03-validator-and-gates.md), [05 Semantic layer](05-semantic-layer.md), [06 X_ITE, the oracle](06-xite-the-oracle.md).
