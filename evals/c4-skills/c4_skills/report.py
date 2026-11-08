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

"""The run report (Task 100.150).

Pass rates per condition and per case, the ACC-008/ACC-012 gate margins
(the machinery evaluates them whenever a `skill` condition is present; for
a Phase 100 run with only `none`/`upstream` the comparison is reported as
information), the Wilson intervals and pass^k as information only, the
per-gate failure breakdown, the flags (timeouts, contention) and the cost
estimate against the Measurement budget.

The report is pure: it reads the run record (`run.json` + the per-trial
records) and writes `report.md` + `report.json`.
"""

from __future__ import annotations

import dataclasses
import json
import statistics
from dataclasses import dataclass
from pathlib import Path

from . import pins, stats

#: The full-run shape of the budget (Measurement): 6 cases x 3 conditions x
#: k=5 trials, up to the per-trial timeout each.
BUDGET_FULL_CASES = 6
BUDGET_FULL_CONDITIONS = 3
BUDGET_FULL_K = 5
BUDGET_FULL_HOURS = 30.0


@dataclass
class ReportInput:
    """The run record the report renders.

    Attributes:
        run: The `run.json` payload (versions, seed, order, trials).
        preflight: The `preflight.json` payload (or None when absent).
        phase_cases: The cases this report's phase is measured on (for the
            margin checks; defaults to the run's cases).
        comparison: The comparison condition of the phase (defaults to
            `upstream`).
    """

    run: dict
    preflight: dict | None = None
    phase_cases: list[str] | None = None
    comparison: str = pins.CONDITION_UPSTREAM


def _trials_by_condition(run: dict) -> dict[str, list[dict]]:
    """Split the run's trial records by condition."""
    by: dict[str, list[dict]] = {}
    for trial in run.get("trials", []):
        plan = trial.get("plan") or {}
        condition = str(plan.get("condition", ""))
        by.setdefault(condition, []).append(trial)
    return by


def _outcomes(run: dict, condition: str, cases: list[str] | None) -> dict[str, list[bool]]:
    """Return case -> [passed, ...] for one condition (optional case filter)."""
    by = _trials_by_condition(run)
    result: dict[str, list[bool]] = {}
    for trial in by.get(condition, []):
        plan = trial.get("plan") or {}
        case_id = str(plan.get("case_id", ""))
        if cases is not None and case_id not in cases:
            continue
        result.setdefault(case_id, []).append(bool(trial.get("passed")))
    return result


def _gate_failures(run: dict, condition: str) -> dict[str, int]:
    """Count per-gate failures for one condition (the breakdown)."""
    counts: dict[str, int] = {}
    for trial in _trials_by_condition(run).get(condition, []):
        for gate in trial.get("gates", []):
            if not gate.get("passed"):
                name = str(gate.get("name", "?"))
                counts[name] = counts.get(name, 0) + 1
    return counts


def _flags(run: dict, condition: str) -> dict[str, int]:
    """Count the timeout / contention / cached flags for one condition."""
    timeouts = 0
    contended = 0
    cached = 0
    for trial in _trials_by_condition(run).get(condition, []):
        if trial.get("timeout"):
            timeouts += 1
        if trial.get("contended"):
            contended += 1
        if trial.get("cached"):
            cached += 1
    result = {"timeout": timeouts, "contended": contended, "cached": cached}
    return result


def _wall_times(run: dict) -> list[float]:
    """Return every measured trial wall time (the cost estimate input)."""
    times = [
        float(t["wall_time_s"])
        for t in run.get("trials", [])
        if t.get("wall_time_s") is not None and not t.get("cached")
    ]
    return times


