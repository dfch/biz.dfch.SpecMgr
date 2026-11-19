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

"""Resource: specmgr://harness-bundle (feat-167-mcp-lifecycle-commands-2, Phase 130, REQ-008).

The packaged specmgr harness bundle as JSON (``application/json``): the
complete agent-driven install protocol in the top-level ``instructions``
field plus every ``.opencode/{agent,command,skill}/`` markdown file of the
published package as a ``{path, sha256, content}`` entry in the top-level
``files`` array (``path`` relative to ``.opencode/``, ``content`` the
file's verbatim text, ``sha256`` the hex digest of that text). The bundle
is the single generated package-data file
``general/data/general_harness_bundle.json`` -- regenerated from the
repo-root ``.opencode/`` tree by the flat ``specmgr harness-bundle`` CLI
command (``[cli]``-only, deterministic: ``json.dumps(indent=2,
ensure_ascii=False)`` + trailing newline, no timestamps, so two runs over
an unchanged tree are byte-identical) and kept from drifting by the
``specmgr-harness-bundle`` pre-commit hook (regenerate + fail on diff) and
the Python 3.13-pinned CI parity check.

This resource is the agent's sole discoverable entry point for installing
the harness files into a fresh harness setup (OpenCode, Claude Code, ...):
the active harness's own agent reads it and follows the ``instructions``
protocol (harness config root via the harness's own configuration skill,
byte-exact writes, the sha256 skip/ask/verify loop, the per-file
installed/skipped/updated/failed report, never touching ``opencode.json``).
There is deliberately no install CLI and no MCP prompt for this flow --
OpenCode exposes MCP tools but not MCP prompts to the agent, so the
self-describing resource is the carrier (REQ-008, the feature plan's
Design Notes).

Served as the packaged file's raw text (``application/json``), mirroring
``specmgr://rasci``'s packaged-read pattern: ``read_packaged_text("general",
"harness_bundle", "json")`` reads the file fresh on every call (no cache,
hard failure on a missing file), a fail-fast ``json.loads`` on every call
guards the structure (no dedicated model -- the bundle has no schema of
its own), and the parsed result is discarded with the raw text returned
unchanged. Reading via ``importlib.resources`` means the resource works
identically from an editable checkout and a real, non-editable install.
"""

from __future__ import annotations

import json

from ...server import mcp
from ..tools._packaged_data import read_packaged_text


@mcp.resource(
    "specmgr://harness-bundle",
    name="harness_bundle",
    title="SpecMgr Harness Bundle (agents, commands, skills + install protocol)",
    description=(
        "The packaged specmgr harness bundle as application/json: the complete agent-driven "
        "install protocol in the top-level `instructions` field plus every "
        ".opencode/{agent,command,skill}/ markdown file as a {path, sha256, content} entry in "
        "`files` (path relative to .opencode/, content verbatim). The active harness's own agent "
        "reads this resource and installs the files into its harness config root per the protocol "
        "-- byte-exact writes, sha256 skip/ask/verify, per-file report, never touching "
        "opencode.json."
    ),
    mime_type="application/json",
)
def harness_bundle() -> str:
    """Return the packaged harness bundle's full JSON text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as every other cross-cutting ``general`` resource -- reads the
    file fresh on every call. Also ``json.loads``-parses the text on every
    call purely to fail fast on structural drift in production (the bundle
    has no dedicated model of its own, so a JSON-decode failure is the
    guard); the parsed result is discarded and the raw text is returned
    unchanged.

    Returns
    -------
    str
        The harness bundle's raw JSON source (``{"instructions",
        "files": [{"path", "sha256", "content"}]}``).

    Raises
    ------
    FileNotFoundError
        If the packaged ``general_harness_bundle.json`` is missing.
    json.JSONDecodeError
        If the packaged file is not valid JSON (structural drift).
    """
    text = read_packaged_text("general", "harness_bundle", "json")
    json.loads(text)
    result = text
    return result
