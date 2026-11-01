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

"""ACC-001..005 tests for the two-stage dirty/clean ``list_feat`` cold-scan-timeout fix
(feat-187-list-feat-timeout, GitHub issue #187, ADR 3982712a-a46b-4b2b-809f-9c6925a49b44).

Phase 100/110 already implemented the production code this module exercises
(the feat-local dirty/clean ``DocCache`` pair in ``feat/tools/_cache.py``,
the rewired ``list_feat`` request path, ``feat/tools/_warmup.py``'s
``warmup_feat_caches()``) -- this is Phase 120's own verification suite.

ACC-009 (REQ-007's four-flag-combination lifespan gating invariant) lives in
``tests/general/tools/test__similarity_search.py`` instead, alongside the
pre-existing ``TestStartSimilarityWarmup``/``TestServerLifespan`` classes it
extends. ACC-006 (the live one-shot ``uvx`` measurement) is a manual
protocol recorded in the feature's own ``### Updates``, not a committed
test. ACC-007 is the gate itself; ACC-008 (the ADR) is already done.
"""

from __future__ import annotations

import tempfile
import textwrap
import time
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.feat.models.v1 import FeatDocument
from biz.dfch.specmgr.feat.tools import _cache as cache_module
from biz.dfch.specmgr.feat.tools._cache import read_feat, read_feat_dirty
from biz.dfch.specmgr.general.tools._doc_cache import CACHEABLE_ERROR_TYPES
from biz.dfch.specmgr.feat.tools._paths import (
    FEAT_DIR_ENV_VAR,
    README_FILENAME,
    feat_base_dir,
    iter_feat_paths,
)
from biz.dfch.specmgr.feat.tools._warmup import warmup_feat_caches
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.feat.tools.get_feat import get_feat
from biz.dfch.specmgr.feat.tools.list_feat import _to_failed_summary, _to_summary, list_feat
from biz.dfch.specmgr.feat.tools.set_feat_id import set_feat_id
from biz.dfch.specmgr.general.models import ParseFailureResult
from biz.dfch.specmgr.general.tools._listing import FAILED_TO_PARSE_MARKER, build_summaries
from biz.dfch.specmgr.general.tools._paging import normalize_paging, paginate
from biz.dfch.specmgr.general.tools.delete import delete
from biz.dfch.specmgr.general.tools.set_classification import set_classification
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.general.tools.update import update

from ._fixture_corpus import SHAPE_LETTERS, FixtureCorpus, generate_fixture_corpus, write_feat_folder

#: Letters whose dirty-stage error text is byte-identical to ``get_feat``'s from call one
#: (tier 1: malformed/missing YAML frontmatter).
_TIER1_LETTERS = frozenset({"a"})

#: Letters that fail at BOTH stages from call one, with DIFFERENT text pre-convergence (tier 2:
#: a missing or wrong-shape H1).
_TIER2_LETTERS = frozenset({"b", "c", "l"})

#: Letters that are transiently HEALTHY pre-convergence (valid frontmatter + H1, a body-level
#: defect the dirty stage never looks for) and converge to a failed row post-convergence (tier 3).
_TIER3_LETTERS = frozenset({"d", "e", "f", "g", "h", "i"})

#: Letters that are healthy in BOTH states (never fail at either stage).
_HEALTHY_LETTERS = frozenset({"j", "k", "m"})

assert _TIER1_LETTERS | _TIER2_LETTERS | _TIER3_LETTERS | _HEALTHY_LETTERS == set(SHAPE_LETTERS)

#: Each healthy/tier-3 letter's own expected title (the free-form part after ``"Feature: "``),
#: matching ``_fixture_corpus``'s own body builders -- used for ACC-002's "correct id/title/status"
#: assertions.
_EXPECTED_TITLE_BY_LETTER: dict[str, str] = {
    "d": "Legacy Requirements Shape",
    "e": "Missing Task List",
    "f": "Legacy Task Item Shape",
    "g": "Legacy Updates Timestamp",
    "h": "Raw HTML Inline Token",
    "i": "Stray List Marker",
    "j": "Healthy Baseline",
    "k": "Setext Title",
    "m": "Indented Title",
}

