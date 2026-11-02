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

"""The measurement statistics: Wilson intervals, pass^k and the gate margins.

The gate (Measurement/Stop Rule) works on point estimates with fixed
margins; the Wilson interval and pass^k are reported for information only,
because k=5 gives very wide intervals.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

#: The default Wilson z (95% confidence).
WILSON_Z_DEFAULT = 1.959964

#: The ACC-008 margin: the skill's pass rate may be at most this much lower
#: than the comparison condition's (percentage points).
ACC008_MAX_MARGIN_PCT = 10.0

#: The ACC-008 per-case rule: a case is clearly worse when the comparison
#: condition passed at least this many more trials out of k.
ACC008_CASE_CLEARLY_WORSE_TRIALS = 2


def wilson_interval(successes: int, trials: int, z: float = WILSON_Z_DEFAULT) -> tuple[float, float]:
    """Return the Wilson score interval for a binomial proportion.

    Args:
        successes: The number of passing trials.
        trials: The number of trials (must be > 0).
        z: The z value (default 95%).

    Returns:
        The (lower, upper) bounds, each clamped to [0, 1].

    Raises:
        ValueError: On a non-positive trial count or an out-of-range
            success count.
    """
    assert isinstance(successes, int) and isinstance(trials, int)
    if trials <= 0:
        raise ValueError(f"trials must be > 0, got {trials}")
    if not 0 <= successes <= trials:
        raise ValueError(f"successes {successes} out of range for {trials} trials")
    p = successes / trials
    z2 = z * z
    denominator = 1.0 + z2 / trials
    centre = (p + z2 / (2.0 * trials)) / denominator
    half = (z / denominator) * math.sqrt(p * (1.0 - p) / trials + z2 / (4.0 * trials * trials))
    lower = max(0.0, centre - half)
    upper = min(1.0, centre + half)
    result: tuple[float, float] = (lower, upper)
    return result


def pass_power_k(pass_rate: float, k: int) -> float:
    """Return pass^k (the information-only reliability figure).

    Args:
        pass_rate: The observed pass rate (0..1).
        k: The exponent (the trials per case).

    Returns:
        `pass_rate ** k`.

    Raises:
        ValueError: On an out-of-range rate or non-positive k.
    """
    assert 0.0 <= pass_rate <= 1.0, pass_rate
    if k <= 0:
        raise ValueError(f"k must be > 0, got {k}")
    result = pass_rate**k
    return result


@dataclass(frozen=True)
class ConditionStats:
    """The pass-rate statistics of one condition over a case set.

    Attributes:
        condition: The condition name.
        passes: Passing trials over the evaluated cases.
        trials: All evaluated trials.
        per_case: case id -> (passes, trials) over that case.
    """

    condition: str
    passes: int
    trials: int
    per_case: dict[str, tuple[int, int]]

    @property
    def pass_rate(self) -> float:
        """Return the point-estimate pass rate (0.0 when no trials)."""
        if self.trials <= 0:
            return 0.0
        result = self.passes / self.trials
        return result

    def wilson(self) -> tuple[float, float] | None:
        """Return the Wilson interval, or None without trials."""
        if self.trials <= 0:
            return None
        result = wilson_interval(self.passes, self.trials)
        return result


def stats_for_condition(condition: str, case_outcomes: dict[str, list[bool]]) -> ConditionStats:
    """Aggregate one condition's per-case trial outcomes.

    Args:
        condition: The condition name.
        case_outcomes: case id -> one boolean per trial (passed or not).

    Returns:
        The ConditionStats.
    """
    assert isinstance(condition, str) and condition
    passes = 0
    trials = 0
    per_case: dict[str, tuple[int, int]] = {}
    for case_id, outcomes in case_outcomes.items():
        case_passes = sum(1 for ok in outcomes if ok)
        per_case[case_id] = (case_passes, len(outcomes))
        passes += case_passes
        trials += len(outcomes)
    result = ConditionStats(condition=condition, passes=passes, trials=trials, per_case=per_case)
    return result


@dataclass(frozen=True)
class MarginCheck:
    """The ACC-008/ACC-012 margin verdict for one skill phase.

    Attributes:
        ok: Whether the stop-rule margins hold.
        rate_margin_pp: The pass-rate difference in percentage points
            (comparison - skill; positive = the skill is lower).
        within_rate_margin: The rate difference is at most the ACC-008
            margin.
        clearly_worse_cases: The cases where the comparison passed at least
            `ACC008_CASE_CLEARLY_WORSE_TRIALS` more trials (per-case rule).
        better_than_none: The ACC-012 verdict (skill rate >= none rate).
        none_rate: The `none` condition's pass rate (information).
    """

    ok: bool
    rate_margin_pp: float
    within_rate_margin: bool
    clearly_worse_cases: list[str]
    better_than_none: bool | None
    none_rate: float


def check_margins(
    skill: ConditionStats,
    comparison: ConditionStats | None,
    none: ConditionStats | None,
) -> MarginCheck:
    """Evaluate the stop-rule margins of one skill phase (ACC-008/ACC-012).

    Args:
        skill: The skill condition's stats over the phase's cases.
        comparison: The phase's comparison condition's stats (None when the
            phase compares against `none` only).
        none: The `none` condition's stats (ACC-012).

    Returns:
        The MarginCheck verdict.
    """
    assert isinstance(skill, ConditionStats)
    reference = comparison if comparison is not None and comparison.trials > 0 else none
    if reference is None or reference.trials <= 0:
        no_reference = MarginCheck(
            ok=False,
            rate_margin_pp=float("inf"),
            within_rate_margin=False,
            clearly_worse_cases=[],
            better_than_none=None,
            none_rate=none.pass_rate if none else 0.0,
        )
        return no_reference

    rate_margin_pp = (reference.pass_rate - skill.pass_rate) * 100.0
    within = rate_margin_pp <= ACC008_MAX_MARGIN_PCT

    clearly_worse: list[str] = []
    for case_id, (skill_passes, skill_trials) in skill.per_case.items():
        ref_case = reference.per_case.get(case_id)
        if ref_case is None:
            continue
        ref_passes = ref_case[0]
        if skill_trials == ref_case[1] and (ref_passes - skill_passes) >= ACC008_CASE_CLEARLY_WORSE_TRIALS:
            clearly_worse.append(case_id)

    better_than_none: bool | None = None
    if none is not None and none.trials > 0:
        better_than_none = skill.pass_rate >= none.pass_rate

    ok = within and not clearly_worse and better_than_none is not False
    result = MarginCheck(
        ok=ok,
        rate_margin_pp=round(rate_margin_pp, 2),
        within_rate_margin=within,
        clearly_worse_cases=sorted(clearly_worse),
        better_than_none=better_than_none,
        none_rate=none.pass_rate if none else 0.0,
    )
    return result
