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

"""Tests for the TxtFrontmatter Pydantic model (ACC-003, REQ-005)."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.txt.models.v1.frontmatter import _ALLOWED_STATUSES, _STATUS_TRANSITIONS, TxtFrontmatter

#: The locked free-form-text status state machine (feat-108-fsm Phase 120, the feature
#: plan's Design Notes table): current status -> the allowed target statuses. This domain
#: has no terminal state (every current status carries at least one allowed target).
_EXPECTED_TRANSITIONS = {
    "draft": frozenset({"progress"}),
    "progress": frozenset({"done", "draft"}),
    "done": frozenset({"progress"}),
}


class TestTxtFrontmatter(unittest.TestCase):
    """Tests for the TxtFrontmatter Pydantic model."""

    def test_type_defaults_to_txt(self) -> None:
        sut = TxtFrontmatter()

        self.assertEqual(sut.type, "txt")

    def test_type_rejects_other_document_types(self) -> None:
        for other in ("req", "gol", "dec", "vcr", "sop"):
            with self.subTest(other=other):
                with self.assertRaises(ValidationError):
                    TxtFrontmatter(type=other)

    def test_version_defaults_to_current_schema_version(self) -> None:
        sut = TxtFrontmatter(status="progress")

        self.assertEqual(sut.version, "1.0.0")

    def test_version_accepts_matching_major_with_different_minor_patch(self) -> None:
        sut = TxtFrontmatter(version="1.4.2")

        self.assertEqual(sut.version, "1.4.2")

    def test_version_rejects_mismatched_major(self) -> None:
        with self.assertRaises(ValidationError):
            TxtFrontmatter(version="2.0.0")

    def test_accepts_exactly_the_three_statuses(self) -> None:
        for status in ("draft", "progress", "done"):
            with self.subTest(status=status):
                self.assertEqual(TxtFrontmatter(status=status).status, status)

    def test_rejects_unknown_status(self) -> None:
        with self.assertRaises(ValidationError):
            TxtFrontmatter(status="in-review")

    def test_rejects_vcr_only_statuses(self) -> None:
        # "complete"/"approved" belong to VCR's four-value verification
        # lifecycle, not TXT's three-value set (REQ-005).
        for status in ("complete", "approved"):
            with self.subTest(status=status):
                with self.assertRaises(ValidationError):
                    TxtFrontmatter(status=status)

    def test_rejects_dec_only_statuses(self) -> None:
        # "accepted"/"proposed"/etc. belong to DEC's six-value set, not TXT's three.
        for status in ("accepted", "proposed", "rejected", "superseded", "deprecated"):
            with self.subTest(status=status):
                with self.assertRaises(ValidationError):
                    TxtFrontmatter(status=status)

    def test_rejects_feat_only_statuses(self) -> None:
        # "planning"/"review" belong to the feature-README status set, not TXT's three.
        for status in ("planning", "review"):
            with self.subTest(status=status):
                with self.assertRaises(ValidationError):
                    TxtFrontmatter(status=status)

    def test_status_defaults_to_draft(self) -> None:
        sut = TxtFrontmatter()

        self.assertEqual(sut.status, "draft")

    def test_blank_status_defaults_to_draft(self) -> None:
        self.assertEqual(TxtFrontmatter.model_validate({"status": None}).status, "draft")
        self.assertEqual(TxtFrontmatter.model_validate({"status": "   "}).status, "draft")

    def test_optional_fields_default_to_none(self) -> None:
        sut = TxtFrontmatter(status="progress")

        self.assertIsNone(sut.id)
        self.assertIsNone(sut.created)
        self.assertIsNone(sut.updated)
        self.assertIsNone(sut.classification)

    def test_classification_is_optional_free_text(self) -> None:
        sut = TxtFrontmatter(classification="internal")

        self.assertEqual(sut.classification, "internal")


class TestTxtStatusTransitions(unittest.TestCase):
    """feat-108-fsm Phase 120 (REQ-001, ACC-001's txt pin): the free-form-text status
    state machine owned next to ``_ALLOWED_STATUSES``, golden-pinned -- the full 3x3
    transition matrix over the vocabulary is classified exactly as the locked table says."""

    def test_table_equals_the_locked_design(self) -> None:
        self.assertEqual(_STATUS_TRANSITIONS, _EXPECTED_TRANSITIONS)

    def test_no_state_is_terminal(self) -> None:
        """This domain has no terminal state: every current status carries at least one allowed
        target (the locked table's explicit property, distinct from the terminal-bearing
        req/uc/dec/gol machines)."""
        for current, targets in _STATUS_TRANSITIONS.items():
            with self.subTest(current=current):
                self.assertTrue(targets)

    def test_keys_cover_exactly_the_closed_status_vocabulary(self) -> None:
        """Full vocabulary coverage: every status is a key exactly once, so a document's on-disk
        status is always a key and the "current not a key" case is structurally unreachable."""
        self.assertEqual(set(_STATUS_TRANSITIONS), _ALLOWED_STATUSES)

    def test_every_target_is_in_the_closed_status_vocabulary(self) -> None:
        for current, targets in _STATUS_TRANSITIONS.items():
            with self.subTest(current=current):
                self.assertTrue(targets <= _ALLOWED_STATUSES, targets)

    def test_full_three_by_three_matrix_is_pinned(self) -> None:
        """Every (current, target) pair of the three-value vocabulary classifies allowed iff the
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
