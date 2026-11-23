# C4/Structurizr Skills — Measurement Results (feat-250-c4-structurizr-skills)

FINAL — Phase 160 (Tasks 160.110/160.120), finalized 2026-11-23 after the
cumulative run `p160-cumulative-2026-11-22T094832Z` completed. Finalized from
the pre-draft skeleton
`.specmgr/feat/feat-250-c4-structurizr-skills/draft-p160-results-writeup.md`
(drafted 2026-11-20 against the post-merge base `d0fd1434`): every figure in
the inherited sections was read from a committed file under `evals/c4-skills/`
at draft time (the file is cited per section) and re-verified against the
current tree at finalization (the tree is unchanged except this phase's
additions); the new sections below were read from the final run dirs on
2026-11-23. The draft's four PENDING items are closed (see "Closed PENDING
items"); the ACC traceability list (Task 160.120) is the final section.

## Version surface (invariant across all five phases)

Version tuple hash `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`
in every run's `run.json`/`report.json` (verified in all canonical runs cited
below, on both machines). Grader hash: `b4ae81afcc4ae8e5c0484e480a6dc18ea1c9bf0b75e458c5a3c5d90a4ee8f81b`
on sys0 (recorded in the result-cache keys, e.g.
`evals/c4-skills/cache/heldout-review.none.json`; re-verified unchanged by
the 2026-11-20 origin/dev merge) and `b3864185b5744420d911ced32f69791355495b13c78075ffd262fdc3885f5e11`
on sys1 (path-dependent — absolute source paths fold in; recomputed on sys1
per the locked one-liner before the Phase 150 held-out and the Phase 160
cumulative run, both of which ran under it). OpenCode
`ghcr.io/anomalyco/opencode:2.2.5`, Structurizr MCP
`structurizr/mcp:2026.04.20`, Structurizr CLI
`structurizr/structurizr:2026.10.26-noble` (matching pair), Python 3.13.13,
`jq` 1.6, upstream pinned `jrjsmrtn/c4-skills` @
`e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b`, model
`qwen3.8-27b-bf16-896k` (vLLM 0.26.0, MTP 5 speculative tokens, max_model_len
917504), sampling temperature 0.0 / topP 1.0 / seed 1337 (the
`version_tuple` block of any cited `run.json`; pins at
`evals/c4-skills/c4_skills/pins.py`). The Phases 110–150 canonical runs were
measured on sys0 (shared production vLLM, provider id `vllm-sys0`); the
Phase 150 held-out and the Phase 160 cumulative run were measured on the
dedicated sys1 test instance (same provider id, same model/build — the
version tuple did not move across machines).

## Per-phase results (the committed canonical runs)

| Phase | Skill | Stop-rule run (label, seed) | skill | comparison | none | Held-out run (label, seed) | held-out skill | held-out baselines | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 110 | `structurizr-validate-loop` | `p110-iter2-2026-11-05T143241Z` (p110-iter2, 865648), comparison `none` | 4/15 | — | 0/15 | `p110-heldout-2026-11-05T203735Z` (p110-heldout, 743505) | 4/5 | none 0/5 (5 cache hits) | clean |
| 120 | `structurizr-dsl-authoring` | `p120-iter1-2026-11-07T231831Z` (p120-iter1, 93247), comparison `upstream` | 5/20 | upstream 0/20 | 1/20 | `p120-heldout-2026-11-08T004718Z` (p120-heldout, 98838) | 5/5 | none 0/5, upstream 0/5 (cache hits) | clean |
| 130 | `c4-modeling` | `p130-iter2-2026-11-09T172621Z` (p130-iter2, 31001), comparison `upstream` | 3/10 | upstream 0/10 | 2/10 | `p130-heldout-2026-11-09T214830Z` (p130-heldout, 31812) | 1/5 (degraded-window floor; re-measured 5/5 in the Phase 160 cumulative run) | none 0/5, upstream 0/5 (cache hits) | clean — degraded-window floor recorded, floor moved up in Phase 160 |
| 140 | `c4-view-design` | `p140r-skill-2026-11-15T083350Z` (p140r-skill, 731630), comparison `none`, locked 12-gate | 0/10 (locked; Option A skill-owned 2/5 on `design-views` vs 0/5) | — | 0/10 (locked; skill-owned 0/5) | `p140r-heldout-2026-11-15T131822Z` (p140r-heldout, 748702) | 0/5 (locked; skill-owned 1/5) | none 0/5 (5 cache hits) | clean — HAProxy-restart note on the k4 taint; the full locked 12-gate conjunction re-demanded in Phase 160 |
| 150 | `c4-model-review` | `p150-iter1-2026-11-17T202412Z` (p150-iter1, 947052), comparison `upstream`, full locked 9-gate set (no Option A narrowing) | 2/10 | upstream 0/10 | 0/10 | `p150-heldout-2026-11-22T064104Z` (p150-heldout, 329664) | 2/5 | none 0/5, upstream 0/5 (15 fresh trials, 0 cache hits on sys1) | CLEAN ACCEPTANCE (hybrid rule: 2/5 ≥ 1/5) — two vLLM interruptions cost the skill at most 2 trials, never fabricated a pass |

