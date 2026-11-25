# Run report: p140-prove-2026-11-10T133052Z

Label: p140-prove; cases: design-views, no-trigger, heldout-views; conditions: none; k=5; seed=41733.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 1 | 15 | 7% | [1%, 30%] | 0.000 | design-views: 0/5; heldout-views: 0/5; no-trigger: 1/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

No `skill` condition in this run (Phase 100 measures `none` vs `none` as the baseline pair). The margin machinery activates with the first skill phase: the skill's pass rate must be not more than 10 percentage points lower than the comparison condition, no case may be clearly worse (>= 2 fewer passes out of k), and the skill must be not worse than `none`.

Information: `none` vs `none` differ by +0 percentage points (none 7% vs none 7%).

## Per-gate failures

- **none**: cli_export x7, cli_valid x7, dsl_written x6, elements_described x7, explicit_view_keys x7, external_system_tagged x10, has_person x7, has_system x7, has_view x7, mcp_limit_stated x4, relationship_technology x9, validate_ok_called x8, views_within_element_bound x3

## Flags

- **none**: timeout=11, contended=5, cached=0

## Cost estimate (Task 100.170)

Measured over 15 trial(s): median 1201.1 s, mean 1008.0 s, max 1201.4 s.
Full run = 90 trials -> 30.0 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: False.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

