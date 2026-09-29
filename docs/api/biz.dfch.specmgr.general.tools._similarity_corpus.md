# `biz.dfch.specmgr.general.tools._similarity_corpus`

Candidate enumeration and source resolution for the similarity engine (feat-134, Phase 2, Task 2.1).

Built on top of the Phase 1 shared ``WHOLE_BODY_DOMAINS`` registry
(``general/tools/_domains.py``, REQ-012) and backing ADR
750842b2-aca4-4649-ba0c-855ec8e1f505's **corpus and registry**
sub-decision: the two Phase 3 similarity tools (``find_related``/
``find_similar_text``) and the background warmup (Phase 3, Task 3.7)
reach the document corpus exclusively through this module's primitives,
so the per-domain base-dir / path-iterator / parse / lookup adapters
stay in exactly one place.

**Candidate enumeration (REQ-006/REQ-012).** :func:`iter_candidate_paths`
yields every ``(domain name, on-disk path)`` candidate pair across the
target whole-body domains -- the full registry set (req, uc, tsk, qa,
prb, gol, rsk, dec, sop, feat, vcr, sysrs) by default, a
caller-supplied, order-preserving, de-duplicated subset otherwise --
flat domains via the shared ``iter_doc_paths`` and ``feat``'s
``<base>/<id>/README.md`` folder shape via its own bespoke
``iter_feat_paths`` (ADR 8cf940c5). Every target name is validated up
front via :func:`whole_body_domain` (a ``ValueError`` **before any
filesystem access** -- ``adr`` and every unknown name rejected,
REQ-009/ACC-007), so the returned iterator itself is a plain lazy path
walk: a bad name never lets one domain's paths slip through before it
fires.

**Source resolution (REQ-009/ACC-015).** :func:`resolve_source` resolves
a ``find_related`` source ``type``/``id`` the way the generic
``delete``/``update``/``set_status`` tools do: the registry rejects an
unknown/``adr`` ``type`` and :func:`_path_safety.validate_id` rejects a
path-injection or wrong-format ``id`` -- both as ``ValueError`` before
any filesystem access -- then the domain's own ``load_by_id`` resolves
and parses the document (the domain's own ``XNotFoundError`` propagates
unchanged for a missing source -- id lookup skips unparseable files, so
an unparseable source is indistinguishable from a missing one by design,
the feature README's Decisions Made), and
:func:`_path_safety.assert_within` confines the resolved path to the
domain's own base directory (defense-in-depth, the same convention).

**Per-candidate parseability (REQ-009).** :func:`is_parseable` runs the
domain's own text parser (the registry's ``parse_text`` adapter --
added to :class:`WholeBodyDomain` by this phase, Task 2.1) over a
document's exact text: a document is unparseable when that parse raises
on **any** of the three parse-failure channels
(``AssertionError``/``pydantic.ValidationError``/``yaml.YAMLError`` --
``_listing.DEFAULT_ERROR_TYPES``), exactly the channel set
``list_<domain>``'s own failed entries use. :func:`candidate_similarity_text`
combines that decision with ``_similarity_text``'s domain-agnostic
extraction: the structured embedding input plus the validated result-row
``id``/``status``/title for a parseable document, or the
``FAILED_TO_PARSE_MARKER`` title/status with ``id = None`` and the full
raw text as the embedding input for an unparseable one (REQ-009). It is
the Phase 3 per-candidate entry point -- including inside the embedding
cache's ``embed_fn`` closures, where it is called on the exact
already-read file text and never re-reads the file itself (the cache's
own TOCTOU contract, ADR bfd76370).

**Dependency-light.** Standard library + ``python-frontmatter`` (base
dependency) + the Phase 1/2 ``general.tools`` siblings only -- no
``fastembed``, no ``numpy``, no ``mcp``: importable on a base/
``mcp``-only install, where the Phase 3 tools register and return the
structured unavailable result (REQ-003) without ever touching the
corpus.

## Functions

### `_iter_candidate_paths(names: 'tuple[str, ...]') -> 'Iterator[tuple[str, Path]]'`

The actual lazy walk over the validated domain names (see :func:`iter_candidate_paths`).


### `_validated_target_types(target_types: 'Sequence[str] | None') -> 'tuple[str, ...]'`

Validate and normalize a ``target_types`` input to an ordered, de-duplicated domain-name tuple.

