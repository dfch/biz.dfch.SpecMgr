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

"""Standard Operating Procedure (SOP) body models: whole-section fields under a single H1.

Built on the generic `models.md` `MarkdownSection1`/`MarkdownSection2`/
`MarkdownSection3`/`MarkdownParagraph`/`MarkdownListItem` engine: each class
below models one markdown heading (`## `/`### `) or list, and `Sop` is the
top-level H1 container. An SOP is built on the generic engine with the simple
surface used by GOL/RSK/QA/DEC (see `.specmgr/feat/feat-30-sop/README.md`
Design Notes).

Field declaration order on `Sop`/`RolesAndResponsibilities`/`Procedure`/
`RelatedArtifacts`/`Updates` enforces markdown order (Purpose -> Scope ->
Definitions -> Roles and Responsibilities (-> Accountable -> Responsible ->
Support -> Consulted -> Informed) -> Safety and Precautions -> Procedure
(-> Step 1: -> Step 2: -> ...) -> Related Artifacts (-> Requirements ->
Decisions -> Goals -> Acceptance Criteria -> Sops) -> More Information ->
Updates (-> entry 1 -> entry 2 -> ...)), since `models.md`'s
`MarkdownStr.from_text` distributes text among declared fields in that same
order.
"""

from __future__ import annotations

import re

from pydantic import Field, computed_field, model_validator

from ....models.md import (
    MarkdownListItem,
    MarkdownParagraph,
    MarkdownSection1,
    MarkdownSection2,
    MarkdownSection3,
    alias,
    AliasType,
)


class Purpose(MarkdownSection2):
    """`## Purpose` -- why this SOP exists and the outcome it produces.
    Mandatory, free-form prose (DEC's `Context` precedent: opaque free text,
    no declared nested fields).
    """


class Scope(MarkdownSection2):
    """`## Scope` -- what this SOP covers (and, optionally, what it does not).
    Optional, free-form prose."""


class Definitions(MarkdownSection2):
    """`## Definitions` -- terms-of-art used by this SOP, defined for the
    reader. Optional, free-form prose."""


class Accountable(MarkdownSection3):
    """`### Accountable` under `## Roles and Responsibilities` -- the single
    owner who is ultimately answerable for the SOP.

    A single mandatory paragraph (never a bullet list): exactly one owner,
    structurally discouraging multiple owners. See the general
    `specmgr://rasci` resource for RASCI role definitions.

    Parameters
    ----------
    value:
        The single paragraph naming the accountable party. Mandatory.
    """

    value: MarkdownParagraph = Field(
        description="The single paragraph naming the accountable party. Mandatory; never a bullet list."
    )


class Responsible(MarkdownSection3):
    """`### Responsible` under `## Roles and Responsibilities` -- those who do
    the work the SOP describes.

    A mandatory bullet list (>=1 entry). See the general `specmgr://rasci`
    resource for RASCI role definitions.

    Parameters
    ----------
    items:
        Bullet list naming the responsible parties; must contain at least one
        item.
    """

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Bullet list naming the responsible parties; must contain at least one item.",
    )


class Support(MarkdownSection3):
    """`### Support` under `## Roles and Responsibilities` -- those who
    provide resources or assistance to the responsible parties.

    An optional bullet list that MAY be present with zero list items (an
    intentional "considered, currently empty" placeholder distinct from
    omitting the heading entirely). See the general `specmgr://rasci` resource
    for RASCI role definitions.

    Parameters
    ----------
    items:
        Bullet list naming the support parties, or ``None`` when the heading
        is present with no items. Optional as a whole.
    """

    items: list[MarkdownListItem] | None = Field(
        default=None,
        description="Bullet list naming the support parties, or ``None`` when the heading is present "
        "with no items. Optional; the heading MAY appear with zero items.",
    )


class Consulted(MarkdownSection3):
    """`### Consulted` under `## Roles and Responsibilities` -- those whose
    opinions are sought before or during the work.

    An optional bullet list that MAY be present with zero list items (an
    intentional "considered, currently empty" placeholder distinct from
    omitting the heading entirely). See the general `specmgr://rasci` resource
    for RASCI role definitions.

    Parameters
    ----------
    items:
        Bullet list naming the consulted parties, or ``None`` when the heading
        is present with no items. Optional as a whole.
    """

    items: list[MarkdownListItem] | None = Field(
        default=None,
        description="Bullet list naming the consulted parties, or ``None`` when the heading is present "
        "with no items. Optional; the heading MAY appear with zero items.",
    )


