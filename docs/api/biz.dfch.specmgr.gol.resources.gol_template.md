# `biz.dfch.specmgr.gol.resources.gol_template`

Resource: specmgr://gol/template (Task 3.11).

Read-only, addressable counterpart of the ``get_gol_template`` tool,
mirroring this repo's existing tool+resource pairs (e.g.
``get_gol_example`` / ``specmgr://gol/example``) for a host that wants to
fetch the template as context without an explicit tool call. Deliberately
does not import from ``gol.tools`` (nor vice versa): both this resource and
the ``get_gol_template`` tool import the shared, doc-type-agnostic
``general.tools._packaged_data`` helper directly, so neither sub-package
depends on the other just for this one file read. Mirrors
``prb.resources.prb_template`` file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://gol/schema``/``specmgr://gol/example``'s own precedent.

## Functions

### `gol_template() -> 'str'`

Return the packaged GOL template's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``gol.tools.get_gol_template.get_gol_template`` -- this is
simply that same read exposed as an MCP resource instead of a
``@mcp.tool()``. Not guaranteed to satisfy ``parse_gol``/``GolDocument``'s
field-level validators -- see ``get_gol_template``'s own docstring.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

