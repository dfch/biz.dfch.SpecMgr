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

"""Tool-level tests for ``find_related`` (feat-134, Phase 3, Task 3.1).

Drives the real ``find_related`` tool function against a temp corpus seeded with
the deterministic :class:`~._similarity_helpers.FakeProvider`, so every expected
cosine is hand-computable. Covers ACC-001 (ranked hits, self-exclusion, marker
rows, the default non-``adr`` set), ACC-003 (the tool still registers and returns
the structured unavailable result with the backend missing), ACC-004 (the disabled
flag), ACC-005/ACC-006 (cache reuse / invalidation), ACC-007 (``adr`` rejection),
ACC-009 (model-load failure), ACC-011 (``delete`` invalidation + ``set_feat_id``
move), and ACC-015 (the error contract: ``ValueError`` before filesystem access,
``ReqNotFoundError`` for a missing source).
"""

from __future__ import annotations

import asyncio
import math
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from biz.dfch.specmgr.general.models import (
    REASON_BACKEND_UNAVAILABLE,
    REASON_DISABLED,
    SimilarityHit,
    SimilarityUnavailableResult,
)
from biz.dfch.specmgr.general.tools import _embedding_cache as embedding_cache_module
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._listing import FAILED_TO_PARSE_MARKER
from biz.dfch.specmgr.general.tools._similarity_search import make_embed_fn
from biz.dfch.specmgr.general.tools._embedding_cache import read_embedding
from biz.dfch.specmgr.general.tools.delete import delete
from biz.dfch.specmgr.general.tools.find_related import find_related
from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError

from ._similarity_helpers import (
    _FEAT_MINIMAL_BODY,
    block_fastembed_import,
    fail_fastembed_model_load,
    reset_default_provider,
    SimilarityTestCase,
)

_MISSING_UUID = "00000000-0000-0000-0000-000000000000"

#: A valid feat-NNN-slug for the ``set_feat_id`` rename target.
_RENAMED_FEAT_ID = "feat-134-renamed"


class TestFindRelatedRegistration(unittest.TestCase):
    """ACC-003 (registration half): the tool is registered on the live ``mcp`` server regardless of the extra."""

    @classmethod
    def setUpClass(cls) -> None:
        from biz.dfch.specmgr.server import mcp

        cls._tools = asyncio.run(mcp.list_tools())

    def test_find_related_is_registered(self) -> None:
        matching = [tool for tool in self._tools if tool.name == "find_related"]

        self.assertEqual(len(matching), 1)

    def test_find_related_type_enum_excludes_adr(self) -> None:
        tool = [t for t in self._tools if t.name == "find_related"][0]

        type_prop = tool.input_schema["properties"]["type"]

        self.assertNotIn("adr", type_prop["enum"])
        self.assertIn("req", type_prop["enum"])
        self.assertEqual(len(type_prop["enum"]), 12)


class _RankedCorpusMixin:
    """Seeds the source + three ranked candidates (+ optionally the broken doc) used by several tests."""

    def _seed_ranked_corpus(self) -> tuple[Any, Any, Any, Any]:
        source = self.seed_req("Source Doc", "alpha alpha alpha")
        first = self.seed_req("First Doc", "alpha alpha beta")  # 2/sqrt(5) ~ 0.894
        second = self.seed_req("Second Doc", "alpha beta")  # 1/sqrt(2) ~ 0.707
        third = self.seed_req("Third Doc", "alpha beta beta gamma")  # 1/sqrt(6) ~ 0.408
        return source, first, second, third


