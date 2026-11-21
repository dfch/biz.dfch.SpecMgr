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

"""Tests for the uniform sharded per-language layout core (feat-245 Phase 100).

Covers the ``general.tools._doc_paths`` primitives reworked by Phase 100 --
``SHARD_DIGITS``/:func:`shard_token`/:func:`sharded_doc_path`, the shard-only
:func:`iter_doc_paths` listing (``<base>/*/*.md``, sorted by relative path),
the shard-narrowed :func:`find_doc_path_by_id`/:func:`find_parse_failure`
with the full per-language listing fallback, the re-rooted
:func:`doc_base_dir`/:func:`ensure_doc_base_dir`/:func:`doc_domain_base_dir`
(every language -- ``en`` included, no flat special case; ``None`` => the
``en/`` directory), the first-subdirectory :func:`language_for_doc_path`,
and the sharded :func:`iter_doc_paths_all_languages` union -- plus the two
per-domain pins over all thirteen sharded domains (``SPECS``, imported from
the feat-197-i18n suite): the EN-only consumers re-rooted at the ``en/``
directory see EN files only, never variant files (ACC-008), and every
``parse_<d>`` tool derives the language from the path's first subdirectory
under the domain base (``en`` => canonical, ``de`` => the ``de`` table;
ACC-009).
"""

from __future__ import annotations

import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import ValidateResult
from biz.dfch.specmgr.general.tools._doc_paths import (
    DOCS_DIR_ENV_VAR,
    SHARD_DIGITS,
    DocNotFoundError,
    doc_base_dir,
    doc_domain_base_dir,
    ensure_doc_base_dir,
    find_doc_path_by_id,
    find_parse_failure,
    iter_doc_paths,
    iter_doc_paths_all_languages,
    language_for_doc_path,
    sharded_doc_path,
    shard_token,
)
from tests.general.tools.test_i18n_all_domains import SPECS, DomainSpec, translate_to_de

#: A fixed canonical id whose first two characters ("de") double as a valid
#: two-letter language code -- the shard/language collision case.
_TARGET_ID = "deadbeef-0000-0000-0000-000000000000"


class _FakeDoc:
    """Minimal stand-in for a parsed document, holding just an id."""

    def __init__(self, id_: str | None) -> None:
        self.id = id_


def _read_fake(path: Path) -> _FakeDoc:
    """Read and parse ``path``'s fixture text into a ``_FakeDoc`` (the ``read_fn`` shape, Path in).

    ``"BROKEN"`` simulates a parse failure (a ``ValueError``); empty content
    yields an id-less document (``id=None``).
    """
    stripped = path.read_text(encoding="utf-8").strip()
    if stripped == "BROKEN":
        raise ValueError("simulated parse failure")
    return _FakeDoc(id_=stripped or None)


def _get_id(doc: _FakeDoc) -> str | None:
    return doc.id


def _read_broken(path: Path) -> _FakeDoc:
    """``read_fn`` that fails to parse a file whose content is ``"BROKEN"`` (a structural ``AssertionError``)."""
    stripped = path.read_text(encoding="utf-8").strip()
    if stripped == "BROKEN":
        raise AssertionError("simulated structural parse failure")
    return _FakeDoc(id_=stripped or None)


