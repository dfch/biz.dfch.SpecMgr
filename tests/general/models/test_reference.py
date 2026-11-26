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

"""Tests for `general.models.reference.ReferenceRow` (feat-144-ref-artifact Phase 3, Task 3.1)."""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.general.models.reference import ReferenceRow

#: A canonical lowercase 8-4-4-4-12 hex UUID.
_UUID = "4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d"

#: A not-found reference's error message (the target domain's own wording).
_NOT_FOUND_ERROR = "no requirement found with id '4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d'."


class TestReferenceRow(unittest.TestCase):
    """Tests for ReferenceRow."""

    def test_holds_fields_in_the_documented_order(self):
        self.assertEqual(
            list(ReferenceRow.model_fields.keys()),
            ["type", "id", "title", "path", "error"],
        )

    def test_title_path_and_error_default_to_none(self):
        sut = ReferenceRow(type="req", id=_UUID)

        self.assertEqual(sut.type, "req")
        self.assertEqual(sut.id, _UUID)
        self.assertIsNone(sut.title)
        self.assertIsNone(sut.path)
        self.assertIsNone(sut.error)

    def test_constructs_a_fully_populated_resolved_row(self):
        path = f"/tmp/docs/req/{_UUID}-maximum-engine-temperature.md"
        sut = ReferenceRow(type="req", id=_UUID, title="Maximum Engine Temperature", path=path)

        self.assertEqual(sut.type, "req")
        self.assertEqual(sut.id, _UUID)
        self.assertEqual(sut.title, "Maximum Engine Temperature")
        self.assertEqual(sut.path, path)
        self.assertIsNone(sut.error)

    def test_constructs_a_not_found_row(self):
        sut = ReferenceRow(type="req", id=_UUID, error=_NOT_FOUND_ERROR)

        self.assertEqual(sut.type, "req")
        self.assertEqual(sut.id, _UUID)
        self.assertIsNone(sut.title)
        self.assertIsNone(sut.path)
        self.assertEqual(sut.error, _NOT_FOUND_ERROR)

    def test_serializes_to_the_documented_shape(self):
        sut = ReferenceRow(type="req", id=_UUID)

        dumped = sut.model_dump()

        self.assertEqual(
            dumped,
            {"type": "req", "id": _UUID, "title": None, "path": None, "error": None},
        )

    def test_serializes_a_fully_populated_row(self):
        path = f"/tmp/docs/req/{_UUID}-maximum-engine-temperature.md"
        sut = ReferenceRow(type="req", id=_UUID, title="Maximum Engine Temperature", path=path)

        dumped = sut.model_dump()

        self.assertEqual(
            dumped,
            {
                "type": "req",
                "id": _UUID,
                "title": "Maximum Engine Temperature",
                "path": path,
                "error": None,
            },
        )


if __name__ == "__main__":
    unittest.main()
