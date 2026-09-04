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

"""Tests for the `specmgr://dtais` resource (`general.resources.dtais.dtais`)."""

import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.resources.dtais import dtais
from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.vcr.models.v1 import AcceptanceCriterion

#: A bullet line starting with exactly one backticked method word, followed by
#: its one-line definition -- the shape the resource uses to document the five
#: valid `### AC-NNN (Method): ...` method words verbatim.
_VALID_WORD_BULLET = re.compile(r"^- `([A-Za-z]+)` -- ", re.MULTILINE)

#: The five words the resource must document as the closed DTAIS set, in
#: order -- exactly `vcr.models.v1.body`'s `_AC_HEADING_PATTERN` method group.
_EXPECTED_DTAIS_WORDS = ["Demonstration", "Test", "Analysis", "Inspection", "Special"]

#: VCR's own retired 5th-method name (renamed to `Special`, see
#: `.specmgr/feat/feat-33-vcr/README.md` Decisions Made) -- not accepted.
_REJECTED_WORDS = ["Certification"]


def _acceptance_criterion_heading(method: str) -> str:
    """Build a minimal, well-formed `### AC-001 ({method}): ...` heading fixture."""
    result = f"### AC-001 ({method}): Some criterion text\n"
    return result


def _valid_dtais_text(marker: str) -> str:
    """Build a minimal, well-formed DTAIS-shaped document, tagged with `marker`.

    `marker` is embedded in the title so two calls with different markers produce
    distinguishable, but both individually valid, `parse_dtais`-accepted text.
    """
    result = f"""# {marker}

The five valid `### AC-NNN (Method): ...` method words used by `vcr`'s
`## Acceptance Criteria`:

- `Demonstration` -- observing the system in operation.
- `Test` -- exercising the system under controlled conditions.
- `Analysis` -- using calculation, modeling, or simulation.
- `Inspection` -- visual or procedural examination of the system.
- `Special` -- any other verification approach not covered above.

## When to apply each method

- **`Demonstration`** -- use when the criterion is about observable behavior.
- **`Test`** -- use when the criterion states a quantitative threshold.
- **`Analysis`** -- use when direct observation is not practical.
- **`Inspection`** -- use when the criterion is about the presence of an artifact.
- **`Special`** -- use for verification approaches outside the other four.

## Relationship to `## Coverage`

`## Coverage` is the document-level roll-up of every criterion's status.

- **`full`** -- every acceptance criterion has been verified.
- **`partial`** -- at least one criterion has been verified, but not all.
- **`none`** -- no acceptance criterion has been successfully verified yet.

`## Coverage` always reflects the least-verified criterion in the set.
"""
    return result


class TestDtaisResource(unittest.TestCase):
    """Tests for the `dtais` resource function."""

    def test_returns_real_packaged_content(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = dtais

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("# DTAIS"))
        self.assertIn("## When to apply each method", result)
        self.assertIn("## Relationship to `## Coverage`", result)

    def test_documents_exactly_the_five_valid_dtais_words(self):
        """The documented valid-word bullets must be exactly the model's closed DTAIS set."""
        result = dtais()

        words = _VALID_WORD_BULLET.findall(result)

        self.assertEqual(words, _EXPECTED_DTAIS_WORDS)

    def test_documented_words_are_accepted_by_the_model(self):
        """Every documented word must parse through `AcceptanceCriterion`'s own alias/regex."""
        for word in _EXPECTED_DTAIS_WORDS:
            with self.subTest(word=word):
                sut = AcceptanceCriterion.from_text(format_text(_acceptance_criterion_heading(word)))

                self.assertEqual(sut.method, word)

    def test_documented_rejected_words_are_rejected_by_the_model(self):
        """Every word the resource does not document must fail `AcceptanceCriterion`'s alias match."""
        for word in _REJECTED_WORDS:
            with self.subTest(word=word):
                with self.assertRaises(AssertionError):
                    AcceptanceCriterion.from_text(format_text(_acceptance_criterion_heading(word)))

    def test_mentions_coverage_full_partial_none(self):
        """The `## Coverage` interaction section must name all three closed coverage values."""
        result = dtais()
        for value in ("full", "partial", "none"):
            self.assertIn(f"**`{value}`**", result)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        first_text = _valid_dtais_text("First Marker")
        second_text = _valid_dtais_text("Second Marker")

        with tempfile.TemporaryDirectory() as tmp:
            dtais_path = Path(tmp) / "general_dtais.md"
            dtais_path.write_text(first_text, encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=dtais_path):
                sut = dtais

                first = sut()
                dtais_path.write_text(second_text, encoding="utf-8")
                second = sut()

            self.assertEqual(first, first_text)
            self.assertEqual(second, second_text)

    def test_raises_file_not_found_when_missing(self):
        """A missing packaged general_dtais.md must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = dtais

                with self.assertRaises(FileNotFoundError):
                    sut()

    def test_raises_on_structural_drift(self):
        """A malformed packaged file must fail fast via `parse_dtais`, not return silently."""
        malformed_text = "# Not A Valid DTAIS Document\n\nThis file has no method bullets at all.\n"

        with tempfile.TemporaryDirectory() as tmp:
            dtais_path = Path(tmp) / "general_dtais.md"
            dtais_path.write_text(malformed_text, encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=dtais_path):
                sut = dtais

                with self.assertRaises((AssertionError, ValueError)):
                    sut()


if __name__ == "__main__":
    unittest.main()
