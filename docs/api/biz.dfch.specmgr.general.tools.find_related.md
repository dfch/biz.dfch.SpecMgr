# `biz.dfch.specmgr.general.tools.find_related`

``@mcp.tool()`` wrapper: find_related (feat-134, Phase 3, Task 3.1).

The generic, cross-domain semantic-similarity tool for finding the
documents most related to one **existing** document, given its
``type``/``id`` (ACC-001). It resolves the source document the way the
generic ``delete``/``update``/``set_status`` tools do (the shared
``WHOLE_BODY_DOMAINS`` registry's own ``load_by_id``, path-safety guards
included), embeds it through the content-hash-validated embedding cache
(``_embedding_cache.read_embedding``), enumerates every candidate document
across the target domains (``_similarity_corpus.iter_candidate_paths`` --
all whole-body domains by default, ``adr`` structurally excluded, issue
#46; a caller-supplied ``target_types`` subset otherwise), collects each
candidate's row metadata plus cached vector through the shared
``_similarity_search.collect_candidates`` loop, drops the source document
itself (by resolved-path comparison -- ACC-001's self-exclusion, ADR
750842b2's own Ranking sub-decision),
and ranks the rest with the pure-Python cosine (dot-on-normalized)
``_similarity_ranking.rank_candidates``.

**Availability first (REQ-003, ADR 750842b2's Availability sub-decision).**
The tool body checks ``_embedding._similarity_availability()`` **first
thing** -- before any argument validation, source resolution, or
filesystem access: when it returns the structured, non-raising
``SimilarityUnavailableResult`` (``SPECMGR_SIMILARITY_DISABLED`` present,
or the backend failed to import / the model failed to load, including a
first-use download failure), the tool returns that result as-is. Note the
ordering consequence: in a disabled/backend-missing environment the
structured result is returned **even for bad arguments** -- that is the
normative order (the plan's own words), not a bug to fix. Tool
*registration* is independent of availability (the ``@mcp.tool()``
decorator runs at module-import time, REQ-003), so the tool always appears
in the tool list.

**Error contract (REQ-009/ACC-015).** After the availability check, every
argument is validated **before any filesystem access**, in this order:
``top_k``/``min_score`` (``_similarity_ranking.validate_ranking_bounds``),
``target_types`` (``iter_candidate_paths``'s own up-front
``whole_body_domain`` check -- ``adr`` and every unknown name rejected),
then ``type``/``id`` (``resolve_source``'s own ``whole_body_domain``/
``validate_id`` pair -- a path-injection or wrong-format ``id`` is a
``ValueError`` before dispatch). Only then does any file get read, and a
missing source raises the domain's own ``XNotFoundError`` (propagated
unchanged from the registry's ``load_by_id`` -- like ``get_<d>``).

**Dependency-light.** This module imports ``server`` only for the
``@mcp.tool()`` decorator (exactly like every other ``general/tools``
tool module); the embedding backend (``fastembed``) is never imported
here -- it is reached lazily through the ``get_default_provider`` seam
after the availability check has already passed, so the module imports
(and the tool registers) fine on a base/``mcp``-only install.

## Functions

### `find_related(type: 'WholeBodyType', id: 'str', target_types: 'list[str] | None' = None, top_k: 'int' = 10, min_score: 'float | None' = None) -> 'list[SimilarityHit] | SimilarityUnavailableResult'`

Find the documents most semantically related to an existing document, by its ``type``/``id``.

Resolves the source document (the registry's own ``load_by_id``,
path-safety guards included), embeds it through the
content-hash-validated embedding cache, and ranks every candidate
document across the target whole-body domains (all of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs by default --
``adr`` is structurally excluded, issue #46 -- or the
caller-supplied ``target_types`` subset) against the source's own
vector by cosine similarity (dot product on L2-normalized vectors),
excluding the source document itself from the results (by
resolved-path comparison). Unparseable candidates still appear:
embedded from their full raw file text, with the
``"<failed to parse>"`` marker title/status and ``id = None``
(REQ-009).

When the embedding feature is unavailable at runtime (the
``SPECMGR_SIMILARITY_DISABLED`` environment variable is present, or
the embedding backend fails to import or the model fails to load,
including a first-use download failure), this tool returns the
structured, non-raising ``SimilarityUnavailableResult``
(``{available: false, reason, message}``) instead of doing any of the
above -- checked first thing, before argument validation or
filesystem access (REQ-003).

Parameters
----------
type:
    The source document's type / domain: one of ``req``, ``uc``,
    ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``,
    ``feat``, ``vcr``, ``sysrs`` (``adr`` is rejected).
id:
    The source document's specmgr-assigned identifier: a canonical
    lowercase-hex UUID for every domain other than ``feat``, a
    ``feat-NNN-slug`` folder name for ``feat``.
target_types:
    The domains to search (each one of ``req``, ``uc``, ``tsk``,
    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``,
    ``vcr``, ``sysrs``), in the order to enumerate them in;
    ``None`` (the default) means every whole-body domain.
top_k:
    The maximum number of hits to return (1..100, default 10).
min_score:
    An inclusive lower bound on the cosine score ([-1, 1]);
    ``None`` (the default) returns up to ``top_k`` hits regardless
    of score.

Returns
-------
list[SimilarityHit] | SimilarityUnavailableResult
    On a successful search: the ranked hits, best first -- each row
    the candidate's ``type``, validated ``id`` (``None`` for an
    unparseable candidate), ``title`` (the marker for one),
    ``status`` (the marker for one), real absolute ``path``, and
    cosine ``score`` -- at most ``top_k`` rows, all with
    ``score >= min_score`` when a threshold is given; the source
    document itself never appears. When the feature is unavailable:
    the structured ``SimilarityUnavailableResult`` (never raises for
    unavailability, REQ-003).

Raises
------
ValueError
    ``type`` is not one of the whole-body domains (e.g. ``"adr"``),
    ``id`` is a path-injection attempt or not in the domain's own
    format, a ``target_types`` entry is not one of the whole-body
    domains, or ``top_k`` is outside 1..100 / ``min_score`` outside
    [-1, 1] -- each raised **before any filesystem access**
    (REQ-009/ACC-015); nothing is read or embedded.
ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
SopNotFoundError / FeatNotFoundError / VcrNotFoundError / SysrsNotFoundError
    No document of ``type`` has this ``id`` -- the domain's own
    not-found error, propagated unchanged from the registry's
    ``load_by_id`` (REQ-009/ACC-015; an unparseable source is
    indistinguishable from a missing one by design -- id lookup
    skips unparseable files).

