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

"""Confirms a generic, non-pydantic-specific walk over a class's attributes.

``test_field_declaration_order.py`` pins down that ``BaseModel.model_fields``
preserves declaration order. ``walk_attributes`` here generalizes that to any
class by reading each class in ``cls.__mro__`` (base to derived) and merging
their own (non-inherited) ``__annotations__`` -- the same mechanism the
generic heading-mapped parser sketched in
``tests/feat-5-md-model-parser/req_parser.py`` needs when it is not
walking a ``pydantic.BaseModel`` directly.
"""

import unittest
from collections.abc import Iterator

from pydantic import StrictStr


def walk_attributes(cls: type) -> Iterator[str]:
    """Enumerate ``cls``'s attribute names in declaration order.

    Declaration order follows ``cls.__mro__`` from the most base class down
    to ``cls`` itself, using each class's own ``__annotations__`` (not the
    inherited, already-merged ``__annotations__`` a subclass would otherwise
    expose) to avoid double-counting a parent's attributes. An attribute
    redeclared by a subclass keeps its original position, matching ``dict``
    insertion-order semantics for a repeated key, rather than moving to the
    end.

    Args:
        cls: The class to enumerate.

    Yields:
        Each attribute name, in declaration order.
    """
    assert isinstance(cls, type), type(cls)

    names: dict[str, None] = {}
    for klass in reversed(cls.__mro__):
        own_annotations = vars(klass).get("__annotations__", {})
        for name in own_annotations:
            names[name] = None

    yield from names


class SampleAttributeClass:
    """Plain class with attributes declared in a deliberately non-alphabetical order."""

    zeta: str
    alpha: str
    middle: str
    beta: str
    omega: str


class SampleAttributeBase:
    """Base class contributing the first attributes of an inheritance chain."""

    zeta: str
    alpha: str


class SampleAttributeDerived(SampleAttributeBase):
    """Derived class appending further attributes after the inherited ones."""

    middle: str
    beta: str
    omega: str


class SampleAttributeOverride(SampleAttributeBase):
    """Derived class redeclaring an inherited attribute instead of adding a new one."""

    alpha: str
    omega: str


class SampleAttributeEmpty:
    """Class with no annotated attributes at all."""


class MarkdownStr(StrictStr):
    pass


class TestWalkAttributes(unittest.TestCase):
    def test_walk_visits_every_attribute_in_declaration_order(self):
        expected_order = ["zeta", "alpha", "middle", "beta", "omega"]

        sut = SampleAttributeClass

        result = list(walk_attributes(sut))

        self.assertEqual(result, expected_order)

    def test_walk_preserves_inherited_attribute_order(self):
        expected_order = ["zeta", "alpha", "middle", "beta", "omega"]

        sut = SampleAttributeDerived

        result = list(walk_attributes(sut))

        self.assertEqual(result, expected_order)

    def test_walk_keeps_redeclared_attribute_at_its_original_position(self):
        expected_order = ["zeta", "alpha", "omega"]

        sut = SampleAttributeOverride

        result = list(walk_attributes(sut))

        self.assertEqual(result, expected_order)

    def test_walk_empty_class_yields_nothing(self):
        sut = SampleAttributeEmpty

        result = list(walk_attributes(sut))

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
