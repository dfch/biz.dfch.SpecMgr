---
classification: null
created: '2026-08-31 15:24:14.582Z'
id: 98537416-0e6e-4a02-925f-974a17bfa10a
status: active
type: sop
updated: '2026-10-24T17:58:14.528+02:00'
version: 1.0.0
---

# Perform a release of biz.dfch.SpecMgr

## Purpose

This procedure defines how a new version of `biz-dfch-specmgr` is released
from the `dev` branch to TestPyPI, PyPI, a GitHub Release, and the MCP
Registry. It exists so that every release — whether driven by the release
agent through the staged `scripts/release.sh` script or performed manually
by the maintainer — passes the same gates (green CI on `dev` and on the
merge pull request, the fast-forward invariant between `main` and `dev`, a
curated changelog, and a verified publication) and produces the same
reproducible outcome.

## Scope

This SOP covers: resolving the target version; pre-release checks;
curating the `CHANGELOG.md` `[Unreleased]` section; bumping the version in
`pyproject.toml` and syncing `uv.lock`; committing and pushing the release
to `dev`; merging `dev` into `main` through a fast-forward-only pull
request; creating and pushing the `vX.Y.Z` tag on `main`; waiting for the
four publication jobs of `.github/workflows/publish.yml`; and setting the
GitHub Release notes (the release name stays the bare version string
`vX.Y.Z` that the Step 8 publication workflow sets; see Step 9).

It does not cover: deciding whether the changes warrant a patch, minor, or
major version (a maintainer decision made before this SOP is invoked); the
hotfix/backport path (no such path is defined yet — should one ever be
needed, it is an exception to this SOP and must be recorded in its
`Updates`); and the internals of the `publish.yml` workflow (OIDC trusted
publishing, `server.json` generation).

This procedure assumes a working checkout of this repository on the `dev`
branch with `git`, `uv`, `jq`, and an authenticated `gh` CLI on the
`PATH`. The staged script is written against the old `gh` 2.4.0 that this
environment ships, so it avoids `gh` conveniences that newer releases
added (`gh run list --commit`, `gh run view --json jobs`, `gh release
edit`, `--ff`-style merge flags) — see Safety and Precautions. The gates
themselves do not depend on the `gh` version.

