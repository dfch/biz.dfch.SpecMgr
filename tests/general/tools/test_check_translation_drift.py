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

"""Tests for the ``check_translation_drift`` tool (feat-197-i18n Phase 140, Tasks 140.100/140.110, REQ-014, ACC-009).

Real tool calls against temporary base directories (``SPECMGR_DOCS_DIR``), no LLM. Covers: the in-sync baseline for
all twelve i18n-eligible domains (each domain's packaged template translated through ``de.json``); **ACC-009** (a
deliberately out-of-sync translation reports the structural mismatch AND the staleness in one result); structural
drift (missing, extra, reordered; for every domain via direct on-disk edits, and for ``dec``/``vcr`` through the write
tools); no false positives (translated free text of ``Option N:``/``AC-NNN (Method):`` headings, prose-only
differences, the ``prb`` ``problem_statement`` exemption); a broken variant or source (an ``unparseable`` finding
carrying the byte-identical parse error, never raised); the staleness semantics (equal/older/newer, the one-millisecond
boundary, mixed ``T``/space separators and offsets, PyYAML-coerced timestamps, a missing timestamp); a non-EN source
language; the guard matrix before any filesystem access; the not-found contract; the registered MCP surface; and the
read-only guarantee.
"""

from __future__ import annotations

import asyncio
import re
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import ParseFailureResult, TranslationDriftResult, ValidateResult
from biz.dfch.specmgr.general.models import heading_table as heading_table_module
from biz.dfch.specmgr.general.tools._domains import ALL_DOMAINS
from biz.dfch.specmgr.general.tools._language_guard import LANGUAGE_AWARE_DOMAINS
from biz.dfch.specmgr.general.tools.check_translation_drift import check_translation_drift
from biz.dfch.specmgr.general.tools.edit import edit
from biz.dfch.specmgr.general.tools.update import update

from .test_i18n_all_domains import SPECS, SPECS_BY_NAME, DomainSpec, _TempDocsMixin
from .test_list_languages import snapshot

_MISSING_UUID = "00000000-0000-4000-8000-000000000000"
#: The concrete ``problem_statement`` lead sentence of the packaged ``prb`` template (English in every language).
_PRB_SENTENCE = "The current process is causing delays, for users because of missing automation."
_LOCATE = "biz.dfch.specmgr.general.tools.check_translation_drift.locate"


def set_updated(path: Path, value: str, *, quote: bool = True) -> None:
    """Rewrite the frontmatter ``updated`` line of the document at ``path`` (quoted string, or a bare YAML scalar)."""
    text = path.read_text(encoding="utf-8")
    rendered = f"'{value}'" if quote else value
    replaced, count = re.subn(r"(?m)^updated: .*$", f"updated: {rendered}", text, count=1)
    assert count == 1, "no updated line"
    path.write_text(replaced, encoding="utf-8")


def rewrite_body(path: Path, transform: Callable[[str], str]) -> None:
    """Rewrite the body of the document at ``path`` (everything after the frontmatter block) in place."""
    text = path.read_text(encoding="utf-8")
    _empty, frontmatter_block, body = text.split("---\n", 2)
    path.write_text(f"---\n{frontmatter_block}---\n{transform(body)}", encoding="utf-8")


def split_h2_blocks(body: str) -> tuple[str, list[str]]:
    """Split a body into its preamble (up to the first ``## `` line) and its ``## `` blocks (each with its heading)."""
    parts = re.split(r"(?m)^(?=## )", body)
    return parts[0], parts[1:]


def findings(result: TranslationDriftResult, kind: str) -> list:
    return [finding for finding in result.structural if finding.kind == kind]


