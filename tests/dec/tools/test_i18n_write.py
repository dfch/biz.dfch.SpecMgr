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

"""Tests for the ``dec`` domain's write-side ``language`` support (feat-197-i18n Phase 120, ADR 38efdb66).

Pins the pilot-domain write side: ``create_dec``'s variant creation (requires
the EN source, shared id, EN basename, no overwrite), and the generic
``update``/``edit``/``set_status``/``set_classification``/``delete`` tools'
``language="de"`` path acting on the DE variant ONLY (ACC-006, all six
write tools), the Task 120.110 cache-isolation confirmation (``DocCache``'s
``Path`` keying needs no code change), the Task 120.120 end-to-end REQ-003
shared-id test, and the non-raising ``ParseFailureResult``/not-found
channels for a DE variant.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.dec.models.v1 import DecDocument, DecFrontmatter
from biz.dfch.specmgr.dec.tools._cache import _cache, read_dec, reset_dec_cache
from biz.dfch.specmgr.dec.tools._lock import dec_lock_key
from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError, dec_base_dir
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.dec.tools.get_dec import get_dec
from biz.dfch.specmgr.dec.tools.list_dec import list_dec
from biz.dfch.specmgr.general.models import InvalidStatusResult, ParseFailureResult, UpdateResult, ValidateResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.general.tools.delete import delete
from biz.dfch.specmgr.general.tools.edit import edit
from biz.dfch.specmgr.general.tools.set_classification import set_classification
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.general.tools.update import update

from .test_i18n_language import _DE_BODY, _EN_BODY, _MISSING_UUID

#: A fixed timestamp every patched ``now_timestamp`` returns, so a write's ``updated`` bump is
#: deterministic and distinguishable from the seeded timestamps.
_FIXED_NOW = "2031-02-03T04:05:06.007+00:00"

_DE_OUTCOME_OLD = "Wir haben das Dokumentlager gew\u00e4hlt."
_DE_OUTCOME_NEW = "Wir haben die Datenbank gew\u00e4hlt."


def _seed(docs_root: Path) -> tuple[str, Path, Path]:
    """Create the EN document and its DE variant, both through ``create_dec``; return (id, en_path, de_path)."""
    created = create_dec(_EN_BODY)
    assert isinstance(created, DecFrontmatter)
    assert created.id is not None
    variant = create_dec(_DE_BODY, language="de", id=created.id)
    assert isinstance(variant, DecFrontmatter)
    en_path = next((docs_root / "dec").glob("*.md"))
    de_path = docs_root / "dec" / "de" / en_path.name
    return created.id, en_path, de_path


class _TempDocsTestCase(unittest.TestCase):
    """Common fixture: a temp docs root, a clean dec cache, and the seeded EN + DE pair."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        reset_dec_cache()
        self.doc_id, self.en_path, self.de_path = _seed(self.docs_root)
        self.en_bytes = self.en_path.read_bytes()
        self.en_updated = self._updated(self.en_path)

    def _updated(self, path: Path) -> str:
        """Return the ``updated`` frontmatter value of the document at ``path`` (read straight from the cache-backed reader)."""
        doc = read_dec(path)
        assert doc.frontmatter.updated is not None
        return doc.frontmatter.updated

    def assert_en_untouched(self) -> None:
        """The EN file's bytes and ``updated`` timestamp must be exactly as seeded (ACC-006)."""
        self.assertEqual(self.en_path.read_bytes(), self.en_bytes)
        self.assertEqual(self._updated(self.en_path), self.en_updated)


