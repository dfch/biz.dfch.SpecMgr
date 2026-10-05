# `biz.dfch.specmgr.uc.resources.uc_plantuml_example`

Resource: specmgr://uc/plantuml-example (feat-185-uc-diagrams, Phase 120).

Static packaged-data resource: the complete, fully attributed PlantUML
sequence diagram for the packaged "Buy Goods" example UC as raw PlantUML
source. The resource-side half of the ``get_uc_plantuml_example``
tool's packaged-data pair (REQ-008) -- both read the same file
(``uc/data/uc_plantuml_example.md``) fresh on every call.

Served as ``text/plain`` -- frozen in the plan's §11 resource mime-type
contract: the file is PlantUML source, **not** markdown and **not** a
specmgr document (no frontmatter, not ``validate``-able) -- closer to the
``specmgr://rsk/tara`` domain-knowledge shape than to a document template
(``specmgr://uc/template``, which is a specmgr document and
``text/markdown``). The example is ``render_uc_sequence_skeleton`` of the
packaged example UC with each ``UNATTRIBUTED`` marker replaced by its
reasoned attribution (the ``generate_uc_sequence_diagram`` prompt flow's
model; the pinning test in ``tests/uc/models/v2/test_renderer.py`` keeps
it from drifting from the renderer).

The resource's URI is deliberately unversioned (no ``/v2``), matching
``specmgr://uc/schema``'s own precedent.

## Functions

### `uc_plantuml_example() -> 'str'`

Return the packaged sequence-diagram example's full PlantUML text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as every other ``uc`` resource/tool -- reads the file fresh on
every call.

Returns
-------
str
    The example's raw PlantUML source.

Raises
------
FileNotFoundError
    If the packaged ``uc_plantuml_example.md`` is missing.

