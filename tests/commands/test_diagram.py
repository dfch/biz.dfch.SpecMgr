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

"""Tests for the ``diagram uc`` command (feat-185-uc-diagrams, Phase 130).

The command is a thin, deterministic-only layer: disk resolution is the Phase
120 ``get_use_case_package_diagram`` tool's own wiring (imported lazily by the
command), rendering is the pure Phase 110 ``uc.models.v2.renderer``. These
tests pin the CLI's own contract: the §2.10 file layout (``<id>.usecase.puml``
+ ``package.puml``), byte parity with the committed goldens (``package.golden``
for the package fixture set, ``buy-goods.usecase.golden`` for the packaged
example), the pinned exit codes (0 no diff / 1 diff found / 2 usage-or-render
error), the sequence-file immunity (``<id>.sequence.puml`` is agent-owned and
never created, overwritten, read, or diffed), and the absence of the
agent-path ``' validated: structure-only`` header (ACC-001).

The isolated docs root follows the Phase 110/120 test pattern: a tmp
``SPECMGR_DOCS_DIR`` seeded from the committed fixtures under
``tests/fixtures/uc-diagrams/package/``.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from typer.testing import CliRunner

from biz.dfch.specmgr.cli import app
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text
from biz.dfch.specmgr.uc.models.v2 import parse_uc
from biz.dfch.specmgr.uc.models.v2.renderer import render_uc_diagram

runner = CliRunner()

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "uc-diagrams"
_PACKAGE_FIXTURES = _FIXTURES / "package"
_USECASE_GOLDEN = _FIXTURES / "buy-goods.usecase.golden"
_PACKAGE_GOLDEN = _FIXTURES / "package.golden"

#: The fixture documents' frozen ids (the same map the Phase 110/120 tests seed with).
_PLACE = "11111111-1111-4111-8111-111111111111"
_CHARGE = "22222222-2222-4222-8222-222222222222"
_REFUND = "33333333-3333-4333-8333-333333333333"
_BROKEN = "44444444-4444-4444-8444-444444444444"
_MISSING = "00000000-0000-0000-0000-000000000000"

#: The packaged example UC's own (legacy, non-UUID) id — resolvable in ``all``
#: mode via the ``list_uc`` rows, never a valid explicit ``validate_id`` input.
_EXAMPLE_ID = "uc-001"


class _DiagramUcTestBase(unittest.TestCase):
    """Shared setUp: an isolated ``SPECMGR_DOCS_DIR`` + a fresh tmp ``--out`` dir (never pre-created)."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        self.out_dir = Path(self.enterContext(tempfile.TemporaryDirectory())) / "diagrams" / "uc"

    def _seed_package_fixtures(self) -> None:
        """Seed the four committed package fixture documents (the healthy ones as ``<id>.md``, the
        broken one in the ``create_uc`` naming convention ``uc-<id>-<slug>.md`` so
        ``find_parse_failure`` can classify an explicit request as existing-but-broken, not missing)."""
        uc_dir = self.docs_root / "uc"
        uc_dir.mkdir()
        for name, doc_id in (
            ("place-order.md", _PLACE),
            ("charge-card.md", _CHARGE),
            ("refund-order.md", _REFUND),
        ):
            shutil.copy(_PACKAGE_FIXTURES / name, uc_dir / f"{doc_id}.md")
        shutil.copy(_PACKAGE_FIXTURES / "broken.md", uc_dir / f"uc-{_BROKEN}-broken.md")

    def _seed_example_only(self) -> None:
        """Seed only the packaged example UC document (its own ``read_packaged_text`` content)."""
        uc_dir = self.docs_root / "uc"
        uc_dir.mkdir()
        example_text = read_packaged_text("uc", "example")
        (uc_dir / f"uc-{_EXAMPLE_ID}-buy-goods.md").write_text(example_text, encoding="utf-8")

    def _invoke(self, *args: str) -> "unittest.mock.MagicMock":
        """One ``specmgr diagram uc ...`` invocation (the full Typer app, like every CLI test)."""
        result = runner.invoke(app, ["diagram", "uc", *args])
        return result


