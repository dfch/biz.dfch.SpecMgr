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

"""Unit tests for models.md.common_sections (feat-29-dec-source-roles).

The `*Base` classes are deliberately never parsed directly -- their default
`SPACE_SEPARATED` alias derives from their own (suffixed) class name, e.g.
`"AccountableBase"` -> `"Accountable Base"`, which does not match the real
`### Accountable` heading. They only produce a working, matchable class once
subclassed with a bare, correctly-named concrete class (e.g. `class
Accountable(AccountableBase): pass`), exactly the pattern every domain
(`req`, `sop`, `dec`) actually uses. These tests exercise the base classes
through minimal local subclasses named exactly like the real domain
classes would be, mirroring that usage, plus the
`@alias` inheritance mechanism `RolesAndResponsibilitiesBase` relies on:
it declares `@alias(value="Roles and Responsibilities", ...)` exactly once,
and a domain subclass that never redeclares it must still match that literal
heading (not the default `SPACE_SEPARATED` derivation of its own subclass
name, which would produce "Roles And Responsibilities" with a capital
"And").
"""

import unittest

import mdformat
from pydantic import Field

from biz.dfch.specmgr.models.md.common_sections import (
    AccountableBase,
    ConsultedBase,
    InformedBase,
    ResponsibleBase,
    RolesAndResponsibilitiesBase,
    SourceBase,
    SupportBase,
)


class Source(SourceBase):
    pass


class Accountable(AccountableBase):
    pass


class Responsible(ResponsibleBase):
    pass


class Support(SupportBase):
    pass


class Consulted(ConsultedBase):
    pass


class Informed(InformedBase):
    pass


class TestSourceBase(unittest.TestCase):
    """Tests for a concrete Source subclass parsing its own `## Source` heading."""

    def test_parses_single_line_value(self) -> None:
        text = mdformat.text("## Source\n\nA stakeholder request.\n")
        instance = Source.from_text(text)
        self.assertEqual(instance.value.text, "A stakeholder request.")


class TestRasciLeafBases(unittest.TestCase):
    """Tests for concrete subclasses of the five RASCI leaf base classes parsing their own headings."""

    def test_accountable_base_parses_single_paragraph(self) -> None:
        text = mdformat.text("### Accountable\n\nJane Doe.\n")
        instance = Accountable.from_text(text)
        self.assertEqual(instance.value.text, "Jane Doe.")

    def test_responsible_base_parses_bullet_list(self) -> None:
        text = mdformat.text("### Responsible\n\n- Alice\n- Bob\n")
        instance = Responsible.from_text(text)
        assert instance.items is not None
        self.assertEqual(len(instance.items), 2)

    def test_support_base_may_be_present_with_zero_items(self) -> None:
        text = mdformat.text("### Support\n")
        instance = Support.from_text(text)
        self.assertIsNone(instance.items)

    def test_consulted_base_may_be_present_with_zero_items(self) -> None:
        text = mdformat.text("### Consulted\n")
        instance = Consulted.from_text(text)
        self.assertIsNone(instance.items)

    def test_informed_base_may_be_present_with_zero_items(self) -> None:
        text = mdformat.text("### Informed\n")
        instance = Informed.from_text(text)
        self.assertIsNone(instance.items)


class TestRolesAndResponsibilitiesBaseAlias(unittest.TestCase):
    """Tests for RolesAndResponsibilitiesBase's @alias and its inheritance by subclasses."""

    def test_base_class_alias_metadata_is_literal_roles_and_responsibilities(self) -> None:
        metadata = RolesAndResponsibilitiesBase._alias_metadata
        self.assertEqual(metadata["value"], "Roles and Responsibilities")

    def test_undecorated_subclass_inherits_alias_metadata(self) -> None:
        """A domain subclass that never redeclares `@alias` still inherits the
        base's `_alias_metadata` via normal Python attribute lookup (verified
        during feat-29-dec-source-roles planning) -- this is what lets every
        domain's own `RolesAndResponsibilities` subclass skip redeclaring
        `@alias` itself.
        """

        class RolesAndResponsibilities(RolesAndResponsibilitiesBase):
            accountable: Accountable = Field(description="test")  # type: ignore
            responsible: Responsible = Field(description="test")  # type: ignore

        self.assertNotIn("_alias_metadata", RolesAndResponsibilities.__dict__)
        self.assertEqual(
            RolesAndResponsibilities._alias_metadata["value"],
            "Roles and Responsibilities",
        )

    def test_undecorated_subclass_parses_the_literal_heading(self) -> None:
        class RolesAndResponsibilities(RolesAndResponsibilitiesBase):
            accountable: Accountable = Field(description="test")  # type: ignore
            responsible: Responsible = Field(description="test")  # type: ignore

        text = mdformat.text(
            "## Roles and Responsibilities\n\n### Accountable\n\nJane Doe.\n\n### Responsible\n\n- Alice\n"
        )
        instance = RolesAndResponsibilities.from_text(text)
        self.assertEqual(instance.accountable.value.text, "Jane Doe.")

    def test_undecorated_subclass_rejects_the_space_separated_default(self) -> None:
        """Confirms the inherited alias is actually enforced, not silently
        ignored: the class-name-derived default ("Roles And Responsibilities",
        capital "And") must NOT satisfy the inherited LITERAL alias."""

        class RolesAndResponsibilities(RolesAndResponsibilitiesBase):
            accountable: Accountable = Field(description="test")  # type: ignore
            responsible: Responsible = Field(description="test")  # type: ignore

        text = mdformat.text(
            "## Roles And Responsibilities\n\n### Accountable\n\nJane Doe.\n\n### Responsible\n\n- Alice\n"
        )
        with self.assertRaises(AssertionError):
            RolesAndResponsibilities.from_text(text)
