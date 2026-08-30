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

"""Tests for ``feat.tools._paths`` (base dir resolution, hand-rolled id lookup, Task 2.1)."""

from __future__ import annotations

import os
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.feat.tools._paths import (
    DEFAULT_FEAT_DIR,
    FEAT_DIR_ENV_VAR,
    README_FILENAME,
    FeatNotFoundError,
    ensure_feat_base_dir,
    feat_base_dir,
    feature_title,
    find_feat_path_by_id,
    iter_feat_paths,
)

_DOC_TEMPLATE = textwrap.dedent(
    """\
    ---
    id: {id}
    type: feat
    version: 1.0.0
    status: planning
    created: 2026-08-30
    updated: 2026-08-30
    ---

    # Feature: Example Widget

    ## Plan

    ### Overview

    Short description.

    ### Requirements

    - REQ-001: The widget must render within 200ms.

    ### Acceptance Criteria

    - [ ] ACC-001: Render time stays below 200ms.

    ### Scope

    #### Included

    - The widget component itself.

    #### Explicitly Out Of Scope

    - Mobile touch gestures.

    ### Task List

    #### Phase 0: Scaffolding

    - [x] Task 0.1: Create branch and package skeleton

    ## Progress

    ### Current Status

    **As of 2026-08-30**: free-form narrative.

    ### Updates

    #### 2026-08-30 16:47:59.981Z — Paused for review

    Free-form prose describing what happened in this update.
    """
)


def _feat_text(id_: str) -> str:
    """Render a minimal, valid feature document's text for the given id."""
    return _DOC_TEMPLATE.format(id=id_)


def _write_feat_folder(base: Path, folder_name: str, id_: str) -> Path:
    """Write ``<base>/<folder_name>/README.md`` with the given frontmatter id, returning its path."""
    folder = base / folder_name
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / README_FILENAME
    path.write_text(_feat_text(id_), encoding="utf-8")
    return path


class TestFeatBaseDir(unittest.TestCase):
    """Tests for feat_base_dir."""

    def test_defaults_when_env_var_unset(self) -> None:
        """Without SPECMGR_FEAT_DIR set, DEFAULT_FEAT_DIR is returned."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(FEAT_DIR_ENV_VAR, None)
            self.assertEqual(feat_base_dir(), DEFAULT_FEAT_DIR)

    def test_respects_env_var(self) -> None:
        """SPECMGR_FEAT_DIR, when set, overrides the default."""
        with mock.patch.dict(os.environ, {FEAT_DIR_ENV_VAR: "/tmp/some-custom-feat-dir"}):
            self.assertEqual(feat_base_dir(), Path("/tmp/some-custom-feat-dir"))

    def test_does_not_create_the_directory(self) -> None:
        """feat_base_dir must never create the directory as a side effect."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {FEAT_DIR_ENV_VAR: str(missing_root)}):
                feat_base_dir()
            self.assertFalse(missing_root.exists())


class TestEnsureFeatBaseDir(unittest.TestCase):
    """Tests for ensure_feat_base_dir."""

    def test_creates_the_directory(self) -> None:
        """ensure_feat_base_dir must create the directory (and its parents) if missing."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {FEAT_DIR_ENV_VAR: str(missing_root)}):
                result = ensure_feat_base_dir()
            self.assertTrue(result.exists())
            self.assertEqual(result, missing_root)


class TestFeatureTitle(unittest.TestCase):
    """Tests for feature_title."""

    def test_strips_the_feature_prefix(self) -> None:
        self.assertEqual(feature_title("Feature: My Title"), "My Title")

    def test_leaves_text_without_the_prefix_unchanged(self) -> None:
        self.assertEqual(feature_title("Some Other Text"), "Some Other Text")


class TestIterFeatPaths(unittest.TestCase):
    """Tests for iter_feat_paths."""

    def test_empty_iterator_for_missing_directory(self) -> None:
        """A non-existent base_dir must yield nothing, not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist"
            self.assertEqual(list(iter_feat_paths(missing_root)), [])

    def test_yields_readme_files_one_level_deep_sorted_by_folder_name(self) -> None:
        """<base>/*/README.md files must be yielded, sorted by folder name -- not <base>/*.md."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _write_feat_folder(base, "feat-2-b", "feat-2-b")
            _write_feat_folder(base, "feat-1-a", "feat-1-a")
            (base / "not-a-feature-folder.md").write_text("x", encoding="utf-8")

            paths = list(iter_feat_paths(base))

            self.assertEqual([p.parent.name for p in paths], ["feat-1-a", "feat-2-b"])
            for p in paths:
                self.assertEqual(p.name, README_FILENAME)


class TestFindFeatPathById(unittest.TestCase):
    """Tests for find_feat_path_by_id (the hand-rolled, no-scan shortcut)."""

    def test_resolves_via_direct_shortcut(self) -> None:
        """A folder named exactly `id_` with a matching frontmatter id must be returned."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            expected_path = _write_feat_folder(base, "feat-1-example-widget", "feat-1-example-widget")

            self.assertEqual(find_feat_path_by_id(base, "feat-1-example-widget"), expected_path)

    def test_raises_not_found_for_missing_folder(self) -> None:
        """A missing <base>/<id>/README.md must raise FeatNotFoundError, mentioning the path."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)

            with self.assertRaises(FeatNotFoundError) as ctx:
                find_feat_path_by_id(base, "feat-1-does-not-exist")
            message = str(ctx.exception)
            self.assertIn("no feature found with id 'feat-1-does-not-exist'", message)
            self.assertIn("does not exist", message)

    def test_does_not_support_partial_id_match(self) -> None:
        """A bare prefix ('feat-31') must NOT resolve to a differently-named folder ('feat-31-feature')."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _write_feat_folder(base, "feat-31-feature", "feat-31-feature")

            with self.assertRaises(FeatNotFoundError):
                find_feat_path_by_id(base, "feat-31")

    def test_raises_not_found_for_id_folder_mismatch(self) -> None:
        """A folder whose frontmatter id does not match its own folder name must raise, distinctly."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _write_feat_folder(base, "feat-1-example-widget", "feat-1-a-different-id")

            with self.assertRaises(FeatNotFoundError) as ctx:
                find_feat_path_by_id(base, "feat-1-example-widget")
            message = str(ctx.exception)
            self.assertIn("does not match the containing folder", message)

    def test_raises_not_found_for_unparseable_folder(self) -> None:
        """A folder whose README.md fails to parse must raise FeatNotFoundError, distinctly."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            folder = base / "feat-1-broken"
            folder.mkdir(parents=True)
            (folder / README_FILENAME).write_text("not a valid feature document at all", encoding="utf-8")

            with self.assertRaises(FeatNotFoundError) as ctx:
                find_feat_path_by_id(base, "feat-1-broken")
            message = str(ctx.exception)
            self.assertIn("could not be parsed", message)


if __name__ == "__main__":
    unittest.main()