All cells above: the run's own `report.json` (`per_condition.*.passes`/
`trials`, `skill_margins.margin`), cited per phase below. Stop-rule margins
(`report.json → skill_margins.margin`): P110 `ok: true, rate_margin_pp:
-26.67, better_than_none: true, clearly_worse_cases: []`; P120 `ok: true,
-25.0, true, []`; P130 `ok: true, -30.0, true, []`; P140r `ok: true, 0.0
(tie), true, []` (the locked-12-gate computation — the Option A
skill-owned adjudication stands on the per-trial records, the 2026-11-15
16:03:10.777Z README entry); P150 `ok: true, -20.0, true, []`; P150 held-out
`ok: true, -40.0, true, []`.

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
again in its own window). **Phase 160 re-measurement (this document,
Phase 160 section): the floor moved up — 5/5 full 13-gate passes under
sys1's own window (0 timeouts, 0 contended).** Prove
`p130-prove-2026-11-09T063128Z` (seed 64292; cases
`modeling-decisions`, `no-trigger`, `heldout-modeling`): `none` 2/15
(`no-trigger` 2/5), `upstream` 0/15 — ACC-013 clause 1 holds on all three;
clause 2 via `skill` (iter2 2/5, held-out 1/5) and in-phase for
`no-trigger` (`none` 2/5 in the prove).

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
**Phase 160 follow-through (the Option A clause's locked re-demand — the
FULL locked 12-gate conjunction on `design-views`/`heldout-views` with all
five skills loaded): `design-views` skill 2/5 and `heldout-views` skill
1/5 full 12-gate passes (see the Phase 160 section).**

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
`review-model` via `skill` (iter1 2/5); for `heldout-review` via the
held-out run below (2/5); `no-trigger` stands on its home-phase data per
the byte-unchanged reused-case adjudication (reused byte-unchanged; Phase
130 prove `none` 2/5; here `none` 0/5 with every trial failing ONLY the
known `mcp_limit_stated` matcher deviation).

