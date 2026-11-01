# `biz.dfch.specmgr.general.resources.reference_graph`

Resource: specmgr://reference-graph (feat-207-reference-graph, Phase 100).

Static, cross-cutting domain-knowledge resource: the frozen reference-graph
rulebook — the deterministic PlantUML component-diagram layout for the
cross-reference network (the emission layout + palette, the alias/label/
truncation rules, the title override + defaults, the FEAT-exclusion rule,
the bare-`feat-NNN` source-id rejection with the `list_feat` discovery
pointer, the SCC cycle rule + red-arrow syntax, the graph-construction
semantics, the CLI file layout) plus the pointer at the UC rulebook §3–§6
for the validation chain reused as-is.

Served as raw packaged markdown (``text/markdown``, mirroring
``specmgr://dtais``/``specmgr://rasci``'s raw-passthrough style and the
UC rulebook ``specmgr://uc/plantuml``'s own shape: the audience is an LLM
agent — and the Phase 110+ implementer — that needs to read a frozen spec,
not code that needs data). Unlike ``dtais``/``rasci`` there is no dedicated
model to parse the rulebook with, so there is no per-call drift-guard
parse — the sanity pins in
``tests/general/resources/test_reference_graph.py`` play that role instead
(the ``tests/uc/resources/test_uc_plantuml.py`` precedent). The content is
the Phase 100 freeze of the feature plan's Design Notes §2–§5 (+ the §7
source-id rule); a change to the rulebook is a spec change, not a content
edit.

Registered as a flat, top-level ``specmgr://reference-graph`` URI (like
``specmgr://dtais``/``specmgr://iso25010``, not under any domain) since the
reference network spans every document domain — it is not owned by any
single domain's own schema.

## Functions

### `reference_graph() -> 'str'`

Return the packaged reference-graph rulebook's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as every other cross-cutting ``general`` resource — reads the
file fresh on every call.

Returns
-------
str
    The rulebook's raw markdown source.

Raises
------
FileNotFoundError
    If the packaged ``general_reference_graph.md`` is missing.

