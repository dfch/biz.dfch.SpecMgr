# Phase 150 held-out — resume prompt (self-contained subagent brief)

Launch this as ONE delegation at the moment the shared-vLLM window is free.
Everything needed is in this file — do not re-derive, re-plan, or "improve"
the locked procedure; execute it. Where this prompt states a locked value
(hash, case set, gate set, rule), that value is final: a mismatch is a
STOP-and-report, never a correction.

## 1. Context (verified state at draft time, 2026-11-20)

**Repo.** Worktree
`/home/user/src/biz.dfch.SpecMgr.worktree/feat-250-c4-structurizr-skills`,
branch `feat-250-c4-structurizr-skills`. At draft time HEAD is `d0fd1434`
(the 2026-11-20 origin/dev merge). At launch, record
`git log --oneline -1` in your report — the orchestrator may have advanced
the branch; the measurement invariants below pin the harness regardless of
HEAD, and if any invariant re-verification in step 3 fails, STOP and report
before anything else.

**Phase 150 (skill `c4-model-review`) state.** Tasks 150.100–150.130 are
complete and committed; the stop rule **PASSED at iteration 1 of 3** on
2026-11-17 (the FULL locked 9-gate set — no Option A narrowing; the Phase
140 Option A clause revision was scoped to that single-skill phase and does
not apply here). Task 150.150's bookkeeping (the pinning test
`tests/opencode/test_skill_c4_model_review.py` (30 tests), the harness
bundle regeneration 49 → 55, the `tests/commands/test_harness_bundle.py`
count) is DONE and committed (`ad555af4`). Only **Task 150.140 (the
held-out campaign) and its record are outstanding** — that is this
prompt's entire job.

**Stop-rule record (the evidence base).** Canonical runs (committed under
`evals/c4-skills/results/`):
- `p150-prove-2026-11-17T165125Z` (seed 916537; cases
  `review-model`,`no-trigger`,`heldout-review`; conditions
  `none`,`upstream`): `none` 0/15 AND `upstream` 0/15 — ACC-013 clause 1
  holds on all three cases.
- `p150-iter1-2026-11-17T202412Z` (seed 947052; cases
  `review-model`,`no-trigger`; conditions `none`,`upstream`,`skill`):
  `skill` 2/10 vs `none` 0/10 vs `upstream` 0/10 — two full 9/9 passes on
  `review-model` (k1, k3; 1067 s / 1011 s), the other three `review-model`
  skill trials 1200 s timeouts (window degradation: 8 of 10 fresh skill
  trials at the timeout, 5 of 10 contended, an external client held the
  shared 2-slot vLLM from ~20:24Z onward); `no-trigger` 0/5 for all three
  conditions with the negative trigger holding 5/5 on skill;
  `skill_margins.margin` = {ok: true, better_than_none: true,
  rate_margin_pp: -20.0, within_rate_margin: true, clearly_worse_cases:
  []}.

**The two abort cycles (bounded-wait policy, exhausted).** The held-out
campaign was launched twice and aborted twice by the runner's locked 1-h
busy-server idle-wait, under a sustained external load of ~38 h on the
shared vLLM:
- Cycle 1: run `p150-heldout-2026-11-18T154347Z` (seed 16627) — 5 cache
  hits + 2 fresh skill trials resolved, then aborted at
  "vLLM was still busy after 3601s of waiting". Forensics: `skill-k2`
  PASS 9/9 at 678 s (contended), `skill-k4` FAIL at the 1200 s timeout.
- Cycle 2: run `p150-heldout-2026-11-19T070020Z` (seed 71620) — 5 cache
  hits, then `skill-k0` completed at 598.6 s (contended) with **8/9 gates —
  the only failure `no_false_findings`** (a finding line names the clean,
  correctly `External`-tagged element `Loyalty Points Feed`), then aborted
  at "vLLM was still busy after 3604s of waiting". No `run.json`, no
  `report.json` — a partial.
Forensics of both partials is committed under
`.specmgr/feat/feat-250-c4-structurizr-skills/work/p150-heldout-abort1-2026-11-18T154347Z/`
and `work/p150-heldout-abort2-2026-11-19T070020Z/` (trial JSONs, event
streams, preflights, logs) — the cycle-2 stdout log is
`work/p150-heldout-attempt2.log`. **The aborted trials are forensic
history only: they never count toward a held-out verdict** (a `skill`
trial is never cacheable, and a verdict requires one complete campaign
run). The full state is recorded in
`.specmgr/feat/feat-250-c4-structurizr-skills/phase-150-heldout-status.md`.

