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

"""Unit tests for the embedding provider seam (feat-134, Phase 1 Task 1.3 + Phase 2 Task 2.3).

Covers ACC-012 (the chunker + renormalized mean-pool math, verified against
hand-computed expected values), ACC-010 (the :class:`FastEmbedProvider` wrapper
with ``fastembed.TextEmbedding`` monkeypatched at the import boundary), the
lazy ``get_default_provider`` import boundary (ACC-003/ACC-009), and the
``_similarity_availability`` helper's three triggers (ACC-003 missing-extra,
ACC-004 disabled-flag, ACC-009 model-load-failure). No real model, no network.
"""

from __future__ import annotations

import math
import sys
import types
import unittest
from typing import Any

from biz.dfch.specmgr.general.models import (
    REASON_BACKEND_UNAVAILABLE,
    REASON_DISABLED,
    SimilarityUnavailableResult,
)
from biz.dfch.specmgr.general.tools._embedding import (
    _CHUNK_SIZE,
    _DEFAULT_MODEL_NAME,
    _MAX_CHUNKS_PER_DOC,
    _QUERY_INSTRUCTION,
    _chunk_text,
    _evenly_sample,
    _mean_pool,
    _similarity_availability,
    FastEmbedProvider,
    get_default_provider,
    reset_default_provider,
)

from ._similarity_helpers import (
    SimilarityTestCase,
    block_fastembed_import,
    fail_fastembed_model_load,
    install_fake_provider,
)


class TestChunkText(unittest.TestCase):
    """ACC-012: whitespace-boundary character chunks, each within the model max length, no word split."""

    def test_short_input_is_a_single_chunk(self) -> None:
        result = _chunk_text("hello world")

        self.assertEqual(result, ["hello world"])

    def test_long_input_splits_at_whitespace_within_max_length(self) -> None:
        words = [f"w{i:04d}" for i in range(1000)]
        text = " ".join(words)
        self.assertGreater(len(text), _CHUNK_SIZE)

        chunks = _chunk_text(text)

        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            with self.subTest(chunk=chunk[:20]):
                self.assertLessEqual(len(chunk), _CHUNK_SIZE)
                self.assertTrue(chunk)
                self.assertFalse(chunk[0].isspace())
                self.assertFalse(chunk[-1].isspace())

    def test_no_word_is_split_across_chunks(self) -> None:
        words = [f"w{i:04d}" for i in range(1000)]
        text = " ".join(words)

        chunks = _chunk_text(text)

        self.assertEqual(" ".join(chunks).split(), text.split())

    def test_token_longer_than_budget_is_hard_split(self) -> None:
        text = "x" * (_CHUNK_SIZE + 1000)  # a single token with no whitespace

        chunks = _chunk_text(text)

        self.assertEqual([len(chunk) for chunk in chunks], [_CHUNK_SIZE, 1000])

    def test_whitespace_only_input_yields_one_unchanged_chunk(self) -> None:
        text = "   \n\t  "

        chunks = _chunk_text(text)

        self.assertEqual(chunks, [text])


class TestEvenlySample(unittest.TestCase):
    """ACC-012: the ``_MAX_CHUNKS_PER_DOC`` cap engages by even sampling (first/last kept, interior spread)."""

    def test_at_or_below_cap_is_unchanged(self) -> None:
        for count in (1, _MAX_CHUNKS_PER_DOC - 1, _MAX_CHUNKS_PER_DOC):
            with self.subTest(count=count):
                chunks = [f"c{i}" for i in range(count)]

                result = _evenly_sample(chunks)

                self.assertEqual(result, chunks)
                self.assertIs(result, chunks)  # returned unchanged (the same object)

    def test_above_cap_keeps_exactly_the_cap_with_first_and_last(self) -> None:
        count = 300
        chunks = [f"c{i}" for i in range(count)]

        result = _evenly_sample(chunks)

        self.assertEqual(len(result), _MAX_CHUNKS_PER_DOC)
        self.assertEqual(result[0], chunks[0])
        self.assertEqual(result[-1], chunks[-1])

    def test_above_cap_interior_is_evenly_spread(self) -> None:
        count = 300
        chunks = [f"c{i}" for i in range(count)]

        result = _evenly_sample(chunks)

        step = (count - 1) / (_MAX_CHUNKS_PER_DOC - 1)
        expected_indices = [round(i * step) for i in range(_MAX_CHUNKS_PER_DOC)]
        self.assertEqual(result, [chunks[index] for index in expected_indices])
        self.assertEqual(expected_indices, sorted(expected_indices))
        for earlier, later in zip(expected_indices, expected_indices[1:]):
            self.assertLess(earlier, later)  # strictly increasing: no chunk sampled twice


