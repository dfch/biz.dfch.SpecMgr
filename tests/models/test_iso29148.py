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

"""Tests for `parse_iso29148`, exercised end-to-end against the real,
packaged ``general/data/general_iso29148.md`` (feat-173-req-iso29148-
level-set Phase 130, REQ-003/ACC-003), plus fail-fast/malformed-content
drift-guard tests, mirroring ``tests/models/test_ears.py``'s structure
and style.
"""

from __future__ import annotations

import re
import unittest

import pydantic

from biz.dfch.specmgr.general.models import Iso29148, parse_iso29148
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

#: The standard's own §5.4 mapping sentence, verbatim (the source's mixed
#: dash typography -- `BRS –` en dash, `StRS -`/`SyRS -`/`SRS -` hyphens --
#: is part of the pinned text).
_MAPPING_SENTENCE = (
    "The business requirements specification (BRS), the stakeholder requirements specification (StRS), "
    "the system requirements specification (SyRS) and the software requirements specification (SRS) are "
    "intended to represent different sets of requirement information items. The specifications correspond "
    "to the requirements in Figure 3 as follows: BRS – Business Requirement (business management level); "
    "StRS - Stakeholder Requirement (business operational level); SyRS - System Requirements; and SRS - "
    "Software Requirements."
)


def _valid_iso29148_text(marker: str = "ISO/IEC/IEEE 29148:2018 Requirement Specifications") -> str:
    """Build a minimal, well-formed ISO 29148-shaped document, tagged with `marker`.

    `marker` is embedded in the title so two calls with different markers produce
    distinguishable, but both individually valid, `parse_iso29148`-accepted text.
    """
    result = f"""# {marker}

ISO/IEC/IEEE 29148:2018 defines four requirement specifications.

## The four requirement specifications

{_MAPPING_SENTENCE}

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


class TestParseIso29148(unittest.TestCase):
    """Tests for `parse_iso29148` against the packaged ISO 29148 guidance data."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read_packaged_text("general", "iso29148", "md")

    def test_returns_iso29148_instance(self):
        """The parser must return an `Iso29148` instance."""
        result = parse_iso29148(self.text)
        self.assertIsInstance(result, Iso29148)

    def test_has_four_specifications_and_four_when_to_use_items(self):
        """Exactly 4 specification bullets and exactly 4 'when to use' bullets."""
        result = parse_iso29148(self.text)
        self.assertEqual(len(result.specifications.items), 4)
        self.assertEqual(len(result.when_to_use.items), 4)

    def test_has_five_characteristics(self):
        """Exactly 5 characteristic bullets."""
        result = parse_iso29148(self.text)
        self.assertEqual(len(result.characteristics.items), 5)

    def test_specification_abbreviations(self):
        """The 4 specification abbreviations must be exactly the closed ISO 29148 §3.2 vocabulary, in order."""
        result = parse_iso29148(self.text)
        abbreviations = [item.abbreviation for item in result.specifications.items]
        self.assertEqual(abbreviations, _EXPECTED_ABBREVIATIONS)

    def test_when_to_use_abbreviations_match_specifications(self):
        """The 'when to use' abbreviations must match the specifications list's abbreviations, in order."""
        result = parse_iso29148(self.text)
        abbreviations = [item.abbreviation for item in result.when_to_use.items]
        self.assertEqual(abbreviations, _EXPECTED_ABBREVIATIONS)

    def test_characteristic_names(self):
        """The 5 characteristic names must be exactly the closed ISO 29148 §5.2.6 vocabulary, in order."""
        result = parse_iso29148(self.text)
        names = [item.characteristic for item in result.characteristics.items]
        self.assertEqual(names, _EXPECTED_CHARACTERISTICS)

    def test_mapping_sentence_is_verbatim(self):
        """The packaged file must carry the standard's §5.4 mapping sentence verbatim (mixed dash typography included)."""
        normalized = re.sub(r"\s+", " ", self.text)
        self.assertIn(_MAPPING_SENTENCE, normalized)

    def test_raises_on_reordered_specifications(self):
        """A specifications list with two kinds swapped must fail fast (the closed ordered vocabulary)."""
        text = _valid_iso29148_text()
        st_rs = "- **StRS** -- Stakeholder Requirements Specification. The stakeholder level's specification."
        sy_rs = "- **SyRS** -- System Requirements Specification. The system level's specification."
        text = text.replace(st_rs, "@@SWAP@@").replace(sy_rs, st_rs).replace("@@SWAP@@", sy_rs)

        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_iso29148(text)

    def test_raises_on_mismatched_when_to_use(self):
        """A 'when to use' list with two entries swapped must fail fast (the strict ordered cross-check)."""
        text = _valid_iso29148_text()
        st_rs = "- **`StRS`** -- use for stakeholder needs."
        sy_rs = "- **`SyRS`** -- use for system behaviour."
        text = text.replace(st_rs, "@@SWAP@@").replace(sy_rs, st_rs).replace("@@SWAP@@", sy_rs)

        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_iso29148(text)

    def test_raises_on_missing_obligation_section(self):
        """A document with the `## Requirement obligation` section dropped must fail fast (the position pin)."""
        text = _valid_iso29148_text()
        start = text.index("## Requirement obligation")
        end = text.index("## Characteristics of a set of requirements")
        text = text[:start] + text[end:]

        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_iso29148(text)

    def test_raises_on_reordered_sections(self):
        """A document with two `##` sections swapped must fail fast (the declaration-order pin)."""
        text = _valid_iso29148_text()
        mapping_start = text.index("## Mapping to specmgr document types")
        obligation_start = text.index("## Requirement obligation")
        characteristics_start = text.index("## Characteristics of a set of requirements")
        mapping_block = text[mapping_start:obligation_start]
        obligation_block = text[obligation_start:characteristics_start]
        text = text[:mapping_start] + obligation_block + mapping_block + text[characteristics_start:]

        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_iso29148(text)

    def test_raises_on_renamed_characteristic(self):
        """A characteristics list with one name outside the closed §5.2.6 vocabulary must fail fast."""
        text = _valid_iso29148_text()
        text = text.replace("**`Able to be validated`**", "**`Validatable`**")

        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_iso29148(text)

    def test_raises_on_sixth_specification(self):
        """A specifications list with a sixth, out-of-vocabulary kind must fail fast."""
        text = _valid_iso29148_text()
        text = text.replace(
            "- **SRS** -- Software Requirements Specification. The software level's specification.",
            "- **SRS** -- Software Requirements Specification. The software level's specification.\n"
            "- **XRS** -- Extra Requirements Specification. An out-of-vocabulary sixth kind.",
        )

        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_iso29148(text)

    def test_raises_on_mapping_sentence_dash_typography_change(self):
        """The §5.4 sentence with its en dash normalized to a hyphen must fail fast (the verbatim pin)."""
        text = _valid_iso29148_text()
        text = text.replace("BRS – Business Requirement", "BRS - Business Requirement")

        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_iso29148(text)


if __name__ == "__main__":
    unittest.main()