class TestShardTokenAndShardedDocPath(unittest.TestCase):
    """Tests for ``shard_token``/``sharded_doc_path`` (the layout's write-side core, Task 100.100)."""

    def test_shard_digits_is_two(self):
        self.assertEqual(SHARD_DIGITS, 2)

    def test_shard_token_is_the_first_two_id_characters(self):
        self.assertEqual(shard_token("deadbeef-0000-0000-0000-000000000000"), "de")
        self.assertEqual(shard_token("01020304-1111-1111-1111-111111111111"), "01")
        self.assertEqual(shard_token("ffffffff-2222-2222-2222-222222222222"), "ff")

    def test_sharded_doc_path_is_prefix_less_under_the_shard(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            result = sharded_doc_path(base, _TARGET_ID, "my-doc")
            self.assertEqual(result, base / "de" / f"{_TARGET_ID}-my-doc.md")
            self.assertTrue(result.name.startswith(_TARGET_ID))  # no ``<type>-`` prefix

    def test_sharded_doc_path_creates_the_shard_directory_but_not_the_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "req" / "en"  # the language dir is missing on purpose
            result = sharded_doc_path(base, _TARGET_ID, "my-doc")
            self.assertTrue(result.parent.is_dir())
            self.assertFalse(result.exists())


class TestIterDocPathsSharded(unittest.TestCase):
    """Tests for ``iter_doc_paths``' sharded listing (Task 100.110)."""

    def test_missing_directory_yields_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(list(iter_doc_paths(Path(tmp) / "missing")), [])

    def test_empty_directory_yields_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(list(iter_doc_paths(Path(tmp))), [])

    def test_yields_files_exactly_one_subdirectory_level_below_sorted_by_relative_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "zz").mkdir()
            (base / "ab").mkdir()
            (base / "ab" / "b.md").write_text("b", encoding="utf-8")
            (base / "ab" / "a.md").write_text("a", encoding="utf-8")
            (base / "zz" / "z.md").write_text("z", encoding="utf-8")
            (base / "zz" / "not-markdown.txt").write_text("x", encoding="utf-8")
            rel = [str(p.relative_to(base)) for p in iter_doc_paths(base)]
            self.assertEqual(rel, ["ab/a.md", "ab/b.md", "zz/z.md"])

    def test_listing_order_equals_lexicographic_file_name_order_for_uuid_prefixed_names(self):
        """ACC-002 order identity: the shard is the two-hex uuid prefix and the file name starts with
        the uuid, so (shard dir, file name) order equals the lexicographic file-name order."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            ids = [
                "ab001122-0000-0000-0000-000000000000",
                "00112233-0000-0000-0000-000000000000",
                "ffeedd00-0000-0000-0000-000000000000",
                "ab001133-0000-0000-0000-000000000000",
            ]
            for index, ident in enumerate(ids):
                path = base / ident[:2] / f"{ident}-doc-{index}.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(ident, encoding="utf-8")
            names = [p.name for p in iter_doc_paths(base)]
            self.assertEqual(names, sorted(names))
            self.assertEqual(
                names,
                [
                    "00112233-0000-0000-0000-000000000000-doc-1.md",
                    "ab001122-0000-0000-0000-000000000000-doc-0.md",
                    "ab001133-0000-0000-0000-000000000000-doc-3.md",
                    "ffeedd00-0000-0000-0000-000000000000-doc-2.md",
                ],
            )

    def test_flat_files_are_not_yielded(self):
        """ACC-003: a file directly under the language dir (missing shard dir) is invisible."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "flat.md").write_text("x", encoding="utf-8")
            (base / "shard").mkdir()
            (base / "shard" / "ok.md").write_text("x", encoding="utf-8")
            self.assertEqual([p.name for p in iter_doc_paths(base)], ["ok.md"])

    def test_deeper_nesting_is_not_yielded(self):
        """ACC-003: a file deeper than one shard level is invisible."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "a" / "b").mkdir(parents=True)
            (base / "a" / "b" / "deep.md").write_text("x", encoding="utf-8")
            (base / "a" / "ok.md").write_text("x", encoding="utf-8")
            self.assertEqual([p.name for p in iter_doc_paths(base)], ["ok.md"])

    def test_the_shard_level_is_shape_agnostic_on_the_read_path(self):
        """A non-hex shard dir is still yielded on read (the lint gate, Phase 120, flags it); only the
        depth is structural."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "zz").mkdir()
            (base / "zz" / "x.md").write_text("x", encoding="utf-8")
            self.assertEqual([p.name for p in iter_doc_paths(base)], ["x.md"])


