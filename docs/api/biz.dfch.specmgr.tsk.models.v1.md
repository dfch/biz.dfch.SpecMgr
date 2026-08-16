# `biz.dfch.specmgr.tsk.models.v1`

TaskList (TSK) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``req/models/v1`` layout: a free-function ``parse_tsk`` entry point,
document-level ``TskDocument(frontmatter, body)`` wrapper, frontmatter and body
subclasses under this same package. Body classes map directly to heading sections
in a ``tsk`` markdown file -- see ``body.py``/``task_item.py`` for the full hierarchy.
