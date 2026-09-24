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

"""Tool-level tests for ``find_similar_text`` (feat-134, Phase 3, Task 3.2).

Drives the real ``find_similar_text`` tool against a temp corpus seeded with the
deterministic :class:`~._similarity_helpers.FakeProvider`. Covers ACC-002 (ranked
hits for a free-text query, the query going through ``embed_query``, the same
hit shape incl. marker rows), ACC-003 (registration + backend-missing
unavailable result), ACC-004 (the disabled flag), ACC-009 (model-load failure),
and ACC-015 (the error contract: ``ValueError`` for bad ``target_types``/``top_k``/
``min_score`` before filesystem access).
"""

from __future__ import annotations

import asyncio
import math
import tempfile
import textwrap
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
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._embedding_cache import _cache as embedding_cache_singleton
from biz.dfch.specmgr.general.tools._listing import FAILED_TO_PARSE_MARKER
from biz.dfch.specmgr.general.tools._similarity_search import warmup_similarity_cache
from biz.dfch.specmgr.general.tools.find_similar_text import find_similar_text

from ._similarity_helpers import (
    block_fastembed_import,
    fail_fastembed_model_load,
    reset_default_provider,
    SimilarityTestCase,
)


class TestFindSimilarTextRegistration(unittest.TestCase):
    """ACC-003 (registration half): the tool is registered on the live ``mcp`` server."""

    @classmethod
    def setUpClass(cls) -> None:
        from biz.dfch.specmgr.server import mcp

        cls._tools = asyncio.run(mcp.list_tools())

    def test_find_similar_text_is_registered(self) -> None:
        matching = [tool for tool in self._tools if tool.name == "find_similar_text"]

        self.assertEqual(len(matching), 1)


class TestFindSimilarTextRanking(SimilarityTestCase):
    """ACC-002: ranked hits for a free-text query; the query goes through ``embed_query``."""

    def test_ranks_by_query_similarity_and_uses_embed_query(self) -> None:
        # Neutral (vocabulary-free) titles: the title is deliberately double-weighted in the
        # embedding text, so a titled "Alpha Doc" would add an extra "alpha" and skew the math.
        self.seed_req("First Doc", "alpha alpha beta")  # 2/sqrt(5) ~ 0.894 against an "alpha" query
        self.seed_req("Second Doc", "beta gamma")  # 0.0 against an "alpha" query
        self.seed_unparseable_req()  # 0.0 (zero vector), marker row
        fake = self.install_fake()

        hits = find_similar_text(query="alpha")

        self.assertIsInstance(hits, list)
        for hit in hits:
            self.assertIsInstance(hit, SimilarityHit)
        self.assertEqual([hit.title for hit in hits], ["First Doc", "Second Doc", FAILED_TO_PARSE_MARKER])
        self.assertAlmostEqual(hits[0].score, 2.0 / math.sqrt(5.0), places=6)
        self.assertAlmostEqual(hits[1].score, 0.0, places=6)
        self.assertAlmostEqual(hits[2].score, 0.0, places=6)
        self.assertEqual(fake.embed_query_calls, 1)
        self.assertEqual(fake.embed_query_inputs, ["alpha"])  # the raw query, via embed_query
        self.assertEqual(fake.embed_calls, 3)  # the three document-side candidates
        self.assertIsNone(hits[2].id)  # the unparseable candidate is a marker row

    def test_target_types_restricts_the_candidate_set(self) -> None:
        self.seed_req("First Req", "alpha")
        self.seed_gol("First Goal", "alpha")
        self.install_fake()

        only_req = find_similar_text(query="alpha", target_types=["req"])
        default = find_similar_text(query="alpha")

        self.assertEqual({hit.type for hit in only_req}, {"req"})
        self.assertIn("gol", {hit.type for hit in default})

    def test_top_k_and_min_score_shape_the_results(self) -> None:
        self.seed_req("First Doc", "alpha alpha beta")  # 0.894
        self.seed_req("Mid Doc", "alpha beta")  # 0.707
        self.seed_req("Low Doc", "beta gamma")  # 0.0
        self.install_fake()

        top_one = find_similar_text(query="alpha", top_k=1)
        above_half = find_similar_text(query="alpha", min_score=0.5)
        at_zero = find_similar_text(query="alpha", min_score=0.0)

        self.assertEqual([hit.title for hit in top_one], ["First Doc"])
        self.assertEqual([hit.title for hit in above_half], ["First Doc", "Mid Doc"])
        self.assertEqual(len(at_zero), 3)  # 0.0 is inclusive: the zero-score doc is kept


