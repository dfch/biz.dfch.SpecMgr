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

"""Feature (FEAT) body models: whole-section fields under a single H1.

Built on the generic `models.md` `MarkdownSection1`/`MarkdownSection2`/
`MarkdownSection3`/`MarkdownSection3WithComment`/`MarkdownSection4`/
`MarkdownParagraph`/`MarkdownListItem` engine, plus `tsk`'s own `TaskItem`
(reused as-is, not reimplemented -- see `Phase.items` below). `Feature` is
the top-level H1 container, holding exactly two children, `Plan` and
`Progress` -- see `.specmgr/feat/feat-31-feature/README.md` Design Notes
("Document structure"/"Model classes") for the full ASCII diagram this
mirrors field-for-field.

Field declaration order on every composite class below enforces markdown
order (``Feature``: plan -> progress; ``Plan``: overview -> requirements ->
acceptance_criteria -> scope -> dependencies -> design_notes ->
related_decisions -> task_list; ``Progress``: current_status -> blockers ->
updates -> decisions_made -> related_prs_commits -> more_information),
since `models.md`'s `MarkdownStr.from_text` distributes text among declared
fields in that same order.

Two eager-computed-field-validation `model_validator`s extend the existing
`tsk.models.v1.body.Task._validate_items_eagerly` pattern beyond this
package's own precedent set (`dec`'s duplicate-option-number check is a
cross-item invariant, not an eager-evaluation one): `Requirements`/
`AcceptanceCriteria` force every item's regex-derived computed field(s) to
evaluate during construction/parsing rather than lazily on first access,
consistent with `tsk.Task`'s reasoning (a malformed item must not silently
parse and only fail, if ever, whenever something later happens to read the
computed field). `Phase` does the same for its own `items: list[TaskItem]`
(forcing `.checked` eagerly), for the same reason.
"""

from __future__ import annotations

import re
from datetime import datetime

from pydantic import Field, computed_field, model_validator

from ....models.md import (
    AliasType,
    MarkdownListItem,
    MarkdownParagraph,
    MarkdownSection1,
    MarkdownSection2,
    MarkdownSection3,
    MarkdownSection3WithComment,
    MarkdownSection4,
    alias,
)
from ....tsk.models.v1.task_item import TaskItem


class Overview(MarkdownSection3):
    """`### Overview` -- free-form prose describing what this feature is and
    why it exists. Mandatory."""


#: Matches a `REQ-NNN: {description}` list item's `.text`, capturing the
#: description (named group `description`). Mirrors `dec`'s
#: `_OPTION_HEADING_PATTERN`/`tsk`'s `TaskItem._MARKER_PATTERN` -- the value
#: is carried by the item's own text and extracted at access time, never
#: stored.
_REQUIREMENT_ITEM_PATTERN = re.compile(r"^REQ-\d{3}: (?P<description>.+)$")


class RequirementItem(MarkdownListItem):
    """`- REQ-NNN: {text}` -- one bullet-list requirement entry under `### Requirements`.

    A leaf `MarkdownListItem` subclass (no checkbox marker, unlike `TaskItem`):
    the requirement number and its description both live in the item's own
    text (e.g. `"REQ-001: The widget must render within 200ms."`), recovered
    by the `@computed_field` below.

    Parameters
    ----------
    description:
        Computed. This item's own text with the `REQ-NNN: ` prefix stripped.
        Raises `AssertionError` if `.text` does not match `REQ-\\d{3}: .+`.
    """

    @computed_field  # type: ignore
    @property
    def description(self) -> str:
        """This item's own description, with the `REQ-NNN: ` prefix stripped.

        Returns:
            The description text following the `REQ-NNN: ` prefix.

        Raises:
            AssertionError: `.text` does not match `^REQ-\\d{3}: .+$`.
        """
        match = _REQUIREMENT_ITEM_PATTERN.fullmatch(self.text)
        assert match, f"RequirementItem: expected 'REQ-NNN: <description>', got {self.text!r}"
        result: str = match.group("description")
        return result


