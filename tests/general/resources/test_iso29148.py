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

"""Tests for the `specmgr://iso29148` resource (`general.resources.iso29148.iso29148`)."""

import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.resources.iso29148 import iso29148
from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text

#: The four valid ISO 29148 §3.2 abbreviations, in the closed, ordered
#: vocabulary.
_EXPECTED_ABBREVIATIONS = ["BRS", "StRS", "SyRS", "SRS"]

#: The five valid ISO 29148 §5.2.6 characteristic names, in the closed,
#: ordered vocabulary.
_EXPECTED_CHARACTERISTICS = [
    "Complete",
    "Consistent",
    "Feasible",
    "Comprehensible",
    "Able to be validated",
]


def _valid_iso29148_text(marker: str) -> str:
    """Build a minimal, well-formed ISO 29148-shaped document, tagged with `marker`.

    `marker` is embedded in the title so two calls with different markers produce
    distinguishable, but both individually valid, `parse_iso29148`-accepted text.
    """
    result = f"""# {marker}

ISO/IEC/IEEE 29148:2018 defines four requirement specifications.

## The four requirement specifications

The business requirements specification (BRS), the stakeholder requirements specification (StRS), the system requirements specification (SyRS) and the software requirements specification (SRS) are intended to represent different sets of requirement information items. The specifications correspond to the requirements in Figure 3 as follows: BRS – Business Requirement (business management level); StRS - Stakeholder Requirement (business operational level); SyRS - System Requirements; and SRS - Software Requirements.

- **BRS** -- Business Requirements Specification. The business level's specification.
- **StRS** -- Stakeholder Requirements Specification. The stakeholder level's specification.
- **SyRS** -- System Requirements Specification. The system level's specification.
- **SRS** -- Software Requirements Specification. The software level's specification.

## When to use each

- **`BRS`** -- use for business-level goals.
- **`StRS`** -- use for stakeholder needs.
- **`SyRS`** -- use for system behaviour.
- **`SRS`** -- use for software behaviour.

## Mapping to specmgr document types

- `StRS` maps to `qa`.
- `SyRS` maps to `sysrs`.
- `SRS` maps to `req`.
- `BRS` maps to `gol`.

## Requirement obligation

Obligation is carried by the statement's phrasing; `shall` expresses it.

## Characteristics of a set of requirements

The §5.2.6 list, the input guidance for examining a requirement set.

- **`Complete`** -- nothing missing.
- **`Consistent`** -- no contradictions.
- **`Feasible`** -- realizable.
- **`Comprehensible`** -- understandable.
- **`Able to be validated`** -- a means to validate exists.
"""
    return result


class TestIso29148Resource(unittest.TestCase):
    """Tests for the `iso29148` resource function."""

    def test_returns_real_packaged_content(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = iso29148

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("# ISO/IEC/IEEE 29148"))
        self.assertIn("## The four requirement specifications", result)
        self.assertIn("## When to use each", result)
        self.assertIn("## Mapping to specmgr document types", result)
        self.assertIn("## Requirement obligation", result)
        self.assertIn("## Characteristics of a set of requirements", result)

    def test_returns_the_packaged_file_verbatim(self):
        """The resource must return the packaged file's text unchanged, byte-identical."""
        result = iso29148()

        self.assertEqual(result, read_packaged_text("general", "iso29148"))

    def test_documents_exactly_the_four_closed_abbreviations(self):
        """The documented abbreviations must be exactly the closed ISO 29148 §3.2 vocabulary."""
        result = iso29148()

        for abbreviation in _EXPECTED_ABBREVIATIONS:
            with self.subTest(abbreviation=abbreviation):
                self.assertIn(f"**{abbreviation}**", result)
                self.assertIn(f"**`{abbreviation}`**", result)

    def test_documents_exactly_the_five_closed_characteristics(self):
        """The documented characteristic names must be exactly the closed ISO 29148 §5.2.6 vocabulary."""
        result = iso29148()

        for name in _EXPECTED_CHARACTERISTICS:
            with self.subTest(name=name):
                self.assertIn(f"**`{name}`**", result)

    def test_mapping_sentence_is_verbatim(self):
        """The §5.4 mapping sentence must be present verbatim (mixed dash typography included)."""
        result = iso29148()
        sentence = (
            "The business requirements specification (BRS), the stakeholder requirements specification (StRS), "
            "the system requirements specification (SyRS) and the software requirements specification (SRS) are "
            "intended to represent different sets of requirement information items. The specifications correspond "
            "to the requirements in Figure 3 as follows: BRS – Business Requirement (business management level); "
            "StRS - Stakeholder Requirement (business operational level); SyRS - System Requirements; and SRS - "
            "Software Requirements."
        )

        self.assertIn(sentence, re.sub(r"\s+", " ", result))

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        first_text = _valid_iso29148_text("First Marker")
        second_text = _valid_iso29148_text("Second Marker")

        with tempfile.TemporaryDirectory() as tmp:
            iso29148_path = Path(tmp) / "general_iso29148.md"
            iso29148_path.write_text(first_text, encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=iso29148_path):
                sut = iso29148

                first = sut()
                iso29148_path.write_text(second_text, encoding="utf-8")
                second = sut()

            self.assertEqual(first, first_text)
            self.assertEqual(second, second_text)

    def test_raises_file_not_found_when_missing(self):
        """A missing packaged general_iso29148.md must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = iso29148

                with self.assertRaises(FileNotFoundError):
                    sut()

    def test_raises_on_structural_drift(self):
        """A malformed packaged file must fail fast via `parse_iso29148`, not return silently."""
        malformed_text = "# Not A Valid ISO 29148 Document\n\nThis file has no sections at all.\n"

        with tempfile.TemporaryDirectory() as tmp:
            iso29148_path = Path(tmp) / "general_iso29148.md"
            iso29148_path.write_text(malformed_text, encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=iso29148_path):
                sut = iso29148

                with self.assertRaises((AssertionError, ValueError)):
                    sut()


if __name__ == "__main__":
    unittest.main()