class Informed(MarkdownSection3):
    """`### Informed` under `## Roles and Responsibilities` -- those who are
    kept up to date on progress or outcomes.

    An optional bullet list that MAY be present with zero list items (an
    intentional "considered, currently empty" placeholder distinct from
    omitting the heading entirely). See the general `specmgr://rasci` resource
    for RASCI role definitions.

    Parameters
    ----------
    items:
        Bullet list naming the informed parties, or ``None`` when the heading
        is present with no items. Optional as a whole.
    """

    items: list[MarkdownListItem] | None = Field(
        default=None,
        description="Bullet list naming the informed parties, or ``None`` when the heading is present "
        "with no items. Optional; the heading MAY appear with zero items.",
    )


@alias(value="Roles and Responsibilities", type=AliasType.LITERAL)
class RolesAndResponsibilities(MarkdownSection2):
    """`## Roles and Responsibilities` -- the RASCI responsibility assignment
    for this SOP. Optional as a whole; once present, `### Accountable` and
    `### Responsible` are both mandatory (strict-RACI "always has an owner and
    a doer"), while `### Support`/`### Consulted`/`### Informed` stay
    independently optional and MAY each be present with zero list items. See
    the general `specmgr://rasci` resource for RASCI role definitions.

    Parameters
    ----------
    accountable:
        `### Accountable` sub-section (single paragraph). Mandatory once this
        container is present.
    responsible:
        `### Responsible` sub-section (bullet list, >=1 item). Mandatory once
        this container is present.
    support:
        `### Support` sub-section (bullet list, MAY be empty). Optional.
    consulted:
        `### Consulted` sub-section (bullet list, MAY be empty). Optional.
    informed:
        `### Informed` sub-section (bullet list, MAY be empty). Optional.
    """

    accountable: Accountable = Field(
        description="`### Accountable` sub-section (single paragraph). Mandatory once this container is present."
    )
    responsible: Responsible = Field(
        description="`### Responsible` sub-section (bullet list, >=1 item). Mandatory once this container is present."
    )
    support: Support | None = Field(default=None, description="`### Support` sub-section. Optional; MAY be empty.")
    consulted: Consulted | None = Field(
        default=None, description="`### Consulted` sub-section. Optional; MAY be empty."
    )
    informed: Informed | None = Field(default=None, description="`### Informed` sub-section. Optional; MAY be empty.")


@alias(value="Safety and Precautions", type=AliasType.LITERAL)
class SafetyAndPrecautions(MarkdownSection2):
    """`## Safety and Precautions` -- warnings and precautions to read before
    following the procedure. Optional, free-form prose.

    The class name `SafetyAndPrecautions` does not match the heading's wording
    ("Safety and Precautions"), so the alias is pinned LITERAL (the implicit
    `SPACE_SEPARATED` alias would expect "Safety And Precautions").
    """


#: Matches a `### Step {N}: {name}` heading line as retained in a leaf
#: `MarkdownSection3`'s `.text` (first line), capturing the step number
#: (group 1) and its name (group 2). Mirrors `Step`'s own `@alias`, which
#: sees the heading text without the `###` marker, and DEC's `Option`'s
#: `_OPTION_HEADING_PATTERN` (the value is carried by the heading and
#: extracted at access time, never stored).
_STEP_HEADING_PATTERN = re.compile(r"### Step (\d+): (.+)")


