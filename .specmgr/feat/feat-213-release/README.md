---
classification: null
created: '2026-10-15T11:38:21.870+02:00'
id: feat-213-release
status: progress
type: feat
updated: '2026-10-15T13:42:45.518+02:00'
version: 1.0.0
---

# Feature: close_pr_if_open gh-state-read race in release.sh pr-merge (#213)

## Plan

### Overview

GitHub issue #213: `scripts/release.sh pr-merge <version>`'s `close_pr_if_open` helper (scripts/release.sh:286-297) can still exit the stage non-zero immediately after a fully successful fast-forward merge. The helper reads the PR's state via `gh api repos/{owner}/{repo}/pulls/<n> --jq .state` and only calls `gh pr close` when that state is not `merged`/`closed`. Immediately after `stage_pr_merge` pushes the local `git merge --ff-only` of `origin/dev` onto `main`, GitHub detects the PR is now fully contained in `main` and flips it to `MERGED` asynchronously; if the state read lands in the (apparently non-trivial) window before that server-side detection has landed, the read comes back empty/stale, the `case` falls into the `*)` branch, and `gh pr close` is issued against an already-merged PR — failing with "can't be closed because it was already merged". Under the script's `set -euo pipefail`, that bare statement kills the whole stage non-zero *after* the merge + push have already fully succeeded: `pr-merge: done` is never printed, and `release.sh status` is the only way to discover that nothing is actually broken.

It reproduced live during the v0.36.0 release (PR #212; `origin/main` and `origin/dev` both at `91d2b57`); the workaround was to re-run `pr-merge` once the race had settled — safe because the stage's early-return guard (`origin/main` already equals `origin/dev` → "nothing to merge") makes the re-run a no-op. This is the second occurrence of the already-merged-close symptom: the first (v0.35.0, fixed by commit `0cdaa98`) is what introduced `close_pr_if_open` itself and logged the incident in the release SOP's Updates section; this issue is the narrower residual race inside the helper.

This feature hardens `close_pr_if_open` with a layered defense: it retries the PR-state read with a short backoff (bounded, mirroring the `wait_for_run`/`wait_for_pr_checks` polling pattern) before falling through to `gh pr close`, and if the close still fails, it re-verifies the state once more — treating the failure as the known race (info note, success) only when the state is now `merged`/`closed`, and dying with an actionable message otherwise. `stage_pr_merge` must end by printing `pr-merge: done (...)` for this already-merged-by-GitHub case. The behavior is pinned by new fake-`gh`-shim test cases in `tests/test_release_sh.py`, and the release SOP's Updates section gains a dated entry recording the v0.36.0 incident and the hardened behavior (the script's header makes the SOP the normative record).

### Requirements

