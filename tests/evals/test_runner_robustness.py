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

import errno
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from c4_skills import pins, preflight, runner, sidecar
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
    run,
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

    def _fake_container(self, workdir, case, *, network, vllm_base_url, mcp_url, timeout_s, log_path, container_name):
        # at the moment the container "starts", record what the agent would
        # already see in its mounted work dir
        skill_md = workdir / ".opencode" / "skills" / "structurizr-validate-loop" / "SKILL.md"
        self.captured["skills_present_before_start"] = skill_md.is_file()
        self.captured["skill_bytes_before_start"] = skill_md.read_text(encoding="utf-8") if skill_md.is_file() else None
        self.captured["container_network"] = network
        self.captured["vllm_base_url"] = vllm_base_url
        self.captured["mcp_url"] = mcp_url
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
                network="c4eval-run-x",
                vllm_base_url="http://172.21.0.1:8081/v1",
                mcp_url="http://172.21.0.3:8181/mcp",
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
        # Phase 110: the trial container got the private network + the two
        # explicit endpoints (never a host mcp port)
        self.assertEqual(self.captured["container_network"], "c4eval-run-x")
        self.assertEqual(self.captured["vllm_base_url"], "http://172.21.0.1:8081/v1")
        self.assertEqual(self.captured["mcp_url"], "http://172.21.0.3:8181/mcp")


class TestNetworkHelpers(unittest.TestCase):
    """Phase 110: the per-run private network lifecycle (docker mocked)."""

    def test_network_name_is_derived_from_the_run_id(self) -> None:
        sut = runner.network_name_for

        self.assertEqual(sut("run-x"), "c4eval-run-x")
        self.assertEqual(sut("p110-prove-2026-11-03T162909Z"), "c4eval-p110-prove-2026-11-03T162909Z")

    def test_create_run_network_is_an_internal_bridge(self) -> None:
        captured: dict = {}

        def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess:
            captured["cmd"] = cmd
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        with mock.patch("subprocess.run", side_effect=fake_run):
            runner.create_run_network("c4eval-run-x")

        self.assertEqual(captured["cmd"], ["docker", "network", "create", "--internal", "c4eval-run-x"])

    def test_create_run_network_failure_raises(self) -> None:
        def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess:
            return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="exists already")

        with mock.patch("subprocess.run", side_effect=fake_run):
            with self.assertRaises(RuntimeError) as ctx:
                runner.create_run_network("c4eval-run-x")

        self.assertIn("exists already", str(ctx.exception))

    def test_remove_run_network_is_best_effort(self) -> None:
        # docker gone (OSError) or rc != 0: never raises (teardown context)
        with mock.patch("subprocess.run", side_effect=OSError("docker gone")):
            runner.remove_run_network("c4eval-run-x")

        def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess:
            return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="still in use")

        with mock.patch("subprocess.run", side_effect=fake_run):
            runner.remove_run_network("c4eval-run-x")

    def test_sweep_run_networks_removes_and_returns_the_names(self) -> None:
        def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess:
            if cmd[1:3] == ["network", "ls"]:
                return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="c4eval-old-run\n", stderr="")
            assert cmd[1:3] == ["network", "rm"]
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        with mock.patch("subprocess.run", side_effect=fake_run) as run_mock:
            result = runner.sweep_run_networks()

        self.assertEqual(result, ["c4eval-old-run"])
        self.assertEqual(run_mock.call_count, 2)
        self.assertEqual(run_mock.call_args.args[0][-1], "c4eval-old-run")

    def test_sweep_run_networks_never_raises_when_docker_is_gone(self) -> None:
        with mock.patch("subprocess.run", side_effect=OSError("docker gone")):
            self.assertEqual(runner.sweep_run_networks(), [])

    def test_network_gateway_ip_parses_the_inspect_answer(self) -> None:
        captured: dict = {}

        def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess:
            captured["cmd"] = cmd
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="172.21.0.1\n", stderr="")

        with mock.patch("subprocess.run", side_effect=fake_run):
            result = runner.network_gateway_ip("c4eval-run-x")

        self.assertEqual(result, "172.21.0.1")
        self.assertEqual(captured["cmd"][:2], ["docker", "network"])
        self.assertIn("c4eval-run-x", captured["cmd"])

    def test_network_gateway_ip_missing_is_a_runtime_error(self) -> None:
        def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="\n", stderr="")

        with mock.patch("subprocess.run", side_effect=fake_run):
            with self.assertRaises(RuntimeError) as ctx:
                runner.network_gateway_ip("c4eval-run-x")

        self.assertIn("no gateway", str(ctx.exception))


