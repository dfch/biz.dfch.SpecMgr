# `biz.dfch.specmgr.feat.resources.feat_example`

Resource: specmgr://feat/example (feat-31 Task 3.5).

Read-only, addressable counterpart of the ``get_feat_example`` tool, mirroring
this repo's existing tool+resource pairs (e.g. ADR's ``get_adr`` tool /
``specmgr://adr/{id}`` resource) for a host that wants to fetch the example as
context without an explicit tool call. Deliberately does not import from
``feat.tools`` (nor vice versa): both this resource and the ``get_feat_example``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly, so neither sub-package depends on the other just for this
one file read. Mirrors ``dec.resources.dec_example`` file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://feat/schema``'s own precedent.

## Functions

### `feat_example() -> 'str'`

Return the packaged FEAT example's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``feat.tools.get_feat_example.get_feat_example`` -- this is
simply that same read exposed as an MCP resource instead of a
``@mcp.tool()``.

Returns
-------
str
    The example document's raw markdown source, including its YAML
    frontmatter block.