#: A small, valid feature body for the ACC-005 write-path tests (bypassing the fixture-corpus
#: generator's own lettered shapes, which are deliberately invalid documents for most letters).
_MINIMAL_BODY = textwrap.dedent(
    """\
    # Feature: {title}

    ## Plan

    ### Overview

    Short description.

    ### Requirements

    - REQ-001: The widget must render within 200ms.

    ### Acceptance Criteria

    - [ ] ACC-001: Render time stays below 200ms.

    ### Scope

    #### Included

    - The widget component itself.

    #### Explicitly Out Of Scope

    - Mobile touch gestures.

    ### Task List

    #### Phase 100: Scaffolding

    - [x] Task 100.100: Create branch and package skeleton

    ## Progress

    ### Current Status

    **As of 2026-08-30**: free-form narrative.

    ### Updates

    #### 2026-08-30 16:47:59.981Z - Paused for review

    Free-form prose describing what happened in this update.
    """
)

#: A valid-frontmatter/H1, body-defective (missing ``### Task List``) document, for the
#: ACC-005 hand-created-broken-body sub-case -- a tier-3 shape, like ACC-002's letter (e).
_BROKEN_BODY_FRONTMATTER = """\
---
classification: null
created: '2026-08-30T10:00:00.000+02:00'
id: {id}
status: planning
type: feat
updated: '2026-08-30T10:00:00.000+02:00'
version: 1.0.0
---

"""
_BROKEN_BODY_PLAN = textwrap.dedent(
    """\
    # Feature: Hand-Created Broken Body

    ## Plan

    ### Overview

    Short description.

    ### Requirements

    - REQ-001: The widget must render within 200ms.

    ### Acceptance Criteria

    - [ ] ACC-001: Render time stays below 200ms.

    ### Scope

    #### Included

    - The widget component itself.

    #### Explicitly Out Of Scope

    - Mobile touch gestures.

    ## Progress

    ### Current Status

    **As of 2026-08-30**: free-form narrative.

    ### Updates

    #### 2026-08-30 16:47:59.981Z - Paused for review

    Free-form prose describing what happened in this update.
    """
)


class _FeatTimeoutTestCase(unittest.TestCase):
    """Shared fixture: a per-test temp ``SPECMGR_FEAT_DIR``, both feat cache stages reset.

    Per the feature's own Testability design note: the pre-existing ``tests/feat/`` suite
    isolates by a fresh temp ``SPECMGR_FEAT_DIR`` per test rather than calling the reset: this
    new, Phase 120 in-process suite additionally resets both cache stages in ``setUp``/
    ``tearDown`` (belt-and-braces -- a fresh temp dir alone already guarantees no path collision
    across tests, but an explicit reset keeps this suite's own discipline self-documenting and
    robust to a future change in path derivation).
    """

    def setUp(self) -> None:
        self.feat_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {FEAT_DIR_ENV_VAR: str(self.feat_root)}))
        cache_module.reset_feat_cache()
        cache_module.reset_feat_dirty_cache()

    def tearDown(self) -> None:
        cache_module.reset_feat_cache()
        cache_module.reset_feat_dirty_cache()

    def _row_for(self, folder_id: str):
        """The sole ``list_feat()`` row whose ``ref`` is ``folder_id`` (asserts exactly one)."""
        result_page = list_feat(max_results=100)
        rows = [row for row in result_page.results if row.ref == folder_id]
        self.assertEqual(len(rows), 1, f"expected exactly one list_feat row for {folder_id!r}")
        return rows[0]

    def _assert_clean_stage_warm(self, path: Path) -> None:
        """Assert ``path`` is already warm in the clean (full-parse) cache -- zero additional parse cost.

        ``read_feat`` legitimately re-raises a cached *failure* for a defective fixture document
        (one of :data:`CACHEABLE_ERROR_TYPES`) -- that is still a cache HIT (the stored exception,
        not a fresh parse), so it is caught here rather than treated as a warmth-check failure; the
        spy assertion below is what actually proves no re-parse happened, in either outcome.
        """
        with mock.patch.object(cache_module, "_parse", wraps=cache_module._parse) as spy:
            try:
                read_feat(path)
            except CACHEABLE_ERROR_TYPES:
                pass
        spy.assert_not_called()

    def _assert_dirty_stage_warm(self, path: Path) -> None:
        """Assert ``path`` is already warm in the dirty (frontmatter-stage) cache -- zero additional parse cost.

        See :meth:`_assert_clean_stage_warm`'s own docstring for why a cached failure is caught,
        not treated as a warmth-check failure.
        """
        with mock.patch.object(
            cache_module, "_parse_frontmatter_summary", wraps=cache_module._parse_frontmatter_summary
        ) as spy:
            try:
                read_feat_dirty(path)
            except CACHEABLE_ERROR_TYPES:
                pass
        spy.assert_not_called()


