# `biz.dfch.specmgr.feat.resources.feat_template`

Resource: specmgr://feat/template (feat-31 Task 3.5).

Read-only, addressable counterpart of the ``get_feat_template`` tool,
mirroring this repo's existing tool+resource pairs (e.g.
``get_feat_example`` / ``specmgr://feat/example``) for a host that wants to
fetch the template as context without an explicit tool call. Deliberately
does not import from ``feat.tools`` (nor vice versa): both this resource and
the ``get_feat_template`` tool import the shared, doc-type-agnostic
``general.tools._packaged_data`` helper directly, so neither sub-package
depends on the other just for this one file read. Mirrors
``dec.resources.dec_template`` file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://feat/schema``/``specmgr://feat/example``'s own precedent.

## Functions

### `feat_template() -> 'str'`

Return the packaged FEAT template's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as ``feat.tools.get_feat_template.get_feat_template`` -- this is
simply that same read exposed as an MCP resource instead of a
``@mcp.tool()``. The committed FEAT template is guaranteed to round-trip
through ``parse_feat``: its placeholder content satisfies every
structural constraint (the DEC/RSK precedent).

Returns
-------
str
    The template document's raw markdown source, including its YAML
    frontmatter block.

