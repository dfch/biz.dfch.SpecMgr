# `biz.dfch.specmgr.uc.tools.get_uc_plantuml_template`

``@mcp.tool()`` wrapper: get_uc_plantuml_template (feat-185-uc-diagrams, Phase 120).

Returns the packaged PlantUML sequence-skeleton template (rulebook
``specmgr://uc/plantuml`` §2.9: placeholder participants + mapping
comments) as raw PlantUML source, verbatim -- the tool-side half of the
``specmgr://uc/plantuml-template`` packaged-data pair (REQ-008). The file
is PlantUML source, not markdown and not a specmgr document (no
frontmatter, not ``validate``-able); the trivial usecase-diagram shape is
frozen in the rulebook §2.6 instead (no template needed for it).

## Functions

### `get_uc_plantuml_template() -> 'str'`

Return the packaged sequence-skeleton template's full PlantUML text, verbatim.

The template file is shipped as package data (declared in
``pyproject.toml``'s ``[tool.setuptools.package-data]``), so its
presence is a build-time guarantee, not something that can be missing
at runtime in a correctly installed package. Reads the file fresh on
every call (no in-memory cache). A missing or corrupted packaged file
is not caught or wrapped here -- it propagates as a hard
:class:`FileNotFoundError`, the same let-it-raise convention every
other tool/resource in this codebase follows.

Returns
-------
str
    The template's raw PlantUML source.

