# `biz.dfch.specmgr.req.tools.delete_req`

``@mcp.tool()`` wrapper: delete_req (Task 3.15).

Registered stub only -- reserves the ``delete_req`` name/slot in the REQ
lifecycle tool surface without committing to a deletion strategy yet
(soft-delete via ``status``, archival, hard removal from disk, or something
else -- undecided, see Task 3.9's design discussion). Always raises
``NotImplementedError`` unconditionally, without resolving ``id`` or
touching the filesystem at all, so it cannot be mistaken for a working
no-op.

## Functions

### `delete_req(id: 'str') -> 'NoReturn'`

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

