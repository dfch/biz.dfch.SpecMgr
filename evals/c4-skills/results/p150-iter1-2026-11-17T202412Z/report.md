# Run report: p150-iter1-2026-11-17T202412Z

Label: p150-iter1; cases: review-model, no-trigger; conditions: none, upstream, skill; k=5; seed=947052.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 0 | 10 | 0% | [0%, 28%] | 0.000 | no-trigger: 0/5; review-model: 0/5 |
| upstream | 0 | 10 | 0% | [0%, 28%] | 0.000 | no-trigger: 0/5; review-model: 0/5 |
| skill | 2 | 10 | 20% | [6%, 51%] | 0.000 | no-trigger: 0/5; review-model: 2/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

ok=True; rate margin -20.0 pp (limit 10); clearly worse cases: none; not worse than none: True; none rate 0%; skill Wilson [6%, 51%].

## Per-gate failures

- **none**: crowded_view_found x5, external_tag_found x3, keyless_view_found x3, library_container_found x3, mcp_limit_stated x5, no_false_findings x2, orphan_found x3, vague_label_found x4
- **upstream**: crowded_view_found x4, mcp_limit_stated x5, no_false_findings x5, no_mounted_skill_loaded x5
- **skill**: crowded_view_found x3, external_tag_found x3, keyless_view_found x3, library_container_found x3, mcp_limit_stated x5, orphan_found x3, vague_label_found x3

## Flags

- **none**: timeout=3, contended=3, cached=10
- **upstream**: timeout=2, contended=3, cached=10
- **skill**: timeout=8, contended=5, cached=0

## Cost estimate (Task 100.170)

Measured over 10 trial(s): median 1200.8 s, mean 1168.4 s, max 1200.9 s.
Full run = 90 trials -> 30.0 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: False.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

