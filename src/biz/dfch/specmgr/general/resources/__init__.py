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

"""MCP resource registrations that are not specific to any single document
domain.

See ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by document-type domain".

``version`` registers the server package version resource. ``iso25010``
registers the ISO/IEC 25010:2023 product quality model resource. ``dtais``
registers the DTAIS verification-method vocabulary resource
(``specmgr://dtais``, feat-33-vcr REQ-006) -- cross-cutting domain
knowledge for ``vcr``'s ``## Acceptance Criteria`` method vocabulary, not
owned by ``vcr``'s own schema. Domain-specific resources (e.g.
``adr_list``/``adr_get``) live under their own domain package instead
(``biz.dfch.specmgr.adr.resources``). Import this package to load all
cross-cutting resources at once::

    from biz.dfch.specmgr.general import resources  # noqa: F401 (side-effects only)
"""

from . import dtais, iso25010, version  # noqa: F401

__all__ = [
    "dtais",
    "iso25010",
    "version",
]
