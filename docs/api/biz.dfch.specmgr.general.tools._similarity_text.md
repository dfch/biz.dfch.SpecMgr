# `biz.dfch.specmgr.general.tools._similarity_text`

Embedding-input text extraction for the similarity engine (feat-134, Phase 2, Task 2.2).

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

## Classes

### `SimilarityText`

One candidate document's embedding input plus its result-row metadata (REQ-005/REQ-009).

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


## Functions

### `_fence_close(line: 'str', fence_char: 'str', fence_length: 'int') -> 'bool'`

Whether ``line`` closes the open ``fence_char`` fence of ``fence_length`` chars.

A CommonMark closing fence: the same character, at least as long as
the opening fence, and nothing but trailing whitespace.


### `_fence_open(line: 'str') -> 'tuple[str, int] | None'`

Whether ``line`` opens a fenced code block: its ``(fence char, fence length)``.

A CommonMark opening fence: 0-3 leading spaces + 3-or-more backticks
or tildes. A backtick fence's info string may not contain backticks
(such a line is paragraph text, not a fence).


### `compose_embedding_text(title: 'str', frontmatter: 'Mapping[str, object]', body: 'str') -> 'str'`

Compose a parseable document's embedding input text (REQ-005).

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


### `failed_similarity_text(raw_text: 'str') -> 'SimilarityText'`

Build the unparseable-document :class:`SimilarityText` (REQ-009).

Embeds the file's full raw text (no frontmatter split, no title
scan) and surfaces the :data:`FAILED_TO_PARSE_MARKER` title/status
with ``id = None`` -- broken artifacts stay discoverable instead of
vanishing from similarity results (the feature README's Decisions
Made).

Args:
    raw_text: The file's full raw text, exactly as read from disk.

Returns:
    The marker :class:`SimilarityText`.


### `first_h1(body: 'str') -> 'str | None'`

Return the body's first level-1 heading's title (ATX or setext), or ``None``.

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

