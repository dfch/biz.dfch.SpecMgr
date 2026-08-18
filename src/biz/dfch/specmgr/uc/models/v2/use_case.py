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
    MarkdownListItemWithNotes,
)
from biz.dfch.specmgr.models.md import alias, AliasType

# 'Characteristic Information' [required]


@alias(value="Goal in Context", type=AliasType.LITERAL)
class GoalInContext(MarkdownSection3):
    """The goal the primary actor is trying to achieve by carrying out this use case, stated in the context of the
    surrounding business process.

    Free-form prose.
    """

    body: list[MarkdownParagraph]


class Scope(MarkdownSection3):
    """The boundary of the system or business process being designed -- what falls inside vs. outside this use
    case's responsibility.

    Free-form prose.
    """

    body: list[MarkdownParagraph]


class Level(MarkdownSection3):
    """The use case's altitude in Cockburn's goal hierarchy (e.g. user-goal, summary, subfunction), signalling how
    large a piece of work it covers.

    Free-form prose.
    """

    body: list[MarkdownParagraph]


class Preconditions(MarkdownSection3):
    """Conditions that must already hold true in the world before this use case is allowed to start.

    A bullet list of conditions.
    """

    items: list[MarkdownListItem]


class SuccessEndCondition(MarkdownSection3):
    """Conditions that must hold true once the use case completes successfully -- the guarantee given to
    stakeholders.

    A bullet list of conditions.
    """

    items: list[MarkdownListItem]


class FailedEndCondition(MarkdownSection3):
    """Conditions that must hold true if the use case aborts or fails partway through.

    A bullet list of conditions.
    """

    items: list[MarkdownListItem]


class PrimaryActor(MarkdownSection3):
    """The actor who initiates the use case and whose goal it exists to satisfy.

    Free-form prose naming and describing that actor.
    """

    body: list[MarkdownParagraph]


class SecondaryActors(MarkdownSection3):
    """Actors other than the primary actor who take part in the use case or have a stake in its outcome (e.g.
    external systems, other roles).

    A bullet list of actors.
    """

    items: list[MarkdownListItem]


class Trigger(MarkdownSection3):
    """The event that starts the use case, whether an actor's action, a point in time, or a condition becoming
    true.

    Free-form prose.
    """

    body: list[MarkdownParagraph]


class Frequency(MarkdownSection3):
    """How often this use case is expected to occur, informing performance and capacity decisions.

    Free-form prose.
    """

    body: list[MarkdownParagraph]


class Priority(MarkdownSection3):
    """How important this use case is relative to others, guiding implementation order.

    Free-form prose.
    """

    body: list[MarkdownParagraph]


class PerformanceTarget(MarkdownSection3):
    """The response-time or throughput goal the system must meet while executing this use case.

    Free-form prose.
    """

    body: list[MarkdownParagraph]


@alias(value="Channels to Primary Actor", type=AliasType.LITERAL)
class ChannelsToPrimaryActor(MarkdownSection3):
    """The communication channel(s) (e.g. web, phone, in person) through which the primary actor interacts with
    the system.

    A bullet list of channels.
    """

    items: list[MarkdownListItem]


@alias(value="Channels to Secondary Actors", type=AliasType.LITERAL)
class ChannelsToSecondaryActors(MarkdownSection3):
    """The communication channel(s) through which secondary actors interact with the system during this use
    case.

    A bullet list of channels.
    """

    items: list[MarkdownListItem]


class RelatedUseCases(MarkdownSection3):
    """Other use cases that this one depends on, is a variation of, or is otherwise related to.

    A bullet list of use case references.
    """

    items: list[MarkdownListItem]


class CharacteristicInformation(MarkdownSection2):
    """The descriptive metadata that frames a use case before its steps are told -- who wants what, when it
    applies, and how success is judged.

    Composed of the sub-sections above (Goal in Context, Scope, Level, Preconditions, ...).
    """

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
    """The primary, everything-goes-right path: the sequence of actor/system interactions that satisfies the
    primary actor's goal with no exceptions.

    An ordered list of numbered steps.
    """

    steps: list[MarkdownListItem]


# 'Extensions' [required]


class ExtensionItem(MarkdownListItemWithNotes):
    """One action taken while handling an extension's alternate flow, with any continuation text that clarifies it."""


@alias(value=r"^Extension \d+[a-z]?\. .+$", type=AliasType.REGEX)
class Extension(MarkdownSection3):
    """An alternate flow that branches off a specific main-scenario step when a named condition holds, describing
    how the use case proceeds differently from that point.

    An ordered list of actions (`items`), headed by a condition naming which step it branches from.
    """

    items: list[ExtensionItem]


class Extensions(MarkdownSection2):
    """All the alternate flows that can branch off the main success scenario, covering exceptional or
    alternative conditions.

    An optional introductory paragraph followed by a list of Extension sections, one per branching condition.
    """

    intro: MarkdownParagraph | None = None
    extensions: list[Extension] | None = None


# 'Sub-Variations' [optional]


@alias(value=r"^Step \d+: .+$", type=AliasType.REGEX)
class SubVariation(MarkdownSection3):
    """A minor variation in how a single main-scenario step is carried out, without branching into a full
    alternate flow.

    A bullet list of variant actions for that one step.
    """

    items: list[MarkdownListItem]


@alias(value="Sub-Variations", type=AliasType.LITERAL)
class SubVariations(MarkdownSection2):
    """Minor, non-branching variations on individual main-scenario steps, collected in one place instead of
    cluttering the main flow.

    A list of SubVariation sections, one per varying step.
    """

    sub_variations: list[SubVariation] | None = None


# 'Open Issues' [optional]


class OpenIssues(MarkdownSection2):
    """Unresolved questions or decisions about the use case that still need to be settled.

    A bullet list of open questions.
    """

    items: list[MarkdownListItem]


# 'Related Information' [optional]


class Notes(MarkdownSection3):
    """Free-form remarks about the use case that do not fit any other section.

    A bullet list of notes.
    """

    items: list[MarkdownListItem]


class Assumptions(MarkdownSection3):
    """Conditions taken for granted while writing the use case, which -- if wrong -- would invalidate parts of
    it.

    A bullet list of assumptions.
    """

    items: list[MarkdownListItem]


class RelatedInformation(MarkdownSection2):
    """Supplementary commentary about the use case, kept separate from its behavioral content.

    Composed of two optional sub-sections: Notes and Assumptions.
    """

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
    """A single use case: one actor-facing goal, described end to end from context through its main flow and
    every alternate/variant path.

    Composed of Characteristic Information, the Main Success Scenario, and the optional Extensions,
    Sub-Variations, Open Issues, and Related Information sections.
    """

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
