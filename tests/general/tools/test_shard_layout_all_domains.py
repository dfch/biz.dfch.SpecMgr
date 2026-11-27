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

"""Tool-level pins of the sharded read/write layout over all thirteen sharded domains (feat-245 Phase 180).

- **ACC-003 (Task 180.130, G1) + the non-hex shard (Task 180.190, D4)** -- a healthy document hand-placed directly
  under ``docs/<type>/`` (missing language dir), directly under ``docs/<type>/<lang>/`` (missing shard dir), or in a
  non-hex shard dir (``docs/<type>/<lang>/zz/``) is absent from ``list_<d>`` (EN and ``language="de"``), ``get_<d>``
  raises the domain's not-found error, and ``list_languages`` does not report it; a BROKEN file at the same positions
  is not surfaced as a ``ParseFailureResult`` either (the ``find_parse_failure`` probe reads the sharded listing only).
  Phase 190 (Task 190.120): with the EN document correctly sharded, a misplaced ``de`` variant alone is invisible
  (``list_languages`` -> ``["en"]``, ``get_<d>(language="de")`` not-found, ``list_<d>(language="de")`` empty).
- **E3 (Task 180.120)** -- a language variant's basename is the EN source's basename verbatim (DEC 38efdb66 item 2),
  even for an EN source not named ``<id>-<slug>.md``, through the shared ``sharded_variant_path`` helper.
- **S3 (Task 180.220)** -- a broken legacy-named ``<type>-<uuid>-<slug>.md`` file inside its correct shard makes
  ``get_<d>`` return the real ``ParseFailureResult`` (the kept ``-{id}-`` name match), not a bare not-found.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from biz.dfch.specmgr.general.models import ParseFailureResult, ValidateResult
from biz.dfch.specmgr.general.tools.list_languages import list_languages

from .test_i18n_all_domains import SPECS, DomainSpec, _TempDocsMixin

_BROKEN_TEXT = "not a valid specmgr document -- no frontmatter, no headings\n"


def _misplaced_positions(domain_dir: Path, language: str, name: str) -> list[Path]:
    """The invalid read positions of one language: missing language dir, missing shard dir, non-hex shard dir."""
    result = [
        domain_dir / name,
        domain_dir / language / name,
        domain_dir / language / "zz" / name,
    ]
    return result


class TestAcc003MisplacedFilesAreInvisibleAllDomains(_TempDocsMixin):
    """ACC-003 at tool level (Task 180.130) + the non-hex shard case (Task 180.190): misplaced = invisible."""

    def _seed_and_move(self, spec: DomainSpec, en_target: Path, de_target: Path | None) -> str:
        """Create the EN document + its DE variant through the tools, then move both to the given positions."""
        doc_id, en_file, de_file = self.seed(spec)
        en_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(en_file, en_target)
        if de_target is None:
            de_file.unlink()
        else:
            de_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(de_file, de_target)
        spec.reset_cache()
        return doc_id

    def _assert_invisible(self, spec: DomainSpec, doc_id: str) -> None:
        for language in ("en", "de"):
            listed = spec.fn("list")(language=language)
            self.assertEqual(listed.total, 0, (language, listed))
            self.assertEqual(listed.results, [])
            with self.assertRaises(spec.not_found_error()):
                spec.fn("get")(doc_id, language=language)
        with self.assertRaises(spec.not_found_error()):
            list_languages(spec.d, doc_id)

    def test_a_healthy_misplaced_file_is_absent_from_list_get_and_list_languages(self):
        for spec in SPECS:
            domain_dir = self.docs_root / spec.d
            cases = {
                "missing language dir": (domain_dir / "flat.md", None),
                "missing shard dir": (domain_dir / "en" / "flat.md", domain_dir / "de" / "flat.md"),
                "non-hex shard dir": (domain_dir / "en" / "zz" / "x.md", domain_dir / "de" / "zz" / "x.md"),
            }
            for case, (en_target, de_target) in cases.items():
                with self.subTest(domain=spec.d, case=case):
                    shutil.rmtree(domain_dir, ignore_errors=True)
                    doc_id = self._seed_and_move(spec, en_target, de_target)
                    self.assertTrue(en_target.is_file(), en_target)
                    self._assert_invisible(spec, doc_id)

    def test_a_misplaced_variant_beside_a_correctly_sharded_en_document_is_invisible(self):
        """Phase 190 (Task 190.120, G1 of review cycle 5): the EN document stays correctly sharded, only the
        ``de`` variant is misplaced (flat directly under ``docs/<d>/de/``, or in the non-hex ``docs/<d>/de/zz/``):
        ``list_languages`` reports ``["en"]`` only, ``get_<d>(language="de")`` raises not-found, and
        ``list_<d>(language="de")`` is empty -- while the EN document stays fully visible."""
        for spec in SPECS:
            domain_dir = self.docs_root / spec.d
            for case, shard in (("missing shard dir", None), ("non-hex shard dir", "zz")):
                with self.subTest(domain=spec.d, case=case):
                    shutil.rmtree(domain_dir, ignore_errors=True)
                    doc_id, en_file, de_file = self.seed(spec)
                    de_dir = domain_dir / "de" if shard is None else domain_dir / "de" / shard
                    de_target = de_dir / de_file.name
                    de_target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(de_file, de_target)
                    spec.reset_cache()
                    self.assertTrue(en_file.is_file(), en_file)
                    self.assertTrue(de_target.is_file(), de_target)

                    languages = list_languages(spec.d, doc_id)
                    self.assertEqual(languages.languages, ["en"])
                    self.assertEqual([Path(entry.path) for entry in languages.entries], [en_file.resolve()])
                    with self.assertRaises(spec.not_found_error()):
                        spec.fn("get")(doc_id, language="de")
                    listed_de = spec.fn("list")(language="de")
                    self.assertEqual(listed_de.total, 0, listed_de)
                    self.assertEqual(listed_de.results, [])
                    self.assertEqual(spec.fn("list")(language="en").total, 1)

    def test_a_broken_misplaced_file_is_not_surfaced_as_a_parse_failure(self):
        for spec in SPECS:
            domain_dir = self.docs_root / spec.d
            with self.subTest(domain=spec.d):
                shutil.rmtree(domain_dir, ignore_errors=True)
                doc_id, en_file, de_file = self.seed(spec)
                en_file.unlink()
                de_file.unlink()
                for language in ("en", "de"):
                    for position in _misplaced_positions(domain_dir, language, f"{doc_id}-broken.md"):
                        position.parent.mkdir(parents=True, exist_ok=True)
                        position.write_text(_BROKEN_TEXT, encoding="utf-8")
                spec.reset_cache()
                for language in ("en", "de"):
                    # A returned ParseFailureResult (instead of the raise) fails this assertion.
                    with self.assertRaises(spec.not_found_error()):
                        spec.fn("get")(doc_id, language=language)
                    listed = spec.fn("list")(language=language)
                    self.assertEqual(listed.total, 0, (language, listed))


class TestVariantBasenameIsTheEnSourceBasenameVerbatimAllDomains(_TempDocsMixin):
    """E3 (Task 180.120): the variant lands under ``<lang>/<shard>/`` at the EN source's basename, verbatim."""

    def test_an_en_source_not_named_id_dash_slug_keeps_its_exact_basename_for_the_variant(self):
        for spec in SPECS:
            for form in ("legacy", "doubled"):
                with self.subTest(domain=spec.d, form=form):
                    spec.reset_cache()
                    created = spec.fn("create")(spec.en_body())
                    assert not isinstance(created, ValidateResult), created
                    doc_id = created.id
                    en_file = next(path for path in spec.iter_paths() if path.name.startswith(f"{doc_id}-"))
                    slug = en_file.name.removeprefix(f"{doc_id}-")
                    # "legacy": a pre-sharding type-prefixed name moved into its shard without renaming (the
                    # case the former removeprefix-and-rebuild derivation doubled to <id>-<type>-<id>-<slug>.md);
                    # "doubled": the hand-named <id>-<type>-<id>-<slug>.md form of the Task 180.120 line.
                    hand_name = (
                        f"{spec.d}-{doc_id}-{slug}" if form == "legacy" else f"{doc_id}-{spec.d}-{doc_id}-{slug}"
                    )
                    hand_named = en_file.with_name(hand_name)
                    en_file.rename(hand_named)
                    spec.reset_cache()

                    variant = spec.fn("create")(spec.de_body(), language="de", id=doc_id)
                    assert not isinstance(variant, ValidateResult), variant

                    expected = spec.base_dir("de") / doc_id[:2] / hand_name
                    self.assertTrue(expected.is_file(), expected)
                    de_files = [path for path in spec.iter_paths("de") if doc_id in path.name]
                    self.assertEqual(de_files, [expected])


class TestBrokenLegacyNamedFileInItsShardSurfacesTheParseFailure(_TempDocsMixin):
    """S3 (Task 180.220): the kept legacy ``-{id}-`` name match -- one domain suffices, the primitive is shared."""

    def test_get_returns_parse_failure_result_for_a_broken_legacy_named_file_in_its_shard(self):
        spec = next(s for s in SPECS if s.d == "req")
        created = spec.fn("create")(spec.en_body())
        assert not isinstance(created, ValidateResult), created
        doc_id = created.id
        en_file = spec.iter_paths()[0]
        legacy = en_file.with_name(f"req-{en_file.name}")
        en_file.rename(legacy)
        legacy.write_text(_BROKEN_TEXT, encoding="utf-8")
        spec.reset_cache()

        result = spec.fn("get")(doc_id)

        self.assertIsInstance(result, ParseFailureResult)
        self.assertEqual(Path(result.path), legacy.resolve())
        self.assertEqual(result.id, doc_id)
