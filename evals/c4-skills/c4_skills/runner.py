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

"""The trial runner (Task 100.130, reworked for the Phase 110 egress-
control change).

Sequential trials (one at a time, `-j 1` semantics): the planned (case,
condition, k) combinations are shuffled once with a recorded seed, and each
trial runs in its own fresh work dir and its own OpenCode container
(no host OpenCode config mounted, no `AGENTS.md`, no skills except the
condition's, web access denied by the injected config).

Network topology (the Phase 110 locked directive -- the agent under test
must never reach the external network unless explicitly configured): every
run owns one private Docker bridge network `c4eval-<run_id>` created with
`--internal` (Docker enforces NO egress from it). On that network live the
trial containers and the harness sidecar (its container IP), and the
vLLM access the trial's config points at the network's gateway IP
(a host interface address): PREFER the run's vLLM forwarder bound there
(proxying to the shared vLLM on the host loopback -- best isolation, the
gateway's only vLLM exposure is the forwarder); when that bind fails with
EADDRINUSE the shared vLLM already owns the gateway address:port (it
answers on 0.0.0.0), and the DIRECT path is used instead -- but only after
`establish_vllm_access` strictly verifies from the host that the pinned
vLLM server (exact version + model id) is what answers there (option C,
locked decision). The injected config's two endpoints are those two
addresses in BOTH modes -- nothing else is reachable from a trial. Each
trial container gets its own netns, which also removes the opencode
"managed service on a random host port" collision class that bit Phase 100
smoke run 1 (a killed-or-orphaned service held a host port the next trial's
container picked the same).

The shared-server rules (Measurement): the runner refuses to start while
vLLM reports running requests, re-checks (and waits) between trials, and
flags -- never fails -- a trial that ran while another client was active.
A per-trial timeout is a failure, flagged separately.

The event stream is captured into the gitignored work root (a sibling of
the trial's mounted work dir, never inside it) by a single non-following
`docker logs <name>` after the container stops, so no start-gap output is
lost; streams up to EVENT_FILE_COMMIT_LIMIT are committed into the
results dir, over-limit streams stay in the work dir and are flagged in
the trial record (`event_file_committed: false`, `event_file_bytes`).

The result cache (Task 100.130) reuses the `none`/`upstream` trial
summaries when (case, condition, version tuple, grader hash, skill variant
hash) all match, so skill iterations cost only the `skill` trials; the
per-trial cache hit/miss reason is recorded in `run.json`
(`cache_reason`). The `skill` condition takes its variant from
`RunConfig.skills_dir` (`load_skill_source`): the files are copied into
the trial work dir before the container starts and hashed with
`pins.skill_variant_hash`, which the run record carries.
"""

from __future__ import annotations

import errno
import json
import random
import shutil
import subprocess
import threading
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import forwarder, graders, metrics as metrics_mod, pins, preflight, sidecar
from .cache import CacheKey, ResultCache
from .cases import Case, get_case
from .events import ParsedTrial, parse_events_file
from .occonfig import OPENCODE_CONFIG_CONTENT_ENV, opencode_config_content
from .upstream import UpstreamSource, mount_skills_into

#: The in-container work dir (the trial's CWD).
CONTAINER_WORKDIR = "/work"

#: The event stream is committed with the trial record only up to this size.
#: An over-limit stream is NOT committed and NOT deleted: it stays in the
#: gitignored work dir (useful for debugging, the dir is never committed),
#: the trial record carries `event_file: null`, `event_file_committed:
#: false` and the stream's size in `event_file_bytes`.
EVENT_FILE_COMMIT_LIMIT = 2_000_000

#: The event types a trial's stream may legitimately start with (every
#: healthy stream opens with a `step_start`; a container that dies before
#: the first step emits a lone `error` event -- the smoke run 1 port
#: collision did). A captured stream whose first line is anything else is
#: suspect (truncated or wrong source) and is reported.
EVENT_STREAM_FIRST_TYPES: frozenset[str] = frozenset({"step_start", "error"})

#: The run id's time-stamp format (committed results are keyed by it).
RUN_ID_FORMAT = "%Y-%m-%dT%H%M%SZ"


@dataclass(frozen=True)
class TrialPlan:
    """One planned trial.

    Attributes:
        case_id: The case to run.
        condition: The condition (`none`/`upstream`/`skill`).
        k_index: The trial's index within its (case, condition) pair (0-based).
    """

    case_id: str
    condition: str
    k_index: int


@dataclass
class TrialRecord:
    """The full record of one trial (the cache unit and the report input).

    Attributes:
        plan: The TrialPlan.
        run_id: The run identifier.
        workdir: The host work dir path.
        started_at: ISO-8601 UTC start time.
        finished_at: ISO-8601 UTC end time.
        wall_time_s: Measured wall time (None when it could not be measured).
        exit_code: The `opencode run` exit code (None on timeout/kill).
        timeout: The per-trial timeout fired (a failure, flagged).
        contended: Another client ran vLLM while this trial ran (flagged,
            not failed).
        idle_wait_s: Seconds the runner waited for vLLM to drain before
            starting this trial.
        cached: The summary came from the result cache (no trial run).
        cache_reason: Why the cache was or was not used for this trial
            (`hit` / `miss:file-absent` / `miss:key-mismatch` /
            `miss:file-unparseable` / `miss:trial-absent` / `n/a` when the
            condition is not cacheable). Additive field: pre-existing
            records parse via the default.
        event_file: The committed event stream file (relative to the run
            results dir), or None (over-limit streams stay in the work dir).
        event_file_bytes: The captured event stream's size in bytes (None
            when no stream was captured).
        event_file_committed: The event stream was committed with the
            record (False for over-limit and uncommitted streams).
        skills_installed: The skill names the condition installed into the
            work dir before the agent started (empty for `none`). Additive
            field: pre-existing records parse via the default.
        gates: The GateResult dicts, in the case's order.
        passed: Every gate passed and no timeout.
        metrics: The TrialMetrics JSON.
    """

    plan: TrialPlan
    run_id: str
    workdir: str
    started_at: str
    finished_at: str
    wall_time_s: float | None
    exit_code: int | None
    timeout: bool
    contended: bool
    idle_wait_s: float
    cached: bool
    event_file: str | None
    gates: list[dict] = field(default_factory=list)
    passed: bool = False
    metrics: dict = field(default_factory=dict)
    cache_reason: str = "n/a"
    event_file_bytes: int | None = None
    event_file_committed: bool = False
    skills_installed: list[str] = field(default_factory=list)

    def to_json(self) -> dict:
        """Return the JSON-serialisable record (the cache unit)."""
        result = asdict(self)
        return result


