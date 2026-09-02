# `biz.dfch.specmgr.sysrs.resources.sysrs_template`

Resource: specmgr://sysrs/template (Task 4.5).

Read-only, addressable counterpart of the ``get_sysrs_template`` tool,
mirroring this repo's existing tool+resource pairs (e.g.
``get_sop_example`` / ``specmgr://sop/example``) for a host that wants to
fetch the template as context without an explicit tool call. Deliberately
does not import from ``sysrs.tools`` (nor vice versa): both this resource and
the ``get_sysrs_template`` tool import the shared, doc-type-agnostic
``general.tools._packaged_data`` helper directly, so neither sub-package
depends on the other just for this one file read. Mirrors
``sop.resources.sop_template``/``vcr.resources.vcr_template`` file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://sysrs/schema``/``specmgr://sysrs/example``'s own precedent.

## Functions

### `sysrs_template() -> 'str'`

Return the packaged SYSRS template's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``sysrs.tools.get_sysrs_template.get_sysrs_template`` -- this is
simply that same read exposed as an MCP resource instead of a
``@mcp.tool()``. The committed SYSRS template is guaranteed to round-trip
through ``parse_sysrs``: its placeholder content satisfies every
structural constraint (the SOP/VCR precedent).

