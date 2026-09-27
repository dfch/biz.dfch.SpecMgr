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

"""Tests for the ``get_qa`` ``@mcp.tool()`` wrapper."""

from __future__ import annotations

import re
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.general.tools.update import update
from biz.dfch.specmgr.qa.models.v2 import QaDocument
from biz.dfch.specmgr.qa.tools import _io
from biz.dfch.specmgr.qa.tools._paths import QaNotFoundError
from biz.dfch.specmgr.qa.tools.create_qa import create_qa
from biz.dfch.specmgr.qa.tools.get_qa import get_qa
from biz.dfch.specmgr.qa.tools.list_qa import list_qa
from biz.dfch.specmgr.general.models import ParseFailureResult


#: A well-formed but non-existent canonical UUID (feat-38-39-41-43-44 Phase 4: the id
#: must be well-formed to reach the domain's own not-found error past the new
#: ``validate_id`` guard).
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"
_MINIMAL_BODY = textwrap.dedent(
    """\
    # Some QA Title

    ## General

    ### Introduction

    Some intro text.

    ### Raw Requirements

    Some raw requirements text.

    ## Elicitation Context

    ## Functional Suitability

    ## Performance Efficiency

    ## Compatibility

    ## Interaction Capability

    ## Reliability

    ## Security

    ## Maintainability

    ## Flexibility

    ## Safety
    """
)

_V1_SHAPED_DOC = textwrap.dedent(
    """\
    ---
    id: v1-shaped-id
    type: qa
    status: draft
    ---

    # Some QA Title

    ## General

    ### Introduction

    Some intro text.

    ### Raw Requirements

    Some raw requirements text.

    ## Functional Suitability

    ### What must happen?

    > Is this acceptable?

    Yes, it is acceptable.

    ## Performance Efficiency

    ## Compatibility

    ## Interaction Capability

    ## Reliability

    ## Security

    ## Maintainability

    ## Flexibility

    ## Safety
    """
)


def _strip_pydantic_footer(text: str) -> str:
    """Strip the optional trailing pydantic documentation line from a parse-error text.

    The ``DocCache``'s exception reconstruction drops pydantic's "For further
    information visit https://errors.pydantic.dev/..." line on warm re-raises,
    so the ``get_qa``/``list_qa`` error-text identity is asserted modulo that
    line (Option B, 2026-09-26; the str-faithful reconstruction is tracked as
    follow-up issue #162).
    """
    result = re.sub(r"[ \t]*For further information visit https://errors\.pydantic\.dev/.*$", "", text, flags=re.S)
    return result


