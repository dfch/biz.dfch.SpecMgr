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

import re

from pydantic import model_validator

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


class Preconditions(MarkdownSection3):
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


@alias(value="Channels to Primary Actor", type=AliasType.LITERAL)
class ChannelsToPrimaryActor(MarkdownSection3):
    items: list[MarkdownListItem]


@alias(value="Channels to Secondary Actors", type=AliasType.LITERAL)
class ChannelsToSecondaryActors(MarkdownSection3):
    items: list[MarkdownListItem]


class RelatedUseCases(MarkdownSection3):
    items: list[MarkdownListItem]


class CharacteristicInformation(MarkdownSection2):
    goal_in_context: GoalInContext
    scope: Scope
    level: Level
    preconditions: Preconditions
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


# `Extension`/`SubVariation` heading text (`.text`) carries the step reference
# structurally (e.g. "Extension 3a. ..." / "Step 1: ..."), extracted here for the
# cross-reference check below -- see `Extension`/`SubVariation`'s own `@alias`
# regexes above, which these two patterns intentionally mirror.
_EXTENSION_HEADING_PATTERN = re.compile(r"^Extension (\d+[a-z]?)\. .+$")
_SUB_VARIATION_HEADING_PATTERN = re.compile(r"^Step (\d+): .+$")

# Leading digits of a reference (e.g. "3" out of "3a") are what must resolve to a
# `main_success_scenario` step number; a trailing letter (`Extension` only) is
# never itself checked against `main_success_scenario.steps`.
_LEADING_DIGITS_PATTERN = re.compile(r"^\d+")


def _extract_reference(heading_text: str, pattern: re.Pattern[str], label: str) -> str:
    """Extract the step-reference group (e.g. ``"3a"``/``"1"``) from a heading."""
    match = pattern.match(heading_text)
    assert match is not None, f"{label} heading {heading_text!r} does not match its declared @alias pattern"
    return match.group(1)


def _validate_unique_and_resolvable(references: list[str], step_count: int, section: str) -> None:
    """Every reference in `references` must resolve to an existing step number
    (its leading digits, 1-based, within `1..step_count`) and must not appear
    more than once within `section`."""
    seen: set[str] = set()
    for reference in references:
        if reference in seen:
            raise ValueError(f"{section} has a duplicate reference {reference!r}")
        seen.add(reference)

        digits_match = _LEADING_DIGITS_PATTERN.match(reference)
        assert digits_match is not None, f"reference {reference!r} has no leading digits"
        step_number = int(digits_match.group())
        if step_number < 1 or step_number > step_count:
            raise ValueError(
                f"{section} reference {reference!r} does not resolve to any main_success_scenario "
                f"step in 1..{step_count}"
            )


@alias(value=r".+", type=AliasType.REGEX)
class UseCase(MarkdownSection1):
    characteristic_information: CharacteristicInformation
    main_success_scenario: MainSuccessScenario
    extensions: Extensions | None = None
    sub_variations: SubVariations | None = None
    open_issues: OpenIssues | None = None
    related_information: RelatedInformation | None = None

    @model_validator(mode="after")
    def validate_step_references_resolve_and_are_unique(self) -> "UseCase":
        """`Extensions`/`SubVariations` step references must resolve to a real
        `main_success_scenario` step, with no duplicates within either collection.

        Neither the generic markdown engine nor a single model's own fields can
        express this: it requires cross-checking each `Extension`/`SubVariation`
        heading's `{ref}` against the sibling `main_success_scenario.steps`
        collection. Ports Task 1.3B's `UseCase`-level cross-reference invariant
        (`uc/models/v1/use_case.py`'s `_validate_unique_and_resolvable`) onto the
        v2 model tree (Task 1.6, item 3) -- the only one of the original three
        Task 1.3B validators that still applies: the other two (step/action
        numbering contiguity) are now structurally unnecessary, since `steps`/
        `Extension.items` are real CommonMark ordered lists (see DEC-010).
        """
        step_count = len(self.main_success_scenario.steps)

        if self.extensions is not None and self.extensions.extensions is not None:
            references = [
                _extract_reference(extension.text, _EXTENSION_HEADING_PATTERN, "Extension")
                for extension in self.extensions.extensions
            ]
            _validate_unique_and_resolvable(references, step_count, "extensions")

        if self.sub_variations is not None and self.sub_variations.sub_variations is not None:
            references = [
                _extract_reference(sub_variation.text, _SUB_VARIATION_HEADING_PATTERN, "SubVariation")
                for sub_variation in self.sub_variations.sub_variations
            ]
            _validate_unique_and_resolvable(references, step_count, "sub_variations")

        return self
