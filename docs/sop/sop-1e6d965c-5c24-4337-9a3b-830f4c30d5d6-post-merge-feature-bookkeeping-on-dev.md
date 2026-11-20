---
classification: null
created: '2026-11-13T22:24:40.797+01:00'
id: 1e6d965c-5c24-4337-9a3b-830f4c30d5d6
status: draft
type: sop
updated: '2026-11-13T22:24:40.797+01:00'
version: 1.0.0
---

# Post-merge feature bookkeeping on dev

## Purpose

This procedure defines how a merged feature PR is recorded on `dev`: verifying the squash merge, updating the feature plan (`.specmgr/feat/<id>/README.md`) with a dated Updates entry and a Current Status correction, deciding between a full closeout (`status: done`) and a mid-feature record, and landing a single conventional-commit bookkeeping commit on `dev`. It exists so that every merged feature leaves `dev` with a parseable, current plan record, and so the release precheck's feat closeout gate (SOP 98537416, step 2) is never surprised by an unclosed in-window feature.

## Scope

This SOP covers: verifying the squash merge (state, squash hash, tree identity against the branch head); classifying the bookkeeping kind (closeout vs. mid-feature record) including the gate attribution check; the plan frontmatter / Current Status / Updates edits; the plan validation; and the bookkeeping commit + push to `dev` (the delegated-bookkeeping exception to the standing constraint that agents never merge PRs).

It does not cover: merging the PR itself (a user action); the release flow (SOP 98537416); feature implementation or review; branch/worktree cleanup (a user decision); and creating the feature plan itself.

## Definitions