class TestAcc001ColdScanTiming(_FeatTimeoutTestCase):
    """ACC-001: the first ``list_feat`` call, fresh caches, returns ``total == 70`` in well under 5 s,
    with zero full body parses on the request path for any file (the parse-count seam on the
    clean-stage ``parse_fn``)."""

    def test_first_call_returns_total_70_under_5s_with_zero_full_parses(self) -> None:
        corpus: FixtureCorpus = generate_fixture_corpus(self.feat_root, num_healthy=57)
        self.assertEqual(corpus.total, 70)

        with mock.patch.object(cache_module, "_parse", wraps=cache_module._parse) as parse_spy:
            start = time.perf_counter()
            result = list_feat(max_results=100)
            elapsed = time.perf_counter() - start

        self.assertEqual(result.total, 70)
        self.assertLess(elapsed, 5.0, f"list_feat took {elapsed:.3f}s, expected well under 5s")
        # The request path must never invoke the clean-stage parse_fn -- the warmup does, by
        # design, but this seam is checked only across list_feat's own call above.
        parse_spy.assert_not_called()


class TestAcc002ThreeTierFailureVisibility(_FeatTimeoutTestCase):
    """ACC-002: a table-driven test over the (a)-(m) fixture shapes, asserting the three-tier
    contract (REQ-004) per letter, including convergence via an on-demand ``get_feat`` read."""

    def test_each_lettered_shape_follows_its_own_tier_contract(self) -> None:
        corpus = generate_fixture_corpus(self.feat_root, num_healthy=3)

        for letter in SHAPE_LETTERS:
            with self.subTest(letter=letter):
                folder_id = corpus.shape_ids[letter]
                pre = self._row_for(folder_id)

                if letter in _TIER1_LETTERS:
                    self._check_tier1(folder_id, pre)
                elif letter in _TIER2_LETTERS:
                    self._check_tier2(folder_id, pre)
                elif letter in _TIER3_LETTERS:
                    self._check_tier3(folder_id, pre, letter)
                else:
                    self._check_healthy(folder_id, pre, letter)

    def _check_tier1(self, folder_id: str, pre) -> None:
        """Tier 1: failed row from call one, byte-identical to ``get_feat``'s error, unconditionally."""
        self.assertEqual(pre.title, FAILED_TO_PARSE_MARKER)
        self.assertEqual(pre.status, FAILED_TO_PARSE_MARKER)
        self.assertIsNone(pre.id)
        self.assertTrue(pre.error)

        get_result = get_feat(folder_id)
        self.assertIsInstance(get_result, ParseFailureResult)
        self.assertEqual(pre.error, get_result.error)

        post = self._row_for(folder_id)
        self.assertEqual(post.error, get_result.error)

    def _check_tier2(self, folder_id: str, pre) -> None:
        """Tier 2: failed row from call one with dirty-stage text, converging to byte-identical."""
        self.assertEqual(pre.title, FAILED_TO_PARSE_MARKER)
        self.assertEqual(pre.status, FAILED_TO_PARSE_MARKER)
        self.assertTrue(pre.error)

        get_result = get_feat(folder_id)
        self.assertIsInstance(get_result, ParseFailureResult)
        # Byte-identity from call one is deliberately sacrificed for tier 2 (REQ-004): the
        # dirty-stage text differs until the clean stage has passed this file.
        self.assertNotEqual(pre.error, get_result.error)

        post = self._row_for(folder_id)
        self.assertEqual(post.error, get_result.error)

    def _check_tier3(self, folder_id: str, pre, letter: str) -> None:
        """Tier 3: transiently healthy pre-convergence, failed (byte-identical) post-convergence."""
        self.assertNotEqual(pre.title, FAILED_TO_PARSE_MARKER)
        self.assertNotEqual(pre.status, FAILED_TO_PARSE_MARKER)
        self.assertEqual(pre.id, folder_id)
        self.assertEqual(pre.status, "planning")
        self.assertEqual(pre.title, _EXPECTED_TITLE_BY_LETTER[letter])
        self.assertIsNone(pre.error)

        get_result = get_feat(folder_id)
        self.assertIsInstance(get_result, ParseFailureResult)

        post = self._row_for(folder_id)
        self.assertEqual(post.title, FAILED_TO_PARSE_MARKER)
        self.assertEqual(post.status, FAILED_TO_PARSE_MARKER)
        self.assertIsNone(post.id)
        self.assertEqual(post.error, get_result.error)

    def _check_healthy(self, folder_id: str, pre, letter: str) -> None:
        """Healthy in both states, correct id/title/status, unaffected by an on-demand clean read."""
        self.assertNotEqual(pre.title, FAILED_TO_PARSE_MARKER)
        self.assertEqual(pre.id, folder_id)
        self.assertEqual(pre.status, "planning")
        self.assertEqual(pre.title, _EXPECTED_TITLE_BY_LETTER[letter])
        self.assertIsNone(pre.error)

        get_result = get_feat(folder_id)
        self.assertIsInstance(get_result, FeatDocument)

        post = self._row_for(folder_id)
        self.assertEqual(post.id, pre.id)
        self.assertEqual(post.title, pre.title)
        self.assertEqual(post.status, pre.status)
        self.assertIsNone(post.error)


