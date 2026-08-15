# `biz.dfch.specmgr.req.resources.req_example`

Resource: specmgr://req/example (Task 3.6).

Read-only, addressable counterpart of the ``get_req_example`` tool, mirroring
this repo's existing tool+resource pairs (e.g. ADR's ``get_adr`` tool /
``specmgr://adr/{id}`` resource) for a host that wants to fetch the example as
context without an explicit tool call. Deliberately does not import from
``req.tools`` (nor vice versa): both this resource and the ``get_req_example``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly (Task 5.3), so neither sub-package depends on the other just
for this one file read.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://req/schema``'s own precedent -- see
`.specmgr/feat/feat-6-requirement-artifact/README.md`'s Decisions Made.

## Functions

### `req_example() -> 'str'`

Return the packaged REQ example's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``req.tools.get_req_example.get_req_example`` -- this is simply
that same read exposed as an MCP resource instead of a ``@mcp.tool()``.

Returns
-------
str
    The example document's raw markdown source, including its YAML
    frontmatter block.