Held-out — `p150-heldout-2026-11-22T064104Z` (seed 329664, k=5, 1200 s,
the full locked 9-gate set, `--cases heldout-review --conditions
none,upstream,skill --comparison upstream`), run on the dedicated sys1
instance 2026-11-22 06:41:04Z–07:48:47Z (≈68 min model wall): **`skill`
2/5 vs `none` 0/5 vs `upstream` 0/5 over 15 fresh trials (0 cache hits —
the sys1-adapted expectation; a cache HIT would have been a STOP
condition, none fired)**. Per trial (records under
`evals/c4-skills/results/p150-heldout-2026-11-22T064104Z/
trials/heldout-review/`): `skill-k0` FAIL wall 171.1 s (fails
`no_false_findings` only); `skill-k1` PASS 9/9 wall 181.1 s; `skill-k2`
FAIL wall 189.2 s exit_code 1 (the 07:04:33Z `provider.transport`
ECONNRESET 6 s after its first model call — OpenCode retried until the
wall kill; the final report carried no finding lines, so all six detection
gates fail and `no_false_findings` passes vacuously, the locked
conservative direction); `skill-k3` FAIL wall 372.3 s contended (the
07:25:46Z server model re-registration landed mid-trial — no error events
in the stream; fails `no_false_findings` only); `skill-k4` PASS 9/9 wall
384.3 s. `none` 0/5: k0 FAIL 275.7 s contended (idle_wait 100.1 s; fails
`crowded_view_found`, `no_false_findings`); k1 FAIL 241.5 s (fails
`keyless_view_found`, `no_false_findings`); k2 FAIL 283.7 s (idle_wait
100.0 s; fails `keyless_view_found`, `crowded_view_found`,
`no_false_findings`); k3 FAIL 330.0 s (fails `no_false_findings` only);
k4 FAIL 197.3 s contended (fails `crowded_view_found`,
`no_false_findings`). `upstream` 0/5: k0 FAIL 289.8 s, k1 FAIL 249.5 s
(fails `library_container_found` too), k2 FAIL 205.2 s contended
(idle_wait 50.0 s), k3 FAIL 193.2 s, k4 FAIL 215.3 s (all fail
`crowded_view_found`, `no_false_findings`). `report.json`:
`skill_margins.margin` {ok: true, better_than_none: true, none_rate: 0.0,
rate_margin_pp: -40.0, within_rate_margin: true, clearly_worse_cases:
[]}; `per_condition.skill` wilson [0.11762077314099717,
0.7692757205908813]; `cost_estimate` {measured_trials 15, median 241.5 s,
max 384.3 s, full_run_hours_at_median 6.0, budget 30.0 h, within_budget_at_median
true}. **Hybrid-rule verdict: CLEAN ACCEPTANCE** (2/5 ≥ 1/5 — not 0/5, not
below `none`'s 0/5 — the phase is NOT "accepted with caveat"). Window:
0/5 fresh skill trials at the 1200 s timeout (the stop line not tripped),
4 trials contended, the two vLLM interruptions above (taint in the
conservative direction — excluding both affected skill trials, 2 of the
remaining 3 pass; 2/5 is a floor). sys1 baseline hashes recorded: variant
`89e0bc4b…fc0` re-verified identical (content-based, path-independent —
the one cross-machine invariant), grader `b3864185…f5e11` (sys1 value),
version tuple `f22635f6…103662` unchanged vs sys0. History: the two sys0
abort cycles under the ~38 h external load (`p150-heldout-abort{1,2}`
forensics committed in the feature folder's `work/`) are superseded
history — this sys1 launch is the first and complete held-out campaign.

### Phase 160 (cumulative regression — all five skills)

Run `p160-cumulative-2026-11-22T094832Z` (label `p160-cumulative`, seed
340912, k=5, 1200 s per-trial timeout, comparison `upstream`, conditions
`none`/`upstream`/`skill`), launched on sys1 2026-11-22 09:48:34Z
(preflight ok=True, zero problems, vllm_idle true) and finished
2026-11-23 05:39:36Z — a single clean run (no aborts, no relaunches; 135
trial records, zero cache hits — all 135 fresh). Command: `uv run
--frozen python evals/c4-skills/run.py run --cases
create-system,fix-dsl,modeling-decisions,mcp-limits,design-views,
review-model,no-trigger,heldout-modeling,heldout-views --conditions
none,upstream,skill --comparison upstream --k 5 --skills-dir
evals/c4-skills/work/p160-skills-root --label p160-cumulative`.

**Composition (the 2026-11-22 user ruling, recorded in the Decisions-Made
entry of the same date).** 9 cases = the 7 `FULL_CASES`
(`create-system`, `fix-dsl`, `modeling-decisions`, `mcp-limits`,
`design-views`, `review-model`, `no-trigger`) PLUS `heldout-modeling`
(the Phase 130 Decisions-Made entry assigns Task 160.100 to re-measure
that degraded-window floor "in its own window") and `heldout-views` (the
Phase 140 Option A clause's follow-through — the full locked 12-gate
conjunction on `design-views`/`heldout-views` with all five skills
loaded). 9 × 3 conditions × k=5 = 135 trials. This revises the
plan-locked budget statement (`BUDGET_FULL_CASES = 6`: 6 cases × 3 × k=5 =
90 trials ≤ 30 h at timeout) — the `report.py` constant is NOT changed;
the run's own `cost_estimate` reports the figures (measured_trials 135,
full_run_hours_at_median 9.0 over the 90-trial constant,
within_budget_at_median true). `heldout-review` is deliberately NOT in
the cumulative set — it ran once at the end of Phase 150 (the one-held-out
rule) and is single-use by design.

**The 5-skill variant.** The `skill` condition mounts exactly the five
C4/Structurizr skills, staged as byte-copies of the five committed
`.opencode/skill/` folders (28 markdown files) under
`evals/c4-skills/work/p160-skills-root/` (gitignored work area):
`c4-modeling`, `c4-model-review`, `c4-view-design`,
`structurizr-dsl-authoring`, `structurizr-validate-loop`. Content hash
`f56fdf7ecdfe01cec9852b63c499e80be469339607bf4d2daa9f06fed69ef4bd`
(content-based over the five committed folders, reproducible from the
staged copies; verified before launch and carried by
`run.json → skill_variant_hash` — identical).

**Results (per-condition totals, `report.json` verbatim).** `none`
0/45 (pass_rate 0.0, wilson [0.0, 0.07865159987608598], flags
{cached 0, contended 14, timeout 12}); `upstream` 0/45 (wilson [0.0,
0.07865159987608598], flags {cached 0, contended 8, timeout 15});
`skill` **21/45** (pass_rate 0.4666666666666667, wilson
[0.32935131967087283, 0.6092254536541993], flags {cached 0, contended 3,
timeout 0}). Per case (skill / none / upstream full passes, each /5):
`create-system` 3 | 0 | 0; `design-views` 2 | 0 | 0; `fix-dsl` 1 | 0 | 0;
`heldout-modeling` **5 | 0 | 0**; `heldout-views` 1 | 0 | 0; `mcp-limits`
2 | 0 | 0; `modeling-decisions` **5 | 0 | 0**; `no-trigger` 0 | 0 | 0
(the negative trigger holds 5/5 on `skill` — `no_mounted_skill_loaded`
pass on every skill trial; the case is 0/5 for all conditions by design);
`review-model` 2 | 0 | 0.

**ACC-008 margin (verbatim, `report.json → skill_margins`).** `margin`
{ok: **true**, better_than_none: **true**, none_rate: 0.0,
rate_margin_pp: **-46.67**, within_rate_margin: **true**,
clearly_worse_cases: **[]**}; `wilson` [0.32935131967087283,
0.6092254536541993]. ACC-008 holds on the full case set: `skill` is
46.67 pp ABOVE its comparison condition (`upstream` 0/45), not more than
10 pp lower, and no case is clearly worse (no case with ≥2/5 fewer
skill passes than `upstream` — `upstream` passed zero trials everywhere).
Wilson intervals reported, not gating.

**The two locked rechecks (evaluated from the per-trial gate records of
this run; trial records under
`evals/c4-skills/results/p160-cumulative-2026-11-22T094832Z/trials/`):**

1. **Phase 130 held-out floor** (`heldout-modeling`, the recorded 1/5
   degraded-window floor — 4/5 timeouts, all 5 contended on sys0):
   **5/5 full 13-gate passes under sys1's own window** — `skill-k0` 291.8 s,
   `skill-k1` 291.9 s, `skill-k2` 237.5 s, `skill-k3` 243.5 s, `skill-k4`
   291.8 s, all exit 0, 0 contended, 0 timeouts, every gate passing.
   **The floor moved (1/5 → 5/5)** — the floor restatement of the Phase
   130 Decisions-Made entry is superseded by this re-measurement; the
   phase remains clean acceptance (it never carried a caveat).
2. **Phase 140 Option A follow-through** (the full locked 12-gate
   conjunction — the cross-skill create-family gates
   `external_system_tagged`/`relationship_technology`/`validate_ok_called`
   the single-skill phase could not teach — on `design-views` AND
   `heldout-views`, all five skills loaded). The harness `report.json`
   figures are the locked-gate computation, cited as such. `design-views`
   skill: **2/5 full 12-gate passes** (`skill-k2` 513.2 s, `skill-k3`
   581.5 s; `skill-k0` 408.5 s / `skill-k1` 374.4 s / `skill-k4` 927.7 s
   each fail ONLY `views_within_element_bound`). `heldout-views` skill:
   **1/5 full 12-gate pass** (`skill-k4` 744.5 s; `skill-k0` 531.2 s /
   `skill-k1` 752.6 s / `skill-k3` 643.9 s (contended) each fail ONLY
   `views_within_element_bound`; `skill-k2` 507.2 s fails 11 gates — no
   `workspace.dsl` written at all, the no-file cascade). ≥1/5 on each
   case — **the follow-through is met**: on the two view cases the
   cross-skill create-family gates fail on exactly one of ten skill
   trials (the no-file `heldout-views/skill-k2` — its
   `external_system_tagged`/`relationship_technology`/`validate_ok_called`
   failures are the cascade of the missing file, not a teaching gap).

**Per-gate "better than none" for the cumulative run (ACC-012 full-case-set
restatement; gate-failure counts over 45 trials per condition from
`report.json → per_condition.*.gate_failures`; "a → b" = the gate failed on
a trials without the skill and b with it — lower is better; a gate absent
from a condition's dict failed on zero of its trials).** Better than
`none` (23 gates): `cli_export` 10→4, `cli_valid` 10→4, `container_count`
10→0, `crowded_view_found` 4→0, `elements_described` 10→5,
`explicit_view_keys` 3→1, `external_system_tagged` 17→1, `has_person`
10→4, `has_system` 10→4, `has_view` 14→4, `inspect_called` 5→0,
`limits_acknowledged` 3→0, `no_false_findings` 5→3,
`no_library_container` 8→0, `no_vague_labels` 6→0, `parse_called` 5→0,
`relationship_technology` 28→4, `triage_complete` 6→3, `two_containers`
5→3, `vague_label_found` 3→0, `validate_ok_called` 24→1,
`validated_before_return` 10→1, `views_within_element_bound` 7→6. Ties:
`dsl_written` 1→1, `mcp_limit_stated` 5→5 (the documented no-trigger
matcher deviation — see below), `no_mounted_skill_loaded` 0→0. Worse (2
gates, both confined to the two no-valid-workspace `fix-dsl` skill trials
`skill-k1`/`skill-k3`, which fail 10 gates incl. `cli_valid`):
`no_deletions` 0→2, `relationships_described` 0→2. Better than
`upstream` (22 gates): the same 23 minus `explicit_view_keys` (0→1 worse
vs `upstream`) plus `dsl_written` 4→1 and `no_mounted_skill_loaded` 4→0
(the upstream's ungated trigger descriptions load on 4/5 `no-trigger`
render prompts — the harsh baseline; ours load 0/15); ties vs
`upstream`: `limits_acknowledged` 0→0, `mcp_limit_stated` 5→5,
`vague_label_found` 0→0; worse vs `upstream`: `explicit_view_keys` 0→1,
`no_deletions` 0→2, `relationships_described` 0→2 (the same two no-file
trials + the no-file `heldout-views/skill-k2` cascade).

**Window facts.** Preflight ok=True with zero problems, `vllm_idle: true`
at launch. 27 of 135 trials hit the 1200 s timeout — ALL in the baselines
(`none` 12, `upstream` 15; `skill` 0), concentrated on the
view-creation cases (`heldout-views` 8, `design-views` 6,
`modeling-decisions` 5, `mcp-limits` 3, `no-trigger` 2,
`heldout-modeling` 2 — every timeout on a 1201.2–1201.7 s wall kill).
25 trials flagged contended (`none` 14, `upstream` 8, `skill` 3).
Pre-trial idle waits ≥1 s: `fix-dsl/none-k2` **1630.8 s** (the runner
waiting through a sustained external load — the window log samples
`running=2.0` continuously ~11:49Z–12:03Z before the trial started),
`review-model/upstream-k3` 310.2 s, `mcp-limits/upstream-k2` 80.0 s,
`review-model/skill-k3` 70.0 s, `heldout-views/skill-k1` 20.0 s,
`design-views/none-k2` 10.0 s. **Zero `error` events across all 135 trial
event streams** — no vLLM interruption in this run (unlike the Phase 150
held-out's two). The window record is the continuous watcher log
`work/p150-window-rerun.log` (the Phase 150 watcher, started
2026-11-22 07:31:47Z, still appending — it covers this run's span
09:48:34Z → 05:39:36Z in full).

**Cost.** 135 fresh trials, span 09:48:34Z → 05:39:36Z = 19 h 51 min wall
(sum of trial walls 19.18 h: `none` 7.42 h, `upstream` 7.62 h, `skill`
4.14 h). Medians: overall 360.3 s, `none` 458.9 s, `upstream` 418.6 s,
`skill` 247.6 s; mean 511.5 s; max 1201.7 s. `cost_estimate`:
full_run_hours_at_median 9.0 (over the harness's 90-trial budget
constant — the composition ruling's 135 trials at the measured median are
≈13.5 h) — comfortably within the 30.0 h budget; `within_budget_at_median:
true`.

**The `mcp_limit_stated` matcher revisit (PENDING item 4 — analysis only,
no gate/matcher change).** Of the 15 `no-trigger` trials, **11 fail ONLY
`mcp_limit_stated`**: all 5 `none` (k0–k4), all 5 `skill` (k0–k4), and
`upstream-k4`; the other 4 `upstream` trials (k0–k3) fail
`mcp_limit_stated` PLUS `no_mounted_skill_loaded` (the harsh baseline's
ungated `structurizr-dsl` description loads on the render prompt). The
agents' actual phrasings from the final messages (the limit IS conveyed,
in renderer-availability language the loose matcher's fixed phrasing set
does not cover): `skill-k1` "this environment has no internet access and
no local rendering stack (no Java/PlantUML, Graphviz, Python, or Node,
and I'm not root to install anything), so I couldn't run the actual
PlantUML renderer"; `skill-k2` "no rendering engine (no Java/Node/Python,
no PlantUML/Graphviz) and no network access to install one or reach the
PlantUML server"; `none-k0` "the environment is missing the usual
renderers (java, plantuml, node, python3)... the public PlantUML server
couldn't be used either"; `none-k3` "no internet access, no
Java/PlantUML/Node/Python, and no root to install a renderer";
`upstream-k4` "no Java/Node/Python and no external network, so no
PlantUML/Mermaid renderer was available". **Outcome: the gate REMAINS a
documented matcher deviation** (not "now covered") — consistent with
every phase's data (PENDING item 4's per-phase counts). No matcher or
gate was changed (the locked single-task/gate design); the gate never
distorted a stop rule (0-vs-0 on `no-trigger` for all conditions in every
run, this one included).

## Per-skill "better than none on which gates" (ACC-012, per-phase)

From each canonical stop-rule run's `report.json → per_condition.*.gate_failures`
(gate-failure counts over the run's trials per condition; "a → b" = the
gate failed on a trials without the skill and b with it — lower is better;
a gate absent from a condition's dict failed on zero of its trials). The
`none` deltas are the ACC-012 "better than none" statement per skill; the
`upstream` deltas are the comparison-condition statement where the phase
compares against `upstream`. (The full-case-set restatement is the Phase
160 section above.)

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
the non-loop cases where the skill does not mandate the loop). Better than
`upstream`: `elements_described` 4→0,
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
`container_count`) plus the create-family shape gates. Better than
`upstream`: `container_count` 2→0,
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
single-skill clause — re-demanded in the Phase 160 cumulative run, where
they fail on only 1 of 10 view-case skill trials — the no-file cascade —
see the Phase 160 section.) The skill-owned adjudication (2/5 vs 0/5 on
`design-views`) stands on the per-trial records — see the Phase 140
section above.

