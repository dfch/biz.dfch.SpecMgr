# `biz.dfch.specmgr.req.models.v1`

Requirement (REQ) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``uc/models/v2`` layout: a free-function ``parse_req`` entry point,
document-level ``ReqDocument(frontmatter, body)`` wrapper, frontmatter and body
subclasses under this same package. Body classes map directly to heading sections
in a requirement markdown file -- see ``body.py`` for the full hierarchy.