class TestInSyncBaseline(_TempDocsMixin):
    """A faithfully translated variant (the packaged template through ``de.json``) is in sync, for every domain."""

    def test_every_language_aware_domain_is_in_sync(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, en_file, de_file = self.seed(spec)

                result = check_translation_drift(spec.d, doc_id, "de")

                self.assertIsInstance(result, TranslationDriftResult)
                self.assertEqual(result.structural, [])
                self.assertFalse(result.stale)
                self.assertIsNone(result.staleness_error)
                self.assertTrue(result.in_sync)
                self.assertEqual((result.type, result.id), (spec.d, doc_id))
                self.assertEqual((result.source_language, result.language), ("en", "de"))
                self.assertEqual(Path(result.source_path), en_file.resolve())
                self.assertEqual(Path(result.variant_path), de_file.resolve())
                self.assertIsNotNone(result.source_updated)
                self.assertIsNotNone(result.variant_updated)

    def test_the_variant_created_after_the_source_is_not_stale(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, _en_file, _de_file = self.seed(spec)

        result = check_translation_drift("dec", doc_id, "de")

        self.assertFalse(result.stale)
        self.assertLessEqual(result.source_ahead_by_seconds, 0.0)


class TestAcc009BothDriftKindsInOneRun(_TempDocsMixin):
    """ACC-009: a deliberately out-of-sync translation reports the structural mismatch AND the staleness."""

    def test_missing_section_and_stale_variant_are_both_reported(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, en_file, de_file = self.seed(spec)
        # drop the optional `## Weitere Informationen` section from the German variant, through the write tool
        body = spec.fn("get")(doc_id, raw=True, language="de")
        preamble, blocks = split_h2_blocks(body)
        kept = [block for block in blocks if not block.startswith("## Weitere Informationen")]
        self.assertEqual(len(kept), len(blocks) - 1)
        outcome = update(doc_id, "dec", preamble + "".join(kept), language="de")
        self.assertNotIsInstance(outcome, ValidateResult, outcome)
        # ...and let the English source move on afterwards
        set_updated(en_file, "2099-01-01T00:00:00.000Z")

        result = check_translation_drift("dec", doc_id, "de")

        self.assertFalse(result.in_sync)
        self.assertEqual(
            [(f.kind, f.heading, f.level) for f in result.structural], [("missing", "More Information", 2)]
        )
        self.assertTrue(result.stale)
        self.assertGreater(result.source_ahead_by_seconds, 0)
        self.assertEqual(result.source_updated, "2099-01-01T00:00:00.000Z")
        self.assertIsNone(result.staleness_error)

    def test_both_kinds_are_independent(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, en_file, de_file = self.seed(spec)
        rewrite_body(de_file, lambda body: body.replace("## Weitere Informationen", "## Weitere Infos"))
        set_updated(en_file, "2026-01-01T00:00:00.000Z")
        set_updated(de_file, "2026-06-01T00:00:00.000Z")

        structural_only = check_translation_drift("dec", doc_id, "de")

        self.assertTrue(structural_only.structural)
        self.assertFalse(structural_only.stale)
        self.assertFalse(structural_only.in_sync)

        rewrite_body(de_file, lambda body: body.replace("## Weitere Infos", "## Weitere Informationen"))
        set_updated(en_file, "2026-12-01T00:00:00.000Z")

        stale_only = check_translation_drift("dec", doc_id, "de")

        self.assertEqual(stale_only.structural, [])
        self.assertTrue(stale_only.stale)
        self.assertFalse(stale_only.in_sync)

    def test_extra_section_and_staleness_in_one_result(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, en_file, de_file = self.seed(spec)
        outcome = edit(
            doc_id,
            "dec",
            "### Option 1: name of the first option\n\nThe pros and cons of the first option.\n",
            "### Option 1: name of the first option\n\nThe pros and cons of the first option.\n\n"
            "### Option 2: eine zusätzliche Option\n\nNur in der Übersetzung.\n",
            language="de",
        )
        self.assertNotIsInstance(outcome, ValidateResult, outcome)
        set_updated(en_file, "2099-01-01T00:00:00.000Z")

        result = check_translation_drift("dec", doc_id, "de")

        extras = findings(result, "extra")
        self.assertEqual(
            [(f.heading, f.level, f.text) for f in extras], [("Option 2:", 3, "Option 2: eine zusätzliche Option")]
        )
        self.assertEqual(extras[0].path, "Pros and Cons > Option 2:")
        self.assertIsNone(extras[0].source_position)
        self.assertIsNotNone(extras[0].variant_position)
        self.assertTrue(result.stale)
        self.assertFalse(result.in_sync)


class TestStructuralDriftEveryDomain(_TempDocsMixin):
    """Missing / extra / reordered are detected for every domain via direct on-disk edits of the variant."""

    def _de_file(self, spec: DomainSpec) -> tuple[str, Path]:
        spec.reset_cache()
        doc_id, _en_file, de_file = self.seed(spec)
        return doc_id, de_file

    def test_a_removed_section_is_missing_for_every_domain(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                doc_id, de_file = self._de_file(spec)

                def drop_last_h2(body: str) -> str:
                    preamble, blocks = split_h2_blocks(body)
                    return preamble + "".join(blocks[:-1])

                rewrite_body(de_file, drop_last_h2)

                result = check_translation_drift(spec.d, doc_id, "de")

                self.assertFalse(result.in_sync)
                missing = findings(result, "missing")
                self.assertTrue(missing, result.structural)
                self.assertEqual(missing[0].level, 2)
                self.assertIsNone(missing[0].variant_position)
                self.assertIsNotNone(missing[0].source_position)

    def test_an_unknown_extra_section_is_extra_for_every_domain(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                doc_id, de_file = self._de_file(spec)
                rewrite_body(de_file, lambda body: body.rstrip("\n") + "\n\n## Zusätzlicher Abschnitt\n\nNur hier.\n")

                result = check_translation_drift(spec.d, doc_id, "de")

                extras = findings(result, "extra")
                self.assertEqual(
                    [(f.heading, f.text) for f in extras], [("Zusätzlicher Abschnitt", "Zusätzlicher Abschnitt")]
                )
                self.assertFalse(result.in_sync)
                # the variant no longer parses as the domain's schema: reported, not raised
                self.assertEqual(len(findings(result, "unparseable")), 1)

    def test_two_swapped_sections_are_reordered_for_every_domain(self):
        for spec in SPECS:
            if spec.d == "tsk":
                continue  # the task-list template has a single h2 section: nothing to swap (covered by the unit tests)
            with self.subTest(domain=spec.d):
                doc_id, de_file = self._de_file(spec)

                def swap_first_two(body: str) -> str:
                    preamble, blocks = split_h2_blocks(body)
                    return preamble + "".join([blocks[1], blocks[0], *blocks[2:]])

                rewrite_body(de_file, swap_first_two)

                result = check_translation_drift(spec.d, doc_id, "de")

                reordered = findings(result, "reordered")
                self.assertEqual(len(reordered), 1, result.structural)
                self.assertIsNotNone(reordered[0].source_position)
                self.assertIsNotNone(reordered[0].variant_position)
                self.assertNotEqual(reordered[0].source_position, reordered[0].variant_position)
                self.assertFalse(result.in_sync)
                self.assertEqual(findings(result, "missing") + findings(result, "extra"), [])

    def test_a_valid_reorder_through_the_write_tools_is_reordered_only(self):
        """``vcr`` accepts its acceptance criteria in any order: a reorder that still validates is *only* drift."""
        spec = SPECS_BY_NAME["vcr"]
        doc_id, en_file, _de_file = self.seed(spec)
        body = spec.fn("get")(doc_id, raw=True, language="de")
        first = body.index("### AC-001 (Test)")
        second = body.index("### AC-002 (Analysis)")
        end = body.index("## Weitere Informationen")
        swapped = body[:first] + body[second:end] + body[first:second] + body[end:]
        outcome = update(doc_id, "vcr", swapped, language="de")
        self.assertNotIsInstance(outcome, ValidateResult, outcome)

        result = check_translation_drift("vcr", doc_id, "de")

        self.assertEqual([f.kind for f in result.structural], ["reordered"])
        self.assertIn(result.structural[0].heading, {"AC-001 (Test):", "AC-002 (Analysis):"})
        self.assertNotEqual(result.structural[0].source_position, result.structural[0].variant_position)
        self.assertFalse(result.in_sync)


class TestNoFalsePositives(_TempDocsMixin):
    """Wording and translated free text are not structure."""

    def test_translated_option_title_is_not_drift(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, _en_file, _de_file = self.seed(spec)
        outcome = edit(
            doc_id,
            "dec",
            "### Option 1: name of the first option",
            "### Option 1: Name der ersten Option-DE",
            language="de",
        )
        self.assertNotIsInstance(outcome, ValidateResult, outcome)

        result = check_translation_drift("dec", doc_id, "de")

        self.assertEqual(result.structural, [])

    def test_translated_acceptance_criterion_text_is_not_drift_but_a_changed_method_is(self):
        spec = SPECS_BY_NAME["vcr"]
        doc_id, _en_file, de_file = self.seed(spec)
        outcome = edit(
            doc_id,
            "vcr",
            "### AC-001 (Test): Blind text describing the first criterion",
            "### AC-001 (Test): Blindtext zum ersten Kriterium",
            language="de",
        )
        self.assertNotIsInstance(outcome, ValidateResult, outcome)

        unchanged = check_translation_drift("vcr", doc_id, "de")

        self.assertEqual(unchanged.structural, [])

        outcome = edit(
            doc_id, "vcr", "### AC-001 (Test): Blindtext", "### AC-001 (Inspection): Blindtext", language="de"
        )
        self.assertNotIsInstance(outcome, ValidateResult, outcome)

        changed = check_translation_drift("vcr", doc_id, "de")

        self.assertEqual(
            [(f.kind, f.heading) for f in changed.structural],
            # the changed token renames the section, so its sub-section (`Test Steps`) moves with it
            [
                ("missing", "AC-001 (Test):"),
                ("missing", "Test Steps"),
                ("extra", "AC-001 (Inspection):"),
                ("extra", "Test Steps"),
            ],
        )

    def test_prose_only_differences_are_never_structural(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, _en_file, de_file = self.seed(spec)
                rewrite_body(
                    de_file,
                    lambda body: re.sub(r"(?m)^([A-Z][a-z ,]+)\.$", r"Völlig andere Formulierung \1.", body),
                )

                result = check_translation_drift(spec.d, doc_id, "de")

                self.assertEqual(result.structural, [])

    def test_update_entries_are_not_compared(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, _en_file, de_file = self.seed(spec)
        rewrite_body(
            de_file,
            lambda body: body.replace(
                "### 2026-08-27 09:14:27.512Z - Created",
                "### 2026-09-01 10:00:00.000Z - Übersetzt\n\nNeu.\n\n### 2026-08-27 09:14:27.512Z - Angelegt",
            ),
        )

        result = check_translation_drift("dec", doc_id, "de")

        self.assertEqual(result.structural, [])

    def test_prb_problem_statement_differences_are_ignored(self):
        spec = SPECS_BY_NAME["prb"]
        doc_id, en_file, de_file = self.seed(spec)
        self.assertIn(_PRB_SENTENCE, en_file.read_text(encoding="utf-8"))
        self.assertIn(_PRB_SENTENCE, de_file.read_text(encoding="utf-8"))  # the exempt sentence: English in the variant
        # a different (still valid) English sentence in the source: the lead paragraph is not a heading, never compared
        rewrite_body(
            en_file,
            lambda body: body.replace(
                _PRB_SENTENCE,
                "Our API is causing frequent outages, for customers because of unbounded retries.",
            ),
        )
        self.assertNotIsInstance(spec.fn("get")(doc_id), ParseFailureResult)
        self.assertNotIn(_PRB_SENTENCE, en_file.read_text(encoding="utf-8"))  # the two sentences really differ

        result = check_translation_drift("prb", doc_id, "de")

        self.assertEqual(result.structural, [])

    def test_a_translated_prb_problem_statement_is_the_variants_parse_failure_only(self):
        """A translated ``problem_statement`` breaks the (unchanged) validator: reported as unparseable, with no
        structural finding about the lead paragraph itself."""
        spec = SPECS_BY_NAME["prb"]
        doc_id, _en_file, de_file = self.seed(spec)
        rewrite_body(
            de_file,
            lambda body: body.replace(
                _PRB_SENTENCE,
                "Der aktuelle Prozess verursacht Verzögerungen, für Nutzer wegen fehlender Automatisierung.",
            ),
        )

        result = check_translation_drift("prb", doc_id, "de")

        self.assertEqual([f.kind for f in result.structural], ["unparseable"])


class TestUnparseableDocuments(_TempDocsMixin):
    """A document that exists but fails to parse is a structural finding carrying the parse error, never raised."""

    def test_broken_variant_is_an_unparseable_finding_with_the_byte_identical_error_and_still_diffed(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, _en_file, de_file = self.seed(spec)
        rewrite_body(de_file, lambda body: body.replace("## Quelle", "## Völlig Falsch"))

        result = check_translation_drift("dec", doc_id, "de")

        unparseable = findings(result, "unparseable")
        self.assertEqual(len(unparseable), 1)
        self.assertEqual(unparseable[0].language, "de")
        self.assertIsNone(unparseable[0].heading)
        failure = spec.fn("get")(doc_id, language="de")
        self.assertIsInstance(failure, ParseFailureResult)
        self.assertEqual(unparseable[0].error, failure.error)
        self.assertIn(str(de_file.resolve()), unparseable[0].message)
        # the raw skeleton is still diffed: the mistranslated heading is also missing/extra
        self.assertEqual(
            [(f.kind, f.heading) for f in result.structural if f.kind != "unparseable"],
            [
                ("missing", "Source"),
                ("extra", "Völlig Falsch"),
            ],
        )
        self.assertFalse(result.in_sync)

    def test_broken_source_is_an_unparseable_finding_for_the_source_language(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, en_file, _de_file = self.seed(spec)
        rewrite_body(en_file, lambda body: body.replace("## Source", "## Garbage"))

        result = check_translation_drift("dec", doc_id, "de")

        unparseable = findings(result, "unparseable")
        self.assertEqual([f.language for f in unparseable], ["en"])
        self.assertEqual(unparseable[0].error, spec.fn("get")(doc_id).error)
        self.assertFalse(result.in_sync)

    def test_broken_frontmatter_never_raises_and_reports_the_staleness_problem(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, _en_file, de_file = self.seed(spec)
                de_file.write_text("---\nnot: [valid\n---\n# x\n", encoding="utf-8")

                result = check_translation_drift(spec.d, doc_id, "de")

                self.assertEqual([f.kind for f in result.structural], ["unparseable"])
                self.assertFalse(result.stale)
                self.assertIsNotNone(result.staleness_error)
                self.assertFalse(result.in_sync)

    def test_both_documents_broken_reports_both(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, en_file, de_file = self.seed(spec)
        en_file.write_text("---\nnot: [valid\n---\n# x\n", encoding="utf-8")
        de_file.write_text("---\nnot: [valid\n---\n# x\n", encoding="utf-8")

        result = check_translation_drift("dec", doc_id, "de")

        self.assertEqual([f.language for f in result.structural], ["en", "de"])
        self.assertEqual({f.kind for f in result.structural}, {"unparseable"})


class TestStaleness(_TempDocsMixin):
    """REQ-014b: the source's ``updated`` strictly newer than the variant's; compared as datetimes."""

    def setUp(self) -> None:
        super().setUp()
        spec = SPECS_BY_NAME["dec"]
        self.doc_id, self.en_file, self.de_file = self.seed(spec)

    def _check(self, source: str, variant: str, *, quote: bool = True) -> TranslationDriftResult:
        set_updated(self.en_file, source, quote=quote)
        set_updated(self.de_file, variant, quote=quote)
        return check_translation_drift("dec", self.doc_id, "de")

    def test_equal_timestamps_are_not_stale(self):
        result = self._check("2026-10-30T15:05:00.000+01:00", "2026-10-30T15:05:00.000+01:00")

        self.assertFalse(result.stale)
        self.assertEqual(result.source_ahead_by_seconds, 0.0)
        self.assertTrue(result.in_sync)

    def test_source_one_millisecond_newer_is_stale(self):
        result = self._check("2026-10-30T15:05:00.001+01:00", "2026-10-30T15:05:00.000+01:00")

        self.assertTrue(result.stale)
        self.assertFalse(result.in_sync)
        self.assertAlmostEqual(result.source_ahead_by_seconds, 0.001, places=6)
        self.assertEqual(result.source_updated, "2026-10-30T15:05:00.001+01:00")
        self.assertEqual(result.variant_updated, "2026-10-30T15:05:00.000+01:00")

    def test_variant_newer_is_not_stale(self):
        result = self._check("2026-10-30T15:05:00.000+01:00", "2026-10-31T00:00:00.000+01:00")

        self.assertFalse(result.stale)
        self.assertLess(result.source_ahead_by_seconds, 0)

    def test_different_offsets_compare_as_instants(self):
        older = self._check("2026-10-30T15:05:00.000+01:00", "2026-10-30T14:30:00.000Z")
        newer = self._check("2026-10-30T14:30:00.000Z", "2026-10-30T15:05:00.000+01:00")
        equal = self._check("2026-10-30T14:05:00.000Z", "2026-10-30T15:05:00.000+01:00")

        self.assertFalse(older.stale)  # string comparison would say stale
        self.assertTrue(newer.stale)  # string comparison would say not stale
        self.assertFalse(equal.stale)

    def test_t_and_space_separators_compare_equal(self):
        result = self._check("2026-10-30 15:05:00.000+01:00", "2026-10-30T15:05:00.000+01:00")

        self.assertFalse(result.stale)
        self.assertEqual(result.source_ahead_by_seconds, 0.0)

    def test_unquoted_yaml_timestamps_are_compared_too(self):
        newer_source = self._check("2026-10-30 15:05:01.000+01:00", "2026-10-30T15:05:00.000+01:00", quote=False)
        equal = self._check("2026-10-30 15:05:00.000+01:00", "2026-10-30T14:05:00.000Z", quote=False)

        self.assertTrue(newer_source.stale)
        self.assertEqual(newer_source.source_ahead_by_seconds, 1.0)
        self.assertFalse(equal.stale)
        self.assertIsNone(equal.staleness_error)

    def test_a_missing_updated_is_reported_and_blocks_in_sync(self):
        text = self.de_file.read_text(encoding="utf-8")
        self.de_file.write_text(re.sub(r"(?m)^updated: .*\n", "", text), encoding="utf-8")

        result = check_translation_drift("dec", self.doc_id, "de")

        self.assertFalse(result.stale)
        self.assertIsNone(result.variant_updated)
        self.assertIn("variant", result.staleness_error or "")
        self.assertIn("missing", result.staleness_error or "")
        self.assertFalse(result.in_sync)

    def test_a_write_to_the_source_makes_the_variant_stale_naturally(self):
        """No hand-edited timestamps: a real ``set_classification`` on the EN source bumps ``updated``."""
        from biz.dfch.specmgr.general.tools.set_classification import set_classification

        set_classification(self.doc_id, "dec", "internal")

        result = check_translation_drift("dec", self.doc_id, "de")

        self.assertTrue(result.stale)
        self.assertEqual(result.structural, [])
        self.assertFalse(result.in_sync)


class TestSourceLanguage(unittest.TestCase):
    """``source_language`` may be any language with a heading table, not only ``en``."""

    def setUp(self) -> None:
        from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR

        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        # a second language ("fr") whose table is a copy of de.json (redirected through the loader's path seam)
        original = heading_table_module.heading_table_path
        copy = self.docs_root / "fr.json"
        copy.write_text(original("de").read_text(encoding="utf-8"), encoding="utf-8")
        self.enterContext(
            mock.patch.object(
                heading_table_module,
                "heading_table_path",
                side_effect=lambda language: copy if language == "fr" else original(language),
            )
        )
        heading_table_module.reset_heading_table_cache()
        self.addCleanup(heading_table_module.reset_heading_table_cache)
        SPECS_BY_NAME["dec"].reset_cache()

    def test_a_non_en_source_is_compared_through_its_own_table(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id = spec.fn("create")(spec.en_body()).id
        spec.fn("create")(spec.de_body(), language="de", id=doc_id)
        spec.fn("create")(spec.de_body(), language="fr", id=doc_id)

        result = check_translation_drift("dec", doc_id, "fr", source_language="de")

        self.assertEqual((result.source_language, result.language), ("de", "fr"))
        self.assertEqual(result.structural, [])
        self.assertEqual(Path(result.source_path).parent.name, "de")
        self.assertEqual(Path(result.variant_path).parent.name, "fr")

    def test_a_non_en_source_reports_drift_too(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id = spec.fn("create")(spec.en_body()).id
        spec.fn("create")(spec.de_body(), language="de", id=doc_id)
        spec.fn("create")(spec.de_body(), language="fr", id=doc_id)
        fr_file = spec.base_dir("fr").glob("*.md").__next__()
        rewrite_body(fr_file, lambda body: body.replace("## Weitere Informationen", "## Weitere Infos"))

        result = check_translation_drift("dec", doc_id, "fr", source_language="de")

        self.assertEqual(
            [(f.kind, f.heading) for f in result.structural if f.kind != "unparseable"],
            [
                ("missing", "More Information"),
                ("extra", "Weitere Infos"),
            ],
        )

    def test_en_as_the_variant_is_rejected_even_with_a_non_en_source(self):
        with self.assertRaises(ValueError):
            check_translation_drift("dec", _MISSING_UUID, "en", source_language="de")


class TestGuardsBeforeAnyFilesystemAccess(_TempDocsMixin):
    """``type``/``id``/``language``/``source_language`` are validated before any filesystem access."""

    def _assert_rejected(self, *args: object, **kwargs: object) -> ValueError:
        with mock.patch(_LOCATE) as locate_probe:
            with self.assertRaises(ValueError) as ctx:
                check_translation_drift(*args, **kwargs)  # type: ignore[arg-type]
            locate_probe.assert_not_called()
        return ctx.exception

    def test_path_injection_and_wrong_format_ids(self):
        for bad_id in ("../../etc/passwd", "..", "a/b", "a\\b", "", "   ", "not-a-uuid"):
            with self.subTest(id=bad_id):
                self._assert_rejected("dec", bad_id, "de")

    def test_unknown_type(self):
        for bad_type in ("zzz", "", "../dec", "DEC"):
            with self.subTest(type=bad_type):
                self._assert_rejected(bad_type, _MISSING_UUID, "de")

    def test_feat_and_adr_with_the_permanent_wording(self):
        for type_, id_ in (("feat", "feat-197-i18n"), ("feat", _MISSING_UUID), ("adr", _MISSING_UUID)):
            with self.subTest(type=type_, id=id_):
                error = self._assert_rejected(type_, id_, "de")
                self.assertIn(f"{type_} documents are always English", str(error))

    def test_language_shape_matrix(self):
        for bad_language in ("../../etc", "de/x", "DE", "d", "deu", "", "d1", "/abs", "..", "e n"):
            with self.subTest(language=bad_language):
                self._assert_rejected("dec", _MISSING_UUID, bad_language)

    def test_source_language_shape_matrix(self):
        for bad_language in ("../../etc", "de/x", "EN", "e", "eng", "", "/abs"):
            with self.subTest(source_language=bad_language):
                self._assert_rejected("dec", _MISSING_UUID, "de", bad_language)

    def test_table_less_languages_are_rejected_for_either_side(self):
        error = self._assert_rejected("dec", _MISSING_UUID, "fr")
        self.assertIn("no heading-mapping table for language 'fr'", str(error))
        error = self._assert_rejected("dec", _MISSING_UUID, "de", "fr")
        self.assertIn("no heading-mapping table for language 'fr'", str(error))

    def test_en_is_never_the_variant(self):
        error = self._assert_rejected("dec", _MISSING_UUID, "en")
        self.assertIn("never a translation target", str(error))

    def test_equal_languages_are_rejected(self):
        error = self._assert_rejected("dec", _MISSING_UUID, "de", "de")
        self.assertIn("must differ", str(error))

    def test_every_language_aware_domain_passes_the_guards(self):
        for domain in LANGUAGE_AWARE_DOMAINS:
            with self.subTest(domain=domain):
                with self.assertRaises(LookupError):  # past the guards: only the not-found of a missing id
                    check_translation_drift(domain, _MISSING_UUID, "de")


class TestNotFound(_TempDocsMixin):
    """A truly absent source or variant raises the domain's own not-found error (naming the missing side)."""

    def test_missing_variant_raises_not_found_naming_the_variant(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                created = spec.fn("create")(spec.en_body())

                with self.assertRaises(spec.not_found_error()) as ctx:
                    check_translation_drift(spec.d, created.id, "de")

                self.assertIn("variant", str(ctx.exception))
                self.assertIn("'de'", str(ctx.exception))

    def test_missing_source_raises_not_found_naming_the_source(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, en_file, _de_file = self.seed(spec)
        en_file.unlink()
        spec.reset_cache()

        with self.assertRaises(spec.not_found_error()) as ctx:
            check_translation_drift("dec", doc_id, "de")

        self.assertIn("source", str(ctx.exception))
        self.assertIn("'en'", str(ctx.exception))

    def test_unknown_id_raises_not_found(self):
        with self.assertRaises(LookupError):
            check_translation_drift("req", _MISSING_UUID, "de")


class TestReadOnly(_TempDocsMixin):
    """The tool never writes, creates, touches, or cache-invalidates anything."""

    def test_the_docs_tree_is_byte_and_mtime_identical_after_any_outcome(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, en_file, de_file = self.seed(spec)
        scenarios: list[Callable[[], None]] = [
            lambda: None,
            lambda: rewrite_body(de_file, lambda body: body.replace("## Quelle", "## Falsch")),
            lambda: set_updated(en_file, "2099-01-01T00:00:00.000Z"),
            lambda: de_file.write_text("---\nnot: [valid\n---\n", encoding="utf-8"),
        ]
        for index, scenario in enumerate(scenarios):
            with self.subTest(scenario=index):
                scenario()
                before = snapshot(self.docs_root)

                check_translation_drift("dec", doc_id, "de")
                check_translation_drift("dec", doc_id, "de")

                self.assertEqual(snapshot(self.docs_root), before)

    def test_no_cache_entry_is_invalidated_or_written(self):
        spec = SPECS_BY_NAME["dec"]
        doc_id, _en_file, _de_file = self.seed(spec)

        with mock.patch("biz.dfch.specmgr.general.tools._doc_cache.DocCache.invalidate") as invalidate:
            check_translation_drift("dec", doc_id, "de")

        invalidate.assert_not_called()

    def test_a_missing_variant_creates_no_directory(self):
        spec = SPECS_BY_NAME["dec"]
        created = spec.fn("create")(spec.en_body())
        before = snapshot(self.docs_root)

        with self.assertRaises(LookupError):
            check_translation_drift("dec", created.id, "de")

        self.assertEqual(snapshot(self.docs_root), before)
        self.assertFalse(spec.base_dir("de").exists())

    def test_every_domain_leaves_its_tree_untouched(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, _en_file, _de_file = self.seed(spec)
                before = snapshot(self.docs_root)

                check_translation_drift(spec.d, doc_id, "de")

                self.assertEqual(snapshot(self.docs_root), before)


class TestRegistration(unittest.TestCase):
    """The tool is a registered MCP tool with a precise schema."""

    def test_registered_with_the_expected_parameters(self):
        from biz.dfch.specmgr.server import mcp

        tools = {tool.name: tool for tool in asyncio.run(mcp.list_tools())}

        self.assertIn("check_translation_drift", tools)
        schema = tools["check_translation_drift"].input_schema
        self.assertEqual(set(schema["properties"]), {"type", "id", "language", "source_language"})
        self.assertEqual(set(schema["required"]), {"type", "id", "language"})
        self.assertEqual(schema["properties"]["source_language"]["default"], "en")
        self.assertEqual(set(schema["properties"]["type"]["enum"]), set(ALL_DOMAINS))

    def test_the_description_states_the_contract(self):
        from biz.dfch.specmgr.server import mcp

        tools = {tool.name: tool for tool in asyncio.run(mcp.list_tools())}
        description = tools["check_translation_drift"].description

        for phrase in ("Read-only", "missing", "extra", "reordered", "stale", "in_sync", "unparseable", "never 'en'"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, description)


if __name__ == "__main__":
    unittest.main()
