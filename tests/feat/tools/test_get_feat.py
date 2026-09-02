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

"""Tests for the ``get_feat`` ``@mcp.tool()`` wrapper (Task 2.3)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.feat.models.v1 import FeatDocument
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, FeatNotFoundError
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.feat.tools.get_feat import get_feat
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.general.tools.update import update

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


class TestGetFeat(unittest.TestCase):
    """Tests for the get_feat tool."""

    def setUp(self) -> None:
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_root = tmp / "feat"
        self.enterContext(mock.patch.dict("os.environ", {FEAT_DIR_ENV_VAR: str(self.feat_root)}))

    def test_returns_matching_document(self) -> None:
        """get_feat must return the full FeatDocument for a matching id."""
        created = create_feat(_MINIMAL_BODY)

        result = get_feat(created.frontmatter.id)

        self.assertIsInstance(result, FeatDocument)
        self.assertEqual(result.frontmatter.id, created.frontmatter.id)
        self.assertEqual(result.body.text, "Feature: Example Widget")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """get_feat must raise FeatNotFoundError for an id with no matching folder."""
        create_feat(_MINIMAL_BODY)

        with self.assertRaises(FeatNotFoundError) as ctx:
            get_feat("feat-99-no-such-id")
        message = str(ctx.exception)
        self.assertIn("does not exist", message)

    def _doc_path(self, id_: str) -> Path:
        """The document's on-disk README.md path, for a given id."""
        result = self.feat_root / id_ / "README.md"
        return result

    def test_raw_returns_body_text_via_shared_helper(self) -> None:
        """raw=True must return the frontmatter-stripped body text, byte-identical to the shared body_text helper's output."""
        created = create_feat(_MINIMAL_BODY)

        result = get_feat(created.frontmatter.id, raw=True)

        self.assertIsInstance(result, str)
        self.assertEqual(result, body_text(self._doc_path(created.frontmatter.id)))

    def test_raw_line_coordinates_index_into_the_splice_target(self) -> None:
        """The line numbers from a raw read must index byte-for-byte into the text the update splice targets (ACC-003/ACC-004)."""
        created = create_feat(_MINIMAL_BODY)
        lines = get_feat(created.frontmatter.id, raw=True).splitlines()
        k = lines.index("Short description.") + 1
        replacement = "Updated short description."

        update(id=created.frontmatter.id, type="feat", content=replacement, offset=k, limit=1)

        new_lines = get_feat(created.frontmatter.id, raw=True).splitlines()
        self.assertEqual(new_lines[k - 1], replacement)
        self.assertEqual(new_lines[: k - 1] + new_lines[k:], lines[: k - 1] + lines[k:])
        self.assertEqual(len(new_lines), len(lines))

    def test_raw_windowed_read_returns_the_requested_slice(self) -> None:
        """raw=True with offset/limit must return exactly the requested body window, each line
        keeping its trailing newline."""
        created = create_feat(_MINIMAL_BODY)
        doc_id = created.frontmatter.id
        lines = get_feat(doc_id, raw=True).splitlines()

        result = get_feat(doc_id, raw=True, offset=2, limit=3)

        self.assertIsInstance(result, str)
        self.assertEqual(result, "\n".join(lines[1:4]) + "\n")

    def test_raw_windowed_read_clamps_out_of_range_coordinates(self) -> None:
        """raw=True: an offset past the last body line returns the empty string, and a limit
        larger than the remaining lines caps at them."""
        created = create_feat(_MINIMAL_BODY)
        doc_id = created.frontmatter.id
        lines = get_feat(doc_id, raw=True).splitlines()

        self.assertEqual(get_feat(doc_id, raw=True, offset=len(lines) + 1), "")
        self.assertEqual(get_feat(doc_id, raw=True, offset=len(lines) + 10, limit=5), "")
        self.assertEqual(get_feat(doc_id, raw=True, offset=2, limit=len(lines) + 10), "\n".join(lines[1:]) + "\n")

    def test_coordinates_with_raw_false_raise_value_error(self) -> None:
        """offset/limit with raw=False must raise ValueError (naming raw), before any file access."""
        created = create_feat(_MINIMAL_BODY)

        with self.assertRaises(ValueError) as ctx:
            get_feat(created.frontmatter.id, raw=False, offset=2, limit=3)
        message = str(ctx.exception)
        self.assertIn("raw", message)
        self.assertIn("offset", message)
        with self.assertRaises(ValueError):
            get_feat(created.frontmatter.id, raw=False, limit=3)

    def test_windowed_raw_read_coordinates_index_into_the_splice_target(self) -> None:
        """The coordinates of a windowed raw read must splice at exactly those lines, unchanged
        regions byte-identical (ACC-003 windowed)."""
        created = create_feat(_MINIMAL_BODY)
        doc_id = created.frontmatter.id
        lines = get_feat(doc_id, raw=True).splitlines()
        k, m = 5, 3
        window = get_feat(doc_id, raw=True, offset=k, limit=m)
        self.assertEqual(window, "\n".join(lines[k - 1 : k - 1 + m]) + "\n")
        replacement = "### Overview\n\nUpdated short description."

        update(id=doc_id, type="feat", content=replacement, offset=k, limit=m)

        new_lines = get_feat(doc_id, raw=True).splitlines()
        self.assertEqual(new_lines[k - 1 : k - 1 + m], replacement.splitlines())
        self.assertEqual(new_lines[: k - 1] + new_lines[k - 1 + m :], lines[: k - 1] + lines[k - 1 + m :])
        self.assertEqual(len(new_lines), len(lines))

    def test_raw_false_returns_parsed_document_as_before(self) -> None:
        """raw=False (explicit) must return the parsed document, exactly as the default call does."""
        created = create_feat(_MINIMAL_BODY)

        result = get_feat(created.frontmatter.id, raw=False)
        default = get_feat(created.frontmatter.id)

        self.assertIsInstance(result, FeatDocument)
        self.assertEqual(result, default)

    def test_raw_unknown_id_raises_not_found_in_both_modes(self) -> None:
        """raw=True and raw=False must both raise FeatNotFoundError for an unknown id, windowed raw
        reads included."""
        create_feat(_MINIMAL_BODY)

        with self.assertRaises(FeatNotFoundError):
            get_feat("feat-99-no-such-id", raw=True)
        with self.assertRaises(FeatNotFoundError):
            get_feat("feat-99-no-such-id", raw=True, offset=2, limit=3)
        with self.assertRaises(FeatNotFoundError):
            get_feat("feat-99-no-such-id", raw=False)


if __name__ == "__main__":
    unittest.main()
