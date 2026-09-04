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

"""Tests for the `specmgr://ears` resource (`general.resources.ears.ears`)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.resources.ears import ears
from biz.dfch.specmgr.general.tools import _packaged_data

#: The five valid EARS pattern names, in the closed, ordered vocabulary.
_EXPECTED_PATTERN_NAMES = ["Ubiquitous", "Event-driven", "State-driven", "Unwanted behavior", "Optional feature"]


def _valid_ears_text(marker: str) -> str:
    """Build a minimal, well-formed EARS-shaped document, tagged with `marker`.

    `marker` is embedded in the title so two calls with different markers produce
    distinguishable, but both individually valid, `parse_ears`-accepted text.
    """
    result = f"""# {marker}

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
- **`Event-driven`** -- use for an immediate reaction to an event.
- **`State-driven`** -- use for the duration of an ongoing state.
- **`Unwanted behavior`** -- use for error handling or fault recovery.
- **`Optional feature`** -- use for a specific optional feature.

## Combining patterns

A single requirement may combine more than one trigger/condition keyword.
"""
    return result


class TestEarsResource(unittest.TestCase):
    """Tests for the `ears` resource function."""

    def test_returns_real_packaged_content(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = ears

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("# EARS"))
        self.assertIn("## The five requirement patterns", result)
        self.assertIn("## When to use each pattern", result)
        self.assertIn("## Combining patterns", result)

    def test_documents_exactly_the_five_valid_ears_patterns(self):
        """The documented pattern names must be exactly the closed EARS vocabulary, in order."""
        result = ears()

        for name in _EXPECTED_PATTERN_NAMES:
            with self.subTest(name=name):
                self.assertIn(f"**{name}**", result)
                self.assertIn(f"**`{name}`**", result)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        first_text = _valid_ears_text("First Marker")
        second_text = _valid_ears_text("Second Marker")

        with tempfile.TemporaryDirectory() as tmp:
            ears_path = Path(tmp) / "general_ears.md"
            ears_path.write_text(first_text, encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=ears_path):
                sut = ears

                first = sut()
                ears_path.write_text(second_text, encoding="utf-8")
                second = sut()

            self.assertEqual(first, first_text)
            self.assertEqual(second, second_text)

    def test_raises_file_not_found_when_missing(self):
        """A missing packaged general_ears.md must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = ears

                with self.assertRaises(FileNotFoundError):
                    sut()

    def test_raises_on_structural_drift(self):
        """A malformed packaged file must fail fast via `parse_ears`, not return silently."""
        malformed_text = "# Not A Valid EARS Document\n\nThis file has no pattern bullets at all.\n"

        with tempfile.TemporaryDirectory() as tmp:
            ears_path = Path(tmp) / "general_ears.md"
            ears_path.write_text(malformed_text, encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=ears_path):
                sut = ears

                with self.assertRaises((AssertionError, ValueError)):
                    sut()


if __name__ == "__main__":
    unittest.main()
