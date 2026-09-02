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

"""Decision (DEC) body models: whole-section fields under a single H1.

Built on the generic `models.md` `MarkdownSection1`/`MarkdownSection2`/
`MarkdownSection3`/`MarkdownParagraph`/`MarkdownListItem` engine: each class
below models one markdown heading (`## `/`### `) or list, and `Decision` is
the top-level H1 container. A `dec` document keeps the ADR's general
structure (MADR-style headings, an `Options` collection) but is built on the
generic engine with the simple surface used by GOL/RSK/QA (see
`.specmgr/feat/feat-21-decision/README.md` Design Notes).

Field declaration order on `Decision`/`DecisionOutcome`/`RelatedArtifacts`/
`ProsAndCons`/`Updates` enforces markdown order (Context and Problem
Statement -> Decision Drivers -> Considered Options -> Decision Outcome
(-> Consequences -> Confirmation) -> Related Artifacts (-> Requirements ->
Decisions -> Goals -> Acceptance Criteria) -> Pros and Cons (-> Option 1: ->
Option 2: -> ...) -> More Information -> Updates (-> entry 1 -> entry 2 ->
...)), since `models.md`'s `MarkdownStr.from_text` distributes text among
declared fields in that same order.
"""

from __future__ import annotations

import re

from pydantic import Field, computed_field, model_validator

from ....models.md import (
    MarkdownListItem,
    MarkdownParagraph,
    MarkdownSection1,
    MarkdownSection2,
    MarkdownSection2WithComment,
    MarkdownSection3,
    alias,
    AliasType,
)
from ....models.md._ordering import validate_newest_first


@alias(value="Context and Problem Statement", type=AliasType.LITERAL)
class Context(MarkdownSection2):
    """`## Context and Problem Statement` -- the situation and the problem
    the decision addresses. Mandatory, free-form prose.

    The class name `Context` does not match the heading's wording, so the
    alias is pinned LITERAL (the implicit `SPACE_SEPARATED` alias would
    expect "Context").
    """


class DecisionDrivers(MarkdownSection2):
    """`## Decision Drivers` -- the requirements, constraints, and
    stakeholder interests that shape the decision. Optional, free-form prose."""


class ConsideredOptions(MarkdownSection2):
    """`## Considered Options` -- a free-form summary of the options that
    were weighed. Optional, free-form prose; the structured per-option
    content lives under `## Pros and Cons`."""


class Consequences(MarkdownSection3):
    """`### Consequences` under `## Decision Outcome` -- what follows from
    the chosen outcome. Optional, free-form prose."""


class Confirmation(MarkdownSection3):
    """`### Confirmation` under `## Decision Outcome` -- how the outcome was
    or will be confirmed. Optional, free-form prose."""


class DecisionOutcome(MarkdownSection2):
    """`## Decision Outcome` -- the chosen option plus its consequences. Mandatory.

    Parameters
    ----------
    statement:
        The mandatory lead paragraph directly under the H2 -- the outcome
        itself (e.g. "We chose option 1 because ..."). Any other block in
        place of a lead paragraph (a bare list, an H3 first, nothing at
        all) is a structural error.
    consequences:
        `### Consequences` sub-section. Optional.
    confirmation:
        `### Confirmation` sub-section. Optional.
    """

    statement: MarkdownParagraph = Field(
        description="The lead paragraph directly under the H2, before any H3 sub-section -- the "
        "decision outcome itself. Mandatory."
    )
    consequences: Consequences | None = Field(default=None, description="`### Consequences` sub-section. Optional.")
    confirmation: Confirmation | None = Field(default=None, description="`### Confirmation` sub-section. Optional.")


class Requirements(MarkdownSection3):
    """`### Requirements` under Related Artifacts -- bullet list of
    cross-references to requirements, one per line
    (e.g. "REQ-9687: <title>")."""

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Bullet list of cross-references to requirements, one per line "
        '(e.g. "REQ-9687: <title>"); must contain at least one item.',
    )


class Decisions(MarkdownSection3):
    """`### Decisions` under Related Artifacts -- bullet list of
    cross-references to decisions, one per line (e.g. "DEC-2703: <title>")."""

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Bullet list of cross-references to decisions, one per line "
        '(e.g. "DEC-2703: <title>"); must contain at least one item.',
    )


class Goals(MarkdownSection3):
    """`### Goals` under Related Artifacts -- bullet list of
    cross-references to goals, one per line (e.g. "GOL-0007: <title>")."""

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Bullet list of cross-references to goals, one per line "
        '(e.g. "GOL-0007: <title>"); must contain at least one item.',
    )


