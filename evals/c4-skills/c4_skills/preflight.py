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

"""The run preflight (Task 100.180).

Records, with every run: the vLLM endpoint, the provider id, the model id,
the vLLM version, the speculative configuration (as deployed -- vLLM 0.26.0
exposes no external metric for it, so it is recorded as not externally
verifiable rather than guessed), the sampling parameters the harness
injects, the pinned images with their digests, the host Python and jq
versions, the upstream SHA, and the server's idle state
(``vllm:num_requests_running`` summed over all engines).

The preflight ABORTS the run (returns `ok=False`) when a pin no longer
holds: the vLLM version or model id changed, the process Python or jq
version differs from the pin, or a pinned image is missing locally.
"""

from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from . import pins

#: The idle check: the sum of `vllm:num_requests_running` over all engines
#: must be exactly this for the server to count as idle.
IDLE_RUNNING = 0

#: The metric line pattern (engine label optional, value last).
_RUNNING_RE = re.compile(r"^vllm:num_requests_running\{[^}]*\}\s+([0-9.]+)$", re.MULTILINE)


@dataclass
class PreflightResult:
    """The recorded preflight facts plus the abort decision.

    Attributes:
        ok: False when a pin no longer holds (the run must not start).
        problems: The pin violations / probe failures, human-readable.
        data: Every recorded fact (the preflight.json payload).
    """

    ok: bool
    problems: list[str] = field(default_factory=list)
    data: dict = field(default_factory=dict)

    def to_json(self) -> dict:
        """Return the JSON payload written to `preflight.json`."""
        result = dict(self.data)
        result["ok"] = self.ok
        result["problems"] = list(self.problems)
        return result