class TestCreateDecVariant(_TempDocsTestCase):
    """create_dec(language=..., id=...) (ACC-006 create, ACC-007 write half, REQ-003, ADR item 2)."""

    def test_variant_is_written_under_the_en_basename_in_the_language_subfolder(self):
        """The DE variant must live at docs/dec/de/ under the EN source's exact basename (ADR item 2)."""
        self.assertTrue(self.de_path.exists())
        self.assertEqual(self.de_path.parent, dec_base_dir("de"))
        self.assertEqual(self.de_path.name, self.en_path.name)
        self.assertEqual([p.name for p in (self.docs_root / "dec" / "de").glob("*.md")], [self.en_path.name])

    def test_variant_carries_the_shared_id_and_introduces_no_duplicate(self):
        """The DE frontmatter id must equal the EN id (REQ-003); the EN dir still holds one document,
        each language lists exactly one row with that id (ACC-003/ACC-007)."""
        de_doc = get_dec(self.doc_id, language="de")
        en_doc = get_dec(self.doc_id)
        assert isinstance(de_doc, DecDocument) and isinstance(en_doc, DecDocument)
        self.assertEqual(de_doc.frontmatter.id, self.doc_id)
        self.assertEqual(en_doc.frontmatter.id, self.doc_id)
        self.assertEqual(len(list((self.docs_root / "dec").glob("*.md"))), 1)
        en_rows = list_dec()
        de_rows = list_dec(language="de")
        self.assertEqual((en_rows.total, de_rows.total), (1, 1))
        self.assertEqual(en_rows.results[0].id, self.doc_id)
        self.assertEqual(de_rows.results[0].id, self.doc_id)

    def test_variant_is_draft_with_fresh_timestamps_and_the_en_file_is_untouched(self):
        """The variant is a fresh draft document; creating it never touches the EN file (ACC-006)."""
        de_doc = get_dec(self.doc_id, language="de")
        assert isinstance(de_doc, DecDocument)
        self.assertEqual(de_doc.frontmatter.status, "draft")
        self.assertEqual(de_doc.frontmatter.type, "dec")
        self.assert_en_untouched()

    def test_german_headings_are_accepted_via_the_table_and_persisted_verbatim(self):
        """The translated body is validated through the de table and written byte-for-byte (translation preserved)."""
        raw = get_dec(self.doc_id, language="de", raw=True)
        self.assertIn("## Kontext und Problembeschreibung", raw)
        self.assertEqual(raw.rstrip("\n"), _DE_BODY.rstrip("\n"))

    def test_invalid_variant_content_is_a_non_raising_validate_result(self):
        """A body whose headings neither translate nor match canonical keys is a non-raising ValidateResult, nothing written."""
        before = sorted(p.name for p in (self.docs_root / "dec" / "de").glob("*.md"))
        other = create_dec("# T\n\nJust a paragraph.\n", language="de", id=self.doc_id)
        self.assertIsInstance(other, ValidateResult)
        self.assertFalse(other.valid)
        self.assertEqual(sorted(p.name for p in (self.docs_root / "dec" / "de").glob("*.md")), before)

    def test_existing_variant_is_never_overwritten(self):
        """A second create of the same id+language must raise FileExistsError and leave the file byte-identical."""
        before = self.de_path.read_bytes()
        with self.assertRaises(FileExistsError):
            create_dec(_DE_BODY, language="de", id=self.doc_id)
        self.assertEqual(self.de_path.read_bytes(), before)

    def test_variant_requires_the_en_source(self):
        """A variant of an id with no EN source must raise DecNotFoundError and write nothing (ADR item 2)."""
        with self.assertRaises(DecNotFoundError) as ctx:
            create_dec(_DE_BODY, language="de", id=_MISSING_UUID)
        self.assertIn("requires its 'en' source", str(ctx.exception))
        self.assertEqual(len(list((self.docs_root / "dec" / "de").glob("*.md"))), 1)

    def test_variant_requires_the_en_source_even_if_a_variant_exists(self):
        """Only the flat EN directory counts as the source: once the EN file is gone, the existing DE
        variant cannot stand in for it (the source lookup runs before the existing-variant guard)."""
        delete(self.doc_id, "dec")  # remove the EN file; the DE variant stays
        with self.assertRaises(DecNotFoundError):
            create_dec(_DE_BODY, language="de", id=self.doc_id)

    def test_variant_without_id_is_rejected_before_any_filesystem_access(self):
        """A non-default language without the id-mapping parameter is a ValueError before any FS access."""
        with mock.patch("biz.dfch.specmgr.dec.tools.create_dec.find_dec_path", side_effect=AssertionError("no")):
            with self.assertRaises(ValueError) as ctx:
                create_dec(_DE_BODY, language="de")
        self.assertIn("id is required", str(ctx.exception))

    def test_id_for_the_default_language_is_rejected(self):
        """Supplying the id-mapping parameter for the default language is a ValueError; EN create stays server-assigned."""
        for language in ("en",):
            with self.subTest(language=language):
                with self.assertRaises(ValueError) as ctx:
                    create_dec(_EN_BODY, language=language, id=self.doc_id)
                self.assertIn("non-default language", str(ctx.exception))
        with self.assertRaises(ValueError):
            create_dec(_EN_BODY, id=self.doc_id)
        self.assertEqual(len(list((self.docs_root / "dec").glob("*.md"))), 1)

    def test_malformed_variant_id_is_rejected_before_any_filesystem_access(self):
        """A path-injection-shaped id is a ValueError before any FS access."""
        with mock.patch("biz.dfch.specmgr.dec.tools.create_dec.find_dec_path", side_effect=AssertionError("no")):
            for bad_id in ("../../x", "not-a-uuid", "", "dec-" + self.doc_id):
                with self.subTest(id=bad_id):
                    with self.assertRaises(ValueError):
                        create_dec(_DE_BODY, language="de", id=bad_id)

    def test_bad_and_unusable_languages_are_rejected_before_any_filesystem_access(self):
        """ACC-013 for create_dec: malformed languages and table-less ones ('fr') never reach the filesystem."""
        with (
            mock.patch("biz.dfch.specmgr.dec.tools.create_dec.find_dec_path", side_effect=AssertionError("no")),
            mock.patch("biz.dfch.specmgr.dec.tools.create_dec.ensure_dec_base_dir", side_effect=AssertionError("no")),
        ):
            for value in ("", "d", "DE", "../../etc", "de/x", "/abs", "de3"):
                with self.subTest(value=value):
                    with self.assertRaises(ValueError) as ctx:
                        create_dec(_DE_BODY, language=value, id=self.doc_id)
                    self.assertIn(repr(value), str(ctx.exception))
            with self.assertRaises(ValueError) as ctx:
                create_dec(_DE_BODY, language="fr", id=self.doc_id)
            self.assertIn("no heading-mapping table", str(ctx.exception))
        self.assertFalse((self.docs_root / "dec" / "fr").exists())

    def test_default_create_is_unchanged(self):
        """create_dec(content) without language/id assigns a fresh id and writes the flat file as before."""
        created = create_dec(_EN_BODY)
        assert isinstance(created, DecFrontmatter)
        self.assertNotEqual(created.id, self.doc_id)
        self.assertEqual(len(list((self.docs_root / "dec").glob("*.md"))), 2)

    def test_create_variant_uses_a_fixed_timestamp_for_created_and_updated(self):
        """created/updated of a variant come from the shared now_timestamp (same ms) like any create."""
        delete(self.doc_id, "dec", language="de")
        with mock.patch("biz.dfch.specmgr.dec.tools.create_dec.now_timestamp", return_value=_FIXED_NOW):
            variant = create_dec(_DE_BODY, language="de", id=self.doc_id)
        assert isinstance(variant, DecFrontmatter)
        self.assertEqual((variant.created, variant.updated), (_FIXED_NOW, _FIXED_NOW))
        self.assert_en_untouched()