The nine procedure steps map one-to-one onto the stages of
`scripts/release.sh`, which execute in this order: `resolve` → `precheck`
→ *(step 3 — the agent's, not a stage)* → `bump` → `changelog` →
`commit-push` → `pr-create` → *(the merge gate — the maintainer's, not a
stage)* → `pr-merge` → `tag-push` → `publish-wait` → `release-notes`.
Every stage is idempotent: a stage that has already completed reports
success and exits, so a failed release is resumed by re-running the
failed stage — never by restarting from `resolve`.
`scripts/release.sh status <X.Y.Z>` shows where the release stands at any
point.

## Definitions

- **Release commit**: the single commit on `dev` touching exactly three
  files — `pyproject.toml`, `uv.lock`, `CHANGELOG.md` — with the message
  `chore(release): bump version to vX.Y.Z`.
- **Release name**: the title of the GitHub Release — the bare version
  string `vX.Y.Z`, matching the tag, set by the publication workflow's
  "Make GitHub Release" job (Step 8) and never modified by the
  procedure. Releases v0.16.0–v0.37.0 carry a changelog-derived
  headline of the form `vX.Y.Z - <text>` instead; that behaviour was
  introduced 2026-09-01 and reverted 2026-10-22 (see Updates), and the
  revert applies only to newer releases.
- **Fast-forward invariant**: `main` is always an ancestor of `dev`, i.e.
  `main` carries no unique commits. The invariant is what makes the
  `dev` → `main` merge possible in fast-forward-only form, and it must
  hold before every release.
- **Stage**: a subcommand of `scripts/release.sh` (e.g. `precheck`,
  `bump`, `pr-merge`). Stages mirror the steps of this procedure one-to-
  one, are idempotent (a completed stage reports "done" instead of
  re-running), and are the only sanctioned way for the agent to perform
  release mechanics.
- **`/release`**: the OpenCode command (`.opencode/command/release.md`)
  that drives the stages and performs this SOP's agent-judgment steps
  (version confirmation, changelog curation, merge gate, failure triage).
- **Publication jobs**: the four jobs of
  `.github/workflows/publish.yml`, triggered by pushing a `v*` tag:
  *Publish to TestPyPI* → *Publish to PyPI* → *Make GitHub Release* →
  *Publish to MCP Registry*.
- **`[Unreleased]` section**: the Keep a Changelog staging area at the top
  of `CHANGELOG.md` that accumulates notable changes between releases.
- **Merge gate**: the maintainer's explicit go-ahead to merge the release
  pull request, given after the agent presents it (Step 6).
- **Delivery commit**: the `merge_commit_sha` of the newest merged PR
  under a branch's or feat folder's lookup — the real `dev`-side commit
  for both squash- and merge-PRs (a squash merge rewrites the branch
  head, so head-SHA ancestry is the wrong test). The Step 2 closeout
  gate and branch cleanup key their window and staleness tests on it.
- **Stale branch**: a `feat-*`/`fix/*` branch (local and/or on
  `origin`) whose delivery commit is an ancestor of the latest release
  tag (`vPrev`) — it shipped in the previous release or older, hence it
  is deletable at the current release's precheck (Step 2, sub-item (h)).
- **Issue-number prefix**: the `feat-<NNN>-` prefix of a feat folder's
  id, where `NNN` is the GitHub issue number (unique per folder). The
  closeout gate's fallback lookup key for work merged from a renamed
  branch (Step 2, sub-item (g)); `feat-0-*` folders carry no issue
  number and stay exact-match only.

## Roles and Responsibilities

### Accountable

The repository maintainer (`dfch`) is accountable for every release and
for the continued validity of this procedure: they make the version
decision, confirm the resolved version number (Step 1), approve the merge
gate (Step 6), and adjudicate any exception.

### Responsible

- The release agent (the OpenCode session executing `/release`) runs the
  stages in order, performs the changelog curation (Step 3), and reports
  progress and failures. In manual mode the maintainer performs every
  step themselves.

### Support

- `scripts/release.sh` — the deterministic stage implementations
  (pre-checks, file edits, git/gh mechanics, CI polling).
- GitHub Actions — `ci.yml` (lint, tests, and docs-drift checks on `dev`
  and on the pull request) and `publish.yml` (the four publication jobs).
- The `uv` and `gh` CLIs, and the external publication targets: TestPyPI
  and PyPI (both via OIDC trusted publishing) and the MCP Registry (via
  `mcp-publisher` with GitHub OIDC).

### Consulted

- The maintainer is consulted at exactly two gates: the version
  confirmation after `resolve` (Step 1) and the merge gate after
  `pr-create` (Step 6).

### Informed

- Downstream consumers are informed via the GitHub Release (notes plus
  sdist/wheel artifacts), the PyPI and TestPyPI project pages, and the MCP
  Registry listing.

## Safety and Precautions

- **Tag push is irreversible.** Pushing the tag immediately starts
  publication to TestPyPI, PyPI, and the MCP Registry. A published version
  cannot be retracted, only superseded by a newer one. Never push a tag
  whose preconditions (Steps 1–5) have not all succeeded.
- **Merge fast-forward only.** Never create a merge commit or squash-merge
  when merging `dev` into `main` — a commit unique to `main` breaks the
  fast-forward invariant and poisons every later release. The script
  enforces this in three places: it asserts `origin/main` is an ancestor
  of `origin/dev` *before* merging, it performs the merge *locally* —
  `git merge --ff-only` of `origin/dev` on `main`, pushed directly, with
  the pull request (which has served as the CI check gate) closed
  afterwards — and it re-asserts `origin/main == origin/dev` *after* the
  merge. The local `--ff-only` merge is the only deterministic
  fast-forward available here: the plain `gh pr merge --merge` method
  cannot be relied on to fast-forward (during the v0.16.0 release it
  created a merge commit on `main` although the invariant held), and this
  environment's `gh` 2.4.0 ships no `--ff`-style flag. `pr-merge` also
  *polls* for green checks rather than fail-fasting on pending ones:
  `ci.yml` triggers on both `push` and `pull_request`, so the release PR
  starts a second CI run of the same commit whose check-runs can register
  only after `pr-create` was already satisfied by the first (push) run's
  green jobs (v0.16.0 incident). Manual mode uses the same
  `git merge --ff-only dev`.
- **Never double-bump.** If `pyproject.toml` already carries the target
  version, the `bump` stage refuses to run. If a stage failed mid-release,
  resume from the failed stage — every stage is idempotent, and
  `scripts/release.sh status <version>` shows where the release stands —
  rather than restarting the flow from scratch.
- **An empty `[Unreleased]` section is a stop condition.** A release that
  documents nothing is almost always a mistake; the `changelog` stage
  refuses to proceed without explicit confirmation (and fails outright in
  non-interactive mode).
- **The release commit is exactly three files.** Any other pending change
  in the working tree means unfinished work would be mixed into the
  release; the pre-check and `commit-push` stages assert the tree state
  and stop otherwise.
- **CI failures stop the release.** A red build on `dev` or on the release
  pull request is never force-merged or skipped: diagnose, fix on `dev`,
  and resume from the failed stage.
- **The script targets the old `gh` in this environment.** The environment
  ships `gh` 2.4.0, which predates `gh run list --commit`,
  `gh run view --json jobs`, `gh release view --json`, `gh release edit`,
  and any `--ff`-style merge flag. The script therefore finds the
  publication run by workflow *name* ("Publish to PyPI") plus the tag's
  commit SHA (filtered with `jq`), lists that run's jobs from the plain
  `gh run view` output, and reads and updates the GitHub Release through
  `gh api`. Upgrading `gh` is optional; if you do, keep the stages' gates
  identical when modernizing these call sites.
- **The branch cleanup is the only mutating precheck sub-item.** Step 2's
  sub-item (h) deletes refs — local and `origin` — unlike every other
  precheck, which is read-only. That is safe because every deletion is
  proven by a merged PR for the branch's head ref whose delivery commit
  is an ancestor of `vPrev` (the branch shipped), and the four guards
  exclude live work (checked out in a worktree), in-flight or abandoned
  branches (no merged PR), current-release branches (delivery inside
  `vPrev..HEAD`), and ambiguous tip pairs (local tip ≠ `origin` tip);
  the `-D` fallback for the local ref is justified by that same proof.
  The closeout gate runs before the cleanup, so a gate failure mutates
  no ref; `--dry-run` makes the cleanup report-only; and a failed
  deletion stops the precheck with an actionable manual step — the
  idempotent re-run resumes from the remaining side.

## Procedure

### Step 1: Resolve and confirm the target version

Start from the maintainer's decision: either a full semantic version
(`0.15.0`) or a bump keyword (`patch`/`minor`/`major`).

**Automated:** `scripts/release.sh resolve <arg>` computes the target
version — the keyword is applied to the current `pyproject.toml` version
per SemVer (e.g. `0.14.0` + `minor` → `0.15.0`) — and prints it without
mutating anything. The agent then confirms the resolved number with the
maintainer before anything else runs; a keyword that produces a
surprising number (e.g. `major` on a `0.x` version → `1.0.0`) must be
explicitly acknowledged.

**Manual fallback:** read the `version` field of `pyproject.toml`, apply
the SemVer bump by hand, and record the target version.

### Step 2: Run the pre-release checks

**Automated:** `scripts/release.sh precheck` verifies, in order: (a) the
checkout is on `dev` with a clean tree in sync with `origin/dev`; (b)
`origin/main` is an ancestor of `origin/dev` (the fast-forward
invariant); (c) the latest CI run on `dev` is green (waiting for an
in-flight run, polling every 30 s); (d) the tag `vX.Y.Z` exists neither
locally nor on `origin`; (e) `uv lock --check` passes, i.e. `uv.lock` is
in sync with `pyproject.toml` before the bump; (f) the `uv` and `gh` CLIs
are present and `gh` is authenticated; (g) the feat closeout gate — every
`.specmgr/feat/feat-*/` folder whose implementation merged into the
current release window (`vPrev..HEAD`, `vPrev` the latest release tag
reachable from `dev` via `git describe --tags --abbrev=0`; with no tag at
all the window is `HEAD`) must be closed out to `status: done`, where
"merged" is the newest merged PR under the folder id (its exact head ref,
extended by the issue-number prefix `feat-<NNN>-` for work merged from a
renamed branch) whose delivery commit is an ancestor of `HEAD` but not of
`vPrev`; a violation fails the precheck with one actionable line per
offending feat plus the remediation pointer, and a missing or unparseable
`status:` line is a violation in its own right — the gate blocks, never
skips; feats with no merged PR (plan-only or in-flight) and deliveries
inside `vPrev` are never gated; (h) the previous-release branch cleanup —
the local and `origin` `feat-*`/`fix/*` branches whose delivery commit is
an ancestor of `vPrev` (stale) are deleted on every side that exists,
each side independently: the local ref via `git branch -d` (a refusal is
the expected squash-merge case, so `-D` follows, justified by the
merged-PR proof) and the `origin` ref via `git push origin --delete`, a
one-side branch being deleted and reported on its side alone; the
cleanup's four guards — (a) the branch is checked out in a worktree,
(b) it has no merged PR, (c) its delivery is inside `vPrev..HEAD`
(current release — it becomes deletable at the next precheck), (d) its
local and `origin` tips differ — are evaluated per branch in that order
and the first guard that fires wins, emitting exactly one report line
naming the branch and that guard (a delivery that is an ancestor of
neither `vPrev` nor `HEAD` is kept with a fail-safe line); under
`--dry-run` the cleanup is report-only (the would-delete/would-keep
table, no ref is deleted), and with no prior tag it deletes nothing and
reports the skip. The gate runs before the cleanup, so a gate failure
stops the precheck with zero ref mutations. Any failure stops the release
with a diagnostic.

**Manual fallback:** run the checks individually: `git status`;
`git fetch && git merge-base --is-ancestor origin/main origin/dev`;
`gh run list --limit 30 --json databaseId,headSha,headBranch,event,name,status,conclusion --jq '[.[] | select(.headBranch == "dev" and .name == "Lint and Test" and .event == "push")] | .[0]'` (this `gh` version has no `--branch` flag; the name/event filters keep dependabot "Graph Update" runs and pull_request runs out of the gate — SOP Updates 2026-10-06); `git tag -l vX.Y.Z` and
`git ls-remote --tags origin vX.Y.Z`; `uv lock --check`;
`gh auth status`; for (g), verify that every feat folder shipped in the
window (`vPrev..HEAD`, or `HEAD` with no prior tag) is closed out to
`status: done` in its `.specmgr/feat/<id>/README.md` frontmatter — or
simply run the `precheck` stage, which enforces it; for (h), delete the
stale `feat-*`/`fix/*` branches per the same four guards — or run the
`precheck` stage, which does so with the merged-PR proof.

### Step 3: Curate the changelog

Bring the `[Unreleased]` section of `CHANGELOG.md` to the point where it
fully describes everything user-visible since the last tag, organized
under Keep a Changelog categories (`Added`, `Changed`, `Deprecated`,
`Removed`, `Fixed`, `Security`).

**Automated:** the agent (not the script) performs this step. It diffs
`git log <last-tag>..HEAD --oneline` against the existing `[Unreleased]`
entries, adds missing items, rewrites internal or verbose entries into
user-facing prose, and presents the finished section to the maintainer for
review. This is the only step in which the agent edits a file directly.

**Manual fallback:** edit the `[Unreleased]` section by hand to the same
standard.

### Step 4: Bump the version and sync the lockfile

**Automated:** `scripts/release.sh bump <X.Y.Z>` sets the `version` field
of `pyproject.toml` (asserting exactly one version line exists, and
refusing if the current version already equals the target), runs
`uv lock`, and asserts the resulting `uv.lock` diff is only the version
line. The stage tolerates the dirty `CHANGELOG.md` left by Step 3.

**Manual fallback:** edit the `version` field of `pyproject.toml` to
`X.Y.Z`; run `uv lock`; verify via `git diff uv.lock` that only the
`biz-dfch-specmgr` version entry changed.

### Step 5: Finalize the changelog, commit, push, and wait for CI

**Automated:** `scripts/release.sh changelog <X.Y.Z>` mechanically moves
the `[Unreleased]` content into a new dated section
`## [X.Y.Z] - YYYY-MM-DD` directly under a re-emptied `## [Unreleased]`
header (refusing an empty section — see Safety and Precautions). Then
`scripts/release.sh commit-push <X.Y.Z>` asserts the working-tree changes
are exactly the three release files, commits them as
`chore(release): bump version to vX.Y.Z`, pushes `dev`, and waits for the
push-triggered CI run (the lint/tests/docs-drift matrix), polling every
30 s.

**Manual fallback:** move the section by hand (this repo uses no compare-
link references in the changelog); `git add pyproject.toml uv.lock
CHANGELOG.md`; commit with the conventional message; `git push origin
dev`; watch the Actions run until green.

A red build stops the release: fix on `dev` and resume from the failed
stage.

### Step 6: Merge `dev` into `main` (pull request, fast-forward only, with merge gate)

**Automated:** `scripts/release.sh pr-create <X.Y.Z>` creates — or resumes
— the `dev` → `main` pull request with the new dated changelog section as
the pull request body, waits until the pull request's checks are green
(30 s polling), and prints the pull request URL and head SHA — without
merging. The agent then presents the pull request and the changelog
section to the maintainer and asks for the merge gate. Once approved,
`scripts/release.sh pr-merge <X.Y.Z>` waits until the pull request's
checks are green (30 s polling, like `pr-create` — a single re-check
fail-fasts on the pending second CI run from the `pull_request` trigger;
see Safety and Precautions), asserts the fast-forward invariant
(`origin/main` an ancestor of `origin/dev`), merges *locally* with
`git merge --ff-only` of `origin/dev` on `main` and pushes `main`
directly (closing the pull request, which has served as the CI check
gate — the plain `gh pr merge --merge` method cannot be relied on to
fast-forward), and re-asserts that `origin/main` equals `origin/dev`.

**Manual fallback:** `gh pr create --base main --head dev` (body: the new
changelog section); wait for green checks; present to the maintainer; on
approval, `git checkout main && git merge --ff-only dev && git push origin
main`. Never use `--no-ff`, squash, or rebase merges.

### Step 7: Tag the release and push the tag

**Automated:** `scripts/release.sh tag-push <X.Y.Z>` checks out `main`,
runs `git pull --ff-only` (main now equals dev), creates the lightweight
tag `vX.Y.Z` at `main`'s HEAD, pushes the tag, and switches back to
`dev`.

**Manual fallback:** `git checkout main && git pull --ff-only && git tag
vX.Y.Z && git push origin vX.Y.Z && git checkout dev`.

Warning: pushing the tag immediately starts publication (Step 8); the
release is irreversible from here.

### Step 8: Wait for the publication jobs

**Automated:** `scripts/release.sh publish-wait <X.Y.Z>` waits for the
publication run triggered by the tag — the workflow *file* is
`.github/workflows/publish.yml`, but its *name* (the `name:` key) is
"Publish to PyPI", and the script locates the run by that name plus the
tag's commit SHA, since `gh run list --workflow` filters by name —
*Publish to TestPyPI* → *Publish to PyPI* → *Make GitHub Release*
(creates the release with the bare version as its name — the name the
procedure keeps — and attaches the sdist and wheel) → *Publish to MCP
Registry* (updates `server.json`'s version and publishes via OIDC) —
polling every 30 s until all four jobs complete.

**Manual fallback:** watch the `publish.yml` Actions run for the tag until
all four jobs are green.

Any failed job stops the release: report the run URL, diagnose from its
logs, and escalate to the maintainer. The tag already exists, so the
remedy is never re-tagging — it is a fix plus a new, higher version.

### Step 9: Verify the publication and finalize the release notes

**Automated:** `scripts/release.sh release-notes <X.Y.Z>` verifies the
GitHub Release exists with both artifacts (sdist and wheel) and sets
the release notes to the section's content (through `gh api` — this
environment's `gh` has no `gh release edit`); the release name is left
as the bare version string set by the Step 8 workflow (the
`v<X.Y.Z> - <text>` name-text derivation that used to live here was
reverted 2026-10-22, see Updates). The stage prints the final summary:
version, tag, GitHub Release URL, PyPI and TestPyPI project URLs, and
the MCP Registry listing.

**Manual fallback:** open the GitHub Release, confirm both assets are
attached, and paste the new changelog section into the release body —
leaving its title as the bare version string `vX.Y.Z`.

The release is complete when all four publication targets are reachable
and the maintainer is informed.

## More Information

The staged script and the `/release` command are projections of this SOP:
the SOP is the normative procedure, and where the two ever disagree the
SOP wins and the script/command must be corrected. Stages are named to
mirror the step order so that drift between the document and its
implementations stays visible.

The first release executed under this SOP (v0.15.0, 2026-08-31) surfaced
two script defects against `gh` 2.4.0: `pr-merge` passed a `--ff-only`
flag that no `gh` release provides, and `publish-wait`/`status`/
`release-notes` used call sites old `gh` does not support (`gh run list
--commit`, the workflow *file* name in `--workflow`, `gh release view
--json`, `gh release edit`). The script was rewritten to
version-independent equivalents (see Safety and Precautions) and this SOP
was corrected to describe the merge mechanism the script actually uses.

The v0.16.0 release (2026-09-01) surfaced two further `pr-merge`
defects, both fixed in the script and documented in Safety and
Precautions: it fail-fasted on a *pending* check suite (the
`pull_request` trigger's second run of the release commit registering
its check-runs only after `pr-create` had been satisfied by the `push`
run's green jobs), and the plain `gh pr merge --merge` method created a
merge commit on `main` although the fast-forward invariant held — caught
by the post-merge SHA assertion before anything was tagged or published.
The invariant was repaired by a `--force-with-lease` push of `main` back
to the release commit, after which the release completed (tag `v0.16.0`,
publication run
https://github.com/dfch/biz.dfch.SpecMgr/actions/runs/33484265428, all
four jobs green). The merge is now a local `git merge --ff-only` plus a
direct push of `main`, with the pull request closed afterwards.

The `sop` tooling that manages this document (the `specmgr-test` MCP
server) runs against this repository's own dev tree; until the first
release ships the `sop` domain to PyPI, this SOP is created and validated
directly against the local checkout.

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-10-24 17:56:57.000+02:00 - Precheck gains a feat closeout gate and previous-release branch cleanup (feat-233, issue #233)

The 2026-10-23 manual cleanup — stale `feat-*`/`fix/*` branches deleted
by hand and the feat-129/feat-214 plans closed out by hand (commits
`b5cd89c`/`4a33271`) — exposed two gaps the release flow did not enforce.
This change folds both into `scripts/release.sh precheck` (Step 2) as two
new sub-items, in run order:

- **Sub-item (g), the feat closeout gate.** Every `.specmgr/feat/feat-*/`
  folder whose implementation merged into the current release window
  (`vPrev..HEAD`, `vPrev` the latest release tag; with no prior tag the
  window is `HEAD`) must be closed out to `status: done`. "Merged" is the
  newest merged PR under the folder id (its exact head ref, extended by
  the issue-number prefix `feat-<NNN>-` for work merged from a renamed
  branch) whose delivery commit is an ancestor of `HEAD` but not of
  `vPrev`. Any violation fails the precheck with one actionable line per
  offending feat plus the remediation pointer; a missing or unparseable
  `status:` line is a violation in its own right (the gate blocks, never
  skips); feats with no merged PR (plan-only or in-flight) and deliveries
  inside `vPrev` are never gated.
- **Sub-item (h), the previous-release branch cleanup.** The local and
  `origin` `feat-*`/`fix/*` branches whose delivery commit is an ancestor
  of `vPrev` (stale) are deleted on every side that exists, each side
  independently (the local ref via `git branch -d` with the `-D` fallback
  justified by the merged-PR proof, the `origin` ref via `git push origin
  --delete`; a one-side branch is deleted and reported on its side
  alone), guarded by the four hazards — (a) worktree-checked-out, (b) no
  merged PR, (c) in-window delivery, (d) local≠`origin` tips — evaluated
  in order — the first guard that fires wins, emitting exactly one
  report
  line. Under `--dry-run` the cleanup is report-only (the
  would-delete/would-keep table, no ref is deleted); with no prior tag it
  deletes nothing and reports the skip.

The gate runs before the cleanup, so a gate failure stops the precheck
with zero ref mutations. Definitions gains *delivery commit*, *stale
branch*, and *issue-number prefix*; Safety and Precautions records that
the branch cleanup is the only mutating precheck sub-item and why the
merged-PR proof plus the four guards make that safe; Step 2's manual
fallback names how both sub-items reduce by hand. The script's
header/usage comment, the `/release` command, and the README "Make a
Release" section are synced to the same behaviour (feat-233).

### 2026-10-22 18:56:02.000+02:00 - Release name behaviour reverted: releases carry the bare version again

The maintainer decided that a new release carries only the version
number as its GitHub Release title (e.g. `v0.38.0`), reverting the
`vX.Y.Z - <text>` name-text behaviour introduced 2026-09-01 (the two
Updates entries dated that day). Surfaces changed: the
`release-notes` stage of `scripts/release.sh` no longer takes a
name-text positional (a second positional is now rejected like any
other stage argument), no longer composes or sends a release name (it
PATCHes the notes only), and its idempotency check compares the stored
body alone, ignoring the stored name; the `/release` command no longer
derives or passes name text (and no longer lists a release name in its
success summary); and this SOP's Scope, `Release name` definition,
Step 8, and Step 9 were updated accordingly — Step 9 no longer has an
agent-judgment part. The release name is whatever the publication
workflow's "Make GitHub Release" job sets — the bare version string
via `gh release create --title "${VERSION}"` — and the procedure never
modifies it. Existing releases (v0.16.0–v0.37.0) keep their names; the
revert applies only to newer releases. `tests/test_release_sh.py`
pins the body-only PATCH, the name-blind "already set" check, and the
2nd-positional rejection.

### 2026-10-15 14:29:18.000+02:00 - v0.36.0 released under this SOP; the pr-merge already-merged close race recurred (issue #213) and close_pr_if_open was hardened

The v0.36.0 release (PR #212) hit the already-merged-close symptom a
second time: `pr-merge`'s local fast-forward merge of `origin/dev` onto
`main` + direct push succeeded fully (`origin/main` and `origin/dev` both
at `91d2b57`), but the final `close_pr_if_open` read the PR state in the
window before GitHub's async merge detection flipped the PR to `MERGED` —
the read came back empty/stale, so `gh pr close` was issued against the
already-merged PR and failed ("can't be closed because it was already
merged"), killing the stage non-zero under `set -euo pipefail` after the
work had succeeded: `pr-merge: done` was never printed. (The first
occurrence, v0.35.0 — logged in the 2026-10-06 entry — is what introduced
`close_pr_if_open` itself, commit `0cdaa98`; issue #213 is the residual
race inside the helper.) The workaround was to re-run `pr-merge` once the
race had settled — safe because the early-return guard (`origin/main`
already equals `origin/dev` → "nothing to merge") makes the re-run a
no-op.

`close_pr_if_open` is now hardened (feat-213-release, GitHub issue #213)
as a layered defense: (1) the state read is a bounded retry —
`PR_STATE_RETRY_ATTEMPTS=5` attempts, `PR_STATE_RETRY_INTERVAL=3` s
between (never after the last), each attempt info-logged, early return
on `merged`/`closed`; (2) after the budget, `gh pr close` is attempted
exactly as before (a genuinely open PR must still close); (3) a failed
close re-verifies the state once — `merged`/`closed` is the known race
(info note, success), anything else dies with an actionable message
naming the PR. The re-verify keys on the state (ground truth), not on
`gh`'s error text; the race outcomes are pinned by new fake-`gh`-shim
tests in `tests/test_release_sh.py`, and `pr-merge` now ends with
`pr-merge: done (...)` in the already-merged-by-GitHub case.

### 2026-10-06 20:15:56.000+02:00 - v0.35.0 released under this SOP; three release-script defects found and fixed

The v0.35.0 release surfaced three `scripts/release.sh` defects, all
fixed in the script (the SOP's own step descriptions were already
correct — the script had drifted from them) and covered by a new
`tests/test_release_sh.py` (a fake-`gh`-shim unittest suite that sources
the script's helpers — enabled by a `BASH_SOURCE` dispatch guard added
to the script, behavior-preserving for direct runs):

(1) The dev CI gate matched the wrong workflow. `latest_dev_run_tsv`
filtered only by `headBranch == "dev"`, so the newest run of ANY
workflow qualified; at `commit-push`'s wait, the newest dev run was a
dependabot "Graph Update" run (47 s, green, same head SHA), and the
gate declared "dev CI green" while the real "Lint and Test" push run
was still in flight. The helper now also requires the workflow name
("Lint and Test", the `name:` key of `.github/workflows/ci.yml`) and
`event == "push"` (pull_request runs also carry `headBranch "dev"`),
which fixes the same latent hazard in `precheck`'s latest-dev-CI check
and `status`'s display; Step 2's manual fallback jq one-liner carries
the same filter now.

(2) `pr-create` fail-fasted on pending checks. This environment's
`gh` 2.4.0 (Ubuntu's `2.4.0+dfsg1` build) returns `gh pr checks` exit
code 1 for PENDING checks as well as failing ones (0 only when every
registered check passes) — verified live when `pr-create` died with
"checks are failing" although every listed check was pass or pending.
`wait_for_pr_checks` now distinguishes the two by parsing the output:
a terminal failure state (`fail`/`failure`/`error`/`cancelled`/
`canceled`) dies the stage with the output; anything else keeps polling
within the existing timeout. (The v0.16.0 pending-suite fix had added
polling, but its pending-detection relied on exit codes this `gh` build
never returns.)

(3) `pr-merge` exited non-zero after a fully successful merge. The
local `git merge --ff-only` + push of `main` made GitHub mark the PR
`MERGED` itself, so the stage's final `gh pr close` hit a GraphQL
"Could not close the pull request" error. The close is now
`close_pr_if_open`: it reads the PR state via the REST API (`gh pr
view`'s default GraphQL field set breaks on today's GitHub in this
`gh` build — the Projects-classic deprecation error) and skips the
close when the PR is already `merged`/`closed`. Along the way,
`status`'s `pr` line now reports `[x] merged (tag vX.Y.Z on
origin/main)` once the tag is on `main`, instead of the misleading
"no open PR; main behind dev" for the normal post-release state, and
`help` no longer truncates its final usage line.

The publication itself was held up by an external outage, not a defect
in what we ship: TestPyPI's upload/OIDC endpoint (`test.pypi.org/
legacy/`) returned 503 while the front page and simple index stayed up
(no incident declared on status.python.org, which does not track
test.pypi.org components). Both the original publish run and one
re-run failed at the "Publish to TestPyPI" job's audience retrieval
with no file uploaded anywhere. The recovery was a manual `gh api
-X POST repos/dfch/biz.dfch.SpecMgr/actions/runs/<id>/rerun-failed-
jobs` on the SAME tag once the endpoint responded, followed by
`publish-wait` — no new version was needed since nothing had been
published. Re-running the failed publish jobs on the same tag after a
transient external failure (as opposed to "a fix plus a new, higher
version", which applies when OUR artifact or workflow is at fault) is
therefore a sanctioned operator step; a dedicated `publish-rerun`
stage was deliberately not added in this round.

### 2026-09-01 12:37:17.000+02:00 - Release name format refined (version prefix required); script and command aligned

The name set for v0.16.0 under the previous entry's rule ("Generic
delete tool") dropped the version; the maintainer wants the name to
identify the release at a glance. The `Release name` is now of the
form `vX.Y.Z - <text>` (version matching the tag, space-dash-space,
then the changelog-derived headline), and the two owed corrections
were made: the `release-notes` stage takes the name text as a second
positional argument and composes and sets the full name alongside the
notes (the non-agent `all` path passes no text, leaves the name as-is,
and says so in its output), and the `/release` command derives the
text from the curated section before calling the stage. The stage's
idempotency check was fixed along the way: GitHub returns the stored
release body with CRLF line endings (confirmed for v0.15.0 and
v0.16.0), so the comparison strips CRs — without that the stage would
re-PATCH forever and never report "already set". The v0.16.0 release
was renamed to "v0.16.0 - Generic delete tool".

### 2026-09-01 11:37:37.000+02:00 - Gap closed: the release name is derived from the changelog and set in Step 9

A gap surfaced after the v0.16.0 release: the `release-notes` stage only
ever set the GitHub Release *body* from the dated changelog section, so
the release *name* stayed the bare version string that the publish
workflow's "Make GitHub Release" job passes as `--title` — and the
workflow cannot do better, since a name derived from the changelog
section's content is agent judgment, like the Step 3 curation. Step 9
now requires the agent to derive the release name from the dated
changelog section's content (a concise title-case headline of the
section's most significant user-visible change, never the bare version
string) and to pass it to `release-notes`, which sets name and notes
together; a `Release name` definition was added, Step 8 now states that
the workflow creates the release with the bare version as its name, and
Step 9's description of the mechanism was corrected to `gh api` (this
environment's `gh` 2.4.0 has no `gh release edit`, as Safety and
Precautions already states). The script's `release-notes` stage and the
`/release` command must be corrected to match (where the two disagree,
the SOP wins); as of this entry they still set the body only.

### 2026-09-01 10:07:30.000+02:00 - v0.16.0 released under this SOP; pr-merge made deterministic (two incidents fixed)

The second release executed end to end under this SOP (v0.16.0, the
generic `delete` tool). During it, `pr-merge` tripped twice. (1) It
fail-fasted on a *pending* check suite: `ci.yml` triggers on both
`push` and `pull_request`, so the release PR started a second CI run of
the release commit whose check-runs registered only after `pr-create`'s
polling had been satisfied by the push run's green jobs — nothing was
red. (2) After the checks were green, the plain `gh pr merge --merge`
method created a merge commit on `main` although the fast-forward
invariant held; the post-merge SHA assertion caught it and stopped the
stage before tagging (nothing was published). `main` was repaired with a
`--force-with-lease` push back to the release commit, and the release
then completed: tag `v0.16.0`, publication run
https://github.com/dfch/biz.dfch.SpecMgr/actions/runs/33484265428 (all
four jobs green), GitHub Release notes set. The script was corrected:
`pr-merge` now polls for green checks like `pr-create` and performs the
merge locally with `git merge --ff-only` plus a direct push of `main`,
closing the pull request afterwards — the only fast-forward guarantee
this environment's `gh` 2.4.0 offers (v0.15.0's plain-method merge
happened to fast-forward; v0.16.0's did not). Safety and Precautions
and Step 6 were corrected to describe the mechanism the script actually
uses.

### 2026-08-31 18:27:40.000+02:00 - v0.15.0 released under this SOP; script compatibility fixes; activated

The first release executed end to end under this SOP (v0.15.0): PR #37
merged fast-forward into `main`, tag `v0.15.0` published to TestPyPI,
PyPI, the GitHub Release (notes set from the changelog section), and the
MCP Registry (publication run
https://github.com/dfch/biz.dfch.SpecMgr/actions/runs/33410331930, all
four jobs green). During the run, `scripts/release.sh` was found to rely
on `gh` features that do not exist in this environment's `gh` 2.4.0 and
was fixed (see More Information); this SOP was corrected to match (the
actual fast-forward-only enforcement, the publication workflow's name,
the old-`gh` constraints) and simplified (stage-to-step mapping up
front, prerequisites in Scope). Status changed from `draft` to `active`.

### 2026-08-31 15:19:05.000+02:00 - Created

Created as the normative procedure for releasing `biz-dfch-specmgr`,
consolidating the previously hand-run README "Make a Release" steps
(direct merge plus tag) with the new automation: the staged
`scripts/release.sh`, the `/release` OpenCode command with its
agent-judgment steps (version confirmation, changelog curation, merge
gate, failure triage), and the pull-request-plus-fast-forward-only merge
strategy that keeps `main` a strict ancestor of `dev`. Status is
`draft`; the SOP is activated once the first release executed under it
succeeds end to end (expected to be v0.15.0, the first release to carry
the `sop` domain itself).
