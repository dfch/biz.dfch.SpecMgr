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

"""Docker-dependent grader tests (skipped when Docker is missing, ACC-006).

These run the pinned Structurizr CLI image over the committed fixture
workspaces and assert that the live CLI facts match the pre-exported
fixtures: the same exit codes and a JSON-equivalent export. They need
Docker (no model call) and are the live half of the ACC-006 proof; the
pure half is `test_graders.py`.
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from c4_skills import pins

from .conftest import FIXTURES_DIR, docker_available

WORKSPACES = FIXTURES_DIR / "workspaces"


def _skip_if_no_docker(testcase: unittest.TestCase) -> None:
    if not docker_available():
        testcase.skipTest("Docker is not available; the CLI grader tests are skipped (ACC-006)")


def _run_cli(workdir: Path, args: list[str]) -> tuple[int, str]:
    # Mirrors c4_skills.graders._run_cli, including the Phase 110
    # `--network none` (the CLI image needs no network: these four tests
    # are the live proof that it works).
    from c4_skills.preflight import host_user_flags

    cmd = [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        *host_user_flags(),
        "-v",
        f"{workdir}:/w",
        "-w",
        "/w",
        pins.STRUCTURIZR_CLI_IMAGE,
        *args,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # noqa: S603 -- pinned image
    return proc.returncode, (proc.stderr or "") + (proc.stdout or "")


@unittest.skipUnless(shutil.which("docker") is not None, "docker CLI missing")
class TestCliOverFixtures(unittest.TestCase):
    def setUp(self) -> None:
        _skip_if_no_docker(self)
        self._tmp = tempfile.TemporaryDirectory(prefix="c4eval-cli-")
        self.addCleanup(lambda: self._tmp.cleanup())
        self.tmp = Path(self._tmp.name)

    def _stage(self, name: str) -> Path:
        workdir = self.tmp / name
        workdir.mkdir()
        shutil.copy(WORKSPACES / name / "workspace.dsl", workdir / "workspace.dsl")
        return workdir

    def test_good_workspace_cli_matches_preexported_fixture(self) -> None:
        workdir = self._stage("good")

        validate_rc, _ = _run_cli(workdir, ["validate", "-w", "workspace.dsl"])
        export_rc, _ = _run_cli(workdir, ["export", "-w", "workspace.dsl", "-f", "json", "-o", "/w/out"])

        self.assertEqual(validate_rc, 0)
        self.assertEqual(export_rc, 0)
        live = json.loads((workdir / "out" / "workspace.json").read_text(encoding="utf-8"))
        expected = json.loads((WORKSPACES / "good" / "export.json").read_text(encoding="utf-8"))
        self.assertEqual(live, expected)

    def test_weak_workspace_cli_is_valid_but_thin(self) -> None:
        workdir = self._stage("weak")

        validate_rc, _ = _run_cli(workdir, ["validate", "-w", "workspace.dsl"])
        export_rc, _ = _run_cli(workdir, ["export", "-w", "workspace.dsl", "-f", "json", "-o", "/w/out"])

        self.assertEqual(validate_rc, 0)
        self.assertEqual(export_rc, 0)
        live = json.loads((workdir / "out" / "workspace.json").read_text(encoding="utf-8"))
        expected = json.loads((WORKSPACES / "weak" / "export.json").read_text(encoding="utf-8"))
        self.assertEqual(live, expected)

    def test_bad_workspace_cli_rejects(self) -> None:
        workdir = self._stage("bad")

        validate_rc, validate_out = _run_cli(workdir, ["validate", "-w", "workspace.dsl"])
        export_rc, _ = _run_cli(workdir, ["export", "-w", "workspace.dsl", "-f", "json", "-o", "/w/out"])

        self.assertNotEqual(validate_rc, 0)
        self.assertNotEqual(export_rc, 0)
        self.assertIn("ERROR", validate_out)

    def test_fixdsl_seed_workspace_cli_rejects(self) -> None:
        # the Phase 120 fix-dsl seed must fail the pinned CLI's `validate`
        # (the known-bad half of ACC-006 for the fix-dsl case; verified at
        # case creation, Task 120.100)
        workdir = self._stage("fixdsl-seed")

        validate_rc, validate_out = _run_cli(workdir, ["validate", "-w", "workspace.dsl"])
        export_rc, _ = _run_cli(workdir, ["export", "-w", "workspace.dsl", "-f", "json", "-o", "/w/out"])

        self.assertNotEqual(validate_rc, 0)
        self.assertNotEqual(export_rc, 0)
        self.assertIn("ERROR", validate_out)

    def test_heldout_dsl_seed_workspace_cli_rejects(self) -> None:
        workdir = self._stage("heldout-dsl-seed")

        validate_rc, validate_out = _run_cli(workdir, ["validate", "-w", "workspace.dsl"])
        export_rc, _ = _run_cli(workdir, ["export", "-w", "workspace.dsl", "-f", "json", "-o", "/w/out"])

        self.assertNotEqual(validate_rc, 0)
        self.assertNotEqual(export_rc, 0)
        self.assertIn("ERROR", validate_out)

    def test_fixdsl_fixed_workspace_cli_matches_preexported_fixture(self) -> None:
        # the Phase 120 known-good fixed reference: valid, and its live
        # export is JSON-equivalent to the committed pre-exported fixture
        workdir = self._stage("fixdsl-fixed")

        validate_rc, _ = _run_cli(workdir, ["validate", "-w", "workspace.dsl"])
        export_rc, _ = _run_cli(workdir, ["export", "-w", "workspace.dsl", "-f", "json", "-o", "/w/out"])

        self.assertEqual(validate_rc, 0)
        self.assertEqual(export_rc, 0)
        live = json.loads((workdir / "out" / "workspace.json").read_text(encoding="utf-8"))
        expected = json.loads((WORKSPACES / "fixdsl-fixed" / "export.json").read_text(encoding="utf-8"))
        self.assertEqual(live, expected)

    def test_heldout_dsl_fixed_workspace_cli_matches_preexported_fixture(self) -> None:
        workdir = self._stage("heldout-dsl-fixed")

        validate_rc, _ = _run_cli(workdir, ["validate", "-w", "workspace.dsl"])
        export_rc, _ = _run_cli(workdir, ["export", "-w", "workspace.dsl", "-f", "json", "-o", "/w/out"])

        self.assertEqual(validate_rc, 0)
        self.assertEqual(export_rc, 0)
        live = json.loads((workdir / "out" / "workspace.json").read_text(encoding="utf-8"))
        expected = json.loads((WORKSPACES / "heldout-dsl-fixed" / "export.json").read_text(encoding="utf-8"))
        self.assertEqual(live, expected)

    def test_cli_image_matches_the_pin(self) -> None:
        proc = subprocess.run(  # noqa: S603 -- pinned image
            ["docker", "run", "--rm", pins.STRUCTURIZR_CLI_IMAGE, "version"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(proc.returncode, 0)
        # the CLI reports `structurizr: <release>` on its stdout (the tag's
        # distro suffix, e.g. `-noble`, is not part of the release)
        tag = pins.STRUCTURIZR_CLI_IMAGE.rsplit(":", 1)[1]
        release = tag.split("-", 1)[0]
        self.assertIn(f"structurizr: {release}", proc.stdout)


if __name__ == "__main__":
    unittest.main()
