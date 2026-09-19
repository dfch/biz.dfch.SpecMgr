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

"""Pluggable embedding provider seam plus the shared similarity-availability check (feat-134, Phase 1 + Phase 2).

Backs ADR 750842b2-aca4-4649-ba0c-855ec8e1f505's **provider seam** (REQ-002),
**long documents** (REQ-010), and **availability contract** (REQ-003)
sub-decisions.

**Provider seam (REQ-002).** :class:`EmbeddingProvider` is the protocol the
two similarity tools (Phase 3, ``find_related``/``find_similar_text``) depend
on -- ``embed`` (document-side) and ``embed_query`` (query-side) -- so a
different backend can be substituted later without changing tool code.
:class:`FastEmbedProvider` is the shipped default: a thin wrapper over
``fastembed.TextEmbedding`` running ``BAAI/bge-small-en-v1.5``
(ONNX Runtime, CPU-only, 384-dim -- the model is fixed for v1, REQ-001).

**Long documents (REQ-010).** ``bge-small``'s 512-token max sequence length
would otherwise silently truncate long inputs -- and the corpus contains
documents (the ``.specmgr/feat`` READMEs, 5k-40k tokens) far beyond it.
:meth:`FastEmbedProvider.embed` therefore splits any input longer than
:data:`_CHUNK_SIZE` characters into whitespace-boundary character chunks
(:func:`_chunk_text` -- character-based on purpose, no private tokenizer
API; each chunk is at most :data:`_CHUNK_SIZE` characters and never splits
a word), embeds every chunk, and pools the document vector as
``normalize(mean(chunk_vectors))`` (:func:`_mean_pool` -- renormalizing
after the mean keeps cosine == dot-product comparability across documents
of different lengths). Input at/below :data:`_CHUNK_SIZE` characters takes
the single-embed fast path (every current spec artifact does).
:data:`_MAX_CHUNKS_PER_DOC` (evenly sampled above it, :func:`_evenly_sample`)
bounds worst-case per-document cost, so the embedding cost per document is
capped at ``min(chunk_count, _MAX_CHUNKS_PER_DOC)`` backend calls regardless
of file size. The backend's own ``truncate`` default guards any slight
per-chunk character/token overflow. The whole strategy lives *inside* the
provider: the protocol still returns exactly one vector per input, so tool
code (Phase 3) never sees per-chunk vectors. :meth:`FastEmbedProvider.
embed_query` prepends ``bge-small``'s retrieval instruction
(:data:`_QUERY_INSTRUCTION` -- "Represent this sentence for searching
relevant passages:") and never chunks (queries are short).

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

**What this module does NOT do yet (later phases).** The two tools
themselves (Phase 3, Task 3.1/3.2, in their own ``general/tools/``
modules) and the background warmup (Phase 3, Task 3.7, which gates on
this module's :data:`SIMILARITY_DISABLED_ENV_VAR`). The sibling Phase 2
concerns live in their own modules: the embedding-input text extraction
(``general/tools/_similarity_text.py``, Task 2.2), the candidate
enumeration / source resolution (``general/tools/_similarity_corpus.py``,
Task 2.1), and the pure-Python ranking (``general/tools/_similarity_ranking.py``,
Task 2.4).
"""

from __future__ import annotations

import math
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

#: The per-chunk character budget -- and the single-embed fast-path
#: threshold (REQ-010). Input at/below this many characters is embedded
#: whole, in one backend call, with no chunking (every current spec
#: artifact does); input above it is split into whitespace-boundary
#: chunks of at most this many characters each. ``bge-small``'s own 512-
#: token max sequence length is approximated by this character budget
#: (~2000 characters for English text at the model's ~4 characters/token
#: ratio) -- character-based on purpose, since the backend exposes no
#: public tokenizer API, and the backend's own ``truncate`` default
#: guards any slight per-chunk overflow. A future model swap (deferred,
#: v1 fixes the model) updates this constant alongside the chunker.
_CHUNK_SIZE = 2000

#: The safety cap on the number of chunks one document may contribute to
#: a single :meth:`FastEmbedProvider.embed` call (REQ-010/ADR 750842b2:
#: "evenly sampled above it"): a document that would split into more than
#: this many chunks is reduced to this many, sampled evenly across its
#: length (first and last chunk kept, the interior at equal spacing), so
#: worst-case per-document cost is bounded at
#: ``min(chunk_count, _MAX_CHUNKS_PER_DOC)`` backend calls regardless of
#: file size.
_MAX_CHUNKS_PER_DOC = 128

#: ``bge-small``'s own retrieval instruction, prepended to every query-
#: side input (REQ-010/ADR 750842b2, **provider seam** sub-decision).
#: ``bge-small-en-v1.5`` is a retrieval model: its training used this
#: instruction on the query side (and none on the passage side), so a
#: query embedded without it scores systematically lower against the
#: document-side vectors the same model produced for the corpus. A
#: trailing space separates the instruction from the query text (the
#: model card's own ``"Represent this sentence for searching relevant
#: passages: {query}"`` shape).
_QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages:"

