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

"""Tests for `general.models.parse_failure_result.ParseFailureResult` (feat-150-mcp-lifecycle-commands Phase 1a,
REQ-013, ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c)."""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.general.models import ParseFailureResult

#: The exact field names `ParseFailureResult` declares (the ADR 9080b37c's fixed shape).
_EXPECTED_FIELD_NAMES = ["error", "path", "id"]


class TestParseFailureResult(unittest.TestCase):
    """Tests for ParseFailureResult itself."""

    def test_declares_the_three_fields(self) -> None:
        self.assertEqual(list(ParseFailureResult.model_fields.keys()), _EXPECTED_FIELD_NAMES)

    def test_all_fields_are_required_strings(self) -> None:
        for name in _EXPECTED_FIELD_NAMES:
            with self.subTest(field=name):
                self.assertTrue(ParseFailureResult.model_fields[name].is_required())
                self.assertEqual(ParseFailureResult.model_fields[name].annotation, str)

    def test_constructs_and_holds_the_fields(self) -> None:
        sut = ParseFailureResult(error="boom", path="/abs/doc.md", id="some-id")

        self.assertEqual(sut.error, "boom")
        self.assertEqual(sut.path, "/abs/doc.md")
        self.assertEqual(sut.id, "some-id")

    def test_model_dump_is_the_full_failure_shape(self) -> None:
        """The exclude_none dump must be exactly the {error, path, id} failure shape the SDK serializes."""
        sut = ParseFailureResult(error="boom", path="/abs/doc.md", id="some-id")

        self.assertEqual(sut.model_dump(exclude_none=True), {"error": "boom", "path": "/abs/doc.md", "id": "some-id"})


if __name__ == "__main__":
    unittest.main()