class TestWriteToolsActOnTheDeVariantOnly(_TempDocsTestCase):
    """ACC-006: each write tool with language='de' acts on the DE variant path only (EN bytes/updated untouched)."""

    def test_update_whole_body(self):
        """update(language='de') whole-body mode rewrites only the DE file."""
        new_body = _DE_BODY.replace(_DE_OUTCOME_OLD, _DE_OUTCOME_NEW)
        with mock.patch("biz.dfch.specmgr.general.tools.update.now_timestamp", return_value=_FIXED_NOW):
            result = update(self.doc_id, "dec", new_body, language="de")
        self.assertIsInstance(result, UpdateResult)
        assert isinstance(result, UpdateResult)
        self.assertEqual(result.frontmatter.id, self.doc_id)
        self.assertIsNone(result.snippet)
        self.assertIn(_DE_OUTCOME_NEW, body_text(self.de_path))
        self.assertNotIn(_DE_OUTCOME_OLD, body_text(self.de_path))
        self.assertEqual(self._updated(self.de_path), _FIXED_NOW)
        self.assert_en_untouched()

    def test_update_range_mode(self):
        """update(language='de') range mode addresses the DE variant's own raw body lines."""
        lines = get_dec(self.doc_id, language="de", raw=True).splitlines()
        k = lines.index(_DE_OUTCOME_OLD) + 1
        with mock.patch("biz.dfch.specmgr.general.tools.update.now_timestamp", return_value=_FIXED_NOW):
            result = update(self.doc_id, "dec", _DE_OUTCOME_NEW, offset=k, limit=1, language="de")
        self.assertIsInstance(result, UpdateResult)
        assert isinstance(result, UpdateResult)
        self.assertIsNotNone(result.snippet)
        self.assertIn(_DE_OUTCOME_NEW, body_text(self.de_path))
        self.assertEqual(self._updated(self.de_path), _FIXED_NOW)
        self.assert_en_untouched()

    def test_update_validates_through_the_variant_table(self):
        """German headings are accepted for a de update; the same body is a non-raising ValidateResult for EN."""
        new_body = _DE_BODY.replace(_DE_OUTCOME_OLD, _DE_OUTCOME_NEW)
        ok = update(self.doc_id, "dec", new_body, language="de")
        self.assertIsInstance(ok, UpdateResult)
        bad = update(self.doc_id, "dec", new_body)  # EN: German headings do not match the canonical keys
        self.assertIsInstance(bad, ValidateResult)
        self.assert_en_untouched()

    def test_update_invalid_content_returns_validate_result_and_writes_nothing(self):
        """A content-validation failure for a de update is the non-raising ValidateResult; the DE file is unchanged."""
        before = self.de_path.read_bytes()
        result = update(self.doc_id, "dec", "# T\n\nJust a paragraph.\n", language="de")
        self.assertIsInstance(result, ValidateResult)
        self.assertEqual(self.de_path.read_bytes(), before)
        self.assert_en_untouched()

    def test_edit(self):
        """edit(language='de') matches against and rewrites only the DE variant's body."""
        with mock.patch("biz.dfch.specmgr.general.tools.edit.now_timestamp", return_value=_FIXED_NOW):
            result = edit(self.doc_id, "dec", _DE_OUTCOME_OLD, _DE_OUTCOME_NEW, language="de")
        self.assertIsInstance(result, DecFrontmatter)
        self.assertIn(_DE_OUTCOME_NEW, body_text(self.de_path))
        self.assertEqual(self._updated(self.de_path), _FIXED_NOW)
        self.assert_en_untouched()

    def test_edit_matches_the_variant_body_not_the_en_body(self):
        """The stage-1 match runs against the DE body: the German text is not found in the EN document."""
        with self.assertRaises(ValueError) as ctx:
            edit(self.doc_id, "dec", _DE_OUTCOME_OLD, _DE_OUTCOME_NEW)
        self.assertIn("Could not find oldString", str(ctx.exception))
        self.assert_en_untouched()

    def test_edit_validates_the_edited_body_through_the_variant_table(self):
        """Breaking a (German) heading is a stage-2 non-raising ValidateResult; the DE file is unchanged."""
        before = self.de_path.read_bytes()
        result = edit(self.doc_id, "dec", "## Entscheidungsergebnis", "## Kaputt", language="de")
        self.assertIsInstance(result, ValidateResult)
        self.assertEqual(self.de_path.read_bytes(), before)
        self.assert_en_untouched()

    def test_set_status(self):
        """set_status(language='de') changes the DE status only; the EN document keeps its status and updated."""
        with mock.patch("biz.dfch.specmgr.general.tools.set_status.now_timestamp", return_value=_FIXED_NOW):
            result = set_status(self.doc_id, "dec", "accepted", language="de")
        self.assertIsInstance(result, DecFrontmatter)
        assert isinstance(result, DecFrontmatter)
        self.assertEqual(result.status, "accepted")
        de_doc = get_dec(self.doc_id, language="de")
        en_doc = get_dec(self.doc_id)
        assert isinstance(de_doc, DecDocument) and isinstance(en_doc, DecDocument)
        self.assertEqual(de_doc.frontmatter.status, "accepted")
        self.assertEqual(de_doc.frontmatter.updated, _FIXED_NOW)
        self.assertEqual(en_doc.frontmatter.status, "draft")
        self.assert_en_untouched()

    def test_set_status_same_status_is_a_noop_on_the_variant(self):
        """The unchanged-status no-op compares against the DE variant: no write, no updated bump (issue #109)."""
        de_before = self.de_path.read_bytes()
        result = set_status(self.doc_id, "dec", "draft", language="de")
        self.assertIsInstance(result, DecFrontmatter)
        self.assertEqual(self.de_path.read_bytes(), de_before)
        self.assert_en_untouched()

    def test_set_status_noop_compares_against_the_variant_not_en(self):
        """When EN is accepted and DE draft, set_status('accepted', language='de') is a real change, not a no-op."""
        set_status(self.doc_id, "dec", "accepted")  # EN -> accepted
        en_bytes = self.en_path.read_bytes()
        result = set_status(self.doc_id, "dec", "accepted", language="de")
        assert isinstance(result, DecFrontmatter)
        self.assertEqual(result.status, "accepted")
        self.assertEqual(get_dec(self.doc_id, language="de").frontmatter.status, "accepted")
        self.assertEqual(self.en_path.read_bytes(), en_bytes)

    def test_set_status_invalid_status_is_the_non_raising_result_before_lock_and_load(self):
        """InvalidStatusResult still runs pre-lock/pre-load for the language path; nothing is written."""
        de_before = self.de_path.read_bytes()
        with mock.patch("biz.dfch.specmgr.general.tools.set_status.load_dec_by_id", side_effect=AssertionError("no")):
            result = set_status(self.doc_id, "dec", "bogus", language="de")
        self.assertIsInstance(result, InvalidStatusResult)
        self.assertEqual(self.de_path.read_bytes(), de_before)
        self.assert_en_untouched()

    def test_set_classification(self):
        """set_classification(language='de') sets the DE classification only."""
        with mock.patch("biz.dfch.specmgr.general.tools.set_classification.now_timestamp", return_value=_FIXED_NOW):
            result = set_classification(self.doc_id, "dec", "intern", language="de")
        self.assertIsInstance(result, DecFrontmatter)
        assert isinstance(result, DecFrontmatter)
        self.assertEqual(result.classification, "intern")
        de_doc = get_dec(self.doc_id, language="de")
        assert isinstance(de_doc, DecDocument)
        self.assertEqual(de_doc.frontmatter.classification, "intern")
        self.assertEqual(de_doc.frontmatter.updated, _FIXED_NOW)
        en_doc = get_dec(self.doc_id)
        assert isinstance(en_doc, DecDocument)
        self.assertIsNone(en_doc.frontmatter.classification)
        self.assert_en_untouched()

    def test_delete(self):
        """delete(language='de') removes only the DE variant file; EN stays on disk, cached and readable."""
        result = delete(self.doc_id, "dec", language="de")
        self.assertEqual(Path(result), self.de_path)
        self.assertFalse(self.de_path.exists())
        self.assertTrue(self.en_path.exists())
        self.assert_en_untouched()
        en_doc = get_dec(self.doc_id)
        self.assertIsInstance(en_doc, DecDocument)
        with self.assertRaises(DecNotFoundError):
            get_dec(self.doc_id, language="de")
        self.assertEqual(list_dec().total, 1)
        self.assertEqual(list_dec(language="de").total, 0)

    def test_delete_en_leaves_the_de_variant(self):
        """The reverse direction: delete(id) without language removes only the EN file."""
        de_bytes = self.de_path.read_bytes()
        delete(self.doc_id, "dec")
        self.assertFalse(self.en_path.exists())
        self.assertEqual(self.de_path.read_bytes(), de_bytes)
        self.assertIsInstance(get_dec(self.doc_id, language="de"), DecDocument)

    def test_omitted_and_explicit_en_language_target_the_en_file(self):
        """language omitted and language='en' are interchangeable and act on the flat EN file only."""
        de_bytes = self.de_path.read_bytes()
        set_classification(self.doc_id, "dec", "oeffentlich")
        set_classification(self.doc_id, "dec", "public", language="en")
        en_doc = get_dec(self.doc_id)
        assert isinstance(en_doc, DecDocument)
        self.assertEqual(en_doc.frontmatter.classification, "public")
        self.assertEqual(self.de_path.read_bytes(), de_bytes)


