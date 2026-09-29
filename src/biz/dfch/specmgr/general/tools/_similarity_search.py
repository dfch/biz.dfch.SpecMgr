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

"""Shared per-candidate collection, hit-row assembly, and background warmup (feat-134, Phase 3).

The one place the "for every candidate: result-row metadata plus cached
vector" loop lives, so the two similarity tools (``find_related``/
``find_similar_text``, Phase 3, Task 3.1/3.2) and the background warmup
(Phase 3, Task 3.7, REQ-011) share a single, TOCTOU-safe per-candidate
pattern instead of triplicating it (ADR 750842b2-aca4-4649-ba0c-855ec8e1f505,
**ranking** and **warmup** sub-decisions):

- :func:`make_embed_fn` -- the embedding-cache ``embed_fn`` closure for one
  ``(provider, domain)``: it re-runs ``_similarity_corpus.
  candidate_similarity_text`` on the *exact text the cache itself read and
  hashed* (the cache's own TOCTOU contract, ADR bfd76370: the stored
  vector's content always matches the stored hash), then embeds just the
  resulting ``embedding_text`` through the provider's document-side
  :meth:`~biz.dfch.specmgr.general.tools._embedding.EmbeddingProvider.embed`
  and returns the ``(vector, similarity_text)`` pair -- the cache stores
  the row metadata with the vector (feat-134, Phase 6), so the metadata a
  warm read serves came from exactly the text the stored hash covers. It
  must never close over a separately-read copy of the file's text -- that
  would store a vector whose content does not match the stored hash.
- :func:`collect_candidates` -- walks an already-materialized
  ``iter_candidate_paths`` iterator (the caller created it, so the
  caller's own argument-validation ordering -- REQ-009's "``ValueError``
  before any filesystem access" -- is under the caller's control) and, per
  candidate ``(domain, path)``, gets **both** the result-row metadata
  (title/id/status, the marker rows for unparseable documents) and the
  vector from the same ``_embedding_cache.read_embedding`` call (one file
  read per candidate, content-hash-validated: a candidate whose on-disk
  content is unchanged since its last read is never re-embedded -- and,
  since the row metadata is stored with the vector (Phase 6), never
  re-parsed either). A candidate file vanishing mid-walk (a concurrent
  ``delete`` racing this intentionally lock-free scan, the same event
  ``general.tools._listing.build_summaries``'s ``silent_skip_types``
  handles for ``list_<domain>``) is skipped, not raised.
- :func:`to_similarity_hit` -- assembles one ranked hit row
  (:class:`~biz.dfch.specmgr.general.models.similarity_hit.SimilarityHit`,
  the plan's own hit shape ``type``/``id``/``title``/``status``/``path``/
  ``score``, ACC-001/ACC-002) from a collected candidate and its score.
- :func:`warmup_similarity_cache` / :func:`start_similarity_warmup` -- the
  REQ-011 background warmup: the full default corpus (no ``target_types``
  restriction) through the same :func:`collect_candidates` path. The startup
  gate (:func:`start_similarity_warmup`, called from ``server.py``'s own
  ``_lifespan``) is the ``SPECMGR_SIMILARITY_DISABLED`` presence flag
  **only** -- lightweight and synchronous, so server startup is never
  blocked by the embedding backend (Phase 5, Task 5.2, REQ-011's strict
  reading); the flag present means no thread is started at all (a no-op).
  The full availability probe (``_embedding._similarity_availability()``,
  the same check both tool bodies run first thing, REQ-003 -- the lazy
  ``import fastembed`` plus the eager model load, including the one-time
  first-use download) runs **inside** the daemon thread
  (:func:`warmup_similarity_cache`'s first step): a structured unavailable
  result means the thread exits immediately, without cache writes. When
  started, the thread is a daemon (it dies with the process -- no shutdown
  join logic), its entire body is wrapped so that no exception escapes it
  (logged and swallowed -- a mid-warmup failure leaves the cache partially
  warm and the demand path keeps working), and it never blocks the caller
  (no join at startup).

**Dependency-light.** Standard library + ``python-frontmatter`` (base
dependency) + the Phase 1/2 ``general.tools`` siblings and the base
``pydantic``-backed ``general.models`` only -- no ``fastembed``, no
``numpy``, no ``mcp``: importable on a base/``mcp``-only install, where
the two similarity tools register and return the structured unavailable
result (REQ-003) and the warmup is a no-op without ever importing the
backend.
"""

