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

"""Tests for the ``mcp`` command.

Requires the ``mcp`` extra (``pip install "biz-dfch-specmgr[mcp]"``).
"""

import unittest
from unittest import mock

from biz.dfch.specmgr.commands.mcp import _warn_on_public_binding, mcp


class TestMcpCommand(unittest.TestCase):
    """Tests that each ``--transport`` branch calls ``mcp_server.run`` correctly."""

    def test_stdio_calls_run_with_stdio_transport(self):
        """``--transport stdio`` calls ``run(transport=\"stdio\")`` only."""
        with mock.patch("biz.dfch.specmgr.server.mcp") as mcp_server:
            mcp(transport="stdio", host="localhost", port=8000)
        mcp_server.run.assert_called_once_with(transport="stdio")

    def test_sse_calls_run_with_sse_transport(self):
        """``--transport sse`` calls ``run`` with ``transport=\"sse\"``, ``host``, and ``port``."""
        with mock.patch("biz.dfch.specmgr.server.mcp") as mcp_server:
            mcp(transport="sse", host="localhost", port=8000)
        mcp_server.run.assert_called_once_with(transport="sse", host="localhost", port=8000)

    def test_streamable_http_calls_run_with_streamable_http_transport(self):
        """``--transport streamable-http`` calls ``run`` with ``stateless_http=True``."""
        with mock.patch("biz.dfch.specmgr.server.mcp") as mcp_server:
            mcp(transport="streamable-http", host="localhost", port=8000)
        mcp_server.run.assert_called_once_with(
            transport="streamable-http", host="localhost", port=8000, stateless_http=True
        )


class TestWarnOnPublicBinding(unittest.TestCase):
    """Tests for the ``_warn_on_public_binding`` helper."""

    def test_silent_for_localhost(self):
        """No warning is written when the host is not a public bind address."""
        with mock.patch("sys.stderr") as stderr:
            _warn_on_public_binding("localhost")
        stderr.write.assert_not_called()

    def test_warns_for_all_interfaces_outside_a_container(self):
        """A warning is written for '0.0.0.0' when no container markers are set."""
        with (
            mock.patch("os.path.exists", return_value=False),
            mock.patch.dict("os.environ", {}, clear=True),
            mock.patch("sys.stderr") as stderr,
        ):
            _warn_on_public_binding("0.0.0.0")
        stderr.write.assert_called_once()

    def test_silent_for_all_interfaces_inside_a_container(self):
        """No warning is written for '0.0.0.0' when a container marker is set."""
        with (
            mock.patch("os.path.exists", return_value=True),
            mock.patch("sys.stderr") as stderr,
        ):
            _warn_on_public_binding("0.0.0.0")
        stderr.write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
