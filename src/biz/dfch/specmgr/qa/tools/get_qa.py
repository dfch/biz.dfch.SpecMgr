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

# pylint: disable=redefined-builtin  # id/type intentionally shadow the builtins: public tool API, issue #41

"""``@mcp.tool()`` wrapper: get_qa (Phase 4, Task 4.1).

Mirrors ``adr.tools.get_adr``/``req.tools.get_req`` -- a thin
file-I/O/id-lookup adapter that re-reads and re-parses the current on-disk
state on every call; there is no in-memory cache of a parsed
:class:`QaDocument`: the ``.md`` file itself is always the source of truth.

There is no ``specmgr://qa/{id}`` resource -- id-based reads go through
this tool only, mirroring REQ's own choice; see ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614 ("Expose id-based REQ document reads as
a tool (get_req), not a resource") for the full rationale.

``raw=True`` (feat-22-consolidate-mutation-tools, Phase 2) returns the
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

from ...general.tools._path_safety import assert_within, validate_id
from ...general.tools._splice import body_text, window_body
from ...server import mcp
from ..models.v2 import QaDocument
from ._io import load_by_id
from ._paths import qa_base_dir


@mcp.tool(
    name="get_qa",
    title="Get QA document",
    description=(
        "Read, parse, and return a full QA document (frontmatter and body) by its id. "
        "Pass raw=True to return the frontmatter-stripped body text verbatim instead. With "
        "raw=True, optional read-style `offset`/`limit` window the raw read: `offset` (1-based, "
        "default 1) is the first body line to return, `limit` (line count, default through end "
        "of body) how many; out-of-range values clamp (`offset > N` returns the empty string), "
        "and coordinates with raw=False raise ValueError."
        " An invalid id (path-injection attempt "
        "or wrong format) is also a ValueError, raised before any file access."
    ),
)
def get_qa(id: str, raw: bool = False, offset: int | None = None, limit: int | None = None) -> QaDocument | str:
    """Read and return the Question and Answer (QA) document identified by ``id``.

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
    QaDocument | str
        With ``raw=False``: the current on-disk document, freshly re-read
        and re-parsed. With ``raw=True``: the body text (or its
        ``offset``/``limit`` window) as a plain string.
        Raises :class:`._paths.QaNotFoundError` if no QA document has this id.

    Raises
    ------
    ValueError
        ``id`` is a path-injection attempt or not a well-formed id for this domain
        (raised before any filesystem access), or ``offset``/``limit`` coordinates
        are given with ``raw=False`` (a parsed document requires the whole body;
        also raised before any file access).
    """
    validate_id("qa", id)
    if not raw and (offset is not None or limit is not None):
        raise ValueError(f"offset/limit are only valid with raw=True, got offset={offset!r}, limit={limit!r}")

    base_dir = qa_base_dir()
    path, doc = load_by_id(base_dir, id)
    assert_within(base_dir, path)
    if raw:
        text = body_text(path)
        if offset is None and limit is None:
            result: QaDocument | str = text
            return result
        result = window_body(text, offset if offset is not None else 1, limit)
        return result
    result = doc
    return result
