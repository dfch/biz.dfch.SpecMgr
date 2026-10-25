#!/usr/bin/env bash
# Staged release automation for biz.dfch.SpecMgr.
#
# Deterministic projection of the normative SOP "Perform a release of
# biz.dfch.SpecMgr" (SOP 98537416-0e6e-4a02-925f-974a17bfa10a,
# docs/sop/sop-98537416-0e6e-4a02-925f-974a17bfa10a-perform-a-release-of-biz-dfch-specmgr.md).
# Where this script and the SOP disagree, the SOP wins: fix the script.
#
# Usage: scripts/release.sh <stage> [X.Y.Z | patch | minor | major] [--dry-run]
#
# Stages (mirror the SOP's 9 procedure steps; every stage is idempotent):
#   resolve       compute and print the target version (no mutation)
#   precheck      fail-fast pre-release checks (SOP step 2), ending with
#                 the feat closeout gate (every feat shipped in the
#                 current release window must be closed out to status:
#                 done) and the previous-release branch cleanup (stale
#                 local/origin feat-*/fix/* branches, each deletion
#                 proven by a merged PR)
#   bump          pyproject.toml + uv.lock version bump (SOP step 4)
#   changelog     move [Unreleased] into a dated section (SOP step 5a)
#   commit-push   commit the 3 release files, push dev, wait for CI (SOP step 5b)
#   pr-create     open the dev->main release PR, wait for checks (SOP step 6a)
#   pr-merge      wait for green checks, then ff-only merge locally (git
#                 merge --ff-only of origin/dev on main + push of main,
#                 closing the PR afterwards; the plain `gh pr merge
#                 --merge` cannot be relied on to fast-forward)
#                 (SOP step 6b, after the merge gate)
#   tag-push      tag vX.Y.Z on main, push the tag, back to dev (SOP step 7)
#   publish-wait  wait for the 4 publish.yml jobs (SOP step 8)
#   release-notes verify the release + set the GitHub Release notes (the
#                 name stays the bare version set in SOP step 8) (SOP step 9)
#   status        read-only: where does this release stand?
#   all           resolve + precheck + bump + changelog + commit-push +
#                 pr-create + [TTY merge gate] + pr-merge + tag-push +
#                 publish-wait + release-notes (no agent curation: the
#                 [Unreleased] section must already be curated)
#
# --dry-run makes the mutating stages report-only; for `precheck` the
# previous-release branch cleanup then prints its would-delete/would-keep
# table without deleting any ref.
#
# Only `resolve` and `all` accept bump keywords; all other stages take the
# full resolved version.
#
# Written against the old `gh` (2.4.0) this environment ships: no
# `gh run list --commit`, no `gh run view --json jobs`, no `gh release
# edit`, no `--ff`-style merge flag. The publication run is located by
# workflow NAME ("Publish to PyPI") plus the tag's commit SHA (filtered
# with `jq`); the release notes are set via `gh api`; ff-only merging is
# enforced by pre- and post-merge SHA assertions around a LOCAL
# `git merge --ff-only` + push of main — the plain `gh pr merge --merge`
# method has been observed to create a merge commit although the
# invariant held (v0.16.0 release) and cannot be relied on to
# fast-forward. The SOP's "Safety and Precautions" documents the same
# constraints.

set -euo pipefail

SOP_ID="98537416-0e6e-4a02-925f-974a17bfa10a"
REPO_ROOT="biz-dfch-specmgr"
# Workflow NAME (the `name:` key) of .github/workflows/publish.yml —
# `gh run list --workflow` filters by name, not by file name.
PUBLISH_WORKFLOW="Publish to PyPI"
# Workflow NAME (the `name:` key) of .github/workflows/ci.yml — the dev
# CI gate must match this workflow only: `latest_dev_run_tsv` used to
# accept the newest run of ANY workflow on dev, and a dependabot
# "Graph Update" run (47 s, green, same head SHA) once satisfied the
# commit-push gate while the real "Lint and Test" run was still in
# flight (v0.35.0 release, SOP Updates 2026-10-06).
CI_WORKFLOW="Lint and Test"
POLL_INTERVAL=30
# close_pr_if_open's bounded PR-state read retry (issue #213): the attempt
# budget, and the seconds slept between attempts (never after the last one).
PR_STATE_RETRY_ATTEMPTS=5
PR_STATE_RETRY_INTERVAL=3
# close_pr_if_open's failed-close re-verify read budget (issue #213
# hardening): the re-verify reads are separated by PR_STATE_RETRY_INTERVAL
# seconds (never after the last one).
PR_STATE_REVERIFY_ATTEMPTS=3
DEV_CI_TIMEOUT_MIN=40
PUBLISH_TIMEOUT_MIN=45

DRY_RUN=0
VERSION_ARG=""

info() { printf 'release: %s\n' "$*"; }
die() { printf 'release: ERROR: %s\n' "$*" >&2; exit 1; }
is_tty() { [ -t 0 ]; }

usage() {
  sed -n '2,43p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
}

# --- generic helpers ---------------------------------------------------------

require_repo_root() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git work tree"
  [ "$(git rev-parse --show-toplevel)" = "$(pwd)" ] || die "run from the repo root (cwd: $(pwd))"
}

require_tools() {
  command -v git >/dev/null || die "git not found"
  command -v uv >/dev/null || die "uv not found"
  command -v gh >/dev/null || die "gh not found"
  command -v jq >/dev/null || die "jq not found"
  gh auth status >/dev/null 2>&1 || die "gh is not authenticated (gh auth status)"
}

current_version() {
  local line
  line=$(grep -m1 '^version = "' pyproject.toml) || die "no version line in pyproject.toml"
  printf '%s' "${line#version = \"}" | sed 's/"$//'
}

validate_full_version() {
  [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "'$1' is not a full semantic version (X.Y.Z)"
}

# $1 = current version, $2 = keyword -> prints bumped version
bump_semver() {
  local a b c
  a=$(cut -d. -f1 <<<"$1"); b=$(cut -d. -f2 <<<"$1"); c=$(cut -d. -f3 <<<"$1")
  case "$2" in
    patch) echo "$a.$b.$((c + 1))" ;;
    minor) echo "$a.$((b + 1)).0" ;;
    major) echo "$((a + 1)).0.0" ;;
    *) die "unknown bump keyword: $2" ;;
  esac
}

