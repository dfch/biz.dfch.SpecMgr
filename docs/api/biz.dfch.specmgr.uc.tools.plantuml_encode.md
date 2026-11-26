# `biz.dfch.specmgr.uc.tools.plantuml_encode`

``@mcp.tool()`` wrapper: plantuml_encode (feat-185-uc-diagrams, Phase 120).

Direct, thin wrapper over ``plantuml.encode.encode_puml`` (Phase 110) --
the PlantUML classic text encoding (custom-base64 ``0-9A-Za-z-_`` over the
raw-deflate stream of the text's UTF-8 bytes, no prefix; the ``SoWkI…``
form, rulebook ``specmgr://uc/plantuml`` §5.1). Fully offline: no source,
no subprocess, no network.

The tool returns the **encoding itself** -- the ``{enc}`` payload of
``GET {base}/svg/{enc}`` -- not a full URL: it takes no base URL, and the
renderable URL is the configured server's base (``SPECMGR_PLANTUML_URL``
for the ``url`` source) with the encoding appended.

## Functions

### `plantuml_encode(text: 'str') -> 'str'`

Encode ``text`` to the PlantUML classic URL encoding.

Parameters
----------
text:
    The diagram source (or any text) to encode.

Returns
-------
str
    The classic (``SoWkI…``-form) encoding of ``text``'s UTF-8 bytes --
    the ``{enc}`` payload for ``GET {base}/svg/{enc}``. The tool takes
    no base URL, so the result is the encoding itself, not a full URL:
    prepend the configured server base to make it renderable.

