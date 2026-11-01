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

"""Tests for ``general.models.heading_table`` (the per-language heading-mapping table loader and the
fence-aware normalization pre-pass, feat-197-i18n Phase 110, ADR 38efdb66 items 3/4/5).

Covers: the lazy once-per-process load (the ``heading_table_path`` seam), the
loader's rejection channels (missing table for a shape-valid code, malformed
JSON, non-``str -> str`` objects, non-pairwise-distinct values), the
omitted/EN-aware ``resolve_heading_table`` entry point, the pre-pass's
fence-aware heading rewriting (`` ` `` / ``~~~`` fences, non-heading lines
byte-identical), and the ``de.json`` packaged table's basic integrity (every
value is a real canonical heading of some i18n-eligible domain's document
model, values pairwise distinct -- the full closed-set drift test is Phase
150's).
"""

from __future__ import annotations

import json
import tempfile
import types
import typing
import unittest
from importlib import import_module
from inspect import isclass
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models.heading_table import (
    heading_table_path,
    iter_heading_lines,
    load_heading_table,
    normalize_heading_lines,
    reset_heading_table_cache,
    resolve_heading_table,
)
from biz.dfch.specmgr.models.md.alias_match import space_separated_name
from biz.dfch.specmgr.models.md.alias_type import AliasType
from biz.dfch.specmgr.models.md.markdown_section import MarkdownSection

#: The i18n-eligible domains' own current document-model packages (feat-197-i18n: every
#: whole-body domain except ``feat``; ``adr`` excluded). The derivation below walks each
#: domain's ``*Document`` body field tree -- the exact sections the engine can match.
_DOCUMENT_MODEL_PACKAGES = {
    "req": "biz.dfch.specmgr.req.models.v1",
    "uc": "biz.dfch.specmgr.uc.models.v2",
    "tsk": "biz.dfch.specmgr.tsk.models.v1",
    "qa": "biz.dfch.specmgr.qa.models.v2",
    "prb": "biz.dfch.specmgr.prb.models.v1",
    "gol": "biz.dfch.specmgr.gol.models.v1",
    "rsk": "biz.dfch.specmgr.rsk.models.v1",
    "dec": "biz.dfch.specmgr.dec.models.v1",
    "sop": "biz.dfch.specmgr.sop.models.v1",
    "vcr": "biz.dfch.specmgr.vcr.models.v1",
    "sysrs": "biz.dfch.specmgr.sysrs.models.v1",
    "txt": "biz.dfch.specmgr.txt.models.v1",
}

#: Regex constructs that mark a pattern as data-carrying (free text, values, alternatives,
#: groups, classes) -- the complement of a fixed-text (literal) pattern.
_REGEX_SPECIALS = set("()[]{}|+*?.^$")


def _classify_regex(pattern: str) -> str | None:
    """The pattern's fixed canonical text (escaping undone), or None if it carries data."""
    body = pattern
    if body.startswith("^"):
        body = body[1:]
    if body.endswith("$"):
        body = body[:-1]
    out: list[str] = []
    i = 0
    while i < len(body):
        char = body[i]
        if char == "\\":
            if i + 1 >= len(body) or body[i + 1].isalnum():
                return None
            out.append(body[i + 1])
            i += 2
        else:
            if char in _REGEX_SPECIALS:
                return None
            out.append(char)
            i += 1
    return "".join(out)


def _concrete_types(annotation: object) -> list[type]:
    """Peel ``Optional``/``list`` wrappers down to the concrete types ``annotation`` names."""
    if annotation is None:
        return []
    origin = typing.get_origin(annotation)
    if origin is typing.Union or origin is types.UnionType:
        result: list[type] = []
        for arg in typing.get_args(annotation):
            result.extend(_concrete_types(arg))
        return result
    if origin in (list, tuple, set, frozenset):
        result = []
        for arg in typing.get_args(annotation):
            result.extend(_concrete_types(arg))
        return result
    if isinstance(annotation, type):
        return [annotation]
    return []


