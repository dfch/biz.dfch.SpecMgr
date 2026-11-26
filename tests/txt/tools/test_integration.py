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

"""Live, end-to-end lifecycle exercise for the ``txt`` MCP tool surface (feat-229-txt Phase 110).

Unlike the per-tool unit tests elsewhere under ``tests/txt/tools/``, this
module drives the actual tool functions in a single realistic sequence --
  ``list_txt`` (empty) -> ``create_txt`` -> ``get_txt`` -> ``list_txt`` (1)
  -> ``get_txt`` (raw windowed/numbered) -> ``parse_txt`` -> break the file
  -> ``get_txt`` (ParseFailureResult) -> ``list_txt`` (failed row,
  byte-identical error) -> repair (host-native write) -> ``get_txt``
  (healthy again, cache re-validated) -> ``list_txt`` (healthy) -- against a
real temporary docs directory.

The generic ``update``/``set_status``/``validate``/``delete`` tools are
**not** part of this sequence: ``txt`` is a registered dispatch type for
all of them, and each carries its own ``txt`` cases in the generic tools'
own test suites under ``tests/general/tools/`` (``test_update.py``,
``test_set_status.py``, ``test_validate.py``, and ``test_delete.py``).

Isolation follows the exact same pattern as ``test_create_txt.py``'s
``TempTxtDirTestCase``: a fresh ``tempfile.TemporaryDirectory()`` is pointed
to by ``SPECMGR_DOCS_DIR`` for the duration of each test, so nothing is ever
written to the real, developer-configured ``txt`` base directory.
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
from biz.dfch.specmgr.txt.models.v1 import TxtDocument, TxtFrontmatter
from biz.dfch.specmgr.txt.tools._paths import TxtNotFoundError, txt_base_dir
from biz.dfch.specmgr.txt.tools.create_txt import create_txt
from biz.dfch.specmgr.txt.tools.get_txt import get_txt
from biz.dfch.specmgr.txt.tools.list_txt import list_txt
from biz.dfch.specmgr.txt.tools.parse_txt import parse_txt

_INITIAL_BODY = textwrap.dedent(
    """\
    # Sample Review Notes

    Some free-form prose about what was reviewed.

    ## Updates

    ### 2026-08-31 00:00:00.000Z - Created

    Initial draft of the review notes.
    """
)


class TempTxtDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestTxtLifecycleIntegration(TempTxtDirTestCase):
    """Live, end-to-end lifecycle exercise, isolated to a temp docs directory."""

    def test_list_create_get_raw_list_parse_break_repair_roundtrip(self) -> None:
        """list_txt -> create_txt -> get_txt -> list_txt -> get_txt(raw) -> parse_txt -> break ->
        get_txt (ParseFailureResult) -> list_txt (failed row) -> repair -> get_txt -> list_txt, live."""
        # 0. list_txt: an empty base directory must list nothing.
        initial_page = list_txt()
        self.assertEqual(initial_page.total, 0)
        self.assertEqual(initial_page.results, [])

        # 1. create_txt: a freshly created document must be a TxtFrontmatter in status "draft",
        #    with its file on disk named exactly txt-{id}-{slug}.md.
        created = create_txt(_INITIAL_BODY)
        self.assertIsInstance(created, TxtFrontmatter)
        self.assertEqual(created.status, "draft")
        self.assertEqual(created.type, "txt")
        self.assertIsNotNone(created.id)
        self.assertEqual(created.created, created.updated)
        txt_id = created.id
        assert txt_id is not None
        expected_path = txt_base_dir() / f"txt-{txt_id}-sample-review-notes.md"
        self.assertTrue(expected_path.exists())

        # 2. get_txt: must reflect the freshly created document.
        fetched = get_txt(txt_id)
        self.assertIsInstance(fetched, TxtDocument)
        self.assertEqual(fetched.frontmatter.id, txt_id)
        self.assertEqual(fetched.body.text, "Sample Review Notes")
        self.assertEqual(fetched.body.body.text, "Some free-form prose about what was reviewed.\n")
        # 3. list_txt: must reflect the one created document.
        page = list_txt()
        self.assertEqual(page.total, 1)
        self.assertEqual(len(page.results), 1)
        self.assertEqual(page.results[0].id, txt_id)
        self.assertEqual(page.results[0].status, "draft")
        self.assertEqual(page.results[0].title, "Sample Review Notes")
        self.assertEqual(page.error_count, 0)

        # 4. get_txt(raw=True): the raw body must be byte-identical to the shared body_text
        #    helper, and the windowed/numbered reads must index into the same text.
        raw = get_txt(txt_id, raw=True)
        self.assertIsInstance(raw, str)
        self.assertEqual(raw, body_text(expected_path))
        lines = raw.splitlines()
        self.assertEqual(get_txt(txt_id, raw=True, offset=2, limit=2), "\n".join(lines[1:3]) + "\n")
        self.assertEqual(
            get_txt(txt_id, raw=True, numbered=True, offset=3, limit=1),
            f"3: {lines[2]}\n",
        )

        # 5. parse_txt: the on-disk file must parse via the parse_txt tool into a TxtDocument.
        parsed = parse_txt(str(expected_path))
        self.assertIsInstance(parsed, TxtDocument)
        self.assertEqual(parsed.frontmatter.id, txt_id)
        self.assertEqual(parsed.body.text, "Sample Review Notes")

        # 6. break the file: get_txt must return the non-raising ParseFailureResult channel,
        #    and list_txt's failed row must carry the byte-identical error.
        before_break = expected_path.read_text(encoding="utf-8")
        expected_path.write_text("not a valid document, no headings at all\n", encoding="utf-8")

        broken_get = get_txt(txt_id)
        self.assertIsInstance(broken_get, ParseFailureResult)
        self.assertEqual(broken_get.id, txt_id)
        self.assertEqual(broken_get.path, str(expected_path.resolve()))

        broken_page = list_txt()
        failed = [summary for summary in broken_page.results if summary.title == "<failed to parse>"]
        self.assertEqual(len(failed), 1)
        self.assertEqual(broken_page.error_count, 1)
        self.assertEqual(broken_get.error, failed[0].error)

        # 7. repair (host-native write, the `repair` flow's mechanism): a healthy rewrite must
        #    clear both the get_txt parse-failure channel and the list_txt failed row -- the
        #    content-hash-validated cache serves the fresh content, never the stale failure.
        expected_path.write_text(before_break, encoding="utf-8")

        repaired = get_txt(txt_id)
        self.assertIsInstance(repaired, TxtDocument)
        self.assertEqual(repaired.body.text, "Sample Review Notes")

        repaired_page = list_txt()
        self.assertEqual(repaired_page.error_count, 0)
        self.assertEqual(repaired_page.total, 1)
        self.assertEqual(repaired_page.results[0].status, "draft")

    def test_broken_document_unknown_id_still_raises_not_found(self) -> None:
        """With one broken file on disk, an id that matches no file at all must still raise
        TxtNotFoundError (the parse-failure channel only recovers the name-matching case)."""
        create_txt(_INITIAL_BODY)
        broken_path = txt_base_dir() / "broken.md"
        broken_path.write_text("not a valid document, no headings at all\n", encoding="utf-8")

        with self.assertRaises(TxtNotFoundError):
            get_txt("00000000-0000-0000-0000-000000000000")


if __name__ == "__main__":
    unittest.main()
