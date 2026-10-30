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

"""REQ-013/ACC-014: the similarity and cross-reference tools stay EN-only (feat-197-i18n Phase 150, Task 150.115).

``find_related``/``find_similar_text`` (semantic similarity) and ``list_references``/``get_reference_diagram``/
``get_reference_diagram_all`` (cross-references) must never resolve, enumerate, or index a ``docs/{type}/{language}/``
entry, and every reference or similarity hit resolves to the EN variant's path (ADR 38efdb66 item 8: a directory-layout
property of the non-recursive ``iter_doc_paths`` scan, with zero code change in those tools). These tests build a docs
tree that holds BOTH the EN documents and ``de/`` variants of the same ids -- with content *marked* so a leak is
unambiguous (a ``gamma``-only German title the deterministic fake embedding backend scores as the nearest possible
match, a German-only reference edge, German-only titles) -- and assert nothing of the variants surfaces.

Coverage: every one of the eleven i18n-eligible domains for the similarity tools and the registry-wide diagram; the
``dec``/``req``/``vcr`` source domains deeply; the ``list_references`` resolved-row path/title; a ``de/``-only document
is no resolvable source; plus the structural fact the whole property rests on -- each domain's flat scan, id lookup and
listing never see a ``de/`` file, even a hand-planted one -- so a future recursive glob fails these tests.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR
from biz.dfch.specmgr.general.models import ValidateResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR, iter_doc_paths
from biz.dfch.specmgr.general.tools.find_related import find_related
from biz.dfch.specmgr.general.tools.find_similar_text import find_similar_text
from biz.dfch.specmgr.general.tools.get_reference_diagram import get_reference_diagram
from biz.dfch.specmgr.general.tools.get_reference_diagram_all import get_reference_diagram_all
from biz.dfch.specmgr.general.tools.list_references import list_references
from biz.dfch.specmgr.gol.tools._paths import GolNotFoundError

from ._reference_graph_helpers import _reset_caches
from ._similarity_helpers import SimilarityTestCase
from .test_i18n_all_domains import SPECS, SPECS_BY_NAME, DomainSpec, translate_to_de

#: The only word the fake embedding backend scores (see ``_similarity_helpers.VOCAB``); the German variants' titles are
#: made of it, so a variant that were indexed would be the nearest possible match for a ``gamma`` query.
_MARKER = "gamma"

#: The prefix ``sysrs`` requires of its H1 (schema-enforced English, see ``general_i18n.md``).
_SYSRS_PREFIX = "System Requirements Specification: "


def retitle(body: str, title: str) -> str:
    """Return ``body`` with its first line (the H1) replaced by ``title`` (``sysrs`` keeps its mandatory prefix)."""
    lines = body.split("\n")
    assert lines[0].startswith("# "), lines[0]
    prefix = _SYSRS_PREFIX if lines[0].startswith("# " + _SYSRS_PREFIX) else ""
    lines[0] = f"# {prefix}{title}"
    result = "\n".join(lines)
    return result


def en_title(spec: DomainSpec) -> str:
    """The distinct EN title the seeded document of ``spec`` carries."""
    result = f"EN {spec.d} document"
    return result


def de_title(spec: DomainSpec) -> str:
    """The marked German title of the seeded variant of ``spec`` (whole-word ``gamma``)."""
    result = f"{_MARKER} {_MARKER} {_MARKER} DE {spec.d} document"
    return result


def seed_pair(spec: DomainSpec) -> tuple[str, Path, Path]:
    """Create the EN document and its marked ``de/`` variant for ``spec``; return ``(id, EN path, DE path)``."""
    created = spec.fn("create")(retitle(spec.en_body(), en_title(spec)))
    assert not isinstance(created, ValidateResult), created
    variant = spec.fn("create")(translate_to_de(retitle(spec.en_body(), de_title(spec))), language="de", id=created.id)
    assert not isinstance(variant, ValidateResult), variant
    en_file = next(spec.base_dir().glob(f"*{created.id}*.md"))
    de_file = spec.base_dir("de") / en_file.name
    assert de_file.is_file()
    return created.id, en_file, de_file


class _EnOnlyTestCase(SimilarityTestCase):
    """Similarity fixture (docs + feat tmp dirs, reset provider/cache) plus an ADR tmp dir and cleared doc caches."""

    def setUp(self) -> None:
        super().setUp()
        self.adr_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict(os.environ, {ADR_DIR_ENV_VAR: str(self.adr_dir)}))
        _reset_caches()
        self.addCleanup(_reset_caches)

    def seed_all(self) -> dict[str, tuple[str, Path, Path]]:
        """Seed the EN document and its marked German variant for every i18n-eligible domain."""
        result = {spec.d: seed_pair(spec) for spec in SPECS}
        return result

    def assert_flat_en_path(self, path: str | Path, domain: str) -> None:
        """Fail unless ``path`` is a document directly inside ``domain``'s own flat directory (never a subfolder)."""
        resolved = Path(path).resolve()
        self.assertEqual(resolved.parent, (self.docs_root / domain).resolve(), f"{path} is not a flat {domain} file")


