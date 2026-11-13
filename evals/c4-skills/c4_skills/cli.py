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

"""The harness command line (the run entry point of Task 100.100).

Subcommands:

- ``preflight`` -- record the environment (versions, pins, idle state) to
  a JSON file, exit 0 ok / 1 pin violation.
- ``probe`` -- one trivial trial against the real vLLM + sidecar (verifies
  the full chain: config, provider, MCP, event stream) without a case.
- ``run`` -- the full measurement run (Task 100.130).
- ``report`` -- rebuild the report from an existing results dir.

Exit codes (the documented contract, enforced by ``main``):

- ``0`` -- ok.
- ``1`` -- a runtime-shaped failure: a pin/preflight violation, the
  sidecar or a trial container failing, a missing/failed docker or git
  call (``RuntimeError`` -- including a hung Structurizr CLI run of the
  graders, whose ``subprocess.TimeoutExpired`` is mapped to
  ``RuntimeError`` by ``graders._run_cli``, Task 125.130/I3), or an I/O
  failure (``OSError``).
- ``2`` -- a usage-shaped failure: an unknown case or gate
  (``KeyError``), an invalid caller argument such as ``k <= 0`` or a
  missing/misplaced ``--skills-dir`` (``ValueError``), or a caller
  precondition on an artifact the command needs -- e.g. ``report``
  against a results dir without ``run.json`` (``AssertionError``).

Any other exception type is a harness bug and propagates as a raw
traceback on purpose (it must not be papered over by an exit code).
The ``probe`` subcommand additionally returns 2 for a failed probe
outcome (a probe that did not verify the chain is not a pin failure).

The harness is standard-library only; Docker and git are the only external
tools (both host prerequisites recorded in the preflight).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from . import forwarder, pins, preflight, report, runner, sidecar
from .cases import Case, get_case
from .events import parse_events_file
from .upstream import ensure_upstream

#: The default work root / cache root (both gitignored).
DEFAULT_WORKROOT = pins.HARNESS_ROOT / "work"
DEFAULT_CACHE_ROOT = pins.HARNESS_ROOT / "cache"

#: The probe case: a trivial prompt that verifies the chain without any C4
#: work (its gates are the empty set -- the probe is never graded).
PROBE_PROMPT = "Reply with exactly the following single line and nothing else: PROBE-OK"


def _run_id(label: str) -> str:
    """Return a fresh run id (label + UTC stamp)."""
    stamp = time.strftime(runner.RUN_ID_FORMAT, time.gmtime())
    result = f"{label}-{stamp}" if label else stamp
    return result


def cmd_preflight(args: argparse.Namespace) -> int:
    """Run the preflight and write the JSON (the `preflight` subcommand)."""
    out = Path(args.out)
    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    upstream_source = None
    if pins.CONDITION_UPSTREAM in conditions:
        upstream_source = ensure_upstream(DEFAULT_CACHE_ROOT / "upstream")
    result = preflight.run_preflight(
        conditions=conditions,
        upstream_source=upstream_source,
        extra={"cli": "preflight"},
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result.to_json(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"preflight ok={result.ok} -> {out}")
    for problem in result.problems:
        print(f"  PROBLEM: {problem}")
    return 0 if result.ok else 1


def cmd_probe(args: argparse.Namespace) -> int:
    """Run one trivial trial through the full chain (the `probe` subcommand).

    The probe exists to verify the injected config, the vLLM provider, the
    MCP sidecar and the event-stream shape before a real run; it is a
    single, short model call and never counts toward any measurement.

    It exercises the SAME topology a real run uses (Phase 110): its own
    per-run private `--internal` network, the sidecar on it, and the vLLM
    forwarder on the network's gateway IP -- so a green probe is proof
    the egress-controlled chain works end to end.
    """
    run_id = args.run_id or _run_id("probe")
    results_dir = Path(args.results_dir) if args.results_dir else pins.HARNESS_ROOT / "results" / f"probe-{run_id}"
    workroot = Path(args.workroot) if args.workroot else DEFAULT_WORKROOT
    network = runner.network_name_for(run_id)
    stale = sidecar.sidecar_container_list()
    if stale:
        print(f"stale c4eval-mcp sidecar(s) still running: {stale}; tear them down first")
        return 1
    swept = runner.sweep_trial_containers()
    if swept:
        print(f"swept {len(swept)} leftover trial container(s): {swept}")
    swept_networks = runner.sweep_run_networks()
    if swept_networks:
        print(f"swept {len(swept_networks)} leftover run network(s): {swept_networks}")
    handle: sidecar.SidecarHandle | None = None
    forwarder_handle: forwarder.ForwarderHandle | None = None
    try:
        runner.create_run_network(network)
        handle = sidecar.start_sidecar(run_id, network)
        gateway_ip = runner.network_gateway_ip(network)
        # option C (conditional): forwarder preferred, strictly-verified
        # direct bind fallback (the trial's vLLM URL is mode-invariant).
        forwarder_handle, vllm_access = runner.establish_vllm_access(gateway_ip)
        vllm_base_url = f"http://{gateway_ip}:{pins.vllm_host_port()}/v1"
        mcp_url = f"http://{handle.ip}:{handle.port}/mcp"
        workdir = workroot / f"probe.{run_id}"
        if workdir.exists():
            workdir = workdir / str(int(time.time()))
        workdir.mkdir(parents=True)
        pre = preflight.run_preflight(
            conditions=[pins.CONDITION_NONE],
            mcp_port=handle.port,
            extra={
                "run_id": run_id,
                "label": "probe",
                "network_mode": pins.NETWORK_MODE,
                "network_name": network,
                "sidecar_ip": handle.ip,
                "vllm_access": vllm_access,
                "vllm_base_url": vllm_base_url,
            },
        )
        preflight.write_preflight(results_dir / "preflight.json", pre)
        if not pre.ok:
            print("preflight pin check failed:")
            for problem in pre.problems:
                print(f"  PROBLEM: {problem}")
            return 1
        probe = Case(id="__probe__", prompt=PROBE_PROMPT, gates=(), setup_files={})
        event_path = results_dir / "probe.events.ndjson"
        exit_code, timed_out, wall = runner._run_opencode_container(
            workdir,
            probe,
            network=network,
            vllm_base_url=vllm_base_url,
            mcp_url=mcp_url,
            timeout_s=args.timeout,
            log_path=event_path,
            container_name=f"{runner.TRIAL_CONTAINER_PREFIX}{run_id}.probe",
        )
        parsed = parse_events_file(event_path) if event_path.is_file() else runner.ParsedTrial()
        summary = {
            "run_id": run_id,
            "exit_code": exit_code,
            "timed_out": timed_out,
            "wall_time_s": wall,
            "steps": parsed.steps,
            "tool_calls": len(parsed.completed_tool_calls()),
            "finish_seen": parsed.finish_seen,
            "errors": len(parsed.errors),
            "unknown_types": dict(parsed.unknown_types),
            "tokens": parsed.tokens,
            "final_text": parsed.final_text(),
        }
        (results_dir / "probe.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0 if (exit_code == 0 and not timed_out) else 2
    finally:
        # Same teardown order as runner.run: forwarder, sidecar, network.
        if forwarder_handle is not None:
            forwarder.stop(forwarder_handle)
        if handle is not None:
            sidecar.stop_sidecar(container_id=handle.container_id)
        runner.remove_run_network(network)


def cmd_run(args: argparse.Namespace) -> int:
    """Run the full measurement (the `run` subcommand)."""
    cases = [c.strip() for c in args.cases.split(",") if c.strip()]
    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    if not cases:
        raise ValueError("at least one case is required")
    if not conditions:
        raise ValueError("at least one condition is required")
    if args.k <= 0:
        raise ValueError(f"k must be > 0, got {args.k}")
    if pins.CONDITION_SKILL in conditions:
        if args.skills_dir is None:
            raise ValueError("the skill condition needs --skills-dir <path>")
    elif args.skills_dir is not None:
        raise ValueError("--skills-dir is only valid with the skill condition")
    for case_id in cases:
        get_case(case_id)  # unknown case -> KeyError -> usage error
    for condition in conditions:
        if condition not in pins.CONDITIONS:
            print(f"unknown condition: {condition!r}")
            return 2
    run_id = args.run_id or _run_id(args.label)
    config = runner.RunConfig(
        run_id=run_id,
        case_ids=cases,
        conditions=conditions,
        k=args.k,
        seed=args.seed,
        workroot=Path(args.workroot) if args.workroot else DEFAULT_WORKROOT,
        results_dir=Path(args.results_dir) if args.results_dir else pins.HARNESS_ROOT / "results" / run_id,
        cache_root=Path(args.cache) if args.cache else DEFAULT_CACHE_ROOT,
        timeout_s=args.timeout,
        label=args.label,
        skills_dir=Path(args.skills_dir) if args.skills_dir else None,
    )
    config.results_dir.mkdir(parents=True, exist_ok=True)
    print(f"run {run_id}: cases={cases} conditions={conditions} k={config.k} seed={config.seed}")
    runner.run(config)
    rep = report.build_and_write(config.results_dir, phase_cases=cases, comparison=args.comparison)
    print(f"done: {config.results_dir}")
    for condition, entry in rep.get("per_condition", {}).items():
        rate = entry.get("pass_rate")
        print(
            f"  {condition}: {entry['passes']}/{entry['trials']} passed ({rate:.0%})"
            if rate is not None
            else f"  {condition}: n/a"
        )
    cost = rep.get("cost_estimate")
    if cost:
        print(
            f"  cost: median {cost['median_wall_time_s']} s/trial -> full run {cost['full_run_hours_at_median']} h "
            f"(budget {cost['budget_hours']} h)"
        )
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Rebuild the report from an existing results dir (the `report` subcommand)."""
    results_dir = Path(args.results_dir)
    phase_cases = [c.strip() for c in args.cases.split(",") if c.strip()] if args.cases else None
    rep = report.build_and_write(results_dir, phase_cases=phase_cases, comparison=args.comparison)
    print(f"report written to {results_dir / 'report.md'}")
    print(json.dumps(rep, indent=2, sort_keys=True)[:2000])
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser (the `main` entry point's contract)."""
    parser = argparse.ArgumentParser(prog="c4_skills", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("preflight", help="record the environment and check the pins")
    p.add_argument("--out", default=str(pins.HARNESS_ROOT / "results" / "preflight.json"), help="the JSON output path")
    p.add_argument(
        "--conditions", default="none,upstream", help="comma-separated conditions (drives the upstream check)"
    )
    p.set_defaults(func=cmd_preflight)

    p = sub.add_parser("probe", help="one trivial trial through the full chain (no case, no grading)")
    p.add_argument("--run-id", default=None)
    p.add_argument("--results-dir", default=None)
    p.add_argument("--workroot", default=None)
    p.add_argument("--timeout", type=int, default=600, help="probe timeout in seconds")
    p.set_defaults(func=cmd_probe)

    p = sub.add_parser("run", help="run the full measurement")
    p.add_argument("--cases", required=True, help="comma-separated case ids")
    p.add_argument("--conditions", required=True, help="comma-separated condition names")
    p.add_argument("--k", type=int, default=pins.K_FULL, help="trials per case and condition")
    p.add_argument("--seed", type=int, default=None, help="the order seed (random + recorded when omitted)")
    p.add_argument("--run-id", default=None)
    p.add_argument("--label", default="", help="a short run label (e.g. smoke)")
    p.add_argument("--results-dir", default=None)
    p.add_argument("--workroot", default=None)
    p.add_argument("--cache", default=None)
    p.add_argument(
        "--skills-dir",
        default=None,
        help="the skill condition's variant directory (a skill folder or a root of skill folders)",
    )
    p.add_argument("--timeout", type=int, default=pins.TRIAL_TIMEOUT_S, help="per-trial timeout in seconds")
    p.add_argument(
        "--comparison", default=pins.CONDITION_UPSTREAM, help="the phase's comparison condition for the margins"
    )
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("report", help="rebuild the report from an existing results dir")
    p.add_argument("--results-dir", required=True)
    p.add_argument("--cases", default=None, help="comma-separated phase case filter (default: all run cases)")
    p.add_argument("--comparison", default=pins.CONDITION_UPSTREAM)
    p.set_defaults(func=cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    """The CLI entry point (returns the process exit code).

    The module docstring's exit-code contract is enforced here:
    ``KeyError``/``ValueError``/``AssertionError`` are usage-shaped (exit
    2), ``RuntimeError``/``OSError`` are runtime-shaped (exit 1); any
    other exception type propagates (a harness bug, not a documented
    failure shape).

    Args:
        argv: The argument list (defaults to `sys.argv[1:]`).

    Returns:
        The exit code (0 ok, 1 runtime failure, 2 usage; the probe's
        failed outcome is a 2 by the probe's own convention).
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run" and args.seed is None:
        args.seed = int(time.time()) % 1_000_000
    try:
        result = args.func(args)
    except KeyError as exc:
        print(f"unknown case: {exc}")
        return 2
    except ValueError as exc:
        print(f"usage error: {exc}")
        return 2
    except AssertionError as exc:
        print(f"usage error: precondition failed: {exc}")
        return 2
    except RuntimeError as exc:
        print(f"error: {exc}")
        return 1
    except OSError as exc:
        print(f"error: {exc}")
        return 1
    return result


if __name__ == "__main__":
    sys.exit(main())
