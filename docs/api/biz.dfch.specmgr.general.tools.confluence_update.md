# `biz.dfch.specmgr.general.tools.confluence_update`

``@mcp.tool()`` wrapper: confluence_update (ADR a156fdf9-052c-4f43-93a2-eeec04a91eac,
feat-50-confluence Phase 3).

Writes a local Markdown file's content into an existing Confluence page's
body via the REST API, using the same Bearer/PAT authentication and the
same two environment variables :mod:`.confluence_fetch` already uses (see
:mod:`._confluence_config`). This Phase 3 implementation covers only the
core write flow (REQ-007/REQ-008, ACC-006):

1. Resolve ``page_url_or_id`` to a numeric page id (see
   :func:`._confluence_url.resolve_page_id`) -- a bare id, a browsable page
   URL, or an already-REST-shaped URL are all accepted; a ``/x/<tinyid>``
   tiny link is rejected the same way :func:`.confluence_fetch.confluence_fetch`
   rejects it.
2. ``GET {base}/rest/api/content/{id}?expand=version,title`` to read the
   page's current ``version.number`` and ``title`` (``body.storage`` is not
   needed here, since this phase never reads the *existing* body).
3. Render the Markdown file at ``markdown_file_path`` to an HTML fragment
   via ``markdown_it.MarkdownIt("commonmark").render(...)``.
4. ``PUT {base}/rest/api/content/{id}`` with the incremented version number,
   the unchanged title, and the rendered fragment as the new
   ``body.storage.value``.

Local-image attachment upload and ``<img>`` -> ``<ac:image>`` storage-format
macro rewriting (REQ-009/ACC-007) are explicitly deferred to Phase 4 -- this
module renders and pushes the Markdown's HTML as-is, with no attachment
handling.

## Classes

### `ConfluencePageIdNotResolvedError`

``page_url_or_id`` could not be resolved to a numeric Confluence page id.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


### `ConfluenceUnexpectedResponseShapeError`

A Confluence REST API response is missing an expected ``version``/``title`` key.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_read_version_and_title(payload: 'dict[str, Any]') -> 'tuple[int, str]'`

Extract ``version.number`` and ``title`` from a GET response's JSON payload.

Parameters
----------
payload:
    The parsed JSON body of the ``GET {base}/rest/api/content/{id}``
    response.

Returns
-------
tuple[int, str]
    The ``(version_number, title)`` pair.

Raises
------
ConfluenceUnexpectedResponseShapeError
    If ``version``, ``version.number``, or ``title`` is missing, instead
    of letting a raw ``KeyError``/``TypeError`` propagate.


### `_resolve_page_id(page_url_or_id: 'str') -> 'str'`

Resolve ``page_url_or_id`` to a numeric page id, or raise a clear error.

Parameters
----------
page_url_or_id:
    A bare numeric page id, a browsable page URL, or a REST content URL.

Returns
-------
str
    The resolved numeric page id.

Raises
------
ConfluenceTinyLinkNotSupportedError
    If ``page_url_or_id`` is a ``/x/<tinyid>`` tiny link.
ConfluencePageIdNotResolvedError
    If ``page_url_or_id`` matches none of the accepted shapes.


### `confluence_update(page_url_or_id: 'str', markdown_file_path: 'str') -> 'dict[str, Any]'`

Write ``markdown_file_path``'s rendered content into the Confluence page identified by ``page_url_or_id``.

Resolves ``page_url_or_id`` to a numeric page id, ``GET``\ s the page's
current ``version.number``/``title``, renders the Markdown file at
``markdown_file_path`` to an HTML fragment, then ``PUT``\ s the
incremented version with that fragment as the new
``body.storage.value``, leaving the title unchanged. Both the GET and
the PUT apply the same post-redirect host check
:func:`.confluence_fetch.confluence_fetch` applies, via
:func:`._confluence_url.assert_same_host_as_base_url`.

Parameters
----------
page_url_or_id:
    A bare numeric page id, a browsable Confluence page URL
    (Cloud-style ``/pages/<id>/<title>`` or Server-style
    ``?pageId=<id>``), or an already-``/rest/api/content/<id>``-shaped
    REST URL.
markdown_file_path:
    The local filesystem path to the Markdown file to render and push
    as the page's new body. Read as UTF-8 text; a missing file raises
    the natural ``FileNotFoundError`` -- no dedicated wrapper, since
    that built-in exception already names the offending path clearly.

Returns
-------
dict[str, Any]
    ``{"id": <page id>, "title": <unchanged title>, "version": <new version number>}``
    -- a small, caller-useful summary rather than the raw PUT response
    JSON, so callers do not need to know Confluence's own response
    shape just to confirm what changed.

Raises
------
ConfluenceNotConfiguredError
    If either environment variable is unset or blank.
ConfluenceTinyLinkNotSupportedError
    If ``page_url_or_id`` is a ``/x/<tinyid>`` tiny link.
ConfluencePageIdNotResolvedError
    If ``page_url_or_id`` cannot be resolved to a page id.
ConfluenceAuthRedirectError
    If either the GET's or the PUT's final response URL host differs
    from the configured base URL's host.
ConfluenceUnexpectedResponseShapeError
    If the GET response JSON is missing ``version``/``version.number``/``title``.
FileNotFoundError
    If ``markdown_file_path`` does not exist.
httpx.HTTPStatusError
    If either the GET or the PUT response status code is not in the 2xx
    range.

