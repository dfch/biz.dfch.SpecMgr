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

"""Tests for `parse_tara`, exercised end-to-end against the real, packaged
``rsk/data/rsk_tara.md`` (feat-92-resources Task 3.1, REQ-003), plus
fail-fast/malformed-content drift-guard tests (ACC-003), mirroring
``tests/models/test_dtais.py``'s structure and style.
"""

from __future__ import annotations

import unittest

import pydantic

from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text
from biz.dfch.specmgr.rsk.models.v1 import Tara, parse_tara

#: A deliberately malformed document: only 3 of the required 4 intro
#: strategy bullets, so `Tara.strategies`'s `min_length=4`/`max_length=4`
#: constraint rejects it.
_MISSING_STRATEGY_TEXT = """# TARA risk-response strategies for `rsk` documents

`rsk` documents (risk register entries) carry a mandatory `## Strategy`
section with exactly one lowercase word naming the TARA response chosen for
the risk. **TARA** is the risk-response framework: **T**ransfer, **A**ccept,
**R**educe, **A**void. Only the four valid words below are accepted by the
schema — anything else (including the TARRA-era words `tolerate`, `assign`,
`recover`, or any capitalized/compound variant) is a validation error:

- `transfer`
- `accept`
- `reduce`

## When to apply each strategy

Read the risk's matrix coordinates (`## Initial Assessment`, see the risk
matrix document) to pick a strategy:

- **Low probability / high impact → `transfer`**
  The risk is unlikely but would be severe if it hit.
- **High probability / high impact → `avoid`**
  The risk is both likely and severe.
- **High probability / low impact → `reduce`**
  The risk is likely but the consequence is bounded.
- **Low probability / low impact → `accept`**
  The risk is unlikely and bounded.

The four quadrants are a guideline, not a rule — the documented
rationale of the choice matters more than the quadrant label.

## Interaction with `## Mitigation`

`## Mitigation` is the treatment section between the two assessments.

- `reduce`: concrete measures are mandatory.
- `transfer`: name the transfer mechanism.
- `avoid`: describe what is eliminated.
- `accept`: write `none` — acceptance means no treatment is taken.

## Interaction with the frontmatter `status`

The `rsk` frontmatter `status` is a six-value lifecycle:

- `open` — identified and monitored; no treatment decided or started yet.
- `mitigating` — treatment is in progress.
- `accepted` — the residual risk is formally accepted.
- `occurred` — the risk event materialized.
- `closed` — resolved or expired.
- `dropped` — removed from the register.

`status` tracks the lifecycle state of the entry; `strategy` tracks the
chosen response. They are independent fields.
"""

#: A deliberately malformed document: the quadrant list drops `accept`
#: entirely and duplicates `avoid` instead, so its *set* of strategy words
#: no longer matches the intro list's, and
#: `Tara._validate_quadrant_matches_strategies` rejects it.
_QUADRANT_MISSING_STRATEGY_TEXT = """# TARA risk-response strategies for `rsk` documents

`rsk` documents (risk register entries) carry a mandatory `## Strategy`
section with exactly one lowercase word naming the TARA response chosen for
the risk. **TARA** is the risk-response framework: **T**ransfer, **A**ccept,
**R**educe, **A**void. Only the four valid words below are accepted by the
schema — anything else (including the TARRA-era words `tolerate`, `assign`,
`recover`, or any capitalized/compound variant) is a validation error:

- `transfer`
- `accept`
- `reduce`
- `avoid`

## When to apply each strategy

Read the risk's matrix coordinates (`## Initial Assessment`, see the risk
matrix document) to pick a strategy:

- **Low probability / high impact → `transfer`**
  The risk is unlikely but would be severe if it hit.
- **High probability / high impact → `avoid`**
  The risk is both likely and severe.
- **High probability / low impact → `reduce`**
  The risk is likely but the consequence is bounded.
- **Low probability / low impact → `avoid`**
  Duplicated `avoid` instead of naming `accept`.

The four quadrants are a guideline, not a rule — the documented
rationale of the choice matters more than the quadrant label.

## Interaction with `## Mitigation`

`## Mitigation` is the treatment section between the two assessments.

- `reduce`: concrete measures are mandatory.
- `transfer`: name the transfer mechanism.
- `avoid`: describe what is eliminated.
- `accept`: write `none` — acceptance means no treatment is taken.

## Interaction with the frontmatter `status`

The `rsk` frontmatter `status` is a six-value lifecycle:

- `open` — identified and monitored; no treatment decided or started yet.
- `mitigating` — treatment is in progress.
- `accepted` — the residual risk is formally accepted.
- `occurred` — the risk event materialized.
- `closed` — resolved or expired.
- `dropped` — removed from the register.

`status` tracks the lifecycle state of the entry; `strategy` tracks the
chosen response. They are independent fields.
"""

