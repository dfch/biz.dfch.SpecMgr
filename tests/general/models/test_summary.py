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

"""Tests for `general.models.summary.DocSummary` (feat-13 Task 1.3/1.4, REQ-003/ACC-001/ACC-003).

``ReqSummary``/``UcSummary``/``TskSummary``/``QaSummary`` are asserted to be
actual subclasses of :class:`DocSummary`. ``FeatSummary`` gets its own,
narrower test class below (feat-81-83-validation Phase 4, REQ-007): it used
to redeclare its own separate ``path`` field, and Phase 4 removed that
redundant declaration, so it is now checked for the same field set as
every other whole-body domain, plus a direct assertion that ``path`` is no
longer redeclared.
"""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.feat.models.v1.summary import FeatSummary
from biz.dfch.specmgr.general.models.summary import DocSummary
from biz.dfch.specmgr.qa.models.v2.summary import QaSummary
from biz.dfch.specmgr.req.models.v1.summary import ReqSummary
from biz.dfch.specmgr.tsk.models.v1.summary import TskSummary
from biz.dfch.specmgr.uc.models.v2.summary import UcSummary

#: The current shared `DocSummary` base's fields -- the four original ones plus `path`/`error`,
#: added in feat-81-83-validation Phase 3 (REQ-006/REQ-007) for the whole-body domains only.
_EXPECTED_FIELD_NAMES = ["id", "title", "status", "ref", "path", "error"]


class TestDocSummary(unittest.TestCase):
    """Tests for DocSummary itself."""

    def test_declares_the_four_common_fields(self):
        self.assertEqual(list(DocSummary.model_fields.keys()), _EXPECTED_FIELD_NAMES)

    def test_allows_a_none_id(self):
        sut = DocSummary(id=None, title="t", status="draft", ref="r", path="/tmp/r.md")

        self.assertIsNone(sut.id)

    def test_error_defaults_to_none(self):
        sut = DocSummary(id="x", title="t", status="draft", ref="r", path="/tmp/r.md")

        self.assertIsNone(sut.error)


class TestReqSummarySharesDocSummaryBase(unittest.TestCase):
    """Tests that ReqSummary subclasses DocSummary."""

    def test_is_a_docsummary_subclass(self):
        self.assertTrue(issubclass(ReqSummary, DocSummary))

    def test_declares_no_extra_fields(self):
        self.assertEqual(list(ReqSummary.model_fields.keys()), _EXPECTED_FIELD_NAMES)


class TestUcSummarySharesDocSummaryBase(unittest.TestCase):
    """Tests that UcSummary subclasses DocSummary."""

    def test_is_a_docsummary_subclass(self):
        self.assertTrue(issubclass(UcSummary, DocSummary))

    def test_declares_no_extra_fields(self):
        self.assertEqual(list(UcSummary.model_fields.keys()), _EXPECTED_FIELD_NAMES)


class TestTskSummarySharesDocSummaryBase(unittest.TestCase):
    """Tests that TskSummary subclasses DocSummary."""

    def test_is_a_docsummary_subclass(self):
        self.assertTrue(issubclass(TskSummary, DocSummary))

    def test_declares_no_extra_fields(self):
        self.assertEqual(list(TskSummary.model_fields.keys()), _EXPECTED_FIELD_NAMES)


class TestQaSummarySharesDocSummaryBase(unittest.TestCase):
    """Tests that QaSummary subclasses DocSummary."""

    def test_is_a_docsummary_subclass(self):
        self.assertTrue(issubclass(QaSummary, DocSummary))

    def test_declares_no_extra_fields(self):
        self.assertEqual(list(QaSummary.model_fields.keys()), _EXPECTED_FIELD_NAMES)


class TestFeatSummarySharesDocSummaryBase(unittest.TestCase):
    """Tests that FeatSummary subclasses DocSummary and no longer redeclares `path` (feat-81-83-validation Phase 4).

    ``FeatSummary`` used to redeclare its own, separate ``path`` field
    (predating ``path``'s generalization onto the shared base in Phase 3);
    Phase 4 (Task 4.2, REQ-007) removed that redundant declaration, so
    ``path`` -- like every other field -- is now purely inherited.
    """

    def test_is_a_docsummary_subclass(self):
        self.assertTrue(issubclass(FeatSummary, DocSummary))

    def test_declares_no_extra_fields(self):
        self.assertEqual(list(FeatSummary.model_fields.keys()), _EXPECTED_FIELD_NAMES)

    def test_does_not_redeclare_path(self):
        self.assertNotIn("path", FeatSummary.__dict__.get("__annotations__", {}))


class TestAllFourWholeBodySummariesShareTheCommonBaseFieldSet(unittest.TestCase):
    """Side-by-side test across every whole-body domain's summary model (ACC-001/ACC-003)."""

    def test_all_four_summaries_declare_the_same_field_names(self):
        summary_classes = [ReqSummary, UcSummary, TskSummary, QaSummary]

        for summary_class in summary_classes:
            with self.subTest(summary_class=summary_class.__name__):
                self.assertEqual(list(summary_class.model_fields.keys()), _EXPECTED_FIELD_NAMES)


if __name__ == "__main__":
    unittest.main()
