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
"""

from __future__ import annotations

import httpx

from ...server import mcp
from ._confluence_config import confluence_config

__all__ = [
    "ConfluenceUrlNotAllowedError",
    "confluence_fetch",
]

#: Request timeout, in seconds, for the underlying ``httpx.get`` call.
_REQUEST_TIMEOUT_SECONDS = 30.0


class ConfluenceUrlNotAllowedError(ValueError):
    """The requested URL does not match the configured base URL."""


@mcp.tool(
    name="confluence_fetch",
    title="Fetch a Confluence URL with bearer authentication",
    description=(
        "Fetch a URL over HTTP GET with a bearer token, but only if the URL matches the "
        "configured base URL (case-insensitively). Returns the raw response body text. "
        "Intended primarily for Confluence instances using PAT authentication."
    ),
)
def confluence_fetch(url: str) -> str:
    """Fetch ``url`` over HTTP GET, sending a bearer token, if ``url`` is allowed.

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
    """
    assert isinstance(url, str), type(url)
    assert url.strip()

    base_url, bearer_token = confluence_config()

    if not url.casefold().startswith(base_url.casefold()):
        raise ConfluenceUrlNotAllowedError(f"URL {url!r} does not match the configured base URL {base_url!r}.")

    response = httpx.get(
        url,
        headers={"Authorization": f"Bearer {bearer_token}"},
        follow_redirects=True,
        timeout=_REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    result = response.text
    return result