from __future__ import annotations

import logging
import os
import threading
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

from ..models import SimilarityHit
from ._embedding import (
    EmbeddingProvider,
    SIMILARITY_DISABLED_ENV_VAR,
    Vector,
    _similarity_availability,
    get_default_provider,
)
from ._embedding_cache import read_embedding
from ._similarity_corpus import candidate_similarity_text, iter_candidate_paths
from ._similarity_text import SimilarityText

__all__ = [
    "CollectedCandidate",
    "collect_candidates",
    "make_embed_fn",
    "start_similarity_warmup",
    "to_similarity_hit",
    "warmup_similarity_cache",
]

#: The warmup thread's name (diagnostics: shows up as its own thread in
#: ``threading.enumerate()``/profilers; a daemon, so it dies with the
#: process -- no shutdown join logic by design, REQ-011).
_WARMUP_THREAD_NAME = "specmgr-similarity-warmup"

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CollectedCandidate:
    """One candidate's result-row metadata plus its cached embedding vector.

    The unit :func:`collect_candidates` yields and the two similarity
    tools consume: everything a ranked hit row needs (the row's
    ``type``/``id``/``title``/``status``/``path`` via the
    :class:`~biz.dfch.specmgr.general.tools._similarity_text.SimilarityText`
    metadata) plus the vector :func:`_similarity_ranking.rank_candidates`
    scores against.

    Attributes:
        domain:
            The candidate's domain name (one of
            ``WHOLE_BODY_DOMAINS`` -- the key's domain half).
        path:
            The candidate's on-disk path (the cache key's path half; not
            resolved here -- the cache and the hit row each ``.resolve()``
            what they need, and ``find_related``'s self-exclusion compares
            the resolved forms).
        text:
            The candidate's :class:`SimilarityText` -- its exact
            embedding input plus its result-row ``id``/``title``/``status``
            (the ``FAILED_TO_PARSE_MARKER`` rows, ``id = None``, for an
            unparseable document, REQ-009).
        vector:
            The candidate's single embedding vector (read-only -- see the
            ``_embedding_cache`` module's own read-only-vectors rule),
            from the content-hash-validated cache.
    """

    domain: str
    path: Path
    text: SimilarityText
    vector: Vector


def make_embed_fn(provider: EmbeddingProvider, domain: str) -> Callable[[str], tuple[Vector, SimilarityText]]:
    """The TOCTOU-safe embedding-cache ``embed_fn`` closure for one ``(provider, domain)``.

    The closure hands the *given* text -- the exact text the cache
    (``_embedding_cache.read_embedding``) itself read and hashed, never a
    separately-read copy (ADR bfd76370's TOCTOU contract: the stored
    vector's content must match the stored hash) -- through
    ``candidate_similarity_text`` (the unparseable-text decision, plus the
    marker degradation, REQ-009), embeds just the resulting
    ``embedding_text`` through the provider's document-side ``embed``
    (one vector per input, the protocol contract -- the chunk + mean-pool
    long-document strategy lives inside the provider, REQ-010), and
    returns the ``(vector, similarity_text)`` pair -- the same
    ``SimilarityText`` the embedding was computed from, so the cache's
    stored row metadata always matches its stored hash (feat-134, Phase 6).
    The text extraction runs exactly once per miss (the vector and the
    metadata share it).

    Args:
        provider:
            The embedding backend to embed with (the default provider in
            practice; a deterministic test fake in the Phase 4 tests).
        domain:
            The candidate's domain name: one of ``WHOLE_BODY_DOMAINS``
            (the text parser to run inside
            ``candidate_similarity_text``).

    Returns:
        The ``embed_fn`` callable (``text -> (Vector, SimilarityText)``)
        to pass to ``read_embedding`` for candidates of this domain.
    """
    assert provider is not None, type(provider)
    assert isinstance(domain, str), type(domain)
    assert domain.strip()

    def embed_fn(text: str) -> tuple[Vector, SimilarityText]:
        similarity_text = candidate_similarity_text(domain, text)
        vectors = provider.embed([similarity_text.embedding_text])
        result: tuple[Vector, SimilarityText] = (vectors[0], similarity_text)
        return result

    return embed_fn