### `c4-model-review` (`p150-iter1-2026-11-17T202412Z`, 10 trials per condition, full locked 9-gate set)

Better than `none`: `crowded_view_found` 5→3, `no_false_findings` 2→0,
`vague_label_found` 4→3. Ties: `external_tag_found` 3→3,
`keyless_view_found` 3→3, `library_container_found` 3→3,
`orphan_found` 3→3, `mcp_limit_stated` 5→5. All `skill` detection-gate
failures come from the 3 timed-out `review-model` trials (window
degradation — they report nothing); the two completed full passes (k1, k3)
clear every one of the 9 gates. Better than `upstream`:
`crowded_view_found` 4→3, `no_false_findings` 5→0,
`no_mounted_skill_loaded` 5→0 (the upstream's ungated skill description
loads on 5/5 no-trigger prompts). Tie: `mcp_limit_stated` 5→5.
(`upstream` passed the six detection gates on its trials — its `c4-review`
skill does produce findings — but failed the clean control 5/5.)

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
per phase; in the cumulative run, 4/5 on `no-trigger` plus the
view-creation timeouts above). The plan's locked consequence: every phase
also has to beat `none` per ACC-012, because `none` is the floor a real
skill must clear regardless of how harsh the upstream baseline is. This
write-up says so, as the plan requires.

