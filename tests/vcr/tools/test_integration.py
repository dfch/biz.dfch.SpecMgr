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

"""Live, end-to-end lifecycle exercise for the ``vcr`` MCP tool surface (Phase 2, Task 2.1).

Unlike the per-tool unit tests elsewhere under ``tests/vcr/tools/``, this
module drives the actual tool functions in a single realistic sequence --
 ``list_vcr`` (empty) -> ``create_vcr`` -> ``get_vcr`` -> ``list_vcr`` (1) ->
 ``update`` -> ``set_status`` (``type="vcr"``) -> ``get_vcr`` (status changed)
 -> ``list_vcr`` (status reflected) -> ``validate_vcr`` -> ``delete``
 (generic, ``type="vcr"``) -- against a real temporary docs directory.

Isolation follows the exact same pattern as ``test_create_vcr.py``'s
``TempVcrDirTestCase``: a fresh ``tempfile.TemporaryDirectory()`` is pointed
to by ``SPECMGR_DOCS_DIR`` for the duration of each test, so nothing is ever
written to the real, developer-configured ``vcr`` base directory.
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
from biz.dfch.specmgr.vcr.models.v1 import VcrFrontmatter
from biz.dfch.specmgr.vcr.tools._paths import VcrNotFoundError, vcr_base_dir
from biz.dfch.specmgr.vcr.tools.create_vcr import create_vcr
from biz.dfch.specmgr.vcr.tools.get_vcr import get_vcr
from biz.dfch.specmgr.vcr.tools.list_vcr import list_vcr
from biz.dfch.specmgr.vcr.tools.validate_vcr import validate_vcr

_INITIAL_BODY = textwrap.dedent(
    """\
    # Sample Verification Case

    ## Verifies

    REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Sample requirement title

    Confirms that the sample requirement is met.

    ## Coverage

    partial

    ## Acceptance Criteria

    ### AC-001 (Test): The sample criterion passes
    """
)

_REVISED_BODY = _INITIAL_BODY.replace("partial", "full")


class TempVcrDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestVcrLifecycleIntegration(TempVcrDirTestCase):
    """Live, end-to-end lifecycle exercise, isolated to a temp docs directory."""

    def test_list_create_get_list_update_set_status_get_list_validate_delete_roundtrip(self) -> None:
        """list_vcr -> create_vcr -> get_vcr -> list_vcr -> update -> set_status -> get_vcr ->
        list_vcr -> validate_vcr -> delete (generic, type="vcr"), live."""
        # 0. list_vcr: an empty base directory must list nothing.
        initial_page = list_vcr()
        self.assertEqual(initial_page.total, 0)
        self.assertEqual(initial_page.results, [])

        # 1. create_vcr: a freshly created document must be a VcrFrontmatter in status "draft",
        #    with its file on disk named exactly vcr-{id}-{slug}.md.
        created = create_vcr(_INITIAL_BODY)
        self.assertIsInstance(created, VcrFrontmatter)
        self.assertEqual(created.status, "draft")
        self.assertEqual(created.type, "vcr")
        self.assertIsNotNone(created.id)
        self.assertEqual(created.created, created.updated)
        vcr_id = created.id
        assert vcr_id is not None
        expected_path = vcr_base_dir() / f"vcr-{vcr_id}-sample-verification-case.md"
        self.assertTrue(expected_path.exists())

        # 2. get_vcr: must reflect the freshly created document.
        fetched = get_vcr(vcr_id)
        self.assertEqual(fetched.frontmatter.id, vcr_id)
        self.assertEqual(fetched.body.text, "Sample Verification Case")
        self.assertEqual(fetched.body.coverage.value.text, "partial")

        # 3. list_vcr: must reflect the one created document.
        page = list_vcr()
        self.assertEqual(page.total, 1)
        self.assertEqual(len(page.results), 1)
        self.assertEqual(page.results[0].id, vcr_id)
        self.assertEqual(page.results[0].status, "draft")
        self.assertEqual(page.results[0].title, "Sample Verification Case")

        # 4. update (type="vcr"): whole-body replace must bump only `updated` and preserve
        #    id/type/status/created/version.
        updated = update(vcr_id, "vcr", _REVISED_BODY)
        self.assertEqual(updated.id, created.id)
        self.assertEqual(updated.type, created.type)
        self.assertEqual(updated.created, created.created)
        self.assertEqual(updated.status, "draft")
        self.assertEqual(updated.version, created.version)
        self.assertNotEqual(updated.updated, created.updated)
        self.assertEqual(get_vcr(vcr_id).body.coverage.value.text, "full")

        # 5. set_status (type="vcr"): only status/updated may change.
        progressed = set_status(vcr_id, "vcr", "progress")
        self.assertEqual(progressed.status, "progress")
        self.assertEqual(progressed.id, updated.id)
        self.assertEqual(progressed.created, updated.created)
        self.assertNotEqual(progressed.updated, updated.updated)
        # The body must be carried forward verbatim, untouched by the status change.
        self.assertEqual(get_vcr(vcr_id).body.coverage.value.text, "full")

        # 6. get_vcr: must reflect the latest on-disk state.
        fetched_after_status = get_vcr(vcr_id)
        self.assertEqual(fetched_after_status.frontmatter.status, "progress")
        self.assertEqual(fetched_after_status.frontmatter.id, vcr_id)

        # 7. list_vcr: must reflect the same document, with the current status/title.
        page_after_status = list_vcr()
        matches = [s for s in page_after_status.results if s.id == vcr_id]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].status, "progress")
        self.assertEqual(matches[0].title, "Sample Verification Case")

        # 8. validate_vcr: the on-disk file must validate as a complete
        #    document (full=True) and its body-only half must validate as body-only.
        on_disk_text = expected_path.read_text(encoding="utf-8")
        self.assertIs(validate_vcr(on_disk_text, full=True), True)
        body_only = frontmatter.loads(on_disk_text).content  # type: ignore[union-attr]
        self.assertIs(validate_vcr(body_only), True)

        # 9. delete (generic, type="vcr"): a real hard delete via the generic tool -- the
        #    returned str must be the seeded file path, the file must be gone, and a
        #    follow-up get_vcr must raise VcrNotFoundError.
        deleted_path = delete(vcr_id, type="vcr")
        self.assertEqual(deleted_path, str(expected_path))
        self.assertFalse(expected_path.exists())
        with self.assertRaises(VcrNotFoundError):
            get_vcr(vcr_id)

    def test_set_status_rejects_dec_only_accepted_status(self) -> None:
        """set_status (type="vcr") must reject `accepted` (DEC's/GOL's value, outside VCR's closed four-set)."""
        created = create_vcr(_INITIAL_BODY)
        expected_path = vcr_base_dir() / f"vcr-{created.id}-sample-verification-case.md"
        before = expected_path.read_text(encoding="utf-8")

        with self.assertRaises(ValidationError):
            set_status(created.id, "vcr", "accepted")

        self.assertEqual(expected_path.read_text(encoding="utf-8"), before)

    def test_validate_rejects_malformed_body_and_wrong_full_shape(self) -> None:
        """validate_vcr's body-only/full semantics must match validate_dec's --
        invalid body fails (AssertionError); full=True requires a frontmatter block (ValueError)."""
        with self.assertRaises(AssertionError):
            validate_vcr("# Title\n\nJust a paragraph, no recognized verification case record sections.\n")

        with self.assertRaises(ValueError):
            validate_vcr(_INITIAL_BODY, full=True)


if __name__ == "__main__":
    unittest.main()
