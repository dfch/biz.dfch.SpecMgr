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

"""Live, end-to-end lifecycle exercise for the ``prb`` MCP tool surface (feat-16 Phase 5, Task 5.1).

Unlike the per-tool unit tests elsewhere under ``tests/prb/tools/``, this
 module drives the actual tool functions in a single realistic sequence --
 ``create_prb`` -> ``update`` -> ``set_status`` (``type="prb"``) -> ``get_prb`` ->
 ``list_prb`` -> ``delete`` (generic, ``type="prb"``) -- against a real
 temporary docs directory, confirming ACC-004/ACC-006's "verified live, not
 just asserted" requirement with concrete evidence beyond the isolated
 per-tool tests.

Isolation follows the exact same pattern as ``test_create_prb.py``'s
``TempPrbDirTestCase``: a fresh ``tempfile.TemporaryDirectory()`` is pointed
to by ``SPECMGR_DOCS_DIR`` for the duration of each test, so nothing is ever
written to the real, developer-configured ``prb`` base directory.
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
from biz.dfch.specmgr.prb.models.v1 import PrbDocument, PrbFrontmatter, parse_prb
from biz.dfch.specmgr.prb.tools._paths import PrbNotFoundError, find_prb_path, prb_base_dir
from biz.dfch.specmgr.prb.tools.create_prb import create_prb
from biz.dfch.specmgr.prb.tools.get_prb import get_prb
from biz.dfch.specmgr.prb.tools.get_prb_example import get_prb_example
from biz.dfch.specmgr.prb.tools.get_prb_template import get_prb_template
from biz.dfch.specmgr.prb.tools.list_prb import list_prb

_INITIAL_BODY = textwrap.dedent(
    """\
    # Checkout Errors Spike on Mobile

    ## Current State

    ### Summary

    Mobile checkout is failing for a growing share of customers.

    ### What Is the Problem?

    Checkout requests from the mobile app return HTTP 500 more often than
    from desktop clients.

    ## Gap

    Mobile checkout error rate is 8%, versus an expected/desktop baseline
    of under 1%.

    ## Future State

    Mobile checkout error rate is at or below 1%, matching desktop.
    """
)

_REVISED_BODY = textwrap.dedent(
    """\
    # Checkout Errors Spike on Mobile

    ## Current State

    ### Summary

    Mobile checkout is failing for a growing share of customers, most
    acutely on Android during peak evening traffic.

    ### What Is the Problem?

    Checkout requests from the mobile app return HTTP 500 more often than
    from desktop clients.

    ### Where Is the Problem Observed?

    Primarily on Android devices during the 18:00-22:00 traffic peak.

    ## Gap

    Mobile checkout error rate is 8%, versus an expected/desktop baseline
    of under 1%.

    ## Impact

    Estimated $40k/week in abandoned-cart revenue.

    ## Future State

    Mobile checkout error rate is at or below 1%, matching desktop.
    """
)


class TempPrbDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestPrbLifecycleIntegration(TempPrbDirTestCase):
    """Live, end-to-end lifecycle exercise, isolated to a temp docs directory."""

    def test_create_update_set_status_get_list_delete_roundtrip(self) -> None:
        """create_prb -> update -> set_status -> get_prb -> list_prb -> delete (generic, type="prb"), live."""
        # 1. create_prb: a freshly created document must be a PrbFrontmatter in status "draft".
        created = create_prb(_INITIAL_BODY)
        self.assertIsInstance(created, PrbFrontmatter)
        self.assertEqual(created.status, "draft")
        self.assertEqual(created.type, "prb")
        self.assertIsNotNone(created.id)
        self.assertEqual(created.created, created.updated)
        prb_id = created.id
        assert prb_id is not None

        # 2. update: whole-body replace must preserve id/type/created, bump updated.
        updated = update(prb_id, "prb", _REVISED_BODY)
        self.assertEqual(updated.id, created.id)
        self.assertEqual(updated.type, created.type)
        self.assertEqual(updated.created, created.created)
        self.assertEqual(updated.status, "draft")
        self.assertNotEqual(updated.updated, created.updated)
        after_update = get_prb(prb_id)
        self.assertIn("Android", after_update.body.current_state.question_3.text)  # type: ignore[union-attr]
        self.assertIsNotNone(after_update.body.impact)

        # 3. set_status (type="prb"): only status/updated may change.
        activated = set_status(prb_id, "prb", "active")
        self.assertEqual(activated.status, "active")
        self.assertEqual(activated.id, updated.id)
        self.assertEqual(activated.created, updated.created)
        self.assertNotEqual(activated.updated, updated.updated)
        # The body must be carried forward verbatim, untouched by the status change.
        self.assertIn("Android", get_prb(prb_id).body.current_state.question_3.text)  # type: ignore[union-attr]

        # 4. get_prb: must reflect the latest on-disk state.
        fetched = get_prb(prb_id)
        self.assertEqual(fetched.frontmatter.status, "active")
        self.assertEqual(fetched.frontmatter.id, prb_id)

        # 5. list_prb: must reflect the same document, with the current status/title.
        page = list_prb()
        matches = [s for s in page.results if s.id == prb_id]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].status, "active")
        self.assertEqual(matches[0].title, "Checkout Errors Spike on Mobile")

        # 6. delete (generic, type="prb"): a real hard delete via the generic tool -- the
        #    returned str must be the seeded file path, the file must be gone, and a
        #    follow-up get_prb must raise PrbNotFoundError.
        prb_path = find_prb_path(prb_base_dir(), prb_id)
        deleted_path = delete(prb_id, type="prb")
        self.assertEqual(deleted_path, str(prb_path))
        self.assertFalse(prb_path.exists())
        with self.assertRaises(PrbNotFoundError):
            get_prb(prb_id)

    def test_get_prb_example_and_template_are_real_parseable_content(self) -> None:
        """Packaged example/template content must be real, non-empty, parseable markdown."""
        example_text = get_prb_example()
        template_text = get_prb_template()

        self.assertGreater(len(example_text), 0)
        self.assertGreater(len(template_text), 0)

        example = parse_prb(example_text)
        template = parse_prb(template_text)
        self.assertIsInstance(example, PrbDocument)
        self.assertIsInstance(template, PrbDocument)
        self.assertGreater(len(example.body.text), 0)
        self.assertGreater(len(template.body.text), 0)


if __name__ == "__main__":
    unittest.main()
