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

"""Tests for the ``dec`` domain's read-side ``language`` support (feat-197-i18n Phase 110, ADR 38efdb66).

Pins the pilot-domain read side: ``get_dec``/``list_dec``'s optional
``language`` parameter (default ``"en"``, omitted = today's exact behavior),
the path-derived language of the ``parse_dec`` tool, the language guard's
before-filesystem-access rejection (ACC-013), the flat-scan non-recursive
property at the domain level (ACC-014 unit pin), the translated-headings-
resolve-to-canonical-keys behavior (ACC-004), the closed-vocabulary tokens
staying canonical (ACC-012 unit pin), the raw-read byte-identity
(ACC-005/ACC-007 read half), and the ``ParseFailureResult``/failed-row
byte-identity for a broken DE variant (the feat-150/162 contract, ADR
9080b37c, extended to language variants).
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.dec.models.v1 import DecDocument
from biz.dfch.specmgr.dec.models.v1.parser import parse_dec_body
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.dec.tools.get_dec import get_dec
from biz.dfch.specmgr.dec.tools.list_dec import list_dec
from biz.dfch.specmgr.dec.tools.parse_dec import parse_dec
from biz.dfch.specmgr.dec.tools._cache import reset_dec_cache
from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError, dec_base_dir, find_dec_path, iter_dec_paths
from biz.dfch.specmgr.general.models import ParseFailureResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._splice import body_text

from ._helpers import MANDATORY_ROLES_AND_SOURCE

#: A well-formed but non-existent canonical UUID (a valid id to reach the domain's
#: not-found error past the guards).
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"

#: The EN document body (the single filename authority: the DE variant is stored under the
#: EN source's exact basename, ADR 38efdb66 item 2).
_EN_BODY = (
    textwrap.dedent(
        """\
        # Choose a Document Store

        ## Context and Problem Statement

        The current store cannot serve the dashboard read path.

        ## Decision Outcome

        We chose the document store.
        """
    )
    + MANDATORY_ROLES_AND_SOURCE
)

#: The DE variant's body: every fixed-text heading translated (per the packaged de table), the
#: H1 free in German, the closed-vocabulary/schema-constant tokens kept canonical in the file
#: itself (``### Option 1:``/``### Option 2:`` with their numbers, the timestamp-led update
#: entry heading -- REQ-010/ACC-012), and a fenced code block carrying ``#``-leading lines
#: (including one that spells a translated heading) that the pre-pass must not touch.
_DE_BODY = textwrap.dedent(
    """\
    # Dokumentlager w\u00e4hlen

    ## Kontext und Problembeschreibung

    Der aktuelle Store kann den Dashboard-Lesepfad nicht bedienen.

    ```python
    # Kontext und Problembeschreibung
    choice = "document store"
    ```

    ## Entscheidungsergebnis

    Wir haben das Dokumentlager gew\u00e4hlt.

    ## Rollen und Verantwortlichkeiten

    ### Endverantwortlich

    Die f\u00fchrende Plattformarchitektin.

    ### Durchf\u00fchrend

    - Das Order-Service-Team.

    ## Quelle

    Die Incident-Review-Meeting zum Dashboard-Latenz-Vorfall.

    ## Pro und Contra

    ### Option 1: Kanban

    Prose \u00fcber Kanban.

    ### Option 2: Datenbank

    Prose \u00fcber die Datenbank.

    ## Aktualisierungen

    ### 2026-08-27T14:30:00.000+02:00 - Best\u00e4tigt

    Der Entscheidungsweg wurde best\u00e4tigt.
    """
)


def _seed_en_and_de(docs_root: Path) -> tuple[str, Path, Path]:
    """Create the EN document via ``create_dec`` and write its DE variant under the same basename.

    Returns the shared id, the EN file path, and the DE file path (the DE frontmatter is the EN
    frontmatter verbatim -- the language is encoded by directory location only, ADR item 1).
    """
    created = create_dec(_EN_BODY)
    assert created.id is not None  # create_dec always assigns the frontmatter id
    en_file = next((docs_root / "dec").glob("*.md"))
    de_dir = docs_root / "dec" / "de"
    de_dir.mkdir(parents=True)
    frontmatter = en_file.read_text(encoding="utf-8").split("---\n")[1]
    de_file = de_dir / en_file.name
    de_file.write_text(f"---\n{frontmatter}---\n{_DE_BODY}", encoding="utf-8")
    return created.id, en_file, de_file


class TestGetDecLanguage(unittest.TestCase):
    """Tests for get_dec's optional language parameter (ACC-005, ACC-013)."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        reset_dec_cache()
        self.doc_id, self.en_file, self.de_file = _seed_en_and_de(self.docs_root)

    def test_omitted_language_is_today_exact_behavior(self):
        """get_dec(id) without a language must return the EN document exactly as before this feature
        (ACC-005 second half: the default is unaffected)."""
        result = get_dec(self.doc_id)
        self.assertIsInstance(result, DecDocument)
        assert isinstance(result, DecDocument)
        self.assertEqual(result.body.text, "Choose a Document Store")
        self.assertEqual(result.frontmatter.id, self.doc_id)

    def test_explicit_en_is_the_en_document(self):
        """An explicit language='en' must behave identically to the omitted default."""
        result = get_dec(self.doc_id, language="en")
        self.assertIsInstance(result, DecDocument)
        assert isinstance(result, DecDocument)
        self.assertEqual(result.body.text, "Choose a Document Store")

    def test_de_returns_the_german_variant(self):
        """get_dec(id, language='de') must return the German variant's content (ACC-005)."""
        result = get_dec(self.doc_id, language="de")
        self.assertIsInstance(result, DecDocument)
        assert isinstance(result, DecDocument)
        self.assertEqual(result.frontmatter.id, self.doc_id)
        self.assertEqual(result.body.text, "Dokumentlager w\u00e4hlen")
        self.assertIn("Der aktuelle Store", result.body.context.text)

    def test_de_structured_model_holds_canonical_heading_keys(self):
        """A DE file's German fixed-text headings must resolve via the table to the same canonical
        schema keys the EN parser uses (ACC-004): the structured fields are the EN ones
        (context/outcome/roles_and_responsibilities/source), the prose stays translated."""
        result = get_dec(self.doc_id, language="de")
        assert isinstance(result, DecDocument)
        self.assertEqual(result.body.context.text.splitlines()[0], "## Context and Problem Statement")
        self.assertEqual(result.body.outcome.statement.text, "Wir haben das Dokumentlager gew\u00e4hlt.")
        self.assertEqual(
            result.body.roles_and_responsibilities.accountable.value.text, "Die f\u00fchrende Plattformarchitektin."
        )
        self.assertEqual(result.body.source.value.text, "Die Incident-Review-Meeting zum Dashboard-Latenz-Vorfall.")

    def test_closed_vocabulary_tokens_stay_canonical_in_the_file(self):
        """The DE variant's schema-constant tokens are never translated: ``### Option {N}:`` headings
        keep their canonical prefix and number (the German option names are free data), and the
        timestamp-led update entry heading keeps its canonical timestamp form (ACC-012 unit pin)."""
        on_disk = self.de_file.read_text(encoding="utf-8")
        self.assertIn("### Option 1: Kanban", on_disk)
        self.assertIn("### Option 2: Datenbank", on_disk)
        self.assertIn("### 2026-08-27T14:30:00.000+02:00 - Best\u00e4tigt", on_disk)

        result = get_dec(self.doc_id, language="de")
        assert isinstance(result, DecDocument)
        assert result.body.pros_and_cons is not None
        self.assertEqual([option.number for option in result.body.pros_and_cons.options], [1, 2])
        self.assertEqual([option.name for option in result.body.pros_and_cons.options], ["Kanban", "Datenbank"])
        assert result.body.updates is not None
        self.assertEqual(result.body.updates.updates[0].timestamp, "2026-08-27T14:30:00.000+02:00")
        self.assertEqual(result.body.updates.updates[0].title, "Best\u00e4tigt")

    def test_de_raw_is_the_variant_body_verbatim(self):
        """raw=True must return the DE variant's on-disk body byte-for-byte (the translation
        preserved -- the raw read never applies the table)."""
        result = get_dec(self.doc_id, language="de", raw=True)
        self.assertIsInstance(result, str)
        self.assertEqual(result, body_text(self.de_file))
        self.assertIn("## Kontext und Problembeschreibung", result)

    def test_fenced_code_block_headings_are_not_rewritten(self):
        """A ``#``-leading line inside a fenced code block (even one spelling a translated
        heading) is code, not a heading: the pre-pass leaves it byte-identical in the parsed
        section body, while the real (unfenced) heading is rewritten to its canonical text."""
        result = get_dec(self.doc_id, language="de")
        assert isinstance(result, DecDocument)
        context = result.body.context.text
        self.assertEqual(context.splitlines()[0], "## Context and Problem Statement")
        self.assertIn("# Kontext und Problembeschreibung", context)
        self.assertIn("```python", context)

        raw = get_dec(self.doc_id, language="de", raw=True)
        self.assertIn("# Kontext und Problembeschreibung", raw)

    def test_de_raw_window_and_numbered_work_on_the_variant(self):
        """The read-style offset/limit/numbered windowing must address the DE variant's own raw body."""
        lines = get_dec(self.doc_id, language="de", raw=True).splitlines()
        k = lines.index("## Kontext und Problembeschreibung") + 1
        windowed = get_dec(self.doc_id, language="de", raw=True, offset=k, limit=1)
        self.assertEqual(windowed, f"{lines[k - 1]}\n")
        numbered = get_dec(self.doc_id, language="de", raw=True, offset=k, limit=1, numbered=True)
        self.assertEqual(numbered, f"{k}: {lines[k - 1]}\n")

    def test_bad_language_is_rejected_before_any_filesystem_access(self):
        """A path-injection-shaped language must be rejected by the guard before any document
        lookup runs (ACC-013) -- the load_by_id call (the first filesystem access) is never
        reached."""
        with mock.patch("biz.dfch.specmgr.dec.tools.get_dec.load_by_id", side_effect=AssertionError("must not run")):
            for value in ("", "d", "de3", "DE", "de x", "../../etc", "de/x", "/abs"):
                with self.subTest(value=value):
                    with self.assertRaises(ValueError) as ctx:
                        get_dec(self.doc_id, language=value)
                    self.assertIn(repr(value), str(ctx.exception))

    def test_bad_language_wins_over_an_absent_id(self):
        """The language guard runs before the id lookup: an absent id with a bad language still
        reports the language error, not the not-found error."""
        with self.assertRaises(ValueError) as ctx:
            get_dec(_MISSING_UUID, language="../../etc")
        self.assertIn("'../../etc'", str(ctx.exception))

    def test_unusable_language_is_rejected_before_any_filesystem_access(self):
        """A shape-valid language without a packaged heading table (e.g. 'fr') is rejected up front
        with the table loader's actionable error, before any filesystem access."""
        with mock.patch("biz.dfch.specmgr.dec.tools.get_dec.load_by_id", side_effect=AssertionError("must not run")):
            with self.assertRaises(ValueError) as ctx:
                get_dec(self.doc_id, language="fr")
        message = str(ctx.exception)
        self.assertIn("'fr'", message)
        self.assertIn("no heading-mapping table", message)

    def test_absent_id_in_de_raises_not_found(self):
        """A truly-absent id in a (usable) language still raises the domain's not-found error."""
        with self.assertRaises(DecNotFoundError):
            get_dec(_MISSING_UUID, language="de")

    def test_absent_id_in_de_with_missing_variant_directory_raises_not_found(self):
        """An absent id when the language subdirectory does not exist at all raises not-found (an
        empty listing is not an error)."""
        import shutil

        shutil.rmtree(self.docs_root / "dec" / "de")
        reset_dec_cache()
        with self.assertRaises(DecNotFoundError):
            get_dec(self.doc_id, language="de")

    def test_broken_de_variant_returns_parse_failure_result_byte_identical_to_list_row(self):
        """get_dec(id, language='de') on a broken DE variant must return the non-raising
        ParseFailureResult whose error text is byte-identical to list_dec(language='de')'s failed
        row for the same file (the feat-150/162 byte-identity contract, ADR 9080b37c, extended to
        language variants)."""
        broken = self.de_file.read_text(encoding="utf-8").replace("## Entscheidungsergebnis", "## BROKEN-HEADING")
        self.de_file.write_text(broken, encoding="utf-8")
        reset_dec_cache()

        failure = get_dec(self.doc_id, language="de")
        row = list_dec(language="de").results[0]

        self.assertIsInstance(failure, ParseFailureResult)
        assert isinstance(failure, ParseFailureResult)
        self.assertEqual(failure.error, row.error)
        self.assertEqual(failure.path, row.path)
        self.assertEqual(failure.id, self.doc_id)
        self.assertEqual(row.title, "<failed to parse>")

    def test_broken_en_variant_is_unaffected_by_de(self):
        """A broken EN file still returns the EN ParseFailureResult (the DE variant's presence
        changes nothing about the default language's own failure channel)."""
        broken = self.en_file.read_text(encoding="utf-8").replace("## Decision Outcome", "## BROKEN-HEADING")
        self.en_file.write_text(broken, encoding="utf-8")
        reset_dec_cache()

        failure = get_dec(self.doc_id)
        row = list_dec().results[0]

        self.assertIsInstance(failure, ParseFailureResult)
        assert isinstance(failure, ParseFailureResult)
        self.assertEqual(failure.error, row.error)
        self.assertEqual(failure.path, row.path)


