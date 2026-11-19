# `biz.dfch.specmgr.set.resources.set_template`

Resource: specmgr://set/template (feat-173-req-iso29148-level-set Phase 180).

Read-only, addressable counterpart of the ``get_set_template`` tool,
mirroring this repo's existing tool+resource pairs (e.g.
``get_set_example`` / ``specmgr://set/example``) for a host that wants to
fetch the template as context without an explicit tool call. Deliberately
does not import from ``set.tools`` (nor vice versa): both this resource and
the ``get_set_template`` tool import the shared, doc-type-agnostic
``general.tools._packaged_data`` helper directly, so neither sub-package
depends on the other just for this one file read. Mirrors
``vcr.resources.vcr_template``/``sysrs.resources.sysrs_template``
file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://set/template``/``specmgr://set/example``'s own precedent.

## Functions

### `set_template() -> 'str'`

Return the packaged set template's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``set.tools.get_set_template.get_set_template`` -- this is
simply that same read exposed as an MCP resource instead of a
``@mcp.tool()``. The committed set template is guaranteed to round-trip
through ``parse_set``: its placeholder content satisfies every
structural constraint (the DEC/RSK precedent).

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

