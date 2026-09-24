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

"""Embedding-input text extraction for the similarity engine (feat-134, Phase 2, Task 2.2).

Backs ADR 750842b2-aca4-4649-ba0c-855ec8e1f505's **embedding input**
sub-decision (REQ-005/REQ-009): the embedding input text for a document
is its title, plus its frontmatter fields excluding the bookkeeping-only
keys :data:`BOOKKEEPING_FRONTMATTER_KEYS`, plus its raw frontmatter-
stripped body text (the same text ``raw=True`` reads already expose).
Across every whole-body domain the only frontmatter field that survives
the exclusion is ``classification`` (free-text, meaningful when present)
-- ``status`` is deliberately part of the exclusion (closed, low-
cardinality lifecycle vocabulary, near-zero semantic signal; see the
feature README's Decisions Made). Unparseable documents (parse failure
of any channel -- the parseability decision itself is made by the
per-domain text parser, in ``_similarity_corpus.candidate_similarity_text``)
degrade to the file's full raw text as the embedding input, and their
result rows carry the :data:`FAILED_TO_PARSE_MARKER` title/status
convention (reused from ``_listing``, not redefined) with ``id = None``
(REQ-009) -- broken artifacts stay discoverable instead of vanishing
from similarity results.

**Domain-agnostic by design.** No per-domain field extraction: the title
is the document's first H1 -- both level-1 heading syntaxes markdown-it
emits as an ``h1`` token, ATX (``# Title``) and setext (``Title`` over a
``=`` underline), scanned off the raw body with fenced-code-block
tracking -- it is also present in the body text, the plan's own
deliberate double weighting of the title signal, no dedup. The frontmatter
mapping is filtered by the shared bookkeeping-key set alone, and the body
is the raw ``python-frontmatter``-split text (base dependency, never a
private tokenizer). A document parsed in another domain's shape but
structurally valid here still extracts identically -- the embedding
input is a text concern, not a model concern.

**No corpus-shape invariant is assumed.** The corpus is *not*
mdformat-normalized: there is no mdformat pre-commit hook, the write
tools persist raw validated bytes, and the hand-edited
``.specmgr/feat`` READMEs sit in the default corpus via
``DEFAULT_FEAT_DIR``. The domain parsers (markdown-it) therefore accept
any CommonMark heading shape in a raw body, and :func:`first_h1`'s own
scan covers exactly that -- both H1 syntaxes, 0-3 leading-space indent,
fenced-code-block tracking (feat-134, Phase 6, Task 6.1).

**Dependency-light.** Standard library + ``python-frontmatter`` (base
dependency) + ``_listing`` (itself dependency-light) only -- no
``fastembed``, no ``numpy``, no ``mcp``: importable on a base/
``mcp``-only install, where the Phase 3 similarity tools register and
return the structured unavailable result (REQ-003) without ever touching
the corpus.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

from ._listing import FAILED_TO_PARSE_MARKER

__all__ = [
    "BOOKKEEPING_FRONTMATTER_KEYS",
    "SimilarityText",
    "compose_embedding_text",
    "failed_similarity_text",
    "first_h1",
]

#: The frontmatter keys excluded from the embedding input (ADR
#: 750842b2, **embedding input** sub-decision; REQ-005): bookkeeping
#: metadata with no semantic similarity signal. ``status`` is part of
#: this exclusion by an explicit decision (the feature README's
#: Decisions Made -- closed, low-cardinality lifecycle vocabulary,
#: near-zero signal), not an oversight. Across every whole-body domain
#: the only frontmatter field that survives the exclusion is
#: ``classification``.
BOOKKEEPING_FRONTMATTER_KEYS: frozenset[str] = frozenset({"id", "type", "version", "created", "updated", "status"})

#: A level-1 ATX heading: 0-3 leading spaces (CommonMark's indent
#: tolerance -- a heading indented by 4 or more is code, not a heading),
#: ``#`` + one or more spaces/tabs + a non-empty title. A level-2 line
#: (``## ...``) never matches -- its second character is ``#``, not
#: whitespace. The corpus is NOT mdformat-normalized (see the module
#: docstring), so the indent tolerance is load-bearing: markdown-it
#: accepts indented headings in a raw body.
_H1_ATX_PATTERN = re.compile(r"^ {0,3}#[ \t]+(.+?)[ \t]*$")

#: An ATX heading of *any* level (1-6 ``#``s, then a space/tab or end of
#: line -- ``#`` alone is an empty heading, ``#x`` and seven-or-more
#: ``#``s are paragraph text). Used only to recognize level-2+ lines as
#: leaf blocks that end a paragraph, so they can never be a setext title
#: line; :data:`_H1_ATX_PATTERN` does the actual H1 return.
_ATX_HEADING_PATTERN = re.compile(r"^ {0,3}#{1,6}(?:[ \t].*)?$")

#: A setext level-1 underline: 0-3 leading spaces, one or more ``=`` and
#: nothing but trailing whitespace. A ``-`` underline is a setext
#: level-2 heading and never matches here.
_SETEXT_H1_PATTERN = re.compile(r"^ {0,3}=+[ \t]*$")

#: A setext level-2 underline (the ``-`` twin of
#: :data:`_SETEXT_H1_PATTERN`): a leaf block that ends a paragraph, so it
#: can never be a setext title line either.
_SETEXT_H2_PATTERN = re.compile(r"^ {0,3}-+[ \t]*$")

#: A fenced code block line: 0-3 leading spaces + 3-or-more backticks or
#: tildes (CommonMark), plus the line's remainder (an info string on an
#: opening fence, nothing on a closing one). :func:`first_h1` tracks
#: fences so a ``# ...``/``===`` line inside one is never a title -- the
#: corpus is raw, and a code sample showing a heading is a natural
#: corpus shape (feat-134, Phase 6, Task 6.1).
_FENCE_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*(.*)$")


@dataclass(frozen=True)
class SimilarityText:
    """One candidate document's embedding input plus its result-row metadata (REQ-005/REQ-009).

    The unit the Phase 3 similarity tools build a result row from: the
    exact text handed to the provider's ``embed`` on a cache miss, plus
    the ``(id, title, status)`` triple the ranked hit carries (the hit
    shape's own fields -- ACC-001/ACC-002).

    Attributes:
        embedding_text:
            The exact text the embedding provider's ``embed`` receives
            for this document: title + surviving (non-bookkeeping,
            non-``None``) frontmatter fields + raw frontmatter-stripped
            body for a parseable document -- or the file's full raw text
            for an unparseable one (REQ-009).
        title:
            The document's first H1 (deliberately double-weighted -- it
            is also present inside ``embedding_text``'s body part, no
            dedup) -- or :data:`FAILED_TO_PARSE_MARKER` for an
            unparseable document.
        id_:
            The validated document id -- ``None`` for an unparseable
            document (REQ-009's marker rows are not addressable).
        status:
            The validated document status (the domain's own default
            applied for a blank/absent key, exactly what
            ``list_<domain>`` surfaces) -- or
            :data:`FAILED_TO_PARSE_MARKER` for an unparseable document.
    """

    embedding_text: str
    title: str
    id_: str | None
    status: str


def _fence_open(line: str) -> tuple[str, int] | None:
    """Whether ``line`` opens a fenced code block: its ``(fence char, fence length)``.

    A CommonMark opening fence: 0-3 leading spaces + 3-or-more backticks
    or tildes. A backtick fence's info string may not contain backticks
    (such a line is paragraph text, not a fence).
    """
    match = _FENCE_PATTERN.match(line)
    if match is None:
        result: tuple[str, int] | None = None
        return result
    marker = match.group(1)
    if marker.startswith("`") and "`" in match.group(2):
        result = None
        return result
    result = (marker[0], len(marker))
    return result


def _fence_close(line: str, fence_char: str, fence_length: int) -> bool:
    """Whether ``line`` closes the open ``fence_char`` fence of ``fence_length`` chars.

    A CommonMark closing fence: the same character, at least as long as
    the opening fence, and nothing but trailing whitespace.
    """
    match = _FENCE_PATTERN.match(line)
    if match is None:
        return False
    marker = match.group(1)
    result = marker[0] == fence_char and len(marker) >= fence_length and not match.group(2)
    return result


def first_h1(body: str) -> str | None:
    """Return the body's first level-1 heading's title (ATX or setext), or ``None``.

    A plain line scan (no markdown parsing) covering **both** level-1
    heading syntaxes markdown-it emits as an ``h1`` token -- so the scan
    can never miss the mandatory H1 of a parsed document (the
    ``_similarity_corpus.candidate_similarity_text`` invariant):

    - **ATX** -- :data:`_H1_ATX_PATTERN`: 0-3 leading spaces
      (CommonMark's indent tolerance) + ``#`` + a non-empty title.
    - **setext** -- a :data:`_SETEXT_H1_PATTERN` underline (0-3 leading
      spaces + ``=``s) immediately under a non-empty paragraph; the
      title is the stripped paragraph line(s) above it, joined with
      single spaces (a multi-line setext paragraph renders as one line
      of inline content, soft breaks included).

    Fence-aware: a fenced code block (``` / ~~~, 3-or-more chars, the
    closing fence the same character at least as long) is tracked, and a
    ``# ...``/``===`` line inside one is never a title. Leaf blocks that
    end a paragraph -- ATX headings of level 2-6 and setext level-2
    (``-``) underlines -- are recognized so they can never be a setext
    title line. The corpus is NOT mdformat-normalized (see the module
    docstring: no such pre-commit hook, the write tools persist raw
    validated bytes, and the hand-edited ``.specmgr/feat`` READMEs sit
    in the default corpus), so any raw CommonMark shape can appear.

    Args:
        body: The raw frontmatter-stripped body text.

    Returns:
        The first H1's title (the heading text, no ``#`` marker and no
        setext underline), or ``None`` when the body carries no level-1
        heading at all.
    """
    assert isinstance(body, str), type(body)

    paragraph: list[str] = []
    fence_char: str | None = None
    fence_length = 0

    for line in body.splitlines():
        if fence_char is not None:
            if _fence_close(line, fence_char, fence_length):
                fence_char = None
                paragraph = []
            continue

        opened = _fence_open(line)
        if opened is not None:
            fence_char, fence_length = opened
            paragraph = []
            continue

        if not line.strip():
            paragraph = []
            continue

        if _SETEXT_H1_PATTERN.match(line) is not None:
            if paragraph:
                result = " ".join(part.strip() for part in paragraph)
                return result
            paragraph.append(line)  # no paragraph above: plain paragraph text
            continue

        match = _H1_ATX_PATTERN.match(line)
        if match is not None:
            result = match.group(1)
            return result

        if _ATX_HEADING_PATTERN.match(line) is not None:
            paragraph = []  # an ATX heading of level 2-6 is a leaf block
            continue

        if _SETEXT_H2_PATTERN.match(line) is not None:
            paragraph = []  # a setext level-2 heading is a leaf block
            continue

        paragraph.append(line)

    result = None
    return result


def compose_embedding_text(title: str, frontmatter: Mapping[str, object], body: str) -> str:
    """Compose a parseable document's embedding input text (REQ-005).

    The ``title``, then one ``key: value`` line per surviving frontmatter
    field (a key not in :data:`BOOKKEEPING_FRONTMATTER_KEYS` with a
    non-``None`` value, in the mapping's own order), then the raw
    frontmatter-stripped ``body`` -- joined with single newlines. The
    title is deliberately not deduplicated against its occurrence inside
    ``body`` (the plan's own Design Notes: the deliberate double
    weighting of the title signal).

    Args:
        title: The document's first H1 title (see :func:`first_h1`).
        frontmatter: The document's frontmatter mapping -- the full,
            unfiltered one (a validated model's ``model_dump()`` in
            practice); the bookkeeping keys and ``None`` values are
            filtered here.
        body: The raw frontmatter-stripped body text.

    Returns:
        The composed embedding input text.
    """
    assert isinstance(title, str), type(title)
    assert isinstance(frontmatter, Mapping), type(frontmatter)
    assert isinstance(body, str), type(body)

    lines: list[str] = [title]
    for key, value in frontmatter.items():
        if key in BOOKKEEPING_FRONTMATTER_KEYS or value is None:
            continue
        lines.append(f"{key}: {value}")
    lines.append(body)
    result = "\n".join(lines)
    return result


def failed_similarity_text(raw_text: str) -> SimilarityText:
    """Build the unparseable-document :class:`SimilarityText` (REQ-009).

    Embeds the file's full raw text (no frontmatter split, no title
    scan) and surfaces the :data:`FAILED_TO_PARSE_MARKER` title/status
    with ``id = None`` -- broken artifacts stay discoverable instead of
    vanishing from similarity results (the feature README's Decisions
    Made).

    Args:
        raw_text: The file's full raw text, exactly as read from disk.

    Returns:
        The marker :class:`SimilarityText`.
    """
    assert isinstance(raw_text, str), type(raw_text)

    result = SimilarityText(
        embedding_text=raw_text,
        title=FAILED_TO_PARSE_MARKER,
        id_=None,
        status=FAILED_TO_PARSE_MARKER,
    )
    return result
