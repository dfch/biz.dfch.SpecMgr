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

"""Parametrized i18n tests over all eleven language-aware domains (feat-197-i18n Phase 125).

Phase 125 rolled the ``dec`` pilot's read/write ``language`` plumbing out to the remaining ten i18n-eligible
domains (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``sop``/``vcr``/``sysrs``). The ``dec`` pilot keeps its
own deep test modules (``tests/dec/tools/test_i18n_language.py``/``test_i18n_write.py``); this module drives *every*
language-aware domain, ``dec`` included, through the same behaviors, so a regression in any one domain's port is caught
here at a pragmatic depth:

- **ACC-001 x11** -- ``create_<d>(language=...)``/``get_<d>(language=...)`` resolve a non-EN variant to
  ``docs/{type}/{language}/<EN basename>`` while EN stays at ``docs/{type}/``;
- **ACC-003/REQ-003** -- the variant carries the shared id;
- **ACC-004/ACC-011 x11** -- a German-translated version of each domain's packaged *example* and *template* documents
  (derived from ``de.json`` by reverse-mapping the fixed-text headings) parses via ``parse_<d>(..., language="de")`` to
  a document structurally equal to the EN parse -- the evidence that ``de.json`` covers every domain's heading set;
- **ACC-012 unit pin** -- every data-carrying heading (the ``de.json``-less tokens) and every frontmatter value stays
  canonical in the translated text;
- **ACC-006 generalized** -- ``update``/``edit``/``set_status``/``set_classification``/``delete`` with ``language="de"``
  act on the DE variant only and leave the EN bytes untouched;
- **ACC-007** -- ``list_<d>(language=...)`` lists exactly one language's variants;
- **ACC-013** -- a path-injection-shaped (or table-less) ``language`` is rejected before any filesystem access, for
  ``get_<d>``/``list_<d>``/``create_<d>`` of every domain;
- the ``ParseFailureResult``/failed-list-row byte-identity for a broken DE variant;
- ``create_<d>`` variant-mode contract (id required/forbidden, EN source required, never overwrite, ``status``);
- the per-language lock key and the path-derived language of the ``parse_<d>`` tool;
- **Task 125.120 ``DocCache``** -- EN and DE of one id have independent cache entries, interleaved tool reads/writes
  never leak content, a write to one language leaves the other's cache entry object identical, deleting DE leaves EN
  intact (no ``DocCache`` code change was needed);
- **Task 125.120 regex-locked prose** -- ``prb``'s ``problem_statement`` is the one pattern-locked English field and is
  EXEMPT (stays canonical English in every language): a German variant with the canonical English sentence parses, a
  translated sentence is rejected by the *unchanged* validator.
"""

from __future__ import annotations

import importlib
import inspect
import re
import tempfile
import unittest
from collections.abc import Callable
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest import mock

from biz.dfch.specmgr.general.models import ParseFailureResult, ValidateResult
from biz.dfch.specmgr.general.models.heading_table import load_heading_table
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._domains import WHOLE_BODY_DOMAINS
from biz.dfch.specmgr.general.tools._language_guard import LANGUAGE_AWARE_DOMAINS
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text
from biz.dfch.specmgr.general.tools.delete import delete
from biz.dfch.specmgr.general.tools.edit import edit
from biz.dfch.specmgr.general.tools.set_classification import set_classification
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.general.tools.update import update

_MISSING_UUID = "00000000-0000-0000-0000-000000000000"

#: The domains whose models live in a ``v2`` package; every other domain is ``v1``.
_V2_DOMAINS = frozenset({"uc", "qa"})

#: The status a fresh ``create_<d>`` assigns, per domain (``rsk`` is born ``open``, every other domain ``draft``).
_CREATE_STATUS = {d: ("open" if d == "rsk" else "draft") for d in LANGUAGE_AWARE_DOMAINS}


def _heading_re() -> re.Pattern[str]:
    return re.compile(r"^(#{1,6}) (.*)$")


def _strip_frontmatter(text: str) -> str:
    """Return the body of a packaged example/template (everything after the YAML frontmatter block)."""
    assert text.startswith("---\n")
    result = text.split("\n---\n", 1)[1].lstrip("\n")
    return result


def translate_to_de(text: str) -> str:
    """Translate every fixed-text heading of ``text`` into German via the packaged ``de.json`` (fence-aware).

    Data-carrying headings (``### Option 1: ...``, ``### Step N: ...``, ``### AC-001 (Test): ...``,
    ``### Probability 4``, timestamp-led update entries ...) hold no table entry and stay byte-identical -- exactly
    the REQ-010 contract. Prose and frontmatter are never touched.
    """
    reverse = {canonical: translated for translated, canonical in load_heading_table("de").items()}
    pattern = _heading_re()
    out: list[str] = []
    in_fence = False
    for line in text.split("\n"):
        if re.match(r"^(```|~~~)", line):
            in_fence = not in_fence
        match = pattern.match(line)
        if match and not in_fence and match.group(2) in reverse:
            out.append(f"{match.group(1)} {reverse[match.group(2)]}")
        else:
            out.append(line)
    result = "\n".join(out)
    return result