def _derive_canonical_headings() -> set[str]:
    """Derive the closed set of fixed-text canonical headings reachable from the document models.

    The test-side mirror of the ADR 38efdb66 item 3/4 closed-set derivation: for every
    i18n-eligible domain, walk its ``*Document`` body class's field tree (the sections the
    engine can actually match when parsing a document) and collect each section's effective
    ``@alias`` (LITERAL value, SPACE_SEPARATED class-name derivation, or a REGEX carrying no
    free-text group -- the pattern with its escaping undone).
    """
    seen: set[type] = set()
    canonical: set[str] = set()

    def visit(cls: type) -> None:
        if cls in seen or not isclass(cls) or not issubclass(cls, MarkdownSection):
            return
        seen.add(cls)
        metadata = getattr(cls, "_alias_metadata", None)
        if metadata is None:
            text: str | None = space_separated_name(cls.__name__)
        elif metadata["type"] == AliasType.REGEX:
            text = _classify_regex(str(metadata["value"]))
        else:
            text = str(metadata["value"])
        if text is not None:
            canonical.add(text)
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
    return canonical


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class TestLoadHeadingTable(unittest.TestCase):
    """Tests for load_heading_table (the lazy once-per-process packaged-table load)."""

    def setUp(self) -> None:
        self.enterContext(mock.patch("biz.dfch.specmgr.general.models.heading_table._loaded_tables", {}))

    def test_de_table_loads_with_the_expected_shape(self):
        """The packaged de table loads as a flat str -> str object with the ADR's own example entry."""
        result = load_heading_table("de")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["Kontext und Problembeschreibung"], "Context and Problem Statement")
        self.assertEqual(result["Was ist das Problem?"], "What Is the Problem?")
        for key, value in result.items():
            with self.subTest(key=key):
                self.assertIsInstance(key, str)
                self.assertIsInstance(value, str)
                self.assertEqual(key, key.strip())
                self.assertEqual(value, value.strip())

    def test_load_is_lazy_once_per_process(self):
        """The table file is read exactly once per process per language (the seam is called once;
        a second load returns the cached object without re-reading)."""
        with mock.patch(
            "biz.dfch.specmgr.general.models.heading_table.heading_table_path", wraps=heading_table_path
        ) as wrapped:
            first = load_heading_table("de")
            second = load_heading_table("de")
        self.assertEqual(wrapped.call_count, 1)
        self.assertEqual(first, second)

    def test_reset_forces_a_reload(self):
        """reset_heading_table_cache (the test-only hook) clears the cache: the next load re-reads."""
        with mock.patch(
            "biz.dfch.specmgr.general.models.heading_table.heading_table_path", wraps=heading_table_path
        ) as wrapped:
            load_heading_table("de")
            reset_heading_table_cache()
            load_heading_table("de")
            self.assertEqual(wrapped.call_count, 2)

    def test_missing_table_for_a_shape_valid_code_is_an_actionable_error(self):
        """A shape-valid code without a packaged table file is unusable: an actionable ValueError
        naming the missing file (ADR 38efdb66 item 3/6)."""
        with self.assertRaises(ValueError) as ctx:
            load_heading_table("fr")
        message = str(ctx.exception)
        self.assertIn("'fr'", message)
        self.assertIn("general/data/headings/fr.json", message)
        self.assertIn("shape-valid but unusable", message)

    def test_a_failed_load_is_not_cached(self):
        """A language whose load failed is retried on the next call (no error pinning)."""
        with mock.patch(
            "biz.dfch.specmgr.general.models.heading_table.heading_table_path", wraps=heading_table_path
        ) as wrapped:
            with self.assertRaises(ValueError):
                load_heading_table("fr")
            with self.assertRaises(ValueError):
                load_heading_table("fr")
            self.assertEqual(wrapped.call_count, 2)

    def test_malformed_json_is_rejected(self):
        """A table file that is not valid JSON is rejected with an actionable ValueError."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "xx.json"
            path.write_text("{ not json", encoding="utf-8")
            with mock.patch("biz.dfch.specmgr.general.models.heading_table.heading_table_path", return_value=path):
                with self.assertRaises(ValueError) as ctx:
                    load_heading_table("xx")
        self.assertIn("not valid JSON", str(ctx.exception))

    def test_non_object_table_is_rejected(self):
        """A table that is a JSON array (not a flat object) is rejected."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "yy.json"
            _write_json(path, [{"Kontext": "Context"}])
            with mock.patch("biz.dfch.specmgr.general.models.heading_table.heading_table_path", return_value=path):
                with self.assertRaises(ValueError) as ctx:
                    load_heading_table("yy")
        self.assertIn("flat JSON object", str(ctx.exception))

    def test_non_string_values_are_rejected(self):
        """A table entry with a non-string value is rejected."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "zz.json"
            _write_json(path, {"Kontext": 42})
            with mock.patch("biz.dfch.specmgr.general.models.heading_table.heading_table_path", return_value=path):
                with self.assertRaises(ValueError) as ctx:
                    load_heading_table("zz")
        self.assertIn("flat JSON object", str(ctx.exception))

    def test_duplicate_values_are_rejected(self):
        """Two distinct canonical headings translated to the same string are rejected -- the values
        must be pairwise distinct (a document heading to that string would be structurally
        ambiguous)."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "xx.json"
            _write_json(path, {"Änderungen": "Updates", "Kürzliche Änderungen": "Updates"})
            with mock.patch("biz.dfch.specmgr.general.models.heading_table.heading_table_path", return_value=path):
                with self.assertRaises(ValueError) as ctx:
                    load_heading_table("xx")
        message = str(ctx.exception)
        self.assertIn("'Updates'", message)
        self.assertIn("pairwise distinct", message)
        self.assertIn("Änderungen", message)
        self.assertIn("Kürzliche Änderungen", message)


