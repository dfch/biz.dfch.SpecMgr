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

"""Shared, ``mcp``-free Confluence URL helpers, used by both
``confluence_fetch`` and ``confluence_update`` (ADR
a156fdf9-052c-4f43-93a2-eeec04a91eac, feat-50-confluence Phases 2-3).

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

:func:`assert_same_host_as_base_url` (feat-50-confluence Phase 3) plus its
:class:`ConfluenceAuthRedirectError` live here too, since both
``confluence_fetch`` and ``confluence_update`` must apply the identical
post-redirect host-comparison check to every request they make (the ADR's
Design Notes: SSO-redirect detection is "reused for ``confluence_update``'s
internal GET/PUT").

This module has no dependency on ``mcp`` or any other tool-specific
machinery beyond ``httpx`` itself (needed for :class:`httpx.URL` host
parsing) -- it is plain, unit-testable logic, mirroring the shape of
:mod:`_confluence_config` and :mod:`_path_safety`.
"""

from __future__ import annotations

import re

import httpx

__all__ = [
    "ConfluenceAuthRedirectError",
    "assert_same_host_as_base_url",
    "build_rest_content_url",
    "extract_page_id",
    "looks_like_rest_or_download_url",
    "looks_like_tiny_link",
    "resolve_page_id",
]

#: Matches a Server-style ``pageId`` query parameter, e.g. ``?pageId=123`` or
#: ``&pageId=123`` anywhere in the query string; captures the numeric id.
_PAGE_ID_QUERY_PATTERN = re.compile(r"[?&]pageId=(\d+)")

#: Matches a Cloud-style ``/pages/<id>/...`` path segment; captures the numeric
#: id. The id must be immediately followed by ``/``, the end of the string, or
#: ``?`` -- so ``/pages/123abc`` (not a pure numeric id) does not match.
_PAGE_ID_PATH_PATTERN = re.compile(r"/pages/(\d+)(?:/|$|\?)")

#: Matches the Confluence "tiny link" shape, e.g. ``/x/AbCdEf`` -- ``/x/``
#: followed by a non-empty opaque segment (no ``/`` inside it).
_TINY_LINK_PATTERN = re.compile(r"/x/[^/?#]+")

#: Substrings that mark a URL as already being a REST API or attachment
#: download URL, which must be passed through unchanged rather than
#: re-converted via :func:`extract_page_id`. Matched case-sensitively, since
#: real Confluence REST/download paths are lowercase and treating e.g.
#: ``/REST/API/`` as equivalent would risk masking a genuinely different path.
_REST_OR_DOWNLOAD_MARKERS = ("/rest/api/", "/download/")

#: Matches a Confluence REST API content URL's numeric page id, e.g.
#: ``/rest/api/content/12345`` (optionally followed by ``/``, ``?``, or the
#: end of the string) -- used by :func:`resolve_page_id` for
#: ``confluence_update``, which (unlike :func:`extract_page_id`) must also
#: accept an already-REST-shaped URL as input.
_REST_CONTENT_ID_PATTERN = re.compile(r"/rest/api/content/(\d+)(?:/|$|\?)")


class ConfluenceAuthRedirectError(RuntimeError):
    """A request was redirected off the configured base URL's host.

    Typically means the endpoint is gated by an SSO/auth proxy that does not
    forward Bearer tokens, and the response received is an SSO login page,
    not the requested Confluence content. Shared between ``confluence_fetch``
    and ``confluence_update`` (both perform the identical host-comparison
    check via :func:`assert_same_host_as_base_url`).
    """


def extract_page_id(url: str) -> str | None:
    """Extract a Confluence numeric page id from a browsable page URL.

    Tries the Server-style ``pageId`` query parameter first
    (``[?&]pageId=(\\d+)``), then the Cloud-style ``/pages/<id>/...`` path
    segment (``/pages/(\\d+)(?:/|$|\\?)``). Anything else -- including the
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
    """
    assert isinstance(url, str), type(url)
    assert url.strip()

    query_match = _PAGE_ID_QUERY_PATTERN.search(url)
    if query_match is not None:
        result = query_match.group(1)
        return result

    path_match = _PAGE_ID_PATH_PATTERN.search(url)
    if path_match is not None:
        result = path_match.group(1)
        return result

    return None


