# `biz.dfch.specmgr.sysrs.models.v1`

System Requirements Specification (SYSRS) models -- Pydantic schema and parser powered by the generic
``models/md`` engine.

Mirrors the ``sop/models/v1`` layout: a free-function ``parse_sysrs`` entry
point, document-level ``SysrsDocument(frontmatter, body)`` wrapper,
frontmatter and body subclasses under this same package, and the
``SysrsSummary`` listing model for the (Phase-3) ``list_sysrs`` tool. Body
classes map directly to heading sections in a SYSRS markdown file --
see ``body.py`` for the full hierarchy.
