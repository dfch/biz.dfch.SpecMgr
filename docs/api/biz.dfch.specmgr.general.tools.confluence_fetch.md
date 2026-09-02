# `biz.dfch.specmgr.general.tools.confluence_fetch`

``@mcp.tool()`` wrapper: confluence_fetch (renamed from ``webfetch``, ADR
a156fdf9-052c-4f43-93a2-eeec04a91eac).

A bearer-authenticated HTTP GET fetch tool, restricted to URLs that match a
configured base URL (case-insensitively). Intended primarily for Confluence
instances that accept PAT (Personal Access Token) authentication. Beyond a
plain authenticated fetch, this tool (feat-50-confluence Phase 2) also:

- automatically converts a normal, browsable Confluence page URL (Cloud-style
  ``/pages/<id>/<title>`` or Server-style ``?pageId=<id>``) into the
  equivalent ``{base}/rest/api/content/{id}?expand=body.storage`` REST API
  URL before fetching it (see :mod:`._confluence_url`);
- rejects the ``/x/<tinyid>`` "tiny link" URL shape outright, since it cannot
  be resolved to a page id without an authenticated browser session;
- detects when the request was redirected off the configured base URL's host
  (e.g. to an SSO login page) and raises instead of silently returning that
  page's content as if it were the requested resource;
- downloads non-text/binary content (based on the response ``Content-Type``)
  by writing it to a caller-supplied ``destination_path`` and returning that
  path, while still returning text/JSON/XML content directly as before.

Configuration is read from the shared :mod:`._confluence_config` helper
(:data:`CONFLUENCE_BASE_URL_ENV_VAR`, :data:`CONFLUENCE_BEARER_ENV_VAR`),
mirroring the constant + private-helper pattern used by
``general/tools/_doc_paths.py`` and ``adr/tools/_paths.py`` -- no
``pydantic-settings``, no in-memory caching.

## Classes

### `ConfluenceDestinationPathRequiredError`

A non-text/binary response was received but no ``destination_path`` was given.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


### `ConfluenceTinyLinkNotSupportedError`

The requested URL is a Confluence ``/x/<tinyid>`` tiny link.

Tiny links cannot be resolved to a page id without an authenticated
browser session, so no HTTP request is attempted for them.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


### `ConfluenceUrlNotAllowedError`

The requested URL does not match the configured base URL.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_is_text_content_type(content_type: 'str') -> 'bool'`

Return whether ``content_type`` should be treated as text and returned as-is.

Parameters
----------
content_type:
    The raw ``Content-Type`` response header value (may include
    parameters, e.g. ``"text/html; charset=utf-8"``).

Returns
-------
bool
    ``True`` if the media type (the part before any ``;`` parameters)
    starts with one of :data:`_TEXT_CONTENT_TYPE_PREFIXES` or ends with
    one of :data:`_TEXT_CONTENT_TYPE_SUFFIXES` (case-insensitively),
    ``False`` otherwise (including when ``content_type`` is blank, which
    is conservatively treated as non-text).


### `confluence_fetch(url: 'str', destination_path: 'str | None' = None) -> 'str'`

Fetch ``url`` over HTTP GET, sending a bearer token, if ``url`` is allowed.

Validates that both :data:`CONFLUENCE_BASE_URL_ENV_VAR` and
:data:`CONFLUENCE_BEARER_ENV_VAR` are configured, then that ``url`` matches
the configured base URL via a case-insensitive prefix match (e.g. a
configured base URL of ``https://example.com`` matches
``HTTPS://Example.com/page``) -- this check is applied to the
caller-supplied ``url`` itself, before any REST-URL conversion, since a
constructed REST URL is always on the same host as the base URL by
construction.

``url`` is then classified and possibly rewritten before the request is
made:

- a ``/x/<tinyid>`` tiny link raises :class:`ConfluenceTinyLinkNotSupportedError`
  immediately, with no HTTP request attempted;
- a URL that already targets ``/rest/api/`` or ``/download/`` (see
  :func:`._confluence_url.looks_like_rest_or_download_url`) is used
  unchanged;
- a URL from which a numeric page id can be extracted (see
  :func:`._confluence_url.extract_page_id`) is rewritten to
  ``{base}/rest/api/content/{id}?expand=body.storage``;
- any other URL is fetched exactly as given (the original, generic
  ``webfetch`` behavior).

The request follows redirects (``httpx`` does not do so by default,
unlike ``urllib.request``) and raises on a non-2xx response. After a
successful response, if the final response URL's host (post-redirects)
does not match the configured base URL's host, :class:`ConfluenceAuthRedirectError`
is raised instead of returning that (likely SSO login page) content.

Finally, the response ``Content-Type`` determines how the body is
returned: text/JSON/XML content is returned as ``response.text`` (any
given ``destination_path`` is ignored in this case); any other content
type is written as raw bytes to ``destination_path`` and that path is
returned, or :class:`ConfluenceDestinationPathRequiredError` is raised if
``destination_path`` was not given.

Parameters
----------
url:
    The URL to fetch. Must case-insensitively start with the configured
    base URL (:data:`CONFLUENCE_BASE_URL_ENV_VAR`).
destination_path:
    The filesystem path to write non-text/binary response content to.
    Ignored for text/JSON/XML responses. Required for any other content
    type.

Returns
-------
str
    The raw response body text for text/JSON/XML responses, unprocessed
    (no HTML-to-markdown conversion or JSON parsing -- the calling agent
    handles that itself); or, for binary/image content, the
    ``destination_path`` the response bytes were written to.

Raises
------
ConfluenceNotConfiguredError
    If either environment variable is unset or blank.
ConfluenceUrlNotAllowedError
    If ``url`` does not match the configured base URL.
ConfluenceTinyLinkNotSupportedError
    If ``url`` is a ``/x/<tinyid>`` tiny link.
ConfluenceAuthRedirectError
    If the final response URL's host differs from the configured base
    URL's host.
ConfluenceDestinationPathRequiredError
    If the response content type is non-text/binary and no
    ``destination_path`` was given.
httpx.HTTPStatusError
    If the response status code is not in the 2xx range.

