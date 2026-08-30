# `biz.dfch.specmgr.sop.models.v1`

Standard Operating Procedure (SOP) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``dec/models/v1`` layout: a free-function ``parse_sop`` entry
point, document-level ``SopDocument(frontmatter, body)`` wrapper,
frontmatter and body subclasses under this same package, and the
``SopSummary`` listing model for the (Phase-2) ``list_sop`` tool. Body
classes map directly to heading sections in an SOP markdown file --
see ``body.py`` for the full hierarchy.
