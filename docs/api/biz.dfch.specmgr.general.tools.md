# `biz.dfch.specmgr.general.tools`

MCP tool wrappers for general-purpose utilities (mirrors ``adr/tools/``'s shape).

Currently just ``mdformat`` -- a markdown document formatter that preserves YAML
frontmatter blocks (for ADR/UC files) and formats only the body markdown.
Import this package to register all general tools at once::

    from biz.dfch.specmgr.general import tools  # noqa: F401 (side-effects only)
