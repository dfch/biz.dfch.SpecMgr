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
missing packaged file). No drift-guard test is needed here: unlike
`rsk/tara` (whose four documented TARA words are validated by
`rsk.models.v1.body.Strategy`'s closed set), no Pydantic field
independently validates against the RASCI role vocabulary -- the resource
is generic framework guidance, not a closed-set mirror of a model field.

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
        with tempfile.TemporaryDirectory() as tmp:
            rasci_path = Path(tmp) / "general_rasci.md"
            rasci_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=rasci_path):
                sut = rasci

                first = sut()
                rasci_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_missing(self):
        """A missing packaged general_rasci.md must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = rasci

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
