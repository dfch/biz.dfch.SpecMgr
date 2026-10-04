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

"""Tests for the `specmgr://uc/plantuml` resource (`uc.resources.uc_plantuml.uc_plantuml`).

The resource serves the Phase 100 frozen UC → PlantUML rulebook
(``uc/data/uc_plantuml.md``) as raw markdown. Because the rulebook is the
spec the later phases implement against, these tests pin the load-bearing
frozen strings in it (marker grammar, env-var names, the reference
rendering, the URL matrix) so a silent edit of the packaged data file is
caught here rather than surfacing as a renderer/checker drift in Phase 110+.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from mcp.server.mcpserver.resources.base import Resource

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.server import mcp
from biz.dfch.specmgr.uc.resources.uc_plantuml import uc_plantuml

#: The three UNATTRIBUTED marker grammar forms, exactly as frozen in the rulebook.
_MARKER_GRAMMAR_LINES = [
    "' UNATTRIBUTED step {N}: <text>",
    "' UNATTRIBUTED ext {N}{a} step {M}: <text>",
    "' UNATTRIBUTED trigger: <text>",
]

#: The exactly-three validation-source env vars (no defaults, no PATH discovery).
_ENV_VARS = [
    "SPECMGR_PLANTUML_JAR",
    "SPECMGR_PLANTUML_BIN",
    "SPECMGR_PLANTUML_URL",
]

#: The Buy Goods reference rendering's load-bearing lines (the frozen golden for
#: `render_uc_diagram`, §2.6 of the rulebook).
_BUY_GOODS_REFERENCE_LINES = [
    "@startuml Buy Goods",
    "actor Buyer",
    'actor "Credit card company" as actor2',
    "actor Bank",
    'actor "Shipping service" as actor4',
    'usecase "Buy Goods" as uc <<summary>>',
    "Buyer --> uc",
    "actor2 --> uc",
    "Bank --> uc",
    "actor4 --> uc",
    "@enduml",
]

#: The structure checker's verified lenient set, one line each (§6.4).
_LENIENT_SET_LINES = [
    "an unclosed `alt` at EOF",
    "a missing `@enduml`",
    "a bare `@end` (closing an open fragment by name-omission)",
    "a dangling `A -->` (a usecase association with no target on the line)",
    "an undeclared participant in a sequence message (auto-created by the parser)",
]


def _registered_resource(uri: str) -> Resource:
    """Return the registered Resource model for `uri` from the server's resource manager."""
    result = [resource for resource in mcp._resource_manager.list_resources() if resource.uri == uri]
    assert len(result) == 1, f"expected exactly one registration for {uri}, got {len(result)}"
    return result[0]


class TestUcPlantumlResource(unittest.TestCase):
    """Tests for the uc_plantuml resource function."""

    def test_is_registered_with_markdown_mime_type(self):
        """The resource must be registered under its unversioned URI as text/markdown."""
        resource = _registered_resource("specmgr://uc/plantuml")

        self.assertEqual(resource.name, "uc_plantuml")
        self.assertEqual(resource.mime_type, "text/markdown")

    def test_returns_the_packaged_data_file_verbatim(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = uc_plantuml

        result = sut()

        on_disk = _packaged_data.packaged_data_path("uc", "plantuml")
        self.assertIsInstance(result, str)
        self.assertEqual(result, on_disk.read_text(encoding="utf-8"))
        self.assertTrue(result.startswith("# UC → PlantUML Diagram Rulebook"))

    def test_pins_the_unattributed_marker_grammar(self):
        """All three frozen marker forms must appear verbatim (renderer + checker share them)."""
        result = uc_plantuml()

        for line in _MARKER_GRAMMAR_LINES:
            with self.subTest(line=line):
                self.assertIn(line, result)

    def test_pins_the_three_env_vars_and_no_others(self):
        """Exactly the three frozen source env vars; no fourth SPECMGR_PLANTUML_* name."""
        import re

        result = uc_plantuml()

        for var in _ENV_VARS:
            with self.subTest(var=var):
                self.assertIn(var, result)
        found = set(re.findall(r"SPECMGR_PLANTUML_[A-Z_]+", result))
        self.assertEqual(found, set(_ENV_VARS))

    def test_pins_the_buy_goods_reference_rendering(self):
        """The frozen usecase-diagram golden's load-bearing lines must all be present, in order."""
        result = uc_plantuml()

        position = -1
        for line in _BUY_GOODS_REFERENCE_LINES:
            with self.subTest(line=line):
                found_at = result.find(line, position + 1)
                self.assertNotEqual(found_at, -1, f"line missing or out of order: {line!r}")
                position = found_at

    def test_pins_the_url_matrix_and_local_contract_freezes(self):
        """The frozen protocol/classification strings must appear verbatim."""
        result = uc_plantuml()

        for fragment in (
            "GET {base}/svg/{enc}",
            "Welcome to PlantUML!",
            "generated a bad URL",
            "INCONCLUSIVE",
            "PLANTUML_LIMIT_SIZE=8192",
            "--check-syntax --no-error-image -pipe",
            "-checkonly",
            # both documented ERROR-block byte shapes (older one-liner / 1.2026.8 three-line)
            "ERROR / {line} / Syntax Error? (Assumed diagram type: {type})",
            "Syntax Error? (Assumed diagram type: {type})",
            # the amended freeze: the classic no-prefix form + the rejected prefixed forms
            "SoWkI",
            "`~1` was never a real PlantUML URL-decoder prefix",
            'participant "Famous Bob" aass Bob',
            "' validated: structure-only",
            "#quot;",
            "left to right direction",
            'note bottom of {this-alias}: Unresolved UC reference: "{inline text}"',
            "9cfe511e…",
            "cf9a9dfe…",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, result)

    def test_pins_the_five_verified_lenient_cases(self):
        """The checker's verified lenient set must be all five cases, in order."""
        result = uc_plantuml()

        position = -1
        for line in _LENIENT_SET_LINES:
            with self.subTest(line=line):
                found_at = result.find(line, position + 1)
                self.assertNotEqual(found_at, -1, f"lenient case missing or out of order: {line!r}")
                position = found_at

    def test_pins_the_platform_adapter_snippet_and_no_wrapper_claim(self):
        """The docker reference snippet and the 'specmgr ships NO wrapper' claim must be present."""
        result = uc_plantuml()

        self.assertIn('exec docker exec -i plantuml-cli java -jar /opt/plantuml.jar "$@"', result)
        self.assertIn("specmgr ships NO wrapper", result)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            rulebook_path = Path(tmp) / "uc_plantuml.md"
            rulebook_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=rulebook_path):
                sut = uc_plantuml

                first = sut()
                rulebook_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_rulebook_missing(self):
        """A missing packaged rulebook file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = uc_plantuml

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