# Resolve $1 (full version or keyword) against the current pyproject version.
resolve_target() {
  local current arg
  current=$(current_version)
  arg="${1:-}"
  if [ -z "$arg" ]; then
    if is_tty; then
      info "current version: $current"
      local v
      read -r -p "Target version (X.Y.Z or patch/minor/major) [suggested: $(bump_semver "$current" minor)]: " v
      arg="$v"
    else
      die "version required in non-interactive mode: $0 <stage> <X.Y.Z|patch|minor|major>"
    fi
  fi
  local target
  if [[ "$arg" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    target="$arg"
  elif [[ "$arg" == patch || "$arg" == minor || "$arg" == major ]]; then
    target=$(bump_semver "$current" "$arg")
  else
    die "version must be a full X.Y.Z or one of patch/minor/major, got: $arg"
  fi
  [ "$target" != "$current" ] || die "pyproject.toml already carries $target (no re-bump; use status <v> to see where the release stands)"
  printf '%s' "$target"
}

# Extract the dated changelog section body for $1 (heading line excluded,
# leading blanks trimmed).
extract_changelog_section() {
  awk -v v="$1" '
    index($0, "## [" v "] - ") == 1 { found = 1; next }
    found && /^## / { exit }
    found && $0 ~ /^[[:space:]]*$/ && !started { next }
    found { started = 1; print }
  ' CHANGELOG.md
}

# Print the content of the current [Unreleased] section (heading excluded).
unreleased_content() {
  awk '
    $0 == "## [Unreleased]" { found = 1; next }
    found && /^## / { exit }
    found { print }
  ' CHANGELOG.md
}

unreleased_is_empty() {
  ! grep -q '[^[:space:]]' <<<"$(unreleased_content)"
}

# Poll a workflow run every POLL_INTERVAL seconds until it completes.
# $1 = run id, $2 = label, $3 = timeout in minutes.
wait_for_run() {
  local run_id="$1" label="$2" timeout_min="${3:-$DEV_CI_TIMEOUT_MIN}"
  local run_url line status conclusion polls max_polls
  run_url=$(gh run view "$run_id" --json url --jq .url) || die "cannot query run $run_id"
  info "waiting for $label: $run_url (poll every ${POLL_INTERVAL}s, timeout ${timeout_min}m)"
  max_polls=$((timeout_min * 60 / POLL_INTERVAL))
  polls=0
  while :; do
    line=$(gh run view "$run_id" --json status,conclusion --jq '[.status, (.conclusion // "")] | @tsv') || die "cannot query run $run_id"
    status="${line%%$'\t'*}"
    conclusion="${line#*$'\t'}"
    if [ "$status" = "completed" ]; then
      if [ "$conclusion" = "success" ]; then
        info "$label: success"
        return 0
      fi
      die "$label failed (conclusion: $conclusion): $run_url"
    fi
    polls=$((polls + 1))
    if [ "$polls" -ge "$max_polls" ]; then
      die "timed out waiting for $label: $run_url"
    fi
    sleep "$POLL_INTERVAL"
  done
}

# Print "databaseId headSha status conclusion" (tab-separated) for the newest
# dev-branch "Lint and Test" push run, or nothing if none exists. (This gh
# version has no 'gh run list --branch' flag, hence the headBranch filter.)
# The workflow-NAME and -event filters are mandatory: unfiltered, the newest
# run of any workflow on dev qualifies (a dependabot "Graph Update" run once
# satisfied this gate — v0.35.0 release), and pull_request runs are excluded
# because they also carry headBranch "dev".
latest_dev_run_tsv() {
  # The filtering runs in standalone jq (with `--arg`), the same pattern
  # the publish-run lookups below use — `gh --jq` in this build takes only
  # the program and its `$ENV` does not see the process environment.
  local runs
  runs=$(gh run list --limit 30 --json databaseId,headSha,headBranch,event,name,status,conclusion 2>/dev/null || true)
  [ -n "$runs" ] || return 0
  jq -r --arg wf "$CI_WORKFLOW" \
    '[.[] | select(.headBranch == "dev" and .name == $wf and .event == "push")]
       | .[0] // empty
       | [.databaseId, .headSha, .status, (.conclusion // "")] | @tsv' <<<"$runs" 2>/dev/null || true
}

# Wait until a dev run exists for the current origin/dev head, then for it to pass.
wait_for_dev_ci() {
  local head_sha line rid sha status polls
  head_sha=$(git rev-parse origin/dev)
  info "waiting for a CI run to appear on dev head ${head_sha:0:12} ..."
  polls=0
  while :; do
    line=$(latest_dev_run_tsv)
    if [ -n "$line" ]; then
      IFS=$'\t' read -r rid sha status _ <<<"$line"
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

# Poll a PR's checks every POLL_INTERVAL seconds. $1 = PR number.
# This gh build (2.4.0+dfsg1) returns `gh pr checks` rc=1 for PENDING
# checks as well as failing ones — rc=0 only when every registered check
# passes (verified live in the v0.35.0 release, when the old
# rc=1-is-fatal handling below fail-fasted although every listed check
# was pass or pending). The pending/failing distinction therefore comes
# from parsing the output, not the exit code: a line whose state column
# is a terminal failure state dies the stage; anything else (pending,
# queued, no checks registered yet, error text) keeps polling within the
# timeout.
wait_for_pr_checks() {
  local pr="$1" out rc polls fatal
  polls=0
  while :; do
    out=$(gh pr checks "$pr" 2>&1) && rc=0 || rc=$?
    if [ "$rc" -eq 0 ]; then
      info "PR #$pr checks: all green"
      return 0
    fi
    fatal=$(printf '%s\n' "$out" | awk -F'\t' '$2 == "fail" || $2 == "failure" || $2 == "error" || $2 == "cancelled" || $2 == "canceled" { print }')
    if [ -n "$fatal" ]; then
      printf '%s\n' "$out" >&2
      die "PR #$pr checks are failing (see above); fix on dev and resume from the failed stage"
    fi
    polls=$((polls + 1))
    if [ "$polls" -ge 40 ]; then
      die "timed out waiting for PR #$pr checks"
    fi
    info "PR #$pr checks: pending (poll ${polls}/40)"
    sleep "$POLL_INTERVAL"
  done
}

# Close the PR if GitHub has not already done it: the local ff-only push
# of main can make GitHub mark the PR MERGED itself, and `gh pr close`
# then fails with a GraphQL "Could not close the pull request" error —
# observed live in the v0.35.0 release, exiting the stage non-zero after
# everything substantive had succeeded. The state comes from the REST API
# (`gh pr view`'s default GraphQL field set breaks on today's GitHub in
# this gh build — the Projects-classic deprecation error), matching the
# script's other `gh api` call sites.
#
# That same already-merged symptom recurred live in the v0.36.0 release
# (issue #213): the single state read can land in the window before
# GitHub's async merge detection flips the PR to MERGED and come back
# empty/stale. The read is therefore a layered defense: (1) it is retried
# a bounded number of times (PR_STATE_RETRY_ATTEMPTS, sleeping
# PR_STATE_RETRY_INTERVAL seconds between attempts — never after the
# last), returning early with the success message once the state reads
# merged/closed; (2) when the budget is exhausted the close is attempted
# exactly as before, since a genuinely open PR must still be closed; (3)
# a failed close re-verifies the state with a bounded budget of reads
# (PR_STATE_REVERIFY_ATTEMPTS, sleeping PR_STATE_RETRY_INTERVAL seconds
# between them — never after the last, each read info-logged), treating
# the failure as the known race (info note, success) as soon as a read is
# merged/closed and dying with an actionable message when the budget is
# exhausted. The re-verify keys on the state (ground truth), not on `gh`'s
# close error text — a message-gated `|| true` was rejected as brittle
# across gh versions. Before any read or sleep runs, the three retry
# variables are guard-checked: an empty or non-numeric value dies with an
# actionable message naming the variable and the bad value, instead of an
# opaque arithmetic/sleep error under `set -euo pipefail`.
# $1 = PR number.
close_pr_if_open() {
  local pr_num="$1" pr_state="" attempt=0
  [[ "$PR_STATE_RETRY_ATTEMPTS" =~ ^[1-9][0-9]*$ ]] || die "PR_STATE_RETRY_ATTEMPTS must be a positive integer (got: '${PR_STATE_RETRY_ATTEMPTS}')"
  [[ "$PR_STATE_RETRY_INTERVAL" =~ ^[0-9]+$ ]] || die "PR_STATE_RETRY_INTERVAL must be a non-negative integer (got: '${PR_STATE_RETRY_INTERVAL}')"
  [[ "$PR_STATE_REVERIFY_ATTEMPTS" =~ ^[1-9][0-9]*$ ]] || die "PR_STATE_REVERIFY_ATTEMPTS must be a positive integer (got: '${PR_STATE_REVERIFY_ATTEMPTS}')"
  while [ "$attempt" -lt "$PR_STATE_RETRY_ATTEMPTS" ]; do
    attempt=$((attempt + 1))
    pr_state=$(gh api repos/{owner}/{repo}/pulls/"$pr_num" --jq .state 2>/dev/null || true)
    case "$pr_state" in
      merged | closed)
        info "PR #$pr_num already $pr_state — nothing to close"
        return 0
        ;;
    esac
    info "PR #$pr_num state read: '${pr_state:-<empty>}' (attempt ${attempt}/${PR_STATE_RETRY_ATTEMPTS})"
    if [ "$attempt" -lt "$PR_STATE_RETRY_ATTEMPTS" ]; then
      sleep "$PR_STATE_RETRY_INTERVAL"
    fi
  done
  if ! gh pr close "$pr_num"; then
    local reverify=0
    while [ "$reverify" -lt "$PR_STATE_REVERIFY_ATTEMPTS" ]; do
      reverify=$((reverify + 1))
      pr_state=$(gh api repos/{owner}/{repo}/pulls/"$pr_num" --jq .state 2>/dev/null || true)
      case "$pr_state" in
        merged | closed)
          info "PR #$pr_num: gh pr close failed but the state re-read is $pr_state (re-verify attempt ${reverify}/${PR_STATE_REVERIFY_ATTEMPTS}) — GitHub's async merge detection marked the PR merged after the push; the close failure is the known race (issue #213), nothing to do"
          return 0
          ;;
      esac
      info "PR #$pr_num state re-read: '${pr_state:-<empty>}' (re-verify attempt ${reverify}/${PR_STATE_REVERIFY_ATTEMPTS})"
      if [ "$reverify" -lt "$PR_STATE_REVERIFY_ATTEMPTS" ]; then
        sleep "$PR_STATE_RETRY_INTERVAL"
      fi
    done
    die "PR #$pr_num could not be closed and the state re-read is '${pr_state:-<empty>}' (not merged/closed) — close the PR manually or investigate, then resume from the failed stage"
  fi
  return 0
}

# Tracked files differing from HEAD (staged or unstaged); untracked paths are
# deliberately excluded — the release commit stages exactly three explicit
# paths, so untracked files cannot enter it.
dirty_files() {
  git diff --name-only HEAD
}

# Assert the dirty set is a subset of the given file list ($2..$n).
assert_dirty_subset() {
  local f
  for f in $(dirty_files); do
    local ok=0 a
    for a in "$@"; do
      if [ "$f" = "$a" ]; then ok=1; break; fi
    done
    [ "$ok" -eq 1 ] || die "unexpected working-tree change: $f (allowed: $*)"
  done
}

confirm_or_die() {
  # $1 = question; TTY: prompt (default no); non-TTY: die.
  local q="$1" a
  if is_tty; then
    read -r -p "$q [y/N]: " a
    [ "$a" = "y" ] || [ "$a" = "Y" ] || die "aborted at confirmation"
  else
    die "$q (interactive confirmation required; re-run from a TTY)"
  fi
}

# --- feat closeout gate helpers (feat-233, SOP step 2 sub-item) --------------

# Sentinel returned by feat_status for a frontmatter `status:` value that is
# missing, empty, or outside the closed set planning/progress/review/done.
# The gate turns the sentinel into its own violation line (the fail-safe:
# block the release, never skip the folder).
FEAT_STATUS_UNPARSEABLE="__unparseable__"

# Per-run cache path of closed_pr_scan's one-shot page fetch. PID-keyed so
# that every call — which necessarily runs in a pipeline/command
# substitution subshell (whose variable assignments never propagate back
# to the parent shell) — re-derives the SAME file path ($$ is inherited by
# subshells) and finds the already-fetched cache on disk. The precheck
# stage removes a stale file at run start and traps the removal on EXIT.
closed_pr_scan_cache_path() {
  printf '%s/release-closed-pr-scan-%s' "${TMPDIR:-/tmp}" "$$"
}

# Print the latest release tag reachable from HEAD
# (`git describe --tags --abbrev=0`), or nothing when no tag is reachable
# (the first release). Pure stdout contract: the caller captures the tag
# via command substitution and must emit its own info note when the
# result is empty (the release window is then HEAD — the gate counts every
# merged delivery as in-window; the cleanup has no "previous release or
# older" to delete). An info() call INSIDE this function would be
# captured by the substitution and pollute the tag value.
latest_tag() {
  local tag
  tag=$(git describe --tags --abbrev=0 2>/dev/null || true)
  printf '%s' "$tag"
}

# Print the ids of every `.specmgr/feat/feat-*/` folder (one per line,
# sorted), or nothing when the directory is absent.
feat_folders() {
  local d
  [ -d .specmgr/feat ] || return 0
  for d in .specmgr/feat/feat-*/; do
    [ -d "$d" ] || continue
    d="${d%/}"
    printf '%s\n' "${d##*/}"
  done | sort
}

# Print the frontmatter `status:` value of `.specmgr/feat/<id>/README.md`
# (the first frontmatter block only). Prints FEAT_STATUS_UNPARSEABLE when
# the README is missing, the `status:` line is absent or empty, or the
# value is outside the closed set planning/progress/review/done. Before
# the closed-set check the value is normalized the way YAML would read
# it: a trailing comment (YAML requires whitespace before the `#`) is
# stripped, and ONE pair of surrounding matching single or double quotes
# is removed — `status: 'review'` and `status: planning # note` are the
# same values as the bare forms, not defects.
feat_status() {
  local id="$1" file value
  file=".specmgr/feat/$id/README.md"
  [ -f "$file" ] || { printf '%s' "$FEAT_STATUS_UNPARSEABLE"; return 0; }
  value=$(
    awk -v sq="'" '
      NR == 1 && $0 != "---" { exit }
      NR == 1 { next }
      /^---/ { exit }
      /^status:[ \t]*/ {
        sub(/^status:[ \t]*/, "")
        sub(/[ \t]+$/, "")
        sub(/[ \t]#.*$/, "")
        sub(/[ \t]+$/, "")
        if (length($0) >= 2 && substr($0, 1, 1) == sq && substr($0, length($0), 1) == sq) {
          $0 = substr($0, 2, length($0) - 2)
        } else if (length($0) >= 2 && substr($0, 1, 1) == "\"" && substr($0, length($0), 1) == "\"") {
          $0 = substr($0, 2, length($0) - 2)
        }
        print
        exit
      }
    ' "$file"
  )
  case "$value" in
    planning | progress | review | done) printf '%s' "$value" ;;
    *) printf '%s' "$FEAT_STATUS_UNPARSEABLE" ;;
  esac
}

# Print the newest merged PR whose head ref is exactly $1 (a same-repo
# branch name), one line: number<TAB>merged_at<TAB>merge_commit_sha — or
# nothing when the ref has no merged PR (REQ-002: such a feat is never
# gated). The `head` filter uses the documented user:ref COLON form and
# the {owner} placeholder is expanded by gh inside the query string —
# both verified live 2026-10-24 against gh 2.4.0+dfsg1 (the slash form
# is silently ignored by the API and returns every closed PR, which would
# gate every feat on the repo's newest merged PR). A gh failure is
# swallowed (|| true) and read as "no merged PR": a full GitHub outage
# already fails the precheck's CI-green check upstream.
merged_delivery() {
  local ref="$1" page
  page=$(gh api "repos/{owner}/{repo}/pulls?state=closed&head={owner}:$ref&per_page=100" 2>/dev/null || true)
  if [ -n "$page" ]; then
    jq -r '
      [.[] | select(.merged_at != null)]
      | sort_by(.merged_at) | reverse | .[0] // empty
      | [.number, .merged_at, .merge_commit_sha] | @tsv
    ' <<<"$page" 2>/dev/null || true
  fi
}

# Print every merged PR among the 100 most recently closed PRs of the
# repo (the REQ-011 issue-number-prefix fallback source), one line each:
# number<TAB>merged_at<TAB>merge_commit_sha<TAB>head.ref. The page is
# fetched at most once per run: the first call issues the single gh api
# page scan (per_page=100, the API's max page size) and caches the parsed
# lines in the PID-keyed file of closed_pr_scan_cache_path (removed by
# the precheck stage's EXIT trap); later calls — including from sibling
# subshells of the same run — cat that cache, so the cost is constant,
# not per-folder.
closed_pr_scan() {
  local cache page
  cache=$(closed_pr_scan_cache_path)
  if [ ! -e "$cache" ]; then
    : >"$cache"
    page=$(gh api "repos/{owner}/{repo}/pulls?state=closed&per_page=100" 2>/dev/null || true)
    if [ -n "$page" ]; then
      jq -r '
        [.[] | select(.merged_at != null)]
        | .[]
        | [.number, .merged_at, .merge_commit_sha, .head.ref] | @tsv
      ' <<<"$page" 2>/dev/null >"$cache" || true
    fi
  fi
  cat "$cache"
}

# --- previous-release branch cleanup helpers (feat-233, SOP step 2 sub-item) --

# Per-run cache path of origin_branches' one-shot listing fetch. PID-keyed
# (the closed_pr_scan_cache_path idiom) so that every call — which runs in
# a pipeline/command-substitution subshell ($$ is inherited) — re-derives
# the same file path. The precheck stage removes a stale file at run start
# and traps the removal on EXIT.
origin_branches_cache_path() {
  printf '%s/release-origin-branches-%s' "${TMPDIR:-/tmp}" "$$"
}

# Print origin's full branch listing (`git ls-remote --heads origin` raw
# output: sha<TAB>refs/heads/<name>, ALL branches, unfiltered), fetched at
# most once per run: the first call writes the cache file of
# origin_branches_cache_path, later calls — including from sibling
# subshells of the same run — cat it. The listing is valid for the whole
# run: the only ref deletions mid-run are the cleanup loop's own, and each
# candidate is processed once (a candidate is never re-queried after its
# own deletion). A failed fetch dies (fail-fast: the remote side cannot be
# verified, so no cleanup may run) rather than silently degrading.
origin_branches() {
  local cache
  cache=$(origin_branches_cache_path)
  if [ ! -e "$cache" ]; then
    git ls-remote --heads origin >"$cache" || die "branch cleanup: cannot list origin branches (git ls-remote --heads origin failed)"
  fi
  cat "$cache"
}

# Print the origin tip sha of refs/heads/<name> from the once-per-run
# listing (origin_branches), or nothing when the name is absent from the
# cache (an empty result means "no origin side"). Pure stdout contract:
# the caller captures the sha via command substitution. Replaces the
# per-candidate `git ls-remote` re-fetch — under set -euo pipefail a
# transient failure of that second network call exited the precheck with
# only git's raw stderr (no die diagnostic).
origin_branch_tip() {
  origin_branches | awk -v ref="refs/heads/$1" '$2 == ref { print $1 }'
}

# Print the branch names the previous-release cleanup considers, one per
# line, sorted and de-duplicated: the union of EVERY local branch name
# (git branch) and the origin branch names matching refs/heads/feat-* or
# refs/heads/fix/* (the once-per-run origin_branches listing, the
# refs/heads/ prefix stripped), excluding dev and main (the release
# branches are never cleanup targets). Pure stdout contract: the caller
# captures the list via command substitution. A failed origin fetch dies
# (fail-fast: the remote side cannot be verified, so no cleanup may run)
# rather than silently degrading to the local branch set.
cleanup_candidates() {
  local remote
  remote=$(origin_branches)
  {
    git branch --format='%(refname:short)'
    awk '$2 ~ /^refs\/heads\/(feat-|fix\/)/ { print substr($2, 12) }' <<<"$remote"
  } | sort -u | grep -v -x -e dev -e main || true
}

# Print the branch names checked out in ANY worktree (git worktree list
# --porcelain, all worktrees including the main one; a worktree on a
# detached HEAD carries no `branch` line and contributes nothing), one per
# line. Pure stdout contract: the caller captures the list via command
# substitution.
worktree_branches() {
  git worktree list --porcelain | awk '$1 == "branch" { print substr($2, 12) }'
}

# Print the newest merged PR delivered from the branch named $1 — a thin
# wrapper over merged_delivery keyed on the branch name. Exact head-ref
# lookup only: the REQ-011 issue-number-prefix fallback is a gate-only
# concern of feat FOLDER ids and deliberately does not apply to branch
# names here (a branch is stale iff its own head ref has a merged PR).
# Same 3-column line as merged_delivery (number<TAB>merged_at<TAB>
# merge_commit_sha), or nothing when the branch has no merged PR.
branch_delivery() {
  merged_delivery "$1"
}

# --- stages ------------------------------------------------------------------

stage_resolve() {
  local target
  target=$(resolve_target "${1:-}")
  echo "$target"
}

stage_precheck() {
  local v="${1:-}"
  [ -n "$v" ] || die "usage: $0 precheck <X.Y.Z>"
  validate_full_version "$v"
  require_repo_root
  require_tools
  info "target: v$v"

  local branch
  branch=$(git rev-parse --abbrev-ref HEAD)
  [ "$branch" = "dev" ] || die "not on dev (on: $branch)"

  [ -z "$(dirty_files)" ] || { die "working tree has modified tracked files:"; git status --porcelain >&2; }
  local untracked
  untracked=$(git status --porcelain | grep -c '^??' || true)
  if [ "$untracked" -gt 0 ]; then
    info "note: $untracked untracked path(s) ignored (untracked files cannot enter the release commit)"
  fi

  git fetch origin dev main --quiet
  [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/dev)" ] || die "local dev is not in sync with origin/dev (push or pull first)"

  if git merge-base --is-ancestor origin/main origin/dev; then
    info "fast-forward invariant holds (main is an ancestor of dev)"
  else
    die "main is AHEAD of dev (main has unique commits) — the dev->main merge could not fast-forward; resolve this before releasing"
  fi

  local line rid status conclusion
  line=$(latest_dev_run_tsv)
  [ -n "$line" ] || die "no CI runs found on dev"
  IFS=$'\t' read -r rid _ status conclusion <<<"$line"
  if [ "$status" != "completed" ]; then
    info "latest dev CI run still in flight (status: $status) — waiting"
    wait_for_run "$rid" "dev CI (in-flight)" "$DEV_CI_TIMEOUT_MIN"
  else
    [ "$conclusion" = "success" ] || die "latest dev CI run is not green (conclusion: ${conclusion:-none})"
    info "latest dev CI run is green"
  fi

  if [ -n "$(git tag -l "v$v")" ] || [ -n "$(git ls-remote --tags origin "refs/tags/v$v")" ]; then
    die "tag v$v already exists (locally or on origin)"
  fi
  info "tag v$v does not exist yet"

  uv lock --check >/dev/null 2>&1 || die "uv.lock is out of sync with pyproject.toml — run 'uv lock' and commit the result before releasing"
  info "uv.lock is in sync"

  # --- feat closeout gate (feat-233, SOP step 2 sub-item) ---
  # Every feat folder whose implementation merged into this release window
  # (vPrev..HEAD, or HEAD when no tag is reachable) must already be closed
  # out to status: done. A missing/unparseable status line is a violation
  # in its own right (reported before any PR lookup); a feat with no
  # merged delivery is never gated (REQ-002); a delivery that is an
  # ancestor of vPrev shipped in an earlier release (REQ-003).
  local vprev id delivery delivery_at exact fb fb_at prefix num sha violations
  vprev=$(latest_tag)
  if [ -z "$vprev" ]; then
    info "no release tag reachable from HEAD — the release window is HEAD (first release)"
  fi
  # Drop the stale per-run caches (PID reuse after a crashed run) and
  # trap their removal at the end of this process.
  rm -f "$(closed_pr_scan_cache_path)" "$(origin_branches_cache_path)"
  trap 'rm -f "$(closed_pr_scan_cache_path)" "$(origin_branches_cache_path)"' EXIT
  violations=""
  for id in $(feat_folders); do
    status=$(feat_status "$id")
    if [ "$status" = "$FEAT_STATUS_UNPARSEABLE" ]; then
      violations="${violations}  - $id: frontmatter 'status:' is missing or unparseable (must be one of planning/progress/review/done) — repair the frontmatter, or close out to done"$'\n'
      continue
    fi
    if [ "$status" = "done" ]; then
      continue
    fi
    delivery=""
    delivery_at=""
    exact=$(merged_delivery "$id")
    if [ -n "$exact" ]; then
      delivery="$exact"
      delivery_at=$(cut -f2 <<<"$exact")
    fi
    if [[ "$id" =~ ^feat-([1-9][0-9]*)- ]]; then
      # REQ-011 fallback: the newest merged PR whose head ref starts with
      # the folder's feat-<NNN>- prefix (the one-shot page scan, fetched
      # once per run). feat-0-* has no issue number: exact match only.
      prefix="feat-${BASH_REMATCH[1]}-"
      fb=$(closed_pr_scan | awk -F'\t' -v p="$prefix" 'index($4, p) == 1' | sort -t$'\t' -k2,2 | tail -1)
      if [ -n "$fb" ]; then
        fb_at=$(cut -f2 <<<"$fb")
        if [ -z "$delivery" ] || [[ "$fb_at" > "$delivery_at" ]]; then
          delivery="${fb%$'\t'*}"
        fi
      fi
    fi
    if [ -n "$delivery" ]; then
      num=$(cut -f1 <<<"$delivery")
      sha=$(cut -f3 <<<"$delivery")
      if git merge-base --is-ancestor "$sha" HEAD 2>/dev/null; then
        if [ -n "$vprev" ] && git merge-base --is-ancestor "$sha" "$vprev" 2>/dev/null; then
          info "closeout gate: $id shipped in an earlier release (delivery ${sha:0:12} is an ancestor of $vprev) — not gated"
        else
          violations="${violations}  - $id: status is '$status' but the feature shipped in the current release window (PR #$num, delivery $sha) — close out the feat to done on dev and commit"$'\n'
        fi
      else
        # Explicit not-gated line for an unresolvable delivery (mirror of
        # the cleanup's fail-safe keep): a delivery that is an ancestor of
        # neither HEAD nor vPrev is outside the release window — the gate's
        # condition is the ancestry test, so this is not a violation — but
        # it must not pass silently. "nor of $vprev" only when a prior tag
        # exists (with no prior tag the window is HEAD alone).
        if [ -n "$vprev" ]; then
          info "closeout gate: $id (PR #$num, delivery ${sha:0:12}) is outside the release window (not an ancestor of HEAD, nor of $vprev) — not gated; verify the PR's merge target manually"
        else
          info "closeout gate: $id (PR #$num, delivery ${sha:0:12}) is outside the release window (not an ancestor of HEAD) — not gated; verify the PR's merge target manually"
        fi
      fi
    fi
  done
  if [ -n "$violations" ]; then
    die "feat closeout gate failed (every feat shipped in the current release window must be closed out to status: done):
$violations  remediation: close out the named feat(s) to status: done on dev (or repair the frontmatter), commit, then re-run: scripts/release.sh precheck v$v"
  fi
  info "closeout gate: no feat shipped in this window is left unclosed"

  # --- previous-release branch cleanup (feat-233, SOP step 2 sub-item) ---
  # A feat-*/fix/* branch (local and/or on origin) whose newest merged-PR
  # delivery (branch_delivery — exact head-ref lookup, no REQ-011 prefix
  # fallback) is an ancestor of vPrev is stale (shipped in the previous
  # release or older) and is deleted on every side that exists, local
  # first: the local ref via git branch -d (a refusal is the expected
  # squash-merge case, so -D follows, justified by the delivery proof) and
  # the origin ref via git push origin --delete. Guards (a)-(d) are
  # evaluated per candidate in that order and the FIRST one that fires
  # wins, emitting exactly one report line: (a) checked out in a worktree,
  # (b) no merged PR for the head ref, (c) delivery inside vPrev..HEAD
  # (this release — deletable at the NEXT precheck), (d) local and origin
  # tips differ. A delivery that is an ancestor of neither vPrev nor HEAD
  # is unresolvable locally and is kept with a fail-safe line (manual
  # adjudication needed). With no vPrev there is no "previous release or
  # older": one skip note, no loop, no mutation. DRY_RUN prints the same
  # table with would-delete lines and mutates nothing; the gate above dies
  # on a violation, so a failing precheck never reaches this code.
  local candidates name wt_lines cdel cnum csha local_tip remote_tip side_note mech del_note
  local deleted_count=0 kept_count=0
  if [ -z "$vprev" ]; then
    info "branch cleanup: no previous release tag — nothing to clean up"
  else
    candidates=$(cleanup_candidates)
    if [ -z "$candidates" ]; then
      info "branch cleanup: no stale feat-*/fix/* branches (nothing to delete)"
    else
      wt_lines=$(worktree_branches)
      for name in $candidates; do
        if grep -Fqx "$name" <<<"$wt_lines"; then
          info "branch cleanup: $name: skipped (guard a: checked out in a worktree)"
          kept_count=$((kept_count + 1))
          continue
        fi
        cdel=$(branch_delivery "$name")
        if [ -z "$cdel" ]; then
          info "branch cleanup: $name: kept (guard b: no merged PR for head ref $name)"
          kept_count=$((kept_count + 1))
          continue
        fi
        cnum=$(cut -f1 <<<"$cdel")
        csha=$(cut -f3 <<<"$cdel")
        if ! git merge-base --is-ancestor "$csha" HEAD 2>/dev/null; then
          info "branch cleanup: $name: kept (fail-safe: delivery ${csha:0:12} is an ancestor of neither $vprev nor HEAD — manual adjudication needed)"
          kept_count=$((kept_count + 1))
          continue
        fi
        if ! git merge-base --is-ancestor "$csha" "$vprev" 2>/dev/null; then
          info "branch cleanup: $name: kept (guard c: delivery ${csha:0:12} is inside the current release window $vprev..HEAD)"
          kept_count=$((kept_count + 1))
          continue
        fi
        local_tip=""
        if git rev-parse --verify --quiet "refs/heads/$name" >/dev/null; then
          local_tip=$(git rev-parse --verify "refs/heads/$name")
        fi
        remote_tip=$(origin_branch_tip "$name")
        if [ -n "$local_tip" ] && [ -n "$remote_tip" ] && [ "$local_tip" != "$remote_tip" ]; then
          info "branch cleanup: $name: skipped (guard d: local tip ${local_tip:0:12} != origin tip ${remote_tip:0:12} — manual decision)"
          kept_count=$((kept_count + 1))
          continue
        fi
        if [ -z "$local_tip" ] && [ -z "$remote_tip" ]; then
          # Unreachable (the name came from the candidate union) — kept,
          # never deleted, on the defensive side.
          info "branch cleanup: $name: kept (neither side resolvable — manual decision)"
          kept_count=$((kept_count + 1))
          continue
        fi
        # One-side marker: only a branch present on a single side is
        # annotated with that side (both sides present -> no marker).
        side_note=""
        if [ -n "$local_tip" ] && [ -z "$remote_tip" ]; then
          side_note="local side only; "
        elif [ -z "$local_tip" ] && [ -n "$remote_tip" ]; then
          side_note="origin side only; "
        fi
        if [ -n "$local_tip" ]; then
          if [ "$DRY_RUN" -eq 1 ]; then
            info "branch cleanup: $name: would delete local ref (${side_note}proven stale by PR #$cnum, delivery ${csha:0:12} ≤ $vprev)"
          else
            if git branch -d "$name" 2>/dev/null; then
              mech="git branch -d"
            else
              git branch -D "$name" || die "branch cleanup: git branch -D $name failed (git branch -d refused as well) — delete the local ref manually, then re-run: scripts/release.sh precheck v$v"
              mech="git branch -D — -d refused the squash-merged head"
            fi
            info "branch cleanup: $name: deleted local ref ($side_note$mech; proven stale by PR #$cnum, delivery ${csha:0:12} ≤ $vprev)"
          fi
        fi
        if [ -n "$remote_tip" ]; then
          if [ "$DRY_RUN" -eq 1 ]; then
            info "branch cleanup: $name: would delete origin ref (${side_note}proven stale by PR #$cnum, delivery ${csha:0:12} ≤ $vprev)"
          else
            if [ -n "$local_tip" ]; then
              del_note="the local ref was already deleted"
            else
              del_note="the branch was origin-side only (no local ref)"
            fi
            git push origin --delete "$name" >/dev/null || die "branch cleanup: git push origin --delete $name failed ($del_note) — delete the origin ref manually, then re-run: scripts/release.sh precheck v$v"
            info "branch cleanup: $name: deleted origin ref (${side_note}git push origin --delete; proven stale by PR #$cnum, delivery ${csha:0:12} ≤ $vprev)"
          fi
        fi
        deleted_count=$((deleted_count + 1))
      done
      if [ "$DRY_RUN" -eq 1 ]; then
        info "branch cleanup: [dry-run] $deleted_count branch(es) would be deleted, $kept_count kept/skipped"
      else
        info "branch cleanup: $deleted_count branch(es) deleted, $kept_count kept/skipped"
      fi
    fi
  fi

  info "precheck: all checks passed for v$v"
}

stage_bump() {
  local v="${1:-}"
  [ -n "$v" ] || die "usage: $0 bump <X.Y.Z>"
  validate_full_version "$v"
  require_repo_root
  assert_dirty_subset "" CHANGELOG.md
  local current
  current=$(current_version)
  [ "$current" != "$v" ] || die "pyproject.toml already carries $v"

  if [ "$DRY_RUN" -eq 1 ]; then
    info "[dry-run] would set pyproject.toml version $current -> $v, then run 'uv lock'"
    return 0
  fi

  local n
  n=$(grep -c '^version = "' pyproject.toml)
  [ "$n" -eq 1 ] || die "expected exactly one 'version = \"...\"' line in pyproject.toml, found $n"
  sed -i "s/^version = \"[^\"]*\"/version = \"$v\"/" pyproject.toml
  info "pyproject.toml: $current -> $v"

  uv lock
  local changed old_line new_line
  changed=$(git diff --unified=0 uv.lock | grep -cE '^[+-][^+-]' || true)
  [ "$changed" -eq 2 ] || die "uv.lock diff is not exactly the version line ($changed changed lines) — inspect 'git diff uv.lock'"
  old_line=$(git diff --unified=0 uv.lock | grep -E '^-' | grep -v '^---')
  new_line=$(git diff --unified=0 uv.lock | grep -E '^+' | grep -v '^+++')
  grep -q "$current" <<<"$old_line" && grep -q "$v" <<<"$new_line" || die "uv.lock version-line diff does not look like $current -> $v:"
  info "uv.lock: only the $REPO_ROOT version entry changed"
  info "bump: done ($v)"
}

stage_changelog() {
  local v="${1:-}"
  [ -n "$v" ] || die "usage: $0 changelog <X.Y.Z>"
  validate_full_version "$v"
  require_repo_root
  assert_dirty_subset "" pyproject.toml uv.lock CHANGELOG.md

  if grep -q "^## \[$v\] - " CHANGELOG.md; then
    info "changelog: section ## [$v] already present — nothing to do"
    return 0
  fi

  if unreleased_is_empty; then
    confirm_or_die "the [Unreleased] section is EMPTY — releasing with no documented changes is almost always a mistake. Continue with v$v?"
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    info "[dry-run] would move the [Unreleased] content into '## [$v] - $(date +%F)' under a re-emptied '## [Unreleased]' header"
    return 0
  fi

  local line_no
  line_no=$(grep -n '^## \[Unreleased\]$' CHANGELOG.md | head -1 | cut -d: -f1) || die "no '## [Unreleased]' header in CHANGELOG.md"
  awk -v n="$line_no" -v v="$v" -v d="$(date +%F)" '
    NR == n { print; print ""; print "## [" v "] - " d; next }
    { print }
  ' CHANGELOG.md > CHANGELOG.md.tmp
  mv CHANGELOG.md.tmp CHANGELOG.md

  grep -q "^## \[$v\] - " CHANGELOG.md || die "changelog transform failed: section header missing"
  [ -n "$(extract_changelog_section "$v")" ] || die "changelog transform failed: section body is empty"
  info "changelog: [Unreleased] moved into ## [$v] - $(date +%F)"
}

stage_commit_push() {
  local v="${1:-}"
  [ -n "$v" ] || die "usage: $0 commit-push <X.Y.Z>"
  validate_full_version "$v"
  require_repo_root
  require_tools

  local msg="chore(release): bump version to v$v"
  if [ "$(git log -1 --format=%s)" = "$msg" ] && [ -z "$(dirty_files)" ] && [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/dev)" ]; then
    info "commit-push: release commit already made and pushed — waiting for CI"
    wait_for_dev_ci
    return 0
  fi

  [ "$(current_version)" = "$v" ] || die "pyproject.toml does not carry $v — run the bump stage first"
  local f
  for f in $(dirty_files); do
    case "$f" in
      pyproject.toml|uv.lock|CHANGELOG.md) ;;
      *) die "unexpected working-tree change: $f — the release commit must be exactly pyproject.toml, uv.lock, CHANGELOG.md" ;;
    esac
  done

  if [ "$DRY_RUN" -eq 1 ]; then
    info "[dry-run] would commit the dirty release files as '$msg' and push dev"
    return 0
  fi

  git add pyproject.toml uv.lock CHANGELOG.md
  git commit -m "$msg"
  git push origin dev
  info "release commit pushed to dev"
  wait_for_dev_ci
  info "commit-push: done (dev CI green)"
}

