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

"""Shared, private validation helpers for the ``models.adr`` subpackage."""

from __future__ import annotations


def blank_to_none(value: str | None) -> str | None:
    """Normalize a blank/whitespace-only string to ``None``.

    Used by optional frontmatter/body fields so that "absent" and
    "whitespace-only" are treated as the same state, consistent with the
    render-time rule that an absent optional section omits its heading.
    """
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return value