class TestFindRelatedRanking(SimilarityTestCase, _RankedCorpusMixin):
    """ACC-001: ranked ``(type, id, title, status, path, score)`` hits, source excluded, marker rows."""

    def test_ranks_by_cosine_excludes_source_and_marks_unparseable(self) -> None:
        source, first, second, third = self._seed_ranked_corpus()
        self.seed_unparseable_req()
        self.install_fake()

        hits = find_related(type="req", id=source.id)

        self.assertIsInstance(hits, list)
        self.assertNotIsInstance(hits, SimilarityUnavailableResult)
        for hit in hits:
            self.assertIsInstance(hit, SimilarityHit)
        self.assertEqual([hit.title for hit in hits], ["First Doc", "Second Doc", "Third Doc", FAILED_TO_PARSE_MARKER])
        self.assertNotIn("Source Doc", [hit.title for hit in hits])  # self-exclusion
        self.assertAlmostEqual(hits[0].score, 2.0 / math.sqrt(5.0), places=6)
        self.assertAlmostEqual(hits[1].score, 1.0 / math.sqrt(2.0), places=6)
        self.assertAlmostEqual(hits[2].score, 1.0 / math.sqrt(6.0), places=6)
        self.assertAlmostEqual(hits[3].score, 0.0, places=6)

    def test_hit_row_carries_type_id_status_and_resolved_path(self) -> None:
        source, first, _second, _third = self._seed_ranked_corpus()
        self.install_fake()

        hits = find_related(type="req", id=source.id)

        top = hits[0]
        self.assertEqual(top.type, "req")
        self.assertEqual(top.id, first.id)
        self.assertEqual(top.status, "draft")
        self.assertEqual(top.path, str(self.path_for_id("req", first.id).resolve()))
        self.assertIsInstance(top.score, float)

    def test_unparseable_candidate_is_a_marker_row_with_none_id(self) -> None:
        source = self.seed_req("Source Doc", "alpha alpha alpha")
        self.seed_unparseable_req()
        self.install_fake()

        hits = find_related(type="req", id=source.id)

        marker = [hit for hit in hits if hit.title == FAILED_TO_PARSE_MARKER]
        self.assertEqual(len(marker), 1)
        self.assertIsNone(marker[0].id)
        self.assertEqual(marker[0].status, FAILED_TO_PARSE_MARKER)
        self.assertTrue(Path(marker[0].path).exists())

    def test_default_target_set_spans_whole_body_domains_and_excludes_adr(self) -> None:
        source = self.seed_req("Source Doc", "alpha alpha alpha")
        self.seed_gol("Gol Doc", "alpha")
        self.seed_dec("Dec Doc", "alpha")
        self.seed_feat(_FEAT_MINIMAL_BODY)
        self.install_fake()

        hits = find_related(type="req", id=source.id)

        types = {hit.type for hit in hits}
        self.assertEqual(types, {"gol", "dec", "feat"})  # the source req is excluded
        self.assertNotIn("adr", types)

    def test_target_types_restricts_the_candidate_set(self) -> None:
        source = self.seed_req("Source Doc", "alpha alpha alpha")
        self.seed_req("Other Req", "alpha")
        self.seed_gol("Gol Doc", "alpha")
        self.install_fake()

        only_req = find_related(type="req", id=source.id, target_types=["req"])
        default = find_related(type="req", id=source.id)

        self.assertEqual({hit.type for hit in only_req}, {"req"})
        self.assertIn("gol", {hit.type for hit in default})


class TestFindRelatedBoundsAndFilters(SimilarityTestCase, _RankedCorpusMixin):
    """ACC-001/ACC-015: ``top_k`` and ``min_score`` shape the result set."""

    def test_top_k_limits_the_result_count(self) -> None:
        source, _first, _second, _third = self._seed_ranked_corpus()
        self.install_fake()

        hits = find_related(type="req", id=source.id, top_k=2)

        self.assertEqual(len(hits), 2)
        self.assertEqual([hit.title for hit in hits], ["First Doc", "Second Doc"])

    def test_min_score_filters_below_the_threshold(self) -> None:
        source, _first, _second, _third = self._seed_ranked_corpus()
        self.install_fake()

        above_half = find_related(type="req", id=source.id, min_score=0.5)
        above_eight_tenths = find_related(type="req", id=source.id, min_score=0.8)

        self.assertEqual([hit.title for hit in above_half], ["First Doc", "Second Doc"])
        self.assertEqual([hit.title for hit in above_eight_tenths], ["First Doc"])