def build_report_input(run: dict, preflight: dict | None, phase_cases: list[str] | None, comparison: str) -> dict:
    """Compute every report figure (pure; the JSON payload).

    Args:
        run: The `run.json` payload.
        preflight: The `preflight.json` payload.
        phase_cases: The phase's case filter (None = every run case).
        comparison: The phase's comparison condition.

    Returns:
        The report.json payload.
    """
    conditions = [c for c in run.get("conditions", []) if _trials_by_condition(run).get(c)]
    case_filter = phase_cases if phase_cases is not None else list(run.get("cases", []))

    per_condition: dict[str, dict] = {}
    for condition in conditions:
        outcomes = _outcomes(run, condition, case_filter)
        all_outcomes = [ok for oks in outcomes.values() for ok in oks]
        passes = sum(1 for ok in all_outcomes if ok)
        trials = len(all_outcomes)
        entry: dict = {
            "passes": passes,
            "trials": trials,
            "pass_rate": (passes / trials) if trials else None,
            "wilson": stats.wilson_interval(passes, trials) if trials else None,
            "pass_power_k": (stats.pass_power_k(passes / trials, trials) if trials else None),
            "per_case": {
                case: {"passes": sum(1 for ok in oks if ok), "trials": len(oks)}
                for case, oks in sorted(outcomes.items())
            },
            "gate_failures": _gate_failures(run, condition),
            "flags": _flags(run, condition),
        }
        per_condition[condition] = entry

    skill_entry = None
    if pins.CONDITION_SKILL in per_condition:
        skill_stats = stats.stats_for_condition(pins.CONDITION_SKILL, _outcomes(run, pins.CONDITION_SKILL, case_filter))
        comparison_stats = (
            stats.stats_for_condition(comparison, _outcomes(run, comparison, case_filter))
            if comparison in per_condition
            else None
        )
        none_stats = (
            stats.stats_for_condition(pins.CONDITION_NONE, _outcomes(run, pins.CONDITION_NONE, case_filter))
            if pins.CONDITION_NONE in per_condition
            else None
        )
        margin = stats.check_margins(skill_stats, comparison_stats, none_stats)
        skill_entry = {
            "margin": dataclasses.asdict(margin),
            "wilson": per_condition[pins.CONDITION_SKILL]["wilson"],
        }

    walls = _wall_times(run)
    cost = None
    if walls:
        median = statistics.median(walls)
        total_trials = BUDGET_FULL_CASES * BUDGET_FULL_CONDITIONS * BUDGET_FULL_K
        full_hours = median * total_trials / 3600.0
        cost = {
            "measured_trials": len(walls),
            "median_wall_time_s": round(median, 1),
            "mean_wall_time_s": round(statistics.fmean(walls), 1),
            "max_wall_time_s": round(max(walls), 1),
            "full_run_trials": total_trials,
            "full_run_hours_at_median": round(full_hours, 1),
            "full_run_hours_at_timeout": round(pins.TRIAL_TIMEOUT_S * total_trials / 3600.0, 1),
            "budget_hours": BUDGET_FULL_HOURS,
            "within_budget_at_median": full_hours <= BUDGET_FULL_HOURS,
        }

    result: dict = {
        "run_id": run.get("run_id"),
        "label": run.get("label"),
        "cases": case_filter,
        "conditions": conditions,
        "k": run.get("k"),
        "seed": run.get("seed"),
        "version_tuple_hash": run.get("version_tuple_hash"),
        "comparison": comparison,
        "per_condition": per_condition,
        "skill_margins": skill_entry,
        "cost_estimate": cost,
        "preflight_ok": (preflight or {}).get("ok"),
        "preflight_problems": (preflight or {}).get("problems", []),
    }
    return result


def _fmt_rate(value: float | None) -> str:
    """Format a pass rate (or None) for the markdown report."""
    if value is None:
        return "n/a"
    result = f"{value:.0%}"
    return result


def _fmt_wilson(wilson: tuple[float, float] | list[float] | None) -> str:
    """Format a Wilson interval (or None) for the markdown report."""
    if not wilson:
        return "n/a"
    lo, hi = wilson[0], wilson[1]
    result = f"[{lo:.0%}, {hi:.0%}]"
    return result


