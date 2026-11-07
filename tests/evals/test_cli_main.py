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

"""The CLI exit-code contract tests (Phase 100 review cycle 1, fix I4).

`main` maps the documented failure shapes: `KeyError`/`ValueError`/
`AssertionError` are usage-shaped (exit 2), `RuntimeError`/`OSError` are
runtime-shaped (exit 1), any other exception type propagates as a raw
traceback (a harness bug, not a documented failure shape). These tests
need no Docker: the usage paths fail before any container call, and the
runtime/propagation paths mock `runner.run` at the CLI boundary.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from c4_skills.cli import main


class TestUsageErrorsReturnTwo(unittest.TestCase):
    def test_report_on_a_dir_without_run_json_returns_2(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c4eval-cli-") as tmp:
            result = main(["report", "--results-dir", tmp])

        self.assertEqual(result, 2)

    def test_run_with_k_zero_returns_2(self) -> None:
        result = main(["run", "--cases", "smoke-create-system", "--conditions", "none", "--k", "0"])

        self.assertEqual(result, 2)

    def test_run_with_an_unknown_case_returns_2(self) -> None:
        result = main(["run", "--cases", "no-such-case", "--conditions", "none"])

        self.assertEqual(result, 2)

    def test_run_with_the_skill_condition_but_no_skills_dir_returns_2(self) -> None:
        result = main(["run", "--cases", "smoke-create-system", "--conditions", "skill"])

        self.assertEqual(result, 2)

    def test_run_with_a_skills_dir_but_no_skill_condition_returns_2(self) -> None:
        result = main(
            [
                "run",
                "--cases",
                "smoke-create-system",
                "--conditions",
                "none",
                "--skills-dir",
                "/does/not/need/to/exist",
            ]
        )

        self.assertEqual(result, 2)


class TestRuntimeErrorsReturnOne(unittest.TestCase):
    def test_runner_runtime_error_returns_1(self) -> None:
        argv = ["run", "--cases", "smoke-create-system", "--conditions", "none", "--k", "1"]
        with tempfile.TemporaryDirectory(prefix="c4eval-cli-") as tmp:
            args = ["--results-dir", tmp, "--workroot", tmp, "--cache", tmp]
            with mock.patch("c4_skills.runner.run", side_effect=RuntimeError("sidecar failed")):
                result = main(argv + args)

        self.assertEqual(result, 1)


class TestUnexpectedExceptionsPropagate(unittest.TestCase):
    def test_harness_bug_stays_a_traceback(self) -> None:
        argv = ["run", "--cases", "smoke-create-system", "--conditions", "none", "--k", "1"]
        with tempfile.TemporaryDirectory(prefix="c4eval-cli-") as tmp:
            args = ["--results-dir", tmp, "--workroot", tmp, "--cache", tmp]
            with mock.patch("c4_skills.runner.run", side_effect=TypeError("a harness bug")):
                with self.assertRaises(TypeError):
                    main(argv + args)


class TestSkillsDirWiring(unittest.TestCase):
    def test_skills_dir_reaches_the_run_config(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c4eval-cli-") as tmp:
            root = Path(tmp)
            variant = root / "variant" / "structurizr-validate-loop"
            variant.mkdir(parents=True)
            (variant / "SKILL.md").write_text("# loop\n", encoding="utf-8")
            captured: dict = {}

            def fake_run(config) -> dict:
                captured["config"] = config
                return {}

            argv = [
                "run",
                "--cases",
                "smoke-create-system",
                "--conditions",
                "none,skill",
                "--k",
                "1",
                "--skills-dir",
                str(variant),
                "--results-dir",
                str(root / "results"),
                "--workroot",
                str(root / "work"),
                "--cache",
                str(root / "cache"),
            ]
            with (
                mock.patch("c4_skills.runner.run", side_effect=fake_run) as run_mock,
                mock.patch("c4_skills.report.build_and_write", return_value={"per_condition": {}}),
            ):
                result = main(argv)

        self.assertEqual(result, 0)
        self.assertTrue(run_mock.called)
        config = captured["config"]
        self.assertEqual(config.skills_dir, variant)
        self.assertEqual(config.conditions, ["none", "skill"])
        # Phase 110: the additive network_name field defaults to empty
        # (the run derives c4eval-<run_id> -- no CLI flag)
        self.assertEqual(config.network_name, "")


if __name__ == "__main__":
    unittest.main()
