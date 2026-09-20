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

"""Unit tests for the shared collection, hit-row assembly, and background warmup
(feat-134, Phase 3, Task 3.7 + the shared per-candidate loop).

Covers ACC-014 (the warmup seam: enabled -> a daemon thread named
``specmgr-similarity-warmup`` populates the cache without blocking; flag set or
backend missing -> ``start_similarity_warmup`` returns ``None`` and starts no
thread; ``warmup_similarity_cache`` swallows a mid-corpus provider failure,
leaving the cache partially warm, never raising; ``server._lifespan`` completes
without raising in both the enabled and disabled cases) plus the unit behavior
of ``collect_candidates`` (the vanished-file skip), ``to_similarity_hit`` (field
assembly, plain-``float`` score), and ``make_embed_fn`` (embeds the candidate's
own embedding text).
"""

from __future__ import annotations

import asyncio
import threading
import unittest

from biz.dfch.specmgr.general.tools._embedding_cache import _cache as embedding_cache_singleton
from biz.dfch.specmgr.general.tools._similarity_corpus import candidate_similarity_text, iter_candidate_paths
from biz.dfch.specmgr.general.tools._similarity_search import (
    _WARMUP_THREAD_NAME,
    CollectedCandidate,
    collect_candidates,
    make_embed_fn,
    start_similarity_warmup,
    to_similarity_hit,
    warmup_similarity_cache,
)

from ._similarity_helpers import block_fastembed_import, reset_default_provider, SimilarityTestCase


class TestStartSimilarityWarmup(SimilarityTestCase):
    """ACC-014: the ``start_similarity_warmup`` gate + thread seam."""

    def test_enabled_starts_a_named_daemon_thread_and_populates_the_cache(self) -> None:
        self.seed_req("Doc A", "alpha")
        self.seed_req("Doc B", "beta")
        fake = self.install_fake()

        thread = start_similarity_warmup()

        self.assertIsInstance(thread, threading.Thread)
        self.assertTrue(thread.daemon)
        self.assertEqual(thread.name, _WARMUP_THREAD_NAME)
        thread.join(timeout=15)
        self.assertFalse(thread.is_alive())
        self.assertEqual(fake.embed_calls, 2)
        self.assertEqual(len(embedding_cache_singleton._entries), 2)  # pylint: disable=protected-access

    def test_disabled_flag_returns_none_and_starts_no_thread(self) -> None:
        self.seed_req("Doc A", "alpha")
        fake = self.install_fake()
        self.set_disabled("1")

        thread = start_similarity_warmup()

        self.assertIsNone(thread)
        self.assertEqual(fake.embed_calls, 0)
        self.assertEqual(len(embedding_cache_singleton._entries), 0)  # pylint: disable=protected-access
        self.assertFalse(any(t.name == _WARMUP_THREAD_NAME for t in threading.enumerate()))

    def test_backend_missing_returns_none(self) -> None:
        self.seed_req("Doc A", "alpha")
        reset_default_provider()

        with block_fastembed_import():
            thread = start_similarity_warmup()

        self.assertIsNone(thread)


class TestWarmupSimilarityCache(SimilarityTestCase):
    """ACC-014: the warmup body never raises and leaves the cache partially warm on a mid-corpus failure."""

    def test_never_raises_and_partial_warm_on_provider_failure(self) -> None:
        self.seed_req("Doc A", "alpha")
        self.seed_req("Doc B", "beta")
        self.seed_req("Doc C", "gamma")
        fake = self.install_fake(raise_after=2)  # the third embed raises

        warmup_similarity_cache()  # must not raise

        self.assertEqual(fake.embed_calls, 3)  # the third was attempted (and raised)
        self.assertEqual(len(embedding_cache_singleton._entries), 2)  # partially warm


class TestServerLifespan(SimilarityTestCase):
    """ACC-014: ``server._lifespan`` starts the warmup at startup and never raises out of it."""

    def test_enabled_lifespan_completes_without_raising(self) -> None:
        from biz.dfch.specmgr.server import _lifespan, mcp

        self.seed_req("Doc A", "alpha")
        fake = self.install_fake()

        async def drive() -> None:
            async with _lifespan(mcp):
                pass

        asyncio.run(drive())
        for thread in threading.enumerate():
            if thread.name == _WARMUP_THREAD_NAME:
                thread.join(timeout=15)
        self.assertGreater(fake.embed_calls, 0)

    def test_disabled_lifespan_completes_without_raising_and_starts_no_thread(self) -> None:
        from biz.dfch.specmgr.server import _lifespan, mcp

        self.seed_req("Doc A", "alpha")
        fake = self.install_fake()
        self.set_disabled("1")

        async def drive() -> None:
            async with _lifespan(mcp):
                pass

        asyncio.run(drive())
        self.assertFalse(any(t.name == _WARMUP_THREAD_NAME for t in threading.enumerate()))
        self.assertEqual(fake.embed_calls, 0)


class TestCollectCandidates(SimilarityTestCase):
    """The shared per-candidate loop: row metadata + cached vector; a vanished file is skipped, not raised."""

    def test_reads_metadata_and_vector_per_candidate(self) -> None:
        doc = self.seed_req("Doc A", "alpha")
        fake = self.install_fake()

        candidates = collect_candidates(fake, iter_candidate_paths(["req"]))

        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertIsInstance(candidate, CollectedCandidate)
        self.assertEqual(candidate.domain, "req")
        self.assertEqual(candidate.text.title, "Doc A")
        self.assertEqual(candidate.text.id_, doc.id)
        self.assertEqual(list(candidate.vector), [1.0, 0.0, 0.0])

    def test_skips_a_vanished_file_without_raising(self) -> None:
        fake = self.install_fake()
        missing = self.docs_root / "req" / "nonexistent.md"

        candidates = collect_candidates(fake, iter([("req", missing)]))

        self.assertEqual(candidates, [])
        self.assertEqual(fake.embed_calls, 0)


class TestToSimilarityHit(SimilarityTestCase):
    """ACC-001/ACC-002 hit shape: field assembly and the plain-``float`` score."""

    def test_assembles_fields_and_normalizes_the_score_to_float(self) -> None:
        self.seed_req("Doc A", "alpha")
        fake = self.install_fake()
        candidate = collect_candidates(fake, iter_candidate_paths(["req"]))[0]

        hit = to_similarity_hit(candidate, 0.123)

        self.assertEqual(hit.type, "req")
        self.assertEqual(hit.id, candidate.text.id_)
        self.assertEqual(hit.title, "Doc A")
        self.assertEqual(hit.status, "draft")
        self.assertEqual(hit.path, str(candidate.path.resolve()))
        self.assertEqual(hit.score, 0.123)
        self.assertIsInstance(hit.score, float)


class TestMakeEmbedFn(SimilarityTestCase):
    """The TOCTOU-safe ``embed_fn`` embeds the candidate's own embedding text."""

    def test_embeds_the_candidates_embedding_text(self) -> None:
        doc = self.seed_req("Doc A", "alpha beta")
        fake = self.install_fake()
        fn = make_embed_fn(fake, "req")
        text = self.path_for_id("req", doc.id).read_text(encoding="utf-8")

        vector = fn(text)

        expected = candidate_similarity_text("req", text).embedding_text
        self.assertEqual(fake.embed_inputs, [expected])
        self.assertEqual(list(vector), fake.vector(expected))


if __name__ == "__main__":
    unittest.main()
