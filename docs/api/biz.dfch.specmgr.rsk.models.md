# `biz.dfch.specmgr.rsk.models`

Risk (RSK) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors ``tsk/models``'s layout: a versioned sub-package (``v1``, ...) holding
the frontmatter/body classes, the document wrapper and parser for ``rsk``
documents, and the one-line ``RskSummary`` for the paged ``list_rsk`` tool.
