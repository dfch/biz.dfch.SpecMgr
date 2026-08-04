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

"""Tests for ``adr.tools._paths`` (base dir resolution, slugify, id lookup)."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.models.adr import Adr, AdrBody, AdrFrontmatter, render_adr
from biz.dfch.specmgr.adr.tools._paths import (
    ADR_DIR_ENV_VAR,
    DEFAULT_ADR_DIR,
    AdrNotFoundError,
    adr_base_dir,
    find_adr_path,
    iter_adr_paths,
    slugify,
)


def _adr(id_: str | None = None, title: str = "A title") -> Adr:
    return Adr(
        frontmatter=AdrFrontmatter(id=id_),
        body=AdrBody(
            title=title,
            context_and_problem_statement="Context.",
            considered_options="Options.",
            decision_outcome="Outcome.",
        ),
    )


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

    def test_empty_result_falls_back_to_adr(self):
        """A title with no alphanumeric characters at all must fall back to 'adr'."""
        self.assertEqual(slugify("!!!???"), "adr")


class TestAdrBaseDir(unittest.TestCase):
    """Tests for adr_base_dir."""

    def test_defaults_when_env_var_unset(self):
        """Without SPECMGR_ADR_DIR set, the default path is returned."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(ADR_DIR_ENV_VAR, None)
            self.assertEqual(adr_base_dir(), DEFAULT_ADR_DIR)

    def test_respects_env_var(self):
        """SPECMGR_ADR_DIR, when set, overrides the default."""
        with mock.patch.dict(os.environ, {ADR_DIR_ENV_VAR: "/tmp/some-custom-adr-dir"}):
            self.assertEqual(adr_base_dir(), Path("/tmp/some-custom-adr-dir"))

    def test_does_not_create_the_directory(self):
        """adr_base_dir must never create the directory as a side effect."""
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {ADR_DIR_ENV_VAR: str(missing)}):
                adr_base_dir()
            self.assertFalse(missing.exists())


class TestIterAdrPaths(unittest.TestCase):
    """Tests for iter_adr_paths."""

    def test_empty_iterator_for_missing_directory(self):
        """A non-existent base_dir must yield nothing, not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist"
            self.assertEqual(list(iter_adr_paths(missing)), [])

    def test_empty_iterator_for_empty_directory(self):
        """An existing but empty directory must yield nothing."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(list(iter_adr_paths(Path(tmp))), [])

    def test_yields_md_files_sorted_by_name(self):
        """*.md files must be yielded in sorted (by name) order."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "b.md").write_text("b", encoding="utf-8")
            (base / "a.md").write_text("a", encoding="utf-8")
            (base / "not-markdown.txt").write_text("x", encoding="utf-8")
            paths = list(iter_adr_paths(base))
            self.assertEqual([p.name for p in paths], ["a.md", "b.md"])


class TestFindAdrPath(unittest.TestCase):
    """Tests for find_adr_path."""

    def test_finds_matching_id(self):
        """A file whose frontmatter.id matches must be returned."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "target.md"
            path.write_text(render_adr(_adr(id_="target-id")), encoding="utf-8")
            self.assertEqual(find_adr_path(base, "target-id"), path)

    def test_raises_not_found_for_unknown_id(self):
        """An id with no matching file must raise AdrNotFoundError."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "one.md").write_text(render_adr(_adr(id_="one-id")), encoding="utf-8")
            with self.assertRaises(AdrNotFoundError):
                find_adr_path(base, "missing-id")

    def test_skips_malformed_file_and_still_finds_valid_one(self):
        """A file that fails to parse must not prevent finding a different, valid id."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "broken.md").write_text("not a valid ADR file at all, no headings", encoding="utf-8")
            good_path = base / "good.md"
            good_path.write_text(render_adr(_adr(id_="good-id")), encoding="utf-8")
            self.assertEqual(find_adr_path(base, "good-id"), good_path)


if __name__ == "__main__":
    unittest.main()
