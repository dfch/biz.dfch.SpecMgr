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

"""ACC-001/ACC-003/REQ-003/REQ-012 with THREE languages of one artifact, for all eleven domains
(feat-197-i18n Phase 150, Task 150.100/150.110 gap closing).

The shipped ``de`` table is the only real second language, so the existing suites exercise two languages at most.
This module adds a third one (``fr``, whose table is a copy of ``de.json`` redirected through the loader's
``heading_table_path`` seam -- the established technique of ``test_check_translation_drift.py``; the *content* of a
table is irrelevant to the properties pinned here) and asserts, for every i18n-eligible domain, that two NON-EN
variants of one artifact share the id of the EN source (ACC-003, REQ-003), live in their own language subfolder under
the identical basename (ACC-001, ADR item 2), never disturb each other or EN, are each listed by exactly one
``list_<d>(language=...)`` call, and are all reported by ``list_languages`` (REQ-012).
"""

from __future__ import annotations

from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import heading_table as heading_table_module
from biz.dfch.specmgr.general.models import ValidateResult
from biz.dfch.specmgr.general.tools.delete import delete
from biz.dfch.specmgr.general.tools.list_languages import list_languages
from biz.dfch.specmgr.general.tools.update import update

from .test_i18n_all_domains import SPECS, _TempDocsMixin


class TestThreeLanguagesOfOneArtifact(_TempDocsMixin):
    """EN + ``de`` + ``fr`` of one id, per domain."""

    def setUp(self) -> None:
        super().setUp()
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

    def seed_three(self, spec) -> tuple[str, Path, Path, Path]:
        """Create EN, then the ``de`` and ``fr`` variants of the same id; return (id, EN, DE, FR) paths."""
        created = spec.fn("create")(spec.en_body())
        assert not isinstance(created, ValidateResult), created
        for language in ("de", "fr"):
            variant = spec.fn("create")(spec.de_body(), language=language, id=created.id)
            assert not isinstance(variant, ValidateResult), variant
            assert variant.id == created.id
        en_file = next(spec.base_dir().glob("*.md"))
        return created.id, en_file, spec.base_dir("de") / en_file.name, spec.base_dir("fr") / en_file.name

    def test_two_non_en_variants_share_the_en_id_and_basename(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, en_file, de_file, fr_file = self.seed_three(spec)

                for path in (en_file, de_file, fr_file):
                    self.assertTrue(path.is_file(), path)
                    self.assertIn(f"id: {doc_id}", path.read_text(encoding="utf-8").split("---\n")[1])
                self.assertEqual({en_file.name, de_file.name, fr_file.name}, {en_file.name})
                self.assertEqual(
                    {p.parent.name for p in (en_file, de_file, fr_file)}, {spec.d, "de", "fr"}
                )  # ACC-001: EN flat, others in their own subfolder
                ids = {spec.fn("get")(doc_id, language=lang).frontmatter.id for lang in ("en", "de", "fr")}
                self.assertEqual(ids, {doc_id})

    def test_each_list_call_sees_exactly_one_language_and_the_id_is_never_duplicated(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, en_file, de_file, fr_file = self.seed_three(spec)

                for language, path in (("en", en_file), ("de", de_file), ("fr", fr_file)):
                    rows = spec.fn("list")(language=language).results
                    self.assertEqual([r.id for r in rows], [doc_id])
                    self.assertEqual(Path(rows[0].path), path.resolve())

    def test_list_languages_reports_all_three_with_en_first(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, _en_file, _de_file, _fr_file = self.seed_three(spec)

                result = list_languages(type=spec.d, id=doc_id)

                self.assertEqual(result.languages, ["en", "de", "fr"])
                self.assertTrue(all(entry.parseable for entry in result.entries))

    def test_writing_or_deleting_one_variant_leaves_the_other_two_untouched(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, en_file, de_file, fr_file = self.seed_three(spec)
                en_before, fr_before = en_file.read_bytes(), fr_file.read_bytes()

                updated = update(type=spec.d, id=doc_id, content=spec.de_body().rstrip("\n") + "\n", language="de")
                self.assertNotIsInstance(updated, ValidateResult, updated)
                self.assertEqual(en_file.read_bytes(), en_before)
                self.assertEqual(fr_file.read_bytes(), fr_before)

                delete(type=spec.d, id=doc_id, language="de")
                self.assertFalse(de_file.exists())
                self.assertEqual(en_file.read_bytes(), en_before)
                self.assertEqual(fr_file.read_bytes(), fr_before)
                self.assertEqual(list_languages(type=spec.d, id=doc_id).languages, ["en", "fr"])
