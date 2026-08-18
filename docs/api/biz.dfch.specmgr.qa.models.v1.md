# `biz.dfch.specmgr.qa.models.v1`

Question and Answer (QA) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``tsk/models/v1`` layout: a free-function ``parse_qa`` entry point,
document-level ``QaDocument(frontmatter, body)`` wrapper, frontmatter and body
subclasses under this same package. Body classes map directly to heading sections
in a ``qa`` markdown file -- see ``body.py`` for the full hierarchy.
