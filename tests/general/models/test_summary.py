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
actual subclasses of :class:`DocSummary`. ``AdrSummary`` is a deliberate
exception (see ``biz.dfch.specmgr.models.adr.v1.summary``'s module
docstring and this feature's Decisions Made log for why it cannot subclass
:class:`DocSummary` without adding an ``mcp`` dependency to the
dependency-free base library) -- it is instead asserted to be
*structurally* equivalent: same field names, same annotations.
"""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.general.models.summary import DocSummary
from biz.dfch.specmgr.models.adr.v1.summary import AdrSummary
from biz.dfch.specmgr.qa.models.v1.summary import QaSummary
from biz.dfch.specmgr.req.models.v1.summary import ReqSummary
from biz.dfch.specmgr.tsk.models.v1.summary import TskSummary
from biz.dfch.specmgr.uc.models.v2.summary import UcSummary

_EXPECTED_FIELD_NAMES = ["id", "title", "status", "ref"]


class TestDocSummary(unittest.TestCase):
    """Tests for DocSummary itself."""

    def test_declares_the_four_common_fields(self):
        self.assertEqual(list(DocSummary.model_fields.keys()), _EXPECTED_FIELD_NAMES)

    def test_allows_a_none_id(self):
        sut = DocSummary(id=None, title="t", status="draft", ref="r")

        self.assertIsNone(sut.id)


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


class TestAdrSummaryIsStructurallyEquivalent(unittest.TestCase):
    """Tests that AdrSummary, though not a DocSummary subclass, shares its field set."""

    def test_is_deliberately_not_a_docsummary_subclass(self):
        self.assertFalse(issubclass(AdrSummary, DocSummary))

    def test_declares_the_same_field_names_as_docsummary(self):
        self.assertEqual(list(AdrSummary.model_fields.keys()), _EXPECTED_FIELD_NAMES)

    def test_declares_the_same_field_annotations_as_docsummary(self):
        adr_annotations = {name: field.annotation for name, field in AdrSummary.model_fields.items()}
        doc_annotations = {name: field.annotation for name, field in DocSummary.model_fields.items()}

        self.assertEqual(adr_annotations, doc_annotations)


class TestAllFiveSummariesShareTheCommonBaseFieldSet(unittest.TestCase):
    """Side-by-side test across every domain's summary model (ACC-001/ACC-003)."""

    def test_all_five_summaries_declare_the_same_field_names(self):
        summary_classes = [AdrSummary, ReqSummary, UcSummary, TskSummary, QaSummary]

        for summary_class in summary_classes:
            with self.subTest(summary_class=summary_class.__name__):
                self.assertEqual(list(summary_class.model_fields.keys()), _EXPECTED_FIELD_NAMES)


if __name__ == "__main__":
    unittest.main()
