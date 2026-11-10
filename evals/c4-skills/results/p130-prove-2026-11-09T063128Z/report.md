# Run report: p130-prove-2026-11-09T063128Z

Label: p130-prove; cases: modeling-decisions, no-trigger, heldout-modeling; conditions: none, upstream; k=5; seed=64292.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 2 | 15 | 13% | [4%, 38%] | 0.000 | heldout-modeling: 0/5; modeling-decisions: 0/5; no-trigger: 2/5 |
| upstream | 0 | 15 | 0% | [0%, 20%] | 0.000 | heldout-modeling: 0/5; modeling-decisions: 0/5; no-trigger: 0/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

No `skill` condition in this run (Phase 100 measures `none` vs `none` as the baseline pair). The margin machinery activates with the first skill phase: the skill's pass rate must be not more than 10 percentage points lower than the comparison condition, no case may be clearly worse (>= 2 fewer passes out of k), and the skill must be not worse than `none`.

Information: `none` vs `none` differ by +0 percentage points (none 13% vs none 13%).

## Per-gate failures

- **none**: cli_export x5, cli_valid x5, container_count x7, dsl_written x2, elements_described x5, external_system_tagged x9, has_person x5, has_system x5, has_view x6, mcp_limit_stated x3, no_library_container x4, no_vague_labels x6, relationship_technology x8, validate_ok_called x9
- **upstream**: cli_export x1, cli_valid x1, container_count x3, dsl_written x1, elements_described x1, external_system_tagged x1, has_person x1, has_system x1, has_view x1, mcp_limit_stated x4, no_library_container x6, no_mounted_skill_loaded x3, no_vague_labels x1, relationship_technology x1, validate_ok_called x10

## Flags

- **none**: timeout=7, contended=2, cached=0
- **upstream**: timeout=7, contended=4, cached=0

## Cost estimate (Task 100.170)

Measured over 30 trial(s): median 1097.9 s, mean 824.8 s, max 1201.3 s.
Full run = 90 trials -> 27.4 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