class TestAcc003ConvergenceAndGetFeatSurface(_FeatTimeoutTestCase):
    """ACC-003: once the warmup's full-parse phase has completed, ``list_feat``'s entire output is
    byte-identical to the still-untouched ``build_summaries`` reference implementation; also
    exercises ``get_feat``'s full surface against a cold miss and a warmed hit (REQ-006)."""

    def test_converged_output_is_byte_identical_to_the_build_summaries_reference(self) -> None:
        corpus = generate_fixture_corpus(self.feat_root, num_healthy=10)
        warmup_feat_caches()  # drives both phases synchronously -- every path now clean-cached

        actual = list_feat(max_results=100)

        paths = list(iter_feat_paths(feat_base_dir()))
        reference_summaries, reference_error_count = build_summaries(paths, read_feat, _to_summary, _to_failed_summary)
        reference = paginate(reference_summaries, *normalize_paging(100, 0), error_count=reference_error_count)

        self.assertEqual(actual.total, corpus.total)
        self.assertEqual(actual.total, reference.total)
        self.assertEqual(actual.error_count, reference.error_count)
        self.assertEqual(
            [row.model_dump() for row in actual.results],
            [row.model_dump() for row in reference.results],
        )

    def test_get_feat_full_surface_cold_miss_and_warm_hit_for_healthy_and_failing_documents(self) -> None:
        corpus = generate_fixture_corpus(self.feat_root, num_healthy=3)
        healthy_id = corpus.shape_ids["j"]
        failing_id = corpus.shape_ids["d"]  # tier-3: fails only at full parse

        # Cold miss (fresh caches from setUp): every read-mode surface, for both representative docs.
        cold_doc = get_feat(healthy_id)
        self.assertIsInstance(cold_doc, FeatDocument)
        cold_raw = get_feat(healthy_id, raw=True)
        self.assertIsInstance(cold_raw, str)
        cold_numbered = get_feat(healthy_id, raw=True, numbered=True, offset=1, limit=2)
        self.assertIsInstance(cold_numbered, str)

        cold_failing = get_feat(failing_id)
        self.assertIsInstance(cold_failing, ParseFailureResult)
        self.assertEqual(cold_failing.id, failing_id)
        self.assertTrue(cold_failing.error)

        # Warm hit: both documents are now clean-cached; the parse_fn must not be re-invoked, and
        # every surface's output must be unchanged (REQ-006's cache-transparency claim).
        with mock.patch.object(cache_module, "_parse", wraps=cache_module._parse) as parse_spy:
            warm_doc = get_feat(healthy_id)
            warm_raw = get_feat(healthy_id, raw=True)
            warm_numbered = get_feat(healthy_id, raw=True, numbered=True, offset=1, limit=2)
            warm_failing = get_feat(failing_id)

        parse_spy.assert_not_called()
        self.assertEqual(warm_doc, cold_doc)
        self.assertEqual(warm_raw, cold_raw)
        self.assertEqual(warm_numbered, cold_numbered)
        self.assertIsInstance(warm_failing, ParseFailureResult)
        self.assertEqual(warm_failing.error, cold_failing.error)
        self.assertEqual(warm_failing.id, cold_failing.id)