class TestFindDocPathByIdSharded(unittest.TestCase):
    """Tests for ``find_doc_path_by_id``'s shard-narrowed scan (Task 100.120)."""

    def test_finds_a_correctly_placed_document_via_the_fast_path_and_reads_only_its_shard(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = base / "de" / f"{_TARGET_ID}-target.md"
            target.parent.mkdir(parents=True)
            target.write_text(_TARGET_ID, encoding="utf-8")
            decoy = base / "ab" / "ab000000-0000-0000-0000-000000000000-decoy.md"
            decoy.parent.mkdir(parents=True)
            decoy.write_text("ab000000-0000-0000-0000-000000000000", encoding="utf-8")
            reads: list[Path] = []

            def _counting_read(path: Path) -> _FakeDoc:
                reads.append(path)
                return _read_fake(path)

            result = find_doc_path_by_id(base, _TARGET_ID, _counting_read, _get_id)

            self.assertEqual(result, target)
            self.assertEqual(reads, [target])  # the cold cost is one shard's files, not the whole domain

    def test_finds_a_wrong_shard_document_via_the_full_fallback_in_an_en_base(self):
        """ACC-004 (EN): a document whose placement disagrees with its id still resolves, byte-identical."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "en"
            path = base / "00" / f"{_TARGET_ID}-misplaced.md"
            path.parent.mkdir(parents=True)
            content = _TARGET_ID
            path.write_text(content, encoding="utf-8")

            result = find_doc_path_by_id(base, _TARGET_ID, _read_fake, _get_id)

            self.assertEqual(result, path)
            self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_finds_a_wrong_shard_document_via_the_full_fallback_in_a_variant_base(self):
        """ACC-004 (variant): the same fallback runs inside a variant language's own directory."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "de"
            path = base / "ab" / f"{_TARGET_ID}-misplaced.md"
            path.parent.mkdir(parents=True)
            content = _TARGET_ID
            path.write_text(content, encoding="utf-8")

            result = find_doc_path_by_id(base, _TARGET_ID, _read_fake, _get_id)

            self.assertEqual(result, path)
            self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_reconcile_fn_still_gets_the_full_sharded_listing(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paths = []
            for ident in (_TARGET_ID, "ab000000-0000-0000-0000-000000000000"):
                path = base / ident[:2] / f"{ident}-x.md"
                path.parent.mkdir(parents=True)
                path.write_text(ident, encoding="utf-8")
                paths.append(path)
            calls: list[list[Path]] = []

            def _reconcile(live_paths) -> None:
                calls.append(sorted(live_paths))

            find_doc_path_by_id(base, _TARGET_ID, _read_fake, _get_id, reconcile_fn=_reconcile)

            self.assertEqual(calls, [sorted(paths)])  # the reconcile semantics: the full listing, once

    def test_skips_a_broken_file_in_the_fast_shard_and_finds_the_valid_one_elsewhere(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "de").mkdir(parents=True)
            (base / "de" / f"{_TARGET_ID}-broken.md").write_text("BROKEN", encoding="utf-8")
            good = base / "00" / f"{_TARGET_ID}-good.md"
            good.parent.mkdir(parents=True)
            good.write_text(_TARGET_ID, encoding="utf-8")

            self.assertEqual(find_doc_path_by_id(base, _TARGET_ID, _read_fake, _get_id), good)

    def test_raises_not_found_for_unknown_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "de").mkdir(parents=True)
            (base / "de" / f"{_TARGET_ID}-x.md").write_text(_TARGET_ID, encoding="utf-8")

            with self.assertRaises(DocNotFoundError) as ctx:
                find_doc_path_by_id(base, "ffffffff-9999-9999-9999-999999999999", _read_fake, _get_id)
            self.assertIn("no document found with id 'ffffffff-9999-9999-9999-999999999999'", str(ctx.exception))

    def test_id_less_document_in_a_shard_is_list_visible_and_does_not_block_lookup(self):
        """ACC-002/ACC-003: an id-less doc placed inside a shard dir (any shard, e.g. ``00/``) stays
        list-visible with its author-chosen stem; the flat placement is invisible; and its presence
        never blocks lookup of a different id."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            id_less = base / "00" / "my-notes.md"
            id_less.parent.mkdir(parents=True)
            id_less.write_text("", encoding="utf-8")  # empty content => _read_fake yields id None
            good = base / "de" / f"{_TARGET_ID}-x.md"
            good.parent.mkdir(parents=True)
            good.write_text(_TARGET_ID, encoding="utf-8")
            (base / "flat-notes.md").write_text("", encoding="utf-8")

            listed = [p.name for p in iter_doc_paths(base)]

            self.assertIn("my-notes.md", listed)
            self.assertNotIn("flat-notes.md", listed)
            self.assertEqual(find_doc_path_by_id(base, _TARGET_ID, _read_fake, _get_id), good)


class TestFindParseFailureSharded(unittest.TestCase):
    """Tests for ``find_parse_failure``'s shard-narrowed scan (Task 100.130)."""

    def test_broken_file_in_the_right_shard_returns_path_and_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "de" / f"{_TARGET_ID}-broken.md"
            path.parent.mkdir(parents=True)
            path.write_text("BROKEN", encoding="utf-8")

            result = find_parse_failure(base, _TARGET_ID, _read_broken)

            self.assertEqual(result, (path, "simulated structural parse failure"))

    def test_broken_file_in_a_wrong_shard_is_found_by_the_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "00" / f"{_TARGET_ID}-broken.md"
            path.parent.mkdir(parents=True)
            path.write_text("BROKEN", encoding="utf-8")

            result = find_parse_failure(base, _TARGET_ID, _read_broken)

            self.assertEqual(result, (path, "simulated structural parse failure"))

    def test_a_correctly_placed_name_match_wins_over_a_misplaced_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            right = base / "de" / f"{_TARGET_ID}-broken.md"
            right.parent.mkdir(parents=True)
            right.write_text("BROKEN", encoding="utf-8")
            misplaced = base / "00" / f"{_TARGET_ID}-other.md"
            misplaced.parent.mkdir(parents=True)
            misplaced.write_text("some-other-id", encoding="utf-8")

            result = find_parse_failure(base, _TARGET_ID, _read_broken)

            self.assertEqual(result, (right, "simulated structural parse failure"))

    def test_no_name_match_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "11").mkdir(parents=True)
            (base / "11" / "11111111-1111-1111-1111-111111111111-x.md").write_text(
                "11111111-1111-1111-1111-111111111111", encoding="utf-8"
            )

            result = find_parse_failure(base, _TARGET_ID, _read_broken)

            self.assertIsNone(result)

    def test_two_wrong_shard_name_matches_are_ambiguous_and_return_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "00").mkdir(parents=True)
            (base / "00" / f"{_TARGET_ID}-a.md").write_text("BROKEN", encoding="utf-8")
            (base / "00" / f"{_TARGET_ID}-b.md").write_text("BROKEN", encoding="utf-8")

            result = find_parse_failure(base, _TARGET_ID, _read_broken)

            self.assertIsNone(result)

    def test_name_match_that_parses_cleanly_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "de").mkdir(parents=True)
            (base / "de" / f"{_TARGET_ID}-healthy.md").write_text("some-other-id", encoding="utf-8")

            result = find_parse_failure(base, _TARGET_ID, _read_broken)

            self.assertIsNone(result)