stage_pr_create() {
  local v="${1:-}"
  [ -n "$v" ] || die "usage: $0 pr-create <X.Y.Z>"
  validate_full_version "$v"
  require_repo_root
  require_tools
  [ "$(current_version)" = "$v" ] || die "pyproject.toml does not carry $v — finish commit-push first"

  local pr_line pr_num pr_url
  pr_line=$(gh pr list --base main --head dev --state open --json number,url --jq '.[0] // empty | [.number, .url] | @tsv' 2>/dev/null || true)
  if [ -n "$pr_line" ]; then
    IFS=$'\t' read -r pr_num pr_url <<<"$pr_line"
    info "resuming existing release PR: $pr_url"
  else
    if [ "$DRY_RUN" -eq 1 ]; then
      info "[dry-run] would create PR dev->main 'Release v$v' with the changelog section as body, then wait for its checks"
      return 0
    fi
    local body_file
    body_file=$(mktemp)
    {
      echo "Release v$v (SOP $SOP_ID, step 6)."
      echo
      extract_changelog_section "$v"
    } >"$body_file"
    pr_url=$(gh pr create --base main --head dev --title "Release v$v" --body-file "$body_file")
    rm -f "$body_file"
    pr_num=$(gh pr view "$pr_url" --json number --jq .number)
    info "created release PR: $pr_url"
  fi

  wait_for_pr_checks "$pr_num"
  info "pr-create: done — PR $pr_url is green. Merge gate: present this PR to the maintainer, then run: $0 pr-merge $v"
}

