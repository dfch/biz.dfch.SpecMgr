# `biz.dfch.specmgr.plantuml.encode`

The PlantUML classic URL text encoding and its inverse (rulebook §5.1).

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

## Functions

### `_base64_custom(data: 'bytes') -> 'str'`

Encode ``data`` in the classic custom-base64 (3 bytes → 4 chars, zero-padded).


### `_base64_custom_decode(payload: 'str') -> 'bytes'`

The inverse of :func:`_base64_custom`.

The padding character (``0``) is indistinguishable from a data ``0`` at
the character level, so the decoder always yields all three bytes of
every group — the encoder's zero-padding makes the trailing bytes of a
partial final group exactly ``0x00``, which the inflating layer ignores
(the end-of-stream marker is the length oracle, not the payload).


### `_deflate_raw(text: 'str') -> 'bytes'`

Compress ``text``'s UTF-8 bytes into a raw deflate stream.


### `_inflate(payload: 'bytes') -> 'bytes'`

Inflate the compressed layer: raw deflate first, the zlib stream as fallback.

The canonical encoder emits raw deflate (the layer plantuml.com accepts —
see the module docstring); the zlib-stream fallback keeps decoding robust
for the layer dev jetty additionally tolerates.


### `decode_puml(encoded: 'str') -> 'str'`

Decode a classic payload back into the original diagram source.

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


### `encode_puml(text: 'str') -> 'str'`

Encode diagram source into a renderable classic PlantUML URL payload.

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

