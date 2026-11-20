# Draft: Phase 160 results write-up (Task 160.110 skeleton)

DRAFT — pre-drafted 2026-11-20 against the post-merge base (`d0fd1434`) for
the Phase 160 session. Every figure below was read from a committed file
under `evals/c4-skills/` at draft time (the file is cited per section); no
number is re-derived from memory. The Phase 160 session finalizes this into
`evals/c4-skills/results/` once Task 160.100's cumulative run lands (see the
PENDING section) — this draft is the skeleton and the verified-to-date
content.

## Version surface (invariant across all five phases)

Version tuple hash `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`
in every run's `run.json`/`report.json` (verified in all nine canonical runs
cited below). The final grader hash is
`b4ae81afcc4ae8e5c0484e480a6dc18ea1c9bf0b75e458c5a3c5d90a4ee8f81b`
(recorded in the result-cache keys, e.g.
`evals/c4-skills/cache/heldout-review.none.json`; re-verified unchanged by
the 2026-11-20 origin/dev merge). OpenCode
`ghcr.io/anomalyco/opencode:2.2.5`, Structurizr MCP
`structurizr/mcp:2026.04.20`, Structurizr CLI
`structurizr/structurizr:2026.10.26-noble` (matching pair), Python 3.13.13,
`jq` 1.6, upstream pinned `jrjsmrtn/c4-skills` @
`e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b`, model
`qwen3.8-27b-bf16-896k` on `vllm-sys0` (vLLM 0.26.0, MTP 5 speculative
tokens), sampling temperature 0.0 / topP 1.0 / seed 1337 (the `version_tuple`
block of any cited `run.json`; pins at `evals/c4-skills/c4_skills/pins.py`).

## Per-phase results (the committed canonical runs)

| Phase | Skill | Stop-rule run (label, seed) | skill | comparison | none | Held-out run (label, seed) | held-out skill | held-out baselines | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 110 | `structurizr-validate-loop` | `p110-iter2-2026-11-05T143241Z` (p110-iter2, 865648), comparison `none` | 4/15 | — | 0/15 | `p110-heldout-2026-11-05T203735Z` (p110-heldout, 743505) | 4/5 | none 0/5 (5 cache hits) | clean |
| 120 | `structurizr-dsl-authoring` | `p120-iter1-2026-11-07T231831Z` (p120-iter1, 93247), comparison `upstream` | 5/20 | upstream 0/20 | 1/20 | `p120-heldout-2026-11-08T004718Z` (p120-heldout, 98838) | 5/5 | none 0/5, upstream 0/5 (cache hits) | clean |
| 130 | `c4-modeling` | `p130-iter2-2026-11-09T172621Z` (p130-iter2, 31001), comparison `upstream` | 3/10 | upstream 0/10 | 2/10 | `p130-heldout-2026-11-09T214830Z` (p130-heldout, 31812) | 1/5 | none 0/5, upstream 0/5 (cache hits) | clean — degraded-window floor recorded |
| 140 | `c4-view-design` | `p140r-skill-2026-11-15T083350Z` (p140r-skill, 731630), comparison `none`, locked 12-gate | 0/10 (locked; Option A skill-owned 2/5 on `design-views` vs 0/5) | — | 0/10 (locked; skill-owned 0/5) | `p140r-heldout-2026-11-15T131822Z` (p140r-heldout, 748702) | 0/5 (locked; skill-owned 1/5) | none 0/5 (5 cache hits) | clean — HAProxy-restart note on the k4 taint |
| 150 | `c4-model-review` | `p150-iter1-2026-11-17T202412Z` (p150-iter1, 947052), comparison `upstream`, full locked 9-gate set (no Option A narrowing) | 2/10 | upstream 0/10 | 0/10 | **PENDING** (`p150-heldout-2026-11-19T070020Z` aborted partial, no `run.json`) | — | 10 cache hits pre-verified (see PENDING) | **PENDING** — two abort cycles under the 38 h external load; forensics 9/9 + 8/9 partial passes cited; no verdict |

