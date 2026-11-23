---
created: '2026-11-23T05:47:05.215Z'
id: feat-274-evals-rootless-docker
status: review
type: feat
updated: '2026-11-23T06:01:51.136Z'
version: 1.0.0
---

# Feature: Evals Structurizr CLI Tests Under Rootless Docker

## Plan

### Overview

Retrospective plan for GitHub issue #274. The fix (PR #272) was implemented and opened before this issue and plan existed, which broke the issue-first, plan-first workflow (DEC e369ee2e-3353-4f92-991c-6367d76d832e). This plan records what was done after the fact.

Under a rootless Docker daemon, the two Structurizr CLI eval tests in `tests/evals/test_cli_gates.py` fail locally. `evals/c4-skills/c4_skills/preflight.py` `host_user_flags()` always passed `--user uid:gid`. Under rootless Docker, container uid 0 already maps to the host user, while container uid 1000 maps to a subordinate uid that cannot read the host user's `0700` temp work dir mounted at `/w`. The JVM in the Structurizr CLI image then cannot open its working directory and fails with `/tmp/hsperfdata_ubuntu/workspace.dsl does not exist`. Because the `pytest` pre-commit hook runs the full suite, this blocks every local commit on a rootless host. CI (rootful Docker) is not affected.

A second defect surfaced on the PR: CI failed its `docs/` drift check because `docs/GENERATED.md` records the test-file count and the PR added a test file without regenerating it. The `specmgr-docs` pre-commit hook is scoped to `src/**/*.py`, so a change that only adds or deletes a test file never ran it locally.

### Requirements

- REQ-001: Under a rootless Docker daemon, `host_user_flags()` returns `["--user", "0:0"]`, so every container runs as the host user whatever default `USER` its image declares.
- REQ-002: On a rootful daemon, or when the rootless probe fails for any reason, `host_user_flags()` returns `["--user", "uid:gid"]` of the host user. Without a POSIX user identity it returns `[]` and does not run the probe.
- REQ-003: A successful rootless probe runs at most once per process. A failed probe is not cached, so a transient failure is retried on the next call.
- REQ-004: A commit that adds or deletes a `tests/**/test_*.py` file without regenerating `docs/GENERATED.md` fails the local pre-commit hooks.
- REQ-005: The preflight record of every evals run states the Docker daemon mode (`docker_rootless`) and the resulting `container_user_flags`.

### Acceptance Criteria

- [x] ACC-001: On a rootless Docker host, `tests/evals/test_cli_gates.py` passes (REQ-001).
- [x] ACC-002: `tests/evals/test_preflight_user_flags.py` covers, with `subprocess.run` mocked inside `preflight` only: rootless (`--user 0:0`), rootful (`--user uid:gid`), every probe failure (missing CLI, timeout, non-zero exit, text that is not JSON, empty output, a JSON object, non-string entries, a non-exact `rootless` match), the cache (one probe after a success, a retry after a failure, the explicit clear), and the non-POSIX path (`[]`, no probe) (REQ-001 to REQ-003).
- [x] ACC-003: `scripts/check_generated_test_count.py` exits 0 when the count in `docs/GENERATED.md` matches, and exits 1 with an actionable message after adding or after deleting one test file; the `specmgr-docs-test-count` hook runs it on every commit (`always_run`) (REQ-004).
- [x] ACC-004: `run_preflight` records `docker_rootless` and `container_user_flags` (REQ-005).
- [ ] ACC-005: PR #272 CI is green, including the Python 3.13 `docs/` drift check.

### Scope

#### Included

- `evals/c4-skills/c4_skills/preflight.py`: the rootless probe, its success-only cache, `host_user_flags()`, and the preflight record fields.
- `tests/evals/test_preflight_user_flags.py`: unit tests for the probe, the cache, and the flags.
- `scripts/check_generated_test_count.py` and `tests/test_check_generated_test_count.py`: the test-file count check and its tests.
- `.pre-commit-config.yaml`: the new `specmgr-docs-test-count` hook; the `specmgr-docs` hook stays scoped to `src/**/*.py`.
- `docs/GENERATED.md`: the regenerated test-file count.
- `AGENTS.md` and `CHANGELOG.md`: the hook description and an `[Unreleased]` Fixed entry.
- `.specmgr/feat/feat-250-c4-structurizr-skills/README.md`: a note that its "host uid:gid" container-user statements hold for rootful Docker only.
- This retrospective plan.

#### Explicitly Out Of Scope

