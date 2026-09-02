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

"""Live, end-to-end lifecycle exercise for the ``sop`` MCP tool surface (Phase 2, Task 2.4).

Unlike the per-tool unit tests elsewhere under ``tests/sop/tools/``, this
module drives the actual tool functions in a single realistic sequence --
 ``list_sop`` (empty) -> ``create_sop`` -> ``get_sop`` -> ``list_sop`` (1) ->
 ``update`` (generic, ``type="sop"``) -> ``set_status`` (generic,
 ``type="sop"``) -> ``get_sop`` (status changed) -> ``list_sop`` (status
 reflected) -> ``validate_sop`` -> ``delete`` (generic, ``type="sop"``) --
 against a real temporary docs directory, confirming ACC-003's
 create->get->list->update->set_status->validate round-trip requirement
 with concrete evidence beyond the isolated per-tool tests.

``sop`` is the first domain built dispatch-only from day one (ADR
36905d5b): it has **no** per-domain ``update_sop``/``set_status_sop``
tools, so the round-trip below drives the GENERIC ``update``/
``set_status`` tools in ``general.tools`` with ``type="sop"`` -- not
per-domain mutation tools (which do not exist). Both the whole-body and
line-range (``offset``/``limit``) branches of ``update`` are exercised.

Isolation follows the exact same pattern as ``test_create_sop.py``'s
``TempSopDirTestCase``: a fresh ``tempfile.TemporaryDirectory()`` is pointed
to by ``SPECMGR_DOCS_DIR`` for the duration of each test, so nothing is ever
written to the real, developer-configured ``sop`` base directory.

The packaged-example/template live check some domains' integration tests
carry is deliberately not ported here -- ``sop/data/`` does not exist until
Phase 3 (Task 3.1/3.2).
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

import frontmatter
from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools.delete import delete
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.general.tools.update import update
from biz.dfch.specmgr.sop.models.v1 import SopDocument
from biz.dfch.specmgr.sop.tools._paths import SopNotFoundError, sop_base_dir
from biz.dfch.specmgr.sop.tools.create_sop import create_sop
from biz.dfch.specmgr.sop.tools.get_sop import get_sop
from biz.dfch.specmgr.sop.tools.list_sop import list_sop
from biz.dfch.specmgr.sop.tools.validate_sop import validate_sop

_INITIAL_BODY = textwrap.dedent(
    """\
    # New Employee IT Account Provisioning

    ## Purpose

    Provision accounts for new hires.

    ## Procedure

    ### Step 1: Submit request

    HR submits the request.
    """
)

_REVISED_BODY = textwrap.dedent(
    """\
    # New Employee IT Account Provisioning

    ## Purpose

    Provision accounts for new hires.

    ## Scope

    All new hires in the engineering organization.

    ## Procedure

    ### Step 1: Submit request

    HR submits the request.
    """
)


class TempSopDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestSopLifecycleIntegration(TempSopDirTestCase):
    """Live, end-to-end lifecycle exercise, isolated to a temp docs directory (ACC-003)."""

    def test_list_create_get_list_update_set_status_get_list_validate_delete_roundtrip(self) -> None:
        """list_sop -> create_sop -> get_sop -> list_sop -> update -> set_status -> get_sop ->
        list_sop -> validate_sop -> delete (generic, type="sop"), live -- using the GENERIC
        update/set_status/delete tools (no per-domain mutation tools exist)."""
        # 0. list_sop: an empty base directory must list nothing.
        initial_page = list_sop()
        self.assertEqual(initial_page.total, 0)
        self.assertEqual(initial_page.results, [])

        # 1. create_sop: a freshly created document must be a SopDocument in status "draft"
        #    (ACC-003: status is fixed, never caller-supplied), with its file on disk
        #    named exactly sop-{id}-{slug}.md.
        created = create_sop(_INITIAL_BODY)
        self.assertIsInstance(created, SopDocument)
        self.assertEqual(created.frontmatter.status, "draft")
        self.assertEqual(created.frontmatter.type, "sop")
        self.assertIsNotNone(created.frontmatter.id)
        self.assertEqual(created.frontmatter.created, created.frontmatter.updated)
        sop_id = created.frontmatter.id
        assert sop_id is not None
        expected_path = sop_base_dir() / f"sop-{sop_id}-new-employee-it-account-provisioning.md"
        self.assertTrue(expected_path.exists())

        # 2. get_sop: must reflect the freshly created document.
        fetched = get_sop(sop_id)
        self.assertEqual(fetched.frontmatter.id, sop_id)
        self.assertEqual(fetched.body.text, "New Employee IT Account Provisioning")
        self.assertIsNone(fetched.body.scope)

        # 3. list_sop: must reflect the one created document.
        page = list_sop()
        self.assertEqual(page.total, 1)
        self.assertEqual(len(page.results), 1)
        self.assertEqual(page.results[0].id, sop_id)
        self.assertEqual(page.results[0].status, "draft")
        self.assertEqual(page.results[0].title, "New Employee IT Account Provisioning")

        # 4. update (type="sop", GENERIC): whole-body replace must bump only `updated` and preserve
        #    id/type/status/created/version (ACC-003, ACC-006).
        updated = update(sop_id, "sop", _REVISED_BODY)
        self.assertEqual(updated.frontmatter.id, created.frontmatter.id)
        self.assertEqual(updated.frontmatter.type, created.frontmatter.type)
        self.assertEqual(updated.frontmatter.created, created.frontmatter.created)
        self.assertEqual(updated.frontmatter.status, "draft")
        self.assertEqual(updated.frontmatter.version, created.frontmatter.version)
        self.assertNotEqual(updated.frontmatter.updated, created.frontmatter.updated)
        self.assertIsNotNone(updated.body.scope)

        # 4b. update (type="sop", GENERIC) range mode: a line-range splice must persist and stay valid.
        raw_lines = get_sop(sop_id, raw=True).splitlines()
        k = raw_lines.index("HR submits the request.") + 1
        replacement = "HR submits the onboarding request."
        update(id=sop_id, type="sop", content=replacement, offset=k, limit=1)
        range_checked = get_sop(sop_id)
        self.assertEqual(range_checked.body.procedure.steps[0].name, "Submit request")
        self.assertIn("onboarding", get_sop(sop_id, raw=True))

        # 5. set_status (type="sop", GENERIC): only status/updated may change (ACC-003, ACC-006).
        active = set_status(sop_id, "sop", "active")
        self.assertEqual(active.frontmatter.status, "active")
        self.assertEqual(active.frontmatter.id, updated.frontmatter.id)
        self.assertEqual(active.frontmatter.created, updated.frontmatter.created)
        self.assertNotEqual(active.frontmatter.updated, updated.frontmatter.updated)
        # The body must be carried forward verbatim, untouched by the status change.
        self.assertIsNotNone(active.body.scope)

        # 6. get_sop: must reflect the latest on-disk state.
        fetched_after_status = get_sop(sop_id)
        self.assertEqual(fetched_after_status.frontmatter.status, "active")
        self.assertEqual(fetched_after_status.frontmatter.id, sop_id)

        # 7. list_sop: must reflect the same document, with the current status/title.
        page_after_status = list_sop()
        matches = [s for s in page_after_status.results if s.id == sop_id]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].status, "active")
        self.assertEqual(matches[0].title, "New Employee IT Account Provisioning")

        # 8. validate_sop (ACC-003): the on-disk file must validate as a complete
        #    document (full=True) and its body-only half must validate as body-only.
        on_disk_text = expected_path.read_text(encoding="utf-8")
        self.assertIs(validate_sop(on_disk_text, full=True), True)
        body_only = frontmatter.loads(on_disk_text).content  # type: ignore[union-attr]
        self.assertIs(validate_sop(body_only), True)

        # 9. delete (generic, type="sop"): a real hard delete via the generic tool -- the
        #    returned str must be the seeded file path, the file must be gone, and a
        #    follow-up get_sop must raise SopNotFoundError.
        deleted_path = delete(sop_id, type="sop")
        self.assertEqual(deleted_path, str(expected_path))
        self.assertFalse(expected_path.exists())
        with self.assertRaises(SopNotFoundError):
            get_sop(sop_id)

    def test_set_status_rejects_gol_only_implemented_status(self) -> None:
        """ACC-003: set_status (type="sop") must reject `implemented` (GOL's value, outside SOP's closed five-set)."""
        created = create_sop(_INITIAL_BODY)
        expected_path = sop_base_dir() / f"sop-{created.frontmatter.id}-new-employee-it-account-provisioning.md"
        before = expected_path.read_text(encoding="utf-8")

        with self.assertRaises(ValidationError):
            set_status(created.frontmatter.id, "sop", "implemented")

        self.assertEqual(expected_path.read_text(encoding="utf-8"), before)

    def test_set_status_rejects_superseded_by_for_sop(self) -> None:
        """ACC-006: set_status (type="sop") must reject `superseded_by` (ADR-only) with ValueError, before any file access."""
        created = create_sop(_INITIAL_BODY)
        expected_path = sop_base_dir() / f"sop-{created.frontmatter.id}-new-employee-it-account-provisioning.md"
        before = expected_path.read_text(encoding="utf-8")

        with self.assertRaises(ValueError):
            set_status(created.frontmatter.id, "sop", "active", superseded_by="other-sop")

        self.assertEqual(expected_path.read_text(encoding="utf-8"), before)

    def test_validate_rejects_malformed_body_and_wrong_full_shape(self) -> None:
        """ACC-003: validate_sop's body-only/full semantics must match validate_dec's --
        invalid body fails (AssertionError); full=True requires a frontmatter block (ValueError)."""
        with self.assertRaises(AssertionError):
            validate_sop("# Title\n\nJust a paragraph, no recognized SOP sections.\n")

        with self.assertRaises(ValueError):
            validate_sop(_INITIAL_BODY, full=True)


if __name__ == "__main__":
    unittest.main()
