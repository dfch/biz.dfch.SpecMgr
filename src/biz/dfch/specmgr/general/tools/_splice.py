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

Small, doc-type-agnostic helpers shared by the generic ``update`` tool's
range mode and every ``get_<d>`` tool's ``raw=True`` reads (and the
``get_<d>`` tools' own read-argument validation):

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
  non-destructive). With ``numbered=True``, each returned line is
  additionally prefixed with its 1-based **absolute** body-line number
  (numbering starts at the clamped offset and never restarts at 1 within a
  window, so a number seen in a numbered read can be fed straight back into
  the generic ``update`` tool's ``offset``; feat-153-off-by-n Phase 3,
  REQ-004, ADR 19ff316b-cd11-41a7-a616-ffd84917da51's Decision Outcome item
  6).
- :func:`splice_snippet` renders the before/after window of a range-mode
  splice (the dropped lines, the inserted lines, and up to 2 unchanged
  context lines per side, each labeled with its 1-based body-line number per
  the pre-splice/post-splice split) as the ``snippet`` string the generic
  ``update`` tool returns on success in range mode (feat-153-off-by-n
  Phase 2, REQ-002, ADR 19ff316b-cd11-41a7-a616-ffd84917da51).
- :func:`validate_read_args` raises ``ValueError`` for the ``get_<d>``
  read-argument misuses -- the ``offset``/``limit`` windowing coordinates or
  ``numbered=True`` combined with ``raw=False`` -- the single shared guard
  behind all 12 ``get_<d>`` tools, which the caller runs before any file
  access (feat-153-off-by-n Phase 3, REQ-005).

**The raw/splice invariant.** The text helpers (:func:`body_text`,
:func:`splice_body`, and :func:`window_body`) are the *single* definition of
"the body text" in this codebase: every ``get_<d>(raw=True)`` read (windowed
or not) and every ``update`` range splice go through :func:`body_text`, so
*what the client counts is what the server splices* -- the line numbers a
client sees in any ``get_<d>(raw=True)`` read, windowed or not, index
byte-for-byte into the same text the server splices against;
:func:`window_body` is the single windowing definition shared by every
``get_<d>`` tool (its ``numbered`` argument only prefixes the window's lines
with their absolute body-line numbers -- the unnumbered output is unchanged,
and the splice coordinates keep addressing the *unprefixed* line count).
:func:`splice_snippet` is the single snippet definition
shared by the generic ``update`` tool's dispatcher (it consumes, never
defines, the body text).

As with :mod:`_doc_paths`, this module has no ``mcp`` dependency -- plain
file I/O, text manipulation, and argument validation only, kept separately
from any ``@mcp.tool()``-decorated function so it stays independently
testable.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import frontmatter

__all__ = ["body_text", "splice_body", "splice_snippet", "validate_read_args", "window_body"]

#: Minimum allowed 1-based body-line coordinate (the first line of the body).
_MIN_LINE = 1

#: The number of unchanged context lines the :func:`splice_snippet` window
#: carries on each side of the touched range (fixed at 2, not configurable --
#: feat-153-off-by-n's Explicitly Out Of Scope).
_CONTEXT_LINES = 2


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


