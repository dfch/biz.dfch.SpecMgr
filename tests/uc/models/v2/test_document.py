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

"""Tests for the UcDocument Pydantic model (frontmatter + body composition).

Mirrors `tests/models/adr/v1/test_adr.py`'s own `Adr` test shape.
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.uc.models.v2 import UcDocument, UcFrontmatter, UseCase


def _make_body() -> UseCase:
    markdown_text = format_text("""# Buy Goods

## Characteristic Information

### Goal in Context

Buyer issues request.

### Scope

Company.

### Level

Summary

### Precondition

- We know Buyer

### Success End Condition

- Buyer has goods

### Primary Actor

Buyer.

### Trigger

Purchase request comes in.

## Main Success Scenario

1. Buyer calls in with a purchase request.
2. Company creates order in system.
""")
    return UseCase.from_text(markdown_text)


class TestUcDocument(unittest.TestCase):
    """Tests for the UcDocument Pydantic model."""

    def test_holds_frontmatter_and_body(self) -> None:
        """A UcDocument must hold both a validated frontmatter and body."""
        document = UcDocument(frontmatter=UcFrontmatter(status="accepted"), body=_make_body())
        self.assertEqual(document.frontmatter.status, "accepted")
        self.assertEqual(document.body.text, "Buy Goods")

    def test_accepts_nested_dict_frontmatter(self) -> None:
        """UcDocument must validate a nested plain dict into UcFrontmatter."""
        document = UcDocument.model_validate({"frontmatter": {"status": "proposed"}, "body": _make_body()})
        self.assertIsInstance(document.frontmatter, UcFrontmatter)
        self.assertEqual(document.frontmatter.status, "proposed")

    def test_invalid_nested_frontmatter_fails(self) -> None:
        """An invalid nested frontmatter must fail validation at the UcDocument level."""
        with self.assertRaises(ValidationError):
            UcDocument.model_validate({"frontmatter": {"status": "not-a-real-status"}, "body": _make_body()})

    def test_frontmatter_defaults_when_omitted_fields(self) -> None:
        """UcDocument's frontmatter still applies UcFrontmatter's own defaults."""
        document = UcDocument(frontmatter=UcFrontmatter(), body=_make_body())
        self.assertEqual(document.frontmatter.type, "uc")
        self.assertEqual(document.frontmatter.status, "draft")


if __name__ == "__main__":
    unittest.main()
