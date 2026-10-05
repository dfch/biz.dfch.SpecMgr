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
``specmgr-startup-warmup`` populates the cache without blocking; backend
missing -> the thread still starts (the similarity phase's own availability
probe runs inside itself, Phase 5, Task 5.2), and exits without cache writes
or a provider installed; ``warmup_similarity_cache`` swallows a mid-corpus
provider failure, leaving the cache partially warm, never raising;
``server._lifespan`` completes without raising in both the enabled and
fully-disabled cases) plus the unit behavior of ``collect_candidates`` (the
vanished-file skip), ``to_similarity_hit`` (field assembly, plain-``float``
score), and ``make_embed_fn`` (embeds the candidate's own embedding text).

**feat-187-list-feat-timeout, Task 110.120.** The standalone
``start_similarity_warmup`` spawner this module's own tests used to drive
directly has been retired: ``general.tools._startup_warmup.start_startup_warmup``
is the new, unified entry point (feat frontmatter phase -> feat full-parse
phase -> this module's own, unchanged ``warmup_similarity_cache`` body as
phase 3), so the warmup-seam tests below now drive that spawner instead.
``SPECMGR_SIMILARITY_DISABLED`` alone no longer means "no thread at all" --
the unified thread still starts for the (here: empty, so near-instant)
``feat`` phases -- it now means "no similarity phase, no embed work"
instead; the ``SimilarityTestCase`` fixture's own ``SPECMGR_FEAT_DIR`` temp
dir has no feature folders, so the ``feat`` phases are an immediate no-op in
every test below, isolating these assertions to the similarity phase alone.
The true "no thread at all" invariant now requires *both*
``SPECMGR_SIMILARITY_DISABLED`` and ``SPECMGR_FEAT_WARMUP_DISABLED`` to be
set (ACC-009's exhaustive four-combination coverage is Phase 120's own,
later addition; this module's lifespan test below only pins the
both-flags-set no-op case it already covered under the old design).
"""

from __future__ import annotations

import asyncio
import os
import threading
import unittest
from unittest import mock

from biz.dfch.specmgr.feat.tools import _cache as feat_cache_module
from biz.dfch.specmgr.feat.tools._paths import README_FILENAME, feat_base_dir
from biz.dfch.specmgr.general.tools import _embedding as embedding_module
from biz.dfch.specmgr.general.tools._embedding_cache import _cache as embedding_cache_singleton
from biz.dfch.specmgr.general.tools._similarity_corpus import candidate_similarity_text, iter_candidate_paths
from biz.dfch.specmgr.general.tools._similarity_search import (
    CollectedCandidate,
    collect_candidates,
    make_embed_fn,
    to_similarity_hit,
    warmup_similarity_cache,
)
from biz.dfch.specmgr.general.tools._startup_warmup import FEAT_WARMUP_DISABLED_ENV_VAR, start_startup_warmup

from ._similarity_helpers import _FEAT_MINIMAL_BODY, block_fastembed_import, reset_default_provider, SimilarityTestCase

#: The unified thread's own name (``general.tools._startup_warmup``'s own
#: module-private constant) -- duplicated here rather than imported, since
#: it is intentionally not part of that module's public ``__all__``.
_WARMUP_THREAD_NAME = "specmgr-startup-warmup"


class TestStartSimilarityWarmup(SimilarityTestCase):
    """ACC-014: the unified ``start_startup_warmup`` gate + thread seam (feat-187-list-feat-timeout,
    Task 110.120 -- this class used to drive the now-retired, similarity-only ``start_similarity_warmup``
    directly; the fixture's empty ``feat`` corpus keeps the new feat phases a near-instant no-op here)."""

    def test_enabled_starts_a_named_daemon_thread_and_populates_the_cache(self) -> None:
        self.seed_req("Doc A", "alpha")
        self.seed_req("Doc B", "beta")
        fake = self.install_fake()

        thread = start_startup_warmup()

        self.assertIsInstance(thread, threading.Thread)
        self.assertTrue(thread.daemon)
        self.assertEqual(thread.name, _WARMUP_THREAD_NAME)
        thread.join(timeout=15)
        self.assertFalse(thread.is_alive())
        self.assertEqual(fake.embed_calls, 2)
        self.assertEqual(len(embedding_cache_singleton._entries), 2)  # pylint: disable=protected-access

    def test_similarity_disabled_flag_alone_starts_a_thread_but_runs_no_similarity_phase(self) -> None:
        """SPECMGR_SIMILARITY_DISABLED alone: the unified thread still starts (for the feat phases),
        but the similarity phase itself never runs -- no embed calls, no cache writes (feat-187-list-feat-timeout,
        Task 110.120; this is the "no thread at all" assertion the pre-unification design made here, now
        corrected -- see ``test_disabled_lifespan_completes_without_raising_and_starts_no_thread`` below for
        the genuine both-flags-set no-thread invariant)."""
        self.seed_req("Doc A", "alpha")
        fake = self.install_fake()
        self.set_disabled("1")

        thread = start_startup_warmup()

        self.assertIsInstance(thread, threading.Thread)
        thread.join(timeout=15)
        self.assertFalse(thread.is_alive())
        self.assertEqual(fake.embed_calls, 0)
        self.assertEqual(len(embedding_cache_singleton._entries), 0)  # pylint: disable=protected-access

    def test_backend_missing_starts_a_thread_that_exits_without_cache_writes(self) -> None:
        self.seed_req("Doc A", "alpha")
        reset_default_provider()

        # The similarity phase's own startup gate is the env flag only (Phase 5, Task 5.2): with the
        # backend missing, a thread is still started. Join it *inside* the
        # import blocker, so the thread's own availability probe (the lazy
        # ``import fastembed``) is guaranteed to run against the blocked
        # boundary and fail, not after the blocker is restored.
        with block_fastembed_import():
            thread = start_startup_warmup()
            self.assertIsInstance(thread, threading.Thread)
            self.assertTrue(thread.daemon)
            self.assertEqual(thread.name, _WARMUP_THREAD_NAME)
            thread.join(timeout=15)

        self.assertFalse(thread.is_alive())
        self.assertEqual(len(embedding_cache_singleton._entries), 0)  # pylint: disable=protected-access
        self.assertIs(embedding_module._default_provider, None)  # pylint: disable=protected-access


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
        """The true "no thread at all" invariant now requires BOTH opt-out flags (feat-187-list-feat-timeout,
        Task 110.120): SPECMGR_SIMILARITY_DISABLED alone would still start the unified thread for the
        (here: empty) feat phases -- ACC-009's exhaustive four-combination coverage is Phase 120's own,
        later addition; this test only re-pins the both-flags-set no-op case the pre-unification design
        already covered under a single flag."""
        from biz.dfch.specmgr.server import _lifespan, mcp

        self.seed_req("Doc A", "alpha")
        fake = self.install_fake()
        self.set_disabled("1")

        async def drive() -> None:
            with mock.patch.dict(os.environ, {FEAT_WARMUP_DISABLED_ENV_VAR: "1"}):
                async with _lifespan(mcp):
                    pass

        asyncio.run(drive())
        self.assertFalse(any(t.name == _WARMUP_THREAD_NAME for t in threading.enumerate()))
        self.assertEqual(fake.embed_calls, 0)


class _FeatCacheResetSimilarityTestCase(SimilarityTestCase):
    """``SimilarityTestCase``, extended with both ``feat`` cache stages reset per test and
    ``SPECMGR_FEAT_WARMUP_DISABLED`` saved/restored (feat-187-list-feat-timeout, Phase 120's own
    Testability design note: "both feat cache stages reset per test... the new lifespan/startup
    tests built on the SimilarityTestCase fixture with both feat cache stages reset and
    SPECMGR_FEAT_WARMUP_DISABLED saved/restored"). Scoped to this one new test class rather than
    folded into the shared fixture itself, since every pre-existing test in this module already
    isolates correctly via the fixture's own fresh-temp-``SPECMGR_FEAT_DIR``-per-test convention."""

    def setUp(self) -> None:
        super().setUp()
        feat_cache_module.reset_feat_cache()
        feat_cache_module.reset_feat_dirty_cache()
        self._saved_feat_warmup_disabled = os.environ.pop(FEAT_WARMUP_DISABLED_ENV_VAR, None)

    def tearDown(self) -> None:
        feat_cache_module.reset_feat_cache()
        feat_cache_module.reset_feat_dirty_cache()
        if self._saved_feat_warmup_disabled is not None:
            os.environ[FEAT_WARMUP_DISABLED_ENV_VAR] = self._saved_feat_warmup_disabled
        super().tearDown()

    def _feat_is_warm(self, path) -> bool:  # noqa: ANN001 -- Path, kept untyped to avoid an unused import here
        """Whether ``path`` is already clean-cache-warm, via a parse-free ``peek_feat`` lookup."""
        text = path.read_text(encoding="utf-8")
        result = feat_cache_module.peek_feat(path, text) is not None
        return result

    def _seed_cold_feat_doc(self):  # noqa: ANN201 -- Path, kept untyped to avoid an unused import here
        """Seed a feat document on disk, then reset both cache stages so it starts genuinely cold.

        ``create_feat`` itself warms both cache stages as part of its own write-path warming
        (Task 110.130) -- irrelevant to a real server startup, where every feat document predates
        the process and starts cold. Resetting after seeding simulates that real cold-start
        condition, so this class's own warm/cold assertions test the warmup's own gating, not
        ``create_feat``'s unrelated write-path warming.
        """
        created = self.seed_feat(_FEAT_MINIMAL_BODY)
        feat_cache_module.reset_feat_cache()
        feat_cache_module.reset_feat_dirty_cache()
        result = feat_base_dir() / created.id / README_FILENAME
        return result


class TestAcc009ExhaustiveFlagGating(_FeatCacheResetSimilarityTestCase):
    """ACC-009: REQ-007's per-phase gating invariant, asserted directly and exhaustively across all
    four ``SPECMGR_FEAT_WARMUP_DISABLED``/``SPECMGR_SIMILARITY_DISABLED`` flag combinations --
    closing the gap the pre-existing ``TestStartSimilarityWarmup``/``TestServerLifespan`` classes
    above only partially covered (feat caches were never asserted warm/empty there; the both-
    flags-set no-thread case was the only one directly pinned)."""

    def test_both_flags_absent_thread_started_all_three_phases_run(self) -> None:
        path = self._seed_cold_feat_doc()
        fake = self.install_fake()

        thread = start_startup_warmup()

        self.assertIsInstance(thread, threading.Thread)
        thread.join(timeout=15)
        self.assertFalse(thread.is_alive())
        self.assertTrue(self._feat_is_warm(path), "feat caches must be warmed when both flags are absent")
        self.assertGreater(fake.embed_calls, 0, "the similarity cache must be populated when both flags are absent")

    def test_feat_warmup_disabled_alone_skips_feat_phases_similarity_still_runs(self) -> None:
        path = self._seed_cold_feat_doc()
        fake = self.install_fake()
        os.environ[FEAT_WARMUP_DISABLED_ENV_VAR] = "1"

        thread = start_startup_warmup()

        self.assertIsInstance(thread, threading.Thread)
        thread.join(timeout=15)
        self.assertFalse(thread.is_alive())
        self.assertFalse(self._feat_is_warm(path), "feat phases must be skipped when SPECMGR_FEAT_WARMUP_DISABLED")
        self.assertGreater(fake.embed_calls, 0, "phase 3 must still run with only the feat flag set")

    def test_similarity_disabled_alone_feat_phases_still_run_similarity_skipped(self) -> None:
        path = self._seed_cold_feat_doc()
        fake = self.install_fake()
        self.set_disabled("1")

        thread = start_startup_warmup()

        self.assertIsInstance(thread, threading.Thread)
        thread.join(timeout=15)
        self.assertFalse(thread.is_alive())
        self.assertTrue(self._feat_is_warm(path), "feat phases must still run with only the similarity flag set")
        self.assertEqual(fake.embed_calls, 0, "phase 3 must be skipped when SPECMGR_SIMILARITY_DISABLED")

    def test_both_flags_set_no_thread_started_at_all(self) -> None:
        path = self._seed_cold_feat_doc()
        fake = self.install_fake()
        self.set_disabled("1")
        os.environ[FEAT_WARMUP_DISABLED_ENV_VAR] = "1"

        thread = start_startup_warmup()

        self.assertIsNone(thread, "both flags set must be a true no-op -- no thread started at all")
        self.assertFalse(any(t.name == _WARMUP_THREAD_NAME for t in threading.enumerate()))
        self.assertFalse(self._feat_is_warm(path))
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
    """The TOCTOU-safe ``embed_fn`` embeds the candidate's own embedding text and returns its row metadata."""

    def test_embeds_the_candidates_embedding_text_and_returns_the_metadata(self) -> None:
        doc = self.seed_req("Doc A", "alpha beta")
        fake = self.install_fake()
        fn = make_embed_fn(fake, "req")
        text = self.path_for_id("req", doc.id).read_text(encoding="utf-8")

        vector, similarity_text = fn(text)

        expected = candidate_similarity_text("req", text)
        self.assertEqual(fake.embed_inputs, [expected.embedding_text])
        self.assertEqual(list(vector), fake.vector(expected.embedding_text))
        self.assertEqual(similarity_text, expected)  # the vector and the metadata share the one extraction


if __name__ == "__main__":
    unittest.main()