class TestResolveHeadingTable(unittest.TestCase):
    """Tests for resolve_heading_table (the omitted/EN-aware entry point the parse boundaries use)."""

    def setUp(self) -> None:
        self.enterContext(mock.patch("biz.dfch.specmgr.general.models.heading_table._loaded_tables", {}))

    def test_none_resolves_to_no_table(self):
        """An omitted language (None) resolves to None -- canonical, no table."""
        self.assertIsNone(resolve_heading_table(None))

    def test_en_resolves_to_no_table(self):
        """The default language 'en' resolves to None -- EN is the canonical form itself (no
        packaged table file exists for it, and none is needed)."""
        self.assertIsNone(resolve_heading_table("en"))

    def test_de_resolves_to_the_loaded_table(self):
        """A non-default language resolves to its loaded table."""
        result = resolve_heading_table("de")
        assert result is not None
        self.assertEqual(result["Kontext und Problembeschreibung"], "Context and Problem Statement")

    def test_missing_table_propagates_the_loader_error(self):
        """A shape-valid language without a table raises the loader's actionable ValueError."""
        with self.assertRaises(ValueError) as ctx:
            resolve_heading_table("fr")
        self.assertIn("shape-valid but unusable", str(ctx.exception))


class TestNormalizeHeadingLines(unittest.TestCase):
    """Tests for normalize_heading_lines (the fence-aware, line-based pre-pass, ADR 38efdb66 item 5)."""

    def setUp(self) -> None:
        self.table = {
            "Kontext und Problembeschreibung": "Context and Problem Statement",
            "Entscheidungsergebnis": "Decision Outcome",
            "Quelle": "Source",
        }

    def test_mapped_headings_are_rewritten_to_canonical(self):
        """Every table-mapped heading line (any of the levels 1-6) is rewritten to its canonical text."""
        text = (
            "# Dokument\n"
            "\n"
            "## Kontext und Problembeschreibung\n"
            "\n"
            "## Entscheidungsergebnis\n"
            "\n"
            "### Quelle\n"
            "\n"
            "#### Quelle\n"
            "\n"
            "##### Quelle\n"
            "\n"
            "###### Quelle\n"
        )
        result = normalize_heading_lines(text, self.table)
        expected = (
            "# Dokument\n"
            "\n"
            "## Context and Problem Statement\n"
            "\n"
            "## Decision Outcome\n"
            "\n"
            "### Source\n"
            "\n"
            "#### Source\n"
            "\n"
            "##### Source\n"
            "\n"
            "###### Source\n"
        )
        self.assertEqual(result, expected)

    def test_unmapped_headings_stay_byte_identical(self):
        """A heading without a table entry (e.g. the free-form H1, or a data-carrying regex
        heading) is left byte-identical."""
        text = "# Dokumentlager wählen\n\n### Option 1: Kanban\n\n## Unbekanntes\n"
        result = normalize_heading_lines(text, self.table)
        self.assertEqual(result, text)

    def test_non_heading_lines_stay_byte_identical(self):
        """Every non-heading line (prose, lists, blank lines) stays byte-identical."""
        text = "Prose with a hash # inside.\n\n- a bullet\n- another: bullet\n\n> ## not a heading\n"
        result = normalize_heading_lines(text, self.table)
        self.assertEqual(result, text)

    def test_backtick_fenced_lines_are_not_rewritten(self):
        """A # line (or a mapped heading line) inside a ``` fenced code block is code, not a
        heading -- it stays byte-identical, as does the fence itself."""
        text = (
            "## Kontext und Problembeschreibung\n"
            "\n"
            "```python\n"
            "## Kontext und Problembeschreibung\n"
            "# a comment\n"
            "```\n"
            "\n"
            "## Ende\n"
        )
        result = normalize_heading_lines(text, self.table)
        expected = (
            "## Context and Problem Statement\n"
            "\n"
            "```python\n"
            "## Kontext und Problembeschreibung\n"
            "# a comment\n"
            "```\n"
            "\n"
            "## Ende\n"
        )
        self.assertEqual(result, expected)

    def test_tilde_fenced_lines_are_not_rewritten(self):
        """The same fence-awareness holds for ~~~ fenced code blocks."""
        text = "~~~\n## Kontext und Problembeschreibung\n~~~\n\n## Kontext und Problembeschreibung\n"
        result = normalize_heading_lines(text, self.table)
        expected = "~~~\n## Kontext und Problembeschreibung\n~~~\n\n## Context and Problem Statement\n"
        self.assertEqual(result, expected)

    def test_indented_fences_in_lists_are_respected(self):
        """An indented (list-continuation) fenced code block still shields its # lines."""
        text = (
            "- step one\n"
            "    ```\n"
            "    ## Kontext und Problembeschreibung\n"
            "    ```\n"
            "- ## Kontext und Problembeschreibung\n"
        )
        result = normalize_heading_lines(text, self.table)
        expected = (
            "- step one\n"
            "    ```\n"
            "    ## Kontext und Problembeschreibung\n"
            "    ```\n"
            "- ## Kontext und Problembeschreibung\n"
        )
        # Only the list item's own heading-ish line is NOT rewritten (it is list content, not an
        # ATX heading -- the pattern requires the hashes at column 0), and the fenced one is
        # shielded: the text is byte-identical.
        self.assertEqual(result, expected)

    def test_backtick_info_string_with_backtick_is_not_a_fence(self):
        """A ``` line whose info string contains a backtick is not a fence opener (CommonMark):
        the following heading line is rewritten."""
        text = "```a`b\n## Kontext und Problembeschreibung\n"
        result = normalize_heading_lines(text, self.table)
        expected = "```a`b\n## Context and Problem Statement\n"
        self.assertEqual(result, expected)

    def test_seven_hashes_is_not_a_heading(self):
        """A run of seven hashes is not an ATX heading (the pattern allows 1-6) -- byte-identical."""
        text = "####### Kontext und Problembeschreibung\n"
        result = normalize_heading_lines(text, self.table)
        self.assertEqual(result, text)

    def test_hashes_without_a_space_are_not_a_heading(self):
        """'#Kontext' (no space after the hashes) is not an ATX heading -- byte-identical."""
        text = "##Kontext und Problembeschreibung\n"
        result = normalize_heading_lines(text, self.table)
        self.assertEqual(result, text)

    def test_empty_table_is_a_byte_identity_noop(self):
        """An empty table rewrites nothing (the pre-pass is a pure no-op)."""
        text = "## Kontext und Problembeschreibung\n\nProse.\n"
        result = normalize_heading_lines(text, {})
        self.assertEqual(result, text)

    def test_canonical_en_text_through_the_de_table_is_byte_identical(self):
        """EN (canonical) text carries no mapped headings: the pass through the de table is a
        byte-identity no-op (the EN parse path stays untouched)."""
        en_text = "# A Decision\n\n## Context and Problem Statement\n\nProse.\n\n## Decision Outcome\n\nWe chose.\n"
        with mock.patch("biz.dfch.specmgr.general.models.heading_table._loaded_tables", {}):
            table = load_heading_table("de")
        result = normalize_heading_lines(en_text, table)
        self.assertEqual(result, en_text)

    def test_line_count_is_preserved(self):
        """The pass never adds or removes lines."""
        text = "## Kontext und Problembeschreibung\n\n```\n# code\n```\n\n## Ende\n"
        result = normalize_heading_lines(text, self.table)
        self.assertEqual(len(result.split("\n")), len(text.split("\n")))


