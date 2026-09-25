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
``tests/commands/``; this module covers registration on ``app`` plus the
import-scope ``.env`` ordering of ``cli.py`` itself (the project ``.env``'s
``SPECMGR_LOG_*``/``SPECMGR_OTEL_*`` values must be loaded before the command
import chain executes ``server.py``'s module scope, where the telemetry
config is read from ``os.environ`` at import time).
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from importlib.metadata import version
from pathlib import Path

from typer.testing import CliRunner

from biz.dfch.specmgr import cli
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


def _stripped_telemetry_env() -> dict[str, str]:
    """Return the current environment with every ``SPECMGR_*`` var removed."""
    return {name: value for name, value in os.environ.items() if not name.startswith("SPECMGR_")}


def _upward_env_file(from_file: Path) -> Path | None:
    """Return the first ``.env`` found walking up from ``from_file``'s directory, or ``None``.

    Replicates python-dotenv's ``find_dotenv(usecwd=False)`` start point: the
    first stack frame outside the dotenv package is ``cli.py``'s own
    ``_load_default_dotenv``, so the upward search starts at ``cli.py``'s
    directory regardless of the caller's CWD.
    """
    directory = from_file.resolve().parent
    while True:
        candidate = directory / ".env"
        if candidate.is_file():
            return candidate
        if directory.parent == directory:
            return None
        directory = directory.parent


class TestDotenvTelemetryOrdering(unittest.TestCase):
    """End-to-end (subprocess): a project ``.env``'s telemetry vars reach ``server.py``'s import scope.

    ``cli.py``'s command import chain transitively executes ``server.py``'s
    module scope -- where ``load_telemetry_config()``/``setup_logging()``/
    ``bootstrap_telemetry()`` read ``os.environ`` at import time -- so
    ``cli.py`` must load the default ``.env`` BEFORE that import. Every other
    ``SPECMGR_*`` variable family reads its env var lazily at call time and
    is unaffected by the ordering; this family was the only one broken by it
    (a ``.env``-only enablement was silently ignored, the fail-closed refusal
    was bypassed for a ``.env``-only misconfiguration, and the status
    resource reported a config that was not in effect). Both directions are
    pinned here with a fresh child process and a clean (``SPECMGR_*``-
    stripped) process environment -- the child's only telemetry
    configuration is the temp ``.env``.
    """

    #: The child script: import the CLI (executing the import scope under
    #: test) and report the root logger's handler/formatter classes.
    _CHILD_IMPORT_SCRIPT = (
        "import json, logging\n"
        "import biz.dfch.specmgr.cli\n"
        "root = logging.getLogger()\n"
        "handlers = [\n"
        '    {"handler": type(h).__name__,\n'
        '     "formatter": type(h.formatter).__name__ if getattr(h, "formatter", None) else None}\n'
        "    for h in root.handlers\n"
        "]\n"
        "print(json.dumps(handlers))\n"
    )

    def _assert_temp_dotenv_is_the_resolved_one(self) -> None:
        """Skip if a ``.env`` above the installed ``cli.py`` would shadow the temp one.

        ``find_dotenv(usecwd=False)`` walks up from ``cli.py``'s directory
        before the CWD fallback engages; on a machine with a stray ``.env``
        higher up the tree (none in the CI checkouts), the child would load
        that file instead of the test's, so the assertion below would no
        longer test what it claims to.
        """
        upward = _upward_env_file(Path(cli.__file__))
        if upward is not None:
            self.skipTest(f"a .env at {upward} would be loaded before the temp .env (find_dotenv's upward search)")

    def test_env_only_enablement_installs_the_configured_logging_at_import(self):
        """``SPECMGR_LOG_ENABLED=true`` + ``SPECMGR_LOG_FORMAT=json`` in a ``.env`` alone takes effect.

        The child imports ``biz.dfch.specmgr.cli`` with a clean process
        environment; the ``.env``-configured JSON console handler
        (a ``StreamHandler`` carrying the scrub-wired
        ``ScrubbingFormatter``) must be installed on the root logger by the
        import -- red against the pre-fix ordering, where the import-time
        config read saw the clean environment and left the SDK's own
        default handlers in place.
        """
        self._assert_temp_dotenv_is_the_resolved_one()
        with tempfile.TemporaryDirectory(prefix="specmgr-dotenv-test-") as tmpdir:
            (Path(tmpdir) / ".env").write_text("SPECMGR_LOG_ENABLED=true\nSPECMGR_LOG_FORMAT=json\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-c", self._CHILD_IMPORT_SCRIPT],
                capture_output=True,
                text=True,
                env=_stripped_telemetry_env(),
                cwd=tmpdir,
                timeout=120,
            )
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        self.assertEqual(len(lines), 1, f"expected exactly one stdout line (the JSON report), got: {result.stdout!r}")
        handlers = json.loads(lines[0])
        self.assertIn({"handler": "StreamHandler", "formatter": "ScrubbingFormatter"}, handlers)

    def test_env_only_misconfiguration_fails_closed_at_import(self):
        """A ``.env``-only static misconfiguration refuses to start (ACC-011).

        With ``SPECMGR_LOG_FILE_ENABLED=true`` and no ``SPECMGR_LOG_FILE_PATH``
        in the ``.env`` (and a clean process environment), ``python -m
        biz.dfch.specmgr version`` must refuse with exit code 1, empty
        stdout, and exactly one stderr line -- the ``TelemetryConfigError``
        message naming the offending env var(s) -- before any command
        dispatch. Red against the pre-fix ordering, where the validation ran
        against the clean environment and the ``.env`` misconfiguration was
        silently bypassed.
        """
        self._assert_temp_dotenv_is_the_resolved_one()
        with tempfile.TemporaryDirectory(prefix="specmgr-dotenv-test-") as tmpdir:
            (Path(tmpdir) / ".env").write_text("SPECMGR_LOG_FILE_ENABLED=true\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "biz.dfch.specmgr", "version"],
                capture_output=True,
                text=True,
                env=_stripped_telemetry_env(),
                cwd=tmpdir,
                timeout=120,
            )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        lines = [line for line in result.stderr.splitlines() if line.strip()]
        self.assertEqual(len(lines), 1, f"expected exactly one stderr line, got: {result.stderr!r}")
        self.assertIn("SPECMGR_LOG_FILE_PATH", lines[0])
        self.assertIn("SPECMGR_LOG_FILE_ENABLED", lines[0])
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
