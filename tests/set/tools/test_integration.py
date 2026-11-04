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

"""Live, end-to-end lifecycle exercise for the ``set`` MCP tool surface (feat-229-set Phase 110).

Unlike the per-tool unit tests elsewhere under ``tests/set/tools/``, this
module drives the actual tool functions in a single realistic sequence --
  ``list_set`` (empty) -> ``create_set`` -> ``get_set`` -> ``list_set`` (1)
  -> ``get_set`` (raw windowed/numbered) -> ``parse_set`` -> break the file
  -> ``get_set`` (ParseFailureResult) -> ``list_set`` (failed row,
  byte-identical error) -> repair (host-native write) -> ``get_set``
  (healthy again, cache re-validated) -> ``list_set`` (healthy) -- against a
real temporary docs directory.

The generic ``update``/``set_status``/``validate``/``delete`` tools are
**not** part of this sequence: ``set`` is a registered dispatch type for
all of them, and each carries its own ``set`` cases in the generic tools'
own test suites under ``tests/general/tools/`` (``test_update.py``,
``test_set_status.py``, ``test_validate.py``, and ``test_delete.py``).

Isolation follows the exact same pattern as ``test_create_set.py``'s
``TempSetDirTestCase``: a fresh ``tempfile.TemporaryDirectory()`` is pointed
to by ``SPECMGR_DOCS_DIR`` for the duration of each test, so nothing is ever
written to the real, developer-configured ``set`` base directory.
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import ParseFailureResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.set.models.v1 import SetDocument, SetFrontmatter
from biz.dfch.specmgr.set.tools._paths import SetNotFoundError, set_base_dir
from biz.dfch.specmgr.set.tools.create_set import create_set
from biz.dfch.specmgr.set.tools.get_set import get_set
from biz.dfch.specmgr.set.tools.list_set import list_set
from biz.dfch.specmgr.set.tools.parse_set import parse_set

_INITIAL_BODY = textwrap.dedent(
    """\
    # Sample Review Set

    ## Description

    Some prose about what the set bundles and why the items belong together.

    ## Items

    - REQ 00000000-0000-4000-8000-000000000001: Sample Requirement
    """
)


class TempSetDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestSetLifecycleIntegration(TempSetDirTestCase):
    """Live, end-to-end lifecycle exercise, isolated to a temp docs directory."""

    def test_list_create_get_raw_list_parse_break_repair_roundtrip(self) -> None:
        """list_set -> create_set -> get_set -> list_set -> get_set(raw) -> parse_set -> break ->
        get_set (ParseFailureResult) -> list_set (failed row) -> repair -> get_set -> list_set, live."""
        # 0. list_set: an empty base directory must list nothing.
        initial_page = list_set()
        self.assertEqual(initial_page.total, 0)
        self.assertEqual(initial_page.results, [])

        # 1. create_set: a freshly created document must be a SetFrontmatter in status "draft",
        #    with its file on disk named exactly set-{id}-{slug}.md.
        created = create_set(_INITIAL_BODY)
        self.assertIsInstance(created, SetFrontmatter)
        self.assertEqual(created.status, "draft")
        self.assertEqual(created.type, "set")
        self.assertIsNotNone(created.id)
        self.assertEqual(created.created, created.updated)
        set_id = created.id
        assert set_id is not None
        expected_path = set_base_dir() / f"set-{set_id}-sample-review-set.md"
        self.assertTrue(expected_path.exists())

        # 2. get_set: must reflect the freshly created document.
        fetched = get_set(set_id)
        self.assertIsInstance(fetched, SetDocument)
        self.assertEqual(fetched.frontmatter.id, set_id)
        self.assertEqual(fetched.body.text, "Sample Review Set")
        self.assertEqual(
            fetched.body.description.text,
            "## Description\n\nSome prose about what the set bundles and why the items belong together.\n",
        )
        # 3. list_set: must reflect the one created document.
        page = list_set()
        self.assertEqual(page.total, 1)
        self.assertEqual(len(page.results), 1)
        self.assertEqual(page.results[0].id, set_id)
        self.assertEqual(page.results[0].status, "draft")
        self.assertEqual(page.results[0].title, "Sample Review Set")
        self.assertEqual(page.error_count, 0)

        # 4. get_set(raw=True): the raw body must be byte-identical to the shared body_text
        #    helper, and the windowed/numbered reads must index into the same text.
        raw = get_set(set_id, raw=True)
        self.assertIsInstance(raw, str)
        self.assertEqual(raw, body_text(expected_path))
        lines = raw.splitlines()
        self.assertEqual(get_set(set_id, raw=True, offset=2, limit=2), "\n".join(lines[1:3]) + "\n")
        self.assertEqual(
            get_set(set_id, raw=True, numbered=True, offset=3, limit=1),
            f"3: {lines[2]}\n",
        )

        # 5. parse_set: the on-disk file must parse via the parse_set tool into a SetDocument.
        parsed = parse_set(str(expected_path))
        self.assertIsInstance(parsed, SetDocument)
        self.assertEqual(parsed.frontmatter.id, set_id)
        self.assertEqual(parsed.body.text, "Sample Review Set")

        # 6. break the file: get_set must return the non-raising ParseFailureResult channel,
        #    and list_set's failed row must carry the byte-identical error.
        before_break = expected_path.read_text(encoding="utf-8")
        expected_path.write_text("not a valid document, no headings at all\n", encoding="utf-8")

        broken_get = get_set(set_id)
        self.assertIsInstance(broken_get, ParseFailureResult)
        self.assertEqual(broken_get.id, set_id)
        self.assertEqual(broken_get.path, str(expected_path.resolve()))

        broken_page = list_set()
        failed = [summary for summary in broken_page.results if summary.title == "<failed to parse>"]
        self.assertEqual(len(failed), 1)
        self.assertEqual(broken_page.error_count, 1)
        self.assertEqual(broken_get.error, failed[0].error)

        # 7. repair (host-native write, the `repair` flow's mechanism): a healthy rewrite must
        #    clear both the get_set parse-failure channel and the list_set failed row -- the
        #    content-hash-validated cache serves the fresh content, never the stale failure.
        expected_path.write_text(before_break, encoding="utf-8")

        repaired = get_set(set_id)
        self.assertIsInstance(repaired, SetDocument)
        self.assertEqual(repaired.body.text, "Sample Review Set")

        repaired_page = list_set()
        self.assertEqual(repaired_page.error_count, 0)
        self.assertEqual(repaired_page.total, 1)
        self.assertEqual(repaired_page.results[0].status, "draft")

    def test_broken_document_unknown_id_still_raises_not_found(self) -> None:
        """With one broken file on disk, an id that matches no file at all must still raise
        SetNotFoundError (the parse-failure channel only recovers the name-matching case)."""
        create_set(_INITIAL_BODY)
        broken_path = set_base_dir() / "broken.md"
        broken_path.write_text("not a valid document, no headings at all\n", encoding="utf-8")

        with self.assertRaises(SetNotFoundError):
            get_set("00000000-0000-0000-0000-000000000000")


if __name__ == "__main__":
    unittest.main()
