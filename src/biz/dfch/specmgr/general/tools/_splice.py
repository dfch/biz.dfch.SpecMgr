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

"""Frontmatter-stripped body extraction and body-line splicing for the generic
``update`` tool (feat-22-consolidate-mutation-tools, Phase 2).

Two small, doc-type-agnostic text helpers shared by the generic ``update``
tool's range mode and the seven ``get_<d>`` tools' ``raw=True`` reads:

- :func:`body_text` extracts a document file's frontmatter-stripped body text
  using the established ``frontmatter.loads(path.read_text(encoding="utf-8")).
  content`` mechanism -- the same one every ``set_status_<d>`` tool uses.
- :func:`splice_body` replaces a 1-based, inclusive body-line range of that
  text with a replacement fragment, implementing the plan's range contract
  (the ``N+1`` end-of-body sentinel, splice-then-validate-whole).

**The raw/splice invariant.** Both helpers are the *single* definition of
"the body text" in this codebase: every ``get_<d>(raw=True)`` read and every
``update`` range splice go through :func:`body_text`, so *what the client
counts is what the server splices* -- the line numbers a client sees in a raw
read index byte-for-byte into the same text the server splices against.

As with :mod:`_doc_paths`, this module has no ``mcp`` dependency -- plain
file I/O and text manipulation only, kept separately from any
``@mcp.tool()``-decorated function so it stays independently testable.
"""

from __future__ import annotations

from pathlib import Path

import frontmatter

__all__ = ["body_text", "splice_body"]

#: Minimum allowed 1-based body-line coordinate (the first line of the body).
_MIN_LINE = 1


def body_text(path: Path) -> str:
    """Return the frontmatter-stripped body text of the document at ``path``.

    Uses the established ``frontmatter.loads(path.read_text(encoding=
    "utf-8")).content`` mechanism (the same one every ``set_status_<d>``
    tool uses to re-read the raw body): the YAML frontmatter block is
    removed, and the remaining body markdown is returned verbatim -- never
    reformatted, re-rendered, or otherwise touched. The returned text is
    exactly the text whose 1-based lines the generic ``update`` tool's
    ``begin``/``end`` coordinates address (see the module docstring's
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


def splice_body(current_body: str, begin: int, end: int, content: str) -> str:
    """Replace the 1-based, inclusive body-line range ``begin..end`` of ``current_body`` with ``content``.

    Implements the generic ``update`` tool's range contract (REQ-002)
    exactly. Let ``N = len(current_body.splitlines())`` be the number of
    lines of the current body; ``N + 1`` is a virtual position past the
    last line:

    - ``begin = end = k`` (1 <= k <= N) -> replace line ``k`` only.
    - ``begin = k``, ``end = m`` (k <= m <= N) -> replace lines ``k..m``.
    - ``end = N + 1`` -> the range extends through the last line (``k..N``).
    - ``begin = end = N + 1`` -> the range is empty at end-of-body: a pure
      append of ``content`` after the last line.
    - ``begin = 1``, ``end = N`` -> whole-body replace, equivalent to the
      no-range (whole-body) mode with the identical text.
    - Empty ``content`` -> the range is deleted (legal iff the spliced
      result still validates as a whole body).

    The splice drops lines ``begin..min(end, N)``, inserts
    ``content.splitlines()`` at position ``begin - 1``, and rejoins with
    ``"\\n"`` plus a single trailing ``"\\n"``. Lines outside the range are
    never touched, so unchanged regions of the on-disk body stay
    byte-identical; the caller validates the *spliced result* as a whole
    document before persisting it.

    Parameters
    ----------
    current_body:
        The current frontmatter-stripped body text (e.g. from
        :func:`body_text`).
    begin:
        The 1-based first line of the range to replace.
    end:
        The 1-based last line of the range to replace (inclusive); may be
        ``N + 1`` to extend the range through (or past, i.e. append after)
        the last line.
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
        Misused coordinates -- ``begin < 1``, ``begin > end``, or
        ``end > N + 1`` -- with a message naming the offending value(s)
        and the allowed range. Client-controlled input, so this is a
        ``ValueError`` (not an ``assert``), per the project's
        user-controlled-flow-control rule.
    """
    assert isinstance(current_body, str), type(current_body)
    assert isinstance(begin, int), type(begin)
    assert isinstance(end, int), type(end)
    assert isinstance(content, str), type(content)

    lines = current_body.splitlines()
    n_lines = len(lines)
    max_coordinate = n_lines + _MIN_LINE

    if begin < _MIN_LINE:
        raise ValueError(f"begin must be in {_MIN_LINE}..{max_coordinate}, got {begin}")
    if begin > end:
        raise ValueError(f"begin must be <= end, got begin={begin} > end={end}")
    if end > max_coordinate:
        raise ValueError(
            f"end must be in {_MIN_LINE}..{max_coordinate} for this {n_lines}-line body "
            f"(N+1 = {max_coordinate} is the end-of-body sentinel), got {end}"
        )

    drop_end = min(end, n_lines)
    result_lines = lines[: begin - _MIN_LINE] + content.splitlines() + lines[drop_end:]
    result = "\n".join(result_lines) + "\n"
    return result
