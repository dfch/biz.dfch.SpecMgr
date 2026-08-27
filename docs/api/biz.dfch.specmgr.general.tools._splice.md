# `biz.dfch.specmgr.general.tools._splice`

Frontmatter-stripped body extraction and body-line splicing for the generic
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

## Functions

### `body_text(path: 'Path') -> 'str'`

Return the frontmatter-stripped body text of the document at ``path``.

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


### `splice_body(current_body: 'str', begin: 'int', end: 'int', content: 'str') -> 'str'`

Replace the 1-based, inclusive body-line range ``begin..end`` of ``current_body`` with ``content``.

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
``"\n"`` plus a single trailing ``"\n"``. Lines outside the range are
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

