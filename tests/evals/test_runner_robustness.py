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

"""Runner robustness tests: event-stream commit/capture, the skill variant.

Pure Python (no model call, no Docker): the container layer is mocked at
the `runner._run_opencode_container` boundary. Covers the Phase 100 review
cycle 1 fixes:

- D2: over-limit event streams stay in the gitignored work dir and are
  flagged in the trial record (never summarized, never deleted);
- I2: the captured stream is a single full `docker logs` after exit
  (the start-gap loss of a `docker logs -f --tail 0` is gone) and its
  first event type is cheaply checked;
- I3b: the TrialRecord carries the additive cache-reason and event-file
  fields and parses pre-existing (older-shape) records via defaults;
- I5: the `skill` condition takes a variant directory, hashes it with the
  existing content hash, and copies it into the trial work dir BEFORE the
  container starts.
"""

import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from c4_skills import pins
from c4_skills.graders import GraderInputs
from c4_skills.runner import (
    EVENT_FILE_COMMIT_LIMIT,
    TrialPlan,
    _capture_full_logs,
    _install_skills,
    _record_from_json,
    _stream_first_type,
    commit_event_stream,
    load_skill_source,
    run_trial,
)

MINIMAL_STREAM = (
    '{"type": "step_start", "part": {"type": "step-start"}, "timestamp": 1}\n{"type": "finish", "timestamp": 2}\n'
)


def _empty_inputs() -> GraderInputs:
    return GraderInputs(
        dsl_path=None,
        dsl_text=None,
        validate_rc=None,
        validate_stderr="no .dsl file in the work dir",
        export_json=None,
        export_rc=None,
        export_stderr="no .dsl file in the work dir",
        inspect_rc=None,
        inspect_findings=[],
    )


