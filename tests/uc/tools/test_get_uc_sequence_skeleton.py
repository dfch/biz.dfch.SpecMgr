# Copyright (C) 2026 Ronald Rink, http://d-fens.ch
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

"""Tests for the ``get_uc_sequence_skeleton`` ``@mcp.tool()`` wrapper (feat-185-uc-diagrams, Phase 120).

Read-only id-based diagram tool: the id resolution mirrors ``get_uc``
(``_path_safety``-guarded, cache-aware; a truly-absent id raises the
domain's not-found error, an existing-but-broken document returns the
non-raising ``ParseFailureResult`` per the feat-150 precedent), and the
rendering is the pure ``render_uc_sequence_skeleton`` (the tool is thin --
pinned here against the renderer and the frozen golden, including the
UNATTRIBUTED markers the checker reports as warnings in both modes).
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import ParseFailureResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text
from biz.dfch.specmgr.plantuml import structure as S
from biz.dfch.specmgr.uc.models.v2 import parse_uc
from biz.dfch.specmgr.uc.models.v2.renderer import render_uc_sequence_skeleton
from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError
from biz.dfch.specmgr.uc.tools.create_uc import create_uc
from biz.dfch.specmgr.uc.tools.get_uc_sequence_skeleton import get_uc_sequence_skeleton

#: A well-formed but non-existent canonical UUID (the id must be well-formed
#: to reach the domain's own not-found error past the ``validate_id`` guard).
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"
_GOLDENS = Path(__file__).resolve().parents[2] / "fixtures" / "uc-diagrams"


def _example_body() -> str:
    """The packaged example's body markdown (frontmatter block stripped -- ``create_uc`` takes body
    markdown only, and assigns its own fresh id)."""
    full = read_packaged_text("uc", "example")
    assert full.startswith("---\n")
    end = full.index("\n---\n") + len("\n---\n")
    result = full[end:]
    return result


_MINIMAL_BODY = textwrap.dedent(
    """\
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


class TestGetUcSequenceSkeleton(unittest.TestCase):
    """Tests for the get_uc_sequence_skeleton tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def _doc_path(self) -> Path:
        """The single on-disk document file seeded for this test."""
        matches = list((self.docs_root / "uc").glob("*.md"))
        self.assertEqual(len(matches), 1)
        result = matches[0]
        return result

    def test_renders_the_packaged_example_like_the_pure_renderer(self):
        """For a real document, the tool must return exactly render_uc_sequence_skeleton(doc.body)."""
        example = read_packaged_text("uc", "example")
        created = create_uc(_example_body())

        result = get_uc_sequence_skeleton(created.id)

        self.assertIsInstance(result, str)
        self.assertEqual(result, render_uc_sequence_skeleton(parse_uc(example).body))

    def test_returns_the_buy_goods_skeleton_golden(self):
        """The packaged example must render byte-identical to the frozen rulebook §2.9 golden."""
        created = create_uc(_example_body())

        result = get_uc_sequence_skeleton(created.id)

        golden = (_GOLDENS / "buy-goods.sequence.golden").read_text(encoding="utf-8")
        self.assertEqual(result, golden)

    def test_skeleton_carries_the_unattributed_markers_as_checker_warnings(self):
        """The example skeleton must carry UNATTRIBUTED marker lines -- warnings in both checker
        modes (deliberate placeholders the agent flow resolves; the zero-marker rule is the
        prompt flow's, not the checker's)."""
        created = create_uc(_example_body())

        result = get_uc_sequence_skeleton(created.id)

        marker_lines = [line for line in result.split("\n") if line.startswith(S.UNATTRIBUTED_MARKER_PREFIX)]
        self.assertEqual(len(marker_lines), 5)
        for mode in (S.MODE_PREFLIGHT, S.MODE_STANDALONE):
            with self.subTest(mode=mode):
                check = S.check_structure(result, mode)
                self.assertTrue(check.ok)
                self.assertEqual(len(check.warnings), 5)
                for warning in check.warnings:
                    self.assertIn("UNATTRIBUTED marker", warning.message)

    def test_wrong_format_id_raises_value_error_before_any_file_access(self):
        """An id that is not a well-formed canonical UUID must raise ValueError (the _path_safety guard)."""
        with self.assertRaises(ValueError) as ctx:
            get_uc_sequence_skeleton("not-a-well-formed-uuid")
        self.assertIn("not-a-well-formed-uuid", str(ctx.exception))
        with self.assertRaises(ValueError):
            get_uc_sequence_skeleton("../escape")

    def test_unknown_id_raises_not_found(self):
        """A well-formed id with no matching document must raise UcNotFoundError."""
        create_uc(_MINIMAL_BODY)

        with self.assertRaises(UcNotFoundError):
            get_uc_sequence_skeleton(_MISSING_UUID)

    def test_broken_document_returns_parse_failure_result(self):
        """An id whose on-disk file exists but fails to parse must return the feat-150
        ParseFailureResult channel, never the not-found error and never a skeleton."""
        created = create_uc(_MINIMAL_BODY)
        self._doc_path().write_text("not a valid document, no headings at all\n", encoding="utf-8")

        result = get_uc_sequence_skeleton(created.id)

        self.assertIsInstance(result, ParseFailureResult)
        self.assertNotIsInstance(result, str)
        self.assertEqual(result.id, created.id)
        self.assertEqual(result.path, str(self._doc_path().resolve()))
        self.assertTrue(result.error)


if __name__ == "__main__":
    unittest.main()
