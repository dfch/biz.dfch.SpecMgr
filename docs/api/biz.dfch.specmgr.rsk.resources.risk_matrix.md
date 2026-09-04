# `biz.dfch.specmgr.rsk.resources.risk_matrix`

Resource: specmgr://rsk/risk-matrix (Task 3.15).

Static, domain-knowledge resource: the 5x5 risk matrix for ``rsk`` documents
-- the probability/impact scale anchors (1 = rare ... 5 = almost certain;
1 = negligible ... 5 = severe), the 5x5 zone table, and the product
thresholds (1-4 ``low``, 5-9 ``medium``, 10-14 ``high``, 15-25 ``very
high``) -- i.e. what 'high risk' and 'low risk' mean, plus the
initial/residual reading rule (a ``reduce`` strategy implies residual <
initial).

Served as raw packaged markdown (``text/markdown``, mirroring
``specmgr://iso25010``/``specmgr://rsk/tara``, per ADR
356d8781-e446-4c26-917a-eda85648ce9d's uniform convention: raw markdown
output, backed by a dedicated model that is parsed on every resource call
purely to fail fast on structural drift, with the parsed result discarded
and the original raw text returned unchanged) -- the audience is an LLM
agent that needs to read guidance, not code that needs data. The documented
zone thresholds are the same ones
``rsk.models.v1.assessment.level_from_product`` derives from; both the
model's own cross-check (``rsk.models.v1.risk_matrix.ProductThresholds.
_validate_thresholds``) and a resource-level test
(``tests/rsk/resources/test_risk_matrix.py``) guard the two against drift.

## Functions

### `risk_matrix() -> 'str'`

Return the packaged risk-matrix guidance's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as every other ``rsk`` resource/tool -- reads the file fresh on
every call. Also parses the text via
:func:`~biz.dfch.specmgr.rsk.models.v1.parse_risk_matrix` on every call
purely to fail fast on structural drift in production (ADR
356d8781-e446-4c26-917a-eda85648ce9d); the parsed result is discarded
and the raw text is returned unchanged.

Returns
-------
str
    The risk-matrix guidance document's raw markdown source.

Raises
------
FileNotFoundError
    If the packaged ``rsk_risk_matrix.md`` is missing.
AssertionError
    If the packaged file's heading/list structure is malformed.
pydantic.ValidationError
    If the packaged file is structurally sound but a field value fails
    schema validation.

