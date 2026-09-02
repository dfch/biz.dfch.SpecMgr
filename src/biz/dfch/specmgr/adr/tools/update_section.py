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

"""``@mcp.tool()`` wrapper: update_section (plan §4, §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter over
``models.adr.v1.mutations.update_section``: re-reads and re-parses the
current on-disk state, then re-renders and re-writes the full file; there
is no in-memory cache of a parsed :class:`Adr` (plan §7, §9a): the ``.md``
file itself is always the source of truth. The whole sequence runs
under ``_lock.adr_lock(id)`` so a concurrent mutation against the same
id cannot interleave with it and cause a lost update.

``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
because the pure, in-memory operation it delegates to shares this
wrapper's own name.
"""

from __future__ import annotations

from ...models.adr import Adr
from ...models.adr.v1 import mutations
from ...server import mcp
from ._io import load_by_id, write_adr
from ._lock import adr_lock
from ._paths import adr_base_dir


@mcp.tool(
    name="update_section",
    title="Update ADR Section",
    description="Whole-section replace/delete of one AdrBody field (plan §4).",
)
def update_section(id: str, key: str, value: str) -> Adr:
    """Replace (or, via a deletion sentinel, clear) one whole-section field.

    Delegates to ``models.adr.v1.mutations.update_section`` (plan §4):
    ``value`` being blank/whitespace-only or the literal ``"REMOVE"``
    (case-insensitive) clears the section, unless ``key`` names a
    mandatory field, in which case ``AdrSectionError`` is raised and
    nothing is written. Lets ``AdrSectionError``/``pydantic.ValidationError``
    propagate unmodified -- this tool does not catch or wrap them.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    key:
        An ``AdrBody`` field name, e.g. ``"decision_drivers"``. ``"options"``
        is rejected -- use the ``option_*`` tools instead.
    value:
        The new section text, or a deletion sentinel.

    Returns
    -------
    Adr
        The updated document.
    """
    base_dir = adr_base_dir()
    with adr_lock(id):
        path, adr = load_by_id(base_dir, id)
        new_adr = mutations.update_section(adr, key, value)
        write_adr(path, new_adr)
    return new_adr
