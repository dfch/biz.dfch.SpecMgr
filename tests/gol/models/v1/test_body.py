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

"""Tests for the `Goal` body model (ACC-002).

Covers the reference document from
`.specmgr/feat/feat-18-goal/gol_reference.md` (all optional sections
present, `Related Artifacts` with all four sub-lists), plus explicit
coverage of each mandatory-vs-optional field combination: each optional
section (`Description`/`Priority`/`Tags`/`Related Artifacts`/
`More Information`/`Notes`) individually absent/present, and each of the
four `Related Artifacts` sub-lists individually absent/present.

Also covers feat-135-related-artifacts-risks: `AcceptanceCriteria` was
removed and replaced by `Risks` (REQ-001/REQ-002), and every sub-list now
enforces the shared `"<TAG> <uuid>: <title>"` cross-reference format
(REQ-004) with an optional trailing notes paragraph (REQ-006).
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.gol.models.v1.body import (
    Decisions,
    Description,
    Goal,
    Goals,
    MoreInformation,
    Notes,
    Priority,
    RelatedArtifacts,
    Requirements,
    Risks,
    Source,
    Tags,
)
from biz.dfch.specmgr.models.md import MarkdownParagraph
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md.alias_match import match_alias

# A well-formed, lowercase 8-4-4-4-12 hex UUID reused by every generic
# (non-reference-document) cross-reference fixture below -- the exact value
# is never significant, only its shape.
_VALID_UUID = "12345678-1234-1234-1234-123456789abc"

# Every `RelatedArtifacts` sub-list class alongside the exact canonical
# heading text it must -- and only it must -- match. The headings derive
# from the class names via the `AliasType.SPACE_SEPARATED` convention (no
# explicit `@alias`).
_SUB_LIST_CLASSES_AND_HEADINGS = [
    (Requirements, "Requirements"),
    (Decisions, "Decisions"),
    (Goals, "Goals"),
    (Risks, "Risks"),
]

# The reference document's body (`gol_reference.md`, frontmatter stripped),
# exercising every field: `statement` + all optional sections present,
# `Related Artifacts` with all four sub-lists.
_REFERENCE_TEXT = format_text(
    """\
# Competitive Engines in Consumer Vehicles

THE company shall provide engines that are competitive in power output and
fuel consumption in the consumer vehicle segment, so that the vehicle line
attracts buyers and supports the company's market share target.

## Description

Before purchase, buyers of consumer vehicles compare engine power output
and fuel consumption across competing manufacturers. An engine that is not
competitive on these two dimensions reduces the appeal of the entire
vehicle line, independent of every other feature it offers. This goal
captures the business-level outcome that engine-related requirements
ultimately serve: it states what the organization wants to achieve, not
how any individual requirement must behave.

## Priority

<!-- A number between 0 and 99. Lower number is higher priority. -->

10

## Tags

- Business Goals

- Combustion Engines

- Vehicles

## Source

The vehicle program's 2027 market analysis and the sales organization's consumer vehicle segment study

## Related Artifacts

### Requirements

- REQ f04dc881-ec40-4072-9a75-35002fca2bd7: Maximum temperatures of running engines in civil vehicles

### Decisions

- DEC 8502621c-177a-4e76-9bf2-d79b4e960b2c: Usage of metal conductors in moving engine parts

### Goals

- GOL 68a4a8dc-8a9f-4150-b7ca-dc5591ee6ede: Affordable and Efficient Powertrains for the Consumer Segment

- GOL 115fa636-2b33-4baa-be66-52bcbb8eaa7c: Competitive Engines in Consumer Vehicles

### Risks

- RSK 7d310eed-1eeb-4820-bc79-03bc5ac4612c: Sensor Drift Under Sustained High-Temperature Operation

## More Information

Progress against this goal is tracked at program level, not by any single
requirement's status. The requirements listed under `Related Artifacts`
are examples of the work that contributes to this goal, not an exhaustive
list; further contributing requirements are identified during requirement
engineering and linked there as they are created.

## Notes

