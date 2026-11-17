# 21. Many hands on one scene: Yjs, CRDTs and the X3D scene graph

> **Say it:** A scene graph can be held as a Yjs document so that people, browsers and an LLM agent edit one X3D scene at the same time and always converge, provided the tree is stored as a flat node table with a parent register and the export is made order-independent. **[C]**

| field | value |
|---|---|
| chapter code | `YJS` |
| prerequisites | [02 Loom laws](02-loom-laws.md), [04 MCP for agents](04-mcp-for-agents.md), [08 The Babylon bridge](08-babylon-bridge.md) |
| after this you can | map an X3D node tree onto Yjs types and say which conflicts it resolves and how; list the five ways a tree CRDT can lose an edit; run two X_ITE browsers on one document and compare their pictures; put an agent on the same document as a person, with refusals instead of corruption; read the cost of a structural edit off a table |
| sources read | `x3d.loom@a9640eb:x3d.yjs/{README.md,src/yx3d.js,src/sai-adapter.js,src/agent.js,src/link.js,python/yx3d_py.py,test/,tools/,receipts/}`; `x3d_mcp:src/tools/scene_ops.py` (op vocabulary, read not run) |
| instruments used | Node v22.23.4 with Yjs 13.6.33 on an Intel Xeon 2.10 GHz x4 (no GPU); X_ITE 16.6.0 and Chromium 153.0.8010.12 with SwiftShader (software GL); three.js r187 through the `x3d.threejs` bridge shared reader; pycrdt 0.14.13; `x3d.loom@a9640eb` tests and receipts |

A scene is a tree plus fields, and two people editing it concurrently need a rule for every pair of operations. A conflict-free replicated data type (CRDT) makes the rule a property of the data, so peers exchange updates in any order, offline or not, and end identical. Yjs is the CRDT library the web uses most; this chapter is how an X3D scene sits on it, what the bridges do with the changes, and what it costs. Folder: `x3d.loom/x3d.yjs` (track prefix `YJS-`).

---

## 1. The map

```text
   person A (X_ITE)      person B (X_ITE)       agent (LLM)          Python (x3d_mcp side)
        |                      |                    |                       |
   X3DDoc (Y.Doc)         X3DDoc (Y.Doc)       X3DDoc (Y.Doc)         pycrdt Doc
        |                      |                    |                       |
        +----- Yjs updates (bytes, any order, any delay, any relay) --------+
        |
   observe(): resolved events  { field | added | removed | moved }
        |
   SaiAdapter  ->  X_ITE (granular)   |   x3d.loom bridge shim -> Babylon or three.js body
        |
   toXML(): canonical X3D text, validator-ready (deterministic on every peer)
```

| in scope | out of scope here |
|---|---|
| node, field, ROUTE and DEF/USE editing; reparenting; offline merge; an agent peer; X_ITE and three.js drawing | cursors and presence UI; permissions; a production relay; per-component vector merge; `<Script>` text merge |

Read next: deeper, [04 MCP for agents](04-mcp-for-agents.md) (the op vocabulary the agent peer reuses); wider, [08 The Babylon bridge](08-babylon-bridge.md) (the shim whose SAI the adapter speaks).

## 2. The model

| Y type | content | why |
|---|---|---|
| `x3d.nodes` Map | `uid -> Map{type, def, use, text, at, fields, kids}` | flat: a node's fields never move |
| `fields` Map per node | `name -> X3D attribute string` | last-writer-wins per field |
| `at` register | `"parentUid\|containerField"` | one parent after concurrent moves |
| `kids` Array per node, `x3d.roots` | child uids | sibling order only (a hint) |
| `x3d.routes` Map | `rid -> {from, fromField, to, toField}` with uids | survives a DEF rename |

```text
   nested (rejected)                       flat table + register (used)
   Transform                               nodes{ t1:{at:"#scene|children", fields{translation}},
     Shape  <- move = delete + insert              s1:{at:"t1|children"} }
   A moves Shape, B edits Shape.fields     A: s1.at = "t2|children"   B: s1.fields.x = ...
   -> B's edit is on a deleted Map: lost   -> both apply; the walk from roots decides the tree
```