class TestListDecLanguage(unittest.TestCase):
    """Tests for list_dec's optional language parameter (ACC-007 read half, ADR 38efdb66 item 7)."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        reset_dec_cache()
        self.doc_id, self.en_file, self.de_file = _seed_en_and_de(self.docs_root)

    def test_omitted_lists_only_the_flat_en_files(self):
        """list_dec() must list exactly the EN (flat) documents -- a DE variant of the same id
        never appears in the default listing (ACC-007 second half; the flat scan is non-recursive,
        ACC-014)."""
        result = list_dec()
        self.assertEqual(result.total, 1)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].id, self.doc_id)
        self.assertEqual(result.results[0].title, "Choose a Document Store")
        self.assertEqual(result.results[0].path, str(self.en_file.resolve()))

    def test_explicit_en_matches_the_omitted_listing(self):
        """list_dec(language='en') must be the exact same listing as the omitted default."""
        self.assertEqual(list_dec().results, list_dec(language="en").results)

    def test_de_lists_only_the_german_variants(self):
        """list_dec(language='de') must list only the existing DE variants -- the EN document does
        not appear (ACC-007 first half)."""
        result = list_dec(language="de")
        self.assertEqual(result.total, 1)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].id, self.doc_id)
        self.assertEqual(result.results[0].title, "Dokumentlager w\u00e4hlen")
        self.assertEqual(result.results[0].path, str(self.de_file.resolve()))

    def test_row_shape_is_unchanged_no_language_column(self):
        """The PagedResult row shape is unchanged: a DE listing row carries exactly the same fields
        as an EN row (no language column, ADR item 7)."""
        en_row = list_dec().results[0].model_dump()
        de_row = list_dec(language="de").results[0].model_dump()
        self.assertEqual(set(en_row), set(de_row))
        self.assertNotIn("language", en_row)

    def test_missing_language_directory_lists_empty(self):
        """A language with no subdirectory at all lists empty (not an error)."""
        result = list_dec(language="de")
        de_dir = self.docs_root / "dec" / "de"
        import shutil

        shutil.rmtree(de_dir)
        reset_dec_cache()
        empty = list_dec(language="de")
        self.assertEqual(empty.total, 0)
        self.assertEqual(empty.results, [])
        self.assertEqual(result.total, 1)

    def test_bad_language_is_rejected_before_any_scan(self):
        """A shape-invalid language must raise the guard's ValueError before the directory scan."""
        for value in ("../../etc", "DE", "de/x"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError) as ctx:
                    list_dec(language=value)
                self.assertIn(repr(value), str(ctx.exception))

    def test_unusable_language_is_rejected_with_the_table_error(self):
        """A shape-valid language without a table is rejected up front (listing a document set
        that could never be parsed is not a meaningful outcome)."""
        with self.assertRaises(ValueError) as ctx:
            list_dec(language="fr")
        self.assertIn("no heading-mapping table", str(ctx.exception))

    def test_reconcile_covers_the_domain_wide_union(self):
        """list_dec reconciles the cache against the domain-wide live listing (flat EN files plus
        every {language} subdirectory's files), never just the scanned directory -- with a DE
        variant present, reconciling a DE scan still carries the EN file, so the EN cache entries
        survive (ADR 38efdb66 item 9, behaviorally pinned at the call-argument level)."""
        import importlib

        list_module = importlib.import_module("biz.dfch.specmgr.dec.tools.list_dec")
        real_reconcile = list_module.reconcile_dec_cache
        with mock.patch.object(list_module, "reconcile_dec_cache", wraps=real_reconcile) as spy:
            list_dec(language="de")
            args, _ = spy.call_args
            self.assertEqual(sorted(args[0]), sorted([self.en_file.resolve(), self.de_file.resolve()]))
            spy.reset_mock()
            list_dec()
            args, _ = spy.call_args
            self.assertEqual(sorted(args[0]), sorted([self.en_file.resolve(), self.de_file.resolve()]))

    def test_de_failed_row_error_is_byte_identical_to_get(self):
        """A broken DE variant appears as list_dec(language='de')'s failed row, with the same error
        text get_dec(id, language='de')'s ParseFailureResult carries (cross-tool byte-identity)."""
        broken = self.de_file.read_text(encoding="utf-8").replace("## Quelle", "## BROKEN-HEADING")
        self.de_file.write_text(broken, encoding="utf-8")
        reset_dec_cache()

        row = list_dec(language="de").results[0]
        failure = get_dec(self.doc_id, language="de")

        self.assertIsNotNone(row.error)
        assert isinstance(failure, ParseFailureResult)
        self.assertEqual(failure.error, row.error)
        self.assertEqual(list_dec().error_count, 0)


