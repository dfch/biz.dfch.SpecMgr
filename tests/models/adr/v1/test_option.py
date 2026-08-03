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

"""Tests for the AdrOption Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models import AdrOption


class TestAdrOption(unittest.TestCase):
    """Tests for the AdrOption Pydantic model."""

    def test_full_title_renders_option_heading(self):
        """full_title must render as 'Option {number}: {partial_title}'."""
        option = AdrOption(number=1, partial_title="Use Postgres", content="Good, because ...")
        self.assertEqual(option.full_title, "Option 1: Use Postgres")

    def test_content_defaults_to_empty_string(self):
        """content is not mandatory and defaults to an empty string."""
        option = AdrOption(number=1, partial_title="Use Postgres")
        self.assertEqual(option.content, "")

    def test_number_must_be_positive(self):
        """number must be greater than zero."""
        with self.assertRaises(ValidationError):
            AdrOption(number=0, partial_title="Use Postgres")

    def test_rejects_blank_partial_title(self):
        """partial_title must not be blank."""
        with self.assertRaises(ValidationError):
            AdrOption(number=1, partial_title="   ")

    def test_rejects_partial_title_with_line_break(self):
        """partial_title must not contain embedded line breaks."""
        with self.assertRaises(ValidationError):
            AdrOption(number=1, partial_title="Use Postgres\nfor storage")


if __name__ == "__main__":
    unittest.main()
