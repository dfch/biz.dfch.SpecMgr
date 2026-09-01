---
created: '2026-08-31 15:24:14.582Z'
id: 98537416-0e6e-4a02-925f-974a17bfa10a
status: active
type: sop
updated: '2026-09-01 12:37:17.000Z'
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
GitHub Release name and notes (the name is derived from the dated
changelog section; see Step 9).

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
- **Release name**: the title of the GitHub Release, of the form
  `vX.Y.Z - <text>`: the release's version (always matching the tag),
  a space-dash-space, and a concise title-case headline (a few words)
  naming the dated changelog section's most significant user-visible
  change, derived from the section's content. When a section has no
  single dominant change, the text is a short compound of its two main
  changes. The `release-notes` stage composes the version prefix; the
  agent supplies the text (Step 9).
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
are present and `gh` is authenticated. Any failure stops the release with
a diagnostic.

**Manual fallback:** run the checks individually: `git status`;
`git fetch && git merge-base --is-ancestor origin/main origin/dev`;
`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == "dev")] | .[0]'` (this `gh` version has no `--branch` flag); `git tag -l vX.Y.Z` and
`git ls-remote --tags origin vX.Y.Z`; `uv lock --check`;
`gh auth status`.

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
(creates the release with the bare version as its name — Step 9
replaces it — and attaches the sdist and wheel) → *Publish to MCP
Registry* (updates `server.json`'s version and publishes via OIDC) —
polling every 30 s until all four jobs complete.

**Manual fallback:** watch the `publish.yml` Actions run for the tag until
all four jobs are green.

Any failed job stops the release: report the run URL, diagnose from its
logs, and escalate to the maintainer. The tag already exists, so the
remedy is never re-tagging — it is a fix plus a new, higher version.

### Step 9: Verify the publication and finalize the release name and notes

**Automated:** first, the agent (not the script) derives the release
name *text* from the new dated changelog section's content, per the
`Release name` definition: a concise title-case headline naming the
section's most significant user-visible change. Then
`scripts/release.sh release-notes <X.Y.Z> <text>` verifies the GitHub
Release exists with both artifacts (sdist and wheel), sets the release
name — composed by the stage as `v<X.Y.Z> - <text>` — and the release
notes to the section's content (through `gh api` — this environment's
`gh` has no `gh release edit`), and prints the final summary: version,
tag, GitHub Release URL, PyPI and TestPyPI project URLs, and the MCP
Registry listing.

**Manual fallback:** derive the release name text from the dated
changelog section's content as above; open the GitHub Release, confirm
both assets are attached, set its title to `vX.Y.Z - <text>` (version
matching the tag, space-dash-space, text), and paste the new changelog
section into the release body.

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
