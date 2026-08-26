# `biz.dfch.specmgr.rsk.resources.rsk_example`

Resource: specmgr://rsk/example (Task 3.11).

Read-only, addressable counterpart of the ``get_rsk_example`` tool, mirroring
this repo's existing tool+resource pairs (e.g. ``get_req_example`` /
``specmgr://req/example``) for a host that wants to fetch the example as
context without an explicit tool call. Deliberately does not import from
``rsk.tools`` (nor vice versa): both this resource and the ``get_rsk_example``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly, so neither sub-package depends on the other just for this
one file read.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://req/schema``'s own precedent.

## Functions

### `rsk_example() -> 'str'`

Return the packaged RSK example's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``rsk.tools.get_rsk_example.get_rsk_example`` -- this is simply
that same read exposed as an MCP resource instead of a ``@mcp.tool()``.

Returns
-------
str
    The example document's raw markdown source, including its YAML
    frontmatter block.