stage_pr_merge() {
  local v="${1:-}"
  [ -n "$v" ] || die "usage: $0 pr-merge <X.Y.Z>"
  validate_full_version "$v"
  require_repo_root
  require_tools

  git fetch origin main dev --quiet
  if [ "$(git rev-parse origin/main)" = "$(git rev-parse origin/dev)" ]; then
    info "pr-merge: main already equals dev — nothing to merge"
    return 0
  fi

  local pr_line pr_num
  pr_line=$(gh pr list --base main --head dev --state open --json number --jq '.[0] // empty | [.number] | @tsv' 2>/dev/null || true)
  [ -n "$pr_line" ] || die "no open dev->main PR — run pr-create first (after the maintainer's merge gate)"
  pr_num="${pr_line%%$'\t'*}"

  # Poll like pr-create, never fail fast on pending: ci.yml triggers on
  # both push and pull_request, so the PR's own run can register pending
  # check-runs after pr-create was already satisfied by the push run's
  # green jobs (v0.16.0 incident).
  wait_for_pr_checks "$pr_num"

  # Fast-forward-only, enforced three ways. The merge itself is LOCAL
  # (git merge --ff-only + push of main, then close the PR): the plain
  # `gh pr merge --merge` method cannot be relied on to fast-forward —
  # during the v0.16.0 release it created a merge commit on main
  # although the invariant held, and this environment's gh 2.4.0 has
  # no --ff flag.
  if git merge-base --is-ancestor origin/main origin/dev; then
    info "fast-forward invariant holds (main is an ancestor of dev)"
  else
    die "origin/main is not an ancestor of origin/dev — the merge could not fast-forward; resolve before merging"
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    info "[dry-run] would run: git checkout main && git merge --ff-only origin/dev && git push origin main && git checkout dev, then close PR #$pr_num (fast-forward enforced by --ff-only and the assertions above and below)"
    return 0
  fi

  git checkout main --quiet
  git merge --ff-only origin/dev --quiet
  git push origin main --quiet
  git checkout dev --quiet
  git fetch origin main --quiet
  [ "$(git rev-parse origin/main)" = "$(git rev-parse origin/dev)" ] || die "after merge, origin/main != origin/dev — the invariant is broken; investigate before tagging"
  close_pr_if_open "$pr_num"
  info "pr-merge: done (fast-forward via local --ff-only merge; the invariant holds)"
}

