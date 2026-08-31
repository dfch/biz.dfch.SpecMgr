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

"""Tests for the ``delete_vcr`` ``@mcp.tool()`` stub wrapper (Task 2.1)."""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.vcr.tools.delete_vcr import delete_vcr


class TestDeleteVcr(unittest.TestCase):
    """Tests for the delete_vcr stub tool."""

    def test_raises_not_implemented_error(self) -> None:
        """delete_vcr must always raise NotImplementedError, regardless of id."""
        with self.assertRaises(NotImplementedError):
            delete_vcr("some-id")

    def test_raises_not_implemented_error_for_unknown_id(self) -> None:
        """delete_vcr must never look up or validate the id -- it always raises."""
        with self.assertRaises(NotImplementedError):
            delete_vcr("does-not-exist-and-never-checked")


if __name__ == "__main__":
    unittest.main()
