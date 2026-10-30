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

"""Tests for ``general.models.translation_drift`` (the pure heading-skeleton comparison and the staleness comparison
of the ``check_translation_drift`` tool, feat-197-i18n Phase 140, REQ-014, ACC-009).

Covers: the structural-key rule (table mapping, the data-carrying token reduction, the update-entry exclusion, the
ancestor-path keys, occurrence disambiguation, h1/fence/prose invisibility), the diff (missing/extra/reordered, the
LCS-based single-move reorder), the staleness comparison (parsed offset-aware datetimes, mixed separators/offsets,
the equal boundary, missing/unparseable/offset-less values), and the **alias pin**: every free-text ``@alias`` REGEX
of the eleven i18n-eligible domains' document models is covered by a token rule (a new data-carrying heading in any
domain fails this test until the rule table learns it).
"""

from __future__ import annotations

import re
import typing
import unittest
from datetime import datetime, timezone
from importlib import import_module
from inspect import isclass

from biz.dfch.specmgr.general.models.heading_table import load_heading_table
from biz.dfch.specmgr.general.models.translation_drift import (
    DriftFinding,
    SkeletonEntry,
    TranslationDriftResult,
    _canonical_token,
    check_staleness,
    compare_skeletons,
    heading_skeleton,
)
from biz.dfch.specmgr.models.md.markdown_section import MarkdownSection
from biz.dfch.specmgr.models.md.markdown_section1 import MarkdownSection1

from .test_heading_table import _DOCUMENT_MODEL_PACKAGES, _classify_regex, _concrete_types

_DE = load_heading_table("de")


def _tokens(skeleton: list[SkeletonEntry]) -> list[str]:
    return [entry.token for entry in skeleton]


def _paths(skeleton: list[SkeletonEntry]) -> list[str]:
    return [entry.path for entry in skeleton]


class TestCanonicalToken(unittest.TestCase):
    """The structural-key rule per heading (table mapping, token reduction, update-entry exclusion)."""

    def test_en_heading_is_its_own_token(self):
        self.assertEqual(_canonical_token("Decision Outcome", None), "Decision Outcome")

    def test_translated_heading_maps_to_canonical_through_the_table(self):
        self.assertEqual(_canonical_token("Entscheidungsergebnis", _DE), "Decision Outcome")

    def test_unmapped_heading_passes_through(self):
        self.assertEqual(_canonical_token("Decision Outcome", _DE), "Decision Outcome")
        self.assertEqual(_canonical_token("Völlig Unbekannt", _DE), "Völlig Unbekannt")

    def test_data_carrying_headings_reduce_to_their_schema_constant_token(self):
        for text, expected in (
            ("Option 1: Keep it", "Option 1:"),
            ("Option 12: Behalte es-DE", "Option 12:"),
            ("Step 3: Do it", "Step 3:"),
            ("Extension 3a. Something else", "Extension 3a."),
            ("Extension 12. Something else", "Extension 12."),
            ("AC-001 (Test): Does the thing", "AC-001 (Test):"),
            ("AC-014 (Demonstration): Zeigt es", "AC-014 (Demonstration):"),
        ):
            with self.subTest(text=text):
                self.assertEqual(_canonical_token(text, _DE), expected)

    def test_a_changed_token_changes_the_key(self):
        self.assertNotEqual(_canonical_token("Option 1: x", None), _canonical_token("Option 2: x", None))
        self.assertNotEqual(_canonical_token("AC-001 (Test): x", None), _canonical_token("AC-001 (Analysis): x", None))

    def test_whole_token_headings_compare_as_a_whole(self):
        self.assertEqual(_canonical_token("Probability 3", _DE), "Probability 3")
        self.assertNotEqual(_canonical_token("Probability 3", _DE), _canonical_token("Probability 4", _DE))

    def test_update_entries_are_excluded(self):
        for text in (
            "2026-10-30T15:05:00.000+01:00 - Created",
            "2026-10-30 15:05:00.000Z : Angelegt",
            "2026-10-30T15:05:00.000-05:00 - Anything goes: here",
        ):
            with self.subTest(text=text):
                self.assertIsNone(_canonical_token(text, _DE))

    def test_a_date_only_heading_is_not_an_update_entry(self):
        self.assertEqual(_canonical_token("2026-10-30 - Created", None), "2026-10-30 - Created")


