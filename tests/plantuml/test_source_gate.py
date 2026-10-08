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

The ``SPECMGR_TESTS_NO_DOTENV`` sentinel tests (Phase 145, the user-approved
2026-10-06 amendment C) pin the ``.env``-load skip the ``specmgr
coverage-badge`` pre-commit hook relies on: the committed badge matches the
CI condition where no ``SPECMGR_PLANTUML_*`` is configured, so the hook's
source-less re-run must not pick a source up from the local (gitignored)
``.env``.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.plantuml import backends, chain
from tests import conftest
from tests.conftest import assert_rendered_svg, plantuml_source, render_proof_body, require_plantuml_source


class TestNoDotenvSentinel(unittest.TestCase):
    """The ``SPECMGR_TESTS_NO_DOTENV`` sentinel (Phase 145, amendment C).

    Pins the ``.env``-load skip the ``specmgr coverage-badge`` pre-commit
    hook relies on: when the sentinel is set, ``_load_default_dotenv`` must
    not even look for a ``.env`` (so a local, gitignored ``.env`` cannot
    re-select a source during the hook's CI source-less re-run); when it is
    absent, the dual-lookup load runs as before.
    """

    def test_sentinel_skips_the_dotenv_lookup_entirely(self):
        with mock.patch.dict(os.environ, {conftest.NO_DOTENV_SENTINEL: "1"}):
            with mock.patch.object(conftest, "find_dotenv") as find:
                with mock.patch.object(conftest, "load_dotenv") as load:
                    conftest._load_default_dotenv()
        find.assert_not_called()
        load.assert_not_called()

    def test_without_sentinel_the_dotenv_lookup_runs(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(conftest.NO_DOTENV_SENTINEL, None)
            with mock.patch.object(conftest, "find_dotenv", return_value=None) as find:
                with mock.patch.object(conftest, "load_dotenv") as load:
                    conftest._load_default_dotenv()
        # find_dotenv(usecwd=False) returns None → falls through to find_dotenv(usecwd=True)
        self.assertEqual(find.call_count, 2)
        load.assert_not_called()  # no path found → nothing to load

    def test_without_sentinel_a_found_dotenv_is_loaded(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop(conftest.NO_DOTENV_SENTINEL, None)
                with mock.patch.object(conftest, "find_dotenv", return_value=str(Path(tmp) / ".env")) as find:
                    with mock.patch.object(conftest, "load_dotenv") as load:
                        conftest._load_default_dotenv()
            load.assert_called_once()
            self.assertEqual(find.call_count, 1)

    def test_cli_and_conftest_sentinel_names_agree(self):
        """Drift guard: the hook sets ONE env var that BOTH .env loaders must honour
        (cli.py's module-level load runs in every test process that imports it —
        without its copy of the sentinel the badge hook's source-less re-run
        would still select the local .env's source)."""
        from biz.dfch.specmgr import cli

        self.assertEqual(cli.NO_DOTENV_SENTINEL, conftest.NO_DOTENV_SENTINEL)


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
        assert info.kind is not None
        assert info.value is not None  # an available source always carries its configured value

        result = chain.validate_plantuml(backends.CANARY_DIAGRAM)

        self.assertEqual(result.checked_by, info.kind)
        self.assertTrue(result.available)
        self.assertEqual(result.source_state, chain.STATE_OK)
        self.assertTrue(result.structure_ok)
        self.assertIs(result.valid, True)
        self.assertIs(result.rendered, True)
        # the Phase 145 render-proof contract: rendered=True must mean a TRUE
        # render — the selected source's own render-proof SVG body carries the
        # canary's message text and no crash marker
        assert_rendered_svg(render_proof_body(info.kind, info.value, backends.CANARY_DIAGRAM), "hello")


if __name__ == "__main__":
    unittest.main()