#: The whitespace characters :func:`_chunk_text` may break on (the
#: ``str.isspace()`` set restricted to the characters that occur in
#: practice in markdown sources): the chunk boundary always lands *at*
#: one of these, so a word is never split across two chunks.
_WHITESPACE = " \t\n\r\x0b\x0c"


def _chunk_text(text: str) -> list[str]:
    """Split ``text`` into whitespace-boundary chunks of at most :data:`_CHUNK_SIZE` characters.

    Greedy fill: each chunk runs from the current position to the last
    whitespace character strictly before ``start + _CHUNK_SIZE`` (the
    separator itself is dropped -- it is pure whitespace between chunks
    and carries no embedding signal), so every chunk is at most
    :data:`_CHUNK_SIZE` characters long and never splits a word. A run
    with no whitespace at all (a single token longer than the budget)
    hard-splits at the budget. Whitespace-only text yields a single
    chunk containing the text unchanged (degenerate; the backend's own
    ``truncate`` handles it).

    Args:
        text: The input text to split (non-empty in practice -- the
            caller only routes text above the fast-path threshold here).

    Returns:
        The chunks, in order; every chunk is a substring of ``text``
        (no re-joining, no character changes other than the dropped
        boundary whitespace), at most :data:`_CHUNK_SIZE` characters
        long, and non-empty.
    """
    assert isinstance(text, str), type(text)

    chunks: list[str] = []
    start = 0
    length = len(text)
    while start < length:
        while start < length and text[start] in _WHITESPACE:
            start += 1
        if start >= length:
            break
        end = min(start + _CHUNK_SIZE, length)
        if end < length:
            boundary = max(text.rfind(char, start, end) for char in _WHITESPACE)
            if boundary > start:
                end = boundary
        chunks.append(text[start:end])
        start = end
    if not chunks:
        chunks.append(text)
    result = chunks
    return result


def _evenly_sample(chunks: list[str]) -> list[str]:
    """Apply the :data:`_MAX_CHUNKS_PER_DOC` safety cap by even sampling (REQ-010).

    At or below the cap, ``chunks`` is returned unchanged. Above it,
    exactly :data:`_MAX_CHUNKS_PER_DOC` chunks are kept: the first and
    the last (the document's opening -- carrying the double-weighted
    title -- and its closing) plus the interior at equal spacing, so no
    region of the document is over- or under-represented in the pool.

    Args:
        chunks: The :func:`_chunk_text` output to cap.

    Returns:
        ``chunks`` unchanged at/below the cap, else exactly
        :data:`_MAX_CHUNKS_PER_DOC` of its elements (first and last
        included), in order.
    """
    assert isinstance(chunks, list), type(chunks)
    assert chunks, "sampling needs at least one chunk"

    if len(chunks) <= _MAX_CHUNKS_PER_DOC:
        result = chunks
        return result

    count = len(chunks)
    step = (count - 1) / (_MAX_CHUNKS_PER_DOC - 1)
    result = [chunks[round(i * step)] for i in range(_MAX_CHUNKS_PER_DOC)]
    return result


