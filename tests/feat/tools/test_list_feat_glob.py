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

"""Tests for the ``list_feat`` tool's own optional ``glob`` parameter (feat-200-list, GitHub issue #200,
Phase 100: ACC-001, ACC-004, ACC-005, REQ-004, the empty-string-is-a-pattern decision, and the
``glob=None``-unchanged half of ACC-003).

Per the feature's own plan, the corpus is a small, hand-built set of folders in a per-test temp
directory pointed at by ``SPECMGR_FEAT_DIR`` -- two ``feat-7*`` ids (the ACC-001 pattern's matches),
two non-matching ids, and one broken folder -- rather than the live repo corpus or feat-187's own
70-folder generator (whose healthy bulk filler ids all share the ``feat-7`` prefix the ACC-001
pattern matches, and which is far larger than this parameter's tests need). The healthy folders are
written directly to disk (``_fixture_corpus.write_feat_folder`` -- bypassing ``create_feat``/the
tool layer, so the first ``list_feat`` call resolves them through the dirty (frontmatter-stage)
cache only, the same cold-cache path feat-187's own ACC-001 exercises); one test additionally
brings one folder through the clean (full-parse) cache via an on-demand ``get_feat`` read to prove
the filter sees rows whatever stage produced them. Both feat cache stages are reset in
``setUp``/``tearDown`` the way ``test_list_feat_timeout.py`` does (the request path is
cache-sensitive; a fresh temp directory alone already guarantees no cross-test path collision, but
the explicit reset keeps this module's own discipline self-documenting).
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.feat.models.v1 import FeatDocument
from biz.dfch.specmgr.feat.tools import _cache as cache_module
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR
from biz.dfch.specmgr.feat.tools.get_feat import get_feat
from biz.dfch.specmgr.feat.tools.list_feat import list_feat
from biz.dfch.specmgr.general.models import PagedResult

from ._fixture_corpus import write_feat_folder

#: The corpus's own two matching (the ACC-001 ``feat-7*`` pattern), two non-matching, and one
#: broken folder ids.
_MATCHING_IDS: tuple[str, ...] = ("feat-7-alpha", "feat-7-beta")
_NON_MATCHING_IDS: tuple[str, ...] = ("feat-8-gamma", "feat-100-delta")
_BROKEN_ID = "feat-99-broken"

#: The total healthy folder count (and thus the unfiltered ``total`` minus the one broken folder).
_HEALTHY_COUNT = len(_MATCHING_IDS) + len(_NON_MATCHING_IDS)

#: The broken folder's own content: no frontmatter block and no headings at all -- the same shape
#: ``test_list_feat.py``'s pre-existing failed-entry test writes (a tier-1 failure at both cache
#: stages, ``FeatFrontmatter``'s own required fields missing).
_BROKEN_CONTENT = "not a valid feature, no headings at all"

#: The fixed frontmatter block every healthy fixture folder carries (``{id}`` substituted per
#: folder) -- the same template shape feat-187's own ``_fixture_corpus`` uses.
_FRONTMATTER_TEMPLATE = """\
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


