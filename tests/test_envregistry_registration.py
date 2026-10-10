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

"""Tests pinning Phase 110's real import-time registrations (feat-208, ACC-001).

Phase 100's registry started empty; Phase 110 registers all 13 environment
variables (the 12 ``SPECMGR_*`` vars plus ``FASTEMBED_CACHE_PATH``) at
import time of their nine owning modules. This test explicitly imports every
owning module at module level, so it is self-contained (green when run
alone), and pins:

* the registry contains **exactly** those 13 names,
* each record's ``default``/``format``/``choices``/
  ``empty_falls_back_to_default``/``owner`` against the Phase 110
  registration table (the ``description`` is pinned to the ``server.json``
  manifest's text verbatim by the Phase 160 documentation-coverage test,
  not duplicated here),
* the three base-dir modules' derived ``DEFAULT_*`` constants stay
  byte-identical to their pre-Phase-110 values (the registry is the single
  authority for the default; the constants are kept for the ~29 existing
  test references).

The exact-13 assertion assumes no other test module in the worker process
registers a name that survives into this read: ``tests/test_envregistry.py``
only ever registers its own test-only names inside
``_IsolatedRegistry`` subclasses, whose ``tearDown`` restores the
pre-test registry snapshot, so they can never leak. These tests read the
registry; they never register into it, so no isolation subclass is needed.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import biz.dfch.specmgr.cli  # noqa: F401 (side-effects only: SPECMGR_TESTS_NO_DOTENV registration)
import biz.dfch.specmgr.commands.mcp  # noqa: F401 (side-effects only: the three Typer MCP vars' registration)
import biz.dfch.specmgr.general.resources.config  # noqa: F401 (side-effects only: FASTEMBED_CACHE_PATH registration)
import biz.dfch.specmgr.general.tools._embedding  # noqa: F401 (side-effects only: SPECMGR_SIMILARITY_DISABLED registration)
import biz.dfch.specmgr.general.tools._startup_warmup  # noqa: F401 (side-effects only: SPECMGR_FEAT_WARMUP_DISABLED registration)
import biz.dfch.specmgr.uc.tools.validate_plantuml  # noqa: F401 (side-effects only: the plantuml trio's registration)

from biz.dfch.specmgr.adr.tools._paths import DEFAULT_ADR_DIR
from biz.dfch.specmgr.feat.tools._paths import DEFAULT_FEAT_DIR
from biz.dfch.specmgr.general.tools._doc_paths import DEFAULT_DOCS_ROOT
from biz.dfch.specmgr._envregistry import all_vars

#: The Phase 110 registration table, pinned field by field:
#: ``name -> (default, format, choices, empty_falls_back_to_default, owner)``.
#: The ``FASTEMBED_CACHE_PATH`` default is the code's own fallback
#: expression (``str(Path(tempfile.gettempdir()) / "fastembed_cache")``),
#: re-evaluated at test time -- stable within the process (no test mutates
#: ``TMPDIR``/``tempfile.tempdir``; the registration read the same way at
#: import time).
_EXPECTED_METADATA: dict[str, tuple[str | None, str | None, tuple[str, ...], bool, str]] = {
    "SPECMGR_ADR_DIR": ("docs/adr", "filepath", (), True, "adr"),
    "SPECMGR_DOCS_DIR": ("docs", "filepath", (), True, "general"),
    "SPECMGR_FEAT_DIR": (".specmgr/feat", "filepath", (), True, "feat"),
    "SPECMGR_MCP_TRANSPORT": ("stdio", None, ("stdio", "sse", "streamable-http"), False, "cli"),
    "SPECMGR_MCP_HOST": ("localhost", None, (), False, "cli"),
    "SPECMGR_MCP_PORT": ("8000", "number", (), False, "cli"),
    "SPECMGR_SIMILARITY_DISABLED": (None, None, (), False, "general"),
    "SPECMGR_FEAT_WARMUP_DISABLED": (None, None, (), False, "general"),
    "SPECMGR_PLANTUML_JAR": (None, None, (), False, "plantuml/uc"),
    "SPECMGR_PLANTUML_BIN": (None, None, (), False, "plantuml/uc"),
    "SPECMGR_PLANTUML_URL": (None, None, (), False, "plantuml/uc"),
    "SPECMGR_TESTS_NO_DOTENV": (None, None, (), False, "cli"),
    "FASTEMBED_CACHE_PATH": (
        str(Path(tempfile.gettempdir()) / "fastembed_cache"),
        "filepath",
        (),
        True,
        "general/similarity",
    ),
}


class TestPhase110Registrations(unittest.TestCase):
    """The 13 real import-time registrations, pinned against the Phase 110 table."""

    def test_registry_contains_exactly_the_13_registered_names(self):
        result = {entry.name for entry in all_vars()}

        self.assertEqual(
            result,
            set(_EXPECTED_METADATA),
            (
                f"registry names drifted from the Phase 110 table: "
                f"missing {sorted(set(_EXPECTED_METADATA) - result)}, "
                f"extra {sorted(result - set(_EXPECTED_METADATA))}"
            ),
        )

    def test_every_record_pins_the_phase_110_metadata_table(self):
        entries = {entry.name: entry for entry in all_vars()}

        for name, (default, expected_format, choices, empty_fallback, owner) in _EXPECTED_METADATA.items():
            self.assertIn(name, entries, f"{name!r} is not registered")
            entry = entries[name]
            self.assertEqual(entry.default, default, f"{name}.default drifted")
            self.assertEqual(entry.format, expected_format, f"{name}.format drifted")
            self.assertEqual(entry.choices, choices, f"{name}.choices drifted")
            self.assertEqual(
                entry.empty_falls_back_to_default, empty_fallback, f"{name}.empty_falls_back_to_default drifted"
            )
            self.assertEqual(entry.owner, owner, f"{name}.owner drifted")
            self.assertTrue(entry.description.strip(), f"{name}.description is blank")

    def test_the_three_derived_default_constants_are_byte_identical(self):
        # The base-dir modules derive their pre-existing DEFAULT_* constants
        # from the registry records (feat-208 Phase 110, the user-approved
        # Option A decision) -- the values must stay byte-identical to the
        # pre-Phase-110 literals (REQ-005: no default change).
        self.assertEqual(DEFAULT_ADR_DIR, Path("docs/adr"))
        self.assertEqual(DEFAULT_DOCS_ROOT, Path("docs"))
        self.assertEqual(DEFAULT_FEAT_DIR, Path(".specmgr/feat"))


if __name__ == "__main__":
    unittest.main()