class TestFindRelatedAvailability(SimilarityTestCase):
    """ACC-003/ACC-004/ACC-009: the structured unavailable result, never a raise."""

    def test_disabled_flag_returns_unavailable_even_with_the_extra_installed(self) -> None:
        source = self.seed_req("Source Doc", "alpha")
        self.install_fake()  # the "extra" is present (a provider is installable)
        self.set_disabled("1")

        result = find_related(type="req", id=source.id)

        self.assertIsInstance(result, SimilarityUnavailableResult)
        self.assertFalse(result.available)
        self.assertEqual(result.reason, REASON_DISABLED)

    def test_backend_missing_returns_unavailable_and_never_raises(self) -> None:
        source = self.seed_req("Source Doc", "alpha")
        reset_default_provider()

        with block_fastembed_import():
            result = find_related(type="req", id=source.id)

        self.assertIsInstance(result, SimilarityUnavailableResult)
        self.assertFalse(result.available)
        self.assertEqual(result.reason, REASON_BACKEND_UNAVAILABLE)

    def test_model_load_failure_returns_unavailable_and_never_raises(self) -> None:
        source = self.seed_req("Source Doc", "alpha")
        reset_default_provider()

        with fail_fastembed_model_load():
            result = find_related(type="req", id=source.id)

        self.assertIsInstance(result, SimilarityUnavailableResult)
        self.assertEqual(result.reason, REASON_BACKEND_UNAVAILABLE)

    def test_backend_missing_returns_unavailable_even_with_invalid_arguments(self) -> None:
        # REQ-003's normative ordering (feat-134, Phase 6, Task 6.2): a
        # disabled/backend-missing environment short-circuits **before**
        # any argument validation -- every invalid-argument shape below
        # returns the structured unavailable result instead of the
        # ValueError (or the domain's XNotFoundError, for the missing
        # source) it would raise in an available environment.
        source = self.seed_req("Source Doc", "alpha")
        reset_default_provider()

        with block_fastembed_import():
            with self.subTest(top_k=0):
                result = find_related(type="req", id=source.id, top_k=0)  # outside 1..100 -> ValueError when available
                self.assertIsInstance(result, SimilarityUnavailableResult)
                self.assertFalse(result.available)
                self.assertEqual(result.reason, REASON_BACKEND_UNAVAILABLE)
            with self.subTest(target_types=["adr"]):
                # structurally excluded -> ValueError when available
                result = find_related(type="req", id=source.id, target_types=["adr"])
                self.assertIsInstance(result, SimilarityUnavailableResult)
                self.assertFalse(result.available)
                self.assertEqual(result.reason, REASON_BACKEND_UNAVAILABLE)
            with self.subTest(type="bogus"):
                result = find_related(type="bogus", id=source.id)  # unknown type -> ValueError when available
                self.assertIsInstance(result, SimilarityUnavailableResult)
                self.assertFalse(result.available)
                self.assertEqual(result.reason, REASON_BACKEND_UNAVAILABLE)
            with self.subTest(id=_MISSING_UUID):
                result = find_related(type="req", id=_MISSING_UUID)  # missing source -> ReqNotFoundError when available
                self.assertIsInstance(result, SimilarityUnavailableResult)
                self.assertFalse(result.available)
                self.assertEqual(result.reason, REASON_BACKEND_UNAVAILABLE)


class TestFindRelatedCaching(SimilarityTestCase, _RankedCorpusMixin):
    """ACC-005/ACC-006: unchanged documents reuse the cache; a content change re-embeds exactly once."""

    def test_repeated_call_reuses_cached_embeddings(self) -> None:
        source, _first, _second, _third = self._seed_ranked_corpus()
        fake = self.install_fake()

        find_related(type="req", id=source.id)
        cold = fake.embed_calls
        self.assertEqual(cold, 4)  # the source + three candidates, each embedded once

        find_related(type="req", id=source.id)

        self.assertEqual(fake.embed_calls, cold)  # the warm walk re-embeds nothing

    def test_content_change_re_embeds_exactly_the_changed_document(self) -> None:
        source, first, _second, _third = self._seed_ranked_corpus()
        fake = self.install_fake()

        find_related(type="req", id=source.id)
        cold = fake.embed_calls

        path = self.path_for_id("req", first.id)
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("alpha alpha beta", "gamma gamma gamma"), encoding="utf-8")

        find_related(type="req", id=source.id)

        self.assertEqual(fake.embed_calls, cold + 1)


