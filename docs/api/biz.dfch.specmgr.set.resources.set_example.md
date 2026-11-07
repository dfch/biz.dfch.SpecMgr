# `biz.dfch.specmgr.set.resources.set_example`

Resource: specmgr://set/example (feat-173-req-iso29148-level-set Phase 180).

Read-only, addressable counterpart of the ``get_set_example`` tool, mirroring
this repo's existing tool+resource pairs (e.g. ADR's ``get_adr`` tool /
``specmgr://adr/{id}`` resource) for a host that wants to fetch the example as
context without an explicit tool call. Deliberately does not import from
``set.tools`` (nor vice versa): both this resource and the
``get_set_example`` tool import the shared, doc-type-agnostic
``general.tools._packaged_data`` helper directly, so neither sub-package
depends on the other just for this one file read. Mirrors
``vcr.resources.vcr_example``/``sysrs.resources.sysrs_example``
file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://set/template``'s own precedent.

## Functions

### `set_example() -> 'str'`

Return the packaged set example's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``set.tools.get_set_example.get_set_example`` -- this is
simply that same read exposed as an MCP resource instead of a
``@mcp.tool()``.

Returns
-------
str
    The example document's raw markdown source, including its YAML
    frontmatter block.

