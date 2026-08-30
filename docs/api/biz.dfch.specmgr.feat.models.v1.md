# `biz.dfch.specmgr.feat.models.v1`

Feature (FEAT) v1 schema -- frontmatter, body, document, parser, summary.

Mirrors the ``dec/models/v1`` layout: a free-function ``parse_feat`` entry
point, document-level ``FeatDocument(frontmatter, body)`` wrapper,
frontmatter and body subclasses under this same package, and the
``FeatSummary`` listing model for the (Phase-2) ``list_feat`` tool. Body
classes map directly to heading sections in a feature markdown file -- see
``body.py`` for the full hierarchy.
