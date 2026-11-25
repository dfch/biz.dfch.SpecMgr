# Run report: p120-iter1-2026-11-07T231831Z

Label: p120-iter1; cases: create-system, mcp-limits, fix-dsl, no-trigger; conditions: none, upstream, skill; k=5; seed=93247.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 1 | 20 | 5% | [1%, 24%] | 0.000 | create-system: 0/5; fix-dsl: 0/5; mcp-limits: 0/5; no-trigger: 1/5 |
| upstream | 0 | 20 | 0% | [0%, 16%] | 0.000 | create-system: 0/5; fix-dsl: 0/5; mcp-limits: 0/5; no-trigger: 0/5 |
| skill | 5 | 20 | 25% | [11%, 47%] | 0.000 | create-system: 0/5; fix-dsl: 5/5; mcp-limits: 0/5; no-trigger: 0/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

ok=True; rate margin -25.0 pp (limit 10); clearly worse cases: none; not worse than none: True; none rate 5%; skill Wilson [11%, 47%].

## Per-gate failures

- **none**: cli_export x5, cli_valid x5, elements_described x5, has_person x5, has_system x5, has_view x5, inspect_called x5, mcp_limit_stated x4, parse_called x5, relationship_technology x10, triage_complete x7, two_containers x5, validate_ok_called x8, validated_before_return x10
- **upstream**: cli_export x2, cli_valid x2, elements_described x4, has_person x2, has_system x2, has_view x2, inspect_called x3, limits_acknowledged x1, mcp_limit_stated x5, no_deletions x2, no_mounted_skill_loaded x5, parse_called x5, relationship_technology x7, triage_complete x5, two_containers x2, validate_ok_called x5, validated_before_return x10
- **skill**: cli_export x2, cli_valid x2, has_person x2, has_system x2, has_view x2, inspect_called x5, mcp_limit_stated x5, parse_called x9, relationship_technology x2, triage_complete x5, two_containers x2, validate_ok_called x4, validated_before_return x10

## Flags

- **none**: timeout=1, contended=0, cached=20
- **upstream**: timeout=1, contended=0, cached=20
- **skill**: timeout=0, contended=0, cached=0

## Cost estimate (Task 100.170)

Measured over 20 trial(s): median 109.3 s, mean 216.8 s, max 996.8 s.
Full run = 90 trials -> 2.7 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