class TestCommitEventStream(unittest.TestCase):
    """D2: the commit decision over the captured stream."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="c4eval-commit-")
        self.addCleanup(lambda: self._tmp.cleanup())
        self.root = Path(self._tmp.name)
        self.results_dir = self.root / "results" / "run-x"
        self.source = self.root / "work" / "trial.events.ndjson"
        self.source.parent.mkdir(parents=True)
        self.dest = self.results_dir / "trials" / "case-a" / "none-k0.events.ndjson"

    def test_under_limit_stream_is_committed_with_relative_path(self) -> None:
        self.source.write_text(MINIMAL_STREAM, encoding="utf-8")

        sut = commit_event_stream

        result = sut(self.source, self.dest, self.results_dir)

        self.assertTrue(result.event_file_committed)
        self.assertEqual(result.event_file, "trials/case-a/none-k0.events.ndjson")
        self.assertEqual(result.event_file_bytes, len(MINIMAL_STREAM.encode("utf-8")))
        self.assertEqual(self.dest.read_text(encoding="utf-8"), MINIMAL_STREAM)

    def test_over_limit_stream_is_kept_flagged_and_not_committed(self) -> None:
        big = "x" * (EVENT_FILE_COMMIT_LIMIT + 1)
        self.source.write_text(big, encoding="utf-8")

        sut = commit_event_stream

        result = sut(self.source, self.dest, self.results_dir)

        self.assertFalse(result.event_file_committed)
        self.assertIsNone(result.event_file)
        self.assertEqual(result.event_file_bytes, EVENT_FILE_COMMIT_LIMIT + 1)
        self.assertFalse(self.dest.exists())
        # the stream stays in the gitignored work dir (debugging material)
        self.assertEqual(self.source.stat().st_size, EVENT_FILE_COMMIT_LIMIT + 1)

    def test_missing_stream_records_no_bytes(self) -> None:
        sut = commit_event_stream

        result = sut(self.source, self.dest, self.results_dir)

        self.assertFalse(result.event_file_committed)
        self.assertIsNone(result.event_file)
        self.assertIsNone(result.event_file_bytes)


class TestFullLogCapture(unittest.TestCase):
    """I2: the post-exit, non-following full capture."""

    def test_capture_writes_the_full_log_after_exit(self) -> None:
        captured: dict = {}

        def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess:
            if len(cmd) >= 2 and cmd[1] == "logs":
                file = kwargs.get("stdout")
                if isinstance(file, io.TextIOBase):
                    file.write("FULL-LOG-DATA")
            captured["cmd"] = cmd
            return subprocess.CompletedProcess(args=cmd, returncode=0)

        with tempfile.TemporaryDirectory(prefix="c4eval-logs-") as tmp:
            log_path = Path(tmp) / "stream.events.ndjson"

            with mock.patch("subprocess.run", side_effect=fake_run):
                _capture_full_logs("c4eval-trial-x", log_path)

            self.assertEqual(log_path.read_text(encoding="utf-8"), "FULL-LOG-DATA")
            # single, non-following `docker logs <name>` (no -f, no --tail)
            self.assertEqual(captured["cmd"][:3], ["docker", "logs", "c4eval-trial-x"])
            self.assertNotIn("-f", captured["cmd"])

    def test_capture_failure_leaves_an_empty_file_and_does_not_raise(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c4eval-logs-") as tmp:
            log_path = Path(tmp) / "stream.events.ndjson"

            with mock.patch("subprocess.run", side_effect=OSError("docker gone")):
                _capture_full_logs("c4eval-trial-x", log_path)

            self.assertTrue(log_path.is_file())
            self.assertEqual(log_path.read_text(encoding="utf-8"), "")


class TestStreamFirstType(unittest.TestCase):
    """I2: the cheap integrity check over the captured stream's first line."""

    def _first_type(self, text: str | None) -> str | None:
        with tempfile.TemporaryDirectory(prefix="c4eval-first-") as tmp:
            path = Path(tmp) / "stream.ndjson"
            if text is not None:
                path.write_text(text, encoding="utf-8")
            result = _stream_first_type(path)
            return result

    def test_step_start_stream_is_healthy(self) -> None:
        self.assertEqual(self._first_type(MINIMAL_STREAM), "step_start")

    def test_error_only_stream_is_healthy(self) -> None:
        # a container that dies before its first step emits a lone error
        # event (the smoke run 1 port collision did)
        self.assertEqual(self._first_type('{"type": "error", "error": {}}\n'), "error")

    def test_empty_and_malformed_streams_are_suspect(self) -> None:
        self.assertIsNone(self._first_type(""))
        self.assertIsNone(self._first_type(None))
        self.assertIsNone(self._first_type("not json at all\n"))
        self.assertIsNone(self._first_type("[1, 2, 3]\n"))


class TestTrialRecordShapes(unittest.TestCase):
    """I3b/D2: the additive record fields and the older-shape defaults."""

    def _old_shape_raw(self) -> dict:
        # the shape committed before the review cycle (no cache_reason /
        # event_file_bytes / event_file_committed keys)
        return {
            "plan": {"case_id": "case-a", "condition": "none", "k_index": 0},
            "run_id": "run-old",
            "workdir": "/w",
            "started_at": "2026-11-02T06:57:31Z",
            "finished_at": "2026-11-02T07:00:00Z",
            "wall_time_s": 150.0,
            "exit_code": 0,
            "timeout": False,
            "contended": False,
            "idle_wait_s": 1.0,
            "cached": True,
            "event_file": "trials/case-a/none-k0.events.ndjson",
            "gates": [],
            "passed": True,
            "metrics": {},
        }

    def test_old_shape_record_parses_with_defaults(self) -> None:
        sut = _record_from_json

        result = sut(self._old_shape_raw())

        self.assertEqual(result.cache_reason, "n/a")
        self.assertIsNone(result.event_file_bytes)
        self.assertTrue(result.event_file_committed)  # the old field carried a path
        self.assertEqual(result.event_file, "trials/case-a/none-k0.events.ndjson")

    def test_new_shape_fields_round_trip(self) -> None:
        raw = self._old_shape_raw()
        raw["cache_reason"] = "hit"
        raw["event_file_bytes"] = 42
        raw["event_file_committed"] = False
        raw["event_file"] = None

        sut = _record_from_json

        record = sut(raw)
        as_json = record.to_json()

        self.assertEqual(record.cache_reason, "hit")
        self.assertEqual(record.event_file_bytes, 42)
        self.assertFalse(record.event_file_committed)
        self.assertEqual(as_json["cache_reason"], "hit")
        self.assertEqual(as_json["event_file_bytes"], 42)
        self.assertEqual(as_json["event_file_committed"], False)


