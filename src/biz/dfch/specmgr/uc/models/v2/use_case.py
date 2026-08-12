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

from biz.dfch.specmgr.models.md import (
    MarkdownSection1,
    MarkdownSection2,
    MarkdownSection3,
    MarkdownParagraph,
    MarkdownListItem,
)
from biz.dfch.specmgr.models.md import alias, AliasType

# 'Characteristic Information' [required]


@alias(value="Goal in Context", type=AliasType.LITERAL)
class GoalInContext(MarkdownSection3):
    body: list[MarkdownParagraph]


class Scope(MarkdownSection3):
    body: list[MarkdownParagraph]


class Level(MarkdownSection3):
    body: list[MarkdownParagraph]


class Precondition(MarkdownSection3):
    items: list[MarkdownListItem]


class SuccessEndCondition(MarkdownSection3):
    items: list[MarkdownListItem]


class FailedEndCondition(MarkdownSection3):
    items: list[MarkdownListItem]


class PrimaryActor(MarkdownSection3):
    body: list[MarkdownParagraph]


class SecondaryActors(MarkdownSection3):
    items: list[MarkdownListItem]


class Trigger(MarkdownSection3):
    body: list[MarkdownParagraph]


class Frequency(MarkdownSection3):
    body: list[MarkdownParagraph]


class Priority(MarkdownSection3):
    body: list[MarkdownParagraph]


class PerformanceTarget(MarkdownSection3):
    body: list[MarkdownParagraph]


class ChannelsToPrimaryActor(MarkdownSection3):
    items: list[MarkdownListItem]


class ChannelsToSecondaryActors(MarkdownSection3):
    items: list[MarkdownListItem]


class RelatedUseCases(MarkdownSection3):
    items: list[MarkdownListItem]


class CharacteristicInformation(MarkdownSection2):
    goal_in_context: GoalInContext
    scope: Scope
    level: Level
    precondition: Precondition
    success_end_condition: SuccessEndCondition
    failed_end_condition: FailedEndCondition | None = None
    primary_actor: PrimaryActor
    secondary_actors: SecondaryActors | None = None
    trigger: Trigger
    frequency: Frequency | None = None
    priority: Priority | None = None
    performance_target: PerformanceTarget | None = None
    channels_to_primary_actor: ChannelsToPrimaryActor | None = None
    channels_to_secondary_actors: ChannelsToSecondaryActors | None = None
    related_use_cases: RelatedUseCases | None = None


# 'Main Success Scenario' [required]


class MainSuccessScenario(MarkdownSection2):
    steps: list[MarkdownListItem]


# 'Extensions' [required]


class ExtensionItem(MarkdownListItem):
    # The leading paragraph of item is in `.text` property.
    notes: list[MarkdownParagraph] | None = None


@alias(value=r"^Extension \d+[a-z]?\. .+$", type=AliasType.REGEX)
class Extension(MarkdownSection3):
    items: list[ExtensionItem]


class Extensions(MarkdownSection2):
    intro: MarkdownParagraph | None = None
    extensions: list[Extension] | None = None


# 'Sub-Variations' [optional]


@alias(value=r"^Step \d+: .+$", type=AliasType.REGEX)
class SubVariation(MarkdownSection3):
    items: list[MarkdownListItem]


@alias(value="Sub-Variations", type=AliasType.LITERAL)
class SubVariations(MarkdownSection2):
    sub_variations: list[SubVariation] | None = None


# 'Open Issues' [optional]


class OpenIssues(MarkdownSection2):
    items: list[MarkdownListItem]


# 'Related Information' [optional]


class Notes(MarkdownSection3):
    items: list[MarkdownListItem]


class Assumptions(MarkdownSection3):
    items: list[MarkdownListItem]


class RelatedInformation(MarkdownSection2):
    notes: Notes | None = None
    assumptions: Assumptions | None = None


@alias(value=r".+", type=AliasType.REGEX)
class UseCase(MarkdownSection1):
    characteristic_information: CharacteristicInformation
    main_success_scenario: MainSuccessScenario
    extensions: Extensions | None = None
    sub_variations: SubVariations | None = None
    open_issues: OpenIssues | None = None
    related_information: RelatedInformation | None = None