def _healthy_document(folder_id: str) -> str:
    """A plain, valid feature document (feat-187 letter (j)'s own shape) for fixture folder ``folder_id``."""
    body = textwrap.dedent(
        f"""\
        # Feature: Glob Fixture {folder_id}

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
    result = _FRONTMATTER_TEMPLATE.format(id=folder_id) + body
    return result


class TestListFeatGlob(unittest.TestCase):
    """Tests for the list_feat tool's optional glob parameter (feat-200-list, Phase 100)."""

    def setUp(self) -> None:
        self.feat_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {FEAT_DIR_ENV_VAR: str(self.feat_root)}))
        cache_module.reset_feat_cache()
        cache_module.reset_feat_dirty_cache()
        for folder_id in (*_MATCHING_IDS, *_NON_MATCHING_IDS):
            write_feat_folder(self.feat_root, folder_id, _healthy_document(folder_id))
        write_feat_folder(self.feat_root, _BROKEN_ID, _BROKEN_CONTENT)

    def tearDown(self) -> None:
        cache_module.reset_feat_cache()
        cache_module.reset_feat_dirty_cache()

    def test_acc001_glob_returns_exactly_the_matching_features_and_no_others(self) -> None:
        sut = list_feat(glob="feat-7*", max_results=100)

        self.assertIsInstance(sut, PagedResult)
        self.assertEqual(sut.total, len(_MATCHING_IDS))
        self.assertEqual(sut.error_count, 0)
        self.assertEqual([row.id for row in sut.results], list(_MATCHING_IDS))
        self.assertEqual({row.ref for row in sut.results}, set(_MATCHING_IDS))
        self.assertFalse(sut.truncated)

    def test_req004_matching_is_case_insensitive_in_the_pattern(self) -> None:
        for pattern in ("FEAT-7*", "Feat-7*"):
            with self.subTest(pattern=pattern):
                sut = list_feat(glob=pattern, max_results=100)

                self.assertEqual(sut.total, len(_MATCHING_IDS))
                self.assertEqual([row.id for row in sut.results], list(_MATCHING_IDS))

    def test_acc004_paging_composes_with_the_glob_filter(self) -> None:
        match_count = len(_MATCHING_IDS)

        first_page = list_feat(glob="feat-7*", max_results=1)
        self.assertEqual(first_page.total, match_count)
        self.assertEqual(len(first_page.results), 1)
        self.assertTrue(first_page.truncated)
        self.assertEqual(first_page.results[0].id, _MATCHING_IDS[0])

        second_page = list_feat(glob="feat-7*", max_results=1, offset=1)
        self.assertEqual(second_page.total, match_count)
        self.assertEqual(len(second_page.results), 1)
        self.assertFalse(second_page.truncated)
        self.assertEqual(second_page.results[0].id, _MATCHING_IDS[1])

        past_end = list_feat(glob="feat-7*", max_results=100, offset=match_count)
        self.assertEqual(past_end.total, match_count)
        self.assertEqual(past_end.results, [])
        self.assertFalse(past_end.truncated)

    def test_acc005_broken_folder_is_reported_unfiltered_but_absent_for_any_glob(self) -> None:
        unfiltered = list_feat()

        self.assertEqual(unfiltered.total, _HEALTHY_COUNT + 1)
        self.assertEqual(unfiltered.error_count, 1)
        failed = next(row for row in unfiltered.results if row.ref == _BROKEN_ID)
        self.assertIsNone(failed.id)
        self.assertIsNotNone(failed.error)

        for pattern in ("*", "feat-7*", "feat-99*"):
            with self.subTest(pattern=pattern):
                sut = list_feat(glob=pattern, max_results=100)

                self.assertEqual(sut.error_count, 0)
                self.assertNotIn(_BROKEN_ID, {row.ref for row in sut.results})
                for row in sut.results:
                    self.assertIsNotNone(row.id)
                    self.assertIsNone(row.error)

        self.assertEqual(list_feat(glob="*", max_results=100).total, _HEALTHY_COUNT)
        self.assertEqual(list_feat(glob="feat-99*", max_results=100).total, 0)

    def test_empty_glob_string_is_a_pattern_matching_nothing_not_an_off_switch(self) -> None:
        sut = list_feat(glob="", max_results=100)

        self.assertEqual(sut.total, 0)
        self.assertEqual(sut.results, [])
        self.assertEqual(sut.error_count, 0)
        self.assertFalse(sut.truncated)

    def test_acc003_glob_none_output_is_unchanged(self) -> None:
        default_call = list_feat()
        explicit_none = list_feat(glob=None)

        self.assertEqual(default_call, explicit_none)
        self.assertEqual(default_call.total, _HEALTHY_COUNT + 1)
        self.assertEqual(default_call.error_count, 1)
        self.assertEqual(len(default_call.results), _HEALTHY_COUNT + 1)

    def test_glob_filters_rows_whatever_cache_stage_produced_them(self) -> None:
        # Dirty stage: the corpus was written directly to disk, so this first list_feat call
        # resolves every healthy folder through the dirty (frontmatter-stage) cache only.
        dirty_stage = list_feat(glob="feat-7*", max_results=100)
        self.assertEqual([row.id for row in dirty_stage.results], list(_MATCHING_IDS))
        self.assertEqual(dirty_stage.results[0].title, "Glob Fixture feat-7-alpha")

        # Clean stage: an on-demand get_feat read full-parses one of the two matching folders, so
        # the next list_feat resolves it from the clean (full-parse) cache instead of the dirty
        # one -- the filter must yield the same rows either way.
        doc = get_feat("feat-7-alpha")
        self.assertIsInstance(doc, FeatDocument)
        clean_stage = list_feat(glob="feat-7*", max_results=100)
        self.assertEqual(clean_stage.total, len(_MATCHING_IDS))
        self.assertEqual([row.id for row in clean_stage.results], list(_MATCHING_IDS))
        self.assertEqual(clean_stage.results[0].title, "Glob Fixture feat-7-alpha")


if __name__ == "__main__":
    unittest.main()