class Requirements(MarkdownSection3):
    """`### Requirements` -- bullet list of `REQ-NNN: {text}` entries. Mandatory. At least one item.

    Parameters
    ----------
    items:
        The `REQ-NNN: {text}` entries, in document order. At least one item.
    """

    items: list[RequirementItem] = Field(
        min_length=1,
        description="Bullet list of `REQ-NNN: {text}` entries, in document order. Must contain at least one item.",
    )

    @model_validator(mode="after")
    def _validate_items_eagerly(self) -> Requirements:
        """Force every item's `.description` computed field to evaluate eagerly, not lazily.

        Mirrors `tsk.models.v1.body.Task._validate_items_eagerly`: without
        this, a malformed item (e.g. `"- Not a requirement"`) would parse
        silently and only raise, if ever, whenever something later happens
        to read `.description`.
        """
        for item in self.items:
            _ = item.description
        return self


#: Matches an `ACC-NNN: {description}` `TaskItem.description` value (already
#: stripped of its `- [ ]`/`- [x]` marker), capturing the description (named
#: group `description`).
_ACCEPTANCE_CRITERION_ITEM_PATTERN = re.compile(r"^ACC-\d{3}: (?P<description>.+)$")


class AcceptanceCriterionItem(TaskItem):
    """`- [ ] ACC-NNN: {text}` -- one checklist acceptance-criterion entry under `### Acceptance Criteria`.

    Reuses `tsk.TaskItem`'s `checked`/`description`-from-checkbox split
    as-is, adding one more computed field re-matching the `ACC-NNN: ` prefix
    against the inherited `description`.

    Parameters
    ----------
    criterion_description:
        Computed. `.description` (already checkbox-stripped) with the
        `ACC-NNN: ` prefix further stripped. Raises `AssertionError` if
        `.description` does not match `ACC-\\d{3}: .+`.
    """

    @computed_field  # type: ignore
    @property
    def criterion_description(self) -> str:
        """This item's own description, with the `ACC-NNN: ` prefix further stripped.

        Returns:
            The description text following the `ACC-NNN: ` prefix.

        Raises:
            AssertionError: `.description` does not match `^ACC-\\d{3}: .+$`.
        """
        match = _ACCEPTANCE_CRITERION_ITEM_PATTERN.fullmatch(self.description)
        assert match, f"AcceptanceCriterionItem: expected 'ACC-NNN: <description>', got {self.description!r}"
        result: str = match.group("description")
        return result


class AcceptanceCriteria(MarkdownSection3):
    """`### Acceptance Criteria` -- checklist of `- [ ]/[x] ACC-NNN: {text}` entries. Mandatory. At least one item.

    Parameters
    ----------
    items:
        The `ACC-NNN: {text}` checklist entries, in document order. At
        least one item.
    """

    items: list[AcceptanceCriterionItem] = Field(
        min_length=1,
        description="Checklist of `- [ ]/[x] ACC-NNN: {text}` entries, in document order. "
        "Must contain at least one item.",
    )

    @model_validator(mode="after")
    def _validate_items_eagerly(self) -> AcceptanceCriteria:
        """Force every item's `.checked`/`.criterion_description` computed fields to evaluate eagerly.

        Mirrors `tsk.models.v1.body.Task._validate_items_eagerly` and
        `Requirements._validate_items_eagerly` above.
        """
        for item in self.items:
            _ = item.checked
            _ = item.criterion_description
        return self


class Included(MarkdownSection4):
    """`#### Included` under `### Scope` -- free-form bullet list of what this feature covers. Mandatory."""


class ExplicitlyOutOfScope(MarkdownSection4):
    """`#### Explicitly Out Of Scope` under `### Scope` -- free-form bullet list of what this feature
    deliberately does not cover. Mandatory."""


class Scope(MarkdownSection3):
    """`### Scope` -- container for the two mandatory Included/Explicitly Out Of Scope leaves. No own text.

    Parameters
    ----------
    included:
        `#### Included`. Mandatory.
    explicitly_out_of_scope:
        `#### Explicitly Out Of Scope`. Mandatory.
    """

    included: Included = Field(description="`#### Included` section. Mandatory.")
    explicitly_out_of_scope: ExplicitlyOutOfScope = Field(
        description="`#### Explicitly Out Of Scope` section. Mandatory."
    )


class DependsOn(MarkdownSection4):
    """`#### Depends On` under `### Dependencies` -- free-form list of things this feature needs first.
    Optional."""


