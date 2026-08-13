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

"""
Requirement (REQ) models.
"""

from ....models.md import (
    MarkdownSection1,
    MarkdownSection2,
    MarkdownSection3,
    MarkdownParagraph,
    MarkdownListItem,
    alias,
    AliasType,
)


class Description(MarkdownSection2): ...


class Characteristics(MarkdownSection2):
    items: list[MarkdownListItem]


class Level(MarkdownSection2):
    value: MarkdownParagraph


class Priority(MarkdownSection2):
    value: MarkdownParagraph


class Tags(MarkdownSection2):
    items: list[MarkdownListItem]


class Source(MarkdownSection2):
    value: MarkdownParagraph


class Requirements(MarkdownSection3):
    items: list[MarkdownListItem]


class Decisions(MarkdownSection3):
    items: list[MarkdownListItem]


class AcceptanceCriteria(MarkdownSection3):
    items: list[MarkdownListItem]


class Goals(MarkdownSection3):
    items: list[MarkdownListItem]


class RelatedArtifacts(MarkdownSection2):
    requirements: Requirements | None = None
    decisions: Decisions | None = None
    goals: Goals | None = None
    acceptance_criteria: AcceptanceCriteria | None = None


class MoreInformation(MarkdownSection2): ...


class Notes(MarkdownSection2): ...


@alias(value=".+", type=AliasType.REGEX)
class Requirement(MarkdownSection1):
    statement: MarkdownParagraph
    description: Description
    characteristics: Characteristics
    level: Level
    priority: Priority | None = None
    tags: Tags | None = None
    source: Source
    related_artifacts: RelatedArtifacts | None = None
    more_information: MoreInformation | None = None
    notes: Notes | None = None
