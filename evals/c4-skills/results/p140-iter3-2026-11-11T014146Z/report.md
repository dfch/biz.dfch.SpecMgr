# Run report: p140-iter3-2026-11-11T014146Z

Label: p140-iter3; cases: design-views, no-trigger; conditions: none, skill; k=5; seed=31865.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 1 | 10 | 10% | [2%, 40%] | 0.000 | design-views: 0/5; no-trigger: 1/5 |
| skill | 0 | 10 | 0% | [0%, 28%] | 0.000 | design-views: 0/5; no-trigger: 0/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

ok=False; rate margin 10.0 pp (limit 10); clearly worse cases: none; not worse than none: False; none rate 10%; skill Wilson [0%, 28%].

## Per-gate failures

- **none**: cli_export x4, cli_valid x4, dsl_written x3, elements_described x4, explicit_view_keys x4, external_system_tagged x5, has_person x4, has_system x4, has_view x4, mcp_limit_stated x4, relationship_technology x5, validate_ok_called x3, views_within_element_bound x1
- **skill**: cli_export x5, cli_valid x5, dsl_written x5, elements_described x5, explicit_view_keys x5, external_system_tagged x5, has_person x5, has_system x5, has_view x5, mcp_limit_stated x5, relationship_technology x5, validate_ok_called x5

## Flags

- **none**: timeout=6, contended=3, cached=10
- **skill**: timeout=10, contended=0, cached=0

## Cost estimate (Task 100.170)

Measured over 10 trial(s): median 1201.1 s, mean 1201.1 s, max 1201.2 s.
Full run = 90 trials -> 30.0 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: False.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