**Invariants (re-verify in step 3; any mismatch = STOP and report).**
- Frozen skill variant **v2** =
  `89e0bc4bb4867b8885a3e393eaf1c76d3811dd39bd17702a533788f0b7620fc0`
  (`.opencode/skill/c4-model-review/`, 6 markdown files).
- Grader hash =
  `b4ae81afcc4ae8e5c0484e480a6dc18ea1c9bf0b75e458c5a3c5d90a4ee8f81b`.
- Version tuple hash =
  `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`.
- The expected 10 held-out cache hits:
  `evals/c4-skills/cache/heldout-review.none.json` and
  `evals/c4-skills/cache/heldout-review.upstream.json` (5 trials each)
  carry key blocks whose `grader_hash` and `version_tuple_hash` are exactly
  the two values above (verified at draft time).

**Working-file rule.** All session artifacts live in the feature folder
FEAT = `.specmgr/feat/feat-250-c4-structurizr-skills/` (its `work/`
subfolder for logs) — never /tmp (the host reaps /tmp on an age schedule;
this bit us twice already).

## 2. Trigger

Launch ONLY when the background monitor has declared the window free: the
monitor (started `2026-11-20T12:50:51Z`, 5-minute samples, "stops after 3
consecutive idle samples or 36 h") appends to `FEAT/work/p150-window-wait.log`
and writes a **`WINDOW-CLEARED`** line when 3 consecutive samples show
`running=0 waiting=0`. That line is the trigger evidence — read the log's
first line (the start stamp) and the `WINDOW-CLEARED` line verbatim; you
cite both in the final README entry (the monitor-log span). If the monitor
hit its 36 h limit without clearing, the orchestrator re-triggers — do not
launch on your own window judgment.

## 3. Procedure

Work from the worktree root. `FEAT` =
`.specmgr/feat/feat-250-c4-structurizr-skills`.

**3.1 Pre-launch checks.**
- `git log --oneline -1` (record in the report).
- `git status --short` — expect the untracked partial
  `evals/c4-skills/results/p150-heldout-2026-11-19T070020Z/` plus the
  pre-existing FEAT draft files; no other surprise.
- `docker ps --filter name=c4eval` — must be empty; sweep any leftover
  `c4eval*` container/network first (the runner refuses a stale sidecar).
- Confirm `FEAT/work/p150-window-wait.log` carries the `WINDOW-CLEARED`
  line (the trigger) and read its span (step 2).

**3.2 Sweep the untracked partial (locked policy: one results dir per
attempt; the forensics are already committed in
`FEAT/work/p150-heldout-abort2-2026-11-19T070020Z/`).**
- Verify the sweep is safe: `evals/c4-skills/results/p150-heldout-2026-11-19T070020Z/`
  has NO `run.json` AND `FEAT/work/p150-heldout-abort2-2026-11-19T070020Z/`
  is non-empty (contains the trial JSONs + events). If either check fails,
  STOP and report — do not sweep.
- `rm -rf evals/c4-skills/results/p150-heldout-2026-11-19T070020Z`

**3.3 Re-verify the invariants (any mismatch = STOP and report).**
```bash
cd evals/c4-skills && uv run --frozen python - <<'EOF'
from pathlib import Path
from c4_skills import pins, runner

src = runner.load_skill_source(Path("../../.opencode/skill/c4-model-review"))
print("variant:", pins.skill_variant_hash(src.files))
print("grader: ", pins.source_hash([str(p) for p in runner.grader_source_paths()]))
print("vtuple: ", pins.version_tuple_hash())
EOF
```
Expect exactly: variant `89e0bc4b…fc0`, grader `b4ae81af…f81b`, vtuple
`f22635f6…103662`. (The grader hash folds in absolute paths — it is only
reproducible from this worktree, which is the one the campaign runs in.)

**3.4 Preflight + probe.**
- `uv run --frozen python evals/c4-skills/run.py preflight` — expect
  `ok=True` with NO pin violation; copy the recorded JSON to
  `FEAT/work/preflight-heldout-rerun.json` (the going-forward rule). A
  preflight that records `vllm_idle: false` is NOT a stop condition by
  itself (the runner idle-waits per trial) — note it and proceed.
- Probe: `uv run --frozen python evals/c4-skills/run.py probe` (one trivial
  trial through the full container/sidecar/vLLM/MCP chain; expect exit 0 /
  `PROBE-OK`). The window just cleared and the chain was last verified
  2026-11-18 under this exact version tuple, but a fresh probe is cheap
  insurance against a host-side change over the wait.

**3.5 Launch the campaign (the exact command; stdout to
`FEAT/work/p150-heldout-rerun.log`).**
```bash
setsid nohup uv run --frozen python evals/c4-skills/run.py run --cases heldout-review --conditions none,upstream,skill --comparison upstream --k 5 --skills-dir .opencode/skill/c4-model-review --label p150-heldout > .specmgr/feat/feat-250-c4-structurizr-skills/work/p150-heldout-rerun.log 2>&1 &
```
(Identical to the 2026-11-18/19 launches; `--seed` omitted = fresh random
seed, recorded in `run.json` — the seed only shuffles trial order,
sampling is `temperature=0.0`, so it changes nothing measurable. The 10
`none`/`upstream` trials are cache hits under the step-3.3 pins; the 5
`skill` trials are always fresh. Plan order and expected shape per
`phase-150-heldout-status.md`.)
- Optional (recommended, window evidence of record): start a 60 s window
  watcher appending to `FEAT/work/p150-window-rerun.log`:
```bash
( while true; do echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $(curl -s --max-time 10 http://127.0.0.1:8081/metrics | grep -E '^vllm:num_requests_(running|waiting)\{' | sed -E 's/.*num_requests_(running|waiting)\{[^}]*\} ([0-9.]+)/\1=\2 ' | tr -d '\n')" >> .specmgr/feat/feat-250-c4-structurizr-skills/work/p150-window-rerun.log; sleep 60; done ) &
```
  Kill it when the run finishes. If you skip it, the per-trial
  `idle_wait_s`/`timeout`/`contended` flags in the run dir are the
  surviving window evidence (the established precedent).

**3.6 Monitor: poll every 300 s** (tail
`FEAT/work/p150-heldout-rerun.log` + count trial files under the new run
dir `evals/c4-skills/results/p150-heldout-<timestamp>Z/trials/`). Until
`run.json` + `report.json` appear, expect: 10 `cache_reason: hit` trials
resolving near-instantly and up to 5 fresh skill trials at ≤1200 s each
(≈ up to 100 min of model wall in a healthy window, plus any
idle-waits).

**3.7 Stop lines (locked; finish the run, then act).**
- **≥3 of the 5 fresh skill trials at the 1200 s timeout** ⇒ the sample is
  window-tainted. Do NOT evaluate under the hybrid rule, do NOT relaunch
  — STOP and report (the orchestrator decides; the Phase 150 record will
  carry the taint note like the Phase 130 floor).
- **The runner aborts on the 1-h busy-wait** (log line "vLLM was still
  busy after 360…s of waiting") ⇒ sweep the new partial results dir
  (after copying its forensics into
  `FEAT/work/p150-heldout-abort3-<run-id>/`, the established pattern —
  trial JSONs + events + preflight + the rerun log) and **relaunch the
  identical command once more (max 1 more cycle)**. If that relaunch also
  aborts, STOP and report: held-out remains PENDING, bookkeeping complete
  — no third loop.

## 4. Verification checklist (on the completed run dir)

All of these must hold; ANY failure = STOP and report before the README
record (no verdict on a broken run).
1. `run.json` + `report.json` present; `run.json → label` = `p150-heldout`,
   `k` = 5, `cases` = `["heldout-review"]`, `conditions` =
   `["none", "upstream", "skill"]`, `comparison` = `upstream`.
2. `run.json → skill_variant_hash` = `89e0bc4bb4867b8885a3e393eaf1c76d3811dd39bd17702a533788f0b7620fc0`;
   `run.json → version_tuple_hash` =
   `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`.
   (The grader hash is not a `run.json` field — it was fixed in step 3.3
   and is PROVEN by check 3: a cache hit is a full key match, and the key
   carries the grader hash.)
3. All 10 `none`/`upstream` trial records have `cache_reason: "hit"`.
   **Any fresh baseline trial = the cache key moved = STOP and report**
   (investigate pins before any verdict).
4. The 5 `skill` trial records carry the FULL locked 9-gate set:
   `cli_valid`, `file_untouched`, `vague_label_found`,
   `library_container_found`, `external_tag_found`, `keyless_view_found`,
   `crowded_view_found`, `orphan_found`, `no_false_findings` (no Option A
   narrowing — this phase has none; the gate set is the case's locked
   set).

## 5. Evaluation rules (locked)

- **Hybrid rule** (the plan's stop-rule held-out clause): count the fresh
  skill trials passing ALL 9 gates (`report.json → per_condition.skill`,
  and the per-trial `gates`/`passed` fields):
  - **≥1/5** ⇒ **clean acceptance** — the phase is NOT "accepted with
    caveat".
  - **0/5, or below `none`'s rate** (`none` is 0/5 from the cache —
    re-confirm from `report.json`) ⇒ the phase is **"accepted with
    caveat"** — record it; the caveat is rechecked in Phase 160's
    cumulative run and stated in the results.
- The held-out result can only ADD the caveat record — it never changes
  the stop-rule verdict (PASS at iteration 1) or the frozen variant.
- Window facts of record: the per-trial `timeout`/`contended`/
  `idle_wait_s` flags, the preflight JSON, and the monitor-log span
  (step 2) — plus any watcher log you kept.

## 6. Final README record (via the specmgr MCP tools on
`type="feat"`, `id="feat-250-c4-structurizr-skills"` — read with
`get_feat(id, raw=True, numbered=True)` for coordinates; never hand-edit
frontmatter; never feed numbered output back verbatim)

1. **Task List:** tick `- [ ] Task 150.140` → `- [x] Task 150.140` and
   `- [ ] Task 150.150` → `- [x] Task 150.150` (in place, exact strings).
2. **Current Status:** PREPEND a new leading paragraph above the current
   `**As of 2026-11-18**:` paragraph:
   `**As of 2026-11-20**: Phase 150 (Skill c4-model-review) is COMPLETE — held-out <Held-out run id, seed> landed <date>: skill <X>/5 vs none 0/5 (10 cache hits) — <CLEAN ACCEPTANCE | ACCEPTED WITH CAVEAT (0/5 / below none); caveat rechecked in Phase 160>. Stop rule PASSED at iteration 1 (unchanged: p150-iter1-2026-11-17T202412Z, 2/10 vs 0/10 vs 0/10, margin ok -20.0 pp); bookkeeping (pinning test 30 tests, bundle 49→55) committed in ad555af4. Phase 160 can start.`
   (adapt the `<…>` slots to the actual data; keep it one paragraph, the
   established Current Status shape).
3. **Updates:** PREPEND a dated entry (TRUE UTC from `date -u` at write
   time, the `.000Z` form, header shape
   `#### 2026-11-20 HH:MM:SS.000Z - Phase 150 held-out complete — <verdict>; Phase 150 COMPLETE, Phase 160 can start`)
   directly below the `<!-- Newest entry first … -->` comment, carrying:
   - the campaign data VERBATIM: run id, seed, the 5 skill trials' wall
     times + `timeout`/`contended` flags + per-gate pass/fail (the failing
     gates named per trial, the established per-trial citation style), the
     10 baseline `cache_reason: hit` confirmations, the
     `report.json → per_condition` figures (skill/none/upstream
     pass-rates, `skill_margins.margin`), the hybrid-rule verdict with the
     rule applied to the numbers;
   - the window facts: the preflight (`vllm_idle`, `running`), the
     monitor-log span cited verbatim (`FEAT/work/p150-window-wait.log`
     start line → `WINDOW-CLEARED` line), the watcher-log span if kept,
     the abort-cycle history in one sentence (cycles 1–2 aborted under the
     38 h load; this launch is cycle 3 and complete — or the relaunch
     facts, per 3.7);
   - the bookkeeping recap: 150.140 = this run; 150.150 was already
     committed in `ad555af4` (pinning test `tests/opencode/
     test_skill_c4_model_review.py` 30 tests, bundle 49 → 55, count test
     updated) — re-confirmed idempotent by the step-7 gates;
   - the tree state (your `git status --short`, verified at the end).
4. Do NOT touch "Decisions Made" and do NOT change any other existing
   entry.

## 7. Quality gates (run from the worktree root; fix your own failures,
re-run until green)

