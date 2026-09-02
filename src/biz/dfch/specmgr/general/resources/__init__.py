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
owned by ``vcr``'s own schema. ``rasci`` registers the generic RASCI
responsibility-assignment guidance resource (``specmgr://rasci``,
REQ-011) -- motivated by the ``sop`` domain but not scoped to it, mirroring
``iso25010``'s cross-cutting placement rather than ``rsk/tara``'s
domain-scoped one. ``config`` registers the ``specmgr://config`` diagnostic
resource (feat-51-mcp-cwd REQ-001) -- the resolved absolute base directory
and env-var-set flag for all twelve document domains, so a client can
self-diagnose a CWD/env-var misconfiguration without shell access to the
server's host; it never discloses the value of any environment variable,
only whether a domain's own ``SPECMGR_*_DIR`` is set (REQ-002). Domain-specific
resources (e.g. ``adr_list``/``adr_get``)
live under their own domain package instead (``biz.dfch.specmgr.adr.resources``).
Import this package to load all cross-cutting resources at once::

    from biz.dfch.specmgr.general import resources  # noqa: F401 (side-effects only)
"""

from . import config, dtais, iso25010, rasci, version  # noqa: F401

__all__ = [
    "config",
    "dtais",
    "iso25010",
    "rasci",
    "version",
]
