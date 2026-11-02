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

"""The trial runner (Task 100.130).

Sequential trials (one at a time, `-j 1` semantics): the planned (case,
condition, k) combinations are shuffled once with a recorded seed, and each
trial runs in its own fresh work dir and its own OpenCode container
(``--network host``, no host OpenCode config mounted, no `AGENTS.md`, no
skills except the condition's, web access denied by the injected config).

The shared-server rules (Measurement): the runner refuses to start while
vLLM reports running requests, re-checks (and waits) between trials, and
flags -- never fails -- a trial that ran while another client was active.
A per-trial timeout is a failure, flagged separately.

The result cache (Task 100.130) reuses the `none`/`upstream` trial
summaries when (case, condition, version tuple, grader hash, skill variant
hash) all match, so skill iterations cost only the `skill` trials.
"""

from __future__ import annotations

import json
import random
import shutil
import subprocess
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import graders, metrics as metrics_mod, pins, preflight, sidecar
from .cache import CacheKey, ResultCache
from .cases import Case, get_case
from .events import ParsedTrial, parse_events_file
from .occonfig import OPENCODE_CONFIG_CONTENT_ENV, opencode_config_content
from .upstream import UpstreamSource, mount_skills_into

#: The in-container work dir (the trial's CWD).
CONTAINER_WORKDIR = "/work"

#: The event stream is committed with the trial record only up to this size
#: (larger streams are summarized, the file kept in the work dir).
EVENT_FILE_COMMIT_LIMIT = 2_000_000

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
        event_file: The committed event stream file (relative to the run
            results dir), or None.
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
#: container, and opencode 2.x's managed service would keep its host-network
#: port bound for the next trial).
TRIAL_CONTAINER_PREFIX = "c4eval-trial-"

#: The poll interval while waiting for a trial container to exit.
CONTAINER_POLL_S = 2.0


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


def _run_opencode_container(
    workdir: Path,
    case: Case,
    mcp_port: int,
    timeout_s: int,
    log_path: Path,
    container_name: str,
) -> tuple[int | None, bool, float]:
    """Run one trial container (detached) and capture its event output.

    The container is addressed by name throughout: on timeout the harness
    sends `docker kill` to the CONTAINER (never just to the client), so a
    timed-out trial cannot orphan a process that keeps a host-network port
    or a vLLM sequence slot.

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
        "host",
        *preflight.host_user_flags(),
        "-e",
        "HOME=/tmp/oc-home",
        "-w",
        CONTAINER_WORKDIR,
        "-v",
        f"{workdir}:{CONTAINER_WORKDIR}",
        "-e",
        f"{OPENCODE_CONFIG_CONTENT_ENV}={opencode_config_content(mcp_port)}",
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
    log_file = open(log_path, "w", encoding="utf-8")
    log_tail = subprocess.Popen(  # noqa: S603 -- fixed container name
        ["docker", "logs", "-f", "--tail", "0", container_name],
        stdout=log_file,
        stderr=subprocess.DEVNULL,
    )
    try:
        timed_out = False
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
    finally:
        log_tail.terminate()
        try:
            log_tail.wait(timeout=10)
        except subprocess.TimeoutExpired:
            log_tail.kill()
        log_file.close()
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


def _install_skills(workdir: Path, condition: str, upstream: UpstreamSource | None) -> list[str]:
    """Install the condition's skills into the work dir (returns the names).

    `none`: nothing. `upstream`: the fetched, unmodified upstream skills.
    `skill`: the adapted skills from the variant dir (Phases 110-150 pass a
    directory; Phase 100 never reaches this branch with content).
    """
    assert condition in pins.CONDITIONS
    if condition == pins.CONDITION_NONE:
        return []
    if condition == pins.CONDITION_UPSTREAM:
        if upstream is None:
            raise RuntimeError("the upstream condition needs a verified upstream source")
        return mount_skills_into(workdir, upstream)
    # skill: a variant directory is supplied through the work dir itself
    # (Phases 110-150 copy their files into <workdir>/.opencode/skills/
    # before the runner is invoked); nothing to do here.
    skill_root = workdir / ".opencode" / "skills"
    if skill_root.is_dir():
        return sorted(p.name for p in skill_root.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())
    return []


def _skill_variant_files(workdir: Path) -> list[tuple[str, bytes]]:
    """Collect the work dir's skill files (for the variant content hash)."""
    skill_root = workdir / ".opencode" / "skills"
    if not skill_root.is_dir():
        return []
    files: list[tuple[str, bytes]] = []
    for path in sorted(skill_root.glob("**/*")):
        if path.is_file():
            files.append((path.relative_to(skill_root).as_posix(), path.read_bytes()))
    return files


