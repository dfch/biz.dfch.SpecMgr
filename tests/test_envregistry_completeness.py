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

"""Registry-to-source completeness drift guard (feat-208, REQ-003, ACC-003).

The feat-208 plan's Design Notes "Documentation tracking" names this as the first
of the two registry-anchored tests: read-site discovery is generalized from
feat-126's hardcoded `SPECMGR_` prefix to the quoted form of every registered
name (so the third-party `FASTEMBED_CACHE_PATH` is visible to the scan) union
the `SPECMGR_` prefix net (so unregistered specmgr variables are still caught),
minus the documented hosting-probe exclusion set; the scanned name set must
equal the registry name set. The failure messages name the specific variable in
both directions:

* read in `src/` but missing from the registry (an unregistered-read drift --
  a read site that bypasses the registry accessor), and
* registered but never read in `src/` (a stale-registration drift -- a
  registry entry whose read sites no longer exist).

The scan runs on the shared `tests/_env_scan.py` helper (extracted by Task
150.100 from feat-126's drift test, behaviour-preserving on its default
`SPECMGR_` name pattern), with the name pattern built at test time from
`_envregistry.all_vars()` (the helper's own `discovery_name_pattern`,
factored out of this test in Phase 160 so `tests/test_server_json.py`'s
`setUp` can share it).

Self-contained: the ten owning modules' import-time registrations (feat-208
Phase 110; `SPECMGR_DIAGRAM_MAX_TITLE`'s owning module
`general.tools._diagram_config` joined the list in the feat-207 dev sync)
are triggered by the explicit side-effect imports below -- the same
module list `tests/test_envregistry_registration.py` uses -- so this test is
green when run alone. The entry-point completeness test
(`TestEntryPointCompleteness`) additionally imports the two real entry points
-- `biz.dfch.specmgr.server` and `biz.dfch.specmgr.cli` -- at module level, so
it pins the registry's completeness in the production import context (the
`_envregistry.py` module docstring's "complete by the time any server/CLI entry
point runs" claim), not just the ten-module test context; `server` is already
in this module's import closure (the `general.resources.config` and
`uc.tools.validate_plantuml` imports above each carry `from ...server import
mcp`), so the explicit import adds no dependency. These tests read the
registry; they never register into it. The hosting probes are additionally
pinned below: they are read in `commands/mcp.py` (raw-text grep plus a
broadened-pattern scan, so their exclusion is a tested fact rather than an
unexamined literal), yet they are neither registered nor part of this test's
own discovered set.
"""

from __future__ import annotations

import unittest

import biz.dfch.specmgr.adr.tools._paths  # noqa: F401 (side-effects only: SPECMGR_ADR_DIR registration)
import biz.dfch.specmgr.cli  # noqa: F401 (side-effects only: SPECMGR_TESTS_NO_DOTENV registration)
import biz.dfch.specmgr.commands.mcp  # noqa: F401 (side-effects only: the three Typer MCP vars' registration)
import biz.dfch.specmgr.feat.tools._paths  # noqa: F401 (side-effects only: SPECMGR_FEAT_DIR registration)
import biz.dfch.specmgr.general.resources.config  # noqa: F401 (side-effects only: FASTEMBED_CACHE_PATH registration)
import biz.dfch.specmgr.general.tools._diagram_config  # noqa: F401 (side-effects only: SPECMGR_DIAGRAM_MAX_TITLE registration)
import biz.dfch.specmgr.general.tools._doc_paths  # noqa: F401 (side-effects only: SPECMGR_DOCS_DIR registration)
import biz.dfch.specmgr.general.tools._embedding  # noqa: F401 (side-effects only: SPECMGR_SIMILARITY_DISABLED registration)
import biz.dfch.specmgr.general.tools._startup_warmup  # noqa: F401 (side-effects only: SPECMGR_FEAT_WARMUP_DISABLED registration)
import biz.dfch.specmgr.server  # noqa: F401 (side-effects only: imports every domain package -- the real entry point that must leave the registry complete)
import biz.dfch.specmgr.uc.tools.validate_plantuml  # noqa: F401 (side-effects only: the plantuml trio's registration)

from biz.dfch.specmgr import _envregistry
from tests._env_scan import REPO_ROOT, discovery_name_pattern, scan_env_var_read_sites

#: The hosting-platform probe variables `commands/mcp.py`'s
#: `_warn_on_public_binding` reads (feat-185/Phase 120's container detection).
#: They are not specmgr-defined environment variables and are declared out of
#: scope by the feat-208 plan (Scope, "Explicitly Out Of Scope" -- feat-126
#: already declared them out of scope for the manifest drift test), so the
#: completeness assertion subtracts them from the discovered set. The pin
#: test below keeps this literal a tested fact: every entry must still be read
#: in `commands/mcp.py`, visible to a broadened-pattern scan, yet absent from
#: both the registry and this test's own (completeness-pattern) discovered set.
_HOSTING_PROBE_EXCLUSIONS = frozenset({"KUBERNETES_SERVICE_HOST", "RAILWAY_PROJECT_ID", "RENDER"})

