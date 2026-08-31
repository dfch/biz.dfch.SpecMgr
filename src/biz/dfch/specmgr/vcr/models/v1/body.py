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

"""Verification Case Record (VCR) body models: whole-section fields under a single H1.

Built on the generic `models.md` `MarkdownSection1WithComment`/`MarkdownSection2`/
`MarkdownSection2WithComment`/`MarkdownSection3`/`MarkdownSection4`/
`MarkdownParagraph`/`MarkdownListItem` engine, mirroring `dec/models/v1/body.py`'s
"one class per heading" shape and `rsk/models/v1/body.py`'s free-form-H1 +
optional-leading-comment pattern. `Vcr` is the top-level H1 container:

```
# {H1 title}
<!-- optional leading comment -->        comment: MarkdownComment | None

## Verifies                              verifies: Verifies
<!-- optional leading comment -->
REQ|UC <uuid>: <title>
{mandatory paraphrase}
## Coverage                              coverage: Coverage
{full | partial | none}
## Acceptance Criteria                   acceptance_criteria: AcceptanceCriteria (>=1 entry)
### AC-NNN (Method): <criterion text>
{free-form description}                  (optional, per AC)
#### Test Steps                          (optional, per AC)
## More Information                      more_information: MoreInformation | None
{free-form}
## Updates                                updates: Updates | None
<!-- optional leading comment -->
### {free-form title}                    (>=1 entry if present)
```

Field declaration order on `Vcr` enforces the markdown order (title ->
optional comment (inherited) -> Verifies -> Coverage -> Acceptance Criteria
-> optional More Information -> optional Updates), since `models.md`'s
`MarkdownStr.from_text` distributes text among declared fields in that same
order. See `.specmgr/feat/feat-33-vcr/README.md`'s Design Notes for the full
schema rationale (REQ-001..004).
"""

from __future__ import annotations

import re

from pydantic import Field, computed_field, field_validator, model_validator

from ....models.md import (
    MarkdownListItem,
    MarkdownParagraph,
    MarkdownSection1WithComment,
    MarkdownSection2,
    MarkdownSection2WithComment,
    MarkdownSection3,
    MarkdownSection4,
    alias,
    AliasType,
)

#: Matches `## Verifies`' single-line `value` paragraph: exactly one `REQ`
#: or `UC` cross-reference, tagged with its type, followed by a standard
#: 8-4-4-4-12 hex UUID and a title (REQ-001). No id-prefix precedent existed
#: elsewhere in the codebase to reuse for the UUID shape, so this introduces
#: one -- see `.specmgr/feat/feat-33-vcr/README.md` Design Notes' persisted
#: `Verifies` class sketch.
_VERIFIES_PATTERN = r"^(REQ|UC) [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}: .+$"


class Verifies(MarkdownSection2WithComment):
    """`## Verifies` -- exactly one REQ or UC cross-reference. Mandatory.

    Modeled as a single non-list value field (SOP's `Accountable` / RSK's
    `Strategy`&`Owner` / REQ&GOL's `Source` precedent), not a bullet list
    -- a single-value field is structurally incapable of holding more than
    one reference, so no cardinality `model_validator` is needed. `value`
    and `notes` are two mandatory fields in fixed declaration order,
    mirroring RSK's `Assessment.probability`/`.impact` two-mandatory-
    fields-in-sequence idiom (just `MarkdownParagraph` instead of
    `Probability`/`Impact`).

    Parameters
    ----------
    comment:
        Optional explanatory HTML comment (`<!-- ... -->`). Inherited from
        `MarkdownSection2WithComment`.
    value:
        Single-line `"REQ|UC <uuid>: <title>"`. Mandatory.
        `field_validator`-regex-checked against `_VERIFIES_PATTERN`
        (standard 8-4-4-4-12 hex UUID shape -- no UUID-format precedent
        existed elsewhere in the codebase to reuse, so this introduces
        one).
    notes:
        One-paragraph paraphrase of why this REQ/UC is verified here.
        Mandatory (unlike `MarkdownListItemWithNotes.notes`, which is
        optional).
    """

    value: MarkdownParagraph = Field(description='Single-line value: "REQ|UC <uuid>: <title>".')
    notes: MarkdownParagraph = Field(description="Mandatory one-paragraph paraphrase.")

    @field_validator("value")
    @classmethod
    def _validate_value(cls, value: MarkdownParagraph) -> MarkdownParagraph:
        """Enforce `_VERIFIES_PATTERN` against `value.text` (mirrors `req.Level`/`rsk.Strategy`)."""
        if not re.fullmatch(_VERIFIES_PATTERN, value.text):
            raise ValueError(f"value must match pattern {_VERIFIES_PATTERN!r}, got {value.text!r}")
        return value


