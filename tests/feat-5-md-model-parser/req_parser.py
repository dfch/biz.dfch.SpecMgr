# Use ONLY this file as a reference: "tests/feat-3-md-str-constraints/uc_example.md"
#
# ============================================================================
# CONTINUATION NOTES (2026-08-08) -- read this first in a new session.
# ============================================================================
#
# This file is a design SKETCH (not runnable, not tested) for a generic
# heading-mapped Markdown-to-Pydantic document parser. The design decisions
# below are captured in full in ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae
# ("Generic heading-mapped markdown-to-Pydantic parsing with declarative
# Heading metadata and opt-in constraints", version 1.1.0 as of this note)
# and tracked in .specmgr/feat/feat-5-md-model-parser/README.md (GitHub
# issue #5). Read the ADR for full rationale; this comment is a short
# pointer + open-items list so a fresh session can resume without re-reading
# the whole chat history.
#
# DECIDED (already reflected in the code below):
# - Heading level (h1..h6) is encoded structurally via a MarkdownHeading1..
#   MarkdownHeading6 base-class hierarchy, not via Annotated field metadata.
#   Each MarkdownHeadingN has a default model_validator asserting no nested
#   heading_open token at-or-above its own level appears in self._tokens[3:]
#   (self._tokens[0:3] is this instance's OWN heading_open/inline/
#   heading_close triple -- see next point).
# - Every heading-bearing instance stores its OWN heading triple as the
#   first 3 entries of _tokens, followed by all nested content up to (not
#   including) the next same-or-shallower-level heading. str()/__repr__
#   therefore just replay _tokens through the renderer -- NO separate
#   metadata-driven heading synthesis ("outer + result" is gone). This is
#   what makes inline formatting inside a heading (**bold**, *emph*)
#   round-trip correctly for free, for every class uniformly, including
#   Title.
# - `alias` is a CLASS-LEVEL property (see CharacteristicInformation's
#   `# @some_annotation(alias=...)` comment -- still a placeholder, not a
#   real decorator/attribute yet) used ONLY for parse-time identity
#   matching, never for rendering. When absent, it should default to a
#   Title-Case derivation of the class name (not yet implemented anywhere
#   in this file).
# - Alias matching must compare against the heading's PLAIN TEXT: walk the
#   heading's `inline` token's `.children` and concatenate only `text`-type
#   children, ignoring formatting tokens (strong_open/strong_close/
#   em_open/em_close/...). This is NOT the same as inline_token.content.
#   See the parsing-strategy section below for why this matters.
# - `Title(MarkdownHeading1)` is a distinct leaf type for the document's own
#   H1: it is DATA (varies per document instance, e.g. "Buy Goods"), not a
#   fixed schema label like the ## / ### section headings, so it has no
#   alias -- there is exactly one H1 per document, no disambiguation needed.
#
# PARSING STRATEGY (agreed, NOT YET IMPLEMENTED as code in this file):
# Sequential, cursor-based recursive-descent walk over a model's fields in
# Pydantic declaration order (Model.model_fields is an ordinary dict and
# preserves declaration order, including inherited fields -- pinned down by
# tests/feat-5-md-model-parser/test_field_declaration_order.py, no need to
# re-derive this).
#   1. cursor = start of this model's own token span (right after its own
#      heading triple, if it has one).
#   2. For each field, in declaration order:
#      a. Determine expected (tag, alias) from the field's annotated type.
#      b. If the heading at `cursor` matches (tag, alias): consume that
#         field's full span (its own heading triple + everything up to the
#         next same-or-shallower-level heading), recursively construct the
#         field's type from that span using this SAME algorithm one heading
#         level deeper, and advance `cursor` past the consumed span.
#      c. If it does NOT match:
#         - Optional (`X | None`) field -> assign None, do NOT advance
#           cursor (retry the same cursor position against the NEXT field).
#         - Required field -> raise an explicit parse error (never guess /
#           never silently proceed).
#   3. COMPLETENESS CHECK (not optional -- this is the safety net that makes
#      "match by (tag, alias)" actually safe): after all fields have been
#      walked, assert `cursor` has reached the end of this model's own span.
#      Any leftover unconsumed heading means either an out-of-declared-order
#      section or a section with no matching field at all -- this MUST be a
#      parse error, not silently dropped. Without this check, an
#      out-of-order optional section would silently vanish instead of
#      erroring, reintroducing the exact "silent misassignment" failure mode
#      that (tag, alias) matching was chosen to avoid over pure positional
#      matching.
#
# PROTOTYPED SINCE THIS NOTE (2026-08-08, later same day) -- standalone spike
# tests, NOT wired into this file's classes/functions yet. Committed under
# tests/feat-5-md-model-parser/ (that feature's own test folder, kept
# separate from this file's location) as throwaway-style proofs of specific
# mechanisms ahead of the real Phase 1 implementation:
# - `get_section(token, tokens)` (test_annotations.py) -- slices a heading's
#   own span out of a flat token list, terminating at the next
#   same-or-shallower-level heading (not just an exact tag match; an h1
#   correctly terminates a preceding h2's section). This is exactly the span
#   definition PARSING STRATEGY step 2b needs and is now proven correct in
#   isolation, but is not yet used by MarkdownHeadingN/parse_document here.
# - `walk_token_tree(tokens)` (test_annotations.py) -- depth-first walk
#   descending into `inline` tokens' `.children`. A necessary building block
#   for the still-NOT-implemented alias plain-text extraction (it visits
#   every child token, including formatting ones; a caller must still filter
#   to `type == "text"` to get plain text -- that filtering step itself is
#   not written yet).
# - `model_fields` declaration-order preservation (including inherited
#   fields), used by the PARSING STRATEGY above, is now a committed test
#   (test_field_declaration_order.py) instead of only an ad hoc chat check.
# - `walk_attributes(cls)` (test_walk_attributes.py) -- generalizes the same
#   declaration-order guarantee to plain (non-BaseModel) classes, for if a
#   future need arises to walk something other than a Pydantic model.
#
# OPEN ITEMS / NOT YET DONE:
# - No real `@some_annotation(...)` decorator/class-attribute exists yet --
#   still just comments. Needs an actual implementation (plain class
#   attribute, e.g. `_alias: ClassVar[str | None] = None`, is probably
#   simplest; a decorator is unnecessary machinery for a single string).
# - Class-name -> Title-Case default alias derivation is not implemented.
# - The actual recursive-descent parser function (parse_document /
#   equivalent) does not exist yet -- only the model classes do. The
#   `get_section` prototype above proves out its core span-slicing step but
#   has not been integrated here.
# - The corresponding renderer (render_document) does not exist yet.
# - Plain-text extraction from a heading's inline.children (for alias
#   matching) is not implemented yet -- see PARSING STRATEGY above. The
#   `walk_token_tree` prototype above is a reusable building block for this
#   but does not itself filter to text-only content.
# - `Document`'s other fields (main_success_scenario, extensions,
#   sub_variants, open_issues, related_information) are still plain
#   MarkdownStr -- only `characteristic_information`/`CharacteristicInformation`
#   has been converted to the MarkdownHeadingN + alias pattern. Generalizing
#   the rest (each needs its own dedicated MarkdownHeading2 subclass +
#   alias) is the natural next step once the parser itself exists.
# - `CharacteristicInformation` itself has no nested h3 fields yet (empty
#   docstring body) -- uc_example.md's "## Characteristic Information" has
#   ~15 h3 children (Goal in Context, Scope, Level, Preconditions, ...)
#   that should eventually become typed MarkdownHeading3 fields on it.
# - `DocumentFrontMatter(dict[str, Any])` is still untyped; earlier
#   discussion (not yet reflected here) leaned towards a typed Pydantic
#   base with id/version/status/created/updated fields -- not started.
# - The opt-in constraint markers from the ADR (LengthConstraint, NoRawHtml,
#   RoundTrip) are not implemented anywhere in this file yet; only the
#   MarkdownHeadingN level-invariant validators exist so far.
# - No unit tests exist for anything IN THIS FILE yet (the spike tests above
#   are standalone reimplementations proving mechanisms, not tests of this
#   file's actual classes/functions).
# ============================================================================

