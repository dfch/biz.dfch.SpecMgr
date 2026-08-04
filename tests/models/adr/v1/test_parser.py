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

"""Tests for :func:`parse_adr` (plan §7/§10 item 2)."""

import textwrap
import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models.adr.v1 import CURRENT_SCHEMA_VERSION
from biz.dfch.specmgr.models.adr.v1.parser import AdrParseError, parse_adr

_FULL_ADR = textwrap.dedent(
    """\
    ---
    status: accepted
    date: 2024-01-15
    decision-makers: Alice, Bob
    consulted: Carol
    informed: Dave
    ---
    # Use Postgres for the primary datastore

    ## Context and Problem Statement

    We need a datastore for the new service.

    Second paragraph of context.

    ## Decision Drivers

    * Must support transactions
    * Team familiarity

    ## Considered Options

    * Postgres
    * MongoDB

    ## Decision Outcome

    Chosen option: Postgres, because it best satisfies the drivers above.

    ### Consequences

    * Good, because ACID transactions
    * Bad, because more ops overhead

    ### Confirmation

    Reviewed and confirmed by the architecture board.

    ## Pros and Cons of the Options

    <!-- This is an optional element. -->

    ### Option 1: Postgres

    * Good, because mature
    * Bad, because another service to run

    ### Option 2: MongoDB

    * Good, because flexible schema

    ## More Information

    See the team wiki for background.
    """
)


