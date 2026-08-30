# `biz.dfch.specmgr.sop.resources.sop_example`

Resource: specmgr://sop/example (feat-30 Task 3.7).

Read-only, addressable counterpart of the ``get_sop_example`` tool, mirroring
this repo's existing tool+resource pairs (e.g. DEC's ``get_dec_example`` tool /
``specmgr://dec/example`` resource) for a host that wants to fetch the example as
context without an explicit tool call. Deliberately does not import from
``sop.tools`` (nor vice versa): both this resource and the ``get_sop_example``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly, so neither sub-package depends on the other just for this
one file read. Mirrors ``dec.resources.dec_example`` file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://sop/schema``'s own precedent.

## Functions

### `sop_example() -> 'str'`

Return the packaged SOP example's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``sop.tools.get_sop_example.get_sop_example`` -- this is simply
that same read exposed as an MCP resource instead of a ``@mcp.tool()``.

Returns
-------
str
    The example document's raw markdown source, including its YAML
    frontmatter block.