class TestWriteToolsAbsentAndBrokenVariants(_TempDocsTestCase):
    """The not-found and non-raising ParseFailureResult channels for a DE variant."""

    def _break_de(self) -> None:
        broken = self.de_path.read_text(encoding="utf-8").replace("## Entscheidungsergebnis", "## BROKEN-HEADING")
        self.de_path.write_text(broken, encoding="utf-8")
        reset_dec_cache()

    def test_absent_variant_id_raises_not_found_even_if_en_exists(self):
        """A truly-absent DE id raises DecNotFoundError in every write tool, although the EN document exists."""
        delete(self.doc_id, "dec", language="de")
        calls = {
            "update": lambda: update(self.doc_id, "dec", _DE_BODY, language="de"),
            "edit": lambda: edit(self.doc_id, "dec", "a", "b", language="de"),
            "set_status": lambda: set_status(self.doc_id, "dec", "accepted", language="de"),
            "set_classification": lambda: set_classification(self.doc_id, "dec", "x", language="de"),
            "delete": lambda: delete(self.doc_id, "dec", language="de"),
        }
        for name, call in calls.items():
            with self.subTest(tool=name):
                with self.assertRaises(DecNotFoundError):
                    call()
        self.assert_en_untouched()

    def test_broken_variant_returns_parse_failure_result_byte_identical_to_the_list_row(self):
        """update/edit/set_status/set_classification on a broken DE variant return ParseFailureResult whose
        error/path match list_dec(language='de')'s failed row; nothing is written."""
        self._break_de()
        broken_bytes = self.de_path.read_bytes()
        row = list_dec(language="de").results[0]
        self.assertEqual(row.title, "<failed to parse>")
        results = {
            "update": update(self.doc_id, "dec", _DE_BODY, offset=1, limit=0, language="de"),
            "edit": edit(self.doc_id, "dec", "a", "b", language="de"),
            "set_status": set_status(self.doc_id, "dec", "accepted", language="de"),
            "set_classification": set_classification(self.doc_id, "dec", "x", language="de"),
        }
        for name, result in results.items():
            with self.subTest(tool=name):
                self.assertIsInstance(result, ParseFailureResult)
                assert isinstance(result, ParseFailureResult)
                self.assertEqual(result.error, row.error)
                self.assertEqual(result.path, row.path)
                self.assertEqual(result.id, self.doc_id)
        self.assertEqual(self.de_path.read_bytes(), broken_bytes)
        self.assert_en_untouched()

    def test_broken_variant_does_not_affect_the_en_write_channels(self):
        """A broken DE variant leaves the EN document fully writable."""
        self._break_de()
        result = set_status(self.doc_id, "dec", "accepted")
        self.assertIsInstance(result, DecFrontmatter)


