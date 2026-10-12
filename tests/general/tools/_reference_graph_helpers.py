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

"""Shared test machinery for the reference-graph builder and tool tests (feat-207-reference-graph,
Phase 110 Task 110.150, extended in Phase 120 Task 120.150).

The fixture ids and the seeded-registry test case shared by
``test__reference_graph.py`` (the builder integration tests) and the
Phase 120 tool tests (``test_get_reference_diagram.py`` /
``test_get_reference_diagram_all.py``): the isolated
``SPECMGR_DOCS_DIR``/``SPECMGR_ADR_DIR``/``SPECMGR_FEAT_DIR`` tmp dirs
follow the ``tests/commands/test_diagram.py`` precedent (the env vars are
read per call, so patching is clean and isolated), the per-domain
process-local doc caches are reset in ``setUp``/``tearDown`` (the
``reset_<d>_cache`` test hooks), and -- since Phase 120 -- the
``SPECMGR_DIAGRAM_MAX_TITLE`` env var is guarded (popped in ``setUp``,
restored in ``tearDown``) so the tool tests' byte-stable golden comparisons
run at the frozen default label limit 40 regardless of the ambient
environment.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR
from biz.dfch.specmgr.general.models.reference_graph import render_reference_graph
from biz.dfch.specmgr.general.tools._diagram_config import ENV_VAR_DIAGRAM_MAX_TITLE
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "reference-graphs"
_GOLDENS = _FIXTURES / "goldens"

# --- the fixture documents' frozen ids -----------------------------------------

_C001 = "c001c001-c001-4c01-8c01-c001c001c001"  # req "Cycle Requirement One"
_C002 = "c002c002-c002-4c02-8c02-c002c002c002"  # req "Cycle Requirement Two"
_D900 = "d900d900-d900-4d90-8d90-d900d900d900"  # a DEC id that does not exist on disk (dangling)
_H001 = "c003c003-c003-4c03-8c03-c003c003c003"  # req "Chain Top Requirement With A Very Long Title" (44 chars)
_G001 = "c004c004-c004-4c04-8c04-c004c004c004"  # gol "Chain Middle Goal"
_K001 = "c005c005-c005-4c05-8c05-c005c005c005"  # rsk "Chain Leaf Risk"
_R001 = "c006c006-c006-4c06-8c06-c006c006c006"  # req "Reverse Target"
_D001 = "c007c007-c007-4c07-8c07-c007c007c007"  # dec "Reverse Referrer"
_G900 = "d901d901-d901-4d91-8d91-d901d901d901"  # a GOL id that does not exist on disk (dangling)
_N001 = "c008c008-c008-4c08-8c08-c008c008c008"  # req "No Feat Source"
_W001 = "c009c009-c009-4c09-8c09-c009c009c009"  # req "Wide Requirement One"
_U001 = "c00ac00a-c00a-4c0a-8c0a-c00ac00ac00a"  # uc "Wide Use Case"
_WG001 = "c00bc00b-c00b-4c0b-8c0b-c00bc00bc00b"  # gol "Wide Goal"
_A001 = "c00cc00c-c00c-4c0c-8c0c-c00cc00cc00c"  # adr "Wide ADR"
_D002 = "c00dc00d-c00d-4c0d-8c0d-c00dc00dc00d"  # dec "Broken Decision" (deliberately unparseable)
_B001 = "c00ec00e-c00e-4c0e-8c0e-c00ec00ec00e"  # dec "Bare Referrer" (bare-`feat-42` reference + the bare-`feat-43` negative control)

_MISSING_UUID = "00000000-0000-0000-0000-000000000000"  # well-formed, never seeded


def _reset_caches() -> None:
    """Clear every per-domain process-local doc cache (the ``reset_<d>_cache`` test hooks)."""
    from biz.dfch.specmgr.dec.tools._cache import reset_dec_cache
    from biz.dfch.specmgr.feat.tools._cache import reset_feat_cache, reset_feat_dirty_cache
    from biz.dfch.specmgr.gol.tools._cache import reset_gol_cache
    from biz.dfch.specmgr.prb.tools._cache import reset_prb_cache
    from biz.dfch.specmgr.qa.tools._cache import reset_qa_cache
    from biz.dfch.specmgr.req.tools._cache import reset_req_cache
    from biz.dfch.specmgr.rsk.tools._cache import reset_rsk_cache
    from biz.dfch.specmgr.sop.tools._cache import reset_sop_cache
    from biz.dfch.specmgr.sysrs.tools._cache import reset_sysrs_cache
    from biz.dfch.specmgr.tsk.tools._cache import reset_tsk_cache
    from biz.dfch.specmgr.uc.tools._cache import reset_uc_cache
    from biz.dfch.specmgr.vcr.tools._cache import reset_vcr_cache

    for reset in (
        reset_req_cache,
        reset_uc_cache,
        reset_tsk_cache,
        reset_qa_cache,
        reset_prb_cache,
        reset_gol_cache,
        reset_rsk_cache,
        reset_dec_cache,
        reset_sop_cache,
        reset_feat_cache,
        reset_feat_dirty_cache,
        reset_vcr_cache,
        reset_sysrs_cache,
    ):
        reset()


class _SeededRegistryTestCase(unittest.TestCase):
    """Common fixture: isolated ``SPECMGR_DOCS_DIR``/``SPECMGR_ADR_DIR``/``SPECMGR_FEAT_DIR`` tmp dirs
    seeded from the committed fixture documents (the ``tests/commands/test_diagram.py`` precedent),
    with every per-domain doc cache reset around each test and the
    ``SPECMGR_DIAGRAM_MAX_TITLE`` env var guarded (Phase 120: the byte-stable tool tests run at
    the frozen default label limit 40)."""

    #: ``(fixture relative path, destination relative to the tmp root)`` pairs: the
    #: destination is ``docs/<domain>/<name>`` for a flat document, ``adr/<name>`` for an
    #: ADR, or ``feat/<id>`` for a feature folder (the whole folder is copied).
    SEEDS: tuple[tuple[str, str], ...] = ()

    def setUp(self) -> None:
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.docs_root = self.root / "docs"
        self.adr_dir = self.root / "adr"
        self.feat_dir = self.root / "feat"
        self._previous_max_title = os.environ.get(ENV_VAR_DIAGRAM_MAX_TITLE)
        os.environ.pop(ENV_VAR_DIAGRAM_MAX_TITLE, None)
        self.enterContext(
            mock.patch.dict(
                "os.environ",
                {
                    DOCS_DIR_ENV_VAR: str(self.docs_root),
                    ADR_DIR_ENV_VAR: str(self.adr_dir),
                    FEAT_DIR_ENV_VAR: str(self.feat_dir),
                },
            )
        )
        _reset_caches()
        for fixture, dest in self.SEEDS:
            target = self.root / dest
            target.parent.mkdir(parents=True, exist_ok=True)
            if dest.startswith("feat/"):
                shutil.copytree(_FIXTURES / fixture, target)
            else:
                shutil.copy(_FIXTURES / fixture, target)

    def tearDown(self) -> None:
        _reset_caches()
        if self._previous_max_title is None:
            os.environ.pop(ENV_VAR_DIAGRAM_MAX_TITLE, None)
        else:
            os.environ[ENV_VAR_DIAGRAM_MAX_TITLE] = self._previous_max_title

    def _golden(self, name: str) -> str:
        return (_GOLDENS / name).read_text(encoding="utf-8")

    def _render_golden(self, name: str, graph) -> None:
        self.assertEqual(render_reference_graph(graph), self._golden(name))
