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

"""``@mcp.tool()`` wrapper: get_tsk (Task 3.8).

Mirrors ``req.tools.get_req`` -- a thin file-I/O/id-lookup adapter that
re-reads and re-parses the current on-disk state on every call; there is no
in-memory cache of a parsed :class:`TskDocument`: the ``.md`` file itself is
always the source of truth.

Implemented as a tool, not a resource, from the start -- id-based single-
document reads for TSK never had a ``specmgr://tsk/{id}`` resource in the
first place, matching REQ's own revisited conclusion (ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614: "Expose id-based REQ document reads as
a tool (get_req), not a resource").

``raw=True`` (feat-22-consolidate-mutation-tools, Phase 2) returns the
frontmatter-stripped body text verbatim instead of the parsed document --
produced by the same
:func:`~biz.dfch.specmgr.general.tools._splice.body_text` helper the
generic ``update`` tool's range splice uses, so the line numbers a client
counts in a raw read index byte-for-byte into the text the server splices
against.
"""

from __future__ import annotations

from ...general.tools._path_safety import assert_within, validate_id
from ...general.tools._splice import body_text
from ...server import mcp
from ..models.v1 import TskDocument
from ._io import load_by_id
from ._paths import tsk_base_dir


@mcp.tool(
    name="get_tsk",
    title="Get task list",
    description=(
        "Read, parse, and return a full task list document (frontmatter and body) by its id. "
        "Pass raw=True to return the frontmatter-stripped body text verbatim instead. "
        "An invalid id (path-injection attempt or wrong format) is a ValueError raised before any file access."
    ),
)
def get_tsk(id: str, raw: bool = False) -> TskDocument | str:
    """Read and return the task list identified by ``id``.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    raw:
        With ``False`` (the default), return the parsed document, exactly
        as before. With ``True``, return the frontmatter-stripped body
        text verbatim as a plain string -- the same text whose 1-based
        lines the generic ``update`` tool's ``begin``/``end`` coordinates
        address (shared body-extraction helper with the splice).

    Returns
    -------
    TskDocument | str
        With ``raw=False``: the current on-disk document, freshly re-read
        and re-parsed. With ``raw=True``: the body text as a plain string.
        Raises :class:`._paths.TskNotFoundError` if no task list has this id.

    Raises
    ------
    ValueError
        ``id`` is a path-injection attempt or not a well-formed id for this domain
        (raised before any filesystem access).
    """
    validate_id("tsk", id)
    base_dir = tsk_base_dir()
    path, doc = load_by_id(base_dir, id)
    assert_within(base_dir, path)
    if raw:
        result: TskDocument | str = body_text(path)
        return result
    result = doc
    return result