class TestDiagramUcAllWrite(_DiagramUcTestBase):
    """``diagram uc all`` over the committed package fixture set (plus the broken document)."""

    def setUp(self) -> None:
        super().setUp()
        self._seed_package_fixtures()

    def test_all_writes_per_uc_files_and_the_package_golden(self):
        """(a) all → one <id>.usecase.puml per parsed UC + package.puml byte-identical to the committed
        golden; the per-UC files equal the pure renderer's own output for the same documents (the CLI
        wiring, not the renderer, is what this command owns)."""
        result = self._invoke("all", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            {path.name for path in self.out_dir.iterdir()},
            {f"{_PLACE}.usecase.puml", f"{_CHARGE}.usecase.puml", f"{_REFUND}.usecase.puml", "package.puml"},
        )
        self.assertEqual(
            (self.out_dir / "package.puml").read_text(encoding="utf-8"),
            _PACKAGE_GOLDEN.read_text(encoding="utf-8"),
        )
        for name, doc_id in (("place-order.md", _PLACE), ("charge-card.md", _CHARGE), ("refund-order.md", _REFUND)):
            doc = parse_uc((_PACKAGE_FIXTURES / name).read_text(encoding="utf-8"))
            self.assertEqual(
                (self.out_dir / f"{doc_id}.usecase.puml").read_text(encoding="utf-8"),
                render_uc_diagram(doc.body),
            )

    def test_all_with_broken_doc_skips_it_without_failing(self):
        """(g) all with the broken document present → exit 0, a skip warning, no per-UC file for it, and
        the package carries its deterministic unresolvable note (REQ-002 — the render never fails)."""
        result = self._invoke("all", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("skipped", result.stdout)
        self.assertFalse((self.out_dir / f"{_BROKEN}.usecase.puml").exists())
        self.assertIn("Unresolved UC reference", (self.out_dir / "package.puml").read_text(encoding="utf-8"))

    def test_sequence_file_never_touched(self):
        """(h) SEQUENCE-FILE IMMUNITY: a pre-existing <id>.sequence.puml (agent-owned) is byte-identical
        after a write run — the CLI never creates, overwrites, reads, or diffs it."""
        self.out_dir.mkdir(parents=True)
        sentinel = "@startuml\n' agent-owned sentinel — never CLI-reproducible\n@enduml\n"
        sequence_path = self.out_dir / f"{_PLACE}.sequence.puml"
        sequence_path.write_text(sentinel, encoding="utf-8")

        result = self._invoke("all", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(sequence_path.read_text(encoding="utf-8"), sentinel)
        self.assertEqual(list(self.out_dir.glob("*.sequence.puml")), [sequence_path])

    def test_no_structure_only_header_in_any_artifact(self):
        """(i) ACC-001: no written artifact carries the agent-path ' validated: structure-only header
        (the CLI output is checker-clean by construction, REQ-005)."""
        result = self._invoke("all", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        for path in self.out_dir.iterdir():
            with self.subTest(path=path.name):
                self.assertNotIn("validated: structure-only", path.read_text(encoding="utf-8"))

    def test_check_green_then_red_after_mutation(self):
        """(c) --check → exit 0 (every file unchanged) on the just-written files; after mutating one,
        exit 1 naming the differing file (the untouched files still report unchanged)."""
        write = self._invoke("all", "--out", str(self.out_dir))
        self.assertEqual(write.exit_code, 0, write.output)

        green = self._invoke("all", "--out", str(self.out_dir), "--check")
        self.assertEqual(green.exit_code, 0, green.output)
        self.assertEqual(green.stdout.count("(unchanged)"), 4)
        self.assertNotIn("(differs)", green.stdout)

        package_path = self.out_dir / "package.puml"
        package_path.write_text(package_path.read_text(encoding="utf-8") + "' drift\n", encoding="utf-8")

        red = self._invoke("all", "--out", str(self.out_dir), "--check")
        self.assertEqual(red.exit_code, 1, red.output)
        self.assertIn("package.puml", red.stdout)
        self.assertIn("(differs)", red.stdout)
        self.assertEqual(red.stdout.count("(unchanged)"), 3)

    def test_check_missing_file_counts_as_differing_and_writes_nothing(self):
        """(d) --check against an out dir that was never written → exit 1, every expected file reported
        missing; check mode never creates the directory or writes a file."""
        result = self._invoke("all", "--out", str(self.out_dir), "--check")

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertEqual(result.stdout.count("(missing)"), 4)
        self.assertFalse(self.out_dir.exists())

    def test_default_out_is_cwd_relative_diagrams_uc(self):
        """The default --out is CWD-relative diagrams/uc/ (rulebook §2.10 file layout)."""
        cwd = Path(self.enterContext(tempfile.TemporaryDirectory()))
        old_cwd = os.getcwd()
        os.chdir(cwd)
        self.addCleanup(os.chdir, old_cwd)

        result = self._invoke("all")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue((cwd / "diagrams" / "uc" / "package.puml").is_file())
        self.assertTrue((cwd / "diagrams" / "uc" / f"{_PLACE}.usecase.puml").is_file())


class TestDiagramUcExample(_DiagramUcTestBase):
    """``diagram uc all`` over only the packaged example UC (the per-UC golden parity)."""

    def setUp(self) -> None:
        super().setUp()
        self._seed_example_only()

    def test_all_writes_the_buy_goods_usecase_golden(self):
        """(a) byte-identical to the committed golden: uc-001.usecase.puml == buy-goods.usecase.golden —
        and the example's legacy UC-NNN references take the package's unresolvable-note path."""
        result = self._invoke("all", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            (self.out_dir / f"{_EXAMPLE_ID}.usecase.puml").read_text(encoding="utf-8"),
            _USECASE_GOLDEN.read_text(encoding="utf-8"),
        )
        package_text = (self.out_dir / "package.puml").read_text(encoding="utf-8")
        self.assertIn('usecase "Buy Goods" as uc1 <<summary>>', package_text)
        self.assertIn("Unresolved UC reference", package_text)


class TestDiagramUcExplicitIds(_DiagramUcTestBase):
    """Explicit-id invocations: the pinned usage/render error paths (exit 2) + the subset write."""

    def setUp(self) -> None:
        super().setUp()
        self._seed_package_fixtures()

    def test_explicit_subset_writes_only_those_files_and_the_same_package(self):
        """(b) explicit ids → exactly those per-UC files + package.puml, byte-identical to the Phase 120
        tool's own render for the same ids (the one-implementation reuse pin)."""
        from biz.dfch.specmgr.uc.tools.get_use_case_package_diagram import get_use_case_package_diagram

        ids = [_PLACE, _CHARGE]
        result = self._invoke(*ids, "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            {path.name for path in self.out_dir.iterdir()},
            {f"{_PLACE}.usecase.puml", f"{_CHARGE}.usecase.puml", "package.puml"},
        )
        self.assertEqual(
            (self.out_dir / "package.puml").read_text(encoding="utf-8"),
            get_use_case_package_diagram(ids=ids),
        )

    def test_wrong_format_id_exits_2_before_any_write(self):
        """(e) a wrong-format id → exit 2 (the _path_safety guard, before any file access) — no out dir."""
        result = self._invoke("not-a-uuid", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("not-a-uuid", result.output)
        self.assertFalse(self.out_dir.exists())

    def test_path_injection_id_exits_2(self):
        """A traversal id → exit 2, no out dir (the same guard's injection branch)."""
        result = self._invoke("../escape", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertFalse(self.out_dir.exists())

    def test_no_ids_is_a_usage_error(self):
        """Zero ids (the variadic argument is required) → the Typer usage error, exit 2, no out dir."""
        result = self._invoke("--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertFalse(self.out_dir.exists())

    def test_all_combined_with_explicit_ids_exits_2(self):
        """'all' alongside explicit ids is a usage error (the literal selects every UC on its own)."""
        result = self._invoke("all", _PLACE, "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("all", result.output)
        self.assertFalse(self.out_dir.exists())

    def test_explicit_missing_id_exits_2(self):
        """(f) an explicitly requested id missing on disk → exit 2 (the requested artifact cannot be
        produced), naming the id, no out dir."""
        result = self._invoke(_MISSING, "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn(_MISSING, result.output)
        self.assertIn("missing on disk", result.output)
        self.assertFalse(self.out_dir.exists())

    def test_explicit_broken_id_exits_2_and_reports_the_parse_error(self):
        """(f) an explicitly requested existing-but-broken id → exit 2 (render error) with the parse
        error reported — the requested artifact cannot be produced, no out dir."""
        result = self._invoke(_BROKEN, "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn(_BROKEN, result.output)
        self.assertIn("fails to parse (render error)", result.output)
        self.assertFalse(self.out_dir.exists())

    def test_healthy_plus_missing_ids_reports_the_missing_one(self):
        """A healthy id alongside a missing one still exits 2 (the requested set cannot be fully
        produced), naming the missing id, no out dir."""
        result = self._invoke(_PLACE, _MISSING, "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn(_MISSING, result.output)
        self.assertFalse(self.out_dir.exists())


if __name__ == "__main__":
    unittest.main()