- Changing the callers of `host_user_flags()` (`graders._run_cli`, `runner._run_opencode_container`, the `tests/evals/test_cli_gates.py` mirror); they splice the flags in unchanged. The trial container sets `HOME=/tmp/oc-home` itself, so running it as uid 0 needs no other change.
- A rootful daemon with user-namespace remapping (`userns-remap`, reported as `name=userns`): `--user uid:gid` also maps to a subordinate uid there and can hit the same unreadable mount. It is reported as rootful and not handled.
- Updating the "Operational gotchas" of the finished plans feat-263-delegation-prompts, feat-167-mcp-lifecycle-commands-2 and feat-123-test-gap-cache, which say a test-only commit needs a manual `specmgr docs` run. They stay as historical record; see Design Notes.

### Dependencies

#### Blocks

- feat-253-md-line-offset: its local commits are blocked by the two failing eval tests on a rootless host until this lands on `dev`.

### Design Notes

The probe is `docker info --format '{{json .SecurityOptions}}'`, checked for an exact `name=rootless` element of a comma-separated security option. Every probe failure falls back to the rootful behavior (`--user uid:gid`), so a rootful host is never changed by a flaky probe. Only a successful probe is cached (a module-level value, cleared by `clear_docker_rootless_cache()`); a failed probe, e.g. a timeout while the daemon starts, is retried instead of fixing the rootful default for the whole run.

Under rootless Docker the flags are an explicit `--user 0:0` rather than no flag. The first version passed no flag and relied on each image's default `USER` being root. That holds for `structurizr/structurizr:2026.10.26-noble` (empty `Config.User`), and the locally available `ghcr.io/anomalyco/opencode:latest` also has an empty `Config.User`, but the pinned `ghcr.io/anomalyco/opencode:2.2.5` could not be inspected (the registry token request returned 403). An explicit `0:0` makes the fix independent of any image's `USER`.

pre-commit never passes deleted files to a hook (its staged-file list uses `git diff --staged --diff-filter=ACMRTUXB`), so widening the `specmgr-docs` `files:` pattern to `tests/` cannot catch a commit that only deletes a test file. The first version of this fix did that widening; it is replaced by the `specmgr-docs-test-count` hook, which runs on every commit and only compares counts (one directory walk, no regeneration). It reuses `specmgr docs`'s own `_count_test_files`, so the two cannot count differently. Like `specmgr docs`, it counts the working tree, so an untracked `tests/**/test_*.py` file that is not staged counts too (pre-commit does not stash untracked files). With the count check in place, the "Operational gotchas" of feat-263, feat-167 and feat-123 are superseded: a stale count now fails locally instead of only in CI.

### Related Decisions

- DEC e369ee2e-3353-4f92-991c-6367d76d832e: development artifacts in `.specmgr` with feature-driven work units (the workflow this retrospective restores).
- DEC 9c687bb1-8ee7-41c8-84ec-07606356bc73: enforce doc generation, lint, and tests locally via pre-commit, not just CI (the reason for REQ-004).

### Task List

#### Phase 100: Rootless Docker Fix

- [x] Task 100.100: Add the cached rootless probe to `preflight.py` and change `host_user_flags()` under rootless Docker.
- [x] Task 100.110: Add `tests/evals/test_preflight_user_flags.py`.

#### Phase 110: Docs Drift Fix

- [x] Task 110.100: Regenerate `docs/GENERATED.md` (test-file count 502 to 503).
- [x] Task 110.110: Widen the `specmgr-docs` hook to `tests/**/*.py` and document it in `AGENTS.md` (superseded by Task 130.110).

#### Phase 120: Retrospective Bookkeeping

- [x] Task 120.100: Open GitHub issue #274 and link PR #272 to it (`Fixes #274`).
- [x] Task 120.110: Write this retrospective plan.
- [ ] Task 120.120: Confirm PR #272 CI is green (ACC-005), merge, and set the status to done.

#### Phase 130: Review Fixes

- [x] Task 130.100: G2: pass an explicit `--user 0:0` under rootless Docker instead of no flag.
- [x] Task 130.110: G1, D3, I3: replace the widened `specmgr-docs` pattern with the always-run `specmgr-docs-test-count` hook and `scripts/check_generated_test_count.py` (with tests); `specmgr-docs` back to `src/**/*.py`.
- [x] Task 130.120: S1: cache only a successful probe; add `clear_docker_rootless_cache()`.
- [x] Task 130.130: G3, G4, S2: add tests for empty output, a JSON object, non-string entries, a non-exact match, the cache, and the non-POSIX path; patch `subprocess.run` inside `preflight` only.
- [x] Task 130.140: I1: record `docker_rootless` and `container_user_flags` in the preflight record.
- [x] Task 130.150: D1: add an `[Unreleased]` Fixed entry to `CHANGELOG.md`.
- [x] Task 130.160: D2: note in the feat-250 plan that its container-user statements hold for rootful Docker only.
- [x] Task 130.170: D4, D5, I2, I4: record the superseded gotchas, the plan commit, the `userns-remap` limitation, and the exact verification commands in this plan.

