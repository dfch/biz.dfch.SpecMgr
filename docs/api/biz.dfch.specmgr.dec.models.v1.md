# `biz.dfch.specmgr.dec.models.v1`

Decision (DEC) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``gol/models/v1`` layout: a free-function ``parse_dec`` entry
point, document-level ``DecDocument(frontmatter, body)`` wrapper,
frontmatter and body subclasses under this same package, and the
``DecSummary`` listing model for the (Phase-2) ``list_dec`` tool. Body
classes map directly to heading sections in a decision markdown file --
see ``body.py`` for the full hierarchy.