def _mean_pool(chunk_vectors: list[Vector]) -> list[float]:
    """Pool a document's chunk vectors as ``normalize(mean(chunk_vectors))`` (REQ-010).

    Element-wise arithmetic mean of the equally-weighted chunk vectors,
    then L2 renormalization -- renormalizing after the mean keeps cosine
    == dot-product comparability between documents of different chunk
    counts (the ADR's own rationale). Pure Python on purpose (no
    ``numpy`` import, module-level or otherwise -- the dependency-light
    constraint): the backend's ``numpy.ndarray`` chunks are iterated as
    read-only :data:`Vector` sequences, and the pooled vector is a plain
    ``list[float]``. The embedding cache (``_embedding_cache``) stores
    whatever the provider returns unconverted, so the cache's own
    "native arrays" note applies to the single-embed fast path (the
    backend's own arrays, returned as-is); a pooled vector is a list by
    construction -- at most ~128 x 384 floats per chunked document, a
    negligible fraction of the whole-corpus cache.

    Args:
        chunk_vectors: One document's per-chunk vectors (two or more in
            practice -- the caller mean-pools only the chunked inputs;
            a single vector is returned by the fast path un-pooled).

    Returns:
        The renormalized mean as a plain ``list[float]``. A mean that is
        the zero vector (possible only for degenerate all-zero chunk
        vectors) is returned un-normalized -- dividing by a zero norm is
        undefined, and there is nothing to rank against it anyway.

    Raises:
        AssertionError: The chunk vectors disagree on dimension (program
            invariant -- one backend, one model, one fixed dimension).
    """
    assert isinstance(chunk_vectors, list), type(chunk_vectors)
    assert chunk_vectors, "a mean-pool needs at least one chunk vector"

    dimension = len(chunk_vectors[0])
    assert all(len(vector) == dimension for vector in chunk_vectors), "all chunk vectors must share one dimension"

    count = len(chunk_vectors)
    sums = [0.0] * dimension
    for vector in chunk_vectors:
        for i in range(dimension):
            sums[i] += vector[i]

    mean = [total / count for total in sums]
    norm = math.sqrt(sum(component * component for component in mean))
    if norm == 0.0:
        result: list[float] = mean
        return result

    result = [component / norm for component in mean]
    return result


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

    Phase 2, Task 2.3 (this module): :meth:`embed` applies the chunk +
    mean-pool long-document strategy (single-embed fast path at/below
    :data:`_CHUNK_SIZE` characters; above it, whitespace-boundary
    character chunks capped by :data:`_MAX_CHUNKS_PER_DOC` even sampling,
    pooled as ``normalize(mean(chunk_vectors))``) and :meth:`embed_query`
    prepends the BGE retrieval-instruction prefix -- both still returning
    exactly one vector per input, without any change to this class's
    public surface (REQ-010: the strategy lives inside the provider, so
    tool code never sees per-chunk vectors).

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

    def _backend_inputs(self, text: str) -> list[str]:
        """The backend input(s) for one document-side text (REQ-010).

        The single-embed fast path for text at/below :data:`_CHUNK_SIZE`
        characters (the text itself, unchanged); above it, the
        whitespace-boundary character chunks (never splitting a word, each
        at most :data:`_CHUNK_SIZE` characters) reduced by the
        :data:`_MAX_CHUNKS_PER_DOC` even-sampling cap.

        Args:
            text: One document-side input string.

        Returns:
            The one (fast path) or several (chunked) strings to hand to
            the backend for this input.
        """
        assert isinstance(text, str), type(text)

        if len(text) <= _CHUNK_SIZE:
            result: list[str] = [text]
            return result

        result = _evenly_sample(_chunk_text(text))
        return result

    def embed(self, texts: list[str]) -> list[Vector]:
        """Embed document-side inputs, one vector per input (REQ-002/REQ-010).

        Every input at/below :data:`_CHUNK_SIZE` characters is embedded
        whole (the single-embed fast path, the backend's own array
        returned unconverted); every longer input is split into
        whitespace-boundary character chunks (capped at
        :data:`_MAX_CHUNKS_PER_DOC` by even sampling), the chunks are
        embedded, and the input's vector is their renormalized mean
        (:func:`_mean_pool`) -- never silent truncation (REQ-010). All
        inputs' backend strings are collected first and handed to the
        backend in **one** ``TextEmbedding.embed`` call (the backend's
        own batching is preserved across the chunk expansion), then the
        per-input vectors are reassembled in input order.

        Args:
            texts: The document-side input strings.

        Returns:
            One :data:`Vector` per input string, in input order -- the
            backend's native arrays on the fast path, plain
            ``list[float]`` renormalized means for chunked inputs.
        """
        assert isinstance(texts, list), type(texts)

        groups: list[list[str]] = [self._backend_inputs(text) for text in texts]
        flat: list[str] = [chunk for group in groups for chunk in group]
        if not flat:
            result: list[Vector] = []
            return result

        flat_vectors: list[Vector] = [vector for vector in self.text_embedding.embed(flat)]
        assert len(flat_vectors) == len(flat), f"backend returned {len(flat_vectors)} vectors for {len(flat)} inputs"

        result = []
        offset = 0
        for group in groups:
            group_vectors = flat_vectors[offset : offset + len(group)]
            offset += len(group)
            if len(group_vectors) == 1:
                result.append(group_vectors[0])
            else:
                result.append(_mean_pool(group_vectors))
        return result

    def embed_query(self, texts: list[str]) -> list[Vector]:
        """Embed query-side inputs, one vector per input (REQ-002/REQ-010).

        Prepends :data:`_QUERY_INSTRUCTION` (``bge-small``'s own retrieval
        instruction -- the model was trained with it on the query side, so
        queries embedded without it score systematically lower against the
        corpus's document-side vectors) to every input and hands the
        prefixed inputs to the backend in one call. Queries are **never
        chunked** (they are short -- the chunk + mean-pool strategy is a
        document-side concern, REQ-010): no input length check, no
        fallback.

        Args:
            texts: The query-side input strings.

        Returns:
            One :data:`Vector` per input string, in input order.
        """
        assert isinstance(texts, list), type(texts)

        prefixed: list[str] = [f"{_QUERY_INSTRUCTION} {text}" for text in texts]
        if not prefixed:
            result: list[Vector] = []
            return result

        result = [vector for vector in self.text_embedding.embed(prefixed)]
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
