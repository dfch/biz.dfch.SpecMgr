# Run report: smoke-2026-11-01T224901Z

Label: smoke; cases: smoke-create-system; conditions: none, upstream; k=2; seed=573341.
Version tuple hash: `0de1ba9850e9d7e426a2f12a852cf17d25b2f2f5d0d12f528ce3b4cb2395a7b4`; preflight ok: True.

## Pass rates

| Condition | Passes | Trials | Rate | Wilson (95%) | pass^k (info) | Per-case |
|---|---|---|---|---|---|---|
| none | 1 | 2 | 50% | [9%, 91%] | 0.250 | smoke-create-system: 1/2 |
| upstream | 1 | 2 | 50% | [9%, 91%] | 0.250 | smoke-create-system: 1/2 |

Wilson intervals and pass^k are information only (k is small).

## Gate margins (ACC-008 / ACC-012 machinery)

No `skill` condition in this run (Phase 100 measures `none` vs `upstream` as the baseline pair). The margin machinery activates with the first skill phase: the skill's pass rate must be not more than 10 percentage points lower than the comparison condition, no case may be clearly worse (>= 2 fewer passes out of k), and the skill must be not worse than `none`.

Information: `upstream` vs `none` differ by +0 percentage points (none 50% vs upstream 50%).

## Per-gate failures

- **upstream**: cli_export x1, cli_valid x1, dsl_written x1, has_person x1, has_system x1, has_view x1, relationship_technology x1, two_containers x1

## Flags

- **none**: timeout=1, contended=0, cached=0
- **upstream**: timeout=0, contended=0, cached=0

## Cost estimate (Task 100.170)

Measured over 4 trial(s): median 317.7 s, mean 464.0 s, max 1200.0 s.
Full run = 90 trials -> 7.9 h at the median per-trial time (budget 30.0 h at the 1200 s timeout: 30.0 h worst case). Within budget at median: True.

Per-phase expectation: each skill phase is measured on its own cases against `none` and its comparison condition, with the `none`/`upstream` baselines cached, so a phase costs only its `skill` trials plus any uncached baselines. See the run label and the case list above; cached `none`/`upstream` trials cost zero model time.

