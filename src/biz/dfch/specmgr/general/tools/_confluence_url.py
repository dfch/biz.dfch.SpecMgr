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
"""

from __future__ import annotations

import re

__all__ = [
    "build_rest_content_url",
    "extract_page_id",
    "looks_like_rest_or_download_url",
    "looks_like_tiny_link",
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
