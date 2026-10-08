# `biz.dfch.specmgr.uc.tools.get_uc_plantuml_example`

``@mcp.tool()`` wrapper: get_uc_plantuml_example (feat-185-uc-diagrams, Phase 120).

Returns the packaged, complete, fully attributed PlantUML sequence diagram
for the "Buy Goods" example UC as raw PlantUML source, verbatim -- the
tool-side half of the ``specmgr://uc/plantuml-example`` packaged-data pair
(REQ-008). It is ``render_uc_sequence_skeleton`` of the packaged example
UC with each ``UNATTRIBUTED`` marker replaced by its reasoned
attribution (the ``generate_uc_sequence_diagram`` prompt flow's model).
The file is PlantUML source, not markdown and not a specmgr document (no
frontmatter, not ``validate``-able).

## Functions

### `get_uc_plantuml_example() -> 'str'`

Return the packaged sequence-diagram example's full PlantUML text, verbatim.

The example file is shipped as package data (declared in
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
    The example's raw PlantUML source.

