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

"""Tests for the `specmgr://rasci` resource (`general.resources.rasci.rasci`).

Mirrors `tests/rsk/resources/test_tara.py`'s non-drift-guard tests
(real-content assertions, fresh-read-per-call, `FileNotFoundError` on a
missing packaged file). Since feat-92-resources Phase 5, `rasci` also
gains a dedicated `general.models.rasci.Rasci` model, parsed on every
resource call purely to fail fast on structural drift (ADR
356d8781-e446-4c26-917a-eda85648ce9d) -- see
`test_raises_on_structural_drift` below, mirroring
`tests/general/resources/test_dtais.py`'s equivalent test.

ACC-010 additionally requires the content to be genuinely generic (no
`sop`-specific structural rule leaked in), covered by
`test_content_is_generic_no_sop_specific_rules`.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.resources.rasci import rasci
from biz.dfch.specmgr.general.tools import _packaged_data

#: The five RASCI role names the resource must define, in their canonical
#: spelling. The content must mention each one.
_RASCI_ROLES = ["Responsible", "Accountable", "Support", "Consulted", "Informed"]

#: `sop`-specific structural text that must NOT appear in the generic
#: RASCI guidance -- these are `sop`'s own binding headings/cardinality,
#: which stay exclusively in `sop`'s schema/instructions (ACC-010).
_SOP_SPECIFIC_STRUCTURAL = [
    "## Procedure",
    "### Step ",
    "## Roles and Responsibilities",
    "### Accountable",
    "### Responsible",
    "### Support",
    "### Consulted",
    "### Informed",
]


def _valid_rasci_text(marker: str) -> str:
    """Build a minimal, well-formed RASCI-shaped document, tagged with `marker`.

    `marker` is embedded in the title so two calls with different markers produce
    distinguishable, but both individually valid, `parse_rasci`-accepted text.
    """
    result = f"""# {marker}

RASCI is a responsibility-assignment framework that names, for a given
piece of work, who does it, who owns it, who helps, who is consulted, and
who is kept informed.

## The five roles

- **Responsible** -- the people who do the work.
- **Accountable** -- the single owner who is ultimately answerable for the
  work.
- **Support** -- the people who provide resources, tooling, or assistance.
- **Consulted** -- the people whose opinions are sought before or during
  the work.
- **Informed** -- the people who are kept up to date on progress.

## RASCI vs. plain RACI

Plain RACI names four roles -- Responsible, Accountable, Consulted, and
Informed. RASCI adds the fifth, **S**upport role.
"""
    return result


class TestRasciResource(unittest.TestCase):
    """Tests for the `rasci` resource function."""

    def test_returns_real_packaged_content(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = rasci

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("# RASCI"))
        for role in _RASCI_ROLES:
            with self.subTest(role=role):
                self.assertIn(role, result)
        self.assertIn("RACI", result)

    def test_content_is_generic_no_sop_specific_rules(self):
        """ACC-010: the guidance must not carry any `sop`-specific structural rule."""
        result = rasci()

        for sop_specific in _SOP_SPECIFIC_STRUCTURAL:
            with self.subTest(sop_specific=sop_specific):
                self.assertNotIn(sop_specific, result)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        first_text = _valid_rasci_text("First Marker")
        second_text = _valid_rasci_text("Second Marker")

        with tempfile.TemporaryDirectory() as tmp:
            rasci_path = Path(tmp) / "general_rasci.md"
            rasci_path.write_text(first_text, encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=rasci_path):
                sut = rasci

                first = sut()
                rasci_path.write_text(second_text, encoding="utf-8")
                second = sut()

            self.assertEqual(first, first_text)
            self.assertEqual(second, second_text)

    def test_raises_file_not_found_when_missing(self):
        """A missing packaged general_rasci.md must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = rasci

                with self.assertRaises(FileNotFoundError):
                    sut()

    def test_raises_on_structural_drift(self):
        """A malformed packaged file must fail fast via `parse_rasci`, not return silently."""
        malformed_text = "# Not A Valid RASCI Document\n\nThis file has no role bullets at all.\n"

        with tempfile.TemporaryDirectory() as tmp:
            rasci_path = Path(tmp) / "general_rasci.md"
            rasci_path.write_text(malformed_text, encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=rasci_path):
                sut = rasci

                with self.assertRaises((AssertionError, ValueError)):
                    sut()


if __name__ == "__main__":
    unittest.main()
