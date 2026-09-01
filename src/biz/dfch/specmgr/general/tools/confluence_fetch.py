# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``@mcp.tool()`` wrapper: confluence_fetch (renamed from ``webfetch``, ADR
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
"""

from __future__ import annotations

from pathlib import Path

import httpx

from ...server import mcp
from ._confluence_config import confluence_config
from ._confluence_url import (
    ConfluenceAuthRedirectError,
    assert_same_host_as_base_url,
    build_rest_content_url,
    extract_page_id,
    looks_like_rest_or_download_url,
    looks_like_tiny_link,
)

__all__ = [
    "ConfluenceAuthRedirectError",
    "ConfluenceDestinationPathRequiredError",
    "ConfluenceTinyLinkNotSupportedError",
    "ConfluenceUrlNotAllowedError",
    "confluence_fetch",
]

#: Request timeout, in seconds, for the underlying ``httpx.get`` call.
_REQUEST_TIMEOUT_SECONDS = 30.0

#: The ``expand`` value used when auto-converting a browsable page URL into a
#: REST API content URL (REQ-001/002/ACC-001).
_DEFAULT_EXPAND = "body.storage"

#: ``Content-Type`` prefixes that are treated as text and returned directly as
#: ``response.text`` rather than triggering binary/download handling.
_TEXT_CONTENT_TYPE_PREFIXES = ("text/", "application/json", "application/xml")

#: A ``Content-Type`` suffix that also counts as text/XML-like (e.g.
#: ``application/vnd.api+json``, ``application/atom+xml``).
_TEXT_CONTENT_TYPE_SUFFIXES = ("+json", "+xml")


class ConfluenceUrlNotAllowedError(ValueError):
    """The requested URL does not match the configured base URL."""


class ConfluenceTinyLinkNotSupportedError(ValueError):
    """The requested URL is a Confluence ``/x/<tinyid>`` tiny link.

    Tiny links cannot be resolved to a page id without an authenticated
    browser session, so no HTTP request is attempted for them.
    """


class ConfluenceDestinationPathRequiredError(ValueError):
    """A non-text/binary response was received but no ``destination_path`` was given."""


def _is_text_content_type(content_type: str) -> bool:
    """Return whether ``content_type`` should be treated as text and returned as-is.

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
    """
    assert isinstance(content_type, str), type(content_type)

    media_type = content_type.split(";", 1)[0].strip().casefold()
    if not media_type:
        return False

    result = media_type.startswith(_TEXT_CONTENT_TYPE_PREFIXES) or media_type.endswith(_TEXT_CONTENT_TYPE_SUFFIXES)
    return result


@mcp.tool(
    name="confluence_fetch",
    title="Fetch a Confluence URL with bearer authentication",
    description=(
        "Fetch a URL over HTTP GET with a bearer token, but only if the URL matches the "
        "configured base URL (case-insensitively). A normal, browsable Confluence page URL "
        "(Cloud-style '/pages/<id>/<title>' or Server-style '?pageId=<id>') is automatically "
        "converted into the equivalent '{base}/rest/api/content/{id}?expand=body.storage' REST "
        "API URL before fetching; a '/x/<tinyid>' tiny link is rejected outright, since it cannot "
        "be resolved to a page id without an authenticated browser session; a request that gets "
        "redirected off the configured base URL's host (e.g. to an SSO login page) raises instead "
        "of returning that page's content. Text/JSON/XML responses are returned as raw body text; "
        "other (binary/image) content types are written to the given destination_path and that "
        "path is returned instead. Intended primarily for Confluence instances using PAT "
        "authentication."
    ),
)
def confluence_fetch(url: str, destination_path: str | None = None) -> str:
    """Fetch ``url`` over HTTP GET, sending a bearer token, if ``url`` is allowed.

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
    """
    assert isinstance(url, str), type(url)
    assert url.strip()
    assert destination_path is None or isinstance(destination_path, str), type(destination_path)

    base_url, bearer_token = confluence_config()

    if not url.casefold().startswith(base_url.casefold()):
        raise ConfluenceUrlNotAllowedError(f"URL {url!r} does not match the configured base URL {base_url!r}.")

    if looks_like_tiny_link(url):
        raise ConfluenceTinyLinkNotSupportedError(
            f"URL {url!r} is a Confluence tiny link ('/x/<tinyid>'), which cannot be resolved to a "
            "page id without an authenticated browser session; use the full page URL instead."
        )

    target_url = url
    if not looks_like_rest_or_download_url(url):
        page_id = extract_page_id(url)
        if page_id is not None:
            target_url = build_rest_content_url(base_url, page_id, expand=_DEFAULT_EXPAND)

    response = httpx.get(
        target_url,
        headers={"Authorization": f"Bearer {bearer_token}"},
        follow_redirects=True,
        timeout=_REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    assert_same_host_as_base_url(target_url, response.url, base_url)

    if _is_text_content_type(response.headers.get("content-type", "")):
        result = response.text
        return result

    if destination_path is None:
        raise ConfluenceDestinationPathRequiredError(
            f"Response for {target_url!r} has a non-text Content-Type "
            f"({response.headers.get('content-type', '')!r}); a destination_path is required to "
            "save binary/image content."
        )

    path = Path(destination_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)

    result = destination_path
    return result
