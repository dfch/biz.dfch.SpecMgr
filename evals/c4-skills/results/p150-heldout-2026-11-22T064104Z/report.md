# Run report: p150-heldout-2026-11-22T064104Z

Label: p150-heldout; cases: heldout-review; conditions: none, upstream, skill; k=5; seed=329664.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 0 | 5 | 0% | [0%, 43%] | 0.000 | heldout-review: 0/5 |
| upstream | 0 | 5 | 0% | [0%, 43%] | 0.000 | heldout-review: 0/5 |
| skill | 2 | 5 | 40% | [12%, 77%] | 0.010 | heldout-review: 2/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

ok=True; rate margin -40.0 pp (limit 10); clearly worse cases: none; not worse than none: True; none rate 0%; skill Wilson [12%, 77%].

## Per-gate failures

- **none**: crowded_view_found x3, keyless_view_found x2, no_false_findings x5
- **upstream**: crowded_view_found x5, library_container_found x1, no_false_findings x5
- **skill**: crowded_view_found x1, external_tag_found x1, keyless_view_found x1, library_container_found x1, no_false_findings x2, orphan_found x1, vague_label_found x1

## Flags

- **none**: timeout=0, contended=2, cached=0
- **upstream**: timeout=0, contended=1, cached=0
- **skill**: timeout=0, contended=1, cached=0

## Cost estimate (Task 100.170)

Measured over 15 trial(s): median 241.5 s, mean 251.9 s, max 384.3 s.
Full run = 90 trials -> 6.0 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