- `uv run --frozen ruff format --check`
- `uv run --frozen ruff check`
- `uv run --frozen vulture src/ whitelist.py --min-confidence 60`
- full pytest: `uv run --frozen pytest -n auto --cov=src --cov-report=`
  — expect **6384 passed / 18 skipped / 0 failed** (the post-merge tree
  baseline; this session adds no test files — if your README record
  changed any count, report actuals and the reason).
- `uv run --frozen specmgr lint .specmgr/feat/feat-250-c4-structurizr-skills/README.md`
  — expect `linted=1 failed=0`.
- Bundle/docs idempotency: `uv run --frozen specmgr harness-bundle` then
  `git diff --exit-code src/biz/dfch/specmgr/general/data/general_harness_bundle.json`
  (expect NO diff — the six c4-model-review files are already in the
  committed 55-entry bundle; the `.opencode/` tree is unchanged by this
  session) and `uv run --frozen specmgr docs` then `git diff --exit-code
  docs/` (expect NO diff — no `src/`/`tests/` module or test-file change).

## 8. Final commit (orchestrator's job — you do NOT commit)

Report the exact untracked/modified set from `git status --short`. The
Phase 150 final commit takes: the new run dir
`evals/c4-skills/results/p150-heldout-<timestamp>Z/` (all of it — the
established per-run-dir commit pattern), this README, and the `FEAT/work/`
additions. **Force-add note:** `FEAT/work/p150-window-wait.log` and
`FEAT/work/p150-heldout-rerun.log` (plus `FEAT/work/p150-window-rerun.log`
if the watcher ran) are gitignored `*.log` files — the final commit
force-adds them WITH the record (user ruling; the 2026-11-20 persistence
entry's going-forward rule says logs live in `work/` and are committed
with the phase). Also list any abort-3 forensics dir if 3.7 fired.

