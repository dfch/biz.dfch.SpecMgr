# `biz.dfch.specmgr.general.tools._domains`

The shared ``WHOLE_BODY_DOMAINS`` registry (feat-134, Phase 1, REQ-012).

The one source of the whole-body domain set. Before this registry, the set
(req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs) was copy-pasted as
``Literal``/tuple literals across the five existing generic tools in this
package (``update``'s/``set_status``'s/``set_classification``'s/``delete``'s/
``validate``'s own ``type`` parameter literals, plus ``delete.py``'s and
``validate.py``'s own module-scope tuples) -- and the two new similarity
tools (Phase 3) would have been the sixth and seventh copies. REQ-012
(ADR 750842b2-aca4-4649-ba0c-855ec8e1f505, **corpus and registry**
sub-decision) makes this module the single place the set is spelled out:

- :data:`WHOLE_BODY_DOMAINS` -- the 12-domain tuple itself. The five
  existing generic tools' ``type`` parameter annotations are now derived
  from it (``Literal[WHOLE_BODY_DOMAINS]`` /
  ``Literal[WHOLE_BODY_DOMAINS + ("adr",)]`` via the
  :data:`WholeBodyType`/:data:`WholeBodyOrAdrType` aliases below), so a
  future domain (e.g. the reserved ``ac``) is added in exactly one place
  and every tool's own dispatch domain set re-derives from it.
- :class:`WholeBodyDomain` + the module-scope ``_DOMAINS`` mapping --
  the per-domain adapters every cross-domain consumer needs: the
  base-dir resolver, the path iterator, and ``load_by_id`` -- the same
  per-domain adapter shape ``general/tools/delete.py`` already imports at
  module level. ``feat``'s ``<base>/<id>/README.md`` folder shape is the
  one bespoke path iterator (``iter_feat_paths``); every other domain uses
  the shared flat-file ``iter_doc_paths``.
- :data:`WholeBodyType` / :data:`WholeBodyOrAdrType` -- the derived
  ``Literal`` ``type``-parameter annotations for the generic tools.
- :func:`whole_body_domain` -- the ``name -> WholeBodyDomain`` lookup with
  the path-safety-convention ``ValueError`` for an unknown name (raised
  before any filesystem access).

**``adr`` is structurally excluded** (issue #46, "Remove adr artifact
type": ADR is being removed as an artifact type entirely, so it is not a
useful similarity target/source, and it never had a whole-body
replace/status/classification/delete/validate adapter of its own to begin
with -- ``set_status``'s own ``adr`` branch is the single generic-tool
exception, hence the separate :data:`WholeBodyOrAdrType`).

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

