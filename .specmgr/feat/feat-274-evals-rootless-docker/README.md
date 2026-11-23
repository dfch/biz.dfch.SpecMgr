---
created: '2026-11-23T05:47:05.215Z'
id: feat-274-evals-rootless-docker
status: review
type: feat
updated: '2026-11-23T05:47:05.215Z'
version: 1.0.0
---

# Feature: Evals Structurizr CLI Tests Under Rootless Docker

## Plan

### Overview

Retrospective plan for GitHub issue #274. The fix (PR #272) was implemented and opened before this issue and plan existed, which broke the issue-first, plan-first workflow (DEC e369ee2e-3353-4f92-991c-6367d76d832e). This plan records what was done after the fact.

Under a rootless Docker daemon, the two Structurizr CLI eval tests in `tests/evals/test_cli_gates.py` fail locally. `evals/c4-skills/c4_skills/preflight.py` `host_user_flags()` always passes `--user uid:gid`. Under rootless Docker, container uid 0 already maps to the host user, while container uid 1000 maps to a subordinate uid that cannot read the host user's `0700` temp work dir mounted at `/w`. The JVM in the Structurizr CLI image then cannot open its working directory and fails with `/tmp/hsperfdata_ubuntu/workspace.dsl does not exist`. Because the `pytest` pre-commit hook runs the full suite, this blocks every local commit on a rootless host. CI (rootful Docker) is not affected.

A second defect surfaced on the PR: CI failed its `docs/` drift check because `docs/GENERATED.md` records the test-file count and the PR added a test file without regenerating it. The `specmgr-docs` pre-commit hook was scoped to `src/**/*.py` only, so a change that adds only a test file never ran it locally.

### Requirements

- REQ-001: `host_user_flags()` returns no `--user` flag when the Docker daemon is rootless, so the container runs as its default user, which maps to the host user.
- REQ-002: On a rootful daemon, or when the rootless probe fails for any reason, `host_user_flags()` keeps returning `["--user", "uid:gid"]`.
- REQ-003: The rootless probe runs at most once per process.
- REQ-004: The `specmgr-docs` pre-commit hook runs when a staged change touches `tests/**/*.py`, not only `src/**/*.py`.

### Acceptance Criteria

- [x] ACC-001: On a rootless Docker host, `tests/evals/test_cli_gates.py` passes (REQ-001).
- [x] ACC-002: `tests/evals/test_preflight_user_flags.py` covers rootless (no flag), rootful (`--user`), and every probe failure (missing CLI, timeout, non-zero exit, unparseable output) with the Docker CLI mocked, and asserts that the probe runs once (REQ-001 to REQ-003).
- [x] ACC-003: `pre-commit run specmgr-docs --files <a tests/ file>` runs the hook instead of skipping it (REQ-004).
- [ ] ACC-004: PR #272 CI is green, including the Python 3.13 `docs/` drift check.

### Scope

#### Included

- `evals/c4-skills/c4_skills/preflight.py`: the rootless probe and the `host_user_flags()` change.
- `tests/evals/test_preflight_user_flags.py`: unit tests for the probe and the flags.
- `docs/GENERATED.md`: the regenerated test-file count.
- `.pre-commit-config.yaml` and `AGENTS.md`: the widened `specmgr-docs` hook scope.
- This retrospective plan.

#### Explicitly Out Of Scope

- Changing the callers of `host_user_flags()` (`graders._run_cli`, `runner._run_opencode_container`, the `tests/evals/test_cli_gates.py` mirror); they splice the flags in unchanged and stay correct.
- An explicit `--user 0:0` for rootless Docker; only needed if an image ever sets a non-root `USER`.
- A `CHANGELOG.md` entry; the evals harness has no history of entries there.

### Dependencies

#### Blocks

- feat-253-md-line-offset: its local commits are blocked by the two failing eval tests on a rootless host until this lands on `dev`.

### Design Notes

The probe is `docker info --format '{{json .SecurityOptions}}'`, checked for a `name=rootless` entry and cached with `functools.lru_cache(maxsize=1)`. Every probe failure falls back to the previous behavior (`--user uid:gid`), so a rootful host is never changed by a flaky probe.

Widening the `specmgr-docs` hook to `^(src|tests)/.*\.py$` makes it run on any test-file change, not only on additions or removals. The extra cost is one `specmgr docs` run per such commit, which is accepted in exchange for catching the test-count drift locally instead of in CI.

### Related Decisions

- DEC e369ee2e-3353-4f92-991c-6367d76d832e: development artifacts in `.specmgr` with feature-driven work units (the workflow this retrospective restores).
- DEC 9c687bb1-8ee7-41c8-84ec-07606356bc73: enforce doc generation, lint, and tests locally via pre-commit, not just CI (the reason for REQ-004).

### Task List

#### Phase 100: Rootless Docker Fix

- [x] Task 100.100: Add the cached rootless probe to `preflight.py` and return no `--user` flag under rootless Docker.
- [x] Task 100.110: Add `tests/evals/test_preflight_user_flags.py`.

#### Phase 110: Docs Drift Fix

- [x] Task 110.100: Regenerate `docs/GENERATED.md` (test-file count 502 to 503).
- [x] Task 110.110: Widen the `specmgr-docs` hook to `tests/**/*.py` and document it in `AGENTS.md`.

#### Phase 120: Retrospective Bookkeeping

- [x] Task 120.100: Open GitHub issue #274 and link PR #272 to it (`Fixes #274`).
- [x] Task 120.110: Write this retrospective plan.
- [ ] Task 120.120: Confirm PR #272 CI is green (ACC-004), merge, and set the status to done.

## Progress

### Current Status

**As of 2026-11-23**: The implementation is complete and in review on PR #272. ACC-001 to ACC-003 are met. ACC-004 waits on the CI run for the docs drift fix (commit 6b85f09b).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-23T05:47:05.215Z - Retrospective plan created

Created this plan after the fact for issue #274. The code (482e4d95) and PR #272 were made without an issue or a plan; issue #274 was opened and linked from the PR on 2026-11-23. The docs drift fix (6b85f09b) regenerated `docs/GENERATED.md` and widened the `specmgr-docs` hook. `pre-commit run specmgr-docs --files tests/evals/test_preflight_user_flags.py` now runs the hook and passes.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-23T05:47:05.215Z - Fix the hook gap in the same PR

The `specmgr-docs` hook gap is fixed in PR #272 rather than in a separate feature, because it is what let this PR's CI failure through and the change is three lines.

### Related PRs / Commits

- PR #272: fix(evals): skip --user under rootless Docker so mounted work dirs stay readable.
- 482e4d95: fix(evals): skip --user under rootless Docker so mounted work dirs stay readable.
- 6b85f09b: fix(docs): regenerate GENERATED.md test count; run specmgr-docs hook on tests/ changes (#274).
