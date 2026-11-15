# Run report: p140r-skill-2026-11-15T083350Z

Label: p140r-skill; cases: design-views, no-trigger; conditions: none, skill; k=5; seed=731630.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 0 | 10 | 0% | [0%, 28%] | 0.000 | design-views: 0/5; no-trigger: 0/5 |
| skill | 0 | 10 | 0% | [0%, 28%] | 0.000 | design-views: 0/5; no-trigger: 0/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

ok=True; rate margin 0.0 pp (limit 10); clearly worse cases: none; not worse than none: True; none rate 0%; skill Wilson [0%, 28%].

## Per-gate failures

- **none**: cli_export x1, cli_valid x1, elements_described x1, explicit_view_keys x1, external_system_tagged x5, has_person x1, has_system x1, has_view x1, mcp_limit_stated x5, relationship_technology x4, validate_ok_called x4, views_within_element_bound x4
- **skill**: explicit_view_keys x1, external_system_tagged x5, has_view x1, mcp_limit_stated x5, relationship_technology x4, validate_ok_called x4, views_within_element_bound x2

## Flags

- **none**: timeout=2, contended=0, cached=10
- **skill**: timeout=1, contended=0, cached=0

## Cost estimate (Task 100.170)

Measured over 10 trial(s): median 305.3 s, mean 437.3 s, max 1200.7 s.
Full run = 90 trials -> 7.6 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

