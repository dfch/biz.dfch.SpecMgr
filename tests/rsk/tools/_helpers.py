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

"""Shared test fixtures for the per-tool ``rsk.tools.*`` test modules.

Not itself a ``test_*.py`` module -- imported by the individual per-tool
test files under this directory so the now-mandatory `## Source` section
(feat-102-133-rsk-tags-source, GitHub issues #102 + #133) is not duplicated
verbatim across every fixture that builds its own minimal ``rsk`` body text.
"""

from __future__ import annotations

#: The mandatory `## Source` section, as a markdown snippet. Carries both a
#: leading and a trailing newline -- the leading `\n` lets a caller
#: concatenate this directly onto fixture text that already ends in a single
#: `\n`, producing the blank line markdown needs between sections, without
#: the caller having to add its own trailing blank line first. Append after
#: the `## Residual Assessment` section's own content (or after `## Tags`/
#: `## Owner` when present) in a hand-built minimal `rsk` body fixture.
MANDATORY_SOURCE = "\n## Source\n\nThe QA interview on 2026-09-17 that elicited this risk.\n"
