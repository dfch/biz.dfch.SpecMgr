# `biz.dfch.specmgr.general.tools._embedding`

Pluggable embedding provider seam plus the shared similarity-availability check (feat-134, Phase 1).

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

## Classes

### `EmbeddingProvider`

The pluggable backend seam the similarity tools depend on (REQ-002).

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

**Methods:**

- `embed(self, texts: 'list[str]') -> 'list[Vector]'`
  Embed document-side inputs (one vector per input).

- `embed_query(self, texts: 'list[str]') -> 'list[Vector]'`
  Embed query-side inputs (one vector per input).

  Phase 2, Task 2.3: applies the backend's retrieval instruction
  prefix (``bge-small``'s "Represent this sentence for searching
  relevant passages:") and never chunks (queries are short).


### `FastEmbedProvider`

The default :class:`EmbeddingProvider`: ``fastembed.TextEmbedding``, CPU-only.

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

**Methods:**

- `embed(self, texts: 'list[str]') -> 'list[Vector]'`
  Embed document-side inputs, one vector per input (REQ-002).

  Phase 1: direct ``TextEmbedding.embed`` call. Phase 2, Task 2.3
  replaces the body with the chunk + mean-pool strategy (the backend's
  own ``truncate`` default guards any slight per-chunk overflow).

  Args:
      texts: The document-side input strings.

  Returns:
      One :data:`Vector` per input string, in input order -- the
      backend's native arrays, stored and returned unconverted.

- `embed_query(self, texts: 'list[str]') -> 'list[Vector]'`
  Embed query-side inputs, one vector per input (REQ-002).

  Phase 1: direct ``TextEmbedding.embed`` call, identical to
  :meth:`embed`. Phase 2, Task 2.3 prepends the backend's retrieval
  instruction prefix and guarantees queries are never chunked.

  Args:
      texts: The query-side input strings.

  Returns:
      One :data:`Vector` per input string, in input order.


### `_TextEmbeddingLike`

The minimal ``fastembed.TextEmbedding`` surface :class:`FastEmbedProvider` wraps.

Declared structurally (not imported) so this module stays importable
without the ``similarity`` extra installed (REQ-003): the real
``fastembed.TextEmbedding`` satisfies it, and the Phase 4 wrapper test
(ACC-010) monkeypatches ``fastembed.TextEmbedding`` at the import
boundary, where :func:`get_default_provider` constructs it. The real
class carries further optional parameters (``batch_size``, ``parallel``,
``truncate``, ...) that the provider does not use yet.

**Methods:**

- `embed(self, documents: 'Iterable[str]') -> 'Iterable[Any]'`
  Embed ``documents``; one vector per input, in input order.


## Functions

### `_similarity_availability() -> 'SimilarityUnavailableResult | None'`

The shared runtime-availability check both similarity tools run first thing (REQ-003).

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


### `get_default_provider() -> 'EmbeddingProvider'`

Return the process's default :class:`FastEmbedProvider`, constructing it on first use.

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


### `reset_default_provider() -> 'None'`

Drop the cached default provider instance, if any (test-only).

Not for production use: exists so the Phase 4 wrapper test (ACC-010)
can monkeypatch ``fastembed.TextEmbedding`` at the import boundary and
force :func:`get_default_provider` to re-run its own lazy import +
construction against the patched class, and so tests never observe
another test's cached provider within the same process.