class AcceptanceCriteria(MarkdownSection3):
    """`### Acceptance Criteria` under Related Artifacts -- bullet list of
    cross-references to acceptance criteria, one per line
    (e.g. "ACC-1234: <title>")."""

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Bullet list of cross-references to acceptance criteria, one per line "
        '(e.g. "ACC-1234: <title>"); must contain at least one item.',
    )


class RelatedArtifacts(MarkdownSection2):
    """`## Related Artifacts` -- container for four independent, all-optional
    `### ` cross-reference lists (requirements/decisions/goals/acceptance
    criteria). Optional as a whole; no consistency check is enforced between
    the sub-lists.
    """

    requirements: Requirements | None = Field(default=None, description="`### Requirements` sub-section. Optional.")
    decisions: Decisions | None = Field(default=None, description="`### Decisions` sub-section. Optional.")
    goals: Goals | None = Field(default=None, description="`### Goals` sub-section. Optional.")
    acceptance_criteria: AcceptanceCriteria | None = Field(
        default=None, description="`### Acceptance Criteria` sub-section. Optional."
    )


#: Matches a `### Option {N}: {name}` heading line as retained in a leaf
#: `MarkdownSection3`'s `.text` (first line), capturing the option number
#: (group 1) and its name (group 2). Mirrors `Option`'s own `@alias`, which
#: sees the heading text without the `###` marker, and `rsk`'s
#: `_PROBABILITY_HEADING_PATTERN`/`_IMPACT_HEADING_PATTERN` (the value is
#: carried by the heading and extracted at access time, never stored).
_OPTION_HEADING_PATTERN = re.compile(r"### Option (\d+): (.+)")


@alias(value=r"^Option \d+: .+$", type=AliasType.REGEX)
class Option(MarkdownSection3):
    """`### Option {N}: {name}` under `## Pros and Cons` -- one weighed option.

    A leaf H3 section: the number and the name both live in the heading
    itself (e.g. `### Option 1: Use PostgreSQL`), constrained by the regex
    `@alias` above and enforced by `match_alias` (`re.fullmatch`) at parse
    time -- a missing colon/title (`### Option 1`), a non-numeric number
    (`### Option one: X`), or a title-less heading (`### Option 1:`) all
    fail the parse eagerly. The number may carry leading zeros
    (`### Option 01: X`); it is normalized to an integer by the computed
    `number` below. Option numbers need not be contiguous (gaps are
    allowed, numbers are never renumbered); duplicates are rejected by
    `Decision`'s own after-validator (the `ValidationError` channel). Any
    body text under the heading is absorbed into the leaf like every other
    leaf `MarkdownSection`.

    Parameters
    ----------
    number:
        Computed. The option's number (e.g. `1` for `### Option 1: X`, also
        `1` for `### Option 01: X`). Never stored separately -- derived
        from the retained heading text.
    name:
        Computed. The option's name (the heading text after `": "`). Never
        stored separately -- derived from the retained heading text.
    """

    @computed_field  # type: ignore
    @property
    def number(self) -> int:
        """The option's number carried by this heading (e.g. `1` for `### Option 1: X`).

        Returns:
            The integer number parsed from the retained heading text
            (leading zeros accepted: `### Option 01: X` yields `1`).

        Raises:
            AssertionError: the retained heading text does not match
                `Option`'s declared `@alias` (unreachable via the engine:
                `match_alias` already enforced it at parse time).
        """
        heading_line = self.text.splitlines()[0].strip() if self.text else ""
        match = _OPTION_HEADING_PATTERN.fullmatch(heading_line)
        assert match, f"Option: expected heading '### Option N: <name>', got {heading_line!r}"
        result: int = int(match.group(1))
        return result

    @computed_field  # type: ignore
    @property
    def name(self) -> str:
        """The option's name carried by this heading (e.g. `X` for `### Option 1: X`).

        Returns:
            The name parsed from the retained heading text (the heading
            text after `": "`, colons inside the name included).

        Raises:
            AssertionError: the retained heading text does not match
                `Option`'s declared `@alias` (unreachable via the engine:
                `match_alias` already enforced it at parse time).
        """
        heading_line = self.text.splitlines()[0].strip() if self.text else ""
        match = _OPTION_HEADING_PATTERN.fullmatch(heading_line)
        assert match, f"Option: expected heading '### Option N: <name>', got {heading_line!r}"
        result: str = match.group(2)
        return result