def plan_trials(case_ids: list[str], conditions: list[str], k: int, seed: int) -> list[TrialPlan]:
    """Build the shuffled trial plan (conditions interleaved, seed recorded).

    Args:
        case_ids: The cases to run.
        conditions: The conditions to run.
        k: Trials per (case, condition).
        seed: The shuffle seed (recorded with the run).

    Returns:
        The ordered list of TrialPlans (all `k * len(cases) * len(conditions)`
        combinations, shuffled once).
    """
    assert case_ids, "no cases"
    assert conditions, "no conditions"
    if k <= 0:
        raise ValueError(f"k must be > 0, got {k}")
    combos = [TrialPlan(case_id, condition, ki) for case_id in case_ids for condition in conditions for ki in range(k)]
    rng = random.Random(seed)
    rng.shuffle(combos)
    result = combos
    return result


def _trial_workdir_name(plan: TrialPlan, run_id: str) -> str:
    """Return the flat work dir name for one trial."""
    result = f"{plan.case_id}.{plan.condition}-k{plan.k_index}.{run_id}"
    return result


def _start_contended_sampler() -> tuple[list[int], threading.Thread, threading.Event]:
    """Start sampling vLLM running requests while a trial runs.

    The sample list is a single-consumer queue in practice (one sampler
    thread appends, the runner reads it after joining), so no lock is
    needed.

    Returns:
        (samples, thread, stop_event): the observed running-request counts,
        the sampler thread, and the event that stops it.
    """
    samples: list[int] = []
    stop_event = threading.Event()

    def sample_loop() -> None:
        while not stop_event.wait(pins.CONTENTION_SAMPLE_INTERVAL_S):
            seen = preflight.vllm_running_requests()
            if seen is not None:
                samples.append(seen)

    thread = threading.Thread(target=sample_loop, name="c4eval-contention-sampler", daemon=True)
    thread.start()
    result: tuple[list[int], threading.Thread, threading.Event] = (samples, thread, stop_event)
    return result


def _was_contended(samples: list[int]) -> bool:
    """Return True iff another client ran vLLM while the trial ran.

    The trial's own request accounts for one running request; a sample
    above that means a second (foreign) client was active.
    """
    result = any(s > 1 for s in samples)
    return result


#: The trial container name prefix (the timeout kill addresses the container
#: by name -- killing the `docker run` client alone would orphan the
#: container and its vLLM sequence slot. Phase 100 additionally had the
#: orphaned opencode managed service hold a host-network port for the next
#: trial; the Phase 110 private network removed that class -- each trial
#: container now has its own netns, so a killed container's ports die with
#: it).
TRIAL_CONTAINER_PREFIX = "c4eval-trial-"

#: The poll interval while waiting for a trial container to exit.
CONTAINER_POLL_S = 2.0

#: The per-run network name prefix (one `--internal` bridge network per run
#: id, `c4eval-<run_id>`; the sidecar and every trial container join it,
#: and the vLLM forwarder binds its gateway IP).
NETWORK_PREFIX = "c4eval-"


def network_name_for(run_id: str) -> str:
    """Return the per-run private network name (derived from the run id).

    No CLI flag: the network is 1:1 with the run, exactly like the sidecar
    container name.

    Args:
        run_id: The run identifier.

    Returns:
        The network name (`c4eval-<run_id>`).
    """
    result = f"{NETWORK_PREFIX}{run_id}"
    return result


def create_run_network(name: str) -> None:
    """Create the run's private `--internal` bridge network.

    `--internal` makes Docker enforce that containers on the network have
    no route to the outside world (the egress block of the Phase 110
    locked directive); the default bridge subnet is used (the runner does
    not need to know the subnet -- only the gateway, which it resolves
    afterwards).

    Args:
        name: The network name (`c4eval-<run_id>`).

    Raises:
        RuntimeError: When docker cannot create the network (docker
            unavailable, or a same-name network the sweep missed).
    """
    assert isinstance(name, str) and name
    proc = subprocess.run(  # noqa: S603 -- fixed name
        ["docker", "network", "create", "--internal", name],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"docker network create {name} failed: {proc.stderr.strip()}")


