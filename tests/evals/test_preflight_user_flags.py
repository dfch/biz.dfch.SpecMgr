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

"""`preflight.host_user_flags` / `preflight.docker_is_rootless` tests (feat-274, issue #274).

Pure Python (no Docker): the `docker info` probe is mocked at the
`subprocess.run` boundary of the `preflight` module only, and the probe's
process-wide cache is cleared around every test. Covers the rootless-Docker
fix: under a rootless daemon container uid 0 already maps to the host user
and `--user uid:gid` would make the mounted work dirs unreadable, so
`--user 0:0` is returned; a rootful daemon or a failed probe keeps the
host `--user uid:gid` flags; a failed probe is not cached.
"""

from __future__ import annotations

import os
import subprocess
import unittest
from unittest import mock

from c4_skills import preflight

_ROOTLESS_STDOUT = '["name=seccomp,profile=builtin","name=rootless","name=cgroupns"]\n'
_ROOTFUL_STDOUT = '["name=apparmor","name=seccomp,profile=builtin","name=cgroupns"]\n'
_ROOTLESS_FLAGS = ["--user", preflight.ROOTLESS_CONTAINER_USER]


def _completed(stdout: str, returncode: int = 0) -> subprocess.CompletedProcess:
    """Return a fake `docker info` result with the given stdout/exit code."""
    result = subprocess.CompletedProcess(args=["docker", "info"], returncode=returncode, stdout=stdout, stderr="")
    return result


def _patch_run(**kwargs: object) -> mock._patch:
    """Patch `subprocess.run` as seen by the `preflight` module only."""
    result = mock.patch.object(preflight.subprocess, "run", **kwargs)
    return result


class _ProbeCacheReset(unittest.TestCase):
    """Clear the process-wide probe cache before and after every test."""

    def setUp(self) -> None:
        preflight.clear_docker_rootless_cache()
        self.addCleanup(preflight.clear_docker_rootless_cache)


@unittest.skipUnless(hasattr(os, "getuid"), "POSIX user identity required")
class TestHostUserFlags(_ProbeCacheReset):
    """`host_user_flags` follows the daemon mode reported by `docker info`."""

    def setUp(self) -> None:
        super().setUp()
        self.expected_user_flags = ["--user", f"{os.getuid()}:{os.getgid()}"]

    def test_rootless_daemon_returns_container_root_user(self) -> None:
        with _patch_run(return_value=_completed(_ROOTLESS_STDOUT)):
            result = preflight.host_user_flags()

        self.assertEqual(result, _ROOTLESS_FLAGS)
        self.assertEqual(preflight.ROOTLESS_CONTAINER_USER, "0:0")

    def test_rootful_daemon_returns_host_user_flags(self) -> None:
        with _patch_run(return_value=_completed(_ROOTFUL_STDOUT)):
            result = preflight.host_user_flags()

        self.assertEqual(result, self.expected_user_flags)

    def test_missing_docker_cli_keeps_host_user_flags(self) -> None:
        with _patch_run(side_effect=OSError("docker gone")):
            result = preflight.host_user_flags()

        self.assertEqual(result, self.expected_user_flags)

    def test_probe_timeout_keeps_host_user_flags(self) -> None:
        with _patch_run(side_effect=subprocess.TimeoutExpired(cmd="docker", timeout=30)):
            result = preflight.host_user_flags()

        self.assertEqual(result, self.expected_user_flags)

    def test_docker_info_failure_keeps_host_user_flags(self) -> None:
        with _patch_run(return_value=_completed("", returncode=1)):
            result = preflight.host_user_flags()

        self.assertEqual(result, self.expected_user_flags)

    def test_unparseable_probe_output_keeps_host_user_flags(self) -> None:
        with _patch_run(return_value=_completed("not json")):
            result = preflight.host_user_flags()

        self.assertEqual(result, self.expected_user_flags)

    def test_empty_probe_output_keeps_host_user_flags(self) -> None:
        with _patch_run(return_value=_completed("")):
            result = preflight.host_user_flags()

        self.assertEqual(result, self.expected_user_flags)

    def test_json_object_probe_output_keeps_host_user_flags(self) -> None:
        with _patch_run(return_value=_completed('{"name": "rootless"}')):
            result = preflight.host_user_flags()

        self.assertEqual(result, self.expected_user_flags)

    def test_non_string_security_options_are_ignored(self) -> None:
        with _patch_run(return_value=_completed('[1, null, {"name": "rootless"}, ["name=rootless"]]')):
            result = preflight.host_user_flags()

        self.assertEqual(result, self.expected_user_flags)

    def test_rootless_must_be_an_exact_option_element(self) -> None:
        with _patch_run(return_value=_completed('["name=rootlessish", "profile=name=rootless"]')):
            result = preflight.host_user_flags()

        self.assertEqual(result, self.expected_user_flags)


class TestDockerIsRootlessCache(_ProbeCacheReset):
    """Only a successful probe is cached; a failed probe is retried."""

    def test_successful_probe_runs_docker_info_security_options_once(self) -> None:
        with _patch_run(return_value=_completed(_ROOTLESS_STDOUT)) as run_mock:
            preflight.docker_is_rootless()
            result = preflight.docker_is_rootless()

        self.assertTrue(result)
        run_mock.assert_called_once()
        self.assertEqual(run_mock.call_args.args[0], ["docker", "info", "--format", "{{json .SecurityOptions}}"])

    def test_failed_probe_is_not_cached(self) -> None:
        with _patch_run(
            side_effect=[subprocess.TimeoutExpired(cmd="docker", timeout=30), _completed(_ROOTLESS_STDOUT)]
        ) as run_mock:
            first = preflight.docker_is_rootless()
            result = preflight.docker_is_rootless()

        self.assertFalse(first)
        self.assertTrue(result)
        self.assertEqual(run_mock.call_count, 2)

    def test_clear_forgets_the_cached_result(self) -> None:
        with _patch_run(side_effect=[_completed(_ROOTFUL_STDOUT), _completed(_ROOTLESS_STDOUT)]):
            first = preflight.docker_is_rootless()
            preflight.clear_docker_rootless_cache()
            result = preflight.docker_is_rootless()

        self.assertFalse(first)
        self.assertTrue(result)


class TestHostUserFlagsWithoutPosixIdentity(_ProbeCacheReset):
    """Without `os.getuid` the flags are empty and the probe never runs."""

    def test_no_getuid_returns_no_flags_without_probing(self) -> None:
        with mock.patch.object(preflight, "os", mock.Mock(spec=[])), _patch_run() as run_mock:
            result = preflight.host_user_flags()

        self.assertEqual(result, [])
        run_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
