# `biz.dfch.specmgr.sop.resources.sop_template`

Resource: specmgr://sop/template (feat-30 Task 3.7).

Read-only, addressable counterpart of the ``get_sop_template`` tool,
mirroring this repo's existing tool+resource pairs (e.g.
``get_sop_example`` / ``specmgr://sop/example``) for a host that wants to
fetch the template as context without an explicit tool call. Deliberately
does not import from ``sop.tools`` (nor vice versa): both this resource and
the ``get_sop_template`` tool import the shared, doc-type-agnostic
``general.tools._packaged_data`` helper directly, so neither sub-package
depends on the other just for this one file read. Mirrors
``dec.resources.dec_template`` file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://sop/schema``/``specmgr://sop/example``'s own precedent.

## Functions

### `sop_template() -> 'str'`

Return the packaged SOP template's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``sop.tools.get_sop_template.get_sop_template`` -- this is
simply that same read exposed as an MCP resource instead of a
``@mcp.tool()``. The committed SOP template is guaranteed to round-trip
through ``parse_sop``: its placeholder content satisfies every
structural constraint (the RSK/DEC precedent).

