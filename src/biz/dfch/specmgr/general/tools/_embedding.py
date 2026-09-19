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

"""Pluggable embedding provider seam plus the shared similarity-availability check (feat-134, Phase 1).

Backs ADR 750842b2-aca4-4649-ba0c-855ec8e1f505's two Phase-1 sub-decisions:
the **provider seam** (REQ-002) and the **availability contract** (REQ-003).

**Provider seam (REQ-002).** :class:`EmbeddingProvider` is the protocol the
two similarity tools (Phase 3, ``find_related``/``find_similar_text``) depend
on -- ``embed`` (document-side) and ``embed_query`` (query-side) -- so a
different backend can be substituted later without changing tool code.
:class:`FastEmbedProvider` is the shipped default: a thin wrapper over
``fastembed.TextEmbedding`` running ``BAAI/bge-small-en-v1.5``
(ONNX Runtime, CPU-only, 384-dim -- the model is fixed for v1, REQ-001).

**Lazy import, never at module level (REQ-003).** ``fastembed`` is imported
only inside :func:`get_default_provider` -- not at this module's import
time -- because ``server.py``'s unconditional domain-import line registers
``@mcp.tool()`` decorators via introspection at module-import time,
independent of whether any runtime dependency the tool *body* needs is
installed. A module-level ``import fastembed`` here would make the whole
server fail to start (and every tool fail to register) on a base/
``mcp``-only install. The default provider instance is constructed lazily,
guarded by a load lock (the MCP SDK thread-pools every sync tool call, so
concurrent first calls must not double-load the model).

**Availability contract (REQ-003).** Tool *registration* is independent of
dependency *availability*: the two similarity tools always register, and
both tool bodies check :func:`_similarity_availability` first thing. It
returns the structured, non-raising
:class:`~biz.dfch.specmgr.general.models.similarity_unavailable.
SimilarityUnavailableResult` (mirroring the ``set_status``
``InvalidStatusResult`` precedent, ADR b399f1ce) when either (a) the
embedding backend fails to import or to load -- including a first-use
model-download failure -- or (b) ``SPECMGR_SIMILARITY_DISABLED`` is present
(presence-based, any value, ``os.environ.get(name) is not None`` -- the
repo's own env-flag convention, ``general.resources.config``). One code
path, two triggers. ``None`` means "available -- proceed with the real
ranking logic".

**What this module does NOT do yet (later phases).** The chunk + mean-pool
long-document strategy and the ``embed_query`` retrieval-instruction prefix
(Phase 2, Task 2.3 -- :class:`FastEmbedProvider`'s two methods are the
deliberate slot points), text extraction (Phase 2, Task 2.2), ranking
(Phase 2, Task 2.4), the two tools themselves (Phase 3), and the background
warmup (Phase 3, Task 3.7, which gates on this module's
:data:`SIMILARITY_DISABLED_ENV_VAR`).
"""

from __future__ import annotations

import os
import threading
from collections.abc import Iterable, Sequence
from typing import Any, Protocol

from ...general.models import REASON_BACKEND_UNAVAILABLE, REASON_DISABLED, SimilarityUnavailableResult

__all__ = [
    "EmbeddingProvider",
    "FastEmbedProvider",
    "SIMILARITY_DISABLED_ENV_VAR",
    "Vector",
    "get_default_provider",
    "reset_default_provider",
]

#: A single embedding vector.
#:
#: The default provider yields its backend's native arrays (``numpy.ndarray``
#: of ``float32``) here, which this codebase treats as read-only
#: ``Sequence[float]`` -- the embedding cache (``_embedding_cache``) stores
#: them unconverted (ADR 750842b2: "vectors are stored in the provider's
#: native arrays (numpy), not converted to Python ``list[float]``", ~7x
#: memory bloat avoided), and a deterministic test fake yields plain
#: ``list[float]``, which is a ``Sequence[float]`` as well. Callers must
#: never mutate a vector in place: the cache returns its stored array as-is.
Vector = Sequence[float]

#: The environment variable that opts out of the similarity feature entirely
#: (presence-based, any value -- REQ-003, mirroring the repo's own env-flag
#: convention in ``general.resources.config``: ``specmgr://config`` reports
#: env vars by presence, never value).
SIMILARITY_DISABLED_ENV_VAR = "SPECMGR_SIMILARITY_DISABLED"

#: The default backend's model name, fixed for v1 (ADR 750842b2, Backend
#: sub-decision: configurability is deferred -- a quality upgrade means a
#: provider substitution, which the protocol exists to allow).
_DEFAULT_MODEL_NAME = "BAAI/bge-small-en-v1.5"


