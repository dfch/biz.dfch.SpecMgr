# Phase 150 sys1 handoff (feat-250, written 2026-11-21 at the sys0→sys1 wrap-up)

Boot document for the fresh **sys1** session that finishes
**feat-250-c4-structurizr-skills**: the Phase 150 held-out (the
phase's only outstanding work), its final entry/commit, Phase 160
(cumulative run + results + repo docs), and finalization. Everything
up to the held-out verdict is committed; nothing is re-planned — the
locked procedure is the resume prompt, this file says where you are
and what to run. Verified against the committed tree. UTC-anchored.

## Where we are

- Branch `feat-250-c4-structurizr-skills` at the 2026-11-21 wrap-up
  commit (this handoff, on top of `4d68d78c`), **pushed to origin at
  the 2026-11-21 wrap-up** — the sys1 agent pulls the head from
  origin; nothing local is needed.
- Phases 100/110/120/125/130/140 complete and committed. Phase 150
  (`c4-model-review`): stop rule **PASSED at iteration 1 of 3**
  (2026-11-17) on `p150-prove-2026-11-17T165125Z` (`none` 0/15 AND
  `upstream` 0/15 over `review-model` + `no-trigger` +
  `heldout-review`) + `p150-iter1-2026-11-17T202412Z` (`skill` 2/10 —
  two full 9/9-gate passes on `review-model` — vs 0/10 vs 0/10;
  margins `ok: true, -20.0pp, no clearly-worse case`); Task 150.150
  bookkeeping committed (`ad555af4`: pinning test 30 tests, bundle
  49 → 55, suite 6384/18/0 after the origin/dev merge `d0fd1434`).
  **ONLY Task 150.140 (the held-out run + its verdict) and the final
  README entry/commit remain** — this handoff's first job.
- Frozen skill variant **v2** committed: `.opencode/skill/c4-model-review/`
  (6 markdown files), content hash
  `89e0bc4bb4867b8885a3e393eaf1c76d3811dd39bd17702a533788f0b7620fc0`
  (content-based = path-independent — verify it before any run).
- Phase 160 pre-drafted in this folder: `draft-p160-results-writeup.md`,
  `draft-p160-acc-traceability.md`, `draft-p160-agents-changelog-notice.md`
  (each with PENDING cells); its cumulative run (Task 160.100) is
  outstanding — all-fresh under sys1's own hashes.
- Feature status stays `progress`. Finalization = the standing user
  directive, in order: status → `review` (its own small docs commit),
  push, open the PR (do NOT merge), drive CI to green (poll `gh pr
  checks` without `--watch`), then the `review-feature` agent.

## Why sys1 (and the sys0 window record)

sys0's vLLM (`http://127.0.0.1:8081`, `qwen3.8-27b-bf16-896k`) is
**shared with production**. It carried an external load for ~38 h
(2026-11-17 ~20:24Z → 2026-11-20 ~20:44Z), which aborted both held-out
launch attempts at the runner's locked 1-h busy-wait, one cycle each:

- Cycle 1, `p150-heldout-2026-11-18T154347Z` (seed 16627): 5 cache
  hits + `skill-k2` **PASS 9/9** at 678 s (contended) + `skill-k4`
  FAIL at the 1200 s timeout, then aborted.
- Cycle 2, `p150-heldout-2026-11-19T070020Z` (seed 71620): 5 cache
  hits + `skill-k0` at 598.6 s (contended) with **8/9 gates — only
  failure `no_false_findings`** (a finding line names the clean,
  correctly `External`-tagged element `Loyalty Points Feed`), then
  aborted (no `run.json`/`report.json` — a partial).

The two completed partial skill trials are **forensic history only —
they count for NO verdict** (a `skill` trial is never cacheable; a
verdict needs one complete campaign run); forensics committed under
`FEAT/work/p150-heldout-abort1-…/` + `work/p150-heldout-abort2-…/`
(trial JSONs, event streams, preflights; cycle-2 stdout
`work/p150-heldout-attempt2.log`). The window DID clear on sys0 — the
monitor (started 2026-11-20T12:50:51Z, 5-min samples) wrote
`2026-11-20T20:48:56Z WINDOW-CLEARED (3 consecutive idle samples)` to
`FEAT/work/p150-window-wait.log` — but the resource belongs to
production, so the campaigns do not take it; the monitor is stopped at
the wrap-up and the closed log (final NOTE line; gitignored `*.log`,
force-added with the wrap-up record) is the complete sys0 window
record.

The user provides an **additional dedicated, currently-idle test
instance, sys1** (Exoscale, 2× RTX Pro 6000 Blackwell; a different
agent was installing it at the wrap-up — verify via preflight); both
remaining campaigns (held-out, cumulative run) run there.

## sys1 setup checklist (fresh agent, in order)

1. Clone the branch from origin: `feat-250-c4-structurizr-skills` (the pushed head).
2. `uv sync --all-extras --frozen`.
3. `uv run --frozen pre-commit install`.
4. Docker-pull the three pinned images (tag + digest; the preflight
   re-verifies the digests and aborts on any pin violation):
   - `ghcr.io/anomalyco/opencode:2.2.5` — digest
     `sha256:1690aad69864d2f6714772d1e040918feebc6df5286d2bd7e181fbb35d12d4a9`
   - `structurizr/mcp:2026.04.20` — digest
     `sha256:fc4ef98b7da925d62b08c71a90eb995a527fae30e2c04b39e3041f253c135539`
   - `structurizr/structurizr:2026.10.26-noble` — digest
     `sha256:1081d615e7a539aee8b8360e36a58f42ff6412dd8f0e1b053134cb2c76ab2303`
5. Confirm vLLM serves `qwen3.8-27b-bf16-896k` at `127.0.0.1:8081/v1`
   with the pinned MTP 5-speculative-tokens / `--max-num-seqs 2`
   config; if the install is still finishing, **poll** `uv run
   --frozen python evals/c4-skills/run.py preflight` until `ok=True`
   with no pin violation (expected to complete within hours) — do not
   launch against a not-yet-ready endpoint.
6. **Do NOT copy any sys0 `cache/` content** — expect none to be there:
   the result cache's key is the full tuple `(case_id, condition,
   version_tuple_hash, grader_hash, skill_variant_hash)` and
   `ResultCache.get` returns a miss unless the STORED key dict
   matches exactly (`evals/c4-skills/c4_skills/cache.py`). On sys1
   all three machine-dependent inputs move at once — the gitignored
   `cache/` dir is empty in the fresh clone, the grader hash is
   path-dependent, and the new GPU/vLLM build (likely) moves the
   version tuple (sys0's:
   `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`)
   — so by design the held-out measures **15 fresh trials** (5 `none`
   + 5 `upstream` + 5 `skill`), the resume prompt's "sys1
   adaptations" section superseding its "10 cache hits + 5 fresh"
   expectation, and Phase 160's cumulative run measures everything
   fresh under sys1's own hashes (no cache cleanup needed). A cache
   HIT on sys1 means a sys0 file was wrongly copied: STOP and report.
7. Recompute the grader hash on sys1 with the locked one-liner (the
   resume prompt's step-3.3 snippet) and treat **THAT** value as the
   sys1 baseline — it differs from sys0's `b4ae81af…f81b` by
   construction (absolute paths fold in); record it in the final
   README entry. The one hash that MUST match across machines is the
   skill VARIANT hash `89e0bc4b…fc0` (content-based, path-independent).

## Immediate next actions

1. Read THIS file, the README's Phase 150 entries (2026-11-18
   03:22:56.136Z, 2026-11-20 08:20:14.000Z + 15:07:31.000Z) and its
   "Decisions Made" (the Phase 150 entry at the top, the Phase 140
   Option A clause) + `phase-150-heldout-status.md`.
2. Run the held-out per `phase-150-heldout-resume-prompt.md` **AS
   AMENDED BY ITS NEW "sys1 adaptations" SECTION** — that section
   wins over any conflicting original line.
3. On completion: the final README record per the prompt's step 6
   (tick 150.140 + 150.150, new Current Status paragraph, new Updates
   entry — recording the sys1 grader hash + version tuple), the
   quality gates per step 7, and the Phase 150 completion commit —
   ONE Conventional Commit (orchestrator pattern: verify every gate,
   re-read the run's `report.json`, recompute the variant hash from
   the on-disk skill folder before committing).
4. Phase 160 per the three `draft-p160-*.md` files: Task 160.100's
   cumulative run all-fresh under sys1's hashes (the plan's 30 h
   worst-case budget applies; sys1 is dedicated, so comfortable). The
   `FULL_CASES` composition call (7 cases vs locked
   `BUDGET_FULL_CASES = 6`) and the caveat/floor rechecks are in
   `draft-p160-results-writeup.md`; the ACC rows in
   `draft-p160-acc-traceability.md`; the AGENTS/CHANGELOG/NOTICE
   target texts in `draft-p160-agents-changelog-notice.md` (Task
   160.130).
5. Finalization per the standing directive (see "Where we are").

## Locked rulings to respect (pointers — full text at the cited places)

- README "Decisions Made": the **Phase 140 Option A clause revision**
  (scoped to that single-skill phase — Phase 150 runs the FULL locked
  9-gate set, NO Option A narrowing); **G2 Option E** (the
  truth-anchored `fix` triage label); the **ACC-013 plan-literal**
  reading (user-ruled 2026-11-04) + the home-phase-data adjudication
  for byte-unchanged reused cases; the **Phase 120 loop-gate
  separation**; the **single-task skill design** (REQ-007 — one task
  per skill, the `no-trigger` trap).
- `phase-140-handoff.md`: "Key locked rulings to respect" + "Never"
  (no committed record under `evals/c4-skills/results/` ever modified
  — cite only; the `no-trigger` case definition byte-unchanged; no
  locked-value changes).
- The **going-forward rule** (README 2026-11-20 08:20:14.000Z entry):
  campaign watcher logs, preflights, runner stdout live in
  `FEAT/work/` from the start — /tmp is throwaway only (the host reaps
  it on an age schedule; it has already cost two evidence sets).
- The resume prompt's own locks: k=5, the 1200 s per-trial timeout,
  the ≥3/5-fresh-timeout stop line, the 1-h busy-wait bounded policy
  (step 3.7 unchanged on sys1), the hybrid rule (≥1/5 full 9-gate
  passes ⇒ clean acceptance; 0/5 or below `none` ⇒ "accepted with
  caveat", rechecked in Phase 160), the frozen v2 variant.

## sys0 residue (record — no action on sys1)

- The 2026-11-19 partial results dir
  (`evals/c4-skills/results/p150-heldout-2026-11-19T070020Z/`) left
  UNTRACKED on sys0 (disposable: no `run.json`; forensics committed
  under `FEAT/work/p150-heldout-abort2-…/`); it never travels — on
  sys1 the first launch is a fresh one (the sweep step is a no-op).
- The `/home/user/src/feat250-*.tar.gz` backups stay on sys0
  (redundant since `e160b692`/`ad555af4`; kept per the user ruling
  until Phase 150's final commit).
- The sys0 monitor is STOPPED at the wrap-up; `FEAT/work/p150-window-wait.log`
  (closed, final NOTE line; force-added with the wrap-up record) is the
  complete sys0 window record.
