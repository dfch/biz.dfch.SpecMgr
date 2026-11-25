# Run report: p140r-prove-2026-11-15T060904Z

Label: p140r-prove; cases: design-views, heldout-views, no-trigger; conditions: none; k=5; seed=722944.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 0 | 15 | 0% | [0%, 20%] | 0.000 | design-views: 0/5; heldout-views: 0/5; no-trigger: 0/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

No `skill` condition in this run (Phase 100 measures `none` vs `none` as the baseline pair). The margin machinery activates with the first skill phase: the skill's pass rate must be not more than 10 percentage points lower than the comparison condition, no case may be clearly worse (>= 2 fewer passes out of k), and the skill must be not worse than `none`.

Information: `none` vs `none` differ by +0 percentage points (none 0% vs none 0%).

## Per-gate failures

- **none**: cli_export x2, cli_valid x2, dsl_written x1, elements_described x2, explicit_view_keys x3, external_system_tagged x9, has_person x2, has_system x2, has_view x3, mcp_limit_stated x5, relationship_technology x9, validate_ok_called x9, views_within_element_bound x7

## Flags

- **none**: timeout=2, contended=0, cached=0

## Cost estimate (Task 100.170)

Measured over 15 trial(s): median 418.6 s, mean 547.2 s, max 1200.8 s.
Full run = 90 trials -> 10.5 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

