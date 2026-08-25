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

"""Problem Statement (PRB) domain -- Six-Sigma-style problem statement specifications.

This is a domain-first package, mirroring ``tsk``/``qa``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), containing models (and, in later
phases, tools, prompts, and resources) for managing ``prb`` documents.

Only ``models`` exists so far (`.specmgr/feat/feat-16-problem-statement/README.md`
Phase 1: Specification) -- this package intentionally does not yet import
``prompts``/``resources``/``tools`` sub-packages, since none exist yet.
"""

__all__: list[str] = []