class Blocks(MarkdownSection4):
    """`#### Blocks` under `### Dependencies` -- free-form list of things that cannot start until this
    feature ships. Optional."""


class Dependencies(MarkdownSection3):
    """`### Dependencies` -- container for the two independently optional Depends On/Blocks leaves. No own text.

    Optional as a whole; a feature may have no dependencies and block
    nothing else.

    Parameters
    ----------
    depends_on:
        `#### Depends On`. Optional.
    blocks:
        `#### Blocks`. Optional.
    """

    depends_on: DependsOn | None = Field(default=None, description="`#### Depends On` section. Optional.")
    blocks: Blocks | None = Field(default=None, description="`#### Blocks` section. Optional.")


class DesignNotes(MarkdownSection3):
    """`### Design Notes` -- free-form design rationale, schema sketches, etc. Optional."""


class RelatedDecisions(MarkdownSection3):
    """`### Related Decisions` -- free-form cross-reference list; entries may reference either an ADR id or a
    `dec` id (or any other decision record). Optional."""


#: Matches a `Phase N: {title}` heading line, capturing the phase number
#: (named group `number`) and its title (named group `title`). Mirrors
#: `dec`'s `_OPTION_HEADING_PATTERN`.
_PHASE_HEADING_PATTERN = re.compile(r"^Phase (?P<number>\d+): (?P<title>.+)$")


@alias(value=r"^Phase \d+: .+$", type=AliasType.REGEX)
class Phase(MarkdownSection4):
    """`#### Phase N: {title}` under `### Task List` -- one phase's own flat checklist.

    Unpadded phase numbers (matching this very plan's own "Phase 0".."Phase
    5" headings). Per-item metadata (`depends on:`/`status:`/`ETA`) stays
    unparsed free text inside each item's own description.

    Parameters
    ----------
    items:
        The flat `- [ ] .../- [x] ...` checklist for this phase, reusing
        `tsk.models.v1.task_item.TaskItem` as-is. At least one item.
    number:
        Computed. The phase's number (e.g. `1` for `#### Phase 1: X`).
        Never stored separately -- derived from the retained heading text.
    title:
        Computed. The phase's title (the heading text after `": "`). Never
        stored separately -- derived from the retained heading text.
    """

    items: list[TaskItem] = Field(
        min_length=1,
        description="The flat `- [ ] .../- [x] ...` checklist for this phase, in document order. "
        "Must contain at least one item.",
    )

    @computed_field  # type: ignore
    @property
    def number(self) -> int:
        """The phase's number carried by this heading (e.g. `1` for `#### Phase 1: X`).

        Returns:
            The integer number parsed from the retained heading text.

        Raises:
            AssertionError: the retained heading text does not match
                `Phase`'s declared `@alias` (unreachable via the engine:
                `match_alias` already enforced it at parse time).
        """
        match = _PHASE_HEADING_PATTERN.fullmatch(self.text)
        assert match, f"Phase: expected heading 'Phase N: <title>', got {self.text!r}"
        result: int = int(match.group("number"))
        return result

    @computed_field  # type: ignore
    @property
    def title(self) -> str:
        """The phase's title carried by this heading (e.g. `X` for `#### Phase 1: X`).

        Returns:
            The title parsed from the retained heading text (the heading
            text after `": "`, colons inside the title included).

        Raises:
            AssertionError: the retained heading text does not match
                `Phase`'s declared `@alias` (unreachable via the engine:
                `match_alias` already enforced it at parse time).
        """
        match = _PHASE_HEADING_PATTERN.fullmatch(self.text)
        assert match, f"Phase: expected heading 'Phase N: <title>', got {self.text!r}"
        result: str = match.group("title")
        return result

    @model_validator(mode="after")
    def _validate_items_eagerly(self) -> Phase:
        """Force every item's `.checked` computed field to evaluate eagerly, not lazily.

        Mirrors `tsk.models.v1.body.Task._validate_items_eagerly`.
        """
        for item in self.items:
            _ = item.checked
        return self


