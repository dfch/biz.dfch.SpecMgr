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

from typer.main import get_command
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


class TestDiagramAndPlantumlCommands(unittest.TestCase):
    """Registration + help smoke for the feat-185-uc-diagrams Phase 130 commands.

    Pins the ``_callback`` gotcha in both directions: the new ``diagram`` sub-group and the two flat
    ``plantuml-*`` commands register alongside every pre-existing subcommand, and a pre-existing
    subcommand still dispatches (the explicit callback keeps Typer from collapsing the app).
    """

    def test_all_commands_still_registered(self):
        """The full registered command set: the ten pre-existing commands + plantuml-check,
        plantuml-encode, and the diagram sub-group."""
        names = set(get_command(app).commands)

        self.assertEqual(
            names,
            {
                "version",
                "mcp",
                "docs",
                "mcp-docs",
                "adr-toc",
                "coverage-badge",
                "schema",
                "unused-code",
                "req-parse",
                "mdformat",
                "plantuml-check",
                "plantuml-encode",
                "diagram",
            },
        )

    def test_diagram_help_lists_the_uc_subcommand(self):
        """``specmgr diagram --help`` renders and lists the ``uc`` subcommand."""
        result = runner.invoke(app, ["diagram", "--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("uc", _strip_ansi(result.stdout))

    def test_diagram_uc_help_lists_out_and_check(self):
        """``specmgr diagram uc --help`` renders and documents the ``--out``/``--check`` options."""
        result = runner.invoke(app, ["diagram", "uc", "--help"])

        self.assertEqual(result.exit_code, 0)
        stdout = _strip_ansi(result.stdout)
        for option in ("--out", "--check"):
            self.assertIn(option, stdout)

    def test_plantuml_check_help_renders(self):
        """``specmgr plantuml-check --help`` renders."""
        result = runner.invoke(app, ["plantuml-check", "--help"])

        self.assertEqual(result.exit_code, 0)

    def test_plantuml_encode_help_renders(self):
        """``specmgr plantuml-encode --help`` renders."""
        result = runner.invoke(app, ["plantuml-encode", "--help"])

        self.assertEqual(result.exit_code, 0)

    def test_preexisting_command_still_dispatches(self):
        """A pre-existing subcommand still dispatches end-to-end (the ``_callback`` gotcha)."""
        result = runner.invoke(app, ["version"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout.strip(), version("biz-dfch-specmgr"))


if __name__ == "__main__":
    unittest.main()