class TestIterHeadingLines(unittest.TestCase):
    """``iter_heading_lines`` -- the shared heading/fence recognizer (also behind the Phase 140 drift skeleton)."""

    def test_yields_index_level_and_stripped_text_for_every_heading(self):
        text = "# Title\n\nprose\n\n## Section  \n\n#### Deep\n"

        result = list(iter_heading_lines(text))

        self.assertEqual(result, [(0, 1, "Title"), (4, 2, "Section"), (6, 4, "Deep")])

    def test_fenced_and_non_heading_lines_are_skipped(self):
        text = "## A\n```\n## B\n```\n####### seven\n#nospace\n~~~\n## C\n~~~\n## D\n"

        result = [heading for _index, _level, heading in iter_heading_lines(text)]

        self.assertEqual(result, ["A", "D"])

    def test_the_indexes_address_text_split_on_newline(self):
        text = "x\n## A\n\n## B\n"

        lines = text.split("\n")

        for index, _level, heading in iter_heading_lines(text):
            self.assertEqual(lines[index], f"## {heading}")

    def test_normalize_agrees_with_the_recognizer(self):
        """``normalize_heading_lines`` is built on the same recognizer: it rewrites exactly the yielded lines."""
        text = "# T\n\n## Beschreibung\n\n```\n## Beschreibung\n```\n"

        result = normalize_heading_lines(text, {"Beschreibung": "Description"})

        self.assertEqual(result, "# T\n\n## Description\n\n```\n## Beschreibung\n```\n")