class TaskList(MarkdownSection3):
    """`### Task List` -- container for the `#### Phase N: ...` entries. No own text. Mandatory. At least
    one phase.

    Parameters
    ----------
    phases:
        The `#### Phase N: {title}` entries, in document order. At least
        one phase.
    """

    phases: list[Phase] = Field(
        min_length=1,
        description="The `#### Phase N: {title}` entries, in document order. Must contain at least one phase.",
    )


class Plan(MarkdownSection2):
    """`## Plan` -- container for the feature's plan-side sections. No own text. Mandatory.

    Parameters
    ----------
    overview:
        `### Overview`. Mandatory.
    requirements:
        `### Requirements`. Mandatory.
    acceptance_criteria:
        `### Acceptance Criteria`. Mandatory.
    scope:
        `### Scope`. Mandatory.
    dependencies:
        `### Dependencies`. Optional.
    design_notes:
        `### Design Notes`. Optional.
    related_decisions:
        `### Related Decisions`. Optional.
    task_list:
        `### Task List`. Mandatory.
    """

    overview: Overview = Field(description="`### Overview` section. Mandatory.")
    requirements: Requirements = Field(description="`### Requirements` section. Mandatory.")
    acceptance_criteria: AcceptanceCriteria = Field(description="`### Acceptance Criteria` section. Mandatory.")
    scope: Scope = Field(description="`### Scope` section. Mandatory.")
    dependencies: Dependencies | None = Field(default=None, description="`### Dependencies` section. Optional.")
    design_notes: DesignNotes | None = Field(default=None, description="`### Design Notes` section. Optional.")
    related_decisions: RelatedDecisions | None = Field(
        default=None, description="`### Related Decisions` section. Optional."
    )
    task_list: TaskList = Field(description="`### Task List` section. Mandatory.")


class CurrentStatus(MarkdownSection3):
    """`### Current Status` -- free-form narrative of where things stand. Mandatory."""


class Blockers(MarkdownSection3):
    """`### Blockers` -- free-form list of open blockers. Optional."""


#: Matches a `{timestamp} — {title}` heading line, capturing the ISO8601
#: timestamp (named group `timestamp`) and the title (named group `title`).
#: Shared verbatim between `UpdateEntry` and `DecisionEntry` (identical
#: shape, see both classes' docstrings).
_ENTRY_HEADING_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})) — (?P<title>.+)$"
)

#: The `@alias` REGEX value shared verbatim by `UpdateEntry` and
#: `DecisionEntry` -- ISO8601 date + space + time + milliseconds + explicit
#: UTC offset (`+02:00`, `-05:00`) or `Z` for UTC.
_ENTRY_HEADING_ALIAS = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}) — .+$"


@alias(value=_ENTRY_HEADING_ALIAS, type=AliasType.REGEX)
class UpdateEntry(MarkdownSection4):
    """`#### {timestamp} — {title}` under `### Updates` -- one update entry.

    The timestamp format is deliberately not the same format as frontmatter
    `created`/`updated` (a `datetime.isoformat(timespec="microseconds")`
    value, e.g. `2026-08-30T14:23:01.123456`) -- this format is scoped to
    `### Updates`/`### Decisions Made` entry headings only, hand/LLM-authored
    body content, not tool-generated frontmatter.

    Parameters
    ----------
    content:
        The lead paragraph right after the H4 heading -- this entry's own
        update text. Mandatory.
    timestamp:
        Computed. The entry's ISO8601 timestamp, verbatim from the heading.
        Never stored separately -- derived from the retained heading text.
    title:
        Computed. The entry's title (the heading text after `" — "`). Never
        stored separately -- derived from the retained heading text.
    """

    content: MarkdownParagraph = Field(
        description="The lead paragraph directly under the H4 heading -- this entry's own update text. Mandatory."
    )

    @computed_field  # type: ignore
    @property
    def timestamp(self) -> str:
        """The entry's ISO8601 timestamp carried by this heading, verbatim.

        Returns:
            The timestamp string parsed from the retained heading text.

        Raises:
            AssertionError: the retained heading text does not match this
                class's declared `@alias` (unreachable via the engine:
                `match_alias` already enforced it at parse time).
        """
        match = _ENTRY_HEADING_PATTERN.fullmatch(self.text)
        assert match, f"{type(self).__name__}: expected heading '{{timestamp}} — {{title}}', got {self.text!r}"
        result: str = match.group("timestamp")
        return result

    @computed_field  # type: ignore
    @property
    def title(self) -> str:
        """The entry's title carried by this heading (the heading text after `" — "`).

        Returns:
            The title parsed from the retained heading text.

        Raises:
            AssertionError: the retained heading text does not match this
                class's declared `@alias` (unreachable via the engine:
                `match_alias` already enforced it at parse time).
        """
        match = _ENTRY_HEADING_PATTERN.fullmatch(self.text)
        assert match, f"{type(self).__name__}: expected heading '{{timestamp}} — {{title}}', got {self.text!r}"
        result: str = match.group("title")
        return result


