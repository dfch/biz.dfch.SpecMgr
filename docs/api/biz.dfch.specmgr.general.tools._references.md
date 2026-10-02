# `biz.dfch.specmgr.general.tools._references`

Shared cross-reference extraction and per-domain target resolution
(feat-144-ref-artifact, Phase 2; the ``FEAT`` tag: feat-177-list-ref-feat).

Plain Python with **no** ``mcp`` import (like ``_paging.py``,
``_path_safety.py``, and ``_splice.py``), so it stays independently
testable. It holds the two shared, doc-type-agnostic halves of the
generic ``list_references`` tool (``general.tools.list_references``):

- :func:`find_references` extracts every ``<TYPE> <id>``
  cross-reference from a frontmatter-stripped body text via
  :data:`_REFERENCE_PATTERN` (the ten UUID tags, a canonical 8-4-4-4-12
  hex id) and :data:`_FEAT_REFERENCE_PATTERN` (the ``FEAT`` tag, a full
  ``feat-NNN-slug`` id or a bare ``feat-NNN`` number), each applied with
  ``re.finditer``, the two match sets merged by stable sort on match
  position (their spans are provably disjoint -- a UUID cannot contain
  ``t``; a feat id cannot be a UUID), yielding ``(type, id)`` pairs with
  ``type``/``id`` lowercased, in first-occurrence order. Repeated
  occurrences of the same reference are **not** deduped here -- dedup
  happens in the row-materialization step (in the tool itself).
- :func:`resolve_reference` resolves one unique reference into a
  :class:`~biz.dfch.specmgr.general.models.reference.ReferenceRow` by
  dispatching on the reference's tag to the target domain's own
  cache-backed ``load_by_id`` and ``<d>_base_dir``. Target resolution
  **never raises for a missing document**: a reference whose target is
  absent on disk (a ``LookupError`` from ``load_by_id`` -- every domain's
  ``XNotFoundError`` subclasses ``LookupError``) yields a row with
  ``title=None``, ``path=None``, and the not-found message in ``error``.
  An unknown ``ref_type`` (a tag with no ``_TARGET_RESOLVERS`` entry) is
  a programming error that propagates as a ``KeyError`` (feat-144-ref-artifact, Task 7.4).
- Caveat (accepted v1 tradeoff of the regex-based, schema-agnostic
  extractor; pinned by a dedicated test -- feat-144-ref-artifact Task 7.6):
  :data:`_REFERENCE_PATTERN` and :data:`_FEAT_REFERENCE_PATTERN` scan the
  raw, frontmatter-stripped body text **unconditionally**, including
  inside fenced code blocks and inline code spans. A document that
  quotes/illustrates the ``<TAG> <id>`` syntax as a literal example
  (rather than as a live reference) is still extracted and
  resolved/reported as if it were real.

The reference *tag* vocabulary is the ten tags the SYSRS/VCR structured
patterns validate as reference targets plus ``sysrs`` (the aggregator
document type may reference in free-form prose) plus ``feat``
(feat-177-list-ref-feat -- the one tag whose id is not a UUID: a FEAT
reference carries the full ``feat-NNN-slug`` id or the bare ``feat-NNN``
number, and :func:`_load_feat` resolves it by its own folder lookup). It
is deliberately distinct from the source-domain set every ``list_*``/
generic tool dispatches over (``sop``/``tsk`` are plausible future tag
additions).

## Functions

### `_load_adr(ref_id: 'str') -> 'tuple[str, Path]'`

Resolve one ``adr`` reference to ``(title, path)`` (feat-144 Task 2.1).

``adr`` is the one target domain that never reads through the doc
cache (ADR bfd76370-b59b-4d65-b550-a969f6c93c9d -- ADR is permanently
excluded from the cache mechanism), and ``title`` is the referenced
ADR's own ``# {title}`` H1 via ``doc.body.title`` (not
``doc.body.text``). ``AdrNotFoundError`` propagates unchanged (caught
by :func:`resolve_reference`).


### `_load_dec(ref_id: 'str') -> 'tuple[str, Path]'`

Resolve one ``dec`` reference to ``(title, path)``.

Same as :func:`_load_gol`, for the ``dec`` domain.


### `_load_feat(ref_id: 'str') -> 'tuple[str, Path]'`

Resolve one ``feat`` reference to ``(title, path)`` (feat-177-list-ref-feat Task 100.110).

``feat`` is the one target domain whose ids are not uuids: ``ref_id``
is either the full ``feat-NNN-slug`` folder name or the bare
``feat-NNN`` number (lowercased by :func:`find_references`). A
full-id-shaped ref -- and any other shape, e.g. a UUID, which can
never be a feat id -- resolves through feat's own cache-backed exact
``load_by_id`` (a miss is a ``FeatNotFoundError`` -> not-found row).
A bare ``feat-NNN`` ref resolves through the first README-backed
feature folder (the :func:`iter_feat_paths` view, lexicographic
folder-name order -- the same order ``list_feat`` reports) whose name
starts with ``feat-NNN-``: a name-only prefix filter that parses no
document in the scan (the prefix's trailing hyphen keeps ``feat-1``
from ever matching ``feat-10-*``; a ``feat-NNN-*`` folder without a
``README.md`` is not a candidate), followed by the same exact
``load_by_id`` for that first match -- if the first match's README
fails to parse, the collapsed ``FeatNotFoundError`` yields a not-found
row, and the resolver does not skip on to the next match. ``title`` is
the referenced feature's own ``# Feature: {title}`` H1 with the
``Feature: `` prefix stripped (:func:`feature_title`); ``path`` is the
resolved on-disk ``README.md`` path. ``FeatNotFoundError`` propagates
unchanged (caught by :func:`resolve_reference`).


