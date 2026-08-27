# `biz.dfch.specmgr.dec.resources.dec_template`

Resource: specmgr://dec/template (feat-21 Task 3.4).

Read-only, addressable counterpart of the ``get_dec_template`` tool,
mirroring this repo's existing tool+resource pairs (e.g.
``get_dec_example`` / ``specmgr://dec/example``) for a host that wants to
fetch the template as context without an explicit tool call. Deliberately
does not import from ``dec.tools`` (nor vice versa): both this resource and
the ``get_dec_template`` tool import the shared, doc-type-agnostic
``general.tools._packaged_data`` helper directly, so neither sub-package
depends on the other just for this one file read. Mirrors
``gol.resources.gol_template`` file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://dec/schema``/``specmgr://dec/example``'s own precedent.

## Functions

### `dec_template() -> 'str'`

Return the packaged DEC template's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``dec.tools.get_dec_template.get_dec_template`` -- this is
simply that same read exposed as an MCP resource instead of a
``@mcp.tool()``. Unlike GOL's template, the committed DEC template is
guaranteed to round-trip through ``parse_dec``: its placeholder content
satisfies every structural constraint (the RSK precedent, feat-21
Design Notes).

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

