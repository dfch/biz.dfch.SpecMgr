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

"""Pydantic model for one line of ADR listing output (plan §8, §9a)."""

from __future__ import annotations

from pydantic import BaseModel


class AdrSummary(BaseModel):
    """One line of ``list_adrs``/``specmgr://adr/list`` output (plan §8, §9a).

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier, or ``None`` if the file
        has not been assigned one yet (e.g. hand-authored without the
        ``id`` frontmatter key -- plan §9a).
    title:
        The ADR's ``# {title}`` H1.
    status:
        The ADR's ``frontmatter.status`` value, verbatim.
    filename:
        The on-disk file's base name (e.g. ``"<uuid>-a-title.md"``), not a
        full path -- callers already know the configured ADR base directory.
    """

    id: str | None
    title: str
    status: str
    filename: str
