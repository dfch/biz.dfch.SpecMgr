# `biz.dfch.specmgr.feat.tools.delete_feat`

``@mcp.tool()`` wrapper: delete_feat (Task 2.3).

Registered stub only -- reserves the ``delete_feat`` name/slot in the FEAT
lifecycle tool surface without committing to a deletion strategy yet
(soft-delete via ``status``, archival, hard removal of the whole
``<id>/`` folder from disk, or something else -- undecided, matching every
other domain's own ``delete_*`` stub, a shared cross-domain decision
deferred to future work). Always raises ``NotImplementedError``
unconditionally, without resolving ``id`` or touching the filesystem at
all, so it cannot be mistaken for a working no-op.

## Functions

### `delete_feat(id: 'str') -> 'NoReturn'`

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