class TestDocBaseDirSharded(unittest.TestCase):
    """Tests for ``doc_base_dir``/``ensure_doc_base_dir``/``doc_domain_base_dir`` re-rooting (Task 100.160)."""

    def test_omitted_language_is_the_en_directory(self):
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/custom-docs"}):
            self.assertEqual(doc_base_dir("req"), Path("/tmp/custom-docs/req/en"))

    def test_none_language_is_the_en_directory(self):
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/custom-docs"}):
            self.assertEqual(doc_base_dir("req", None), Path("/tmp/custom-docs/req/en"))

    def test_explicit_en_is_the_en_directory(self):
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/custom-docs"}):
            self.assertEqual(doc_base_dir("req", "en"), Path("/tmp/custom-docs/req/en"))

    def test_every_language_including_en_is_a_subdirectory_of_the_domain_base(self):
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/custom-docs"}):
            for language in ("en", "de", "fr"):
                with self.subTest(language=language):
                    self.assertEqual(doc_base_dir("req", language), doc_domain_base_dir("req") / language)

    def test_domain_base_dir_is_the_parent_of_every_language_directory(self):
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/custom-docs"}):
            self.assertEqual(doc_domain_base_dir("req"), Path("/tmp/custom-docs/req"))

    def test_other_language_is_its_own_directory(self):
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/custom-docs"}):
            self.assertEqual(doc_base_dir("dec", "de"), Path("/tmp/custom-docs/dec/de"))

    def test_invalid_language_is_rejected_before_path_construction(self):
        for value in ("", "d", "de3", "DE", "de x", "../../etc", "de/x", "/abs"):
            with self.subTest(value=value):
                with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/custom-docs"}):
                    with self.assertRaises(ValueError) as ctx:
                        doc_base_dir("dec", value)
                    self.assertIn(repr(value), str(ctx.exception))

    def test_doc_base_dir_does_not_create_the_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                doc_base_dir("req")
            self.assertFalse(missing_root.exists())

    def test_ensure_creates_the_en_directory_when_omitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: tmp}):
                result = ensure_doc_base_dir("req")
            self.assertTrue(result.exists())
            self.assertEqual(result, Path(tmp) / "req" / "en")

    def test_ensure_creates_the_variant_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                result = ensure_doc_base_dir("dec", "de")
            self.assertTrue(result.exists())
            self.assertEqual(result, missing_root / "dec" / "de")


