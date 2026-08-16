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

"""Tests for ``general.tools._doc_paths`` (base dir resolution, slugify, id lookup)."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import (
    DEFAULT_DOCS_ROOT,
    DOCS_DIR_ENV_VAR,
    DocNotFoundError,
    doc_base_dir,
    ensure_doc_base_dir,
    find_doc_path_by_id,
    iter_doc_paths,
    slugify,
)


class _FakeDoc:
    """Minimal stand-in for a parsed document, holding just an id."""

    def __init__(self, id_: str | None) -> None:
        self.id = id_


def _parse_fake(text: str) -> _FakeDoc:
    """Parse fixture text into a ``_FakeDoc``; ``"BROKEN"`` simulates a parse failure."""
    stripped = text.strip()
    if stripped == "BROKEN":
        raise ValueError("simulated parse failure")
    return _FakeDoc(id_=stripped or None)


def _get_id(doc: _FakeDoc) -> str | None:
    return doc.id


class TestSlugify(unittest.TestCase):
    """Tests for slugify."""

    def test_lowercases(self):
        """Upper-case letters must be lowercased."""
        self.assertEqual(slugify("A Title"), "a-title")

    def test_collapses_non_alnum_runs(self):
        """A run of non-alphanumeric characters must collapse to a single hyphen."""
        self.assertEqual(slugify("A  Title!! With--Punctuation"), "a-title-with-punctuation")

    def test_strips_leading_and_trailing_hyphens(self):
        """Leading/trailing separator characters must not survive as hyphens."""
        self.assertEqual(slugify("!!!A Title!!!"), "a-title")

    def test_truncates_to_60_characters(self):
        """The slug must be truncated to 60 characters."""
        long_title = "word " * 30  # much longer than 60 chars once slugified
        slug = slugify(long_title)
        self.assertLessEqual(len(slug), 60)

    def test_truncation_does_not_leave_a_trailing_hyphen(self):
        """Truncating mid-run must not leave a dangling trailing hyphen."""
        # Constructed so the 60-char cut lands exactly on a hyphen.
        title = "a" * 59 + " " + "b" * 10
        slug = slugify(title)
        self.assertFalse(slug.endswith("-"))

    def test_empty_result_falls_back_to_doc(self):
        """A title with no alphanumeric characters at all must fall back to 'doc'."""
        self.assertEqual(slugify("!!!???"), "doc")


class TestDocBaseDir(unittest.TestCase):
    """Tests for doc_base_dir."""

    def test_defaults_when_env_var_unset(self):
        """Without SPECMGR_DOCS_DIR set, the default root + type_name is returned."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(DOCS_DIR_ENV_VAR, None)
            self.assertEqual(doc_base_dir("req"), DEFAULT_DOCS_ROOT / "req")

    def test_respects_env_var(self):
        """SPECMGR_DOCS_DIR, when set, overrides the default root."""
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/some-custom-docs-dir"}):
            self.assertEqual(doc_base_dir("req"), Path("/tmp/some-custom-docs-dir/req"))

    def test_different_type_names_yield_different_subdirectories(self):
        """Each doc type gets its own subdirectory under the shared root."""
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/some-custom-docs-dir"}):
            self.assertEqual(doc_base_dir("req"), Path("/tmp/some-custom-docs-dir/req"))
            self.assertEqual(doc_base_dir("uc"), Path("/tmp/some-custom-docs-dir/uc"))

    def test_does_not_create_the_directory(self):
        """doc_base_dir must never create the directory as a side effect."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                doc_base_dir("req")
            self.assertFalse(missing_root.exists())


class TestEnsureDocBaseDir(unittest.TestCase):
    """Tests for ensure_doc_base_dir."""

    def test_creates_the_directory(self):
        """ensure_doc_base_dir must create the directory (and its parents) if missing."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                result = ensure_doc_base_dir("req")
            self.assertTrue(result.exists())
            self.assertEqual(result, missing_root / "req")

    def test_is_idempotent_for_an_already_existing_directory(self):
        """Calling ensure_doc_base_dir twice must not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: tmp}):
                ensure_doc_base_dir("req")
                result = ensure_doc_base_dir("req")
            self.assertTrue(result.exists())


class TestIterDocPaths(unittest.TestCase):
    """Tests for iter_doc_paths."""

    def test_empty_iterator_for_missing_directory(self):
        """A non-existent base_dir must yield nothing, not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist"
            self.assertEqual(list(iter_doc_paths(missing)), [])

    def test_empty_iterator_for_empty_directory(self):
        """An existing but empty directory must yield nothing."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(list(iter_doc_paths(Path(tmp))), [])

    def test_yields_md_files_sorted_by_name(self):
        """*.md files must be yielded in sorted (by name) order."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "b.md").write_text("b", encoding="utf-8")
            (base / "a.md").write_text("a", encoding="utf-8")
            (base / "not-markdown.txt").write_text("x", encoding="utf-8")
            paths = list(iter_doc_paths(base))
            self.assertEqual([p.name for p in paths], ["a.md", "b.md"])


class TestFindDocPathById(unittest.TestCase):
    """Tests for find_doc_path_by_id."""

    def test_finds_matching_id(self):
        """A file whose parsed id matches must be returned."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "target.md"
            path.write_text("target-id", encoding="utf-8")
            self.assertEqual(find_doc_path_by_id(base, "target-id", _parse_fake, _get_id), path)

    def test_raises_not_found_for_unknown_id(self):
        """An id with no matching file must raise DocNotFoundError with the standardized message."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "one.md").write_text("one-id", encoding="utf-8")
            with self.assertRaises(DocNotFoundError) as ctx:
                find_doc_path_by_id(base, "missing-id", _parse_fake, _get_id)
            message = str(ctx.exception)
            self.assertIn("no document found with id 'missing-id'", message)
            self.assertIn("bare document UUID", message)
            self.assertIn("without a domain prefix", message)

    def test_raises_not_found_for_empty_directory(self):
        """An empty base_dir must raise DocNotFoundError, not e.g. StopIteration."""
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(DocNotFoundError):
                find_doc_path_by_id(Path(tmp), "missing-id", _parse_fake, _get_id)

    def test_skips_malformed_file_and_still_finds_valid_one(self):
        """A file that fails to parse must not prevent finding a different, valid id."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "broken.md").write_text("BROKEN", encoding="utf-8")
            good_path = base / "good.md"
            good_path.write_text("good-id", encoding="utf-8")
            self.assertEqual(find_doc_path_by_id(base, "good-id", _parse_fake, _get_id), good_path)

    def test_is_generic_over_doc_type_via_parse_and_get_id_functions(self):
        """A different parse_fn/get_id_fn pair must work independently (no ADR/REQ coupling)."""

        class _OtherDoc:
            def __init__(self, ident: str) -> None:
                self.ident = ident

        def _parse_other(text: str) -> _OtherDoc:
            return _OtherDoc(ident=text.strip())

        def _get_other_id(doc: _OtherDoc) -> str:
            return doc.ident

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "other.md"
            path.write_text("other-id", encoding="utf-8")
            self.assertEqual(find_doc_path_by_id(base, "other-id", _parse_other, _get_other_id), path)


if __name__ == "__main__":
    unittest.main()