This goal was accepted during the 2027 vehicle program kickoff. If the
consumer vehicle segment study is repeated and no longer supports the
assumptions above, this goal is superseded by the revised goal that
replaces it.
"""
)


def _statement() -> MarkdownParagraph:
    return MarkdownParagraph.from_text(format_text("Some goal statement.\n"))


def _source() -> Source:
    return Source.from_text(format_text("## Source\n\nSome source.\n"))


def _minimal_goal_kwargs() -> dict:
    return {
        "statement": _statement(),
        "source": _source(),
    }


class TestGoalHeadingAlias(unittest.TestCase):
    """`Goal`'s H1 alias is the free-form `.+` REGEX: any non-empty title matches."""

    def test_goal_matches_any_nonempty_h1_text(self) -> None:
        for heading in ("Competitive Engines in Consumer Vehicles", "A Goal", "x"):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(Goal, heading))

    def test_goal_rejects_empty_h1_text(self) -> None:
        self.assertFalse(match_alias(Goal, ""))

    def test_metadata_is_heading_open_h1(self) -> None:
        self.assertEqual(Goal._metadata.get("type"), "heading_open")
        self.assertEqual(Goal._metadata.get("tag"), "h1")


class TestSubListHeadingAliases(unittest.TestCase):
    """Each `RelatedArtifacts` sub-list class resolves its own, correct, distinct heading alias.

    Regression-style coverage mirroring PRB's `Question{N}`-shaped alias
    test: since the four sub-list headings are all short, single-word
    title-case names, this confirms each class's `SPACE_SEPARATED`-derived
    alias matches its own exact wording and no other sub-list's.
    """

    def test_each_sub_list_matches_its_own_canonical_heading_and_no_other(self) -> None:
        for cls, heading in _SUB_LIST_CLASSES_AND_HEADINGS:
            with self.subTest(cls=cls.__name__):
                self.assertTrue(match_alias(cls, heading))
                for other_cls, other_heading in _SUB_LIST_CLASSES_AND_HEADINGS:
                    if other_heading == heading:
                        continue
                    self.assertFalse(
                        match_alias(cls, other_heading),
                        f"{cls.__name__} incorrectly matched {other_heading!r}",
                    )

    def test_metadata_is_heading_open_h3_for_every_sub_list(self) -> None:
        for cls, _heading in _SUB_LIST_CLASSES_AND_HEADINGS:
            with self.subTest(cls=cls.__name__):
                self.assertEqual(cls._metadata.get("type"), "heading_open")
                self.assertEqual(cls._metadata.get("tag"), "h3")


class TestStatementAndSourceMandatory(unittest.TestCase):
    """`Goal.statement`/`Goal.source` are mandatory -- absent raises.

    Two distinct channels, mirroring the engine's own split: direct
    construction without a mandatory field raises
    `pydantic.ValidationError` (the field is simply missing from the
    constructor call), while `Goal.from_text` on a markdown document that
    lacks the lead paragraph or the `## Source` section raises
    `AssertionError` (the engine found no match for a mandatory field).
    """

    def test_missing_statement_raises_validation_error(self) -> None:
        kwargs = _minimal_goal_kwargs()
        del kwargs["statement"]

        with self.assertRaises(ValidationError):
            Goal(**kwargs)

    def test_missing_source_raises_validation_error(self) -> None:
        kwargs = _minimal_goal_kwargs()
        del kwargs["source"]

        with self.assertRaises(ValidationError):
            Goal(**kwargs)

    def test_from_text_missing_statement_raises_assertion_error(self) -> None:
        text = format_text("# A Goal\n\n## Source\n\nSome source.\n")

        with self.assertRaises(AssertionError):
            Goal.from_text(text)

    def test_from_text_missing_source_raises_assertion_error(self) -> None:
        text = format_text("# A Goal\n\nSome statement.\n")

        with self.assertRaises(AssertionError):
            Goal.from_text(text)


