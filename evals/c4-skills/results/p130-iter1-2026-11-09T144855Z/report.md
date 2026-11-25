# Run report: p130-iter1-2026-11-09T144855Z

Label: p130-iter1; cases: modeling-decisions, no-trigger; conditions: none, upstream, skill; k=5; seed=10585.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 2 | 10 | 20% | [6%, 51%] | 0.000 | modeling-decisions: 0/5; no-trigger: 2/5 |
| upstream | 0 | 10 | 0% | [0%, 28%] | 0.000 | modeling-decisions: 0/5; no-trigger: 0/5 |
| skill | 1 | 10 | 10% | [2%, 40%] | 0.000 | modeling-decisions: 1/5; no-trigger: 0/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

ok=False; rate margin -10.0 pp (limit 10); clearly worse cases: none; not worse than none: False; none rate 20%; skill Wilson [2%, 40%].

## Per-gate failures

- **none**: cli_export x2, cli_valid x2, container_count x2, elements_described x2, external_system_tagged x5, has_person x2, has_system x2, has_view x3, mcp_limit_stated x3, no_library_container x2, no_vague_labels x2, relationship_technology x4, validate_ok_called x5
- **upstream**: container_count x2, mcp_limit_stated x4, no_library_container x4, no_mounted_skill_loaded x3, validate_ok_called x5
- **skill**: container_count x3, has_view x1, mcp_limit_stated x5, no_library_container x4, relationship_technology x3, validate_ok_called x3

## Flags

- **none**: timeout=4, contended=1, cached=10
- **upstream**: timeout=2, contended=1, cached=10
- **skill**: timeout=2, contended=0, cached=0

## Cost estimate (Task 100.170)

Measured over 10 trial(s): median 448.9 s, mean 607.4 s, max 1201.1 s.
Full run = 90 trials -> 11.2 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