class TestMeanPool(unittest.TestCase):
    """ACC-012: the pooled vector is the renormalized mean (verified against hand-computed values)."""

    def test_two_orthogonal_chunks_pool_to_normalized_mean(self) -> None:
        result = _mean_pool([[1.0, 0.0], [0.0, 1.0]])

        expected = 1.0 / math.sqrt(2.0)
        self.assertAlmostEqual(result[0], expected, places=9)
        self.assertAlmostEqual(result[1], expected, places=9)

    def test_multiple_chunks_pool_to_normalized_mean(self) -> None:
        result = _mean_pool([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]])

        self.assertAlmostEqual(result[0], 2.0 / math.sqrt(5.0), places=9)
        self.assertAlmostEqual(result[1], 1.0 / math.sqrt(5.0), places=9)

    def test_single_chunk_is_normalized(self) -> None:
        result = _mean_pool([[3.0, 4.0]])

        self.assertAlmostEqual(result[0], 0.6, places=9)
        self.assertAlmostEqual(result[1], 0.8, places=9)

    def test_all_zero_chunks_return_the_zero_vector_unnormalized(self) -> None:
        result = _mean_pool([[0.0, 0.0], [0.0, 0.0]])

        self.assertEqual(result, [0.0, 0.0])

    def test_dimension_mismatch_raises_assertion(self) -> None:
        with self.assertRaises(AssertionError):
            _mean_pool([[1.0, 0.0], [0.0, 1.0, 0.0]])


class SequenceTextEmbedding:
    """A stand-in ``fastembed.TextEmbedding`` that returns a pre-computed sequence of vectors.

    The ``n``-th input (across all calls) yields ``vectors[n]``; records every
    input string and the number of ``embed`` calls so the wrapper's batching
    and chunk expansion are observable.
    """

    def __init__(self, vectors: list[list[float]]) -> None:
        self._vectors: list[list[float]] = list(vectors)
        self._next: int = 0
        self.inputs: list[str] = []
        self.calls: int = 0

    def embed(self, documents: Any) -> list[list[float]]:
        self.calls += 1
        result: list[list[float]] = []
        for document in documents:
            self.inputs.append(document)
            result.append(self._vectors[self._next])
            self._next += 1
        return result


class TestFastEmbedProviderWrapper(unittest.TestCase):
    """ACC-010: the wrapper delegates to ``fastembed.TextEmbedding`` at the import boundary.

    The backend is injected directly (the class never imports ``fastembed``
    itself), so these tests exercise the wrapper's chunk + mean-pool and
    query-prefix logic without the model.
    """

    def test_short_input_takes_the_single_embed_fast_path(self) -> None:
        backend = SequenceTextEmbedding([[1.0, 0.0]])
        provider = FastEmbedProvider(backend)

        result = provider.embed(["a short input"])

        self.assertEqual(backend.calls, 1)
        self.assertEqual(backend.inputs, ["a short input"])  # the text itself, unchanged
        self.assertEqual(result, [[1.0, 0.0]])

    def test_long_input_is_chunked_and_mean_pooled(self) -> None:
        text = " ".join(f"token{i:04d}" for i in range(1000))
        self.assertGreater(len(text), _CHUNK_SIZE)
        chunks = _evenly_sample(_chunk_text(text))
        backend = SequenceTextEmbedding([[float(index), 1.0] for index in range(len(chunks))])
        provider = FastEmbedProvider(backend)

        result = provider.embed([text])

        self.assertEqual(backend.calls, 1)  # one batched backend call
        self.assertEqual(backend.inputs, chunks)  # every chunk handed to the backend, in order
        expected_pool = _mean_pool([[float(index), 1.0] for index in range(len(chunks))])
        self.assertEqual(len(result), 1)
        for got, want in zip(result[0], expected_pool):
            self.assertAlmostEqual(got, want, places=9)

    def test_mixed_batch_is_one_backend_call_reassembled_in_input_order(self) -> None:
        short = "a short input"
        long = " ".join(f"token{i:04d}" for i in range(1000))
        chunks = _evenly_sample(_chunk_text(long))
        backend = SequenceTextEmbedding([[1.0, 0.0]] + [[0.0, float(index + 1)] for index in range(len(chunks))])
        provider = FastEmbedProvider(backend)

        result = provider.embed([short, long])

        self.assertEqual(backend.calls, 1)
        self.assertEqual(backend.inputs, [short] + chunks)
        self.assertEqual(result[0], [1.0, 0.0])  # the short input's own vector, un-pooled
        expected_pool = _mean_pool([[0.0, float(index + 1)] for index in range(len(chunks))])
        for got, want in zip(result[1], expected_pool):
            self.assertAlmostEqual(got, want, places=9)

    def test_embed_query_prepends_the_retrieval_instruction_and_never_chunks(self) -> None:
        backend = SequenceTextEmbedding([[1.0, 0.0]])
        provider = FastEmbedProvider(backend)

        result = provider.embed_query(["my query"])

        self.assertEqual(backend.calls, 1)
        self.assertEqual(backend.inputs, [f"{_QUERY_INSTRUCTION} my query"])
        self.assertEqual(result, [[1.0, 0.0]])

    def test_empty_embed_is_a_no_op_on_the_backend(self) -> None:
        backend = SequenceTextEmbedding([])
        provider = FastEmbedProvider(backend)

        result = provider.embed([])

        self.assertEqual(result, [])
        self.assertEqual(backend.calls, 0)

    def test_empty_embed_query_is_a_no_op_on_the_backend(self) -> None:
        backend = SequenceTextEmbedding([])
        provider = FastEmbedProvider(backend)

        result = provider.embed_query([])

        self.assertEqual(result, [])
        self.assertEqual(backend.calls, 0)