class TestOptionalSectionsIndividuallyOptional(unittest.TestCase):
    """Each optional section is independently optional (ACC-002).

    Covers all six sections absent at once (a freshly created `gol`
    document carries only `statement` + `Source`) and each section
    present one at a time.
    """

    def test_all_six_optional_sections_default_to_none_when_absent(self) -> None:
        sut = Goal(**_minimal_goal_kwargs())

        self.assertIsNone(sut.description)
        self.assertIsNone(sut.priority)
        self.assertIsNone(sut.tags)
        self.assertIsNone(sut.related_artifacts)
        self.assertIsNone(sut.more_information)
        self.assertIsNone(sut.notes)

    def test_description_present(self) -> None:
        kwargs = _minimal_goal_kwargs()
        kwargs["description"] = Description.from_text(format_text("## Description\n\nSome description text.\n"))

        sut = Goal(**kwargs)

        self.assertIsNotNone(sut.description)
        self.assertIn("Some description text.", sut.description.text)
        self.assertIsNone(sut.priority)
        self.assertIsNone(sut.tags)
        self.assertIsNone(sut.related_artifacts)
        self.assertIsNone(sut.more_information)
        self.assertIsNone(sut.notes)

    def test_priority_present(self) -> None:
        kwargs = _minimal_goal_kwargs()
        kwargs["priority"] = Priority.from_text(format_text("## Priority\n\n50\n"))

        sut = Goal(**kwargs)

        self.assertIsNotNone(sut.priority)
        self.assertEqual(sut.priority.value.text, "50")
        self.assertIsNone(sut.description)
        self.assertIsNone(sut.tags)
        self.assertIsNone(sut.related_artifacts)
        self.assertIsNone(sut.more_information)
        self.assertIsNone(sut.notes)

    def test_tags_present(self) -> None:
        kwargs = _minimal_goal_kwargs()
        kwargs["tags"] = Tags.from_text(format_text("## Tags\n\n- Some Tag\n"))

        sut = Goal(**kwargs)

        self.assertIsNotNone(sut.tags)
        self.assertEqual([item.text for item in sut.tags.items], ["Some Tag"])
        self.assertIsNone(sut.description)
        self.assertIsNone(sut.priority)
        self.assertIsNone(sut.related_artifacts)
        self.assertIsNone(sut.more_information)
        self.assertIsNone(sut.notes)

    def test_related_artifacts_present(self) -> None:
        kwargs = _minimal_goal_kwargs()
        kwargs["related_artifacts"] = RelatedArtifacts.from_text(
            format_text(
                "## Related Artifacts\n\n### Decisions\n\n- DEC 12345678-1234-1234-1234-123456789abc: Some decision.\n"
            )
        )

        sut = Goal(**kwargs)

        self.assertIsNotNone(sut.related_artifacts)
        self.assertIsNone(sut.description)
        self.assertIsNone(sut.priority)
        self.assertIsNone(sut.tags)
        self.assertIsNone(sut.more_information)
        self.assertIsNone(sut.notes)

    def test_more_information_present(self) -> None:
        kwargs = _minimal_goal_kwargs()
        kwargs["more_information"] = MoreInformation.from_text(
            format_text("## More Information\n\nSome more information text.\n")
        )

        sut = Goal(**kwargs)

        self.assertIsNotNone(sut.more_information)
        self.assertIn("Some more information text.", sut.more_information.text)
        self.assertIsNone(sut.description)
        self.assertIsNone(sut.priority)
        self.assertIsNone(sut.tags)
        self.assertIsNone(sut.related_artifacts)
        self.assertIsNone(sut.notes)

    def test_notes_present(self) -> None:
        kwargs = _minimal_goal_kwargs()
        kwargs["notes"] = Notes.from_text(format_text("## Notes\n\nSome notes text.\n"))

        sut = Goal(**kwargs)

        self.assertIsNotNone(sut.notes)
        self.assertIn("Some notes text.", sut.notes.text)
        self.assertIsNone(sut.description)
        self.assertIsNone(sut.priority)
        self.assertIsNone(sut.tags)
        self.assertIsNone(sut.related_artifacts)
        self.assertIsNone(sut.more_information)


