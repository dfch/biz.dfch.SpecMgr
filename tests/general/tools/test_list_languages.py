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

"""Tests for the ``list_languages`` tool (feat-197-i18n Phase 140, Task 140.120, REQ-012, ACC-008).

Real tool calls against temporary base directories (``SPECMGR_DOCS_DIR``), no LLM. Covers: ACC-008 (EN only lists
``["en"]``; EN + variants list ``"en"`` first, then the others sorted), the parametrized EN+DE case over all twelve
i18n-eligible domains, a variant without an EN source (``"en"`` is never invented), a broken variant (listed, flagged,
byte-identical error text), a table-less language directory (listed, flagged), the layout rules (non-``.md`` siblings,
``sysrs``' ``.pdf``, shape-invalid directory names, other ids' documents are ignored), the guards before any filesystem
access (path-injection ``type``/``id``, ``feat``/``adr`` with the permanent wording), the not-found contract, the
registered MCP surface, and the read-only guarantee (no file is written, created, touched, or cache-invalidated).
"""

from __future__ import annotations

import asyncio
import shutil
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import LanguageListResult, ParseFailureResult
from biz.dfch.specmgr.general.tools._domains import ALL_DOMAINS
from biz.dfch.specmgr.general.tools._language_guard import LANGUAGE_AWARE_DOMAINS
from biz.dfch.specmgr.general.tools.list_languages import list_languages

from .test_i18n_all_domains import SPECS, SPECS_BY_NAME, _TempDocsMixin

_MISSING_UUID = "00000000-0000-4000-8000-000000000000"


def snapshot(root: Path) -> dict[str, tuple[bytes | None, int]]:
    """Every file and directory under ``root`` with its bytes (``None`` for a directory) and ``mtime_ns``."""
    result: dict[str, tuple[bytes | None, int]] = {}
    for path in sorted(root.rglob("*")):
        content = path.read_bytes() if path.is_file() else None
        result[str(path.relative_to(root))] = (content, path.stat().st_mtime_ns)
    return result


