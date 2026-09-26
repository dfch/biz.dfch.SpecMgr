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

"""Tests for the ``get_rsk`` ``@mcp.tool()`` wrapper (Task 3.8)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.general.tools.update import update
from biz.dfch.specmgr.rsk.models.v1 import RskDocument
from biz.dfch.specmgr.rsk.tools._paths import RskNotFoundError
from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk
from biz.dfch.specmgr.rsk.tools.get_rsk import get_rsk
from biz.dfch.specmgr.rsk.tools.list_rsk import list_rsk
from biz.dfch.specmgr.general.models import ParseFailureResult

from ._helpers import MANDATORY_SOURCE


#: A well-formed but non-existent canonical UUID (feat-38-39-41-43-44 Phase 4: the id
#: must be well-formed to reach the domain's own not-found error past the new
#: ``validate_id`` guard).
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"
_MINIMAL_BODY = (
    textwrap.dedent(
        """\
        # Sample Risk

        ## Cause

        A root condition.

        ## Trigger

        An event that sets the risk in motion.

        ## Consequence

        A bounded consequence.

        ## Scope

        - Sample subsystem

        ## Initial Assessment

        ### Probability 4

        ### Impact 3

        ## Strategy

        reduce

        ## Mitigation

        Sample treatment measures.

        ## Residual Assessment

        ### Probability 2

        ### Impact 3
        """
    )
    + MANDATORY_SOURCE
)


class TestGetRsk(unittest.TestCase):
    """Tests for the get_rsk tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_matching_document(self) -> None:
        """get_rsk must return the full RskDocument for a matching id."""
        created = create_rsk(_MINIMAL_BODY)

        result = get_rsk(created.id)

        self.assertIsInstance(result, RskDocument)
        self.assertEqual(result.frontmatter.id, created.id)
        self.assertEqual(result.body.text, "Sample Risk")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """get_rsk must raise RskNotFoundError, with the standardized message, when no risk matches."""
        create_rsk(_MINIMAL_BODY)

        with self.assertRaises(RskNotFoundError) as ctx:
            get_rsk(_MISSING_UUID)
        message = str(ctx.exception)
        self.assertIn("bare document UUID", message)
        self.assertIn("without a domain prefix", message)

    def _doc_path(self) -> Path:
        """The single on-disk document file seeded for this test."""
        matches = list((self.docs_root / "rsk").glob("*.md"))
        self.assertEqual(len(matches), 1)
        result = matches[0]
        return result

    def test_raw_returns_body_text_via_shared_helper(self) -> None:
        """raw=True must return the frontmatter-stripped body text, byte-identical to the shared body_text helper's output."""
        created = create_rsk(_MINIMAL_BODY)

        result = get_rsk(created.id, raw=True)

        self.assertIsInstance(result, str)
        self.assertEqual(result, body_text(self._doc_path()))

    def test_raw_line_coordinates_index_into_the_splice_target(self) -> None:
        """The line numbers from a raw read must index byte-for-byte into the text the update splice targets (ACC-003)."""
        created = create_rsk(_MINIMAL_BODY)
        lines = get_rsk(created.id, raw=True).splitlines()
        k = lines.index("A root condition.") + 1
        replacement = "A revised root condition."

        update(id=created.id, type="rsk", content=replacement, offset=k, limit=1)

        new_lines = get_rsk(created.id, raw=True).splitlines()
        self.assertEqual(new_lines[k - 1], replacement)
        self.assertEqual(new_lines[: k - 1] + new_lines[k:], lines[: k - 1] + lines[k:])
        self.assertEqual(len(new_lines), len(lines))

    def test_raw_windowed_read_returns_the_requested_slice(self) -> None:
        """raw=True with offset/limit must return exactly the requested body window, each line
        keeping its trailing newline."""
        created = create_rsk(_MINIMAL_BODY)
        doc_id = created.id
        lines = get_rsk(doc_id, raw=True).splitlines()

        result = get_rsk(doc_id, raw=True, offset=2, limit=3)

        self.assertIsInstance(result, str)
        self.assertEqual(result, "\n".join(lines[1:4]) + "\n")

    def test_raw_windowed_read_clamps_out_of_range_coordinates(self) -> None:
        """raw=True: an offset past the last body line returns the empty string, and a limit
        larger than the remaining lines caps at them."""
        created = create_rsk(_MINIMAL_BODY)
        doc_id = created.id
        lines = get_rsk(doc_id, raw=True).splitlines()

        self.assertEqual(get_rsk(doc_id, raw=True, offset=len(lines) + 1), "")
        self.assertEqual(get_rsk(doc_id, raw=True, offset=len(lines) + 10, limit=5), "")
        self.assertEqual(get_rsk(doc_id, raw=True, offset=2, limit=len(lines) + 10), "\n".join(lines[1:]) + "\n")

    def test_coordinates_with_raw_false_raise_value_error(self) -> None:
        """offset/limit with raw=False must raise ValueError (naming raw), before any file access."""
        created = create_rsk(_MINIMAL_BODY)

        with self.assertRaises(ValueError) as ctx:
            get_rsk(created.id, raw=False, offset=2, limit=3)
        message = str(ctx.exception)
        self.assertIn("raw", message)
        self.assertIn("offset", message)
        with self.assertRaises(ValueError):
            get_rsk(created.id, raw=False, limit=3)

    def test_windowed_raw_read_coordinates_index_into_the_splice_target(self) -> None:
        """The coordinates of a windowed raw read must splice at exactly those lines, unchanged
        regions byte-identical (ACC-003 windowed)."""
        created = create_rsk(_MINIMAL_BODY)
        doc_id = created.id
        lines = get_rsk(doc_id, raw=True).splitlines()
        k, m = 3, 3
        window = get_rsk(doc_id, raw=True, offset=k, limit=m)
        self.assertEqual(window, "\n".join(lines[k - 1 : k - 1 + m]) + "\n")
        replacement = "## Cause\n\nA revised root condition."

        update(id=doc_id, type="rsk", content=replacement, offset=k, limit=m)

        new_lines = get_rsk(doc_id, raw=True).splitlines()
        self.assertEqual(new_lines[k - 1 : k - 1 + m], replacement.splitlines())
        self.assertEqual(new_lines[: k - 1] + new_lines[k - 1 + m :], lines[: k - 1] + lines[k - 1 + m :])
        self.assertEqual(len(new_lines), len(lines))

    def test_raw_false_returns_parsed_document_as_before(self) -> None:
        """raw=False (explicit) must return the parsed document, exactly as the default call does."""
        created = create_rsk(_MINIMAL_BODY)

        result = get_rsk(created.id, raw=False)
        default = get_rsk(created.id)

        self.assertIsInstance(result, RskDocument)
        self.assertEqual(result, default)

    def test_raw_unknown_id_raises_not_found_in_both_modes(self) -> None:
        """raw=True and raw=False must both raise RskNotFoundError for an unknown id, windowed raw
        reads included."""
        create_rsk(_MINIMAL_BODY)

        with self.assertRaises(RskNotFoundError):
            get_rsk(_MISSING_UUID, raw=True)
        with self.assertRaises(RskNotFoundError):
            get_rsk(_MISSING_UUID, raw=True, offset=2, limit=3)
        with self.assertRaises(RskNotFoundError):
            get_rsk(_MISSING_UUID, raw=False)

    def test_broken_document_returns_parse_failure_result(self) -> None:
        """get_rsk must return a ParseFailureResult (not raise) for an id whose on-disk file fails to parse."""
        created = create_rsk(_MINIMAL_BODY)
        self._doc_path().write_text("not a valid document, no headings at all\n", encoding="utf-8")

        result = get_rsk(created.id)

        self.assertIsInstance(result, ParseFailureResult)
        self.assertEqual(result.id, created.id)
        self.assertEqual(result.path, str(self._doc_path().resolve()))
        self.assertTrue(result.error)
        self.assertNotIsInstance(result, RskDocument)

    def test_broken_document_raw_true_returns_parse_failure_result_never_str(self) -> None:
        """raw=True on a broken document must return a ParseFailureResult, never a raw str."""
        created = create_rsk(_MINIMAL_BODY)
        self._doc_path().write_text("not a valid document, no headings at all\n", encoding="utf-8")

        result = get_rsk(created.id, raw=True)

        self.assertIsInstance(result, ParseFailureResult)
        self.assertNotIsInstance(result, str)

    def test_broken_document_error_matches_list_failed_row(self) -> None:
        """ParseFailureResult.error must equal list_rsk's failed-row error for the same broken file."""
        created = create_rsk(_MINIMAL_BODY)
        self._doc_path().write_text("not a valid document, no headings at all\n", encoding="utf-8")

        get_result = get_rsk(created.id)
        failed = [summary for summary in list_rsk().results if summary.title == "<failed to parse>"]

        self.assertIsInstance(get_result, ParseFailureResult)
        self.assertEqual(len(failed), 1)
        self.assertEqual(get_result.error, failed[0].error)

    def test_invalid_id_shape_raises_value_error(self) -> None:
        """An id that is not a well-formed canonical UUID must raise ValueError before any file access."""
        with self.assertRaises(ValueError):
            get_rsk("not-a-well-formed-uuid")


if __name__ == "__main__":
    unittest.main()
