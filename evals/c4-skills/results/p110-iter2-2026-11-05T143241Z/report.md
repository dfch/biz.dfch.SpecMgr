# Run report: p110-iter2-2026-11-05T143241Z

Label: p110-iter2; cases: create-system, mcp-limits, no-trigger; conditions: none, skill; k=5; seed=865648.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 0 | 15 | 0% | [0%, 20%] | 0.000 | create-system: 0/5; mcp-limits: 0/5; no-trigger: 0/5 |
| skill | 4 | 15 | 27% | [11%, 52%] | 0.000 | create-system: 2/5; mcp-limits: 2/5; no-trigger: 0/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

ok=True; rate margin -26.67 pp (limit 10); clearly worse cases: none; not worse than none: True; none rate 0%; skill Wilson [11%, 52%].

## Per-gate failures

- **none**: cli_export x4, cli_valid x5, has_person x4, has_system x4, has_view x5, inspect_called x5, limits_acknowledged x3, mcp_limit_stated x5, parse_called x5, relationship_technology x5, triage_complete x8, two_containers x4, validate_ok_called x5, validated_before_return x10
- **skill**: cli_export x1, cli_valid x2, dsl_written x1, has_person x1, has_system x1, has_view x1, inspect_called x1, limits_acknowledged x1, mcp_limit_stated x5, parse_called x1, relationship_technology x1, triage_complete x3, two_containers x2, validate_ok_called x1, validated_before_return x1

## Flags

- **none**: timeout=3, contended=0, cached=15
- **skill**: timeout=4, contended=2, cached=0

## Cost estimate (Task 100.170)

Measured over 15 trial(s): median 455.0 s, mean 593.9 s, max 1201.3 s.
Full run = 90 trials -> 11.4 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

