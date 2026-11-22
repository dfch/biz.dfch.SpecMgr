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

"""`preflight.host_user_flags` / `preflight.docker_is_rootless` tests.

Pure Python (no Docker): the `docker info` probe is mocked at the
`subprocess.run` boundary and the probe's process-wide cache is cleared
around every test. Covers the rootless-Docker fix: under a rootless
daemon container uid 0 already maps to the host user and `--user
uid:gid` would make the mounted work dirs unreadable, so no flags are
returned; a rootful daemon or a failed probe keeps the `--user` flags.
"""

from __future__ import annotations

import os
import subprocess
import unittest
from unittest import mock

from c4_skills import preflight

_ROOTLESS_STDOUT = '["name=seccomp,profile=builtin","name=rootless","name=cgroupns"]\n'
_ROOTFUL_STDOUT = '["name=apparmor","name=seccomp,profile=builtin","name=cgroupns"]\n'


def _completed(stdout: str, returncode: int = 0) -> subprocess.CompletedProcess:
    """Return a fake `docker info` result with the given stdout/exit code."""
    result = subprocess.CompletedProcess(args=["docker", "info"], returncode=returncode, stdout=stdout, stderr="")
    return result


@unittest.skipUnless(hasattr(os, "getuid"), "POSIX user identity required")
class TestHostUserFlags(unittest.TestCase):
    """`host_user_flags` follows the daemon mode reported by `docker info`."""

    def setUp(self) -> None:
        preflight.docker_is_rootless.cache_clear()
        self.addCleanup(preflight.docker_is_rootless.cache_clear)
        self.expected_user_flags = ["--user", f"{os.getuid()}:{os.getgid()}"]

    def test_rootless_daemon_returns_no_flags(self) -> None:
        with mock.patch("subprocess.run", return_value=_completed(_ROOTLESS_STDOUT)):
            result = preflight.host_user_flags()

        self.assertEqual(result, [])

    def test_rootful_daemon_returns_user_flags(self) -> None:
        with mock.patch("subprocess.run", return_value=_completed(_ROOTFUL_STDOUT)):
            result = preflight.host_user_flags()

        self.assertEqual(result, self.expected_user_flags)

    def test_missing_docker_cli_keeps_user_flags(self) -> None:
        with mock.patch("subprocess.run", side_effect=OSError("docker gone")):
            result = preflight.host_user_flags()

        self.assertEqual(result, self.expected_user_flags)

    def test_probe_timeout_keeps_user_flags(self) -> None:
        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="docker", timeout=30)):
            result = preflight.host_user_flags()

        self.assertEqual(result, self.expected_user_flags)

    def test_docker_info_failure_keeps_user_flags(self) -> None:
        with mock.patch("subprocess.run", return_value=_completed("", returncode=1)):
            result = preflight.host_user_flags()

        self.assertEqual(result, self.expected_user_flags)

    def test_unparseable_probe_output_keeps_user_flags(self) -> None:
        with mock.patch("subprocess.run", return_value=_completed("not json")):
            result = preflight.host_user_flags()

        self.assertEqual(result, self.expected_user_flags)

    def test_probe_runs_docker_info_security_options_once(self) -> None:
        with mock.patch("subprocess.run", return_value=_completed(_ROOTLESS_STDOUT)) as run_mock:
            preflight.host_user_flags()
            result = preflight.host_user_flags()

        self.assertEqual(result, [])
        run_mock.assert_called_once()
        self.assertEqual(run_mock.call_args.args[0], ["docker", "info", "--format", "{{json .SecurityOptions}}"])


if __name__ == "__main__":
    unittest.main()
