# `biz.dfch.specmgr.prb.models.v1`

Problem Statement (PRB) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``tsk/models/v1``/``qa/models/v2`` layout: a free-function
``parse_prb`` entry point, document-level ``PrbDocument(frontmatter, body)``
wrapper, frontmatter and body classes all live directly in this package.
Body classes map directly to heading sections in a ``prb`` markdown file --
see ``body.py`` for the full hierarchy.
