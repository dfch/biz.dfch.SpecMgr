# `biz.dfch.specmgr.general.tools.confluence_fetch`

``@mcp.tool()`` wrapper: confluence_fetch (renamed from ``webfetch``, ADR
a156fdf9-052c-4f43-93a2-eeec04a91eac).

A generic, bearer-authenticated HTTP GET fetch tool, restricted to URLs that
match a configured base URL (case-insensitively). Intended primarily for
Confluence instances that accept PAT (Personal Access Token) authentication,
but implemented as a plain authenticated fetch, not Confluence-specific
page-ID/REST-API logic -- the calling agent processes the raw response body
itself (no HTML-to-markdown conversion or JSON parsing). Later phases of
feat-50-confluence extend this tool with automatic REST-API URL construction,
tiny-link rejection, SSO-redirect detection, and binary/image download
support.

Configuration is read from the shared :mod:`._confluence_config` helper
(:data:`CONFLUENCE_BASE_URL_ENV_VAR`, :data:`CONFLUENCE_BEARER_ENV_VAR`),
mirroring the constant + private-helper pattern used by
``general/tools/_doc_paths.py`` and ``adr/tools/_paths.py`` -- no
``pydantic-settings``, no in-memory caching.

## Classes

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

### `confluence_fetch(url: 'str') -> 'str'`

Fetch ``url`` over HTTP GET, sending a bearer token, if ``url`` is allowed.

Validates that both :data:`CONFLUENCE_BASE_URL_ENV_VAR` and
:data:`CONFLUENCE_BEARER_ENV_VAR` are configured, then that ``url`` matches
the configured base URL via a case-insensitive prefix match (e.g. a
configured base URL of ``https://example.com`` matches
``HTTPS://Example.com/page``). The request follows redirects (``httpx``
does not do so by default, unlike ``urllib.request``) and raises on a
non-2xx response.

Parameters
----------
url:
    The URL to fetch. Must case-insensitively start with the configured
    base URL (:data:`CONFLUENCE_BASE_URL_ENV_VAR`).

Returns
-------
str
    The raw response body text, unprocessed (no HTML-to-markdown
    conversion or JSON parsing -- the calling agent handles that itself).

Raises
------
ConfluenceNotConfiguredError
    If either environment variable is unset or blank.
ConfluenceUrlNotAllowedError
    If ``url`` does not match the configured base URL.
httpx.HTTPStatusError
    If the response status code is not in the 2xx range.

