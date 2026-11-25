# Run report: p120-prove-2026-11-07T185741Z

Label: p120-prove; cases: create-system, mcp-limits, fix-dsl, no-trigger, heldout-dsl; conditions: none, upstream; k=5; seed=77027.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 1 | 25 | 4% | [1%, 20%] | 0.000 | create-system: 0/5; fix-dsl: 0/5; heldout-dsl: 0/5; mcp-limits: 0/5; no-trigger: 1/5 |
| upstream | 0 | 25 | 0% | [0%, 13%] | 0.000 | create-system: 0/5; fix-dsl: 0/5; heldout-dsl: 0/5; mcp-limits: 0/5; no-trigger: 0/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

No `skill` condition in this run (Phase 100 measures `none` vs `none` as the baseline pair). The margin machinery activates with the first skill phase: the skill's pass rate must be not more than 10 percentage points lower than the comparison condition, no case may be clearly worse (>= 2 fewer passes out of k), and the skill must be not worse than `none`.

Information: `none` vs `none` differ by +0 percentage points (none 4% vs none 4%).

## Per-gate failures

- **none**: cli_export x5, cli_valid x5, elements_described x10, has_person x5, has_system x5, has_view x5, inspect_called x5, mcp_limit_stated x4, parse_called x5, relationship_technology x15, triage_complete x7, two_containers x5, validate_ok_called x8, validated_before_return x10
- **upstream**: cli_export x2, cli_valid x2, elements_described x8, has_person x2, has_system x2, has_view x2, inspect_called x3, limits_acknowledged x1, mcp_limit_stated x5, no_deletions x5, no_mounted_skill_loaded x5, parse_called x5, relationship_technology x12, triage_complete x5, two_containers x2, validate_ok_called x5, validated_before_return x10

## Flags

- **none**: timeout=1, contended=0, cached=0
- **upstream**: timeout=1, contended=0, cached=0

## Cost estimate (Task 100.170)

Measured over 50 trial(s): median 114.4 s, mean 281.0 s, max 1201.5 s.
Full run = 90 trials -> 2.9 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