@dataclass(frozen=True)
class DomainSpec:
    """Everything the parametrized tests need to drive one language-aware domain generically."""

    d: str
    status: str

    def module(self, dotted: str) -> ModuleType:
        return importlib.import_module(f"biz.dfch.specmgr.{self.d}.{dotted}")

    def models(self) -> ModuleType:
        return self.module(f"models.{'v2' if self.d in _V2_DOMAINS else 'v1'}")

    def fn(self, tool: str) -> Callable[..., Any]:
        """The ``<tool>_<d>`` tool function (``get``/``list``/``create``/``parse``)."""
        return getattr(self.module(f"tools.{tool}_{self.d}"), f"{tool}_{self.d}")

    def parse(self) -> Callable[..., Any]:
        return getattr(self.models(), f"parse_{self.d}")

    def reset_cache(self) -> None:
        getattr(self.module("tools._cache"), f"reset_{self.d}_cache")()

    def read(self, path: Path) -> Any:
        return getattr(self.module("tools._cache"), f"read_{self.d}")(path)

    def base_dir(self, language: str | None = None) -> Path:
        return getattr(self.module("tools._paths"), f"{self.d}_base_dir")(language)

    def iter_paths(self, language: str | None = None) -> list[Path]:
        return list(getattr(self.module("tools._paths"), f"iter_{self.d}_paths")(language))

    def not_found_error(self) -> type[Exception]:
        for name in dir(self.module("tools._paths")):
            if name.endswith("NotFoundError") and name.lower().startswith(self.d):
                return getattr(self.module("tools._paths"), name)
        raise AssertionError(f"no NotFoundError class found for {self.d}")

    def lock_key(self, id_: str, language: str | None = None) -> str:
        return getattr(self.module("tools._lock"), f"{self.d}_lock_key")(id_, language)

    def example_text(self) -> str:
        return read_packaged_text(self.d, "example")

    def template_text(self) -> str:
        return read_packaged_text(self.d, "template")

    def en_body(self) -> str:
        """The EN body the tool-driven tests create: the packaged template's body (every section present, and much
        cheaper to parse than the full example -- the example is exercised by the ACC-004/ACC-011 parse tests)."""
        return _strip_frontmatter(self.template_text())

    def de_body(self) -> str:
        return translate_to_de(self.en_body())


SPECS = tuple(DomainSpec(d, _CREATE_STATUS[d]) for d in LANGUAGE_AWARE_DOMAINS)