class EmbeddingProvider(Protocol):
    """The pluggable backend seam the similarity tools depend on (REQ-002).

    A backend implements the two-sided embedding surface: ``embed`` for
    document-side inputs (every candidate corpus document, plus a
    ``find_related`` source document) and ``embed_query`` for query-side
    inputs (a ``find_similar_text`` free-text query). Both are batch
    (list-in, list-out) and return exactly one vector per input string --
    for the default provider, that includes the chunk + mean-pool
    long-document strategy (Phase 2, Task 2.3) living *inside* the
    provider, so tool code never sees per-chunk vectors.

    Parameters (shared by both methods)
    -----------------------------------
    texts:
        The input strings to embed (document text for :meth:`embed`,
        query text for :meth:`embed_query`); never empty in practice, but
        an empty list is a valid, empty-input edge case.

    Returns (shared by both methods)
    --------------------------------
    list[Vector]
        One :data:`Vector` per input string, in input order.
    """

    def embed(self, texts: list[str]) -> list[Vector]:
        """Embed document-side inputs (one vector per input)."""
        ...

    def embed_query(self, texts: list[str]) -> list[Vector]:
        """Embed query-side inputs (one vector per input).

        Phase 2, Task 2.3: applies the backend's retrieval instruction
        prefix (``bge-small``'s "Represent this sentence for searching
        relevant passages:") and never chunks (queries are short).
        """
        ...


class _TextEmbeddingLike(Protocol):
    """The minimal ``fastembed.TextEmbedding`` surface :class:`FastEmbedProvider` wraps.

    Declared structurally (not imported) so this module stays importable
    without the ``similarity`` extra installed (REQ-003): the real
    ``fastembed.TextEmbedding`` satisfies it, and the Phase 4 wrapper test
    (ACC-010) monkeypatches ``fastembed.TextEmbedding`` at the import
    boundary, where :func:`get_default_provider` constructs it. The real
    class carries further optional parameters (``batch_size``, ``parallel``,
    ``truncate``, ...) that the provider does not use yet.
    """

    def embed(self, documents: Iterable[str]) -> Iterable[Any]:
        """Embed ``documents``; one vector per input, in input order."""
        ...


class FastEmbedProvider:
    """The default :class:`EmbeddingProvider`: ``fastembed.TextEmbedding``, CPU-only.

    Wraps an already-constructed ``fastembed.TextEmbedding`` instance
    (injected by :func:`get_default_provider`, which performs the lazy
    ``import fastembed`` and the model load -- including the one-time
    first-use download -- under the load lock). This class itself never
    imports ``fastembed`` and never constructs the model: it is a pure,
    directly-testable wrapper.

    Phase 1 (this module): both methods call the underlying
    ``TextEmbedding.embed`` directly, one vector per input. Phase 2,
    Task 2.3 slots the chunk + mean-pool long-document strategy into
    :meth:`embed` (whitespace-boundary character chunks, single-embed fast
    path at/below the model max length, ``_MAX_CHUNKS_PER_DOC`` even-
    sampling cap, ``normalize(mean(chunk_vectors))`` pooling) and the BGE
    retrieval-instruction prefix into :meth:`embed_query` -- without any
    change to this class's public surface.

    Attributes:
        text_embedding: The wrapped ``fastembed.TextEmbedding`` instance
            (structural type :class:`_TextEmbeddingLike`); injected, never
            constructed here.
    """

    def __init__(self, text_embedding: _TextEmbeddingLike) -> None:
        """Wrap an already-constructed ``fastembed.TextEmbedding``.

        Args:
            text_embedding: The backend instance to wrap (see
                :class:`_TextEmbeddingLike`); constructed by
                :func:`get_default_provider` under its own load lock.
        """
        assert text_embedding is not None, type(text_embedding)
        self.text_embedding = text_embedding

    def embed(self, texts: list[str]) -> list[Vector]:
        """Embed document-side inputs, one vector per input (REQ-002).

        Phase 1: direct ``TextEmbedding.embed`` call. Phase 2, Task 2.3
        replaces the body with the chunk + mean-pool strategy (the backend's
        own ``truncate`` default guards any slight per-chunk overflow).

        Args:
            texts: The document-side input strings.

        Returns:
            One :data:`Vector` per input string, in input order -- the
            backend's native arrays, stored and returned unconverted.
        """
        assert isinstance(texts, list), type(texts)

        result: list[Vector] = [vector for vector in self.text_embedding.embed(texts)]
        return result

    def embed_query(self, texts: list[str]) -> list[Vector]:
        """Embed query-side inputs, one vector per input (REQ-002).

        Phase 1: direct ``TextEmbedding.embed`` call, identical to
        :meth:`embed`. Phase 2, Task 2.3 prepends the backend's retrieval
        instruction prefix and guarantees queries are never chunked.

        Args:
            texts: The query-side input strings.

        Returns:
            One :data:`Vector` per input string, in input order.
        """
        assert isinstance(texts, list), type(texts)

        result: list[Vector] = [vector for vector in self.text_embedding.embed(texts)]
        return result


