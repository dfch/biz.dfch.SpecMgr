# `biz.dfch.specmgr.rsk.resources.tara`

Resource: specmgr://rsk/tara (Task 3.15).

Static, domain-knowledge resource: what TARA is (Transfer, Accept, Reduce,
Avoid), the four valid ``## Strategy`` words verbatim (exactly the model's
closed set), when and how to apply each, and how the strategy interacts with
``## Mitigation`` and the frontmatter ``status`` vocabulary.

Served as raw packaged markdown (``text/markdown``, mirroring
``specmgr://iso25010``/``specmgr://tsk/example``/``/template``, per ADR
356d8781-e446-4c26-917a-eda85648ce9d's uniform convention: raw markdown
output, backed by a dedicated model that is parsed on every resource call
purely to fail fast on structural drift, with the parsed result discarded
and the original raw text returned unchanged) -- the audience is an LLM
agent that needs to read guidance, not code that needs data. The content
was drafted in Phase 1 of
``.specmgr/feat/feat-15-add-artifact-type-risk`` and packaged here in
Phase 3; the TARA words have a single source of truth
(``rsk.models.v1.body.Strategy``'s closed set).

## Functions

### `tara() -> 'str'`

Return the packaged TARA guidance's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as every other ``rsk`` resource/tool -- reads the file fresh on
every call. Also parses the text via
:func:`~biz.dfch.specmgr.rsk.models.v1.parse_tara` on every call purely
to fail fast on structural drift in production (ADR
356d8781-e446-4c26-917a-eda85648ce9d); the parsed result is discarded
and the raw text is returned unchanged.

Returns
-------
str
    The TARA guidance document's raw markdown source.

Raises
------
FileNotFoundError
    If the packaged ``rsk_tara.md`` is missing.
AssertionError
    If the packaged file's heading/list structure is malformed.
pydantic.ValidationError
    If the packaged file is structurally sound but a field value fails
    schema validation.

