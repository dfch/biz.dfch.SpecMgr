# `biz.dfch.specmgr.general.tools.webfetch`

``@mcp.tool()`` wrapper: webfetch.

A generic, bearer-authenticated HTTP GET fetch tool, restricted to URLs that
match a configured base URL (case-insensitively). Intended primarily for
Web Server instances that accept PAT (Personal Access Token)
authentication, but implemented as a plain authenticated fetch, not
Web Server-specific page-ID/REST-API logic -- the calling agent processes the
raw response body itself (no HTML-to-markdown conversion or JSON parsing).

Configuration is read directly from two environment variables
(:data:`WEBFETCH_BASE_URL_ENV_VAR`, :data:`WEBFETCH_BEARER_ENV_VAR`), mirroring
the constant + private-helper pattern used by ``general/tools/_doc_paths.py``
and ``adr/tools/_paths.py`` -- no ``pydantic-settings``, no in-memory caching.

## Classes

### `WebfetchNotConfiguredError`

:data:`WEBFETCH_BASE_URL_ENV_VAR` and/or :data:`WEBFETCH_BEARER_ENV_VAR` are not set.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


### `WebfetchUrlNotAllowedError`

The requested URL does not match the configured base URL.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_webfetch_config() -> 'tuple[str, str]'`

Return the configured ``(base_url, bearer_token)`` pair.

Reads :data:`WEBFETCH_BASE_URL_ENV_VAR` and :data:`WEBFETCH_BEARER_ENV_VAR`
directly from the environment on every call -- no caching, consistent with
this codebase's "the environment is the sole source of truth" config
style (mirrors ``adr.tools._paths.adr_base_dir``).

Returns
-------
tuple[str, str]
    The configured ``(base_url, bearer_token)`` pair.

Raises
------
WebfetchNotConfiguredError
    If either environment variable is unset or blank.


### `webfetch(url: 'str') -> 'str'`

Fetch ``url`` over HTTP GET, sending a bearer token, if ``url`` is allowed.

Validates that both :data:`WEBFETCH_BASE_URL_ENV_VAR` and
:data:`WEBFETCH_BEARER_ENV_VAR` are configured, then that ``url`` matches
the configured base URL via a case-insensitive prefix match (e.g. a
configured base URL of ``https://example.com`` matches
``HTTPS://Example.com/page``). The request follows redirects (``httpx``
does not do so by default, unlike ``urllib.request``) and raises on a
non-2xx response.

Parameters
----------
url:
    The URL to fetch. Must case-insensitively start with the configured
    base URL (:data:`WEBFETCH_BASE_URL_ENV_VAR`).

Returns
-------
str
    The raw response body text, unprocessed (no HTML-to-markdown
    conversion or JSON parsing -- the calling agent handles that itself).

Raises
------
WebfetchNotConfiguredError
    If either environment variable is unset or blank.
WebfetchUrlNotAllowedError
    If ``url`` does not match the configured base URL.
httpx.HTTPStatusError
    If the response status code is not in the 2xx range.

