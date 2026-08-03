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

"""Tests for :func:`parse_adr` against the four official MADR 4.0.0 templates.

Fixtures live in ``examples/`` (verbatim copies, see that directory's own
``README.md`` for provenance/license). These are *unfilled placeholder*
templates, not real ADRs -- plan §2's source document, not hand-written
test data -- so most of them are expected to fail parsing/validation
exactly because a mandatory section (or ``status``) still holds template
placeholder text instead of real content. Each test documents which error
channel (see ``parser.py``'s module docstring) fires and why, so a future
change to either the templates (a new MADR release) or the schema has a
concrete regression signal.
"""

import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.models.adr.v1.parser import AdrParseError, parse_adr

_EXAMPLES_DIR = Path(__file__).parent / "examples"


def _read(name: str) -> str:
    return (_EXAMPLES_DIR / name).read_text(encoding="utf-8")


class TestMadrExampleTemplates(unittest.TestCase):
    """One test per official MADR 4.0.0 template, documenting its parse outcome."""

    def test_bare_minimal_template_fails_validation_on_blank_mandatory_sections(self):
        """adr-template-bare-minimal.md has no frontmatter and leaves every mandatory
        whole-section field (context/considered-options/decision-outcome) completely
        blank -- a structurally well-formed but semantically empty document, so this
        must surface as a pydantic.ValidationError, not an AdrParseError."""
        text = _read("adr-template-bare-minimal.md")
        with self.assertRaises(ValidationError) as ctx:
            parse_adr(text)
        error_fields = {error["loc"][0] for error in ctx.exception.errors()}
        self.assertEqual(error_fields, {"context_and_problem_statement", "considered_options", "decision_outcome"})

    def test_bare_template_fails_parsing_on_unfilled_option_heading(self):
        """adr-template-bare.md's frontmatter is all-blank keys (now defaulted per
        AdrFrontmatter.status's blank-handling), so parsing gets as far as the body --
        but its '### <!-- title of option --> ' heading is unfilled placeholder text
        that matches neither 'Consequences'/'Confirmation' nor 'Option N: ...', which
        is a structural problem (AdrParseError), not a field-value problem."""
        text = _read("adr-template-bare.md")
        with self.assertRaises(AdrParseError) as ctx:
            parse_adr(text)
        self.assertIn("title of option", str(ctx.exception))

    def test_minimal_template_parses_successfully(self):
        """adr-template-minimal.md has no frontmatter block and every mandatory
        section filled with placeholder (but non-blank) text -- this is the one
        template that is structurally and semantically valid as-is."""
        adr = parse_adr(_read("adr-template-minimal.md"))
        self.assertEqual(adr.frontmatter.status, "draft")
        self.assertIn("short title", adr.body.title)
        self.assertIn("Describe the context", adr.body.context_and_problem_statement)
        self.assertIn("title of option 1", adr.body.considered_options)
        self.assertIn("Chosen option", adr.body.decision_outcome)
        self.assertIsNotNone(adr.body.consequences)
        self.assertIn("Good, because", adr.body.consequences or "")
        self.assertIsNone(adr.body.decision_drivers)
        self.assertIsNone(adr.body.confirmation)
        self.assertIsNone(adr.body.more_information)
        self.assertEqual(adr.body.options, [])

    def test_full_template_fails_validation_on_unfilled_status(self):
        """adr-template.md's frontmatter 'status' value is still the unfilled
        placeholder text listing every allowed value, e.g.
        '{proposed | rejected | ... }' -- a field-value problem
        (pydantic.ValidationError), even though its body also has unrecognized
        '### {title of option N}' headings that would independently raise
        AdrParseError; frontmatter is validated first."""
        text = _read("adr-template.md")
        with self.assertRaises(ValidationError) as ctx:
            parse_adr(text)
        error_fields = {error["loc"][0] for error in ctx.exception.errors()}
        self.assertEqual(error_fields, {"status"})

    def test_full_template_ok(self):
        text = _read("adr-template-valid.md")
        result = parse_adr(text)

        fm = result.frontmatter
        self.assertEqual(fm.status, "draft")
        self.assertEqual(fm.date, "1927-03-27")
        self.assertEqual(fm.version, "1.0.0")
        self.assertEqual(fm.consulted, "cons-1, cons-2")
        self.assertEqual(fm.informed, "informed-1, informed-2")
        self.assertEqual(fm.decision_makers, "dec-1, dec-2")

        md = result.body
        self.assertEqual(md.title, "Arbitrary short title")
        self.assertEqual(md.context_and_problem_statement, "This is the problem statement.")
        self.assertEqual(
            md.decision_drivers,
            """* Driver 1
* Driver 2""",
        )
        self.assertEqual(
            md.considered_options,
            """* Considered Option 1
* Considered Option 2""",
        )
        self.assertEqual(md.decision_outcome, "This is the decision outcome.")
        self.assertEqual(md.consequences, "All the consequences.")
        self.assertEqual(md.confirmation, "This is the confirmation.")
        self.assertEqual(len(md.options), 2)

        o1 = md.options[0]
        self.assertEqual(o1.full_title, "Option 1: {title of option 1}")
        self.assertEqual(o1.number, 1)
        self.assertEqual(o1.content, "This is Option 1.")

        o2 = md.options[1]
        self.assertEqual(o2.full_title, "Option 3: {title of other option}")
        self.assertEqual(o2.number, 3)
        self.assertEqual(o2.content, "This is Option 3. There is no Option 2.")

        self.assertEqual(md.more_information, "And here is some more information.")


if __name__ == "__main__":
    unittest.main()
