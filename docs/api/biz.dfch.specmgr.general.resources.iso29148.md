# `biz.dfch.specmgr.general.resources.iso29148`

Resource: specmgr://iso29148 -- the ISO/IEC/IEEE 29148:2018 requirement-specifications guidance
(feat-173-req-iso29148-level-set Phase 130, REQ-003).

Static, domain-knowledge resource: what the four ISO/IEC/IEEE 29148:2018
requirement specifications are (the §3.2 abbreviations `BRS`, `StRS`,
`SyRS`, `SRS`), the standard's §5.4 mapping sentence (verbatim), the
§6.2-6.4 processes, the §8.2-8.5 example outlines, the §9.3-9.6
normative content clauses, how the four kinds map onto specmgr document
types, where a requirement's obligation lives (the statement's phrasing,
EARS), and the §5.2.6 "Characteristics of a set of requirements" list.

Served as raw packaged markdown (``text/markdown``, mirroring
``specmgr://ears``/``specmgr://iso25010``/``specmgr://dtais``, per DEC
356d8781-e446-4c26-917a-eda85648ce9d's uniform convention: raw markdown
output, backed by a dedicated model that is parsed on every resource call
purely to fail fast on structural drift, with the parsed result discarded
and the original raw text returned unchanged) -- the audience is an LLM
agent that needs to read guidance, not code that needs data. Registered
as a flat, top-level ``specmgr://iso29148`` URI (like ``specmgr://ears``/
``specmgr://dtais``/``specmgr://iso25010``, not e.g. ``specmgr://req/
iso29148``) since the ISO 29148 kinds are cross-cutting domain knowledge
-- referenced by ``req``'s ``## Level`` field but not owned by the
``req`` schema -- mirroring `general/resources/ears.py`'s cross-domain
placement rationale.

## Functions

### `iso29148() -> 'str'`

Return the packaged ISO/IEC/IEEE 29148:2018 guidance's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as every other cross-cutting ``general`` resource -- reads the
file fresh on every call. Also parses the text via
:func:`~biz.dfch.specmgr.general.models.parse_iso29148` on every call
purely to fail fast on structural drift in production (DEC
356d8781-e446-4c26-917a-eda85648ce9d); the parsed result is discarded
and the raw text is returned unchanged.

Returns
-------
str
    The ISO 29148 guidance document's raw markdown source.

Raises
------
FileNotFoundError
    If the packaged ``general_iso29148.md`` is missing.
AssertionError
    If the packaged file's heading/list structure is malformed.
pydantic.ValidationError
    If the packaged file is structurally sound but a field value fails
    schema validation.