@alias(value="Pros and Cons", type=AliasType.LITERAL)
class ProsAndCons(MarkdownSection2):
    """`## Pros and Cons` -- the structured per-option pros/cons appendix.

    Optional as a whole, but present only if it carries at least one
    `### Option {N}: {name}` entry (``min_length=1``) -- an H2 with zero
    options is a structural error. The ADR heading "Pros and Cons of the
    Options" is deliberately NOT accepted (LITERAL alias).

    Parameters
    ----------
    options:
        The `### Option {N}: {name}` entries, in document order. Requires
        at least one option.
    """

    options: list[Option] = Field(
        min_length=1,
        description="Dynamic collection of `### Option {N}: {name}` entries, in document order. "
        "Must contain at least one option.",
    )


class MoreInformation(MarkdownSection2):
    """`## More Information` -- free-form optional supplementary text, no
    fixed format. Optional."""


#: Matches a `{yyyy-MM-dd or full date+time} ( - | : ) {title}` heading line
#: as retained in a composite `MarkdownSection3`'s `.text` (which carries the
#: heading's inline content, no `###` marker), capturing the timestamp
#: (named group `timestamp`) and the title (named group `title`). Mirrors
#: `sop.models.v1.body._UPDATE_ENTRY_HEADING_PATTERN`, except the date+time
#: variant's time-of-day/milliseconds/offset is entirely optional here --
#: a bare `yyyy-MM-dd` date is also accepted (REQ-004).
_UPDATE_ENTRY_HEADING_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}))?)(?: - | : )(?P<title>.+)"
)


@alias(
    value=r"^\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}))?(?: - | : ).+$",
    type=AliasType.REGEX,
)
class UpdateEntry(MarkdownSection3):
    """`### {timestamp} ( - | : ) {title}` under `## Updates` -- one update entry.

    The H3 heading text carries a timestamp and a title, joined by either
    ``" - "`` (space, hyphen, space) or ``" : "`` (space, colon, space):
    e.g. `### 2026-08-27 - Confirmed` or
    `### 2026-08-27 14:30:00.000+02:00 : Confirmed`. The em-dash separator
    is rejected. The timestamp is either a bare ``yyyy-MM-dd`` date or the
    full ``yyyy-MM-dd HH:mm:ss.fff`` + explicit UTC offset (``+02:00``,
    ``-05:00``) or ``Z`` for UTC variant (REQ-004) -- deliberately **not**
    the same format as frontmatter ``created``/``updated``; this format is
    scoped to `## Updates` entry headings only, which are hand/LLM-authored
    body content. Constrained by the regex `@alias` above and enforced by
    `match_alias` (`re.fullmatch`) at parse time -- a heading that does not
    start with a valid date, an em-dash separator, or a missing
    `` - ``/`` : `` title all fail the parse eagerly.

    Parameters
    ----------
    content:
        The lead paragraph right after the H3 heading -- this entry's own
        update text. Mandatory.
    timestamp:
        Computed. The timestamp carried by the heading, verbatim. Never
        stored separately -- derived from the retained heading text.
    title:
        Computed. The title carried by the heading (the text after
        ``" - "``/``" : "``). Never stored separately -- derived from the
        retained heading text.
    """

    content: MarkdownParagraph = Field(
        description="The lead paragraph directly under the H3 heading -- this entry's own update text. Mandatory."
    )

    @computed_field  # type: ignore
    @property
    def timestamp(self) -> str:
        """The timestamp carried by this heading (e.g. `2026-08-27` or `2026-08-27 14:30:00.000+02:00`).

        Returns:
            The timestamp string parsed from the retained heading text.

        Raises:
            AssertionError: the retained heading text does not match
                `UpdateEntry`'s declared `@alias` (unreachable via the
                engine: `match_alias` already enforced it at parse time).
        """
        match = _UPDATE_ENTRY_HEADING_PATTERN.fullmatch(self.text)
        assert match, f"UpdateEntry: expected heading '{{timestamp}} ( - | : ) {{title}}', got {self.text!r}"
        result: str = match.group("timestamp")
        return result

    @computed_field  # type: ignore
    @property
    def title(self) -> str:
        """The title carried by this heading (e.g. `Confirmed` for `### 2026-08-27 - Confirmed`).

        Returns:
            The title parsed from the retained heading text (the text
            after ``" - "``/``" : "``).

        Raises:
            AssertionError: the retained heading text does not match
                `UpdateEntry`'s declared `@alias` (unreachable via the
                engine: `match_alias` already enforced it at parse time).
        """
        match = _UPDATE_ENTRY_HEADING_PATTERN.fullmatch(self.text)
        assert match, f"UpdateEntry: expected heading '{{timestamp}} ( - | : ) {{title}}', got {self.text!r}"
        result: str = match.group("title")
        return result