@alias(value=r"^Step \d+: .+$", type=AliasType.REGEX)
class Step(MarkdownSection3):
    """`### Step {N}: {name}` under `## Procedure` -- one step of the procedure.

    A leaf H3 section: the number and the name both live in the heading
    itself (e.g. `### Step 1: Provision the account`), constrained by the
    regex `@alias` above and enforced by `match_alias` (`re.fullmatch`) at
    parse time -- a missing colon/title (`### Step 1`), a non-numeric number
    (`### Step one: X`), or a title-less heading (`### Step 1:`) all fail the
    parse eagerly. The number may carry leading zeros (`### Step 01: X`); it
    is normalized to an integer by the computed `number` below. Step numbers
    need not be contiguous (gaps are allowed, numbers are never renumbered);
    duplicates are rejected by `Sop`'s own after-validator (the
    `ValidationError` channel). Any body text under the heading is absorbed
    into the leaf like every other leaf `MarkdownSection`.

    Parameters
    ----------
    number:
        Computed. The step's number (e.g. `1` for `### Step 1: X`, also `1`
        for `### Step 01: X`). Never stored separately -- derived from the
        retained heading text.
    name:
        Computed. The step's name (the heading text after `": "`). Never
        stored separately -- derived from the retained heading text.
    """

    @computed_field  # type: ignore
    @property
    def number(self) -> int:
        """The step's number carried by this heading (e.g. `1` for `### Step 1: X`).

        Returns:
            The integer number parsed from the retained heading text
            (leading zeros accepted: `### Step 01: X` yields `1`).

        Raises:
            AssertionError: the retained heading text does not match
                `Step`'s declared `@alias` (unreachable via the engine:
                `match_alias` already enforced it at parse time).
        """
        heading_line = self.text.splitlines()[0].strip() if self.text else ""
        match = _STEP_HEADING_PATTERN.fullmatch(heading_line)
        assert match, f"Step: expected heading '### Step N: <name>', got {heading_line!r}"
        result: int = int(match.group(1))
        return result

    @computed_field  # type: ignore
    @property
    def name(self) -> str:
        """The step's name carried by this heading (e.g. `X` for `### Step 1: X`).

        Returns:
            The name parsed from the retained heading text (the heading
            text after `": "`, colons inside the name included).

        Raises:
            AssertionError: the retained heading text does not match
                `Step`'s declared `@alias` (unreachable via the engine:
                `match_alias` already enforced it at parse time).
        """
        heading_line = self.text.splitlines()[0].strip() if self.text else ""
        match = _STEP_HEADING_PATTERN.fullmatch(heading_line)
        assert match, f"Step: expected heading '### Step N: <name>', got {heading_line!r}"
        result: str = match.group(2)
        return result


class Procedure(MarkdownSection2):
    """`## Procedure` -- the structured, ordered set of steps a reader follows.
    Mandatory; present only if it carries at least one `### Step {N}: {name}`
    entry (``min_length=1``) -- an H2 with zero steps is a structural error.

    Parameters
    ----------
    steps:
        The `### Step {N}: {name}` entries, in document order. Requires at
        least one step.
    """

    steps: list[Step] = Field(
        min_length=1,
        description="Dynamic collection of `### Step {N}: {name}` entries, in document order. "
        "Must contain at least one step.",
    )


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
    """`### Goals` under Related Artifacts -- bullet list of cross-references
    to goals, one per line (e.g. "GOL-0007: <title>")."""

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


class Sops(MarkdownSection3):
    """`### Sops` under Related Artifacts -- bullet list of cross-references to
    other, related/superseding SOPs, one per line (e.g. "SOP-0042: <title>").
    A self-cross-reference sub-list (GOL's self-referencing `Goals` sub-list
    precedent)."""

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Bullet list of cross-references to other SOPs, one per line "
        '(e.g. "SOP-0042: <title>"); must contain at least one item.',
    )


class RelatedArtifacts(MarkdownSection2):
    """`## Related Artifacts` -- container for five independent, all-optional
    `### ` cross-reference lists (requirements/decisions/goals/acceptance
    criteria/sops). Optional as a whole; no consistency check is enforced
    between the sub-lists. The `### Sops` sub-list is a self-cross-reference
    (a `sop` document may reference other, related/superseding SOPs).
    """

    requirements: Requirements | None = Field(default=None, description="`### Requirements` sub-section. Optional.")
    decisions: Decisions | None = Field(default=None, description="`### Decisions` sub-section. Optional.")
    goals: Goals | None = Field(default=None, description="`### Goals` sub-section. Optional.")
    acceptance_criteria: AcceptanceCriteria | None = Field(
        default=None, description="`### Acceptance Criteria` sub-section. Optional."
    )
    sops: Sops | None = Field(default=None, description="`### Sops` sub-section (self-cross-reference). Optional.")