class TestParseDecLanguage(unittest.TestCase):
    """Tests for the parse_dec tool's path-derived language (ADR 38efdb66 item 5)."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        reset_dec_cache()
        self.doc_id, self.en_file, self.de_file = _seed_en_and_de(self.docs_root)

    def test_a_path_under_the_language_subdirectory_applies_the_table(self):
        """parse_dec on a file under docs/dec/de/ must apply the de table: German fixed-text
        headings resolve to the canonical schema keys."""
        result = parse_dec(str(self.de_file))
        self.assertIsInstance(result, DecDocument)
        assert isinstance(result, DecDocument)
        self.assertEqual(result.body.text, "Dokumentlager w\u00e4hlen")
        self.assertIn("Der aktuelle Store", result.body.context.text)

    def test_a_flat_path_applies_no_table(self):
        """parse_dec on a file in the flat directory must NOT apply a table: a DE heading there is
        an ordinary alias-mismatch parse error (the table is position-derived, not content-derived)."""
        flat_de = self.docs_root / "dec" / "flat-de.md"
        frontmatter = self.en_file.read_text(encoding="utf-8").split("---\n")[1]
        flat_de.write_text(f"---\n{frontmatter}---\n{_DE_BODY}", encoding="utf-8")

        result = parse_dec(str(flat_de))

        self.assertNotIsInstance(result, DecDocument)
        assert not isinstance(result, DecDocument)
        self.assertFalse(result.valid)
        assert not result.valid
        self.assertTrue(any("alias" in entry.message or "expected" in entry.message for entry in result.errors))

    def test_a_path_outside_the_base_applies_no_table(self):
        """parse_dec on a file outside the decision base directory parses canonical (no table)."""
        outside = Path(self.enterContext(tempfile.TemporaryDirectory())) / "outside.md"
        frontmatter = self.en_file.read_text(encoding="utf-8").split("---\n")[1]
        outside.write_text(f"---\n{frontmatter}---\n{_DE_BODY}", encoding="utf-8")

        result = parse_dec(str(outside))

        self.assertNotIsInstance(result, DecDocument)
        assert not isinstance(result, DecDocument)
        self.assertFalse(result.valid)

    def test_a_flat_en_path_parses_as_before(self):
        """parse_dec on the flat EN file must parse exactly as before this feature."""
        result = parse_dec(str(self.en_file))
        self.assertIsInstance(result, DecDocument)
        assert isinstance(result, DecDocument)
        self.assertEqual(result.body.text, "Choose a Document Store")

    def test_a_path_under_a_tableless_language_directory_raises_the_loader_error(self):
        """A file under a shape-valid {language} directory without a packaged table (docs/dec/fr/)
        fails with the table loader's actionable ValueError at parse time (the language is
        shape-valid but unusable, ADR 38efdb66 item 3/6)."""
        fr_dir = self.docs_root / "dec" / "fr"
        fr_dir.mkdir(parents=True)
        frontmatter = self.en_file.read_text(encoding="utf-8").split("---\n")[1]
        fr_file = fr_dir / self.en_file.name
        fr_file.write_text(f"---\n{frontmatter}---\n{_DE_BODY}", encoding="utf-8")

        with self.assertRaises(ValueError) as ctx:
            parse_dec(str(fr_file))
        message = str(ctx.exception)
        self.assertIn("'fr'", message)
        self.assertIn("no heading-mapping table", message)


class TestDecPathsLanguage(unittest.TestCase):
    """Tests for the dec path helpers' language support (ACC-014 unit pin, path resolution)."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        reset_dec_cache()
        self.doc_id, self.en_file, self.de_file = _seed_en_and_de(self.docs_root)

    def test_iter_dec_paths_is_flat_only_by_default(self):
        """iter_dec_paths() (omitted language) yields only the flat EN files -- it never descends
        into the {language} subfolder (ACC-014 unit pin at the domain level)."""
        paths = list(iter_dec_paths())
        self.assertEqual(paths, [self.en_file])

    def test_iter_dec_paths_language_yields_only_that_language(self):
        """iter_dec_paths('de') yields only the DE variant's directory."""
        paths = list(iter_dec_paths("de"))
        self.assertEqual(paths, [self.de_file])

    def test_dec_base_dir_language(self):
        """dec_base_dir() is the flat directory (as before); dec_base_dir('de') is the subfolder;
        dec_base_dir('en') is the flat directory."""
        self.assertEqual(dec_base_dir(), self.docs_root / "dec")
        self.assertEqual(dec_base_dir("en"), self.docs_root / "dec")
        self.assertEqual(dec_base_dir("de"), self.docs_root / "dec" / "de")

    def test_find_dec_path_in_the_language_subdirectory(self):
        """find_dec_path must resolve the id against the language subdirectory exactly as it does
        against the flat one (the id scan is language-agnostic once the base_dir is chosen)."""
        self.assertEqual(find_dec_path(dec_base_dir("de"), self.doc_id), self.de_file)
        self.assertEqual(find_dec_path(dec_base_dir(), self.doc_id), self.en_file)

    def test_find_dec_path_does_not_cross_languages(self):
        """An id absent from the scanned base_dir raises DecNotFoundError for both the flat scan and
        the language-subdirectory scan (the id scan is confined to the given base_dir)."""
        with self.assertRaises(DecNotFoundError):
            find_dec_path(dec_base_dir(), "11111111-1111-1111-1111-111111111111")
        with self.assertRaises(DecNotFoundError):
            find_dec_path(dec_base_dir("de"), "11111111-1111-1111-1111-111111111111")

    def test_bad_language_in_iter_dec_paths_raises_the_guard_error(self):
        """iter_dec_paths with a shape-invalid language raises the guard's ValueError (via
        dec_base_dir's own guard)."""
        for value in ("../../etc", "DE"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    list(iter_dec_paths(value))


class TestDecCacheLanguage(unittest.TestCase):
    """Tests for the cache's cross-language behavior (ADR 38efdb66 item 9: no cache code change,
    path-keyed entries keep languages independent)."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        reset_dec_cache()
        self.doc_id, self.en_file, self.de_file = _seed_en_and_de(self.docs_root)

    def test_en_and_de_of_one_id_are_independent_cache_entries(self):
        """Reading the EN document, then the DE variant, then EN again must never cross-contaminate:
        the two languages of one id live at distinct paths and get distinct, correct results
        (DocCache is path-keyed -- ADR item 9's confirmed design fact, pinned behaviorally)."""
        en_first = get_dec(self.doc_id)
        de = get_dec(self.doc_id, language="de")
        en_second = get_dec(self.doc_id)
        assert isinstance(en_first, DecDocument)
        assert isinstance(de, DecDocument)
        assert isinstance(en_second, DecDocument)
        self.assertEqual(en_first.body.text, "Choose a Document Store")
        self.assertEqual(de.body.text, "Dokumentlager w\u00e4hlen")
        self.assertEqual(en_second.body.text, "Choose a Document Store")

    def test_listing_one_language_does_not_evict_the_others(self):
        """A list of one language reconciles against the domain-wide live listing (never just the
        scanned directory): after list_dec(language='de'), a previously-read EN document is still
        served correctly (and vice versa)."""
        en = get_dec(self.doc_id)
        list_dec(language="de")
        en_again = get_dec(self.doc_id)
        de = get_dec(self.doc_id, language="de")
        list_dec()
        de_again = get_dec(self.doc_id, language="de")
        assert isinstance(en, DecDocument)
        assert isinstance(en_again, DecDocument)
        assert isinstance(de, DecDocument)
        assert isinstance(de_again, DecDocument)
        self.assertEqual(en.body.text, en_again.body.text)
        self.assertEqual(de.body.text, de_again.body.text)


#: German H1 titles that equal a key of the packaged de heading table (``Quelle`` -> ``Source``,
#: ``Weitere Informationen`` -> ``More Information``): review finding E1.
_TITLES_EQUAL_TO_TABLE_KEYS = ("Quelle", "Weitere Informationen")


class TestTitleEqualToTableKeyIsNeverMapped(unittest.TestCase):
    """Regression for review finding E1: the free-form H1 title is never looked up in the heading table.

    A German title that happens to equal a table key must reach the parsed model as written, on the
    pure parse path (``parse_dec_body``) and through the tools (``get_dec``/``list_dec``).
    """

    def test_parse_dec_body_keeps_the_title_as_written(self):
        for title in _TITLES_EQUAL_TO_TABLE_KEYS:
            with self.subTest(title=title):
                body = _DE_BODY.replace("# Dokumentlager w\u00e4hlen", f"# {title}", 1)
                self.assertTrue(body.startswith(f"# {title}\n"))
                result = parse_dec_body(body, language="de")
                self.assertEqual(result.text, title)
                # the section headings are still normalized to canonical keys
                self.assertEqual(result.context.text.splitlines()[0], "## Context and Problem Statement")

    def test_get_and_list_keep_the_title_as_written(self):
        for title in _TITLES_EQUAL_TO_TABLE_KEYS:
            with self.subTest(title=title):
                with tempfile.TemporaryDirectory() as tmp:
                    docs_root = Path(tmp)
                    with mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(docs_root)}):
                        reset_dec_cache()
                        doc_id, _en_file, de_file = _seed_en_and_de(docs_root)
                        de_text = de_file.read_text(encoding="utf-8")
                        de_file.write_text(
                            de_text.replace("# Dokumentlager w\u00e4hlen", f"# {title}", 1), encoding="utf-8"
                        )
                        reset_dec_cache()

                        document = get_dec(doc_id, language="de")
                        row = list_dec(language="de").results[0]

                        assert isinstance(document, DecDocument)
                        self.assertEqual(document.body.text, title)
                        self.assertEqual(row.title, title)
                        reset_dec_cache()


if __name__ == "__main__":
    unittest.main()