def run_trial(
    plan: TrialPlan,
    *,
    run_id: str,
    workroot: Path,
    results_dir: Path,
    mcp_port: int,
    upstream: UpstreamSource | None,
    timeout_s: int = pins.TRIAL_TIMEOUT_S,
) -> TrialRecord:
    """Run one trial end to end (container + graders + metrics + record).

    Args:
        plan: The TrialPlan.
        run_id: The run identifier (work dir + record naming).
        workroot: The gitignored trial work dir root.
        results_dir: The committed results dir for this run.
        mcp_port: The harness sidecar's host port.
        upstream: The verified upstream source (the `upstream` condition).
        timeout_s: The per-trial wall-clock timeout.

    Returns:
        The TrialRecord.
    """
    case = get_case(plan.case_id)
    workdir = workroot / _trial_workdir_name(plan, run_id)
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)
    _write_setup_files(workdir, case)
    _install_skills(workdir, plan.condition, upstream)

    trial_dir = results_dir / "trials" / plan.case_id
    trial_dir.mkdir(parents=True, exist_ok=True)
    record_name = f"{plan.condition}-k{plan.k_index}"
    event_path = trial_dir / f"{record_name}.events.ndjson"

    idle, last_seen, idle_wait = preflight.wait_until_idle(budget_s=3600.0, poll_s=pins.IDLE_POLL_INTERVAL_S)
    if not idle:
        raise RuntimeError(
            f"vLLM was still busy after {idle_wait:.0f}s of waiting (last seen {last_seen} running request(s)); "
            "refusing to start a trial that is guaranteed to be contended"
        )
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    samples, sampler_thread, stop_event = _start_contended_sampler()
    container_name = f"{TRIAL_CONTAINER_PREFIX}{run_id}.{plan.case_id}.{plan.condition}-k{plan.k_index}"
    exit_code, timed_out, wall = _run_opencode_container(workdir, case, mcp_port, timeout_s, event_path, container_name)
    stop_event.set()
    sampler_thread.join(timeout=5.0)
    contended = _was_contended(samples)
    finished_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    inputs = graders.collect_inputs(workdir)
    if event_path.is_file():
        parsed = parse_events_file(event_path)
    else:
        parsed = ParsedTrial()
    triage_metrics = metrics_mod.compute_metrics(
        parsed,
        inputs,
        timeout=timed_out,
        contended=contended,
    )
    gate_results = graders.grade_case(case, inputs)
    passed = graders.case_passed(gate_results) and not timed_out

    commit_event: str | None = None
    if event_path.is_file() and event_path.stat().st_size <= EVENT_FILE_COMMIT_LIMIT:
        commit_event = str(event_path.relative_to(results_dir))
    else:
        event_path.unlink(missing_ok=True)

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
        event_file=commit_event,
        gates=[asdict(g) for g in gate_results],
        passed=passed,
        metrics=triage_metrics.to_json(),
    )
    return record


def sweep_trial_containers() -> list[str]:
    """Kill and remove every leftover `c4eval-trial-*` container.

    Safety sweep (a previous crashed run may have left a trial container
    behind on the host network, still holding a port and a vLLM sequence
    slot). Returns the removed container ids.
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
    """
    import c4_skills  # the harness package root (tests/evals put it on sys.path)

    root = Path(c4_skills.__file__).parent
    result = [
        root / "graders.py",
        root / "metrics.py",
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


def _write_trial_record(results_dir: Path, record: TrialRecord) -> Path:
    """Write one trial record next to its event stream (committed)."""
    trial_dir = results_dir / "trials" / record.plan.case_id
    trial_dir.mkdir(parents=True, exist_ok=True)
    path = trial_dir / f"{record.plan.condition}-k{record.plan.k_index}.json"
    path.write_text(json.dumps(record.to_json(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def run(config: RunConfig) -> dict:
    """Run one full harness measurement (the Task 100.130 runner).

    Sequence: refuse a stale sidecar, preflight (pins + idle), start the
    pinned sidecar, verify upstream when needed, plan the shuffled trial
    order (seed recorded), run every trial sequentially (cached
    `none`/`upstream` trials are reused, not reordered), write the per-
    trial records + `run.json`, tear the sidecar down, and build the
    report.

    Args:
        config: The RunConfig.

    Returns:
        The run record (the `run.json` payload).

    Raises:
        RuntimeError: When the preflight pin check fails or the sidecar
            does not come up.
    """
    assert config.case_ids and config.conditions
    stale = sidecar.sidecar_container_list()
    if stale:
        raise RuntimeError(f"stale c4eval-mcp sidecar(s) still running: {stale}; tear them down first")
    swept = sweep_trial_containers()
    if swept:
        print(f"swept {len(swept)} leftover trial container(s): {swept}")

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
        },
    )
    if not preflight_result.ok:
        preflight.write_preflight(config.results_dir / "preflight.json", preflight_result)
        raise RuntimeError("preflight pin check failed: " + "; ".join(preflight_result.problems))

    handle = sidecar.start_sidecar(config.run_id)
    try:
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
            skill_variant = pins.skill_variant_hash(
                upstream.files if (plan.condition == pins.CONDITION_UPSTREAM and upstream is not None) else []
            )
            record: TrialRecord | None = None
            if plan.condition in pins.CACHEABLE_CONDITIONS:
                key = CacheKey.make(plan.case_id, plan.condition, grader_hash, skill_variant)
                hit = cache.get(key)
                if hit is not None:
                    for cached_trial in hit.get("trials", []):
                        if cached_trial.get("plan", {}).get("k_index") == plan.k_index:
                            raw = dict(cached_trial)
                            raw["cached"] = True
                            record = _record_from_json(raw)
                            _copy_cached_event(config.results_dir, raw)
                            break
            if record is None:
                record = run_trial(
                    plan,
                    run_id=config.run_id,
                    workroot=config.workroot,
                    results_dir=config.results_dir,
                    mcp_port=handle.port,
                    upstream=upstream,
                    timeout_s=config.timeout_s,
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
        sidecar.stop_sidecar(container_id=handle.container_id)
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
    """Rebuild a TrialRecord from its JSON form (the cache-hit path)."""
    assert isinstance(raw, dict)
    plan_raw = raw.get("plan") or {}
    plan = TrialPlan(
        case_id=str(plan_raw.get("case_id", "")),
        condition=str(plan_raw.get("condition", "")),
        k_index=int(plan_raw.get("k_index", 0)),
    )
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
        event_file=raw.get("event_file"),
        gates=list(raw.get("gates", [])),
        passed=bool(raw.get("passed", False)),
        metrics=dict(raw.get("metrics", {})),
    )
    return result
