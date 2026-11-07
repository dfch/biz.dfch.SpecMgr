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

"""The injected OpenCode configuration (Task 100.110, reworked for the
Phase 110 egress-control change).

Every trial container runs with exactly this config, injected through the
`OPENCODE_CONFIG_CONTENT` env var (the documented inline-config source; no
host OpenCode config is mounted, no project config file is written). The
config is condition-agnostic except for the two endpoints, and those are
explicit arguments, never derived: the trial containers live on the run's
private `--internal` network, where the ONLY reachable endpoints are the
two the harness exposes -- vLLM access on the network's gateway IP
(`baseURL` -- the run's forwarder, or the shared vLLM's strictly-verified
0.0.0.0 bind, mode-invariant to this config) and the sidecar on its
container IP (`mcp` url). The `none`/`upstream`/`skill` difference is the
mounted skills, not the config.

The `mcp.<name>` block keeps the pinned image's deprecated shape: a config
schema probe (Phase 110) verified that both the deprecated shape and
`mcp.servers` + `codemode: false` yield NO native MCP tools in the pinned
opencode image -- Code Mode is the access path (the detection layer reads
the Code Mode invocations out of the event stream), so the shape must not
be "upgraded".
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


def build_opencode_config(*, vllm_base_url: str, mcp_url: str) -> dict:
    """Build the injected OpenCode config for one run.

    Args:
        vllm_base_url: The provider `baseURL` as reachable from the trial
            container: `http://<gateway_ip>:8081/v1` -- vLLM access on the
            private network's gateway IP (the run's forwarder, or the
            shared vLLM's verified 0.0.0.0 bind; mode-invariant here).
        mcp_url: The MCP sidecar's URL as reachable from the trial
            container: `http://<sidecar_ip>:<port>/mcp` -- the sidecar's
            own address on the private network.

    Returns:
        A JSON-serialisable dict (written with sorted keys).
    """
    assert isinstance(vllm_base_url, str) and vllm_base_url.startswith("http://")
    assert isinstance(mcp_url, str) and mcp_url.startswith("http://")
    result: dict = {
        "$schema": "https://opencode.ai/config.json",
        "model": f"{pins.PROVIDER_ID}/{pins.MODEL_ID}",
        "provider": {
            pins.PROVIDER_ID: {
                "npm": PROVIDER_NPM,
                "name": "vLLM sys0 (shared, 2 sequence slots)",
                "options": {
                    "baseURL": vllm_base_url,
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
                "url": mcp_url,
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


def opencode_config_content(*, vllm_base_url: str, mcp_url: str) -> str:
    """Return the `OPENCODE_CONFIG_CONTENT` value (canonical JSON).

    Args:
        vllm_base_url: The provider `baseURL` (see
            :func:`build_opencode_config`).
        mcp_url: The MCP sidecar's URL (see :func:`build_opencode_config`).
    """
    config = build_opencode_config(vllm_base_url=vllm_base_url, mcp_url=mcp_url)
    result = json.dumps(config, indent=2, sort_keys=True) + "\n"
    return result