class MoreInformation(MarkdownSection2):
    """`## More Information` -- free-form optional supplementary text, no
    fixed format. Optional."""


#: Matches a `### {ISO8601 timestamp} ( - | : ) {title}` heading line as
#: retained in a composite `MarkdownSection3`'s `.text` (which carries the
#: heading's inline content without the `###` marker), capturing the
#: timestamp (named group `timestamp`) and the title (named group `title`).
#: Mirrors `UpdateEntry`'s own `@alias`, which sees the heading text without
#: the `###` marker, and DEC's `Option`/RSK's `Probability`/`Impact`
#: computed-field precedent (the value is carried by the heading and
#: extracted at access time, never stored). Unlike DEC's leaf `Option`,
#: `UpdateEntry` is a *composite* (it has a mandatory `content` paragraph),
#: so its `.text` returns only the heading text, not the full extent --
#: hence no `### ` prefix here.
_UPDATE_ENTRY_HEADING_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}))(?: - | : )(?P<title>.+)"
)


@alias(value=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})(?: - | : ).+$", type=AliasType.REGEX)
class UpdateEntry(MarkdownSection3):
    """`### {ISO8601 timestamp} ( - | : ) {title}` under `## Updates` -- one update entry.

    The H3 heading text carries an ISO8601 timestamp and a title, joined by
    either ``" - "`` (space, hyphen, space) or ``" : "`` (space, colon,
    space): e.g. `### 2026-08-30 14:30:00.000+02:00 - Approved` or
    `### 2026-08-30 14:30:00.000+02:00 : Approved`. The em-dash separator is
    rejected. The format is ``yyyy-MM-dd HH:mm:ss.fff`` with an explicit UTC
    offset (``+02:00``, ``-05:00``) or ``Z`` for UTC -- deliberately **not**
    the same format as frontmatter ``created``/``updated`` (which keep the
    shared generic tools' format); this format is scoped to `## Updates`
    entry headings only, which are hand/LLM-authored body content.
    Constrained by the regex `@alias` above and enforced by `match_alias`
    (`re.fullmatch`) at parse time -- a wrong timestamp format, a missing
    offset, an em-dash separator, or a missing `` - ``/`` : `` title all
    fail the parse eagerly.

    Parameters
    ----------
    content:
        The lead paragraph right after the H3 heading -- this entry's own
        update text. Mandatory.
    timestamp:
        Computed. The ISO8601 timestamp carried by the heading. Never stored
        separately -- derived from the retained heading text.
    title:
        Computed. The title carried by the heading (the text after
        ``" - "``/``" : "``). Never stored separately -- derived from the
        retained heading text.

    Raises:
        AssertionError: the retained heading text does not match
            `UpdateEntry`'s declared `@alias` (unreachable via the engine:
            `match_alias` already enforced it at parse time).
    """

    content: MarkdownParagraph = Field(
        description="The lead paragraph directly under the H3 heading -- this entry's own update text. Mandatory."
    )

    @computed_field  # type: ignore
    @property
    def timestamp(self) -> str:
        """The ISO8601 timestamp carried by this heading (e.g. `2026-08-30 14:30:00.000+02:00`).

        Returns:
            The timestamp parsed from the retained heading text.

        Raises:
            AssertionError: the retained heading text does not match
                `UpdateEntry`'s declared `@alias` (unreachable via the
                engine: `match_alias` already enforced it at parse time).
        """
        heading_line = self.text.splitlines()[0].strip() if self.text else ""
        match = _UPDATE_ENTRY_HEADING_PATTERN.fullmatch(heading_line)
        assert match, f"UpdateEntry: expected heading '### <ISO8601> ( - | : ) <title>', got {heading_line!r}"
        result: str = match.group("timestamp")
        return result

    @computed_field  # type: ignore
    @property
    def title(self) -> str:
        """The title carried by this heading (e.g. `Approved` for `### 2026-08-30 14:30:00.000+02:00 - Approved`).

        Returns:
            The title parsed from the retained heading text (the text after
            ``" - "``/``" : "``).

        Raises:
            AssertionError: the retained heading text does not match
                `UpdateEntry`'s declared `@alias` (unreachable via the
                engine: `match_alias` already enforced it at parse time).
        """
        heading_line = self.text.splitlines()[0].strip() if self.text else ""
        match = _UPDATE_ENTRY_HEADING_PATTERN.fullmatch(heading_line)
        assert match, f"UpdateEntry: expected heading '### <ISO8601> ( - | : ) <title>', got {heading_line!r}"
        result: str = match.group("title")
        return result


