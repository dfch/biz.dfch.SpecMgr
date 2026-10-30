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

"""REQ-010/ACC-012 gap-closing tests: closed vocabulary stays canonical English in translated documents
(feat-197-i18n Phase 150, Task 150.110).

Complements the existing evidence -- ``test_i18n_all_domains.py`` (the ACC-012 unit pins and the fresh-variant
frontmatter), ``test_translate_artifact_flow.py`` (the 14-case negative matrix over nine domains) -- with what those do
not reach:

- **frontmatter ``status`` through the write tools of a variant (all eleven domains):** a translated status word is
  rejected by ``set_status(language="de")`` with the non-raising ``InvalidStatusResult`` naming the *canonical* allowed
  values, nothing is written, and a canonical value is accepted and persisted verbatim -- ``sop``'s five-value
  approval/effectivity lifecycle is exercised value by value (REQ-010 names it explicitly);
- **``classification``** is free text by design (never a closed vocabulary), so the variant keeps whatever the caller
  sets, and the EN variant is untouched by it;
- **the two domains the negative matrix skipped:** ``gol`` (its ``Priority`` number and cross-reference tags) and
  ``sysrs`` (its cross-reference tags and the fixed H1 prefix ``System Requirements Specification: ``, a schema-enforced
  English token that the Phase 130 resource and prompt now name explicitly);
- the translation texts the agent reads (``specmgr://i18n`` and the ``translate_artifact`` prompt) carry the ``sysrs``
  H1-prefix rule, since a translator who translated the whole H1 would only learn of it from the write tool's error.
"""

from __future__ import annotations

import re
import unittest

from biz.dfch.specmgr.general.models import InvalidStatusResult, ValidateResult
from biz.dfch.specmgr.general.prompts.translate_artifact import translate_artifact
from biz.dfch.specmgr.general.resources.i18n import i18n as i18n_resource
from biz.dfch.specmgr.general.tools.set_classification import set_classification
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.general.tools.update import update

from .test_i18n_all_domains import SPECS, SPECS_BY_NAME, _TempDocsMixin

#: A German word for each status the domains might be tempted to translate (none is a valid status anywhere).
_TRANSLATED_STATUS = "entwurf"

#: SOP's closed approval/effectivity lifecycle (REQ-010 names it explicitly).
_SOP_LIFECYCLE = ("draft", "review", "approved", "active", "retired")


def frontmatter_of(path) -> str:
    """The raw YAML frontmatter block of the document at ``path``."""
    result = path.read_text(encoding="utf-8").split("---\n")[1]
    return result