#: A deliberately malformed document: the mitigation list drops `accept`
#: entirely and duplicates `reduce` instead, so its *set* of strategy
#: words no longer matches the intro list's, and
#: `Tara._validate_mitigation_matches_strategies` rejects it.
_MITIGATION_WRONG_STRATEGY_TEXT = """# TARA risk-response strategies for `rsk` documents

`rsk` documents (risk register entries) carry a mandatory `## Strategy`
section with exactly one lowercase word naming the TARA response chosen for
the risk. **TARA** is the risk-response framework: **T**ransfer, **A**ccept,
**R**educe, **A**void. Only the four valid words below are accepted by the
schema — anything else (including the TARRA-era words `tolerate`, `assign`,
`recover`, or any capitalized/compound variant) is a validation error:

- `transfer`
- `accept`
- `reduce`
- `avoid`

## When to apply each strategy

Read the risk's matrix coordinates (`## Initial Assessment`, see the risk
matrix document) to pick a strategy:

- **Low probability / high impact → `transfer`**
  The risk is unlikely but would be severe if it hit.
- **High probability / high impact → `avoid`**
  The risk is both likely and severe.
- **High probability / low impact → `reduce`**
  The risk is likely but the consequence is bounded.
- **Low probability / low impact → `accept`**
  The risk is unlikely and bounded.

The four quadrants are a guideline, not a rule — the documented
rationale of the choice matters more than the quadrant label.

## Interaction with `## Mitigation`

`## Mitigation` is the treatment section between the two assessments.

- `reduce`: concrete measures are mandatory.
- `transfer`: name the transfer mechanism.
- `avoid`: describe what is eliminated.
- `reduce`: duplicated instead of naming `accept`.

## Interaction with the frontmatter `status`

The `rsk` frontmatter `status` is a six-value lifecycle:

- `open` — identified and monitored; no treatment decided or started yet.
- `mitigating` — treatment is in progress.
- `accepted` — the residual risk is formally accepted.
- `occurred` — the risk event materialized.
- `closed` — resolved or expired.
- `dropped` — removed from the register.

`status` tracks the lifecycle state of the entry; `strategy` tracks the
chosen response. They are independent fields.
"""

#: A deliberately malformed document: the status list has only 5 of the
#: required 6 values (`occurred` dropped entirely), so
#: `StatusInteraction.items`'s `min_length=6`/`max_length=6` constraint
#: rejects it.
_WRONG_STATUS_COUNT_TEXT = """# TARA risk-response strategies for `rsk` documents

`rsk` documents (risk register entries) carry a mandatory `## Strategy`
section with exactly one lowercase word naming the TARA response chosen for
the risk. **TARA** is the risk-response framework: **T**ransfer, **A**ccept,
**R**educe, **A**void. Only the four valid words below are accepted by the
schema — anything else (including the TARRA-era words `tolerate`, `assign`,
`recover`, or any capitalized/compound variant) is a validation error:

- `transfer`
- `accept`
- `reduce`
- `avoid`

## When to apply each strategy

Read the risk's matrix coordinates (`## Initial Assessment`, see the risk
matrix document) to pick a strategy:

- **Low probability / high impact → `transfer`**
  The risk is unlikely but would be severe if it hit.
- **High probability / high impact → `avoid`**
  The risk is both likely and severe.
- **High probability / low impact → `reduce`**
  The risk is likely but the consequence is bounded.
- **Low probability / low impact → `accept`**
  The risk is unlikely and bounded.

The four quadrants are a guideline, not a rule — the documented
rationale of the choice matters more than the quadrant label.

## Interaction with `## Mitigation`

`## Mitigation` is the treatment section between the two assessments.

- `reduce`: concrete measures are mandatory.
- `transfer`: name the transfer mechanism.
- `avoid`: describe what is eliminated.
- `accept`: write `none` — acceptance means no treatment is taken.

## Interaction with the frontmatter `status`

The `rsk` frontmatter `status` is a six-value lifecycle:

- `open` — identified and monitored; no treatment decided or started yet.
- `mitigating` — treatment is in progress.
- `accepted` — the residual risk is formally accepted.
- `closed` — resolved or expired.
- `dropped` — removed from the register.

`status` tracks the lifecycle state of the entry; `strategy` tracks the
chosen response. They are independent fields.
"""