class TestRelatedArtifactsSubListsIndividuallyOptional(unittest.TestCase):
    """Each of the four `RelatedArtifacts` sub-lists is independently optional (ACC-002)."""

    def test_all_four_sub_lists_default_to_none_when_absent(self) -> None:
        sut = RelatedArtifacts()

        self.assertIsNone(sut.requirements)
        self.assertIsNone(sut.decisions)
        self.assertIsNone(sut.goals)
        self.assertIsNone(sut.risks)

    def test_requirements_sub_list_present(self) -> None:
        sut = RelatedArtifacts.from_text(
            format_text(f"## Related Artifacts\n\n### Requirements\n\n- REQ {_VALID_UUID}: Some requirement.\n")
        )

        self.assertIsNotNone(sut.requirements)
        self.assertEqual([item.text for item in sut.requirements.items], [f"REQ {_VALID_UUID}: Some requirement."])
        self.assertIsNone(sut.decisions)
        self.assertIsNone(sut.goals)
        self.assertIsNone(sut.risks)

    def test_decisions_sub_list_present(self) -> None:
        sut = RelatedArtifacts.from_text(
            format_text(f"## Related Artifacts\n\n### Decisions\n\n- DEC {_VALID_UUID}: Some decision.\n")
        )

        self.assertIsNotNone(sut.decisions)
        self.assertEqual([item.text for item in sut.decisions.items], [f"DEC {_VALID_UUID}: Some decision."])
        self.assertIsNone(sut.requirements)
        self.assertIsNone(sut.goals)
        self.assertIsNone(sut.risks)

    def test_goals_sub_list_present(self) -> None:
        sut = RelatedArtifacts.from_text(
            format_text(f"## Related Artifacts\n\n### Goals\n\n- GOL {_VALID_UUID}: Some goal.\n")
        )

        self.assertIsNotNone(sut.goals)
        self.assertEqual([item.text for item in sut.goals.items], [f"GOL {_VALID_UUID}: Some goal."])
        self.assertIsNone(sut.requirements)
        self.assertIsNone(sut.decisions)
        self.assertIsNone(sut.risks)

    def test_risks_sub_list_present(self) -> None:
        sut = RelatedArtifacts.from_text(
            format_text(f"## Related Artifacts\n\n### Risks\n\n- RSK {_VALID_UUID}: Some risk.\n")
        )

        self.assertIsNotNone(sut.risks)
        self.assertEqual([item.text for item in sut.risks.items], [f"RSK {_VALID_UUID}: Some risk."])
        self.assertIsNone(sut.requirements)
        self.assertIsNone(sut.decisions)
        self.assertIsNone(sut.goals)

    def test_empty_sub_list_items_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Requirements(items=[])
        with self.assertRaises(ValidationError):
            Decisions(items=[])
        with self.assertRaises(ValidationError):
            Goals(items=[])
        with self.assertRaises(ValidationError):
            Risks(items=[])


class TestPriorityValueValidation(unittest.TestCase):
    """`Priority.value` is a 0-99 number, no leading zeros other than "0" itself (ACC-002/ACC-003)."""

    def test_priority_accepts_zero(self) -> None:
        sut = Priority.from_text(format_text("## Priority\n\n0\n"))

        self.assertEqual(sut.value.text, "0")

    def test_priority_accepts_upper_bound(self) -> None:
        sut = Priority.from_text(format_text("## Priority\n\n99\n"))

        self.assertEqual(sut.value.text, "99")

    def test_priority_rejects_out_of_range_and_malformed_values(self) -> None:
        for value in ("100", "-1", "007", "5a", "1.5"):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    Priority.from_text(format_text(f"## Priority\n\n{value}\n"))

    def test_priority_comment_is_captured_when_present(self) -> None:
        text = format_text(
            "## Priority\n\n<!-- A number between 0 and 99. Lower number is higher priority. -->\n\n50\n"
        )
        sut = Priority.from_text(text)

        self.assertIsNotNone(sut.comment)
        self.assertIn("A number between 0 and 99.", sut.comment.text)
        self.assertEqual(sut.value.text, "50")

    def test_priority_round_trips_with_comment(self) -> None:
        text = format_text(
            "## Priority\n\n<!-- A number between 0 and 99. Lower number is higher priority. -->\n\n50\n"
        )
        sut = Priority.from_text(text)

        self.assertEqual(str(sut), text)


