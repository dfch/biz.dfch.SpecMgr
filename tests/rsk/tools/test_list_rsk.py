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

"""Tests for the ``list_rsk`` ``@mcp.tool()`` wrapper (Task 3.14/3.16).

Mirrors ``tests/tsk/tools/test_list_tsk.py``'s paging-contract coverage, plus
the risk-specific ``RskSummary`` fields (the initial/residual zone levels,
the TARA strategy word, the first ``## Scope`` entry, and the residual-risk
coordinates) that ``list_rsk`` carries beyond the base's four.
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import PagedResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._paging import DEFAULT_MAX_RESULTS, MAX_MAX_RESULTS
from biz.dfch.specmgr.rsk.models.v1 import LEVEL_HIGH, LEVEL_LOW, LEVEL_MEDIUM, LEVEL_VERY_HIGH, RskSummary
from biz.dfch.specmgr.rsk.tools._paths import ensure_rsk_base_dir
from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk
from biz.dfch.specmgr.rsk.tools.list_rsk import list_rsk

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Sample Risk

    ## Cause

    A root condition.

    ## Trigger

    An event that sets the risk in motion.

    ## Consequence

    A bounded consequence.

    ## Scope

    - Sample subsystem

    ## Initial Assessment

    ### Probability 4

    ### Impact 3

    ## Strategy

    reduce

    ## Mitigation

    Sample treatment measures.

    ## Residual Assessment

    ### Probability 2

    ### Impact 3
    """
)

_OTHER_BODY = _MINIMAL_BODY.replace("Sample Risk", "Another Risk")

_VERY_HIGH_BODY = _MINIMAL_BODY.replace(
    "## Residual Assessment\n\n### Probability 2\n\n### Impact 3\n",
    "## Residual Assessment\n\n### Probability 5\n\n### Impact 5\n",
)


def _body_with_title(title: str) -> str:
    return _MINIMAL_BODY.replace("Sample Risk", title)


class TestListRsk(unittest.TestCase):
    """Tests for the list_rsk tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_summaries_and_skips_malformed_file(self) -> None:
        first = create_rsk(_MINIMAL_BODY)
        second = create_rsk(_OTHER_BODY)

        base_dir = ensure_rsk_base_dir()
        (base_dir / "broken.md").write_text("not a valid risk, no headings at all", encoding="utf-8")

        sut = list_rsk()

        self.assertIsInstance(sut, PagedResult)
        self.assertEqual(sut.total, 2)
        for summary in sut.results:
            self.assertIsInstance(summary, RskSummary)
        ids = {summary.id for summary in sut.results}
        self.assertEqual(ids, {first.frontmatter.id, second.frontmatter.id})
        titles = {summary.title for summary in sut.results}
        self.assertEqual(titles, {"Sample Risk", "Another Risk"})
        statuses = {summary.status for summary in sut.results}
        self.assertEqual(statuses, {"open"})
        for summary in sut.results:
            self.assertNotIn(".md", summary.ref)
            self.assertTrue(summary.ref)

    def test_empty_result_for_missing_directory(self) -> None:
        self.assertFalse((self.docs_root / "rsk").exists())

        sut = list_rsk()

        self.assertEqual(sut.total, 0)
        self.assertEqual(sut.results, [])
        self.assertFalse(sut.truncated)

    def test_default_page_size_and_shape(self) -> None:
        for i in range(3):
            create_rsk(_body_with_title(f"Title {i}"))

        sut = list_rsk()

        self.assertEqual(sut.total, 3)
        self.assertEqual(sut.offset, 0)
        self.assertEqual(sut.max_results, DEFAULT_MAX_RESULTS)
        self.assertEqual(len(sut.results), 3)
        self.assertFalse(sut.truncated)

    def test_max_results_limits_page_and_marks_truncated(self) -> None:
        for i in range(3):
            create_rsk(_body_with_title(f"Title {i}"))

        sut = list_rsk(max_results=2)

        self.assertEqual(sut.total, 3)
        self.assertEqual(len(sut.results), 2)
        self.assertTrue(sut.truncated)

    def test_offset_selects_the_next_page(self) -> None:
        for i in range(3):
            create_rsk(_body_with_title(f"Title {i}"))

        first_page = list_rsk(max_results=2)
        second_page = list_rsk(max_results=2, offset=2)

        self.assertEqual(len(second_page.results), 1)
        self.assertFalse(second_page.truncated)
        self.assertNotEqual(first_page.results[0].id, second_page.results[0].id)

    def test_max_results_is_clamped_to_the_cap(self) -> None:
        create_rsk(_MINIMAL_BODY)

        sut = list_rsk(max_results=500)

        self.assertEqual(sut.max_results, MAX_MAX_RESULTS)

    def test_negative_offset_is_floored_to_zero(self) -> None:
        create_rsk(_MINIMAL_BODY)

        sut = list_rsk(offset=-5)

        self.assertEqual(sut.offset, 0)

    def test_truncated_boundary_false_when_page_covers_all_items(self) -> None:
        for i in range(2):
            create_rsk(_body_with_title(f"Title {i}"))

        sut = list_rsk(max_results=2)

        self.assertFalse(sut.truncated)

    def test_truncated_boundary_true_when_one_item_remains(self) -> None:
        for i in range(3):
            create_rsk(_body_with_title(f"Title {i}"))

        sut = list_rsk(max_results=2)

        self.assertTrue(sut.truncated)

    def test_total_reflects_full_parseable_count_regardless_of_paging(self) -> None:
        for i in range(5):
            create_rsk(_body_with_title(f"Title {i}"))
        base_dir = ensure_rsk_base_dir()
        (base_dir / "broken.md").write_text("not a valid risk, no headings at all", encoding="utf-8")

        sut = list_rsk(max_results=1, offset=1)

        self.assertEqual(sut.total, 5)

    def test_residual_fields_present_and_correct(self) -> None:
        """Every summary line must carry the risk-specific fields, derived correctly from the document."""
        created = create_rsk(_MINIMAL_BODY)

        sut = list_rsk()

        self.assertEqual(len(sut.results), 1)
        summary = sut.results[0]
        self.assertEqual(summary.id, created.frontmatter.id)
        self.assertEqual(summary.initial_level, LEVEL_HIGH)  # 4 x 3 = 12 -> high
        self.assertEqual(summary.residual_level, LEVEL_MEDIUM)  # 2 x 3 = 6 -> medium
        self.assertEqual(summary.strategy, "reduce")
        self.assertEqual(summary.scope, "Sample subsystem")
        self.assertEqual(summary.residual_probability, 2)
        self.assertEqual(summary.residual_impact, 3)
        self.assertEqual(summary.residual_product, 6)

    def test_residual_product_consistent_with_zone_mapping(self) -> None:
        """A 5x5 residual cell must map to the `very high` zone with product 25."""
        created = create_rsk(_VERY_HIGH_BODY)

        sut = list_rsk()

        summary = next(s for s in sut.results if s.id == created.frontmatter.id)
        self.assertEqual(summary.initial_level, LEVEL_HIGH)  # 4 x 3 = 12 -> high
        self.assertEqual(summary.residual_probability, 5)
        self.assertEqual(summary.residual_impact, 5)
        self.assertEqual(summary.residual_product, 25)
        self.assertEqual(summary.residual_level, LEVEL_VERY_HIGH)
        # The minimal body's residual (2 x 3 = 6) is untouched by the other document.
        self.assertNotIn(LEVEL_LOW, [s.residual_level for s in sut.results if s.id == created.frontmatter.id])


if __name__ == "__main__":
    unittest.main()
