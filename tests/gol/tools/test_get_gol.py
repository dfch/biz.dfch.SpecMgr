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

"""Tests for the ``get_gol`` ``@mcp.tool()`` wrapper (Task 3.8)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.general.tools.update import update
from biz.dfch.specmgr.gol.models.v1 import GolDocument
from biz.dfch.specmgr.gol.tools._paths import GolNotFoundError
from biz.dfch.specmgr.gol.tools.create_gol import create_gol
from biz.dfch.specmgr.gol.tools.get_gol import get_gol

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Competitive Engines in Consumer Vehicles

    THE company shall provide engines that are competitive in power output and fuel consumption.

    ## Source

    The vehicle program's 2027 market analysis
    """
)


class TestGetGol(unittest.TestCase):
    """Tests for the get_gol tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_matching_document(self) -> None:
        """get_gol must return the full GolDocument for a matching id."""
        created = create_gol(_MINIMAL_BODY)

        result = get_gol(created.frontmatter.id)

        self.assertIsInstance(result, GolDocument)
        self.assertEqual(result.frontmatter.id, created.frontmatter.id)
        self.assertEqual(result.body.text, "Competitive Engines in Consumer Vehicles")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """get_gol must raise GolNotFoundError, with the standardized message, when no goal matches."""
        create_gol(_MINIMAL_BODY)

        with self.assertRaises(GolNotFoundError) as ctx:
            get_gol("no-such-id")
        message = str(ctx.exception)
        self.assertIn("bare document UUID", message)
        self.assertIn("without a domain prefix", message)

    def _doc_path(self) -> Path:
        """The single on-disk document file seeded for this test."""
        matches = list((self.docs_root / "gol").glob("*.md"))
        self.assertEqual(len(matches), 1)
        result = matches[0]
        return result

    def test_raw_returns_body_text_via_shared_helper(self) -> None:
        """raw=True must return the frontmatter-stripped body text, byte-identical to the shared body_text helper's output."""
        created = create_gol(_MINIMAL_BODY)

        result = get_gol(created.frontmatter.id, raw=True)

        self.assertIsInstance(result, str)
        self.assertEqual(result, body_text(self._doc_path()))

    def test_raw_line_coordinates_index_into_the_splice_target(self) -> None:
        """The line numbers from a raw read must index byte-for-byte into the text the update splice targets (ACC-003)."""
        created = create_gol(_MINIMAL_BODY)
        lines = get_gol(created.frontmatter.id, raw=True).splitlines()
        k = (
            lines.index("THE company shall provide engines that are competitive in power output and fuel consumption.")
            + 1
        )
        replacement = "THE company shall provide competitive engines in power output and fuel consumption."

        update(id=created.frontmatter.id, type="gol", content=replacement, offset=k, limit=1)

        new_lines = get_gol(created.frontmatter.id, raw=True).splitlines()
        self.assertEqual(new_lines[k - 1], replacement)
        self.assertEqual(new_lines[: k - 1] + new_lines[k:], lines[: k - 1] + lines[k:])
        self.assertEqual(len(new_lines), len(lines))

    def test_raw_windowed_read_returns_the_requested_slice(self) -> None:
        """raw=True with offset/limit must return exactly the requested body window, each line
        keeping its trailing newline."""
        created = create_gol(_MINIMAL_BODY)
        doc_id = created.frontmatter.id
        lines = get_gol(doc_id, raw=True).splitlines()

        result = get_gol(doc_id, raw=True, offset=2, limit=3)

        self.assertIsInstance(result, str)
        self.assertEqual(result, "\n".join(lines[1:4]) + "\n")

    def test_raw_windowed_read_clamps_out_of_range_coordinates(self) -> None:
        """raw=True: an offset past the last body line returns the empty string, and a limit
        larger than the remaining lines caps at them."""
        created = create_gol(_MINIMAL_BODY)
        doc_id = created.frontmatter.id
        lines = get_gol(doc_id, raw=True).splitlines()

        self.assertEqual(get_gol(doc_id, raw=True, offset=len(lines) + 1), "")
        self.assertEqual(get_gol(doc_id, raw=True, offset=len(lines) + 10, limit=5), "")
        self.assertEqual(get_gol(doc_id, raw=True, offset=2, limit=len(lines) + 10), "\n".join(lines[1:]) + "\n")

    def test_coordinates_with_raw_false_raise_value_error(self) -> None:
        """offset/limit with raw=False must raise ValueError (naming raw), before any file access."""
        created = create_gol(_MINIMAL_BODY)

        with self.assertRaises(ValueError) as ctx:
            get_gol(created.frontmatter.id, raw=False, offset=2, limit=3)
        message = str(ctx.exception)
        self.assertIn("raw", message)
        self.assertIn("offset", message)
        with self.assertRaises(ValueError):
            get_gol(created.frontmatter.id, raw=False, limit=3)

    def test_windowed_raw_read_coordinates_index_into_the_splice_target(self) -> None:
        """The coordinates of a windowed raw read must splice at exactly those lines, unchanged
        regions byte-identical (ACC-003 windowed)."""
        created = create_gol(_MINIMAL_BODY)
        doc_id = created.frontmatter.id
        lines = get_gol(doc_id, raw=True).splitlines()
        k, m = 5, 3
        window = get_gol(doc_id, raw=True, offset=k, limit=m)
        self.assertEqual(window, "\n".join(lines[k - 1 : k - 1 + m]) + "\n")
        replacement = "## Source\n\nThe vehicle program's 2026 market analysis"

        update(id=doc_id, type="gol", content=replacement, offset=k, limit=m)

        new_lines = get_gol(doc_id, raw=True).splitlines()
        self.assertEqual(new_lines[k - 1 : k - 1 + m], replacement.splitlines())
        self.assertEqual(new_lines[: k - 1] + new_lines[k - 1 + m :], lines[: k - 1] + lines[k - 1 + m :])
        self.assertEqual(len(new_lines), len(lines))

    def test_raw_false_returns_parsed_document_as_before(self) -> None:
        """raw=False (explicit) must return the parsed document, exactly as the default call does."""
        created = create_gol(_MINIMAL_BODY)

        result = get_gol(created.frontmatter.id, raw=False)
        default = get_gol(created.frontmatter.id)

        self.assertIsInstance(result, GolDocument)
        self.assertEqual(result, default)

    def test_raw_unknown_id_raises_not_found_in_both_modes(self) -> None:
        """raw=True and raw=False must both raise GolNotFoundError for an unknown id, windowed raw
        reads included."""
        create_gol(_MINIMAL_BODY)

        with self.assertRaises(GolNotFoundError):
            get_gol("no-such-id", raw=True)
        with self.assertRaises(GolNotFoundError):
            get_gol("no-such-id", raw=True, offset=2, limit=3)
        with self.assertRaises(GolNotFoundError):
            get_gol("no-such-id", raw=False)


if __name__ == "__main__":
    unittest.main()
