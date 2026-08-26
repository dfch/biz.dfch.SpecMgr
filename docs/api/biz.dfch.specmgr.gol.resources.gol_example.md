# `biz.dfch.specmgr.gol.resources.gol_example`

Resource: specmgr://gol/example (Task 3.11).

Read-only, addressable counterpart of the ``get_gol_example`` tool, mirroring
this repo's existing tool+resource pairs (e.g. ADR's ``get_adr`` tool /
``specmgr://adr/{id}`` resource) for a host that wants to fetch the example as
context without an explicit tool call. Deliberately does not import from
``gol.tools`` (nor vice versa): both this resource and the ``get_gol_example``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly, so neither sub-package depends on the other just for this
one file read. Mirrors ``prb.resources.prb_example`` file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://gol/schema``'s own precedent.

## Functions

### `gol_example() -> 'str'`

Return the packaged GOL example's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``gol.tools.get_gol_example.get_gol_example`` -- this is simply
that same read exposed as an MCP resource instead of a ``@mcp.tool()``.

Returns
-------
str
    The example document's raw markdown source, including its YAML
    frontmatter block.

