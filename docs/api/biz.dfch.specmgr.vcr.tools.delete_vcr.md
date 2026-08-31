# `biz.dfch.specmgr.vcr.tools.delete_vcr`

``@mcp.tool()`` wrapper: delete_vcr (Task 2.1).

Registered stub only -- reserves the ``delete_vcr`` name/slot in the VCR
lifecycle tool surface without committing to a deletion strategy yet
(soft-delete via ``status``, archival, hard removal from disk, or something
else -- undecided, matching every other domain's own ``delete_*`` stubs, a
shared cross-domain decision deferred to future work). Always raises
``NotImplementedError`` unconditionally, without resolving ``id`` or
touching the filesystem at all, so it cannot be mistaken for a working
no-op.

## Functions

### `delete_vcr(id: 'str') -> 'NoReturn'`

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

