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

"""Tests for `parse_rasci`, exercised end-to-end against the real, packaged
``general/data/general_rasci.md`` (feat-92-resources Task 5.1, REQ-005),
plus fail-fast/malformed-content drift-guard tests (ACC-005), mirroring
``tests/models/test_dtais.py``'s structure and style.
"""

from __future__ import annotations

import unittest

import pydantic

from biz.dfch.specmgr.general.models import Rasci, parse_rasci
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text

#: A deliberately malformed document: only 4 of the required 5 role
#: bullets (`Informed` dropped), so `Roles.items`'s
#: `min_length=5`/`max_length=5` constraint rejects it.
_MISSING_ROLE_TEXT = """# RASCI Responsibility Assignment

RASCI is a responsibility-assignment framework that names, for a given
piece of work, who does it, who owns it, who helps, who is consulted, and
who is kept informed.

## The five roles

- **Responsible** -- the people who do the work.
- **Accountable** -- the single owner who is ultimately answerable for the
  work.
- **Support** -- the people who provide resources, tooling, or assistance.
- **Consulted** -- the people whose opinions are sought before or during
  the work.

## RASCI vs. plain RACI

Plain RACI names four roles -- Responsible, Accountable, Consulted, and
Informed. RASCI adds the fifth, **S**upport role.
"""

#: A deliberately malformed document: the role list has all 5 required
#: entries, but two are swapped out of the expected order (`Support` and
#: `Accountable`), so `Roles._validate_roles` rejects it.
_OUT_OF_ORDER_ROLE_TEXT = """# RASCI Responsibility Assignment

RASCI is a responsibility-assignment framework that names, for a given
piece of work, who does it, who owns it, who helps, who is consulted, and
who is kept informed.

## The five roles

- **Responsible** -- the people who do the work.
- **Support** -- the people who provide resources, tooling, or assistance.
- **Accountable** -- the single owner who is ultimately answerable for the
  work.
- **Consulted** -- the people whose opinions are sought before or during
  the work.
- **Informed** -- the people who are kept up to date on progress.

## RASCI vs. plain RACI

Plain RACI names four roles -- Responsible, Accountable, Consulted, and
Informed. RASCI adds the fifth, **S**upport role.
"""

#: A deliberately malformed document: the role list has 5 entries, but one
#: (`Owner`) is not in the closed RASCI role vocabulary, so
#: `Roles._validate_roles` rejects it.
_OUT_OF_VOCABULARY_ROLE_TEXT = """# RASCI Responsibility Assignment

RASCI is a responsibility-assignment framework that names, for a given
piece of work, who does it, who owns it, who helps, who is consulted, and
who is kept informed.

## The five roles

- **Responsible** -- the people who do the work.
- **Accountable** -- the single owner who is ultimately answerable for the
  work.
- **Owner** -- the people who provide resources, tooling, or assistance.
- **Consulted** -- the people whose opinions are sought before or during
  the work.
- **Informed** -- the people who are kept up to date on progress.

## RASCI vs. plain RACI

Plain RACI names four roles -- Responsible, Accountable, Consulted, and
Informed. RASCI adds the fifth, **S**upport role.
"""


class TestParseRasci(unittest.TestCase):
    """Tests for `parse_rasci` against the packaged RASCI guidance data."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read_packaged_text("general", "rasci", "md")

    def test_returns_rasci_instance(self):
        """The parser must return a `Rasci` instance."""
        result = parse_rasci(self.text)
        self.assertIsInstance(result, Rasci)

    def test_has_five_role_items(self):
        """Exactly 5 role bullets."""
        result = parse_rasci(self.text)
        self.assertEqual(len(result.roles.items), 5)

    def test_role_names_in_order(self):
        """The 5 role names must be exactly the RASCI vocabulary, in order."""
        result = parse_rasci(self.text)
        roles = [item.role for item in result.roles.items]
        self.assertEqual(roles, ["Responsible", "Accountable", "Support", "Consulted", "Informed"])

    def test_role_descriptions_are_non_empty(self):
        """Every role item's description must be non-empty prose."""
        result = parse_rasci(self.text)
        for item in result.roles.items:
            with self.subTest(role=item.role):
                self.assertTrue(item.description.strip())

    def test_raises_on_missing_role(self):
        """A document with only 4 of the 5 required role bullets must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_rasci(_MISSING_ROLE_TEXT)

    def test_raises_on_out_of_order_role(self):
        """A role list with a role name out of the expected order must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_rasci(_OUT_OF_ORDER_ROLE_TEXT)

    def test_raises_on_out_of_vocabulary_role(self):
        """A role list with a role name not in the closed vocabulary must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_rasci(_OUT_OF_VOCABULARY_ROLE_TEXT)


if __name__ == "__main__":
    unittest.main()