class TestAcc004CrashContainment(_FeatTimeoutTestCase):
    """ACC-004: an unexpected (non-parse) exception on one file during the warmup neither dies nor
    stalls it -- later files still warm, and subsequent ``list_feat`` calls are unaffected."""

    def test_unexpected_exception_on_one_file_does_not_stop_the_warmup_or_break_subsequent_list_feat(self) -> None:
        corpus = generate_fixture_corpus(self.feat_root, num_healthy=5)
        boom_path = corpus.shape_paths["j"]  # an arbitrary, otherwise-healthy path to fail on
        real_read_text = Path.read_text

        def _flaky_read_text(path_self: Path, *args: object, **kwargs: object) -> str:
            if path_self == boom_path:
                raise OSError("simulated unexpected failure warming this one file")
            return real_read_text(path_self, *args, **kwargs)

        with mock.patch.object(Path, "read_text", _flaky_read_text):
            result = warmup_feat_caches()  # must not raise

        self.assertGreater(result.frontmatter_phase.paths_warmed, 0)
        self.assertGreater(result.full_parse_phase.paths_warmed, 0)

        # Later files still warmed: every path besides boom_path is clean-cached.
        for letter, path in corpus.shape_paths.items():
            if path == boom_path:
                continue
            with self.subTest(letter=letter):
                self._assert_clean_stage_warm(path)

        # boom_path itself never got a cache entry (the OSError is not a cacheable failure type).
        self.assertNotIn(boom_path.resolve(), cache_module._cache._entries)  # pylint: disable=protected-access

        # Subsequent list_feat calls are unaffected: correct total, no uncaught exception, and
        # boom_path (no longer mocked) reads normally again.
        listed = list_feat(max_results=100)
        self.assertEqual(listed.total, corpus.total)