def build_rest_content_url(base_url: str, page_id: str, expand: str | None = None) -> str:
    """Build a Confluence REST API content URL for ``page_id``.

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
    """
    assert isinstance(base_url, str), type(base_url)
    assert base_url.strip()
    assert isinstance(page_id, str), type(page_id)
    assert page_id.strip()
    assert expand is None or isinstance(expand, str), type(expand)

    result = f"{base_url.rstrip('/')}/rest/api/content/{page_id}"
    if expand:
        result = f"{result}?expand={expand}"
    return result


def looks_like_rest_or_download_url(url: str) -> bool:
    """Return whether ``url`` already targets a REST API or download endpoint.

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
    """
    assert isinstance(url, str), type(url)
    assert url.strip()

    result = any(marker in url for marker in _REST_OR_DOWNLOAD_MARKERS)
    return result


def looks_like_tiny_link(url: str) -> bool:
    """Return whether ``url`` is a Confluence "tiny link" (``/x/<tinyid>``).

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
    """
    assert isinstance(url, str), type(url)
    assert url.strip()

    result = _TINY_LINK_PATTERN.search(url) is not None
    return result


def assert_same_host_as_base_url(request_url: str, response_url: httpx.URL, base_url: str) -> None:
    """Raise :class:`ConfluenceAuthRedirectError` if ``response_url``'s host differs from ``base_url``'s.

    Shared between ``confluence_fetch`` and ``confluence_update``
    (ADR a156fdf9-052c-4f43-93a2-eeec04a91eac's Design Notes: SSO-redirect
    detection is "reused for ``confluence_update``'s internal GET/PUT"), so
    both tools apply the identical post-redirect host comparison instead of
    duplicating it.

    Parameters
    ----------
    request_url:
        The URL that was requested, used only for the error message.
    response_url:
        The final response URL (``httpx.Response.url``), i.e. after
        following any redirects.
    base_url:
        The configured Confluence base URL.

    Raises
    ------
    ConfluenceAuthRedirectError
        If ``response_url``'s host (case-insensitively) differs from
        ``base_url``'s host.
    """
    assert isinstance(request_url, str), type(request_url)
    assert isinstance(response_url, httpx.URL), type(response_url)
    assert isinstance(base_url, str), type(base_url)
    assert base_url.strip()

    response_host = (response_url.host or "").casefold()
    configured_host = (httpx.URL(base_url).host or "").casefold()
    if response_host != configured_host:
        raise ConfluenceAuthRedirectError(
            f"Request for {request_url!r} was redirected to a different host ({response_host!r}), "
            f"expected {configured_host!r}; the endpoint may be gated by an SSO/auth proxy that "
            "does not forward Bearer tokens."
        )


def resolve_page_id(value: str) -> str | None:
    """Resolve ``value`` to a Confluence numeric page id, for ``confluence_update``.

    Unlike :func:`extract_page_id` (browsable page URLs only, used by
    ``confluence_fetch`` to build a fresh REST URL from scratch),
    ``confluence_update`` must also accept a bare numeric page id or an
    already-``/rest/api/content/<id>``-shaped URL directly, since it always
    rebuilds the GET/PUT target itself from the configured base URL plus the
    resolved id (the id, not the caller-supplied value, is what actually
    matters). Tried, in order:

    - ``value`` stripped of surrounding whitespace is a bare numeric id
      (``str.isdigit()``);
    - :func:`extract_page_id` (Server-style ``?pageId=`` query parameter or
      Cloud-style ``/pages/<id>/...`` path segment);
    - the numeric id embedded in an already-``/rest/api/content/<id>``-shaped
      URL.

    Parameters
    ----------
    value:
        A bare numeric page id, a browsable page URL, or a REST content URL.

    Returns
    -------
    str | None
        The resolved numeric page id, or ``None`` if none of the above
        match -- including a ``/x/<tinyid>`` tiny link, which callers must
        detect separately via :func:`looks_like_tiny_link` and reject with a
        dedicated error, mirroring :func:`extract_page_id`'s own tiny-link
        handling.
    """
    assert isinstance(value, str), type(value)
    assert value.strip()

    stripped = value.strip()
    if stripped.isdigit():
        return stripped

    page_id = extract_page_id(stripped)
    if page_id is not None:
        return page_id

    rest_match = _REST_CONTENT_ID_PATTERN.search(stripped)
    if rest_match is not None:
        result = rest_match.group(1)
        return result

    return None