class TestSkillSource(unittest.TestCase):
    """I5: the skill variant directory (hash + verification)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="c4eval-skill-")
        self.addCleanup(lambda: self._tmp.cleanup())
        self.root = Path(self._tmp.name)
        skill_a = self.root / "structurizr-validate-loop"
        (skill_a / "refs").mkdir(parents=True)
        (skill_a / "SKILL.md").write_text("# validate loop\n", encoding="utf-8")
        (skill_a / "refs" / "limits.md").write_text("the MCP limits\n", encoding="utf-8")
        skill_b = self.root / "c4-modeling"
        skill_b.mkdir()
        (skill_b / "SKILL.md").write_text("# modeling\n", encoding="utf-8")

    def test_root_shape_lists_every_skill_folder_and_file(self) -> None:
        sut = load_skill_source

        source = sut(self.root)

        self.assertEqual(source.skills, ("c4-modeling", "structurizr-validate-loop"))
        rel_paths = [rel for rel, _ in source.files]
        self.assertIn("structurizr-validate-loop/SKILL.md", rel_paths)
        self.assertIn("structurizr-validate-loop/refs/limits.md", rel_paths)
        self.assertIn("c4-modeling/SKILL.md", rel_paths)
        self.assertEqual(source.skills_root, self.root.resolve())

    def test_single_folder_shape_hashes_equally_to_the_root_shape(self) -> None:
        sut = load_skill_source

        root_source = sut(self.root)
        single_source = sut(self.root / "structurizr-validate-loop")

        self.assertEqual(single_source.skills, ("structurizr-validate-loop",))
        root_subset = [f for f in root_source.files if f[0].startswith("structurizr-validate-loop/")]
        self.assertEqual(
            pins.skill_variant_hash(single_source.files),
            pins.skill_variant_hash(root_subset),
        )

    def test_content_change_changes_the_variant_hash(self) -> None:
        sut = load_skill_source

        first = pins.skill_variant_hash(sut(self.root).files)
        (self.root / "c4-modeling" / "SKILL.md").write_text("# modeling v2\n", encoding="utf-8")
        second = pins.skill_variant_hash(sut(self.root).files)

        self.assertNotEqual(first, second)

    def test_missing_dir_and_skillless_dir_are_usage_errors(self) -> None:
        sut = load_skill_source

        with self.assertRaises(ValueError):
            sut(self.root / "does-not-exist")
        empty = self.root / "empty"
        empty.mkdir()
        with self.assertRaises(ValueError):
            sut(empty)
        no_skill_md = self.root / "no-skill-md"
        (no_skill_md / "some-folder").mkdir(parents=True)
        (no_skill_md / "some-folder" / "README.md").write_text("no SKILL.md here\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            sut(no_skill_md)


class TestInstallSkills(unittest.TestCase):
    """I5: the per-condition install into the trial work dir."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="c4eval-install-")
        self.addCleanup(lambda: self._tmp.cleanup())
        self.root = Path(self._tmp.name)
        self.workdir = self.root / "work"
        self.workdir.mkdir()
        variant = self.root / "variant"
        (variant / "structurizr-validate-loop").mkdir(parents=True)
        (variant / "structurizr-validate-loop" / "SKILL.md").write_text("# loop\n", encoding="utf-8")
        self.source = load_skill_source(variant)

    def test_none_condition_installs_nothing(self) -> None:
        sut = _install_skills

        result = sut(self.workdir, pins.CONDITION_NONE, None)

        self.assertEqual(result, [])
        self.assertFalse((self.workdir / ".opencode").exists())

    def test_skill_condition_copies_the_variant_files(self) -> None:
        sut = _install_skills

        result = sut(self.workdir, pins.CONDITION_SKILL, None, self.source)

        self.assertEqual(result, ["structurizr-validate-loop"])
        installed = self.workdir / ".opencode" / "skills" / "structurizr-validate-loop" / "SKILL.md"
        self.assertEqual(installed.read_text(encoding="utf-8"), "# loop\n")

    def test_skill_condition_without_a_source_is_a_usage_error(self) -> None:
        sut = _install_skills

        with self.assertRaises(ValueError):
            sut(self.workdir, pins.CONDITION_SKILL, None)

    def test_upstream_condition_without_a_source_is_a_runtime_error(self) -> None:
        sut = _install_skills

        with self.assertRaises(RuntimeError):
            sut(self.workdir, pins.CONDITION_UPSTREAM, None)