stage_tag_push() {
  local v="${1:-}"
  [ -n "$v" ] || die "usage: $0 tag-push <X.Y.Z>"
  validate_full_version "$v"
  require_repo_root
  require_tools

  if [ -n "$(git ls-remote --tags origin "refs/tags/v$v")" ]; then
    info "tag-push: tag v$v already exists on origin — nothing to do"
    return 0
  fi
  if [ -n "$(git tag -l "v$v")" ]; then
    die "local tag v$v exists but is not on origin — resolve manually (delete or push it)"
  fi

  git fetch origin main --quiet
  [ "$(git rev-parse origin/main)" = "$(git rev-parse origin/dev)" ] || die "origin/main != origin/dev — finish pr-merge first (fast-forward invariant)"

  if [ "$DRY_RUN" -eq 1 ]; then
    info "[dry-run] would checkout main, pull --ff-only, tag v$v at main HEAD, push the tag, and switch back to dev"
    return 0
  fi

  git checkout main
  git pull --ff-only origin main
  git tag "v$v"
  git push origin "v$v"
  git checkout dev
  info "tag-push: done — WARNING: publication (publish.yml) has now started; the release is irreversible"
}

stage_publish_wait() {
  local v="${1:-}"
  [ -n "$v" ] || die "usage: $0 publish-wait <X.Y.Z>"
  validate_full_version "$v"
  require_repo_root
  require_tools

  git rev-parse --verify --quiet "refs/tags/v$v" >/dev/null || die "tag v$v does not exist locally — fetch tags or run tag-push first"
  local tag_sha
  tag_sha=$(git rev-parse --verify "refs/tags/v$v^{commit}")

  local line runs rid polls jobs
  polls=0
  while :; do
    # `gh run list --commit` does not exist in old `gh`; filter by the tag's
    # commit SHA (headSha) with jq instead.
    runs=$(gh run list --workflow "$PUBLISH_WORKFLOW" --limit 30 --json databaseId,headSha,status 2>/dev/null || true)
    line=$(jq -r --arg sha "$tag_sha" '[.[] | select(.headSha == $sha)] | .[0] // empty | [.databaseId, .status] | @tsv' <<<"$runs" 2>/dev/null || true)
    if [ -n "$line" ]; then
      rid="${line%%$'\t'*}"
      wait_for_run "$rid" "publish (v$v)" "$PUBLISH_TIMEOUT_MIN"
      # `gh run view --json jobs` does not exist in old `gh`; parse the
      # plain `gh run view` output (a run only completes "success" when
      # every job succeeded).
      jobs=$(gh run view "$rid" 2>/dev/null | sed -n '/^JOBS$/,/^ANNOTATIONS$/p' | grep -E '^[✓✗] ' | sed -E 's/^[✓✗] //; s/ in [0-9]+(m[0-9]+s|s|ms)? \(ID [0-9]+\)$//' | paste -sd, - | sed 's/,/, /g') || jobs=""
      info "publish-wait: done — jobs: ${jobs:-all succeeded (run conclusion: success)}"
      return 0
    fi
    polls=$((polls + 1))
    if [ "$polls" -ge 10 ]; then
      die "no publish.yml run appeared for tag v$v within 150s"
    fi
    sleep 15
  done
}

