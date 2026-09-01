# `biz.dfch.specmgr.general.tools._confluence_url`

Shared, ``mcp``-free Confluence URL helpers, used by both
``confluence_fetch`` and (later) ``confluence_update`` (ADR
a156fdf9-052c-4f43-93a2-eeec04a91eac, feat-50-confluence Phase 2).

Confirmed against a real Confluence Server/Data Center instance
(read-only GETs; see the feature README's Design Notes): a page's numeric
id can be recovered from two browsable URL shapes -- Cloud-style
``/pages/<id>/<title>`` and Server-style ``?pageId=<id>`` -- and converted
into ``{base}/rest/api/content/{id}`` (optionally with an ``expand``
query string), which the configured Bearer/PAT auth reaches successfully.
A third browsable shape, the ``/x/<tinyid>`` "tiny link", carries no
recoverable page id at all and is *not* matched by :func:`extract_page_id`
-- callers must detect it separately via :func:`looks_like_tiny_link` and
reject it with a dedicated error, since resolving it would require an
authenticated browser session this tool does not attempt to emulate.

This module has no dependency on ``mcp``, ``httpx``, or any other
tool-specific machinery -- it is plain, unit-testable string/regex logic,
mirroring the shape of :mod:`_confluence_config` and :mod:`_path_safety`.

## Functions

### `build_rest_content_url(base_url: 'str', page_id: 'str', expand: 'str | None' = None) -> 'str'`

Build a Confluence REST API content URL for ``page_id``.

Parameters
----------
base_url:
    The configured Confluence base URL. A single trailing ``/``, if
    present, is stripped before appending the REST path.
page_id:
    The numeric page id, as a string (typically from
    :func:`extract_page_id`).
expand:
    An optional comma-separated Confluence ``expand`` value (e.g.
    ``"body.storage"``); when given, appended as a ``?expand=`` query
    string.

Returns
-------
str
    ``f"{base_url}/rest/api/content/{page_id}"``, with the trailing
    slash of ``base_url`` stripped, plus an ``?expand={expand}`` suffix
    if ``expand`` was given.


### `extract_page_id(url: 'str') -> 'str | None'`

Extract a Confluence numeric page id from a browsable page URL.

Tries the Server-style ``pageId`` query parameter first
(``[?&]pageId=(\d+)``), then the Cloud-style ``/pages/<id>/...`` path
segment (``/pages/(\d+)(?:/|$|\?)``). Anything else -- including the
``/x/<tinyid>`` tiny-link shape, which carries no recoverable page id --
returns ``None``.

Parameters
----------
url:
    The browsable page URL to inspect.

Returns
-------
str | None
    The extracted numeric page id, as a string, or ``None`` if neither
    pattern matches.


### `looks_like_rest_or_download_url(url: 'str') -> 'bool'`

Return whether ``url`` already targets a REST API or download endpoint.

Such URLs must be passed through unchanged rather than re-converted via
:func:`extract_page_id` -- e.g. an already-built
``{base}/rest/api/content/123?expand=body.storage`` URL contains
``pageId=``-shaped text nowhere, but re-deriving it would be redundant
and fragile.

Parameters
----------
url:
    The URL to inspect.

Returns
-------
bool
    ``True`` if ``url`` contains ``/rest/api/`` or ``/download/``
    (case-sensitive substring check -- real Confluence REST/download
    paths are always lowercase), ``False`` otherwise.


### `looks_like_tiny_link(url: 'str') -> 'bool'`

Return whether ``url`` is a Confluence "tiny link" (``/x/<tinyid>``).

Tiny links carry no recoverable page id and cannot be resolved to a
``/rest/api/content/<id>`` URL without an authenticated browser session
(confirmed against a real instance); callers must reject them with a
dedicated, clear error instead of attempting any request.

Parameters
----------
url:
    The URL to inspect.

Returns
-------
bool
    ``True`` if ``url`` contains a ``/x/<opaque-non-empty-segment>``
    path segment, ``False`` otherwise.

