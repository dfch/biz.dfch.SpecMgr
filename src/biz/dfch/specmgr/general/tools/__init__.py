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

"""MCP tool wrappers for general-purpose utilities (mirrors ``adr/tools/``'s shape).

``mdformat`` -- a markdown document formatter that preserves YAML frontmatter
blocks (for ADR/UC files) and formats only the body markdown. ``update`` --
the generic, cross-domain whole-body or line-range replace for the seven
whole-body document types (``type`` is one of req/uc/tsk/qa/prb/gol/rsk;
optional 1-based inclusive body-line ``begin``/``end`` range with the
``N+1`` end-of-body sentinel). ``set_status`` -- the generic, cross-domain
status change for all eight document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/adr; ``superseded_by`` is ``adr``-only, composing
the status as ``"superseded by {superseded_by}"``). ``delete`` -- the
generic, cross-domain hard-delete for the eleven whole-body document types
(``type`` is one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr; ``adr`` is
not supported), resolving the document by ``id``, taking the domain's own
per-id lock, and removing it from disk (the single ``*.md`` file for the
ten flat domains, the entire ``<base>/<id>/`` folder for ``feat``),
returning the deleted path as a string. ``confluence_fetch`` (renamed from
``webfetch``, ADR a156fdf9-052c-4f43-93a2-eeec04a91eac) -- a
bearer-authenticated HTTP GET fetch restricted to a configured Confluence
base URL; automatically converts a normal, browsable Confluence page URL
(Cloud-style ``/pages/<id>/<title>`` or Server-style ``?pageId=<id>``) into
the equivalent ``{base}/rest/api/content/{id}?expand=body.storage`` REST
API URL, rejects ``/x/<tinyid>`` tiny links outright, raises on an
SSO-redirect off the configured base URL's host, and downloads
non-text/binary content (e.g. images) to a caller-supplied
``destination_path`` instead of returning it as text. ``confluence_update``
(ADR a156fdf9-052c-4f43-93a2-eeec04a91eac, feat-50-confluence Phases 3-4) --
writes a local Markdown file's rendered HTML into an existing Confluence
page's body via the REST API: resolves ``page_url_or_id`` (bare page id,
browsable page URL, or REST content URL) to a page id, ``GET``\\ s the
page's current ``version.number``/``title``, renders the Markdown file via
``markdown-it-py``, best-effort uploads every local image the Markdown
references as a Confluence attachment (``POST .../child/attachment``,
falling back to updating an existing attachment's content if the filename
already exists) and rewrites the corresponding ``<img>`` tags into
Confluence's ``<ac:image>``/``<ri:attachment>`` storage-format macro, then
``PUT``\\ s the incremented version with that (possibly rewritten) HTML
fragment as the new body.
Import this package to register all general tools at once::

    from biz.dfch.specmgr.general import tools  # noqa: F401 (side-effects only)
"""

from .confluence_fetch import confluence_fetch
from .confluence_update import confluence_update
from .delete import delete
from .mdformat import mdformat
from .set_status import set_status
from .update import update

__all__ = [
    "confluence_fetch",
    "confluence_update",
    "delete",
    "mdformat",
    "set_status",
    "update",
]