class TestHeadingSkeleton(unittest.TestCase):
    """The skeleton of a raw body: h1/fence/prose invisibility, ancestors, positions, duplicates."""

    def test_h1_and_prose_are_not_part_of_the_skeleton(self):
        body = "# A Title\n\nSome prose, with a # in it.\n\n## Context and Problem Statement\n\nText\n"

        result = heading_skeleton(body, None)

        self.assertEqual(_tokens(result), ["Context and Problem Statement"])
        self.assertEqual([e.level for e in result], [2])
        self.assertEqual([e.position for e in result], [1])

    def test_fenced_headings_are_not_headings(self):
        body = "# T\n\n## Real\n\n```\n## Not A Heading\n```\n\n~~~\n### Nor This\n~~~\n\n## Also Real\n"

        result = heading_skeleton(body, None)

        self.assertEqual(_tokens(result), ["Real", "Also Real"])

    def test_text_is_the_on_disk_text_and_token_the_canonical_one(self):
        body = "# T\n\n## Entscheidungsergebnis\n\n### Option 1: Behalte es\n\nx\n"

        result = heading_skeleton(body, _DE)

        self.assertEqual([e.text for e in result], ["Entscheidungsergebnis", "Option 1: Behalte es"])
        self.assertEqual(_tokens(result), ["Decision Outcome", "Option 1:"])

    def test_keys_carry_the_canonical_ancestor_path(self):
        body = (
            "# T\n\n## Initiale Bewertung\n\n### Probability 3\n\n### Impact 2\n\n"
            "## Residuale Bewertung\n\n### Probability 1\n\n### Impact 1\n"
        )

        result = heading_skeleton(body, _DE)

        self.assertEqual(
            _paths(result),
            [
                "Initial Assessment",
                "Initial Assessment > Probability 3",
                "Initial Assessment > Impact 2",
                "Residual Assessment",
                "Residual Assessment > Probability 1",
                "Residual Assessment > Impact 1",
            ],
        )
        self.assertEqual(len({e.key for e in result}), 6)

    def test_a_repeated_heading_under_the_same_parent_gets_an_occurrence_suffix(self):
        body = "# T\n\n## A\n\n### Same\n\n### Same\n"

        result = heading_skeleton(body, None)

        self.assertEqual([e.key for e in result], ["A", "A > Same", "A > Same#2"])

    def test_update_entries_and_everything_nested_in_them_are_excluded(self):
        body = (
            "# T\n\n## Updates\n\n### 2026-10-30T15:05:00.000+01:00 - Created\n\ntext\n\n"
            "#### Nested Heading In Entry\n\n### 2026-10-31T15:05:00.000+01:00 - Again\n\n## More Information\n"
        )

        result = heading_skeleton(body, None)

        self.assertEqual(_tokens(result), ["Updates", "More Information"])

    def test_sibling_after_an_excluded_entry_is_not_excluded(self):
        body = "# T\n\n## Updates\n\n### 2026-10-30T15:05:00.000+01:00 - Created\n\n### Normal Child\n"

        result = heading_skeleton(body, None)

        self.assertEqual(_tokens(result), ["Updates", "Normal Child"])

    def test_empty_body_has_an_empty_skeleton(self):
        self.assertEqual(heading_skeleton("", None), [])


