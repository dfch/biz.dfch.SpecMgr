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

import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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

    def test_version_tuple_hash_matches_the_pinned_golden(self) -> None:
        # The golden of the Phase 110 egress-control change (it added the
        # `network_mode` pin; the Phase 100 golden was
        # 0de1ba9850e9d7e426a2f12a852cf17d25b2f2f5d0d12f528ce3b4cb2395a7b4).
        # A change here invalidates every cached baseline by design --
        # update this literal (computed, never guessed) when the tuple
        # legitimately changes.
        sut = pins.version_tuple_hash

        self.assertEqual(sut(), "f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662")

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
        self.assertEqual(result["network_mode"], pins.NETWORK_MODE)
        self.assertEqual(result["network_mode"], "internal-bridge")


class TestVllmEndpointHelpers(unittest.TestCase):
    """The forwarder's bind/target facts derived from the pinned endpoint."""

    def test_vllm_host_and_port_match_the_pin(self) -> None:
        self.assertEqual(pins.vllm_host(), "127.0.0.1")
        self.assertEqual(pins.vllm_host_port(), 8081)
        # the helpers and the endpoint stay in sync (one source of truth)
        self.assertIn(f":{pins.vllm_host_port()}/v1", pins.VLLM_ENDPOINT)
        self.assertIn(pins.vllm_host(), pins.VLLM_ENDPOINT)


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

    def test_get_reason_reports_the_miss_kind(self) -> None:
        cache = ResultCache(self.root)
        key = self._key()
        trial = {"plan": {"case_id": key.case_id, "condition": key.condition, "k_index": 0}, "passed": True}

        self.assertEqual(cache.get_reason(key), "miss:file-absent")
        cache.put(key, [trial])
        self.assertEqual(cache.get_reason(key), "hit")

        drifted = self._key(grader_hash="h" * 64)
        self.assertEqual(cache.get_reason(drifted), "miss:key-mismatch")

        other = self._key(case_id="another-case")
        self.assertEqual(cache.get_reason(other), "miss:file-absent")

    def test_get_reason_reports_an_unparseable_file(self) -> None:
        cache = ResultCache(self.root)
        key = self._key()
        cache.root.mkdir(parents=True, exist_ok=True)
        (cache.root / "smoke-create-system.none.json").write_text("{ not json", encoding="utf-8")

        self.assertEqual(cache.get_reason(key), "miss:file-unparseable")
        self.assertIsNone(cache.get(key))


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


_GOLDEN_VERSION_TUPLE_HASH = "f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662"


def _environ_without_overrides() -> dict[str, str]:
    """The current environment minus every C4EVAL_* pin variable."""
    result = {k: v for k, v in os.environ.items() if k not in pins.PIN_OVERRIDE_ENV.values()}
    return result


class TestPinOverrideParsing(unittest.TestCase):
    """Task 190.150 (I4): the C4EVAL_* override parsing (pure)."""

    def test_nothing_set_means_no_override(self) -> None:
        result = pins.parse_pin_overrides({"PATH": "/usr/bin"})

        self.assertEqual(result, ({}, []))

    def test_empty_and_blank_values_are_unset(self) -> None:
        result = pins.parse_pin_overrides({"C4EVAL_MODEL_ID": "", "C4EVAL_PROVIDER_ID": "   "})

        self.assertEqual(result, ({}, []))

    def test_valid_values_are_applied_and_stripped(self) -> None:
        environ = {
            "C4EVAL_VLLM_ENDPOINT": " http://10.0.0.7:8000/v1 ",
            "C4EVAL_VLLM_METRICS_URL": "http://10.0.0.7:8000/metrics",
            "C4EVAL_MODEL_ID": "org/other-model-7b",
            "C4EVAL_PROVIDER_ID": "vllm-sys1",
        }

        overrides, errors = pins.parse_pin_overrides(environ)

        self.assertEqual(errors, [])
        self.assertEqual(
            overrides,
            {
                "MODEL_ID": "org/other-model-7b",
                "PROVIDER_ID": "vllm-sys1",
                "VLLM_ENDPOINT": "http://10.0.0.7:8000/v1",
                "VLLM_METRICS_URL": "http://10.0.0.7:8000/metrics",
            },
        )

    def test_invalid_values_are_reported_and_not_applied(self) -> None:
        environ = {
            "C4EVAL_VLLM_ENDPOINT": "https://host/v1",  # no port, not http
            "C4EVAL_PROVIDER_ID": "a/b",  # a provider id carries no slash
            "C4EVAL_MODEL_ID": "ok-model",
        }

        overrides, errors = pins.parse_pin_overrides(environ)

        self.assertEqual(overrides, {"MODEL_ID": "ok-model"})
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("C4EVAL_VLLM_ENDPOINT" in e for e in errors))
        self.assertTrue(any("C4EVAL_PROVIDER_ID" in e for e in errors))


