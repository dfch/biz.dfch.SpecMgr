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
    created: '2026-08-24T00:00:00.000Z'
    updated: '2026-08-24T00:00:00.000Z'
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

    ## Source

    The QA interview on 2026-09-17 that elicited this risk.
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
        self.assertEqual(document.body.source.value.text, "The QA interview on 2026-09-17 that elicited this risk.")
        self.assertIsNone(document.body.more_information)

    def test_parses_full_reference_document(self) -> None:
        """The feature's own reference document round-trips through parse_rsk."""
        text = _REFERENCE_PATH.read_text(encoding="utf-8")

        document = parse_rsk(text)

        self.assertEqual(document.frontmatter.id, "deadbeef-risk-risk-risk-deadbeefrisk")
        self.assertEqual(document.frontmatter.type, "rsk")
        self.assertEqual(document.frontmatter.status, "open")
        # The on-disk reference document's frontmatter keeps the space separator
        # (a dev artifact outside this feature's sweep -- space remains accepted;
        # frontmatter values converge to `T` on the next write).
        self.assertEqual(document.frontmatter.created, "2026-08-24 00:00:00.000Z")
        self.assertEqual(document.frontmatter.updated, "2026-08-24 00:00:00.000Z")
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
        self.assertEqual(
            document.body.source.value.text,
            "QA interview 2026-09-17 -- risk elicitation for the document-processing upload pipeline (issue #15's worked example).",
        )
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

    def test_missing_source_section_raises_assertion_error(self) -> None:
        """A missing mandatory `## Source` section is a structural failure (feat-102-133-rsk-tags-source,
        GitHub issue #102) -- the raised message names the expected field and a 1-based line reference
        (feat-27-validation convention); the content is asserted, not just the exception type (ACC-002)."""
        text = _MINIMAL_DOC.replace("\n## Source\n\nThe QA interview on 2026-09-17 that elicited this risk.\n", "")

        with self.assertRaises(AssertionError) as ctx:
            parse_rsk(text)
        message = str(ctx.exception)
        self.assertIn("Risk > Source", message)
        self.assertIn("expected Source (heading 'Source')", message)
        self.assertIn("found no match", message)

    def test_source_before_tags_raises_assertion_error(self) -> None:
        """`## Source` placed ahead of `## Tags` is a structural failure (ACC-003): the tag list ends up
        left over with no declared field to consume it, and the message names the leftover section.
        `_MINIMAL_DOC`'s `## Source` already sits at the body's end, so appending `## Tags` after it
        puts Source ahead of Tags."""
        text = _MINIMAL_DOC + "\n## Tags\n\n- security\n"

        with self.assertRaises(AssertionError) as ctx:
            parse_rsk(text)
        message = str(ctx.exception)
        self.assertIn("text left over after processing all fields", message)
        self.assertIn("## Tags", message)

    def test_source_after_more_information_raises_assertion_error(self) -> None:
        """`## Source` placed behind `## More Information` is a structural failure (ACC-003): the mandatory
        `## Source` field finds its heading only behind foreign text, and the message names both the
        expected field and the section it actually found first."""
        text = _MINIMAL_DOC.replace(
            "## Source\n", "## More Information\n\nFree-form supplementary text.\n\n## Source\n", 1
        )

        with self.assertRaises(AssertionError) as ctx:
            parse_rsk(text)
        message = str(ctx.exception)
        self.assertIn("Risk > Source", message)
        self.assertIn("expected Source (heading 'Source')", message)
        self.assertIn("found no match", message)
        self.assertIn("## More Information", message)

    def test_wrong_section_order_raises_assertion_error(self) -> None:
        """Assessment sections in the wrong order (residual before initial) is a structural failure."""
        text = textwrap.dedent(
            """\
            ---
            id: rsk-001
            type: rsk
            version: 1.0.0
            status: open
            created: '2026-08-24T00:00:00.000Z'
            updated: '2026-08-24T00:00:00.000Z'
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


class TestUnquotedTimestampNormalization(unittest.TestCase):
    """The `_stringify_metadata` datetime-coercion branch (feat-146 REQ-006/REQ-003).

    An unquoted frontmatter `created`/`updated` timestamp is coerced by PyYAML to a
    `datetime` before this domain's own `_stringify_metadata` runs -- such a value
    must parse and converge to the `T`-canonical form, and an unquoted date-only
    value must still be rejected by the frontmatter's own date+time pattern.
    """

    def test_unquoted_timestamps_converge_to_t_canonical_form(self) -> None:
        """Unquoted `T`- and space-separated timestamps parse and converge to the `T`-canonical
        form; an unquoted date-only value still fails the frontmatter pattern."""
        text = _MINIMAL_DOC.replace("created: '2026-08-24T00:00:00.000Z'", "created: 2026-08-24T00:00:00.000Z").replace(
            "updated: '2026-08-24T00:00:00.000Z'", "updated: 2026-08-24 00:00:00.000Z"
        )
        document = parse_rsk(text)
        self.assertEqual(document.frontmatter.created, "2026-08-24T00:00:00.000Z")
        self.assertEqual(document.frontmatter.updated, "2026-08-24T00:00:00.000Z")

        with self.assertRaises(ValidationError):
            parse_rsk(text.replace("created: 2026-08-24T00:00:00.000Z", "created: 2026-08-24"))


if __name__ == "__main__":
    unittest.main()