def render_report_md(report: dict) -> str:
    """Render the markdown report from the report figures (pure).

    Args:
        report: The `build_report_input` payload.

    Returns:
        The markdown text.
    """
    lines: list[str] = []
    lines.append(f"# Run report: {report.get('run_id')}")
    lines.append("")
    lines.append(
        f"Label: {report.get('label') or '-'}; cases: {', '.join(report.get('cases', []))}; "
        f"conditions: {', '.join(report.get('conditions', []))}; k={report.get('k')}; seed={report.get('seed')}."
    )
    lines.append(
        f"Version tuple hash: `{report.get('version_tuple_hash')}`; preflight ok: {report.get('preflight_ok')}."
    )
    lines.append("")
    lines.append("## Pass rates")
    lines.append("")
    lines.append("| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |")
    lines.append("|---|---|---|---|---|---|---|")
    for condition, entry in report.get("per_condition", {}).items():
        per_case = "; ".join(
            f"{case}: {c['passes']}/{c['trials']}" for case, c in sorted(entry.get("per_case", {}).items())
        )
        lines.append(
            f"| {condition} | {entry['passes']} | {entry['trials']} | {_fmt_rate(entry.get('pass_rate'))} "
            f"| {_fmt_wilson(entry.get('wilson'))} | {_fmt_ppk(entry)} | {per_case} |"
        )
    lines.append("")
    lines.append("Wilson intervals and pass^k are information only (k is small).")
    lines.append("")
    lines.append("## Gate margins (ACC-008 / ACC-012 machinery)")
    lines.append("")
    skill = report.get("skill_margins")
    if skill is None:
        lines.append(
            f"No `skill` condition in this run (Phase 100 measures `none` vs `{report.get('comparison')}` as the "
            "baseline pair). The margin machinery activates with the first skill phase: the skill's pass rate must "
            f"be not more than {stats.ACC008_MAX_MARGIN_PCT:.0f} percentage points lower than the comparison "
            f"condition, no case may be clearly worse (>= {stats.ACC008_CASE_CLEARLY_WORSE_TRIALS} fewer passes "
            "out of k), and the skill must be not worse than `none`."
        )
        delta = _condition_delta(report)
        if delta is not None:
            lines.append("")
            lines.append(
                f"Information: `{delta['lower']}` vs `{delta['higher']}` differ by "
                f"{delta['pp']:+.0f} percentage points ({delta['detail']})."
            )
    else:
        margin = skill["margin"]
        lines.append(
            f"ok={margin['ok']}; rate margin {margin['rate_margin_pp']} pp "
            f"(limit {stats.ACC008_MAX_MARGIN_PCT:.0f}); "
            f"clearly worse cases: {margin['clearly_worse_cases'] or 'none'}; "
            f"not worse than none: {margin['better_than_none']}; "
            f"none rate {_fmt_rate(margin.get('none_rate'))}; "
            f"skill Wilson {_fmt_wilson(skill.get('wilson'))}."
        )
    lines.append("")
    lines.append("## Per-gate failures")
    lines.append("")
    any_failure = False
    for condition, entry in report.get("per_condition", {}).items():
        failures = entry.get("gate_failures", {})
        if failures:
            any_failure = True
            detail = ", ".join(f"{name} x{count}" for name, count in sorted(failures.items()))
            lines.append(f"- **{condition}**: {detail}")
    if not any_failure:
        lines.append("- no gate failures")
    lines.append("")
    lines.append("## Flags")
    lines.append("")
    for condition, entry in report.get("per_condition", {}).items():
        flags = entry.get("flags", {})
        lines.append(
            f"- **{condition}**: timeout={flags.get('timeout', 0)}, "
            f"contended={flags.get('contended', 0)}, cached={flags.get('cached', 0)}"
        )
    lines.append("")
    lines.append("## Cost estimate (Task 100.170)")
    lines.append("")
    cost = report.get("cost_estimate")
    if cost is None:
        lines.append("No measured (uncached) trials, no estimate.")
    else:
        lines.append(
            f"Measured over {cost['measured_trials']} trial(s): median {cost['median_wall_time_s']} s, "
            f"mean {cost['mean_wall_time_s']} s, max {cost['max_wall_time_s']} s."
        )
        lines.append(
            f"Full run = {cost['full_run_trials']} trials -> "
            f"{cost['full_run_hours_at_median']} h at the median per-trial time "
            f"(budget {cost['budget_hours']} h at the {pins.TRIAL_TIMEOUT_S} s timeout: "
            f"{cost['full_run_hours_at_timeout']} h worst case). "
            f"Within budget at median: {cost['within_budget_at_median']}."
        )
        lines.append("")
        lines.append(
            "Per-phase expectation: each skill phase is measured on its own cases against "
            "`none` and its comparison condition, with the `none`/`upstream` baselines cached, "
            "so a phase costs only its `skill` trials plus any uncached baselines. See the run "
            "label and the case list above; cached `none`/`upstream` trials cost zero model time."
        )
    lines.append("")
    result = "\n".join(lines) + "\n"
    return result