def collect_candidates(
    provider: EmbeddingProvider,
    candidates: Iterator[tuple[str, Path]],
) -> list[CollectedCandidate]:
    """Walk every candidate ``(domain, path)`` and collect its row metadata plus cached vector.

    The shared per-candidate loop (see the module docstring): for every
    candidate, both the result-row metadata (title/id/status, the marker
    rows for unparseable documents) and the vector come from the same
    ``read_embedding`` call, with the :func:`make_embed_fn` closure for
    the candidate's own domain -- so a candidate whose on-disk content is
    unchanged since its last read is never re-embedded *and* never
    re-parsed (REQ-004's content-hash-validated cache; the row metadata
    is stored with the vector, feat-134 Phase 6). A cold candidate costs
    exactly one file read and one parse (the closure's own
    ``candidate_similarity_text`` run on the cache's read text); a warm
    one, one file read and no parse. The metadata and the vector always
    originate from the same on-disk snapshot of the file.

    Args:
        provider:
            The embedding backend to embed with on a cache miss (the
            default provider in practice; a deterministic test fake in
            the Phase 4 tests).
        candidates:
            The candidate ``(domain name, path)`` pairs to collect -- an
            already-materialized ``iter_candidate_paths`` iterator (the
            caller created it, which is where that iterator's own up-front
            ``target_types`` ``ValueError`` fires -- before any
            filesystem access, REQ-009 -- and which this function
            therefore never re-validates).

    Returns:
        The collected candidates, in the iterator's own (deterministic)
        order, excluding any candidate whose file vanished mid-walk.

    Raises:
        FileNotFoundError:
            Does **not** raise for a vanished candidate file -- it is
            skipped (a concurrent ``delete`` racing this intentionally
            lock-free scan, the same event ``general.tools._listing.
            build_summaries``'s ``silent_skip_types`` handles for
            ``list_<domain>``): the walk continues with the remaining
            candidates. Any other failure (a provider failure on a cache
            miss, a parser invariant break) propagates uncaught.
    """
    assert provider is not None, type(provider)
    assert isinstance(candidates, Iterator), type(candidates)

    collected: list[CollectedCandidate] = []
    for domain, path in candidates:
        try:
            vector, similarity_text = read_embedding(domain, path, make_embed_fn(provider, domain))
        except FileNotFoundError:
            continue
        collected.append(CollectedCandidate(domain=domain, path=path, text=similarity_text, vector=vector))

    result = collected
    return result


def to_similarity_hit(candidate: CollectedCandidate, score: float) -> SimilarityHit:
    """Assemble one ranked hit row from a collected candidate and its score (ACC-001/ACC-002).

    The hit shape is the plan's own ``(type, id, title, status, path,
    score)``: the candidate's domain name, its :class:`SimilarityText`'s
    validated ``id``/``title``/``status`` (``None``/marker/marker for an
    unparseable candidate, REQ-009), the real absolute on-disk path, and
    the cosine score :func:`_similarity_ranking.rank_candidates` computed
    against the query.

    Args:
        candidate:
            The collected candidate the hit row is built from.
        score:
            The candidate's cosine similarity against the query (in
            [-1, 1] on the provider's normalized vectors). With the
            default provider this is the backend's own numeric scalar
            type (``numpy.float32`` -- the dot product accumulates in
            the array's dtype), which is normalized to a plain Python
            ``float`` here (the hit row's own field type); with a test
            fake it is already a plain ``float``.

    Returns:
        The hit row.
    """
    assert isinstance(candidate, CollectedCandidate), type(candidate)
    assert not isinstance(score, (bool, str, bytes)), type(score)
    assert hasattr(score, "__float__"), type(score)

    result = SimilarityHit(
        type=candidate.domain,
        id=candidate.text.id_,
        title=candidate.text.title,
        status=candidate.text.status,
        path=str(candidate.path.resolve()),
        score=float(score),
    )
    return result