class TestCompareSkeletons(unittest.TestCase):
    """missing / extra / reordered, and the in-sync case."""

    @staticmethod
    def _skeleton(headings: list[str]) -> list[SkeletonEntry]:
        body = "# T\n\n" + "\n\n".join(f"## {heading}" for heading in headings) + "\n"
        return heading_skeleton(body, None)

    def test_identical_skeletons_have_no_findings(self):
        skeleton = self._skeleton(["A", "B", "C"])

        self.assertEqual(compare_skeletons(skeleton, skeleton), [])

    def test_a_missing_section(self):
        result = compare_skeletons(self._skeleton(["A", "B", "C"]), self._skeleton(["A", "C"]))

        self.assertEqual(
            [(f.kind, f.heading, f.source_position, f.variant_position) for f in result], [("missing", "B", 2, None)]
        )
        self.assertEqual(result[0].level, 2)
        self.assertEqual(result[0].text, "B")

    def test_an_extra_section(self):
        result = compare_skeletons(self._skeleton(["A", "C"]), self._skeleton(["A", "X", "C"]))

        self.assertEqual(
            [(f.kind, f.heading, f.source_position, f.variant_position) for f in result], [("extra", "X", None, 2)]
        )

    def test_a_single_moved_section_is_one_reordered_finding(self):
        result = compare_skeletons(self._skeleton(["A", "B", "C", "D"]), self._skeleton(["A", "C", "D", "B"]))

        self.assertEqual(
            [(f.kind, f.heading, f.source_position, f.variant_position) for f in result], [("reordered", "B", 2, 4)]
        )

    def test_a_swapped_pair_is_reported_once(self):
        result = compare_skeletons(self._skeleton(["A", "B", "C"]), self._skeleton(["B", "A", "C"]))

        self.assertEqual([f.kind for f in result], ["reordered"])

    def test_missing_extra_and_reordered_are_ordered_missing_extra_reordered(self):
        result = compare_skeletons(self._skeleton(["A", "B", "C", "D"]), self._skeleton(["D", "X", "A", "C"]))

        self.assertEqual([f.kind for f in result], ["missing", "extra", "reordered"])
        self.assertEqual([f.heading for f in result], ["B", "X", "D"])

    def test_every_finding_carries_a_human_readable_message(self):
        result = compare_skeletons(self._skeleton(["A", "B"]), self._skeleton(["B", "X"]))

        for finding in result:
            with self.subTest(kind=finding.kind):
                self.assertTrue(finding.message.strip())

    def test_translated_free_text_is_not_a_finding(self):
        en = heading_skeleton("# T\n\n## Considered Options\n\n### Option 1: Foo\n\n### Option 2: Bar\n", None)
        de = heading_skeleton("# T\n\n## Betrachtete Optionen\n\n### Option 1: Foo-DE\n\n### Option 2: Balken\n", _DE)

        self.assertEqual(compare_skeletons(en, de), [])

    def test_a_dropped_option_is_missing(self):
        en = heading_skeleton("# T\n\n## Considered Options\n\n### Option 1: Foo\n\n### Option 2: Bar\n", None)
        de = heading_skeleton("# T\n\n## Betrachtete Optionen\n\n### Option 1: Foo-DE\n", _DE)

        result = compare_skeletons(en, de)

        self.assertEqual([(f.kind, f.path) for f in result], [("missing", "Considered Options > Option 2:")])

    def test_a_changed_closed_vocabulary_token_is_a_missing_extra_pair(self):
        en = heading_skeleton("# T\n\n## Initial Assessment\n\n### Probability 3\n\n### Impact 2\n", None)
        de = heading_skeleton("# T\n\n## Initiale Bewertung\n\n### Probability 4\n\n### Impact 2\n", _DE)

        result = compare_skeletons(en, de)

        self.assertEqual(
            [(f.kind, f.path) for f in result],
            [("missing", "Initial Assessment > Probability 3"), ("extra", "Initial Assessment > Probability 4")],
        )

    def test_a_mistranslated_heading_is_a_missing_extra_pair_carrying_what_the_translator_wrote(self):
        en = heading_skeleton("# T\n\n## Decision Outcome\n", None)
        de = heading_skeleton("# T\n\n## Entscheidungsresultat\n", _DE)

        result = compare_skeletons(en, de)

        self.assertEqual(
            [(f.kind, f.heading, f.text) for f in result],
            [
                ("missing", "Decision Outcome", "Decision Outcome"),
                ("extra", "Entscheidungsresultat", "Entscheidungsresultat"),
            ],
        )


