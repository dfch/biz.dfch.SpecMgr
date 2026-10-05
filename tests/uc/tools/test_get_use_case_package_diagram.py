# Copyright (C) 2026 Ronald Rink, http://d-fens.ch
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

"""Tests for the ``get_use_case_package_diagram`` ``@mcp.tool()`` wrapper (feat-185-uc-diagrams, Phase 120).

The tool is thin over the pure ``render_use_case_package``: it owns the disk
resolution only. ``ids=None`` delegates to the ``list_uc`` tool (all pages,
its filename-sorted order, its ``<failed to parse>`` failed rows); explicit
ids are ``_path_safety``-guarded (wrong format => ``ValueError`` before any
file access) and read cache-aware. A missing id or an existing-but-broken
one becomes a skipped ``use_case=None`` slot, and every reference that does
not resolve to a parsed slot of the package takes the renderer's
deterministic unresolvable-note path -- the render never fails on an id.

The multi-UC fixture documents (cross-referencing the Phase 110 goldens)
are the committed files under ``tests/fixtures/uc-diagrams/package/``.
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.uc.tools.get_use_case_package_diagram import get_use_case_package_diagram

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "uc-diagrams" / "package"
_GOLDEN = _FIXTURES.parent / "package.golden"

#: The fixture documents' frozen ids (the same map the Phase 110 renderer
#: tests seed with; the files are named ``<id>.md``).
_PLACE = "11111111-1111-4111-8111-111111111111"
_CHARGE = "22222222-2222-4222-8222-222222222222"
_REFUND = "33333333-3333-4333-8333-333333333333"
_BROKEN = "44444444-4444-4444-8444-444444444444"
_MISSING = "00000000-0000-0000-0000-000000000000"

#: The Phase 110 golden's node order (place, charge, refund -- broken skipped),
#: which is also ``list_uc``'s filename-sorted order for this fixture set.
_GOLDEN_ORDER = (_PLACE, _CHARGE, _REFUND, _BROKEN)


class TestGetUseCasePackageDiagram(unittest.TestCase):
    """Tests for the get_use_case_package_diagram tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        self._seed_package_fixtures()

    def _seed_package_fixtures(self) -> None:
        """Seed the four committed package fixture documents under the isolated docs root,
        each named ``<id>.md`` (the flat-file form ``find_uc_path``'s id scan resolves)."""
        uc_dir = self.docs_root / "uc"
        uc_dir.mkdir()
        for name, doc_id in (
            ("place-order.md", _PLACE),
            ("charge-card.md", _CHARGE),
            ("refund-order.md", _REFUND),
            ("broken.md", _BROKEN),
        ):
            shutil.copy(_FIXTURES / name, uc_dir / f"{doc_id}.md")

    def test_ids_none_matches_the_phase_110_golden(self):
        """ids=None = every UC in list_uc order (filename-sorted for this fixture set = the
        Phase 110 golden's order); the broken fixture is a list_uc failed row -> skipped slot,
        and its reference takes the unresolvable-note path."""
        result = get_use_case_package_diagram()

        self.assertEqual(result, _GOLDEN.read_text(encoding="utf-8"))

    def test_explicit_ids_in_golden_order_match_the_golden(self):
        """Explicit ids in the same order as ids=None must render the identical diagram."""
        result = get_use_case_package_diagram(ids=list(_GOLDEN_ORDER))

        self.assertEqual(result, _GOLDEN.read_text(encoding="utf-8"))

    def test_explicit_ids_control_the_node_order(self):
        """The given order is the package order: uc1/uc2 aliases follow the id list, not the listing."""
        result = get_use_case_package_diagram(ids=[_REFUND, _PLACE])

        lines = result.split("\n")
        refund_line = 'usecase "Refund Order" as uc1 <<subfunction>>'
        place_line = 'usecase "Place Order" as uc2 <<user goal>>'
        self.assertIn(refund_line, lines)
        self.assertIn(place_line, lines)
        self.assertLess(lines.index(refund_line), lines.index(place_line))

    def test_explicit_missing_id_is_a_skipped_slot_with_a_note(self):
        """An id missing on disk never fails the render: it is a skipped slot, and Place order's
        references to the other (here, out-of-package) ids all take the unresolvable-note path."""
        result = get_use_case_package_diagram(ids=[_PLACE, _MISSING])

        self.assertNotIn("as uc2", result)  # the missing id renders no node
        for label in ("Charge card", "Refund order", "Legacy item", ""):
            with self.subTest(label=label):
                self.assertIn(f'note bottom of uc1: Unresolved UC reference: "{label}"', result)

    def test_explicit_broken_id_is_the_same_note_path_as_a_missing_one(self):
        """An id that exists but fails to parse is the same skipped slot as a missing one: no node,
        and Place order's reference to it carries the unresolvable note (empty inline label)."""
        result = get_use_case_package_diagram(ids=[_PLACE, _BROKEN])

        self.assertNotIn("Broken Fixture", result)  # skipped as a node
        self.assertIn('note bottom of uc1: Unresolved UC reference: ""', result)

    def test_broken_and_missing_slots_render_checker_clean(self):
        """The note-path render is deterministic PlantUML source (checker-clean, both modes)."""
        from biz.dfch.specmgr.plantuml import structure as S

        result = get_use_case_package_diagram(ids=[_PLACE, _BROKEN, _MISSING])

        for mode in (S.MODE_PREFLIGHT, S.MODE_STANDALONE):
            with self.subTest(mode=mode):
                check = S.check_structure(result, mode)
                self.assertTrue(check.ok)
                self.assertEqual(check.errors, [])

    def test_wrong_format_id_raises_value_error_before_any_file_access(self):
        """A wrong-format id in the list must raise ValueError (even alongside valid ids) -- the
        _path_safety guard runs over the whole list before any disk read."""
        with self.assertRaises(ValueError) as ctx:
            get_use_case_package_diagram(ids=[_PLACE, "not-a-uuid"])
        self.assertIn("not-a-uuid", str(ctx.exception))
        with self.assertRaises(ValueError):
            get_use_case_package_diagram(ids=["../escape"])

    def test_empty_explicit_id_list_renders_the_empty_package(self):
        """An empty explicit list is a valid, deterministic package: header + direction + @enduml,
        no nodes, no edges, no notes."""
        result = get_use_case_package_diagram(ids=[])

        self.assertEqual(result, "@startuml UC Package\nleft to right direction\n\n\n\n@enduml\n")

    def test_ids_none_with_no_documents_renders_the_empty_package(self):
        """An empty docs directory (list_uc rows: none) is the same deterministic empty package."""
        uc_dir = self.docs_root / "uc"
        for path in uc_dir.glob("*.md"):
            path.unlink()

        result = get_use_case_package_diagram()

        self.assertEqual(result, "@startuml UC Package\nleft to right direction\n\n\n\n@enduml\n")


if __name__ == "__main__":
    unittest.main()
