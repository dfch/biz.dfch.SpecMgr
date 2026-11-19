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

"""Injected OpenCode config tests (Phase 110: the parameterized endpoints).

No Docker, no model: the config is a pure dict/JSON builder. Covers the
locked rework -- the provider `baseURL` and the MCP `url` are EXPLICIT
arguments (the run's gateway-IP forwarder and the sidecar's container IP
on the private network), never derived from pins/127.0.0.1 -- and the
rest of the shape (the deprecated `mcp.<name>` block, the permissions,
the sampling parameters) is unchanged.
"""

import json
import unittest

from c4_skills import occonfig, pins

#: The two endpoints a trial on the run's private network can reach.
GATEWAY_URL = "http://172.21.0.1:8081/v1"
SIDECAR_URL = "http://172.21.0.3:8181/mcp"


class TestBuildOpencodeConfig(unittest.TestCase):
    def test_the_explicit_endpoints_replace_the_loopback_derivations(self) -> None:
        sut = occonfig.build_opencode_config

        config = sut(vllm_base_url=GATEWAY_URL, mcp_url=SIDECAR_URL)

        provider = config["provider"][pins.PROVIDER_ID]
        self.assertEqual(provider["options"]["baseURL"], GATEWAY_URL)
        mcp_block = config["mcp"][occonfig.MCP_SERVER_NAME]
        self.assertEqual(mcp_block["url"], SIDECAR_URL)
        # the old loopback derivations are gone from the content
        content = json.dumps(config)
        self.assertNotIn("127.0.0.1", content)

    def test_the_deprecated_mcp_shape_is_kept(self) -> None:
        # a config-schema probe verified both the deprecated shape and
        # mcp.servers+codemode:false yield NO native MCP tools in the
        # pinned image -- Code Mode is the access path; do not upgrade.
        sut = occonfig.build_opencode_config

        config = sut(vllm_base_url=GATEWAY_URL, mcp_url=SIDECAR_URL)

        mcp = config["mcp"]
        self.assertNotIn("servers", mcp)  # not the mcp.servers shape
        self.assertEqual(set(mcp.keys()), {occonfig.MCP_SERVER_NAME})
        block = mcp[occonfig.MCP_SERVER_NAME]
        self.assertEqual(block["type"], "remote")
        self.assertTrue(block["enabled"])
        self.assertEqual(block["timeout"], occonfig.MCP_TIMEOUT_MS)

    def test_everything_else_is_unchanged(self) -> None:
        sut = occonfig.build_opencode_config

        config = sut(vllm_base_url=GATEWAY_URL, mcp_url=SIDECAR_URL)

        self.assertEqual(config["$schema"], "https://opencode.ai/config.json")
        self.assertEqual(config["model"], f"{pins.PROVIDER_ID}/{pins.MODEL_ID}")
        provider = config["provider"][pins.PROVIDER_ID]
        self.assertEqual(provider["npm"], occonfig.PROVIDER_NPM)
        self.assertEqual(provider["options"]["apiKey"], occonfig.PROVIDER_API_KEY)
        model = provider["models"][pins.MODEL_ID]
        self.assertEqual(model["limit"]["context"], pins.MODEL_MAX_CONTEXT)
        self.assertEqual(model["options"], dict(pins.SAMPLING_PARAMETERS))
        self.assertEqual(
            config["permission"],
            {
                "webfetch": "deny",
                "websearch": "deny",
                "question": "deny",
                "edit": "allow",
                "bash": "allow",
                "task": "allow",
                "skill": "allow",
                "external_directory": "allow",
            },
        )
        self.assertFalse(config["snapshot"])
        self.assertFalse(config["formatter"])
        self.assertFalse(config["lsp"])
        self.assertEqual(config["update"], "disable")

    def test_endpoints_are_keyword_only(self) -> None:
        sut = occonfig.build_opencode_config

        with self.assertRaises(TypeError):
            sut(GATEWAY_URL, SIDECAR_URL)  # type: ignore[call-arg] -- positional on purpose


class TestOpencodeConfigContent(unittest.TestCase):
    def test_the_content_is_canonical_json_with_the_endpoints(self) -> None:
        sut = occonfig.opencode_config_content

        content = sut(vllm_base_url=GATEWAY_URL, mcp_url=SIDECAR_URL)

        parsed = json.loads(content)
        self.assertEqual(parsed["provider"][pins.PROVIDER_ID]["options"]["baseURL"], GATEWAY_URL)
        self.assertEqual(parsed["mcp"][occonfig.MCP_SERVER_NAME]["url"], SIDECAR_URL)
        # canonical: sorted keys, indent 2, trailing newline
        self.assertEqual(content, json.dumps(parsed, indent=2, sort_keys=True) + "\n")
        self.assertTrue(content.endswith("\n"))

    def test_non_http_endpoints_are_rejected(self) -> None:
        sut = occonfig.build_opencode_config

        with self.assertRaises(AssertionError):
            sut(vllm_base_url="https://172.21.0.1:8081/v1", mcp_url=SIDECAR_URL)
        with self.assertRaises(AssertionError):
            sut(vllm_base_url=GATEWAY_URL, mcp_url="not a url")


if __name__ == "__main__":
    unittest.main()
