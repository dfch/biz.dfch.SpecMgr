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

"""Closed-set drift test of the packaged heading-mapping tables (feat-197-i18n Phase 150, ADR 38efdb66 item 4(c)).

The ADR promised a drift test that derives the closed set of fixed-text headings from the i18n-eligible domains'
document models and asserts every language table covers *exactly* that set. ``test_heading_table.py`` derives the set
(``_derive_canonical_headings``) and pins the "no invented headings" direction; this module pins the whole
contract for **every** table file shipped under ``general/data/headings/`` (so a future ``fr.json`` is covered
automatically, with no test change):

- the table's *values* equal the model-derived closed set exactly -- a heading added to (or removed from) a document
  model without the matching table edit fails here, naming the heading to add to (or drop from) the table;
- the values are pairwise distinct (also enforced by the loader at parse time);
- data-carrying heading patterns (``Option {N}:``, ``Step {N}:``, ``AC-{NNN} ({Method}):``, ``Extension {N}.``,
  ``Probability {1..5}``/``Impact {1..5}``, timestamp-led update entries, the ``sysrs`` H1 prefix) have no entry --
  neither as a key nor as a value (REQ-010) -- and no *translated* key may shadow a canonical heading.

Adding a language therefore means: add ``general/data/headings/<language>.json`` (flat ``<translated> -> <canonical>``
object covering exactly the set this test derives); the failure messages below say what is missing or surplus.
"""

from __future__ import annotations

import re
import typing
import unittest
from importlib import import_module, resources
from inspect import isclass

from biz.dfch.specmgr.general.models.heading_table import load_heading_table, reset_heading_table_cache
from biz.dfch.specmgr.models.md.alias_type import AliasType
from biz.dfch.specmgr.models.md.markdown_section import MarkdownSection

from .test_heading_table import (
    _DOCUMENT_MODEL_PACKAGES,
    _classify_regex,
    _concrete_types,
    _derive_canonical_headings,
)

#: The regex alias of every free-form H1 (``.+``): matches any text, so it cannot constrain a table entry.
_MATCH_ANYTHING = ".+"


def derive_heading_classes() -> tuple[set[str], dict[str, str]]:
    """Walk the twelve document models once and classify every section heading alias.

    Returns:
        ``(fixed, data_carrying)``: ``fixed`` is the closed set of canonical fixed-text headings (LITERAL,
        SPACE_SEPARATED, or REGEX without a free-text group, escaping undone); ``data_carrying`` maps each REGEX alias
        that carries data (free text, a closed-vocabulary value, a number, a timestamp) to the class that declares it.
    """
    # pylint: disable=protected-access
    fixed: set[str] = set()
    data_carrying: dict[str, str] = {}
    seen: set[type] = set()

    def visit(cls: type) -> None:
        if cls in seen or not isclass(cls) or not issubclass(cls, MarkdownSection):
            return
        seen.add(cls)
        metadata = getattr(cls, "_alias_metadata", None)
        if metadata is None:
            from biz.dfch.specmgr.models.md.alias_match import space_separated_name

            fixed.add(space_separated_name(cls.__name__))
        elif metadata["type"] == AliasType.REGEX:
            canonical = _classify_regex(str(metadata["value"]))
            if canonical is None:
                data_carrying[str(metadata["value"])] = cls.__name__
            else:
                fixed.add(canonical)
        else:
            fixed.add(str(metadata["value"]))
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
    return fixed, data_carrying


def shipped_languages() -> list[str]:
    """The language codes that have a packaged heading table (every ``<language>.json`` file)."""
    directory = resources.files("biz.dfch.specmgr.general") / "data" / "headings"
    result = sorted(entry.name[: -len(".json")] for entry in directory.iterdir() if entry.name.endswith(".json"))
    return result


def sample_data_heading(pattern: str) -> str | None:
    """A concrete heading text a data-carrying ``pattern`` accepts, for the patterns this suite knows how to sample."""
    samples = {
        r"^AC-(\d{3}) \((Demonstration|Test|Analysis|Inspection|Special)\): .+$": "AC-001 (Test): sample",
        r"^Extension \d+[a-z]?\. .+$": "Extension 1a. sample",
        r"^Impact [1-5]$": "Impact 3",
        r"^Option \d+: .+$": "Option 1: sample",
        r"^Probability [1-5]$": "Probability 3",
        r"^Step \d+: .+$": "Step 1: sample",
        r"^System Requirements Specification: .+$": "System Requirements Specification: sample",
        r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})(?: - | : ).+$": (
            "2026-10-30T15:07:15.000+01:00 - sample"
        ),
    }
    return samples.get(pattern)


