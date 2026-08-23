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

"""Tests for ``qa.tools._io`` (thin file read helpers)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from biz.dfch.specmgr.qa.models.v2 import QaDocument
from biz.dfch.specmgr.qa.tools._io import load_by_id, read_qa
from biz.dfch.specmgr.qa.tools._paths import QaNotFoundError

_DOC_TEMPLATE = textwrap.dedent(
    """\
    ---
    id: {id}
    type: qa
    version: 1.0.0
    status: draft
    created: 2026-08-18
    updated: 2026-08-18
    ---

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

_V1_SHAPED_DOC_TEMPLATE = textwrap.dedent(
    """\
    ---
    id: {id}
    type: qa
    version: 1.0.0
    status: draft
    created: 2026-08-18
    updated: 2026-08-18
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


def _qa_text(id_: str) -> str:
    """Render a minimal, valid QA document's text for the given id."""
    return _DOC_TEMPLATE.format(id=id_)


def _v1_shaped_qa_text(id_: str) -> str:
    """Render a v1-shaped (per-question `### {heading}`, no Elicitation Context)
    document's text for the given id -- no longer parseable by `qa.models.v2`.
    """
    return _V1_SHAPED_DOC_TEMPLATE.format(id=id_)


class TestReadQa(unittest.TestCase):
    """Tests for read_qa."""

    def test_reads_and_parses_a_real_file(self):
        """read_qa must return a QaDocument matching the file's own content."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text(_qa_text("some-id"), encoding="utf-8")

            document = read_qa(path)

            self.assertIsInstance(document, QaDocument)
            self.assertEqual(document.frontmatter.id, "some-id")
            self.assertEqual(document.body.text, "Some QA Title")

    def test_raises_structural_error_for_v1_shaped_document(self) -> None:
        """`read_qa` -- the read path `get_qa` calls internally once `load_by_id`
        has resolved an id to a path -- must fail with the same structural
        `AssertionError` that `Qa.from_text` raises on its own for a
        v1-shaped document (per-question `### {heading}` sub-sections, no
        `## Elicitation Context`); no version gate, no silent fallback to v1
        parsing (ACC-005, REQ-004 revised 2026-08-23).
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text(_v1_shaped_qa_text("some-id"), encoding="utf-8")

            with self.assertRaises(AssertionError):
                read_qa(path)


class TestLoadById(unittest.TestCase):
    """Tests for load_by_id."""

    def test_returns_path_and_parsed_qa(self):
        """load_by_id must return both the resolved path and the parsed document."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            expected_path = base / "doc.md"
            expected_path.write_text(_qa_text("the-id"), encoding="utf-8")

            path, document = load_by_id(base, "the-id")

            self.assertEqual(path, expected_path)
            self.assertEqual(document.frontmatter.id, "the-id")

    def test_raises_not_found_for_unknown_id(self):
        """load_by_id must raise QaNotFoundError for an id with no matching file."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with self.assertRaises(QaNotFoundError):
                load_by_id(base, "does-not-exist")


if __name__ == "__main__":
    unittest.main()