from __future__ import annotations
from typing import Any

from biz.dfch.specmgr.models.md import MarkdownSection1, MarkdownSection2, MarkdownStr


class Title(MarkdownSection1):
    """This is the title of a document."""


class DocumentFrontMatter(dict[str, Any]):
    """This is the metadata of `uc_example.md`."""


# @some_annotation(alias="Characteristics Information (has different title)!")
class CharacteristicInformation(MarkdownSection2):
    """contains more attributes that a children of this element"""


class MainSuccessScenario(MarkdownSection2):
    """contains more attributes that a children of this element"""


class Extensions(MarkdownSection2):
    """contains more attributes that a children of this element"""


class SubVariants(MarkdownSection2):
    """contains more attributes that a children of this element"""


class OpenIssues(MarkdownSection2):
    """contains more attributes that a children of this element"""


class RelatedInformation(MarkdownSection2):
    """contains more attributes that a children of this element"""


class Document(MarkdownStr):
    """This is the contents of `uc_example.md`."""

    # Title of the document required
    title: Title

    # "Characteristic Information" required
    characteristic_information: CharacteristicInformation

    # "Main Success Scenario" required
    main_success_scenario: MainSuccessScenario

    # "Extensions" optional
    extensions: Extensions | None

    # "Sub-Variations" optional
    sub_variants: SubVariants | None

    # "Open Issues" optional
    open_issues: OpenIssues | None

    # "Related Information" optional
    related_information: RelatedInformation | None
