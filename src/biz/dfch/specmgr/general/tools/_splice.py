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

"""Frontmatter-stripped body extraction, body-line splicing, and body-line
windowing for the generic ``update`` tool (feat-22-consolidate-mutation-tools,
Phase 2) and the ``get_<d>`` tools (feat-28-get-update, Phase 2).

Three small, doc-type-agnostic text helpers shared by the generic ``update``
tool's range mode and the eleven ``get_<d>`` tools' ``raw=True`` reads:

- :func:`body_text` extracts a document file's frontmatter-stripped body text
  using the established ``frontmatter.loads(path.read_text(encoding="utf-8")).
  content`` mechanism -- the same frontmatter-stripping mechanism the
  domain write paths use.
- :func:`splice_body` replaces a body-line range of that text, addressed by
  read-style ``offset``/``limit`` coordinates (``offset`` = 1-based first
  line to replace, ``limit`` = number of lines, omitted = through the last
  body line, ``0`` = pure insert, ``offset = N + 1`` = the virtual
  end-of-body append position), implementing the plan's range contract
  (strict validation, splice-then-validate-whole).
- :func:`window_body` returns the read-style ``offset``/``limit`` window of
  that text (``offset`` = 1-based first line to return, floored to 1;
  ``limit`` = number of lines, omitted = through the last body line, capped
  at the remaining lines), clamping out-of-range values instead of erroring
  (the ``list_<d>`` "clamped, not errored" convention; reads are
  non-destructive).

**The raw/splice invariant.** All three helpers are the *single* definition
of "the body text" in this codebase: every ``get_<d>(raw=True)`` read
(windowed or not) and every ``update`` range splice go through
:func:`body_text`, so *what the client counts is what the server splices* --
the line numbers a client sees in any ``get_<d>(raw=True)`` read, windowed or
not, index byte-for-byte into the same text the server splices against;
:func:`window_body` is the single windowing definition shared by all eleven
``get_<d>`` tools.

As with :mod:`_doc_paths`, this module has no ``mcp`` dependency -- plain
file I/O and text manipulation only, kept separately from any
``@mcp.tool()``-decorated function so it stays independently testable.
"""

from __future__ import annotations

from pathlib import Path

import frontmatter

__all__ = ["body_text", "splice_body", "window_body"]

#: Minimum allowed 1-based body-line coordinate (the first line of the body).
_MIN_LINE = 1


def body_text(path: Path) -> str:
    """Return the frontmatter-stripped body text of the document at ``path``.

    Uses the established ``frontmatter.loads(path.read_text(encoding=
    "utf-8")).content`` mechanism (the same frontmatter-stripping
    mechanism the domain write paths use to re-read the raw body): the
    YAML frontmatter block is
    removed, and the remaining body markdown is returned verbatim -- never
    reformatted, re-rendered, or otherwise touched. The returned text is
    exactly the text whose 1-based lines the generic ``update`` tool's
    ``offset``/``limit`` coordinates address (see the module docstring's
    raw/splice invariant).

    Parameters
    ----------
    path:
        The filesystem path to the document ``.md`` file.

    Returns
    -------
    str
        The body text with the YAML frontmatter block removed, verbatim.

    Raises
    ------
    FileNotFoundError
        The file at ``path`` does not exist.
    ValueError
        The file has no parseable frontmatter delimiters (the
        ``frontmatter`` library raises ``ValueError`` for that shape).
    """
    assert isinstance(path, Path), type(path)

    post = frontmatter.loads(path.read_text(encoding="utf-8"))
    content: str | bytes = post.content
    assert isinstance(content, str), type(content)
    result = content
    return result


