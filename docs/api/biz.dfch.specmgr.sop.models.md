# `biz.dfch.specmgr.sop.models`

Standard Operating Procedure (SOP) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors ``dec/models``'s layout: a versioned sub-package (``v1``, ...)
holding the frontmatter/body classes, the document wrapper and parser for
``sop`` documents, and the one-line ``SopSummary`` for the paged
``list_sop`` tool.
