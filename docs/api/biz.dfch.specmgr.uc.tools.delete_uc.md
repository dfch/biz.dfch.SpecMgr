# `biz.dfch.specmgr.uc.tools.delete_uc`

``@mcp.tool()`` wrapper: delete_uc (Task 3.1.5).

Registered stub only -- reserves the ``delete_uc`` name/slot in the UC
lifecycle tool surface without committing to a deletion strategy yet
(soft-delete via ``status``, archival, hard removal from disk, or something
else -- undecided). Always raises ``NotImplementedError`` unconditionally,
without resolving ``id`` or touching the filesystem at all, so it cannot be
mistaken for a working no-op. Mirrors ``req.tools.delete_req``.

## Functions

### `delete_uc(id: 'str') -> 'NoReturn'`

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

