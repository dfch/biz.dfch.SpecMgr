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

"""Requirement (REQ) models: whole-section fields under a single H1.

Built on the generic `models.md` `MarkdownSectionN`/`MarkdownParagraph`/
`MarkdownListItem` engine: each class below models one markdown heading
(`## `/`### `) or list, and `Requirement` is the top-level H1 container.
"""

import re

from pydantic import Field, field_validator

from ....models.md import (
    MarkdownSection1,
    MarkdownSection2,
    MarkdownSection3,
    MarkdownParagraph,
    MarkdownListItem,
    alias,
    AliasType,
)


class Description(MarkdownSection2):
    """`## Description` -- free-form prose giving context/rationale for the
    requirement statement above it. Mandatory.
    """


class Characteristics(MarkdownSection2):
    """`## Characteristics` -- bullet list of ISO 25010:2023 quality attributes this
    requirement concerns ("Functional Suitability", "Performance", "User Interaction",
    "Compatibility", "Maintainability", "Security", "Reliability", "Safety").
    Mandatory. At least one characteristic.
    """

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Bullet list of ISO 25010:2023 quality attributes; must contain at least one item.",
    )


_LEVEL_PATTERN = r"^(MUST|SHOULD|MUST NOT|SHOULD NOT|MAY)$"


class Level(MarkdownSection2):
    """`## Level` -- single-line value giving the requirement's obligation
    strength (e.g. "MUST"). Mandatory.
    """

    value: MarkdownParagraph = Field(
        description='Single-line value giving the requirement\'s obligation strength (e.g. "MUST").',
    )

    @field_validator("value")
    @classmethod
    def _validate_value(cls, value: MarkdownParagraph) -> MarkdownParagraph:
        """Enforce `_LEVEL_PATTERN` against `value.text`.

        `value` is a `MarkdownParagraph` (a model, not a `str`), so a
        `Field(pattern=...)` string constraint cannot be applied directly --
        pydantic only applies `pattern` to string-typed schemas. This
        validator re-implements the same check against `value.text`, the
        paragraph's own inline text.
        """
        if not re.fullmatch(_LEVEL_PATTERN, value.text):
            raise ValueError(f"value must match pattern {_LEVEL_PATTERN!r}, got {value.text!r}")
        return value


_PRIORITY_PATTERN = r"^(0|[1-9][0-9]?)$"  # 0-99, no leading zeros other than "0" itself


class Priority(MarkdownSection2):
    """`## Priority` -- single-line value giving the requirement's relative
    priority (e.g. a numeric rank). Optional.
    """

    value: MarkdownParagraph = Field(
        description=(
            "Single-line value giving the requirement's relative importance (0 to 99, lower number"
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
    requirements. Optional.
    """

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Bullet list of free-form labels for grouping/filtering requirements; "
        "must contain at least one item.",
    )


class Source(MarkdownSection2):
    """`## Source` -- single-line value naming the origin/authority of this
    requirement. Mandatory.
    """

    value: MarkdownParagraph = Field(description="Single-line value naming the origin/authority of this requirement.")


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
class Requirement(MarkdownSection1):
    """The requirement body: a single H1 section with the fields below.

    The H1 heading text is free-form. `@alias(value=".+", type=AliasType.REGEX)`
    matches any non-blank title.

    Parameters
    ----------
    statement:
        The lead paragraph right after the H1. Mandatory.
    description:
        `## Description`. Mandatory.
    characteristics:
        `## Characteristics`. Mandatory.
    level:
        `## Level`. Mandatory.
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
        "requirement statement itself. Mandatory."
    )
    description: Description = Field(description="`## Description` section. Mandatory.")
    characteristics: Characteristics = Field(description="`## Characteristics` section. Mandatory.")
    level: Level = Field(description="`## Level` section. Mandatory.")
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
