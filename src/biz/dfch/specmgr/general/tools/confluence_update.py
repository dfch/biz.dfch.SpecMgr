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

"""``@mcp.tool()`` wrapper: confluence_update (ADR a156fdf9-052c-4f43-93a2-eeec04a91eac,
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
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx
from markdown_it import MarkdownIt

from ...server import mcp
from ._confluence_config import confluence_config
from ._confluence_url import (
    assert_same_host_as_base_url,
    build_rest_content_url,
    looks_like_tiny_link,
    resolve_page_id,
)
from .confluence_fetch import ConfluenceTinyLinkNotSupportedError

__all__ = [
    "ConfluencePageIdNotResolvedError",
    "ConfluenceUnexpectedResponseShapeError",
    "confluence_update",
]

#: Request timeout, in seconds, for the underlying ``httpx.get``/``httpx.put`` calls.
_REQUEST_TIMEOUT_SECONDS = 30.0

#: The ``expand`` value used for the version/title lookup GET (REQ-008/ACC-006);
#: ``body.storage`` is deliberately omitted since Phase 3 never reads the
#: existing body.
_VERSION_TITLE_EXPAND = "version,title"

#: A local ``MarkdownIt`` instance, not the shared ``models.md._markdown.md``
#: instance -- that module is private to ``models/md/`` (not re-exported via
#: ``models.md.__all__``) and is not intended for reuse outside that
#: package's own parser pipeline (e.g. its `parse()` wrapper additionally
#: rejects raw HTML, a constraint irrelevant here). Confirmed via
#: ``MarkdownIt().render()``'s own behavior: it emits a bare HTML fragment
#: with no ``<html>``/``<head>``/``<body>`` wrapper, exactly what Confluence's
#: storage representation requires.
_MD = MarkdownIt("commonmark")

#: Confluence content type for a page (as opposed to e.g. a blog post),
#: required by the REST API on every ``PUT`` even when unchanged.
_CONFLUENCE_CONTENT_TYPE = "page"

#: Confluence body representation used for the rendered HTML fragment.
_CONFLUENCE_STORAGE_REPRESENTATION = "storage"


class ConfluencePageIdNotResolvedError(ValueError):
    """``page_url_or_id`` could not be resolved to a numeric Confluence page id."""


class ConfluenceUnexpectedResponseShapeError(RuntimeError):
    """A Confluence REST API response is missing an expected ``version``/``title`` key."""


def _resolve_page_id(page_url_or_id: str) -> str:
    """Resolve ``page_url_or_id`` to a numeric page id, or raise a clear error.

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
    """
    if looks_like_tiny_link(page_url_or_id):
        raise ConfluenceTinyLinkNotSupportedError(
            f"URL {page_url_or_id!r} is a Confluence tiny link ('/x/<tinyid>'), which cannot be "
            "resolved to a page id without an authenticated browser session; use the full page "
            "URL, a REST content URL, or a bare page id instead."
        )

    page_id = resolve_page_id(page_url_or_id)
    if page_id is None:
        raise ConfluencePageIdNotResolvedError(
            f"Could not resolve {page_url_or_id!r} to a Confluence page id; expected a bare "
            "numeric id, a browsable page URL ('/pages/<id>/...' or '?pageId=<id>'), or a REST "
            "content URL ('/rest/api/content/<id>')."
        )
    return page_id


def _read_version_and_title(payload: dict[str, Any]) -> tuple[int, str]:
    """Extract ``version.number`` and ``title`` from a GET response's JSON payload.

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
    """
    assert isinstance(payload, dict), type(payload)

    version = payload.get("version")
    if not isinstance(version, dict) or "number" not in version:
        raise ConfluenceUnexpectedResponseShapeError(
            f"Confluence response is missing a 'version.number' field: {payload!r}"
        )
    if "title" not in payload:
        raise ConfluenceUnexpectedResponseShapeError(f"Confluence response is missing a 'title' field: {payload!r}")

    version_number = version["number"]
    title = payload["title"]
    return version_number, title


@mcp.tool(
    name="confluence_update",
    title="Update a Confluence page's body from a local Markdown file",
    description=(
        "Render a local Markdown file to an HTML fragment and write it into an existing "
        "Confluence page's body via the REST API, incrementing the page's version number. "
        "Accepts a bare numeric page id, a browsable page URL ('/pages/<id>/...' or "
        "'?pageId=<id>'), or a REST content URL; a '/x/<tinyid>' tiny link is rejected. Reuses "
        "the same two environment variables confluence_fetch uses. Local-image attachment upload "
        "and <img> -> <ac:image> macro rewriting are not yet supported (planned for a later "
        "phase) -- the rendered HTML is written as-is."
    ),
)
def confluence_update(page_url_or_id: str, markdown_file_path: str) -> dict[str, Any]:
    """Write ``markdown_file_path``'s rendered content into the Confluence page identified by ``page_url_or_id``.

    Resolves ``page_url_or_id`` to a numeric page id, ``GET``\\ s the page's
    current ``version.number``/``title``, renders the Markdown file at
    ``markdown_file_path`` to an HTML fragment, then ``PUT``\\ s the
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
    """
    assert isinstance(page_url_or_id, str), type(page_url_or_id)
    assert page_url_or_id.strip()
    assert isinstance(markdown_file_path, str), type(markdown_file_path)
    assert markdown_file_path.strip()

    base_url, bearer_token = confluence_config()
    page_id = _resolve_page_id(page_url_or_id)

    headers = {"Authorization": f"Bearer {bearer_token}"}

    get_url = build_rest_content_url(base_url, page_id, expand=_VERSION_TITLE_EXPAND)
    get_response = httpx.get(
        get_url,
        headers=headers,
        follow_redirects=True,
        timeout=_REQUEST_TIMEOUT_SECONDS,
    )
    get_response.raise_for_status()
    assert_same_host_as_base_url(get_url, get_response.url, base_url)

    version_number, title = _read_version_and_title(get_response.json())
    new_version = version_number + 1

    markdown_text = Path(markdown_file_path).read_text(encoding="utf-8")
    html_fragment = _MD.render(markdown_text)

    put_url = build_rest_content_url(base_url, page_id)
    put_payload = {
        "version": {"number": new_version},
        "title": title,
        "type": _CONFLUENCE_CONTENT_TYPE,
        "body": {
            "storage": {
                "value": html_fragment,
                "representation": _CONFLUENCE_STORAGE_REPRESENTATION,
            }
        },
    }
    put_response = httpx.put(
        put_url,
        headers=headers,
        json=put_payload,
        follow_redirects=True,
        timeout=_REQUEST_TIMEOUT_SECONDS,
    )
    put_response.raise_for_status()
    assert_same_host_as_base_url(put_url, put_response.url, base_url)

    result = {"id": page_id, "title": title, "version": new_version}
    return result