class TestGoalReferenceDocumentRoundTrips(unittest.TestCase):
    """The full reference document (`gol_reference.md`'s body) parses and round-trips (ACC-001/ACC-002)."""

    def test_round_trips(self) -> None:
        sut = Goal.from_text(_REFERENCE_TEXT)

        self.assertEqual(str(sut), _REFERENCE_TEXT)

    def test_title_and_statement(self) -> None:
        sut = Goal.from_text(_REFERENCE_TEXT)

        self.assertEqual(sut.text, "Competitive Engines in Consumer Vehicles")
        self.assertIn("THE company shall provide engines", sut.statement.text)
        self.assertIn("competitive in power output and", sut.statement.text)

    def test_all_optional_sections_present(self) -> None:
        sut = Goal.from_text(_REFERENCE_TEXT)

        self.assertIsNotNone(sut.description)
        self.assertIn("buyers of consumer vehicles compare", sut.description.text)
        self.assertIsNotNone(sut.priority)
        self.assertIsNotNone(sut.priority.comment)
        self.assertEqual(sut.priority.value.text, "10")
        self.assertIsNotNone(sut.tags)
        self.assertEqual([item.text for item in sut.tags.items], ["Business Goals", "Combustion Engines", "Vehicles"])
        self.assertIsNotNone(sut.source)
        self.assertEqual(
            sut.source.value.text,
            "The vehicle program's 2027 market analysis and the sales organization's consumer vehicle segment study",
        )
        self.assertIsNotNone(sut.related_artifacts)
        self.assertIsNotNone(sut.more_information)
        self.assertIn("tracked at program level", sut.more_information.text)
        self.assertIsNotNone(sut.notes)
        self.assertIn("accepted during the 2027 vehicle program kickoff", sut.notes.text)

    def test_related_artifacts_sub_lists_present(self) -> None:
        sut = Goal.from_text(_REFERENCE_TEXT)

        related_artifacts = sut.related_artifacts
        self.assertIsNotNone(related_artifacts)
        self.assertEqual(
            [item.text for item in related_artifacts.requirements.items],
            ["REQ f04dc881-ec40-4072-9a75-35002fca2bd7: Maximum temperatures of running engines in civil vehicles"],
        )
        self.assertEqual(
            [item.text for item in related_artifacts.decisions.items],
            ["DEC 8502621c-177a-4e76-9bf2-d79b4e960b2c: Usage of metal conductors in moving engine parts"],
        )
        self.assertEqual(
            [item.text for item in related_artifacts.goals.items],
            [
                "GOL 68a4a8dc-8a9f-4150-b7ca-dc5591ee6ede: Affordable and Efficient Powertrains for the Consumer Segment",
                "GOL 115fa636-2b33-4baa-be66-52bcbb8eaa7c: Competitive Engines in Consumer Vehicles",
            ],
        )
        self.assertEqual(
            [item.text for item in related_artifacts.risks.items],
            ["RSK 7d310eed-1eeb-4820-bc79-03bc5ac4612c: Sensor Drift Under Sustained High-Temperature Operation"],
        )


# Every sub-list class alongside its own correct type tag (feat-135-related-artifacts-risks).
_SUB_LIST_CLASSES_AND_TAGS = [
    (Requirements, "REQ"),
    (Decisions, "DEC"),
    (Goals, "GOL"),
    (Risks, "RSK"),
]


