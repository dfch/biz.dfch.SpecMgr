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

"""The injected OpenCode configuration (Task 100.110).

Every trial container runs with exactly this config, injected through the
`OPENCODE_CONFIG_CONTENT` env var (the documented inline-config source; no
host OpenCode config is mounted, no project config file is written). The
config is condition-agnostic except for the MCP sidecar port: the
`none`/`upstream`/`skill` difference is the mounted skills, not the config.
"""

from __future__ import annotations

import json

from . import pins

#: The OpenAI-compatible provider npm package opencode loads for vLLM.
PROVIDER_NPM = "@ai-sdk/openai-compatible"

#: The dummy API key (vLLM needs no auth; the provider package wants one).
PROVIDER_API_KEY = "harness-local-no-auth"

#: The MCP server name; opencode prefixes its tool names with it
#: (`structurizr_validate`, `structurizr_parse`, ...).
MCP_SERVER_NAME = "structurizr"

#: The MCP request timeouts in ms (the structurizr export of a large model
#: can exceed the 5 s default).
MCP_TIMEOUT_MS = 300_000

#: The env var the injected config is written under (the documented
#: inline-config source of opencode).
OPENCODE_CONFIG_CONTENT_ENV = "OPENCODE_CONFIG_CONTENT"


def build_opencode_config(mcp_port: int) -> dict:
    """Build the injected OpenCode config for one run.

    Args:
        mcp_port: The host port of the harness's own structurizr MCP
            sidecar (the trial containers use `--network host`, so
            `127.0.0.1:<port>` reaches it).

    Returns:
        A JSON-serialisable dict (written with sorted keys).
    """
    assert isinstance(mcp_port, int) and 1 <= mcp_port <= 65535
    result: dict = {
        "$schema": "https://opencode.ai/config.json",
        "model": f"{pins.PROVIDER_ID}/{pins.MODEL_ID}",
        "provider": {
            pins.PROVIDER_ID: {
                "npm": PROVIDER_NPM,
                "name": "vLLM sys0 (shared, 2 sequence slots)",
                "options": {
                    "baseURL": pins.VLLM_ENDPOINT,
                    "apiKey": PROVIDER_API_KEY,
                },
                "models": {
                    pins.MODEL_ID: {
                        "name": "Qwen3.8 27B (MTP, 5 speculative tokens)",
                        "limit": {
                            "context": pins.MODEL_MAX_CONTEXT,
                            "output": 32768,
                        },
                        # The sampling parameters the harness injects
                        # (Task 100.180 records them in the preflight).
                        "options": dict(pins.SAMPLING_PARAMETERS),
                    }
                },
            }
        },
        "mcp": {
            MCP_SERVER_NAME: {
                "type": "remote",
                "url": f"http://127.0.0.1:{mcp_port}/mcp",
                "enabled": True,
                "timeout": MCP_TIMEOUT_MS,
            }
        },
        # Isolation (Measurement): no web access for any condition, so a
        # baseline cannot download the upstream skills; no user questions in
        # a headless run.
        "permission": {
            "webfetch": "deny",
            "websearch": "deny",
            "question": "deny",
            "edit": "allow",
            "bash": "allow",
            "task": "allow",
            "skill": "allow",
            "external_directory": "allow",
        },
        # Determinism: no snapshot git index, no formatters, no LSP inside
        # the trial container.
        "snapshot": False,
        "formatter": False,
        "lsp": False,
        "update": "disable",
    }
    return result


def opencode_config_content(mcp_port: int) -> str:
    """Return the `OPENCODE_CONFIG_CONTENT` value (canonical JSON)."""
    config = build_opencode_config(mcp_port)
    result = json.dumps(config, indent=2, sort_keys=True) + "\n"
    return result