def window_body(text: str, offset: int = 1, limit: int | None = None, numbered: bool = False) -> str:
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
    - With ``numbered=True`` (feat-153-off-by-n Phase 3, REQ-004, ACC-011;
      ADR 19ff316b-cd11-41a7-a616-ffd84917da51's Decision Outcome item 6),
      each returned line is additionally prefixed with its 1-based
      **absolute** body-line number in the ``f"{n}: {text}"`` form (plain
      decimal, no padding; the line text verbatim, so an empty body line
      renders as ``"<n>: "`` with the separator's trailing space):
      numbering starts at the clamped ``offset`` (``max(1, offset)``) and
      increments by 1 per line -- never a per-window restart at 1 -- so a
      number seen in a numbered, windowed read can be fed straight back
      into the generic ``update`` tool's ``offset``. Non-empty numbered
      output ends with exactly one trailing ``"\\n"`` regardless of whether
      ``text`` had one (so a ``numbered=True`` no-window read and a
      ``numbered=True`` whole-body-equivalent windowed read of the same
      body are byte-identical); an empty window (or empty ``text``)
      returns ``""`` as for the unnumbered case.

    The unnumbered result is the window's lines, each keeping its trailing
    newline -- ``""`` if the window is empty, else ``"\\n".join(lines[
    offset - 1 : offset - 1 + count]) + "\\n"``. Consequently,
    :func:`window_body` with the defaults (``offset = 1``, ``limit = None``)
    equals a normal trailing-newline body byte-for-byte, and concatenating
    consecutive non-overlapping windows reproduces the body -- the
    raw/splice invariant holds for windowed reads exactly as for full raw
    reads (see the module docstring). ``numbered=False`` (the default) is
    byte-identical to that current behavior, including for a ``text``
    without a trailing newline.

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
    numbered:
        When ``True``, prefix each returned line with its 1-based absolute
        body-line number (see the third bullet above); ``False`` (the
        default) returns the plain window.

    Returns
    -------
    str
        The window's lines joined with ``"\\n"`` plus a single trailing
        newline, or ``""`` for an empty window.
    """
    assert isinstance(text, str), type(text)
    assert isinstance(offset, int), type(offset)
    assert limit is None or isinstance(limit, int), type(limit)
    assert isinstance(numbered, bool), type(numbered)

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
    window = lines[start - _MIN_LINE : start - _MIN_LINE + count]
    if numbered:
        numbered_lines = [f"{start + i}: {line}" for i, line in enumerate(window)]
        result = "\n".join(numbered_lines) + "\n"
    else:
        result = "\n".join(window) + "\n"
    return result


def validate_read_args(raw: bool, offset: int | None, limit: int | None, numbered: bool) -> None:
    """Reject ``get_<d>`` read-argument misuses before any file access.

    The single shared guard behind every ``get_<d>`` tool (feat-153-off-by-n
    Phase 3, REQ-005, ACC-005) for the read-surface argument rules that were
    formerly hand-duplicated inline in each of the 12 ``get_<d>.py`` files:
    a parsed-document read (``raw=False``) requires the whole body, so the
    raw-read-only arguments -- the ``offset``/``limit`` windowing
    coordinates and ``numbered=True`` -- are misuses of the read surface
    when combined with it. Client-controlled input, so these are
    ``ValueError``s (not ``assert``s), per the project's
    user-controlled-flow-control rule. The caller runs this guard after its
    own ``validate_id`` and before the ``load_by_id`` attempt and the
    post-feat-150 parse-failure channel, so a misused argument reports
    ``ValueError`` even for a document that fails to parse (REQ-005).

    Parameters
    ----------
    raw:
        The tool's ``raw`` argument (``False`` = parsed document,
        ``True`` = frontmatter-stripped body text).
    offset:
        The tool's ``offset`` argument (``None`` = not given).
    limit:
        The tool's ``limit`` argument (``None`` = not given).
    numbered:
        The tool's ``numbered`` argument (``False`` = unnumbered body
        text, the default; ``True`` = line-numbered).

    Raises
    ------
    ValueError
        ``raw`` is ``False`` and ``offset`` or ``limit`` is given (the
        message is byte-identical to the one each ``get_<d>`` raised
        inline before this factorization), or ``raw`` is ``False`` and
        ``numbered`` is ``True``; the ``numbered`` message mirrors the
        ``offset``/``limit`` one and names the offending value.
    """
    assert isinstance(raw, bool), type(raw)
    assert offset is None or isinstance(offset, int), type(offset)
    assert limit is None or isinstance(limit, int), type(limit)
    assert isinstance(numbered, bool), type(numbered)

    if not raw and (offset is not None or limit is not None):
        raise ValueError(f"offset/limit are only valid with raw=True, got offset={offset!r}, limit={limit!r}")
    if not raw and numbered:
        raise ValueError(f"numbered is only valid with raw=True, got numbered={numbered!r}")


def splice_snippet(pre_body: str, post_body: str, offset: int, limit: int | None) -> str:
    """Render the before/after snippet of the range-mode splice of ``pre_body`` at
    ``offset``/``limit`` into ``post_body``.

    The single snippet definition behind the generic ``update`` tool's
    ``UpdateResult.snippet`` (feat-153-off-by-n Phase 2, REQ-002, ADR
    19ff316b-cd11-41a7-a616-ffd84917da51's Decision Outcome items 2/3/4):
    given the pre-splice body, the post-splice body (the result of splicing
    ``pre_body`` at these same coordinates via :func:`splice_body`), and the
    ``offset``/``limit`` coordinates, returns the touched range's before/after
    window -- the dropped lines, the inserted lines, and up to
    :data:`_CONTEXT_LINES` unchanged context lines immediately above and below
    the touched range in the *post-splice* body, clamped at the body's
    start/end (clamped, never errored, mirroring :func:`window_body`) --
    rendered as the ADR's exact snippet line format:

    - Each snippet line is ``<marker> <n>: <line text>``: ``<marker>`` is
      exactly one character -- ``-`` for a dropped line, ``+`` for an
      inserted line, a single space for a context line; ``<n>`` is the plain
      decimal line number (no zero padding, no fixed-width alignment); the
      separator is exactly ``": "``; ``<line text>`` is the line's verbatim
      text, so an empty body line renders as ``<marker> <n>: `` with a
      trailing space (no empty-line special case).
    - Dropped lines are labeled with their **pre-splice** 1-based body-line
      numbers (``offset..offset + drop_count - 1``; they no longer exist
      afterward, so no post-splice number applies to them); inserted lines
      (``offset..offset + insert_count - 1``) and context lines are labeled
      with their **post-splice** numbers. The two numbering sequences are
      independent and need not be contiguous or to overlap when the
      replacement changes the line count -- expected, not a defect.
    - Line order: context-above, dropped, inserted, context-below.
    - The snippet text is its lines joined with ``"\\n"`` plus a single
      trailing ``"\\n"``, or ``""`` when it contains no lines at all (only a
      no-op splice on an empty body).
    - The window is bounded by the touched range, not the document size:
      at most ``drop_count`` + ``insert_count`` + ``2 * _CONTEXT_LINES``
      lines, no hard cap and no elision markers.

    Equivalent view (the format family shared with the ``get_<d>`` numbered
    read): every snippet line is a 2-character marker prefix (``"- "``/
    ``"+ "``/``"  "``) prepended to exactly the line a
    ``get_<d>(raw=True, numbered=True)`` read prints for that number.

    Doc-type-agnostic like its neighbors: no I/O, no schema knowledge -- the
    generic ``update`` tool's shared dispatcher computes the snippet once per
    call from the adapter's pre/post bodies and coordinates, never
    duplicating it into the per-domain adapters.

    Parameters
    ----------
    pre_body:
        The frontmatter-stripped body text as it existed before the splice
        (e.g. from :func:`body_text`).
    post_body:
        The frontmatter-stripped body text after the splice -- the result of
        splicing ``pre_body`` at these same ``offset``/``limit`` coordinates
        via :func:`splice_body`.
    offset:
        The 1-based first line of the spliced range; must satisfy
        :func:`splice_body`'s own coordinate contract (``1..N + 1``, where
        ``N + 1`` is the virtual end-of-body position) -- the caller enforces
        it, since the dispatcher only ever hands the helper coordinates
        ``splice_body`` already accepted.
    limit:
        The number of lines the spliced range spans; must satisfy
        :func:`splice_body`'s own contract (``0`` = pure insert,
        ``None`` (omitted) = through the last body line) -- enforced by the
        caller as for ``offset``.

    Returns
    -------
    str
        The rendered snippet (see the class of behavior above), or ``""``
        when the window contains no lines at all.

    Raises
    ------
    AssertionError
        The inputs violate the helper's invariants (non-string bodies,
        non-integer coordinates, or coordinates outside :func:`splice_body`'s
        own contract) -- program-invariant failures only, never
        user-controlled flow control.
    """
    assert isinstance(pre_body, str), type(pre_body)
    assert isinstance(post_body, str), type(post_body)
    assert isinstance(offset, int), type(offset)
    assert limit is None or isinstance(limit, int), type(limit)

    pre_lines = pre_body.splitlines()
    post_lines = post_body.splitlines()
    n_pre = len(pre_lines)

    # The same coordinate contract as `splice_body` (which the caller ran
    # first on these exact coordinates -- invariants, not flow control).
    assert _MIN_LINE <= offset <= n_pre + _MIN_LINE, (offset, n_pre)
    assert limit is None or limit >= 0, limit
    assert limit is None or offset + limit - _MIN_LINE <= n_pre, (offset, limit, n_pre)

    drop_count = limit if limit is not None else n_pre - offset + _MIN_LINE
    insert_count = len(post_lines) - n_pre + drop_count
    assert insert_count >= 0, (offset, limit, n_pre, len(post_lines))

    range_start = offset - _MIN_LINE
    dropped_lines = pre_lines[range_start : range_start + drop_count]
    inserted_lines = post_lines[range_start : range_start + insert_count]
    above_start = max(0, range_start - _CONTEXT_LINES)
    context_above = post_lines[above_start:range_start]
    below_start = range_start + insert_count
    context_below = post_lines[below_start : below_start + _CONTEXT_LINES]

    def _numbered(marker: str, numbers: Iterable[int], lines: list[str]) -> list[str]:
        result = [f"{marker} {number}: {line}" for number, line in zip(numbers, lines, strict=True)]
        return result

    snippet_lines = (
        _numbered(" ", range(above_start + _MIN_LINE, range_start + _MIN_LINE), context_above)
        + _numbered("-", range(offset, offset + drop_count), dropped_lines)
        + _numbered("+", range(offset, offset + insert_count), inserted_lines)
        + _numbered(" ", range(below_start + _MIN_LINE, below_start + _MIN_LINE + len(context_below)), context_below)
    )
    if not snippet_lines:
        result = ""
    else:
        result = "\n".join(snippet_lines) + "\n"
    return result
