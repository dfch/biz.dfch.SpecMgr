---
description: Run the release SOP — version bump, changelog, dev→main PR, tag, and publish — by driving scripts/release.sh stages.
---

Execute the release SOP (`docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md`) by driving the `scripts/release.sh` stages from the repo root. The script is the single source of truth for release mechanics; the SOP is the single source of truth for the procedure. My input: $ARGUMENTS

Follow these steps in order:

1. **Parse my input.** It is either a version spec (`X.Y.Z` or `patch`/`minor`/`major`), optionally combined with `--dry-run`, or nothing. If no version spec was given, ask me with the question tool — offer the current version from `pyproject.toml` plus the suggested next minor and patch. Never guess a version.
2. **Resolve.** Run `bash scripts/release.sh resolve <spec>` (or `resolve --dry-run`-equivalent: `resolve` never mutates). Confirm the resolved version with me before continuing — a surprising number (e.g. `major` on a `0.x` version) needs my explicit acknowledgement.
3. **Pre-check.** Run `bash scripts/release.sh precheck <version>`. It ends with two sub-items beyond the six standing checks (SOP step 2 (a)–(f)): the **feat closeout gate** — every feat folder shipped in the current release window (since the last tag) must be `status: done`, and a violation names each offending feat — and the **previous-release branch cleanup** — stale local/`origin` `feat-*`/`fix/*` branches from the previous release or older, deleted with the merged-PR proof and the four guards (`--dry-run` makes it report-only: the would-delete/would-keep table, no ref is deleted). On a gate failure, perform the remediation the gate prints: close out each named feat to `status: done` on `dev` (edit the feat README's frontmatter plus a finalization entry recording the PR merge), commit, and re-run `precheck` — the cleanup runs only after the gate passes, so a gate failure mutates no branch. Any other failure: report it verbatim and stop.
4. **Curate the changelog** (SOP step 3 — this is your only direct file edit, never done by the script): read the `[Unreleased]` section of `CHANGELOG.md` and `git log $(git describe --tags --abbrev=0)..HEAD --oneline`, add missing user-visible items, rewrite verbose or internal entries into Keep a Changelog categories (`Added`/`Changed`/`Deprecated`/`Removed`/`Fixed`/`Security`), then show me the finished section and wait for my OK before continuing. If `[Unreleased]` is empty, stop and ask me what should be documented for this release.
5. **Run the mutating stages in order**, each as its own bash call with a generous timeout (these wait on CI: use at least 45 minutes / 2700000 ms):
   - `bash scripts/release.sh bump <version>`
   - `bash scripts/release.sh changelog <version>`
   - `bash scripts/release.sh commit-push <version>`
   - `bash scripts/release.sh pr-create <version>`
6. **Merge gate.** After `pr-create` succeeds, show me the PR URL and the new changelog section, and ask for my explicit go-ahead. Only once I approve, run `bash scripts/release.sh pr-merge <version>`.
7. **Finish the release** (generous timeouts again, `publish-wait` can take up to 45 minutes):
   - `bash scripts/release.sh tag-push <version>`
   - `bash scripts/release.sh publish-wait <version>`
   - `bash scripts/release.sh release-notes <version>`

**Dry-run mode** (when I gave `--dry-run`): run only `resolve`, `precheck`, `bump --dry-run`, and `changelog --dry-run` (plus the changelog curation in step 4 if useful), then stop and show me what the remaining stages would do. Never commit, push, open a PR, tag, or publish.

**On any non-zero exit:** stop immediately. Run `bash scripts/release.sh status <version>` to locate the failed stage, fetch the relevant CI log if a run failed (`gh run view <id> --log-failed`), and report the diagnosis with the run/PR URLs verbatim. Wait for my direction. Never auto-retry, never skip a failed stage, never perform release steps outside the script, and never merge a red PR.

**On success:** summarize in a few lines — version, PR, tag, and the release URLs from the script's final output.
