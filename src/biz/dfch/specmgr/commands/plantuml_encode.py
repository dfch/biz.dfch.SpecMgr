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

"""``plantuml-encode`` -- print the classic PlantUML URL encoding of a diagram source (feat-185-uc-diagrams, Phase 130).

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
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer

from ..plantuml.encode import encode_puml

__all__ = ["plantuml_encode"]

#: The stdin literal (the argument value that reads the diagram source from stdin).
STDIN_LITERAL = "-"

#: The usage-error exit code (missing/unreadable file, empty input).
EXIT_USAGE = 2


def plantuml_encode(
    source: Annotated[
        str,
        typer.Argument(help="The .puml file to encode, or '-' to read the diagram source from stdin."),
    ],
) -> None:
    """Print the classic PlantUML URL encoding of the diagram source.

    The input is the file named by ``source`` (or stdin when ``source`` is
    ``-``); the output is ``plantuml.encode.encode_puml`` of the full text —
    the ``{enc}`` payload of ``GET {base}/svg/{enc}`` (rulebook §5.1). The
    command takes no base URL, so it prints the encoding itself. A missing
    or unreadable file, or an empty input, is a usage error (exit 2).
    """
    try:
        if source == STDIN_LITERAL:
            text = sys.stdin.read()
        else:
            text = Path(source).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as ex:
        typer.echo(f"error: {source}: unreadable ({ex}) (usage error)", err=True)
        raise typer.Exit(EXIT_USAGE) from ex
    if not text:
        typer.echo(f"error: {source}: empty input (no diagram source to encode) (usage error)", err=True)
        raise typer.Exit(EXIT_USAGE)
    typer.echo(encode_puml(text))