class TestDeJsonIntegrity(unittest.TestCase):
    """Basic integrity of the packaged de.json table (the full closed-set drift test is Phase 150's)."""

    def setUp(self) -> None:
        self.enterContext(mock.patch("biz.dfch.specmgr.general.models.heading_table._loaded_tables", {}))
        self.table = load_heading_table("de")

    def test_values_are_pairwise_distinct(self):
        """No two distinct canonical headings may translate to the same German string (the loader's
        own invariant, re-pinned here against the packaged file)."""
        values = list(self.table.values())
        self.assertEqual(len(values), len(set(values)))

    def test_every_value_is_a_real_canonical_heading_of_a_document_model(self):
        """Every canonical value in de.json is the effective alias of a real section of some
        i18n-eligible domain's document model (the machine-derivation is the authority -- the table
        must not invent headings)."""
        canonical = _derive_canonical_headings()
        invented = set(self.table.values()) - canonical
        self.assertEqual(invented, set(), f"de.json maps to headings no document model declares: {sorted(invented)}")

    def test_no_entry_is_the_identity_map_and_no_data_carrying_heading_is_mapped(self):
        """Every entry is a genuine translation (the German key differs from the canonical value), and
        no value is a data-carrying heading prefix (``Option {N}:``/``Step {N}:``/``AC-{NNN} (...)``
        carry free text and hold no table entry, REQ-010 -- the timestamp-led update entries cannot
        occur either, since no fixed string matches them; the derived-set test above already pins
        full membership)."""
        data_carrying_prefixes = ("Option ", "Step ", "AC-")
        for key, value in self.table.items():
            with self.subTest(key=key):
                self.assertNotEqual(key, value)
                self.assertFalse(value.startswith(data_carrying_prefixes))

    def test_the_adr_example_entries_are_present(self):
        """The ADR's own named examples (item 3) are pinned: PRB's escaped-question regex headings
        decode with the '?' restored, and the shared 'More Information' heading maps too."""
        self.assertEqual(self.table["Was ist das Problem?"], "What Is the Problem?")
        self.assertEqual(self.table["Weitere Informationen"], "More Information")


