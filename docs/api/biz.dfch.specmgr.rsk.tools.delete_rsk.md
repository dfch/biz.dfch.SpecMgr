# `biz.dfch.specmgr.rsk.tools.delete_rsk`

``@mcp.tool()`` wrapper: delete_rsk (Task 3.6).

Registered stub only -- reserves the ``delete_rsk`` name/slot in the RSK
lifecycle tool surface without committing to a deletion strategy yet
(soft-delete via ``status``, archival, hard removal from disk, or something
else -- undecided, mirroring ``tsk.tools.delete_tsk``'s own open question).
Always raises ``NotImplementedError`` unconditionally, without resolving
``id`` or touching the filesystem at all, so it cannot be mistaken for a
working no-op.

## Functions

### `delete_rsk(id: 'str') -> 'NoReturn'`

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

