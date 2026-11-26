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

"""Tests for the `specmgr://rsk/tara` resource (`rsk.resources.tara.tara`)."""

import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.rsk.models.v1 import Strategy
from biz.dfch.specmgr.rsk.resources.tara import tara

#: A bullet line holding exactly one backticked lowercase word -- the shape the
#: resource uses to document the four valid `## Strategy` words verbatim.
_VALID_WORD_BULLET = re.compile(r"^- `([a-z]+)`$", re.MULTILINE)

#: The four words the resource must document as the closed TARA set, in order.
_EXPECTED_TARA_WORDS = ["transfer", "accept", "reduce", "avoid"]

#: TARRA-era words the resource explicitly calls out as *not* accepted.
_REJECTED_WORDS = ["tolerate", "assign", "recover"]


def _valid_tara_text(marker: str) -> str:
    """Build a minimal, well-formed TARA-shaped document, tagged with `marker`.

    `marker` is embedded in the title so two calls with different markers produce
    distinguishable, but both individually valid, `parse_tara`-accepted text.
    """
    result = f"""# {marker}

`rsk` documents (risk register entries) carry a mandatory `## Strategy`
section with exactly one lowercase word naming the TARA response chosen for
the risk. **TARA** is the risk-response framework: **T**ransfer, **A**ccept,
**R**educe, **A**void. Only the four valid words below are accepted by the
schema -- anything else (including the TARRA-era words `tolerate`, `assign`,
`recover`, or any capitalized/compound variant) is a validation error:

- `transfer`
- `accept`
- `reduce`
- `avoid`

## When to apply each strategy

Read the risk's matrix coordinates (`## Initial Assessment`, see the risk
matrix document) to pick a strategy:

- **Low probability / high impact → `transfer`**
  The risk is unlikely but would be severe if it hit.
- **High probability / high impact → `avoid`**
  The risk is both likely and severe.
- **High probability / low impact → `reduce`**
  The risk is likely but the consequence is bounded.
- **Low probability / low impact → `accept`**
  The risk is unlikely and bounded.

The four quadrants are a guideline, not a rule -- the documented
rationale of the choice matters more than the quadrant label.

## Interaction with `## Mitigation`

`## Mitigation` is the treatment section between the two assessments.

- `reduce`: concrete measures are mandatory.
- `transfer`: name the transfer mechanism.
- `avoid`: describe what is eliminated.
- `accept`: write `none` — acceptance means no treatment is taken.

## Interaction with the frontmatter `status`

The `rsk` frontmatter `status` is a six-value lifecycle:

- `open` — identified and monitored; no treatment decided or started yet.
- `mitigating` — treatment is in progress.
- `accepted` — the residual risk is formally accepted.
- `occurred` — the risk event materialized.
- `closed` — resolved or expired.
- `dropped` — removed from the register.

`status` tracks the lifecycle state of the entry; `strategy` tracks the
chosen response. They are independent fields.
"""
    return result


class TestRskTaraResource(unittest.TestCase):
    """Tests for the `tara` resource function."""

    def test_returns_real_packaged_content(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = tara

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("# TARA"))
        self.assertIn("## When to apply each strategy", result)
        self.assertIn("## Interaction with `## Mitigation`", result)
        self.assertIn("## Interaction with the frontmatter `status`", result)

    def test_documents_exactly_the_four_valid_tara_words(self):
        """The documented valid-word bullets must be exactly the model's closed TARA set."""
        result = tara()

        words = _VALID_WORD_BULLET.findall(result)

        self.assertEqual(words, _EXPECTED_TARA_WORDS)

    def test_documented_words_are_accepted_by_the_model(self):
        """Every documented word must parse through `Strategy`'s own validator."""
        for word in _EXPECTED_TARA_WORDS:
            with self.subTest(word=word):
                sut = Strategy.from_text(format_text(f"## Strategy\n\n{word}\n"))

                self.assertEqual(sut.value.text, word)

    def test_documented_rejected_words_are_rejected_by_the_model(self):
        """Every word the resource calls out as invalid must fail `Strategy`'s own validator."""
        for word in _REJECTED_WORDS:
            with self.subTest(word=word):
                with self.assertRaises(ValidationError):
                    Strategy.from_text(format_text(f"## Strategy\n\n{word}\n"))

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        first_text = _valid_tara_text("First Marker")
        second_text = _valid_tara_text("Second Marker")

        with tempfile.TemporaryDirectory() as tmp:
            tara_path = Path(tmp) / "rsk_tara.md"
            tara_path.write_text(first_text, encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=tara_path):
                sut = tara

                first = sut()
                tara_path.write_text(second_text, encoding="utf-8")
                second = sut()

            self.assertEqual(first, first_text)
            self.assertEqual(second, second_text)

    def test_raises_file_not_found_when_missing(self):
        """A missing packaged rsk_tara.md must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = tara

                with self.assertRaises(FileNotFoundError):
                    sut()

    def test_raises_on_structural_drift(self):
        """A malformed packaged file must fail fast via `parse_tara`, not return silently."""
        malformed_text = "# Not A Valid TARA Document\n\nThis file has no strategy bullets at all.\n"

        with tempfile.TemporaryDirectory() as tmp:
            tara_path = Path(tmp) / "rsk_tara.md"
            tara_path.write_text(malformed_text, encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=tara_path):
                sut = tara

                with self.assertRaises((AssertionError, ValueError)):
                    sut()


if __name__ == "__main__":
    unittest.main()
