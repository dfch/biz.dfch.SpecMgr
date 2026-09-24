# `biz.dfch.specmgr.general.tools._domains`

The shared document-type domain names and per-domain adapter registry (feat-125-domain-lists
+ feat-134, Phase 1, REQ-012).

This module is the single source of truth for the document-type domain
**names** (feat-125-domain-lists, REQ-001, ADR c4efbde6-fd19-4aa8-8668-
95316ed62dcc "Single source of truth for the document-type domain-name
set") and for the per-domain **adapters** every cross-domain consumer
needs (feat-134, Phase 1, REQ-012, ADR 750842b2-aca4-4649-ba0c-855ec8e1f505,
**corpus and registry** sub-decision).

Every other module that names a set of document types imports the names
from here instead of hand-listing them itself (the feat-125 sweep
ruling: no other ``src/`` or ``tests/`` module may hand-list a
domain-name set). Before the feat-134 registry, the same set
(req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs) was copy-pasted as
``Literal``/tuple literals across the five existing generic tools in
this package (``update``'s/``set_status``'s/``set_classification``'s/
``delete``'s/``validate``'s own ``type`` parameter literals, plus
``delete.py``'s and ``validate.py``'s own module-scope tuples) -- and
the two new similarity tools (Phase 3) would have been the sixth and
seventh copies.

- :data:`WHOLE_BODY_DOMAINS` -- the 12-domain tuple itself: the only
  hand-listed tuple in the module, the whole-body document types in the
  canonical order ``req``, ``uc``, ``tsk``, ``qa``, ``prb``, ``gol``,
  ``rsk``, ``dec``, ``sop``, ``feat``, ``vcr``, ``sysrs``. Every other
  name-set constant is derived from it, never hand-listed a second
  time: :data:`WHOLE_BODY_NO_FEAT_DOMAINS` is the whole-body domains
  without ``feat``, :data:`UUID_DOMAINS` is those plus ``adr``, and
  :data:`ALL_DOMAINS` is ``adr`` prefixed to the whole-body domains.
  :data:`ADR` and :data:`FEAT` are the two name singletons. The five
  existing generic tools' and the two Phase 3 similarity tools' ``type``
  parameter annotations are derived from it (via the
  :data:`WholeBodyType`/:data:`WholeBodyOrAdrType` aliases below), so a
  new document type (e.g. the reserved ``ac``) registers its name in
  :data:`WHOLE_BODY_DOMAINS` once and every derived tuple and tool
  domain set picks it up by construction.
- :class:`WholeBodyDomain` + the module-scope ``_DOMAINS`` mapping --
  the per-domain adapters every cross-domain consumer needs: the
  base-dir resolver, the path iterator, ``load_by_id``, and the pure
  text parser (``parse_text``) -- the same per-domain adapter shape
  ``general/tools/delete.py`` already imports at module level. ``feat``'s
  ``<base>/<id>/README.md`` folder shape is the one bespoke path iterator
  (``iter_feat_paths``); every other domain uses the shared flat-file
  ``iter_doc_paths``. ``parse_text`` (added feat-134 Phase 2, Task 2.1)
  backs the similarity engine's per-candidate parseability check -- a
  document is unparseable when its domain's own text parser raises on any
  of the three parse-failure channels (REQ-009) -- and its candidate
  enumeration / source resolution live in
  ``general/tools/_similarity_corpus.py``, built on this registry.
- :data:`WholeBodyType` / :data:`WholeBodyOrAdrType` -- the derived
  ``Literal`` ``type``-parameter annotations for the generic tools.
- :func:`whole_body_domain` -- the ``name -> WholeBodyDomain`` lookup with
  the path-safety-convention ``ValueError`` for an unknown name (raised
  before any filesystem access).

**``adr`` is structurally excluded** from :data:`WHOLE_BODY_DOMAINS`
(issue #46, "Remove adr artifact type": ADR is being removed as an
artifact type entirely, so it is not a useful similarity target/source,
and it never had a whole-body
replace/status/classification/delete/validate adapter of its own to begin
with -- ``set_status``'s own ``adr`` branch is the single generic-tool
exception, hence the separate :data:`WholeBodyOrAdrType`; ``adr`` enters
the name-set constants only through :data:`UUID_DOMAINS` and
:data:`ALL_DOMAINS`).

**No ``mcp`` dependency here**, like every other private ``general/tools/``
support module: the registry is plain data plus the per-domain adapter
imports (the same imports ``delete.py``/``update.py``/``set_status.py``/
``set_classification.py`` already make at module level), so importing it
never registers or touches a tool.

## Classes

### `WholeBodyDomain`

One whole-body domain's registry entry: its name plus its adapters (REQ-012).

Attributes:
    name:
        The domain's name: the ``type`` value the generic tools
        dispatch on (``"req"``, ``"feat"``, ...).
    base_dir:
        The domain's base-dir resolver -- its own ``<d>.tools._paths``
        function, reading the domain's own ``SPECMGR_*_DIR`` env var
        with its own default (the shared ``SPECMGR_DOCS_DIR``-rooted
        one for every domain other than ``feat``, ``SPECMGR_FEAT_DIR``
        for ``feat``).
    iter_paths:
        The domain's document path iterator: the shared flat-file
        ``iter_doc_paths`` (every ``*.md`` directly under the base
        directory, sorted) for every domain other than ``feat``,
        ``iter_feat_paths`` (``<base>/<id>/README.md``, sorted by
        folder name) for ``feat`` -- the one bespoke,
        folder-per-document domain (ADR 8cf940c5).
    load_by_id:
        The domain's ``load_by_id`` -- resolves ``id_`` under the given
        base directory and parses the matching document, raising the
        domain's own ``XNotFoundError``. The document slot is typed
        ``object`` (each domain's own concrete document type --
        ``tuple[Path, ReqDocument]`` and so on -- is what the specific
        function actually returns); registry callers that only need
        the path (the generic ``delete`` adapters' own
        resolve-then-act pattern) discard it.
    parse_text:
        The domain's own pure text parser -- the ``parse_<d>(text)``
        function from the domain's ``models`` package (no file I/O, no
        ``mcp``): the single call that decides whether a document's
        exact text is parseable at all, raising the domain's three
        parse-failure channels (structural ``AssertionError``,
        ``pydantic.ValidationError``, ``yaml.YAMLError`` --
        ``general.tools._listing.DEFAULT_ERROR_TYPES``) on failure.
        On success it yields the validated document (the return slot
        is typed ``Any`` -- each domain's own concrete document type,
        whose ``.frontmatter`` the feat-134 Phase 2 candidate
        extraction reads for the result-row ``id``/``status``);
        ``general/tools/_similarity_corpus.py`` is the first caller.


## Functions

### `whole_body_domain(name: 'str') -> 'WholeBodyDomain'`

Return the registry entry for the whole-body domain ``name``.

The ``name -> WholeBodyDomain`` lookup the Phase 3 similarity tools
(and any future cross-domain consumer) use to reach a domain's own
adapters without re-importing them per call site.

Args:
    name:
        The domain's name: one of :data:`WHOLE_BODY_DOMAINS`.

Returns:
    The domain's :class:`WholeBodyDomain` registry entry.

Raises:
    ValueError:
        ``name`` is not one of the whole-body domains (e.g. ``"adr"``,
        or a future unregistered name) -- raised before any filesystem
        access (the path-safety convention), naming the offending value
        and the allowed set.

