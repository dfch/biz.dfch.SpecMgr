# `biz.dfch.specmgr.adr.resources.adr_list`

Resource: specmgr://adr/list (plan §8, §9a).

Implemented as an MCP resource rather than an ``@mcp.tool()`` (plan §9a),
matching this repo's existing ``specmgr://version`` convention.

## Functions

### `adr_list() -> 'list[AdrSummary]'`

Return a one-line summary of every ADR in the configured base directory.

A file that fails to parse (:class:`AdrParseError` or
``pydantic.ValidationError``) is silently skipped -- a single malformed
file must not break listing every other valid one (mirrors
``adr.tools._paths.find_adr_path``'s own skip-on-parse-failure rule).

Returns
-------
list[AdrSummary]
    One entry per successfully-parsed ``*.md`` file, in filename-sorted
    order. Empty if the base directory does not exist or holds no ADRs.

