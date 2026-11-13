# Run report: p120-heldout-2026-11-08T004718Z

Label: p120-heldout; cases: heldout-dsl; conditions: none, upstream, skill; k=5; seed=98838.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 0 | 5 | 0% | [0%, 43%] | 0.000 | heldout-dsl: 0/5 |
| upstream | 0 | 5 | 0% | [0%, 43%] | 0.000 | heldout-dsl: 0/5 |
| skill | 5 | 5 | 100% | [57%, 100%] | 1.000 | heldout-dsl: 5/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

ok=True; rate margin -100.0 pp (limit 10); clearly worse cases: none; not worse than none: True; none rate 0%; skill Wilson [57%, 100%].

## Per-gate failures

- **none**: elements_described x5, relationship_technology x5
- **upstream**: elements_described x4, no_deletions x3, relationship_technology x5

## Flags

- **none**: timeout=0, contended=0, cached=5
- **upstream**: timeout=0, contended=0, cached=5
- **skill**: timeout=0, contended=0, cached=0

## Cost estimate (Task 100.170)

Measured over 5 trial(s): median 64.8 s, mean 249.2 s, max 978.6 s.
Full run = 90 trials -> 1.6 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

