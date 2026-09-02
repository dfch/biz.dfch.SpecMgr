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

"""Tests for the `RskSummary` model and its `from_document` factory.

`RskSummary` subclasses `general.models.summary.DocSummary` (unlike the
other domains' summaries, it carries risk-specific fields beyond the base's
`id`/`title`/`status`/`ref` -- see `.specmgr/feat/feat-15-add-artifact-type-risk/README.md`
Decisions Made). The factory derives every risk-specific field from the
parsed document's computed `level`/`value` fields -- the 5x5 zone mapping is
never re-implemented here, so a zone drift in `assessment.py` surfaces in
these tests.
"""

from __future__ import annotations

import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.general.models.summary import DocSummary
from biz.dfch.specmgr.rsk.models.v1 import LEVEL_HIGH, LEVEL_MEDIUM, RskSummary, parse_rsk

_REFERENCE_PATH = (
    Path(__file__).resolve().parents[4] / ".specmgr" / "feat" / "feat-15-add-artifact-type-risk" / "rsk_reference.md"
)

_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: rsk-001
    type: rsk
    version: 1.0.0
    status: open
    created: '2026-08-24 00:00:00.000Z'
    updated: '2026-08-24 00:00:00.000Z'
    ---

    # Simple Risk

    ## Cause

    The parser library is unmaintained.

    ## Trigger

    An uploaded file exploits a known format flaw.

    ## Consequence

    Remote code execution in the document-processing subsystem.

    ## Scope

    - document-processing subsystem

    ## Initial Assessment

    ### Probability 4

    ### Impact 3

    ## Strategy

    reduce

    ## Mitigation

    Replace the parser with a maintained library.

    ## Residual Assessment

    ### Probability 2

    ### Impact 3
    """
)


class TestRskSummarySharesDocSummaryBase(unittest.TestCase):
    """`RskSummary` is a real `DocSummary` subclass with the base's four fields first."""

    def test_is_doc_summary_subclass(self) -> None:
        self.assertTrue(issubclass(RskSummary, DocSummary))

    def test_base_fields_come_first(self) -> None:
        fields = list(RskSummary.model_fields.keys())

        self.assertEqual(fields[:4], ["id", "title", "status", "ref"])


class TestRskSummaryFromDocument(unittest.TestCase):
    """`from_document` derives the risk-specific fields from the parsed assessments."""

    def test_builds_all_fields_from_minimal_document(self) -> None:
        document = parse_rsk(_MINIMAL_DOC)

        sut = RskSummary.from_document(document, ref="rsk-001-simple-risk")

        self.assertEqual(sut.id, "rsk-001")
        self.assertEqual(sut.title, "Simple Risk")
        self.assertEqual(sut.status, "open")
        self.assertEqual(sut.ref, "rsk-001-simple-risk")
        self.assertEqual(sut.initial_level, LEVEL_HIGH)
        self.assertEqual(sut.residual_level, LEVEL_MEDIUM)
        self.assertEqual(sut.strategy, "reduce")
        self.assertEqual(sut.scope, "document-processing subsystem")
        self.assertEqual(sut.residual_probability, 2)
        self.assertEqual(sut.residual_impact, 3)
        self.assertEqual(sut.residual_product, 6)

    def test_builds_all_fields_from_reference_document(self) -> None:
        document = parse_rsk(_REFERENCE_PATH.read_text(encoding="utf-8"))

        sut = RskSummary.from_document(document, ref="rsk-reference")

        self.assertEqual(sut.id, "deadbeef-risk-risk-risk-deadbeefrisk")
        self.assertEqual(sut.title, "Untrusted File Uploads Parsed by an Unmaintained Parser Library")
        self.assertEqual(sut.status, "open")
        self.assertEqual(sut.ref, "rsk-reference")
        self.assertEqual(sut.initial_level, LEVEL_HIGH)
        self.assertEqual(sut.residual_level, LEVEL_MEDIUM)
        self.assertEqual(sut.strategy, "reduce")
        self.assertEqual(sut.scope, "document-processing subsystem")
        self.assertEqual(sut.residual_probability, 2)
        self.assertEqual(sut.residual_impact, 3)
        self.assertEqual(sut.residual_product, 6)


class TestRskSummaryFieldValidation(unittest.TestCase):
    """The residual-risk coordinates carry the 5x5 bounds in their own schemas."""

    def test_rejects_out_of_range_coordinates(self) -> None:
        for kwargs in (
            {"residual_probability": 0},
            {"residual_probability": 6},
            {"residual_impact": 0},
            {"residual_impact": 6},
            {"residual_product": 0},
            {"residual_product": 26},
        ):
            with self.subTest(kwargs=kwargs):
                base = {
                    "id": "rsk-001",
                    "title": "Simple Risk",
                    "status": "open",
                    "ref": "r",
                    "initial_level": "low",
                    "residual_level": "low",
                    "strategy": "accept",
                    "scope": "s1",
                    "residual_probability": 1,
                    "residual_impact": 1,
                    "residual_product": 1,
                }
                base.update(kwargs)

                with self.assertRaises(ValidationError):
                    RskSummary(**base)


if __name__ == "__main__":
    unittest.main()