class TestFrontmatterStatusStaysCanonicalInAVariant(_TempDocsMixin):
    """REQ-010: ``status`` is closed vocabulary in every language -- the write tools of a variant enforce it."""

    def test_a_translated_status_is_rejected_and_nothing_is_written_for_every_domain(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, en_file, de_file = self.seed(spec)
                before_de, before_en = de_file.read_bytes(), en_file.read_bytes()

                result = set_status(type=spec.d, id=doc_id, status=_TRANSLATED_STATUS, language="de")

                self.assertIsInstance(result, InvalidStatusResult)
                self.assertFalse(result.valid)
                self.assertNotIn(_TRANSLATED_STATUS, result.allowed_values)
                self.assertTrue(all(value == value.lower() and value.isascii() for value in result.allowed_values))
                self.assertIn(spec.status, result.allowed_values)
                self.assertEqual(de_file.read_bytes(), before_de)
                self.assertEqual(en_file.read_bytes(), before_en)

    def test_a_canonical_status_is_accepted_and_persisted_verbatim_for_every_domain(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, en_file, de_file = self.seed(spec)
                rejected = set_status(type=spec.d, id=doc_id, status=_TRANSLATED_STATUS, language="de")
                assert isinstance(rejected, InvalidStatusResult)
                target = next(value for value in rejected.allowed_values if value != spec.status)
                en_before = en_file.read_bytes()

                result = set_status(type=spec.d, id=doc_id, status=target, language="de")

                self.assertEqual(result.status, target)
                self.assertIn(f"status: {target}", frontmatter_of(de_file))
                self.assertEqual(spec.fn("get")(doc_id, language="de").frontmatter.status, target)
                self.assertEqual(en_file.read_bytes(), en_before)
                self.assertEqual(spec.fn("get")(doc_id).frontmatter.status, spec.status)

    def test_every_value_of_the_sop_lifecycle_is_accepted_in_a_variant_and_no_translation_is(self):
        spec = SPECS_BY_NAME["sop"]
        doc_id, _en_file, de_file = self.seed(spec)
        rejected = set_status(type="sop", id=doc_id, status="genehmigt", language="de")
        self.assertIsInstance(rejected, InvalidStatusResult)
        self.assertEqual(set(rejected.allowed_values), set(_SOP_LIFECYCLE))

        for value in _SOP_LIFECYCLE:
            with self.subTest(status=value):
                result = set_status(type="sop", id=doc_id, status=value, language="de")

                self.assertEqual(result.status, value)
                self.assertIn(f"status: {value}", frontmatter_of(de_file))

    def test_classification_is_free_text_in_a_variant_and_never_touches_en(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, en_file, de_file = self.seed(spec)
                en_before = en_file.read_bytes()

                result = set_classification(type=spec.d, id=doc_id, classification="Vertraulich", language="de")

                self.assertEqual(result.classification, "Vertraulich")
                self.assertIn("classification: Vertraulich", frontmatter_of(de_file))
                self.assertEqual(en_file.read_bytes(), en_before)
                self.assertIsNone(spec.fn("get")(doc_id).frontmatter.classification)


class TestTheDomainsTheNegativeMatrixSkipped(_TempDocsMixin):
    """``gol`` and ``sysrs``: their schema-enforced tokens are rejected when translated, on create and on update."""

    def _assert_rejected_everywhere(self, domain: str, label: str, transform) -> None:
        spec = SPECS_BY_NAME[domain]
        spec.reset_cache()
        created = spec.fn("create")(spec.en_body())
        assert not isinstance(created, ValidateResult), created
        good = spec.de_body()
        bad = transform(good)
        self.assertNotEqual(bad, good, f"the transform for {label!r} changed nothing")

        rejected = spec.fn("create")(bad, language="de", id=created.id)

        self.assertIsInstance(rejected, ValidateResult, label)
        self.assertFalse(rejected.valid)
        self.assertEqual(len(rejected.errors), 1)
        self.assertFalse(spec.base_dir("de").exists() and list(spec.base_dir("de").glob("*.md")))

        accepted = spec.fn("create")(good, language="de", id=created.id)
        self.assertNotIsInstance(accepted, ValidateResult, accepted)
        de_file = next(spec.base_dir("de").glob("*.md"))
        before = de_file.read_bytes()

        refused = update(type=domain, id=created.id, content=bad, language="de")

        self.assertIsInstance(refused, ValidateResult, label)
        self.assertFalse(refused.valid)
        self.assertEqual(de_file.read_bytes(), before)

    def test_gol_priority_number_is_schema_enforced(self):
        self._assert_rejected_everywhere("gol", "Priority", lambda b: re.sub(r"(?m)^50$", "fünfzig", b))

    def test_gol_cross_reference_tag_is_schema_enforced(self):
        self._assert_rejected_everywhere("gol", "REQ tag", lambda b: b.replace("- REQ ", "- ANF ", 1))

    def test_sysrs_cross_reference_tag_is_schema_enforced(self):
        self._assert_rejected_everywhere("sysrs", "GOL tag", lambda b: b.replace("- GOL ", "- ZIEL ", 1))

    def test_sysrs_h1_prefix_is_schema_enforced(self):
        self._assert_rejected_everywhere(
            "sysrs",
            "H1 prefix",
            lambda b: b.replace("# System Requirements Specification: ", "# Systemanforderungsspezifikation: ", 1),
        )

    def test_sysrs_title_after_the_prefix_is_translatable(self):
        """The prefix is fixed, the title after it is prose: translating only the title is accepted."""
        spec = SPECS_BY_NAME["sysrs"]
        created = spec.fn("create")(spec.en_body())
        body = re.sub(
            r"(?m)^(# System Requirements Specification: ).*$", r"\1Deutscher Systemtitel", spec.de_body(), count=1
        )

        variant = spec.fn("create")(body, language="de", id=created.id)

        self.assertNotIsInstance(variant, ValidateResult, variant)
        self.assertEqual(spec.fn("get")(created.id, language="de").frontmatter.id, created.id)


class TestTheTranslationTextsNameTheSysrsPrefix(unittest.TestCase):
    """The agent-facing texts must not tell a translator to translate the whole ``sysrs`` H1."""

    _PREFIX = "System Requirements Specification: "

    def test_the_i18n_resource_names_the_prefix_as_schema_enforced(self):
        text = i18n_resource()

        self.assertIn(self._PREFIX, text)
        row = next(line for line in text.splitlines() if line.startswith("| `sysrs` |"))
        self.assertIn(self._PREFIX, row.split("|")[2], "the prefix belongs to the schema-enforced column")
        self.assertIn("`sysrs`, whose H1 must keep the prefix", " ".join(text.split()))

    def test_the_translate_prompt_names_the_prefix_in_its_never_translate_list(self):
        rendered = translate_artifact("sysrs", "0e15c5de-4ac9-4279-aa75-53249a3e43e4", "de")

        self.assertIn(self._PREFIX, rendered)
        self.assertIn("`sysrs`: the H1 prefix", rendered)


if __name__ == "__main__":
    unittest.main()