class TestPinOverridesInEffect(unittest.TestCase):
    """Task 190.150 (I4): an override moves the pin and the version tuple; no
    override keeps the pinned defaults and the golden tuple hash."""

    def tearDown(self) -> None:
        with mock.patch.dict(os.environ, _environ_without_overrides(), clear=True):
            importlib.reload(pins)

    def test_defaults_and_golden_hash_when_nothing_is_set(self) -> None:
        with mock.patch.dict(os.environ, _environ_without_overrides(), clear=True):
            importlib.reload(pins)

        self.assertEqual(pins.PIN_OVERRIDES, {})
        self.assertEqual(pins.VLLM_ENDPOINT, "http://127.0.0.1:8081/v1")
        self.assertEqual(pins.VLLM_METRICS_URL, "http://127.0.0.1:8081/metrics")
        self.assertEqual(pins.MODEL_ID, "qwen3.8-27b-bf16-896k")
        self.assertEqual(pins.PROVIDER_ID, "vllm-sys0")
        self.assertNotIn("pin_overrides", pins.version_tuple())
        self.assertEqual(pins.version_tuple_hash(), _GOLDEN_VERSION_TUPLE_HASH)

    def test_an_override_moves_the_pin_and_the_version_tuple(self) -> None:
        environ = _environ_without_overrides() | {"C4EVAL_MODEL_ID": "other-model", "C4EVAL_PROVIDER_ID": "vllm-x"}
        with mock.patch.dict(os.environ, environ, clear=True):
            importlib.reload(pins)

        self.assertEqual(pins.MODEL_ID, "other-model")
        self.assertEqual(pins.PROVIDER_ID, "vllm-x")
        result = pins.version_tuple()
        self.assertEqual(result["model_id"], "other-model")
        self.assertEqual(result["pin_overrides"], {"MODEL_ID": "other-model", "PROVIDER_ID": "vllm-x"})
        self.assertNotEqual(pins.version_tuple_hash(), _GOLDEN_VERSION_TUPLE_HASH)

    def test_a_metrics_url_override_alone_still_moves_the_version_tuple(self) -> None:
        # the metrics URL is no tuple field of its own; the recorded
        # `pin_overrides` block makes every override visible in the hash
        environ = _environ_without_overrides() | {"C4EVAL_VLLM_METRICS_URL": "http://127.0.0.1:9090/metrics"}
        with mock.patch.dict(os.environ, environ, clear=True):
            importlib.reload(pins)

        self.assertEqual(pins.VLLM_METRICS_URL, "http://127.0.0.1:9090/metrics")
        self.assertNotEqual(pins.version_tuple_hash(), _GOLDEN_VERSION_TUPLE_HASH)

    def test_an_endpoint_override_moves_the_forwarder_host_and_port(self) -> None:
        environ = _environ_without_overrides() | {"C4EVAL_VLLM_ENDPOINT": "http://10.1.2.3:8000/v1"}
        with mock.patch.dict(os.environ, environ, clear=True):
            importlib.reload(pins)

        self.assertEqual(pins.vllm_host(), "10.1.2.3")
        self.assertEqual(pins.vllm_host_port(), 8000)


