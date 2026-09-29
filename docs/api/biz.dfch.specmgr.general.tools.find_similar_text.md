# `biz.dfch.specmgr.general.tools.find_similar_text`

``@mcp.tool()`` wrapper: find_similar_text (feat-134, Phase 3, Task 3.2).

The generic, cross-domain semantic-similarity tool for finding the
documents most similar to one **free-form query text** (ACC-002) -- the
pre-creation dedup/discovery companion to ``find_related``: no source
document is resolved (there is nothing to resolve against yet), the
query itself is the query-side vector (embedded through the provider's
``embed_query`` -- the default backend's retrieval-instruction prefix,
REQ-010), and every candidate document across the target whole-body
domains (all of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs by
default, ``adr`` structurally excluded, issue #46; a caller-supplied
``target_types`` subset otherwise) is ranked against it with the same
pure-Python cosine (dot-on-normalized) ``_similarity_ranking.
rank_candidates``.

Everything else -- the availability-first contract (REQ-003, the plan's
normative ordering: the structured ``SimilarityUnavailableResult`` is
returned **even for bad arguments** in a disabled/backend-missing
environment), the error contract (REQ-009/ACC-015: ``target_types``/
``top_k``/``min_score`` validated **before any filesystem access**, the
unparseable-candidate marker rows), and the dependency-light import rule
(``server`` only for the ``@mcp.tool()`` decorator; the ``fastembed``
backend reached lazily through ``get_default_provider`` after the
availability check) -- is shared with ``find_related`` (see its own
module docstring); the candidate walk itself is the shared
``_similarity_search.collect_candidates`` loop (one per-candidate pattern
for both tools and the warmup, not a duplicated one).

## Functions

### `find_similar_text(query: 'str', target_types: 'list[str] | None' = None, top_k: 'int' = 10, min_score: 'float | None' = None) -> 'list[SimilarityHit] | SimilarityUnavailableResult'`

Find the documents most semantically similar to a free-form ``query`` text.

The pre-creation dedup/discovery companion to ``find_related``:
instead of an existing document's ``type``/``id``, the query is the
free text itself (e.g. a draft requirement's statement) -- there is
no source to resolve, and the query-side vector is the provider's
``embed_query`` output (the default backend's retrieval-instruction
prefix, REQ-010). Every candidate document across the target
whole-body domains (all of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/
vcr/sysrs by default -- ``adr`` is structurally excluded, issue
#46 -- or the caller-supplied ``target_types`` subset) is ranked
against it by cosine similarity (dot product on L2-normalized
vectors). Unparseable candidates still appear: embedded from their
full raw file text, with the ``"<failed to parse>"`` marker
title/status and ``id = None`` (REQ-009).

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
query:
    The free-form text to search for (e.g. a draft artifact's
    statement or a natural-language description of what exists
    already).
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
    ``score >= min_score`` when a threshold is given. When the
    feature is unavailable: the structured ``SimilarityUnavailableResult``
    (never raises for unavailability, REQ-003).

Raises
------
ValueError
    A ``target_types`` entry is not one of the whole-body domains
    (e.g. ``"adr"``), or ``top_k`` is outside 1..100 / ``min_score``
    outside [-1, 1] -- each raised **before any filesystem access**
    (REQ-009/ACC-015); nothing is read or embedded.