class TestParseAdr(unittest.TestCase):
    """End-to-end tests for :func:`parse_adr` against a full MADR-shaped document."""

    def test_parses_frontmatter(self):
        """Every frontmatter key must round-trip into the right AdrFrontmatter field."""
        adr = parse_adr(_FULL_ADR)
        self.assertEqual(adr.frontmatter.status, "accepted")
        self.assertEqual(adr.frontmatter.date, "2024-01-15")
        self.assertEqual(adr.frontmatter.decision_makers, "Alice, Bob")
        self.assertEqual(adr.frontmatter.consulted, "Carol")
        self.assertEqual(adr.frontmatter.informed, "Dave")

    def test_frontmatter_version_defaults_when_absent(self):
        """A document with no explicit 'version' key must get the current schema version."""
        adr = parse_adr(_FULL_ADR)
        self.assertEqual(adr.frontmatter.version, CURRENT_SCHEMA_VERSION)

    def test_parses_mandatory_body_fields(self):
        """The four mandatory whole-section fields must be extracted verbatim."""
        adr = parse_adr(_FULL_ADR)
        self.assertEqual(adr.body.title, "Use Postgres for the primary datastore")
        self.assertIn("We need a datastore", adr.body.context_and_problem_statement)
        self.assertIn("Second paragraph of context", adr.body.context_and_problem_statement)
        self.assertIn("Postgres", adr.body.considered_options)
        self.assertIn("MongoDB", adr.body.considered_options)
        self.assertTrue(adr.body.decision_outcome.startswith("Chosen option: Postgres"))

    def test_parses_optional_body_fields(self):
        """Optional whole-section fields must be extracted when present."""
        adr = parse_adr(_FULL_ADR)
        self.assertIn("Must support transactions", adr.body.decision_drivers)
        self.assertIn("ACID transactions", adr.body.consequences)
        self.assertEqual(adr.body.confirmation, "Reviewed and confirmed by the architecture board.")
        self.assertEqual(adr.body.more_information, "See the team wiki for background.")

    def test_pros_and_cons_heading_itself_is_not_stored(self):
        """The derived 'Pros and Cons of the Options' heading text/placeholder must be discarded."""
        adr = parse_adr(_FULL_ADR)
        for value in (
            adr.body.title,
            adr.body.context_and_problem_statement,
            adr.body.decision_drivers,
            adr.body.considered_options,
            adr.body.decision_outcome,
            adr.body.consequences,
            adr.body.confirmation,
            adr.body.more_information,
        ):
            self.assertNotIn("optional element", value or "")

    def test_parses_options_in_order_with_content(self):
        """Every '### Option N: ...' heading must become an AdrOption with its own content."""
        adr = parse_adr(_FULL_ADR)
        self.assertEqual(len(adr.body.options), 2)
        first, second = adr.body.options
        self.assertEqual(first.number, 1)
        self.assertEqual(first.partial_title, "Postgres")
        self.assertIn("mature", first.content)
        self.assertEqual(second.number, 2)
        self.assertEqual(second.partial_title, "MongoDB")
        self.assertIn("flexible schema", second.content)

    def test_no_options_yields_empty_list(self):
        """A document with no 'Option N' headings at all must parse to an empty options list."""
        text = textwrap.dedent(
            """\
            ---
            status: draft
            ---
            # A title

            ## Context and Problem Statement

            Context.

            ## Considered Options

            Options.

            ## Decision Outcome

            Outcome.
            """
        )
        adr = parse_adr(text)
        self.assertEqual(adr.body.options, [])

    def test_options_recognized_without_pros_and_cons_wrapper(self):
        """'### Option N: ...' headings must be recognized even without the derived H2 wrapper."""
        text = textwrap.dedent(
            """\
            ---
            status: draft
            ---
            # A title

            ## Context and Problem Statement

            Context.

            ## Considered Options

            Options.

            ## Decision Outcome

            Outcome.

            ### Option 1: Solo option

            Some content.
            """
        )
        adr = parse_adr(text)
        self.assertEqual(len(adr.body.options), 1)
        self.assertEqual(adr.body.options[0].partial_title, "Solo option")

    def test_no_frontmatter_block_still_parses_with_defaults(self):
        """A file with no YAML frontmatter block at all must fall back to AdrFrontmatter's defaults."""
        text = textwrap.dedent(
            """\
            # A title

            ## Context and Problem Statement

            Context.

            ## Considered Options

            Options.

            ## Decision Outcome

            Outcome.
            """
        )
        adr = parse_adr(text)
        self.assertEqual(adr.frontmatter.status, "draft")

    def test_missing_mandatory_body_field_raises_validation_error(self):
        """Omitting a mandatory whole-section heading must surface as a pydantic ValidationError."""
        text = textwrap.dedent(
            """\
            ---
            status: draft
            ---
            # A title

            ## Context and Problem Statement

            Context.
            """
        )
        with self.assertRaises(ValidationError):
            parse_adr(text)

    def test_invalid_frontmatter_value_raises_validation_error(self):
        """An invalid frontmatter value (e.g. bad status) must surface as a pydantic ValidationError."""
        text = textwrap.dedent(
            """\
            ---
            status: not-a-real-status
            ---
            # A title

            ## Context and Problem Statement

            Context.

            ## Considered Options

            Options.

            ## Decision Outcome

            Outcome.
            """
        )
        with self.assertRaises(ValidationError):
            parse_adr(text)

    def test_unrecognized_h2_heading_raises_parse_error(self):
        """An H2 heading outside the fixed set must raise AdrParseError, not silently drop content."""
        text = textwrap.dedent(
            """\
            ---
            status: draft
            ---
            # A title

            ## Context and Problem Statement

            Context.

            ## Not A Real Section

            Surprise content.

            ## Considered Options

            Options.

            ## Decision Outcome

            Outcome.
            """
        )
        with self.assertRaises(AdrParseError):
            parse_adr(text)

    def test_unrecognized_h3_heading_raises_parse_error(self):
        """An H3 heading that is neither Consequences/Confirmation nor 'Option N: ...' must raise."""
        text = textwrap.dedent(
            """\
            ---
            status: draft
            ---
            # A title

            ## Context and Problem Statement

            Context.

            ## Considered Options

            Options.

            ## Decision Outcome

            Outcome.

            ### Not A Real Subsection

            Surprise content.
            """
        )
        with self.assertRaises(AdrParseError):
            parse_adr(text)

    def test_duplicate_h2_heading_raises_parse_error(self):
        """Two headings mapping to the same field must raise AdrParseError."""
        text = textwrap.dedent(
            """\
            ---
            status: draft
            ---
            # A title

            ## Context and Problem Statement

            Context, take one.

            ## Context and Problem Statement

            Context, take two.

            ## Considered Options

            Options.

            ## Decision Outcome

            Outcome.
            """
        )
        with self.assertRaises(AdrParseError):
            parse_adr(text)

    def test_duplicate_option_number_raises_parse_error(self):
        """Two 'Option N' headings sharing the same N must raise AdrParseError."""
        text = textwrap.dedent(
            """\
            ---
            status: draft
            ---
            # A title

            ## Context and Problem Statement

            Context.

            ## Considered Options

            Options.

            ## Decision Outcome

            Outcome.

            ### Option 1: First

            Content.

            ### Option 1: Duplicate number

            More content.
            """
        )
        with self.assertRaises(AdrParseError):
            parse_adr(text)

    def test_multiple_h1_headings_raises_parse_error(self):
        """More than one top-level (H1) heading must raise AdrParseError."""
        text = textwrap.dedent(
            """\
            ---
            status: draft
            ---
            # First title

            ## Context and Problem Statement

            Context.

            # Second title

            ## Considered Options

            Options.

            ## Decision Outcome

            Outcome.
            """
        )
        with self.assertRaises(AdrParseError):
            parse_adr(text)

    def test_content_before_first_heading_raises_parse_error(self):
        """Non-blank text before the first (H1) heading must raise AdrParseError."""
        text = textwrap.dedent(
            """\
            ---
            status: draft
            ---
            Some stray preamble text.

            # A title

            ## Context and Problem Statement

            Context.

            ## Considered Options

            Options.

            ## Decision Outcome

            Outcome.
            """
        )
        with self.assertRaises(AdrParseError):
            parse_adr(text)

    def test_h4_heading_raises_parse_error(self):
        """A heading level this schema doesn't define (H4+) must raise AdrParseError."""
        text = textwrap.dedent(
            """\
            ---
            status: draft
            ---
            # A title

            ## Context and Problem Statement

            Context.

            ## Considered Options

            Options.

            ## Decision Outcome

            Outcome.

            #### Too deep

            Content.
            """
        )
        with self.assertRaises(AdrParseError):
            parse_adr(text)

    def test_h3_inside_considered_options_is_swallowed_as_content(self):
        """A heading nested inside a 'leaf' H2 (e.g. Considered Options) must not break parsing."""
        text = textwrap.dedent(
            """\
            ---
            status: draft
            ---
            # A title

            ## Context and Problem Statement

            Context.

            ## Considered Options

            ### Postgres

            Mature, ACID.

            ### MongoDB

            Flexible schema.

            ## Decision Outcome

            Outcome.
            """
        )
        adr = parse_adr(text)
        self.assertIn("### Postgres", adr.body.considered_options)
        self.assertIn("Mature, ACID", adr.body.considered_options)
        self.assertIn("### MongoDB", adr.body.considered_options)
        self.assertIn("Flexible schema", adr.body.considered_options)

    def test_h4_inside_consequences_is_swallowed_as_content(self):
        """A heading nested inside 'Consequences' (H3) must not break parsing."""
        text = textwrap.dedent(
            """\
            ---
            status: draft
            ---
            # A title

            ## Context and Problem Statement

            Context.

            ## Considered Options

            Options.

            ## Decision Outcome

            Outcome.

            ### Consequences

            #### Good

            ACID transactions.

            #### Bad

            More ops overhead.
            """
        )
        adr = parse_adr(text)
        self.assertIn("#### Good", adr.body.consequences)
        self.assertIn("ACID transactions", adr.body.consequences)
        self.assertIn("#### Bad", adr.body.consequences)
        self.assertIn("More ops overhead", adr.body.consequences)

    def test_h4_inside_confirmation_is_swallowed_as_content(self):
        """A heading nested inside 'Confirmation' (H3) must not break parsing."""
        text = textwrap.dedent(
            """\
            ---
            status: draft
            ---
            # A title

            ## Context and Problem Statement

            Context.

            ## Considered Options

            Options.

            ## Decision Outcome

            Outcome.

            ### Confirmation

            #### Review board

            Approved.
            """
        )
        adr = parse_adr(text)
        self.assertIn("#### Review board", adr.body.confirmation)
        self.assertIn("Approved", adr.body.confirmation)

    def test_h3_inside_more_information_is_swallowed_as_content(self):
        """A heading nested inside 'More Information' (leaf H2) must not break parsing."""
        text = textwrap.dedent(
            """\
            ---
            status: draft
            ---
            # A title

            ## Context and Problem Statement

            Context.

            ## Considered Options

            Options.

            ## Decision Outcome

            Outcome.

            ## More Information

            ### Links

            See the team wiki.
            """
        )
        adr = parse_adr(text)
        self.assertIn("### Links", adr.body.more_information)
        self.assertIn("See the team wiki", adr.body.more_information)

    def test_deeply_nested_headings_across_full_document_round_trip(self):
        """A full document exercising all four previously-broken cases at once must parse cleanly."""
        text = textwrap.dedent(
            """\
            ---
            status: draft
            ---
            # A title

            ## Context and Problem Statement

            Context.

            ## Considered Options

            ### Postgres

            Details.

            ## Decision Outcome

            Outcome.

            ### Consequences

            #### Good

            Details.

            ### Confirmation

            #### Review

            Details.

            ## More Information

            ### Links

            Details.
            """
        )
        adr = parse_adr(text)
        self.assertIn("### Postgres", adr.body.considered_options)
        self.assertIn("#### Good", adr.body.consequences)
        self.assertIn("#### Review", adr.body.confirmation)
        self.assertIn("### Links", adr.body.more_information)


if __name__ == "__main__":
    unittest.main()
