---
classification: null
created: '2026-10-24T11:39:24.997+02:00'
id: feat-233-update-release
status: planning
type: feat
updated: '2026-10-24T11:39:24.997+02:00'
version: 1.0.0
---

# Feature: Update the release precheck — feat closeout gate and previous-release branch cleanup

## Plan

### Overview

The 2026-10-23 manual branch/record cleanup surfaced two process gaps in the release
flow, neither of which the staged `scripts/release.sh` machinery currently enforces:

1. **Features ship with their plan documents still at `status: review`.** feat-129 and
   feat-214 were both merged into `dev` (PRs #220/#216) and shipped in v0.37.0, yet their
   `.specmgr/feat/*/README.md` frontmatter stayed at `review` until closed out by hand
   (commits `b5cd89c`, `4a33271`). Nothing on the release path required the closeout.
2. **Stale feature branches accumulate.** ~30 local branches and 25+ remote branches from
   previous releases had to be deleted manually, each requiring a per-branch attribution of
   *which release its work shipped in* (tip-ancestor check or squash-commit lookup) plus
   safety gates (four pre-squash-convention branches, two local≠origin pairs, and the
   worktree-checked-out feat-139 branch).

This feature bakes both rules into `scripts/release.sh precheck` (SOP 98537416 step 2) so
that every future release stops — before the version increment is written — until (Rule 1)
every feat that shipped in the current release window is closed out to `status: done`, and
then (Rule 2) deletes the stale local/origin `feat-*`/`fix/*` branches from the *previous*
release (or older), each deletion proven by a merged-PR lookup and guarded against the
four hazard classes met in the manual pass.

### Requirements

- REQ-001: `stage_precheck` gains a **feat closeout gate** that runs *before* `stage_bump` writes the version increment: for every `.specmgr/feat/feat-*/` folder whose frontmatter `status` is not `done`, determine whether the feature's implementation merged into the current release window (`vPrev..HEAD`, `vPrev` = the latest tag reachable from `dev` via `git describe --tags --abbrev=0`); if it did, the gate fails the precheck, with "merged" determined as the newest merged PR (head ref = the feat id, read from GitHub REST `pulls?state=closed&head=<owner>/<feat-id>` filtered on `merged_at != null`) whose `merge_commit_sha` (valid for both squash and merge PRs) is an ancestor of `HEAD` but not of `vPrev`, and any violation failing the precheck with an actionable line per offending feat (feat id, current status, PR number, delivery sha).
- REQ-002: A feat with **no** merged PR for its head ref is *never* gated by the closeout gate — plan-only feats (a freshly-added plan with no implementation PR yet) and in-flight/abandoned feats pass the gate regardless of their `status`.
- REQ-003: A feat whose newest merged-PR delivery commit is **not** inside `vPrev..HEAD` (i.e. it shipped in an earlier release) is not gated by the closeout gate — the gate covers only the feature set of the release being cut.
- REQ-004: `stage_precheck` gains a **previous-release branch cleanup** that runs *after* the closeout gate: it deletes local and `origin/` `feat-*`/`fix/*` branches whose newest merged-PR delivery commit is an ancestor of `vPrev` (stale from the previous release or older), deleting the local ref with `git branch -d` (falling back to `-D`, justified by the merged-PR proof) and the remote ref with `git push origin --delete <name>`.
- REQ-005: The cleanup applies four guards, each emitting a report line instead of a deletion: (a) the branch is checked out in any worktree (from `git worktree list --porcelain`) → skip; (b) the branch has no merged PR for its head ref → keep (in-flight/abandoned, manual decision); (c) the branch's delivery commit is inside `vPrev..HEAD` → keep (current release — it becomes deletable at the *next* release's precheck); (d) the branch name exists on both the local and `origin/` side with local tip ≠ remote tip → skip both sides (manual decision).
- REQ-006: The existing global `--dry-run` flag (`DRY_RUN=1`) makes the cleanup report-only: it prints the full would-delete/would-keep table and mutates no ref, and a closeout-gate failure stops the precheck before any cleanup mutation runs (sub-item ordering: existing checks (a)–(f) → closeout gate → branch cleanup).
- REQ-007: Both new sub-items are idempotent: re-running `precheck` after a successful cleanup reports nothing to delete, and re-running after the closeout gate's remediation (the feat docs committed to `done`) passes.
- REQ-008: The SOP (98537416) is updated to remain the normative document: step 2 gains the two sub-items, `Definitions` gains *delivery commit* and *stale branch*, `Safety and Precautions` records that branch cleanup is the only mutating precheck sub-item (and why that is safe), and a dated `Updates` entry describes the change.
- REQ-009: The `scripts/release.sh` header/usage comment, the `/release` OpenCode command (`.opencode/command/release.md`), and the README "Make a Release" section are synced to describe the two new precheck sub-items and the closeout-remediation loop.
- REQ-010: `tests/test_release_sh.py` (the existing fake-`gh`-shim unittest suite that sources the script's helpers) gains coverage for the closeout gate (review-status feat with an in-window merged PR ⇒ precheck dies with the actionable line; the same feat at `done` ⇒ passes; a plan-only feat with no merged PR ⇒ passes; a feat delivered in an earlier release ⇒ passes) and for the cleanup (matching-tip branch delivered ≤ vPrev ⇒ local+origin deleted; in-window delivery ⇒ kept; no merged PR ⇒ kept; worktree-checked-out ⇒ skipped; local≠origin ⇒ both skipped; `--dry-run` ⇒ no mutation; gate failure ⇒ no cleanup mutation; re-run ⇒ no-op).

### Acceptance Criteria

- [ ] ACC-001: With a fixture repo carrying a feat folder at `status: review` whose head ref has a merged PR with `merge_commit_sha` inside `vPrev..HEAD`, `stage_precheck` exits non-zero and its output names the feat, its status, the PR number, and the delivery sha (REQ-001).
- [ ] ACC-002: The same fixture with the feat at `status: done`, and a fixture with a plan-only feat (no merged PR for its head ref) at any status, both pass the closeout gate (REQ-001, REQ-002).
- [ ] ACC-003: A feat whose newest merged-PR delivery commit is an ancestor of `vPrev` passes the closeout gate even at `status: review` (REQ-003).
- [ ] ACC-004: With a local and `origin/` `feat-*` branch (matching tips) whose delivery commit is an ancestor of `vPrev`, the cleanup deletes both refs, the local deletion using `-d` and the remote using `git push origin --delete` (REQ-004).
- [ ] ACC-005: Each of the four guard classes (worktree-checked-out; no merged PR; in-window delivery; local≠origin tips) produces a keep/skip report line and leaves the ref(s) intact (REQ-005).
- [ ] ACC-006: `precheck ... --dry-run` prints the full would-delete/would-keep table and leaves every ref intact, and a precheck that fails the closeout gate mutates no ref (REQ-006).
- [ ] ACC-007: Re-running `precheck` after a successful cleanup reports nothing to delete, and after the closeout remediation passes (REQ-007).
- [ ] ACC-008: The SOP's step 2, Definitions, Safety and Precautions, and a dated Updates entry describe both sub-items, and the SOP remains parseable (`parse_sop` green) (REQ-008).
- [ ] ACC-009: The `scripts/release.sh` header/usage, `/release` command, and README "Make a Release" section all describe the two new sub-items and the closeout-remediation loop (REQ-009).
- [ ] ACC-010: `tests/test_release_sh.py` gains the gate and cleanup cases listed in REQ-010 and the full suite (`uv run --frozen pytest -n auto`) passes, with `ruff format --check`, `ruff check`, and `vulture` staying clean (REQ-010).

### Scope

#### Included

- `scripts/release.sh`: the `stage_precheck` extensions (closeout gate + branch cleanup), the helper functions they need (latest-tag resolution, feat-folder scan, merged-PR delivery lookup via `gh api`, the four cleanup guards, the would-delete/would-keep report), and the header/usage comment.
- `tests/test_release_sh.py`: the fake-`gh`-shim fixture extensions and the gate/cleanup test cases.
- `docs/sop/sop-98537416-...md`: step 2, Definitions, Safety and Precautions, Updates.
- `.opencode/command/release.md` and `README.md` ("Make a Release"): the synced prose.

#### Explicitly Out Of Scope

- A new release stage or SOP procedure step — both rules fold into the existing `precheck` stage (maintainer decision 2026-10-23); no step renumbering.
- Automatic feat closeout — the agent/maintainer still edits the feat READMEs (status → `done` + finalization entry); the gate only *enforces*, it does not *perform*, the closeout.
- A `status`-stage display change and a `--skip-cleanup` flag — possible follow-ups, not part of this feature.
- Deleting any branch class other than `feat-*`/`fix/*` (e.g. `dependabot/*`) — the manual pass left those to their own lifecycle.
- Changing how the release PR/tag/publication stages behave.

### Dependencies

#### Depends On

- The existing `tests/test_release_sh.py` fake-`gh`-shim harness and the script's `BASH_SOURCE` dispatch guard (both landed with feat-213-release) — the new tests extend that harness rather than introducing a new one.

#### Blocks

- Nothing. This feature is additive to the release precheck and does not gate any other in-flight feature.

### Design Notes

**Why `precheck` and not a new stage.** The maintainer placed Rule 1 in `precheck` because it must hold *before* the version increment is written to `pyproject.toml` (`stage_bump` is the first mutating stage after `precheck`), and placed Rule 2 in `precheck` because the latest tag is unambiguous there (`vPrev` is simply `git describe --tags --abbrev=0` — the release being cut has no tag yet, which precheck's existing check (d) already asserts). Folding both into `precheck` keeps the stage/step 1:1 mapping intact and avoids SOP step renumbering. The consequence that `stage_all` (the non-agent path) inherits the cleanup is accepted and recorded in the issue.

**Delivery commit via `merge_commit_sha`, not the head SHA.** A squash-merged feat branch leaves *no* head-SHA ancestor on `dev` (the head commits are rewritten), so `git merge-base --is-ancestor <head> dev` is the wrong staleness test for the majority of this repo's features. GitHub's `merge_commit_sha` is the real `dev`-side commit for both squash and merge PRs, so "stale" and "shipped-in-window" reduce to two ancestry tests against that one SHA: ancestor of `vPrev` (stale, delete) vs. ancestor of `HEAD` but not of `vPrev` (current release, keep).

**GitHub REST, not GraphQL.** The script is written against this environment's `gh` 2.4.0, whose GraphQL call sites (`gh pr view --json`, `gh run view --json jobs`) are known-broken (SOP Safety and Precautions). The merged-PR lookup therefore uses `gh api "repos/dfch/biz.dfch.SpecMgr/pulls?state=closed&head=dfch/<feat-id>"` filtered with `jq` for `merged_at != null`, taking the newest by `merged_at` — the same REST precedent the script already uses for `close_pr_if_open` and the release notes.

**The four cleanup guards, and where each came from.** (a) Worktree-checked-out: a branch checked out in a worktree cannot be deleted and represents live work (the manual pass's feat-139). (b) No merged PR: in-flight or abandoned work the maintainer may still want (the manual pass's `feat-46-remove-adr`, `feat-63-refine`, `feat-134-similarity-requires-mcp`). (c) In-window delivery: the current release's branches stay one cycle (the manual pass kept every v0.37.0 branch). (d) Local≠origin tips: the two sides may carry different content, so neither is provably stale (the manual pass's feat-134/feat-144 pairs). Each guard is a keep/skip with a report line, never a silent skip.

**Gate ordering is a safety property.** The closeout gate runs before the cleanup so a gate failure stops the precheck with zero ref mutations (REQ-006/ACC-006). This is pinned by a dedicated test, not just by code order.

### Related Decisions

- SOP 98537416-0e6e-4a02-925f-974a17bfa10a ("Perform a release of biz.dfch.SpecMgr") — the normative procedure this feature amends (step 2, Definitions, Safety and Precautions, Updates).
- feat-213-release (`.specmgr/feat/feat-213-release/README.md`, GitHub issue #213) — the release-script hardening precedent that established `tests/test_release_sh.py`'s fake-`gh`-shim harness and the `BASH_SOURCE` dispatch guard this feature's tests extend.
- The 2026-10-23 manual closeout commits `b5cd89c` (feat-129) and `4a33271` (feat-214) — the concrete gap Rule 1 closes; the feat-closeout shape (status → `done` + a "Finalization" Updates entry recording the PR merge) they establish is the remediation the gate's actionable message points at.

### Task List

#### Phase 100: Closeout gate in `stage_precheck`

- [ ] Task 100.100: Add the helper functions the gate needs: `latest_tag()` (`git describe --tags --abbrev=0`, empty + info note when no tag exists), `feat_folders()` (list `.specmgr/feat/feat-*/` ids), `feat_status(<id>)` (read the frontmatter `status:` line), and `merged_delivery(<head-ref>)` (`gh api pulls?state=closed&head=...` + `jq` filter for `merged_at != null`, newest by `merged_at`, printing `number<TAB>merge_commit_sha` or nothing).
- [ ] Task 100.110: Wire the gate into `stage_precheck` after the existing checks (a)–(f): for each feat folder whose `status` is not `done`, look up its merged delivery; if found and the delivery SHA is an ancestor of `HEAD` but not of `vPrev`, record it as a violation; after the loop, if there are violations, `die` with one actionable line per offending feat (id, status, PR number, sha) plus the remediation pointer (close out to `done` on `dev`, then re-run `precheck`).
- [ ] Task 100.120: Add the gate's `tests/test_release_sh.py` cases (ACC-001, ACC-002, ACC-003): review-status feat with an in-window merged PR ⇒ precheck dies naming the feat; the same feat at `done` ⇒ passes; plan-only feat (no merged PR) ⇒ passes; feat delivered in an earlier release ⇒ passes.

#### Phase 110: Previous-release branch cleanup in `stage_precheck`

- [ ] Task 110.100: Add the cleanup helpers: `cleanup_candidates()` (local + `origin/` `feat-*`/`fix/*` branch names, excluding `dev`/`main`), `worktree_branches()` (from `git worktree list --porcelain`), and `branch_delivery(<name>)` (the same `merged_delivery` lookup keyed on the branch's head ref).
- [ ] Task 110.110: Implement the cleanup loop in `stage_precheck` after the gate: for each candidate name, apply guards (a) worktree-checked-out → skip, (b) no merged delivery → keep, (c) delivery inside `vPrev..HEAD` → keep, (d) local and origin tips differ → skip both; otherwise delete the local ref (`git branch -d`, `-D` fallback) and the `origin/` ref (`git push origin --delete <name>`); under `DRY_RUN=1` print the would-delete/would-keep table and mutate nothing. Every keep/skip emits a report line naming the branch and the guard that fired.
- [ ] Task 110.120: Add the cleanup's `tests/test_release_sh.py` cases (ACC-004, ACC-005, ACC-006, ACC-007): matching-tip branch delivered ≤ vPrev ⇒ both refs deleted; each of the four guards ⇒ ref(s) intact with a report line; `--dry-run` ⇒ table printed, no mutation; gate failure ⇒ no cleanup mutation; re-run after cleanup ⇒ nothing to delete.

#### Phase 120: Documentation sync (SOP, script header, `/release`, README)

- [ ] Task 120.100: Update `scripts/release.sh`'s header/usage comment so the `precheck` line names the two new sub-items (feat closeout gate, previous-release branch cleanup) and the `--dry-run` note covers the cleanup's report-only mode.
- [ ] Task 120.110: Update SOP 98537416: step 2 gains the two sub-items in their run order, `Definitions` gains *delivery commit* and *stale branch*, `Safety and Precautions` gains an entry recording that the cleanup is the only mutating precheck sub-item and why the merged-PR proof + four guards make that safe, and a dated `Updates` entry describes the change; confirm `parse_sop` stays green.
- [ ] Task 120.120: Sync `.opencode/command/release.md` and the README "Make a Release" section to describe the two sub-items and the closeout-remediation loop (gate fails → close out the named feats to `done` on `dev` → commit → re-run `precheck`).

#### Phase 130: Verification and closeout

- [ ] Task 130.100: Run the full quality gate — `uv run --frozen pytest -n auto` (the `test_release_sh.py` cases green), `ruff format --check`, `ruff check`, and `vulture src/ whitelist.py --min-confidence 60` — and confirm ACC-001 through ACC-010 are each evidenced by a named test or a named doc surface.
- [ ] Task 130.110: Close out — tick the verified acceptance criteria, set the plan status to `review`, and add the `CHANGELOG.md` `[Unreleased]` entry describing the two new precheck sub-items.

## Progress

### Current Status

**As of 2026-10-24**: Planned. The design was settled in a planning session against the
live repo state (the 2026-10-23 manual cleanup of ~30 stale local branches, 25+ stale
remote branches, and the feat-129/feat-214 closeouts is the motivating evidence). The
maintainer's two placement decisions are recorded in Design Notes: the closeout gate runs
in `precheck` (it must hold before `stage_bump` writes the version increment), and the
branch cleanup also runs in `precheck` (where the latest tag unambiguously names the
previous release). Nothing implemented yet; the plan is ready for review.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-24T11:39:24.997+02:00 - Created

Drafted the feature plan from GitHub issue #233, grounded in the 2026-10-23 manual
branch/record cleanup (the stale-branch attribution work, the four cleanup hazard classes,
and the feat-129/feat-214 closeout commits `b5cd89c`/`4a33271`) and a read of
`scripts/release.sh`'s `stage_precheck`, the SOP 98537416 procedure, and the
`tests/test_release_sh.py` fake-`gh`-shim harness.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-24T11:39:24.997+02:00 - Both rules fold into `precheck`; no new stage or SOP step

The maintainer rejected a dedicated post-`release-notes` cleanup stage and a
separate pre-`bump` gate stage in favor of extending `stage_precheck` with two sub-items
(closeout gate, then branch cleanup). Rationale captured in Design Notes: the gate must
hold before the version increment is written (precheck is the last stage before `bump`),
and the latest tag is unambiguous in precheck because the release being cut has no tag
yet. This keeps the SOP's stage/step 1:1 mapping and avoids renumbering. The accepted
consequence — `stage_all` inherits the cleanup — is recorded in the issue.