class TestVerifyDirectVllm(unittest.TestCase):
    """Option C: the STRICT verification of a direct (0.0.0.0-bound) vLLM.

    A permissive "something answers on 8081" is not acceptable: the probes
    must see the exact pinned version AND the pinned model id, from the
    host, on the gateway's vLLM port.
    """

    GATEWAY = "172.21.0.1"

    def _good_docs(self) -> dict[str, object]:
        return {
            f"http://{self.GATEWAY}:{pins.vllm_host_port()}/version": {"version": pins.VLLM_VERSION_PIN},
            f"http://{self.GATEWAY}:{pins.vllm_host_port()}/v1/models": {
                "object": "list",
                "data": [{"id": pins.MODEL_ID, "max_model_len": pins.MODEL_MAX_CONTEXT}],
            },
        }

    def _verify(self, docs: dict[str, object]):
        fetched: list[str] = []

        def fake_get_json(url: str, timeout_s: float = 5.0) -> object:
            fetched.append(url)
            return docs.get(url)

        with mock.patch("c4_skills.runner._gateway_http_json", side_effect=fake_get_json):
            runner._verify_direct_vllm(self.GATEWAY)
        return fetched

    def test_a_verified_server_passes_and_both_probes_run(self) -> None:
        fetched = self._verify(self._good_docs())

        self.assertEqual(
            fetched,
            [
                f"http://{self.GATEWAY}:{pins.vllm_host_port()}/version",
                f"http://{self.GATEWAY}:{pins.vllm_host_port()}/v1/models",
            ],
        )

    def test_a_wrong_version_is_a_pin_violation(self) -> None:
        docs = self._good_docs()
        docs[f"http://{self.GATEWAY}:{pins.vllm_host_port()}/version"] = {"version": "9.9.9"}

        with self.assertRaises(RuntimeError) as ctx:
            self._verify(docs)

        message = str(ctx.exception)
        self.assertIn("'9.9.9'", message)
        self.assertIn(pins.VLLM_VERSION_PIN, message)

    def test_an_unreachable_server_is_a_pin_violation(self) -> None:
        # no answer at all (the /version probe returns None)
        docs = self._good_docs()
        del docs[f"http://{self.GATEWAY}:{pins.vllm_host_port()}/version"]

        with self.assertRaises(RuntimeError) as ctx:
            self._verify(docs)

        self.assertIn("None", str(ctx.exception))

    def test_a_model_set_without_the_pin_is_a_pin_violation(self) -> None:
        docs = self._good_docs()
        docs[f"http://{self.GATEWAY}:{pins.vllm_host_port()}/v1/models"] = {
            "object": "list",
            "data": [{"id": "some-other-model"}],
        }

        with self.assertRaises(RuntimeError) as ctx:
            self._verify(docs)

        message = str(ctx.exception)
        self.assertIn(pins.MODEL_ID, message)
        self.assertIn("some-other-model", message)

    def test_non_json_answers_are_pin_violations(self) -> None:
        docs = self._good_docs()
        docs[f"http://{self.GATEWAY}:{pins.vllm_host_port()}/version"] = "not json at all"

        with self.assertRaises(RuntimeError):
            self._verify(docs)


