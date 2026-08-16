# `biz.dfch.specmgr.general.resources.iso25010`

Resource: specmgr://iso25010 (Task 0.8.3).

Reads the packaged ISO/IEC 25010:2023 product quality model markdown
(``general/data/general_iso25010.md``, via
``general.tools._packaged_data.read_packaged_text``) and parses it into a
structured :class:`~biz.dfch.specmgr.models.Iso25010`, mirroring
``req/resources/req_schema.py``'s packaged-data-read style.

## Functions

### `iso25010() -> 'Iso25010'`

Return the parsed ISO/IEC 25010:2023 product quality model.

Reads the packaged copy (``general/data/general_iso25010.md``) fresh on
every call (no in-memory cache, consistent with every other resource/tool
in this codebase) but never regenerates it -- this is static reference
data, not a user-edited/versioned document type.

Returns
-------
Iso25010
    The nine main characteristics (each with its sub-characteristics),
    the ordered list of characteristic names, and the copyright notice.

Raises
------
FileNotFoundError
    If the packaged ``general_iso25010.md`` is missing.
AssertionError
    If the packaged file's heading/list structure is malformed.

