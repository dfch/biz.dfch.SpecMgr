# `biz.dfch.specmgr.txt.resources.txt_template`

Resource: specmgr://txt/template (feat-229-txt Phase 120).

Read-only, addressable counterpart of the ``get_txt_template`` tool,
mirroring this repo's existing tool+resource pairs (e.g.
``get_txt_example`` / ``specmgr://txt/example``) for a host that wants to
fetch the template as context without an explicit tool call. Deliberately
does not import from ``txt.tools`` (nor vice versa): both this resource and
the ``get_txt_template`` tool import the shared, doc-type-agnostic
``general.tools._packaged_data`` helper directly, so neither sub-package
depends on the other just for this one file read. Mirrors
``vcr.resources.vcr_template``/``sysrs.resources.sysrs_template``
file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://txt/template``/``specmgr://txt/example``'s own precedent.

## Functions

### `txt_template() -> 'str'`

Return the packaged TXT template's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``txt.tools.get_txt_template.get_txt_template`` -- this is
simply that same read exposed as an MCP resource instead of a
``@mcp.tool()``. The committed TXT template is guaranteed to round-trip
through ``parse_txt``: its placeholder content satisfies every
structural constraint (the DEC/RSK precedent).

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

