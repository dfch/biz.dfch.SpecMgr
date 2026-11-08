# Run report: p110-prove2-2026-11-04T200612Z

Label: p110-prove2; cases: create-system, mcp-limits, no-trigger, heldout-validate; conditions: none; k=5; seed=448993.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 0 | 20 | 0% | [0%, 16%] | 0.000 | create-system: 0/5; heldout-validate: 0/5; mcp-limits: 0/5; no-trigger: 0/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

No `skill` condition in this run (Phase 100 measures `none` vs `none` as the baseline pair). The margin machinery activates with the first skill phase: the skill's pass rate must be not more than 10 percentage points lower than the comparison condition, no case may be clearly worse (>= 2 fewer passes out of k), and the skill must be not worse than `none`.

Information: `none` vs `none` differ by +0 percentage points (none 0% vs none 0%).

## Per-gate failures

- **none**: cli_export x4, cli_valid x5, has_person x4, has_system x4, has_view x5, inspect_called x10, limits_acknowledged x3, mcp_limit_stated x5, parse_called x10, relationship_technology x5, triage_complete x13, two_containers x4, validate_ok_called x5, validated_before_return x15

## Flags

- **none**: timeout=3, contended=0, cached=6

## Cost estimate (Task 100.170)

Measured over 14 trial(s): median 272.1 s, mean 357.8 s, max 1201.8 s.
Full run = 90 trials -> 6.8 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

