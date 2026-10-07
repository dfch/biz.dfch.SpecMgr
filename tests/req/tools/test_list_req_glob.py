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

"""Tests for the ``list_req`` tool's own optional ``glob`` parameter (feat-200-list, GitHub issue #200,
Phase 110: REQ-002/REQ-004/REQ-005, plus the plan's named example additions ACC-002/ACC-004/ACC-005).

Per the feature's own plan, the corpus is a small, hand-built set of files in a per-test temp
directory pointed at by ``SPECMGR_DOCS_DIR`` -- two healthy requirements sharing the known
``deadbeef-*`` UUID prefix (so the ACC-004 paging test has N = 2 matches), one healthy
requirement with a different (``cafe...``) prefix, and one broken file -- written directly to
disk (bypassing ``create_req``/the tool layer, which would assign random UUIDs the filter could
not be tested against deterministically). The ``req`` cache is reset in ``setUp``/``tearDown``
(the request path is cache-sensitive; a fresh temp directory alone already guarantees no
cross-test path collision, but the explicit reset keeps this module's own discipline
self-documenting).
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import PagedResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.req.models.v1 import ReqSummary
from biz.dfch.specmgr.req.tools import _cache as cache_module
from biz.dfch.specmgr.req.tools.list_req import list_req

#: The corpus's own two healthy (shared ``deadbeef-*`` prefix), one non-matching (``cafe...``
#: prefix), and one broken file ids.
_DEAD_IDS: tuple[str, ...] = ("deadbeef-0000-4000-8000-000000000001", "deadbeef-0000-4000-8000-000000000002")
_CAFE_ID = "cafebab0-1234-4567-89ab-cdef01234567"
_BROKEN_REF = "broken"

#: The ACC-002 known-UUID: a real id from this repo's own live corpus, read off
#: ``docs/req/req-10b78b36-abad-4bfe-9281-f75677ff7d09-verification-case-record-document-management.md``.
_DOCS_REQ_ID = "10b78b36-abad-4bfe-9281-f75677ff7d09"

#: The total healthy file count (and thus the unfiltered ``total`` minus the one broken file).
_HEALTHY_COUNT = len(_DEAD_IDS) + 1

#: The broken file's own content: no frontmatter block and no headings at all -- the same shape
#: ``test_list_req.py``'s pre-existing failed-entry test writes.
_BROKEN_CONTENT = "not a valid requirement, no headings at all"

#: The fixed frontmatter block every healthy fixture file carries (``{id}`` substituted per file).
_FRONTMATTER_TEMPLATE = """\
---
classification: null
created: '2026-08-30T10:00:00.000+02:00'
id: {id}
status: draft
type: req
updated: '2026-08-30T10:00:00.000+02:00'
version: 1.0.0
---