def _http_get_json(url: str, timeout: float = 15.0) -> dict | None:
    """GET one JSON document; None on any failure (recorded, not raised)."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:  # noqa: S310 -- pinned http://127.0.0.1 endpoint
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
        return None


def vllm_running_requests() -> int | None:
    """Return the sum of `vllm:num_requests_running` over all engines.

    Returns:
        The integer sum, or None when the metrics endpoint does not answer.
    """
    try:
        metrics_url = pins.VLLM_METRICS_URL
        with urllib.request.urlopen(metrics_url, timeout=15) as response:  # noqa: S310 -- pinned local endpoint
            body = response.read().decode("utf-8")
    except (urllib.error.URLError, OSError, TimeoutError):
        return None
    values = [float(m) for m in _RUNNING_RE.findall(body)]
    result: int | None = int(sum(values)) if values else None
    return result


def wait_until_idle(budget_s: float, poll_s: float = 10.0) -> tuple[bool, int, float]:
    """Block until vLLM reports zero running requests (or the budget ends).

    The runner uses this before start and between trials (Task 100.130):
    the shared server has two sequence slots and every other client's
    request is contention for the trial.

    Args:
        budget_s: How long to wait at most.
        poll_s: The poll interval.

    Returns:
        (idle, last_seen, waited_s): whether it drained, the last observed
        running-request count, and the seconds waited.
    """
    assert budget_s >= 0
    start = time.monotonic()
    last = -1
    while True:
        seen = vllm_running_requests()
        if seen is not None:
            last = seen
        if seen == IDLE_RUNNING:
            return True, last, time.monotonic() - start
        if time.monotonic() - start >= budget_s:
            return False, last, time.monotonic() - start
        time.sleep(poll_s)


def _docker_image_digest(image: str) -> str | None:
    """Return the locally stored repo digest of one image (None if absent)."""
    try:
        proc = subprocess.run(  # noqa: S603 -- fixed image reference
            ["docker", "image", "inspect", image, "--format", "{{index .RepoDigests 0}}"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    digest = proc.stdout.strip()
    result: str | None = _normalize_digest(digest) if digest else None
    return result


def _docker_version() -> str | None:
    """Return the host Docker version string (e.g. `29.1.3`)."""
    try:
        proc = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=30)  # noqa: S603
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    match = re.search(r"version\s+([0-9.]+)", proc.stdout or "")
    result: str | None = match.group(1) if match else (proc.stdout or "").strip()
    return result


def _normalize_digest(digest: str) -> str:
    """Reduce a `repo@sha256:...` RepoDigest to the bare `sha256:...` form."""
    result = digest.strip()
    if "@" in result:
        result = result.split("@", 1)[1]
    return result


def _jq_version() -> str | None:
    """Return the host jq version string (e.g. `1.6`)."""
    try:
        proc = subprocess.run(["jq", "--version"], capture_output=True, text=True, timeout=30)  # noqa: S603
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    match = re.search(r"jq-[0-9.]+", proc.stdout or "")
    result: str | None = match.group(0).removeprefix("jq-") if match else None
    return result


def run_preflight(
    *,
    conditions: list[str],
    upstream_source: object | None = None,
    mcp_port: int | None = None,
    extra: dict | None = None,
) -> PreflightResult:
    """Collect every preflight fact and check the pins (pure probes).

    Args:
        conditions: The conditions this run will use (drives the upstream
            SHA verification).
        upstream_source: A verified UpstreamSource when the upstream
            condition is used (its SHA and files feed the record).
        mcp_port: The sidecar port (recorded with the run).
        extra: Extra facts to fold into the record (seed, k, cases, ...).

    Returns:
        The PreflightResult (`ok=False` lists the violated pins).
    """
    assert isinstance(conditions, list)
    problems: list[str] = []
    data: dict = {
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "provider_id": pins.PROVIDER_ID,
        "model_id": pins.MODEL_ID,
        "vllm_endpoint": pins.VLLM_ENDPOINT,
        "sampling_parameters": dict(pins.SAMPLING_PARAMETERS),
        "speculative_config": dict(pins.SPECULATIVE_CONFIG),
        "opencode_image": pins.OPENCODE_IMAGE,
        "structurizr_mcp_image": pins.STRUCTURIZR_MCP_IMAGE,
        "structurizr_cli_image": pins.STRUCTURIZR_CLI_IMAGE,
        "python": ".".join(str(x) for x in sys.version_info[:3]),
        "conditions": list(conditions),
    }
    if mcp_port is not None:
        data["mcp_port"] = mcp_port

    # vLLM: version + model id + idle state
    version_doc = _http_get_json(pins.VLLM_ENDPOINT.removesuffix("/v1") + "/version")
    vllm_version = version_doc.get("version") if isinstance(version_doc, dict) else None
    data["vllm_version"] = vllm_version
    if vllm_version != pins.VLLM_VERSION_PIN:
        problems.append(f"vLLM version {vllm_version!r} != pin {pins.VLLM_VERSION_PIN!r}")

    models_doc = _http_get_json(pins.VLLM_ENDPOINT + "/models")
    model_ids = []
    max_model_len = None
    if isinstance(models_doc, dict):
        for entry in models_doc.get("data") or []:
            if isinstance(entry, dict):
                model_ids.append(entry.get("id"))
                if entry.get("id") == pins.MODEL_ID:
                    max_model_len = entry.get("max_model_len")
    data["vllm_model_ids"] = model_ids
    data["vllm_max_model_len"] = max_model_len
    if pins.MODEL_ID not in model_ids:
        problems.append(f"model {pins.MODEL_ID!r} not served (served: {model_ids})")
    elif max_model_len != pins.MODEL_MAX_CONTEXT:
        problems.append(f"max_model_len {max_model_len} != pin {pins.MODEL_MAX_CONTEXT}")

    running = vllm_running_requests()
    data["vllm_num_requests_running"] = running
    data["vllm_idle"] = running == IDLE_RUNNING

    # host tooling pins
    jq = _jq_version()
    data["jq"] = jq
    if jq != pins.JQ_VERSION_PIN:
        problems.append(f"jq {jq!r} != pin {pins.JQ_VERSION_PIN!r}")
    py = data["python"]
    if py != pins.PYTHON_VERSION_PIN:
        problems.append(f"harness python {py!r} != pin {pins.PYTHON_VERSION_PIN!r}")
    docker_version = _docker_version()
    data["docker"] = docker_version
    if docker_version is None:
        problems.append("docker is not available")

    # image pins (tag + the locally stored digest)
    for label, image, digest_pin in (
        ("opencode", pins.OPENCODE_IMAGE, pins.OPENCODE_IMAGE_DIGEST),
        ("structurizr_mcp", pins.STRUCTURIZR_MCP_IMAGE, pins.STRUCTURIZR_MCP_IMAGE_DIGEST),
        ("structurizr_cli", pins.STRUCTURIZR_CLI_IMAGE, pins.STRUCTURIZR_CLI_IMAGE_DIGEST),
    ):
        digest = _docker_image_digest(image)
        data[f"{label}_image_digest"] = digest
        if digest is None:
            problems.append(f"image {image} is not present locally")
        elif digest != digest_pin:
            problems.append(f"image {image} digest {digest} != pin {digest_pin}")

    # upstream verification (only when the condition is actually used)
    if pins.CONDITION_UPSTREAM in conditions:
        sha: str | None = None
        skill_count = 0
        if upstream_source is not None:
            sha = getattr(upstream_source, "sha", None)
            skill_count = len(getattr(upstream_source, "skills", ()))
        data["upstream_repo"] = pins.UPSTREAM_REPO
        data["upstream_sha"] = sha
        data["upstream_skills"] = skill_count
        if sha != pins.UPSTREAM_SHA_PIN:
            problems.append(f"upstream SHA {sha!r} != pin {pins.UPSTREAM_SHA_PIN!r}")

    if extra:
        data.update(extra)

    result = PreflightResult(ok=not problems, problems=problems, data=data)
    return result


def write_preflight(path: Path, preflight: PreflightResult) -> None:
    """Write the preflight record (the committed run artifact)."""
    assert path is not None
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(preflight.to_json(), indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")


def local_host_addr() -> str:
    """Return this host's primary IPv4 address (recorded for the run)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            result = sock.getsockname()[0]
            return result
    except OSError:
        return "127.0.0.1"


def host_user_flags() -> list[str]:
    """Return the docker `--user uid:gid` flags for host-owned file output.

    The trial and CLI containers run as the invoking host user so every
    file they write into the mounted work dirs (the event stream is
    host-written; the CLI `export` writes `out/`) stays host-owned and the
    gitignored work roots never accumulate root-owned files.

    Returns:
        `["--user", "uid:gid"]` on POSIX, `[]` when the user identity is
        unavailable (the containers then run as their default user).
    """
    if not hasattr(os, "getuid"):
        return []
    result = ["--user", f"{os.getuid()}:{os.getgid()}"]
    return result