class TestRunTrialSkillCondition(unittest.TestCase):
    """I5: the install happens BEFORE the container starts (mocked run)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="c4eval-runtrial-")
        self.addCleanup(lambda: self._tmp.cleanup())
        self.root = Path(self._tmp.name)
        self.workroot = self.root / "work"
        self.results_dir = self.root / "results" / "run-x"
        self.workroot.mkdir()
        self.results_dir.mkdir(parents=True)
        variant = self.root / "variant"
        (variant / "structurizr-validate-loop").mkdir(parents=True)
        (variant / "structurizr-validate-loop" / "SKILL.md").write_text("# loop\n", encoding="utf-8")
        self.source = load_skill_source(variant)
        self.captured: dict = {}

    def _fake_container(self, workdir, case, mcp_port, timeout_s, log_path, container_name):
        # at the moment the container "starts", record what the agent would
        # already see in its mounted work dir
        skill_md = workdir / ".opencode" / "skills" / "structurizr-validate-loop" / "SKILL.md"
        self.captured["skills_present_before_start"] = skill_md.is_file()
        self.captured["skill_bytes_before_start"] = skill_md.read_text(encoding="utf-8") if skill_md.is_file() else None
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(MINIMAL_STREAM, encoding="utf-8")
        return 0, False, 1.5

    def test_skills_are_copied_before_the_container_starts(self) -> None:
        plan = TrialPlan(case_id=pins.SMOKE_CASE, condition=pins.CONDITION_SKILL, k_index=0)
        with (
            mock.patch("c4_skills.preflight.wait_until_idle", return_value=(True, 0, 0.0)) as idle_mock,
            mock.patch("c4_skills.preflight.vllm_running_requests", return_value=0),
            mock.patch("c4_skills.runner._run_opencode_container", side_effect=self._fake_container),
            mock.patch("c4_skills.graders.collect_inputs", return_value=_empty_inputs()),
        ):
            record = run_trial(
                plan,
                run_id="run-x",
                workroot=self.workroot,
                results_dir=self.results_dir,
                mcp_port=12345,
                upstream=None,
                skill_source=self.source,
                cache_reason="n/a",
            )

        self.assertTrue(idle_mock.called)
        # the ordering fix: the variant is in the work dir before the
        # container step runs (the fake recorded it at call time)
        self.assertTrue(self.captured["skills_present_before_start"])
        self.assertEqual(self.captured["skill_bytes_before_start"], "# loop\n")
        # the record carries the committed stream + the cache reason
        self.assertEqual(record.event_file, "trials/smoke-create-system/skill-k0.events.ndjson")
        self.assertTrue(record.event_file_committed)
        self.assertEqual(record.cache_reason, "n/a")
        self.assertFalse(record.cached)
        # metrics were parsed from the captured stream (steps from the
        # minimal stream)
        self.assertEqual(record.metrics["steps"], 1)
        # the skill condition never passed without a workspace (gates fail)
        self.assertFalse(record.passed)


if __name__ == "__main__":
    unittest.main()
