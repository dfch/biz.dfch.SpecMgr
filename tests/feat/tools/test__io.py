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

"""Tests for ``feat.tools._io`` (thin file read helpers, Task 2.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from biz.dfch.specmgr.feat.models.v1 import FeatDocument
from biz.dfch.specmgr.feat.tools._io import load_by_id, read_feat
from biz.dfch.specmgr.feat.tools._paths import FeatNotFoundError, README_FILENAME

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

    #### 2026-08-30 16:47:59.981Z - Paused for review

    Free-form prose describing what happened in this update.
    """
)


def _feat_text(id_: str) -> str:
    """Render a minimal, valid feature document's text for the given id."""
    return _DOC_TEMPLATE.format(id=id_)


class TestReadFeat(unittest.TestCase):
    """Tests for read_feat."""

    def test_reads_and_parses_a_real_file(self) -> None:
        """read_feat must return a FeatDocument matching the file's own content."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / README_FILENAME
            path.write_text(_feat_text("feat-1-example-widget"), encoding="utf-8")

            document = read_feat(path)

            self.assertIsInstance(document, FeatDocument)
            self.assertEqual(document.frontmatter.id, "feat-1-example-widget")
            self.assertEqual(document.body.text, "Feature: Example Widget")


class TestLoadById(unittest.TestCase):
    """Tests for load_by_id."""

    def test_returns_path_and_parsed_feat(self) -> None:
        """load_by_id must return both the resolved path and the parsed document."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            folder = base / "feat-1-example-widget"
            folder.mkdir()
            expected_path = folder / README_FILENAME
            expected_path.write_text(_feat_text("feat-1-example-widget"), encoding="utf-8")

            path, document = load_by_id(base, "feat-1-example-widget")

            self.assertEqual(path, expected_path)
            self.assertEqual(document.frontmatter.id, "feat-1-example-widget")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """load_by_id must raise FeatNotFoundError for an id with no matching folder."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with self.assertRaises(FeatNotFoundError):
                load_by_id(base, "feat-99-does-not-exist")


if __name__ == "__main__":
    unittest.main()
