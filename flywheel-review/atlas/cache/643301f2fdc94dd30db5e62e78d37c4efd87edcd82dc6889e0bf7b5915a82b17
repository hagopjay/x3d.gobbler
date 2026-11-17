# 05. The semantic layer: RDF, OWL, SPARQL, SHACL on X3D

> **Say it:** An X3D scene can be turned into a graph of facts, questioned with SPARQL, held to SHACL shapes and (carefully) reasoned over, but the ontology only proposes, the shapes dispose and the validators gate; every result names a node, a check id and an instrument. **[C]**

| field | value |
|---|---|
| chapter code | `SEM` |
| prerequisites | [01 The tether](01-the-tether.md); [03 The validator and the gates](03-validator-and-gates.md) for the rungs this layer sits beside |
| after this you can | convert a scene to Turtle and say whether the DTD defaults were applied; write and run SPARQL for DEF/USE, ROUTE chains, colours and parent/child legality; write a SHACL shape that catches a scene the XSD passes (a part that floats or sinks); explain why `inference="rdfs"` turns a clean scene into 2,185 findings; call the five semantic tools of `x3d_mcp` PR #17, name their caps and guards, read the `instrument` block; say which layer catches which fault, from a measured matrix |
| sources read | x3d_mcp@b4efcd3:src/tools/semantic_web.py, src/x3d_utils/{semantic_web,scene_rdf,ontology_guard}.py, src/validation/schemas/ (both ontologies, x3d-core shapes), docs/semantic-web-tools.md, tests/fixtures/scene_rdf/*; x3d.docs@f172f67:docs/x3d.onto/MASTERCLASS.md |
| instruments used | `x3d_mcp fork b4efcd3`; `x3d_mcp fork 13121b6` (PR base); ontology `X3dOntology4.1.ttl` (sha256 057f1ba083a6) and `X3dOntology4.0.ttl` (b7bb83d13177) as bundled; `X3DUOM 4.1` (4fc10e8e15c0); `X3D XSD 4.1`; stylesheet `X3dToTurtle.xslt r40388` (e3c5aa40756b, read from the fixture manifest, not run); rdflib 7.6.0; pyshacl 0.40.2; owlrl 7.6.2; Python 3.13.18; software only (4 vCPU Intel Xeon 2.30 GHz, no GPU) |

Rig for every **[C]** number: a scratch virtualenv with the repo's pinned dependencies (`mcp` 1.30.0, `lxml` 6.1.3, `xmlschema` 4.3.2, `pytest` 9.2.0 and the libraries above), 2026-11-14, a read-only checkout of `x3d_mcp@b4efcd3`. Tools were called in memory through `server.mcp.call_tool` (the stdio path minus the transport) and `x3d_utils.semantic_web`. No LLM ran; a "model turn" is scripted and says so. No network, GPU or paid API.

## 1. The map

```text
 X3D document (XML)                          X3D Ontology 4.1 (TBox, Consortium Turtle, bundled)
   |  version picks the DTD: 3.x -> 3.3,        364 classes, 1,064 properties, 18,108 triples
   |  4.0 -> 4.0, else 4.1 (containerField      0 owl:disjointWith, 0 owl:Restriction
   |  and attribute defaults)
   v                                                            |
 scene_to_rdf --> scene graph (ABox) -- joined with ------------+
   |              graph_id = sha256(Turtle)[:16]
   +--> sparql_scene    SELECT / ASK             "what is in it?"    an answer, never a verdict
   +--> rdf_infer       subclass | rdfs | owl-rl  "what follows?"    proposes types
   +--> shacl_validate  x3d-core + your shapes    "what must hold?"  disposes: node, id, fix
   +--> ontology_vs_gate(child)  map | gate | XSD "where may it go?" three answers side by side
 outside RDF (document order lives here): validate_x3d (XSD)  validate_semantic  render_image
```

| layer | answers | instrument | blind to |
|---|---|---|---|
| RDF graph | what nodes, fields and links the file states | converter, isomorphic to 10 of 10 recorded Saxon goldens | order, defaults (omitted), MFString items |
| SPARQL | which nodes match; how many | rdflib 7.6.0 | whether a match is wrong |
| RDFS, OWL-RL | which types follow from the axioms | owlrl 7.6.2 | anything not axiomatised (no disjointness) |
| SHACL | what must hold of every matching node | pyshacl 0.40.2 | order; engine-dependent features |

**In scope:** the five semantic tools of PR #17, the ontology as bundled, shapes and SPARQL you can run, and the plan for a public teaching lab. **Out of scope:** transport and the other 48 tools ([04](04-mcp-for-agents.md)); what X_ITE draws ([06](06-xite-the-oracle.md)); the XSD and semantic rungs ([03](03-validator-and-gates.md)).

**Read next:** deeper, `x3d_mcp@b4efcd3:docs/semantic-web-tools.md` and [the x3d.onto masterclass](../x3d.onto/MASTERCLASS.md); wider, [04 MCP for agents](04-mcp-for-agents.md) for how a model calls these tools.

## 2. RDF in ten minutes: what a graph gains and what it forgets

A **triple** is subject, predicate, object: IRIs and literals; a set of triples is a graph. The **ABox** holds the facts about one scene, the **TBox** the vocabulary (classes such as `x3do:Transform`, properties such as `x3do:hasChildren`). One XML element becomes one **individual**. An excerpt from `LabScene41.x3d` (a scene written for the converter's tests; 230 triples, 28 individuals):

```xml
<Transform DEF='Orb' translation='0 1 0'>
  <MetadataString name='role' value='"hero"' containerField='metadata'/>
  <Shape><Appearance><Material DEF='Blue' diffuseColor='0.1 0.5 1' transparency='0.2'/></Appearance>
    <Sphere radius='0.75'/></Shape>
</Transform>
```

```turtle
:Orb a owl:NamedIndividual, x3do:Transform ;
  x3do:hasParent :Scene ;
  x3do:hasMetadata :MetadataString_2_4_1 ;     # containerField='metadata' was written in the XML
  x3do:hasChildren :Shape_2_4_2 ;              # Shape's default containerField is 'children'
  x3do:DEF "Orb" ;
  x3do:translation ( 0 1 0 ) .                 # an rdf:List: first / rest cells
:Shape_2_4_2 a owl:NamedIndividual, x3do:Shape ; x3do:hasParent :Orb ;   # no DEF: positional name
  x3do:hasAppearance :Appearance_2_4_2_1 ; x3do:hasGeometry :Sphere_2_4_2_2 .   # <Element>_<i>_<j>_<k>
:Blue a owl:NamedIndividual, x3do:Material ; x3do:hasParent :Appearance_2_4_2_1 ; x3do:DEF "Blue" ;
  x3do:diffuseColor ( 0.1 0.5 1 ) ; x3do:transparency 0.2 .
```

| X3D | triples (read from the converter and the output above) | grade |
|---|---|---|
| element; `DEF='Orb'` | `:Name a owl:NamedIndividual, x3do:<Element>`; the DEF is the IRI and `x3do:DEF "Orb"` | **[C]** |
| `USE='Blue'` | a new individual `:Blue-USE-1 a x3do:Material ; owl:sameAs :Blue`, no fields | **[C]** |
| parent and child | both ways: `:c x3do:hasParent :p` and `:p x3do:has<Field> :c` | **[C]** |
| SFFloat, SFBool; SFVec3f, SFColor, MFFloat | bare `0.75`, `true`; an `rdf:List` `( 0.1 0.5 1 )` | **[C]** |
| SFTime, SFString, MFString | one string literal: an MFString's items are not separate | **[C]** |
| a field at its default | omitted: `<Cone/>` is a type and a parent, 2 triples | **[C]** |
| `ROUTE` | an `x3do:ROUTE` individual under `x3do:hasROUTE`; endpoints are DEF strings | **[C]** |

| the graph gains | evidence | the graph forgets | evidence |
|---|---|---|---|
| class-hierarchy queries: all geometry in one pattern | Q2: 3 rows | the order of `children` (Switch picks by index) | Q11 lists 3 children as a set, no order |
| reuse as identity: 19 USE copies in `Altar.x3d` in one query | Q3b: 19 rows | USE before DEF | same graph either way (D-SEM-8) |
| a verdict with a node, DEF, check id and fix | section 7 | stable names for unnamed nodes | one inserted node renamed 8 of 42 (section 4) |

Three readings of "nothing here": **open world** (RDFS, OWL) is unknown, not false; **closed over this graph** (SPARQL `FILTER NOT EXISTS`): absent from this data (Q6); **closed by declaration** (SHACL): a violation if the shape says so (S2 on the same Shape).

## 3. The rule: the ontology proposes, shapes dispose, the validator gates

Each verb is a different instrument. The ontology states which property a class may use and what range it admits: what is *conceivable*. A SHACL shape turns a requirement into a repeatable yes or no on named nodes. The XSD and `validate_semantic` decide validity and see document order, which RDF cannot. Never write "the ontology can gate". The measured case, "where may this node go?", answers three ways in `ontology_vs_gate(child)` (rules in section 8; XSD verdicts from the shipped `verified-containment.json` plus live one-node documents; `x3d_mcp fork b4efcd3`, `X3DUOM 4.1`, 2026-11-14):

```text
 where may a Box go?                                       each # is one parent
 ontology map   12 parents (10 concrete, 2 abstract)       ############
 X3DUOM gate    10 parents, 9 of them also in the map      ##########
 XSD on the 10 gate pairs: 5 accepted, 3 rejected, 2 unclear              #####  (accepted)
 where may an ImageTexture go?                             each # is about 2 parents
 ontology map   62 parents (55 concrete), 85 rows          ##############################
 X3DUOM gate    14 parents, 36 pairs; 12 parents in both   #######
 XSD on the 36 gate pairs: 31 accepted, 1 rejected, 4 unclear;
 on the 44 map-only pairs it could test: 42 rejected, 2 unclear
```

The gate is not the last word: for Box, 3 of 10 gate pairs are rejected by the XSD (`GeoMetadata.data`, `LinePickSensor.pickingGeometry`, `PointPickSensor.pickingGeometry`). Quote the layer you ran. The "62 slots for a Box" in older notes keeps every `(parent, field)` whose range is the bare `X3DNode` class; `node_parents` filters it on purpose and gives 12 (source conflict 3, Honest limits).

## 4. Faithful X3D to Turtle

The Consortium's `X3dToTurtle.xslt` is run on documents *with their DTD*, so attributes the author never wrote, above all `containerField`, arrive as defaults. A property is `has` plus the upper-camel `containerField`, or the element name if there is none. Drop the DOCTYPE and every `<Sphere/>` becomes `x3do:hasSphere` instead of `x3do:hasGeometry`; SPARQL joined to the ontology then returns silent blanks.

| measurement | value | grade | instrument |
|---|---|---|---|
| converter graph vs recorded Saxon golden, 10 fixtures | isomorphic 10 of 10; text-identical 0 of 10 (HelloWorld: 118 of 197 lines differ) | **[C]** | `x3d_mcp fork b4efcd3`, rdflib `isomorphic`, `difflib` |
| elements with a `containerField` default in the converter tables | 235 of 252 (3.3), 261 of 278 (4.0), 268 of 285 (4.1) | **[C]** | tables sha256 1a5f3229a7ee |
| DOCTYPE stripped (emulated: tables emptied): `has*` names the ontology does not declare | HelloWorld 0 faithful, 8 stripped (`hasBackground hasGroup hasImageTexture hasSphere hasText hasTransform hasViewpoint hasWorldInfo`); Altar 0 to 7; SwitchOrder 0 to 4 | **[C]** | `scene_rdf`, ontology 4.1 (D-SEM-3) |

The emulation is the converter's own rule for a node its tables lack, applied to all nodes; it is not a Saxon run. The count excludes `hasROUTE` and `hasProtoDeclare`.

| document `version` | DTD defaults | ontology for `sparql_scene`, `rdf_infer` | ontology for `shacl_validate` |
|---|---|---|---|
| 3.x (HelloWorld is 3.3) | 3.3 | 4.0, rewritten into the 4.1 namespace | 4.1 |
| 4.0 | 4.0 | 4.0 | 4.1 |
| 4.1, later or none | 4.1 | 4.1 | 4.1 |

The split matters: Q8 (a field the parent type does not allow) on the 3.3 `HelloWorldFaulted` returns **6** rows against 4.0 and **1** against 4.1 (D-SEM-4). The 4.0 file lists fewer `rdfs:domain` classes, so five legal fields look illegal; the shapes therefore read 4.1 for every document.

**Identity.** DEF names are stable IRIs; anything else is positional and shifts on insertion. One `<NavigationInfo/>` inserted before HelloWorld's Group: 42 individuals before, 43 after, **34 kept, 8 renamed**, 5 of 5 DEF-named kept (`x3d_mcp fork b4efcd3`). Without an `identifier` meta the base is the shared `https://www.web3d.org/semantics/scenes/UnnamedX3dModel.ttl#`; the tool warns that such scenes collide when merged; `base_iri=` overrides it. Two nodes with one DEF merge into one IRI; S8 `duplicate-def` fired when their parents differed, not when they shared one, and the XSD rejected both (two probes, **[C]**): the XSD is the gate here.

## 5. SPARQL on scenes

`sparql_scene(sparql, graph_id | content | path | blob_id, include_ontology=true, ontology_version, offset, limit)` runs SELECT or ASK over the scene joined to the ontology. Pre-declared prefixes: `x3do:` (4.1 namespace), `rdf`, `rdfs`, `owl`, `xsd`, `dcterms`, and `:` for the scene base. Behaviours that surprise (all **[C]**, `x3d_mcp fork b4efcd3`):

| behaviour | what happens | consequence |
|---|---|---|
| rows are sorted by the server | pages sort by each row's JSON text | stable `page_sha256`; do not rely on ORDER BY |
| a guard parses first | UPDATE, LOAD, CONSTRUCT, DESCRIBE, SERVICE, FROM, a syntax error and a 21,393-character query: 8 of 8 refused | no write, no network |
| multi-step paths over the joined graph can duplicate rows | `rdf:rest/rdf:first` twice in a pattern: 4 rows for one material with the ontology joined, 1 without (D-SEM-8) | use `DISTINCT`, or explicit `rdf:rest` hops |
| the first query on a scene is slow | 520 to 730 ms, then 15 to 30 ms | pass `graph_id=` |

The catalogue; every query is complete, runs as the `sparql` argument or with `sw.sparql(sg, q, ontology_version="4.1")`. Rows are on the named fixture:

```sparql
# Q2  SELECT ?n ?t WHERE { ?n a ?t . ?t rdfs:subClassOf* x3do:X3DGeometryNode . FILTER(STRSTARTS(STR(?t), STR(x3do:))) }
# Q3  SELECT ?use ?def WHERE { ?use owl:sameAs ?def }   (Q3b: the same on Altar)
# Q4  SELECT ?a ?b ?c WHERE { ?r1 x3do:fromNode ?a ; x3do:toNode ?b . ?r2 x3do:fromNode ?b ; x3do:toNode ?c }
# Q5  SELECT DISTINCT ?m ?Y WHERE { ?m a x3do:Material ; x3do:diffuseColor ?c .
#       ?c rdf:first ?r ; rdf:rest/rdf:first ?g ; rdf:rest/rdf:rest/rdf:first ?b .
#       BIND(0.2126*?r + 0.7152*?g + 0.0722*?b AS ?Y) }
# Q6  SELECT ?s WHERE { ?s a x3do:Shape . FILTER NOT EXISTS { ?s x3do:hasGeometry ?g } FILTER NOT EXISTS { ?s owl:sameAs ?d } }
# Q8  SELECT ?parent ?p ?child WHERE { ?parent ?p ?child . ?p rdfs:subPropertyOf+ x3do:hasChild . ?parent a ?pt .
#       FILTER(STRSTARTS(STR(?pt), STR(x3do:))) FILTER NOT EXISTS { ?p rdfs:domain ?d . ?pt rdfs:subClassOf* ?d } }
# Q9  SELECT ?use ?ut ?def ?dt WHERE { ?use owl:sameAs ?def . ?use a ?ut . ?def a ?dt .
#       FILTER(STRSTARTS(STR(?ut), STR(x3do:)) && STRSTARTS(STR(?dt), STR(x3do:)) && ?ut != ?dt) }
# Q11 SELECT ?c WHERE { :Picker x3do:hasChildren ?c }
```

| query | scene | rows | what it teaches |
|---|---|---|---|
| Q2 geometry | LabScene41 | 3 (Box, Cone, Sphere) | one pattern replaces 37 geometry classes (34 leaves; 4.1 file) |
| Q3, Q3b | LabScene41, Altar | 1 (`:Blue-USE-1` to `:Blue`), 19 | `owl:sameAs` is the whole USE story |
| Q4 | LabScene41 | 1 (Clock, Spin, Orb) | ROUTE endpoints are strings; join on `x3do:DEF` |
| Q5 | LabScene41 | 1 (`:Blue`, Y = 0.45106) | colours are lists; the DISTINCT matters |
| Q6 | HelloWorldFaulted | 1 (`Shape_2_3_1_1`) | closed-world absence; the SHACL twin is S2 |
| Q8 | HelloWorldFaulted | 6 against 4.0, 1 against 4.1 | legality is a question to the ontology, and the release matters |
| Q9 | HelloWorldFaulted | 1 (Material USE of an ImageTexture DEF) | the XSD and OWL cannot see it |
| Q11 | SwitchOrder | 3, no order | a set, not a sequence |

A query that returns rows is not a verdict: use SPARQL to find out, SHACL to say it every time (Q9 and S3 state one fact).

## 6. RDFS and OWL-RL on the X3D Ontology

| profile of `rdf_infer` | adds | HelloWorld (3.3, ontology 4.0) | LabScene41 (4.1) |
|---|---|---|---|
| `subclass` (default) | each node's superclasses as `rdf:type` | +81 triples; types per node 3 / 3 / 8 (min / median / max); 688 ms | +72; 3 / 4 / 6; 46 ms |
| `rdfs` | the full RDFS closure of scene plus ontology | +17,985; 5 / 34 / 343; 4.9 s | +18,620; 5 / 30.5 / 352; 4.8 s |
| `owl-rl` | the OWL 2 RL closure | +32,510; 15.2 s | +33,394; 15.4 s |

(`x3d_mcp fork b4efcd3`, owlrl 7.6.2, **[C]**.) `subclass` is safe: a Sphere is also an `X3DGeometryNode` and an `X3DNode`. The others are not, and one modelling choice is the cause:

```text
 x3do:DEF  rdfs:domain  Anchor, Appearance, Box, ..., Transform, ..., Viewpoint   (337 in 4.1)
        |  RDFS rule rdfs2: if p rdfs:domain C and s p o then s a C, once per listed class
        v
 :Orb  x3do:DEF "Orb"   =>   :Orb a Anchor, a Appearance, a Box, a Transform, ... all at once
```

The authors list many classes as the domain of one field to say "any of these may carry it" (a union); RDFS and OWL read several `rdfs:domain` values as **all apply** (an intersection). Counts re-derived on the bundled files (rdflib 7.6.0, **[C]**):

| quantity | 4.0 | 4.1 |
|---|---|---|
| triples; classes; object and datatype properties | 17,736; 355; 326 and 712 | 18,108; 364; 337 and 727 |
| properties with a domain; with more than one; most domains on one | 877; 296; 347 | 901; 294; 355 |
| domains of `x3do:DEF`; `owl:disjointWith`; `owl:Restriction` | 329; 0; 0 | 337; 0; 0 |

Three consequences. **The type count depends on whether the node has a DEF:** the DEF'd Transform in HelloWorld ends with 343 types, the DEF-less Group 51; quote counts with the DEF status and the release. **OWL has no teeth here:** with no disjointness axioms a node typed both `Box` and `Transform` is consistent; OWL-RL expanded it to 14 types in 8.3 s with 0 subjects typed `owl:Nothing`, so the ontology cannot reject a chimera and cannot gate. **A closed graph answers differently:** with `inference="rdfs"` the shapes find 2,180 nodes holding fields they should not (section 7). Use `subclass` for class membership; use `rdfs` and `owl-rl` to study the ontology, never to validate a scene.

## 7. SHACL shapes

A **shape** says what must hold of every node it targets; a **result** names the node, path, message and shape. The bundled `x3d-core` file has 272 lines, 9 node shapes, 11 property shapes, 12 `check_id` values; 5 shapes carry a SHACL 1.2 `sh:agentInstruction`, which pyshacl 0.40.2 treats as data. Shapes read a 1,734-triple slice of the 4.1 ontology (of 18,108).

| shape | check_id | severity | rule and measured case |
|---|---|---|---|
| S1 | `colour-out-of-range`, `value-out-of-range` | Violation | colour, transparency, intensity in [0, 1]; `0.1 1.5 1` and `transparency` 1.2 caught |
| S1b | `tuple-count` | Violation | an SFColor has 3 members (a SPARQL constraint, see below); a 2-component colour caught |
| S2 | `shape-no-geometry` | Warning | a non-USE Shape has geometry |
| S3 | `use-type-mismatch`, `use-undefined-def` | Violation | a USE names an existing DEF of its type; Material USE of an ImageTexture caught |
| S4 | `no-viewpoint` | Warning | the Scene has a viewpoint; 3 of 7 clean fixtures lack one (a convention) |
| S5 | `route-missing-from-node`, `-to-node` | Violation | endpoints name DEFs; `Ghost` caught |
| S6 | `field-not-in-domain` | Violation | each `has<Field>` is allowed for the type by the 4.1 ontology; Box in a Transform's `geometry` caught |
| S7 | `children-not-child-node` | Violation | children are `X3DChildNode` |
| S8 | `duplicate-def` | Violation | one DEF names one node (section 4) |

`inference="none"`, pyshacl 0.40.2, `x3d_mcp fork b4efcd3`: the 7 clean fixtures give 0 Violations and 3 Warnings (S4); `HelloWorldFaulted` one result per planted fault (6 check ids: 4 V, 2 W); `HelloWorldBoxChild` 1 V; `LabScene41Faulted` 3 V. Calls took 356 to 2,956 ms.

**Valid but wrong: a part that floats or sinks.** This scene passes the XSD (4.1), `validate_semantic` (0 errors) and `x3d-core` (0 results):

```xml
<X3D profile='Interchange' version='4.1'>
  <head><meta name='identifier' content='https://example.org/learn/ShelfCase.x3d'/></head>
  <Scene>
    <Viewpoint DEF='Front' description='Front view' position='0 1.5 9'/>
    <Transform DEF='Table' translation='0 0.5 0'><Shape><Appearance><Material diffuseColor='0.5 0.35 0.2'/></Appearance><Box size='4 1 2'/></Shape></Transform>
    <Transform DEF='Mug'   translation='0 1.25 0'><Shape><Appearance><Material diffuseColor='0.9 0.9 0.9'/></Appearance><Box size='0.5 0.5 0.5'/></Shape></Transform>
    <Transform DEF='Lamp'  translation='1 2.1 0'><Shape><Appearance><Material diffuseColor='1 0.9 0.4'/></Appearance><Sphere radius='0.25'/></Shape></Transform>
    <Transform DEF='Book'  translation='-1 0.9 0'><Shape><Appearance><Material diffuseColor='0.2 0.3 0.8'/></Appearance><Box size='1 0.2 1'/></Shape></Transform>
  </Scene>
</X3D>
```

The table spans y 0 to 1. The mug (bottom 1.0) rests; the lamp's bottom is 1.85, 0.85 above; the book's bottom is 0.8, sunk 0.2. The shape `parts.ttl` finds the nearest overlapping part below and compares its top with this part's bottom:

```turtle
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix x3do: <https://www.web3d.org/specifications/X3dOntology4.1#> .
@prefix ex:   <urn:example:parts#> .
ex: sh:declare [ sh:prefix "x3do" ; sh:namespace "https://www.web3d.org/specifications/X3dOntology4.1#"^^xsd:anyURI ] ,
               [ sh:prefix "rdf"  ; sh:namespace "http://www.w3.org/1999/02/22-rdf-syntax-ns#"^^xsd:anyURI ] .
ex:PartRestsOnSupport a sh:NodeShape ; sh:targetClass x3do:Transform ; sh:severity sh:Warning ;
  sh:sparql [ a sh:SPARQLConstraint ; sh:prefixes ex: ;
    sh:message "part is {?kind}: its lowest point is {?gap} from the top of the part below it" ;
    sh:select """
SELECT $this ?gap ?kind WHERE {
  { SELECT $this ?gap WHERE {
      # part $this: centre (px py pz), half-extents (phx phy phz); omitted fields are defaults
      $this x3do:translation ?pt . ?pt rdf:first ?px ; rdf:rest/rdf:first ?py ; rdf:rest/rdf:rest/rdf:first ?pz .
      $this x3do:hasChildren/x3do:hasGeometry ?pg .
      { ?pg a x3do:Box . OPTIONAL { ?pg x3do:size ?pl . ?pl rdf:first ?pa ; rdf:rest/rdf:first ?pb ; rdf:rest/rdf:rest/rdf:first ?pc }
        BIND(COALESCE(?pa, 2) / 2 AS ?phx) BIND(COALESCE(?pb, 2) / 2 AS ?phy) BIND(COALESCE(?pc, 2) / 2 AS ?phz) }
      UNION { ?pg a x3do:Sphere . OPTIONAL { ?pg x3do:radius ?pr }
        BIND(COALESCE(?pr, 1) AS ?phx) BIND(COALESCE(?pr, 1) AS ?phy) BIND(COALESCE(?pr, 1) AS ?phz) }
      # every other part q, same pattern
      ?q x3do:translation ?qt . ?qt rdf:first ?qx ; rdf:rest/rdf:first ?qy ; rdf:rest/rdf:rest/rdf:first ?qz .
      ?q x3do:hasChildren/x3do:hasGeometry ?qg .
      { ?qg a x3do:Box . OPTIONAL { ?qg x3do:size ?ql . ?ql rdf:first ?qa ; rdf:rest/rdf:first ?qb ; rdf:rest/rdf:rest/rdf:first ?qc }
        BIND(COALESCE(?qa, 2) / 2 AS ?qhx) BIND(COALESCE(?qb, 2) / 2 AS ?qhy) BIND(COALESCE(?qc, 2) / 2 AS ?qhz) }
      UNION { ?qg a x3do:Sphere . OPTIONAL { ?qg x3do:radius ?qr }
        BIND(COALESCE(?qr, 1) AS ?qhx) BIND(COALESCE(?qr, 1) AS ?qhy) BIND(COALESCE(?qr, 1) AS ?qhz) }
      # q is below the part and overlaps it on the floor plan (axis-aligned)
      FILTER(?q != $this && ?qy < ?py && ABS(?px - ?qx) < ?phx + ?qhx && ABS(?pz - ?qz) < ?phz + ?qhz)
      BIND(?py - ?phy - (?qy + ?qhy) AS ?gap)
    } ORDER BY DESC(?qy + ?qhy) LIMIT 1 }
  FILTER(ABS(?gap) > 0.05)
  BIND(IF(?gap > 0, "floating", "sunk") AS ?kind)
}""" ] .
```

Result through `shacl_validate(shapes="none", extra_shapes_ttl=...)`: `Book: sunk, -0.2` and `Lamp: floating, 0.85`; mug and table pass. On `LabScene41` (a fixture written for converter tests, not a physical scene): `Orb: floating, 1.00`. Carry over: the nested SELECT must select `$this` (pyshacl refuses it otherwise); `COALESCE(?pa, 2)` and `COALESCE(?pr, 1)` because defaults are omitted (a Box without `size` is 2 by 2 by 2); pick the nearest support first, then judge it; Warning severity and a tolerance of 0.05 chosen by hand **[S]**. Scope: Box and Sphere under a top-level Transform, no rotation, no scale. Turn the table 90 degrees and move the mug off it: still no mug result, a false negative (D-SEM-5).

**The set-semantics trap.** SHACL counts *distinct value nodes*. Over the path `( x3do:diffuseColor [ sh:zeroOrMorePath rdf:rest ] rdf:first )` a white `( 1 1 1 )` has one value, so `sh:minCount 3` flags it. Measured (D-SEM-7): naive `minCount 3` flags `( 1 1 1 )` (wrong) and `( 1 1 )` (right); a SPARQL `COUNT` over `rdf:rest*` flags only `( 1 1 )`; the SHACL 1.2 draft's `sh:minListLength 3` flags nothing and answers `conforms=True`, because this engine version does not implement it: a false green with no warning. That is why S1b is SPARQL, and why every new constraint needs a known-bad input.

**The false-violation trap.** The same shapes with the ontology's closure applied (`shacl_validate`, 2026-11-14, D-SEM-6):

| scene | inference | results | by check_id | time |
|---|---|---|---|---|
| HelloWorld (clean) | none | 0 | none | 1.8 s |
| HelloWorld (clean) | rdfs | **2,185** (2,180 V, 5 W) | `field-not-in-domain` 2,180, `shape-no-geometry` 5 | 17.3 s |
| HelloWorldFaulted (6 faults) | none | 6 | one each | 1.4 s |
| HelloWorldFaulted | rdfs | 2,236 (2,231 V, 5 W) | `field-not-in-domain` 2,229, `colour-out-of-range` 1, `route-missing-from-node` 1, `shape-no-geometry` 5 | 15.6 s |

Of six planted faults under `rdfs`, two vanish (`use-type-mismatch`, `no-viewpoint`), one drowns among 2,229 look-alikes (the Box in a Transform) and two survive. Only the `warnings` text names the reasoner. `owlrl` hit the 20 s deadline. Keep `inference="none"`; for class membership use `rdfs:subClassOf*`.

## 8. The tool surface added in PR #17

PR #17 (merge b4efcd3, 2026-11-13) is four commits on the base `13121b6` (2026-11-03): the 4.1 ontology bundle; the converter (`scene_rdf` 649 lines, `xpath_mini` 245, DTD tables) with 10 fixtures and Saxon goldens; the five tools (758 and 378 lines, shapes 272, 30 test functions), the `semantic_audit` prompt and `instrument` on every answer; and `docs/semantic-web-tools.md`. Its tests plus `tests/test_prompts.py`: 61 passed, 1 skipped, 25 s.

**Counting the surface at b4efcd3** (D-SEM-1): **53 tools**, 5 prompts, 1 resource, 1 resource template with numpy installed; **51 tools without numpy** (the two splat tools need it). At `13121b6`: 48 tools, 4 prompts; the difference is the five tools below and the prompt.

| tool | inputs | returns | caps and guards |
|---|---|---|---|
| `scene_to_rdf` | `content`, `path` or `blob_id`; `format`; `base_iri`; `return_mode` | `graph_id`, `sha256`, `triples`, `individuals`, `warnings`, `turtle` | 300,000 triples; 120,000 inline characters; 8 graphs per session |
| `sparql_scene` | `sparql`; `graph_id` or a document; `ontology_version`; `offset`; `limit` 1 to 500 | `rows`, `total`, `next_offset`, `page_sha256` | SELECT and ASK only; 20,000 characters; 20 s forked deadline; 20,000 rows |
| `shacl_validate` | `graph_id` or a document; `shapes`; `extra_shapes_ttl`; `inference` none, rdfs, owlrl, both | `conforms`, `counts`, `by_check`, `results` of `{focus, def, node_type, path, value, severity, message, shape, check_id, fix_hint}` | shapes 256,000 characters; `owl:imports`, `sh:construct`, `sh:update` refused; shape SPARQL passes the same guard |
| `rdf_infer` | `graph_id` or a document; `profile`; `budget` 1 to 300 s | `added`, `per_node_type_counts`, `warnings` | the session graph is never changed |
| `ontology_vs_gate` | `child`; `ontology_version`; `xsd` | `counts`, `parents`, `counting_rules` | at most 120 live XSD documents per call; needs no scene |

Counting rules of `ontology_vs_gate`: **map** is `node_parents` (a `(parent, has<Field>)` whose property is under `hasChild` and whose range subsumes the child, other than bare `X3DNode`); **gate** is `where_can_place` on the X3DUOM (`acceptableNodeTypes`, no event-only fields); parents are distinct names; XSD verdicts are A accepts, R rejects, I could not tell. Caps are set by `X3D_MCP_SCENE_MAX_TRIPLES`, `X3D_MCP_TURTLE_INLINE_MAX`, `X3D_MCP_SPARQL_TIMEOUT` (shared by queries, SHACL and inference), `X3D_MCP_SPARQL_MAX_CHARS` and `X3D_MCP_ONTOLOGY_MAX_ROWS`. A `graph_id` is the first 16 hex digits of the Turtle's sha256, so an identical document gives the same id. The `instrument` block carries the commit and dirty flag, the ontology, shapes and X3DUOM hashes, the converter and the library versions; paste it into `claim_append` so a finding is re-runnable. The `semantic_audit` prompt has 7 steps (graph, ask, shapes, gate, placement, receipts, repeat) and says to keep `inference="none"`.

## 9. A worked session (scripted, not a model run)

`ShelfStranger.x3d` is the shelf with a colour of 1.5 on the table, a USE of `Wood` before its DEF, a ROUTE from `Ghost`, and the lamp and book problems. The calls are real, in the `semantic_audit` order; the choosing is the author's, so this shows tool input and output, not model skill, and no bare-versus-grounded trial exists.

```text
[1] scene_to_rdf(content=<ShelfStranger.x3d>, return_mode="summary")
    graph_id e88db1ed180ea947, 230 triples, 31 individuals, ontology 4.1, 56 ms
[2] sparql_scene(graph_id=e88db1..., ?use owl:sameAs ?def)       :Wood-USE-1 -> :Wood
[3] shacl_validate(graph_id=e88db1...)         conforms false, 2 Violation
      colour-out-of-range      :Wood       component outside [0,1], value 1.5
      route-missing-from-node  :ROUTE_2_7  fromNode 'Ghost' names no DEF in this scene
[4] shacl_validate(shapes="none", extra_shapes_ttl=<parts.ttl>)   2 Warning
      Book: part is sunk, -0.2            Lamp: part is floating, 0.85
[5] validate_x3d       valid false, 1 error: diffuseColor '0.5 1.5 0.2' fails the colour pattern
[6] validate_semantic  3 errors: use-before-def (USE='Wood'), route-missing-from-node,
                       colour-out-of-range
[7] claim_append x3    3 records (Confirmed, Confirmed, Likely), head ba02c848be0e901c
[8] claims_verify      ok true; one changed character in record 0: ok false, index 0
[9] scripted edits (colour 0.35, Spare after Table, ROUTE deleted, Lamp y 1.25, Book y 1.1):
    x3d-core + parts.ttl 0 results; validate_x3d valid; validate_semantic 0 errors
```

The matrix this session measured (each cell a real verdict; `x3d_mcp fork b4efcd3`, `X3D XSD 4.1`):

```text
 fault in the scene             XSD       x3d-core    parts.ttl   validate_semantic
 ----------------------------   -------   ---------   ---------   ---------------------
 colour component 1.5           caught    caught S1   -           caught
 USE before its DEF             -         -           -           caught use-before-def
 ROUTE from a missing node      -         caught S5   -           caught
 lamp floats, book sunk         -         -           caught      -
```

Four faults, four different sets of layers, and the last row is seen by exactly one: the argument for stacking layers and for naming which one caught what. Results carried the DEF and a `fix_hint`; `claim_append` refuses a grade outside Confirmed, Likely, Suspected.

## 10. Lookup before judge

If the X3DUOM, the XSD, the scene's own DEF table or a shape can answer a statement exactly, call the tool and quote it; do not ask a model, or a person, to judge it.

| question | exact source | call | what a model may still judge |
|---|---|---|---|
| may an ImageTexture sit under this parent | X3DUOM, then the XSD | `where_can_place`, `ontology_vs_gate` | which of the 14 gate parents the scene needs |
| USE before its DEF; colour legal | document order; XSD pattern, S1 | `validate_semantic`, `validate_x3d` | whether 0 to 255 was meant (the fix hint says so) |
| does the lamp touch the table | geometry in the graph | a contact shape (section 7) | whether a hanging lamp is intended |
| does it look right | no exact source | `render_image`, a person | everything; grade it **[S]** or **[L]** |

In practice: never state a placement from memory (map, gate and XSD disagree, so say which you ran); quote the `check_id`, node and `instrument`; record **Confirmed** only when a tool verdict shows it, **Likely** when it follows from one, **Suspected** otherwise; and where no oracle exists say so, because that is where judgment, and its grade, begins.

## 11. The ontology lab: the plan, not yet published

**Status: not yet published.** A public, interactive teaching page for this material is being designed for the `x3d.demo` site. At `x3d.demo@d10b457` (2026-11-14) it has no ontology-lab page; the one ontology page there is a separate 3D viewer of the class tree (`docs/demos/ontology-constellation/v1/index.html`). The design is a private working note, so there is no link; this chapter will link the page by relative path when it ships and will not call it existing until then. The lab must show the facts measured here.

| tier | question | sections | measured fact a station would show |
|---|---|---|---|
| T1 Facts (RDF) | what is a scene as triples | 2, 4 | Turtle beside the scene; 8 of 42 positional IRIs renamed by one insertion |
| T2 Questions (SPARQL) | what can I ask | 5 | Q2 to Q11 with row counts |
| T3 Meaning (RDFS, OWL) | what follows | 6 | one node from 2 types to 343; 0 disjointness axioms |
| T4 Accountability (SHACL, gates) | what must hold, who decides | 3, 7 | the Box funnel 12 to 10 to 5; the 2,185-result false alarm; a fault bench naming each catching layer |
| T5 Agents (MCP) | what does a model see | 8 to 10 | recorded sessions replayed with tool, arguments, result hash |

**The receipt-gathering protocol.** A lab number is quotable only with a receipt: claim, grade, command, pins, output hash, date. (1) **Pin table first:** ontology, X3DUOM and XSD sha256, `x3d_mcp` commit, X_ITE version and rig, every engine version. (2) **Build the Turtle at build time** through the faithful pipeline, never from a DOCTYPE-stripped copy, and gate the build on isomorphism with the recorded Saxon golden. (3) **Give every station an oracle:** the Python result (rdflib, pyshacl, owlrl) beside the live result with a parity flag; report engines that disagree (pyshacl ignores SHACL 1.2 list constraints; a second engine may differ **[S]**). (4) **Source and grade on every number;** the build fails on one with none. (5) **Record sessions, do not stage them:** per call the tool, arguments, latency, a sha256 of the result; say "recorded"; claim no LLM improvement without a bare-versus-grounded trial. (6) **Publish after a leak sweep and the owner's go;** Consortium example scenes keep their licence notice, and nothing says one is defective. (7) **Version, never overwrite:** a new measurement is a new dated row ([AUTHORING](AUTHORING.md)).

## Heuristics

| ID | Rule (imperative, at most 30 words) | Grade | Evidence | Instrument |
|---|---|---|---|---|
| H-SEM-1 | Write "the ontology proposes, shapes dispose, validators gate"; never let an ontology answer stand as a validity verdict. Check placement with `ontology_vs_gate` and the XSD. | C | ImageTexture: 62 map parents, 14 gate; XSD rejects 42 of 44 tested map-only pairs | `x3d_mcp fork b4efcd3`, `X3DUOM 4.1`, `X3D XSD 4.1` |
| H-SEM-2 | Run `shacl_validate` with `inference="none"`. For class membership use `rdf_infer` profile `subclass` or `rdfs:subClassOf*`. | C | clean HelloWorld 0 results, 2,185 with rdfs | `x3d_mcp fork b4efcd3`, pyshacl 0.40.2, owlrl 7.6.2 |
| H-SEM-3 | Convert with the DTD defaults of the document's version; count `has<Element>` predicates the ontology does not declare, and read a non-zero count as missing defaults. | C | HelloWorld: 0 faithful, 8 with the tables emptied | `x3d_mcp fork b4efcd3` converter tables |
| H-SEM-4 | Join on DEF names or the identifier meta, never on positional IRIs such as `Shape_2_4_2`. | C | 8 of 42 individuals renamed by one inserted node; DEF-named 5 of 5 kept | `x3d_mcp fork b4efcd3` |
| H-SEM-5 | Keep document-order rules in XML checks: USE before DEF is invisible to SPARQL and SHACL, and `children` is a set in the graph. | C | both orders give the same graph; only `validate_semantic` reports it | `x3d_mcp fork b4efcd3` |
| H-SEM-6 | Count list members with SPARQL over `rdf:rest*`, not `sh:minCount`: SHACL counts distinct values, so white `( 1 1 1 )` fails a naive arity shape. | C | naive shape flags white and `( 1 1 )`; SPARQL flags only `( 1 1 )` | pyshacl 0.40.2 |
| H-SEM-7 | Give every new constraint a known-bad input before trusting a pass; an engine may ignore a feature silently. | C | `sh:minListLength 3` on `( 1 1 )` gave `conforms=True` | pyshacl 0.40.2 |
| H-SEM-8 | After XSD, semantic and core shapes pass, add a contact shape for floating and sunk parts as a Warning with a stated tolerance and scope. | C | lamp 0.85 above, book 0.2 sunk, both passed every other layer | `x3d_mcp fork b4efcd3`, pyshacl 0.40.2 |
| H-SEM-9 | Record each verdict with `claim_append`, passing the `instrument` the tool returned; then run `claims_verify`. | C | 3 chained records; one changed character fails at index 0 | `x3d_mcp fork b4efcd3` |
| H-SEM-10 | Look up before you judge: when the XSD, X3DUOM, a DEF table or a shape answers exactly, call it; reserve judgment for what no oracle covers, and grade it. | L | 3 of 4 session faults had an exact tool; no tool saw all four | `x3d_mcp fork b4efcd3` |
| H-SEM-11 | Name, in every report, the layer that caught each problem; a fault one layer sees is why the others exist. | C | lamp and book seen by 1 of 4 layers, colour by 3 of 4 | `x3d_mcp fork b4efcd3` |

## Drills

Run each script from the root of an `x3d_mcp` checkout at `b4efcd3` with its dependencies installed, as `PYTHONPATH=src python3 <file>`. `d5.py` reads `parts.ttl` and `shelf.x3d` (section 7) from its own folder; run it there with `PYTHONPATH=<checkout>/src`. D-SEM-2, 4 and 6 are one-liners given in their Verify lines.

```python
# d3.py  strip the DOCTYPE: empty the converter's DTD tables, count undeclared has* names
import rdflib
from rdflib import RDF
from x3d_utils import scene_rdf as sr
X = "https://www.web3d.org/specifications/X3dOntology4.1#"
declared = set(rdflib.Graph().parse("src/validation/schemas/X3dOntology4.1.ttl").subjects(RDF.type, None))
text = open("tests/fixtures/scene_rdf/HelloWorld.x3d").read()
def undeclared():
    g = sr.scene_to_rdf(text).graph
    return sorted(str(p)[len(X):] for p in set(g.predicates()) if str(p).startswith(X + "has") and p not in declared)
print("faithful:", undeclared())
for table in sr.get_rules().dtd.values():
    table.clear()
print("stripped:", undeclared())
```

```python
# d5.py  the contact shape, then three variations
from x3d_utils import semantic_web as sw
shape, scene = open("parts.ttl").read(), open("shelf.x3d").read()
def run(label, xml):
    res = sw.shacl(sw.convert(xml), shapes="none", extra_shapes_ttl=shape)
    print(label, [(r["def"], r["message"].split(": its")[0]) for r in res["results"]])
run("base           ", scene)
run("Mug at y=1.35  ", scene.replace("translation='0 1.25 0'", "translation='0 1.35 0'"))
rot = scene.replace("DEF='Table' translation='0 0.5 0'", "DEF='Table' translation='0 0.5 0' rotation='0 1 0 1.5708'")
run("table turned 90", rot.replace("DEF='Mug' translation='0 1.25 0'", "DEF='Mug' translation='1.5 1.25 0'"))
```

```python
# d7.py  set semantics and a silent ignore
import pyshacl, rdflib
from rdflib import Graph
P = """@prefix sh: <http://www.w3.org/ns/shacl#> . @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix x3do: <https://www.web3d.org/specifications/X3dOntology4.1#> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> . @prefix : <urn:s#> .
: sh:declare [ sh:prefix "x3do" ; sh:namespace "https://www.web3d.org/specifications/X3dOntology4.1#"^^xsd:anyURI ] ,
             [ sh:prefix "rdf" ; sh:namespace "http://www.w3.org/1999/02/22-rdf-syntax-ns#"^^xsd:anyURI ] .
:s a sh:NodeShape ; sh:targetClass x3do:Material ; """
SHAPES = {
 "naive minCount 3": P + "sh:property [ sh:path ( x3do:diffuseColor [ sh:zeroOrMorePath rdf:rest ] rdf:first ) ; sh:minCount 3 ] .",
 "SPARQL arity": P + '''sh:sparql [ a sh:SPARQLConstraint ; sh:prefixes : ; sh:message "arity" ; sh:select """SELECT $this ?n WHERE {
   { SELECT $this (COUNT(?c) AS ?n) WHERE { $this x3do:diffuseColor ?l . ?l rdf:rest* ?k . ?k rdf:first ?c } GROUP BY $this } FILTER(?n != 3) }""" ] .''',
 "SHACL 1.2 list": P + "sh:property [ sh:path x3do:diffuseColor ; sh:minListLength 3 ] .",
}
data = Graph().parse(format="turtle", data="""@prefix x3do: <https://www.web3d.org/specifications/X3dOntology4.1#> . @prefix : <urn:t#> .
:white a x3do:Material ; x3do:diffuseColor ( 1 1 1 ) . :grey a x3do:Material ; x3do:diffuseColor ( 0.2 0.5 0.8 ) .
:short a x3do:Material ; x3do:diffuseColor ( 1 1 ) .""")
for name, shapes in SHAPES.items():
    ok, rep, _ = pyshacl.validate(data, shacl_graph=Graph().parse(format="turtle", data=shapes))
    print(f"{name:17s} conforms={ok} flagged={sorted(str(o).split('#')[1] for o in rep.objects(None, rdflib.SH.focusNode))}")
```

```python
# d8.py  what RDF forgets (USE before DEF) and the duplicate-row trap
from x3d_utils import semantic_web as sw
from validation.semantic import semantic_diagnostics
T = "<X3D profile='Interchange' version='4.1'><head/><Scene><Viewpoint position='0 0 6'/>%s</Scene></X3D>"
A = "<Shape><Appearance><Material DEF='M' diffuseColor='1 0 0'/></Appearance><Sphere/></Shape>"
B = "<Shape><Appearance><Material USE='M'/></Appearance><Box/></Shape>"
for name, doc in (("DEF then USE", T % (A + B)), ("USE then DEF", T % (B + A))):
    print(name, "| shacl conforms:", sw.shacl(sw.convert(doc))["conforms"],
          "| semantic errors:", [d.check for d in semantic_diagnostics(doc) if d.level == "error"])
sg = sw.convert(open("tests/fixtures/scene_rdf/LabScene41.x3d").read())
Q = "SELECT %s ?m WHERE { ?m a x3do:Material ; x3do:diffuseColor ?c . ?c rdf:first ?r ; rdf:rest/rdf:first ?g ; rdf:rest/rdf:rest/rdf:first ?b }"
for kw in ("", "DISTINCT"):
    print(kw or "plain   ", "rows with / without the ontology:", [sw.sparql(sg, Q % kw, include_ontology=i)["total"] for i in (True, False)])
```

### D-SEM-1 Count the tool surface
- **Level:** L1
- **Task:** At `x3d_mcp@b4efcd3` count the tools and prompts the server registers; block numpy and count again; repeat at `13121b6`.
- **Verify:** `len(asyncio.run(server.mcp.list_tools()))` and `list_prompts()` after `import server` with `PYTHONPATH=src`; set `sys.modules['numpy'] = None` before the import for the second count; `git archive 13121b6 src` for the base.
- **Answer:** 53 tools and 5 prompts; 51 and 5 without numpy (the two splat tools need it); 48 and 4 at `13121b6`. New: `scene_to_rdf`, `sparql_scene`, `shacl_validate`, `rdf_infer`, `ontology_vs_gate`, prompt `semantic_audit`.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3` and `x3d_mcp fork 13121b6`, Python 3.13.18, in-memory `list_tools`.

### D-SEM-2 Count the ontology
- **Level:** L1
- **Task:** For the bundled 4.1 ontology state triples, classes, properties with a domain, those with several, the largest domain count, the domains of `x3do:DEF`, and the `owl:disjointWith` count.
- **Verify:** load `src/validation/schemas/X3dOntology4.1.ttl` (sha256 starts 057f1ba083a6) with rdflib; `Counter(s for s, _ in g.subject_objects(RDFS.domain))` gives the domain counts per property.
- **Answer:** 18,108 triples, 364 classes, 901 properties with a domain, 294 with several, largest 355; `x3do:DEF` has 337; 0 disjointness axioms.
- **Checked:** 2026-11-14 rdflib 7.6.0, `X3dOntology4.1.ttl` as bundled at `x3d_mcp fork b4efcd3`.

### D-SEM-3 Strip the DOCTYPE
- **Level:** L2
- **Task:** Run `d3.py`. Name the predicates that appear only without DTD defaults and say why a query for `x3do:hasGeometry` returns nothing on the stripped graph. Repeat with `Altar.x3d` and `SwitchOrder.x3d`.
- **Verify:** `PYTHONPATH=src python3 d3.py`.
- **Answer:** faithful `[]`; stripped `['hasBackground', 'hasGroup', 'hasImageTexture', 'hasSphere', 'hasText', 'hasTransform', 'hasViewpoint', 'hasWorldInfo']`. With no `containerField` default the field is named after the element (`hasSphere`), so the ontology's `hasGeometry` never matches.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3` converter, ontology 4.1 (an emulation, not a Saxon run).

### D-SEM-4 One query, two ontologies
- **Level:** L2
- **Task:** On `tests/fixtures/scene_rdf/faulted/HelloWorldFaulted.x3d` run query Q8 (section 5) once with `ontology_version="4.0"` and once with `"4.1"`. Explain the two counts and say which row is the real fault.
- **Verify:** `sw.sparql(sw.convert(xml), Q8, ontology_version=v)["rows"]` with `from x3d_utils import semantic_web as sw`.
- **Answer:** 6 with 4.0, 1 with 4.1 (`Transform_2_3_2 hasGeometry Box_2_3_2_1`, the Box in a Transform's `geometry` field). The 4.0 file lists fewer `rdfs:domain` classes for `hasChildren`, `hasGeometry`, `hasCoord`, so 5 legal fields look illegal.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3`, rdflib 7.6.0.

### D-SEM-5 A part that floats
- **Level:** L3
- **Task:** Save section 7's scene and shape as `shelf.x3d` and `parts.ttl`; run `d5.py`. Predict, then check, the three runs. Then find a scene the shape passes that a person would call wrong.
- **Verify:** from that folder, `PYTHONPATH=<checkout>/src python3 d5.py`.
- **Answer:** base: `Book` sunk, `Lamp` floating, nothing for Mug and Table. Mug at y 1.35: `Mug` floating (gap 0.10) as a third result. Table turned 90 degrees, mug at x 1.5 (now off it): still only Book and Lamp, a false negative, because the shape reads translation and size and ignores rotation and scale. A fix composes rotation and scale into the extents.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3`, pyshacl 0.40.2.

### D-SEM-6 Break it with reasoning
- **Level:** L3
- **Task:** Call `sw.shacl(sg, inference=...)` with `"none"` and `"rdfs"` (set `X3D_MCP_SPARQL_TIMEOUT=120` first) on `HelloWorld.x3d` and `faulted/HelloWorldFaulted.x3d`. Which of the six faults are visible with rdfs, and what in the answer shows the reasoner is at fault?
- **Verify:** print `r["counts"]` and the `check_id` of each result; about 35 s in all.
- **Answer:** clean 0, then 2,185 (2,180 V `field-not-in-domain`, 5 W `shape-no-geometry`); faulted 6, then 2,236. Under rdfs `use-type-mismatch` and `no-viewpoint` are gone, `colour-out-of-range` and `route-missing-from-node` remain, the Box fault hides among 2,229 look-alikes. The `warnings` text names the cause.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3`, pyshacl 0.40.2, owlrl 7.6.2, 35.6 s.

### D-SEM-7 Set semantics and a silent ignore
- **Level:** L2
- **Task:** Run `d7.py`. Which colours does each of the three shapes flag, and which flag is wrong or missing?
- **Verify:** `python3 d7.py` with pyshacl 0.40.2.
- **Answer:** naive `minCount 3`: `short` (right) and `white` (wrong, its value set is `{1}`); SPARQL arity: `short` only; `sh:minListLength 3`: nothing, `conforms=True`, a false green in this engine version.
- **Checked:** 2026-11-14 pyshacl 0.40.2, rdflib 7.6.0.

### D-SEM-8 What RDF forgets
- **Level:** L2
- **Task:** Run `d8.py`. Which layer notices USE before DEF? Why do the last two lines differ?
- **Verify:** `PYTHONPATH=src python3 d8.py`.
- **Answer:** both orders give `shacl conforms: True`; only `USE then DEF` gives `['use-before-def']` from `validate_semantic`. The query returns `[4, 1]` plain and `[1, 1]` with `DISTINCT`: the joined graph repeats rows for multi-step paths.
- **Checked:** 2026-11-14 `x3d_mcp fork b4efcd3`, rdflib 7.6.0, pyshacl 0.40.2.

## Honest limits

- **The session was scripted. [C]** No LLM issued the calls in section 9; inputs and outputs are real. Nothing here measures whether a model does better with these tools.
- **The DOCTYPE strip is an emulation. [C]** I emptied the converter's DTD tables; `X3dToTurtle.xslt` was not run. That a Saxon run on a stripped copy gives the same 8 names comes from a private note **[S]**, carried, not re-checked. The converter is graph-isomorphic to 10 Saxon goldens, not text-identical.
- **Contact shape scope. [C]** Axis-aligned Box and Sphere, top-level Transform with one Shape, no rotation or scale, floor under the lowest part, tolerance chosen by hand **[S]**. It misses a rotated table (D-SEM-5) and cannot know a lamp is meant to hang.
- **One SHACL engine. [C]** All shape results are pyshacl 0.40.2; divergence elsewhere is not measured.
- **Inference on two scenes, two releases. [C]** HelloWorld read against 4.0 (it is 3.3) and LabScene41 against 4.1; counts shift with release and DEF status. `inference="owlrl"` through `shacl_validate` hit the 20 s deadline; I did not raise it.
- **Duplicate rows reproduced, not root-caused. [L]** rdflib internals not read.
- **`ontology_vs_gate` XSD numbers rest on a shipped table plus live probes. [C]** `verified-containment.json` was read, not regenerated.
- **No render, no GPU; tools called in memory, not over a transport. [C]**
- **Source conflicts.** (1) Ontology 4.1: 18,108 triples in the bundled file (re-derived) against 18,121 in the older x3d.onto data copy named in [the x3d.onto masterclass](../x3d.onto/MASTERCLASS.md); both right for their own file. (2) False violations under rdfs: 2,185 here against about 1,749 in a private note using a seven-shape variant; the code and this run support 2,185. (3) A Box in "62 slots" (bare `X3DNode` range kept) against 12 parents (`node_parents`); section 3 states the rule. (4) `containerField` defaults 235 (3.3) and 268 (4.1) here against 258 and 293 in a private note with no stated rule **[S]**. (5) Older docs saying the fork cannot query a user scene describe `13121b6`, before PR #17.
- **Not published:** the lab page (section 11). **Not covered:** CONSTRUCT and SPARQL update (the guard refuses them), ShEx, JSON-LD for X3D JSON.

## Numbers register

| ID | Quantity | Value | Grade | Instrument | Source |
|---|---|---|---|---|---|
| N-SEM-1 | tools, prompts at b4efcd3 | 53 tools, 5 prompts, 1 resource, 1 template; 51 tools without numpy | C | `x3d_mcp fork b4efcd3`, in-memory `list_tools` | x3d_mcp@b4efcd3:src/server.py |
| N-SEM-2 | tools, prompts at the PR base | 48 tools, 4 prompts | C | `x3d_mcp fork 13121b6` | x3d_mcp@13121b6:src/server.py |
| N-SEM-3 | converter vs Saxon goldens | graph-isomorphic 10 of 10; text-identical 0 of 10 | C | `x3d_mcp fork b4efcd3`, rdflib 7.6.0 | x3d_mcp@b4efcd3:tests/fixtures/scene_rdf/ |
| N-SEM-4 | ontology 4.1 as bundled | 18,108 triples, 364 classes, 337 object and 727 datatype properties, sha256 057f1ba083a6 | C | rdflib 7.6.0 | x3d_mcp@b4efcd3:src/validation/schemas/X3dOntology4.1.ttl |
| N-SEM-5 | domain pooling, 4.1 (4.0) | 901 (877) properties with a domain, 294 (296) with several, max 355 (347), `DEF` 337 (329) | C | rdflib 7.6.0 | same files |
| N-SEM-6 | axioms that could reject a node | 0 `owl:disjointWith`, 0 `owl:Restriction`, both releases | C | rdflib 7.6.0 | same files |
| N-SEM-7 | containerField defaults | 235 of 252 (3.3), 261 of 278 (4.0), 268 of 285 (4.1) elements | C | converter tables sha256 1a5f3229a7ee | x3d_mcp@b4efcd3:src/validation/schemas/X3dToTurtle-tables.json |
| N-SEM-8 | positional IRI churn | 42 to 43 individuals; 34 kept, 8 renamed; 5 of 5 DEF-named kept | C | `x3d_mcp fork b4efcd3` | one NavigationInfo inserted into HelloWorld |
| N-SEM-9 | Box: map vs gate vs XSD | map 12 parents (10 concrete); gate 10; both 9; XSD on gate pairs A 5, R 3, I 2 | C | `x3d_mcp fork b4efcd3`, `X3DUOM 4.1`, `X3D XSD 4.1` | `ontology_vs_gate("Box")` |
| N-SEM-10 | ImageTexture: map vs gate vs XSD | map 85 rows, 62 parents (55 concrete); gate 36 pairs, 14 parents; both 12; XSD gate A 31, R 1, I 4; map-only R 42, I 2 | C | same | `ontology_vs_gate("ImageTexture")` |
| N-SEM-11 | `subclass` inference | HelloWorld +81 triples, types 3 / 3 / 8, 688 ms; LabScene41 +72, 3 / 4 / 6, 46 ms | C | `x3d_mcp fork b4efcd3` `rdf_infer` | scratch run, 2026-11-14 |
| N-SEM-12 | RDFS and OWL-RL closure | RDFS +17,985 (HelloWorld, 4.9 s), +18,620 (LabScene41); OWL-RL +32,510 and +33,394, about 15 s | C | owlrl 7.6.2 | same |
| N-SEM-13 | DEF effect on type count (RDFS) | DEF'd Transform 343, DEF-less Group 51, Scene 46; Box plus Transform node under OWL-RL: 14 types, 0 `owl:Nothing` | C | owlrl 7.6.2 | same |
| N-SEM-14 | `x3d-core` shapes | 9 node shapes, 11 property shapes, 12 check ids, 5 `sh:agentInstruction`; slice 1,734 triples | C | rdflib, pyshacl 0.40.2 | x3d_mcp@b4efcd3:src/validation/schemas/shapes/x3d-core.shacl.ttl |
| N-SEM-15 | shapes on fixtures, no inference | 7 clean: 0 V, 3 W (S4); Faulted 4 V + 2 W; BoxChild 1 V; LabScene41Faulted 3 V | C | pyshacl 0.40.2 | x3d_mcp@b4efcd3:tests/fixtures/scene_rdf/ |
| N-SEM-16 | false alarm with `inference="rdfs"` | clean HelloWorld 2,185 results (2,180 V, 5 W), 17.3 s; faulted 2,236; 2 of 6 faults gone | C | pyshacl 0.40.2, owlrl 7.6.2 | D-SEM-6 |
| N-SEM-17 | contact shape on ShelfCase | Lamp floating 0.85, Book sunk -0.2; XSD valid, `validate_semantic` 0 errors, `x3d-core` 0 results; LabScene41 Orb floating 1.00 | C | `x3d_mcp fork b4efcd3`, pyshacl 0.40.2 | section 7 |
| N-SEM-18 | arity shapes on 3 colours | naive minCount flags 2 (white wrongly); SPARQL arity 1; `sh:minListLength` 0 | C | pyshacl 0.40.2 | D-SEM-7 |
| N-SEM-19 | legality query by release | 6 rows (4.0), 1 row (4.1) on HelloWorldFaulted | C | `x3d_mcp fork b4efcd3` | D-SEM-4 |
| N-SEM-20 | duplicate rows, joined graph | 4 plain, 1 with DISTINCT or without the ontology | C | rdflib 7.6.0 | D-SEM-8 |
| N-SEM-21 | tool caps | 300,000 triples; 120,000 inline characters; 20,000 query characters; 20 s; 20,000 rows; 500 per page; 8 graphs; 256,000 shape characters; 120 XSD documents | C | read, not run | x3d_mcp@b4efcd3:src/x3d_utils/{semantic_web,ontology_guard}.py |
| N-SEM-22 | session fault matrix | colour seen by 3 of 4 layers, USE-before-DEF 1, ROUTE 2, floating and sunk 1 | C | `x3d_mcp fork b4efcd3` | section 9 |
| N-SEM-23 | claim ledger tamper test | 3 records verify; one changed character fails at index 0 | C | `x3d_mcp fork b4efcd3` | `claim_append`, `claims_verify` |
| N-SEM-24 | the lab page | not yet published; no ontology-lab page at the pinned commit | C | `x3d.demo@d10b457` directory read | x3d.demo@d10b457:docs/demos/ |

## Sources and provenance

- `x3d_mcp@b4efcd3` (merge of PR #17, 2026-11-13): `src/tools/semantic_web.py`, `src/x3d_utils/{semantic_web,scene_rdf,ontology_guard,xpath_mini}.py`, `src/validation/schemas/` (both ontologies, converter tables, `shapes/x3d-core.shacl.ttl`), `src/server.py`, `docs/semantic-web-tools.md`, `tests/test_semantic_web_tools.py`, `tests/fixtures/scene_rdf/*` (7 scenes, 3 faulted, goldens, manifest). The five Consortium example scenes in the fixtures keep the licence notice in that directory. Base comparison at `13121b6`.
- `x3d.docs@f172f67`: `docs/x3d.onto/MASTERCLASS.md` (read, not re-derived). `x3d.demo@d10b457`: directory listing only.
- Re-run on 2026-11-14 in a scratch virtualenv: tool counts at two commits, ontology statistics, the converter isomorphism check, the emulated DOCTYPE strip, Q2 to Q11, `ontology_vs_gate` for four nodes, all SHACL runs, the inference profiles, the contact shape, the arity shapes, the duplicate probes, the scripted session, the guard probes and the PR's tests.
- Private working notes were pointers only. A figure from them is re-derived above or graded **[S]** with "carried from a private note, not re-checked". They are not linked.
- Siblings: [01 The tether](01-the-tether.md), [02 Loom laws](02-loom-laws.md), [03 The validator and the gates](03-validator-and-gates.md), [04 MCP for agents](04-mcp-for-agents.md), [06 X_ITE, the oracle](06-xite-the-oracle.md).