class TestGetQa(unittest.TestCase):
    """Tests for the get_qa tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_matching_document(self) -> None:
        """get_qa must return the full QaDocument for a matching id."""
        created = create_qa(_MINIMAL_BODY)

        result = get_qa(created.id)

        self.assertIsInstance(result, QaDocument)
        self.assertEqual(result.frontmatter.id, created.id)
        self.assertEqual(result.body.text, "Some QA Title")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """get_qa must raise QaNotFoundError, with the standardized message, when no document matches."""
        create_qa(_MINIMAL_BODY)

        with self.assertRaises(QaNotFoundError) as ctx:
            get_qa(_MISSING_UUID)
        message = str(ctx.exception)
        self.assertIn("bare document UUID", message)
        self.assertIn("without a domain prefix", message)

    def _doc_path(self) -> Path:
        """The single on-disk document file seeded for this test."""
        matches = list((self.docs_root / "qa").glob("*.md"))
        self.assertEqual(len(matches), 1)
        result = matches[0]
        return result

    def test_raw_returns_body_text_via_shared_helper(self) -> None:
        """raw=True must return the frontmatter-stripped body text, byte-identical to the shared body_text helper's output."""
        created = create_qa(_MINIMAL_BODY)

        result = get_qa(created.id, raw=True)

        self.assertIsInstance(result, str)
        self.assertEqual(result, body_text(self._doc_path()))

    def test_raw_line_coordinates_index_into_the_splice_target(self) -> None:
        """The line numbers from a raw read must index byte-for-byte into the text the update splice targets (ACC-003)."""
        created = create_qa(_MINIMAL_BODY)
        lines = get_qa(created.id, raw=True).splitlines()
        k = lines.index("Some intro text.") + 1
        replacement = "Updated intro text."

        update(id=created.id, type="qa", content=replacement, offset=k, limit=1)

        new_lines = get_qa(created.id, raw=True).splitlines()
        self.assertEqual(new_lines[k - 1], replacement)
        self.assertEqual(new_lines[: k - 1] + new_lines[k:], lines[: k - 1] + lines[k:])
        self.assertEqual(len(new_lines), len(lines))

    def test_raw_windowed_read_returns_the_requested_slice(self) -> None:
        """raw=True with offset/limit must return exactly the requested body window, each line
        keeping its trailing newline."""
        created = create_qa(_MINIMAL_BODY)
        doc_id = created.id
        lines = get_qa(doc_id, raw=True).splitlines()

        result = get_qa(doc_id, raw=True, offset=2, limit=3)

        self.assertIsInstance(result, str)
        self.assertEqual(result, "\n".join(lines[1:4]) + "\n")

    def test_raw_windowed_read_clamps_out_of_range_coordinates(self) -> None:
        """raw=True: an offset past the last body line returns the empty string, and a limit
        larger than the remaining lines caps at them."""
        created = create_qa(_MINIMAL_BODY)
        doc_id = created.id
        lines = get_qa(doc_id, raw=True).splitlines()

        self.assertEqual(get_qa(doc_id, raw=True, offset=len(lines) + 1), "")
        self.assertEqual(get_qa(doc_id, raw=True, offset=len(lines) + 10, limit=5), "")
        self.assertEqual(get_qa(doc_id, raw=True, offset=2, limit=len(lines) + 10), "\n".join(lines[1:]) + "\n")

    def test_coordinates_with_raw_false_raise_value_error(self) -> None:
        """offset/limit with raw=False must raise ValueError (naming raw), before any file access."""
        created = create_qa(_MINIMAL_BODY)

        with self.assertRaises(ValueError) as ctx:
            get_qa(created.id, raw=False, offset=2, limit=3)
        message = str(ctx.exception)
        self.assertIn("raw", message)
        self.assertIn("offset", message)
        with self.assertRaises(ValueError):
            get_qa(created.id, raw=False, limit=3)

    def test_windowed_raw_read_coordinates_index_into_the_splice_target(self) -> None:
        """The coordinates of a windowed raw read must splice at exactly those lines, unchanged
        regions byte-identical (ACC-003 windowed)."""
        created = create_qa(_MINIMAL_BODY)
        doc_id = created.id
        lines = get_qa(doc_id, raw=True).splitlines()
        k, m = 5, 3
        window = get_qa(doc_id, raw=True, offset=k, limit=m)
        self.assertEqual(window, "\n".join(lines[k - 1 : k - 1 + m]) + "\n")
        replacement = "### Introduction\n\nUpdated intro text."

        update(id=doc_id, type="qa", content=replacement, offset=k, limit=m)

        new_lines = get_qa(doc_id, raw=True).splitlines()
        self.assertEqual(new_lines[k - 1 : k - 1 + m], replacement.splitlines())
        self.assertEqual(new_lines[: k - 1] + new_lines[k - 1 + m :], lines[: k - 1] + lines[k - 1 + m :])
        self.assertEqual(len(new_lines), len(lines))

    def test_raw_false_returns_parsed_document_as_before(self) -> None:
        """raw=False (explicit) must return the parsed document, exactly as the default call does."""
        created = create_qa(_MINIMAL_BODY)

        result = get_qa(created.id, raw=False)
        default = get_qa(created.id)

        self.assertIsInstance(result, QaDocument)
        self.assertEqual(result, default)

    def test_raw_unknown_id_raises_not_found_in_both_modes(self) -> None:
        """raw=True and raw=False must both raise QaNotFoundError for an unknown id, windowed raw
        reads included."""
        create_qa(_MINIMAL_BODY)

        with self.assertRaises(QaNotFoundError):
            get_qa(_MISSING_UUID, raw=True)
        with self.assertRaises(QaNotFoundError):
            get_qa(_MISSING_UUID, raw=True, offset=2, limit=3)
        with self.assertRaises(QaNotFoundError):
            get_qa(_MISSING_UUID, raw=False)

    def test_read_path_surfaces_structural_error_for_v1_shaped_document(self) -> None:
        """`get_qa`'s own read path (`qa.tools._io.read_qa`, which `load_by_id`
        calls once an id has been resolved to a path) must fail with the same
        structural `AssertionError`/`pydantic.ValidationError` that
        `qa.models.v2.parser.parse_qa`/`Qa.from_text` raise on their own for a
        v1-shaped document -- no version gate, no silent fallback to v1
        parsing (ACC-005, REQ-004 revised 2026-08-23).

        Exercised directly against `_io.read_qa(path)` rather than
        `get_qa(id)` itself: `get_qa` resolves an id to a path by scanning and
        parsing every file under the QA base directory
        (`qa.tools._paths.find_qa_path`), silently skipping any file that
        fails to parse -- a pre-existing, unrelated-to-this-cutover behavior
        (see `test__paths.py`'s own `test_skips_malformed_file_and_still_finds_valid_one`).
        A v1-shaped file therefore can never be *found* by id in the first
        place, so calling `get_qa` with its id surfaces `QaNotFoundError`, not
        the structural parse error -- `read_qa` is the smallest unit that
        demonstrates the actual "no v1 fallback" guarantee.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_V1_SHAPED_DOC, encoding="utf-8")

            with self.assertRaises(AssertionError):
                _io.read_qa(path)

    def test_broken_document_returns_parse_failure_result(self) -> None:
        """get_qa must return a ParseFailureResult (not raise) for an id whose on-disk file fails to parse."""
        created = create_qa(_MINIMAL_BODY)
        self._doc_path().write_text("not a valid document, no headings at all\n", encoding="utf-8")

        result = get_qa(created.id)

        self.assertIsInstance(result, ParseFailureResult)
        self.assertEqual(result.id, created.id)
        self.assertEqual(result.path, str(self._doc_path().resolve()))
        self.assertTrue(result.error)
        self.assertNotIsInstance(result, QaDocument)

    def test_broken_document_raw_true_returns_parse_failure_result_never_str(self) -> None:
        """raw=True on a broken document must return a ParseFailureResult, never a raw str."""
        created = create_qa(_MINIMAL_BODY)
        self._doc_path().write_text("not a valid document, no headings at all\n", encoding="utf-8")

        result = get_qa(created.id, raw=True)

        self.assertIsInstance(result, ParseFailureResult)
        self.assertNotIsInstance(result, str)

    def test_broken_document_error_matches_list_failed_row(self) -> None:
        """ParseFailureResult.error must carry the same parse defect as list_qa's failed-row error for the same
        broken file (identical field path and cause; the trailing pydantic documentation line is modulo)."""
        created = create_qa(_MINIMAL_BODY)
        self._doc_path().write_text("not a valid document, no headings at all\n", encoding="utf-8")

        get_result = get_qa(created.id)
        failed = [summary for summary in list_qa().results if summary.title == "<failed to parse>"]

        self.assertIsInstance(get_result, ParseFailureResult)
        self.assertEqual(len(failed), 1)
        # Option B (2026-09-26): identity is modulo the trailing pydantic line; restore plain equality with issue #162.
        self.assertEqual(_strip_pydantic_footer(get_result.error), _strip_pydantic_footer(failed[0].error))
        # The core defect content (this fixture's structural parse failure) must be present in both texts.
        self.assertIn("Token[0]: expected 'heading_open', got 'paragraph_open'.", get_result.error)
        self.assertIn("Token[0]: expected 'heading_open', got 'paragraph_open'.", failed[0].error)

    def test_invalid_id_shape_raises_value_error(self) -> None:
        """An id that is not a well-formed canonical UUID must raise ValueError before any file access."""
        with self.assertRaises(ValueError):
            get_qa("not-a-well-formed-uuid")


if __name__ == "__main__":
    unittest.main()
