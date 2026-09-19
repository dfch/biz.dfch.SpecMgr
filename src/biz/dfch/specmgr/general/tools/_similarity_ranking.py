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

"""Pure-Python cosine (dot-on-normalized) ranking (feat-134, Phase 2, Task 2.4).

Backs ADR 750842b2-aca4-4649-ba0c-855ec8e1f505's **ranking** sub-decision
(REQ-009): the similarity score is the dot product on L2-normalized
vectors (== cosine), the candidates are sorted by score descending,
``top_k`` is validated to 1..100 (the same cap the ``list_*`` tools apply
to ``max_results``; default 10, ACC-001/ACC-002), and an optional
``min_score`` filter (cosine lives in [-1, 1]; ``None`` returns up to
``top_k`` hits regardless of score). ``find_related``'s own self-exclusion
of the source document and the hit shape's assembly from the ranked keys
are the Phase 3 tools' own concern (Task 3.1/3.2, in
``find_related.py``/``find_similar_text.py`` and
``_similarity_search.to_similarity_hit`` -- this function ranks whatever
candidates it is handed).

**Numpy-free on purpose.** The chunker and the ranking are plain Python
(the dependency-light constraint: this module imports only
``collections.abc``/``typing`` plus the :data:`Vector` annotation from
``_embedding`, which itself imports nothing beyond the standard library
and the base ``pydantic``-backed ``general.models``) -- the Phase 4
deterministic-fake unit tests exercise the whole ranking path with no ML
dependency installed. A :data:`Vector` may be the backend's own
``numpy.ndarray`` (fast path) or a plain ``list[float]`` (a pooled
vector, or a test fake): both are read-only ``Sequence[float]`` and are
iterated, never mutated, never converted.

**Normalized-input contract.** The vectors handed in must already be
L2-normalized -- which both sides of the :class:`EmbeddingProvider`
protocol guarantee (the backend's own ``bge-small`` output is normalized,
and the provider's mean-pool renormalizes after the mean -- see
``_embedding._mean_pool``'s own docstring). This module therefore
performs the dot product only; it never re-normalizes (that would hide a
broken provider and change the scores). A dot product on normalized
inputs is the cosine, in [-1, 1] -- which is why ``min_score`` is
validated against exactly those bounds.

**Ties.** The sort is stable: equal scores keep the candidates' input
order, which the Phase 3 corpus enumeration makes deterministic (registry
domain order, each adapter's own sorted path order) -- a deterministic
tie-break without any key inspection (the keys are generic,
:func:`rank_candidates` is agnostic over them).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

from ._embedding import Vector

__all__ = [
    "DEFAULT_TOP_K",
    "MAX_SCORE_BOUND",
    "MAX_TOP_K",
    "MIN_SCORE_BOUND",
    "MIN_TOP_K",
    "dot_product",
    "rank_candidates",
    "validate_ranking_bounds",
]

#: The smallest valid ``top_k`` (REQ-009).
MIN_TOP_K = 1

#: The largest valid ``top_k`` (REQ-009) -- the same cap the ``list_*``
#: tools apply to ``max_results``.
MAX_TOP_K = 100

#: The default ``top_k`` (ACC-001/ACC-002's own signatures).
DEFAULT_TOP_K = 10

#: Cosine's lower bound -- the smallest meaningful ``min_score`` (a
#: threshold below it would filter out every hit).
MIN_SCORE_BOUND = -1.0

#: Cosine's upper bound -- the largest meaningful ``min_score``.
MAX_SCORE_BOUND = 1.0

#: The candidate-key type :func:`rank_candidates` is generic over (Phase 3
#: passes the candidate's own list index; the key is carried through
#: uninterpreted -- never inspected, compared, or reordered by score ties
#: beyond the stable sort's own input-order preservation).
KeyT = TypeVar("KeyT")


def _assert_vector(vector: Vector) -> None:
    """Assert ``vector`` is a read-only sequence of numbers (not a string/bytes).

    A structural check (``__getitem__`` + ``__len__`` present) on purpose,
    **not** ``isinstance(vector, collections.abc.Sequence)``: the default
    provider's native arrays (``numpy.ndarray`` -- the fast-path vectors
    the embedding cache stores and returns) are *not* virtual subclasses
    of ``collections.abc.Sequence`` (``isinstance`` reports ``False`` even
    though the array is fully indexable and length-carrying), so the
    ABC check would reject exactly the production vector type. The
    structural check accepts everything the :data:`Vector` contract
    means: plain ``list[float]`` (a pooled vector, or a test fake) and
    the backend's native arrays alike, while still rejecting
    strings/bytes (the ``str``/``bytes`` guard -- a string is indexable
    and length-carrying too, but it is not a vector).
    """
    assert not isinstance(vector, (str, bytes)), type(vector)
    assert hasattr(vector, "__getitem__") and hasattr(vector, "__len__"), type(vector)


def validate_ranking_bounds(top_k: int, min_score: float | None) -> None:
    """Reject a ``top_k`` outside 1..100 or a ``min_score`` outside [-1, 1] (REQ-009).

    The exact bounds check :func:`rank_candidates` applies to its own
    arguments, factored out so the Phase 3 similarity tools
    (``find_related``/``find_similar_text``) can run it **before any
    filesystem access** (the path-safety convention, REQ-009/ACC-015)
    instead of only at the end of the call -- :func:`rank_candidates`
    itself runs after the corpus walk (it needs the walked candidates'
    vectors to score), so a tool that deferred its ``top_k``/``min_score``
    validation to that point would have already read the source document
    and every candidate file before rejecting an invalid bound.

    Args:
        top_k: The maximum number of hits to return (1..100, REQ-009).
        min_score: The inclusive minimum cosine score ([-1, 1]); ``None``
            (no filter) is always valid.

    Raises:
        ValueError:
            ``top_k`` outside 1..100, or ``min_score`` outside [-1, 1] --
            raised before any scoring or filesystem access, naming the
            offending value and its bounds.
    """
    assert isinstance(top_k, int) and not isinstance(top_k, bool), type(top_k)
    assert min_score is None or (isinstance(min_score, (int, float)) and not isinstance(min_score, bool)), type(
        min_score
    )

    if not MIN_TOP_K <= top_k <= MAX_TOP_K:
        raise ValueError(f"top_k must be between {MIN_TOP_K} and {MAX_TOP_K} (inclusive); got {top_k}")
    if min_score is not None and not MIN_SCORE_BOUND <= min_score <= MAX_SCORE_BOUND:
        raise ValueError(
            f"min_score must be between {MIN_SCORE_BOUND} and {MAX_SCORE_BOUND} (inclusive); got {min_score}"
        )


def dot_product(a: Vector, b: Vector) -> float:
    """The dot product of two equal-dimension vectors.

    The cosine similarity when both vectors are L2-normalized (the
    :data:`Vector` contract this module's callers -- the
    :class:`EmbeddingProvider` protocol's own outputs -- satisfy; see the
    module docstring's normalized-input contract).

    Args:
        a: The first vector (read-only -- never mutated, never converted).
        b: The second vector (read-only -- same dimension as ``a``).

    Returns:
        The dot product of ``a`` and ``b`` (a ``float`` in [-1, 1] on the
        normalized-input contract).

    Raises:
        AssertionError:
            The two vectors have different dimensions (program invariant
            -- one backend, one model, one fixed dimension).
    """
    _assert_vector(a)
    _assert_vector(b)
    assert len(a) == len(b), (len(a), len(b))

    result = 0.0
    for left, right in zip(a, b):
        result += left * right
    return result


def rank_candidates(
    query_vector: Vector,
    candidates: Sequence[tuple[KeyT, Vector]],
    *,
    top_k: int = DEFAULT_TOP_K,
    min_score: float | None = None,
) -> list[tuple[KeyT, float]]:
    """Rank ``candidates`` against ``query_vector`` by cosine similarity (REQ-009).

    Every candidate is scored with :func:`dot_product` (cosine, on the
    protocol's normalized vectors), the ``min_score`` filter is applied
    (inclusive: a score exactly at the threshold is kept), the surviving
    scores are sorted descending (stable: equal scores keep the
    candidates' input order -- deterministic for a deterministic corpus
    enumeration), and the result is truncated to ``top_k``.

    Args:
        query_vector: The query-side vector (an ``embed_query`` output)
            -- or a ``find_related`` source document's own vector.
        candidates: The ``(key, candidate vector)`` pairs to rank -- the
            key is carried through uninterpreted (Phase 3: the
            candidate's own list index into the tool's own
            candidate/extracted/row lists).
        top_k: The maximum number of hits to return (1..100, REQ-009;
            default :data:`DEFAULT_TOP_K`).
        min_score: The inclusive minimum cosine score ([-1, 1]);
            ``None`` (the default) returns up to ``top_k`` hits
            regardless of score.

    Returns:
        The ranked ``(key, score)`` pairs, best first: at most ``top_k``,
        all with ``score >= min_score`` when a threshold is given, equal
        scores in the candidates' own input order.

    Raises:
        ValueError:
            ``top_k`` outside 1..100, or ``min_score`` outside [-1, 1] --
            raised before any scoring (the path-safety convention:
            invalid inputs rejected up front, REQ-009/ACC-015).
    """
    _assert_vector(query_vector)
    assert isinstance(candidates, Sequence) and not isinstance(candidates, (str, bytes)), type(candidates)

    validate_ranking_bounds(top_k, min_score)  # ValueError (top_k/min_score) before any scoring

    scored: list[tuple[KeyT, float]] = [(key, dot_product(query_vector, vector)) for key, vector in candidates]
    if min_score is not None:
        scored = [pair for pair in scored if pair[1] >= min_score]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    result = scored[:top_k]
    return result