class TestCheckStaleness(unittest.TestCase):
    """The staleness comparison: parsed offset-aware datetimes, never strings."""

    def test_source_newer_is_stale_with_the_signed_delta(self):
        result = check_staleness("2026-10-30T15:05:01.000+01:00", "2026-10-30T15:05:00.000+01:00")

        self.assertTrue(result.stale)
        self.assertEqual(result.source_ahead_by_seconds, 1.0)
        self.assertIsNone(result.error)
        self.assertEqual(result.source_updated, "2026-10-30T15:05:01.000+01:00")
        self.assertEqual(result.variant_updated, "2026-10-30T15:05:00.000+01:00")

    def test_equal_is_not_stale(self):
        result = check_staleness("2026-10-30T15:05:00.000+01:00", "2026-10-30T15:05:00.000+01:00")

        self.assertFalse(result.stale)
        self.assertEqual(result.source_ahead_by_seconds, 0.0)
        self.assertIsNone(result.error)

    def test_older_is_not_stale_and_the_delta_is_negative(self):
        result = check_staleness("2026-10-30T15:05:00.000+01:00", "2026-10-30T15:05:02.500+01:00")

        self.assertFalse(result.stale)
        self.assertEqual(result.source_ahead_by_seconds, -2.5)

    def test_one_millisecond_newer_is_stale(self):
        result = check_staleness("2026-10-30T15:05:00.001+01:00", "2026-10-30T15:05:00.000+01:00")

        self.assertTrue(result.stale)

    def test_t_and_space_separators_compare_equal(self):
        result = check_staleness("2026-10-30 15:05:00.000+01:00", "2026-10-30T15:05:00.000+01:00")

        self.assertFalse(result.stale)
        self.assertEqual(result.source_ahead_by_seconds, 0.0)

    def test_different_offsets_compare_as_instants_not_as_strings(self):
        # 15:05 +01:00 == 14:05Z: as strings "2026-10-30T15:05..." > "2026-10-30T14:30...", as instants the source is older
        older_source = check_staleness("2026-10-30T15:05:00.000+01:00", "2026-10-30T14:30:00.000Z")
        newer_source = check_staleness("2026-10-30T14:30:00.000Z", "2026-10-30T15:05:00.000+01:00")

        self.assertFalse(older_source.stale)
        self.assertEqual(older_source.source_ahead_by_seconds, -1500.0)
        self.assertTrue(newer_source.stale)
        self.assertEqual(newer_source.source_ahead_by_seconds, 1500.0)

    def test_z_equals_zero_offset(self):
        result = check_staleness("2026-10-30T14:05:00.000Z", "2026-10-30T15:05:00.000+01:00")

        self.assertFalse(result.stale)
        self.assertEqual(result.source_ahead_by_seconds, 0.0)

    def test_pyyaml_coerced_datetimes_are_accepted(self):
        result = check_staleness(
            datetime(2026, 10, 30, 14, 5, 1, tzinfo=timezone.utc), datetime(2026, 10, 30, 14, 5, 0, tzinfo=timezone.utc)
        )

        self.assertTrue(result.stale)

    def test_missing_timestamp_is_reported_not_raised(self):
        for source, variant, which in (
            (None, "2026-10-30T15:05:00.000Z", "source"),
            ("2026-10-30T15:05:00.000Z", None, "variant"),
        ):
            with self.subTest(which=which):
                result = check_staleness(source, variant)

                self.assertFalse(result.stale)
                self.assertIsNone(result.source_ahead_by_seconds)
                self.assertIn(which, result.error or "")
                self.assertIn("missing", result.error or "")

    def test_unparseable_timestamp_is_reported_not_raised(self):
        result = check_staleness("not a timestamp", "2026-10-30T15:05:00.000Z")

        self.assertFalse(result.stale)
        self.assertIsNone(result.source_ahead_by_seconds)
        self.assertIn("not a valid ISO 8601", result.error or "")
        self.assertEqual(result.source_updated, "not a timestamp")

    def test_offset_less_timestamp_is_reported_not_compared(self):
        result = check_staleness("2026-10-30T15:05:00.000", "2026-10-30T15:05:00.000Z")

        self.assertFalse(result.stale)
        self.assertIn("no UTC offset", result.error or "")

    def test_non_timestamp_type_is_reported(self):
        result = check_staleness(12345, "2026-10-30T15:05:00.000Z")

        self.assertFalse(result.stale)
        self.assertIn("not a timestamp", result.error or "")

    def test_both_problems_are_reported_together(self):
        result = check_staleness(None, "garbage")

        self.assertIn("source", result.error or "")
        self.assertIn("variant", result.error or "")


