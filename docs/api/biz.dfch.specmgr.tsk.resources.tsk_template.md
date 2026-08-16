# `biz.dfch.specmgr.tsk.resources.tsk_template`

Resource: specmgr://tsk/template (Task 3.11).

Read-only, addressable counterpart of the ``get_tsk_template`` tool, mirroring
this repo's existing tool+resource pairs (e.g. ``get_req_template`` /
``specmgr://req/template``) for a host that wants to fetch the template as
context without an explicit tool call. Deliberately does not import from
``tsk.tools`` (nor vice versa): both this resource and the ``get_tsk_template``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly, so neither sub-package depends on the other just for this
one file read.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://req/schema``/``specmgr://req/example``'s own precedent.

## Functions

### `tsk_template() -> 'str'`

Return the packaged TSK template's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``tsk.tools.get_tsk_template.get_tsk_template`` -- this is
simply that same read exposed as an MCP resource instead of a
``@mcp.tool()``. Not guaranteed to satisfy every field-level
validator beyond structure -- see ``get_tsk_template``'s own docstring.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