class TestLanguageForDocPathSharded(unittest.TestCase):
    """Tests for ``language_for_doc_path``'s first-subdirectory derivation (Task 100.170)."""

    def _layout(self, tmp: str) -> Path:
        base = Path(tmp) / "req"
        for name in ("en/ab", "de/ff", "en/de", "Notes", "de-DE", "00"):
            (base / name).mkdir(parents=True)
        return base

    def test_en_shard_file_maps_to_en(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = self._layout(tmp)
            self.assertEqual(language_for_doc_path(base, base / "en" / "ab" / "x.md"), "en")

    def test_variant_shard_file_maps_to_its_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = self._layout(tmp)
            self.assertEqual(language_for_doc_path(base, base / "de" / "ff" / "x.md"), "de")

    def test_flat_file_under_the_domain_base_maps_to_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = self._layout(tmp)
            self.assertIsNone(language_for_doc_path(base, base / "x.md"))

    def test_flat_file_inside_a_language_dir_maps_to_that_language(self):
        """A file missing its shard dir (a lint violation) still sits in the language's own position."""
        with tempfile.TemporaryDirectory() as tmp:
            base = self._layout(tmp)
            self.assertEqual(language_for_doc_path(base, base / "de" / "x.md"), "de")

    def test_non_shape_valid_first_subdirectory_maps_to_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = self._layout(tmp)
            self.assertIsNone(language_for_doc_path(base, base / "Notes" / "x.md"))
            self.assertIsNone(language_for_doc_path(base, base / "de-DE" / "x.md"))

    def test_shard_shaped_first_subdirectory_maps_to_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = self._layout(tmp)
            self.assertIsNone(language_for_doc_path(base, base / "00" / "x.md"))

    def test_a_shard_named_like_a_language_is_never_derived(self):
        """The shard/language collision is dead: ``en/de/`` is the ``en`` language dir's own shard ``de``, and
        the derived language is ``en``, not ``de``."""
        with tempfile.TemporaryDirectory() as tmp:
            base = self._layout(tmp)
            self.assertEqual(language_for_doc_path(base, base / "en" / "de" / "x.md"), "en")

    def test_path_outside_the_base_maps_to_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = self._layout(tmp)
            other = Path(tmp) / "other"
            other.mkdir()
            self.assertIsNone(language_for_doc_path(base, other / "x.md"))

    def test_unresolved_and_resolved_spellings_agree(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = self._layout(tmp)
            doc = base / "de" / "ff" / "x.md"
            self.assertEqual(language_for_doc_path(base, doc), language_for_doc_path(doc.parent.parent.parent, doc))


class TestIterDocPathsAllLanguagesSharded(unittest.TestCase):
    """Tests for ``iter_doc_paths_all_languages``' sharded union (Task 100.170)."""

    def test_missing_directory_yields_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(list(iter_doc_paths_all_languages(Path(tmp) / "missing")), [])

    def test_union_covers_the_sharded_listing_of_every_language_dir_sorted(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "req"
            for rel in ("en/ab/x.md", "en/ff/y.md", "de/00/z.md", "fr/11/w.md"):
                path = base / rel
                path.parent.mkdir(parents=True)
                path.write_text(rel, encoding="utf-8")

            names = [str(p.relative_to(base)) for p in iter_doc_paths_all_languages(base)]

            self.assertEqual(names, ["de/00/z.md", "en/ab/x.md", "en/ff/y.md", "fr/11/w.md"])

    def test_flat_files_and_non_language_subdirectories_are_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "req"
            base.mkdir(parents=True)
            (base / "a.md").write_text("a", encoding="utf-8")  # flat under the domain base
            (base / "Notes").mkdir()
            (base / "Notes" / "n.md").write_text("n", encoding="utf-8")
            (base / "00").mkdir()
            (base / "00" / "s.md").write_text("s", encoding="utf-8")  # a shard-shaped, non-language dir
            (base / "en" / "ab").mkdir(parents=True)
            (base / "en" / "ab" / "x.md").write_text("x", encoding="utf-8")
            (base / "en" / "flat-in-lang.md").write_text("f", encoding="utf-8")  # missing shard dir

            names = [str(p.relative_to(base)) for p in iter_doc_paths_all_languages(base)]

            self.assertEqual(names, ["en/ab/x.md"])


class TestEnOnlyConsumersReRootedAtEnDir(unittest.TestCase):
    """ACC-008 (per domain): the omitted-language base dir is ``en/``, and the EN-only scan sees EN
    files only, never variant files -- the invariant holds by construction (no glob-shape argument)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self._patch = mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(self.root)})
        self._patch.start()
        self.addCleanup(self._patch.stop)
        self.addCleanup(self._tmp.cleanup)

    def _seed_en_and_de(self, spec: DomainSpec) -> tuple[Path, Path]:
        en_file = self.root / spec.d / "en" / "ab" / "abcdef01-0000-0000-0000-000000000001-en.md"
        de_file = self.root / spec.d / "de" / "ab" / "abcdef02-0000-0000-0000-000000000002-de.md"
        for path in (en_file, de_file):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(path.stem, encoding="utf-8")
        return en_file, de_file

    def test_omitted_language_base_dir_is_the_en_directory_for_every_domain(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                self.assertEqual(spec.base_dir(), self.root / spec.d / "en")
                self.assertEqual(spec.base_dir(None), spec.base_dir("en"))

    def test_en_only_scan_never_sees_a_variant_file(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                en_file, de_file = self._seed_en_and_de(spec)

                self.assertEqual(spec.iter_paths(), [en_file])
                self.assertEqual(spec.iter_paths(None), [en_file])
                self.assertEqual(spec.iter_paths("en"), [en_file])
                self.assertEqual(spec.iter_paths("de"), [de_file])

    def test_the_all_languages_union_sees_every_language(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                en_file, de_file = self._seed_en_and_de(spec)

                self.assertEqual(
                    list(iter_doc_paths_all_languages(self.root / spec.d)),
                    sorted([de_file, en_file]),
                )


class TestParseDerivesLanguageFromPathAllDomains(unittest.TestCase):
    """ACC-009 (per domain): every ``parse_<d>`` tool derives the language from the path's first
    subdirectory under the domain base -- a shape-valid two-letter name; ``en`` => canonical, any
    other table-bearing language => that language's table."""

    _ID_PATTERN = re.compile(r"^id: (\S+)$", re.MULTILINE)

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self._patch = mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(self.root)})
        self._patch.start()
        self.addCleanup(self._patch.stop)
        self.addCleanup(self._tmp.cleanup)

    def _seed(self, spec: DomainSpec, relative: str, text: str) -> Path:
        match = self._ID_PATTERN.search(spec.example_text())
        assert match is not None  # every packaged example carries a frontmatter id
        doc_id = match.group(1)
        path = self.root / spec.d / relative.format(shard=doc_id[:2], id=doc_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_parse_in_every_position_for_every_domain(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                en_text = spec.example_text()
                de_text = translate_to_de(en_text)
                self.assertNotEqual(de_text, en_text, f"{spec.d}: de.json covers no heading?")

                # en/ sharded: "en" is derived from the path and resolves to the canonical parse.
                en_doc = spec.fn("parse")(str(self._seed(spec, "en/{shard}/{id}-en-example.md", en_text)))
                self.assertNotIsInstance(en_doc, ValidateResult, en_doc)

                # de/ sharded: the de table is derived from the path and applied.
                de_doc = spec.fn("parse")(str(self._seed(spec, "de/{shard}/{id}-de-example.md", de_text)))
                self.assertNotIsInstance(de_doc, ValidateResult, de_doc)
                self.assertEqual(de_doc, en_doc)  # the same canonical document

                # de text under en/: "en" derives to canonical -- the German headings fail.
                failed = spec.fn("parse")(str(self._seed(spec, "en/{shard}/{id}-de-in-en.md", de_text)))
                self.assertIsInstance(failed, ValidateResult, failed)
                self.assertFalse(failed.valid)


if __name__ == "__main__":
    unittest.main()
