# `biz.dfch.specmgr.req.resources.req_template`

Resource: specmgr://req/template (Task 3.7).

Read-only, addressable counterpart of the ``get_req_template`` tool, mirroring
this repo's existing tool+resource pairs (e.g. ``get_req_example`` /
``specmgr://req/example``) for a host that wants to fetch the template as
context without an explicit tool call. Deliberately does not import from
``req.tools`` (nor vice versa): both this resource and the ``get_req_template``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly (Task 5.3), so neither sub-package depends on the other just
for this one file read.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://req/schema``/``specmgr://req/example``'s own precedent -- see
`.specmgr/feat/feat-6-requirement-artifact/README.md`'s Decisions Made.

## Functions

### `req_template() -> 'str'`

Return the packaged REQ template's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``req.tools.get_req_template.get_req_template`` -- this is
simply that same read exposed as an MCP resource instead of a
``@mcp.tool()``. Not guaranteed to satisfy ``parse_req``/``ReqDocument``'s
field-level validators -- see ``get_req_template``'s own docstring.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

