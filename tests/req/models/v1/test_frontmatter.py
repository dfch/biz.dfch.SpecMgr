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

"""Tests for the ReqFrontmatter Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.req.models.v1.frontmatter import _ALLOWED_STATUSES, _STATUS_TRANSITIONS, ReqFrontmatter

#: The locked requirement status state machine (feat-108-fsm Phase 110, the feature plan's
#: Design Notes table -- also ``gol``'s, which Phase 120 pins the same way): current status ->
#: the allowed target statuses, with ``superseded``/``deprecated`` terminal (an empty set).
_EXPECTED_TRANSITIONS = {
    "draft": frozenset({"proposed", "rejected"}),
    "proposed": frozenset({"accepted", "rejected", "draft"}),
    "accepted": frozenset({"implemented", "superseded", "deprecated", "rejected"}),
    "rejected": frozenset({"proposed", "draft"}),
    "implemented": frozenset({"superseded", "deprecated"}),
    "superseded": frozenset(),
    "deprecated": frozenset(),
}


class TestReqFrontmatter(unittest.TestCase):
    """Tests for the ReqFrontmatter Pydantic model."""

    def test_type_defaults_to_req(self):
        frontmatter = ReqFrontmatter()
        self.assertEqual(frontmatter.type, "req")

    def test_version_defaults_to_current_schema_version(self):
        frontmatter = ReqFrontmatter(status="accepted")
        self.assertEqual(frontmatter.version, "1.0.0")

    def test_version_accepts_matching_major_with_different_minor_patch(self):
        frontmatter = ReqFrontmatter(version="1.4.2")
        self.assertEqual(frontmatter.version, "1.4.2")

    def test_version_rejects_mismatched_major(self):
        with self.assertRaises(ValidationError):
            ReqFrontmatter(version="2.0.0")

    def test_accepts_all_seven_statuses(self):
        for status in (
            "draft",
            "proposed",
            "accepted",
            "superseded",
            "deprecated",
            "rejected",
            "implemented",
        ):
            with self.subTest(status=status):
                self.assertEqual(ReqFrontmatter(status=status).status, status)

    def test_rejects_unknown_status(self):
        with self.assertRaises(ValidationError):
            ReqFrontmatter(status="in-review")

    def test_status_defaults_to_draft(self):
        frontmatter = ReqFrontmatter()
        self.assertEqual(frontmatter.status, "draft")

    def test_blank_status_defaults_to_draft(self):
        self.assertEqual(ReqFrontmatter.model_validate({"status": None}).status, "draft")
        self.assertEqual(ReqFrontmatter.model_validate({"status": "   "}).status, "draft")

    def test_optional_fields_default_to_none(self):
        frontmatter = ReqFrontmatter(status="proposed")
        self.assertIsNone(frontmatter.id)
        self.assertIsNone(frontmatter.created)
        self.assertIsNone(frontmatter.updated)


class TestReqStatusTransitions(unittest.TestCase):
    """feat-108-fsm Phase 110 (REQ-001, ACC-001's pilot pin): the requirement status state
    machine owned next to ``_ALLOWED_STATUSES``, golden-pinned -- the full 7x7 transition
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

    def test_full_seven_by_seven_matrix_is_pinned(self):
        """Every (current, target) pair of the seven-value vocabulary classifies allowed iff the
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
