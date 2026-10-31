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

"""``@mcp.tool()`` wrapper: parse_txt (feat-229-txt Phase 110).

Reads a free-form text markdown file from disk and parses it into a
structured :class:`TxtDocument`, mirroring ``vcr.tools.parse_vcr``'s own
pattern -- read path -> parse via free-function returning typed document
model. A content-validation failure of an existing file (the parser's
``AssertionError``/``pydantic.ValidationError``/``yaml.YAMLError``) is
caught and returned as the non-raising ``ValidateResult``
(feat-204-create-error, ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e -- case
5 of the ADR 519d1206-4d2a-4500-9046-6db635209996 non-raising,
structured-result workaround chain); only the file-access errors raised
by ``Path.read_text()`` for a truly-absent or unreadable path still
surface as MCP tool errors to the caller.

**Path-derived language (feat-197-i18n Phase 125, ADR 38efdb66 item 5).**
A 1:1 port of ``parse_req``'s handling. This tool takes no ``language``
parameter: it derives the effective language from the file's own position
relative to the free-form text base directory
(``general.tools._doc_paths.language_for_doc_path``) -- a file directly in
the flat ``docs/txt/`` directory parses canonical (no heading-mapping
table), a file directly in a shape-validated ``docs/txt/{language}/``
subdirectory parses with that language's table, and any other location
(outside the base, a non-shape-validated subdirectory, a deeper nesting)
parses canonical. A derived language without a table file therefore fails
with the table loader's actionable ``ValueError`` (propagated, like every
other caller-usage error -- the non-raising ``ValidateResult`` channel
covers content-validation failures only).
"""

from __future__ import annotations

from pathlib import Path

from ...general.models import ValidateResult, ValidationErrorEntry
from ...general.tools._doc_paths import language_for_doc_path
from ...general.tools.validate import _CAUGHT_EXCEPTIONS, _MAX_VALIDATE_ERROR_CHARS
from ...models.md._errors import wrap_tool_errors
from ...models.md._markdown import snippet
from ...server import mcp
from ..models.v1 import TxtDocument, parse_txt as _parse_txt
from ._paths import txt_base_dir


@mcp.tool(
    name="parse_txt",
    title="Parse free-form text",
    description=(
        "Parse a free-form text markdown file (YAML frontmatter + body) from disk "
        "into a structured :class:`~biz.dfch.specmgr.txt.models.v1.TxtDocument`. An existing file "
        "that fails to parse returns a non-raising `ValidateResult` (`valid=False`, a single "
        "`errors[].message` capped at 300 chars as the generic `validate` tool caps it, feat-110) "
        "instead of raising `AssertionError`/`pydantic.ValidationError`/`yaml.YAMLError` (ADR "
        "f14f125e-eaad-4f4f-a6fd-3c931bed726e, GitHub issue #204 -- case 5 of the ADR 519d1206 "
        "non-raising-structured-result workaround chain); a truly-absent or unreadable path still "
        "raises the `OSError`-family file-access error (`FileNotFoundError`/`PermissionError`/`OSError`) "
        "from `Path.read_text()`."
        " The file's language is derived from its path position relative to the free-form text base "
        "directory: a file in the flat docs/txt/ directory parses canonical (no heading-mapping table); "
        "a file in a direct two-letter docs/txt/{language}/ subdirectory parses through that language's "
        "table (an actionable ValueError when no table exists for the language); any other location "
        "parses canonical."
    ),
)
def parse_txt(path: str) -> TxtDocument | ValidateResult:
    """Parse the free-form text file at ``path`` into a :class:`TxtDocument`.

    Reads the file from disk, then parses and validates its content. "Parse"
    here also means "validate": letting :class:`Txt` /
    :class:`TxtFrontmatter` / :class:`TxtDocument`'s own Pydantic validators
    run during parsing is the only validation pass there is -- there is
    no separate validation step. Any structural problem (a missing
    ``## Updates`` section, a leftover H2 after it, an empty body) or
    field/cross-field validation failure (e.g. out-of-order ``## Updates``
    entries, a frontmatter ``status`` outside the closed three-value set)
    raises ``AssertionError``/``pydantic.ValidationError`` (a malformed
    frontmatter block raises ``yaml.YAMLError``) internally, but this tool
    catches all three (feat-204-create-error, ADR
    f14f125e-eaad-4f4f-a6fd-3c931bed726e -- case 5 of the ADR
    519d1206-4d2a-4500-9046-6db635209996 non-raising, structured-result
    workaround chain) and returns the enriched message (domain/tool context
    prepended by the shared tool-boundary wrapper,
    :func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`, on top of
    the engine's own field-path/line/snippet enrichment, feat-27-validation
    Phases 1/2), capped at 300 chars exactly as the generic ``validate`` tool
    caps it (feat-110), as the non-raising ``ValidateResult(valid=False, ...)``
    (see Returns below) -- the caller still gets something concrete to
    self-correct from, in-band. File-access errors for a truly-absent or
    unreadable path are never caught: they still propagate as
    ``FileNotFoundError``/``PermissionError``/``OSError`` (see Raises below).

    Parameters
    ----------
    path:
        The filesystem path to the ``.md`` file to parse (absolute or
        relative to the current working directory).

        The file's language is derived from this path's position relative to the
        free-form text base directory (feat-197-i18n Phase 125, ADR 38efdb66 item 5):
        flat ``docs/txt/`` = canonical (no table), a direct shape-validated
        ``docs/txt/{language}/`` subdirectory = that language's table, any
        other location = canonical.

    Returns
    -------
    TxtDocument | ValidateResult
        The parsed, validated document. On an existing file that fails to
        parse, a non-raising
        :class:`~biz.dfch.specmgr.general.models.ValidateResult`
        (``valid=False``) with exactly one ``errors`` entry whose
        ``message`` is the enriched exception text capped at 300 chars
        exactly as the generic ``validate`` tool caps it (feat-110, via
        :func:`~biz.dfch.specmgr.models.md._markdown.snippet`), instead of
        ``AssertionError``/``pydantic.ValidationError``/``yaml.YAMLError``
        (feat-204-create-error, ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e --
        case 5 of the ADR 519d1206-4d2a-4500-9046-6db635209996 non-raising,
        structured-result workaround chain).

    Raises
    ------
    FileNotFoundError / PermissionError / OSError
        A file-access failure reading ``path`` -- the only remaining raise on
        this surface: ``Path.read_text()`` runs outside the tool's own catch,
        so a truly-absent or unreadable path still surfaces the ``OSError``-
        family error to the caller unchanged (the documented file-access
        contract, feat-204-create-error REQ-002).
    ValueError
        The path sits in a direct ``{language}`` subdirectory whose language
        has no packaged heading-mapping table (the table loader's actionable
        error, feat-197-i18n Phase 125).
    """
    doc_path = Path(path)
    text = doc_path.read_text(encoding="utf-8")
    language = language_for_doc_path(txt_base_dir(), doc_path)
    try:
        with wrap_tool_errors(domain="txt", tool="parse_txt"):
            return _parse_txt(text, language=language)
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])
