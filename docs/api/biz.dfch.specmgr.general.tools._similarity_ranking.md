# `biz.dfch.specmgr.general.tools._similarity_ranking`

Pure-Python cosine (dot-on-normalized) ranking (feat-134, Phase 2, Task 2.4).

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

## Functions

### `_assert_vector(vector: 'Vector') -> 'None'`

Assert ``vector`` is a read-only sequence of numbers (not a string/bytes).

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


### `dot_product(a: 'Vector', b: 'Vector') -> 'float'`

The dot product of two equal-dimension vectors.

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


### `rank_candidates(query_vector: 'Vector', candidates: 'Sequence[tuple[KeyT, Vector]]', *, top_k: 'int' = 10, min_score: 'float | None' = None) -> 'list[tuple[KeyT, float]]'`

Rank ``candidates`` against ``query_vector`` by cosine similarity (REQ-009).

Every candidate is scored with :func:`dot_product` (cosine, on the
protocol's normalized vectors), the ``min_score`` filter is applied
(inclusive plus :data:`_MIN_SCORE_EPSILON`: a score exactly at the
threshold is kept, and a score within float32 accumulation error
below it is kept too), the surviving scores are sorted descending
(stable: equal scores keep the candidates' input order --
deterministic for a deterministic corpus enumeration), and the
result is truncated to ``top_k``.

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


### `validate_ranking_bounds(top_k: 'int', min_score: 'float | None') -> 'None'`

Reject a ``top_k`` outside 1..100 or a ``min_score`` outside [-1, 1] (REQ-009).

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

