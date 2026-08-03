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

"""Tests for :func:`render_adr` (plan §7/§10 item 2, the render half of the
parse -> validate -> render pipeline).
"""

import unittest
from pathlib import Path

from biz.dfch.specmgr.models.adr.v1 import Adr, AdrBody, AdrFrontmatter, AdrOption
from biz.dfch.specmgr.models.adr.v1.parser import parse_adr
from biz.dfch.specmgr.models.adr.v1.renderer import render_adr

_EXAMPLES_DIR = Path(__file__).parent / "examples"


def _read(name: str) -> str:
    return (_EXAMPLES_DIR / name).read_text(encoding="utf-8")


def _full_adr() -> Adr:
    return Adr(
        frontmatter=AdrFrontmatter(
            status="accepted",
            date="2024-01-15",
            decision_makers="Alice, Bob",
            consulted="Carol",
            informed="Dave",
        ),
        body=AdrBody(
            title="Use Postgres for the primary datastore",
            context_and_problem_statement="We need a datastore for the new service.",
            decision_drivers="* Must support transactions\n* Team familiarity",
            considered_options="* Postgres\n* MongoDB",
            decision_outcome="Chosen option: Postgres, because it best satisfies the drivers above.",
            consequences="* Good, because ACID transactions\n* Bad, because more ops overhead",
            confirmation="Reviewed and confirmed by the architecture board.",
            options=[
                AdrOption(number=1, partial_title="Postgres", content="* Good, because mature"),
                AdrOption(number=2, partial_title="MongoDB", content="* Good, because flexible schema"),
            ],
            more_information="See the team wiki for background.",
        ),
    )


class TestRenderAdrGoldenFile(unittest.TestCase):
    """Locks down the exact bytes :func:`render_adr` produces for a fully-populated ADR."""

    def test_full_adr_renders_exact_canonical_markdown(self):
        """A fully-populated Adr must render to this exact, byte-for-byte string."""
        expected = _read("adr-full-golden.md")
        self.assertEqual(render_adr(_full_adr()), expected)


class TestRenderAdrOptionalSectionOmission(unittest.TestCase):
    """Every optional section must be entirely absent (heading and all) when unset."""

    def _minimal_adr(self) -> Adr:
        return Adr(
            frontmatter=AdrFrontmatter(),
            body=AdrBody(
                title="A title",
                context_and_problem_statement="Context.",
                considered_options="Options.",
                decision_outcome="Outcome.",
            ),
        )

    def test_decision_drivers_omitted_when_none(self):
        """'## Decision Drivers' must not appear when the field is unset."""
        self.assertNotIn("Decision Drivers", render_adr(self._minimal_adr()))

    def test_consequences_omitted_when_none(self):
        """'### Consequences' must not appear when the field is unset."""
        self.assertNotIn("Consequences", render_adr(self._minimal_adr()))

    def test_confirmation_omitted_when_none(self):
        """'### Confirmation' must not appear when the field is unset."""
        self.assertNotIn("Confirmation", render_adr(self._minimal_adr()))

    def test_more_information_omitted_when_none(self):
        """'## More Information' must not appear when the field is unset."""
        self.assertNotIn("More Information", render_adr(self._minimal_adr()))

    def test_pros_and_cons_heading_omitted_when_no_options(self):
        """The derived '## Pros and Cons of the Options' container must be fully omitted
        when there are zero options."""
        self.assertNotIn("Pros and Cons", render_adr(self._minimal_adr()))

    def test_pros_and_cons_heading_present_when_at_least_one_option(self):
        """The derived container must appear, with its option sub-heading, once >=1 option exists."""
        adr = self._minimal_adr()
        adr.body.options.append(AdrOption(number=1, partial_title="Solo option", content="Some content."))
        rendered = render_adr(adr)
        self.assertIn("## Pros and Cons of the Options", rendered)
        self.assertIn("### Option 1: Solo option", rendered)

    def test_option_numbering_gap_is_preserved_verbatim(self):
        """Rendering must not renumber/reorder options -- a gap (e.g. missing 2) stays a gap."""
        adr = self._minimal_adr()
        adr.body.options = [
            AdrOption(number=1, partial_title="First", content="First content."),
            AdrOption(number=3, partial_title="Third", content="Third content."),
        ]
        rendered = render_adr(adr)
        self.assertIn("### Option 1: First", rendered)
        self.assertIn("### Option 3: Third", rendered)
        self.assertNotIn("Option 2", rendered)

    def test_frontmatter_omits_none_fields(self):
        """Unset optional frontmatter keys must not appear in the YAML block at all."""
        rendered = render_adr(self._minimal_adr())
        frontmatter_block = rendered.split("---")[1]
        for key in ("date", "decision-makers", "consulted", "informed", "id"):
            self.assertNotIn(key, frontmatter_block)

    def test_id_rendered_immediately_before_version_when_set(self):
        """id, when set, must be emitted right before version, both after the MADR keys."""
        adr = self._minimal_adr()
        adr.frontmatter.id = "11111111-1111-1111-1111-111111111111"
        rendered = render_adr(adr)
        frontmatter_block = rendered.split("---")[1]
        id_index = frontmatter_block.index("id:")
        version_index = frontmatter_block.index("version:")
        self.assertLess(id_index, version_index)
        self.assertIn("id: 11111111-1111-1111-1111-111111111111", frontmatter_block)

    def test_option_with_empty_content_renders_heading_only(self):
        """An option with empty content must render as a bare heading, no stray blank block."""
        adr = self._minimal_adr()
        adr.body.options.append(AdrOption(number=1, partial_title="Empty", content=""))
        rendered = render_adr(adr)
        self.assertIn("### Option 1: Empty", rendered)
        # No stray blank content block between the option heading and whatever follows it.
        self.assertNotIn("### Option 1: Empty\n\n\n", rendered)


class TestRenderAdrRoundTrip(unittest.TestCase):
    """render(parse(text)) must be a semantic (and, on a second pass, byte-exact) fixed point."""

    def test_render_parse_round_trip_preserves_full_adr(self):
        """Rendering a fully-populated Adr and re-parsing it must reproduce the same model."""
        adr = _full_adr()
        reparsed = parse_adr(render_adr(adr))
        self.assertEqual(reparsed, adr)

    def test_rendering_twice_is_idempotent(self):
        """Canonical form is a fixed point: re-parsing and re-rendering must not change a byte."""
        once = render_adr(_full_adr())
        twice = render_adr(parse_adr(once))
        self.assertEqual(once, twice)

    def test_drift_check_against_full_madr_example_fixture(self):
        """render(parse(file)) must reproduce the same structured document for a real fixture
        (plan §10 item 4) -- not byte-identical to the original file (which carries a
        human-authored comment the schema doesn't model), but a stable, idempotent fixed
        point once passed through the pipeline once.
        """
        original = parse_adr(_read("adr-template-valid.md"))
        rendered_once = render_adr(original)
        reparsed = parse_adr(rendered_once)
        self.assertEqual(reparsed, original)
        rendered_twice = render_adr(reparsed)
        self.assertEqual(rendered_once, rendered_twice)

    def test_drift_check_against_minimal_madr_example_fixture(self):
        """Same drift check as above, against the minimal (fewer optional sections,
        zero options) fixture."""
        original = parse_adr(_read("adr-template-minimal-valid.md"))
        rendered_once = render_adr(original)
        reparsed = parse_adr(rendered_once)
        self.assertEqual(reparsed, original)
        rendered_twice = render_adr(reparsed)
        self.assertEqual(rendered_once, rendered_twice)


if __name__ == "__main__":
    unittest.main()