#: The process's single default provider instance, constructed at most once
#: (lazily, under :data:`_load_lock`); ``None`` until the first successful
#: :func:`get_default_provider` call -- and reset back to ``None`` by a
#: failed load (so a later call can retry once the model is downloadable)
#: or by the test-only :func:`reset_default_provider` hook.
_default_provider: EmbeddingProvider | None = None

#: Guards the double-checked construction in :func:`get_default_provider` --
#: the MCP SDK thread-pools every sync tool call, so concurrent first calls
#: must not double-load (and double-download) the model.
_load_lock = threading.Lock()


def get_default_provider() -> EmbeddingProvider:
    """Return the process's default :class:`FastEmbedProvider`, constructing it on first use.

    The single construction point for the default backend (REQ-002/REQ-003):
    performs the lazy ``import fastembed`` (never at module level -- see the
    module docstring) and constructs ``fastembed.TextEmbedding(
    _DEFAULT_MODEL_NAME)`` -- eager model load, including the one-time
    first-use download, guarded by the double-checked
    :data:`_load_lock` so concurrent first calls load the model exactly
    once. The constructed provider is cached in
    :data:`_default_provider` for the process's lifetime.

    Returns:
        The shared default provider (a :class:`FastEmbedProvider`).

    Raises:
        Exception:
            Any failure of the ``import fastembed`` (the ``similarity``
            extra not installed) or of the model load (e.g. no network for
            the first-use download). :func:`_similarity_availability` is
            the sanctioned catch point that turns exactly this into the
            structured, non-raising unavailable result; direct callers
            (Phase 3 tools after the availability check passes) may still
            receive it if the model dies between the check and the call.
    """
    global _default_provider

    cached_provider = _default_provider
    if cached_provider is not None:
        return cached_provider

    with _load_lock:
        cached_provider = _default_provider
        if cached_provider is None:
            import fastembed  # REQ-003: lazy -- never at module level

            text_embedding = fastembed.TextEmbedding(_DEFAULT_MODEL_NAME)
            cached_provider = FastEmbedProvider(text_embedding)
            _default_provider = cached_provider

    return cached_provider


def reset_default_provider() -> None:
    """Drop the cached default provider instance, if any (test-only).

    Not for production use: exists so the Phase 4 wrapper test (ACC-010)
    can monkeypatch ``fastembed.TextEmbedding`` at the import boundary and
    force :func:`get_default_provider` to re-run its own lazy import +
    construction against the patched class, and so tests never observe
    another test's cached provider within the same process.
    """
    global _default_provider

    with _load_lock:
        _default_provider = None


def _similarity_availability() -> SimilarityUnavailableResult | None:
    """The shared runtime-availability check both similarity tools run first thing (REQ-003).

    One code path, two triggers, structured non-raising result
    (:class:`~biz.dfch.specmgr.general.models.similarity_unavailable.
    SimilarityUnavailableResult`, mirroring the ``set_status``
    ``InvalidStatusResult`` precedent):

    - :data:`REASON_DISABLED` -- ``SPECMGR_SIMILARITY_DISABLED`` is present
      in the environment (any value; presence-based,
      ``os.environ.get(name) is not None`` -- the repo's own env-flag
      convention, ``general.resources.config``). Checked first, before any
      backend import or model load is even attempted.
    - :data:`REASON_BACKEND_UNAVAILABLE` -- the backend failed to import
      (the ``similarity`` extra is not installed) or the model failed to
      load (including a first-use download failure, e.g. no network).
      :func:`get_default_provider` performs both, so "attempt to obtain
      the default provider" is the entire backend check.

    Returns:
        The structured unavailable result for the trigger that fired, or
        ``None`` when the feature is available and the caller should
        proceed with the real ranking logic.
    """
    if os.environ.get(SIMILARITY_DISABLED_ENV_VAR) is not None:
        result = SimilarityUnavailableResult(
            available=False,
            reason=REASON_DISABLED,
            message=(
                f"Similarity search is disabled: the {SIMILARITY_DISABLED_ENV_VAR} environment "
                "variable is present (any value; presence-based). Unset it to re-enable "
                "find_related/find_similar_text."
            ),
        )
        return result

    try:
        get_default_provider()
    except Exception:
        result = SimilarityUnavailableResult(
            available=False,
            reason=REASON_BACKEND_UNAVAILABLE,
            message=(
                "The embedding backend is unavailable: the `similarity` extra (fastembed) is not "
                f"installed, or the {_DEFAULT_MODEL_NAME} model failed to load (including a "
                "first-use download failure, e.g. no network). Install it with "
                "`pip install 'biz-dfch-specmgr[similarity]'` to enable find_related/"
                "find_similar_text."
            ),
        )
        return result

    return None
