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

"""Per-language section-heading mapping tables: the lazy loader and the fence-aware
normalization pre-pass (feat-197-i18n Phase 110).

Implements ADR 38efdb66's items 3/4/5 for the read side: one flat JSON
object per language at ``general/data/headings/<language>.json`` mapping
``<translated heading text> -> <canonical English heading text>`` (keys and
values are the heading's inline text without the leading ``#`` markers and
without surrounding whitespace -- exactly the string the ``models/md``
engine's ``match_alias`` sees). The table's domain is closed: exactly the
fixed-text heading aliases (LITERAL, SPACE_SEPARATED, or REGEX without a
free-text group) of the i18n-eligible domains' document models; headings
whose alias carries free text (``Option {N}:``, ``Step {N}:``, timestamp-led
update entries, ...) hold no entry, and their schema-constant tokens stay
canonical in the variant file itself (REQ-010). There is no file for the
default language EN (:data:`DEFAULT_LANGUAGE`): EN is the canonical form
itself, so it needs no table.

:func:`load_heading_table` resolves lazily, once per process per language,
via :mod:`importlib.resources` (the existing ``general/data`` packaged-data
precedent, the ``general_*.md`` files), and rejects a table whose values
are not pairwise distinct -- two distinct canonical headings must never
translate to the same string, since a document heading to that string would
then be structurally ambiguous. A shape-valid language with no table file
is UNUSABLE: the loader raises an actionable :class:`ValueError` (the
shape guard itself, :func:`~biz.dfch.specmgr.general.tools._path_safety.
assert_language`, is deliberately shape-only -- the open set passes, and
this is the closed-set check, ADR item 6).

:func:`normalize_heading_lines` is the pre-parse heading-normalization
pre-pass of ADR item 5: a fence-aware (``` / ~~~ code fences), line-based
transform that rewrites each ``^#{1,6} `` heading line outside a fence to
its canonical text when (and only when) the table maps it, leaving every
other line byte-identical. It sits at each domain's text-to-model parse
boundary (for the pilot domain ``dec``, :func:`biz.dfch.specmgr.
dec.models.v1.parse_dec`) *after* the mdformat normalization and *before*
the unchanged ``models/md`` engine runs -- the engine then sees canonical
English heading text, the parsed model holds the same canonical keys the EN
parser produces (ACC-011), and the on-disk file keeps its translation
(``raw=True`` reads return it verbatim).
"""

from __future__ import annotations

import json
import re
import threading
from collections.abc import Iterator
from importlib import resources
from importlib.resources.abc import Traversable

from ..tools._path_safety import DEFAULT_LANGUAGE

__all__ = [
    "heading_table_path",
    "iter_heading_lines",
    "load_heading_table",
    "normalize_heading_lines",
    "reset_heading_table_cache",
    "resolve_heading_table",
]

#: The anchor package whose packaged data holds the per-language tables
#: (the existing ``general/data`` precedent, ``general/data/general_*.md``):
#: the file for a language is ``general/data/headings/<language>.json``.
_TABLES_PACKAGE = "biz.dfch.specmgr.general"

#: Process-wide lazy cache: language -> the loaded table. A language whose
#: load failed is never stored -- the next call retries, so a broken table
#: must not pin its error for the process's lifetime.
_loaded_tables: dict[str, dict[str, str]] = {}

#: Guards :data:`_loaded_tables` bookkeeping (the MCP SDK thread-pools every
#: sync tool call, so two calls for the same not-yet-loaded language can
#: race; the load is idempotent, so the race is benign -- the lock just
#: keeps the dict mutation itself atomic, the ``_embedding_cache``'s own
#: lock precedent).
_load_lock = threading.Lock()

#: An ATX heading line in mdformat-normalized form: 1-6 hashes, one space,
#: then the inline text (the ADR item 5 ``^#{1,6} `` match, trailing
#: whitespace tolerated for the lookup key).
_HEADING_LINE_PATTERN = re.compile(r"^(#{1,6}) (.+)$")