``None`` means the full registry set (REQ-006's default). Every
supplied name is checked via :func:`whole_body_domain` -- a
``ValueError`` for an unknown name (including ``"adr"``) raised
before any filesystem access (REQ-009/ACC-007/ACC-015).


### `candidate_similarity_text(domain: 'str', text: 'str') -> 'SimilarityText'`

Build one candidate document's :class:`SimilarityText` (REQ-005/REQ-009).

The Phase 3 per-candidate entry point: runs the domain's own text
parser over ``text`` first (the REQ-009 "parse failure of any
channel" decision -- :func:`is_parseable`'s own logic), then hands
the text to ``_similarity_text``'s domain-agnostic extraction:

- **Parseable** -- the structured embedding input (title +
  non-bookkeeping, non-``None`` frontmatter fields + raw
  frontmatter-stripped body, via ``python-frontmatter``) plus the
  validated result-row ``id``/``status`` (the domain's own defaults
  applied for a blank/absent key, exactly what ``list_<domain>``
  surfaces) and the first-H1 title.
- **Unparseable** -- the :class:`SimilarityText` from
  ``_similarity_text.failed_similarity_text``: the full raw text as
  the embedding input, the ``FAILED_TO_PARSE_MARKER`` title/status,
  ``id = None`` (REQ-009).

Purely a function of ``(domain, text)`` -- no file I/O of its own:
called on the exact already-read file text inside the embedding
cache's ``embed_fn`` closures (the demand path's one parse site since
Phase 6 -- the cache stores the resulting ``SimilarityText`` with its
vector, so a warm read serves the stored metadata instead of re-running
this), where re-reading the file would break the cache's own
hash-then-embed TOCTOU contract (ADR bfd76370); the tests call it
directly.

Args:
    domain:
        The candidate's domain name: one of
        :data:`WHOLE_BODY_DOMAINS`.
    text:
        The candidate's exact on-disk file content.

Returns:
    The candidate's :class:`SimilarityText`.

Raises:
    ValueError:
        ``domain`` is not one of the whole-body domains (e.g.
        ``"adr"``) -- before any parsing work.


### `is_parseable(domain: 'str', text: 'str') -> 'bool'`

Whether ``text`` parses as a valid document of ``domain`` (REQ-009's "any channel" decision).

Runs the domain's own text parser (the registry's ``parse_text``
adapter) over ``text`` and reports whether it raises on **any** of
the three parse-failure channels -- structural
``AssertionError``, ``pydantic.ValidationError``, ``yaml.YAMLError``
(malformed frontmatter) -- ``_listing.DEFAULT_ERROR_TYPES``, exactly
the channel set ``list_<domain>``'s own failed entries use. Any
other exception (a parser bug) propagates uncaught.

:func:`candidate_similarity_text` deliberately inlines this same
parseability decision (one parser run, not a second, separate one)
instead of calling this function -- it is kept public and is the
direct entry point the tests use.

Args:
    domain:
        The domain name: one of :data:`WHOLE_BODY_DOMAINS`.
    text:
        The document's exact text (its on-disk file content, or a
        tool-submitted body for the source side).

Returns:
    ``True`` when the parse succeeds, ``False`` on any of the three
    parse-failure channels.


### `iter_candidate_paths(target_types: 'Sequence[str] | None' = None) -> 'Iterator[tuple[str, Path]]'`

Yield every candidate ``(domain name, on-disk path)`` pair across the target domains (REQ-006).

The default target set is the full :data:`WHOLE_BODY_DOMAINS`
registry set (req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr,
sysrs -- ``adr`` structurally excluded, issue #46); a
caller-supplied ``target_types`` restricts the walk to that
(order-preserving, de-duplicated) subset. Within each domain the
paths come from the domain's own registry adapter -- the shared
flat-file ``iter_doc_paths`` (every domain other than ``feat``) or
``feat``'s own ``iter_feat_paths`` (``<base>/<id>/README.md``,
folder-per-document, ADR 8cf940c5) -- in the adapter's own sorted
order, so the enumeration is deterministic for a given on-disk
state. The base directories resolve through the domains' own
``SPECMGR_*_DIR`` env vars / defaults at iteration time, and a
missing base directory simply yields no paths for that domain (the
adapters' own convention, like ``list_<domain>``).

Args:
    target_types:
        The domain names to enumerate (each one of
        :data:`WHOLE_BODY_DOMAINS`), in the order to enumerate them
        in; ``None`` (the default) means the full registry set.

Returns:
    A lazy iterator over ``(domain name, path)`` candidate pairs.

Raises:
    ValueError:
        A ``target_types`` entry is not one of the whole-body
        domains (e.g. ``"adr"``) -- raised up front, **before any
        filesystem access** (the path-safety convention,
        REQ-009/ACC-007/ACC-015), never mid-iteration.


### `resolve_source(type_: 'str', id_: 'str') -> 'tuple[str, Path, Any]'`

Resolve a ``find_related`` source ``type``/``id`` to its on-disk path and parsed document (REQ-009).

The source-side counterpart of :func:`iter_candidate_paths`: the
registry rejects an unknown/``adr`` ``type`` and
:func:`_path_safety.validate_id` rejects a path-injection or
wrong-format ``id`` -- both as ``ValueError`` **before any
filesystem access** (the same convention the generic
``delete``/``update``/``set_status`` tools apply) -- then the
domain's own ``load_by_id`` resolves the id under the domain's own
base directory and parses the matching document, and
:func:`_path_safety.assert_within` confines the resolved path to
that base directory (defense-in-depth). A missing source raises the
domain's own ``XNotFoundError`` -- propagated unchanged, the
``find_related`` contract (REQ-009/ACC-015; ``get_<d>``'s own
behavior): id lookup skips unparseable files, so an unparseable
source is indistinguishable from a missing one by design.

Args:
    type_:
        The source's domain name: one of
        :data:`WHOLE_BODY_DOMAINS` (``"adr"`` rejected).
    id_:
        The source's id: a canonical lowercase-hex UUID for every
        domain other than ``feat``, a ``feat-NNN-slug`` folder name
        for ``feat``.

Returns:
    ``(type_, path, doc)`` -- the validated domain name, the
    resolved on-disk path (confined to the domain's own base
    directory), and the domain's own parsed document (the caller
    that only needs the path -- ``find_related``'s self-exclusion,
    Phase 3, Task 3.1 -- discards it, like the generic
    ``delete`` adapters).

Raises:
    ValueError:
        ``type_`` is not one of the whole-body domains (e.g.
        ``"adr"``), or ``id_`` is a path-injection attempt (``/``,
        ``\``, ``..``) or not in the domain's own format -- raised
        before any filesystem access.
    LookupError:
        The domain's own ``XNotFoundError`` (a ``LookupError``
        subclass, per domain): no document of ``type_`` has this
        ``id_`` -- propagated unchanged from the domain's own
        ``load_by_id``.