class TestEstablishVllmAccess(unittest.TestCase):
    """Option C: the mode selection (forwarder preferred, verified direct fallback)."""

    GATEWAY = "172.21.0.1"

    def test_a_successful_bind_is_forwarder_mode(self) -> None:
        fake_handle = object()
        with (
            mock.patch("c4_skills.runner.forwarder.start_forwarder", return_value=fake_handle) as start_mock,
            mock.patch("c4_skills.runner._verify_direct_vllm") as verify_mock,
        ):
            handle, mode = runner.establish_vllm_access(self.GATEWAY)

        self.assertIs(handle, fake_handle)
        self.assertEqual(mode, "forwarder")
        self.assertFalse(verify_mock.called)
        kwargs = start_mock.call_args.kwargs
        self.assertEqual(kwargs["bind_ip"], self.GATEWAY)
        self.assertEqual(kwargs["bind_port"], pins.vllm_host_port())
        self.assertEqual(kwargs["target_ip"], pins.vllm_host())
        self.assertEqual(kwargs["target_port"], pins.vllm_host_port())

    def test_eaddrinuse_with_a_verified_server_is_direct_mode(self) -> None:
        with (
            mock.patch(
                "c4_skills.runner.forwarder.start_forwarder",
                side_effect=OSError(errno.EADDRINUSE, "Address already in use"),
            ),
            mock.patch("c4_skills.runner._verify_direct_vllm") as verify_mock,
        ):
            handle, mode = runner.establish_vllm_access(self.GATEWAY)

        self.assertIsNone(handle)
        self.assertEqual(mode, "direct-0.0.0.0-bind")
        verify_mock.assert_called_once_with(self.GATEWAY)

    def test_eaddrinuse_with_an_unverified_server_aborts(self) -> None:
        error = RuntimeError("direct vLLM access unverified: ...")
        with (
            mock.patch(
                "c4_skills.runner.forwarder.start_forwarder",
                side_effect=OSError(errno.EADDRINUSE, "Address already in use"),
            ),
            mock.patch("c4_skills.runner._verify_direct_vllm", side_effect=error),
        ):
            with self.assertRaises(RuntimeError) as ctx:
                runner.establish_vllm_access(self.GATEWAY)

        self.assertIs(ctx.exception, error)  # the verification failure is the abort

    def test_a_non_eaddrinuse_bind_error_propagates(self) -> None:
        error = OSError(errno.EADDRNOTAVAIL, "Cannot assign requested address")
        with (
            mock.patch("c4_skills.runner.forwarder.start_forwarder", side_effect=error) as start_mock,
            mock.patch("c4_skills.runner._verify_direct_vllm") as verify_mock,
        ):
            with self.assertRaises(OSError) as ctx:
                runner.establish_vllm_access(self.GATEWAY)

        self.assertIs(ctx.exception, error)  # a genuine harness failure, not a fallback
        self.assertEqual(start_mock.call_count, 1)
        self.assertFalse(verify_mock.called)