class TestSourceHashIsCheckoutPathIndependent(unittest.TestCase):
    """Task 190.120 (G3): the grader hash folds in relative paths only."""

    def _tree(self, root: Path) -> list[str]:
        files = {"c4_skills/graders.py": b"GATES = 1\n", "c4_skills/cases/__init__.py": b"CASES = {}\n"}
        paths: list[str] = []
        for rel, content in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            paths.append(str(path))
        return paths

    def test_same_tree_under_two_absolute_roots_hashes_equally(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c4eval-a-") as a, tempfile.TemporaryDirectory(prefix="c4eval-b-") as b:
            root_a = Path(a) / "one" / "evals" / "c4-skills"
            root_b = Path(b) / "elsewhere" / "deeper" / "evals" / "c4-skills"
            paths_a = self._tree(root_a)
            paths_b = self._tree(root_b)

            sut = pins.source_hash

            first = sut(paths_a, root=root_a)
            second = sut(list(reversed(paths_b)), root=root_b)

            self.assertEqual(first, second)

    def test_content_change_changes_the_hash(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c4eval-c-") as c:
            root = Path(c)
            paths = self._tree(root)
            before = pins.source_hash(paths, root=root)
            (root / "c4_skills" / "graders.py").write_bytes(b"GATES = 2\n")

            after = pins.source_hash(paths, root=root)

            self.assertNotEqual(before, after)

    def test_a_path_outside_the_root_is_a_precondition_failure(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c4eval-d-") as d, tempfile.TemporaryDirectory(prefix="c4eval-e-") as e:
            paths = self._tree(Path(d))

            with self.assertRaises(AssertionError):
                pins.source_hash(paths, root=Path(e))

    def test_the_default_root_is_the_harness_root(self) -> None:
        from c4_skills.runner import grader_source_paths

        paths = [str(path) for path in grader_source_paths()]

        self.assertEqual(pins.source_hash(paths), pins.source_hash(paths, root=pins.HARNESS_ROOT))


class TestReportRecordsTheHashes(unittest.TestCase):
    """Task 190.120 (G3): report.json/report.md carry the recorded hashes."""

    def test_recorded_hashes_are_carried_into_the_report(self) -> None:
        run = {
            "run_id": "r",
            "cases": ["c"],
            "conditions": [pins.CONDITION_NONE],
            "version_tuple_hash": "v" * 64,
            "grader_hash": "g" * 64,
            "skill_variant_hash": None,
            "trials": [{"plan": {"case_id": "c", "condition": pins.CONDITION_NONE, "k_index": 0}, "passed": True}],
        }

        result = report.build_report_input(run, None, None, pins.CONDITION_UPSTREAM)

        self.assertEqual(result["grader_hash"], "g" * 64)
        self.assertEqual(result["version_tuple_hash"], "v" * 64)
        self.assertIsNone(result["skill_variant_hash"])
        self.assertIn(f"Grader hash: `{'g' * 64}`", report.render_report_md(result))

    def test_a_committed_run_without_grader_hash_reports_null(self) -> None:
        # the committed p160 cumulative run predates the grader_hash field;
        # it is only read here (the report goes to a temp dir, never into
        # the committed run dir)
        results_dir = pins.HARNESS_ROOT / "results" / "p160-cumulative-2026-11-22T094832Z"
        if not (results_dir / "run.json").is_file():
            self.skipTest("committed p160 run not present")
        with tempfile.TemporaryDirectory(prefix="c4eval-p160-") as tmp:
            result = report.build_and_write(results_dir, out_dir=Path(tmp))

            self.assertIsNone(result["grader_hash"])
            self.assertIn("Grader hash: `null`", (Path(tmp) / "report.md").read_text(encoding="utf-8"))
            on_disk = json.loads((Path(tmp) / "report.json").read_text(encoding="utf-8"))
            self.assertIsNone(on_disk["grader_hash"])


def _trial(case_id: str, condition: str, k_index: int, passed: bool, installed: list[str], loaded: list[str]) -> dict:
    """One synthetic trial record for the trigger-table / baseline tests."""
    return {
        "plan": {"case_id": case_id, "condition": condition, "k_index": k_index},
        "passed": passed,
        "skills_installed": installed,
        "metrics": {"skills_loaded": loaded},
    }


class TestSkillTriggerTable(unittest.TestCase):
    """Task 190.130 (G1): per case, the trials each mounted skill loaded in."""

    BUNDLE = ["dsl-authoring", "validate-loop"]

    def _run(self) -> dict:
        skill = pins.CONDITION_SKILL
        return {
            "run_id": "trig",
            "cases": ["fix-dsl", "no-trigger"],
            "conditions": [pins.CONDITION_NONE, skill],
            "trials": [
                _trial("fix-dsl", skill, 0, False, self.BUNDLE, ["validate-loop"]),
                _trial("fix-dsl", skill, 1, True, self.BUNDLE, ["validate-loop", "dsl-authoring"]),
                _trial("fix-dsl", skill, 2, False, self.BUNDLE, ["validate-loop", "not-mounted"]),
                _trial("no-trigger", skill, 0, True, self.BUNDLE, []),
                _trial("fix-dsl", pins.CONDITION_NONE, 0, False, [], []),
            ],
        }

    def test_counts_loads_per_case_and_mounted_skill(self) -> None:
        sut = report.skill_trigger_table

        result = sut(self._run(), None)

        assert result is not None
        self.assertEqual(result["skills"], self.BUNDLE)
        self.assertEqual(
            result["per_case"]["fix-dsl"], {"trials": 3, "loaded": {"dsl-authoring": 1, "validate-loop": 3}}
        )
        self.assertEqual(
            result["per_case"]["no-trigger"], {"trials": 1, "loaded": {"dsl-authoring": 0, "validate-loop": 0}}
        )

    def test_the_case_filter_applies(self) -> None:
        result = report.skill_trigger_table(self._run(), ["no-trigger"])

        assert result is not None
        self.assertEqual(list(result["per_case"]), ["no-trigger"])

    def test_none_without_skill_trials(self) -> None:
        run = {"trials": [_trial("fix-dsl", pins.CONDITION_NONE, 0, False, [], [])]}

        self.assertIsNone(report.skill_trigger_table(run, None))

    def test_the_table_is_rendered(self) -> None:
        payload = report.build_report_input(self._run(), None, None, pins.CONDITION_NONE)

        result = report.render_report_md(payload)

        self.assertIn("## Skill trigger table", result)
        self.assertIn("| fix-dsl | 3 | 1/3 | 3/3 |", result)


class TestBaselineRegression(unittest.TestCase):
    """Task 190.130 (G2): flag a case whose skill passes dropped by >= 2 trials."""

    def _run(self, run_id: str, passes: dict[str, int], k: int = 5) -> dict:
        trials = [
            _trial(case_id, pins.CONDITION_SKILL, i, i < n, [], []) for case_id, n in passes.items() for i in range(k)
        ]
        return {"run_id": run_id, "cases": list(passes), "conditions": [pins.CONDITION_SKILL], "trials": trials}

    def test_flags_a_two_trial_drop_and_not_a_one_trial_drop(self) -> None:
        baseline = self._run("base", {"fix-dsl": 5, "create-system": 2, "mcp-limits": 0})
        current = self._run("cur", {"fix-dsl": 1, "create-system": 1, "mcp-limits": 3, "design-views": 0})

        sut = report.baseline_regression

        result = sut(current, baseline, None)

        self.assertEqual(result["flagged_cases"], ["fix-dsl"])
        self.assertEqual(result["per_case"]["fix-dsl"]["delta"], -4)
        self.assertFalse(result["per_case"]["create-system"]["flagged"])
        self.assertNotIn("design-views", result["per_case"])  # only cases present in both runs
        self.assertEqual(result["baseline_run_id"], "base")

    def test_exactly_two_trials_lower_is_flagged(self) -> None:
        result = report.baseline_regression(self._run("c", {"x": 3}), self._run("b", {"x": 5}), None)

        self.assertEqual(result["flagged_cases"], ["x"])

    def test_build_and_write_reads_the_baseline_dir(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c4eval-g2-") as tmp:
            current_dir = Path(tmp) / "current"
            baseline_dir = Path(tmp) / "baseline"
            out_dir = Path(tmp) / "out"
            for directory, run in (
                (current_dir, self._run("cur", {"fix-dsl": 1})),
                (baseline_dir, self._run("base", {"fix-dsl": 5})),
            ):
                directory.mkdir()
                (directory / "run.json").write_text(json.dumps(run), encoding="utf-8")

            result = report.build_and_write(current_dir, baseline_dir=baseline_dir, out_dir=out_dir)

            self.assertEqual(result["baseline_regression"]["flagged_cases"], ["fix-dsl"])
            self.assertFalse((current_dir / "report.md").exists())
            self.assertIn("Flagged: fix-dsl.", (out_dir / "report.md").read_text(encoding="utf-8"))

    def test_no_baseline_section_without_a_baseline(self) -> None:
        payload = report.build_report_input(self._run("cur", {"x": 1}), None, None, pins.CONDITION_NONE)

        self.assertIsNone(payload["baseline_regression"])
        self.assertNotIn("## Baseline regression check", report.render_report_md(payload))


if __name__ == "__main__":
    unittest.main()