class TestResultModels(unittest.TestCase):
    """The result models serialize (the MCP wire shape)."""

    def test_unparseable_finding_round_trips(self):
        finding = DriftFinding(kind="unparseable", language="de", error="boom", message="the 'de' document fails")

        self.assertEqual(DriftFinding.model_validate_json(finding.model_dump_json()), finding)
        self.assertIsNone(finding.heading)

    def test_result_round_trips(self):
        result = TranslationDriftResult(
            type="dec",
            id="x",
            source_language="en",
            language="de",
            source_path="/a",
            variant_path="/b",
            in_sync=True,
            structural=[],
            stale=False,
            source_updated="2026-10-30T15:05:00.000Z",
            variant_updated="2026-10-30T15:05:00.000Z",
            source_ahead_by_seconds=0.0,
            staleness_error=None,
        )

        self.assertEqual(TranslationDriftResult.model_validate_json(result.model_dump_json()), result)


#: Every data-carrying (free-text or value-carrying) REGEX ``@alias`` of the eleven i18n-eligible domains' non-h1
#: sections, mapped to a sample heading that fullmatches it. The drift check's token rules must cover each: a
#: ``(free-text)`` row reduces to its schema-constant token, a ``(whole token)`` row compares as a whole (its text is
#: entirely schema-constant), the update-entry row is excluded. A NEW data-carrying alias in any domain fails
#: ``test_every_data_carrying_alias_is_covered`` until it is added here and to the rule table of
#: ``translation_drift`` (ADR 38efdb66 item 3 closedness).
_COVERED_ALIASES: dict[str, tuple[str, str | None]] = {
    r"^Option \d+: .+$": ("Option 7: Whatever", "Option 7:"),
    r"^Step \d+: .+$": ("Step 2: Whatever", "Step 2:"),
    r"^Extension \d+[a-z]?\. .+$": ("Extension 4b. Whatever", "Extension 4b."),
    r"^AC-(\d{3}) \((Demonstration|Test|Analysis|Inspection|Special)\): .+$": (
        "AC-003 (Inspection): Whatever",
        "AC-003 (Inspection):",
    ),
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})(?: - | : ).+$": (
        "2026-10-30T15:05:00.000+01:00 - Whatever",
        None,
    ),
    r"^Probability [1-5]$": ("Probability 5", "Probability 5"),
    r"^Impact [1-5]$": ("Impact 1", "Impact 1"),
}


def _walk_non_h1_regex_aliases() -> set[str]:
    """The REGEX alias patterns of the document models' non-h1 sections that are not plain fixed text."""
    seen: set[type] = set()
    found: set[str] = set()

    def visit(cls: type) -> None:
        if cls in seen or not isclass(cls) or not issubclass(cls, MarkdownSection):
            return
        seen.add(cls)
        metadata = getattr(cls, "_alias_metadata", None)
        if (
            metadata is not None
            and str(metadata["type"].name) == "REGEX"
            and not issubclass(cls, MarkdownSection1)
            and _classify_regex(str(metadata["value"])) is None
        ):
            found.add(str(metadata["value"]))
        hints = typing.get_type_hints(cls)
        for field_name in cls.model_fields:
            for concrete in _concrete_types(hints[field_name]):
                visit(concrete)

    for package in _DOCUMENT_MODEL_PACKAGES.values():
        module = import_module(package)
        for name in dir(module):
            obj = getattr(module, name)
            fields = getattr(obj, "model_fields", None)
            if (
                isclass(obj)
                and name.endswith("Document")
                and fields is not None
                and "frontmatter" in fields
                and "body" in fields
            ):
                for concrete in _concrete_types(typing.get_type_hints(obj)["body"]):
                    visit(concrete)
    return found


class TestAliasPin(unittest.TestCase):
    """The token rules cover exactly the models' data-carrying heading aliases (drift pin)."""

    def test_every_data_carrying_alias_is_covered(self):
        walked = _walk_non_h1_regex_aliases()

        self.assertEqual(
            walked, set(_COVERED_ALIASES), "a data-carrying heading alias changed -- update the drift rules"
        )

    def test_each_sample_matches_its_alias_and_the_rule_yields_the_expected_token(self):
        for pattern, (sample, expected) in _COVERED_ALIASES.items():
            with self.subTest(pattern=pattern):
                self.assertIsNotNone(re.fullmatch(pattern, sample), f"{sample!r} does not match {pattern!r}")
                self.assertEqual(_canonical_token(sample, _DE), expected)


if __name__ == "__main__":
    unittest.main()
