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
``destination_path`` instead of returning it as text. ``confluence_update``
(ADR a156fdf9-052c-4f43-93a2-eeec04a91eac, feat-50-confluence Phases 3-4) --
writes a local Markdown file's rendered HTML into an existing Confluence
page's body via the REST API: resolves ``page_url_or_id`` (bare page id,
browsable page URL, or REST content URL) to a page id, ``GET``\ s the
page's current ``version.number``/``title``, renders the Markdown file via
``markdown-it-py``, best-effort uploads every local image the Markdown
references as a Confluence attachment (``POST .../child/attachment``,
falling back to updating an existing attachment's content if the filename
already exists) and rewrites the corresponding ``<img>`` tags into
Confluence's ``<ac:image>``/``<ri:attachment>`` storage-format macro, then
``PUT``\ s the incremented version with that (possibly rewritten) HTML
fragment as the new body.
Import this package to register all general tools at once::

    from biz.dfch.specmgr.general import tools  # noqa: F401 (side-effects only)
