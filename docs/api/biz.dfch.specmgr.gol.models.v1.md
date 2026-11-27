# `biz.dfch.specmgr.gol.models.v1`

Goal (GOL) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``req/models/v1`` layout: a free-function ``parse_gol`` entry point,
document-level ``GolDocument(frontmatter, body)`` wrapper, frontmatter and body
subclasses under this same package, and the ``GolSummary`` listing model for
the (Phase-3) ``list_gol`` tool. Body classes map directly to heading sections
in a goal markdown file -- see ``body.py`` for the full hierarchy.