`tree()` walks from `roots`, takes a uid under a parent only if its `at` agrees, drops duplicates, and leaves unreachable nodes out. The five ways a tree CRDT loses or breaks an edit, and the answer used:

| hazard | answer | tested |
|---|---|---|
| field edit concurrent with a move | flat table, edit survives | `field edit concurrent with a move` |
| concurrent moves of one node | LWW on `at`, duplicates dropped in the walk | same test |
| concurrent moves forming a cycle | unreachable from roots, so cut out; listed in `tree().orphans` | `concurrent moves ... cycle` |
| two adds into an SFNode slot | array order picks one; `sfnode-slot` conflict listed | `concurrent adds into an SFNode slot` |
| two nodes with one DEF | export renames the later uids `DEF_2`; `def-clash` listed | `delete concurrent with edit ... DEF clash` |

## 3. What the fuzz found

Three real bugs came out of random testing, none from the hand-written cases.

| bug | symptom | cause | fix |
|---|---|---|---|
| attribute order | peers converged on every Yjs type yet `toXML()` text differed (9 of 12 seeds when the sort is removed) | `Y.Map` iteration order is the order that replica integrated updates | `tree()` sorts field names |
| runaway delete | `RangeError: Maximum call stack size exceeded` in `remove()` (bench, 200 seeds) | `kids` arrays are hints and can form a cycle after concurrent moves; delete followed them | follow only children whose `at` register names this parent, once each |
| orphans pile up | 5,096 orphan nodes over 200 seeds (about 25 per seed) | a subtree deleted or cut by a cycle keeps its concurrent children | counted and reported, not collected: a limit, the Honest limits section |

## 4. Two browsers, one scene

Rig: Chromium 153.0.8010.12 SwiftShader, X_ITE 16.6.0, two `x3d-canvas` elements in one page, an in-process link (no network). After each step the two canvases are screenshotted and compared pixel by pixel (a pixel counts as different when the sum of channel differences exceeds 6; 145,116 pixels per canvas).

| step | peers act | different pixels |
|---|---|---|
| initial load | none | 0 |
| 20 `translation` edits on A | A | 0 |
| add a Transform+Shape+Sphere on A | A | 0 |
| move it under another Transform on B | B | 0 |
| remove it on B | B | 0 |
| link offline, both edit (control: must differ) | A and B | 16,633 |
| link back online | exchange | 0 |
| agent peer: modify, refused op, add | C | 0 |

At the end the node names reachable in X_ITE (walked through the SAI) equal the document's node uids on both browsers (23 of 23), and `toXML()` is identical on A, B and the agent's document. The offline row is the control that shows the comparison can fail.

Apply cost, A's `setField` to the SAI field value read on B (20 edits, polled with `setTimeout(0)`): median 0.40 ms, max 2.3 ms. This is apply cost on a no-network link. A real relay adds its round trip.

## 5. The bridges

The three.js bridge shares its reader with the Babylon bridge, and its shim speaks the subset of the SAI the adapter needs (`getNamedNode`, `getFieldDefinitions`, property get and set, `rootNodes`, `addRootNode`). The adapter probes the first node (`getField` exists in X_ITE only) and picks a mode.

| operation | X_ITE mode | bridge mode |
|---|---|---|
| field edit | `field.fromString` | typed value parsed from the string (`parseValue`); unknown types reload |
| add | MFNode splice at the index, SFNode assignment | append by `push` or `addRootNode`; other positions reload |
| remove, move | detach by DEF name, attach | reload the world |

Run on the three.js bridge (r187, shared reader, SwiftShader): 20 field edits median 0.20 ms, max 2.1 ms; seven steps (fields, colour, add at root, append, move, remove, agent) each ended with the bridge's node set equal to the document's; the picture after incremental application and the picture after loading the final text from scratch differ in 0 of 153,600 pixels. Two X_ITE facts found on the way: SAI wrappers are not identity-stable (match nodes by DEF name, not `===`), and an SFNode read through `field.getValue()` hands back an internal object, while property access (`node.appearance`) hands back the real SAI node.

