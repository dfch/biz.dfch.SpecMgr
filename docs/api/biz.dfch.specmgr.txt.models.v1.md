# `biz.dfch.specmgr.txt.models.v1`

Free-Form Text (TXT) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``vcr/models/v1`` layout: a free-function ``parse_txt`` entry
point, document-level ``TxtDocument(frontmatter, body)`` wrapper,
frontmatter and body subclasses under this same package, and the
``TxtSummary`` listing model for the (Phase 110) ``list_txt`` tool. Body
classes map directly to the structure of a free-form text markdown file --
an opaque free-form ``body`` plus a mandatory newest-first ``## Updates``
log -- see ``body.py`` for the full hierarchy.
