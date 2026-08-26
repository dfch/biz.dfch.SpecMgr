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

"""Goal (GOL) models: whole-section fields under a single H1.

Built on the generic `models.md` `MarkdownSectionN`/`MarkdownParagraph`/
`MarkdownListItem` engine: each class below models one markdown heading
(`## `/`### `) or list, and `Goal` is the top-level H1 container.

`Goal` mirrors `req/models/v1/body.py::Requirement` with exactly two
deliberate omissions (see the feature README's Scope/Design Notes): no
`Characteristics` section (ISO 25010:2023 quality attributes are a
requirement-level attribute -- a business goal states *what* to achieve,
not *which quality dimension* it loads) and no `Level` section (RFC 2119
obligation strength is implicit -- a goal is always a MUST). Consequently
the only mandatory body fields are `statement` and `Source`; the rest are
optional. Field declaration order on `Goal`/`RelatedArtifacts` enforces
markdown order (statement -> `Description` -> `Priority` -> `Tags` ->
`Source` -> `Related Artifacts` -> `More Information` -> `Notes`, and
within `RelatedArtifacts`: `Requirements` -> `Decisions` -> `Goals` ->
`Acceptance Criteria`), since `models.md`'s `MarkdownStr.from_text`
distributes text among declared fields in that same order.
"""

import re

from pydantic import Field, field_validator

from ....models.md import (
    MarkdownSection1,
    MarkdownSection2,
    MarkdownSection2WithComment,
    MarkdownSection3,
    MarkdownParagraph,
    MarkdownListItem,
    MarkdownListItemWithNotes,
    MarkdownComment,
    alias,
    AliasType,
)


class Description(MarkdownSection2):
    """`## Description` -- free-form prose giving context/rationale for the
    goal statement above it. Optional.
    """


_PRIORITY_PATTERN = r"^(0|[1-9][0-9]?)$"  # 0-99, no leading zeros other than "0" itself


class Priority(MarkdownSection2WithComment):
    """`## Priority` -- single-line value giving the goal's relative
    priority (e.g. a numeric rank). Optional. May be preceded by an
    explanatory HTML comment (e.g. describing the numeric range).
    """

    comment: MarkdownComment | None = Field(
        default=None,
        description="Optional explanatory HTML comment (`<!-- ... -->`) preceding `value`, "
        "e.g. describing the numeric range.",
    )
    value: MarkdownParagraph = Field(
        description=(
            "Single-line value giving the goal's relative importance (0 to 99, lower number"
            " is more important, e.g. 50)."
        ),
    )

    @field_validator("value")
    @classmethod
    def _validate_value(cls, value: MarkdownParagraph) -> MarkdownParagraph:
        """Enforce `_PRIORITY_PATTERN` against `value.text`.

        `value` is a `MarkdownParagraph` (a model, not a `str`), so a
        `Field(pattern=...)` string constraint cannot be applied directly --
        pydantic only applies `pattern` to string-typed schemas. This
        validator re-implements the same check against `value.text`, the
        paragraph's own inline text.
        """
        if not re.fullmatch(_PRIORITY_PATTERN, value.text):
            raise ValueError(f"value must match pattern {_PRIORITY_PATTERN!r}, got {value.text!r}")
        return value


class Tags(MarkdownSection2):
    """`## Tags` -- bullet list of free-form labels for grouping/filtering
    goals. Optional.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of free-form labels for grouping/filtering goals; must contain at least one item.",
    )


class Source(MarkdownSection2):
    """`## Source` -- single-line value naming the origin/authority of this
    goal. Mandatory.
    """

    value: MarkdownParagraph = Field(description="Single-line value naming the origin/authority of this goal.")


class Requirements(MarkdownSection3):
    """`### Requirements` under Related Artifacts -- bullet list of
    cross-references to other requirements, one per line
    (e.g. "REQ-9687: <title>").
    """

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Bullet list of cross-references to other requirements, one per line "
        '(e.g. "REQ-9687: <title>"); must contain at least one item.',
    )


class Decisions(MarkdownSection3):
    """`### Decisions` under Related Artifacts -- bullet list of
    cross-references to decisions, one per line (e.g. "DEC-2703: <title>").
    """

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Bullet list of cross-references to decisions, one per line "
        '(e.g. "DEC-2703: <title>"); must contain at least one item.',
    )


class AcceptanceCriteria(MarkdownSection3):
    """`### Acceptance Criteria` under Related Artifacts -- bullet list of
    cross-references to acceptance criteria, one per line
    (e.g. "ACC-1234: <title>").
    """

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Bullet list of cross-references to acceptance criteria, one per line "
        '(e.g. "ACC-1234: <title>"); must contain at least one item.',
    )


class Goals(MarkdownSection3):
    """`### Goals` under Related Artifacts -- bullet list of
    cross-references to goals, one per line (e.g. "GOL-0007: <title>").
    """

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Bullet list of cross-references to goals, one per line "
        '(e.g. "GOL-0007: <title>"); must contain at least one item.',
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


class MoreInformation(MarkdownSection2):
    """`## More Information` -- free-form optional supplementary text, no
    fixed format. Optional.
    """


class Notes(MarkdownSection2):
    """`## Notes` -- free-form optional remarks (e.g. change history). Optional."""


@alias(value=".+", type=AliasType.REGEX)
class Goal(MarkdownSection1):
    """The goal body: a single H1 section with the fields below.

    The H1 heading text is free-form. Mirrors `Requirement` (REQ) minus
    `Characteristics` and minus `Level` -- see the module docstring.

    Parameters
    ----------
    statement:
        The lead paragraph right after the H1. Mandatory.
    description:
        `## Description`. Optional.
    priority:
        `## Priority`. Optional.
    tags:
        `## Tags`. Optional.
    source:
        `## Source`. Mandatory.
    related_artifacts:
        `## Related Artifacts`. Optional.
    more_information:
        `## More Information`. Optional.
    notes:
        `## Notes`. Optional.
    """

    statement: MarkdownParagraph = Field(
        description="The lead paragraph directly under the H1, before any H2 section -- the "
        "goal statement itself. Mandatory."
    )
    description: Description | None = Field(default=None, description="`## Description` section. Optional.")
    priority: Priority | None = Field(default=None, description="`## Priority` section. Optional.")
    tags: Tags | None = Field(default=None, description="`## Tags` section. Optional.")
    source: Source = Field(description="`## Source` section. Mandatory.")
    related_artifacts: RelatedArtifacts | None = Field(
        default=None, description="`## Related Artifacts` section. Optional."
    )
    more_information: MoreInformation | None = Field(
        default=None, description="`## More Information` section. Optional."
    )
    notes: Notes | None = Field(default=None, description="`## Notes` section. Optional.")