class TestListLanguagesAcc008(_TempDocsMixin):
    """ACC-008: the listing reports the available languages, ``"en"`` first when the EN source exists."""

    def test_en_only_artifact_lists_en(self):
        spec = SPECS_BY_NAME["dec"]
        created = spec.fn("create")(spec.en_body())

        result = list_languages("dec", created.id)

        self.assertIsInstance(result, LanguageListResult)
        self.assertEqual(result.languages, ["en"])
        self.assertEqual(result.type, "dec")
        self.assertEqual(result.id, created.id)
        self.assertEqual(len(result.entries), 1)
        entry = result.entries[0]
        self.assertEqual(entry.language, "en")
        self.assertTrue(entry.parseable)
        self.assertIsNone(entry.error)
        self.assertEqual(Path(entry.path), next(spec.base_dir().glob("*.md")).resolve())

    def test_en_and_de_variant_list_en_first_then_de(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, en_file, de_file = self.seed(spec)

        result = list_languages("dec", doc_id)

        self.assertEqual(result.languages, ["en", "de"])
        self.assertEqual([e.language for e in result.entries], ["en", "de"])
        self.assertEqual([Path(e.path) for e in result.entries], [en_file.resolve(), de_file.resolve()])
        self.assertTrue(all(e.parseable and e.error is None for e in result.entries))

    def test_other_languages_follow_en_sorted_by_code(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, en_file, de_file = self.seed(spec)
        # the variants of `fr` and `bg` are placed by hand (no heading tables for them: listed, flagged)
        for language in ("fr", "bg"):
            target = spec.base_dir(language)
            target.mkdir(parents=True)
            shutil.copy(de_file, target / de_file.name)

        result = list_languages("dec", doc_id)

        self.assertEqual(result.languages, ["en", "bg", "de", "fr"])
        self.assertEqual([e.parseable for e in result.entries], [True, False, True, False])

    def test_every_language_aware_domain_lists_en_and_de(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, en_file, de_file = self.seed(spec)

                result = list_languages(spec.d, doc_id)

                self.assertEqual(result.languages, ["en", "de"])
                self.assertEqual([Path(e.path) for e in result.entries], [en_file.resolve(), de_file.resolve()])
                self.assertEqual(result.type, spec.d)
                self.assertEqual(result.id, doc_id)

    def test_every_language_aware_domain_lists_en_only(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                created = spec.fn("create")(spec.en_body())

                result = list_languages(spec.d, created.id)

                self.assertEqual(result.languages, ["en"])


class TestListLanguagesVariantStates(_TempDocsMixin):
    """A variant without an EN source, a broken variant, and a table-less language directory."""

    def test_variant_without_en_source_does_not_invent_en(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, en_file, de_file = self.seed(spec)
        en_file.unlink()
        spec.reset_cache()

        result = list_languages("dec", doc_id)

        self.assertEqual(result.languages, ["de"])
        self.assertNotIn("en", [e.language for e in result.entries])

    def test_broken_variant_is_listed_flagged_with_the_byte_identical_parse_error(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, en_file, de_file = self.seed(spec)
        de_file.write_text(
            de_file.read_text(encoding="utf-8").replace("## Quelle", "## Völlig Falsch"), encoding="utf-8"
        )
        spec.reset_cache()

        result = list_languages("dec", doc_id)

        self.assertEqual(result.languages, ["en", "de"])
        de_entry = result.entries[1]
        self.assertFalse(de_entry.parseable)
        self.assertEqual(Path(de_entry.path), de_file.resolve())
        self.assertTrue(de_entry.error)
        # byte-identical to get_dec's ParseFailureResult and list_dec's failed row for the same file
        failure = spec.fn("get")(doc_id, language="de")
        self.assertIsInstance(failure, ParseFailureResult)
        self.assertEqual(de_entry.error, failure.error)
        failed_rows = [row for row in spec.fn("list")(language="de").results if row.error is not None]
        self.assertEqual([row.error for row in failed_rows], [de_entry.error])
        # the healthy EN entry is unaffected
        self.assertTrue(result.entries[0].parseable)

    def test_broken_variant_is_flagged_for_every_domain(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, _en_file, de_file = self.seed(spec)
                de_file.write_text("---\nnot: [valid\n---\n# x\n", encoding="utf-8")
                spec.reset_cache()

                result = list_languages(spec.d, doc_id)

                self.assertEqual(result.languages, ["en", "de"])
                self.assertFalse(result.entries[1].parseable)
                self.assertTrue(result.entries[1].error)

    def test_table_less_language_directory_is_listed_and_flagged_with_the_table_error(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, _en_file, de_file = self.seed(spec)
        target = spec.base_dir("fr")
        target.mkdir(parents=True)
        shutil.copy(de_file, target / de_file.name)

        result = list_languages("dec", doc_id)

        fr_entry = next(e for e in result.entries if e.language == "fr")
        self.assertFalse(fr_entry.parseable)
        self.assertIn("no heading-mapping table for language 'fr'", fr_entry.error or "")


class TestListLanguagesLayoutRules(_TempDocsMixin):
    """Only ``*.md`` documents of the id under shape-valid language directories participate."""

    def test_non_md_siblings_are_ignored(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, en_file, de_file = self.seed(spec)
        (spec.base_dir("de") / "notes.txt").write_text("x", encoding="utf-8")
        (spec.base_dir("de") / f"{de_file.stem}.pdf").write_bytes(b"%PDF")
        (spec.base_dir("pt")).mkdir()
        (spec.base_dir("pt") / f"{de_file.stem}.pdf").write_bytes(b"%PDF")

        result = list_languages("dec", doc_id)

        self.assertEqual(result.languages, ["en", "de"])

    def test_sysrs_pdf_siblings_never_count_as_a_language(self):
        spec = SPECS_BY_NAME["sysrs"]
        created = spec.fn("create")(spec.en_body())
        (spec.base_dir() / "appendix-a.pdf").write_bytes(b"%PDF")
        (spec.base_dir("de")).mkdir()
        (spec.base_dir("de") / "appendix-a.pdf").write_bytes(b"%PDF")

        result = list_languages("sysrs", created.id)

        self.assertEqual(result.languages, ["en"])

    def test_shape_invalid_directory_names_are_ignored(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, en_file, de_file = self.seed(spec)
        for name in ("Notes", "de-DE", "DE", "deu"):
            target = spec.base_dir() / name
            target.mkdir()
            shutil.copy(de_file, target / de_file.name)

        result = list_languages("dec", doc_id)

        self.assertEqual(result.languages, ["en", "de"])

    def test_documents_of_other_ids_do_not_count(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, _en_file, _de_file = self.seed(spec)
        other = spec.fn("create")(spec.en_body())
        spec.fn("create")(spec.de_body(), language="de", id=other.id)
        third = spec.fn("create")(spec.en_body())  # EN only

        self.assertEqual(list_languages("dec", doc_id).languages, ["en", "de"])
        self.assertEqual(list_languages("dec", other.id).languages, ["en", "de"])
        self.assertEqual(list_languages("dec", third.id).languages, ["en"])

    def test_the_other_ids_files_are_never_reported_as_this_ids_path(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, _en_file, de_file = self.seed(spec)
        other = spec.fn("create")(spec.en_body())
        spec.fn("create")(spec.de_body(), language="de", id=other.id)

        result = list_languages("dec", doc_id)

        self.assertEqual({Path(e.path).name for e in result.entries}, {de_file.name})

    def test_a_language_directory_that_is_a_file_is_ignored(self):
        spec = SPECS_BY_NAME["dec"]
        created = spec.fn("create")(spec.en_body())
        (spec.base_dir() / "de").write_text("not a directory", encoding="utf-8")

        self.assertEqual(list_languages("dec", created.id).languages, ["en"])


class TestListLanguagesNotFound(_TempDocsMixin):
    """An id that exists in no language raises the domain's own not-found error."""

    def test_absent_id_raises_the_domains_not_found_error_for_every_domain(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                spec.fn("create")(spec.en_body())  # a sibling, so the directory exists

                with self.assertRaises(spec.not_found_error()) as ctx:
                    list_languages(spec.d, _MISSING_UUID)

                self.assertIn("in any language", str(ctx.exception))
                self.assertIn(_MISSING_UUID, str(ctx.exception))

    def test_absent_base_directory_raises_not_found(self):
        spec = SPECS_BY_NAME["dec"]

        with self.assertRaises(spec.not_found_error()):
            list_languages("dec", _MISSING_UUID)

    def test_a_not_found_error_is_a_lookup_error(self):
        with self.assertRaises(LookupError):
            list_languages("req", _MISSING_UUID)


class TestListLanguagesGuards(_TempDocsMixin):
    """``type``/``id`` are validated before any filesystem access."""

    def test_path_injection_ids_are_rejected_before_any_filesystem_access(self):
        for bad_id in (
            "../../etc/passwd",
            "..",
            "a/b",
            "a\\b",
            "",
            "   ",
            "not-a-uuid",
            "DEC-1",
            "ABCDEF01-0000-4000-8000-000000000000",
        ):
            with self.subTest(id=bad_id):
                with mock.patch("biz.dfch.specmgr.general.tools.list_languages.list_language_variants") as probe:
                    with self.assertRaises(ValueError):
                        list_languages("dec", bad_id)
                    probe.assert_not_called()

    def test_unknown_type_is_rejected_before_any_filesystem_access(self):
        for bad_type in ("zzz", "", "../dec", "DEC", "ac"):
            with self.subTest(type=bad_type):
                with mock.patch("biz.dfch.specmgr.general.tools.list_languages.list_language_variants") as probe:
                    with self.assertRaises(ValueError):
                        list_languages(bad_type, _MISSING_UUID)
                    probe.assert_not_called()

    def test_feat_and_adr_are_rejected_with_the_permanent_wording(self):
        for type_, id_ in (
            ("feat", "feat-197-i18n"),
            ("feat", _MISSING_UUID),
            ("adr", _MISSING_UUID),
            ("feat", "../../x"),
        ):
            with self.subTest(type=type_, id=id_):
                with mock.patch("biz.dfch.specmgr.general.tools.list_languages.list_language_variants") as probe:
                    with self.assertRaises(ValueError) as ctx:
                        list_languages(type_, id_)
                    probe.assert_not_called()
                self.assertIn(f"{type_} documents are always English", str(ctx.exception))
                self.assertIn("they have no language variants", str(ctx.exception))

    def test_the_wording_matches_the_write_tools_guard(self):
        """The permanent clause is the one ``guard_language`` uses for the same types (one wording)."""
        from biz.dfch.specmgr.general.tools._language_guard import guard_language

        with self.assertRaises(ValueError) as write_guard:
            guard_language("feat", "de")
        with self.assertRaises(ValueError) as listing_guard:
            list_languages("feat", "feat-197-i18n")

        clause = "feat documents are always English (they have no language variants)"
        self.assertIn(clause, str(write_guard.exception))
        self.assertIn(clause, str(listing_guard.exception))

    def test_all_twelve_domains_are_accepted_by_the_type_guard(self):
        for domain in LANGUAGE_AWARE_DOMAINS:
            with self.subTest(domain=domain):
                with self.assertRaises(LookupError):  # past the guards: only the not-found of a missing id
                    list_languages(domain, _MISSING_UUID)


class TestListLanguagesReadOnly(_TempDocsMixin):
    """The tool never writes, creates, touches, or cache-invalidates anything."""

    def test_the_docs_tree_is_byte_and_mtime_identical_after_a_listing(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, _en_file, de_file = self.seed(spec)
        (spec.base_dir("fr")).mkdir()
        shutil.copy(de_file, spec.base_dir("fr") / de_file.name)
        before = snapshot(self.docs_root)

        list_languages("dec", doc_id)
        list_languages("dec", doc_id)

        self.assertEqual(snapshot(self.docs_root), before)

    def test_an_absent_id_creates_no_directory(self):
        before = snapshot(self.docs_root)

        with self.assertRaises(LookupError):
            list_languages("dec", _MISSING_UUID)

        self.assertEqual(snapshot(self.docs_root), before)
        self.assertEqual(list(self.docs_root.rglob("*")), [])

    def test_no_cache_entry_is_invalidated(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, _en_file, _de_file = self.seed(spec)

        with mock.patch("biz.dfch.specmgr.general.tools._doc_cache.DocCache.invalidate") as invalidate:
            list_languages("dec", doc_id)

        invalidate.assert_not_called()

    def test_every_domain_leaves_its_tree_untouched(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, _en_file, _de_file = self.seed(spec)
                before = snapshot(self.docs_root)

                list_languages(spec.d, doc_id)

                self.assertEqual(snapshot(self.docs_root), before)


class TestListLanguagesDoesNotChangeTheEnOnlyScans(_TempDocsMixin):
    """REQ-013: the EN-only consumers still see exactly the flat EN files after (and regardless of) a listing."""

    def test_list_dec_en_is_unchanged_by_the_presence_of_variants_and_the_listing(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, _en_file, _de_file = self.seed(spec)
        before = spec.fn("list")()

        list_languages("dec", doc_id)

        self.assertEqual(spec.fn("list")(), before)
        self.assertEqual([row.id for row in before.results], [doc_id])


class TestListLanguagesRegistration(unittest.TestCase):
    """The tool is a registered MCP tool with a precise schema."""

    def test_registered_with_type_and_id_only(self):
        from biz.dfch.specmgr.server import mcp

        tools = {tool.name: tool for tool in asyncio.run(mcp.list_tools())}

        self.assertIn("list_languages", tools)
        schema = tools["list_languages"].input_schema
        self.assertEqual(set(schema["properties"]), {"type", "id"})
        self.assertEqual(set(schema["required"]), {"type", "id"})
        # feat/adr are in the schema's enum only so that they get the explanatory rejection
        self.assertEqual(set(schema["properties"]["type"]["enum"]), set(ALL_DOMAINS))

    def test_no_language_parameter_and_not_in_the_en_only_tool_family(self):
        import inspect

        self.assertEqual(list(inspect.signature(list_languages).parameters), ["type", "id"])


if __name__ == "__main__":
    unittest.main()