#: A deliberately malformed document: the status list has 6 values, but
#: one (`unknown`) is not in the closed vocabulary (`occurred` was
#: renamed), so `StatusInteraction._validate_status_values` rejects it.
_WRONG_STATUS_VALUES_TEXT = """# TARA risk-response strategies for `rsk` documents

`rsk` documents (risk register entries) carry a mandatory `## Strategy`
section with exactly one lowercase word naming the TARA response chosen for
the risk. **TARA** is the risk-response framework: **T**ransfer, **A**ccept,
**R**educe, **A**void. Only the four valid words below are accepted by the
schema — anything else (including the TARRA-era words `tolerate`, `assign`,
`recover`, or any capitalized/compound variant) is a validation error:

- `transfer`
- `accept`
- `reduce`
- `avoid`

## When to apply each strategy

Read the risk's matrix coordinates (`## Initial Assessment`, see the risk
matrix document) to pick a strategy:

- **Low probability / high impact → `transfer`**
  The risk is unlikely but would be severe if it hit.
- **High probability / high impact → `avoid`**
  The risk is both likely and severe.
- **High probability / low impact → `reduce`**
  The risk is likely but the consequence is bounded.
- **Low probability / low impact → `accept`**
  The risk is unlikely and bounded.

The four quadrants are a guideline, not a rule — the documented
rationale of the choice matters more than the quadrant label.

## Interaction with `## Mitigation`

`## Mitigation` is the treatment section between the two assessments.

- `reduce`: concrete measures are mandatory.
- `transfer`: name the transfer mechanism.
- `avoid`: describe what is eliminated.
- `accept`: write `none` — acceptance means no treatment is taken.

## Interaction with the frontmatter `status`

The `rsk` frontmatter `status` is a six-value lifecycle:

- `open` — identified and monitored; no treatment decided or started yet.
- `mitigating` — treatment is in progress.
- `accepted` — the residual risk is formally accepted.
- `unknown` — the risk event materialized.
- `closed` — resolved or expired.
- `dropped` — removed from the register.

`status` tracks the lifecycle state of the entry; `strategy` tracks the
chosen response. They are independent fields.
"""


class TestParseTara(unittest.TestCase):
    """Tests for `parse_tara` against the packaged TARA guidance data."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read_packaged_text("rsk", "tara", "md")

    def test_returns_tara_instance(self):
        """The parser must return a `Tara` instance."""
        result = parse_tara(self.text)
        self.assertIsInstance(result, Tara)

    def test_has_four_strategies(self):
        """Exactly 4 intro strategy bullets."""
        result = parse_tara(self.text)
        self.assertEqual(len(result.strategies), 4)

    def test_strategy_words_in_order(self):
        """The 4 strategy words must be exactly the TARA vocabulary, in the intro's own order."""
        result = parse_tara(self.text)
        words = [item.strategy for item in result.strategies]
        self.assertEqual(words, ["transfer", "accept", "reduce", "avoid"])

    def test_has_four_quadrant_items_matching_by_set(self):
        """Exactly 4 quadrant bullets, naming the same 4 strategy words as a set (order may differ)."""
        result = parse_tara(self.text)
        self.assertEqual(len(result.when_to_apply.items), 4)
        strategy_words = {item.strategy for item in result.strategies}
        quadrant_words = {item.strategy for item in result.when_to_apply.items}
        self.assertEqual(quadrant_words, strategy_words)

    def test_has_four_mitigation_items_matching_by_set(self):
        """Exactly 4 mitigation bullets, naming the same 4 strategy words as a set (order may differ)."""
        result = parse_tara(self.text)
        self.assertEqual(len(result.mitigation.items), 4)
        strategy_words = {item.strategy for item in result.strategies}
        mitigation_words = {item.strategy for item in result.mitigation.items}
        self.assertEqual(mitigation_words, strategy_words)

    def test_status_values_in_order(self):
        """The 6 status values must be exactly the closed lifecycle vocabulary, in order."""
        result = parse_tara(self.text)
        values = [item.status for item in result.status.items]
        self.assertEqual(
            values,
            ["open", "mitigating", "accepted", "occurred", "closed", "dropped"],
        )

    def test_raises_on_missing_strategy(self):
        """A document with only 3 of the 4 required intro strategy bullets must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_tara(_MISSING_STRATEGY_TEXT)

    def test_raises_on_quadrant_set_mismatch(self):
        """A quadrant list whose strategy-word set doesn't match the intro list's must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_tara(_QUADRANT_MISSING_STRATEGY_TEXT)

    def test_raises_on_mitigation_set_mismatch(self):
        """A mitigation list whose strategy-word set doesn't match the intro list's must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_tara(_MITIGATION_WRONG_STRATEGY_TEXT)

    def test_raises_on_wrong_status_count(self):
        """A status list with only 5 of the required 6 values must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_tara(_WRONG_STATUS_COUNT_TEXT)

    def test_raises_on_wrong_status_values(self):
        """A status list whose values are not exactly the closed 6-value vocabulary must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_tara(_WRONG_STATUS_VALUES_TEXT)


if __name__ == "__main__":
    unittest.main()
