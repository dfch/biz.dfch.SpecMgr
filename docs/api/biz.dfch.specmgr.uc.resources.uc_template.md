# `biz.dfch.specmgr.uc.resources.uc_template`

Resource: specmgr://uc/template (Task 3.1.4).

Read-only, addressable counterpart of the ``get_uc_template`` tool, mirroring
this repo's existing tool+resource pairs (e.g. ``get_uc_example`` /
``specmgr://uc/example``) for a host that wants to fetch the template as
context without an explicit tool call. Deliberately does not import from
``uc.tools`` (nor vice versa): both this resource and the ``get_uc_template``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly, so neither sub-package depends on the other just for this
one file read.

The resource's URI is deliberately unversioned (no ``/v2``), matching
``specmgr://uc/schema``/``specmgr://uc/example``'s own precedent.

## Functions

### `uc_template() -> 'str'`

Return the packaged UC template's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``uc.tools.get_uc_template.get_uc_template`` -- this is simply
that same read exposed as an MCP resource instead of a ``@mcp.tool()``.
Not guaranteed to satisfy ``parse_uc``/``UcDocument``'s field-level
validators -- see ``get_uc_template``'s own docstring.

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

