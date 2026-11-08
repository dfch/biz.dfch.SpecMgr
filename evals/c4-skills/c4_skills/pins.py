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

"""Pinned versions and the version tuple of the c4-skills measurement harness.

Every pin below was verified against the host at pin time (2026-11-01):
the image digests from ``docker image inspect``, the vLLM version from
``GET /version``, the upstream commit from ``api.github.com``. The
preflight re-records the mutable values (vLLM version, docker version,
process Python) with every run and compares them against these pins; a
mismatch aborts the run before any trial starts.

The version tuple (REQ-008 reproducibility) is the canonical JSON of
:data:`VERSION_TUPLE` plus the sampling parameters; its sha256 is the
``version_tuple_hash`` recorded with every run and used as a result-cache
key component (a changed pin invalidates every cached ``none``/
``upstream`` result).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

#: The harness root (evals/c4-skills), the parent of this package. Both the
#: CLI and the runner resolve their default directories from it.
HARNESS_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# condition names
# ---------------------------------------------------------------------------

#: Condition with MCP access but no skills (the floor every skill must beat,
#: ACC-012).
CONDITION_NONE = "none"

#: The unmodified `jrjsmrtn/c4-skills` skills, fetched at run time from the
#: pinned commit (the baseline to beat, never patched).
CONDITION_UPSTREAM = "upstream"

#: The adapted specmgr skills (Phases 110-150; not part of the Phase 100
#: smoke run).
CONDITION_SKILL = "skill"

#: Every condition the harness knows, in canonical order.
CONDITIONS: tuple[str, ...] = (CONDITION_NONE, CONDITION_UPSTREAM, CONDITION_SKILL)

#: The conditions whose results are cached across runs (Task 100.130): they
#: are content-pinned, so a rerun under the same version tuple and grader
#: hash is byte-for-byte the same measurement.
CACHEABLE_CONDITIONS: frozenset[str] = frozenset({CONDITION_NONE, CONDITION_UPSTREAM})

# ---------------------------------------------------------------------------
# model and provider (the shared sys0 vLLM server)
# ---------------------------------------------------------------------------

#: The OpenCode provider id the harness injects (REQ-008).
PROVIDER_ID = "vllm-sys0"

#: The vLLM OpenAI-compatible endpoint the harness PROBES from the host.
#: The shared vLLM server actually answers on `0.0.0.0:8081` (verified via
#: `ss -tlnp`; it is shared infrastructure and cannot be rebound), so the
#: `127.0.0.1` form works for the preflight and the contention sampler
#: under either bind. The trial containers reach the same server at the
#: per-run private network's GATEWAY IP (see :data:`NETWORK_MODE`):
#: preferably through the run's vLLM forwarder bound there, or directly
#: when the 0.0.0.0 bind already owns the gateway address:port -- the
#: option-C conditional in `runner.establish_vllm_access` (strictly
#: verified in that case). The trial's vLLM URL is mode-invariant.
VLLM_ENDPOINT = "http://127.0.0.1:8081/v1"


def vllm_host() -> str:
    """Return the host part of :data:`VLLM_ENDPOINT` (the forwarder's target).

    Returns:
        The host the shared vLLM server answers on the loopback (pinned to
        `127.0.0.1`).
    """
    host_port = VLLM_ENDPOINT.split("://", 1)[1].split("/", 1)[0]
    result = host_port.rsplit(":", 1)[0]
    return result


def vllm_host_port() -> int:
    """Return the port of :data:`VLLM_ENDPOINT` (the forwarder's bind/target port).

    The runner binds the vLLM forwarder to the private network's gateway IP
    on exactly this port, so a trial container's
    `http://<gateway>:<port>/v1` reaches the host's loopback-bound vLLM.

    Returns:
        The vLLM TCP port (pinned to 8081).
    """
    host_port = VLLM_ENDPOINT.split("://", 1)[1].split("/", 1)[0]
    result = int(host_port.rsplit(":", 1)[1])
    return result


#: The Prometheus metrics endpoint the runner uses for the idle/contention
#: checks (`vllm:num_requests_running`).
VLLM_METRICS_URL = "http://127.0.0.1:8081/metrics"

#: The model id served at :data:`VLLM_ENDPOINT` (verified via
#: ``GET /v1/models``: `max_model_len` 917504).
MODEL_ID = "qwen3.8-27b-bf16-896k"

#: The model's context limit as reported by the server (`max_model_len`).
MODEL_MAX_CONTEXT = 917504

#: The vLLM version recorded at pin time (``GET /version``); the preflight
#: re-reads it and aborts the run on a mismatch.
VLLM_VERSION_PIN = "0.26.0"

#: The speculative-decoding configuration the server was deployed with.
#: vLLM 0.26.0 exposes no external metrics for the speculative algorithm or
#: the number of draft tokens, so the preflight records this as "as
#: deployed, not externally verifiable" (Task 100.180 rule -- no guessing).
SPECULATIVE_CONFIG = {"method": "mtp", "num_speculative_tokens": 5, "externally_verifiable": False}

# ---------------------------------------------------------------------------
# sampling parameters (injected into the OpenCode config, recorded in the
# preflight -- Task 100.180)
# ---------------------------------------------------------------------------

#: Temperature: 0 for maximal trial-to-trial determinism.
SAMPLING_TEMPERATURE = 0.0

#: top_p: 1.0 (no nucleus filtering; with temperature 0 it is a no-op, kept
#: explicit so it is recorded).
SAMPLING_TOP_P = 1.0

#: seed: fixed so a rerun under the same version tuple samples the same way.
SAMPLING_SEED = 1337

#: The sampling block exactly as injected into the provider config.
SAMPLING_PARAMETERS: dict[str, object] = {
    "temperature": SAMPLING_TEMPERATURE,
    "topP": SAMPLING_TOP_P,
    "seed": SAMPLING_SEED,
}

# ---------------------------------------------------------------------------
# images (matching pair: the spike found the MCP and CLI six months apart
# still produced identical results; the pair is pinned together)
# ---------------------------------------------------------------------------

#: The OpenCode trial image (tag + digest). The runner pulls/runs the TAG;
#: the digest is the integrity pin the preflight enforces -- it aborts the
#: run when the locally stored image `RepoDigests` differ from this value.
OPENCODE_IMAGE = "ghcr.io/anomalyco/opencode:2.2.5"
OPENCODE_IMAGE_DIGEST = "sha256:1690aad69864d2f6714772d1e040918feebc6df5286d2bd7e181fbb35d12d4a9"

#: The Structurizr MCP sidecar image (the `parse`/`validate`/`inspect` tools
#: the agents under test may call).
STRUCTURIZR_MCP_IMAGE = "structurizr/mcp:2026.04.20"
STRUCTURIZR_MCP_IMAGE_DIGEST = "sha256:fc4ef98b7da925d62b08c71a90eb995a527fae30e2c04b39e3041f253c135539"

#: The Structurizr CLI image the graders use (`export -format json` + the
#: `validate`/`inspect` gates). Must match the MCP image's release pair.
STRUCTURIZR_CLI_IMAGE = "structurizr/structurizr:2026.10.26-noble"
STRUCTURIZR_CLI_IMAGE_DIGEST = "sha256:1081d615e7a539aee8b8360e36a58f42ff6412dd8f0e1b053134cb2c76ab2303"

# ---------------------------------------------------------------------------
# host tooling
# ---------------------------------------------------------------------------

#: The exact host Python the harness must run under (uv project Python).
PYTHON_VERSION_PIN = "3.13.13"

#: The exact `jq` version the graders run (host tool; recorded in the
#: preflight, asserted at run start).
JQ_VERSION_PIN = "1.6"

# ---------------------------------------------------------------------------
# upstream skills (fetched at run time, never vendored -- Task 100.110)
# ---------------------------------------------------------------------------

UPSTREAM_REPO = "jrjsmrtn/c4-skills"
UPSTREAM_REPO_URL = f"https://github.com/{UPSTREAM_REPO}.git"

#: The pinned upstream commit (re-verified against the GitHub API at pin
#: time, 2026-11-01; its LICENSE is MIT, see results/provenance.md).
UPSTREAM_SHA_PIN = "e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b"

#: The upstream skills mounted into the trial container for the
#: `upstream` condition, as directory names under the fetched repo's
#: ``skills/`` folder (verified against the pinned commit's tree).
UPSTREAM_SKILLS: tuple[str, ...] = ("c4-deployment", "c4-model", "c4-review", "structurizr-dsl")

# ---------------------------------------------------------------------------
# runner defaults
# ---------------------------------------------------------------------------

#: The trial containers' network topology (Phase 110, locked user directive):
#: every run owns one private Docker bridge network
#: (`docker network create --internal c4eval-<run_id>`) on which the trial
#: containers and the harness sidecar live, and where the vLLM access the
#: trial's config points at is served from the network's gateway IP (a host
#: interface address): the host-side vLLM forwarder bound there when it can
#: bind (preferred, best isolation), or the shared vLLM's own 0.0.0.0 bind
#: answering there directly when it already owns the address:port (the
#: option-C fallback, strictly verified). `--internal` means Docker enforces
#: NO route from that network to the outside world, so the agent under test
#: can only reach those two explicitly configured endpoints. It replaces the
#: Phase 100 `--network host` decision. Part of the version tuple: a change
#: here invalidates every cached baseline by design.
NETWORK_MODE = "internal-bridge"

#: Per-trial wall-clock timeout in seconds (Task 100.130: a timeout is a
#: failure, flagged separately).
TRIAL_TIMEOUT_S = 1200

#: How often the runner samples `vllm:num_requests_running` while a trial is
#: running (the contention flag).
CONTENTION_SAMPLE_INTERVAL_S = 30

#: How often the runner re-checks the idle state while waiting for vLLM to
#: drain between trials / before start.
IDLE_POLL_INTERVAL_S = 10

#: The number of trials per case and condition in a full run (REQ-008/
#: Measurement). The Phase 100 smoke run uses its own smaller k.
K_FULL = 5

#: The number of trials per case and condition for the Phase 100 smoke run
#: (Task 100.170) -- small enough to finish while the server is shared.
K_SMOKE = 2

#: The case set of the full run (Measurement); Phase 100 only exercises the
#: smoke case of it.
FULL_CASES: tuple[str, ...] = (
    "create-system",
    "fix-dsl",
    "mcp-limits",
    "design-views",
    "review-model",
    "no-trigger",
)

#: The Phase 100 smoke case (Task 100.170): the smallest shared case, used
#: to measure the real time per trial.
SMOKE_CASE = "smoke-create-system"

#: The Phase 110 held-out case (Task 110.100/110.140): the same task shape
#: as `create-system` in a different domain. Deliberately NOT part of
#: `FULL_CASES` -- a held-out case is never used while tuning and runs
#: once, at the end of its phase (Stop Rule).
HELDOUT_VALIDATE_CASE = "heldout-validate"

#: The Phase 120 held-out case (Task 120.100/120.140): the same task shape
#: as `fix-dsl` (a seeded broken workspace to repair) in a different
#: domain. Deliberately NOT part of `FULL_CASES` -- held out exactly like
#: `HELDOUT_VALIDATE_CASE`.
HELDOUT_DSL_CASE = "heldout-dsl"


def version_tuple() -> dict[str, object]:
    """Return the version tuple as a plain dict (REQ-008 reproducibility).

    The tuple is the set of pins that fully determine a trial's
    environment: the three images (tag + digest), the model and provider,
    the vLLM version pin, the host Python and jq versions, the upstream
    commit, the sampling parameters, the runner timeout and the trial
    network topology (Phase 110: `internal-bridge`, the per-run egress-
    blocking private network).

    Returns:
        A JSON-serialisable dict, sorted for stable hashing.
    """
    result: dict[str, object] = {
        "conditions_cacheable": sorted(CACHEABLE_CONDITIONS),
        "jq": JQ_VERSION_PIN,
        "model_id": MODEL_ID,
        "network_mode": NETWORK_MODE,
        "opencode_image": OPENCODE_IMAGE,
        "opencode_image_digest": OPENCODE_IMAGE_DIGEST,
        "python": PYTHON_VERSION_PIN,
        "provider_id": PROVIDER_ID,
        "sampling_parameters": dict(SAMPLING_PARAMETERS),
        "speculative_config": dict(SPECULATIVE_CONFIG),
        "structurizr_cli_image": STRUCTURIZR_CLI_IMAGE,
        "structurizr_cli_image_digest": STRUCTURIZR_CLI_IMAGE_DIGEST,
        "structurizr_mcp_image": STRUCTURIZR_MCP_IMAGE,
        "structurizr_mcp_image_digest": STRUCTURIZR_MCP_IMAGE_DIGEST,
        "trial_timeout_s": TRIAL_TIMEOUT_S,
        "upstream_sha": UPSTREAM_SHA_PIN,
        "vllm_endpoint": VLLM_ENDPOINT,
        "vllm_version": VLLM_VERSION_PIN,
    }
    result = dict(sorted(result.items()))
    return result


def version_tuple_hash() -> str:
    """Return the stable sha256 of the canonical JSON of the version tuple.

    Used as a result-cache key component (Task 100.130): any pin change
    invalidates every cached result.

    Returns:
        A 64-character lowercase hex digest.
    """
    canonical = json.dumps(version_tuple(), sort_keys=True, separators=(",", ":"))
    result = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return result


def skill_variant_hash(skill_files: list[tuple[str, bytes]]) -> str:
    """Return the stable content hash of a skill variant (Measurement).

    The hash is taken over the sorted ``(relative_path, sha256(content))``
    pairs of every file that makes up the condition's skills, so two
    variants with identical content hash equally regardless of fetch order
    or mtime. The `none` condition has no skill files and hashes the empty
    set.

    Args:
        skill_files: ``(path_relative_to_the_variant_root, file_bytes)``
            pairs, e.g. collected over a mounted skill directory.

    Returns:
        A 64-character lowercase hex digest.
    """
    assert isinstance(skill_files, list)
    pairs: list[tuple[str, str]] = []
    for rel_path, content in skill_files:
        assert isinstance(rel_path, str) and rel_path
        assert isinstance(content, (bytes, bytearray))
        pairs.append((rel_path, hashlib.sha256(bytes(content)).hexdigest()))
    pairs.sort()
    canonical = json.dumps(pairs, sort_keys=True, separators=(",", ":"))
    result = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return result


def source_hash(paths: list[str]) -> str:
    """Return the sha256 over the sorted bytes of the given source files.

    This is the ``grader_hash`` component of the result cache key
    (Task 100.130): a change to the graders or the case definitions
    invalidates the cached ``none``/``upstream`` results.

    Args:
        paths: Absolute paths of the files that define the gates being
            run (grader module + case module + fixture files).

    Returns:
        A 64-character lowercase hex digest.
    """
    assert paths, "source_hash requires at least one path"
    h = hashlib.sha256()
    for path in sorted(paths):
        assert isinstance(path, str) and path
        h.update(path.encode("utf-8"))
        h.update(b"\x00")
        with open(path, "rb") as f:
            h.update(f.read())
    result = h.hexdigest()
    return result
