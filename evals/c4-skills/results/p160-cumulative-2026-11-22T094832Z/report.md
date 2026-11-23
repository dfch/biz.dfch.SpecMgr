# Run report: p160-cumulative-2026-11-22T094832Z

Label: p160-cumulative; cases: create-system, fix-dsl, modeling-decisions, mcp-limits, design-views, review-model, no-trigger, heldout-modeling, heldout-views; conditions: none, upstream, skill; k=5; seed=340912.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 0 | 45 | 0% | [0%, 8%] | 0.000 | create-system: 0/5; design-views: 0/5; fix-dsl: 0/5; heldout-modeling: 0/5; heldout-views: 0/5; mcp-limits: 0/5; modeling-decisions: 0/5; no-trigger: 0/5; review-model: 0/5 |
| upstream | 0 | 45 | 0% | [0%, 8%] | 0.000 | create-system: 0/5; design-views: 0/5; fix-dsl: 0/5; heldout-modeling: 0/5; heldout-views: 0/5; mcp-limits: 0/5; modeling-decisions: 0/5; no-trigger: 0/5; review-model: 0/5 |
| skill | 21 | 45 | 47% | [33%, 61%] | 0.000 | create-system: 3/5; design-views: 2/5; fix-dsl: 1/5; heldout-modeling: 5/5; heldout-views: 1/5; mcp-limits: 2/5; modeling-decisions: 5/5; no-trigger: 0/5; review-model: 2/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

ok=True; rate margin -46.67 pp (limit 10); clearly worse cases: none; not worse than none: True; none rate 0%; skill Wilson [33%, 61%].

## Per-gate failures

- **none**: cli_export x10, cli_valid x10, container_count x10, crowded_view_found x4, dsl_written x1, elements_described x10, explicit_view_keys x3, external_system_tagged x17, has_person x10, has_system x10, has_view x14, inspect_called x5, limits_acknowledged x3, mcp_limit_stated x5, no_false_findings x5, no_library_container x8, no_vague_labels x6, parse_called x5, relationship_technology x28, triage_complete x6, two_containers x5, vague_label_found x3, validate_ok_called x24, validated_before_return x10, views_within_element_bound x7
- **upstream**: cli_export x8, cli_valid x8, container_count x4, crowded_view_found x5, dsl_written x4, elements_described x9, external_system_tagged x4, has_person x8, has_system x8, has_view x8, inspect_called x5, mcp_limit_stated x5, no_false_findings x5, no_library_container x5, no_mounted_skill_loaded x4, no_vague_labels x4, parse_called x5, relationship_technology x13, triage_complete x7, two_containers x4, validate_ok_called x25, validated_before_return x10, views_within_element_bound x10
- **skill**: cli_export x4, cli_valid x4, dsl_written x1, elements_described x5, explicit_view_keys x1, external_system_tagged x1, has_person x4, has_system x4, has_view x4, mcp_limit_stated x5, no_deletions x2, no_false_findings x3, relationship_technology x4, relationships_described x2, triage_complete x3, two_containers x3, validate_ok_called x1, validated_before_return x1, views_within_element_bound x6

## Flags

- **none**: timeout=12, contended=14, cached=0
- **upstream**: timeout=15, contended=8, cached=0
- **skill**: timeout=0, contended=3, cached=0

## Cost estimate (Task 100.170)

Measured over 135 trial(s): median 360.3 s, mean 511.5 s, max 1201.7 s.
Full run = 90 trials -> 9.0 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