stage_release_notes() {
  local v="${1:-}"
  [ -n "$v" ] || die "usage: $0 release-notes <X.Y.Z>"
  validate_full_version "$v"
  require_repo_root
  require_tools

  # The release NAME is never touched: the publication workflow's "Make
  # GitHub Release" job creates it with the bare version string (SOP
  # step 8), and this stage sets the notes only (SOP step 9). The
  # `v<X.Y.Z> - <text>` name-text behaviour that used to live here was
  # reverted 2026-10-22 (SOP Updates).
  #
  # `gh release view --json` and `gh release edit` do not exist in old `gh`;
  # read and update the release through `gh api` instead.
  local rel url assets
  rel=$(gh api repos/{owner}/{repo}/releases/tags/v$v 2>/dev/null) || die "GitHub Release v$v not found — the publish run's 'Make GitHub Release' job may have failed; check it before proceeding"
  url=$(jq -r '.html_url // empty' <<<"$rel" 2>/dev/null || true)
  [ -n "$url" ] || die "cannot read the GitHub Release v$v URL from the API response"
  assets=$(jq '.assets | length' <<<"$rel" 2>/dev/null || echo 0)
  [ "$assets" -ge 2 ] || die "GitHub Release v$v has only $assets asset(s); expected sdist + wheel"

  local section
  section=$(extract_changelog_section "$v")
  [ -n "$section" ] || die "no changelog section for v$v in CHANGELOG.md"

  local current_notes
  # The stored body is returned with CRLF line endings (confirmed for
  # every release set this way — v0.15.0 and v0.16.0), while the
  # changelog section is LF: compare with the CRs stripped, or the stage
  # would re-PATCH forever and never report "already set". The stored
  # NAME is deliberately not compared: since the 2026-10-22 revert it is
  # not part of this stage's contract (SOP Updates).
  current_notes=$(jq -r '.body // ""' <<<"$rel" 2>/dev/null | tr -d '\r')
  if [ "$current_notes" = "$section" ]; then
    info "release-notes: already set — nothing to do"
  elif [ "$DRY_RUN" -eq 1 ]; then
    info "[dry-run] would set the release notes of $url to the v$v changelog section"
  else
    local notes_file rel_id
    notes_file=$(mktemp)
    printf '%s\n' "$section" >"$notes_file"
    rel_id=$(jq -r '.id' <<<"$rel")
    gh api --method PATCH repos/{owner}/{repo}/releases/"$rel_id" -F "body=@$notes_file" >/dev/null
    rm -f "$notes_file"
    info "release-notes: set (notes from the v$v changelog section; release name untouched)"
  fi

  info "----------------------------------------------------------------"
  info "release v$v complete:"
  info "  GitHub Release:  $url"
  info "  PyPI:            https://pypi.org/project/$REPO_ROOT/$v/"
  info "  TestPyPI:        https://test.pypi.org/project/$REPO_ROOT/$v/"
  info "  MCP Registry:    https://registry.modelcontextprotocol.io/?q=io.github.dfch%2Fbiz-dfch-specmgr"
  info "  SOP:             docs/sop/sop-$SOP_ID-perform-a-release-of-biz-dfch-specmgr.md"
}

