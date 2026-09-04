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

"""Dedicated tests for the RSK sentinel document (feat-81-83-validation Phase 3, Task 3.2).

Parses ``_SENTINEL_RSK_TEXT`` via the real ``parse_rsk`` pipeline directly,
independent of ``list_rsk``'s own tests, so a future RSK schema change (a
new mandatory section, a changed ``_TARA_PATTERN``, a renamed heading)
surfaces here first, at the narrowest and fastest possible test, rather than
only indirectly through ``list_rsk``.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from biz.dfch.specmgr.general.tools._listing import FAILED_TO_PARSE_MARKER
from biz.dfch.specmgr.rsk.models.v1 import LEVEL_VERY_HIGH, RskDocument, parse_rsk
from biz.dfch.specmgr.rsk.tools._sentinel import _SENTINEL_RSK_DOCUMENT, _SENTINEL_RSK_TEXT, build_failed_rsk_summary


class TestSentinelRskTextParsesSuccessfully(unittest.TestCase):
    """Tests that `_SENTINEL_RSK_TEXT` parses successfully, on its own."""

    def test_parses_into_an_rsk_document(self) -> None:
        sut = parse_rsk(_SENTINEL_RSK_TEXT)

        self.assertIsInstance(sut, RskDocument)

    def test_module_level_sentinel_document_matches_a_fresh_parse(self) -> None:
        fresh = parse_rsk(_SENTINEL_RSK_TEXT)

        self.assertEqual(fresh.frontmatter.status, _SENTINEL_RSK_DOCUMENT.frontmatter.status)
        self.assertEqual(fresh.body.text, _SENTINEL_RSK_DOCUMENT.body.text)

    def test_is_deliberately_worst_case_severity(self) -> None:
        sut = _SENTINEL_RSK_DOCUMENT

        self.assertEqual(sut.body.initial_assessment.probability.value, 5)
        self.assertEqual(sut.body.initial_assessment.impact.value, 5)
        self.assertEqual(sut.body.initial_assessment.level, LEVEL_VERY_HIGH)
        self.assertEqual(sut.body.residual_assessment.probability.value, 5)
        self.assertEqual(sut.body.residual_assessment.impact.value, 5)
        self.assertEqual(sut.body.residual_assessment.level, LEVEL_VERY_HIGH)

    def test_strategy_is_the_passive_accept_value(self) -> None:
        self.assertEqual(_SENTINEL_RSK_DOCUMENT.body.strategy.value.text, "accept")

    def test_frontmatter_status_is_the_passive_dropped_value(self) -> None:
        self.assertEqual(_SENTINEL_RSK_DOCUMENT.frontmatter.status, "dropped")

    def test_scope_first_entry_is_unknown(self) -> None:
        self.assertEqual(_SENTINEL_RSK_DOCUMENT.body.scope.items[0].text, "unknown")


class TestBuildFailedRskSummary(unittest.TestCase):
    """Tests for build_failed_rsk_summary (the sentinel -> RskSummary construction site)."""

    def test_overrides_id_title_status_path_and_error(self) -> None:
        path = Path("/tmp/some-risk.md")
        error = ValueError("boom")

        sut = build_failed_rsk_summary(path, error)

        self.assertIsNone(sut.id)
        self.assertEqual(sut.title, FAILED_TO_PARSE_MARKER)
        self.assertEqual(sut.status, FAILED_TO_PARSE_MARKER)
        self.assertEqual(Path(sut.path), path.resolve())
        self.assertEqual(sut.error, "boom")

    def test_ref_is_the_real_paths_stem(self) -> None:
        path = Path("/tmp/some-risk.md")

        sut = build_failed_rsk_summary(path, ValueError("boom"))

        self.assertEqual(sut.ref, "some-risk")

    def test_risk_specific_fields_are_genuinely_derived_worst_case_severity(self) -> None:
        sut = build_failed_rsk_summary(Path("/tmp/some-risk.md"), ValueError("boom"))

        self.assertEqual(sut.initial_level, LEVEL_VERY_HIGH)
        self.assertEqual(sut.residual_level, LEVEL_VERY_HIGH)
        self.assertEqual(sut.residual_probability, 5)
        self.assertEqual(sut.residual_impact, 5)
        self.assertEqual(sut.residual_product, 25)
        self.assertEqual(sut.strategy, "accept")
        self.assertEqual(sut.scope, "unknown")


if __name__ == "__main__":
    unittest.main()
