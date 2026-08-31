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
#   precheck      fail-fast pre-release checks (SOP step 2)
#   bump          pyproject.toml + uv.lock version bump (SOP step 4)
#   changelog     move [Unreleased] into a dated section (SOP step 5a)
#   commit-push   commit the 3 release files, push dev, wait for CI (SOP step 5b)
#   pr-create     open the dev->main release PR, wait for checks (SOP step 6a)
#   pr-merge      ff-only merge of the release PR (SOP step 6b, after the merge gate)
#   tag-push      tag vX.Y.Z on main, push the tag, back to dev (SOP step 7)
#   publish-wait  wait for the 4 publish.yml jobs (SOP step 8)
#   release-notes verify the release + set the GitHub Release notes (SOP step 9)
#   status        read-only: where does this release stand?
#   all           resolve + precheck + bump + changelog + commit-push +
#                 pr-create + [TTY merge gate] + pr-merge + tag-push +
#                 publish-wait + release-notes (no agent curation: the
#                 [Unreleased] section must already be curated)
#
# Only `resolve` and `all` accept bump keywords; all other stages take the
# full resolved version.
#
# Written against the old `gh` (2.4.0) this environment ships: no
# `gh run list --commit`, no `gh run view --json jobs`, no `gh release
# edit`, no `--ff`-style merge flag. The publication run is located by
# workflow NAME ("Publish to PyPI") plus the tag's commit SHA (filtered
# with `jq`); the release notes are set via `gh api`; ff-only merging is
# enforced by pre- and post-merge SHA assertions around the plain merge
# method. The SOP's "Safety and Precautions" documents the same
# constraints.

set -euo pipefail

SOP_ID="98537416-0e6e-4a02-925f-974a17bfa10a"
REPO_ROOT="biz-dfch-specmgr"
# Workflow NAME (the `name:` key) of .github/workflows/publish.yml —
# `gh run list --workflow` filters by name, not by file name.
PUBLISH_WORKFLOW="Publish to PyPI"
POLL_INTERVAL=30
DEV_CI_TIMEOUT_MIN=40
PUBLISH_TIMEOUT_MIN=45

DRY_RUN=0
VERSION_ARG=""

info() { printf 'release: %s\n' "$*"; }
die() { printf 'release: ERROR: %s\n' "$*" >&2; exit 1; }
is_tty() { [ -t 0 ]; }

usage() {
  sed -n '2,38p' "$0" | sed 's/^# \{0,1\}//'
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
# dev-branch run, or nothing if none exists. (This gh version has no
# 'gh run list --branch' flag, hence the headBranch filter.)
latest_dev_run_tsv() {
  gh run list --limit 30 --json databaseId,headSha,headBranch,status,conclusion \
    --jq '[.[] | select(.headBranch == "dev")] | .[0] // empty
          | [.databaseId, .headSha, .status, (.conclusion // "")] | @tsv' 2>/dev/null || true
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
wait_for_pr_checks() {
  local pr="$1" out rc polls
  polls=0
  while :; do
    out=$(gh pr checks "$pr" 2>&1) && rc=0 || rc=$?
    if [ "$rc" -eq 0 ]; then
      info "PR #$pr checks: all green"
      return 0
    fi
    if [ "$rc" -eq 1 ]; then
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

  local out rc
  out=$(gh pr checks "$pr_num" 2>&1) && rc=0 || rc=$?
  [ "$rc" -eq 0 ] || { printf '%s\n' "$out" >&2; die "PR #$pr_num checks are not all green — do not merge"; }

  # Fast-forward-only, enforced three ways (old `gh` has no --ff-only flag):
  # assert the invariant before, merge with the plain merge method
  # (GitHub fast-forwards an up-to-date branch instead of creating a
  # merge commit), and re-assert the SHAs after.
  if git merge-base --is-ancestor origin/main origin/dev; then
    info "fast-forward invariant holds (main is an ancestor of dev)"
  else
    die "origin/main is not an ancestor of origin/dev — the merge could not fast-forward; resolve before merging"
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    info "[dry-run] would run: gh pr merge $pr_num --merge (fast-forward enforced by the assertions above and below)"
    return 0
  fi

  gh pr merge "$pr_num" --merge
  git fetch origin main --quiet
  [ "$(git rev-parse origin/main)" = "$(git rev-parse origin/dev)" ] || die "after merge, origin/main != origin/dev — a merge commit was created (the invariant is broken); investigate before tagging"
  info "pr-merge: done (fast-forward; the invariant holds)"
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
  current_notes=$(jq -r '.body // ""' <<<"$rel" 2>/dev/null || true)
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
    info "release-notes: set"
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
        [ -z "$VERSION_ARG" ] || die "at most one positional argument (got: $VERSION_ARG and $a)"
        VERSION_ARG="$a"
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

main "$@"
