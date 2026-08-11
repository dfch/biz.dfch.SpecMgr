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

"""Model tree + integration test for `tests/feat-5-md-model-parser/uc_example.md`.

`uc_example.md` is a full, realistic Alistair-Cockburn-style "fully dressed"
use case, exercising the `MarkdownStr`/`MarkdownSection` framework
(`biz.dfch.specmgr.models.md`) against a document far larger than
`various_models.py`'s hand-built `MainDocument` fixture: three heading
levels, ~15 fixed h3 fields under `Characteristic Information`, and a mix of
required and `Optional[...]` sections (see `feat-5-md-model-parser`'s
`from_text` optional-field support).

Two things the document has that this model tree deliberately does *not*
attempt to represent structurally:

- A YAML frontmatter block (`---\\n...\\n---`) before the `# Buy Goods`
  heading. `mdformat.text()` is CommonMark-only and mangles it (it does not
  understand frontmatter), which breaks `MarkdownStr`'s
  `text == mdformat.text(text)` invariant. `frontmatter.loads(text).content`
  (the `python-frontmatter` package, already a project dependency and
  already used the same way by `models.adr.v1.parser`/`uc.models.v1.parser`)
  strips it before any `MarkdownStr` code ever sees the text -- frontmatter
  parsing is a separate concern, out of scope for this generic markdown-body
  framework, so this test only ever looks at `.content`, never `.metadata`.
- `Extensions`/`Sub-Variations` (and, in other use cases, potentially
  `Open Issues`) contain a variable number of *dynamically named* h3
  sub-headings (e.g. `"3a. Company is out of one of the ordered items"`,
  `"4a. Buyer requests expedited shipping"`) that differ per use case. The
  framework has no "repeated/list section" concept yet (only fixed,
  statically declared fields), so these three are modelled as leaf
  `MarkdownSection2`s: `from_text` captures their entire heading+body extent
  verbatim in `_value`, and their internal h3 headings are inert text as far
  as the model is concerned -- exactly like `Notes`/`Assumptions` below, just
  with heading structure inside that nothing recurses into.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import frontmatter

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md.alias import alias
from biz.dfch.specmgr.models.md.alias_type import AliasType
from biz.dfch.specmgr.models.md.markdown_section1 import MarkdownSection1
from biz.dfch.specmgr.models.md.markdown_section2 import MarkdownSection2
from biz.dfch.specmgr.models.md.markdown_section3 import MarkdownSection3

# The real document lives under the older `feat-5-md-model-parser` scratch
# folder (see that folder's own, unrelated, non-`MarkdownStr`-based
# experiments) rather than under `tests/models/md/`; only the `.md` fixture
# itself is reused here.
_UC_EXAMPLE_PATH = Path(__file__).resolve().parents[2] / "feat-5-md-model-parser" / "uc_example.md"


# --- Characteristic Information's h3 fields, in document order -------------
#
# Every field's heading carries a "(required)"/"(optional)" suffix, so none
# of them can rely on `@alias`'s default `AliasType.SPACE_SEPARATED`
# auto-conversion (which would derive e.g. "Goal In Context", missing both
# the suffix and this document's lowercase "in") -- each needs an explicit
# `AliasType.LITERAL` alias matching the heading text verbatim.


@alias(value="Goal in Context (required)", type=AliasType.LITERAL)
class GoalInContext(MarkdownSection3): ...


@alias(value="Scope (required)", type=AliasType.LITERAL)
class Scope(MarkdownSection3): ...


@alias(value="Level (required)", type=AliasType.LITERAL)
class Level(MarkdownSection3): ...


@alias(value="Preconditions (required)", type=AliasType.LITERAL)
class Preconditions(MarkdownSection3): ...


@alias(value="Success End Condition (required)", type=AliasType.LITERAL)
class SuccessEndCondition(MarkdownSection3): ...


@alias(value="Failed End Condition (optional)", type=AliasType.LITERAL)
class FailedEndCondition(MarkdownSection3): ...


@alias(value="Primary Actor (required)", type=AliasType.LITERAL)
class PrimaryActor(MarkdownSection3): ...


@alias(value="Secondary Actors (optional)", type=AliasType.LITERAL)
class SecondaryActors(MarkdownSection3): ...


@alias(value="Trigger (required)", type=AliasType.LITERAL)
class Trigger(MarkdownSection3): ...


@alias(value="Frequency (optional)", type=AliasType.LITERAL)
class Frequency(MarkdownSection3): ...


@alias(value="Priority (optional)", type=AliasType.LITERAL)
class Priority(MarkdownSection3): ...


@alias(value="Performance Target (optional)", type=AliasType.LITERAL)
class PerformanceTarget(MarkdownSection3): ...


@alias(value="Channels to Primary Actor (optional)", type=AliasType.LITERAL)
class ChannelsToPrimaryActor(MarkdownSection3): ...


@alias(value="Channels to Secondary Actors (optional)", type=AliasType.LITERAL)
class ChannelsToSecondaryActors(MarkdownSection3): ...


@alias(value="Related Use Cases (optional)", type=AliasType.LITERAL)
class RelatedUseCases(MarkdownSection3): ...


@alias(value="Characteristic Information (required)", type=AliasType.LITERAL)
class CharacteristicInformation(MarkdownSection2):
    """All metadata/context about the use case: goal, scope, actors, triggers, etc.

    Field order mirrors the document's own h3 heading order exactly --
    `MarkdownStr.from_text` slices the section's body sequentially, one
    field at a time, so a field declared out of order would never find its
    heading where it expects it.
    """

    goal_in_context: GoalInContext
    scope: Scope
    level: Level
    preconditions: Preconditions
    success_end_condition: SuccessEndCondition
    failed_end_condition: FailedEndCondition | None = None
    primary_actor: PrimaryActor
    secondary_actors: SecondaryActors | None = None
    trigger: Trigger
    frequency: Frequency | None = None
    priority: Priority | None = None
    performance_target: PerformanceTarget | None = None
    channels_to_primary_actor: ChannelsToPrimaryActor | None = None
    channels_to_secondary_actors: ChannelsToSecondaryActors | None = None
    related_use_cases: RelatedUseCases | None = None


@alias(value="Main Success Scenario (required)", type=AliasType.LITERAL)
class MainSuccessScenario(MarkdownSection2):
    """The happy-path numbered steps. A leaf: no h3 sub-headings to decompose."""


@alias(value="Extensions (optional)", type=AliasType.LITERAL)
class Extensions(MarkdownSection2):
    """Alternative flows. A leaf: its h3 sub-headings are dynamic (see module docstring)."""


@alias(value="Sub-Variations (optional)", type=AliasType.LITERAL)
class SubVariations(MarkdownSection2):
    """Per-step technology variations. A leaf, for the same reason as `Extensions`."""


@alias(value="Open Issues (optional)", type=AliasType.LITERAL)
class OpenIssues(MarkdownSection2):
    """Open questions. A leaf: plain bullet list, no sub-headings at all."""


@alias(value="Notes (optional)", type=AliasType.LITERAL)
class Notes(MarkdownSection3): ...


@alias(value="Assumptions (optional)", type=AliasType.LITERAL)
class Assumptions(MarkdownSection3): ...


@alias(value="Related Information (optional)", type=AliasType.LITERAL)
class RelatedInformation(MarkdownSection2):
    """Free-form notes/assumptions, both individually optional."""

    notes: Notes | None = None
    assumptions: Assumptions | None = None


@alias(value=".+", type=AliasType.REGEX)
class UseCase(MarkdownSection1):
    """Top-level use case document: an h1 title plus the h2 sections above.

    Declares a permissive regex `@alias` rather than a fixed literal: a use
    case's title (`"Buy Goods"` here) is document-specific data, not
    something a reusable template class should pin down to one exact
    string. "No alias at all" defaults to `AliasType.SPACE_SEPARATED`'s
    derivation of the class name (`"UseCase"` -> `"Use Case"`, ADR
    832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.4.0) -- still a fixed value, not
    "accept anything" -- so accepting arbitrary titles must still be
    declared explicitly via the `.+` regex, same convention as
    `various_models.py`'s `MainDocument`.
    """

    characteristic_information: CharacteristicInformation
    main_success_scenario: MainSuccessScenario
    extensions: Extensions | None = None
    sub_variations: SubVariations | None = None
    open_issues: OpenIssues | None = None
    related_information: RelatedInformation | None = None


class TestUseCaseFromText(unittest.TestCase):
    """Integration test: parse the full, real `uc_example.md` fixture end-to-end."""

    @classmethod
    def setUpClass(cls) -> None:
        raw_text = _UC_EXAMPLE_PATH.read_text(encoding="utf-8")
        cls.body = format_text(frontmatter.loads(raw_text).content)

    def test_parses_title_and_top_level_sections(self) -> None:
        """The h1 title and all h2 sections (required and present-optional) are populated."""
        instance = UseCase.from_text(self.body)
        self.assertIsInstance(instance, UseCase)
        self.assertEqual(instance._value, "Buy Goods")

        self.assertIsInstance(instance.characteristic_information, CharacteristicInformation)
        self.assertIsInstance(instance.main_success_scenario, MainSuccessScenario)
        self.assertIsNotNone(instance.extensions)
        self.assertIsNotNone(instance.sub_variations)
        self.assertIsNotNone(instance.open_issues)
        self.assertIsNotNone(instance.related_information)

    def test_parses_all_characteristic_information_fields(self) -> None:
        """Every `Characteristic Information` h3 field is present in this fixture (none omitted)."""
        instance = UseCase.from_text(self.body)
        ci = instance.characteristic_information

        self.assertEqual(ci._value, "Characteristic Information (required)")
        self.assertIn("Buyer issues request directly", ci.goal_in_context._value)
        self.assertIn("Company (the system being designed", ci.scope._value)
        self.assertIn("Summary", ci.level._value)
        self.assertIn("We know Buyer", ci.preconditions._value)
        self.assertIn("Buyer has goods", ci.success_end_condition._value)
        self.assertIsNotNone(ci.failed_end_condition)
        self.assertIn("Buyer (any agent or computer", ci.primary_actor._value)
        self.assertIsNotNone(ci.secondary_actors)
        self.assertIn("Purchase request comes in", ci.trigger._value)
        self.assertIsNotNone(ci.frequency)
        self.assertIsNotNone(ci.priority)
        self.assertIsNotNone(ci.performance_target)
        self.assertIsNotNone(ci.channels_to_primary_actor)
        self.assertIsNotNone(ci.channels_to_secondary_actors)
        self.assertIsNotNone(ci.related_use_cases)

    def test_parses_related_information_sub_fields(self) -> None:
        """Both `Notes` and `Assumptions` are present in this fixture."""
        instance = UseCase.from_text(self.body)
        ri = instance.related_information
        assert ri is not None, type(ri)

        self.assertIsNotNone(ri.notes)
        self.assertIsNotNone(ri.assumptions)

    def test_round_trip_reproduces_the_source_document(self) -> None:
        """`str(instance)` reproduces the (frontmatter-stripped, mdformat-normalized) body."""
        instance = UseCase.from_text(self.body)
        self.assertEqual(str(instance), self.body)


if __name__ == "__main__":
    unittest.main()
