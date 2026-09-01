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

"""Tests for ``qa.tools._paths`` (base dir resolution, id lookup)."""

from __future__ import annotations

import os
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DEFAULT_DOCS_ROOT, DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.qa.tools._paths import (
    QA_TYPE_NAME,
    QaNotFoundError,
    ensure_qa_base_dir,
    find_qa_path,
    iter_qa_paths,
    qa_base_dir,
)

_DOC_TEMPLATE = textwrap.dedent(
    """\
    ---
    id: {id}
    type: qa
    version: 1.0.0
    status: draft
    created: '2026-08-18 00:00:00.000Z'
    updated: '2026-08-18 00:00:00.000Z'
    ---

    # Some QA Title

    ## General

    ### Introduction

    Some intro text.

    ### Raw Requirements

    Some raw requirements text.

    ## Elicitation Context

    ## Functional Suitability

    ## Performance Efficiency

    ## Compatibility

    ## Interaction Capability

    ## Reliability

    ## Security

    ## Maintainability

    ## Flexibility

    ## Safety
    """
)


def _qa_text(id_: str) -> str:
    """Render a minimal, valid QA document's text for the given id."""
    return _DOC_TEMPLATE.format(id=id_)


class TestQaBaseDir(unittest.TestCase):
    """Tests for qa_base_dir."""

    def test_defaults_when_env_var_unset(self):
        """Without SPECMGR_DOCS_DIR set, the default root's qa subdirectory is returned."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(DOCS_DIR_ENV_VAR, None)
            self.assertEqual(qa_base_dir(), DEFAULT_DOCS_ROOT / QA_TYPE_NAME)

    def test_respects_env_var(self):
        """SPECMGR_DOCS_DIR, when set, overrides the default root."""
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/some-custom-docs-dir"}):
            self.assertEqual(qa_base_dir(), Path("/tmp/some-custom-docs-dir/qa"))

    def test_does_not_create_the_directory(self):
        """qa_base_dir must never create the directory as a side effect."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                qa_base_dir()
            self.assertFalse(missing_root.exists())


class TestEnsureQaBaseDir(unittest.TestCase):
    """Tests for ensure_qa_base_dir."""

    def test_creates_the_directory(self):
        """ensure_qa_base_dir must create the directory (and its parents) if missing."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                result = ensure_qa_base_dir()
            self.assertTrue(result.exists())
            self.assertEqual(result, missing_root / QA_TYPE_NAME)


class TestIterQaPaths(unittest.TestCase):
    """Tests for iter_qa_paths."""

    def test_empty_iterator_for_missing_directory(self):
        """A non-existent qa_base_dir() must yield nothing, not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                self.assertEqual(list(iter_qa_paths()), [])

    def test_yields_md_files_sorted_by_name(self):
        """*.md files under qa_base_dir() must be yielded in sorted (by name) order."""
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: tmp}):
                base = ensure_qa_base_dir()
                (base / "b.md").write_text(_qa_text("b-id"), encoding="utf-8")
                (base / "a.md").write_text(_qa_text("a-id"), encoding="utf-8")
                (base / "not-markdown.txt").write_text("x", encoding="utf-8")
                paths = list(iter_qa_paths())
            self.assertEqual([p.name for p in paths], ["a.md", "b.md"])


class TestFindQaPath(unittest.TestCase):
    """Tests for find_qa_path."""

    def test_finds_matching_id(self):
        """A file whose frontmatter.id matches must be returned."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "target.md"
            path.write_text(_qa_text("target-id"), encoding="utf-8")
            self.assertEqual(find_qa_path(base, "target-id"), path)

    def test_raises_not_found_for_unknown_id(self):
        """An id with no matching file must raise QaNotFoundError with the standardized message."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "one.md").write_text(_qa_text("one-id"), encoding="utf-8")
            with self.assertRaises(QaNotFoundError) as ctx:
                find_qa_path(base, "missing-id")
            message = str(ctx.exception)
            self.assertIn("no Question and Answer (QA) document found with id 'missing-id'", message)
            self.assertIn("bare document UUID", message)
            self.assertIn("without a domain prefix", message)
            self.assertIn("not 'qa-<uuid>'", message)

    def test_skips_malformed_file_and_still_finds_valid_one(self):
        """A file that fails to parse must not prevent finding a different, valid id."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "broken.md").write_text("not a valid QA file at all, no headings", encoding="utf-8")
            good_path = base / "good.md"
            good_path.write_text(_qa_text("good-id"), encoding="utf-8")
            self.assertEqual(find_qa_path(base, "good-id"), good_path)


if __name__ == "__main__":
    unittest.main()
