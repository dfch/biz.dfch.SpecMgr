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

"""``@mcp.tool()`` wrapper: webfetch.

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
"""

from __future__ import annotations

import os

import httpx

from ...server import mcp

__all__ = [
    "WEBFETCH_BASE_URL_ENV_VAR",
    "WEBFETCH_BEARER_ENV_VAR",
    "WebfetchNotConfiguredError",
    "WebfetchUrlNotAllowedError",
    "webfetch",
]

#: Environment variable holding the base URL that requested URLs must match.
WEBFETCH_BASE_URL_ENV_VAR = "SPECMGR_WEBFETCH_BASE_URL"

#: Environment variable holding the bearer token sent as the ``Authorization`` header.
WEBFETCH_BEARER_ENV_VAR = "SPECMGR_WEBFETCH_BEARER"

#: Request timeout, in seconds, for the underlying ``httpx.get`` call.
_REQUEST_TIMEOUT_SECONDS = 30.0


class WebfetchNotConfiguredError(RuntimeError):
    """:data:`WEBFETCH_BASE_URL_ENV_VAR` and/or :data:`WEBFETCH_BEARER_ENV_VAR` are not set."""


class WebfetchUrlNotAllowedError(ValueError):
    """The requested URL does not match the configured base URL."""


def _webfetch_config() -> tuple[str, str]:
    """Return the configured ``(base_url, bearer_token)`` pair.

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
    """
    base_url = os.environ.get(WEBFETCH_BASE_URL_ENV_VAR)
    bearer_token = os.environ.get(WEBFETCH_BEARER_ENV_VAR)
    if not base_url or not bearer_token:
        raise WebfetchNotConfiguredError(
            f"webfetch is not configured: both {WEBFETCH_BASE_URL_ENV_VAR!r} and {WEBFETCH_BEARER_ENV_VAR!r} "
            f"must be set as environment variables."
        )
    return base_url, bearer_token


@mcp.tool(
    name="webfetch",
    title="Fetch a URL with bearer authentication",
    description=(
        "Fetch a URL over HTTP GET with a bearer token, but only if the URL matches the "
        "configured base URL (case-insensitively). Returns the raw response body text. "
        "Intended primarily for Web Server instances using PAT authentication."
    ),
)
def webfetch(url: str) -> str:
    """Fetch ``url`` over HTTP GET, sending a bearer token, if ``url`` is allowed.

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
    """
    assert isinstance(url, str), type(url)
    assert url.strip()

    base_url, bearer_token = _webfetch_config()

    if not url.casefold().startswith(base_url.casefold()):
        raise WebfetchUrlNotAllowedError(f"URL {url!r} does not match the configured base URL {base_url!r}.")

    response = httpx.get(
        url,
        headers={"Authorization": f"Bearer {bearer_token}"},
        follow_redirects=True,
        timeout=_REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    result = response.text
    return result