"""

_BODY = textwrap.dedent(
    """\
    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 80 \u00b0C.

    ## Description

    If the engine becomes too hot, the lifetime of the system decreases.

    ## Characteristics

    1. Safety
    1. Reliability

    ## Level

    MUST

    ## Source

    The International Safety Board Association (TISBA)
    """
)


def _body_with_title(title: str) -> str:
    return _BODY.replace("Maximum Engine Temperature", title)


def _write_document(base_dir: Path, filename: str, doc_id: str, title: str) -> None:
    """Write one healthy fixture document (frontmatter carrying ``doc_id`` plus the titled body)."""
    content = _FRONTMATTER_TEMPLATE.format(id=doc_id) + _body_with_title(title)
    (base_dir / filename).write_text(content, encoding="utf-8")


class TestListReqGlob(unittest.TestCase):
    """Tests for the list_req tool's optional glob parameter (feat-200-list, Phase 110)."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        cache_module.reset_req_cache()
        base_dir = self.docs_root / "req"
        base_dir.mkdir()
        for index, doc_id in enumerate(_DEAD_IDS, start=1):
            _write_document(base_dir, f"dead-{index}.md", doc_id, f"Glob Fixture {index}")
        _write_document(base_dir, "cafe.md", _CAFE_ID, "Glob Fixture Three")
        (base_dir / f"{_BROKEN_REF}.md").write_text(_BROKEN_CONTENT, encoding="utf-8")

    def tearDown(self) -> None:
        cache_module.reset_req_cache()

    def test_uuid_prefix_glob_returns_exactly_the_matching_rows_and_no_others(self) -> None:
        sut = list_req(glob="dead*", max_results=100)

        self.assertIsInstance(sut, PagedResult)
        self.assertEqual(sut.total, len(_DEAD_IDS))
        self.assertEqual(sut.error_count, 0)
        self.assertEqual([row.id for row in sut.results], list(_DEAD_IDS))
        self.assertEqual({row.ref for row in sut.results}, {"dead-1", "dead-2"})
        self.assertFalse(sut.truncated)
        for row in sut.results:
            self.assertIsInstance(row, ReqSummary)

    def test_matching_is_case_insensitive_in_the_pattern(self) -> None:
        for pattern in ("DEAD*", "Dead*"):
            with self.subTest(pattern=pattern):
                sut = list_req(glob=pattern, max_results=100)

                self.assertEqual(sut.total, len(_DEAD_IDS))
                self.assertEqual([row.id for row in sut.results], list(_DEAD_IDS))

    def test_glob_none_output_is_unchanged_and_reports_the_full_corpus(self) -> None:
        default_call = list_req()
        explicit_none = list_req(glob=None)

        self.assertEqual(default_call, explicit_none)
        self.assertEqual(default_call.total, _HEALTHY_COUNT + 1)
        self.assertEqual(default_call.error_count, 1)
        self.assertEqual(len(default_call.results), _HEALTHY_COUNT + 1)
        self.assertEqual(
            {row.id for row in default_call.results},
            {*_DEAD_IDS, _CAFE_ID, None},
        )
        failed = next(row for row in default_call.results if row.ref == _BROKEN_REF)
        self.assertIsNone(failed.id)
        self.assertIsNotNone(failed.error)

    def test_acc002_known_repo_uuid_matches_in_any_case_of_the_pattern(self) -> None:
        base_dir = self.docs_root / "req"
        _write_document(base_dir, "docs-req.md", _DOCS_REQ_ID, "Verification Case Record Document Management")

        for pattern in ("10b7*", "10B7*"):
            with self.subTest(pattern=pattern):
                sut = list_req(glob=pattern, max_results=100)

                self.assertEqual(sut.total, 1)
                self.assertEqual(sut.error_count, 0)
                self.assertEqual([row.id for row in sut.results], [_DOCS_REQ_ID])
                self.assertEqual({row.ref for row in sut.results}, {"docs-req"})

    def test_acc004_paging_composes_with_the_glob_filter(self) -> None:
        match_count = len(_DEAD_IDS)

        first_page = list_req(glob="dead*", max_results=1)
        self.assertEqual(first_page.total, match_count)
        self.assertEqual(len(first_page.results), 1)
        self.assertTrue(first_page.truncated)
        self.assertEqual(first_page.results[0].id, _DEAD_IDS[0])

        second_page = list_req(glob="dead*", max_results=1, offset=1)
        self.assertEqual(second_page.total, match_count)
        self.assertEqual(len(second_page.results), 1)
        self.assertFalse(second_page.truncated)
        self.assertEqual(second_page.results[0].id, _DEAD_IDS[1])

        past_end = list_req(glob="dead*", max_results=100, offset=match_count)
        self.assertEqual(past_end.total, match_count)
        self.assertEqual(past_end.results, [])
        self.assertFalse(past_end.truncated)

    def test_acc005_broken_file_is_reported_unfiltered_but_absent_for_any_glob(self) -> None:
        unfiltered = list_req()

        self.assertEqual(unfiltered.total, _HEALTHY_COUNT + 1)
        self.assertEqual(unfiltered.error_count, 1)
        failed = next(row for row in unfiltered.results if row.ref == _BROKEN_REF)
        self.assertIsNone(failed.id)
        self.assertIsNotNone(failed.error)

        for pattern in ("*", "dead*", "cafe*", ""):
            with self.subTest(pattern=pattern):
                sut = list_req(glob=pattern, max_results=100)

                self.assertEqual(sut.error_count, 0)
                self.assertNotIn(_BROKEN_REF, {row.ref for row in sut.results})
                for row in sut.results:
                    self.assertIsNotNone(row.id)
                    self.assertIsNone(row.error)

        self.assertEqual(list_req(glob="*", max_results=100).total, _HEALTHY_COUNT)
        self.assertEqual(list_req(glob="cafe*", max_results=100).total, 1)
        self.assertEqual(list_req(glob="", max_results=100).total, 0)


if __name__ == "__main__":
    unittest.main()