class _TempDocsMixin(unittest.TestCase):
    """Isolated docs root + cleared caches for every spec'd domain."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        for spec in SPECS:
            spec.reset_cache()

    def seed(self, spec: DomainSpec) -> tuple[str, Path, Path]:
        """Create the EN document and its DE variant through the tools; return (id, EN file, DE file)."""
        created = spec.fn("create")(spec.en_body())
        assert not isinstance(created, ValidateResult), created
        assert created.id is not None
        variant = spec.fn("create")(spec.de_body(), language="de", id=created.id)
        assert not isinstance(variant, ValidateResult), variant
        en_file = next(spec.base_dir().glob("*.md"))
        de_file = spec.base_dir("de") / en_file.name
        return created.id, en_file, de_file


class TestEveryAwareDomainIsCovered(unittest.TestCase):
    """The parametrization table is exactly the eleven language-aware domains."""

    def test_specs_cover_exactly_the_language_aware_domains(self):
        self.assertEqual(tuple(s.d for s in SPECS), LANGUAGE_AWARE_DOMAINS)
        self.assertEqual(len(SPECS), 11)
        self.assertEqual(set(LANGUAGE_AWARE_DOMAINS), set(WHOLE_BODY_DOMAINS) - {"feat"})


class TestAcc001PathResolutionAllDomains(_TempDocsMixin):
    """ACC-001/ACC-003: a variant lives at docs/{type}/{language}/<EN basename> with the shared id; EN is unchanged."""

    def test_create_and_get_resolve_the_variant_under_the_language_subfolder(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                created = spec.fn("create")(spec.en_body())
                assert not isinstance(created, ValidateResult), created
                en_files = list((self.docs_root / spec.d).glob("*.md"))
                self.assertEqual(len(en_files), 1)
                en_file = en_files[0]
                en_bytes_before = en_file.read_bytes()

                variant = spec.fn("create")(spec.de_body(), language="de", id=created.id)
                assert not isinstance(variant, ValidateResult), variant

                de_file = self.docs_root / spec.d / "de" / en_file.name
                self.assertTrue(de_file.is_file(), de_file)
                self.assertEqual(en_file.read_bytes(), en_bytes_before)
                # ACC-003: the shared id
                self.assertEqual(variant.id, created.id)
                self.assertIn(f"id: {created.id}", de_file.read_text(encoding="utf-8").split("---\n")[1])
                # fresh frontmatter at the domain's own create status
                self.assertEqual(variant.status, spec.status)
                self.assertEqual(variant.type, spec.d)
                # the language is encoded by the location only: no `language` frontmatter field
                self.assertNotIn("language:", de_file.read_text(encoding="utf-8").split("---\n")[1])
                # reads
                en_doc = spec.fn("get")(created.id)
                de_doc = spec.fn("get")(created.id, language="de")
                self.assertEqual(en_doc.frontmatter.id, de_doc.frontmatter.id)
                self.assertEqual(de_doc.body, en_doc.body)  # same canonical model (de.json -> canonical keys)
                self.assertEqual(Path(spec.fn("list")(language="de").results[0].path), de_file.resolve())
                self.assertEqual(Path(spec.fn("list")().results[0].path), en_file.resolve())

    def test_raw_read_of_a_variant_is_the_on_disk_translation_verbatim(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, _en_file, de_file = self.seed(spec)
                raw_de = spec.fn("get")(doc_id, raw=True, language="de")
                self.assertEqual(raw_de.rstrip("\n"), spec.de_body().rstrip("\n"))  # byte-for-byte what was written
                self.assertIn(raw_de.rstrip("\n"), de_file.read_text(encoding="utf-8"))
                self.assertNotEqual(raw_de, spec.fn("get")(doc_id, raw=True))

    def test_omitted_and_explicit_en_language_are_the_same_en_document(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                doc_id, _en_file, _de_file = self.seed(spec)
                self.assertEqual(spec.fn("get")(doc_id), spec.fn("get")(doc_id, language="en"))
                self.assertEqual(spec.fn("list")(), spec.fn("list")(language="en"))


class TestAcc004Acc011HeadingTableCoversEveryDomain(unittest.TestCase):
    """ACC-004/ACC-011 evidence per domain: the translated example/template parse to the EN document."""

    def test_translated_example_parses_to_the_en_document(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                en_text = spec.example_text()
                de_text = translate_to_de(en_text)
                self.assertNotEqual(de_text, en_text, "nothing was translated -- de.json covers no heading?")
                self.assertEqual(spec.parse()(de_text, language="de"), spec.parse()(en_text))

    def test_translated_template_parses_to_the_en_document(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                en_text = spec.template_text()
                de_text = translate_to_de(en_text)
                self.assertEqual(spec.parse()(de_text, language="de"), spec.parse()(en_text))

    def test_untranslated_headings_in_a_translated_document_still_fail_as_ordinary_alias_mismatches(self):
        """An EN-only text parsed as 'de' still works (EN headings are canonical, the table maps nothing for them),
        but a translated heading in an EN parse is an ordinary structural error (the table is opt-in)."""
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                en_text = spec.example_text()
                self.assertEqual(spec.parse()(en_text, language="de"), spec.parse()(en_text))
                with self.assertRaises((AssertionError, ValueError)):
                    spec.parse()(translate_to_de(en_text))


class TestAcc012ClosedVocabularyStaysCanonical(_TempDocsMixin):
    """ACC-012 unit pin: schema-constant tokens never translate."""

    def test_only_table_headings_change_and_every_other_line_is_byte_identical(self):
        table = load_heading_table("de")
        canonical_fixed = set(table.values())
        pattern = _heading_re()
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                en_lines = spec.en_body().split("\n")
                de_lines = spec.de_body().split("\n")
                self.assertEqual(len(en_lines), len(de_lines))
                for en_line, de_line in zip(en_lines, de_lines):
                    match = pattern.match(en_line)
                    if match and match.group(2) in canonical_fixed:
                        continue  # a fixed-text heading: translated
                    self.assertEqual(
                        en_line, de_line
                    )  # prose, frontmatter-free body, data-carrying headings: untouched

    def test_domain_specific_tokens_stay_in_the_file(self):
        rsk_de = SPECS_BY_NAME["rsk"].de_body()
        self.assertRegex(rsk_de, r"(?m)^### Probability [1-5]$")
        self.assertRegex(rsk_de, r"(?m)^### Impact [1-5]$")
        vcr_de = SPECS_BY_NAME["vcr"].de_body()
        self.assertRegex(vcr_de, r"(?m)^### AC-\d{3} \((Demonstration|Test|Analysis|Inspection|Special)\): ")
        sop_de = SPECS_BY_NAME["sop"].de_body()
        self.assertRegex(sop_de, r"(?m)^### Step \d+: ")
        dec_de = SPECS_BY_NAME["dec"].de_body()
        self.assertRegex(dec_de, r"(?m)^### Option \d+: ")

    def test_variant_frontmatter_values_are_canonical_english(self):
        """status/type/version of a fresh variant are the canonical closed-vocabulary values (REQ-010)."""
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, _en_file, de_file = self.seed(spec)
                frontmatter_text = de_file.read_text(encoding="utf-8").split("---\n")[1]
                self.assertIn(f"status: {spec.status}", frontmatter_text)
                self.assertIn(f"type: {spec.d}", frontmatter_text)
                self.assertIn("version: 1.0.0", frontmatter_text)
                self.assertIsNotNone(doc_id)


class TestAcc007ListAllDomains(_TempDocsMixin):
    """ACC-007: list_<d>(language=...) lists exactly that language's variants; the shared id is never duplicated."""

    def test_each_language_lists_exactly_its_own_documents(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, en_file, de_file = self.seed(spec)
                en_rows = spec.fn("list")().results
                de_rows = spec.fn("list")(language="de").results
                self.assertEqual([r.id for r in en_rows], [doc_id])
                self.assertEqual([r.id for r in de_rows], [doc_id])
                self.assertEqual(en_rows[0].ref, de_rows[0].ref)  # same basename stem
                self.assertEqual(Path(en_rows[0].path), en_file.resolve())
                self.assertEqual(Path(de_rows[0].path), de_file.resolve())
                self.assertEqual(spec.fn("list")(language="de").total, 1)
                self.assertEqual(spec.fn("list")().total, 1)

    def test_missing_language_directory_lists_empty(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.fn("create")(spec.en_body())
                result = spec.fn("list")(language="de")
                self.assertEqual(result.total, 0)
                self.assertEqual(result.results, [])

    def test_the_flat_scan_never_descends_into_language_subfolders(self):
        """ACC-014 unit pin per domain: iter_<d>_paths() is non-recursive."""
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                _doc_id, en_file, de_file = self.seed(spec)
                self.assertEqual(spec.iter_paths(), [en_file])
                self.assertEqual(spec.iter_paths("de"), [de_file])


class TestAcc006WriteToolsAllDomains(_TempDocsMixin):
    """ACC-006 generalized: each of the five generic write tools acts on the DE variant only."""

    def _seed(self, spec: DomainSpec) -> tuple[str, Path, Path]:
        spec.reset_cache()
        return self.seed(spec)

    def test_update_edit_set_status_set_classification_leave_en_untouched(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                doc_id, en_file, de_file = self._seed(spec)
                en_bytes = en_file.read_bytes()
                de_before = de_file.read_bytes()
                title_line = spec.de_body().split("\n", 1)[0]

                # update (whole body) -- retitles the DE variant
                new_body = spec.de_body().replace(title_line, f"{title_line} (v2)", 1)
                result = update(id=doc_id, type=spec.d, content=new_body, language="de")
                self.assertFalse(isinstance(result, (ParseFailureResult, ValidateResult)), result)
                self.assertEqual(en_file.read_bytes(), en_bytes)
                self.assertIn("(v2)", de_file.read_text(encoding="utf-8"))

                # edit -- surgical replacement in the DE variant
                result = edit(id=doc_id, type=spec.d, old_str="(v2)", new_str="(v3)", language="de")
                self.assertFalse(isinstance(result, (ParseFailureResult, ValidateResult)), result)
                self.assertEqual(en_file.read_bytes(), en_bytes)
                self.assertIn("(v3)", de_file.read_text(encoding="utf-8"))
                self.assertNotIn("(v2)", de_file.read_text(encoding="utf-8"))

                # set_status -- to another allowed value (the variant's own status is its create status)
                allowed = sorted(_allowed_statuses(spec.d) - {spec.status})
                result = set_status(id=doc_id, type=spec.d, status=allowed[0], language="de")
                self.assertEqual(result.status, allowed[0])
                self.assertEqual(en_file.read_bytes(), en_bytes)
                self.assertIn(f"status: {allowed[0]}", de_file.read_text(encoding="utf-8").split("---\n")[1])

                # set_classification
                result = set_classification(id=doc_id, type=spec.d, classification="internal", language="de")
                self.assertEqual(result.classification, "internal")
                self.assertEqual(en_file.read_bytes(), en_bytes)
                self.assertIn("classification: internal", de_file.read_text(encoding="utf-8").split("---\n")[1])

                self.assertNotEqual(de_file.read_bytes(), de_before)

    def test_delete_removes_the_variant_only_and_en_stays_readable(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                doc_id, en_file, de_file = self._seed(spec)
                en_bytes = en_file.read_bytes()
                spec.fn("get")(doc_id, language="de")  # warm both cache entries
                spec.fn("get")(doc_id)

                deleted = delete(id=doc_id, type=spec.d, language="de")

                self.assertEqual(Path(deleted), de_file.resolve())
                self.assertFalse(de_file.exists())
                self.assertEqual(en_file.read_bytes(), en_bytes)
                self.assertEqual(spec.fn("get")(doc_id).frontmatter.id, doc_id)
                with self.assertRaises(spec.not_found_error()):
                    spec.fn("get")(doc_id, language="de")

    def test_default_language_tools_still_act_on_en_only(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                doc_id, en_file, de_file = self._seed(spec)
                de_bytes = de_file.read_bytes()
                set_classification(id=doc_id, type=spec.d, classification="public")
                self.assertIn("classification: public", en_file.read_text(encoding="utf-8").split("---\n")[1])
                self.assertEqual(de_file.read_bytes(), de_bytes)

    def test_write_to_an_absent_de_variant_raises_not_found_even_if_en_exists(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                created = spec.fn("create")(spec.en_body())
                with self.assertRaises(spec.not_found_error()):
                    set_classification(id=created.id, type=spec.d, classification="x", language="de")
                with self.assertRaises(spec.not_found_error()):
                    delete(id=created.id, type=spec.d, language="de")

    def test_translated_headings_are_accepted_by_update_but_not_en_validation(self):
        """The write side validates through the language's table: a DE body is valid for language='de' only."""
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                doc_id, _en_file, _de_file = self._seed(spec)
                rejected = update(id=doc_id, type=spec.d, content=spec.de_body())  # EN: translated headings
                self.assertIsInstance(rejected, ValidateResult)
                self.assertFalse(rejected.valid)


class TestAcc013GuardBeforeFilesystemAllDomains(_TempDocsMixin):
    """ACC-013 + guard-before-IO ordering: bad/unusable language is rejected before any filesystem access."""

    _BAD = ("", "d", "de3", "DE", "de x", "../../etc", "de/x", "/abs")

    def _trap(self, spec: DomainSpec) -> list[Any]:
        """Patchers that fail the test if any first-filesystem-access seam of get/list/create is reached."""
        boom = AssertionError("must not run: language guard comes before any filesystem access")
        targets = [
            f"biz.dfch.specmgr.{spec.d}.tools.get_{spec.d}.load_by_id",
            f"biz.dfch.specmgr.{spec.d}.tools.list_{spec.d}.iter_{spec.d}_paths",
            f"biz.dfch.specmgr.{spec.d}.tools.create_{spec.d}.find_{spec.d}_path",
            f"biz.dfch.specmgr.{spec.d}.tools.create_{spec.d}.ensure_{spec.d}_base_dir",
            f"biz.dfch.specmgr.{spec.d}.tools.create_{spec.d}.write_{spec.d}_file",
        ]
        return [mock.patch(t, side_effect=boom) for t in targets]

    def test_bad_language_is_rejected_by_get_list_create(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                with ExitStack() as stack:
                    for patcher in self._trap(spec):
                        stack.enter_context(patcher)
                    for value in self._BAD:
                        with self.subTest(domain=spec.d, value=value):
                            with self.assertRaises(ValueError) as ctx:
                                spec.fn("get")(_MISSING_UUID, language=value)
                            self.assertIn(repr(value), str(ctx.exception))
                            with self.assertRaises(ValueError) as ctx:
                                spec.fn("list")(language=value)
                            self.assertIn(repr(value), str(ctx.exception))
                            with self.assertRaises(ValueError) as ctx:
                                spec.fn("create")(spec.en_body(), language=value, id=_MISSING_UUID)
                            self.assertIn(repr(value), str(ctx.exception))
                self.assertFalse((self.docs_root / spec.d).exists(), "a rejected call must not create anything")

    def test_unusable_language_is_rejected_with_the_table_error(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                with ExitStack() as stack:
                    for patcher in self._trap(spec):
                        stack.enter_context(patcher)
                    for call in (
                        lambda: spec.fn("get")(_MISSING_UUID, language="fr"),
                        lambda: spec.fn("list")(language="fr"),
                        lambda: spec.fn("create")(spec.en_body(), language="fr", id=_MISSING_UUID),
                    ):
                        with self.assertRaises(ValueError) as ctx:
                            call()
                        self.assertIn("'fr'", str(ctx.exception))
                        self.assertIn("no heading-mapping table", str(ctx.exception))
                self.assertFalse((self.docs_root / spec.d).exists())

    def test_bad_language_wins_over_an_absent_id(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                with self.assertRaises(ValueError) as ctx:
                    spec.fn("get")(_MISSING_UUID, language="../../etc")
                self.assertIn("'../../etc'", str(ctx.exception))

    def test_generic_tools_reject_a_bad_language_for_every_aware_domain(self):
        for spec in SPECS:
            for name, call in (
                ("update", lambda s=spec: update(id=_MISSING_UUID, type=s.d, content="# T\n", language="../../etc")),
                ("edit", lambda s=spec: edit(id=_MISSING_UUID, type=s.d, old_str="a", new_str="b", language="de/x")),
                ("set_status", lambda s=spec: set_status(id=_MISSING_UUID, type=s.d, status="x", language="DE")),
                (
                    "set_classification",
                    lambda s=spec: set_classification(id=_MISSING_UUID, type=s.d, classification="x", language=""),
                ),
                ("delete", lambda s=spec: delete(id=_MISSING_UUID, type=s.d, language="d")),
            ):
                with self.subTest(domain=spec.d, tool=name):
                    with self.assertRaises(ValueError):
                        call()
            self.assertFalse((self.docs_root / spec.d).exists())


class TestParseFailureByteIdentityAllDomains(_TempDocsMixin):
    """get_<d>'s ParseFailureResult.error is byte-identical to list_<d>'s failed row for a broken DE variant."""

    def test_broken_de_variant(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, en_file, de_file = self.seed(spec)
                de_file.write_text(
                    de_file.read_text(encoding="utf-8") + "\n## BROKEN-HEADING\n\ntext\n", encoding="utf-8"
                )
                spec.reset_cache()

                failure = spec.fn("get")(doc_id, language="de")
                rows = spec.fn("list")(language="de")
                row = rows.results[0]

                self.assertIsInstance(failure, ParseFailureResult)
                self.assertEqual(failure.error, row.error)
                self.assertEqual(failure.path, row.path)
                self.assertEqual(failure.id, doc_id)
                self.assertEqual(row.title, "<failed to parse>")
                self.assertEqual(rows.error_count, 1)
                # the raw=True channel also returns the result, never a broken document's text
                self.assertIsInstance(spec.fn("get")(doc_id, raw=True, language="de"), ParseFailureResult)
                # EN is unaffected by the broken DE variant
                self.assertEqual(spec.fn("get")(doc_id).frontmatter.id, doc_id)
                self.assertEqual(spec.fn("list")().error_count, 0)


class TestCreateVariantContractAllDomains(_TempDocsMixin):
    """create_<d> variant mode: id required/forbidden, EN source required, never overwritten, per-language lock."""

    def test_id_is_required_for_a_variant_and_forbidden_for_en(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                with self.assertRaises(ValueError) as ctx:
                    spec.fn("create")(spec.de_body(), language="de")
                self.assertIn("id is required", str(ctx.exception))
                with self.assertRaises(ValueError) as ctx:
                    spec.fn("create")(spec.en_body(), id=_MISSING_UUID)
                self.assertIn("can only be given together with a non-default language", str(ctx.exception))
                with self.assertRaises(ValueError):
                    spec.fn("create")(spec.de_body(), language="de", id="../../etc")
                self.assertFalse((self.docs_root / spec.d).exists())

    def test_en_source_is_required(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                with self.assertRaises(spec.not_found_error()) as ctx:
                    spec.fn("create")(spec.de_body(), language="de", id=_MISSING_UUID)
                self.assertIn("requires its 'en' source", str(ctx.exception))
                self.assertFalse((self.docs_root / spec.d / "de").exists())

    def test_existing_variant_is_never_overwritten(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, _en_file, de_file = self.seed(spec)
                before = de_file.read_bytes()
                with self.assertRaises(FileExistsError):
                    spec.fn("create")(spec.de_body(), language="de", id=doc_id)
                self.assertEqual(de_file.read_bytes(), before)

    def test_invalid_variant_content_is_a_non_raising_validate_result_and_writes_nothing(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                created = spec.fn("create")(spec.en_body())
                # EN headings are canonical, so the *translated* body is invalid for EN but a broken body is invalid
                # for DE too.
                result = spec.fn("create")("# only a title\n", language="de", id=created.id)
                self.assertIsInstance(result, ValidateResult)
                self.assertFalse(result.valid)
                self.assertFalse((self.docs_root / spec.d / "de").exists())

    def test_en_create_is_unchanged_fresh_id_flat_file(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                created = spec.fn("create")(spec.en_body())
                files = list((self.docs_root / spec.d).glob("*.md"))
                self.assertEqual(len(files), 1)
                self.assertTrue(files[0].name.startswith(f"{spec.d}-{created.id}-"))
                self.assertEqual(created.status, spec.status)
                self.assertFalse((self.docs_root / spec.d / "de").exists())

    def test_variant_basename_is_the_en_basename_even_for_a_retitled_translation(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, en_file, de_file = self.seed(spec)
                self.assertEqual(de_file.name, en_file.name)
                self.assertTrue(de_file.is_file())

    def test_lock_keys_are_per_language(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                self.assertEqual(spec.lock_key(_MISSING_UUID), _MISSING_UUID)
                self.assertEqual(spec.lock_key(_MISSING_UUID, "en"), _MISSING_UUID)
                self.assertEqual(spec.lock_key(_MISSING_UUID, None), _MISSING_UUID)
                self.assertEqual(spec.lock_key(_MISSING_UUID, "de"), f"{_MISSING_UUID}/de")
                self.assertNotEqual(spec.lock_key(_MISSING_UUID, "de"), spec.lock_key(_MISSING_UUID, "fr"))


class TestParseToolPathDerivedLanguageAllDomains(_TempDocsMixin):
    """parse_<d> derives the language from the file position (no language parameter)."""

    def test_variant_path_applies_the_table_and_flat_path_does_not(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                _doc_id, en_file, de_file = self.seed(spec)
                self.assertNotIn("language", _params(spec.fn("parse")))
                en = spec.fn("parse")(str(en_file))
                de = spec.fn("parse")(str(de_file))
                self.assertEqual(en.body, de.body)
                # a translated body outside any language directory is parsed canonical -> a structural failure
                stray = self.docs_root / f"stray-{spec.d}.md"
                stray.write_text(de_file.read_text(encoding="utf-8"), encoding="utf-8")
                self.assertIsInstance(spec.fn("parse")(str(stray)), ValidateResult)

    def test_tableless_language_directory_raises_the_loader_error(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                fr_dir = self.docs_root / spec.d / "fr"
                fr_dir.mkdir(parents=True)
                (fr_dir / "x.md").write_text(spec.example_text(), encoding="utf-8")
                with self.assertRaises(ValueError) as ctx:
                    spec.fn("parse")(str(fr_dir / "x.md"))
                self.assertIn("no heading-mapping table", str(ctx.exception))


class TestDocCacheGeneralizationAllDomains(_TempDocsMixin):
    """Task 125.120: the DocCache path-keying analysis generalizes -- no per-domain collision, no cache code change.

    A cache *hit* is observable as "no ``parse_<d>`` call": the cache's ``parse_fn`` is only invoked on a miss, so
    counting the domain's own ``parse_<d>`` calls pins which reads were served from which path-keyed entry.
    """

    @staticmethod
    def _parse_counter(spec: DomainSpec) -> Any:
        real = getattr(spec.module("tools._cache"), f"parse_{spec.d}")
        return mock.patch(f"biz.dfch.specmgr.{spec.d}.tools._cache.parse_{spec.d}", wraps=real)

    def _seed_retitled(self, spec: DomainSpec) -> tuple[str, Path, Path, str, str]:
        """Seed EN + DE and retitle the DE variant, so the two languages' cached documents visibly differ."""
        spec.reset_cache()
        doc_id, en_file, de_file = self.seed(spec)
        de_title = spec.de_body().split("\n", 1)[0]
        result = update(
            id=doc_id,
            type=spec.d,
            content=spec.de_body().replace(de_title, f"{de_title} (DE)", 1),
            language="de",
        )
        assert not isinstance(result, (ParseFailureResult, ValidateResult)), result
        en_text = spec.read(en_file).body.text
        return doc_id, en_file, de_file, en_text, spec.read(de_file).body.text

    def test_en_and_de_are_independent_entries_and_never_leak(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                doc_id, en_file, de_file, en_text, de_text = self._seed_retitled(spec)
                self.assertNotEqual(en_text, de_text)
                self.assertTrue(de_text.endswith("(DE)"))
                with self._parse_counter(spec) as parse_calls:
                    # interleaved reads, direct and through the tools: every one a cache hit on its own path's entry
                    for _ in range(2):
                        self.assertEqual(spec.read(en_file).body.text, en_text)
                        self.assertEqual(spec.read(de_file).body.text, de_text)
                        self.assertEqual(spec.fn("get")(doc_id).body.text, en_text)
                        self.assertEqual(spec.fn("get")(doc_id, language="de").body.text, de_text)
                    self.assertEqual(parse_calls.call_count, 0)

    def test_writing_one_language_leaves_the_other_cache_entry_untouched(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                doc_id, en_file, de_file, en_text, de_text = self._seed_retitled(spec)
                with self._parse_counter(spec) as parse_calls:
                    set_classification(id=doc_id, type=spec.d, classification="internal", language="de")
                    self.assertEqual(parse_calls.call_count, 1)  # the DE write's own cache warm, nothing else
                    parse_calls.reset_mock()
                    self.assertEqual(spec.read(en_file).body.text, en_text)  # EN entry intact: a hit, no re-parse
                    self.assertIsNone(spec.read(en_file).frontmatter.classification)
                    self.assertEqual(spec.read(de_file).frontmatter.classification, "internal")
                    self.assertEqual(spec.read(de_file).body.text, de_text)
                    self.assertEqual(parse_calls.call_count, 0)

                    set_classification(id=doc_id, type=spec.d, classification="public")
                    self.assertEqual(parse_calls.call_count, 1)  # the EN write's own cache warm
                    parse_calls.reset_mock()
                    self.assertEqual(spec.read(de_file).frontmatter.classification, "internal")  # and vice versa
                    self.assertEqual(spec.read(en_file).frontmatter.classification, "public")
                    self.assertEqual(parse_calls.call_count, 0)

    def test_listing_one_language_does_not_evict_the_others(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                _doc_id, en_file, de_file, en_text, de_text = self._seed_retitled(spec)
                with self._parse_counter(spec) as parse_calls:
                    spec.fn("list")(language="de")
                    self.assertEqual(spec.read(en_file).body.text, en_text)
                    spec.fn("list")()
                    self.assertEqual(spec.read(de_file).body.text, de_text)
                    self.assertEqual(parse_calls.call_count, 0)

    def test_delete_of_de_leaves_en_cached_and_readable(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                doc_id, en_file, de_file, en_text, _de_text = self._seed_retitled(spec)
                delete(id=doc_id, type=spec.d, language="de")
                with self._parse_counter(spec) as parse_calls:
                    self.assertEqual(spec.read(en_file).body.text, en_text)
                    self.assertEqual(spec.fn("get")(doc_id).body.text, en_text)
                    self.assertEqual(parse_calls.call_count, 0)
                with self.assertRaises(FileNotFoundError):
                    spec.read(de_file)


class TestPrbProblemStatementExemption(_TempDocsMixin):
    """Task 125.120 / Task 100.150 resolution (b): ``prb``'s ``problem_statement`` stays canonical English in every
    language -- the unchanged validator accepts the English template sentence in a DE variant and rejects a
    translated one (the exemption is enforced, not silently loosened)."""

    _GERMAN_STATEMENT = (
        "Der fehlende Rollback-Schritt verursacht halb migrierte Widgets, "
        "fuer die Bereitschaftsingenieure, weil der Aufruf zur Abmeldung manchmal fehlschlaegt."
    )

    def setUp(self) -> None:
        super().setUp()
        self.spec = SPECS_BY_NAME["prb"]
        self.en_body = self.spec.en_body()
        self.statement = _lead_paragraph(self.en_body)

    def test_the_canonical_english_sentence_is_kept_in_a_german_variant_and_validates(self):
        de_body = self.spec.de_body()
        self.assertIn(self.statement, de_body)  # the translator-equivalent step left it untouched
        document = self.spec.parse()(
            f"---\nid: {_MISSING_UUID}\ntype: prb\nstatus: draft\ncreated: '2026-01-01T00:00:00.000Z'\n"
            f"updated: '2026-01-01T00:00:00.000Z'\nversion: 1.0.0\n---\n{de_body}",
            language="de",
        )
        self.assertEqual(document.body.problem_statement.text, " ".join(self.statement.split()))

    def test_a_german_variant_with_the_english_sentence_can_be_created(self):
        created = self.spec.fn("create")(self.en_body)
        variant = self.spec.fn("create")(self.spec.de_body(), language="de", id=created.id)
        self.assertNotIsInstance(variant, ValidateResult)
        self.assertEqual(variant.id, created.id)

    def test_a_translated_problem_statement_is_rejected_by_the_unchanged_validator(self):
        created = self.spec.fn("create")(self.en_body)
        translated = self.spec.de_body().replace(self.statement, self._GERMAN_STATEMENT, 1)
        self.assertIn(self._GERMAN_STATEMENT, translated)

        result = self.spec.fn("create")(translated, language="de", id=created.id)

        self.assertIsInstance(result, ValidateResult)
        self.assertFalse(result.valid)
        self.assertIn("problem_statement must match the template", result.errors[0].message)
        self.assertFalse((self.docs_root / "prb" / "de").exists())

    def test_the_same_translated_sentence_is_rejected_identically_in_en_and_via_update(self):
        created = self.spec.fn("create")(self.en_body)
        variant = self.spec.fn("create")(self.spec.de_body(), language="de", id=created.id)
        translated = self.spec.de_body().replace(self.statement, self._GERMAN_STATEMENT, 1)
        result = update(id=variant.id, type="prb", content=translated, language="de")
        self.assertIsInstance(result, ValidateResult)
        self.assertIn("problem_statement must match the template", result.errors[0].message)
        # the validator itself is language-agnostic: the very same text is rejected for an EN parse of EN headings
        en_translated = self.en_body.replace(self.statement, self._GERMAN_STATEMENT, 1)
        en_result = update(id=created.id, type="prb", content=en_translated)
        self.assertIsInstance(en_result, ValidateResult)
        self.assertIn("problem_statement must match the template", en_result.errors[0].message)

    def test_no_other_domain_has_a_regex_locked_prose_field_that_a_translated_body_would_trip(self):
        """Every other domain's translated example validates unchanged (Task 100.150 inventory: 'none found')."""
        for spec in SPECS:
            if spec.d == "prb":
                continue
            with self.subTest(domain=spec.d):
                self.assertEqual(
                    spec.parse()(translate_to_de(spec.example_text()), language="de"),
                    spec.parse()(spec.example_text()),
                )


# --------------------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------------------

SPECS_BY_NAME = {s.d: s for s in SPECS}


def _lead_paragraph(body: str) -> str:
    """The prb ``problem_statement`` lead paragraph: the first non-comment paragraph after the H1."""
    blocks = [b for b in body.split("\n\n") if b.strip()]
    for block in blocks[1:]:
        if not block.startswith("<!--") and not block.startswith("#"):
            return block.rstrip("\n")
    raise AssertionError("no lead paragraph found")


def _allowed_statuses(d: str) -> set[str]:
    module = importlib.import_module("biz.dfch.specmgr.general.tools.set_status")
    result = set(module._ALLOWED_STATUSES_BY_TYPE[d])
    return result


def _params(fn: Callable[..., Any]) -> set[str]:
    return set(inspect.signature(fn).parameters)


if __name__ == "__main__":
    unittest.main()
