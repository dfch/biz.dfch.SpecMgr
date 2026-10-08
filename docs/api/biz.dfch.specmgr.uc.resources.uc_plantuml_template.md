# `biz.dfch.specmgr.uc.resources.uc_plantuml_template`

Resource: specmgr://uc/plantuml-template (feat-185-uc-diagrams, Phase 120).

Static packaged-data resource: the PlantUML sequence-skeleton template
(placeholder participants + mapping comments, rulebook §2.9) as raw
PlantUML source. The resource-side half of the ``get_uc_plantuml_template``
tool's packaged-data pair (REQ-008) -- both read the same file
(``uc/data/uc_plantuml_template.md``) fresh on every call.

Served as ``text/plain`` -- frozen in the plan's §11 resource mime-type
contract: the file is PlantUML source, **not** markdown and **not** a
specmgr document (no frontmatter, not ``validate``-able) -- closer to the
``specmgr://rsk/tara`` domain-knowledge shape than to a document template
(``specmgr://uc/template``, which is a specmgr document and
``text/markdown``). The trivial usecase-diagram shape is frozen in the
rulebook §2.6 instead (no template needed for it).

The resource's URI is deliberately unversioned (no ``/v2``), matching
``specmgr://uc/schema``'s own precedent.

## Functions

### `uc_plantuml_template() -> 'str'`

Return the packaged sequence-skeleton template's full PlantUML text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as every other ``uc`` resource/tool -- reads the file fresh on
every call.

Returns
-------
str
    The template's raw PlantUML source.

Raises
------
FileNotFoundError
    If the packaged ``uc_plantuml_template.md`` is missing.

