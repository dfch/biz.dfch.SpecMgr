# Run report: p150-prove-2026-11-16T070512Z

Label: p150-prove; cases: review-model, no-trigger, heldout-review; conditions: none, upstream; k=5; seed=812712.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 0 | 15 | 0% | [0%, 20%] | 0.000 | heldout-review: 0/5; no-trigger: 0/5; review-model: 0/5 |
| upstream | 0 | 15 | 0% | [0%, 20%] | 0.000 | heldout-review: 0/5; no-trigger: 0/5; review-model: 0/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

No `skill` condition in this run (Phase 100 measures `none` vs `upstream` as the baseline pair). The margin machinery activates with the first skill phase: the skill's pass rate must be not more than 10 percentage points lower than the comparison condition, no case may be clearly worse (>= 2 fewer passes out of k), and the skill must be not worse than `none`.

Information: `upstream` vs `none` differ by +0 percentage points (none 0% vs upstream 0%).

## Per-gate failures

- **none**: crowded_view_found x10, external_tag_found x5, keyless_view_found x6, library_container_found x6, mcp_limit_stated x5, no_false_findings x5, orphan_found x5, vague_label_found x6
- **upstream**: crowded_view_found x9, external_tag_found x2, keyless_view_found x2, library_container_found x2, mcp_limit_stated x4, no_false_findings x8, no_mounted_skill_loaded x5, orphan_found x2, vague_label_found x2

## Flags

- **none**: timeout=9, contended=12, cached=0
- **upstream**: timeout=4, contended=9, cached=0

## Cost estimate (Task 100.170)

Measured over 30 trial(s): median 805.6 s, mean 804.6 s, max 1201.1 s.
Full run = 90 trials -> 20.1 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

