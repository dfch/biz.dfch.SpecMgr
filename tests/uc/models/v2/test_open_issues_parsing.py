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

"""Verify OpenIssues parses its plain bullet list (no dynamic h3 sub-headings)."""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.uc.models.v2.use_case import OpenIssues


class TestOpenIssuesParsing(unittest.TestCase):
    """Test parsing of the Open Issues section."""

    def test_items_parsed_from_bullet_list(self) -> None:
        """OpenIssues.items is populated from the h2's own bullet list."""
        markdown_text = format_text("""## Open Issues

- What happens if we have only part of the order in stock?
- What happens if credit card is stolen?
- How do we handle international orders?
""")
        open_issues = OpenIssues.from_text(markdown_text)

        self.assertEqual(len(open_issues.items), 3)
        self.assertEqual(open_issues.items[0].text, "What happens if we have only part of the order in stock?")
        self.assertEqual(open_issues.items[1].text, "What happens if credit card is stolen?")
        self.assertEqual(open_issues.items[2].text, "How do we handle international orders?")

    def test_loose_bullet_list_round_trips_byte_exact(self) -> None:
        """A loose bullet list (blank line between every item) round-trips exactly."""
        markdown_text = format_text("""## Open Issues

- What happens if we have only part of the order in stock?

- What happens if credit card is stolen?
""")
        open_issues = OpenIssues.from_text(markdown_text)

        self.assertEqual(str(open_issues), markdown_text)

    def test_tight_bullet_list_round_trips_to_loose_equivalent(self) -> None:
        """A tight bullet list round-trips to an equivalent loose list -- same
        documented `MarkdownListItem` exception used throughout this model."""
        tight = format_text("""## Open Issues

- What happens if we have only part of the order in stock?
- What happens if credit card is stolen?
""")
        loose_equivalent = format_text("""## Open Issues

- What happens if we have only part of the order in stock?

- What happens if credit card is stolen?
""")
        open_issues = OpenIssues.from_text(tight)

        self.assertNotEqual(str(open_issues), tight)
        self.assertEqual(str(open_issues), loose_equivalent)


if __name__ == "__main__":
    unittest.main()