class TestFindRelatedStaysEnOnly(_EnOnlyTestCase):
    """REQ-013/ACC-014 for ``find_related``."""

    def test_every_domain_source_gets_only_en_hits_and_no_variant_is_embedded(self):
        seeded = self.seed_all()
        fake = self.install_fake()
        en_paths = {en.resolve() for _id, en, _de in seeded.values()}
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                doc_id = seeded[spec.d][0]

                hits = find_related(type=spec.d, id=doc_id, top_k=100)

                self.assertEqual({Path(hit.path).resolve() for hit in hits}, en_paths - {seeded[spec.d][1].resolve()})
                for hit in hits:
                    self.assert_flat_en_path(hit.path, hit.type)
                    self.assertNotIn(_MARKER, hit.title)
                self.assertEqual(len({hit.id for hit in hits}), len(hits), "an id appeared twice (a variant leaked)")
                self.assertNotIn(doc_id, [hit.id for hit in hits])
        self.assertTrue(fake.embed_inputs, "the backend was never consulted")
        for text in fake.embed_inputs:
            self.assertNotIn(_MARKER, text, "a German variant's text reached the embedding backend")

    def test_a_variant_that_is_the_nearest_possible_match_is_still_never_returned(self):
        """``req`` source with ``gamma`` text; its own DE variant and a second DE variant carry the identical text."""
        spec = SPECS_BY_NAME["req"]
        source = spec.fn("create")(retitle(spec.en_body(), f"{_MARKER} {_MARKER} {_MARKER}"))
        other = spec.fn("create")(retitle(spec.en_body(), "alpha alpha beta"))
        for doc in (source, other):
            variant = spec.fn("create")(
                translate_to_de(retitle(spec.en_body(), f"{_MARKER} {_MARKER} {_MARKER}")), language="de", id=doc.id
            )
            assert not isinstance(variant, ValidateResult), variant
        self.install_fake()

        hits = find_related(type="req", id=source.id, top_k=100)

        self.assertEqual([hit.id for hit in hits], [other.id])
        self.assertEqual(Path(hits[0].path).parent, spec.base_dir().resolve())
        self.assertEqual(hits[0].score, 0.0)

    def test_dec_and_vcr_sources_resolve_to_the_en_variant_path(self):
        seeded = self.seed_all()
        self.install_fake()
        for domain in ("dec", "vcr"):
            with self.subTest(domain=domain):
                doc_id, en_file, _de_file = seeded[domain]
                hits = find_related(type=domain, id=doc_id, target_types=[domain, "req"], top_k=100)
                self.assertEqual([hit.type for hit in hits], ["req"])
                self.assertEqual(Path(hits[0].path).resolve(), seeded["req"][1].resolve())
                # the other direction: the req source sees exactly the one EN dec/vcr document of that domain
                back = find_related(type="req", id=seeded["req"][0], target_types=[domain])
                self.assertEqual([Path(hit.path).resolve() for hit in back], [en_file.resolve()])

    def test_a_de_only_document_is_not_a_resolvable_source(self):
        seeded = self.seed_all()
        self.install_fake()
        spec = SPECS_BY_NAME["dec"]
        orphan_id = "00000000-0000-4000-8000-0000000000d0"
        de_file = seeded["dec"][2]
        orphan = de_file.parent / f"dec-{orphan_id}-orphan.md"
        orphan.write_text(de_file.read_text(encoding="utf-8").replace(seeded["dec"][0], orphan_id), encoding="utf-8")

        with self.assertRaises(Exception) as context:
            find_related(type="dec", id=orphan_id)

        self.assertIs(type(context.exception), spec.not_found_error())


