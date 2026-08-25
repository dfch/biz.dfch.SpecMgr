# `biz.dfch.specmgr.rsk.models.v1`

Risk (RSK) models -- Pydantic schema and (in a later phase) parser powered by the generic ``models/md`` engine.

Mirrors the ``tsk/models/v1`` layout: body classes map directly to heading
sections in an ``rsk`` markdown file -- see ``body.py``/``assessment.py`` for
the full hierarchy -- and ``frontmatter.py`` narrows the generic
``MarkdownFrontmatter`` for the ``rsk`` document type.

Per `.specmgr/feat/feat-15-add-artifact-type-risk/README.md` Phase 1
("Specification"), only the frontmatter and body models exist so far. There is
no ``RskDocument``/``parse_rsk``/``RskSummary`` yet -- those are Phase 2 -- so,
unlike ``tsk.models.v1``, this package does not yet export them.