## 9. Never

- No commit, no stage, no push (the orchestrator commits the phase after
  verifying your report).
- No Phase 160 work: no cumulative run, no results write-up, no
  AGENTS/CHANGELOG/NOTICE application, no 160.100/160.110/160.120/160.130.
- No locked-value changes: the variant hash, the grader hash,
  `pins.py`, the case definitions, the 9-gate set, k=5, the 1200 s
  timeout, the hybrid rule, the stop lines — all final.
- No modification of committed run dirs, the cache, or the `FEAT/work/`
  forensics of cycles 1–2 (cite, never modify).
- No sweep of anything other than the named partial (3.2) or an abort-3
  partial you created (3.7).
- No task ticks beyond 150.140/150.150; no "Current Status" paragraph
  removals (prepend only); no "Decisions Made" edits.
- If any step's STOP condition fires, STOP and report — do not paper over
  a mismatch, do not relaunch beyond the bounded policy, do not start the
  Phase 160 work "while waiting".

## 10. Report contract (your final message to the orchestrator)

1. Launch-time HEAD + the `git status --short` snapshot.
2. Trigger evidence: the monitor log's start line and `WINDOW-CLEARED`
   line verbatim.
3. The sweep (3.2) + the safety checks that authorized it.
4. Re-verified invariants (3.3): the three hashes + "10 expected cache
   hits still valid".
5. Preflight + probe outcomes (ok, `vllm_idle`/`running`, `PROBE-OK`).
6. The run: id, seed, plan order as executed, per-trial facts for all 15
   trials (wall, `cache_reason`, `timeout`/`contended`/`idle_wait_s`,
   gate summary), the `report.json` figures verbatim.
7. The hybrid-rule verdict (clean / accepted with caveat) + the window
   stop-line status (fresh timeouts n/5).
8. README record: the ticked tasks, the new Current Status paragraph, and
   the new Updates entry HEADER + body verbatim.
9. Quality gates: each command + pass/fail + the actual pytest counts.
10. Tree state: final `git status --short`, the files the final commit
    takes, and the force-add paths.
11. Any deviation from this prompt, with the reason.
