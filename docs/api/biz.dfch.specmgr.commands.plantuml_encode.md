# `biz.dfch.specmgr.commands.plantuml_encode`

``plantuml-encode`` -- print the classic PlantUML URL encoding of a diagram source (feat-185-uc-diagrams, Phase 130).

Reads the diagram source from a file (or from stdin when the argument is
``-``) and prints the classic ``SoWkI…``-form encoding —
``plantuml.encode.encode_puml`` verbatim (rulebook §5.1, amended 2026-10-04):
custom-base64 (alphabet ``0-9A-Za-z-_``, digits first) over the raw-deflate
stream of the source's UTF-8 bytes, no prefix. That output is the ``{enc}``
payload of ``GET {base}/svg/{enc}`` — the command takes no base URL, so it
prints the renderable encoding itself (append it to your
``SPECMGR_PLANTUML_URL`` base to render). Fully offline: no Java, no
network, no validation source, no diagram validation.

Exit codes (pinned):

* ``0`` — the encoding was printed
* ``2`` — usage error: the file is missing/unreadable, or the input is empty

## Functions

### `plantuml_encode(source: 'Annotated[str, typer.Argument(help="The .puml file to encode, or \'-\' to read the diagram source from stdin.")]') -> 'None'`

Print the classic PlantUML URL encoding of the diagram source.

The input is the file named by ``source`` (or stdin when ``source`` is
``-``); the output is ``plantuml.encode.encode_puml`` of the full text —
the ``{enc}`` payload of ``GET {base}/svg/{enc}`` (rulebook §5.1). The
command takes no base URL, so it prints the encoding itself. A missing
or unreadable file, or an empty input, is a usage error (exit 2).

