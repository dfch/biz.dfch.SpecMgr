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

"""``@mcp.tool()`` wrapper: delete_dec (Task 2.2).

Registered stub only -- reserves the ``delete_dec`` name/slot in the DEC
lifecycle tool surface without committing to a deletion strategy yet
(soft-delete via ``status``, archival, hard removal from disk, or something
else -- undecided, matching the other six domains' own ``delete_*`` stubs,
a shared cross-domain decision deferred to future work). Always raises
``NotImplementedError`` unconditionally, without resolving ``id`` or
touching the filesystem at all, so it cannot be mistaken for a working
no-op.
"""

from __future__ import annotations

from typing import NoReturn

from ...server import mcp


@mcp.tool(
    name="delete_dec",
    title="Delete decision (not yet implemented)",
    description="Stub only -- always raises NotImplementedError. Reserves the name for a future implementation.",
    # `NoReturn` has no pydantic-serializable schema; this stub never returns anyway, so
    # skip structured-output schema derivation entirely rather than lying with a fake return type.
    structured_output=False,
)
def delete_dec(id: str) -> NoReturn:
    """Always raise ``NotImplementedError``; deletion is not yet implemented.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier. Unused -- accepted only
        to fix this tool's future signature; never resolved or validated.

    Raises
    ------
    NotImplementedError
        Always.
    """
    raise NotImplementedError("delete_dec is not yet implemented")
