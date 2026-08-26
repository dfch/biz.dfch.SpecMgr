# `biz.dfch.specmgr.rsk.resources.tara`

Resource: specmgr://rsk/tara (Task 3.15).

Static, domain-knowledge resource: what TARA is (Transfer, Accept, Reduce,
Avoid), the four valid ``## Strategy`` words verbatim (exactly the model's
closed set), when and how to apply each, and how the strategy interacts with
``## Mitigation`` and the frontmatter ``status`` vocabulary.

Served as raw packaged markdown (``text/markdown``, mirroring
``specmgr://tsk/example``/``/template``) rather than parsed into structured
models -- the audience is an LLM agent that needs to read guidance, not code
that needs data (``specmgr://iso25010``'s structured parse is the precedent
for machine-readable reference data; these are prose). The content was
drafted in Phase 1 of ``.specmgr/feat/feat-15-add-artifact-type-risk`` and
packaged here in Phase 3; the TARA words have a single source of truth
(``rsk.models.v1.body.Strategy``'s closed set).

## Functions

### `tara() -> 'str'`

Return the packaged TARA guidance's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as every other ``rsk`` resource/tool -- reads the file fresh on
every call.

Returns
-------
str
    The TARA guidance document's raw markdown source.

