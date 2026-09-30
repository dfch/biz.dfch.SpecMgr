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

"""Tests for the `RelatedArtifacts` sub-list classes of the `Requirement` body model.

`req` has no other `test_body.py` -- its remaining body-level shape is covered
through `test_parser.py`'s `parse_req`-level tests instead. This file is scoped
to feat-135-related-artifacts-risks: `AcceptanceCriteria` was removed and
replaced by `Risks` (REQ-001/REQ-002), and every `RelatedArtifacts` sub-list
now enforces the shared `"<TAG> <uuid>: <title>"` cross-reference format
(REQ-004), `Decisions` is DEC-only (REQ-005), and an optional trailing notes
paragraph is supported (REQ-006). Mirrors the equivalent test classes added to
`gol`/`dec`/`sop`'s own `test_body.py` files.
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.req.models.v1.body import Decisions, Goals, Requirements, Risks

# A well-formed, lowercase 8-4-4-4-12 hex UUID reused by every fixture below --
# the exact value is never significant, only its shape.
_VALID_UUID = "12345678-1234-1234-1234-123456789abc"

# Every `RelatedArtifacts` sub-list class alongside its own correct type tag.
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