## Progress

### Current Status

**As of 2026-11-23**: The implementation and the Phase 130 review fixes are complete and in review on PR #272. ACC-001 to ACC-004 are met. ACC-005 waits on the CI run for the review-fix commit.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-23T06:01:51.136Z - Phase 130 review fixes

Implemented every finding of the feat-reviewer pass (G1 to G4, D1 to D5, S1, S2, I1 to I4) as Phase 130. All commands ran in the `fix-evals-rootless-docker` worktree on a host whose `docker info` reports `name=rootless`.

- G2: `host_user_flags()` returns `["--user", "0:0"]` (`ROOTLESS_CONTAINER_USER`) under rootless Docker. `docker image inspect` shows an empty `Config.User` for `structurizr/structurizr:2026.10.26-noble` and for the local `ghcr.io/anomalyco/opencode:latest`; the pinned `ghcr.io/anomalyco/opencode:2.2.5` could not be fetched for inspection (registry token request: 403 Forbidden), which is why the user is now explicit.
- G1, D3, I3: the `specmgr-docs` hook is back on `^src/.*\.py$` (so `specmgr-mcp-docs`'s "equally broad" wording is true again), and the new `specmgr-docs-test-count` hook (`always_run: true`) runs `scripts/check_generated_test_count.py`. Run by hand, the script exited 0 with the count in sync, and exited 1 with `docs/GENERATED.md records 504 test file(s), but tests/ has 505` after adding an empty test file and with `... but tests/ has 503` after removing `tests/test_paths.py` (both restored afterwards). `pre-commit run specmgr-docs-test-count` passed.
- S1: `docker_is_rootless()` caches only a successful probe in a module-level value; `clear_docker_rootless_cache()` resets it. `functools` is no longer imported.
- G3, G4, S2: `tests/evals/test_preflight_user_flags.py` now has 14 tests (was 7), patching `preflight.subprocess.run` only.
- I1: `run_preflight` records `docker_rootless` and `container_user_flags`; the module docstring lists them.
- D1: `CHANGELOG.md` `[Unreleased]` Fixed entry for the hook and the evals fix.
- D2: the feat-250 plan's two container-user statements now say they hold for rootful Docker and point to this plan.
- `docs/GENERATED.md` regenerated: test-file count 503 to 504 (the new `tests/test_check_generated_test_count.py`).
- Gate: `uv run --frozen pytest -q tests/evals/test_cli_gates.py tests/evals/test_preflight_user_flags.py` gave 18 passed on the rootless host (ACC-001, ACC-002). `uv run --frozen pytest -q -n auto` gave 6135 passed, 18 skipped, 0 failed. `ruff format --check`, `ruff check`, and `vulture src/ whitelist.py --min-confidence 60` are clean.

#### 2026-11-23T05:47:05.215Z - Retrospective plan created

Created this plan after the fact for issue #274. The code (482e4d95) and PR #272 were made without an issue or a plan; issue #274 was opened and linked from the PR on 2026-11-23. The docs drift fix (6b85f09b) regenerated `docs/GENERATED.md` and widened the `specmgr-docs` hook. `pre-commit run specmgr-docs --files tests/evals/test_preflight_user_flags.py` then ran the hook and passed.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-23T06:01:51.136Z - Explicit container root under rootless Docker

Under rootless Docker the containers run as `--user 0:0` instead of with no `--user` flag, so the fix does not depend on an image's default `USER`, which could not be verified for the pinned OpenCode image.

#### 2026-11-23T06:01:51.136Z - Count check instead of a wider hook pattern

The test-file count is checked by a dedicated always-run hook instead of widening the `specmgr-docs` `files:` pattern, because pre-commit never passes deleted files to a hook, and because the check costs one directory walk instead of a full regeneration on every test edit.

#### 2026-11-23T05:47:05.215Z - Fix the hook gap in the same PR

The `specmgr-docs` hook gap is fixed in PR #272 rather than in a separate feature, because it is what let this PR's CI failure through and the change is small.

### Related PRs / Commits

- PR #272: fix(evals): skip --user under rootless Docker so mounted work dirs stay readable.
- 482e4d95: fix(evals): skip --user under rootless Docker so mounted work dirs stay readable.
- 6b85f09b: fix(docs): regenerate GENERATED.md test count; run specmgr-docs hook on tests/ changes (#274).
- 4b4fb355: docs(feat-274): retrospective plan for the rootless Docker evals fix (issue #274).