def remove_run_network(name: str) -> None:
    """Remove the run's private network (best-effort, never raises).

    Teardown runs in a `finally` after the sidecar stop; a failure here
    must not mask the run's outcome (the next run's sweep catches the
    leftover).
    """
    assert isinstance(name, str) and name
    try:
        subprocess.run(  # noqa: S603 -- fixed name
            ["docker", "network", "rm", name],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass


def sweep_run_networks() -> list[str]:
    """Remove every leftover `c4eval-*` network (best-effort, never raises).

    Safety sweep at run start, next to :func:`sweep_trial_containers` (a
    crashed run can leave its per-run network behind). The harness assumes
    single-run-per-host, exactly like the sidecar-staleness check: a live
    `c4eval-mcp-*` container already refuses the run, so any network
    carrying the prefix at this point is a crash leftover, not a
    concurrent run's.

    Returns:
        The removed network names.
    """
    try:
        proc = subprocess.run(  # noqa: S603 -- fixed filter
            ["docker", "network", "ls", "--filter", f"name={NETWORK_PREFIX}", "--format", "{{.Name}}"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    removed: list[str] = []
    for name in (proc.stdout or "").splitlines():
        net_name = name.strip()
        if not net_name:
            continue
        try:
            subprocess.run(["docker", "network", "rm", net_name], capture_output=True, text=True, timeout=60)  # noqa: S603
        except (OSError, subprocess.TimeoutExpired):
            pass
        removed.append(net_name)
    result = removed
    return result


def network_gateway_ip(name: str) -> str:
    """Return the run network's gateway IP (the vLLM access address).

    The gateway is a host interface address: the host may bind it (the
    forwarder's preferred address), and the host reaches every container
    on the network through it (while the `--internal` flag keeps the
    containers' own egress blocked). The trial's vLLM endpoint is always
    this address on vLLM's port, in either access mode.

    Args:
        name: The network name.

    Returns:
        The gateway IPv4 address.

    Raises:
        RuntimeError: When docker cannot inspect the network, or the
            network has no gateway (no vLLM access address for the trial).
    """
    assert isinstance(name, str) and name
    proc = subprocess.run(  # noqa: S603 -- fixed name
        ["docker", "network", "inspect", name, "--format", "{{(index .IPAM.Config 0).Gateway}}"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"docker network inspect {name} failed: {proc.stderr.strip()}")
    gateway = proc.stdout.strip()
    if not gateway:
        raise RuntimeError(f"network {name} has no gateway IP (no vLLM access address for the trial)")
    result = gateway
    return result


def _gateway_http_json(url: str, timeout_s: float = 5.0) -> dict | None:
    """GET one JSON document from the host; None on any failure.

    The option-C verification probes (strict, from the host). A failure
    here is a verification failure, not a harness crash: the caller names
    what it found and aborts the run before any trial.
    """
    try:
        with urllib.request.urlopen(url, timeout=timeout_s) as response:  # noqa: S310 -- the run's own gateway IP (a host interface address)
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
        return None


def _verify_direct_vllm(gateway_ip: str) -> None:
    """Strictly verify that the PINNED vLLM server answers on the gateway's vLLM port.

    The option-C fallback (the shared vLLM's own 0.0.0.0 bind already owns
    the gateway address:port) is legal only when what answers there really
    is the pinned server -- a permissive "something answers on 8081" is a
    pin violation. Both checks run from the host and are exact:

    - `GET http://<gateway_ip>:<port>/version` must be JSON whose
      `version` equals `pins.VLLM_VERSION_PIN`;
    - `GET http://<gateway_ip>:<port>/v1/models` must be JSON whose
      `data` list contains `pins.MODEL_ID`.

    Args:
        gateway_ip: The run network's gateway IP.

    Raises:
        RuntimeError: When either check fails (unreachable, non-JSON, a
            different version, or a different model set) -- the message
            names what was found, and the run must abort before any trial.
    """
    assert isinstance(gateway_ip, str) and gateway_ip
    port = pins.vllm_host_port()
    version_doc = _gateway_http_json(f"http://{gateway_ip}:{port}/version")
    version = version_doc.get("version") if isinstance(version_doc, dict) else None
    if version != pins.VLLM_VERSION_PIN:
        raise RuntimeError(
            f"direct vLLM access unverified: GET http://{gateway_ip}:{port}/version answered {version!r} "
            f"(expected the pinned version {pins.VLLM_VERSION_PIN!r}); something else answers on the "
            "vLLM port at the run's gateway -- aborting before any trial"
        )
    models_doc = _gateway_http_json(f"http://{gateway_ip}:{port}/v1/models")
    model_ids: list[str] = []
    if isinstance(models_doc, dict):
        for entry in models_doc.get("data") or []:
            if isinstance(entry, dict):
                model_ids.append(str(entry.get("id")))
    if pins.MODEL_ID not in model_ids:
        raise RuntimeError(
            f"direct vLLM access unverified: GET http://{gateway_ip}:{port}/v1/models does not serve "
            f"{pins.MODEL_ID!r} (served: {model_ids}); aborting before any trial"
        )


def establish_vllm_access(gateway_ip: str) -> tuple[forwarder.ForwarderHandle | None, str]:
    """Establish the run's vLLM access on the private network (option C, conditional).

    PREFERRED: the vLLM forwarder bound to `<gateway_ip>:<vllm_port>`
    (best isolation -- the gateway's only vLLM exposure is the forwarder's).
    When that bind fails with EADDRINUSE, the shared vLLM server itself
    already owns the gateway address:port (it answers on 0.0.0.0) -- the
    DIRECT path is then used, but only after :func:`_verify_direct_vllm`
    strictly verified from the host that the pinned server (exact version
    + model id) is what answers there. Any OTHER bind error is a genuine
    harness failure and propagates unchanged. The trial's vLLM endpoint
    URL is mode-invariant: `http://<gateway_ip>:<vllm_port>/v1` in both
    modes -- that is the point.

    Args:
        gateway_ip: The run network's gateway IP (a host interface address).

    Returns:
        (handle, mode): the forwarder handle (None in direct mode) and the
        access mode (`"forwarder"` | `"direct-0.0.0.0-bind"`), recorded
        with the run (preflight extra `vllm_access`).

    Raises:
        RuntimeError: EADDRINUSE with something other than the pinned vLLM
            server answering on the gateway's vLLM port (a pin violation;
            the run must abort before any trial).
        OSError: Any other bind error (not EADDRINUSE) -- propagated.
    """
    assert isinstance(gateway_ip, str) and gateway_ip
    try:
        handle = forwarder.start_forwarder(
            bind_ip=gateway_ip,
            bind_port=pins.vllm_host_port(),
            target_ip=pins.vllm_host(),
            target_port=pins.vllm_host_port(),
        )
    except OSError as exc:
        if exc.errno != errno.EADDRINUSE:
            raise  # a genuine harness failure, not a fallback trigger
        _verify_direct_vllm(gateway_ip)  # raises when the pin is not verified
        result: tuple[forwarder.ForwarderHandle | None, str] = (None, "direct-0.0.0.0-bind")
        return result
    result = (handle, "forwarder")
    return result


def _docker_inspect(container_name: str, template: str) -> str:
    """Run `docker inspect <container> --format <template>` (text answer)."""
    proc = subprocess.run(  # noqa: S603 -- fixed container name + template
        ["docker", "inspect", container_name, "--format", template],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"docker inspect {container_name} failed: {proc.stderr.strip()}")
    result = proc.stdout.strip()
    return result


def _capture_full_logs(container_name: str, log_path: Path) -> None:
    """Write the container's FULL log to `log_path` (single, non-following).

    One `docker logs <name>` after the container has exited (or been
    killed) captures everything it emitted -- a `docker logs -f --tail 0`
    started AFTER `docker run` would miss the output produced in the gap
    between the two calls. The capture runs before the `docker rm`, so the
    logs are still available. A capture failure (container already gone,
    docker error) leaves an empty file in place and never raises: the
    parse tolerates empty/truncated streams and the trial's own outcome
    (exit code, gates) is unaffected.
    """
    try:
        with open(log_path, "w", encoding="utf-8") as log_file:
            subprocess.run(  # noqa: S603 -- fixed container name
                ["docker", "logs", container_name],
                stdout=log_file,
                stderr=subprocess.DEVNULL,
                timeout=120,
            )
    except (OSError, subprocess.TimeoutExpired):
        pass


def _stream_first_type(path: Path) -> str | None:
    """Return the `type` token of the stream's first event line (or None).

    The cheap integrity check for a captured stream: every healthy trial
    stream opens with a `step_start`, a container that dies before its
    first step emits a lone `error` event; anything else (including an
    empty file) is suspect.
    """
    try:
        with open(path, encoding="utf-8") as file:
            first_line = file.readline().strip()
    except OSError:
        return None
    if not first_line:
        return None
    try:
        event = json.loads(first_line)
    except json.JSONDecodeError:
        return None
    if not isinstance(event, dict):
        return None
    result: str | None = str(event.get("type") or None)
    return result


def _run_opencode_container(
    workdir: Path,
    case: Case,
    *,
    network: str,
    vllm_base_url: str,
    mcp_url: str,
    timeout_s: int,
    log_path: Path,
    container_name: str,
) -> tuple[int | None, bool, float]:
    """Run one trial container (detached) and capture its event output.

    The container joins the run's private `--internal` network (its own
    netns -- the egress block plus the removal of the Phase 100
    host-network managed-service port collision class) and is given
    exactly two endpoints in the injected config: `vllm_base_url` (the
    vLLM forwarder on the network's gateway IP) and `mcp_url` (the sidecar
    on its container IP).

    The container is addressed by name throughout: on timeout the harness
    sends `docker kill` to the CONTAINER (never just to the client), so a
    timed-out trial cannot orphan a process that keeps a vLLM sequence
    slot. The exit code comes from `docker inspect`
    (`{{.State.ExitCode}}` -- the same value `docker wait` would report),
    so a killed (timed-out) trial keeps its exit code of None plus the
    timeout flag. The event stream is captured AFTER the container stops,
    by one non-following `docker logs <name>` (the full log; no start gap
    can lose output).

    Returns:
        (exit_code, timed_out, wall_time_s). The exit code is None when the
        timeout fired.
    """
    assert workdir.is_dir()
    assert container_name.startswith(TRIAL_CONTAINER_PREFIX)
    run_cmd = [
        "docker",
        "run",
        "-d",
        "--name",
        container_name,
        "--network",
        network,
        *preflight.host_user_flags(),
        "-e",
        "HOME=/tmp/oc-home",
        "-w",
        CONTAINER_WORKDIR,
        "-v",
        f"{workdir}:{CONTAINER_WORKDIR}",
        "-e",
        f"{OPENCODE_CONFIG_CONTENT_ENV}={opencode_config_content(vllm_base_url=vllm_base_url, mcp_url=mcp_url)}",
        pins.OPENCODE_IMAGE,
        "run",
        "--format",
        "json",
        "--model",
        f"{pins.PROVIDER_ID}/{pins.MODEL_ID}",
        case.prompt,
    ]
    proc = subprocess.run(run_cmd, capture_output=True, text=True, timeout=120)  # noqa: S603 -- fixed pinned image
    if proc.returncode != 0:
        raise RuntimeError(f"trial container start failed: {proc.stderr.strip()}")

    started = time.monotonic()
    timed_out = False
    exit_code: int | None = None
    deadline = started + timeout_s
    try:
        while True:
            status = _docker_inspect(container_name, "{{.State.Status}}")
            if status != "running":
                break
            if time.monotonic() >= deadline:
                timed_out = True
                subprocess.run(["docker", "kill", container_name], capture_output=True, timeout=60)  # noqa: S603
                break
            time.sleep(CONTAINER_POLL_S)
        if not timed_out:
            exit_code = int(_docker_inspect(container_name, "{{.State.ExitCode}}"))
        _capture_full_logs(container_name, log_path)
    finally:
        subprocess.run(["docker", "rm", "-f", container_name], capture_output=True, timeout=60)  # noqa: S603
    wall = time.monotonic() - started
    result: tuple[int | None, bool, float] = (exit_code, timed_out, wall)
    return result


def _write_setup_files(workdir: Path, case: Case) -> None:
    """Place the case's setup files into the fresh work dir."""
    for rel, text in case.setup_files.items():
        target = workdir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


@dataclass(frozen=True)
class EventCommit:
    """The event-stream commit decision of one trial (D2).

    Attributes:
        event_file: The committed stream's path relative to the run's
            results dir (None when the stream was not committed).
        event_file_bytes: The captured stream's size in bytes (None when
            no stream was captured at all).
        event_file_committed: The stream was copied into the results dir.
    """

    event_file: str | None
    event_file_bytes: int | None
    event_file_committed: bool


def commit_event_stream(event_source: Path, event_path: Path, results_dir: Path) -> EventCommit:
    """Copy the trial's event stream into the results dir when it fits.

    The stream is captured in the gitignored work dir (never inside the
    trial's mounted work dir, where the agent would see it); only streams
    up to EVENT_FILE_COMMIT_LIMIT are copied into the committed results
    dir. An over-limit stream is kept in the work dir for debugging and
    flagged in the decision (`event_file_committed` False, size recorded)
    instead of being summarized or deleted.

    Args:
        event_source: The captured stream in the work root.
        event_path: Where the committed stream lands (results dir).
        results_dir: The run's results dir (the event_file base).

    Returns:
        The EventCommit decision.
    """
    assert isinstance(event_source, Path) and isinstance(event_path, Path)
    if not event_source.is_file():
        return EventCommit(event_file=None, event_file_bytes=None, event_file_committed=False)
    size = event_source.stat().st_size
    if size > EVENT_FILE_COMMIT_LIMIT:
        return EventCommit(event_file=None, event_file_bytes=size, event_file_committed=False)
    event_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(event_source, event_path)
    result = EventCommit(
        event_file=str(event_path.relative_to(results_dir)),
        event_file_bytes=size,
        event_file_committed=True,
    )
    return result


@dataclass(frozen=True)
class SkillSource:
    """A verified `skill`-condition variant (Phases 110-150).

    Attributes:
        skills_root: The directory that contains the skill folders (the
            variant root; files are hashed relative to it, the same shape
            as `UpstreamSource.files`).
        skills: The skill folder names found under `skills_root`.
        files: Every skill file as (path relative to `skills_root`,
            bytes) -- the input of `pins.skill_variant_hash`.
    """

    skills_root: Path
    skills: tuple[str, ...]
    files: list[tuple[str, bytes]]


def load_skill_source(path: Path) -> SkillSource:
    """Load and verify one `skill` variant directory (pure filesystem read).

    `path` is either a variant root (one or more direct subfolders that
    each carry a `SKILL.md`) or a single skill folder (itself carrying a
    `SKILL.md`); the files are hashed relative to the containing skills
    root in both shapes, so the same content hashes equally from either.

    Args:
        path: The variant directory on the host.

    Returns:
        The verified SkillSource.

    Raises:
        ValueError: When the directory is missing or carries no skill
            folder (a usage error, mapped to exit code 2).
    """
    assert isinstance(path, Path)
    path = path.resolve()
    if not path.is_dir():
        raise ValueError(f"skills dir does not exist: {path}")
    if (path / "SKILL.md").is_file():
        skills_root = path.parent
        skill_dirs = (path.name,)
    else:
        skills_root = path
        skill_dirs = tuple(sorted(p.name for p in path.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()))
    if not skill_dirs:
        raise ValueError(f"no skill folder (a directory carrying a SKILL.md) in {path}")
    files: list[tuple[str, bytes]] = []
    for skill in skill_dirs:
        for file_path in sorted((skills_root / skill).glob("**/*")):
            if file_path.is_file():
                files.append((file_path.relative_to(skills_root).as_posix(), file_path.read_bytes()))
    result = SkillSource(skills_root=skills_root, skills=skill_dirs, files=files)
    return result


def _copy_skill_folders(workdir: Path, source: SkillSource) -> list[str]:
    """Copy a verified skill variant into the trial work dir.

    The target is `<workdir>/.opencode/skills/<name>/` (opencode 2.x's
    project skill location, the same layout `mount_skills_into` uses for
    the `upstream` condition). Returns the skill names copied.
    """
    assert workdir.is_dir()
    target_root = workdir / ".opencode" / "skills"
    copied: list[str] = []
    for skill in source.skills:
        src = source.skills_root / skill
        dst = target_root / skill
        dst.mkdir(parents=True, exist_ok=True)
        for path in src.rglob("*"):
            if path.is_file():
                rel = path.relative_to(src)
                out = dst / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(path.read_bytes())
        copied.append(skill)
    result = copied
    return result


def _install_skills(
    workdir: Path,
    condition: str,
    upstream: UpstreamSource | None,
    skill_source: SkillSource | None = None,
) -> list[str]:
    """Install the condition's skills into the work dir (returns the names).

    Runs BEFORE the trial container starts. `none`: nothing. `upstream`:
    the fetched, unmodified upstream skills. `skill`: the verified variant
    directory (Phases 110-150 pass it through `RunConfig.skills_dir`; the
    files are copied in here, so the trial's work dir always carries them
    before the agent sees anything).
    """
    assert condition in pins.CONDITIONS
    if condition == pins.CONDITION_NONE:
        return []
    if condition == pins.CONDITION_UPSTREAM:
        if upstream is None:
            raise RuntimeError("the upstream condition needs a verified upstream source")
        return mount_skills_into(workdir, upstream)
    if skill_source is None:
        raise ValueError("the skill condition needs a verified skill source (RunConfig.skills_dir)")
    return _copy_skill_folders(workdir, skill_source)


def run_trial(
    plan: TrialPlan,
    *,
    run_id: str,
    workroot: Path,
    results_dir: Path,
    network: str,
    vllm_base_url: str,
    mcp_url: str,
    upstream: UpstreamSource | None,
    timeout_s: int = pins.TRIAL_TIMEOUT_S,
    skill_source: SkillSource | None = None,
    cache_reason: str = "n/a",
) -> TrialRecord:
    """Run one trial end to end (container + graders + metrics + record).

    The event stream is captured into the gitignored work root (a sibling
    of the trial's mounted work dir -- never inside it, where the agent
    would see it) and committed into the results dir when it fits
    (`commit_event_stream`); the metrics always parse the captured stream,
    over-limit or not.

    Args:
        plan: The TrialPlan.
        run_id: The run identifier (work dir + record naming).
        workroot: The gitignored trial work dir root.
        results_dir: The committed results dir for this run.
        network: The run's private `--internal` network name (the trial
            container joins it).
        vllm_base_url: The vLLM endpoint as reachable from the trial
            (`http://<gateway_ip>:8081/v1`, through the run's forwarder).
        mcp_url: The sidecar endpoint as reachable from the trial
            (`http://<sidecar_ip>:<port>/mcp`).
        upstream: The verified upstream source (the `upstream` condition).
        timeout_s: The per-trial wall-clock timeout.
        skill_source: The verified skill variant (the `skill` condition).
        cache_reason: The result-cache outcome for this trial (recorded
            with it; a fresh trial carries the lookup's miss reason or
            `n/a` for non-cacheable conditions).

    Returns:
        The TrialRecord.
    """
    case = get_case(plan.case_id)
    workdir = workroot / _trial_workdir_name(plan, run_id)
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)
    _write_setup_files(workdir, case)
    skills_installed = _install_skills(workdir, plan.condition, upstream, skill_source)

    trial_dir = results_dir / "trials" / plan.case_id
    trial_dir.mkdir(parents=True, exist_ok=True)
    record_name = f"{plan.condition}-k{plan.k_index}"
    event_path = trial_dir / f"{record_name}.events.ndjson"
    event_source = workroot / f"{_trial_workdir_name(plan, run_id)}.events.ndjson"

    idle, last_seen, idle_wait = preflight.wait_until_idle(budget_s=3600.0, poll_s=pins.IDLE_POLL_INTERVAL_S)
    if not idle:
        raise RuntimeError(
            f"vLLM was still busy after {idle_wait:.0f}s of waiting (last seen {last_seen} running request(s)); "
            "refusing to start a trial that is guaranteed to be contended"
        )
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    samples, sampler_thread, stop_event = _start_contended_sampler()
    container_name = f"{TRIAL_CONTAINER_PREFIX}{run_id}.{plan.case_id}.{plan.condition}-k{plan.k_index}"
    exit_code, timed_out, wall = _run_opencode_container(
        workdir,
        case,
        network=network,
        vllm_base_url=vllm_base_url,
        mcp_url=mcp_url,
        timeout_s=timeout_s,
        log_path=event_source,
        container_name=container_name,
    )
    stop_event.set()
    sampler_thread.join(timeout=5.0)
    contended = _was_contended(samples)
    finished_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    first_type = _stream_first_type(event_source)
    if first_type not in EVENT_STREAM_FIRST_TYPES:
        print(
            f"warning: trial {record_name} event stream does not open with a step_start/error event "
            f"(first type: {first_type!r}); the capture may be truncated"
        )

    inputs = graders.collect_inputs(workdir)
    if event_source.is_file():
        parsed = parse_events_file(event_source)
    else:
        parsed = ParsedTrial()
    trial_metrics = metrics_mod.compute_metrics(
        parsed,
        inputs,
        timeout=timed_out,
        contended=contended,
    )
    gate_results = graders.grade_case(
        graders.GateContext(
            inputs=inputs,
            case=case,
            trial=parsed,
            metrics=trial_metrics,
            skills_installed=tuple(skills_installed),
        )
    )
    passed = graders.case_passed(gate_results) and not timed_out

    commit = commit_event_stream(event_source, event_path, results_dir)

    record = TrialRecord(
        plan=plan,
        run_id=run_id,
        workdir=str(workdir),
        started_at=started_at,
        finished_at=finished_at,
        wall_time_s=wall,
        exit_code=exit_code,
        timeout=timed_out,
        contended=contended,
        idle_wait_s=idle_wait,
        cached=False,
        event_file=commit.event_file,
        gates=[asdict(g) for g in gate_results],
        passed=passed,
        metrics=trial_metrics.to_json(),
        cache_reason=cache_reason,
        event_file_bytes=commit.event_file_bytes,
        event_file_committed=commit.event_file_committed,
        skills_installed=skills_installed,
    )
    return record


def sweep_trial_containers() -> list[str]:
    """Kill and remove every leftover `c4eval-trial-*` container.

    Safety sweep (a previous crashed run may have left a trial container
    behind, still holding a vLLM sequence slot; the run's own network
    leftover is the :func:`sweep_run_networks` counterpart). Returns the
    removed container ids.
    """
    proc = subprocess.run(  # noqa: S603 -- fixed filter
        ["docker", "ps", "-aq", "--filter", f"name={TRIAL_CONTAINER_PREFIX}"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    removed: list[str] = []
    for container_id in (proc.stdout or "").splitlines():
        cid = container_id.strip()
        if not cid:
            continue
        subprocess.run(["docker", "rm", "-f", cid], capture_output=True, text=True, timeout=60)  # noqa: S603
        removed.append(cid)
    result = removed
    return result


def grader_source_paths() -> list[Path]:
    """Return the source files that define the gates and the metrics.

    Their combined hash is the `grader_hash` of the result cache key: a
    change to any of them invalidates the cached `none`/`upstream` results.
    The set includes `codemode.py` -- the Code Mode detection layer whose
    conservative attribution rules feed the normalized MCP-call view every
    stream-derived metric and gate counts over (added 2026-11-07, the
    Phase 110 review remediation: it was missing, so a change to the
    attribution rules alone would not have invalidated the cache).
    """
    import c4_skills  # the harness package root (tests/evals put it on sys.path)

    root = Path(c4_skills.__file__).parent
    result = [
        root / "graders.py",
        root / "metrics.py",
        root / "codemode.py",
        root / "events.py",
        root / "cases" / "__init__.py",
        root / "pins.py",
    ]
    return result


@dataclass(frozen=True)
class RunConfig:
    """One harness run (the `run` subcommand's parameters).

    Attributes:
        run_id: The run identifier (results dir name, sidecar name).
        case_ids: The cases to run.
        conditions: The conditions to run.
        k: Trials per (case, condition).
        seed: The order-shuffle seed (recorded with the run).
        workroot: The gitignored trial work dir root.
        results_dir: The committed results dir for this run.
        cache_root: The gitignored result cache dir.
        timeout_s: The per-trial wall-clock timeout.
        label: A short run label for the report (e.g. `smoke`).
        skills_dir: The `skill` condition's variant directory (required
            iff `skill` is in `conditions`; see `load_skill_source`).
        network_name: The run's private network name (additive; empty
            derives `c4eval-<run_id>` -- no CLI flag, the network is 1:1
            with the run).
    """

    run_id: str
    case_ids: list[str]
    conditions: list[str]
    k: int
    seed: int
    workroot: Path
    results_dir: Path
    cache_root: Path
    timeout_s: int = pins.TRIAL_TIMEOUT_S
    label: str = ""
    skills_dir: Path | None = None
    network_name: str = ""


def _write_trial_record(results_dir: Path, record: TrialRecord) -> Path:
    """Write one trial record next to its event stream (committed)."""
    trial_dir = results_dir / "trials" / record.plan.case_id
    trial_dir.mkdir(parents=True, exist_ok=True)
    path = trial_dir / f"{record.plan.condition}-k{record.plan.k_index}.json"
    path.write_text(json.dumps(record.to_json(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def run(config: RunConfig) -> dict:
    """Run one full harness measurement (the Task 100.130 runner).

    Sequence: refuse a stale sidecar, sweep leftover trial containers and
    run networks, preflight (pins + idle), create the run's private
    `--internal` network (`c4eval-<run_id>`), start the pinned sidecar on
    it, establish the vLLM access on the network's gateway IP (option C:
    the forwarder preferred, a strictly-verified direct bind when the
    forwarder's bind is already owned), verify upstream when needed, plan
    the shuffled trial order (seed recorded), run every trial sequentially
    (cached `none`/`upstream` trials are reused, not reordered), write the
    per-trial records + `run.json`, and tear down in order: forwarder (when
    in use), sidecar, network. The report is built by the caller.

    Args:
        config: The RunConfig.

    Returns:
        The run record (the `run.json` payload).

    Raises:
        RuntimeError: When the preflight pin check fails, the run network
            cannot be created or has no gateway, or the sidecar does not
            come up.
        ValueError: When the `skill` condition is used without (or with a
            malformed) `skills_dir`, or `skills_dir` is given without the
            `skill` condition (usage errors; the CLI maps them to exit 2).
    """
    assert config.case_ids and config.conditions
    if pins.CONDITION_SKILL in config.conditions:
        if config.skills_dir is None:
            raise ValueError("the skill condition needs a variant directory (RunConfig.skills_dir)")
        skill_source = load_skill_source(config.skills_dir)
    elif config.skills_dir is not None:
        raise ValueError("skills_dir is only valid when the skill condition is run")
    else:
        skill_source = None
    network = config.network_name or network_name_for(config.run_id)
    stale = sidecar.sidecar_container_list()
    if stale:
        raise RuntimeError(f"stale c4eval-mcp sidecar(s) still running: {stale}; tear them down first")
    swept = sweep_trial_containers()
    if swept:
        print(f"swept {len(swept)} leftover trial container(s): {swept}")
    swept_networks = sweep_run_networks()
    if swept_networks:
        print(f"swept {len(swept_networks)} leftover run network(s): {swept_networks}")

    upstream: UpstreamSource | None = None
    if pins.CONDITION_UPSTREAM in config.conditions:
        from .upstream import ensure_upstream

        upstream = ensure_upstream(config.cache_root / "upstream")

    preflight_result = preflight.run_preflight(
        conditions=list(config.conditions),
        upstream_source=upstream,
        extra={
            "run_id": config.run_id,
            "label": config.label,
            "seed": config.seed,
            "k": config.k,
            "cases": list(config.case_ids),
            "trial_timeout_s": config.timeout_s,
            "version_tuple_hash": pins.version_tuple_hash(),
            "host_addr": preflight.local_host_addr(),
            "network_mode": pins.NETWORK_MODE,
            "network_name": network,
        },
    )
    if not preflight_result.ok:
        preflight.write_preflight(config.results_dir / "preflight.json", preflight_result)
        raise RuntimeError("preflight pin check failed: " + "; ".join(preflight_result.problems))

    handle: sidecar.SidecarHandle | None = None
    forwarder_handle: forwarder.ForwarderHandle | None = None
    try:
        create_run_network(network)
        handle = sidecar.start_sidecar(config.run_id, network)
        gateway_ip = network_gateway_ip(network)
        # option C (conditional): the forwarder is preferred; an EADDRINUSE
        # bind (the shared vLLM already owns the gateway address:port) falls
        # back to the direct path after strict pin verification. The trial's
        # vLLM URL is the same in both modes.
        forwarder_handle, vllm_access = establish_vllm_access(gateway_ip)
        vllm_base_url = f"http://{gateway_ip}:{pins.vllm_host_port()}/v1"
        mcp_url = f"http://{handle.ip}:{handle.port}/mcp"
        preflight_result = preflight.run_preflight(
            conditions=list(config.conditions),
            upstream_source=upstream,
            mcp_port=handle.port,
            extra={
                "run_id": config.run_id,
                "label": config.label,
                "seed": config.seed,
                "k": config.k,
                "cases": list(config.case_ids),
                "trial_timeout_s": config.timeout_s,
                "version_tuple_hash": pins.version_tuple_hash(),
                "host_addr": preflight.local_host_addr(),
                "network_mode": pins.NETWORK_MODE,
                "network_name": network,
                "sidecar_ip": handle.ip,
                "vllm_access": vllm_access,
                "vllm_base_url": vllm_base_url,
            },
        )
        preflight.write_preflight(config.results_dir / "preflight.json", preflight_result)
        if not preflight_result.ok:
            raise RuntimeError(
                "preflight pin check failed after sidecar start: " + "; ".join(preflight_result.problems)
            )

        cache = ResultCache(config.cache_root)
        grader_hash = pins.source_hash([str(p) for p in grader_source_paths()])
        plans = plan_trials(config.case_ids, list(config.conditions), config.k, config.seed)
        records: list[TrialRecord] = []
        for plan in plans:
            if plan.condition == pins.CONDITION_UPSTREAM and upstream is not None:
                skill_variant = pins.skill_variant_hash(upstream.files)
            elif plan.condition == pins.CONDITION_SKILL and skill_source is not None:
                skill_variant = pins.skill_variant_hash(skill_source.files)
            else:
                skill_variant = pins.skill_variant_hash([])
            record: TrialRecord | None = None
            cache_reason = "n/a"
            if plan.condition in pins.CACHEABLE_CONDITIONS:
                key = CacheKey.make(plan.case_id, plan.condition, grader_hash, skill_variant)
                lookup_reason = cache.get_reason(key)
                if lookup_reason == "hit":
                    hit = cache.get(key)
                    assert hit is not None
                    for cached_trial in hit.get("trials", []):
                        if cached_trial.get("plan", {}).get("k_index") == plan.k_index:
                            raw = dict(cached_trial)
                            raw["cached"] = True
                            raw["cache_reason"] = "hit"
                            record = _record_from_json(raw)
                            _copy_cached_event(config.results_dir, raw)
                            break
                    else:
                        cache_reason = "miss:trial-absent"
                else:
                    cache_reason = lookup_reason
            if record is None:
                # vllm_base_url/mcp_url were built right after the sidecar
                # start (above the loop); the sidecar handle itself is not
                # needed here -- the trial gets the two endpoint URLs only.
                record = run_trial(
                    plan,
                    run_id=config.run_id,
                    workroot=config.workroot,
                    results_dir=config.results_dir,
                    network=network,
                    vllm_base_url=vllm_base_url,
                    mcp_url=mcp_url,
                    upstream=upstream,
                    timeout_s=config.timeout_s,
                    skill_source=skill_source,
                    cache_reason=cache_reason,
                )
                if plan.condition in pins.CACHEABLE_CONDITIONS:
                    key = CacheKey.make(plan.case_id, plan.condition, grader_hash, skill_variant)
                    existing = cache.get(key)
                    trials = [
                        t
                        for t in (existing or {}).get("trials", [])
                        if t.get("plan", {}).get("k_index") != plan.k_index
                    ]
                    trials.append(record.to_json())
                    trials.sort(key=lambda t: t["plan"]["k_index"])
                    cache.put(key, trials)
            _write_trial_record(config.results_dir, record)
            records.append(record)

        run_record = {
            "run_id": config.run_id,
            "label": config.label,
            "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "seed": config.seed,
            "k": config.k,
            "cases": list(config.case_ids),
            "conditions": list(config.conditions),
            "trial_timeout_s": config.timeout_s,
            "version_tuple": pins.version_tuple(),
            "version_tuple_hash": pins.version_tuple_hash(),
            # the skill condition's variant content hash (None when the run
            # has no skill condition) -- Phases 110-150 record each measured
            # variant by this hash
            "skill_variant_hash": pins.skill_variant_hash(skill_source.files) if skill_source is not None else None,
            "order": [
                {"case": p.case_id, "condition": p.condition, "k": p.k_index, "cached": r.cached}
                for p, r in zip(plans, records)
            ],
            "trials": [r.to_json() for r in records],
        }
        (config.results_dir / "run.json").write_text(
            json.dumps(run_record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    finally:
        # Teardown order (all best-effort, never raising): the forwarder
        # first (it holds the gateway bind), then the sidecar, then the
        # network (which removes the gateway interface the forwarder was
        # bound to). A leftover of any step is the next run's sweep.
        if forwarder_handle is not None:
            forwarder.stop(forwarder_handle)
        if handle is not None:
            sidecar.stop_sidecar(container_id=handle.container_id)
        remove_run_network(network)
    return run_record


def _copy_cached_event(results_dir: Path, cached_trial: dict) -> None:
    """Copy a cached trial's event stream into the current results dir.

    The cached record's `event_file` is relative to the ORIGINAL run's
    results dir (`<harness root>/results/<original run id>`); without the
    copy a rerun's report dir would lack the streams of its cached trials.
    """
    event_file = cached_trial.get("event_file")
    original_run_id = cached_trial.get("run_id")
    if not event_file or not original_run_id:
        return
    original_dir = pins.HARNESS_ROOT / "results" / str(original_run_id)
    src = original_dir / str(event_file)
    if not src.is_file():
        return
    dst = results_dir / str(event_file)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def _record_from_json(raw: dict) -> TrialRecord:
    """Rebuild a TrialRecord from its JSON form (the cache-hit path).

    The additive fields (`cache_reason`, `event_file_bytes`,
    `event_file_committed`, `skills_installed`) default for pre-existing
    records that predate them (old cache entries and committed run records
    parse unchanged).
    """
    assert isinstance(raw, dict)
    plan_raw = raw.get("plan") or {}
    plan = TrialPlan(
        case_id=str(plan_raw.get("case_id", "")),
        condition=str(plan_raw.get("condition", "")),
        k_index=int(plan_raw.get("k_index", 0)),
    )
    event_file = raw.get("event_file")
    result = TrialRecord(
        plan=plan,
        run_id=str(raw.get("run_id", "")),
        workdir=str(raw.get("workdir", "")),
        started_at=str(raw.get("started_at", "")),
        finished_at=str(raw.get("finished_at", "")),
        wall_time_s=raw.get("wall_time_s"),
        exit_code=raw.get("exit_code"),
        timeout=bool(raw.get("timeout", False)),
        contended=bool(raw.get("contended", False)),
        idle_wait_s=float(raw.get("idle_wait_s", 0.0)),
        cached=bool(raw.get("cached", True)),
        event_file=event_file,
        gates=list(raw.get("gates", [])),
        passed=bool(raw.get("passed", False)),
        metrics=dict(raw.get("metrics", {})),
        cache_reason=str(raw.get("cache_reason", "n/a")),
        event_file_bytes=raw.get("event_file_bytes"),
        event_file_committed=bool(raw.get("event_file_committed", event_file is not None)),
        skills_installed=[str(name) for name in (raw.get("skills_installed") or [])],
    )
    return result
