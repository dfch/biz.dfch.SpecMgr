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

# pylint: disable=redefined-builtin  # id/type intentionally shadow the builtins: public tool API, issue #41

"""``@mcp.tool()`` wrapper: find_related (feat-134, Phase 3, Task 3.1).

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
"""

from __future__ import annotations

from ...server import mcp
from ..models import SimilarityHit, SimilarityUnavailableResult
from ._domains import WholeBodyType
from ._embedding import _similarity_availability, get_default_provider
from ._embedding_cache import read_embedding
from ._similarity_corpus import iter_candidate_paths, resolve_source
from ._similarity_ranking import DEFAULT_TOP_K, rank_candidates, validate_ranking_bounds
from ._similarity_search import collect_candidates, make_embed_fn, to_similarity_hit

__all__ = ["find_related"]


@mcp.tool(
    name="find_related",
    title="Find related documents",
    description=(
        "Find the documents most semantically related to an existing document, given its `type`/`id`, "
        "ranked by cosine similarity of local sentence embeddings (`fastembed`/`bge-small`, the "
        "`similarity` extra). By default every whole-body domain is searched (req, uc, tsk, qa, prb, "
        "gol, rsk, dec, sop, feat, vcr, sysrs; `adr` is excluded structurally) -- restrict with "
        "`target_types`; the source document itself is excluded from the results. Returns up to "
        "`top_k` (default 10, validated 1..100) hits as `{type, id, title, status, path, score}` rows, "
        "sorted by `score` descending; `min_score` (default: no filter) is an inclusive cosine lower "
        "bound. An unparseable candidate still appears, embedded from its full raw text, with "
        "`id = null` and the `<failed to parse>` marker title/status. When the embedding feature is "
        "unavailable (`SPECMGR_SIMILARITY_DISABLED` present, or the backend/model fails to load), "
        "returns the structured `{available: false, reason, message}` result instead of raising. A "
        "bad `type`/`id`/`target_types`/`top_k` is a `ValueError` before any filesystem access; a "
        "missing source is the domain's own `XNotFoundError`."
    ),
)
def find_related(
    type: WholeBodyType,
    id: str,
    target_types: list[str] | None = None,
    top_k: int = DEFAULT_TOP_K,
    min_score: float | None = None,
) -> list[SimilarityHit] | SimilarityUnavailableResult:
    """Find the documents most semantically related to an existing document, by its ``type``/``id``.

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
    """
    # REQ-003: availability first -- checked before any argument validation
    # or filesystem access; a structured result short-circuits the whole call.
    unavailable = _similarity_availability()
    if unavailable is not None:
        return unavailable

    # REQ-009/ACC-015: every argument validated before any filesystem access.
    validate_ranking_bounds(top_k, min_score)
    candidates_iter = iter_candidate_paths(target_types)  # ValueError (target_types), before any filesystem access
    type_, source_path, _doc = resolve_source(
        type, id
    )  # ValueError (type/id) before fs; XNotFoundError for a missing source

    provider = get_default_provider()
    source_vector = read_embedding(type_, source_path, make_embed_fn(provider, type_))
    candidates = collect_candidates(provider, candidates_iter)

    # ACC-001: the source document itself is excluded (by resolved-path comparison).
    source_key = source_path.resolve()
    others = [
        (index, candidate) for index, candidate in enumerate(candidates) if candidate.path.resolve() != source_key
    ]
    ranked = rank_candidates(
        source_vector,
        [(index, candidate.vector) for index, candidate in others],
        top_k=top_k,
        min_score=min_score,
    )
    result = [to_similarity_hit(candidates[index], score) for index, score in ranked]
    return result