class TestFindSimilarTextStaysEnOnly(_EnOnlyTestCase):
    """REQ-013/ACC-014 for ``find_similar_text``."""

    def test_a_query_matching_the_german_variants_never_returns_them(self):
        seeded = self.seed_all()
        fake = self.install_fake()
        en_paths = {en.resolve() for _id, en, _de in seeded.values()}

        hits = find_similar_text(query=f"{_MARKER} {_MARKER} {_MARKER}", top_k=100)

        self.assertEqual({Path(hit.path).resolve() for hit in hits}, en_paths)
        self.assertEqual(len(hits), len(SPECS))
        for hit in hits:
            self.assert_flat_en_path(hit.path, hit.type)
            self.assertNotIn(_MARKER, hit.title)
            self.assertEqual(hit.score, 0.0)  # the EN documents carry none of the query's words
        for text in fake.embed_inputs:
            self.assertNotIn(_MARKER, text)
        self.assertEqual(fake.embed_query_inputs, [f"{_MARKER} {_MARKER} {_MARKER}"])

    def test_per_domain_restriction_never_reaches_into_the_language_folder(self):
        seeded = self.seed_all()
        self.install_fake()
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                hits = find_similar_text(query=_MARKER, target_types=[spec.d])
                self.assertEqual([Path(hit.path).resolve() for hit in hits], [seeded[spec.d][1].resolve()])
                self.assertEqual([hit.id for hit in hits], [seeded[spec.d][0]])


def _gol_body(spec: DomainSpec, title: str, *references: tuple[str, str]) -> str:
    """The ``gol`` template body with H1 ``title`` whose first ``Requirements`` bullet is replaced by ``references``."""
    placeholder = "- REQ 00000000-0000-4000-8000-000000000001: title of the related requirement"
    body = retitle(spec.en_body(), title)
    assert placeholder in body
    bullets = "\n".join(f"- REQ {doc_id}: {text}" for doc_id, text in references)
    result = body.replace(placeholder, bullets)
    return result


class _ReferenceFixtureTestCase(_EnOnlyTestCase):
    """``gol`` G (EN + DE) -> ``req`` B (EN + DE); the DE variant of G additionally references ``req`` C (EN only)."""

    def setUp(self) -> None:
        super().setUp()
        req = SPECS_BY_NAME["req"]
        gol = SPECS_BY_NAME["gol"]
        self.req_b = req.fn("create")(retitle(req.en_body(), "Target EN Requirement"))
        req.fn("create")(
            translate_to_de(retitle(req.en_body(), "Ziel DE Anforderung")), language="de", id=self.req_b.id
        )
        self.req_c = req.fn("create")(retitle(req.en_body(), "Other EN Requirement"))
        self.gol_g = gol.fn("create")(_gol_body(gol, "Source EN Goal", (self.req_b.id, "Target EN Requirement")))
        variant = gol.fn("create")(
            translate_to_de(
                _gol_body(
                    gol,
                    "Quelle DE Ziel",
                    (self.req_b.id, "Ziel DE Anforderung"),
                    (self.req_c.id, "Nur im deutschen Ziel"),
                )
            ),
            language="de",
            id=self.gol_g.id,
        )
        assert not isinstance(variant, ValidateResult), variant
        self.req_b_en = next(req.base_dir().glob(f"*{self.req_b.id}*.md")).resolve()
        self.gol_de = next(gol.base_dir("de").glob("*.md"))


