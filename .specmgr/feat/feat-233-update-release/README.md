---
classification: null
created: '2026-10-24T11:39:24.997+02:00'
id: feat-233-update-release
status: review
type: feat
updated: '2026-10-24T23:29:29.223+02:00'
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
   safety gates for the four hazard classes the pass met — the same classes the cleanup's
   guards (a)–(d) protect: a worktree-checked-out branch, a branch with no merged PR,
   an in-window (current-release) branch, and a local≠origin tip pair.

This feature bakes both rules into `scripts/release.sh precheck` (SOP 98537416 step 2) so
that every future release stops — before the version increment is written — until (Rule 1)
every feat that shipped in the current release window is closed out to `status: done`, and
then (Rule 2) deletes the stale local/origin `feat-*`/`fix/*` branches from the *previous*
release (or older), each deletion proven by a merged-PR lookup and guarded against the
four hazard classes met in the manual pass.

### Requirements

- REQ-001: `stage_precheck` gains a **feat closeout gate** that runs *before* `stage_bump` writes the version increment: for every `.specmgr/feat/feat-*/` folder whose frontmatter `status` is not `done`, determine whether the feature's implementation merged into the current release window (`vPrev..HEAD`, `vPrev` = the latest tag reachable from `dev` via `git describe --tags --abbrev=0`; when no tag exists at all the window is `HEAD`, so the first release gates every non-`done` feat that has any merged PR); if it did, the gate fails the precheck, with "merged" determined as the newest merged PR (head ref = the feat id, read from GitHub REST `repos/{owner}/{repo}/pulls?state=closed&head={owner}:<ref>&per_page=100` filtered on `merged_at != null`, extended by the REQ-011 issue-number-prefix fallback) whose `merge_commit_sha` (valid for both squash and merge PRs) is an ancestor of `HEAD` but not of `vPrev`, and any violation failing the precheck with an actionable line per offending feat (feat id, current status, PR number, delivery sha). A folder whose frontmatter `status` line is missing or unparseable is a violation in its own right — the gate cannot prove the feat is `done` — with an actionable line naming the defect (repair the frontmatter, or close out to `done`, then re-run `precheck`); the fail-safe is to block the release, never to skip the folder.
- REQ-002: A feat with **no** merged PR under its lookup (the exact head ref, or the REQ-011 issue-number-prefix fallback) is *never* gated by the closeout gate — plan-only feats (a freshly-added plan with no implementation PR yet) and in-flight/abandoned feats pass the gate regardless of their `status`.
- REQ-003: A feat whose newest merged-PR delivery commit is **not** inside `vPrev..HEAD` (i.e. it shipped in an earlier release) is not gated by the closeout gate — the gate covers only the feature set of the release being cut.
- REQ-004: `stage_precheck` gains a **previous-release branch cleanup** that runs *after* the closeout gate: it deletes local and `origin/` `feat-*`/`fix/*` branches whose newest merged-PR delivery commit is an ancestor of `vPrev` (stale from the previous release or older), deleting the local ref with `git branch -d` (falling back to `-D`, justified by the merged-PR proof) and the remote ref with `git push origin --delete <name>`; each side is deleted and reported independently, so a branch present only locally or only on `origin/` is deleted on the side that exists and reported as one-side. When no tag exists at all there is no "previous release or older," so the cleanup deletes nothing and reports the skip alongside the gate's no-prior-tag note.
- REQ-005: The cleanup applies four guards, each emitting a report line instead of a deletion: (a) the branch is checked out in any worktree (from `git worktree list --porcelain`) → skip; (b) the branch has no merged PR for its head ref → keep (in-flight/abandoned, manual decision); (c) the branch's delivery commit is inside `vPrev..HEAD` → keep (current release — it becomes deletable at the *next* release's precheck); (d) the branch name exists on both the local and `origin/` side with local tip ≠ remote tip → skip both sides (manual decision). Guards are evaluated per branch in the order (a)→(d) and the first guard that fires wins, emitting exactly one report line naming the branch and that guard, even when several guards could apply.
- REQ-006: The existing global `--dry-run` flag (`DRY_RUN=1`) makes the cleanup report-only: it prints the full would-delete/would-keep table and mutates no ref, and a closeout-gate failure stops the precheck before any cleanup mutation runs (sub-item ordering: the six existing checks (a)–(f) documented in SOP 98537416 step 2 → closeout gate → branch cleanup).
- REQ-007: Both new sub-items are idempotent: re-running `precheck` after a successful cleanup reports nothing to delete, and re-running after the closeout gate's remediation (the feat docs committed to `done`) passes.
- REQ-008: The SOP (98537416) is updated to remain the normative document: step 2 gains the two sub-items, `Definitions` gains *delivery commit*, *stale branch*, and *issue-number prefix*, `Safety and Precautions` records that branch cleanup is the only mutating precheck sub-item (and why that is safe), and a dated `Updates` entry describes the change.
- REQ-009: The `scripts/release.sh` header/usage comment, the `/release` OpenCode command (`.opencode/command/release.md`), and the README "Make a Release" section are synced to describe the two new precheck sub-items and the closeout-remediation loop.
- REQ-010: `tests/test_release_sh.py` (the existing fake-`gh`-shim unittest suite that sources the script's helpers; its fake `gh` is extended in Task 100.115 to answer the merged-PR search call) gains coverage for the closeout gate (review-status feat with an in-window merged PR ⇒ precheck dies with the actionable line; the same feat at `done` ⇒ passes; a plan-only feat with no merged PR ⇒ passes; a feat delivered in an earlier release ⇒ passes; a feat folder with a missing or unparseable `status` line ⇒ precheck dies with the frontmatter-defect line; a feat whose work merged only under a differently-named `feat-<NNN>-*` branch ⇒ found by the prefix fallback and gated; no prior tag ⇒ every delivery counts as in-window) and for the cleanup (matching-tip branch delivered ≤ vPrev ⇒ local+origin deleted, the local side via the `-D` fallback when `-d` refuses the squash-merged head; local-only or remote-only branch ⇒ deleted on the side that exists, reported one-side; in-window delivery ⇒ kept; no merged PR ⇒ kept; worktree-checked-out ⇒ skipped; local≠origin ⇒ both skipped; `--dry-run` ⇒ no mutation; gate failure ⇒ no cleanup mutation; re-run ⇒ no-op).
- REQ-011: A feat folder whose implementation merged under a branch name different from the folder id is still found by the gate: when the exact head-ref lookup (REQ-001) returns no merged PR, the gate falls back to merged PRs whose head ref starts with the folder's `feat-<NNN>-` issue-number prefix (the closed-PR page scan is fetched once per precheck run and reused across folders; `feat-0-*` folders have no issue number and stay exact-match only), and the newest by `merged_at` across the exact and fallback matches is the delivery, to which REQ-002 and REQ-003 apply. Motivating instance: folder `feat-134-related-artifact-similarity`, whose work merged from both `feat-134-related-artifact-similarity` (PR #137) and the renamed branch `feat-134-similarity-requires-mcp` (PR #168).

### Acceptance Criteria

- [x] ACC-001: With a fixture repo carrying a feat folder at `status: review` whose head ref has a merged PR with `merge_commit_sha` inside `vPrev..HEAD`, `stage_precheck` exits non-zero and its output names the feat, its status, the PR number, and the delivery sha (REQ-001).
- [x] ACC-002: The same fixture with the feat at `status: done`, and a fixture with a plan-only feat (no merged PR for its head ref) at any status, both pass the closeout gate (REQ-001, REQ-002).
- [x] ACC-003: A feat whose newest merged-PR delivery commit is an ancestor of `vPrev` passes the closeout gate even at `status: review` (REQ-003).
- [x] ACC-004: With a local and `origin/` `feat-*` branch (matching tips) whose delivery commit is an ancestor of `vPrev`, the cleanup deletes both refs: the local deletion attempts `git branch -d` and succeeds via the `-D` fallback when `-d` refuses because the squash-merged head is not an ancestor of the current branch, and the remote deletion uses `git push origin --delete` (REQ-004).
- [x] ACC-005: Each of the four guard classes (worktree-checked-out; no merged PR; in-window delivery; local≠origin tips) produces a keep/skip report line and leaves the ref(s) intact (REQ-005).
- [x] ACC-006: `precheck ... --dry-run` prints the full would-delete/would-keep table and leaves every ref intact, and a precheck that fails the closeout gate mutates no ref (REQ-006).
- [x] ACC-007: Re-running `precheck` after a successful cleanup reports nothing to delete, and after the closeout remediation passes (REQ-007).
- [x] ACC-008: The SOP's step 2, Definitions, Safety and Precautions, and a dated Updates entry describe both sub-items, and the SOP remains parseable (`parse_sop` green) (REQ-008).
- [x] ACC-009: The `scripts/release.sh` header/usage, `/release` command, and README "Make a Release" section all describe the two new sub-items and the closeout-remediation loop (REQ-009).
- [x] ACC-010: `tests/test_release_sh.py` gains the gate and cleanup cases listed in REQ-010 and the full suite (`uv run --frozen pytest -n auto`) passes, with `ruff format --check`, `ruff check`, and `vulture` staying clean (REQ-010).
- [x] ACC-011: A feat folder at `status: review` whose work merged only under a differently-named `feat-<NNN>-*` branch (no merged PR for the exact head ref) is still gated via the issue-number-prefix fallback (REQ-011).

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

- The existing `tests/test_release_sh.py` fake-`gh`-shim harness and the script's `BASH_SOURCE` dispatch guard (both landed with feat-213-release) — the new tests extend that harness rather than introducing a new one. The extension is scoped work (Task 100.115): the harness's fake `gh` was built to simulate closing a PR and reading its state, not to answer the `pulls?state=closed&head=...` search call (and the REQ-011 page scan) the gate and cleanup lookups issue, so the shim must learn those endpoints before the gate's and cleanup's test cases can run.

#### Blocks

- Nothing. This feature is additive to the release precheck and does not gate any other in-flight feature.

### Design Notes

**Why `precheck` and not a new stage.** The maintainer placed Rule 1 in `precheck` because it must hold *before* the version increment is written to `pyproject.toml` (`stage_bump` is the first mutating stage after `precheck`), and placed Rule 2 in `precheck` because the latest tag is unambiguous there (`vPrev` is simply `git describe --tags --abbrev=0` — the release being cut has no tag yet, which precheck's existing check (d) already asserts). Folding both into `precheck` keeps the stage/step 1:1 mapping intact and avoids SOP step renumbering. The consequence that `stage_all` (the non-agent path) inherits the cleanup is accepted and recorded in the issue.

**Delivery commit via `merge_commit_sha`, not the head SHA.** A squash-merged feat branch leaves *no* head-SHA ancestor on `dev` (the head commits are rewritten), so `git merge-base --is-ancestor <head> dev` is the wrong staleness test for the majority of this repo's features. GitHub's `merge_commit_sha` is the real `dev`-side commit for both squash and merge PRs, so "stale" and "shipped-in-window" reduce to two ancestry tests against that one SHA: ancestor of `vPrev` (stale, delete) vs. ancestor of `HEAD` but not of `vPrev` (current release, keep).

**GitHub REST, not GraphQL.** The script is written against this environment's `gh` 2.4.0, whose GraphQL call sites (`gh pr view --json`, `gh run view --json jobs`) are known-broken (SOP Safety and Precautions). The merged-PR lookup therefore uses `gh api "repos/{owner}/{repo}/pulls?state=closed&head={owner}:<ref>&per_page=100"` filtered with `jq` for `merged_at != null`, taking the newest by `merged_at` — the same REST precedent the script already uses for `close_pr_if_open` and the release notes.

**The issue-number-prefix fallback (REQ-011).** The gate's primary lookup keys on head ref = the folder id, which assumes the implementation branch was named after the folder. The assumption has broken in this repo: folder `feat-134-related-artifact-similarity` shipped from two branches — `feat-134-related-artifact-similarity` (PR #137, merged 2026-09-29) and the renamed `feat-134-similarity-requires-mcp` (PR #168, same day) — and a folder whose only merged PR came from a differently-named branch would otherwise look plan-only and slip past the gate (REQ-002), the exact false negative the gate exists to prevent. The fallback matches merged PRs by the folder's `feat-<NNN>-` prefix (issue numbers are unique per folder; `feat-0-*` has none), fetched in one page scan of closed PRs per precheck run so the cost is constant rather than per-folder, and takes the newest by `merged_at` across exact and fallback matches.

**The four cleanup guards, and where each came from.** (a) Worktree-checked-out: a branch checked out in a worktree cannot be deleted and represents live work (the manual pass's feat-139, still checked out in its worktree as of 2026-10-24). (b) No merged PR: in-flight or abandoned work the maintainer may still want (the manual pass's remote-only branches `feat-46-remove-adr` and `feat-63-refine` — no feature folder on disk and no merged PR for either head ref, both still on `origin` as of 2026-10-24). (c) In-window delivery: the current release's branches stay one cycle (the manual pass kept every v0.37.0 branch). (d) Local≠origin tips: the two sides may carry different content, so neither is provably stale (the manual pass's feat-134/feat-144 pairs; both branches since deleted, their merged PRs #137 and #147 on record). Guards are evaluated per branch in the order (a)→(d) and the first guard that fires wins, emitting exactly one report line naming the branch and that guard — feat-139 is both worktree-checked-out and no-merged-PR, and it reports under (a) only. Each guard is a keep/skip with a report line, never a silent skip.

**Gate ordering is a safety property.** The closeout gate runs before the cleanup so a gate failure stops the precheck with zero ref mutations (REQ-006/ACC-006). This is pinned by a dedicated test, not just by code order.

### Related Decisions

- SOP 98537416-0e6e-4a02-925f-974a17bfa10a ("Perform a release of biz.dfch.SpecMgr") — the normative procedure this feature amends (step 2, Definitions, Safety and Precautions, Updates).
- feat-213-release (`.specmgr/feat/feat-213-release/README.md`, GitHub issue #213) — the release-script hardening precedent that established `tests/test_release_sh.py`'s fake-`gh`-shim harness and the `BASH_SOURCE` dispatch guard this feature's tests extend.
- The 2026-10-23 manual closeout commits `b5cd89c` (feat-129) and `4a33271` (feat-214) — the concrete gap Rule 1 closes; the feat-closeout shape (status → `done` + a "Finalization" Updates entry recording the PR merge) they establish is the remediation the gate's actionable message points at.

### Task List

#### Phase 100: Closeout gate in `stage_precheck`

- [x] Task 100.100: Add the helper functions the gate needs: `latest_tag()` (`git describe --tags --abbrev=0`, empty + info note when no tag exists — the gate then treats the window as `HEAD`), `feat_folders()` (list `.specmgr/feat/feat-*/` ids), `feat_status(<id>)` (read the frontmatter `status:` line; a missing or unparseable value is a distinct sentinel the gate turns into its own violation line), and `merged_delivery(<head-ref>)` (`gh api pulls?state=closed&head=...` + `jq` filter for `merged_at != null`, newest by `merged_at`, printing `number<TAB>merged_at<TAB>merge_commit_sha` or nothing).
- [x] Task 100.110: Wire the gate into `stage_precheck` after the six existing checks (a)–(f) documented in SOP 98537416 step 2: for each feat folder whose `status` is not `done` (a missing or unparseable `status` line is a violation on its own, reported before any PR lookup), look up its merged delivery (exact head ref first, then the REQ-011 `feat-<NNN>-` prefix fallback); if found and the delivery SHA is an ancestor of `HEAD` but not of `vPrev` (with `vPrev` absent, every delivery counts), record it as a violation; after the loop, if there are violations, `die` with one actionable line per offending feat (id, status or frontmatter defect, PR number, sha) plus the remediation pointer (close out to `done` on `dev`, or repair the frontmatter, then re-run `precheck`).
- [x] Task 100.115: Extend the fake `gh` shim in `tests/test_release_sh.py` to answer the merged-PR search call `repos/{owner}/{repo}/pulls?state=closed&head={owner}:<ref>&per_page=100` (and, once the REQ-011 fallback lands, the one-shot page scan of closed PRs): the shim's configured PR fixtures carry `number`, `head.ref`, `merged_at`, and `merge_commit_sha`, so the gate and cleanup tests can assert per-branch merged and unmerged delivery.
- [x] Task 100.120: Add the gate's `tests/test_release_sh.py` cases (ACC-001, ACC-002, ACC-003, ACC-011): review-status feat with an in-window merged PR ⇒ precheck dies naming the feat; the same feat at `done` ⇒ passes; plan-only feat (no merged PR) ⇒ passes; feat delivered in an earlier release ⇒ passes; feat folder with a missing or unparseable `status` ⇒ precheck dies with the frontmatter-defect line; feat merged only under a renamed `feat-<NNN>-*` branch ⇒ gated via the prefix fallback; no prior tag ⇒ the window is `HEAD` (an in-window review-status feat ⇒ dies).

#### Phase 110: Previous-release branch cleanup in `stage_precheck`

- [x] Task 110.100: Add the cleanup helpers: `cleanup_candidates()` (local + `origin/` `feat-*`/`fix/*` branch names, excluding `dev`/`main`), `worktree_branches()` (from `git worktree list --porcelain`), and `branch_delivery(<name>)` (the same `merged_delivery` lookup keyed on the branch's head ref).
- [x] Task 110.110: Implement the cleanup loop in `stage_precheck` after the gate: for each candidate name, apply the guards in order — (a) worktree-checked-out → skip, (b) no merged delivery → keep, (c) delivery inside `vPrev..HEAD` → keep, (d) the branch exists on both sides with local tip ≠ origin tip → skip both — the first guard that fires wins and emits exactly one report line; otherwise delete each side that exists (the local ref via `git branch -d` with the `-D` fallback, the `origin/` ref via `git push origin --delete <name>`; a one-side branch deletes and reports on its side alone); under `DRY_RUN=1` print the would-delete/would-keep table and mutate nothing. Every keep/skip/delete emits a report line naming the branch, the guard that fired (if any), and the side(s) affected.
- [x] Task 110.120: Add the cleanup's `tests/test_release_sh.py` cases (ACC-004, ACC-005, ACC-006, ACC-007): matching-tip branch delivered ≤ vPrev ⇒ both refs deleted, the local side via the `-D` fallback when `-d` refuses the squash-merged head; local-only or remote-only branch ⇒ deleted on the side that exists with a one-side report line; each of the four guards ⇒ ref(s) intact with exactly one report line naming the guard that fired; `--dry-run` ⇒ table printed, no mutation; gate failure ⇒ no cleanup mutation; re-run after cleanup ⇒ nothing to delete.

#### Phase 120: Documentation sync (SOP, script header, `/release`, README)

- [x] Task 120.100: Update `scripts/release.sh`'s header/usage comment so the `precheck` line names the two new sub-items (feat closeout gate, previous-release branch cleanup) and the `--dry-run` note covers the cleanup's report-only mode.
- [x] Task 120.110: Update SOP 98537416: step 2 gains the two sub-items in their run order (the gate sub-item recording the no-prior-tag window = `HEAD` and the unparseable-`status` fail-safe; the cleanup sub-item recording one-side deletion and first-guard-wins reporting), `Definitions` gains *delivery commit*, *stale branch*, and *issue-number prefix*, `Safety and Precautions` gains an entry recording that the cleanup is the only mutating precheck sub-item and why the merged-PR proof + four guards make that safe, and a dated `Updates` entry describes the change; confirm `parse_sop` stays green.
- [x] Task 120.120: Sync `.opencode/command/release.md` and the README "Make a Release" section to describe the two sub-items and the closeout-remediation loop (gate fails → close out the named feats to `done` on `dev` → commit → re-run `precheck`).

#### Phase 130: Verification and closeout

- [x] Task 130.100: Run the full quality gate — `uv run --frozen pytest -n auto` (the `test_release_sh.py` cases green), `ruff format --check`, `ruff check`, and `vulture src/ whitelist.py --min-confidence 60` — and confirm ACC-001 through ACC-010 are each evidenced by a named test or a named doc surface.
- [x] Task 130.110: Close out — tick the verified acceptance criteria, set the plan status to `review`, and add the `CHANGELOG.md` `[Unreleased]` entry describing the two new precheck sub-items.

#### Phase 140: Review remediation (PR #236 post-implementation review)

- [x] Task 140.100: Fix the reviewed code findings in scripts/release.sh — E1/I1 (reuse the one-shot origin listing for per-candidate tips), G1 (explicit gate line for an unresolvable delivery), I4 (feat_status tolerates quoted/trailing-comment values), I6 (side-aware push-delete failure message).
- [x] Task 140.110: Fix the reviewed test findings in tests/test_release_sh.py — the G1 gate case, the I4 quoted-status case, I5 (adversarial head-filter pin in the plan-only test), I9 (module docstring).
- [x] Task 140.120: Fix the reviewed doc findings — D1 (/release dry-run paragraph), G2 (SOP: record the one-page fallback bound), D3 (SOP: 'latest tag' wording), I8 (split the CHANGELOG bullet into two).

#### Phase 150: Independent review closeout (plan-text corrections, test gaps, deferrals)

- [x] Task 150.100: Fix the reviewed plan-text findings — D1 (the slash-form head filter `head=<owner>/<feat-id>` and the hard-coded `repos/dfch/biz.dfch.SpecMgr` in REQ-001, the Design Notes "GitHub REST, not GraphQL" bullet, and Task 100.115's text → the implemented colon form `head={owner}:<ref>` with the `{owner}/{repo}` placeholder, matching the Phase 100 Decisions entry (1)) and D2 (Task 100.100's `merged_delivery` print shape, the two-field sketch → the implemented three-column form `number<TAB>merged_at<TAB>merge_commit_sha`, matching the Phase 100 Decisions entry (2)).
- [x] Task 150.110: Cover the `fix/*` branch class in `tests/test_release_sh.py` — a stale `fix/<name>` branch on both the local and the `origin/` side (matching tips, delivery an ancestor of `vPrev`, the existing `commit-tree` fixture shape) is deleted on both sides with the report lines naming the slash-containing branch (G1).
- [x] Task 150.120: Pin the local-delete clean-merge success path — a branch whose tip is a genuine ancestor of dev (the `v0.9.8`-tagged fixture commit) with a merged-PR delivery equal to it is deleted locally via plain `git branch -d` (the report line carries the plain `-d` mechanic, not the `-D`-refusal wording) and on origin via `git push origin --delete` (G2).
- [x] Task 150.130: Record the independent review in Progress — a Decisions-Made entry covering the D1/D2 plan-text corrections, the G1/G2 test additions, and the I1/I2 deferrals with their rationale; a dated Recent Updates entry for Phase 150 completion carrying the phase-end gate evidence; the Current Status paragraph updated (all six phases complete; the plan status stays `review` — the final closeout to `done` is post-merge and is enforced by this feature's own gate at the next release's precheck).

## Progress

### Current Status

**As of 2026-10-24**: All six phases complete — Phase 100 (the closeout
gate in `stage_precheck`), 110 (the previous-release branch cleanup), 120
(the documentation sync), 130 (verification and closeout), 140 (review
remediation of the PR #236 post-implementation findings), and 150
(independent review closeout). An independent post-implementation review
verdict: **no errors** — every requirement REQ-001…REQ-011 implemented,
all 11 acceptance criteria re-verified, and the full quality gate
independently re-run and green; its actionable findings are all
dispositioned in Phase 150 (plan text and tests only, no
`scripts/release.sh` behaviour change): D1/D2 corrected the three
stale slash-form head-filter occurrences and Task 100.100's two-field
delivery sketch to the implemented colon-form `head={owner}:<ref>`
lookup and three-column `merged_delivery` line, G1 added the
`fix/*` branch-class cleanup test, and G2 pinned the local-delete
clean-merge plain-`git branch -d` success path; I1 (the PID-keyed
per-run cache files) and I2 (the unpatterned `latest_tag`) are deferred
with rationale (see Decisions Made). The full quality gate is green
(the Phase 150 Updates entry below carries the refreshed evidence):
`uv run --frozen pytest -n auto` 4825 passed / 18 skipped,
`ruff format --check`, `ruff check`, and `vulture src/ whitelist.py
--min-confidence 60` all clean, and `tests/test_release_sh.py` alone runs
97/97; every acceptance criterion ACC-001…ACC-011 is evidenced by a named
test or a named doc surface (the evidence table in the Phase 130 Updates
entry below; the Task 130.100 text's "ACC-001 through ACC-010" is a wording
gap against the plan's 11 criteria — see Decisions Made), and the
`CHANGELOG.md` `[Unreleased]` entry (two bullets, one per sub-item) is in
place. The plan status stays `review` — the final closeout (status →
`done` + finalization entry) happens only after the PR merges into
`dev`, and this feature's own gate will then enforce exactly that at the
next release's precheck.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-24T23:29:29.223+02:00 - Phase 150 complete (independent review closeout)

Implemented the independent post-implementation review closeout (Tasks
150.100/150.110/150.120/150.130). The independent `feat-reviewer` pass
over `dev..HEAD` returned the verdict **no errors** — every requirement
REQ-001…REQ-011 implemented, all 11 acceptance criteria re-verified, and
the full quality gate independently re-run and green — with two stale
plan-text findings (D1, D2), two test gaps (G1, G2), and two hardening
notes (I1, I2) this phase disposes of; plan text and tests only, no
`scripts/release.sh` behaviour change. **D1**: the three stale slash-form
occurrences of the merged-PR head filter — REQ-001's
`pulls?state=closed&head=<owner>/<feat-id>`, the Design Notes "GitHub
REST, not GraphQL" bullet's hard-coded `gh api
"repos/dfch/biz.dfch.SpecMgr/pulls?state=closed&head=dfch/<feat-id>"`,
and Task 100.115's `pulls?state=closed&head=<owner>/<ref>` — are
corrected to the implemented documented `user:ref` COLON form with the
`{owner}/{repo}` placeholder
(`repos/{owner}/{repo}/pulls?state=closed&head={owner}:<ref>&per_page=100`),
matching the Phase 100 Decisions entry (1) adjudication (the slash form
was tested live and is silently ignored by the API); the elided `head=...`
fragments on the Depends-On and Task 100.100 lines assert no form and are
left alone. **D2**: Task 100.100's two-field `merged_delivery` print
shape (`number<TAB>merge_commit_sha`) is corrected to the implemented
three-column form (`number<TAB>merged_at<TAB>merge_commit_sha`), matching
the Phase 100 Decisions entry (2); the rest of the task line is untouched.
**G1**: `ReleaseShBranchCleanupTestCase` gains
`test_precheck_cleanup_deletes_stale_fix_slash_branch` — the `fix/*`
branch class is now exercised: a stale `fix/233-release-precheck` branch
on BOTH the local and the `origin/` side (matching tips, the existing
`commit-tree` squash-stand-in shape, the merged-PR delivery an ancestor of
`vPrev`) is deleted on both sides, the slash-containing name carried
through the remote-candidate filter and the local candidate union, the
local `git branch -d`→`-D` mechanic, and `git push origin --delete`, with
both report lines naming that name and proven by the merged PR. **G2**:
the class also gains
`test_precheck_cleanup_deletes_stale_clean_merge_plain_d` — the
local-delete clean-merge SUCCESS path is pinned: a branch whose tip IS a
genuine ancestor of dev (the `v0.9.8`-tagged first fixture commit, with a
merged-PR delivery equal to it, hence stale) is deleted locally via PLAIN
`git branch -d` (the report line carries the plain `-d` mechanic, and the
`-D`-refusal wording is asserted absent) and on origin via `git push
origin --delete`. **I1/I2**: deferred with rationale (recorded in the
Decisions entry below). The new Phase 150 section (Tasks 150.100–150.130)
is added to the Task List with all four tasks ticked. Gate evidence:
`uv run --frozen pytest tests/test_release_sh.py -n auto -q` 97 passed
(the 95 pre-existing runs plus the 2 new cleanup cases); `uv run
--frozen pytest -n auto -q` 4825 passed / 18 skipped; `uv run --frozen
ruff format --check` (2114 files already formatted); `uv run --frozen
ruff check` (all checks passed); `uv run --frozen vulture src/
whitelist.py --min-confidence 60` clean; `bash -n scripts/release.sh`
clean; `bash scripts/release.sh help` rc 2 with the complete usage (final
`full resolved version.` line); specmgr `parse_sop` green (the SOP is
unchanged this phase); specmgr `get_feat` green (the plan parses with the
new phase). The plan status stays `review`.

#### 2026-10-24T21:11:46.739+02:00 - Phase 140 complete (review remediation)

Implemented the PR #236 post-implementation review remediation (Tasks
140.100/140.110/140.120) — no plan or design change, the five reviewed code
fixes plus their tests and doc sync. `scripts/release.sh`: **E1/I1** — the
cleanup's per-candidate `git ls-remote` re-fetch is replaced by the script's
PID-keyed per-run cache idiom (new `origin_branches_cache_path` /
`origin_branches` / `origin_branch_tip`; the one-shot `git ls-remote --heads
origin` is fetched once where `cleanup_candidates` previously did, a failed
fetch still `die`s with the existing message, `cleanup_candidates` filters
the cache, and the same two `stage_precheck` rm/trap lines now cover both
per-run caches), removing E1's surface (a transient per-candidate network
failure can no longer exit the precheck with only git's raw stderr);
**G1** — the gate's outer ancestry test's empty else now prints an explicit
not-gated info line naming the feat, the PR number, and the short sha
("not an ancestor of HEAD" plus "nor of `$vprev`" only when a prior tag
exists, and the manual-verify pointer), mirroring the cleanup's fail-safe
keep and not a violation; **I4** — `feat_status`'s awk now strips a trailing
YAML comment (whitespace before `#`) and one pair of surrounding matching
single/double quotes before the closed-set check, so `status: 'done'` and
`status: planning # note` are no longer false-positive defects; **I6** — the
`git push origin --delete` failure `die` is side-aware ("the local ref was
already deleted" only when a local side existed, otherwise "the branch was
origin-side only (no local ref)"). `tests/test_release_sh.py`: the **G1**
gate case in `ReleaseShCloseoutGateTestCase`
(`test_precheck_gate_unresolvable_delivery_not_gated` — a commit-tree side
commit that is an ancestor of neither vPrev nor HEAD, full precheck rc 0,
the explicit line on stdout, no gate violation), the **I4** cases
(`test_precheck_gate_tolerates_quoted_and_commented_status` — a `'done'`
feat and a trailing-comment `planning # note` feat both pass, the in-window
merged PR on the first's head ref included;
`test_precheck_gate_tolerates_quoted_review_status` — a quoted `'review'` is
gated with the ordinary violation line, never the defect line), **I5** — the
plan-only test now seeds one extra unrelated in-window merged PR
(`feat-99-unrelated`) the exact head-ref lookup must exclude (a regression
to the broken whole-page-return shape would gate the plan-only feat and fail
it), and **I9** — the module docstring records the full-`stage_precheck`
coverage since feat-233, naming both test classes. Docs: **D1** — the
`/release` command's dry-run paragraph now says `precheck --dry-run` (the
cleanup is report-only under `--dry-run`, so the "never push" promise holds
again); **G2 + D3** — SOP 98537416 step 2 (g) records the fallback's bound
(a single `per_page=100` page of the most recently closed PRs, fetched once
per precheck run, constant cost — a renamed-branch delivery merged beyond
that page is outside the fallback's reach) and drops the over-promising
"release" from the `vPrev` definition (now "the latest tag reachable from
`dev` (`git describe --tags --abbrev=0`)") and the *Stale branch* definition
("an ancestor of the latest tag (`vPrev`)"); **I8** — the single ~35-line
CHANGELOG bullet is split into two self-contained bullets under the same
`### Changed` (one for the closeout gate, one for the branch cleanup — same
behaviour facts, the one-page fallback bound included, no internal
test-class names, each ending with the feat/issue reference). Gate evidence:
`uv run --frozen pytest -n auto --cov=src --cov-report=` 4823 passed / 18
skipped; `uv run --frozen pytest tests/test_release_sh.py -n auto -q` 95
passed (the 89 pre-existing runs plus the 3 new gate cases, which the
cleanup class inherits — +6 runs); `uv run --frozen ruff format --check`
(2114 files already formatted); `uv run --frozen ruff check` (all checks
passed); `uv run --frozen vulture src/ whitelist.py --min-confidence 60`
clean; `bash -n scripts/release.sh` clean; `bash scripts/release.sh help`
rc 2 with the complete usage (final `full resolved version.` line); specmgr
`parse_sop` green; specmgr `get_feat` green. Deferred without change: I2,
I3, I7 (rationale in Decisions Made).

#### 2026-10-24T18:26:40.571+02:00 - Phase 130 complete

Ran the full quality gate and closed out the feature (Tasks 130.100/
130.110). Gate evidence: `uv run --frozen pytest -n auto` — 4817 passed /
18 skipped; `uv run --frozen ruff format --check` — 2114 files already
formatted; `uv run --frozen ruff check` — all checks passed; `uv run
--frozen vulture src/ whitelist.py --min-confidence 60` — clean.
`tests/test_release_sh.py` alone: 89/89, including the 9 closeout-gate
cases (`test_precheck_gate_*`) in `ReleaseShCloseoutGateTestCase` and the
12 branch-cleanup cases (`test_precheck_cleanup_*`) in
`ReleaseShBranchCleanupTestCase` (plus the pre-existing harness cases
inherited from `ReleaseShGateTestCase`). Every acceptance criterion is
evidenced by a named test or a named doc surface — the Task 130.100 text
says "ACC-001 through ACC-010", but the plan carries 11 criteria (ACC-011
was added by the refinement pass with REQ-011 and the task text was not
updated), so all 11 are verified (see Decisions Made):

| ACC | Evidence | Verified |
| --- | --- | --- |
| ACC-001 | `tests/test_release_sh.py::ReleaseShCloseoutGateTestCase::test_precheck_gate_dies_for_review_feat_shipped_in_window` | yes |
| ACC-002 | `ReleaseShCloseoutGateTestCase::test_precheck_gate_passes_for_done_feat` + `..._passes_for_plan_only_feat` | yes |
| ACC-003 | `ReleaseShCloseoutGateTestCase::test_precheck_gate_passes_for_feat_delivered_before_prev_tag` | yes |
| ACC-004 | `ReleaseShBranchCleanupTestCase::test_precheck_cleanup_deletes_stale_both_sides` | yes |
| ACC-005 | `ReleaseShBranchCleanupTestCase::test_precheck_cleanup_guard_a_worktree_checked_out` / `..._guard_b_no_merged_pr` / `..._guard_c_in_window_delivery` / `..._guard_d_tips_differ` | yes |
| ACC-006 | `ReleaseShBranchCleanupTestCase::test_precheck_cleanup_dry_run_mutates_nothing` + `test_precheck_gate_failure_precedes_cleanup_mutation` | yes |
| ACC-007 | `ReleaseShBranchCleanupTestCase::test_precheck_cleanup_second_run_reports_nothing_to_delete` | yes |
| ACC-008 | SOP 98537416 step 2 sub-items (g)/(h), Definitions (*delivery commit*, *stale branch*, *issue-number prefix*), the Safety-and-Precautions entry, the dated 2026-10-24 17:56:57 Updates entry — `parse_sop` green | yes |
| ACC-009 | `bash scripts/release.sh help` (the `precheck` usage line + the `--dry-run` note), `.opencode/command/release.md` step 3, the README "Make a Release" note after the usage block | yes |
| ACC-010 | the gate + cleanup test cases above (89/89 in `tests/test_release_sh.py`) + the full-suite/lint gate evidence above | yes |
| ACC-011 | `ReleaseShCloseoutGateTestCase::test_precheck_gate_prefix_fallback_gates_renamed_branch` | yes |

Bookkeeping: all 11 acceptance criteria ticked, Tasks 130.100/130.110
ticked, the plan status set to `review` via the specmgr `set_status` tool,
and the `CHANGELOG.md` `[Unreleased]` `### Changed` entry added describing
the two new precheck sub-items, the synced doc surfaces, and the
`tests/test_release_sh.py` coverage (the wording-discrepancy and the
changelog-category choice are recorded in Decisions Made).

#### 2026-10-24T18:08:43.525+02:00 - Phase 120 complete

Implemented the documentation sync (Tasks 120.100/120.110/120.120) — no code
behaviour change: the only `scripts/release.sh` diff is the header/usage
comment (the `precheck` line now names the feat closeout gate and the
previous-release branch cleanup, and a new `--dry-run` note covers the
cleanup's report-only mode) plus `usage()`'s sed range recomputed from `2,34p`
to `2,43p` (the inserted comment lines shifted the `# full resolved version.`
line down; `test_help_prints_full_usage` pins the complete output). SOP
98537416, edited through the generic `edit` tool (each pass re-parsed the
document and bumped `updated`): step 2's *Automated* paragraph gains sub-items
(g) and (h) in run order — the gate (the window `vPrev..HEAD`, the
no-prior-tag window `HEAD`, the newest-merged-PR delivery via the exact head
ref plus the `feat-<NNN>-` prefix fallback, one actionable line per offending
feat plus the remediation pointer, the missing/unparseable-`status` fail-safe,
the never-gated classes) and the cleanup (the per-side independent deletions,
`git branch -d` → the `-D` fallback justified by the merged-PR proof, `git push
origin --delete`, the one-side reporting, the four guards first-fires-wins with
exactly one report line, the unresolvable-delivery fail-safe keep, `--dry-run`
report-only, the no-prior-tag skip, and the gate-first zero-ref-mutation
property) — and its *Manual fallback* paragraph names how both sub-items reduce
by hand; Definitions gains *delivery commit*, *stale branch*, and *issue-number
prefix*; Safety and Precautions records that the branch cleanup is the only
mutating precheck sub-item and why the merged-PR proof plus the four guards
make that safe; a dated Updates entry (2026-10-24 17:56:57) describes the
change, citing the 2026-10-23 manual cleanup (the stale branches deleted by
hand, the feat-129/feat-214 closeouts, commits `b5cd89c`/`4a33271`) as the gap
it closes; `parse_sop` green. `.opencode/command/release.md` step 3 names both
sub-items and the closeout-remediation loop (gate fails → close out the named
feats to `done` on `dev` — frontmatter edit plus a finalization entry recording
the PR merge — commit → re-run `precheck`; the cleanup runs only after the gate
passes, so a gate failure mutates no branch; `--dry-run` = the
would-delete/would-keep table). The README "Make a Release" usage-block comment
on the `precheck` line names both sub-items (block alignment preserved) and a
note directly after the block describes the gate, the remediation loop, and the
cleanup's merged-PR proof + four guards + `--dry-run` report-only mode.
Phase-end gate: `bash -n` clean, `help` rc 2 with the full usage (final `full
resolved version.` line), `ruff format --check` / `ruff check` / `vulture`
clean, `pytest tests/test_release_sh.py -n auto` 89/89, full suite 4817 passed
/ 18 skipped, `parse_sop` green.

#### 2026-10-24T17:20:28.288+02:00 - Phase 110 complete

Implemented the previous-release branch cleanup in `stage_precheck` (Tasks
110.100/110.110/110.120). `scripts/release.sh` gains the cleanup helpers —
`cleanup_candidates` (the union of every local branch name and origin's
`refs/heads/feat-*`/`refs/heads/fix/*` names, deduped and sorted, excluding
`dev`/`main`; a failed `ls-remote` dies fail-fast rather than degrading to the
local set), `worktree_branches` (the `branch refs/heads/<name>` lines of `git
worktree list --porcelain`, all worktrees incl. the main one), and
`branch_delivery` (a thin exact-lookup-only wrapper over `merged_delivery` keyed
on the branch name — the REQ-011 prefix fallback is gate-only) — and the cleanup
loop, wired after the closeout gate and before the final pass line: no previous
tag ⇒ one skip note, no loop, no mutation; an empty candidate set ⇒ the "nothing
to delete" note; otherwise, per candidate, the guards (a)→(d) in order (first
fires wins, exactly one line: worktree-checked-out / no merged PR / in-window
delivery / local≠origin tips), the unresolvable-delivery fail-safe keep (a
delivery that is an ancestor of neither `vPrev` nor `HEAD`), and — for a stale
candidate (delivery an ancestor of `vPrev`) — the per-side deletions, local
first (`git branch -d`, the `-D` fallback on the expected squash-merge refusal, a
still-failing delete `die`s fail-fast) then `git push origin --delete`, each side
reported independently with the `proven stale by PR #<n>, delivery <sha12> ≤
<vprev>` proof, a one-side marker when only one side exists, and a trailing
`<N> branch(es) deleted, <M> kept/skipped` summary (under `DRY_RUN=1` the delete
lines read `would delete …`, nothing is mutated, and the summary reads
`[dry-run] … would be deleted`). `tests/test_release_sh.py` gains
`ReleaseShBranchCleanupTestCase` (full `stage_precheck 0.9.9` runs over the gate's
fixture repo, branches created after the build via `git commit-tree` + `git
branch`/`git push origin <sha>:refs/heads/<n>`/`git worktree add` without
switching off dev): ACC-004 (a stale matching-tip branch deleted on both sides,
the local via the `-D` fallback), the REQ-004 one-side deletions (local-only and
origin-only, each reported with the side marker), ACC-005 one test per guard
(the guard-(a) test's branch is worktree-checked-out AND carries a stale merged
PR — it reports under guard (a) only, first-guard-wins — plus no-merged-PR,
in-window delivery, and local≠origin tips), the unresolvable-delivery fail-safe
keep, ACC-006 (the dry-run would-delete table with no mutation, and a gate
failure dying before any cleanup report line or mutation), ACC-007 (a second full
precheck over the same repo reports nothing to delete), and the no-previous-tag
skip. Phase-end gate: `ruff format --check` / `ruff check` / `vulture` clean,
`bash -n scripts/release.sh` clean, `pytest tests/test_release_sh.py -n auto`
89/89, full suite 4817 passed / 18 skipped.

#### 2026-10-24T15:41:54.052+02:00 - Phase 100 complete

Implemented the feat closeout gate in `stage_precheck` (Tasks 100.100/100.110/
100.115/100.120). `scripts/release.sh` gains the gate helpers — `latest_tag`
(`git describe --tags --abbrev=0`, empty when no tag is reachable; the caller
emits the window-is-`HEAD` info note), `feat_folders` (the `.specmgr/feat/
feat-*/` ids, sorted), `feat_status` (the frontmatter `status:` value, the
`FEAT_STATUS_UNPARSEABLE` sentinel for a missing/empty/out-of-set line),
`merged_delivery` (the exact head-ref search, newest by `merged_at`, printing
`number<TAB>merged_at<TAB>merge_commit_sha`), and `closed_pr_scan` (the one-shot
`per_page=100` page scan for the REQ-011 prefix fallback, parsed lines cached in
a PID-keyed per-run file) — and the gate itself, wired after the six existing
precheck checks: every non-`done` feat folder whose newest merged delivery (exact
match and fallback combined) is an ancestor of `HEAD` but not of `vPrev` (every
delivery when `vPrev` is absent) dies the precheck with one actionable line per
offending feat (id, status or frontmatter defect, PR number, full delivery sha)
plus the remediation pointer; a missing/unparseable `status:` line is a
violation on its own, reported before any PR lookup. `tests/test_release_sh.py`'s
fake `gh` now answers both search endpoints from a `pulls_closed.json` fixture
(PR objects carry `number`, `head.ref`, `merged_at`, `merge_commit_sha`), and the
new `ReleaseShCloseoutGateTestCase` (with a `main` branch + `v0.9.8` tag +
in-window commits, a green `lint_test_run` fixture, and a fake `uv` shim) runs
the full `stage_precheck 0.9.9`: ACC-001 (review feat with an in-window merged
PR dies, naming feat/status/PR/sha), ACC-002 (`done` passes; plan-only passes),
ACC-003 (delivery an ancestor of `vPrev` passes at `review`), ACC-011 (merged
only under a renamed `feat-<NNN>-*` branch is gated via the prefix fallback, the
page scan fetched exactly once per run), the newest-by-`merged_at`-across-exact-
and-fallback delivery choice (PR #168 wins over #137), the missing- and
out-of-set-`status` defect cases (no PR lookup for the offending folder), and
the no-prior-tag window-is-`HEAD` case. Phase-end gate: `ruff format --check` /
`ruff check` / `vulture` clean, `bash -n scripts/release.sh` clean,
`pytest tests/test_release_sh.py -n auto` 54/54, full suite 4782 passed /
18 skipped.

#### 2026-10-24T14:09:57.499+02:00 - Plan refined

Applied a refinement pass (findings G1–G4, D1–D4, I1–I4): specified the no-prior-tag
first-release behavior for gate (window = `HEAD`) and cleanup (no deletion, reported
skip) (G1), the missing/unparseable-`status` fail-safe (G2), an explicit fake-`gh`-shim
extension task (G3, Task 100.115), and the issue-number-prefix fallback for feats merged
under a renamed branch (G4, REQ-011/ACC-011 — verified against PR #137 and PR #168, both
merged from branches of folder `feat-134-related-artifact-similarity`); corrected ACC-004
to the `-d` attempt → `-D` fallback the squash-merge strategy requires (D1), aligned the
Overview's hazard enumeration with guards (a)–(d) (D2), and replaced the guard-(b)
examples with the verified no-merged-PR, no-folder remote-only branches `feat-46-remove-adr`
and `feat-63-refine` (D3, D4); made the six SOP checks (a)–(f) explicit (I1), clarified the
`planning` vs. `review` status semantics (I2), one-side deletion (I3), and first-guard-wins
reporting (I4).

#### 2026-10-24T11:39:24.997+02:00 - Created

Drafted the feature plan from GitHub issue #233, grounded in the 2026-10-23 manual
branch/record cleanup (the stale-branch attribution work, the four cleanup hazard classes,
and the feat-129/feat-214 closeout commits `b5cd89c`/`4a33271`) and a read of
`scripts/release.sh`'s `stage_precheck`, the SOP 98537416 procedure, and the
`tests/test_release_sh.py` fake-`gh`-shim harness.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-24T23:29:29.223+02:00 - Phase 150 independent review closeout: the colon-form URL plan text, the three-column delivery shape, the `fix/*` and clean-merge test pins, and the two deferred hardening notes

Five points settled by the independent post-implementation review
closeout (Tasks 150.100/150.110/150.120; the review verdict itself — no
errors, REQ-001…REQ-011 all implemented, all 11 ACCs re-verified, the
gate independently re-run green — is recorded in the Recent Updates
entry). (1) **D1 plan-text URL corrections**: the three stale slash-form
occurrences (REQ-001, the Design Notes "GitHub REST, not GraphQL" bullet
with its hard-coded repo name, and Task 100.115's text) are corrected to
the implemented documented `user:ref` COLON form with the `{owner}/{repo}`
placeholder — `repos/{owner}/{repo}/pulls?state=closed&head={owner}:
<ref>&per_page=100` — matching the Phase 100 Decisions entry (1)
adjudication (the slash form was tested live and is silently ignored by
the API, returning every closed PR); only the stale fragments are
rewritten — the elided `head=...` forms on the Depends-On and
Task 100.100 lines assert no form and are left alone, and no
phase/task is renumbered. (2) **D2 delivery line shape**: Task 100.100's
two-field sketch is corrected to the implemented three-column form
(`number<TAB>merged_at<TAB>merge_commit_sha`), matching the Phase 100
Decisions entry (2) ("the 3-column form supersedes Task 100.100's
two-field sketch wherever it conflicts"); the single clause is rewritten,
the rest of the task line untouched. (3) **G1 the `fix/*` class pin**:
every pre-existing cleanup fixture created only `feat-*` branches, so the
`fix/` arm of the remote-candidate filter, the local candidate union, and
the deletion of a slash-containing branch name had never run; the new
`test_precheck_cleanup_deletes_stale_fix_slash_branch` closes that gap
with a stale `fix/233-release-precheck` on both sides (matching tips, the
`commit-tree` squash-stand-in shape, delivery an ancestor of `vPrev`),
asserting both refs deleted and both report lines naming the
slash-containing branch — the test passes against the unchanged script,
confirming the `fix/` arm works as documented. (4) **G2 the clean-merge
plain-`-d` pin**: every deletion fixture used a `commit-tree` side commit
that is NOT an ancestor of dev, so `git branch -d` refused in all of them
and only the `-D`-fallback mechanic string was ever asserted; the new
`test_precheck_cleanup_deletes_stale_clean_merge_plain_d` uses a branch
whose tip IS a genuine ancestor of dev (the `v0.9.8`-tagged first
fixture commit, merged-PR delivery equal to it), asserting the local
deletion succeeds via plain `git branch -d` (the report line carries the
plain `-d` mechanic, the `-D`-refusal wording asserted absent) and the
origin side via `git push origin --delete` — pinning Phase 110
Decisions entry (4)'s "plain `git branch -d` on the rare clean-merge
success" half, which was previously unpinned. (5) **The DEFERRED
hardening notes, with rationale** — left untouched in this phase:
**I1** — the two per-run cache files live in world-writable
`${TMPDIR:-/tmp}` keyed by PID only, and a pre-existing file is trusted
(`[ ! -e "$cache" ]` skips the fetch): a planted closed-PR-scan cache
could suppress the REQ-011 fallback (an unclosed feat merged only under a
renamed branch would pass the gate — the exact false negative the gate
exists to prevent), while a planted origin-branches listing can at worst
cause deletion misses (each deletion still requires the live `gh api`
merged-PR proof plus both ancestry tests, so no wrongful deletion is
possible). Deferred because the PID-keyed file idiom is load-bearing —
the scan runs in pipeline/command-substitution subshells where only `$$`
(not variables or traps) propagates (Phase 100 Decisions entry (3)) — so
a `mktemp -d` (0700)/O_EXCL redesign is a design change beyond this
phase's scope; the deletion-side exposure is bounded by the live proof,
and the gate-side exposure is theoretical (requires a local actor able to
plant a file at exactly this run's PID path before the fetch). **I2** —
`latest_tag` runs `git describe --tags --abbrev=0` with no name pattern,
so any ad-hoc non-`v*` tag later placed in dev's history would silently
become `vPrev` (wrong gate window, wrong cleanup staleness boundary).
Deferred because all 41 current tags are `v*`-shaped and the SOP defines
`vPrev` identically (no script/SOP drift today); adding a `v*` pattern is
a behaviour change to the normative `vPrev` definition (SOP step 2 +
Definitions would need syncing) and is a follow-up candidate.

#### 2026-10-24T21:11:46.739+02:00 - Phase 140 review remediation: the origin-listing cache reuse, the explicit-not-gated gate line, the `status:` YAML-tolerance scope, and the deferred findings

Four points settled during the PR #236 post-implementation review
remediation (Tasks 140.100/140.110). (1) **I1 cache reuse (removes the
E1 surface)**: the per-candidate `git ls-remote origin refs/heads/<name>`
tip lookup is replaced by the once-per-run `git ls-remote --heads origin`
listing cached in a PID-keyed file (the `closed_pr_scan` idiom:
`origin_branches_cache_path` + `origin_branches` + `origin_branch_tip`,
the same two `stage_precheck` rm/trap lines covering both caches). One
origin round-trip per precheck run instead of one per candidate, and the
E1 failure surface disappears with the second call — the only remaining
fetch is the one that still `die`s with the existing message, so a
transient network failure can no longer exit the precheck with only git's
raw stderr under `set -euo pipefail`. The listing is valid for the whole
run: the only ref deletions mid-run are the loop's own, and each candidate
is processed once (never re-queried after its own deletion). (2) **G1
explicit-not-gated, not a violation**: the plan's gate condition is the
ancestry test (a delivery inside `vPrev..HEAD`), so a delivery that is an
ancestor of neither `HEAD` nor `vPrev` cannot be inside the window —
gating it would contradict the plan. The empty else therefore prints an
explicit not-gated info line naming the feat id, the PR number, and the
short sha ("not an ancestor of `HEAD`", plus "nor of `$vprev`" only when a
prior tag exists, since with no prior tag the window is `HEAD` alone) and
the manual-verify pointer — the cleanup-symmetric counterpart of the
cleanup's own fail-safe keep for the same situation. (3) **I4
YAML-tolerance scope**: `feat_status` normalizes exactly what well-formed
YAML frontmatter emits for a scalar status — a trailing comment (YAML
requires whitespace before the `#`) and ONE pair of surrounding matching
single or double quotes (via a `-v`-passed quote character, so the awk
program stays inside its bash single quotes) — nothing more (no escape
handling, no nested/mixed quotes, no flow collections); the existing
closed-set `case` still decides, and every other defect condition (missing
README or line, empty value, out-of-set value) is unchanged. (4) **The
DEFERRED findings, with rationale** — left untouched in this phase:
**I2** — the `-D` fallback's conflation of "squash-merged head" with "tip
drifted after the merged-PR proof" is the plan-accepted codification of the
2026-10-23 manual pass (the merged-PR proof justifies the `-D` by design,
Design Notes + Decisions item (4) of the Phase 110 entry); the mitigation
(comparing the PR's recorded head sha against the branch tip before `-D`)
changes what the proof establishes and is a design change for a follow-up.
**I3** — the swallowed `gh api` delivery-lookup failures (read as "no
merged PR found", REQ-002 semantics) were adjudicated in the Phase 100
Decisions-Made item (5) with the outage already failing the CI-green check
upstream; adding a warning channel for them is a design change, not a
review fix. **I7** — the repeated `shipped in an earlier release` info line
(one per earlier-release feat) is kept as signal: it is the affirmative
evidence that the gate examined each delivery and deliberately did not
gate it, and collapsing it would lose per-feat visibility.

#### 2026-10-24T18:26:40.571+02:00 - Phase 130 closeout: ACC-001..010-vs-11 wording discrepancy, `### Changed` changelog category

Two points settled during closeout (Tasks 130.100/130.110). (1) **ACC
count discrepancy**: Task 130.100's text says "confirm ACC-001 through
ACC-010 are each evidenced," but the plan's Acceptance Criteria section
carries 11 criteria — ACC-011 (the REQ-011 issue-number-prefix fallback)
was added by the 2026-10-24 refinement pass (finding G4) without the task
text being updated. All 11 were evidenced (the evidence table in the
Phase 130 Updates entry); the task text is read as "every acceptance
criterion in the plan," not as a ceiling of 10, so the phase closes on
the full criterion set and no plan-text correction was required.
(2) **Changelog category**: the `CHANGELOG.md` `[Unreleased]` entry goes
under a new `### Changed` heading (the section was empty) — the two new
sub-items change the behaviour of the pre-existing `precheck` stage rather
than adding a new user-facing surface (no new stage, command, tool, or
resource), which is what Keep a Changelog's `Changed` category covers;
`Added` would overstate it.

#### 2026-10-24T18:09:18.574+02:00 - Phase 120 documentation sync: usage() sed-range recomputation, SOP sub-item shape, note placement

Four points fixed while syncing the docs (all verified by the phase-end gate).
(1) **`usage()` sed range**: the header insertions (the 6-line `precheck` entry
replacing the 1-line one, and the 4-line `--dry-run` note block) shift the
usage block's final line (`# full resolved version.`) from line 34 to line 43,
so `usage()`'s `sed -n '2,34p'` became `sed -n '2,43p'` — the range still ends
at the last usage line and excludes the "Written against the old `gh`"
paragraph (which begins two lines below); that range adjustment is the ONLY
non-comment change in `scripts/release.sh`, and `test_help_prints_full_usage`
(rc 2 + `full resolved version.` in stdout) pins it. (2) **SOP sub-item
shape**: step 2's two sub-items continue the existing (a)–(f) enumeration as
(g) and (h), so the SOP's "verifies, in order" list stays the single normative
description of the precheck's run order; the cleanup's four guards are scoped
as "the cleanup's four guards — (a)…(d)" to avoid colliding with the step's
own (a)–(f) check letters, and the unresolvable-delivery fail-safe keep (a
Phase 110 implementation decision) is recorded in (h) as well. (3) **SOP
manual-fallback wording**: both sub-items reduce by hand as verification
(enumerate the shipped feat folders, confirm each is `done`) and deletion
(stale branches per the same four guards), each with the "or simply run the
`precheck` stage, which …" escape the SOP's script-as-projection convention
sanctions — no new procedure step is invented. (4) **README/command note
placement**: the README keeps the single-line usage-block comment (block
alignment preserved, the `#` column unchanged) and carries the prose in a note
directly after the block; the `/release` command keeps its
one-paragraph-per-step shape, folding the closeout-remediation loop into step 3
as the named exception to "any failure: report and stop" (a gate failure is
remediated per the gate's own printed pointer — close out, commit, re-run —
rather than triaged like any other failure).

#### 2026-10-24T17:20:28.288+02:00 - Phase 110 implementation: candidate discovery, exact-lookup delivery, fail-safe keeps, deletion mechanics

Nine points fixed while implementing the cleanup (all pinned by named tests in
`ReleaseShBranchCleanupTestCase`). (1) **Candidate discovery**: the union of
EVERY local branch name (`git branch --format='%(refname:short)'`) and origin's
`refs/heads/feat-*`/`refs/heads/fix/*` names (`git ls-remote --heads origin`, the
`refs/heads/` prefix stripped), deduped and sorted, excluding `dev` and `main` —
the remote side is pattern-filtered while the local side is name-based, so a
local branch of any other name still surfaces (and in the common no-merged-PR
case is kept with a guard-b report line rather than silently skipped); a failed
`ls-remote` dies fail-fast (the remote side cannot be verified, so no cleanup may
run) instead of degrading to the local set. (2) **`branch_delivery` is
exact-lookup only**: a thin wrapper over `merged_delivery` keyed on the branch
name — the REQ-011 issue-number-prefix fallback is a gate-only concern of feat
FOLDER ids and deliberately does not apply to branch names (a branch is stale iff
its own head ref has a merged PR). (3) **Unresolvable-delivery fail-safe keep**:
a delivery sha that is an ancestor of NEITHER `vPrev` nor `HEAD` is kept (never
deleted on unproven ancestry) with a report line naming the unresolvable sha and
that manual adjudication is needed; it is evaluated before guard (c) (the two are
the exclusive branches of the same ancestry test), and a defensive "neither side
resolvable" keep guards the unreachable empty-tip pair. (4) **`-d`→`-D`
mechanics**: the local delete attempts `git branch -d` first; the refusal is the
EXPECTED squash-merge case (the merge rewrote the head, so the branch tip is not
an ancestor of dev) and the `merged_delivery` proof justifies the follow-up
`git branch -D` — the report line then reads `git branch -D — -d refused the
squash-merged head` (or plain `git branch -d` on the rare clean-merge success); a
still-failing `-D`, or a failing `git push origin --delete`, `die`s with an
actionable message naming the manual step and the `precheck v<v>` re-run
(fail-fast; the idempotent re-run resumes from the remaining side, hence the
local-first deletion order). (5) **No-tag skip**: with no `vPrev` there is no
"previous release or older" — a single `branch cleanup: no previous release tag —
nothing to clean up` line, no candidate computation, no loop, no mutation (the
gate's own window-is-`HEAD` note is printed alongside). (6) **Report-line
formats**: exactly one line per candidate — the guard lines name the guard
(`skipped (guard a: checked out in a worktree)`, `kept (guard b: no merged PR for
head ref <name>)`, `kept (guard c: delivery <sha12> is inside the current release
window <vprev>..HEAD)`, `skipped (guard d: local tip <sha12> != origin tip
<sha12> — manual decision)`) and the delete lines carry the side mechanic plus
`proven stale by PR #<n>, delivery <sha12> ≤ <vprev>`, with a `<side> side only; `
marker only when the branch exists on a single side; the summary is `<N>
branch(es) deleted, <M> kept/skipped` after the loop, or `no stale
feat-*/fix/* branches (nothing to delete)` for an empty candidate set. (7)
**First-guard-wins pinned by test**: the guard-(a) test's branch is
worktree-checked-out AND carries a stale merged PR — it reports under guard (a)
only (the (a)→(d) order is a safety property: every guard is a fail-safe
keep/skip, so ordering can never delete what a later guard would have kept).
(8) **`DRY_RUN=1`**: same computation and guard lines, but the delete lines read
`would delete local ref …`/`would delete origin ref …`, no `git branch
-d/-D`/`git push origin --delete` runs, and the summary reads `[dry-run] <N>
branch(es) would be deleted, <M> kept/skipped` (the script's existing
`[dry-run]` line convention); the gate-failure-ordering test pins that a failing
gate prints no `branch cleanup:` line at all. (9) **Test fixture mechanics**:
stale branches are built with `git commit-tree` (a side commit on the
previous-release commit, NOT an ancestor of dev head — the squash-merge stand-in
that makes `git branch -d` refuse) plus `git branch <n> <sha>`/`git push origin
<sha>:refs/heads/<n>`/`git worktree add`, so dev is never switched and the
ancestry tests exercise genuine history; the one-side and tip-mismatch cases
reuse the same commit-tree shape.

#### 2026-10-24T15:41:54.052+02:00 - Phase 100 implementation: URL shape, delivery columns, subshell-safe scan cache

Seven points fixed while implementing the gate (all verified in code; the
URL-shape point was verified live against GitHub on 2026-10-24). (1) **Exact
lookup URL**: `gh api repos/{owner}/{repo}/pulls?state=closed&head={owner}:<ref>&
per_page=100` — the documented `user:ref` COLON form. The plan's sketch
`head=<owner>/<feat-id>` (slash) was tested live and is silently ignored by the
API (it returns every closed PR, which would gate every feat on the repo's
newest merged PR); a bogus-owner colon control returned 0 hits while the
placeholder returned the one hit, proving gh 2.4.0+dfsg1 expands `{owner}`
inside the query string — so no per-run owner/repo resolution is needed.
(2) **Delivery line shape**: `number<TAB>merged_at<TAB>merge_commit_sha` (the
3-column form supersedes Task 100.100's two-field sketch wherever it conflicts):
the gate needs `merged_at` from the exact match too, to pick the newest delivery
across the exact and the REQ-011 fallback matches; the page scan emits the same
three columns plus `head.ref` as a fourth, and the gate compares `merged_at`
lexicographically (ISO-8601 Zulu) across both. (3) **Page scan**: exactly one
`gh api` call of `repos/{owner}/{repo}/pulls?state=closed&per_page=100` (the
API's max page size) per precheck run, parsed lines cached in a PID-keyed file
(`${TMPDIR:-/tmp}/release-closed-pr-scan-<pid>`). The PID keying is mandatory
because `closed_pr_scan` is always invoked from a pipeline/command-substitution
subshell, where variable assignments and traps never propagate to the parent;
`$$` IS inherited, so every subshell re-derives the same path and finds the
already-fetched file on disk. The precheck removes a stale file (PID reuse after
a crash) at run start and traps the removal on EXIT. (4) **Unparseable
`status`**: the frontmatter `status:` line of a feat README is a defect iff the
README is missing, the line is missing or present-but-empty, or the value is
outside the closed set {planning, progress, review, done}; `planning`/
`progress`/`review` are parseable and take the normal PR-lookup path, `done`
is exempt, and the defect is reported before any PR lookup for that folder.
(5) **`gh api` failures in the delivery lookup are swallowed** (`|| true`) and
read as "no merged PR found" (REQ-002 semantics), consistent with the script's
`gh api` tolerance in `close_pr_if_open` and `stage_status`; a full GitHub
outage already fails precheck's CI-green check upstream. (6) **Full-stage test
strategy**: the ACC wording runs the full `stage_precheck`, so the harness
gained `make_release_repo` (adds the `main` branch the existing `make_repo`
lacks, a `v0.9.8` tag at the first commit, an in-window second commit, and feat
folders with minimal frontmatter committed at the head), a fake `uv` shim
answering `uv lock --check` with rc 0, the green `lint_test_run` fixture at
dev's head, and target `0.9.9` (no tag); delivery SHAs are REAL fixture commits
so the `git merge-base --is-ancestor` tests exercise genuine ancestry, and the
no-prior-tag case uses the same fixture without the tag. (7) **Gate report
format**: one line per offending feat naming the id, the current status (or the
frontmatter defect), the PR number, and the FULL delivery sha, plus a trailing
remediation pointer (close out to `done` on `dev` or repair the frontmatter,
commit, re-run `scripts/release.sh precheck v<v>`); `die` receives the
multi-line message as a single argument and the tests assert `result.stderr`
substrings plus exit code 1.

#### 2026-10-24T14:09:57.499+02:00 - Refinement choices: fail-safe gating, prefix fallback, first-guard-wins

Three design points fixed by the refinement pass. (1) A feat folder whose `status` line is
missing or unparseable blocks the release rather than being skipped — the gate's job is to
prove every shipped feat is closed out, and an unreadable frontmatter is not proof.
(2) The gate's PR lookup falls back to the folder's `feat-<NNN>-` issue-number prefix when
the exact head ref has no merged PR, because this repo has shipped work from renamed
branches (feat-134: PR #137 from the folder-named branch, PR #168 from
`feat-134-similarity-requires-mcp`), and a silent miss is the failure the gate exists to
prevent; `feat-0-*` folders have no issue number and stay exact-match only. (3) The
cleanup evaluates guards (a)→(d) in order and the first guard that fires wins, so a branch
matching several guards (e.g. feat-139: worktree-checked-out and no-merged-PR) reports
exactly one line naming the decisive guard.

#### 2026-10-24T11:39:24.997+02:00 - Both rules fold into `precheck`; no new stage or SOP step

The maintainer rejected a dedicated post-`release-notes` cleanup stage and a
separate pre-`bump` gate stage in favor of extending `stage_precheck` with two sub-items
(closeout gate, then branch cleanup). Rationale captured in Design Notes: the gate must
hold before the version increment is written (precheck is the last stage before `bump`),
and the latest tag is unambiguous in precheck because the release being cut has no tag
yet. This keeps the SOP's stage/step 1:1 mapping and avoids renumbering. The accepted
consequence — `stage_all` inherits the cleanup — is recorded in the issue.
