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

"""Tests for the ``list_uc`` tool's own optional ``glob`` parameter (feat-200-list, GitHub issue #200,
Phase 110: REQ-002/REQ-004/REQ-005).

Per the feature's own plan, the corpus is a small, hand-built set of files in a per-test temp
directory pointed at by ``SPECMGR_DOCS_DIR`` -- two healthy use cases with known,
different-prefix UUIDs (``deadbeef-*`` / ``cafe...``) plus one broken file -- written directly
to disk (bypassing ``create_uc``/the tool layer, which would assign random UUIDs the filter
could not be tested against deterministically). The ``uc`` cache is reset in ``setUp``/
``tearDown`` (the request path is cache-sensitive; a fresh temp directory alone already
guarantees no cross-test path collision, but the explicit reset keeps this module's own
discipline self-documenting).
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import PagedResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.uc.models.v2 import UcSummary
from biz.dfch.specmgr.uc.tools import _cache as cache_module
from biz.dfch.specmgr.uc.tools.list_uc import list_uc

#: The corpus's own two healthy (different-prefix UUID) and one broken file ids.
_DEAD_ID = "deadbeef-0000-4000-8000-000000000001"
_CAFE_ID = "cafebab0-1234-4567-89ab-cdef01234567"
_BROKEN_REF = "broken"

#: The total healthy file count (and thus the unfiltered ``total`` minus the one broken file).
_HEALTHY_COUNT = 2

#: The broken file's own content: no frontmatter block and no headings at all -- the same shape
#: ``test_list_uc.py``'s pre-existing failed-entry test writes.
_BROKEN_CONTENT = "not a valid use case, no headings at all"

#: The fixed frontmatter block every healthy fixture file carries (``{id}`` substituted per file).
_FRONTMATTER_TEMPLATE = """\
---
classification: null
created: '2026-08-30T10:00:00.000+02:00'
id: {id}
status: draft
type: uc
updated: '2026-08-30T10:00:00.000+02:00'
version: 1.0.0
---

"""

_BODY = textwrap.dedent(
    """\
    # Buy Goods

    ## Characteristic Information

    ### Goal in Context

    Buyer issues request directly to our company.

    ### Scope

    Company (the system being designed as a black box)

    ### Level

    Summary

    ### Preconditions

    - We know Buyer

    ### Success End Condition

    - Buyer has goods

    ### Primary Actor

    Buyer.

    ### Trigger

    Purchase request comes in.

    ## Main Success Scenario

    1. Buyer calls in with a purchase request.
    2. Company creates order in system.
    """
)


def _body_with_title(title: str) -> str:
    return _BODY.replace("Buy Goods", title)


def _write_document(base_dir: Path, filename: str, doc_id: str, title: str) -> None:
    """Write one healthy fixture document (frontmatter carrying ``doc_id`` plus the titled body)."""
    content = _FRONTMATTER_TEMPLATE.format(id=doc_id) + _body_with_title(title)
    (base_dir / filename).write_text(content, encoding="utf-8")


class TestListUcGlob(unittest.TestCase):
    """Tests for the list_uc tool's optional glob parameter (feat-200-list, Phase 110)."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        cache_module.reset_uc_cache()
        base_dir = self.docs_root / "uc"
        base_dir.mkdir()
        _write_document(base_dir, "dead.md", _DEAD_ID, "Glob Fixture One")
        _write_document(base_dir, "cafe.md", _CAFE_ID, "Glob Fixture Two")
        (base_dir / f"{_BROKEN_REF}.md").write_text(_BROKEN_CONTENT, encoding="utf-8")

    def tearDown(self) -> None:
        cache_module.reset_uc_cache()

    def test_uuid_prefix_glob_returns_exactly_the_matching_rows_and_no_others(self) -> None:
        sut = list_uc(glob="dead*", max_results=100)

        self.assertIsInstance(sut, PagedResult)
        self.assertEqual(sut.total, 1)
        self.assertEqual(sut.error_count, 0)
        self.assertEqual([row.id for row in sut.results], [_DEAD_ID])
        self.assertEqual({row.ref for row in sut.results}, {"dead"})
        self.assertFalse(sut.truncated)
        for row in sut.results:
            self.assertIsInstance(row, UcSummary)

    def test_matching_is_case_insensitive_in_the_pattern(self) -> None:
        for pattern in ("DEAD*", "Dead*"):
            with self.subTest(pattern=pattern):
                sut = list_uc(glob=pattern, max_results=100)

                self.assertEqual(sut.total, 1)
                self.assertEqual([row.id for row in sut.results], [_DEAD_ID])

    def test_glob_none_output_is_unchanged_and_reports_the_full_corpus(self) -> None:
        default_call = list_uc()
        explicit_none = list_uc(glob=None)

        self.assertEqual(default_call, explicit_none)
        self.assertEqual(default_call.total, _HEALTHY_COUNT + 1)
        self.assertEqual(default_call.error_count, 1)
        self.assertEqual(len(default_call.results), _HEALTHY_COUNT + 1)
        self.assertEqual({row.id for row in default_call.results}, {_DEAD_ID, _CAFE_ID, None})
        failed = next(row for row in default_call.results if row.ref == _BROKEN_REF)
        self.assertIsNone(failed.id)
        self.assertIsNotNone(failed.error)


if __name__ == "__main__":
    unittest.main()
