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

"""Tests for the DecFrontmatter Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.dec.models.v1.frontmatter import _ALLOWED_STATUSES, _STATUS_TRANSITIONS, DecFrontmatter

#: The locked decision status state machine (feat-108-fsm Phase 120, the feature plan's
#: Design Notes table): current status -> the allowed target statuses, with
#: ``superseded``/``deprecated`` terminal (an empty set).
_EXPECTED_TRANSITIONS = {
    "draft": frozenset({"proposed", "rejected"}),
    "proposed": frozenset({"accepted", "rejected", "draft"}),
    "accepted": frozenset({"superseded", "deprecated", "rejected"}),
    "rejected": frozenset({"proposed", "draft"}),
    "superseded": frozenset(),
    "deprecated": frozenset(),
}


class TestDecFrontmatter(unittest.TestCase):
    """Tests for the DecFrontmatter Pydantic model."""

    def test_type_defaults_to_dec(self) -> None:
        sut = DecFrontmatter()

        self.assertEqual(sut.type, "dec")

    def test_type_rejects_other_document_types(self) -> None:
        for other in ("req", "gol", "adr"):
            with self.subTest(other=other):
                with self.assertRaises(ValidationError):
                    DecFrontmatter(type=other)

    def test_version_defaults_to_current_schema_version(self) -> None:
        sut = DecFrontmatter(status="accepted")

        self.assertEqual(sut.version, "1.0.0")

    def test_version_accepts_matching_major_with_different_minor_patch(self) -> None:
        sut = DecFrontmatter(version="1.4.2")

        self.assertEqual(sut.version, "1.4.2")

    def test_version_rejects_mismatched_major(self) -> None:
        with self.assertRaises(ValidationError):
            DecFrontmatter(version="2.0.0")

    def test_accepts_all_six_statuses(self) -> None:
        for status in ("draft", "proposed", "accepted", "rejected", "superseded", "deprecated"):
            with self.subTest(status=status):
                self.assertEqual(DecFrontmatter(status=status).status, status)

    def test_rejects_unknown_status(self) -> None:
        with self.assertRaises(ValidationError):
            DecFrontmatter(status="in-review")

    def test_rejects_gol_only_implemented_status(self) -> None:
        # "implemented" belongs to GOL's seven-value set, not DEC's six.
        with self.assertRaises(ValidationError):
            DecFrontmatter(status="implemented")

    def test_status_defaults_to_draft(self) -> None:
        sut = DecFrontmatter()

        self.assertEqual(sut.status, "draft")

    def test_blank_status_defaults_to_draft(self) -> None:
        self.assertEqual(DecFrontmatter.model_validate({"status": None}).status, "draft")
        self.assertEqual(DecFrontmatter.model_validate({"status": "   "}).status, "draft")

    def test_optional_fields_default_to_none(self) -> None:
        sut = DecFrontmatter(status="proposed")

        self.assertIsNone(sut.id)
        self.assertIsNone(sut.created)
        self.assertIsNone(sut.updated)


class TestDecStatusTransitions(unittest.TestCase):
    """feat-108-fsm Phase 120 (REQ-001, ACC-001's dec pin): the decision status state
    machine owned next to ``_ALLOWED_STATUSES``, golden-pinned -- the full 6x6 transition
    matrix over the vocabulary is classified exactly as the locked table says."""

    def test_table_equals_the_locked_design(self):
        self.assertEqual(_STATUS_TRANSITIONS, _EXPECTED_TRANSITIONS)

    def test_terminal_states_are_superseded_and_deprecated(self):
        self.assertEqual(_STATUS_TRANSITIONS["superseded"], frozenset())
        self.assertEqual(_STATUS_TRANSITIONS["deprecated"], frozenset())

    def test_keys_cover_exactly_the_closed_status_vocabulary(self):
        """Full vocabulary coverage: every status is a key exactly once, so a document's on-disk
        status is always a key and the "current not a key" case is structurally unreachable."""
        self.assertEqual(set(_STATUS_TRANSITIONS), _ALLOWED_STATUSES)

    def test_every_target_is_in_the_closed_status_vocabulary(self):
        for current, targets in _STATUS_TRANSITIONS.items():
            with self.subTest(current=current):
                self.assertTrue(targets <= _ALLOWED_STATUSES, targets)

    def test_full_six_by_six_matrix_is_pinned(self):
        """Every (current, target) pair of the six-value vocabulary classifies allowed iff the
        locked table says so (the matrix the generic ``set_status`` tool enforces end-to-end)."""
        for current in _ALLOWED_STATUSES:
            for target in _ALLOWED_STATUSES:
                with self.subTest(current=current, target=target):
                    self.assertEqual(
                        target in _STATUS_TRANSITIONS[current],
                        target in _EXPECTED_TRANSITIONS[current],
                    )


if __name__ == "__main__":
    unittest.main()
