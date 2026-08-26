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

"""Tests for :func:`parse_rsk`: the `RskDocument`-level `from_text` entry point.

Mirrors `tests/tsk/models/v1/test_parser.py`'s case shape. Two error channels:
structural problems (missing mandatory sections, wrong section order, an
assessment heading outside its regex `@alias` -- out-of-range or missing value
digit, a zero-entry `## Scope`) raise `AssertionError`; value problems
(a frontmatter `status` outside the closed six-value set, a `## Strategy` word
outside the TARA closed set) raise `pydantic.ValidationError`.
"""

from __future__ import annotations

import textwrap
import unittest
from pathlib import Path

import frontmatter
from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.rsk.models.v1 import LEVEL_HIGH, LEVEL_MEDIUM, RskDocument
from biz.dfch.specmgr.rsk.models.v1.parser import parse_rsk

_REFERENCE_PATH = (
    Path(__file__).resolve().parents[4] / ".specmgr" / "feat" / "feat-15-add-artifact-type-risk" / "rsk_reference.md"
)

_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: rsk-001
    type: rsk
    version: 1.0.0
    status: open
    created: 2026-08-24
    updated: 2026-08-24
    ---

    # Simple Risk

    ## Cause

    The parser library is unmaintained.

    ## Trigger

    An uploaded file exploits a known format flaw.

    ## Consequence

    Remote code execution in the document-processing subsystem.

    ## Scope

    - document-processing subsystem

    ## Initial Assessment

    ### Probability 4

    ### Impact 3

    ## Strategy

    reduce

    ## Mitigation

    Replace the parser with a maintained library.

    ## Residual Assessment

    ### Probability 2

    ### Impact 3
    """
)


class TestParseRsk(unittest.TestCase):
    """Tests for `parse_rsk`."""

    def test_parses_minimal_document(self) -> None:
        """A minimal, valid document parses into a RskDocument with the expected shape."""
        document = parse_rsk(_MINIMAL_DOC)

        self.assertIsInstance(document, RskDocument)
        self.assertEqual(document.frontmatter.id, "rsk-001")
        self.assertEqual(document.frontmatter.type, "rsk")
        self.assertEqual(document.frontmatter.status, "open")
        self.assertEqual(document.body.text, "Simple Risk")
        self.assertIsNone(document.body.comment)
        self.assertEqual(document.body.cause.text, "## Cause\n\nThe parser library is unmaintained.\n")
        self.assertEqual(document.body.trigger.text, "## Trigger\n\nAn uploaded file exploits a known format flaw.\n")
        self.assertEqual(
            document.body.consequence.text,
            "## Consequence\n\nRemote code execution in the document-processing subsystem.\n",
        )
        self.assertEqual([item.text for item in document.body.scope.items], ["document-processing subsystem"])
        self.assertEqual(document.body.initial_assessment.probability.value, 4)
        self.assertEqual(document.body.initial_assessment.impact.value, 3)
        self.assertEqual(document.body.initial_assessment.level, LEVEL_HIGH)
        self.assertEqual(document.body.strategy.value.text, "reduce")
        self.assertEqual(
            document.body.mitigation.text, "## Mitigation\n\nReplace the parser with a maintained library.\n"
        )
        self.assertEqual(document.body.residual_assessment.probability.value, 2)
        self.assertEqual(document.body.residual_assessment.impact.value, 3)
        self.assertEqual(document.body.residual_assessment.level, LEVEL_MEDIUM)
        self.assertIsNone(document.body.owner)
        self.assertIsNone(document.body.tags)
        self.assertIsNone(document.body.more_information)

    def test_parses_full_reference_document(self) -> None:
        """The feature's own reference document round-trips through parse_rsk."""
        text = _REFERENCE_PATH.read_text(encoding="utf-8")

        document = parse_rsk(text)

        self.assertEqual(document.frontmatter.id, "deadbeef-risk-risk-risk-deadbeefrisk")
        self.assertEqual(document.frontmatter.type, "rsk")
        self.assertEqual(document.frontmatter.status, "open")
        self.assertEqual(document.frontmatter.created, "2026-08-24")
        self.assertEqual(document.frontmatter.updated, "2026-08-24")
        self.assertEqual(document.frontmatter.version, "1.0.0")
        self.assertEqual(document.body.text, "Untrusted File Uploads Parsed by an Unmaintained Parser Library")
        self.assertIsNotNone(document.body.comment)
        self.assertEqual(
            [item.text for item in document.body.scope.items],
            ["document-processing subsystem"],
        )
        self.assertEqual(document.body.initial_assessment.probability.value, 4)
        self.assertEqual(document.body.initial_assessment.impact.value, 3)
        self.assertEqual(document.body.initial_assessment.level, LEVEL_HIGH)
        self.assertEqual(document.body.strategy.value.text, "reduce")
        self.assertEqual(document.body.residual_assessment.probability.value, 2)
        self.assertEqual(document.body.residual_assessment.impact.value, 3)
        self.assertEqual(document.body.residual_assessment.level, LEVEL_MEDIUM)
        self.assertEqual(document.body.owner.value.text, "Ronald Rink")
        self.assertEqual([item.text for item in document.body.tags.items], ["security", "upload pipeline"])
        self.assertIsNotNone(document.body.more_information)

        # Re-round-trip stability: the rendered body equals the formatted body text.
        self.assertEqual(str(document.body), format_text(frontmatter.loads(text).content))

    def test_defaults_frontmatter_when_absent(self) -> None:
        """Omitting the frontmatter block entirely still parses, applying RskFrontmatter's defaults."""
        text = "\n".join(_MINIMAL_DOC.splitlines()[8:]) + "\n"

        document = parse_rsk(text)

        self.assertIsNone(document.frontmatter.id)
        self.assertEqual(document.frontmatter.type, "rsk")
        self.assertEqual(document.frontmatter.status, "open")

    def test_invalid_status_raises_validation_error(self) -> None:
        """A frontmatter `status` outside RskFrontmatter's closed set fails validation.

        Covers the base default `draft` (valid for REQ/TSK, not part of the rsk
        six-value set) and an unknown word.
        """
        for status in ("draft", "not-a-real-status"):
            with self.subTest(status=status):
                text = _MINIMAL_DOC.replace("status: open", f"status: {status}")

                with self.assertRaises(ValidationError):
                    parse_rsk(text)

    def test_missing_mitigation_section_raises_assertion_error(self) -> None:
        """A missing mandatory `## Mitigation` section is a structural failure."""
        text = _MINIMAL_DOC.replace("## Mitigation\n\nReplace the parser with a maintained library.\n\n", "")

        with self.assertRaises(AssertionError):
            parse_rsk(text)

    def test_wrong_section_order_raises_assertion_error(self) -> None:
        """Assessment sections in the wrong order (residual before initial) is a structural failure."""
        text = textwrap.dedent(
            """\
            ---
            id: rsk-001
            type: rsk
            version: 1.0.0
            status: open
            created: 2026-08-24
            updated: 2026-08-24
            ---

            # Simple Risk

            ## Cause

            The parser library is unmaintained.

            ## Trigger

            An uploaded file exploits a known format flaw.

            ## Consequence

            Remote code execution in the document-processing subsystem.

            ## Scope

            - document-processing subsystem

            ## Residual Assessment

            ### Probability 2

            ### Impact 3

            ## Strategy

            reduce

            ## Mitigation

            Replace the parser with a maintained library.

            ## Initial Assessment

            ### Probability 4

            ### Impact 3
            """
        )

        with self.assertRaises(AssertionError):
            parse_rsk(text)

    def test_out_of_range_assessment_heading_value_raises_assertion_error(self) -> None:
        """An assessment heading value outside 1..5 (`### Probability 6`) fails the parse eagerly."""
        text = _MINIMAL_DOC.replace("### Probability 4", "### Probability 6", 1)

        with self.assertRaises(AssertionError):
            parse_rsk(text)

    def test_missing_assessment_heading_value_raises_assertion_error(self) -> None:
        """An assessment heading without its value digit (`### Probability`) fails the parse eagerly."""
        text = _MINIMAL_DOC.replace("### Probability 4\n", "### Probability\n", 1)

        with self.assertRaises(AssertionError):
            parse_rsk(text)

    def test_invalid_tara_word_raises_validation_error(self) -> None:
        """A `## Strategy` word outside the TARA closed set fails validation."""
        text = _MINIMAL_DOC.replace("## Strategy\n\nreduce\n", "## Strategy\n\ntolerate\n", 1)

        with self.assertRaises(ValidationError):
            parse_rsk(text)

    def test_missing_scope_entry_raises_assertion_error(self) -> None:
        """A `## Scope` heading present but with zero list entries is a structural failure."""
        text = _MINIMAL_DOC.replace("## Scope\n\n- document-processing subsystem\n\n", "## Scope\n\n", 1)

        with self.assertRaises(AssertionError):
            parse_rsk(text)


if __name__ == "__main__":
    unittest.main()
