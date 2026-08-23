# `biz.dfch.specmgr.qa.models.v2`

Question and Answer (QA) v2 models -- adjacent question/answer pairs, no per-question heading.

This package models a QA body where many question/answer pairs can appear
directly one after another inside a single ISO/IEC 25010:2023 characteristic
section -- see `.specmgr/feat/feat-14-qa-v2-adjacent-qa/README.md` for the
full design. As of feat-14 Phase 8, this is QA's only schema: the earlier
`qa/models/v1/` package (one `### {heading}` H3 per question/answer pair) has
been removed entirely now that every QA MCP tool/resource/prompt is
repointed at v2.

`question_answer.py`'s `QaAnswer`/`QaQuestionAnswer`, `body.py`'s
`General`/`Introduction`/`RawRequirements`/`MoreInformation`/
`ElicitationContext`/the 9 ISO/IEC 25010:2023 characteristic subclasses/`Qa`,
`frontmatter.py`'s `QaFrontmatter`, `summary.py`'s `QaSummary`,
`document.py`'s `QaDocument` (pairing `Qa` with `QaFrontmatter`), and
`parser.py`'s `parse_qa` -- the shared QA parsing entry point -- are all
implemented and exported here (`_QaCategory` stays private/un-exported).

**No `version`-based dispatch/gate exists** (REQ-004/ACC-004 revised
2026-08-23, see the feature README's Decisions Made): `QaFrontmatter.version`
was found to encode the shared `models.md` parsing engine's own schema
version (hardcoded to major 1), not a per-document-type body-schema version,
so no major-2 dispatch is possible. `parse_qa` mirrors
`uc/models/v2/parser.py::parse_uc`'s unconditional-v2-parsing shape exactly
instead -- a v1-shaped document simply fails naturally with whatever
structural error `Qa.from_text`/`QaFrontmatter.model_validate` raises on its
own.
