# `biz.dfch.specmgr.uc.resources.uc_plantuml`

Resource: specmgr://uc/plantuml (feat-185-uc-diagrams, Phase 100).

Static, domain-knowledge resource: the frozen UC → PlantUML mapping rulebook. It
specifies, verbatim, the deterministic mapping from a parsed v2 ``UseCase`` to the
per-UC usecase diagram, the package usecase diagram, and the sequence skeleton
(including the full UNATTRIBUTED marker grammar), plus the validation chain's
strict source-selection semantics, the local jar/bin invocation contract, the URL
protocol's frozen classification matrix, the two-mode structure checker contract,
and the user-owned platform-adapter reference snippets.

Served as raw packaged markdown (``text/markdown`` — frozen in the plan's §11
resource mime-type contract; the rulebook *is* markdown, unlike the later
``text/plain`` PlantUML-source template/example resources), mirroring the
domain-knowledge shape of ``specmgr://rsk/tara`` / ``specmgr://dtais``: the
audience is an LLM agent (and the Phase 110+ implementer) that needs to read a
frozen spec, not code that needs data. Unlike ``rsk_tara`` there is no
dedicated model to parse the rulebook with, so there is no per-call drift-guard
parse — the sanity pins in ``tests/uc/resources/test_uc_plantuml.py`` play that
role instead. The content is the Phase 100 freeze of the feature plan's §2–§6
and §8; a change to the rulebook is a spec change, not a content edit.

The resource's URI is deliberately unversioned (no ``/v2``), matching
``specmgr://uc/schema``'s own precedent.

## Functions

### `uc_plantuml() -> 'str'`

Return the packaged UC → PlantUML rulebook's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as every other ``uc`` resource/tool — reads the file fresh on
every call.

Returns
-------
str
    The rulebook's raw markdown source.

Raises
------
FileNotFoundError
    If the packaged ``uc_plantuml.md`` is missing.

