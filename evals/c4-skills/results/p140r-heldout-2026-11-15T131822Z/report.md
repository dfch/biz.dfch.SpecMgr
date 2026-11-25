# Run report: p140r-heldout-2026-11-15T131822Z

Label: p140r-heldout; cases: heldout-views; conditions: none, skill; k=5; seed=748702.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 0 | 5 | 0% | [0%, 43%] | 0.000 | heldout-views: 0/5 |
| skill | 0 | 5 | 0% | [0%, 43%] | 0.000 | heldout-views: 0/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

ok=True; rate margin 0.0 pp (limit 10); clearly worse cases: none; not worse than none: True; none rate 0%; skill Wilson [0%, 43%].

## Per-gate failures

- **none**: cli_export x1, cli_valid x1, dsl_written x1, elements_described x1, explicit_view_keys x2, external_system_tagged x4, has_person x1, has_system x1, has_view x2, relationship_technology x5, validate_ok_called x5, views_within_element_bound x3
- **skill**: cli_export x1, cli_valid x1, elements_described x1, explicit_view_keys x2, external_system_tagged x5, has_person x1, has_system x1, has_view x2, relationship_technology x5, validate_ok_called x4, views_within_element_bound x2

## Flags

- **none**: timeout=0, contended=0, cached=5
- **skill**: timeout=2, contended=2, cached=0

## Cost estimate (Task 100.170)

Measured over 5 trial(s): median 889.6 s, mean 995.0 s, max 1200.8 s.
Full run = 90 trials -> 22.2 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