## 6. An LLM peer

The agent is one more Yjs peer. `agentApply(doc, ops, id)` takes JSON ops against DEF names (`modify_node`, `add_node`, `remove_node`, `move_node`, the same verbs as `x3d_mcp/src/tools/scene_ops.py`), checks each, applies it as one transaction tagged `agent:<id>`, and returns a per-op result. A hallucinated DEF returns `{ok:false, error:"no node DEF Nope"}` and touches nothing. The tag lets a UI show who changed what. A Python peer (`python/yx3d_py.py`, pycrdt) reads and writes the same layout, so an x3d_mcp server can join a session by exchanging update bytes: the test sends a JS state to Python, edits `translation` there while JS edits `scale`, and both ends hold both edits.

Nothing here makes the agent's edit valid X3D: a field value is any string. The tether ([01](01-the-tether.md)) still applies: run the canonical `toXML()` through the validator before an agent's session is accepted.

## 7. Cost

All rows: Node v22.23.4, Yjs 13.6.33, Intel Xeon 2.10 GHz x4, wall time, no GPU. Scene unit: Transform, Shape, Appearance, Material, Box (5 nodes).

| nodes | loadXML | toXML | tree() | state bytes | bytes per node |
|---|---|---|---|---|---|
| 500 | 19.5 ms | 8.0 ms | 4.7 ms | 77,749 | 155.5 |
| 5,000 | 96.9 ms | 44.7 ms | 32.2 ms | 819,211 | 163.8 |
| 50,000 | 535.5 ms | 285.4 ms | 235.8 ms | 8,379,203 | 167.6 |

| nodes | local setField/s | with observer (field-only path) | add+remove pairs/s, incremental | add+remove pairs/s, full rebuild | bytes per field update | remote apply/s |
|---|---|---|---|---|---|---|
| 500 | 89,496 | 162,639 | 844 | 296.8 | 51 | 87,774 |
| 5,000 | 140,378 | 183,330 | 44 | 21.7 | 54 | 84,005 |
| 50,000 | 196,851 | 191,547 | 1 | 1.4 | 52 | 147,739 |

The scene above is flat: all 10,000 units hang from the root, so every structural edit re-resolves one 10,000-entry child list. With bounded fan-out the cost stops following the scene (groups of 10, one Box added under a leaf group and removed):

| nodes | depth | pairs/s incremental | pairs/s full rebuild |
|---|---|---|---|
| 511 | 2 | 6,572 | 305.3 |
| 5,111 | 3 | 6,967 | 15.6 |
| 51,111 | 4 | 6,687 | 1.5 |

Reading it: field edits, the thing a drag produces, are flat in scene size and cheap on the wire (51 to 54 bytes). A structural edit used to rebuild the resolved index twice (O(n)); `observe()` now keeps an incremental index and re-resolves only the child lists of the parents a transaction touched, plus the subtrees whose reachability flipped, so the cost follows the fan-out of those parents. The O(n) rebuild survives as `observe(cb, {full:true})`, the oracle the tests compare against after every operation. The state is about 160 bytes per node because each node is a Map with a fields Map and a kids Array.

Convergence fuzz (`tools/bench.js`): 200 seeds, 3 peers, 300 random operations each (field set, add, remove, move, SFNode-slot add, partial syncs): 200 of 200 converged to identical text, and the incremental index equalled the full rebuild on 600 of 600 peer copies, in 7.2 s.

## Heuristics

