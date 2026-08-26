# `biz.dfch.specmgr.prb.resources.prb_template`

Resource: specmgr://prb/template (Task 3.11).

Read-only, addressable counterpart of the ``get_prb_template`` tool, mirroring
this repo's existing tool+resource pairs (e.g. ``get_tsk_template`` /
``specmgr://tsk/template``) for a host that wants to fetch the template as
context without an explicit tool call. Deliberately does not import from
``prb.tools`` (nor vice versa): both this resource and the ``get_prb_template``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly, so neither sub-package depends on the other just for this
one file read.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://req/schema``/``specmgr://req/example``'s own precedent.

## Functions

### `prb_template() -> 'str'`

Return the packaged PRB template's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``prb.tools.get_prb_template.get_prb_template`` -- this is
simply that same read exposed as an MCP resource instead of a
``@mcp.tool()``. Not guaranteed to satisfy every field-level
validator beyond structure -- see ``get_prb_template``'s own docstring.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