if __name__ == "__main__":
    unittest.main()


class TestNormalizeHeadingLinesNeverMapsTheTitle(unittest.TestCase):
    """Regression for review finding E1: the level-1 title line is free text and is never looked up in the table."""

    def setUp(self) -> None:
        self.table = {
            "Quelle": "Source",
            "Weitere Informationen": "More Information",
            "Kontext und Problembeschreibung": "Context and Problem Statement",
        }

    def test_a_level_1_line_equal_to_a_table_key_stays_byte_identical(self):
        """'# Quelle' (a German title that equals a table key) is not rewritten."""
        for title in ("Quelle", "Weitere Informationen", "Kontext und Problembeschreibung"):
            with self.subTest(title=title):
                text = f"# {title}\n\nProse.\n"
                result = normalize_heading_lines(text, self.table)
                self.assertEqual(result, text)

    def test_the_same_text_at_level_2_to_6_is_rewritten(self):
        """Only the level differs: '## Quelle' .. '###### Quelle' become '<hashes> Source'."""
        for level in range(2, 7):
            with self.subTest(level=level):
                hashes = "#" * level
                result = normalize_heading_lines(f"{hashes} Quelle\n", self.table)
                self.assertEqual(result, f"{hashes} Source\n")

    def test_title_is_kept_while_the_section_heading_below_it_is_normalized(self):
        """A document whose title equals a key: the title survives, the same-text section heading maps."""
        text = "# Quelle\n\n## Quelle\n\nProse.\n"
        result = normalize_heading_lines(text, self.table)
        self.assertEqual(result, "# Quelle\n\n## Source\n\nProse.\n")

    def test_a_fenced_title_lookalike_is_unaffected(self):
        """A '# Quelle' line inside a fence is code (not a heading) and stays byte-identical; a mapped
        heading after the fence is still rewritten."""
        text = "# Quelle\n\n```\n# Quelle\n## Quelle\n```\n\n## Quelle\n"
        result = normalize_heading_lines(text, self.table)
        self.assertEqual(result, "# Quelle\n\n```\n# Quelle\n## Quelle\n```\n\n## Source\n")

    def test_canonical_english_text_through_a_table_is_still_a_no_op(self):
        """EN text with canonical headings (incl. an English title) is byte-identical through a table."""
        text = "# Choose a Document Store\n\n## Context and Problem Statement\n\n## More Information\n"
        result = normalize_heading_lines(text, self.table)
        self.assertEqual(result, text)

    def test_iter_heading_lines_still_yields_the_level_1_line(self):
        """The shared recognizer (also behind the translation drift check) is unchanged: it yields level 1."""
        result = list(iter_heading_lines("# Quelle\n\n## Quelle\n"))
        self.assertEqual(result, [(0, 1, "Quelle"), (2, 2, "Quelle")])
