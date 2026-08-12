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

"""Tests for the `UseCase`-level cross-field `model_validator` (Task 1.6).

Ports the last of the three Task 1.3B cross-field validators onto the v2
model tree: every `Extension`/`SubVariation` heading's step reference must
resolve to an existing 1-based position in `main_success_scenario.steps`,
with no duplicate references within either collection. Mirrors
`tests/uc/models/v1/test_use_case.py`'s equivalent coverage.

The other two original Task 1.3B validators (`MainSuccessScenario.steps`
numbered contiguously; `Extension` actions numbered sequentially) are
deliberately *not* ported: both are structurally unnecessary now that
`steps`/`Extension.items` are real CommonMark ordered lists (no gap/
duplicate/out-of-order state is even representable) rather than compound-
numbered prose -- see `test_extension_items_have_no_representable_numbering_gap`
below, which documents rather than "tests" that finding, since there is no
numbering field left to assert on.
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.uc.models.v2.use_case import UseCase, Extension, ExtensionItem


def _make_use_case_text(*, extensions: str = "", sub_variations: str = "") -> str:
    """Build a minimal, valid `UseCase` document with 2 main-scenario steps,
    optionally followed by an `Extensions`/`Sub-Variations` section body."""
    return format_text(f"""# Buy Goods

## Characteristic Information

### Goal in Context

Buyer issues request.

### Scope

Company.

### Level

Summary

### Preconditions

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
{extensions}{sub_variations}""")


class TestUseCaseStepReferenceValidation(unittest.TestCase):
    """Tests for `UseCase.validate_step_references_resolve_and_are_unique`."""

    def test_valid_extension_and_sub_variation_references_resolve(self) -> None:
        """References that resolve to an existing step, with no duplicates, succeed."""
        markdown_text = _make_use_case_text(
            extensions="""
## Extensions

### Extension 1a. Buyer cancels the request

1. Company cancels the order.

""",
            sub_variations="""
## Sub-Variations

### Step 2: Company may create the order via

- Manual entry
- Automated system
""",
        )
        use_case = UseCase.from_text(markdown_text)

        self.assertIsNotNone(use_case.extensions.extensions)
        self.assertIsNotNone(use_case.sub_variations.sub_variations)

    def test_extension_reference_must_resolve_to_existing_step(self) -> None:
        """An extension referencing a non-existent main scenario step must be rejected."""
        markdown_text = _make_use_case_text(
            extensions="""
## Extensions

### Extension 5a. Step 5 does not exist

1. Company cancels the order.
"""
        )
        with self.assertRaises(ValidationError):
            UseCase.from_text(markdown_text)

    def test_extension_step_references_must_be_unique(self) -> None:
        """Two extensions with the same `{ref}` (e.g. "1a") must be rejected."""
        markdown_text = _make_use_case_text(
            extensions="""
## Extensions

### Extension 1a. Buyer cancels the request

1. Company cancels the order.

### Extension 1a. Buyer changes the request

1. Company updates the order.
"""
        )
        with self.assertRaises(ValidationError):
            UseCase.from_text(markdown_text)

    def test_sub_variation_reference_must_resolve_to_existing_step(self) -> None:
        """A sub-variation referencing a non-existent main scenario step must be rejected."""
        markdown_text = _make_use_case_text(
            sub_variations="""
## Sub-Variations

### Step 7: Step 7 does not exist

- Some variation
"""
        )
        with self.assertRaises(ValidationError):
            UseCase.from_text(markdown_text)

    def test_sub_variation_references_must_be_unique(self) -> None:
        """Two sub-variations with the same `{N}` (e.g. "1") must be rejected."""
        markdown_text = _make_use_case_text(
            sub_variations="""
## Sub-Variations

### Step 1: Buyer may use

- Phone call

### Step 1: Buyer may also use

- Fax
"""
        )
        with self.assertRaises(ValidationError):
            UseCase.from_text(markdown_text)

    def test_extension_letter_suffix_is_never_checked_against_steps(self) -> None:
        """Only an `Extension` reference's leading digits are resolved against
        `main_success_scenario.steps` -- the letter suffix (`"1a"` vs `"1b"`) is
        never itself checked, mirroring v1's `_validate_unique_and_resolvable`."""
        markdown_text = _make_use_case_text(
            extensions="""
## Extensions

### Extension 1z. An unusual but structurally valid suffix

1. Company handles the extension.
"""
        )
        use_case = UseCase.from_text(markdown_text)

        self.assertEqual(len(use_case.extensions.extensions), 1)

    def test_extension_items_have_no_representable_numbering_gap(self) -> None:
        """Documents Task 1.6 item 2's finding: `Extension.items` (a real
        CommonMark ordered list) has no gap/duplicate/out-of-order state to
        validate against -- there is no numbering field on `ExtensionItem` at
        all, including when an item carries a `notes` continuation paragraph.
        No `UseCase`-level (or `Extension`-level) invariant is needed here."""
        markdown_text = format_text("""### Extension 3a. Company is out of one of the ordered items

1. Company informs buyer of out-of-stock items.

   This should rarely happen. Still we have to address this.

2. Buyer chooses to wait for restock.
3. Return to step 4.
""")
        extension = Extension.from_text(markdown_text)

        self.assertEqual(len(extension.items), 3)
        for item in extension.items:
            self.assertIsInstance(item, ExtensionItem)
        self.assertIsNotNone(extension.items[0].notes)
        self.assertIsNone(extension.items[1].notes)
        self.assertIsNone(extension.items[2].notes)


if __name__ == "__main__":
    unittest.main()