class Updates(MarkdownSection2WithComment):
    """`## Updates` -- a dynamic, newest-first list of timestamp-led `### ` update
    entries. Optional as a whole, and the last section of the document if
    present. May be preceded by an explanatory HTML comment (e.g. an
    ordering hint).

    Mirrors `tsk`'s `RecentUpdates` shape: no dedicated per-entry tools (no
    `option_create`/`option_list` equivalent) -- entries are prepended
    (newest-first) by editing the whole body.

    Parameters
    ----------
    comment:
        Optional explanatory HTML comment (`<!-- ... -->`), e.g.
        `<!-- Newest entry first -- prepend new entries directly below
        this comment. -->`. Inherited from `MarkdownSection2WithComment`.
    updates:
        The dynamic collection of `### ` entries, in document order,
        newest-first (enforced, see `_validate_newest_first`). Requires
        at least one entry (``min_length=1``) -- an H2 with zero entries is
        a structural error.
    """

    updates: list[UpdateEntry] = Field(
        min_length=1,
        description="Dynamic collection of `### {timestamp} ( - | : ) {title}` entries, in document order, "
        "newest-first. Must contain at least one entry.",
    )

    @model_validator(mode="after")
    def _validate_newest_first(self) -> Updates:
        """Reject entries that are not in newest-first order.

        Delegates to the shared `models.md._ordering.validate_newest_first`
        helper (mixed date-only/date+time day-granularity rule, equal
        values allowed) -- mirrors `feat.models.v1.body.Updates._validate_newest_first`
        without duplicating its logic. Raises on the first out-of-order pair.
        """
        validate_newest_first([update.timestamp for update in self.updates], "Updates")
        return self


@alias(value=".+", type=AliasType.REGEX)
class Decision(MarkdownSection1):
    """The `dec` body: a single H1 section with the fields below.

    The H1 heading text is free-form. Keeps the ADR's general structure
    (MADR headings + an options collection) on the generic `models.md`
    engine -- see the module docstring.

    Parameters
    ----------
    context:
        `## Context and Problem Statement`. Mandatory.
    drivers:
        `## Decision Drivers`. Optional.
    considered:
        `## Considered Options`. Optional.
    outcome:
        `## Decision Outcome` (mandatory lead paragraph + optional
        `### Consequences`/`### Confirmation`). Mandatory.
    related_artifacts:
        `## Related Artifacts` (four all-optional H3 bullet lists). Optional.
    pros_and_cons:
        `## Pros and Cons` (`### Option {N}: {name}` entries, >=1 if
        present). Optional.
    more_information:
        `## More Information`. Optional.
    updates:
        `## Updates` (>=1 entry if present). Optional; last section.
    """

    context: Context = Field(description="`## Context and Problem Statement` section. Mandatory.")
    drivers: DecisionDrivers | None = Field(default=None, description="`## Decision Drivers` section. Optional.")
    considered: ConsideredOptions | None = Field(default=None, description="`## Considered Options` section. Optional.")
    outcome: DecisionOutcome = Field(description="`## Decision Outcome` section. Mandatory.")
    related_artifacts: RelatedArtifacts | None = Field(
        default=None, description="`## Related Artifacts` section. Optional."
    )
    pros_and_cons: ProsAndCons | None = Field(default=None, description="`## Pros and Cons` section. Optional.")
    more_information: MoreInformation | None = Field(
        default=None, description="`## More Information` section. Optional."
    )
    updates: Updates | None = Field(default=None, description="`## Updates` section. Optional; last.")

    @model_validator(mode="after")
    def _validate_option_numbers_unique(self) -> Decision:
        """Reject duplicate option numbers across `## Pros and Cons`.

        `Option.number`/`.name` are `@computed_field`s -- Pydantic only
        evaluates a computed field's getter on access (e.g. during
        `model_dump()`/serialization), never during construction/validation
        of the underlying model itself. Accessing `.number` here therefore
        both forces every option's number to evaluate eagerly and checks
        the cross-field invariant: no two options may carry the same number
        (`### Option 1` and `### Option 01` are the same number and
        therefore a duplicate). Gaps are allowed (options are never
        renumbered). A duplicate raises `ValueError`, which Pydantic
        channels into `ValidationError` (the value-violation channel,
        mirroring the RSK-TARA cross-field-validator precedent).
        """
        if self.pros_and_cons is not None:
            seen: set[int] = set()
            for option in self.pros_and_cons.options:
                number = option.number
                if number in seen:
                    raise ValueError(f"option number {number} is used by more than one `### Option` heading")
                seen.add(number)
        return self
