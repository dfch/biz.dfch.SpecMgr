# `biz.dfch.specmgr.sop.tools.delete_sop`

``@mcp.tool()`` wrapper: delete_sop (Task 2.2).

Registered stub only -- reserves the ``delete_sop`` name/slot in the SOP
lifecycle tool surface without committing to a deletion strategy yet
(soft-delete via ``status``, archival, hard removal from disk, or something
else -- undecided, matching the other domains' own ``delete_*`` stubs, a
shared cross-domain decision deferred to future work). Always raises
``NotImplementedError`` unconditionally, without resolving ``id`` or
touching the filesystem at all, so it cannot be mistaken for a working
no-op.

## Functions

### `delete_sop(id: 'str') -> 'NoReturn'`

Always raise ``NotImplementedError``; deletion is not yet implemented.

Parameters
----------
id:
    The document's specmgr-assigned identifier. Unused -- accepted only
    to fix this tool's future signature; never resolved or validated.

Raises
------
NotImplementedError
    Always.

