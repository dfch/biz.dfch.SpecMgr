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

"""Tests for ``dec.tools._paths`` (base dir resolution, id lookup)."""

from __future__ import annotations

import os
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DEFAULT_DOCS_ROOT, DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.dec.tools._paths import (
    DEC_TYPE_NAME,
    DecNotFoundError,
    dec_base_dir,
    ensure_dec_base_dir,
    find_dec_path,
    iter_dec_paths,
)

_DOC_TEMPLATE = textwrap.dedent(
    """\
    ---
    id: {id}
    type: dec
    version: 1.0.0
    status: draft
    created: '2026-08-26 00:00:00.000Z'
    updated: '2026-08-26 00:00:00.000Z'
    ---

    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Outcome

    We chose the document store.
    """
)


def _dec_text(id_: str) -> str:
    """Render a minimal, valid decision document's text for the given id."""
    return _DOC_TEMPLATE.format(id=id_)


class TestDecBaseDir(unittest.TestCase):
    """Tests for dec_base_dir."""

    def test_defaults_when_env_var_unset(self) -> None:
        """Without SPECMGR_DOCS_DIR set, the default root's dec subdirectory is returned."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(DOCS_DIR_ENV_VAR, None)
            self.assertEqual(dec_base_dir(), DEFAULT_DOCS_ROOT / DEC_TYPE_NAME)

    def test_respects_env_var(self) -> None:
        """SPECMGR_DOCS_DIR, when set, overrides the default root."""
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/some-custom-docs-dir"}):
            self.assertEqual(dec_base_dir(), Path("/tmp/some-custom-docs-dir/dec"))

    def test_does_not_create_the_directory(self) -> None:
        """dec_base_dir must never create the directory as a side effect."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                dec_base_dir()
            self.assertFalse(missing_root.exists())


class TestEnsureDecBaseDir(unittest.TestCase):
    """Tests for ensure_dec_base_dir."""

    def test_creates_the_directory(self) -> None:
        """ensure_dec_base_dir must create the directory (and its parents) if missing."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                result = ensure_dec_base_dir()
            self.assertTrue(result.exists())
            self.assertEqual(result, missing_root / DEC_TYPE_NAME)


class TestIterDecPaths(unittest.TestCase):
    """Tests for iter_dec_paths."""

    def test_empty_iterator_for_missing_directory(self) -> None:
        """A non-existent dec_base_dir() must yield nothing, not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                self.assertEqual(list(iter_dec_paths()), [])

    def test_yields_md_files_sorted_by_name(self) -> None:
        """*.md files under dec_base_dir() must be yielded in sorted (by name) order."""
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: tmp}):
                base = ensure_dec_base_dir()
                (base / "b.md").write_text(_dec_text("b-id"), encoding="utf-8")
                (base / "a.md").write_text(_dec_text("a-id"), encoding="utf-8")
                (base / "not-markdown.txt").write_text("x", encoding="utf-8")
                paths = list(iter_dec_paths())
            self.assertEqual([p.name for p in paths], ["a.md", "b.md"])


class TestFindDecPath(unittest.TestCase):
    """Tests for find_dec_path."""

    def test_finds_matching_id(self) -> None:
        """A file whose frontmatter.id matches must be returned."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "target.md"
            path.write_text(_dec_text("target-id"), encoding="utf-8")
            self.assertEqual(find_dec_path(base, "target-id"), path)

    def test_raises_not_found_for_unknown_id(self) -> None:
        """An id with no matching file must raise DecNotFoundError with the standardized message."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "one.md").write_text(_dec_text("one-id"), encoding="utf-8")
            with self.assertRaises(DecNotFoundError) as ctx:
                find_dec_path(base, "missing-id")
            message = str(ctx.exception)
            self.assertIn("no decision found with id 'missing-id'", message)
            self.assertIn("bare document UUID", message)
            self.assertIn("without a domain prefix", message)
            self.assertIn("not 'dec-<uuid>'", message)

    def test_skips_malformed_file_and_still_finds_valid_one(self) -> None:
        """A file that fails to parse must not prevent finding a different, valid id."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "broken.md").write_text("not a valid DEC file at all, no headings", encoding="utf-8")
            good_path = base / "good.md"
            good_path.write_text(_dec_text("good-id"), encoding="utf-8")
            self.assertEqual(find_dec_path(base, "good-id"), good_path)


if __name__ == "__main__":
    unittest.main()