class Updates(MarkdownSection3WithComment):
    """`### Updates` -- a dynamic, newest-first list of ISO8601-timestamped `#### ` update entries. Mandatory.
    At least one entry. May be preceded by an explanatory HTML comment (e.g. an ordering hint).

    Parameters
    ----------
    comment:
        Optional explanatory HTML comment (`<!-- ... -->`), e.g.
        `<!-- Newest entry first -- prepend new entries directly below
        this comment. -->`. Inherited from `MarkdownSection3WithComment`.
    updates:
        The `#### {timestamp} — {title}` entries, in document order,
        newest-first (enforced, see `_validate_newest_first`). At least
        one entry.
    """

    updates: list[UpdateEntry] = Field(
        min_length=1,
        description="Dynamic collection of `#### {timestamp} — {title}` entries, in document order, "
        "newest-first. Must contain at least one entry.",
    )

    @model_validator(mode="after")
    def _validate_newest_first(self) -> Updates:
        """Reject entries that are not in newest-first order.

        Consecutive entries' parsed `datetime.fromisoformat(entry.timestamp)`
        values must be non-increasing (each entry's timestamp `<=` the
        previous entry's) -- extending the existing eager-computed-field-
        validation pattern (`tsk.models.v1.body.Task._validate_items_eagerly`)
        to a genuine cross-item ordering guarantee. Raises on the first
        out-of-order pair.
        """
        for earlier, later in zip(self.updates, self.updates[1:]):
            earlier_ts = datetime.fromisoformat(earlier.timestamp)
            later_ts = datetime.fromisoformat(later.timestamp)
            assert earlier_ts >= later_ts, (
                f"Updates: entries must be newest-first; {earlier.timestamp!r} precedes {later.timestamp!r}"
            )
        return self


@alias(value=_ENTRY_HEADING_ALIAS, type=AliasType.REGEX)
class DecisionEntry(MarkdownSection4):
    """`#### {timestamp} — {title}` under `### Decisions Made` -- one decision entry.

    Identical shape to `UpdateEntry` (same alias regex, same `timestamp`/
    `title` computed-field extraction, same `content: MarkdownParagraph`) --
    a distinct class since it belongs to a semantically distinct section.

    Parameters
    ----------
    content:
        The lead paragraph right after the H4 heading -- this entry's own
        decision text. Mandatory.
    timestamp:
        Computed. The entry's ISO8601 timestamp, verbatim from the heading.
        Never stored separately -- derived from the retained heading text.
    title:
        Computed. The entry's title (the heading text after `" — "`). Never
        stored separately -- derived from the retained heading text.
    """

    content: MarkdownParagraph = Field(
        description="The lead paragraph directly under the H4 heading -- this entry's own decision text. Mandatory."
    )

    @computed_field  # type: ignore
    @property
    def timestamp(self) -> str:
        """The entry's ISO8601 timestamp carried by this heading, verbatim.

        Returns:
            The timestamp string parsed from the retained heading text.

        Raises:
            AssertionError: the retained heading text does not match this
                class's declared `@alias` (unreachable via the engine:
                `match_alias` already enforced it at parse time).
        """
        match = _ENTRY_HEADING_PATTERN.fullmatch(self.text)
        assert match, f"{type(self).__name__}: expected heading '{{timestamp}} — {{title}}', got {self.text!r}"
        result: str = match.group("timestamp")
        return result

    @computed_field  # type: ignore
    @property
    def title(self) -> str:
        """The entry's title carried by this heading (the heading text after `" — "`).

        Returns:
            The title parsed from the retained heading text.

        Raises:
            AssertionError: the retained heading text does not match this
                class's declared `@alias` (unreachable via the engine:
                `match_alias` already enforced it at parse time).
        """
        match = _ENTRY_HEADING_PATTERN.fullmatch(self.text)
        assert match, f"{type(self).__name__}: expected heading '{{timestamp}} — {{title}}', got {self.text!r}"
        result: str = match.group("title")
        return result


