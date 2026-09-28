# `biz.dfch.specmgr.general.resources.version`

Resource: specmgr://version — MCP server package version number.

## Functions

### `version_info() -> 'VersionInfo'`

Return the installed version numbers of the packages that back this MCP server.

``specmgr``: the ``biz-dfch-specmgr`` package version. ``fastembed`` (feat-134
Phase 7, REQ-014): the installed ``fastembed`` package version (the
``similarity`` extra's embedding backend), or ``None`` when the extra is
not installed (``PackageNotFoundError``) -- read via ``importlib.metadata``,
never by importing ``fastembed`` itself.

Returns
-------
VersionInfo
    The version of this ``biz-dfch-specmgr`` package, plus the installed
    ``fastembed`` version (or ``None``).

