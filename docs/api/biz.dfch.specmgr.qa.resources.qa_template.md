# `biz.dfch.specmgr.qa.resources.qa_template`

Resource: specmgr://qa/template (Phase 4, Task 4.2).

Read-only, addressable counterpart of the ``get_qa_template`` tool, mirroring
this repo's existing tool+resource pairs (e.g. ``get_req_template`` /
``specmgr://req/template``) for a host that wants to fetch the template as
context without an explicit tool call. Deliberately does not import from
``qa.tools`` (nor vice versa): both this resource and the ``get_qa_template``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly, so neither sub-package depends on the other just for this
one file read.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://qa/schema``/``specmgr://qa/example``'s own precedent.

## Functions

### `qa_template() -> 'str'`

Return the packaged QA template's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``qa.tools.get_qa_template.get_qa_template`` -- this is
simply that same read exposed as an MCP resource instead of a
``@mcp.tool()``. Not guaranteed to satisfy ``parse_qa``/``QaDocument``'s
field-level validators -- see ``get_qa_template``'s own docstring.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

