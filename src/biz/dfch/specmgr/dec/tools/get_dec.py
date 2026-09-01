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

"""``@mcp.tool()`` wrapper: get_dec (Task 2.2).

Mirrors ``gol.tools.get_gol`` -- a thin file-I/O/id-lookup adapter that
re-reads and re-parses the current on-disk state on every call; there is no
in-memory cache of a parsed :class:`DecDocument`: the ``.md`` file itself is
always the source of truth.

This tool is the sole id-based read path for DEC: there is no
``specmgr://dec/{id}`` resource (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614,
same reasoning as GOL/REQ/UC/TSK/QA/PRB's own ``get_*`` tools).

``raw=True`` (feat-22-consolidate-mutation-tools, Phase 8) returns the
frontmatter-stripped body text verbatim instead of the parsed document --
produced by the same
:func:`~biz.dfch.specmgr.general.tools._splice.body_text` helper the
generic ``update`` tool's range splice uses, so the line numbers a client
counts in a raw read index byte-for-byte into the text the server splices
against. With optional read-style ``offset``/``limit`` coordinates
(feat-28-get-update, Phase 2), the same raw read instead returns the window
of that text, served by the shared
:func:`~biz.dfch.specmgr.general.tools._splice.window_body` helper (clamping
out-of-range values, never erroring).
"""

from __future__ import annotations

from ...general.tools._splice import body_text, window_body
from ...server import mcp
from ..models.v1 import DecDocument
from ._io import load_by_id
from ._paths import dec_base_dir


@mcp.tool(
    name="get_dec",
    title="Get decision",
    description=(
        "Read, parse, and return a full decision document (frontmatter and body) by its id. "
        "Pass raw=True to return the frontmatter-stripped body text verbatim instead. With "
        "raw=True, optional read-style `offset`/`limit` window the raw read: `offset` (1-based, "
        "default 1) is the first body line to return, `limit` (line count, default through end "
        "of body) how many; out-of-range values clamp (`offset > N` returns the empty string), "
        "and coordinates with raw=False raise ValueError."
    ),
)
def get_dec(id: str, raw: bool = False, offset: int | None = None, limit: int | None = None) -> DecDocument | str:
    """Read and return the decision identified by ``id``.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    raw:
        With ``False`` (the default), return the parsed document, exactly
        as before. With ``True``, return the frontmatter-stripped body
        text verbatim as a plain string -- the same text whose 1-based
        lines the generic ``update`` tool's ``offset``/``limit``
        coordinates address (shared body-extraction helper with the
        splice) -- optionally windowed by ``offset``/``limit`` (see below).
    offset:
        With ``raw=True`` only: the 1-based first body line of the window
        to return (default 1; values below 1 floor to 1, values past the
        last body line return the empty string).
    limit:
        With ``raw=True`` only: the number of body lines the window spans
        (default through the end of the body; capped at the remaining
        lines, a negative value returns the empty string).

    Returns
    -------
    DecDocument | str
        With ``raw=False``: the current on-disk document, freshly re-read
        and re-parsed. With ``raw=True``: the body text (or its
        ``offset``/``limit`` window) as a plain string.
        Raises :class:`._paths.DecNotFoundError` if no decision has this id.

    Raises
    ------
    ValueError
        ``offset``/``limit`` coordinates with ``raw=False`` -- a parsed
        document requires the whole body; raised before any file access.
    """
    if not raw and (offset is not None or limit is not None):
        raise ValueError(f"offset/limit are only valid with raw=True, got offset={offset!r}, limit={limit!r}")

    base_dir = dec_base_dir()
    path, doc = load_by_id(base_dir, id)
    if raw:
        text = body_text(path)
        if offset is None and limit is None:
            result: DecDocument | str = text
            return result
        result = window_body(text, offset if offset is not None else 1, limit)
        return result
    result = doc
    return result