class DecisionsMade(MarkdownSection3WithComment):
    """`### Decisions Made` -- a dynamic, newest-first list of ISO8601-timestamped `#### ` decision entries.
    Optional as a whole; at least one entry once present. May be preceded by an explanatory HTML comment
    (e.g. an ordering hint).

    Optionality lives one level up (`Progress.decisions_made: DecisionsMade
    | None = None`) -- a brand-new feature has no `### Decisions Made`
    section at all, rather than an empty one, same "non-`Optional` `list[X]`
    implies >=1 once the section exists" convention as `Updates.updates`/
    `TaskList.phases`.

    Parameters
    ----------
    comment:
        Optional explanatory HTML comment (`<!-- ... -->`). Inherited from
        `MarkdownSection3WithComment`.
    decisions:
        The `#### {timestamp} — {title}` entries, in document order,
        newest-first (enforced, see `_validate_newest_first`). At least
        one entry.
    """

    decisions: list[DecisionEntry] = Field(
        min_length=1,
        description="Dynamic collection of `#### {timestamp} — {title}` entries, in document order, "
        "newest-first. Must contain at least one entry.",
    )

    @model_validator(mode="after")
    def _validate_newest_first(self) -> DecisionsMade:
        """Reject entries that are not in newest-first order.

        Mirrors `Updates._validate_newest_first` exactly -- see its
        docstring for the full rationale.
        """
        for earlier, later in zip(self.decisions, self.decisions[1:]):
            earlier_ts = datetime.fromisoformat(earlier.timestamp)
            later_ts = datetime.fromisoformat(later.timestamp)
            assert earlier_ts >= later_ts, (
                f"DecisionsMade: entries must be newest-first; {earlier.timestamp!r} precedes {later.timestamp!r}"
            )
        return self


@alias(value="Related PRs / Commits", type=AliasType.LITERAL)
class RelatedPrsCommits(MarkdownSection3):
    """`### Related PRs / Commits` -- free-form list of related pull requests/commits. Optional.

    The slash/mixed-case wording breaks the plain `SPACE_SEPARATED`
    convention, so the heading is pinned `LITERAL`.
    """


class MoreInformation(MarkdownSection3):
    """`### More Information` -- free-form optional supplementary text, no fixed format. Optional."""


class Progress(MarkdownSection2):
    """`## Progress` -- container for the feature's progress-side sections. No own text. Mandatory.

    Parameters
    ----------
    current_status:
        `### Current Status`. Mandatory.
    blockers:
        `### Blockers`. Optional.
    updates:
        `### Updates`. Mandatory.
    decisions_made:
        `### Decisions Made`. Optional.
    related_prs_commits:
        `### Related PRs / Commits`. Optional.
    more_information:
        `### More Information`. Optional.
    """

    current_status: CurrentStatus = Field(description="`### Current Status` section. Mandatory.")
    blockers: Blockers | None = Field(default=None, description="`### Blockers` section. Optional.")
    updates: Updates = Field(description="`### Updates` section. Mandatory.")
    decisions_made: DecisionsMade | None = Field(default=None, description="`### Decisions Made` section. Optional.")
    related_prs_commits: RelatedPrsCommits | None = Field(
        default=None, description="`### Related PRs / Commits` section. Optional."
    )
    more_information: MoreInformation | None = Field(
        default=None, description="`### More Information` section. Optional."
    )


@alias(value="^Feature: .+$", type=AliasType.REGEX)
class Feature(MarkdownSection1):
    """The `feat` body: a single H1 section (`# Feature: {title}`) with the fields below.

    Parameters
    ----------
    plan:
        `## Plan`. Mandatory.
    progress:
        `## Progress`. Mandatory.
    """

    plan: Plan = Field(description="`## Plan` section. Mandatory.")
    progress: Progress = Field(description="`## Progress` section. Mandatory.")
