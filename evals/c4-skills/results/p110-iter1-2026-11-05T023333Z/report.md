# Run report: p110-iter1-2026-11-05T023333Z

Label: p110-iter1; cases: create-system, mcp-limits, no-trigger; conditions: none, skill; k=5; seed=671615.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 0 | 15 | 0% | [0%, 20%] | 0.000 | create-system: 0/5; mcp-limits: 0/5; no-trigger: 0/5 |
| skill | 0 | 15 | 0% | [0%, 20%] | 0.000 | create-system: 0/5; mcp-limits: 0/5; no-trigger: 0/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

ok=True; rate margin 0.0 pp (limit 10); clearly worse cases: none; not worse than none: True; none rate 0%; skill Wilson [0%, 20%].

## Per-gate failures

- **none**: cli_export x4, cli_valid x5, has_person x4, has_system x4, has_view x5, inspect_called x5, limits_acknowledged x3, mcp_limit_stated x5, parse_called x5, relationship_technology x5, triage_complete x8, two_containers x4, validate_ok_called x5, validated_before_return x10
- **skill**: cli_export x5, cli_valid x5, dsl_written x4, file_untouched x1, has_person x5, has_system x5, has_view x5, inspect_called x4, limits_acknowledged x4, mcp_limit_stated x4, no_mounted_skill_loaded x4, parse_called x4, relationship_technology x5, triage_complete x5, two_containers x5, validate_ok_called x10, validated_before_return x10

## Flags

- **none**: timeout=3, contended=0, cached=15
- **skill**: timeout=10, contended=1, cached=0

## Cost estimate (Task 100.170)

Measured over 15 trial(s): median 1201.2 s, mean 1005.5 s, max 1201.4 s.
Full run = 90 trials -> 30.0 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: False.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

