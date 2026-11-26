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

"""Tests for the RskFrontmatter Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.rsk.models.v1.frontmatter import _ALLOWED_STATUSES, _STATUS_TRANSITIONS, RskFrontmatter

#: The locked risk status state machine (feat-108-fsm Phase 120, the feature plan's
#: Design Notes table): current status -> the allowed target statuses. This domain has no
#: terminal state (every current status carries at least one allowed target).
_EXPECTED_TRANSITIONS = {
    "open": frozenset({"mitigating", "accepted", "occurred", "dropped"}),
    "mitigating": frozenset({"accepted", "occurred", "closed", "dropped", "open"}),
    "accepted": frozenset({"mitigating", "occurred", "closed", "dropped"}),
    "occurred": frozenset({"closed", "mitigating", "dropped"}),
    "closed": frozenset({"open", "occurred"}),
    "dropped": frozenset({"open"}),
}


class TestRskFrontmatter(unittest.TestCase):
    """Tests for the RskFrontmatter Pydantic model."""

    def test_type_defaults_to_rsk(self):
        sut = RskFrontmatter()

        self.assertEqual(sut.type, "rsk")

    def test_version_defaults_to_current_schema_version(self):
        sut = RskFrontmatter(status="mitigating")

        self.assertEqual(sut.version, "1.0.0")

    def test_version_accepts_matching_major_with_different_minor_patch(self):
        sut = RskFrontmatter(version="1.4.2")

        self.assertEqual(sut.version, "1.4.2")

    def test_version_rejects_mismatched_major(self):
        with self.assertRaises(ValidationError):
            RskFrontmatter(version="2.0.0")

    def test_accepts_all_six_statuses(self):
        for status in ("open", "mitigating", "accepted", "occurred", "closed", "dropped"):
            with self.subTest(status=status):
                self.assertEqual(RskFrontmatter(status=status).status, status)

    def test_rejects_unknown_status(self):
        with self.assertRaises(ValidationError):
            RskFrontmatter(status="in-review")

    def test_rejects_base_default_status_draft(self):
        with self.assertRaises(ValidationError):
            RskFrontmatter(status="draft")

    def test_status_defaults_to_open(self):
        sut = RskFrontmatter()

        self.assertEqual(sut.status, "open")

    def test_blank_status_defaults_to_open(self):
        self.assertEqual(RskFrontmatter.model_validate({"status": None}).status, "open")
        self.assertEqual(RskFrontmatter.model_validate({"status": "   "}).status, "open")

    def test_optional_fields_default_to_none(self):
        sut = RskFrontmatter(status="mitigating")

        self.assertIsNone(sut.id)
        self.assertIsNone(sut.created)
        self.assertIsNone(sut.updated)


class TestRskStatusTransitions(unittest.TestCase):
    """feat-108-fsm Phase 120 (REQ-001, ACC-001's rsk pin): the risk status state
    machine owned next to ``_ALLOWED_STATUSES``, golden-pinned -- the full 6x6 transition
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
