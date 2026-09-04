# `biz.dfch.specmgr.general.resources.iso25010`

Resource: specmgr://iso25010 (Task 0.8.3; feat-92-resources Phase 1).

Reads the packaged ISO/IEC 25010:2023 product quality model markdown
(``general/data/general_iso25010.md``, via
``general.tools._packaged_data.read_packaged_text``) and returns it
verbatim as raw markdown, mirroring ``specmgr://dtais``/``specmgr://rsk/tara``'s
raw-passthrough style. Unlike its plain-passthrough siblings, it still
parses the text into a :class:`~biz.dfch.specmgr.models.Iso25010` on every
call purely to fail fast on structural drift (ADR
356d8781-e446-4c26-917a-eda85648ce9d): the parsed result is discarded and
the original raw text is what's returned.

## Functions

### `iso25010() -> 'str'`

Return the packaged ISO/IEC 25010:2023 guidance's full markdown text, verbatim.

Reads the packaged copy (``general/data/general_iso25010.md``) fresh on
every call (no in-memory cache, consistent with every other resource/tool
in this codebase) but never regenerates it -- this is static reference
data, not a user-edited/versioned document type. Also parses the text
via :func:`~biz.dfch.specmgr.models.parse_iso25010` on every call purely
to fail fast on structural drift in production; the parsed result is
discarded and the raw text is returned unchanged.

Returns
-------
str
    The ISO/IEC 25010:2023 product quality model document's raw
    markdown source.

Raises
------
FileNotFoundError
    If the packaged ``general_iso25010.md`` is missing.
AssertionError
    If the packaged file's heading/list structure is malformed.
pydantic.ValidationError
    If the packaged file is structurally sound but a field value fails
    schema validation.

