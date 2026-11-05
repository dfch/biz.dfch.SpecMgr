# Run report: p110-heldout-2026-11-05T203735Z

Label: p110-heldout; cases: heldout-validate; conditions: none, skill; k=5; seed=743505.
Version tuple hash: `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 0 | 5 | 0% | [0%, 43%] | 0.000 | heldout-validate: 0/5 |
| skill | 4 | 5 | 80% | [38%, 96%] | 0.328 | heldout-validate: 4/5 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

ok=True; rate margin -80.0 pp (limit 10); clearly worse cases: none; not worse than none: True; none rate 0%; skill Wilson [38%, 96%].

## Per-gate failures

- **none**: inspect_called x5, parse_called x5, triage_complete x5, validated_before_return x5
- **skill**: triage_complete x1

## Flags

- **none**: timeout=0, contended=0, cached=5
- **skill**: timeout=0, contended=0, cached=0

## Cost estimate (Task 100.170)

Measured over 5 trial(s): median 62.8 s, mean 57.5 s, max 64.8 s.
Full run = 90 trials -> 1.6 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

