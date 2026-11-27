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

"""Tests for ``general.tools._doc_paths`` (base dir resolution, slugify, id lookup)."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import (
    DEFAULT_DOCS_ROOT,
    DOCS_DIR_ENV_VAR,
    DocNotFoundError,
    doc_base_dir,
    ensure_doc_base_dir,
    find_doc_path_by_id,
    find_parse_failure,
    iter_doc_paths,
    iter_doc_paths_all_languages,
    iter_language_dirs,
    language_for_doc_path,
    slugify,
)


class _FakeDoc:
    """Minimal stand-in for a parsed document, holding just an id."""

    def __init__(self, id_: str | None) -> None:
        self.id = id_


def _read_fake(path: Path) -> _FakeDoc:
    """Read and parse ``path``'s fixture text into a ``_FakeDoc`` (the ``read_fn`` shape, Path in).

    ``"BROKEN"`` simulates a parse failure -- mirrors the shape a domain's
    own cache-backed ``read_<domain>`` (e.g. ``req.tools._cache.read_req``)
    has: takes a ``Path``, reads its text itself.
    """
    stripped = path.read_text(encoding="utf-8").strip()
    if stripped == "BROKEN":
        raise ValueError("simulated parse failure")
    return _FakeDoc(id_=stripped or None)


def _get_id(doc: _FakeDoc) -> str | None:
    return doc.id


def _read_broken(path: Path) -> _FakeDoc:
    """``read_fn`` that fails to parse a file whose content is ``"BROKEN"`` (a structural ``AssertionError``).

    Distinct from :func:`_read_fake` (which raises a plain ``ValueError``) -- :func:`find_parse_failure`
    catches the exact parse-failure channels a domain's ``parse_<d>`` raises (``AssertionError``/
    ``pydantic.ValidationError``/``yaml.YAMLError``), so the simulated failure must be one of those.
    """
    stripped = path.read_text(encoding="utf-8").strip()
    if stripped == "BROKEN":
        raise AssertionError("simulated structural parse failure")
    return _FakeDoc(id_=stripped or None)


class TestSlugify(unittest.TestCase):
    """Tests for slugify."""

    def test_lowercases(self):
        """Upper-case letters must be lowercased."""
        self.assertEqual(slugify("A Title"), "a-title")

    def test_collapses_non_alnum_runs(self):
        """A run of non-alphanumeric characters must collapse to a single hyphen."""
        self.assertEqual(slugify("A  Title!! With--Punctuation"), "a-title-with-punctuation")

    def test_strips_leading_and_trailing_hyphens(self):
        """Leading/trailing separator characters must not survive as hyphens."""
        self.assertEqual(slugify("!!!A Title!!!"), "a-title")

    def test_truncates_to_60_characters(self):
        """The slug must be truncated to 60 characters."""
        long_title = "word " * 30  # much longer than 60 chars once slugified
        slug = slugify(long_title)
        self.assertLessEqual(len(slug), 60)

    def test_truncation_does_not_leave_a_trailing_hyphen(self):
        """Truncating mid-run must not leave a dangling trailing hyphen."""
        # Constructed so the 60-char cut lands exactly on a hyphen.
        title = "a" * 59 + " " + "b" * 10
        slug = slugify(title)
        self.assertFalse(slug.endswith("-"))

    def test_empty_result_falls_back_to_doc(self):
        """A title with no alphanumeric characters at all must fall back to 'doc'."""
        self.assertEqual(slugify("!!!???"), "doc")


class TestDocBaseDir(unittest.TestCase):
    """Tests for doc_base_dir."""

    def test_defaults_when_env_var_unset(self):
        """Without SPECMGR_DOCS_DIR set, the default root + type_name + the ``en/`` language dir
        is returned (feat-245: the omitted language resolves to ``en/``, no flat special case)."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(DOCS_DIR_ENV_VAR, None)
            self.assertEqual(doc_base_dir("req"), DEFAULT_DOCS_ROOT / "req" / "en")

    def test_respects_env_var(self):
        """SPECMGR_DOCS_DIR, when set, overrides the default root."""
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/some-custom-docs-dir"}):
            self.assertEqual(doc_base_dir("req"), Path("/tmp/some-custom-docs-dir/req/en"))

    def test_set_but_empty_env_var_falls_back_to_default(self):
        """SPECMGR_DOCS_DIR, when set but empty, falls back to the default root (the Option A
        ``empty_falls_back_to_default`` registry flag, feat-208 Phase 110/120)."""
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: ""}):
            self.assertEqual(doc_base_dir("req"), DEFAULT_DOCS_ROOT / "req" / "en")

    def test_different_type_names_yield_different_subdirectories(self):
        """Each doc type gets its own subdirectory under the shared root (the ``en/`` dir in every
        one, feat-245)."""
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/some-custom-docs-dir"}):
            self.assertEqual(doc_base_dir("req"), Path("/tmp/some-custom-docs-dir/req/en"))
            self.assertEqual(doc_base_dir("uc"), Path("/tmp/some-custom-docs-dir/uc/en"))

    def test_does_not_create_the_directory(self):
        """doc_base_dir must never create the directory as a side effect."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                doc_base_dir("req")
            self.assertFalse(missing_root.exists())


class TestEnsureDocBaseDir(unittest.TestCase):
    """Tests for ensure_doc_base_dir."""

    def test_creates_the_directory(self):
        """ensure_doc_base_dir must create the directory (and its parents) if missing -- the
        ``en/`` language dir (feat-245)."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                result = ensure_doc_base_dir("req")
            self.assertTrue(result.exists())
            self.assertEqual(result, missing_root / "req" / "en")

    def test_is_idempotent_for_an_already_existing_directory(self):
        """Calling ensure_doc_base_dir twice must not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: tmp}):
                ensure_doc_base_dir("req")
                result = ensure_doc_base_dir("req")
            self.assertTrue(result.exists())


class TestIterDocPaths(unittest.TestCase):
    """Tests for iter_doc_paths."""

    def test_empty_iterator_for_missing_directory(self):
        """A non-existent base_dir must yield nothing, not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist"
            self.assertEqual(list(iter_doc_paths(missing)), [])

    def test_empty_iterator_for_empty_directory(self):
        """An existing but empty directory must yield nothing."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(list(iter_doc_paths(Path(tmp))), [])

    def test_yields_sharded_md_files_sorted_by_relative_path(self):
        """The sharded listing of a language dir must be yielded in sorted (by relative path)
        order, and only ``*.md`` files (feat-245's shard-only scan)."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "01" / "b.md").parent.mkdir(parents=True)
            (base / "01" / "b.md").write_text("b", encoding="utf-8")
            (base / "00" / "a.md").parent.mkdir(parents=True)
            (base / "00" / "a.md").write_text("a", encoding="utf-8")
            (base / "00" / "not-markdown.txt").write_text("x", encoding="utf-8")
            paths = list(iter_doc_paths(base))
            self.assertEqual([p.name for p in paths], ["a.md", "b.md"])

    def test_flat_files_missing_the_shard_dir_are_never_yielded(self):
        """A *.md file directly under the language dir (missing the shard dir) is invisible to the
        shard-only scan (feat-245, REQ-003 -- the hard cut-over; the lint gate is what catches
        such a file)."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "a.md").write_text("a", encoding="utf-8")
            (base / "00" / "x.md").parent.mkdir(parents=True)
            (base / "00" / "x.md").write_text("x", encoding="utf-8")
            paths = list(iter_doc_paths(base))
            self.assertEqual([p.name for p in paths], ["x.md"])

    def test_files_deeper_than_one_shard_level_are_never_yielded(self):
        """A *.md file nested deeper than the one shard level is invisible to the shard-only scan
        (feat-245, REQ-003)."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "00" / "x.md").parent.mkdir(parents=True)
            (base / "00" / "x.md").write_text("x", encoding="utf-8")
            (base / "00" / "nested" / "d.md").parent.mkdir(parents=True)
            (base / "00" / "nested" / "d.md").write_text("deep", encoding="utf-8")
            paths = list(iter_doc_paths(base))
            self.assertEqual([p.name for p in paths], ["x.md"])


class TestFindDocPathById(unittest.TestCase):
    """Tests for find_doc_path_by_id."""

    def test_finds_matching_id(self):
        """A file whose parsed id matches must be returned (sharded under the shard derived from
        the id, feat-245's fast path)."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "ab" / "ab-target-id.md"
            path.parent.mkdir(parents=True)
            path.write_text("ab-target-id", encoding="utf-8")
            self.assertEqual(find_doc_path_by_id(base, "ab-target-id", _read_fake, _get_id), path)

    def test_a_document_in_the_wrong_shard_is_still_found_by_the_fallback(self):
        """REQ-004: a file whose shard dir disagrees with its id is still resolved through the
        full sharded-listing fallback (the filesystem remains the sole source of truth)."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "ff" / "ab-target-id.md"  # the id "ab-target-id" wants shard "ab"
            path.parent.mkdir(parents=True)
            path.write_text("ab-target-id", encoding="utf-8")
            self.assertEqual(find_doc_path_by_id(base, "ab-target-id", _read_fake, _get_id), path)

    def test_raises_not_found_for_unknown_id(self):
        """An id with no matching file must raise DocNotFoundError with the standardized message."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "0e" / "one-id.md").parent.mkdir(parents=True)
            (base / "0e" / "one-id.md").write_text("one-id", encoding="utf-8")
            with self.assertRaises(DocNotFoundError) as ctx:
                find_doc_path_by_id(base, "missing-id", _read_fake, _get_id)
            message = str(ctx.exception)
            self.assertIn("no document found with id 'missing-id'", message)
            self.assertIn("bare document UUID", message)
            self.assertIn("without a domain prefix", message)

    def test_raises_not_found_for_empty_directory(self):
        """An empty base_dir must raise DocNotFoundError, not e.g. StopIteration."""
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(DocNotFoundError):
                find_doc_path_by_id(Path(tmp), "missing-id", _read_fake, _get_id)

    def test_skips_malformed_file_and_still_finds_valid_one(self):
        """A file that fails to parse must not prevent finding a different, valid id (both in the
        id's own shard, so the fast path exercises the skip)."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "cd" / "broken.md").parent.mkdir(parents=True)
            (base / "cd" / "broken.md").write_text("BROKEN", encoding="utf-8")
            good_path = base / "cd" / "cd-good-id.md"
            good_path.write_text("cd-good-id", encoding="utf-8")
            self.assertEqual(find_doc_path_by_id(base, "cd-good-id", _read_fake, _get_id), good_path)

    def test_is_generic_over_doc_type_via_parse_and_get_id_functions(self):
        """A different read_fn/get_id_fn pair must work independently (no cross-domain coupling)."""

        class _OtherDoc:
            def __init__(self, ident: str) -> None:
                self.ident = ident

        def _read_other(path: Path) -> _OtherDoc:
            return _OtherDoc(ident=path.read_text(encoding="utf-8").strip())

        def _get_other_id(doc: _OtherDoc) -> str:
            return doc.ident

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "ef" / "ef-other-id.md"
            path.parent.mkdir(parents=True)
            path.write_text("ef-other-id", encoding="utf-8")
            self.assertEqual(find_doc_path_by_id(base, "ef-other-id", _read_other, _get_other_id), path)

    def test_reconcile_fn_is_called_with_the_materialized_live_path_listing_before_any_per_file_work(self):
        """`reconcile_fn`, when given, is invoked once with the full live path listing."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "ab" / "ab-target-id.md"
            path.parent.mkdir(parents=True)
            path.write_text("ab-target-id", encoding="utf-8")
            calls: list[list[Path]] = []

            def _reconcile(live_paths):
                calls.append(list(live_paths))

            self.assertEqual(
                find_doc_path_by_id(base, "ab-target-id", _read_fake, _get_id, reconcile_fn=_reconcile), path
            )
            self.assertEqual(calls, [[path]])

    def test_reconcile_fn_defaults_to_none_and_is_never_called_if_omitted(self):
        """Omitting `reconcile_fn` must not raise -- it defaults to a no-op (None)."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "ab" / "ab-target-id.md"
            path.parent.mkdir(parents=True)
            path.write_text("ab-target-id", encoding="utf-8")
            self.assertEqual(find_doc_path_by_id(base, "ab-target-id", _read_fake, _get_id), path)


class TestFindParseFailure(unittest.TestCase):
    """Tests for find_parse_failure (feat-150-mcp-lifecycle-commands Phase 1a, DEC 9080b37c)."""

    def test_name_match_parse_fail_returns_path_and_error(self) -> None:
        """A name-matching file that fails to parse must return (path, str(exc)) -- sharded under
        the id's own shard (feat-245); the pre-sharding ``<type>-<id>-<slug>.md`` name form is kept
        as the compatibility branch pin."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "de" / "req-deadbeef-0000-0000-0000-000000000000-broken.md"
            path.parent.mkdir(parents=True)
            path.write_text("BROKEN", encoding="utf-8")

            result = find_parse_failure(base, "deadbeef-0000-0000-0000-000000000000", _read_broken)

            self.assertIsNotNone(result)
            assert result is not None
            self.assertEqual(result[0], path)
            self.assertEqual(result[1], "simulated structural parse failure")

    def test_name_match_parse_ok_returns_none(self) -> None:
        """A name-matching file that parses cleanly (a frontmatter-id mismatch, not our document) must return None."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            healthy = base / "de" / "req-deadbeef-0000-0000-0000-000000000000-healthy.md"
            healthy.parent.mkdir(parents=True)
            healthy.write_text("some-other-id", encoding="utf-8")

            result = find_parse_failure(base, "deadbeef-0000-0000-0000-000000000000", _read_broken)

            self.assertIsNone(result)

    def test_no_name_match_returns_none(self) -> None:
        """No name-matching file must return None."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            other = base / "11" / "req-11111111-1111-1111-1111-111111111111-x.md"
            other.parent.mkdir(parents=True)
            other.write_text("11111111-1111-1111-1111-111111111111", encoding="utf-8")

            result = find_parse_failure(base, "deadbeef-0000-0000-0000-000000000000", _read_broken)

            self.assertIsNone(result)

    def test_prefix_only_match_parse_fail_returns_path_and_error(self) -> None:
        """A file matching the id-prefix form (`<id>-<slug>.md`, no type prefix -- the sharded
        layout's own naming) that fails to parse must return (path, str(exc))."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "de" / "deadbeef-0000-0000-0000-000000000000-broken.md"
            path.parent.mkdir(parents=True)
            path.write_text("BROKEN", encoding="utf-8")

            result = find_parse_failure(base, "deadbeef-0000-0000-0000-000000000000", _read_broken)

            self.assertIsNotNone(result)
            assert result is not None
            self.assertEqual(result[0], path)
            self.assertEqual(result[1], "simulated structural parse failure")

    def test_two_name_matches_are_ambiguous_returns_none(self) -> None:
        """Two files both name-matching the same id (however that happened) must return None -- ambiguous, skip."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "de").mkdir(parents=True)
            (base / "de" / "req-deadbeef-0000-0000-0000-000000000000-a.md").write_text("BROKEN", encoding="utf-8")
            (base / "de" / "req-deadbeef-0000-0000-0000-000000000000-b.md").write_text("BROKEN", encoding="utf-8")

            result = find_parse_failure(base, "deadbeef-0000-0000-0000-000000000000", _read_broken)

            self.assertIsNone(result)

    def test_vanished_file_mid_scan_returns_none(self) -> None:
        """A name-matching file whose read_fn raises FileNotFoundError (vanished mid-scan) must return None."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            path = base / "de" / "req-deadbeef-0000-0000-0000-000000000000-x.md"
            path.parent.mkdir(parents=True)
            path.write_text("irrelevant", encoding="utf-8")

            def _read_vanished(_path: Path) -> _FakeDoc:
                raise FileNotFoundError("simulated vanish mid-scan")

            result = find_parse_failure(base, "deadbeef-0000-0000-0000-000000000000", _read_vanished)

            self.assertIsNone(result)


class TestDocBaseDirLanguage(unittest.TestCase):
    """Tests for doc_base_dir's optional language parameter (feat-197-i18n Phase 110, DEC 38efdb66 item 1)."""

    def test_omitted_language_is_the_en_directory(self):
        """language omitted must resolve to the ``en/`` directory (feat-245: no flat-EN special
        case any more -- every language, EN included, gets its own subdirectory)."""
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/custom-docs"}):
            self.assertEqual(doc_base_dir("dec"), Path("/tmp/custom-docs/dec/en"))

    def test_none_language_is_the_en_directory(self):
        """language=None must resolve to the ``en/`` directory."""
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/custom-docs"}):
            self.assertEqual(doc_base_dir("dec", None), Path("/tmp/custom-docs/dec/en"))

    def test_explicit_en_is_the_en_directory(self):
        """An explicit language='en' must resolve to the ``en/`` directory (EN is a normal language
        dir, feat-245's uniform layout)."""
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/custom-docs"}):
            self.assertEqual(doc_base_dir("dec", "en"), Path("/tmp/custom-docs/dec/en"))

    def test_other_language_is_its_subdirectory(self):
        """A shape-validated non-default language resolves to docs/{type}/{language}/."""
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/custom-docs"}):
            self.assertEqual(doc_base_dir("dec", "de"), Path("/tmp/custom-docs/dec/de"))

    def test_invalid_language_is_rejected_before_path_construction(self):
        """A shape-invalid language must raise ValueError (the guard runs before the path is
        built -- no path-significant value can reach the join)."""
        for value in ("", "d", "de3", "DE", "de x", "../../etc", "de/x", "/abs"):
            with self.subTest(value=value):
                with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/custom-docs"}):
                    with self.assertRaises(ValueError) as ctx:
                        doc_base_dir("dec", value)
                    self.assertIn(repr(value), str(ctx.exception))

    def test_language_parameter_does_not_create_the_directory(self):
        """doc_base_dir (any language) must never create the directory as a side effect."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                doc_base_dir("dec", "de")
            self.assertFalse(missing_root.exists())


class TestEnsureDocBaseDirLanguage(unittest.TestCase):
    """Tests for ensure_doc_base_dir's optional language parameter (feat-197-i18n Phase 110)."""

    def test_creates_the_language_subdirectory(self):
        """ensure_doc_base_dir(type, 'de') must create docs/{type}/de/ (and its parents)."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist-yet"
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(missing_root)}):
                result = ensure_doc_base_dir("dec", "de")
            self.assertTrue(result.exists())
            self.assertEqual(result, missing_root / "dec" / "de")

    def test_en_creates_the_en_directory(self):
        """ensure_doc_base_dir(type, 'en') (and omitted) must create the ``en/`` directory (feat-245:
        no flat special case)."""
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: tmp}):
                self.assertEqual(ensure_doc_base_dir("dec", "en"), Path(tmp) / "dec" / "en")
                self.assertEqual(ensure_doc_base_dir("dec"), Path(tmp) / "dec" / "en")


class TestLanguageForDocPath(unittest.TestCase):
    """Tests for language_for_doc_path (the path-position -> language derivation, DEC 38efdb66 item 5)."""

    def _layout(self, tmp: str) -> Path:
        base = Path(tmp) / "dec"
        (base / "de" / "00").mkdir(parents=True)
        (base / "Notes").mkdir()
        return base

    def test_a_document_missing_the_language_dir_is_none(self):
        """A document directly in the domain base directory (missing the language dir -- the
        pre-sharding flat position) maps to None (canonical parse, no table)."""
        with tempfile.TemporaryDirectory() as tmp:
            base = self._layout(tmp)
            self.assertIsNone(language_for_doc_path(base, base / "a.md"))

    def test_language_subdirectory_document_maps_to_its_language(self):
        """A sharded document in a shape-valid {language} subdirectory maps to that language (the
        shard level in between is never inspected, feat-245)."""
        with tempfile.TemporaryDirectory() as tmp:
            base = self._layout(tmp)
            self.assertEqual(language_for_doc_path(base, base / "de" / "00" / "a.md"), "de")

    def test_non_shape_valid_subdirectory_is_none(self):
        """A document in a non-shape-validated subdirectory ('Notes', 'de-DE') maps to None -- it is
        not a language location, so the document parses canonical-only."""
        with tempfile.TemporaryDirectory() as tmp:
            base = self._layout(tmp)
            self.assertIsNone(language_for_doc_path(base, base / "Notes" / "a.md"))
            (base / "de-DE").mkdir()
            self.assertIsNone(language_for_doc_path(base, base / "de-DE" / "a.md"))

    def test_the_shard_level_is_never_inspected_and_a_shard_shaped_first_dir_is_no_language(self):
        """A document nested under a language dir plus a shard dir maps to the language (the shard
        level is never inspected); a shard-shaped first subdirectory (two digits) is NOT a shape-
        valid language and maps to None."""
        with tempfile.TemporaryDirectory() as tmp:
            base = self._layout(tmp)
            self.assertEqual(language_for_doc_path(base, base / "de" / "00" / "a.md"), "de")
            (base / "00").mkdir(parents=True)
            self.assertIsNone(language_for_doc_path(base, base / "00" / "a.md"))

    def test_path_outside_the_base_is_none(self):
        """A document outside the base directory entirely maps to None."""
        with tempfile.TemporaryDirectory() as tmp:
            base = self._layout(tmp)
            other = Path(tmp) / "other"
            other.mkdir()
            self.assertIsNone(language_for_doc_path(base, other / "a.md"))

    def test_unresolved_and_resolved_spellings_agree(self):
        """Relative and resolved spellings of the same location must classify identically
        (both sides are .resolve()d)."""
        with tempfile.TemporaryDirectory() as tmp:
            base = self._layout(tmp)
            doc = base / "de" / "00" / "a.md"
            self.assertEqual(language_for_doc_path(base, doc), language_for_doc_path(doc.parent.parent.parent, doc))


class TestIterDocPathsAllLanguages(unittest.TestCase):
    """Tests for iter_doc_paths_all_languages (the domain-wide live listing, DEC 38efdb66 item 9)."""

    def test_missing_directory_yields_nothing(self):
        """A non-existent base directory must yield nothing, not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(list(iter_doc_paths_all_languages(Path(tmp) / "missing")), [])

    def test_union_of_the_sharded_listings_of_every_language_directory(self):
        """The union covers the sharded listing of ``en/`` plus the sharded listing of every other
        shape-valid {language} subdirectory, sorted by path (feat-245's domain-wide live listing)."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "dec"
            (base / "en" / "01").mkdir(parents=True)
            (base / "en" / "00").mkdir(parents=True)
            (base / "de" / "aa").mkdir(parents=True)
            (base / "fr" / "bb").mkdir(parents=True)
            (base / "flat.md").write_text("flat", encoding="utf-8")
            (base / "en" / "01" / "b.md").write_text("b", encoding="utf-8")
            (base / "en" / "00" / "a.md").write_text("a", encoding="utf-8")
            (base / "de" / "aa" / "x.md").write_text("x", encoding="utf-8")
            (base / "fr" / "bb" / "y.md").write_text("y", encoding="utf-8")
            names = [str(p.relative_to(base)) for p in iter_doc_paths_all_languages(base)]
            self.assertEqual(names, ["de/aa/x.md", "en/00/a.md", "en/01/b.md", "fr/bb/y.md"])

    def test_non_language_subdirectories_and_flat_files_are_excluded(self):
        """Files in non-shape-validated subdirectories and a flat file directly under the domain
        base are not part of any domain's live listing (no tool ever scans them, so no cache entry
        for them can exist)."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "dec"
            (base / "en" / "00").mkdir(parents=True)
            (base / "de" / "aa").mkdir(parents=True)
            (base / "Notes").mkdir()
            (base / "de-DE").mkdir()
            (base / "flat.md").write_text("flat", encoding="utf-8")
            (base / "en" / "00" / "a.md").write_text("a", encoding="utf-8")
            (base / "de" / "aa" / "x.md").write_text("x", encoding="utf-8")
            (base / "Notes" / "n.md").write_text("n", encoding="utf-8")
            (base / "de-DE" / "d.md").write_text("d", encoding="utf-8")
            names = [str(p.relative_to(base)) for p in iter_doc_paths_all_languages(base)]
            self.assertEqual(names, ["de/aa/x.md", "en/00/a.md"])


class TestIterLanguageDirs(unittest.TestCase):
    """Tests for iter_language_dirs (the language-directory discovery primitive, feat-197-i18n Phase 140)."""

    def test_missing_directory_yields_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(list(iter_language_dirs(Path(tmp) / "missing")), [])

    def test_yields_shape_valid_language_directories_sorted_and_skips_everything_else(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "dec"
            for name in ("fr", "de", "Notes", "de-DE", "DE", "deu", "x", "00"):
                (base / name).mkdir(parents=True)
            (base / "xx").write_text("a file named like a language", encoding="utf-8")
            (base / "a.md").write_text("a", encoding="utf-8")

            result = [(language, path.name) for language, path in iter_language_dirs(base)]

            # "00" (a shard-shaped dir) carries a digit and is not a shape-valid language code.
            self.assertEqual(result, [("de", "de"), ("fr", "fr")])

    def test_does_not_inspect_directory_contents_or_descend(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "dec"
            (base / "de" / "nested").mkdir(parents=True)
            (base / "pt").mkdir()

            result = [language for language, _path in iter_language_dirs(base)]

            self.assertEqual(result, ["de", "pt"])  # an empty language dir is still a language location


if __name__ == "__main__":
    unittest.main()
