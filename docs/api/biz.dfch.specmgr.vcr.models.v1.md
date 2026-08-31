# `biz.dfch.specmgr.vcr.models.v1`

Verification Case Record (VCR) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``dec/models/v1`` layout: a free-function ``parse_vcr`` entry
point, document-level ``VcrDocument(frontmatter, body)`` wrapper,
frontmatter and body subclasses under this same package, and the
``VcrSummary`` listing model for the (Phase-2) ``list_vcr`` tool. Body
classes map directly to heading sections in a verification case record
markdown file -- see ``body.py`` for the full hierarchy.
