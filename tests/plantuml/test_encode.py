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

"""Tests for `plantuml.encode` (the classic URL text encoding, rulebook §5.1 —
amended 2026-10-04 to the `SoWkI…` form after the legacy `~1` freeze was found
to be a documentation error: no current 1.2026.8 deployment accepts a prefixed
hex payload over HTTP).

Offline: round-trips (canary, unicode, 25 KB+), the custom-base64/raw-deflate
algorithm pinned by an independent formulation and by exact known vectors
(including the dev server's own root-redirect code, which decodes back to its
diagram text — a cross-implementation pin), and the rejection of non-classic
input (e.g. the legacy `~1` form). The env-gated live test proves the produced
URL renders on the selected source.
"""

import unittest
import zlib
from pathlib import Path

from biz.dfch.specmgr.plantuml import backends, encode, url
from tests.conftest import assert_rendered_svg, require_plantuml_source

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "plantuml"

#: The classic custom-base64 alphabet (digits first — rulebook §5.1).
_CLASSIC_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"


def _classic_of_rawdeflate(text: str) -> str:
    """The payload as an independent formulation: custom-base64 over the
    raw-deflate stream (the zlib stream minus the 2-byte header and the
    4-byte adler32 tail)."""

    def six(value: int) -> str:
        value &= 0x3F
        if value < 10:
            result = "0123456789"[value]
        elif value < 36:
            result = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[value - 10]
        elif value < 62:
            result = "abcdefghijklmnopqrstuvwxyz"[value - 36]
        else:
            result = "-_"[value - 62]
        return result

    compressor = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
    stream = compressor.compress(text.encode("utf-8")) + compressor.flush()
    chars: list[str] = []
    for index in range(0, len(stream), 3):
        chunk = stream[index : index + 3]
        if len(chunk) == 3:
            chars += [
                six(chunk[0] >> 2),
                six(((chunk[0] & 3) << 4) | (chunk[1] >> 4)),
                six(((chunk[1] & 0xF) << 2) | (chunk[2] >> 6)),
                six(chunk[2] & 0x3F),
            ]
        elif len(chunk) == 2:
            chars += [
                six(chunk[0] >> 2),
                six(((chunk[0] & 3) << 4) | (chunk[1] >> 4)),
                six((chunk[1] & 0xF) << 2),
                six(0),
            ]
        else:
            chars += [six(chunk[0] >> 2), six((chunk[0] & 3) << 4), six(0), six(0)]
    result = "".join(chars)
    return result


class TestEncode(unittest.TestCase):
    """Tests for encode_puml/decode_puml (the classic form)."""

    def test_round_trip_canary(self):
        sut = encode.encode_puml

        text = backends.CANARY_DIAGRAM

        result = encode.decode_puml(sut(text))

        self.assertEqual(result, text)

    def test_round_trip_unicode(self):
        sut = encode.encode_puml

        text = "@startuml\nBöb -> Älîce: hëllo wörld — «ünïcode» ✓\n@enduml\n"

        result = encode.decode_puml(sut(text))

        self.assertEqual(result, text)

    def test_round_trip_25kb_plus(self):
        sut = encode.encode_puml

        text = "@startuml\n" + "\n".join(f"participant p{i}\n" for i in range(1500)) + "\nA -> B: x\n@enduml\n"
        self.assertGreater(len(text), 25_000)

        result = encode.decode_puml(sut(text))

        self.assertEqual(result, text)

    def test_round_trip_all_stream_lengths(self):
        """The encoder/decoder pair is exact for every payload length mod 3."""
        sut = encode.encode_puml

        for length in range(1, 30):
            with self.subTest(length=length):
                text = "x" * length
                self.assertEqual(encode.decode_puml(sut(text)), text)

    def test_payload_is_classic_base64_of_the_raw_deflate_stream(self):
        sut = encode.encode_puml

        text = "@startuml\nBob -> Alice: hello\n@enduml\n"
        encoded = sut(text)

        self.assertEqual(encoded, _classic_of_rawdeflate(text))
        self.assertEqual(len(encoded) % 4, 0)
        self.assertTrue(all(character in _CLASSIC_ALPHABET for character in encoded))

    def test_known_vector_canary(self):
        """The exact classic encoding of the canary (pinned 2026-10-04 — the
        `SoWkI…` form that renders on dev jetty AND plantuml.com)."""
        sut = encode.encode_puml

        result = sut(backends.CANARY_DIAGRAM)

        self.assertEqual(result, "SoWkIImgAStDuNBAJrBGjLDmpCbCJhLIo4ZDoSddSaZDIm790G00")

    def test_known_vector_dev_server_redirect_code(self):
        """Cross-implementation pin: the dev server's own root-redirect short
        code (recorded 2026-10-04 from `http://localhost:8080/`) decodes back
        to its diagram text through this module's inverse."""
        sut = encode.decode_puml

        result = sut("SyfFKj2rKt3CoKnELR1Io4ZDoSa70000")

        self.assertEqual(result, "Bob -> Alice : hello")

    def test_decode_accepts_a_full_url(self):
        sut = encode.decode_puml

        text = backends.CANARY_DIAGRAM
        result = sut(f"http://localhost:8080/svg/{encode.encode_puml(text)}")

        self.assertEqual(result, text)

    def test_decode_rejects_non_classic_alphabet_characters(self):
        sut = encode.decode_puml

        for payload in ("+standard/base64", "standard==padding", "a~1-prefixed-payload"):
            with self.subTest(payload=payload):
                with self.assertRaises(AssertionError):
                    sut(payload)

    def test_decode_rejects_invalid_base64_length(self):
        sut = encode.decode_puml

        with self.assertRaises(AssertionError):
            sut("abcde")  # length 5 — no base64 payload has length ≡ 1 (mod 4)

    def test_canary_fixture_file_matches_the_backend_canary(self):
        """The committed canary fixture IS the backend's canary (one probe text)."""
        on_disk = (_FIXTURES / "canary.puml").read_text(encoding="utf-8")

        self.assertEqual(on_disk, backends.CANARY_DIAGRAM)


class TestEncodeLive(unittest.TestCase):
    """Env-gated: the produced classic URL renders on the selected source."""

    def test_encoded_url_renders_on_selected_source(self):
        info = require_plantuml_source(self)
        if info.kind != "url":
            self.skipTest("the live classic-URL render test applies only to a selected URL source")
        assert info.value is not None  # an available source always carries its configured value

        verdict = url.validate_url(info.value, backends.CANARY_DIAGRAM)

        self.assertEqual(verdict.classification, url.CLASS_VALID)
        self.assertIs(verdict.valid, True)
        self.assertIs(verdict.rendered, True)
        self.assertTrue(verdict.proof_path)
        # the Phase 145 render-proof contract: the SVG body carries the diagram
        # text and no crash marker (never is_real_svg alone)
        assert verdict.proof_path is not None
        assert_rendered_svg(Path(verdict.proof_path).read_bytes(), "hello")


if __name__ == "__main__":
    unittest.main()
