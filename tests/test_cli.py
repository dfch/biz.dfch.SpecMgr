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

"""Tests for the ``specmgr`` Typer ``app`` wiring in ``cli.py``.

Requires the ``cli`` and ``mcp`` extras (``pip install "biz-dfch-specmgr[cli,mcp]"``).
Per-command behaviour is tested next to each command under
``tests/commands/``; this module only covers registration on ``app``.
"""

import re
import unittest
from importlib.metadata import version

from typer.testing import CliRunner

from biz.dfch.specmgr.cli import app

runner = CliRunner()

_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    """Remove ANSI colour/style escape codes from Rich-rendered CLI output.

    Typer/Rich may render ``--transport`` as two adjacent, identically
    styled spans (``-`` and ``-transport``), each wrapped in its own
    escape sequence. Whether that happens depends on colour/terminal
    detection (e.g. ``FORCE_COLOR`` in CI vs. a plain local shell), which
    would otherwise make plain substring checks like ``"--transport" in
    stdout`` environment-dependent.
    """
    return _ANSI_ESCAPE_RE.sub("", text)


class TestVersionCommand(unittest.TestCase):
    """Tests for the ``specmgr version`` command registration."""

    def test_prints_installed_version(self):
        """The command must print the installed package version."""
        result = runner.invoke(app, ["version"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout.strip(), version("biz-dfch-specmgr"))


class TestMcpCommand(unittest.TestCase):
    """Tests for the ``specmgr mcp`` command registration."""

    def test_mcp_is_registered(self):
        """The ``mcp`` command must be registered on the Typer app."""
        names = set()
        for command in app.registered_commands:
            assert command.callback is not None
            names.add(command.callback.__name__)

        self.assertIn("mcp", names)

    def test_mcp_help_lists_transport_host_port_options(self):
        """``mcp --help`` must document the transport, host, and port options."""
        result = runner.invoke(app, ["mcp", "--help"])
        self.assertEqual(result.exit_code, 0)
        stdout = _strip_ansi(result.stdout)
        for option in ("--transport", "-t", "--host", "-h", "--port", "-p"):
            self.assertIn(option, stdout)


if __name__ == "__main__":
    unittest.main()
