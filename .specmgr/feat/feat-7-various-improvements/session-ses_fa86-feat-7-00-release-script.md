# SpecMgr PR 34 status check

**Session ID:** ses_fa864e48bffeuuPGXunSYeGCqh
**Created:** 8/31/2026, 1:36:18 PM
**Updated:** 8/31/2026, 5:00:08 PM

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 41.0s)

_Thinking:_

The commit failed because I forgot to stage the file! `git commit` without `-a`, and nothing had been staged. The file is still modified/unstaged. (The reason the pre-commit warning about "Unstaged files detected" appeared was due to the stash of the modified README... it was stashed and restored, and the commit produced nothing.)

Wait, looking more carefully: after the hooks were run, it displayed "On branch dev... Changes not staged for commit: modified: .specmgr/feat/feat-7-various-improvements/README.md" — so no commit was created (no "[dev ...]" line). In the previous commit I explicitly ran `git add` first. This time I forgot to add.

Also, from the second command: the remote branches are dev, feat-31-feature, feat-32-sysrs, feat-33-vcr, main.

Note: origin/feat-31-feature still exists! PR #32 was squash-merged with `--delete-branch` specified, but that deleted `feat-30-sop` (the PR's head branch was feat-30-sop). Wait — PR #34 was feat-30-sop → dev. PR #32 was "feat(31): Formalize the Feature artifact type" — its head branch must have been feat-31-feature. Was PR #32 merged with delete-branch? I didn't do it; someone else did it previously (merged on 2026-08-30). But origin/feat-31-feature still exists on the remote! Let me check whether it's fully merged into origin/dev (if it was squash-merged, the commits won't be ancestors, but the contents should be identical, or it might have been merge-committed).

So next:

1. Stage + commit + push the feat-7 changes.
2. For each remote branch other than dev/main, check: is it merged into origin/dev? `git branch -r --merged origin/dev`. Also compare trees.

For feat-31-feature: if PR #32 was squash-merged, that branch's commits don't exist in dev's history → it'll show as unmerged, but the contents are in dev. Check `git diff origin/dev origin/feat-31-feature` — if empty (or nearly so), it's stale and can be deleted.

Let me run the commit first, then do the staleness check.

I forgot to stage the file in the commit, so I'll fix that now and then check the remote branches:

**Tool: bash**

**Input:**

```json
{
  "command": "git add .specmgr/feat/feat-7-various-improvements/README.md && git commit -m \"chore(feat-7): extend Task 0.29 with issue #27 sibling trigger\" && git push"
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...........................................(no files to check)Skipped
vulture..............................................(no files to check)Skipped
unittest.............................................(no files to check)Skipped
specmgr coverage-badge...............................(no files to check)Skipped
specmgr docs.........................................(no files to check)Skipped
specmgr mcp-docs.....................................(no files to check)Skipped
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (sop package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped
[dev 1a0daf3] chore(feat-7): extend Task 0.29 with issue #27 sibling trigger
 1 file changed, 19 insertions(+), 4 deletions(-)
To https://github.com/dfch/biz.dfch.SpecMgr.git
   03260fe..1a0daf3  dev -> dev

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 33.1s)

_Thinking:_

Committed and pushed: 1a0daf3. Next, regarding stale remote branches (excluding dev and main): the candidates are feat-31-feature, feat-32-sysrs, feat-33-vcr.

- feat-31-feature: PR #32 was squash-merged into dev (ad20f83). Check whether the branch's contents are included in dev: run `git diff origin/dev origin/feat-31-feature --stat`, and also check the open/closed state of PR #32. If the diff is empty → stale, can be deleted.
- feat-32-sysrs: According to the worktree info, there's 1 commit ahead of dev ("rebuild feature branch from clean origin/dev") — this is WIP for issue #32 (SYSRS). Active, not stale.
- feat-33-vcr: 11 commits ahead of dev (VCR implementation in progress). Active, not stale. Additionally, the local worktree is 6 commits ahead of this remote branch.

I'll check the diff for feat-31-feature and the state of PR #32.

I've pushed the commit `1a0daf3`. Now I'm checking three candidate branches, starting with `feat-31-feature` since PR #32 was squash-merged:

**Tool: bash**

**Input:**

```json
{
  "command": "git diff --stat origin/dev origin/feat-31-feature | tail -3; echo \"diff-count: $(git diff --name-only origin/dev origin/feat-31-feature | wc -l)\""
}
```

**Output:**

```
 uv.lock                                            |     2 +-
 whitelist.py                                       |    15 -
 125 files changed, 460 insertions(+), 39155 deletions(-)
diff-count: 125

```

**Tool: bash**

**Input:**

```json
{
  "command": "gh pr view 32 --repo dfch/biz.dfch.SpecMgr --json state,mergedAt,headRefName --jq '{state,mergedAt,head:.headRefName}'; echo ===; git log --oneline -2 origin/feat-32-sysrs; echo ===; git log --oneline -1 origin/feat-33-vcr"
}
```

**Output:**

```
{"head":"feat-31-feature","mergedAt":"2026-08-30T19:22:23Z","state":"MERGED"}
===
4a4fc62 docs(feat-32-sysrs): rebuild feature branch from clean origin/dev
4c7d976 chore(release): increase version to v0.14.0
===
28bd472 docs(feat-33): Verification Case Record (vcr)

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 47.3s)

_Thinking:_

Analysis:

1. **feat-31-feature**: PR #32 was merged (squash, 2026-08-30). The diff between origin/dev and origin/feat-31-feature shows 125 files changed — but this is a diff in both directions: dev contains the SOP merge (ec3d644, merged *after* feat-31's branch point... no wait). Let me think: feat-31-feature branched off from dev at some point, and PR #32 was squash-merged as ad20f83. Since it's a squash merge, the branch's commits are not in dev's history. Then dev moved on with the SOP merge (ec3d644). The diff origin/dev...origin/feat-31-feature shows what's in the branch but not in dev, and vice versa. "125 files changed, 460 insertions(+), 39155 deletions(-)" — the huge deletions suggest that dev has content (the SOP domain, ~39k lines) that isn't in the branch, plus 460 insertions = content in the branch but not in dev?

Hmm, this is concerning. If the branch has feat-31 work that isn't in dev, that would mean the squash merge lost something. But wait — the squash merge combined all of the branch's changes into a single commit ad20f83, so the *content* of the feat domain should be in dev. The 460 insertions might be the feature folder documentation (feat-31-feature/README.md, etc.)... no wait, those should have been part of the PR.

Let me verify properly: what's actually different? Compare the file lists in both directions. Actually, the cleanest check is: `git diff origin/feat-31-feature origin/dev --stat` gives the same numbers (it's symmetric). To determine whether the branch has anything that isn't in dev: `git log origin/dev..origin/feat-31-feature` (commits) — for a squash merge this will always show the branch's commits (that's how it works). Content-wise: check whether files that exist on the branch are missing from dev, or have different contents.

Let me look at the diff more carefully — enumerate which files differ, and for a few key ones (feat domain files), check the direction of the diff. Actually, a simpler approach: `git diff --name-status origin/dev origin/feat-31-feature | grep -v "^D" | head` — files that exist in the branch but not in dev (A = added in the branch relative to dev... no wait, the diff dev→branch: D means present in dev but not in the branch (i.e., dev has newer content like SOP), A means present in the branch but not in dev, M means modified.

460 insertions: could this be from a revert? Let me check the name-status output.

The `feat-31-feature` diff needs a closer look — checking direction (what the branch has that `dev` lacks, vs. what `dev` gained after the branch point):

**Tool: bash**

**Input:**

```json
{
  "command": "git diff --name-status origin/dev origin/feat-31-feature | awk '{print $1}' | sort | uniq -c; echo ===; git diff --name-status origin/dev origin/feat-31-feature | grep -E \"^(A|M)\" | head -20"
}
```

**Output:**

```
     96 D
     29 M
===
M	.github/workflows/ci.yml
M	.pre-commit-config.yaml
M	.specmgr/feat/feat-30-sop/README.md
M	.specmgr/feat/feat-7-various-improvements/README.md
M	AGENTS.md
M	CHANGELOG.md
M	README.md
M	docs/GENERATED.md
M	docs/MCP.md
M	docs/api/README.md
M	docs/api/biz.dfch.specmgr.commands.schema.md
M	docs/api/biz.dfch.specmgr.general.md
M	docs/api/biz.dfch.specmgr.general.models.paged_result.md
M	docs/api/biz.dfch.specmgr.general.resources.md
M	docs/api/biz.dfch.specmgr.general.tools.set_status.md
M	docs/api/biz.dfch.specmgr.general.tools.update.md
M	docs/api/biz.dfch.specmgr.server.md
M	docs/coverage.svg
M	pyproject.toml
M	src/biz/dfch/specmgr/commands/schema.py

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 38.9s)

_Thinking:_

No `A` entries — there's not a single file that exists in the branch but not in dev. 96 `D` entries = files that exist in dev but not in the branch (the SOP domain that was merged later). 29 `M` entries = files with different content — but since the branch was cut *before* the SOP merge (ec3d644) and several other commits (e.g., feat-7 changes from 03260fe/1a0daf3), these M entries should show the branch version differing from the dev version — i.e., dev is newer (dev's changes are missing from the branch), not the other way around.

To make sure the branch isn't ahead of dev in any file, verify that the M files differ only because dev moved forward. Simple check: for the M files, compare with the merge base. The branch's contents should match dev at the point of the squash merge… the cleanest check is: `git diff origin/feat-31-feature..origin/dev --stat` is the same set. Better approach: verify that the branch has no unique content — that is, `git log --oneline origin/dev..origin/feat-31-feature` will show the squashed branch's commits (expected in a squash merge), but as for content, compare the branch's tree with dev's tree at the point of the merge commit ad20f83:

`git diff ad20f83 origin/feat-31-feature` — if this is empty (or only feature docs?), the branch's content is fully included in the squash commit, and everything else is just dev moving forward.

Actually, ad20f83 is the squash commit in dev. If the branch's tree matches the tree of ad20f83, the branch is 100% merged content-wise. Let's check this.

No `A` entries — the branch has no files that dev is missing. The 29 `M` files are just the result of dev moving forward after the branch point (SOP merge, feat-7 edits). Currently verifying whether the branch's tree matches exactly the squash merge commit `ad20f83`:

**Tool: bash**

**Input:**

```json
{
  "command": "git diff --stat ad20f83 origin/feat-31-feature; echo \"exit: $?\""
}
```

**Output:**

```
exit: 0

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 33.8s)

_Thinking:_

`git diff ad20f83 origin/feat-31-feature` is empty — the branch tree is completely identical to the squash merge commit in dev. In other words, **feat-31-feature is fully merged content-wise and is stale → can be deleted**.

- **feat-32-sysrs**: Has 1 unique commit (4a4fc62 "rebuild feature branch from clean origin/dev") — WIP for issue #32 (SYSRS, an issue still open). Active, not stale.
- **feat-33-vcr**: 11 commits ahead of dev, VCR implementation (issue #33, open). Active, not stale. (Furthermore, there are 6 unpushed commits in the local worktree.)

Summary for the user:

1. Commit done + pushed (1a0daf3).
2. Stale branch: only `feat-31-feature` (PR #32 has been squash-merged, the tree is identical to ad20f83). feat-32-sysrs and feat-33-vcr are active WIP.

Suggestion: delete the remote branch feat-31-feature. Don't execute without confirmation.

**1. Committed & pushed:** `1a0daf3` — `chore(feat-7): extend Task 0.29 with issue #27 sibling trigger`.

**2. Stale branches (excluding dev/main):**

| Branch | Verdict |
|---|---|
| `feat-31-feature` | **Stale** — PR #32 was squash-merged (`ad20f83`), and the branch tree is byte-identical to that merge commit. Nothing unique remains |
| `feat-32-sysrs` | Active — WIP for open issue #32 (SYSRS); 1 commit ahead of dev |
| `feat-33-vcr` | Active — VCR implementation for open issue #33; 11 commits ahead of dev (plus 6 unpushed commits in its local worktree) |

Only `feat-31-feature` qualifies. Want me to delete it on GitHub?

______________________________________________________________________

## User

yes, delete feat-31-feature branch

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 25.2s)

_Thinking:_

Delete the remote branch feat-31-feature on GitHub. Use `git push origin --delete feat-31-feature` or `gh api`. `git push origin :feat-31-feature` / `git push origin --delete feat-31-feature` is the standard method.

**Tool: bash**

**Input:**

```json
{
  "command": "git push origin --delete feat-31-feature && git branch -r | grep -v HEAD"
}
```

**Output:**

```
To https://github.com/dfch/biz.dfch.SpecMgr.git
 - [deleted]         feat-31-feature
  origin/dev
  origin/feat-32-sysrs
  origin/feat-33-vcr
  origin/main

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 23.1s)

_Thinking:_

Deleted. The remaining remote branches are: dev, feat-32-sysrs, feat-33-vcr, main. Done, concise reply.

Deleted. Remaining remote branches: `dev`, `main`, `feat-32-sysrs`, `feat-33-vcr` (both active WIP).

______________________________________________________________________

## User

I want you to write a command that automates a release for this repo.

00. make sure that we are on dev branch
01. increase version in pyproject as specified in the command or ask if not provided
02. uv lock to sync pyproject and lock
03. create and update CHANGELOG for release (according to keep-a-change-log convention)
04. create "conventional commit message" (ccm) for these 3 files and push
05. eamine runner status on github that this run succeeds. this takes several minutes, so only poll every 30s
06. change to "main" branch.
07. make sure that is is "behind" dev and not "ahead" (do you know what I mean with it? maybe do this already at the very beginning)
08. create a pr to merge dev into main
09. wait until ci runners complete successfully (again 30s poll)
10. create a tag as described in README.md and push
11. wait until ci is completed successfully (again logn poll 30s)
12. watch the testpyi, pypi and github release to be created
13. on github add the contents of CHANGELOG for this release to the release notes

is this clear? make suggestions for improvement. ask

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 123.2s)

_Thinking:_

The user wants me to write a command that automates releases in this repo. Plan mode is enabled — read-only. What I should do:

1. Investigate the repo: the release section of README.md, publish.yml workflow, CHANGELOG.md conventions, current version in pyproject.
2. Understand the steps the user enumerated, and clarify ambiguities:
   - Step 7: "ensure it's 'behind' dev, not 'ahead' (do I know what you mean? maybe do this right at the very beginning)" — I think the user's intent is this: the main branch should be behind dev (i.e., dev has all of main's commits plus more, and main has no unique commits). If main were "ahead" of dev (main has commits not in dev), merging dev into main wouldn't be fast-forward / would cause divergence. So the check is: `git rev-list --count dev..main` == 0 (main has no unique commits). And this can be checked at the very beginning (before doing work on dev) — that's the user's suggestion.
   - Step 4: "conventional commit message (ccm) for these 3 files" — the 3 files being: pyproject.toml, uv.lock, CHANGELOG.md. Use the ccm agent? There's a subagent "ccm" that writes conventional commit messages for staged changes. Or just a message like `chore(release): bump version to v0.15.0` (following the repo's style: "chore(release): increase version to v0.14.0", "chore(release): set version to v0.13.0").
   - Step 10: tag as described in README.md — I need to read the tag naming convention in the README (probably `vX.Y.Z`).
   - Step 12: "watch for creation of testpyi, pypi, and the GitHub release" — the publish workflow is triggered on v\* tags. Need to read .github/workflows/publish.yml to see what jobs exist (test PyPI? upload to PyPI + test.pypi? creation of the GitHub release?). "testpyi" is probably a test PyPI upload job.
   - Step 13: add the contents of this release's CHANGELOG to the GitHub release notes (the workflow might be creating a release with an empty body. Then use `gh release edit` to set the body from the CHANGELOG section).

The user is asking: "Is this clear? Suggest improvements. Ask" — so they want clarifying questions and improvement suggestions before implementation.

First, investigate the repo to have a basis for the questions:

- README.md (release/tag section, "Add to OpenCode" was mentioned)
- .github/workflows/publish.yml
- .github/workflows/ci.yml (to know what jobs run on push to dev and on PRs)
- CHANGELOG.md (current format)
- pyproject.toml (version)
- How the CLI is structured (commands/ package — there's a typer CLI, and the user says "write a command" — probably a new `specmgr release` CLI subcommand? "I want a command written that automates the release in this repo" — a typer CLI command like `specmgr release --version X.Y.Z`? Given the repo has cli.py with commands, and that the `ccm` subagent exists for commit messages... the user says "create a 'conventional commit message' (ccm)" — this references the ccm subagent in this environment. Hmm, but if it's a standalone script, it can't use opencode subagents.

Actually, wait — re-reading: "I want a command written that automates the release in this repo." The enumerated steps include "ask if not specified" (step 1) — that's interactive, which a plain shell script can do, but the phrasing "ask" + the overall interactive nature (and the final "Is this clear? Suggest improvements. Ask") suggests they want me (the agent) to do this via a scripted workflow, or they want a script written. The fact that plan mode is enabled and they want a plan means: I should plan the automation. Options:
a) A shell script `scripts/release.sh` (or a Makefile target)
b) A new typer CLI subcommand `specmgr release` (but the CLI is a library, and the release automation needs git/gh — the cli extra has typer/rich, and adding git/gh dependencies to the CLI is a bigger design decision)
c) Just a documented procedure I execute interactively (an agent workflow)

The user says "write a command" — a single command. Given steps 1 ("ask if not specified") and 5/9/11 ("poll every 30 seconds") and 12 ("watch"), a shell script with `gh` calls fits well: `./release.sh 0.15.0` or with an interactive prompt.

I need to read the repo first. Let me look at:

- README.md (tag convention, release docs)
- .github/workflows/publish.yml (jobs, triggers)
- .github/workflows/ci.yml (jobs on dev push / PR)
- CHANGELOG.md (top section)
- pyproject.toml (version + project metadata)

Also check existing scripts/ directory, and check git tag convention (`git tag -l`).

Since it's plan mode, all read-only. Let me batch the reads.

After that, I'll present:

- Understanding + confirmation of step 7 (main must be an ancestor of dev, i.e., `dev..main` is empty. Check at the start)
- Improvement suggestions:
  - Do the main-behind-dev check at the very beginning (as the user suggests), fail-fast before bumping the version
  - Use `git rev-list --count main..dev` and `git rev-list --count dev..main`
  - Version scheme: the repo is at v0.14.0, and the next release is probably 0.15.0. Semver bump type — ask the user which (patch/minor/major) or full version
  - Commit message: repo convention is `chore(release): set version to vX.Y.Z` — but the user wants "conventional commit message for these 3 files" — suggest `chore(release): bump version to v0.15.0`, or generate with ccm
  - CHANGELOG: move [Unreleased] into a dated section. Also, add a new [Unreleased] header for the next cycle? keep-a-changelog convention — after release, an empty [Unreleased] section should remain at the top. Suggest that.
  - Tag: README says `v*` tag triggers publish. Confirm exact format (v0.14.0).
  - PR to main: branch protection? Does a PR from dev→main need review? In past releases: "v0.1.0, v0.2.0, v0.2.1 shipped to PyPI / MCP Registry, triggered by v\* tags". How did they merge dev into main? Let me check the main branch history (git log origin/main --oneline) to see if they used PRs or direct merges.
  - CI on the PR: ci.yml runs on PRs. Wait for the checks on the PR, then merge the PR? Step 8 is "create a PR to merge dev into main", and step 9 is "wait for CI runner success" — then probably merge the PR (implicit? steps 10-11 are tag + CI on tag). Actually, merging the PR is missing between 9 and 10! Suggestion: after CI passes, merge the PR (squash? no — main must remain fast-forwardable... actually, for tag-based publishing, the merge method doesn't matter much, but if main is behind dev, a regular merge (non-fast-forward) is fine). Wait — but if we merge dev into main via PR, main gets all of dev's commits. Then tag on main? Or on dev? The tag should point to the release commit — usually on main after the merge. publish.yml is triggered on v\* tags — check whether the tag is created on main or on the dev commit. Let me read publish.yml.
  - Step 12: watch for "testpyi, pypi, and github release" — read publish.yml to get the job names.
  - Step 13: `gh release edit vX.Y.Z --notes "$(extract the CHANGELOG section)"`.
  - Also: the version bump commit — in the past it was two commits? "chore(release): set version to v0.13.0" followed later by "chore(release): increase version to v0.14.0". AGENTS.md says: "Version bump: update the version in pyproject.toml (single source) and move CHANGELOG.md's [Unreleased] into a dated section, in the same commit." So 1 commit including pyproject + uv.lock + CHANGELOG.
  - uv lock: the user says "uv lock to sync pyproject and lock" — `uv lock` updates uv.lock. (AGENTS says the lockfile is committed and uses --frozen for sync. For the version bump, `uv lock` regenerates the hash in the lock.)

Improvement suggestions to make:

01. Fail-fast pre-checks (step 7 at the beginning): clean working tree, on dev, main is an ancestor of dev (dev..main empty), no tag already exists at the target version, dev is up to date with origin/dev.
02. Missing step: merge the PR (dev→main) after CI passes — between 9 and 10.
03. Tag target: create the tag on main's HEAD after the merge (confirm via publish.yml's behavior).
04. After tagging: keep [Unreleased] in the CHANGELOG (create a new empty section).
05. Polling: use `gh run watch` (has its own polling) or `gh run watch <id> --interval 30`? Actually `gh run watch` polls. There's a `--exit-status` flag. Suggest `gh run watch --interval 30` (does gh support --interval? let me recall: `gh run watch` has no --interval... actually does `gh run watch` have a `--stacks` option? I think recent gh versions don't have an interval flag. Safe bet: a loop with `gh run view <id> --json status,conclusion` + sleep 30.)
06. Test PyPI / PyPI job names — confirm from publish.yml.
07. Interactive ask for version: if not specified, propose the next minor (0.15.0) — ask with a question or prompt.
08. Release notes (step 13): extract the section between the dated header and the next header.
09. Also, after tagging, should we switch back to dev? (convenience)
10. Where to put the script: `scripts/release.sh`? Check whether the repo has a scripts directory. Or a CLI subcommand `specmgr release`? The user says "write a command" — ambiguous between "shell command/script" and "CLI subcommand". Given the heavy git/gh use and the interactive nature, a shell script is practical. But a CLI subcommand fits the repo's shape (typer app, pyproject scripts). However, adding a release command to the library CLI mixes release tooling into the library (needs `gh` binary dependency). Suggest a standalone `scripts/release.sh` (or `make release`). This repo doesn't seem to have a Makefile. Let me check.

OK, let me investigate. Read in batch:

- README.md (look for release/tag section)
- .github/workflows/publish.yml
- .github/workflows/ci.yml
- CHANGELOG.md (top)
- pyproject.toml
- git tag -l
- ls scripts (or glob)
- git log origin/main -5 (how previous releases merged into main)

Let me execute these in parallel.

Good — plan mode is on, so let me research the repo's release machinery first, then I'll confirm my understanding and ask the open questions.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.github/workflows/publish.yml"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/.github/workflows/publish.yml</path>
<type>file</type>
<content>
1: name: Publish to PyPI
2: 
3: on:
4:   push:
5:     tags: ['v*']
6: 
7: permissions:
8:   contents: write
9:   id-token: write
10: 
11: jobs:
12:   publish-to-testpypi:
13:     name: Publish to TestPyPI
14:     env:
15:       # Opt-in to Node 24 to avoid Node 20 deprecation warnings (effective June 2026)
16:       FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
17:     runs-on: ubuntu-latest
18:     environment: testpypi
19:     steps:
20:     - name: Checkout
21:       # uses: actions/checkout@v5
22:       uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8
23: 
24:     - name: Set up Python
25:       # uses: actions/setup-python@v6
26:       uses: actions/setup-python@e797f83bcb11b83ae66e0230d6156d7c80228e7c
27:       with:
28:         python-version: "3.11"
29: 
30:     - name: Install uv
31:       # uses: astral-sh/setup-uv@v5 v5.2.1
32:       uses: astral-sh/setup-uv@b5f58b2abc5763ade55e4e9d0fe52cd1ff7979ca
33:       with:
34:         enable-cache: true
35: 
36:     - name: Verify tools
37:       run: |
38:         uv --version
39:         uv run --frozen python --version
40: 
41:     - name: Install dependencies
42:       run: uv sync --frozen --all-extras --python "3.11" # NOSONAR
43: 
44:     - name: Build sdist and wheel
45:       run: uv build
46: 
47:     - name: Publish to TestPyPI
48:       # uses: pypa/gh-action-pypi-publish@release/v1
49:       uses: pypa/gh-action-pypi-publish@ba38be9e461d3875417946c167d0b5f3d385a247
50:       with:
51:         repository-url: https://test.pypi.org/legacy/
52: 
53:   publish-to-pypi:
54:     name: Publish to PyPI
55:     needs: [publish-to-testpypi]
56:     env:
57:       # Opt-in to Node 24 to avoid Node 20 deprecation warnings (effective June 2026)
58:       FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
59:     runs-on: ubuntu-latest
60:     environment: pypi
61:     steps:
62:     - name: Checkout
63:       # uses: actions/checkout@v5
64:       uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8
65: 
66:     - name: Set up Python
67:       # uses: actions/setup-python@v6
68:       uses: actions/setup-python@e797f83bcb11b83ae66e0230d6156d7c80228e7c
69:       with:
70:         python-version: "3.11"
71: 
72:     - name: Install uv
73:       # uses: astral-sh/setup-uv@v5 v5.2.1
74:       uses: astral-sh/setup-uv@b5f58b2abc5763ade55e4e9d0fe52cd1ff7979ca
75:       with:
76:         enable-cache: true
77: 
78:     - name: Verify tools
79:       run: |
80:         uv --version
81:         uv run --frozen python --version
82: 
83:     - name: Install dependencies
84:       run: uv sync --frozen --all-extras --python "3.11" # NOSONAR
85: 
86:     - name: Build sdist and wheel
87:       run: uv build
88: 
89:     - name: Publish to PyPI
90:       # uses: pypa/gh-action-pypi-publish@release/v1
91:       uses: pypa/gh-action-pypi-publish@ba38be9e461d3875417946c167d0b5f3d385a247
92: 
93:   create-github-release:
94:     name: Make GitHub Release
95:     needs: [publish-to-pypi]
96:     env:
97:       # Opt-in to Node 24 to avoid Node 20 deprecation warnings (effective June 2026)
98:       FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
99:       GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
100:     runs-on: ubuntu-latest
101:     steps:
102:     - name: Checkout
103:       # uses: actions/checkout@v5
104:       uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8
105: 
106:     - name: Set up Python
107:       # uses: actions/setup-python@v6
108:       uses: actions/setup-python@e797f83bcb11b83ae66e0230d6156d7c80228e7c
109:       with:
110:         python-version: "3.11"
111: 
112:     - name: Install uv
113:       # uses: astral-sh/setup-uv@v5 v5.2.1
114:       uses: astral-sh/setup-uv@b5f58b2abc5763ade55e4e9d0fe52cd1ff7979ca
115:       with:
116:         enable-cache: true
117: 
118:     - name: Verify tools
119:       run: |
120:         uv --version
121:         uv run --frozen python --version
122:         gh --version
123: 
124:     - name: Install dependencies
125:       run: uv sync --frozen --all-extras --python "3.11" # NOSONAR
126: 
127:     - name: Build sdist and wheel
128:       run: uv build
129: 
130:     - name: Create GitHub Release
131:       run: |
132:         VERSION=${{ github.ref_name }}
133:         gh release create ${VERSION} --title "${VERSION}" --generate-notes || true
134:         gh release upload ${VERSION} dist/* --clobber
135: 
136:   publish-to-mcp-registry:
137:     name: Publish to MCP Registry
138:     needs: [publish-to-pypi]
139:     env:
140:       FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
141:     runs-on: ubuntu-latest
142:     permissions:
143:       id-token: write
144:       contents: read
145:     steps:
146:     - name: Checkout
147:       # uses: actions/checkout@v5
148:       uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8
149: 
150:     - name: Verify tools 1
151:       run: |
152:         curl --version
153:         jq --version
154:         cat --version
155: 
156:     - name: Install mcp-publisher
157:       run: |
158:         curl -L "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/').tar.gz" | tar xz mcp-publisher
159:         chmod +x mcp-publisher
160: 
161:     - name: Verify tools 2
162:       run: |
163:         ./mcp-publisher --version
164: 
165:     - name: Update server.json version
166:       run: |
167:         VERSION=${GITHUB_REF#refs/tags/v}
168:         jq --arg v "$VERSION" '.version = $v | .packages[0].version = $v' server.json > server.tmp && mv server.tmp server.json
169:         cat server.json
170: 
171:     - name: Authenticate to MCP Registry (GitHub OIDC)
172:       run: ./mcp-publisher login github-oidc
173: 
174:     - name: Publish to MCP Registry
175:       run: ./mcp-publisher publish
176: 

(End of file - total 176 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.github/workflows/ci.yml"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/.github/workflows/ci.yml</path>
<type>file</type>
<content>
1: name: Lint and Test
2: 
3: on: [push, pull_request]
4: 
5: jobs:
6:   build:
7:     env:
8:       # Opt-in to Node 24 to avoid Node 20 deprecation warnings (effective June 2026).
9:       FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
10:     permissions:
11:       contents: read
12:     runs-on: ubuntu-latest
13:     strategy:
14:       matrix:
15:         python-version: ["3.11", "3.12", "3.13"]
16:     steps:
17:     - name: Checkout
18:       # uses: actions/checkout@v5
19:       uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8
20: 
21:     - name: Install uv
22:       # uses: astral-sh/setup-uv@v5 v5.2.1
23:       uses: astral-sh/setup-uv@b5f58b2abc5763ade55e4e9d0fe52cd1ff7979ca
24:       with:
25:         enable-cache: true
26:         python-version: ${{ matrix.python-version }}
27: 
28:     - name: Verify tools 1
29:       run: |
30:         uv --version
31: 
32:     - name: Install dependencies
33:       run: uv sync --frozen --python "${{ matrix.python-version }}" --all-extras
34: 
35:     - name: Verify tools 2
36:       run: |
37:         uv run --frozen python --version
38:         uv run --frozen ruff --version
39:         uv run --frozen pylint --version
40:         uv run --frozen vulture --version
41: 
42:     - name: Analyzing the code with pylint and ruff
43:       run: |
44:         uv run --frozen ruff format --check
45:         uv run --frozen ruff check
46:         uv run --frozen pylint $(git ls-files '*.py') || true
47: 
48:     - name: Check for dead code with vulture
49:       run: |
50:         uv run --frozen vulture src/ whitelist.py --min-confidence 60
51: 
52:     - name: Run unit tests with coverage
53:       run: |
54:         uv run --frozen coverage run -m unittest discover -v -s tests -t . -p "test_*.py"
55: 
56:     - name: Make sure `docs/` is correct
57:       # Python's inspect module (used by annotated-doc for API docs generation) formats
58:       # exception method signatures differently across Python versions (e.g., 3.12 vs 3.13).
59:       # This causes docs/ to differ when regenerated on different Python versions. To avoid
60:       # CI failures due to Python version differences rather than actual code changes, we
61:       # pin this check to Python 3.13.13 (the project's default dev version in .python-version).
62:       if: matrix.python-version == '3.13'
63:       run: |
64:         uv run --frozen --all-extras --python 3.13.13 specmgr docs
65:         git diff --exit-code -- docs/ || {
66:           echo "::error::docs/ is out of date -- run 'uv run --frozen --all-extras specmgr docs' and commit the result (see AGENTS.md)."
67:           exit 1
68:         }
69: 
70:     - name: Make sure `docs/adr/README.md` is correct
71:       if: matrix.python-version == '3.13'
72:       run: |
73:         uv run --frozen --all-extras --python 3.13.13 specmgr adr-toc
74:         git diff --exit-code -- docs/adr/README.md || {
75:           echo "::error::docs/adr/README.md is out of date -- run 'uv run --frozen --all-extras specmgr adr-toc' and commit the result (see AGENTS.md)."
76:           exit 1
77:         }
78: 
79:     - name: Make sure `docs/MCP.md` is correct
80:       if: matrix.python-version == '3.13'
81:       run: |
82:         uv run --frozen --all-extras --python 3.13.13 specmgr mcp-docs
83:         git diff --exit-code -- docs/MCP.md || {
84:           echo "::error::docs/MCP.md is out of date -- run 'uv run --frozen --all-extras specmgr mcp-docs' and commit the result (see AGENTS.md)."
85:           exit 1
86:         }
87: 
88:     - name: Make sure `docs/*_schema.json` is correct
89:       # `specmgr schema` without --type regenerates/checks ALL registered doc types
90:       # (dec, feat, gol, prb, qa, req, rsk, sop, tsk, uc) in a single run, and the command itself
91:       # exits 1 when the regenerated content differs from what was already on disk
92:       # (or the file didn't exist yet), so no separate `git diff --exit-code` step
93:       # is needed here, unlike the `docs/`/`docs/adr/README.md` checks above.
94:       # One step covers every `docs/<type>_schema.json` -- including `tsk` and
95:       # `rsk`, which never got their own dedicated step (their docs copies are
96:       # checked incidentally via this run).
97:       if: matrix.python-version == '3.13'
98:       run: |
99:         uv run --frozen --all-extras --python 3.13.13 specmgr schema || {
100:           echo "::error::docs/*_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema' and commit the result (see AGENTS.md)."
101:           exit 1
102:         }
103: 
104:     - name: Make sure `src/biz/dfch/specmgr/req/data/req_schema.json` is correct
105:       # Packaged copy of the same schema, read by the `specmgr://req/schema` MCP resource
106:       # via importlib.resources (Task 3.8) so it works from a real, non-editable install.
107:       # Same generator as the step above, just a second --output-dir.
108:       if: matrix.python-version == '3.13'
109:       run: |
110:         uv run --frozen --all-extras --python 3.13.13 specmgr schema --type req --output-dir src/biz/dfch/specmgr/req/data || {
111:           echo "::error::src/biz/dfch/specmgr/req/data/req_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type req --output-dir src/biz/dfch/specmgr/req/data' and commit the result (see AGENTS.md)."
112:           exit 1
113:         }
114: 
115:     - name: Make sure `src/biz/dfch/specmgr/uc/data/uc_schema.json` is correct
116:       # Packaged copy of the same schema, read by the `specmgr://uc/schema` MCP resource
117:       # via importlib.resources so it works from a real, non-editable install.
118:       # Same generator as the step above, just a second --output-dir.
119:       if: matrix.python-version == '3.13'
120:       run: |
121:         uv run --frozen --all-extras --python 3.13.13 specmgr schema --type uc --output-dir src/biz/dfch/specmgr/uc/data || {
122:           echo "::error::src/biz/dfch/specmgr/uc/data/uc_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type uc --output-dir src/biz/dfch/specmgr/uc/data' and commit the result (see AGENTS.md)."
123:           exit 1
124:         }
125: 
126:     - name: Make sure `src/biz/dfch/specmgr/tsk/data/tsk_schema.json` is correct
127:       # Packaged copy of the same schema, read by the `specmgr://tsk/schema` MCP resource
128:       # via importlib.resources so it works from a real, non-editable install.
129:       # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
130:       if: matrix.python-version == '3.13'
131:       run: |
132:         uv run --frozen --all-extras --python 3.13.13 specmgr schema --type tsk --output-dir src/biz/dfch/specmgr/tsk/data || {
133:           echo "::error::src/biz/dfch/specmgr/tsk/data/tsk_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type tsk --output-dir src/biz/dfch/specmgr/tsk/data' and commit the result (see AGENTS.md)."
134:           exit 1
135:         }
136: 
137:     - name: Make sure `src/biz/dfch/specmgr/rsk/data/rsk_schema.json` is correct
138:       # Packaged copy of the same schema, read by the `specmgr://rsk/schema` MCP resource
139:       # via importlib.resources so it works from a real, non-editable install.
140:       # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
141:       if: matrix.python-version == '3.13'
142:       run: |
143:         uv run --frozen --all-extras --python 3.13.13 specmgr schema --type rsk --output-dir src/biz/dfch/specmgr/rsk/data || {
144:           echo "::error::src/biz/dfch/specmgr/rsk/data/rsk_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type rsk --output-dir src/biz/dfch/specmgr/rsk/data' and commit the result (see AGENTS.md)."
145:           exit 1
146:         }
147: 
148:     - name: Make sure `src/biz/dfch/specmgr/qa/data/qa_schema.json` is correct
149:       # Packaged copy of the same schema, read by the `specmgr://qa/schema` MCP resource
150:       # via importlib.resources so it works from a real, non-editable install.
151:       # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
152:       if: matrix.python-version == '3.13'
153:       run: |
154:         uv run --frozen --all-extras --python 3.13.13 specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data || {
155:           echo "::error::src/biz/dfch/specmgr/qa/data/qa_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data' and commit the result (see AGENTS.md)."
156:           exit 1
157:         }
158: 
159:     - name: Make sure `src/biz/dfch/specmgr/prb/data/prb_schema.json` is correct
160:       # Packaged copy of the same schema, read by the `specmgr://prb/schema` MCP resource
161:       # via importlib.resources so it works from a real, non-editable install.
162:       # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
163:       if: matrix.python-version == '3.13'
164:       run: |
165:         uv run --frozen --all-extras --python 3.13.13 specmgr schema --type prb --output-dir src/biz/dfch/specmgr/prb/data || {
166:           echo "::error::src/biz/dfch/specmgr/prb/data/prb_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type prb --output-dir src/biz/dfch/specmgr/prb/data' and commit the result (see AGENTS.md)."
167:           exit 1
168:         }
169: 
170:     - name: Make sure `src/biz/dfch/specmgr/gol/data/gol_schema.json` is correct
171:       # Packaged copy of the same schema, read by the `specmgr://gol/schema` MCP resource
172:       # via importlib.resources so it works from a real, non-editable install.
173:       # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
174:       if: matrix.python-version == '3.13'
175:       run: |
176:         uv run --frozen --all-extras --python 3.13.13 specmgr schema --type gol --output-dir src/biz/dfch/specmgr/gol/data || {
177:           echo "::error::src/biz/dfch/specmgr/gol/data/gol_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type gol --output-dir src/biz/dfch/specmgr/gol/data' and commit the result (see AGENTS.md)."
178:           exit 1
179:         }
180: 
181:     - name: Make sure `src/biz/dfch/specmgr/dec/data/dec_schema.json` is correct
182:       # Packaged copy of the same schema, read by the `specmgr://dec/schema` MCP resource
183:       # via importlib.resources so it works from a real, non-editable install.
184:       # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
185:       if: matrix.python-version == '3.13'
186:       run: |
187:         uv run --frozen --all-extras --python 3.13.13 specmgr schema --type dec --output-dir src/biz/dfch/specmgr/dec/data || {
188:           echo "::error::src/biz/dfch/specmgr/dec/data/dec_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type dec --output-dir src/biz/dfch/specmgr/dec/data' and commit the result (see AGENTS.md)."
189:           exit 1
190:         }
191: 
192:     - name: Make sure `src/biz/dfch/specmgr/sop/data/sop_schema.json` is correct
193:       # Packaged copy of the same schema, read by the `specmgr://sop/schema` MCP resource
194:       # via importlib.resources so it works from a real, non-editable install.
195:       # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
196:       if: matrix.python-version == '3.13'
197:       run: |
198:         uv run --frozen --all-extras --python 3.13.13 specmgr schema --type sop --output-dir src/biz/dfch/specmgr/sop/data || {
199:           echo "::error::src/biz/dfch/specmgr/sop/data/sop_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type sop --output-dir src/biz/dfch/specmgr/sop/data' and commit the result (see AGENTS.md)."
200:           exit 1
201:         }
202: 
203:     - name: Make sure `src/biz/dfch/specmgr/feat/data/feat_schema.json` is correct
204:       # Packaged copy of the same schema, read by the `specmgr://feat/schema` MCP resource
205:       # via importlib.resources so it works from a real, non-editable install.
206:       # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
207:       if: matrix.python-version == '3.13'
208:       run: |
209:         uv run --frozen --all-extras --python 3.13.13 specmgr schema --type feat --output-dir src/biz/dfch/specmgr/feat/data || {
210:           echo "::error::src/biz/dfch/specmgr/feat/data/feat_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type feat --output-dir src/biz/dfch/specmgr/feat/data' and commit the result (see AGENTS.md)."
211:           exit 1
212:         }
213: 
214:     - name: Make sure `docs/coverage.svg` is correct
215:       if: matrix.python-version == '3.13'
216:       run: |
217:         uv run --frozen --all-extras --python 3.13.13 specmgr coverage-badge
218:         git diff --exit-code -- docs/coverage.svg || {
219:           echo "::error::docs/coverage.svg is out of date -- run 'uv run --frozen --all-extras specmgr coverage-badge' and commit the result (see AGENTS.md)."
220:           exit 1
221:         }

(End of file - total 221 lines)
</content>
```

**Tool: bash**

**Input:**

```json
{
  "command": "git tag -l | tail -10; echo ===; git log --oneline origin/main -8; echo ===; grep -n \"version\" pyproject.toml | head -5; echo ===; ls scripts 2>/dev/null || echo \"no scripts dir\"; ls Makefile 2>/dev/null || echo \"no Makefile\""
}
```

**Output:**

```
v0.2.1
v0.3.0
v0.3.1
v0.4.0
v0.5.0
v0.5.1
v0.6.0
v0.7.0
v0.8.0
v0.9.0
===
4c7d976 chore(release): increase version to v0.14.0
ad20f83 feat(31): Formalize the Feature artifact type (feat) — complete (#32)
c8f8a87 feat(sop): update design and add session transcript
a98ab53 feat(sop): add session transcript design
7647967 feat(sop): add session transcript design
889c89b feat(sop): add session transcript design
d73c06a chore(feat-7): add backlog task "consolidate 'Updates' section"
b28867b docs: record Task 0.29 validation failure investigation
===
7:version = "0.14.0"
===
no scripts dir
no Makefile

```

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n -i \"release\\|tag\" README.md | head -20; echo ===; head -40 CHANGELOG.md"
}
```

**Output:**

```
48:- [Make a Release](#make-a-release)
289:## Make a Release
310:Move the `[Unreleased]` section in `CHANGELOG.md` into a new dated
329:### 5. Create and push a version tag
333:git tag v${VERSION}
338:_Note: `.github/workflows/publish.yml` handles the rest of the release
339:automatically once the tag above is pushed — it builds and publishes the
341:stored token), creates the matching GitHub Release with the built
===
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.14.0] - 2026-08-30

### Added

- **Eleventh domain feature (FEAT/Feature tooling)**: formalized the ad hoc
  `.specmgr/feat/<id>/README.md` convention (ADR e369ee2e-3353-4f92-991c-6367d76d832e)
  into a real, schema-backed `feat` document-type domain, with full MCP tool surface,
  resources, prompts, and cross-cutting registration. Deliberately special among domains:
  uses non-UUID `feat-NNN-slug` ids (chosen by user, derived from H1 title) and
  folder-per-document addressing (`.specmgr/feat/<id>/README.md`), deviating from ADR
  8cf940c5's flat-file UUID precedent. Mirrors GOL/RSK/DEC's simple surface (no
  fine-grained mutation tools, no renderer — writes persist raw validated body
  byte-for-byte) and uses the post-feat-22 generic `update`/`set_status` dispatch
  from day one:
  - `feat/models/v1/`: Pydantic schema (`FeatFrontmatter` with a closed 4-value
    status set `planning`/`progress`/`review`/`done`, `Feature` body with mandatory
    `## Plan`/`## Progress` composites containing structured `### Requirements`
    (regex-validated list), `### Acceptance Criteria` (checked list), `### Scope`
    (mandatory `#### Included`/`#### Explicitly Out Of Scope`), optional `### Dependencies`
    (`#### Depends On`/`#### Blocks`), `### Task List` (`#### Phase N` entries each with
    `- [ ] ...` checklist), `### Updates`/`### Decisions Made` (ISO8601-enforced
    `#### {timestamp} — {title}` entries, newest-first ordered), and optional leaves),
    parser (`parse_feat`), `FeatSummary` (adds `path: str` field — the only document
    type where direct hand/agent markdown editing remains the sanctioned workflow),
    and JSON schema generation, inside the domain package itself.
  - `feat/tools/`: `@mcp.tool()` wrappers for the FEAT lifecycle (`create_feat`,
    `parse_feat`, `list_feat`, `get_feat`, `get_feat_example`, `get_feat_template`,
    `validate_feat`), plus a stub for `delete_feat`. Bespoke `_paths.py` (hand-rolled
    like ADR's own, not the shared flat-file pattern): `feat_base_dir()`/
    `find_feat_path_by_id()` (no-scan shortcut + folder-name-mismatch rejection at
    tool layer), global `feat_create_lock()` (since id doesn't exist until scanning

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 27.1s)

_Thinking:_

Very useful. Next, read the "Make a Release" section of the README (around lines 289–345) to get the exact documented procedure and tag format.

Reading the README's "Make a Release" section in full:

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/README.md",
  "offset": 285,
  "limit": 65
}
```

**Output:**

````
<path>/home/user/src/biz.dfch.SpecMgr/README.md</path>
<type>file</type>
<content>
285: 
286: The TUI requires a real TTY (raw-mode support) and does not run in a
287: headless CI job — use the CLI client there instead.
288: 
289: ## Make a Release
290: 
291: ### 1. Make sure all tests pass
292: 
293: Before releasing, make sure the CI pipeline is green on the `dev` branch:
294: 
295: ```bash
296: uv run --frozen ruff format --check
297: uv run --frozen ruff check
298: uv run --frozen pylint $(git ls-files '*.py')
299: uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"
300: ```
301: 
302: ### 2. Increase the version
303: 
304: Update the version in `pyproject.toml`:
305: 
306: ```toml
307: version = "x.y.z"
308: ```
309: 
310: Move the `[Unreleased]` section in `CHANGELOG.md` into a new dated
311: `## [x.y.z] - YYYY-MM-DD` section.
312: 
313: ### 3. Commit and push to `dev`
314: 
315: ```bash
316: git add pyproject.toml CHANGELOG.md
317: git commit -m "chore: bump version to vx.y.z"
318: git push origin dev
319: ```
320: 
321: ### 4. Merge `dev` into `main`
322: 
323: ```bash
324: git checkout main
325: git merge dev
326: git push origin main
327: ```
328: 
329: ### 5. Create and push a version tag
330: 
331: ```bash
332: export VERSION=x.y.z
333: git tag v${VERSION}
334: git push origin v${VERSION}
335: git checkout dev
336: ```
337: 
338: _Note: `.github/workflows/publish.yml` handles the rest of the release
339: automatically once the tag above is pushed — it builds and publishes the
340: `sdist`/wheel to TestPyPI then PyPI via Trusted Publishing (OIDC, no
341: stored token), creates the matching GitHub Release with the built
342: artifacts attached, and publishes `server.json` (repo root, the MCP
343: Registry publisher manifest — see the
344: [server.json format spec](https://github.com/modelcontextprotocol/registry/blob/main/docs/reference/server-json/generic-server-json.md))
345: to the [MCP Registry](https://registry.modelcontextprotocol.io/?q=io.github.dfch%2Fbiz-dfch-specmgr)
346: via `mcp-publisher`/GitHub OIDC. `biz-dfch-specmgr` is live on
347: [PyPI](https://pypi.org/project/biz-dfch-specmgr/) and in the
348: [MCP Registry](https://registry.modelcontextprotocol.io/?q=io.github.dfch%2Fbiz-dfch-specmgr)
349: as of `v0.1.0`._

(Showing lines 285-349 of 353. Use offset=350 to continue.)
</content>
````

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 118.1s)

_Thinking:_

Now I have the full picture. Main findings:

**Documented release process (README "Make a Release"):**

1. Verify tests pass locally
2. Bump version in pyproject.toml + move [Unreleased] to a dated section in the changelog
3. Commit + push to dev (`chore: bump version to vx.y.z` — README's example. Past actual commits use `chore(release): ...`)
4. Merge dev into main — **the README documents a direct merge + push to main**, not a PR!
5. Tag with `vX.Y.Z`, push, return to dev
6. publish.yml fires: TestPyPI → PyPI → GitHub Release (auto-generated notes, `|| true`) → MCP Registry

**Discrepancies with the user's steps:**

- The user's step 8 says "create a PR merging dev into main", but the README documents a direct merge. Past evidence: `git log origin/main -8` shows main contains ad20f83 (PR #32's squash commit) — i.e., main is in a fast-forward state relative to dev's history (all commits are from dev). The last commit on main is 4c7d976 (version bump), which is also on dev. So the previous release was a direct push to main (README steps 4–5), not a PR. Need to confirm: does main have branch protection that requires PRs? Can't tell from the local repo. `gh api repos/dfch/biz.dfch.SpecMgr/branches/main` will tell us. Let's check.
- User's step 7: "ensure it's 'behind' dev, not 'ahead'" — yes: main must be an ancestor of dev (`git rev-list --count dev..main` == 0), i.e., main has no unique commits. If main is ahead (has unique commits), merging dev into main won't be a fast-forward, and main will diverge. The user themselves also suggests doing this check at the start — good. That's fail-fast before touching versions.
- User's step 12: "watch testpyi, pypi, github release" — publish.yml has 4 jobs: publish-to-testpypi, publish-to-pypi, create-github-release, publish-to-mcp-registry. The user didn't mention MCP Registry — suggest watching all 4.
- User's step 13: add the release's CHANGELOG content to the release notes — the workflow does `gh release create ... --generate-notes || true`, so notes will be auto-generated (or empty if that fails). Then the script should `gh release edit vX.Y.Z --notes "$(extracted section)"`. Note: `--generate-notes` on a tag with no associated PRs/commits... actually, generate-notes works from commits between tags. No problem, we'll overwrite it later.
- Step 2 "uv lock" — README doesn't mention it, but pyproject's version change doesn't affect dependencies... wait, does `uv lock` need to run on a version bump? Does uv.lock contain the project version? Let me check: uv.lock has `name = "biz-dfch-specmgr"` and `version = "0.14.0"`. Yes, uv.lock records the package version of the root project. So a version bump in pyproject makes the lock stale → `uv lock` is needed. CI uses `uv sync --frozen`, which would fail if the lock is out of sync... actually, `--frozen` just uses the lock as-is without checking pyproject, so CI might not catch the drift, but the lock should be kept correct. The user is right to include this.
  - Let me check whether uv.lock contains the version. Grep it.
- Step 4 "ccm for these 3 files" — pyproject.toml, uv.lock, CHANGELOG.md. Past convention: `chore(release): increase version to v0.14.0` / `chore(release): set version to v0.13.0`. Suggest using a deterministic `chore(release): bump version to vX.Y.Z` (or keep using the ccm agent — but if the deliverable is a script, ccm is an opencode subagent that can't be invoked from bash. The user wrote "(ccm)" — maybe they want the commit message to be conventional-commit style. Suggest a fixed message template `chore(release): ...` matching repo history, and drop the ccm agent from the script (or, if we're asking me to run it interactively, use the ccm subagent).
- Step 1 "bump version in pyproject as specified on the command line, or ask if not provided" — CLI arg + interactive prompt fallback.
- Tag naming: README uses `v${VERSION}` (v0.14.0). publish.yml triggers on `v*` tags.

**Key design questions for the user:**

01. **Deliverable form**: (a) standalone bash script `scripts/release.sh` (recommended — no new dependencies, works anywhere with git+gh+uv), (b) new typer CLI subcommand `specmgr release` (fits the repo's shape but drags release/git/gh concerns into the library CLI, and the "ask if not provided" interactivity is awkward), (c) a documented agent workflow. The user said "write a command" — a script invoked as `scripts/release.sh [x.y.z]` is a single command.
02. **Direct push to main vs PR**: The user's step 8 says PR. README says direct merge. Which do they want? PR adds review + CI on the PR. Past releases were direct pushes (main's history == dev's history, no merge commits on main... let me check: main's log shows 4c7d976 at the tip — same commit as dev at the time, no merge commit, so it was a direct FF push or a merge). Check main's branch protection via gh api.
    - Note: if we use a PR, CI runs on the PR, then merge, then tag main's HEAD. If direct push, CI runs on the push to main. Either way, we then tag.
03. **Where to tag**: after the merge, main's HEAD (so main points to the release). If PR-merge, tag after merge. The tag must be on the release commit.
04. **Which version bump**: full `x.y.z` argument or bump type (patch/minor/major)? Suggest taking a full version string, and if not provided, default to proposing the next minor.
05. **MCP Registry job**: include in monitoring (the user listed testpyi/pypi/GH release — but the 4th job, publish-to-mcp-registry, also matters. If it fails, the release is partial). Suggest watching all 4 jobs.
06. **Pre-checks** (improvements):
    - Clean working tree
    - On dev, dev up-to-date with origin/dev
    - main is an ancestor of dev (`dev..main` empty) — at the start (fail-fast, as the user suggested)
    - CI is currently green on dev's HEAD (README step 1) — or at least confirm the last dev push passed. Suggest checking `gh run list --branch dev` latest success.
    - Target tag doesn't already exist locally or on the remote
    - CHANGELOG's [Unreleased] section is non-empty (releasing with an empty changelog is suspicious) — warn, don't fail? Or fail. Suggest warn.
    - `uv` and `gh` available, gh authenticated
07. **Changelog edit**: mechanically move the [Unreleased] section: replace `## [Unreleased]` with `## [Unreleased]\n\n## [x.y.z] - YYYY-MM-DD` (i.e., keep an empty [Unreleased] above the new dated section — keep-a-changelog convention). Also, the CHANGELOG has link references at the bottom like `[0.14.0]: https://github.com/.../compare/v0.13.0...v0.14.0`? Let me check the bottom of CHANGELOG — the top I saw had `## [0.14.0] - 2026-08-30` with no link reference. Keep-a-changelog usually has comparison links at the bottom. Let me grep. If link references exist, the script has to add one. Let me check.
08. **Polling**: 30-second loop with `gh run view <id> --json status,conclusion --jq ...`. Use `gh run list --workflow=publish.yml --tag=vX.Y.Z` etc. For PR: `gh pr checks <n> --watch`? Simpler: find the run and poll.
09. **Release notes (step 13)**: extract the `## [x.y.z] - date` section from CHANGELOG (up to the next `## `) and `gh release edit vX.Y.Z --notes "$section"`. Note: the workflow's `gh release create ... || true` — if it fails, the release doesn't exist. The script should verify the release exists before editing, and create it with notes if it's missing (fallback).
10. **After tagging**: switch back to dev (README does this).
11. **Server.json**: publish's MCP Registry job updates server.json version on the runner — no local action needed.

Let me check the link references at the bottom of CHANGELOG and main's branch protection. Also check whether uv.lock contains the version.

Then, produce a plan + questions (via the question tool? The user explicitly said "ask" — I can ask in text, but the `question` tool is designed for that. In plan mode, asking clarifying questions is expected. Use the question tool with the key decisions: script vs CLI, PR vs direct push to main, version arg style. Actually, let me keep questions to the important ones (3):

1. Deliverable: bash script `scripts/release.sh` (recommended) vs typer CLI subcommand vs just an agent workflow?
2. main strategy: user's step 8 says PR. README documents a direct push. Which? (Branch protection might force PR — let me check first!)
3. Version input: full x.y.z on the command line (with interactive prompt fallback, as stated) — or also accept a bump keyword (patch/minor/major)?

Let me gather the remaining facts: bottom of changelog, branch protection, uv.lock's version.

Two more facts to pin down — CHANGELOG link references, `uv.lock` version coupling, and whether `main` enforces PRs:

**Tool: bash**

**Input:**

```json
{
  "command": "tail -15 CHANGELOG.md; echo ===; grep -n \"version\" uv.lock | head -5; echo ===; grep -c \"compare\" CHANGELOG.md"
}
```

**Output:**

```
  TestPyPI/PyPI version, PyPI downloads, and MCP Registry badges.

### Changed

- Moved each CLI command into its own module under
  `src/biz/dfch/specmgr/commands/` (`version.py`, `mcp.py`), registered
  on the Typer `app` in `cli.py` via `app.command()(fn)`, mirroring the
  `commands/` package layout used by sibling projects (e.g.
  `biz-dfch-asdste100vocab`).
- Split `tools/adr/tools.py`'s 11 `@mcp.tool()` wrappers into one module
  per tool (`get_adr.py`, `create_adr.py`, `update_frontmatter.py`,
  `update_section.py`, `set_status.py`, `option_create.py`,
  `option_update.py`, `option_read.py`, `option_delete.py`,
  `option_list.py`, `validate_adr.py`), re-exported unchanged through
  `tools/adr/__init__.py`.
===
1:version = 1
5:    "python_full_version >= '3.15'",
6:    "python_full_version == '3.14.*'",
7:    "python_full_version >= '3.12' and python_full_version < '3.14'",
8:    "python_full_version < '3.12'",
===
1

```

**Tool: bash**

**Input:**

```json
{
  "command": "gh api repos/dfch/biz.dfch.SpecMgr/branches/main --jq '{protected: .protection != null, required_status_checks: (.protection.required_status_checks // null), required_pull_request_reviews: (.protection.required_pull_request_reviews != null), restrictions: (.protection.restrictions != null)}' 2>&1 | head; echo ===; git merge-base --is-ancestor origin/main origin/dev && echo \"main is ancestor of dev (behind: OK)\" || echo \"main has unique commits (AHEAD: problem)\""
}
```

**Output:**

```
unexpected token "!="
===
main is ancestor of dev (behind: OK)

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 42.9s)

_Thinking:_

1. At the end of CHANGELOG.md, a section of the old changelog is displayed (the "Changed" for some version — this is the 0.x section at the bottom). `grep -c "compare"` = 1 — meaning, there is one compare link somewhere. Let's find it and check the link-reference style. Actually, let's search for where the "compare" line is.

2. In the first 5 lines of uv.lock, "version = 1" (lockfile schema version) is shown, and I need to find the root project's version entry. Let's grep for the package name.

3. My gh api jq query failed because of `!=` inside jq (jq uses `!=` correctly... the error "unexpected token" — is it because of `.protection != null`? That's valid jq. Hmm, the issue might be shell quoting: single quotes... I wrapped the jq program in single quotes, so it should be fine. The actual error: `unexpected token "!="` — maybe the gh api JSON already... no. Let's redo it with a simpler query: `gh api repos/dfch/biz.dfch.SpecMgr/branches/main --jq '.protection'`. If protection is null → no branch protection → direct push is allowed.

4. main is currently an ancestor of dev → good, this confirms my understanding of step 7: "behind" = main has no unique commits = `git merge-base --is-ancestor origin/main origin/dev`.

Let's redo these checks.

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"compare\" CHANGELOG.md; echo ===; awk '/name = \"biz-dfch-specmgr\"/{print NR\": \"$0; getline; print NR\": \"$0}' uv.lock | head -4"
}
```

**Output:**

```
477:  test suite references them, never production code itself: compares a
===
111: name = "biz-dfch-specmgr"
112: version = "0.14.0"
161:     { name = "biz-dfch-specmgr", extras = ["cli"], marker = "extra == 'mcp'" },
162:     { name = "biz-dfch-specmgr", extras = ["cli", "mcp", "test"], marker = "extra == 'dev'" },

```

**Tool: bash**

**Input:**

```json
{
  "command": "gh api repos/dfch/biz.dfch.SpecMgr/branches/main --jq '.protection | if . == null then \"NO branch protection (direct push allowed)\" else \"protected\" end'"
}
```

**Output:**

```
protected

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 42.2s)

_Thinking:_

Findings:

1. The CHANGELOG has no keep-a-changelog style compare link references at the bottom (the "compare" hit is just prose). That means the dated section is simply `## [x.y.z] - YYYY-MM-DD`, and no link reference needs to be appended.

2. `uv.lock` pins the root package's `version = "0.14.0"` → the user's step 2 (`uv lock` after bumping pyproject) is indeed required.

3. `main` is **protected**. The `!= null` check in my earlier jq failed, but now "protected" has been confirmed. I need to check which protections are in place — in particular, whether PRs with reviews / status checks are required. Let me fetch the details: required status checks (strict?), required review count, whether direct pushes are allowed at all.

`gh api repos/dfch/biz.dfch.SpecMgr/branches/main/protection` — this might return 404 if only some rules are set. There's also a newer "branch ruleset" API. Let me try the classic endpoint, and rulesets if needed.

`main` is protected — checking exactly what that requires (PRs? reviews? status checks?):

**Tool: bash**

**Input:**

```json
{
  "command": "gh api repos/dfch/biz.dfch.SpecMgr/branches/main/protection --jq '{reqs: .required_status_checks.contexts, strict: .required_status_checks.strict, reviews: .required_pull_request_reviews, admin_pushes: .admin_enforced_rules}' 2>&1; echo ===; gh api repos/dfch/biz.dfch.SpecMgr/rulesets --jq '.[] | select(.target.type == \"branch\") | {name, enforcement, rules: [.rules[].type]}' 2>&1 | head -20"
}
```

**Output:**

```
{"admin_pushes":null,"reqs":null,"reviews":null,"strict":null}
gh: Branch not protected (HTTP 404)
===

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 41.3s)

_Thinking:_

The old-format protection API returned 404 "Branch not protected" — meaning the old-format `protection` object doesn't exist. The earlier check `.protection | if . == null` output "protected" because the response JSON had a `protection` key that was non-null? Hmm, actually in the case of the `/branches/main` endpoint, when there's no legacy protection, `protection` is `null`, but... it output "protected". Wait — in the case of rulesets, the `/branches/{branch}` API returns `protection: null`, and additionally the new rulesets show up separately. But my jq output "protected" — that means `.protection` was non-null... but then the direct call to `/branches/main/protection` said 404?

Actually, in recent GitHub, when branch rulesets exist, the `.protection` field of the `/branches/{branch}` response can end up being a non-null object with all fields null (like what I saw: reqs/reviews/admin_pushes/strict all null). And rulesets show up under `/rulesets`. The second command (rulesets) returned nothing (empty output after ===, head -20). Maybe the rulesets call needs pagination or a different filter, or maybe the user isn't an admin (viewing rulesets requires admin rights).

Let me retry rulesets without jq filtering, to see the raw output.

**Tool: bash**

**Input:**

```json
{
  "command": "gh api repos/dfch/biz.dfch.SpecMgr/rulesets 2>&1 | head -c 2000"
}
```

**Output:**

```
[]
```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 31.7s)

_Thinking:_

Rulesets are empty (either the user can't see them, or they don't exist). The legacy protection endpoint returns 404. However, `.protection` on the branch object was non-null... Let's look at the raw `.protection` object from /branches/main:

**Tool: bash**

**Input:**

```json
{
  "command": "gh api repos/dfch/biz.dfch.SpecMgr/branches/main --jq '.protection'; echo ===; gh api repos/dfch/biz.dfch.SpecMgr/branches/main --jq '{name: .name, protected: .protected}'"
}
```

**Output:**

```
{"enabled":false,"required_status_checks":{"checks":[],"contexts":[],"enforcement_level":"off"}}
===
{"name":"main","protected":false}

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 255.1s)

_Thinking:_

`"protected": false` — main is **not** protected. The reason the earlier check output "protected" is that the `.protection` object exists (with `enabled: false`), and it was non-null. My jq logic was wrong. The truth: **main has no branch protection — direct pushes are permitted**, which matches the README's documented flow (direct merge + push to main) and past history (main is a strict ancestor of dev, with no merge commits).

So, the user's step 8 ("create a PR to merge dev into main") **deviates** from both the README and the repo's actual history. This is the main point to confirm/suggest:

- Option A (repo convention): direct merge dev→main + push (README step 4). CI runs on push to main.
- Option B (user's step): create a PR dev→main, wait for PR's CI to go green, merge the PR (create a merge commit), then tag. Slightly safer (the merge itself gets a CI run against the combined state; PRs provide a review surface). Since main is unprotected, both work.

The user explicitly said "create a PR" — but the README says direct. Since I was asked for suggestions, I should point out this discrepancy and confirm which they prefer. My suggestion: keep it a PR (it's what the user asked for, it gets CI against the exact merged tree, and it creates a visible record for releases), and update the README's "Make a Release" section to match the new automation (or keep the README as the manual fallback). Hmm — but changing the README is scope creep, so I'll just mention it as an option.

Additional note: the PR's CI runs on the `pull_request` event → a single build matrix run for the PR. After merging, the push to main triggers another CI run. The tag run (publish.yml) is the long one (4 jobs).

Next, the commit message (step 4 "ccm for these 3 files"): files = pyproject.toml, uv.lock, CHANGELOG.md. Repo history convention: `chore(release): increase version to v0.14.0` / `chore(release): set version to v0.13.0`. The ccm subagent is an opencode agent that writes to .git/COMMIT_EDITMSG — not callable from a bash script. In a script, use a deterministic template: `chore(release): bump version to vX.Y.Z`. If the user runs this as an agent workflow (me), I can use the ccm agent. Suggestion: fixed conventional message inside the script (predictable, matches history).

Version input (step 1): "as specified by the command, or ask if not provided" → `scripts/release.sh [X.Y.Z]`, prompt if missing (read -r -p). Suggestion: additionally accept `patch|minor|major` keywords? Keep it simple: full version only, with interactive prompt suggesting the next minor. Actually, supporting bump keywords is cheap and convenient. I'll suggest it as an option.

Changelog mechanics (step 3): move the contents of `## [Unreleased]` into a new `## [X.Y.Z] - YYYY-MM-DD` section placed directly under the (now emptied) `## [Unreleased]` header. Current top of the file:

```
## [Unreleased]

## [0.14.0] - 2026-08-30
```

So the transformation is: replace the `## [Unreleased]\n\n## [0.14.0]` boundary with… General algorithm: find the `## [Unreleased]` line; take everything after it up to the next `## [` line as the unreleased content; output:

```
## [Unreleased]

## [0.15.0] - 2026-08-31

{unreleased content}

## [0.14.0] - 2026-08-30
...
```

If the unreleased content is empty → warn (nothing to release) — confirmation? Fail? I suggest a warning + proceed (the version-bump commit is still valid), or make `--force` required. I'll go with suggesting a prominent warning.

Tag (step 10): `git tag vX.Y.Z` at main's HEAD after merge, push. publish.yml triggers on `v*` tag push. Note: the tag is created **on main** (after the merge) — the README does `git checkout main; git merge dev; ... git tag`. In the PR flow: create PR → wait for CI → merge PR → now main == dev → tag main's HEAD → push tag → return to dev.

Monitoring (steps 5, 9, 11, 12):

- Step 5: CI on the dev push (build matrix ×3 Python versions + doc check). Poll the run for the push: `gh run list --branch dev --limit 1`, or capture the run via the push event. Simpler: after `git push origin dev`, find the latest run on dev and poll every 30s.
- Step 9: PR checks: `gh pr checks <pr> --watch` (gh's built-in watch) or a manual 30s poll.
- Steps 11/12: publish.yml run for the tag: `gh run list --workflow publish.yml --limit 1` or filter by tag: `gh run list --tag vX.Y.Z`. Poll all 4 jobs: publish-to-testpypi, publish-to-pypi, create-github-release, publish-to-mcp-registry. The user listed 3 ("testpyi, pypi and github release") — I'll suggest including the 4th (MCP Registry) too. A failure there means the release is partial (the MCP Registry version lags).
- Pre-check (README step 1): before starting, confirm dev's CI is currently green (latest run on dev succeeded). I'll suggest this as a pre-check.

Release notes (step 13): extract the `## [X.Y.Z] - date` section from CHANGELOG (up to the next `## `), and `gh release edit vX.Y.Z --notes "$section"`. Fallback: if the workflow's `gh release create` failed (it has `|| true`), create it myself: `gh release create vX.Y.Z --title vX.Y.Z --notes "$section"` — but in that case, the dist artifacts won't be uploaded (the workflow's upload step should also have failed). Suggestion: verify the release exists and artifacts are present; if the create-github-release job succeeded, edit the notes; if not, error out and point to the run logs (don't try to upload dist from the runner).

Where the script lives: no scripts/ directory, no Makefile. Options: `scripts/release.sh` (new directory) or a root-level `release.sh`. Repo conventions: this is a library, and adding scripts/ is fine. I'll suggest `scripts/release.sh`, executable, `set -euo pipefail`, `#!/usr/bin/env bash`.

Pre-check summary (improvements to the user's list):
0\. On dev (as the user's step 0) + clean working tree + dev up-to-date with origin/dev (pull --ff-only)

1. **main is an ancestor of dev** (the user's step 7, moved to the front as they suggested) — fail if main has unique commits
2. Latest CI run on dev is green (README step 1)
3. Target tag doesn't exist (locally or on the remote) — fail
4. Unreleased section of the CHANGELOG is non-empty — warn
5. `uv`, `gh` available; `gh auth status` OK; `git push` permissions

Additional improvement: `uv lock` — run `uv lock` (not `uv sync`), then check the diff: only the version line should change in uv.lock; if other dependency changes appear (stale lock), surface a warning (the lock may have drifted; `uv lock` updates everything). Hmm — actually, if the lock has drifted from the pyproject dependencies, `uv lock` will also update the deps, polluting the release commit. Suggestion: first run `uv lock --check`? `uv lock --check` fails if the lock is stale. Better order: before bumping the version, run `uv lock --check` to confirm the lock is in sync with pyproject (fail if not, tell the user to fix it first); after bumping the version, run `uv lock` to sync the version; then verify the uv.lock diff contains only the version line. This keeps the release commit clean (3 files). A good improvement to suggest.

Polling helper: a function `wait_for_run <run_id>` with a 30s sleep loop, checking `gh run view $id --json status,conclusion`. Timeouts? Suggest a generous timeout (e.g., 30 min) with a clear error.

Deliverable format: the user said "write a command." My suggestion: **a single bash script** `scripts/release.sh [X.Y.Z]` that does everything, invoked as one command. Not a typer subcommand (release tooling shouldn't go into the library CLI; would require `gh` and interactive TTY; the CLI is also shipped to PyPI consumers). State this reasoning concisely and confirm.

Also: the "ask if not provided" (step 1) — interactive `read` prompt; if not a TTY and no argument, fail with a usage message.

Open questions for the user (via the question tool):

1. How to merge into main: PR (your step 8; adds a CI gate on the merged tree and a visible record) vs direct push (README convention; fewer moving parts). — My suggestion: PR, as you specified. But since it contradicts the README, confirm… no wait, they explicitly wrote PR in the step, and the README says direct push. Since the README contradicts, I should ask which is authoritative. I'll present PR as the recommended option (their stated intent + CI gate), and note that the README should be updated to match.
2. Script or CLI subcommand? — I recommend a script.
3. Version argument: full X.Y.Z only, or also accept patch/minor/major keywords?

I could bundle these into a single question-tool call (up to 3 questions). The user said "ask" — so I'll use the question tool for the key decisions, and present the plan + understanding (including the confirmation of step 7) as text.

Wait — one more thing about step 5: "check that this run's GitHub runner status succeeds" — after pushing the version-bump commit to dev, CI runs (push trigger). Poll. Good.

And the tag: lightweight or annotated? README: `git tag v${VERSION}` (lightweight). publish.yml only needs the ref. To match convention, keep it lightweight.

One more: after the release, the user's flow ends with the release notes. I'll suggest ending by switching back to dev (README step 5 does `git checkout dev`).

Also: should the script update the README's "Make a Release" to document `scripts/release.sh`? I'll suggest it as an optional final step.

OK, structuring the reply:

1. Confirmation of understanding — especially the step 7 question (yes, I know what they mean: main must be a strict ancestor of dev, i.e., `dev..main` is empty; otherwise dev→main merge isn't a fast-forward and main diverges; agree to move it to the front as a fail-fast pre-check).
2. Key facts discovered (no branch protection on main → direct push is permitted; the README documents a direct merge; uv.lock pins the version → `uv lock` is required; no link references in the CHANGELOG; publish.yml has 4 jobs including MCP Registry; the GH Release is auto-created with generated notes → step 13 = `gh release edit`).
3. Proposed flow (numbered, refined version of the user's list).
4. Suggestions for improvements (the list).
5. Question tool with 3 questions.

Since I'm in plan mode, end with questions. Keep it reasonably concise, but this really does need detail. Use a table where it helps.

I have the full picture now. Let me confirm my understanding, then the open decisions.

## Understanding check

**Step 7 — yes, I know what you mean.** "main behind dev, not ahead" = `main` must be an *ancestor* of `dev` (i.e. `git rev-list dev..main` is empty, no commits unique to main). If main were ahead, merging dev→main wouldn't fast-forward and the branches would diverge — the tag/release would then not sit on a clean tip. Your instinct is right: check this **up front** as a fail-fast pre-check, before touching the version. (Verified today: main is currently a strict ancestor of dev — `protected: false`, no rulesets, so direct pushes are allowed.)

**Facts from the repo that shape the plan:**

- `uv.lock` pins the root package version (`version = "0.14.0"` at line 112) → your step 2 is genuinely needed, and the release commit is exactly 3 files: `pyproject.toml`, `uv.lock`, `CHANGELOG.md`
- CHANGELOG has **no** keep-a-changelog compare-link refs at the bottom → moving `[Unreleased]` is a pure text transform: new `## [X.Y.Z] - YYYY-MM-DD` section under an emptied `## [Unreleased]`
- `publish.yml` (tag `v*` trigger) runs **4** jobs, not 3: TestPyPI → PyPI → GitHub Release (`--generate-notes || true`, artifacts uploaded) → **MCP Registry** — your step 12 omits the 4th
- Step 13 = `gh release edit vX.Y.Z --notes "<changelog section>"` (release already exists from the workflow)
- Tag is lightweight, named `vX.Y.Z` (README), created on **main's HEAD after the merge**
- Repo has no `scripts/` dir or Makefile; commit-history convention for this commit: `chore(release): ... version to vX.Y.Z`
- **Conflict:** your step 8 says *PR* dev→main, but the README's "Make a Release" documents a *direct* merge+push (and history confirms direct pushes). Both work since main is unprotected — need your call.

## Proposed flow (refined)

Pre-checks (all fail-fast, before any change): on `dev` + clean tree + up-to-date with origin → **main is ancestor of dev** (your step 7) → latest dev CI run green (README step 1) → target tag doesn't exist → `uv lock --check` passes (lock in sync *before* the bump, so the bump commit stays exactly 3 files) → `uv`/`gh` available + authed.

01. Bump `pyproject.toml` (arg or interactive ask)
02. `uv lock` (verify only the version line changed)
03. Transform CHANGELOG `[Unreleased]` → dated section (warn if section empty)
04. Commit `chore(release): bump version to vX.Y.Z` (deterministic template, matches history — the `ccm` agent isn't callable from a bash script) + push dev
05. Poll dev's CI run, 30s interval
06. Merge dev→main (PR per your step 8, or direct per README — your call below)
07. Poll that CI, 30s
08. Tag `vX.Y.Z` on main HEAD, push tag, switch back to dev
09. Poll the publish run — **all 4 jobs** — 30s
10. Verify GH Release exists + artifacts; `gh release edit` with the changelog section as notes

Questions:

**Tool: question**

**Input:**

```json
{
  "questions": [
    {
      "question": "Your step 8 says create a PR to merge dev into main, but the README documents a direct merge+push (which history also shows). Which should the automation do?",
      "header": "dev → main merge",
      "options": [
        {
          "label": "PR (Recommended)",
          "description": "Create PR, wait for its CI, merge. CI validates the exact merged tree and the release gets a visible PR record. I'd also update the README's 'Make a Release' section to match."
        },
        {
          "label": "Direct push",
          "description": "Keep the README convention: merge dev into main locally and push. Fewer moving parts, no PR overhead."
        }
      ]
    },
    {
      "question": "What form should the automation take?",
      "header": "Deliverable",
      "options": [
        {
          "label": "scripts/release.sh (Recommended)",
          "description": "Single bash script, invoked as one command: scripts/release.sh [X.Y.Z]. Keeps release tooling (git/gh/uv) out of the library CLI, which is shipped to PyPI consumers."
        },
        {
          "label": "specmgr release CLI subcommand",
          "description": "New Typer command in cli.py. Fits the repo's command layout but drags gh/git release concerns into the shipped library and makes the interactive 'ask if not provided' step awkward."
        }
      ]
    },
    {
      "question": "How should the target version be provided?",
      "header": "Version input",
      "options": [
        {
          "label": "Full version + ask (Recommended)",
          "description": "Exactly as you described: scripts/release.sh 0.15.0, or interactive prompt if omitted (suggests next minor, refuses non-TTY)."
        },
        {
          "label": "Also accept bump keywords",
          "description": "Additionally allow patch/minor/major, computed from the current pyproject version (0.14.0 + minor → 0.15.0)."
        }
      ]
    }
  ]
}
```

**Output:**

```
User has answered your questions: "Your step 8 says create a PR to merge dev into main, but the README documents a direct merge+push (which history also shows). Which should the automation do?"="PR (Recommended)", "What form should the automation take?"="scripts/release.sh (Recommended)", "How should the target version be provided?"="Also accept bump keywords". You can now continue with the user's answers in mind.
```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 176.5s)

_Thinking:_

User's choices:

1. PR flow for dev → main (also update the "Make a Release" section in the README to match)
2. `scripts/release.sh`
3. Full version or bump keyword, with an interactive prompt fallback

Okay, so I'm still in plan mode — I need to present the final plan for approval. Let me write a concrete and complete plan for the script, including edge cases:

**Script: `scripts/release.sh`** — `#!/usr/bin/env bash`, `set -euo pipefail`.

Usage: `scripts/release.sh [X.Y.Z | patch | minor | major]`

Structure (functions):

- `die()` / `info()` helpers

- Pre-checks:

  1. `git rev-parse --abbrev-ref HEAD == dev`
  2. Working tree is clean (`git status --porcelain` is empty)
  3. `git fetch origin dev main` + dev is up-to-date with origin/dev (fast-forward check)
  4. main is an ancestor of dev: `git merge-base --is-ancestor origin/main origin/dev` → otherwise die ("main is ahead of dev")
  5. Latest dev CI run is green: `gh run list --branch dev --limit 1 --json status,conclusion` — if it's in progress, poll? The user's flow says CI gets run after the push. Pre-check: the latest completed run on dev must be success. If the latest run is in progress, wait for it first (30-second polling) — or die and ask them to wait. Simpler: if the latest run is in progress, poll it to completion (it's the current state of dev anyway).
  6. Target tag doesn't exist: `git tag -l vX.Y.Z` + `git ls-remote --tags origin vX.Y.Z`
  7. `uv lock --check` (lock is in sync with pyproject before the bump)
  8. `command -v uv gh git`, `gh auth status` (quietly)

- Version resolution:

  - Arg is full X.Y.Z (regex ^[0-9]+.[0-9]+.[0-9]+$), must be greater than the current version (compare with sort -V)
  - Arg is patch/minor/major → compute from the current pyproject version
  - No arg → prompt: show current version, suggest next minor, `read -r -p`; non-TTY with no arg → die with usage
  - Re-prompt if empty/invalid

- Changes:

  1. pyproject: replace `version = "old"` with the new version (sed against the exact line; assert there's exactly one match)
  2. `uv lock` → assert the diff of `uv.lock` contains only the version line: `git diff --unified=0 uv.lock | grep '^[-+][^-+]'` should be exactly two lines (the old version / the new version)
  3. CHANGELOG: use awk/python to transform: under `## [Unreleased]` (first occurrence), before the next `## [` heading, insert `## [X.Y.Z] - YYYY-MM-DD\n\n`. Content extraction: lines after `## [Unreleased]` up to (not including) the next line starting with `## [`. If content is empty (no non-blank lines) → warn loudly and continue? Earlier I said warn. Decision: warn and continue (they might just want to cut a version for the tag? Unlikely but their call — warn, no confirmation since the script is non-interactive except for version... hmm, in practice it's interactive enough. Warn + continue is fine; or die if empty. I think warn + continue is more flexible; but releasing an empty changelog is almost certainly a mistake. I'll go with: warn prominently and continue — no wait. Let me think about what's most useful: if [Unreleased] is empty, there's nothing to document in the release; the version bump commit is still legitimate, but they probably forgot to fill in the changelog. A confirmation prompt ("[Unreleased] is empty — continue? [y/N]") is the safe, user-friendly choice. The script already has an interactive mode (version prompt), so a second confirmation is acceptable. Non-TTY + empty → die. I'll go with confirmation prompt.)
  4. Show a `git diff --stat` summary (3 files) for review before committing? The script auto-commits per the user's flow (no manual review step in their list). I'll go with showing the diff stat and committing (their step 4 is create commit + push — automatic).

- Commit + push:

  - `git add pyproject.toml uv.lock CHANGELOG.md`
  - `git commit -m "chore(release): bump version to vX.Y.Z"` (note: pre-commit hooks run — no .py changes so all skipped except ruff format; fine)
  - `git push origin dev`

- Wait for dev CI:

  - Find the run: after the push, `gh run list --branch dev --limit 1` → but there's a delay before the run appears (a few seconds to ~1 minute). Poll for run existence for up to ~2 minutes, then `wait_for_run` every 30 seconds: `gh run view $id --json status,conclusion --jq ...`; status=completed + conclusion=success → OK; conclusion=failure/action_required → die with run URL.
  - Helper: `wait_for_run() { local id=$1; while :; do read status conclusion < <(gh run view $id --json status,conclusion --jq '[.status,.conclusion] | @tsv'); if [[ $status == completed ]]; then ...; sleep 30; done; }` with a timeout (e.g. 40 minutes → die with URL).

- PR dev→main:

  - `gh pr create --base main --head dev --title "Release vX.Y.Z" --body "<changelog section or summary>"` — PR body: the release's changelog section (useful as a record) — nice touch.
  - PR number: `gh pr view $num --json number` or parse it
  - Wait for PR checks: `gh pr checks $num` loop (30s) until all pass (no pending/failing). `gh pr checks` exit code: non-zero if any failing/pending. Loop until exit 0 or timeout. Note: the ci.yml PR run is a single "build" job with matrix → 3 checks named "build (3.11)" etc.
  - Merge: `gh pr merge $num --merge` (regular merge — creates a merge commit on main; or `--squash`? For a release, a regular merge keeps main's history aligned with dev; squash would put a single commit on main, and main would no longer be an ancestor of dev... wait, actually if you squash-merge dev into main, main gets a new commit not in dev → next time main is "ahead" of dev → violates the step-7 invariant! Important: the merge must be a **regular merge** (or fast-forward — but a regular merge with a merge commit is fine. Because after merging dev into main, main contains all of dev's commits... let me think: regular merge: main gets a merge commit M with parents main_tip and dev_tip. Is main still an ancestor of dev? No! M is not in dev. So after a regular merge, `dev..main` contains M → main is 1 commit ahead → next release's pre-check fails!)

  Hmm, wait, that's a problem for the step-7 invariant. How did past releases handle this? The README says `git checkout main; git merge dev; git push`. If dev was ahead of main, `git merge dev` from main is a **fast-forward** (since main is an ancestor of dev) → no merge commit; main just moves to dev's tip. Then main is again a strict ancestor of dev (equal, actually, until the next dev commit). So the README flow is a fast-forward merge → invariant preserved.

  In the PR flow, GitHub's merge options:

  - "Create a merge commit" → main gets a merge commit not in dev → main is 1 commit ahead of dev (that merge commit) → the next release's step-7 pre-check `merge-base --is-ancestor origin/main origin/dev` **fails** (main's tip M is not an ancestor of dev).
  - "Fast-forward" → only available when main is an ancestor of dev → exactly our pre-checked state → main moves to dev's tip, no new commit → invariant preserved.
  - "Squash" → new commit on main → invariant broken.

  So with the PR approach, we must use **`gh pr merge $num --ff-only`** (fast-forward only). Since we pre-checked that main is an ancestor of dev, ff-only will succeed. This is a critical detail — a good finding to include in the plan. If someone runs the script when main is ahead, the pre-check catches it first.

  Actually wait — does the PR's merge require main to be up-to-date? The PR is created from the current dev tip; ff merge is possible if the base (main) is an ancestor of the head (dev) — which is our pre-checked state, and main doesn't move between pre-check and merge (unprotected but nobody else is pushing — small race risk; `--ff-only` fails loudly if that happens, acceptable).

- Tag:

  - After PR merge: `git fetch origin main && git checkout main && git pull --ff-only` (or just use origin/main's SHA)
  - `git tag vX.Y.Z` at main's HEAD (== dev's HEAD), `git push origin vX.Y.Z`, `git checkout dev`

- Wait for publish:

  - Find the run: `gh run list --workflow "publish.yml" --limit 1` (or `--tag vX.Y.Z`) — poll for existence, then `wait_for_run` (30s, longer timeout, e.g. 45 minutes). The 4 jobs are sequential: testpypi → pypi → (release, mcp-registry parallel). A single run-level success covers all 4 jobs.

- Release notes:

  - Extract the `## [X.Y.Z] - date` section from the (updated) CHANGELOG (up to the next `## `)
  - `gh release view vX.Y.Z --json tagName` to confirm existence (if the job succeeded it exists)
  - `gh release edit vX.Y.Z --notes "$section"`
  - Optionally verify the artifact list is non-empty: `gh release view vX.Y.Z --json assets --jq '.assets | length'` ≥ 2 (sdist + wheel)

- Final: print a summary (PyPI URL, TestPyPI URL, GH release URL, MCP registry URL) and stay on dev.

**README update**: rewrite the "Make a Release" section to document `scripts/release.sh` (usage + version-argument variants + what it does), keeping the manual procedure as a fallback? The user chose "I'd also update the README's Make a Release section to match" (that was part of my recommended option's description). Plan: replace the manual steps with the script usage, leave a concise "what it does" list; either drop the old manual commands or keep them as a "manual fallback" subsection. I'll propose: new section = usage + behavior; keep the manual procedure as a collapsed/fallback subsection (since it's still valid if gh/uv are missing). Simplest: replace steps 2–5 with the script and leave step 1 (tests green) as a note that the script verifies it.

**Tests/verification of the script itself**: bash syntax check (`bash -n`), shellcheck if available? Not in the repo. Dry-run mode: add a `--dry-run` flag? Good improvement: `--dry-run` does pre-checks + version resolution + shows the 3-file diff but stops before commit/push. Cheap to add, very useful. I'll include it.

Edge cases to note in the plan:

- `--ff-only` merge (invariant preservation) — the key insight
- Polling helper with 30-second interval and timeout
- Non-TTY: version required as arg; empty changelog → die
- `uv lock` diff assertion (only the version line)
- pyproject version line: assert exactly one match of `^version = "`
- Date: `date +%F`
- CHANGELOG date format: `## [0.14.0] - 2026-08-30` → `## [X.Y.Z] - YYYY-MM-DD`

Plan structure (phases):

1. Write `scripts/release.sh` (executable, ~250 lines)
2. Update README's "Make a Release"
3. Verification: `bash -n`, `shellcheck` (if present), run with no args non-TTY (usage error), run with a fake version + `--dry-run` (pre-checks pass, shows diff, stops before commit), confirm the script leaves no changes behind.

Also AGENTS.md: should I mention the new script? AGENTS.md has a "Developer Commands" section — add `scripts/release.sh` there? Good: one line under Developer Commands. I'll include it.

Let me present the final plan concisely. I'm in plan mode — presenting the plan and asking for approval to execute (just presenting; the user will exit plan mode / say go).

All three decisions noted. One critical detail the PR choice forces — and it's why your step-7 instinct matters even more:

**Merge method must be `--ff-only`.** Since `main` is an ancestor of `dev` (pre-checked), GitHub's "Create a merge commit" or "Squash" would put a new commit on `main` that isn't in `dev` — making main *ahead* of dev and breaking your step-7 invariant for the **next** release. A fast-forward merge (which is exactly what the README's old `git merge dev` did) moves main to dev's tip and keeps the invariant intact.

## Plan

**Deliverable: `scripts/release.sh [X.Y.Z | patch | minor | major]`** (`set -euo pipefail`, bash; `--dry-run` flag stops after showing the 3-file diff, before any commit/push)

**Phase A — fail-fast pre-checks** (before any change):

1. On `dev`, clean tree, `git fetch`, dev == origin/dev
2. `origin/main` is an ancestor of `origin/dev` (your step 7, moved up front — dies with a clear message if main is ahead)
3. Latest `dev` CI run green (polls it to completion if still in flight)
4. Tag `vX.Y.Z` absent locally and on origin
5. `uv lock --check` passes (lock already in sync, so the bump stays exactly 3 files)
6. `uv`/`gh` present, `gh` authed

**Phase B — version + changes:**
7\. Resolve version: arg (full semver, must be > current, or `patch`/`minor`/`major` computed from `pyproject.toml`); no arg → interactive prompt suggesting next minor (non-TTY → usage error)
8\. Bump `pyproject.toml` (assert exactly one `version = "..."` line matched)
9\. `uv lock`; assert the `uv.lock` diff is *only* the version line
10\. CHANGELOG: insert `## [X.Y.Z] - YYYY-MM-DD` under an emptied `## [Unreleased]` (no link refs needed — verified); if `[Unreleased]` is empty → confirm prompt (non-TTY → die)
11\. `--dry-run` exits here with the diff shown

**Phase C — ship:**
12\. Commit `chore(release): bump version to vX.Y.Z` (matches repo history; deterministic, no `ccm` agent from bash) + push `dev`
13\. Poll the push-triggered CI run — 30s interval, ~40min timeout, die with run URL on failure
14\. `gh pr create --base main --head dev` titled `Release vX.Y.Z`, body = the changelog section
15\. Poll PR checks — 30s interval
16\. `gh pr merge --ff-only` (keeps main a strict ancestor of dev)
17\. `git checkout main && git pull --ff-only`, tag `vX.Y.Z` (lightweight, per README), push tag, `git checkout dev`
18\. Poll the `publish.yml` tag run — **all 4 jobs** (TestPyPI → PyPI → GitHub Release → MCP Registry) — 30s interval, ~45min timeout
19\. Verify release exists with ≥2 assets; `gh release edit vX.Y.Z --notes "<changelog section>"` (your step 13)
20\. Print summary links (PyPI / TestPyPI / GH Release / MCP Registry)

**Phase D — docs:**
21\. README "Make a Release": replace manual steps 2–5 with `scripts/release.sh` usage + what it does; keep the manual procedure as a fallback subsection
22\. AGENTS.md "Developer Commands": one line for the script

**Verification (no real release):** `bash -n`, non-TTY no-arg → clean usage error, `--dry-run 0.15.0` → all pre-checks pass, diff limited to the 3 files, nothing committed/pushed.

Want me to execute?

______________________________________________________________________

## User

not yet, in the end after the script is created I also want an OpenCode commadn in this repo that I will use to kick off the script

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 39.4s)

_Thinking:_

The user is saying: after the script is created, they also want an OpenCode command in this repository to launch the script.

OpenCode commands — in opencode, custom commands can be defined in `.opencode/command/*.md` (project-level) or in opencode.json. An OpenCode command is a markdown file with frontmatter, which the user invokes as `/command-name`. Since the `customize-opencode` skill is for opencode configuration (opencode.json, .opencode/, agents, commands, etc.), I should load it to get the exact format.

Let me check the current state of the repository: is there a `.opencode/` directory? Let me take a look. The skill is at the built-in location. I'll load it to get the authoritative command format.

Plan mode: read-only. I can use the skill tool (it just injects instructions) — that's fine, it's not a modification.

Let me check the existing `.opencode/` in the repo and load the skill.

**Tool: skill**

**Input:**

```json
{
  "name": "customize-opencode"
}
```

**Output:**

````
<skill_content name="customize-opencode">
# Skill: customize-opencode

<!--
  Built-in skill. Name and description are registered in code at
  packages/core/src/plugin/skill.ts
  and CUSTOMIZE_OPENCODE_SKILL_DESCRIPTION). The body below becomes the
  skill's content.
-->

# Customizing opencode

opencode validates its own config strictly and refuses to start when a field
is wrong. The shapes below cover the common surface area, but they are a
**summary, not the source of truth**.

## Full schema reference

The authoritative list of every config option — with field types, enums,
defaults, and descriptions — lives in the published JSON Schema:

**<https://opencode.ai/config.json>**

If a field is not documented in this skill, or you need to confirm an exact
shape before writing config, **fetch that URL and read the schema directly**
rather than guessing. opencode hard-fails on invalid config, so the cost of a
wrong shape is a broken startup.

Independently, every `opencode.json` should declare
`"$schema": "https://opencode.ai/config.json"` so the user's editor catches
mistakes as they type.

## Applying changes

Config is loaded once when opencode starts and is not hot-reloaded. After
saving changes to `opencode.json`, an agent file, a skill, a plugin, or any
other config-time file, **tell the user to quit and restart opencode** for
the changes to take effect. The running session will keep using the
already-loaded config until then.

## Where files live

| Scope                         | Path                                                                                                                      |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Project config                | `./opencode.json`, `./opencode.jsonc`, or `.opencode/opencode.json` (opencode walks up from the cwd to the worktree root) |
| Global config                 | `~/.config/opencode/opencode.json` or `~/.config/opencode/opencode.jsonc` (NOT `~/.opencode/`)                            |
| Project agents                | `.opencode/agent/<name>.md` or `.opencode/agents/<name>.md`                                                               |
| Global agents                 | `~/.config/opencode/agent(s)/<name>.md`                                                                                   |
| Project commands              | `.opencode/command/<name>.md` or `.opencode/commands/<name>.md`                                                           |
| Global commands               | `~/.config/opencode/command(s)/<name>.md`                                                                                 |
| Project skills                | `.opencode/skill(s)/<name>/SKILL.md`                                                                                      |
| Global skills                 | `~/.config/opencode/skill(s)/<name>/SKILL.md`                                                                             |
| External skills (auto-loaded) | `~/.claude/skills/<name>/SKILL.md`, `~/.agents/skills/<name>/SKILL.md`                                                    |

Configs from each scope are deep-merged. Project overrides global. Unknown
top-level keys in `opencode.json` are rejected with `ConfigInvalidError`.

## opencode.json

Every field is optional.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "username": "string",
  "model": "provider/model-id",
  "small_model": "provider/model-id",
  "default_agent": "agent-name",
  "shell": "/bin/zsh",
  "logLevel": "DEBUG" | "INFO" | "WARN" | "ERROR",
  "share": "manual" | "auto" | "disabled",
  "autoupdate": true | false | "notify",
  "snapshot": true,
  "instructions": ["AGENTS.md", "docs/style.md"],

  "skills": {
    "paths": [".opencode/skills", "/abs/path/to/skills"],
    "urls": ["https://example.com/.well-known/skills/"]
  },

  "references": {
    "docs": {
      "path": "../docs",
      "description": "Use for product behavior and documentation conventions"
    },
    "sdk": {
      "repository": "owner/sdk",
      "branch": "main",
      "description": "Use for SDK implementation details",
      "hidden": true
    }
  },

  "agent": {
    "my-agent": {
      "model": "anthropic/claude-sonnet-4-6",
      "mode": "subagent",
      "description": "...",
      "permission": { "edit": "deny" }
    }
  },

  "command": {
    "deploy": { "description": "...", "template": "..." }
  },

  "provider": {
    "anthropic": { "options": { "apiKey": "..." } }
  },
  "disabled_providers": ["openai"],
  "enabled_providers": ["anthropic"],

  "mcp": {
    "playwright": {
      "type": "local",
      "command": ["npx", "-y", "@playwright/mcp"],
      "enabled": true,
      "environment": {}
    },
    "remote-thing": {
      "type": "remote",
      "url": "https://...",
      "headers": { "Authorization": "Bearer ..." }
    }
  },

  "plugin": [
    "opencode-gemini-auth",
    "opencode-foo@1.2.3",
    "./local-plugin.ts",
    ["opencode-bar", { "option": "value" }]
  ],

  "permission": {
    "edit": "deny",
    "bash": { "git *": "allow", "*": "ask" }
  },

  "formatter": false,
  "lsp": false,

  "experimental": {
    "primary_tools": ["edit"],
    "mcp_timeout": 30000
  },

  "tool_output": { "max_lines": 200, "max_bytes": 8192 },

  "compaction": { "auto": true, "tail_turns": 15 }
}
````

Shape notes worth being explicit about:

- `model` always carries a provider prefix: `"anthropic/claude-sonnet-4-6"`.
- `skills` is an object with `paths` and/or `urls`, not an array.
- `references` is an object keyed by alias. Each value is a local path, Git repository, or string shorthand.
- `agent` is an object keyed by agent name, not an array.
- `command` is an object keyed by command name, not an array.
- `plugin` is an array of strings or `[name, options]` tuples, not an object.
- `mcp[name].command` is an array of strings, never a single string. `type` is required.
- `permission` is either a string action or an object keyed by tool name.

## Skills

opencode's skill loader scans for `**/SKILL.md` inside skill directories. The
file is named `SKILL.md` exactly, and lives in its own folder named after the
skill:

```
.opencode/skills/my-skill/SKILL.md
```

Frontmatter:

```markdown
---
name: my-skill
description: One sentence covering what this skill does AND when to trigger it. Front-load the literal keywords or filenames the user is likely to say.
---

# My Skill

(skill body in markdown: instructions, examples, references)
```

- `name` is required, lowercase hyphen-separated, up to 64 chars, and matches the folder name.
- `description` is effectively required: skills without one are filtered out and never surfaced to the model. Cover both _what_ the skill does and _when_ to use it. Write in third person ("Use when...", not "I help with..."). Front-load concrete trigger keywords and filenames; gate with "Use ONLY when..." if the skill should stay quiet on adjacent topics.
- Optional: `license`, `compatibility`, `metadata` (string-string map).

Register skills from non-default locations via `skills.paths` (scanned
recursively for `**/SKILL.md`) and `skills.urls` (each URL serves a list of
skills).

## References

References make local directories and Git repositories outside the active
project available as supporting context. Configure them under `references`,
keyed by the alias used in `@` autocomplete:

```json
{
  "references": {
    "docs": {
      "path": "../product-docs",
      "description": "Use for product behavior and terminology"
    },
    "effect": {
      "repository": "Effect-TS/effect",
      "branch": "main",
      "description": "Use for Effect implementation details"
    }
  }
}
```

Local `path` values may be relative to the declaring config, absolute, or use
`~/`. Git `repository` values accept Git URLs, host/path references, and GitHub
`owner/repo` shorthand; `branch` is optional. Both forms support optional
`description` and `hidden` fields.

- Only references with a `description` are advertised to agents in system context.
- `hidden: true` removes a reference from TUI `@` autocomplete only. It remains available to agents and by direct path.
- Reference directories are automatically allowed through the external-directory boundary; normal read/edit/tool permissions still apply.
- String shorthand is supported: use `"docs": "../docs"` for local paths or `"effect": "Effect-TS/effect"` for Git repositories.

## Agents

Two ways to define an agent. Use the file form for anything non-trivial.

### Inline (in `opencode.json`)

```json
{
  "agent": {
    "my-reviewer": {
      "description": "Reviews PRs for style violations.",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-6",
      "permission": { "edit": "deny", "bash": "ask" },
      "prompt": "You are a strict PR reviewer..."
    }
  }
}
```

### File

```
.opencode/agent/my-reviewer.md      OR     .opencode/agents/my-reviewer.md
```

```markdown
---
description: Reviews PRs for style violations.
mode: subagent
model: anthropic/claude-sonnet-4-6
permission:
  edit: deny
  bash: ask
---

You are a strict PR reviewer. Focus on...
```

The file body becomes the agent's `prompt`. Do not also put `prompt:` in the
frontmatter.

`mode` is one of `"primary"`, `"subagent"`, `"all"`.

Allowed top-level frontmatter fields: `name, model, variant, description, mode, hidden, color, steps, options, permission, disable, temperature, top_p`. Any
unknown field is silently routed into `options`.

To disable a built-in agent: `agent: { build: { disable: true } }`, or in a
file, `disable: true` in frontmatter.

`default_agent` must point to a non-hidden, primary-mode agent.

### Built-in agents

opencode ships with `build`, `plan`, `general`, `explore`. Hidden internal agents:
`compaction`, `title`, `summary`. To override a built-in's fields, define the
same key in `agent: { <name>: { ... } }`.

## Commands

opencode's command loader scans for `**/*.md` inside command directories. The
file is named after the command, and lives directly inside the `command` folder:

```
.opencode/command/deploy.md
```

Frontmatter:

```markdown
---
description: One sentence describing what the command does.
agent: build
model: anthropic/claude-sonnet-4-6
---

(command body in markdown: the prompt opencode runs, with $ARGUMENTS for the user's input)
```

- `template` is the command body — everything below the frontmatter — and is required: it is the prompt opencode runs when the command is invoked. Do not also put a `template:` key in the frontmatter.
- `$ARGUMENTS` is replaced with everything the user typed after the command; `$1`, `$2`, … pull individual positional arguments.
- Optional: `description`, `agent`, `model`, `variant`, `subtask`.

## Plugins

`plugin:` is an array. Each entry is one of:

```json
"plugin": [
  "opencode-gemini-auth",            // npm spec, latest
  "opencode-foo@1.2.3",              // npm spec, pinned
  "./local-plugin.ts",               // file path, relative to the declaring config
  "file:///abs/path/plugin.js",      // file URL
  ["opencode-bar", { "key": "val" }] // tuple form with options
]
```

Auto-discovered plugins (no config entry needed): any `*.ts` or `*.js` file in
`.opencode/plugin/` or `.opencode/plugins/`.

A plugin module exports `default` (or any named export) of type
`Plugin = (input: PluginInput, options?) => Promise<Hooks>`. The export is a
function, not a plain object literal, and the function returns an object
(return `{}` if there is nothing to register).

```ts
import type { Plugin } from "@opencode-ai/plugin"

export default (async ({ client, project, directory, $ }) => {
  return {
    config: (cfg) => {
      // cfg is the live merged config; mutate fields here.
    },
    "tool.execute.before": async (input, output) => {
      // mutate output.args before the tool runs
    },
  }
}) satisfies Plugin
```

Hook surface (mutate `output` in place; return `void`):

- `event(input)`: every bus event
- `config(cfg)`: once on init with the merged config
- `chat.message`, `chat.params`, `chat.headers`
- `tool.execute.before`, `tool.execute.after`
- `tool.definition`
- `command.execute.before`
- `shell.env`
- `permission.ask`
- `experimental.chat.messages.transform`, `experimental.chat.system.transform`,
  `experimental.session.compacting`, `experimental.compaction.autocontinue`,
  `experimental.text.complete`

Special object-shaped (not callbacks): `tool: { my_tool: { ... } }`,
`auth: { ... }`, `provider: { ... }`.

## MCP servers

`mcp:` is an object keyed by server name. Each server is discriminated by
`type`:

```json
{
  "mcp": {
    "playwright": {
      "type": "local",
      "command": ["npx", "-y", "@playwright/mcp"],
      "enabled": true,
      "environment": { "BROWSER": "chromium" }
    },
    "github": {
      "type": "remote",
      "url": "https://...",
      "enabled": true,
      "headers": { "Authorization": "Bearer {env:GITHUB_TOKEN}" }
    },
    "old-server": { "enabled": false }
  }
}
```

`command` is an array of strings. `environment` sets environment variables for
a local MCP server. `type` is required. Use `enabled: false` to
disable a server inherited from a parent config. String values such as header
tokens support `{env:VAR}` interpolation (and `{file:path}`); the shell-style
`${VAR}` is not substituted.

## Permissions

```json
"permission": {
  "edit": "deny",
  "bash": { "git *": "allow", "rm *": "deny", "*": "ask" },
  "external_directory": { "~/secrets/**": "deny", "*": "allow" }
}
```

Actions: `"allow"`, `"ask"`, `"deny"`.

Per-tool value forms: `"allow"` shorthand (treated as `{"*": "allow"}`), or an
object `{ pattern: action }`. Within an object, **insertion order matters**.
opencode evaluates the LAST matching rule, so put broad rules first and narrow
rules last.

`permission: "allow"` (a string at the top level) is shorthand for "allow
everything" and is rarely what the user wants.

Known permission keys: `read, edit, glob, grep, list, bash, task, external_directory, todowrite, question, webfetch, websearch, lsp, doom_loop, skill`. Some of these (`todowrite, question, webfetch, websearch, doom_loop`) only accept a flat
action, not a per-pattern object.

`external_directory` patterns are filesystem paths (use `~/`, absolute paths,
or globs like `~/projects/**`).

Per-agent `permission:` overrides top-level `permission:`. Plan Mode lives on
the `plan` agent's permission ruleset (`edit: deny *`).

## Escape hatches

When a user's config is broken and opencode won't start, these env vars help:

- `OPENCODE_DISABLE_PROJECT_CONFIG=1`: skip the project's local `opencode.json`
  and start from globals only. Run from the project directory, opencode loads,
  the user edits the broken file, then they restart without the flag.
- `OPENCODE_CONFIG=/path/to/file.json`: load an additional explicit config.
- `OPENCODE_CONFIG_CONTENT='{"$schema":"https://opencode.ai/config.json"}'`:
  inject inline JSON as a final local-scope merge.
- `OPENCODE_DISABLE_DEFAULT_PLUGINS=1`: skip default plugins.
- `OPENCODE_PURE=1`: skip external plugins entirely.
- `OPENCODE_DISABLE_EXTERNAL_SKILLS=1`,
  `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1`: skip the external skill scans under
  `~/.claude/` and `~/.agents/`.

## When proposing edits

- Validate against the schema before writing. If you are unsure of a field's
  exact shape, or the field is not covered in this skill, fetch
  `https://opencode.ai/config.json` and read the schema rather than guessing.
- Preserve `$schema` and any existing fields the user did not ask to change.
- For agent, command, skill, and plugin definitions, prefer creating new files
  in the correct location over inlining everything in `opencode.json`.
- If the user's existing config is malformed, point them at the env-var escape
  hatches above so they can edit from inside opencode without breaking their
  session.
- After saving any config change, remind the user to quit and restart opencode
  — running sessions keep using the already-loaded config.

Base directory for this skill: .
Relative paths in this skill (e.g., scripts/, reference/) are relative to this base directory.
Note: file list is sampled.

\<skill_files>
<file>/home/user/src/biz.dfch.SpecMgr/whitelist.py</file>
<file>/home/user/src/biz.dfch.SpecMgr/CONTRIBUTING.md</file>
<file>/home/user/src/biz.dfch.SpecMgr/.python-version</file>
<file>/home/user/src/biz.dfch.SpecMgr/README.md</file>
<file>/home/user/src/biz.dfch.SpecMgr/.vscode/settings.json</file>
<file>/home/user/src/biz.dfch.SpecMgr/tests/__init__.py</file>
<file>/home/user/src/biz.dfch.SpecMgr/tests/models/__init__.py</file>
<file>/home/user/src/biz.dfch.SpecMgr/tests/models/test_iso25010.py</file>
<file>/home/user/src/biz.dfch.SpecMgr/tests/models/test_version_info.py</file>
<file>/home/user/src/biz.dfch.SpecMgr/tests/models/md/__init__.py</file>
\</skill_files>
\</skill_content>

````

**Tool: bash**

**Input:**
```json
{
  "command": "ls -la .opencode 2>/dev/null || echo \"no .opencode dir\"; ls .opencode/command 2>/dev/null; ls opencode.json opencode.jsonc 2>/dev/null || echo \"no opencode config in repo\"; ls ~/.config/opencode 2>/dev/null | head"
}
````

**Output:**

```
total 44
drwxrwxr-x  5 user user  4096 Aug 25 20:34 .
drwxrwxr-x 15 user user  4096 Aug 31 13:39 ..
drwxrwxr-x  2 user user  4096 Aug 25 20:34 agent
drwxrwxr-x  2 user user  4096 Aug 25 20:34 command
-rw-rw-r--  1 user user    63 Aug 25 20:34 .gitignore
drwxrwxr-x 29 user user  4096 Aug 25 20:34 node_modules
-rw-rw-r--  1 user user    65 Aug 25 20:34 package.json
-rw-rw-r--  1 user user 14632 Aug 25 20:34 package-lock.json
implement-feature.md
no opencode config in repo
agents
node_modules
opencode.jsonc
package.json
package-lock.json

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 36.5s)

_Thinking:_

The repo already has `.opencode/command/implement-feature.md`, plus `.opencode/agent/`, `.opencode/.gitignore`, and `package.json` (probably for opencode plugins). To follow the existing conventions, let me take a look at the existing command files and .gitignore (is node_modules being ignored? What about package.json?).

The repo already has an `.opencode/command/` with one command — checking its format and the directory's git conventions:

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.opencode/command/implement-feature.md"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/.opencode/command/implement-feature.md</path>
<type>file</type>
<content>
1: ---
2: description: Drive a .specmgr feature plan to completion, one phase per subagent.
3: agent: phase-orchestrator
4: ---
5: 
6: Implement the feature planned in `.specmgr/feat/$ARGUMENTS/README.md`.
7: 
8: Act strictly as an orchestrator: read the plan in full, build a phase-by-phase
9: `todowrite` list, and drive it to completion by delegating **each phase** to a
10: fresh `phase-implementer` subagent (one subagent per phase, in dependency
11: order). After each subagent returns, independently re-run that phase's quality
12: gate, inspect `git diff`, confirm the phase's acceptance criteria, then — with
13: my confirmation — commit that phase as one Conventional Commit before moving
14: on. Do not write or edit any file yourself; delegate all implementation.
15: 
16: Before delegating a phase whose design depends on an unresolved decision, ask
17: me first.

(End of file - total 17 lines)
</content>
```

**Tool: bash**

**Input:**

```json
{
  "command": "cat .opencode/.gitignore .opencode/package.json; ls .opencode/agent/; git check-ignore .opencode/node_modules && echo \"node_modules ignored\""
}
```

**Output:**

```
node_modules
package.json
package-lock.json
bun.lock
.gitignore{
  "dependencies": {
    "@opencode-ai/plugin": "1.18.23"
  }
}
phase-implementer.md
phase-orchestrator.md
.opencode/node_modules
node_modules ignored

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 159.5s)

_Thinking:_

The repo has the following:

- `.opencode/command/implement-feature.md` — frontmatter `description` + `agent`, body contains `$ARGUMENTS`
- `.opencode/agent/phase-orchestrator.md`, `phase-implementer.md`
- `.opencode/node_modules` is gitignored (plugins)

So the OpenCode command for release is: `.opencode/command/release.md`, invoked as `/release [X.Y.Z | patch | minor | major | --dry-run]`.

Key design question: what should the command's template do? Two options:

**Option A — thin wrapper**: the command body just instructs the agent to run `bash scripts/release.sh "$ARGUMENTS"` via the bash tool and report back. The script does everything; the agent is a pass-through. Simple, deterministic.

**Option B — agent-driven**: the command body describes the release procedure in natural language, and the agent executes it step-by-step (using its own tools). This duplicates the script's logic in prose, is non-deterministic, and is exactly what we wanted to avoid by writing the script.

Option A is clearly right: the script is the single source of truth, and the command is a convenient one-keystroke invocation with a bit of wrapper behavior.

But there are nuances for Option A worth planning:

1. **Argument passing**: the user types `/release 0.15.0` or `/release minor` or just `/release`. `$ARGUMENTS` captures the raw trailing text. Template: "Run `bash scripts/release.sh $ARGUMENTS`" — but if ARGUMENTS is empty, we'd run it with no args → the script enters interactive prompt mode (read -p). Problem: the script's interactive prompt runs inside opencode's bash tool — non-TTY → the `read` would fail immediately (EOF on stdin)! In non-TTY, interactive prompts don't work: `read -r -p` on closed stdin returns EOF immediately.

   So the design must handle: when launched via the OpenCode command, the version argument is effectively required (the agent can ask the user via the `question` tool first if no arg given, then re-invoke the script with the resolved version). Or the script detects non-TTY and dies with a usage message (per plan) — then the command template instructs: "If no version was provided, ask the user (question tool) for a full version or bump keyword before running the script."

   Better: the command template itself handles the ask: "If `$ARGUMENTS` is empty, ask me for the target version (full X.Y.Z or patch/minor/major) using the question tool. Then run `bash scripts/release.sh <resolved>`." That keeps the script strictly non-interactive (no `read` at all?) — hmm, but the user explicitly said in the original spec "ask if not provided" (step 1). The interactive-ask requirement can be satisfied at the command layer (agent asks via question tool), while the script stays headless-safe:

   - Script: version arg required; no arg → usage error exit 2 (works in any context including direct terminal use? In a direct terminal the user might want the prompt…).

   Trade-off: script usable standalone in terminal (with interactive prompt) vs. purely headless (arg required). Can do both: the script prompts only if stdin is a TTY, else dies with usage. And the command template: if $ARGUMENTS empty → agent asks user via question tool, passes resolved version to script. This satisfies everything.

2. **Long-running execution**: the full release takes many minutes (CI polls: dev CI ~5–10 min, PR CI similar, publish ~5–10 min). The opencode bash tool has a timeout (default 120s, configurable up to…). The template should instruct the agent to run the script with a generous timeout (e.g. `timeout` parameter ~45–60 min = 3,600,000ms). Or the script prints progress and the agent just waits. The bash tool accepts a `timeout` in ms — 3600000 (1h) is fine.

   Alternatively, run in background and tail. Keep it simple: single bash invocation with a large timeout; the script prints progress lines as it goes (which show up in the tool output). Actually — will intermediate stdout show up in real time? The bash tool captures output at end (possibly truncated to file). The user won't see live progress, but will get the full log on completion. Acceptable; the script's final summary matters most.

3. **Permission/confirmation**: the command does commits/pushes/merges — the agent's bash permission might prompt per-command depending on user config; not our concern in the plan, but the template can note "run the script; do not attempt any of the release steps manually."

4. **Failure handling**: if the script exits non-zero mid-way, the agent should report the failure point + the run/PR URLs the script printed, and not retry blindly (releases are not idempotent in the middle of the flow — though with the pre-checks, re-running after a fix is largely safe: e.g. if dev CI fails, fix and re-run → the script's pre-check "latest dev CI green" would fail… hmm, re-run after a failed CI: the latest dev run is a failure → pre-check 3 dies. Need a nuance: after a code fix is pushed, the latest run is new and green → re-run OK. If the failure was the release commit itself (e.g. changelog transform bug) — the version bump is already committed and pushed; re-run with same version would re-bump? The script bumps from current pyproject version (already new) to the new version again? No — if the user passes an explicit X.Y.Z that equals the current version, we should detect "already at this version" → either continue from where it left off or die with a clear message. Simplest robust behavior: if the resolved target == current pyproject version, die with "already at vX.Y.Z — release in progress? Re-run with the next version or finish manually" — avoids double-bump. Or: if the version line in pyproject already matches the target and the CHANGELOG already has a dated section for it → "release commit already made; continuing from CI wait" is complex state-machine territory. Keep it simple: die with a clear message. That's the right call for v1 of the automation.)

   So in the template: "If the script fails, stop and report the error output verbatim (including any run/PR URLs). Do not re-run or fix things yourself unless I say so."

5. **Command name**: `/release`. File: `.opencode/command/release.md`.

6. **Description**: "Kick off the release automation: version bump, CHANGELOG, dev→main PR, tag, and publish wait (scripts/release.sh)."

7. Should the command also pass `--dry-run`? `/release --dry-run 0.15.0` → $ARGUMENTS = "--dry-run 0.15.0" → passes straight through to the script. Works with a thin wrapper.

Template sketch:

```markdown
---
description: Run the release automation (scripts/release.sh) — version bump, CHANGELOG, dev→main PR, tag, publish wait.
---

Kick off a release by running `bash scripts/release.sh $ARGUMENTS` from the repo root.

- If I gave no version (no arguments, or nothing after `--dry-run`), ask me first
  using the question tool: full version (e.g. 0.15.0) or a bump keyword
  (patch/minor/major). Do not guess.
- Pass my answer through verbatim as the script argument.
- Give the bash call a long timeout (the release waits on several CI runs:
  use ~60 minutes / 3600000 ms).
- Run it exactly once. If it exits non-zero, stop and show me the tail of its
  output verbatim (including any run/PR/release URLs). Do not retry, do not
  re-run pre-checks manually, and do not perform any release step yourself —
  the script is the single source of truth.
- On success, show me the script's final summary (versions, PR, tag, release
  URLs) in a few lines.
```

Wait — one issue: `agent:` frontmatter — implement-feature.md sets `agent: phase-orchestrator`. For release we'd use the default (build) agent — omit the key. Fine.

Also, should the command be `subtask: false`? Not necessary.

One more consideration: the script's own interactive TTY prompt — if the agent passes a version, no prompt needed. If the user runs the script directly in a terminal without an arg, the TTY prompt works (stdin is a TTY). Non-TTY + no arg → usage exit 2. Consistent.

OK, updating the plan: add Phase E — OpenCode command `.opencode/command/release.md` (thin wrapper, asks via question tool if no version given, long timeout, no auto-retry, verbatim failure report). And the verification step: we can't easily test the command inside a plan-mode session, but post-implementation the user can restart opencode (per skill: config changes require restart) and type `/release --dry-run 0.15.0`. Should note the restart requirement in the plan.

Also, the README's "Make a Release" should mention the `/release` command as the primary entry point.

OK, let me present the final consolidated plan (updated with the command addition) and ask for execution approval. Keep it concise — the user already saw the full script plan; what's new is the command part. I should re-present the full plan briefly (since it's the final approval request) but not repeat everything in full; the previous message had it. I'll show a delta + a compact restatement. Actually, for approval clarity, a compact full plan with the new Phase E is best. Keep each item to one line.

The repo already has `.opencode/command/` (with `implement-feature.md` as the format reference) and gitignored `node_modules` for plugins — so a project command `.opencode/command/release.md` fits existing conventions. Here's the final plan with the command added:

## Final plan

**Phase A — `scripts/release.sh [X.Y.Z | patch | minor | major] [--dry-run]`** (bash, `set -euo pipefail`; version arg **required** — no arg + TTY → prompt suggesting next minor; no arg + non-TTY → usage exit 2)

01. Fail-fast pre-checks: on `dev`/clean/in-sync → **`origin/main` is ancestor of `origin/dev`** (your step 7, up front) → latest dev CI green (poll if in flight) → tag absent locally+remotely → `uv lock --check` → `uv`/`gh` available+authed
02. Bump `pyproject.toml` (assert one match); if target == current version → die "already at vX.Y.Z" (prevents double-bump on re-run)
03. `uv lock`; assert diff is only the version line
04. CHANGELOG: `## [X.Y.Z] - YYYY-MM-DD` under emptied `## [Unreleased]`; empty section → TTY confirm / non-TTY die
05. `--dry-run` exits here with the 3-file diff
06. Commit `chore(release): bump version to vX.Y.Z` + push dev
07. Poll dev CI — 30s, ~40min timeout, die with run URL
08. `gh pr create --base main --head dev` (body = changelog section) → poll PR checks 30s → **`gh pr merge --ff-only`** (keeps main a strict ancestor of dev)
09. `checkout main && pull --ff-only` → lightweight tag `vX.Y.Z` on main HEAD → push → back to dev
10. Poll `publish.yml` tag run — all 4 jobs (TestPyPI/PyPI/GH Release/MCP Registry) — 30s, ~45min
11. Verify release + ≥2 assets → `gh release edit --notes "<changelog section>"`
12. Print summary (PyPI/TestPyPI/GH Release/MCP Registry URLs)

**Phase B — OpenCode command `.opencode/command/release.md`** (invoked as `/release [args]`; thin wrapper — the script stays the single source of truth):

- Template passes `$ARGUMENTS` verbatim to `bash scripts/release.sh` (so `/release 0.15.0`, `/release minor`, `/release --dry-run 0.15.0` all work)
- If no version given → agent asks you first via the `question` tool (full version or patch/minor/major), never guesses
- Bash call gets a ~60-min timeout (release waits on 3+ CI runs)
- Runs exactly once; on non-zero exit → stops and shows output tail verbatim (with run/PR URLs), no retry, no manual release steps
- On success → shows the script's summary in a few lines
- Matches existing `implement-feature.md` frontmatter style; no `agent:` override (default build agent)

**Phase C — docs:**

- README "Make a Release": `/release` command as primary entry, `scripts/release.sh` usage, manual procedure kept as fallback subsection
- AGENTS.md "Developer Commands": one line each for the script and the command

**Verification (no real release):** `bash -n` the script; non-TTY no-arg → clean usage error; `--dry-run 0.15.0` → pre-checks pass, diff limited to 3 files, nothing committed/pushed; then **restart opencode** (commands load at startup) and smoke-test `/release --dry-run 0.15.0`.

Shall I execute?

______________________________________________________________________

## User

should we create a command or a skill for this? or a combination thereof?

I think there are parts that we can truly automate (and make them deterministic). But for example to create the CHANGELOG this should be done via an agent. Cannot we run sth like this: "/release minor" -- > and then the agent determines that this is a minor update and inserts and increments the correct minor version number? the script would be run in "stages" and the agent would interact with it.

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 291.4s)

_Thinking:_

The user is asking a design question: command or skill, or a combination of both? And they're proposing a hybrid architecture:

- Truly deterministic parts → script stages
- Parts requiring judgment (e.g., CHANGELOG creation/curation) → agent
- Flow: `/release minor` → agent resolves "minor" to an actual version number (0.15.0) → runs the script in stages, interacting between stages

So they want a **staged** script with agent-driven stages. Let me think about the right architecture.

First, command vs skill:

- **Command** (`.opencode/command/release.md`): a user-initiated, named, one-keystroke entry point with `$ARGUMENTS`. Ideal for "kick off a known workflow with an argument." The user explicitly wants to type `/release minor`.
- **Skill** (`SKILL.md` under `.opencode/skills/release/`): model-initiated, description-triggered guidance injected when the task matches. Skills are for "when to do X and how," not for user-facing invocations.

For a user-initiated workflow, **command is the right primary surface**. Skill is optional add-on: if the user later says "cut a release" in natural language, a skill can steer the agent toward `/release`/the staged script. But that's a nice-to-have, not required. I should recommend: command (primary) + staged script (deterministic core) + agent as orchestrator between stages. Skill is optional — probably skip it to avoid two sources of truth; if added, it must be thin ("use the release command / staged script").

Now, the staged design. Let me partition the whole flow by "deterministic" vs "requires judgment":

**Deterministic (script stages):**

1. `precheck` — all fail-fast checks (branch, clean tree, main ancestor, CI green, tag absent, uv lock --check, tooling). Fully deterministic.
2. `bump` — version resolution (arg: full semver or keyword — keyword→number resolution is deterministic arithmetic), pyproject edit, uv lock, assertion that lock diff is version-only. Deterministic.
3. `changelog` — hmm. The mechanical part (inserting a dated header, emptying [Unreleased]) is deterministic. But the user says CHANGELOG "creation" should be done by the agent. What requires judgment in a changelog?
   - Curation: [Unreleased] section entries should be accurate and well-worded. The agent can review/rewrite entries, verify they reflect the actual commits since the last tag, and add missing items.
   - Categorization: Keep a Changelog categories (Added/Changed/Fixed/...). The agent can reorganize raw notes into proper categories.
   - So: the agent *drafts/reviews* the [Unreleased] content **before** the release (i.e., as part of stage 3's "agent work"), and the script only does the mechanical transformation (inserting the dated header).
   - Actually — an important nuance: the right time for the agent to write changelog content is *when entries are added* (during feature development), not at release time. But the user wants the agent to do it at release time — fine, the agent can also audit [Unreleased] against `git log v0.14.0..HEAD` and fix gaps. That's a genuinely agent-like task (judgment, prose).
4. `commit-push-dev` — stage the 3 files, conventional commit, push, wait for dev CI. Deterministic.
5. `pr-merge` — create PR (PR body = changelog section — can be passed as an arg/file), wait for checks, ff-only merge. Deterministic (except PR title/body wording — the script can use a fixed template).
6. `tag-push` — checkout main, pull, tag, push, back to dev. Deterministic.
7. `publish-wait` — wait for the publish run (4 jobs). Deterministic.
8. `release-notes` — set GH release notes to the changelog section. Deterministic (extraction is mechanical).

**Requires agent judgment (stages where the script pauses or the agent acts directly):**

- A. Version selection confirmation: `/release minor` → script (or agent?) computes 0.15.0. The user says "the agent decides this is a minor update and inserts/increments the correct minor version number." Keyword→number resolution is deterministic (bump minor of 0.14.0 → 0.15.0), but the *decision* of minor vs patch vs major is the user's (they typed it). So the script can resolve it, and the agent can just confirm with the user before proceeding ("I'm about to release 0.15.0 — confirm?"). This is a nice agent touch: pre-bump confirmation.
- B. CHANGELOG curation: agent reviews [Unreleased] against the commit log, rewrites/extends entries, ensures Keep-a-Changelog categories. Agent edits CHANGELOG.md directly (it's a text file; the agent has edit tools). Then the script's `changelog` stage does the mechanical transformation and verifies the result.
  - Alternative: the script exposes a `changelog draft` stage that outputs the raw `git log` + current [Unreleased] section to a scratch file, the agent writes the curated content, and the `changelog apply` stage transforms it. Simpler: the agent just edits the [Unreleased] section in place (that's its natural home), and the script only moves it to a dated section. I prefer this — less script surface area.
- C. Failure triage: if any stage's CI run fails, the agent inspects logs (`gh run view --log-failed`), reports a diagnosis, and optionally proposes a fix — but does not auto-retry the release. The script just reports; judgment is the agent's.
- D. PR review gate (optional): agent can ask the user whether to wait for human review before merging (main is unprotected, but a release PR might be worth a look). The user's flow has no human review step; I'll make it an optional flag/confirmation the agent asks about.

**Staged script interface:**
`scripts/release.sh <stage> [args]`
Stages: `precheck`, `bump <version|keyword>` (does pyproject+uv lock, no changelog), `changelog <version>` (mechanical transformation + assertion), `commit-push <version>`, `pr-merge <version>`, `tag-push <version>`, `publish-wait <version>`, `release-notes <version>`, plus `all` (the fully automated one-shot from my earlier plan, for terminal use without an agent) and `status <version>` (where are we? — idempotent stage detection, very useful for re-runs after failures!).

Idempotency/state: each stage should detect whether it has already been completed (e.g., `changelog` stage: if a dated section for the version already exists and [Unreleased] is empty → "already done"; `tag-push`: if tag exists → done; `pr-merge`: find existing PR dev→main). This makes re-runs after failures safe and enables the agent to resume. This is a key improvement over the monolithic script — and it's what makes "stages" truly useful. A `status` subcommand that reports which stages are done/pending gives the agent a cheap situational awareness tool.

Also each stage prints machine-readable-ish output (or a final line like `STAGE=changelog STATUS=ok VERSION=0.15.0`) so the agent can parse it. Keep it simple: clear human-readable + consistent "done/skipped-already/failed" semantics with a non-zero exit code on failure.

**Command template** (`.opencode/command/release.md`): describes the orchestration protocol:

1. Parse `$ARGUMENTS` (version/keyword, optional --dry-run). If none → question tool.
2. Resolve the version (run `scripts/release.sh bump --resolve <arg>`? — better: a tiny stage `resolve <arg>` that prints the computed full version without changing anything. Agent confirms with user.)
3. Run `precheck`.
4. Agent's CHANGELOG work: read the [Unreleased] section + `git log <last-tag>..HEAD --oneline`, curate (edit file directly), show user the proposed changelog section before locking (question tool / show and confirm).
5. Run stages in order: `bump`, `changelog`, `commit-push`, `pr-merge` (agent may ask about waiting for review), `tag-push`, `publish-wait` (long), `release-notes`.
6. Between stages: report progress; on failure: fetch the failure log, diagnose, report to user, stop (no auto-retry).
7. Final summary.

The command's template is prose instructions for the agent (like implement-feature.md). It must explicitly say: do not perform any git/release operation directly — always via the script's stages; the only file the agent edits directly is the [Unreleased] section of CHANGELOG.md (during the curation step).

**Skill or not?** My recommendation: **no skill** (or optionally a very thin one later). Reasons:

- The workflow is user-initiated → command is the right surface; a skill triggers on natural language and duplicates the protocol.
- Two documents describing the same protocol = drift risk.
- If the user later finds themselves typing "release" in plain chat, add a 3-line skill at that point: "Use the /release command (scripts/release.sh staged)." Not part of v1.

Actually wait — a consideration: the command body is a prompt template with $ARGUMENTS. The command file itself can carry the entire orchestration protocol (like implement-feature.md carries its orchestrator protocol). That's self-contained. Good.

Also: should the CHANGELOG curation be a *separate, reusable* part? For example, the agent might want to curate the changelog without releasing. A skill could serve "how to write changelog entries in this repo." Hmm — Keep-a-Changelog is already in the CHANGELOG header; the feature's README has the convention. I'll leave it out of v1.

**Answer to "command or skill or both":** command + staged script (agent as orchestrator). No skill in v1; explain why (avoiding drift, user-initiated vs model-initiated distinction). Optionally propose a thin skill later.

Now — the user also specifically asked: "the agent decides this is a minor update and inserts/increments the correct minor version number?" — yes: the agent (via the script's `resolve` stage) computes 0.14.0 + minor → 0.15.0, confirms with the user, and the `bump` stage does the mechanical insertion/increment. The *decision* stays with the user (they typed "minor"); the *arithmetic* is deterministic.

Edge case: what if the user types a full version 0.15.0? Same flow, no arithmetic.
What about "major" on 0.x? Semver 0.x: major bump 0.14.0 → 1.0.0. Deterministic but surprising — the agent's confirmation step catches it. Nice illustration of why the confirm-with-user step exists.

Let me also reconsider which parts should *not* be scripted: PR body (changelog section — deterministic extraction), release notes (same). CI wait (deterministic polling). Tag (deterministic). Commit message (deterministic template — the user previously accepted dropping ccm in favor of the template).

One more: my earlier plan had the script do version resolution from keyword internally. In the staged design, `resolve` becomes its own no-op stage — cleaner for the agent to get the number before doing any work.

**Dry-run in the staged design:** does `--dry-run` apply to mutating stages (bump/changelog/commit-push/pr-merge/tag-push), or a global flag? Simpler: each mutating stage takes an optional `--dry-run` that prints the intended action and exits 0. Agent smoke-test: `/release --dry-run minor` → resolve → precheck → dry-run the rest.

**Verification plan update:**

- `bash -n`, run each stage's no-op/idempotency paths: `resolve minor` (prints 0.15.0), `precheck` (should pass now), `status 0.15.0` (all pending), `bump --dry-run`, `changelog --dry-run` (shows header insertion without applying), non-TTY misuse.
- Full `all` mode on a throwaway? Can't safely test a real release. Test `all` up to just before commit? No — `all` runs the whole thing. Keep testing to stages + dry-run only; a real release is the user's own first `/release`.
- Restart opencode for the new command; smoke-test `/release --dry-run minor`.

Hmm, wait, one issue: `precheck` in the staged flow — precheck includes "latest dev CI green." After the agent's changelog curation edit (working tree dirty — CHANGELOG.md modified), precheck's "clean tree" fails! Order matters: either precheck runs *before* changelog curation (tree clean at that point), or precheck must tolerate exactly this one pending CHANGELOG edit. Cleanest: the agent runs `precheck` first (clean tree), then does the changelog curation (which dirties the tree with exactly the changelog), then the subsequent stages re-validate what they need (the `commit-push` stage asserts that the dirty files ⊆ {CHANGELOG.md} before bump? no — the `bump` stage asserts that the dirty files ⊆ {CHANGELOG.md}, then adds pyproject+uv.lock, and asserts that the staged set is exactly 3 files). Let me define per-stage state assertions:

- `precheck`: clean tree, branch, main ancestor, CI green, tag absent, lock in sync, tooling. (Run once at the start, on a clean tree.)
- `bump`: working tree clean, or only CHANGELOG.md modified. Applies pyproject+uv lock changes. Asserts dirty set ⊆ {pyproject.toml, uv.lock, CHANGELOG.md}.
- `changelog`: asserts dirty set ⊆ {pyproject.toml, uv.lock, CHANGELOG.md} (i.e., bump has been done, or this stage alone after agent curation). Applies header transformation. Asserts the resulting [Unreleased] is empty + a dated section exists with content.
- `commit-push`: asserts dirty set is exactly {pyproject.toml, uv.lock, CHANGELOG.md} (or already committed → idempotency check: latest dev commit message matches the template → skip to CI wait). Commits + pushes + waits for CI.
- `pr-merge`: looks for an existing open PR dev→main (resume), else creates; waits for checks; ff-only merge; idempotent: PR already merged → done.
- `tag-push`: idempotent (tag exists → done).
- `publish-wait`: idempotent (run for tag completed → done).
- `release-notes`: idempotent (notes already match the section → done).
- `status`: runs all idempotency probes read-only, prints a table: stage | done|pending|in-progress | detail.

This gives the agent a robust resume protocol: after any failure, the agent runs `status`, reports where we are, and re-runs from the failed stage.

That's the design. Now let me structure the answer:

1. Direct answer: command + staged script; agent as orchestrator; no skill in v1 (why).
2. What's deterministic vs what's for the agent (table).
3. The staged interface (list of stages + idempotency/resume + `status`).
4. The `/release minor` walkthrough (concrete sequence — the user asked exactly for this).
5. Answer their minor→0.15.0 question: user decides the bump type, script `resolve` does the arithmetic, agent confirms with user before mutation (major-on-0.x example).
6. CHANGELOG: agent curates [Unreleased] against git log (its only direct file edit), script does the mechanical transformation.
7. Updated plan (phases) + verification.
8. Ask for confirmation / remaining open points: (a) OK to drop the `all` one-shot mode, or keep it for terminal use? (I'll keep it — it's cheap: `all` = run the stages in order, no agent. Actually with agent curation, `all` can't curate the changelog; `all` should either skip curation (mechanical move only) or require the changelog to be pre-curated. Hmm — keep `all` as a "mechanical release of an already-curated [Unreleased]" mode. Fine.)
   (b) Optional human review gate before pr merge (agent asks)?
   (c) Skill: skip for now?

I'm in plan mode and the user asked a design question — I should answer it, present the refined plan, and ask the remaining questions. Use the question tool for (a)/(b)/(c)? The user said "make suggestions for improvement. Ask" earlier — they like being asked. Three short questions at the end via the question tool, with the design explanation before it.

Let me write it up concisely but completely.

Great question — and your instinct is right: this is a **command + staged script**, with the agent as orchestrator. Let me lay out the design, then answer the minor→0.15.0 question specifically.

## Command vs skill

- **Command** = user-initiated entry point (`/release minor`) with `$ARGUMENTS`. That's exactly what you described — command is the right primary surface.
- **Skill** = model-initiated, trigger-based guidance. It would *duplicate* the orchestration protocol in a second file → drift risk. The workflow has no "agent notices it should release on its own" use case.
- **Recommendation: no skill in v1.** The command file carries the full orchestration protocol (same style as the existing `implement-feature.md`). If you later catch yourself typing "do a release" in plain chat, we add a 3-line skill that just points at `/release`.

## Deterministic vs agent judgment

| Part | Who | Why |
|---|---|---|
| All pre-checks, version arithmetic, pyproject/uv.lock edits, commit+push, CI polling, PR create/merge (`--ff-only`), tag, publish polling, release-notes write | **Script stages** | Pure mechanics, no judgment |
| Version *choice* (patch/minor/major) | **You** (typed in `/release minor`) | Release intent |
| Confirming the resolved number before anything mutates | **Agent** (question tool) | Catches surprises, e.g. `major` on 0.x → 1.0.0 |
| **CHANGELOG curation**: reviewing `[Unreleased]` against `git log v0.14.0..HEAD`, fixing gaps, re-wording entries, organizing into Keep-a-Changelog categories | **Agent** (its one direct file edit) | Prose + judgment — exactly what you said |
| Failure triage: reading failed CI logs, diagnosing, proposing fix | **Agent** (never auto-retries) | Judgment |
| The mechanical `[Unreleased]` → dated-section move | **Script** | Text transform |

## Your `/release minor` walkthrough

1. Agent parses `minor` → runs `scripts/release.sh resolve minor` → prints `0.15.0` (deterministic bump of 0.14.0)
2. Agent confirms with you: *"About to release 0.15.0 — proceed?"*
3. Agent runs `precheck` (clean tree, on dev, **main is ancestor of dev**, dev CI green, tag absent, lock in sync)
4. **Agent's changelog pass**: reads `[Unreleased]` + `git log $(last-tag)..HEAD --oneline`, curates the entries in `CHANGELOG.md` directly, shows you the proposed section
5. Agent runs the stages in order: `bump 0.15.0` → `changelog 0.15.0` → `commit-push 0.15.0` (waits dev CI, 30s polls) → `pr-merge 0.15.0` (waits PR checks, ff-only merge) → `tag-push 0.15.0` → `publish-wait 0.15.0` (4 jobs) → `release-notes 0.15.0`
6. Any stage fails → agent runs `status 0.15.0`, fetches the failed log, reports diagnosis, **stops**. You fix, agent resumes from the failed stage — every stage is **idempotent** (tag exists → done; PR already merged → done; notes already match → done), so re-runs are safe.

That idempotency + `status` probe is the key improvement the staging buys over the monolithic script from my earlier plan: resumable releases.

## Staged interface

`scripts/release.sh <stage> [args] [--dry-run]`: `resolve`, `precheck`, `bump`, `changelog`, `commit-push`, `pr-merge`, `tag-push`, `publish-wait`, `release-notes`, `status`, and `all` (stages 5–13 without agent curation, for terminal use when `[Unreleased]` is already written). Each stage asserts the working-tree state it expects (e.g. `commit-push` requires dirty set ⊆ the 3 release files).

Three open points before I finalize the plan:

**Tool: question**

**Input:**

```json
{
  "questions": [
    {
      "header": "Review gate",
      "question": "Between pr-merge's CI wait and the actual merge: should the agent pause and ask you for a human look at the release PR (changelog section, diff) before merging? Main is unprotected, so the script could just merge.",
      "options": [
        {
          "label": "Ask before merge (Recommended)",
          "description": "Agent shows the PR URL + changelog section and waits for your go-ahead. One extra confirmation for the one irreversible-ish step."
        },
        {
          "label": "Merge automatically",
          "description": "CI green → merge. Faster, fully hands-off after the version confirmation."
        }
      ]
    },
    {
      "header": "all mode",
      "question": "Keep the `all` one-shot mode (mechanical release of an already-curated [Unreleased], no agent) in addition to the staged interface?",
      "options": [
        {
          "label": "Keep all mode (Recommended)",
          "description": "Terminal users can still do scripts/release.sh all 0.15.0 without opencode. Cheap to implement — it's just the stages in sequence."
        },
        {
          "label": "Staged only",
          "description": "Smaller script surface; releases always go through /release with the agent."
        }
      ]
    },
    {
      "header": "Skill",
      "question": "Confirm: skip the skill in v1 (command carries the protocol; add a thin pointer-skill later if natural-language triggering proves useful)?",
      "options": [
        {
          "label": "Skip skill (Recommended)",
          "description": "Single source of truth in the command file."
        },
        {
          "label": "Add thin skill now",
          "description": "A 3-line skill that says 'use /release' so plain-chat release requests also route correctly."
        }
      ]
    }
  ]
}
```

**Output:**

```
User has answered your questions: "Between pr-merge's CI wait and the actual merge: should the agent pause and ask you for a human look at the release PR (changelog section, diff) before merging? Main is unprotected, so the script could just merge."="Ask before merge (Recommended)", "Keep the `all` one-shot mode (mechanical release of an already-curated [Unreleased], no agent) in addition to the staged interface?"="Keep all mode (Recommended)", "Confirm: skip the skill in v1 (command carries the protocol; add a thin pointer-skill later if natural-language triggering proves useful)?"="Skip skill (Recommended)". You can now continue with the user's answers in mind.
```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 87.0s)

_Thinking:_

All three answers have been confirmed. Next, finalize the plan. The user has not yet said "execute" — they asked design questions, and I answered and locked down the remaining decisions. I should present a concise final plan (v2) and ask for approval to execute. Since the earlier plan has already been laid out in detail, the final plan should be compact — only the diffs from the previously approved direction (staged design, review gate, no skill) plus a confirmation of the full scope.

One detail about the review gate: the `pr-merge` stage will now be split into two stages: `pr-create` (create the PR, wait for checks, print the URL and stop) and `pr-merge` (merge an already-green PR with --ff-only). This way the agent can pause in between for the user's confirmation. Let me formalize this:

Stages: `resolve`, `precheck`, `bump`, `changelog`, `commit-push`, `pr-create`, `pr-merge`, `tag-push`, `publish-wait`, `release-notes`, `status`, `all`.

- `pr-create <version>`: resume if an open dev→main PR exists; create it if not; wait for checks to pass (30-second polling); print the PR URL + head SHA; exit 0 (do not merge).
- `pr-merge <version>`: look up the open dev→main PR (or one that has already been merged → done); assert that its checks are green; `gh pr merge --ff-only`; idempotent.

`all` = precheck bump changelog commit-push pr-create pr-merge tag-push publish-wait release-notes (no pause, no curation).

Command protocol update: after `pr-create`, the agent shows the user the PR URL + changelog section + a diff summary, and asks for confirmation before `pr-merge`.

Final plan phase structure:

- Phase 1: `scripts/release.sh` (staged, idempotent, --dry-run, status)
- Phase 2: `.opencode/command/release.md` (orchestration protocol)
- Phase 3: README "Make a Release" + one line in AGENTS.md's Developer Commands
- Phase 4: Verification (bash -n, resolve/precheck/status/dry-run paths, non-TTY misuse, restart opencode, /release --dry-run minor smoke test)

Present this compactly and ask, "Ready to execute?"

All locked in. Final plan v2 — compact version, deltas from v1 in bold:

## `scripts/release.sh` — staged, idempotent release script

**Stages:** `resolve` · `precheck` · `bump` · `changelog` · `commit-push` · **`pr-create`** · **`pr-merge`** · `tag-push` · `publish-wait` · `release-notes` · `status` · `all`

- `resolve [X.Y.Z|patch|minor|major]` — prints computed version, mutates nothing
- `precheck` — clean tree, on dev, **main is ancestor of dev**, dev CI green (polls if in flight), tag absent, `uv lock --check`, tooling+auth
- `bump <v>` — pyproject (assert one match; die if already at v) + `uv lock` (assert diff = version line only); tolerates a dirty `CHANGELOG.md` (agent curation)
- `changelog <v>` — mechanical move: `## [v] - YYYY-MM-DD` under emptied `[Unreleased]`; die on empty section (non-TTY) / confirm (TTY)
- `commit-push <v>` — asserts dirty set ⊆ the 3 release files, commits `chore(release): bump version to v`, pushes, waits dev CI (30s polls)
- **`pr-create <v>`** — creates/resumes the dev→main PR (body = changelog section), waits for checks green, prints PR URL + head SHA, **stops without merging**
- **`pr-merge <v>`** — asserts PR checks green, `gh pr merge --ff-only` (keeps main a strict ancestor of dev)
- `tag-push <v>` — main pull --ff-only, lightweight tag on main HEAD, push, back to dev (idempotent if tag exists)
- `publish-wait <v>` — publish.yml run, all 4 jobs, 30s polls
- `release-notes <v>` — verify release + ≥2 assets, `gh release edit --notes "<changelog section>"`
- `status <v>` — read-only probes: per-stage done/pending/in-progress table (the agent's resume tool after any failure)
- `all [v|keyword]` — the whole chain without agent curation or the merge pause (terminal mode)
- Every mutating stage: `--dry-run`; per-stage working-tree assertions; consistent exit codes

## `.opencode/command/release.md` — `/release [X.Y.Z|patch|minor|major] [--dry-run]`

Orchestration protocol (agent = orchestrator, script = hands):

1. No version → `question` tool; keyword → `resolve` → **confirm the number with you** (catches 0.x-major surprises)
2. `precheck`
3. **Agent's only direct file edit**: curate `[Unreleased]` against `git log <last-tag>..HEAD`, show you the proposed section
4. `bump` → `changelog` → `commit-push` → `pr-create` → **pause: show PR URL + changelog, ask your go-ahead** → `pr-merge` → `tag-push` → `publish-wait` (long timeouts on bash calls) → `release-notes`
5. Failure at any point → `status` + failed-log diagnosis + report, **stop — never auto-retry, never perform release steps outside the script**
6. Final summary (PyPI / TestPyPI / GH Release / MCP Registry URLs)

## Docs

- README "Make a Release": `/release` as primary entry → staged usage → `all` mode → old manual procedure as fallback
- AGENTS.md "Developer Commands": lines for the script and the command

## Verification (no real release)

`bash -n` · non-TTY misuse → clean usage errors · `resolve minor` → 0.15.0 · `precheck` (should pass on today's state) · `status 0.15.0` → all pending · `bump`/`changelog`/`pr-create` `--dry-run` → no mutations, correct intended actions · restart opencode · `/release --dry-run minor` end-to-end smoke

No skill (v1). Ready to execute?

______________________________________________________________________

## User

can we put the steps (with or without script and agent support) into a SOP?

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 94.1s)

_Thinking:_

User's question: Can we put the procedure (with or without script/agent support) into an SOP?

Interesting — the specmgr MCP server has a `sop` domain (Standard Operating Procedure), which we merged earlier in PR #34! The user is asking whether we can record this release procedure as an SOP document in specmgr.

Plan mode is enabled — read-only. What I should do:

1. Look at the SOP schema/template to understand what an SOP document looks like (structure, sections, frontmatter).
2. Think about how the release procedure maps onto it.
3. Consider the trade-offs: SOP is documentation (a record of a procedure), whereas script + command is executable automation. An SOP could serve as the "master document" for the procedure, and the script + command could implement/execute it. Or, the SOP could be a fallback for manual execution.

Key design question: where does the SOP document live? The specmgr tool uses the SPECMGR_SOP_DIR environment variable or a default base directory. Let me check what the default is — probably the `.specmgr/sop/` directory? Let me look at the sop tool's \_paths.py to check the default base directory.

Also, I'll read the SOP template (specmgr_get_sop_template) to check the structure: RASCI-style role assignment, approval/activation lifecycle, sections like `## Purpose`, `## Scope`, `## Roles and Responsibilities`, `## Procedure`/steps, etc. Let me fetch the template and an example.

The user's phrasing: "put the procedure (with or without script/agent support) into an SOP" — that is, the SOP should describe the procedure in a way that covers both: when the script/agent is available (automated procedure), and when it's not (manual fallback). This aligns nicely with the SOP domain: it's a "structured, step-by-step operational document" equipped with roles/responsibilities and an approval lifecycle.

So the answer is: yes, and here's how to structure it. The SOP becomes the canonical, approval-gated document for the release procedure, and the script + command reference it (or are generated from it). This is actually a lovely dogfooding moment: the repo just merged the SOP domain (feat-30), and now we're going to create its first real SOP.

Things to investigate:

1. SOP template structure (specmgr_get_sop_template)
2. SOP example (specmgr_get_sop_example)
3. Where SOPs are stored (sop/tools/\_paths.py — the SPECMGR_SOP_DIR default)
4. rasci resource (specmgr://rasci) for role definitions
5. SOP lifecycle statuses (draft → … approved → effective?)

Then, planning:

- Create an SOP document "Perform a release of biz.dfch.SpecMgr" (id auto-assigned, specmgr-generated UUID — unlike feat, SOP uses UUID ids and flat files)
- Content mapping: purpose, scope, roles (RASCI: who does what — in this repo, probably just "the release engineer" = the user/agent pair; RACI in the agent context is interesting: agent = executor, human = approver), procedure steps corresponding to the staged design (each stage as a step, with both an automated path (script stage) and a manual fallback), exceptions/failure handling, validation/criteria for completion
- Status lifecycle: draft → … → effective. The SOP's frontmatter has an approval/activation lifecycle (a closed set). Should I check the SOP model's frontmatter status values? Per AGENTS.md, SOP has a "closed approval/activation lifecycle." I'll check the template/example.
- Relationship to README "Make a Release" and the script: the SOP is the canonical procedure; the README points to it; the script's stages mirror the SOP's steps (numbered correspondingly, e.g., step S1…S10 ↔ stages). Cross-reference from the script's docstring/header to the SOP id.
- Ordering: should we write the SOP first (document the procedure, get it approved), then build the script + command to match it? Or build the script first, then document it? I'd propose the SOP-first ordering: define the steps in the SOP (with both the automated and manual paths), then implement the script's stages to exactly mirror them, and reference the SOP id.

Also to consider: the SOP domain is new (just merged). Creating the first real SOP is a dogfooding opportunity, but also carries schema risk (a v1 schema we haven't used in production yet). I should note this in the plan — but the schema has tests, so it should be fine.

Where do SOPs get stored? Let me check the \_paths default. Probably the SPECMGR_SOP_DIR env var, or the default is `.specmgr/sop/`? Let me look at the code.

Let me run the reads (all read-only, allowed in plan mode):

- specmgr_get_sop_template
- specmgr_get_sop_example
- Read src/biz/dfch/specmgr/sop/tools/\_paths.py
- specmgr_get_sop (check status values) — or read sop/models/v1/frontmatter.py
- specmgr list sop (check existing SOPs — probably zero)
- Read the rasci resource data: src/biz/dfch/specmgr/general/data/general_rasci.md

Let me batch these.

Yes — and it's timely, since the `sop` domain we merged earlier (PR #34) was built exactly for this. Let me examine the SOP schema and conventions before answering how it fits in:

**Tool: invalid**

**Input:**

```json
{
  "tool": "specmgr_get_sop_template",
  "error": "Model tried to call unavailable tool 'specmgr_get_sop_template'. Available tools: asdste100_rules_by_category, asdste100_rules_by_section, asdste100_rules_examples, asdste100_rules_find, asdste100_rules_match, asdste100_rules_overview, asdste100_rules_search, asdste100_rules_toc, asdste100_word_count, asdste100_word_find, asdste100_word_find_many, asdste100_word_fuzzy, asdste100_word_list, asdste100_word_match, asdste100_word_synonym, bash, edit, glob, grep, invalid, list_mcp_resource_templates, list_mcp_resources, question, read, read_mcp_resource, skill, specmgr_create_adr, specmgr_create_dec, specmgr_create_feat, specmgr_create_gol, specmgr_create_prb, specmgr_create_qa, specmgr_create_req, specmgr_create_rsk, specmgr_create_tsk, specmgr_create_uc, specmgr_delete_dec, specmgr_delete_feat, specmgr_delete_gol, specmgr_delete_prb, specmgr_delete_qa, specmgr_delete_req, specmgr_delete_rsk, specmgr_delete_tsk, specmgr_delete_uc, specmgr_get_adr, specmgr_get_dec, specmgr_get_dec_example, specmgr_get_dec_template, specmgr_get_feat, specmgr_get_feat_example, specmgr_get_feat_template, specmgr_get_gol, specmgr_get_gol_example, specmgr_get_gol_template, specmgr_get_prb, specmgr_get_prb_example, specmgr_get_prb_template, specmgr_get_qa, specmgr_get_qa_example, specmgr_get_qa_template, specmgr_get_req, specmgr_get_req_example, specmgr_get_req_template, specmgr_get_rsk, specmgr_get_rsk_example, specmgr_get_rsk_template, specmgr_get_tsk, specmgr_get_tsk_example, specmgr_get_tsk_template, specmgr_get_uc, specmgr_get_uc_example, specmgr_get_uc_template, specmgr_list_adr, specmgr_list_dec, specmgr_list_feat, specmgr_list_gol, specmgr_list_prb, specmgr_list_qa, specmgr_list_req, specmgr_list_rsk, specmgr_list_tsk, specmgr_list_uc, specmgr_mdformat, specmgr_option_create, specmgr_option_delete, specmgr_option_list, specmgr_option_read, specmgr_option_update, specmgr_parse_dec, specmgr_parse_feat, specmgr_parse_gol, specmgr_parse_prb, specmgr_parse_qa, specmgr_parse_req, specmgr_parse_rsk, specmgr_parse_tsk, specmgr_parse_uc, specmgr_set_status, specmgr_update, specmgr_update_frontmatter, specmgr_update_section, specmgr_validate_adr, specmgr_validate_dec, specmgr_validate_feat, specmgr_validate_gol, specmgr_validate_prb, specmgr_validate_qa, specmgr_validate_req, specmgr_validate_rsk, specmgr_validate_tsk, specmgr_validate_uc, specmgr_webfetch, task, todowrite, webfetch, write."
}
```

**Output:**

```
The arguments provided to the tool are invalid: Model tried to call unavailable tool 'specmgr_get_sop_template'. Available tools: asdste100_rules_by_category, asdste100_rules_by_section, asdste100_rules_examples, asdste100_rules_find, asdste100_rules_match, asdste100_rules_overview, asdste100_rules_search, asdste100_rules_toc, asdste100_word_count, asdste100_word_find, asdste100_word_find_many, asdste100_word_fuzzy, asdste100_word_list, asdste100_word_match, asdste100_word_synonym, bash, edit, glob, grep, invalid, list_mcp_resource_templates, list_mcp_resources, question, read, read_mcp_resource, skill, specmgr_create_adr, specmgr_create_dec, specmgr_create_feat, specmgr_create_gol, specmgr_create_prb, specmgr_create_qa, specmgr_create_req, specmgr_create_rsk, specmgr_create_tsk, specmgr_create_uc, specmgr_delete_dec, specmgr_delete_feat, specmgr_delete_gol, specmgr_delete_prb, specmgr_delete_qa, specmgr_delete_req, specmgr_delete_rsk, specmgr_delete_tsk, specmgr_delete_uc, specmgr_get_adr, specmgr_get_dec, specmgr_get_dec_example, specmgr_get_dec_template, specmgr_get_feat, specmgr_get_feat_example, specmgr_get_feat_template, specmgr_get_gol, specmgr_get_gol_example, specmgr_get_gol_template, specmgr_get_prb, specmgr_get_prb_example, specmgr_get_prb_template, specmgr_get_qa, specmgr_get_qa_example, specmgr_get_qa_template, specmgr_get_req, specmgr_get_req_example, specmgr_get_req_template, specmgr_get_rsk, specmgr_get_rsk_example, specmgr_get_rsk_template, specmgr_get_tsk, specmgr_get_tsk_example, specmgr_get_tsk_template, specmgr_get_uc, specmgr_get_uc_example, specmgr_get_uc_template, specmgr_list_adr, specmgr_list_dec, specmgr_list_feat, specmgr_list_gol, specmgr_list_prb, specmgr_list_qa, specmgr_list_req, specmgr_list_rsk, specmgr_list_tsk, specmgr_list_uc, specmgr_mdformat, specmgr_option_create, specmgr_option_delete, specmgr_option_list, specmgr_option_read, specmgr_option_update, specmgr_parse_dec, specmgr_parse_feat, specmgr_parse_gol, specmgr_parse_prb, specmgr_parse_qa, specmgr_parse_req, specmgr_parse_rsk, specmgr_parse_tsk, specmgr_parse_uc, specmgr_set_status, specmgr_update, specmgr_update_frontmatter, specmgr_update_section, specmgr_validate_adr, specmgr_validate_dec, specmgr_validate_feat, specmgr_validate_gol, specmgr_validate_prb, specmgr_validate_qa, specmgr_validate_req, specmgr_validate_rsk, specmgr_validate_tsk, specmgr_validate_uc, specmgr_webfetch, task, todowrite, webfetch, write.
```

**Tool: invalid**

**Input:**

```json
{
  "tool": "specmgr_list_sop",
  "error": "Model tried to call unavailable tool 'specmgr_list_sop'. Available tools: asdste100_rules_by_category, asdste100_rules_by_section, asdste100_rules_examples, asdste100_rules_find, asdste100_rules_match, asdste100_rules_overview, asdste100_rules_search, asdste100_rules_toc, asdste100_word_count, asdste100_word_find, asdste100_word_find_many, asdste100_word_fuzzy, asdste100_word_list, asdste100_word_match, asdste100_word_synonym, bash, edit, glob, grep, invalid, list_mcp_resource_templates, list_mcp_resources, question, read, read_mcp_resource, skill, specmgr_create_adr, specmgr_create_dec, specmgr_create_feat, specmgr_create_gol, specmgr_create_prb, specmgr_create_qa, specmgr_create_req, specmgr_create_rsk, specmgr_create_tsk, specmgr_create_uc, specmgr_delete_dec, specmgr_delete_feat, specmgr_delete_gol, specmgr_delete_prb, specmgr_delete_qa, specmgr_delete_req, specmgr_delete_rsk, specmgr_delete_tsk, specmgr_delete_uc, specmgr_get_adr, specmgr_get_dec, specmgr_get_dec_example, specmgr_get_dec_template, specmgr_get_feat, specmgr_get_feat_example, specmgr_get_feat_template, specmgr_get_gol, specmgr_get_gol_example, specmgr_get_gol_template, specmgr_get_prb, specmgr_get_prb_example, specmgr_get_prb_template, specmgr_get_qa, specmgr_get_qa_example, specmgr_get_qa_template, specmgr_get_req, specmgr_get_req_example, specmgr_get_req_template, specmgr_get_rsk, specmgr_get_rsk_example, specmgr_get_rsk_template, specmgr_get_tsk, specmgr_get_tsk_example, specmgr_get_tsk_template, specmgr_get_uc, specmgr_get_uc_example, specmgr_get_uc_template, specmgr_list_adr, specmgr_list_dec, specmgr_list_feat, specmgr_list_gol, specmgr_list_prb, specmgr_list_qa, specmgr_list_req, specmgr_list_rsk, specmgr_list_tsk, specmgr_list_uc, specmgr_mdformat, specmgr_option_create, specmgr_option_delete, specmgr_option_list, specmgr_option_read, specmgr_option_update, specmgr_parse_dec, specmgr_parse_feat, specmgr_parse_gol, specmgr_parse_prb, specmgr_parse_qa, specmgr_parse_req, specmgr_parse_rsk, specmgr_parse_tsk, specmgr_parse_uc, specmgr_set_status, specmgr_update, specmgr_update_frontmatter, specmgr_update_section, specmgr_validate_adr, specmgr_validate_dec, specmgr_validate_feat, specmgr_validate_gol, specmgr_validate_prb, specmgr_validate_qa, specmgr_validate_req, specmgr_validate_rsk, specmgr_validate_tsk, specmgr_validate_uc, specmgr_webfetch, task, todowrite, webfetch, write."
}
```

**Output:**

```
The arguments provided to the tool are invalid: Model tried to call unavailable tool 'specmgr_list_sop'. Available tools: asdste100_rules_by_category, asdste100_rules_by_section, asdste100_rules_examples, asdste100_rules_find, asdste100_rules_match, asdste100_rules_overview, asdste100_rules_search, asdste100_rules_toc, asdste100_word_count, asdste100_word_find, asdste100_word_find_many, asdste100_word_fuzzy, asdste100_word_list, asdste100_word_match, asdste100_word_synonym, bash, edit, glob, grep, invalid, list_mcp_resource_templates, list_mcp_resources, question, read, read_mcp_resource, skill, specmgr_create_adr, specmgr_create_dec, specmgr_create_feat, specmgr_create_gol, specmgr_create_prb, specmgr_create_qa, specmgr_create_req, specmgr_create_rsk, specmgr_create_tsk, specmgr_create_uc, specmgr_delete_dec, specmgr_delete_feat, specmgr_delete_gol, specmgr_delete_prb, specmgr_delete_qa, specmgr_delete_req, specmgr_delete_rsk, specmgr_delete_tsk, specmgr_delete_uc, specmgr_get_adr, specmgr_get_dec, specmgr_get_dec_example, specmgr_get_dec_template, specmgr_get_feat, specmgr_get_feat_example, specmgr_get_feat_template, specmgr_get_gol, specmgr_get_gol_example, specmgr_get_gol_template, specmgr_get_prb, specmgr_get_prb_example, specmgr_get_prb_template, specmgr_get_qa, specmgr_get_qa_example, specmgr_get_qa_template, specmgr_get_req, specmgr_get_req_example, specmgr_get_req_template, specmgr_get_rsk, specmgr_get_rsk_example, specmgr_get_rsk_template, specmgr_get_tsk, specmgr_get_tsk_example, specmgr_get_tsk_template, specmgr_get_uc, specmgr_get_uc_example, specmgr_get_uc_template, specmgr_list_adr, specmgr_list_dec, specmgr_list_feat, specmgr_list_gol, specmgr_list_prb, specmgr_list_qa, specmgr_list_req, specmgr_list_rsk, specmgr_list_tsk, specmgr_list_uc, specmgr_mdformat, specmgr_option_create, specmgr_option_delete, specmgr_option_list, specmgr_option_read, specmgr_option_update, specmgr_parse_dec, specmgr_parse_feat, specmgr_parse_gol, specmgr_parse_prb, specmgr_parse_qa, specmgr_parse_req, specmgr_parse_rsk, specmgr_parse_tsk, specmgr_parse_uc, specmgr_set_status, specmgr_update, specmgr_update_frontmatter, specmgr_update_section, specmgr_validate_adr, specmgr_validate_dec, specmgr_validate_feat, specmgr_validate_gol, specmgr_validate_prb, specmgr_validate_qa, specmgr_validate_req, specmgr_validate_rsk, specmgr_validate_tsk, specmgr_validate_uc, specmgr_webfetch, task, todowrite, webfetch, write.
```

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"SPECMGR_SOP_DIR\\|default\\|base_dir\" src/biz/dfch/specmgr/sop/tools/_paths.py | head -15; echo ===; grep -n \"status\\|_ALLOWED\" src/biz/dfch/specmgr/sop/models/v1/frontmatter.py | head -20"
}
```

**Output:**

```
26:Mirrors ``dec.tools._paths``'s read-only/write split: :func:`sop_base_dir`
28:effect), only :func:`ensure_sop_base_dir` does, for ``create_sop``. There is
41:    doc_base_dir,
42:    ensure_doc_base_dir,
51:    "sop_base_dir",
52:    "ensure_sop_base_dir",
72:def sop_base_dir() -> Path:
75:    Thin wrapper over ``general.tools._doc_paths.doc_base_dir(SOP_TYPE_NAME)``
76:    -- see that function's own docstring for the env var/default it reads.
83:    result = doc_base_dir(SOP_TYPE_NAME)
87:def ensure_sop_base_dir() -> Path:
91:    the read-only :func:`sop_base_dir` instead.
98:    result = ensure_doc_base_dir(SOP_TYPE_NAME)
103:    """Yield every SOP ``*.md`` file under :func:`sop_base_dir`, sorted by name.
112:    result = iter_doc_paths(sop_base_dir())
===
23:``status`` to SOP's own closed five-value approval/effectivity lifecycle set
28:is a manual ``set_status`` call, not automatic.
39:#: Fixed, closed set of accepted ``status`` values for SOPs -- a five-value
44:_ALLOWED_STATUSES = frozenset(
64:    status:
68:        ``"draft"`` (inherited from the base's ``_default_blank_status_to_draft``
71:        them is a manual ``set_status`` call, not automatic.
82:    @field_validator("status")
84:    def _validate_status(cls, value: str) -> str:
85:        if value not in _ALLOWED_STATUSES:
86:            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 67.4s)

_Thinking:_

Interesting — the MCP tool for `sop` is **not** registered in the current opencode session. The specmgr MCP server's tool list doesn't include `specmgr_create_sop`/`specmgr_get_sop_template` etc. That's because the MCP server running in this session is the *old* one (it was started before the SOP domain was merged — the config is loaded at startup and not hot-reloaded. Also, this repo's specmgr MCP server is probably configured to run from this checkout… no wait, actually the MCP server in my session is a specmgr server instance launched with the pre-SOP-merge code. The sop domain was merged at ec3d644, and my session's MCP server was probably started before that, or was launched from an installed package).

So: I can't use specmgr's MCP sop tool *right now*. But I can read the SOP schema directly from the source (post-merge, in the working tree on dev) and plan the SOP document. The SOP document can be created as a markdown file under the SOP base directory — let me check the default base directory in `general/tools/_doc_paths.py`.

I'll read the following:

1. `general/tools/_doc_paths.py` — the environment variable / default for the base directory
2. `sop/models/v1/frontmatter.py` — the 5 status values
3. `sop/data/sop_template.md` and `sop_example.md` — structure
4. `general/data/general_rasci.md` — RASCI roles
5. `sop/models/v1/body.py` — section requirements (skim the headings)

This is a bit ironic but worth noting: the SOP MCP tool isn't available in this session. To create an SOP, either restart the MCP server (does the user do that? The MCP server is configured in opencode's settings — probably via `uvx` or from the repo), or write the file directly and validate it with `specmgr_validate_sop`… which is also not available. Hmm — I could validate it with a local Python call: `uv run --frozen --all-extras python -c "from biz.dfch.specmgr.sop.models.v1 import parse_sop; ..."`. This is a read-only validation (parsing from a file) — but writing the SOP file itself is a write action (currently forbidden by plan mode. It's a normal action once out of plan mode).

Let me read the template/example to get the structure.

The specmgr MCP tools for the `sop` domain don't exist in this session (the MCP server was started before PR #34 was merged, and opencode doesn't hot-reload) — however, the schema is already in my local dev tree, so I'll read the structure directly from the source:

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/data/sop_template.md"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/data/sop_template.md</path>
<type>file</type>
<content>
1: ---
2: created: 2026-08-30
3: id: deadbeef-dead-dead-dead-deadbeefdead
4: status: draft
5: type: sop
6: updated: 2026-08-30
7: version: 1.0.0
8: ---
9: 
10: # Level 1 Heading is the Title of the Standard Operating Procedure
11: 
12: ## Purpose
13: 
14: Why this SOP exists and the outcome it produces.
15: 
16: ## Scope
17: 
18: What this SOP covers, and optionally what it does not.
19: 
20: ## Definitions
21: 
22: - A term-of-art used by this SOP, defined for the reader.
23: 
24: ## Roles and Responsibilities
25: 
26: ### Accountable
27: 
28: The single owner who is ultimately answerable for this SOP.
29: 
30: ### Responsible
31: 
32: - A party who does the work the SOP describes.
33: 
34: ### Support
35: 
36: - A party who provides resources or assistance to the responsible parties.
37: 
38: ### Consulted
39: 
40: - A party whose opinion is sought before or during the work.
41: 
42: ### Informed
43: 
44: - A party who is kept up to date on progress or outcomes.
45: 
46: ## Safety and Precautions
47: 
48: Warnings and precautions to read before following the procedure.
49: 
50: ## Procedure
51: 
52: ### Step 1: name of the first step
53: 
54: The actions that make up the first step.
55: 
56: ## Related Artifacts
57: 
58: ### Requirements
59: 
60: - A bullet list with related requirements, e.g. REQ-0001: title.
61: 
62: ### Decisions
63: 
64: - A bullet list with related decisions, e.g. DEC-0001: title.
65: 
66: ### Goals
67: 
68: - A bullet list with related goals, e.g. GOL-0001: title.
69: 
70: ### Acceptance Criteria
71: 
72: - A bullet list with related acceptance criteria, e.g. ACC-0001: title.
73: 
74: ### Sops
75: 
76: - A bullet list with related SOPs, e.g. SOP-0001: title.
77: 
78: ## More Information
79: 
80: Optional free-form supplementary text.
81: 
82: ## Updates
83: 
84: ### 2026-08-30 09:00:00.000+02:00 — Created
85: 
86: A lead paragraph describing this update.

(End of file - total 86 lines)
</content>
```

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"_ALLOWED_STATUSES = frozenset\" -A 8 src/biz/dfch/specmgr/sop/models/v1/frontmatter.py; echo ===; grep -n \"SPECMGR_SOP_DIR\\|specmgr/sop\\|\\.specmgr\" src/biz/dfch/specmgr/general/tools/_doc_paths.py | head"
}
```

**Output:**

```
44:_ALLOWED_STATUSES = frozenset(
45-    {
46-        "draft",
47-        "review",
48-        "approved",
49-        "active",
50-        "retired",
51-    }
52-)
===

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 45.8s)

_Thinking:_

SOP template structure:

- Frontmatter: created, id, status, type: sop, updated, version
- H1 title
- ## Purpose
- ## Scope
- ## Definitions
- ## Roles and Responsibilities (### Accountable / Responsible / Support / Consulted / Informed)
- ## Safety and Precautions
- ## Procedure (### Step N: name)
- ## Related Artifacts (### Requirements / Decisions / Goals / Acceptance Criteria / Sops)
- ## More Information
- ## Updates (### {ISO8601} — {title}, newest-first per the feat domain convention — SOP uses `### 2026-08-30 09:00:00.000+02:00 — Created`)

Status lifecycle: draft → review → approved → active → retired (5 values).

Base directory: grepping \_doc_paths.py for SPECMGR_SOP_DIR turned up nothing — let me check how doc_base_dir resolves the environment variable. Probably `SPECMGR_{TYPE}_DIR` is being built dynamically. Let me grep more broadly.

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"environ\\|getenv\\|SPECMGR\\|base_dir\" src/biz/dfch/specmgr/general/tools/_doc_paths.py | head -20; echo ===; ls .specmgr/sop 2>/dev/null || echo \"no .specmgr/sop dir yet\""
}
```

**Output:**

```
28:``SPECMGR_ADR_DIR``/``docs/adr`` env var and default (``adr.tools._paths``).
33:dependency beyond read-only directory listing: :func:`doc_base_dir` never
35:only :func:`ensure_doc_base_dir` does. There is deliberately no in-memory
53:    "doc_base_dir",
54:    "ensure_doc_base_dir",
61:DOCS_DIR_ENV_VAR = "SPECMGR_DOCS_DIR"
85:    value = os.environ.get(DOCS_DIR_ENV_VAR)
90:def doc_base_dir(type_name: str) -> Path:
93:    Reads :data:`DOCS_DIR_ENV_VAR` from the environment, falling back to
97:    directory -- see :func:`ensure_doc_base_dir` for the write path.
116:def ensure_doc_base_dir(type_name: str) -> Path:
120:    tool/resource uses the read-only :func:`doc_base_dir` instead.
136:    result = doc_base_dir(type_name)
170:def iter_doc_paths(base_dir: Path) -> Iterator[Path]:
171:    """Yield every ``*.md`` file directly under ``base_dir``, sorted by name.
173:    Yields nothing (rather than raising) if ``base_dir`` does not exist.
177:    base_dir:
185:    assert isinstance(base_dir, Path), type(base_dir)
187:    if not base_dir.exists():
189:    result = iter(sorted(base_dir.glob("*.md")))
===
no .specmgr/sop dir yet

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 42.4s)

_Thinking:_

The SOP base directory is the `SPECMGR_DOCS_DIR` environment variable, or if that's not set, a fallback is used (probably `.specmgr/sop` — line 93 says "falls back to ...", so let's not chase this too deep. In the plan, we can just write "verify the fallback default at implementation time (probably `.specmgr/sop/`)").

Let me quickly check the fallback default on lines 93–100 of doc_base_dir.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/_doc_paths.py",
  "offset": 90,
  "limit": 28
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/_doc_paths.py</path>
<type>file</type>
<content>
90: def doc_base_dir(type_name: str) -> Path:
91:     """Return the base directory for ``type_name`` documents, without creating it.
92: 
93:     Reads :data:`DOCS_DIR_ENV_VAR` from the environment, falling back to
94:     :data:`DEFAULT_DOCS_ROOT`, then appends ``type_name`` as a subdirectory
95:     (e.g. ``docs/req`` for ``type_name="req"``). Read-only tools/resources
96:     use this so merely reading never has the side effect of creating the
97:     directory -- see :func:`ensure_doc_base_dir` for the write path.
98: 
99:     Parameters
100:     ----------
101:     type_name:
102:         The document type's subdirectory name, e.g. ``"req"``.
103: 
104:     Returns
105:     -------
106:     Path
107:         The resolved base directory for ``type_name`` documents.
108:     """
109:     assert isinstance(type_name, str), type(type_name)
110:     assert type_name.strip()
111: 
112:     result = _docs_root() / type_name
113:     return result
114: 
115: 
116: def ensure_doc_base_dir(type_name: str) -> Path:
117:     """Return the base directory for ``type_name`` documents, creating it if missing.

(Showing lines 90-117 of 245. Use offset=118 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 39.1s)

_Thinking:_

Default document root — grep for DEFAULT_DOCS_ROOT:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"DEFAULT_DOCS_ROOT\" -A 3 src/biz/dfch/specmgr/general/tools/_doc_paths.py | head -8; grep -rn \"docs/req\\|docs/adr\" .specmgr/feat/feat-30-sop/README.md 2>/dev/null | head -3"
}
```

**Output:**

```
23:env var (:data:`DOCS_DIR_ENV_VAR`, default :data:`DEFAULT_DOCS_ROOT`) holds
24-every doc type's own subdirectory (``{root}/{type_name}/``, e.g. ``docs/req/``
25-for ``type_name="req"``).
26-
--
50:    "DEFAULT_DOCS_ROOT",
51-    "DOCS_DIR_ENV_VAR",
52-    "DocNotFoundError",

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 41.3s)

_Thinking:_

The default documentation root is `docs/` (i.e., SOPs by default go in `docs/sop/`, and can be overridden with `SPECMGR_DOCS_DIR`). Interesting point: `docs/adr/` is where ADRs live. So SOPs default to `docs/sop/`.

Hmm, wait, let me check the value of the DEFAULT_DOCS_ROOT constant:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"^DEFAULT_DOCS_ROOT\" -A 2 src/biz/dfch/specmgr/general/tools/_doc_paths.py"
}
```

**Output:**

```
64:DEFAULT_DOCS_ROOT = Path("docs")
65-
66-#: Anything that isn't a lowercase ASCII letter or digit, run-collapsed.

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 159.6s)

_Thinking:_

The default SOP base directory is `docs/sop/` (overridable via the `SPECMGR_DOCS_DIR` environment variable).

That's everything I need to answer the user's question and present the plan. Key points:

**Yes — we can, and it fits well.** The SOP domain (which we just merged via PR #34) is precisely designed for "structured step-by-step operational documents equipped with RASCI-style role assignments and a closed approval/activation lifecycle." The release procedure is a textbook SOP.

**What the SOP adds to script + command:**

1. A **formal, version-controlled, approval-gated** master for the procedure (draft → review → approved → active → retired)
2. **Both paths**: the automated one (script stage / agent command) and the manual fallback (bare git/gh/uv commands) in the same document — exactly what the user meant by "with or without script or agent support"
3. **Roles**: RASCI mapping for the human + agent split (Accountable: repo owner; Responsible: release agent; Support: script + CI; Consulted: human at the version confirmation + merge gate; Informed: community downstream / PyPI consumers)
4. **Safety and Precautions**: the irreversible steps (tag push → publish to PyPI, ff-only merge to keep invariants, don't re-bump, empty changelog), failure/resume protocol
5. A **stable reference target**: the script header, command file, and README can all cite the SOP's id as the canonical source; procedure changes go through the SOP (Updates section + status lifecycle) rather than drifting across three files

**Design decision — what is the canonical source?**
Options:

- (a) SOP is canonical; script + command implement it; README points to the SOP. Procedure changes: edit the SOP (active lifecycle), then sync the script.
- (b) Script is canonical; SOP documents it.
  I recommend (a): the SOP is the human-readable master with the approval gate; the script is its executable projection. The SOP's `Procedure` steps map 1:1 to the script stages (Step N ↔ stage name), so drift is visible.

**Where to place it:** `docs/sop/<uuid>-release-...md` (specmgr-generated UUID id, flat file per the sop domain's addressing scheme). Note: `.specmgr/` is for dev artifacts; `docs/` is for public documents — SOPs belong in `docs/sop/` by default.

**Current constraints (important, to state honestly):**

- This session's specmgr MCP server predates the SOP merge → `specmgr_create_sop`/`specmgr_validate_sop` etc. are not available here. Two options:
  1. Restart opencode (the MCP server will pick up the new tools from the repo checkout… wait — is the MCP server running from this repo's source, or from the installed package? The specmgr MCP in my session — how is it launched? Probably configured in ~/.config/opencode (I saw an opencode.jsonc there). If it's launched via `uvx --from biz-dfch-specmgr[mcp] specmgr mcp` it runs the *PyPI package*, not my local dev tree — in which case even a restart won't give me the sop tools until the 0.15.0 release! This is a chicken-and-egg problem. If it's launched from the local repo (e.g., `uv run specmgr mcp`), a restart suffices. I should check the user's opencode config to see how the specmgr server is launched — read-only check: ~/.config/opencode/opencode.jsonc.
  2. Write the SOP file directly (hand-authored, matching the schema), and validate it with a local Python parse: `uv run --frozen --all-extras python -c "from biz.dfch.specmgr.sop.models.v1 import parse_sop; print(parse_sop('docs/sop/<file>'))"` — fully doable in this repo without MCP.
- Option 2 works regardless of the MCP config; I'll propose that (and note that once the server is restarted / the package is released, the MCP tools will also work).

Let me check how the specmgr MCP is launched in the user's config (read-only).

**Proposed SOP content (structure):**

- Title: "Release biz.dfch.SpecMgr (dev → main → tag → PyPI/MCP Registry)"
- Purpose: produce a correct, complete release; single owner of the procedure.
- Scope: version bump + changelog + dev→main + tag + publish + release notes; out of scope: feature development, hotfix policy (note: hotfixes are not covered → future SOP or note).
- Definitions: stage, ff-only invariant, publish jobs.
- Roles: Accountable: repo maintainer (dfch); Responsible: release agent (opencode) via the /release command; Support: scripts/release.sh, GitHub Actions (ci.yml, publish.yml), PyPI Test/Prod, MCP Registry; Consulted: maintainer (version confirmation, merge gate); Informed: users of the package (via the GH release).
- Safety and Precautions: main must be an ancestor of dev (ff-only invariant — never squash/merge-commit into main); a tag push publishes to TestPyPI+PyPI+MCP Registry (irreversible); don't re-run bump on the same version; an empty [Unreleased] is a stop condition; CI failure → stop, no auto-retry; the release commit is exactly 3 files.
- Procedure: steps mirroring the stages:
  - Step 1: version resolution (S1: resolve + confirmation) — automated: `scripts/release.sh resolve <arg>`; manual: read the pyproject version, apply semver
  - Step 2: precheck (clean tree, dev, main is an ancestor, CI green, tag absent, lock in sync)
  - Step 3: changelog curation (agent-only step; manual: hand-edit [Unreleased])
  - Step 4: bump + lock (pyproject, uv lock, 3-file assertion)
  - Step 5: commit + push dev + wait for CI
  - Step 6: PR dev→main + wait for checks + maintainer confirmation + ff-only merge
  - Step 7: tag on main's HEAD + push + back to dev
  - Step 8: wait for publish (4 jobs)
  - Step 9: release notes + verify assets
  - Each step: "Automated" (command/stage) + "Manual fallback" (raw commands)
- Related Artifacts: ADRs (ece4554b domain-first? more relevant: ADR 9c687bb1 pre-commit, the sop domain's ADR 36905d5b? Actually the Related Artifacts section has Requirements/Decisions/Goals/ACs/Sops subsections — what to cite: ADRs about the release process? There's the CI/publish workflow; feat-30-sop (the domain that hosts this SOP), the README's Make a Release section.
- Updates: created entry.
- Status: draft → (after review) → active. Plan: create as draft, user reviews, we flip to active via set_status (or manually).

**Plan restructuring** (integrating everything agreed so far):

- Phase 0 (new): author the SOP in `docs/sop/` (hand-written + local parse validation), status draft
- Phase 1: scripts/release.sh (stages mirror the SOP's steps; the script header cites the SOP id)
- Phase 2: .opencode/command/release.md (cites the SOP id)
- Phase 3: README Make a Release (points to the SOP as canonical + how to use the command/script) + one line in AGENTS.md
- Phase 4: validation (bash -n, dry run, local parse of the SOP, opencode restart, /release --dry-run minor smoke test)
- Phase 5 (follow-up, after user review): SOP status draft → active

Open questions:

1. Is the SOP the canonical master (script/command/README are its projections) — confirm the direction?
2. How is the specmgr MCP server launched (check the config now — read-only), to know whether the MCP sop tools will be available after a restart or only after the next release? Actually I can just check it myself.
3. SOP id: specmgr-generated UUID via the tool (unavailable in this session) vs. hand-written — the domain's addressing scheme is a UUID id that the server assigns on creation; hand-writing means I have to generate the UUID myself (uuidgen) and use it consistently in the frontmatter id + filename. That's fine (id is just a UUID string, and create_sop "assigns a new id" — the same shape). Note: the filename convention is `<id>-<slug>.md`? For sop, iter_doc_paths globs \*.md directly under docs/sop/. The ADR filename convention is `<uuid>-<slug>.md`. For sop, I'll check the naming used elsewhere… the sop domain's addressing is "flat files directly under the base directory" — the create tool derives the filename from the H1 title + id. Hand-written: `docs/sop/<uuid>-<slug-from-title>.md`. I'll validate with parse_sop at implementation time.
4. Should the SOP also cover the "hotfix" path? Scope note: out of scope (v1) — just note it in Scope.

Let me check the MCP server launch config (read-only) before I answer. ~/.config/opencode/opencode.jsonc.

One more fact — how this session's specmgr MCP server is launched (determines whether `sop` MCP tools appear after a restart):

**Tool: bash**

**Input:**

```json
{
  "command": "cat ~/.config/opencode/opencode.jsonc 2>/dev/null | head -40; ls .opencode/ ; cat .vscode/launch.json 2>/dev/null | head -20"
}
```

**Output:**

```
{
    "$schema": "https://opencode.ai/config.json",
    "formatter": true,
    "lsp": true,
    "provider": {
        "abacus": {
            "npm": "@ai-sdk/openai-compatible",
            "name": "Abacus",
            "options": {
                "baseURL": "https://routellm.abacus.ai/v1"
            },
            "models": {}
        },
        "vllm-dgx": {
            "npm": "@ai-sdk/openai-compatible",
            "name": "vllm (DGX)",
            "options": {
                "baseURL": "http://192.168.1.46:8000/v1"
            },
            "models": {
                "qwen3.8:27b-nvfp4-896k": {
                    "name": "qwen3.8:27b-nvfp4-896k",
                    "limit": {
                        "context": 917504,
                        "output": 131072
                    },
                    "variants": {
                        "off": {
                            "chat_template_kwargs": {
                                "enable_thinking": false
                            }
                        },
                        "low": {
                            "reasoningEffort": "low"
                        },
                        "medium": {
                            "reasoningEffort": "medium"
                        },
                        "xhigh": {
                            "reasoningEffort": "xhigh"
agent
command
node_modules
package.json
package-lock.json

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 38.6s)

_Thinking:_

the global config has providers written in it, but I need the mcp section. Let me try grepping for "mcp" inside the config file.

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n -A 10 '\"mcp\"' ~/.config/opencode/opencode.jsonc | head -30"
}
```

**Output:**

```
172:    "mcp": {
173-        "excalidraw": {
174-            "type": "local",
175-            "command": [
176-                "npx",
177-                "-y",
178-                "mcp-excalidraw-server"
179-            ],
180-            "enabled": false,
181-            "env": {
182-                "PORT": "3030",
--
229:                "mcp"
230-            ]
231-        },
232-        "specmgr-test": {
233-            "type": "local",
234-            "enabled": false,
235-            "command": [
236-                "uv",
237-                "run",
238-                // "--no-cache",
239-                "--directory",
--
242:                "mcp"
243-            ]
244-        },
245-        "asdste100-test": {
246-            "type": "local",
247-            "enabled": false,

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 41.2s)

_Thinking:_

Around lines 220-244 there's a specmgr entry, and there's also a disabled "specmgr-test". In order to check how the active specmgr server is being launched (from the local repository via `uv run --directory ... specmgr mcp`, or from the PyPI package via uvx), let me take a look at the complete mcp section.

**Tool: bash**

**Input:**

```json
{
  "command": "sed -n '215,250p' ~/.config/opencode/opencode.jsonc"
}
```

**Output:**

```
                "npx",
                "@playwright/mcp@latest",
                "--headless"
            ]
        },
        "specmgr": {
            "type": "local",
            "enabled": true,
            "command": [
                "uvx",
                // "--no-cache",
                "--from",
                "biz-dfch-specmgr[mcp]>=0.4.0",
                "specmgr",
                "mcp"
            ]
        },
        "specmgr-test": {
            "type": "local",
            "enabled": false,
            "command": [
                "uv",
                "run",
                // "--no-cache",
                "--directory",
                "/home/user/src/biz.dfch.SpecMgr",
                "specmgr",
                "mcp"
            ]
        },
        "asdste100-test": {
            "type": "local",
            "enabled": false,
            "command": [
                "uvx",
                // "--no-cache",

```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 202.2s)

_Thinking:_

Major discovery: the active `specmgr` MCP server is being run from **the PyPI package** (`uvx --from "biz-dfch-specmgr[mcp]>=0.4.0"`), not from the local dev tree. Therefore, even if I restart opencode, the `sop` MCP tool **will not be obtained** until the SOP release (v0.15.0) is published to PyPI. This is the very chicken-and-egg situation I was suspecting: the SOP domain ships in the next release, but the MCP server in this session is the 0.14.0 package.

There's a disabled `specmgr-test` server that runs from the local repository (`uv run --directory /home/user/src/biz.dfch.SpecMgr specmgr mcp`). For creating/verifying the SOP in this session, we could:

- Option 1: hand-write the SOP markdown + verify with a local Python parse (`uv run --frozen --all-extras python -c "parse_sop(...)"`) — no config change needed.
- Option 2: temporarily enable `specmgr-test` (a config change — requires user consent + restart) and use the actual MCP tools.
- Option 3: use the SOP MCP tools in a future session after the 0.15.0 release (fully dogfooding, but the SOP has to exist before that release… circular).

For the plan: Option 1 (hand-write + local parse verification) is the practical choice — the file format is the same either way (MCP's create_sop just writes the same markdown under docs/sop/). Also note: the UUID id can be generated with uuidgen; the filename follows the `<id>-<slug>.md` convention (I'll check what create_sop does at implementation time — the dec/feat create tools "derive the filename from the H1 title in the body"; the sop tools are the same: "assigns a new id, derives the filename from the H1 title in the body"). In other words, filename = `<uuid>-<slug-from-h1>.md`. I'll reflect this at implementation time.

Now, structuring the response:

1. **Yes — and here's why it fits**: the SOP domain is designed for exactly this; the release procedure is a textbook SOP; it's also a dogfooding of the feature we just released.

2. **What the SOP gives us** (compared to the script+command plan):

   - A formal, approval-gated canonical (draft → review → approved → active → retired)
   - Both paths in one document: each step has an automated (stage/command) and a manual fallback (raw git/gh/uv) — exactly the "with or without script or agent support" the user wants
   - RASCI roles for the human/agent split
   - Safety and Precautions section for the irreversible points (tag → publish; ff-only invariant)
   - A single reference point that the script header, command file, and README can all cite; the procedure's steps map 1:1 to the script's stages

3. **Relationship / canonical**: SOP = canonical procedure; script = executable projection (stages mirror the steps, and cite the SOP id in the header); command = agent protocol that drives the script; README = pointer. Changes to the procedure start from the SOP (Updates entry), then sync to script/command.

4. **Location**: `docs/sop/<uuid>-<slug>.md` (the domain's default base directory; the id is a specmgr-style UUID, not feat-style).

5. **Practical constraint (discovery)**: the active specmgr MCP server is the PyPI 0.14.0 package (uvx) → the sop tool isn't available in this session even after a restart; there is a disabled `specmgr-test` (local repo). Plan: hand-write the SOP + verify with a local `parse_sop` (same output as the MCP tool); optionally, the user can enable `specmgr-test` if they prefer going through the real tool.

6. **SOP content outline** (sections → content, in particular Procedure steps 1–9 corresponding to the stages, each with automated + manual subpaths; Safety and Precautions listing the invariant points; RASCI mapping).

7. **Updated phase plan**: Phase 0 SOP (draft) → Phase 1 script → Phase 2 command → Phase 3 docs (README/AGENTS) → Phase 4 verification → Phase 5 SOP lifecycle (user review → approved → active), probably after the first real release proves the procedure.

8. Open questions:
   a. Confirm SOP-as-canonical?
   b. Creation method: hand-write + local parse (recommended) vs. enabling `specmgr-test` MCP (config change + restart)?
   c. SOP lifecycle: create as `draft`, flip to `active` after the first successful automated release (dogfooding proof), or approve right after the user review?
   d. Hotfix path: out of scope for v1 (note in Scope)?

Keep the answer structured but not verbose. Use the question tool for the 3–4 open items. Actually, (d) is trivial — bake it into the plan (out of scope, noted). (c) I can just recommend; maybe not worth asking. What I'll ask is: (a) canonical direction, (b) creation mechanism, (c) when to activate. Three questions.

Yes — and it fits remarkably well, with one practical wrinkle I just found. Here's the analysis:

## Why an SOP is the right container

The `sop` domain (which we shipped in PR #34 minutes ago) is defined as exactly this: a *structured, step-by-step operational document with RASCI responsibility assignment and a closed approval/effectivity lifecycle* (`draft → review → approved → active → retired`). A release procedure is the textbook SOP. And writing the repo's first real SOP dogfoods the domain on its very next release.

**What it adds over script+command:**

- **Both paths in one document** — exactly your "with or without script and agent support": every `Procedure` step carries an *Automated* sub-path (script stage / `/release`) **and** a *Manual fallback* (raw `git`/`gh`/`uv` commands). If the script is missing, broken, or the release is an emergency, the SOP still works.
- **RASCI for the human/agent split** — Accountable: you (maintainer); Responsible: the release agent via `/release`; Support: `scripts/release.sh`, GitHub Actions, PyPI/MCP Registry; Consulted: you at the two gates (version confirmation, merge go-ahead); Informed: downstream users via the GH Release.
- **Safety and Precautions** as a first-class section — the ff-only invariant (never let main carry unique commits), the irreversibility of the tag push (publishes to TestPyPI→PyPI→MCP Registry), "no re-bump on the same version", empty-`[Unreleased]` stop condition, 3-file release commit.
- **Approval gate + Updates history** — procedure changes go through the SOP's lifecycle instead of silently drifting between README, script, and command.
- **Single citation target** — script header, command file, and README all reference the SOP's id; its 9 steps map 1:1 to the 9 script stages, so drift is visible.

**Proposed canonical hierarchy:** SOP = the procedure (source of truth) · script = its executable projection (stages mirror steps, cite the SOP id) · command = the agent protocol driving the script · README = pointer + manual fallback.

## The wrinkle: this session's specmgr MCP server can't create SOPs

The active server runs the **PyPI package** (`uvx --from "biz-dfch-specmgr[mcp]>=0.4.0"`) — i.e. v0.14.0, from *before* the SOP domain existed. A restart won't help; the `sop` tools only ship in v0.15.0 (chicken and egg — the release that carries them needs this SOP). There is a disabled `specmgr-test` server pointing at this repo, and the SOP file format is plain markdown either way. So the plan is: **hand-author `docs/sop/<uuid>-release-biz-dfch-specmgr.md` and validate it with a local `parse_sop` call** (byte-identical to what `create_sop` would write; the id is a generated UUID, filename derived from the title per the domain's convention).

## SOP outline (maps to the staged design)

- **Purpose/Scope**: produce a complete, correct release; covers version-bump → PyPI/MCP Registry; hotfix path explicitly out of scope (v1)
- **Definitions**: stage, ff-only invariant, publish jobs
- **Roles and Responsibilities**: RASCI as above
- **Safety and Precautions**: the invariant/irreversibility list
- **Procedure** — 9 steps, each `Automated` + `Manual`: (1) resolve version + confirm · (2) pre-checks · (3) curate `[Unreleased]` (agent step; manual: edit by hand) · (4) bump pyproject + `uv lock` · (5) commit 3 files + push dev + wait CI · (6) PR dev→main + wait checks + **merge gate** + `--ff-only` · (7) tag main HEAD + push + back to dev · (8) wait publish (4 jobs) · (9) release notes + verify assets
- **Related Artifacts**: feat-30-sop (the domain), README "Make a Release", `publish.yml`/`ci.yml`
- **Updates**: created entry

## Updated plan (phases)

- **Phase 0 (new)**: author SOP in `docs/sop/`, validate via local `parse_sop`; status `draft`
- **Phase 1**: `scripts/release.sh` (stages mirror SOP steps; header cites SOP id)
- **Phase 2**: `.opencode/command/release.md` (cites SOP id)
- **Phase 3**: README "Make a Release" (SOP canonical + command + script + manual fallback) & AGENTS.md line
- **Phase 4**: verification (`bash -n`, dry-runs, `resolve`/`precheck`/`status`, non-TTY misuse, restart opencode, `/release --dry-run minor`)
- **Phase 5 (later)**: SOP lifecycle — your review, then flip `draft → active`

**Tool: question**

**Input:**

```json
{
  "questions": [
    {
      "header": "Canonical",
      "question": "Confirm the source-of-truth direction: the SOP is the canonical procedure, and script/command/README are its projections (procedure changes start in the SOP, then sync outward)?",
      "options": [
        {
          "label": "SOP canonical (Recommended)",
          "description": "Single approval-gated master; script stages mirror its 9 steps and cite its id."
        },
        {
          "label": "Script canonical",
          "description": "The bash script is the master; the SOP merely documents it."
        }
      ]
    },
    {
      "header": "SOP creation",
      "question": "How should the SOP document be created, given this session's MCP server is the pre-SOP PyPI 0.14.0 package?",
      "options": [
        {
          "label": "Hand-author + parse_sop (Recommended)",
          "description": "Write docs/sop/<uuid>-....md directly, validate with a local uv run parse_sop call. No config changes; identical result to the MCP tool."
        },
        {
          "label": "Enable specmgr-test MCP",
          "description": "Flip the disabled local-repo specmgr server on in ~/.config/opencode, restart opencode, then use create_sop/validate_sop properly. Config change + restart required."
        }
      ]
    },
    {
      "header": "Activation",
      "question": "When should the SOP leave draft and become active?",
      "options": [
        {
          "label": "After first real release (Recommended)",
          "description": "The first /release run is the SOP's acceptance test; flip to active once it succeeds end-to-end."
        },
        {
          "label": "After your review now",
          "description": "You review the draft, we set it active before the script is even written."
        }
      ]
    }
  ]
}
```

**Output:**

```
User has answered your questions: "Confirm the source-of-truth direction: the SOP is the canonical procedure, and script/command/README are its projections (procedure changes start in the SOP, then sync outward)?"="SOP canonical (Recommended)", "How should the SOP document be created, given this session's MCP server is the pre-SOP PyPI 0.14.0 package?"="Enable specmgr-test MCP", "When should the SOP leave draft and become active?"="After first real release (Recommended)". You can now continue with the user's answers in mind.
```

______________________________________________________________________

## Assistant (Plan · qwen3.8-27b-bf16-896k-mtp-1 · 152.2s)

_Thinking:_

User's decisions:

1. SOP is the canonical one
2. **Enable the specmgr-test MCP server** (config change + restart) and use the real `create_sop`/`validate_sop` tools
3. SOP goes to active after the first actual release

Regarding #2, the config change is in `~/.config/opencode/opencode.jsonc` — flipping `"specmgr-test": { ... "enabled": false }` → `true`. But wait: there's a consideration — if I enable specmgr-test while `specmgr` (the PyPI one) is also enabled, both servers' tools get loaded → tool name collisions! Both register `specmgr_create_adr`, `specmgr_list_req`, etc. How does opencode handle duplicate tool names from two MCP servers? Normally it either namespaces per server, or one shadows the other. Looking at the tool list in this session: the tools show up as `specmgr_create_adr` etc. — prefixed with the server name "specmgr". If specmgr-test is enabled, its tools would be `specmgr-test_create_adr`… hmm, actually opencode's MCP tool naming is: `{serverName}_{toolName}` — the server name has a hyphen: "specmgr-test". In the current session, the specmgr server's tools appear in my function list as `specmgr_create_adr`. So if I enable specmgr-test, they should appear as `specmgr-test_create_adr` — no collision, but there would be two copies of every tool.

Cleaner approach: **disable** `specmgr` (PyPI) and **enable** `specmgr-test` (local repo) — a swap. That way there's exactly one specmgr server, running from the dev tree, with all domains including sop. This is clearly the intent of the "test" server (it's a dev-mode swap). The user said "enable the specmgr-test MCP" — in the plan I'll describe it as a swap (disable PyPI specmgr, enable local specmgr-test), and flag that both can also be enabled simultaneously (duplicated tool surface, harmless but noisy). Actually — should I just do what was asked: enable specmgr-test? If both are enabled, tool names: `specmgr_*` (PyPI 0.14.0, no sop) and `specmgr-test_*` (local, with sop). I'd use the specmgr-test\_\* ones for sop work. It works, but it's messy and risks confusion (two sources of truth in one session). I'll recommend the swap and note the alternative. The user already chose "enable specmgr-test" — the swap is the sensible implementation of that choice; I'll note it explicitly in the plan so it can be rejected.

Also note: the MCP config is at the global scope (~/.config/opencode) — changing it affects all projects for this user. The specmgr-test server is repo-specific anyway (it points at this repo's path). A swap is fine.

One more thing to verify: the specmgr-test command: `uv run --directory /home/user/src/biz.dfch.SpecMgr specmgr mcp` — hmm, `uv run` without `--frozen`? It's just `uv run` with a --directory. Without --frozen, uv might update the lockfile if it's out of sync… but we're keeping them in sync. Also, does the base `uv run specmgr mcp` have the mcp extra? `uv run` by default only installs the base dependencies (per the AGENTS.md caveat: "without --all-extras in uv run, only the base dependencies are installed, and you get ModuleNotFoundError for the CLI/MCP extras like typer"). The specmgr-test entry doesn't have --all-extras! It would fail to launch (no mcp/typer). Wait — actually `uv run` in a project directory: uses the project environment; `uv run specmgr mcp` — the entry point `specmgr` requires the cli extra (typer) and mcp. Without --all-extras the entry point might not even be resolvable… actually the script is defined in pyproject's [project.scripts], and the package itself is installed in the project env (base), but the extras' dependencies (typer, mcp) won't be present unless they're in the dev group. pyproject probably has a `dev` extra that includes cli+mcp+test (I saw earlier in uv.lock: `extras = ["cli", "mcp", "test"], marker = "extra == 'dev'"`). `uv run` by default installs the project with no extras, unless there's `default-groups`/dependency-group config. So specmgr-test as currently written is likely broken — needs `--all-extras` (or `--extra mcp --extra cli`). I'll note in the plan: fix the specmgr-test command to include `--all-extras` (matching the AGENTS.md guidance) when enabling it. This is a config detail I should flag.

Hmm, but modifying the user's global opencode config is a system change — currently forbidden in plan mode, fine at execution time. The user approved "enable the specmgr-test MCP" so the config edit is approved in principle; the plan will spell out the exact edit (swap + --all-extras fix).

OK, final consolidated plan. Since I've presented the full plan twice already, this time I'll present a compact final version: the full scope (SOP canonical → script → command → docs → validation → lifecycle) with the MCP swap inserted as the first execution step (a session prerequisite, requiring a restart).

Important sequencing note: because the MCP swap requires restarting opencode, the execution will be: (1) edit the config, (2) user restarts opencode, (3) the rest of the work in the new session. Or: do the config edit + restart first, then everything else. Since plan mode ends when the user approves, the execution sequence should spell this out: step 0 = config swap → restart → then Phases 0–5 in the new session. Alternatively, we could do the hand-crafted SOP work now… no — the user explicitly chose the MCP route. Keep it simple: after approval, I make the config change, tell them to restart, and continue after the restart (in a new session the SOP creation via specmgr-test\_\* tools is the first task).

Hmm wait — actually one subtle point: if I flip the config and the user restarts, the next session's MCP server = the local dev tree. Then `create_sop` assigns a UUID id and writes to `docs/sop/<id>-<slug>.md`. Good. The SOP content itself I'll draft during execution (I have the full design).

Also: does the SOP document need to be committed? Yes — docs/ is a published artifact; the SOP goes in via commit (probably as part of the release work's commit, or as an independent docs commit before the release). It'll be committed as part of this feature work (a chore/docs commit to dev) — note: the SOP is about the release procedure; committing it to dev is fine. It'll flow to main at the next release (ironically, its first release will carry it).

Let me write the final plan compactly, and ask for the go-ahead.

All three decisions locked. One execution detail I found while looking at your config: the disabled `specmgr-test` entry is missing `--all-extras`, so as written it would fail to start (`ModuleNotFoundError` for `mcp`/`typer` — the exact gotcha documented in AGENTS.md). Enabling it means also fixing that line. And enabling it *alongside* the PyPI `specmgr` server would give you two tool surfaces in one session, so the clean move is a **swap**: `specmgr` (PyPI 0.14.0) → disabled, `specmgr-test` (this repo, `--all-extras`) → enabled.

## Final plan v3 (complete scope)

**Step 0 — MCP swap (requires opencode restart):** edit `~/.config/opencode/opencode.jsonc`: `specmgr.enabled = false`, `specmgr-test.enabled = true` + add `--all-extras` to its command. You restart opencode; everything below runs against the local dev tree, `sop` tools included.

**Phase 0 — the SOP (canonical):** via `create_sop` (new `specmgr-test` server): *"Release biz.dfch.SpecMgr (dev → main → tag → PyPI/MCP Registry)"* → `docs/sop/<uuid>-....md`, status `draft`. Sections per the outline: Purpose/Scope (hotfix path out of scope v1) · Definitions · RASCI (you accountable; agent responsible; script+CI+registries support; you consulted at the two gates; users informed) · Safety & Precautions (ff-only invariant, tag-push irreversibility, no re-bump, empty-`[Unreleased]` stop, 3-file commit) · **Procedure: 9 steps, each with Automated (stage/command) + Manual fallback (raw commands)** · Related Artifacts (feat-30-sop, README, workflows) · Updates. Committed to `dev` as its own docs commit.

**Phase 1 — `scripts/release.sh`:** staged per plan v2 (`resolve`/`precheck`/`bump`/`changelog`/`commit-push`/`pr-create`/`pr-merge`/`tag-push`/`publish-wait`/`release-notes`/`status`/`all`), idempotent, `--dry-run`, per-stage working-tree assertions, 30s polls — stages mirror SOP steps 1:1, header cites the SOP id.

**Phase 2 — `.opencode/command/release.md`:** `/release [X.Y.Z|patch|minor|major] [--dry-run]` orchestration protocol: resolve+confirm → precheck → **agent curates `[Unreleased]`** (its only direct file edit) → stages → **merge-gate confirmation after `pr-create`** → failure = `status` + diagnosis + stop, never auto-retry. Cites SOP id.

**Phase 3 — docs:** README "Make a Release" = SOP pointer (canonical) + `/release` usage + `all` mode + manual fallback (now sourced from the SOP); AGENTS.md Developer Commands line.

**Phase 4 — verification:** `bash -n` · non-TTY misuse · `resolve minor` → 0.15.0 · `precheck` · `status 0.15.0` · dry-runs of `bump`/`changelog`/`pr-create` (no mutations) · opencode restart (new command loaded) · `/release --dry-run minor` smoke test.

**Phase 5 — activation (later):** first real `/release 0.15.0` is the SOP's acceptance test → on success, flip SOP `draft → active` via `set_status`.

Ready to execute — starting with the Step 0 config swap, then you restart?

______________________________________________________________________

## User

I already swapped the mcp. Check the live version from the mcp resource.

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 54.5s)

_Thinking:_

The user has already switched over the MCP config and restarted (or is expecting a check). Now in build mode. First: "Verify the running version from the mcp resource."

The specmgr server exposes a `specmgr://version` resource (general/resources). I should be able to read it via `list_mcp_resources` + `read_mcp_resource`. If the server is the local dev tree (0.14.0 + sop domain, since dev has the sop merge — the pyproject version on dev is 0.14.0, but the sop domain code is present), then the version resource will report 0.14.0 (the version in pyproject hasn't been bumped yet — that's what we're going to do in the release!). So the way to distinguish between PyPI 0.14.0 and local dev 0.14.0 is: check whether `sop` tools/resources exist in the live server (e.g., specmgr://sop/schema resource, or specmgr_list_sop tool availability).

Let me list the MCP resources and read the version resource. If `specmgr://version` exists, read it. Additionally, check for `specmgr://sop/template` or similar sop resources to confirm that the local build is running.

**Tool: list_mcp_resources**

**Input:**

```json
{
  "server": "specmgr-test"
}
```

**Output:**

```
{
  "resources": [
    {
      "name": "dec_example",
      "title": "Decision (DEC) Example",
      "uri": "specmgr://dec/example",
      "description": "A complete, valid sample decision document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "dec_schema",
      "title": "Decision (DEC) JSON Schema",
      "uri": "specmgr://dec/schema",
      "description": "The generated DEC JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document.",
      "mimeType": "application/json",
      "server": "specmgr-test"
    },
    {
      "name": "dec_template",
      "title": "Decision (DEC) Template",
      "uri": "specmgr://dec/template",
      "description": "A DEC document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new decision.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "feat_example",
      "title": "Feature (FEAT) Example",
      "uri": "specmgr://feat/example",
      "description": "A complete, valid sample feature document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "feat_schema",
      "title": "Feature (FEAT) JSON Schema",
      "uri": "specmgr://feat/schema",
      "description": "The generated FEAT JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document.",
      "mimeType": "application/json",
      "server": "specmgr-test"
    },
    {
      "name": "feat_template",
      "title": "Feature (FEAT) Template",
      "uri": "specmgr://feat/template",
      "description": "A FEAT document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new feature.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "gol_example",
      "title": "Goal (GOL) Example",
      "uri": "specmgr://gol/example",
      "description": "A complete, valid sample goal document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "gol_schema",
      "title": "Goal (GOL) JSON Schema",
      "uri": "specmgr://gol/schema",
      "description": "The generated GOL JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document.",
      "mimeType": "application/json",
      "server": "specmgr-test"
    },
    {
      "name": "gol_template",
      "title": "Goal (GOL) Template",
      "uri": "specmgr://gol/template",
      "description": "A GOL document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new goal.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "iso25010",
      "title": "ISO/IEC 25010:2023 Product Quality Model",
      "uri": "specmgr://iso25010",
      "description": "The nine main characteristics (and their sub-characteristics) of the ISO/IEC 25010:2023 system/software product quality model, each with a description.",
      "mimeType": "application/json",
      "server": "specmgr-test"
    },
    {
      "name": "prb_example",
      "title": "Problem Statement (PRB) Example",
      "uri": "specmgr://prb/example",
      "description": "A complete, valid sample problem statement document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "prb_schema",
      "title": "Problem Statement (PRB) JSON Schema",
      "uri": "specmgr://prb/schema",
      "description": "The generated PRB JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document.",
      "mimeType": "application/json",
      "server": "specmgr-test"
    },
    {
      "name": "prb_template",
      "title": "Problem Statement (PRB) Template",
      "uri": "specmgr://prb/template",
      "description": "A PRB document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new problem statement.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "qa_example",
      "title": "Question and Answer (QA) Example",
      "uri": "specmgr://qa/example",
      "description": "A complete, valid sample QA document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "qa_schema",
      "title": "Question and Answer (QA) JSON Schema",
      "uri": "specmgr://qa/schema",
      "description": "The generated QA JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document.",
      "mimeType": "application/json",
      "server": "specmgr-test"
    },
    {
      "name": "qa_template",
      "title": "Question and Answer (QA) Template",
      "uri": "specmgr://qa/template",
      "description": "A QA document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new QA document.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "rasci",
      "title": "RASCI Responsibility Assignment Guidance",
      "uri": "specmgr://rasci",
      "description": "What RASCI is (Responsible, Accountable, Support, Consulted, Informed), the five roles' standard definitions, and how RASCI differs from plain RACI, as raw markdown guidance.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "req_example",
      "title": "Requirement (REQ) Example",
      "uri": "specmgr://req/example",
      "description": "A complete, valid sample requirement document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "req_schema",
      "title": "Requirement (REQ) JSON Schema",
      "uri": "specmgr://req/schema",
      "description": "The generated REQ JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document.",
      "mimeType": "application/json",
      "server": "specmgr-test"
    },
    {
      "name": "req_template",
      "title": "Requirement (REQ) Template",
      "uri": "specmgr://req/template",
      "description": "A REQ document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new requirement.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "rsk_example",
      "title": "Risk (RSK) Example",
      "uri": "specmgr://rsk/example",
      "description": "A complete, valid sample risk document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "rsk_risk_matrix",
      "title": "Risk (RSK) 5x5 Risk Matrix",
      "uri": "specmgr://rsk/risk-matrix",
      "description": "The 5x5 risk matrix: probability/impact scale anchors, the zone table, and the product thresholds (what 'high risk' and 'low risk' mean), as raw markdown domain-knowledge guidance.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "rsk_schema",
      "title": "Risk (RSK) JSON Schema",
      "uri": "specmgr://rsk/schema",
      "description": "The generated RSK JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document.",
      "mimeType": "application/json",
      "server": "specmgr-test"
    },
    {
      "name": "rsk_tara",
      "title": "Risk (RSK) TARA Guidance",
      "uri": "specmgr://rsk/tara",
      "description": "What TARA is (Transfer, Accept, Reduce, Avoid), the four valid `## Strategy` words, and when and how to apply each, as raw markdown domain-knowledge guidance.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "rsk_template",
      "title": "Risk (RSK) Template",
      "uri": "specmgr://rsk/template",
      "description": "A risk document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new risk.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "sop_example",
      "title": "Standard Operating Procedure (SOP) Example",
      "uri": "specmgr://sop/example",
      "description": "A complete, valid sample Standard Operating Procedure document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "sop_schema",
      "title": "Standard Operating Procedure (SOP) JSON Schema",
      "uri": "specmgr://sop/schema",
      "description": "The generated SOP JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document.",
      "mimeType": "application/json",
      "server": "specmgr-test"
    },
    {
      "name": "sop_template",
      "title": "Standard Operating Procedure (SOP) Template",
      "uri": "specmgr://sop/template",
      "description": "A SOP document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new Standard Operating Procedure.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "tsk_example",
      "title": "Task List (TSK) Example",
      "uri": "specmgr://tsk/example",
      "description": "A complete, valid sample task list document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "tsk_schema",
      "title": "Task List (TSK) JSON Schema",
      "uri": "specmgr://tsk/schema",
      "description": "The generated TSK JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document.",
      "mimeType": "application/json",
      "server": "specmgr-test"
    },
    {
      "name": "tsk_template",
      "title": "Task List (TSK) Template",
      "uri": "specmgr://tsk/template",
      "description": "A TSK document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new task list.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "uc_example",
      "title": "Use Case (UC) Example",
      "uri": "specmgr://uc/example",
      "description": "A complete, valid sample use case document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "uc_schema",
      "title": "Use Case (UC) JSON Schema",
      "uri": "specmgr://uc/schema",
      "description": "The generated UC JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document.",
      "mimeType": "application/json",
      "server": "specmgr-test"
    },
    {
      "name": "uc_template",
      "title": "Use Case (UC) Template",
      "uri": "specmgr://uc/template",
      "description": "A UC document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new use case.",
      "mimeType": "text/markdown",
      "server": "specmgr-test"
    },
    {
      "name": "version",
      "title": "SpecMgr MCP Server Version",
      "uri": "specmgr://version",
      "description": "Installed version number of the biz-dfch-specmgr package that backs this MCP server. Lets a client check compatibility without a tool round-trip.",
      "mimeType": "application/json",
      "server": "specmgr-test"
    }
  ]
}
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 49.0s)

_Thinking:_

The `specmgr-test` server is currently running, and all SOP resources (`specmgr://sop/example`, `specmgr://sop/schema`, `specmgr://sop/template`) are present — this confirms that it's a local dev tree that includes the SOP domain. Also, the `specmgr://rasci` resource (general, REQ-011) is present too.

Next, I'll read `specmgr://version` to check the running version. Note: since the version in pyproject on dev is still 0.14.0 (bumping it is the job of the release), it will probably display as 0.14.0. However, the existence of the SOP resources is the real proof that it's the local dev build.

The `specmgr-test` server is live with all three SOP resources registered — reading the version resource:

**Tool: read_mcp_resource**

**Input:**

```json
{
  "server": "specmgr-test",
  "uri": "specmgr://version"
}
```

**Output:**

```
Resource: specmgr://version
MIME: application/json
{
  "specmgr": "0.14.0"
}
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 123.8s)

_Thinking:_

The running version is 0.14.0 — this is the pyproject version on dev (unchanged; the release itself will bump it to 0.15.0). The fact that the `specmgr://sop/*` resource exists proves that this is a local dev build (the PyPI 0.14.0 package shouldn't have the sop domain — wait, actually, hold on. PyPI 0.14.0 was released from dev after the sop merge? Let me think.

Timeline:

- v0.14.0 was tagged from dev (commit 4c7d976 "chore(release): increase version to v0.14.0" is the tip of main, and it's on the dev line too)
- PR #34 (sop) was merged into dev today at ec3d644 — after the v0.14.0 tag
- So PyPI 0.14.0 = dev at the 4c7d976 point = no sop domain
- Local dev tree = ec3d644..1a0daf3 = has sop domain

Therefore: the running version "0.14.0" + the existence of the sop resource = a local dev tree built from the post-sop-merge code. If it had been PyPI 0.14.0, the sop resource wouldn't exist. Confirmed: the swap was successful, and it's running locally.

Interesting implication: the next release (0.15.0) will be the first one to ship the sop domain to PyPI. And this SOP document (release SOP) will be included in it.

Also, I should check whether the old `specmgr` (PyPI) server is gone — the list I requested was only for specmgr-test. Let me quickly check the global list to see if both are running (in case the user just added specmgr-test without disabling specmgr). Actually, the user said "I already swapped the mcp" — meaning both directions. I can verify with list_mcp_resources (all servers). Let me quickly check, then report the status.

Then, per the plan, proceed to Phase 0: create the SOP via specmgr-test_create_sop.

No wait — the plan is approved (build mode is enabled, and the user's message is effectively a "go" for step 0 verification). Should I now proceed to build the whole thing (SOP, script, command, docs)? The user's last instruction was "check the running version from the mcp resource" — that's a specific verification request. The bigger plan (v3) was already approved... let me actually check: did the user explicitly approve execution of plan v3? My last message ended with "shall we proceed — starting with the step 0 config swap, then you restart?" and the user replied "I already swapped the mcp. Check the running version from the mcp resource." + mode switched to build. This is a go signal: step 0 is done by the user, they asked for verification, and the mode change to build means it's okay to execute the plan.

So: verify (done: 0.14.0 local with sop), report briefly, then start Phase 0 (SOP creation). This is a big task — let me set up todos:

1. Verify MCP swap (done)
2. Phase 0: Create SOP via specmgr-test (draft), commit
3. Phase 1: scripts/release.sh
4. Phase 2: .opencode/command/release.md
5. Phase 3: README + AGENTS.md
6. Phase 4: Verification
   (Phase 5 is later, after the actual release)

Let me set up the todo list, then read the sop template + example + rasci resource from the live server, and create the SOP properly (the create_sop prompt probably says "read specmgr://rasci first" — per AGENTS.md: "both prompts include an explicit read-first step for specmgr://rasci before ## Roles and Responsibilities").

For SOP content, I need to draft the full body. Let me first fetch the template and example (from the live MCP) to align precisely with the schema, then write the SOP content.

Title: "Release biz.dfch.SpecMgr (dev → main → tag → PyPI/MCP Registry)" — hmm, filename is derived from H1. Shorter: "Release biz-dfch-specmgr to PyPI and the MCP Registry"? The package is biz-dfch-specmgr on PyPI. Let me go with: "Release biz.dfch.SpecMgr (version bump, dev → main, tag, publish)". Filename slug generation — the tool derives it; either is fine. Let me keep the H1 concise: "Release biz.dfch.SpecMgr".

Actually, let me think about what the H1/title should be for a good slug: "Perform a release of biz.dfch.SpecMgr" → slug is probably "perform-a-release-of-biz.dfch-specmgr". Dots in filenames... does the domain slugify collapse runs of non-alphanumerics? \_doc_paths has a slug regex: "collapse runs of anything that isn't a lowercase ASCII letter or digit". So dots are handled (collapsed). OK.

Let me go with the title: "Release biz.dfch.SpecMgr (dev → main → tag → PyPI/MCP Registry)". Arrows and slashes in the H1 are fine for markdown, but for the slug: "release-biz.dfch.specmgr-dev-main-tag-pypi-mcp-registry" → collapsed: "release-bizdfchspecmgr-dev-main-tag-pypi-mcpregistry". Long, but fine. Hmm, maybe simpler: "Release biz.dfch.SpecMgr to PyPI and MCP Registry" → slug "release-bizdfchspecmgr-to-pypi-and-mcp-registry". Better. But this SOP also covers the dev→main/tag steps — the title should reflect the whole procedure, not just the endpoints. "Perform a release of biz.dfch.SpecMgr" is cleanest. Going with this.

Plan for this turn:

1. Report the verification result (0.14.0 local, sop present, swap OK).
2. Set up todos.
3. Read the sop template + example + rasci from the live server (the create_sop prompt flow expects reading rasci first — I'm not running the prompt, I'm using the tool directly, but reading rasci is still good practice for the Roles section).
4. Draft + create the SOP via specmgr-test_create_sop.
5. Commit the SOP (docs commit to dev).
6. Then Phase 1 (script) — the big part.

Lots to do; let me get started. First the report + todos + reading resources in parallel.

Confirmed the swap: the running server is the local development tree — the version resource reports `0.14.0` (the pyproject version on `dev`, still un-bumped), but `specmgr://sop/*` exists, and that only exists after the merge of PR #34. PyPI's 0.14.0 does not include the SOP domain. Therefore `specmgr-test` is running from this repository.

Kicking off execution of Plan v3 — first Phase 0 (SOP):

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Verify specmgr-test MCP swap (version + sop resources)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 0: create release SOP via specmgr-test (draft), commit to dev",
      "status": "in_progress",
      "priority": "high"
    },
    {
      "content": "Phase 1: scripts/release.sh (staged, idempotent, --dry-run, status, all)",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 2: .opencode/command/release.md orchestration protocol",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 3: README 'Make a Release' + AGENTS.md updates",
      "status": "pending",
      "priority": "medium"
    },
    {
      "content": "Phase 4: verification (bash -n, dry-runs, resolve/precheck/status, non-TTY misuse)",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 5 (later): first real /release 0.15.0, then SOP draft → active",
      "status": "pending",
      "priority": "low"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Verify specmgr-test MCP swap (version + sop resources)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 0: create release SOP via specmgr-test (draft), commit to dev",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Phase 1: scripts/release.sh (staged, idempotent, --dry-run, status, all)",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 2: .opencode/command/release.md orchestration protocol",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 3: README 'Make a Release' + AGENTS.md updates",
    "status": "pending",
    "priority": "medium"
  },
  {
    "content": "Phase 4: verification (bash -n, dry-runs, resolve/precheck/status, non-TTY misuse)",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 5 (later): first real /release 0.15.0, then SOP draft → active",
    "status": "pending",
    "priority": "low"
  }
]
```

**Tool: read_mcp_resource**

**Input:**

```json
{
  "server": "specmgr-test",
  "uri": "specmgr://sop/template"
}
```

**Output:**

```
Resource: specmgr://sop/template
MIME: text/markdown
---
created: 2026-08-30
id: deadbeef-dead-dead-dead-deadbeefdead
status: draft
type: sop
updated: 2026-08-30
version: 1.0.0
---

# Level 1 Heading is the Title of the Standard Operating Procedure

## Purpose

Why this SOP exists and the outcome it produces.

## Scope

What this SOP covers, and optionally what it does not.

## Definitions

- A term-of-art used by this SOP, defined for the reader.

## Roles and Responsibilities

### Accountable

The single owner who is ultimately answerable for this SOP.

### Responsible

- A party who does the work the SOP describes.

### Support

- A party who provides resources or assistance to the responsible parties.

### Consulted

- A party whose opinion is sought before or during the work.

### Informed

- A party who is kept up to date on progress or outcomes.

## Safety and Precautions

Warnings and precautions to read before following the procedure.

## Procedure

### Step 1: name of the first step

The actions that make up the first step.

## Related Artifacts

### Requirements

- A bullet list with related requirements, e.g. REQ-0001: title.

### Decisions

- A bullet list with related decisions, e.g. DEC-0001: title.

### Goals

- A bullet list with related goals, e.g. GOL-0001: title.

### Acceptance Criteria

- A bullet list with related acceptance criteria, e.g. ACC-0001: title.

### Sops

- A bullet list with related SOPs, e.g. SOP-0001: title.

## More Information

Optional free-form supplementary text.

## Updates

### 2026-08-30 09:00:00.000+02:00 — Created

A lead paragraph describing this update.

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 45.0s)

_Thinking:_

Got the template. Next, I'll also read the SOP example (to check how a filled-in example looks — especially the format of the procedure steps) and the RASCI resource (guidance for the roles section). After that, I'll draft the SOP.

**Tool: read_mcp_resource**

**Input:**

```json
{
  "server": "specmgr-test",
  "uri": "specmgr://sop/example"
}
```

**Output:**

```
Resource: specmgr://sop/example
MIME: text/markdown
---
created: 2026-06-15
id: c4e7b8a3-1f2d-4e9c-8b6a-3d5f7e9c1a2b
status: active
type: sop
updated: 2026-08-30
version: 1.0.0
---

# New Employee IT Account Provisioning

## Purpose

This procedure defines how the IT department provisions accounts,
hardware, and core application access for a new employee between the
confirmation of their start date and the end of their first working
day. It exists so that every new starter can begin productive work
immediately on day one, with the correct access for their role and no
unauthorized privileges.

## Scope

This procedure applies to all permanent and fixed-term employees
onboarded into the engineering and corporate functions. It does not
cover contractors (handled by the vendor-onboarding procedure), interns
covered by the internship program, or access to regulated systems
requiring a separate compliance review (handled by the access-control
review board). It covers directory accounts, email, endpoint
enrollment, and the standard application catalog; bespoke application
access requested outside the standard catalog follows the exception
process in the access-management policy.

## Definitions

- A new starter is an employee whose start date has been confirmed in
  writing by HR and entered into the HRIS.
- The standard application catalog is the published list of
  applications whose access can be granted by role, without an
  additional business justification.
- An endpoint is the laptop or workstation imaged and assigned to the
  new starter.
- An access ticket is the ITSM record that tracks this provisioning
  request end to end.

## Roles and Responsibilities

### Accountable

The IT Operations Manager is accountable for ensuring that every new
employee is provisioned correctly and on time, and for the overall
health of this procedure.

### Responsible

- IT Service Desk engineers create the directory account, enroll the
  endpoint, and assign the standard application roles.
- The hiring manager submits the access ticket with the confirmed role
  and start date, and confirms any role-specific access on day one.
- HR notifies IT of the confirmed start date at least three working
  days before it.

### Support

### Consulted

- Information Security is consulted on any access that falls outside
  the standard application catalog.
- The Facilities team is consulted when the new starter needs a desk or
  building access badge.

### Informed

- The new starter is informed by email once the account is ready and
  the endpoint is available for collection.
- The hiring manager is informed when provisioning is complete.

## Safety and Precautions

Do not grant access that the role does not require: least-privilege is
the default, and any deviation must be recorded on the access ticket
with a business justification and the approving manager's name. Never
reuse a directory account that belonged to a previous employee; every
new starter gets a fresh, uniquely named identity. If the start date
moves or the offer is withdrawn, close the access ticket immediately so
no orphan account is created.

## Procedure

### Step 1: Receive and verify the access ticket

Confirm the access ticket from the hiring manager is complete: it must
name the new starter, the confirmed start date, the role, and the
manager. If any field is missing or the start date is fewer than three
working days away, return the ticket to the hiring manager rather than
proceeding, and record the reason on the ticket.

### Step 2: Create the directory account

Create the directory account using the naming convention in the
identity-management standard. Set an initial password that the new
starter will change on first login, and add the account to the role
groups that map to the standard application catalog for the confirmed
role. Do not add the account to any group outside the standard catalog
at this stage.

### Step 3: Enroll the endpoint

Image the assigned endpoint from the current golden image and join it
to the directory domain. Install the standard endpoint tooling
(endpoint detection and response, full-disk encryption, the corporate
VPN client). Verify the endpoint reports as compliant in the
management console before handing it over.

### Step 4: Assign application access

Grant the applications in the standard catalog for the role. For any
application outside the standard catalog requested on the ticket, route
the request to Information Security for consultation, and only grant it
once that consultation is recorded on the ticket with an approval.

### Step 5: Hand over and close

Email the new starter that the account is ready and the endpoint is
available for collection, with the first-login instructions. Notify the
hiring manager that provisioning is complete. Update the access ticket
with what was provisioned, close it, and record the completion date.

## Related Artifacts

### Requirements

- REQ-9687: Every new employee must be able to log in and send email on
  their first working day.

### Decisions

- DEC-2703: Adopt least-privilege role groups as the default access
  model.

### Goals

- GOL-0007: New employees reach full productive access on day one.

### Acceptance Criteria

- ACC-1234: The access ticket is closed within one working day of the
  start date.

### Sops

- SOP-0042: Offboarding and account de-provisioning.

## More Information

The standard application catalog and the role-to-group mapping are
maintained by the identity-management team and published on the IT
intranet. Provisioning metrics (ticket lead time, day-one readiness
rate) are reported monthly to the IT Operations Manager.

## Updates

### 2026-08-30 14:30:00.000+02:00 — Approved and activated

The procedure was approved by the IT Operations Manager and activated
as the standing reference for new-employee provisioning. It supersedes
the interim onboarding notes used since the start of the year.

```

**Tool: read_mcp_resource**

**Input:**

```json
{
  "server": "specmgr-test",
  "uri": "specmgr://rasci"
}
```

**Output:**

```
Resource: specmgr://rasci
MIME: text/markdown
# RASCI Responsibility Assignment

RASCI is a responsibility-assignment framework that names, for a given
piece of work, who does it, who owns it, who helps, who is consulted, and
who is kept informed. It is a variant of the better-known RACI matrix,
adding an explicit **S**upport role. Each role is defined by a single
responsibility, not by a person or job title: one person may carry
several roles across different pieces of work, and one role may be shared
by several people on a single piece of work.

## The five roles

- **Responsible** -- the people who do the work. There is at least one
  responsible party for every piece of work; the role may be shared by
  several people.
- **Accountable** -- the single owner who is ultimately answerable for the
  work being done and done correctly. There is exactly one accountable
  party; the work is not complete until the accountable party signs it
  off.
- **Support** -- the people who provide resources, tooling, or assistance
  to the responsible parties so the work can proceed. The role is
  distinct from Responsible: support parties help, they do not own the
  delivery of the work itself.
- **Consulted** -- the people whose opinions are sought before or during
  the work, typically subject-matter experts or downstream stakeholders.
  Consultation is two-way: their input is gathered and considered.
- **Informed** -- the people who are kept up to date on progress or
  outcomes. Communication is one-way: they receive information, they are
  not asked for input.

## RASCI vs. plain RACI

Plain RACI names four roles -- Responsible, Accountable, Consulted, and
Informed. RASCI adds the fifth, **S**upport, to make explicit who enables
the responsible parties (with tooling, access, expertise on tap, or
additional hands). The extra role is useful when the people who do the
work depend on others who are neither doing the work themselves nor
merely being consulted: treating those enablers as a separate Support
role keeps the Responsible list focused on delivery and the Consulted
list focused on input. A team that does not need that distinction can use
the framework as plain RACI by simply leaving the Support role empty.

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 168.1s)

_Thinking:_

Everything needed is in place. Note: In the RASCI example, the Support section is left empty (permitted: "Teams that don't need that distinction can use the framework as plain RACI by simply leaving the Support role empty" — but in our SOP, Support actually exists: script + CI + registry).

Interesting point: in the example, Support is empty with no bullet points — meaning the section permits zero entries. In our case, there are entries.

Now, let's draft the SOP. Key design points (from the approved plan):

**Title**: "Perform a release of biz.dfch.SpecMgr"

**Purpose**: To define the canonical procedure for releasing a new version of biz-dfch-specmgr from dev to PyPI (test+prod), TestPyPI, the MCP Registry, and GitHub Releases. To guarantee that every release passes the same gates (CI green on dev and on the PR, the ff-only invariant, changelog curation, verification of the publication), regardless of whether it is performed by a human manually or by an agent via the staged script.

**Scope**: Covers the version bump, CHANGELOG finalization, the commit to dev, the dev→main merge (PR + ff-only), version tagging, the publication workflow (4 jobs), and the GitHub Release notes. Out of scope: feature development, deciding the version bump type (that's a maintainer decision preceding the SOP), the hotfix/backport path (not yet defined — note for the future), publishing outside the v\* tag trigger.

**Definitions**:

- Release commit: exactly 3 files (pyproject.toml, uv.lock, CHANGELOG.md)
- ff-only invariant: main must always be an ancestor of dev (no unique commits on main) — what keeps future releases fast-forwardable
- Stages: the subcommands of scripts/release.sh, each mapping 1:1 to the Procedure steps
- /release: the OpenCode command that drives the stages with agent judgment inserted
- Publication jobs: the 4 jobs in publish.yml (TestPyPI, PyPI, GitHub Release, MCP Registry)
- [Unreleased] section: the keep-a-changelog staging area

**Roles and Responsibilities** (RASCI, per resource):

- Accountable: the repository maintainer (dfch) — ultimately responsible; signs off at the two gates (version confirmation, merge approval)
- Responsible: the release agent (an opencode session running the /release command) executes the stages; in manual mode the maintainer
- Support: scripts/release.sh (deterministic stages), GitHub Actions (ci.yml on dev and the PR, publish.yml on the tag), uv/gh CLI, the PyPI + TestPyPI + MCP Registry services
- Consulted: the maintainer at the gates (version number confirmation after resolve; go-ahead for the merge after pr-create)
- Informed: downstream users (via the GitHub Release notes + PyPI/MCP Registry listing)

**Safety and Precautions**:

- Pushing the tag is irreversible and immediately publishes to TestPyPI, PyPI, and the MCP Registry (trusted publishing; versions cannot be retracted, only superseded)
- Never create a merge commit or squash when merging dev into main — use ff-only; a unique commit on main breaks the invariant and future releases
- Never re-run the bump/commit-push stage against a version that is already in pyproject (double bump); if a stage fails, resume from the failed stage (idempotent status probe)
- An empty [Unreleased] is a stop condition — a release with nothing documented is nearly always a mistake
- The release commit must contain exactly 3 files; if the working tree has other changes, stop (a dirty tree means unfinished work is about to be mixed in)
- On CI failure: stop, diagnose, fix on dev, and re-run from the failed stage — never force-merge or skip checks
- Release only from a dev whose CI is green and which is in sync with origin

**Procedure** (9 steps, each step with an automated + manual path). Let's draft:

Step 1: Resolve and confirm the target version

- Input: a full semver X.Y.Z or a bump keyword (patch/minor/major)
- Automated: `scripts/release.sh resolve <arg>` outputs the computed version (keyword → semver arithmetic against the current pyproject version; e.g. 0.14.0 + minor → 0.15.0). The agent confirms the resolved number with the maintainer before anything mutates (a keyword on 0.x major → 1.0.0 deserves explicit confirmation).
- Manual: read `version` in pyproject.toml; apply the SemVer bump; note the target.
- Gate: maintainer confirms the target version.

Step 2: Run pre-checks

- Automated: `scripts/release.sh precheck` — verify: on dev with a clean tree in sync with origin/dev; origin/main is an ancestor of origin/dev (the ff-only invariant); the latest dev CI run is green; the tag vX.Y.Z does not exist locally or on origin; `uv lock --check` passes (the lock is in sync); uv and gh are available and authenticated. If any check fails, stop.
- Manual: run the README checklist... (git commands + gh run list + git merge-base --is-ancestor + uv lock --check)
- Stop conditions: any check failure; an empty [Unreleased] (the script warns/confirms).

Step 3: Curate the CHANGELOG's [Unreleased] section

- Automated: the agent (not the script) reviews the [Unreleased] entries against `git log <last-tag>..HEAD --oneline`, fills in missing items, rewrites entries into Keep-a-Changelog categories (Added/Changed/Deprecated/Removed/Fixed/Security), and shows the proposed dated section to the maintainer. This is the only step the agent performs directly on a file.
- Manual: edit the [Unreleased] section of CHANGELOG.md by hand, keeping Keep a Changelog format.
- The changelog must describe everything user-visible since the last tag.

Step 4: Bump the version and sync the lock

- Automated: `scripts/release.sh bump <X.Y.Z>` — update the version line in pyproject.toml (asserting there is exactly one match; refusing if the current version is already the target), run `uv lock`, and assert that the uv.lock diff is only the version line. Tolerates a dirty CHANGELOG.md from step 3.
- Manual: edit version in pyproject.toml; `uv lock`; confirm the uv.lock diff is version-only.

Step 5: Finalize the CHANGELOG and commit the release

- Automated: `scripts/release.sh changelog <X.Y.Z>` — mechanically move [Unreleased] to a new dated section `## [X.Y.Z] - YYYY-MM-DD` under an emptied `## [Unreleased]` (refusing if the section is empty). Then `scripts/release.sh commit-push <X.Y.Z>` — assert the working-tree changes are exactly {pyproject.toml, uv.lock, CHANGELOG.md}, commit as `chore(release): bump version to vX.Y.Z`, push to dev, wait for dev's CI run (poll every 30 s).
- Manual: move the section by hand (README convention); git add the 3 files; commit; push; watch CI.
- Stop condition: dev CI failure → fix on dev and re-run from the failed stage.

Step 6: Merge dev into main (PR, ff-only, with a merge gate)

- Automated: `scripts/release.sh pr-create <X.Y.Z>` — create (or resume) the dev→main PR with the new changelog section as the body, wait until the PR's checks are green (30 s), output the PR URL and head SHA, and stop without merging. The agent then shows the maintainer the PR and the changelog section and asks for go-ahead (the merge gate). With the maintainer's approval: `scripts/release.sh pr-merge <X.Y.Z>` — `gh pr merge --ff-only`. ff-only is mandatory: it moves main to dev's tip without adding a commit unique to main, preserving the ff-only invariant for the next release.
- Manual: gh pr create --base main --head dev; wait for checks; maintainer reviews; git checkout main && git merge --ff-only dev && git push origin main. (A plain `git merge dev` from main fast-forwards when the invariant holds; never use --no-ff or squash.)
- Stop condition: PR check failure, or the maintainer declines the merge.

Step 7: Tag the release and push

- Automated: `scripts/release.sh tag-push <X.Y.Z>` — checkout main, pull --ff-only (main is now == dev), create a lightweight tag vX.Y.Z on main's HEAD, push the tag, and switch back to dev.
- Manual: git checkout main && git pull --ff-only && git tag vX.Y.Z && git push origin vX.Y.Z && git checkout dev.
- Warning: pushing the tag immediately triggers the publication workflow — from here on it is irreversible.

Step 8: Wait for publication (4 jobs)

- Automated: `scripts/release.sh publish-wait <X.Y.Z>` — wait for the publish.yml run triggered by the tag: Publish to TestPyPI → Publish to PyPI → Make GitHub Release (attaching sdist+wheel) → Publish to MCP Registry (updating the server.json version via OIDC). Poll every 30 s; on job failure, report the run URL and stop (do not re-tag).
- Manual: watch the run in the Actions tab; check each of the 4 jobs.
- Stop condition: any job failure — diagnose via the run log; fixing and re-pushing a new tag is impossible (the tag already exists) — escalate to the maintainer (retraction/superseding release is the only remedy).

Step 9: Verify and finalize the GitHub Release notes

- Automated: `scripts/release.sh release-notes <X.Y.Z>` — verify the GitHub Release exists with the built artifacts (sdist + wheel), and set the release notes to the body of the new changelog section (`gh release edit`). Output the final summary: the version, the tag, the GH Release URL, the PyPI/TestPyPI project URLs, and the MCP Registry entry.
- Manual: confirm the release assets; edit the release body with the changelog section.
- Completion: all 4 publication targets reachable; the maintainer is informed. The SOP flips from draft→active after the first release performed under this SOP succeeds (recorded in Updates).

**Related Artifacts**:

- Requirements: none yet (hmm — the section probably needs at least something; the template shows a bullet list. In the example there are bullets under all subsections. Is an empty subsection allowed? The body schema — "each question/answer category holds zero or more" was for QA. For SOP, let's not guess: to be safe, put at least one bullet under each subsection, or check the body model. Let me quickly check the SOP body schema for which Related Artifacts subsections are required/optional.)
- Decisions: feat-30-sop ADR 36905d5b (dispatch-only generic tools — the convention the release command follows)... no, that's about the tools. Better: there's no DEC document in the repository. Use ADR references? The "Decisions" subsection says "DEC-0001: title" — the dec domain. There are no dec documents in the repo. Hmm. Let me check the body model for which subsections are optional.

Let me check the related-artifacts section of sop/models/v1/body.py to figure out the required/optional subsections.

I have the template, example, and RASCI guidance. Before drafting, checking which SOP body sections/subsections are mandatory vs optional:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"class \\|@alias\\|optional\\|Related\\|Heading\\|step\\|Step\" src/biz/dfch/specmgr/sop/models/v1/body.py | head -50"
}
```

**Output:**

```
28:`RelatedArtifacts`/`Updates` enforces markdown order (Purpose -> Scope ->
31:(-> Step 1: -> Step 2: -> ...) -> Related Artifacts (-> Requirements ->
55:class Purpose(MarkdownSection2):
62:class Scope(MarkdownSection2):
63:    """`## Scope` -- what this SOP covers (and, optionally, what it does not).
67:class Definitions(MarkdownSection2):
72:class Accountable(MarkdownSection3):
91:class Responsible(MarkdownSection3):
111:class Support(MarkdownSection3):
115:    An optional bullet list that MAY be present with zero list items (an
134:class Consulted(MarkdownSection3):
138:    An optional bullet list that MAY be present with zero list items (an
157:class Informed(MarkdownSection3):
161:    An optional bullet list that MAY be present with zero list items (an
180:@alias(value="Roles and Responsibilities", type=AliasType.LITERAL)
181:class RolesAndResponsibilities(MarkdownSection2):
186:    independently optional and MAY each be present with zero list items. See
218:@alias(value="Safety and Precautions", type=AliasType.LITERAL)
219:class SafetyAndPrecautions(MarkdownSection2):
223:    The class name `SafetyAndPrecautions` does not match the heading's wording
229:#: Matches a `### Step {N}: {name}` heading line as retained in a leaf
230:#: `MarkdownSection3`'s `.text` (first line), capturing the step number
231:#: (group 1) and its name (group 2). Mirrors `Step`'s own `@alias`, which
235:_STEP_HEADING_PATTERN = re.compile(r"### Step (\d+): (.+)")
238:@alias(value=r"^Step \d+: .+$", type=AliasType.REGEX)
239:class Step(MarkdownSection3):
240:    """`### Step {N}: {name}` under `## Procedure` -- one step of the procedure.
243:    itself (e.g. `### Step 1: Provision the account`), constrained by the
244:    regex `@alias` above and enforced by `match_alias` (`re.fullmatch`) at
245:    parse time -- a missing colon/title (`### Step 1`), a non-numeric number
246:    (`### Step one: X`), or a title-less heading (`### Step 1:`) all fail the
247:    parse eagerly. The number may carry leading zeros (`### Step 01: X`); it
248:    is normalized to an integer by the computed `number` below. Step numbers
257:        Computed. The step's number (e.g. `1` for `### Step 1: X`, also `1`
258:        for `### Step 01: X`). Never stored separately -- derived from the
261:        Computed. The step's name (the heading text after `": "`). Never
268:        """The step's number carried by this heading (e.g. `1` for `### Step 1: X`).
272:            (leading zeros accepted: `### Step 01: X` yields `1`).
276:                `Step`'s declared `@alias` (unreachable via the engine:
281:        assert match, f"Step: expected heading '### Step N: <name>', got {heading_line!r}"
288:        """The step's name carried by this heading (e.g. `X` for `### Step 1: X`).
296:                `Step`'s declared `@alias` (unreachable via the engine:
301:        assert match, f"Step: expected heading '### Step N: <name>', got {heading_line!r}"
306:class Procedure(MarkdownSection2):
307:    """`## Procedure` -- the structured, ordered set of steps a reader follows.
308:    Mandatory; present only if it carries at least one `### Step {N}: {name}`
309:    entry (``min_length=1``) -- an H2 with zero steps is a structural error.
313:    steps:
314:        The `### Step {N}: {name}` entries, in document order. Requires at
315:        least one step.

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 44.8s)

_Thinking:_

Let's check the `RelatedArtifacts` class and see which subsections are required:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"class RelatedArtifacts\" -A 40 src/biz/dfch/specmgr/sop/models/v1/body.py | head -55"
}
```

**Output:**

```
384:class RelatedArtifacts(MarkdownSection2):
385-    """`## Related Artifacts` -- container for five independent, all-optional
386-    `### ` cross-reference lists (requirements/decisions/goals/acceptance
387-    criteria/sops). Optional as a whole; no consistency check is enforced
388-    between the sub-lists. The `### Sops` sub-list is a self-cross-reference
389-    (a `sop` document may reference other, related/superseding SOPs).
390-    """
391-
392-    requirements: Requirements | None = Field(default=None, description="`### Requirements` sub-section. Optional.")
393-    decisions: Decisions | None = Field(default=None, description="`### Decisions` sub-section. Optional.")
394-    goals: Goals | None = Field(default=None, description="`### Goals` sub-section. Optional.")
395-    acceptance_criteria: AcceptanceCriteria | None = Field(
396-        default=None, description="`### Acceptance Criteria` sub-section. Optional."
397-    )
398-    sops: Sops | None = Field(default=None, description="`### Sops` sub-section (self-cross-reference). Optional.")
399-
400-
401-class MoreInformation(MarkdownSection2):
402-    """`## More Information` -- free-form optional supplementary text, no
403-    fixed format. Optional."""
404-
405-
406-#: Matches a `### {ISO8601 timestamp} — {title}` heading line as retained in a
407-#: composite `MarkdownSection3`'s `.text` (which carries the heading's inline
408-#: content without the `###` marker), capturing the timestamp (named group
409-#: `timestamp`) and the title (named group `title`). Mirrors `UpdateEntry`'s
410-#: own `@alias`, which sees the heading text without the `###` marker, and
411-#: DEC's `Option`/RSK's `Probability`/`Impact` computed-field precedent (the
412-#: value is carried by the heading and extracted at access time, never
413-#: stored). Unlike DEC's leaf `Option`, `UpdateEntry` is a *composite*
414-#: (it has a mandatory `content` paragraph), so its `.text` returns only the
415-#: heading text, not the full extent -- hence no `### ` prefix here.
416-_UPDATE_ENTRY_HEADING_PATTERN = re.compile(
417-    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})) — (?P<title>.+)"
418-)
419-
420-
421-@alias(value=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}) — .+$", type=AliasType.REGEX)
422-class UpdateEntry(MarkdownSection3):
423-    """`### {ISO8601 timestamp} — {title}` under `## Updates` -- one update entry.
424-

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 94.3s)

_Thinking:_

`## Related Artifacts` is entirely optional, and all five subsections are optional too. Therefore I can include just the subsections that have meaningful content (e.g., Decisions — hmm, but there are no DEC docs. Related stuff: ADRs? This subsection expects DEC-NNNN references. Since no DEC/REQ/GOL/AC docs exist in the repo, I could omit Related Artifacts entirely, or include just a "Sops" self-reference... actually, there's a more natural fit: this SOP relates to the repo's documented release process. The template/example shows the format, but the schema says optional. I'll include a Related Artifacts with just the subsections that have real content — for instance "Decisions": no DEC documents exist...

Hmm, wait — actually, is there anything? `specmgr_list_dec` — I can quickly check via the live server. If there are DEC documents (e.g., the decision on release automation!), I can reference them. In fact — the decision on release automation (SOP as canonical, staged scripts, PR + ff-only) could itself be recorded as a DEC document! That's a nice dogfooding move, but it's scope creep. The user asked for SOP + scripts + commands. The DEC recording was part of... no, it wasn't in the plan. Keep the scope: SOP only.

For Related Artifacts, the honest content available:

- Sops: none yet (this is the first SOP).
- Requirements/Goals/AC: none exist in the repo.
- Decisions: check whether any DEC documents exist.

Let me quickly list dec/req/gol via the live server to see what referenceable artifacts exist. If nothing exists, I'll either omit the whole `## Related Artifacts` section (per schema, optional) — or include it with a single "Sops" subsection? No — don't include empty subsections. Omit it entirely? The template includes it, but the schema says optional. Hmm, but for the sake of documentation completeness... I think it's cleaner to omit a section with no real references. No wait — there's one real cross-reference type: ADRs. But the SOP schema has no "ADRs" subsection (only req/dec/gol/ac/sops). So omit.

Updates section: `### {ISO8601 ms + tz} — {title}` format, e.g., `### 2026-08-31 15:00:00.000+02:00 — Created`. Note: em dash `—` between timestamp and title. Order: newest first? The SOP template has a single entry. The feat domain convention is newest first. For Updates, let me quickly check body.py... The RSK/DEC/feat `Updates` — feat is newest first. Let me quickly check the SOP Updates class for the order constraint.

Also: the `create_sop` tool derives the filename from the H1 title and assigns a UUID id. Status defaults to draft (I want draft — good).

Timestamp: I need the current time with ms + offset. Today: 2026-08-31, system tz is probably +02:00 (in earlier git output commits were +0200). Use `date +%Y-%m-%d\ %H:%M:%S.000%:z`... I'll just compute it with bash's date.

Let me check the Updates order + required subsections (Purpose/Scope/Definitions/RASCI/Safety/Procedure all required? From the body class: Purpose (H2, required per "markdown order is enforced: Purpose -> Scope -> ..."), Scope, Definitions, Roles, Safety, Procedure are required (Procedure has min_length=1 steps). Let me confirm Definitions is required and check the Updates order.

Checking two remaining schema details — mandatory sections and Updates ordering:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"class Definitions\\|class Updates\" -A 12 src/biz/dfch/specmgr/sop/models/v1/body.py | head -40; echo ===; grep -n \"class Sop\\|purpose:\\|scope:\\|definitions:\\|roles\\|safety\\|procedure:\\|related\\|more_info\\|updates:\" src/biz/dfch/specmgr/sop/models/v1/document.py | head -20"
}
```

**Output:**

```
67:class Definitions(MarkdownSection2):
68-    """`## Definitions` -- terms-of-art used by this SOP, defined for the
69-    reader. Optional, free-form prose."""
70-
71-
72-class Accountable(MarkdownSection3):
73-    """`### Accountable` under `## Roles and Responsibilities` -- the single
74-    owner who is ultimately answerable for the SOP.
75-
76-    A single mandatory paragraph (never a bullet list): exactly one owner,
77-    structurally discouraging multiple owners. See the general
78-    `specmgr://rasci` resource for RASCI role definitions.
79-
--
500:class Updates(MarkdownSection2):
501-    """`## Updates` -- a dynamic list of ISO8601-timestamped `### ` update
502-    entries. Optional as a whole, and the last section of the document if
503-    present.
504-
505-    Mirrors `tsk`/`dec`'s `Updates`/`RecentUpdates` container shape: no
506-    dedicated per-entry tools (no `option_create`/`option_list` equivalent)
507-    -- entries are appended by editing the whole body.
508-
509-    Parameters
510-    ----------
511-    updates:
512-        The dynamic collection of `### ` entries, in document order. Requires
===
42:class SopDocument(BaseModel):

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 46.3s)

_Thinking:_

Definitions is optional. Updates is optional, and if present, it must be the final section. Let's check the required fields of SopDocument:

**Tool: bash**

**Input:**

```json
{
  "command": "sed -n '42,80p' src/biz/dfch/specmgr/sop/models/v1/document.py"
}
```

**Output:**

```
class SopDocument(BaseModel):
    """A full Standard Operating Procedure document: YAML frontmatter and body.

    Attributes
    ----------
    frontmatter:
        The YAML frontmatter block. See :class:`SopFrontmatter`.
    body:
        The parsed SOP sections. See :class:`Sop`.
    """

    frontmatter: SopFrontmatter
    body: Sop

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 47.3s)

_Thinking:_

Let me quickly check the required fields of the `Sop` body model:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"class Sop\" -A 30 src/biz/dfch/specmgr/sop/models/v1/body.py | grep -E \"class Sop|: .*Field|= Field|default\" | head -15"
}
```

**Output:**

```
371:class Sops(MarkdownSection3):
377-    items: list[MarkdownListItem] = Field(
392-    requirements: Requirements | None = Field(default=None, description="`### Requirements` sub-section. Optional.")
393-    decisions: Decisions | None = Field(default=None, description="`### Decisions` sub-section. Optional.")
394-    goals: Goals | None = Field(default=None, description="`### Goals` sub-section. Optional.")
395-    acceptance_criteria: AcceptanceCriteria | None = Field(
396-        default=None, description="`### Acceptance Criteria` sub-section. Optional."
398-    sops: Sops | None = Field(default=None, description="`### Sops` sub-section (self-cross-reference). Optional.")
525:class Sop(MarkdownSection1):
554-    purpose: Purpose = Field(description="`## Purpose` section. Mandatory.")
555-    scope: Scope | None = Field(default=None, description="`## Scope` section. Optional.")

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 227.6s)

_Thinking:_

Sufficient information is available. Mandatory: only Purpose. Everything else is optional (but for a good SOP, include all the main sections). So, draft the SOP content and create it with `specmgr-test_create_sop`.

Title (H1): "Perform a release of biz.dfch.SpecMgr"

The content will consist of body only (create_sop takes body only and assigns id/frontmatter).

Timestamp for Updates: current time. Get it with bash `date`. The format requires `\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(Z|[+-]\d{2}:\d{2})`. Example: `2026-08-31 15:30:00.000+02:00`.

So, write the complete SOP. Keep the prose concise and precise. Each step: description + "**Automated (staged script):**" and "**Manual fallback:**" — wait, can I use bold sub-structure within a step's MarkdownSection3? Step is a MarkdownSection3, and the content is free markdown (leaf text + probably paragraphs). The step's content is probably free-form markdown (same as other sections). Bold lines are fine.

So, draft it:

______________________________________________________________________

# Perform a release of biz.dfch.SpecMgr

## Purpose

This procedure defines how a new version of `biz-dfch-specmgr` is released from the `dev` branch to TestPyPI, PyPI, the GitHub Release, and the MCP Registry. It exists so that every release — whether run by the release agent via the staged `scripts/release.sh` script or performed manually by the maintainer — passes the same gates (green CI on `dev` and on the merge PR, the fast-forward invariant between `main` and `dev`, curated changelog, verified publication) and produces an identical, reproducible outcome.

## Scope

This SOP covers: resolving the target version; pre-release checks; curating the `CHANGELOG.md` `[Unreleased]` section; bumping the version in `pyproject.toml` and syncing `uv.lock`; committing and pushing the release to `dev`; merging `dev` into `main` via a fast-forward-only PR; creating and pushing the `vX.Y.Z` tag on `main`; waiting for the four publication jobs in `.github/workflows/publish.yml`; and setting the GitHub Release notes.

Out of scope: deciding whether a change warrants patch/minor/major (that is a maintainer decision made before this SOP is invoked); the hotfix/backport path (no such path is defined yet — if one is needed, it is handled as an exception and recorded under Updates); anything the `publish.yml` workflow does internally (trusted-publishing credentials, `server.json` generation).

## Definitions

- **Release commit**: a single commit on `dev` touching exactly three files — `pyproject.toml`, `uv.lock`, `CHANGELOG.md` — with the message `chore(release): bump version to vX.Y.Z`.
- **Fast-forward invariant**: `main` is always an ancestor of `dev`, i.e., `main` has no unique commits. This invariant is what allows `dev` → `main` to be merged fast-forward-only, and must hold before every release.
- **Stage**: a subcommand of `scripts/release.sh` (e.g., `precheck`, `bump`, `pr-merge`). Stages mirror the steps of this procedure one-to-one, are idempotent (a completed stage reports done and does not re-execute), and are the only sanctioned way for the agent to perform release mechanics.
- **`/release`**: the OpenCode command (`.opencode/command/release.md`) that drives the stages with the agent-judgment steps of this SOP (version confirmation, changelog curation, merge gate, failure triage).
- **Publication jobs**: the four jobs of `.github/workflows/publish.yml`, triggered by pushing a `v*` tag: *Publish to TestPyPI* → *Publish to PyPI* → *Make GitHub Release* → *Publish to MCP Registry*.
- **`[Unreleased]` section**: the Keep a Changelog staging area at the top of `CHANGELOG.md` that accumulates noteworthy changes between releases.
- **Merge gate**: the maintainer's explicit go-ahead to merge the release PR after the agent has presented it (step 6).

## Roles and Responsibilities

### Accountable

The repository maintainer (`dfch`) is accountable for every release and for the continued validity of this procedure: they make the version decision, confirm the resolved version number (step 1), approve the merge gate (step 6), and sign off on any exception.

### Responsible

- The release agent (the OpenCode session executing `/release`) runs the stages in order, performs the changelog curation (step 3), and reports progress and failures. In manual mode, the maintainer performs all steps themselves.

### Support

- `scripts/release.sh` — the deterministic stage implementations (prechecks, edits, git/gh mechanics, CI polling).
- GitHub Actions — `ci.yml` (lint/tests/docs-drift on `dev` and on the PR) and `publish.yml` (the four publication jobs).
- The `uv` and `gh` CLIs, and the external publication targets: TestPyPI, PyPI (both via OIDC trusted publishing), and the MCP Registry (via `mcp-publisher` OIDC).

### Consulted

- The maintainer is consulted at exactly two gates: the version confirmation after `resolve` (step 1) and the merge gate after `pr-create` (step 6).

### Informed

- Downstream consumers are informed via the GitHub Release (notes + sdist/wheel artifacts), the PyPI/TestPyPI project pages, and the MCP Registry listing.

## Safety and Precautions

- **Pushing the tag is irreversible.** It immediately starts publication to TestPyPI, PyPI, and the MCP Registry. A published version cannot be retracted, only superseded by a newer one. Never push a tag whose preconditions (steps 1–5) have not all succeeded.
- **Merge only fast-forward.** Never create a merge commit or squash merge when merging `dev` into `main` — a unique commit on `main` breaks the fast-forward invariant and poisons every subsequent release. The script enforces this with `--ff-only`; in manual mode use `git merge --ff-only dev`.
- **Never double-bump.** If `pyproject.toml` already carries the target version, the `bump` stage refuses to run. If a stage failed mid-release, resume from the failed stage (each stage is idempotent; `scripts/release.sh status <version>` shows where you are) — do not restart the flow from scratch.
- **An empty `[Unreleased]` section is a stop condition.** A release that documents nothing is nearly always a mistake; the `changelog` stage refuses to proceed without confirmation (and fails outright in non-interactive mode).
- **The release commit is exactly three files.** Any other pending change in the working tree means unshipped work will be mixed into the release; the precheck and `commit-push` stages assert the tree state and stop otherwise.
- **CI failures stop the release.** A red build on `dev` or on the release PR is never force-merged or skipped: diagnose, fix on `dev`, and resume from the failed stage.

## Procedure

### Step 1: Resolve and confirm the target version

Start from the maintainer's decision: a full semver string (`0.15.0`) or a bump keyword (`patch`/`minor`/`major`).

**Automated:** `scripts/release.sh resolve <argument>` computes the target version (the keyword is applied to the current `pyproject.toml` version via SemVer; e.g., `0.14.0` + `minor` → `0.15.0`) and prints it, mutating nothing. The agent then confirms the resolved number with the maintainer before anything else runs — a keyword that produces a surprising number (e.g., `major` on a `0.x` version → `1.0.0`) must be explicitly acknowledged.

**Manual fallback:** read the `version` field of `pyproject.toml`, apply the SemVer bump by hand, and record the target version.

### Step 2: Run the pre-release checks

**Automated:** `scripts/release.sh precheck` — verifies, in order: (a) the checkout is on `dev` with a clean tree in sync with `origin/dev`; (b) `origin/main` is an ancestor of `origin/dev` (fast-forward invariant); (c) the most recent CI run on `dev` is green (waits for an in-flight run, polling every 30 s); (d) the tag `vX.Y.Z` exists neither locally nor on `origin`; (e) `uv lock --check` passes, i.e., `uv.lock` is in sync with `pyproject.toml` before the bump; (f) the `uv` and `gh` CLIs are present and `gh` is authenticated. Any failure stops the release with a diagnostic.

**Manual fallback:** run the individual checks by hand: `git status`, `git fetch && git merge-base --is-ancestor origin/main origin/dev`, `gh run list --branch dev --limit 1`, `git tag -l vX.Y.Z` and `git ls-remote --tags origin vX.Y.Z`, `uv lock --check`, `gh auth status`.

### Step 3: Curate the changelog

Bring the `[Unreleased]` section of `CHANGELOG.md` into a state that fully describes everything user-visible since the last tag, organized under Keep a Changelog categories (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`).

**Automated:** the agent (not the script) performs this step. It diffs `git log <last-tag>..HEAD --oneline` against the existing `[Unreleased]` entries, adds missing items, rewords verbose or internal-facing entries into user-facing prose, and presents the finished section to the maintainer for review. This is the only step in which the agent edits a file directly.

**Manual fallback:** edit the `[Unreleased]` section by hand, using the same standard.

### Step 4: Bump the version and sync the lockfile

**Automated:** `scripts/release.sh bump <X.Y.Z>` — sets `version` in `pyproject.toml` (asserts there is exactly one version line, and refuses if the current version already equals the target), runs `uv lock`, and asserts the resulting `uv.lock` diff is only the version line. This stage tolerates the dirty `CHANGELOG.md` left by step 3.

**Manual fallback:** edit the `version` field of `pyproject.toml` to `X.Y.Z`; run `uv lock`; confirm via `git diff uv.lock` that only the `biz-dfch-specmgr` version entry changed.

### Step 5: Finalize the changelog, commit, push, and wait for CI

**Automated:** `scripts/release.sh changelog <X.Y.Z>` mechanically moves the `[Unreleased]` content into a new dated section `## [X.Y.Z] - YYYY-MM-DD` directly below a re-emptied `## [Unreleased]` header (refusing an empty section — see Safety). Then `scripts/release.sh commit-push <X.Y.Z>` asserts that the working-tree changes are exactly the three release files, commits them as `chore(release): bump version to vX.Y.Z`, pushes `dev`, and waits for the push-triggered CI run (lint/tests/docs-drift matrix), polling every 30 s.

**Manual fallback:** move the section by hand (Keep a Changelog convention, no comparison link reference in this repository); `git add pyproject.toml uv.lock CHANGELOG.md`; commit with the conventional message; `git push origin dev`; watch the Actions run until green.

A red build here stops the release: fix on `dev` and resume from the failed stage.

### Step 6: Merge `dev` into `main` (PR, fast-forward-only, with merge gate)

**Automated:** `scripts/release.sh pr-create <X.Y.Z>` creates — or resumes — the `dev` → `main` pull request, using the new dated changelog section as the PR body, waits until the PR's checks are green (30 s polling), and prints the PR URL and head SHA — without merging. The agent then presents the PR and the changelog section to the maintainer and asks for the merge gate. Upon approval, `scripts/release.sh pr-merge <X.Y.Z>` executes `gh pr merge --ff-only`.

**Manual fallback:** `gh pr create --base main --head dev` (body: the new changelog section); wait for green checks; present to the maintainer; on approval, `git checkout main && git merge --ff-only dev && git push origin main`. Never use `--no-ff`, squash, or rebase-merge.

### Step 7: Tag the release and push the tag

**Automated:** `scripts/release.sh tag-push <X.Y.Z>` — checks out `main`, `git pull --ff-only` (main now equals dev), creates the lightweight tag `vX.Y.Z` at `main`'s HEAD, pushes the tag, and switches back to `dev`.

**Manual fallback:** `git checkout main && git pull --ff-only && git tag vX.Y.Z && git push origin vX.Y.Z && git checkout dev`.

Warning: pushing the tag immediately starts publication (step 8). From here on the release is irreversible.

### Step 8: Wait for the publication jobs

**Automated:** `scripts/release.sh publish-wait <X.Y.Z>` waits for the `publish.yml` run triggered by the tag — *Publish to TestPyPI* → *Publish to PyPI* → *Make GitHub Release* (attaches sdist + wheel) → *Publish to MCP Registry* (updates `server.json` and publishes via OIDC) — polling every 30 s until all four jobs complete.

**Manual fallback:** watch the Actions run of `publish.yml` for the tag until all four jobs are green.

Any job failure stops the release: report the run URL, diagnose from the logs, and escalate to the maintainer. The tag already exists, so the remedy is never a re-tag; it is a fix plus a new (higher) version.

### Step 9: Verify the publication and finalize the release notes

**Automated:** `scripts/release.sh release-notes <X.Y.Z>` — verifies that the GitHub Release exists and has both artifacts (sdist and wheel), sets the release notes to the body of the new dated changelog section (`gh release edit`), and prints the final summary: version, tag, GitHub Release URL, PyPI and TestPyPI project URLs, and the MCP Registry listing.

**Manual fallback:** open the GitHub Release, confirm the two assets are present, and paste the new changelog section into the release body.

The release is complete when all four publication targets are reachable and the maintainer has been informed.

## More Information

The staged script and the `/release` command are projections of this SOP: the SOP is the normative procedure, and if the two ever disagree, the SOP wins and the script/command must be corrected. Stages are named to mirror the step numbers (step N ≈ stage N), which makes drift visible.

The specmgr MCP server running the `sop` tooling for this document is this repository itself (see the `specmgr-test` server entry in the opencode configuration); prior to the first release that ships the `sop` domain, the SOP is created/validated directly against the local tree.

## Updates

### <timestamp> — Created

Created as the normative procedure for releasing `biz-dfch-specmgr`, consolidating the previously hand-run README "Make a Release" steps (direct merge + tag) with the new automation: the staged `scripts/release.sh`, the `/release` OpenCode command with agent-judgment steps (version confirmation, changelog curation, merge gate, failure triage), and the PR + fast-forward-only merge strategy that keeps `main` a strict ancestor of `dev`. Status is `draft`; it will be activated after the first release executed under this SOP completes successfully (planned as v0.15.0, the first release to carry the `sop` domain itself).

______________________________________________________________________

Wait — one issue: "Related Artifacts" — I omitted it. That's allowed (optional as a whole). But hmm, should I include it? There are no REQ/DEC/GOL/AC documents in the repository (let's not bother checking; even if DEC documents existed, the only relevant one would be the release-automation decision, which we haven't written as a DEC). Omitting is the honest choice. Actually — wait, let me reconsider: the ADRs are related (e369ee2e for .specmgr? no…). The SOP schema has no ADR subsection, and forcing ADRs into "Decisions" would be a lie (those are DEC references). Omit. OK.

Another check — step heading format: `### Step 1: name` matches the regex `^Step \d+: .+$`. My headings: "### Step 1: Resolve and confirm the target version" ✓.

Updates entry heading: `### 2026-08-31 15:45:00.000+02:00 — Created` — must use em-dash `—` with spaces, and milliseconds `.000` ✓.

Bold + paragraphs within steps: Step is a MarkdownSection3 with free content — should be fine (the example step has only paragraphs; my steps have bold lead-in lines + paragraphs. Bold is inline, so OK).

Another consideration: create_sop takes body only — no frontmatter. The tool assigns id + frontmatter (status defaults to draft).

Timestamp: get the current time. The system date shows commits with +0200 offset. Use `date "+%Y-%m-%d %H:%M:%S.000%:z"` — hmm, `date`'s `%:z` gives +02:00. Let me get it first.

Also, the SOP mentions "planned as v0.15.0" — a nice forward reference.

So: get the timestamp, then create the SOP.

Schema confirmed (only `Purpose` is mandatory; `Related Artifacts` is optional as a whole, so since there are no referenceable REQ/DEC/GOL/AC documents in the repository, it will be omitted). Fetching the timestamp for the Updates entry and creating the SOP:

**Tool: bash**

**Input:**

```json
{
  "command": "date \"+%Y-%m-%d %H:%M:%S.000%:z\""
}
```

**Output:**

```
2026-08-31 15:19:05.000+02:00

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 148.7s)

_Thinking:_

Now creating the SOP with specmgr-test_create_sop (body only — the tool assigns the id and frontmatter, and the status defaults to draft).

**Tool: invalid**

**Input:**

```json
{
  "tool": "specmgr_create_sop",
  "error": "Model tried to call unavailable tool 'specmgr_create_sop'. Available tools: asdste100_rules_by_category, asdste100_rules_by_section, asdste100_rules_examples, asdste100_rules_find, asdste100_rules_match, asdste100_rules_overview, asdste100_rules_search, asdste100_rules_toc, asdste100_word_count, asdste100_word_find, asdste100_word_find_many, asdste100_word_fuzzy, asdste100_word_list, asdste100_word_match, asdste100_word_synonym, bash, edit, glob, grep, invalid, list_mcp_resource_templates, list_mcp_resources, question, read, read_mcp_resource, skill, specmgr-test_create_adr, specmgr-test_create_dec, specmgr-test_create_feat, specmgr-test_create_gol, specmgr-test_create_prb, specmgr-test_create_qa, specmgr-test_create_req, specmgr-test_create_rsk, specmgr-test_create_sop, specmgr-test_create_tsk, specmgr-test_create_uc, specmgr-test_delete_dec, specmgr-test_delete_feat, specmgr-test_delete_gol, specmgr-test_delete_prb, specmgr-test_delete_qa, specmgr-test_delete_req, specmgr-test_delete_rsk, specmgr-test_delete_sop, specmgr-test_delete_tsk, specmgr-test_delete_uc, specmgr-test_get_adr, specmgr-test_get_dec, specmgr-test_get_dec_example, specmgr-test_get_dec_template, specmgr-test_get_feat, specmgr-test_get_feat_example, specmgr-test_get_feat_template, specmgr-test_get_gol, specmgr-test_get_gol_example, specmgr-test_get_gol_template, specmgr-test_get_prb, specmgr-test_get_prb_example, specmgr-test_get_prb_template, specmgr-test_get_qa, specmgr-test_get_qa_example, specmgr-test_get_qa_template, specmgr-test_get_req, specmgr-test_get_req_example, specmgr-test_get_req_template, specmgr-test_get_rsk, specmgr-test_get_rsk_example, specmgr-test_get_rsk_template, specmgr-test_get_sop, specmgr-test_get_sop_example, specmgr-test_get_sop_template, specmgr-test_get_tsk, specmgr-test_get_tsk_example, specmgr-test_get_tsk_template, specmgr-test_get_uc, specmgr-test_get_uc_example, specmgr-test_get_uc_template, specmgr-test_list_adr, specmgr-test_list_dec, specmgr-test_list_feat, specmgr-test_list_gol, specmgr-test_list_prb, specmgr-test_list_qa, specmgr-test_list_req, specmgr-test_list_rsk, specmgr-test_list_sop, specmgr-test_list_tsk, specmgr-test_list_uc, specmgr-test_mdformat, specmgr-test_option_create, specmgr-test_option_delete, specmgr-test_option_list, specmgr-test_option_read, specmgr-test_option_update, specmgr-test_parse_dec, specmgr-test_parse_feat, specmgr-test_parse_gol, specmgr-test_parse_prb, specmgr-test_parse_qa, specmgr-test_parse_req, specmgr-test_parse_rsk, specmgr-test_parse_sop, specmgr-test_parse_tsk, specmgr-test_parse_uc, specmgr-test_set_status, specmgr-test_update, specmgr-test_update_frontmatter, specmgr-test_update_section, specmgr-test_validate_adr, specmgr-test_validate_dec, specmgr-test_validate_feat, specmgr-test_validate_gol, specmgr-test_validate_prb, specmgr-test_validate_qa, specmgr-test_validate_req, specmgr-test_validate_rsk, specmgr-test_validate_sop, specmgr-test_validate_tsk, specmgr-test_validate_uc, specmgr-test_webfetch, task, todowrite, webfetch, write."
}
```

**Output:**

```
The arguments provided to the tool are invalid: Model tried to call unavailable tool 'specmgr_create_sop'. Available tools: asdste100_rules_by_category, asdste100_rules_by_section, asdste100_rules_examples, asdste100_rules_find, asdste100_rules_match, asdste100_rules_overview, asdste100_rules_search, asdste100_rules_toc, asdste100_word_count, asdste100_word_find, asdste100_word_find_many, asdste100_word_fuzzy, asdste100_word_list, asdste100_word_match, asdste100_word_synonym, bash, edit, glob, grep, invalid, list_mcp_resource_templates, list_mcp_resources, question, read, read_mcp_resource, skill, specmgr-test_create_adr, specmgr-test_create_dec, specmgr-test_create_feat, specmgr-test_create_gol, specmgr-test_create_prb, specmgr-test_create_qa, specmgr-test_create_req, specmgr-test_create_rsk, specmgr-test_create_sop, specmgr-test_create_tsk, specmgr-test_create_uc, specmgr-test_delete_dec, specmgr-test_delete_feat, specmgr-test_delete_gol, specmgr-test_delete_prb, specmgr-test_delete_qa, specmgr-test_delete_req, specmgr-test_delete_rsk, specmgr-test_delete_sop, specmgr-test_delete_tsk, specmgr-test_delete_uc, specmgr-test_get_adr, specmgr-test_get_dec, specmgr-test_get_dec_example, specmgr-test_get_dec_template, specmgr-test_get_feat, specmgr-test_get_feat_example, specmgr-test_get_feat_template, specmgr-test_get_gol, specmgr-test_get_gol_example, specmgr-test_get_gol_template, specmgr-test_get_prb, specmgr-test_get_prb_example, specmgr-test_get_prb_template, specmgr-test_get_qa, specmgr-test_get_qa_example, specmgr-test_get_qa_template, specmgr-test_get_req, specmgr-test_get_req_example, specmgr-test_get_req_template, specmgr-test_get_rsk, specmgr-test_get_rsk_example, specmgr-test_get_rsk_template, specmgr-test_get_sop, specmgr-test_get_sop_example, specmgr-test_get_sop_template, specmgr-test_get_tsk, specmgr-test_get_tsk_example, specmgr-test_get_tsk_template, specmgr-test_get_uc, specmgr-test_get_uc_example, specmgr-test_get_uc_template, specmgr-test_list_adr, specmgr-test_list_dec, specmgr-test_list_feat, specmgr-test_list_gol, specmgr-test_list_prb, specmgr-test_list_qa, specmgr-test_list_req, specmgr-test_list_rsk, specmgr-test_list_sop, specmgr-test_list_tsk, specmgr-test_list_uc, specmgr-test_mdformat, specmgr-test_option_create, specmgr-test_option_delete, specmgr-test_option_list, specmgr-test_option_read, specmgr-test_option_update, specmgr-test_parse_dec, specmgr-test_parse_feat, specmgr-test_parse_gol, specmgr-test_parse_prb, specmgr-test_parse_qa, specmgr-test_parse_req, specmgr-test_parse_rsk, specmgr-test_parse_sop, specmgr-test_parse_tsk, specmgr-test_parse_uc, specmgr-test_set_status, specmgr-test_update, specmgr-test_update_frontmatter, specmgr-test_update_section, specmgr-test_validate_adr, specmgr-test_validate_dec, specmgr-test_validate_feat, specmgr-test_validate_gol, specmgr-test_validate_prb, specmgr-test_validate_qa, specmgr-test_validate_req, specmgr-test_validate_rsk, specmgr-test_validate_sop, specmgr-test_validate_tsk, specmgr-test_validate_uc, specmgr-test_webfetch, task, todowrite, webfetch, write.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 161.1s)

_Thinking:_

The tool name is `specmgr-test_create_sop` (server name prefix with hyphen), not `specmgr_create_sop`. Retrying with the correct name.

Wrong tool prefix — it's `specmgr-test_create_sop`:

**Tool: specmgr-test_create_sop**

**Input:**

```json
{
  "content": "# Perform a release of biz.dfch.SpecMgr\n\n## Purpose\n\nThis procedure defines how a new version of `biz-dfch-specmgr` is released\nfrom the `dev` branch to TestPyPI, PyPI, a GitHub Release, and the MCP\nRegistry. It exists so that every release — whether driven by the release\nagent through the staged `scripts/release.sh` script or performed manually\nby the maintainer — passes the same gates (green CI on `dev` and on the\nmerge pull request, the fast-forward invariant between `main` and `dev`, a\ncurated changelog, and a verified publication) and produces the same\nreproducible outcome.\n\n## Scope\n\nThis SOP covers: resolving the target version; pre-release checks;\ncurating the `CHANGELOG.md` `[Unreleased]` section; bumping the version in\n`pyproject.toml` and syncing `uv.lock`; committing and pushing the release\nto `dev`; merging `dev` into `main` through a fast-forward-only pull\nrequest; creating and pushing the `vX.Y.Z` tag on `main`; waiting for the\nfour publication jobs of `.github/workflows/publish.yml`; and setting the\nGitHub Release notes.\n\nIt does not cover: deciding whether the changes warrant a patch, minor, or\nmajor version (a maintainer decision made before this SOP is invoked); the\nhotfix/backport path (no such path is defined yet — should one ever be\nneeded, it is an exception to this SOP and must be recorded in its\n`Updates`); and the internals of the `publish.yml` workflow (OIDC trusted\npublishing, `server.json` generation).\n\n## Definitions\n\n- **Release commit**: the single commit on `dev` touching exactly three\n  files — `pyproject.toml`, `uv.lock`, `CHANGELOG.md` — with the message\n  `chore(release): bump version to vX.Y.Z`.\n- **Fast-forward invariant**: `main` is always an ancestor of `dev`, i.e.\n  `main` carries no unique commits. The invariant is what makes the\n  `dev` → `main` merge possible in fast-forward-only form, and it must\n  hold before every release.\n- **Stage**: a subcommand of `scripts/release.sh` (e.g. `precheck`,\n  `bump`, `pr-merge`). Stages mirror the steps of this procedure one-to-\n  one, are idempotent (a completed stage reports \"done\" instead of\n  re-running), and are the only sanctioned way for the agent to perform\n  release mechanics.\n- **`/release`**: the OpenCode command (`.opencode/command/release.md`)\n  that drives the stages and performs this SOP's agent-judgment steps\n  (version confirmation, changelog curation, merge gate, failure triage).\n- **Publication jobs**: the four jobs of\n  `.github/workflows/publish.yml`, triggered by pushing a `v*` tag:\n  *Publish to TestPyPI* → *Publish to PyPI* → *Make GitHub Release* →\n  *Publish to MCP Registry*.\n- **`[Unreleased]` section**: the Keep a Changelog staging area at the top\n  of `CHANGELOG.md` that accumulates notable changes between releases.\n- **Merge gate**: the maintainer's explicit go-ahead to merge the release\n  pull request, given after the agent presents it (Step 6).\n\n## Roles and Responsibilities\n\n### Accountable\n\nThe repository maintainer (`dfch`) is accountable for every release and\nfor the continued validity of this procedure: they make the version\ndecision, confirm the resolved version number (Step 1), approve the merge\ngate (Step 6), and adjudicate any exception.\n\n### Responsible\n\n- The release agent (the OpenCode session executing `/release`) runs the\n  stages in order, performs the changelog curation (Step 3), and reports\n  progress and failures. In manual mode the maintainer performs every\n  step themselves.\n\n### Support\n\n- `scripts/release.sh` — the deterministic stage implementations\n  (pre-checks, file edits, git/gh mechanics, CI polling).\n- GitHub Actions — `ci.yml` (lint, tests, and docs-drift checks on `dev`\n  and on the pull request) and `publish.yml` (the four publication jobs).\n- The `uv` and `gh` CLIs, and the external publication targets: TestPyPI\n  and PyPI (both via OIDC trusted publishing) and the MCP Registry (via\n  `mcp-publisher` with GitHub OIDC).\n\n### Consulted\n\n- The maintainer is consulted at exactly two gates: the version\n  confirmation after `resolve` (Step 1) and the merge gate after\n  `pr-create` (Step 6).\n\n### Informed\n\n- Downstream consumers are informed via the GitHub Release (notes plus\n  sdist/wheel artifacts), the PyPI and TestPyPI project pages, and the MCP\n  Registry listing.\n\n## Safety and Precautions\n\n- **Tag push is irreversible.** Pushing the tag immediately starts\n  publication to TestPyPI, PyPI, and the MCP Registry. A published version\n  cannot be retracted, only superseded by a newer one. Never push a tag\n  whose preconditions (Steps 1–5) have not all succeeded.\n- **Merge fast-forward only.** Never create a merge commit or squash-merge\n  when merging `dev` into `main` — a commit unique to `main` breaks the\n  fast-forward invariant and poisons every later release. The script\n  enforces this with `gh pr merge --ff-only`; manual mode uses\n  `git merge --ff-only dev`.\n- **Never double-bump.** If `pyproject.toml` already carries the target\n  version, the `bump` stage refuses to run. If a stage failed mid-release,\n  resume from the failed stage — every stage is idempotent, and\n  `scripts/release.sh status <version>` shows where the release stands —\n  rather than restarting the flow from scratch.\n- **An empty `[Unreleased]` section is a stop condition.** A release that\n  documents nothing is almost always a mistake; the `changelog` stage\n  refuses to proceed without explicit confirmation (and fails outright in\n  non-interactive mode).\n- **The release commit is exactly three files.** Any other pending change\n  in the working tree means unfinished work would be mixed into the\n  release; the pre-check and `commit-push` stages assert the tree state\n  and stop otherwise.\n- **CI failures stop the release.** A red build on `dev` or on the release\n  pull request is never force-merged or skipped: diagnose, fix on `dev`,\n  and resume from the failed stage.\n\n## Procedure\n\n### Step 1: Resolve and confirm the target version\n\nStart from the maintainer's decision: either a full semantic version\n(`0.15.0`) or a bump keyword (`patch`/`minor`/`major`).\n\n**Automated:** `scripts/release.sh resolve <arg>` computes the target\nversion — the keyword is applied to the current `pyproject.toml` version\nper SemVer (e.g. `0.14.0` + `minor` → `0.15.0`) — and prints it without\nmutating anything. The agent then confirms the resolved number with the\nmaintainer before anything else runs; a keyword that produces a\nsurprising number (e.g. `major` on a `0.x` version → `1.0.0`) must be\nexplicitly acknowledged.\n\n**Manual fallback:** read the `version` field of `pyproject.toml`, apply\nthe SemVer bump by hand, and record the target version.\n\n### Step 2: Run the pre-release checks\n\n**Automated:** `scripts/release.sh precheck` verifies, in order: (a) the\ncheckout is on `dev` with a clean tree in sync with `origin/dev`; (b)\n`origin/main` is an ancestor of `origin/dev` (the fast-forward\ninvariant); (c) the latest CI run on `dev` is green (waiting for an\nin-flight run, polling every 30 s); (d) the tag `vX.Y.Z` exists neither\nlocally nor on `origin`; (e) `uv lock --check` passes, i.e. `uv.lock` is\nin sync with `pyproject.toml` before the bump; (f) the `uv` and `gh` CLIs\nare present and `gh` is authenticated. Any failure stops the release with\na diagnostic.\n\n**Manual fallback:** run the checks individually: `git status`;\n`git fetch && git merge-base --is-ancestor origin/main origin/dev`;\n`gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and\n`git ls-remote --tags origin vX.Y.Z`; `uv lock --check`;\n`gh auth status`.\n\n### Step 3: Curate the changelog\n\nBring the `[Unreleased]` section of `CHANGELOG.md` to the point where it\nfully describes everything user-visible since the last tag, organized\nunder Keep a Changelog categories (`Added`, `Changed`, `Deprecated`,\n`Removed`, `Fixed`, `Security`).\n\n**Automated:** the agent (not the script) performs this step. It diffs\n`git log <last-tag>..HEAD --oneline` against the existing `[Unreleased]`\nentries, adds missing items, rewrites internal or verbose entries into\nuser-facing prose, and presents the finished section to the maintainer for\nreview. This is the only step in which the agent edits a file directly.\n\n**Manual fallback:** edit the `[Unreleased]` section by hand to the same\nstandard.\n\n### Step 4: Bump the version and sync the lockfile\n\n**Automated:** `scripts/release.sh bump <X.Y.Z>` sets the `version` field\nof `pyproject.toml` (asserting exactly one version line exists, and\nrefusing if the current version already equals the target), runs\n`uv lock`, and asserts the resulting `uv.lock` diff is only the version\nline. The stage tolerates the dirty `CHANGELOG.md` left by Step 3.\n\n**Manual fallback:** edit the `version` field of `pyproject.toml` to\n`X.Y.Z`; run `uv lock`; verify via `git diff uv.lock` that only the\n`biz-dfch-specmgr` version entry changed.\n\n### Step 5: Finalize the changelog, commit, push, and wait for CI\n\n**Automated:** `scripts/release.sh changelog <X.Y.Z>` mechanically moves\nthe `[Unreleased]` content into a new dated section\n`## [X.Y.Z] - YYYY-MM-DD` directly under a re-emptied `## [Unreleased]`\nheader (refusing an empty section — see Safety and Precautions). Then\n`scripts/release.sh commit-push <X.Y.Z>` asserts the working-tree changes\nare exactly the three release files, commits them as\n`chore(release): bump version to vX.Y.Z`, pushes `dev`, and waits for the\npush-triggered CI run (the lint/tests/docs-drift matrix), polling every\n30 s.\n\n**Manual fallback:** move the section by hand (this repo uses no compare-\nlink references in the changelog); `git add pyproject.toml uv.lock\nCHANGELOG.md`; commit with the conventional message; `git push origin\ndev`; watch the Actions run until green.\n\nA red build stops the release: fix on `dev` and resume from the failed\nstage.\n\n### Step 6: Merge `dev` into `main` (pull request, fast-forward only, with merge gate)\n\n**Automated:** `scripts/release.sh pr-create <X.Y.Z>` creates — or resumes\n— the `dev` → `main` pull request with the new dated changelog section as\nthe pull request body, waits until the pull request's checks are green\n(30 s polling), and prints the pull request URL and head SHA — without\nmerging. The agent then presents the pull request and the changelog\nsection to the maintainer and asks for the merge gate. Once approved,\n`scripts/release.sh pr-merge <X.Y.Z>` performs\n`gh pr merge --ff-only`.\n\n**Manual fallback:** `gh pr create --base main --head dev` (body: the new\nchangelog section); wait for green checks; present to the maintainer; on\napproval, `git checkout main && git merge --ff-only dev && git push origin\nmain`. Never use `--no-ff`, squash, or rebase merges.\n\n### Step 7: Tag the release and push the tag\n\n**Automated:** `scripts/release.sh tag-push <X.Y.Z>` checks out `main`,\nruns `git pull --ff-only` (main now equals dev), creates the lightweight\ntag `vX.Y.Z` at `main`'s HEAD, pushes the tag, and switches back to\n`dev`.\n\n**Manual fallback:** `git checkout main && git pull --ff-only && git tag\nvX.Y.Z && git push origin vX.Y.Z && git checkout dev`.\n\nWarning: pushing the tag immediately starts publication (Step 8); the\nrelease is irreversible from here.\n\n### Step 8: Wait for the publication jobs\n\n**Automated:** `scripts/release.sh publish-wait <X.Y.Z>` waits for the\n`publish.yml` run triggered by the tag — *Publish to TestPyPI* →\n*Publish to PyPI* → *Make GitHub Release* (attaches the sdist and wheel)\n→ *Publish to MCP Registry* (updates `server.json`'s version and\npublishes via OIDC) — polling every 30 s until all four jobs complete.\n\n**Manual fallback:** watch the `publish.yml` Actions run for the tag until\nall four jobs are green.\n\nAny failed job stops the release: report the run URL, diagnose from its\nlogs, and escalate to the maintainer. The tag already exists, so the\nremedy is never re-tagging — it is a fix plus a new, higher version.\n\n### Step 9: Verify the publication and finalize the release notes\n\n**Automated:** `scripts/release.sh release-notes <X.Y.Z>` verifies the\nGitHub Release exists with both artifacts (sdist and wheel), sets the\nrelease notes to the new dated changelog section's content\n(`gh release edit`), and prints the final summary: version, tag, GitHub\nRelease URL, PyPI and TestPyPI project URLs, and the MCP Registry\nlisting.\n\n**Manual fallback:** open the GitHub Release, confirm both assets are\nattached, and paste the new changelog section into the release body.\n\nThe release is complete when all four publication targets are reachable\nand the maintainer is informed.\n\n## More Information\n\nThe staged script and the `/release` command are projections of this SOP:\nthe SOP is the normative procedure, and where the two ever disagree the\nSOP wins and the script/command must be corrected. Stages are named to\nmirror the step order so that drift between the document and its\nimplementations stays visible.\n\nThe `sop` tooling that manages this document (the `specmgr-test` MCP\nserver) runs against this repository's own dev tree; until the first\nrelease ships the `sop` domain to PyPI, this SOP is created and validated\ndirectly against the local checkout.\n\n## Updates\n\n### 2026-08-31 15:19:05.000+02:00 — Created\n\nCreated as the normative procedure for releasing `biz-dfch-specmgr`,\nconsolidating the previously hand-run README \"Make a Release\" steps\n(direct merge plus tag) with the new automation: the staged\n`scripts/release.sh`, the `/release` OpenCode command with its\nagent-judgment steps (version confirmation, changelog curation, merge\ngate, failure triage), and the pull-request-plus-fast-forward-only merge\nstrategy that keeps `main` a strict ancestor of `dev`. Status is\n`draft`; the SOP is activated once the first release executed under it\nsucceeds end to end (expected to be v0.15.0, the first release to carry\nthe `sop` domain itself)."
}
```

**Output:**

```
{
  "frontmatter": {
    "id": "98537416-0e6e-4a02-925f-974a17bfa10a",
    "type": "sop",
    "created": "2026-08-31T15:24:14.582592",
    "updated": "2026-08-31T15:24:14.582592",
    "status": "draft",
    "version": "1.0.0"
  },
  "body": {
    "purpose": {
      "text": "## Purpose\n\nThis procedure defines how a new version of `biz-dfch-specmgr` is released\nfrom the `dev` branch to TestPyPI, PyPI, a GitHub Release, and the MCP\nRegistry. It exists so that every release — whether driven by the release\nagent through the staged `scripts/release.sh` script or performed manually\nby the maintainer — passes the same gates (green CI on `dev` and on the\nmerge pull request, the fast-forward invariant between `main` and `dev`, a\ncurated changelog, and a verified publication) and produces the same\nreproducible outcome.\n"
    },
    "scope": {
      "text": "## Scope\n\nThis SOP covers: resolving the target version; pre-release checks;\ncurating the `CHANGELOG.md` `[Unreleased]` section; bumping the version in\n`pyproject.toml` and syncing `uv.lock`; committing and pushing the release\nto `dev`; merging `dev` into `main` through a fast-forward-only pull\nrequest; creating and pushing the `vX.Y.Z` tag on `main`; waiting for the\nfour publication jobs of `.github/workflows/publish.yml`; and setting the\nGitHub Release notes.\n\nIt does not cover: deciding whether the changes warrant a patch, minor, or\nmajor version (a maintainer decision made before this SOP is invoked); the\nhotfix/backport path (no such path is defined yet — should one ever be\nneeded, it is an exception to this SOP and must be recorded in its\n`Updates`); and the internals of the `publish.yml` workflow (OIDC trusted\npublishing, `server.json` generation).\n"
    },
    "definitions": {
      "text": "## Definitions\n\n- **Release commit**: the single commit on `dev` touching exactly three\n  files — `pyproject.toml`, `uv.lock`, `CHANGELOG.md` — with the message\n  `chore(release): bump version to vX.Y.Z`.\n- **Fast-forward invariant**: `main` is always an ancestor of `dev`, i.e.\n  `main` carries no unique commits. The invariant is what makes the\n  `dev` → `main` merge possible in fast-forward-only form, and it must\n  hold before every release.\n- **Stage**: a subcommand of `scripts/release.sh` (e.g. `precheck`,\n  `bump`, `pr-merge`). Stages mirror the steps of this procedure one-to-\n  one, are idempotent (a completed stage reports \"done\" instead of\n  re-running), and are the only sanctioned way for the agent to perform\n  release mechanics.\n- **`/release`**: the OpenCode command (`.opencode/command/release.md`)\n  that drives the stages and performs this SOP's agent-judgment steps\n  (version confirmation, changelog curation, merge gate, failure triage).\n- **Publication jobs**: the four jobs of\n  `.github/workflows/publish.yml`, triggered by pushing a `v*` tag:\n  *Publish to TestPyPI* → *Publish to PyPI* → *Make GitHub Release* →\n  *Publish to MCP Registry*.\n- **`[Unreleased]` section**: the Keep a Changelog staging area at the top\n  of `CHANGELOG.md` that accumulates notable changes between releases.\n- **Merge gate**: the maintainer's explicit go-ahead to merge the release\n  pull request, given after the agent presents it (Step 6).\n"
    },
    "roles_and_responsibilities": {
      "accountable": {
        "value": {
          "text": "The repository maintainer (`dfch`) is accountable for every release and\nfor the continued validity of this procedure: they make the version\ndecision, confirm the resolved version number (Step 1), approve the merge\ngate (Step 6), and adjudicate any exception."
        },
        "text": "Accountable"
      },
      "responsible": {
        "items": [
          {
            "text": "The release agent (the OpenCode session executing `/release`) runs the\nstages in order, performs the changelog curation (Step 3), and reports\nprogress and failures. In manual mode the maintainer performs every\nstep themselves."
          }
        ],
        "text": "Responsible"
      },
      "support": {
        "items": [
          {
            "text": "`scripts/release.sh` — the deterministic stage implementations\n(pre-checks, file edits, git/gh mechanics, CI polling)."
          },
          {
            "text": "GitHub Actions — `ci.yml` (lint, tests, and docs-drift checks on `dev`\nand on the pull request) and `publish.yml` (the four publication jobs)."
          },
          {
            "text": "The `uv` and `gh` CLIs, and the external publication targets: TestPyPI\nand PyPI (both via OIDC trusted publishing) and the MCP Registry (via\n`mcp-publisher` with GitHub OIDC)."
          }
        ],
        "text": "Support"
      },
      "consulted": {
        "items": [
          {
            "text": "The maintainer is consulted at exactly two gates: the version\nconfirmation after `resolve` (Step 1) and the merge gate after\n`pr-create` (Step 6)."
          }
        ],
        "text": "Consulted"
      },
      "informed": {
        "items": [
          {
            "text": "Downstream consumers are informed via the GitHub Release (notes plus\nsdist/wheel artifacts), the PyPI and TestPyPI project pages, and the MCP\nRegistry listing."
          }
        ],
        "text": "Informed"
      },
      "text": "Roles and Responsibilities"
    },
    "safety_and_precautions": {
      "text": "## Safety and Precautions\n\n- **Tag push is irreversible.** Pushing the tag immediately starts\n  publication to TestPyPI, PyPI, and the MCP Registry. A published version\n  cannot be retracted, only superseded by a newer one. Never push a tag\n  whose preconditions (Steps 1–5) have not all succeeded.\n- **Merge fast-forward only.** Never create a merge commit or squash-merge\n  when merging `dev` into `main` — a commit unique to `main` breaks the\n  fast-forward invariant and poisons every later release. The script\n  enforces this with `gh pr merge --ff-only`; manual mode uses\n  `git merge --ff-only dev`.\n- **Never double-bump.** If `pyproject.toml` already carries the target\n  version, the `bump` stage refuses to run. If a stage failed mid-release,\n  resume from the failed stage — every stage is idempotent, and\n  `scripts/release.sh status <version>` shows where the release stands —\n  rather than restarting the flow from scratch.\n- **An empty `[Unreleased]` section is a stop condition.** A release that\n  documents nothing is almost always a mistake; the `changelog` stage\n  refuses to proceed without explicit confirmation (and fails outright in\n  non-interactive mode).\n- **The release commit is exactly three files.** Any other pending change\n  in the working tree means unfinished work would be mixed into the\n  release; the pre-check and `commit-push` stages assert the tree state\n  and stop otherwise.\n- **CI failures stop the release.** A red build on `dev` or on the release\n  pull request is never force-merged or skipped: diagnose, fix on `dev`,\n  and resume from the failed stage.\n"
    },
    "procedure": {
      "steps": [
        {
          "text": "### Step 1: Resolve and confirm the target version\n\nStart from the maintainer's decision: either a full semantic version\n(`0.15.0`) or a bump keyword (`patch`/`minor`/`major`).\n\n**Automated:** `scripts/release.sh resolve <arg>` computes the target\nversion — the keyword is applied to the current `pyproject.toml` version\nper SemVer (e.g. `0.14.0` + `minor` → `0.15.0`) — and prints it without\nmutating anything. The agent then confirms the resolved number with the\nmaintainer before anything else runs; a keyword that produces a\nsurprising number (e.g. `major` on a `0.x` version → `1.0.0`) must be\nexplicitly acknowledged.\n\n**Manual fallback:** read the `version` field of `pyproject.toml`, apply\nthe SemVer bump by hand, and record the target version.\n",
          "number": 1,
          "name": "Resolve and confirm the target version"
        },
        {
          "text": "### Step 2: Run the pre-release checks\n\n**Automated:** `scripts/release.sh precheck` verifies, in order: (a) the\ncheckout is on `dev` with a clean tree in sync with `origin/dev`; (b)\n`origin/main` is an ancestor of `origin/dev` (the fast-forward\ninvariant); (c) the latest CI run on `dev` is green (waiting for an\nin-flight run, polling every 30 s); (d) the tag `vX.Y.Z` exists neither\nlocally nor on `origin`; (e) `uv lock --check` passes, i.e. `uv.lock` is\nin sync with `pyproject.toml` before the bump; (f) the `uv` and `gh` CLIs\nare present and `gh` is authenticated. Any failure stops the release with\na diagnostic.\n\n**Manual fallback:** run the checks individually: `git status`;\n`git fetch && git merge-base --is-ancestor origin/main origin/dev`;\n`gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and\n`git ls-remote --tags origin vX.Y.Z`; `uv lock --check`;\n`gh auth status`.\n",
          "number": 2,
          "name": "Run the pre-release checks"
        },
        {
          "text": "### Step 3: Curate the changelog\n\nBring the `[Unreleased]` section of `CHANGELOG.md` to the point where it\nfully describes everything user-visible since the last tag, organized\nunder Keep a Changelog categories (`Added`, `Changed`, `Deprecated`,\n`Removed`, `Fixed`, `Security`).\n\n**Automated:** the agent (not the script) performs this step. It diffs\n`git log <last-tag>..HEAD --oneline` against the existing `[Unreleased]`\nentries, adds missing items, rewrites internal or verbose entries into\nuser-facing prose, and presents the finished section to the maintainer for\nreview. This is the only step in which the agent edits a file directly.\n\n**Manual fallback:** edit the `[Unreleased]` section by hand to the same\nstandard.\n",
          "number": 3,
          "name": "Curate the changelog"
        },
        {
          "text": "### Step 4: Bump the version and sync the lockfile\n\n**Automated:** `scripts/release.sh bump <X.Y.Z>` sets the `version` field\nof `pyproject.toml` (asserting exactly one version line exists, and\nrefusing if the current version already equals the target), runs\n`uv lock`, and asserts the resulting `uv.lock` diff is only the version\nline. The stage tolerates the dirty `CHANGELOG.md` left by Step 3.\n\n**Manual fallback:** edit the `version` field of `pyproject.toml` to\n`X.Y.Z`; run `uv lock`; verify via `git diff uv.lock` that only the\n`biz-dfch-specmgr` version entry changed.\n",
          "number": 4,
          "name": "Bump the version and sync the lockfile"
        },
        {
          "text": "### Step 5: Finalize the changelog, commit, push, and wait for CI\n\n**Automated:** `scripts/release.sh changelog <X.Y.Z>` mechanically moves\nthe `[Unreleased]` content into a new dated section\n`## [X.Y.Z] - YYYY-MM-DD` directly under a re-emptied `## [Unreleased]`\nheader (refusing an empty section — see Safety and Precautions). Then\n`scripts/release.sh commit-push <X.Y.Z>` asserts the working-tree changes\nare exactly the three release files, commits them as\n`chore(release): bump version to vX.Y.Z`, pushes `dev`, and waits for the\npush-triggered CI run (the lint/tests/docs-drift matrix), polling every\n30 s.\n\n**Manual fallback:** move the section by hand (this repo uses no compare-\nlink references in the changelog); `git add pyproject.toml uv.lock CHANGELOG.md`; commit with the conventional message; `git push origin dev`; watch the Actions run until green.\n\nA red build stops the release: fix on `dev` and resume from the failed\nstage.\n",
          "number": 5,
          "name": "Finalize the changelog, commit, push, and wait for CI"
        },
        {
          "text": "### Step 6: Merge `dev` into `main` (pull request, fast-forward only, with merge gate)\n\n**Automated:** `scripts/release.sh pr-create <X.Y.Z>` creates — or resumes\n— the `dev` → `main` pull request with the new dated changelog section as\nthe pull request body, waits until the pull request's checks are green\n(30 s polling), and prints the pull request URL and head SHA — without\nmerging. The agent then presents the pull request and the changelog\nsection to the maintainer and asks for the merge gate. Once approved,\n`scripts/release.sh pr-merge <X.Y.Z>` performs\n`gh pr merge --ff-only`.\n\n**Manual fallback:** `gh pr create --base main --head dev` (body: the new\nchangelog section); wait for green checks; present to the maintainer; on\napproval, `git checkout main && git merge --ff-only dev && git push origin main`. Never use `--no-ff`, squash, or rebase merges.\n",
          "number": 6,
          "name": "Merge `dev` into `main` (pull request, fast-forward only, with merge gate)"
        },
        {
          "text": "### Step 7: Tag the release and push the tag\n\n**Automated:** `scripts/release.sh tag-push <X.Y.Z>` checks out `main`,\nruns `git pull --ff-only` (main now equals dev), creates the lightweight\ntag `vX.Y.Z` at `main`'s HEAD, pushes the tag, and switches back to\n`dev`.\n\n**Manual fallback:** `git checkout main && git pull --ff-only && git tag vX.Y.Z && git push origin vX.Y.Z && git checkout dev`.\n\nWarning: pushing the tag immediately starts publication (Step 8); the\nrelease is irreversible from here.\n",
          "number": 7,
          "name": "Tag the release and push the tag"
        },
        {
          "text": "### Step 8: Wait for the publication jobs\n\n**Automated:** `scripts/release.sh publish-wait <X.Y.Z>` waits for the\n`publish.yml` run triggered by the tag — *Publish to TestPyPI* →\n*Publish to PyPI* → *Make GitHub Release* (attaches the sdist and wheel)\n→ *Publish to MCP Registry* (updates `server.json`'s version and\npublishes via OIDC) — polling every 30 s until all four jobs complete.\n\n**Manual fallback:** watch the `publish.yml` Actions run for the tag until\nall four jobs are green.\n\nAny failed job stops the release: report the run URL, diagnose from its\nlogs, and escalate to the maintainer. The tag already exists, so the\nremedy is never re-tagging — it is a fix plus a new, higher version.\n",
          "number": 8,
          "name": "Wait for the publication jobs"
        },
        {
          "text": "### Step 9: Verify the publication and finalize the release notes\n\n**Automated:** `scripts/release.sh release-notes <X.Y.Z>` verifies the\nGitHub Release exists with both artifacts (sdist and wheel), sets the\nrelease notes to the new dated changelog section's content\n(`gh release edit`), and prints the final summary: version, tag, GitHub\nRelease URL, PyPI and TestPyPI project URLs, and the MCP Registry\nlisting.\n\n**Manual fallback:** open the GitHub Release, confirm both assets are\nattached, and paste the new changelog section into the release body.\n\nThe release is complete when all four publication targets are reachable\nand the maintainer is informed.\n",
          "number": 9,
          "name": "Verify the publication and finalize the release notes"
        }
      ],
      "text": "Procedure"
    },
    "related_artifacts": null,
    "more_information": {
      "text": "## More Information\n\nThe staged script and the `/release` command are projections of this SOP:\nthe SOP is the normative procedure, and where the two ever disagree the\nSOP wins and the script/command must be corrected. Stages are named to\nmirror the step order so that drift between the document and its\nimplementations stays visible.\n\nThe `sop` tooling that manages this document (the `specmgr-test` MCP\nserver) runs against this repository's own dev tree; until the first\nrelease ships the `sop` domain to PyPI, this SOP is created and validated\ndirectly against the local checkout.\n"
    },
    "updates": {
      "updates": [
        {
          "content": {
            "text": "Created as the normative procedure for releasing `biz-dfch-specmgr`,\nconsolidating the previously hand-run README \"Make a Release\" steps\n(direct merge plus tag) with the new automation: the staged\n`scripts/release.sh`, the `/release` OpenCode command with its\nagent-judgment steps (version confirmation, changelog curation, merge\ngate, failure triage), and the pull-request-plus-fast-forward-only merge\nstrategy that keeps `main` a strict ancestor of `dev`. Status is\n`draft`; the SOP is activated once the first release executed under it\nsucceeds end to end (expected to be v0.15.0, the first release to carry\nthe `sop` domain itself)."
          },
          "text": "2026-08-31 15:19:05.000+02:00 — Created",
          "timestamp": "2026-08-31 15:19:05.000+02:00",
          "title": "Created"
        }
      ],
      "text": "Updates"
    },
    "text": "Perform a release of biz.dfch.SpecMgr"
  }
}
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 55.4s)

_Thinking:_

The SOP was created and parsed successfully (the entire structured body was returned — all sections parsed, 9 steps with numbers/names, and the Updates entry was parsed with timestamp/title). ID: `98537416-0e6e-4a02-925f-974a17bfa10a`, status is draft.

Let me confirm where it was written on disk, and then commit it to dev.

SOP created and fully parsed (id `98537416`, status `draft`, all 9 steps + RASCI + updates validated). Verifying the file on disk and committing:

**Tool: bash**

**Input:**

```json
{
  "command": "ls docs/sop/ && head -12 docs/sop/*.md"
}
```

**Output:**

```
sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md
---
created: '2026-08-31T15:24:14.582592'
id: 98537416-0e6e-4a02-925f-974a17bfa10a
status: draft
type: sop
updated: '2026-08-31T15:24:14.582592'
version: 1.0.0
---

# Perform a release of biz.dfch.SpecMgr

## Purpose

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 70.1s)

_Thinking:_

The file is at `docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md`.

Next, commit to dev. Note: vulture/ruff don't apply to .md. Pre-commit should pass. But wait — will the `specmgr docs` pre-commit hook run? That's scoped to `src/**/*.py` changes — not applicable this time. OK.

Commit message convention: docs commit — for example, "docs(sop): add release SOP (draft)". Looking at past styles: "docs: record Task 0.29 validation failure investigation", "docs(feat-7): ...". I'll go with "docs(sop): add 'Perform a release of biz.dfch.SpecMgr' SOP (draft)".

After that, push to dev (consistent with this session's flow — the SOP needs to be on dev so that it's included in the release commit… no wait, the release commit is only 3 files. The SOP commit is a separate docs commit on dev, made before the release bump. This will flow to main via the release PR. Good.)

Also — the pre-commit hook list included a "specmgr schema" hook scoped to specific files. A new file under docs/sop — is docs/sop/\*.md covered by any hook? The hooks are scoped to src/**, tests/**, docs/adr/\*\*, etc. No problem.

Now, committing.

File in place at `docs/sop/`. Committing and pushing:

**Tool: bash**

**Input:**

```json
{
  "command": "git add docs/sop/ && git commit -m \"docs(sop): add 'Perform a release of biz.dfch.SpecMgr' SOP (draft)\" && git push"
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...........................................(no files to check)Skipped
vulture..............................................(no files to check)Skipped
unittest.............................................(no files to check)Skipped
specmgr coverage-badge...............................(no files to check)Skipped
specmgr docs.........................................(no files to check)Skipped
specmgr mcp-docs.....................................(no files to check)Skipped
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (sop package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped
[dev 79b3951] docs(sop): add 'Perform a release of biz.dfch.SpecMgr' SOP (draft)
 1 file changed, 301 insertions(+)
 create mode 100644 docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md
To https://github.com/dfch/biz.dfch.SpecMgr.git
   1a0daf3..79b3951  dev -> dev

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 443.8s)

_Thinking:_

Phase 0 complete: SOP has been committed as 79b3951 and pushed.

Next up is Phase 1: `scripts/release.sh`. This is the big one. Let me update the TODO and write the script.

Main design (from the approved plan):

- `#!/usr/bin/env bash`, `set -euo pipefail`
- Usage: `scripts/release.sh <stage> [args] [--dry-run]`, stages: resolve, precheck, bump, changelog, commit-push, pr-create, pr-merge, tag-push, publish-wait, release-notes, status, all
- Each stage is idempotent
- 30-second polling
- Per-stage working-tree assertions
- Header cites the SOP id

Let me design the script carefully:

```bash
#!/usr/bin/env bash
# Release automation for biz.dfch.SpecMgr — staged projection of the
# normative SOP "Perform a release of biz.dfch.SpecMgr"
# (docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md).
#
# Usage: scripts/release.sh <stage> [version|keyword] [--dry-run]
#   stages: resolve precheck bump changelog commit-push pr-create pr-merge
#           tag-push publish-wait release-notes status all
set -euo pipefail
```

Global variables/functions:

- `SOP_ID="98537416-0e6e-4a02-925f-974a17bfa10a"`
- `POLL_INTERVAL=30`
- `die()`, `info()` (echo to stderr/stdout)
- `is_tty() { [ -t 0 ]; }`
- `current_version()` — grep `^version = "..."` from pyproject.toml
- `resolve_version <arg>` — if full semver, echo it as-is; if keyword, compute the bump from current.
- `assert_stage <name>` — verify we're in the repo root (git rev-parse)
- `wait_for_run <run_id> <label> <timeout_min>` — 30s polling: `gh run view $id --json status,conclusion --jq '@tsv'`; on completion: success → return, otherwise die with URL.
- `find_run_for <selector...>` helper: after push, discover the run.

Stage details:

**resolve [arg]**:

- Arg: keyword (patch|minor|major) or full semver. If no arg: TTY → prompt (read); non-TTY → show usage and exit 2.
- Compute target: if full, use as-is; if keyword, bump from current.
- Verify target > current (sort -V); if equal, die "already at".
- Print only the target version (machine-readable: last line = bare version). Also print a human-facing line.
- No changes.

**precheck [version]**:

- version arg is optional (needed for tag check; if absent, skip the tag check? No — tag check needs version; make arg required for precheck, or resolve from... The flow is: resolve → precheck <v>. Make version a required arg.)
- Checks (each with a clear message, die on failure):
  a. `git rev-parse --abbrev-ref HEAD` == dev
  b. `git status --porcelain` empty (clean tree)
  c. `git fetch origin dev main` (quiet); `git rev-parse HEAD` == `git rev-parse origin/dev` (in sync)
  d. `git merge-base --is-ancestor origin/main origin/dev` → if it fails, die "main is ahead of dev"
  e. Latest dev CI run: `gh run list --branch dev --limit 1 --json databaseId,status,conclusion,displayTitle,url`. If status is in_progress/queued → wait_for_run (with a note). If conclusion != success → die with URL.
  f. Tag `v$V` not present locally (`git tag -l`) nor on origin (`git ls-remote --tags origin refs/tags/v$V`)
  g. `uv lock --check` (exit 0) — on failure, die with a hint.
  h. `command -v uv`, `command -v gh`, `gh auth status --active >/dev/null 2>&1`? `gh auth status` exits 0 if logged in to the active host. Use `gh auth status >/dev/null 2>&1`.
- Print "precheck: all checks passed (target vX.Y.Z)".

**bump <version> [--dry-run]**:

- Assert: clean tree, or only CHANGELOG.md is modified. `dirty=$(git status --porcelain)`; verify each entry is one of ` M CHANGELOG.md` / `M CHANGELOG.md` / untracked? No, no untracked allowed: entries must match only `^[ M]CHANGELOG.md$`... porcelain format: XY PATH. So filter: any line whose PATH != CHANGELOG.md → die.
- current=$(current_version); [ current != version ] || die "already at version"
- dry-run: print "would set pyproject version $current → $version and run uv lock"; exit 0.
- Edit pyproject: use sed with exact pattern `^version = "..."`. Assert exactly one match: `grep -c '^version = "' pyproject.toml` == 1. `sed -i "s/^version = \"[^\"]*\"/version = \"$version\"/" pyproject.toml`
- `uv lock`
- Assert uv.lock diff is version-only: `git diff --unified=0 uv.lock | grep -E '^[+-][^+-]'` → lines must be exactly two: the old-version line and the new-version line, both containing the version. Check: `changed=$(git diff --unified=0 uv.lock | grep -cE '^[+-][^+-]')` == 2, and both mention "version". Otherwise, die with a hint (lock drift).
- Print done.

**changelog <version> [--dry-run]**:

- Assert dirty ⊆ {pyproject.toml, uv.lock, CHANGELOG.md}
- Extract [Unreleased] content: awk from after the line `^## \[Unreleased\]` up to (not including) the next `^## \[`.
- If content has no non-empty lines → empty section: TTY → confirm with read -y/N (default no); non-TTY → die.
- dry-run: print the section that would be created; exit 0.
- Transform: replace the `## [Unreleased]` line in CHANGELOG.md with:
  ```
  ## [Unreleased]

  ## [version] - YYYY-MM-DD
  ```
  and then the original content follows... wait. The current top of the file is:
  ```
  ## [Unreleased]

  ## [0.14.0] - 2026-08-30
  ```
  With content:
  ```
  ## [Unreleased]

  <content>

  ## [0.14.0] - 2026-08-30
  ```
  Target:
  ```
  ## [Unreleased]

  ## [0.15.0] - 2026-08-31

  <content>

  ## [0.14.0] - 2026-08-30
  ```
  So: insert `## [version] - date\n\n` immediately after the blank line following `## [Unreleased]`. Robust approach: find the line number N of `^## \[Unreleased\]` (first occurrence); insert after N+1 (which must be a blank line). Use awk:
  ```awk
  NR==n { print; print ""; print "## [" v "] - " d; next } ...
  ```
  Let me try writing it:
  ```bash
  line_no=$(grep -n '^## \[Unreleased\]$' CHANGELOG.md | head -1 | cut -d: -f1)
  date_str=$(date +%F)
  awk -v n="$line_no" -v v="$version" -v d="$date_str" '
    NR==n { print; print ""; print "## [" v "] - " d; next }
    { print }
  ' CHANGELOG.md > CHANGELOG.md.tmp && mv CHANGELOG.md.tmp CHANGELOG.md
  ```
  Wait — after line N (`## [Unreleased]`) comes a blank line (N+1). awk prints line N, then `""` (a new blank line), then the header, then continues from N+1 (the original blank line). Result:
  ```
  ## [Unreleased]
  (blank from print "")
  ## [0.15.0] - date
  (blank from original N+1)
  <content...>
  ```
  Yes, correct.
- After transform: assert a dated section exists (`grep -q "^## \[$version\] - " CHANGELOG.md`), and assert the new [Unreleased] is empty (content between `## [Unreleased]` and the next `## [` is empty).

**commit-push <version> [--dry-run]**:

- Idempotency: if the message of the latest commit on dev matches `^chore(release): bump version to v$version$` and the tree is clean and HEAD == origin/dev → release commit is already pushed → skip to CI wait. Check: `git log -1 --format=%s` == expected message and clean and in sync → info "already committed and pushed; waiting for CI" and go to CI wait.
- Assert dirty == exactly {pyproject.toml, uv.lock, CHANGELOG.md} (all three present? If bump has already been run and committed... In the normal flow all three are dirty. If some are already committed (resume), the dirty set might be empty — handled by the idempotency path above. So: if the dirty set is non-empty, it must be exactly these three files.)
- current_version must equal $version (otherwise the bump wasn't run) → die with a hint.
- dry-run: print what would be committed; exit 0.
- `git add pyproject.toml uv.lock CHANGELOG.md`
- `git commit -m "chore(release): bump version to v$version"`
- `git push origin dev`
- CI wait: discover the run triggered by the push. After push, poll for a new run: `gh run list --branch dev --limit 1` — a run should appear within ~30–60s. Loop: for i in 1..10: run=$(gh run list --branch dev --limit 1 --json databaseId,headSha,status --jq '.[0]'); if headSha == $(git rev-parse HEAD) → found. Sleep 15s. Then wait_for_run.
  - Note: ci.yml runs on push → a run exists for the new head SHA.
- wait_for_run run_id "dev CI" 40 min.

**pr-create <version> [--dry-run]**:

- Prereq: release commit is on origin/dev (HEAD == origin/dev, or at least origin/dev contains the bump commit).
- Idempotency: an existing open PR with base main, head dev → resume: `gh pr list --base main --head dev --state open --json number,url --jq '.[0]'`. If found → go to checks wait.
- dry-run: print the PR that would be created; exit 0.
- Create: `gh pr create --base main --head dev --title "Release v$version" --body "<changelog section>"` — extract the changelog section: from `^## \[$version\] - ` to the next `^## `. Write to a temp file and use `--body-file`.
- Wait for checks: `gh pr checks <num>` — exit 0 if all pass, 1 if any fail, 2 if pending? Actually `gh pr checks` exit codes: 0 all pass, 1 at least one fail, 2 at least one pending. Loop every 30s: until exit 0 (→ done) or exit 1 (→ die with failing checks). With a timeout.
- Print "PR <url> ready (checks green) — merge gate required" and exit 0. (No merge.)

**pr-merge <version> [--dry-run]**:

- Find open PR (base main head dev); if none → die "no open release PR; run pr-create first".
- Assert checks are green (`gh pr checks` exit 0, or 1 → die).
- dry-run: print "would ff-only merge PR <num>"; exit 0.
- `gh pr merge <num> --ff-only` (no --delete-branch: head is dev itself! `--delete-branch` would try to delete dev — never use it. gh by default doesn't delete unless --delete-branch is passed. Good. Also no auto-merge needed.)
- After merge: `git fetch origin main`; assert `git rev-parse origin/main` == `git rev-parse origin/dev`? After an ff merge, main == dev's tip. Verify (if they differ, die — something unexpected happened).
- Print done.

**tag-push <version> [--dry-run]**:

- Idempotency: if tag exists locally or on origin → if it exists on origin at the correct SHA (origin/main) → done. If the tag exists at a different SHA → die (tag collision — serious).
- Prereq: on dev, clean tree (or at least the ability to checkout main).
- dry-run: print the plan; exit 0.
- `git checkout main && git pull --ff-only origin main`
- `git tag v$version`
- `git push origin v$version`
- `git checkout dev`
- Print done + warning that publication has started.

**publish-wait <version> [--dry-run]**:

- Discover the run for the tag: `gh run list --workflow "publish.yml" --limit 1 --json databaseId,headSha,status,conclusion,url --jq '.[0]'` — the run for the tag has headSha == tag's target. Or use `--tag v$version`? Does `gh run list` support `--tag`? Yes: `gh run list --tag <tag>`.
- Poll for run to appear (a few seconds after tag push), then wait_for_run with a 45-min timeout.
- On completion: also verify all 4 jobs succeeded: run-level success means all jobs succeeded (required jobs). Sufficient; but for the report, list jobs: `gh run view $id --json jobs --jq '.jobs[].name'`... just reporting the run is fine.
- dry-run: print the plan; exit 0.

**release-notes <version> [--dry-run]**:

- Verify the release exists: `gh release view v$version --json tagName,assets,url` → if it doesn't exist, die with a hint (the publish job failed).
- Assert assets >= 2 (sdist+wheel).
- Extract the section body (same awk as pr-create).
- dry-run: print the notes that would be set; exit 0.
- `gh release edit v$version --notes-file <tmp>`
- Print summary: version, tag, GH release URL, PyPI URLs:
  - https://pypi.org/project/biz-dfch-specmgr/v/
  - https://test.pypi.org/project/biz-dfch-specmgr/v/
  - MCP registry: https://registry.modelcontextprotocol.io/ (search by name? README's URL: https://registry.modelcontextprotocol.io/?q=io.github.dfch%2Fbiz-dfch-specmgr)
- Done.

**status <version>**:

- Read-only probe, print a table:
  - bump done? current_version == version
  - changelog done? dated section exists && [Unreleased] is empty
  - commit-push done? dev has a bump commit (log search) && pushed (origin/dev has it)
  - dev CI: latest run's status/conclusion
  - PR: open PR dev→main? number, state, check status
  - merged? origin/main == origin/dev (and contains the bump commit)
  - tag: does v exist locally/origin? at which SHA?
  - publish: latest run of publish.yml for the tag: status
  - release: does it exist? asset count? do notes match the section?
- Print each line as " [x] bump (0.15.0 in pyproject.toml)" / "[ ] ..." / "[!] ...".
- exit 0 (informational).

**all [arg] [--dry-run]**:

- Resolve version (arg or prompt) → then run: precheck, (no curation — note that [Unreleased] must already be curated), bump, changelog, commit-push, pr-create, **merge gate: TTY → confirm; non-TTY → die "use pr-create + pr-merge manually or in an agent"**... Hmm, wait. all mode is "mechanical release of an already-curated [Unreleased], no agent". The merge gate is a human confirmation — in terminal TTY mode, all mode can do a read confirmation. Non-TTY all mode → stop after pr-create? That's awkward. Decision: `all` requires a TTY (since it has interactive confirmations: version prompt (if no arg), empty-changelog confirmation, merge gate). Non-TTY `all` → die with "all mode is interactive; run the stages individually". Simple, safe.
- Then pr-merge, tag-push, publish-wait, release-notes.

**Version-arg handling for each stage**: bump/changelog/commit-push/pr-\*/tag-push/publish-wait/release-notes/status take `<version>` as a required arg (full semver — stages take the resolved version, not a keyword; only `resolve` and `all` accept keywords). --dry-run is the last arg (parse args manually: iterate over args, collect version + flags).

Arg-parsing approach: each stage function takes positional args; a top-level parse: stage=$1, shift; then loop over the rest: `--dry-run` sets DRY_RUN=1, otherwise VERSION_ARG=$arg (at most one non-flag arg; resolve may have keyword-or-version).

Timeouts: wait_for_run takes a label + max minutes; loops with a counter; on timeout, die with URL.

Polling helper:

```bash
wait_for_run() {
  local run_id="$1" label="$2" timeout_min="${3:-45}"
  local run_url status conclusion i
  run_url=$(gh run view "$run_id" --json url --jq .url)
  info "waiting for $label ($run_url) — polling every ${POLL_INTERVAL}s"
  i=0
  while :; do
    read -r status conclusion < <(gh run view "$run_id" --json status,conclusion --jq '[.status, .conclusion // ""] | @tsv')
    if [[ "$status" == "completed" ]]; then
      if [[ "$conclusion" == "success" ]]; then info "$label: success"; return 0; fi
      die "$label failed (conclusion: $conclusion) — $run_url"
    fi
    i=$((i+1)); (( i >= timeout_min*60/POLL_INTERVAL )) && die "timed out waiting for $label — $run_url"
    sleep "$POLL_INTERVAL"
  done
}
```

Note `read -r status conclusion < <(...)` — needs process substitution; fine in bash. Under set -e, `(( i >= ... )) && die` — if the arithmetic is 0 (false), `(( ))` returns 1, and `&& die` short-circuits... but under set -e, if `(( ))` returns nonzero as part of an `&&` list — if it's the last command of a compound list... actually `a && b` where a fails: the list returns a's failure status, but set -e doesn't fire for commands within an && list except the last one... hmm: set -e exits when a *pipeline* fails, unless it's part of a conditional context. `(( i >= n )) && die` — if `(( ))` fails, the && list's result is failure, and that list is a top-level statement → set -e triggers! Classic pitfall. Use `if (( i >= n )); then die; fi`.

Also `read -r status conclusion < <(gh ...)` — if gh fails, read gets EOF → read returns 1 → set -e kills the script. Wrap: `gh ... || die "cannot query run"`.

find_new_dev_run:

```bash
wait_for_dev_run() {
  local head_sha target i
  head_sha=$(git rev-parse origin/dev)
  i=0
  while :; do
    local run_json
    run_json=$(gh run list --branch dev --limit 1 --json databaseId,headSha,status)
    if [[ "$(jq -r '.[0].headSha' <<<"$run_json")" == "$head_sha" ]]; then
      local rid; rid=$(jq -r '.[0].databaseId' <<<"$run_json")
      wait_for_run "$rid" "dev CI" 40
      return 0
    fi
    i=$((i+1)); if (( i >= 10 )); then die "no CI run appeared for dev head $head_sha"; fi
    sleep 15
  done
}
```

jq dependency — is jq available? It's in the publish workflow, and on this machine? Check `command -v jq`. Add jq to precheck's tool list. Or avoid jq and use gh --jq. Better: use gh's built-in --jq everywhere (no jq dependency):
`gh run list --branch dev --limit 1 --json headSha --jq '.[0].headSha'` and separately `--json databaseId --jq '.[0].databaseId'` (2 calls) or one call with @tsv. Let's go with a single call: `gh run list --branch dev --limit 1 --json databaseId,headSha --jq '.[0] | @tsv'` → "id\\tsha". Then `read -r rid sha <<< "$line"`.

gh pr checks exit codes: 0 = all pass; 1 = at least one fail; 2 = at least one pending (I believe that's correct per gh docs: "exits 0 if all checks pass, 1 if any fail, 2 if any are pending"). Loop:

```bash
wait_for_pr_checks() {
  local pr="$1" i=0 rc
  while :; do
    if gh pr checks "$pr" >/dev/null 2>&1; then info "PR #$pr checks green"; return 0; fi
    rc=$?  # note: under set -e, `if` guards it
    ...
```

Hmm, capturing rc under set -e: use `if gh pr checks "$pr" >/dev/null; then return; else rc=$?; fi` — but `$?` after `else`... inside the else branch, $? is the exit code of the if condition? No — in `if cmd; then A; else B; fi`, at the start of B, $? is cmd's exit status. Yes, that works. But we need to distinguish rc=1 (fail → die) from rc=2 (pending → sleep). But wait — `gh pr checks` also outputs a table; redirect to /dev/null. On failure, show the output: `gh pr checks "$pr" || true` to capture... simpler:

```bash
local out rc
out=$(gh pr checks "$pr" 2>&1) && rc=0 || rc=$?
if (( rc == 0 )); then info ...; return 0; fi
if (( rc == 1 )); then printf '%s\n' "$out" >&2; die "PR #$pr checks failing"; fi
# rc==2 (pending) or other → sleep
```

The `out=$(cmd) && rc=0 || rc=$?` pattern is safe under set -e.

Wait, one more subtlety: `gh pr checks` with no required checks configured — does it exit 0 if there are no checks? If there are no checks at all, does it exit 0 with "no checks found"? Hmm, if there are no checks, it might exit 1 with "no checks found on PR". Our PR has CI checks (ci.yml runs on pull_request). No problem.

Changelog section extraction (for PR body and release notes):

```bash
extract_section() {  # $1 = version; prints the section body (heading line excluded? included?)
  awk -v v="$1" '
    $0 == "## [" v "] - " { found=1; next }
    found && /^## / { exit }
    found { print }
  ' CHANGELOG.md
}
```

For the notes, we want the body without the `## [v] - date` heading (GH renders the heading fine, but cleaner without). For the PR body, include the heading? For a PR body, the section content under the heading is enough. Let's extract the content without the heading line; leading blank line — strip it (awk prints from the first content line; the blank line right after the heading is included as "" — trim leading blank lines with sed 's/^\[[:space:]\]\*$//'? Simpler: pipe through `sed -e :a -e '/./,$!d'` to strip leading blank lines. Or start awk after skipping blanks:

```awk
$0 == "## [" v "] - " { found=1; next }
found && /^## / { exit }
found && !skipblank && $0 ~ /^[[:space:]]*$/ { next }
found { skipblank=0; print }
```

Hmm, wait, that skips all leading blank lines — good. But the internal structure: the section content includes `### Added` etc. No problem.

Trim trailing blank lines too: `| sed -e '${/^$/d}'` loop... awk's print then `awk` again... skip the trailing trim; harmless.

pyproject version:

```bash
current_version() {
  grep -m1 '^version = "' pyproject.toml | sed 's/^version = "\(.*\)"$/\1/'
}
```

Resolve keyword bump:

```bash
bump_semver() {  # $1=current, $2=keyword → echo new
  local IFS=. maj="${1%% *}"
  local a b c
  a=$(cut -d. -f1 <<<"$1"); b=$(cut -d. -f2 <<<"$1"); c=$(cut -d. -f3 <<<"$1")
  case "$2" in
    patch) echo "$a.$b.$((c+1))" ;;
    minor) echo "$a.$((b+1)).0" ;;
    major) echo "$((a+1)).0.0" ;;
    *) die "unknown bump keyword: $2" ;;
  esac
}
```

TTY prompt for version (in resolve/all with no arg):

```bash
if [[ -z "${1:-}" ]]; then
  if is_tty; then
    read -r -p "Target version (full X.Y.Z or patch/minor/major) [suggested: $(suggest)]: " v
  else
    die "version required (non-interactive): $0 resolve <X.Y.Z|patch|minor|major>"
  fi
fi
```

Now — `precheck` requires a version for the tag check. But in the agent flow, precheck runs after resolve. `all` runs resolve first. OK: `precheck <version>` is required.

Wait, one more thing: precheck (a) requires a clean tree — but in the agent flow, precheck (step 2) runs before changelog curation (step 3), so the tree is clean at that point. Good, this matches the SOP's step order.

Edge: the `bump` stage asserts dirty ⊆ {CHANGELOG.md}. If the user runs bump without curation (all mode: curation is skipped — [Unreleased] is assumed pre-curated), the tree is clean → fine (the subset check allows clean too).

The `changelog` stage: dirty ⊆ {pyproject.toml, uv.lock, CHANGELOG.md}. In all mode after bump: dirty = {pyproject, uv.lock} (CHANGELOG clean) → OK. In agent mode: dirty = {pyproject, uv.lock, CHANGELOG} → OK.

`commit-push`: dirty is exactly the 3 files, or (idempotency path) clean with the bump commit already pushed.

Also `commit-push` asserts current_version == $version.

Another design point: all stages except resolve require the VERSION arg to be a full semver (validate with a regex). `all` accepts a keyword (resolves first).

Script length: probably ~350–400 lines. That's fine.

Also add a `usage()` that prints the stages + SOP reference.

SOP reference in header: full path `docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md` and id.

Now, let me double-check the behavior of `gh run list --workflow "publish.yml"`: it matches by the workflow name ("Publish to PyPI") or by the file name? `--workflow` takes a workflow name or filename — I believe the filename (publish.yml) also works. Safer: `--tag v$V`? Does `gh run list --tag` exist? Let me check: `gh run list` flags: --branch, --commit, --event, --job, --label, --owner, --repo, --set-exit-status, --source, --team, --user, --workflow. Hmm, no --tag. So use `--workflow publish.yml` (I'm pretty sure gh accepts the workflow file name). Or `--commit $(git rev-parse v$V)` — the tag points to a commit; runs are triggered by push to a tag ref → run's headSha == the tag's commit. `--commit <sha>` filters by head SHA. That's robust: `gh run list --commit $(git rev-parse "v$V") --limit 5` and pick the one whose event == push and workflow is publish. Simpler: use `--workflow "publish.yml"` — I'll verify against gh at runtime during the test phase (can't fully test publish-wait without a real tag; but `--workflow publish.yml` can be tested to list past runs). I'll do a quick sanity check with bash during the test phase.

Actually, let me test `gh run list --workflow publish.yml --limit 3` right now (read-only) to confirm it works.

Also `gh release view v$V --json tagName,assets,url`.

And `gh pr merge <n> --ff-only` — the flag exists (--ff-only). Yes.

`uv lock --check` — exists (uv 0.4+). Verify uv version at runtime during the test phase.

Now let me write the script. Write it to scripts/release.sh with the `write` tool, chmod +x, bash -n, then test the safe stages (resolve, precheck, status, dry-runs).

One more thing: `set -euo pipefail` + arithmetic — watch out for `(( ))`. Use the `if (( ))` form.

`wait_for_run` TSV read:

```bash
local line status conclusion
line=$(gh run view "$run_id" --json status,conclusion --jq '[.status, (.conclusion // "")] | @tsv') || die "cannot query run $run_id"
status=${line%%$'\t'*}
conclusion=${line#*$'\t'}
```

This avoids read/process-substitution pitfalls.

Polling timeout count: max_polls=$((timeout_min * 60 / POLL_INTERVAL)).

For dev-run discovery:

```bash
line=$(gh run list --branch dev --limit 1 --json databaseId,headSha --jq '.[0] | @tsv') || die ...
rid=${line%%$'\t'*}; sha=${line#*$'\t'}
```

OK, writing now. Also, info() goes to stdout with a "release:" prefix; die() goes to stderr with exit 1.

Dry-run semantics per stage: print the intended actions, no changes, exit 0.

Let me write the file.

Phase 0 complete (commit `79b3951`). Moving to Phase 1 — the staged script:

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Verify specmgr-test MCP swap (version + sop resources)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 0: create release SOP via specmgr-test (draft), commit to dev",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 1: scripts/release.sh (staged, idempotent, --dry-run, status, all)",
      "status": "in_progress",
      "priority": "high"
    },
    {
      "content": "Phase 2: .opencode/command/release.md orchestration protocol",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 3: README 'Make a Release' + AGENTS.md updates",
      "status": "pending",
      "priority": "medium"
    },
    {
      "content": "Phase 4: verification (bash -n, dry-runs, resolve/precheck/status, non-TTY misuse)",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 5 (later): first real /release 0.15.0, then SOP draft → active",
      "status": "pending",
      "priority": "low"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Verify specmgr-test MCP swap (version + sop resources)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 0: create release SOP via specmgr-test (draft), commit to dev",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 1: scripts/release.sh (staged, idempotent, --dry-run, status, all)",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Phase 2: .opencode/command/release.md orchestration protocol",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 3: README 'Make a Release' + AGENTS.md updates",
    "status": "pending",
    "priority": "medium"
  },
  {
    "content": "Phase 4: verification (bash -n, dry-runs, resolve/precheck/status, non-TTY misuse)",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 5 (later): first real /release 0.15.0, then SOP draft → active",
    "status": "pending",
    "priority": "low"
  }
]
```

**Tool: bash**

**Input:**

```json
{
  "command": "gh run list --workflow publish.yml --limit 3 --json databaseId,event,headSha,displayTitle 2>&1 | head -5; uv lock --check && echo \"uv lock --check OK\""
}
```

**Output:**

```
Unknown JSON field: "displayTitle"
Available fields:
  conclusion
  createdAt
  databaseId
Resolved 95 packages in 1ms
uv lock --check OK

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 365.4s)

_Thinking:_

`gh run list --workflow publish.yml` works (only the JSON field displayTitle was invalid). `uv lock --check` works. Let me quickly re-verify the available fields for run list, then write the script.

Actually, the list of available fields was truncated at the head of the error (only showing up to databaseId). The standard fields include status, conclusion, headSha, event, title, databaseId, url. I'll go with `databaseId,headSha,status,conclusion,event,title`.

Alright, let's write the script.

`--workflow publish.yml` works and `uv lock --check` is available. Writing the script:

**Tool: write**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "content": "#!/usr/bin/env bash\n# Staged release automation for biz.dfch.SpecMgr.\n#\n# Deterministic projection of the normative SOP \"Perform a release of\n# biz.dfch.SpecMgr\" (SOP 98537416-0e6e-4a02-925f-974a17bfa10a,\n# docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md).\n# Where this script and the SOP disagree, the SOP wins: fix the script.\n#\n# Usage: scripts/release.sh <stage> [X.Y.Z | patch | minor | major] [--dry-run]\n#\n# Stages (mirror the SOP's 9 procedure steps; every stage is idempotent):\n#   resolve       compute and print the target version (no mutation)\n#   precheck      fail-fast pre-release checks (SOP step 2)\n#   bump          pyproject.toml + uv.lock version bump (SOP step 4)\n#   changelog     move [Unreleased] into a dated section (SOP step 5a)\n#   commit-push   commit the 3 release files, push dev, wait for CI (SOP step 5b)\n#   pr-create     open the dev->main release PR, wait for checks (SOP step 6a)\n#   pr-merge      ff-only merge of the release PR (SOP step 6b, after the merge gate)\n#   tag-push      tag vX.Y.Z on main, push the tag, back to dev (SOP step 7)\n#   publish-wait  wait for the 4 publish.yml jobs (SOP step 8)\n#   release-notes verify the release + set the GitHub Release notes (SOP step 9)\n#   status        read-only: where does this release stand?\n#   all           resolve + precheck + bump + changelog + commit-push +\n#                 pr-create + [TTY merge gate] + pr-merge + tag-push +\n#                 publish-wait + release-notes (no agent curation: the\n#                 [Unreleased] section must already be curated)\n#\n# Only `resolve` and `all` accept bump keywords; all other stages take the\n# full resolved version.\n\nset -euo pipefail\n\nSOP_ID=\"98537416-0e6e-4a02-925f-974a17bfa10a\"\nREPO_ROOT=\"biz-dfch-specmgr\"\nPOLL_INTERVAL=30\nDEV_CI_TIMEOUT_MIN=40\nPUBLISH_TIMEOUT_MIN=45\n\nDRY_RUN=0\nVERSION_ARG=\"\"\n\ninfo() { printf 'release: %s\\n' \"$*\"; }\ndie() { printf 'release: ERROR: %s\\n' \"$*\" >&2; exit 1; }\nis_tty() { [ -t 0 ]; }\n\nusage() {\n  sed -n '2,30p' \"$0\" | sed 's/^# \\{0,1\\}//'\n  exit 2\n}\n\n# --- generic helpers ---------------------------------------------------------\n\nrequire_repo_root() {\n  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die \"not inside a git work tree\"\n  [ \"$(git rev-parse --show-toplevel)\" = \"$(pwd)\" ] || die \"run from the repo root (cwd: $(pwd))\"\n}\n\nrequire_tools() {\n  command -v git >/dev/null || die \"git not found\"\n  command -v uv >/dev/null || die \"uv not found\"\n  command -v gh >/dev/null || die \"gh not found\"\n  gh auth status >/dev/null 2>&1 || die \"gh is not authenticated (gh auth status)\"\n}\n\ncurrent_version() {\n  local line\n  line=$(grep -m1 '^version = \"' pyproject.toml) || die \"no version line in pyproject.toml\"\n  printf '%s' \"${line#version = \\\"}\" | sed 's/\"$//'\n}\n\nvalidate_full_version() {\n  [[ \"$1\" =~ ^[0-9]+\\.[0-9]+\\.[0-9]+$ ]] || die \"'$1' is not a full semantic version (X.Y.Z)\"\n}\n\n# $1 = current version, $2 = keyword -> prints bumped version\nbump_semver() {\n  local a b c\n  a=$(cut -d. -f1 <<<\"$1\"); b=$(cut -d. -f2 <<<\"$1\"); c=$(cut -d. -f3 <<<\"$1\")\n  case \"$2\" in\n    patch) echo \"$a.$b.$((c + 1))\" ;;\n    minor) echo \"$a.$((b + 1)).0\" ;;\n    major) echo \"$((a + 1)).0.0\" ;;\n    *) die \"unknown bump keyword: $2\" ;;\n  esac\n}\n\n# Resolve $1 (full version or keyword) against the current pyproject version.\nresolve_target() {\n  local current arg\n  current=$(current_version)\n  arg=\"${1:-}\"\n  if [ -z \"$arg\" ]; then\n    if is_tty; then\n      info \"current version: $current\"\n      local v\n      read -r -p \"Target version (X.Y.Z or patch/minor/major) [suggested: $(bump_semver \"$current\" minor)]: \" v\n      arg=\"$v\"\n    else\n      die \"version required in non-interactive mode: $0 <stage> <X.Y.Z|patch|minor|major>\"\n    fi\n  fi\n  local target\n  if [[ \"$arg\" =~ ^[0-9]+\\.[0-9]+\\.[0-9]+$ ]]; then\n    target=\"$arg\"\n  elif [[ \"$arg\" == patch || \"$arg\" == minor || \"$arg\" == major ]]; then\n    target=$(bump_semver \"$current\" \"$arg\")\n  else\n    die \"version must be a full X.Y.Z or one of patch/minor/major, got: $arg\"\n  fi\n  [ \"$target\" != \"$current\" ] || die \"pyproject.toml already carries $target (no re-bump; use status <v> to see where the release stands)\"\n  printf '%s' \"$target\"\n}\n\n# Extract the dated changelog section body for $1 (heading line excluded,\n# leading blanks trimmed).\nextract_changelog_section() {\n  awk -v v=\"$1\" '\n    $0 == \"## [\" v \"] - \" { found = 1; next }\n    found && /^## / { exit }\n    found && $0 ~ /^[[:space:]]*$/ && !started { next }\n    found { started = 1; print }\n  ' CHANGELOG.md\n}\n\n# Print the content of the current [Unreleased] section (heading excluded).\nunreleased_content() {\n  awk '\n    $0 == \"## [Unreleased]\" { found = 1; next }\n    found && /^## / { exit }\n    found { print }\n  ' CHANGELOG.md\n}\n\nunreleased_is_empty() {\n  ! grep -q '[^[:space:]]' <<<\"$(unreleased_content)\"\n}\n\n# Poll a workflow run every POLL_INTERVAL seconds until it completes.\n# $1 = run id, $2 = label, $3 = timeout in minutes.\nwait_for_run() {\n  local run_id=\"$1\" label=\"$2\" timeout_min=\"${3:-$DEV_CI_TIMEOUT_MIN}\"\n  local run_url line status conclusion polls max_polls\n  run_url=$(gh run view \"$run_id\" --json url --jq .url) || die \"cannot query run $run_id\"\n  info \"waiting for $label: $run_url (poll every ${POLL_INTERVAL}s, timeout ${timeout_min}m)\"\n  max_polls=$((timeout_min * 60 / POLL_INTERVAL))\n  polls=0\n  while :; do\n    line=$(gh run view \"$run_id\" --json status,conclusion --jq '[.status, (.conclusion // \"\")] | @tsv') || die \"cannot query run $run_id\"\n    status=\"${line%%$'\\t'*}\"\n    conclusion=\"${line#*$'\\t'}\"\n    if [ \"$status\" = \"completed\" ]; then\n      if [ \"$conclusion\" = \"success\" ]; then\n        info \"$label: success\"\n        return 0\n      fi\n      die \"$label failed (conclusion: $conclusion): $run_url\"\n    fi\n    polls=$((polls + 1))\n    if [ \"$polls\" -ge \"$max_polls\" ]; then\n      die \"timed out waiting for $label: $run_url\"\n    fi\n    sleep \"$POLL_INTERVAL\"\n  done\n}\n\n# Wait until a dev run exists for the current origin/dev head, then for it to pass.\nwait_for_dev_ci() {\n  local head_sha line rid sha polls\n  head_sha=$(git rev-parse origin/dev)\n  info \"waiting for a CI run to appear on dev head ${head_sha:0:12} ...\"\n  polls=0\n  while :; do\n    line=$(gh run list --branch dev --limit 1 --json databaseId,headSha --jq '.[0] | @tsv') || die \"cannot list runs\"\n    rid=\"${line%%$'\\t'*}\"\n    sha=\"${line#*$'\\t'}\"\n    if [ \"$sha\" = \"$head_sha\" ]; then\n      wait_for_run \"$rid\" \"dev CI\" \"$DEV_CI_TIMEOUT_MIN\"\n      return 0\n    fi\n    polls=$((polls + 1))\n    if [ \"$polls\" -ge 10 ]; then\n      die \"no CI run appeared for dev head $head_sha within 150s\"\n    fi\n    sleep 15\n  done\n}\n\n# Poll a PR's checks every POLL_INTERVAL seconds. $1 = PR number.\nwait_for_pr_checks() {\n  local pr=\"$1\" out rc polls\n  polls=0\n  while :; do\n    out=$(gh pr checks \"$pr\" 2>&1) && rc=0 || rc=$?\n    if [ \"$rc\" -eq 0 ]; then\n      info \"PR #$pr checks: all green\"\n      return 0\n    fi\n    if [ \"$rc\" -eq 1 ]; then\n      printf '%s\\n' \"$out\" >&2\n      die \"PR #$pr checks are failing (see above); fix on dev and resume from the failed stage\"\n    fi\n    polls=$((polls + 1))\n    if [ \"$polls\" -ge 40 ]; then\n      die \"timed out waiting for PR #$pr checks\"\n    fi\n    info \"PR #$pr checks: pending (poll ${polls}/40)\"\n    sleep \"$POLL_INTERVAL\"\n  done\n}\n\n# List of dirty files (paths only), empty if clean.\ndirty_files() {\n  git status --porcelain | awk '{print $NF}'\n}\n\n# Assert the dirty set is a subset of the given file list ($2..$n).\nassert_dirty_subset() {\n  local allowed=\"${1:-}\" f\n  shift\n  for f in $(dirty_files); do\n    local ok=0 a\n    for a in \"$@\"; do\n      if [ \"$f\" = \"$a\" ]; then ok=1; break; fi\n    done\n    [ \"$ok\" -eq 1 ] || die \"unexpected working-tree change: $f (allowed: $*)\"\n  done\n}\n\nconfirm_or_die() {\n  # $1 = question; TTY: prompt (default no); non-TTY: die.\n  local q=\"$1\" a\n  if is_tty; then\n    read -r -p \"$q [y/N]: \" a\n    [ \"$a\" = \"y\" ] || [ \"$a\" = \"Y\" ] || die \"aborted at confirmation\"\n  else\n    die \"$q (interactive confirmation required; re-run from a TTY)\"\n  fi\n}\n\n# --- stages ------------------------------------------------------------------\n\nstage_resolve() {\n  local target\n  target=$(resolve_target \"${1:-}\")\n  echo \"$target\"\n}\n\nstage_precheck() {\n  local v=\"${1:-}\"\n  [ -n \"$v\" ] || die \"usage: $0 precheck <X.Y.Z>\"\n  validate_full_version \"$v\"\n  require_repo_root\n  require_tools\n  info \"target: v$v\"\n\n  local branch\n  branch=$(git rev-parse --abbrev-ref HEAD)\n  [ \"$branch\" = \"dev\" ] || die \"not on dev (on: $branch)\"\n\n  [ -z \"$(dirty_files)\" ] || die \"working tree is not clean:\"\n  git status --porcelain >&2\n\n  git fetch origin dev main --quiet\n  [ \"$(git rev-parse HEAD)\" = \"$(git rev-parse origin/dev)\" ] || die \"local dev is not in sync with origin/dev (push or pull first)\"\n\n  if git merge-base --is-ancestor origin/main origin/dev; then\n    info \"fast-forward invariant holds (main is an ancestor of dev)\"\n  else\n    die \"main is AHEAD of dev (main has unique commits) — the dev->main merge could not fast-forward; resolve this before releasing\"\n  fi\n\n  local line rid sha status conclusion\n  line=$(gh run list --branch dev --limit 1 --json databaseId,headSha,status,conclusion --jq '.[0] | @tsv') || die \"cannot list dev runs\"\n  IFS=$'\\t' read -r rid sha status conclusion <<<\"$line\"\n  if [ \"$status\" != \"completed\" ]; then\n    info \"latest dev CI run still in flight (status: $status) — waiting\"\n    wait_for_run \"$rid\" \"dev CI (in-flight)\" \"$DEV_CI_TIMEOUT_MIN\"\n  else\n    [ \"$conclusion\" = \"success\" ] || die \"latest dev CI run is not green (conclusion: ${conclusion:-none})\"\n    info \"latest dev CI run is green\"\n  fi\n\n  if [ -n \"$(git tag -l \"v$v\")\" ] || [ -n \"$(git ls-remote --tags origin \"refs/tags/v$v\")\" ]; then\n    die \"tag v$v already exists (locally or on origin)\"\n  fi\n  info \"tag v$v does not exist yet\"\n\n  uv lock --check >/dev/null 2>&1 || die \"uv.lock is out of sync with pyproject.toml — run 'uv lock' and commit the result before releasing\"\n  info \"uv.lock is in sync\"\n\n  info \"precheck: all checks passed for v$v\"\n}\n\nstage_bump() {\n  local v=\"${1:-}\"\n  [ -n \"$v\" ] || die \"usage: $0 bump <X.Y.Z>\"\n  validate_full_version \"$v\"\n  require_repo_root\n  assert_dirty_subset \"\" CHANGELOG.md\n  local current\n  current=$(current_version)\n  [ \"$current\" != \"$v\" ] || die \"pyproject.toml already carries $v\"\n\n  if [ \"$DRY_RUN\" -eq 1 ]; then\n    info \"[dry-run] would set pyproject.toml version $current -> $v, then run 'uv lock'\"\n    return 0\n  fi\n\n  local n\n  n=$(grep -c '^version = \"' pyproject.toml)\n  [ \"$n\" -eq 1 ] || die \"expected exactly one 'version = \\\"...\\\"' line in pyproject.toml, found $n\"\n  sed -i \"s/^version = \\\"[^\\\"]*\\\"/version = \\\"$v\\\"/\" pyproject.toml\n  info \"pyproject.toml: $current -> $v\"\n\n  uv lock\n  local changed old_line new_line\n  changed=$(git diff --unified=0 uv.lock | grep -cE '^[+-][^+-]' || true)\n  [ \"$changed\" -eq 2 ] || die \"uv.lock diff is not exactly the version line ($changed changed lines) — inspect 'git diff uv.lock'\"\n  old_line=$(git diff --unified=0 uv.lock | grep -E '^-' | grep -v '^---')\n  new_line=$(git diff --unified=0 uv.lock | grep -E '^+' | grep -v '^+++')\n  grep -q \"$current\" <<<\"$old_line\" && grep -q \"$v\" <<<\"$new_line\" || die \"uv.lock version-line diff does not look like $current -> $v:\"\n  info \"uv.lock: only the $REPO_ROOT version entry changed\"\n  info \"bump: done ($v)\"\n}\n\nstage_changelog() {\n  local v=\"${1:-}\"\n  [ -n \"$v\" ] || die \"usage: $0 changelog <X.Y.Z>\"\n  validate_full_version \"$v\"\n  require_repo_root\n  assert_dirty_subset \"\" pyproject.toml uv.lock CHANGELOG.md\n\n  if grep -q \"^## \\[$v\\] - \" CHANGELOG.md; then\n    info \"changelog: section ## [$v] already present — nothing to do\"\n    return 0\n  fi\n\n  if unreleased_is_empty; then\n    confirm_or_die \"the [Unreleased] section is EMPTY — releasing with no documented changes is almost always a mistake. Continue with v$v?\"\n  fi\n\n  if [ \"$DRY_RUN\" -eq 1 ]; then\n    info \"[dry-run] would move the [Unreleased] content into '## [$v] - $(date +%F)' under a re-emptied '## [Unreleased]' header\"\n    return 0\n  fi\n\n  local line_no\n  line_no=$(grep -n '^## \\[Unreleased\\]$' CHANGELOG.md | head -1 | cut -d: -f1) || die \"no '## [Unreleased]' header in CHANGELOG.md\"\n  awk -v n=\"$line_no\" -v v=\"$v\" -v d=\"$(date +%F)\" '\n    NR == n { print; print \"\"; print \"## [\" v \"] - \" d; next }\n    { print }\n  ' CHANGELOG.md > CHANGELOG.md.tmp\n  mv CHANGELOG.md.tmp CHANGELOG.md\n\n  grep -q \"^## \\[$v\\] - \" CHANGELOG.md || die \"changelog transform failed: section header missing\"\n  [ -n \"$(extract_changelog_section \"$v\")\" ] || die \"changelog transform failed: section body is empty\"\n  info \"changelog: [Unreleased] moved into ## [$v] - $(date +%F)\"\n}\n\nstage_commit_push() {\n  local v=\"${1:-}\"\n  [ -n \"$v\" ] || die \"usage: $0 commit-push <X.Y.Z>\"\n  validate_full_version \"$v\"\n  require_repo_root\n  require_tools\n\n  local msg=\"chore(release): bump version to v$v\"\n  if [ \"$(git log -1 --format=%s)\" = \"$msg\" ] && [ -z \"$(dirty_files)\" ] && [ \"$(git rev-parse HEAD)\" = \"$(git rev-parse origin/dev)\" ]; then\n    info \"commit-push: release commit already made and pushed — waiting for CI\"\n    wait_for_dev_ci\n    return 0\n  fi\n\n  [ \"$(current_version)\" = \"$v\" ] || die \"pyproject.toml does not carry $v — run the bump stage first\"\n  local f\n  for f in $(dirty_files); do\n    case \"$f\" in\n      pyproject.toml|uv.lock|CHANGELOG.md) ;;\n      *) die \"unexpected working-tree change: $f — the release commit must be exactly pyproject.toml, uv.lock, CHANGELOG.md\" ;;\n    esac\n  done\n\n  if [ \"$DRY_RUN\" -eq 1 ]; then\n    info \"[dry-run] would commit the dirty release files as '$msg' and push dev\"\n    return 0\n  fi\n\n  git add pyproject.toml uv.lock CHANGELOG.md\n  git commit -m \"$msg\"\n  git push origin dev\n  info \"release commit pushed to dev\"\n  wait_for_dev_ci\n  info \"commit-push: done (dev CI green)\"\n}\n\nstage_pr_create() {\n  local v=\"${1:-}\"\n  [ -n \"$v\" ] || die \"usage: $0 pr-create <X.Y.Z>\"\n  validate_full_version \"$v\"\n  require_repo_root\n  require_tools\n  [ \"$(current_version)\" = \"$v\" ] || die \"pyproject.toml does not carry $v — finish commit-push first\"\n\n  local pr_line pr_num pr_url\n  pr_line=$(gh pr list --base main --head dev --state open --json number,url --jq '.[0] | @tsv' 2>/dev/null || true)\n  if [ -n \"$pr_line\" ]; then\n    IFS=$'\\t' read -r pr_num pr_url <<<\"$pr_line\"\n    info \"resuming existing release PR: $pr_url\"\n  else\n    if [ \"$DRY_RUN\" -eq 1 ]; then\n      info \"[dry-run] would create PR dev->main 'Release v$v' with the changelog section as body, then wait for its checks\"\n      return 0\n    fi\n    local body_file\n    body_file=$(mktemp)\n    {\n      echo \"Release v$v (SOP $SOP_ID, step 6).\"\n      echo\n      extract_changelog_section \"$v\"\n    } >\"$body_file\"\n    pr_url=$(gh pr create --base main --head dev --title \"Release v$v\" --body-file \"$body_file\")\n    rm -f \"$body_file\"\n    pr_num=$(gh pr view \"$pr_url\" --json number --jq .number)\n    info \"created release PR: $pr_url\"\n  fi\n\n  wait_for_pr_checks \"$pr_num\"\n  info \"pr-create: done — PR $pr_url is green. Merge gate: present this PR to the maintainer, then run: $0 pr-merge $v\"\n}\n\nstage_pr_merge() {\n  local v=\"${1:-}\"\n  [ -n \"$v\" ] || die \"usage: $0 pr-merge <X.Y.Z>\"\n  validate_full_version \"$v\"\n  require_repo_root\n  require_tools\n\n  git fetch origin main dev --quiet\n  if [ \"$(git rev-parse origin/main)\" = \"$(git rev-parse origin/dev)\" ]; then\n    info \"pr-merge: main already equals dev — nothing to merge\"\n    return 0\n  fi\n\n  local pr_line pr_num\n  pr_line=$(gh pr list --base main --head dev --state open --json number --jq '.[0] | @tsv' 2>/dev/null || true)\n  [ -n \"$pr_line\" ] || die \"no open dev->main PR — run pr-create first (after the maintainer's merge gate)\"\n  pr_num=\"${pr_line%%$'\\t'*}\"\n\n  local out rc\n  out=$(gh pr checks \"$pr_num\" 2>&1) && rc=0 || rc=$?\n  [ \"$rc\" -eq 0 ] || { printf '%s\\n' \"$out\" >&2; die \"PR #$pr_num checks are not all green — do not merge\"; }\n\n  if [ \"$DRY_RUN\" -eq 1 ]; then\n    info \"[dry-run] would run: gh pr merge $pr_num --ff-only\"\n    return 0\n  fi\n\n  gh pr merge \"$pr_num\" --ff-only\n  git fetch origin main --quiet\n  [ \"$(git rev-parse origin/main)\" = \"$(git rev-parse origin/dev)\" ] || die \"after merge, origin/main != origin/dev — investigate before tagging\"\n  info \"pr-merge: done (fast-forward; the invariant holds)\"\n}\n\nstage_tag_push() {\n  local v=\"${1:-}\"\n  [ -n \"$v\" ] || die \"usage: $0 tag-push <X.Y.Z>\"\n  validate_full_version \"$v\"\n  require_repo_root\n  require_tools\n\n  if [ -n \"$(git ls-remote --tags origin \"refs/tags/v$v\")\" ]; then\n    info \"tag-push: tag v$v already exists on origin — nothing to do\"\n    return 0\n  fi\n  if [ -n \"$(git tag -l \"v$v\")\" ]; then\n    die \"local tag v$v exists but is not on origin — resolve manually (delete or push it)\"\n  fi\n\n  git fetch origin main --quiet\n  [ \"$(git rev-parse origin/main)\" = \"$(git rev-parse origin/dev)\" ] || die \"origin/main != origin/dev — finish pr-merge first (fast-forward invariant)\"\n\n  if [ \"$DRY_RUN\" -eq 1 ]; then\n    info \"[dry-run] would checkout main, pull --ff-only, tag v$v at main HEAD, push the tag, and switch back to dev\"\n    return 0\n  fi\n\n  git checkout main\n  git pull --ff-only origin main\n  git tag \"v$v\"\n  git push origin \"v$v\"\n  git checkout dev\n  info \"tag-push: done — WARNING: publication (publish.yml) has now started; the release is irreversible\"\n}\n\nstage_publish_wait() {\n  local v=\"${1:-}\"\n  [ -n \"$v\" ] || die \"usage: $0 publish-wait <X.Y.Z>\"\n  validate_full_version \"$v\"\n  require_repo_root\n  require_tools\n\n  local tag_sha\n  tag_sha=$(git rev-parse \"v$v^{commit}\" 2>/dev/null) || die \"tag v$v does not exist locally — fetch tags or run tag-push first\"\n\n  local line rid polls\n  polls=0\n  while :; do\n    line=$(gh run list --commit \"$tag_sha\" --workflow publish.yml --limit 1 --json databaseId,status --jq '.[0] | @tsv' 2>/dev/null || true)\n    if [ -n \"$line\" ]; then\n      rid=\"${line%%$'\\t'*}\"\n      wait_for_run \"$rid\" \"publish (v$v)\" \"$PUBLISH_TIMEOUT_MIN\"\n      local jobs\n      jobs=$(gh run view \"$rid\" --json jobs --jq '[.jobs[] | .name] | join(\", \")')\n      info \"publish-wait: done — jobs: $jobs\"\n      return 0\n    fi\n    polls=$((polls + 1))\n    if [ \"$polls\" -ge 10 ]; then\n      die \"no publish.yml run appeared for tag v$v within 150s\"\n    fi\n    sleep 15\n  done\n}\n\nstage_release_notes() {\n  local v=\"${1:-}\"\n  [ -n \"$v\" ] || die \"usage: $0 release-notes <X.Y.Z>\"\n  validate_full_version \"$v\"\n  require_repo_root\n  require_tools\n\n  local rel_json url assets\n  rel_json=$(gh release view \"v$v\" --json url,assets --jq '{url, n: (.assets | length)}' 2>/dev/null) || die \"GitHub Release v$v not found — the publish run's 'Make GitHub Release' job may have failed; check it before proceeding\"\n  url=$(gh release view \"v$v\" --json url --jq .url)\n  assets=$(gh release view \"v$v\" --json assets --jq '.assets | length')\n  [ \"$assets\" -ge 2 ] || die \"GitHub Release v$v has only $assets asset(s); expected sdist + wheel\"\n\n  local section\n  section=$(extract_changelog_section \"$v\")\n  [ -n \"$section\" ] || die \"no changelog section for v$v in CHANGELOG.md\"\n\n  local current_notes\n  current_notes=$(gh release view \"v$v\" --json body --jq -r .body)\n  if [ \"$current_notes\" = \"$section\" ]; then\n    info \"release-notes: already set — nothing to do\"\n  elif [ \"$DRY_RUN\" -eq 1 ]; then\n    info \"[dry-run] would set the release notes of $url to the v$v changelog section\"\n  else\n    local notes_file\n    notes_file=$(mktemp)\n    printf '%s\\n' \"$section\" >\"$notes_file\"\n    gh release edit \"v$v\" --notes-file \"$notes_file\"\n    rm -f \"$notes_file\"\n    info \"release-notes: set\"\n  fi\n\n  info \"----------------------------------------------------------------\"\n  info \"release v$v complete:\"\n  info \"  GitHub Release:  $url\"\n  info \"  PyPI:            https://pypi.org/project/$REPO_ROOT/$v/\"\n  info \"  TestPyPI:        https://test.pypi.org/project/$REPO_ROOT/$v/\"\n  info \"  MCP Registry:    https://registry.modelcontextprotocol.io/?q=io.github.dfch%2Fbiz-dfch-specmgr\"\n  info \"  SOP:             docs/sop/sop-$SOP_ID-perform-a-release-of-biz-dfch-specmgr.md\"\n}\n\nstage_status() {\n  local v=\"${1:-}\"\n  [ -n \"$v\" ] || die \"usage: $0 status <X.Y.Z>\"\n  validate_full_version \"$v\"\n  require_repo_root\n  require_tools\n  git fetch origin dev main --quiet 2>/dev/null || true\n\n  local mark detail\n  echo \"release status for v$v:\"\n\n  # 1. bump\n  if [ \"$(current_version)\" = \"$v\" ]; then mark=\"x\"; detail=\"pyproject.toml carries $v\"; else mark=\" \"; detail=\"pyproject.toml carries $(current_version)\"; fi\n  printf '  [%s] bump          %s\\n' \"$mark\" \"$detail\"\n\n  # 2. changelog\n  if grep -q \"^## \\[$v\\] - \" CHANGELOG.md; then\n    if unreleased_is_empty; then mark=\"x\"; detail=\"dated section present, [Unreleased] emptied\"; else mark=\"!\"; detail=\"dated section present but [Unreleased] still has content\"; fi\n  else mark=\" \"; detail=\"no dated section yet\"; fi\n  printf '  [%s] changelog     %s\\n' \"$mark\" \"$detail\"\n\n  # 3. commit-push\n  local msg=\"chore(release): bump version to v$v\"\n  local commit_sha\n  commit_sha=$(git log origin/dev --format='%H %s' 2>/dev/null | grep -m1 \" $msg\\$\" | awk '{print $1}' || true)\n  if [ -n \"$commit_sha\" ]; then\n    mark=\"x\"\n    detail=\"commit ${commit_sha:0:12} on origin/dev\"\n    local line\n    line=$(gh run list --branch dev --limit 1 --json status,conclusion --jq '.[0] | @tsv' 2>/dev/null || true)\n    if [ -n \"$line\" ]; then\n      detail=\"$detail; latest dev CI: ${line}\"\n    fi\n  else mark=\" \"; detail=\"release commit not on origin/dev\"; fi\n  printf '  [%s] commit-push   %s\\n' \"$mark\" \"$detail\"\n\n  # 4. PR / merge\n  local pr_line\n  pr_line=$(gh pr list --base main --head dev --state open --json number,url --jq '.[0] | @tsv' 2>/dev/null || true)\n  if [ -n \"$pr_line\" ]; then\n    mark=\"!\"; detail=\"open PR: $pr_line (merge gate pending?)\"\n  elif [ \"$(git rev-parse origin/main 2>/dev/null || true)\" = \"$(git rev-parse origin/dev 2>/dev/null || true)\" ]; then\n    mark=\"x\"; detail=\"main equals dev (merged)\"\n  else\n    mark=\" \"; detail=\"no open PR; main behind dev\"\n  fi\n  printf '  [%s] pr            %s\\n' \"$mark\" \"$detail\"\n\n  # 5. tag\n  if [ -n \"$(git ls-remote --tags origin \"refs/tags/v$v\" 2>/dev/null || true)\" ]; then\n    mark=\"x\"; detail=\"tag on origin\"\n  elif [ -n \"$(git tag -l \"v$v\")\" ]; then\n    mark=\"!\"; detail=\"local tag exists, not pushed\"\n  else\n    mark=\" \"; detail=\"no tag\"\n  fi\n  printf '  [%s] tag           %s\\n' \"$mark\" \"$detail\"\n\n  # 6. publish\n  local tag_sha pub_line\n  tag_sha=$(git rev-parse \"v$v^{commit}\" 2>/dev/null || true)\n  if [ -n \"$tag_sha\" ]; then\n    pub_line=$(gh run list --commit \"$tag_sha\" --workflow publish.yml --limit 1 --json status,conclusion --jq '.[0] | @tsv' 2>/dev/null || true)\n    if [ -n \"$pub_line\" ]; then mark=\"x\"; detail=\"run: $pub_line\"; else mark=\"!\"; detail=\"tag exists, no publish run found yet\"; fi\n  else mark=\" \"; detail=\"no publish run (no tag)\"; fi\n  printf '  [%s] publish       %s\\n' \"$mark\" \"$detail\"\n\n  # 7. release notes\n  if gh release view \"v$v\" --json url >/dev/null 2>&1; then\n    local assets notes_ok\n    assets=$(gh release view \"v$v\" --json assets --jq '.assets | length')\n    notes_ok=$(gh release view \"v$v\" --json body --jq -r .body)\n    if [ \"$notes_ok\" = \"$(extract_changelog_section \"$v\")\" ]; then mark=\"x\"; detail=\"release exists ($assets assets), notes set\"; else mark=\"!\"; detail=\"release exists ($assets assets), notes NOT yet set\"; fi\n  else\n    mark=\" \"; detail=\"no GitHub Release yet\"\n  fi\n  printf '  [%s] release-notes %s\\n' \"$mark\" \"$detail\"\n}\n\nstage_all() {\n  local arg=\"${1:-}\"\n  [ \"$DRY_RUN\" -eq 1 ] || { is_tty || die \"all mode is interactive (merge gate); in non-interactive contexts run the stages individually\"; }\n  local v\n  v=$(resolve_target \"$arg\")\n  info \"resolved target: v$v\"\n  stage_precheck \"$v\"\n  if [ \"$DRY_RUN\" -eq 0 ]; then\n    unreleased_is_empty || true\n    info \"note: all mode does NOT curate the changelog (SOP step 3 is an agent/manual step); [Unreleased] is taken as-is\"\n  fi\n  stage_bump \"$v\"\n  stage_changelog \"$v\"\n  stage_commit_push \"$v\"\n  stage_pr_create \"$v\"\n  if [ \"$DRY_RUN\" -eq 0 ]; then\n    confirm_or_die \"merge gate: PR is green — merge dev into main now (ff-only)?\"\n  fi\n  stage_pr_merge \"$v\"\n  stage_tag_push \"$v\"\n  stage_publish_wait \"$v\"\n  stage_release_notes \"$v\"\n}\n\n# --- dispatch ----------------------------------------------------------------\n\nmain() {\n  local stage=\"${1:-}\"\n  [ -n \"$stage\" ] || usage\n  shift || true\n  local a\n  for a in \"$@\"; do\n    case \"$a\" in\n      --dry-run) DRY_RUN=1 ;;\n      *)\n        [ -z \"$VERSION_ARG\" ] || die \"at most one positional argument (got: $VERSION_ARG and $a)\"\n        VERSION_ARG=\"$a\"\n        ;;\n    esac\n  done\n\n  case \"$stage\" in\n    resolve) stage_resolve \"$VERSION_ARG\" ;;\n    precheck) stage_precheck \"$VERSION_ARG\" ;;\n    bump) stage_bump \"$VERSION_ARG\" ;;\n    changelog) stage_changelog \"$VERSION_ARG\" ;;\n    commit-push) stage_commit_push \"$VERSION_ARG\" ;;\n    pr-create) stage_pr_create \"$VERSION_ARG\" ;;\n    pr-merge) stage_pr_merge \"$VERSION_ARG\" ;;\n    tag-push) stage_tag_push \"$VERSION_ARG\" ;;\n    publish-wait) stage_publish_wait \"$VERSION_ARG\" ;;\n    release-notes) stage_release_notes \"$VERSION_ARG\" ;;\n    status) stage_status \"$VERSION_ARG\" ;;\n    all) stage_all \"$VERSION_ARG\" ;;\n    help|-h|--help) usage ;;\n    *) die \"unknown stage: $stage\"\n      usage\n    ;;\n  esac\n}\n\nmain \"$@\"\n"
}
```

**Output:**

```
Wrote file successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 90.8s)

_Thinking:_

Next, I'll run chmod +x, do a syntax check with bash -n, and execute the safe verification stages (Phase 4 for this script portion):

01. `bash -n scripts/release.sh`
02. `scripts/release.sh` (no arguments) → usage (exit 2)
03. Non-TTY with no version specified: `scripts/release.sh resolve </dev/null` → should die with "version required in non-interactive mode" — wait, `resolve` with no argument + non-TTY: resolve_target dies. But in main's dispatch: stage_resolve "$VERSION_ARG" with VERSION_ARG="" → resolve_target "" → non-TTY → die.
04. `scripts/release.sh resolve minor` → outputs 0.15.0
05. `scripts/release.sh resolve 0.15.0` → outputs 0.15.0
06. `scripts/release.sh resolve 0.14.0` → die "already carries"
07. `scripts/release.sh precheck 0.15.0` → should pass all checks (tree is clean, dev, main is ancestor, CI green (is the latest dev CI green? The last push 79b3951 triggered a CI run — it might still be running! In that case, precheck will wait for it. That's fine, it'll get polled. Hmm, that could take several minutes. For now let's just run it and see — if CI is running, precheck will block until it goes green (up to 40 minutes). It's probably already done or close to done. Let's first check the CI status of the latest dev run with `gh run list --branch dev --limit 1`.
08. `scripts/release.sh status 0.15.0` → all pending
09. `scripts/release.sh bump 0.15.0 --dry-run` → outputs the intent
10. `scripts/release.sh changelog 0.15.0 --dry-run` → wait, changelog's dry-run: asserts dirty is a subset (tree is clean so no problem), checks existing section (none), checks unreleased_is_empty → not empty (there's content) → dry-run outputs the intent. Good.
11. `scripts/release.sh pr-create 0.15.0 --dry-run` → dies early: current_version != 0.15.0 → "finish commit-push first". That's the expected behavior (dry-run after mutation stages requires those to be done). No problem.
12. shellcheck? Probably not installed; try `command -v shellcheck`.

First let me check the state of dev CI, then run the tests in a batch.

Making it executable, syntax-checking, and running the safe verification stages:

**Tool: bash**

**Input:**

```json
{
  "command": "chmod +x scripts/release.sh && bash -n scripts/release.sh && echo \"syntax OK\"; command -v shellcheck || echo \"no shellcheck\""
}
```

**Output:**

```
syntax OK
no shellcheck

```

**Tool: bash**

**Input:**

```json
{
  "command": "gh run list --branch dev --limit 1 --json status,conclusion,displayTitle --jq '.' 2>/dev/null || gh run list --branch dev --limit 1 --json status,conclusion,title"
}
```

**Output:**

```
unknown flag: --branch

Usage:  gh run list [flags]

Flags:
  -q, --jq expression     Filter JSON output using a jq expression
      --json fields       Output JSON with the specified fields
  -L, --limit int         Maximum number of runs to fetch (default 20)
  -t, --template string   Format JSON output using a Go template
  -w, --workflow string   Filter runs by workflow
  

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 86.5s)

_Thinking:_

`gh run list --branch` is not supported in this version of gh! The available flags are only: --jq, --json, --limit, --template, --workflow. So `--branch` can't be used. A different approach is needed to find the latest run on the dev branch.

Options:

- `gh run list --limit N` returns runs across all branches. Each run's JSON includes `headBranch` and `headSha`. So: fetch the most recent 10 runs, filter by headBranch == dev (and ideally headSha == origin/dev), and pick the first match.

Let's check the available JSON fields: in addition to the standard ones (databaseId, status, conclusion, headBranch, headSha, event, title, url, createdAt), displayTitle might not exist. Let me quickly test it.

Also, `gh run view --json url` worked previously (I used it in a prior command... actually, I used `--json status,conclusion` and `--json url` in the earlier plan — in previous sessions I used `gh pr view --json ...` a lot. Let me verify that `gh run list`'s JSON fields work with headBranch/headSha).

Fixes needed in the script:

1. The CI check in `stage_precheck`: replace `gh run list --branch dev --limit 1 ...` with `gh run list --limit 20 --json databaseId,headSha,headBranch,status,conclusion`, filter for headBranch==dev, and take the first entry (the list is in newest-first order).
2. `wait_for_dev_ci`: same filter, match by headSha == origin/dev.
3. The commit-push probe in `stage_status`: same filter.

Let me write a helper `latest_dev_run_json()`:

```bash
latest_dev_run() {
  gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == "dev")] | .[0] // empty'
}
```

This returns a JSON object or empty. Then parse it as needed.

For the line format: `... | .[0] // empty | [.databaseId, .headSha, .status, (.conclusion // "")] | @tsv`.

Let me test the fields in this gh version.

This `gh` version lacks `--branch` on `run list` — checking what JSON fields are available to filter by branch instead:

**Tool: bash**

**Input:**

```json
{
  "command": "gh run list --limit 5 --json databaseId,headSha,headBranch,status,conclusion,event,title 2>&1 | head -30"
}
```

**Output:**

```
Unknown JSON field: "title"
Available fields:
  conclusion
  createdAt
  databaseId
  event
  headBranch
  headSha
  name
  status
  updatedAt
  url
  workflowDatabaseId

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 63.1s)

_Thinking:_

Available fields: conclusion, createdAt, databaseId, event, headBranch, headSha, name, status, updatedAt, url, workflowDatabaseId. "title" is not allowed, but "name" is.

Let's test filtering by headBranch:

**Tool: bash**

**Input:**

```json
{
  "command": "gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == \"dev\")] | .[0:3] | .[] | [.databaseId, (.headSha[0:12]), .status, (.conclusion // \"-\")] | @tsv'"
}
```

**Output:**

```
33396976281	79b39515a4b0	completed	success
33390194254	1a0daf3d19d8	completed	success
33389532271	03260fe0e83f	completed	success

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 108.9s)

_Thinking:_

The headBranch filter works, and the latest dev run (79b3951 — the SOP commit I just pushed) is `completed/success`.

Next, fix the script: replace the 3 places that use `--branch dev` with a helper that filters by `headBranch == "dev"`:

1. `stage_precheck` — the "latest dev CI run" check
2. `wait_for_dev_ci` — discovering a run matching origin/dev's head
3. `stage_status` — the commit-push CI probe

Add a helper:

```bash
# Output the tsv "databaseId headSha status conclusion" of the latest dev run
# (newest first), or output nothing if none exists.
latest_dev_run_tsv() {
  gh run list --limit 30 --json databaseId,headSha,status,conclusion \
    --jq '[.[] | select(.headBranch == "dev")] | .[0] // empty | [.databaseId, .headSha, .status, (.conclusion // "")] | @tsv' 2>/dev/null || true
}
```

Wait — the `--jq` that uses select needs headBranch in the --json field list. Include it in the field list.

For precheck:

```bash
local line
line=$(latest_dev_run_tsv)
[ -n "$line" ] || die "no CI runs found on dev"
local rid sha status conclusion
IFS=$'\t' read -r rid sha status conclusion <<<"$line"
if [ "$status" != "completed" ]; then
  info "latest dev CI run still in flight (status: $status) — waiting"
  wait_for_run "$rid" "dev CI (in-flight)" "$DEV_CI_TIMEOUT_MIN"
else
  [ "$conclusion" = "success" ] || die "latest dev CI run is not green (conclusion: ${conclusion:-none})"
  info "latest dev CI run is green"
fi
```

For wait_for_dev_ci:

```bash
wait_for_dev_ci() {
  local head_sha line rid sha polls
  head_sha=$(git rev-parse origin/dev)
  info "waiting for a CI run to appear on dev head ${head_sha:0:12} ..."
  polls=0
  while :; do
    line=$(latest_dev_run_tsv)
    if [ -n "$line" ]; then
      IFS=$'\t' read -r rid sha status conclusion <<<"$line"
      if [ "$sha" = "$head_sha" ]; then
        wait_for_run "$rid" "dev CI" "$DEV_CI_TIMEOUT_MIN"
        return 0
      fi
    fi
    polls=$((polls + 1))
    if [ "$polls" -ge 10 ]; then
      die "no CI run appeared for dev head $head_sha within 150s"
    fi
    sleep 15
  done
}
```

For status's commit-push probe:

```bash
local line
line=$(latest_dev_run_tsv)
if [ -n "$line" ]; then
  IFS=$'\t' read -r _ _ status conclusion <<<"$line"
  detail="$detail; latest dev CI: $status${conclusion:+/$conclusion}"
fi
```

Hmm, `read -r _ _ status conclusion` — `_` as a variable name is fine.

Let's apply the edits to the script.

Latest dev CI is green (`79b3951` — the SOP commit). Fixing the script's three `--branch dev` usages with a `headBranch`-filtering helper:

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "# Wait until a dev run exists for the current origin/dev head, then for it to pass.\nwait_for_dev_ci() {\n  local head_sha line rid sha polls\n  head_sha=$(git rev-parse origin/dev)\n  info \"waiting for a CI run to appear on dev head ${head_sha:0:12} ...\"\n  polls=0\n  while :; do\n    line=$(gh run list --branch dev --limit 1 --json databaseId,headSha --jq '.[0] | @tsv') || die \"cannot list runs\"\n    rid=\"${line%%$'\\t'*}\"\n    sha=\"${line#*$'\\t'}\"\n    if [ \"$sha\" = \"$head_sha\" ]; then\n      wait_for_run \"$rid\" \"dev CI\" \"$DEV_CI_TIMEOUT_MIN\"\n      return 0\n    fi\n    polls=$((polls + 1))\n    if [ \"$polls\" -ge 10 ]; then\n      die \"no CI run appeared for dev head $head_sha within 150s\"\n    fi\n    sleep 15\n  done\n}",
  "newString": "# Print \"databaseId headSha status conclusion\" (tab-separated) for the newest\n# dev-branch run, or nothing if none exists. (This gh version has no\n# 'gh run list --branch' flag, hence the headBranch filter.)\nlatest_dev_run_tsv() {\n  gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion \\\n    --jq '[.[] | select(.headBranch == \"dev\")] | .[0] // empty\n          | [.databaseId, .headSha, .status, (.conclusion // \"\")] | @tsv' 2>/dev/null || true\n}\n\n# Wait until a dev run exists for the current origin/dev head, then for it to pass.\nwait_for_dev_ci() {\n  local head_sha line rid sha status polls\n  head_sha=$(git rev-parse origin/dev)\n  info \"waiting for a CI run to appear on dev head ${head_sha:0:12} ...\"\n  polls=0\n  while :; do\n    line=$(latest_dev_run_tsv)\n    if [ -n \"$line\" ]; then\n      IFS=$'\\t' read -r rid sha status _ <<<\"$line\"\n      if [ \"$sha\" = \"$head_sha\" ]; then\n        wait_for_run \"$rid\" \"dev CI\" \"$DEV_CI_TIMEOUT_MIN\"\n        return 0\n      fi\n    fi\n    polls=$((polls + 1))\n    if [ \"$polls\" -ge 10 ]; then\n      die \"no CI run appeared for dev head $head_sha within 150s\"\n    fi\n    sleep 15\n  done\n}"
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 75.0s)

_Thinking:_

Wait, `IFS=$'\t' read -r rid sha status _ <<<"$line"` — the fourth field is `conclusion` (possibly empty). I used `_` for that. But be careful: if conclusion is empty, the line will be "rid\\tsha\\tstatus\\t" — read will set `_`="" — no problem.

Next, fix precheck and status.

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "  local line rid sha status conclusion\n  line=$(gh run list --branch dev --limit 1 --json databaseId,headSha,status,conclusion --jq '.[0] | @tsv') || die \"cannot list dev runs\"\n  IFS=$'\\t' read -r rid sha status conclusion <<<\"$line\"\n  if [ \"$status\" != \"completed\" ]; then",
  "newString": "  local line rid status conclusion\n  line=$(latest_dev_run_tsv)\n  [ -n \"$line\" ] || die \"no CI runs found on dev\"\n  IFS=$'\\t' read -r rid _ status conclusion <<<\"$line\"\n  if [ \"$status\" != \"completed\" ]; then"
}
```

**Output:**

```
Edit applied successfully.
```

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "    mark=\"x\"\n    detail=\"commit ${commit_sha:0:12} on origin/dev\"\n    local line\n    line=$(gh run list --branch dev --limit 1 --json status,conclusion --jq '.[0] | @tsv' 2>/dev/null || true)\n    if [ -n \"$line\" ]; then\n      detail=\"$detail; latest dev CI: ${line}\"\n    fi",
  "newString": "    mark=\"x\"\n    detail=\"commit ${commit_sha:0:12} on origin/dev\"\n    local line s c\n    line=$(latest_dev_run_tsv)\n    if [ -n \"$line\" ]; then\n      IFS=$'\\t' read -r _ _ s c <<<\"$line\"\n      detail=\"$detail; latest dev CI: ${s}${c:+/$c}\"\n    fi"
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 75.6s)

_Thinking:_

Next, I'll re-run the syntax check and execute the verification battery (all safe / no changes):

01. `bash -n`
02. No arguments → usage, exit 2
03. Unknown stage → error
04. `resolve minor` (non-TTY via bash tool) → 0.15.0
05. `resolve 0.15.0` → 0.15.0
06. `resolve 0.14.0` → die "already carries"
07. `resolve` with no version, non-TTY → die "version required"
08. `precheck 0.15.0` → should pass everything (tree is clean; CI is green)
09. `status 0.15.0` → all pending
10. `bump 0.15.0 --dry-run` → outputs intent, no changes
11. `changelog 0.15.0 --dry-run` → outputs intent, no changes
12. Confirm tree is still clean after dry runs (git status)

Batch 1 (fast, parallel-safe — all read-only or no-mutation): run in a few bash calls.

Re-checking syntax and running the verification battery:

**Tool: bash**

**Input:**

```json
{
  "command": "bash -n scripts/release.sh && echo \"syntax OK\" && scripts/release.sh; echo \"exit=$?\""
}
```

**Output:**

```
syntax OK
Staged release automation for biz.dfch.SpecMgr.

Deterministic projection of the normative SOP "Perform a release of
biz.dfch.SpecMgr" (SOP 98537416-0e6e-4a02-925f-974a17bfa10a,
docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md).
Where this script and the SOP disagree, the SOP wins: fix the script.

Usage: scripts/release.sh <stage> [X.Y.Z | patch | minor | major] [--dry-run]

Stages (mirror the SOP's 9 procedure steps; every stage is idempotent):
  resolve       compute and print the target version (no mutation)
  precheck      fail-fast pre-release checks (SOP step 2)
  bump          pyproject.toml + uv.lock version bump (SOP step 4)
  changelog     move [Unreleased] into a dated section (SOP step 5a)
  commit-push   commit the 3 release files, push dev, wait for CI (SOP step 5b)
  pr-create     open the dev->main release PR, wait for checks (SOP step 6a)
  pr-merge      ff-only merge of the release PR (SOP step 6b, after the merge gate)
  tag-push      tag vX.Y.Z on main, push the tag, back to dev (SOP step 7)
  publish-wait  wait for the 4 publish.yml jobs (SOP step 8)
  release-notes verify the release + set the GitHub Release notes (SOP step 9)
  status        read-only: where does this release stand?
  all           resolve + precheck + bump + changelog + commit-push +
                pr-create + [TTY merge gate] + pr-merge + tag-push +
                publish-wait + release-notes (no agent curation: the
                [Unreleased] section must already be curated)

Only `resolve` and `all` accept bump keywords; all other stages take the
full resolved version.

exit=2

```

**Tool: bash**

**Input:**

```json
{
  "command": "echo \"--- resolve minor:\"; scripts/release.sh resolve minor; echo \"--- resolve 0.15.0:\"; scripts/release.sh resolve 0.15.0; echo \"--- resolve 0.14.0 (expect die):\"; scripts/release.sh resolve 0.14.0; echo \"exit=$?\"; echo \"--- resolve noarg nontty (expect die):\"; scripts/release.sh resolve </dev/null; echo \"exit=$?\""
}
```

**Output:**

```
--- resolve minor:
0.15.0
--- resolve 0.15.0:
0.15.0
--- resolve 0.14.0 (expect die):
release: ERROR: pyproject.toml already carries 0.14.0 (no re-bump; use status <v> to see where the release stands)
exit=1
--- resolve noarg nontty (expect die):
release: ERROR: version required in non-interactive mode: scripts/release.sh <stage> <X.Y.Z|patch|minor|major>
exit=1

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 71.5s)

_Thinking:_

All resolve paths work. `usage` outputs the header comment (lines 2–30 via sed) — looks clean.

Note: the usage output includes the "Where this script and the SOP disagree" line and so on. Good.

Next: precheck, status, dry run. precheck requires gh + a fetch — should pass. Running:

- `scripts/release.sh precheck 0.15.0`
- `scripts/release.sh status 0.15.0`
- `scripts/release.sh bump 0.15.0 --dry-run`
- `scripts/release.sh changelog 0.15.0 --dry-run`
- `git status --porcelain` (must remain empty)

All `resolve` paths behave correctly. Now precheck, status, and the dry-runs:

**Tool: bash**

**Input:**

```json
{
  "command": "scripts/release.sh precheck 0.15.0; echo \"exit=$?\""
}
```

**Output:**

```
release: target: v0.15.0
release: ERROR: working tree is not clean:
exit=1

```

**Tool: bash**

**Input:**

```json
{
  "command": "scripts/release.sh status 0.15.0; echo \"exit=$?\""
}
```

**Output:**

```
release status for v0.15.0:
  [ ] bump          pyproject.toml carries 0.14.0
  [ ] changelog     no dated section yet
  [ ] commit-push   release commit not on origin/dev
  [ ] pr            no open PR; main behind dev
  [ ] tag           no tag
  [!] publish       tag exists, no publish run found yet
  [ ] release-notes no GitHub Release yet
exit=0

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 130.6s)

_Thinking:_

Two problems discovered:

1. **precheck: "working tree is not clean"** — but the `git status --porcelain` I just ran was... wait, the tree should be clean, right? Let me verify: the SOP commit + push is done. Did I create something? `scripts/release.sh` is a new untracked file! I wrote it but haven't committed it yet. Untracked files show up in `git status --porcelain` (`?? scripts/release.sh`). My precheck requires a fully clean tree, including no untracked files.

   Design question: should precheck tolerate untracked files? No — untracked files aren't a problem for the release (git add only adds 3 files, and commit only commits staged files). Untracked files don't get mixed into the release commit. The danger is *modified tracked* files. Therefore precheck should fail on modified/staged tracked files, but tolerate untracked ones (or at least just warn). But `dirty_files()` is also used for subset assertions in bump/changelog/commit-push — untracked `??` lines will end up in the list. In the commit-push assertion, the untracked scripts/release.sh will get caught by "unexpected working-tree change" — wrong!

   Fix: in all dirty-state checks, exclude untracked files (porcelain lines starting with `??`). Modify `dirty_files()` to output only tracked changes: `git status --porcelain | grep -v '^??' | awk '{print $NF}'`. And in precheck, warn (don't fail) if untracked files exist — actually, just silently ignoring them is fine too; simpler: dirty = tracked changes only; precheck requires dirty to be empty. Untracked files are tolerated everywhere (they can't get mixed into the release commit).

   Hmm, wait — but is that completely safe? `git add pyproject.toml uv.lock CHANGELOG.md` — explicit paths, so no. Safe.

2. **status: "[!] publish tag exists, no publish run found yet"** — bug in my status logic: the `tag` probe said "no tag" (correct), but the publish probe says "tag exists"?? Looking at my code:

   ```bash
   tag_sha=$(git rev-parse "v$v^{commit}" 2>/dev/null || true)
   if [ -n "$tag_sha" ]; then
   ```

   `git rev-parse v0.15.0^{commit}` — if the tag doesn't exist, rev-parse outputs nothing and returns non-zero → `|| true` → tag_sha should be empty... unless `git rev-parse "v0.15.0^{commit}"` — hmm, wait: does `v0.15.0^{commit}` somehow get parsed? No. Let me test: with the tag not existing, `git rev-parse 'v0.15.0^{commit}'` → error "unknown revision", exit 128, no stdout. So tag_sha="" → should enter the else branch "no publish run (no tag)". But the output was "[!] publish tag exists, no publish run found yet" — meaning tag_sha was non-empty?!

   Ah, wait. I got it — inside `$( ... || true)`, rev-parse's error goes to stderr (suppressed by 2>/dev/null), and stdout is empty. Hmm, then it should be empty...

   Let me look at my status code again:

   ```bash
   local tag_sha pub_line
   tag_sha=$(git rev-parse "v$v^{commit}" 2>/dev/null || true)
   ```

   Hmm — is it possible that `v0.15.0^{commit}` matches something? No, it's not a ref.

   Wait, actually — look at the tag probe output: "[ ] tag no tag". So `git ls-remote --tags origin refs/tags/v0.15.0` is empty and `git tag -l v0.15.0` is also empty. Consistent: no tag. But then tag_sha... let me just run `git rev-parse 'v0.15.0^{commit}'` and check what it outputs.

   Actually — I think the problem is this: under `set -e`, `local tag_sha pub_line` and then `tag_sha=$(cmd || true)` — this is fine. Let me debug directly.

   Hmm wait, there's another subtle point: `git rev-parse "v0.15.0^{commit}"` — `^{commit}` is a peel suffix. For a non-existent ref, rev-parse fails... but for `v0.15.0`, git might try... no, it doesn't.

   Let me test in the shell.

Also, in the precheck output, "working tree is not clean:" is followed by an empty line — the `git status --porcelain >&2` output should have shown the untracked file... it output `?? scripts/release.sh`? In the captured output, nothing is visible after "not clean:" — actually the output shows an empty line; maybe the `?? scripts/release.sh` line was output... I see an empty line — strange. Oh wait, `git status --porcelain >&2` — the bash tool merges stderr into the output; an empty line is displayed. Hmm, `?? scripts/release.sh` should be shown. Maybe... it was shown but got cut off? The output block ends with "exit=1" after an empty line. Strange. Let me check git status directly.

Let me debug both.

Two issues found: precheck chokes on the untracked `scripts/release.sh`, and `status` misreports the publish line. Debugging:

**Tool: bash**

**Input:**

```json
{
  "command": "git status --porcelain; echo ---; git rev-parse 'v0.15.0^{commit}'; echo \"rc=$?\""
}
```

**Output:**

```
?? scripts/
---
v0.15.0^{commit}
rc=128
fatal: ambiguous argument 'v0.15.0^{commit}': unknown revision or path not in the working tree.
Use '--' to separate paths from revisions, like this:
'git <command> [<revision>...] -- [<file>...]'

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 181.8s)

_Thinking:_

Debug findings:

1. `git status --porcelain` shows `?? scripts/` — untracked directory (git collapses it). The precheck correctly detected it as "not clean". Design fix: allow untracked files (since they can't sneak into a release commit), fail only on changes to tracked files.

2. `git rev-parse 'v0.15.0^{commit}'` returns rc=128, and stdout is empty… wait, in the output "v0.15.0^{commit}" is shown on the first line?! No — look carefully:

```
---
v0.15.0^{commit}
rc=128
fatal: ambiguous argument ...
```

Hmm, that first line after `---`… the command was `git rev-parse 'v0.15.0^{commit}'; echo "rc=$?"`. So `git rev-parse` output `v0.15.0^{commit}` to stdout?? That can't be right — unless… oh! `git rev-parse` has a special behavior: for arguments it can't resolve as revisions, does it try other formats? Actually yes — `git rev-parse` falls back to treating arguments as *revisions with output format*, or if the argument looks like a valid object name… no, that's not it. The actual behavior: `git rev-parse <arg>` tries: a raw SHA, a ref, a ref with `^{...}` peel… and if none of those work, it outputs the argument as-is in certain cases? Hmm, actually `git rev-parse --verify` would fail, but plain `git rev-parse` without `--verify` has lenient behavior: if the argument matches no revision, it gets output as-is (treated as "already resolved"). That's it! Plain `git rev-parse` without `--verify` outputs unknown arguments unchanged (that's why people use `--verify`).

So in my status code: `tag_sha=$(git rev-parse "v$v^{commit}" 2>/dev/null || true)` → outputs `v0.15.0^{commit}` (the literal string!) → non-empty → "tag exists" branch. Bug confirmed.

Fix: use `git rev-parse --verify --quiet "v$v^{commit}"` — with `--verify`, it fails cleanly (no output) for unknown revisions. Or better yet: check tag existence first:

```bash
if git rev-parse --verify --quiet "refs/tags/v$v" >/dev/null; then
  tag_sha=$(git rev-parse --verify "refs/tags/v$v^{commit}")
  ...
else
  no-tag branch
fi
```

Same fix for `stage_publish_wait`: `tag_sha=$(git rev-parse "v$v^{commit}" 2>/dev/null) || die ...` — wait, in publish_wait I wrote `tag_sha=$(git rev-parse "v$v^{commit}" 2>/dev/null) || die "tag v$v does not exist locally..."` — but without --verify, rev-parse outputs the literal string and returns rc=0 (no error!), so `|| die` doesn't fire, and tag_sha becomes the literal `v0.15.0^{commit}` → `gh run list --commit "v0.15.0^{commit}"` → gh fails with "unknown commit"… then `line=$(... || true)` is empty → "no publish.yml run appeared... within 150s" die. Confusing failure. Fix both with `--verify --quiet`.

3. Untracked-tolerance fix:

- `dirty_files()`: `git status --porcelain | grep -v '^??' | awk '{print $NF}'` — hmm, for a path containing a space, the porcelain format `M path with space` → $NF is only the last word! Need to strip the first 2 chars + space: `sed 's/^...//'`. Porcelain v1 format: XY<space>path. So: `awk '{print substr($0, 4)}'`? For rename `R  old -> new`, field 4 onward is "old -> new". Edge case, but for our purposes (only the 3 known files can be dirty), use `sed 's/^.[[:space:]].*[[:space:]]//'`… simpler and more robust: `git status --porcelain=v1 | sed -n 's/^....//'` hmm.

  Let's just do: `git diff --name-only` (tracked changes: staged + unstaged vs HEAD) — this is exactly what we want (modified files), and untracked is never included. `git diff --name-only` = worktree vs index; `git diff --name-only HEAD` = worktree vs HEAD (includes staged). Use `git diff --name-only HEAD`. Rename handling: only outputs new name? `git diff --name-only HEAD` outputs the new path for renames. Good enough.

- precheck clean check: `[ -z "$(git diff --name-only HEAD)" ]` → die on changes to tracked files; optionally warn on untracked: count `git status --porcelain | grep -c '^??'` → info "note: N untracked path(s) ignored (not part of the release)".

Let me apply the fixes:

a) `dirty_files()`:

```bash
dirty_files() {
  git diff --name-only HEAD
}
```

(only tracked changes; untracked is intentionally ignored — see precheck note)

b) precheck:

```bash
  local untracked
  untracked=$(git status --porcelain | grep -c '^??' || true)
  [ -z "$(dirty_files)" ] || { die "working tree has modified tracked files:"; git status --porcelain >&2; }
  if [ "$untracked" -gt 0 ]; then info "note: $untracked untracked path(s) ignored (untracked files cannot enter the release commit)"; fi
```

c) publish_wait:

```bash
  git rev-parse --verify --quiet "refs/tags/v$v" >/dev/null || die "tag v$v does not exist locally — fetch tags or run tag-push first"
  local tag_sha
  tag_sha=$(git rev-parse --verify "refs/tags/v$v^{commit}")
```

d) status tag probe + publish probe:

```bash
  # 5. tag
  if [ -n "$(git ls-remote --tags origin "refs/tags/v$v" 2>/dev/null || true)" ]; then
    mark="x"; detail="tag on origin"
  elif git rev-parse --verify --quiet "refs/tags/v$v" >/dev/null; then
    mark="!"; detail="local tag exists, not pushed"
  else
    mark=" "; detail="no tag"
  fi
```

Note: the original used `git tag -l v$v` — fine for local, but let's keep it as `git tag -l`… simpler to keep both consistent: local check via `git rev-parse --verify --quiet refs/tags/v$v`.

```bash
  # 6. publish
  local tag_sha pub_line
  if git rev-parse --verify --quiet "refs/tags/v$v" >/dev/null; then
    tag_sha=$(git rev-parse --verify "refs/tags/v$v^{commit}")
    pub_line=$(gh run list --commit "$tag_sha" --workflow publish.yml --limit 1 --json status,conclusion --jq '.[0] | @tsv' 2>/dev/null || true)
    ...
```

Applying the edits now.

Identified the causes: (1) Untracked files cannot be mixed into the release commit (since we only `git add` three explicit paths), so the check should target only *tracked* modifications; (2) A bare `git rev-parse` without `--verify` **outputs unknown arguments as-is** — that's the cause of the false detection. Fixing all four locations:

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "# List of dirty files (paths only), empty if clean.\ndirty_files() {\n  git status --porcelain | awk '{print $NF}'\n}",
  "newString": "# Tracked files differing from HEAD (staged or unstaged); untracked paths are\n# deliberately excluded — the release commit stages exactly three explicit\n# paths, so untracked files cannot enter it.\ndirty_files() {\n  git diff --name-only HEAD\n}"
}
```

**Output:**

```
Edit applied successfully.
```

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "  [ -z \"$(dirty_files)\" ] || die \"working tree is not clean:\"\n  git status --porcelain >&2",
  "newString": "  [ -z \"$(dirty_files)\" ] || { die \"working tree has modified tracked files:\"; git status --porcelain >&2; }\n  local untracked\n  untracked=$(git status --porcelain | grep -c '^??' || true)\n  if [ \"$untracked\" -gt 0 ]; then\n    info \"note: $untracked untracked path(s) ignored (untracked files cannot enter the release commit)\"\n  fi"
}
```

**Output:**

```
Edit applied successfully.
```

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "  local tag_sha\n  tag_sha=$(git rev-parse \"v$v^{commit}\" 2>/dev/null) || die \"tag v$v does not exist locally — fetch tags or run tag-push first\"",
  "newString": "  git rev-parse --verify --quiet \"refs/tags/v$v\" >/dev/null || die \"tag v$v does not exist locally — fetch tags or run tag-push first\"\n  local tag_sha\n  tag_sha=$(git rev-parse --verify \"refs/tags/v$v^{commit}\")"
}
```

**Output:**

```
Edit applied successfully.
```

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "  # 5. tag\n  if [ -n \"$(git ls-remote --tags origin \"refs/tags/v$v\" 2>/dev/null || true)\" ]; then\n    mark=\"x\"; detail=\"tag on origin\"\n  elif [ -n \"$(git tag -l \"v$v\")\" ]; then\n    mark=\"!\"; detail=\"local tag exists, not pushed\"\n  else\n    mark=\" \"; detail=\"no tag\"\n  fi\n  printf '  [%s] tag           %s\\n' \"$mark\" \"$detail\"\n\n  # 6. publish\n  local tag_sha pub_line\n  tag_sha=$(git rev-parse \"v$v^{commit}\" 2>/dev/null || true)\n  if [ -n \"$tag_sha\" ]; then",
  "newString": "  # 5. tag\n  if [ -n \"$(git ls-remote --tags origin \"refs/tags/v$v\" 2>/dev/null || true)\" ]; then\n    mark=\"x\"; detail=\"tag on origin\"\n  elif git rev-parse --verify --quiet \"refs/tags/v$v\" >/dev/null; then\n    mark=\"!\"; detail=\"local tag exists, not pushed\"\n  else\n    mark=\" \"; detail=\"no tag\"\n  fi\n  printf '  [%s] tag           %s\\n' \"$mark\" \"$detail\"\n\n  # 6. publish\n  local tag_sha pub_line\n  tag_sha=\"\"\n  if git rev-parse --verify --quiet \"refs/tags/v$v\" >/dev/null; then\n    tag_sha=$(git rev-parse --verify \"refs/tags/v$v^{commit}\")\n  fi\n  if [ -n \"$tag_sha\" ]; then"
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 70.6s)

_Thinking:_

Next, re-run the verification battery:

- bash -n
- precheck 0.15.0 (should pass this time, with untracked notes)
- status 0.15.0 (the publish line should show "no publish run (no tag)")
- bump --dry-run
- changelog --dry-run
- confirm that no changes have been made (git diff --name-only HEAD is empty)

Re-running the battery:

**Tool: bash**

**Input:**

```json
{
  "command": "bash -n scripts/release.sh && scripts/release.sh precheck 0.15.0; echo \"precheck exit=$?\""
}
```

**Output:**

```
release: target: v0.15.0
release: note: 1 untracked path(s) ignored (untracked files cannot enter the release commit)
release: fast-forward invariant holds (main is an ancestor of dev)
release: latest dev CI run is green
release: tag v0.15.0 does not exist yet
release: uv.lock is in sync
release: precheck: all checks passed for v0.15.0
precheck exit=0

```

**Tool: bash**

**Input:**

```json
{
  "command": "scripts/release.sh status 0.15.0 && echo === && scripts/release.sh bump 0.15.0 --dry-run && scripts/release.sh changelog 0.15.0 --dry-run && echo === && git diff --name-only HEAD && echo \"tree-clean-check: $? (empty above = clean)\""
}
```

**Output:**

```
release status for v0.15.0:
  [ ] bump          pyproject.toml carries 0.14.0
  [ ] changelog     no dated section yet
  [ ] commit-push   release commit not on origin/dev
  [ ] pr            no open PR; main behind dev
  [ ] tag           no tag
  [ ] publish       no publish run (no tag)
  [ ] release-notes no GitHub Release yet
===
release: [dry-run] would set pyproject.toml version 0.14.0 -> 0.15.0, then run 'uv lock'
release: ERROR: the [Unreleased] section is EMPTY — releasing with no documented changes is almost always a mistake. Continue with v0.15.0? (interactive confirmation required; re-run from a TTY)

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 123.5s)

_Thinking:_

Great progress:

- precheck: all green (with untracked notes)
- status: all correct now
- bump --dry-run: correct
- changelog --dry-run: hit the empty `[Unreleased]` confirmation path — and correctly aborted (non-interactive).

Wait — is `[Unreleased]` actually empty? Looking at the top of the CHANGELOG from earlier:

```
## [Unreleased]

## [0.14.0] - 2026-08-30
```

Yes! `[Unreleased]` is empty — the 0.14.0 release moved everything into the dated section, and nothing has been recorded since (recent work: sop domain, feat domain were recorded in the 0.14.0 section… no wait, the feat domain was 0.14.0 (released 2026-08-30), and sop was merged after that (today, ec3d644). So the SOP domain work is not in the changelog — [Unreleased] should describe the sop domain!

So in reality, the changelog for the next release (0.15.0) is not yet written: the SOP domain (feat-30) was merged after v0.14.0. This is exactly what SOP step 3 (agent curation) is for. The dry-run behavior (refusing empty section non-interactively) is correct.

So my dry-run test for changelog correctly demonstrated the guard. To test the conversion itself without dirtying the real tree, I could: temporarily add a fake entry to [Unreleased], run changelog --dry-run (should print intent), then restore. Or test the actual conversion on a scratch copy. The conversion is critical, so let's test it properly:

Test plan for changelog conversion (safe, local, reversible):

1. `git stash`? No — simpler: make a temp copy of the repo's CHANGELOG? The script operates on the cwd's CHANGELOG.md. Do this:
   - Add a test entry to [Unreleased]
   - Run `bump 0.15.0` for real? No — bump would change pyproject + uv.lock. I want to test changelog in isolation. The changelog stage only asserts that dirty files ⊆ {pyproject, uv.lock, CHANGELOG} — if I only dirty CHANGELOG, it passes (subset).
   - Run `changelog 0.15.0` (for real, not dry-run) → converts
   - Verify the top of the file: `## [Unreleased]` is empty, then `## [0.15.0] - 2026-08-31` with the test entry, then `## [0.14.0]`…
   - Then `git checkout -- CHANGELOG.md` to restore (and confirm the tree is clean again).

This tests the actual conversion end-to-end on a throwaway change.

Also test `bump` for real? That modifies pyproject.toml + uv.lock. Could do the same thing: run `bump 0.15.0` for real, verify, then restore both files. That would also validate uv lock behavior. Let's do bump for real, then restore. (uv lock takes a few seconds.)

Order:

1. `scripts/release.sh bump 0.15.0` (for real) → verify pyproject is 0.15.0, uv.lock diff is version-only → `git checkout -- pyproject.toml uv.lock`
2. Add fake [Unreleased] entry → `scripts/release.sh changelog 0.15.0` (for real) → verify structure → `git checkout -- CHANGELOG.md`

Wait — for step 2, the changelog stage asserts dirty ⊆ {pyproject, uv.lock, CHANGELOG.md}; dirty is only CHANGELOG → OK.

But note — in step 1, running bump for real: after restoring, uv.lock is back to 0.14.0 — but does `uv lock --check` still pass? After restoration, yes, since we restored both files to the committed state.

Also, the `git checkout --` restore: this is a write operation, but that's fine (build mode).

Let's run the tests.

All guards are functioning — and the `changelog` dry-run revealed the *real* state: `[Unreleased]` is actually empty. That's because the SOP domain (feat-30) was merged **after** v0.14.0, and its changelog entry hasn't been written yet — exactly what SOP step 3 (agent curation) is supposed to fill in before the actual release.

Next, let's test the actual `bump` and `changelog` transforms against throwaway changes (we'll revert them later):

**Tool: bash**

**Input:**

```json
{
  "command": "scripts/release.sh bump 0.15.0 && echo \"=== pyproject:\" && grep '^version' pyproject.toml && echo \"=== uv.lock diff:\" && git diff --unified=0 uv.lock && git checkout -- pyproject.toml uv.lock && echo \"restored\""
}
```

**Output:**

```
release: pyproject.toml: 0.14.0 -> 0.15.0
Resolved 95 packages in 1.35s
Updated biz-dfch-specmgr v0.14.0 -> v0.15.0
release: uv.lock: only the biz-dfch-specmgr version entry changed
release: bump: done (0.15.0)
=== pyproject:
version = "0.15.0"
=== uv.lock diff:
diff --git a/uv.lock b/uv.lock
index 41fbe22..ff51fd5 100644
--- a/uv.lock
+++ b/uv.lock
@@ -112 +112 @@ name = "biz-dfch-specmgr"
-version = "0.14.0"
+version = "0.15.0"
restored

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 67.6s)

_Thinking:_

`bump` works end-to-end: pyproject was updated, `uv lock` changed only the version line, and the assertion passed. Restored.

Next, test the changelog transformation: add a fake [Unreleased] entry, run `changelog 0.15.0` for real, verify the structure, and restore.

`bump` verified (exactly the version line in `uv.lock`). Now the changelog transform:

**Tool: bash**

**Input:**

```json
{
  "command": "sed -i '0,/^## \\[Unreleased\\]$/s//## [Unreleased]\\n\\n### Added\\n\\n- TEST-ENTRY: throwaway line to exercise the changelog transform./' CHANGELOG.md && scripts/release.sh changelog 0.15.0 && echo \"=== top of CHANGELOG after transform:\" && head -14 CHANGELOG.md && git checkout -- CHANGELOG.md && echo \"restored\""
}
```

**Output:**

```
release: ERROR: changelog transform failed: section body is empty

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 70.3s)

_Thinking:_

The transform failed with "section body is empty". Two possible causes:

1. My `sed -i '0,/.../s//.../'` insertion didn't work as expected (e.g., the TEST-ENTRY got inserted somewhere else, or in the wrong form).
2. There's a bug in `extract_changelog_section`.

Note: the transform itself ran (the header insertion part) — after which the verification failed. Since it died, the file is now in a "transformed" state, and the fake entry is inside the 0.15.0 section. Let me check the current top of CHANGELOG.md to see what happened.

The transform ran but its verification failed — inspecting the resulting state:

**Tool: bash**

**Input:**

```json
{
  "command": "head -18 CHANGELOG.md"
}
```

**Output:**

```
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.15.0] - 2026-08-31

### Added

- TEST-ENTRY: throwaway line to exercise the changelog transform.

## [0.14.0] - 2026-08-30

### Added

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 87.0s)

_Thinking:_

The conversion itself worked perfectly:

```
## [Unreleased]
(blank line)
## [0.15.0] - 2026-08-31
(blank line)
### Added

- TEST-ENTRY: ...
(blank line)
## [0.14.0] - 2026-08-30
```

So the bug is in `extract_changelog_section` — it returned empty for v0.15.0. Let me check my awk:

```awk
awk -v v="$1" '
    $0 == "## [" v "] - " { found = 1; next }
    found && /^## / { exit }
    found && $0 ~ /^[[:space:]]*$/ && !started { next }
    found { started = 1; print }
  ' CHANGELOG.md
```

The line is `## [0.15.0] - 2026-08-31` — but my match pattern is `$0 == "## [" v "] - "` — an exact match against a prefix?! `==` compares the entire line, so it'll never match (the line has a date after " - "). It should be `index($0, "## [" v "] - ") == 1`, or use a regex match. Fix:

```awk
index($0, "## [" v "] - ") == 1 { found = 1; next }
```

This is the bug. Also checking `stage_changelog`'s grep: `grep -q "^## \[$v\] - " CHANGELOG.md` — this one is correct (a prefix regex). And the idempotency check in `stage_changelog` uses the same grep — no problem there.

I'll fix extract_changelog_section.

Found it — the transformation is perfect, but `extract_changelog_section` is using exact line equality comparison (`$0 == "## [v] - "`), which will never match lines with a date suffix. Fixing it to a prefix match:

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "extract_changelog_section() {\n  awk -v v=\"$1\" '\n    $0 == \"## [\" v \"] - \" { found = 1; next }\n    found && /^## / { exit }\n    found && $0 ~ /^[[:space:]]*$/ && !started { next }\n    found { started = 1; print }\n  ' CHANGELOG.md\n}",
  "newString": "extract_changelog_section() {\n  awk -v v=\"$1\" '\n    index($0, \"## [\" v \"] - \") == 1 { found = 1; next }\n    found && /^## / { exit }\n    found && $0 ~ /^[[:space:]]*$/ && !started { next }\n    found { started = 1; print }\n  ' CHANGELOG.md\n}"
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 77.2s)

_Thinking:_

Okay, let me re-test the entire changelog flow from a clean state (the file is still in the converted state due to the previous run — since it terminated after the conversion, restore it first):

1. `git checkout -- CHANGELOG.md`
2. Re-insert the fake entry
3. Run `changelog 0.15.0`
4. Verify the top of the file + the extraction result
5. Test idempotency: run `changelog 0.15.0` again → "already present — nothing to do"
6. Restore

Re-testing from a clean state, including the idempotency path:

**Tool: bash**

**Input:**

```json
{
  "command": "git checkout -- CHANGELOG.md && sed -i '0,/^## \\[Unreleased\\]$/s//## [Unreleased]\\n\\n### Added\\n\\n- TEST-ENTRY: throwaway line to exercise the changelog transform./' CHANGELOG.md && scripts/release.sh changelog 0.15.0 && echo \"=== extract result:\" && scripts/release.sh 2>/dev/null; awk 'index($0, \"## [0.15.0] - \") == 1 { f=1; next } f && /^## / { exit } f && !s && $0 ~ /^[[:space:]]*$/ { next } f { s=1; print }' CHANGELOG.md && echo \"=== second run (idempotency):\" && bash -c 'source /dev/stdin <<<\"$(sed -n \"/^extract_changelog_section/,/^}/p\" scripts/release.sh)\"; true' 2>/dev/null; head -12 CHANGELOG.md"
}
```

**Output:**

```
release: changelog: [Unreleased] moved into ## [0.15.0] - 2026-08-31
=== extract result:
Staged release automation for biz.dfch.SpecMgr.

Deterministic projection of the normative SOP "Perform a release of
biz.dfch.SpecMgr" (SOP 98537416-0e6e-4a02-925f-974a17bfa10a,
docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md).
Where this script and the SOP disagree, the SOP wins: fix the script.

Usage: scripts/release.sh <stage> [X.Y.Z | patch | minor | major] [--dry-run]

Stages (mirror the SOP's 9 procedure steps; every stage is idempotent):
  resolve       compute and print the target version (no mutation)
  precheck      fail-fast pre-release checks (SOP step 2)
  bump          pyproject.toml + uv.lock version bump (SOP step 4)
  changelog     move [Unreleased] into a dated section (SOP step 5a)
  commit-push   commit the 3 release files, push dev, wait for CI (SOP step 5b)
  pr-create     open the dev->main release PR, wait for checks (SOP step 6a)
  pr-merge      ff-only merge of the release PR (SOP step 6b, after the merge gate)
  tag-push      tag vX.Y.Z on main, push the tag, back to dev (SOP step 7)
  publish-wait  wait for the 4 publish.yml jobs (SOP step 8)
  release-notes verify the release + set the GitHub Release notes (SOP step 9)
  status        read-only: where does this release stand?
  all           resolve + precheck + bump + changelog + commit-push +
                pr-create + [TTY merge gate] + pr-merge + tag-push +
                publish-wait + release-notes (no agent curation: the
                [Unreleased] section must already be curated)

Only `resolve` and `all` accept bump keywords; all other stages take the
full resolved version.

### Added

- TEST-ENTRY: throwaway line to exercise the changelog transform.

=== second run (idempotency):
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.15.0] - 2026-08-31

### Added

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 75.4s)

_Thinking:_

My test command got messy in the middle (I mistakenly ran `scripts/release.sh` without a stage, so it displayed the usage), but the important parts succeeded:

1. `changelog 0.15.0` conversion: **passed** — "changelog: [Unreleased] moved into ## [0.15.0] - 2026-08-31"
2. Extraction via the fixed awk (duplicated inline): outputs `### Added\n\n- TEST-ENTRY...` — correct
3. File structure confirmed to be correct: `## [Unreleased]` is empty, then the dated section after it.

Let me cleanly verify the idempotent path of the actual script function (a second run of `changelog 0.15.0` should display "already present — nothing to do"), and after that restore the file.

The transform and extraction are working (the usage output in the middle was my own erroneous test command). Currently verifying the script's actual idempotency path, then restoring afterward:

**Tool: bash**

**Input:**

```json
{
  "command": "scripts/release.sh changelog 0.15.0; echo \"exit=$?\"; git checkout -- CHANGELOG.md && git status --porcelain"
}
```

**Output:**

```
release: changelog: section ## [0.15.0] already present — nothing to do
exit=0
?? scripts/

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 93.8s)

_Thinking:_

Idempotency confirmed. File restored (the only untracked item is `scripts/` — as expected).

Remaining untested stages: `commit-push`, `pr-create`, `pr-merge`, `tag-push`, `publish-wait`, `release-notes` — these make real remote changes and can't be safely tested end-to-end without an actual release. What I can test:

- The guard rails: e.g. `commit-push 0.15.0` on a clean tree with pyproject at 0.14.0 → should die with "pyproject.toml does not carry 0.15.0 — run the bump stage first". `pr-create 0.15.0` → same guard. `tag-push 0.15.0` → dies with "origin/main != origin/dev — finish pr-merge first". `publish-wait 0.15.0` → dies with "tag v0.15.0 does not exist locally". `release-notes 0.15.0` → dies with "GitHub Release v0.15.0 not found". `pr-merge 0.15.0` → main != dev → "no open dev->main PR — run pr-create first". These are cheap, safe guard tests — let's run them all in a single batch.

After that:

- `bash -n` again after the edits.
- Commit the script.
- Phase 2: the command file.
- Phase 3: README + AGENTS.md.
- Phase 4: the rest of the validation (including restarting opencode for the command — the command can't be tested until the user restarts opencode. Note that).

Running the guard tests now.

Idempotent path works. Testing the remaining stages' guard rails (each should die with a clear "run X first" — no remote effects):

**Tool: bash**

**Input:**

```json
{
  "command": "for s in \"commit-push 0.15.0\" \"pr-create 0.15.0\" \"pr-merge 0.15.0\" \"tag-push 0.15.0\" \"publish-wait 0.15.0\" \"release-notes 0.15.0\"; do echo \"--- $s:\"; scripts/release.sh $s </dev/null 2>&1 | tail -1; done; git status --porcelain"
}
```

**Output:**

```
--- commit-push 0.15.0:
release: ERROR: pyproject.toml does not carry 0.15.0 — run the bump stage first
--- pr-create 0.15.0:
release: ERROR: pyproject.toml does not carry 0.15.0 — finish commit-push first
--- pr-merge 0.15.0:
release: ERROR: no open dev->main PR — run pr-create first (after the maintainer's merge gate)
--- tag-push 0.15.0:
release: ERROR: origin/main != origin/dev — finish pr-merge first (fast-forward invariant)
--- publish-wait 0.15.0:
release: ERROR: tag v0.15.0 does not exist locally — fetch tags or run tag-push first
--- release-notes 0.15.0:
release: ERROR: GitHub Release v0.15.0 not found — the publish run's 'Make GitHub Release' job may have failed; check it before proceeding
?? scripts/

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 198.7s)

_Thinking:_

All 6 guardrails are working correctly, and the tree is unchanged. One more check: the dry-run for `pr-create` after bump... can't do that without an actual bump. The guards are sufficient.

Also, let me re-verify `bash -n` after the edits and review the full script once more for any issues I might have missed:

1. Inside `stage_precheck` — I removed `sha` from the local declarations, but... let me confirm that the edits are consistent:

```bash
  local line rid status conclusion
  line=$(latest_dev_run_tsv)
  [ -n "$line" ] || die "no CI runs found on dev"
  IFS=$'\t' read -r rid _ status conclusion <<<"$line"
```

Good.

2. `latest_dev_run_tsv` — the multi-line jq inside single quotes:

```bash
  gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion \
    --jq '[.[] | select(.headBranch == "dev")] | .[0] // empty
          | [.databaseId, .headSha, .status, (.conclusion // "")] | @tsv' 2>/dev/null || true
```

Multi-line jq inside single quotes — valid. Worked in the precheck test.

3. `wait_for_dev_ci` — `IFS=$'\t' read -r rid sha status _ <<<"$line"` — the 4th field is conclusion, unused (\_). OK.

4. Potential issue in `stage_status`: `local line s c` declared after `local commit_sha` etc. — bash `local` is function-scoped, no problem.

5. `stage_release_notes`: `rel_json=$(gh release view ... --jq '{url, n: (.assets | length)}' 2>/dev/null) || die ...` — this rel_json variable is assigned but never used afterward (I use separate url/assets calls). Minor dead code. vulture doesn't check bash. Let me clean it up: remove the rel_json assignment, keep `url=$(gh release view ... || die)`. Actually, the first gh release view call is the existence check with the die message. Let me restructure:

```bash
  local url assets
  url=$(gh release view "v$v" --json url --jq .url 2>/dev/null) || die "GitHub Release v$v not found — ..."
  assets=$(gh release view "v$v" --json assets --jq '.assets | length')
```

Remove the rel_json line.

6. `usage()` — `sed -n '2,30p' "$0"` — the header comment spans lines 2–30... my file: line 1 is shebang, lines 2–30 are the comment block. From the output, it looked complete and correct (ended with "full resolved version."). OK.

7. `stage_all` — the `unreleased_is_empty || true` line: this is a leftover no-op (calling the function for its side effects — no side effects, and `|| true` under set -e... if it returns 1 (not empty), `|| true` saves it). This line is meaningless — remove it. The info note below it is the actual content.

8. `stage_pr_create`: `pr_line=$(gh pr list ... --jq '.[0] | @tsv' 2>/dev/null || true)` — if the PR doesn't exist, gh pr list outputs `null` for `.[0]`... `.[0] | @tsv` against null → "null"? Let me think: `gh pr list --json number,url` with no PRs → `[]`. `.[0]` → null. `null | @tsv` → "null". So pr_line="null" — not empty! Bug: it would try to resume a fake PR "null".

Hmm wait — in my guard tests, `pr-create` died at an earlier stage (current_version check), so this path wasn't executed. In `pr-merge` I have the same pattern: `pr_line=$(gh pr list --base main --head dev --state open --json number --jq '.[0] | @tsv' 2>/dev/null || true)`; `[ -n "$pr_line" ]` — the "null" string would pass -n, and then `gh pr merge "null"` would fail with a gh error. In `stage_status` too: `pr_line=$(gh pr list ... --jq '.[0] | @tsv' ...)` and `[ -n "$pr_line" ]` → would print "open PR: null".

Actually, let me verify: does `null | @tsv` output "null"? In jq: `echo '[]' | jq '.[0] | @tsv'` → outputs `null`. Yes, it outputs the string "null".

Fix: guard against "null": use `--jq '[.[] | select(...)] | .[0] // empty | ...'` — with `// empty`, if there are no PRs the output becomes empty. In all 3 places (pr-create, pr-merge, status): change `. [0] | @tsv` to `.[0] // empty | @tsv`... wait, operator precedence: `.[0] // empty | @tsv` — does `|` have lower precedence than `//`? In jq, `//` binds tighter than `|`. So `.[0] // empty | @tsv` = `((.[0]) // empty) | @tsv` → if null → empty → no output.

Let me verify locally with jq... is jq installed? I'll test it. If not, trust the jq semantics (documented).

Actually, in the case of `gh pr list`, there's another subtle point: does it exit non-zero when there are no PRs? I think it outputs [] and exits 0. The `|| true` covers either case.

09. `stage_pr_merge`: `gh pr checks "$pr_num"` — for a PR with pending checks, rc=2 → loop? No — pr-merge does a one-shot check: `out=$(gh pr checks "$pr_num" 2>&1) && rc=0 || rc=$?` followed by `[ "$rc" -eq 0 ] || die`. If pending (rc=2) → dies with "checks are not all green". Correct behavior for pr-merge (should only be run after pr-create has confirmed green, or after re-verification). Good.

10. `wait_for_pr_checks` — `gh pr checks` rc semantics: 0=pass, 1=fail, 2=pending. Verified in the code. Note: newer gh versions: "gh pr checks exits 0 if all pass, 1 if any fail, 2 if any pending" — I believe that's stable.

11. `git fetch origin dev main --quiet` in precheck — if the local main branch doesn't exist (this repo has local main? yes, I checked it out earlier — it exists locally). No problem.

12. tag-push: `git checkout main` — if the user is on dev with a clean tree, no problem. If the local main is stale — `git pull --ff-only origin main` updates it. Good.

13. In `stage_commit_push`, the idempotency check `git log -1 --format=%s` — the latest commit on local dev. And the HEAD == origin/dev check. Good.

14. `assert_dirty_subset` — has an unused variable `allowed` (set from $1, then shifted... wait: `local allowed="${1:-}"; shift` — then "$@" is the file list. `allowed` is unused (dead). Remove it.

Let me apply these 3 cleanup/bug fixes (null guard ×3, rel_json, unused `allowed`, meaningless line in stage_all), re-run bash -n + a quick regression (status + guard tests), and then commit.

All guardrails are working correctly. During review I found 3 actual bugs: (1) `gh pr list` with no PR returns `null` via jq's `@tsv` — my `[ -n "$pr_line" ]` check ends up passing against the literal string `"null"`; (2) unused variables; (3) leftover no-op lines. Fixing:

**Tool: bash**

**Input:**

```json
{
  "command": "echo '[]' | jq '.[0] | @tsv'; echo '[]' | jq '.[0] // empty | @tsv'; echo \"null-guard verified\""
}
```

**Output:**

```
jq: error (at <stdin>:1): null (null) cannot be tsv-formatted, only array
null-guard verified

```

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "  local pr_line pr_num pr_url\n  pr_line=$(gh pr list --base main --head dev --state open --json number,url --jq '.[0] | @tsv' 2>/dev/null || true)",
  "newString": "  local pr_line pr_num pr_url\n  pr_line=$(gh pr list --base main --head dev --state open --json number,url --jq '.[0] // empty | @tsv' 2>/dev/null || true)"
}
```

**Output:**

```
Edit applied successfully.
```

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "  local pr_line pr_num\n  pr_line=$(gh pr list --base main --head dev --state open --json number --jq '.[0] | @tsv' 2>/dev/null || true)",
  "newString": "  local pr_line pr_num\n  pr_line=$(gh pr list --base main --head dev --state open --json number --jq '.[0] // empty | @tsv' 2>/dev/null || true)"
}
```

**Output:**

```
Edit applied successfully.
```

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "  local pr_line\n  pr_line=$(gh pr list --base main --head dev --state open --json number,url --jq '.[0] | @tsv' 2>/dev/null || true)",
  "newString": "  local pr_line\n  pr_line=$(gh pr list --base main --head dev --state open --json number,url --jq '.[0] // empty | @tsv' 2>/dev/null || true)"
}
```

**Output:**

```
Edit applied successfully.
```

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "  local rel_json url assets\n  rel_json=$(gh release view \"v$v\" --json url,assets --jq '{url, n: (.assets | length)}' 2>/dev/null) || die \"GitHub Release v$v not found — the publish run's 'Make GitHub Release' job may have failed; check it before proceeding\"\n  url=$(gh release view \"v$v\" --json url --jq .url)\n  assets=$(gh release view \"v$v\" --json assets --jq '.assets | length')",
  "newString": "  local url assets\n  url=$(gh release view \"v$v\" --json url --jq .url 2>/dev/null) || die \"GitHub Release v$v not found — the publish run's 'Make GitHub Release' job may have failed; check it before proceeding\"\n  assets=$(gh release view \"v$v\" --json assets --jq '.assets | length')"
}
```

**Output:**

```
Edit applied successfully.
```

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "assert_dirty_subset() {\n  local allowed=\"${1:-}\" f\n  shift\n  for f in $(dirty_files); do",
  "newString": "assert_dirty_subset() {\n  local f\n  for f in $(dirty_files); do"
}
```

**Output:**

```
Edit applied successfully.
```

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "  stage_precheck \"$v\"\n  if [ \"$DRY_RUN\" -eq 0 ]; then\n    unreleased_is_empty || true\n    info \"note: all mode does NOT curate the changelog (SOP step 3 is an agent/manual step); [Unreleased] is taken as-is\"\n  fi",
  "newString": "  stage_precheck \"$v\"\n  if [ \"$DRY_RUN\" -eq 0 ]; then\n    info \"note: all mode does NOT curate the changelog (SOP step 3 is an agent/manual step); [Unreleased] is taken as-is\"\n  fi"
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 130.5s)

_Thinking:_

Interesting — the output of `echo '[]' | jq '.[0] | @tsv'` was a jq error ("null cannot be tsv-formatted"), not the string "null"! So `.[0] | @tsv` against an empty array → jq error, non-zero exit, no output. And since my command substitution had `|| true`, pr_line would be empty — meaning the original code was actually fine after all (the error was being suppressed). But wait: in that case, the `2>/dev/null` in `pr_line=$(gh pr list ... )` — the jq error comes from gh's --jq evaluation, and gh exits non-zero with an error message on stderr → gets suppressed → `|| true` → empty. Okay, so the original was also safe, but the `// empty` guard is still cleaner and more explicit (in case gh/jq behavior changes). Keeping the fix — it's harmless and more correct.

Hmm, but there's one subtle point: with `.[0] // empty | @tsv`, if `.[0]` is an object like `{number: 5, url: "..."}` → `@tsv` on an object? @tsv requires an array! `{"a":1} | @tsv` → error "only array can be tsv-formatted"?? Let me check: jq's @tsv: "produces a tab-separated values representation of the input... only array inputs". Yes — @tsv on a non-array object is an error!

So in the case of one PR: `gh pr list --json number,url` → `[{number: 42, url: "..."}]`. `.[0]` → object. `.[0] // empty | @tsv` → object | @tsv → error!

Wait — then why did `latest_dev_run_tsv` work? Because I was building an array first: `.[0] // empty | [.databaseId, .headSha, .status, (.conclusion // "")] | @tsv` — there @tsv is applied to an array literal. Correct.

But in the pr list call, I'm applying @tsv directly to `.[0]` (an object) — that should fail! Let me verify what `gh pr list --json number,url --jq '.[0] | @tsv'` does when a PR exists... jq: object | @tsv → "error: ... cannot be tsv-formatted, only array". So if a PR exists → error → `|| true` → empty → the script concludes there's no PR! That's a bug (the reverse one).

Fix: wrap in an array: `.[0] // empty | [.number, .url] | @tsv`. For number only: `.[0] // empty | [.number] | @tsv`.

Let me fix all three places (pr-create, pr-merge, status). And verify by testing the actual jq expression against sample input.

`@tsv` only accepts *arrays* — applying it to the PR object `.[0]` will fail when a PR exists (the opposite bug). I'll fix it by explicitly constructing the array, and verify with sample data:

**Tool: bash**

**Input:**

```json
{
  "command": "echo '[{\"number\": 42, \"url\": \"https://x\"}]' | jq '.[0] // empty | [.number, .url] | @tsv'; echo '[]' | jq '.[0] // empty | [.number, .url] | @tsv'; echo \"both cases OK\""
}
```

**Output:**

```
"42\thttps://x"
both cases OK

```

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "  pr_line=$(gh pr list --base main --head dev --state open --json number,url --jq '.[0] // empty | @tsv' 2>/dev/null || true)\n  if [ -n \"$pr_line\" ]; then\n    IFS=$'\\t' read -r pr_num pr_url <<<\"$pr_line\"\n    info \"resuming existing release PR: $pr_url\"",
  "newString": "  pr_line=$(gh pr list --base main --head dev --state open --json number,url --jq '.[0] // empty | [.number, .url] | @tsv' 2>/dev/null || true)\n  if [ -n \"$pr_line\" ]; then\n    IFS=$'\\t' read -r pr_num pr_url <<<\"$pr_line\"\n    info \"resuming existing release PR: $pr_url\""
}
```

**Output:**

```
Edit applied successfully.
```

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "  pr_line=$(gh pr list --base main --head dev --state open --json number --jq '.[0] // empty | @tsv' 2>/dev/null || true)\n  [ -n \"$pr_line\" ] || die \"no open dev->main PR — run pr-create first (after the maintainer's merge gate)\"\n  pr_num=\"${pr_line%%$'\\t'*}\"",
  "newString": "  pr_line=$(gh pr list --base main --head dev --state open --json number --jq '.[0] // empty | [.number] | @tsv' 2>/dev/null || true)\n  [ -n \"$pr_line\" ] || die \"no open dev->main PR — run pr-create first (after the maintainer's merge gate)\"\n  pr_num=\"${pr_line%%$'\\t'*}\""
}
```

**Output:**

```
Edit applied successfully.
```

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/scripts/release.sh",
  "oldString": "  pr_line=$(gh pr list --base main --head dev --state open --json number,url --jq '.[0] // empty | @tsv' 2>/dev/null || true)\n  if [ -n \"$pr_line\" ]; then\n    mark=\"!\"; detail=\"open PR: $pr_line (merge gate pending?)\"",
  "newString": "  pr_line=$(gh pr list --base main --head dev --state open --json number,url --jq '.[0] // empty | [.number, .url] | @tsv' 2>/dev/null || true)\n  if [ -n \"$pr_line\" ]; then\n    mark=\"!\"; detail=\"open PR: $pr_line (merge gate pending?)\""
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 92.1s)

_Thinking:_

jq verification done: case with PR present → "42\\thttps://x" (output wrapped in quotes, since @tsv generates a JSON string. In the case of a single string result, jq -r is needed... no wait — `gh --jq` automatically outputs the raw string result of jq. `jq '.[0] // empty | [.number, .url] | @tsv'` outputs the JSON string `"42\thttps://x"`. If it's `gh --jq` (Go template / jq output), does it unquote string results? gh's --jq uses gojq, and outputs the raw jq result — for a string it outputs without quotes (gh treats string output as raw). Earlier, `latest_dev_run_tsv` worked via IFS read and produced the correct fields (precheck found the green run) — that was also using @tsv — and gh output it unquoted (read correctly obtained the rid/sha/status/conclusion fields, and the "latest dev CI run is green" decision proves that parsing succeeded). So gh handles it. Good.

Now: full regression — bash -n, rerun status, rerun guards, and the entire read-only flow. Then commit the script.

Full regression pass:

**Tool: bash**

**Input:**

```json
{
  "command": "bash -n scripts/release.sh && echo \"syntax OK\" && scripts/release.sh status 0.15.0 && echo === && scripts/release.sh precheck 0.15.0 && git status --porcelain"
}
```

**Output:**

```
syntax OK
release status for v0.15.0:
  [ ] bump          pyproject.toml carries 0.14.0
  [ ] changelog     no dated section yet
  [ ] commit-push   release commit not on origin/dev
  [ ] pr            no open PR; main behind dev
  [ ] tag           no tag
  [ ] publish       no publish run (no tag)
  [ ] release-notes no GitHub Release yet
===
release: target: v0.15.0
release: note: 1 untracked path(s) ignored (untracked files cannot enter the release commit)
release: fast-forward invariant holds (main is an ancestor of dev)
release: latest dev CI run is green
release: tag v0.15.0 does not exist yet
release: uv.lock is in sync
release: precheck: all checks passed for v0.15.0
?? scripts/

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 196.8s)

_Thinking:_

All green. Next, commit the script (Phase 1), then Phase 2 (command file).

Commit message: "feat: add staged release automation script (SOP 98537416)" — following the conventional commits style. Looking at history: "feat(sop): ..." hmm. This is a new tool under scripts/. Should it be "feat(release): add staged release script ..." or "chore(release): add scripts/release.sh (staged release automation)"? Previous examples: "feat(general): Add webfetch tool to general package", "chore(feat-7): add backlog task ...". Since this adds new functionality (the release tool), "feat(release): add staged release automation script" seems appropriate. The scope "release" hasn't been used before, but it's fine and descriptive.

Also — pre-commit: ruff format ran (passed, no py files), vulture has "no files to check" (scripts/ isn't python), no problem.

After that, Phase 2: .opencode/command/release.md.

Command design (template = the prompt that the agent runs):

```markdown
---
description: Run the release SOP — version bump, changelog, dev→main PR, tag, and publish (scripts/release.sh stages).
---

Execute the release SOP (`docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md`) by driving `scripts/release.sh` stages from the repo root. My input was: $ARGUMENTS

1. Parse my input: it is either a version spec (`X.Y.Z` or `patch`/`minor`/`major`), `--dry-run`, or nothing. If no version spec, ask me via the question tool (offer the current version read from pyproject.toml plus suggested next minor/patch). Never guess.
2. Run `bash scripts/release.sh resolve <spec>` — confirm the resolved version with me before continuing (a surprising number, e.g. major on 0.x, needs explicit acknowledgement).
3. Run `bash scripts/release.sh precheck <version>`.
4. Curate the changelog (SOP step 3 — your only direct file edit): read the `[Unreleased]` section of CHANGELOG.md and `git log <last-tag>..HEAD --oneline`; add missing user-visible items, rewrite entries into Keep a Changelog categories; show me the finished section and wait for my OK before continuing. If `[Unreleased]` is empty, stop and ask me what should be documented.
5. Run the stages in order, each as its own bash call: `bump <version>`, `changelog <version>`, `commit-push <version>`, `pr-create <version>` (long-running: allow a generous timeout).
6. Merge gate: after `pr-create` succeeds, show me the PR URL and the changelog section, and ask for explicit go-ahead. Only then run `pr-merge <version>`.
7. Continue: `tag-push <version>`, `publish-wait <version>` (longest: allow ~60 min), `release-notes <version>`.
8. If `--dry-run` was given, run only: resolve, precheck, and the dry-run forms of bump/changelog/pr-create (the remaining stages are meaningless in dry-run); do not commit, push, open a PR, tag, or publish anything.
9. On any non-zero exit: stop immediately. Run `bash scripts/release.sh status <version>` to locate the failure, fetch the relevant CI log if a run failed, report the diagnosis and the run/PR URLs verbatim, and wait for my direction. Never auto-retry, never re-run a stage past the failure, never perform release steps outside the script.
10. On success: summarize in a few lines (version, PR, tag, release URLs from the script's final output).
```

Hmm, wait, about step 8 (dry-run): the bump dry-run is fine; the changelog dry-run requires [Unreleased] to be non-empty (otherwise it will die at the confirmation stage) — with an empty unreleased, the dry-run would stop at the changelog... acceptable (it's a dry-run of the flow, and the stop condition is informative). commit-push dry-run: requires pyproject to have the version → fails after the dry-run bump (since nothing has actually been bumped). So the dry-run flow is: resolve, precheck, bump --dry-run, changelog --dry-run, and stop (commit-push dry-run is impossible without an actual bump). Let me simplify: "For --dry-run: run resolve, precheck, bump --dry-run, changelog --dry-run and then stop (subsequent stages require actual state); show me what would happen next."

Also, the command file — should I instruct the agent to run `bash scripts/release.sh` or `./scripts/release.sh`? The script is executable; but `bash scripts/release.sh` is more robust. Use `bash scripts/release.sh`.

Long-running bash calls: commit-push (CI wait up to 40 min) and publish-wait (45 min) — the agent must set a large timeout on the bash tool (e.g., 3000000 ms = 50 min, or 3600000). Note this.

Phase 3: README + AGENTS.md.

README "Make a Release" section: rewrite to reference the SOP + /release + scripts/release.sh, keeping the manual fallback. Let me draft:

````markdown
## Make a Release

The normative release procedure is the SOP
["Perform a release of biz.dfch.SpecMgr"](docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md)
(SOP `98537416`). Where this section, the script, or the command ever
disagree with the SOP, the SOP wins.

### Using the OpenCode command (recommended)

`/release [X.Y.Z | patch | minor | major] [--dry-run]`

The command drives the staged script and performs the agent-judgment
steps of the SOP: it confirms the resolved version with you, curates the
changelog's `[Unreleased]` section, and pauses at the merge gate before
`dev` is merged into `main`.

### Using the script directly

Each SOP step has a deterministic, idempotent stage:

```bash
scripts/release.sh resolve minor        # print the target version (0.15.0)
scripts/release.sh precheck 0.15.0      # fail-fast checks
scripts/release.sh bump 0.15.0          # pyproject.toml + uv.lock
scripts/release.sh changelog 0.15.0     # [Unreleased] -> dated section
scripts/release.sh commit-push 0.15.0   # 3-file commit, push dev, wait CI
scripts/release.sh pr-create 0.15.0     # release PR, wait checks (no merge)
scripts/release.sh pr-merge 0.15.0      # ff-only merge (after your go-ahead)
scripts/release.sh tag-push 0.15.0      # tag on main, push, back to dev
scripts/release.sh publish-wait 0.15.0  # 4 publish.yml jobs
scripts/release.sh release-notes 0.15.0 # verify + set release notes
scripts/release.sh status 0.15.0        # where does the release stand?
scripts/release.sh all 0.15.0           # the whole chain, TTY only
````

Note: step 3 of the SOP (changelog curation) is an agent/manual step —
the `changelog` stage only moves the already-curated `[Unreleased]`
section into its dated form.

### Manual fallback

\<old steps, condensed>

```

Keep the old manual procedure as a fallback (the SOP has the complete manual command per step; the README's fallback can point at the SOP's manual fallback line per step + show the core commands). To keep the README concise: "Follow the SOP's *Manual fallback* lines step by step. Core commands: ..." with the main ones enumerated.

AGENTS.md: add to Developer Commands:
```

bash scripts/release.sh all X.Y.Z # staged release automation (see SOP 98537416)

````
Hmm, the AGENTS.md Developer Commands block is a list of bash commands. Add one line: `scripts/release.sh status 0.0.0  # release automation stages (SOP 98537416; see README "Make a Release")`. Keep it a single line.

Wait — should I also mention the `/release` command in AGENTS.md? AGENTS.md is for agents. A one-line pointer would be useful. Let me add it to the same line.

Order of work from here:
1. Commit the script (feat(release): ...)
2. Write .opencode/command/release.md
3. Update README + AGENTS.md
4. Commit these (docs/chore commits)
5. Report + instruct the user to restart opencode for the command (and the SOP status note)

Actually — one more thing to double-check in the script: the `pr_url=$(gh pr create ...)` in `stage_pr_create` — gh pr create outputs the URL. Good. And `pr_num=$(gh pr view "$pr_url" --json number --jq .number)` — gh pr view accepts a URL. Good.

One more check — `wait_for_pr_checks` is used in pr-create before the merge gate. Good.

And in `stage_pr_merge` — after `gh pr merge "$pr_num" --ff-only`: does gh pr merge --ff-only work when the base branch is behind? Yes, that's the point.

Also, a potential issue: `gh pr merge` may require the PR to be mergeable; no problem.

Now — vulture hook: "no files to check" (bash isn't python). ruff: no py files. Committing.




All green. Committing the script:



**Tool: bash**

**Input:**
```json
{
  "command": "git add scripts/release.sh && git commit -m \"feat(release): add staged release automation script (SOP 98537416)\" && git push"
}
````

**Output:**

```
ruff format..........................................(no files to check)Skipped
ruff check...........................................(no files to check)Skipped
vulture..............................................(no files to check)Skipped
unittest.............................................(no files to check)Skipped
specmgr coverage-badge...............................(no files to check)Skipped
specmgr docs.........................................(no files to check)Skipped
specmgr mcp-docs.....................................(no files to check)Skipped
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (sop package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped
[dev 3c2b8e9] feat(release): add staged release automation script (SOP 98537416)
 1 file changed, 725 insertions(+)
 create mode 100755 scripts/release.sh
To https://github.com/dfch/biz.dfch.SpecMgr.git
   79b3951..3c2b8e9  dev -> dev

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 75.1s)

_Thinking:_

Wait — "725 insertions"? My script should have been around 560 lines... Let me check: the file I wrote + the edits. Actually, `wc -l` should tell me. 725 seems too many. Hmm, let me verify whether the committed file is what I expect (no duplication from the edits).

725 insertions looks high for this script — verifying nothing got duplicated by the edits:

**Tool: bash**

**Input:**

```json
{
  "command": "wc -l scripts/release.sh && grep -c \"^stage_\\|^wait_for_\\|^latest_dev_run_tsv\\|^resolve_target\\|^extract_changelog_section\\|^unreleased_\\|^dirty_files\\|^assert_dirty_subset\\|^confirm_or_die\\|^require_\\|^current_version\\|^validate_full\\|^bump_semver\\|^usage\\|^main()\" scripts/release.sh && grep -n \"^main \\\"\\$@\\\"\" scripts/release.sh"
}
```

**Output:**

```
725 scripts/release.sh
30
725:main "$@"

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 74.4s)

_Thinking:_

725 lines, 30 top-level functions (hmm, this grep was counting function-like definitions — there are 12 stages + helpers), and only one `main "$@"` at line 725 (the end). No duplicates. The script really is 725 lines — the usage() header + all the stages are verbose. No problem.

Wait, let me double-check that there's no accidental content duplication — I'll check the number of occurrences of "stage_bump()":

**Tool: bash**

**Input:**

```json
{
  "command": "grep -c \"^stage_bump()\\|^stage_precheck()\\|^wait_for_run()\\|^latest_dev_run_tsv()\" scripts/release.sh; grep -n \"^stage_\\|^main()\" scripts/release.sh"
}
```

**Output:**

```
4
253:stage_resolve() {
259:stage_precheck() {
310:stage_bump() {
342:stage_changelog() {
376:stage_commit_push() {
412:stage_pr_create() {
447:stage_pr_merge() {
480:stage_tag_push() {
511:stage_publish_wait() {
542:stage_release_notes() {
582:stage_status() {
665:stage_all() {
690:main() {

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 110.3s)

_Thinking:_

Each function appears exactly once — the file is clean (725 lines, just verbose).

Phase 1 complete (committed as 3c2b8e9). Next is Phase 2: `.opencode/command/release.md`.

Clean — each function exactly once. Phase 1 done (`3c2b8e9`). Phase 2 — the OpenCode command:

**Tool: write**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.opencode/command/release.md",
  "content": "---\ndescription: Run the release SOP — version bump, changelog, dev→main PR, tag, and publish — by driving scripts/release.sh stages.\n---\n\nExecute the release SOP (`docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md`) by driving the `scripts/release.sh` stages from the repo root. The script is the single source of truth for release mechanics; the SOP is the single source of truth for the procedure. My input: $ARGUMENTS\n\nFollow these steps in order:\n\n1. **Parse my input.** It is either a version spec (`X.Y.Z` or `patch`/`minor`/`major`), optionally combined with `--dry-run`, or nothing. If no version spec was given, ask me with the question tool — offer the current version from `pyproject.toml` plus the suggested next minor and patch. Never guess a version.\n2. **Resolve.** Run `bash scripts/release.sh resolve <spec>` (or `resolve --dry-run`-equivalent: `resolve` never mutates). Confirm the resolved version with me before continuing — a surprising number (e.g. `major` on a `0.x` version) needs my explicit acknowledgement.\n3. **Pre-check.** Run `bash scripts/release.sh precheck <version>`. Any failure: report it verbatim and stop.\n4. **Curate the changelog** (SOP step 3 — this is your only direct file edit, never done by the script): read the `[Unreleased]` section of `CHANGELOG.md` and `git log $(git describe --tags --abbrev=0)..HEAD --oneline`, add missing user-visible items, rewrite verbose or internal entries into Keep a Changelog categories (`Added`/`Changed`/`Deprecated`/`Removed`/`Fixed`/`Security`), then show me the finished section and wait for my OK before continuing. If `[Unreleased]` is empty, stop and ask me what should be documented for this release.\n5. **Run the mutating stages in order**, each as its own bash call with a generous timeout (these wait on CI: use at least 45 minutes / 2700000 ms):\n   - `bash scripts/release.sh bump <version>`\n   - `bash scripts/release.sh changelog <version>`\n   - `bash scripts/release.sh commit-push <version>`\n   - `bash scripts/release.sh pr-create <version>`\n6. **Merge gate.** After `pr-create` succeeds, show me the PR URL and the new changelog section, and ask for my explicit go-ahead. Only once I approve, run `bash scripts/release.sh pr-merge <version>`.\n7. **Finish the release** (generous timeouts again, `publish-wait` can take up to 45 minutes):\n   - `bash scripts/release.sh tag-push <version>`\n   - `bash scripts/release.sh publish-wait <version>`\n   - `bash scripts/release.sh release-notes <version>`\n\n**Dry-run mode** (when I gave `--dry-run`): run only `resolve`, `precheck`, `bump --dry-run`, and `changelog --dry-run` (plus the changelog curation in step 4 if useful), then stop and show me what the remaining stages would do. Never commit, push, open a PR, tag, or publish.\n\n**On any non-zero exit:** stop immediately. Run `bash scripts/release.sh status <version>` to locate the failed stage, fetch the relevant CI log if a run failed (`gh run view <id> --log-failed`), and report the diagnosis with the run/PR URLs verbatim. Wait for my direction. Never auto-retry, never skip a failed stage, never perform release steps outside the script, and never merge a red PR.\n\n**On success:** summarize in a few lines — version, PR, tag, and the release URLs from the script's final output. Remind me that the SOP stays `draft` until this first release succeeds end to end, after which it should be activated.\n"
}
```

**Output:**

```
Wrote file successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 166.8s)

_Thinking:_

Phase 2 files have been written. Next is Phase 3: updating the README and AGENTS.md.

Current state of the README's "Make a Release" section (lines 289–349): steps 1–5 are documented manually. Replace this with the new structure: SOP as canonical → /release command → script stages → manual fallback. Keep the note at the end (about publish.yml automation) — that's still accurate.

Let me re-read the current section to write the replacement text. What I confirmed earlier was:

```
## Make a Release

### 1. Make sure all tests pass
...
### 2. Increase the version
...
### 3. Commit and push to `dev`
...
### 4. Merge `dev` into `main`
...
### 5. Create and push a version tag
...
_Note: `.github/workflows/publish.yml` handles the rest of the release automatically..._
```

New version:

```markdown
## Make a Release

The canonical release procedure is the SOP
[Perform a release of biz.dfch.SpecMgr](docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md)
(SOP `98537416`). If this section, the script, or the command ever diverges
from the SOP, the SOP takes precedence.

### Using the OpenCode command (recommended)

```

/release [X.Y.Z | patch | minor | major] [--dry-run]

````

The command drives the staged script and executes the SOP's agent judgment
steps: it confirms the resolved version, curates the changelog's
`[Unreleased]` section, pauses at the merge gate before `dev` is merged
into `main`, and triages failures without ever auto-retrying.

### Using the script directly

Each SOP step corresponds to a deterministic, idempotent stage (see the
SOP for manual fallback commands for each step):

```bash
scripts/release.sh resolve minor         # display the target version (e.g., 0.15.0); no changes
scripts/release.sh precheck 0.15.0       # fail-fast pre-release checks
scripts/release.sh bump 0.15.0           # pyproject.toml + uv.lock
scripts/release.sh changelog 0.15.0      # [Unreleased] → dated section
scripts/release.sh commit-push 0.15.0    # 3-file release commit, push dev, wait for CI
scripts/release.sh pr-create 0.15.0      # dev→main release PR, wait for checks (no merge)
scripts/release.sh pr-merge 0.15.0       # ff-only merge (after maintainer approval)
scripts/release.sh tag-push 0.15.0       # tag on main, push the tag, return to dev
scripts/release.sh publish-wait 0.15.0   # the 4 publish.yml jobs
scripts/release.sh release-notes 0.15.0  # verify release + set GH release notes
scripts/release.sh status 0.15.0         # where does this release currently stand?
scripts/release.sh all 0.15.0            # the full chain, TTY only (interactive merge gate)
````

The changelog *curation* (SOP step 3) is an agent or manual step: the
`changelog` stage only moves an already-curated `[Unreleased]` section
into dated form.

### Manual fallback

Follow the SOP step by step (each step includes a *Manual fallback*
paragraph). The essential commands are: bump the `version` in
`pyproject.toml` and move `[Unreleased]` to a dated `## [x.y.z] - YYYY-MM-DD` section in `CHANGELOG.md`; `uv lock`; commit exactly
`pyproject.toml` + `uv.lock` + `CHANGELOG.md` as
`chore(release): bump version to vX.Y.Z` and push to `dev`; once CI is
green, open a PR from `dev` → `main` and merge **ff-only**
(`git merge --ff-only dev` — never a merge commit or squash: `main` must
always remain an ancestor of `dev`); then `git tag vX.Y.Z` on `main`,
push the tag, and wait for the publish workflow.

_Note: Once the `vX.Y.Z` tag is pushed, `.github/workflows/publish.yml`
automatically handles the rest of the release — it builds the
`sdist`/`wheel` and publishes to TestPyPI, then PyPI via Trusted
Publishing (OIDC, no stored tokens), creates a corresponding GitHub
Release with the built artifacts attached, and publishes `server.json`
(root of the repo, the MCP Registry publisher manifest — see
[server.json format spec](https://github.com/modelcontextprotocol/registry/blob/main/docs/reference/server-json/generic-server-json.md))
to the [MCP Registry](https://registry.modelcontextprotocol.io/?q=io.github.dfch%2Fbiz-dfch-specmgr)
via `mcp-publisher`/GitHub OIDC. Since `v0.1.0`, `biz-dfch-specmgr` has
been live on [PyPI](https://pypi.org/project/biz-dfch-specmgr/) and in the
[MCP Registry](https://registry.modelcontextprotocol.io/?q=io.github.dfch%2Fbiz-dfch-specmgr)._

```

For AGENTS.md's Developer Commands, add the following after the test command line:

```

bash scripts/release.sh status 0.0.0 # release automation (SOP 98537416; see README's "Make a Release")

```

Hmm, "status 0.0.0" is weird as an example. Maybe a comment-only line would be better:
```

scripts/release.sh --help # staged release automation (SOP 98537416; README's "Make a Release")

````
`scripts/release.sh help` displays the usage. I'll go with `help` as the stage name.

Now let me apply the edits.




Phase 3 — README "Make a Release" section:



**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/README.md",
  "oldString": "## Make a Release\n\n### 1. Make sure all tests pass\n\nBefore releasing, make sure the CI pipeline is green on the `dev` branch:\n\n```bash\nuv run --frozen ruff format --check\nuv run --frozen ruff check\nuv run --frozen pylint $(git ls-files '*.py')\nuv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"\n```\n\n### 2. Increase the version\n\nUpdate the version in `pyproject.toml`:\n\n```toml\nversion = \"x.y.z\"\n```\n\nMove the `[Unreleased]` section in `CHANGELOG.md` into a new dated\n`## [x.y.z] - YYYY-MM-DD` section.\n\n### 3. Commit and push to `dev`\n\n```bash\ngit add pyproject.toml CHANGELOG.md\ngit commit -m \"chore: bump version to vx.y.z\"\ngit push origin dev\n```\n\n### 4. Merge `dev` into `main`\n\n```bash\ngit checkout main\ngit merge dev\ngit push origin main\n```\n\n### 5. Create and push a version tag\n\n```bash\nexport VERSION=x.y.z\ngit tag v${VERSION}\ngit push origin v${VERSION}\ngit checkout dev\n```",
  "newString": "## Make a Release\n\nThe normative release procedure is the SOP\n[Perform a release of biz.dfch.SpecMgr](docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md)\n(SOP `98537416`). Where this section, the script, or the command ever\ndisagree with the SOP, the SOP wins.\n\n### Using the OpenCode command (recommended)\n\n```\n/release [X.Y.Z | patch | minor | major] [--dry-run]\n```\n\nThe command drives the staged script and performs the SOP's agent-judgment\nsteps: it confirms the resolved version with you, curates the changelog's\n`[Unreleased]` section, pauses at the merge gate before `dev` is merged\ninto `main`, and triages failures without ever auto-retrying.\n\n### Using the script directly\n\nEach SOP step maps to a deterministic, idempotent stage (the SOP carries\na manual fallback command for every step):\n\n```bash\nscripts/release.sh resolve minor         # print the target version (e.g. 0.15.0); no mutation\nscripts/release.sh precheck 0.15.0       # fail-fast pre-release checks\nscripts/release.sh bump 0.15.0           # pyproject.toml + uv.lock\nscripts/release.sh changelog 0.15.0      # [Unreleased] -> dated section\nscripts/release.sh commit-push 0.15.0    # 3-file release commit, push dev, wait for CI\nscripts/release.sh pr-create 0.15.0      # dev->main release PR, wait for checks (no merge)\nscripts/release.sh pr-merge 0.15.0       # ff-only merge (after maintainer go-ahead)\nscripts/release.sh tag-push 0.15.0       # tag on main, push the tag, back to dev\nscripts/release.sh publish-wait 0.15.0   # the four publish.yml jobs\nscripts/release.sh release-notes 0.15.0  # verify the release + set the GH release notes\nscripts/release.sh status 0.15.0         # where does this release stand?\nscripts/release.sh all 0.15.0            # the whole chain, TTY only (interactive merge gate)\n```\n\nChangelog *curation* (SOP step 3) is an agent or manual step: the\n`changelog` stage only moves the already-curated `[Unreleased]` section\ninto its dated form.\n\n### Manual fallback\n\nFollow the SOP step by step — each step carries a *Manual fallback*\nparagraph. The essentials: bump the `version` in `pyproject.toml` and\nmove the `[Unreleased]` section of `CHANGELOG.md` into a new dated\n`## [x.y.z] - YYYY-MM-DD` section; `uv lock`; commit exactly\n`pyproject.toml` + `uv.lock` + `CHANGELOG.md` as\n`chore(release): bump version to vX.Y.Z` and push to `dev`; once CI is\ngreen, open the `dev` → `main` pull request and merge it\n**fast-forward-only** (`git merge --ff-only dev` — never a merge commit or\nsquash: `main` must stay a strict ancestor of `dev`); then create\n`git tag vX.Y.Z` on `main`, push the tag, and wait for the publish\nworkflow."
}
````

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 84.4s)

_Thinking:_

Next is the Developer Commands section of AGENTS.md. Let's add one line. The current block:

```bash
uv sync --all-extras                                                   # install deps
uv run --frozen pre-commit install                                     # one-time: enable pre-commit hooks
uv run --frozen ruff format --check && uv run --frozen ruff check      # lint (enforced)
uv run --frozen pylint $(git ls-files '*.py')                          # lint (advisory only; CI runs it with `|| true`)
uv run --frozen vulture src/ whitelist.py --min-confidence 60          # dead code check (enforced)
uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"  # tests
uv run --frozen specmgr docs                                           # regenerate docs/api/ + docs/GENERATED.md
uv run --frozen specmgr adr-toc                                        # regenerate docs/adr/README.md (table of contents for ADRs)
uv run --frozen specmgr unused-code                                    # report unused code in src/ (same check as the vulture hook)
uv run --frozen specmgr unused-code --test                             # report symbols that are only referenced from tests/ and not from src/
uv run --frozen specmgr version                                        # run the CLI
```

Add after the tests line (or at the end):

```
scripts/release.sh help                                                # staged release automation (SOP 98537416; README "Make a Release")
```

AGENTS.md — adding the release line to Developer Commands:

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/AGENTS.md",
  "oldString": "uv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"  # tests\nuv run --frozen specmgr docs                                           # regenerate docs/api/ + docs/GENERATED.md",
  "newString": "uv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"  # tests\nscripts/release.sh help                                            # staged release automation (SOP 98537416; README \"Make a Release\")\nuv run --frozen specmgr docs                                           # regenerate docs/api/ + docs/GENERATED.md"
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 85.0s)

_Thinking:_

Phase 3 file is done. Next, I'll commit these (command file + README + AGENTS.md) as a single docs/chore commit, then push, then run the final validation battery (Phase 4):

- `scripts/release.sh help` (confirm the new usage path works)
- `bash -n` one more time (no changes since last time, so skip? the script is unchanged — skip)
- Re-confirm that the README edits render correctly (read the section)
- The /release command requires restarting opencode — I'll tell the user.

Commit message: "docs(release): add /release command and document SOP-based release flow". Hmm — this includes a new file .opencode/command/release.md + edits to README + edits to AGENTS.md. Conventional: "docs(release): ..." or "feat(release): add /release OpenCode command". I'll go with "feat(release): add /release OpenCode command; document SOP-based flow in README/AGENTS.md".

Committing Phase 2+3 and verifying the README section renders:

**Tool: bash**

**Input:**

```json
{
  "command": "git add .opencode/command/release.md README.md AGENTS.md && git commit -m \"feat(release): add /release OpenCode command; document SOP-based flow in README/AGENTS.md\" && git push"
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...........................................(no files to check)Skipped
vulture..............................................(no files to check)Skipped
unittest.............................................(no files to check)Skipped
specmgr coverage-badge...............................(no files to check)Skipped
specmgr docs.........................................(no files to check)Skipped
specmgr mcp-docs.....................................(no files to check)Skipped
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (sop package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped
[dev 6e614d3] feat(release): add /release OpenCode command; document SOP-based flow in README/AGENTS.md
 3 files changed, 71 insertions(+), 35 deletions(-)
 create mode 100644 .opencode/command/release.md
To https://github.com/dfch/biz.dfch.SpecMgr.git
   3c2b8e9..6e614d3  dev -> dev

```

**Tool: bash**

**Input:**

```json
{
  "command": "scripts/release.sh help | head -8"
}
```

**Output:**

```
Staged release automation for biz.dfch.SpecMgr.

Deterministic projection of the normative SOP "Perform a release of
biz.dfch.SpecMgr" (SOP 98537416-0e6e-4a02-925f-974a17bfa10a,
docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md).
Where this script and the SOP disagree, the SOP wins: fix the script.

Usage: scripts/release.sh <stage> [X.Y.Z | patch | minor | major] [--dry-run]

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 88.7s)

_Thinking:_

Everything's committed and pushed. Next up is the final verification pass (remainder of phase 4):

1. Verify that the SOP still parses correctly with the live MCP server (parse_sop against the committed file) — a good dogfooding check.
2. Verify that the README section renders correctly (read it).
3. Check whether the new dev CI is green (two pushes since the last green: 3c2b8e9, 6e614d3 — a CI run should be in progress).
4. `status 0.15.0` once more.

After that, report + user action: restart opencode to load the /release command; the first actual release will be the SOP acceptance test (after which the SOP → active).

Note: the /release smoke test (`/release --dry-run minor`) requires the user to restart opencode first — I can't invoke my own commands mid-session. So that's the last step for the user.

Final verification — SOP re-parse via live MCP, README render, and current dev CI:

**Tool: specmgr-test_parse_sop**

**Input:**

```json
{
  "path": "docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md"
}
```

**Output:**

```
{
  "frontmatter": {
    "id": "98537416-0e6e-4a02-925f-974a17bfa10a",
    "type": "sop",
    "created": "2026-08-31T15:24:14.582592",
    "updated": "2026-08-31T15:24:14.582592",
    "status": "draft",
    "version": "1.0.0"
  },
  "body": {
    "purpose": {
      "text": "## Purpose\n\nThis procedure defines how a new version of `biz-dfch-specmgr` is released\nfrom the `dev` branch to TestPyPI, PyPI, a GitHub Release, and the MCP\nRegistry. It exists so that every release — whether driven by the release\nagent through the staged `scripts/release.sh` script or performed manually\nby the maintainer — passes the same gates (green CI on `dev` and on the\nmerge pull request, the fast-forward invariant between `main` and `dev`, a\ncurated changelog, and a verified publication) and produces the same\nreproducible outcome.\n"
    },
    "scope": {
      "text": "## Scope\n\nThis SOP covers: resolving the target version; pre-release checks;\ncurating the `CHANGELOG.md` `[Unreleased]` section; bumping the version in\n`pyproject.toml` and syncing `uv.lock`; committing and pushing the release\nto `dev`; merging `dev` into `main` through a fast-forward-only pull\nrequest; creating and pushing the `vX.Y.Z` tag on `main`; waiting for the\nfour publication jobs of `.github/workflows/publish.yml`; and setting the\nGitHub Release notes.\n\nIt does not cover: deciding whether the changes warrant a patch, minor, or\nmajor version (a maintainer decision made before this SOP is invoked); the\nhotfix/backport path (no such path is defined yet — should one ever be\nneeded, it is an exception to this SOP and must be recorded in its\n`Updates`); and the internals of the `publish.yml` workflow (OIDC trusted\npublishing, `server.json` generation).\n"
    },
    "definitions": {
      "text": "## Definitions\n\n- **Release commit**: the single commit on `dev` touching exactly three\n  files — `pyproject.toml`, `uv.lock`, `CHANGELOG.md` — with the message\n  `chore(release): bump version to vX.Y.Z`.\n- **Fast-forward invariant**: `main` is always an ancestor of `dev`, i.e.\n  `main` carries no unique commits. The invariant is what makes the\n  `dev` → `main` merge possible in fast-forward-only form, and it must\n  hold before every release.\n- **Stage**: a subcommand of `scripts/release.sh` (e.g. `precheck`,\n  `bump`, `pr-merge`). Stages mirror the steps of this procedure one-to-\n  one, are idempotent (a completed stage reports \"done\" instead of\n  re-running), and are the only sanctioned way for the agent to perform\n  release mechanics.\n- **`/release`**: the OpenCode command (`.opencode/command/release.md`)\n  that drives the stages and performs this SOP's agent-judgment steps\n  (version confirmation, changelog curation, merge gate, failure triage).\n- **Publication jobs**: the four jobs of\n  `.github/workflows/publish.yml`, triggered by pushing a `v*` tag:\n  *Publish to TestPyPI* → *Publish to PyPI* → *Make GitHub Release* →\n  *Publish to MCP Registry*.\n- **`[Unreleased]` section**: the Keep a Changelog staging area at the top\n  of `CHANGELOG.md` that accumulates notable changes between releases.\n- **Merge gate**: the maintainer's explicit go-ahead to merge the release\n  pull request, given after the agent presents it (Step 6).\n"
    },
    "roles_and_responsibilities": {
      "accountable": {
        "value": {
          "text": "The repository maintainer (`dfch`) is accountable for every release and\nfor the continued validity of this procedure: they make the version\ndecision, confirm the resolved version number (Step 1), approve the merge\ngate (Step 6), and adjudicate any exception."
        },
        "text": "Accountable"
      },
      "responsible": {
        "items": [
          {
            "text": "The release agent (the OpenCode session executing `/release`) runs the\nstages in order, performs the changelog curation (Step 3), and reports\nprogress and failures. In manual mode the maintainer performs every\nstep themselves."
          }
        ],
        "text": "Responsible"
      },
      "support": {
        "items": [
          {
            "text": "`scripts/release.sh` — the deterministic stage implementations\n(pre-checks, file edits, git/gh mechanics, CI polling)."
          },
          {
            "text": "GitHub Actions — `ci.yml` (lint, tests, and docs-drift checks on `dev`\nand on the pull request) and `publish.yml` (the four publication jobs)."
          },
          {
            "text": "The `uv` and `gh` CLIs, and the external publication targets: TestPyPI\nand PyPI (both via OIDC trusted publishing) and the MCP Registry (via\n`mcp-publisher` with GitHub OIDC)."
          }
        ],
        "text": "Support"
      },
      "consulted": {
        "items": [
          {
            "text": "The maintainer is consulted at exactly two gates: the version\nconfirmation after `resolve` (Step 1) and the merge gate after\n`pr-create` (Step 6)."
          }
        ],
        "text": "Consulted"
      },
      "informed": {
        "items": [
          {
            "text": "Downstream consumers are informed via the GitHub Release (notes plus\nsdist/wheel artifacts), the PyPI and TestPyPI project pages, and the MCP\nRegistry listing."
          }
        ],
        "text": "Informed"
      },
      "text": "Roles and Responsibilities"
    },
    "safety_and_precautions": {
      "text": "## Safety and Precautions\n\n- **Tag push is irreversible.** Pushing the tag immediately starts\n  publication to TestPyPI, PyPI, and the MCP Registry. A published version\n  cannot be retracted, only superseded by a newer one. Never push a tag\n  whose preconditions (Steps 1–5) have not all succeeded.\n- **Merge fast-forward only.** Never create a merge commit or squash-merge\n  when merging `dev` into `main` — a commit unique to `main` breaks the\n  fast-forward invariant and poisons every later release. The script\n  enforces this with `gh pr merge --ff-only`; manual mode uses\n  `git merge --ff-only dev`.\n- **Never double-bump.** If `pyproject.toml` already carries the target\n  version, the `bump` stage refuses to run. If a stage failed mid-release,\n  resume from the failed stage — every stage is idempotent, and\n  `scripts/release.sh status <version>` shows where the release stands —\n  rather than restarting the flow from scratch.\n- **An empty `[Unreleased]` section is a stop condition.** A release that\n  documents nothing is almost always a mistake; the `changelog` stage\n  refuses to proceed without explicit confirmation (and fails outright in\n  non-interactive mode).\n- **The release commit is exactly three files.** Any other pending change\n  in the working tree means unfinished work would be mixed into the\n  release; the pre-check and `commit-push` stages assert the tree state\n  and stop otherwise.\n- **CI failures stop the release.** A red build on `dev` or on the release\n  pull request is never force-merged or skipped: diagnose, fix on `dev`,\n  and resume from the failed stage.\n"
    },
    "procedure": {
      "steps": [
        {
          "text": "### Step 1: Resolve and confirm the target version\n\nStart from the maintainer's decision: either a full semantic version\n(`0.15.0`) or a bump keyword (`patch`/`minor`/`major`).\n\n**Automated:** `scripts/release.sh resolve <arg>` computes the target\nversion — the keyword is applied to the current `pyproject.toml` version\nper SemVer (e.g. `0.14.0` + `minor` → `0.15.0`) — and prints it without\nmutating anything. The agent then confirms the resolved number with the\nmaintainer before anything else runs; a keyword that produces a\nsurprising number (e.g. `major` on a `0.x` version → `1.0.0`) must be\nexplicitly acknowledged.\n\n**Manual fallback:** read the `version` field of `pyproject.toml`, apply\nthe SemVer bump by hand, and record the target version.\n",
          "number": 1,
          "name": "Resolve and confirm the target version"
        },
        {
          "text": "### Step 2: Run the pre-release checks\n\n**Automated:** `scripts/release.sh precheck` verifies, in order: (a) the\ncheckout is on `dev` with a clean tree in sync with `origin/dev`; (b)\n`origin/main` is an ancestor of `origin/dev` (the fast-forward\ninvariant); (c) the latest CI run on `dev` is green (waiting for an\nin-flight run, polling every 30 s); (d) the tag `vX.Y.Z` exists neither\nlocally nor on `origin`; (e) `uv lock --check` passes, i.e. `uv.lock` is\nin sync with `pyproject.toml` before the bump; (f) the `uv` and `gh` CLIs\nare present and `gh` is authenticated. Any failure stops the release with\na diagnostic.\n\n**Manual fallback:** run the checks individually: `git status`;\n`git fetch && git merge-base --is-ancestor origin/main origin/dev`;\n`gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and\n`git ls-remote --tags origin vX.Y.Z`; `uv lock --check`;\n`gh auth status`.\n",
          "number": 2,
          "name": "Run the pre-release checks"
        },
        {
          "text": "### Step 3: Curate the changelog\n\nBring the `[Unreleased]` section of `CHANGELOG.md` to the point where it\nfully describes everything user-visible since the last tag, organized\nunder Keep a Changelog categories (`Added`, `Changed`, `Deprecated`,\n`Removed`, `Fixed`, `Security`).\n\n**Automated:** the agent (not the script) performs this step. It diffs\n`git log <last-tag>..HEAD --oneline` against the existing `[Unreleased]`\nentries, adds missing items, rewrites internal or verbose entries into\nuser-facing prose, and presents the finished section to the maintainer for\nreview. This is the only step in which the agent edits a file directly.\n\n**Manual fallback:** edit the `[Unreleased]` section by hand to the same\nstandard.\n",
          "number": 3,
          "name": "Curate the changelog"
        },
        {
          "text": "### Step 4: Bump the version and sync the lockfile\n\n**Automated:** `scripts/release.sh bump <X.Y.Z>` sets the `version` field\nof `pyproject.toml` (asserting exactly one version line exists, and\nrefusing if the current version already equals the target), runs\n`uv lock`, and asserts the resulting `uv.lock` diff is only the version\nline. The stage tolerates the dirty `CHANGELOG.md` left by Step 3.\n\n**Manual fallback:** edit the `version` field of `pyproject.toml` to\n`X.Y.Z`; run `uv lock`; verify via `git diff uv.lock` that only the\n`biz-dfch-specmgr` version entry changed.\n",
          "number": 4,
          "name": "Bump the version and sync the lockfile"
        },
        {
          "text": "### Step 5: Finalize the changelog, commit, push, and wait for CI\n\n**Automated:** `scripts/release.sh changelog <X.Y.Z>` mechanically moves\nthe `[Unreleased]` content into a new dated section\n`## [X.Y.Z] - YYYY-MM-DD` directly under a re-emptied `## [Unreleased]`\nheader (refusing an empty section — see Safety and Precautions). Then\n`scripts/release.sh commit-push <X.Y.Z>` asserts the working-tree changes\nare exactly the three release files, commits them as\n`chore(release): bump version to vX.Y.Z`, pushes `dev`, and waits for the\npush-triggered CI run (the lint/tests/docs-drift matrix), polling every\n30 s.\n\n**Manual fallback:** move the section by hand (this repo uses no compare-\nlink references in the changelog); `git add pyproject.toml uv.lock CHANGELOG.md`; commit with the conventional message; `git push origin dev`; watch the Actions run until green.\n\nA red build stops the release: fix on `dev` and resume from the failed\nstage.\n",
          "number": 5,
          "name": "Finalize the changelog, commit, push, and wait for CI"
        },
        {
          "text": "### Step 6: Merge `dev` into `main` (pull request, fast-forward only, with merge gate)\n\n**Automated:** `scripts/release.sh pr-create <X.Y.Z>` creates — or resumes\n— the `dev` → `main` pull request with the new dated changelog section as\nthe pull request body, waits until the pull request's checks are green\n(30 s polling), and prints the pull request URL and head SHA — without\nmerging. The agent then presents the pull request and the changelog\nsection to the maintainer and asks for the merge gate. Once approved,\n`scripts/release.sh pr-merge <X.Y.Z>` performs\n`gh pr merge --ff-only`.\n\n**Manual fallback:** `gh pr create --base main --head dev` (body: the new\nchangelog section); wait for green checks; present to the maintainer; on\napproval, `git checkout main && git merge --ff-only dev && git push origin main`. Never use `--no-ff`, squash, or rebase merges.\n",
          "number": 6,
          "name": "Merge `dev` into `main` (pull request, fast-forward only, with merge gate)"
        },
        {
          "text": "### Step 7: Tag the release and push the tag\n\n**Automated:** `scripts/release.sh tag-push <X.Y.Z>` checks out `main`,\nruns `git pull --ff-only` (main now equals dev), creates the lightweight\ntag `vX.Y.Z` at `main`'s HEAD, pushes the tag, and switches back to\n`dev`.\n\n**Manual fallback:** `git checkout main && git pull --ff-only && git tag vX.Y.Z && git push origin vX.Y.Z && git checkout dev`.\n\nWarning: pushing the tag immediately starts publication (Step 8); the\nrelease is irreversible from here.\n",
          "number": 7,
          "name": "Tag the release and push the tag"
        },
        {
          "text": "### Step 8: Wait for the publication jobs\n\n**Automated:** `scripts/release.sh publish-wait <X.Y.Z>` waits for the\n`publish.yml` run triggered by the tag — *Publish to TestPyPI* →\n*Publish to PyPI* → *Make GitHub Release* (attaches the sdist and wheel)\n→ *Publish to MCP Registry* (updates `server.json`'s version and\npublishes via OIDC) — polling every 30 s until all four jobs complete.\n\n**Manual fallback:** watch the `publish.yml` Actions run for the tag until\nall four jobs are green.\n\nAny failed job stops the release: report the run URL, diagnose from its\nlogs, and escalate to the maintainer. The tag already exists, so the\nremedy is never re-tagging — it is a fix plus a new, higher version.\n",
          "number": 8,
          "name": "Wait for the publication jobs"
        },
        {
          "text": "### Step 9: Verify the publication and finalize the release notes\n\n**Automated:** `scripts/release.sh release-notes <X.Y.Z>` verifies the\nGitHub Release exists with both artifacts (sdist and wheel), sets the\nrelease notes to the new dated changelog section's content\n(`gh release edit`), and prints the final summary: version, tag, GitHub\nRelease URL, PyPI and TestPyPI project URLs, and the MCP Registry\nlisting.\n\n**Manual fallback:** open the GitHub Release, confirm both assets are\nattached, and paste the new changelog section into the release body.\n\nThe release is complete when all four publication targets are reachable\nand the maintainer is informed.\n",
          "number": 9,
          "name": "Verify the publication and finalize the release notes"
        }
      ],
      "text": "Procedure"
    },
    "related_artifacts": null,
    "more_information": {
      "text": "## More Information\n\nThe staged script and the `/release` command are projections of this SOP:\nthe SOP is the normative procedure, and where the two ever disagree the\nSOP wins and the script/command must be corrected. Stages are named to\nmirror the step order so that drift between the document and its\nimplementations stays visible.\n\nThe `sop` tooling that manages this document (the `specmgr-test` MCP\nserver) runs against this repository's own dev tree; until the first\nrelease ships the `sop` domain to PyPI, this SOP is created and validated\ndirectly against the local checkout.\n"
    },
    "updates": {
      "updates": [
        {
          "content": {
            "text": "Created as the normative procedure for releasing `biz-dfch-specmgr`,\nconsolidating the previously hand-run README \"Make a Release\" steps\n(direct merge plus tag) with the new automation: the staged\n`scripts/release.sh`, the `/release` OpenCode command with its\nagent-judgment steps (version confirmation, changelog curation, merge\ngate, failure triage), and the pull-request-plus-fast-forward-only merge\nstrategy that keeps `main` a strict ancestor of `dev`. Status is\n`draft`; the SOP is activated once the first release executed under it\nsucceeds end to end (expected to be v0.15.0, the first release to carry\nthe `sop` domain itself)."
          },
          "text": "2026-08-31 15:19:05.000+02:00 — Created",
          "timestamp": "2026-08-31 15:19:05.000+02:00",
          "title": "Created"
        }
      ],
      "text": "Updates"
    },
    "text": "Perform a release of biz.dfch.SpecMgr"
  }
}
```

**Tool: bash**

**Input:**

```json
{
  "command": "sed -n '/^## Make a Release/,/^### Manual fallback/p' README.md | head -30; echo ...; gh run list --limit 3 --json headBranch,status,conclusion,name --jq '.[] | select(.headBranch == \"dev\") | [.status, (.conclusion // \"-\"), .name] | @tsv' | head -3"
}
```

**Output:**

```
## Make a Release

The normative release procedure is the SOP
[Perform a release of biz.dfch.SpecMgr](docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md)
(SOP `98537416`). Where this section, the script, or the command ever
disagree with the SOP, the SOP wins.

### Using the OpenCode command (recommended)

```

/release [X.Y.Z | patch | minor | major] [--dry-run]

````

The command drives the staged script and performs the SOP's agent-judgment
steps: it confirms the resolved version with you, curates the changelog's
`[Unreleased]` section, pauses at the merge gate before `dev` is merged
into `main`, and triages failures without ever auto-retrying.

### Using the script directly

Each SOP step maps to a deterministic, idempotent stage (the SOP carries
a manual fallback command for every step):

```bash
scripts/release.sh resolve minor         # print the target version (e.g. 0.15.0); no mutation
scripts/release.sh precheck 0.15.0       # fail-fast pre-release checks
scripts/release.sh bump 0.15.0           # pyproject.toml + uv.lock
scripts/release.sh changelog 0.15.0      # [Unreleased] -> dated section
scripts/release.sh commit-push 0.15.0    # 3-file release commit, push dev, wait for CI
scripts/release.sh pr-create 0.15.0      # dev->main release PR, wait for checks (no merge)
...
in_progress		Lint and Test
completed	success	Lint and Test
completed	success	Lint and Test

````

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 104.8s)

_Thinking:_

All verified:

- The SOP re-parses perfectly on the live MCP server (the entire structure round-trips).
- The README section renders correctly.
- dev CI: the latest run is in_progress (due to my 6e614d3 push), the previous two are green.

One thing I noticed while reviewing the SOP's parse output: the manual fallback for step 2 lists `gh run list --branch dev --limit 1` — but the gh CLI on this machine doesn't support --branch on run list (that's exactly why I fixed the script). The SOP's manual command should be accurate. Let me fix this line in the SOP: replace `gh run list --branch dev --limit 1` with the headBranch filter form:
`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == "dev")] | .[0]'`

I can update the SOP via specmgr-test_update (whole-body) or a targeted edit. Easiest: directly edit the file with the edit tool (the SOP file is on disk; the "write persists byte-for-byte" surface — the SOP domain has a generic update tool, but editing the file directly and re-parsing is equivalent; however, to stay within the domain's sanctioned tooling, use specmgr-test_update with a line range? The update tool replaces a line range of the body. Simpler and safer: direct file edit + re-verify with parse_sop. Actually — the sanctioned route for whole-body domains is the generic `update` tool. But a direct file edit of a document managed by specmgr is… per AGENTS.md, direct editing is only sanctioned for feat; for other domains, writes are via the tool. Use specmgr-test_update with begin/end on the specific line.

The line in question inside the SOP file: search for "gh run list --branch dev --limit 1". Body line numbers (the update tool indexes body lines, i.e., after the front matter). Let me grep the file.

All verifications passed, and the SOP round-trips perfectly through the live MCP parser. However, one accuracy fix is needed: the manual fallback in SOP Step 2 still lists `gh run list --branch dev`, but this isn't supported by the installed `gh` (which is exactly the reason the script needed a `headBranch` filter). Fixing it via the domain's update tool:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"gh run list --branch dev --limit 1\" docs/sop/*.md"
}
```

**Output:**

```
164:`gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 84.0s)

_Thinking:_

Line 164 of the file. The frontmatter is 8 lines (--- created id status type updated version --- = 8 lines). So line 1 of the body = line 9 of the file. File line 164 = body line 156.

Replace body line 156 (file line 164) with the following content:
`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == "dev")] | .[0]'`; `git tag -l vX.Y.Z` and

Use specmgr-test_update with begin=156, end=156.

**Tool: specmgr-test_update**

**Input:**

```json
{
  "content": "`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == \"dev\")] | .[0]'` (this `gh` version has no `--branch` flag); `git tag -l vX.Y.Z` and",
  "id": "98537416-0e6e-4a02-925f-974a17bfa10a",
  "type": "sop",
  "begin": 156,
  "end": 156
}
```

**Output:**

```
{
  "frontmatter": {
    "id": "98537416-0e6e-4a02-925f-974a17bfa10a",
    "type": "sop",
    "created": "2026-08-31T15:24:14.582592",
    "updated": "2026-08-31T16:30:30.599226",
    "status": "draft",
    "version": "1.0.0"
  },
  "body": {
    "purpose": {
      "text": "## Purpose\n\nThis procedure defines how a new version of `biz-dfch-specmgr` is released\nfrom the `dev` branch to TestPyPI, PyPI, a GitHub Release, and the MCP\nRegistry. It exists so that every release — whether driven by the release\nagent through the staged `scripts/release.sh` script or performed manually\nby the maintainer — passes the same gates (green CI on `dev` and on the\nmerge pull request, the fast-forward invariant between `main` and `dev`, a\ncurated changelog, and a verified publication) and produces the same\nreproducible outcome.\n"
    },
    "scope": {
      "text": "## Scope\n\nThis SOP covers: resolving the target version; pre-release checks;\ncurating the `CHANGELOG.md` `[Unreleased]` section; bumping the version in\n`pyproject.toml` and syncing `uv.lock`; committing and pushing the release\nto `dev`; merging `dev` into `main` through a fast-forward-only pull\nrequest; creating and pushing the `vX.Y.Z` tag on `main`; waiting for the\nfour publication jobs of `.github/workflows/publish.yml`; and setting the\nGitHub Release notes.\n\nIt does not cover: deciding whether the changes warrant a patch, minor, or\nmajor version (a maintainer decision made before this SOP is invoked); the\nhotfix/backport path (no such path is defined yet — should one ever be\nneeded, it is an exception to this SOP and must be recorded in its\n`Updates`); and the internals of the `publish.yml` workflow (OIDC trusted\npublishing, `server.json` generation).\n"
    },
    "definitions": {
      "text": "## Definitions\n\n- **Release commit**: the single commit on `dev` touching exactly three\n  files — `pyproject.toml`, `uv.lock`, `CHANGELOG.md` — with the message\n  `chore(release): bump version to vX.Y.Z`.\n- **Fast-forward invariant**: `main` is always an ancestor of `dev`, i.e.\n  `main` carries no unique commits. The invariant is what makes the\n  `dev` → `main` merge possible in fast-forward-only form, and it must\n  hold before every release.\n- **Stage**: a subcommand of `scripts/release.sh` (e.g. `precheck`,\n  `bump`, `pr-merge`). Stages mirror the steps of this procedure one-to-\n  one, are idempotent (a completed stage reports \"done\" instead of\n  re-running), and are the only sanctioned way for the agent to perform\n  release mechanics.\n- **`/release`**: the OpenCode command (`.opencode/command/release.md`)\n  that drives the stages and performs this SOP's agent-judgment steps\n  (version confirmation, changelog curation, merge gate, failure triage).\n- **Publication jobs**: the four jobs of\n  `.github/workflows/publish.yml`, triggered by pushing a `v*` tag:\n  *Publish to TestPyPI* → *Publish to PyPI* → *Make GitHub Release* →\n  *Publish to MCP Registry*.\n- **`[Unreleased]` section**: the Keep a Changelog staging area at the top\n  of `CHANGELOG.md` that accumulates notable changes between releases.\n- **Merge gate**: the maintainer's explicit go-ahead to merge the release\n  pull request, given after the agent presents it (Step 6).\n"
    },
    "roles_and_responsibilities": {
      "accountable": {
        "value": {
          "text": "The repository maintainer (`dfch`) is accountable for every release and\nfor the continued validity of this procedure: they make the version\ndecision, confirm the resolved version number (Step 1), approve the merge\ngate (Step 6), and adjudicate any exception."
        },
        "text": "Accountable"
      },
      "responsible": {
        "items": [
          {
            "text": "The release agent (the OpenCode session executing `/release`) runs the\nstages in order, performs the changelog curation (Step 3), and reports\nprogress and failures. In manual mode the maintainer performs every\nstep themselves."
          }
        ],
        "text": "Responsible"
      },
      "support": {
        "items": [
          {
            "text": "`scripts/release.sh` — the deterministic stage implementations\n(pre-checks, file edits, git/gh mechanics, CI polling)."
          },
          {
            "text": "GitHub Actions — `ci.yml` (lint, tests, and docs-drift checks on `dev`\nand on the pull request) and `publish.yml` (the four publication jobs)."
          },
          {
            "text": "The `uv` and `gh` CLIs, and the external publication targets: TestPyPI\nand PyPI (both via OIDC trusted publishing) and the MCP Registry (via\n`mcp-publisher` with GitHub OIDC)."
          }
        ],
        "text": "Support"
      },
      "consulted": {
        "items": [
          {
            "text": "The maintainer is consulted at exactly two gates: the version\nconfirmation after `resolve` (Step 1) and the merge gate after\n`pr-create` (Step 6)."
          }
        ],
        "text": "Consulted"
      },
      "informed": {
        "items": [
          {
            "text": "Downstream consumers are informed via the GitHub Release (notes plus\nsdist/wheel artifacts), the PyPI and TestPyPI project pages, and the MCP\nRegistry listing."
          }
        ],
        "text": "Informed"
      },
      "text": "Roles and Responsibilities"
    },
    "safety_and_precautions": {
      "text": "## Safety and Precautions\n\n- **Tag push is irreversible.** Pushing the tag immediately starts\n  publication to TestPyPI, PyPI, and the MCP Registry. A published version\n  cannot be retracted, only superseded by a newer one. Never push a tag\n  whose preconditions (Steps 1–5) have not all succeeded.\n- **Merge fast-forward only.** Never create a merge commit or squash-merge\n  when merging `dev` into `main` — a commit unique to `main` breaks the\n  fast-forward invariant and poisons every later release. The script\n  enforces this with `gh pr merge --ff-only`; manual mode uses\n  `git merge --ff-only dev`.\n- **Never double-bump.** If `pyproject.toml` already carries the target\n  version, the `bump` stage refuses to run. If a stage failed mid-release,\n  resume from the failed stage — every stage is idempotent, and\n  `scripts/release.sh status <version>` shows where the release stands —\n  rather than restarting the flow from scratch.\n- **An empty `[Unreleased]` section is a stop condition.** A release that\n  documents nothing is almost always a mistake; the `changelog` stage\n  refuses to proceed without explicit confirmation (and fails outright in\n  non-interactive mode).\n- **The release commit is exactly three files.** Any other pending change\n  in the working tree means unfinished work would be mixed into the\n  release; the pre-check and `commit-push` stages assert the tree state\n  and stop otherwise.\n- **CI failures stop the release.** A red build on `dev` or on the release\n  pull request is never force-merged or skipped: diagnose, fix on `dev`,\n  and resume from the failed stage.\n"
    },
    "procedure": {
      "steps": [
        {
          "text": "### Step 1: Resolve and confirm the target version\n\nStart from the maintainer's decision: either a full semantic version\n(`0.15.0`) or a bump keyword (`patch`/`minor`/`major`).\n\n**Automated:** `scripts/release.sh resolve <arg>` computes the target\nversion — the keyword is applied to the current `pyproject.toml` version\nper SemVer (e.g. `0.14.0` + `minor` → `0.15.0`) — and prints it without\nmutating anything. The agent then confirms the resolved number with the\nmaintainer before anything else runs; a keyword that produces a\nsurprising number (e.g. `major` on a `0.x` version → `1.0.0`) must be\nexplicitly acknowledged.\n\n**Manual fallback:** read the `version` field of `pyproject.toml`, apply\nthe SemVer bump by hand, and record the target version.\n",
          "number": 1,
          "name": "Resolve and confirm the target version"
        },
        {
          "text": "### Step 2: Run the pre-release checks\n\n**Automated:** `scripts/release.sh precheck` verifies, in order: (a) the\ncheckout is on `dev` with a clean tree in sync with `origin/dev`; (b)\n`origin/main` is an ancestor of `origin/dev` (the fast-forward\ninvariant); (c) the latest CI run on `dev` is green (waiting for an\nin-flight run, polling every 30 s); (d) the tag `vX.Y.Z` exists neither\nlocally nor on `origin`; (e) `uv lock --check` passes, i.e. `uv.lock` is\nin sync with `pyproject.toml` before the bump; (f) the `uv` and `gh` CLIs\nare present and `gh` is authenticated. Any failure stops the release with\na diagnostic.\n\n**Manual fallback:** run the checks individually: `git status`;\n`git fetch && git merge-base --is-ancestor origin/main origin/dev`;\n`gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and\n`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == \"dev\")] | .[0]'` (this `gh` version has no `--branch` flag); `git tag -l vX.Y.Z` and\n`gh auth status`.\n",
          "number": 2,
          "name": "Run the pre-release checks"
        },
        {
          "text": "### Step 3: Curate the changelog\n\nBring the `[Unreleased]` section of `CHANGELOG.md` to the point where it\nfully describes everything user-visible since the last tag, organized\nunder Keep a Changelog categories (`Added`, `Changed`, `Deprecated`,\n`Removed`, `Fixed`, `Security`).\n\n**Automated:** the agent (not the script) performs this step. It diffs\n`git log <last-tag>..HEAD --oneline` against the existing `[Unreleased]`\nentries, adds missing items, rewrites internal or verbose entries into\nuser-facing prose, and presents the finished section to the maintainer for\nreview. This is the only step in which the agent edits a file directly.\n\n**Manual fallback:** edit the `[Unreleased]` section by hand to the same\nstandard.\n",
          "number": 3,
          "name": "Curate the changelog"
        },
        {
          "text": "### Step 4: Bump the version and sync the lockfile\n\n**Automated:** `scripts/release.sh bump <X.Y.Z>` sets the `version` field\nof `pyproject.toml` (asserting exactly one version line exists, and\nrefusing if the current version already equals the target), runs\n`uv lock`, and asserts the resulting `uv.lock` diff is only the version\nline. The stage tolerates the dirty `CHANGELOG.md` left by Step 3.\n\n**Manual fallback:** edit the `version` field of `pyproject.toml` to\n`X.Y.Z`; run `uv lock`; verify via `git diff uv.lock` that only the\n`biz-dfch-specmgr` version entry changed.\n",
          "number": 4,
          "name": "Bump the version and sync the lockfile"
        },
        {
          "text": "### Step 5: Finalize the changelog, commit, push, and wait for CI\n\n**Automated:** `scripts/release.sh changelog <X.Y.Z>` mechanically moves\nthe `[Unreleased]` content into a new dated section\n`## [X.Y.Z] - YYYY-MM-DD` directly under a re-emptied `## [Unreleased]`\nheader (refusing an empty section — see Safety and Precautions). Then\n`scripts/release.sh commit-push <X.Y.Z>` asserts the working-tree changes\nare exactly the three release files, commits them as\n`chore(release): bump version to vX.Y.Z`, pushes `dev`, and waits for the\npush-triggered CI run (the lint/tests/docs-drift matrix), polling every\n30 s.\n\n**Manual fallback:** move the section by hand (this repo uses no compare-\nlink references in the changelog); `git add pyproject.toml uv.lock CHANGELOG.md`; commit with the conventional message; `git push origin dev`; watch the Actions run until green.\n\nA red build stops the release: fix on `dev` and resume from the failed\nstage.\n",
          "number": 5,
          "name": "Finalize the changelog, commit, push, and wait for CI"
        },
        {
          "text": "### Step 6: Merge `dev` into `main` (pull request, fast-forward only, with merge gate)\n\n**Automated:** `scripts/release.sh pr-create <X.Y.Z>` creates — or resumes\n— the `dev` → `main` pull request with the new dated changelog section as\nthe pull request body, waits until the pull request's checks are green\n(30 s polling), and prints the pull request URL and head SHA — without\nmerging. The agent then presents the pull request and the changelog\nsection to the maintainer and asks for the merge gate. Once approved,\n`scripts/release.sh pr-merge <X.Y.Z>` performs\n`gh pr merge --ff-only`.\n\n**Manual fallback:** `gh pr create --base main --head dev` (body: the new\nchangelog section); wait for green checks; present to the maintainer; on\napproval, `git checkout main && git merge --ff-only dev && git push origin main`. Never use `--no-ff`, squash, or rebase merges.\n",
          "number": 6,
          "name": "Merge `dev` into `main` (pull request, fast-forward only, with merge gate)"
        },
        {
          "text": "### Step 7: Tag the release and push the tag\n\n**Automated:** `scripts/release.sh tag-push <X.Y.Z>` checks out `main`,\nruns `git pull --ff-only` (main now equals dev), creates the lightweight\ntag `vX.Y.Z` at `main`'s HEAD, pushes the tag, and switches back to\n`dev`.\n\n**Manual fallback:** `git checkout main && git pull --ff-only && git tag vX.Y.Z && git push origin vX.Y.Z && git checkout dev`.\n\nWarning: pushing the tag immediately starts publication (Step 8); the\nrelease is irreversible from here.\n",
          "number": 7,
          "name": "Tag the release and push the tag"
        },
        {
          "text": "### Step 8: Wait for the publication jobs\n\n**Automated:** `scripts/release.sh publish-wait <X.Y.Z>` waits for the\n`publish.yml` run triggered by the tag — *Publish to TestPyPI* →\n*Publish to PyPI* → *Make GitHub Release* (attaches the sdist and wheel)\n→ *Publish to MCP Registry* (updates `server.json`'s version and\npublishes via OIDC) — polling every 30 s until all four jobs complete.\n\n**Manual fallback:** watch the `publish.yml` Actions run for the tag until\nall four jobs are green.\n\nAny failed job stops the release: report the run URL, diagnose from its\nlogs, and escalate to the maintainer. The tag already exists, so the\nremedy is never re-tagging — it is a fix plus a new, higher version.\n",
          "number": 8,
          "name": "Wait for the publication jobs"
        },
        {
          "text": "### Step 9: Verify the publication and finalize the release notes\n\n**Automated:** `scripts/release.sh release-notes <X.Y.Z>` verifies the\nGitHub Release exists with both artifacts (sdist and wheel), sets the\nrelease notes to the new dated changelog section's content\n(`gh release edit`), and prints the final summary: version, tag, GitHub\nRelease URL, PyPI and TestPyPI project URLs, and the MCP Registry\nlisting.\n\n**Manual fallback:** open the GitHub Release, confirm both assets are\nattached, and paste the new changelog section into the release body.\n\nThe release is complete when all four publication targets are reachable\nand the maintainer is informed.\n",
          "number": 9,
          "name": "Verify the publication and finalize the release notes"
        }
      ],
      "text": "Procedure"
    },
    "related_artifacts": null,
    "more_information": {
      "text": "## More Information\n\nThe staged script and the `/release` command are projections of this SOP:\nthe SOP is the normative procedure, and where the two ever disagree the\nSOP wins and the script/command must be corrected. Stages are named to\nmirror the step order so that drift between the document and its\nimplementations stays visible.\n\nThe `sop` tooling that manages this document (the `specmgr-test` MCP\nserver) runs against this repository's own dev tree; until the first\nrelease ships the `sop` domain to PyPI, this SOP is created and validated\ndirectly against the local checkout.\n"
    },
    "updates": {
      "updates": [
        {
          "content": {
            "text": "Created as the normative procedure for releasing `biz-dfch-specmgr`,\nconsolidating the previously hand-run README \"Make a Release\" steps\n(direct merge plus tag) with the new automation: the staged\n`scripts/release.sh`, the `/release` OpenCode command with its\nagent-judgment steps (version confirmation, changelog curation, merge\ngate, failure triage), and the pull-request-plus-fast-forward-only merge\nstrategy that keeps `main` a strict ancestor of `dev`. Status is\n`draft`; the SOP is activated once the first release executed under it\nsucceeds end to end (expected to be v0.15.0, the first release to carry\nthe `sop` domain itself)."
          },
          "text": "2026-08-31 15:19:05.000+02:00 — Created",
          "timestamp": "2026-08-31 15:19:05.000+02:00",
          "title": "Created"
        }
      ],
      "text": "Updates"
    },
    "text": "Perform a release of biz.dfch.SpecMgr"
  }
}
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 116.8s)

_Thinking:_

The line range replacement produced a duplicated/incorrect line! Looking at the text of step 2:

```
`gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and
`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == "dev")] | .[0]'` (this `gh` version has no `--branch` flag); `git tag -l vX.Y.Z` and
`gh auth status`.
```

The original file was wrapping the line like this:

```
`gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and
`git ls-remote --tags origin vX.Y.Z`; `uv lock --check`;
`gh auth status`.
```

My body-line calculation was off by one line: the line I replaced (body line 156) was actually the second line of the wrapped command list, i.e. the line containing `git tag -l vX.Y.Z` and — no wait. Let me look at what happened: the current text shows the old line 1 (`gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and), then my new line (which ends with `git tag -l vX.Y.Z` and), and then `gh auth status`. So the original wrapped block was:

Line A: `git fetch && git merge-base --is-ancestor origin/main origin/dev`;
Line B: `gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and
Line C: `git ls-remote --tags origin vX.Y.Z`; `uv lock --check`;
Line D: `gh auth status`.

I replaced line C (body line 156) with the new text — so now the result is:
Line B: `gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and
Line C': the new gh run list... (this `gh` version has no `--branch` flag); `git tag -l vX.Y.Z` and
Line D: `gh auth status`.

This is broken: the old `--branch` command still exists, `git tag -l` is duplicated, and `git ls-remote --tags origin vX.Y.Z` and `uv lock --check` are completely lost!

I need to cleanly rewrite the entire manual fallback block of step 2. Best approach: use specmgr-test_update to replace the whole range of the manual-fallback paragraph of step 2 with the correct text. Or even simpler: directly edit the file with the `edit` tool, then re-parse to verify. The SOP domain persists the body byte-for-byte as-is, and `update` splices the lines, so either route gives the same result. For a multi-line replacement, the `edit` tool is more reliable.

The correct manual fallback block for step 2:

```
**Manual fallback:** run the checks individually: `git status`;
`git fetch && git merge-base --is-ancestor origin/main origin/dev`;
`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == "dev")] | .[0]'` (this `gh` version has no `--branch` flag); `git tag -l vX.Y.Z` and
`git ls-remote --tags origin vX.Y.Z`; `uv lock --check`;
`gh auth status`.
```

First let me check the current state of the file around that area, then fix it with `edit`, and then verify with parse_sop.

My line-range calculation was off by one line — this replacement ended up corrupting the manual fallback block of Step 2 (the old `--branch` line is still there, `git tag -l` is duplicated, and `git ls-remote`/`uv lock --check` are lost). I'll check the file and fix it properly:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"Manual fallback: run the checks\" -A 7 docs/sop/*.md"
}
```

**Output:**

```
(no output)
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 77.3s)

_Thinking:_

No output? So the text is different on disk. Maybe the file on disk uses a different line-wrapping than what I'm assuming. Let me actually look at the Step 2 section in the file.

**Tool: bash**

**Input:**

```json
{
  "command": "sed -n '/Step 2/,/Step 3/p' docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md"
}
```

**Output:**

```
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
`gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and
`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == "dev")] | .[0]'` (this `gh` version has no `--branch` flag); `git tag -l vX.Y.Z` and
`gh auth status`.

### Step 3: Curate the changelog

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 100.0s)

_Thinking:_

I can confirm the corruption. The manual fallback block is as follows:

```
**Manual fallback:** Run each check individually: `git status`;
`git fetch && git merge-base --is-ancestor origin/main origin/dev`;
`gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and
`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == "dev")] | .[0]'` (this version of `gh` does not have a `--branch` flag); `git tag -l vX.Y.Z` and
`gh auth status`.
```

The original lines `git ls-remote --tags origin vX.Y.Z`; `uv lock --check`; were on the line I replaced. I'll fix it with an edit tool that replaces the entire block:

oldString:

```
**Manual fallback:** Run each check individually: `git status`;
`git fetch && git merge-base --is-ancestor origin/main origin/dev`;
`gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and
`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == "dev")] | .[0]'` (this version of `gh` does not have a `--branch` flag); `git tag -l vX.Y.Z` and
`gh auth status`.
```

newString:

```
**Manual fallback:** Run each check individually: `git status`;
`git fetch && git merge-base --is-ancestor origin/main origin/dev`;
`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == "dev")] | .[0]'` (this version of `gh` does not have a `--branch` flag); `git tag -l vX.Y.Z` and
`git ls-remote --tags origin vX.Y.Z`; `uv lock --check`;
`gh auth status`.
```

After that, I'll verify with parse_sop.

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md",
  "oldString": "**Manual fallback:** run the checks individually: `git status`;\n`git fetch && git merge-base --is-ancestor origin/main origin/dev`;\n`gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and\n`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == \"dev\")] | .[0]'` (this `gh` version has no `--branch` flag); `git tag -l vX.Y.Z` and\n`gh auth status`.",
  "newString": "**Manual fallback:** run the checks individually: `git status`;\n`git fetch && git merge-base --is-ancestor origin/main origin/dev`;\n`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == \"dev\")] | .[0]'` (this `gh` version has no `--branch` flag); `git tag -l vX.Y.Z` and\n`git ls-remote --tags origin vX.Y.Z`; `uv lock --check`;\n`gh auth status`."
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 84.0s)

_Thinking:_

I need to investigate this further. Let me check the details.

Next, I'll verify that the fixed SOP parses correctly, and that step 2's text is as intended:

Verifying the fix round-trips through the SOP parser:

**Tool: bash**

**Input:**

```json
{
  "command": "sed -n '/Manual fallback: run the checks/,/^$/p' docs/sop/*.md && uv run --frozen --all-extras python -c \"\nfrom biz.dfch.specmgr.sop.models.v1 import parse_sop\nfrom pathlib import Path\ndoc = parse_sop(Path('docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md'))\ns2 = doc.body.procedure.steps[1].text\nassert '--branch' not in s2.replace('--branch` flag', ''), s2\nassert s2.count('git tag -l') == 1\nassert 'git ls-remote --tags origin' in s2 and 'uv lock --check' in s2\nprint('parse OK; step 2 verified')\n\""
}
```

**Output:**

```
/bin/bash: -c: line 6: unexpected EOF while looking for matching ``'
/bin/bash: -c: line 11: syntax error: unexpected end of file

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 85.6s)

_Thinking:_

bash quoting issue — the Python code contains backticks (inside the assert string `'--branch` flag'`). Backticks inside bash double quotes... I wrapped the Python code in double quotes `"\`, so the backticks ended up being interpreted by bash as command substitution. Instead, I'll write a small verification script out to a temp file.

Backticks in my inline Python got eaten by bash — using a temp script instead:

**Tool: write**

**Input:**

```json
{
  "content": "from pathlib import Path\n\nfrom biz.dfch.specmgr.sop.models.v1 import parse_sop\n\ndoc = parse_sop(Path(\"docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md\"))\ns2 = doc.body.procedure.steps[1].text\nassert s2.count(\"gh run list\") == 1, s2\nassert s2.count(\"git tag -l\") == 1, s2\nassert \"git ls-remote --tags origin\" in s2, s2\nassert \"uv lock --check\" in s2, s2\nprint(\"parse OK; step 2 manual fallback verified\")\n",
  "filePath": "/tmp/opencode/verify_sop.py"
}
```

**Output:**

```
Wrote file successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 83.2s)

_Thinking:_

Wait — my assertion `s2.count("gh run list") == 1` — s2 is the text of the entire step (automated + manual). The automated part says "the latest CI run on `dev` is green", but there's no "gh run list" in there. The manual part has one "gh run list". So count == 1 ✓. And the text also includes "(this `gh` version has no `--branch` flag)" — no problem, no assertion needed.

Run it.

**Tool: bash**

**Input:**

```json
{
  "command": "uv run --frozen --all-extras python /tmp/opencode/verify_sop.py && sed -n '/Manual fallback: run the checks/,+4p' docs/sop/*.md"
}
```

**Output:**

```
   Building biz-dfch-specmgr @ file:///home/user/src/biz.dfch.SpecMgr
      Built biz-dfch-specmgr @ file:///home/user/src/biz.dfch.SpecMgr
Uninstalled 1 package in 0.79ms
Installed 1 package in 3ms
Traceback (most recent call last):
  File "/tmp/opencode/verify_sop.py", line 5, in <module>
    doc = parse_sop(Path("docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md"))
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/models/v1/parser.py", line 78, in parse_sop
    body = Sop.from_text(format_text(post.content))
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_section.py", line 193, in from_text
    assert t_open.type == expected_type, f"Token[0]: expected '{expected_type}', got '{t_open.type}'."
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Token[0]: expected 'heading_open', got 'paragraph_open'.

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 117.0s)

_Thinking:_

Parse error: "Token\[0\]: expected 'heading_open', got 'paragraph_open'" — occurred at Sop.from_text, i.e., at the top level of the body. `format_text(post.content)` — post.content is the body after the frontmatter. The first token is paragraph_open, not heading_open → the body doesn't start with `# Heading`!

Did my `edit` corrupt the top of the file?? No — I only edited the Step 2 block in the middle of the file. But wait — the `specmgr-test_update` call earlier (line-range splice) — could that have rewritten the file and dropped the H1? No, the subsequent sed showed "### Step 2" fine, and the file looked normal...

Hold on — let me look at what `update` did: it spliced the body lines and then "the spliced result is validated as a whole document before anything is written." That succeeded (returned the full document). So the file after update was valid.

Then my `edit` replaced the corrupted block with the correct block. Could my edit have broken the H1? No — the edit's oldString/newString was localized to the Step 2 fallback.

Let me check the top of the file. Maybe... `format_text` (mdformat/markdown-it) normalizes the markdown, and something in my edit (e.g., unbalanced quotes or backticks) is causing markdown-it to parse the H1 differently? An unbalanced backtick somewhere could swallow the `# heading`... My new text contains the jq expression `'[.[] | select(.headBranch == "dev")] | .[0]'` inside backticks — balanced. Hmm.

Wait, actually — let me look at the original file: did it parse fine before the update? Yes — parse_sop (live MCP) succeeded right after the update (the big tool response showed the full parsed body including the corrupted Step 2). So the file after the update parsed. Therefore my edit is what broke the parse. Let me diff what changed: the file after update had the corrupted block, and my edit replaced that with a clean block. Both variants parse...? The corrupted one parsed (I confirmed via the tool response). So the clean one should parse too — unless my edit accidentally matched/replaced something else, or introduced a subtle issue.

Let me check the raw bytes at the top of the file, and try parsing again after reverting the edit... First, inspect: head -12 of the file.

Parse now fails at the very top — checking the file head (my edit was mid-file, so something subtle):

**Tool: bash**

**Input:**

```json
{
  "command": "head -14 docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md | cat -A | head -16"
}
```

**Output:**

```
---$
created: '2026-08-31T15:24:14.582592'$
id: 98537416-0e6e-4a02-925f-974a17bfa10a$
status: draft$
type: sop$
updated: '2026-08-31T16:30:30.599226'$
version: 1.0.0$
---$
$
# Perform a release of biz.dfch.SpecMgr$
$
## Purpose$
$
This procedure defines how a new version of `biz-dfch-specmgr` is released$

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 139.8s)

_Thinking:_

The top of the file is fine: frontmatter + blank line + `# Perform a release...`. So why does `Sop.from_text(format_text(post.content))` receive `paragraph_open` as the first token?

`post.content` — the body after the frontmatter. If the frontmatter splitting is treating the content differently... Wait — was this file parseable before my `edit`? The last successful parse was the `specmgr-test_update` call (which validated before writing) and the subsequent `specmgr-test_parse_sop`... no, that's wrong! The parse_sop I ran earlier was before the update (around 15:30, after creation, the big verification output — that succeeded). The update call validated the spliced result (including the broken step 2) — that also succeeded. After that, my edit replaced the broken block with a clean block — and now it fails with the first-token-is-paragraph error.

So my edit introduced a problem that affects the parsing of the entire document. The error is `Token[0]: expected 'heading_open', got 'paragraph_open'` in `Sop.from_text` — the first section of the body (Purpose, a MarkdownSection2?) — hmm, `Sop.from_text` expects the first token to be heading_open... but the body starts with `## Purpose` (H1 is consumed by the MarkdownSection1 wrapper?). Whatever — the point is: something before `## Purpose` in the formatted text is now being parsed as a paragraph.

What's before `## Purpose`? `# Perform a release of biz.dfch.SpecMgr` + a blank line. `format_text` runs markdown-it on the entire body (probably after the H1 is extracted).

Aaah, wait. I've got it. `format_text` = mdformat-style normalization via markdown-it's parse→render? If my edit left an unbalanced backtick somewhere in the document, markdown-it would treat everything from that backtick onward as an unclosed code span... An unclosed backtick within a paragraph continues to the end — but that shouldn't turn a heading into a paragraph.

Hmm, actually — a paragraph_open as the first token means the first non-empty content is being parsed as a paragraph. That is, `# Perform a release of biz.dfch.SpecMgr` is being parsed as a paragraph rather than a heading. When does markdown-it parse `# text` as a paragraph? When it's inside a code span/block, or when there's no blank line before the H1 after an unclosed construct...

Let me think about what my edit changed:

```
`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == "dev")] | .[0]'` (this `gh` version has no `--branch` flag); `git tag -l vX.Y.Z` and
`git ls-remote --tags origin vX.Y.Z`; `uv lock --check`;
```

Counting the backticks on this line: `gh run list ... .[0]'` — opens with backtick, closes with backtick → 2. `(this `gh`version has no`--branch` flag)` → 2+2=4. `git tag -l vX.Y.Z` → 2. Total 8 backticks — balanced.

Next line: `git ls-remote --tags origin vX.Y.Z` → 2, `uv lock --check` → 2. Balanced.

Hmm, everything is balanced. So why?

Wait — maybe the problem isn't my edit in the first place. Let me re-verify: could it be that `uv run --frozen --all-extras python` is using a different code path? No — parse_sop is parse_sop.

Let me test directly: parse the file right now, and also check git diff to see exactly what my edit changed relative to the last parsed state... The last parsed state (post-update, pre-my-edit) is not committed — it's in the working tree with the broken block. Let me run git diff on the SOP file to see what changed relative to the committed version (which was parsed successfully at 15:30):

Top of file is fine. Comparing against the committed (last-known-good) state to isolate what my edit actually changed:

**Tool: bash**

**Input:**

```json
{
  "command": "git diff docs/sop/ | head -40"
}
```

**Output:**

```
diff --git a/docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md b/docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md
index c8c7782..261eff8 100644
--- a/docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md
+++ b/docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md
@@ -3,7 +3,7 @@ created: '2026-08-31T15:24:14.582592'
 id: 98537416-0e6e-4a02-925f-974a17bfa10a
 status: draft
 type: sop
-updated: '2026-08-31T15:24:14.582592'
+updated: '2026-08-31T16:30:30.599226'
 version: 1.0.0
 ---
 
@@ -161,7 +161,7 @@ a diagnostic.
 
 **Manual fallback:** run the checks individually: `git status`;
 `git fetch && git merge-base --is-ancestor origin/main origin/dev`;
-`gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and
+`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == "dev")] | .[0]'` (this `gh` version has no `--branch` flag); `git tag -l vX.Y.Z` and
 `git ls-remote --tags origin vX.Y.Z`; `uv lock --check`;
 `gh auth status`.
 

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 180.0s)

_Thinking:_

The git diff shows the changes compared to the COMMITTED version:

1. `updated` timestamp (from the specmgr-test_update call)
2. Manual fallback line in Step 2 — and the committed version has the correct `git ls-remote`/`uv lock --check` lines!

In other words, the file on disk now contains the correct manual fallback block (my edit worked, and the corruption from the update call was... wait). Let me reconstruct:

- Committed file (79b3951): original content, line = `` `gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and `` (followed by `git ls-remote --tags origin vX.Y.Z`; `uv lock --check`;)
- specmgr-test_update replaced BODY line 156 — the update tool re-rendered the document (parse → render → write). The post-render text showed corruption: the `--branch` line was left as-is, and the line that got replaced was the `git ls-remote...` line (body line 156 = file line 164 in the post-render file) — no wait, in the update response, the Step 2 text showed both the `--branch` line and the new line, with `git ls-remote` and `uv lock --check` missing. So after the update, the file had the corruption.
- My edit replaced the corrupted block (which matched oldString exactly) with the correct block.
- Now: git diff against the committed version shows only the timestamp + 1 line changed (the gh run list line). The `git ls-remote`/`uv lock --check` lines are identical to the committed version (they were preserved — the corrupted update dropped them, and my edit restored them).

So the current file content = committed version + timestamp + fixed gh line. And the committed version was parseable (parse_sop succeeded at 15:30 — wait, was that really the case? The successful parse_sop I ran was against the committed file (pre-update). Yes.)

But now, parse is failing?! With an "expected heading_open, got paragraph_open" error at the top. The diff only shows those 2 changes... how can a change in the middle of the file break the parsing of the first token?

Ah, wait. Now I get it. Look at the new line:

`gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion --jq '[.[] | select(.headBranch == "dev")] | .[0]'` (this `gh` version has no `--branch` flag); `git tag -l vX.Y.Z` and

The jq expression inside the backticks contains `== "dev"` — double quotes inside backticks, no problem for markdown...

Hmm, but the error is about the first token of the entire body. Let me think about `format_text(post.content)`: parse with markdown-it and re-serialize (normalize). An unclosed code span could in principle swallow a heading...

Backtick count in the new line: let me count carefully:

1. `` `gh run list ... .[0]'` `` — 2 backticks (open+close)
2. `` `gh` `` — 2
3. `` `--branch` `` — 2
4. `` `git tag -l vX.Y.Z` `` — 2
   Total: 8 → balanced.

The whole document — did my edit change the parity of the backtick count anywhere? The old (corrupted) line had the same backticks. Compared to the committed version: the old line `` `gh run list --branch dev --limit 1`; `git tag -l vX.Y.Z` and `` → 4 backticks; the new line → 8 backticks. Even either way.

So the backtick parity is fine. Then why does the first token become paragraph_open?

Hmm, wait — let me re-read the error:

```
File ".../sop/models/v1/parser.py", line 78, in parse_sop
    body = Sop.from_text(format_text(post.content))
File ".../models/md/markdown_section.py", line 193, in from_text
    assert t_open.type == expected_type
AssertionError: Token[0]: expected 'heading_open', got 'paragraph_open'.
```

`Sop.from_text` — the body of Sop starts with... the H1? No — the H1 is stripped by the Post (frontmatter parsing: `post.content` = body after the frontmatter; then who strips the H1? Probably `format_text` or `Sop.from_text` expects the text to start with the first H2 (`## Purpose`)... and `MarkdownSection1.from_text` handles the H1.

The actual structure is: `Sop(MarkdownSection1)` — from_text probably expects Token[0] = heading_open (the H1 `# Perform...`). What we got was paragraph_open — meaning after format_text, the H1 line was parsed as a paragraph.

When does markdown-it parse `# Perform a release of biz.dfch.SpecMgr` as a paragraph? If the ATX heading rule doesn't apply... it always applies to `# text` at the start of a line. Unless the text is inside a fenced block or code span, or... unless the H1 line is no longer at the top — e.g., if format_text moved something above it.

Wait — maybe `post.content` includes the H1 and... hmm, let me test the committed version: `git stash` my changes? No — more simply: run parse on a `git show` copy of the committed file and see if it parses. Then run parse on the current file. That will isolate whether my changes broke it or something else (e.g., is it an environment issue with this python execution? The MCP parse at 15:30 succeeded with the same code...).

No, wait — the MCP specmgr-test server is running with the version installed in its own uv environment... the `uv run --frozen --all-extras python` I executed just rebuilt the package ("Building biz-dfch-specmgr... Built... Uninstalled 1 package... Installed 1 package"). Same source. Should be identical.

Let me test both files.

The diff is minimal (timestamp + one line) — yet parse fails at token 0. Isolating: parse the committed version vs. the current one:

**Tool: bash**

**Input:**

```json
{
  "command": "git show HEAD:docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md > /tmp/opencode/sop_committed.md && cp docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md /tmp/opencode/sop_current.md && sed -i 's|docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md|/tmp/opencode/sop_committed.md|' /tmp/opencode/verify_sop.py && uv run --frozen --all-extras python /tmp/opencode/verify_sop.py; echo \"committed rc=$?\""
}
```

**Output:**

```
Traceback (most recent call last):
  File "/tmp/opencode/verify_sop.py", line 5, in <module>
    doc = parse_sop(Path("/tmp/opencode/sop_committed.md"))
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/models/v1/parser.py", line 78, in parse_sop
    body = Sop.from_text(format_text(post.content))
  File "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_section.py", line 193, in from_text
    assert t_open.type == expected_type, f"Token[0]: expected '{expected_type}', got '{t_open.type}'."
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Token[0]: expected 'heading_open', got 'paragraph_open'.
committed rc=1

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 87.1s)

_Thinking:_

The COMMITTED version also fails to parse in this python run! In other words, my edit is not the cause. The file was parseable at 15:30 via the MCP server, and `create_sop` validated it at creation time. So something is different about this local `uv run` parse.

The difference: `parse_sop(post.content)` — `format_text(post.content)`. Hmm, wait — maybe the parse depends on... Let me look at parser.py:78 to understand `post` — maybe it's splitting the frontmatter and the H1. Let me read the parser.

Even the committed file fails locally — so it's not my edit; the local `parse_sop` run differs from the MCP one. Reading the parser:

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/models/v1/parser.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/sop/models/v1/parser.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Parse raw Standard Operating Procedure (SOP) ``.md`` text into a :class:`SopDocument`.
19: 
20: Fills the ``from_text``/parser entry-point gap ``document.py``'s own docstring
21: flags: ``SopDocument`` deliberately holds no such method itself, and the generic
22: ``models/md`` engine only ever parses a *body* (``Sop.from_text``), never the
23: combination of frontmatter + body a full on-disk file is. This module is the
24: thin free-function glue between the two, mirroring
25: ``dec/models/v1/parser.parse_dec``/``gol/models/v1/parser.parse_gol``'s own
26: layout -- a free function, not a classmethod on the document model.
27: 
28: Parsing requires the ``frontmatter`` extra (``python-frontmatter``) to split
29: YAML frontmatter from markdown body text before delegating to the generic
30: MarkdownStr engine. Two error channels:
31: 
32: - ``AssertionError`` for structural problems (unrecognized headings, missing
33:   mandatory sections), propagating naturally from ``process_field``/``from_text``.
34: - ``pydantic.ValidationError`` for value/validation failures on field values or
35:   cross-field invariants (e.g. a duplicate ``### Step`` number) --
36:   deliberately left uncaught here, same as all other parsers in the project.
37: 
38: Like ``dec.models.v1.parser.parse_dec``/``gol.models.v1.parser.parse_gol``,
39: there is no dedicated structural-error exception type (no ``SopParseError``
40: equivalent); both error channels are plain ``AssertionError`` /
41: ``pydantic.ValidationError`` that propagate uncaught.
42: """
43: 
44: from __future__ import annotations
45: 
46: import frontmatter  # requires the ``frontmatter`` extra from pyproject.toml
47: 
48: from biz.dfch.specmgr.models.md._markdown import format_text
49: 
50: from .body import Sop
51: from .document import SopDocument
52: from .frontmatter import SopFrontmatter
53: 
54: __all__ = ["parse_sop"]
55: 
56: 
57: def parse_sop(text: str) -> SopDocument:
58:     """Parse a full Standard Operating Procedure ``.md`` file's text into a :class:`SopDocument`.
59: 
60:     Parameters
61:     ----------
62:     text:
63:         The complete file content, YAML frontmatter block and markdown body
64:         together, exactly as read from disk (or submitted verbatim by an MCP
65:         tool call that never wrote it to disk at all).
66: 
67:     Returns
68:     -------
69:     SopDocument
70:         The structured document. Raises ``AssertionError`` for a malformed
71:         heading/list structure, or ``pydantic.ValidationError`` for a
72:         structurally-sound document whose field values (or cross-field
73:         invariants) fail schema validation -- see this module's docstring
74:         for the full split.
75:     """
76:     post = frontmatter.loads(text)  # type: ignore[union-attr]
77:     fm = SopFrontmatter.model_validate(_stringify_metadata(post.metadata))
78:     body = Sop.from_text(format_text(post.content))
79:     return SopDocument(frontmatter=fm, body=body)
80: 
81: 
82: def _stringify_metadata(metadata: dict[str, object]) -> dict[str, object]:
83:     """Coerce YAML-native scalar types back to ``str`` (or ``None``).
84: 
85:     ``python-frontmatter`` parses the YAML block using PyYAML's standard loader,
86:     which auto-converts unquoted dates/timestamps into Python datetime objects,
87:     but every :class:`SopFrontmatter` field inherited from
88:     :class:`~biz.dfch.specmgr.models.md.MarkdownFrontmatter` is ``str | None``,
89:     so a raw non-``str`` object would fail Pydantic's (deliberately non-coercive)
90:     string validation. Converting via ``str()`` reproduces what a human would have
91:     written.  ``None`` (from an empty YAML key like ``version:``) is passed
92:     through so the field's own optional-ness applies normally.
93: 
94:     Mirrors the same helper in ``dec/models/v1/parser._stringify_metadata``/
95:     ``gol/models/v1/parser._stringify_metadata``.
96:     """
97:     return {key: value if value is None or isinstance(value, str) else str(value) for key, value in metadata.items()}

(End of file - total 97 lines)
</content>
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 114.5s)

_Thinking:_

The signature of `parse_sop` is: **`parse_sop(text: str)`** — it takes the file's *text*, not a path! My validation script called `parse_sop(Path(...))` — I passed a Path object. Then `frontmatter.loads(Path)` — does python-frontmatter's `loads` expect a str? If you pass a Path, it probably... `frontmatter.loads` calls `Post(text)`... hmm, what happens if you pass a Path? `post.content` — if it doesn't error out, it's treating the Path as... Actually, in the traceback, `frontmatter.loads(text)` is succeeding (the error is happening at `format_text(post.content)`), so it accepted the Path. `post.content` from a Path — python-frontmatter's `Post.__init__(text)` runs `self.content = text.split("---")`?? If text is a Path (not a str), `str.split` shouldn't exist... unless it's being coerced via f-string or str(). If content is becoming something like the repr of str(Path) (e.g. `"PosixPath('/tmp/...')"`) — then the first token of markdown parsing would be a paragraph_open! That's exactly the error!

So, this isn't a file or a code bug — it's a bug in my test harness: I should have passed the text read from the file. The MCP tool `parse_sop(path)` reads the file and passes the text — that's why it worked.

Fix the validation script: `parse_sop(Path(...).read_text())`.

`parse_sop` takes the file's **text**, not a path — my harness passed a `Path` object (its repr parsed as a paragraph). That's a bug in the harness, not in the file. I'll fix the check:

**Tool: write**

**Input:**

```json
{
  "content": "from pathlib import Path\n\nfrom biz.dfch.specmgr.sop.models.v1 import parse_sop\n\ndoc = parse_sop(Path(\"/tmp/opencode/sop_current.md\").read_text())\ns2 = doc.body.procedure.steps[1].text\nassert s2.count(\"gh run list\") == 1, s2\nassert s2.count(\"git tag -l\") == 1, s2\nassert \"git ls-remote --tags origin\" in s2, s2\nassert \"uv lock --check\" in s2, s2\nassert \"--branch dev\" not in s2, s2\nprint(\"parse OK; step 2 manual fallback verified\")\n",
  "filePath": "/tmp/opencode/verify_sop.py"
}
```

**Output:**

```
Wrote file successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 84.8s)

_Thinking:_

Wait, `s2.count("gh run list")` — s2 is the full text of step 2 (automated + manual). The automated part has "the latest CI run on `dev` is green", but — no "gh run list" there. The manual part: one occurrence of "gh run list". OK, count==1.

But `"--branch dev" not in s2` — my new line contains "(this `gh` version has no `--branch` flag)" — it contains "--branch" but not "--branch dev". OK.

Execute.

**Tool: bash**

**Input:**

```json
{
  "command": "uv run --frozen --all-extras python /tmp/opencode/verify_sop.py"
}
```

**Output:**

```
parse OK; step 2 manual fallback verified

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 93.5s)

_Thinking:_

SOP file (including my fix) parses without issues. Next, commit the SOP fix (updated timestamp + corrected gh line in step 2) and push. After that, final status check:

1. Commit the SOP fix.
2. Check whether dev CI is green against the latest push.
3. Report the final state:
   - Phase 0: SOP created (draft), committed (79b3951), gh CLI fix committed
   - Phase 1: script (3c2b8e9)
   - Phase 2+3: command + README + AGENTS.md (6e614d3)
   - Phase 4: verification results
   - Phase 5: user restarts opencode → `/release --dry-run minor` smoke test → then the actual `/release minor` (v0.15.0) as the SOP acceptance test → after that, SOP → active.

Commit message: "docs(sop): fix gh run list command in SOP step 2 manual fallback".

SOP verified. Committing the fix:

**Tool: bash**

**Input:**

```json
{
  "command": "git add docs/sop/ && git commit -m \"docs(sop): use headBranch-filtered gh run list in step 2 manual fallback\" && git push"
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...........................................(no files to check)Skipped
vulture..............................................(no files to check)Skipped
unittest.............................................(no files to check)Skipped
specmgr coverage-badge...............................(no files to check)Skipped
specmgr docs.........................................(no files to check)Skipped
specmgr mcp-docs.....................................(no files to check)Skipped
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (sop package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped
[dev bb2fd21] docs(sop): use headBranch-filtered gh run list in step 2 manual fallback
 1 file changed, 2 insertions(+), 2 deletions(-)
To https://github.com/dfch/biz.dfch.SpecMgr.git
   6e614d3..bb2fd21  dev -> dev

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 87.1s)

_Thinking:_

All commits have been pushed. Final check: dev CI against bb2fd21 (in progress), and the final `status 0.15.0` probe to confirm that everything is ready for the release. After that, update the todos and report.

Final state check:

**Tool: bash**

**Input:**

```json
{
  "command": "scripts/release.sh status 0.15.0; gh run list --limit 3 --json headBranch,status,conclusion,headSha --jq '.[] | select(.headBranch == \"dev\") | [(.headSha[0:12]), .status, (.conclusion // \"-\")] | @tsv'"
}
```

**Output:**

```
release status for v0.15.0:
  [ ] bump          pyproject.toml carries 0.14.0
  [ ] changelog     no dated section yet
  [ ] commit-push   release commit not on origin/dev
  [ ] pr            no open PR; main behind dev
  [ ] tag           no tag
  [ ] publish       no publish run (no tag)
  [ ] release-notes no GitHub Release yet
bb2fd210544c	in_progress	
6e614d390420	completed	success

```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 139.5s)

_Thinking:_

Everything is in place. The latest dev CI (bb2fd21) is running. The release pipeline is in a state where v0.15.0 can be issued.

I'll update the TODO and give the final report. I'll keep it structured but concise.

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Verify specmgr-test MCP swap (version + sop resources)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 0: create release SOP via specmgr-test (draft), commit to dev",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 1: scripts/release.sh (staged, idempotent, --dry-run, status, all)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 2: .opencode/command/release.md orchestration protocol",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 3: README 'Make a Release' + AGENTS.md updates",
      "status": "completed",
      "priority": "medium"
    },
    {
      "content": "Phase 4: verification (bash -n, dry-runs, resolve/precheck/status, non-TTY misuse)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 5: restart opencode, /release --dry-run minor smoke test, then first real /release 0.15.0, then SOP draft → active",
      "status": "pending",
      "priority": "high"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Verify specmgr-test MCP swap (version + sop resources)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 0: create release SOP via specmgr-test (draft), commit to dev",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 1: scripts/release.sh (staged, idempotent, --dry-run, status, all)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 2: .opencode/command/release.md orchestration protocol",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 3: README 'Make a Release' + AGENTS.md updates",
    "status": "completed",
    "priority": "medium"
  },
  {
    "content": "Phase 4: verification (bash -n, dry-runs, resolve/precheck/status, non-TTY misuse)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 5: restart opencode, /release --dry-run minor smoke test, then first real /release 0.15.0, then SOP draft → active",
    "status": "pending",
    "priority": "high"
  }
]
```

______________________________________________________________________

## Assistant (Build · qwen3.8-27b-bf16-896k-mtp-1 · 187.0s)

_Thinking:_

Done. Final report — concisely:

- What was built (4 commits on dev)
- What was verified
- What the user should do next (restart opencode → /release --dry-run minor → the actual release)
- Interesting bugs discovered and fixed during verification

Phases 0–4 complete — four commits on `dev` (CI on the latest is in flight):

| Commit | What |
|---|---|
| `79b3951` | **SOP** `98537416` "Perform a release of biz.dfch.SpecMgr" (draft) in `docs/sop/` — 9 steps, each with Automated + Manual fallback, RASCI, safety invariants |
| `3c2b8e9` | **`scripts/release.sh`** — 12 stages (`resolve`…`release-notes`, plus `status`, `all`), idempotent, `--dry-run`, 30s polls, per-stage tree assertions, ff-only merge |
| `6e614d3` | **`/release` OpenCode command** + README "Make a Release" rewritten around the SOP + AGENTS.md line |
| `bb2fd21` | SOP fix: step 2's manual fallback uses a `headBranch`-filtered `gh run list` (this `gh` has no `--branch` flag) |

**Verified:** syntax, `resolve` (0.15.0, double-bump refusal, non-TTY usage errors), `precheck` (all green today), `status` (all stages pending), real `bump` (uv.lock diff = version line only) and real `changelog` transform (with throwaway entries, restored), all six later-stage guard rails, and full SOP round-trip through the live MCP parser. Testing also caught three real bugs (untracked-file strictness, `git rev-parse` without `--verify` echoing unknown refs, jq `@tsv` on non-arrays) — all fixed.

**Your moves (Phase 5):**

1. **Restart opencode** — the new `/release` command loads at startup
2. Smoke test: `/release --dry-run minor`
3. When ready, the real thing: `/release minor` → v0.15.0, the first release carrying the SOP domain itself. Note the `[Unreleased]` section is currently **empty** — the agent's curation step (SOP step 3) will draft it from the commits since v0.14.0 (SOP domain, release automation, feat-7 tasks) and show it to you before anything mutates
4. On success: I flip the SOP `draft → active`

______________________________________________________________________
