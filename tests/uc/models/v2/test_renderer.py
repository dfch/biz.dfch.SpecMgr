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
# along with this program.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for the v2 renderers (`uc/models/v2/renderer.py`).

Golden-pinned (ACC-001): the Buy Goods usecase diagram is byte-identical to
the rulebook §2.6 reference rendering; the Buy Goods sequence skeleton and
the multi-UC package diagram are pinned against committed goldens under
`tests/fixtures/uc-diagrams/`. Every renderer output passes the structure
checker (both modes where applicable — the skeleton carries UNATTRIBUTED
marker warnings only; the package/usecase goldens are clean). The packaged
fully-attributed example (`uc/data/uc_plantuml_example.md`) is pinned as the
skeleton with each UNATTRIBUTED marker line replaced by the frozen test-local
attribution table, so it cannot drift from the renderer.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text
from biz.dfch.specmgr.plantuml import structure as S
from biz.dfch.specmgr.uc.models.v1.uc_diagram import (
    _BARE_ALIAS_PATTERN as V1_BARE_ALIAS_PATTERN,
)
from biz.dfch.specmgr.uc.models.v1.uc_diagram import _actor_label as v1_actor_label
from biz.dfch.specmgr.uc.models.v2 import parse_uc
from biz.dfch.specmgr.uc.models.v2.renderer import (
    _UC_REFERENCE_PATTERN,
    PackageDocument,
    render_uc_diagram,
    render_uc_sequence_skeleton,
    render_use_case_package,
)
from biz.dfch.specmgr.uc.tools._io import load_by_id
from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError, uc_base_dir

_FIXTURES = Path(__file__).resolve().parents[3] / "fixtures" / "uc-diagrams"

#: The frozen attribution table for the packaged example: every UNATTRIBUTED
#: marker line of the skeleton → its reasoned arrow (the test-local source of
#: truth the pinning test applies; the reasons live in the example file's
#: own ' comments).
_ATTRIBUTIONS = {
    "' UNATTRIBUTED trigger: Purchase request comes in (via phone, fax, web form, or electronic interchange)": "Buyer -> Company: Purchase request comes in (via phone, fax, web form, or electronic interchange)",
    "' UNATTRIBUTED ext 7a step 2: If backup service also unavailable, company informs buyer of delay.": "Company -> Buyer: If backup service also unavailable, company informs buyer of delay.",
    "' UNATTRIBUTED ext 8a step 2: If all channels fail, company logs issue for manual follow-up.": "Company -> Company: If all channels fail, company logs issue for manual follow-up.",
    "' UNATTRIBUTED ext 10b step 3: Dispute is resolved (refund, credit, or confirmation of charge).": "p2 -> Company: Dispute is resolved (refund, credit, or confirmation of charge).",
    "' UNATTRIBUTED ext 10c step 2: If retry fails, company contacts buyer to resolve payment issue.": "Company -> Buyer: If retry fails, company contacts buyer to resolve payment issue.",
}

_PACKAGE_FIXTURE_IDS = {
    "place-order.md": "11111111-1111-4111-8111-111111111111",
    "charge-card.md": "22222222-2222-4222-8222-222222222222",
    "refund-order.md": "33333333-3333-4333-8333-333333333333",
    "broken.md": "44444444-4444-4444-8444-444444444444",
}


def _example_use_case():
    return parse_uc(read_packaged_text("uc", "example")).body


def _strip_comments(text: str) -> list[str]:
    return [line for line in text.split("\n") if not line.lstrip().startswith("'")]


