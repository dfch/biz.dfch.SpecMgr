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
``specmgr://tsk/example``/``/template``) rather than parsed into structured
models -- the audience is an LLM agent that needs to read guidance, not code
that needs data. The documented zone thresholds are the same ones
``rsk.models.v1.assessment.level_from_product`` derives from; a test
(``tests/rsk/resources/test_risk_matrix.py``) guards the two against drift
(feature README's ACC-005).

## Functions

### `risk_matrix() -> 'str'`

Return the packaged risk-matrix guidance's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as every other ``rsk`` resource/tool -- reads the file fresh on
every call.

Returns
-------
str
    The risk-matrix guidance document's raw markdown source.