class Updates(MarkdownSection2):
    """`## Updates` -- a dynamic list of ISO8601-timestamped `### ` update
    entries. Optional as a whole, and the last section of the document if
    present.

    Mirrors `tsk`/`dec`'s `Updates`/`RecentUpdates` container shape: no
    dedicated per-entry tools (no `option_create`/`option_list` equivalent)
    -- entries are appended by editing the whole body.

    Parameters
    ----------
    updates:
        The dynamic collection of `### ` entries, in document order. Requires
        at least one entry (``min_length=1``) -- an H2 with zero entries is
        a structural error.
    """

    updates: list[UpdateEntry] = Field(
        min_length=1,
        description="Dynamic collection of `### {ISO8601 timestamp} ( - | : ) {title}` entries, in document "
        "order. Must contain at least one entry.",
    )


@alias(value=".+", type=AliasType.REGEX)
class Sop(MarkdownSection1):
    """The `sop` body: a single H1 section with the fields below.

    The H1 heading text is free-form. Built on the generic `models.md` engine
    with the simple surface used by GOL/RSK/QA/DEC -- see the module
    docstring.

    Parameters
    ----------
    purpose:
        `## Purpose`. Mandatory.
    scope:
        `## Scope`. Optional.
    definitions:
        `## Definitions`. Optional.
    roles_and_responsibilities:
        `## Roles and Responsibilities` (RASCI composite). Optional.
    safety_and_precautions:
        `## Safety and Precautions`. Optional.
    procedure:
        `## Procedure` (`### Step {N}: {name}` entries, >=1). Mandatory.
    related_artifacts:
        `## Related Artifacts` (five all-optional H3 bullet lists). Optional.
    more_information:
        `## More Information`. Optional.
    updates:
        `## Updates` (>=1 entry if present). Optional; last section.
    """

    purpose: Purpose = Field(description="`## Purpose` section. Mandatory.")
    scope: Scope | None = Field(default=None, description="`## Scope` section. Optional.")
    definitions: Definitions | None = Field(default=None, description="`## Definitions` section. Optional.")
    roles_and_responsibilities: RolesAndResponsibilities | None = Field(
        default=None, description="`## Roles and Responsibilities` section (RASCI composite). Optional."
    )
    safety_and_precautions: SafetyAndPrecautions | None = Field(
        default=None, description="`## Safety and Precautions` section. Optional."
    )
    procedure: Procedure = Field(description="`## Procedure` section (>=1 step). Mandatory.")
    related_artifacts: RelatedArtifacts | None = Field(
        default=None, description="`## Related Artifacts` section. Optional."
    )
    more_information: MoreInformation | None = Field(
        default=None, description="`## More Information` section. Optional."
    )
    updates: Updates | None = Field(default=None, description="`## Updates` section. Optional; last.")

    @model_validator(mode="after")
    def _validate_step_numbers_unique(self) -> Sop:
        """Reject duplicate step numbers across `## Procedure`.

        `Step.number`/`.name` are `@computed_field`s -- Pydantic only
        evaluates a computed field's getter on access (e.g. during
        `model_dump()`/serialization), never during construction/validation
        of the underlying model itself. Accessing `.number` here therefore
        both forces every step's number to evaluate eagerly and checks the
        cross-field invariant: no two steps may carry the same number
        (`### Step 1` and `### Step 01` are the same number and therefore a
        duplicate). Gaps are allowed (steps are never renumbered). A
        duplicate raises `ValueError`, which Pydantic channels into
        `ValidationError` (the value-violation channel, mirroring DEC's
        `Decision` option-number after-validator and the RSK cross-field
        precedent). `procedure` is mandatory, so `self.procedure.steps` is
        always present.
        """
        seen: set[int] = set()
        for step in self.procedure.steps:
            number = step.number
            if number in seen:
                raise ValueError(f"step number {number} is used by more than one `### Step` heading")
            seen.add(number)
        return self
