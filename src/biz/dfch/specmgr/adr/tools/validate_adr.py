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

"""``@mcp.tool()`` wrapper: validate_adr (plan §7, §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter -- re-reads and re-parses the current
on-disk state on every call; there is no in-memory cache of a parsed
:class:`Adr` (plan §7, §9a): the ``.md`` file itself is always the source
of truth.
"""

from __future__ import annotations

from ...server import mcp
from ._io import load_by_id
from ._paths import adr_base_dir


@mcp.tool(
    name="validate_adr",
    title="Validate ADR",
    description="Re-read and re-parse an ADR by id, letting the models' own Pydantic validators run.",
)
def validate_adr(id: str) -> bool:
    """Validate the ADR identified by ``id``.

    "Validate" is simply letting :class:`Adr`/:class:`AdrBody`/
    :class:`AdrFrontmatter`'s own Pydantic validators run during parsing
    (plan §7): there is no separate validation pass here. Successfully
    constructing the :class:`Adr` *is* the validation, so this function
    only ever returns ``True`` -- it never returns ``False``. Any parse or
    validation failure instead propagates as
    ``AdrParseError``/``pydantic.ValidationError`` (not caught or wrapped
    here), so the MCP layer reports it naturally as a tool error, giving
    the LLM the underlying message to self-correct from.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.

    Returns
    -------
    bool
        Always ``True`` on success.
    """
    base_dir = adr_base_dir()
    load_by_id(base_dir, id)
    return True
