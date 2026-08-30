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

"""Tests for ``feat.tools._write.write_feat_file`` (shared create/update write helper, Task 2.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from biz.dfch.specmgr.feat.models.v1 import FeatFrontmatter, parse_feat
from biz.dfch.specmgr.feat.tools._paths import README_FILENAME
from biz.dfch.specmgr.feat.tools._write import write_feat_file

_BODY = textwrap.dedent(
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

    #### 2026-08-30 16:47:59.981Z — Paused for review

    Free-form prose describing what happened in this update.
    """
)


class TestWriteFeatFile(unittest.TestCase):
    """Tests for write_feat_file."""

    def test_writes_frontmatter_and_body_that_round_trips(self) -> None:
        """The written file must parse back into an equivalent document."""
        frontmatter = FeatFrontmatter(
            id="feat-1-example-widget",
            type="feat",
            status="planning",
            created="2026-08-30",
            updated="2026-08-30",
            version="1.0.0",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feat-1-example-widget" / README_FILENAME
            write_feat_file(path, frontmatter, _BODY)

            self.assertTrue(path.exists())
            document = parse_feat(path.read_text(encoding="utf-8"))
            self.assertEqual(document.frontmatter.id, "feat-1-example-widget")
            self.assertEqual(document.frontmatter.status, "planning")
            self.assertEqual(document.body.text, "Feature: Example Widget")

    def test_creates_the_parent_folder_if_missing(self) -> None:
        """Unlike dec's flat-file write_dec_file, write_feat_file must create <id>/ if it does not exist."""
        frontmatter = FeatFrontmatter(id="feat-1-example-widget")
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "feat-1-example-widget"
            self.assertFalse(folder.exists())
            path = folder / README_FILENAME

            write_feat_file(path, frontmatter, _BODY)

            self.assertTrue(folder.is_dir())
            self.assertTrue(path.exists())

    def test_file_ends_with_exactly_one_trailing_newline(self) -> None:
        """The written file must end with exactly one trailing newline."""
        frontmatter = FeatFrontmatter(id="feat-1-example-widget")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feat-1-example-widget" / README_FILENAME
            write_feat_file(path, frontmatter, _BODY)

            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.endswith("\n"))
            self.assertFalse(text.endswith("\n\n"))


if __name__ == "__main__":
    unittest.main()