class TestRunLifecycle(unittest.TestCase):
    """Phase 110: `run`'s network/forwarder lifecycle and teardown order.

    The container layer is mocked at `runner._run_opencode_container`
    (the established pattern of this file); the docker-level helpers
    (create/remove/sweep network, gateway) and the sidecar/forwarder
    layers are mocked at their module boundary, and every call is
    recorded in one shared list so the ORDER is asserted, not just the
    membership.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="c4eval-lifecycle-")
        self.addCleanup(lambda: self._tmp.cleanup())
        self.root = Path(self._tmp.name)
        self.workroot = self.root / "work"
        self.results_dir = self.root / "results" / "run-x"
        self.cache_root = self.root / "cache"
        self.workroot.mkdir()
        self.results_dir.mkdir(parents=True)
        self.calls: list[str] = []
        self.captured: dict = {}

    def _config(self, network_name: str = "") -> runner.RunConfig:
        return runner.RunConfig(
            run_id="run-x",
            case_ids=[pins.SMOKE_CASE],
            conditions=[pins.CONDITION_NONE],
            k=1,
            seed=7,
            workroot=self.workroot,
            results_dir=self.results_dir,
            cache_root=self.cache_root,
            network_name=network_name,
        )

    def _fake_container(self, workdir, case, *, network, vllm_base_url, mcp_url, timeout_s, log_path, container_name):
        self.captured["container_network"] = network
        self.captured["vllm_base_url"] = vllm_base_url
        self.captured["mcp_url"] = mcp_url
        if self.captured.get("container_should_raise"):
            raise RuntimeError("trial exploded")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(MINIMAL_STREAM, encoding="utf-8")
        return 0, False, 1.5

    def _patches(self, direct_mode: bool = False, verify_error: Exception | None = None):
        def fake_sidecar_list() -> list[str]:
            return []

        def fake_create(name: str) -> None:
            self.calls.append(f"create_run_network:{name}")

        def fake_start_sidecar(run_id: str, network: str) -> sidecar.SidecarHandle:
            self.calls.append(f"sidecar_start:{network}")
            return sidecar.SidecarHandle(
                ip="172.21.0.3", port=sidecar.SIDECAR_PORT, container_id="cid-1", container_name=f"c4eval-mcp-{run_id}"
            )

        def fake_gateway(name: str) -> str:
            self.calls.append(f"gateway:{name}")
            return "172.21.0.1"

        def fake_start_forwarder(*, bind_ip: str, bind_port: int, target_ip: str, target_port: int) -> object:
            if direct_mode:
                # the shared vLLM's 0.0.0.0 bind already owns the address:port
                self.calls.append("forwarder_start_attempt")
                raise OSError(errno.EADDRINUSE, "Address already in use")
            self.calls.append("forwarder_start")
            self.captured["forwarder"] = (bind_ip, bind_port, target_ip, target_port)
            return object()

        def fake_verify_direct(gateway_ip: str) -> None:
            self.calls.append(f"vllm_verify:{gateway_ip}")
            if verify_error is not None:
                raise verify_error

        def fake_stop_forwarder(handle: object) -> None:
            self.calls.append("forwarder_stop")

        def fake_stop_sidecar(*, container_id: str | None = None, container_name: str | None = None) -> None:
            self.calls.append("sidecar_stop")

        def fake_remove(name: str) -> None:
            self.calls.append(f"remove_run_network:{name}")

        def fake_preflight(**kwargs: object) -> preflight.PreflightResult:
            self.captured.setdefault("preflights", []).append(kwargs)
            # carry the extra facts into the data so the REAL
            # write_preflight commits them to preflight.json on disk
            extra = kwargs.get("extra")
            data = dict(extra) if isinstance(extra, dict) else {}
            return preflight.PreflightResult(ok=True, data=data)

        return (
            mock.patch("c4_skills.runner.sidecar.sidecar_container_list", side_effect=fake_sidecar_list),
            mock.patch("c4_skills.runner.sweep_trial_containers", return_value=[]),
            mock.patch("c4_skills.runner.sweep_run_networks", return_value=[]),
            mock.patch("c4_skills.runner.create_run_network", side_effect=fake_create),
            mock.patch("c4_skills.runner.network_gateway_ip", side_effect=fake_gateway),
            mock.patch("c4_skills.runner.remove_run_network", side_effect=fake_remove),
            mock.patch("c4_skills.runner.sidecar.start_sidecar", side_effect=fake_start_sidecar),
            mock.patch("c4_skills.runner.sidecar.stop_sidecar", side_effect=fake_stop_sidecar),
            mock.patch("c4_skills.runner.forwarder.start_forwarder", side_effect=fake_start_forwarder),
            mock.patch("c4_skills.runner.forwarder.stop", side_effect=fake_stop_forwarder),
            mock.patch("c4_skills.runner._verify_direct_vllm", side_effect=fake_verify_direct),
            mock.patch("c4_skills.preflight.run_preflight", side_effect=fake_preflight),
            mock.patch("c4_skills.preflight.local_host_addr", return_value="127.0.0.1"),
            mock.patch("c4_skills.preflight.wait_until_idle", return_value=(True, 0, 0.0)),
            mock.patch("c4_skills.preflight.vllm_running_requests", return_value=0),
            mock.patch("c4_skills.runner._run_opencode_container", side_effect=self._fake_container),
            mock.patch("c4_skills.graders.collect_inputs", return_value=_empty_inputs()),
        )

    def _enter(self, patches: tuple) -> None:
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def test_lifecycle_order_endpoints_and_records(self) -> None:
        self._enter(self._patches())

        result = run(self._config())

        self.assertEqual(
            [c.split(":")[0] for c in self.calls],
            [
                "create_run_network",
                "sidecar_start",
                "gateway",
                "forwarder_start",
                "forwarder_stop",
                "sidecar_stop",
                "remove_run_network",
            ],
        )
        # the derived network name (no override) everywhere
        self.assertEqual(self.calls[0], "create_run_network:c4eval-run-x")
        self.assertEqual(self.calls[-1], "remove_run_network:c4eval-run-x")
        # the forwarder: gateway IP -> vLLM loopback, on vLLM's port
        self.assertEqual(self.captured["forwarder"], ("172.21.0.1", 8081, "127.0.0.1", 8081))
        # the trial container: the private network + the two explicit endpoints
        self.assertEqual(self.captured["container_network"], "c4eval-run-x")
        self.assertEqual(self.captured["vllm_base_url"], "http://172.21.0.1:8081/v1")
        self.assertEqual(self.captured["mcp_url"], "http://172.21.0.3:8181/mcp")
        # the run record carries the new topology pin
        self.assertEqual(result["version_tuple"]["network_mode"], pins.NETWORK_MODE)
        # the committed preflight records the topology facts (incl. the mode)
        preflight_doc = (self.results_dir / "preflight.json").read_text(encoding="utf-8")
        self.assertIn('"network_mode": "internal-bridge"', preflight_doc)
        self.assertIn('"network_name": "c4eval-run-x"', preflight_doc)
        self.assertIn('"sidecar_ip": "172.21.0.3"', preflight_doc)
        self.assertIn('"vllm_access": "forwarder"', preflight_doc)
        self.assertIn('"vllm_base_url": "http://172.21.0.1:8081/v1"', preflight_doc)
        # the second (post-sidecar) preflight carries the sidecar port
        preflights = self.captured["preflights"]
        self.assertEqual(len(preflights), 2)
        self.assertEqual(preflights[1]["mcp_port"], sidecar.SIDECAR_PORT)

    def test_an_explicit_network_name_overrides_the_derivation(self) -> None:
        self._enter(self._patches())

        run(self._config(network_name="custom-net-1"))

        self.assertEqual(self.calls[0], "create_run_network:custom-net-1")
        self.assertEqual(self.calls[-1], "remove_run_network:custom-net-1")
        self.assertEqual(self.captured["container_network"], "custom-net-1")

    def test_a_failing_trial_still_tears_down_in_order(self) -> None:
        self.captured["container_should_raise"] = True
        self._enter(self._patches())

        with self.assertRaises(RuntimeError) as ctx:
            run(self._config())

        self.assertIn("trial exploded", str(ctx.exception))
        self.assertEqual(
            [c.split(":")[0] for c in self.calls],
            [
                "create_run_network",
                "sidecar_start",
                "gateway",
                "forwarder_start",
                "forwarder_stop",
                "sidecar_stop",
                "remove_run_network",
            ],
        )

    def test_direct_mode_lifecycle_no_forwarder_stop_and_same_url(self) -> None:
        # option C fallback: the bind is already owned (EADDRINUSE), the
        # strict verification passes, and the run goes on with the SAME
        # vLLM URL -- teardown must not stop a forwarder that was never
        # started
        self._enter(self._patches(direct_mode=True))

        result = run(self._config())

        self.assertEqual(
            [c.split(":")[0] for c in self.calls],
            [
                "create_run_network",
                "sidecar_start",
                "gateway",
                "forwarder_start_attempt",
                "vllm_verify",
                "sidecar_stop",
                "remove_run_network",
            ],
        )
        self.assertNotIn("forwarder_stop", [c.split(":")[0] for c in self.calls])
        self.assertEqual(self.calls[4], "vllm_verify:172.21.0.1")
        # mode-invariant URL, recorded mode
        self.assertEqual(self.captured["vllm_base_url"], "http://172.21.0.1:8081/v1")
        self.assertEqual(self.captured["mcp_url"], "http://172.21.0.3:8181/mcp")
        preflight_doc = (self.results_dir / "preflight.json").read_text(encoding="utf-8")
        self.assertIn('"vllm_access": "direct-0.0.0.0-bind"', preflight_doc)
        self.assertEqual(result["version_tuple"]["network_mode"], pins.NETWORK_MODE)

    def test_direct_mode_with_an_unverified_server_aborts_and_tears_down(self) -> None:
        # the pin violation aborts BEFORE any trial, and the teardown still
        # runs (sidecar down, network removed)
        self._enter(
            self._patches(
                direct_mode=True,
                verify_error=RuntimeError("direct vLLM access unverified: wrong version"),
            )
        )

        with self.assertRaises(RuntimeError) as ctx:
            run(self._config())

        self.assertIn("wrong version", str(ctx.exception))
        self.assertEqual(
            [c.split(":")[0] for c in self.calls],
            [
                "create_run_network",
                "sidecar_start",
                "gateway",
                "forwarder_start_attempt",
                "vllm_verify",
                "sidecar_stop",
                "remove_run_network",
            ],
        )
        # no trial container ever ran
        self.assertNotIn("container_network", self.captured)


if __name__ == "__main__":
    unittest.main()
