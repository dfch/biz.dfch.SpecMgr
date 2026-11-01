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

"""Import-free, stdlib-only PlantUML support library (feat-185-uc-diagrams, Phase 110).

The cross-cutting package that turns specmgr-emitted PlantUML source into
verdicts: the classic URL text encoder (``encode`` — the ``SoWkI…`` form,
rulebook §5.1), the two-mode structure
checker plus the shared UNATTRIBUTED marker constant (``structure``), the
jar/bin local backends (``backends``), the single-endpoint URL protocol
classifier (``url``), and the strict first-set-wins validation chain with
its non-raising result model (``chain``).

**Import-free:** no ``biz.dfch.specmgr.*`` import anywhere in this package
(the dependency direction is always specmgr-domain → ``plantuml``, never the
reverse), and **stdlib-only** (no new dependency or extra; ``pyproject.toml``
is unchanged). Both properties keep extraction as a standalone library cheap
if the subset contract ever outgrows specmgr (ADR
7a626b12-b189-4561-a51d-ffb2e9e193b4). It is deliberately not a separate
PyPI library: the structure checker's contract is specmgr's emitted subset,
and consuming projects already depend on specmgr (one published artifact).

The normative spec for everything here is the rulebook served as
``specmgr://uc/plantuml`` (``uc/data/uc_plantuml.md``): the invocation
contract (§4), the URL protocol matrix (§5), the structure checker contract
(§6), and the chain semantics (§3).
"""

from . import backends, chain, encode, structure, url
from .chain import PlantumlValidationResult, validate_plantuml

__all__ = [
    "PlantumlValidationResult",
    "backends",
    "chain",
    "encode",
    "structure",
    "url",
    "validate_plantuml",
]