class TestDocCacheKeepsLanguagesIndependent(_TempDocsTestCase):
    """Task 120.110: DocCache's Path-keyed entries keep EN and DE of one id from colliding -- no cache code change."""

    def test_cache_holds_one_entry_per_path(self):
        """After reading both languages the cache has two distinct path-keyed entries for the one id."""
        get_dec(self.doc_id)
        get_dec(self.doc_id, language="de")
        keys = set(_cache._entries)
        self.assertIn(self.en_path.resolve(), keys)
        self.assertIn(self.de_path.resolve(), keys)
        self.assertEqual(len([k for k in keys if self.doc_id in k.name]), 2)

    def test_interleaved_reads_and_writes_never_return_each_others_content(self):
        """Interleaved tool reads/writes of EN and DE never leak content across languages."""
        self.assertEqual(get_dec(self.doc_id).body.text, "Choose a Document Store")
        self.assertEqual(get_dec(self.doc_id, language="de").body.text, "Dokumentlager w\u00e4hlen")

        edit(self.doc_id, "dec", _DE_OUTCOME_OLD, _DE_OUTCOME_NEW, language="de")
        self.assertEqual(get_dec(self.doc_id).body.outcome.statement.text, "We chose the document store.")
        self.assertEqual(get_dec(self.doc_id, language="de").body.outcome.statement.text, _DE_OUTCOME_NEW)

        edit(self.doc_id, "dec", "We chose the document store.", "We chose the database.")
        self.assertEqual(get_dec(self.doc_id).body.outcome.statement.text, "We chose the database.")
        self.assertEqual(get_dec(self.doc_id, language="de").body.outcome.statement.text, _DE_OUTCOME_NEW)

        set_status(self.doc_id, "dec", "accepted", language="de")
        self.assertEqual(get_dec(self.doc_id).frontmatter.status, "draft")
        self.assertEqual(get_dec(self.doc_id, language="de").frontmatter.status, "accepted")

    def test_write_warming_of_one_language_does_not_evict_or_corrupt_the_other(self):
        """A write warms only its own path's entry: the other language's cached entry object is unchanged."""
        en_entry = _cache._entries[self.en_path.resolve()]
        de_entry_before = _cache._entries[self.de_path.resolve()]
        set_classification(self.doc_id, "dec", "intern", language="de")
        self.assertIs(_cache._entries[self.en_path.resolve()], en_entry)
        self.assertIsNot(_cache._entries[self.de_path.resolve()], de_entry_before)

    def test_delete_of_de_invalidates_only_its_own_entry(self):
        """delete(language='de') drops only the DE entry; the EN entry stays cached and readable."""
        get_dec(self.doc_id)
        get_dec(self.doc_id, language="de")
        en_entry = _cache._entries[self.en_path.resolve()]
        delete(self.doc_id, "dec", language="de")
        self.assertNotIn(self.de_path.resolve(), _cache._entries)
        self.assertIs(_cache._entries[self.en_path.resolve()], en_entry)
        self.assertEqual(get_dec(self.doc_id).body.text, "Choose a Document Store")

    def test_scanning_one_language_does_not_evict_the_other_languages_entries(self):
        """A de id-scan (reconcile) keeps the EN entry and an EN scan keeps the DE entry (domain-wide reconcile)."""
        list_dec()
        list_dec(language="de")
        self.assertIn(self.en_path.resolve(), _cache._entries)
        self.assertIn(self.de_path.resolve(), _cache._entries)

    def test_lock_keys_are_per_language(self):
        """The EN lock key is the bare id (unchanged); a variant's key is distinct, never colliding with an id."""
        self.assertEqual(dec_lock_key(self.doc_id), self.doc_id)
        self.assertEqual(dec_lock_key(self.doc_id, "en"), self.doc_id)
        self.assertEqual(dec_lock_key(self.doc_id, "de"), f"{self.doc_id}/de")
        self.assertNotEqual(dec_lock_key(self.doc_id, "de"), dec_lock_key(self.doc_id, "fr"))


