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
# along with this program.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""The env-gate smoke test (feat-185-uc-diagrams Task 110.100, ACC-007).

One trivial test that runs the canary through the SELECTED source when one
is available — and skips cleanly (with a reason, reported by ``pytest -rs``)
on a checkout with nothing configured or with a set-but-unavailable source.
The probe itself is session-memoised (one per pytest worker — see
``tests/conftest.py``), so this test costs at most the shared canary
round-trip.
"""

import unittest

from biz.dfch.specmgr.plantuml import backends, chain
from tests.conftest import plantuml_source, require_plantuml_source


class TestSourceGate(unittest.TestCase):
    """The gate helper + one canary round-trip through the selected source."""

    def test_gate_reports_a_selection_and_an_availability(self):
        info = plantuml_source()

        if info.available:
            self.assertIn(info.kind, ("jar", "bin", "url"))
            self.assertIsNotNone(info.value)
            self.assertIsNone(info.reason)
        else:
            self.assertIsNotNone(info.reason)
            assert info.reason is not None
            if info.kind is None:
                self.assertIn("no SPECMGR_PLANTUML_* source configured", info.reason)
            else:
                assert info.value is not None
                self.assertIn(info.value, info.reason)  # the diagnostic names the configured source

    def test_canary_round_trips_through_the_selected_source(self):
        info = require_plantuml_source(self)
        assert info.value is not None  # an available source always carries its configured value

        result = chain.validate_plantuml(backends.CANARY_DIAGRAM)

        self.assertEqual(result.checked_by, info.kind)
        self.assertTrue(result.available)
        self.assertEqual(result.source_state, chain.STATE_OK)
        self.assertTrue(result.structure_ok)
        self.assertIs(result.valid, True)
        self.assertIs(result.rendered, True)


if __name__ == "__main__":
    unittest.main()