class TestFindRelatedErrorContract(SimilarityTestCase):
    """ACC-007/ACC-015: ``ValueError`` before filesystem access; ``ReqNotFoundError`` for a missing source."""

    def _nonexistent_docs_dir(self) -> Any:
        missing = Path(self.enterContext(tempfile.TemporaryDirectory())) / "does-not-exist"
        return mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(missing)})

    def test_top_k_out_of_range_rejected_before_filesystem_access(self) -> None:
        source = self.seed_req("Source Doc", "alpha")
        self.install_fake()

        with self._nonexistent_docs_dir():
            for bad_top_k in (0, 101, -1):
                with self.subTest(top_k=bad_top_k):
                    with self.assertRaises(ValueError):
                        find_related(type="req", id=source.id, top_k=bad_top_k)

    def test_min_score_out_of_range_rejected(self) -> None:
        source = self.seed_req("Source Doc", "alpha")
        self.install_fake()

        for bad_min_score in (-1.5, 1.5):
            with self.subTest(min_score=bad_min_score):
                with self.assertRaises(ValueError):
                    find_related(type="req", id=source.id, min_score=bad_min_score)

    def test_adr_rejected_as_source_type(self) -> None:
        self.seed_req("Source Doc", "alpha")
        self.install_fake()

        with self.assertRaises(ValueError):
            find_related(type="adr", id=_MISSING_UUID)  # type: ignore[arg-type]

    def test_adr_rejected_as_target_type(self) -> None:
        source = self.seed_req("Source Doc", "alpha")
        self.install_fake()

        with self.assertRaises(ValueError):
            find_related(type="req", id=source.id, target_types=["adr"])

    def test_unknown_target_type_rejected_before_filesystem_access(self) -> None:
        source = self.seed_req("Source Doc", "alpha")
        self.install_fake()

        with self._nonexistent_docs_dir():
            with self.assertRaises(ValueError):
                find_related(type="req", id=source.id, target_types=["bogus"])

    def test_missing_source_raises_req_not_found(self) -> None:
        self.seed_req("Some Doc", "alpha")
        self.install_fake()

        with self.assertRaises(ReqNotFoundError):
            find_related(type="req", id=_MISSING_UUID)


class TestFindRelatedCacheLifecycle(SimilarityTestCase):
    """ACC-011: ``delete`` invalidates the deleted entry (and only it); ``set_feat_id`` moves the entry."""

    def test_delete_invalidates_only_the_deleted_embedding_entry(self) -> None:
        doc_a = self.seed_req("Doc A", "alpha")
        doc_b = self.seed_req("Doc B", "beta")
        fake = self.install_fake()
        path_a = self.path_for_id("req", doc_a.id)
        path_b = self.path_for_id("req", doc_b.id)
        read_embedding("req", path_a, make_embed_fn(fake, "req"))
        read_embedding("req", path_b, make_embed_fn(fake, "req"))
        entries = embedding_cache_module._cache._entries  # pylint: disable=protected-access
        key_a = ("req", path_a.resolve())
        key_b = ("req", path_b.resolve())
        self.assertIn(key_a, entries)
        self.assertIn(key_b, entries)

        delete(id=doc_a.id, type="req")

        self.assertNotIn(key_a, entries)
        self.assertIn(key_b, entries)  # the sibling entry is untouched

    def test_set_feat_id_moves_the_embedding_entry(self) -> None:
        feat_fm = self.seed_feat(_FEAT_MINIMAL_BODY)
        old_id = feat_fm.id
        fake = self.install_fake()
        old_path = self.feat_dir / old_id / "README.md"
        read_embedding("feat", old_path, make_embed_fn(fake, "feat"))
        entries = embedding_cache_module._cache._entries  # pylint: disable=protected-access
        old_key = ("feat", old_path.resolve())
        self.assertIn(old_key, entries)

        from biz.dfch.specmgr.feat.tools.set_feat_id import set_feat_id

        set_feat_id(id=old_id, new_id=_RENAMED_FEAT_ID)

        new_path = self.feat_dir / _RENAMED_FEAT_ID / "README.md"
        new_key = ("feat", new_path.resolve())
        self.assertNotIn(old_key, entries)
        self.assertIn(new_key, entries)


if __name__ == "__main__":
    unittest.main()