class TestListReferencesStaysEnOnly(_ReferenceFixtureTestCase):
    """REQ-013/ACC-014 for ``list_references``."""

    def test_a_reference_resolves_to_the_en_variant_path_and_title(self):
        rows = [row for row in list_references(type="gol", id=self.gol_g.id).results if row.type == "req"]

        self.assertEqual([row.id for row in rows], [self.req_b.id])
        self.assertEqual(Path(rows[0].path).resolve(), self.req_b_en)
        self.assertEqual(rows[0].title, "Target EN Requirement")
        self.assertIsNone(rows[0].error)
        self.assertNotIn("/de/", Path(rows[0].path).as_posix())

    def test_the_references_of_the_german_variant_are_not_reported(self):
        """The DE variant of the goal also references C; the EN source's references never include it."""
        rows = list_references(type="gol", id=self.gol_g.id).results

        self.assertNotIn(self.req_c.id, [row.id for row in rows])
        self.assertNotIn("Ziel DE Anforderung", [row.title for row in rows])

    def test_the_de_variant_of_a_referenced_requirement_is_never_the_resolution_target(self):
        """The id exists in both languages; the resolved row is the flat file even though a DE file shares the id."""
        rows = [row for row in list_references(type="gol", id=self.gol_g.id).results if row.type == "req"]
        de_dir = SPECS_BY_NAME["req"].base_dir("de").resolve()

        self.assertTrue(de_dir.is_dir())
        self.assertNotEqual(Path(rows[0].path).resolve().parent, de_dir)

    def test_a_de_only_document_is_not_a_resolvable_source(self):
        orphan_id = "00000000-0000-4000-8000-0000000000d1"
        orphan = self.gol_de.parent / f"gol-{orphan_id}-orphan.md"
        orphan.write_text(self.gol_de.read_text(encoding="utf-8").replace(self.gol_g.id, orphan_id), encoding="utf-8")

        with self.assertRaises(GolNotFoundError):
            list_references(type="gol", id=orphan_id)

    def test_a_reference_to_a_de_only_document_is_unresolved(self):
        """A reference to an id that exists only below ``de/`` never resolves (it is a dangling reference)."""
        req = SPECS_BY_NAME["req"]
        orphan_id = "00000000-0000-4000-8000-0000000000d2"
        de_file = req.base_dir("de") / next(req.base_dir("de").glob("*.md")).name
        (req.base_dir("de") / f"req-{orphan_id}-orphan.md").write_text(
            de_file.read_text(encoding="utf-8").replace(self.req_b.id, orphan_id), encoding="utf-8"
        )
        gol = SPECS_BY_NAME["gol"]
        gol_source = gol.fn("create")(_gol_body(gol, "Dangling Source Goal", (orphan_id, "Only in de")))

        rows = [row for row in list_references(type="gol", id=gol_source.id).results if row.id == orphan_id]

        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0].path)
        self.assertIsNone(rows[0].title)
        self.assertTrue(rows[0].error)