| ID | Rule | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-YJS-1 | Store the tree as a flat table with a parent register; never nest a node's Map inside its parent's. | [C] | move-with-edit test | `x3d.loom@a9640eb` tests |
| H-YJS-2 | Fuzz the export text, not the Yjs state: converged state can still print differently. | [C] | attribute-order bug, 9 of 12 seeds | same, Node v22.23.4 |
| H-YJS-3 | Treat order-hint arrays as hints: walk by the register, with a visited set. | [C] | runaway-delete bug | bench, 200 seeds |
| H-YJS-4 | Skip structure work for field-only transactions, and keep an incremental index for the rest; keep the O(n) rebuild as the test oracle. | [C] | 6,687 vs 1.5 pairs/s at 51,111 nodes, fan-out 10 | `tools/bench.js` |
| H-YJS-9 | Test an incremental structure with a differential check against the full rebuild after every operation, not only at the end. | [C] | 8 seeds x 250 operations, plus 600 of 600 copies in the bench | `x3d.loom@a9640eb:x3d.yjs/test` |
| H-YJS-5 | Match SAI nodes by DEF name, never by object identity. | [C] | X_ITE 16.6.0 wrappers | `tools/e2e.js` |
| H-YJS-6 | Give every peer a control step that must differ (offline edits) before trusting a zero-difference picture. | [C] | 16,633 pixels differ | `receipts/e2e-xite.json` |
| H-YJS-8 | Keep user DEF names out of the render path: render every node as `y_<uid>` so a DEF clash between peers cannot misdirect a USE or a ROUTE. | [L] | by construction; the unit test checks the clash export names, no renderer run with a clash | `x3d.loom@a9640eb:x3d.yjs/src/yx3d.js` |
| H-YJS-7 | Validate the agent's ops against the document before they enter it; return refusals as results. | [L] | `Nope` DEF refused; no validator run on agent output yet | `src/agent.js` |

## Drills

Commands run from `x3d.loom/x3d.yjs` after `npm ci`; Playwright must be on `NODE_PATH`.

### D-YJS-1 Run the suite
- **Level:** L1
- **Task:** Run the unit, fuzz and Python-peer tests and count them.
- **Verify:** `node --test test/*.test.js`
- **Answer:** 30 tests, 30 pass, 0 fail (the Python-peer test is skipped if pycrdt is missing).
- **Checked:** 2026-11-15 Node v22.23.4, Yjs 13.6.33, pycrdt 0.14.13

### D-YJS-2 Break the export
- **Level:** L3
- **Task:** In `tree()`, replace the sorted key list with `n.get('fields').keys()` and run the fuzz tests. Say which seeds fail and why, then restore.
- **Verify:** `node --test test/*.test.js`
- **Answer:** 9 of the 12 seeds fail (1, 2, 4, 6, 7, 8, 41, 103, 150) with texts that differ only in attribute order; Y.Map iteration order depends on integration order.
- **Checked:** 2026-11-15 Node v22.23.4, Yjs 13.6.33

### D-YJS-3 Two browsers
- **Level:** L2
- **Task:** Run the two-browser rig and read the different-pixel counts. Which row is the control and what does it prove?
- **Verify:** `NODE_PATH=<playwright dir> node tools/e2e.js` and read `checks`.
- **Answer:** all rows 0 except `offlineDiverged` (16,633 pixels): the control, showing the comparison detects divergence.
- **Checked:** 2026-11-15 Chromium 153.0.8010.12 SwiftShader, X_ITE 16.6.0

### D-YJS-4 Price a structural edit
- **Level:** L2
- **Task:** Run `node tools/bench.js`. In the flat scene, at which node count does an add+remove pair drop below 60 per second with the incremental index, and why does the balanced scene not drop?
- **Verify:** read the second and third tables.
- **Answer:** between 500 nodes (844/s) and 5,000 nodes (44/s); at 50,000 it is 1/s, because the root holds 10,000 children and every edit re-resolves that list. With fan-out 10 the rate stays 6,572 to 6,967 per second from 511 to 51,111 nodes.
- **Checked:** 2026-11-15 Node v22.23.4, Intel Xeon 2.10 GHz x4

### D-YJS-5 Predict the winner
- **Level:** L1
- **Task:** Two peers concurrently add a Sphere and a Cone as the `geometry` of one Shape. What does each peer draw, and what does `tree().conflicts` say?
- **Verify:** section 2 table and `test/yx3d.test.js`.
- **Answer:** both peers draw the same one (array order decides); one `sfnode-slot` conflict is reported; the other node is kept in the document, not drawn.
- **Checked:** 2026-11-15 `x3d.loom@a9640eb` tests