def _fmt_ppk(entry: dict) -> str:
    """Format the pass^k information figure."""
    value = entry.get("pass_power_k")
    if value is None:
        return "n/a"
    result = f"{value:.3f}"
    return result


def _condition_delta(report: dict) -> dict | None:
    """Return the rate delta between the two conditions of a Phase 100 run."""
    per = report.get("per_condition", {})
    if pins.CONDITION_NONE in per and report.get("comparison") in per:
        none_rate = per[pins.CONDITION_NONE].get("pass_rate")
        comp_rate = per[report["comparison"]].get("pass_rate")
        if none_rate is not None and comp_rate is not None:
            higher = pins.CONDITION_NONE if none_rate >= comp_rate else report["comparison"]
            lower = report["comparison"] if higher == pins.CONDITION_NONE else pins.CONDITION_NONE
            higher_rate = none_rate if higher == pins.CONDITION_NONE else comp_rate
            lower_rate = comp_rate if higher == pins.CONDITION_NONE else none_rate
            detail = f"{higher} {higher_rate:.0%} vs {lower} {lower_rate:.0%}"
            result = {
                "higher": higher,
                "lower": lower,
                "pp": abs(none_rate - comp_rate) * 100.0,
                "detail": detail,
            }
            return result
    return None


def write_report(results_dir: Path, report: dict) -> tuple[Path, Path]:
    """Write `report.json` + `report.md` into the run's results dir.

    Args:
        results_dir: The run results dir.
        report: The `build_report_input` payload.

    Returns:
        The (json_path, md_path) pair.
    """
    assert isinstance(results_dir, Path)
    results_dir.mkdir(parents=True, exist_ok=True)
    json_path = results_dir / "report.json"
    md_path = results_dir / "report.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_report_md(report), encoding="utf-8")
    result: tuple[Path, Path] = (json_path, md_path)
    return result


def build_and_write(
    results_dir: Path, phase_cases: list[str] | None = None, comparison: str = pins.CONDITION_UPSTREAM
) -> dict:
    """Read `run.json`/`preflight.json`, build the report, write it.

    Args:
        results_dir: The run results dir.
        phase_cases: The phase's case filter (None = every run case).
        comparison: The phase's comparison condition.

    Returns:
        The report payload.
    """
    assert isinstance(results_dir, Path)
    run_path = results_dir / "run.json"
    assert run_path.is_file(), f"no run.json in {results_dir}"
    run = json.loads(run_path.read_text(encoding="utf-8"))
    preflight_path = results_dir / "preflight.json"
    preflight = json.loads(preflight_path.read_text(encoding="utf-8")) if preflight_path.is_file() else None
    report = build_report_input(run, preflight, phase_cases, comparison)
    write_report(results_dir, report)
    return report