def warmup_similarity_cache() -> None:
    """Embed the full default corpus into the cache, never raising (REQ-011).

    The background warmup's thread body. Runs
    :func:`_embedding._similarity_availability` **first thing** (the same
    check both similarity tools run first thing in their bodies, REQ-003)
    -- this is where the full availability probe (the lazy
    ``import fastembed`` plus the eager model load, including the one-time
    first-use download) happens, i.e. *inside this thread* and never on
    the server's startup path (REQ-011's "warmup must not block server
    startup" strict reading; Phase 5, Task 5.2). When the probe returns a
    structured unavailable result, this logs at info level and returns --
    no cache writes, and still never raising. Otherwise the default
    provider is already constructed (the probe's own
    :func:`get_default_provider` call loaded it into the process
    singleton), and this embeds the **full** default corpus
    (``iter_candidate_paths()`` with no ``target_types`` restriction --
    every whole-body domain, the registry set) through the same
    :func:`collect_candidates` path the two similarity tools use, so the
    warm cache is exactly the demand path's own cache (one
    ``(domain, resolved path) -> (hash, vector, similarity_text)`` entry
    per corpus document, content-hash-validated).

    The entire body is wrapped so that **no exception escapes it** (REQ-011:
    warmup never raises out of startup): any failure (a provider failure
    partway through the corpus, an I/O error) is logged and swallowed --
    the cache stays partially warm (every candidate embedded before the
    failure is a future demand-path cache hit) and the demand path keeps
    working (a later tool call re-embeds whatever is missing, on demand).

    Returns:
        ``None`` -- the observable effect is the populated cache (and the
        log record), not a return value.
    """
    try:
        unavailable = _similarity_availability()
        if unavailable is not None:
            _logger.info("similarity warmup skipped: %s", unavailable.reason)
            return
        provider = get_default_provider()
        candidates = collect_candidates(provider, iter_candidate_paths())
        _logger.info("similarity warmup finished: %d candidate(s) embedded into the cache", len(candidates))
    except Exception as ex:
        _logger.warning("similarity warmup failed (the demand path keeps working): %s", ex, exc_info=True)


def start_similarity_warmup() -> threading.Thread | None:
    """Gate on the opt-out flag and start the daemon warmup thread, if enabled (REQ-011).

    The entry point ``server.py``'s ``_lifespan`` calls at startup.
    Synchronously it checks **only** the lightweight, synchronous
    ``SPECMGR_SIMILARITY_DISABLED`` presence gate
    (``os.environ.get(SIMILARITY_DISABLED_ENV_VAR) is not None`` -- the
    repo's own env-flag convention, REQ-003): when the flag is present it
    starts **no thread at all** -- a no-op -- and returns ``None``. When
    the flag is absent it starts a daemon thread running
    :func:`warmup_similarity_cache` and returns the thread **without
    joining it** (REQ-011: warmup must not block server startup -- the
    thread runs in the background, and as a daemon it dies with the
    process; no shutdown join logic is added).

    The full availability probe -- the lazy ``import fastembed`` plus the
    eager model load, including the one-time first-use download (
    :func:`_embedding._similarity_availability`, the same check both
    similarity tools run first thing in their bodies, REQ-003) -- runs
    **inside that daemon thread** (:func:`warmup_similarity_cache`'s first
    step; Phase 5, Task 5.2), never on this startup path: server readiness
    is therefore never blocked by the embedding backend, and on a
    first/air-gapped run the model download -- if it happens at all -- is
    backgrounded. When the probe is unavailable the thread exits
    immediately without cache writes (the demand path serves the structured
    unavailable result); when it is available the thread embeds the full
    default corpus.

    Args:
        (none -- the gate reads only the environment; the backend probe
        runs in the thread the gate starts).

    Returns:
        The started daemon thread, or ``None`` when the
        ``SPECMGR_SIMILARITY_DISABLED`` flag is present and no thread was
        started.
    """
    if os.environ.get(SIMILARITY_DISABLED_ENV_VAR) is not None:
        result: threading.Thread | None = None
        return result

    thread = threading.Thread(target=warmup_similarity_cache, daemon=True, name=_WARMUP_THREAD_NAME)
    thread.start()
    result = thread
    return result
