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

"""The PlantUML classic URL text encoding and its inverse (rulebook §5.1).

A classic payload is PlantUML's **custom-base64** encoding (alphabet
``0-9A-Za-z-_`` — digits first, 3 bytes → 4 characters, the trailing partial
group zero-padded) of the **raw-deflate** stream of the UTF-8 diagram
source, with **no prefix** — the ``SoWkI…`` form of every historical
``plantuml.com/plantuml/svg/`` URL (the server's own short-form redirects
use it). Raw deflate is what ``zlib`` produces with ``wbits = -MAX_WBITS`` —
equivalently, a standard zlib stream (``zlib.compress``) with its 2-byte
header (``0x78 0x9C``) and 4-byte adler32 tail stripped.

Amendment history (rulebook §5.1): the design-time (2026-10-03) freeze said
``~1`` + hex; that was a documentation error — ``~1`` is **not** a real
PlantUML URL-decoder prefix (only ``~b``/``~h`` exist in the decoder), and
current 1.2026.8 deployments reject every prefixed hex form over HTTP
(``~1``/``~b`` → the 200 request-error placeholder, the public server: the
"generated a bad URL" explanatory; ``~h`` → the 400 placeholder — verified
2026-10-04 against dev jetty + plantuml.com). The classic no-prefix form is
the only encoding that renders on both servers, and is frozen as the
protocol (user-approved amendment, 2026-10-04). Note the compression layer:
plantuml.com (1.2026.8) decodes the custom-base64 and inflates **raw**
deflate only — the same payload zlib-wrapped is answered "generated a bad
URL" there, while dev jetty accepts both layers; raw deflate is therefore
the canonical. A legacy ``~1`` payload is **not** decodable by this module
(no server ever accepted it) — :func:`decode_puml` rejects it like any
other non-classic input.

Stdlib-only (``zlib``); no specmgr import.
"""

from __future__ import annotations

import zlib

__all__ = [
    "decode_puml",
    "encode_puml",
]

#: The PlantUML classic custom-base64 alphabet (digits first — NOT standard
#: base64; 62 = ``-``, 63 = ``_``).
_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"

#: The inverse alphabet map (character → 6-bit value).
_ALPHABET_INDEX = {character: index for index, character in enumerate(_ALPHABET)}

#: The deflate compression level (best) — a size property only; any valid
#: raw-deflate stream decodes identically on the server side.
_COMPRESSION_LEVEL = 9

#: The negative ``zlib`` ``wbits`` value for a raw deflate stream (no zlib
#: header, no adler32 tail).
_RAW_WBITS = -zlib.MAX_WBITS


def _deflate_raw(text: str) -> bytes:
    """Compress ``text``'s UTF-8 bytes into a raw deflate stream."""
    compressor = zlib.compressobj(_COMPRESSION_LEVEL, zlib.DEFLATED, _RAW_WBITS)
    result = compressor.compress(text.encode("utf-8")) + compressor.flush()
    return result


def _base64_custom(data: bytes) -> str:
    """Encode ``data`` in the classic custom-base64 (3 bytes → 4 chars, zero-padded)."""
    chars: list[str] = []
    for index in range(0, len(data), 3):
        chunk = data[index : index + 3]
        if len(chunk) == 3:
            chars += [
                _ALPHABET[chunk[0] >> 2],
                _ALPHABET[((chunk[0] & 3) << 4) | (chunk[1] >> 4)],
                _ALPHABET[((chunk[1] & 0xF) << 2) | (chunk[2] >> 6)],
                _ALPHABET[chunk[2] & 0x3F],
            ]
        elif len(chunk) == 2:
            chars += [
                _ALPHABET[chunk[0] >> 2],
                _ALPHABET[((chunk[0] & 3) << 4) | (chunk[1] >> 4)],
                _ALPHABET[(chunk[1] & 0xF) << 2],
                _ALPHABET[0],
            ]
        else:
            chars += [_ALPHABET[chunk[0] >> 2], _ALPHABET[(chunk[0] & 3) << 4], _ALPHABET[0], _ALPHABET[0]]
    result = "".join(chars)
    return result


def _base64_custom_decode(payload: str) -> bytes:
    """The inverse of :func:`_base64_custom`.

    The padding character (``0``) is indistinguishable from a data ``0`` at
    the character level, so the decoder always yields all three bytes of
    every group — the encoder's zero-padding makes the trailing bytes of a
    partial final group exactly ``0x00``, which the inflating layer ignores
    (the end-of-stream marker is the length oracle, not the payload).
    """
    assert len(payload) % 4 != 1, f"classic payload length {len(payload)} is not a valid base64 length"
    out = bytearray()
    for index in range(0, len(payload), 4):
        values = [_ALPHABET_INDEX[character] for character in payload[index : index + 4]]
        out.append((values[0] << 2) | (values[1] >> 4))
        out.append(((values[1] & 0xF) << 4) | (values[2] >> 2))
        out.append(((values[2] & 0x3) << 6) | values[3])
    result = bytes(out)
    return result


def _inflate(payload: bytes) -> bytes:
    """Inflate the compressed layer: raw deflate first, the zlib stream as fallback.

    The canonical encoder emits raw deflate (the layer plantuml.com accepts —
    see the module docstring); the zlib-stream fallback keeps decoding robust
    for the layer dev jetty additionally tolerates.
    """
    try:
        result = zlib.decompress(payload, _RAW_WBITS)
        return result
    except zlib.error:
        result = zlib.decompress(payload)
        return result


def encode_puml(text: str) -> str:
    """Encode diagram source into a renderable classic PlantUML URL payload.

    Parameters
    ----------
    text:
        The full PlantUML diagram source (``@startuml`` ... ``@enduml``).

    Returns
    -------
    str
        The custom-base64 (``0-9A-Za-z-_``) of the raw-deflate stream of
        ``text``'s UTF-8 bytes — no prefix (the ``SoWkI…`` form). Feed it to
        the URL backend as ``GET {base}/svg/{payload}`` (rulebook §5.1) or
        pipe the *decoded source* (not the payload) to a jar/bin backend,
        whose ``-pipe`` input is plain diagram text.
    """
    assert isinstance(text, str), type(text)

    result = _base64_custom(_deflate_raw(text))
    return result


def decode_puml(encoded: str) -> str:
    """Decode a classic payload back into the original diagram source.

    The inverse of :func:`encode_puml` — the round-trip
    ``decode_puml(encode_puml(text)) == text`` holds for every ``text``.

    Parameters
    ----------
    encoded:
        The classic payload (custom-base64, no prefix), or a full
        ``{base}/svg/{payload}`` URL (the last path segment is taken; the
        base URL is ignored).

    Returns
    -------
    str
        The decoded diagram source.

    Raises
    ------
    AssertionError
        ``encoded`` is not a ``str``, its payload characters are outside the
        classic alphabet (e.g. a legacy ``~1`` hex payload — not decodable by
        this module, see the module docstring), or its length is not a valid
        base64 length.
    zlib.error
        The payload is alphabet-valid but neither layer inflates (corrupted).
    UnicodeDecodeError
        The inflated bytes are not valid UTF-8.
    """
    assert isinstance(encoded, str), type(encoded)

    payload = encoded.rsplit("/", 1)[-1] if "://" in encoded else encoded
    assert payload, "expected a non-empty classic payload"
    assert all(character in _ALPHABET_INDEX for character in payload), (
        f"character outside the classic PlantUML alphabet in {payload[:32]!r}…"
    )

    result = _inflate(_base64_custom_decode(payload)).decode("utf-8")
    return result
