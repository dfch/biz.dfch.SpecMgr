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

"""Tests for the `specmgr://sysrs/example` resource (`sysrs.resources.sysrs_example.sysrs_example`)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.sysrs.models.v1 import parse_sysrs
from biz.dfch.specmgr.sysrs.resources.sysrs_example import sysrs_example
from biz.dfch.specmgr.sysrs.tools.get_sysrs_example import get_sysrs_example


class TestSysrsExampleResource(unittest.TestCase):
    """Tests for the sysrs_example resource function."""

    def test_returns_real_packaged_example(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = sysrs_example

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: sysrs", result)
        self.assertIn("# System Requirements Specification: Example Widget Platform", result)

    def test_matches_packaged_file_byte_for_byte(self):
        """ACC-007: the resource must equal the packaged sysrs_example.md byte-for-byte."""
        sut = sysrs_example

        result = sut()

        packaged = _packaged_data.packaged_data_path("sysrs", "example").read_text(encoding="utf-8")
        self.assertEqual(result, packaged)

    def test_matches_the_get_sysrs_example_tool(self):
        """The resource and the tool must return identical content -- same underlying reader."""
        self.assertEqual(sysrs_example(), get_sysrs_example())

    def test_packaged_example_parses_and_exercises_every_section(self):
        """The committed example must parse via parse_sysrs and exercise the expected sections."""
        document = parse_sysrs(sysrs_example())

        self.assertEqual(document.frontmatter.status, "draft")
        self.assertEqual(document.frontmatter.type, "sysrs")

        body = document.body
        self.assertIsNotNone(body.business_context_and_goals)
        self.assertIsNotNone(body.business_context_and_goals.business_context)
        self.assertGreaterEqual(len(body.business_context_and_goals.goals.items), 1)
        self.assertIsNotNone(body.business_context_and_goals.problem_statement)
        self.assertIsNotNone(body.stakeholder_needs_and_elicitation)
        self.assertIsNotNone(body.operational_concept_and_scenarios)
        self.assertIsNotNone(body.decisions)
        self.assertIsNotNone(body.risks)

        self.assertIsNotNone(body.system_overview.system_context)
        self.assertIsNotNone(body.system_overview.system_functions)
        self.assertIsNotNone(body.system_overview.user_characteristics)
        self.assertIsNotNone(body.system_overview.system_integration)

        requirements = body.requirements
        self.assertIsNotNone(requirements.functional_suitability)
        self.assertIsNotNone(requirements.performance_efficiency)
        self.assertIsNotNone(requirements.compatibility)
        self.assertIsNotNone(requirements.interaction_capability)
        self.assertIsNotNone(requirements.reliability)
        self.assertIsNotNone(requirements.security)
        self.assertIsNotNone(requirements.maintainability)
        self.assertIsNotNone(requirements.flexibility)
        self.assertIsNotNone(requirements.safety)

        other_characteristics = body.other_characteristics
        self.assertIsNotNone(other_characteristics)
        self.assertIsNotNone(other_characteristics.physical_characteristics)
        self.assertIsNotNone(other_characteristics.environmental_conditions)
        self.assertIsNotNone(other_characteristics.information_management)
        self.assertIsNotNone(other_characteristics.policy_and_regulation)
        self.assertIsNotNone(other_characteristics.system_life_cycle_sustainment)
        self.assertIsNotNone(other_characteristics.packaging_handling_shipping_and_transportation)

        self.assertIsNotNone(body.verification)
        self.assertIsNotNone(body.references)
        self.assertIsNotNone(body.more_information)
        self.assertIsNotNone(body.appendix)
        self.assertIsNotNone(body.definitions_and_acronyms)

        updates = body.updates
        self.assertIsNotNone(updates)
        self.assertEqual(len(updates.updates), 2)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "sysrs_example.md"
            example_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=example_path):
                sut = sysrs_example

                first = sut()
                example_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_example_missing(self):
        """A missing packaged example file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = sysrs_example

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