#: `## Coverage`'s closed 3-value set (REQ-002) -- `full`/`partial`/`none`,
#: mirroring RSK's `## Strategy` TARA 4-value pattern but for verification
#: coverage instead of a risk-response strategy.
_COVERAGE_PATTERN = r"^(full|partial|none)$"


class Coverage(MarkdownSection2):
    """`## Coverage` -- single-line closed-vocabulary coverage assessment. Mandatory.

    One of the three closed values: `full`, `partial`, `none`. There is no
    separate pass/fail/waived outcome field anywhere in this domain --
    `## Coverage` is the only outcome signal (REQ-002).
    """

    value: MarkdownParagraph = Field(description="Single-line coverage assessment. One of `full`, `partial`, `none`.")

    @field_validator("value")
    @classmethod
    def _validate_value(cls, value: MarkdownParagraph) -> MarkdownParagraph:
        """Enforce `_COVERAGE_PATTERN` against `value.text` (mirrors `rsk.Strategy`)."""
        if not re.fullmatch(_COVERAGE_PATTERN, value.text):
            raise ValueError(f"value must match pattern {_COVERAGE_PATTERN!r}, got {value.text!r}")
        return value


class TestSteps(MarkdownSection4):
    """`#### Test Steps` under an `AcceptanceCriterion` -- numbered verification procedure. Optional.

    The class name's implicit `AliasType.SPACE_SEPARATED` derivation
    ("Test Steps") already matches this heading's own wording, so no
    explicit `@alias` is declared (same as DEC's `Confirmation`/
    `Consequences`).

    Parameters
    ----------
    items:
        The numbered procedure list, in document order. Must contain at
        least one item (``min_length=1``) -- an H4 with zero steps is a
        structural error.
    """

    items: list[MarkdownListItem] = Field(
        min_length=1,
        description="Numbered procedure list, in document order. Must contain at least one item.",
    )


#: Matches a `AC-NNN (Method): <criterion text>` heading as retained by
#: `AcceptanceCriterion.text` (the composite-section heading text, marker
#: already stripped -- see `AcceptanceCriterion`'s own docstring for why
#: this differs from DEC's `Option`/RSK's `Probability`/`Impact`, which are
#: leaf sections and therefore keep the `###`/body text in `.text` too),
#: capturing the 3-digit number (group 1) and the closed DTAIS method word
#: (group 2). Confirmed against 6 valid/8 invalid hand-written heading
#: fixtures via a throwaway `/tmp` scratch script during Phase 0 (Task 0.2)
#: -- see `.specmgr/feat/feat-33-vcr/README.md`'s Updates log.
_AC_HEADING_PATTERN = r"AC-(\d{3}) \((Demonstration|Test|Analysis|Inspection|Special)\): .+"
_AC_HEADING_RE = re.compile(_AC_HEADING_PATTERN)


