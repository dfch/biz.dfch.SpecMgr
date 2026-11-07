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

"""Tests for `general.models.invalid_status_transition_result.InvalidStatusTransitionResult` (feat-108-fsm
Phase 100, REQ-004, GitHub issue #108 -- case 6 of the ADR 519d1206-4d2a-4500-9046-6db635209996
non-raising, structured-result workaround chain)."""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.general.models import InvalidStatusTransitionResult

#: The exact field names `InvalidStatusTransitionResult` declares (the locked Phase 100 shape).
_EXPECTED_FIELD_NAMES = ["valid", "type", "from_status", "to_status", "allowed_values", "message"]

#: The locked normal-form message wording (sorted `allowed_values`, comma-and-space-joined in the
#: same order as the field -- the ADR 519d1206 self-consistency rationale).
_NORMAL_MESSAGE = (
    "Invalid status transition 'accepted' -> 'draft' for type 'req'. "
    "Allowed from 'accepted': deprecated, implemented, rejected, superseded"
)

#: The locked terminal-form message wording (empty `allowed_values` = terminal current state).
_TERMINAL_MESSAGE = (
    "Invalid status transition 'superseded' -> 'draft' for type 'req'. "
    "Status 'superseded' is terminal (no outgoing transitions)."
)


class TestInvalidStatusTransitionResult(unittest.TestCase):
    """Tests for InvalidStatusTransitionResult itself."""

    def test_declares_the_six_fields(self) -> None:
        self.assertEqual(list(InvalidStatusTransitionResult.model_fields.keys()), _EXPECTED_FIELD_NAMES)

    def test_all_fields_are_required(self) -> None:
        for name in _EXPECTED_FIELD_NAMES:
            with self.subTest(field=name):
                self.assertTrue(InvalidStatusTransitionResult.model_fields[name].is_required())

    def test_field_annotations(self) -> None:
        sut = InvalidStatusTransitionResult.model_fields

        self.assertEqual(sut["valid"].annotation, bool)
        self.assertEqual(sut["type"].annotation, str)
        self.assertEqual(sut["from_status"].annotation, str)
        self.assertEqual(sut["to_status"].annotation, str)
        self.assertEqual(sut["allowed_values"].annotation, list[str])
        self.assertEqual(sut["message"].annotation, str)

    def test_constructs_and_holds_the_fields(self) -> None:
        sut = InvalidStatusTransitionResult(
            valid=False,
            type="req",
            from_status="accepted",
            to_status="draft",
            allowed_values=["deprecated", "implemented", "rejected", "superseded"],
            message=_NORMAL_MESSAGE,
        )

        self.assertFalse(sut.valid)
        self.assertEqual(sut.type, "req")
        self.assertEqual(sut.from_status, "accepted")
        self.assertEqual(sut.to_status, "draft")
        self.assertEqual(sut.allowed_values, ["deprecated", "implemented", "rejected", "superseded"])
        self.assertEqual(sut.message, _NORMAL_MESSAGE)

    def test_model_dump_is_the_full_rejection_shape(self) -> None:
        sut = InvalidStatusTransitionResult(
            valid=False,
            type="req",
            from_status="accepted",
            to_status="draft",
            allowed_values=["deprecated", "implemented", "rejected", "superseded"],
            message=_NORMAL_MESSAGE,
        )

        self.assertEqual(
            sut.model_dump(exclude_none=True),
            {
                "valid": False,
                "type": "req",
                "from_status": "accepted",
                "to_status": "draft",
                "allowed_values": ["deprecated", "implemented", "rejected", "superseded"],
                "message": _NORMAL_MESSAGE,
            },
        )

    def test_normal_message_form_is_self_consistent_with_the_sorted_field(self) -> None:
        """The normal form joins `allowed_values` in the field's own (sorted) order -- truncation-safe."""
        allowed_values = ["deprecated", "implemented", "rejected", "superseded"]
        sut = InvalidStatusTransitionResult(
            valid=False,
            type="req",
            from_status="accepted",
            to_status="draft",
            allowed_values=allowed_values,
            message=f"Invalid status transition 'accepted' -> 'draft' for type 'req'. "
            f"Allowed from 'accepted': {', '.join(allowed_values)}",
        )

        self.assertEqual(sut.message, _NORMAL_MESSAGE)
        self.assertEqual(sut.allowed_values, sorted(sut.allowed_values))

    def test_terminal_message_form_carries_an_empty_allowed_values(self) -> None:
        sut = InvalidStatusTransitionResult(
            valid=False,
            type="req",
            from_status="superseded",
            to_status="draft",
            allowed_values=[],
            message=_TERMINAL_MESSAGE,
        )

        self.assertEqual(sut.allowed_values, [])
        self.assertEqual(sut.message, _TERMINAL_MESSAGE)
        self.assertNotIn("Allowed from", sut.message)


if __name__ == "__main__":
    unittest.main()
