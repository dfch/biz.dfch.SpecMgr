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

"""Confirms that ``BaseModel.model_fields`` preserves declaration order.

The generic heading-mapped parser sketched in
``tests/feat-5-md-model-parser/req_parser.py`` walks a model's fields via
``Model.model_fields`` and relies on that dict preserving declaration order
(including fields inherited from a base class). These tests pin down that
behavior with an explicit, committed test instead of an ad-hoc check.
"""

import unittest

from pydantic import BaseModel


class SampleOrderedModel(BaseModel):
    """Plain model with fields declared in a deliberately non-alphabetical order."""

    zeta: str = ""
    alpha: str = ""
    middle: str = ""
    beta: str = ""
    omega: str = ""


class SampleOrderedModelBase(BaseModel):
    """Base model contributing the first fields of an inheritance chain."""

    zeta: str = ""
    alpha: str = ""


class SampleOrderedModelDerived(SampleOrderedModelBase):
    """Derived model appending further fields after the inherited ones."""

    middle: str = ""
    beta: str = ""
    omega: str = ""


class TestFieldDeclarationOrder(unittest.TestCase):
    def test_model_fields_preserves_declaration_order(self):
        expected_order = ["zeta", "alpha", "middle", "beta", "omega"]

        sut = SampleOrderedModel

        result = list(sut.model_fields.keys())

        self.assertEqual(result, expected_order)

    def test_model_fields_preserves_inherited_field_order(self):
        expected_order = ["zeta", "alpha", "middle", "beta", "omega"]

        sut = SampleOrderedModelDerived

        result = list(sut.model_fields.keys())

        self.assertEqual(result, expected_order)


if __name__ == "__main__":
    unittest.main()