class TestUsecaseDiagram(unittest.TestCase):
    """render_uc_diagram — the rulebook §2.6 frozen reference rendering."""

    def test_buy_goods_renders_the_frozen_golden(self):
        sut = render_uc_diagram

        golden = (_FIXTURES / "buy-goods.usecase.golden").read_text(encoding="utf-8")
        result = sut(_example_use_case())

        self.assertEqual(result, golden)
        self.assertEqual(
            result,
            '@startuml Buy Goods\n\nactor Buyer\nactor "Credit card company" as actor2\nactor Bank\n'
            'actor "Shipping service" as actor4\nusecase "Buy Goods" as uc <<summary>>\n\nBuyer --> uc\n'
            "actor2 --> uc\nBank --> uc\nactor4 --> uc\n\n@enduml\n",
        )

    def test_golden_passes_the_structure_checker_both_modes(self):
        golden = (_FIXTURES / "buy-goods.usecase.golden").read_text(encoding="utf-8")

        for mode in (S.MODE_PREFLIGHT, S.MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = S.check_structure(golden, mode)
                self.assertTrue(result.ok)
                self.assertEqual(result.warnings, [])

    def test_level_normalisation(self):
        use_case = _example_use_case()

        with mock.patch.object(
            type(use_case.characteristic_information.level.body[0]), "__str__", return_value="User Goal\n"
        ):
            self.assertIn("<<user goal>>", render_uc_diagram(use_case))
        with mock.patch.object(
            type(use_case.characteristic_information.level.body[0]), "__str__", return_value="  SubFUNCTION  \n"
        ):
            self.assertIn("<<subfunction>>", render_uc_diagram(use_case))
        with mock.patch.object(
            type(use_case.characteristic_information.level.body[0]), "__str__", return_value="Epic\n"
        ):
            rendered = render_uc_diagram(use_case)
            self.assertNotIn("<<", rendered)

    def test_actor_label_parity_with_v1(self):
        from biz.dfch.specmgr.uc.models.v2.renderer import _actor_label

        corpus = [
            "Buyer (any agent or computer acting for the customer)",
            "Credit card company (for payment processing)",
            'Company refers to buyer as "Buyer" (any agent...)',
            '"Quoted only"',
            'Mixed "Quoted" (with parenthetical)',
            "Plain",
            "  spaced  ( padded )",
            "",
        ]
        for text in corpus:
            with self.subTest(text=text):
                self.assertEqual(_actor_label(text), v1_actor_label(text))

    def test_bare_alias_pattern_parity_with_v1(self):
        from biz.dfch.specmgr.uc.models.v2.renderer import _BARE_ALIAS_PATTERN

        self.assertEqual(_BARE_ALIAS_PATTERN.pattern, V1_BARE_ALIAS_PATTERN.pattern)


class TestSequenceSkeleton(unittest.TestCase):
    """render_uc_sequence_skeleton — the rulebook §2.9 frozen layout."""

    def test_buy_goods_renders_the_frozen_golden(self):
        sut = render_uc_sequence_skeleton

        golden = (_FIXTURES / "buy-goods.sequence.golden").read_text(encoding="utf-8")
        result = sut(_example_use_case())

        self.assertEqual(result, golden)

    def test_golden_carries_the_five_expected_markers(self):
        golden = (_FIXTURES / "buy-goods.sequence.golden").read_text(encoding="utf-8")
        markers = [line for line in golden.split("\n") if line.startswith(S.UNATTRIBUTED_MARKER_PREFIX)]

        self.assertEqual(len(markers), 5)
        self.assertTrue(any(line.startswith("' UNATTRIBUTED trigger:") for line in markers))
        self.assertTrue(any("ext 7a step 2" in line for line in markers))
        self.assertTrue(any("ext 8a step 2" in line for line in markers))
        self.assertTrue(any("ext 10b step 3" in line for line in markers))
        self.assertTrue(any("ext 10c step 2" in line for line in markers))

    def test_golden_attribution_spot_checks(self):
        golden = (_FIXTURES / "buy-goods.sequence.golden").read_text(encoding="utf-8")
        lines = golden.split("\n")

        # the frozen worked examples (rulebook §2.9.3)
        self.assertIn("Buyer -> Company: Buyer calls in with a purchase request.", lines)
        self.assertIn(
            "Company -> Buyer: Company captures buyer's name, address, requested goods, quantity, and delivery date preference.",
            lines,
        )
        self.assertIn("Company -> Company: Company checks inventory for requested goods.", lines)
        # the D4 disambiguation: positional receiver, not a self-message
        self.assertIn("Company -> p4: Company attempts to use backup shipping service.", lines)
        # the single-line-escaped soft-wrapped extension item
        self.assertIn(
            "Company -> Buyer: Company informs buyer of out-of-stock items.\\nThis should rarely happen. Still we have to address this.",
            lines,
        )
        # the resumption notes (full item text, no message)
        self.assertIn("  Return to step 4.", lines)
        self.assertIn("  Continue to step 6.", lines)
        self.assertIn("  Once payment is received, continue to step 11.", lines)
        # the sub-variation note (heading text + bullets verbatim)
        self.assertIn("  Step 1: Buyer may use", lines)
        self.assertIn("  Electronic data interchange (EDI)", lines)

    def test_golden_passes_the_structure_checker_zero_errors_marker_warnings_only(self):
        golden = (_FIXTURES / "buy-goods.sequence.golden").read_text(encoding="utf-8")

        for mode in (S.MODE_PREFLIGHT, S.MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = S.check_structure(golden, mode)
                self.assertTrue(result.ok)
                self.assertEqual(len(result.warnings), 5)
                for warning in result.warnings:
                    self.assertIn("UNATTRIBUTED marker", warning.message)

    def test_example_file_is_the_skeleton_with_the_frozen_attributions(self):
        """The ACC-001 pinning: the committed example cannot drift from the renderer.

        The example file (with its ' reasoning comments stripped) must equal
        the skeleton with each UNATTRIBUTED marker line replaced by its frozen
        attribution — and the attribution table must cover every marker.
        """
        use_case = _example_use_case()

        skeleton = render_uc_sequence_skeleton(use_case)
        skeleton_lines = skeleton.split("\n")
        marker_lines = {line for line in skeleton_lines if line.startswith(S.UNATTRIBUTED_MARKER_PREFIX)}
        self.assertEqual(marker_lines, set(_ATTRIBUTIONS))

        transformed = [_ATTRIBUTIONS.get(line, line) for line in skeleton_lines]
        example = read_packaged_text("uc", "plantuml_example")

        self.assertEqual(_strip_comments("\n".join(transformed)), _strip_comments(example))
        self.assertFalse(any(line.startswith(S.UNATTRIBUTED_MARKER_PREFIX) for line in example.split("\n")))


class TestUseCasePackage(unittest.TestCase):
    """render_use_case_package — the multi-UC fixture (ACC-001) via an isolated docs dir."""

    def _package_documents(self) -> list[PackageDocument]:
        """Load the package fixtures via the uc read path under the patched ``SPECMGR_DOCS_DIR``."""
        documents: list[PackageDocument] = []
        for name in ("place-order.md", "charge-card.md", "refund-order.md", "broken.md"):
            doc_id = _PACKAGE_FIXTURE_IDS[name]
            try:
                _path, doc = load_by_id(uc_base_dir(), doc_id)
                documents.append(PackageDocument(id=doc_id, use_case=doc.body))
            except UcNotFoundError:
                documents.append(PackageDocument(id=doc_id, use_case=None))
        return documents

    def test_package_renders_the_frozen_golden(self):
        with tempfile.TemporaryDirectory() as tmp:
            uc_dir = Path(tmp) / "uc"
            uc_dir.mkdir()
            for name, doc_id in _PACKAGE_FIXTURE_IDS.items():
                shutil.copy(_FIXTURES / "package" / name, uc_dir / f"{doc_id}.md")
            with mock.patch.dict(os.environ, {"SPECMGR_DOCS_DIR": tmp}):
                documents = self._package_documents()

        rendered = render_use_case_package(documents)
        golden = (_FIXTURES / "package.golden").read_text(encoding="utf-8")

        self.assertEqual(rendered, golden)

    def test_package_golden_passes_the_structure_checker_both_modes(self):
        golden = (_FIXTURES / "package.golden").read_text(encoding="utf-8")

        for mode in (S.MODE_PREFLIGHT, S.MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = S.check_structure(golden, mode)
                self.assertTrue(result.ok)
                self.assertEqual(result.warnings, [])

    def test_broken_slot_is_skipped_and_referenced_as_unresolvable(self):
        with tempfile.TemporaryDirectory() as tmp:
            uc_dir = Path(tmp) / "uc"
            uc_dir.mkdir()
            for name, doc_id in _PACKAGE_FIXTURE_IDS.items():
                shutil.copy(_FIXTURES / "package" / name, uc_dir / f"{doc_id}.md")
            with mock.patch.dict(os.environ, {"SPECMGR_DOCS_DIR": tmp}):
                documents = self._package_documents()

        broken_slot = documents[3]
        self.assertIsNone(broken_slot.use_case)
        rendered = render_use_case_package(documents)
        self.assertNotIn("Broken Fixture", rendered)  # skipped as a node
        self.assertIn('note bottom of uc1: Unresolved UC reference: ""', rendered)  # the ref to it (empty label)

    def test_edge_kinds_and_note_paths_in_the_golden(self):
        golden = (_FIXTURES / "package.golden").read_text(encoding="utf-8")
        lines = golden.split("\n")

        # resolvable include (Subordinate:), one per reference in the multi-ref bullet
        self.assertIn("uc1 ..> uc2 : <<include>> Charge card", lines)
        self.assertIn("uc1 ..> uc3 : <<include>> Refund order", lines)
        # resolvable extend (Extension:) — referenced ..> this
        self.assertIn("uc3 ..> uc2 : <<extend>> Refund order", lines)
        # resolvable superordinate — superordinate ..> this, no stereotype
        self.assertIn("uc1 ..> uc2 : Place order", lines)
        # unresolvable: legacy UC-NNN, broken document (empty label), outside package
        self.assertIn('note bottom of uc1: Unresolved UC reference: "Legacy item"', lines)
        self.assertIn('note bottom of uc1: Unresolved UC reference: ""', lines)
        self.assertIn('note bottom of uc2: Unresolved UC reference: "Unknown service"', lines)


class TestReferencePatternParity(unittest.TestCase):
    """The renderer's UC-token regex must agree with the shared reference vocabulary."""

    def test_uuid_tokens_match_the_shared_vocabulary(self):
        from biz.dfch.specmgr.general.tools._references import find_references

        bullet = (
            "Subordinate: Charge card (UC 22222222-2222-4222-8222-222222222222), "
            "Refund order (UC-33333333-3333-4333-8333-333333333333), Legacy item (UC-099)"
        )

        renderer_uuids = [match.group(1) for match in _UC_REFERENCE_PATTERN.finditer(bullet) if "-" in match.group(1)]
        shared = [ref_id for ref_type, ref_id in find_references(bullet) if ref_type == "uc"]

        self.assertEqual(renderer_uuids, shared)
        # the legacy token is a renderer-only addition (unresolvable by definition)
        self.assertEqual(len(list(_UC_REFERENCE_PATTERN.finditer(bullet))), 3)


if __name__ == "__main__":
    unittest.main()