@alias(value=rf"^{_AC_HEADING_PATTERN}$", type=AliasType.REGEX)
class AcceptanceCriterion(MarkdownSection3):
    """`### AC-NNN (Method): <criterion text>` under `## Acceptance Criteria` -- one verification criterion.

    The number, method, and criterion text all live in the heading itself
    (e.g. `### AC-001 (Test): The revoke endpoint returns 204 within 1s`),
    constrained by the regex `@alias` above and enforced by `match_alias`
    (`re.fullmatch`) at parse time -- a missing/out-of-range/malformed
    number, an unknown method word, or a title-less heading all fail the
    parse eagerly (REQ-003). AC numbers need not be contiguous (gaps are
    allowed, numbers are never renumbered); duplicates are rejected by
    `Vcr`'s own after-validator (the `ValidationError` channel, mirroring
    DEC's `Decision._validate_option_numbers_unique`).

    Unlike DEC's `Option`/RSK's `Probability`/`Impact` (all *leaf* sections
    with zero other declared fields, so their own `.text` computed property
    returns the *complete* extent verbatim, heading marker and any body
    text both included), this class declares two other fields
    (`description`, `test_steps`), making it a *composite* section: its own
    `.text` therefore returns only the heading's own inline content (marker
    stripped, body text excluded -- see `MarkdownSection.text`'s composite
    branch). `number`/`method` below are matched against that heading-only
    `.text` directly, not `.text.splitlines()[0]` -- the DEC/RSK idiom's
    exact mechanics don't apply verbatim here because of this leaf/composite
    difference, even though the underlying idea (compute a value from the
    retained heading text via a private module-level compiled regex) is the
    same. A consequence: an `AcceptanceCriterion`'s body may contain nothing
    besides an optional free-form `description` paragraph followed by an
    optional `#### Test Steps` -- both independently optional (e.g. one
    criterion may carry only a description, another only `Test Steps`,
    another both, another neither), in that fixed declaration order.

    Parameters
    ----------
    description:
        The lead paragraph directly under the heading -- free-form prose
        elaborating on the criterion beyond what fits in the heading
        itself (mirrors `MoreInformation`'s "free-form, no fixed format"
        tone). Optional; independent of `test_steps`.
    test_steps:
        `#### Test Steps` sub-section (a numbered verification procedure).
        Optional; independent of `description`.
    number:
        Computed. The criterion's 3-digit number (e.g. `1` for
        `### AC-001 (Test): ...`). Never stored separately -- derived from
        the retained heading text.
    method:
        Computed. The closed DTAIS method word carried by the heading
        (e.g. `"Test"` for `### AC-001 (Test): ...`), exactly as written
        (not lowercased/normalized). Never stored separately -- derived
        from the retained heading text.
    """

    description: MarkdownParagraph | None = Field(
        default=None,
        description="The lead paragraph directly under the heading -- free-form prose elaborating on the "
        "criterion. Optional; independent of `test_steps`.",
    )
    test_steps: TestSteps | None = Field(
        default=None, description="`#### Test Steps` sub-section. Optional; independent of `description`."
    )

    @computed_field  # type: ignore
    @property
    def number(self) -> int:
        """The criterion's 3-digit number carried by this heading (e.g. `1` for `### AC-001 (Test): ...`).

        Returns:
            The integer number parsed from the retained heading text.

        Raises:
            AssertionError: the retained heading text does not match
                `AcceptanceCriterion`'s declared `@alias` (unreachable via
                the engine: `match_alias` already enforced it at parse time).
        """
        match = _AC_HEADING_RE.fullmatch(self.text)
        assert match, f"AcceptanceCriterion: expected heading 'AC-NNN (Method): <text>', got {self.text!r}"
        result: int = int(match.group(1))
        return result

    @computed_field  # type: ignore
    @property
    def method(self) -> str:
        """The closed DTAIS method word carried by this heading (e.g. `"Test"` for `### AC-001 (Test): ...`).

        Returns:
            The method word parsed from the retained heading text, exactly
            as written (not lowercased/normalized).

        Raises:
            AssertionError: the retained heading text does not match
                `AcceptanceCriterion`'s declared `@alias` (unreachable via
                the engine: `match_alias` already enforced it at parse time).
        """
        match = _AC_HEADING_RE.fullmatch(self.text)
        assert match, f"AcceptanceCriterion: expected heading 'AC-NNN (Method): <text>', got {self.text!r}"
        result: str = match.group(2)
        return result


@alias(value="Acceptance Criteria", type=AliasType.LITERAL)
class AcceptanceCriteria(MarkdownSection2):
    """`## Acceptance Criteria` -- the dynamic `### AC-NNN (Method): ...` collection. Mandatory.

    Requires at least one entry (``min_length=1``, REQ-003) -- an H2 with
    zero criteria is a structural error.

    Parameters
    ----------
    criteria:
        The `### AC-NNN (Method): <criterion text>` entries, in document
        order. Must contain at least one entry.
    """

    criteria: list[AcceptanceCriterion] = Field(
        min_length=1,
        description="Dynamic collection of `### AC-NNN (Method): <criterion text>` entries, in document order. "
        "Must contain at least one entry.",
    )


class MoreInformation(MarkdownSection2):
    """`## More Information` -- free-form optional supplementary text, no fixed format. Optional."""


@alias(value=".+", type=AliasType.REGEX)
class UpdateEntry(MarkdownSection3):
    """`### {free-form title}` under `## Updates` -- one update entry.

    The H3 heading text is free-form (date-led titles like
    `2026-08-31 — Created` are convention, not enforced). Mirrors DEC's
    `UpdateEntry` shape.

    Parameters
    ----------
    content:
        The lead paragraph right after the H3 heading -- this entry's own
        update text. Mandatory.
    """

    content: MarkdownParagraph = Field(
        description="The lead paragraph directly under the H3 heading -- this entry's own update text. Mandatory."
    )


