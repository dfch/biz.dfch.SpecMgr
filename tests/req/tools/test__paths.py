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

"""Tests for ``req.tools._paths`` (base dir resolution, id lookup)."""

from __future__ import annotations

import os
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DEFAULT_DOCS_ROOT, DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.req.tools._paths import (
    REQ_TYPE_NAME,
    ReqNotFoundError,
    ensure_req_base_dir,
    find_req_path,
    iter_req_paths,
    req_base_dir,
)

_DOC_TEMPLATE = textwrap.dedent(
    """\
    ---
    id: {id}
    type: req
    version: 1.0.0
    status: draft
    created: '2026-08-05 00:00:00.000Z'
    updated: '2026-08-05 00:00:00.000Z'
    ---

    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 80 \u00b0C.

    ## Description

    If the engine becomes too hot, the lifetime of the system decreases.

    ## Characteristics

    1. Safety
    1. Reliability

    ## Level

    MUST

    ## Source

    The International Safety Board Association (TISBA)
    """
)


def _req_text(id_: str) -> str:
    """Render a minimal, valid requirement document's text for the given id."""
    return _DOC_TEMPLATE.format(id=id_)


class TestReqBaseDir(unittest.TestCase):
    """Tests for req_base_dir."""

    def test_defaults_when_env_var_unset(self):
        """Without SPECMGR_DOCS_DIR set, the default root's req subdirectory is returned."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(DOCS_DIR_ENV_VAR, None)
            self.assertEqual(req_base_dir(), DEFAULT_DOCS_ROOT / REQ_TYPE_NAME)

    def test_respects_env_var(self):
        """SPECMGR_DOCS_DIR, when set, overrides the default root."""
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/some-custom-docs-dir"}):
            self.assertEqual(req_base_dir(), Path("/tmp/some-custom-docs-dir/req"))

    def test_does_not_create_the_directory(self):
        """req_base_dir must never create the directory as a side effect."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                req_base_dir()
            self.assertFalse(missing_root.exists())


class TestEnsureReqBaseDir(unittest.TestCase):
    """Tests for ensure_req_base_dir."""

    def test_creates_the_directory(self):
        """ensure_req_base_dir must create the directory (and its parents) if missing."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                result = ensure_req_base_dir()
            self.assertTrue(result.exists())
            self.assertEqual(result, missing_root / REQ_TYPE_NAME)


class TestIterReqPaths(unittest.TestCase):
    """Tests for iter_req_paths."""

    def test_empty_iterator_for_missing_directory(self):
        """A non-existent req_base_dir() must yield nothing, not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                self.assertEqual(list(iter_req_paths()), [])

    def test_yields_md_files_sorted_by_name(self):
        """*.md files under req_base_dir() must be yielded in sorted (by name) order."""
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: tmp}):
                base = ensure_req_base_dir()
                (base / "b.md").write_text(_req_text("b-id"), encoding="utf-8")
                (base / "a.md").write_text(_req_text("a-id"), encoding="utf-8")
                (base / "not-markdown.txt").write_text("x", encoding="utf-8")
                paths = list(iter_req_paths())
            self.assertEqual([p.name for p in paths], ["a.md", "b.md"])


class TestFindReqPath(unittest.TestCase):
    """Tests for find_req_path."""

    def test_finds_matching_id(self):
        """A file whose frontmatter.id matches must be returned."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "target.md"
            path.write_text(_req_text("target-id"), encoding="utf-8")
            self.assertEqual(find_req_path(base, "target-id"), path)

    def test_raises_not_found_for_unknown_id(self):
        """An id with no matching file must raise ReqNotFoundError with the standardized message."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "one.md").write_text(_req_text("one-id"), encoding="utf-8")
            with self.assertRaises(ReqNotFoundError) as ctx:
                find_req_path(base, "missing-id")
            message = str(ctx.exception)
            self.assertIn("no requirement found with id 'missing-id'", message)
            self.assertIn("bare document UUID", message)
            self.assertIn("without a domain prefix", message)
            self.assertIn("not 'req-<uuid>'", message)

    def test_skips_malformed_file_and_still_finds_valid_one(self):
        """A file that fails to parse must not prevent finding a different, valid id."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "broken.md").write_text("not a valid REQ file at all, no headings", encoding="utf-8")
            good_path = base / "good.md"
            good_path.write_text(_req_text("good-id"), encoding="utf-8")
            self.assertEqual(find_req_path(base, "good-id"), good_path)


if __name__ == "__main__":
    unittest.main()