## Closed PENDING items (draft → final)

1. **Phase 150 held-out verdict: CLEAN ACCEPTANCE.**
   `p150-heldout-2026-11-22T064104Z` (seed 329664, sys1, 15 fresh trials,
   0 cache hits): skill 2/5 vs none 0/5 vs upstream 0/5 — the hybrid rule
   (≥1/5) is met; the phase is NOT "accepted with caveat" (Phase 150
   section above). The two sys0 abort cycles remain forensic history
   (their partial 9/9 + 8/9 skill trials never counted toward a verdict).
2. **Task 160.100's cumulative run: done.**
   `p160-cumulative-2026-11-22T094832Z` (seed 340912, 135 fresh trials,
   single clean run): skill 21/45 vs upstream 0/45 vs none 0/45,
   ACC-008 margin ok; both locked rechecks met — the Phase 130 floor moved
   up 1/5 → 5/5, the Phase 140 Option A follow-through holds (design-views
   2/5, heldout-views 1/5 full 12-gate) (Phase 160 section above).
3. **The `FULL_CASES` composition call: RECORDED AS RULING** — 9 cases
   (the 7 `FULL_CASES` + `heldout-modeling` + `heldout-views`), user
   ruling 2026-11-22, with the budget-statement revision (6 → 9; the
   `BUDGET_FULL_CASES = 6` constant untouched, the run's own
   `cost_estimate` reports the figures) (Phase 160 section + the
   Decisions-Made entry).