class TestFindSimilarTextAvailability(SimilarityTestCase):
    """ACC-003/ACC-004/ACC-009: the structured unavailable result, never a raise."""

    def test_disabled_flag_returns_unavailable(self) -> None:
        self.seed_req("Alpha Doc", "alpha")
        self.install_fake()
        self.set_disabled("1")

        result = find_similar_text(query="alpha")

        self.assertIsInstance(result, SimilarityUnavailableResult)
        self.assertFalse(result.available)
        self.assertEqual(result.reason, REASON_DISABLED)

    def test_backend_missing_returns_unavailable_and_never_raises(self) -> None:
        self.seed_req("Alpha Doc", "alpha")
        reset_default_provider()

        with block_fastembed_import():
            result = find_similar_text(query="alpha")

        self.assertIsInstance(result, SimilarityUnavailableResult)
        self.assertEqual(result.reason, REASON_BACKEND_UNAVAILABLE)

    def test_model_load_failure_returns_unavailable_and_never_raises(self) -> None:
        self.seed_req("Alpha Doc", "alpha")
        reset_default_provider()

        with fail_fastembed_model_load():
            result = find_similar_text(query="alpha")

        self.assertIsInstance(result, SimilarityUnavailableResult)
        self.assertEqual(result.reason, REASON_BACKEND_UNAVAILABLE)

    def test_backend_missing_returns_unavailable_even_with_invalid_arguments(self) -> None:
        # REQ-003's normative ordering (feat-134, Phase 6, Task 6.2): a
        # disabled/backend-missing environment short-circuits **before**
        # any argument validation -- every invalid-argument shape below
        # returns the structured unavailable result instead of the
        # ValueError it would raise in an available environment.
        reset_default_provider()

        with block_fastembed_import():
            with self.subTest(top_k=0):
                result = find_similar_text(query="alpha", top_k=0)  # outside 1..100 -> ValueError when available
                self.assertIsInstance(result, SimilarityUnavailableResult)
                self.assertFalse(result.available)
                self.assertEqual(result.reason, REASON_BACKEND_UNAVAILABLE)
            with self.subTest(target_types=["adr"]):
                # structurally excluded -> ValueError when available
                result = find_similar_text(query="alpha", target_types=["adr"])
                self.assertIsInstance(result, SimilarityUnavailableResult)
                self.assertFalse(result.available)
                self.assertEqual(result.reason, REASON_BACKEND_UNAVAILABLE)
            with self.subTest(min_score=1.5):
                result = find_similar_text(query="alpha", min_score=1.5)  # outside [-1, 1] -> ValueError when available
                self.assertIsInstance(result, SimilarityUnavailableResult)
                self.assertFalse(result.available)
                self.assertEqual(result.reason, REASON_BACKEND_UNAVAILABLE)


class TestFindSimilarTextErrorContract(SimilarityTestCase):
    """ACC-015: bad ``target_types``/``top_k``/``min_score`` are a ``ValueError`` before filesystem access."""

    def _nonexistent_docs_dir(self) -> Any:
        missing = Path(self.enterContext(tempfile.TemporaryDirectory())) / "does-not-exist"
        return mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(missing)})

    def test_top_k_out_of_range_rejected_before_filesystem_access(self) -> None:
        self.seed_req("Alpha Doc", "alpha")
        self.install_fake()

        with self._nonexistent_docs_dir():
            for bad_top_k in (0, 101, -1):
                with self.subTest(top_k=bad_top_k):
                    with self.assertRaises(ValueError):
                        find_similar_text(query="alpha", top_k=bad_top_k)

    def test_min_score_out_of_range_rejected(self) -> None:
        self.seed_req("Alpha Doc", "alpha")
        self.install_fake()

        for bad_min_score in (-1.5, 1.5):
            with self.subTest(min_score=bad_min_score):
                with self.assertRaises(ValueError):
                    find_similar_text(query="alpha", min_score=bad_min_score)

    def test_adr_target_rejected_before_filesystem_access(self) -> None:
        self.seed_req("Alpha Doc", "alpha")
        self.install_fake()

        with self._nonexistent_docs_dir():
            with self.assertRaises(ValueError):
                find_similar_text(query="alpha", target_types=["adr"])

    def test_unknown_target_rejected_before_filesystem_access(self) -> None:
        self.seed_req("Alpha Doc", "alpha")
        self.install_fake()

        with self._nonexistent_docs_dir():
            with self.assertRaises(ValueError):
                find_similar_text(query="alpha", target_types=["bogus"])


class TestSetextH1EndToEnd(SimilarityTestCase):
    """ACC-016: a parseable setext-H1 document yields the correct row and never breaks the corpus walk.

    The end-to-end regression for the Phase 6 setext fix: a ``req``
    document whose H1 uses setext syntax (``Title`` over ``===``) is
    parseable by the domain parser (markdown-it emits the same ``h1``
    token) -- before the fix, the ATX-only title scan returned ``None``
    for it and the ``_similarity_corpus`` assert crashed every
    ``find_similar_text``/``find_related`` call and aborted the startup
    warmup mid-corpus.
    """

    _SETEXT_REQ_BODY = textwrap.dedent(
        """\
        Setext Titled Requirement
        =========================

        WHILE the engine is running, THE temperature must be a maximum of 80 °C.

        ## Description

        alpha alpha beta

        ## Characteristics

        1. Safety

        ## Level

        MUST

        ## Source

        The International Safety Board Association (TISBA)
        """
    )

    def _seed_setext_req(self) -> Any:
        from biz.dfch.specmgr.req.tools.create_req import create_req

        return create_req(self._SETEXT_REQ_BODY)

    def test_find_similar_text_yields_the_setext_title_id_and_status(self) -> None:
        fm = self._seed_setext_req()
        self.seed_req("Second Doc", "gamma")
        self.install_fake()

        hits = find_similar_text(query="alpha")

        top = hits[0]
        self.assertEqual(top.type, "req")
        self.assertEqual(top.id, fm.id)
        self.assertEqual(top.title, "Setext Titled Requirement")
        self.assertEqual(top.status, "draft")

    def test_warmup_completes_the_full_corpus_with_a_setext_doc(self) -> None:
        self._seed_setext_req()
        self.seed_req("Second Doc", "gamma")
        fake = self.install_fake()

        warmup_similarity_cache()  # must complete the full corpus, not abort mid-walk

        self.assertEqual(fake.embed_calls, 2)  # every corpus document embedded
        stored_titles = {entry[2].title for entry in embedding_cache_singleton._entries.values()}
        self.assertEqual(stored_titles, {"Setext Titled Requirement", "Second Doc"})


if __name__ == "__main__":
    unittest.main()
