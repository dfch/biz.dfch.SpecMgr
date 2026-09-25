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

"""Tests for the ``create_qa`` ``@mcp.tool()`` wrapper."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION
from biz.dfch.specmgr.qa.models.v2 import QaDocument, QaFrontmatter, parse_qa
from biz.dfch.specmgr.qa.tools._paths import qa_base_dir
from biz.dfch.specmgr.qa.tools.create_qa import create_qa
from biz.dfch.specmgr.qa.tools.get_qa import get_qa

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

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized QA sections.\n"

# A structurally valid v2 body whose single question lacks the bold
# `**<d>.<NNNN>**: ` number prefix (feat-156) -- `create_qa` must reject it
# with the validator's own `pydantic.ValidationError` and write no file.
_UNNUMBERED_QUESTION_BODY = textwrap.dedent(
    """\
    # Some QA Title

    ## General

    ### Introduction

    Some intro text.

    ### Raw Requirements

    Some raw requirements text.

    ## Elicitation Context

    ## Functional Suitability

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


class TempQaDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestCreateQa(TempQaDirTestCase):
    """Tests for the create_qa tool."""

    def test_builds_frontmatter_and_returns_document(self) -> None:
        """create_qa must build the entire frontmatter itself (id/type/status/timestamps/version)."""
        result = create_qa(_MINIMAL_BODY)

        self.assertIsInstance(result, QaFrontmatter)
        self.assertNotIsInstance(result, QaDocument)
        self.assertFalse(hasattr(result, "body"))
        self.assertIsNotNone(result.id)
        self.assertEqual(result.type, "qa")
        self.assertEqual(result.status, "draft")
        self.assertIsNotNone(result.created)
        self.assertEqual(result.created, result.updated)
        self.assertEqual(result.version, CURRENT_SCHEMA_VERSION)

        fetched = get_qa(result.id)
        self.assertEqual(fetched.body.text, "Some QA Title")

    def test_writes_expected_filename(self) -> None:
        """create_qa must write f'qa-{id}-{slug}.md' under the QA base dir."""
        result = create_qa(_MINIMAL_BODY)

        expected_path = qa_base_dir() / f"qa-{result.id}-some-qa-title.md"
        self.assertTrue(expected_path.exists())

    def test_written_file_round_trips_via_parse_qa(self) -> None:
        """The written file must parse back into an equivalent document."""
        result = create_qa(_MINIMAL_BODY)

        expected_path = qa_base_dir() / f"qa-{result.id}-some-qa-title.md"
        on_disk = parse_qa(expected_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.id)
        self.assertEqual(on_disk.frontmatter.status, "draft")
        self.assertEqual(on_disk.body.text, "Some QA Title")
        self.assertIsNone(on_disk.body.compatibility.questions)

    def test_creates_base_dir_if_missing(self) -> None:
        """create_qa must create the QA base directory if it does not exist yet."""
        self.assertFalse(qa_base_dir().exists())

        create_qa(_MINIMAL_BODY)

        self.assertTrue(qa_base_dir().is_dir())

    def test_invalid_content_raises_and_writes_nothing(self) -> None:
        """A structurally invalid body must raise AssertionError and write no file at all.

        The other error channel -- a field-level `pydantic.ValidationError` --
        is exercised by `test_invalid_question_prefix_raises_validation_error_and_writes_nothing`
        (a question lacking its own bold `**<d>.<NNNN>**: ` number prefix,
        feat-156), which gives `qa` the same caller-controllable field-level
        `pydantic.ValidationError` path `req.tools.create_req`'s closed-set
        fields (e.g. `## Level`) already had.
        """
        with self.assertRaises(AssertionError):
            create_qa(_MALFORMED_BODY)

        self.assertFalse(qa_base_dir().exists())

    def test_invalid_question_prefix_raises_validation_error_and_writes_nothing(self) -> None:
        """A structurally valid body whose question lacks the bold `**<d>.<NNNN>**: `
        number prefix (feat-156) must raise `pydantic.ValidationError` and write no
        file at all (feat-156 ACC-001).
        """
        with self.assertRaises(ValidationError) as ctx:
            create_qa(_UNNUMBERED_QUESTION_BODY)

        self.assertIn("question must start with the bold question-number prefix", str(ctx.exception))
        self.assertFalse(qa_base_dir().exists())


if __name__ == "__main__":
    unittest.main()