All cells above: the run's own `report.json` (`per_condition.*.passes`/
`trials`, `skill_margins.margin`), cited per phase below. Stop-rule margins
(`report.json → skill_margins.margin`): P110 `ok: true, rate_margin_pp:
-26.67, better_than_none: true, clearly_worse_cases: []`; P120 `ok: true,
-25.0, true, []`; P130 `ok: true, -30.0, true, []`; P140r `ok: true, 0.0
(tie), true, []` (the locked-12-gate computation — the Option A
skill-owned adjudication stands on the per-trial records, the 2026-11-15
16:03:10.777Z README entry); P150 `ok: true, -20.0, true, []`.

### Phase 110 (`structurizr-validate-loop`)

Stop-rule run `p110-iter2-2026-11-05T143241Z` (seed 865648; cases
`create-system`, `mcp-limits`, `no-trigger`; conditions `none`, `skill`):
`skill` 4/15 (`create-system` 2/5, `mcp-limits` 2/5, `no-trigger` 0/5 as
designed) vs `none` 0/15. Measured variant hash `927d6c3fc039…`
(`run.json → skill_variant_hash`); the committed variant is
`48c9b87bdee8…` after the 2026-11-07 review remediation's one-character
ADR-citation fix (citation-only editorial change post-dating the
measurement — the E1 Decisions-Made entry). Held-out
`p110-heldout-2026-11-05T203735Z` (seed 743505, `heldout-validate`):
`skill` 4/5 vs `none` 0/5 (all 5 `none` trials cache hits) — clean, no
caveat. Prove `p110-prove2-2026-11-04T200612Z` (seed 448993; cases
`create-system`, `mcp-limits`, `no-trigger`, `heldout-validate`): `none`
0/20 — ACC-013 clause 1 holds on all four cases; clause 2 via the `skill`
condition in the iteration/held-out runs (the locked Phase 110 reading).

### Phase 120 (`structurizr-dsl-authoring`)

Stop-rule run `p120-iter1-2026-11-07T231831Z` (seed 93247; cases
`create-system`, `mcp-limits`, `fix-dsl`, `no-trigger`; conditions
`none`, `upstream`, `skill`): `skill` 5/20 (the 5 passes are all
`fix-dsl` — the authoring-knowledge case; the two reused loop cases
`create-system`/`mcp-limits` are 0/5 for all three conditions, as designed
for a non-loop skill) vs `upstream` 0/20 vs `none` 1/20 (the one `none`
pass is a `no-trigger` trial). Measured = committed variant
`cb4abc13146d…20843` (v1, frozen before the held-out). Held-out
`p120-heldout-2026-11-08T004718Z` (seed 98838, `heldout-dsl`): `skill` 5/5
vs `none` 0/5 / `upstream` 0/5 (all 10 baseline trials cache hits) — clean,
no caveat. Prove `p120-prove-2026-11-07T185741Z` (seed 77027; the five
cases incl. `heldout-dsl`): `none` 1/25 (only `no-trigger` 1/5),
`upstream` 0/25 — ACC-013 clause 1 holds on all five; clause 2 via
`skill` (iter1 `fix-dsl` 5/5, held-out 5/5).

### Phase 130 (`c4-modeling`)

