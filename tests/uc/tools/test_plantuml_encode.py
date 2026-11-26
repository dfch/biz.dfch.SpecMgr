# Copyright (C) 2026 Ronald Rink, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for the ``plantuml_encode`` ``@mcp.tool()`` wrapper (feat-185-uc-diagrams, Phase 120).

The tool is a direct, thin, fully-offline wrapper over
``plantuml.encode.encode_puml`` (the classic ``SoWkI…``-form URL text
encoding, rulebook §5.1): these tests pin the wrapper's own contract --
it returns exactly the library's encoding (the ``{enc}`` payload of
``GET {base}/svg/{enc}``, not a URL: the tool takes no base URL), the
classic alphabet, the known vector, and the lossless decode round-trip.
"""

from __future__ import annotations

import re
import unittest

from biz.dfch.specmgr.plantuml.backends import CANARY_DIAGRAM
from biz.dfch.specmgr.plantuml.encode import decode_puml, encode_puml
from biz.dfch.specmgr.uc.tools.plantuml_encode import plantuml_encode

#: The classic PlantUML URL alphabet (digits first; no prefix, no padding).
_CLASSIC_ALPHABET = re.compile(r"^[0-9A-Za-z\-_]+$")


class TestPlantumlEncode(unittest.TestCase):
    """Tests for the plantuml_encode tool."""

    def test_returns_exactly_the_library_encoding(self):
        """The tool must return encode_puml(text) byte-for-byte (no URL, no prefix, no wrapper)."""
        text = "@startuml\nBob -> Alice: hello\n@enduml\n"

        self.assertEqual(plantuml_encode(text), encode_puml(text))

    def test_known_vector_canary(self):
        """The shared canary diagram must encode to the known classic form (the SoWkI... anchor,
        rulebook §5.1; the same vector the Phase 110 library test pins)."""
        self.assertEqual(plantuml_encode(CANARY_DIAGRAM), "SoWkIImgAStDuNBAJrBGjLDmpCbCJhLIo4ZDoSddSaZDIm790G00")

    def test_result_is_classic_alphabet_only(self):
        """The result must be pure classic base64 (0-9A-Za-z-_), no prefix, no padding, no URL."""
        for text in ("", "x", "@startuml\nBob -> Alice: hello\n@enduml\n", "Ünïcödé diagram — ☃"):
            with self.subTest(text=text[:20]):
                result = plantuml_encode(text)
                self.assertRegex(result, _CLASSIC_ALPHABET)
                self.assertNotIn("http", result)
                self.assertNotIn("~~", result)

    def test_round_trip_encode_decode(self):
        """decode_puml(plantuml_encode(text)) == text for the wrapper's outputs (lossless)."""
        texts = (
            "",
            "hello",
            '@startuml\nparticipant "Famous Bob" aass Bob\n@enduml\n',
            "Ünïcödé — «quotes» & <tags> \\ backslash\nline2  spaces",
            "x" * 25_000,
        )
        for text in texts:
            with self.subTest(text=text[:20]):
                self.assertEqual(decode_puml(plantuml_encode(text)), text)

    def test_larger_diagram_round_trip(self):
        """A 25 KB+ diagram (past the old dev jetty's 8192 decoded limit) round-trips losslessly."""
        text = "@startuml\n" + "\n".join(f"p{i} -> p{i + 1}: message {i}" for i in range(1000)) + "\n@enduml\n"
        self.assertGreater(len(text.encode("utf-8")), 25_000)

        self.assertEqual(decode_puml(plantuml_encode(text)), text)


if __name__ == "__main__":
    unittest.main()
