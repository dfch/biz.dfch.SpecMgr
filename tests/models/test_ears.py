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

"""Tests for `parse_ears`, exercised end-to-end against the real, packaged
``general/data/general_ears.md`` (feat-92-resources Task 6.2, REQ-006),
plus fail-fast/malformed-content drift-guard tests (ACC-006), mirroring
``tests/models/test_dtais.py``'s structure and style.
"""

from __future__ import annotations

import unittest

import pydantic

from biz.dfch.specmgr.general.models import Ears, parse_ears
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text

#: The five valid EARS pattern names, in the closed, ordered vocabulary.
_EXPECTED_PATTERN_NAMES = ["Ubiquitous", "Event-driven", "State-driven", "Unwanted behavior", "Optional feature"]

#: A deliberately malformed document: only 4 of the required 5 "The five
#: requirement patterns" bullets, so `Patterns.items`'s
#: `min_length=5`/`max_length=5` constraint rejects it.
_MISSING_PATTERN_TEXT = """# EARS Requirement-Phrasing Templates

EARS is a small set of sentence templates for writing individual
requirements in unambiguous, testable natural language.

## The five requirement patterns

- **Ubiquitous** -- `The <system name> shall <system response>.` Always active.
- **Event-driven** -- `When <trigger>, the <system name> shall <system response>.` Event-triggered.
- **State-driven** -- `While <precondition>, the <system name> shall <system response>.` State-scoped.
- **Unwanted behavior** -- `If <trigger>, then the <system name> shall <system response>.` Guards against faults.

## When to use each pattern

- **`Ubiquitous`** -- use for a requirement with no meaningful trigger.
- **`Event-driven`** -- use for an immediate reaction to an event.
- **`State-driven`** -- use for the duration of an ongoing state.
- **`Unwanted behavior`** -- use for error handling or fault recovery.
- **`Optional feature`** -- use for a specific optional feature.

## Combining patterns

A single requirement may combine more than one trigger/condition keyword.
"""

#: A deliberately malformed document: the "when to use" list's words are
#: out of order relative to the "The five requirement patterns" list, so
#: `Ears._validate_when_to_use_matches_patterns` rejects it.
_MISMATCHED_WHEN_TO_USE_TEXT = """# EARS Requirement-Phrasing Templates

EARS is a small set of sentence templates for writing individual
requirements in unambiguous, testable natural language.

## The five requirement patterns

- **Ubiquitous** -- `The <system name> shall <system response>.` Always active.
- **Event-driven** -- `When <trigger>, the <system name> shall <system response>.` Event-triggered.
- **State-driven** -- `While <precondition>, the <system name> shall <system response>.` State-scoped.
- **Unwanted behavior** -- `If <trigger>, then the <system name> shall <system response>.` Guards against faults.
- **Optional feature** -- `Where <feature is included>, the <system name> shall <system response>.` Feature-conditional.

## When to use each pattern

- **`Ubiquitous`** -- use for a requirement with no meaningful trigger.
- **`State-driven`** -- use for the duration of an ongoing state.
- **`Event-driven`** -- use for an immediate reaction to an event.
- **`Unwanted behavior`** -- use for error handling or fault recovery.
- **`Optional feature`** -- use for a specific optional feature.

## Combining patterns

A single requirement may combine more than one trigger/condition keyword.
"""

#: A deliberately malformed document: the "The five requirement patterns"
#: list has 5 entries, but one (`Guard clause`) is not in the closed EARS
#: vocabulary, so `Patterns._validate_patterns` rejects it.
_WRONG_PATTERN_NAME_TEXT = """# EARS Requirement-Phrasing Templates

EARS is a small set of sentence templates for writing individual
requirements in unambiguous, testable natural language.

## The five requirement patterns

- **Ubiquitous** -- `The <system name> shall <system response>.` Always active.
- **Event-driven** -- `When <trigger>, the <system name> shall <system response>.` Event-triggered.
- **State-driven** -- `While <precondition>, the <system name> shall <system response>.` State-scoped.
- **Guard clause** -- `If <trigger>, then the <system name> shall <system response>.` Guards against faults.
- **Optional feature** -- `Where <feature is included>, the <system name> shall <system response>.` Feature-conditional.

## When to use each pattern

- **`Ubiquitous`** -- use for a requirement with no meaningful trigger.
- **`Event-driven`** -- use for an immediate reaction to an event.
- **`State-driven`** -- use for the duration of an ongoing state.
- **`Guard clause`** -- use for error handling or fault recovery.
- **`Optional feature`** -- use for a specific optional feature.

## Combining patterns

A single requirement may combine more than one trigger/condition keyword.
"""


class TestParseEars(unittest.TestCase):
    """Tests for `parse_ears` against the packaged EARS guidance data."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read_packaged_text("general", "ears", "md")

    def test_returns_ears_instance(self):
        """The parser must return an `Ears` instance."""
        result = parse_ears(self.text)
        self.assertIsInstance(result, Ears)

    def test_has_five_patterns_and_five_when_to_use_items(self):
        """Exactly 5 pattern bullets and exactly 5 'when to use' bullets."""
        result = parse_ears(self.text)
        self.assertEqual(len(result.patterns.items), 5)
        self.assertEqual(len(result.when_to_use.items), 5)

    def test_pattern_names(self):
        """The 5 pattern names must be exactly the closed EARS vocabulary, in order."""
        result = parse_ears(self.text)
        names = [item.name for item in result.patterns.items]
        self.assertEqual(names, _EXPECTED_PATTERN_NAMES)

    def test_pattern_templates(self):
        """Every pattern's template must be a non-empty, backticked sentence template."""
        result = parse_ears(self.text)
        for item in result.patterns.items:
            with self.subTest(name=item.name):
                self.assertTrue(item.template.startswith("`"))
                self.assertTrue(item.template.endswith("`"))

    def test_when_to_use_names_match_patterns(self):
        """The 'when to use' names must match the patterns list's names, in order."""
        result = parse_ears(self.text)
        names = [item.name for item in result.when_to_use.items]
        self.assertEqual(names, _EXPECTED_PATTERN_NAMES)

    def test_raises_on_missing_pattern(self):
        """A document with only 4 of the 5 required pattern bullets must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_ears(_MISSING_PATTERN_TEXT)

    def test_raises_on_mismatched_when_to_use(self):
        """A 'when to use' list out of order relative to the patterns list must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_ears(_MISMATCHED_WHEN_TO_USE_TEXT)

    def test_raises_on_wrong_pattern_name(self):
        """A patterns list with a name not in the closed vocabulary must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_ears(_WRONG_PATTERN_NAME_TEXT)


if __name__ == "__main__":
    unittest.main()
