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

"""Live, end-to-end lifecycle exercise for the ``dec`` MCP tool surface (Phase 2, Task 2.3).

Unlike the per-tool unit tests elsewhere under ``tests/dec/tools/``, this
module drives the actual tool functions in a single realistic sequence --
 ``list_dec`` (empty) -> ``create_dec`` -> ``get_dec`` -> ``list_dec`` (1) ->
 ``update`` -> ``set_status`` (``type="dec"``) -> ``get_dec`` (status changed)
 -> ``list_dec`` (status reflected) -> ``validate_dec`` -> ``delete``
 (generic, ``type="dec"``) -- against a real temporary docs directory,
 confirming ACC-003's create->get->list->update->set_status->validate
 round-trip requirement with concrete evidence beyond the isolated
 per-tool tests.

Isolation follows the exact same pattern as ``test_create_dec.py``'s
``TempDecDirTestCase``: a fresh ``tempfile.TemporaryDirectory()`` is pointed
to by ``SPECMGR_DOCS_DIR`` for the duration of each test, so nothing is ever
written to the real, developer-configured ``dec`` base directory.

The packaged-example/template live check GOL's own integration test carries
is deliberately not ported here -- ``dec/data/`` does not exist until Phase
3 (feat-21 Task 3.1/3.2 + 3.6).
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

import frontmatter
from pydantic import ValidationError

from biz.dfch.specmgr.dec.models.v1 import DecFrontmatter
from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError, dec_base_dir
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.dec.tools.get_dec import get_dec
from biz.dfch.specmgr.dec.tools.list_dec import list_dec
from biz.dfch.specmgr.dec.tools.validate_dec import validate_dec
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools.delete import delete
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.general.tools.update import update

_INITIAL_BODY = textwrap.dedent(
    """\
    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Outcome

    We chose the document store.
    """
)

_REVISED_BODY = textwrap.dedent(
    """\
    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Drivers

    - Latency under 100 ms at p95.

    ## Decision Outcome

    We chose the document store.
    """
)


class TempDecDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestDecLifecycleIntegration(TempDecDirTestCase):
    """Live, end-to-end lifecycle exercise, isolated to a temp docs directory (ACC-003)."""

    def test_list_create_get_list_update_set_status_get_list_validate_delete_roundtrip(self) -> None:
        """list_dec -> create_dec -> get_dec -> list_dec -> update -> set_status -> get_dec ->
        list_dec -> validate_dec -> delete (generic, type="dec"), live."""
        # 0. list_dec: an empty base directory must list nothing.
        initial_page = list_dec()
        self.assertEqual(initial_page.total, 0)
        self.assertEqual(initial_page.results, [])

        # 1. create_dec: a freshly created document must be a DecFrontmatter in status "draft"
        #    (ACC-003: status is fixed, never caller-supplied), with its file on disk
        #    named exactly dec-{id}-{slug}.md.
        created = create_dec(_INITIAL_BODY)
        self.assertIsInstance(created, DecFrontmatter)
        self.assertEqual(created.status, "draft")
        self.assertEqual(created.type, "dec")
        self.assertIsNotNone(created.id)
        self.assertEqual(created.created, created.updated)
        dec_id = created.id
        assert dec_id is not None
        expected_path = dec_base_dir() / f"dec-{dec_id}-choose-a-document-store.md"
        self.assertTrue(expected_path.exists())

        # 2. get_dec: must reflect the freshly created document.
        fetched = get_dec(dec_id)
        self.assertEqual(fetched.frontmatter.id, dec_id)
        self.assertEqual(fetched.body.text, "Choose a Document Store")
        self.assertIsNone(fetched.body.drivers)

        # 3. list_dec: must reflect the one created document.
        page = list_dec()
        self.assertEqual(page.total, 1)
        self.assertEqual(len(page.results), 1)
        self.assertEqual(page.results[0].id, dec_id)
        self.assertEqual(page.results[0].status, "draft")
        self.assertEqual(page.results[0].title, "Choose a Document Store")

        # 4. update (type="dec"): whole-body replace must bump only `updated` and preserve
        #    id/type/status/created/version (ACC-003).
        updated = update(dec_id, "dec", _REVISED_BODY)
        self.assertEqual(updated.id, created.id)
        self.assertEqual(updated.type, created.type)
        self.assertEqual(updated.created, created.created)
        self.assertEqual(updated.status, "draft")
        self.assertEqual(updated.version, created.version)
        self.assertNotEqual(updated.updated, created.updated)
        self.assertIsNotNone(get_dec(dec_id).body.drivers)

        # 5. set_status (type="dec"): only status/updated may change.
        accepted = set_status(dec_id, "dec", "accepted")
        self.assertEqual(accepted.status, "accepted")
        self.assertEqual(accepted.id, updated.id)
        self.assertEqual(accepted.created, updated.created)
        self.assertNotEqual(accepted.updated, updated.updated)
        # The body must be carried forward verbatim, untouched by the status change.
        self.assertIsNotNone(get_dec(dec_id).body.drivers)

        # 6. get_dec: must reflect the latest on-disk state.
        fetched_after_status = get_dec(dec_id)
        self.assertEqual(fetched_after_status.frontmatter.status, "accepted")
        self.assertEqual(fetched_after_status.frontmatter.id, dec_id)

        # 7. list_dec: must reflect the same document, with the current status/title.
        page_after_status = list_dec()
        matches = [s for s in page_after_status.results if s.id == dec_id]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].status, "accepted")
        self.assertEqual(matches[0].title, "Choose a Document Store")

        # 8. validate_dec (ACC-003): the on-disk file must validate as a complete
        #    document (full=True) and its body-only half must validate as body-only.
        on_disk_text = expected_path.read_text(encoding="utf-8")
        self.assertIs(validate_dec(on_disk_text, full=True), True)
        body_only = frontmatter.loads(on_disk_text).content  # type: ignore[union-attr]
        self.assertIs(validate_dec(body_only), True)

        # 9. delete (generic, type="dec"): a real hard delete via the generic tool -- the
        #    returned str must be the seeded file path, the file must be gone, and a
        #    follow-up get_dec must raise DecNotFoundError.
        deleted_path = delete(dec_id, type="dec")
        self.assertEqual(deleted_path, str(expected_path))
        self.assertFalse(expected_path.exists())
        with self.assertRaises(DecNotFoundError):
            get_dec(dec_id)

    def test_set_status_rejects_gol_only_implemented_status(self) -> None:
        """ACC-003: set_status (type="dec") must reject `implemented` (GOL's seventh value, outside DEC's closed six-set)."""
        created = create_dec(_INITIAL_BODY)
        expected_path = dec_base_dir() / f"dec-{created.id}-choose-a-document-store.md"
        before = expected_path.read_text(encoding="utf-8")

        with self.assertRaises(ValidationError):
            set_status(created.id, "dec", "implemented")

        self.assertEqual(expected_path.read_text(encoding="utf-8"), before)

    def test_validate_rejects_malformed_body_and_wrong_full_shape(self) -> None:
        """ACC-003: validate_dec's body-only/full semantics must match validate_gol's --
        invalid body fails (AssertionError); full=True requires a frontmatter block (ValueError)."""
        with self.assertRaises(AssertionError):
            validate_dec("# Title\n\nJust a paragraph, no recognized decision sections.\n")

        with self.assertRaises(ValueError):
            validate_dec(_INITIAL_BODY, full=True)


if __name__ == "__main__":
    unittest.main()
