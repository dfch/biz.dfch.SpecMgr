# `biz.dfch.specmgr.general.tools`

MCP tool wrappers for general-purpose utilities (mirrors ``adr/tools/``'s shape).

``mdformat`` -- a markdown document formatter that preserves YAML frontmatter
blocks (for ADR/UC files) and formats only the body markdown. ``update`` --
the generic, cross-domain whole-body or line-range replace for the seven
whole-body document types (``type`` is one of req/uc/tsk/qa/prb/gol/rsk;
optional 1-based inclusive body-line ``begin``/``end`` range with the
``N+1`` end-of-body sentinel). ``webfetch`` -- a bearer-authenticated HTTP
GET fetch restricted to a configured base URL. Import this package to
register all general tools at once::

    from biz.dfch.specmgr.general import tools  # noqa: F401 (side-effects only)
