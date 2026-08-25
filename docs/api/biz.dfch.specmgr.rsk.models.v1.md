# `biz.dfch.specmgr.rsk.models.v1`

Risk (RSK) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``tsk/models/v1`` layout: a free-function ``parse_rsk`` entry
point, document-level ``RskDocument(frontmatter, body)`` wrapper, and a
one-line ``RskSummary`` for the paged ``list_rsk`` tool, with frontmatter and
body subclasses under this same package. Body classes map directly to heading
sections in an ``rsk`` markdown file -- see ``body.py``/``assessment.py`` for
the full hierarchy.