class TestSubListCrossReferenceFormatMatrix(unittest.TestCase):
    """Every `RelatedArtifacts` sub-list enforces the shared `"<TAG> <uuid>: <title>"`
    cross-reference format (feat-135-related-artifacts-risks, REQ-004, ACC-002/ACC-003):
    a well-formed bullet parses, and each malformed variant (wrong tag, uppercase uuid,
    malformed uuid, dash instead of space, missing title) raises `pydantic.ValidationError`.
    """

    def test_well_formed_bullet_parses(self) -> None:
        for cls, tag in _SUB_LIST_CLASSES_AND_TAGS:
            with self.subTest(cls=cls.__name__):
                text = format_text(f"### {cls.__name__}\n\n- {tag} {_VALID_UUID}: A title\n")

                sut = cls.from_text(text)

                self.assertEqual(len(sut.items), 1)

    def test_wrong_type_tag_raises_validation_error(self) -> None:
        for cls, tag in _SUB_LIST_CLASSES_AND_TAGS:
            wrong_tag = next(other_tag for _, other_tag in _SUB_LIST_CLASSES_AND_TAGS if other_tag != tag)
            with self.subTest(cls=cls.__name__):
                text = format_text(f"### {cls.__name__}\n\n- {wrong_tag} {_VALID_UUID}: A title\n")

                with self.assertRaises(ValidationError):
                    cls.from_text(text)

    def test_uppercase_uuid_raises_validation_error(self) -> None:
        for cls, tag in _SUB_LIST_CLASSES_AND_TAGS:
            with self.subTest(cls=cls.__name__):
                text = format_text(f"### {cls.__name__}\n\n- {tag} {_VALID_UUID.upper()}: A title\n")

                with self.assertRaises(ValidationError):
                    cls.from_text(text)

    def test_malformed_uuid_raises_validation_error(self) -> None:
        # One hex digit short in the last group.
        malformed_uuid = "12345678-1234-1234-1234-123456789a"
        for cls, tag in _SUB_LIST_CLASSES_AND_TAGS:
            with self.subTest(cls=cls.__name__):
                text = format_text(f"### {cls.__name__}\n\n- {tag} {malformed_uuid}: A title\n")

                with self.assertRaises(ValidationError):
                    cls.from_text(text)

    def test_dash_instead_of_space_raises_validation_error(self) -> None:
        for cls, tag in _SUB_LIST_CLASSES_AND_TAGS:
            with self.subTest(cls=cls.__name__):
                text = format_text(f"### {cls.__name__}\n\n- {tag}-{_VALID_UUID}: A title\n")

                with self.assertRaises(ValidationError):
                    cls.from_text(text)

    def test_missing_title_raises_validation_error(self) -> None:
        for cls, tag in _SUB_LIST_CLASSES_AND_TAGS:
            with self.subTest(cls=cls.__name__):
                text = format_text(f"### {cls.__name__}\n\n- {tag} {_VALID_UUID}:\n")

                with self.assertRaises(ValidationError):
                    cls.from_text(text)

    def test_decisions_rejects_adr_tag(self) -> None:
        """`Decisions` is DEC-only (REQ-005/ACC-004): an `ADR` bullet is rejected."""
        text = format_text(f"### Decisions\n\n- ADR {_VALID_UUID}: A title\n")

        with self.assertRaises(ValidationError):
            Decisions.from_text(text)


class TestSubListNotesCapture(unittest.TestCase):
    """A bullet with a trailing indented notes paragraph parses into `.items[0].notes`;
    a bare bullet leaves `.items[0].notes` as `None` (feat-135-related-artifacts-risks,
    REQ-006, ACC-005) -- every sub-list's `items` is now `list[MarkdownListItemWithNotes]`.
    """

    def test_bullet_with_notes_captures_notes(self) -> None:
        for cls, tag in _SUB_LIST_CLASSES_AND_TAGS:
            with self.subTest(cls=cls.__name__):
                text = format_text(f"### {cls.__name__}\n\n- {tag} {_VALID_UUID}: A title\n\n  A paraphrase note.\n")

                sut = cls.from_text(text)

                self.assertIsNotNone(sut.items[0].notes)

    def test_bare_bullet_leaves_notes_none(self) -> None:
        for cls, tag in _SUB_LIST_CLASSES_AND_TAGS:
            with self.subTest(cls=cls.__name__):
                text = format_text(f"### {cls.__name__}\n\n- {tag} {_VALID_UUID}: A title\n")

                sut = cls.from_text(text)

                self.assertIsNone(sut.items[0].notes)


if __name__ == "__main__":
    unittest.main()
