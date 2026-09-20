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

"""Shared test fixtures for the per-tool ``dec.tools.*`` test modules.

Not itself a ``test_*.py`` module -- imported by the individual per-tool
test files under this directory so the now-mandatory `## Roles and
Responsibilities` + `## Source` block (feat-29-dec-source-roles, GitHub
issue #29) is not duplicated verbatim across every fixture that builds its
own minimal ``dec`` body text.
"""

from __future__ import annotations

#: The mandatory `## Roles and Responsibilities` (`### Accountable` +
#: `### Responsible`) and `## Source` sections, as a markdown snippet. Carries
#: both a leading and a trailing newline -- the leading `\n` lets a caller
#: concatenate this directly onto fixture text that already ends in a single
#: `\n`, producing the blank line markdown needs between sections, without
#: the caller having to add its own trailing blank line first. Append after
#: the `## Decision Outcome` section's own content in a hand-built minimal
#: `dec` body fixture.
MANDATORY_ROLES_AND_SOURCE = (
    "\n"
    "## Roles and Responsibilities\n"
    "\n"
    "### Accountable\n"
    "\n"
    "The platform architecture lead.\n"
    "\n"
    "### Responsible\n"
    "\n"
    "- The order service team.\n"
    "\n"
    "## Source\n"
    "\n"
    "The customer dashboard latency incident review meeting.\n"
)
