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

"""Live, end-to-end lifecycle exercise for the ``sysrs`` MCP tool surface (Phase 3, Task 3.4).

Unlike the per-tool unit tests elsewhere under ``tests/sysrs/tools/``, this
module drives the actual tool functions in a single realistic sequence --
``list_sysrs`` (empty) -> ``create_sysrs`` -> ``get_sysrs`` -> ``list_sysrs``
(1) -> ``update`` (whole-body) -> ``update`` (line-range) -> ``set_status``
(``type="sysrs"``) -> ``set_classification`` (``type="sysrs"``) ->
``get_sysrs`` (status/classification changed) -> ``list_sysrs`` (status
reflected) -> ``validate_sysrs`` -> ``delete`` (generic, ``type="sysrs"``)
-- against a real temporary docs directory.

Isolation follows the exact same pattern as ``test_create_sysrs.py``'s
``TempSysrsDirTestCase``: a fresh ``tempfile.TemporaryDirectory()`` is
pointed to by ``SPECMGR_DOCS_DIR`` for the duration of each test, so nothing
is ever written to the real, developer-configured ``sysrs`` base directory.
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
from biz.dfch.specmgr.general.tools.set_classification import set_classification
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.general.tools.update import update
from biz.dfch.specmgr.sysrs.models.v1 import SysrsFrontmatter
from biz.dfch.specmgr.sysrs.tools._paths import SysrsNotFoundError, sysrs_base_dir
from biz.dfch.specmgr.sysrs.tools.create_sysrs import create_sysrs
from biz.dfch.specmgr.sysrs.tools.get_sysrs import get_sysrs
from biz.dfch.specmgr.sysrs.tools.list_sysrs import list_sysrs
from biz.dfch.specmgr.sysrs.tools.validate_sysrs import validate_sysrs

_GOL_ID = "0e15c5de-4ac9-4279-aa75-53249a3e43e4"
_REQ_ID = "a3f8c2d1-7b4e-4d9a-b6c0-91e5f2a8d734"

_INITIAL_BODY = textwrap.dedent(
    f"""\
    # System Requirements Specification: Sample Document

    ## System Purpose

    Provision partner accounts.

    ## System Scope

    Onboarding only.

    ## Business Context and Goals

    ### Goals

    - GOL {_GOL_ID}: A goal

    ## System Overview

    ### System Context

    Context.

    ### System Functions

    Functions.

    ## Requirements

    ### Functional Suitability

    - REQ {_REQ_ID}: A requirement
    """
)

_REVISED_BODY = _INITIAL_BODY.replace("Onboarding only.", "Onboarding and renewals.")


class TempSysrsDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestSysrsLifecycleIntegration(TempSysrsDirTestCase):
    """Live, end-to-end lifecycle exercise, isolated to a temp docs directory."""

    def test_full_lifecycle_roundtrip(self) -> None:
        """list_sysrs -> create_sysrs -> get_sysrs -> list_sysrs -> update (whole-body) ->
        update (line-range) -> set_status -> set_classification -> get_sysrs -> list_sysrs ->
        validate_sysrs -> delete (generic, type="sysrs"), live (ACC-006/ACC-009)."""
        # 0. list_sysrs: an empty base directory must list nothing.
        initial_page = list_sysrs()
        self.assertEqual(initial_page.total, 0)
        self.assertEqual(initial_page.results, [])

        # 1. create_sysrs: a freshly created document must be a SysrsFrontmatter in status "draft",
        #    with its file on disk named exactly sysrs-{id}-{slug}.md.
        created = create_sysrs(_INITIAL_BODY)
        self.assertIsInstance(created, SysrsFrontmatter)
        self.assertEqual(created.status, "draft")
        self.assertEqual(created.type, "sysrs")
        self.assertIsNotNone(created.id)
        self.assertEqual(created.created, created.updated)
        sysrs_id = created.id
        assert sysrs_id is not None
        expected_path = sysrs_base_dir() / f"sysrs-{sysrs_id}-system-requirements-specification-sample-document.md"
        self.assertTrue(expected_path.exists())

        # 2. get_sysrs: must reflect the freshly created document.
        fetched = get_sysrs(sysrs_id)
        self.assertEqual(fetched.frontmatter.id, sysrs_id)
        self.assertEqual(fetched.body.text, "System Requirements Specification: Sample Document")
        self.assertIn("Onboarding only", fetched.body.system_scope.text)

        # 3. list_sysrs: must reflect the one created document.
        page = list_sysrs()
        self.assertEqual(page.total, 1)
        self.assertEqual(len(page.results), 1)
        self.assertEqual(page.results[0].id, sysrs_id)
        self.assertEqual(page.results[0].status, "draft")
        self.assertEqual(page.results[0].title, "System Requirements Specification: Sample Document")

        # 4. update (type="sysrs", whole-body): must bump only `updated` and preserve
        #    id/type/status/created/version.
        updated = update(sysrs_id, "sysrs", _REVISED_BODY)
        self.assertEqual(updated.id, created.id)
        self.assertEqual(updated.type, created.type)
        self.assertEqual(updated.created, created.created)
        self.assertEqual(updated.status, "draft")
        self.assertEqual(updated.version, created.version)
        self.assertNotEqual(updated.updated, created.updated)
        self.assertIn("Onboarding and renewals", get_sysrs(sysrs_id).body.system_scope.text)

        # 5. update (type="sysrs", line-range): replace just the "## System Purpose" body line.
        lines = get_sysrs(sysrs_id, raw=True).splitlines()
        k = lines.index("Provision partner accounts.") + 1
        ranged = update(sysrs_id, "sysrs", "Provision and manage partner accounts.", offset=k, limit=1)
        self.assertIn("Provision and manage partner accounts.", get_sysrs(sysrs_id).body.system_purpose.text)
        new_lines = get_sysrs(sysrs_id, raw=True).splitlines()
        self.assertEqual(new_lines[: k - 1] + new_lines[k:], lines[: k - 1] + lines[k:])

        # 6. set_status (type="sysrs"): only status/updated may change.
        progressed = set_status(sysrs_id, "sysrs", "review")
        self.assertEqual(progressed.status, "review")
        self.assertEqual(progressed.id, ranged.id)
        self.assertEqual(progressed.created, ranged.created)
        self.assertNotEqual(progressed.updated, ranged.updated)
        # The body must be carried forward verbatim, untouched by the status change.
        self.assertIn("Onboarding and renewals", get_sysrs(sysrs_id).body.system_scope.text)

        # 7. set_classification (type="sysrs", ACC-009 feat-56 addendum): only classification/updated
        #    may change.
        classified = set_classification(sysrs_id, "sysrs", "internal")
        self.assertEqual(classified.classification, "internal")
        self.assertEqual(classified.status, "review")
        self.assertEqual(classified.id, progressed.id)
        self.assertNotEqual(classified.updated, progressed.updated)

        # A blank classification clears the field back to None/absent.
        cleared = set_classification(sysrs_id, "sysrs", "")
        self.assertIsNone(cleared.classification)

        # 8. get_sysrs: must reflect the latest on-disk state.
        fetched_after_status = get_sysrs(sysrs_id)
        self.assertEqual(fetched_after_status.frontmatter.status, "review")
        self.assertEqual(fetched_after_status.frontmatter.id, sysrs_id)

        # 9. list_sysrs: must reflect the same document, with the current status/title.
        page_after_status = list_sysrs()
        matches = [s for s in page_after_status.results if s.id == sysrs_id]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].status, "review")
        self.assertEqual(matches[0].title, "System Requirements Specification: Sample Document")

        # 10. validate_sysrs: the on-disk file must validate as a complete
        #     document (full=True) and its body-only half must validate as body-only.
        on_disk_text = expected_path.read_text(encoding="utf-8")
        self.assertIs(validate_sysrs(on_disk_text, full=True), True)
        body_only = frontmatter.loads(on_disk_text).content  # type: ignore[union-attr]
        self.assertIs(validate_sysrs(body_only), True)

        # 11. delete (generic, type="sysrs"): a real hard delete via the generic tool -- the
        #     returned str must be the seeded file path, the file must be gone, and a
        #     follow-up get_sysrs must raise SysrsNotFoundError.
        deleted_path = delete(sysrs_id, type="sysrs")
        self.assertEqual(deleted_path, str(expected_path))
        self.assertFalse(expected_path.exists())
        with self.assertRaises(SysrsNotFoundError):
            get_sysrs(sysrs_id)

    def test_set_status_rejects_superseded_by(self) -> None:
        """set_status (type="sysrs") must reject `superseded_by` -- ADR-only, standard non-adr ValueError."""
        created = create_sysrs(_INITIAL_BODY)

        with self.assertRaises(ValueError):
            set_status(created.id, "sysrs", "review", superseded_by="some-other-id")

    def test_set_status_rejects_status_outside_closed_set(self) -> None:
        """set_status (type="sysrs") must reject a status outside the closed 5-value set."""
        created = create_sysrs(_INITIAL_BODY)
        expected_path = sysrs_base_dir() / f"sysrs-{created.id}-system-requirements-specification-sample-document.md"
        before = expected_path.read_text(encoding="utf-8")

        with self.assertRaises(ValidationError):
            set_status(created.id, "sysrs", "accepted")

        self.assertEqual(expected_path.read_text(encoding="utf-8"), before)

    def test_validate_rejects_malformed_body_and_wrong_full_shape(self) -> None:
        """validate_sysrs's body-only/full semantics -- invalid body fails (AssertionError);
        full=True requires a frontmatter block (ValueError)."""
        with self.assertRaises(AssertionError):
            validate_sysrs("# Title\n\nJust a paragraph, no recognized SYSRS sections.\n")

        with self.assertRaises(ValueError):
            validate_sysrs(_INITIAL_BODY, full=True)


if __name__ == "__main__":
    unittest.main()
