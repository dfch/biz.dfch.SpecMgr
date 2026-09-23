# `biz.dfch.specmgr.general.tools._references`

Shared cross-reference extraction and per-domain target resolution
(feat-144-ref-artifact, Phase 2).

Plain Python with **no** ``mcp`` import (like ``_paging.py``,
``_path_safety.py``, and ``_splice.py``), so it stays independently
testable. It holds the two shared, doc-type-agnostic halves of the
generic ``list_references`` tool (``general.tools.list_references``):

- :func:`find_references` extracts every ``<TYPE> <uuid>``
  cross-reference from a frontmatter-stripped body text via
  :data:`_REFERENCE_PATTERN` (applied with ``re.finditer``), yielding
  ``(type, id)`` pairs with ``type``/``id`` lowercased, in
  first-occurrence order. Repeated occurrences of the same reference are
  **not** deduped here -- dedup happens in the row-materialization step
  (in the tool itself).
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
  :data:`_REFERENCE_PATTERN` scans the raw, frontmatter-stripped body text
  **unconditionally**, including inside fenced code blocks and inline code
  spans. A document that quotes/illustrates the ``<TAG> <uuid>`` syntax as
  a literal example (rather than as a live reference) is still extracted
  and resolved/reported as if it were real.

The reference *tag* vocabulary is the nine tags the SYSRS/VCR structured
patterns validate as reference targets plus ``sysrs`` (the aggregator
document type may reference in free-form prose). It is deliberately
distinct from the source-domain set every ``list_*``/generic tool
dispatches over (``sop``/``tsk`` are plausible future tag additions;
``feat`` can never be one -- its ids are ``feat-NNN-slug``, not uuids).

## Functions

### `_load_adr(ref_id: 'str') -> 'tuple[str, Path]'`

Resolve one ``adr`` reference to ``(title, path)`` (feat-144 Task 2.1).

``adr`` is the special case among the target domains: no doc-cache
(ADR bfd76370-b59b-4d65-b550-a969f6c93c9d -- ADR is permanently
excluded from the cache mechanism), and ``title`` is the referenced
ADR's own ``# {title}`` H1 via ``doc.body.title`` (not
``doc.body.text``). ``AdrNotFoundError`` propagates unchanged (caught
by :func:`resolve_reference`).


### `_load_dec(ref_id: 'str') -> 'tuple[str, Path]'`

Resolve one ``dec`` reference to ``(title, path)``.

Same as :func:`_load_gol`, for the ``dec`` domain.


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

Extract every ``<TYPE> <uuid>`` cross-reference from ``text`` (feat-144 REQ-002).

``text`` is the source document's frontmatter-stripped body markdown
(e.g. from ``general.tools._splice.body_text``). :data:`_REFERENCE_PATTERN`
is applied via ``re.finditer`` over the whole text, so a match may sit
anywhere in any line (bullet prefixes, indentation, and mid-prose
references all count).

Parameters
----------
text:
    The frontmatter-stripped body text to scan.

Returns
-------
list[tuple[str, str]]
    One ``(type, id)`` pair per match, with ``type``/``id`` lowercased
    (the tag's lowercase target-domain name, the canonical lowercase-
    hex uuid), in first-occurrence order. Repeated occurrences of the
    same reference are **not** deduped here -- dedup happens in the
    row-materialization step.


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
    The referenced document's canonical lowercase-hex UUID.

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

