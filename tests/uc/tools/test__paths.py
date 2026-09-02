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

"""Tests for ``uc.tools._paths`` (base dir resolution, id lookup)."""

from __future__ import annotations

import os
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DEFAULT_DOCS_ROOT, DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.uc.tools._paths import (
    UC_TYPE_NAME,
    UcNotFoundError,
    ensure_uc_base_dir,
    find_uc_path,
    iter_uc_paths,
    uc_base_dir,
)

_DOC_TEMPLATE = textwrap.dedent(
    """\
    ---
    id: {id}
    type: uc
    version: 1.0.0
    status: draft
    created: '2026-08-05 00:00:00.000Z'
    updated: '2026-08-05 00:00:00.000Z'
    ---

    # Buy Goods

    ## Characteristic Information

    ### Goal in Context

    Buyer issues request directly to our company.

    ### Scope

    Company (the system being designed as a black box)

    ### Level

    Summary

    ### Preconditions

    - We know Buyer

    ### Success End Condition

    - Buyer has goods

    ### Primary Actor

    Buyer.

    ### Trigger

    Purchase request comes in.

    ## Main Success Scenario

    1. Buyer calls in with a purchase request.
    2. Company creates order in system.
    """
)


def _uc_text(id_: str) -> str:
    """Render a minimal, valid use-case document's text for the given id."""
    return _DOC_TEMPLATE.format(id=id_)


class TestUcBaseDir(unittest.TestCase):
    """Tests for uc_base_dir."""

    def test_defaults_when_env_var_unset(self):
        """Without SPECMGR_DOCS_DIR set, the default root's uc subdirectory is returned."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(DOCS_DIR_ENV_VAR, None)
            self.assertEqual(uc_base_dir(), DEFAULT_DOCS_ROOT / UC_TYPE_NAME)

    def test_respects_env_var(self):
        """SPECMGR_DOCS_DIR, when set, overrides the default root."""
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/some-custom-docs-dir"}):
            self.assertEqual(uc_base_dir(), Path("/tmp/some-custom-docs-dir/uc"))

    def test_does_not_create_the_directory(self):
        """uc_base_dir must never create the directory as a side effect."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                uc_base_dir()
            self.assertFalse(missing_root.exists())


class TestEnsureUcBaseDir(unittest.TestCase):
    """Tests for ensure_uc_base_dir."""

    def test_creates_the_directory(self):
        """ensure_uc_base_dir must create the directory (and its parents) if missing."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                result = ensure_uc_base_dir()
            self.assertTrue(result.exists())
            self.assertEqual(result, missing_root / UC_TYPE_NAME)


class TestIterUcPaths(unittest.TestCase):
    """Tests for iter_uc_paths."""

    def test_empty_iterator_for_missing_directory(self):
        """A non-existent uc_base_dir() must yield nothing, not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                self.assertEqual(list(iter_uc_paths()), [])

    def test_yields_md_files_sorted_by_name(self):
        """*.md files under uc_base_dir() must be yielded in sorted (by name) order."""
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: tmp}):
                base = ensure_uc_base_dir()
                (base / "b.md").write_text(_uc_text("b-id"), encoding="utf-8")
                (base / "a.md").write_text(_uc_text("a-id"), encoding="utf-8")
                (base / "not-markdown.txt").write_text("x", encoding="utf-8")
                paths = list(iter_uc_paths())
            self.assertEqual([p.name for p in paths], ["a.md", "b.md"])


class TestFindUcPath(unittest.TestCase):
    """Tests for find_uc_path."""

    def test_finds_matching_id(self):
        """A file whose frontmatter.id matches must be returned."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "target.md"
            path.write_text(_uc_text("target-id"), encoding="utf-8")
            self.assertEqual(find_uc_path(base, "target-id"), path)

    def test_raises_not_found_for_unknown_id(self):
        """An id with no matching file must raise UcNotFoundError with the standardized message."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "one.md").write_text(_uc_text("one-id"), encoding="utf-8")
            with self.assertRaises(UcNotFoundError) as ctx:
                find_uc_path(base, "missing-id")
            message = str(ctx.exception)
            self.assertIn("no use case found with id 'missing-id'", message)
            self.assertIn("bare document UUID", message)
            self.assertIn("without a domain prefix", message)
            self.assertIn("not 'uc-<uuid>'", message)

    def test_skips_malformed_file_and_still_finds_valid_one(self):
        """A file that fails to parse must not prevent finding a different, valid id."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "broken.md").write_text("not a valid UC file at all, no headings", encoding="utf-8")
            good_path = base / "good.md"
            good_path.write_text(_uc_text("good-id"), encoding="utf-8")
            self.assertEqual(find_uc_path(base, "good-id"), good_path)


if __name__ == "__main__":
    unittest.main()