Stop-rule run `p130-iter2-2026-11-09T172621Z` (seed 31001; cases
`modeling-decisions`, `no-trigger`; conditions `none`, `upstream`,
`skill`): `skill` 3/10 (`modeling-decisions` 2/5, `no-trigger` 1/5) vs
`upstream` 0/10 vs `none` 2/10 (`no-trigger` 2/5, `modeling-decisions`
0/5). Measured = committed variant `fb5499769b0a…a1094a` (v2, the
iteration-2 winner; v1 `36335e97…03204` superseded). Held-out
`p130-heldout-2026-11-09T214830Z` (seed 31812, `heldout-modeling`):
`skill` 1/5 vs `none` 0/5 / `upstream` 0/5 (all 10 baseline trials cache
hits) — clean under the hybrid rule (1/5 ≥ 0/5, not 0/5, not below
`none`), BUT the window was degraded: the `skill` flags are
`{cached: 0, contended: 5, timeout: 4}` and the `cost_estimate` is
`within_budget_at_median: false` (median 1201.3 s) — the recorded 1/5 is a
floor on the skill's held-out performance (the Phase 130 Decisions-Made
"held-out degradation record"; the Phase 160 full re-run measures the case
again in its own window). Prove `p130-prove-2026-11-09T063128Z` (seed
64292; cases `modeling-decisions`, `no-trigger`, `heldout-modeling`):
`none` 2/15 (`no-trigger` 2/5), `upstream` 0/15 — ACC-013 clause 1 holds
on all three; clause 2 via `skill` (iter2 2/5, held-out 1/5) and in-phase
for `no-trigger` (`none` 2/5 in the prove).

### Phase 140 (`c4-view-design`)

Stop-rule run `p140r-skill-2026-11-15T083350Z` (seed 731630; cases
`design-views`, `no-trigger`; conditions `none`, `skill`; the locked
12-gate set): `skill` 0/10 vs `none` 0/10, `margin.ok: true` at a 0.0 pp
tie. Under the user's 2026-11-15 Option A ruling (locked clause in the
Decisions-Made entry of 2026-11-15 13:15:01.000Z), the "clears its own
gates" clause is adjudicated over the skill-owned 9-gate set on
`design-views` from the per-trial records: `skill` 2/5 (k2, k4 full
skill-owned passes) vs `none` 0/5 — stop rule PASS on the recorded stage-2
data (the per-trial re-evaluation is the 2026-11-15 16:03:10.777Z README
entry; the harness `report.json` locked-12-gate figures are cited as such).
Measured = committed variant `24c89794bc9e…6d7d` (v3, frozen). Held-out
`p140r-heldout-2026-11-15T131822Z` (seed 748702, `heldout-views`): locked
12-gate `skill` 0/5 vs `none` 0/5 (5 `none` cache hits, gate data
byte-identical to the prove); skill-owned 1/5 (k0) — clean under the
hybrid rule (≥1/5). Window facts: 2/5 skill timeouts (under the 3/5
threshold), 0 busy-waits, median 889.6 s, 2 contended flags; plus the
HAProxy-restart note (restart 14:07:22Z inside the window taints k4 —
k4's gate failures are the agent's recorded deliberate no-view judgment,
the verdict-deciding k0 pass ran ~50 min before the restart with zero
error events; the 1/5 is a conservative lower bound). Prove
`p140r-prove-2026-11-15T060904Z` (seed 722944; cases `design-views`,
`heldout-views`, `no-trigger`): `none` 0/15 — ACC-013 clause 1 holds on
all three; clause 2 via `skill` (stage 2 skill-owned 2/5, held-out 1/5).
The earlier degraded-window prove `p140-prove-2026-11-10T133052Z` (seed
41733, `none` 1/15) is superseded history, not the canonical prove.

### Phase 150 (`c4-model-review`)

Stop-rule run `p150-iter1-2026-11-17T202412Z` (seed 947052; cases
`review-model`, `no-trigger`; conditions `none`, `upstream`, `skill`; the
FULL locked 9-gate set — no Option A narrowing, which was scoped to the
single-skill Phase 140): `skill` 2/10 (`review-model` 2/5 — two full 9/9
passes, k1/k3; the other three `review-model` skill trials are 1200 s
timeouts reporting nothing; `no-trigger` 0/5 with the negative trigger
holding 5/5) vs `none` 0/10 vs `upstream` 0/10 (all 20 baseline trials
cache hits). Window: 8 of 10 fresh skill trials at the 1200 s timeout,
5 of 10 contended — a persistent external client held the shared 2-slot
vLLM from ~20:24Z onward; the stop-rule verdict is PASS at iteration 1 of
3 on the recorded data (the 3 timeouts cost the skill trials, never
fabricated its passes — 2/5 is a lower bound). Frozen variant
`89e0bc4bb4867b8885a3e393eaf1c76d3811dd39bd17702a533788f0b7620fc0` (v2 =
v1 `d615896a…03ed` + the two checklist fixes + the no-view-element-listing
report rule). Prove `p150-prove-2026-11-17T165125Z` (seed 916537; cases
`review-model`, `no-trigger`, `heldout-review`): `none` 0/15 AND
`upstream` 0/15 — ACC-013 clause 1 holds on all three; clause 2 for
`review-model` via `skill` (iter1 2/5); for `heldout-review` **PENDING**
the held-out run; `no-trigger` stands on its home-phase data per the
byte-unchanged reused-case adjudication (reused byte-unchanged; Phase 130
prove `none` 2/5; here `none` 0/5 with every trial failing ONLY the known
`mcp_limit_stated` matcher deviation).