#: The literal set of the 14 environment variables the registry must hold once
#: the two real entry points (`biz.dfch.specmgr.server` and
#: `biz.dfch.specmgr.cli`, imported at module level above) have run their
#: import-time registrations (feat-208 Phase 110; `SPECMGR_DIAGRAM_MAX_TITLE`
#: added by the feat-207 dev sync). Hardcoded on purpose -- not
#: derived from `_envregistry.all_vars()` or from
#: `tests/test_envregistry_registration.py`'s own table: if a future refactor
#: moves a `register()` call into a module the entry points never import (or
#: out of one they do), this set is what keeps the entry-point test below
#: meaningful (it fails naming the var, instead of silently agreeing with the
#: drifted registry).
_ENTRY_POINT_NAME_SET = frozenset(
    {
        "SPECMGR_ADR_DIR",
        "SPECMGR_DIAGRAM_MAX_TITLE",
        "SPECMGR_DOCS_DIR",
        "SPECMGR_FEAT_DIR",
        "SPECMGR_MCP_TRANSPORT",
        "SPECMGR_MCP_HOST",
        "SPECMGR_MCP_PORT",
        "SPECMGR_SIMILARITY_DISABLED",
        "SPECMGR_FEAT_WARMUP_DISABLED",
        "SPECMGR_PLANTUML_JAR",
        "SPECMGR_PLANTUML_BIN",
        "SPECMGR_PLANTUML_URL",
        "SPECMGR_TESTS_NO_DOTENV",
        "FASTEMBED_CACHE_PATH",
    }
)


class TestRegistryToSourceCompleteness(unittest.TestCase):
    """REQ-003/ACC-003: the registry and the `src/` read sites name the same set of variables."""

    def setUp(self) -> None:
        self.registered_names: set[str] = {entry.name for entry in _envregistry.all_vars()}
        sites = scan_env_var_read_sites(name_pattern=discovery_name_pattern(self.registered_names))
        self.discovered_names: set[str] = set(sites)

    def test_every_read_var_is_registered(self) -> None:
        sut = sorted((self.discovered_names - _HOSTING_PROBE_EXCLUSIONS) - self.registered_names)
        self.assertEqual(
            [],
            sut,
            "environment variables read in src/ but missing from the central env-var registry "
            "(feat-208, REQ-003/ACC-003; the only sanctioned exception is the documented "
            f"hosting-probe exclusion set {sorted(_HOSTING_PROBE_EXCLUSIONS)}): {sut}",
        )

    def test_every_registered_var_is_read(self) -> None:
        sut = sorted(self.registered_names - self.discovered_names)
        self.assertEqual(
            [],
            sut,
            "environment variables registered in the central env-var registry but never read in src/ "
            "(feat-208, REQ-003/ACC-003, stale-registration drift): " + ", ".join(sut),
        )

    def test_hosting_probes_are_read_in_commands_mcp_yet_unregistered(self) -> None:
        mcp_path = REPO_ROOT / "src" / "biz" / "dfch" / "specmgr" / "commands" / "mcp.py"
        mcp_source = mcp_path.read_text(encoding="utf-8")
        for probe in sorted(_HOSTING_PROBE_EXCLUSIONS):
            self.assertIn(
                f'os.environ.get("{probe}")',
                mcp_source,
                f"hosting probe {probe} is no longer read in commands/mcp.py -- its exclusion set "
                "entry is stale (drop it from _HOSTING_PROBE_EXCLUSIONS)",
            )
        broadened = discovery_name_pattern(self.registered_names) + "|" + "|".join(sorted(_HOSTING_PROBE_EXCLUSIONS))
        broadened_names = set(scan_env_var_read_sites(name_pattern=broadened))
        self.assertEqual(
            [],
            sorted(_HOSTING_PROBE_EXCLUSIONS - broadened_names),
            "hosting probes no longer visible to a broadened-pattern read-site scan -- the exclusion "
            "set pins reads that the scanner can no longer find",
        )
        self.assertEqual(
            [],
            sorted(_HOSTING_PROBE_EXCLUSIONS & self.registered_names),
            "hosting probes registered in the central env-var registry -- they are not specmgr-defined "
            "(feat-208 plan, Scope 'Explicitly Out Of Scope') and must stay unregistered",
        )
        self.assertEqual(
            [],
            sorted(_HOSTING_PROBE_EXCLUSIONS & self.discovered_names),
            "hosting probes in the completeness test's own discovered set -- the exclusion set "
            "must subtract them, not the name pattern",
        )


class TestEntryPointCompleteness(unittest.TestCase):
    """The two real entry points (`server`, `cli`) leave the registry complete.

    Every other registry-backed test in this feature imports the ten owning
    modules directly (a documented self-containment choice, see the module
    docstring). If a future refactor moved a `register()` call into a module
    neither entry point imports, the registry would be silently incomplete in
    production while those tests stayed green. This test's own imports are the
    entry points themselves (module level above, so they run no matter which
    other tests the worker process collected first), and the assertion is
    against the literal 14-name set (`_ENTRY_POINT_NAME_SET`), pinning the
    `_envregistry.py` module docstring's "complete by the time any server/CLI
    entry point runs" claim (feat-208, REQ-001/ACC-001).
    """

    def test_registry_name_set_equals_the_14_names_after_the_entry_point_imports(self):
        result = {entry.name for entry in _envregistry.all_vars()}

        self.assertEqual(
            result,
            _ENTRY_POINT_NAME_SET,
            "the central env-var registry is not complete after importing the real entry points "
            "(biz.dfch.specmgr.server and biz.dfch.specmgr.cli, module level above): "
            f"missing {sorted(_ENTRY_POINT_NAME_SET - result)}, "
            f"extra {sorted(result - _ENTRY_POINT_NAME_SET)} -- a register() call moved to a module "
            "the entry points never import (feat-208, REQ-001/ACC-001)",
        )


if __name__ == "__main__":
    unittest.main()