## Honest limits

* **[C]** Latency figures are apply cost on an in-process link. No WebSocket or WebRTC run was made; wire latency is not measured.
* **[C]** Fields merge as whole strings: two peers dragging different axes of one `translation` get one winner.
* **[C]** Structural edits cost O(fan-out of the touched parents): a flat scene with 10,000 children under one parent still manages about 1 add+remove pair per second; a child list is re-resolved whole, not patched from the Yjs delta.
* **[C]** Orphans (cycles, concurrent edits under deleted subtrees) accumulate and are not collected.
* **[C]** The bridge adapter reloads the world for remove, move, inserts that are not appends, and field types `parseValue` does not read (MFVec3f, MFColor and others).
* **[L]** The Babylon body was not run through the adapter; it shares the shim with the three.js body, so the same behaviour is expected.
* **[S]** Behaviour with several hundred simultaneous peers, a real relay and long histories is not measured.
* **[C]** No renderer-to-renderer comparison is made between X_ITE and the bridge in these runs; each is compared with itself.

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-YJS-1 | unit, fuzz and differential tests passing | 30 of 30 | [C] | Node v22.23.4, Yjs 13.6.33 | `x3d.loom@a9640eb:x3d.yjs/test` |
| N-YJS-2 | fuzz seeds converged | 200 of 200 | [C] | same, 3 peers x 300 ops | `x3d.yjs/receipts/bench.md` |
| N-YJS-3 | different pixels after add, move, remove | 0 of 145,116 each | [C] | X_ITE 16.6.0, Chromium 153, SwiftShader | `x3d.yjs/receipts/e2e-xite.json` |
| N-YJS-4 | different pixels, offline control | 16,633 | [C] | same | same |
| N-YJS-5 | apply latency, median, X_ITE | 0.40 ms | [C] | same, in-process link | same |
| N-YJS-6 | apply latency, median, three.js bridge | 0.20 ms | [C] | three r187, SwiftShader | `x3d.yjs/receipts/e2e-threejs-bridge.json` |
| N-YJS-7 | incremental vs fresh picture, bridge | 0 of 153,600 pixels | [C] | same | same |
| N-YJS-8 | bytes per field update | 51 to 54 | [C] | Node v22.23.4, Yjs 13.6.33 | `x3d.yjs/receipts/bench.md` |
| N-YJS-9 | state size per node | 158 to 165 bytes | [C] | same | same |
| N-YJS-10 | local setField at 50,000 nodes with observer | 191,547 per second | [C] | Intel Xeon 2.10 GHz x4 | same |
| N-YJS-11 | structural add+remove pairs, flat scene, incremental index, at 500 / 5,000 / 50,000 nodes | 844 / 44 / 1 per second | [C] | same | same |
| N-YJS-12 | loadXML at 50,000 nodes | 555.7 ms | [C] | same | same |
| N-YJS-13 | remote apply at 500 nodes | 87,774 per second | [C] | same | same |
| N-YJS-16 | add+remove pairs, fan-out 10, incremental, at 511 / 5,111 / 51,111 nodes | 6,572 / 6,967 / 6,687 per second | [C] | same | same |
| N-YJS-17 | same edit with the full rebuild | 305.3 / 15.6 / 1.5 per second | [C] | same | same |
| N-YJS-14 | orphan nodes over 200 fuzz seeds | 5,096 | [C] | same | same |
| N-YJS-15 | reported conflicts over 200 seeds: def-clash, sfnode-slot, duplicate | 223, 34, 15 | [C] | same | same |

## Sources and provenance

`x3d.loom@a9640eb` folder `x3d.yjs` (branch of the first pull request), read and run on 2026-11-15; `x3d_mcp` op vocabulary read from `src/tools/scene_ops.py`, not run; Yjs 13.6.33 from npm; pycrdt 0.14.13 from PyPI; Yjs: Kevin Jahns and contributors (MIT).
