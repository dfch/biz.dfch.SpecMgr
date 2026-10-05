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

"""Tests for the ``plantuml-encode`` command (feat-185-uc-diagrams, Phase 130).

The command is a thin, fully-offline CLI over ``plantuml.encode.encode_puml``
(the classic ``SoWkI…``-form URL text encoding, rulebook §5.1 — amended
2026-10-04): it prints the ``{enc}`` payload of ``GET {base}/svg/{enc}`` (it
takes no base URL, so the renderable encoding itself is printed). These tests
pin the CLI's own contract: the ACC-006 round-trip on the packaged example
file (the printed encoding decodes back to the file's exact content), stdin
(``-``) parity with the file argument, the classic-alphabet shape, and the
usage-error pin (missing file / empty input → exit 2). The env-gated live test
renders the printed encoding at the configured URL source (ACC-006's live
half; ACC-007: clean skip with a reason otherwise — including when the
selected source is not a URL base).
"""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from typer.testing import CliRunner

from biz.dfch.specmgr.cli import app
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text
from biz.dfch.specmgr.plantuml import url
from biz.dfch.specmgr.plantuml.encode import decode_puml, encode_puml

from tests.conftest import require_plantuml_source

runner = CliRunner()

#: The classic PlantUML URL alphabet (digits first; no prefix, no padding, no URL scheme).
_CLASSIC_ALPHABET = re.compile(r"^[0-9A-Za-z\-_]+$")


class TestPlantumlEncode(unittest.TestCase):
    """The offline contract: round-trip, stdin parity, alphabet shape, usage errors."""

    def setUp(self) -> None:
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.example_text = read_packaged_text("uc", "plantuml_example")
        self.example_path = self.tmp / "example.puml"
        self.example_path.write_text(self.example_text, encoding="utf-8")

    def test_file_arg_prints_the_classic_encoding_that_round_trips(self):
        """ACC-006 (offline half): on the packaged example file, the printed encoding is exactly
        encode_puml of the file's content, is pure classic alphabet, and decodes back to the file's
        exact content."""
        result = runner.invoke(app, ["plantuml-encode", str(self.example_path)])

        self.assertEqual(result.exit_code, 0, result.output)
        encoded = result.stdout.strip()
        self.assertRegex(encoded, _CLASSIC_ALPHABET)
        self.assertNotIn("http", encoded)
        self.assertEqual(encoded, encode_puml(self.example_text))
        self.assertEqual(decode_puml(encoded), self.example_text)

    def test_stdin_matches_the_file_arg(self):
        """The ``-`` stdin literal prints the same encoding as the file argument."""
        by_file = runner.invoke(app, ["plantuml-encode", str(self.example_path)])
        by_stdin = runner.invoke(app, ["plantuml-encode", "-"], input=self.example_text)

        self.assertEqual(by_file.exit_code, 0, by_file.output)
        self.assertEqual(by_stdin.exit_code, 0, by_stdin.output)
        self.assertEqual(by_stdin.stdout, by_file.stdout)

    def test_missing_file_exits_2(self):
        """A missing file is a usage error (exit 2, the name reported)."""
        result = runner.invoke(app, ["plantuml-encode", str(self.tmp / "nope.puml")])

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("unreadable", result.output)

    def test_empty_file_exits_2(self):
        """An empty file is a usage error (exit 2 — there is no diagram source to encode)."""
        empty = self.tmp / "empty.puml"
        empty.write_text("", encoding="utf-8")

        result = runner.invoke(app, ["plantuml-encode", str(empty)])

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("empty", result.output)

    def test_empty_stdin_exits_2(self):
        """Empty stdin is the same usage error (exit 2)."""
        result = runner.invoke(app, ["plantuml-encode", "-"], input="")

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("empty", result.output)


class TestPlantumlEncodeLive(unittest.TestCase):
    """The env-gated live test (ACC-006's live half; ACC-007: clean skip with a reason otherwise)."""

    def test_printed_encoding_renders_at_the_configured_url_source(self):
        """GET {base}/svg/{printed encoding} ⇒ 200 + real diagram SVG (the encoding the command prints
        is renderable on the configured server — no placeholder markers in the body)."""
        info = require_plantuml_source(self)
        if info.kind != "url":
            self.skipTest(
                f"the selected source is {info.kind!r}; the live render needs a URL base (SPECMGR_PLANTUML_URL)"
            )
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        example = tmp / "example.puml"
        example.write_text(read_packaged_text("uc", "plantuml_example"), encoding="utf-8")

        result = runner.invoke(app, ["plantuml-encode", str(example)])
        self.assertEqual(result.exit_code, 0, result.output)
        encoded = result.stdout.strip()

        response = url.fetch_svg(f"{info.value.rstrip('/')}/svg/{encoded}")

        self.assertEqual(response.status, 200, f"body: {response.body[:200]!r}")
        self.assertTrue(url.is_real_svg(response.body))


if __name__ == "__main__":
    unittest.main()