stage_status() {
  local v="${1:-}"
  [ -n "$v" ] || die "usage: $0 status <X.Y.Z>"
  validate_full_version "$v"
  require_repo_root
  require_tools
  git fetch origin dev main --quiet 2>/dev/null || true

  local mark detail
  echo "release status for v$v:"

  # 1. bump
  if [ "$(current_version)" = "$v" ]; then mark="x"; detail="pyproject.toml carries $v"; else mark=" "; detail="pyproject.toml carries $(current_version)"; fi
  printf '  [%s] bump          %s\n' "$mark" "$detail"

  # 2. changelog
  if grep -q "^## \[$v\] - " CHANGELOG.md; then
    if unreleased_is_empty; then mark="x"; detail="dated section present, [Unreleased] emptied"; else mark="!"; detail="dated section present but [Unreleased] still has content"; fi
  else mark=" "; detail="no dated section yet"; fi
  printf '  [%s] changelog     %s\n' "$mark" "$detail"

  # 3. commit-push
  local msg="chore(release): bump version to v$v"
  local commit_sha
  commit_sha=$(git log origin/dev --format='%H %s' 2>/dev/null | grep -m1 " $msg\$" | awk '{print $1}' || true)
  if [ -n "$commit_sha" ]; then
    mark="x"
    detail="commit ${commit_sha:0:12} on origin/dev"
    local line s c
    line=$(latest_dev_run_tsv)
    if [ -n "$line" ]; then
      IFS=$'\t' read -r _ _ s c <<<"$line"
      detail="$detail; latest dev CI: ${s}${c:+/$c}"
    fi
  else mark=" "; detail="release commit not on origin/dev"; fi
  printf '  [%s] commit-push   %s\n' "$mark" "$detail"

  # 4. PR / merge
  local pr_line
  pr_line=$(gh pr list --base main --head dev --state open --json number,url --jq '.[0] // empty | [.number, .url] | @tsv' 2>/dev/null || true)
  if [ -n "$pr_line" ]; then
    mark="!"; detail="open PR: $pr_line (merge gate pending?)"
  elif git rev-parse --verify --quiet "refs/tags/v$v" >/dev/null && git merge-base --is-ancestor "v$v" origin/main 2>/dev/null; then
    # Post-release normal state: dev has moved on past the release commit,
    # so main != dev, but the tag being on origin/main proves the merge.
    mark="x"; detail="merged (tag v$v on origin/main)"
  elif [ "$(git rev-parse origin/main 2>/dev/null || true)" = "$(git rev-parse origin/dev 2>/dev/null || true)" ]; then
    mark="x"; detail="main equals dev (merged)"
  else
    mark=" "; detail="no open PR; main behind dev"
  fi
  printf '  [%s] pr            %s\n' "$mark" "$detail"

  # 5. tag
  if [ -n "$(git ls-remote --tags origin "refs/tags/v$v" 2>/dev/null || true)" ]; then
    mark="x"; detail="tag on origin"
  elif git rev-parse --verify --quiet "refs/tags/v$v" >/dev/null; then
    mark="!"; detail="local tag exists, not pushed"
  else
    mark=" "; detail="no tag"
  fi
  printf '  [%s] tag           %s\n' "$mark" "$detail"

  # 6. publish
  local tag_sha pub_line runs
  tag_sha=""
  if git rev-parse --verify --quiet "refs/tags/v$v" >/dev/null; then
    tag_sha=$(git rev-parse --verify "refs/tags/v$v^{commit}")
  fi
  if [ -n "$tag_sha" ]; then
    runs=$(gh run list --workflow "$PUBLISH_WORKFLOW" --limit 30 --json headSha,status,conclusion 2>/dev/null || true)
    pub_line=$(jq -r --arg sha "$tag_sha" '[.[] | select(.headSha == $sha)] | .[0] // empty | [.status, (.conclusion // "-")] | @tsv' <<<"$runs" 2>/dev/null || true)
    if [ -n "$pub_line" ]; then mark="x"; detail="run: $pub_line"; else mark="!"; detail="tag exists, no publish run found yet"; fi
  else mark=" "; detail="no publish run (no tag)"; fi
  printf '  [%s] publish       %s\n' "$mark" "$detail"

  # 7. release notes (via `gh api`; old `gh` has no `gh release view --json`)
  local rel assets notes_ok
  rel=$(gh api repos/{owner}/{repo}/releases/tags/v$v 2>/dev/null) || rel=""
  if [ -n "$rel" ]; then
    assets=$(jq '.assets | length' <<<"$rel" 2>/dev/null || echo 0)
    notes_ok=$(jq -r '.body // ""' <<<"$rel" 2>/dev/null || true)
    if [ "$notes_ok" = "$(extract_changelog_section "$v")" ]; then mark="x"; detail="release exists ($assets assets), notes set"; else mark="!"; detail="release exists ($assets assets), notes NOT yet set"; fi
  else
    mark=" "; detail="no GitHub Release yet"
  fi
  printf '  [%s] release-notes %s\n' "$mark" "$detail"
}