class TestSharedIdEndToEnd(_TempDocsTestCase):
    """Task 120.120 (REQ-003, ACC-003/ACC-007): translating never changes or duplicates the shared id,
    and never touches the EN variant's content or updated timestamp."""

    def test_end_to_end_translation_lifecycle(self):
        """create EN -> create DE (setUp) -> update DE -> set_status DE -> read both: ids identical, one id per
        language directory, EN bytes/updated untouched throughout."""
        update(self.doc_id, "dec", _DE_BODY.replace(_DE_OUTCOME_OLD, _DE_OUTCOME_NEW), language="de")
        self.assert_en_untouched()
        set_status(self.doc_id, "dec", "proposed", language="de")
        self.assert_en_untouched()
        edit(self.doc_id, "dec", _DE_OUTCOME_NEW, _DE_OUTCOME_OLD, language="de")
        self.assert_en_untouched()

        en_doc = get_dec(self.doc_id)
        de_doc = get_dec(self.doc_id, language="de")
        assert isinstance(en_doc, DecDocument) and isinstance(de_doc, DecDocument)
        self.assertEqual(en_doc.frontmatter.id, self.doc_id)
        self.assertEqual(de_doc.frontmatter.id, self.doc_id)
        self.assertEqual(en_doc.frontmatter.status, "draft")
        self.assertEqual(de_doc.frontmatter.status, "proposed")

        en_ids = [row.id for row in list_dec().results]
        de_ids = [row.id for row in list_dec(language="de").results]
        self.assertEqual(en_ids, [self.doc_id])
        self.assertEqual(de_ids, [self.doc_id])
        self.assertEqual(len(list((self.docs_root / "dec").glob("*.md"))), 1)
        self.assertEqual(len(list((self.docs_root / "dec" / "de").glob("*.md"))), 1)
        self.assertEqual(
            sorted(p.name for p in (self.docs_root / "dec").glob("*.md")),
            sorted(p.name for p in (self.docs_root / "dec" / "de").glob("*.md")),
        )

    def test_the_variant_frontmatter_id_survives_every_write_tool(self):
        """No write tool ever alters the frontmatter id of the variant."""
        update(self.doc_id, "dec", _DE_BODY, language="de")
        set_status(self.doc_id, "dec", "accepted", language="de")
        set_classification(self.doc_id, "dec", "intern", language="de")
        edit(self.doc_id, "dec", _DE_OUTCOME_OLD, _DE_OUTCOME_NEW, language="de")
        de_doc = get_dec(self.doc_id, language="de")
        assert isinstance(de_doc, DecDocument)
        self.assertEqual(de_doc.frontmatter.id, self.doc_id)
        self.assertEqual(de_doc.frontmatter.type, "dec")


if __name__ == "__main__":
    unittest.main()
