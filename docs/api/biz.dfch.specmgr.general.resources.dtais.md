# `biz.dfch.specmgr.general.resources.dtais`

Resource: specmgr://dtais -- the DTAIS verification-method vocabulary (feat-33-vcr Task 3.3).

Static, domain-knowledge resource: what DTAIS is (Demonstration, Test,
Analysis, Inspection, Special), the five valid ``### AC-NNN (Method):
...`` method words verbatim (exactly `vcr.models.v1.body`'s closed set),
when and how to apply each, and how the chosen method interacts with a
verification case record's document-level ``## Coverage`` signal.

Served as raw packaged markdown (``text/markdown``, mirroring
``specmgr://rsk/tara``/``specmgr://rsk/risk-matrix``) rather than parsed
into structured models -- the audience is an LLM agent that needs to read
guidance, not code that needs data (``specmgr://iso25010``'s structured
parse is the precedent for machine-readable reference data; this is
prose). Registered as a flat, top-level ``specmgr://dtais`` URI (like
``specmgr://iso25010``, not ``specmgr://vcr/dtais``) since the DTAIS
vocabulary is domain-knowledge that other domains (e.g. a future `sysrs`)
may want to reference too, not owned by `vcr`'s own schema -- see
`.specmgr/feat/feat-33-vcr/README.md` REQ-006/Design Notes for the full
rationale.

## Functions

### `dtais() -> 'str'`

Return the packaged DTAIS guidance's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as every other cross-cutting ``general`` resource -- reads the
file fresh on every call.

Returns
-------
str
    The DTAIS guidance document's raw markdown source.