class TestDerivation(unittest.TestCase):
    """The derivation itself: it agrees with the Phase 110 helper and finds the heading families the ADR names."""

    def test_the_closed_set_equals_the_phase_110_derivation(self):
        fixed, _data = derive_heading_classes()

        self.assertEqual(fixed, _derive_canonical_headings())
        self.assertGreater(len(fixed), 100)

    def test_the_data_carrying_families_are_the_ones_the_adr_names(self):
        _fixed, data = derive_heading_classes()

        families = {pattern for pattern in data if pattern != _MATCH_ANYTHING}

        self.assertEqual(
            {sample_data_heading(pattern) is not None for pattern in families},
            {True},
            f"a new data-carrying heading pattern needs a sample in sample_data_heading(): {sorted(families)}",
        )
        for needle in ("Option", "Step", "AC-", "Extension", "Probability", "Impact", "\\d{4}-\\d{2}-\\d{2}"):
            self.assertTrue(any(needle in pattern for pattern in families), f"no data-carrying pattern with {needle!r}")

    def test_every_sample_matches_its_own_pattern(self):
        _fixed, data = derive_heading_classes()
        for pattern in data:
            sample = sample_data_heading(pattern)
            if sample is not None:
                with self.subTest(pattern=pattern):
                    self.assertRegex(sample, pattern)

    def test_at_least_one_table_ships(self):
        self.assertIn("de", shipped_languages())


class TestEveryShippedTableCoversTheClosedSetExactly(unittest.TestCase):
    """ADR 38efdb66 item 4(c): each ``general/data/headings/<language>.json`` covers exactly the model-derived set."""

    def setUp(self) -> None:
        reset_heading_table_cache()
        self.addCleanup(reset_heading_table_cache)
        self.fixed, self.data_carrying = derive_heading_classes()

    def test_the_values_equal_the_derived_closed_set_with_an_actionable_diff(self):
        for language in shipped_languages():
            with self.subTest(language=language):
                table = load_heading_table(language)
                values = set(table.values())

                missing = sorted(self.fixed - values)
                surplus = sorted(values - self.fixed)

                self.assertEqual(
                    (missing, surplus),
                    ([], []),
                    f"{language}.json drifted from the document models. "
                    f"Add an entry (<translated>: <canonical>) for each MISSING canonical heading: {missing}. "
                    f"Remove (or fix the canonical value of) each entry whose canonical heading no model declares "
                    f"any more: {surplus}.",
                )

    def test_every_canonical_heading_has_exactly_one_translation(self):
        """The values are pairwise distinct: a heading cannot have two German spellings, two headings never share one."""
        for language in shipped_languages():
            with self.subTest(language=language):
                table = load_heading_table(language)
                by_value: dict[str, list[str]] = {}
                for key, value in table.items():
                    by_value.setdefault(value, []).append(key)
                duplicated = {value: keys for value, keys in by_value.items() if len(keys) > 1}

                self.assertEqual(duplicated, {}, f"{language}.json maps several keys to one canonical heading")
                self.assertEqual(len(table), len(self.fixed))

    def test_no_data_carrying_heading_has_an_entry(self):
        """REQ-010: neither a key nor a value of any table matches a data-carrying heading pattern."""
        for language in shipped_languages():
            with self.subTest(language=language):
                table = load_heading_table(language)
                texts = {*table.keys(), *table.values()}
                offenders = sorted(
                    f"{text!r} (pattern {pattern!r})"
                    for pattern in self.data_carrying
                    if pattern != _MATCH_ANYTHING
                    for text in texts
                    if re.fullmatch(pattern, text)
                )

                self.assertEqual(
                    offenders,
                    [],
                    f"{language}.json holds entries for data-carrying headings; their schema-constant tokens "
                    f"must never be translated (REQ-010)",
                )

    def test_a_sample_of_every_data_carrying_heading_passes_through_every_table_unchanged(self):
        """The same fact stated through the table's own lookup: ``table.get(text, text)`` is the identity."""
        for language in shipped_languages():
            table = load_heading_table(language)
            for pattern in self.data_carrying:
                sample = sample_data_heading(pattern)
                if sample is None:
                    continue
                with self.subTest(language=language, sample=sample):
                    self.assertEqual(table.get(sample, sample), sample)

    def test_no_translated_key_shadows_a_canonical_heading(self):
        """A key equal to a *different* canonical heading would silently rewrite canonical English text in a
        translated document (canonical English must stay valid in every language, ADR item 5)."""
        for language in shipped_languages():
            with self.subTest(language=language):
                table = load_heading_table(language)
                shadowing = sorted(key for key, value in table.items() if key in self.fixed and key != value)
                identity = sorted(key for key, value in table.items() if key == value)

                self.assertEqual(shadowing, [], f"{language}.json keys that are another canonical heading")
                self.assertEqual(identity, [], f"{language}.json identity entries (a no-op translation)")

    def test_keys_and_values_are_plain_heading_text(self):
        """Heading text only: no leading ``#`` markers, no surrounding whitespace, never empty (ADR item 3)."""
        for language in shipped_languages():
            with self.subTest(language=language):
                for key, value in load_heading_table(language).items():
                    for text in (key, value):
                        self.assertEqual(text, text.strip())
                        self.assertTrue(text)
                        self.assertFalse(text.startswith("#"), text)


if __name__ == "__main__":
    unittest.main()
