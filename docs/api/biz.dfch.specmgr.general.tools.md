# `biz.dfch.specmgr.general.tools`

MCP tool wrappers for general-purpose utilities (mirrors ``adr/tools/``'s shape).

``mdformat`` -- a markdown document formatter that preserves YAML frontmatter
blocks (for ADR/UC files) and formats only the body markdown. ``update`` --
the generic, cross-domain whole-body or line-range replace for the seven
whole-body document types (``type`` is one of req/uc/tsk/qa/prb/gol/rsk;
optional 1-based inclusive body-line ``begin``/``end`` range with the
``N+1`` end-of-body sentinel). ``set_status`` -- the generic, cross-domain
status change for all eight document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/adr; ``superseded_by`` is ``adr``-only, composing
the status as ``"superseded by {superseded_by}"``). ``delete`` -- the
generic, cross-domain hard-delete for the eleven whole-body document types
(``type`` is one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr; ``adr`` is
not supported), resolving the document by ``id``, taking the domain's own
per-id lock, and removing it from disk (the single ``*.md`` file for the
ten flat domains, the entire ``<base>/<id>/`` folder for ``feat``),
returning the deleted path as a string. ``confluence_fetch`` (renamed from
``webfetch``, ADR a156fdf9-052c-4f43-93a2-eeec04a91eac) -- a
bearer-authenticated HTTP GET fetch restricted to a configured Confluence
base URL; automatically converts a normal, browsable Confluence page URL
(Cloud-style ``/pages/<id>/<title>`` or Server-style ``?pageId=<id>``) into
the equivalent ``{base}/rest/api/content/{id}?expand=body.storage`` REST
API URL, rejects ``/x/<tinyid>`` tiny links outright, raises on an
SSO-redirect off the configured base URL's host, and downloads
non-text/binary content (e.g. images) to a caller-supplied
``destination_path`` instead of returning it as text.
Import this package to register all general tools at once::

    from biz.dfch.specmgr.general import tools  # noqa: F401 (side-effects only)
