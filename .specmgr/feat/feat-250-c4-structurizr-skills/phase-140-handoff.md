# Phase 140 session handoff (feat-250, written 2026-11-11)

Boot document for the fresh session that continues
**feat-250-c4-structurizr-skills** after the orchestrator session that
completed Phases 120/125/130, checkpointed Phase 140, and merged
`origin/dev`. Everything below is verified against the committed tree
unless marked "working tree".

## Where we are

- Worktree: `/home/user/src/biz.dfch.SpecMgr.worktree/feat-250-c4-structurizr-skills`, branch `feat-250-c4-structurizr-skills`, tracking `origin/feat-250-c4-structurizr-skills` (branch is AHEAD of origin by the session's commits — nothing pushed since the Phase 110 state; pushing is a finalization step, not yet).
- Feature status: `progress` (leave it; the end-of-feature flip to `review` happens in finalization).
- Last commits (newest first):
  - `1cb38bd4` — merge of `origin/dev` (forwarder fix #261 taken, this branch's own earlier forwarder fix `41238f0b` dropped per the CI notice "one fix, not two"; all 13 other conflicts resolved to this branch — dev carries only the pre-remediation Phase 110 snapshot; feat-108/255 landed; GENERATED.md regenerated over merged src, 587 modules).
  - `8b1f5a85` — Phase 140 measurement checkpoint (cases, graders, prove + 3 failed iteration runs, fixtures, bookkeeping; skill files deliberately held OUT — see below).
  - `9f42794e` — Phase 130 `c4-modeling` (stop rule PASS at iteration 2).
  - Phase 125 (`fix(evals): close the Phase 110 review findings G2, I1-I4`) and Phase 120 (`feat(skills): add structurizr-dsl-authoring skill`) below that.
- Quality state at `1cb38bd4`: full pytest **6478 passed / 18 skipped**, ruff format/check clean, vulture clean, `specmgr lint` on the README green, `specmgr docs`/`harness-bundle` zero-diff. The forwarder flake is dead (8 clean local runs of `tests/evals/test_forwarder.py`).
- **Working tree (untracked, DO NOT `git add -A`, DO NOT delete):**
  - `.opencode/skill/c4-view-design/` — the Phase 140 skill, 6 markdown files. This is **variant v3** (the iter3 measured variant; verify before any run: content hash over the sorted `(relpath-from-.opencode/skill/, sha256)` pairs must be `24c89794bc9ecb35cbbcabf9218a9f0e9415d4a46d3bd2ab6703b20658a16d7d` — compute with `c4_skills.pins.skill_variant_hash`, the Phase 120/130 orchestrator verification pattern).
  - `tests/opencode/test_skill_c4_view_design.py` — the Phase 140 pinning test (26 tests, green against the folder above).
  Both are held out because the stop rule has not passed: ACC-005 ties the harness-bundle regeneration (and with it the bundle drift-guard tests) to a passed stop rule. Committing the folder without regenerating the bundle breaks 2 tests; regenerating would ship a failed-phase skill in the packaged bundle.

## The pending ruling (the FIRST thing the new session needs)

Phase 140 (`c4-view-design`) **failed its stop rule after 3 iterations**.
Diagnosis (evidence in `8b1f5a85` + the README's 2026-11-10 Updates
entry): the shared 2-slot vLLM was persistently degraded for ~2 days
(Phases 130+140: 31/45 timeouts at the 1200 s budget, 6 contended,
iter3's window ~10× slower). The skill's delta IS measured (iter2's two
furthest trials: 11/12 gates with every skill-delta gate passing —
`views_within_element_bound`, `explicit_view_keys`, `has_view` — killed
at the timeout; positive trigger 5/5 on `design-views`; the no-trigger
trap held 0/10 loads across all iterations). The binding margin failure
(`better_than_none` false, 0/10 vs 1/10) comes from the ONE `none` pass:
`no-trigger`, via the documented Phase 110 `mcp_limit_stated` matcher
limitation (agents state the no-image limit in phrasings the locked
loose matcher doesn't cover; revisit was scheduled for Phase 160).

The options presented to the user (2026-11-11, UNANSWERED — ask first):

- **(a) recommended — re-measure recorded variant v3 in a healthy window.** Not a 4th iteration (same variant, same cases — the locked Phase 100/110 precedent for re-measuring in a healthy window, with disclosure). Steps: verify the window is healthy (below), re-prove the `none` baselines (the degraded-window ones are skewed — remove the affected cache entries in `evals/c4-skills/cache/`, the Phase 100 canonical-smoke precedent, and disclose), one v3 iteration run, the held-out run (~30 fresh trials total), then Task 140.150's stop-rule-conditional half (bundle + docs regeneration, tick 140.140/140.150, bookkeeping) and the single phase commit.
- **(b) (a) + pull forward the `no-trigger` matcher fix** (the Phase 160 item) if the matcher deviation is expected to keep binding `better_than_none` in a healthy window too. A grader change → new hash → re-prove regardless; needs its own locked design (widen `_IMAGE_LIMIT_PATTERNS` in `graders.py` against the committed streams' actual phrasings — the Phase 110/130 entries name the near-misses: "no local renderer", "can't rasterize", …).
- **(c) revise a locked value** (scenario size or the 1200 s budget) and re-run — advised against: the >20-element scenario is the point of the view-size gate, the budget is plan-wide.
- **(d) accept the phase failure as-is** → plan revision per the letter of the stop rule.

The user's standing rules for this feature: "Before delegating a phase
whose design depends on an unresolved decision, ask me first" — the
Phase 140 ruling is exactly such a decision; do not start it (or
Phases 150–160, which are blocked behind 140) before the user answers.

## Window-health check before any campaign

```
curl -s http://127.0.0.1:8081/metrics | grep -E 'vllm:num_requests_(running|waiting)'
```
Healthy = running 0 (or 1 with a fast drain) and waiting 0, sustained
across the preflight. The runner itself idle-waits (aborts after ~1 h;
sweep the partial dir — no `run.json` — and relaunch the IDENTICAL
command: same seed, same label; the result cache resumes baselines).
Last observed (2026-11-11 ~08:47 UTC): 1 running, 0 waiting — fluid,
not proven healthy.

## Locked Phase 140 facts (for the resume, all in `8b1f5a85` + README)

- Case set: `design-views` (online banking, 23 elements; a single
  `include *` view necessarily exceeds the locked 20 bound) +
  `no-trigger` (byte-unchanged, valid through Phase 150) +
  `heldout-views` (insurance claims; `pins.HELDOUT_VIEWS_CASE`, never in
  `FULL_CASES`). 12-gate set; NO loop-discipline gates (the locked
  Phase 120/130 separation). Comparison: `none` ONLY (plan-explicit —
  no upstream skill matches): iteration/held-out commands use
  `--conditions none,skill --comparison none`; prove used
  `--conditions none --comparison none`.
- Runs: prove `p140-prove-2026-11-09T133052Z` (seed 41733; none 1/15:
  design-views 0/5, heldout-views 0/5, no-trigger 1/5), iter1
  `p140-iter1-2026-11-10T185815Z` (seed 58207, v1
  `eae05f1d6ad7…03e24`, skill 1/10 — margin ok:true but the
  clears-its-own-gates clause failed: trigger 0/5), iter2
  `p140-iter2-2026-11-10T221407Z` (seed 93144, v2
  `ca88917c802f…41f9`, 0/10 — FAIL, 11/12-gate evidence), iter3
  `p140-iter3-2026-11-11T014146Z` (seed 31812, v3
  `24c89794bc9e…16d7d`, 0/10 — FAIL, 10/10 timeouts).
- Grader hash at checkpoint: `033fe9d960d7c003bce425176a80a063b23aabd30d407c9b9158af346728b425` (path-based — this worktree's; compute with the locked one-liner, see Phase 125 README entry). Version tuple `f22635f6…103662` unchanged.
- `design-views` is in `FULL_CASES` (7 entries); `report.py`'s
  `BUDGET_FULL_CASES = 6` stays the plan's locked budget statement — the
  Phase 160 full-run composition over 7 cases is a Phase 160 call.

## Remaining roadmap (dependency order)

1. **Phase 140 ruling + completion** (above). On success: single
   Conventional Commit for the phase (skill + results + pinning test +
   bundle/docs regeneration + bookkeeping), orchestrator-verified.
2. **Phase 150: Skill `c4-model-review`** (Tasks 150.100–150.150): case
   `review-model` (seeded defects + a clean control + a no-file-changed
   check) + `no-trigger` + `heldout-review`; comparison `upstream` +
   `none` (the upstream `c4-review` skill is the direct baseline — its
   source is at `/tmp/opencode/c4src/upstream-c4skills/skills/c4-review/SKILL.md`,
   re-clone below if /tmp was wiped); skill must be READ-ONLY (REQ-005/
   ACC-004 — "does not edit any file or model"; the pinning test pins
   the read-only wording per ACC-011). Same operationalization as
   Phase 130 (`--comparison upstream` single run over all three
   conditions, `check_margins` encodes the full stop rule).
3. **Phase 160: Cumulative regression and results** (Tasks 160.100–160.130):
   run all five skills on all cases against `none` and `upstream` under
   the final grader hash; recheck every "accepted with caveat" (none so
   far — Phases 120/130/140-if-passed are clean) AND the recorded floors
   (Phase 130 held-out 1/5 degraded-window floor; Phase 140 if (a)/(b));
   the no-trigger `mcp_limit_stated` matcher revisit (unless pulled
   forward by ruling (b)); the `FULL_CASES`-7 vs `BUDGET_FULL_CASES`-6
   composition call; results write-up under `evals/c4-skills/results/`
   (provenance table exists at `results/provenance.md`, add the
   Docker-CLI-handicap note for `upstream`, the per-skill "better than
   none on which gates" statement); ACC-001…ACC-014 traceability list;
   final `specmgr harness-bundle` drift check; `AGENTS.md` (the skill
   surface + the `evals/` directory), `CHANGELOG.md`, root `NOTICE`
   (adapted sources) — Task 160.130.
4. **Finalization (user directive, in order):** feature status →
   `review` (generic `set_status`, `type="feat"`) as its own small docs
   commit (the Phase 110 precedent `15307595`); push; open the PR (do
   NOT merge); if merge conflicts or CI red — resolve until CI green
   (poll `gh pr checks` without `--watch`; the 3.11/3.12/3.13 matrix is
   slow); THEN run the `review-feature` agent for the
   post-implementation review.

## Operating patterns the session proved (use them)

- **Orchestrator flow**: one `phase-implementer` subagent per phase,
  fresh context, fully self-contained prompt (locks + evidence + report
  contract); the orchestrator NEVER edits files — every deviation goes
  back to the (resumable) subagent with the specific failure; the
  orchestrator re-runs every quality gate itself, re-reads every
  stop-rule `report.json` (margin fields, per-case tables, cache
  reasons, variant hash recomputed from the on-disk skill folder),
  checks the diffs, and makes ONE Conventional Commit per accepted
  phase (commit message pattern: see `9f42794e` / `5d854d10`).
- **Campaign launches**: `setsid nohup uv run --frozen python
  evals/c4-skills/run.py run … > /tmp/opencode/feat250-p1NN/<label>.log
  2>&1 &` — a plain `nohup &` child dies with the launching shell
  tool's 120 s process-group timeout (hit in Phases 120/130/140; the
  Phase 130 subagent's locked wording). Poll: log tail,
  `docker ps --filter name=c4eval`, the results dir, the vLLM metrics.
  On the 1-h busy-wait abort: sweep the partial run dir (no run.json),
  relaunch identical (same seed/label) — the relaunch is the canonical
  run.
- **Quality gates before any commit** (from the worktree root):
  `uv run --frozen ruff format --check && uv run --frozen ruff check`;
  `uv run --frozen vulture src/ whitelist.py --min-confidence 60`;
  `uv run --frozen pytest -n auto --cov=src --cov-report=` (baseline at
  `1cb38bd4`: 6478 / 18 — the 26 held pinning tests are NOT in that
  count; they come back with the phase commit); `uv run --frozen
  specmgr lint .specmgr/feat/feat-250-c4-structurizr-skills/README.md`;
  `uv run --frozen specmgr docs` and `uv run --frozen specmgr
  harness-bundle` (zero diff after regeneration; the bundle test
  `tests/commands/test_harness_bundle.py` tracks the tree's file
  count — update its assertions with every skill addition, the
  Phase 120/130 precedent).
- **Never**: modify any committed record under
  `evals/c4-skills/results/` (cite only); commit
  `evals/c4-skills/work/`, `cache/`, `.upstream/` (gitignored); change
  the reused `no-trigger` case definition; start a phase before the
  previous phase's stop-rule data is committed; push before
  finalization; merge the PR.
- **Adaptation sources** (MIT-verified, provenance at
  `evals/c4-skills/results/provenance.md`; /tmp may be wiped —
  re-clone): `jrjsmrtn/c4-skills` @ `e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b`
  (sources: `c4-review` for Phase 150; all four skills readable for
  context), `structurizr/structurizr.github.io` @
  `530a96451b93f8fb96337b58aaaa1ec8c0ad4589` (DSL docs),
  `passionsplay/structurizr-skill` @
  `5e45154e1c266e0517d456855b415ba770412f16` (NOT an adaptation source
  for Phases 130+; its evals cases were the difficulty reference only).
  Spike: TXT `4a09922d-bc32-4c03-86ba-d30ebc34e0b8` (specmgr `get_txt`).
  c4model.com: concepts only, no text copied.
- **Pinned-DSL facts** (empirically verified, unit-pinned in tests):
  no `externalSystem` keyword (external = top-level `softwareSystem`/
  `element` + `External` tag); custom `element`'s description exports as
  `metadata`; omitted view key exports as `<Kind>-NNN` +
  `generatedKey: true` + the `views.view.key` inspect finding;
  `include *` scoping (Phase 140 gate docstring); CLI `inspect` rc=1
  with findings, pipe-form lines.
- **Key locked rulings to respect** (full text in the README's
  Decisions Made): G2 Option E truth-anchored `fix` labels (user-ruled
  2026-11-08); `--comparison upstream` single-run operationalization +
  prove-scope (held-out baselines measured in the prove run, extended
  to `upstream` in Phase 120); ACC-013 plan-literal reading (user-ruled
  2026-11-04) + the home-phase-data adjudication for byte-unchanged
  reused cases; NO loop-discipline gates on non-loop skills' primary
  cases (Phase 120 separation); the c4-modeling scope cut (Diagram
  Types/Selection Guide → c4-view-design); the no-trigger known
  limitation (documented deviation, Phase 160 revisit).

## Immediate next actions for the fresh session

1. Ask the user for the Phase 140 ruling (options (a)–(d) above;
   recommend (a)). Do not run any campaign or touch the held skill
   files before the answer.
2. On (a)/(b): verify window health; delegate the resume to a
   `phase-implementer` with this file + the README as context; verify
   as in the proven pattern; one phase commit.
3. Continue the roadmap: Phase 150 → Phase 160 → finalization
   (status review commit, push, PR, CI green) → `review-feature` agent.

## 2026-11-13 addendum (origin/dev merged, ed4b4ad9)

- The merge landed: `origin/dev`'s ADR-artifact-removal rename (#46/#258) plus the feat-167 files (#260); parents `61da2be8` + `b5455bf7`, merged 2026-11-13.
- The grader hash in this worktree is now `21140c84f17946b18a81a79e60374b8736b77234c5bb8ec6920b58d23f59c0c8` (verified); the `033fe9d9…` "checkpoint" figure above was computed from a different worktree path (`pins.source_hash` folds in absolute paths) — the p140 campaigns actually ran under `c7340b25…` per the committed cache keys in `evals/c4-skills/cache/*.none.json`.
- The ruling (a) "remove the affected cache entries" step is superseded by the hash move: under the new hash those entries are cache-key mismatches, so the prove run re-measures all three `none` baselines fresh anyway; ruling (a) is otherwise unchanged.
- Unchanged/verified: version tuple (`f22635f6…103662`), the reused `no-trigger` case definition (byte-unchanged), the held-out v3 skill hash (`24c89794…6d7d`).
- The harness bundle is regenerated at 43 entries WITHOUT the held-out c4-view-design skill (ACC-005); `test_harness_bundle.py` count updated to 43.
- See the README Updates entry of the same date for the post-merge tree state (ruff/vulture/`specmgr lint` green; pytest 6275/18 + the two known-red bundle tests; `docs/GENERATED.md` at 502 vs 501 on the bare merge).
- **Session wrap-up (2026-11-13, sys0 restart):** the branch was pushed to `origin/feat-250-c4-structurizr-skills` per user directive (the "pushing is a finalization step, not yet" note above is superseded for the push only — the PR/merge finalization steps still stand). The two held-out paths (`.opencode/skill/c4-view-design/`, `tests/opencode/test_skill_c4_view_design.py`) were deliberately NOT committed (ACC-005: the stop rule has not passed) and are additionally backed up as a tarball at `/home/user/src/feat250-heldout-v3-backup-20261113.tar.gz` — after the restart, if the worktree copies are missing, extract from there and re-verify the v3 hash `24c89794…6d7d` before any run. Post-restart: the vLLM server comes back unknown — re-verify the window from scratch (the preflight re-checks every pin anyway); the passive watcher at `/tmp/opencode/feat250-p140r/window.log` died with the reboot.
