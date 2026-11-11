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

"""Tests for the QaFrontmatter Pydantic model.

Ported from the now-removed `tests/qa/models/v1/test_frontmatter.py`
(feat-14 Phase 8: `QaFrontmatter` moved from `qa/models/v1/` into
`qa/models/v2/` directly, so this unit-level coverage moved with it) --
`tests/qa/models/v2/test_parser.py` only exercises `QaFrontmatter` indirectly
through full-document parsing, so this file's standalone field-level
coverage (status set, version major-component gate, defaults) has no other
home in the v2 suite.
"""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.qa.models.v2.frontmatter import _ALLOWED_STATUSES, _STATUS_TRANSITIONS, QaFrontmatter

#: The locked QA-document status state machine (feat-108-fsm Phase 120, the feature plan's
#: Design Notes table -- identical to tsk's, whose vocabulary qa reuses): current status ->
#: the allowed target statuses. This domain has no terminal state (every current status
#: carries at least one allowed target).
_EXPECTED_TRANSITIONS = {
    "draft": frozenset({"active", "cancelled"}),
    "active": frozenset({"done", "cancelled", "draft"}),
    "done": frozenset({"active", "cancelled"}),
    "cancelled": frozenset({"draft", "active"}),
}


class TestQaFrontmatter(unittest.TestCase):
    """Tests for the QaFrontmatter Pydantic model."""

    def test_type_defaults_to_qa(self):
        sut = QaFrontmatter()

        self.assertEqual(sut.type, "qa")

    def test_version_defaults_to_current_schema_version(self):
        sut = QaFrontmatter(status="active")

        self.assertEqual(sut.version, "1.0.0")

    def test_version_accepts_matching_major_with_different_minor_patch(self):
        sut = QaFrontmatter(version="1.4.2")

        self.assertEqual(sut.version, "1.4.2")

    def test_version_rejects_mismatched_major(self):
        with self.assertRaises(ValidationError):
            QaFrontmatter(version="2.0.0")

    def test_accepts_all_four_statuses(self):
        for status in ("draft", "active", "done", "cancelled"):
            with self.subTest(status=status):
                self.assertEqual(QaFrontmatter(status=status).status, status)

    def test_rejects_unknown_status(self):
        with self.assertRaises(ValidationError):
            QaFrontmatter(status="in-review")

    def test_status_defaults_to_draft(self):
        sut = QaFrontmatter()

        self.assertEqual(sut.status, "draft")

    def test_blank_status_defaults_to_draft(self):
        self.assertEqual(QaFrontmatter.model_validate({"status": None}).status, "draft")
        self.assertEqual(QaFrontmatter.model_validate({"status": "   "}).status, "draft")

    def test_optional_fields_default_to_none(self):
        sut = QaFrontmatter(status="active")

        self.assertIsNone(sut.id)
        self.assertIsNone(sut.created)
        self.assertIsNone(sut.updated)


class TestQaStatusTransitions(unittest.TestCase):
    """feat-108-fsm Phase 120 (REQ-001, ACC-001's qa pin): the QA-document status state
    machine owned next to ``_ALLOWED_STATUSES``, golden-pinned -- the full 4x4 transition
    matrix over the vocabulary is classified exactly as the locked table says."""

    def test_table_equals_the_locked_design(self):
        self.assertEqual(_STATUS_TRANSITIONS, _EXPECTED_TRANSITIONS)

    def test_no_state_is_terminal(self):
        """This domain has no terminal state: every current status carries at least one allowed
        target (the locked table's explicit property, distinct from the terminal-bearing
        req/uc/dec/gol machines)."""
        for current, targets in _STATUS_TRANSITIONS.items():
            with self.subTest(current=current):
                self.assertTrue(targets)

    def test_keys_cover_exactly_the_closed_status_vocabulary(self):
        """Full vocabulary coverage: every status is a key exactly once, so a document's on-disk
        status is always a key and the "current not a key" case is structurally unreachable."""
        self.assertEqual(set(_STATUS_TRANSITIONS), _ALLOWED_STATUSES)

    def test_every_target_is_in_the_closed_status_vocabulary(self):
        for current, targets in _STATUS_TRANSITIONS.items():
            with self.subTest(current=current):
                self.assertTrue(targets <= _ALLOWED_STATUSES, targets)

    def test_full_four_by_four_matrix_is_pinned(self):
        """Every (current, target) pair of the four-value vocabulary classifies allowed iff the
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
