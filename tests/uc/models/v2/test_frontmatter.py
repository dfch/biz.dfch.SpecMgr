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

"""Tests for `UcFrontmatter` (narrows `MarkdownFrontmatter` for the `uc` type)."""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models.v2 import UcFrontmatter
from biz.dfch.specmgr.uc.models.v2.frontmatter import _ALLOWED_STATUSES, _STATUS_TRANSITIONS

#: The locked use-case status state machine (feat-108-fsm Phase 120, the feature plan's
#: Design Notes table): current status -> the allowed target statuses, with
#: ``deprecated``/``superseded`` terminal (an empty set).
_EXPECTED_TRANSITIONS = {
    "draft": frozenset({"proposed"}),
    "proposed": frozenset({"accepted", "draft"}),
    "accepted": frozenset({"superseded", "deprecated"}),
    "deprecated": frozenset(),
    "superseded": frozenset(),
}


class TestUcFrontmatter(unittest.TestCase):
    """Tests for UcFrontmatter's `type`/`status` narrowing."""

    def test_type_defaults_to_uc(self) -> None:
        """`type` defaults to "uc" when omitted."""
        frontmatter = UcFrontmatter()
        self.assertEqual(frontmatter.type, "uc")

    def test_type_rejects_other_values(self) -> None:
        """`type` is a fixed Literal["uc"] -- any other value fails validation."""
        with self.assertRaises(ValidationError):
            UcFrontmatter(type="adr")

    def test_status_defaults_to_draft(self) -> None:
        """`status` defaults to "draft" (inherited from MarkdownFrontmatter)."""
        frontmatter = UcFrontmatter()
        self.assertEqual(frontmatter.status, "draft")

    def test_status_accepts_every_allowed_value(self) -> None:
        """`status` accepts each of the five allowed values."""
        for status in ("draft", "proposed", "accepted", "deprecated", "superseded"):
            with self.subTest(status=status):
                frontmatter = UcFrontmatter(status=status)
                self.assertEqual(frontmatter.status, status)

    def test_status_rejects_unknown_value(self) -> None:
        """`status` rejects a value outside the closed five-value set."""
        with self.assertRaises(ValidationError):
            UcFrontmatter(status="rejected")

    def test_status_rejects_adr_style_superseded_by_phrase(self) -> None:
        """Unlike AdrFrontmatter, "superseded by ..." is not a use-case status shape."""
        with self.assertRaises(ValidationError):
            UcFrontmatter(status="superseded by uc-002")

    def test_blank_status_defaults_to_draft(self) -> None:
        """A blank status string is normalized to "draft" before validation."""
        frontmatter = UcFrontmatter.model_validate({"status": ""})
        self.assertEqual(frontmatter.status, "draft")

    def test_id_defaults_to_none(self) -> None:
        """`id` (inherited) defaults to None, unlike v1's mandatory uc-NNN pattern."""
        frontmatter = UcFrontmatter()
        self.assertIsNone(frontmatter.id)

    def test_id_accepts_any_non_pattern_string(self) -> None:
        """`id` no longer enforces v1's `^uc-[0-9]+$` pattern -- any string is accepted,
        matching AdrFrontmatter.id's own specmgr-assigned-identifier convention."""
        frontmatter = UcFrontmatter(id="not-uc-shaped-at-all")
        self.assertEqual(frontmatter.id, "not-uc-shaped-at-all")

    def test_created_and_updated_default_to_none(self) -> None:
        """`created`/`updated` (inherited) default to None."""
        frontmatter = UcFrontmatter()
        self.assertIsNone(frontmatter.created)
        self.assertIsNone(frontmatter.updated)

    def test_version_defaults_to_current_schema_version(self) -> None:
        """`version` (inherited) defaults to the current models.md schema version."""
        from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION

        frontmatter = UcFrontmatter()
        self.assertEqual(frontmatter.version, CURRENT_SCHEMA_VERSION)


class TestUcStatusTransitions(unittest.TestCase):
    """feat-108-fsm Phase 120 (REQ-001, ACC-001's uc pin): the use-case status state
    machine owned next to ``_ALLOWED_STATUSES``, golden-pinned -- the full 5x5 transition
    matrix over the vocabulary is classified exactly as the locked table says."""

    def test_table_equals_the_locked_design(self):
        self.assertEqual(_STATUS_TRANSITIONS, _EXPECTED_TRANSITIONS)

    def test_terminal_states_are_deprecated_and_superseded(self):
        self.assertEqual(_STATUS_TRANSITIONS["deprecated"], frozenset())
        self.assertEqual(_STATUS_TRANSITIONS["superseded"], frozenset())

    def test_keys_cover_exactly_the_closed_status_vocabulary(self):
        """Full vocabulary coverage: every status is a key exactly once, so a document's on-disk
        status is always a key and the "current not a key" case is structurally unreachable."""
        self.assertEqual(set(_STATUS_TRANSITIONS), _ALLOWED_STATUSES)

    def test_every_target_is_in_the_closed_status_vocabulary(self):
        for current, targets in _STATUS_TRANSITIONS.items():
            with self.subTest(current=current):
                self.assertTrue(targets <= _ALLOWED_STATUSES, targets)

    def test_full_five_by_five_matrix_is_pinned(self):
        """Every (current, target) pair of the five-value vocabulary classifies allowed iff the
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