#: A fenced-code-block opener: up to three leading spaces, then three or
#: more backticks (whose info string may not itself contain a backtick,
#: CommonMark) or three or more tildes.
_FENCE_OPEN_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def heading_table_path(language: str) -> Traversable:
    """Return the ``Traversable`` for ``general/data/headings/<language>.json``.

    The single seam every caller (and every test) goes through for the
    table file's location (the ``general.tools._packaged_data.
    packaged_data_path`` precedent): tests patch this one function to
    redirect a load at a temporary file instead of touching
    :mod:`importlib.resources` itself. Never reads the file or checks its
    existence -- purely a path computation.

    Parameters
    ----------
    language:
        The language code naming the table file (e.g. ``"de"``).

    Returns
    -------
    Traversable
        A lazily-resolved path-like handle; nothing is read yet.
    """
    assert isinstance(language, str), type(language)

    result: Traversable = resources.files(_TABLES_PACKAGE) / "data" / "headings" / f"{language}.json"
    return result


def load_heading_table(language: str) -> dict[str, str]:
    """Load a language's heading-mapping table, lazily once per process.

    Reads ``general/data/headings/<language>.json`` via
    :func:`heading_table_path`, validates it, and caches the parsed object
    process-wide (a second call for the same language never re-reads or
    re-parses). There is no table for the default language EN -- call
    :func:`resolve_heading_table` for the omitted/EN-aware entry point.

    Parameters
    ----------
    language:
        The language code to load the table for (e.g. ``"de"``). Shape
        validation is the caller's job (:func:`biz.dfch.specmgr.
        general.tools._path_safety.assert_language` at every tool
        boundary); this function only requires the value to be a
        non-empty-enough ``str`` to name a file.

    Returns
    -------
    dict[str, str]
        The flat ``<translated heading text> -> <canonical English heading
        text>`` mapping.

    Raises
    ------
    ValueError
        The table file does not exist (the shape-valid-but-unusable
        language, ADR item 3/6 -- the message names the missing file and
        what adding it would enable), the file is not valid JSON, is not a
        flat ``str -> str`` object, or carries two distinct canonical
        headings translated to the same string (values must be pairwise
        distinct).
    """
    assert isinstance(language, str), type(language)

    with _load_lock:
        if language in _loaded_tables:
            return _loaded_tables[language]

        ref = heading_table_path(language)
        if not ref.is_file():
            raise ValueError(
                f"no heading-mapping table for language {language!r} (no packaged file at "
                f"general/data/headings/{language}.json): the language is shape-valid but "
                f"unusable -- add the table file to read or write documents in {language!r}"
            )
        try:
            raw = json.loads(ref.read_text(encoding="utf-8"))
        except json.JSONDecodeError as ex:
            raise ValueError(f"heading-mapping table for language {language!r} is not valid JSON: {ex}") from ex
        if not isinstance(raw, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in raw.items()):
            raise ValueError(
                f"heading-mapping table for language {language!r} must be a flat JSON object mapping "
                f"translated heading text (str) to canonical English heading text (str)"
            )
        seen_values: dict[str, str] = {}
        for key, value in raw.items():
            if value in seen_values:
                raise ValueError(
                    f"heading-mapping table for language {language!r} is ambiguous: two distinct "
                    f"canonical headings translate to the same string {value!r} ({seen_values[value]!r} and "
                    f"{key!r}) -- values must be pairwise distinct"
                )
            seen_values[value] = key

        _loaded_tables[language] = raw
        return raw


def resolve_heading_table(language: str | None) -> dict[str, str] | None:
    """Return the table a parse of ``language`` applies: ``None`` for omitted/EN, the loaded table otherwise.

    The single entry point the parse boundaries (and the language-aware
    tools' own fail-fast checks) use: an omitted language (``None``) or the
    default language EN (:data:`DEFAULT_LANGUAGE`) resolves to ``None``
    -- no table, the canonical headings are expected as-is, and the parse
    runs byte-identically to today's EN path; any other language resolves
    to its loaded table (raising the loader's actionable
    :class:`ValueError` when the language is shape-valid but has no table
    file).

    Parameters
    ----------
    language:
        The effective language of the parse: the tool's explicit
        ``language`` parameter, or the language a path-based parse derived
        from the document's position (``None`` = flat/default).

    Returns
    -------
    dict[str, str] | None
        The loaded table for a non-default language, or ``None`` when no
        table applies (omitted or default language).

    Raises
    ------
    ValueError
        As :func:`load_heading_table`, for a non-default language without
        a usable table.
    """
    assert language is None or isinstance(language, str), type(language)

    if language is None or language == DEFAULT_LANGUAGE:
        result: dict[str, str] | None = None
        return result
    result = load_heading_table(language)
    return result