class TestReferenceDiagramsStayEnOnly(_ReferenceFixtureTestCase):
    """REQ-013/ACC-014 for ``get_reference_diagram`` and ``get_reference_diagram_all``."""

    def test_the_per_document_diagram_has_only_en_nodes_and_edges(self):
        diagram = get_reference_diagram(type="gol", id=self.gol_g.id, depth=2, reverse=True)

        self.assertIn('"Source EN Goal"', diagram)
        self.assertIn('"Target EN Requirement"', diagram)
        self.assertNotIn("Quelle DE Ziel", diagram)
        self.assertNotIn("Ziel DE Anforderung", diagram)
        self.assertNotIn(self.req_c.id, diagram, "the DE-only edge to requirement C leaked")
        self.assertIn(f"[GOL-{self.gol_g.id}] --> [REQ-{self.req_b.id}]", diagram)

    def test_the_reverse_expansion_never_finds_a_referrer_through_a_language_variant(self):
        """C is referenced only by the German variant of the goal: it has no incoming edge in the EN-only registry."""
        diagram = get_reference_diagram(type="req", id=self.req_c.id, reverse=True)

        self.assertIn('"Other EN Requirement"', diagram)
        self.assertNotIn(f"[GOL-{self.gol_g.id}]", diagram)
        self.assertNotIn(f"--> [REQ-{self.req_c.id}]", diagram)

    def test_a_de_only_document_is_not_a_resolvable_diagram_source(self):
        orphan_id = "00000000-0000-4000-8000-0000000000d3"
        orphan = self.gol_de.parent / f"gol-{orphan_id}-orphan.md"
        orphan.write_text(self.gol_de.read_text(encoding="utf-8").replace(self.gol_g.id, orphan_id), encoding="utf-8")

        with self.assertRaises(GolNotFoundError):
            get_reference_diagram(type="gol", id=orphan_id)

    def test_the_registry_wide_diagram_enumerates_no_language_variant(self):
        orphan_id = "00000000-0000-4000-8000-0000000000d4"
        orphan = self.gol_de.parent / f"gol-{orphan_id}-orphan.md"
        orphan.write_text(
            self.gol_de.read_text(encoding="utf-8")
            .replace(self.gol_g.id, orphan_id)
            .replace("Quelle DE Ziel", "Waise"),
            encoding="utf-8",
        )

        diagram = get_reference_diagram_all()

        for text in ("Source EN Goal", "Target EN Requirement", "Other EN Requirement"):
            self.assertIn(f'"{text}"', diagram)
        for text in ("Quelle DE Ziel", "Ziel DE Anforderung", "Waise", orphan_id, self.req_c.id + "] <<UNRESOLVED>>"):
            self.assertNotIn(text, diagram)
        self.assertNotIn(f"[GOL-{self.gol_g.id}] --> [REQ-{self.req_c.id}]", diagram)
        self.assertIn(f"[GOL-{self.gol_g.id}] --> [REQ-{self.req_b.id}]", diagram)


class TestRegistryDiagramAcrossAllDomainsStaysEnOnly(_EnOnlyTestCase):
    """REQ-013/ACC-014: ``get_reference_diagram_all`` over all eleven domains holds one node per EN document."""

    def test_the_registry_wide_diagram_has_one_node_per_en_document_across_all_eleven_domains(self):
        seeded = self.seed_all()

        diagram = get_reference_diagram_all()

        for spec in SPECS:
            with self.subTest(domain=spec.d):
                doc_id = seeded[spec.d][0]
                self.assertEqual(diagram.count(f"as [{spec.d.upper()}-{doc_id}]"), 1)
        self.assertNotIn(_MARKER, diagram)
        self.assertNotIn("DE ", diagram.replace("DE-", ""))


class TestFlatScansNeverSeeALanguageFolder(unittest.TestCase):
    """The structural fact ADR 38efdb66 item 8 rests on, per domain: a ``de/`` file is invisible to the flat scan,
    the id lookup and the listing -- even when hand-planted. A future recursive glob fails these tests."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        for spec in SPECS:
            spec.reset_cache()
            self.addCleanup(spec.reset_cache)

    def test_a_planted_language_only_document_is_invisible_to_scan_lookup_and_listing_in_every_domain(self):
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                spec.reset_cache()
                doc_id, en_file, de_file = seed_pair(spec)
                orphan_id = "00000000-0000-4000-8000-0000000000e1"
                orphan = de_file.parent / de_file.name.replace(doc_id, orphan_id)
                orphan.write_text(de_file.read_text(encoding="utf-8").replace(doc_id, orphan_id), encoding="utf-8")
                nested = de_file.parent / "nested"
                nested.mkdir()
                (nested / de_file.name).write_text(de_file.read_text(encoding="utf-8"), encoding="utf-8")

                self.assertEqual(spec.iter_paths(), [en_file])
                self.assertEqual(list(iter_doc_paths(spec.base_dir())), [en_file])
                self.assertEqual([row.id for row in spec.fn("list")().results], [doc_id])
                self.assertEqual(spec.fn("list")().total, 1)
                with self.assertRaises(spec.not_found_error()):
                    spec.fn("get")(orphan_id)
                self.assertEqual(spec.fn("get")(orphan_id, language="de").frontmatter.id, orphan_id)
                self.assertEqual(spec.iter_paths("de"), sorted([de_file, orphan]))


if __name__ == "__main__":
    unittest.main()