### `_load_gol(ref_id: 'str') -> 'tuple[str, Path]'`

Resolve one ``gol`` reference to ``(title, path)`` (feat-144 Task 2.1).

``title`` is the referenced goal's own ``# {title}`` H1
(``doc.body.text``); ``path`` is the resolved on-disk file path.
``GolNotFoundError`` propagates unchanged (caught by
:func:`resolve_reference`).


### `_load_prb(ref_id: 'str') -> 'tuple[str, Path]'`

Resolve one ``prb`` reference to ``(title, path)``.

Same as :func:`_load_gol`, for the ``prb`` domain.


### `_load_qa(ref_id: 'str') -> 'tuple[str, Path]'`

Resolve one ``qa`` reference to ``(title, path)``.

Same as :func:`_load_gol`, for the ``qa`` domain.


### `_load_req(ref_id: 'str') -> 'tuple[str, Path]'`

Resolve one ``req`` reference to ``(title, path)``.

Same as :func:`_load_gol`, for the ``req`` domain.


### `_load_rsk(ref_id: 'str') -> 'tuple[str, Path]'`

Resolve one ``rsk`` reference to ``(title, path)``.

Same as :func:`_load_gol`, for the ``rsk`` domain.


### `_load_sysrs(ref_id: 'str') -> 'tuple[str, Path]'`

Resolve one ``sysrs`` reference to ``(title, path)``.

Same as :func:`_load_gol`, for the ``sysrs`` domain.


### `_load_uc(ref_id: 'str') -> 'tuple[str, Path]'`

Resolve one ``uc`` reference to ``(title, path)``.

Same as :func:`_load_gol`, for the ``uc`` domain.


### `_load_vcr(ref_id: 'str') -> 'tuple[str, Path]'`

Resolve one ``vcr`` reference to ``(title, path)``.

Same as :func:`_load_gol`, for the ``vcr`` domain.


### `find_references(text: 'str') -> 'list[tuple[str, str]]'`

Extract every ``<TYPE> <id>`` cross-reference from ``text`` (feat-144 REQ-002, the ``FEAT``
tag's own id shapes added by feat-177-list-ref-feat REQ-001).

``text`` is the source document's frontmatter-stripped body markdown
(e.g. from ``general.tools._splice.body_text``). Both
:data:`_REFERENCE_PATTERN` (the ten UUID tags with a canonical
8-4-4-4-12 hex id) and :data:`_FEAT_REFERENCE_PATTERN` (the ``FEAT``
tag with the full ``feat-NNN-slug`` id or the bare ``feat-NNN``
number) are applied via ``re.finditer`` over the whole text, and the
two match sets are merged by stable sort on match position -- the
patterns' match spans are provably disjoint (a UUID cannot contain
``t``; a feat id cannot be a UUID), so no overlap handling is needed --
and a match may sit anywhere in any line (bullet prefixes,
indentation, and mid-prose references all count).

Parameters
----------
text:
    The frontmatter-stripped body text to scan.

Returns
-------
list[tuple[str, str]]
    One ``(type, id)`` pair per match, with ``type``/``id`` lowercased
    (the tag's lowercase target-domain name, and the referenced id as
    it appeared: the canonical lowercase-hex uuid for the ten UUID
    tags, the full ``feat-NNN-slug`` id or the bare ``feat-NNN``
    number for ``feat``), in first-occurrence order. Repeated
    occurrences of the same reference are **not** deduped here -- dedup
    happens in the row-materialization step.


### `resolve_reference(ref_type: 'str', ref_id: 'str') -> 'ReferenceRow'`

Resolve one unique reference into a :class:`ReferenceRow` (feat-144 REQ-003/REQ-004).

Dispatches on ``ref_type`` (the reference tag's lowercase
target-domain name) to the target domain's own ``load_by_id`` +
``<d>_base_dir`` (see :data:`_TARGET_RESOLVERS`). The row's ``title``
is the referenced document's ``# {title}`` H1, re-derived from the
resolved document on disk, and its ``path`` the referenced document's
resolved absolute file path (``str(path.resolve())``).

Target resolution **never raises for a missing document**: a
``LookupError`` from ``load_by_id`` (every domain's
``XNotFoundError`` subclasses ``LookupError``) -- i.e. a reference
whose target is absent on disk -- yields a row with ``title=None``,
``path=None``, and the not-found message in ``error``
(``list_*``-style inline failure). An unknown ``ref_type`` (a tag
with no ``_TARGET_RESOLVERS`` entry) is a programming error that
propagates as a ``KeyError`` (feat-144-ref-artifact, Task 7.4); the
module-scope drift guard above makes the missing-entry case
impossible by construction. Only the source read (in the
``list_references`` tool itself) raises for a missing document.

Parameters
----------
ref_type:
    The reference tag's lowercase target-domain name, e.g. ``"req"``.
ref_id:
    The referenced document's id, as it appeared in the source body
    (lowercased): the canonical lowercase-hex UUID for the ten UUID
    tags, the full ``feat-NNN-slug`` id or the bare ``feat-NNN``
    number for ``feat``.

Returns
-------
ReferenceRow
    The resolved row (``title``/``path`` populated, ``error`` ``None``)
    or the not-found row (``title``/``path`` ``None``, ``error`` set).

Raises
------
KeyError
    ``ref_type`` is not one of :data:`REFERENCE_TYPES` (no
    ``_TARGET_RESOLVERS`` entry) -- a programming error, never
    expected by construction (the module-scope drift guard above).

