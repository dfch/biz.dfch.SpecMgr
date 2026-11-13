# Run report: p130-heldout-2026-11-09T214830Z

Label: p130-heldout; cases: heldout-modeling; conditions: none, upstream, skill; k=5; seed=31812.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 0 | 5 | 0% | [0%, 43%] | 0.000 | heldout-modeling: 0/5 |
| upstream | 0 | 5 | 0% | [0%, 43%] | 0.000 | heldout-modeling: 0/5 |
| skill | 1 | 5 | 20% | [4%, 62%] | 0.000 | heldout-modeling: 1/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

ok=True; rate margin -20.0 pp (limit 10); clearly worse cases: none; not worse than none: True; none rate 0%; skill Wilson [4%, 62%].

## Per-gate failures

- **none**: cli_export x3, cli_valid x3, container_count x5, dsl_written x2, elements_described x3, external_system_tagged x4, has_person x3, has_system x3, has_view x3, no_library_container x2, no_vague_labels x4, relationship_technology x4, validate_ok_called x4
- **upstream**: cli_export x1, cli_valid x1, container_count x1, dsl_written x1, elements_described x1, external_system_tagged x1, has_person x1, has_system x1, has_view x1, no_library_container x2, no_vague_labels x1, relationship_technology x1, validate_ok_called x5
- **skill**: cli_export x2, cli_valid x2, container_count x2, elements_described x2, external_system_tagged x2, has_person x2, has_system x2, has_view x4, no_vague_labels x2, relationship_technology x2, validate_ok_called x3

## Flags

- **none**: timeout=3, contended=1, cached=5
- **upstream**: timeout=5, contended=3, cached=5
- **skill**: timeout=4, contended=5, cached=0

## Cost estimate (Task 100.170)

Measured over 5 trial(s): median 1201.3 s, mean 1074.7 s, max 1201.4 s.
Full run = 90 trials -> 30.0 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: False.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