class Updates(MarkdownSection2WithComment):
    """`## Updates` -- a dynamic list of free-form-titled `### ` update entries. Optional as a whole, and the
    last section of the document if present.

    Unlike DEC's own `Updates` (a plain `MarkdownSection2`, since
    `dec_example.md` carries no comment there), VCR's own `example.md`/
    `template.md` (Phase 0) both demonstrate a permanent "newest first"
    ordering-hint HTML comment directly under this heading -- the same
    structural-anchor role `feat`'s `Updates(MarkdownSection3WithComment)`
    already gives its own comment (not authoring guidance, see
    `.specmgr/feat/feat-33-vcr/README.md` Design Notes' "clean-example
    convention" bullet), so this is `MarkdownSection2WithComment` instead.
    No dedicated per-entry tools -- entries are appended by editing the
    whole body.

    Parameters
    ----------
    comment:
        Optional explanatory HTML comment (`<!-- ... -->`), e.g.
        `<!-- Newest entry first -- prepend new entries directly below
        this comment. -->`. Inherited from `MarkdownSection2WithComment`.
    updates:
        The dynamic collection of `### ` entries, in document order. Requires
        at least one entry (``min_length=1``) -- an H2 with zero entries is
        a structural error.
    """

    updates: list[UpdateEntry] = Field(
        min_length=1,
        description="Dynamic collection of `### {free-form title}` entries, in document order. "
        "Must contain at least one entry.",
    )


@alias(value=".+", type=AliasType.REGEX)
class Vcr(MarkdownSection1WithComment):
    """The `vcr` body: a single H1 section with the fields below.

    The H1 heading text is free-form. `comment` is inherited from
    `MarkdownSection1WithComment` (see its own docstring) -- not redeclared
    here.

    Parameters
    ----------
    comment:
        Optional explanatory HTML comment (`<!-- ... -->`) preceding
        `verifies`. Inherited from `MarkdownSection1WithComment`.
    verifies:
        `## Verifies` (exactly one REQ/UC cross-reference). Mandatory.
    coverage:
        `## Coverage` (closed 3-value set). Mandatory.
    acceptance_criteria:
        `## Acceptance Criteria` (>=1 `### AC-NNN (Method): ...` entry).
        Mandatory.
    more_information:
        `## More Information`. Optional.
    updates:
        `## Updates`. Optional; last section.
    """

    verifies: Verifies = Field(description="`## Verifies` section. Mandatory.")
    coverage: Coverage = Field(description="`## Coverage` section. Mandatory.")
    acceptance_criteria: AcceptanceCriteria = Field(
        description="`## Acceptance Criteria` section (>=1 entry). Mandatory."
    )
    more_information: MoreInformation | None = Field(
        default=None, description="`## More Information` section. Optional."
    )
    updates: Updates | None = Field(default=None, description="`## Updates` section. Optional; last.")

    @model_validator(mode="after")
    def _validate_ac_numbers_unique(self) -> Vcr:
        """Reject duplicate AC numbers across `## Acceptance Criteria`.

        `AcceptanceCriterion.number`/`.method` are `@computed_field`s --
        Pydantic only evaluates a computed field's getter on access (e.g.
        during `model_dump()`/serialization), never during construction/
        validation of the underlying model itself. Accessing `.number` here
        therefore both forces every criterion's number to evaluate eagerly
        and checks the cross-field invariant: no two criteria may carry the
        same number (`### AC-001` and a hypothetical second `### AC-001`
        are the same number and therefore a duplicate). Gaps are allowed
        (criteria are never renumbered). A duplicate raises `ValueError`,
        which Pydantic channels into `ValidationError` -- mirrors DEC's
        `Decision._validate_option_numbers_unique` exactly, except
        `acceptance_criteria` is mandatory here (unlike DEC's optional
        `pros_and_cons`), so no `is not None` guard is needed.
        """
        seen: set[int] = set()
        for criterion in self.acceptance_criteria.criteria:
            number = criterion.number
            if number in seen:
                raise ValueError(f"AC number {number} is used by more than one `### AC-NNN` heading")
            seen.add(number)
        return self