class TestGetDefaultProvider(SimilarityTestCase):
    """ACC-010/ACC-003/ACC-009: the lazy import + construction seam at the ``fastembed`` boundary."""

    def _install_stub_fastembed(self) -> tuple[types.ModuleType, list[str]]:
        """Install a stub ``fastembed`` module whose ``TextEmbedding`` records its model argument."""
        constructed: list[str] = []
        sentinel = object()

        class _TextEmbedding:
            def __init__(self, model_name: str) -> None:
                constructed.append(model_name)

        stub = types.ModuleType("fastembed")
        stub.TextEmbedding = _TextEmbedding  # type: ignore[attr-defined]
        saved = sys.modules.get("fastembed")
        sys.modules["fastembed"] = stub
        self.addCleanup(self._restore_fastembed, saved)
        self._sentinel = sentinel
        self._constructed = constructed
        return stub, constructed

    def _restore_fastembed(self, saved: Any) -> None:
        if saved is not None:
            sys.modules["fastembed"] = saved
        else:
            sys.modules.pop("fastembed", None)

    def test_constructs_a_fastembed_provider_cached_for_the_process(self) -> None:
        reset_default_provider()
        self._install_stub_fastembed()

        first = get_default_provider()
        second = get_default_provider()

        self.assertIsInstance(first, FastEmbedProvider)
        self.assertIs(first, second)  # constructed at most once
        self.assertEqual(len(self._constructed), 1)
        self.assertEqual(self._constructed[0], _DEFAULT_MODEL_NAME)

    def test_import_failure_propagates_out_of_get_default_provider(self) -> None:
        reset_default_provider()

        with block_fastembed_import():
            with self.assertRaises(ImportError):
                get_default_provider()

    def test_model_load_failure_propagates_out_of_get_default_provider(self) -> None:
        reset_default_provider()

        with fail_fastembed_model_load():
            with self.assertRaises(RuntimeError):
                get_default_provider()


class TestSimilarityAvailability(SimilarityTestCase):
    """ACC-003/ACC-004/ACC-009: the shared helper's three triggers, one structured result shape."""

    def test_available_returns_none(self) -> None:
        install_fake_provider()

        result = _similarity_availability()

        self.assertIsNone(result)

    def test_disabled_flag_is_presence_based_not_truthy(self) -> None:
        for value in ("1", "0", ""):
            with self.subTest(value=value):
                self.set_disabled(value)

                result = _similarity_availability()

                self.assertIsInstance(result, SimilarityUnavailableResult)
                self.assertFalse(result.available)
                self.assertEqual(result.reason, REASON_DISABLED)

    def test_backend_unavailable_when_extra_is_missing(self) -> None:
        reset_default_provider()

        with block_fastembed_import():
            result = _similarity_availability()

        self.assertIsInstance(result, SimilarityUnavailableResult)
        self.assertFalse(result.available)
        self.assertEqual(result.reason, REASON_BACKEND_UNAVAILABLE)

    def test_backend_unavailable_when_the_model_fails_to_load(self) -> None:
        reset_default_provider()

        with fail_fastembed_model_load():
            result = _similarity_availability()

        self.assertIsInstance(result, SimilarityUnavailableResult)
        self.assertFalse(result.available)
        self.assertEqual(result.reason, REASON_BACKEND_UNAVAILABLE)

    def test_disabled_is_checked_before_any_backend_import(self) -> None:
        # The flag short-circuits: with the backend blocked AND the flag set, the
        # result is the disabled reason (not backend-unavailable) -- proof the
        # flag is checked first, before the import is even attempted.
        reset_default_provider()
        self.set_disabled("1")

        with block_fastembed_import():
            result = _similarity_availability()

        self.assertIsInstance(result, SimilarityUnavailableResult)
        self.assertEqual(result.reason, REASON_DISABLED)


if __name__ == "__main__":
    unittest.main()
