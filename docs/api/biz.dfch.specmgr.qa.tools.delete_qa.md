# `biz.dfch.specmgr.qa.tools.delete_qa`

``@mcp.tool()`` wrapper: delete_qa (Phase 4, Task 4.1).

Registered stub only -- reserves the ``delete_qa`` name/slot in the QA
lifecycle tool surface without committing to a deletion strategy yet
(soft-delete via ``status``, archival, hard removal from disk, or something
else -- undecided, mirroring ``req.tools.delete_req``'s own open design
question). Always raises ``NotImplementedError`` unconditionally, without
resolving ``id`` or touching the filesystem at all, so it cannot be
mistaken for a working no-op.

## Functions

### `delete_qa(id: 'str') -> 'NoReturn'`

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

