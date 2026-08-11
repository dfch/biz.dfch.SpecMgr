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

"""Test-only fixture model tree exercising `MarkdownSection1`/`2`/`3` nesting.

Not production code: this proves out the generic recursive `from_text`
mechanics (`feat-5-md-model-parser`) end-to-end via a small, hand-built
document model. It lives under `tests/` rather than `src/` for that reason.
"""

from __future__ import annotations

from biz.dfch.specmgr.models.md.alias import alias, AliasType
from biz.dfch.specmgr.models.md.markdown_section1 import MarkdownSection1
from biz.dfch.specmgr.models.md.markdown_section2 import MarkdownSection2
from biz.dfch.specmgr.models.md.markdown_section3 import MarkdownSection3


@alias(value="*Goal* In Context", type=AliasType.LITERAL)
class GoalInContext(MarkdownSection3): ...


class Scope(MarkdownSection3): ...


class CharacteristicInformation(MarkdownSection2):
    goal_in_context: GoalInContext
    scope: Scope


class Notes(MarkdownSection3): ...


class Assumptions(MarkdownSection3): ...


class RelatedInformation(MarkdownSection2):
    notes: Notes
    assumptions: Assumptions


@alias(value=".+", type=AliasType.REGEX)
class MainDocument(MarkdownSection1):
    characteristic_information: CharacteristicInformation
    related_information: RelatedInformation
