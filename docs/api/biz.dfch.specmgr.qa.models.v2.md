# `biz.dfch.specmgr.qa.models.v2`

Question and Answer (QA) v2 models -- adjacent question/answer pairs, no per-question heading.

Alongside (not replacing on disk) `qa/models/v1/`, this package models a QA
body where many question/answer pairs can appear directly one after another
inside a single ISO/IEC 25010:2023 characteristic section -- see
`.specmgr/feat/feat-14-qa-v2-adjacent-qa/README.md` for the full design.

As of Phase 2, `question_answer.py`'s `QaAnswer`/`QaQuestionAnswer` and
`body.py`'s `General`/`Introduction`/`RawRequirements`/`MoreInformation`/
`ElicitationContext`/the 9 ISO/IEC 25010:2023 characteristic subclasses/`Qa`
are implemented and exported here (`_QaCategory` stays private/un-exported,
mirroring `qa/models/v1/__init__.py`'s own choice). Later phases extend this
package (and this `__init__.py`) with the version gate and a `QaFrontmatter`
re-export (imported unchanged from `qa/models/v1/`).