def reset_heading_table_cache() -> None:
    """Clear every cached table (test-only hook; not for production use).

    Tests that redirect :func:`heading_table_path` at temporary files --
    or that need a previously-failed language re-tried -- call this in
    ``setUp``/``tearDown`` so a code loaded earlier in the same worker
    process never shadows their fixture (the ``reset_dec_cache`` test-hook
    precedent).
    """
    with _load_lock:
        _loaded_tables.clear()


def iter_heading_lines(text: str) -> Iterator[tuple[int, int, str]]:
    """Yield every ATX heading line of ``text`` that lies outside a fenced code block (feat-197-i18n).

    The single heading/fence recognizer behind both :func:`normalize_heading_lines` (the parse-boundary pre-pass)
    and the translation drift check's heading skeleton (feat-197-i18n Phase 140), so the two can never disagree on
    what a heading is: a line matching ``^#{1,6} `` (1-6 hashes, one space, then non-empty inline text -- the
    mdformat-normalized heading shape) outside a fenced code block, where a ``#``-leading line inside a
    ``` / ~~~ fence is code, not a heading. Fences follow CommonMark: an opener is up to three leading spaces plus
    three or more backticks (info string free of backticks) or three or more tildes; the closer is a line of only
    the same fence character, at least as many as the opener, with at most trailing whitespace.

    Parameters
    ----------
    text:
        The (mdformat-normalized) body text to scan; split on ``"\\n"``.

    Returns
    -------
    Iterator[tuple[int, int, str]]
        ``(line_index, level, heading_text)`` per heading: the 0-based index of the line in ``text.split("\\n")``,
        the heading level (1-6, the number of hashes), and the inline text with surrounding whitespace stripped
        (exactly the string ``match_alias`` sees).
    """
    assert isinstance(text, str), type(text)

    in_fence = False
    fence_char = ""
    fence_length = 0
    for index, line in enumerate(text.split("\n")):
        if in_fence:
            closer = re.match(rf"^ {{0,3}}{re.escape(fence_char)}{{{fence_length},}}[ \t]*$", line)
            if closer is not None:
                in_fence = False
            continue
        fence = _FENCE_OPEN_PATTERN.match(line)
        if fence is not None and not (fence.group(1)[0] == "`" and "`" in fence.group(2)):
            in_fence = True
            fence_char = fence.group(1)[0]
            fence_length = len(fence.group(1))
            continue
        heading = _HEADING_LINE_PATTERN.match(line)
        if heading is not None:
            yield index, len(heading.group(1)), heading.group(2).strip()


def normalize_heading_lines(text: str, table: dict[str, str]) -> str:
    """Rewrite every table-mapped heading line to its canonical text, fence-aware (ADR 38efdb66 item 5).

    The pre-parse heading-normalization pass: for each heading line outside a fenced code block
    (:func:`iter_heading_lines`: ``^#{1,6} ``, the mdformat-normalized heading shape) the line's inline text
    (surrounding whitespace stripped -- exactly what ``match_alias`` sees)
    is looked up as ``normalized = table.get(heading_text, heading_text)``
    and the line rewritten to ``<hashes> <normalized>`` when (and only
    when) it differs. Every other line -- including every line inside a
    ``` / ~~~ fence, where a ``#``-leading line is code, not a heading --
    stays byte-identical, so the pass is a pure no-op for text whose
    headings the table does not map (e.g. canonical EN text through a
    table, or a translation that leaves some heading untranslated by
    design).

    Parameters
    ----------
    text:
        The (mdformat-normalized) body text to normalize.
    table:
        The language's ``<translated> -> <canonical>`` mapping (a non-empty
        table for a non-default language; the pass is a byte-identity no-op
        for an empty one).

    Returns
    -------
    str
        The text with every table-mapped heading line rewritten and every
        other line unchanged (same line count, same join).
    """
    assert isinstance(text, str), type(text)
    assert isinstance(table, dict), type(table)

    lines = text.split("\n")
    for index, level, heading_text in iter_heading_lines(text):
        normalized = table.get(heading_text, heading_text)
        if normalized != heading_text:
            lines[index] = f"{'#' * level} {normalized}"

    result = "\n".join(lines)
    return result
