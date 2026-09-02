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

"""Live, end-to-end lifecycle exercise for the ``gol`` MCP tool surface (Phase 3, Task 3.17).

Unlike the per-tool unit tests elsewhere under ``tests/gol/tools/``, this
module drives the actual tool functions in a single realistic sequence --
 ``list_gol`` (empty) -> ``create_gol`` -> ``get_gol`` -> ``list_gol`` (1) ->
 ``update`` -> ``set_status`` (``type="gol"``) -> ``get_gol`` (status changed) ->
 ``list_gol`` (status reflected) -> ``delete`` (generic, ``type="gol"``) --
 against a real temporary docs directory, confirming ACC-004/ACC-006's
 "verified live, not just asserted" requirement with concrete evidence
 beyond the isolated per-tool tests.

Isolation follows the exact same pattern as ``test_create_gol.py``'s
``TempGolDirTestCase``: a fresh ``tempfile.TemporaryDirectory()`` is pointed
to by ``SPECMGR_DOCS_DIR`` for the duration of each test, so nothing is ever
written to the real, developer-configured ``gol`` base directory.
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools.delete import delete
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.general.tools.update import update
from biz.dfch.specmgr.gol.models.v1 import GolDocument, GolFrontmatter, parse_gol
from biz.dfch.specmgr.gol.tools._paths import GolNotFoundError, find_gol_path, gol_base_dir
from biz.dfch.specmgr.gol.tools.create_gol import create_gol
from biz.dfch.specmgr.gol.tools.get_gol import get_gol
from biz.dfch.specmgr.gol.tools.get_gol_example import get_gol_example
from biz.dfch.specmgr.gol.tools.get_gol_template import get_gol_template
from biz.dfch.specmgr.gol.tools.list_gol import list_gol

_INITIAL_BODY = textwrap.dedent(
    """\
    # Competitive Engines in Consumer Vehicles

    THE company shall provide engines that are competitive in power output and fuel consumption.

    ## Source

    The vehicle program's 2027 market analysis
    """
)

_REVISED_BODY = textwrap.dedent(
    """\
    # Competitive Engines in Consumer Vehicles

    THE company shall provide engines that are competitive in power output, fuel consumption, and price.

    ## Description

    Buyers compare these three dimensions across competing manufacturers before purchase.

    ## Source

    The vehicle program's 2027 market analysis
    """
)


class TempGolDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestGolLifecycleIntegration(TempGolDirTestCase):
    """Live, end-to-end lifecycle exercise, isolated to a temp docs directory."""

    def test_list_create_get_list_update_set_status_get_list_delete_roundtrip(self) -> None:
        """list_gol -> create_gol -> get_gol -> list_gol -> update -> set_status -> get_gol ->
        list_gol -> delete (generic, type="gol"), live."""
        # 0. list_gol: an empty base directory must list nothing.
        initial_page = list_gol()
        self.assertEqual(initial_page.total, 0)
        self.assertEqual(initial_page.results, [])

        # 1. create_gol: a freshly created document must be a GolFrontmatter in status "draft".
        created = create_gol(_INITIAL_BODY)
        self.assertIsInstance(created, GolFrontmatter)
        self.assertEqual(created.status, "draft")
        self.assertEqual(created.type, "gol")
        self.assertIsNotNone(created.id)
        self.assertEqual(created.created, created.updated)
        gol_id = created.id
        assert gol_id is not None

        # 2. get_gol: must reflect the freshly created document.
        fetched = get_gol(gol_id)
        self.assertEqual(fetched.frontmatter.id, gol_id)
        self.assertEqual(fetched.body.text, "Competitive Engines in Consumer Vehicles")
        self.assertIsNone(fetched.body.description)

        # 3. list_gol: must reflect the one created document.
        page = list_gol()
        self.assertEqual(page.total, 1)
        self.assertEqual(len(page.results), 1)
        self.assertEqual(page.results[0].id, gol_id)
        self.assertEqual(page.results[0].status, "draft")
        self.assertEqual(page.results[0].title, "Competitive Engines in Consumer Vehicles")

        # 4. update: whole-body replace must preserve id/type/created, bump updated.
        updated = update(gol_id, "gol", _REVISED_BODY)
        self.assertEqual(updated.id, created.id)
        self.assertEqual(updated.type, created.type)
        self.assertEqual(updated.created, created.created)
        self.assertEqual(updated.status, "draft")
        self.assertNotEqual(updated.updated, created.updated)
        self.assertIsNotNone(get_gol(gol_id).body.description)

        # 5. set_status (type="gol"): only status/updated may change.
        accepted = set_status(gol_id, "gol", "accepted")
        self.assertEqual(accepted.status, "accepted")
        self.assertEqual(accepted.id, updated.id)
        self.assertEqual(accepted.created, updated.created)
        self.assertNotEqual(accepted.updated, updated.updated)
        # The body must be carried forward verbatim, untouched by the status change.
        self.assertIsNotNone(get_gol(gol_id).body.description)

        # 6. get_gol: must reflect the latest on-disk state.
        fetched_after_status = get_gol(gol_id)
        self.assertEqual(fetched_after_status.frontmatter.status, "accepted")
        self.assertEqual(fetched_after_status.frontmatter.id, gol_id)

        # 7. list_gol: must reflect the same document, with the current status/title.
        page_after_status = list_gol()
        matches = [s for s in page_after_status.results if s.id == gol_id]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].status, "accepted")
        self.assertEqual(matches[0].title, "Competitive Engines in Consumer Vehicles")

        # 8. delete (generic, type="gol"): a real hard delete via the generic tool -- the
        #    returned str must be the seeded file path, the file must be gone, and a
        #    follow-up get_gol must raise GolNotFoundError.
        gol_path = find_gol_path(gol_base_dir(), gol_id)
        deleted_path = delete(gol_id, type="gol")
        self.assertEqual(deleted_path, str(gol_path))
        self.assertFalse(gol_path.exists())
        with self.assertRaises(GolNotFoundError):
            get_gol(gol_id)

    def test_gol_example_and_template_are_real_parseable_content(self) -> None:
        """Packaged example/template content must be real, non-empty, parseable markdown."""
        example_text = get_gol_example()
        template_text = get_gol_template()

        self.assertGreater(len(example_text), 0)
        self.assertGreater(len(template_text), 0)

        example = parse_gol(example_text)
        template = parse_gol(template_text)
        self.assertIsInstance(example, GolDocument)
        self.assertIsInstance(template, GolDocument)
        self.assertGreater(len(example.body.text), 0)
        self.assertGreater(len(template.body.text), 0)


if __name__ == "__main__":
    unittest.main()