Held-out: **PENDING** — see the PENDING section.

## Per-skill "better than none on which gates" (ACC-012)

From each canonical stop-rule run's `report.json → per_condition.*.gate_failures`
(gate-failure counts over the run's trials per condition; "a → b" = the
gate failed on a trials without the skill and b with it — lower is better;
a gate absent from a condition's dict failed on zero of its trials). The
`none` deltas are the ACC-012 "better than none" statement per skill; the
`upstream` deltas are the comparison-condition statement where the phase
compares against `upstream`.

### `structurizr-validate-loop` (`p110-iter2-2026-11-05T143241Z`, 15 trials per condition)

Better than `none`: `cli_export` 4→1, `cli_valid` 5→2, `has_person` 4→1,
`has_system` 4→1, `has_view` 5→1, `inspect_called` 5→1,
`limits_acknowledged` 3→1, `parse_called` 5→1,
`relationship_technology` 5→1, `triage_complete` 8→3, `two_containers`
4→2, `validate_ok_called` 5→1, `validated_before_return` 10→1. Tie:
`mcp_limit_stated` 5→5 (the documented Phase 110 no-trigger matcher
deviation — affects both conditions identically). The wins are exactly the
loop-delta gates (`parse_called`/`validate_ok_called`/`inspect_called`/
`triage_complete`/`validated_before_return`), as designed.

### `structurizr-dsl-authoring` (`p120-iter1-2026-11-07T231831Z`, 20 trials per condition)

Better than `none`: `cli_export` 5→2, `cli_valid` 5→2,
`elements_described` 5→0, `has_person` 5→2, `has_system` 5→2, `has_view`
5→2, `relationship_technology` 10→2, `triage_complete` 7→5,
`two_containers` 5→2, `validate_ok_called` 8→4. Ties: `inspect_called`
5→5, `validated_before_return` 10→10 (the loop-discipline gates — neutral
as designed for a non-loop skill). Worse: `mcp_limit_stated` 4→5,
`parse_called` 5→9 (the no-trigger matcher deviation; `parse_called` on
the non-loop cases where the skill does not mandate the loop).
Better than `upstream`: `elements_described` 4→0,
`limits_acknowledged` 1→0, `no_deletions` 2→0,
`no_mounted_skill_loaded` 5→0 (the upstream's ungated
`structurizr-dsl` description loads on 5/5 no-trigger render prompts — the
harsh baseline; ours loads 0/20), `relationship_technology` 7→2,
`validate_ok_called` 5→4. Ties: `cli_export` 2→2, `cli_valid` 2→2,
`has_person` 2→2, `has_system` 2→2, `has_view` 2→2, `mcp_limit_stated`
5→5, `triage_complete` 5→5, `two_containers` 2→2,
`validated_before_return` 10→10. Worse: `inspect_called` 3→5,
`parse_called` 5→9 (loop-discipline, not this skill's delta — the locked
Phase 120 separation).

### `c4-modeling` (`p130-iter2-2026-11-09T172621Z`, 10 trials per condition)

Better than `none`: `cli_export` 2→0, `cli_valid` 2→0,
`container_count` 2→0, `elements_described` 2→0,
`external_system_tagged` 5→0, `has_person` 2→0, `has_system` 2→0,
`no_library_container` 2→0, `no_vague_labels` 2→0,
`relationship_technology` 4→0, `validate_ok_called` 5→3, `has_view` 3→1.
Worse: `mcp_limit_stated` 3→4 (the documented no-trigger matcher
deviation). The wins are exactly the modeling-decision gates
(`external_system_tagged`, `no_library_container`, `no_vague_labels`,
`container_count`) plus the create-family shape gates.
Better than `upstream`: `container_count` 2→0,
`no_library_container` 4→0, `no_mounted_skill_loaded` 3→0 (the upstream's
ungated `c4-model` description loaded on 3/5 no-trigger prompts; ours
0/10), `validate_ok_called` 5→3. Tie: `mcp_limit_stated` 4→4.

### `c4-view-design` (`p140r-skill-2026-11-15T083350Z`, 10 trials per condition, locked 12-gate)

Better than `none`: `cli_export` 1→0, `cli_valid` 1→0,
`elements_described` 1→0, `has_person` 1→0, `has_system` 1→0,
`views_within_element_bound` 4→2. Ties: `explicit_view_keys` 1→1,
`external_system_tagged` 5→5, `has_view` 1→1, `mcp_limit_stated` 5→5,
`relationship_technology` 4→4, `validate_ok_called` 4→4. (The three
create-family ties are the cross-skill gates Option A keeps out of the
single-skill clause — re-demanded in the Phase 160 cumulative run; the
`none` baseline fails them in the same trials, hence the locked 0/10 vs
0/10 tie.) The skill-owned adjudication (2/5 vs 0/5 on `design-views`)
stands on the per-trial records — see the Phase 140 section above.

### `c4-model-review` (`p150-iter1-2026-11-17T202412Z`, 10 trials per condition, full locked 9-gate set)

Better than `none`: `crowded_view_found` 5→3, `no_false_findings` 2→0,
`vague_label_found` 4→3. Ties: `external_tag_found` 3→3,
`keyless_view_found` 3→3, `library_container_found` 3→3,
`orphan_found` 3→3, `mcp_limit_stated` 5→5. All `skill` detection-gate
failures come from the 3 timed-out `review-model` trials (window
degradation — they report nothing); the two completed full passes (k1, k3)
clear every one of the 9 gates.
Better than `upstream`: `crowded_view_found` 4→3, `no_false_findings`
5→0, `no_mounted_skill_loaded` 5→0 (the upstream's ungated skill
description loads on 5/5 no-trigger prompts). Tie: `mcp_limit_stated`
5→5. (`upstream` passed the six detection gates on its trials — its
`c4-review` skill does produce findings — but failed the clean control
5/5.)

## Provenance

The committed provenance table (source, commit checked, license file,
license type, check date — all three sources MIT-verified 2026-11-01; the
ideas-only sources with no license) is
`evals/c4-skills/results/provenance.md` (Task 100.190). This write-up
references it and does not duplicate it. The per-skill `NOTICE.md` +
`source-map.md` pairs are the passage-level attribution (ACC-010).

## The upstream Docker-CLI handicap (design fact)

The `upstream` condition is deliberately unpatched
(`jrjsmrtn/c4-skills` @ `e86d8a91…` fetched at run time, never modified —
the Measurement section of the plan README and `provenance.md`). Its
DSL skills carry Docker-CLI validation steps ("run `docker run
structurizr/structurizr ... validate`" and friends) that cannot work
inside the trial container (the container has no Docker daemon and egress
is blocked to the private internal network), so the upstream agent is
advised to do something it structurally cannot do — making `upstream` a
harsh comparison baseline (it also loses every no-trigger trial to its
own ungated trigger descriptions, `no_mounted_skill_loaded` 5/5 or 3/5
per phase). The plan's locked consequence: every phase also has to beat
`none` per ACC-012, because `none` is the floor a real skill must clear
regardless of how harsh the upstream baseline is. This write-up says so,
as the plan requires.

## PENDING (explicitly marked — finalizes in the Phase 160 session)

1. **The Phase 150 held-out verdict (clean vs "accepted with caveat").**
   Awaiting the `heldout-review` campaign under a healthy shared-vLLM
   window: the 2026-11-18 and 2026-11-19 launches both aborted on the
   locked 1-h busy-wait (two abort cycles, the bounded-wait policy's
   limit) under a ~38 h sustained external load (the monitor log
   `work/p150-window-wait.log` in this feature folder records the wait;
   the forensics of both partials are under `work/p150-heldout-abort{1,2}-*`
   and `phase-150-heldout-status.md`). The forensics cite two partial
   skill passes that never count toward a verdict (belonging to aborted
   runs): 9/9 (`p150-heldout-2026-11-18T154347Z` skill-k2, 678 s,
   contended) and 8/9 (`p150-heldout-2026-11-19T070020Z` skill-k0,
   598.6 s, contended, failing only `no_false_findings`). The 10
   `none`/`upstream` trials are pre-verified cache hits under the
   current pins (the keys in
   `evals/c4-skills/cache/heldout-review.{none,upstream}.json` — grader
   hash `b4ae81af…`, version tuple `f22635f6…`, 5 trials each). Hybrid
   rule: 0/5 or below `none`'s 0/5 ⇒ "accepted with caveat" (rechecked
   here); ≥1/5 ⇒ clean. The untracked partial
   `evals/c4-skills/results/p150-heldout-2026-11-19T070020Z/` (no
   `run.json`) is swept per the locked policy before the relaunch.
2. **Task 160.100's cumulative run** (all five skills loaded on all cases,
   `none` + `upstream` baselines, under the final grader hash
   `b4ae81af…`). Recheck every caveat/floor recorded above: Phase 130's
   held-out 1/5 degraded-window floor (4/5 timeouts, all contended),
   Phase 140's Option A follow-through (the full locked 12-gate
   conjunction on `design-views`/`heldout-views` with all five skills
   loaded — the cross-skill create-family gates the single-skill phase
   could not teach), and Phase 150's held-out when it lands. Baselines
   re-measure fresh where the cache keys no longer match; `none`/
   `upstream` trials cached under the final hash stay hits.
3. **The `FULL_CASES` composition call.** `pins.py:249`
   (`evals/c4-skills/c4_skills/pins.py`) currently defines
   `FULL_CASES` with SEVEN members — `create-system`, `fix-dsl`,
   `modeling-decisions`, `mcp-limits`, `design-views`, `review-model`,
   `no-trigger` — while `report.py:43`
   (`evals/c4-skills/c4_skills/report.py`) keeps
   `BUDGET_FULL_CASES = 6` (the plan-locked budget statement: 6 cases ×
   3 conditions × k=5 = 90 trials, ≤ 30 h at timeout). Phase 160 must
   decide and record whether the cumulative run covers the 7-case set
   (105 trials — a budget statement revision, recorded) or a 6-case
   subset (which case drops, and why), and state it in the final
   results.
4. **The no-trigger `mcp_limit_stated` matcher revisit** (the documented
   Phase 110 deviation — Decisions-Made entry "no-trigger known
   limitation (accepted 2026-11-05)"). Every phase's no-trigger data
   shows it persisting: P110 `none` 0/5 and `skill` 0/5 (every trial
   fails only the loose matcher — the agents state the no-image limit in
   phrasings it does not cover), P120 `none` 1/5 / `skill` 0/5 /
   `upstream` 0/5, P130 `none` 2/5 / `skill` 1/5 (gate-failure count 4)
   / `upstream` 0/5, P140r `none` 0/5 / `skill` 0/5 (5→5 tie in the
   locked 12-gate), P150 `none` 0/5 / `upstream` 0/5 / `skill` 0/5 (5 on
   all three conditions). Phase 160 revisits matcher coverage vs the
   agents' natural phrasings and records the outcome (the gate never
   distorted a stop rule — 0 vs 0 ties throughout — but the ACC-012
   "which gates better" statement above carries it as a tie/deviation
   each phase).
