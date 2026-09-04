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

"""Tests for the ``set_feat_id`` ``@mcp.tool()`` wrapper (feat-48-feat-id Phase 5, Task 5.3/5.4)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.feat.models.v1 import FeatDocument, FeatFrontmatter, parse_feat
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, FeatNotFoundError, README_FILENAME, feat_base_dir
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.feat.tools.set_feat_id import set_feat_id
from biz.dfch.specmgr.general.tools._splice import body_text

_MINIMAL_BODY = textwrap.dedent(
    """\
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

    #### 2026-08-30 16:47:59.981Z - Paused for review

    Free-form prose describing what happened in this update.
    """
)


def _body_with_title(title: str) -> str:
    return _MINIMAL_BODY.replace("Example Widget", title)


class TempFeatDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the feature base dir via SPECMGR_FEAT_DIR.

    Duplicated locally rather than imported from ``test_create_feat.py``, matching this
    codebase's existing precedent (``dec``/``rsk``'s own per-file fixture duplication) of not
    sharing test fixtures across files prematurely.
    """

    def setUp(self) -> None:
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_root = tmp / "feat"
        self.enterContext(mock.patch.dict("os.environ", {FEAT_DIR_ENV_VAR: str(self.feat_root)}))


class TestSetFeatId(TempFeatDirTestCase):
    """Tests for the set_feat_id tool."""

    def test_happy_path_renames_updates_frontmatter_and_preserves_body(self) -> None:
        """Renaming an id must update the folder + frontmatter id, bump updated, and leave the
        body byte-identical, with every other frontmatter field unchanged (ACC-005, REQ-006)."""
        created = create_feat(_MINIMAL_BODY, id="feat-0-get-update")
        old_path = feat_base_dir() / "feat-0-get-update" / README_FILENAME
        raw_body_before = body_text(old_path)
        updated_before = created.updated

        result = set_feat_id("feat-0-get-update", "feat-42-get-update")

        self.assertIsInstance(result, FeatFrontmatter)
        self.assertNotIsInstance(result, FeatDocument)
        self.assertFalse(hasattr(result, "body"))
        self.assertEqual(result.id, "feat-42-get-update")
        self.assertEqual(result.type, created.type)
        self.assertEqual(result.status, created.status)
        self.assertEqual(result.created, created.created)
        self.assertEqual(result.version, created.version)
        self.assertNotEqual(result.updated, updated_before)
        self.assertRegex(result.updated or "", r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})$")

        old_folder = feat_base_dir() / "feat-0-get-update"
        self.assertFalse(old_folder.exists())

        new_path = feat_base_dir() / "feat-42-get-update" / README_FILENAME
        self.assertTrue(new_path.exists())

        on_disk = parse_feat(new_path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk.frontmatter.id, "feat-42-get-update")

        raw_body_after = body_text(new_path)
        self.assertEqual(raw_body_after, raw_body_before)

    def test_target_id_already_exists_raises_and_leaves_both_untouched(self) -> None:
        """A target id whose folder already exists raises FileExistsError, without renaming
        or modifying either the source or the (already-existing) target (ACC-006)."""
        create_feat(_body_with_title("Widget A"), id="feat-0-a")
        create_feat(_body_with_title("Widget B"), id="feat-1-b")

        source_path = feat_base_dir() / "feat-0-a" / README_FILENAME
        target_path = feat_base_dir() / "feat-1-b" / README_FILENAME
        source_before = source_path.read_text(encoding="utf-8")
        target_before = target_path.read_text(encoding="utf-8")

        with self.assertRaises(FileExistsError):
            set_feat_id("feat-0-a", "feat-1-b")

        self.assertTrue(source_path.exists())
        self.assertTrue(target_path.exists())
        self.assertEqual(source_path.read_text(encoding="utf-8"), source_before)
        self.assertEqual(target_path.read_text(encoding="utf-8"), target_before)
        self.assertEqual(parse_feat(source_path.read_text(encoding="utf-8")).frontmatter.id, "feat-0-a")
        self.assertEqual(parse_feat(target_path.read_text(encoding="utf-8")).frontmatter.id, "feat-1-b")

    def test_source_id_not_found_raises_feat_not_found_error(self) -> None:
        """A non-resolvable source id raises FeatNotFoundError and creates nothing (ACC-007)."""
        with self.assertRaises(FeatNotFoundError):
            set_feat_id("feat-999-does-not-exist", "feat-100-whatever")

        self.assertFalse((feat_base_dir() / "feat-100-whatever").exists())

    def test_invalid_new_id_shape_raises_value_error_and_leaves_source_untouched(self) -> None:
        """A malformed new_id raises ValueError before any lock/fs access, leaving the source
        completely untouched (REQ-005's shape validation)."""
        create_feat(_MINIMAL_BODY, id="feat-0-get-update")
        source_path = feat_base_dir() / "feat-0-get-update" / README_FILENAME
        source_before = source_path.read_text(encoding="utf-8")

        malformed_ids = ["not-a-valid-id", "feat-abc-slug", "Feat-1-Slug"]
        for malformed_id in malformed_ids:
            with self.subTest(malformed_id=malformed_id):
                with self.assertRaises(ValueError):
                    set_feat_id("feat-0-get-update", malformed_id)

        self.assertTrue(source_path.exists())
        self.assertEqual(source_path.read_text(encoding="utf-8"), source_before)
        self.assertEqual(parse_feat(source_path.read_text(encoding="utf-8")).frontmatter.id, "feat-0-get-update")


if __name__ == "__main__":
    unittest.main()
