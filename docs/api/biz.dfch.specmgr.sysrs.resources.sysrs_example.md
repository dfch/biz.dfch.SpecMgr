# `biz.dfch.specmgr.sysrs.resources.sysrs_example`

Resource: specmgr://sysrs/example (Task 4.5).

Read-only, addressable counterpart of the ``get_sysrs_example`` tool, mirroring
this repo's existing tool+resource pairs (e.g. SOP's ``get_sop_example`` tool /
``specmgr://sop/example`` resource) for a host that wants to fetch the example as
context without an explicit tool call. Deliberately does not import from
``sysrs.tools`` (nor vice versa): both this resource and the ``get_sysrs_example``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly, so neither sub-package depends on the other just for this
one file read. Mirrors ``sop.resources.sop_example``/``vcr.resources.vcr_example``
file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://sysrs/schema``'s own precedent.

## Functions

### `sysrs_example() -> 'str'`

Return the packaged SYSRS example's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``sysrs.tools.get_sysrs_example.get_sysrs_example`` -- this is
simply that same read exposed as an MCP resource instead of a
``@mcp.tool()``.

Returns
-------
str
    The example document's raw markdown source, including its YAML
    frontmatter block.