- REQ-001: `close_pr_if_open` retries the `gh api` PR-state read with a short backoff, up to a small bounded attempt count (each attempt info-logged), and returns early with the existing "PR #N already merged/closed — nothing to close" behavior once the state reads `merged`/`closed`; when the budget is exhausted with the state still not `merged`/`closed`, the helper proceeds to `gh pr close` exactly as today (a genuinely open PR must still be closed).
- REQ-002: If `gh pr close` fails, `close_pr_if_open` re-reads the PR state: when it is now `merged`/`closed`, the failure is treated as the known race against GitHub's async merge detection (info note, the helper returns success); only when the state still is not `merged`/`closed` does the helper die with an actionable message naming the PR.
- REQ-003: In the already-merged-by-GitHub case, `stage_pr_merge` ends by printing `pr-merge: done (...)` and exiting 0 — completing the release must not require re-running the stage after the race has settled.
- REQ-004: The behavior is pinned by new fake-`gh`-shim test cases in `tests/test_release_sh.py`: (a) the state read is initially empty/stale and flips to `merged` within the retry budget — the helper skips the close and returns 0, with no `gh pr close` issued; (b) the state never flips and `gh pr close` fails — the helper exits non-zero with the actionable message; (c) `gh pr close` fails and the re-verify read returns `merged` — the helper returns 0 with the info note; the pre-existing suite stays green.
- REQ-005: The release SOP (`docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md`) gains a dated Updates entry (prepended directly below the ordering comment, newest-first) recording the v0.36.0 incident (issue #213, PR #212) and the hardened `close_pr_if_open` behavior.
- REQ-006: No other stage of `scripts/release.sh` changes behavior — the fast-forward-only merge mechanics, the pre-/post-merge SHA invariant assertions, and the stage's idempotent early-return guard are untouched; `CHANGELOG.md`'s `[Unreleased]` section gains a `### Fixed` entry for the repair (repo convention, cf. the v0.36.0 entry for the `0cdaa98` fix).

### Acceptance Criteria

- [ ] ACC-001: `close_pr_if_open` retries the state read with a bounded backoff and skips the close when the state becomes `merged`/`closed` within the budget; a genuinely open PR is still closed once the budget is exhausted (REQ-001).
- [ ] ACC-002: A failed `gh pr close` triggers the state re-verify: the helper succeeds with an info note when the re-read is `merged`/`closed`, and dies with an actionable, PR-naming message when it is not (REQ-002).
- [ ] ACC-003: The already-merged-by-GitHub path through `stage_pr_merge` prints `pr-merge: done (...)` and exits 0 without a re-run (REQ-003).
- [ ] ACC-004: The three new fake-`gh`-shim test cases (stale→`merged` read, failing close with never-`merged` state, failing close with `merged` re-verify) are green and the entire pre-existing `tests/test_release_sh.py` suite stays green (REQ-004).
- [ ] ACC-005: The release SOP's Updates section carries the prepended dated entry for the v0.36.0 incident + hardened behavior, in the SOP's own entry shape (REQ-005).
- [ ] ACC-006: The diff is confined to `close_pr_if_open` in `scripts/release.sh`, the shim extensions + new test cases in `tests/test_release_sh.py`, the SOP Updates entry, and the CHANGELOG entry — no other stage's behavior changes (REQ-006).

### Scope

#### Included

- The layered hardening of `close_pr_if_open` in `scripts/release.sh`: bounded state-read retry with short backoff, plus the failed-close state re-verify that distinguishes the known race from a genuinely broken state.
- The fake-`gh`-shim extensions in `tests/test_release_sh.py` needed to simulate the race: per-call PR-state sequences (the shim's `api` branch currently answers from a single `pull_<n>_state` file) and a `gh pr close` that can fail with a recorded message/exit code (currently an unconditional `exit 0`), plus the three new test cases.
- The release SOP's dated Updates entry (v0.36.0 incident + hardened behavior).
- The `CHANGELOG.md` `[Unreleased]` → `### Fixed` entry.

#### Explicitly Out Of Scope

- Changes to any other `release.sh` stage (`resolve`/`precheck`/`bump`/`changelog`/`commit-push`/`pr-create`/`tag-push`/`publish-wait`/`release-notes`/`status`/`all`) or to the fast-forward-only merge mechanics and invariant assertions.
- The `stage_pr_merge` early-return guard (`origin/main` already equals `origin/dev` → "nothing to merge") — it already makes a re-run a safe no-op and stays as-is.
- Porting the script to newer `gh` versions, or removing/reworking any existing gh-2.4.0-specific workaround.
- Changes to the SOP's own procedure steps or safety notes (the script must stay a deterministic projection of the SOP; only the SOP's Updates log grows).
- Any other open issue (only #213).

### Design Notes

**The race.** `stage_pr_merge` pushes the local `git merge --ff-only` of `origin/dev` onto `main` and then asserts `origin/main == origin/dev` — by that point the PR's content is merged by construction. GitHub, however, marks the PR `MERGED` only after its own server-side detection that the head is contained in the base, which lands asynchronously (seconds after the push, apparently non-trivially often). `close_pr_if_open`'s single state read therefore hits a window in which the read returns empty/stale (the observed v0.36.0 behavior: effectively empty state), the `case` falls into `*)`, and `gh pr close` races GitHub's own close: it fails with "can't be closed because it was already merged", and — being a bare statement under `set -euo pipefail` — kills the stage after the substantive work already succeeded.

**Layered defense (user-approved 2026-10-15).** Issue #213 offered three options; the chosen design combines option 1 (retry the state read with a short backoff, mirroring `wait_for_run`/`wait_for_pr_checks`) and option 3 (re-verify once more after a failed `gh pr close`, dying only if the state still is not `merged`/`closed`). The layers: (1) a bounded retry loop — a small attempt count with a few-seconds backoff, each attempt info-logged, returning early on `merged`/`closed`; this covers the observed stale-read window, and the common path (state already `merged` on the first read) exits immediately. (2) After the budget is exhausted with the state still not `merged`/`closed`, proceed to `gh pr close` exactly as today — `close_pr_if_open` is generic in the PR number (the existing `open`-state test calls it directly), so a genuinely open PR must still be closable. (3) If `gh pr close` fails, re-read the state: `merged`/`closed` → info note + success (the known race); anything else → actionable `die` naming the PR (a genuinely broken state — e.g. the close failed for unrelated reasons and the PR is still open). Option 2 (message-gated `|| true`) is rejected: it keys on `gh`'s error-text phrasing — brittle across `gh` versions and capable of swallowing genuine close failures — while the re-verify layer tolerates exactly the known race, verified against the state (ground truth) rather than an error string, and still fails hard on everything else.

**Retry budget.** Dedicated script-local variables next to `POLL_INTERVAL` (e.g. `PR_STATE_RETRY_ATTEMPTS=5`, `PR_STATE_RETRY_INTERVAL=3`): worst-case added latency on the merge path is ~12 s (5 × 3 s, only when the state stays stale), negligible against the minutes the stage already spends on CI/check polling, and the variables are overridable to 1 in the test bodies so the suite stays fast under the harness's `POLL_INTERVAL=1` convention.

**Test simulation.** The shim's `api` branch answers the state from a single `pull_<n>_state` file (default `open`); it gains a per-call flip counter in the existing `run_<id>_flip`/`run_<id>_views` style, so a test can present a stale/empty state for the first N reads and `merged` afterwards. The shim's `pr close` branch (unconditional `exit 0`) gains a state-file-gated failure: when a recorded rc/message file exists, the shim prints the message to stderr and exits with the recorded rc. The three ACC-004 cases map 1:1 onto these fixtures.

**SOP + CHANGELOG.** The SOP Updates entry follows the existing entry shape (`### {space-separated timestamp} - {title}`, newest-first below the ordering comment, incident narrative in the style of the 2026-10-06 v0.35.0 entry) and records: the v0.36.0 occurrence (issue #213, PR #212, both branches at `91d2b57`), the re-run workaround actually used, and the layered hardening now in `close_pr_if_open`. The CHANGELOG entry goes under `[Unreleased]` → `### Fixed` in the v0.36.0 entry's style, citing feat-213-release / issue #213.

**Phase discipline.** Every phase ends with the full quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src --cov-report=` — the bash change is covered by `tests/test_release_sh.py` inside the suite) and exactly one Conventional Commit.

### Related Decisions

- SOP 98537416-0e6e-4a02-925f-974a17bfa10a ("Perform a release of biz.dfch.SpecMgr"): the normative release procedure; its Updates section carries the v0.35.0 defect log (including the original already-merged-close incident) and gains this feature's v0.36.0 entry — the script's header makes the SOP the authority (where they disagree, fix the script).
- Commit `0cdaa98` ("fix(release): correct CI/PR-check gates in scripts/release.sh; log v0.35.0 incidents in SOP"): introduced `close_pr_if_open` itself and the fake-`gh`-shim test suite this feature extends.

### Task List

#### Phase 100: close_pr_if_open layered defense

- [x] Task 100.100: Implement the bounded state-read retry in `close_pr_if_open` (dedicated `PR_STATE_RETRY_ATTEMPTS`/`PR_STATE_RETRY_INTERVAL` variables next to `POLL_INTERVAL`, each attempt info-logged, early return on `merged`/`closed`, proceed to `gh pr close` after the budget) (REQ-001, ACC-001).
- [x] Task 100.110: Implement the failed-close state re-verify in `close_pr_if_open` (on `gh pr close` failure, re-read the state; `merged`/`closed` → info note + success, otherwise → actionable `die` naming the PR) so the already-merged path through `stage_pr_merge` reaches `pr-merge: done (...)` (REQ-002/REQ-003, ACC-002/ACC-003).
- [x] Task 100.120: Phase-end gate (full quality gate per Design Notes) plus exactly one Conventional Commit.

#### Phase 110: Pin the race outcomes in tests

- [x] Task 110.100: Extend the fake-`gh` shim in `tests/test_release_sh.py` for per-call PR-state sequences (flip-counter style, mirroring the existing `run_<id>_flip`/`run_<id>_views` mechanics) and for a `gh pr close` that fails with a recorded message/exit code (state-file gated; unconditional `exit 0` stays the default) (REQ-004, ACC-004).
- [x] Task 110.110: Add the three test cases: (a) stale/empty state flips to `merged` within the retry budget — no `gh pr close` issued, rc 0; (b) state never flips and `gh pr close` fails — rc non-zero, actionable message on stderr; (c) `gh pr close` fails and the re-verify read returns `merged` — rc 0, info note (REQ-004, ACC-004).
- [x] Task 110.120: Phase-end gate (incl. the full pre-existing `tests/test_release_sh.py` suite green) plus exactly one Conventional Commit.

#### Phase 120: SOP + CHANGELOG record

- [ ] Task 120.100: Prepend the dated Updates entry to the release SOP recording the v0.36.0 incident (issue #213, PR #212, the re-run workaround used) and the layered hardening of `close_pr_if_open`, in the existing entry shape (REQ-005, ACC-005).
- [ ] Task 120.110: Add the `CHANGELOG.md` `[Unreleased]` → `### Fixed` entry in the v0.36.0 entry's style, citing feat-213-release / issue #213 (REQ-006, ACC-006).
- [ ] Task 120.120: Phase-end gate (full quality gate; the SOP change is docs-only, no `specmgr docs` regeneration needed) plus exactly one Conventional Commit.

## Progress

### Current Status

**As of 2026-10-15**: Phases 100 and 110 complete — Phase 100 implemented the layered defense in `close_pr_if_open` (`scripts/release.sh`): the PR-state read is a bounded retry (`PR_STATE_RETRY_ATTEMPTS=5` attempts, `PR_STATE_RETRY_INTERVAL=3` s between — never after the last), each attempt info-logged, early return on `merged`/`closed`, proceed to `gh pr close` after the budget, and a failed close re-verifies the state once (known race → info note + success, otherwise actionable `die` naming the PR). Phase 110 extended the fake-`gh` shim in `tests/test_release_sh.py` with per-call PR-state sequences (flip-counter style) and a state-file-gated `gh pr close` failure, and pinned the three ACC-004 race outcomes (stale/empty → `merged` within the budget skips the close with no `gh pr close` issued; never-flipping state + failing close dies rc 1 with the actionable message; failing close + `merged` re-verify returns rc 0 with the known-race info note) — the full suite (now 11 tests) stays green and fast. Phase 120 (SOP + CHANGELOG record) is pending.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-15 11:42:45.519Z - Phase 110 complete: race outcomes pinned in the fake-gh-shim tests

Extended the fake `gh` shim in `tests/test_release_sh.py` for the v0.36.0 async-merge race (issue #213): the `api` PR-state branch now serves a per-call sequence when a `pull_<n>_flip` file is present — stale value for reads 1..N, final value afterwards, the `run_<id>_flip`/`run_<id>_views` counter mechanics (an empty stale file reproduces the incident's empty read) — and falls back to the existing single `pull_<n>_state` file (default `open`) when no flip file exists, so every pre-existing fixture keeps working; the `pr close` branch now fails with a recorded `close_rc`/`close_msg` when seeded (message to stderr, exit with the recorded rc), with the unconditional `exit 0` staying the default. Added the three ACC-004 test cases: `test_close_pr_if_open_stale_flips_to_merged_skips_close` (stale/empty → `merged` on read 3 of 5, no `gh pr close` issued, rc 0), `test_close_pr_if_open_never_merged_close_fails_dies` (state never flips, close fails, rc 1 with the actionable `die` message naming the PR and the observed state on stderr), and `test_close_pr_if_open_close_fails_reverify_merged` (close fails, re-verify read is `merged`, rc 0 with the known-race info note). The existing `test_close_pr_if_open_closes_open_pr` now pins `PR_STATE_RETRY_ATTEMPTS=1; PR_STATE_RETRY_INTERVAL=0` in its body (assertions unchanged) so the suite stays fast under the new retry loop; `test_close_pr_if_open_skips_merged_pr` needed no change (first read already `merged`). Phase-end gate green: `pytest tests/test_release_sh.py -v` 11/11 in 1.44 s, `ruff format --check`/`ruff check` clean, `vulture` clean, full suite 4665 passed / 17 skipped.

#### 2026-10-15 11:11:00.712Z - Phase 100 complete: layered defense in close_pr_if_open

Implemented the layered defense in `close_pr_if_open` (`scripts/release.sh`): the PR-state read is now a bounded retry loop — `PR_STATE_RETRY_ATTEMPTS=5` attempts with `PR_STATE_RETRY_INTERVAL=3` s slept between (never after the last one, worst case ~12 s added) — each attempt info-logged, and the first `merged`/`closed` read returns early with the existing success message (the common path exits with zero sleeps). After the budget is exhausted the helper proceeds to `gh pr close` exactly as before, and a failed close now re-verifies the state once: `merged`/`closed` is the known async-merge race (info note, success), anything else dies with an actionable message naming the PR and the observed state. The two new variables are plain assignments next to `POLL_INTERVAL` in the script's variable block, so test bodies can override them after sourcing. The pre-existing `tests/test_release_sh.py` suite stays green (8/8, including the open-PR close test, which now sleeps 12 s under the defaults).

#### 2026-10-15 09:25:57.040Z - Created

Planned this feature from GitHub issue #213 after reviewing `scripts/release.sh`'s `close_pr_if_open` (the helper that reproduced the v0.35.0 incident class a second time, live in the v0.36.0 release), the fake-`gh`-shim suite in `tests/test_release_sh.py`, and the release SOP's incident log. The chosen fix is the layered defense (issue options 1+3: bounded state-read retry with short backoff, plus a failed-close state re-verify that dies only on a genuinely unmerged state); issue option 2 (message-gated `|| true`) was rejected as brittle against `gh`'s error text.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-15 09:25:57.040Z - Layered defense (retry + re-verify) for close_pr_if_open

User-approved at planning: combine issue #213's option 1 (retry the `gh api` state read with a short backoff before falling through to `gh pr close`, mirroring `wait_for_run`/`wait_for_pr_checks`) and option 3 (after a failed `gh pr close`, re-verify the state and die only if it still is not `merged`/`closed`). Rejected option 2 (treat a message-matching close failure as success) because it keys on `gh`'s error-text phrasing — brittle across `gh` versions and capable of swallowing genuine close failures — while the re-verify layer tolerates exactly the known race, verified against the state (ground truth) rather than an error string.

### Related PRs / Commits

- PR #212 (Release v0.36.0): the release where the race reproduced live (`origin/main`/`origin/dev` both at `91d2b57` after the successful fast-forward merge).
- Commit `0cdaa98` (v0.35.0, "fix(release): correct CI/PR-check gates in scripts/release.sh; log v0.35.0 incidents in SOP"): introduced `close_pr_if_open` itself and the fake-`gh`-shim test suite this feature extends.