class TestAcc005WritePathConsistency(_FeatTimeoutTestCase):
    """ACC-005: the write paths keep both cache stages coherent, plus the warmup-snapshot and
    hand-created-broken-body convergence sub-cases."""

    def test_create_feat_warms_both_stages_and_list_feat_reflects_it_immediately(self) -> None:
        created = create_feat(_MINIMAL_BODY.format(title="Create Warms Both"), id="feat-900-ww-create")
        path = feat_base_dir() / created.id / README_FILENAME

        self._assert_clean_stage_warm(path)
        self._assert_dirty_stage_warm(path)

        listed = list_feat(max_results=100)
        self.assertIn(created.id, {row.id for row in listed.results})

    def test_generic_update_warms_both_stages(self) -> None:
        created = create_feat(_MINIMAL_BODY.format(title="Update Warms Both"), id="feat-901-ww-update")
        path = feat_base_dir() / created.id / README_FILENAME
        new_body = _MINIMAL_BODY.format(title="Update Warms Both (updated)")

        update(id=created.id, type="feat", content=new_body)

        self._assert_clean_stage_warm(path)
        self._assert_dirty_stage_warm(path)
        listed = list_feat(max_results=100)
        row = next(row for row in listed.results if row.id == created.id)
        self.assertEqual(row.title, "Update Warms Both (updated)")

    def test_generic_set_status_warms_both_stages(self) -> None:
        created = create_feat(_MINIMAL_BODY.format(title="Set Status Warms Both"), id="feat-902-ww-set-status")
        path = feat_base_dir() / created.id / README_FILENAME

        set_status(id=created.id, type="feat", status="progress")

        self._assert_clean_stage_warm(path)
        self._assert_dirty_stage_warm(path)
        listed = list_feat(max_results=100)
        row = next(row for row in listed.results if row.id == created.id)
        self.assertEqual(row.status, "progress")

    def test_generic_set_classification_warms_both_stages(self) -> None:
        created = create_feat(
            _MINIMAL_BODY.format(title="Set Classification Warms Both"), id="feat-903-ww-set-classification"
        )
        path = feat_base_dir() / created.id / README_FILENAME

        set_classification(id=created.id, type="feat", classification="internal")

        self._assert_clean_stage_warm(path)
        self._assert_dirty_stage_warm(path)
        listed = list_feat(max_results=100)
        self.assertIn(created.id, {row.id for row in listed.results})

    def test_generic_delete_invalidates_both_stages(self) -> None:
        created = create_feat(_MINIMAL_BODY.format(title="Delete Invalidates Both"), id="feat-904-ww-delete")
        path = feat_base_dir() / created.id / README_FILENAME

        deleted = delete(id=created.id, type="feat")

        self.assertEqual(deleted, str(path.parent))
        self.assertNotIn(path.resolve(), cache_module._cache._entries)  # pylint: disable=protected-access
        self.assertNotIn(path.resolve(), cache_module._dirty_cache._entries)  # pylint: disable=protected-access
        listed = list_feat(max_results=100)
        self.assertNotIn(created.id, {row.id for row in listed.results})

    def test_set_feat_id_moves_both_stages(self) -> None:
        """``set_feat_id`` *moves* (not re-warms) both stages' entries from the old path to the
        new one (``_cache.py``'s own docstring: ``set_feat_id`` always rewrites ``id``/``updated``
        before writing ``new_path``, so the moved entry's stored hash is guaranteed to mismatch
        ``new_path``'s real content on the very next read -- a harmless, self-healing cache miss
        that reparses once, not a "zero additional parse cost" warm hit like create/update/
        set_status/set_classification's own write-path warming). The behavioral assertion here is
        the move itself (the old key is gone from both stages) plus correct content on the very
        next read and an immediately-consistent ``list_feat``."""
        created = create_feat(_MINIMAL_BODY.format(title="Set Feat Id Moves Both"), id="feat-905-ww-move-old")
        old_path = feat_base_dir() / created.id / README_FILENAME

        set_feat_id(created.id, "feat-905-ww-move-new")

        new_path = feat_base_dir() / "feat-905-ww-move-new" / README_FILENAME
        self.assertNotIn(old_path.resolve(), cache_module._cache._entries)  # pylint: disable=protected-access
        self.assertNotIn(old_path.resolve(), cache_module._dirty_cache._entries)  # pylint: disable=protected-access
        self.assertIn(new_path.resolve(), cache_module._cache._entries)  # pylint: disable=protected-access
        self.assertIn(new_path.resolve(), cache_module._dirty_cache._entries)  # pylint: disable=protected-access
        self.assertEqual(read_feat(new_path).frontmatter.id, "feat-905-ww-move-new")

        listed = list_feat(max_results=100)
        ids = {row.id for row in listed.results}
        self.assertIn("feat-905-ww-move-new", ids)
        self.assertNotIn(created.id, ids)

    def test_folder_created_after_warmup_snapshot_still_yields_complete_total_and_correct_row(self) -> None:
        corpus = generate_fixture_corpus(self.feat_root, num_healthy=3)
        warmup_feat_caches()  # snapshot taken; the new folder below does not exist yet

        new_id = "feat-906-ww-after-snapshot"
        full_text = _BROKEN_BODY_FRONTMATTER.format(id=new_id) + _MINIMAL_BODY.format(title="After Snapshot")
        write_feat_folder(self.feat_root, new_id, full_text)

        listed = list_feat(max_results=100)
        self.assertEqual(listed.total, corpus.total + 1)
        row = next(row for row in listed.results if row.ref == new_id)
        self.assertEqual(row.id, new_id)
        self.assertNotEqual(row.title, FAILED_TO_PARSE_MARKER)

    def test_hand_created_broken_body_folder_stays_healthy_until_next_clean_read_then_converges(self) -> None:
        generate_fixture_corpus(self.feat_root, num_healthy=3)
        warmup_feat_caches()  # snapshot taken; the new folder below does not exist yet

        new_id = "feat-907-ww-broken-body-after-snapshot"
        full_text = _BROKEN_BODY_FRONTMATTER.format(id=new_id) + _BROKEN_BODY_PLAN  # valid FM+H1, missing Task List
        write_feat_folder(self.feat_root, new_id, full_text)

        pre = self._row_for(new_id)
        self.assertNotEqual(pre.title, FAILED_TO_PARSE_MARKER)  # stays healthy (tier-3 transient)
        self.assertEqual(pre.id, new_id)

        get_result = get_feat(new_id)  # the on-demand clean read that triggers convergence
        self.assertIsInstance(get_result, ParseFailureResult)

        post = self._row_for(new_id)
        self.assertEqual(post.title, FAILED_TO_PARSE_MARKER)
        self.assertEqual(post.error, get_result.error)


if __name__ == "__main__":
    unittest.main()
