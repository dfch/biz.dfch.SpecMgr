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

"""Pins, cache and report machinery tests (no model call, no Docker)."""

import json
import tempfile
import unittest
from pathlib import Path

from c4_skills import pins, report
from c4_skills.cache import CacheKey, ResultCache


class TestVersionTuple(unittest.TestCase):
    def test_version_tuple_is_stable_and_sorted(self) -> None:
        first = pins.version_tuple()
        second = pins.version_tuple()

        self.assertEqual(first, second)
        self.assertEqual(list(first.keys()), sorted(first.keys()))
        json.dumps(first, sort_keys=True, separators=(",", ":"))  # must be canonical-JSON-safe

    def test_version_tuple_hash_is_a_stable_sha256(self) -> None:
        expected_length = 64

        sut = pins.version_tuple_hash

        first = sut()
        second = sut()

        self.assertEqual(first, second)
        self.assertEqual(len(first), expected_length)
        int(first, 16)  # must be lowercase hex

    def test_version_tuple_carries_the_pins(self) -> None:
        sut = pins.version_tuple

        result = sut()

        self.assertEqual(result["opencode_image"], pins.OPENCODE_IMAGE)
        self.assertEqual(result["opencode_image_digest"], pins.OPENCODE_IMAGE_DIGEST)
        self.assertEqual(result["structurizr_mcp_image"], pins.STRUCTURIZR_MCP_IMAGE)
        self.assertEqual(result["structurizr_cli_image"], pins.STRUCTURIZR_CLI_IMAGE)
        self.assertEqual(result["model_id"], pins.MODEL_ID)
        self.assertEqual(result["provider_id"], pins.PROVIDER_ID)
        self.assertEqual(result["upstream_sha"], pins.UPSTREAM_SHA_PIN)
        self.assertEqual(result["sampling_parameters"], dict(pins.SAMPLING_PARAMETERS))
        self.assertEqual(result["trial_timeout_s"], pins.TRIAL_TIMEOUT_S)


class TestSkillVariantHash(unittest.TestCase):
    def test_empty_set_is_the_none_condition_hash(self) -> None:
        sut = pins.skill_variant_hash

        result = sut([])

        self.assertEqual(len(result), 64)
        self.assertEqual(result, pins.skill_variant_hash([]))

    def test_content_order_does_not_matter(self) -> None:
        files_a = [("skills/x/SKILL.md", b"one"), ("skills/y/SKILL.md", b"two")]
        files_b = [("skills/y/SKILL.md", b"two"), ("skills/x/SKILL.md", b"one")]

        sut = pins.skill_variant_hash

        self.assertEqual(sut(files_a), sut(files_b))

    def test_content_change_changes_the_hash(self) -> None:
        sut = pins.skill_variant_hash

        first = sut([("skills/x/SKILL.md", b"one")])
        second = sut([("skills/x/SKILL.md", b"one!")])

        self.assertNotEqual(first, second)

    def test_path_change_changes_the_hash(self) -> None:
        sut = pins.skill_variant_hash

        first = sut([("skills/x/SKILL.md", b"one")])
        second = sut([("skills/y/SKILL.md", b"one")])

        self.assertNotEqual(first, second)


class TestResultCache(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="c4eval-cache-")
        self.addCleanup(lambda: self._tmp.cleanup())
        self.root = Path(self._tmp.name)

    def _key(self, **overrides: object) -> CacheKey:
        base: dict[str, object] = {
            "case_id": "smoke-create-system",
            "condition": pins.CONDITION_NONE,
            "grader_hash": "g" * 64,
            "skill_variant_hash": "s" * 64,
        }
        base.update(overrides)
        assert isinstance(base["case_id"], str)
        assert isinstance(base["condition"], str)
        assert isinstance(base["grader_hash"], str)
        assert isinstance(base["skill_variant_hash"], str)
        return CacheKey(
            case_id=base["case_id"],
            condition=base["condition"],
            version_tuple_hash=pins.version_tuple_hash(),
            grader_hash=base["grader_hash"],
            skill_variant_hash=base["skill_variant_hash"],
        )

    def test_miss_then_hit_then_key_mismatch_miss(self) -> None:
        cache = ResultCache(self.root)
        key = self._key()
        trial = {"plan": {"case_id": key.case_id, "condition": key.condition, "k_index": 0}, "passed": True}

        self.assertIsNone(cache.get(key))
        cache.put(key, [trial])
        hit = cache.get(key)
        self.assertIsNotNone(hit)
        assert hit is not None
        self.assertEqual(hit["trials"], [trial])

        drifted = self._key(grader_hash="h" * 64)
        self.assertIsNone(cache.get(drifted))

    def test_skill_condition_is_not_cacheable(self) -> None:
        with self.assertRaises(AssertionError):
            CacheKey.make("case", pins.CONDITION_SKILL, "g" * 64, "s" * 64)