stage_all() {
  local arg="${1:-}"
  [ "$DRY_RUN" -eq 1 ] || { is_tty || die "all mode is interactive (merge gate); in non-interactive contexts run the stages individually"; }
  local v
  v=$(resolve_target "$arg")
  info "resolved target: v$v"
  stage_precheck "$v"
  if [ "$DRY_RUN" -eq 0 ]; then
    info "note: all mode does NOT curate the changelog (SOP step 3 is an agent/manual step); [Unreleased] is taken as-is"
  fi
  stage_bump "$v"
  stage_changelog "$v"
  stage_commit_push "$v"
  stage_pr_create "$v"
  if [ "$DRY_RUN" -eq 0 ]; then
    confirm_or_die "merge gate: PR is green — merge dev into main now (ff-only)?"
  fi
  stage_pr_merge "$v"
  stage_tag_push "$v"
  stage_publish_wait "$v"
  stage_release_notes "$v"
}

# --- dispatch ----------------------------------------------------------------

main() {
  local stage="${1:-}"
  [ -n "$stage" ] || usage
  shift || true
  local a
  for a in "$@"; do
    case "$a" in
      --dry-run) DRY_RUN=1 ;;
      *)
        if [ -z "$VERSION_ARG" ]; then
          VERSION_ARG="$a"
        else
          die "unexpected argument '$a' (every stage takes at most one positional)"
        fi
        ;;
    esac
  done

  case "$stage" in
    resolve) stage_resolve "$VERSION_ARG" ;;
    precheck) stage_precheck "$VERSION_ARG" ;;
    bump) stage_bump "$VERSION_ARG" ;;
    changelog) stage_changelog "$VERSION_ARG" ;;
    commit-push) stage_commit_push "$VERSION_ARG" ;;
    pr-create) stage_pr_create "$VERSION_ARG" ;;
    pr-merge) stage_pr_merge "$VERSION_ARG" ;;
    tag-push) stage_tag_push "$VERSION_ARG" ;;
    publish-wait) stage_publish_wait "$VERSION_ARG" ;;
    release-notes) stage_release_notes "$VERSION_ARG" ;;
    status) stage_status "$VERSION_ARG" ;;
    all) stage_all "$VERSION_ARG" ;;
    help|-h|--help) usage ;;
    *) die "unknown stage: $stage"
      usage
    ;;
  esac
}

# Guard so the file can be SOURCED (tests/test_release_sh.py sources the
# helpers); a direct run still dispatches exactly as before.
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
