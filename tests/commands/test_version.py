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

"""Tests for the ``version`` command."""

import io
import unittest
from contextlib import redirect_stdout
from importlib.metadata import version as installed_version

from biz.dfch.specmgr.commands.version import version


class TestVersionCommand(unittest.TestCase):
    """Tests for the ``version`` command function."""

    def test_prints_installed_version(self):
        """The command must print the installed package version."""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            version()
        self.assertEqual(buffer.getvalue().strip(), installed_version("biz-dfch-specmgr"))


if __name__ == "__main__":
    unittest.main()
