# `biz.dfch.specmgr.set.models.v1`

Set (SET) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``txt/models/v1`` layout: a free-function ``parse_set`` entry
point, document-level ``SetDocument(frontmatter, body)`` wrapper,
frontmatter and body subclasses under this same package, and the
``SetSummary`` listing model for the paged ``list_set`` tool. Body classes
map directly to the structure of a set markdown file -- a mandatory opaque
``## Description`` plus a mandatory mixed-tag ``## Items`` list -- see
``body.py`` for the full hierarchy.
