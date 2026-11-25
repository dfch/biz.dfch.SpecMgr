# Run report: p130-iter2-2026-11-09T172621Z

Label: p130-iter2; cases: modeling-decisions, no-trigger; conditions: none, upstream, skill; k=5; seed=31001.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 2 | 10 | 20% | [6%, 51%] | 0.000 | modeling-decisions: 0/5; no-trigger: 2/5 |
| upstream | 0 | 10 | 0% | [0%, 28%] | 0.000 | modeling-decisions: 0/5; no-trigger: 0/5 |
| skill | 3 | 10 | 30% | [11%, 60%] | 0.000 | modeling-decisions: 2/5; no-trigger: 1/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

ok=True; rate margin -30.0 pp (limit 10); clearly worse cases: none; not worse than none: True; none rate 20%; skill Wilson [11%, 60%].

## Per-gate failures

- **none**: cli_export x2, cli_valid x2, container_count x2, elements_described x2, external_system_tagged x5, has_person x2, has_system x2, has_view x3, mcp_limit_stated x3, no_library_container x2, no_vague_labels x2, relationship_technology x4, validate_ok_called x5
- **upstream**: container_count x2, mcp_limit_stated x4, no_library_container x4, no_mounted_skill_loaded x3, validate_ok_called x5
- **skill**: has_view x1, mcp_limit_stated x4, validate_ok_called x3

## Flags

- **none**: timeout=4, contended=1, cached=10
- **upstream**: timeout=2, contended=1, cached=10
- **skill**: timeout=1, contended=0, cached=0

## Cost estimate (Task 100.170)

Measured over 10 trial(s): median 284.1 s, mean 423.3 s, max 1201.1 s.
Full run = 90 trials -> 7.1 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

