# `biz.dfch.specmgr.uc.resources.uc_example`

Resource: specmgr://uc/example (Task 3.1.4).

Read-only, addressable counterpart of the ``get_uc_example`` tool, mirroring
this repo's existing tool+resource pairs (e.g. ``req.tools.get_req_example``
/ ``specmgr://req/example``) for a host that wants to fetch the example as
context without an explicit tool call. Deliberately does not import from
``uc.tools`` (nor vice versa): both this resource and the ``get_uc_example``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly, so neither sub-package depends on the other just for this
one file read.

The resource's URI is deliberately unversioned (no ``/v2``), matching
``specmgr://uc/schema``'s own precedent.

## Functions

### `uc_example() -> 'str'`

Return the packaged UC example's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``uc.tools.get_uc_example.get_uc_example`` -- this is simply
that same read exposed as an MCP resource instead of a ``@mcp.tool()``.

Returns
-------
str
    The example document's raw markdown source, including its YAML
    frontmatter block.