class TestReportFigures(unittest.TestCase):
    def _run_record(self) -> dict:
        def trial(
            case_id: str,
            condition: str,
            k_index: int,
            passed: bool,
            gates: list[dict],
            wall: float | None,
            cached: bool = False,
        ) -> dict:
            return {
                "plan": {"case_id": case_id, "condition": condition, "k_index": k_index},
                "passed": passed,
                "gates": gates,
                "wall_time_s": wall,
                "cached": cached,
                "timeout": False,
                "contended": False,
            }

        gates_ok = [{"name": "dsl_written", "passed": True, "detail": ""}]
        gates_bad = [{"name": "dsl_written", "passed": False, "detail": "missing"}]
        return {
            "run_id": "unit-run",
            "label": "unit",
            "k": 2,
            "seed": 7,
            "cases": ["smoke-create-system"],
            "conditions": [pins.CONDITION_NONE, pins.CONDITION_UPSTREAM],
            "version_tuple_hash": pins.version_tuple_hash(),
            "trials": [
                trial("smoke-create-system", pins.CONDITION_NONE, 0, True, gates_ok, 600.0),
                trial("smoke-create-system", pins.CONDITION_NONE, 1, False, gates_bad, 700.0),
                trial("smoke-create-system", pins.CONDITION_UPSTREAM, 0, True, gates_ok, 650.0),
                trial("smoke-create-system", pins.CONDITION_UPSTREAM, 1, True, gates_ok, 500.0),
            ],
        }

    def test_report_figures_for_two_condition_run(self) -> None:
        run = self._run_record()
        preflight = {"ok": True, "problems": []}

        sut = report.build_report_input

        result = sut(run, preflight, None, pins.CONDITION_UPSTREAM)

        self.assertEqual(result["per_condition"][pins.CONDITION_NONE]["pass_rate"], 0.5)
        self.assertEqual(result["per_condition"][pins.CONDITION_UPSTREAM]["pass_rate"], 1.0)
        self.assertEqual(result["per_condition"][pins.CONDITION_NONE]["gate_failures"], {"dsl_written": 1})
        self.assertIsNone(result["skill_margins"])
        self.assertIsNotNone(result["cost_estimate"])
        assert result["cost_estimate"] is not None
        self.assertEqual(result["cost_estimate"]["measured_trials"], 4)
        self.assertEqual(result["cost_estimate"]["full_run_trials"], 90)

    def test_report_md_renders_without_skill_condition(self) -> None:
        run = self._run_record()

        sut = report.render_report_md

        result = sut(report.build_report_input(run, None, None, pins.CONDITION_UPSTREAM))

        self.assertIn("# Run report: unit-run", result)
        self.assertIn("## Pass rates", result)
        self.assertIn("## Gate margins", result)
        self.assertIn("No `skill` condition in this run", result)
        self.assertIn("## Cost estimate", result)

    def test_write_report_round_trips(self) -> None:
        run = self._run_record()
        with tempfile.TemporaryDirectory(prefix="c4eval-report-") as tmp:
            results_dir = Path(tmp)
            (results_dir / "run.json").write_text(json.dumps(run), encoding="utf-8")

            sut = report.build_and_write

            result = sut(results_dir)

            self.assertEqual(result["run_id"], "unit-run")
            self.assertTrue((results_dir / "report.md").is_file())
            self.assertTrue((results_dir / "report.json").is_file())


if __name__ == "__main__":
    unittest.main()
