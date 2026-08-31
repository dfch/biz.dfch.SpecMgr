# `biz.dfch.specmgr.vcr.models`

Verification Case Record (VCR) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors ``dec/models``'s layout: a versioned sub-package (``v1``, ...)
holding the frontmatter/body classes, the document wrapper and parser for
``vcr`` documents, and the one-line ``VcrSummary`` for the paged
``list_vcr`` tool.
