# `biz.dfch.specmgr.feat.models`

Feature (FEAT) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Will mirror ``dec/models``'s layout: a versioned sub-package (``v1``, ...)
holding the frontmatter/body classes, the document wrapper and parser for
``feat`` documents, and the one-line ``FeatSummary`` for the paged
``list_feat`` tool.

**Phase 0 scaffolding only** -- ``v1`` is currently empty; see
``.specmgr/feat/feat-31-feature/README.md`` Phase 1 for the schema this
will hold (``FeatFrontmatter``, ``Feature``, ``Plan``, ``Progress``,
``Updates``/``UpdateEntry``, etc.).