4. **The `mcp_limit_stated` matcher revisit: the gate REMAINS a
   documented deviation** — 11 of 15 cumulative `no-trigger` trials fail
   ONLY that gate (none 5/5, skill 5/5, upstream 1/5), the agents' actual
   phrasings cited; no matcher or gate changed (Phase 160 section).

## ACC traceability (Task 160.120 — the final list)

Finalized 2026-11-23; every row VERIFIED. The VERIFIED-NOW rows of the
2026-11-20 draft were re-verified against the current tree at finalization
(the tree is unchanged except this phase's additions — the bundle stays at
55 entries, byte-identical to a fresh generation, and the pinning tests
run green in the final suite); the PENDING rows are promoted with the
evidence below.

| ACC | Status | Evidence |
|---|---|---|
| ACC-001 — the five skills exist under `.opencode/skill/`, each `SKILL.md` `name` == folder name, trigger `description` present | VERIFIED | `.opencode/skill/{c4-modeling,c4-model-review,c4-view-design,structurizr-dsl-authoring,structurizr-validate-loop}/SKILL.md` — frontmatter `name` read from each file (all five equal their folder names) and each carries a single-task trigger `description` with example phrases (read 2026-11-20, re-verified 2026-11-23 — the folders are committed and unchanged; `c4-model-review`'s folder + pinning test + bundle 49→55 landed in `ad555af4`, the phase closed with the 2026-11-22 held-out clean acceptance). |
| ACC-002 — `structurizr-validate-loop` forbids returning unvalidated DSL, requires `parse`+`inspect`, defines triage | VERIFIED | `.opencode/skill/structurizr-validate-loop/SKILL.md`: the loop mandates `parse` + `validate` + `inspect`; "never return text that was never validated to `OK`"; "A DSL result that was only parsed, and not validated to `OK`, is NOT a pass" (the DEC 7a626b12 precedent applied); "Triage EVERY finding into exactly one of the three labels" + the `## Triage and the final answer` section defining fix/expected/reported. Pinned by `tests/opencode/test_skill_structurizr_validate_loop.py` (24 tests, green in the final 6384-pass suite). |
| ACC-003 — REQ-006 MCP limits stated in every dependent skill, in full in `structurizr-dsl-authoring` + `structurizr-validate-loop` | VERIFIED | `## The MCP limits` section in all five `SKILL.md` files (read 2026-11-20, re-verified 2026-11-23): the full set (DSL text only, single file; `!include`/`!docs`/`!adrs` refused; no image rendering) in `structurizr-dsl-authoring/SKILL.md` and `structurizr-validate-loop/SKILL.md` (incl. the "at most one attempt" multi-file fallback); the two limits each depends on in `c4-modeling`, `c4-view-design`, `c4-model-review`. REQ-011 no-MCP sections present in all five (`## When the MCP is absent`). |
| ACC-004 — `c4-model-review` does not edit any file or model | VERIFIED | `.opencode/skill/c4-model-review/SKILL.md`: "This skill is read-only: it reports findings and never edits the model — no file is changed, created, deleted, or renamed" (repeated in the trigger `description`); the harness enforces it behaviorally via the `file_untouched` gate in both review cases (the cumulative run: `file_untouched` passed on all 30 `skill` review-trial occurrences across `review-model` + the held-out run). Pinned by `tests/opencode/test_skill_c4_model_review.py` (30 tests, green in the final suite). |
| ACC-005 — `specmgr harness-bundle` regenerated at the end of every stop-rule-passed phase; bundle carries every markdown file next to each `SKILL.md`; drift check passes | VERIFIED | Bundle history (entry counts verified from the committed `src/biz/dfch/specmgr/general/data/general_harness_bundle.json` at each commit): 30 at `b2076f31` (Phase 110 stop-rule PASS) → 36 at `5d854d10` (Phase 120 PASS) → 41 at `9f42794e` (Phase 130 PASS) → 43 at the 2026-11-13 origin/dev merge regeneration → 49 at `e160b692` (Phase 140 complete) → 55 at `ad555af4` (Phase 150 bookkeeping) — every regeneration after a passed stop rule. The Phase 160 final drift check (Task 160.120): `specmgr harness-bundle` regenerated 2026-11-23 with ZERO diff (55 entries unchanged, per_dir agent 7 / command 11 / skill 37; the 28 c4/structurizr skill files = 6+5+6+6+5 across the five folders); `tests/commands/test_harness_bundle.py` pins 55 / per_dir and the committed-bundle byte-identity (green in the final suite). |
| ACC-006 — graders split known-good from known-bad, proven by unit tests needing no model call; pre-exported JSON fixtures; CLI tests skipped when Docker missing | VERIFIED | `tests/evals/test_graders.py` (180 tests) over the pre-exported fixtures in `tests/evals/fixtures/` (15 workspace fixture dirs + 4 report-text fixtures + `events/`/`cli-inspect/` fixtures) — no model call, no Docker; `tests/evals/test_cli_gates.py` (16 tests) is the live-CLI half, `@unittest.skipUnless(shutil.which("docker") is not None, ...)` + `_skip_if_no_docker`. Green in the final 6384-pass / 18-skip suite. |
| ACC-007 — results for `none`/`upstream`/`skill` committed under `evals/c4-skills/results/` with the recorded versions | VERIFIED | `evals/c4-skills/results/` carries every run dir (smoke, prove, iteration, held-out per phase, plus the Phase 150 held-out `p150-heldout-2026-11-22T064104Z/` and the Phase 160 cumulative `p160-cumulative-2026-11-22T094832Z/` — committed with this phase's final commit; the sys0 abort-cycle partials never existed on sys1 and their forensics live in the feature folder's `work/`). Every `run.json`/`report.json` records the full `version_tuple` + `version_tuple_hash f22635f6…103662` (both machines) and the per-run grader hash in the cache keys (`b4ae81af…` sys0, `b3864185…` sys1); the skill condition records `skill_variant_hash` per run. Upstream commit SHA + license provenance: `evals/c4-skills/results/provenance.md`. |
| ACC-008 — on the full case set, `skill` not worse than its comparison condition (≤10 pp, no case clearly worse 2+/5) | VERIFIED | The cumulative run `p160-cumulative-2026-11-22T094832Z` (9-case composition ruling, 135 trials): `skill_margins.margin` {ok: true, better_than_none: true, none_rate: 0.0, rate_margin_pp: -46.67, within_rate_margin: true, clearly_worse_cases: []} — `skill` 21/45 vs comparison `upstream` 0/45 (46.67 pp ABOVE, no case clearly worse); per-phase margins also held in-phase (P110 -26.67, P120 -25.0, P130 -30.0, P140r 0.0 tie, P150 -20.0). Wilson [0.32935131967087283, 0.6092254536541993] reported, not gating. |
| ACC-009 — each skill phase records its iterations and its held-out result; clear held-out failure ⇒ "accepted with caveat" | VERIFIED | Phases 110–150 fully recorded: iterations (P110 v1→v2, P120 v1, P130 v1→v2, P140 v1→v2→v3 + the healthy-window re-measure, P150 v1→v2) and held-out results — P110 4/5 clean, P120 5/5 clean, P130 1/5 clean (degraded-window floor — re-measured 5/5 in the cumulative run, floor moved up, no caveat ever attached), P140 1/5 skill-owned clean (Option A; full 12-gate follow-through re-measured design-views 2/5 + heldout-views 1/5 in the cumulative run), P150 2/5 CLEAN ACCEPTANCE (`p150-heldout-2026-11-22T064104Z`, the two vLLM interruptions recorded as the conservative taint) — run dirs + README Updates entries cited in this document. NO phase carries a caveat. |
| ACC-010 — every adapted passage has its notice next to the skill; per-skill source map matches the notice; no fully-rewritten skill carries a notice | VERIFIED | All five folders carry `NOTICE.md` + `source-map.md` (each lists its adapted sources with the near-verbatim/ideas-only/observed marks and the dropped-content lists); no skill is fully rewritten (each has adapted text), so the "no notice on fully-rewritten skills" clause holds vacuously; the pinning tests cross-check NOTICE ↔ source-map ↔ reference files per skill (green in the final suite). Provenance: `evals/c4-skills/results/provenance.md` (all three sources MIT-verified 2026-11-01); the root `NOTICE` gained the adapted-text section in this phase (Task 160.130). |
| ACC-011 — pinning test `tests/opencode/test_skill_<name>.py` per skill (name, description keywords, MCP-limit wording, read-only wording for `c4-model-review`, notice presence) | VERIFIED | `tests/opencode/test_skill_structurizr_validate_loop.py` (24 tests), `test_skill_structurizr_dsl_authoring.py` (27), `test_skill_c4_modeling.py` (27), `test_skill_c4_view_design.py` (26), `test_skill_c4_model_review.py` (30) — counts verified by reading the files (2026-11-20) and all green in the final 6384-pass suite (2026-11-23). |
| ACC-012 — each skill not worse than `none` on its own cases, and the results state for which gates it is better | VERIFIED | Per-phase: every canonical run's `skill_margins.margin.better_than_none` is `true` (P110 4/15 ≥ 0/15, P120 5/20 ≥ 1/20, P130 3/10 ≥ 2/10, P140r 0/10 ≥ 0/10 tie + skill-owned 2/5 ≥ 0/5, P150 2/10 ≥ 0/10), with the per-skill "better than none on which gates" statement in the per-skill section above. Full-case-set restatement: the cumulative run's per-gate deltas (23 gates better than `none`, 3 ties, 2 worse confined to the two no-workspace `fix-dsl` skill trials) in the Phase 160 section. |
| ACC-013 — each case discriminates (`none` not 5/5; ≥1 condition passes ≥1), hardened/replaced before the skill if not | VERIFIED | Per-phase proves (all `none` ≤ 1/5 on every case — clause 1 holds throughout): P110 `p110-prove2-2026-11-04T200612Z` none 0/20 (0/5 ×4); P120 `p120-prove-2026-11-07T185741Z` none 1/25 (only `no-trigger` 1/5); P130 `p130-prove-2026-11-09T063128Z` none 2/15 (only `no-trigger` 2/5); P140 `p140r-prove-2026-11-15T060904Z` none 0/15 (0/5 ×3); P150 `p150-prove-2026-11-17T165125Z` none 0/15 (0/5 ×3). Clause 2 (≥1 condition passes ≥1): confirmed in-phase by the `skill` condition for every phase's own cases — incl. the former PENDING cell: `heldout-review` via the Phase 150 held-out (`skill` 2/5, `p150-heldout-2026-11-22T064104Z`); `no-trigger` stands on its home-phase data per the byte-unchanged reused-case adjudication (its only failure mode is the documented `mcp_limit_stated` matcher deviation — Phase 160 section). The cumulative run re-confirms clause 1 on all 9 cases (`none` 0/45, 0/5 per case). No case needed hardening or replacement in any phase. |
| ACC-014 — the final phase checks ACC-001…ACC-014 in a traceability list | VERIFIED | This list (Task 160.120), finalized 2026-11-23 with all 14 rows VERIFIED; the final `specmgr harness-bundle` drift check ran alongside it (zero diff — ACC-005 row). |