- A bookkeeping commit is the single `dev`-side commit that records a merged feature PR in its plan README (and, for a closeout, flips the plan's `status` to `done`).
- A squash hash is the `mergeCommit` of a squash-merged PR; its tree is byte-identical to the merged branch's head.
- A delivery is a merged PR that delivered a feature's content; the release precheck attributes deliveries to feat folders by head-ref name (exact folder-id match, then a `feat-<NNN>-` prefix fallback).
- A closeout is the bookkeeping kind for a finished feature: every plan task ticked, no deferred phases; the plan's `status` moves to `done`.
- A mid-feature record is the bookkeeping kind for a shipped slice: deferred phases remain; the plan's `status` is unchanged.
- Delegated bookkeeping is the standing-constraint exception that permits an agent to commit and push to `dev` for closeouts, verification, and release commits only.
- The plan README is `.specmgr/feat/<id>/README.md`, the single plan-plus-progress artifact per feature folder.

## Roles and Responsibilities

### Accountable

The user (dfch) is accountable: they merge the PR, direct the bookkeeping, and own the standing constraint that agents never merge PRs and never push feature branches ahead of the user.

### Responsible

- The directed agent session (fresh or continuing) performs Steps 1-7 and lands the bookkeeping commit on `dev`.

### Support

- The feature's orchestrator session, if still running, supplies the branch-head sha, the PR number, and the pre-merge verification evidence.

### Informed

- The user is informed of the `dev` tip, the plan lint outcome, and what remains deferred.
- Other in-flight feature sessions are informed through the plan's dated Updates entry (and any untracked HANDOFF note the user maintains).

## Safety and Precautions

Stop and report, do not guess, when: the squash tree differs from the branch head (a manual merge or a stale head); a plan anchor is missing (the plan was edited concurrently); `dev` moved since the pull (re-`git pull --ff-only` and re-verify); or the plan fails `specmgr lint` after the edit. Dated Updates entries are history — prepend new ones, never edit existing ones (when porting another session's unpushed entry onto `dev`, port it verbatim and supersede its stale state lines from the newer entry). Every list item is a single physical line (no soft-wraps). Never `git add -A`: untracked session artifacts (transcripts, HANDOFF notes) must never be committed. Stale `__pycache__`-only directories pollute `specmgr docs` regeneration (e.g. after a merge that deletes source packages) — if the bookkeeping requires regenerated docs, remove the pyc-only shells first. Do not restructure `CHANGELOG.md` `[Unreleased]` (the release flow curates it). Never create a `dev`->`main` PR outside the release flow (SOP 98537416): the standing PR #251 was closed 2026-11-13 as off-process, and the flow's `pr-create` stage creates the release PR. While this SOP is `draft` it is reference-only: follow it, but report any deviation for the activation decision.

## Procedure

### Step 1: Verify the merge

Run `gh pr view <N> --json state,mergedAt,mergeCommit` — `state` must be `MERGED`; record the squash hash `H`. Confirm `git ls-remote origin dev` shows `H` at the tip (or `H` plus later `dev` commits — the Step 2 tree identity targets `H` either way).

### Step 2: Verify tree identity

In the `dev` worktree run `git pull --ff-only origin dev`, then `git diff <branch-head> H --stat` — the output must be empty (a squash carries the branch head's tree). Any output means a manual merge or a stale head: stop and report.

### Step 3: Decide the bookkeeping kind, and check gate attribution

Read the plan's task list: every task ticked with no deferred phases is a closeout; otherwise it is a mid-feature record. Independently of that choice, determine whether the release precheck would attribute the feature's delivery to its folder: the gate (SOP 98537416 step 2) matches merged-PR head refs exactly against the folder id, then by the `feat-<NNN>-` prefix. If the branch was named differently from the folder id (case: feat-167's bare `feat-167` branch vs. its `feat-167-mcp-lifecycle-commands-2` folder), the delivery is not attributed and the feature is not gated — record that fact in the Updates entry, and note that future work on a folder-matching branch name re-enables the gate.

### Step 4: Edit the plan

Single physical lines; assert every anchor and stop if one is missing. Frontmatter: bump `updated` (local timezone, milliseconds) always; set `status` to `done` for a closeout only (legal per the feat table: `review -> done` / `progress -> done`). For a closeout, replace Current Status with the short closeout paragraph (the feat-173/247/46 pattern): the merged PR + squash hash, the closeout statement, the line "The closeout satisfies the feat-233-update-release precheck feat-closeout gate for the `<window>` release window", and the pointer that the historical record lives in the dated Updates entries. For a mid-feature record, update the Current Status date marker and append the merge facts (PR, squash hash, date, what is now on `dev`) plus the next action. Prepend one dated Updates entry (newest first, directly below the comment line): closeout heading `#### <now> - Closeout: PR #<N> merged to dev, status <x> -> done, issue #<M> closed`; mid-feature heading `#### <now> - Phase <NNN> merged to dev (PR #<N>, squash <H>): <what landed>; <what remains> deferred`; body = the empirical record (verification facts, what landed, what remains). For a closeout, also tick any final deferred tasks with a completion note, and remove throw-away feature-folder artifacts only where the plan itself names the removal (case: feat-46 Task 160.120's `bin/` scripts + manifest), preserving the manifest content in the PR description first.

### Step 5: Validate the plan

In the `dev` worktree run `uv run --frozen specmgr lint .specmgr/feat/<id>/README.md` — exit 0 with `failed=0` (the pre-commit hook re-checks at commit time).

### Step 6: Commit and push to dev (delegated bookkeeping)

Stage the plan file only. Commit message: closeout `docs: close out <feat-id> to done (PR #<N> merged[, issue #<M> closed])`; mid-feature `docs(<feat-id>): record Phase <NNN> merge to dev (PR #<N>); <what remains> deferred`. Commit (hooks run) and push to `origin dev`.

### Step 7: Report

Report the `dev` tip hash, the plan lint outcome, the status result, what remains deferred (and, per Step 3, whether the gate attributes the feature), and that branch/worktree cleanup is the user's call.

## Related Artifacts

### Decisions

- DEC e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in .specmgr with feature-driven work units (the plan-README structure this SOP edits).
- DEC a79608e4-88cd-498f-8ca1-445df4d04f92: Per-domain status state machines for set_status (the legal feat transitions this SOP relies on).

### Sops

- SOP 98537416-0e6e-4a02-925f-974a17bfa10a: Perform a release of biz.dfch.SpecMgr (its step 2 feat closeout gate consumes this SOP's closeout decisions).

## More Information

Execution precedents: `3aa34af1` (feat-173 closeout), `0dd59337` (feat-247 closeout), `fffb9cd0` (feat-46 closeout — including the Task 160.120 throw-away removal with the 47th manifest entry preserved as a PR #258 description addendum), and the feat-167 mid-feature record of 2026-11-13 (this SOP's first live case). Gate-attribution case study: the feat-167 branch is named bare `feat-167` while its folder is `feat-167-mcp-lifecycle-commands-2`, so PR #260's delivery is not attributed by the gate and the feature is not subject to the v0.39.0 precheck while its status is `review`. This SOP is `draft`: reference-only until the user activates it.

## Updates

### 2026-11-13 22:24:40.797+01:00 - Created

Created as `draft`, codifying the post-merge bookkeeping practice executed for feat-173, feat-247 and feat-46 (closeouts), with the feat-167 Phase 100 mid-feature record (2026-11-13) as its first live case. Activation (`draft -> active`) is a user decision, expected once the first execution verifies clean.
