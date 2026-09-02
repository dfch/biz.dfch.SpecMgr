# `biz.dfch.specmgr.sysrs.models`

System Requirements Specification (SYSRS) models -- Pydantic schema and parser powered by the generic
``models/md`` engine.

Mirrors ``sop/models``'s layout: a versioned sub-package (``v1``, ...)
holding the frontmatter/body classes, the document wrapper and parser for
``sysrs`` documents, and the one-line ``SysrsSummary`` for the paged
``list_sysrs`` tool.
