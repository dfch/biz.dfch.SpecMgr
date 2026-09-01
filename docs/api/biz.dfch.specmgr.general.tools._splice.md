# `biz.dfch.specmgr.general.tools._splice`

Frontmatter-stripped body extraction and body-line splicing for the generic
``update`` tool (feat-22-consolidate-mutation-tools, Phase 2).

Two small, doc-type-agnostic text helpers shared by the generic ``update``
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


### `splice_body(current_body: 'str', offset: 'int', limit: 'int | None', content: 'str') -> 'str'`

Replace the body-line range ``offset..offset + limit - 1`` of ``current_body`` with ``content``.

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
``"\n"`` plus a single trailing ``"\n"``. Lines outside the range are
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