def splice_body(current_body: str, offset: int, limit: int | None, content: str) -> str:
    """Replace the body-line range ``offset..offset + limit - 1`` of ``current_body`` with ``content``.

    Implements the generic ``update`` tool's range contract (REQ-002)
    exactly. Let ``N = len(current_body.splitlines())`` be the number of
    lines of the current body; ``N + 1`` is a virtual position past the
    last line (the append position):

    - ``offset = k``, ``limit = 1`` (1 <= k <= N) -> replace line ``k`` only.
    - ``offset = k``, ``limit = m`` (k + m - 1 <= N) -> replace lines ``k..k + m - 1``.
    - ``limit`` omitted -> the range extends through the last line (``k..N``).
    - ``limit = 0`` -> a pure insert of ``content``'s lines before line ``offset``.
    - ``offset = N + 1`` (``limit`` omitted or ``0``) -> the range is empty at
      end-of-body: a pure append of ``content`` after the last line.
    - ``offset = 1``, ``limit`` omitted -> whole-body replace, equivalent to
      the no-range (whole-body) mode with the identical text.
    - Empty ``content`` -> the range is deleted (legal iff the spliced
      result still validates as a whole body).

    The splice drops the range's lines (``limit`` of them, or
    ``N - offset + 1`` when ``limit`` is omitted), inserts
    ``content.splitlines()`` at position ``offset - 1``, and rejoins with
    ``"\\n"`` plus a single trailing ``"\\n"``. Lines outside the range are
    never touched, so unchanged regions of the on-disk body stay
    byte-identical; the caller validates the *spliced result* as a whole
    document before persisting it.

    Parameters
    ----------
    current_body:
        The current frontmatter-stripped body text (e.g. from
        :func:`body_text`).
    offset:
        The 1-based first line of the range to replace; allowed
        ``1..N + 1``, where ``N + 1`` (one past the last body line) is the
        virtual end-of-body position.
    limit:
        The number of lines the range spans (``offset..offset + limit -
        1``); ``0`` is a pure insert, ``None`` (omitted) extends the range
        through the last body line.
    content:
        The replacement fragment; its lines (``content.splitlines()``) take
        the place of the dropped range. Empty string deletes the range.

    Returns
    -------
    str
        The spliced body text (rejoined lines plus a single trailing
        newline).

    Raises
    ------
    ValueError
        Misused coordinates -- ``offset < 1``, ``offset > N + 1``,
        ``limit < 0``, or ``offset + limit - 1 > N`` -- with a message
        naming the offending value(s) and the allowed range. Client-
        controlled input, so these are ``ValueError``s (not ``assert``s),
        per the project's user-controlled-flow-control rule.
    """
    assert isinstance(current_body, str), type(current_body)
    assert isinstance(offset, int), type(offset)
    assert limit is None or isinstance(limit, int), type(limit)
    assert isinstance(content, str), type(content)

    lines = current_body.splitlines()
    n_lines = len(lines)
    max_coordinate = n_lines + _MIN_LINE

    if offset < _MIN_LINE:
        raise ValueError(f"offset must be in {_MIN_LINE}..{max_coordinate}, got {offset}")
    if offset > max_coordinate:
        raise ValueError(
            f"offset must be in {_MIN_LINE}..{max_coordinate} for this {n_lines}-line body "
            f"(N+1 = {max_coordinate} is the virtual end-of-body position), got {offset}"
        )
    if limit is not None and limit < 0:
        raise ValueError(f"limit must be in 0..{n_lines - offset + _MIN_LINE}, got {limit}")
    if limit is not None and offset + limit - _MIN_LINE > n_lines:
        raise ValueError(
            f"offset + limit - 1 must be <= {n_lines} for this {n_lines}-line body, got offset={offset}, limit={limit}"
        )

    drop_count = limit if limit is not None else n_lines - offset + _MIN_LINE
    result_lines = lines[: offset - _MIN_LINE] + content.splitlines() + lines[offset - _MIN_LINE + drop_count :]
    result = "\n".join(result_lines) + "\n"
    return result


def window_body(text: str, offset: int = 1, limit: int | None = None) -> str:
    """Return the body-line window ``offset..offset + limit - 1`` of ``text``.

    The single windowing definition behind every
    ``get_<d>(raw=True, offset=..., limit=...)`` read (REQ-002): a
    read-style, *clamping* (never erroring) window over a
    frontmatter-stripped body text, in the ``list_<d>`` "clamped, not
    errored" paging convention (ADR
    ec9f5262-9912-49d0-903f-fcfb54f28c13) -- reads are non-destructive, so
    out-of-range coordinates degrade to the nearest valid window instead of
    raising. Let ``N = len(text.splitlines())`` be the number of lines of
    ``text``:

    - ``offset`` is floored to 1; a floored ``offset > N`` (including an
      empty ``text``) returns the empty string.
    - ``limit = None`` (omitted) extends the window through the last line;
      any given ``limit`` is capped at the remaining lines (``N - offset +
      1``), and a negative ``limit`` yields an empty window.

    The result is the window's lines, each keeping its trailing newline --
    ``""`` if the window is empty, else ``"\\n".join(lines[offset - 1 :
    offset - 1 + count]) + "\\n"``. Consequently, :func:`window_body` with
    the defaults (``offset = 1``, ``limit = None``) equals a normal
    trailing-newline body byte-for-byte, and concatenating consecutive
    non-overlapping windows reproduces the body -- the raw/splice invariant
    holds for windowed reads exactly as for full raw reads (see the module
    docstring).

    Parameters
    ----------
    text:
        The frontmatter-stripped body text (e.g. from :func:`body_text`).
    offset:
        The 1-based first body line of the window; values below 1 floor to
        1.
    limit:
        The number of body lines the window spans; ``None`` (omitted)
        extends the window through the last line, and the value is capped
        at the remaining lines (a negative value yields an empty window).

    Returns
    -------
    str
        The window's lines joined with ``"\\n"`` plus a single trailing
        newline, or ``""`` for an empty window.
    """
    assert isinstance(text, str), type(text)
    assert isinstance(offset, int), type(offset)
    assert limit is None or isinstance(limit, int), type(limit)

    lines = text.splitlines()
    n_lines = len(lines)
    start = max(_MIN_LINE, offset)
    if start > n_lines:
        result = ""
        return result
    remaining = n_lines - start + _MIN_LINE
    count = remaining if limit is None else max(0, min(limit, remaining))
    if count == 0:
        result = ""
        return result
    result = "\n".join(lines[start - _MIN_LINE : start - _MIN_LINE + count]) + "\n"
    return result
