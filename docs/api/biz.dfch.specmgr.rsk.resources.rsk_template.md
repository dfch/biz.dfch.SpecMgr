# `biz.dfch.specmgr.rsk.resources.rsk_template`

Resource: specmgr://rsk/template (Task 3.11).

Read-only, addressable counterpart of the ``get_rsk_template`` tool, mirroring
this repo's existing tool+resource pairs (e.g. ``get_req_template`` /
``specmgr://req/template``) for a host that wants to fetch the template as
context without an explicit tool call. Deliberately does not import from
``rsk.tools`` (nor vice versa): both this resource and the ``get_rsk_template``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly, so neither sub-package depends on the other just for this
one file read.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://req/schema``/``specmgr://req/example``'s own precedent.

## Functions

### `rsk_template() -> 'str'`

Return the packaged RSK template's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``rsk.tools.get_rsk_template.get_rsk_template`` -- this is
simply that same read exposed as an MCP resource instead of a
``@mcp.tool()``. See ``get_rsk_template``'s own docstring.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

